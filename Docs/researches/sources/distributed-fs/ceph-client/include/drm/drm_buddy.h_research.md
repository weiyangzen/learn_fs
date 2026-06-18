# sources/distributed-fs/ceph-client/include/drm/drm_buddy.h

## Purpose
This header exposes DRM printer helpers for the generic GPU buddy allocator. It is diagnostic glue between `linux/gpu_buddy.h` memory-management state and DRM debug output.

## Important APIs, types, and functions
It declares `drm_buddy_print(struct gpu_buddy *mm, struct drm_printer *p)` for whole allocator dumps and `drm_buddy_block_print(struct gpu_buddy *mm, struct gpu_buddy_block *block, struct drm_printer *p)` for individual block dumps.

## Control Flow
Drivers or debugfs callbacks call the print helpers with an allocator or block and a DRM printer. The helpers format allocator state into the selected print sink.

## State and Persistence
The header owns no state. It observes in-memory GPU buddy allocator state and emits diagnostics without changing allocation metadata.

## Dependencies and Integration Points
It depends on the generic `gpu_buddy` allocator and `drm_printer`. It integrates with DRM memory manager debugfs and driver diagnostics.

## Risks and Test Signals
Risks are mostly diagnostic: racing allocator mutation while printing, incomplete block context, or output that becomes misleading for corrupted allocator state. Tests should cover empty, fragmented, fully allocated, and partially freed allocators, block-level printing for root and leaf blocks, and debugfs invocation under allocator locks.
