# sources/distributed-fs/ceph-client/arch/arm/mach-ixp4xx/Kconfig

Purpose: Kconfig entry enabling Intel IXP4xx/XScale platform support.

Important APIs/types/functions: Defines `menuconfig ARCH_IXP4XX` with dependencies on `ARCH_MULTI_V5` and big-endian CPU mode, and selects XScale, GPIO, PCI, I2C, IRQ, timer, endian EHCI, appended DTB, and OF support.

Control flow: No runtime flow; it shapes the kernel configuration graph.

State and persistence: No runtime state. Build-time state selects platform objects and subsystem options.

Dependencies and integration points: Integrates with ARM multi-v5 builds, IXP4XX irq/timer drivers, GPIO, PCI, I2C, and USB EHCI endian handling.

Risks: Over-selecting dependencies can force subsystems into builds. Big-endian and appended-DTB assumptions reflect old bootloaders and can surprise generic kernels.

Test signals: Run `make ARCH=arm olddefconfig` with `ARCH_IXP4XX=y`, verify selected symbols, and boot DT on IXP4xx hardware/emulation.
