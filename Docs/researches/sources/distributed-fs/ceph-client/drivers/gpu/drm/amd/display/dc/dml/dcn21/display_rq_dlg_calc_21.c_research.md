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
