# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn351/dcn351_fpu.h

## Purpose
This compact header declares DCN351 FPU hooks for bandwidth bounding-box update, DML pipe population, and z-state policy. It exposes the DCN351-specific counterparts to the DCN35 FPU routines.

## Important APIs, Types, And Functions
Exports `dcn351_update_bw_bounding_box_fpu(struct dc *dc, struct clk_bw_params *bw_params)`, `dcn351_populate_dml_pipes_from_context_fpu(struct dc *dc, struct dc_state *context, display_e2e_pipe_params_st *pipes, enum dc_validate_mode validate_mode)`, and `dcn351_decide_zstate_support(struct dc *dc, struct dc_state *context)`.

## Control Flow And State
The header has no local behavior. Implementations update mutable DCN351 global IP/SOC bounding boxes, DML/DML2 clock and latency state, per-context DML pipe fields, DET policy, and z-state support.

## Dependencies And Integration Points
It includes `clk_mgr.h` for the display and clock type declarations needed by the prototypes. DCN351 resource code uses these declarations inside FPU-safe wrappers.

## Risks
The interface does not advertise that the implementation initializes DML as `DML_PROJECT_DCN31` or that z-state support is DCN351-restricted. Callers must pick the DCN351 functions rather than the similar DCN35 functions when SoC-specific clocks and z-state policy matter.

## Test Signals
Compile integration should verify DCN351 resource tables bind these hooks. Runtime checks should confirm the DCN351 update path uses `dcn3_51_soc`/`dcn3_51_ip` and that z-state policy differs from DCN35 where required.
