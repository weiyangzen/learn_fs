# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn35/dcn35_fpu.h

## Purpose
This header declares the DCN35 FPU hooks for watermark table setup, bandwidth bounding-box update, DML pipe population, and z-state policy. It is the public interface used by DCN35 resource code to enter the FPU-heavy DML support routines.

## Important APIs, Types, And Functions
Exports `dcn35_build_wm_range_table_fpu(struct clk_mgr *clk_mgr)`, `dcn35_update_bw_bounding_box_fpu(struct dc *dc, struct clk_bw_params *bw_params)`, `dcn35_populate_dml_pipes_from_context_fpu(struct dc *dc, struct dc_state *context, display_e2e_pipe_params_st *pipes, enum dc_validate_mode validate_mode)`, and `dcn35_decide_zstate_support(struct dc *dc, struct dc_state *context)`.

## Control Flow And State
The header has no behavior. Its declarations map to implementation routines that mutate global DCN35 IP/SOC state, DML/DML2 bounding boxes, DML pipe arrays, DET policy, and `context->bw_ctx.bw.dcn.clk.zstate_support`.

## Dependencies And Integration Points
It includes `clk_mgr.h`, which supplies clock manager and display-core type declarations. Resource code wraps these functions in FPU entry/exit helpers before calling them.

## Risks
All declared functions are FPU-sensitive by implementation convention, but the header itself does not enforce that. The watermark table function is declared publicly despite being a no-op/TODO in the implementation.

## Test Signals
Compile-time integration should ensure DCN35 resource tables bind these declarations. Runtime checks should confirm callers enter FPU-safe regions, and that the no-op watermark function is not the only source of required watermark programming.
