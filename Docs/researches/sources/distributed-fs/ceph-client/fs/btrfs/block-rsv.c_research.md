# sources/distributed-fs/ceph-client/fs/btrfs/block-rsv.c

## Purpose
`block-rsv.c` implements Btrfs metadata block reserves: in-memory buckets that group pessimistic metadata reservations by purpose and move bytes between `space_info->bytes_may_use`, reserve-local `reserved`/`size` counters, and fallback/global reserves. These reserves are what let transactions, delayed refs, delayed items, delalloc, tree log, chunk updates, remap updates, truncate, and emergency fallback paths account for metadata before they allocate tree blocks.

## Important APIs, types, and functions
- `btrfs_init_block_rsv()`, `btrfs_init_metadata_block_rsv()`, `btrfs_alloc_block_rsv()`, and `btrfs_free_block_rsv()` initialize or allocate reserve objects and bind them to metadata/system/remap `space_info` instances.
- `btrfs_block_rsv_add()` reserves metadata bytes through `btrfs_reserve_metadata_bytes()` and grows both `size` and `reserved`.
- `btrfs_block_rsv_refill()` tops up `reserved` without changing `size`.
- `btrfs_block_rsv_release()` and internal `block_rsv_release_bytes()` shrink a reserve, return excess bytes to the delayed-ref reserve, global reserve, or `space_info`, and optionally report qgroup metadata to release.
- `btrfs_block_rsv_use_bytes()` consumes reserved bytes for a tree block allocation; `btrfs_block_rsv_add_bytes()` puts bytes back into a reserve.
- `btrfs_block_rsv_migrate()` atomically consumes from one reserve and credits another.
- `btrfs_update_global_block_rsv()`, `btrfs_init_global_block_rsv()`, and `btrfs_release_global_block_rsv()` maintain filesystem-wide fallback reserves.
- `btrfs_init_root_block_rsv()` chooses a root’s default reserve according to tree type.
- `btrfs_use_block_rsv()` selects and consumes the correct reserve for a tree block allocation, including global fallback and emergency metadata reservation.
- `btrfs_check_trunc_cache_free_space()` verifies that truncate/cache cleanup has enough metadata slack.

## Control flow
The file starts with a detailed design comment: callers reserve bytes into a logical bucket, use bytes when allocating tree blocks, and release unused excess at operation completion. Normal reserve addition calls `btrfs_reserve_metadata_bytes()` with a caller-selected flush policy, then records bytes under the reserve spinlock. Refill only asks for the gap between requested bytes and current `reserved`. Use subtracts from `reserved`, marks the reserve not full when it falls below `size`, and returns `-ENOSPC` if insufficient.

Release first shrinks `size`, computes excess `reserved - size`, clamps `reserved` to `size`, and similarly computes qgroup excess. If there are excess bytes, it tries to feed another reserve before freeing to `space_info->bytes_may_use`: delayed-ref reserves release toward the global reserve, while most other reserves release toward the delayed refs reserve if it is not full and uses the same space_info. This keeps highly dynamic delayed refs funded before returning bytes to the general pool.

Global reserve updates are based on the current used bytes of global metadata trees: tree root, extent root, checksum root, free-space tree, optional block-group tree, and optional RAID stripe tree. The reserve also includes unlink/delayed-ref slack, is capped at 512 MiB, updates `bytes_may_use` directly under `space_info->lock`, and can force chunk allocation if it consumes the whole metadata space_info.

When allocating a tree block, `btrfs_use_block_rsv()` picks a reserve from the transaction/root context. Shareable roots, UUID root changes, and checksum additions use the transaction reserve; specific global roots use delayed refs, global, chunk, tree-log, or remap reserves; otherwise the empty reserve is used. If the chosen reserve is short, the function may update the global reserve, reserve metadata without flushing, reject log-tree fallback immediately, consume from the global reserve when compatible, or finally attempt an emergency flush reservation.

## State and persistence behavior
Block reserves are in-memory accounting only; they do not create on-disk records. Their state mirrors metadata reservation obligations already represented by `space_info->bytes_may_use` and related reservation counters. Each reserve tracks `size`, `reserved`, `full`, `failfast`, type, `space_info`, and qgroup upper-bound reservation fields. `fs_info` owns long-lived reserves such as global, transaction, chunk, remap, delayed block, delayed refs, tree log, and empty reserves. Inode-local reserves are embedded in `struct btrfs_inode`.

The qgroup fields deliberately differ from normal metadata reservation sizing: qgroup metadata is based on possible net extent-usage changes rather than checksum sizes or exact tree-block counts. Release can report qgroup excess separately so quota accounting can be unwound consistently.

## Dependencies and integration points
This file depends on space-info reservation helpers, transaction state, block group profile constants, root item accessors, filesystem feature checks, and root IDs. It integrates with transaction start/commit, delayed refs, delayed items, inode delalloc metadata reservation, tree-log fsync, chunk-tree modification, remap-tree updates, qgroups, unlink/truncate recovery, and ENOSPC ticket granting.

## Risks and test signals
The main risks are leaks or double-frees in `bytes_may_use`, incorrect reserve fallback that hides ENOSPC until transaction abort, log tree allocations consuming global emergency space, qgroup reservation mismatches, and races on stale `full` reads. `btrfs_block_rsv_full()` is intentionally a lockless fast path using `data_race()`, while precise reads take the reserve spinlock.

Useful tests include metadata ENOSPC stress, delayed-ref heavy workloads, fsync/log-tree fallback under low space, unlink/truncate on nearly full filesystems, qgroup enabled workloads, zoned tree-log reserve selection, chunk/remap operations, transaction abort injection during reserve use/release, and assertions during unmount that long-lived reserves are fully released.
