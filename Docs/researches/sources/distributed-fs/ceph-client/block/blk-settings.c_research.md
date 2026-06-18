# sources/distributed-fs/ceph-client/block/blk-settings.c

## Purpose

`blk-settings.c` validates, defaults, commits, and stacks block queue limits. It defines the rules that turn driver-provided limits into coherent `queue_limits`, applies them to request queues and backing-dev readahead, handles atomic write constraints, zoned-device constraints, integrity metadata constraints, discard/write-zeroes caps, and reports alignment for block devices and partitions.

## Important APIs, Types, And Functions

Public APIs include `blk_queue_rq_timeout()`, `blk_set_stacking_limits()`, `blk_validate_limits()`, `blk_set_default_limits()`, `queue_limits_commit_update()`, `queue_limits_commit_update_frozen()`, `queue_limits_set()`, `blk_stack_limits()`, `queue_limits_stack_bdev()`, `queue_limits_stack_integrity()`, `blk_set_queue_depth()`, `bdev_alignment_offset()`, and `bdev_discard_alignment()`. Internal validators cover zoned limits, integrity limits, atomic write boundaries, atomic write update calculations, discard alignment, logical/physical block alignment, and stacked-device atomic-write compatibility.

## Control Flow

Drivers initialize or update a `queue_limits` structure, then call `queue_limits_set()` or the start/commit update API. `blk_validate_limits()` fills defaults, rejects impossible configurations, rounds sizes to logical block sectors, derives `max_sectors` from hardware, device, user, and optimal I/O caps, validates segment and DMA constraints, normalizes discard values, clears unsupported FUA without write cache, derives atomic-write limits, validates integrity metadata, and finally validates zoned settings. `queue_limits_commit_update()` requires `q->limits_lock`, validates the candidate, rejects unsupported integrity plus inline encryption, copies it into `q->limits`, updates BDI readahead, and unlocks. The frozen variant wraps the commit in blk-mq freeze/unfreeze.

Stacking drivers call `blk_set_stacking_limits()` to set permissive initial values, then repeatedly call `blk_stack_limits()` or `queue_limits_stack_bdev()` for component devices. Stacking intersects inherited features and sizes, reconciles alignment offsets with LCM/GCD calculations, propagates misalignment flags, combines discard and zone limits, and narrows atomic-write support to configurations aligned across all components.

## State And Persistence Behavior

The file mutates in-memory `queue_limits`, `request_queue::rq_timeout`, `request_queue::queue_depth`, and BDI `ra_pages/io_pages`. Queue-limit updates are serialized by `limits_lock`; frozen commits additionally block I/O while limits change. No persistent storage is written.

## Dependencies And Integration Points

It depends on block core types, backing-dev info, DMA/page constants, integrity/T10 PI/CRC64 metadata, zoned block support, atomic write helpers, and rq-qos queue-depth notification. Sysfs store callbacks in `blk-sysfs.c` use the update/commit APIs. Stacking drivers such as device mapper and MD depend on the stacking functions to produce safe upper-device limits.

## Risks And Edge Cases

Invalid limits can cause data corruption or bio splitting failures, so validation is defensive. Risks include integer shifts between sectors and bytes, non-power-of-two block sizes, atomic-write boundaries incompatible with chunk sizes, integrity interval mismatches, zoned limits without zoned support, discard granularity zeroing when discard is unsupported, and alignment offsets for partitions. Frozen commits are necessary when live I/O could observe changed limits mid-submission. BDI readahead is only increased, not decreased, to preserve user tuning.

## Test Signals

Useful tests include sysfs writes to max sectors/discard/write-cache/iostats, driver initialization with incomplete limits, stacked DM/MD devices with mismatched block sizes and discard granularity, integrity metadata profiles, zoned devices with zone append caps, atomic write positive/negative configurations, inline encryption plus integrity rejection, and lockdep around `limits_lock` and queue freeze.
