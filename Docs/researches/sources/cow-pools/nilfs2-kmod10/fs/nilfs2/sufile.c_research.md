# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sufile.c

## Summary
Implements the NILFS segment usage metadata file. It tracks clean, dirty, active, and erroneous segment state, allocates clean segments, frees or cancels freed segments, reports segment statistics, resizes the segment array, supports user-driven suinfo updates, and implements discard/trim over clean segments.

## Main Responsibilities
- Maintains in-memory sufile private state: clean segment count and allocation range.
- Converts segment numbers to sufile metadata block offsets and entry offsets.
- Updates sufile entries singly or in vectors under `mi_sem`.
- Allocates clean segments using last-allocation and allocation-range scanning.
- Marks segments dirty, clean/free, garbage/scrap, or erroneous.
- Reports `nilfs_sustat` and per-segment `nilfs_suinfo`.
- Applies ioctl-provided `nilfs_suinfo_update` arrays.
- Resizes the segment usage array during filesystem resize.
- Issues discard for clean segment extents for fstrim.
- Reads and initializes the sufile inode from the super-root raw inode.

## Key APIs
- `nilfs_sufile_get_ncleansegs()`.
- `nilfs_sufile_updatev()`, `nilfs_sufile_update()`.
- `nilfs_sufile_set_alloc_range()`.
- `nilfs_sufile_alloc()`.
- `nilfs_sufile_mark_dirty()`.
- `nilfs_sufile_set_segment_usage()`.
- `nilfs_sufile_get_stat()`.
- `nilfs_sufile_get_suinfo()`, `nilfs_sufile_set_suinfo()`.
- `nilfs_sufile_resize()`.
- `nilfs_sufile_trim_fs()`.
- `nilfs_sufile_read()`.

## Important Behavior
`nilfs_sufile_alloc()` scans from the last allocated segment, first inside the configured allocation range and then outside it as needed. It only chooses entries whose segment usage is clean, marks them dirty, updates header clean/dirty counters, updates `sui->ncleansegs`, marks metadata dirty, and emits allocation tracepoints.

`nilfs_sufile_freev()` and cancel-free wrappers are built on `nilfs_sufile_updatev()`, which groups operations by metadata block and returns the number of completed entries for rollback.

`nilfs_sufile_mark_dirty()` rejects unreadable hole blocks and active segments marked erroneous. `nilfs_sufile_set_segment_usage()` updates live block count and optionally last-modified time; timestamped updates warn if the entry is in error.

Resize shrinking verifies the truncated range has no dirty or active segments, converts error-only entries back to clean, deletes whole sufile blocks when possible, updates clean counters, and narrows the allocation range before returning.

`nilfs_sufile_set_suinfo()` validates segment numbers, update field masks, and block counts, masks out the virtual active flag before writing, and adjusts header clean/dirty counts according to flag transitions.

## State and Synchronization
All sufile metadata changes are serialized with `NILFS_MDT(sufile)->mi_sem`. Header counters on disk and the cached `ncleansegs` counter must move together. The file uses local folio mappings for entry access and marks both sufile blocks and metadata dirty after changes.

## Risks
Counter consistency is critical: clean and dirty counters are updated in several primitive operations and must match flag transitions. Hole blocks are tolerated in read paths but treated as corruption in some update paths. The active flag is virtual, derived from `the_nilfs`, and must not be persisted by suinfo updates.
