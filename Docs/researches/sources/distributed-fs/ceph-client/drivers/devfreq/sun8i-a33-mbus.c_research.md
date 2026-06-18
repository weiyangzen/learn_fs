<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/sun8i-a33-mbus.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/sun8i-a33-mbus.c

Purpose: Allwinner sun8i/sun50i MBUS/DRAM devfreq driver. It performs DRAM frequency switching through MBUS MDFS registers and uses MBUS PMU peak bandwidth counters for simple-ondemand load feedback.

Important APIs and control flow: probe maps DRAM and MBUS register ranges, enables the bus clock, obtains DRAM/MBUS clocks, takes exclusive rate locks, builds dynamic OPPs from parent clock divided by allowed DRAM dividers, initializes hardware, registers a simple-ondemand devfreq device, and sets a dynamic suspend frequency. `sun8i_a33_mbus_set_dram_freq()` changes the DRAM clock rate, disables self-refresh/VTF, configures MDFS double-buffering, updates refresh timing, toggles ODT based on frequency and saved ODT map, starts MDFS, polls completion, restores VTF/self-refresh, restarts PMU counters, and updates nominal bandwidth. `sun8i_a33_mbus_get_dram_status()` reports peak PMU bandwidth as busy time and nominal bandwidth as total time.

State and persistence behavior: per-device state stores variant limits, MMIO bases, clocks, devfreq pointer, governor/profile data, DRAM data width, nominal bandwidth, saved ODT map, refresh timings, and flexible-array frequency table. Dynamic OPPs and devfreq state persist until remove, which restores the initial DRAM frequency.

Dependencies and integration points: depends on devfreq simple-ondemand, dynamic OPP helpers, clk exclusive-rate APIs, IO polling, platform named resources `dram` and `mbus`, module parameter `pmu_period`, and compatibles `allwinner,sun50i-a64-mbus` and `allwinner,sun50i-h5-mbus`.

Risks and test signals: PMU period is a module parameter with no range validation; bad values can program invalid periods or skew utilization. Frequency switching touches refresh, ODT, self-refresh, and VTF registers directly, so failures can affect memory stability. `data_width` can become zero if no DX lane is enabled. Test signals include dynamic OPP table contents, MDFS completion polling, refresh timing values by DRAM type, ODT enable threshold, PMU bandwidth under load, suspend clock gating, removal restoring initial frequency, and behavior with edge `pmu_period` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/sun8i-a33-mbus.c -->
