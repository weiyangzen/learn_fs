# subset-b-001419 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_vba.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_vba.c

### Purpose
`display_mode_vba.c` is the C bridge between driver-facing `display_e2e_pipe_params_st` inputs and AMD DML's large VBA-derived calculation state. It copies SoC, IP, and pipe parameters into `mode_lib->vba`, invokes DML recalculation and validation callbacks, and exposes calculated watermarks, clocks, bandwidths, prefetch values, MALL values, PTE metadata timings, and per-pipe attributes through getters.

### Important APIs, Types, And Functions
The main public entry is `dml_get_voltage_level()`, which refreshes cached inputs, runs recalculation or direct fetch helpers, validates, caches debug state, and returns `vba.VoltageLevel`. Macro-generated `get_*` functions expose scalar and pipe-scoped attributes. Other public helpers include `get_total_immediate_flip_bytes()`, `get_total_immediate_flip_bw()`, `get_total_prefetch_bw()`, `get_total_surface_size_in_mall_bytes()`, `get_det_buffer_size_kbytes()`, `get_is_phantom_pipe()`, `Calculate256BBlockSizes()`, `CalculateMinAndMaxPrefetchMode()`, `PixelClockAdjustmentForProgressiveToInterlaceUnit()`, `ModeSupportAndSystemConfiguration()`, and `CalculateWriteBackDISPCLK()`. Private helpers `fetch_socbb_params()`, `fetch_ip_params()`, `fetch_pipe_params()`, `recalculate_params()`, `get_pipe_idx()`, `CursorBppEnumToBits()`, and `cache_debug_params()` do the state transfer and cache management.

### Control Flow
Getter calls first call `recalculate_params()`, which compares current SoC/IP/pipes against the cached copies with `memcmp()`. When inputs changed, it copies the new values and calls `mode_lib->funcs.recalculate()`. `dml_get_voltage_level()` follows a slightly different path: if clocks are already specified it recalculates, otherwise it directly fetches SoC/IP/pipe data and adjusts interlace pixel clocks before validation. `fetch_pipe_params()` is the largest conversion step: it walks cached pipes, collapses hsplit pipes into planes, counts active planes and surfaces, maps timing and source fields into parallel VBA arrays, derives cursor counts, handles overlay blending-and-timing ownership, computes VM enablement and forced page table levels, validates PTE buffer mode constraints, and applies viewport caps.

### State, Persistence, And Dependencies
All persistent state is in `struct display_mode_lib`, especially `mode_lib->vba`, `vba.cache_pipes`, and `vba.cache_num_pipes`. There is no file or hardware persistence here; hardware-facing values are later consumed by other DC/DML code. Dependencies include `display_mode_lib.h`, `display_mode_vba.h`, `dml_inline_defs.h`, DML math wrappers, logger macros, `mode_lib->funcs.recalculate`, and `mode_lib->funcs.validate`.

### Integration Points
This file is used by the AMD display core when mode validation, watermark programming, clock selection, MALL policy, immediate flip, DSC, writeback, and RQ/DLG programming need calculated DML values. `ModeSupportAndSystemConfiguration()` feeds DML mode support from fixed clock selections. The generated getters are a stable API surface for other DML and DCN files that need one calculated field without owning the VBA internals.

### Risks
`memcmp()` over complex input structs assumes deterministic padding and initialized fields; stale padding can trigger redundant recalculation. Array indexing assumes `num_pipes <= DC__NUM_DPP__MAX` and valid pipe-plane mappings. Many fields are copied through parallel arrays, so off-by-one active plane/surface mistakes would corrupt unrelated planes. Several TODOs and assumptions remain around multistream, audio layout, DCC rate, viewport stationary, and hsplit full recout behavior. Assertions guard some invalid states but may be compiled differently across builds.

### Test Signals
Useful signals include mode validation tests across changed and unchanged pipe caches, hsplit and overlay configurations, interlaced outputs with and without OPP P2I support, GPUVM and HostVM enablement with forced levels, MALL phantom/static-screen modes, immediate flip bandwidth aggregation, writeback DISPCLK formulas, and boundary tests for 256-byte block sizes and prefetch mode selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_vba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_vba.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_vba.h

### Purpose
`display_mode_vba.h` declares the public DML VBA getter surface and defines `struct vba_vars_st`, the central in-memory state object used by the display mode library. It is the shared contract between DML calculation files and callers that need mode support, clock, bandwidth, watermark, VM, MALL, DSC, writeback, and request timing results.

