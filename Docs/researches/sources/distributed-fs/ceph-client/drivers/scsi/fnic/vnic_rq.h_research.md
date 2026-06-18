# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_rq.h

## Purpose

`vnic_rq.h` defines vNIC receive queue control registers, software buffer metadata, queue state, and inline helpers for posting and servicing receive descriptors.

## Important APIs, types, and data

- `struct vnic_rq_ctrl` maps RQ MMIO registers including ring, posted/fetch, CQ index, enable/running, error, and dropped counts.
- `struct vnic_rq_buf` tracks each posted OS buffer, DMA address, length, descriptor pointer, and circular next pointer.
- `struct vnic_rq` owns queue identity, MMIO pointer, DMA ring, buffer blocks, software producer/consumer pointers, and counters.
- Inline helpers expose descriptor availability, next descriptor/index, buffer-index allocation, descriptor posting, batched posted-index updates, descriptor return, completion service, and ring fill.

## Control flow

Receive fill loops call `vnic_rq_fill()`, which repeatedly invokes a caller buffer-fill callback while more than one descriptor is available. Posting records the OS buffer/DMA metadata, advances `to_use`, decrements availability, and periodically writes the posted index after a memory barrier. Completion service walks from `to_clean` to a completed index, calls a callback for each skipped/final buffer, and optionally returns descriptors immediately.

## State and persistence behavior

`ring.desc_avail`, `to_use`, `to_clean`, and `buf_index` are persistent software ownership state. Hardware ownership is communicated through the posted and fetch indexes.

## Dependencies and integration points

It depends on PCI types, `vnic_dev.h`, and `vnic_cq.h`. FNIC receive paths pair it with `rq_enet_desc.h` descriptors and CQ completion handlers.

## Risks and edge cases

- `vnic_rq_next_buf_index()` monotonically increments without wrap in the helper; callers must treat it as an OS-side identifier, not a ring index.
- Posting updates hardware only every `VNIC_RQ_RETURN_RATE + 1` descriptors.
- `vnic_rq_service()` can call the callback for skipped descriptors before the completed descriptor, so callbacks must handle skipped=true cleanup semantics.

## Test signals

Unit tests should cover descriptor availability math, batched posting boundaries, skipped completion handling, deferred descriptor return, and fill-loop error propagation.
