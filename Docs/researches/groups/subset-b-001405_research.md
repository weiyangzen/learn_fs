# Research: subset-b-001405

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20.h

## Purpose

`display_rq_dlg_calc_20.h` is the public DCN 2.0 Display Mode Library header for requestor queue (RQ), display logic generator (DLG), and time-to-use (TTU) register calculation. It exposes the two generation-specific entry points that convert DML pipe timing, scaling, tiling, memory, and watermark data into hardware register structs consumed by AMD Display Core programming paths.

The header itself contains no calculations. Its role is ABI and integration: include the shared RQ/DLG type declarations from `display_rq_dlg_helpers.h`, forward-declare `struct display_mode_lib`, and publish the DCN 2.0 function names that `display_mode_lib.c` installs into the `dml20_funcs` dispatch table.

## Important APIs, Types, And Functions

- `dml20_rq_dlg_get_rq_reg(mode_lib, rq_regs, pipe_param)`: fills `display_rq_regs_st` for one pipe from `display_pipe_params_st`. The implementation computes source-format, tiling, swath, metadata, and PTE sizing before extracting hardware register fields.
- `dml20_rq_dlg_get_dlg_reg(mode_lib, dlg_regs, ttu_regs, e2e_pipe_param, num_pipes, pipe_idx, cstate_en, pstate_en, vm_en, ignore_viewport_pos, immediate_flip_support)`: fills DLG and TTU register structs for one pipe within a compacted active-pipe array.
- `struct display_mode_lib`: forward-declared owner of SoC/IP parameters, DML function tables, logging, and VBA-calculated model state.
- `display_rq_regs_st`, `display_dlg_regs_st`, `display_ttu_regs_st`, `display_pipe_params_st`, and `display_e2e_pipe_params_st`: shared DML structs pulled in indirectly through `display_rq_dlg_helpers.h` and `display_mode_lib.h`.

## Control Flow

Callers do not include implementation details from this header; they select the functions through `struct dml_funcs` or call the named symbols directly. `display_mode_lib.c` includes this header and assigns `dml20_rq_dlg_get_dlg_reg` and `dml20_rq_dlg_get_rq_reg` into the DCN 2.0 function table. DCN resource code later calls those function pointers while populating per-pipe `rq_regs`, `dlg_regs`, and `ttu_regs`.

The header's comments document the intended implementation flow: RQ register generation calls an internal `get_rq_param` style calculation and then extracts RQ register fields; DLG register generation uses compacted end-to-end pipe parameters plus clock, c-state, p-state, virtual-memory, viewport, and immediate-flip policy flags.

## State And Persistence Behavior

This header declares pure calculation entry points from the caller perspective. It owns no storage, global variables, or persistent state. The implementation writes caller-owned output structs and reads `mode_lib`, pipe parameters, and DML model state. Hardware persistence happens later when the display core programs the generated register values; this header is only the calculation contract.

## Dependencies And Integration Points

The only direct include is `../display_rq_dlg_helpers.h`, which supplies shared DML typedefs and debug printer prototypes. The header integrates with:

- `display_mode_lib.c`, where DCN 2.0 DML function pointers are registered.
- `display_mode_lib.h`, which defines the common `struct dml_funcs` slots matching these prototypes.
- DCN 2.0 FPU/resource code that calls the registered functions to fill pipe register programming data.
- The sibling implementation file `display_rq_dlg_calc_20.c`, which contains the actual calculations.

## Risks And Edge Cases

- Prototype drift between this header, `display_mode_lib.h`, and `display_rq_dlg_calc_20.c` would break DCN 2.0 function-table registration or produce compile errors.
- The function signatures expose several boolean policy flags. Misordered arguments at direct call sites are hard to detect because they share the same type.
- The header uses shared DML typedefs rather than local structs, so any incompatible change in `display_mode_structs.h` can affect this API.
- DCN 2.0 and DCN 2.0v2 headers are intentionally very similar. Mixing `dml20_*` and `dml20v2_*` symbols would silently select a different algorithm variant if function-table wiring is changed incorrectly.