### Important APIs, Types, And Functions
The header declares `ModeSupportAndSystemConfiguration()`, scalar `get_*` accessors through `dml_get_attr_decl`, pipe-scoped `get_*` accessors through `dml_get_pipe_attr_decl`, aggregate helpers, `dml_get_voltage_level()`, `get_is_phantom_pipe()`, `PixelClockAdjustmentForProgressiveToInterlaceUnit()`, `Calculate256BBlockSizes()`, `CalculateMinAndMaxPrefetchMode()`, and `CalculateWriteBackDISPCLK()`. The key type is `struct vba_vars_st`, which embeds `ip_params_st`, `soc_bounding_box_st`, cached pipe inputs, dummy scratch structs for generated DML code, and hundreds of input, intermediate, and output arrays keyed by voltage state, MPC combine mode, and DPP plane.

### Control Flow
The header has no executable control flow beyond function declarations, but its data layout defines the control flow of callers: fetch/copy inputs into `vba_vars_st`, calculate mode support per state, calculate performance and watermark outputs, then read values through getters. Field groups are organized as SoC bounding box parameters, IP parameters, pipe and plane parameters, calculated outputs, mode support reasons, mode support locals, and performance locals.

### State, Persistence, And Dependencies
`struct vba_vars_st` is persistent for the lifetime of `display_mode_lib`. It caches previous SoC/IP/pipe inputs to avoid unnecessary recalculation and stores debug snapshots such as `CachedActiveDRAMClockChangeLatencyMargin`. It depends on types from `display_mode_lib.h` and related DC/DML definitions, including DPP limits, voltage states, enum classes, pipe parameter structs, watermarks, and DML pipe/SOC helper structs.

### Integration Points
Every C file that reads or writes DML state depends on this layout. Register calculators read results such as PTE group bytes, VM group bytes, swath heights, delivery times, and MALL fields. DC mode validation uses status booleans and reason flags to decide whether a mode is supported. Debugging and tests use calculated clock and watermark getters declared here.

### Risks
The struct is very large and heavily index based, which makes field lifetime and plane/state indexing easy to misuse. Many fields mirror spreadsheet names, so similar names can differ subtly, for example luma/chroma, per-state/current-state, flip/vblank/nominal, and plane/surface. ABI risk is mostly internal to the driver, but build risk is high because many files assume exact field names. Any new field must be initialized on all calculation paths to avoid stale cache behavior.

### Test Signals
Compile coverage is important because this header binds many generated-style symbols. Runtime signals should check getter consistency after recalculation, per-pipe mapping for hsplit and overlay cases, voltage-state arrays across all states, MALL/VM/DCC fields for enabled and disabled paths, and debug values that must survive later getter recalculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_mode_vba.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_rq_dlg_helpers.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_rq_dlg_helpers.c

### Purpose
`display_rq_dlg_helpers.c` provides debug printers for DML requestor, deadline generator, and TTU parameter and register structures. It does not compute display behavior; it serializes important RQ/DLG values into the DML log stream so calculation results can be inspected.

### Important APIs, Types, And Functions
The exported functions are `print__rq_params_st()`, `print__data_rq_sizing_params_st()`, `print__data_rq_dlg_params_st()`, `print__data_rq_misc_params_st()`, `print__dlg_sys_params_st()`, `print__data_rq_regs_st()`, `print__rq_regs_st()`, `print__dlg_regs_st()`, and `print__ttu_regs_st()`. They consume `_vcs_dpi_display_*` structs from `display_mode_lib.h` and print through `dml_print()`.

### Control Flow
The printers are straight-line logging helpers. Composite printers such as `print__rq_params_st()` and `print__rq_regs_st()` call the luma and chroma data-level printers, then log common fields. DLG and TTU register printers enumerate each register-like field in hexadecimal, while sizing and system parameter printers use decimal or floating-point formats.

### State, Persistence, And Dependencies
The file does not mutate the supplied structures and has no retained state. Its only side effect is logging through the `mode_lib->logger` path hidden behind `dml_print()`. Dependencies are `display_rq_dlg_helpers.h`, `dml_logger.h`, `display_mode_lib.h`, and the logging backend that implements `DC_LOG_DML`.

### Integration Points
`dml1_display_rq_dlg_calc.c` calls these helpers after calculating RQ params and final DLG/TTU registers. They are useful for comparing software-generated register values against programming guide expectations, spreadsheet traces, or hardware debugging captures.

