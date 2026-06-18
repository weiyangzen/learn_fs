# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/Makefile

## Purpose

`omap/Makefile` defines the Kbuild object composition for the OMAP1 framebuffer driver, including base driver objects, external controller support, board LCD panel files, and MIPI DBI panel support. The source was read as a complete 26-line file.

## Important APIs, Types, and Functions

The key variables are `obj-$(CONFIG_FB_OMAP)`, `obj-y`, `objs-yy`, `objs-y$(CONFIG_FB_OMAP_LCDC_EXTERNAL)`, `objs-y$(CONFIG_FB_OMAP_LCDC_HWA742)`, `lcds-y$(CONFIG_MACH_AMS_DELTA)`, `lcds-y$(CONFIG_MACH_OMAP_PALMTE)`, `lcds-y$(CONFIG_FB_OMAP_LCD_MIPID)`, and `omapfb-objs`. Base `omapfb` objects are `omapfb_main.o` and `lcdc.o`; optional objects include `sossi.o`, `hwa742.o`, `lcd_ams_delta.o`, `lcd_palmte.o`, and `lcd_mipid.o`. `lcd_dma.o` is forced built-in when `CONFIG_FB_OMAP` is set.

## Control Flow

There is no runtime flow. Kbuild evaluates configuration symbols, links selected base objects into `omapfb.o`, builds `lcd_dma.o` built-in for base support, and includes board/panel LCD objects according to machine and panel configuration.

## State and Persistence Behavior

The file owns build-time object-selection state only. Runtime state is in the compiled driver objects.

## Dependencies and Integration Points

It integrates with `omap/Kconfig` symbols and machine symbols such as `CONFIG_MACH_AMS_DELTA` and `CONFIG_MACH_OMAP_PALMTE`. The explicit `obj-y += lcd_dma.o` comment notes that DMA support must be built-in when OMAP fbdev is enabled, which may matter for initialization ordering or exported helper availability.

## Risks and Edge Cases

The `objs-y$(CONFIG_...)` pattern relies on Kbuild variable expansion producing `objs-yy` for enabled booleans; typos would silently omit objects. If `FB_OMAP=m`, the forced `lcd_dma.o` built-in object can create built-in/module coupling that must be intentional and link-safe. Board LCD objects are added as standalone objects, not part of `omapfb-objs`, so initialization ordering and symbol visibility should be checked when moving code.

## Test Signals

Build with `CONFIG_FB_OMAP=y` and `m`, with external LCD/HWA742 enabled, with AMS Delta and PalmTE machine configs, and with MIPI DBI support. Confirm `omapfb.o` includes expected base/optional controller objects and that board LCD objects link without unresolved symbols.
