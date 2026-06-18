# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_platform_sm8650.h

## Purpose
Supplies SM8650-specific reset-name tables used by `sm8650_data`.

## Important APIs And Data
- `sm8650_clk_reset_table` lists `"bus"` and `"core"` resets.
- `sm8650_controller_reset_table` lists the `"xo"` controller reset.

## Control Flow And Integration Points
`iris_platform_gen2.c` assigns these arrays to `.clk_rst_tbl` and `.controller_rst_tbl` for `sm8650_data`. `iris_probe.c` resolves them via `iris_init_resets()`, and VPU33 controller power-off code asserts/deasserts the controller reset during low-power teardown.

## State And Persistence Behavior
Static const reset-name data, immutable for module lifetime.

## Dependencies
The arrays are plain string tables but their meaning depends on reset-controller entries in SM8650 DT and VPU33 power code.

## Risks
- Missing or renamed DT resets cause probe failure or incomplete controller reset handling.
- The `"xo"` reset is only used when `controller_rst_tbl_size` is nonzero, so size propagation in platform data is critical.

## Test Signals
- SM8650 probe succeeds with all reset controls resolved.
- Runtime suspend/resume and close/open loops exercise VPU33 controller reset handling.
