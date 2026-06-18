# sources/distributed-fs/ceph-client/drivers/dma/ti/dma-crossbar.c

## Purpose
This file implements TI DMA crossbar routing as an OF DMA router for AM335x/AM437x EDMA crossbars and DRA7-family crossbars. It translates client DMA specifiers into DMA-master specifiers while programming mux registers.

## Important APIs, Types, and Functions
AM335x support uses `struct ti_am335x_xbar_data`, `struct ti_am335x_xbar_map`, `ti_am335x_xbar_route_allocate()`, and `ti_am335x_xbar_free()`. DRA7 support uses `struct ti_dra7_xbar_data`, `struct ti_dra7_xbar_map`, `ti_dra7_xbar_route_allocate()`, and `ti_dra7_xbar_free()`. `ti_dma_xbar_probe()` dispatches by compatible string. `of_dma_router_register()` is the integration API.

## Control Flow
At `arch_initcall`, the platform driver registers. Probe identifies the crossbar type. AM335x probe validates the DMA master, reads request counts, maps the mux resource, resets all request lines to zero, and registers a router. AM335x allocation validates three arguments, sets `dma_spec->np` to the DMA master, rewrites the request spec to two cells, and writes the requested event value to the selected DMA line. DRA7 probe validates the master, reads request counts and safe-map value, reserves configured request ranges, resets free lines to the safe value, and registers a router. DRA7 allocation finds a free output line under a mutex, rewrites the first DMA spec arg to the allocated DMA request plus offset, and writes the selected input to the mux.

## State and Persistence
AM335x state is simple MMIO plus request-count limits; route-free resets the mapped line to zero. DRA7 keeps a `dma_inuse` bitmap protected by a mutex, a safe reset value, request counts, and a master-specific offset for EDMA vs SDMA numbering. Mux register programming persists until route-free or driver/probe reset.

## Dependencies and Integration Points
The driver depends on OF DMA router infrastructure, OF platform device lookup, DMA master phandles, MMIO resource mapping, and device tree properties such as `dma-masters`, `dma-requests`, `ti,dma-safe-map`, and `ti,reserved-dma-request-ranges`. It is selected internally by EDMA/OMAP DMA Kconfig paths.

## Risks
DRA7 dynamic allocation can exhaust DMA request lines. Incorrect reserved ranges or safe-map values can route spurious events. AM335x has a special register layout for events 60-63, so off-by-one errors are hardware-specific. Allocation uses `of_find_device_by_node()` and must always balance `put_device()`. Bad DT arg counts or unsupported DMA master compatibles lead to routing failure.

## Test Signals
Validate DT routing for AM335x and DRA7 with multiple clients, free/reallocate cycles, reserved-range enforcement, request exhaustion, safe-map reset on route free, and EDMA vs SDMA offset handling. Build and boot tests should verify `arch_initcall` registration before DMA clients request channels.
