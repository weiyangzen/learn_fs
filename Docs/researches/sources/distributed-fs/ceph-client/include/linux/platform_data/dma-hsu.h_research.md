
# sources/distributed-fs/ceph-client/include/linux/platform_data/dma-hsu.h

## Purpose
This header defines platform slave data for Intel High Speed UART DMA. It maps a consumer to a specific HSU DMA controller device and channel id.

## Important APIs And Types
`struct hsu_dma_slave` contains `dma_dev`, the DMA master device, and `chan_id`, the channel identifier to request or match.

## Control Flow, State, And Persistence
No executable control flow is defined. UART or serial platform code supplies this structure, and the DMA engine driver or filter uses it during channel selection. The state is static platform routing.

## Dependencies And Integration Points
It forward-declares `struct device` and integrates serial/HSUART clients with the HSU DMA controller through platform data.

## Risks And Test Signals
Wrong channel ids or device pointers lead to failed DMA channel lookup or data routed through the wrong channel. Test signals include UART TX/RX DMA operation, fallback to PIO if supported, suspend/resume with DMA active, and channel allocation failure paths.
