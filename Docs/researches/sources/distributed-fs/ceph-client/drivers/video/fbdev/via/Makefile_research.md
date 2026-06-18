# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/Makefile

## Purpose
This Makefile defines how the VIA framebuffer driver is built when `CONFIG_FB_VIA` is enabled. It links a single `viafb.o` module/object from the core fbdev file, hardware programming files, output-device helpers, acceleration, mode tables, VIA core helpers, and AUX/I2C encoder support.

## Important APIs, Types, And Functions
There are no C APIs in this file. Its important build contract is `obj-$(CONFIG_FB_VIA) += viafb.o` and the `viafb-y := ...` object list. The list includes `viafbdev.o`, `hw.o`, `via_i2c.o`, `dvi.o`, `lcd.o`, `ioctl.o`, `accel.o`, `global.o`, `viamode.o`, `via_clock.o`, GPIO/core files, modesetting, and multiple AUX encoder implementations.

## Control Flow
Kbuild evaluates the config-gated object line. When enabled, all objects in `viafb-y` are compiled and linked into the composite `viafb.o`. Ordering is mostly link ordering; runtime initialization is still governed by the C files' init paths and function calls.

## State And Persistence
The Makefile has no runtime state. Its persistent effect is the build graph and which object files become part of the VIA fbdev driver.

## Dependencies And Integration Points
It integrates with Linux kbuild and the `CONFIG_FB_VIA` Kconfig symbol. Because it aggregates many helper files, missing or misordered entries would surface as unresolved symbols or absent runtime support for DVI, LCD, acceleration, I2C, AUX encoders, or mode tables.

## Risks
The broad object list means build failures can arise from optional-looking functionality that is actually always linked when `CONFIG_FB_VIA` is enabled. The file does not express finer-grained config around individual encoders or acceleration helpers. Build-only changes here can alter the driver's symbol availability and runtime feature set.

## Test Signals
Primary signals are successful `make drivers/video/fbdev/via/` or kernel builds with `CONFIG_FB_VIA=y/m`, absence of unresolved symbols, and a resulting `viafb.o` containing expected helper symbols such as `viafb_setmode`, `viafb_dvi_enable`, and `viafb_setup_engine`.
