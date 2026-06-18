# sources/distributed-fs/ceph-client/include/linux/rbtree_augmented.h

Purpose: provides augmented red-black tree support, where user-maintained aggregate data is propagated, copied, and rotated consistently during insert and erase rebalancing.

Important APIs and types: `struct rb_augment_callbacks` supplies `propagate`, `copy`, and `rotate` callbacks. Public helpers include `rb_insert_augmented()`, `rb_insert_augmented_cached()`, `rb_add_augmented_cached()`, `rb_erase_augmented()`, and `rb_erase_augmented_cached()`. Template macros `RB_DECLARE_CALLBACKS()` and `RB_DECLARE_CALLBACKS_MAX()` generate callbacks for common subtree aggregate patterns. Implementation helpers define RB colors, parent/color setters, child replacement, RCU child replacement, and `__rb_erase_augmented()`.

Control flow: users update augmented data on the insertion path before linking, then call augmented insert so rotations update aggregates. Erase selects simple or successor cases, uses `copy()` when a successor replaces a node, propagates changed aggregates, then rebalances with rotation callbacks if needed.

State and persistence: state is caller-owned tree nodes plus caller-defined augmented fields, usually subtree maxima/minima or interval metadata. No persistence exists.

Dependencies and integration points: depends on generic rbtree and RCU helpers. It underpins interval trees and other ordered indexes needing subtree summaries.

Risks and test signals: risks include incorrect compute callbacks, failure to update the insertion path before rebalance, stale augmented data after erase successor replacement, cached-leftmost drift, and RCU replacement ordering errors. Test interval queries after random insert/delete, rotations, duplicate ranges, cached augmented roots, and debug validation of aggregate fields.
