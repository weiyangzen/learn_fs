# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap.h

## Purpose
`xfs_rmap.h` declares reverse mapping owner helpers, packed-offset helpers, low-level btree operations, deferred intent APIs, owner query APIs, and optional live update hook interfaces.

## Important APIs and types
`xfs_rmap_ino_owner` and `xfs_rmap_ino_bmbt_owner` construct `xfs_owner_info` for inode data/attr fork extents and bmbt blocks. `xfs_rmap_irec_offset_pack` and `xfs_rmap_irec_offset_unpack` encode/decode fork, bmbt, and unwritten flags into the high bits of the on-disk offset field; `xfs_owner_info_pack` and `xfs_owner_info_unpack` convert between owner-info and rmap flags.

The header declares direct update/query primitives, `enum xfs_rmap_intent_type`, `struct xfs_rmap_intent`, deferred enqueue functions for file and metadata changes, and the finisher `xfs_rmap_finish_one`. It also defines `struct xfs_rmap_matches` for owner-count analysis and `struct xfs_rmap_update_params` for live hook callbacks.

## Control flow and integration
Callers choose between direct AG operations (`xfs_rmap_alloc`, `xfs_rmap_free`) and deferred operations (`xfs_rmap_map_extent`, `xfs_rmap_unmap_extent`, conversion, metadata alloc/free). The finisher uses the encoded intent to update the persistent rmapbt. Scrub/repair callers use `xfs_rmap_query_range`, `xfs_rmap_query_all`, owner counting, and raw map insertion.

## State and persistence behavior
The header defines no persistent storage, but its packed offset format is part of the on-disk rmap record contract. `XFS_RMAP_OINFO_SKIP_UPDATE` uses owner `XFS_RMAP_OWN_NULL` to suppress owner updates; `XFS_RMAP_OINFO_ANY_OWNER` uses `XFS_RMAP_OWN_UNKNOWN` for wildcard-style recovery paths.

## Dependencies, risks, and test signals
The API depends on `xfs_btree_cur`, transactions, inodes, bmbt records, perag/rtgroup structures, and optional `CONFIG_XFS_LIVE_HOOKS`. Risks center on mismatched packed flag semantics and misuse of skip/unknown owner sentinels. Tests should cover owner-info round trips, deferred intent dispatch, hook enable/disable behavior, and rmap query callbacks.
