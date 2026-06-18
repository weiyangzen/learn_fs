# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_resources.c

## Purpose
Provides low-level resource helpers for interconnect bandwidth, OPP rate selection, PM-domain enable/disable, and logical clock enable/disable.

## Important APIs And Functions
- `iris_set_icc_bw()` clamps requested `"video-mem"` bandwidth to platform min/max, suppresses small changes below `BW_THRESHOLD`, updates `core->power.icc_bw`, and calls `icc_bulk_set_bw()`.
- `iris_unset_icc_bw()` clears all ICC votes.
- `iris_opp_set_rate()` resolves a recommended OPP for a frequency and applies it with `dev_pm_opp_set_opp()`.
- `iris_enable_power_domains()` sets max OPP then runtime-resumes a PM-domain device.
- `iris_disable_power_domains()` sets zero OPP then runtime-puts the PM-domain device.
- `iris_get_clk_by_type()` maps an Iris logical clock type to a runtime `struct clk *` using platform clock-name tables and devm bulk clocks.
- `iris_prepare_enable_clock()` and `iris_disable_unprepare_clock()` wrap clock lookup plus enable/disable.

## Control Flow And Integration Points
Probe fills `core->icc_tbl`, `core->clock_tbl`, `core->pmdomain_tbl`, and OPP config. Power scaling calls `iris_set_icc_bw()` and `iris_opp_set_rate()`. VPU generation power-on/off code uses PM-domain and clock helpers to sequence hardware.

## State And Persistence Behavior
Mutates aggregate `core->power.icc_bw` and the in-memory ICC bulk table. Clock and PM-domain references are devm/probe state; helpers do not persist additional state.

## Dependencies
Linux clk, devfreq/OPP, interconnect, PM-domain, PM runtime, reset includes, and `iris_core` platform data.

## Risks
- `iris_enable_power_domains()` returns negative `pm_runtime_get_sync()` errors without balancing a failed get, matching common kernel risk patterns.
- `iris_opp_set_rate(ULONG_MAX)` assumes an OPP table can resolve a max rate.
- Clock lookup depends on exact string matches between platform data and DT.
- `BW_THRESHOLD` suppresses small vote changes, which can hide expected test-observed transitions.

## Test Signals
- PM-domain and clock enable failure injection should unwind in VPU power code.
- Trace ICC votes for clamp and threshold behavior.
- Validate every logical clock used by platform VPU ops resolves on each SoC.
