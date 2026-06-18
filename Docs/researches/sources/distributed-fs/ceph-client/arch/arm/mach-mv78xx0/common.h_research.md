# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.h

Purpose: Private MV78xx0 declarations shared by board/core files.

Important APIs/types/functions: Declares common init, map, device setup, PCIe, MPP, IRQ, and board helper functions.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Integrates board setup files with `common.c`, `mpp.c`, `pcie.c`, and `irq.c`.

Risks: Prototype drift breaks legacy board builds or causes wrong init ordering.

Test signals: Compile all MV78xx0 board configurations.
