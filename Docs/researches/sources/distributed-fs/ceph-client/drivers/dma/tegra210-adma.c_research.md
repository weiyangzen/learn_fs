# sources/distributed-fs/ceph-client/drivers/dma/tegra210-adma.c

## Purpose
This driver provides DMAengine support for NVIDIA Tegra ADMA audio DMA controllers on Tegra210, Tegra186, and Tegra264. It is cyclic-oriented and intended for AHUB/audio peripheral transfers between memory and ADMAIF-style request lines.

## Important APIs, Types, and Functions
The central structures are `struct tegra_adma`, `struct tegra_adma_chan`, `struct tegra_adma_desc`, and `struct tegra_adma_chip_data`. The chip data table provides register offsets, bit shifts, request masks, channel counts, page programming callbacks, and burst encoding callbacks. DMAengine operations include `tegra_adma_prep_dma_cyclic()`, `tegra_adma_issue_pending()`, `tegra_adma_tx_status()`, `tegra_adma_pause()`, `tegra_adma_resume()`, `tegra_adma_terminate_all()`, and `tegra_adma_synchronize()`. It uses virt-dma helpers for queueing and callbacks.

## Control Flow
Probe maps either legacy single-region resources or newer page/global resources, derives the ADMA page number, initializes enabled channels from `dma-channel-mask`, initializes global hardware, registers the DMAengine device, and registers `tegra_dma_of_xlate()`. OF xlate assigns a nonzero slave request index to a free channel. Preparation validates cyclic buffer and period sizes, allocates a descriptor, calculates channel control/config/FIFO/TC registers, and reserves the request line for the transfer direction. `issue_pending()` starts the next virt-dma descriptor, programming channel registers and asserting `ADMA_CH_CMD`. Interrupts clear transfer-done status and call `vchan_cyclic_callback()`.

## State and Persistence
The controller tracks reserved RX/TX request lines in bitmaps, enabled channel masks, channel request metadata, the active descriptor pointer, transfer-position counters, and saved register images for runtime PM. Runtime suspend saves global command and active channel registers before disabling `d_audio`; runtime resume restores the clock, page configuration, and active channel state.

## Dependencies and Integration Points
The driver depends on DMAengine, virt-dma, OF DMA, OF IRQ mapping, runtime PM, clocks, and MMIO polling. It integrates with Tegra AHUB clients through one-cell DMA specifiers that name the request index. Tegra186 and Tegra264 page/global-register layouts are selected by compatible string.

## Risks
Only cyclic transfers are implemented, so SG or memcpy clients are unsupported. `tegra_adma_pause()` and `resume()` assume `tdc->desc` exists; callers must not pause an idle channel. Request-line reservation prevents RX/TX sharing conflicts, but stale reservations would block future users until termination/free. Page resource math can fail if DT resource order or offsets are wrong. Residue uses a hardware position counter with wrap handling and must be tested over long-running cyclic streams.

## Test Signals
Exercise audio capture/playback on each supported SoC data variant, valid and invalid `dma-channel-mask` values, one-cell OF request mapping, concurrent RX/TX reservation conflicts, pause/resume, runtime suspend/resume during active cyclic DMA, and removal/IRQ disposal. Negative tests should include zero request index, unaligned buffers, too many periods, and invalid page/global resource layout.
