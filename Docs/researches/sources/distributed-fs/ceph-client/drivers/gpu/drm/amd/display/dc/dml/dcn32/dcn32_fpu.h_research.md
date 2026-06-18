# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/dcn32_fpu.h

Purpose: declares the DCN32 floating-point helper surface used by resource validation, clock management, SubVP/FPO policy, watermark/DLG programming, and bounding-box updates.

Important APIs/types/functions: includes `clk_mgr_internal.h` and exposes functions operating on `struct clk_mgr_internal`, `struct dc`, `struct dc_state`, `struct pipe_ctx`, `struct dc_stream_state`, `struct clk_bw_params`, `display_e2e_pipe_params_st`, and `_vcs_dpi_soc_bounding_box_st`. Key exported routines are `dcn32_build_wm_range_table_fpu`, `dcn32_internal_validate_bw`, `dcn32_calculate_wm_and_dlg_fpu`, `dcn32_update_bw_bounding_box_fpu`, `dcn32_patch_dpm_table`, SubVP/FPO helpers, and clock-limit/memclk override helpers.

Control flow: the header has no executable flow, but its API order reflects the normal pipeline: build watermark ranges, populate phantom timing/DLG data when SubVP is used, validate bandwidth and pipe topology, compute watermarks/DLG registers, update bounding boxes from firmware/platform data, and apply policy helpers for FPO/SubVP and memory-clock constraints.

State and persistence: no storage is defined in the header. Implementations mutate caller-owned DC state, clock-manager bandwidth params, DML contexts, and static DCN32 bounding boxes.

Dependencies and integration: guarded by `__DCN32_FPU_H__`. This header is consumed by DCN32 resource and clock-management code that must run these functions with FPU access enabled. It bridges display core resource objects with DML pipe arrays and SoC/IP bounding-box structures.

Risks: these declarations expose many mutable state pointers; callers must pass arrays sized for active pipes and keep `pipe_cnt`/`vlevel` synchronized with the current DML context. Calling without the required FPU guard or before DML pipe population can corrupt validation results. Signature changes ripple into resource validation and clock-manager code.

Test signals: compile coverage for DCN32 resource integration, bandwidth-validation tests that call `dcn32_internal_validate_bw`, clock-table update tests for `dcn32_update_bw_bounding_box_fpu`, and modeset stress that exercises SubVP/FPO, DLG/RQ programming, and memory-clock override behavior.
