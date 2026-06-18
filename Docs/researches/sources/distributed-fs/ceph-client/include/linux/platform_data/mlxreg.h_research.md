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
