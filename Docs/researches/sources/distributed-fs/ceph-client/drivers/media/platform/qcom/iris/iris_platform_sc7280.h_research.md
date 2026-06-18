# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_sc7280.h

## Purpose
Provides SC7280-specific bandwidth, OPP power-domain, clock, and OPP clock tables used by gen1 platform data.

## Important APIs And Data
- `sc7280_bw_table_dec` maps descending decode macroblocks-per-second breakpoints to DDR bandwidth votes.
- `sc7280_opp_pd_table` names the `"cx"` OPP power domain.
- `sc7280_clk_table` maps Iris logical clocks to `"core"`, `"iface"`, `"bus"`, `"vcodec_core"`, and `"vcodec_bus"`.
- `sc7280_opp_clk_table` uses `"vcodec_core"` for OPP rate selection.

## Control Flow And Integration Points
`sc7280_data` in `iris_platform_gen1.c` references these tables. Probe resolves their clock/PM-domain names from DT, power scaling reads the bandwidth table, and VPU/resource helpers look up logical clock types through `iris_prepare_enable_clock()`.

## State And Persistence Behavior
All data is static const and immutable at runtime.

## Dependencies
Requires `struct bw_info`, `struct platform_clk_data`, and `IRIS_*_CLK` enum definitions from `iris_platform_common.h`.

## Risks
- DT clock names must match these strings exactly; mismatches fail probe or VPU power transitions.
- Bandwidth points are consumed by a linear lookup in `iris_power.c`; table ordering matters.

## Test Signals
- SC7280 probe validates clock and OPP-domain names.
- Decode workloads at 1080p/4K and 30/60 fps should produce the expected ICC vote tiers.
