# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/irqs.h

Purpose: MV78xx0 fixed interrupt-number definitions.

Important APIs/types/functions: Defines IRQ constants for bridge, timers, GPIO, PCIe, Ethernet, SATA, USB, and other SoC blocks.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Used by board files and irq setup for legacy resource numbers.

Risks: Wrong numbers silently route devices to bad interrupts.

Test signals: Compile board resources and run interrupt smoke tests on hardware.
