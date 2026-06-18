<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rbtree_augmented.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/rbtree_augmented.h

## Purpose
This header provides augmented red-black tree callbacks and erase/insert helpers used by interval trees and other metadata-indexed structures.

## APIs And Flow
It defines `struct rb_augment_callbacks`, declares `__rb_insert_augmented()` and `__rb_erase_color()`, provides `rb_insert_augmented()`, `rb_insert_augmented_cached()`, `RB_DECLARE_CALLBACKS()`, `RB_DECLARE_CALLBACKS_MAX()`, color/parent helpers, `__rb_change_child()`, `__rb_erase_augmented()`, `rb_erase_augmented()`, and `rb_erase_augmented_cached()`. Erase handles zero, one, or two child cases, copies augmentation to successors, propagates changes, and rebalances if a black node removal requires it.

## State, Dependencies, Risks, Tests
State is augmentation stored in caller node fields plus rb topology. Dependencies are `linux/compiler.h` and `linux/rbtree.h`. Risks include depending on implementation-detail helpers, callbacks that fail to recompute after rotations, cached-leftmost desynchronization, and code bloat from macro-generated callbacks. Tests should exercise all erase cases, rotations with augmentation recomputation, interval tree users, and cached-tree leftmost updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/rbtree_augmented.h -->
