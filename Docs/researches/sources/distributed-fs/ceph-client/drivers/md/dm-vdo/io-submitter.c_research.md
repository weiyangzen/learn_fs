# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/io-submitter.c

## Purpose
`io-submitter.c` owns VDO bio-submission work queues. It keeps potentially blocking `submit_bio*()` calls off other VDO threads, starts block plugs on bio threads, routes data and metadata I/O to the backing device, counts statistics, and opportunistically merges adjacent data bios before submission.

## Important APIs, Types, and Functions
`struct io_submitter` stores bio-queue count, rotation interval, and per-queue data. `struct bio_queue_data` holds a work queue, `blk_plug`, merge `int_map`, mutex, and queue number. Public functions are `vdo_make_io_submitter()`, `vdo_cleanup_io_submitter()`, `vdo_free_io_submitter()`, `vdo_submit_vio()`, `vdo_submit_data_vio()`, `__submit_metadata_vio()`, and `vdo_submit_metadata_vio_wait()`. Important internals include `send_bio_to_device()`, `submit_data_vio()`, `try_bio_map_merge()`, and merge-map helpers.

## Control Flow
Initialization allocates one bio queue per configured bio thread, creates an `int_map` sized for active requests, and creates VDO work queues whose start/finish hooks start and finish `blk_plug`. Data VIO submission first initializes a single-bio list, checks the merge map for adjacent same-priority same-direction bios, and either merges into a pending VIO or schedules submission on the bio zone. Submission removes the head/tail sector mappings and submits the merged bio list. Metadata submission resets the VIO bio, marks it `REQ_META`, assigns a bio-zone callback, and launches by metadata priority. The synchronous metadata path calls `submit_bio_wait()` before full queue infrastructure is available.

## State and Persistence Behavior
State is runtime-only. Merge maps are protected by per-queue mutexes and map the current head and tail sectors of each pending merged bio list. Stats are updated in `send_bio_to_device()`. Cleanup finishes queues before `vdo_free_io_submitter()` releases queue references and maps.

## Dependencies and Integration Points
This file depends on Linux `bio`, `blk_plug`, mutexes, VDO work queues, VIO/data_vio helpers, the backing device accessor, `int-map`, logging, memory allocation, and VDO admin state. It is called by data write paths, metadata read/write paths, packer compressed writes, and journal/block-map code.

## Risks and Edge Cases
Merge tracking assumes serialized access through the per-queue mutex and only tracks head/tail sectors. Map insertion failure is logged as an assertion-only condition, so memory pressure can reduce merge correctness diagnostics. Metadata error-handler thread assumptions are documented as fragile if future callers change callback threading. Submitting while quiescent is assertion-logged but not hard-blocked beyond existing state handling. Cleanup order matters to avoid work-queue races.

## Test Signals
Validate data reads/writes and metadata I/O under multiple bio thread counts, merge of adjacent bios in both directions, no merge across priority or direction, flush VIO submission, sync metadata I/O before work queues, stats counters, queue cleanup, and backing-device error completion.