## Test Signals

- Kernel build coverage verifies prototypes, includes, and function-table assignment compatibility.
- Static symbol checks can confirm that `dml20_funcs` points at the DCN 2.0 symbols and not the v2 symbols.
- Runtime validation should compare generated RQ/DLG/TTU register values against known-good DCN 2.0 DML vectors for RGB, YUV420, tiled, linear, c-state, p-state, VM, and immediate-flip scenarios.
- Regression tests should include direct compile coverage for consumers including only this header and calling both public entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20v2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20v2.c

## Purpose

`display_rq_dlg_calc_20v2.c` implements the DCN 2.0v2 RQ, DLG, and TTU register calculations for AMD's Display Mode Library. Given DML pipe descriptions, SoC/IP limits, display clocks, scaler ratios, tiling mode, cursor data, watermarks, and prefetch values, it produces the requestor queue registers, display logic generator deadline registers, and TTU QoS registers needed by the display hardware programming path.

The file is explicitly treated as hardware-engineer supplied "HW gospel"; local comments warn that it is GCC-parseable but not expected to follow normal kernel style. The implementation is therefore formula-heavy, register-format aware, and packed with DML debug prints and assertions rather than defensive API wrappers.

The v2 variant is almost identical to the DCN 2.0 implementation but uses `dml20v2_*` symbols and includes one important DLG behavioral change: `min_dst_y_next_start` is computed from `dlg_vblank_start + min_dst_y_ttu_vblank`, while the non-v2 DCN 2.0 implementation uses only `dlg_vblank_start`.

## Important APIs, Types, And Functions

- `dml20v2_rq_dlg_get_rq_reg(mode_lib, rq_regs, pipe_param)`: public RQ entry point. It zeroes `rq_regs`, computes internal `display_rq_params_st`, extracts hardware register fields, and prints the result.
- `dml20v2_rq_dlg_get_dlg_reg(mode_lib, dlg_regs, ttu_regs, e2e_pipe_param, num_pipes, pipe_idx, cstate_en, pstate_en, vm_en, ignore_viewport_pos, immediate_flip_support)`: public DLG/TTU entry point. It derives system watermark parameters, recomputes per-pipe RQ/DLG params, and fills `display_dlg_regs_st` plus `display_ttu_regs_st`.
- `dml20v2_rq_dlg_get_rq_params(...)`: static internal RQ calculation driver for luma and optional chroma planes.
- `dml20v2_rq_dlg_get_dlg_params(...)`: static internal deadline and TTU calculation driver for a selected pipe.
- `get_bytes_per_element(source_format, is_chroma)`: maps DML source formats to bytes per luma or chroma element.
- `is_dual_plane(source_format)`: identifies YUV420 formats that need chroma-plane calculations.
- `get_blk_size_bytes(tile_size)`: maps macro tile size enum values to 256 KiB, 64 KiB, or 4 KiB block sizes.
- `get_refcyc_per_delivery(...)`: computes reference-clock cycles per line or per request delivery, with special handling for ODM combine and vertical ratio.
- `get_meta_and_pte_attr(...)`: central metadata and PTE geometry calculator. It derives swath dimensions, meta request rows, meta chunk counts, meta PTE bytes, virtual-memory page geometry, dPTE request shape, dPTE row height, dPTE group size, and upper-bound row/group counts.
- `get_surf_rq_param(...)`: initializes chunk, meta chunk, and MPTE group sizes for one surface plane, then delegates geometry work to `get_meta_and_pte_attr`.
- `handle_det_buf_split(...)`: decides luma/chroma detile-buffer storage, 128-byte vs 256-byte request mode, and final swath heights based on format, scan direction, and buffer size.
- `extract_rq_sizing_regs(...)` and `extract_rq_regs(...)`: convert calculated byte sizes and swath geometry into encoded register fields such as chunk size, meta chunk size, group sizes, swath height, expansion modes, and plane1 base address.
- `calculate_ttu_cursor(...)`: computes cursor request delivery timing for 2-bit and 32-bit cursor formats.

