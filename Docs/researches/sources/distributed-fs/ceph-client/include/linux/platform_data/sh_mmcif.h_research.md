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
