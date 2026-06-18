# Research: subset-b-001407

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_rq_dlg_calc_21.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_rq_dlg_calc_21.c

## Purpose

This file implements the DCN 2.1 Display Mode Library request queue, display logic generator, and time-to-use register calculations. It translates high-level pipe state, surface layout, memory/VM parameters, scaler ratios, timing, and clock data into `display_rq_regs_st`, `display_dlg_regs_st`, and `display_ttu_regs_st` values consumed by the AMD display pipeline. The source explicitly warns that it is hardware-provided formula code and intentionally does not follow normal kernel style; preserving the formulas matters more than stylistic cleanup.

The implementation has two exported entry points: `dml21_rq_dlg_get_rq_reg()` for request queue register fields and `dml21_rq_dlg_get_dlg_reg()` for DLG/TTU timing registers. Everything else is static helper code that computes byte geometry, swath sizes, meta/PTE request grouping, detile buffer allocation, prefetch timing, cursor request timing, and fixed-point register encoding.

## Important APIs, Types, and Functions

The public API is the pair declared in the companion header. `dml21_rq_dlg_get_rq_reg()` receives a `display_mode_lib`, output `display_rq_regs_st`, and a single `display_pipe_params_st`; it zeroes output state, computes internal `display_rq_params_st`, extracts register encodings, and emits debug prints. `dml21_rq_dlg_get_dlg_reg()` receives an array of compacted end-to-end pipe params plus flags for cstate and pstate behavior. It builds `display_dlg_sys_params_st` from DML watermark helpers, computes per-pipe RQ state again, and fills DLG and TTU outputs for the requested pipe.

Key static helpers are:

- `get_bytes_per_element()` maps `enum source_format_class` and luma/chroma selection to element byte size for 4:4:4 and 4:2:0 formats.
- `is_dual_plane()` identifies 4:2:0 formats that need luma and chroma plane calculations.
- `get_refcyc_per_delivery()` computes reference-clock cycles per line or request, switching formulas for vertical ratio greater than 1.0 and for ODM combine.
- `extract_rq_sizing_regs()` and `extract_rq_regs()` encode byte-sized RQ sizing parameters into hardware register fields using log2-based encodings.
- `handle_det_buf_split()` decides stored swath bytes and swath height based on detile buffer size, 128-byte request fallback, surface scan direction, and 4:2:0 special handling.
- `get_meta_and_pte_attr()` is the central geometry routine for swath width, meta request rows/chunks, meta PTE frame bytes, data PTE request shape, row height, group width, and PTE group bytes.
- `get_surf_rq_param()` selects luma or chroma viewport/pitch, handles ODM split viewport adjustment, fixes chunk sizes, and calls `get_meta_and_pte_attr()`.
- `dml_rq_dlg_get_dlg_params()` is the large DLG/TTU timing routine. It gathers timing/scaler/clock data, computes vblank prefetch and active delivery timing, handles cursor TTU, clamps several register fields, and writes fixed-point register fields.
- `calculate_ttu_cursor()` derives cursor request width, request count, and prefetch/active delivery cycles for 2-bit and 32-bit cursors.

The code depends heavily on DML structures from `display_mode_structs.h`, helper prints from `display_rq_dlg_helpers.h`, math utilities from `dml_inline_defs.h`, and VBA-derived timing/watermark getters from `display_mode_vba.h`.

## Control Flow

The RQ path starts in `dml21_rq_dlg_get_rq_reg()`. It initializes a local `display_rq_params_st`, then `dml_rq_dlg_get_rq_params()` marks whether the source is 4:2:0 or 10-bit 4:2:0, computes luma request parameters, optionally computes chroma request parameters, and calls `handle_det_buf_split()`. After the internal request model is complete, `extract_rq_regs()` converts it to register encoding, including luma and chroma sizing fields, PTE row height, swath heights, request expansion modes, and the chroma plane base address in the detile buffer.

The meta/PTE geometry flow is nested inside `get_meta_and_pte_attr()`. It first obtains 256-byte block dimensions via `Calculate256BBlockSizes()`, chooses luma or chroma dimensions, computes macro tile block dimensions, and derives swath width/request count in horizontal or vertical access mode. It then computes meta request dimensions, row heights, chunks per row, meta surface byte upper bounds, and meta PTE bytes per frame. The PTE section derives virtual memory page shape and data PTE request shape for linear, 4 KiB tiled, 64 KiB tiled, 4 KiB page, and 64 KiB page cases. Finally it computes row request counts, row bytes, row height, group bytes, group width, and `dpte_groups_per_row_ub`.

