# File Research: sources/block-storage/kvdo/vdo/packer.c

## Purpose
Implements the compressed block packer, which batches multiple compressed `data_vio` fragments into a single compressed block write.

## Core Model
- Maintains multiple `packer_bin` instances sorted by ascending `free_space`.
- Each bin holds pending compressed VIO fragments.
- First-best-fit bin selection is used.
- A special canceled bin holds canceled VIOs waiting for rendezvous with canceling VIOs.

## Key Flow
- `vdo_attempt_packing`: validates packer-thread context, increments in-packer stats, checks admin state/flush generation, selects a bin, transitions VIO to packing, and enqueues it.
- `add_data_vio_to_packer_bin`: inserts VIO, updates free space, writes bin if full, restores sort order.
- `write_bin`: picks an agent VIO, packs client fragments into the agent’s compressed block, aborts if only one fragment, prepares and submits compressed write otherwise.
- `finish_compressed_write`: releases clients first, shares the compressed write PBN lock, then releases the agent.
- `handle_compressed_write_error`: moves to allocated-zone thread if needed, updates error stats, releases clients/agent back to the normal write path.

## Administrative Operations
- `vdo_flush_packer`: writes all non-empty bins.
- `vdo_increment_packer_flush_generation`: increments generation and flushes older VIOs.
- `vdo_drain_packer`: starts drain and prevents new packer entries.
- `vdo_resume_packer`: resumes after suspension.
- `vdo_dump_packer`: logs state and non-empty bins.

## Statistics
`vdo_get_packer_statistics` returns READ_ONCE copies of fragment/block counters. Writes use `WRITE_ONCE`.

## Integration Notes
Integrates with compression state, allocation, compressed block layout, VIO I/O submit, read-only notifier, admin state, and PBN locks.

## Risks / Invariants
Correctness depends on packer-thread serialization and the cancellation rendezvous rules documented around VDO-2809/VDO-2826. A VIO in `VIO_PACKING` must be placed in a bin before another packer-thread request can observe it.
