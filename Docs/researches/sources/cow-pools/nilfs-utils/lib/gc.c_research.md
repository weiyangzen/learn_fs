# File Research: sources/cow-pools/nilfs-utils/lib/gc.c

Implements NILFS garbage collection logic. It scans selected segments, filters unreclaimable or protected segments, parses segment summaries into virtual block descriptors and DAT block descriptors, queries live mapping data from the kernel, removes live/protected/snapshot-covered blocks from deletion candidates, unifies checkpoint deletion periods, and finally calls `nilfs_clean_segments()`.

`nilfs_xreclaim_segment()` is the main enhanced API. It requires `NILFS_RECLAIM_PARAM_PROTSEQ`, blocks signals, takes the cleaner lock, supports dry-run assessment, fills detailed reclaim stats, and can defer cleaning by updating `sui_lastmod` through `nilfs_set_suinfo()` when reclaimable blocks are below a configured threshold.

The file carefully distinguishes virtual file blocks from real DAT blocks and protects snapshots and recent checkpoints.
