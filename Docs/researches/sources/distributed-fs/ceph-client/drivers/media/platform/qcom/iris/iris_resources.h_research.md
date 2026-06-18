# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_resources.h

## Purpose
Declares resource-management helpers used by power, probe, and VPU generation code.

## Important APIs
- OPP: `iris_opp_set_rate()`.
- PM domains: `iris_enable_power_domains()`, `iris_disable_power_domains()`.
- ICC: `iris_set_icc_bw()`, `iris_unset_icc_bw()`.
- Clocks: `iris_prepare_enable_clock()`, `iris_disable_unprepare_clock()`.

## Control Flow And Integration Points
Included by platform, power, and VPU files. The functions are implemented in `iris_resources.c` and operate on `iris_core` resources initialized by `iris_probe.c`.

## State And Persistence Behavior
No state in the header; callers mutate core resource state through the implementation.

## Dependencies
Requires `struct device`, `struct iris_core`, and `enum platform_clk_type` declarations from surrounding includes.

## Risks
Header users must include platform-common definitions before using clock-type APIs.

## Test Signals
Build coverage verifies function prototypes across VPU/power users.
