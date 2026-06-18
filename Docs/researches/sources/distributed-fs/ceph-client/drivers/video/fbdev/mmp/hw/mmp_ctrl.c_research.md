# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/mmp_ctrl.c

## Purpose
Implements the Marvell MMP LCD/display controller hardware provider. It maps controller registers, enables clocks, handles interrupts, registers MMP display paths with overlay operations, programs timing/pixel clock/interface registers, and optionally registers the LCD-controller SPI bus.

## Important APIs, Types, and Functions
- `ctrl_handle_irq()` masks and clears pending LCD interrupt status.
- `fmt_to_reg()` translates MMP pixel formats into DMA control register bits including RGB/YUV swap and CSC enable.
- `overlay_set_win()`, `overlay_set_addr()`, `overlay_set_onoff()`, and `overlay_set_fetch()` implement hardware overlay operations.
- `path_onoff()`, `path_enabledisable()`, and `path_set_mode()` manage path power, panel callbacks, display timings, interface polarity, and pixel clock divisor.
- `ctrl_set_default()` initializes global LCD control and interrupt enable/mask defaults.
- `path_set_default()`, `path_init()`, and `path_deinit()` configure path defaults and register/unregister paths with the MMP core.
- `mmphw_probe()` is the platform driver probe for `mmp-disp`.

## Control Flow
Probe gets memory and IRQ resources plus `mmp_mach_plat_info`, allocates `mmphw_ctrl` with one `mmphw_path_plat` per configured path, requests/maps registers, requests IRQ, enables the named clock, initializes global registers, registers each path into the core, then registers the LCD SPI master when enabled. Framebuffer clients later call overlay/path ops: `set_par()` in `mmpfb.c` leads to `path_set_mode()`, `overlay_set_win()`, `overlay_set_addr()`, and `overlay_set_onoff()`.

## State and Persistence
`struct mmphw_ctrl` stores platform name, IRQ, MMIO base, clock, device, mutex, and flexible path-platform array. Each path platform stores config/link/rbswap bits and the registered `mmp_path`. Hardware state includes LCD global control, DMA control, path timing registers, SCLK divisors, interface mode/rbswap registers, and overlay DMA addresses.

## Dependencies and Integration Points
Depends on `mmp_ctrl.h`, `<video/mmp_disp.h>`, platform data, devm resource APIs, clocks, IRQ handling, and optional `lcd_spi_register()` from `mmp_spi.c`. Exposes hardware to `core.c` through `mmp_register_path()`.

## Risks
There is no remove callback, so registered paths and optional SPI host are not explicitly unregistered on device removal. `ctrl_handle_irq()` writes `~isr` to clear status, which depends on write-one/zero semantics being exactly as expected. Pixel clock divider is integer-only and does not handle zero or out-of-range divisors robustly. `path_init()` returns 0 for allocation or registration failure, losing detailed error codes.

## Test Signals
Test platform probe with valid/invalid resources and platform data, IRQ clear under status bits, path registration count and names, panel power callbacks on overlay enable/disable, pixel format conversion for RGB/YUV formats, timing register programming, clock divisor values, and SPI bus registration when configured.
