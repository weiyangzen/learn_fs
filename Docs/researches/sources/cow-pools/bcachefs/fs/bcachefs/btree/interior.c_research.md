# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/interior.c

This file implements bcachefs interior btree node maintenance: topology checking, node allocation/replacement, root changes, splits, compactions, foreground merges, async rewrites, parent-key updates, reserve caches, and completion of multi-node interior updates.

Core responsibilities:
- Validates interior topology with `bch2_btree_node_check_topology_msg()`: root bounds, child min-key continuity, non-empty interior nodes, and final child max-key coverage.
- Calculates ideal packed-key formats for rewritten nodes and checks whether repacking fits.
- Allocates and frees in-memory btree nodes, including replacement nodes with incremented sequence numbers and recalculated formats.
- Maintains a btree-node reserve cache of allocated open buckets to avoid allocator livelock during multi-level splits.
- Starts `struct btree_update` operations with disk reservations, allocator requests, GC read locking, preallocated replacement nodes, and update range metadata.
- Completes interior updates asynchronously after new nodes are written, marking superblock btree bitmaps, journaling old/new node visibility, updating allocation triggers, unblocking parent writes, flushing writes, and releasing open buckets.
- Transfers journal pins from old nodes being replaced to the enclosing update so old on-disk locations are not freed before replacement nodes become persistent and reachable.
- Updates roots in memory and records root updates for journal persistence.
- Inserts child pointer keys into interior nodes, validates inserted keys, and checks topology after insertion.
- Splits or compacts full nodes via `btree_split()`, including recursive parent insertion and root growth.
- Increases depth explicitly with `bch2_btree_increase_depth()`.
- Attempts foreground sibling merges with `__bch2_foreground_maybe_merge()`, including deferred sibling reads using evicted-size estimates.
- Computes balanced split/merge layouts, predicts packed sizes/formats, and packs source keys into one or two destination nodes.
- Rewrites individual nodes by key or position and schedules async rewrite/merge work.
- Updates a btree node's key in its parent or root journal entry, with special handling for nodes that are not yet reachable.
- Creates fake roots for bringup/new-filesystem initialization.
- Exposes diagnostics for active interior updates and reserve-cache contents.
- Initializes and tears down interior update and async node rewrite workers/mempools.

Interior update model:
- Foreground split/merge/rewrite allocates replacement nodes and mutates in-memory topology under btree locks.
- New nodes are written before the parent/root update is allowed to become durable.
- Parent nodes that reference not-yet-written children are marked write-blocked and linked to the `btree_update`.
- Once child writes complete, worker-side transaction code journals old-node overwrites, new-node keys or roots, and allocation trigger effects.
- Only after new nodes are persistent and reachable are old node pins dropped and open buckets released.

Split/merge behavior:
- `btree_split()` may either compact a node into one replacement or split into two replacements, depending on live key count and whether the failed key would fit after compaction.
- Interior inserts are applied before splitting because child pointer updates must remain atomic and pivots must not bisect coalesced child ranges.
- Root splits allocate a new root and insert child pointers into it.
- Foreground merge considers previous/current/next siblings, first using cached `sib_u64s` or evicted-size estimates, then revalidating parent identity after locks are upgraded.
- Merges can produce one destination node or, for larger three-source merges, two balanced destination nodes.

Important invariants:
- Root nodes are protected from reclaim by the permanent flag while still participating in cache lists.
- Replacement nodes keep owned intent/write refs while reserved; consumed and unused reserves are cleaned through shared rollback/release paths.
- `will_make_reachable` gates writes and key updates for nodes that exist in memory but are not yet durable/reachable from an on-disk parent.
- Topology continuity is expressed by child `min_key` and parent key position as child `max_key`.
- Btree pointer keys must have `sectors_written` stamped before being consumed into parent updates or root records.
- Old nodes must be freed in memory before unlocking new nodes, so readers cannot reacquire stale nodes after a replacement becomes visible.
- Interior update completion uses `commit_lock` to synchronize with `bch2_btree_node_update_key()`.

Dependencies:
- Uses allocation/open-bucket/disk-reservation code, btree cache/locking/iter/read/sort/write helpers, journal pins/reclaim, superblock btree bitmaps, reconcile metadata, data write flags, keylists, and filesystem error handling.
- Interacts directly with `commit.c` through transaction commits and with `interior.h` inline capacity/whiteout helpers.

Risk points:
- Error cleanup is complex because preallocated nodes may be unused, consumed but uncommitted, or already handed to paths.
- Deferred sibling merge estimates must be revalidated after real traversal and parent locking.
- Journal error/read-only transitions are explicitly guarded because interior updates can otherwise run allocation triggers without a durable journal half.
- Parent/root updates involving not-yet-written nodes rely on write blocking and journal pins for crash consistency.
- Root updates, fake roots, and pending rewrites have separate lifecycle paths that must converge before shutdown.
