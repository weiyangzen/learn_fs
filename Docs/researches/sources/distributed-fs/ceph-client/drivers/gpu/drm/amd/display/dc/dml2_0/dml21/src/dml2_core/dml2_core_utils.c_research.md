# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_utils.c

## Purpose
Implements reusable core helpers for display format classification, logging support reasons, clock/table lookup, swizzle/tile traits, implicit SubVP expansion, encoder/link classification, ODM classification, and frame-time calculation. These helpers reduce duplication across DCN4 core calculators.

## Important APIs, types, and functions
- Format helpers: `dml2_core_utils_is_420()`, `dml2_core_utils_is_422_planar()`, `dml2_core_utils_is_422_packed()`, and `dml2_core_utils_is_dual_plane()` classify DML source formats and assert on unknown cases.
- Debug/string helpers: `dml2_core_utils_internal_bw_type_str()`, `dml2_core_utils_internal_soc_state_type_str()`, and `dml2_core_utils_print_mode_support_info()` map enums/support flags to verbose log text.
- Numeric helpers: `dml2_core_utils_div_rem()`, `dml2_core_utils_round_to_multiple()`, and `dml2_core_utils_log_and_substract_if_non_zero()` wrap common arithmetic.
- Mapping helpers: `dml2_core_util_get_num_active_pipes()` sums `dpps_used`; `dml2_core_utils_pipe_plane_mapping()` expands plane support into a pipe-to-plane array using the no-plane sentinel.
- Surface/tile helpers: `dml2_core_utils_is_phantom_pipe()`, `dml2_core_utils_get_tile_block_size_bytes()`, `dml2_core_utils_get_segment_horizontal_contiguous()`, `dml2_core_utils_is_linear()`, `dml2_core_utils_is_vertical_rotation()`, and `dml2_core_utils_get_gfx_version()` classify tiling, rotation, and phantom pipes.
- Clock/QoS helpers: `dml2_core_utils_get_qos_param_index()` and `dml2_core_utils_get_active_min_uclk_dpm_index()` map UCLK values to QoS/min-clock indices.
- Output/link helpers: `dml2_core_utils_get_stream_output_bpp()`, `dml2_core_utils_is_stream_encoder_required()`, `dml2_core_utils_is_encoder_dsc_capable()`, `dml2_core_utils_is_dp_encoder()`, `dml2_core_utils_is_dio_dp_encoder()`, `dml2_core_utils_is_hpo_dp_encoder()`, `dml2_core_utils_is_dp_8b_10b_link_rate()`, and `dml2_core_utils_is_dp_128b_132b_link_rate()`.
- `dml2_core_utils_expand_implict_subvp()` copies a display config and adds phantom streams/planes for implicit SubVP stage3 metadata.
- `dml2_core_utils_is_odm_split()` identifies split/MSO ODM modes, and `dml2_core_utils_get_frame_time_us()` derives frame duration from timing.

## Control flow and integration
Most functions are pure classifiers or mutators of caller-owned arrays. The notable multi-step flow is implicit SubVP expansion: copy the base config, reset scratch maps, optionally force unbounded requesting off before stage3, create phantom streams from valid `stage3.stream_svp_meta`, create matching phantom planes with MALL refresh disabled/no-data-return SVP mode, map phantom/main indices in scratch, and mark original planes as main pipes.

## State and persistence behavior
The helpers do not own persistent state. They mutate supplied arrays, `dml2_display_cfg`, and `dml2_core_scratch` structures. `expand_implict_subvp()` is stateful through scratch mapping arrays and increments `num_streams`/`num_planes` in the expanded config.

## Dependencies
Includes `dml2_core_utils.h`, which pulls internal shared types, debug logging, and float math. It relies on DML enums for source format, swizzle, rotation, encoder, DP link rate, ODM mode, p-state, and SubVP/MALL overrides.

## Risks and edge cases
Several format classifiers assert on unknown formats, so adding a new source format requires updating all switch statements. `dml2_core_utils_get_segment_horizontal_contiguous()` ignores `sw_mode` and returns `byte_per_pixel != 2`, which may be intentional but should be validated against future tiling modes. `get_active_min_uclk_dpm_index()` asserts if the exact UCLK is absent. `expand_implict_subvp()` can increase stream/plane counts and depends on capacity in fixed arrays; it also disables unbounded requesting before stage3 is performed.

## Test signals
Unit tests should exercise every source format, swizzle, encoder, link-rate, and ODM enum value. Integration tests should verify implicit SubVP expansion for no metadata, one SVP stream, multiple planes on a stream, stage3-performed versus not performed, and phantom-plane viewport height math. Clock-index tests should include exact matches, missing UCLK assertion paths, and zero-terminated QoS parameter tables.
