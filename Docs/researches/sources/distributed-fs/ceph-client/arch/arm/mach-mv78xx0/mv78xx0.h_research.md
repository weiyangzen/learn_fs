# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/mv78xx0.h

Purpose: Main MV78xx0 SoC address map and helper macro header.

Important APIs/types/functions: Defines register base addresses, peripheral resources, window offsets, and conversion/access macros for MV78xx0 code.

Control flow: No runtime flow.

State and persistence: No mutable state.

Dependencies and integration points: Shared by common, IRQ, PCIe, MPP, and board setup code.

Risks: Incorrect base addresses break broad platform functionality.

Test signals: Boot tests covering early mapping, timers, IRQ, PCIe, and device resources.
