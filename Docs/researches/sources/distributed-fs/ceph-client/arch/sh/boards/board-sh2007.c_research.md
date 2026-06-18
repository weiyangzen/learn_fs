<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-sh2007.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-sh2007.c

Purpose: This file supports the SH-2007 SH7780 single-board computer with two SMSC9118 Ethernet devices, CompactFlash resources, dummy regulators, setup/IRQ callbacks, and the machine vector.

Important APIs/types/functions: It defines SMSC911x platform config `smc911x_info`, resources/devices for two Ethernet controllers, CF resources/device, `sh2007_devices`, `sh2007_io_init`, `sh2007_init_irq`, `sh2007_setup`, and `mv_sh2007`.

Control flow: A subsys initcall registers fixed regulators and all platform devices early enough for bus users. Setup configures I/O behavior, and IRQ init installs board interrupt handling.

State and persistence: Static platform resources persist for Ethernet and CF. Board setup may alter persistent bus/register state for I/O routing.

Dependencies and integration points: It depends on SH7780 CPU support, fixed regulators, SMSC911x, pata/CF platform support, platform devices, and SuperH IRQ/machvec infrastructure.

Risks and test signals: Two Ethernet devices need distinct resources/IRQs and correct regulator consumers. CF window/IRQ definitions must match the PC-104/CF wiring. Tests include dual Ethernet probe/traffic, CF detection, IRQ handling, and SH2007 boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-sh2007.c -->
