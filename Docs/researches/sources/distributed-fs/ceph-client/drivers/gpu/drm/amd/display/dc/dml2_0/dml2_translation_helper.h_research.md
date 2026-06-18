<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_translation_helper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_translation_helper.h

Purpose: exposes the DML2.0 translation boundary between DC state and DML structures.

Important APIs/types/functions: declares native initializers for IP params, SOC bounding box, and SOC states; legacy translators from `dc->dml`; `map_dc_state_into_dml_display_cfg()` for runtime stream/plane conversion; `dml2_update_pipe_ctx_dchub_regs()` for copying calculated RQ/DLG/TTU registers into a `pipe_ctx`; and `is_dp2p0_output_encoder()`.

Control flow: no direct runtime flow. Callers choose native construction versus translation through wrapper functions in `dml2_wrapper_fpu.c`.

State and persistence behavior: no state in the header. Declared functions mutate `dml2_context`, `dml_display_cfg_st`, and `pipe_ctx` data passed by the caller.

Dependencies and integration points: intentionally relies on surrounding includes for DC/DML type declarations. It is included by DML2 wrapper, utility, and translation implementation files.

Risks and test signals: since the header does not include all dependent type definitions, include ordering matters. Build signals should cover all translation users, especially when adding fields to DML register structs or DC pipe contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_translation_helper.h -->
