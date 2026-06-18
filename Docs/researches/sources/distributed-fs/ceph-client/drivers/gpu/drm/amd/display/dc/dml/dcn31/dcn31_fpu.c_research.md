# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/dcn31_fpu.c

## Purpose
This file centralizes DCN 3.1, 3.1.5, and 3.1.6 floating-point DML operations. It defines versioned IP and SoC bounding boxes, updates those bounding boxes from clock-manager data, computes watermarks and DLG parameters, handles pstate/z8 behavior, and exposes utility calculations for maximum non-ODM pixel rate and DET segments needed to hide pstate latency.

## Important APIs, Types, And Functions
- Versioned IP descriptors: `dcn3_1_ip`, `dcn3_15_ip`, and `dcn3_16_ip`.
- Versioned SoC descriptors: `dcn3_1_soc`, `dcn3_15_soc`, and `dcn3_16_soc`.
- Public functions: `dcn31_zero_pipe_dcc_fraction()`, `dcn31_update_soc_for_wm_a()`, `dcn315_update_soc_for_wm_a()`, `dcn31_calculate_wm_and_dlg_fp()`, `dcn31_update_bw_bounding_box_fpu()`, `dcn315_update_bw_bounding_box_fpu()`, `dcn316_update_bw_bounding_box_fpu()`, `dcn_get_max_non_odm_pix_rate_100hz()`, and `dcn_get_approx_det_segs_required_for_pstate()`.
- Key external dependencies include DML helpers for watermarks, stutter, clocks, DET size, and `dcn20_calculate_dlg_params()`.

## Control Flow
The file starts by documenting the FPU containment pattern: public functions assert FPU access, while callers must perform the FPU begin/end wrapping. The bounding-box update functions for 3.1 and 3.1.6 copy default clock limits to scratch, update IP resource counts and channel counts, scan max DISPCLK/DPPCLK, map SMU entries to default voltage states, fill voltage-dependent and independent clocks, apply VCO/debug latency overrides, and initialize DML. The 3.1.5 update path writes directly into `dcn3_15_soc`, uses max DISPCLK/DPPCLK for all states to avoid ODM lowering voltage, derives DSCCLK from DISPCLK, and sets the DML VCO to twice max DISPCLK.

`dcn31_calculate_wm_and_dlg_fp()` selects the active DCFCLK from DML VBA state data and min DCFCLK, handles zero-pipe configs by lowering blocking clocks, updates DML SoC latency for WM_A through the resource-pool hook, calculates watermark set A including Z8 stutter timing and urgent/meta/bandwidth fractions, clones set A into B/C/D, fills per-pipe DISPCLK/DPPCLK with forced/min-clock overrides, calls `dcn20_calculate_dlg_params()`, records pstate-change support, zeros clocks when there are streams but no active HUBP planes, then updates per-pipe DET buffer size and remaining compbuf size.

## State And Persistence
The versioned SoC/IP descriptors are mutable static/global state. Update functions persistently rewrite clock limits, resource counts, memory topology, VCO speed, and latency overrides before reinitializing `dc->dml`. `dcn31_calculate_wm_and_dlg_fp()` mutates `context->bw_ctx`, `pipes`, per-pipe `det_buffer_size_kb`, and clock fields. It does not allocate memory or persist data outside display-core state.

## Dependencies And Integration Points
This file integrates DCN31/315/316 resource definitions, clock-manager bandwidth parameters, DML VBA-calculated voltage-level data, debug knobs, and common DCN20 DLG calculation. It is the FPU boundary for DCN31x resource validation. Resource pools provide `update_soc_for_wm_a()` so DCN315 can use dummy pstate latency unless vactive pstate change is supported.

## Risks And Edge Cases
- All public functions require an active FPU context; misuse can violate kernel FPU rules.
- `dcn31_zero_pipe_dcc_fraction()` indexes `pipes[pipe_cnt]`, which appears to expect a current pipe index despite the parameter name and could be risky if passed a count.
- The zero-pipe path sets only DCFCLK and returns early; callers must tolerate partial clock updates.
- WM sets B/C/D are copied from set A rather than independently calculated, which is a deliberate DCN31x policy but differs from DCN301.
- Active stream without active plane forces several clocks to zero and enables pstate change; this is power-sensitive behavior that needs validation for blanking/phantom streams.
- DET buffer sizes over 384 KiB are halved before total DET subtraction, so compbuf accounting depends on DML DET outputs and hardware limits.
- Clock-table assertions require nonzero entries; state arrays must fit the DML voltage-state capacity.

## Test Signals
Test DCN31, DCN315, and DCN316 clock-table ingestion separately, including max clock fallback, WCK ratio memory-speed conversion, debug latency overrides, min/forced display clocks, zero-pipe validation, active stream with no active plane, WM_A latency update differences, Z8 residency clamping, pstate-change support, DET/compbuf accounting, and utility functions. Golden vectors should compare watermarks, clocks, and DLG parameters across DCN31x variants.
