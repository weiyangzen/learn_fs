# sources/distributed-fs/ceph-client/arch/arm/mach-keystone/Kconfig

Purpose: Kconfig entry for TI Keystone ARMv7 SoCs.

Important APIs/types/functions: Defines `ARCH_KEYSTONE` with selections for GIC, ARM arch timer, Keystone timer/common clock, reset controller, SMP erratum 798181, DMA zone under LPAE, pinctrl, and generic PM domains.

Control flow: No runtime flow; it enables compile-time support and required subsystem symbols.

State and persistence: No runtime state. Build-time selections influence DMA, PM, timer, irq, clock, and reset behavior.

Dependencies and integration points: Integrates with ARM multi-v7, Keystone timer/clock drivers, PM clock domains, and LPAE DMA mapping.

Risks: Incorrect dependency/selects can produce unbootable images or bad DMA zones, especially with high physical memory under LPAE.

Test signals: Config build matrix for Keystone with/without LPAE, SMP, and PM; verify selected symbols match hardware requirements.