The DLG path starts in `dml21_rq_dlg_get_dlg_reg()`, which gathers global system timing and watermark values via helper functions such as `get_wm_urgent()`, `get_clk_dcf_deepsleep()`, and immediate flip bandwidth helpers. It then computes RQ params for the target pipe and passes them to `dml_rq_dlg_get_dlg_params()`. That routine builds OTG-dependent fields first (`ref_freq_to_pix_freq`, `refcyc_per_htotal`, vblank boundaries, hblank end), then computes prefetch timing (`dst_y_prefetch`, VM and row contributions), luma/chroma active delivery, TTU request delivery, cursor delivery, PTE/meta group timing, VM group/request timing, nominal row timing, and QoS fields. Several values are encoded as fixed point, commonly using `2^2`, `2^8`, `2^10`, or `2^19` scale factors.

## State and Persistence Behavior

This file does not own durable state. It mutates only caller-owned output structures and local stack structures. The persistent effect is indirect: the register structs it fills are later programmed into display hardware by higher layers. It reads static configuration from `mode_lib->ip` and `mode_lib->soc`, and it reads per-pipe runtime state from `display_pipe_params_st` and `display_e2e_pipe_params_st`. Debug output is emitted through `dml_print()` and formula assumptions are enforced with `ASSERT()`.

There are no heap allocations, reference-counted resources, locks, file I/O, or hardware writes in this file. However, the calculations are stateful in the sense that DLG results depend on global mode-lib VBA cache/output values exposed through getter functions.

## Dependencies and Integration Points

This implementation is integrated through `display_mode_lib.c`, where the DML 2.1 function table assigns `.rq_dlg_get_dlg_reg = dml21_rq_dlg_get_dlg_reg` and `.rq_dlg_get_rq_reg = dml21_rq_dlg_get_rq_reg`. Callers use the function table rather than the static helpers directly. The file includes `display_mode_lib.h`, `display_mode_vba.h`, `dml_inline_defs.h`, and its own header, so it sits at the boundary between VBA mode evaluation and register programming.

External helpers supply hardware model values: `Calculate256BBlockSizes()`, `get_tcalc()`, `get_min_ttu_vblank()`, `get_dst_y_prefetch()`, VM/row/flip timing getters, urgent watermark getters, DSC delay getters, and calculated clock helpers. Its outputs are the canonical DML register model structures defined under `display_mode_structs.h`.

## Risks and Edge Cases

The main risk is arithmetic fragility. Many formulas assume positive, power-of-two, or bounded inputs and then use log2, shifts, divides, fixed-point casts, and register width assertions. Invalid pitch, viewport, chunk, page size, htotal, or ratio inputs can produce divide-by-zero, underflow, nonsensical log2 values, or assertion failures. Several paths intentionally clamp only selected values, such as VM register fields to 23 bits and low pixel-rate PTE group vblank timing to 13 bits.

4:2:0 handling is a risk area because luma/chroma detile split and chroma meta behavior include special cases and comments noting unsupported or approximate DCC behavior. ODM combine and hsplit behavior are also sensitive: `get_surf_rq_param()` adjusts viewport width/height based on half hactive and scaler ratio, while `dml_rq_dlg_get_dlg_params()` has a fallback that guesses `full_recout_width` for some hsplit cases. Cursor handling asserts cursor width <= 256 and has a comment questioning hactive treatment.

The file contains several TODO/FIXME comments around detile buffer chunk choice, writeback of chroma meta timing, urgent latency selection, min vblank assumptions, cursor handling, and whether chroma meta nominal timing should halve htotal. These are signals that behavior is hardware-tuned and regression-prone.

## Test Signals

Useful tests are DML golden-output comparisons for representative pipe configurations: linear and tiled surfaces, 4 KiB and 64 KiB page sizes, 4 KiB/64 KiB/256 KiB macro tiles, horizontal and vertical source scan, 4:4:4 and 4:2:0 formats, 8/10/16/32/64 bpp classes, DCC on/off, host VM on/off, ODM combine, hsplit, interlaced timing, DSC, low htotal, high vertical scaling, and one/two cursor cases. Assertions should remain enabled in debug validation because they encode register width and timing feasibility constraints.

