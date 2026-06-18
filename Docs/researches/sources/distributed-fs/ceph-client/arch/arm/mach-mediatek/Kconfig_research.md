# sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/Kconfig

Purpose: Kconfig menu for MediaTek ARMv7 SoC families.

Important APIs/types/functions: Defines `ARCH_MEDIATEK` and SoC selections including `MACH_MT2701`, `MACH_MT6589`, `MACH_MT6592`, `MACH_MT7623`, `MACH_MT7629`, `MACH_MT8127`, `MACH_MT8135`, and `MACH_MT8173`, with selections for GIC, timers, SCPSYS, SMP, and platform drivers.

Control flow: No runtime flow; the symbols select which machine/SMP objects and subsystem drivers are built.

State and persistence: No runtime state. Build state gates generic MediaTek machine support and SMP availability.

Dependencies and integration points: Integrates with ARM multi-v7, GIC, arch timer, MediaTek SCPSYS, SMP, and DT roots.

Risks: Incorrect selects can enable SMP or power-domain assumptions on unsupported SoCs. Some symbols are grouped despite differing boot methods.

Test signals: Build configs for each MediaTek SoC and verify expected objects and power-domain/SMP dependencies.
