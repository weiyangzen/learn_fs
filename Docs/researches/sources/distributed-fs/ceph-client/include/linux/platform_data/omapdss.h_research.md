# sources/distributed-fs/ceph-client/include/linux/platform_data/omapdss.h

## Purpose
`omapdss.h` is a Linux kernel TI OMAP platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct omap_dss_board_info`; enumerations such as `enum omapdss_version` into the matching driver
at probe time.

## Important APIs, types, and functions
Macros/constants: `__OMAPDSS_PDATA_H`. Types: `struct omap_dss_board_info`, `enum omapdss_version`.
Declared or inline functions: `int`, `void`. Important struct details: struct omap_dss_board_info
fields include `int (*dsi_enable_pads)(int dsi_id, unsigned int lane_mask)`, `void
(*dsi_disable_pads)(int dsi_id, unsigned int lane_mask)`, `int (*set_min_bus_tput)(struct device
*dev, unsigned long r)`, `enum omapdss_version version`. Important enum details: enum
omapdss_version values include `OMAPDSS_VER_UNKNOWN`, `OMAPDSS_VER_OMAP24xx`,
`OMAPDSS_VER_OMAP34xx_ES1`, `OMAPDSS_VER_OMAP34xx_ES3`, `OMAPDSS_VER_OMAP3630`,
`OMAPDSS_VER_AM35xx`, `OMAPDSS_VER_OMAP4430_ES1`, `OMAPDSS_VER_OMAP4430_ES2`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/include/video/omapfb_dss.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/display.c`, `sources/distributed-fs/ceph-client/include/sound/omap-hdmi-audio.h`,
`sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/omapdss.h`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/include/video/omapfb_dss.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/display.c`, `sources/distributed-fs/ceph-client/include/sound/omap-hdmi-audio.h`,
`sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/omapdss.h`. It integrates through
`struct platform_device` platform data, board files, MFD child registration, and legacy non-DT setup
paths; many modern systems may replace parts of this contract with Device Tree, ACPI, or software-
node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/omapdss.h` completely for this pass (32 lines, 897 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/omapdss.h_research.md`.
