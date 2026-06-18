# sources/distributed-fs/ceph-client/fs/btrfs/block-rsv.h

## Purpose
`block-rsv.h` declares the Btrfs metadata block reserve abstraction used throughout the filesystem. It defines reserve types, the `struct btrfs_block_rsv` accounting fields, public reserve manipulation APIs, and small inline helpers for returning or reading reserved bytes.

## Important APIs, types, and functions
- `enum btrfs_rsv_type` distinguishes reserve purposes: global, delalloc, transaction, chunk, remap, delayed operations, delayed refs, tree log, empty fallback, and temporary.
- `struct btrfs_block_rsv` stores the target size, current reserved bytes, backing `btrfs_space_info`, spinlock, `full`/`failfast` flags, type, and qgroup reservation size/reserved counters.
- Declarations cover initialization/allocation/freeing, reserve add/check/refill/migrate/use/add-bytes/release, global reserve init/update/release, root reserve initialization, reserve selection for tree block allocation, and truncate cache free-space checking.
- `btrfs_unuse_block_rsv()` returns one tree-block-sized allocation to a reserve and releases any resulting excess.
- `btrfs_block_rsv_full()` is a lockless fast-path fullness check for contexts where a stale value is acceptable.
- `btrfs_block_rsv_reserved()` and `btrfs_block_rsv_size()` provide KCSAN-safe locked reads of mutable counters.

## Control flow
The header’s API describes a simple reserve lifecycle. A caller initializes a reserve and binds it to a metadata-like `space_info`, adds or refills bytes through the implementation, consumes bytes when allocating tree blocks, and releases the remaining size at operation completion. Root and filesystem initialization use the declarations to wire each Btrfs tree or operation class to the correct reserve. `btrfs_unuse_block_rsv()` is the inverse of a single tree block use: it credits bytes back, then lets the implementation free or re-route surplus.

## State and persistence behavior
Reserve state is not persisted on disk. It is an in-memory view of metadata reservation obligations, protected by `struct btrfs_block_rsv::lock` and tied to `btrfs_space_info` accounting. The `full` flag is cached state used by fast paths and can be read without locking only when staleness is acceptable. `failfast` is used by temporary/unbounded operations such as truncate so they can stop and re-reserve instead of consuming emergency space indefinitely.

The qgroup fields track a quota-oriented upper bound rather than exact metadata tree block needs. They are part of the same reserve object so quota release can be correlated with normal metadata reserve release.

## Dependencies and integration points
The header depends only on Linux types/compiler/spinlock definitions plus forward declarations of Btrfs transaction, root, space-info, filesystem, and reserve-flush types. It is included by inode, transaction, delalloc, extent-tree, block-group, and qgroup-related code that needs to reserve or consume metadata.

## Risks and test signals
Risks include callers reading `size`/`reserved` directly without locking, using the wrong reserve type for a tree, forgetting to release temporary reserves, or treating a stale `full` result as authoritative. API changes should be tested with metadata ENOSPC stress, qgroup workloads, fsync/tree-log paths, truncate/iput loops, chunk-tree updates, and unmount assertions that all long-lived reserves have zero size and reserved bytes.
