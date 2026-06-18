# subset-b-005906 grouped research

Grouped research for Linux platform-data, platform-device, firmware-update, priority-list, and power-management headers in the ceph-client kernel tree. Each source file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-omap.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-pca-platform.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-pca-platform.h

## Purpose
`i2c-pca-platform.h` is a Linux kernel I2C controller or adapter board-data header. It gives board
files, MFD children, ACPI glue, or platform-device setup code a compact contract for passing the
primary type `struct i2c_pca9564_pf_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `I2C_PCA9564_PLATFORM_H`. Types: `struct i2c_pca9564_pf_platform_data`. Declared
or inline functions: none visible in this header. Important struct details: struct
i2c_pca9564_pf_platform_data fields include `int i2c_clock_speed`, `int timeout`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/i2c/busses/i2c-pca-platform.c`, `sources/distributed-fs/ceph-
client/arch/sh/boards/board-sh7785lcr.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/i2c/busses/i2c-pca-platform.c`, `sources/distributed-fs/ceph-
client/arch/sh/boards/board-sh7785lcr.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-pca-platform.h` completely for this pass (10 lines, 291 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-pca-platform.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-pca-platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-pxa.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-pxa.h

## Purpose
`i2c-pxa.h` is a Linux kernel I2C controller or adapter board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct i2c_pxa_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_I2C_PXA_H_`. Types: `struct i2c_pxa_platform_data`. Declared or inline
functions: none visible in this header. Important struct details: struct i2c_pxa_platform_data
fields include `unsigned int class`, `unsigned int use_pio :1`, `unsigned int fast_mode :1`,
`unsigned int high_mode:1`, `unsigned char master_code`, `unsigned long rate`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/pxa3xx.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/spitz.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/pxa3xx.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/spitz.c`, `sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pxa-
pci.c`, `sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pxa.c`. It integrates through
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-pxa.h` completely for this pass (18 lines, 354 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-pxa.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-pxa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-s3c2410.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-s3c2410.h

## Purpose
`i2c-s3c2410.h` is a Linux kernel I2C controller or adapter board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct s3c2410_platform_i2c` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__I2C_S3C2410_H`, `S3C_IICFLG_FILTER`. Types: `struct s3c2410_platform_i2c`.
Declared or inline functions: `void`, `s3c_i2c0_set_platdata`, `s3c_i2c1_set_platdata`,
`s3c_i2c2_set_platdata`, `s3c_i2c3_set_platdata`, `s3c_i2c4_set_platdata`, `s3c_i2c5_set_platdata`,
`s3c_i2c6_set_platdata`, `s3c_i2c7_set_platdata`, `s5p_i2c_hdmiphy_set_platdata`,
`s3c_i2c0_cfg_gpio`, `s3c_i2c1_cfg_gpio`, `s3c_i2c2_cfg_gpio`, `s3c_i2c3_cfg_gpio`,
`s3c_i2c4_cfg_gpio`, `s3c_i2c5_cfg_gpio`, `s3c_i2c6_cfg_gpio`, `s3c_i2c7_cfg_gpio`. Important struct
details: struct s3c2410_platform_i2c fields include `int bus_num`, `unsigned int flags`, `unsigned
int slave_addr`, `unsigned long frequency`, `unsigned int sda_delay`, `void (*cfg_gpio)(struct
platform_device *dev)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/devs.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-
crag6410.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c0-s3c64xx.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c1-s3c64xx.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/devs.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-
crag6410.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c0-s3c64xx.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-i2c1-s3c64xx.c`, `sources/distributed-
fs/ceph-client/drivers/i2c/busses/i2c-s3c2410.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-s3c2410.h` completely for this pass (75 lines, 2929 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-s3c2410.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-s3c2410.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-xiic.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-xiic.h

## Purpose
`i2c-xiic.h` is a Linux kernel I2C controller or adapter board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct xiic_i2c_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_LINUX_I2C_XIIC_H`. Types: `struct xiic_i2c_platform_data`. Declared or inline
functions: none visible in this header. Important struct details: struct xiic_i2c_platform_data
fields include `u8 num_devices`, `struct i2c_board_info const *devices`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mfd/timberdale.c`, `sources/distributed-fs/ceph-client/drivers/ptp/ptp_ocp.c`,
`sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xiic.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/mfd/timberdale.c`, `sources/distributed-fs/ceph-client/drivers/ptp/ptp_ocp.c`,
`sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xiic.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-xiic.h` completely for this pass (31 lines, 853 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-xiic.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-xiic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/invensense_mpu6050.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/invensense_mpu6050.h

## Purpose
`invensense_mpu6050.h` is a Linux kernel legacy board/platform-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct inv_mpu6050_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__INV_MPU6050_PLATFORM_H_`. Types: `struct inv_mpu6050_platform_data`. Declared
or inline functions: none visible in this header. Important struct details: struct
inv_mpu6050_platform_data fields include `__s8 orientation[9]`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/iio/imu/inv_mpu6050/inv_mpu_iio.h`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/iio/imu/inv_mpu6050/inv_mpu_iio.h`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/invensense_mpu6050.h` completely for this pass (26 lines, 865 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/invensense_mpu6050.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/invensense_mpu6050.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/iommu-omap.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/iommu-omap.h

## Purpose
`iommu-omap.h` is a Linux kernel IOMMU platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
iommu_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: none visible in this header. Types: `struct iommu_platform_data`. Declared or
inline functions: `int`. Important struct details: struct iommu_platform_data fields include `const
char *reset_name`, `int (*assert_reset)(struct platform_device *pdev, const char *name)`, `int
(*deassert_reset)(struct platform_device *pdev, const char *name)`, `int (*device_enable)(struct
platform_device *pdev)`, `int (*device_idle)(struct platform_device *pdev)`, `u8 *pwrst)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/iommu/omap-iommu-debug.c`, `sources/distributed-fs/ceph-client/drivers/iommu/omap-
iommu.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pdata-quirks.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/platform_device.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/iommu/omap-iommu-debug.c`, `sources/distributed-fs/ceph-
client/drivers/iommu/omap-iommu.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pdata-
quirks.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/iommu-omap.h` completely for this pass (20 lines, 618 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/iommu-omap.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/iommu-omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/isl9305.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/isl9305.h

## Purpose
`isl9305.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
isl9305_pdata` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__ISL9305_H`, `ISL9305_DCD1`, `ISL9305_DCD2`, `ISL9305_LDO1`, `ISL9305_LDO2`,
`ISL9305_MAX_REGULATOR`. Types: `struct isl9305_pdata`. Declared or inline functions: none visible
in this header. Important struct details: struct isl9305_pdata fields include `struct
regulator_init_data *init_data[ISL9305_MAX_REGULATOR + 1]`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/regulator/isl9305.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/regulator/isl9305.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/isl9305.h` completely for this pass (26 lines, 487 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/isl9305.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/isl9305.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/itco_wdt.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/itco_wdt.h

## Purpose
`itco_wdt.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct itco_wdt_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_ITCO_WDT_H_`, `ICH_RES_IO_TCO`, `ICH_RES_IO_SMI`, `ICH_RES_MEM_OFF`,
`ICH_RES_MEM_GCS_PMC`. Types: `struct itco_wdt_platform_data`. Declared or inline functions: none
visible in this header. Important struct details: struct itco_wdt_platform_data fields include `char
name[32]`, `unsigned int version`, `bool no_reboot_use_pmc`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mfd/lpc_ich.c`, `sources/distributed-fs/ceph-client/drivers/mfd/intel_pmc_bxt.c`,
`sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-i801.c`, `sources/distributed-fs/ceph-
client/drivers/watchdog/iTCO_wdt.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/mfd/lpc_ich.c`, `sources/distributed-fs/ceph-client/drivers/mfd/intel_pmc_bxt.c`,
`sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-i801.c`, `sources/distributed-fs/ceph-
client/drivers/watchdog/iTCO_wdt.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/itco_wdt.h` completely for this pass (27 lines, 588 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/itco_wdt.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/itco_wdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/keypad-omap.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/keypad-omap.h

## Purpose
`keypad-omap.h` is a Linux kernel TI OMAP platform integration data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct omap_kp_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__KEYPAD_OMAP_H`, `omap_readw`, `omap_writew`, `GROUP_SHIFT`, `GROUP_0`,
`GROUP_1`, `GROUP_2`, `GROUP_3`, `GROUP_MASK`. Types: `struct omap_kp_platform_data`. Declared or
inline functions: none visible in this header. Important struct details: struct
omap_kp_platform_data fields include `int rows`, `int cols`, `const struct matrix_keymap_data
*keymap_data`, `bool rep`, `unsigned long delay`, `bool dbounce`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/board-sx1.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap1/board-nokia770.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-palmte.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/input/matrix_keypad.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-sx1.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/board-nokia770.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap1/board-palmte.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-ams-delta.c`,
`sources/distributed-fs/ceph-client/drivers/input/keyboard/omap-keypad.c`. It integrates through
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/keypad-omap.h` completely for this pass (44 lines, 1253 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/keypad-omap.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/keypad-omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lcd-mipid.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/lcd-mipid.h

## Purpose
`lcd-mipid.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct mipid_platform_data`; enumerations such as `enum mipid_test_num`, `enum mipid_test_result`
into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LCD_MIPID_H`. Types: `struct mipid_platform_data`, `enum mipid_test_num`, `enum
mipid_test_result`. Declared or inline functions: `int`. Important struct details: struct
mipid_platform_data fields include `int data_lines`, `int level)`, `int (*get_bklight_level)(struct
mipid_platform_data *pdata)`, `int (*get_bklight_max)(struct mipid_platform_data *pdata)`. Important
enum details: enum mipid_test_num values include `MIPID_TEST_RGB_LINES`; enum mipid_test_result
values include `MIPID_TEST_SUCCESS`, `MIPID_TEST_INVALID`, `MIPID_TEST_FAILED`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/board-nokia770.c`, `sources/distributed-fs/ceph-
client/drivers/video/fbdev/omap/lcd_mipid.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/board-nokia770.c`, `sources/distributed-fs/ceph-
client/drivers/video/fbdev/omap/lcd_mipid.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/lcd-mipid.h` completely for this pass (28 lines, 514 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/lcd-mipid.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lcd-mipid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm355x.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm355x.h

## Purpose
`leds-lm355x.h` is a Linux kernel LED/flash/backlight board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct lm355x_platform_data`; enumerations such as `enum lm355x_strobe`, `enum lm355x_torch` into
the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `LM355x_NAME`, `LM3554_NAME`, `LM3556_NAME`. Types: `struct lm355x_platform_data`,
`enum lm355x_strobe`, `enum lm355x_torch`, `enum lm355x_tx2`, `enum lm355x_ntc`, `enum
lm355x_pmode`. Declared or inline functions: none visible in this header. Important struct details:
struct lm355x_platform_data fields include `enum lm355x_strobe pin_strobe`, `enum lm355x_torch
pin_tx1`, `enum lm355x_tx2 pin_tx2`, `enum lm355x_ntc ntc_pin`, `enum lm355x_pmode pass_mode`.
Important enum details: enum lm355x_strobe values include `LM355x_PIN_STROBE_DISABLE`,
`LM355x_PIN_STROBE_ENABLE`; enum lm355x_torch values include `LM355x_PIN_TORCH_DISABLE`,
`LM3554_PIN_TORCH_ENABLE`, `LM3556_PIN_TORCH_ENABLE`; enum lm355x_tx2 values include
`LM355x_PIN_TX_DISABLE`, `LM3554_PIN_TX_ENABLE`, `LM3556_PIN_TX_ENABLE`; enum lm355x_ntc values
include `LM355x_PIN_NTC_DISABLE`, `LM3554_PIN_NTC_ENABLE`, `LM3556_PIN_NTC_ENABLE`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/leds/leds-lm355x.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/leds/leds-lm355x.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm355x.h` completely for this pass (65 lines, 1454 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm355x.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm355x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm3642.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm3642.h

## Purpose
`leds-lm3642.h` is a Linux kernel LED/flash/backlight board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct lm3642_platform_data`; enumerations such as `enum lm3642_torch_pin_enable`, `enum
lm3642_strobe_pin_enable` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_LM3642_H`, `LM3642_NAME`. Types: `struct lm3642_platform_data`, `enum
lm3642_torch_pin_enable`, `enum lm3642_strobe_pin_enable`, `enum lm3642_tx_pin_enable`. Declared or
inline functions: none visible in this header. Important struct details: struct lm3642_platform_data
fields include `enum lm3642_torch_pin_enable torch_pin`, `enum lm3642_strobe_pin_enable strobe_pin`,
`enum lm3642_tx_pin_enable tx_pin`. Important enum details: enum lm3642_torch_pin_enable values
include `LM3642_TORCH_PIN_DISABLE`, `LM3642_TORCH_PIN_ENABLE`; enum lm3642_strobe_pin_enable values
include `LM3642_STROBE_PIN_DISABLE`, `LM3642_STROBE_PIN_ENABLE`; enum lm3642_tx_pin_enable values
include `LM3642_TX_PIN_DISABLE`, `LM3642_TX_PIN_ENABLE`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/leds/leds-lm3642.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/leds/leds-lm3642.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm3642.h` completely for this pass (37 lines, 818 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm3642.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lm3642.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lp55xx.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lp55xx.h

## Purpose
`leds-lp55xx.h` is a Linux kernel LED/flash/backlight board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct lp55xx_led_config`; enumerations such as `enum lp8501_pwr_sel` into the matching driver at
probe time.

## Important APIs, types, and functions
Macros/constants: `_LEDS_LP55XX_H`, `LP55XX_CLOCK_AUTO`, `LP55XX_CLOCK_INT`, `LP55XX_CLOCK_EXT`,
`LP55XX_MAX_GROUPED_CHAN`. Types: `struct lp55xx_led_config`, `struct lp55xx_predef_pattern`,
`struct lp55xx_platform_data`, `enum lp8501_pwr_sel`. Declared or inline functions: none visible in
this header. Important struct details: struct lp55xx_led_config fields include `const char *name`,
`const char *default_trigger`, `u8 chan_nr`, `u8 led_current`, `u8 max_current`, `int num_colors`,
`unsigned int max_channel`, `int color_id[LED_COLOR_ID_MAX]`; struct lp55xx_predef_pattern fields
include `const u8 *r`, `const u8 *g`, `const u8 *b`, `u8 size_r`, `u8 size_g`, `u8 size_b`; struct
lp55xx_platform_data fields include `struct lp55xx_led_config *led_config`, `u8 num_channels`,
`const char *label`, `u8 clock_mode`, `u32 charge_pump_mode`, `struct gpio_desc *enable_gpiod`,
`struct lp55xx_predef_pattern *patterns`, `unsigned int num_patterns`. Important enum details: enum
lp8501_pwr_sel values include `LP8501_ALL_VDD`, `LP8501_6VDD_3VOUT`, `LP8501_3VDD_6VOUT`,
`LP8501_ALL_VOUT`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/leds/leds-lp5523.c`, `sources/distributed-fs/ceph-client/drivers/leds/leds-lp5569.c`,
`sources/distributed-fs/ceph-client/drivers/leds/leds-lp55xx-common.c`, `sources/distributed-
fs/ceph-client/drivers/leds/leds-lp5562.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/gpio/consumer.h`, `linux/led-class-multicolor.h`. Direct source-tree consumers
found by include search are `sources/distributed-fs/ceph-client/drivers/leds/leds-lp5523.c`,
`sources/distributed-fs/ceph-client/drivers/leds/leds-lp5569.c`, `sources/distributed-fs/ceph-
client/drivers/leds/leds-lp55xx-common.c`, `sources/distributed-fs/ceph-client/drivers/leds/leds-
lp5562.c`, `sources/distributed-fs/ceph-client/drivers/leds/leds-lp5521.c`, `sources/distributed-
fs/ceph-client/drivers/leds/leds-lp8501.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lp55xx.h` completely for this pass (90 lines, 2219 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lp55xx.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/leds-lp55xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lenovo-yoga-c630.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/lenovo-yoga-c630.h

## Purpose
`lenovo-yoga-c630.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing macros, constants,
or function prototypes into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_LENOVO_YOGA_C630_DATA_H`, `YOGA_C630_MOD_NAME`, `YOGA_C630_DEV_UCSI`,
`YOGA_C630_DEV_PSY`, `YOGA_C630_UCSI_WRITE_SIZE`, `YOGA_C630_UCSI_CCI_SIZE`,
`YOGA_C630_UCSI_DATA_SIZE`, `YOGA_C630_UCSI_READ_SIZE`, `LENOVO_EC_EVENT_USB`,
`LENOVO_EC_EVENT_UCSI`, `LENOVO_EC_EVENT_HPD`, `LENOVO_EC_EVENT_BAT_STATUS`,
`LENOVO_EC_EVENT_BAT_INFO`, `LENOVO_EC_EVENT_BAT_ADPT_STATUS`. Types: none visible in this header.
Declared or inline functions: `yoga_c630_ec_read8`, `yoga_c630_ec_read16`,
`yoga_c630_ec_register_notify`, `yoga_c630_ec_unregister_notify`, `yoga_c630_ec_ucsi_get_version`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/power/supply/lenovo_yoga_c630_battery.c`, `sources/distributed-fs/ceph-
client/drivers/platform/arm64/lenovo-yoga-c630.c`, `sources/distributed-fs/ceph-
client/drivers/usb/typec/ucsi/ucsi_yoga_c630.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/power/supply/lenovo_yoga_c630_battery.c`, `sources/distributed-fs/ceph-
client/drivers/platform/arm64/lenovo-yoga-c630.c`, `sources/distributed-fs/ceph-
client/drivers/usb/typec/ucsi/ucsi_yoga_c630.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/lenovo-yoga-c630.h` completely for this pass (44 lines, 1350 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/lenovo-yoga-c630.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lenovo-yoga-c630.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lm3630a_bl.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/lm3630a_bl.h

## Purpose
`lm3630a_bl.h` is a Linux kernel backlight controller board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct lm3630a_platform_data`; enumerations such as `enum lm3630a_pwm_ctrl`, `enum
lm3630a_leda_ctrl` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_LM3630A_H`, `LM3630A_NAME`, `LM3630A_MAX_BRIGHTNESS`. Types: `struct
lm3630a_platform_data`, `enum lm3630a_pwm_ctrl`, `enum lm3630a_leda_ctrl`, `enum lm3630a_ledb_ctrl`.
Declared or inline functions: none visible in this header. Important struct details: struct
lm3630a_platform_data fields include `const char *leda_label`, `int leda_init_brt`, `int
leda_max_brt`, `enum lm3630a_leda_ctrl leda_ctrl`, `const char *ledb_label`, `int ledb_init_brt`,
`int ledb_max_brt`, `enum lm3630a_ledb_ctrl ledb_ctrl`. Important enum details: enum
lm3630a_pwm_ctrl values include `LM3630A_PWM_DISABLE`, `LM3630A_PWM_BANK_A`, `LM3630A_PWM_BANK_B`,
`LM3630A_PWM_BANK_ALL`, `LM3630A_PWM_BANK_A_ACT_LOW`, `LM3630A_PWM_BANK_B_ACT_LOW`,
`LM3630A_PWM_BANK_ALL_ACT_LOW`; enum lm3630a_leda_ctrl values include `LM3630A_LEDA_DISABLE`,
`LM3630A_LEDA_ENABLE`, `LM3630A_LEDA_ENABLE_LINEAR`; enum lm3630a_ledb_ctrl values include
`LM3630A_LEDB_DISABLE`, `LM3630A_LEDB_ON_A`, `LM3630A_LEDB_ENABLE`, `LM3630A_LEDB_ENABLE_LINEAR`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/video/backlight/lm3630a_bl.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/video/backlight/lm3630a_bl.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/lm3630a_bl.h` completely for this pass (65 lines, 1671 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/lm3630a_bl.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lm3630a_bl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lm3639_bl.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/lm3639_bl.h

## Purpose
`lm3639_bl.h` is a Linux kernel backlight controller board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct lm3639_platform_data`; enumerations such as `enum lm3639_pwm`, `enum lm3639_strobe` into the
matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_LM3639_H`, `LM3639_NAME`. Types: `struct lm3639_platform_data`, `enum
lm3639_pwm`, `enum lm3639_strobe`, `enum lm3639_txpin`, `enum lm3639_fleds`, `enum lm3639_bleds`,
`enum lm3639_bled_mode`. Declared or inline functions: `void`, `int`. Important struct details:
struct lm3639_platform_data fields include `unsigned int max_brt_led`, `unsigned int init_brt_led`,
`enum lm3639_pwm pin_pwm`, `enum lm3639_strobe pin_strobe`, `enum lm3639_txpin pin_tx`, `enum
lm3639_fleds fled_pins`, `enum lm3639_bleds bled_pins`, `enum lm3639_bled_mode bled_mode`. Important
enum details: enum lm3639_pwm values include `LM3639_PWM_DISABLE`, `LM3639_PWM_EN_ACTLOW`,
`LM3639_PWM_EN_ACTHIGH`; enum lm3639_strobe values include `LM3639_STROBE_DISABLE`,
`LM3639_STROBE_EN_ACTLOW`, `LM3639_STROBE_EN_ACTHIGH`; enum lm3639_txpin values include
`LM3639_TXPIN_DISABLE`, `LM3639_TXPIN_EN_ACTLOW`, `LM3639_TXPIN_EN_ACTHIGH`; enum lm3639_fleds
values include `LM3639_FLED_DIASBLE_ALL`, `LM3639_FLED_EN_1`, `LM3639_FLED_EN_2`,
`LM3639_FLED_EN_ALL`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/video/backlight/lm3639_bl.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/video/backlight/lm3639_bl.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/lm3639_bl.h` completely for this pass (65 lines, 1401 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/lm3639_bl.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lm3639_bl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lm8323.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/lm8323.h

## Purpose
`lm8323.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
lm8323_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_LM8323_H`, `LM8323_KEYMAP_SIZE`, `LM8323_NUM_PWMS`. Types: `struct
lm8323_platform_data`. Declared or inline functions: none visible in this header. Important struct
details: struct lm8323_platform_data fields include `int debounce_time`, `int active_time`, `int
size_x`, `int size_y`, `bool repeat`, `const unsigned short *keymap`, `const char
*pwm_names[LM8323_NUM_PWMS]`, `const char *name`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/input/keyboard/lm8323.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/input/keyboard/lm8323.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/lm8323.h` completely for this pass (34 lines, 746 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/lm8323.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lm8323.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lp855x.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/lp855x.h

## Purpose
`lp855x.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
lp855x_rom_data`; enumerations such as `enum lp855x_chip_id`, `enum lp8550_brighntess_source` into
the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_LP855X_H`, `BL_CTL_SHFT`, `BRT_MODE_SHFT`, `BRT_MODE_MASK`, `ENABLE_BL`,
`DISABLE_BL`, `I2C_CONFIG`, `PWM_CONFIG`, `LP8550_PWM_CONFIG`, `LP8550_I2C_CONFIG`,
`LP8551_PWM_CONFIG`, `LP8551_I2C_CONFIG`, `LP8552_PWM_CONFIG`, `LP8552_I2C_CONFIG`, and 23 more.
Types: `struct lp855x_rom_data`, `struct lp855x_platform_data`, `enum lp855x_chip_id`, `enum
lp8550_brighntess_source`, `enum lp8551_brighntess_source`, `enum lp8552_brighntess_source`, `enum
lp8553_brighntess_source`, `enum lp8555_brightness_source`, `enum lp8556_brightness_source`, `enum
lp8557_brightness_source`. Declared or inline functions: none visible in this header. Important
struct details: struct lp855x_rom_data fields include `u8 addr`, `u8 val`; struct
lp855x_platform_data fields include `const char *name`, `u8 device_control`, `u8
initial_brightness`, `unsigned int period_ns`, `int size_program`, `struct lp855x_rom_data
*rom_data`. Important enum details: enum lp855x_chip_id values include `LP8550`, `LP8551`, `LP8552`,
`LP8553`, `LP8555`, `LP8556`, `LP8557`; enum lp8550_brighntess_source values include
`LP8550_PWM_ONLY`, `LP8550_I2C_ONLY`; enum lp8551_brighntess_source values include
`LP8551_PWM_ONLY`, `LP8551_I2C_ONLY`; enum lp8552_brighntess_source values include
`LP8552_PWM_ONLY`, `LP8552_I2C_ONLY`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/x86-android-tablets/lenovo.c`, `sources/distributed-fs/ceph-
client/drivers/video/backlight/lp855x_bl.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/platform/x86/x86-android-tablets/lenovo.c`, `sources/distributed-fs/ceph-
client/drivers/video/backlight/lp855x_bl.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/lp855x.h` completely for this pass (145 lines, 4055 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/lp855x.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lp855x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lp8727.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/lp8727.h

## Purpose
`lp8727.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
lp8727_chg_param`; enumerations such as `enum lp8727_eoc_level`, `enum lp8727_ichg` into the
matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_LP8727_H`. Types: `struct lp8727_chg_param`, `struct lp8727_platform_data`,
`enum lp8727_eoc_level`, `enum lp8727_ichg`. Declared or inline functions: `u8`, `u16`. Important
struct details: struct lp8727_chg_param fields include `enum lp8727_eoc_level eoc_level`, `enum
lp8727_ichg ichg`; struct lp8727_platform_data fields include `u8 (*get_batt_present)(void)`, `u16
(*get_batt_level)(void)`, `u8 (*get_batt_capacity)(void)`, `u8 (*get_batt_temp)(void)`, `struct
lp8727_chg_param *ac`, `struct lp8727_chg_param *usb`, `unsigned int debounce_msec`. Important enum
details: enum lp8727_eoc_level values include `LP8727_EOC_5P`, `LP8727_EOC_10P`, `LP8727_EOC_16P`,
`LP8727_EOC_20P`, `LP8727_EOC_25P`, `LP8727_EOC_33P`, `LP8727_EOC_50P`; enum lp8727_ichg values
include `LP8727_ICHG_90mA`, `LP8727_ICHG_100mA`, `LP8727_ICHG_400mA`, `LP8727_ICHG_450mA`,
`LP8727_ICHG_500mA`, `LP8727_ICHG_600mA`, `LP8727_ICHG_700mA`, `LP8727_ICHG_800mA`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/power/supply/lp8727_charger.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/power/supply/lp8727_charger.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/lp8727.h` completely for this pass (65 lines, 1477 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/lp8727.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lp8727.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lp8755.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/lp8755.h

## Purpose
`lp8755.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
lp8755_platform_data`; enumerations such as `enum lp8755_bucks`, `enum lp8755_mphase_config` into
the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_LP8755_H`, `LP8755_NAME`, `LP8755_EVENT_PWR_FAULT`, `LP8755_EVENT_OCP`,
`LP8755_EVENT_OVP`, `LP8755_EVENT_TEMP_WARN`, `LP8755_EVENT_TEMP_SHDN`, `LP8755_EVENT_I_LOAD`.
Types: `struct lp8755_platform_data`, `enum lp8755_bucks`, `enum lp8755_mphase_config`. Declared or
inline functions: none visible in this header. Important struct details: struct lp8755_platform_data
fields include `int mphase`, `struct regulator_init_data *buck_data[LP8755_BUCK_MAX]`. Important
enum details: enum lp8755_bucks values include `LP8755_BUCK0`, `LP8755_BUCK1`, `LP8755_BUCK2`,
`LP8755_BUCK3`, `LP8755_BUCK4`, `LP8755_BUCK5`, `LP8755_BUCK_MAX`; enum lp8755_mphase_config values
include `MPHASE_CONF0`, `MPHASE_CONF1`, `MPHASE_CONF2`, `MPHASE_CONF3`, `MPHASE_CONF4`,
`MPHASE_CONF5`, `MPHASE_CONF6`, `MPHASE_CONF7`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/regulator/lp8755.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/regulator/consumer.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/regulator/lp8755.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/lp8755.h` completely for this pass (67 lines, 1505 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/lp8755.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lp8755.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ltc4245.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/ltc4245.h

## Purpose
`ltc4245.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
ltc4245_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `LINUX_LTC4245_H`. Types: `struct ltc4245_platform_data`. Declared or inline
functions: none visible in this header. Important struct details: struct ltc4245_platform_data
fields include `bool use_extra_gpios`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/hwmon/ltc4245.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/hwmon/ltc4245.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/ltc4245.h` completely for this pass (17 lines, 331 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/ltc4245.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ltc4245.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lv5207lp.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/lv5207lp.h

## Purpose
`lv5207lp.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct lv5207lp_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LV5207LP_H__`. Types: `struct lv5207lp_platform_data`. Declared or inline
functions: none visible in this header. Important struct details: struct lv5207lp_platform_data
fields include `struct device *dev`, `unsigned int max_value`, `unsigned int def_value`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/sh/boards/mach-kfr2r09/setup.c`, `sources/distributed-fs/ceph-
client/drivers/video/backlight/lv5207lp.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/sh/boards/mach-kfr2r09/setup.c`, `sources/distributed-fs/ceph-
client/drivers/video/backlight/lv5207lp.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/lv5207lp.h` completely for this pass (16 lines, 271 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/lv5207lp.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/lv5207lp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/max197.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/max197.h

## Purpose
`max197.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
max197_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_PDATA_MAX197_H`. Types: `struct max197_platform_data`. Declared or inline
functions: `int`. Important struct details: struct max197_platform_data fields include `int
(*convert)(u8 ctrl)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/x86/platform/ts5500/ts5500.c`, `sources/distributed-fs/ceph-
client/drivers/hwmon/max197.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/x86/platform/ts5500/ts5500.c`, `sources/distributed-fs/ceph-
client/drivers/hwmon/max197.c`. It integrates through `struct platform_device` platform data, board
files, MFD child registration, and legacy non-DT setup paths; many modern systems may replace parts
of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/max197.h` completely for this pass (23 lines, 615 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/max197.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/max197.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/max3421-hcd.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/max3421-hcd.h

## Purpose
`max3421-hcd.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct max3421_hcd_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `MAX3421_HCD_PLAT_H_INCLUDED`. Types: `struct max3421_hcd_platform_data`. Declared
or inline functions: none visible in this header. Important struct details: struct
max3421_hcd_platform_data fields include `u8 vbus_gpout`, `u8 vbus_active_level`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/usb/host/max3421-hcd.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/usb/host/max3421-hcd.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/max3421-hcd.h` completely for this pass (25 lines, 808 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/max3421-hcd.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/max3421-hcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/max732x.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/max732x.h

## Purpose
`max732x.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
max732x_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_I2C_MAX732X_H`. Types: `struct max732x_platform_data`. Declared or inline
functions: none visible in this header. Important struct details: struct max732x_platform_data
fields include `unsigned gpio_base`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/gpio/gpio-max732x.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/gpio/gpio-max732x.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/max732x.h` completely for this pass (11 lines, 288 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/max732x.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/max732x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mdio-bcm-unimac.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mdio-bcm-unimac.h

## Purpose
`mdio-bcm-unimac.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct unimac_mdio_pdata` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__MDIO_BCM_UNIMAC_PDATA_H`, `UNIMAC_MDIO_DRV_NAME`. Types: `struct
unimac_mdio_pdata`. Declared or inline functions: `int`. Important struct details: struct
unimac_mdio_pdata fields include `u32 phy_mask`, `int (*wait_func)(void *data)`, `void
*wait_func_data`, `const char *bus_name`, `struct clk *clk`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/net/ethernet/broadcom/genet/bcmmii.c`, `sources/distributed-fs/ceph-
client/drivers/net/mdio/mdio-bcm-unimac.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/net/ethernet/broadcom/genet/bcmmii.c`, `sources/distributed-fs/ceph-
client/drivers/net/mdio/mdio-bcm-unimac.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mdio-bcm-unimac.h` completely for this pass (16 lines, 306 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mdio-bcm-unimac.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mdio-bcm-unimac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/media/camera-pxa.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/media/camera-pxa.h

## Purpose
`camera-pxa.h` is a Linux kernel media/camera/radio board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct pxacamera_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__ASM_ARCH_CAMERA_H_`, `PXA_CAMERA_MASTER`, `PXA_CAMERA_DATAWIDTH_4`,
`PXA_CAMERA_DATAWIDTH_5`, `PXA_CAMERA_DATAWIDTH_8`, `PXA_CAMERA_DATAWIDTH_9`,
`PXA_CAMERA_DATAWIDTH_10`, `PXA_CAMERA_PCLK_EN`, `PXA_CAMERA_MCLK_EN`, `PXA_CAMERA_PCP`,
`PXA_CAMERA_HSP`, `PXA_CAMERA_VSP`. Types: `struct pxacamera_platform_data`. Declared or inline
functions: `pxa_set_camera_info`. Important struct details: struct pxacamera_platform_data fields
include `unsigned long flags`, `unsigned long mclk_10khz`, `int sensor_i2c_adapter_id`, `int
sensor_i2c_address`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/media/platform/intel/pxa_camera.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/media/platform/intel/pxa_camera.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/media/camera-pxa.h` completely for this pass (34 lines, 869 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/media/camera-pxa.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/media/camera-pxa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/media/mmp-camera.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/media/mmp-camera.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/media/si4713.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/media/si4713.h

## Purpose
`si4713.h` is a Linux kernel media/camera/radio board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct si4713_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `SI4713_H`, `SI4713_I2C_ADDR_BUSEN_HIGH`, `SI4713_I2C_ADDR_BUSEN_LOW`,
`SI4713_IOC_MEASURE_RNL`. Types: `struct si4713_platform_data`, `struct si4713_rnl`. Declared or
inline functions: none visible in this header. Important struct details: struct si4713_platform_data
fields include `bool is_platform_device`; struct si4713_rnl fields include `__u32 index`, `__u32
frequency`, `__s32 rnl`, `__u32 reserved[4]`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/media/radio/si4713/radio-usb-si4713.c`, `sources/distributed-fs/ceph-
client/drivers/media/radio/si4713/si4713.h`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/media/radio/si4713/radio-usb-si4713.c`, `sources/distributed-fs/ceph-
client/drivers/media/radio/si4713/si4713.h`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/media/si4713.h` completely for this pass (48 lines, 1414 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/media/si4713.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/media/si4713.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/media/timb_radio.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/media/timb_radio.h

## Purpose
`timb_radio.h` is a Linux kernel media/camera/radio board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct timb_radio_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_TIMB_RADIO_`. Types: `struct timb_radio_platform_data`. Declared or inline
functions: none visible in this header. Important struct details: struct timb_radio_platform_data
fields include `int i2c_adapter`, `struct i2c_board_info *tuner`, `struct i2c_board_info *dsp`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mfd/timberdale.c`, `sources/distributed-fs/ceph-client/drivers/media/radio/radio-
timb.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/i2c.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/mfd/timberdale.c`, `sources/distributed-fs/ceph-
client/drivers/media/radio/radio-timb.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/media/timb_radio.h` completely for this pass (18 lines, 403 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/media/timb_radio.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/media/timb_radio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/media/timb_video.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/media/timb_video.h

## Purpose
`timb_video.h` is a Linux kernel display or framebuffer board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct timb_video_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_TIMB_VIDEO_`. Types: `struct timb_video_platform_data`. Declared or inline
functions: none visible in this header. Important struct details: struct timb_video_platform_data
fields include `int dma_channel`, `int i2c_adapter`, `const char *module_name`, `struct
i2c_board_info *info`, `} encoder`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mfd/timberdale.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/i2c.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/mfd/timberdale.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/media/timb_video.h` completely for this pass (21 lines, 443 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/media/timb_video.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/media/timb_video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mfd-mcp-sa11x0.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mfd-mcp-sa11x0.h

## Purpose
`mfd-mcp-sa11x0.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct mcp_plat_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__MFD_MCP_SA11X0_H`. Types: `struct mcp_plat_data`. Declared or inline functions:
none visible in this header. Important struct details: struct mcp_plat_data fields include `u32
mccr0`, `u32 mccr1`, `unsigned int sclk_rate`, `void *codec_pdata`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-sa1100/assabet.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
sa1100/collie.c`, `sources/distributed-fs/ceph-client/drivers/mfd/mcp-sa11x0.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/assabet.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-sa1100/collie.c`, `sources/distributed-fs/ceph-client/drivers/mfd/mcp-
sa11x0.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mfd-mcp-sa11x0.h` completely for this pass (17 lines, 272 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mfd-mcp-sa11x0.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mfd-mcp-sa11x0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/microchip-ksz.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/microchip-ksz.h

## Purpose
`microchip-ksz.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct ksz_platform_data`; enumerations such as `enum ksz_chip_id` into the matching driver at
probe time.

## Important APIs, types, and functions
Macros/constants: `__MICROCHIP_KSZ_H`. Types: `struct ksz_platform_data`, `enum ksz_chip_id`.
Declared or inline functions: none visible in this header. Important struct details: struct
ksz_platform_data fields include `struct dsa_chip_data cd`, `u32 chip_id`. Important enum details:
enum ksz_chip_id values include `KSZ8463_CHIP_ID`, `KSZ8563_CHIP_ID`, `KSZ8795_CHIP_ID`,
`KSZ8794_CHIP_ID`, `KSZ8765_CHIP_ID`, `KSZ88X3_CHIP_ID`, `KSZ8864_CHIP_ID`, `KSZ8895_CHIP_ID`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/net/dsa/microchip/ksz8.c`, `sources/distributed-fs/ceph-
client/drivers/net/dsa/microchip/ksz9477.c`, `sources/distributed-fs/ceph-
client/drivers/net/dsa/microchip/ksz_common.c`, `sources/distributed-fs/ceph-
client/drivers/net/dsa/microchip/ksz_common.h`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`, `linux/platform_data/dsa.h`. Direct source-tree consumers found by
include search are `sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz8.c`,
`sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz9477.c`, `sources/distributed-
fs/ceph-client/drivers/net/dsa/microchip/ksz_common.c`, `sources/distributed-fs/ceph-
client/drivers/net/dsa/microchip/ksz_common.h`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/microchip-ksz.h` completely for this pass (55 lines, 1713 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/microchip-ksz.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/microchip-ksz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mipi-i3c-hci.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mipi-i3c-hci.h

## Purpose
`mipi-i3c-hci.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct mipi_i3c_hci_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `INCLUDE_PLATFORM_DATA_MIPI_I3C_HCI_H`. Types: `struct
mipi_i3c_hci_platform_data`. Declared or inline functions: none visible in this header. Important
struct details: struct mipi_i3c_hci_platform_data fields include `void __iomem *base_regs`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/i3c/master/mipi-i3c-hci/core.c`, `sources/distributed-fs/ceph-
client/drivers/i3c/master/mipi-i3c-hci/mipi-i3c-hci-pci.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/compiler_types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/core.c`, `sources/distributed-
fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/mipi-i3c-hci-pci.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mipi-i3c-hci.h` completely for this pass (15 lines, 400 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mipi-i3c-hci.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mipi-i3c-hci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mlxcpld.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mlxcpld.h

## Purpose
`mlxcpld.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
mlxcpld_mux_plat_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_LINUX_I2C_MLXCPLD_H`. Types: `struct mlxcpld_mux_plat_data`. Declared or inline
functions: none visible in this header. Important struct details: struct mlxcpld_mux_plat_data
fields include `int *chan_ids`, `int num_adaps`, `int sel_reg_addr`, `u8 reg_size`, `void *handle`,
`struct i2c_adapter *adapters[])`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/mlxreg-dpu.c`, `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/mlxreg-lc.c`, `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/nvsw-sn2201.c`, `sources/distributed-fs/ceph-
client/drivers/i2c/muxes/i2c-mux-mlxcpld.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/mlxreg-dpu.c`, `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/mlxreg-lc.c`, `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/nvsw-sn2201.c`, `sources/distributed-fs/ceph-
client/drivers/i2c/muxes/i2c-mux-mlxcpld.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mlxcpld.h` completely for this pass (31 lines, 885 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mlxcpld.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mlxcpld.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mlxreg.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mlxreg.h

## Purpose
`mlxreg.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
mlxreg_core_hotplug_notifier`; enumerations such as `enum mlxreg_wdt_type`, `enum
mlxreg_hotplug_kind` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_PLATFORM_DATA_MLXREG_H`, `MLXREG_CORE_LABEL_MAX_SIZE`,
`MLXREG_CORE_WD_FEATURE_NOWAYOUT`, `MLXREG_CORE_WD_FEATURE_START_AT_BOOT`. Types: `struct
mlxreg_core_hotplug_notifier`, `struct mlxreg_hotplug_device`, `struct mlxreg_core_data`, `struct
mlxreg_core_item`, `struct mlxreg_core_platform_data`, `struct mlxreg_core_hotplug_platform_data`,
`enum mlxreg_wdt_type`, `enum mlxreg_hotplug_kind`, `enum mlxreg_hotplug_device_action`. Declared or
inline functions: `int`. Important struct details: struct mlxreg_core_hotplug_notifier fields
include `char identity[MLXREG_CORE_LABEL_MAX_SIZE]`, `void *handle`, `int (*user_handler)(void
*handle, enum mlxreg_hotplug_kind kind, u8 action)`; struct mlxreg_hotplug_device fields include
`struct i2c_adapter *adapter`, `struct i2c_client *client`, `struct i2c_board_info *brdinfo`, `int
nr`, `struct platform_device *pdev`, `enum mlxreg_hotplug_device_action action`, `void *handle`,
`int (*user_handler)(void *handle, enum mlxreg_hotplug_kind kind, u8 action)`; struct
mlxreg_core_data fields include `char label[MLXREG_CORE_LABEL_MAX_SIZE]`, `u32 reg`, `u32 mask`,
`u32 bit`, `u32 capability`, `u32 reg_prsnt`, `u32 reg_sync`, `u32 reg_pwr`; struct mlxreg_core_item
fields include `struct mlxreg_core_data *data`, `enum mlxreg_hotplug_kind kind`, `u32 aggr_mask`,
`u32 reg`, `u32 mask`, `u32 capability`, `u32 cache`, `u8 count`; struct mlxreg_core_platform_data
fields include `struct mlxreg_core_data *data`, `void *regmap`, `int counter`, `u32 features`, `u32
version`, `char identity[MLXREG_CORE_LABEL_MAX_SIZE]`, `u32 capability`. Important enum details:
enum mlxreg_wdt_type values include `MLX_WDT_TYPE1`, `MLX_WDT_TYPE2`, `MLX_WDT_TYPE3`; enum
mlxreg_hotplug_kind values include `MLXREG_HOTPLUG_DEVICE_NA`, `MLXREG_HOTPLUG_LC_PRESENT`,
`MLXREG_HOTPLUG_LC_VERIFIED`, `MLXREG_HOTPLUG_LC_POWERED`, `MLXREG_HOTPLUG_LC_SYNCED`,
`MLXREG_HOTPLUG_LC_READY`, `MLXREG_HOTPLUG_LC_ACTIVE`, `MLXREG_HOTPLUG_LC_THERMAL`; enum
mlxreg_hotplug_device_action values include `MLXREG_HOTPLUG_DEVICE_DEFAULT_ACTION`,
`MLXREG_HOTPLUG_DEVICE_PLATFORM_ACTION`, `MLXREG_HOTPLUG_DEVICE_NO_ACTION`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/mlxreg-dpu.c`, `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/mlxreg-lc.c`, `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/nvsw-sn2201.c`, `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/mlxreg-hotplug.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/mlxreg-dpu.c`, `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/mlxreg-lc.c`, `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/nvsw-sn2201.c`, `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/mlxreg-hotplug.c`, `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/mlx-platform.c`, `sources/distributed-fs/ceph-
client/drivers/platform/mellanox/mlxreg-io.c`, `sources/distributed-fs/ceph-
client/drivers/leds/leds-mlxreg.c`, `sources/distributed-fs/ceph-
client/drivers/net/ethernet/mellanox/mlxsw/i2c.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mlxreg.h` completely for this pass (239 lines, 7756 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mlxreg.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mlxreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-davinci.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-davinci.h

## Purpose
`mmc-davinci.h` is a Linux kernel MMC/SD/SDHCI host board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct davinci_mmc_config`; enumerations such as `anonymous enum` into the matching driver at probe
time.

## Important APIs, types, and functions
Macros/constants: `_DAVINCI_MMC_H`. Types: `struct davinci_mmc_config`, `anonymous enum`. Declared
or inline functions: `int`, `void`, `davinci_setup_mmc`. Important struct details: struct
davinci_mmc_config fields include `int (*get_cd)(int module)`, `int (*get_ro)(int module)`, `void
(*set_power)(int module, bool on)`, `u8 wires`, `u32 max_freq`, `u32 caps`, `u8 nr_sg`. Important
enum details: anonymous enum values include `MMC_CTLR_VERSION_1`, `MMC_CTLR_VERSION_2`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mmc/host/davinci_mmc.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`, `linux/mmc/host.h`. Direct source-tree consumers found by include
search are `sources/distributed-fs/ceph-client/drivers/mmc/host/davinci_mmc.c`. It integrates
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-davinci.h` completely for this pass (37 lines, 736 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-davinci.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-davinci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-esdhc-mcf.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-esdhc-mcf.h

## Purpose
`mmc-esdhc-mcf.h` is a Linux kernel MMC/SD/SDHCI host board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct mcf_esdhc_platform_data`; enumerations such as `enum cd_types` into the matching driver at
probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_PLATFORM_DATA_MCF_ESDHC_H__`. Types: `struct mcf_esdhc_platform_data`,
`enum cd_types`. Declared or inline functions: none visible in this header. Important struct
details: struct mcf_esdhc_platform_data fields include `int max_bus_width`, `int cd_type`. Important
enum details: enum cd_types values include `ESDHC_CD_NONE`, `ESDHC_CD_CONTROLLER`,
`ESDHC_CD_PERMANENT`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/m68k/coldfire/device.c`, `sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-
esdhc-mcf.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/m68k/coldfire/device.c`, `sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-
esdhc-mcf.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-esdhc-mcf.h` completely for this pass (17 lines, 447 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-esdhc-mcf.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-esdhc-mcf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-mxcmmc.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-mxcmmc.h

## Purpose
`mmc-mxcmmc.h` is a Linux kernel MMC/SD/SDHCI host board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct imxmmc_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `ASMARM_ARCH_MMC_H`. Types: `struct imxmmc_platform_data`. Declared or inline
functions: `int`, `void`. Important struct details: struct imxmmc_platform_data fields include `int
(*get_ro)(struct device *)`, `int (*init)(struct device *dev, irq_handler_t handler, void *data)`,
`void (*exit)(struct device *dev, void *data)`, `unsigned int ocr_avail`, `void (*setpower)(struct
device *, unsigned int vdd)`, `int dat3_card_detect`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mmc/host/mxcmmc.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/interrupt.h`, `linux/mmc/host.h`. Direct source-tree consumers found by include
search are `sources/distributed-fs/ceph-client/drivers/mmc/host/mxcmmc.c`. It integrates through
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-mxcmmc.h` completely for this pass (41 lines, 1099 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-mxcmmc.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-mxcmmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-omap.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-omap.h

## Purpose
`mmc-omap.h` is a Linux kernel MMC/SD/SDHCI host board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct omap_mmc_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `OMAP_MMC_MAX_SLOTS`, `MMC_OMAP7XX`, `MMC_OMAP15XX`, `MMC_OMAP16XX`. Types:
`struct omap_mmc_platform_data`. Declared or inline functions: `int`, `void`. Important struct
details: struct omap_mmc_platform_data fields include `struct device *dev`, `unsigned nr_slots:2`,
`unsigned int max_freq`, `int (*init)(struct device *dev)`, `void (*cleanup)(struct device *dev)`,
`void (*shutdown)(struct device *dev)`, `int (*get_context_loss_count)(struct device *dev)`, `u8
controller_flags`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/mmc.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/board-n8x0.c`, `sources/distributed-fs/ceph-client/drivers/mmc/host/omap.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/mmc.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/board-n8x0.c`, `sources/distributed-fs/ceph-client/drivers/mmc/host/omap.c`. It integrates
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-omap.h` completely for this pass (118 lines, 3294 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-omap.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-pxamci.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-pxamci.h

## Purpose
`mmc-pxamci.h` is a Linux kernel MMC/SD/SDHCI host board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct pxamci_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `ASMARM_ARCH_MMC_H`. Types: `struct pxamci_platform_data`. Declared or inline
functions: `int`, `void`, `pxa3xx_set_mci2_info`, `pxa3xx_set_mci3_info`. Important struct details:
struct pxamci_platform_data fields include `unsigned int ocr_mask`, `unsigned long detect_delay_ms`,
`int (*init)(struct device *, irq_handler_t , void *)`, `int (*get_ro)(struct device *)`, `int
(*setpower)(struct device *, unsigned int)`, `void (*exit)(struct device *, void *)`, `bool
gpio_card_ro_invert`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/gumstix.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
pxa/devices.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.c`,
`sources/distributed-fs/ceph-client/drivers/mmc/host/pxamci.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/mmc/host.h`, `linux/interrupt.h`. Direct source-tree consumers found by include
search are `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.c`, `sources/distributed-
fs/ceph-client/arch/arm/mach-pxa/devices.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
pxa/spitz.c`, `sources/distributed-fs/ceph-client/drivers/mmc/host/pxamci.c`. It integrates through
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-pxamci.h` completely for this pass (27 lines, 882 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-pxamci.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-pxamci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-sdhci-s3c.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-sdhci-s3c.h

## Purpose
`mmc-sdhci-s3c.h` is a Linux kernel MMC/SD/SDHCI host board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct s3c_sdhci_platdata`; enumerations such as `enum cd_types` into the matching driver at probe
time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_SDHCI_S3C_H`. Types: `struct s3c_sdhci_platdata`, `enum
cd_types`. Declared or inline functions: `void`. Important struct details: struct s3c_sdhci_platdata
fields include `unsigned int max_width`, `unsigned int host_caps`, `unsigned int host_caps2`,
`unsigned int pm_caps`, `enum cd_types cd_type`, `int ext_cd_gpio`, `bool ext_cd_gpio_invert`, `int
state))`. Important enum details: enum cd_types values include `S3C_SDHCI_CD_INTERNAL`,
`S3C_SDHCI_CD_EXTERNAL`, `S3C_SDHCI_CD_GPIO`, `S3C_SDHCI_CD_NONE`, `S3C_SDHCI_CD_PERMANENT`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/sdhci.h`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/sdhci-s3c.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/sdhci.h`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/sdhci-s3c.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-sdhci-s3c.h` completely for this pass (57 lines, 2278 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-sdhci-s3c.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmc-sdhci-s3c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmp_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mmp_dma.h

## Purpose
`mmp_dma.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
mmp_dma_platdata` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `MMP_DMA_H`. Types: `struct mmp_dma_platdata`. Declared or inline functions: none
visible in this header. Important struct details: struct mmp_dma_platdata fields include `int
dma_channels`, `int nb_requestors`, `int slave_map_cnt`, `const struct dma_slave_map *slave_map`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/dma/pxa_dma.c`, `sources/distributed-fs/ceph-client/drivers/dma/mmp_pdma.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/pxa3xx.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/dma/pxa_dma.c`, `sources/distributed-fs/ceph-client/drivers/dma/mmp_pdma.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/pxa3xx.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mmp_dma.h` completely for this pass (20 lines, 350 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mmp_dma.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mmp_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-omap2.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-omap2.h

## Purpose
`mtd-nand-omap2.h` is a Linux kernel NAND flash controller board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct gpmc_nand_regs`; enumerations such as `enum nand_io`, `enum omap_ecc` into the matching
driver at probe time.

## Important APIs, types, and functions
Macros/constants: none visible in this header. Types: `struct gpmc_nand_regs`, `enum nand_io`, `enum
omap_ecc`. Declared or inline functions: none visible in this header. Important struct details:
struct gpmc_nand_regs fields include `void __iomem *gpmc_nand_command`, `void __iomem
*gpmc_nand_address`, `void __iomem *gpmc_nand_data`, `void __iomem *gpmc_prefetch_config1`, `void
__iomem *gpmc_prefetch_config2`, `void __iomem *gpmc_prefetch_control`, `void __iomem
*gpmc_prefetch_status`, `void __iomem *gpmc_ecc_config`. Important enum details: enum nand_io values
include `NAND_OMAP_PREFETCH_POLLED`, `NAND_OMAP_POLLED`, `NAND_OMAP_PREFETCH_DMA`,
`NAND_OMAP_PREFETCH_IRQ`; enum omap_ecc values include `/*`, `OMAP_ECC_HAM1_CODE_SW`, `/*`,
`OMAP_ECC_HAM1_CODE_HW`, `OMAP_ECC_BCH4_CODE_HW_DETECTION_SW`, `OMAP_ECC_BCH4_CODE_HW`,
`OMAP_ECC_BCH8_CODE_HW_DETECTION_SW`, `OMAP_ECC_BCH8_CODE_HW`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mtd/nand/raw/omap2.c`, `sources/distributed-fs/ceph-client/drivers/memory/omap-
gpmc.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/mtd/partitions.h`, `linux/mod_devicetable.h`. Direct source-tree consumers found
by include search are `sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/omap2.c`,
`sources/distributed-fs/ceph-client/drivers/memory/omap-gpmc.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-omap2.h` completely for this pass (72 lines, 2244 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-omap2.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-omap2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-pxa3xx.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-pxa3xx.h

## Purpose
`mtd-nand-pxa3xx.h` is a Linux kernel NAND flash controller board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct pxa3xx_nand_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__ASM_ARCH_PXA3XX_NAND_H`. Types: `struct pxa3xx_nand_platform_data`. Declared or
inline functions: `pxa3xx_set_nand_info`. Important struct details: struct pxa3xx_nand_platform_data
fields include `bool keep_config`, `bool flash_bbt`, `int ecc_strength, ecc_step_size`, `const
struct mtd_partition *parts`, `unsigned int nr_parts`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mtd/nand/raw/marvell_nand.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/mtd/mtd.h`, `linux/mtd/partitions.h`. Direct source-tree consumers found by
include search are `sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/marvell_nand.c`. It
integrates through `struct platform_device` platform data, board files, MFD child registration, and
legacy non-DT setup paths; many modern systems may replace parts of this contract with Device Tree,
ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-pxa3xx.h` completely for this pass (27 lines, 812 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-pxa3xx.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-nand-pxa3xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-orion_nand.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-orion_nand.h

## Purpose
`mtd-orion_nand.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct orion_nand_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__MTD_ORION_NAND_H`. Types: `struct orion_nand_data`. Declared or inline
functions: none visible in this header. Important struct details: struct orion_nand_data fields
include `struct mtd_partition *parts`, `u32 nr_parts`, `u8 ale`, `u8 cle`, `u8 width`, `u8
chip_delay`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-orion5x/common.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
orion5x/kurobox_pro-setup.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.c`,
`sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/orion_nand.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-orion5x/common.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
orion5x/kurobox_pro-setup.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.c`,
`sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/orion_nand.c`. It integrates through
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-orion_nand.h` completely for this pass (23 lines, 520 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-orion_nand.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mtd-orion_nand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mv88e6xxx.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mv88e6xxx.h

## Purpose
`mv88e6xxx.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct dsa_mv88e6xxx_pdata` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__DSA_MV88E6XXX_H`. Types: `struct dsa_mv88e6xxx_pdata`. Declared or inline
functions: none visible in this header. Important struct details: struct dsa_mv88e6xxx_pdata fields
include `struct dsa_chip_data cd`, `const char *compatible`, `unsigned int enabled_ports`, `struct
net_device *netdev`, `u32 eeprom_len`, `int irq`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/net/dsa/mv88e6xxx/chip.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/platform_data/dsa.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/chip.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mv88e6xxx.h` completely for this pass (19 lines, 416 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mv88e6xxx.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mv88e6xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mv_usb.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/mv_usb.h

## Purpose
`mv_usb.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct mv_usb_addon_irq`; enumerations such as `anonymous enum` into the matching driver at probe
time.

## Important APIs, types, and functions
Macros/constants: `__MV_PLATFORM_USB_H`. Types: `struct mv_usb_addon_irq`, `struct
mv_usb_platform_data`, `anonymous enum`. Declared or inline functions: `int`, `void`. Important
struct details: struct mv_usb_addon_irq fields include `unsigned int irq`, `int (*poll)(void)`;
struct mv_usb_platform_data fields include `struct mv_usb_addon_irq *id`, `struct mv_usb_addon_irq
*vbus`, `unsigned int mode`, `unsigned int disable_otg_clock_gating:1`, `unsigned int
otg_force_a_bus_req:1`, `int (*phy_init)(void __iomem *regbase)`, `void (*phy_deinit)(void __iomem
*regbase)`, `int (*set_vbus)(unsigned int vbus)`. Important enum details: anonymous enum values
include `MV_USB_MODE_OTG`, `MV_USB_MODE_HOST`; anonymous enum values include `VBUS_LOW`,
`VBUS_HIGH`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/usb/host/ehci-mv.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/usb/host/ehci-mv.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/mv_usb.h` completely for this pass (40 lines, 900 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/mv_usb.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/mv_usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/net-cw1200.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/net-cw1200.h

## Purpose
`net-cw1200.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct cw1200_platform_data_spi` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `CW1200_PLAT_H_INCLUDED`. Types: `struct cw1200_platform_data_spi`, `struct
cw1200_platform_data_sdio`. Declared or inline functions: `cw1200_sdio_set_platform_data`. Important
struct details: struct cw1200_platform_data_spi fields include `u8 spi_bits_per_word`, `u16
ref_clk`, `bool have_5ghz`, `bool enable)`, `bool enable)`, `const u8 *macaddr`, `const char
*sdd_file`; struct cw1200_platform_data_sdio fields include `u16 ref_clk`, `bool have_5ghz`, `bool
no_nptb`, `int irq`, `bool enable)`, `bool enable)`, `const u8 *macaddr`, `const char *sdd_file`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/net/wireless/st/cw1200/cw1200_sdio.c`, `sources/distributed-fs/ceph-
client/drivers/net/wireless/st/cw1200/cw1200_spi.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/net/wireless/st/cw1200/cw1200_sdio.c`, `sources/distributed-fs/ceph-
client/drivers/net/wireless/st/cw1200/cw1200_spi.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/net-cw1200.h` completely for this pass (77 lines, 2496 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/net-cw1200.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/net-cw1200.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/omap-twl4030.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/omap-twl4030.h

## Purpose
`omap-twl4030.h` is a Linux kernel TI OMAP platform integration data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct omap_tw4030_pdata` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_OMAP_TWL4030_H_`, `OMAP_TWL4030_LEFT`, `OMAP_TWL4030_RIGHT`. Types: `struct
omap_tw4030_pdata`. Declared or inline functions: none visible in this header. Important struct
details: struct omap_tw4030_pdata fields include `const char *card_name`, `bool voice_connected`,
`bool custom_routing`, `u8 has_hs`, `u8 has_hf`, `u8 has_predriv`, `u8 has_carkit`, `bool has_ear`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/sound/soc/ti/omap-twl4030.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/sound/soc/ti/omap-twl4030.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/omap-twl4030.h` completely for this pass (42 lines, 990 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/omap-twl4030.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/omap-twl4030.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/omap-wd-timer.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/omap-wd-timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/omap1_bl.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/omap1_bl.h

## Purpose
`omap1_bl.h` is a Linux kernel backlight controller board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct omap_backlight_config` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__OMAP1_BL_H__`. Types: `struct omap_backlight_config`. Declared or inline
functions: none visible in this header. Important struct details: struct omap_backlight_config
fields include `int default_intensity`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/board-osk.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap1/board-palmte.c`, `sources/distributed-fs/ceph-client/drivers/video/backlight/omap1_bl.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/device.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-omap1/board-osk.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/board-palmte.c`, `sources/distributed-fs/ceph-
client/drivers/video/backlight/omap1_bl.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/omap1_bl.h` completely for this pass (11 lines, 179 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/omap1_bl.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/omap1_bl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/omapdss.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/omapdss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/pca953x.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/pca953x.h

## Purpose
`pca953x.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
pca953x_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_LINUX_PCA953X_H`. Types: `struct pca953x_platform_data`. Declared or inline
functions: none visible in this header. Important struct details: struct pca953x_platform_data
fields include `unsigned gpio_base`, `int irq_base`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/spitz.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-
crag6410.c`, `sources/distributed-fs/ceph-client/drivers/gpio/gpio-pca953x.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`, `linux/i2c.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/mach-crag6410.c`, `sources/distributed-fs/ceph-client/drivers/gpio/gpio-
pca953x.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/pca953x.h` completely for this pass (18 lines, 360 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/pca953x.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/pca953x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/phy-da8xx-usb.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/phy-da8xx-usb.h

## Purpose
`phy-da8xx-usb.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct da8xx_usb_phy_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_PLATFORM_DATA_PHY_DA8XX_USB_H__`. Types: `struct
da8xx_usb_phy_platform_data`. Declared or inline functions: none visible in this header. Important
struct details: struct da8xx_usb_phy_platform_data fields include `struct regmap *cfgchip`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/phy/ti/phy-da8xx-usb.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/regmap.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/phy/ti/phy-da8xx-usb.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/phy-da8xx-usb.h` completely for this pass (21 lines, 474 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/phy-da8xx-usb.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/phy-da8xx-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/pic32.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/pic32.h

## Purpose
`pic32.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing macros, constants, or
function prototypes into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_PLATFORM_DATA_PIC32_H`, `PIC32_CLR`, `PIC32_SET`, `PIC32_INV`,
`PIC32_BASE_CONFIG`, `PIC32_BASE_OSC`, `PIC32_BASE_RESET`, `PIC32_BASE_PPS`, `PIC32_BASE_UART`,
`PIC32_BASE_PORT`, `PIC32_BASE_DEVCFG2`, `pic32_syskey_unlock`. Types: none visible in this header.
Declared or inline functions: `pic32_syskey_unlock_debug`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/mips/pic32/common/reset.c`, `sources/distributed-fs/ceph-
client/arch/mips/pic32/pic32mzda/config.c`, `sources/distributed-fs/ceph-
client/arch/mips/pic32/pic32mzda/early_console.c`, `sources/distributed-fs/ceph-
client/arch/mips/pic32/pic32mzda/early_clk.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/mips/pic32/common/reset.c`, `sources/distributed-fs/ceph-
client/arch/mips/pic32/pic32mzda/config.c`, `sources/distributed-fs/ceph-
client/arch/mips/pic32/pic32mzda/early_console.c`, `sources/distributed-fs/ceph-
client/arch/mips/pic32/pic32mzda/early_clk.c`, `sources/distributed-fs/ceph-
client/drivers/irqchip/irq-pic32-evic.c`, `sources/distributed-fs/ceph-client/drivers/rtc/rtc-
pic32.c`, `sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pic32.c`,
`sources/distributed-fs/ceph-client/drivers/tty/serial/pic32_uart.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/pic32.h` completely for this pass (39 lines, 1132 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/pic32.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/pic32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/pinctrl-single.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/pinctrl-single.h

## Purpose
`pinctrl-single.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct pcs_pdata` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_PINCTRL_SINGLE_H`. Types: `struct pcs_pdata`. Declared or inline functions:
`void`. Important struct details: struct pcs_pdata fields include `int irq`, `void (*rearm)(void)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/pdata-quirks.c`, `sources/distributed-fs/ceph-
client/drivers/pinctrl/pinctrl-single.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/pdata-quirks.c`, `sources/distributed-fs/ceph-
client/drivers/pinctrl/pinctrl-single.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/pinctrl-single.h` completely for this pass (19 lines, 425 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/pinctrl-single.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/pinctrl-single.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/pm33xx.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/pm33xx.h

## Purpose
`pm33xx.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
am33xx_pm_sram_addr` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_LINUX_PLATFORM_DATA_PM33XX_H`, `WFI_FLAG_FLUSH_CACHE`, `WFI_FLAG_SELF_REFRESH`,
`WFI_FLAG_SAVE_EMIF`, `WFI_FLAG_WAKE_M3`, `WFI_FLAG_RTC_ONLY`. Types: `struct am33xx_pm_sram_addr`,
`struct am33xx_pm_platform_data`. Declared or inline functions: `void`, `int`. Important struct
details: struct am33xx_pm_sram_addr fields include `void (*do_wfi)(void)`, `unsigned long
*do_wfi_sz`, `unsigned long *resume_offset`, `unsigned long *emif_sram_table`, `unsigned long
*ro_sram_data`, `unsigned long resume_address`; struct am33xx_pm_platform_data fields include `int
(*init)(int (*idle)(u32 wfi_flags))`, `int (*deinit)(void)`, `unsigned long args)`, `int
(*cpu_suspend)(int (*fn)(unsigned long), unsigned long args)`, `void (*begin_suspend)(void)`, `void
(*finish_suspend)(void)`, `struct am33xx_pm_sram_addr *(*get_sram_addrs)(void)`, `void
(*save_context)(void)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/sleep43xx.S`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/pm33xx-core.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm-asm-offsets.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep33xx.S`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/kbuild.h`, `linux/types.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep43xx.S`, `sources/distributed-
fs/ceph-client/arch/arm/mach-omap2/pm33xx-core.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/pm-asm-offsets.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/sleep33xx.S`, `sources/distributed-fs/ceph-client/drivers/soc/ti/pm33xx.c`. It integrates
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/pm33xx.h` completely for this pass (75 lines, 2305 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/pm33xx.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/pm33xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/pxa2xx_udc.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/pxa2xx_udc.h

## Purpose
`pxa2xx_udc.h` is a Linux kernel Marvell PXA platform integration data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct pxa2xx_udc_mach_info` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `PXA2XX_UDC_H`, `pxa27x_clear_otgph`. Types: `struct pxa2xx_udc_mach_info`.
Declared or inline functions: `int`, `void`, `pxa27x_clear_otgph`. Important struct details: struct
pxa2xx_udc_mach_info fields include `int (*udc_is_connected)(void)`, `void (*udc_command)(int cmd)`,
`bool gpio_pullup_inverted`, `int gpio_pullup`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/udc.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c`,
`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/pxa27x_udc.c`, `sources/distributed-
fs/ceph-client/drivers/usb/gadget/udc/pxa25x_udc.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/udc.h`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c`,
`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/pxa27x_udc.c`, `sources/distributed-
fs/ceph-client/drivers/usb/gadget/udc/pxa25x_udc.c`, `sources/distributed-fs/ceph-
client/drivers/usb/host/ohci-pxa27x.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/pxa2xx_udc.h` completely for this pass (34 lines, 1101 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/pxa2xx_udc.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/pxa2xx_udc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/pxa_sdhci.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/pxa_sdhci.h

## Purpose
`pxa_sdhci.h` is a Linux kernel Marvell PXA platform integration data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct sdhci_pxa_platdata` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_PXA_SDHCI_H_`, `PXA_FLAG_ENABLE_CLOCK_GATING`, `PXA_FLAG_CARD_PERMANENT`,
`PXA_FLAG_SD_8_BIT_CAPABLE_SLOT`. Types: `struct sdhci_pxa_platdata`. Declared or inline functions:
none visible in this header. Important struct details: struct sdhci_pxa_platdata fields include
`unsigned int flags`, `unsigned int clk_delay_cycles`, `unsigned int clk_delay_sel`, `bool
clk_delay_enable`, `unsigned int max_speed`, `u32 host_caps`, `u32 host_caps2`, `unsigned int
quirks`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mmc/host/sdhci-pxav3.c`, `sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-
pxav2.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/mmc/host/sdhci-pxav3.c`, `sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-
pxav2.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/pxa_sdhci.h` completely for this pass (51 lines, 1482 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/pxa_sdhci.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/pxa_sdhci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/regulator-haptic.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/regulator-haptic.h

## Purpose
`regulator-haptic.h` is a Linux kernel regulator or haptic power board-data header. It gives board
files, MFD children, ACPI glue, or platform-device setup code a compact contract for passing the
primary type `struct regulator_haptic_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_REGULATOR_HAPTIC_H`. Types: `struct regulator_haptic_data`. Declared or inline
functions: none visible in this header. Important struct details: struct regulator_haptic_data
fields include `unsigned int max_volt`, `unsigned int min_volt`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/input/misc/regulator-haptic.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/input/misc/regulator-haptic.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/regulator-haptic.h` completely for this pass (26 lines, 691 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/regulator-haptic.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/regulator-haptic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/s3c-hsotg.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/s3c-hsotg.h

## Purpose
`s3c-hsotg.h` is a Linux kernel Samsung S3C platform integration data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct dwc2_hsotg_plat`; enumerations such as `enum dwc2_hsotg_dmamode` into the matching
driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_USB_S3C_HSOTG_H`. Types: `struct dwc2_hsotg_plat`, `enum
dwc2_hsotg_dmamode`. Declared or inline functions: `int`, `dwc2_hsotg_set_platdata`. Important
struct details: struct dwc2_hsotg_plat fields include `enum dwc2_hsotg_dmamode dma`, `unsigned int
is_osc:1`, `int phy_type`, `int (*phy_init)(struct platform_device *pdev, int type)`, `int
(*phy_exit)(struct platform_device *pdev, int type)`. Important enum details: enum
dwc2_hsotg_dmamode values include `S3C_HSOTG_DMA_NONE`, `S3C_HSOTG_DMA_ONLY`, `S3C_HSOTG_DMA_DRV`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/devs.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-
crag6410.c`, `sources/distributed-fs/ceph-client/drivers/usb/dwc2/platform.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/devs.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-
crag6410.c`, `sources/distributed-fs/ceph-client/drivers/usb/dwc2/platform.c`. It integrates through
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/s3c-hsotg.h` completely for this pass (39 lines, 1064 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/s3c-hsotg.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/s3c-hsotg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/sa11x0-serial.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/sa11x0-serial.h

## Purpose
`sa11x0-serial.h` is a Linux kernel serial/UART board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct sa1100_port_fns` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `SA11X0_SERIAL_H`. Types: `struct sa1100_port_fns`. Declared or inline functions:
`void`, `u_int`, `int`, `sa1100_register_uart_fns`, `sa1100_register_uart`. Important struct
details: struct sa1100_port_fns fields include `void (*set_mctrl)(struct uart_port *, u_int)`,
`u_int (*get_mctrl)(struct uart_port *)`, `void (*pm)(struct uart_port *, u_int, u_int)`, `int
(*set_wake)(struct uart_port *, u_int)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-sa1100/jornada720.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
sa1100/assabet.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/h3xxx.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/collie.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-sa1100/jornada720.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
sa1100/assabet.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/h3xxx.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/collie.c`, `sources/distributed-fs/ceph-
client/drivers/tty/serial/sa1100.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/sa11x0-serial.h` completely for this pass (37 lines, 856 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/sa11x0-serial.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/sa11x0-serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/sc18is602.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/sc18is602.h

## Purpose
`sc18is602.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct sc18is602_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: none visible in this header. Types: `struct sc18is602_platform_data`. Declared or
inline functions: none visible in this header. Important struct details: struct
sc18is602_platform_data fields include `u32 clock_frequency`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/spi/spi-sc18is602.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/spi/spi-sc18is602.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/sc18is602.h` completely for this pass (16 lines, 401 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/sc18is602.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/sc18is602.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/sdhci-pic32.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/sdhci-pic32.h

## Purpose
`sdhci-pic32.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct pic32_sdhci_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PIC32_SDHCI_PDATA_H__`. Types: `struct pic32_sdhci_platform_data`. Declared or
inline functions: `int`. Important struct details: struct pic32_sdhci_platform_data fields include
`int (*setup_dma)(u32 rfifo, u32 wfifo)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/mips/pic32/pic32mzda/init.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/sdhci-pic32.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/mips/pic32/pic32mzda/init.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/sdhci-pic32.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/sdhci-pic32.h` completely for this pass (14 lines, 360 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/sdhci-pic32.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/sdhci-pic32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/serial-omap.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/serial-omap.h

## Purpose
`serial-omap.h` is a Linux kernel serial/UART board-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
omap_uart_port_info` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__OMAP_SERIAL_H__`, `OMAP_SERIAL_DRIVER_NAME`, `OMAP_SERIAL_NAME`. Types: `struct
omap_uart_port_info`. Declared or inline functions: `int`, `void`. Important struct details: struct
omap_uart_port_info fields include `bool dma_enabled`, `unsigned int uartclk`, `upf_t flags`,
`unsigned int dma_rx_buf_size`, `unsigned int dma_rx_timeout`, `unsigned int autosuspend_timeout`,
`unsigned int dma_rx_poll_rate`, `int (*get_context_loss_count)(struct device *)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/tty/serial/omap-serial.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/serial_core.h`, `linux/device.h`, `linux/pm_qos.h`. Direct source-tree consumers
found by include search are `sources/distributed-fs/ceph-client/drivers/tty/serial/omap-serial.c`.
It integrates through `struct platform_device` platform data, board files, MFD child registration,
and legacy non-DT setup paths; many modern systems may replace parts of this contract with Device
Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/serial-omap.h` completely for this pass (42 lines, 1024 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/serial-omap.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/serial-omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/serial-sccnxp.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/serial-sccnxp.h

## Purpose
`serial-sccnxp.h` is a Linux kernel serial/UART board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct sccnxp_pdata` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_PLATFORM_DATA_SERIAL_SCCNXP_H_`, `SCCNXP_MAX_UARTS`, `LINE_OP0`, `LINE_OP1`,
`LINE_OP2`, `LINE_OP3`, `LINE_OP4`, `LINE_OP5`, `LINE_OP6`, `LINE_OP7`, `LINE_IP0`, `LINE_IP1`,
`LINE_IP2`, `LINE_IP3`, and 11 more. Types: `struct sccnxp_pdata`. Declared or inline functions:
none visible in this header. Important struct details: struct sccnxp_pdata fields include `const u8
reg_shift`, `const u32 mctrl_cfg[SCCNXP_MAX_UARTS]`, `const unsigned int poll_time_us`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/mips/sni/a20r.c`, `sources/distributed-fs/ceph-client/drivers/tty/serial/sccnxp.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/mips/sni/a20r.c`, `sources/distributed-fs/ceph-client/drivers/tty/serial/sccnxp.c`. It
integrates through `struct platform_device` platform data, board files, MFD child registration, and
legacy non-DT setup paths; many modern systems may replace parts of this contract with Device Tree,
ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/serial-sccnxp.h` completely for this pass (84 lines, 1938 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/serial-sccnxp.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/serial-sccnxp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/sgi-w1.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/sgi-w1.h

## Purpose
`sgi-w1.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
sgi_w1_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `PLATFORM_DATA_SGI_W1_H`. Types: `struct sgi_w1_platform_data`. Declared or inline
functions: none visible in this header. Important struct details: struct sgi_w1_platform_data fields
include `char dev_id[64]`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/mips/sgi-ip27/ip27-xtalk.c`, `sources/distributed-fs/ceph-client/arch/mips/sgi-
ip30/ip30-xtalk.c`, `sources/distributed-fs/ceph-client/drivers/mfd/ioc3.c`, `sources/distributed-
fs/ceph-client/drivers/w1/masters/sgi_w1.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/mips/sgi-ip27/ip27-xtalk.c`, `sources/distributed-fs/ceph-client/arch/mips/sgi-
ip30/ip30-xtalk.c`, `sources/distributed-fs/ceph-client/drivers/mfd/ioc3.c`, `sources/distributed-
fs/ceph-client/drivers/w1/masters/sgi_w1.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/sgi-w1.h` completely for this pass (13 lines, 222 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/sgi-w1.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/sgi-w1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/sh_mmcif.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/sh_mmcif.h

## Purpose
`sh_mmcif.h` is a Linux kernel MMC/SD/SDHCI host board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct sh_mmcif_plat_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `LINUX_MMC_SH_MMCIF_H`, `MMCIF_CE_CMD_SET`, `MMCIF_CE_ARG`, `MMCIF_CE_ARG_CMD12`,
`MMCIF_CE_CMD_CTRL`, `MMCIF_CE_BLOCK_SET`, `MMCIF_CE_CLK_CTRL`, `MMCIF_CE_BUF_ACC`,
`MMCIF_CE_RESP3`, `MMCIF_CE_RESP2`, `MMCIF_CE_RESP1`, `MMCIF_CE_RESP0`, `MMCIF_CE_RESP_CMD12`,
`MMCIF_CE_DATA`, and 23 more. Types: `struct sh_mmcif_plat_data`. Declared or inline functions:
`__raw_readl`, `__raw_writel`, `sh_mmcif_writel`, `sh_mmcif_boot_cmd_send`,
`sh_mmcif_boot_cmd_poll`, `sh_mmcif_boot_cmd`, `sh_mmcif_readl`, `sh_mmcif_boot_do_read_single`,
`sh_mmcif_boot_do_read`, `sh_mmcif_boot_init`. Important struct details: struct sh_mmcif_plat_data
fields include `unsigned int slave_id_tx`, `unsigned int slave_id_rx`, `u8 sup_pclk`, `unsigned long
caps`, `u32 ocr`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/sh/boards/mach-ecovec24/setup.c`, `sources/distributed-fs/ceph-
client/arch/sh/boards/board-sh7757lcr.c`, `sources/distributed-fs/ceph-
client/arch/sh/boot/romimage/mmcif-sh7724.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/sh_mmcif.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/io.h`, `linux/platform_device.h`. Direct source-tree consumers found by include
search are `sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/setup.c`,
`sources/distributed-fs/ceph-client/arch/sh/boards/board-sh7757lcr.c`, `sources/distributed-fs/ceph-
client/arch/sh/boot/romimage/mmcif-sh7724.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/sh_mmcif.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/sh_mmcif.h` completely for this pass (207 lines, 5548 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/sh_mmcif.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/sh_mmcif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/shmob_drm.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/shmob_drm.h

## Purpose
`shmob_drm.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct shmob_drm_panel_data`; enumerations such as `enum shmob_drm_clk_source` into the matching
driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__SHMOB_DRM_H__`. Types: `struct shmob_drm_panel_data`, `struct
shmob_drm_interface_data`, `struct shmob_drm_platform_data`, `enum shmob_drm_clk_source`. Declared
or inline functions: none visible in this header. Important struct details: struct
shmob_drm_panel_data fields include `unsigned int width_mm`, `unsigned int height_mm`, `struct
videomode mode`; struct shmob_drm_interface_data fields include `unsigned int bus_fmt`, `unsigned
int clk_div`; struct shmob_drm_platform_data fields include `enum shmob_drm_clk_source clk_source`,
`struct shmob_drm_interface_data iface`, `struct shmob_drm_panel_data panel`. Important enum
details: enum shmob_drm_clk_source values include `SHMOB_DRM_CLK_BUS`, `SHMOB_DRM_CLK_PERIPHERAL`,
`SHMOB_DRM_CLK_EXTERNAL`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/gpu/drm/renesas/shmobile/shmob_drm_drv.h`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `video/videomode.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_drv.h`. It integrates
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/shmob_drm.h` completely for this pass (38 lines, 822 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/shmob_drm.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/shmob_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/shtc1.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/shtc1.h

## Purpose
`shtc1.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
shtc1_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__SHTC1_H_`. Types: `struct shtc1_platform_data`. Declared or inline functions:
none visible in this header. Important struct details: struct shtc1_platform_data fields include
`bool blocking_io`, `bool high_precision`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/hwmon/shtc1.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/hwmon/shtc1.c`. It integrates through `struct platform_device` platform data, board
files, MFD child registration, and legacy non-DT setup paths; many modern systems may replace parts
of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/shtc1.h` completely for this pass (14 lines, 303 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/shtc1.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/shtc1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/si5351.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/si5351.h

## Purpose
`si5351.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
si5351_clkout_config`; enumerations such as `enum si5351_pll_src`, `enum si5351_multisynth_src` into
the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_PLATFORM_DATA_SI5351_H__`. Types: `struct si5351_clkout_config`, `struct
si5351_platform_data`, `enum si5351_pll_src`, `enum si5351_multisynth_src`, `enum
si5351_clkout_src`, `enum si5351_drive_strength`, `enum si5351_disable_state`. Declared or inline
functions: none visible in this header. Important struct details: struct si5351_clkout_config fields
include `enum si5351_multisynth_src multisynth_src`, `enum si5351_clkout_src clkout_src`, `enum
si5351_drive_strength drive`, `enum si5351_disable_state disable_state`, `bool pll_master`, `bool
pll_reset`, `unsigned long rate`; struct si5351_platform_data fields include `enum si5351_pll_src
pll_src[2]`, `bool pll_reset[2]`, `struct si5351_clkout_config clkout[8]`. Important enum details:
enum si5351_pll_src values include `SI5351_PLL_SRC_DEFAULT`, `SI5351_PLL_SRC_XTAL`,
`SI5351_PLL_SRC_CLKIN`; enum si5351_multisynth_src values include `SI5351_MULTISYNTH_SRC_DEFAULT`,
`SI5351_MULTISYNTH_SRC_VCO0`, `SI5351_MULTISYNTH_SRC_VCO1`; enum si5351_clkout_src values include
`SI5351_CLKOUT_SRC_DEFAULT`, `SI5351_CLKOUT_SRC_MSYNTH_N`, `SI5351_CLKOUT_SRC_MSYNTH_0_4`,
`SI5351_CLKOUT_SRC_XTAL`, `SI5351_CLKOUT_SRC_CLKIN`; enum si5351_drive_strength values include
`SI5351_DRIVE_DEFAULT`, `SI5351_DRIVE_2MA`, `SI5351_DRIVE_4MA`, `SI5351_DRIVE_6MA`,
`SI5351_DRIVE_8MA`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/clk/clk-si5351.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/clk/clk-si5351.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/si5351.h` completely for this pass (117 lines, 3733 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/si5351.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/si5351.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/simplefb.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/simplefb.h

## Purpose
`simplefb.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct simplefb_format` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_SIMPLEFB_H__`, `SIMPLEFB_FORMATS`. Types: `struct
simplefb_format`, `struct simplefb_platform_data`. Declared or inline functions: none visible in
this header. Important struct details: struct simplefb_format fields include `const char *name`,
`u32 bits_per_pixel`, `struct fb_bitfield red`, `struct fb_bitfield green`, `struct fb_bitfield
blue`, `struct fb_bitfield transp`, `u32 fourcc`; struct simplefb_platform_data fields include `u32
width`, `u32 height`, `u32 stride`, `const char *format`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/mips/n64/init.c`, `sources/distributed-fs/ceph-client/include/linux/sysfb.h`,
`sources/distributed-fs/ceph-client/drivers/mfd/ls2k-bmc-core.c`, `sources/distributed-fs/ceph-
client/drivers/firmware/google/framebuffer-coreboot.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `drm/drm_fourcc.h`, `linux/fb.h`, `linux/types.h`. Direct source-tree consumers found by
include search are `sources/distributed-fs/ceph-client/arch/mips/n64/init.c`, `sources/distributed-
fs/ceph-client/include/linux/sysfb.h`, `sources/distributed-fs/ceph-client/drivers/mfd/ls2k-bmc-
core.c`, `sources/distributed-fs/ceph-client/drivers/firmware/google/framebuffer-coreboot.c`,
`sources/distributed-fs/ceph-client/drivers/firmware/sysfb_simplefb.c`, `sources/distributed-
fs/ceph-client/drivers/firmware/sysfb.c`, `sources/distributed-fs/ceph-
client/drivers/video/fbdev/simplefb.c`, `sources/distributed-fs/ceph-
client/drivers/gpu/drm/sysfb/simpledrm.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/simplefb.h` completely for this pass (62 lines, 2258 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/simplefb.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/simplefb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/spi-mt65xx.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/spi-mt65xx.h

## Purpose
`spi-mt65xx.h` is a Linux kernel SPI controller board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct mtk_chip_config` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `____LINUX_PLATFORM_DATA_SPI_MTK_H`. Types: `struct mtk_chip_config`. Declared or
inline functions: none visible in this header. Important struct details: struct mtk_chip_config
fields include `u32 sample_sel`, `u32 tick_delay`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/spi/spi-mt65xx.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/spi/spi-mt65xx.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/spi-mt65xx.h` completely for this pass (17 lines, 361 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/spi-mt65xx.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/spi-mt65xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/spi-omap2-mcspi.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/spi-omap2-mcspi.h

## Purpose
`spi-omap2-mcspi.h` is a Linux kernel SPI controller board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct omap2_mcspi_platform_config` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_OMAP2_MCSPI_H`, `OMAP4_MCSPI_REG_OFFSET`, `MCSPI_PINDIR_D0_IN_D1_OUT`,
`MCSPI_PINDIR_D0_OUT_D1_IN`. Types: `struct omap2_mcspi_platform_config`, `struct
omap2_mcspi_device_config`. Declared or inline functions: none visible in this header. Important
struct details: struct omap2_mcspi_platform_config fields include `unsigned short num_cs`, `unsigned
int regs_offset`, `unsigned int pin_dir:1`, `size_t max_xfer_len`; struct omap2_mcspi_device_config
fields include `unsigned turbo_mode:1`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/board-n8x0.c`, `sources/distributed-fs/ceph-client/drivers/spi/spi-
omap2-mcspi.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/board-n8x0.c`, `sources/distributed-fs/ceph-client/drivers/spi/spi-
omap2-mcspi.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/spi-omap2-mcspi.h` completely for this pass (21 lines, 406 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/spi-omap2-mcspi.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/spi-omap2-mcspi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/spi-s3c64xx.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/spi-s3c64xx.h

## Purpose
`spi-s3c64xx.h` is a Linux kernel SPI controller board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct s3c64xx_spi_csinfo` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__SPI_S3C64XX_H`. Types: `struct s3c64xx_spi_csinfo`, `struct s3c64xx_spi_info`.
Declared or inline functions: `int`, `s3c64xx_spi0_set_platdata`, `s3c64xx_spi0_cfg_gpio`. Important
struct details: struct s3c64xx_spi_csinfo fields include `u8 fb_delay`; struct s3c64xx_spi_info
fields include `int src_clk_nr`, `int num_cs`, `bool no_cs`, `bool polling`, `int
(*cfg_gpio)(void)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/devs.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-
crag6410.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-spi-s3c64xx.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410-module.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/dmaengine.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-s3c/devs.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/mach-crag6410.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/setup-spi-s3c64xx.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/mach-crag6410-module.c`, `sources/distributed-fs/ceph-
client/drivers/spi/spi-s3c64xx.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/spi-s3c64xx.h` completely for this pass (58 lines, 1610 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/spi-s3c64xx.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/spi-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/st_sensors_pdata.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/st_sensors_pdata.h

## Purpose
`st_sensors_pdata.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct st_sensors_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `ST_SENSORS_PDATA_H`. Types: `struct st_sensors_platform_data`. Declared or inline
functions: none visible in this header. Important struct details: struct st_sensors_platform_data
fields include `u8 drdy_int_pin`, `bool open_drain`, `bool spi_3wire`, `bool pullups`, `bool
wakeup_source`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/include/linux/iio/common/st_sensors.h`, `sources/distributed-fs/ceph-
client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_core.c`, `sources/distributed-fs/ceph-
client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_buffer.c`, `sources/distributed-fs/ceph-
client/drivers/iio/humidity/hts221_buffer.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/include/linux/iio/common/st_sensors.h`, `sources/distributed-fs/ceph-
client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_core.c`, `sources/distributed-fs/ceph-
client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_buffer.c`, `sources/distributed-fs/ceph-
client/drivers/iio/humidity/hts221_buffer.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/st_sensors_pdata.h` completely for this pass (32 lines, 978 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/st_sensors_pdata.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/st_sensors_pdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/tda9950.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/tda9950.h

## Purpose
`tda9950.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
tda9950_glue` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `LINUX_PLATFORM_DATA_TDA9950_H`. Types: `struct tda9950_glue`. Declared or inline
functions: `int`, `void`. Important struct details: struct tda9950_glue fields include `struct
device *parent`, `unsigned long irq_flags`, `void *data`, `int (*init)(void *)`, `void (*exit)(void
*)`, `int (*open)(void *)`, `void (*release)(void *)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/gpu/drm/bridge/tda998x_drv.c`, `sources/distributed-fs/ceph-
client/drivers/media/cec/i2c/tda9950.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/gpu/drm/bridge/tda998x_drv.c`, `sources/distributed-fs/ceph-
client/drivers/media/cec/i2c/tda9950.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/tda9950.h` completely for this pass (16 lines, 282 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/tda9950.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/tda9950.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ti-prm.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/ti-prm.h

## Purpose
`ti-prm.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
ti_prm_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_LINUX_PLATFORM_DATA_TI_PRM_H`. Types: `struct ti_prm_platform_data`. Declared or
inline functions: `void`. Important struct details: struct ti_prm_platform_data fields include `void
(*clkdm_deny_idle)(struct clockdomain *clkdm)`, `void (*clkdm_allow_idle)(struct clockdomain
*clkdm)`, `struct clockdomain * (*clkdm_lookup)(const char *name)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/pmdomain/ti/omap_prm.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/pdata-quirks.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/pmdomain/ti/omap_prm.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/pdata-quirks.c`. It integrates through `struct platform_device` platform data, board files,
MFD child registration, and legacy non-DT setup paths; many modern systems may replace parts of this
contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/ti-prm.h` completely for this pass (21 lines, 524 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/ti-prm.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ti-prm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ti-sysc.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/ti-sysc.h

## Purpose
`ti-sysc.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
ti_sysc_cookie`; enumerations such as `enum ti_sysc_module_type`, `enum sysc_registers` into the
matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__TI_SYSC_DATA_H__`, `SYSC_MODULE_QUIRK_OTG`, `SYSC_QUIRK_RESET_ON_CTX_LOST`,
`SYSC_QUIRK_REINIT_ON_CTX_LOST`, `SYSC_QUIRK_REINIT_ON_RESUME`, `SYSC_QUIRK_GPMC_DEBUG`,
`SYSC_MODULE_QUIRK_ENA_RESETDONE`, `SYSC_MODULE_QUIRK_PRUSS`, `SYSC_MODULE_QUIRK_DSS_RESET`,
`SYSC_MODULE_QUIRK_RTC_UNLOCK`, `SYSC_QUIRK_CLKDM_NOAUTO`, `SYSC_QUIRK_FORCE_MSTANDBY`,
`SYSC_MODULE_QUIRK_AESS`, `SYSC_MODULE_QUIRK_SGX`, and 18 more. Types: `struct ti_sysc_cookie`,
`struct sysc_regbits`, `struct sysc_capabilities`, `struct sysc_config`, `struct
ti_sysc_module_data`, `struct ti_sysc_platform_data`, `enum ti_sysc_module_type`, `enum
sysc_registers`. Declared or inline functions: `bool`. Important struct details: struct
ti_sysc_cookie fields include `void *data`, `void *clkdm`; struct sysc_regbits fields include `s8
midle_shift`, `s8 clkact_shift`, `s8 sidle_shift`, `s8 enwkup_shift`, `s8 srst_shift`, `s8
autoidle_shift`, `s8 dmadisable_shift`, `s8 emufree_shift`; struct sysc_capabilities fields include
`const enum ti_sysc_module_type type`, `const u32 sysc_mask`, `const struct sysc_regbits *regbits`,
`const u32 mod_quirks`; struct sysc_config fields include `u32 sysc_val`, `u32 syss_mask`, `u8
midlemodes`, `u8 sidlemodes`, `u8 srst_udelay`, `u32 quirks`; struct ti_sysc_module_data fields
include `const char *name`, `u64 module_pa`, `u32 module_size`, `int *offsets`, `int nr_offsets`,
`const struct sysc_capabilities *cap`, `struct sysc_config *cfg`. Important enum details: enum
ti_sysc_module_type values include `TI_SYSC_OMAP2`, `TI_SYSC_OMAP2_TIMER`, `TI_SYSC_OMAP3_SHAM`,
`TI_SYSC_OMAP3_AES`, `TI_SYSC_OMAP4`, `TI_SYSC_OMAP4_TIMER`, `TI_SYSC_OMAP4_SIMPLE`,
`TI_SYSC_OMAP34XX_SR`; enum sysc_registers values include `SYSC_REVISION`, `SYSC_SYSCONFIG`,
`SYSC_SYSSTATUS`, `SYSC_MAX_REGS`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/bus/ti-sysc.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/omap_hwmod.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/omap_hwmod_common_data.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pdata-
quirks.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/bus/ti-sysc.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/omap_hwmod.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
omap2/omap_hwmod_common_data.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pdata-
quirks.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/ti-sysc.h` completely for this pass (171 lines, 5112 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/ti-sysc.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/ti-sysc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/tmio.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/tmio.h

## Purpose
`tmio.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
tmio_mmc_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `MFD_TMIO_H`, `TMIO_MMC_BLKSZ_2BYTES`, `TMIO_MMC_SDIO_IRQ`, `TMIO_MMC_MIN_RCAR2`,
`TMIO_MMC_HAS_IDLE_WAIT`, `TMIO_MMC_USE_BUSY_TIMEOUT`, `TMIO_MMC_HAVE_CMD12_CTRL`,
`TMIO_MMC_SDIO_STATUS_SETBITS`, `TMIO_MMC_32BIT_DATA_PORT`, `TMIO_MMC_CLK_ACTUAL`,
`TMIO_MMC_HAVE_CBSY`, `TMIO_MMC_64BIT_DATA_PORT`. Types: `struct tmio_mmc_data`. Declared or inline
functions: none visible in this header. Important struct details: struct tmio_mmc_data fields
include `void *chan_priv_tx`, `void *chan_priv_rx`, `unsigned int hclk`, `unsigned long
capabilities`, `unsigned long capabilities2`, `unsigned long flags`, `u32 ocr_mask`, `dma_addr_t
dma_rx_offset`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mmc/host/tmio_mmc_core.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/renesas_sdhi_internal_dmac.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/uniphier-sd.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/renesas_sdhi_core.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/platform_device.h`, `linux/types.h`. Direct source-tree consumers found by
include search are `sources/distributed-fs/ceph-client/drivers/mmc/host/tmio_mmc_core.c`,
`sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_internal_dmac.c`,
`sources/distributed-fs/ceph-client/drivers/mmc/host/uniphier-sd.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/renesas_sdhi_core.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/renesas_sdhi_sys_dmac.c`, `sources/distributed-fs/ceph-
client/arch/sh/boards/mach-ap325rxa/setup.c`, `sources/distributed-fs/ceph-
client/arch/sh/boards/mach-kfr2r09/setup.c`, `sources/distributed-fs/ceph-
client/arch/sh/boards/mach-ecovec24/setup.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/tmio.h` completely for this pass (65 lines, 1860 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/tmio.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/tmio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/tps68470.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/tps68470.h

## Purpose
`tps68470.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct tps68470_regulator_platform_data`; enumerations such as `enum tps68470_regulators` into the
matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PDATA_TPS68470_H`. Types: `struct tps68470_regulator_platform_data`, `struct
tps68470_clk_consumer`, `struct tps68470_clk_platform_data`, `enum tps68470_regulators`. Declared or
inline functions: none visible in this header. Important struct details: struct
tps68470_regulator_platform_data fields include `const struct regulator_init_data
*reg_init_data[TPS68470_NUM_REGULATORS]`; struct tps68470_clk_consumer fields include `const char
*consumer_dev_name`, `const char *consumer_con_id`; struct tps68470_clk_platform_data fields include
`unsigned int n_consumers`, `struct tps68470_clk_consumer consumers[]`. Important enum details: enum
tps68470_regulators values include `TPS68470_CORE`, `TPS68470_ANA`, `TPS68470_VCM`, `TPS68470_VIO`,
`TPS68470_VSIO`, `TPS68470_AUX1`, `TPS68470_AUX2`, `TPS68470_NUM_REGULATORS`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/regulator/tps68470-regulator.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/tps68470.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/tps68470_board_data.c`, `sources/distributed-fs/ceph-
client/drivers/clk/clk-tps68470.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/regulator/tps68470-regulator.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/tps68470.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/tps68470_board_data.c`, `sources/distributed-fs/ceph-
client/drivers/clk/clk-tps68470.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/tps68470.h` completely for this pass (40 lines, 785 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/tps68470.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/tps68470.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/tsc2007.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/tsc2007.h

## Purpose
`tsc2007.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
tsc2007_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_I2C_TSC2007_H`. Types: `struct tsc2007_platform_data`. Declared or inline
functions: `int`, `void`. Important struct details: struct tsc2007_platform_data fields include `u16
model`, `u16 x_plate_ohms`, `u16 max_rt`, `unsigned long poll_period`, `int fuzzx`, `int fuzzy`,
`int fuzzz`, `int (*get_pendown_state)(struct device *)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/sh/boards/mach-ecovec24/setup.c`, `sources/distributed-fs/ceph-
client/drivers/input/touchscreen/tsc2007_core.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/sh/boards/mach-ecovec24/setup.c`, `sources/distributed-fs/ceph-
client/drivers/input/touchscreen/tsc2007_core.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/tsc2007.h` completely for this pass (23 lines, 655 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/tsc2007.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/tsc2007.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/tsl2772.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/tsl2772.h

## Purpose
`tsl2772.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
tsl2772_lux` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__TSL2772_H`, `TSL2772_MAX_LUX_TABLE_SIZE`, `TSL2772_DEF_LUX_TABLE_SZ`,
`TSL2772_DEFAULT_TABLE_BYTES`, `TSL2772_DIODE0`, `TSL2772_DIODE1`, `TSL2772_DIODE_BOTH`,
`TSL2772_100_mA`, `TSL2772_50_mA`, `TSL2772_25_mA`, `TSL2772_13_mA`. Types: `struct tsl2772_lux`,
`struct tsl2772_settings`, `struct tsl2772_platform_data`. Declared or inline functions: none
visible in this header. Important struct details: struct tsl2772_lux fields include `unsigned int
ch0`, `unsigned int ch1`; struct tsl2772_settings fields include `int als_time`, `int als_gain`,
`int als_gain_trim`, `int wait_time`, `int prox_time`, `int prox_gain`, `int als_prox_config`, `int
als_cal_target`; struct tsl2772_platform_data fields include `struct tsl2772_lux
platform_lux_table[TSL2772_MAX_LUX_TABLE_SIZE]`, `struct tsl2772_settings
*platform_default_settings`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/iio/light/tsl2772.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/iio/light/tsl2772.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/tsl2772.h` completely for this pass (101 lines, 3819 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/tsl2772.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/tsl2772.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/txx9/ndfmc.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/txx9/ndfmc.h

## Purpose
`ndfmc.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
txx9ndfmc_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__TXX9_NDFMC_H`, `NDFMC_PLAT_FLAG_USE_BSPRT`, `NDFMC_PLAT_FLAG_NO_RSTR`,
`NDFMC_PLAT_FLAG_HOLDADD`, `NDFMC_PLAT_FLAG_DUMMYWRITE`. Types: `struct txx9ndfmc_platform_data`.
Declared or inline functions: none visible in this header. Important struct details: struct
txx9ndfmc_platform_data fields include `unsigned int shift`, `unsigned int gbus_clock`, `unsigned
int hold`, `unsigned int spw`, `unsigned int flags`, `unsigned char ch_mask`, `unsigned char
wp_mask`, `unsigned char wide_mask`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/mips/txx9/generic/setup_tx4938.c`, `sources/distributed-fs/ceph-
client/arch/mips/txx9/generic/setup.c`, `sources/distributed-fs/ceph-
client/drivers/mtd/nand/raw/txx9ndfmc.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/mips/txx9/generic/setup_tx4938.c`, `sources/distributed-fs/ceph-
client/arch/mips/txx9/generic/setup.c`, `sources/distributed-fs/ceph-
client/drivers/mtd/nand/raw/txx9ndfmc.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/txx9/ndfmc.h` completely for this pass (28 lines, 806 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/txx9/ndfmc.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/txx9/ndfmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/uio_dmem_genirq.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/uio_dmem_genirq.h

## Purpose
`uio_dmem_genirq.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct uio_dmem_genirq_pdata` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_UIO_DMEM_GENIRQ_H`. Types: `struct uio_dmem_genirq_pdata`. Declared or inline
functions: none visible in this header. Important struct details: struct uio_dmem_genirq_pdata
fields include `struct uio_info uioinfo`, `unsigned int *dynamic_region_sizes`, `unsigned int
num_dynamic_regions`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/uio/uio_dmem_genirq.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/uio_driver.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/uio/uio_dmem_genirq.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/uio_dmem_genirq.h` completely for this pass (18 lines, 397 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/uio_dmem_genirq.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/uio_dmem_genirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ehci-orion.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ehci-orion.h

## Purpose
`usb-ehci-orion.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct orion_ehci_data`; enumerations such as `enum orion_ehci_phy_ver` into the matching
driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__USB_EHCI_ORION_H`. Types: `struct orion_ehci_data`, `enum orion_ehci_phy_ver`.
Declared or inline functions: none visible in this header. Important struct details: struct
orion_ehci_data fields include `enum orion_ehci_phy_ver phy_version`. Important enum details: enum
orion_ehci_phy_ver values include `EHCI_PHY_ORION`, `EHCI_PHY_DD`, `EHCI_PHY_KW`, `EHCI_PHY_NA`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/usb/host/ehci-orion.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
dove/common.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/mbus.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-orion.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-dove/common.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
orion5x/common.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.c`,
`sources/distributed-fs/ceph-client/arch/arm/plat-orion/common.c`, `sources/distributed-fs/ceph-
client/arch/arm/plat-orion/include/plat/common.h`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ehci-orion.h` completely for this pass (24 lines, 440 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ehci-orion.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ehci-orion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb-musb-ux500.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/usb-musb-ux500.h

## Purpose
`usb-musb-ux500.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct ux500_musb_board_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__ASM_ARCH_USB_H`, `UX500_MUSB_DMA_NUM_RX_TX_CHANNELS`. Types: `struct
ux500_musb_board_data`. Declared or inline functions: `bool`. Important struct details: struct
ux500_musb_board_data fields include `void **dma_rx_param_array`, `void **dma_tx_param_array`, `bool
(*dma_filter)(struct dma_chan *chan, void *filter_param)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/usb/musb/ux500_dma.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/dmaengine.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/usb/musb/ux500_dma.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/usb-musb-ux500.h` completely for this pass (22 lines, 558 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/usb-musb-ux500.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb-musb-ux500.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-pxa27x.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-pxa27x.h

## Purpose
`usb-ohci-pxa27x.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct pxaohci_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `ASMARM_ARCH_OHCI_H`, `ENABLE_PORT1`, `ENABLE_PORT2`, `ENABLE_PORT3`,
`ENABLE_PORT_ALL`, `POWER_SENSE_LOW`, `POWER_CONTROL_LOW`, `NO_OC_PROTECTION`, `OC_MODE_GLOBAL`,
`OC_MODE_PERPORT`, `PMM_NPS_MODE`, `PMM_GLOBAL_MODE`, `PMM_PERPORT_MODE`. Types: `struct
pxaohci_platform_data`. Declared or inline functions: `int`, `void`, `pxa_set_ohci_info`. Important
struct details: struct pxaohci_platform_data fields include `int (*init)(struct device *)`, `void
(*exit)(struct device *)`, `unsigned long flags`, `int power_on_delay`, `int port_mode`, `int
power_budget`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/pxa3xx.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/spitz.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/pxa3xx.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/spitz.c`, `sources/distributed-fs/ceph-client/drivers/usb/host/ohci-
pxa27x.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-pxa27x.h` completely for this pass (37 lines, 925 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-pxa27x.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-pxa27x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-s3c2410.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-s3c2410.h

## Purpose
`usb-ohci-s3c2410.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct s3c2410_hcd_port` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__ASM_ARCH_USBCONTROL_H`, `S3C_HCDFLG_USED`. Types: `struct s3c2410_hcd_port`,
`struct s3c2410_hcd_info`. Declared or inline functions: `void`, `s3c_ohci_set_platdata`,
`s3c2410_usb_report_oc`. Important struct details: struct s3c2410_hcd_port fields include `unsigned
char flags`, `unsigned char power`, `unsigned char oc_status`, `unsigned char oc_changed`; struct
s3c2410_hcd_info fields include `struct usb_hcd *hcd`, `struct s3c2410_hcd_port port[2]`, `void
(*power_control)(int port, int to)`, `void (*enable_oc)(struct s3c2410_hcd_info *, int on)`, `void
(*report_oc)(struct s3c2410_hcd_info *, int ports)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/usb/host/ohci-s3c2410.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/usb/host/ohci-s3c2410.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-s3c2410.h` completely for this pass (40 lines, 941 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-s3c2410.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb-ohci-s3c2410.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap.h

## Purpose
`usb-omap.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct usbtll_omap_platform_data`; enumerations such as `enum usbhs_omap_port_mode`, `enum
musb_interface` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `OMAP3_HS_USB_PORTS`. Types: `struct usbtll_omap_platform_data`, `struct
ehci_hcd_omap_platform_data`, `struct ohci_hcd_omap_platform_data`, `struct
usbhs_omap_platform_data`, `struct omap_musb_board_data`, `enum usbhs_omap_port_mode`, `enum
musb_interface`. Declared or inline functions: `void`. Important struct details: struct
usbtll_omap_platform_data fields include `enum usbhs_omap_port_mode port_mode[OMAP3_HS_USB_PORTS]`;
struct ehci_hcd_omap_platform_data fields include `enum usbhs_omap_port_mode
port_mode[OMAP3_HS_USB_PORTS]`, `int reset_gpio_port[OMAP3_HS_USB_PORTS]`, `struct regulator
*regulator[OMAP3_HS_USB_PORTS]`, `unsigned phy_reset:1`; struct ohci_hcd_omap_platform_data fields
include `enum usbhs_omap_port_mode port_mode[OMAP3_HS_USB_PORTS]`, `unsigned es2_compatibility:1`;
struct usbhs_omap_platform_data fields include `int nports`, `enum usbhs_omap_port_mode
port_mode[OMAP3_HS_USB_PORTS]`, `int reset_gpio_port[OMAP3_HS_USB_PORTS]`, `struct regulator
*regulator[OMAP3_HS_USB_PORTS]`, `struct ehci_hcd_omap_platform_data *ehci_data`, `struct
ohci_hcd_omap_platform_data *ohci_data`, `unsigned single_ulpi_bypass:1`, `unsigned
es2_compatibility:1`; struct omap_musb_board_data fields include `u8 interface_type`, `u8 mode`,
`u16 power`, `unsigned extvbus:1`, `void (*set_phy_power)(u8 on)`, `void (*clear_irq)(void)`, `void
(*set_mode)(u8 mode)`, `void (*reset)(void)`. Important enum details: enum usbhs_omap_port_mode
values include `OMAP_USBHS_PORT_MODE_UNUSED`, `OMAP_EHCI_PORT_MODE_PHY`, `OMAP_EHCI_PORT_MODE_TLL`,
`OMAP_EHCI_PORT_MODE_HSIC`, `OMAP_OHCI_PORT_MODE_PHY_6PIN_DATSE0`,
`OMAP_OHCI_PORT_MODE_PHY_6PIN_DPDM`, `OMAP_OHCI_PORT_MODE_PHY_3PIN_DATSE0`,
`OMAP_OHCI_PORT_MODE_PHY_4PIN_DPDM`; enum musb_interface values include `MUSB_INTERFACE_ULPI`,
`MUSB_INTERFACE_UTMI`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/usb-tusb6010.c`, `sources/distributed-fs/ceph-client/drivers/mfd/omap-
usb-tll.c`, `sources/distributed-fs/ceph-client/drivers/mfd/omap-usb-host.c`, `sources/distributed-
fs/ceph-client/drivers/usb/host/ehci-omap.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/usb-tusb6010.c`, `sources/distributed-fs/ceph-client/drivers/mfd/omap-
usb-tll.c`, `sources/distributed-fs/ceph-client/drivers/mfd/omap-usb-host.c`, `sources/distributed-
fs/ceph-client/drivers/usb/host/ehci-omap.c`, `sources/distributed-fs/ceph-
client/drivers/usb/musb/omap2430.h`, `sources/distributed-fs/ceph-
client/drivers/usb/musb/musb_dsps.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap.h` completely for this pass (74 lines, 1981 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap1.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap1.h

## Purpose
`usb-omap1.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct omap_usb_config` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_USB_OMAP1_H`. Types: `struct omap_usb_config`. Declared or inline
functions: `u32`, `int`, `void`. Important struct details: struct omap_usb_config fields include
`unsigned register_host:1`, `unsigned register_dev:1`, `u8 otg`, `const char *extcon`, `u8
hmc_mode`, `u8 rwc`, `u8 pins[3]`, `struct platform_device *udc_device`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap1/usb.h`, `sources/distributed-fs/ceph-
client/drivers/usb/gadget/udc/omap_udc.c`, `sources/distributed-fs/ceph-
client/drivers/usb/host/ohci-omap.c`, `sources/distributed-fs/ceph-client/drivers/usb/phy/phy-omap-
otg.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/platform_device.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-omap1/usb.h`, `sources/distributed-fs/ceph-
client/drivers/usb/gadget/udc/omap_udc.c`, `sources/distributed-fs/ceph-
client/drivers/usb/host/ohci-omap.c`, `sources/distributed-fs/ceph-client/drivers/usb/phy/phy-omap-
otg.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap1.h` completely for this pass (57 lines, 1567 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap1.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb-omap1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb3503.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/usb3503.h

## Purpose
`usb3503.h` is a Linux kernel USB host/device/PHY board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct usb3503_platform_data`; enumerations such as `enum usb3503_mode` into the matching driver at
probe time.

## Important APIs, types, and functions
Macros/constants: `__USB3503_H__`, `USB3503_I2C_NAME`, `USB3503_OFF_PORT1`, `USB3503_OFF_PORT2`,
`USB3503_OFF_PORT3`. Types: `struct usb3503_platform_data`, `enum usb3503_mode`. Declared or inline
functions: none visible in this header. Important struct details: struct usb3503_platform_data
fields include `enum usb3503_mode initial_mode`, `u8 port_off_mask`. Important enum details: enum
usb3503_mode values include `USB3503_MODE_UNKNOWN`, `USB3503_MODE_HUB`, `USB3503_MODE_STANDBY`,
`USB3503_MODE_BYPASS`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/usb/misc/usb3503.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/usb/misc/usb3503.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/usb3503.h` completely for this pass (23 lines, 431 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/usb3503.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/usb3503.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/video-ep93xx.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/video-ep93xx.h

## Purpose
`video-ep93xx.h` is a Linux kernel display or framebuffer board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct ep93xxfb_mach_info` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__VIDEO_EP93XX_H`, `EP93XXFB_STATE_MACHINE_ENABLE`,
`EP93XXFB_PIXEL_CLOCK_ENABLE`, `EP93XXFB_VSYNC_ENABLE`, `EP93XXFB_PIXEL_DATA_ENABLE`,
`EP93XXFB_COMPOSITE_SYNC`, `EP93XXFB_SYNC_VERT_HIGH`, `EP93XXFB_SYNC_HORIZ_HIGH`,
`EP93XXFB_SYNC_BLANK_HIGH`, `EP93XXFB_PCLK_FALLING`, `EP93XXFB_ENABLE_AC`, `EP93XXFB_ENABLE_LCD`,
`EP93XXFB_ENABLE_CCIR`, `EP93XXFB_USE_PARALLEL_INTERFACE`, and 11 more. Types: `struct
ep93xxfb_mach_info`. Declared or inline functions: `int`, `void`. Important struct details: struct
ep93xxfb_mach_info fields include `unsigned int flags`, `int (*setup)(struct platform_device
*pdev)`, `void (*teardown)(struct platform_device *pdev)`, `void (*blank)(int blank_mode, struct
fb_info *info)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/video/fbdev/ep93xx-fb.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/video/fbdev/ep93xx-fb.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/video-ep93xx.h` completely for this pass (45 lines, 1525 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/video-ep93xx.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/video-ep93xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/video-pxafb.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/video-pxafb.h

## Purpose
`video-pxafb.h` is a Linux kernel display or framebuffer board-data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct pxafb_mode_info` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `LCD_CONN_TYPE`, `LCD_CONN_WIDTH`, `LCD_TYPE_MASK`, `LCD_TYPE_UNKNOWN`,
`LCD_TYPE_MONO_STN`, `LCD_TYPE_MONO_DSTN`, `LCD_TYPE_COLOR_STN`, `LCD_TYPE_COLOR_DSTN`,
`LCD_TYPE_COLOR_TFT`, `LCD_TYPE_SMART_PANEL`, `LCD_TYPE_MAX`, `LCD_MONO_STN_4BPP`,
`LCD_MONO_STN_8BPP`, `LCD_MONO_DSTN_8BPP`, and 27 more. Types: `struct pxafb_mode_info`, `struct
pxafb_mach_info`. Declared or inline functions: `void`, `pxa_set_fb_info`, `pxafb_smart_queue`,
`pxafb_smart_flush`. Important struct details: struct pxafb_mode_info fields include `u_long
pixclock`, `u_short xres`, `u_short yres`, `u_char bpp`, `unused:22`, `u_char hsync_len`, `u_char
left_margin`, `u_char right_margin`; struct pxafb_mach_info fields include `struct pxafb_mode_info
*modes`, `unsigned int num_modes`, `unsigned int lcd_conn`, `unsigned long video_mem_size`,
`unused:28`, `u_int lccr0`, `u_int lccr3`, `u_int lccr4`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/am300epd.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-
pxa/devices.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am200epd.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/fb.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am300epd.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-pxa/devices.c`, `sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.c`,
`sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am200epd.c`, `sources/distributed-fs/ceph-
client/drivers/video/fbdev/pxafb.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/video-pxafb.h` completely for this pass (189 lines, 6141 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/video-pxafb.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/video-pxafb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/video_s3c.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/video_s3c.h

## Purpose
`video_s3c.h` is a Linux kernel display or framebuffer board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct s3c_fb_pd_win` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_VIDEO_S3C`, `S3C_FB_MAX_WIN`. Types: `struct s3c_fb_pd_win`,
`struct s3c_fb_platdata`. Declared or inline functions: `void`. Important struct details: struct
s3c_fb_pd_win fields include `unsigned short default_bpp`, `unsigned short max_bpp`, `unsigned short
xres`, `unsigned short yres`, `unsigned short virtual_x`, `unsigned short virtual_y`; struct
s3c_fb_platdata fields include `void (*setup_gpio)(void)`, `struct s3c_fb_pd_win
*win[S3C_FB_MAX_WIN]`, `struct fb_videomode *vtiming`, `u32 vidcon0`, `u32 vidcon1`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/fb.h`, `sources/distributed-fs/ceph-client/drivers/video/fbdev/s3c-fb.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-s3c/fb.h`, `sources/distributed-fs/ceph-client/drivers/video/fbdev/s3c-fb.c`.
It integrates through `struct platform_device` platform data, board files, MFD child registration,
and legacy non-DT setup paths; many modern systems may replace parts of this contract with Device
Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/video_s3c.h` completely for this pass (55 lines, 1756 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/video_s3c.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/video_s3c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/voltage-omap.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/voltage-omap.h

## Purpose
`voltage-omap.h` is a Linux kernel TI OMAP platform integration data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct omap_volt_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__ARCH_ARM_OMAP_VOLTAGE_H`. Types: `struct omap_volt_data`. Declared or inline
functions: `voltdm_get_voltage`. Important struct details: struct omap_volt_data fields include `u32
volt_nominal`, `u32 sr_efuse_offs`, `u8 sr_errminlimit`, `u8 vp_errgain`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/voltage.h`, `sources/distributed-fs/ceph-
client/include/linux/power/smartreflex.h`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/voltage.h`, `sources/distributed-fs/ceph-
client/include/linux/power/smartreflex.h`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/voltage-omap.h` completely for this pass (35 lines, 1101 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/voltage-omap.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/voltage-omap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/wilco-ec.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/wilco-ec.h

## Purpose
`wilco-ec.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct wilco_ec_device`; enumerations such as `enum wilco_ec_msg_type` into the matching driver at
probe time.

## Important APIs, types, and functions
Macros/constants: `WILCO_EC_H`, `WILCO_EC_FLAG_NO_RESPONSE`, `EC_MAILBOX_DATA_SIZE`,
`WILCO_EC_PROPERTY_MAX_SIZE`. Types: `struct wilco_ec_device`, `struct wilco_ec_request`, `struct
wilco_ec_message`, `struct wilco_ec_property_msg`, `enum wilco_ec_msg_type`. Declared or inline
functions: `wilco_ec_mailbox`, `wilco_keyboard_leds_init`, `wilco_ec_add_sysfs`,
`wilco_ec_remove_sysfs`. Important struct details: struct wilco_ec_device fields include `struct
device *dev`, `struct mutex mailbox_lock`, `struct resource *io_command`, `struct resource
*io_data`, `struct resource *io_packet`, `void *data_buffer`, `size_t data_size`, `struct
platform_device *debugfs_pdev`; struct wilco_ec_request fields include `u8 struct_version`, `u8
checksum`, `u16 mailbox_id`, `u8 mailbox_version`, `u8 reserved`, `u16 data_size`, `} __packed`, `u8
struct_version`; struct wilco_ec_message fields include `enum wilco_ec_msg_type type`, `u8 flags`,
`size_t request_size`, `void *request_data`, `size_t response_size`, `void *response_data`; struct
wilco_ec_property_msg fields include `u32 property_id`, `int length`, `u8
data[WILCO_EC_PROPERTY_MAX_SIZE]`. Important enum details: enum wilco_ec_msg_type values include
`WILCO_EC_MSG_LEGACY`, `WILCO_EC_MSG_PROPERTY`, `WILCO_EC_MSG_TELEMETRY`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/rtc/rtc-wilco-ec.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/core.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/properties.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/mailbox.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/mutex.h`, `linux/types.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/drivers/rtc/rtc-wilco-ec.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/core.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/properties.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/mailbox.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/debugfs.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/keyboard_leds.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/sysfs.c`, `sources/distributed-fs/ceph-
client/drivers/platform/chrome/wilco_ec/telemetry.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/wilco-ec.h` completely for this pass (225 lines, 7076 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/wilco-ec.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/wilco-ec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/wiznet.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/wiznet.h

## Purpose
`wiznet.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
wiznet_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `PLATFORM_DATA_WIZNET_H`, `CONFIG_WIZNET_BUS_SHIFT`, `W5100_BUS_DIRECT_SIZE`,
`W5300_BUS_DIRECT_SIZE`. Types: `struct wiznet_platform_data`. Declared or inline functions: none
visible in this header. Important struct details: struct wiznet_platform_data fields include `int
link_gpio`, `u8 mac_addr[ETH_ALEN]`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/net/ethernet/wiznet/w5300.c`, `sources/distributed-fs/ceph-
client/drivers/net/ethernet/wiznet/w5100.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/if_ether.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/w5300.c`, `sources/distributed-
fs/ceph-client/drivers/net/ethernet/wiznet/w5100.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/wiznet.h` completely for this pass (23 lines, 511 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/wiznet.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/wiznet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/wkup_m3.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/wkup_m3.h

## Purpose
`wkup_m3.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
wkup_m3_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_LINUX_PLATFORM_DATA_WKUP_M3_H`. Types: `struct wkup_m3_platform_data`. Declared
or inline functions: `int`. Important struct details: struct wkup_m3_platform_data fields include
`const char *reset_name`, `int (*assert_reset)(struct platform_device *pdev, const char *name)`,
`int (*deassert_reset)(struct platform_device *pdev, const char *name)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/pdata-quirks.c`, `sources/distributed-fs/ceph-
client/drivers/remoteproc/wkup_m3_rproc.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/arch/arm/mach-omap2/pdata-quirks.c`, `sources/distributed-fs/ceph-
client/drivers/remoteproc/wkup_m3_rproc.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/wkup_m3.h` completely for this pass (22 lines, 542 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/wkup_m3.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/wkup_m3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/amd-fch.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/amd-fch.h

## Purpose
`amd-fch.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing macros, constants,
or function prototypes into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_ASM_X86_AMD_FCH_H_`, `FCH_PM_BASE`, `FCH_PM_DECODEEN`,
`FCH_PM_DECODEEN_SMBUS0SEL`, `FCH_PM_SCRATCH`, `FCH_PM_S5_RESET_STATUS`. Types: none visible in this
header. Declared or inline functions: none visible in this header.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/amd/pmc/pmc-quirks.c`, `sources/distributed-fs/ceph-
client/drivers/i2c/busses/i2c-piix4.c`, `sources/distributed-fs/ceph-
client/arch/x86/kernel/cpu/amd.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/platform/x86/amd/pmc/pmc-quirks.c`, `sources/distributed-fs/ceph-
client/drivers/i2c/busses/i2c-piix4.c`, `sources/distributed-fs/ceph-
client/arch/x86/kernel/cpu/amd.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/amd-fch.h` completely for this pass (13 lines, 349 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/amd-fch.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/amd-fch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/apple.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/apple.h

## Purpose
`apple.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing macros, constants,
or function prototypes into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `PLATFORM_DATA_X86_APPLE_H`, `x86_apple_machine`. Types: none visible in this
header. Declared or inline functions: none visible in this header.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/bluetooth/hci_bcm.c`, `sources/distributed-fs/ceph-client/drivers/acpi/sbs.c`,
`sources/distributed-fs/ceph-client/drivers/acpi/scan.c`, `sources/distributed-fs/ceph-
client/drivers/acpi/osi.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/bluetooth/hci_bcm.c`, `sources/distributed-fs/ceph-client/drivers/acpi/sbs.c`,
`sources/distributed-fs/ceph-client/drivers/acpi/scan.c`, `sources/distributed-fs/ceph-
client/drivers/acpi/osi.c`, `sources/distributed-fs/ceph-client/drivers/acpi/x86/apple.c`,
`sources/distributed-fs/ceph-client/drivers/acpi/pci_root.c`, `sources/distributed-fs/ceph-
client/arch/x86/kernel/early-quirks.c`, `sources/distributed-fs/ceph-
client/arch/x86/kernel/quirks.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/apple.h` completely for this pass (13 lines, 248 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/apple.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/apple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/asus-wmi.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/asus-wmi.h

## Purpose
`asus-wmi.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct asus_hid_listener`; enumerations such as `enum asus_ally_mcu_hack`, `enum asus_hid_event`
into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_ASUS_WMI_H`, `ASUS_WMI_MGMT_GUID`, `ASUS_ACPI_UID_ASUSWMI`,
`ASUS_WMI_METHODID_SPEC`, `ASUS_WMI_METHODID_SFBD`, `ASUS_WMI_METHODID_GLCD`,
`ASUS_WMI_METHODID_GPID`, `ASUS_WMI_METHODID_QMOD`, `ASUS_WMI_METHODID_SPLV`,
`ASUS_WMI_METHODID_AGFN`, `ASUS_WMI_METHODID_SFUN`, `ASUS_WMI_METHODID_SDSP`,
`ASUS_WMI_METHODID_GDSP`, `ASUS_WMI_METHODID_DEVP`, and 96 more. Types: `struct asus_hid_listener`,
`enum asus_ally_mcu_hack`, `enum asus_hid_event`. Declared or inline functions: `void`,
`set_ally_mcu_hack`, `set_ally_mcu_powersave`, `asus_wmi_get_devstate_dsts`,
`asus_wmi_set_devstate`, `asus_wmi_evaluate_method`, `asus_hid_register_listener`,
`asus_hid_unregister_listener`, `asus_hid_event`. Important struct details: struct asus_hid_listener
fields include `struct list_head list`, `void (*brightness_set)(struct asus_hid_listener *listener,
int brightness)`. Important enum details: enum asus_ally_mcu_hack values include
`ASUS_WMI_ALLY_MCU_HACK_INIT`, `ASUS_WMI_ALLY_MCU_HACK_ENABLED`, `ASUS_WMI_ALLY_MCU_HACK_DISABLED`;
enum asus_hid_event values include `ASUS_EV_BRTUP`, `ASUS_EV_BRTDOWN`, `ASUS_EV_BRTTOGGLE`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/asus-wmi.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/asus-armoury.c`, `sources/distributed-fs/ceph-client/drivers/hid/hid-
asus.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/errno.h`, `linux/types.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wmi.c`, `sources/distributed-
fs/ceph-client/drivers/platform/x86/asus-armoury.c`, `sources/distributed-fs/ceph-
client/drivers/hid/hid-asus.c`. It integrates through `struct platform_device` platform data, board
files, MFD child registration, and legacy non-DT setup paths; many modern systems may replace parts
of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/asus-wmi.h` completely for this pass (232 lines, 8128 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/asus-wmi.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/asus-wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/clk-lpss.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/clk-lpss.h

## Purpose
`clk-lpss.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct lpss_clk_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__CLK_LPSS_H`. Types: `struct lpss_clk_data`. Declared or inline functions:
`lpss_atom_clk_init`. Important struct details: struct lpss_clk_data fields include `const char
*name`, `struct clk *clk`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/acpi/x86/lpss.c`, `sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lpss-
atom.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/acpi/x86/lpss.c`, `sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lpss-
atom.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/clk-lpss.h` completely for this pass (20 lines, 418 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/clk-lpss.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/clk-lpss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/clk-pmc-atom.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/clk-pmc-atom.h

## Purpose
`clk-pmc-atom.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct pmc_clk` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_CLK_PMC_ATOM_H`. Types: `struct pmc_clk`, `struct
pmc_clk_data`. Declared or inline functions: none visible in this header. Important struct details:
struct pmc_clk fields include `const char *name`, `unsigned long freq`, `const char *parent_name`;
struct pmc_clk_data fields include `void __iomem *base`, `const struct pmc_clk *clks`, `bool
critical`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/pmc_atom.c`, `sources/distributed-fs/ceph-client/drivers/clk/x86/clk-
pmc-atom.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/platform/x86/pmc_atom.c`, `sources/distributed-fs/ceph-client/drivers/clk/x86/clk-
pmc-atom.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/clk-pmc-atom.h` completely for this pass (39 lines, 1020 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/clk-pmc-atom.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/clk-pmc-atom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/int3472.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/int3472.h

## Purpose
`int3472.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct int3472_cldb` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_INT3472_H`, `I2C_DEV_NAME_FORMAT`, `INT3472_GPIO_TYPE_RESET`,
`INT3472_GPIO_TYPE_POWERDOWN`, `INT3472_GPIO_TYPE_STROBE`, `INT3472_GPIO_TYPE_POWER_ENABLE`,
`INT3472_GPIO_TYPE_CLK_ENABLE`, `INT3472_GPIO_TYPE_PRIVACY_LED`, `INT3472_GPIO_TYPE_DOVDD`,
`INT3472_GPIO_TYPE_HANDSHAKE`, `INT3472_GPIO_TYPE_HOTPLUG_DETECT`, `INT3472_PDEV_MAX_NAME_LEN`,
`INT3472_MAX_SENSOR_GPIOS`, `INT3472_MAX_LEDS`, and 11 more. Types: `struct int3472_cldb`, `struct
int3472_discrete_quirks`, `struct int3472_gpio_regulator`, `struct int3472_discrete_device`.
Declared or inline functions: `skl_int3472_fill_cldb`, `int3472_discrete_parse_crs`,
`int3472_discrete_cleanup`, `skl_int3472_register_dsm_clock`, `skl_int3472_unregister_clock`,
`skl_int3472_unregister_regulator`, `skl_int3472_unregister_leds`. Important struct details: struct
int3472_cldb fields include `u8 version`, `u8 control_logic_type`, `u8 control_logic_id`, `u8
sensor_card_sku`, `u8 reserved[10]`, `u8 clock_source`, `u8 reserved2[17]`; struct
int3472_discrete_quirks fields include `const char *avdd_second_sensor`; struct
int3472_gpio_regulator fields include `struct regulator_consumer_supply
supply_map[GPIO_REGULATOR_SUPPLY_MAP_COUNT * 2]`, `char supply_name_upper[GPIO_SUPPLY_NAME_LENGTH]`,
`char regulator_name[GPIO_REGULATOR_NAME_LENGTH]`, `struct regulator_dev *rdev`, `struct
regulator_desc rdesc`; struct int3472_discrete_device fields include `struct acpi_device *adev`,
`struct device *dev`, `struct acpi_device *sensor`, `const char *sensor_name`, `struct
int3472_gpio_regulator regulators[INT3472_MAX_REGULATORS]`, `struct clk *clk`, `struct clk_hw
clk_hw`, `struct clk_lookup *cl`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/led.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/discrete.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/discrete_quirks.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/common.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/clk-provider.h`, `linux/gpio/machine.h`, `linux/leds.h`,
`linux/regulator/driver.h`, `linux/regulator/machine.h`, `linux/types.h`. Direct source-tree
consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/led.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/discrete.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/discrete_quirks.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/common.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/tps68470.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int3472/clk_and_regulator.c`, `sources/distributed-fs/ceph-
client/drivers/staging/media/atomisp/pci/atomisp_csi2_bridge.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/int3472.h` completely for this pass (171 lines, 5351 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/int3472.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/int3472.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel-mid_wdt.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel-mid_wdt.h

## Purpose
`intel-mid_wdt.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct intel_mid_wdt_pdata` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_X86_INTEL_MID_WDT_H_`. Types: `struct intel_mid_wdt_pdata`. Declared
or inline functions: `int`. Important struct details: struct intel_mid_wdt_pdata fields include `int
irq`, `int (*probe)(struct platform_device *pdev)`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel_scu_wdt.c`, `sources/distributed-fs/ceph-
client/drivers/watchdog/intel-mid_wdt.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/platform_device.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_wdt.c`, `sources/distributed-
fs/ceph-client/drivers/watchdog/intel-mid_wdt.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel-mid_wdt.h` completely for this pass (19 lines, 494 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel-mid_wdt.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel-mid_wdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_pmc_ipc.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_pmc_ipc.h

## Purpose
`intel_pmc_ipc.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct pmc_ipc_cmd` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `INTEL_PMC_IPC_H`, `IPC_SOC_REGISTER_ACCESS`, `IPC_SOC_SUB_CMD_READ`,
`IPC_SOC_SUB_CMD_WRITE`, `PMC_IPCS_PARAM_COUNT`, `VALID_IPC_RESPONSE`. Types: `struct pmc_ipc_cmd`,
`struct pmc_ipc_rbuf`. Declared or inline functions: `intel_pmc_ipc`. Important struct details:
struct pmc_ipc_cmd fields include `u32 cmd`, `u32 sub_cmd`, `u32 size`, `u32 wbuf[4]`; struct
pmc_ipc_rbuf fields include `u32 buf[4]`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/acpi.h`, `linux/cleanup.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel.c`. It
integrates through `struct platform_device` platform data, board files, MFD child registration, and
legacy non-DT setup paths; many modern systems may replace parts of this contract with Device Tree,
ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_pmc_ipc.h` completely for this pass (98 lines, 2418 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_pmc_ipc.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_pmc_ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_scu_ipc.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_scu_ipc.h

## Purpose
`intel_scu_ipc.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct intel_scu_ipc_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_X86_INTEL_SCU_IPC_H_`, `intel_scu_ipc_register`,
`devm_intel_scu_ipc_register`. Types: `struct intel_scu_ipc_data`. Declared or inline functions:
`intel_scu_ipc_unregister`, `intel_scu_ipc_dev_put`, `intel_scu_ipc_dev_command`. Important struct
details: struct intel_scu_ipc_data fields include `struct resource mem`, `int irq`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/x86/platform/intel-mid/intel-mid.c`, `sources/distributed-fs/ceph-
client/arch/x86/include/asm/intel_telemetry.h`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel_scu_ipc.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel_scu_ipcutil.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/init.h`, `linux/ioport.h`, `linux/types.h`. Direct source-tree consumers found by
include search are `sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/intel-mid.c`,
`sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_telemetry.h`, `sources/distributed-
fs/ceph-client/drivers/platform/x86/intel_scu_ipc.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel_scu_ipcutil.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel_scu_pcidrv.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel_scu_pltdrv.c`, `sources/distributed-fs/ceph-
client/drivers/mfd/intel_soc_pmic_mrfld.c`, `sources/distributed-fs/ceph-
client/drivers/mfd/intel_pmc_bxt.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_scu_ipc.h` completely for this pass (72 lines, 2310 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_scu_ipc.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/intel_scu_ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/nvidia-wmi-ec-backlight.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/nvidia-wmi-ec-backlight.h

## Purpose
`nvidia-wmi-ec-backlight.h` is a Linux kernel x86 platform integration data header. It gives board
files, MFD children, ACPI glue, or platform-device setup code a compact contract for passing the
primary type `struct wmi_brightness_args`; enumerations such as `enum wmi_brightness_method`, `enum
wmi_brightness_mode` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_NVIDIA_WMI_EC_BACKLIGHT_H`, `WMI_BRIGHTNESS_GUID`. Types:
`struct wmi_brightness_args`, `enum wmi_brightness_method`, `enum wmi_brightness_mode`, `enum
wmi_brightness_source`. Declared or inline functions: none visible in this header. Important struct
details: struct wmi_brightness_args fields include `u32 mode`, `u32 val`, `u32 ret`, `u32
ignored[3]`. Important enum details: enum wmi_brightness_method values include
`WMI_BRIGHTNESS_METHOD_LEVEL`, `WMI_BRIGHTNESS_METHOD_SOURCE`, `WMI_BRIGHTNESS_METHOD_MAX`; enum
wmi_brightness_mode values include `WMI_BRIGHTNESS_MODE_GET`, `WMI_BRIGHTNESS_MODE_SET`,
`WMI_BRIGHTNESS_MODE_GET_MAX_LEVEL`, `WMI_BRIGHTNESS_MODE_MAX`; enum wmi_brightness_source values
include `WMI_BRIGHTNESS_SOURCE_GPU`, `WMI_BRIGHTNESS_SOURCE_EC`, `WMI_BRIGHTNESS_SOURCE_AUX`,
`WMI_BRIGHTNESS_SOURCE_MAX`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/nvidia-wmi-ec-backlight.c`, `sources/distributed-fs/ceph-
client/drivers/acpi/video_detect.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/platform/x86/nvidia-wmi-ec-backlight.c`, `sources/distributed-fs/ceph-
client/drivers/acpi/video_detect.c`. It integrates through `struct platform_device` platform data,
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/nvidia-wmi-ec-backlight.h` completely for this pass (76 lines, 2902 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/nvidia-wmi-ec-backlight.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/nvidia-wmi-ec-backlight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/p2sb.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/p2sb.h

## Purpose
`p2sb.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing macros, constants, or
function prototypes into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `_PLATFORM_DATA_X86_P2SB_H`. Types: none visible in this header. Declared or
inline functions: `p2sb_bar`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/edac/pnd2_edac.c`, `sources/distributed-fs/ceph-client/drivers/platform/x86/p2sb.c`,
`sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-i801.c`, `sources/distributed-fs/ceph-
client/drivers/watchdog/simatic-ipc-wdt.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/errno.h`, `linux/kconfig.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/drivers/edac/pnd2_edac.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/p2sb.c`, `sources/distributed-fs/ceph-
client/drivers/i2c/busses/i2c-i801.c`, `sources/distributed-fs/ceph-client/drivers/watchdog/simatic-
ipc-wdt.c`, `sources/distributed-fs/ceph-client/drivers/mfd/lpc_ich.c`. It integrates through
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/p2sb.h` completely for this pass (28 lines, 575 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/p2sb.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/p2sb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pmc_atom.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pmc_atom.h

## Purpose
`pmc_atom.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing macros, constants,
or function prototypes into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `PMC_ATOM_H`, `PMC_CLK_CTL_OFFSET`, `PMC_CLK_CTL_SIZE`, `PMC_CLK_NUM`,
`PMC_CLK_CTL_GATED_ON_D3`, `PMC_CLK_CTL_FORCE_ON`, `PMC_CLK_CTL_FORCE_OFF`, `PMC_CLK_CTL_RESERVED`,
`PMC_MASK_CLK_CTL`, `PMC_MASK_CLK_FREQ`, `PMC_CLK_FREQ_XTAL`, `PMC_CLK_FREQ_PLL`, `PMC_PSS_BIT_GBE`,
`PMC_PSS_BIT_SATA`, and 16 more. Types: none visible in this header. Declared or inline functions:
`pmc_atom_read`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/pmc_atom.c`, `sources/distributed-fs/ceph-
client/drivers/acpi/x86/lpss.c`, `sources/distributed-fs/ceph-client/drivers/clk/x86/clk-pmc-
atom.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/bits.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/platform/x86/pmc_atom.c`, `sources/distributed-fs/ceph-
client/drivers/acpi/x86/lpss.c`, `sources/distributed-fs/ceph-client/drivers/clk/x86/clk-pmc-
atom.c`. It integrates through `struct platform_device` platform data, board files, MFD child
registration, and legacy non-DT setup paths; many modern systems may replace parts of this contract
with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pmc_atom.h` completely for this pass (163 lines, 5026 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pmc_atom.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pmc_atom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pwm-lpss.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pwm-lpss.h

## Purpose
`pwm-lpss.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct pwm_lpss_boardinfo` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_PWM_LPSS_H`. Types: `struct pwm_lpss_boardinfo`. Declared or
inline functions: none visible in this header. Important struct details: struct pwm_lpss_boardinfo
fields include `unsigned long clk_rate`, `unsigned int npwm`, `unsigned long base_unit_bits`, `bool
bypass`, `bool other_devices_aml_touches_pwm_regs`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/pinctrl/intel/pinctrl-intel.c`, `sources/distributed-fs/ceph-client/drivers/pwm/pwm-
lpss.h`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-intel.c`, `sources/distributed-
fs/ceph-client/drivers/pwm/pwm-lpss.h`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pwm-lpss.h` completely for this pass (60 lines, 2405 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pwm-lpss.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/pwm-lpss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc-base.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc-base.h

## Purpose
`simatic-ipc-base.h` is a Linux kernel x86 platform integration data header. It gives board files,
MFD children, ACPI glue, or platform-device setup code a compact contract for passing the primary
type `struct simatic_ipc_platform` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_SIMATIC_IPC_BASE_H`, `SIMATIC_IPC_DEVICE_NONE`,
`SIMATIC_IPC_DEVICE_227D`, `SIMATIC_IPC_DEVICE_427E`, `SIMATIC_IPC_DEVICE_127E`,
`SIMATIC_IPC_DEVICE_227E`, `SIMATIC_IPC_DEVICE_227G`, `SIMATIC_IPC_DEVICE_BX_21A`,
`SIMATIC_IPC_DEVICE_BX_39A`, `SIMATIC_IPC_DEVICE_BX_59A`. Types: `struct simatic_ipc_platform`.
Declared or inline functions: none visible in this header. Important struct details: struct
simatic_ipc_platform fields include `u8 devmode`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/include/linux/platform_data/x86/simatic-ipc.h`, `sources/distributed-fs/ceph-
client/drivers/leds/simatic/simatic-ipc-leds-gpio-elkhartlake.c`, `sources/distributed-fs/ceph-
client/drivers/leds/simatic/simatic-ipc-leds.c`, `sources/distributed-fs/ceph-
client/drivers/leds/simatic/simatic-ipc-leds-gpio-apollolake.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc.h`,
`sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-elkhartlake.c`,
`sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds.c`, `sources/distributed-
fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-apollolake.c`, `sources/distributed-
fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds-gpio-f7188x.c`, `sources/distributed-fs/ceph-
client/drivers/leds/simatic/simatic-ipc-leds-gpio-core.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/siemens/simatic-ipc-batt.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/siemens/simatic-ipc-batt-f7188x.c`. It integrates through `struct
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
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc-base.h` completely for this pass (31 lines, 768 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc-base.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc-base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc.h

## Purpose
`simatic-ipc.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing enumerations such
as `enum simatic_ipc_station_ids` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_SIMATIC_IPC_H`, `SIMATIC_IPC_DMI_ENTRY_OEM`,
`SIMATIC_IPC_DMI_TYPE`, `SIMATIC_IPC_DMI_GROUP`, `SIMATIC_IPC_DMI_ENTRY`, `SIMATIC_IPC_DMI_TID`.
Types: `enum simatic_ipc_station_ids`. Declared or inline functions: `le32_to_cpu`,
`simatic_ipc_get_station_id`. Important enum details: enum simatic_ipc_station_ids values include
`SIMATIC_IPC_INVALID_STATION_ID`, `SIMATIC_IPC_IPC227D`, `SIMATIC_IPC_IPC427D`,
`SIMATIC_IPC_IPC227E`, `SIMATIC_IPC_IPC277E`, `SIMATIC_IPC_IPC427E`, `SIMATIC_IPC_IPC477E`,
`SIMATIC_IPC_IPC127E`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/pmc_atom.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/siemens/simatic-ipc.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/dmi.h`, `linux/platform_data/x86/simatic-ipc-base.h`. Direct source-tree
consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/platform/x86/pmc_atom.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/siemens/simatic-ipc.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc.h` completely for this pass (79 lines, 2203 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/simatic-ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/soc.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/soc.h

## Purpose
`soc.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing macros, constants, or
function prototypes into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_SOC_H`, `SOC_INTEL_IS_CPU`. Types: none visible in this
header. Declared or inline functions: `SOC_INTEL_IS_CPU`, `soc`, `soc_intel_is_byt`,
`soc_intel_is_cht`, `soc_intel_is_apl`, `soc_intel_is_glk`, `soc_intel_is_cml`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/sound/soc/sof/sof-pci-dev.c`, `sources/distributed-fs/ceph-
client/sound/soc/intel/boards/bytcr_wm5102.c`, `sources/distributed-fs/ceph-
client/sound/soc/intel/common/soc-intel-quirks.h`, `sources/distributed-fs/ceph-
client/sound/soc/intel/avs/boards/da7219.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`, `linux/mod_devicetable.h`, `asm/cpu_device_id.h`. Direct source-tree
consumers found by include search are `sources/distributed-fs/ceph-client/sound/soc/sof/sof-pci-
dev.c`, `sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcr_wm5102.c`,
`sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-intel-quirks.h`,
`sources/distributed-fs/ceph-client/sound/soc/intel/avs/boards/da7219.c`, `sources/distributed-
fs/ceph-client/drivers/mmc/host/sdhci-acpi.c`, `sources/distributed-fs/ceph-
client/drivers/mfd/intel_soc_pmic_crc.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/intel/int0002_vgpio.c`, `sources/distributed-fs/ceph-
client/drivers/input/misc/axp20x-pek.c`. It integrates through `struct platform_device` platform
data, board files, MFD child registration, and legacy non-DT setup paths; many modern systems may
replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/soc.h` completely for this pass (70 lines, 1358 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/soc.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/spi-intel.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/spi-intel.h

## Purpose
`spi-intel.h` is a Linux kernel SPI controller board-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct intel_spi_boardinfo`; enumerations such as `enum intel_spi_type` into the matching driver at
probe time.

## Important APIs, types, and functions
Macros/constants: `SPI_INTEL_PDATA_H`. Types: `struct intel_spi_boardinfo`, `enum intel_spi_type`.
Declared or inline functions: `bool`. Important struct details: struct intel_spi_boardinfo fields
include `enum intel_spi_type type`, `bool (*set_writeable)(void __iomem *base, void *data)`, `void
*data`. Important enum details: enum intel_spi_type values include `INTEL_SPI_BYT`, `INTEL_SPI_LPT`,
`INTEL_SPI_BXT`, `INTEL_SPI_CNL`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/include/linux/mfd/lpc_ich.h`, `sources/distributed-fs/ceph-client/drivers/spi/spi-intel.h`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/include/linux/mfd/lpc_ich.h`, `sources/distributed-fs/ceph-client/drivers/spi/spi-intel.h`.
It integrates through `struct platform_device` platform data, board files, MFD child registration,
and legacy non-DT setup paths; many modern systems may replace parts of this contract with Device
Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/spi-intel.h` completely for this pass (31 lines, 756 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/spi-intel.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/x86/spi-intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/xilinx-ll-temac.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/xilinx-ll-temac.h

## Purpose
`xilinx-ll-temac.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct ll_temac_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__LINUX_XILINX_LL_TEMAC_H`. Types: `struct ll_temac_platform_data`. Declared or
inline functions: none visible in this header. Important struct details: struct
ll_temac_platform_data fields include `bool txcsum`, `bool rxcsum`, `u8 mac_addr[ETH_ALEN]`, `u32
mdio_clk_freq`, `unsigned long long mdio_bus_id`, `int phy_addr`, `phy_interface_t phy_interface`,
`bool reg_little_endian`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/net/ethernet/xilinx/ll_temac_main.c`, `sources/distributed-fs/ceph-
client/drivers/net/ethernet/xilinx/ll_temac_mdio.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/if_ether.h`, `linux/phy.h`, `linux/spinlock.h`. Direct source-tree consumers
found by include search are `sources/distributed-fs/ceph-
client/drivers/net/ethernet/xilinx/ll_temac_main.c`, `sources/distributed-fs/ceph-
client/drivers/net/ethernet/xilinx/ll_temac_mdio.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/xilinx-ll-temac.h` completely for this pass (33 lines, 1320 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/xilinx-ll-temac.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/xilinx-ll-temac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/xtalk-bridge.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_data/xtalk-bridge.h

## Purpose
`xtalk-bridge.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct xtalk_bridge_platform_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `PLATFORM_DATA_XTALK_BRIDGE_H`. Types: `struct xtalk_bridge_platform_data`.
Declared or inline functions: none visible in this header. Important struct details: struct
xtalk_bridge_platform_data fields include `struct resource mem`, `struct resource io`, `unsigned
long bridge_addr`, `unsigned long intr_addr`, `unsigned long mem_offset`, `unsigned long io_offset`,
`nasid_t nasid`, `int masterwid`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/arch/mips/sgi-ip27/ip27-xtalk.c`, `sources/distributed-fs/ceph-client/arch/mips/pci/pci-
xtalk-bridge.c`, `sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-xtalk.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `asm/sn/types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-xtalk.c`, `sources/distributed-fs/ceph-
client/arch/mips/pci/pci-xtalk-bridge.c`, `sources/distributed-fs/ceph-client/arch/mips/sgi-
ip30/ip30-xtalk.c`. It integrates through `struct platform_device` platform data, board files, MFD
child registration, and legacy non-DT setup paths; many modern systems may replace parts of this
contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/xtalk-bridge.h` completely for this pass (22 lines, 437 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/xtalk-bridge.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_data/xtalk-bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_device.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_device.h

## Purpose
the Linux platform bus interface. It defines platform devices, platform drivers, resource lookup
helpers, registration APIs, and driver matching surfaces used by non-discoverable or firmware-
described devices.

## Important APIs, types, and functions
Macros/constants: `_PLATFORM_DEVICE_H_`, `PLATFORM_DEVID_NONE`, `PLATFORM_DEVID_AUTO`,
`platform_get_device_id`, `dev_is_platform`, `to_platform_device`, `to_platform_driver`,
`platform_driver_register`, `platform_driver_probe`, `module_platform_driver`,
`builtin_platform_driver`, `module_platform_driver_probe`, `builtin_platform_driver_probe`,
`platform_create_bundle`, and 8 more. Types: `struct platform_device`, `struct
platform_device_info`, `struct platform_driver`. Declared or inline functions:
`platform_device_register`, `platform_device_unregister`, `IOMEM_ERR_PTR`, `platform_get_irq`,
`platform_get_irq_optional`, `platform_irq_count`, `platform_get_irq_byname`,
`platform_add_devices`, `platform_device_register_full`, `platform_device_add`,
`platform_device_del`, `platform_device_put`, `int`, `void`, `platform_driver_unregister`,
`dev_get_drvdata`, `dev_set_drvdata`, `module_init`, and 15 more. Important struct details: struct
platform_device fields include `const char *name`, `int id`, `bool id_auto`, `struct device dev`,
`u64 platform_dma_mask`, `struct device_dma_parameters dma_parms`, `u32 num_resources`, `struct
resource *resource`; struct platform_device_info fields include `struct device *parent`, `struct
fwnode_handle *fwnode`, `bool of_node_reused`, `const char *name`, `int id`, `const struct resource
*res`, `unsigned int num_res`, `const void *data`; struct platform_driver fields include `int
(*probe)(struct platform_device *)`, `void (*remove)(struct platform_device *)`, `void
(*shutdown)(struct platform_device *)`, `int (*suspend)(struct platform_device *, pm_message_t
state)`, `int (*resume)(struct platform_device *)`, `struct device_driver driver`, `const struct
platform_device_id *id_table`, `bool prevent_deferred_probe`.

## Control flow
Board, firmware, or MFD code allocates resources and platform data, registers a `struct
platform_device`, and the platform bus matches it to a `struct platform_driver` by id table, OF/ACPI
data, or name. Probe code retrieves MMIO/IRQ/resources and platform data, then normal driver
lifecycle callbacks handle remove, shutdown, suspend, and resume.

## State and persistence
Persistent kernel state is the registered `struct platform_device`, its resource array, optional
platform data, DMA mask, id, and `struct device` membership on the platform bus. The objects live
until unregistration or devres cleanup and do not survive reboot.

## Dependencies and integration points
It includes `linux/device.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/rust/bindings/bindings_helper.h`, `sources/distributed-fs/ceph-
client/arch/um/drivers/vector_kern.c`, `sources/distributed-fs/ceph-
client/arch/um/drivers/virtio_uml.c`, `sources/distributed-fs/ceph-
client/arch/um/drivers/ubd_kern.c`, `sources/distributed-fs/ceph-
client/arch/xtensa/platforms/xt2000/setup.c`, `sources/distributed-fs/ceph-
client/arch/um/drivers/vector_kern.h`, `sources/distributed-fs/ceph-
client/arch/um/drivers/rtc_kern.c`, `sources/distributed-fs/ceph-client/net/rfkill/rfkill-gpio.c`.
It integrates with the Linux driver core and in-kernel helper libraries that include this header.

## Risks and test signals
Risks include resource index/name mismatches, stale platform-data pointers, incorrect DMA masks,
duplicate platform ids, OF/ACPI/name matching ambiguity, and unregister paths racing active driver
users. Test signals include probe/remove cycles, deferred probe, resource lookup by name and index,
hotplug or MFD child teardown, and randconfig builds with and without OF/ACPI.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_device.h` completely for this pass (432 lines, 15416 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_device.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_profile.h -->
# sources/distributed-fs/ceph-client/include/linux/platform_profile.h

## Purpose
the platform performance-profile class contract. It lets platform drivers expose balanced,
performance, low-power, and custom profile choices through a common handler object.

## Important APIs, types, and functions
Macros/constants: `_PLATFORM_PROFILE_H_`. Types: `struct platform_profile_ops`, `enum
platform_profile_option`. Declared or inline functions: `int`, `platform_profile_remove`,
`platform_profile_cycle`, `platform_profile_notify`. Important struct details: struct
platform_profile_ops fields include `int (*probe)(void *drvdata, unsigned long *choices)`, `int
(*hidden_choices)(void *drvdata, unsigned long *choices)`, `int (*profile_get)(struct device *dev,
enum platform_profile_option *profile)`, `int (*profile_set)(struct device *dev, enum
platform_profile_option profile)`. Important enum details: enum platform_profile_option values
include `PLATFORM_PROFILE_LOW_POWER`, `PLATFORM_PROFILE_COOL`, `PLATFORM_PROFILE_QUIET`,
`PLATFORM_PROFILE_BALANCED`, `PLATFORM_PROFILE_BALANCED_PERFORMANCE`,
`PLATFORM_PROFILE_PERFORMANCE`, `PLATFORM_PROFILE_MAX_POWER`, `PLATFORM_PROFILE_CUSTOM`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/surface/surface_platform_profile.c`, `sources/distributed-fs/ceph-
client/drivers/acpi/platform_profile.c`, `sources/distributed-fs/ceph-client/drivers/cpufreq/amd-
pstate.h`, `sources/distributed-fs/ceph-client/drivers/platform/x86/acer-wmi.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/device.h`, `linux/bitops.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/drivers/platform/surface/surface_platform_profile.c`,
`sources/distributed-fs/ceph-client/drivers/acpi/platform_profile.c`, `sources/distributed-fs/ceph-
client/drivers/cpufreq/amd-pstate.h`, `sources/distributed-fs/ceph-client/drivers/platform/x86/acer-
wmi.c`, `sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wmi.c`, `sources/distributed-
fs/ceph-client/drivers/platform/x86/lenovo/ideapad-laptop.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/lenovo/wmi-gamezone.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/lenovo/wmi-other.c`. It integrates with the Linux driver core and in-
kernel helper libraries that include this header.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_profile.h` completely for this pass (61 lines, 2103 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_profile.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/platform_profile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pldmfw.h -->
# sources/distributed-fs/ceph-client/include/linux/pldmfw.h

## Purpose
the PLDM firmware-update library interface. It describes firmware package parsing, component
matching, flash-update callbacks, and transfer progress plumbing for devices that consume PLDM
firmware images.

## Important APIs, types, and functions
Macros/constants: `_PLDMFW_H_`, `PLDM_DEVICE_UPDATE_CONTINUE_AFTER_FAIL`,
`PLDM_STRING_TYPE_UNKNOWN`, `PLDM_STRING_TYPE_ASCII`, `PLDM_STRING_TYPE_UTF8`,
`PLDM_STRING_TYPE_UTF16`, `PLDM_STRING_TYPE_UTF16LE`, `PLDM_STRING_TYPE_UTF16BE`,
`PLDM_DESC_ID_PCI_VENDOR_ID`, `PLDM_DESC_ID_IANA_ENTERPRISE_ID`, `PLDM_DESC_ID_UUID`,
`PLDM_DESC_ID_PNP_VENDOR_ID`, `PLDM_DESC_ID_ACPI_VENDOR_ID`, `PLDM_DESC_ID_PCI_DEVICE_ID`, and 31
more. Types: `struct pldmfw_record`, `struct pldmfw_desc_tlv`, `struct pldmfw_component`, `struct
pldmfw`, `struct pldmfw_ops`, `enum pldmfw_update_mode`. Declared or inline functions:
`pldmfw_op_pci_match_record`, `bool`, `int`, `pldmfw_flash_image`. Important struct details: struct
pldmfw_record fields include `struct list_head entry`, `struct list_head descs`, `const u8
*version_string`, `u8 version_type`, `u8 version_len`, `u16 package_data_len`, `u32
device_update_flags`, `const u8 *package_data`; struct pldmfw_desc_tlv fields include `struct
list_head entry`, `const u8 *data`, `u16 type`, `u16 size`; struct pldmfw_component fields include
`struct list_head entry`, `u16 classification`, `u16 identifier`, `u16 options`, `u16
activation_method`, `u32 comparison_stamp`, `u32 component_size`, `const u8 *component_data`; struct
pldmfw fields include `const struct pldmfw_ops *ops`, `struct device *dev`, `u16
component_identifier`, `enum pldmfw_update_mode mode`; struct pldmfw_ops fields include `bool
(*match_record)(struct pldmfw *context, struct pldmfw_record *record)`, `int
(*send_package_data)(struct pldmfw *context, const u8 *data, u16 length)`, `u8 transfer_flag)`, `int
(*flash_component)(struct pldmfw *context, struct pldmfw_component *component)`, `int
(*finalize_update)(struct pldmfw *context)`. Important enum details: enum pldmfw_update_mode values
include `PLDMFW_UPDATE_MODE_FULL`, `PLDMFW_UPDATE_MODE_SINGLE_COMPONENT`.

## Control flow
A device driver supplies `struct pldmfw_ops` and private context, then calls the PLDM firmware
helper with a firmware blob. The helper parses the package, matches descriptors against the device,
requests component-table decisions, streams component payloads through the driver's write hooks, and
reports progress or cancellation through the callback table.

## State and persistence
The header stores no data itself; firmware-update state lives in the caller context and parser-owned
transfer state while an update is in progress. Component identity, package metadata, cancellation
state, and written bytes are transient unless the driver's flash operation commits them to device
storage.

## Dependencies and integration points
It includes `linux/list.h`, `linux/firmware.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/lib/pldmfw/pldmfw.c`, `sources/distributed-fs/ceph-
client/drivers/net/ethernet/meta/fbnic/fbnic_devlink.c`, `sources/distributed-fs/ceph-
client/drivers/net/ethernet/intel/ixgbe/ixgbe_fw_update.c`, `sources/distributed-fs/ceph-
client/drivers/net/ethernet/intel/ice/ice_fw_update.c`. It integrates with the Linux driver core and
in-kernel helper libraries that include this header.

## Risks and test signals
Risks include accepting an incompatible component image, descriptor matching mistakes, integer
overflows in package offsets and sizes, partial flash writes after cancellation, and callback
implementations that sleep or fail in unsupported contexts. Test signals include malformed PLDM
packages, descriptor mismatch, multi-component updates, cancellation, progress accounting, and
injected flash-write failures.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/pldmfw.h` completely for this pass (173 lines, 5032 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/pldmfw.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pldmfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/plist.h -->
# sources/distributed-fs/ceph-client/include/linux/plist.h

## Purpose
the priority-sorted list helper API. It layers priority ordering on top of Linux list heads and is
used when callers need deterministic insertion by integer priority.

## Important APIs, types, and functions
Macros/constants: `_LINUX_PLIST_H_`, `PLIST_HEAD_INIT`, `PLIST_HEAD`, `PLIST_NODE_INIT`,
`plist_for_each`, `plist_for_each_continue`, `plist_for_each_safe`, `plist_for_each_entry`,
`plist_for_each_entry_continue`, `plist_for_each_entry_safe`, `plist_next`, `plist_prev`. Types:
none visible in this header. Declared or inline functions: `INIT_LIST_HEAD`, `plist_add`,
`plist_del`, `plist_requeue`, `list_empty`, `WARN_ON`, `container_of`, `plist_node_init`,
`plist_head_empty`, `plist_node_empty`, `plist_first`, `plist_last`.

## Control flow
Callers initialize a `plist_head`, initialize embedded `plist_node` objects with priorities, insert
them with `plist_add()`, and remove or iterate them through list-style helpers. Insertions maintain
priority order while preserving node linkage in ordinary kernel lists.

## State and persistence
State lives in caller-owned `struct plist_head` and `struct plist_node` objects. Ordering is in-
memory only and must be protected by the caller's lock discipline when shared between CPUs.

## Dependencies and integration points
It includes `linux/container_of.h`, `linux/list.h`, `linux/plist_types.h`, `asm/bug.h`. Direct
source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/mm/swapfile.c`, `sources/distributed-fs/ceph-client/lib/plist.c`, `sources/distributed-
fs/ceph-client/kernel/sched/sched.h`, `sources/distributed-fs/ceph-client/kernel/futex/core.c`,
`sources/distributed-fs/ceph-client/kernel/futex/requeue.c`, `sources/distributed-fs/ceph-
client/kernel/futex/waitwake.c`, `sources/distributed-fs/ceph-client/init/init_task.c`,
`sources/distributed-fs/ceph-client/include/linux/pm_qos.h`. It integrates with the Linux driver
core and in-kernel helper libraries that include this header.

## Risks and test signals
Risks include priority ordering regressions, double-add or double-delete of nodes, iteration while
mutating without proper locking, and callers confusing equal-priority FIFO behavior with strict
sorting. Test signals include plist selftests, lockdep on caller locks, empty/list singleton cases,
duplicate priorities, and removal during iteration.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/plist.h` completely for this pass (291 lines, 8797 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/plist.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/plist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/plist_types.h -->
# sources/distributed-fs/ceph-client/include/linux/plist_types.h

## Purpose
the type-only companion for priority lists. It exposes the storage layout needed by users that embed
plist nodes without pulling in the full helper API.

## Important APIs, types, and functions
Macros/constants: `_LINUX_PLIST_TYPES_H`. Types: `struct plist_head`, `struct plist_node`. Declared
or inline functions: none visible in this header. Important struct details: struct plist_head fields
include `struct list_head node_list`; struct plist_node fields include `int prio`, `struct list_head
prio_list`, `struct list_head node_list`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/include/linux/plist.h`, `sources/distributed-fs/ceph-client/include/linux/sched.h`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/include/linux/plist.h`, `sources/distributed-fs/ceph-
client/include/linux/sched.h`. It integrates with the Linux driver core and in-kernel helper
libraries that include this header.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/plist_types.h` completely for this pass (17 lines, 315 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/plist_types.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/plist_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm-trace.h -->
# sources/distributed-fs/ceph-client/include/linux/pm-trace.h

## Purpose
the suspend/resume trace helper interface. It records device fingerprints across failed suspend
cycles so the next boot can identify the last device reached.

## Important APIs, types, and functions
Macros/constants: `PM_TRACE_H`, `TRACE_DEVICE`, `TRACE_RESUME`, `TRACE_SUSPEND`. Types: none visible
in this header. Declared or inline functions: `set_trace_device`, `generate_pm_trace`,
`show_trace_dev_match`, `pm_trace_rtc_valid`, `pm_trace_is_enabled`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/kernel/power/main.c`, `sources/distributed-fs/ceph-client/include/linux/mc146818rtc.h`,
`sources/distributed-fs/ceph-client/drivers/base/power/main.c`, `sources/distributed-fs/ceph-
client/drivers/base/power/trace.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/types.h`, `asm/pm-trace.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/kernel/power/main.c`, `sources/distributed-fs/ceph-
client/include/linux/mc146818rtc.h`, `sources/distributed-fs/ceph-client/drivers/base/power/main.c`,
`sources/distributed-fs/ceph-client/drivers/base/power/trace.c`. It integrates with the driver core,
bus types, PM domains, wakeup-source code, runtime PM, suspend/hibernate sequencing, and
architecture/platform suspend backends.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/pm-trace.h` completely for this pass (43 lines, 940 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/pm-trace.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm.h -->
# sources/distributed-fs/ceph-client/include/linux/pm.h

## Purpose
the central Linux device power-management interface. It defines system sleep callbacks, runtime PM
state, wakeup-source accounting, PM messages, event constants, and helper APIs shared by drivers and
core code.

## Important APIs, types, and functions
Macros/constants: `_LINUX_PM_H`, `power_group_name`, `SYSTEM_SLEEP_PM_OPS`,
`LATE_SYSTEM_SLEEP_PM_OPS`, `NOIRQ_SYSTEM_SLEEP_PM_OPS`, `RUNTIME_PM_OPS`,
`SET_SYSTEM_SLEEP_PM_OPS`, `SET_LATE_SYSTEM_SLEEP_PM_OPS`, `SET_NOIRQ_SYSTEM_SLEEP_PM_OPS`,
`SET_RUNTIME_PM_OPS`, `_DEFINE_DEV_PM_OPS`, `_EXPORT_PM_OPS`, `_DISCARD_PM_OPS`,
`_EXPORT_DEV_PM_OPS`, and 83 more. Types: `struct pm_message`, `struct pm_subsys_data`, `struct
dev_pm_info`, `struct dev_pm_domain`, `enum rpm_status`, `enum rpm_request`, `enum dpm_order`,
`typedef struct pm_message {`. Declared or inline functions: `void`, `pm_vt_switch_required`,
`pm_vt_switch_unregister`, `cxl_mem_active`, `int`, `__EXPORT_SYMBOL`, `dev_pm_get_subsys_data`,
`dev_pm_put_subsys_data`, `device_pm_lock`, `dpm_resume_start`, `dpm_resume_end`,
`dpm_resume_noirq`, `dpm_resume_early`, `dpm_resume`, `dpm_complete`, `device_pm_unlock`,
`dpm_suspend_end`, `dpm_suspend_start`, and 27 more. Important struct details: struct pm_message
fields include `int event`, `} pm_message_t`, `int (*prepare)(struct device *dev)`, `void
(*complete)(struct device *dev)`, `int (*suspend)(struct device *dev)`, `int (*resume)(struct device
*dev)`, `int (*freeze)(struct device *dev)`, `int (*thaw)(struct device *dev)`; struct
pm_subsys_data fields include `spinlock_t lock`, `unsigned int refcount`, `unsigned int
clock_op_might_sleep`, `struct mutex clock_mutex`, `struct list_head clock_list`, `struct
pm_domain_data *domain_data`; struct dev_pm_info fields include `pm_message_t power_state`, `bool
can_wakeup:1`, `bool async_suspend:1`, `bool in_dpm_list:1`, `bool is_prepared:1`, `bool
is_suspended:1`, `bool is_noirq_suspended:1`, `bool is_late_suspended:1`; struct dev_pm_domain
fields include `struct dev_pm_ops ops`, `int (*start)(struct device *dev)`, `void (*detach)(struct
device *dev, bool power_off)`, `int (*activate)(struct device *dev)`, `void (*sync)(struct device
*dev)`, `void (*dismiss)(struct device *dev)`, `int (*set_performance_state)(struct device *dev,
unsigned int state)`. Important enum details: enum rpm_status values include `RPM_INVALID`,
`RPM_ACTIVE`, `RPM_RESUMING`, `RPM_SUSPENDED`, `RPM_SUSPENDING`, `RPM_BLOCKED`; enum rpm_request
values include `RPM_REQ_NONE`, `RPM_REQ_IDLE`, `RPM_REQ_SUSPEND`, `RPM_REQ_AUTOSUSPEND`,
`RPM_REQ_RESUME`; enum dpm_order values include `DPM_ORDER_NONE`, `DPM_ORDER_DEV_AFTER_PARENT`,
`DPM_ORDER_PARENT_BEFORE_DEV`, `DPM_ORDER_DEV_LAST`.

## Control flow
Device drivers or bus types populate `struct dev_pm_ops` callbacks; the PM core runs prepare,
suspend or hibernation callbacks, noirq phases, resume or restore callbacks, and completion
callbacks in ordered device-tree or dependency order. Runtime PM helpers update `struct
dev_pm_info`, wakeup accounting, timers, locks, and work items as drivers request autosuspend,
forbid/allow runtime PM, or mark devices active/suspended.

## State and persistence
State is embedded in `struct dev_pm_info`, wakeup-source objects, completion objects, timers, wait
queues, spinlocks, mutexes, and work items owned by each device. It is runtime kernel state, not
filesystem persistence; suspend and hibernation preserve or restore hardware and memory according to
the selected callbacks.

## Dependencies and integration points
It includes `linux/completion.h`, `linux/export.h`, `linux/hrtimer_types.h`, `linux/mutex.h`,
`linux/spinlock.h`, `linux/types.h`, `linux/util_macros.h`, `linux/wait.h`,
`linux/workqueue_types.h`. Direct source-tree consumers found by include search are
`sources/distributed-fs/ceph-client/sound/hda/core/regmap.c`, `sources/distributed-fs/ceph-
client/sound/ac97/bus.c`, `sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos_scb_lib.c`,
`sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos.c`, `sources/distributed-fs/ceph-
client/sound/pci/cs46xx/cs46xx_lib.c`, `sources/distributed-fs/ceph-client/sound/hda/common/bind.c`,
`sources/distributed-fs/ceph-client/sound/hda/common/codec.c`, `sources/distributed-fs/ceph-
client/arch/arm64/kernel/hibernate.c`. It integrates with the driver core, bus types, PM domains,
wakeup-source code, runtime PM, suspend/hibernate sequencing, and architecture/platform suspend
backends.

## Risks and test signals
Risks concentrate around callback ordering, direct-complete decisions, async suspend races, wakeup-
source reference leaks, runtime PM usage-count imbalance, noirq operations that sleep, and
hibernation restore paths diverging from suspend/resume. Test signals include suspend-to-idle,
suspend-to-RAM, hibernation, runtime autosuspend stress, wakeup-source accounting, lockdep,
`pm_test` modes, and driver unbind during PM transitions.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/pm.h` completely for this pass (913 lines, 37678 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/pm.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_clock.h -->
# sources/distributed-fs/ceph-client/include/linux/pm_clock.h

## Purpose
the PM clock-domain helper contract. It lets platform and generic PM code attach clock lists to
devices and coordinate clock enable/disable around runtime/system PM transitions.

## Important APIs, types, and functions
Macros/constants: `_LINUX_PM_CLOCK_H`, `USE_PM_CLK_RUNTIME_OPS`, `pm_clk_suspend`, `pm_clk_resume`.
Types: `struct pm_clk_notifier_block`. Declared or inline functions: `pm_clk_runtime_suspend`,
`pm_clk_runtime_resume`, `pm_clk_init`, `pm_clk_create`, `pm_clk_destroy`, `pm_clk_add`,
`pm_clk_add_clk`, `of_pm_clk_add_clks`, `pm_clk_remove_clk`, `pm_clk_suspend`, `pm_clk_resume`,
`devm_pm_clk_create`, `pm_clk_no_clocks`, `pm_clk_add_notifier`. Important struct details: struct
pm_clk_notifier_block fields include `struct notifier_block nb`, `struct dev_pm_domain *pm_domain`,
`char *con_ids[]`.

## Control flow
Platform setup or PM-domain code creates a per-device PM clock list, adds named clocks, then
runtime/system PM transitions call the helper to enable clocks before device access and disable them
when the device can idle. Notifier helpers wire this behavior to bus events.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/device.h`, `linux/notifier.h`. Direct source-tree consumers found by include
search are `sources/distributed-fs/ceph-client/arch/arm/mach-omap1/pm_bus.c`, `sources/distributed-
fs/ceph-client/arch/arm/mach-keystone/keystone.c`, `sources/distributed-fs/ceph-
client/arch/arm/mach-davinci/pm_domain.c`, `sources/distributed-fs/ceph-
client/drivers/base/power/clock_ops.c`, `sources/distributed-fs/ceph-
client/drivers/base/power/common.c`, `sources/distributed-fs/ceph-client/drivers/bus/qcom-ssc-block-
bus.c`, `sources/distributed-fs/ceph-client/drivers/pmdomain/core.c`, `sources/distributed-fs/ceph-
client/drivers/pmdomain/rockchip/pm-domains.c`. It integrates with the driver core, bus types, PM
domains, wakeup-source code, runtime PM, suspend/hibernate sequencing, and architecture/platform
suspend backends.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/pm_clock.h` completely for this pass (98 lines, 2437 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/pm_clock.h_research.md`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pm_clock.h -->
