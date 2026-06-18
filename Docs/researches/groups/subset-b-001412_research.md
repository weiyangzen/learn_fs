# Research: subset-b-001412

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_mode_vba_31.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_mode_vba_31.h

## Purpose

`display_mode_vba_31.h` is the public DCN 3.1 Display Mode Library VBA header. It declares the generation-specific entry points that run the DCN 3.1 mode-support and system-configuration calculations and exposes the writeback DISPCLK helper used by display validation and bandwidth programming code.

The file is intentionally small. It is a contract header for the large `display_mode_vba_31.c` implementation and lets other DML/DCN code call DCN 3.1 VBA logic without depending on implementation-private functions.

## Important APIs, Types, And Functions

- `dml31_recalculate(struct display_mode_lib *mode_lib)`: recalculates the current `display_mode_lib` VBA state after inputs have been populated.
- `dml31_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)`: runs the full DCN 3.1 mode-support and system-configuration pass.
- `dml31_CalculateWriteBackDISPCLK(...)`: computes the DISPCLK requirement for writeback from writeback pixel format, pixel clock, horizontal/vertical ratios, filter taps, source/destination widths, total timing width, and writeback line-buffer size.
- `struct display_mode_lib` and `enum source_format_class`: referenced but not defined here; callers must include the broader DML headers that provide those definitions before or alongside this header.

## Control Flow

There is no executable control flow in this header. Compile-time control flow is limited to the include guard `__DML31_DISPLAY_MODE_VBA_H__`. Runtime behavior is entirely in the implementation file that provides these declarations.

The expected call pattern is that DCN 3.1 resource validation code populates `struct display_mode_lib`, calls the full mode-support pass or recalculation entry point, and then reads derived VBA fields. Writeback code can call `dml31_CalculateWriteBackDISPCLK` independently when sizing writeback clock requirements.

## State And Persistence Behavior

This header owns no state and performs no persistence. The declared functions operate on caller-owned `struct display_mode_lib` instances or scalar writeback parameters. Persistent effects, if any, are in the implementation and are expected to be in-memory DML state updates only.

## Dependencies And Integration Points

The header is part of AMDGPU Display Core's DML generation split under `dcn31`. It integrates with:

- DCN 3.1 VBA implementation code.
- DML callers that hold a `struct display_mode_lib`.
- Writeback validation paths that need a DCN 3.1-specific DISPCLK calculation.
- Neighbor headers such as `display_mode_lib.h`, `display_mode_vba.h`, and generation FPU/resource code that provide concrete types and call sites.

## Risks And Edge Cases

- The header forward-uses `struct display_mode_lib` and `enum source_format_class` without including their definitions. This is fine for translation units that already include DML base headers, but include-order mistakes can produce build errors.
- Function declarations are generation-specific. Accidentally wiring DCN 3.0 or DCN 3.14 callers to these declarations can silently apply the wrong hardware model if signatures still match.
- `dml31_CalculateWriteBackDISPCLK` takes a mix of `double`, `unsigned int`, and `long` values. Callers must preserve units and avoid truncation before invoking it.

## Test Signals

- Kernel build coverage catches missing type declarations, signature drift from the implementation, and incorrect include ordering.
- DML validation tests should compare DCN 3.1 mode-support results and writeback DISPCLK values against known-good tables.
- Runtime issues would usually surface outside this header as rejected modes, unexpected writeback clock requests, or mismatches between DCN generation-specific validation and hardware programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_mode_vba_31.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_rq_dlg_calc_31.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_rq_dlg_calc_31.c

## Purpose

`display_rq_dlg_calc_31.c` calculates DCN 3.1 request-queue, display logic generator, and TTU register values from DML pipe descriptions. It converts source surface geometry, tiling, viewport, scaling, cursor, VM, ODM, and timing data into packed register fields for luma/chroma request sizing, detile-buffer allocation, meta/PTE request grouping, prefetch timing, delivery timing, and QoS watermarks.

The file is a bridge between abstract DML/VBA calculations and hardware register programming. It contains two public entry points: one for RQ registers for a single pipe source, and one for DLG/TTU registers for a selected pipe in a compacted end-to-end pipe array.

## Important APIs, Types, And Functions

