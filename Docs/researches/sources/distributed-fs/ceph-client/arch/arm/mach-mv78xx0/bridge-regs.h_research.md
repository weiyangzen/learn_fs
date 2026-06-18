# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/bridge-regs.h

Purpose: MV78xx0 bridge-register address and bit definitions.

Important APIs/types/functions: Defines CPU/DDR/bridge register offsets used by common, IRQ, PCIe, and reset code.

Control flow: No runtime flow.

State and persistence: No mutable state.

Dependencies and integration points: Integrates with low-level MV78xx0 register access helpers.

Risks: Wrong offsets affect resets, interrupts, PCIe windows, and system identification.

Test signals: Boot smoke exercising IRQ, PCIe, and reset paths.
