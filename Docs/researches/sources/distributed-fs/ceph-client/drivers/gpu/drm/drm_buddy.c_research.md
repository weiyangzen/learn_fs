# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_buddy.c

## Purpose
`drm_buddy.c` contains DRM-specific diagnostic print helpers for the generic GPU buddy allocator. It formats allocator blocks and free-list state but does not allocate or free memory.

## Important APIs, Types, And Functions
`drm_buddy_block_print()` prints one block's offset range and size. `drm_buddy_print()` prints chunk size, total/available/clear-free totals, then counts free blocks per order across each free-tree variant.

## Control Flow
`drm_buddy_print()` emits a summary, iterates orders from `max_order` down to zero, walks each RB tree with `rbtree_postorder_for_each_entry_safe()`, asserts visited blocks are free with `BUG_ON`, computes total free bytes for that order, and prints in KiB or MiB.

## State And Persistence
It reads `struct gpu_buddy` and `struct gpu_buddy_block` state and writes transient output through `struct drm_printer`. No allocator state is modified and nothing is persisted.

## Dependencies And Integration Points
It depends on `linux/gpu_buddy.h`, DRM printer APIs, RB-tree iteration, and size constants. GPU memory managers use it for debugfs or log diagnostics.

## Risks And Edge Cases
The helper does not take allocator locks, so callers must provide a stable allocator view. The diagnostic `BUG_ON` can crash the kernel if corruption is seen. Large sizes rely on correct `u64` formatting.

## Test Signals
Validate output against known allocator layouts, per-order block counts, size unit selection, and lock-protected debugfs/log call sites.
