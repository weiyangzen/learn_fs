# sources/distributed-fs/ceph-client/arch/mips/bcm47xx/time.c

Purpose: computes and registers the BCM47xx MIPS CPU clock for timer calibration.

Important APIs and functions: `plat_time_init()` selects clock source data from SSB or BCMA chipcommon, handles board-specific clock overrides such as Huawei E970 and SSB extif, and calls `mips_hpt_frequency = hz / 2` for the CP0 counter.

Control flow: MIPS time initialization asks this platform hook for the CPU frequency after bus detection. The function branches by `bcm47xx_bus_type`, reads the current bus/chipcommon clock, applies known corrections, and publishes the high precision timer frequency.

State and persistence: writes the global `mips_hpt_frequency`; no persistent state.

Dependencies and integration points: depends on BCM47xx board detection, SSB/BCMA clock APIs, and MIPS timekeeping.

Risks and test signals: wrong clock causes scheduler and delay timing drift. Test by comparing kernel-reported BogoMIPS/timer frequency, serial timestamps, network timing, and board-specific boot behavior.
