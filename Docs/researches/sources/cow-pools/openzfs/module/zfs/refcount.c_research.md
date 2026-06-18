# File Research: sources/cow-pools/openzfs/module/zfs/refcount.c

## Summary
Implements ZFS debug reference-count tracking. Under `ZFS_DEBUG`, a refcount can either be a fast untracked atomic count or a tracked AVL tree of holder records.

## Main Responsibilities
- Initializes and destroys the `reference_cache` slab.
- Creates tracked, untracked, or tunable-controlled `zfs_refcount_t` objects.
- Adds and removes references, including multi-reference holds.
- Preserves a short history of recently removed tracked references.
- Transfers counts between refcount objects and transfers ownership tags.
- Answers approximate or exact held/not-held queries depending on tracking mode.

## Key APIs
- `zfs_refcount_init()`, `zfs_refcount_fini()`.
- `zfs_refcount_create()`, `zfs_refcount_create_tracked()`, `zfs_refcount_create_untracked()`.
- `zfs_refcount_destroy()`, `zfs_refcount_destroy_many()`.
- `zfs_refcount_add()`, `zfs_refcount_add_many()`, `zfs_refcount_add_few()`.
- `zfs_refcount_remove()`, `zfs_refcount_remove_many()`, `zfs_refcount_remove_few()`.
- `zfs_refcount_transfer()`, `zfs_refcount_transfer_ownership()`.
- `zfs_refcount_count()`, `zfs_refcount_is_zero()`, `zfs_refcount_held()`, `zfs_refcount_not_held()`.

## Important Behavior
When tracking is disabled, add/remove are atomic count updates. When tracking is enabled, each hold records a holder pointer and reference number in an AVL tree; removal panics if the matching hold does not exist. Removed references can be kept in `rc_removed` for debugging history.

`zfs_refcount_held()` is exact only for tracked counters. For untracked counters it returns true if any reference exists, regardless of holder.

## Risks
This file is compiled only for `ZFS_DEBUG`, so production behavior depends on non-debug definitions elsewhere. Tracked mode has meaningful CPU and memory cost, which is why `reference_tracking_enable` defaults off. Holder identity is pointer/tag based and must be used consistently by callers.