### Risks
Because these helpers are used for diagnostics, format mismatches or omitted fields can hide calculation errors. Several functions cast parameters to `(void)` but still access the structures, so the casts only suppress selected warnings. Logging volume can be high if enabled on mode-set hot paths. The printers assume pointers are valid and do not guard against NULL.

### Test Signals
Build tests should confirm format strings match argument types on all supported compilers. Runtime debug tests can enable DML logging for representative single-plane, dual-plane, DCC, VM, and cursor modes and verify expected luma/chroma sections and key register fields appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_rq_dlg_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_rq_dlg_helpers.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_rq_dlg_helpers.h

### Purpose
`display_rq_dlg_helpers.h` declares the debug-print API for RQ, DLG, and TTU calculation structures used by DML's display request and deadline code.

### Important APIs, Types, And Functions
It includes `display_mode_lib.h` for `struct display_mode_lib` and all `_vcs_dpi_display_*` structure definitions, then declares printers for RQ params, data sizing params, data DLG params, data misc params, DLG system params, data RQ regs, whole RQ regs, DLG regs, and TTU regs.

### Control Flow
The header has no runtime flow. It exposes the printer declarations so calculator files can log intermediate and final structures without depending directly on printer implementation details.

### State, Persistence, And Dependencies
There is no state in the header. Its dependency on `display_mode_lib.h` is broad but necessary because every printer signature names concrete DML structs. Include guards prevent repeated declarations.

### Integration Points
`dml1_display_rq_dlg_calc.h` includes this header, so any file using the DCN1 RQ/DLG calculator also sees these debug printer declarations. The C implementation integrates with `dml_logger.h`.

### Risks
The header exposes debug helpers in the same include path as functional RQ/DLG calculation APIs, so changes to structure names or header includes can cause wide rebuild fallout. It also creates a dependency edge from calculators to the full display mode library definitions.

### Test Signals
Compile tests are the main signal. Any rename or shape change of `_vcs_dpi_display_*` structs should fail here or in the C implementation quickly. DML logging smoke tests confirm the declarations and definitions stay linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_rq_dlg_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml1_display_rq_dlg_calc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml1_display_rq_dlg_calc.c

### Purpose
`dml1_display_rq_dlg_calc.c` computes DCN1 requestor sizing parameters, DLG deadline registers, and TTU QoS/register values from DML pipe, SoC, and IP parameters. It converts abstract surface geometry, tiling, VM, DCC, scaling, prefetch, and latency inputs into hardware-programmable register fields.

### Important APIs, Types, And Functions
Public functions are `dml1_rq_dlg_get_rq_params()`, `dml1_extract_rq_regs()`, and `dml1_rq_dlg_get_dlg_params()`. Private helpers include `get_bytes_per_element()`, `is_dual_plane()`, `get_blk256_size()`, `get_refcyc_per_delivery()`, `get_vratio_pre()`, `get_swath_need()`, `get_blk_size_bytes()`, `extract_rq_sizing_regs()`, `handle_det_buf_split()`, `dml1_rq_dlg_get_row_heights()`, and `get_surf_rq_param()`.

### Control Flow
RQ calculation starts by classifying luma/chroma planes, deriving bytes per element and 256-byte block dimensions, calculating swath width/request counts, computing meta request geometry, meta chunks, meta PTE bytes per frame, DPTE request shape, row height, row bytes, and group counts, then checking row-height results against the standalone row-height helper. Dual-plane YUV420 paths repeat the surface calculation for chroma. `handle_det_buf_split()` decides 256-byte versus 128-byte request behavior and luma/chroma detile-buffer allocation. `dml1_extract_rq_regs()` encodes byte sizes as log2 register fields and sets expansion modes and plane1 base address. `dml1_rq_dlg_get_dlg_params()` clears output regs, computes refclk-to-pixel conversions, vblank deadlines, prefetch line budget, VM/meta row timing, prefetch ratios, nominal and vblank PTE/meta timings, line and request delivery times, cursor TTU timing, QoS levels, and final `min_ttu_vblank`.

### State, Persistence, And Dependencies
The file is stateless except for output structures filled by callers. It reads immutable inputs from `display_mode_lib`, `_vcs_dpi_display_rq_dlg_params_st`, `_vcs_dpi_display_dlg_sys_params_st`, and `_vcs_dpi_display_e2e_pipe_params_st`. Dependencies include DML math wrappers, logger macros through helpers, SoC latencies, IP buffer sizes and delay totals, and DML enum values for tiling, source formats, scan direction, cursor depth, and macro tile size.

