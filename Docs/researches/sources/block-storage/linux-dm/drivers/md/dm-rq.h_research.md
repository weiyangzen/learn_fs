# File Research: sources/block-storage/linux-dm/drivers/md/dm-rq.h

## Purpose

`dm-rq.h` is the internal header for request-based Device Mapper support.

## API And Data

It forward-declares `struct mapped_device` and defines `struct dm_rq_clone_bio_info`, the front-padded metadata used when cloning bios for request-based DM. The struct stores the original bio, associated `dm_rq_target_io`, and embedded clone bio. The embedded bio must remain last because allocation uses `bio_alloc_bioset()` front padding.

The header declares blk-mq request-queue setup/cleanup, queue start/stop helpers, requeue kicking, reserved request-based I/O count lookup, and compatibility sysfs attribute show/store functions for the deprecated sequential I/O merge deadline.

## Invariants And Risks

- `struct dm_rq_clone_bio_info` layout is ABI-like within the module: `clone` must stay last.
- Callers rely on queue helpers mapping directly to blk-mq quiesce/unquiesce and requeue behavior.
- The deprecated sysfs attributes are preserved for userspace compatibility even though they no longer tune a real heuristic.

## Test Focus

Test that request-based queue init users include this header consistently, clone-bio front padding resolves back to metadata correctly, queue start/stop invoke blk-mq behavior, requeue kick is exported, and compatibility attributes remain readable/writable.
