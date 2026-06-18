<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_translation_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_translation_helper.c

Purpose: converts AMD DC state and legacy DML data into DML2.0 structures, initializes native IP/SOC defaults, applies bounding-box overrides, maps stream/plane identities between DC and DML indexes, and copies calculated DML RQ/DLG/TTU register fields back into DC pipe contexts.

Important APIs/types/functions: exported entry points are `dml2_init_ip_params()`, `dml2_init_socbb_params()`, `dml2_init_soc_states()`, `dml2_translate_ip_params()`, `dml2_translate_socbb_params()`, `dml2_translate_soc_states()`, `map_dc_state_into_dml_display_cfg()`, and `dml2_update_pipe_ctx_dchub_regs()`. Internal mapping helpers populate timing, output, surface, plane, writeback, HPO encoder, stream id, plane id, and pipe-to-plane-index tables.

Control flow: initialization chooses project-specific hardcoded IP/SOC values for DCN32/DCN321/DCN35/DCN351/DCN36/DCN401, applies override clock tables and latency overrides, then either copies independent DCN35-style states or calls the synthetic-state policy builder. Runtime mapping clears DML/DC mapping arrays, sets VM policy flags, builds scaling data, creates one DML timing per stream or per duplicated plane when needed, emits dummy planes for plane-less streams, maps surfaces from `dc_plane_state`, sets MALL policy for SubVP main/phantom streams, and records stream/plane ids for reverse lookup.

State and persistence behavior: writes persistent-for-validation data into `dml2->v20.dml_core_ctx`, `dml2->v20.scratch`, and caller-provided `dml_display_cfg_st`. `dml2_update_pipe_ctx_dchub_regs()` zeroes and repopulates `pipe_ctx` RQ, DLG, and TTU register caches.

Dependencies and integration points: depends on `display_mode_core.h`, `dml2_internal_types.h`, DC stream/plane/writeback/scaler/resource helpers, HPO DP encoder instances, DML struct layouts, and SubVP stream-type helpers. It is central to the wrapper FPU validation path.

Risks and test signals: many defaults are hardcoded and project-specific; wrong DCN version selection changes bandwidth support. Mapping arrays are size-limited by `__DML2_WRAPPER_MAX_STREAMS_PLANES__`; duplicated planes and MPO require exact plane-id handling. Some functions assume stream audio mode pointers, pipe state, and pixel clocks are valid. Test signals include DCN32/DCN35/DCN401 default initialization, override clock table ingestion, plane-less streams, MPO plane duplicates, SubVP main/phantom MALL flags, DP2/HPO encoder mapping, writeback mapping, and register-copy parity with DML getters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_translation_helper.c -->
