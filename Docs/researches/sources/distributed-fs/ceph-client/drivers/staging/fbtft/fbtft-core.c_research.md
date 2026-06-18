# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-core.c

## Purpose

`fbtft-core.c` is the shared framebuffer core for small TFT LCD drivers in staging. It allocates and registers `fb_info`, owns deferred framebuffer flushing, initializes display controllers from platform data or firmware properties, requests GPIOs, manages optional backlight support, and provides the common probe/remove helpers used by panel-specific FBTFT drivers.

## Important APIs, Types, and Functions

Exported entry points are `fbtft_write_buf_dc()`, `fbtft_dbg_hex()`, `fbtft_framebuffer_alloc()`, `fbtft_framebuffer_release()`, `fbtft_register_framebuffer()`, `fbtft_unregister_framebuffer()`, `fbtft_register_backlight()`, `fbtft_unregister_backlight()`, `fbtft_init_display()`, `fbtft_probe_common()`, and `fbtft_remove_common()`. Internal helpers include GPIO acquisition, generic reset, MIPI DCS address window setup, dirty-line tracking, deferred I/O, color-register programming, blanking, operation-table merging, firmware-property parsing, and default GPIO verification.

## Control Flow

Probe enters `fbtft_probe_common()`, obtains platform data or properties, allocates the framebuffer, assigns SPI or platform device ownership, chooses default register/video-memory/write methods from bus width and register width, handles 9-bit SPI emulation when needed, merges driver and platform callbacks, and calls `fbtft_register_framebuffer()`. Registration requests GPIOs, verifies required pins, initializes and configures the controller, performs a full display update, applies gamma, registers backlight, registers the framebuffer, and creates sysfs attributes. Deferred framebuffer writes mark dirty line ranges and later call `update_display()` to set a GRAM window and flush the corresponding vmem range.

## State and Persistence Behavior

Runtime state is in `struct fbtft_par`: GPIO descriptors, operation callbacks, vmem, transmit buffer, gamma curves, dirty-line bounds, debug flags, and backlight polarity. The file has no disk persistence; sysfs debug/gamma writes and framebuffer contents affect only device/kernel state. Display initialization and gamma programming are persistent only as controller-side volatile settings until power or reset.

## Dependencies and Integration Points

The file integrates Linux fbdev deferred I/O, gpiod, SPI, platform devices, firmware properties, backlight, MIPI display commands, sysfs helpers in `fbtft-sysfs.c`, and bus helpers declared in `fbtft.h`. Panel drivers integrate by filling `struct fbtft_display` and optional `fbtft_ops`, usually through registration macros in the header.

## Risks and Edge Cases

The init-sequence walkers pass a fixed 64-element varargs list into `write_register()` even when fewer entries are valid, so the callee must obey the explicit length. Device-tree `init` parsing increments through the array while checking high-bit markers and can read the next value before the loop condition is re-evaluated, making malformed terminal entries worth fuzzing. Deferred dirty ranges reset to start=`yres-1`, end=`0`; callers must avoid scheduling an empty or inverted range except through the sanity fallback. `sprintf()` is used for small diagnostic strings with bounded inputs but still lacks explicit size checking. Backlight polarity is inferred from the current GPIO value, which can be wrong if board defaults are not stable.

## Test Signals

Build with representative SPI and platform FBTFT panel drivers. Probe tests should cover property-only configuration, platform-data overrides, 8/9/16-bit bus paths, missing GPIOs, 9-bit SPI hardware and emulation, gamma parsing, backlight registration, framebuffer unregister/release, and malformed init sequences. Runtime tests should dirty single pages, full-screen ranges, blank/unblank, rotate 90/270 sizing, and exercise error handling from `write_vmem()` and GPIO/regulator absence.
