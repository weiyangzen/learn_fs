# sources/distributed-fs/openafs/src/vol/vg_scan.c

## Purpose

`vg_scan.c` implements the asynchronous partition scanner for the demand-attach volume-group cache. It rebuilds cache state from `.vol` header files and coordinates with concurrent cache deletes while the scan is running.

## Important APIs and Functions

The public-to-private entry point is `_VVGC_scan_start`, declared in `vg_cache_impl.h` and called by `VVGCache_scanStart_r`. The scanner thread runs `_VVGC_scanner_thread`, which calls `_VVGC_scan_partition`. Header walking callbacks are `_VVGC_RecordHeader`, which batches `hdr->id` and `hdr->parent`, and `_VVGC_UnlinkHeader`, which removes invalid volume header files found by `VWalkVolumeHeaders`.

Batching helpers are `_VVGC_scan_table_init`, `_VVGC_scan_table_add`, and `_VVGC_scan_table_flush`. Delete-list helpers are `_VVGC_dlist_lookup_r`, `_VVGC_flush_dlist`, `_VVGC_dlist_add_r`, and `_VVGC_dlist_del_r`.

## Control Flow

`_VVGC_scan_start` changes the partition state to `UPDATING`. If it was already `UPDATING`, it reports a race with `-3`. It allocates per-partition dlist hash buckets, initializes them, configures a detached pthread, and starts `_VVGC_scanner_thread`.

`_VVGC_scan_partition` initializes a local scan table, validates the partition path, flushes old cache entries for the partition under `VOL_LOCK`, opens the partition directory, and calls `VWalkVolumeHeaders`. Each valid header adds a tuple to the local table; if the table reaches `VVGC_SCAN_TBL_LEN`, it flushes to the global cache. A final flush occurs after the walk. On completion, the scanner flushes the delete-list, frees dlist buckets, and transitions the partition state to `VALID` or `INVALID`.

`_VVGC_scan_table_flush` acquires `VOL_LOCK`, skips any tuple present in the delete-list, calls `VVGCache_entry_add_r`, updates counters, and flushes the dlist opportunistically to keep it small. This avoids stale scan results resurrecting entries deleted during a long partition walk.

## State, Persistence, and Concurrency

The scanner reads persistent volume header files but only writes persistence when `_VVGC_UnlinkHeader` deletes illegitimate headers. All cache insertion and delete-list manipulation happens under `VOL_LOCK`, while directory walking and header scanning run without it. The dlist exists only for a partition in `UPDATING` state and is freed before the state transition broadcast.

## Dependencies and Integration Points

The file depends on partition walking (`VPartitionPath`, `VWalkVolumeHeaders`), volume disk headers, queue primitives, pthreads, the global volume lock, and cache internals from `vg_cache_impl.h`. It integrates with `vg_cache.c` add/delete/purge and state-change helpers.

## Risks and Test Signals

Race tests are essential: delete during scan, delete followed by recreate in a different group, duplicate headers, scan start races, pthread creation failure, and invalid partition paths. Error handling should be checked for dlist cleanup on scan-start failures. Scanner tests should also verify that invalid header unlink errors are logged but do not corrupt cache state, and that waiters on `VVGCache_scanWait_r` wake after final state change.
