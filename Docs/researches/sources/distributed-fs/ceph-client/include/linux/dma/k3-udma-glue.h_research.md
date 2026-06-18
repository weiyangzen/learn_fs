<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/k3-udma-glue.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/k3-udma-glue.h

## Purpose
Declares TI K3 UDMA glue APIs that let network and peripheral drivers manage TX/RX channels, rings, descriptors, flows, and address conversions.

## Important APIs, Types, And Functions
TX types include `struct k3_udma_glue_tx_channel_cfg` and opaque TX channels, with request/release, push/pop, enable/disable, teardown, reset, descriptor size, completion queue id, IRQ, DMA-device, and CPPI5 address conversion APIs. RX types include `struct k3_udma_glue_rx_flow_cfg`, `struct k3_udma_glue_rx_channel_cfg`, opaque RX channels, flow selector constants, request/release, enable/disable, teardown, push/pop, flow init/enable/disable, FDQ/flow/IRQ queries, reset, DMA-device, and address conversion APIs.

## Control Flow
Drivers request TX or RX channels by name or thread id, configure rings/flows, push CPPI5 host descriptors to rings, pop completed descriptors, enable channels for traffic, and tear down/reset channels during stop. RX can allocate flow ranges dynamically, use RX channel id as flow id, or attach to a remote-owned channel.

## State And Persistence
State includes channel objects, ring configuration, flow ids, FDQ/RXQ ring ids, descriptor DMA addresses, teardown state, and remote-channel mode. It is runtime hardware/channel state.

## Dependencies And Integration Points
Depends on TI K3 ring accelerator, CPPI5 descriptors, device tree nodes, DMA addresses, and UDMA/PKTDMA controllers. Integrates Ethernet and other K3 peripheral drivers with NAVSS DMA.

## Risks And Edge Cases
Descriptor ownership and address conversion must be exact. Remote RX channels forbid normal channel operations and only allow attach/configure behavior. Flow id base/count/default settings must match hardware allocation. Reset cleanup callbacks must release any descriptors still in rings.

## Test Signals
Tests should cover TX/RX request by name and thread id, descriptor push/pop, IRQ queries, flow init/enable/disable, dynamic and fixed flow ranges, remote RX behavior, teardown sync/async, reset cleanup, CPPI5/DMA address conversion, and stop/remove with pending descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/k3-udma-glue.h -->
