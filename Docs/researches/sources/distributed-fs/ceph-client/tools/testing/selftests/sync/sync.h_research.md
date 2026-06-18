# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync.h

## Purpose
Declares the shared sync helper interface consumed by the sync selftest source files. It keeps the tests independent from direct `sync_file` ioctl details while exposing fence wait, merge, size, and status-count operations.

## Important APIs, Types, And Functions
Defines status constants `FENCE_STATUS_ERROR`, `FENCE_STATUS_ACTIVE`, and `FENCE_STATUS_SIGNALED`, matching the kernel sync-file status conventions used by `struct sync_fence_info.status`. Declares `sync_wait()`, `sync_merge()`, `sync_fence_size()`, and `sync_fence_count_with_status()`.

## Control Flow
This header has no runtime control flow. Compile units include it and link against `sync.c`; tests pass fence fds returned by `sw_sync_fence_create()` or `sync_merge()` into the declared helpers.

## State And Persistence
No state is held here. The status constants are a stable contract between test assertions and kernel-reported fence state.

## Dependencies And Integration Points
Integrated with `sync.c`, `sw_sync.h`, and all sync test cases. It intentionally does not include Linux ioctl headers itself, keeping callers focused on the small helper API.

## Risks
If kernel sync status values change, the hard-coded constants would silently invalidate assertions. The header also exposes only integer fd APIs, so ownership and close responsibilities remain implicit in callers.

## Test Signals
Compilation of all sync selftests against this header and correct active/signaled/error counts in the linked tests are the main signals.
