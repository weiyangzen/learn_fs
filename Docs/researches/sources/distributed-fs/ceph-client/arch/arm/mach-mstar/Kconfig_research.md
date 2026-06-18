# sources/distributed-fs/ceph-client/arch/arm/mach-mstar/Kconfig

Purpose: Kconfig entry for MStar/SigmaStar ARMv7 SoCs.

Important APIs/types/functions: Defines `ARCH_MSTARV7`, selecting ARM GIC, arch timer, and required platform support.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Integrates with ARM multi-v7, irq/timer, and MStar DT machine descriptor.

Risks: Incorrect irq/timer selections prevent basic boot.

Test signals: Build MStar V7 config and boot matching DT.