### Integration Points
This is the DCN1 register preparation layer used after higher-level DML has selected clocks, watermarks, and pipe configuration. Its outputs map directly to requestor, DLG, and TTU register programming structures consumed by AMD display hardware programming paths.

### Risks
The code relies on many power-of-two log calculations and assumes valid nonzero pitches, page sizes, clocks, swath heights, and request counts. Assertions catch several invalid or out-of-range register values but do not provide recovery. DCN1-specific limitations are embedded, including no DCC for 4:2:0, hardcoded chunk sizes, cursor0-only timing, and a DEGVIDCN10-137 workaround forcing chroma request size behavior. Division by zero is possible if malformed inputs provide zero clocks, bandwidth totals, or group counts.

### Test Signals
High-value tests include linear and tiled surfaces, horizontal and vertical scan, 4K/64K/256K tile sizes, RGB/444/420 8bpc and 10bpc formats, DCC on/off, VM on/off, cstate and pstate toggles, immediate flip, hsplit, cursor widths, small vblank edge cases, and register bitfield saturation/assertion boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml1_display_rq_dlg_calc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml1_display_rq_dlg_calc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml1_display_rq_dlg_calc.h

### Purpose
`dml1_display_rq_dlg_calc.h` declares the DCN1 RQ/DLG calculation API. It separates register-definition-agnostic request parameter calculation from register extraction and deadline/TTU register calculation.

### Important APIs, Types, And Functions
The header forward declares `struct display_mode_lib`, includes `display_rq_dlg_helpers.h`, and declares `dml1_extract_rq_regs()`, `dml1_rq_dlg_get_rq_params()`, and `dml1_rq_dlg_get_dlg_params()`. The function comments identify `dml1_rq_dlg_get_rq_params()` as the layer that computes real request values and `dml1_rq_dlg_get_dlg_params()` as the deadline calculation layer.

### Control Flow
The intended sequence is to calculate RQ params from pipe source parameters, extract RQ register encodings from those params, then calculate DLG and TTU registers using RQ/DLG params, system timing parameters, full e2e pipe params, and enable flags for cstate, pstate, VM, and immediate flip.

### State, Persistence, And Dependencies
The header owns no state. It depends on DML display struct definitions pulled in through `display_rq_dlg_helpers.h` and ultimately `display_mode_lib.h`. Output persistence is caller-owned through the register and parameter structs passed to the declared functions.

### Integration Points
Display hardware programming code can include this header to request DCN1-specific RQ/DLG register calculations. The helper include also exposes diagnostic printers for the same structures.

### Risks
The API is version-specific to DML1/DCN1 behavior. Mixing these declarations with newer DML versions or incompatible struct layouts could produce plausible but wrong register values. The signatures use several pointer outputs with no NULL annotations, so caller discipline is required.

### Test Signals
Compile integration with the C implementation is the baseline. Functional tests should exercise the declared call sequence and compare output register structs against known-good DCN1 fixtures for representative formats and timing modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml1_display_rq_dlg_calc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml_inline_defs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml_inline_defs.h

### Purpose
`dml_inline_defs.h` centralizes small math helpers used by DML calculation code. It wraps DC bandwidth math primitives with DML-named inline functions and adds a few local utilities for rounding, powers, modulo, and absolute value.

### Important APIs, Types, And Functions
The header provides `dml_min()`, `dml_min3()`, `dml_min4()`, `dml_max()`, `dml_max3()`, `dml_max4()`, `dml_max5()`, `dml_ceil()`, `dml_floor()`, `dml_round()`, `dml_log2()`, `dml_pow()`, `dml_fmod()`, `dml_ceil_2()`, `dml_ceil_ex()`, `dml_floor_ex()`, `dml_round_to_multiple()`, and `dml_abs()`.

### Control Flow
Most helpers are single-expression wrappers around `dcn_bw_*` functions. `dml_ceil()` and `dml_floor()` return zero for zero granularity. `dml_log2()` extracts the exponent bits from a `double` to return the floor log2 for positive power-oriented values. `dml_round_to_multiple()` rounds an unsigned integer up or down to a multiple depending on the `up` flag.

### State, Persistence, And Dependencies
The header has no state. It depends on `dcn_calc_math.h` for math primitives and `dml_logger.h` for DML-wide includes. Because these are inline functions, behavior is compiled into every including translation unit.

