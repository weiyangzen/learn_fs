# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/Kconfig

Purpose: Kconfig menu for Marvell EBU SoCs including Armada 370/375/38x/39x/XP, Dove, and Kirkwood.

Important APIs/types/functions: Defines `ARCH_MVEBU`, `MACH_MVEBU_ANY`, `MACH_MVEBU_V7`, individual SoC symbols, and selects MBUS, irqchips, timers, SMP, PMSU, coherency, PM, and cache support as needed.

Control flow: No runtime flow; it controls build-time selection of shared and SoC-specific MVEBU support.

State and persistence: No runtime state.

Dependencies and integration points: Integrates with ARM multi-v7/v5, Marvell MBUS, irq/timer/cache/PM/SMP drivers, and DT machine descriptors.

Risks: The menu spans old and newer SoCs with different coherency and PM behavior; wrong symbol combinations can build invalid boot paths.

Test signals: Build matrix for Armada/Dove/Kirkwood with SMP/PM options and verify selected objects.
