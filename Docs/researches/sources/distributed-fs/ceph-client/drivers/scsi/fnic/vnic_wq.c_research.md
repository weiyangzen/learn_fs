# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq.c

## Purpose

`vnic_wq.c` implements transmit/work queue allocation, initialization, enable/disable, cleanup, and release for Cisco vNIC queues. It also supports the special devcmd2 WQ resource.

## Important APIs, types, and functions

- `vnic_wq_alloc()` binds a WQ resource, disables it, allocates a coherent descriptor ring, and creates software buffer tracking.
- `vnic_wq_devcmd2_alloc()` binds the devcmd2 resource and allocates only the descriptor ring required for queued firmware commands.
- `vnic_wq_init_start()` initializes a WQ using explicit fetch and posted indexes, used by devcmd2 setup.
- `vnic_wq_init()` initializes a normal WQ from index zero.
- `vnic_wq_enable()`/`vnic_wq_disable()` control queue execution.
- `vnic_wq_clean()` cleans outstanding buffers, resets indexes/error status, and clears descriptors.
- `vnic_wq_free()` releases ring and buffer-block memory.

## Control flow

Allocation builds a circular chain of `struct vnic_wq_buf` entries that map one-to-one with descriptors. Producers fill the descriptor at `to_use`, call `vnic_wq_post()` from the header, and hardware owns descriptors up to `posted_index`. Completion paths service buffers through `vnic_wq_service()`. Reset/shutdown disables then cleans.

## State and persistence behavior

Persistent software state includes `to_use`, `to_clean`, `ring.desc_avail`, and `pkts_outstanding`. Hardware state is in the WQ control registers: ring base/size, posted/fetch indexes, CQ index, enable/running, DCA, and error interrupt/status fields.

## Dependencies and integration points

It depends on `vnic_dev` for resources and DMA rings. It is used by normal transmit/FCoE work queues and by `vnic_dev.c` for devcmd2 command submission.

## Risks and edge cases

- `vnic_wq_init_start()` indexes `wq->bufs[...]`; devcmd2 allocation does not allocate buffer metadata, so this path relies on the selected usage not dereferencing `to_use` later for devcmd2 buffer servicing.
- Disable waits only 100 microseconds total; slow hardware can produce timeout errors.
- Cleaning asserts the queue is disabled with `BUG_ON()`, which is harsh if callers violate ordering.

## Test signals

Tests should cover normal WQ allocation/post/service/clean, devcmd2 allocation/init, disable timeout, descriptor wraparound, and memory-barrier-sensitive posting.
