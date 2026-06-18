# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/dml21_translation_helper.c

## Purpose
`dml21_translation_helper.c` translates AMD DC driver state into DML 2.1 display configuration and translates DML programming results back into `dc_state` bandwidth, watermark, p-state, and mcache-related fields. It is the bridge between kernel display objects and the DML2.1 core.

## Important APIs, types, and functions
Public functions include `dml21_populate_dml_init_params()`, `dml21_map_dc_state_into_dml_display_cfg()`, `map_plane_to_dml21_display_cfg()`, `dml21_copy_clocks_to_dc_state()`, `dml21_extract_watermark_sets()`, `dml21_map_hw_resources()`, `dml21_get_pipe_mcache_config()`, `dml21_set_dc_p_state_type()`, and `dml21_init_min_clocks_for_dc_state()`. Internal helpers map DCN revision to DML project ID, populate PMO options, convert timings/output formats/swizzles, derive scaler and plane descriptors, create dummy planes for blank streams, and map forced p-state policies.

## Control flow
Initialization selects a DML project from `in_dc->ctx->dce_version`, gets native or externally supplied SoC/IP data, and applies debug/config PMO options. Display mapping clears prior mappings, seeds GPUVM/HostVM/global overrides, iterates DC streams, populates stream timing/output/override descriptors, and then either creates a dummy plane for blank streams or maps each real plane through surface and plane descriptor population. Stable mappings are kept with stream IDs and synthesized plane IDs. Output copy functions then transfer DML clocks, watermarks, mcache pipe geometry, hardware resource mapping, and p-state method decisions into DC structures.

## State and persistence behavior
State is stored inside `dml2_context->v21`: `dml_init`, `display_config`, `dml_to_dc_pipe_mapping`, and mode-programming outputs. The file mutates `dc_state->bw_ctx` and `pipe_ctx` fields but has no durable persistence.

## Dependencies and integration points
It depends on DC core structures, debug flags, `soc_and_ip_translator`, DML internal shared types, DML2 top-level API structures, scaler callbacks, SVP/FAMS callbacks, and DC resource callbacks. It integrates with `dml21_wrapper_fpu.c` for validate/programming flow and `dml21_utils.c` for pipe programming.

## Risks and edge cases
Unsupported DCN revisions map to invalid project ID after logging. Timing conversion includes DSC padding, frame packing, DRR min refresh clamping, and optional flickerless vtotal callbacks. Swizzle conversion asserts for unsupported Addr3 modes and defaults some GFX9 unsupported modes to 64KB 2D for test compatibility. Blank streams get dummy planes and can affect counts. `dml21_map_hw_resources()` marks every mapping slot valid even when source validity is sparse. Plane ID encoding depends on stream/plane ordering remaining stable during validation.

## Test signals
Coverage should include DCN4.01 and DCN4.2 initialization, native and external SoC/IP paths, blank streams, multi-plane streams, DSC padding, VRR/Freesync/DRR, DP2.0 detection, HDMI/eDP/DP output mapping, Addr3 and GFX9 swizzles, forced p-state methods, HostVM/GPUVM levels, watermark set copies, mcache plane1 enablement, and p-state type mapping for vactive/vblank/SVP/DRR.
