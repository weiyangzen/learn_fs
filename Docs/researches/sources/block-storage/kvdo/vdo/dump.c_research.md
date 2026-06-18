# File Research: sources/block-storage/kvdo/vdo/dump.c

## Purpose
Provides diagnostic dump support for VDO state, queues, VIO pools, hash zones, memory usage, and individual data VIOs.

## Main Behavior
- `vdo_dump()` parses dump options and triggers selected diagnostics.
- `vdo_dump_all()` dumps all known categories.
- Options include queues/threads, VIO pool/pools, VDO status, default, and all.
- `do_dump()` logs active device requests, outstanding bios, work queues, hash zones, data VIO pool, VDO status, and UDS memory usage.
- `dump_data_vio()` logs compact per-VIO state including physical/logical/duplicate block numbers, operation, completion state, flush generation, and flags.
- `dump_vio_waiters()` logs waiters on a VIO wait queue.

## Dependencies
Uses VDO data VIO, dedupe/hash-zone dumping, IO submitter work queues, memory reporting, and logger.

## Notes
The per-VIO dump uses static buffers and assumes only one dump runs at a time; concurrent dumps would garble log lines.
