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
