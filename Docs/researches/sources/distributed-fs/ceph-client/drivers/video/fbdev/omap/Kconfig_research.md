# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/Kconfig

## Purpose

`omap/Kconfig` defines configuration symbols for the OMAP1 fbdev driver and optional external LCD controller features. The source was read as a complete 49-line file.

## Important APIs, Types, and Functions

Configuration symbols are `FB_OMAP`, `FB_OMAP_LCDC_EXTERNAL`, `FB_OMAP_LCDC_HWA742`, `FB_OMAP_MANUAL_UPDATE`, `FB_OMAP_LCD_MIPID`, and `FB_OMAP_DMA_TUNE`. `FB_OMAP` is tristate, depends on `FB` and `ARCH_OMAP1 || (ARM && COMPILE_TEST)`, and selects `FB_IOMEM_HELPERS`.

## Control Flow

There is no runtime flow. Kconfig exposes menu choices and dependency constraints that control which source files the OMAP Makefile builds and which code paths are compiled.

## State and Persistence Behavior

The file owns build-time configuration state only. Selected symbols persist in the kernel `.config` and determine compiled driver capabilities.

## Dependencies and Integration Points

It integrates with the fbdev Kconfig tree, OMAP1 architecture support, ARM compile testing, SPI master support for MIPI DBI/DCS panels, and the OMAP Makefile object selections. `FB_OMAP_MANUAL_UPDATE` and `FB_OMAP_DMA_TUNE` influence behavior in the implementation files even though they are not built independently here.

## Risks and Edge Cases

Dependency mistakes can expose OMAP-only code to unsupported architectures or hide useful compile-test coverage. `FB_OMAP_LCDC_HWA742` depends on both base OMAP fbdev and external controller support; breaking that relationship would create missing symbols or invalid UI choices. Help text describes board and userspace expectations that should stay aligned with implementation behavior.

## Test Signals

Run Kconfig/build matrix checks for `FB_OMAP=m/y`, ARM compile-test, external LCD support, HWA742, MIPI DBI with and without `SPI_MASTER`, manual update, and DMA tuning. Verify the resulting object lists match Makefile expectations.
