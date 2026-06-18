
# sources/distributed-fs/ceph-client/include/linux/platform_data/dma-dw.h

## Purpose
This header provides platform data for Synopsys DesignWare DMA controllers and their slave devices. It describes controller capacity, channel allocation policy, bus master widths, burst limits, handshake polarity, and quirks.

## Important APIs And Types
`struct dw_dma_slave` describes a slave endpoint: DMA master device, source/destination request lines, memory/peripheral bus masters, permitted channel mask, and handshake polarity. `struct dw_dma_platform_data` describes the controller: number of masters/channels, allocation and priority order, max block size, per-master data widths, per-channel multi-block and max-burst support, protection-control bits, and quirk flags such as `DW_DMA_QUIRK_XBAR_PRESENT`. Constants cap masters/channels and define burst and protection masks.

## Control Flow, State, And Persistence
There is no code flow here. Platform data is consumed at controller and slave probe to restrict channel selection and program hardware descriptors. State is static hardware topology and controller capability.

## Dependencies And Integration Points
It depends on Linux bits/types and forward-declares `struct device`. It integrates the DesignWare DMA engine driver with platform devices, DMAengine slave configuration, and possible crossbar routing.

## Risks And Test Signals
Incorrect request ids, channel masks, bus master assignment, burst limits, or data widths can cause failed channel allocation or broken transfers. Test signals include DMAengine channel requests from each slave, memory-to-device and device-to-memory transfers, burst-size validation, multi-block operation, and behavior with crossbar-present platforms.
