# sources/distributed-fs/ceph-client/arch/arm/mach-clps711x/board-dt.c

Purpose: supplies DT machine support for Cirrus Logic CLPS711X ARM systems.

Important APIs/types/functions: static IO mapping constants, `clps711x_map_io()`, cpuidle platform resource/device registration in `clps711x_init()`, `clps711x_restart()`, and `DT_MACHINE_START(CLPS711X_DT, ...)`.

Control flow: machine mapping installs a fixed virtual mapping for CLPS711X registers. Init registers an `clps711x-cpuidle` platform device and populates OF devices. Restart writes to the system control region to trigger reset.

State and persistence: fixed IO mapping and a cpuidle platform device persist for the boot lifetime.

Dependencies and integration: depends on ARM machine descriptor hooks, `iotable_init`, OF platform population, CLPS711X register layout, and cpuidle driver matching.

Risks: fixed virtual mappings are sensitive to address conflicts. Restart assumes the mapped control register remains accessible late in shutdown.

Test signals: DT boot, cpuidle device probe, OF child population, and reboot/reset behavior.