### Integration Points
This file is included by mode VBA and RQ/DLG calculators and underpins most DML spreadsheet-derived arithmetic. Register encodings and geometry calculations rely on these helpers for consistent granularity handling.

### Risks
`dml_log2()` type-puns through a pointer to `unsigned long long`, which depends on double representation and can raise strict-aliasing concerns. It only returns exponent-based floor values and is not a general logarithm for non-positive inputs. Rounding behavior must remain consistent with hardware programming guide expectations; changing wrappers can perturb many DML formulas.

### Test Signals
Unit-style tests should cover min/max compositions, ceil/floor with zero and nonzero granularities, round-to-multiple up/down and exact multiples, `dml_log2()` on powers of two and non-powers used by DML, and representative formulas from RQ/DLG and VBA code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml_inline_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml_logger.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml_logger.h

### Purpose
`dml_logger.h` maps DML logging calls to the AMD display core logger. It gives spreadsheet-derived DML code short logging macros without exposing logger plumbing at each call site.

### Important APIs, Types, And Functions
It defines `DC_LOGGER` as `mode_lib->logger`, `dml_print(str, ...)` as a wrapper around `DC_LOG_DML`, and `DTRACE(str, ...)` as the same DML log wrapper. There are no functions or types.

### Control Flow
The macros expand inline at call sites. They assume a visible variable named `mode_lib` exists in scope for `DC_LOGGER`. Calls are forwarded directly to `DC_LOG_DML`.

### State, Persistence, And Dependencies
The header has no state of its own. Its side effect is whatever the display core logging backend does with DML log messages. It depends on `DC_LOG_DML` and the `mode_lib->logger` member being available through including context.

### Integration Points
Mode VBA, RQ/DLG calculators, and debug helper printers use these macros for diagnostics, warnings, and trace dumps. The macro names preserve the style used by AMD's DML code.

### Risks
The implicit `mode_lib` dependency is fragile: any call site lacking that variable name fails to compile. Macros wrap calls in braces but are not expression-safe in all statement contexts. High-volume DTRACE logging can affect performance if the backend is enabled on hot paths.

### Test Signals
Compile coverage of all logging call sites is the main signal. Runtime DML logging tests should verify messages route to the expected DC log category and can be enabled or disabled through normal driver logging controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml_logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dsc/qp_tables.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dsc/qp_tables.h

### Purpose
`dsc/qp_tables.h` contains static DSC rate-control QP lookup tables. Each table maps a bits-per-pixel value to a 15-entry QP set for a specific color mode family, bits-per-component value, and min/max selector.

### Important APIs, Types, And Functions
There are no functions. The file defines `static const qp_table` objects consumed by `rc_calc_fpu.c`, including min and max tables for 444, 422, and 420 modes at 8, 10, and 12 bits per component. Each entry stores a `float bpp` and a `qp_set` of 15 quantization parameters.

### Control Flow
The file is pure data. Runtime selection happens in `get_qp_set()` in `rc_calc_fpu.c`, which chooses a table by color mode, bpc, and min/max selector, then indexes by half-bpp increments from the table's first bpp value.

### State, Persistence, And Dependencies
The arrays are `static const`, so they are translation-unit-local read-only data when included. They depend on `qp_table`, `qp_set`, and `struct qp_entry` being defined before inclusion, which is why `rc_calc_fpu.c` includes `rc_calc_fpu.h` first.

### Integration Points
The tables feed DSC RC parameter generation for AMD display code using `_do_calc_rc_params()`. They encode hardware/spec tuning data and are coupled to the DSC model's 15 range parameter slots.

### Risks
Because this is included as a header with definitions, including it from multiple translation units would duplicate data. Table ordering and first-bpp assumptions are critical: `get_qp_set()` computes `index = (bpp - table[0].bpp) * 2` and does not search by exact bpp. Unsupported or fractional bpp values outside half-step ranges can select the wrong row or exceed table bounds. Manual table edits are high risk because there is little structural validation beyond array size.

### Test Signals
Tests should cover every mode/bpc/min-max combination, first and last bpp rows, half-step bpp values, out-of-range bpp error logging, and known DSC fixtures comparing generated QP min/max arrays against expected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dsc/qp_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dsc/rc_calc_fpu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dsc/rc_calc_fpu.c

