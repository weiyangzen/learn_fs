# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcdc.c

## Purpose
`lcdc.c` implements the OMAP1 internal LCD controller as the `omap1_int_ctrl` backend for the legacy omapfb driver. It programs LCDC timing/control registers, allocates framebuffer and palette DMA memory, configures LCD DMA, handles palette loads, reset-on-error interrupts, update mode, and suspend/resume.

## Important APIs, Types, And Functions
- `struct omap_lcd_controller lcdc` stores update mode, external-mode flag, active plane geometry, color mode, palette memory, IRQ mask/completions, clock, fbdev pointer, DMA callback, and allocated VRAM.
- Register helpers include `set_load_mode()`, `enable_controller()`, `disable_controller_async()`, `disable_controller()`, and `reset_controller()`.
- `setup_lcd_dma()` converts fbdev var/plane state into LCD DMA B1 geometry, data type, stride, rotation, and mirror settings.
- `lcdc_irq_handler()` handles DONE, LOADED_PALETTE, FIFO underflow, and sync-lost status.
- Plane/update APIs include `omap_lcdc_setup_plane()`, `omap_lcdc_enable_plane()`, `omap_lcdc_set_update_mode()`, `omap_lcdc_setcolreg()`, suspend/resume, and DMA callback registration.
- `omap_lcdc_init()` and `omap_lcdc_cleanup()` own clock, IRQ, LCD DMA, palette memory, and framebuffer memory resources.

## Control Flow
Initialization clears LCDC control, obtains `lcd_ck`, derives its rate from `tc_ck` with an AMS Delta adjustment, enables the clock, requests the LCDC IRQ, reserves LCD DMA, configures single-transfer/external mode, optionally allocates palette RAM, and allocates framebuffer DMA memory. Internal mode then uses `omap_lcdc_set_update_mode(OMAPFB_AUTO_UPDATE)` to program panel timings, load palette, set up frame DMA, choose frame load mode, enable DONE IRQs, and enable the LCD controller. External mode skips palette/controller auto-update and uses `setup_lcd_dma()` for single transfer windows driven by an external controller.

Plane setup validates only plane 0/channel 0 at position 0, clamps against rotated panel size, stores offset/width/screen width/color mode, maps color mode to bpp/palette code, and either sets up external DMA immediately or, in auto-update internal mode, disables the controller, stops DMA, reprograms DMA, and reenables the controller. Palette update configures LCD DMA to copy palette RAM and waits for `LOADED_PALETTE`.

## State And Persistence
All state is static singleton state for one OMAP1 LCD controller. `last_frame_complete` and `palette_load_complete` serialize disable/palette operations against IRQs. The controller owns allocated WC DMA memory for both palette and framebuffer until cleanup.

## Dependencies And Integration Points
The file depends on OMAP1 IO accessors, OMAP1 CPU/machine checks, clocks, DMA allocation, LCD DMA helpers, fbdev types, and `struct lcd_panel` timing fields. It is selected by `omapfb_main.c` as the internal controller and is also used in external mode by HWA742/SoSSI.

## Risks
Several invalid input paths call `BUG()`. The reset logic gives up after repeated FIFO underflow/sync-lost events but leaves limited diagnostics. Palette load and disable waits have 500 ms timeouts but continue after logging errors. `free_fbmem()` and `free_palette_ram()` assume allocation succeeded. Register programming uses many panel fields directly and can underflow if timing values are zero where hardware expects `value - 1`.

## Test Signals
Key signals include successful clock/IRQ/DMA allocation, correct mode logs from omapfb, visible auto-update display, CLUT palette writes, DONE and LOADED_PALETTE completions, recoverable FIFO underflow/sync-lost logging, suspend/resume blanking, and external-mode DMA callbacks through SoSSI/HWA742.
