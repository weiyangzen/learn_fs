# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtsummary.c

## Purpose
`rtsummary.c` scrubs the realtime summary file. It recomputes summary counters from the realtime bitmap into an xfile and compares that computed image against the on-disk rtsummary metadata inode, while also validating summary geometry and file mappings.

## Important APIs, types, and functions
`xchk_setup_rtsummary` allocates `struct xchk_rtsummary`, initializes rtgroup state, optional repair setup, xfile storage, transaction reservation, live summary inode, dquots, and rtgroup locks. Helper APIs include `xfsum_load`, `xfsum_store`, exported `xfsum_copyout`, `xchk_rtsum_inc`, `xchk_rtsum_record_free`, `xchk_rtsum_compute`, `xchk_rtsum_compare`, and main `xchk_rtsummary`.

## Control flow
Setup locks realtime bitmap/summary state and computes expected `rextents`, `rbmblocks`, `rsumblocks`, and `rsumlevels`. Scrub compares superblock/mount geometry and summary inode size/alignment, then runs metadata inode fork scrub. It computes a fresh summary by querying all free extents in the realtime bitmap; each free extent determines a bitmap block offset and length-log bucket whose counter is incremented in the xfile. Comparison first verifies all summary file extents are written, then reads each on-disk rtsummary block and compares it with the xfile-computed words.

## State and persistence
Scrub writes only to the transient xfile and scrub flags. It handles both rtgroup big-endian raw suminfo and legacy in-memory increment formats through `xchk_rtsum_inc`. Repair setup and repair implementation are separate.

## Dependencies and integration points
It depends on rtbitmap correctness, realtime allocation query APIs, xfile pageable storage, bmap read helpers, metadata inode scrub, rtgroup locks, and repair setup through `rtsummary.h`. It treats bitmap corruption as an xref corruption against the bitmap inode.

## Risks and test signals
Risks include counter overflow/mis-bucketing by `highbit`, stale geometry during growfs, byte-order mismatches, unwritten summary extents, and false blame when bitmap is corrupt. Tests should cover varied free extent sizes, empty and full realtime volumes, summary files larger than computed size, mismatched `m_rsumlevels`/`m_rsumblocks`, legacy versus rtgroup raw words, unwritten mappings, and intentionally corrupted bitmap input.
