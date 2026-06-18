# sources/distributed-fs/ceph-client/include/linux/soc/ti/knav_dma.h

Purpose: This TI Keystone Navigator header defines packet DMA descriptor formats, channel configuration, and optional API wrappers for Navigator DMA.

Important APIs/types/functions: It defines descriptor bit masks for packet length, tags, EPIB/PS info, return queues, buffer length, and error flags; constants for EPIB/PS/software words; enums for TX priority, RX error mode, RX thresholds, and descriptor type; `struct knav_dma_tx_cfg`, `knav_dma_rx_cfg`, `knav_dma_cfg`, and cacheline-aligned `struct knav_dma_desc`. Enabled builds declare `knav_dma_open_channel`, `close_channel`, `get_flow`, and `device_ready`; disabled builds return NULL, `-EINVAL`, or false.

Control flow: Clients configure TX or RX flow parameters, open a named DMA channel, use descriptors and queues for packet movement, query flow IDs, and close the channel.

State and persistence: Channel allocation, descriptor pools, queue IDs, RX flow config, and hardware DMA state are provider-owned. Descriptors carry packet and software-private state.

Dependencies and integration: Includes DMAengine and integrates with Keystone QMSS, networking, and packet accelerator drivers.

Risks and test signals: Descriptor endian/bitfield mistakes cause packet loss or DMA faults. Test disabled config, channel open/close, RX starvation modes, descriptor map/unmap, flow IDs, and high-throughput traffic.
