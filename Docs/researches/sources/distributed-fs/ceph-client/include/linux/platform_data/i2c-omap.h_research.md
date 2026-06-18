# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-omap.h

## Purpose
`i2c-omap.h` is a Linux kernel I2C controller or adapter board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct omap_i2c_bus_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__I2C_OMAP_H__`, `OMAP_I2C_IP_VERSION_1`, `OMAP_I2C_IP_VERSION_2`,
`OMAP_I2C_FLAG_NO_FIFO`, `OMAP_I2C_FLAG_SIMPLE_CLOCK`, `OMAP_I2C_FLAG_16BIT_DATA_REG`,
`OMAP_I2C_FLAG_ALWAYS_ARMXOR_CLK`, `OMAP_I2C_FLAG_FORCE_19200_INT_CLK`,
`OMAP_I2C_FLAG_BUS_SHIFT_NONE`, `OMAP_I2C_FLAG_BUS_SHIFT_1`, `OMAP_I2C_FLAG_BUS_SHIFT_2`,
`OMAP_I2C_FLAG_BUS_SHIFT__SHIFT`. Types: `struct omap_i2c_bus_platform_data`. Declared or inline
functions: `void`. Important struct details: struct omap_i2c_bus_platform_data fields include `u32
clkrate`, `u32 rev`, `u32 flags`, `void (*set_mpu_wkup_lat)(struct device *dev, long set)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/i2c.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap1/common.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_2430_data.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_2420_data.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/platform_device.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-omap1/i2c.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/common.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/omap_hwmod_2430_data.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/omap_hwmod_2420_data.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common.h`,
`sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_3xxx_data.c`,
`sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-omap.c`. It integrates through `struct
platform_device` platform data, board files, MFD child registration, and legacy non-DT setup paths;
many modern systems may replace parts of this contract with Device Tree, ACPI, or software-node
properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-omap.h` completely for this pass (39 lines, 1241 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-omap.h_research.md`.
