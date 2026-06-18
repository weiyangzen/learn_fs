# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn301/dcn301_fpu.h

## Purpose
This header declares the DCN301 FPU-only bandwidth, bounding-box, watermark-range, and watermark/DLG calculation functions. It separates public call sites from the floating-point implementation file.

## Important APIs, Types, And Functions
- `dcn301_fpu_init_soc_bounding_box(struct bp_soc_bb_info bb_info)` applies BIOS latency data.
- `dcn301_fpu_update_bw_bounding_box(struct dc *dc, struct clk_bw_params *bw_params)` updates the DML SoC/IP bounding box from clock-manager data.
- `dcn301_fpu_set_wm_ranges(int i, struct pp_smu_wm_range_sets *ranges, struct _vcs_dpi_soc_bounding_box_st *loaded_bb)` fills SMU watermark range bounds for a clock state.
- `dcn301_fpu_calculate_wm_and_dlg(struct dc *dc, struct dc_state *context, display_e2e_pipe_params_st *pipes, int pipe_cnt, int vlevel_req)` computes DCN301 watermarks and DLG data.

## Control Flow
The header has no runtime behavior. It publishes functions that callers must invoke under the display core FPU protection protocol.

## State And Persistence
No state is stored in the header. The implementation mutates DCN301 global bounding-box data and `dc`/`context` state.

## Dependencies And Integration Points
The prototypes reference `struct dc`, `struct clk_bw_params`, `struct pp_smu_wm_range_sets`, `struct _vcs_dpi_soc_bounding_box_st`, `struct dc_state`, and `display_e2e_pipe_params_st`. The file is intended for DCN301 resource and clock-management code that already has the relevant type definitions in scope.

## Risks And Edge Cases
The header does not itself enforce FPU entry/exit discipline; callers must follow the implementation contract and call only while FPU access is enabled. Signature drift would break DCN301 resource wiring and SMU watermark range programming.

## Test Signals
Build tests should include this header from DCN301 resource code and ensure all prototypes match definitions. Runtime tests should verify that each declared function asserts or behaves correctly when used in the expected FPU-enabled context.
