# sources/distributed-fs/ceph-client/fs/exfat/balloc.c

## Purpose
`balloc.c` implements allocation bitmap management for exFAT. It locates and loads the on-disk allocation bitmap from the root directory, keeps bitmap sectors pinned in `sbi->vol_amap`, sets/tests/clears cluster bits, counts used clusters, finds the next free cluster, and implements `FITRIM` support by discarding contiguous free cluster ranges.

## Important APIs, types, and functions
`exfat_load_bitmap()` scans root directory entries for the primary `TYPE_BITMAP` entry and calls `exfat_allocate_bitmap()`. `exfat_allocate_bitmap()` validates bitmap size, allocates the buffer-head array, reads bitmap sectors with readahead, and checks that the bitmap's own clusters are marked allocated via `exfat_test_bitmap_range()`. `exfat_free_bitmap()` releases bitmap buffers.

`exfat_set_bitmap()`, `exfat_clear_bitmap()`, and `exfat_test_bitmap()` mutate or query a single cluster bit. `exfat_find_free_bitmap()` scans little-endian machine-word chunks from a hint cluster and wraps to the beginning. `exfat_count_used_clusters()` counts set bits across the bitmap. `exfat_trim_fs()` walks free-cluster runs under `bitmap_lock` and calls `sb_issue_discard()`.

## Control flow
During mount, `exfat_load_bitmap()` starts at `sbi->root_dir` as an `ALLOC_FAT_CHAIN`, reads dentries cluster by cluster, and stops at a bitmap entry with flags zero. Bitmap allocation computes the expected byte length from `EXFAT_DATA_CLUSTER_COUNT()`, tolerates only oversized on-disk bitmaps, reads each sector into `sbi->vol_amap`, and verifies the bitmap file's clusters are allocated.

Allocation paths in `fatent.c` call `exfat_find_free_bitmap()` to choose clusters and `exfat_set_bitmap()` to mark them. Freeing calls `exfat_clear_bitmap()` and expects an already-set bit; clearing an unset bit is treated as I/O/corruption. `FITRIM` translates byte ranges to cluster ranges, finds successive free clusters, coalesces adjacent free clusters, discards ranges meeting `minlen`, honors fatal signals, and returns trimmed byte count in `range->len`.

## State and persistence behavior
Persistent state is the on-disk allocation bitmap file, represented in memory as buffer heads in `sbi->vol_amap`. Updates mark bitmap buffers dirty and optionally synchronously write them through `exfat_update_bh()`. Runtime fields affected include `sbi->map_clu`, `sbi->map_sectors`, `sbi->vol_amap`, and, indirectly through callers, `sbi->used_clusters` and `sbi->clu_srch_ptr`. `bitmap_lock` serializes allocation/free/trim scans that depend on bitmap consistency.

## Dependencies and integration points
This file depends on directory entry reading (`exfat_get_dentry()`), FAT-chain traversal (`exfat_get_next_cluster()`), readahead (`exfat_blk_readahead()`), buffer-head update helpers, cluster/bitmap macros in `exfat_fs.h`, raw dentry definitions, and block discard APIs. It is used by mount, cluster allocation/free, statfs used-cluster accounting, and file ioctl trim.

## Risks and test signals
Risks include endian/word-size mistakes in bitmap word scanning, trusting a corrupt bitmap size, races if callers mutate bitmap without `bitmap_lock`, incorrect wraparound in `exfat_find_free_bitmap()`, mismatches between bitmap bits and FAT chains, and discard over ranges that are not really free. Useful tests include mount images with valid, oversized, undersized, missing, and self-unmarked bitmaps; allocation/free stress around sector and word boundaries; 32-bit and 64-bit builds; full-volume allocation; trim with different `start/len/minlen`; signal interruption; and fsck-style corrupt bitmap/FAT mismatch images.
