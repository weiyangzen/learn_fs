<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_utils.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_utils.h

Purpose: declares shared DML2.0 helper routines for DML config copying, clock/watermark extraction, RQ/DLG calculation, DET policy, pipe construction hooks, and timing predicates.

Important APIs/types/functions: public functions include DML array copy helpers, `dml2_util_get_maximum_odm_combine_for_output()`, `dml2_copy_clocks_to_dc_state()`, `dml2_extract_watermark_set()`, `dml2_extract_writeback_wm()`, `dml2_helper_find_dml_pipe_idx_by_stream_id()`, `is_dtbclk_required()`, `dml2_is_stereo_timing()`, `dml2_calc_max_scaled_time()`, `dml2_calculate_rq_and_dlg_params()`, DET allocation/verification helpers, and declarations for resource-building helpers such as `dml2_dc_construct_pipes()`, `dml2_predict_pipe_split()`, and `dml2_build_mapped_resource()`.

Control flow: no direct control flow, but comments document how DML validation maps hardware resources and then calls these helpers to build DC pipe programming.

State and persistence behavior: no header-owned state. The declared functions mutate DC state, DML context scratch, clocks, watermarks, and pipe register caches.

Dependencies and integration points: includes `os_types.h` and `dml2_dc_types.h`, forward-declares core DC/DML structs, and is used by wrapper, translation, resource-management, and SubVP code.

Risks and test signals: several declared resource helpers are not implemented in this specific file, so link coverage must include the companion DML2 resource-management sources. Header comments contain older DML1 phrasing and should be kept aligned with the actual validation flow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_utils.h -->
