# sources/distributed-fs/ceph/src/rgw/librgw.cc

## Purpose
This source file exposes the C ABI entry points for embedding RGW as `librgw`. It initializes the singleton RGW library object and returns a retained `CephContext` handle to C callers, then shuts the library down and releases the context.

## Important APIs, types, and functions
- Namespace state: `rgw::global_stop`, `rgw::librgw_mtx`, and static `RGWLib rgwlib`.
- `librgw_create(librgw_t* rgw, int argc, char **argv)` initializes `g_rgwlib`, optionally parses the last argument as a whitespace-split argument bundle, calls `rgwlib.init(args)`, and stores `g_ceph_context->get()` into the caller output.
- `librgw_shutdown(librgw_t rgw)` casts the opaque handle to `CephContext*`, calls `rgwlib.stop()`, logs final shutdown, and releases the context with `put()`.

## Control flow
Initialization is guarded by `g_ceph_context`. If no context exists, the mutex serializes the second check and `rgwlib.init()`. The last non-zero command-line argument can be split into multiple arguments before appending to the normal `argv_to_vec()` result. Shutdown is unconditional for the supplied handle.

## State and persistence behavior
The file manages process-global state rather than persistent data: `g_rgwlib`, `g_ceph_context`, the static RGW library instance, and CephContext reference counts. No disk or RADOS objects are written here.

## Dependencies and integration points
It includes the public `include/rados/librgw.h` C header, Ceph argument parsing and context headers, and `rgw_lib.h`. It is the boundary between external C/C++ consumers and RGW's internal singleton service.

## Risks and edge cases
- `librgw_create()` assigns `*rgw = g_ceph_context->get()` even if initialization failed after leaving `g_ceph_context` null; callers rely on `rgwlib.init()` behavior to establish context.
- Only initialization is mutex-protected. Concurrent shutdown/create interactions depend on broader RGW library semantics.
- Splitting only the final argument is a compatibility behavior that can surprise callers if paths or values contain spaces.

## Test signals
Tests should exercise successful create/shutdown, repeated create calls, failing initialization paths, final-argument splitting, reference-count balance under repeated use, and concurrent create attempts.