## Control Flow

RQ register flow starts in `dml20v2_rq_dlg_get_rq_reg`. The function clears the caller's output struct, calls `dml20v2_rq_dlg_get_rq_params`, then encodes the computed parameters through `extract_rq_regs`.

`dml20v2_rq_dlg_get_rq_params` classifies the source format as YUV420 and YUV420 10 bpc, calculates luma surface parameters with `get_surf_rq_param`, optionally calculates chroma surface parameters for dual-plane formats, and finally calls `handle_det_buf_split`. `get_surf_rq_param` applies fixed DCN 2.0v2 request sizing constants: 8192-byte chunks, 1024-byte minimum data chunks, 2048-byte meta chunks, 256-byte minimum meta chunks, and 2048-byte MPTE groups. The detailed geometry work in `get_meta_and_pte_attr` branches on linear vs tiled, horizontal vs vertical scan, tile block size, virtual page size, YUV420, and dPTE request shape.

DLG/TTU flow starts in `dml20v2_rq_dlg_get_dlg_reg`. It currently casts `vm_en`, `ignore_viewport_pos`, and `immediate_flip_support` to void, so those public flags do not affect this implementation. The function fills `display_dlg_sys_params_st` from DML VBA helper getters such as `get_wm_urgent`, `get_clk_dcf_deepsleep`, `get_urgent_extra_latency`, `get_wm_memory_trip`, `get_wm_dram_clock_change`, `get_wm_stutter_enter_exit`, `get_total_immediate_flip_bw`, and `get_total_immediate_flip_bytes`. It then recomputes RQ params for the target pipe and calls `dml20v2_rq_dlg_get_dlg_params`.

`dml20v2_rq_dlg_get_dlg_params` first clears both output structs, loads source, destination, output, clock, scaler, and tap substructures for `pipe_idx`, and derives timing quantities such as `ref_freq_to_pix_freq`, `refcyc_per_htotal`, vblank end, hblank end, and `min_dst_y_next_start`. It includes c-state and p-state latency only when `cstate_en` or `pstate_en` are true, folding urgent, self-refresh, and DRAM-clock-change latencies into `line_wait`.

The prefetch section obtains DML VBA results for destination prefetch and VM/PTE row work in vblank and flip. It asserts that VM and row work fit within hardcoded minima, computes line-store wait, prefetch vertical ratios, luma/chroma swath widths, dPTE row heights, meta row heights, scaler input widths, and horizontal scaler delivery rates. It then calculates delivery timing for luma, optional chroma, and up to two cursors. The last portion encodes these floating-point results into fixed-point DLG and TTU register fields, clamps some nominal reference-cycle fields to register maximums, applies fixed QoS levels, and prints final register structs.

## State And Persistence Behavior

The file has no file-scope mutable state and no on-disk persistence. Its state behavior is calculation-only:

- It writes caller-owned `display_rq_regs_st`, `display_dlg_regs_st`, and `display_ttu_regs_st` outputs.
- It uses stack-local intermediate structs such as `display_rq_params_st` and `display_dlg_sys_params_st`.
- It reads `mode_lib->ip` and `mode_lib->soc` fields for detile-buffer size, dPTE buffer size, VMM page size, timing delays, minimum vblank, and latency constants.
- It reads DML VBA-derived helper values from the current `display_mode_lib` and pipe array.
- It emits debug output through `dml_print` and validation failures through `ASSERT`.

The durable effect of this file is indirect: later display code programs the generated register values into hardware. Because the public functions zero their output structs before filling them, omitted optional fields default to zero.

## Dependencies And Integration Points

Direct includes are `display_mode_lib.h`, `display_mode_vba.h`, `display_rq_dlg_calc_20v2.h`, and `dml_inline_defs.h`. The implementation depends on:

