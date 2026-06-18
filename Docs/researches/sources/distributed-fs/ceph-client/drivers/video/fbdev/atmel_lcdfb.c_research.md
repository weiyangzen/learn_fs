# sources/distributed-fs/ceph-client/drivers/video/fbdev/atmel_lcdfb.c

## Purpose
`atmel_lcdfb.c` is an fbdev platform driver for Atmel AT91 LCD controllers. It parses display configuration from device tree, allocates or maps framebuffer memory, programs LCDC DMA and timing registers, supports palettes/pseudo-palettes, backlight/contrast PWM, regulators or GPIO power control, interrupt recovery, and suspend/resume.

## Important APIs, types, and functions
`struct atmel_lcdfb_info` is the primary private state: fb info, MMIO, IRQ, work item, clocks, backlight, pseudo palette, platform data, SoC config, and optional regulator. `struct atmel_lcdfb_config` records SoC feature differences such as alternate pixel clock, HOZVAL support, and old intensity-bit color format.

Key functions include `atmel_lcdfb_check_var()`, `atmel_lcdfb_set_par()`, `atmel_lcdfb_setcolreg()`, `atmel_lcdfb_pan_display()`, `atmel_lcdfb_blank()`, `atmel_lcdfb_interrupt()`, `atmel_lcdfb_task()`, `atmel_lcdfb_of_init()`, `atmel_lcdfb_probe()`, `atmel_lcdfb_remove()`, and PM callbacks. Backlight support is behind `CONFIG_BACKLIGHT_ATMEL_LCDC`.

## Control flow
Probe allocates `fb_info`, parses the `display` phandle for bits per pixel, guard time, `lcdcon2`, `dmacon`, GPIO power controls, wiring mode, backlight flags, and native videomode. It obtains regulator and clocks, enables clocks, validates the selected mode, reserves/maps MMIO, maps a preallocated framebuffer resource or allocates write-combined DMA memory, initializes contrast/backlight, requests IRQ, sets parameters, registers the framebuffer, then powers up the LCD panel.

`check_var()` selects a modelist mode when required, checks pixel clock against `lcdc_clk`, aligns x resolution to four pixels, validates memory size, clamps timing fields to register limits, and configures bitfields for 1/2/4/8/16/24/32 bpp. `set_par()` stops the controller, updates DMA base and frame config, computes and programs the pixel clock divider, writes LCDCON2, timing registers, frame size, FIFO threshold, interrupt masks, waits for DMA idle, and restarts. Underflow IRQ schedules a workqueue reset rather than resetting directly in interrupt context.

## State and persistence behavior
Framebuffer contents persist in mapped preallocated memory or DMA-allocated write-combined memory until freed. Driver state persists in `fb_info->par` for the device lifetime. Hardware state lives in LCDC registers and is rebuilt by `set_par()` or resume. Suspend saves the contrast control register, disables LCD power and clocks, and resume restores clocks, power, contrast, and error interrupts.

## Dependencies and integration points
The driver integrates with the platform bus, Open Firmware display timing APIs, fbdev core, DMA mapping, resource reservation, clk framework, GPIO descriptors, regulator framework, backlight core, workqueues, and Atmel LCDC register definitions in `<video/atmel_lcdc.h>`.

## Risks and edge cases
Probe error unwinding spans many resources and must keep map-vs-DMA framebuffer ownership correct. `atmel_lcdfb_check_var()` is called in probe but its return value is not checked before continuing, so invalid DT modes may fail later or leave adjusted state unexpectedly. Register polling loops wait for busy bits with sleeps and no explicit timeout. Pixel clock divider rounding mutates `info->var.pixclock`; tests need to accept adjusted clocks. Optional GPIO power control skips failed GPIO indexes rather than failing immediately, which may hide incomplete power definitions.

## Test signals
Boot with each compatible string, validate DT parsing failure paths, test 1/2/4/8/16/24/32 bpp mode setup, verify RGB/BGR wiring and old intensity-bit palettes, confirm DMA framebuffer allocation and preallocated-memory mapping paths, induce FIFO underflow and observe workqueue reset, test blank/powerdown, regulator/GPIO power toggles, backlight brightness updates, pan display y-offset updates, and suspend/resume with display restoration.
