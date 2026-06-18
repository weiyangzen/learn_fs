# sources/distributed-fs/ceph-client/include/linux/platform_data/media/mmp-camera.h

## Purpose
`mmp-camera.h` is a Linux kernel media/camera/radio board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct mmp_camera_platform_data`; enumerations such as `enum dphy3_algo` into the matching driver
at probe time.

## Important APIs, types, and functions
Macros/constants: none visible in this header. Types: `struct mmp_camera_platform_data`, `enum
dphy3_algo`. Declared or inline functions: none visible in this header. Important struct details:
struct mmp_camera_platform_data fields include `enum v4l2_mbus_type bus_type`, `int mclk_src`, `int
mclk_div`, `int dphy[3]`, `enum dphy3_algo dphy3_algo`, `int lane`, `int lane_clk`. Important enum
details: enum dphy3_algo values include `DPHY3_ALGO_DEFAULT`, `DPHY3_ALGO_PXA910`,
`DPHY3_ALGO_PXA2128`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/media/platform/marvell/mmp-driver.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `media/v4l2-mediabus.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mmp-driver.c`. It integrates
through `struct platform_device` platform data, board files, MFD child registration, and legacy non-
DT setup paths; many modern systems may replace parts of this contract with Device Tree, ACPI, or
software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/media/mmp-camera.h` completely for this pass (25 lines, 624 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/media/mmp-camera.h_research.md`.
