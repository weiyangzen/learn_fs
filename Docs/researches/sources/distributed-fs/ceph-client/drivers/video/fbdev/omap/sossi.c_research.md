# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/sossi.c

## Purpose
`sossi.c` implements the OMAP1 Special OptimiSed Screen Interface as a `lcd_ctrl_extif`. It provides the external command/data bus used by HWA742-style controllers, converts extif timings, performs FIFO command/data reads and writes, coordinates tear-sync, and starts LCD DMA transfers.

## Important APIs, Types, And Functions
- The static `sossi` state stores MMIO base, clocks, bus width/count, TE mode/line, LCDC completion callback, timing cache, fbdev pointer, and pending-vsync count.
- Timing functions `calc_rd_timings()`, `calc_wr_timings()`, `sossi_convert_timings()`, and `sossi_set_timings()` convert generic picosecond extif timings to SoSSI `TW0/TW1/div` register values.
- Transfer helpers include `sossi_write_command()`, `sossi_write_data()`, `sossi_read_data()`, and `sossi_transfer_area()`.
- `sossi_setup_tearsync()` and `sossi_enable_tearsync()` configure pulse widths and deferred TE mode.
- `sossi_dma_callback()` completes transfer-area operations after LCD DMA completion; `sossi_match_irq()` starts DMA on TE match when needed.
- `omap1_ext_if` exposes the extif method table.

## Control Flow
Initialization ioremaps SoSSI, obtains parent and functional clocks, resets/enables the SoSSI module, validates sync pattern reads, registers an LCDC DMA callback, enables DMA mode, and requests the external TE/match IRQ. HWA742 calls timing conversion/set functions, sets 8- or 16-bit cycles, writes commands/register data, and requests `transfer_area()`. A transfer programs write timing, bus width, TE mode, data cycles, and starts the external bus cycle. If TE is active, it increments `vsync_dma_pending` and waits for `sossi_match_irq()` to call `omap_enable_lcd_dma()`; otherwise it starts DMA immediately. LCD DMA completion stops DMA, stops the SoSSI transfer, disables the clock, and calls the HWA742 completion callback.

## State And Persistence
State is singleton static memory. `last_access` caches read/write timing programming, and `vsync_dma_pending` is protected by a spinlock. No persistent storage is used.

## Dependencies And Integration Points
The file depends on OMAP1 IO registers, SoSSI MMIO, clocks, IRQs, LCD DMA helpers, LCDC DMA callback API, and the `lcd_ctrl_extif` contract from `omapfb.h`. It is normally paired with `hwa742.c`.

## Risks
Several resource-error paths in `sossi_init()` return without undoing earlier ioremap/clock resources. `wait_end_of_write()` spins without timeout. Many hardware timing failures return `-1` rather than specific errno. The TE path depends on edge-falling IRQ wiring and manually deferred DMA start; missed IRQs can hang transfers. Pointer arithmetic on `void *` relies on compiler extensions.

## Test Signals
Expected signals include valid SoSSI sync pattern/version logs, successful extif timing conversion for HWA742, working register reads/writes, DMA completion callbacks, TE-triggered transfers without hangs, and clean disable/clock behavior around repeated manual updates.
