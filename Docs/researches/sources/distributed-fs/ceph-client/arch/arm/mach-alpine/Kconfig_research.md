# sources/distributed-fs/ceph-client/arch/arm/mach-alpine/Kconfig

Purpose: declares `ARCH_ALPINE` support for Annapurna Labs Alpine V1 under ARM multi-v7 and selects interrupt, timer, syscon, PCI, MSI, and AMBA dependencies.

Control flow is Kconfig selection. It has no runtime state, but it controls compilation of machine declaration, SMP, and CPU power-management files. Risks are dependency drift for PCI/MSI or syscon services required by CPU wakeup. Test signals are Alpine defconfig/randconfig builds and DT boot with selected GIC/timer/PCI support.
