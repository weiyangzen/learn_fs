# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/dcn314_fpu.c

## Purpose

`dcn314_fpu.c` provides DCN 3.14 floating-point DML setup and pipe-population policy. It defines the DCN 3.14 IP capability table, the SoC bounding box defaults, the runtime clock/bandwidth bounding-box update path, and a wrapper around DCN 3.1x pipe population that applies DCN 3.14-specific vblank, HostVM, immediate-flip, DET buffer, DCC, DSC, and ODM policies.

This file is used by display validation paths that are allowed to run floating-point DML code. It customizes the generic DML model for DCN 3.14 hardware limits and for platform clock data supplied by the clock manager/SMU.

## Important APIs, Types, And Functions

- `dcn3_14_ip`: global `_vcs_dpi_ip_params_st` instance describing DCN 3.14 display IP limits, buffer sizes, VM capabilities, scaler limits, DSC count, line buffer properties, chunk sizes, DPP/OTG/WB counts, latency constants, and DCC support.
- `dcn3_14_soc`: static `_vcs_dpi_soc_bounding_box_st` with default voltage states and SoC-level timing/bandwidth/latency parameters.
- `dcn314_update_bw_bounding_box_fpu(dc, bw_params)`: public update entry point. It copies dynamic clock table and memory topology data into the DCN 3.14 bounding box, patches it, and initializes `dc->dml` for `DML_PROJECT_DCN314`.
- `dcn314_populate_dml_pipes_from_context_fpu(dc, context, pipes, validate_mode)`: public pipe-population entry point. It calls the DCN 3.1x base population routine and then applies DCN 3.14 adjustments to each active pipe and to the context DML IP fields.
- `is_dual_plane(format)`: local helper treating video formats and `SURFACE_PIXEL_FORMAT_GRPH_RGBE_ALPHA` as dual-plane.
- `micro_sec_to_vert_lines(num_us, timing)`: converts a microsecond budget into vertical lines for the supplied timing, rounding up.
- `get_vertical_back_porch(timing)`: derives vertical back porch from total/active/front-porch/sync timing fields.

## Control Flow

`dcn314_update_bw_bounding_box_fpu` first asserts that floating-point execution is enabled. If the debug/config path is not using the default clock table, it updates IP counts from the resource pool, copies DRAM channel width and channel count from `bw_params`, and scans the SMU clock table for maximum DISPCLK and DPPCLK. For each clock table entry it finds the closest existing voltage state by DCFCLK, handles the one-entry SMU table case as the highest state, and fills a new clock-limit entry with voltage-dependent DCFCLK/FCLK/SOCCLK/DRAM speed plus voltage-independent maximum display clocks and inherited PHY/DSC/DTB values. It then copies the generated entries back to `dcn3_14_soc.clock_limits` and updates `num_states`.

After optional clock-table replacement, `dcn314_update_bw_bounding_box_fpu` sets the DISPCLK/DPPCLK VCO speed when a maximum DISPCLK was found, calls `dcn20_patch_bounding_box`, and initializes `dc->dml` with `dml_init_instance(..., DML_PROJECT_DCN314)`.

`dcn314_populate_dml_pipes_from_context_fpu` also asserts FPU availability, delegates initial pipe filling to `dcn31x_populate_dml_pipes_from_context`, and then iterates the resource pool pipe array. For each active stream it:

- Converts the default vblank nominal microsecond budget into lines.
- Chooses `vtotal` from `stream->adjust.v_total_min` when present, otherwise timing `v_total`.
- Computes a constrained `vblank_nom`, ensuring it is no larger than the nominal budget, no smaller than vsync plus back porch plus two guard lines, and no larger than 1023.
- Tracks whether any plane is upscaled.
- Applies HostVM policy from hypervisor state or rIOMMU unless overridden.
- Forces source `immediate_flip = true`.
- Clears unbounded request mode and DCC zero-size fractions, records front porch, sets `dcc_rate = 3`, and derives DSC input bits-per-component from timing color depth when DSC is enabled.

After per-pipe updates, it sets the context DET buffer size to the DCN 3.14 default. It then applies special policies: a single non-rotated, non-dual-plane plane at width <= 5120 can reduce DET to 192KB and enable unbounded request mode to avoid an unnecessary pipe split; debug CRB allocation policy can choose a multiple of 64KB for multi-display cases; three or more streams with upscaling also reduce DET to 192KB. A debug flag can force ODM 4:1 support. Finally, it scans streams for seamless boot eDP ODM 2:1 policy and writes `context->bw_ctx.dml.vba.ODMCombinePolicy` when requested.

## State And Persistence Behavior

This file mutates process-global DML model data and caller-owned display context state:

