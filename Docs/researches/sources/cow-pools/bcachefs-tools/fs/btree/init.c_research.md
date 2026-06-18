# File Research: sources/cow-pools/bcachefs-tools/fs/btree/init.c

## Purpose

`init.c` contains btree subsystem lifecycle initialization/teardown plus an extensive embedded design document explaining bcachefs btree architecture.

## Embedded Design Documentation

The file documents bcachefs as a transactional key-value store built on B+trees. It states that filesystem metadata such as extents, inodes, dirents, allocation state, snapshots, quotas, stripes, and accounting all live as key-value pairs in btrees rather than separate specialized structures.

Documented btree groups include:

- Core filesystem data: extents, inodes, dirents, xattrs, reflink.
- Allocation and space management: alloc, freespace, need_discard, bucket_gens, backpointers.
- Snapshots/subvolumes: subvolumes, snapshots, snapshot_trees, subvolume_children, deleted_inodes.
- Reconcile/background maintenance queues.
- Other metadata: quotas, stripes, LRU, logged ops, accounting.

The documentation emphasizes:

- Shallow large btree nodes for scale.
- Atomic cross-object operations through shared transactions.
- Online fsck/repair through the transaction and locking infrastructure.
- Efficient background maintenance via backpointers.
- Snapshot efficiency through snapshot-aware key positions.
- No duplicate keys.
- Deletion by whiteouts because written bsets cannot be modified in place.
- Ordering preservation through journal sequencing.
- Log-structured btree nodes composed of multiple sorted bsets.
- Packed on-disk keys via `bkey_format`.
- Interior btree pointers whose key position is child max key and whose value includes child `min_key`.

## Lifecycle Functions

### `bch2_fs_btree_exit()`

Destroys btree subsystems in reverse-ish dependency order:

- node scan,
- write buffer,
- key cache,
- iterators,
- interior update subsystem,
- evicted-size table,
- btree cache,
- read/write completion workqueues,
- bounce/fill pools and bioset.

### `bch2_fs_btree_init_early()`

Initializes lock/list-only and early structures:

- btree cache,
- interior update state,
- iterators,
- write buffer,
- node scan.

This is early enough to run before full allocation-backed initialization.

### `bch2_fs_btree_init()`

Allocates core btree runtime resources:

- sets foreground merge threshold,
- computes sort iterator pool size from btree block count,
- creates high-priority read completion workqueue,
- initializes fill iterator mempool,
- initializes btree bio set,
- initializes bounce buffer mempool sized to btree node size,
- initializes btree cache,
- initializes iterators,
- initializes key cache,
- initializes read error ratelimiters.

Returns `ENOMEM_fs_other_alloc` on allocation failure.

### `bch2_fs_btree_init_rw()`

Initializes RW-only btree resources:

- high-priority write completion workqueue,
- interior update worker/pool,
- write buffer,
- evicted-size tracking.

This separates mount/read preparation from resources only needed after RW transition.

## Dependencies

Includes btree cache, init, interior, key cache, node scan, read, sort, write, and write buffer headers.

## Important Invariants

- Workqueues and mempools must be torn down only after dependent btree subsystems are stopped.
- `foreground_merge_threshold` is computed from runtime filesystem geometry/options.
- RW initialization is separate because some resources and workers are not valid or needed during early recovery.
