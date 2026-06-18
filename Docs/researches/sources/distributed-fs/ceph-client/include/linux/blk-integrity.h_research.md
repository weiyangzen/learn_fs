# sources/distributed-fs/ceph-client/include/linux/blk-integrity.h

## Purpose
`blk-integrity.h` declares the block-layer data integrity/protection information API. It connects request queues, bios, DMA mapping, metadata buffers, and integrity profiles so devices can verify or generate per-sector metadata.

## Important APIs, Types, And Functions
`enum blk_integrity_flags` defines profile behavior such as no verify, no generate, device capable, reference tags, stacked integrity, and split-interval capability. Always-declared helpers include `blk_integrity_profile_name()`, `queue_limits_stack_integrity()`, and `queue_limits_stack_integrity_bdev()`.

With `CONFIG_BLK_DEV_INTEGRITY`, the header declares `blk_rq_map_integrity_sg()`, `blk_rq_count_integrity_sg()`, `blk_rq_integrity_map_user()`, `blk_get_meta_cap()`, `blk_rq_integrity_dma_map_iter_start()`, and `blk_rq_integrity_dma_map_iter_next()`. Inline helpers expose queue support, disk/bdev integrity profiles, maximum integrity segments, interval and byte calculations, request integrity flag checks, and `rq_integrity_vec()`. Without integrity support, stubs return neutral values or errors.

`enum bio_integrity_action` describes required actions: allocate buffer, check/generate protection information, and zero buffer. `bio_integrity_action()` skips work when the target has no integrity profile or the bio already has integrity metadata; otherwise it calls `__bio_integrity_action()`.

## Control Flow And State
The header gates most behavior on `CONFIG_BLK_DEV_INTEGRITY`. Runtime flow checks queue limits for `integrity.metadata_size`, inspects `REQ_INTEGRITY`, and converts sectors to integrity intervals using `interval_exp`. Request mapping functions operate over request/bio integrity payloads and DMA iterators; action selection is deferred to the implementation when metadata must be synthesized or verified.

State lives in `queue_limits.integrity`, bio integrity payloads, request flags, and DMA iterator state. The header itself does not persist anything.

## Dependencies And Integration Points
It includes `linux/blk-mq.h`, `linux/bio-integrity.h`, and `linux/blk-mq-dma.h`. It integrates with `struct queue_limits` from `blkdev.h`, `struct request` from `blk-mq.h`, `struct bio` from `blk_types.h`, and user ioctls for metadata capabilities.

## Risks And Test Signals
Risks include interval exponent assumptions, division/shift mismatches for non-512-byte intervals, missing stubs in non-integrity builds, DMA iterator errors, integrity segment limits, and failing to allocate or zero metadata buffers. Tests should cover config-enabled and disabled builds, profile stacking, request SG counts, user metadata mapping, `REQ_INTEGRITY` propagation, and action masks for bios with and without preexisting integrity payloads.