- DML math helpers: `dml_min`, `dml_max`, `dml_log2`, `dml_pow`, `dml_floor`, `dml_ceil`, and `dml_round_to_multiple`.
- DML debug and assertion helpers: `dml_print`, `ASSERT`, and `print__*` functions from `display_rq_dlg_helpers.h`.
- Shared DML structs from `display_mode_structs.h`, including pipe source/destination/output/clock/scaler structs and RQ/DLG/TTU register structs.
- VBA helper getters from `display_mode_vba.h` for watermarks, prefetch, dPTE/VM timing, DSC delay, scaler positions, and bandwidth.
- Tiling geometry helper `Calculate256BBlockSizes`.

`display_mode_lib.c` registers this file's public functions in `dml20v2_funcs`. DCN 2.0 display resource code calls through `context->bw_ctx.dml.funcs.rq_dlg_get_dlg_reg` and `rq_dlg_get_rq_reg` when the selected DML generation is DCN 2.0v2. The outputs populate per-pipe register caches that downstream DCN hardware sequencing code uses for HUBP/DLG/TTU programming.

## Risks And Edge Cases

- The public `vm_en`, `ignore_viewport_pos`, and `immediate_flip_support` parameters are ignored. Callers expecting those flags to alter DCN 2.0v2 results will get identical calculations.
- Many formulas divide by inputs such as pixel clock, DPP clock, DISP clock, htotal, request counts, meta chunk counts, dPTE group counts, data pitch, scaler ratios, and vertical ratios. The code assumes upstream DML validation has rejected zero or invalid values.
- Register range safety is mostly enforced with `ASSERT`, which may be compiled out or may not recover gracefully in production paths.
- Some fields saturate silently, such as nominal PTE/meta reference-cycle values clamped to `2^23 - 1`, while other out-of-range fields only assert or warn.
- `handle_det_buf_split` comments assume the incoming configuration fits the detile buffer. Oversized swaths can still produce questionable split or swath-height results if earlier validation is wrong.
- Linear surface dPTE row height asserts `log2_dpte_row_height_linear >= 3`; unusual pitch/page/buffer combinations can trip this.
- `get_meta_and_pte_attr` computes `meta_chunk_threshold = 2 * min_meta_chunk_width - meta_req_width` or height using unsigned arithmetic. Invalid sizing relationships could underflow.
- YUV420 and DCC support is partly approximated: comments state DCC for 4:2:0 is not supported in DCN 1.0 and assign chroma meta timing from luma in some fields.
- Cursor width is asserted to be at most 256. Wider cursor inputs rely on prior validation.
- The v2 change to `min_dst_y_next_start` is timing-sensitive. Regressions would likely appear as underflow, vblank deadline, or TTU issues rather than compile failures.

## Test Signals

- Build tests should cover this file with DCN 2.0v2 enabled and verify that `display_mode_lib.c` registers `dml20v2_rq_dlg_get_dlg_reg` and `dml20v2_rq_dlg_get_rq_reg`.
- Golden-vector DML tests should compare RQ, DLG, and TTU register outputs for linear and tiled RGB, YUV420 8 bpc, YUV420 10 bpc, horizontal and vertical scan, 4 KiB/64 KiB/256 KiB tile sizes, 4 KiB and larger VMM pages, interlaced timing, ODM combine, MPC split, DSC enabled, c-state enabled, and p-state enabled.
- Variant tests should compare DCN 2.0 and DCN 2.0v2 outputs and specifically verify the `min_dst_y_next_start` difference.
- Boundary tests should exercise detile-buffer split decisions, 128-byte request mode, large pitches, high vertical ratios, maximum cursor width, one and two cursor paths, and register field maximums.
- Runtime signals include `DML_DLG` debug prints, `WARNING: DML_DLG` messages about `vstartup_start` vs minimum vblank, and assertions around reference-cycle field widths, prefetch fit, cursor width, and dPTE row height.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20v2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20v2.h

