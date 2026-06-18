# sources/distributed-fs/ceph/src/librados/librados_c.cc

## Purpose

`librados_c.cc` is the implementation of the exported C ABI declared in `include/rados/librados.h`. It translates opaque C handles and C buffers into `RadosClient`, `IoCtxImpl`, `ObjectOperation`, `AioCompletionImpl`, and C++ `IoCtx` calls, while preserving symbol-version compatibility, tracepoints, errno-style return values, and C ownership rules.

## Important APIs, Types, and Functions

The file starts with symbol-version macros (`LIBRADOS_C_API_*`) that emit base/default symbol versions when building shared librados. `rados_create_cct()` initializes a library `CephContext` without global daemon state and initializes tracepoints. Cluster APIs include create/create2/create_with_context, connect, shutdown, cct, version, config parsing/get/set, fsid, pool lookup/list/reverse lookup, stats, blocklist/blacklist, address retrieval, command routing, monitor log, and service registration.

IoCtx APIs create/destroy pool handles, expose pool stats, snapshots, namespace/locator, pool alignment, full-try flags, application metadata, sync object I/O, xattrs, stat, class exec, object listing, and allocation hints. Async APIs create/wait/query/release completions and submit async object, xattr, stat, exec, snap, flush, watch, notify, and operation calls. Watch/notify wrappers adapt C callbacks into `WatchCtx`/`WatchCtx2` subclasses and decode notify replies into C arrays. Compound write/read operation APIs allocate operation objects, add assertions and subops, execute sync/async, and provide omap/xattr/read result iterators. Lock APIs adapt C calls to C++ `IoCtx` lock methods.

## Control Flow and Data Flow

Most functions follow a simple bridge pattern: cast an opaque handle, validate selected arguments, build `object_t`, `bufferlist`, vectors, maps, or sets, call an internal method, copy results into caller buffers or allocate output buffers, emit tracepoints, and return negative errno or positive byte/count results. Output-buffer helpers allocate with `malloc()` for C callers and are paired with `rados_buffer_free()`. Iterator APIs allocate C++ iterator structs and expose pointers valid until the next iteration/end call.

Compound operations are staged: create op, append subops to `ObjectOperation`, then submit through `IoCtxImpl::operate()`/`operate_read()` or async variants. Some read subops install `Context` handlers (`C_bl_to_buf`, `C_out_buffer`, `C_OmapIter`, `C_XattrsIter`) so that after Objecter completion, output buffers or iterators are populated.

## State and Persistence Behavior

The file itself stores almost no global state beyond tracepoint traits. It creates persistent effects through cluster commands, pool lifecycle, object writes/removes/truncates/xattrs/omap/class calls, locks, watch registrations, notify acknowledgements, and metadata updates. Local state is represented by opaque handles: `rados_t` owns a `RadosClient`, `rados_ioctx_t` owns an `IoCtxImpl` ref, completion handles own `AioCompletionImpl`, iterators own result snapshots, and op handles own assembled operations.

## Dependencies and Integration Points

It depends on Ceph config/common init, tracepoints, `hobject_t`, async waiters, public C header, `AioCompletionImpl`, `IoCtxImpl`, `ObjectOperationImpl`, `RadosClient`, `RadosXattrIter`, `ListObjectImpl`, and `librados_util.h`. It is the ABI boundary used by external C callers and also by parts of the C++ API that implement behavior in terms of C wrappers.

## Risks and Edge Cases

ABI compatibility is a major risk: symbol versions preserve old struct layouts such as base `rados_ioctx_pool_stat`, and deprecated tmap base/default behavior differs intentionally. Buffer sizing must return `-ERANGE` and required lengths consistently. Several APIs return borrowed pointers into iterator-owned maps or one-step heap buffers, so lifetime documentation and tests matter. Null-pointer validation is uneven because older ABI behavior may be preserved. Async wrappers that allocate intermediate completions/data must release them on every completion path. Compound ops can be reused/mutated by callers, so concurrent use is unsafe. `rados_aio_writesame()` passes `o` where the local `oid` object was built, relying on implicit conversion and deserving regression coverage.

## Test Signals

Coverage should include C ABI symbol/version checks, create/connect/shutdown, config parsing, pool and cluster stats, pool create/delete and async variants, all sync object I/O paths, user-buffer and allocated-buffer outputs, xattr and omap iterators, object listing cursor/slice APIs, async completion state/callback ordering, watch/notify including reply decoding/freeing, lock/list/break lock, compound read/write operations, error paths for too-small buffers and invalid inputs, and LTTNG tracepoint builds.
