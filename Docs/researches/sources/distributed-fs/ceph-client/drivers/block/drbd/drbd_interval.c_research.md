# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_interval.c

## Purpose
`drbd_interval.c` implements DRBD's augmented red-black interval tree helpers. DRBD uses these trees to track in-flight local and peer I/O ranges, detect overlapping requests, and wait/restart conflicting operations without scanning every request.

## Important APIs, Types, And Functions
The file implements `drbd_insert_interval`, `drbd_contains_interval`, `drbd_remove_interval`, `drbd_find_overlap`, and `drbd_next_overlap`. Internal helpers are `interval_end`, `NODE_END`, and `RB_DECLARE_CALLBACKS_MAX`-generated `augment_callbacks`. The implementation operates on `struct drbd_interval` from `drbd_interval.h`, where `sector` is the start sector, `size` is bytes, and `end` caches the maximum end sector in a subtree.

## Control Flow
`drbd_insert_interval` verifies 512-byte alignment, walks the tree by start sector, and uses pointer address ordering to break ties when multiple intervals start at the same sector. During descent it opportunistically raises ancestor `end` values to include the new interval end, then links and rebalances the node with augmented rbtree callbacks. If the exact same interval node is already present, it returns `false`.

`drbd_contains_interval` searches by the caller-supplied sector and pointer ordering. It is intentionally safe for membership checks where the interval pointer may be invalid or stale: it does not dereference the interval argument unless the tree search has proven identity by pointer comparison. `drbd_remove_interval` ignores already-cleared nodes to avoid repeated erase loops and otherwise calls `rb_erase_augmented`.

`drbd_find_overlap` searches for the first interval overlapping `[sector, sector + size)`. It first follows a left subtree if that subtree's augmented maximum end could overlap the query. Otherwise it checks the current node, then moves right if the query starts at or after the current node's sector. When it finds an overlap, the returned node is the lowest-start overlapping interval; other overlaps can be found via `drbd_next_overlap`. `drbd_next_overlap` walks `rb_next` until it reaches the query end or finds another interval whose end exceeds the query start.

## State And Persistence
The file owns no global state and performs no persistence. It mutates only the passed `rb_root` and the embedded `rb_node`/`end` fields inside `struct drbd_interval`. Tree lifetime, synchronization, and interval ownership are controlled by callers, typically under DRBD's request lock. `end` is derived state and must stay synchronized with `sector` and `size`.

## Dependencies
It depends on Linux rbtree augmented callbacks, sector types, alignment macros, `BUG_ON`, and `drbd_interval.h`. It assumes sizes are 512-byte aligned because all interval math converts bytes to sectors with `size >> 9`.

## Integration Points
`drbd_device` embeds separate `read_requests` and `write_requests` rb roots, and `struct drbd_request` and `struct drbd_peer_request` embed `struct drbd_interval`. Activity-log and request paths use overlap detection to prevent conflicting local/remote writes, coordinate two-primary conflict handling, and decide when requests must wait on `device->misc_wait`.

## Risks
The interval tree relies on strict invariants: callers must initialize nodes with `drbd_clear_interval`, must not mutate `sector` or `size` while inserted, must not insert unaligned sizes, and must erase before freeing an interval owner. Pointer-order tie breaking is deterministic only within one kernel lifetime and is suitable for in-memory identity, not persisted ordering. `drbd_remove_interval` does not clear the node after erase; callers that need `drbd_interval_empty` to become true must clear it themselves. Missing caller-side locking can corrupt the rb tree or the augmented `end` values. Integer overflow in `sector + (size >> 9)` is not guarded here and is expected to be prevented by upper-layer block-size limits.

## Test Signals
Focused tests should insert overlapping and non-overlapping intervals, duplicate start-sector intervals, exact duplicate nodes, left-subtree-only overlaps, removal/reinsertion sequences, and `drbd_for_each_overlap` iteration order. Stress signals include concurrent DRBD request workloads under lockdep, two-primary conflict tests, activity-log wait/retry tests, and boundary cases near maximum bio size and high sector numbers.
