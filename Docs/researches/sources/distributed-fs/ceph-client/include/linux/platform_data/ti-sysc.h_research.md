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
