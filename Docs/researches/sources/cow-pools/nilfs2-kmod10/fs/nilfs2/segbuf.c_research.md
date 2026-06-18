# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segbuf.c

## Purpose

Implements NILFS segment-buffer construction, checksum filling, log buffer lifetime, BIO submission, and write completion waiting.

## Main Responsibilities

- Allocates, initializes, clears, truncates, and frees `struct nilfs_segment_buffer` objects.
- Maps segment buffers to full/partial segment disk block ranges.
- Extends segment summary and payload buffer lists.
- Fills on-disk segment summary fields from in-memory summary state.
- Computes and stores checksums for super root, segment summary, and full data payload.
- Writes segment-summary and payload buffers as BIOs to the block device.
- Waits for all BIO completions and reports log write I/O failures.

## Important Functions

- `nilfs_segbuf_new()` allocates from `nilfs_segbuf_cachep`, initializes lists, completion, error counter, and BIO count.
- `nilfs_segbuf_map()` maps a segment buffer to a segment number and offset.
- `nilfs_segbuf_map_cont()` maps a new buffer immediately after a previous partial segment.
- `nilfs_segbuf_set_next_segnum()` stores the next segment number and next segment start block.
- `nilfs_segbuf_extend_segsum()` gets and initializes an on-disk block for another summary block.
- `nilfs_segbuf_extend_payload()` gets a payload block at the current partial segment end.
- `nilfs_segbuf_reset()` starts a fresh summary with flags, ctime, and checkpoint number.
- `nilfs_segbuf_fill_in_segsum()` writes the raw segment summary header fields.
- `nilfs_add_checksums_on_logs()` fills super-root, summary, and payload CRCs for all logs.
- `nilfs_write_logs()` submits each segment buffer for write.
- `nilfs_wait_on_logs()` waits for all submitted segment buffers.
- `nilfs_segbuf_submit_bh()` builds BIOs with `bio_add_folio()` and submits full BIOs.
- `nilfs_segbuf_wait()` waits on completion events and returns `-EIO` if any BIO completed with error.

## Dependencies and Interactions

- Uses `page.h` for buffer/folio mapping details during payload checksum and BIO construction.
- Uses `the_nilfs` segment geometry helpers to compute segment ranges and next segment block numbers.
- Segment construction code fills segment buffers with summary/payload buffers, then calls these helpers to checksum and write them.
- Recovery validates the checksums written here.

## Notable Behaviors and Edge Cases

- Last BIO in a log is forced `REQ_SYNC`.
- BIO vector count is capped by `BIO_MAX_VECS` and remaining blocks.
- Write completion increments `sb_err` on any BIO status error, then completes `sb_bio_event`.
- `nilfs_segbuf_wait()` waits once per submitted BIO by decrementing `sb_nbio`.
- Payload CRC maps each payload buffer’s folio locally and includes the exact buffer size.
- Segment summary CRC excludes the checksum fields themselves.
