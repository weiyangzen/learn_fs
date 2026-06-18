# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.h

## Purpose

`dcn30_resource.h` declares the public DCN 3.0 resource-pool interface and generation-specific helper APIs for validation, DML population, writeback, bandwidth bounding boxes, MPC 3D LUT resources, stream addition, and firmware-assisted mclk switching.

## Important APIs, Types, And Functions

- `TO_DCN30_RES_POOL()` casts a generic pool to `struct dcn30_resource_pool`.
- Extern `dcn3_0_ip` and `dcn3_0_soc` expose DCN3 DML IP and SoC bounding-box data.
- `dcn30_create_resource_pool()` constructs the resource pool.
- Validation and DML APIs include `dcn30_validate_bandwidth()`, `dcn30_internal_validate_bw()`, `dcn30_calculate_wm_and_dlg()`, `dcn30_update_soc_for_wm_a()`, `dcn30_populate_dml_pipes_from_context()`, and `dcn30_populate_dml_writeback_from_context()`.
- Writeback APIs include `dcn30_set_mcif_arb_params()` and `dcn30_calc_max_scaled_time()`.
- Resource APIs include `dcn30_add_stream_to_ctx()`, `dcn30_acquire_post_bldn_3dlut()`, and `dcn30_release_post_bldn_3dlut()`.
- Clock/bounding-box and mclk-switch APIs include `dcn30_update_bw_bounding_box()`, `dcn30_can_support_mclk_switch_using_fw_based_vblank_stretch()`, `dcn30_setup_mclk_switch_using_fw_based_vblank_stretch()`, and `dcn30_find_dummy_latency_index_for_fw_based_mclk_switch()`.

## Control Flow

The header has no executable control flow. DC initialization uses the constructor, the resource function table dispatches to validation/watermark/DML helpers, and feature code can call the mclk-switch and 3D LUT helpers around mode validation or commit preparation.

## State And Persistence Behavior

The header stores no state. Declared functions mutate DC resource pools, DML state, bandwidth/watermark state, pipe topology, writeback arbitration structures, MPC LUT/shaper acquisition state, and stream status. The extern DML globals are mutable generation-wide data patched by runtime clock and platform information.

## Dependencies And Integration Points

The header includes `core_types.h` and forward-declares resource and DML pipe types. It is included by DCN30 implementation and by common DC paths that need generation-specific validation, DML population, or mclk-switch support.

## Risks And Edge Cases

- Several declarations require FPU discipline in their implementations; callers should use the resource vtable unless they know the wrapper behavior.
- `dcn30_internal_validate_bw()` mutates topology and expects valid output pointers and a populated pipe array.
- The 3D LUT acquire/release API couples LUT and shaper pointers; callers must release both as a pair.
- Firmware-assisted mclk-switch helpers depend on current context assumptions such as single stream and valid timing.
- Extern bounding boxes should not be treated as immutable hardware constants after clock-table updates.

## Test Signals

Compile coverage catches prototype drift. Runtime tests should exercise the declared functions through resource-pool callbacks and direct feature paths: validation, watermark calculation, DML population, writeback arbitration, 3D LUT acquisition/release, bounding-box updates, stream addition, and mclk-switch eligibility/setup.
