# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segment.h

## Summary
Defines segment-constructor state, recovery cursor state, collection stage state, segment summary pointer helpers, constants, and public segment/recovery interfaces.

## Main Contents
- `struct nilfs_recovery_info` for mount-time super-root search and roll-forward state.
- `struct nilfs_cstage` for dirty block collection stage tracking.
- `struct nilfs_segsum_pointer` for current segment-summary buffer/offset.
- `struct nilfs_sc_info` for segctord and active segment construction state.
- Segment-constructor flags and defaults.
- Prototypes for construction, dsync, cleaner, writer attach/detach, and recovery helpers.

## Important Details
`nilfs_sc_info` ties together dirty file lists, GC inode lists, pending iput work, sufile free vectors, dsync target range, current segment buffers, write logs, stage cursors, summary pointers, checkpoint/time counters, request queues, sequence counters, timer, and segctord task pointer.

`NILFS_SC_DIRTY`, `NILFS_SC_UNCLOSED`, `NILFS_SC_SUPER_ROOT`, `NILFS_SC_PRIOR_FLUSH`, and `NILFS_SC_HAVE_DELTA` describe segment-constructor state across checkpoint and lightweight flush operations.

Default behavior is set by `NILFS_SC_DEFAULT_TIMEOUT`, `NILFS_SC_DEFAULT_SR_FREQ`, and `NILFS_SC_DEFAULT_WATERMARK`.

## Risks
Consumers must respect the locking comments: `nilfs_segctor_destroy()` expects the segment semaphore to be held, and `sc_stage.scnt` should be accessed through the wrappers in `segment.c` so tracing remains consistent.