## Purpose

`display_rq_dlg_calc_20v2.h` is the public DCN 2.0v2 Display Mode Library header for RQ, DLG, and TTU register calculation. It exposes the v2 namespaced calculation entry points implemented in `display_rq_dlg_calc_20v2.c` so the shared DML dispatch table can select the DCN 2.0v2 algorithm independently from the original DCN 2.0 implementation.

Like the non-v2 header, this file is a declaration contract only. It does not implement formulas, own state, or program hardware.

## Important APIs, Types, And Functions

- `dml20v2_rq_dlg_get_rq_reg(mode_lib, rq_regs, pipe_param)`: calculates requestor queue register fields for a single pipe and writes `display_rq_regs_st`.
- `dml20v2_rq_dlg_get_dlg_reg(mode_lib, dlg_regs, ttu_regs, e2e_pipe_param, num_pipes, pipe_idx, cstate_en, pstate_en, vm_en, ignore_viewport_pos, immediate_flip_support)`: calculates DLG and TTU register fields for one pipe in an end-to-end active-pipe set.
- `struct display_mode_lib`: forward declaration for the DML context carrying SoC, IP, function-table, logging, and VBA state.
- Shared output/input structs come from `display_rq_dlg_helpers.h` and `display_mode_lib.h`: `display_rq_regs_st`, `display_dlg_regs_st`, `display_ttu_regs_st`, `display_pipe_params_st`, and `display_e2e_pipe_params_st`.

## Control Flow

`display_mode_lib.c` includes this header and wires the public functions into `dml20v2_funcs`. Display resource code that has selected the DCN 2.0v2 DML implementation calls those function pointers while building per-pipe hardware programming state.

The documented flow mirrors the implementation: RQ generation derives register-definition-agnostic request parameters and then extracts encoded register fields; DLG generation consumes compacted end-to-end pipe parameters and system policy flags to produce DLG and TTU register structs.

## State And Persistence Behavior

The header has no mutable state and creates no persistence. Its functions are declared as output-struct writers: they read DML context and pipe arrays, then populate caller-owned register structs. Any hardware-visible persistence is outside this header and occurs only when later code programs the generated values into registers.

## Dependencies And Integration Points

The direct dependency is `../display_rq_dlg_helpers.h`, which brings in shared DML type definitions and print helper declarations. Integration points include:

- `display_rq_dlg_calc_20v2.c`, the implementation for these symbols.
- `display_mode_lib.c`, where `dml20v2_funcs` registers these functions.
- `display_mode_lib.h`, whose `struct dml_funcs` prototypes must stay compatible.
- DCN 2.0 resource/FPU code that consumes `struct dml_funcs` to populate DLG, TTU, and RQ register caches.

## Risks And Edge Cases

- Because this header is nearly identical to `display_rq_dlg_calc_20.h`, accidental symbol substitution between `dml20_*` and `dml20v2_*` is a realistic maintenance risk.
- The boolean policy arguments are positional and same-typed, so direct callers can accidentally swap c-state, p-state, VM, viewport, and immediate-flip controls without compiler help.
- Any mismatch between this header and the implementation breaks the DCN 2.0v2 function-table assignment.
- The header exposes a broader signature than the current v2 implementation uses; in `display_rq_dlg_calc_20v2.c`, `vm_en`, `ignore_viewport_pos`, and `immediate_flip_support` are currently ignored.

## Test Signals

- Compile tests should verify this header can be included wherever `struct dml_funcs` is initialized and that the v2 symbols resolve.
- Function-table tests or static checks should confirm `dml20v2_funcs` uses the v2 functions and not the DCN 2.0 functions.
- ABI-style regression tests should flag changes to these prototypes because downstream function-pointer users depend on exact signatures.
- DML output tests should include at least one case that distinguishes DCN 2.0v2 from DCN 2.0, especially the DLG `min_dst_y_next_start` behavior implemented behind this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20v2.h -->
