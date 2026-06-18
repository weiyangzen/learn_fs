# sources/distributed-fs/ceph-client/fs/nilfs2/segment.h

## Purpose

`segment.h` declares NILFS2's log-writer, recovery, and segment-construction state interfaces. It is the shared contract between transaction users, the segment constructor implementation, recovery, superblock management, and garbage collection.

## Important APIs, Types, and Functions

`struct nilfs_recovery_info` records recovery results: whether recovery is needed, last super-root block/checkpoint, roll-forward scan range and starting sequence, used segments, last partial segment position, sequence, segment number, and next segment. Flags distinguish super-root update from completed roll-forward.

`struct nilfs_cstage` stores collection stage count, stage flags, and cursors into dirty-file and GC-inode lists. `struct nilfs_segsum_pointer` points into a segment summary buffer while finfo/binfo entries are written.

`struct nilfs_sc_info` is the complete log-writer object: superblock/root, block counters, dirty/GC/iput lists, segments to free, dsync range, active segment buffers, write-log buffers, current segment, stage, summary pointers and counters, checkpoint/timestamp/flag state, request queues and sequence counters, flush request bitmap, timing parameters, timer, and segctord task.

Public prototypes expose transaction construction, dsync construction, GC cleaning, log writer attach/detach, recovery scanning, super-root reading, orphan-log salvage, and segment-list disposal.

## Control Flow

The header describes the state consumed by `segment.c`: file operations enter transactions; segctord tracks requests and stages in `nilfs_sc_info`; recovery fills `nilfs_recovery_info`; superblock mount code attaches or detaches the log writer. Stages progress from init through GC, files, metadata files, DAT, super root, dsync, and done.

## State and Persistence Behavior

`nilfs_sc_info` is volatile, but it stages persistent changes to checkpoints, segment usage, DAT, and super roots. `sc_freesegs` and `sc_nfreesegs` represent segments that will become free only after a super-root log containing sufile changes is successfully written. `sc_cno`, `sc_seg_ctime`, and `sc_flags` connect in-memory construction to durable checkpoint identity.

`nilfs_recovery_info` bridges persistent on-disk log scanning and in-memory repair. It determines which segments must be scrapped or reallocated and whether a recovery segment must be constructed.

## Dependencies and Integration Points

The header depends on Linux fs, buffer heads, workqueues, and `nilfs.h`. It is included by `segment.c`, `super.c`, `recovery.c`, and callers that request log construction or cleaning.

## Risks and Edge Cases

Request sequence counters are 32-bit and use wrap-aware comparison in the implementation; changing their type or semantics can break waiters. `sc_stage` cursors must only be manipulated through wrappers in `segment.c` so tracepoints stay accurate. Public construction functions are not safe inside active transactions unless explicitly designed for that mode.

## Test Signals

Tests should verify recovery info population on clean/dirty mounts, wait-request wakeups under sequence wrap-like conditions, dsync range state, GC freed segment arrays, log-writer attach/detach lifecycle, and stage transitions observed through tracepoints.
