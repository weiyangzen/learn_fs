# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/Makefile

Purpose: Build glue for MV78xx0 platform.

Important APIs/types/functions: Links common, irq, mpp, pcie, and board setup objects according to config.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Depends on MV78xx0 Kconfig board symbols.

Risks: Missing an object can remove board init or core PCI/IRQ setup.

Test signals: Compile MV78xx0 board configs and inspect linked objects.
