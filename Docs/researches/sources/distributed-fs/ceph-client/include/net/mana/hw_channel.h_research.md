<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/hw_channel.h -->
# sources/distributed-fs/ceph-client/include/net/mana/hw_channel.h

## Purpose
`hw_channel.h` defines the MANA hardware communication channel used to exchange management messages with the PF/firmware after shared-memory bootstrap.

## Important APIs, types, and functions
Important structures are HWC init unions, `struct hwc_rx_oob`, `struct hwc_tx_oob`, `struct hwc_work_request`, `struct hwc_dma_buf`, `struct hwc_cq`, `struct hwc_wq`, `struct hwc_caller_ctx`, and `struct hw_channel_context`. Public functions are `mana_hwc_create_channel`, `mana_hwc_destroy_channel`, and `mana_hwc_send_request`.

## Control flow
Channel creation builds bootstrap queues with fixed HWC init data IDs, maps DMA buffers for in-flight request/response messages, and wires CQ event callbacks. `mana_hwc_send_request` uses a semaphore and an inflight-resource map to reserve a message slot, posts a TX WQE with OOB routing to PF virtual queues, waits for completion with timeout, and copies the response into the caller buffer.

## State and persistence
Runtime state includes RX/TX GDMA queues, one CQ, DMA-backed in-flight request slots, caller completion context, PF destination queue IDs, negotiated maximum request/response sizes, and HWC timeout. There is no disk persistence; firmware-visible queue and DMA state is torn down by channel destruction.

## Dependencies and integration points
It depends on GDMA WQE/SGE/queue types, Linux completions, semaphores, device memory, and the shared memory channel that bootstraps initial HWC queue data. It integrates GDMA resource management and MANA NIC/RDMA commands.

## Risks and test signals
Risks include request/response size overflow, timeout recovery, stale `caller_ctx`, inflight slot leaks, OOB bitfield mismatch, CQ callback ordering, and bootstrap queue-depth assumptions. Tests should exercise channel create/destroy, parallel requests, timeout paths, PF reconfiguration events, and max-size boundary handling.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mana/hw_channel.h` completely for this pass (211 lines, 4133 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/hw_channel.h -->
