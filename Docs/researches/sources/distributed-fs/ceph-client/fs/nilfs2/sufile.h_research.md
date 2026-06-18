# sources/distributed-fs/ceph-client/fs/nilfs2/sufile.h

## Purpose

`sufile.h` declares the segment usage file interface for NILFS2. It exposes allocation, freeing, error marking, statistics, suinfo ioctl access, resizing, trim, and read initialization helpers used by the segment constructor, recovery, GC, ioctl, and mount code.

## Important APIs, Types, and Functions

`nilfs_sufile_get_nsegments()` derives the segment count from `the_nilfs`. `nilfs_sufile_get_ncleansegs()` returns the cached clean count.

Allocation and state APIs include `nilfs_sufile_set_alloc_range()`, `nilfs_sufile_alloc()`, `nilfs_sufile_mark_dirty()`, `nilfs_sufile_set_segment_usage()`, `nilfs_sufile_updatev()`, `nilfs_sufile_update()`, and primitive callbacks `nilfs_sufile_do_scrap()`, `do_free()`, `do_cancel_free()`, and `do_set_error()`.

Inline wrappers provide semantic operations: `nilfs_sufile_scrap()`, `nilfs_sufile_free()`, `nilfs_sufile_freev()`, `nilfs_sufile_cancel_freev()`, and `nilfs_sufile_set_error()`. Other exports provide resize, read, stat, suinfo get/set, and trim.

## Control Flow

Callers generally use the semantic inline wrappers rather than calling update primitives directly. Segment construction allocates and marks active segments dirty, updates live block counts, and frees old segments through `freev()`. Recovery scraps or frees invalidated segments and allocates replacement segments. IOCTL paths call suinfo get/set and trim.

## State and Persistence Behavior

The header exposes persistent segment usage changes without embedding policy. The implementation writes changes to the sufile metadata blocks and marks the metadata inode dirty; those changes become durable with log construction. Active status remains a runtime projection.

## Dependencies and Integration Points

`sufile.h` depends on VFS, buffer heads, and `mdt.h`. It is included by `segment.c`, `recovery.c`, `super.c`, and likely ioctl/statfs helpers that inspect segment state.

## Risks and Edge Cases

The update primitives assume the caller supplied valid header and entry buffers under the sufile semaphore. External callers should prefer wrappers to avoid bypassing locking and counter updates. `nilfs_sufile_set_error()` permanently removes a segment from normal allocation, so accidental calls are persistent and high impact.

## Test Signals

Test signals include wrapper behavior for single and vector frees, cancel-free counts, error marking, invalid segment numbers, resize and trim public calls, and read initialization with malformed segment usage entry sizes.
