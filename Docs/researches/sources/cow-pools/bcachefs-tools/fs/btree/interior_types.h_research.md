# File Research: sources/cow-pools/bcachefs-tools/fs/btree/interior_types.h

## Purpose

`interior_types.h` defines compact filesystem-level structures for btree interior update allocation, reserve caching, async update tracking, and async node rewrites.

## Types and Constants

### `struct btree_alloc`

Represents a reserved but unused btree node allocation:

- `ob`: open bucket references.
- `k`: padded btree pointer key.

This is stored in the reserve cache to avoid throwing away partially allocated btree node space.

### `BTREE_RESERVE_MAX`

Maximum number of btree nodes that may need to be allocated atomically:

`BTREE_MAX_DEPTH + (BTREE_MAX_DEPTH - 1)`

This covers recursive split needs plus associated parent/root allocation.

### `BTREE_NODE_RESERVE`

Freelist size for btree node reserves:

`BTREE_RESERVE_MAX * 4`

### `struct bch_fs_btree_reserve_cache`

Filesystem cache of allocated btree node disk reservations:

- `lock`
- `nr`
- `data[BTREE_NODE_RESERVE * 2]`

The comment explains why it exists: if a btree node is allocated but unused, freeing it would force the space back through the allocator and can contribute to reserve-allocation livelock. Keeping it cached allows reuse.

### `struct bch_fs_btree_interior_updates`

Tracks active asynchronous interior updates:

- mempool for `struct btree_update`,
- active list,
- unwritten/completion list,
- lock,
- commit lock,
- waitlist,
- worker workqueue and work item.

This structure backs the split/merge/rewrite async completion machinery in `interior.c`.

### `struct bch_fs_btree_node_rewrites`

Tracks queued async node rewrite/merge work:

- active list,
- pending list,
- spinlock,
- waitlist,
- worker workqueue.

Pending rewrites are held until journal replay/RW state permits execution.

## Important Invariants

- Reserve cache is lock-protected and stores ownership of open bucket references.
- Interior update completion has both a general lock and a separate commit lock to serialize sensitive parent/root-key update completion.
- Node rewrite tracking uses a spinlock because it is small, list-oriented queue state.
