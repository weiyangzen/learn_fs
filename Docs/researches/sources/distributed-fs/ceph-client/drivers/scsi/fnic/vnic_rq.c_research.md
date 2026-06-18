# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_rq.c

## Purpose

`vnic_rq.c` implements receive queue allocation, initialization, enable/disable, cleanup, and release for Cisco vNIC rings.

## Important APIs, types, and functions

- `vnic_rq_alloc()` binds an RQ to a `RES_TYPE_RQ` MMIO resource, disables it, allocates a coherent descriptor ring, and builds software buffer metadata.
- `vnic_rq_init()` programs ring base/size, completion queue index, error interrupt settings, clears dropped/error counters, and aligns software pointers to the hardware fetch index.
- `vnic_rq_enable()`/`vnic_rq_disable()` control queue execution and poll for disable acknowledgement.
- `vnic_rq_clean()` calls a buffer-clean callback for outstanding descriptors, realigns to the current fetch index, and clears descriptor memory.
- `vnic_rq_free()` releases descriptor memory and buffer blocks.

## Control flow

Allocation creates a circular list of `struct vnic_rq_buf` entries in 64-entry blocks. Receive-fill code uses inline helpers in `vnic_rq.h` to obtain descriptors and post buffers. Completion processing services buffers up to the completed index. Reset/shutdown disables and cleans the ring.

## State and persistence behavior

Persistent software state includes `to_use`, `to_clean`, `buf_index`, and `ring.desc_avail`. Hardware state lives in RQ control registers: base, size, posted/fetch indexes, CQ index, enable/running, dropped counts, and error status.

## Dependencies and integration points

The file depends on `vnic_dev` ring allocation and resource lookup. It integrates with receive buffer posting, CQ completion handling, and FNIC FCoE receive paths.

## Risks and edge cases

- The circular buffer allocation assumes descriptor count does not exceed the 4096-descriptor block limit.
- `vnic_rq_init()` trusts the current hardware fetch index to index into allocated buffer blocks.
- Disable timeout returns `-ETIMEDOUT`; callers must avoid cleaning an enabled queue.
- The queue posts descriptor indexes in batches controlled by `VNIC_RQ_RETURN_RATE`, so low traffic can leave descriptors unposted until the batching threshold.

## Test signals

Tests should exercise allocation sizes, fill/post/service loops, fetch-index-based initialization, disable timeout handling, dropped-count clearing, and cleanup with outstanding receive buffers.