- `dcn3_14_ip` is a global IP parameter table. Its `max_num_otg` and `max_num_dpp` fields are updated from the current resource pool when the dynamic clock table path is used.
- `dcn3_14_soc` is a static SoC bounding box. Its memory topology, clock limits, number of states, and VCO-related fields are updated from `bw_params` and later used to initialize `dc->dml`.
- `dc->dml` is reinitialized for DCN 3.14 and has its VCO speed updated when available.
- `context->bw_ctx.dml.ip` fields such as `det_buffer_size_kbytes` and `odm_combine_4to1_supported` are changed during pipe population.
- Individual `pipes[]` entries are modified for destination vtotal/vblank, HostVM, immediate flip, unbounded request mode, DCC rates/fractions, front porch, and DSC input BPC.
- `context->bw_ctx.dml.vba.ODMCombinePolicy` may be set for seamless boot eDP ODM behavior.

There is no on-disk persistence. The global/static model mutation means repeated validation for different devices or debug configurations must be carefully sequenced by the driver.

## Dependencies And Integration Points

The file includes clock manager, resource, DCN 3.1 hubbub, its own header, DCN 2.0 and 3.1 FPU helpers, display mode VBA definitions, and DML inline math. Key dependencies include:

- `struct dc`, `struct dc_state`, `struct clk_bw_params`, `struct clk_limit_table`, `struct resource_context`, `struct pipe_ctx`, `struct dc_crtc_timing`.
- Resource pool capabilities such as timing generator count and pipe count.
- Debug/config fields such as `use_default_clock_table`, `dml_hostvm_override`, `disable_z9_mpc`, `crb_alloc_policy_min_disp_count`, `crb_alloc_policy`, `force_odm_combine_4to1`, and `seamless_boot_odm_combine`.
- VM/Hubbub state: `dc->vm_pa_config.is_hvm_enabled`, `dc->res_pool->hubbub->riommu_active`.
- Shared DML routines: `dcn20_patch_bounding_box`, `dml_init_instance`, `dcn31x_populate_dml_pipes_from_context`, `dml_ceil`.
- Display signal/format/depth enums and ODM policy enums.

It integrates with DCN 3.14 validation and bandwidth paths. Downstream DML mode support and watermarks rely on the context and pipe fields populated here.

## Risks And Edge Cases

- The static `dcn3_14_soc` and global `dcn3_14_ip` are mutated at runtime. Multi-device or repeated validation paths need to ensure one device's dynamic table does not unexpectedly leak into another context.
- `dcn314_update_bw_bounding_box_fpu` copies clock entries into `dcn3_14_soc.clock_limits` without an explicit local bound against the array length visible in this file. Correctness relies on `clk_table->num_entries` respecting the SoC table capacity.
- The closest-clock loop uses a signed `int j` and decrements to `-1`; the current condition is conventional, but future type changes could break the loop.
- `dram_speed_mts` is updated only when both `memclk_mhz` and `wck_ratio` are nonzero. Entries with missing values inherit prior/default state and may misrepresent bandwidth.
- In `dcn314_populate_dml_pipes_from_context_fpu`, most per-active-pipe writes use `pipes[pipe_cnt]`, but the HostVM write uses `pipes[i]`. If inactive pipes appear before active pipes and the DML pipe array is compacted by `pipe_cnt`, this can write the wrong element.
- `micro_sec_to_vert_lines` uses integer storage for a value calculated from floating arithmetic. Timing extremes or very small pixel clocks can produce coarse rounding.
- `get_vertical_back_porch` assumes total blanking is at least front porch plus sync width. Invalid timing data can underflow unsigned arithmetic.
- Forcing `immediate_flip = true` is deliberately conservative for underflow avoidance, but it can increase bandwidth requirements and reject modes that might otherwise pass without immediate flip support.
- The DET buffer special cases are policy-heavy and debug-influenced. Small changes can alter pipe split decisions, unbounded request mode, and bandwidth validation outcomes.
- DSC input BPC supports only 8, 10, and 12 bpc. Any other enabled-DSC color depth asserts and leaves the value at zero in non-debug behavior.

## Test Signals

- Build tests catch FPU header/API drift, missing enum values, and structure field changes.
- DML unit tests should validate bounding-box updates from representative SMU clock tables, including one-entry tables, missing memory clock fields, maximum DISPCLK/DPPCLK selection, and DRAM channel overrides.
- Pipe population tests should cover active pipe compaction, vtotal override, vblank clamping, HostVM override/no-override, rIOMMU activity, immediate flip, DSC bpc mapping, upscaled multi-stream policy, single 5K-or-less unbounded request mode, debug CRB allocation policy, forced ODM 4:1, and seamless boot ODM 2:1.
- Runtime validation signals include mode-support changes, watermark changes, unexpected pipe splitting, underflow reports, assertions around missing clock/channel data, and mismatched DML project initialization.
