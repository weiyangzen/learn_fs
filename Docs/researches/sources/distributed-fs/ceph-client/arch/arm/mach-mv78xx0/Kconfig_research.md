# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/Kconfig

Purpose: Kconfig entry for legacy Marvell MV78xx0 platforms.

Important APIs/types/functions: Defines `ARCH_MV78XX0` with selections for Feroceon/Sheeva CPU support, PCI, IRQ, timers, MPP, and board support.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Integrates with non-DT Marvell board files, PCIe, MPP, IRQ, and timer code.

Risks: Legacy non-DT platform selections can pull in board-specific assumptions and fixed mappings.

Test signals: Build MV78xx0 defconfig and boot known boards such as Buffalo WXL.