Integration signals include successful DML validation without underflow, stable `display_rq_regs_st`/`display_dlg_regs_st`/`display_ttu_regs_st` output against known-good hardware spreadsheets, no divide-by-zero or log2 assertion failures under fuzzed mode inputs, and display bring-up tests that exercise vblank, immediate flip, pstate/cstate watermarks, and cursor planes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_rq_dlg_calc_21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_rq_dlg_calc_21.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_rq_dlg_calc_21.h

## Purpose

This header exposes the DCN 2.1 request queue and DLG/TTU calculation interface to the rest of Display Mode Library. It is a narrow declaration file: it includes service/helper declarations, forward-declares `struct display_mode_lib`, and publishes the two functions implemented in `display_rq_dlg_calc_21.c`.

The file documents that these functions are the main entry points for tests and callers that need DML-calculated register values. It does not define data structures itself; it relies on shared DML typedefs such as `display_rq_regs_st`, `display_pipe_params_st`, `display_dlg_regs_st`, `display_ttu_regs_st`, and `display_e2e_pipe_params_st`.

## Important APIs, Types, and Functions

`dml21_rq_dlg_get_rq_reg()` calculates request queue register fields for one pipe source configuration. It takes a `display_mode_lib *`, an output `display_rq_regs_st *`, and a `const display_pipe_params_st *`. The comment describes it as the test-facing path that calls the internal RQ parameter and register extraction routines.

`dml21_rq_dlg_get_dlg_reg()` calculates DLG and TTU register structs for a selected pipe in a compacted pipe array. It takes output `display_dlg_regs_st *` and `display_ttu_regs_st *`, the end-to-end pipe array, pipe count, target pipe index, cstate/pstate enable flags, VM enable, viewport-position ignore flag, and immediate flip support flag. In this DCN 2.1 implementation the latter three flags are accepted for interface compatibility but are explicitly unused by the C file.

The header includes `dm_services.h` and `../display_rq_dlg_helpers.h`, which provide common AMD display service types, assertions, and DML register/helper declarations required for prototypes and callers.

## Control Flow

There is no executable control flow in this header. Its role is compile-time integration: include guards prevent duplicate declarations, and callers include it to bind to the DCN 2.1 implementation. The DML function table in `display_mode_lib.c` references the declarations when assigning the DCN 2.1 RQ/DLG callbacks.

## State and Persistence Behavior

The header has no state, storage, or persistence. It establishes an ABI-like source contract between DML core code and the DCN 2.1 implementation. The only state implications are in the pointer parameters: callers are responsible for providing valid mode-lib input and writable output register structs.

## Dependencies and Integration Points

This file is coupled to shared DML display mode structs and helper declarations. It is included by `display_rq_dlg_calc_21.c` and is also indirectly important to `display_mode_lib.c`, where DCN 2.1 function pointers are initialized. Its sibling headers for DCN20, DCN30, DCN31, and later generations follow a similar contract, which allows project-specific DML implementations to be swapped behind common function pointers.

## Risks and Edge Cases

The main header-level risk is signature drift. The C implementation currently ignores `vm_en`, `ignore_viewport_pos`, and `immediate_flip_support`; if callers assume those flags change behavior for DCN 2.1, they will get misleading results. Another risk is include-order fragility because the prototypes use DML typedefs that must be available through the included helper headers or prior includes.

## Test Signals

Compile coverage should verify that all users can include the header without missing typedefs. Functional tests should call both exported functions through the `display_mode_lib` callback table and directly in any DML unit harness, confirming that output structs are fully initialized and match golden register values for DCN 2.1 mode cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_rq_dlg_calc_21.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/dcn30_fpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/dcn30_fpu.c

## Purpose

This file contains DCN 3.0 Display Mode Library routines that require floating-point execution in the AMD display driver. It defines the DCN 3.0 IP and SOC bounding boxes used to initialize DML, translates runtime display/writeback state into DML structures, calculates watermarks and DLG parameters, updates bandwidth bounding boxes from clock tables and BIOS data, and builds power-management watermark range tables.