- `dml31_rq_dlg_get_rq_reg(mode_lib, rq_regs, pipe_param)`: public RQ calculation entry point. It zeroes the output register struct, derives `display_rq_params_st`, extracts register fields, and prints the result through DML debug helpers.
- `dml31_rq_dlg_get_dlg_reg(mode_lib, dlg_regs, ttu_regs, e2e_pipe_param, num_pipes, pipe_idx, cstate_en, pstate_en, vm_en, ignore_viewport_pos, immediate_flip_support)`: public DLG/TTU entry point. It gathers system watermark values from VBA helper getters, builds RQ parameters for the selected pipe, then fills DLG and TTU register structs.
- `dml_rq_dlg_get_rq_params(...)`: private coordinator for per-surface RQ sizing. It detects dual-plane formats, calculates luma and optional chroma/alpha parameters, then splits detile buffer space.
- `get_surf_rq_param(...)`: chooses viewport, pitch, metadata pitch, surface height, chunk sizes, and MPTE group size for luma, chroma, or RGBE alpha.
- `get_meta_and_pte_attr(...)`: main geometry routine for swath bounds, meta row/chunk counts, meta PTE bytes, DPTE request shape, DPTE row height, DPTE group size, and upper-bound row/group counts.
- `handle_det_buf_split(...)`: decides whether luma/chroma requests can stay at full 256B swath granularity or must use 128B behavior to fit the detile buffer, then writes stored swath bytes and swath heights.
- `extract_rq_sizing_regs(...)` and `extract_rq_regs(...)`: convert byte counts and derived RQ/DLG values into packed register encodings such as chunk size, meta chunk size, group sizes, PTE row height, swath height, expansion modes, and plane1 base address.
- `dml_rq_dlg_get_dlg_params(...)`: main DLG/TTU timing routine. It derives refclock-to-pixel ratios, vblank fields, prefetch parameters, delivery rates, VM/meta/PTE cycles, cursor delivery rates, QoS fields, and fixed-point register encodings.
- `get_refcyc_per_delivery(...)`: shared delivery-cycle calculator for per-line and per-request delivery, with distinct logic for vertical ratio <= 1, vertical scaling > 1, and ODM combine.
- `calculate_ttu_cursor(...)`: derives cursor request size and delivery timing for 2-bit and 32-bit cursors.
- `is_dual_plane(...)` and `get_blk_size_bytes(...)`: local helpers for format and tile-size classification.

The code relies on DML structures such as `display_mode_lib`, `display_pipe_params_st`, `display_e2e_pipe_params_st`, `display_rq_regs_st`, `display_dlg_regs_st`, `display_ttu_regs_st`, `display_rq_params_st`, and their nested luma/chroma sizing, DLG, and misc structs.

## Control Flow

RQ calculation starts at `dml31_rq_dlg_get_rq_reg`. The function clears the output, calls `dml_rq_dlg_get_rq_params`, then calls `extract_rq_regs`. `dml_rq_dlg_get_rq_params` always calculates luma and conditionally calculates chroma/alpha for `dm_420_8`, `dm_420_10`, `dm_420_12`, and `dm_rgbe_alpha`. It then calls `handle_det_buf_split` to fit the active swaths into the configured DET buffer.

Per-surface RQ calculation in `get_surf_rq_param` selects the relevant viewport and pitch fields, adjusts width/height for ODM combine, sets fixed chunk policy (`8192` bytes normally and `4096` bytes for alpha), selects metadata and PTE chunk sizes, and delegates to `get_meta_and_pte_attr`. That routine first asks the DCN 3.0 helper for bytes per element and 256B block dimensions. It then computes the swath upper bound based on scan direction and pitch/surface constraints, calculates metadata request/row/chunk geometry, estimates meta PTE bytes per frame, and calculates DPTE request dimensions for linear, 4KB tile, >=64KB tile with 4KB pages, and 64KB-page cases. HostVM and vertical tiled access can force smaller DPTE groups.

`handle_det_buf_split` compares two swaths of luma and optional chroma against `mode_lib->ip.det_buffer_size_kbytes`. If the swaths fit, both planes retain full request size. If not, it halves luma or chroma swath storage depending on format and luma/chroma byte ratio, then derives luma/chroma swath heights from 256B block dimensions and scan direction. For 10bpc YUV420 it applies a packed 3-to-2 swath-byte adjustment before the fit test.

DLG/TTU calculation starts at `dml31_rq_dlg_get_dlg_reg`. It fills `display_dlg_sys_params_st` from VBA getters such as urgent watermark, deepsleep DCFCLK, extra latency, memory trip, DRAM clock-change watermark, stutter watermark, and immediate-flip totals. It then recalculates RQ params for the selected pipe and calls `dml_rq_dlg_get_dlg_params`.

