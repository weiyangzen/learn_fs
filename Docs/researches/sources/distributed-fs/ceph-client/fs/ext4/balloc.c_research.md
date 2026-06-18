# sources/distributed-fs/ceph-client/fs/ext4/balloc.c

## Purpose

`fs/ext4/balloc.c` provides ext4 block-group/block-allocation support routines used by mballoc, metadata allocation, mount accounting, bitmap validation, and filesystem statistics. In this subset it covers group/block mapping, overhead calculation, lazy bitmap initialization, group descriptor lookup, block bitmap read/verify/wait, free-cluster reservation checks, allocation retry policy, metadata block allocation, free cluster counting, sparse-super/GDT placement, and inode goal-block selection.

## Important APIs, types, and functions

- `ext4_get_group_number()` and `ext4_get_group_no_and_offset()` map physical blocks to block groups and cluster offsets.
- `ext4_free_clusters_after_init()` and `ext4_num_overhead_clusters()` calculate free clusters for uninitialized bitmaps by subtracting superblock/GDT, bitmap, and inode-table metadata.
- `ext4_init_block_bitmap()` materializes an uninitialized group bitmap and sets metadata/padding bits after descriptor checksum verification.
- `ext4_get_group_desc()` safely indexes the RCU-managed group descriptor buffer array and returns a descriptor pointer.
- `ext4_get_group_info()` returns in-memory mballoc group info.
- `ext4_read_block_bitmap_nowait()`, `ext4_wait_block_bitmap()`, and `ext4_read_block_bitmap()` fetch and validate a block bitmap, handling uninitialized bitmap groups, async reads, readahead, checksum verification, padding verification, and corruption marking.
- `ext4_validate_block_bitmap()` combines checksum, required metadata bit checks, and padding checks under group lock.
- `ext4_claim_free_clusters()` and `ext4_has_free_clusters()` reserve dirty clusters after accounting for free, dirty, root-reserved, and delayed-reserved pools.
- `ext4_should_retry_alloc()` decides whether ENOSPC allocation should retry after journal commit or discard work.
- `ext4_new_meta_blocks()` allocates metadata clusters through mballoc and accounts delayed-allocation reserved quota.
- `ext4_count_free_clusters()` sums descriptor free-cluster counts, skipping bitmap-corrupt groups.
- `ext4_bg_has_super()`, `ext4_bg_num_gdb()`, `ext4_num_base_meta_blocks()`, and helpers model sparse-super, sparse-super2, meta_bg, and reserved GDT placement.
- `ext4_inode_to_goal_block()` picks allocation locality from inode group, flex_bg policy, delayed allocation, and process-coloring.

## Control flow

Bitmap read starts with descriptor lookup and bitmap block range validation. If the buffer is locked and the caller is only prefetching, it returns `NULL`. If the buffer is already uptodate, validation runs immediately. Otherwise it locks the buffer, handles checksum-protected uninitialized groups by creating the bitmap in memory, or submits metadata IO with `ext4_read_bh_nowait()`. Synchronous callers then wait, check IO success, clear `buffer_new`, and validate.

Allocation admission reads percpu counters quickly, falls back to summed counters near watermark, and allows reserved block use for root/reserved users, explicit root-block flags, `CAP_SYS_RESOURCE`, or `EXT4_MB_USE_RESERVED`. ENOSPC retry is journaling-aware: without a journal it does not retry; with pending frees it forces a nested commit up to three times, and with no pending frees it may flush discard work and recheck free clusters.

## State and persistence behavior

Persistent state includes group descriptors, block bitmap blocks, inode bitmap/table locations, descriptor checksums, free-cluster counts, backup superblocks, and group descriptor table backups. In-memory state includes group descriptor buffer arrays, group info corruption flags, percpu free/dirty cluster counters, reservation counters, journal state, discard work state, and buffer flags such as uptodate/verified/new. Lazy block bitmap initialization changes buffer contents in memory and later persistence is coordinated by callers.

## Dependencies and integration points

The file depends on ext4 superblock/group descriptor layout, mballoc APIs, JBD2 journaling, buffer-head IO, block bitmap checksum helpers in `bitmap.c`, tracepoints from `<trace/events/ext4.h>`, KUnit static stubs, quota accounting, capability checks, flex_bg helpers, and simulated failure hooks. Many higher-level ext4 paths call these helpers indirectly through mballoc and metadata allocation.

## Risks and edge cases

Bitmap validation is critical because a missing metadata bit can allow allocation over filesystem metadata. Flex_bg intentionally skips local bitmap metadata checks because metadata can live outside the group, so corruption detection differs by feature. Last group sizes, bigalloc cluster conversion, meta_bg/sparse_super2 placement, and reserved GDT accounting are all geometry-sensitive. RCU descriptor access assumes buffer lifetime rules held by the broader superblock state. Free-space admission depends on approximate percpu counters and must account dirty clusters to avoid overcommit.

## Test signals

Test block-to-group mapping with standard and `STD_GROUP_SIZE` modes, last partial groups, bigalloc clusters, sparse_super/sparse_super2/meta_bg combinations, uninitialized bitmap creation, checksum failure injection, padding-bit corruption, invalid bitmap block numbers, ENOSPC retry with pending journal frees and discard work, reserved block access by root/group/capability, KUnit stubs for bitmap reads/descriptors, and goal block selection for directories, regular files, flex_bg, and delalloc.
