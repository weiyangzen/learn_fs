# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/gk20a.c

## Purpose
Implements Tegra GK20A PMU support without firmware upload, using PMU falcon performance counters to drive simple DVFS.

## Important APIs, Types, And Functions
`struct gk20a_pmu` extends `nvkm_pmu` with an alarm and DVFS data. Key helpers are `gk20a_pmu_init()`, `gk20a_pmu_fini()`, `gk20a_pmu_dvfs_work()`, `gk20a_pmu_dvfs_get_dev_status()`, and `gk20a_pmu_dvfs_target()`.

## Control Flow
Init acquires the PMU falcon, programs busy/clock counter slots, and schedules a 2-second alarm. Each alarm reads busy and total counters, smooths utilization, maps load to a clock pstate, calls `nvkm_clk_astate()` when a level change is needed, resets counters, and reschedules after 100 ms.

## State, Persistence, And Dependencies
State lives in `gk20a_pmu`, the static DVFS tuning table, the current `nvkm_clk` pstate, falcon counter registers, and the timer alarm list. No filesystem persistence exists.

## Integration Points
Depends on nvkm clock, timer, volt, falcon, and subdev infrastructure. It integrates with GK20A SoC initialization and complements the Tegra regulator-backed voltage code.

## Risks
DVFS assumes performance level equals pstate and may behave poorly if clock states are sparse. It delays work until CLK and VOLT exist but still depends on timer availability. Counter overflow or unexpected falcon register behavior can skew load.

## Test Signals
Signals include pstate changes under GPU load, stable alarm rescheduling, no falcon acquisition errors, and sane utilization trace logs.