### Purpose
`dsc/rc_calc_fpu.c` computes Display Stream Compression rate-control parameters using floating-point formulas and QP lookup tables. It fills a `struct rc_params` for a requested color mode, bits per component, target DRM bpp, slice dimensions, native subsampling flag, and DSC minor version.

### Important APIs, Types, And Functions
The public function is `_do_calc_rc_params()`. Private helpers include `median3()`, `dsc_roundf()`, `get_qp_set()`, and `get_ofs_set()`. Macros `table_hash`, `MODE_SELECT`, and `TABLE_CASE` implement table selection over color mode, BPC, and min/max. The file includes `qp_tables.h` for data and `amdgpu_dm/dc_fpu.h` for `dc_assert_fp_enabled()`.

### Control Flow
`_do_calc_rc_params()` asserts that DC floating-point use is enabled, converts DRM bpp from sixteenths to float bpp, halves bpp for native 422/420, computes quant increment limits, derives grouped bpp, and switches by color mode to set initial fullness and line BPG offsets. It calculates initial transmit delay and adjusts it for padding constraints, sets flatness thresholds, retrieves QP min and max arrays, applies DSC 1.1 444 decrement rules, computes offset arrays, and writes fixed model size, edge factor, target offsets, and buffer thresholds.

### State, Persistence, And Dependencies
The only mutable state is the caller-provided `struct rc_params`. The code depends on Linux/DRM DSC types, AMD FPU guard discipline, `min`, `swap`, `memcpy`, `dm_error`, and the static QP tables. There is no hardware or file persistence.

### Integration Points
AMD display DSC code calls this when preparing DSC PPS/rate-control configuration. The output fields correspond to DSC RC model registers or PPS fields such as quant increment limits, initial fullness, flatness QPs, range QP min/max, range offsets, model size, edge factor, target offsets, and buffer thresholds.

### Risks
The function requires an FPU-safe context; calling without DC FPU enablement violates kernel floating-point rules. `get_qp_set()` assumes bpp maps to half-step table indexes and only checks upper bound, not negative indexes. Invalid color mode/BPC combinations can leave QP arrays unchanged if no table matches. The parameter name `is_navite_422_or_420` is misspelled but functional. Formula changes can alter DSC bitstream quality or compliance.

### Test Signals
Useful tests include known DSC RC parameter vectors for RGB/444/422/420 at 8/10/12 bpc, native 422/420 bpp halving, DSC 1.1 444 QP decrement behavior, slice widths not divisible by 3, boundary bpp values at each table edge, and FPU guard coverage in kernel display paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dsc/rc_calc_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dsc/rc_calc_fpu.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dsc/rc_calc_fpu.h

### Purpose
`dsc/rc_calc_fpu.h` defines the DSC rate-control parameter data model and declares the floating-point RC calculation entry point.

### Important APIs, Types, And Functions
It defines `QP_SET_SIZE` as 15, `typedef int qp_set[QP_SET_SIZE]`, `struct rc_params`, `enum colour_mode`, `enum bits_per_comp`, `enum max_min`, `struct qp_entry`, `typedef struct qp_entry qp_table[]`, and `_do_calc_rc_params()`. `struct rc_params` contains quant increment limits, initial fullness/transmit delay, line BPG offsets, flatness parameters, min/max QP sets, range offsets, model size, edge factor, target offsets, and 14 buffer thresholds.

### Control Flow
The header has no executable flow. It defines the shape that `_do_calc_rc_params()` fills and the enum values used by table selection in the implementation.

### State, Persistence, And Dependencies
There is no header state. It depends on `os_types.h` for fixed-width and boolean types and `<drm/display/drm_dsc.h>` for DRM DSC context. Output state persists in caller-owned `struct rc_params` instances.

### Integration Points
The header is consumed by DSC rate-control code and by `qp_tables.h`, whose static table definitions require `qp_set`, `qp_table`, and `struct qp_entry`. Callers use the declared function to obtain RC fields before building DSC PPS/register programming.

### Risks
The enum names and values must remain consistent with `rc_calc_fpu.c` table hashing. The typo in `is_navite_422_or_420` is part of the function signature and should be changed only with all callers updated. The fixed QP and threshold sizes mirror DSC assumptions; changing them would require table and PPS layout changes.

### Test Signals
Compile tests should cover all callers and table inclusion. Functional tests should verify the complete `struct rc_params` layout is populated for each supported enum combination and that unsupported combinations fail predictably at the caller level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dsc/rc_calc_fpu.h -->