The file is part of the DCN30 resource/DML integration layer. It is not a generic math library: each function asserts floating-point access with `dc_assert_fp_enabled()` and either reads or mutates `struct dc`, `struct dc_state`, `struct clk_mgr`, DML pipe arrays, or global DCN30 bounding-box structures.

## Important APIs, Types, and Functions

Two global model structures anchor the file. `dcn3_0_ip` is a `_vcs_dpi_ip_params_st` describing DCN 3.0 display IP limits and capacities: DET/ROB sizes, DPP/OTG/DSC counts, chunk sizes, buffer sizes, scaler limits, DCC support, cursor capacity, ODM capability, and clock delay constants. `dcn3_0_soc` is a `_vcs_dpi_soc_bounding_box_st` describing initial clock limits, latency assumptions, bandwidth percentages, return bus widths, DRAM behavior, urgent latency adjustment, and related SOC parameters.

The exported functions are:

- `dcn30_fpu_populate_dml_writeback_from_context()` walks active pipe contexts, finds enabled writeback targets attached to the pipe plane, computes writeback source/destination dimensions, taps, ratios, format, and worst-case writeback DISPCLK, then stores the selected writeback model in the matching DML pipe.
- `dcn30_fpu_set_mcif_arb_params()` fills MCIF writeback urgent and pstate watermarks for all client slots and computes the DRAM speed change duration in refclk cycles.
- `dcn30_fpu_update_soc_for_wm_a()` updates the context DML SOC latencies from clock-manager WM_A table entries, with special handling for firmware-based mclk switching and zero pstate latency.
- `dcn30_fpu_calculate_wm_and_dlg()` is the main watermark/DLG orchestration routine for DCN30 validation. It handles pstate support, firmware-based vblank stretch fallback, DCFCLK selection, watermark sets B/C/A/D, dummy pstate latency selection, display and DPP clock assignment, FPO workarounds, DLG calculation through `dcn20_calculate_dlg_params()`, and final mclk-switch setup.
- `dcn30_fpu_update_dram_channel_width_bytes()` patches the global SOC bounding box from BIOS VRAM info.
- `dcn30_fpu_update_max_clk()` fills missing max clock values from the current global SOC clock limit.
- `dcn30_fpu_get_optimal_dcfclk_fclk_for_uclk()` derives optimal DCFCLK and FCLK from UCLK, channel count, channel width, DRAM bandwidth limits, fabric return width, and DCF return bus width.
- `dcn30_fpu_update_bw_bounding_box()` updates global clock-limit states from validated DCFCLK and DRAM-speed arrays, refreshes VCO speed from the dentist clock, and reinitializes DML instances.
- `dcn30_find_dummy_latency_index_for_fw_based_mclk_switch()` searches dummy pstate latency table entries until DML allows self-refresh plus mclk switch in vblank.
- `dcn3_fpu_build_wm_range_table()` initializes watermark sets A, C, and D plus dummy pstate table defaults for the clock manager.
- `patch_dcn30_soc_bounding_box()` reads BIOS SOC bounding-box latency information and patches the global SOC latency fields.

## Control Flow

Writeback population is a per-active-stream scan. For each pipe context with a stream, it clears writeback enable/count in the current DML pipe, scans `stream->writeback_info`, filters for enabled writebacks whose source plane matches the pipe plane, builds a `writeback_st`, calculates required writeback DISPCLK with `dml30_CalculateWriteBackDISPCLK()`, and keeps only the worst-case writeback because DML models one writeback parameter set per pipe.

The main `dcn30_fpu_calculate_wm_and_dlg()` flow starts from DML VBA outputs: selected voltage level, `maxMpcComb`, DCFCLK state, and DRAM clock-change support. It clears firmware pstate optimization flags on all streams. If natural pstate switching is unsupported, it tests whether firmware-based vblank stretch can support mclk switching, finds a dummy latency index if so, restores original latency state, and revalidates bandwidth. It then selects at least `soc.min_dcfclk`, programs pipe clock config fields, computes watermark set B when valid, computes set C with dummy pstate latency, maps set A to C when pstate is unsupported, or recalculates set A from normal WM_A latencies when pstate is supported. Set D is currently copied from set A after a disabled code block.

