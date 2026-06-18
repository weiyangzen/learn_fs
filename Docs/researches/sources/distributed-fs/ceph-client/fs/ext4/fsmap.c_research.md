# sources/distributed-fs/ceph-client/fs/ext4/fsmap.c

## Purpose
`fsmap.c` implements ext4 support for `FS_IOC_GETFSMAP`, reporting physical block ownership maps for the data device and optional external journal device. It converts user-visible byte-addressed `struct fsmap` requests into ext4 block/cluster queries, fabricates records for fixed filesystem metadata and journal space, reports free space from mballoc, and emits unknown-owner gaps when no better reverse mapping exists.

## Important APIs, types, and functions
The public helpers are `ext4_fsmap_from_internal`, `ext4_fsmap_to_internal`, and `ext4_getfsmap`. Internal state is carried by `struct ext4_getfsmap_info` and `struct ext4_getfsmap_dev`. Major helpers include `ext4_getfsmap_helper`, `ext4_getfsmap_meta_helper`, `ext4_getfsmap_datadev_helper`, `ext4_getfsmap_logdev`, `ext4_getfsmap_fill`, `ext4_getfsmap_find_sb`, `ext4_getfsmap_compare`, `ext4_getfsmap_merge_fixed_metadata`, `ext4_getfsmap_find_fixed_metadata`, `ext4_getfsmap_datadev`, `ext4_getfsmap_is_valid_device`, and `ext4_getfsmap_check_keys`.

## Control flow
`ext4_getfsmap()` validates flags and device keys, creates sorted device handlers for the main block device and optional external journal, converts the low key into a resume point by adding its length, verifies low/high ordering, and dispatches each selected device. The data-device handler clamps the query to filesystem block bounds, derives start/end block groups, builds a sorted/merged list of fixed-location metadata, and queries each group through `ext4_mballoc_query_range`. Metadata and free-space callbacks merge fixed metadata with free extents, retain free extents at block-group boundaries for cross-group merging, and pass each mapping to `ext4_getfsmap_helper`. The helper handles count-only mode, output-limit aborts, unknown gaps, tracing, and formatter callbacks. The log-device handler fabricates one record for the external journal.

## State and persistence behavior
The file is read-only from the filesystem perspective. Runtime state consists of query cursors (`gfi_next_fsblk`, low/high keys, last retained free extent, metadata list, current group/device) and allocated metadata-list entries. It reports persistent ownership from group descriptors, bitmaps, inode tables, free-space bitmaps, and journal geometry but does not mutate them.

## Dependencies and integration points
It integrates with the generic fsmap ioctl ABI, ext4 block group descriptors, buddy allocator range queries, fixed metadata layout helpers, external journal device state, Linux sorting/list APIs, and ext4 tracepoints. Owner constants are defined in `fsmap.h`.

## Risks and test signals
Risks include unit conversion errors between bytes, blocks, and clusters, off-by-one high-key clipping, resume-key duplication or skipping, missing metadata/free-space merge boundaries, memory leaks on early errors, invalid external journal device ordering, count-only overflow behavior, and unknown-gap over-reporting. Test signals include count-only and bounded-output calls, resumed queries using the last returned record, filesystems with flex_bg/meta_bg/sparse superblocks/bigalloc, external journal devices, first/last block boundary queries, signal interruption, metadata checksum corruption, and comparison against `debugfs`/`filefrag` expectations.
