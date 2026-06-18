# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/Kconfig

Purpose: Kconfig menu for Marvell PXA/MMP ARMv5/v7 SoCs.

Important APIs/types/functions: Defines `ARCH_MMP` and SoC/machine symbols such as `CPU_PXA168`, `CPU_PXA910`, `CPU_MMP2`, `MACH_MMP_DT`, `MACH_MMP2_DT`, `MACH_MMP3_DT`, and `MACH_MMP2_DT`, selecting clocksource, irqchip, pinctrl, timers, SMP, and cpuidle pieces.

Control flow: No runtime flow; it controls build composition and dependencies for MMP platforms.

State and persistence: No runtime state.

Dependencies and integration points: Integrates with ARM multi-v5/v7, MMP timers, irq, pinctrl, clocksource, and DT machine descriptors.

Risks: A broad ARCH symbol spanning multiple CPU generations can select incompatible support if SoC symbols are mis-set.

Test signals: Build each MMP/PXA configuration and verify selected drivers/objects.
