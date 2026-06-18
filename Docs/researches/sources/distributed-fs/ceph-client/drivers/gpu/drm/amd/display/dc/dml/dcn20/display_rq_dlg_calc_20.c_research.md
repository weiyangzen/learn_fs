# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20.c

## Purpose

`display_rq_dlg_calc_20.c` converts DCN 2.0 display-mode results and per-pipe source/destination parameters into request-queue, deadline, and TTU register structures. It bridges the high-level DML timing/bandwidth model and the register fields used by HUBP/DLG/TTU programming.

The file computes requestor geometry that is mostly register-definition agnostic, then extracts encoded register values. It separately computes DLG/TTU timing fields from pipe timing, scaling, prefetch, watermarks, RQ metadata/PTE row information, cursor state, cstate and pstate policy.

## Important APIs, Types, And Functions

- `dml20_rq_dlg_get_rq_reg(mode_lib, rq_regs, pipe_param)`: public RQ entry. It zeros output registers, calculates `display_rq_params_st`, encodes RQ sizing/swath/DET fields, and prints the result.
- `dml20_rq_dlg_get_dlg_reg(mode_lib, dlg_regs, ttu_regs, e2e_pipe_param, num_pipes, pipe_idx, cstate_en, pstate_en, vm_en, ignore_viewport_pos, immediate_flip_support)`: public DLG/TTU entry. It gathers system watermark values through DML accessors, computes local RQ params, and fills `display_dlg_regs_st` and `display_ttu_regs_st`.
- `dml20_rq_dlg_get_rq_params`: derives luma/chroma RQ parameters for a pipe source.
- `dml20_rq_dlg_get_dlg_params`: main deadline/TTU calculation and register assignment function.
- `get_bytes_per_element`, `is_dual_plane`, `get_refcyc_per_delivery`, and `get_blk_size_bytes`: local format, request timing, and tile-size helpers.
- `extract_rq_sizing_regs` and `extract_rq_regs`: convert byte-sized request groups/chunks and swath geometry into register encodings.
- `handle_det_buf_split`: decides luma/chroma DET buffer allocation and request size behavior.
- `get_meta_and_pte_attr` and `get_surf_rq_param`: compute swath width, full swath bytes, meta request rows/chunks, meta PTE frame bytes, DPTE request rows/groups, and related sizing values.
- `calculate_ttu_cursor`: computes per-request TTU delivery timing for up to two cursors.

## Control Flow

The RQ path starts in `dml20_rq_dlg_get_rq_reg`. It clears `display_rq_regs_st`, calls `dml20_rq_dlg_get_rq_params` on `pipe_param->src`, then calls `extract_rq_regs`. The parameter pass identifies YUV420/10bpc formats, computes luma surface parameters, optionally computes chroma parameters for dual-plane formats, and calls `handle_det_buf_split`. Surface parameter calculation sets fixed chunk defaults, delegates most geometry to `get_meta_and_pte_attr`, and stores the results in luma/chroma `sizing`, `dlg`, and `misc` structs. Register extraction encodes chunk, min chunk, meta chunk, dpte group, mpte group, PTE row height, swath height, expansion modes, and `plane1_base_address` for the chroma DET split.

`get_meta_and_pte_attr` is the core RQ geometry routine. It determines bytes per element and 256-byte block dimensions, handles linear vs tiled and horizontal vs vertical scan, calculates swath width upper bounds and request counts, computes full swath bytes, derives meta row dimensions and chunk counts, estimates meta surface and meta PTE bytes per frame, determines virtual memory page shape, chooses DPTE request shape, derives DPTE row height/width/request count, sets DPTE bytes per row, chooses reduced DPTE grouping for a vertical tiled special case, and stores groups per row.

The DLG/TTU path starts in `dml20_rq_dlg_get_dlg_reg`. It gathers `display_dlg_sys_params_st` from accessor functions such as urgent watermark, deep sleep DCFCLK, extra latency, memory-trip watermark, dram-clock-change watermark, stutter watermark, and immediate-flip totals. It then recalculates RQ params for the selected pipe and calls `dml20_rq_dlg_get_dlg_params`.

`dml20_rq_dlg_get_dlg_params` reads the selected pipe's source, destination, output, clocks, scale ratio, and taps. It computes reference-to-pixel frequency ratios, htotal/vblank fields, min TTU vblank, vupdate/vready behavior, pipeline delay after scaler/DSC, line wait based on urgent/cstate/pstate, prefetch line allocation from DML accessors, luma/chroma active delivery timing, TTU request delivery for luma/chroma and cursors, and then writes fixed-point register fields. It asserts many register-width assumptions and clamps some nominal delivery fields to maximum register values.

## State And Persistence Behavior

This file does not persist state and does not directly program hardware. It mutates only caller-provided output structures:

