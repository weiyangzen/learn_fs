# sources/distributed-fs/ceph-client/include/linux/platform_data/amd_xdma.h

Purpose: defines platform data and channel filter metadata for AMD XDMA engine integration.

Important APIs and types: `struct xdma_chan_info` carries DMA transfer direction, `XDMA_FILTER_PARAM(chan_info)` casts it for dmaengine filtering, and `struct xdma_platdata` provides `max_dma_channels`, `device_map_cnt`, and `dma_slave_map *device_map`.

Control flow: platform code registers XDMA with the platform data; clients request DMA channels using filter info, and the driver validates requested direction and slave map entries against the advertised channel count.

State and persistence: the header describes static platform capabilities and mappings. Active channels, descriptors, and hardware queues are runtime driver state.

Dependencies and integration points: depends on `linux/dmaengine.h` and integrates with dmaengine client channel request paths, platform devices, and DMA slave mapping.

Risks and test signals: risks include wrong `device_map_cnt`, invalid map lifetime, direction mismatch, and channel limit off-by-one errors. Test probe with multiple map counts, channel request/release, H2D/D2H transfers, error IRQs, and remove while channels are idle/active.
