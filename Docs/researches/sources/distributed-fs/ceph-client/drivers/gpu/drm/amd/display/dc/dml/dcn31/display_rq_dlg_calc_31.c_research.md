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
