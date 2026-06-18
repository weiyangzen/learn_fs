# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/npu.c

## Purpose
Implements Airoha NPU/PPE offload support for mt76 MMIO devices. It provides NPU RX queue provisioning, NAPI polling, IRQ handling, TX descriptor filling for NPU-backed queues, queue register handoff, traffic-control offload callbacks, firmware address notification, IRQ masking, and lifecycle attach/detach of the external `airoha-npu` and `airoha-eth` devices.

## Important APIs, Types, And Functions
Key exported entry points are `mt76_npu_init()`, `mt76_npu_deinit()`, `mt76_npu_rx_queue_init()`, `mt76_npu_dma_add_buf()`, `mt76_npu_txdesc_cleanup()`, `mt76_npu_queue_setup()`, `mt76_npu_check_ppe()`, `mt76_npu_net_setup_tc()`, `mt76_npu_send_txrx_addr()`, and `mt76_npu_disable_irqs()`. Internal helpers manage RX page-pool descriptors (`mt76_npu_fill_rx_queue()`), descriptor cleanup, SKB assembly (`mt76_npu_dequeue()`), NAPI polling, IRQ acknowledgment/disable, and TC flower block binding through PPE callbacks.

## Control Flow
Initialization obtains NPU and PPE devices, requesting modules if needed, initializes reserved NPU memory, switches `dev->dma_dev` to the NPU device, stores physical address/type metadata, enables hardware RRO mode, expands RX token space, and publishes NPU/PPE pointers under RCU. RX queue init allocates NPU descriptor rings through the existing queue ops, requests the NPU IRQ, adds NAPI, fills RX buffers, and enables NAPI. IRQ handling acknowledges and disables the NPU queue IRQ, then schedules NAPI. NAPI drains completed descriptors into SKBs, passes them to `drv->rx_skb()`, refills descriptors, and notifies driver RX completion.

## State And Persistence
State is held in `dev->mmio.npu`, `dev->mmio.ppe_dev`, `dev->mmio.phy_addr`, `dev->mmio.npu_type`, `dev->hwrro_mode`, `dev->rx_token_size`, NPU RX queue flags/descriptors, queue `wed_regs`, NAPI slots, page-pool buffers, and RCU-protected PPE/NPU references. RX descriptor ownership persists between NPU hardware, page pool, and mt76 queue head/tail indexes.

## Dependencies And Integration Points
Depends on Airoha NPU/PPE APIs, Linux NAPI, TC flower offload, flow block callbacks, page-pool DMA metadata, mt76 DMA queue ops, WED/NPU queue flags, mt76 driver RX callbacks, and RCU/mutex lifetime rules. It also assumes HW-RRO is available because the NPU offload path requires hardware packet reordering.

## Risks
Descriptor ownership is sensitive: failed NAPI SKB construction, missing DONE bits, or bad multi-frame counts can leak page-pool buffers or stall the queue. `mt76_npu_dma_add_buf()` notes that non-linear SKBs are not yet handled. RCU pointer replacement must pair with queue cleanup so IRQ/NAPI paths do not use freed NPU/PPE devices. TC block lifetime uses a static callback list and must bind/unbind cleanly across netdev teardown.

## Test Signals
Probe with and without loadable `airoha-npu`/`airoha-eth`, RX queue init for both NPU queues, IRQ-to-NAPI delivery, RX refill after budget exhaustion, PPE hash/reason handling, TC flower bind/unbind, offloaded TX descriptor cleanup, device reset/deinit while IRQs are quiet, and page-pool/dma debug checks for leaks.
