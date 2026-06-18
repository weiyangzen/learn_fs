# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sync.c

## Purpose
Provides the userspace helper layer used by the sync selftests. It wraps Linux `sync_file` ioctls and the debugfs `sw_sync` test driver so the individual test files can create timelines, create fences, merge fences, wait on fence file descriptors, and inspect fence status counts without duplicating ioctl setup.

## Important APIs, Types, And Functions
Public helpers are `sync_wait()`, `sync_merge()`, `sync_fence_size()`, `sync_fence_count_with_status()`, `sw_sync_timeline_create()`, `sw_sync_timeline_inc()`, `sw_sync_timeline_is_valid()`, `sw_sync_timeline_destroy()`, `sw_sync_fence_create()`, `sw_sync_fence_is_valid()`, and `sw_sync_fence_destroy()`. The file defines local `SW_SYNC_IOC_CREATE_FENCE` and `SW_SYNC_IOC_INC` ioctl numbers plus `struct sw_sync_create_fence_data`, while consuming `struct sync_merge_data`, `struct sync_file_info`, and `struct sync_fence_info` from `<linux/sync_file.h>`.

## Control Flow
Creation paths open `/sys/kernel/debug/sync/sw_sync`, then create fences by issuing `SW_SYNC_IOC_CREATE_FENCE` against the timeline fd. `sync_merge()` submits `SYNC_IOC_MERGE` on the first fence fd and returns the kernel-provided merged fence fd. `sync_file_info()` performs the two-stage `SYNC_IOC_FILE_INFO` query: first to learn `num_fences`, then with a caller-allocated `sync_fence_info` array attached through the 64-bit pointer field. Status helpers iterate that returned array and free all temporary allocations before returning.

## State And Persistence
The only persistent state is in kernel-owned file descriptors: timeline fds, fence fds, and merged fence fds. Userspace state is temporary allocation for `SYNC_IOC_FILE_INFO`. The validity helpers use `fcntl(F_GETFD)` and destruction is just `close()` when the fd is valid.

## Dependencies And Integration Points
Depends on debugfs `sw_sync` support, `SYNC_IOC_*` ABI definitions, libc `poll`, `open`, `ioctl`, `fcntl`, and `close`, and the public prototypes in `sync.h` plus `sw_sync.h`. All sync allocation, merge, wait, and stress tests call through this file.

## Risks
The helper assumes the debugfs sw_sync node exists and is accessible, so tests skip or fail depending on mount/permission state. The pointer cast through `uint64_t` must match the kernel ABI. `sync_fence_size()` returns `0` both for an empty fence set and for info-query failure, while `sync_fence_count_with_status()` returns `-1` on failure, so callers need to distinguish those semantics. Tests that forget to close merged fds can exhaust file descriptors during stress runs.

## Test Signals
Good signals are successful timeline/fence allocation, `poll()` returning timeout before signaling and readiness after timeline increments, `SYNC_IOC_FILE_INFO` reporting expected active/signaled/error counts, and stable behavior under repeated merges in the stress tests.