After watermarks, it writes per-pipe calculated DISPCLK and DPPCLK, applies forced-clock and debug minimum overrides, applies a firmware pstate optimization workaround for a narrow DRAM speed/channel case, and calls `dcn20_calculate_dlg_params()` to populate DLG parameters using shared DCN20 logic. It then restores full pstate latency when needed and configures firmware-based vblank stretch if that path was selected.

Bounding-box update flow mutates globals before reinitializing DML. `dcn30_fpu_update_bw_bounding_box()` fills each SOC clock state with per-state DCFCLK/FCLK/DRAM speed and max display clocks, then calls `dml_init_instance()` for `dc->dml` and, when present, `dc->current_state->bw_ctx.dml`.

## State and Persistence Behavior

This file mutates both per-validation state and global model state. Per-validation mutations include `pipes[*].dout.wb`, `pipes[*].clks_cfg`, `context->bw_ctx.dml.soc` latencies, `context->bw_ctx.bw.dcn.watermarks`, `context->bw_ctx.bw.dcn.clk.fw_based_mclk_switching`, stream `fpo_in_use`, `context->perf_params.stutter_period_us`, and MCIF arbitration parameters.

Global mutable state includes `dcn3_0_soc` and `dcn3_0_ip` as DML initialization inputs. BIOS and clock-table patch functions update `dcn3_0_soc`, so subsequent DML initializations inherit those values. There is no file I/O, durable storage, or allocation in this file, but the global bounding-box mutations persist for the life of the driver instance.

## Dependencies and Integration Points

The file includes resource, clock manager, register helper, DCN calculation math, DCN20/DCN30 resource headers, the DCN30 SMU interface, DML VBA 3.0 declarations, and its own header. It is called from `resource/dcn30/dcn30_resource.c` for writeback population, MCIF arbitration, watermark/DLG calculation, DRAM channel width updates, max clock updates, optimal clock derivation, and bandwidth bounding-box refresh. `clk_mgr/dcn30/dcn30_clk_mgr.c` calls `dcn3_fpu_build_wm_range_table()`. Resource construction calls `patch_dcn30_soc_bounding_box()`.

The function set depends on several external DCN30/DCN20 helpers: `dcn30_can_support_mclk_switch_using_fw_based_vblank_stretch()`, `dcn30_internal_validate_bw()`, `dcn30_setup_mclk_switch_using_fw_based_vblank_stretch()`, `dcn20_calculate_dlg_params()`, DML watermark getters, DML clock getters, and DML instance initialization.

## Risks and Edge Cases

Global mutable bounding boxes are a major coupling point. BIOS-derived latency patches, DRAM channel width updates, and bandwidth-table updates change `dcn3_0_soc` globally and then reinitialize DML; incorrect ordering can leave current or future contexts using stale values. The code assumes FPU access is enabled; calling these functions without the FPU guard violates kernel FPU rules.

Watermark calculation is sensitive to pstate support. The fallback path temporarily changes `dram_clock_change_latency_us`, runs validation, restores latency, and may use dummy pstate latencies. A missed restore or stale `pipe_cnt`/`vlevel` after validation would affect watermarks and DLG. The dummy-latency search asserts if no valid index is found and then falls back to index 3, accepting possible underflows over crashes.

Writeback support compresses multiple writebacks attached to one plane into the worst writeback DISPCLK model, which is a deliberate workaround for DML's one-writeback-per-pipe assumption. This can be conservative but may hide per-writeback distinctions. The FPO workaround mutates `DRAMSpeed` for a narrow NV24 bandwidth issue, so tests should check that later calculations see the intended adjusted speed.

`dcn30_fpu_get_optimal_dcfclk_fclk_for_uclk()` performs floating-point bandwidth division and writes integer outputs without explicit rounding policy beyond assignment truncation. `dcn30_fpu_update_bw_bounding_box()` ignores its `bw_params` parameter and assumes input arrays are sized for `dcn3_0_soc.num_states`.

## Test Signals

Good test coverage includes DCN30 bandwidth validation modes with natural pstate support, unsupported pstate with and without firmware-based vblank stretch, dummy pstate table selection, forced clocks, debug minimum clocks, writeback enabled/disabled and multiple writeback targets, BIOS latency overrides, DRAM channel width override, and clock-table-driven bounding-box updates. Golden comparisons should verify watermark sets A/B/C/D, `fw_based_mclk_switching`, `stutter_period_us`, DLG register outputs after `dcn20_calculate_dlg_params()`, and MCIF arbitration watermarks.

