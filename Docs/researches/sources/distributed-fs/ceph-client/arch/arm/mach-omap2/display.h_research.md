<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/display.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/display.h

## Purpose
`display.h` is the small OMAP2+ display integration header. It shares DISPC device-attribute data and legacy helper registration prototypes between display, framebuffer, and platform-device setup code.

## Important APIs, Types, and Functions
It defines `struct omap_dss_dispc_dev_attr` with `manager_count` and `has_framedonetv_irq`. It declares `omap_init_vrfb()`, `omap_init_fb()`, and `omap_init_vout()`.

## Control Flow
The header has no runtime control flow. It enables compile-time sharing of display helper APIs and the DISPC reset attribute shape used by `display.c`.

## State and Persistence Behavior
No state is stored here. The struct fields describe hardware capability state supplied by hwmod data at runtime.

## Dependencies and Integration Points
It includes `linux/kernel.h` for `bool`/integer types and is consumed by `display.c`, `fb.c`, and `devices.c`.

## Risks
Changing the struct layout breaks assumptions in hwmod `dev_attr` users. Removing prototypes without updating config stubs can break display initialization for legacy framebuffer/VOUT paths.

## Test Signals
Compile display-enabled and display-disabled OMAP builds. Runtime signals are successful `omapdss` initialization, VRFB/fb/VOUT helper registration, and `dispc_disable_outputs()` reading correct manager attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/display.h -->
