# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync_alloc.c

## Purpose
Contains allocation-focused sync selftests that verify the `sw_sync` debugfs driver can allocate timelines and fences and rejects fence creation on an invalid timeline fd.

## Important APIs, Types, And Functions
Implements `test_alloc_timeline()`, `test_alloc_fence()`, and `test_alloc_fence_negative()`. These use `sw_sync_timeline_create()`, `sw_sync_timeline_is_valid()`, `sw_sync_fence_create()`, `sw_sync_fence_is_valid()`, and the destruction helpers, with assertions from `synctest.h`.

## Control Flow
Each test creates a timeline, validates it, then optionally creates and validates a fence. The negative case intentionally calls `sw_sync_fence_create(-1, ...)` and expects a negative return. Cleanup closes any valid fence and timeline before returning success.

## State And Persistence
State is limited to local file descriptors. The kernel owns the actual timeline and fence objects until their fds are closed.

## Dependencies And Integration Points
Depends on the shared helper layer in `sync.c`, the `sw_sync` test driver node, and the kselftest runner in `sync_test.c`, which invokes these functions in isolated child processes.

## Risks
The tests assume fd validity checks are enough to prove allocation success. `test_alloc_fence_negative()` checks `timeline > 0` rather than the shared validity helper, so an unusual valid fd `0` would be treated as failure. The negative fence fd is passed to destroy, which is safe because the helper validates first.

## Test Signals
Pass signals are valid timeline fd allocation, valid fence fd allocation, and failure from fence creation with fd `-1`.
