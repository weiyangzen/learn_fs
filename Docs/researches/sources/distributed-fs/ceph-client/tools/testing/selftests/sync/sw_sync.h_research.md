# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sw_sync.h

## Purpose
Header declaring the userspace abstraction for Android-style software sync timelines and fences used by sync selftests.

## Important APIs, types, and functions
Declares timeline functions `sw_sync_timeline_create()`, `sw_sync_timeline_is_valid()`, `sw_sync_timeline_inc()`, `sw_sync_timeline_destroy()` and fence functions `sw_sync_fence_create()`, `sw_sync_fence_is_valid()`, `sw_sync_fence_destroy()`.

## Control flow
No executable flow; implementation is in other sync sources.

## State and persistence
The API manages file descriptors for timelines and fences; this header only declares ownership boundaries.

## Dependencies and integration points
Included by sync allocation/fence/merge/wait/stress tests and their implementation files.

## Risks
The header notes sw_sync is intended for testing, not production kernels. Callers must destroy fds to avoid leaks.

## Test signals
Tests use validity helpers and fd creation/destruction paths declared here to report sync behavior success or failure.
