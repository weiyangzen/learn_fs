# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/mmp2-dt.c

Purpose: Device-tree machine descriptor for Marvell MMP2 platforms.

Important APIs/types/functions: Defines `mmp_init_time()`, `mmp2_dt_board_compat[]`, and `DT_MACHINE_START(MMP2_DT, ...)`.

Control flow: Boot selection matches root compatible `mrvl,mmp2`, maps APB/AXI plus PGU through `mmp2_map_io()`, optionally initializes Tauros2 cache, initializes clocks from DT, and probes timers.

State and persistence: No owned runtime state beyond static mappings and generic cache/clock/timer registration.

Dependencies and integration points: Depends on MMP2 static mapping, optional Tauros2, OF clocks, and timer nodes.

Risks: The descriptor is minimal and delegates all device creation to DT drivers. Missing PGU/SCU mapping would break MMP2/MMP3-style early users.

Test signals: Boot MMP2 DT, check chip id, timer, clocks, and cache initialization.
