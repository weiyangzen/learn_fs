<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libdw.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/libdw.h

## Purpose

`libdw.h` declares optional libdw addr2line support and no-op stubs for builds without elfutils support.

## Important APIs, Types, and Functions

With `HAVE_LIBDW_SUPPORT`, it declares `libdw__addr2line()` and `dso__free_libdw()`. Without support, inline stubs return 0 or no-op.

## Control Flow

Build configuration selects real functions or stubs. Callers can attempt libdw lookup and fall back when 0 is returned.

## State and Persistence Behavior

The header defines no state; implementation caches Dwfl contexts in DSOs.

## Dependencies and Integration Points

It uses `u64` and forward declarations for DSO, inline nodes, and symbols. It integrates srcline resolution with optional libdw availability.

## Risks and Edge Cases

Stub behavior must remain consistent with "not found" rather than fatal error. Callers must free returned file strings only on success from real implementations.

## Test Signals

Build tests should cover libdw enabled and disabled. Runtime tests should verify fallback behavior when stubs return 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libdw.h -->
