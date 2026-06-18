# sources/distributed-fs/ceph-client/drivers/dma/stm32/stm32-dmamux.c

## Purpose
`stm32-dmamux.c` is a DMA router driver for STM32 DMAMUX hardware. It allocates DMAMUX output channels, programs request routing registers, rewrites DMA specifier arguments so requests are forwarded to an underlying STM32 DMA master, and saves/restores routing state across system sleep.

## Important APIs, Types, And Functions
Important types are `struct stm32_dmamux` and `struct stm32_dmamux_data`. The route object stores selected DMA master, input request, and mux channel id. The device data contains a `dma_router`, clock, MMIO base, request counts, spinlock, in-use bitmap, CCR backup array, and per-master DMA request counts.

Key functions are `stm32_dmamux_probe`, `stm32_dmamux_route_allocate`, `stm32_dmamux_free`, `stm32_dmamux_runtime_suspend`, `stm32_dmamux_runtime_resume`, `stm32_dmamux_suspend`, and `stm32_dmamux_resume`. `stm32_dmamux_init` registers the platform driver at `arch_initcall`, before many client drivers request DMA channels.

## Control Flow
Probe validates the DMAMUX node and `dma-masters` property, allocates flexible device data sized for all masters, checks that each master is compatible with `st,stm32-dma`, reads each master's `dma-requests` count, bounds the total by `STM32_DMAMUX_MAX_DMA_REQUESTS`, reads the mux input request count, maps registers, enables the clock, optionally resets when multiple masters exist, clears all DMAMUX channel control registers, enables runtime PM, and registers an OF DMA router.

Route allocation validates three DMAMUX args, finds a free mux output bit under lock, determines which master owns that output range, obtains the master phandle, resumes the DMAMUX device, records the input request, rewrites `dma_spec` into the selected master format, writes the mux request into `STM32_DMAMUX_CCR(chan_id)`, and returns route data. Freeing the route clears the CCR, releases the in-use bit, runtime-PM puts the device, and frees the route object.

## State And Persistence
Runtime state is the `dma_inuse` bitmap, programmed CCR registers, and route objects owned by DMA router clients. System suspend stores each CCR in `ccr[]` after resuming the device and restores them on resume. Runtime suspend only disables the clock. There is no filesystem persistence.

## Dependencies And Integration Points
The driver depends on OF DMA router support, platform devices, clocks, optional reset controls, runtime PM, spinlocks, and the underlying STM32 DMA master driver. It integrates with device tree through `st,stm32h7-dmamux`, `dma-masters`, `dma-requests`, and routed DMA specifier rewriting. Its output is consumed by `of_dma_router_xlate`, which later calls the selected master DMA controller.

## Risks
The route allocator checks `dma_spec->args[0] > dmamux_requests`; if request numbers are zero-based, the exact upper-bound semantics should match bindings. The in-use bit is set before master phandle and runtime PM success, so all error paths must clear it, which this code attempts. The code assumes master nodes are classic `st,stm32-dma`; adding DMA3 or other masters requires match updates and argument rewrite changes. CCR backup uses a fixed maximum array sized for 32 outputs, so `dma_requests` must remain bounded.

## Test Signals
Signals include probe with one and multiple DMA masters, route allocation until exhaustion, correct DMA spec rewrite for each master range, CCR programming and clearing on route free, runtime PM get/put balance during active routes, suspend/resume preserving CCR mappings, and error-path tests for bad arg count, invalid request, unsupported master, missing phandle, and clock/reset failures.
