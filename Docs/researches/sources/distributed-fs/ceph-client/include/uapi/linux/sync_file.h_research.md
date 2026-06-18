# sources/distributed-fs/ceph-client/include/uapi/linux/sync_file.h

## Purpose
Defines the sync_file fence ioctl ABI used by graphics, DMA, and display stacks to merge fences, query fence details, and set scheduling deadline hints.

## Important APIs, Types, and Constants
`struct sync_merge_data` names and merges the calling fence fd with `fd2`, returning a new `fence` fd. `struct sync_fence_info` reports timeline name, driver name, status, flags, and timestamp. `struct sync_file_info` queries a sync file and optionally points to an array of fence info records. `struct sync_set_deadline` carries an absolute `CLOCK_MONOTONIC` deadline. Ioctls are `SYNC_IOC_MERGE`, `SYNC_IOC_FILE_INFO`, and `SYNC_IOC_SET_DEADLINE`; opcode numbers 0-2 are intentionally burned.

## Control Flow, State, and Persistence
Userspace performs a two-pass file-info query when needed: first with `num_fences = 0`, then with a populated user buffer. Fence status evolves in kernel DMA fence state. Deadline hints influence scheduling but are not durable.

## Dependencies and Integration Points
Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with DRM, Android sync framework compatibility, dma-fence, and compositor/display userspace.

## Risks and Test Signals
Risks include invalid user pointers in `sync_fence_info`, stale status races, unsupported deadline semantics, and old API ioctl number confusion. Test merge semantics, two-pass info query, active/signaled/error status transitions, deadline validation, and fd lifecycle.
