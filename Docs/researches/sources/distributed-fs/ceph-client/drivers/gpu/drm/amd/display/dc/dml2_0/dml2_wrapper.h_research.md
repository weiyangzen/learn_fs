<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper.h

Purpose: defines the DML2 public configuration, callback, clock, MALL, bounding-box override, and lifecycle/validation interface shared with AMD DC.

Important APIs/types/functions: key structs are `dml2_soc_mall_info`, `dml2_dcn_clocks`, `dml2_dc_callbacks`, `dml2_dc_svp_callbacks`, `dml2_clks_limit_table`, `dml2_soc_bbox_overrides`, and `dml2_configuration_options`. Public functions include `dml2_create()`, `dml2_destroy()`, `dml2_copy()`, `dml2_create_copy()`, `dml2_reinit()`, `dml2_validate()`, `dml2_extract_dram_and_fclk_change_support()`, `dml2_prepare_mcache_programming()`, debug/validate helpers, and `dml2_allocate_memory()`.

Control flow: no direct flow, but the callback tables define how DML2 requests DC operations: build scaling params, allocate secondary MPC/ODM pipes, query stream/plane topology, create/release phantom SubVP resources, and allocate MCACHE.

State and persistence behavior: the configuration struct is copied into `dml2_context` and persists across validation until reinit or destroy. Callback function pointers are trusted runtime integration state.

Dependencies and integration points: includes `os_types.h` and forward-declares DC resource types. It bridges DML2 with resource pool, pipe, stream, plane, DSC, MALL/SubVP, PMO, GPUVM/HOSTVM, and DML2.1 debug data.

Risks and test signals: most failures come from incomplete callback initialization or mismatched pipe counts. `DML2_MAX_NUM_DPM_LVL` bounds override clock tables. Test signals should verify callback tables are fully populated per ASIC, SubVP callbacks are null-safe when disabled, clock override tables do not exceed limits, and DML2.0/DML2.1 callers share compatible lifecycle semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper.h -->
