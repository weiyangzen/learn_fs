# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/csrc-octeon.c

Purpose: Cavium Octeon clocksource, sched_clock, delay-loop, and CP0 CVMCOUNT setup.

Important APIs and functions: `octeon_setup_delays()` derives delay constants from the IO clock. `octeon_init_cvmcount()` synchronizes or initializes the per-core counter. `octeon_cvmcount_read()` feeds the clocksource. `sched_clock()` returns nanoseconds from CVMCOUNT. `plat_time_init()` registers the clocksource and MIPS clockevent frequency. `__udelay()`, `__ndelay()`, `__delay()`, and `octeon_io_clk_delay()` implement calibrated busy waits.

Control flow: platform time init establishes counter frequency, registers the continuous counter clocksource, and publishes delay calibration. Runtime reads are direct CP0 counter access with scaling.

State and persistence: updates global timing constants and the clocksource registration for the current boot. No persistent state.

Dependencies and integration points: depends on Octeon model/sysinfo data, CP0 CVMCOUNT, MIPS timekeeping, clocksource core, scheduler clock, and SMP synchronization.

Risks and test signals: frequency or synchronization errors break scheduler time, delay loops, and device timing. Test via clocksource selection logs, monotonic time checks across CPUs, delay calibration, network/storage timing, and suspend-free long-running uptime behavior.
