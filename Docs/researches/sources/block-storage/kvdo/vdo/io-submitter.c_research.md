# File Research: sources/block-storage/kvdo/vdo/io-submitter.c

VDO bio submission coordinator with per-bio-thread queues, block-layer plugging, and adjacent data-bio merge tracking.

Key responsibilities:
- Defines `bio_queue_data` with work queue, `blk_plug`, `int_map` merge map, mutex, and queue number.
- Defines `io_submitter` containing bio queue data for configured bio threads.
- Starts/finishes block plugs when bio work queues run.
- Counts submitted bios into data/meta/journal/page-cache stats.
- Submits bios to the backing device with `submit_bio_noacct()`.
- Merges adjacent data VIO bios by sector when priority and direction match.
- Submits data VIO I/O through bio-zone callbacks, or leaves merged VIOs pending until the head/tail owner submits.
- Submits metadata VIO I/O by resetting the bio and scheduling `process_vio_io()` on the appropriate bio-zone thread.
- Creates, cleans up, and frees the I/O submitter and per-thread merge maps.

Important behavior:
- Merge maps store only head and tail sectors for each merged bio list.
- Back merges append to previous tail; front merges prepend to next head.
- If a VIO merges into another pending list, it is not immediately launched.
- `process_data_vio_io()` extracts the merged bio list under lock, removes head/tail map entries, then submits each bio.
- Flush operations are submitted as metadata with `REQ_OP_WRITE | REQ_PREFLUSH`.
- Creation sizes each queue's `int_map` as `max_requests_active * 2`, allowing both first and last sector entries.

Dependencies:
- Linux bio/block APIs, VDO work queues, completions, VIO/data_vio types, atomic stats, `int-map`, assertions, memory allocation, logger, and thread config.

Notable risks:
- `merge_to_prev_tail()` and `merge_to_next_head()` assign `result` twice and only return the second insertion result, so a first insertion failure can be overwritten.
- Comments state `int_map_put()` failure is ignored except for assertions.
- Merge correctness depends on serialized access through each queue's mutex and stable bio-zone assignment.
- Cleanup and free are split to avoid races; callers must call them in the intended order.
