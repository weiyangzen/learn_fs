# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segbuf.h

## Purpose

Declares NILFS segment-buffer and segment-summary in-memory structures plus APIs/macros for log construction and writing.

## Main Structures

- `struct nilfs_segsum_info`
  - In-memory segment summary fields: flags, file-info count, block counts, summary byte count, file block count, segment sequence, checkpoint number, creation time, and next segment block.
- `struct nilfs_segment_buffer`
  - Represents one partial segment/log, including superblock pointer, list node, summary info, current/full segment range, summary buffer list, payload buffer list, optional super-root buffer, outstanding BIO count, error counter, and completion.

## Main APIs

- Lifecycle:
  - `nilfs_segbuf_new()`
  - `nilfs_segbuf_free()`
- Mapping:
  - `nilfs_segbuf_map()`
  - `nilfs_segbuf_map_cont()`
  - `nilfs_segbuf_set_next_segnum()`
- Construction:
  - `nilfs_segbuf_reset()`
  - `nilfs_segbuf_extend_segsum()`
  - `nilfs_segbuf_extend_payload()`
  - `nilfs_segbuf_fill_in_segsum()`
- Log lists and I/O:
  - `nilfs_clear_logs()`
  - `nilfs_truncate_logs()`
  - `nilfs_destroy_logs()`
  - `nilfs_write_logs()`
  - `nilfs_wait_on_logs()`
  - `nilfs_add_checksums_on_logs()`

## Important Inline Helpers and Macros

- Segment-buffer list navigation macros:
  - `NILFS_LIST_SEGBUF`
  - `NILFS_NEXT_SEGBUF`
  - `NILFS_PREV_SEGBUF`
  - `NILFS_LAST_SEGBUF`
  - `NILFS_FIRST_SEGBUF`
  - `NILFS_SEGBUF_IS_LAST`
- Buffer-list navigation macros for `b_assoc_buffers`.
- `nilfs_segbuf_simplex()` checks whether a buffer is both log-begin and log-end.
- `nilfs_segbuf_empty()` checks whether only summary blocks are present.
- `nilfs_segbuf_add_segsum_buffer()` increments total and summary block counts.
- `nilfs_segbuf_add_payload_buffer()` increments total block count.
- `nilfs_segbuf_add_file_buffer()` grabs an extra buffer reference, adds it as payload, and increments file block count.

## Dependencies and Interactions

- Used by segment-construction code to assemble logs and by `recovery.c` to reason about NILFS segment layout.
- The lists use `buffer_head::b_assoc_buffers`, so callers must avoid conflicting use of that list node.
