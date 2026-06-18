# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/Makefile

## Purpose

`dss/Makefile` maps the OMAP DSS Kconfig symbols to built objects. The complete 18-line file was read. It builds the boot init object, the main `omapdss.o` composite module/object, core DSS files, compatibility-layer files, and optional output-specific files.

## Important APIs, Types, and Functions

The important build variables are `obj-$(CONFIG_FB_OMAP2_DSS_INIT)`, `obj-$(CONFIG_FB_OMAP2_DSS)`, `omapdss-y`, and option-specific `omapdss-$(CONFIG_...)` additions. Core entries include `core.o`, `dss.o`, `dss_features.o`, `dispc.o`, `dispc_coefs.o`, `display.o`, `output.o`, `dss-of.o`, `pll.o`, and `video-pll.o`. Compatibility entries include `manager.o`, `manager-sysfs.o`, `overlay.o`, `overlay-sysfs.o`, `apply.o`, `dispc-compat.o`, and `display-sysfs.o`.

## Control Flow

This file controls link composition rather than runtime execution. The order places core DSS and DISPC support before compatibility wrappers and then optional interface drivers. `ccflags-$(CONFIG_FB_OMAP2_DSS_DEBUG) += -DDEBUG` controls debug logging compilation.

## State and Persistence Behavior

There is no runtime state. Build outputs persist in the kernel build tree according to configuration.

## Dependencies and Integration Points

It consumes symbols from `dss/Kconfig` and integrates the core DSS component, overlay/manager compatibility APIs, and output drivers into one `omapdss` unit. Conditional HDMI common and HDMI4/HDMI5 object groups mirror the Kconfig split.

## Risks and Edge Cases

Because many files cross-call initialization functions, removing or reordering objects can expose unresolved symbols. Optional output drivers must match the init/uninit arrays in `core.c`. Debug flag behavior changes logging volume and may expose timing-sensitive messages.

## Test Signals

Signals include configured builds for each output subset, module and built-in builds of `FB_OMAP2_DSS`, compile checks with `FB_OMAP2_DSS_DEBUG`, and symbol/link validation for HDMI_COMMON without the wrong HDMI generation files.
