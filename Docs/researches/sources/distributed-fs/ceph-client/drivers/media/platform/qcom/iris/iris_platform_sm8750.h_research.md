# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_sm8750.h

## Purpose
Provides SM8750-specific reset and clock tables used by the VPU35 platform descriptor.

## Important APIs And Data
- `sm8750_clk_reset_table` names `"bus0"`, `"bus1"`, `"core"`, and `"vcodec0_core"` resets.
- `sm8750_clk_table` maps logical clocks to `"iface"`, `"core"`, `"vcodec0_core"`, `"iface1"`, `"core_freerun"`, and `"vcodec0_core_freerun"`.

## Control Flow And Integration Points
`sm8750_data` in `iris_platform_gen2.c` uses these arrays. Probe resolves all clocks/resets, while VPU35 power-on/off code uses the logical clock types for AXI, hardware, and freerun clocks.

## State And Persistence Behavior
Static const platform tables; no runtime mutation.

## Dependencies
Depends on `struct platform_clk_data` and logical clock enum definitions from `iris_platform_common.h`.

## Risks
- SM8750 introduces additional AXI and freerun clocks. Missing logical-clock mapping causes `iris_prepare_enable_clock()` to fail during power-on.
- Reset names must stay synchronized with device-tree bindings.

## Test Signals
- Probe on SM8750 validates the clock/reset names.
- Firmware boot and runtime PM exercise VPU35 freerun clock enable/disable paths.
