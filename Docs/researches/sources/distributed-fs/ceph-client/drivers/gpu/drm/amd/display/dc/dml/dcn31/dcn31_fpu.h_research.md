# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/dcn31_fpu.h

## Purpose
This header declares the public DCN31x FPU entry points and shared constants for DET and compbuf sizing. It is the versioned interface used by DCN31, DCN315, and DCN316 resource code.

## Important APIs, Types, And Functions
- Constants: `DCN3_1_DEFAULT_DET_SIZE`, `DCN3_15_DEFAULT_DET_SIZE`, `DCN3_15_MIN_COMPBUF_SIZE_KB`, `DCN3_16_DEFAULT_DET_SIZE`, and `DCN3_16_MIN_COMPBUF_SIZE_KB`.
- Watermark/DLG functions: `dcn31_zero_pipe_dcc_fraction()`, `dcn31_update_soc_for_wm_a()`, `dcn315_update_soc_for_wm_a()`, and `dcn31_calculate_wm_and_dlg_fp()`.
- Bounding-box update functions: `dcn31_update_bw_bounding_box_fpu()`, `dcn315_update_bw_bounding_box_fpu()`, and `dcn316_update_bw_bounding_box_fpu()`.
- Utility functions: `dcn_get_max_non_odm_pix_rate_100hz()` and `dcn_get_approx_det_segs_required_for_pstate()`.
- Pipe population hook: `dcn31x_populate_dml_pipes_from_context()`, declared here but implemented elsewhere.

## Control Flow
The header has no runtime control flow. It groups all DCN31x FPU APIs behind one include so resource code can select version-specific update functions and shared calculation helpers.

## State And Persistence
No state is stored in this header. The implementation updates DML SoC/IP descriptors and caller-owned display-core state.

## Dependencies And Integration Points
The declarations depend on DML pipe types, `struct dc`, `struct dc_state`, clock bandwidth parameters, DML SoC bounding-box structs, and `enum dc_validate_mode`. It bridges DCN31x resource construction/validation code to the FPU implementation and to the pipe-population helper.

## Risks And Edge Cases
- FPU discipline is not encoded in the type system; callers must invoke these functions only inside the required DC FPU section.
- Shared constants influence hardware buffer partitioning and must stay aligned with the versioned IP descriptors in the `.c` file.
- `dcn31x_populate_dml_pipes_from_context()` being declared but not defined in this file means integration depends on another compilation unit.

## Test Signals
Build checks should ensure all declared functions resolve for DCN31x configurations. Runtime coverage should exercise each versioned bounding-box update function, WM_A update variant, DLG calculation entry, and utility calculations through resource validation paths.
