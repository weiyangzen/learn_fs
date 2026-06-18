# sources/distributed-fs/ceph-client/drivers/dma/dw/rzn1-dmamux.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/rzn1-dmamux.c -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/rzn1-dmamux.c

### Purpose
`rzn1-dmamux.c` implements the Renesas RZ/N1 DMA router that maps device-tree DMA requests through the SoC system-controller DMAMUX into one of the supported DesignWare DMA masters. It lets client DMA specifiers select a request line and mux value while the DMA router framework rewrites the phandle target to the underlying DMAC.

### Important APIs, Types, And Functions
Important state is `struct rzn1_dmamux_data`, which embeds `struct dma_router` and a bitmap of allocated mux request lines, and `struct rzn1_dmamux_map`, which remembers the request index for release. Key functions are `rzn1_dmamux_probe()`, `rzn1_dmamux_route_allocate()`, and `rzn1_dmamux_free()`. The driver registers through `of_dma_router_register()` and uses `r9a06g032_sysctrl_set_dmamux()` to program mux bits.

### Control Flow, State, And Persistence
Probe validates that the first `dma-masters` phandle is a supported `"renesas,rzn1-dma"` node, initializes the router, and registers an OF DMA router callback. Allocation requires a six-cell DMA specifier, consumes the last two cells as mux request index and value, validates the channel/request relationship, switches `dma_spec->np` to DMAC0 or DMAC1, marks the request line busy in `used_chans`, and programs the sysctrl mux bit. Release clears the allocation bitmap and frees the route data. Runtime state is held only in the device driver data and the sysctrl DMAMUX register state.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on OF DMA router APIs, platform devices, device-tree `dma-masters`, and the RZ/N1 sysctrl driver. It integrates with DesignWare DMA by retargeting the DMA specifier to a DMAC node before normal DMA channel lookup. Risks include invalid device-tree cell counts, leaking OF node references on error paths, double allocation of mux lines, mismatched `req_idx % 16` validation, and global sysctrl state that must match the bitmap. Test signals include two-DMAC routing, busy-line rejection, invalid channel/request handling, route release and reallocation, and functional peripheral DMA after mux programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/rzn1-dmamux.c -->
