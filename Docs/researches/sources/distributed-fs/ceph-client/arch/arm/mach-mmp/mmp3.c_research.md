# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/mmp3.c

Purpose: Device-tree machine descriptor for Marvell MMP3/PXA2128/Armada 620.

Important APIs/types/functions: Defines `mmp3_dt_board_compat[]` and `DT_MACHINE_START(MMP2_DT, "Marvell MMP3")` with PL310 auxiliary-control values.

Control flow: Boot selection matches `marvell,mmp3`, maps using `mmp2_map_io()`, and configures PL310 auxiliary control to enable full-line-of-zero/write allocate, data prefetch, and instruction prefetch with mask `0xc20fffff`.

State and persistence: No owned mutable state; hardware state includes L2 cache auxiliary settings applied by ARM cache init.

Dependencies and integration points: Depends on MMP2-style mapping, ARM L2X0 support, and the MMP3 DT compatible.

Risks: The machine symbol name reuses `MMP2_DT`, which is potentially confusing but compile-time legal. Cache aux settings are global for the machine and must match MMP3 PL310 behavior.

Test signals: Boot MMP3 DT, verify L2 cache aux register programming and early MMIO mappings.
