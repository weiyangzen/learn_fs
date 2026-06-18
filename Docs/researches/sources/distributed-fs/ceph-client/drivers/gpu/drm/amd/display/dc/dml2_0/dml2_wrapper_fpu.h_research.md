<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper_fpu.h

Purpose: declares the FPU-required DML2.0 initialization helpers used by the non-FPU wrapper to populate IP, SOC bounding box, and SOC state data.

Important APIs/types/functions: forward-declares `struct dml2_context`, `struct dc`, `struct ip_params_st`, `struct soc_bounding_box_st`, and `struct soc_states_st`. Exports `initialize_dml2_ip_params()`, `initialize_dml2_soc_bbox()`, and `initialize_dml2_soc_states()`.

Control flow: no direct flow. The implementation chooses native construction or legacy translation based on `dml2->config.use_native_soc_bb_construction`.

State and persistence behavior: no header state. Declared functions initialize persistent fields inside the DML core context supplied by the caller.

Dependencies and integration points: includes `os_types.h` and is included by `dml2_wrapper.c` and `dml2_wrapper_fpu.c`.

Risks and test signals: this header intentionally exposes only initialization helpers; validation helpers live in `dml2_wrapper.h`. Build coverage should ensure FPU separation rules remain valid for AMD DC build configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper_fpu.h -->