Runtime signals include absence of FPU assertion violations, no display underflows during pstate/mclk transitions, correct PMFW watermark range table programming, stable DML validation after reinitialization, and no regression in DCN30 resource validation call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/dcn30_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/dcn30_fpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/dcn30_fpu.h

## Purpose

This header declares the DCN 3.0 floating-point DML/resource integration functions implemented in `dcn30_fpu.c`. It is the public interface used by DCN30 resource and clock-manager code for writeback modeling, watermark/DLG calculation, bounding-box updates, dummy pstate support, and BIOS/PMFW watermark setup.

The header includes `core_types.h` and `dcn20/dcn20_optc.h`, which provide core display, DML, resource, clock, and MCIF/OPT controller type declarations used by the prototypes.

## Important APIs, Types, and Functions

The declarations cover the complete exported surface of the C file:

- `dcn30_fpu_populate_dml_writeback_from_context()` maps `struct resource_context` pipe/writeback state into `display_e2e_pipe_params_st` writeback fields.
- `dcn30_fpu_set_mcif_arb_params()` fills `struct mcif_arb_params` watermarks from a DML instance and pipe array.
- `dcn30_fpu_update_soc_for_wm_a()` applies WM_A latency inputs to a validation context.
- `dcn30_fpu_calculate_wm_and_dlg()` calculates DCN watermarks and DLG data for a context, pipe array, pipe count, and voltage level.
- `dcn30_fpu_update_dram_channel_width_bytes()` patches DML SOC channel width from BIOS VRAM information.
- `dcn30_fpu_update_max_clk()` fills missing max clock fields in `struct dc_bounding_box_max_clk`.
- `dcn30_fpu_get_optimal_dcfclk_fclk_for_uclk()` derives DCFCLK/FCLK recommendations for a UCLK rate.
- `dcn30_fpu_update_bw_bounding_box()` updates DML bounding boxes and reinitializes DML from clock arrays.
- `dcn30_find_dummy_latency_index_for_fw_based_mclk_switch()` searches for a usable dummy pstate latency index.
- `dcn3_fpu_build_wm_range_table()` initializes clock manager watermark ranges and dummy pstate table entries.
- `patch_dcn30_soc_bounding_box()` patches SOC latency fields from BIOS-provided bounding-box data.

## Control Flow

The header has no executable control flow. It enables call sites in `resource/dcn30/dcn30_resource.c` and `clk_mgr/dcn30/dcn30_clk_mgr.c` to call into the FPU-protected implementation. The prototypes make the calling convention explicit: most functions mutate caller-provided context structures and must be invoked under whatever FPU enable/disable discipline the caller uses around DCN FPU code.

## State and Persistence Behavior

There is no direct state in the header. The declared functions imply significant state mutation in their implementation: DML pipe arrays, bandwidth context watermarks, global DCN30 SOC/IP bounding boxes, clock manager watermark tables, and BIOS-derived latency/channel-width fields. Callers should treat these routines as mutating operations rather than pure calculations unless the specific function only writes output pointers.

## Dependencies and Integration Points

This header is an integration contract between DCN30 resource management, clock management, and DML. The resource layer uses it during validation, bandwidth bounding-box setup, writeback modeling, and watermark/DLG calculation. The clock manager uses it when building PMFW watermark ranges. The implementation also depends on DCN20 shared DLG calculation code, but that dependency is intentionally hidden behind the DCN30 API.

## Risks and Edge Cases

The main interface risk is that the header does not encode FPU preconditions; callers must know these functions require FPU-enabled execution because the implementation asserts it. Several prototypes accept raw pointers and array counts without size annotations, so incorrect `pipe_cnt`, `vlevel`, or clock-array sizing can corrupt calculations in the implementation. The `patch_dcn30_soc_bounding_box()` parameter name suggests an IP pointer even though the type is SOC bounding-box; the implementation ignores it, so callers should not expect that argument to be patched.

## Test Signals

Compile tests should cover all DCN30 resource and clock-manager users of this header. Functional validation should exercise each declared function through its real call site, with debug FPU assertions enabled, and verify that DML instances, watermarks, clock recommendations, writeback parameters, and bounding-box patches match expected DCN30 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/dcn30_fpu.h -->
