# sources/distributed-fs/ceph-client/fs/nilfs2/segbuf.h

## Purpose

`segbuf.h` declares NILFS2 segment-buffer structures and helpers. It is the public interface between the segment constructor and the lower-level log buffer/BIO writer implemented in `segbuf.c`.

## Important APIs, Types, and Functions

`struct nilfs_segsum_info` is the in-memory summary for a partial segment: flags, finfo count, total block count, summary block count, summary byte count, file block count, segment sequence, checkpoint number, creation time, and next-segment block.

`struct nilfs_segment_buffer` stores list linkage, summary info, segment mapping (`sb_segnum`, `sb_nextnum`, full segment start/end, partial segment start, remaining blocks), summary and payload buffer lists, optional super-root buffer, and async IO state (`sb_nbio`, `sb_err`, completion).

List and iterator macros walk segment buffers and buffers inside segment-buffer lists. Inline helpers classify a simplex log, detect empty logs, and add summary, payload, or file buffers while updating block counters. File-buffer insertion takes a reference and increments `nfileblk`.

Exports cover allocation/freeing, mapping, reset, summary/payload extension, summary filling, log clearing/truncation/destruction, writing, waiting, and checksum insertion.

## Control Flow

`segment.c` allocates and maps segment buffers, appends dirty buffers through the inline add helpers, fills summary entries, sets next segment numbers, and finally calls `nilfs_add_checksums_on_logs()`, `nilfs_write_logs()`, and `nilfs_wait_on_logs()`.

The header's macros encode assumptions used throughout the constructor: segment buffers are list-linked by `sb_list`, buffer heads are list-linked by `b_assoc_buffers`, and the last segment buffer may carry the super-root block.

## State and Persistence Behavior

The structures are in-memory staging state for persistent NILFS logs. Fields in `sb_sum` are copied to on-disk `struct nilfs_segment_summary`. Payload and summary buffer lists are the ordered write set for a partial segment. IO state records whether persistence succeeded, but the constructor is responsible for updating global filesystem cursors and sufile accounting after success.

## Dependencies and Integration Points

The header depends on filesystem, buffer-head, BIO, and completion APIs. It declares `nilfs_segbuf_cachep`, which is created in `super.c`. It integrates tightly with `segment.c` and with recovery's expectations for segment-summary layout and checksums.

## Risks and Edge Cases

The iterator macros assume non-empty lists when used; misuse on empty logs can dereference list heads as objects. `nilfs_segbuf_simplex()` depends on correct `NILFS_SS_LOGBGN` and `NILFS_SS_LOGEND` flag management. Counters must remain synchronized with list contents or CRC and write lengths will mismatch recovery validation.

## Test Signals

Tests should validate empty/simplex/multi-partial logs, list truncation after failed construction, file buffer reference accounting, summary and payload block counts, and super-root placement in the last segment buffer.
