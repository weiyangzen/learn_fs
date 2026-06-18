# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_power.c

## Purpose
Implements per-session and aggregate power scaling for Iris. It calculates DDR interconnect bandwidth and VPU clock votes from active queued input, then applies aggregate votes across all live sessions.

## Important APIs And Functions
- `iris_calc_bw()` converts resolution and fps to macroblocks per second and chooses a DDR bandwidth tier from the platform decoder bandwidth table.
- `iris_set_interconnects()` sums `instance->power.icc_bw` across sessions with `max_input_data_size` and calls `iris_set_icc_bw()`.
- `iris_vote_interconnects()` derives the current session vote from source format width/height at `DEFAULT_FPS`.
- `iris_set_clocks()` sums `instance->power.min_freq` and calls `iris_opp_set_rate()`.
- `iris_scale_clocks()` scans queued source buffers to find maximum compressed input data size, asks platform `vpu_ops->calc_freq()` for a frequency vote, and updates aggregate clocks.
- `iris_scale_power()` resumes runtime PM if needed, then scales clocks and interconnects.

## Control Flow And Integration Points
Codec queue paths call `iris_scale_power()` when buffers are queued or stream-on begins. The clock calculation delegates to VPU generation-specific `calc_freq` operations. Interconnect programming delegates to `iris_resources.c`. Aggregation is guarded by `core->lock` and only counts sessions that have observed input data.

## State And Persistence Behavior
Updates mutable per-instance `inst->max_input_data_size`, `inst->power.min_freq`, and `inst->power.icc_bw`, plus aggregate `core->power.clk_freq` and `core->power.icc_bw`. Votes persist until later scaling or teardown resets resources.

## Dependencies
Depends on V4L2 mem2mem queued-buffer iteration, PM runtime, `iris_resources` OPP/ICC helpers, platform bandwidth tables, and VPU generation ops.

## Risks
- `iris_calc_bw()` uses `DEFAULT_FPS` rather than actual session frame/operating rate, so bandwidth votes may be approximate.
- `iris_scale_power()` ignores the return value of `iris_scale_power(inst)` in `iris_vb2_start_streaming()` call sites, so failures may be hidden depending on caller.
- Aggregation skips sessions with zero `max_input_data_size`; early stream-on before input data may under-vote clocks.
- Table ordering in `bw_tbl_dec` controls selected ICC votes.

## Test Signals
- Instrument ICC/OPP votes while queueing different resolutions and compressed frame sizes.
- Multi-session tests should show aggregate clock and bandwidth increases.
- Runtime autosuspend/resume tests should verify scaling works after suspended state.