`dml_rq_dlg_get_dlg_params` zeroes the output register structs, extracts source/destination/clock/scaler/tap pointers for `pipe_idx`, encodes refclock/pixel ratios, vblank end, min next-start, and vready-after-vcount0. For ODM combine it builds a pipe-index map by hsplit group so `refcyc_h_blank_end` accounts for each ODM slice. It reads prefetch and VM/row timing values from VBA getters, asserts the key ranges, calculates luma/chroma line and request delivery cycles, optionally handles dynamic metadata VM timing, and derives cursor delivery timing when a cursor is present.

The final stage packs all DLG/TTU values into hardware register units: U/fixed-point encodings for destination Y fields and vratio prefetch, refcycles per PTE/meta/vm group, nominal row timing, prefetch and active line delivery, cursor chunk handling, TTU request delivery, QoS watermarks, QoS fixed levels, ramp-disable flags, and `min_ttu_vblank`.

## State And Persistence Behavior

The file has no durable persistence and no static mutable state. It mutates only caller-provided output structs and stack-local calculation structs:

- `display_rq_regs_st` in `dml31_rq_dlg_get_rq_reg`.
- `display_dlg_regs_st` and `display_ttu_regs_st` in `dml31_rq_dlg_get_dlg_reg`.
- Temporary `display_rq_params_st` and `display_dlg_sys_params_st`.
- Nested sizing fields such as `rq_sizing_param->dpte_group_bytes`, which are later converted into register encodings.

The calculations read `mode_lib->ip` and `mode_lib->soc`, especially DET size, page size, PTE buffer capacities, and GPUVM page sizing. Hardware-facing persistence happens later when other display code programs these register values.

## Dependencies And Integration Points

The file includes `display_mode_lib.h`, `display_mode_vba.h`, `dml_inline_defs.h`, its own header, and DCN 3.0 VBA helpers. It depends heavily on:

- DML math helpers: `dml_log2`, `dml_floor`, `dml_ceil`, `dml_min`, `dml_round_to_multiple`, `dml_pow`.
- Debug/print helpers: `dml_print`, `print__data_rq_sizing_params_st`, `print__rq_params_st`, `print__rq_regs_st`, `print__dlg_sys_params_st`, `print__ttu_regs_st`, `print__dlg_regs_st`.
- DCN 3.0 helper `dml30_CalculateBytePerPixelAnd256BBlockSizes`.
- VBA result getters such as `get_min_ttu_vblank_in_us`, `get_dst_y_prefetch`, `get_vratio_prefetch_l`, `get_refcyc_per_vm_group_vblank_in_us`, and many related line/request delivery helpers.
- Hardware-facing DML register structs declared in `display_rq_dlg_helpers.h` and broader DML headers.

It integrates with DCN 3.1 resource validation and hubp/hubbub programming paths. The output register structs are the values later consumed by generation-specific display code that writes RQ, DLG, and TTU registers for each active pipe.

## Risks And Edge Cases

- Several public flags to `dml31_rq_dlg_get_dlg_reg` are currently cast unused inside `dml_rq_dlg_get_dlg_params` (`cstate_en`, `pstate_en`, `vm_en`, `ignore_viewport_pos`, `immediate_flip_support`). If callers expect these to alter prefetch mode directly, behavior instead depends on precomputed VBA getter state.
- Many calculations assume nonzero pitch, viewport, request count, chunk size, and vertical ratio values. Invalid upstream DML inputs can cause divide-by-zero, invalid log2, or underflowed unsigned encodings.
- Register range checks are mostly `ASSERT` calls. In non-debug builds, values may be clamped only in selected VM paths; other oversized fields can be truncated when assigned to hardware register structs.
- The code uses upper-bound geometry and multiple rounding rules. Off-by-one changes around pitch smaller than block width, surface height smaller than viewport height, vertical access, or ODM slices can materially affect swath/PTE pressure.
- HostVM and vertical tiled access reduce DPTE group bytes to 512. Incorrect HostVM propagation from callers will change memory request grouping and can affect underflow behavior.
- `surface_height = pipe_param->src.surface_height_y / 2.0` for chroma/alpha is assigned to an unsigned int. That implicit floating expression relies on truncation semantics and may be surprising for odd heights.
- Dual-plane handling includes `dm_rgbe_alpha` alongside YUV420 formats. The code names many fields chroma even when the second plane is alpha, which increases maintenance risk.
- The code contains comments marking old implementation comparisons, TODOs, and "magic" limits for small `htotal`; these are signs that some behavior is inherited from hardware model alignment rather than obvious first principles.
- ODM combine handling assumes the hsplit group order maps cleanly to pipe order and uses a 2-or-4 factor. Bad hsplit metadata can place the wrong horizontal blank offset on a pipe.

