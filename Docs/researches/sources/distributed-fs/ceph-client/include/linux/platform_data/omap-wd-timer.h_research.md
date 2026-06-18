# sources/distributed-fs/ceph-client/include/linux/platform_data/omap-wd-timer.h

## Purpose
`omap-wd-timer.h` is a Linux kernel TI OMAP platform integration data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct omap_wd_timer_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_PLATFORM_DATA_OMAP_WD_TIMER_H`, `OMAP_MPU_WD_RST_SRC_ID_SHIFT`. Types:
`struct omap_wd_timer_platform_data`. Declared or inline functions: `u32`. Important struct details:
struct omap_wd_timer_platform_data fields include `u32 (*read_reset_sources)(void)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/devices.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/wd_timer.c`, `sources/distributed-fs/ceph-client/drivers/watchdog/omap_wdt.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-omap1/devices.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/wd_timer.c`, `sources/distributed-fs/ceph-
client/drivers/watchdog/omap_wdt.c`. It integrates through `struct platform_device` platform data,
board files, MFD child registration, and legacy non-DT setup paths; many modern systems may replace
parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/omap-wd-timer.h` completely for this pass (34 lines, 901 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/omap-wd-timer.h_research.md`.
