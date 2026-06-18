# sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/hw_channel.c

## Purpose
`hw_channel.c` implements the MANA hardware command channel (HWC), the request/response transport used by GDMA setup and later driver commands. It bootstraps HWC queues through the shared-memory channel, receives firmware initialization EQEs, posts RX buffers, sends command WQEs, matches responses by message ID, and handles asynchronous HWC reconfiguration/service events.

## Important APIs, Types, and Functions
- Public entry points are `mana_hwc_create_channel()`, `mana_hwc_destroy_channel()`, and `mana_hwc_send_request()`.
- Message-slot management uses `mana_hwc_get_msg_index()` and `mana_hwc_put_msg_index()` over a semaphore plus `gdma_resource` bitmap.
- RX/TX WQE helpers are `mana_hwc_post_rx_wqe()` and `mana_hwc_post_tx_wqe()`.
- Completion handlers include `mana_hwc_comp_event()`, `mana_hwc_rx_event_handler()`, and `mana_hwc_tx_event_handler()`.
- Initialization and asynchronous EQ handling is centralized in `mana_hwc_init_event_handler()`.
- Queue builders and DMA buffer helpers create HWC EQ/CQ/RQ/SQ structures backed by coherent DMA memory.

## Control Flow
Channel creation allocates `struct hw_channel_context`, assigns it to `gc->hwc.driver_data`, initializes bootstrap queues, asks the shared-memory channel to set up HWC with EQ/CQ/RQ/SQ DMA addresses, waits for initialization completion, builds the CQ table from firmware-provided queue IDs, posts all RX WQEs, allocates caller contexts, and tests the EQ. During initialization, HWC EQEs fill queue IDs, queue depth, maximum request/response sizes, PDID, GPA memory key, PF destination queue IDs, and max CQ count.

Request sending reserves a message ID, copies the caller request into the TX DMA buffer, writes the ID into the GDMA request header, selects PF destination IDs when running as PF, posts the TX WQE, waits for the matching completion, checks response validation and firmware status, then releases the message ID. RX completions find the original RX work request from the SGE DMA address, validate the response message ID, copy the response into the caller buffer, repost the RX WQE before completing the caller, and signal the completion.

Destroy tears down the HWC shared-memory setup if initialization reached the point where `max_num_cqs` was set, destroys TX/RX/CQ/EQ queues, frees caller contexts and inflight bitmap, clears HWC device handles, frees the CQ table, and removes pointers from the GDMA context.

## State and Persistence
HWC state is runtime-only and lives under `struct hw_channel_context`: queue pointers, max request size, inflight message count, caller contexts, timeout, bootstrap values learned from firmware, PF destination queue IDs, and resource bitmap. Message buffers are coherent DMA memory split into per-slot request buffers. The channel persists only while the PCI device is initialized.

## Dependencies and Integration Points
- Depends on GDMA queue APIs from `gdma_main.c`, shared-memory setup/teardown from `shm_channel.c`, and MANA/RDMA service callbacks.
- Uses completions, semaphores, bitmaps, coherent DMA memory, and `vcalloc` for the CQ table.
- HWC events integrate with Ethernet link-change work and RDMA suspend/resume auxiliary service handling.
- `gdma_main.c` depends on HWC to send almost all firmware commands after bootstrap.

## Risks and Edge Cases
- `mana_hwc_get_msg_index()` assumes the semaphore prevents bitmap exhaustion; corrupted bitmap state could set an out-of-range bit.
- Response handling validates response length against caller output buffer but trusts the message ID after the inflight bitmap check.
- RX request index is derived from SGE DMA address arithmetic; corrupted completion OOB data can select the wrong slot unless checks catch it.
- RX WQEs must be reposted before completing the caller to avoid a no-WQE receive window.
- A command timeout shrinks `hwc_timeout` to 1 ms for later commands, and reset paths may set it to zero.

## Test Signals
- HWC bootstrap should receive init EQ ID, queue data, max message sizes, and init-done within 60 seconds.
- `mana_gd_test_eq()` after posting RX buffers is a key channel-health signal.
- Request tests should cover normal replies, `GDMA_STATUS_MORE_ENTRIES`, unsupported-command mapping to `-EOPNOTSUPP`, timeout handling, response too short/too long, invalid message IDs, and RX WQE reposting.