## Test Signals

- Build coverage should catch signature drift between this file and `display_rq_dlg_calc_31.h`, missing DML helper declarations, and struct field renames.
- Unit-style DML tests should compare RQ/DLG/TTU outputs for representative linear, 4KB tiled, 64KB tiled, horizontal/vertical scan, HostVM on/off, GPUVM on/off, compressed/uncompressed, single-plane, YUV420, RGBE alpha, and ODM combine cases.
- Regression tests should pin boundary cases: small pitches, odd chroma dimensions, cursor widths at 16/17/31/32/256, DET buffer fit thresholds, 10bpc YUV420 packed swath sizing, and register range limits.
- Hardware or simulation validation should watch for underflow, incorrect prefetch timing, VM/PTE starvation, cursor fetch issues, and mode rejection/acceptance mismatches against known-good DCN 3.1 DML spreadsheets.
- Runtime diagnostic signals include DML debug prints, `WARNING: DML_DLG` messages for ignored pitch/surface constraints, and assertions around refcycle fields, row timing, cursor width, and prefetch relationships.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_rq_dlg_calc_31.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_rq_dlg_calc_31.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_rq_dlg_calc_31.h

## Purpose

`display_rq_dlg_calc_31.h` declares the DCN 3.1 RQ/DLG/TTU calculation interface. It is the public header for `display_rq_dlg_calc_31.c`, allowing display validation and hardware programming code to request computed register values for one pipe source or one pipe in a complete end-to-end pipe set.

## Important APIs, Types, And Functions

- Includes `../display_rq_dlg_helpers.h`, which supplies `display_rq_regs_st`, `display_dlg_regs_st`, `display_ttu_regs_st`, `display_pipe_params_st`, and `display_e2e_pipe_params_st`.
- Forward declares `struct display_mode_lib`.
- `dml31_rq_dlg_get_rq_reg(mode_lib, rq_regs, pipe_param)`: computes request queue register fields from one source pipe configuration.
- `dml31_rq_dlg_get_dlg_reg(mode_lib, dlg_regs, ttu_regs, e2e_pipe_param, num_pipes, pipe_idx, cstate_en, pstate_en, vm_en, ignore_viewport_pos, immediate_flip_support)`: computes display logic generator and TTU register fields for `pipe_idx` using the full compacted active-pipe array and policy flags.

## Control Flow

This header has no runtime control flow. It exposes two calculation entry points under the include guard `__DML31_DISPLAY_RQ_DLG_CALC_H__`.

The API-level flow implied by the declarations is:

1. Callers populate DML pipe parameters and a `struct display_mode_lib`.
2. Callers invoke `dml31_rq_dlg_get_rq_reg` when they need RQ register fields for a pipe source.
3. Callers invoke `dml31_rq_dlg_get_dlg_reg` with the compacted pipe array, active pipe count, selected pipe index, and validation policy flags when they need DLG and TTU register fields.
4. Callers program the returned register structs through generation-specific hardware code.

## State And Persistence Behavior

The header does not own state. Its functions write caller-provided output structs and read caller-owned DML inputs. There is no allocation, reference ownership, or on-disk persistence in this interface.

## Dependencies And Integration Points

This header is a DCN 3.1 generation-specific interface in AMD Display Core. It integrates with:

- The DML RQ/DLG helper type definitions.
- DCN 3.1 RQ/DLG implementation.
- Resource validation code that constructs `display_e2e_pipe_params_st`.
- Hardware programming code that consumes `display_rq_regs_st`, `display_dlg_regs_st`, and `display_ttu_regs_st`.

The comments explicitly frame `dml31_rq_dlg_get_rq_reg` as a main entry point for tests to obtain register values, so it also supports DML regression harnesses.

## Risks And Edge Cases

