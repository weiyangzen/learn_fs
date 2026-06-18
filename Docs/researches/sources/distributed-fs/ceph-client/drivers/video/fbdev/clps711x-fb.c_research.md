# sources/distributed-fs/ceph-client/drivers/video/fbdev/clps711x-fb.c

## Purpose

This platform driver provides fbdev support for the Cirrus Logic CLPS711X/EP7209 LCD controller. It programs the LCD controller registers, framebuffer start address, grayscale palette, syscon LCD enable bit, and optional LCD regulator. The complete 374-line source was read.

## Important APIs, Types, and Functions

Private state lives in `struct clps711x_fb_info`, containing the LCD clock, controller MMIO base, syscon regmap, framebuffer size, native display mode, optional regulator, AC prescale, and colormap inversion flag. `clps711x_fb_ops` implements `clps711x_fb_setcolreg()`, `clps711x_fb_check_var()`, `clps711x_fb_set_par()`, and a no-op blank method using default I/O-memory fbops. LCD class integration is through `clps711x_lcd_ops`, `clps711x_lcd_get_power()`, and `clps711x_lcd_set_power()`.

## Control Flow

Probe exits early if `video=clps711x-fb:off` disables the driver. It allocates `fb_info`, maps controller and framebuffer resources, requires framebuffer physical alignment to 256 MiB, obtains the clock and syscon regmap, reads the `display` phandle, converts the native timing to `fb_videomode`, reads `ac-prescale`, `cmap-invert`, and `bits-per-pixel`, then disables the LCD if the current hardware start address does not match the resource. If LCD is disabled, it writes the framebuffer base nibble and clears framebuffer memory. It then obtains the optional `lcd` regulator, initializes fb metadata, allocates a 16-entry cmap, applies the mode through `fb_set_var()`, registers an LCD class device, and finally registers the framebuffer.

Mode validation accepts 1 through 4 bpp and checks the LCDCON width and framebuffer-size fields. Mode setting computes line length, `smem_len`, LCDCON frame length, horizontal size, AC prescale, pixel prescaler from clock rate and pixclock, grayscale enable/mode bits, disables the LCD, writes LCDCON, then re-enables the LCD.

## State and Persistence Behavior

State is in `fb_info`, `clps711x_fb_info`, LCDCON/PALLSW/PALMSW/FBADDR registers, syscon `SYSCON1_LCDEN`, and the regulator enable state. The framebuffer memory is cleared on probe only when the controller is not already using the same framebuffer address. There is no persistent storage, but device-tree properties determine startup behavior.

## Dependencies and Integration Points

The file depends on platform-device resources, devm MMIO mapping, clock framework, syscon/regmap, CLPS711X syscon definitions, regulator framework, OF display timings, LCD class devices, and fbdev core registration. Device-tree binding uses compatible `cirrus,ep7209-fb`, a `display` phandle, `bits-per-pixel`, optional `ac-prescale`, optional `cmap-invert`, and optional `lcd` regulator.

## Risks and Edge Cases

Risks include integer truncation in byte-size calculations for non-byte-aligned 1/2/4 bpp modes, strict 256 MiB physical address alignment, optional regulator handling where non-defer errors are tolerated as absent, and no real `fb_blank()` implementation beyond the LCD class power hook. The `clps711x_fb_setcolreg()` inversion path computes `0xf - level` after `level` has already been shifted into position, which is only intuitive for low-index shifts and should be verified against hardware palette layout. The unreachable `unregister_framebuffer(info);` line after a successful return is dead code.

## Test Signals

Test with DT-provided timings at 1, 2, and 4 bpp; invalid bpp and invalid pixclock rejection; syscon LCD enable transitions around `set_par`; framebuffer alignment failure; regulator defer and enable/disable paths; palette writes with and without `cmap-invert`; probe/remove leak checks; and fbcon or userspace writes confirming grayscale output.
