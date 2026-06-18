# sources/distributed-fs/ceph-client/fs/btrfs/delalloc-space.c

## Purpose

`delalloc-space.c` implements Btrfs delayed-allocation reservation accounting for buffered writes, preallocation, and direct I/O. It separates data space reservation from metadata reservation: data writes first charge `space_info->bytes_may_use`, later real extent allocation moves accounting to reserved/used bytes, and ordered extent completion plus delayed refs finish persistence. Metadata reservations are tracked per inode through `inode->block_rsv`, `outstanding_extents`, and `csum_bytes`, so the filesystem can reserve enough tree space for file extent items, checksum items, and inode updates before dirty ranges are actually materialized.

## Important APIs, Types, and Functions

Public entry points are `btrfs_alloc_data_chunk_ondemand()`, `btrfs_check_data_free_space()`, `btrfs_free_reserved_data_space_noquota()`, `btrfs_free_reserved_data_space()`, `btrfs_delalloc_reserve_metadata()`, `btrfs_delalloc_release_metadata()`, `btrfs_delalloc_release_extents()`, `btrfs_delalloc_shrink_extents()`, `btrfs_delalloc_reserve_space()`, and `btrfs_delalloc_release_space()`.

Important helpers include `data_sinfo_for_inode()`, which chooses the normal data space-info or the zoned data-relocation subgroup, `btrfs_inode_rsv_release()`, which releases excess inode block reservation and qgroup reservation, `btrfs_calculate_inode_block_rsv_size()`, which recalculates per-inode metadata and qgroup reservation targets, and `calc_inode_reservations()`, which computes the immediate reservation for a new range.

## Control Flow

The combined reservation flow is `btrfs_delalloc_reserve_space()`: reserve data bytes through `btrfs_check_data_free_space()`, reserve qgroup data for the exact changed extent set, then reserve metadata with `btrfs_delalloc_reserve_metadata()`. Metadata reservation aligns byte counts, computes maximum extent/checksum leaves, preallocates qgroup metadata, reserves metadata bytes with an appropriate flush policy, updates `outstanding_extents` and `csum_bytes` under `inode->lock`, recalculates `inode->block_rsv`, and finally adds bytes to the block reserve.

Release paths mirror the acquisition paths. `btrfs_delalloc_release_metadata()` subtracts checksum bytes, recalculates the inode reserve, and releases/converts qgroup metadata depending on whether the caller is aborting or handing reservation to the transaction. `btrfs_delalloc_release_extents()` drops temporary outstanding extents once another state, such as delalloc or ordered extents, owns them. `btrfs_delalloc_release_space()` releases both metadata and data/qgroup reservations. `btrfs_delalloc_shrink_extents()` adjusts outstanding extent accounting if a previously reserved range shrinks.

## State and Persistence Behavior

The file owns no durable on-disk format directly. It manages in-memory accounting that enables later persistence through extent allocation, ordered extent completion, checksum insertion, inode item update, and delayed refs. Key mutable state is `space_info->bytes_may_use`, the inode block reserve size/reserved/qgroup fields, `inode->outstanding_extents`, `inode->csum_bytes`, qgroup preallocations, and extent-changeset records for accurate data quota release.

Reservation flush behavior depends on context. Free-space inodes and explicit no-flush paths use no-flush reservation to avoid commit recursion. Existing transactions use limited flush to reduce deadlock risk. Testing mode skips actual inode reserve release in some paths after updating logical counters.

## Dependencies and Integration Points

This file integrates with `block-rsv`, `space-info`, qgroups, inode accounting, delalloc extent-state hooks, ordered extent creation, direct I/O, and ENOSPC flushing. Direct I/O uses `btrfs_delalloc_reserve_metadata()` and `btrfs_delalloc_release_extents()` after it creates ordered extents. Buffered writes use the combined reserve/release APIs around setting and clearing delalloc bits.

## Risks and Edge Cases

Reservation sizes intentionally overestimate to avoid many inodes each holding partial reservations, but overestimation can temporarily pressure ENOSPC behavior. The data and qgroup ranges must stay sector-aligned and must match the `extent_changeset` passed back for release. `outstanding_extents` is lifecycle-based rather than simply dirty-range-based, so missed calls to release temporary extents or metadata can leak reservation; early calls can underreserve tree changes. Zoned relocation uses a special data subgroup and asserts the subgroup id. Qgroup free versus convert semantics are context sensitive and easy to misuse on error paths.

## Test Signals

Useful tests include buffered write ENOSPC and EDQUOT paths, O_DIRECT COW and NOCOW reservation/release paths, checksum and NODATASUM inode variants, shrink-after-partial-allocation behavior, free-space inode no-flush behavior, active-transaction flush-limit behavior, qgroup exact-range release, zoned data relocation reservations, and fault injection around metadata reservation after successful data reservation.
