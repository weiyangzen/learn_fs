# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/Makefile

## Purpose
This Makefile wires ATI fbdev drivers into the kernel build. It selects object composition for Mach64 `atyfb`, Rage128 `aty128fb`, and Radeon `radeonfb` based on Kconfig symbols.

## Important APIs, types, and functions
The key build variables are `obj-$(CONFIG_FB_ATY)`, `obj-$(CONFIG_FB_ATY128)`, and `obj-$(CONFIG_FB_RADEON)`. Composite object lists are `atyfb-y`, `atyfb-$(CONFIG_FB_ATY_GX)`, `atyfb-$(CONFIG_FB_ATY_CT)`, `atyfb-objs`, `radeonfb-y`, `radeonfb-$(CONFIG_FB_RADEON_I2C)`, `radeonfb-$(CONFIG_FB_RADEON_BACKLIGHT)`, and `radeonfb-objs`.

## Control flow
Kbuild evaluates config symbols and builds `atyfb.o`, `aty128fb.o`, and/or `radeonfb.o`. `atyfb.o` is composed from `atyfb_base.o`, acceleration/cursor objects, and optional Mach64 GX/CT support. `radeonfb.o` is composed from base, power-management, monitor, acceleration, optional I2C, and optional backlight objects. `aty128fb.o` is a single translation unit from `aty128fb.c`.

## State and persistence behavior
The file has no runtime state. Its persistent effect is build graph shape and which objects enter the kernel or module.

## Dependencies and integration points
It integrates with Kbuild and the Kconfig symbols for ATI, Rage128, Radeon, Radeon I2C, and Radeon backlight support. Source file names here must match actual objects in the `aty` directory.

## Risks and edge cases
Incorrect object composition would produce unresolved symbols or omit optional hardware support. Because `atyfb-y` is later assigned to `atyfb-objs`, any future additions must be made before that assignment or use the correct Kbuild pattern.

## Test signals
Build `CONFIG_FB_ATY`, `CONFIG_FB_ATY_GX`, `CONFIG_FB_ATY_CT`, `CONFIG_FB_ATY128`, `CONFIG_FB_RADEON`, `CONFIG_FB_RADEON_I2C`, and `CONFIG_FB_RADEON_BACKLIGHT` combinations as built-in and module where supported.