- The header does not validate `pipe_idx < num_pipes`, non-null pointers, or fully populated input structs. All such validation is the caller's responsibility.
- The `cstate_en`, `pstate_en`, `vm_en`, `ignore_viewport_pos`, and `immediate_flip_support` parameters imply policy control, but the current implementation treats several of them as unused inside the DLG calculation. Callers should not assume these flags independently override precomputed VBA values unless the implementation changes.
- Because this is a generation-specific header, including it from the wrong DCN generation can create subtle model mismatches even when types and signatures compile.

## Test Signals

- Compile tests catch declaration/definition mismatches and missing helper type includes.
- Unit tests can call the declared functions with synthetic DML inputs and compare output register structs against known DCN 3.1 cases.
- Integration tests should confirm the RQ/DLG/TTU outputs from these APIs match the register programming expected by DCN 3.1 hubp/hubbub/display timing code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_rq_dlg_calc_31.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/dcn314_fpu.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/dcn314_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/dcn314_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/dcn314_fpu.h

## Purpose

`dcn314_fpu.h` declares the DCN 3.14 floating-point DML hooks and defines DCN 3.14 DET/compbuf/CRB sizing constants. It is the public interface used by DCN 3.14 resource and validation code to update the bandwidth bounding box and populate DML pipe parameters from a `dc_state`.

## Important APIs, Types, And Functions

- `DCN3_14_DEFAULT_DET_SIZE`: default DET buffer size in KB, `384`.
- `DCN3_14_MAX_DET_SIZE`: maximum DET buffer size in KB, `384`.
- `DCN3_14_MIN_COMPBUF_SIZE_KB`: minimum compressed buffer size in KB, `128`.
- `DCN3_14_CRB_SEGMENT_SIZE_KB`: CRB segment size in KB, `64`.
- `dcn314_update_bw_bounding_box_fpu(struct dc *dc, struct clk_bw_params *bw_params)`: updates the DCN 3.14 DML bounding box from runtime clock/bandwidth parameters.
- `dcn314_populate_dml_pipes_from_context_fpu(struct dc *dc, struct dc_state *context, display_e2e_pipe_params_st *pipes, enum dc_validate_mode validate_mode)`: fills and adjusts DML pipe parameters from a display context and returns the active pipe count.

The header references `struct dc`, `struct clk_bw_params`, `struct dc_state`, `display_e2e_pipe_params_st`, and `enum dc_validate_mode`, all of which must be defined by surrounding DC/DML includes.

## Control Flow

There is no runtime control flow in the header. It uses the include guard `__DCN314_FPU_H__` and exposes constants plus two function prototypes.

The implied integration flow is:

1. Validation setup calls `dcn314_update_bw_bounding_box_fpu` after clock/bandwidth data is available.
2. Mode validation calls `dcn314_populate_dml_pipes_from_context_fpu` to translate `dc_state` into DML pipe arrays using DCN 3.14 policy.
3. Later DML validation and register calculation consume the populated `display_e2e_pipe_params_st` data.

## State And Persistence Behavior

This header owns no mutable state. Its constants are compile-time sizing policy. The declared functions mutate `dc->dml`, static/global model data in the implementation, `context->bw_ctx`, and caller-provided pipe arrays, but those behaviors are implemented in `dcn314_fpu.c`.

## Dependencies And Integration Points

The file is part of AMD Display Core's DCN 3.14 DML/FPU layer. It integrates with:

- DCN 3.14 resource validation code.
- Clock manager bandwidth parameter flow.
- DML pipe arrays and validation modes.
- DET/compbuf/CRB sizing policy used by the implementation and neighboring DCN 3.14 code.

Because it is an FPU header, callers must follow the driver's FPU access rules before invoking the declared functions.

## Risks And Edge Cases

- The header does not include the type definitions it references. Include order must provide `struct dc`, `struct clk_bw_params`, `struct dc_state`, `display_e2e_pipe_params_st`, and `enum dc_validate_mode`.
- Constants here must remain synchronized with the implementation's `dcn3_14_ip` defaults and DET/CRB policy. Divergence can create confusing validation behavior.
- The functions require floating-point execution to be enabled by the caller/implementation path; calling them from a non-FPU-safe context would violate kernel display-driver rules.
- The pipe population function returns an `int` active pipe count, so callers must handle zero or failure-like counts according to the surrounding validation convention.

## Test Signals

- Compile coverage catches signature drift and missing include dependencies.
- DCN 3.14 validation tests should assert that the declared constants match expected DET and CRB policy.
- Integration tests should call the declared functions through the normal resource validation path and verify resulting DML project, bounding-box, and pipe-array behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/dcn314_fpu.h -->
