# sources/distributed-fs/ceph-client/block/blk-merge.c

## Purpose
`blk-merge.c` enforces queue limits while splitting bios and merging bios or requests. It is the central policy for segment counts, DMA/virtual boundary gaps, discard limits, atomic-write restrictions, integrity and crypto merge compatibility, and scheduler-assisted merging.

## Important APIs, Types, And Functions
Key exported APIs include `bio_submit_split_bioset()`, `bio_split_io_at()`, `bio_split_to_limits()`, `blk_recalc_rq_segments()`, `ll_back_merge_fn()`, `bio_seg_gap()`, `blk_attempt_req_merge()`, `blk_rq_merge_ok()`, `blk_try_merge()`, `bio_attempt_back_merge()`, `blk_attempt_plug_merge()`, `blk_bio_list_merge()`, and `blk_mq_sched_try_merge()`. Internal helpers include `bio_will_gap()`, `get_max_io_size()`, `bvec_split_segs()`, `bio_split_discard()`, `bio_split_zone_append()`, `bio_split_write_zeroes()`, and request-to-request merge routines.

## Control Flow
Bio splitting scans bvecs against queue limits, alignment masks, crypto data-unit size, max segments, max bytes, virtual boundary gaps, zone write granularity, and atomic-write constraints. If splitting is necessary, atomic bios fail with `-EINVAL`, `REQ_NOWAIT` bios fail with `-EAGAIN`, and normal bios are split on a block-aligned boundary with polled I/O cleared. Merge control flow first checks operation, cgroup, integrity, crypto, write hint/stream, I/O priority, and atomic compatibility. Back/front/discard merge paths then enforce gap, sector, and segment limits, update request sector/data/segment accounting, propagate failfast mixed-merge state, call rq-qos merge hooks, and notify trace/elevator code.

## State And Persistence
No persistent state is owned here, but many request and bio fields are mutated: `bi_next`, `biotail`, `__data_len`, `__sector`, `nr_phys_segments`, `nr_integrity_segments`, `phys_gap_bit`, `rq_flags`, and `cmd_flags`. Split bios are chained to preserve completion ordering and resubmit the remainder.

## Dependencies And Integration Points
The file integrates with block queue limits, blk-cgroup merge rules, blk-integrity, blk-crypto, rq-qos, elevator callbacks, blk-throttle, zone write plugging, partition stats, and tracepoints. It is directly consumed by passthrough mapping, bio submission, plug merging, and mq scheduler merging.

## Risks And Test Signals
High-risk cases are off-by-one split boundaries, zero-byte split results, atomic writes being split or cross-boundary merged, NOWAIT semantics, discard segment accounting, mixed failfast propagation, front merges on zoned writes, crypto/integrity incompatibility, and stale physical gap bits. Tests should cover max segment/virt-boundary limits, physical/logical block alignment, write-zeroes limit changes, zone append no-split checks, request-to-request merge accounting, plug-list merge scan limits, and trace/stat increments.
