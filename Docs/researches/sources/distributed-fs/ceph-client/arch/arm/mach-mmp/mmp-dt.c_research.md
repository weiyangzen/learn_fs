# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/mmp-dt.c

Purpose: Device-tree machine descriptors for Marvell PXA168 and PXA910 boards.

Important APIs/types/functions: Defines `pxa168_dt_board_compat[]`, `pxa910_dt_board_compat[]`, `mmp_init_time()`, and two `DT_MACHINE_START` descriptors.

Control flow: Machine selection matches `mrvl,pxa168-aspenite` or `mrvl,pxa910-dkb`. Mapping uses `mmp_map_io()`. Time init optionally initializes Tauros2 cache, initializes clocks from DT, and probes timers.

State and persistence: No owned mutable state beyond static IO mapping and generic clock/timer/cache registration.

Dependencies and integration points: Depends on MMP common mapping, optional Tauros2 cache support, OF clock init, and clocksource probing.

Risks: The compatible lists are board-specific rather than broad SoC compatibles, so other DTs need explicit additions. Timer correctness depends on the DT timer node and the static APB mapping used by common code.

Test signals: Boot Aspenite and DKB DTs, verify Tauros2 when enabled, clock init, and timer interrupts.
