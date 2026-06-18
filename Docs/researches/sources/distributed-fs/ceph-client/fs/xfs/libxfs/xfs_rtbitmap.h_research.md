# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtbitmap.h

## Purpose
`xfs_rtbitmap.h` declares realtime bitmap/summary helper types, geometry conversions, inline accessors for legacy and rtgroup formats, query callback contracts, and exported realtime free/query/create functions.

## Important APIs and types
`struct xfs_rtalloc_args` bundles the target rtgroup, mount, transaction, cached bitmap buffer, cached summary buffer, and their file offsets. Conversion helpers translate among realtime blocks, realtime extents, realtime group block numbers, file offsets, bitmap file blocks, bitmap words, and summary offsets. Accessors such as `xfs_rbmblock_wordptr`, `xfs_rtbitmap_getword`, `xfs_rtbitmap_setword`, `xfs_rsumblock_infoptr`, `xfs_suminfo_get`, and `xfs_suminfo_add` abstract endianness and header offsets for rtgroup versus legacy formats.

`struct xfs_rtalloc_rec` and `xfs_rtalloc_query_range_fn` define callback-based free-space iteration. Under `CONFIG_XFS_RT`, the header declares buffer reads, range checks, find/modify helpers, summary helpers, free operations, free-space queries, geometry calculations, file initialization, and bitmap/summary inode creation. Without realtime support, important operations return `-ENOSYS`.

## Control flow and integration
The inline conversions are used throughout realtime allocation, free, scrub, and growfs code. Callers prepare `xfs_rtalloc_args`, invoke bitmap or summary helpers, and must release cached buffers with `xfs_rtbuf_cache_relse`. `xfs_rtblock_ops` selects CRC/header-aware buffer ops for rtgroups and generic ops for legacy metadata.

## State and persistence behavior
The header defines how persistent bitmap and summary words are interpreted. Legacy format stores native words at the start of the buffer; rtgroup format skips `struct xfs_rtbuf_blkinfo` and stores big-endian words. Summary offsets are derived from summary level and bitmap block number, then translated to metadata file block and in-block word.

## Dependencies, risks, and test signals
The header depends on mount realtime geometry fields, rtgroup structures, buffer ops, transaction types, and config gating. Risks are conversion drift for power-of-two versus non-power-of-two realtime extent sizes, endianness mistakes, and incorrect rtgroup header offset handling. Tests should cover all conversion helpers, `CONFIG_XFS_RT` stubs, rtgroup and legacy word accessors, and summary offset calculations.