- `display_rq_regs_st`: RQ chunk sizes, min chunk sizes, meta chunk sizes, DPTE/MPTE group sizes, PTE row height, swath height, expansion modes, and chroma plane base address.
- `display_dlg_regs_st`: reference frequency ratios, htotal/vblank timing, after-scaler offsets, prefetch line counts, VM/row request timing, vratio prefetch fields, PTE/meta group delivery fields, nominal row timing, line delivery timing, cursor DLG defaults, and QoS-related DLG fields.
- `display_ttu_regs_st`: per-request delivery timing for luma/chroma/cursors, QoS watermarks/levels, ramp-disable flags, and min TTU vblank.

Scratch state is local (`display_rq_params_st rq_param`, `display_dlg_sys_params_st dlg_sys_param`). The computations depend on stable `mode_lib` accessor outputs and the caller's `display_e2e_pipe_params_st` array.

## Dependencies And Integration Points

The file includes `display_mode_lib.h`, `display_mode_vba.h`, `display_rq_dlg_calc_20.h`, and `dml_inline_defs.h`. It depends on DML math/debug helpers (`dml_log2`, `dml_floor`, `dml_ceil`, `dml_round_to_multiple`, `dml_min`, `dml_max`, `dml_pow`, `dml_print`, `ASSERT`) and common DML geometry functions such as `Calculate256BBlockSizes`.

It also depends on accessor functions and print helpers declared elsewhere in DML: `get_wm_urgent`, `get_clk_dcf_deepsleep`, `get_urgent_extra_latency`, `get_wm_memory_trip`, `get_wm_dram_clock_change`, `get_wm_stutter_enter_exit`, `get_total_immediate_flip_bw`, `get_total_immediate_flip_bytes`, `get_tcalc`, `get_min_ttu_vblank`, `get_dsc_delay`, `get_dst_x_after_scaler`, `get_dst_y_after_scaler`, `get_dst_y_prefetch`, `get_dst_y_per_vm_vblank`, `get_dst_y_per_row_vblank`, `get_dst_y_per_vm_flip`, `get_dst_y_per_row_flip`, `get_vratio_prefetch_l`, `get_vratio_prefetch_c`, and the `print__*` diagnostics.

Integration-wise, this is the DCN20 register-preparation side of DML. Higher-level AMD Display Core code builds `display_pipe_params_st` or `display_e2e_pipe_params_st`, calls these functions, and later uses the resulting register structures to program HUBP/DLG/TTU state through hardware abstraction layers.

## Risks And Edge Cases

- The code assumes many values are nonzero and power-of-two compatible: chunk bytes, meta chunk bytes, group bytes, swath heights, DPTE row heights, request counts, pitches, htotal, pixel/ref clocks, dppclk, dispclk, and cursor scaling ratios.
- Register-width assertions catch many overflow cases in debug builds (`refcyc_per_*`, `dst_y_*`, min TTU vblank), but release builds may continue with truncated values unless upstream validation prevents the mode.
- `extract_rq_regs` encodes `pte_row_height_linear` as `floor(log2(dpte_row_height)) - 3`; heights below 8 would underflow unsigned fields.
- `handle_det_buf_split` assumes the incoming configuration fits in DET. If it does not, it chooses 128-byte luma requests or DET splits but does not independently fail validation.
- `get_meta_and_pte_attr` computes meta surface bytes using viewport height even for vertical scan, matching the inherited formulas but making scan/pitch correctness sensitive to the hardware guide.
- The DLG path accepts `vm_en`, `ignore_viewport_pos`, and `immediate_flip_support` parameters but casts them unused. It relies on mode_lib/e2e accessor state rather than these booleans.
- There are several explicit TODOs and comments about inherited behavior: full recout width in hsplit, min_vblank mismatch, DCC for 4:2:0, chroma nominal meta timing, and magic thresholds for tiny `htotal`.
- Cursor support asserts `cur_src_width <= 256`; invalid cursor sizes can stop debug builds.
- Integer casts of fixed-point values can round down. Boundary cases near register limits need golden tests.

## Test Signals

- Build coverage catches structure/member drift with `display_rq_dlg_calc_20.h`, DML accessor declarations, and enum changes for source formats, tiling, macro tile size, scan direction, and cursor bpp.
- Unit or golden DML tests should compare RQ/DLG/TTU register outputs for linear RGB, tiled RGB, YUV420 8bpc, YUV420 10bpc, horizontal and vertical scan, DCC on/off, GPUVM page sizes, 4KB/64KB/256KB macro tiles, one and two cursors, ODM combine, hsplit/MPC combine, DSC enabled, interlaced timing, cstate and pstate enabled/disabled, and immediate flip metadata.
- Runtime diagnostics include `DML_DLG` prints of RQ sizing/regs, system params, delivery timing, prefetch lines, vratio prefetch, cursor timing, and warnings around `full_recout_width` or `vstartup_start >= min_vblank`.
- Assertions around reference cycles, prefetch relationships, register widths, cursor width, and line allocations are important failure signals during hardware bring-up or simulator validation.
