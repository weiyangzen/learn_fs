# sources/distributed-fs/ceph-client/fs/nilfs2/sufile.c

## Purpose

`sufile.c` implements the NILFS2 segment usage metadata file. The sufile records whether each segment is clean, dirty, active, or erroneous, how many live blocks it contains, and its last modification time. It provides segment allocation/freeing, accounting, resizing, suinfo ioctl access, and fstrim discard of clean segments.

## Important APIs, Types, and Functions

`struct nilfs_sufile_info` extends `struct nilfs_mdt_info` with cached `ncleansegs` and allocation range limits `allocmin`/`allocmax`.

Core mutation APIs are `nilfs_sufile_alloc()`, `nilfs_sufile_free()`/`freev()`, `nilfs_sufile_scrap()`, `nilfs_sufile_cancel_freev()`, `nilfs_sufile_mark_dirty()`, `nilfs_sufile_set_segment_usage()`, and `nilfs_sufile_set_error()`. Generic update wrappers `nilfs_sufile_update()` and `nilfs_sufile_updatev()` obtain header and entry blocks under `mi_sem` and call primitive update functions.

Management APIs include `nilfs_sufile_set_alloc_range()`, `nilfs_sufile_resize()`, `nilfs_sufile_get_stat()`, `nilfs_sufile_get_suinfo()`, `nilfs_sufile_set_suinfo()`, `nilfs_sufile_trim_fs()`, and `nilfs_sufile_read()`.

## Control Flow

Allocation reads the header's last allocation, chooses a start segment within the configured allocation range, wraps through the range and then outside it if needed, scans segment usage entries block by block, and marks the first clean entry dirty. It updates header clean/dirty counters, cached clean count, last allocation, buffer dirty state, and metadata dirty state.

Free/scrap/cancel/error operations are small primitives invoked under the generic update wrappers. Free makes an allocated segment clean and adjusts counters. Scrap makes a segment dirty garbage with zero blocks, used for recovery and GC protection. Cancel-free re-dirties a segment after provisional freeing. Set-error marks a segment erroneous and removes it from clean counts if needed.

Resize takes the metadata semaphore, checks reserved-space constraints, truncates trailing segments only if they are clean or error-only and inactive, converts full usage blocks to holes, updates counters and the global segment count, and clamps allocation range after shrink.

Suinfo get/set iterates segment usage entries for ioctl users. Get synthesizes the active flag from `nilfs_segment_is_active()` rather than reading it from disk. Set validates segment numbers, update flags, and block counts, updates selected fields, drops virtual active flags, and adjusts header counters.

Trim computes block/segment ranges from byte input, groups contiguous clean segments into discard extents, issues `blkdev_issue_discard()`, and reports discarded bytes through `range->len`.

## State and Persistence Behavior

Sufile entries and header counters are persistent metadata and are written through normal NILFS segment construction. The cached `ncleansegs` and allocation limits are volatile accelerators and policy state. Active segment status is not stored in entries; it is derived from current `the_nilfs` segment cursors.

Segment frees are often provisional until a log with a super root commits the sufile update. `segment.c` cancels frees if construction fails. Erroneous segments are intended to be permanently avoided by allocation.

## Dependencies and Integration Points

The file depends on `mdt.h`, segment usage on-disk helpers from NILFS headers, tracepoints, block discard APIs, and `the_nilfs` geometry helpers. It is used by segment construction, recovery, GC, statfs/free-block counting, resize, ioctl, and trim paths.

## Risks and Edge Cases

Counter correctness is critical: header clean/dirty counters and cached `ncleansegs` must stay synchronized across allocate/free/scrap/error/resize/set_suinfo. Hole blocks in the sufile are valid in some ranges but can indicate corruption for required entries. Resize must reject dirty or active segments in the truncated range. Trim holds a read lock while issuing discards, which can be slow. User-driven suinfo updates can create dangerous states if validation misses flag combinations.

## Test Signals

Tests should cover allocation wraparound with restricted ranges, ENOSPC, free/cancel-free failure rollback, recovery scrap, active erroneous segment detection, resize expansion/shrink with dirty/active/error segments, suinfo ioctl counter changes, holes in usage blocks, fstrim minlen/range clipping, discard failure handling, and crash recovery after provisional frees.
