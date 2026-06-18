# sources/distributed-fs/ceph-client/fs/nilfs2/segbuf.c

## Purpose

`segbuf.c` implements the physical segment-buffer abstraction used by the NILFS2 segment constructor. A segment buffer represents one partial segment: its summary blocks, payload blocks, optional super-root block, disk mapping, CRCs, and asynchronous BIO write state.

## Important APIs, Types, and Functions

`nilfs_segbuf_new()` and `nilfs_segbuf_free()` allocate from `nilfs_segbuf_cachep`. Mapping helpers are `nilfs_segbuf_map()`, `nilfs_segbuf_map_cont()`, and `nilfs_segbuf_set_next_segnum()`. Capacity helpers extend summary or payload storage with `nilfs_segbuf_extend_segsum()` and `nilfs_segbuf_extend_payload()`.

`nilfs_segbuf_reset()` initializes a partial segment summary, while `nilfs_segbuf_fill_in_segsum()` writes the on-disk segment summary header. CRC helpers fill summary, data, and super-root checksums. Log-list helpers are `nilfs_clear_logs()`, `nilfs_truncate_logs()`, `nilfs_write_logs()`, `nilfs_wait_on_logs()`, and `nilfs_add_checksums_on_logs()`.

BIO submission is handled by `nilfs_segbuf_write()`, `nilfs_segbuf_submit_bh()`, `nilfs_segbuf_submit_bio()`, `nilfs_end_bio_write()`, and `nilfs_segbuf_wait()`.

## Control Flow

The constructor maps a new segment buffer to a full segment and offset, extends at least one summary block, appends summary and payload buffers as dirty blocks are collected, then fills summary fields and checksums. `nilfs_write_logs()` iterates segment buffers and submits writes.

BIO submission walks summary buffers first, then payload buffers. Buffers are coalesced into bios up to `BIO_MAX_VECS` or until `bio_add_folio()` fails, at which point the current bio is submitted and a new one is allocated. The last bio is tagged `REQ_SYNC`. Completion increments `sb_err` on bio failure and signals `sb_bio_event`; `nilfs_segbuf_wait()` waits for all outstanding bios and reports `-EIO` with the segment range if any failed.

CRC order matters: super-root CRC is embedded first if present, then segment-summary CRC, then full data CRC across summaries and payload buffers. Payload CRC maps folios with `kmap_local_folio()` and assumes block size is not larger than page size.

## State and Persistence Behavior

Segment buffers are volatile staging objects, but their contents are the exact bytes written to the log. `sb_sum` mirrors on-disk segment summary state; `sb_segnum`, `sb_nextnum`, `sb_pseg_start`, and `sb_rest_blocks` define disk placement. `sb_nbio`, `sb_err`, and `sb_bio_event` track asynchronous persistence completion.

After writes complete, `segment.c` finalizes buffer and folio state and advances filesystem cursors. On abort, log buffers are cleared or marked failed by the segment constructor, not by `segbuf.c` itself.

## Dependencies and Integration Points

The file depends on buffer-heads, writeback, CRC32, BIO APIs, block devices, and `page.h`/`segbuf.h`. It is driven almost entirely by `segment.c`; recovery reads the on-disk format that this file writes.

## Risks and Edge Cases

`bio_alloc()` return is not explicitly NULL-checked in `nilfs_segbuf_submit_bh()`, so allocation failure behavior depends on the kernel API contract. CRC calculations assume summary size and block list consistency already enforced by the constructor. `nilfs_segbuf_wait()` uses a single completion repeatedly; completions must match `sb_nbio` exactly. Block sizes larger than page size are explicitly unsupported for payload CRC mapping.

## Test Signals

Test coverage should include multi-bio partial segments, summary-block extension, super-root CRC validation by recovery, injected BIO errors, bio vector boundary behavior, blocksize less than page size, continued partial segments, and abort paths after partial submission.
