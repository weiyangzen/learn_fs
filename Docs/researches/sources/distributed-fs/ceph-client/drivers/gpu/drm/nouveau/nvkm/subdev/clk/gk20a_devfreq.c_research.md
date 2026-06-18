# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a_devfreq.c

## Purpose
Implements devfreq support for GK20A-family Tegra GPUs by measuring PMU idle counters and feeding the Linux simple_ondemand governor with GPU utilization and OPP frequencies.

## Important APIs, types, and functions
Defines `struct gk20a_devfreq`, `gk20a_devfreq_init()`, `gk20a_devfreq_resume()`, `gk20a_devfreq_suspend()`, profile callbacks `gk20a_devfreq_target()`, `gk20a_devfreq_get_cur_freq()`, and `gk20a_devfreq_get_dev_status()`, plus PMU counter helpers.

## Control flow
Init allocates managed state, records Tegra register base, registers one OPP per pstate, initializes idle counters, seeds initial frequency, and registers a delayed devfreq device. Status reads total and busy counters, treats overflow or inconsistent counters as fully busy, converts normalized cycles to busy/total time, resets counters, and returns current frequency. Target selects the first pstate at or above the requested frequency and updates both AC and DC user states.

## State and persistence
Persistent state includes devfreq pointer, MMIO base, governor thresholds, busy/total time, and last update timestamp. PMU idle counters and interrupt status are reset each sample.

## Dependencies and integration points
Depends on Linux devfreq/OPP APIs, DRM-managed allocation, Nouveau DRM device data, Tegra register mapping, `nvkm_clk_ustate()`, and GP10B/GK20A clock object lookup by chipset.

## Risks
The debug print divides by `total_time / 100`, so extremely small sampling windows are risky. Targeting mutates both AC and DC user states, which overrides separate power-source preferences. Counter overflow intentionally reports 100% busy.

## Test signals
OPP table creation, devfreq sysfs frequency changes, governor polling at 50 ms, suspend/resume calls, PMU counter overflow handling, and rate agreement between requested pstate and `get_cur_freq()`.
