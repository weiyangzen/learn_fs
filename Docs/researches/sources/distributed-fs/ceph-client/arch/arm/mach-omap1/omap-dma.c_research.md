<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/omap-dma.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/omap-dma.c

## Purpose
Implements the legacy OMAP system DMA platform API and OMAP1 system DMA platform driver, including channel allocation, register programming helpers, start/stop, interrupt dispatch, and command-line channel reservation.

## Important APIs, Types, and Functions
Exports `omap_request_dma()`, `omap_free_dma()`, `omap_set_dma_transfer_params()`, source/destination parameter and burst/pack helpers, `omap_start_dma()`, `omap_stop_dma()`, position queries, `omap_get_dma_active_status()`, `omap_dma_running()`, and `omap_get_plat_info()`.

## Control Flow
The platform driver probe consumes `omap_system_dma_plat_info`, applies channel reservation and 1510 mode flags, allocates `dma_chan[]`, clears channel registers, maps named IRQs, and requests per-channel IRQ handlers. Clients request a free channel under `dma_chan_lock`, configure DMA registers through `p->dma_read/write`, start transfers with IRQ enable and memory barriers, and stop by clearing CCR with errata-specific drain handling. IRQ dispatch reads CSR, handles 1510 shadow channels, logs timeout/drop events, clears active state on block IRQ, and calls client callbacks.

## State and Persistence Behavior
Global state includes platform info `p`, attributes `d`, `errata`, `dma_chan[]`, counts, `enable_1510_mode`, command-line `omap_dma_reserve_channels`, and per-channel dev_id/callback/IRQ/link/saved CSR fields. Hardware state is all SDMA logical channel registers and OMAP16xx dynamic GDMA mux registers.

## Dependencies and Integration Points
Depends on `linux/omap-dma.h`, platform resources named by channel, OMAP1 TC priority registers, clock/device errata flags, LCD DMA helper `omap_lcd_dma_running()`, USB-OMAP consumers, and command-line `omap_dma_reserve_ch=`.

## Risks
This is a deprecated platform DMA API and warns unless the client is `DMA engine`. Channel arrays are global and low-level register writes are SoC-specific. Several paths use `BUG()` on invalid burst modes. Position reads can race running channels unless callers disable interrupts as documented.

## Test Signals
Probe with OMAP15xx and OMAP16xx platform data, request/free all channels, run memory/peripheral DMA through USB or audio clients, verify callbacks and CSR status bits, test `omap_dma_reserve_ch=`, and run suspend idle checks that `omap_dma_running()` blocks deep idle while active.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/omap-dma.c -->
