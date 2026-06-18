# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4_calcs.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001426`: lines 1-5279, `Docs/researches/chunks/subset-b-001426_research.md`
- `subset-b-001427`: lines 5280-9672, `Docs/researches/chunks/subset-b-001427_research.md`
- `subset-b-001428`: lines 9673-13402, `Docs/researches/chunks/subset-b-001428_research.md`

## Chunk Research

### subset-b-001426: lines 1-5279

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4_calcs.c lines 1-5279

## Scope And Purpose

This chunk is the first calculation block of the DCN4 DML2 core model. It defines constants, string helpers, generated readout accessors, and many of the low-level formula helpers used by later mode-support and mode-programming passes. The code is internal math for AMD display mode validation rather than direct hardware programming: it reads `struct dml2_display_cfg`, SOC/IP bounding-box data, and intermediate `mode_lib` scratch/model state, then fills arrays and scalar outputs for clocks, bandwidths, request sizes, DET allocation, MALL/mCache use, VM/PTE row behavior, DSC/link feasibility, latency, and the first part of prefetch scheduling.

The chunk covers these major responsibilities:

- Human-readable enum strings for bandwidth and SOC-state logging.
- Pixel-format, swizzle, block-size, bytes-per-pixel, 4:2:0, rotation, and pipe-to-plane helper logic.
- Swath width, swath height, DET buffer sizing, compressed-buffer reservation, unbounded request eligibility, and DCC request classification.
- Output-link and DSC helper formulas for BPP truncation, ODM selection, DSC delay, DTBCLK, and writeback clocks/delay.
- GPUVM/HostVM, DPTE, meta row, PTE buffer, one-row-per-frame, static-screen MALL, mCache, and TDLUT calculations.
- Average and urgent bandwidth availability/requirements, urgent latency, trip-to-memory latency, cursor fetch attributes, urgent burst factors, DCFCLK deep sleep, dynamic metadata timing, and early `CalculatePrefetchSchedule()` setup.

The public exports appear later in the same file and are declared in `dml2_core_dcn4_calcs.h` (`dml2_core_calcs_mode_support_ex()`, `dml2_core_calcs_mode_programming_ex()`, DLG/watermark/register getters, support-info getters, and enum string helpers). In this chunk, only `dml2_core_internal_bw_type_str()` and `dml2_core_internal_soc_state_type_str()` are non-static; the rest are static formula blocks that feed those exported flows.

## Important APIs, Types, And Functions

The code depends on the DML2 internal type system from `dml2_internal_shared_types.h`, `dml2_core_dcn4_calcs.h`, `dml2_debug.h`, `lib_float_math.h`, and `dml_top_types.h`. Important types visible through function signatures include:

- `struct dml2_display_cfg`, whose planes, streams, GPUVM/HostVM settings, overrides, timing, cursor, TDLUT, DCC, MALL, and link descriptions drive nearly every calculation.
- `struct dml2_core_internal_display_mode_lib`, especially `mode_lib->mp` for mode-programming results and `mode_lib->ms` for mode-support/support-info results. The accessor macros synthesize many `dml_get_*()` functions that read these fields per pipe, per plane, or globally.
- `struct dml2_core_internal_scratch`, which provides large local workspaces for noinline/stack-heavy helpers.
- Parameter carrier structs such as `dml2_core_shared_calculate_vm_and_row_bytes_params`, `dml2_core_calcs_CalculateVMRowAndSwath_params`, `dml2_core_calcs_CalculateSwathAndDETConfiguration_params`, `dml2_core_calcs_calculate_mcache_*_params`, and `dml2_core_calcs_CalculatePrefetchSchedule_params`.
- Enumerations for source format, swizzle mode, rotation, output format/encoder/rate, DSC enablement, ODM mode, MALL/static-screen overrides, SVP/phantom pipe overrides, bandwidth type, SOC state type, QoS type, and internal request type.

Important helper groups:

- Logging/readout helpers: `dml2_print_mode_support_info()` logs each support bit, while the `dml_get_per_pipe_var_func`, `dml_get_per_plane_var_func`, `dml_get_per_plane_array_var_func`, and `dml_get_var_func` macros generate field accessors later used by programming/register export code.
- Format and geometry helpers: `dml_is_420()`, `dml_get_tile_block_size_bytes()`, `dml_is_vertical_rotation()`, `dml_get_gfx_version()`, and `CalculateBytePerPixelAndBlockSizes()` map DML formats and swizzles into byte-per-pixel, 256B request dimensions, macro-tile dimensions, and linear-128 flags.
- Swath and DET helpers: `CalculateSwathWidth()`, `UnboundedRequest()`, `CalculateMaxDETAndMinCompressedBufferSize()`, `CalculateDETBufferSize()`, and `CalculateSwathAndDETConfiguration()` choose per-plane swath spans, rounded swath bytes, request sizes, DET split, compressed-buffer size, viewport support flags, `compbuf_reserved_space_64b`, and `hw_debug5`.
- Link/display helpers: `TruncToValidBPP()`, `CalculateRequiredDispclk()`, `DecideODMMode()`, `CalculateODMConstraints()`, `ValidateODMMode()`, `CalculateODMMode()`, `CalculateOutputLink()`, `dscceComputeDelay()`, `dscComputeDelay()`, `DSCDelayRequirement()`, `RequiredDTBCLK()`, `CalculateWriteBackDelay()`, `CalculateWriteBackDISPCLK()`, and `CalculateMaxVStartup()` model link capacity, DSC/FEC requirements, ODM pipe/OPP consumption, timing divisibility, DSC delay, DTBCLK, and VStartup limits.
- VM/PTE/meta helpers: `CalculateHostVMDynamicLevels()`, `CalculateVMAndRowBytes()`, `CalculatePrefetchSourceLines()`, `CalculateRowBandwidth()`, and `CalculateVMRowAndSwath()` compute meta rows, DPTE rows, VM bytes, PTE buffer fit, one-row-per-frame behavior, per-plane prefetch source lines, row bandwidth, PTE buffer programming fields, and MALL static-screen use.
- DCC, MALL, mCache, and TDLUT helpers: `CalculateDCCConfiguration()`, `CalculateMALLUseForStaticScreen()`, `CalculateSurfaceSizeInMall()`, `calculate_mcache_row_bytes()`, `calculate_mcache_setting()`, `calculate_mall_bw_overhead_factor()`, and `calculate_tdlut_setting()` derive compressed request properties, static-screen/sub-VP MALL footprint, mCache rows/offsets/combining, MALL/SVP overhead factors, and 3D LUT fetch/PTE timing quantities.
- Bandwidth and latency helpers: `dml_get_return_bandwidth_available()`, `calculate_bandwidth_available()`, `calculate_avg_bandwidth_required()`, `get_urgent_bandwidth_required()`, `CalculateUrgentLatency()`, `CalculateTripToMemory()`, `CalculateMetaTripToMemory()`, `CalculateTarb()`, `CalculateTWait()`, and `CalculateExtraLatency()` convert SOC clock/derate tables and per-plane demand into available/required bandwidth and latency terms.
- Cursor and burst helpers: `calculate_cursor_req_attributes()`, `calculate_cursor_urgent_burst_factor()`, and `CalculateUrgentBurstFactor()` size cursor requests and derive urgent burst multipliers from DET/cursor buffer time coverage.
- Clock and metadata helpers: `CalculateSinglePipeDPPCLKAndSCLThroughput()`, `CalculateDCFCLKDeepSleepTdlut()`, `CalculateDCFCLKDeepSleep()`, and `CalculateVUpdateAndDynamicMetadataParameters()` derive scaler throughput, single-DPP DPPCLK, deep-sleep DCFCLK, VUpdate/VReady offsets, and dynamic metadata timing.
- Prefetch scheduling starts at `CalculatePrefetchSchedule()` and, within this chunk, initializes state, checks dynamic metadata time, computes scaler/DISP/DSC delay into `DSTXAfterScaler`, and starts the formulas used to decide if VM, row, cursor, TDLUT, and pixel data can be fetched before active.

## Control Flow

The chunk is formula-heavy, but it has several clear pipelines.

Format and surface characterization starts with source format, surface tiling, pitch, rotation, and viewport information. `CalculateBytePerPixelAndBlockSizes()` first maps a source format into luma/chroma byte counts, DET byte counts, 256B block dimensions, macro-tile dimensions, and linear-surface flags. It distinguishes GFX11 swizzles from DCN4/GFX12 swizzles and asserts on unsupported formats or swizzle modes. `CalculateSwathWidth()` then converts viewport dimensions into single-DPP swath width, applies ODM split limits and DPP splitting unless `ForceSingleDPP` is set, halves chroma width for 4:2:0, aligns swath widths to 256B request blocks, and emits maximum swath heights.

Swath and DET configuration flows through `CalculateSwathAndDETConfiguration()`. It calls `CalculateSwathWidth()`, computes full luma/chroma swath bytes, determines total active DPPs, checks whether the mode qualifies for unbounded requesting, and calls `CalculateDETBufferSize()`. DET allocation has multiple policies: unbounded request uses only surface 0 DET and leaves the rest as compressed buffer; ordinary allocation first satisfies minimum DET needed for two full swaths, honors per-plane DET overrides and phantom pipes, optionally distributes DET by stream pixel-rate to minimize reallocation, and otherwise distributes remaining DET by read bandwidth. After DET allocation, `CalculateSwathAndDETConfiguration()` chooses full or half swath heights, 256/128/64 byte request sizes, marks viewport-size support failures, splits DET bytes between luma and chroma, reserves compressed-buffer 64B slots, and sets `hw_debug5` based on multi-plane or SDPIF-rate-limit policy.

DCC request classification is separate in `CalculateDCCConfiguration()`. It estimates whether horizontal and vertical worst-case swaths fit in DET for luma/chroma, handles 4:2:0 and 10-bit packing adjustments, chooses 256B, contiguous 128B, or non-contiguous 128B request types depending on scan direction and DCC programming assumptions, and converts those request types into max compressed/uncompressed/independent block sizes. DCC-disabled cases zero the block outputs.

VM/PTE/meta control flow is split between per-plane helper and orchestration. `CalculateVMAndRowBytes()` calculates DCC meta request dimensions, meta row bytes, meta PTE bytes, DPDE bytes, VM bytes, pixel PTE request dimensions, virtual memory page dimensions, DPTE row height/width/bytes, and one-row-per-frame alternatives. It has early zero-output behavior when GPUVM is disabled and it asserts on unsupported GPUVM page-size versus tiling combinations. `CalculateVMRowAndSwath()` calls this helper first for chroma when the format is dual-plane, then for luma, calculates prefetch source lines for each plane, scales VM/PTE bytes by HostVM dynamic levels, checks PTE buffer fit and one-row-per-frame fit, runs static-screen MALL selection, chooses `PTE_BUFFER_MODE` and `BIGK_FRAGMENT_SIZE`, switches to one-row-per-frame rows when required, checks DCC meta-buffer size, and finally computes DPTE/meta row bandwidth.

MALL and mCache control flow starts with `CalculateSurfaceSizeInMall()`, which estimates static-screen and sub-VP footprints from surface, viewport, block size, and bytes-per-pixel, then checks them separately against `MALLAllocatedForDCN`. `CalculateMALLUseForStaticScreen()` honors force-enable/force-disable overrides and greedily adds the smallest eligible surfaces that fit and have one-row-per-frame PTE data. `calculate_mcache_setting()` exits early when DCC is off, otherwise calls `calculate_mcache_row_bytes()` for luma and optional chroma, derives whether iMALL can combine two mCache remainders, whether luma/chroma can share the last mCache, and fills per-plane mCache offsets and shift granularities.

ODM and link control flow starts with required DISPCLK estimates for bypass and 2:1/3:1/4:1 combine. In auto mode, `DecideODMMode()` picks at least the ODM mode required by DISPCLK, DSC maximum active pixels, 4:2:0 buffer width, and DSC slice-count constraints. `CalculateODMMode()` then validates the chosen mode against max DISPCLK, DPP/OPP budget, segment symmetry, HActive divisibility, DSC max pixels/slices, and 4:2:0 max active width. `CalculateOutputLink()` separately walks HDMI, DP/eDP, DP2 UHBR, and HDMI FRL rates in increasing capability order, calls `TruncToValidBPP()` to find a legal BPP, and can enable DSC/FEC when `dml2_dsc_enable_if_necessary` and uncompressed link capacity is insufficient.

Bandwidth and latency flow uses SOC derate tables. `calculate_bandwidth_available()` fills average and urgent available bandwidth for system-active and SVP-prefetch states, separately for SDP and DRAM, plus VM-only and pixel-and-VM urgent DRAM cases. `calculate_avg_bandwidth_required()` accumulates system-active and SVP-prefetch average demand from luma, chroma, cursor, DCC overhead, and MALL/SVP factors, excluding phantom pipes from system-active average demand but including them during SVP prefetch. `get_urgent_bandwidth_required()` calculates per-plane and total urgent demand as the maximum of VM row, active plus flip, prefetch plus flip, active plus excess vactive fill, and max prefetch cases; it can include real immediate-flip bandwidth or qualified row bandwidth, and it excludes phantom pipes outside SVP-prefetch state.

Latency helpers distinguish old QoS formulas from DCN4x QoS formulas. `CalculateUrgentLatency()`, `CalculateTripToMemory()`, and `CalculateMetaTripToMemory()` either use legacy urgent-latency inputs or derive latency from FCLK/UCLK cycle fields and margins. `CalculateTarb()` adds extra arbitration bytes for pixel chunks, meta chunks, TDLUT groups, and GPUVM DPTE groups scaled by HostVM levels and inefficiency factors. `CalculateExtraLatency()` combines DCHUB arb-to-return delay, optional ROB outstanding-request pressure, round-trip/reordering legacy terms, HostVM trips, and `Tarb` into `ExtraLatency`, `ExtraLatency_sr`, and `ExtraLatencyPrefetch`.

The visible portion of `CalculatePrefetchSchedule()` initializes a large scratch local block, derives `TWait_p`, HostVM trip count, VUpdate/dynamic metadata timing, VM and row trip timing, dynamic metadata deadlines, scaler/DISP cycles, and `DSTXAfterScaler`. It returns early as supportable if DPPCLK or DISPCLK is zero, and otherwise continues beyond this chunk to calculate detailed prefetch bandwidth and timing.

## State And Persistence Behavior

There is no heap allocation, locking, reference counting, file I/O, or persistent kernel state in this chunk. State persists only through caller-provided arrays, parameter structs, `scratch`, and `mode_lib` fields populated later by the top-level mode-support/programming flows.

The generated `dml_get_*()` accessors expose previously calculated state from `mode_lib->mp` and `mode_lib->ms`, including watermarks, DPP/DCF/disp clocks, bandwidths, DET/compressed buffer sizes, VM/PTE row sizes, mCache allocation, MALL allocation, stutter metrics, urgent latencies, and support metrics. They do not mutate state.

Calculation helpers generally zero their local scratch structs or output arrays before filling them, but many assume callers have already populated dependent fields. Examples include `CalculateVMRowAndSwath()` relying on `myPipe[]` swath/format/timing data and `CalculatePrefetchSchedule()` relying on row-byte, TDLUT, latency, and clock inputs. Several helpers write flags that drive mode acceptance later: `ViewportSizeSupport`, `PTEBufferSizeNotExceeded`, `DCCMetaBufferSizeNotExceeded`, `ExceededMALLSize`, `NotEnoughUrgentLatencyHiding`, `NotEnoughTimeForDynamicMetadata`, `TotalAvailablePipesSupport`, and link BPP/DSC/FEC outputs.

Phantom pipes and MALL modes materially alter stored results. Phantom planes can receive zero DET allocation, get oversized effective DET in urgent-burst calculations, be excluded from system-active bandwidth but included in SVP-prefetch bandwidth, and force one-row-per-frame/PTE buffer mode. Static-screen MALL selection persists through `is_using_mall_for_ss[]`, `use_one_row_for_frame[]`, row-height replacements, and MALL allocation outputs.

The scratch object is important for stack management and state isolation. Several functions are marked `noinline_for_stack` or use scratch-local structs because these formulas carry many arrays and temporaries. Callers must not treat scratch contents as long-lived outputs unless the parameter struct explicitly points to output storage.

## Dependencies And Integration Points

The chunk integrates with AMDGPU display through DML2, not through direct DRM or hardware register APIs. The primary integration contract is:

- Input: display configuration, SOC/IP bounding-box clocks and derates, plane/stream overrides, timing, format, tiling, VM, MALL, cursor, DCC, TDLUT, link, DSC, and writeback parameters.
- Internal state: `mode_lib->mp` and `mode_lib->ms`, plus scratch parameter structs passed through the mode-support and mode-programming paths.
- Output: support flags, bandwidth/latency requirements, clock requirements, DET/mCache/MALL/PTE/DCC/TDLUT parameters, output link type/rate/BPP/DSC/FEC, and prefetch timing values later consumed by watermarks, DLG/TTU register generation, FAMS2 programming, and support-info getters.

Math and logging dependencies are central. All formulas use `math_min2`, `math_max*`, `math_ceil2`, `math_floor2`, `math_round`, `math_log`, and `math_pow` wrappers from the local DML math library, and debug output is emitted with `DML_LOG_VERBOSE` under normal and `__DML_VBA_DEBUG__` paths. Assertion-style validation uses `DML_ASSERT()` for unsupported enum values, unsupported VM page-size/tile combinations, impossible zero mCache sizes, invalid cursor BPP, and some derived bounds.

Several downstream functions outside this line range consume the values generated here. The later mode-support routine uses these helpers to select DPP/ODM/topology, test bandwidth and prefetch support, decide voltage/SOC state feasibility, and set support info. The later mode-programming routine uses the same computed state to build watermark, DLG/TTU, arb, sync, MALL/mCache, FAMS2, and per-stream/per-plane programming outputs.

## Risks And Edge Cases

Rounding and units are high-risk throughout. The code mixes bytes, KB, 64B slots, MHz, kHz, microseconds, cycles, pixels, lines, and fixed 256B/128B/64B request granularities. Small changes to `math_ceil2`/`math_floor2` operands can change mode support, DET fit, PTE buffer fit, DCC request type, link BPP, or prefetch feasibility.

Format and tiling coverage is assert-driven. Unsupported source formats, swizzles, cursor BPP values, or GPUVM page-size/tile combinations hit `DML_ASSERT()` or fall back to defaults intended only for disabled VM cases. New formats or swizzle modes need explicit byte/block/tile handling here before being trusted by mode validation.

Dual-plane and 4:2:0 handling is subtle. Chroma widths, bytes-per-pixel, PTE buffer split, swath sizes, request sizes, DCC limits, DCC overhead, prefetch source lines, urgent burst factors, and row bandwidth all branch on `dml_is_420()` or `dml2_rgbe_alpha`. A luma-only assumption can either undercount chroma bandwidth or over-allocate scarce DET.

Rotation and stationary viewport behavior change alignment math. Vertical rotation swaps width/height-oriented DPTE/meta/swath calculations; stationary viewports use exact floor-aligned spans in several places. Off-by-one errors in these branches can break rotated displays, MPO, or sub-viewport use cases.

Phantom/SVP and MALL interactions are complex. Phantom pipes are sometimes excluded, sometimes included, sometimes given synthetic buffer depth, and sometimes force one-row-per-frame behavior. Static-screen MALL and sub-VP MALL footprints are counted separately, which is intentional but easy to misinterpret when changing allocation checks.

DET and compressed-buffer policies are sensitive to overrides. Per-plane DET overrides, minimize-DET-reallocation mode, unbounded request forcing, MRQ presence, compressed-buffer segment sizes, and `ALLOW_SDPIF_RATE_LIMIT_PRE_CSTATE` alter allocation and support outcomes. A local change can affect both bandwidth support and later watermark/stutter behavior.

Link validation has fallback behavior that can mask root causes. `CalculateOutputLink()` walks rates and can enable DSC if necessary; failures often surface as invalid output BPP (`__DML2_CALCS_DPP_INVALID__` or zero) rather than detailed link errors. ODM/DSC slice divisibility is also enforced here, including a TODO noting that only HActive timing divisibility is checked for timing-div mode.

Division-by-zero protection is mostly by caller contract. Many formulas divide by clocks, return bandwidth, line time, request dimensions, PTE buffer-derived dimensions, mCache sizes, VRatio, or total bandwidth. Some assertions exist, but corrupted or incomplete bounding-box/config inputs could still produce invalid floating-point results before an explicit support failure.

Several comments identify known deltas or incomplete areas, including progressive-to-interlace pixel-clock adjustment, linear DCC meta row bytes, average bandwidth cursor inclusion, backend/MST mapping in later code, H timing divisibility TODOs, and programming-guide condition notes. These are useful signals for regressions when reconciling spreadsheet DML behavior with driver behavior.

## Test Signals

Useful validation signals for this chunk are mostly indirect, through mode validation results, calculated programming values, and display behavior:

- Mode-support acceptance/rejection for large viewports, high pixel clocks, high BPP, DSC-required links, forced/auto ODM, 3:1 ODM, HDMI FRL, DP2 UHBR, eDP/DP HBR variants, and forced output-link rates.
- Swath/DET traces for single-DPP versus multi-DPP, `ForceSingleDPP`, DET override, minimize-det-reallocation, unbounded request, MRQ present/absent, linear surfaces, DCC enabled/disabled, and 4:2:0 10-bit cases.
- GPUVM/HostVM tests varying page size, page-table levels, HostVM min page size, one-row-per-frame, PTE buffer size, immediate flip, static-screen MALL, phantom pipes, and vertical rotation. Watch `PTEBufferSizeNotExceeded`, `DCCMetaBufferSizeNotExceeded`, `PTE_BUFFER_MODE`, `BIGK_FRAGMENT_SIZE`, DPTE/meta row bytes, row bandwidth, and VM bytes.
- MALL and mCache tests with force-enable/force-disable/optimize static-screen MALL, sub-VP phantom pipes, DCC on/off, GPUVM on/off, small and large mCache sizes, luma/chroma sharing, and iMALL enablement. Watch `SurfaceSizeInMALL`, `ExceededMALLSize`, `num_mcaches_*`, `mcache_offsets_*`, and combine flags.
- Latency/bandwidth tests varying SOC derate tables, DCFCLK/FCLK/UCLK/DRAM bandwidth, QoS type, urgent cycle margins, HostVM inefficiency, TDLUT enablement, cursor widths/BPP, DCC overhead, MALL/SVP overhead, and immediate flip. Watch average/urgent required versus available bandwidth, urgent latency, trip-to-memory latency, `ExtraLatency`, `ExtraLatencyPrefetch`, urgent burst factors, and `NotEnoughUrgentLatencyHiding`.
- Dynamic metadata and prefetch tests with small VBlank/VStartup, interlace, P2I support, DSC delay, scaler enabled/disabled, ODM/MSO modes, TDLUT setup, and GPUVM/HostVM. Watch `VUpdateOffsetPix`, `VUpdateWidthPix`, `VReadyOffsetPix`, `Tdmdl`, `NotEnoughTimeForDynamicMetadata`, `DSTXAfterScaler`, `Tvm_trips`, and `Tr0_trips`.
- Hardware symptoms from bad calculations include underflow, flicker during pstate changes or immediate flips, incorrect DRAM/FCLK clock-change support, black screens only on high-bandwidth/rotated/chroma modes, incorrect DSC/link negotiation, cursor corruption, or unexpected loss of self-refresh/stutter efficiency.

`__DML_VBA_DEBUG__` logging is an important test aid because most helpers log their inputs and derived values. Comparing debug traces before and after formula changes is likely more useful than unit-level tests for isolated helpers, although focused formula tests would be valuable for byte/block-size mapping, BPP truncation, ODM validation, VM/PTE row sizing, DCC request classification, and DET allocation boundaries.

## Cross-Chunk Notes

This is only lines 1-5279 of a 13402-line file. The chunk starts the DCN4 DML2 calculation pipeline and reaches the early part of `CalculatePrefetchSchedule()`. Later chunks contain the rest of prefetch scheduling, global prefetch admissibility, peak/immediate-flip bandwidth support, watermarks, pstate/DRAM clock-change support, mode-support orchestration, mode-programming orchestration, DLG/TTU register packing, FAMS2 programming extraction, and public getters. The final per-file report should merge this chunk with those later chunks to explain the complete flow from display configuration and SOC state through mode support, selected programming state, and exported register/programming values.

### subset-b-001427: lines 5280-9672

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4_calcs.c lines 5280-9672

## Scope And Purpose

This chunk covers the central DCN4 DML2 mode-support calculation path. It starts in the middle of `CalculatePrefetchSchedule()`, completes that per-plane prefetch scheduler, then defines helper routines for global prefetch admissibility, urgent/average bandwidth validation, immediate flip scheduling, watermark and clock-change support, p-state latency hiding, DRAM/UCLK/QoS conversion, HostVM inefficiency, G6 temperature-read blackout lookup, and the exported mode-support wrapper. The chunk ends at the start of `CalculatePixelDeliveryTimes()`, so that final function is only a boundary marker for the next chunk.

The main externally visible entry in this range is `dml2_core_calcs_mode_support_ex()`, which calls the internal `dml_core_mode_support()` and, on success, copies `mode_lib->ms.support` into the caller's `out_evaluation_info`. Most other functions are `static` calculation helpers that mutate the `mode_lib->ms` mode-support workspace, arrays in `core_display_cfg_support_info`, or local scratch structures under `struct dml2_core_internal_scratch`.

Functionally, this chunk answers whether a display configuration can run at a given minimum clock table entry. It derives clocks, DPP/OPP/ODM/DSC allocation, swath and DET layout, VM/PTE/meta row traffic, urgent and average bandwidth needs, prefetch timing, immediate flip feasibility, MALL/p-state combinations, watermarks, and a large conjunction of support flags. It is formula-heavy modeling code rather than direct hardware programming.

## Important APIs, Types, And Functions

`CalculatePrefetchSchedule()` is only partially visible in this chunk, but this range contains its final and most important scheduling logic. It computes:

- `DSTXAfterScaler` and `DSTYAfterScaler`, including 4:2:0 and progressive-to-interlace output delay handling.
- Rounded VM and row-trip terms: `Tvm_trips_rounded`, `Tr0_trips_rounded`, and flip variants, quantized to quarter-line units with minimum quarter-line floors.
- `Tno_bw` and `Tno_bw_flip`, the no-bandwidth latency component for deeper GPUVM page-table levels, extra latency, MRQ, and 3DLUT restrictions.
- `prefetch_sw_bytes`, `RequiredPrefetchBWMax`, one-to-one (`oto`) prefetch timing, equalized (`equ`) prefetch timing, VM/row/pixel prefetch bandwidths, cursor prefetch bandwidth, and final `VRatioPrefetchY/C`.
- Failure outputs such as `NoTimeForDynamicMetadata`, `NoTimeForPrefetch`, zeroed prefetch bandwidths, and zeroed VM/row line counts when timing is impossible.

`get_num_lb_source_lines()` estimates line-buffer source lines from maximum line-buffer lines, line-buffer size in bits, DPP count, viewport dimensions, horizontal ratio, and rotation. It switches to viewport height for vertical rotation and assumes 57 bits per pixel in the line buffer model.

`find_max_impact_plane()` and `calculate_impacted_Tsw()` support the global prefetch check. The former chooses the other plane with the largest accumulated return-path delay; the latter sums all prefetch swath bytes except one excluded plane and divides by a bandwidth estimate.

`CheckGlobalPrefetchAdmissibility()` performs an aggregate multi-plane prefetch sanity check when `DML_GLOBAL_PREFETCH_CHECK` is enabled. It estimates return-path pressure from detile-buffer and line-buffer burst sizes, clamps by ROB plus compressed-buffer worst-case occupancy, computes `impacted_dst_y_pre[]`, and requests a prefetch schedule recalculation if the impacted prefetch requirement exceeds the current per-plane `dst_y_prefetch[]`.

`calculate_peak_bandwidth_required()` calls `get_urgent_bandwidth_required()` across `dml2_core_internal_soc_state_max` and `dml2_core_internal_bw_max` for several views of bandwidth: vactive-only urgent bandwidth, urgent bandwidth including prefetch and optional flip, qualification row bandwidth, non-urgent bandwidth, and per-surface average/peak arrays. It uses zero/unity arrays to selectively include or suppress prefetch, cursor, VM-row, flip, and burst-factor terms.

`check_urgent_bandwidth_support()` compares urgent and non-urgent requirements against available SDP/DRAM bandwidth for system-active and, when MALL is allocated, SVP-prefetch states. It outputs nominal and MALL urgent-bandwidth fractions plus separate vactive-only and full-bandwidth support flags.

`get_bandwidth_available_for_immediate_flip()` returns the smaller leftover bandwidth between SDP and DRAM for the selected SoC state after non-flip urgent requirements. `calculate_immediate_flip_bandwidth_support()` validates flip-inclusive urgent and non-urgent bandwidth against the available table and emits `frac_urg_bandwidth_flip` plus `flip_bandwidth_support_ok`.

`CalculateFlipSchedule()` derives per-plane immediate flip timing and bandwidth. It handles two modes:

- `use_lb_flip_bw == true`: mode-support lower-bound flip bandwidth, based on max flip time, VM bytes, two row fetches, register limits, and whether immediate flip is requested.
- `use_lb_flip_bw == false`: bandwidth is apportioned from total available flip bandwidth by per-pipe flip bytes, then VM/row flip times and register line counts are tested.

`CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport()` computes urgent, stutter, Z8, USR retraining, DRAM clock-change, FCLK-change, writeback, and G6 temperature-read watermarks. It then derives per-plane active latency hiding from line-buffer lines, DET buffering, scaler/output delay, multi-surface sharing penalty, writeback limits, and reserved vblank overrides. Outputs include `DRAMClockChangeSupport[]`, `FCLKChangeSupport[]`, global clock-change flags, `SubViewportLinesNeededInMALL[]`, `VActiveLatencyHidingMargin[]`, `VActiveLatencyHidingUs[]`, `g6_temp_read_support`, and `MaxActiveFCLKChangeLatencySupported`.

`calculate_bytes_to_fetch_required_to_hide_latency()` computes luma/chroma bytes needed in vactive to hide a latency interval, including pixel swaths, optional DCC meta rows under MRQ, and optional GPUVM DPTE rows.

`calculate_vactive_det_fill_latency()` derives an informative vactive DET fill delay from the excess of peak over average bandwidth, splitting effective excess between luma and chroma according to their read bandwidth and DRAM DCC overhead factors.

`calculate_excess_vactive_bandwidth_required()` converts a per-plane override `max_vactive_det_fill_delay_us[dml2_pstate_type_uclk]` into extra luma/chroma bandwidth requirements.

Clock/QoS helpers in this chunk include:

- `uclk_khz_to_dram_bw_mbps()`, which converts UCLK to DRAM bandwidth directly from DRAM channel geometry or through an alternate bandwidth table.
- `dram_bw_kbps_to_uclk_mhz()`, the inverse direct conversion used when the min clock table has no explicit UCLK.
- `get_qos_param_index()`, which selects the previous QoS-parameter bucket for a UCLK threshold table.
- `get_active_min_uclk_dpm_index()`, which finds the exact UCLK entry in `mode_lib->soc.clk_table.uclk`.
- `calculate_hostvm_inefficiency_factor()`, which derives HostVM bandwidth inefficiency from pixel+VM versus VM-only urgent bandwidth and enforces a prefetch factor of at least 4 when remote IOMMU outstanding translations are below maximum requests.
- `get_g6_temp_read_blackout_us()` and `get_max_urgent_latency_us()`, which provide blackout and worst urgent-latency terms for DCN4x QoS/watermarks.

`dml_core_ms_prefetch_check()` is the dedicated prefetch, flip, watermark, and p-state support sub-pass inside mode support. It prepares 3DLUT settings, extra latency, per-plane `CalculatePrefetchSchedule()` calls, optional global prefetch recalculation, prefetch urgent bandwidth, immediate flip bandwidth, and watermarks.

`dml_core_mode_support()` is the main internal mode-support engine. It clears scratch and mode-support state, maps the requested clock table index into DCFCLK/FCLK/UCLK/DRAM bandwidth/QoS indexes, runs front-end format/link/pipe/resource checks, builds swath and VM-row state, calculates average and urgent bandwidth availability, invokes `dml_core_ms_prefetch_check()`, checks ROB and outstanding-request support, and finally produces `mode_lib->ms.support.ModeSupport`.

`dml2_core_calcs_mode_support_ex()` is the public wrapper in this chunk. It returns the internal mode-support result and copies the support info out only when the mode is supported.

## Control Flow

The visible tail of `CalculatePrefetchSchedule()` first converts scaler/output delay into integer destination lines and pixels. It then quantizes VM and row latency trips to quarter-line boundaries. GPUVM-enabled paths use measured VM/row trips; non-GPUVM paths fall back to extra latency, urgent latency, trip-to-memory, DCC MRQ, 3DLUT, or a quarter-line minimum depending on active features.

The scheduler computes `Tno_bw` only for GPUVM cases where page-table levels require extra no-bandwidth latency. For flip, `Tno_bw_flip` is retained only if MRQ is present or there are at least three GPUVM page-table levels, because the comment explicitly excludes 3DLUT from immediate flip.

The function then builds byte counts for prefetch:

1. Pixel swath bytes are calculated from prefetch source lines, swath widths, bytes per pixel, and MALL prefetch SDP overhead.
2. Base VM bytes are augmented with 3DLUT PTE bytes and an extra TDPE term when 3DLUT setup and GPUVM are enabled.
3. 3DLUT row bytes are modeled as half the 3DLUT frame bytes, rounded up.
4. Minimum swath line requirements for one-to-one and equalized schedules are capped by prefetch source line ratios, 3DLUT drain time, and a two-line floor.

The one-to-one path estimates a baseline prefetch bandwidth from vactive swath bandwidth and one-line-per-line-time pixel fetch rate, applies MALL overhead, caps it by the minimum swath time, and then raises it to satisfy VM and row register-limit lower bounds. It derives `Tvm_oto`, `Tr0_oto`, line counts, `dst_y_prefetch_oto`, optional global prefetch impact, and `Tpre_oto`.

The equalized path derives available `dst_y_prefetch_equ` from `VStartup`, setup time, calculation time, wait time, and scaler-output delay. It applies the U6.2 register limit of `63.75`, optionally adjusts around global impacted prefetch, rounds to quarter-line units, and computes `Tpre_rounded`. It then tries four bandwidth cases:

- Case 1: VM plus two row fetches plus swath bytes share the whole prefetch interval.
- Case 2: VM plus swath bytes share time after two row-trip latencies.
- Case 3: two row fetches plus swath bytes share time after VM latency.
- Case 4: only swath bytes use the time left after VM and two row latencies.

Cases 1 to 3 are accepted only if their derived VM and row transfer times land on the expected side of the rounded latency constraints. The selected `prefetch_bw_equ` is raised by VM and row register-limit lower bounds. `Tvm_equ` and `Tr0_equ` are then derived from the selected bandwidth and feature presence.

The function chooses the more stressful schedule by comparing `dst_y_prefetch_oto` and `dst_y_prefetch_equ`. For OTO it writes OTO VM/row times and line counts. For EQU it writes equalized times, may promote `dst_y_prefetch` to the impacted value, and updates `RequiredPrefetchBWMax` so mode support and mode programming do not disagree when a later path chooses a different schedule. It then derives lines available for pixel prefetch (`Lsw`), cursor prefetch bandwidth, swath prefetch time, prefetch ratios, and luma/chroma prefetch data bandwidth. Any impossible timing, invalid row/VM line count, insufficient `Lsw`, or zero equalized bandwidth sets `NoTimeToPrefetch` and resets the outputs to zero.

`CheckGlobalPrefetchAdmissibility()` is called only after per-plane prefetch succeeds, only for multi-plane configurations, and only when the compile-time global check is enabled. Its output can force one more pass through the `dml_core_ms_prefetch_check()` do/while loop: `impacted_dst_y_pre[]` is fed back into `CalculatePrefetchSchedule()`, `s->recalc_prefetch_done` prevents repeated recalculation, and `s->recalc_prefetch_schedule` drives the loop condition.

`dml_core_ms_prefetch_check()` performs the following sequence:

1. Set `TimeCalc` from deep-sleep DCFCLK and derive HostVM inefficiency factors.
2. Iterate active planes to count 3DLUT use and call `calculate_tdlut_setting()`.
3. Compute extra latency from QoS, ROB, request size, DPTE groups, 3DLUT bytes, HostVM/GPUVM, page sizes, and return bandwidth.
4. Clear impacted prefetch inputs and enter the optional recalculation loop.
5. For each plane, populate a `struct dml2_core_internal_DmlPipe`, assemble `CalculatePrefetchSchedule_params`, call `CalculatePrefetchSchedule()`, and fold each plane's result into `ms.support.PrefetchSupported`.
6. Recompute DCFCLK deep sleep with 3DLUT delivery and prefetch swath time.
7. Enforce register/timing limits: `dst_y_prefetch >= 2`, `LinesForVM < 32`, `LinesForDPTERow < 16`, no per-plane prefetch failure, and `DSTYAfterScaler <= 8`.
8. Validate dynamic metadata and prefetch ratios.
9. If prefetch still passes, compute prefetch urgent burst factors, urgent bandwidth requirements without flip, urgent bandwidth support, optional global prefetch admissibility, and then immediate flip bandwidth/schedule/support.
10. Build `mSOCParameters`, call watermark/clock-change support, calculate p-state keepout destination lines, and return to the main mode-support pass.

`dml_core_mode_support()` is a single-state evaluator keyed by `in_out_params->min_clk_index`. Its high-level order is:

1. Clear scratch and `mode_lib->ms`, set plane count, output BPPs, and clock/bandwidth fields from `min_clk_table`.
2. Select DCN4x QoS parameter and active UCLK DPM indexes.
3. Compute max DET/compressed buffer capacity and progressive-to-interlace adjusted backend clocks.
4. Run scale/taps, source-format/rotation, byte/block-size, vactive bandwidth, cursor bandwidth, writeback bandwidth/latency, writeback scaler, viewport, pitch, and surface bounds checks.
5. Run a single-DPP swath/DET pass to learn whether each viewport can fit in one pipe.
6. Determine DSC slices, ODM mode with and without DSC, output link requirements, pipe allocation, DPP/OPP totals, DISPCLK/DPPCLK requirements, and output resource limits.
7. Validate link policy, DSC clocks/units/slices, DTBCLK, DP/MSO lane constraints, and DSC/ODM slice alignment.
8. Re-run swath/DET with final DPP and ODM decisions.
9. Calculate MALL surface size, DCC active DPP count, VM/PTE/meta row geometry, PTE/DCC meta buffer support, and p-state bytes to fetch.
10. Calculate urgent latency, trip-to-memory, cursor and surface urgent burst factors, deep-sleep DCFCLK, writeback delay, VStartup limits, MALL/p-state combination validity, outstanding request latency support, MCache/MALL overhead factors, bandwidth availability, average bandwidth support, and urgent latency hiding support.
11. Invoke `dml_core_ms_prefetch_check()`.
12. Check ROB support, compute informative vactive DET fill delay, evaluate the final large conjunction of support flags, and mirror selected outputs into `ms.support`.

The final `ModeSupport` condition is intentionally strict. It requires all major support flags to be true and all disqualifying flags to be false, including scale/taps, source format/scan, viewport size, link/DSC/resource constraints, MALL combinations, ROB, outstanding requests, clocks, writeback, cursor, pitch, prefetch, average bandwidth, dynamic metadata, PTE/DCC meta buffers, MALL size, G6 temp read, and immediate flip support when HostVM or immediate flip is required.

## State And Persistence Behavior

This code uses persistent state only within the DML mode-support object; it does not allocate kernel memory, acquire locks, issue MMIO, program hardware, or persist state outside the caller-provided structures.

`dml_core_mode_support()` begins with:

- `memset(&mode_lib->scratch, 0, sizeof(...))`
- `memset(&mode_lib->ms, 0, sizeof(...))`

That makes every invocation a fresh calculation pass. Outputs persist in `mode_lib->ms` after the function returns, and `dml2_core_calcs_mode_support_ex()` copies `mode_lib->ms.support` out only when the mode is supported. If the mode is unsupported, the caller can still inspect `mode_lib->ms` and debug logs, but `out_evaluation_info` is not refreshed by the wrapper.

Scratch-local structures store large temporary arrays and parameter blocks:

- `dml_core_mode_support_locals` holds intermediate arrays such as scaler delay, line times, swath bytes, VM page dimensions, metadata row heights, p-state byte requirements, dummy arrays, output BPPs, and MALL/p-state booleans.
- `CalculatePrefetchSchedule_params`, `calculate_peak_bandwidth_params`, `CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport_params`, `CalculateVMRowAndSwath_params`, and related structs are reused and overwritten during the pass.
- Many helper outputs are direct pointers into `mode_lib->ms` arrays, so prefetch, bandwidth, flip, watermark, and support state is accumulated in place.

Important persistent fields produced in this chunk include:

- Clock state: `SOCCLK`, `DCFCLK`, `FabricClock`, `MaxDCFCLK`, `MaxFabricClock`, `RequiredDISPCLK`, `RequiredDPPCLK[]`, `GlobalDPPCLK`, `dcfclk_deepsleep`, `uclk_freq_mhz`, `dram_bw_mbps`, `max_dram_bw_mbps`, `qos_param_index`, and `active_min_uclk_dpm_index`.
- Plane allocation: `ODMMode[]`, `MPCCombine[]`, `NoOfDPP[]`, `NoOfOPP[]`, DPP/OPP totals, DSC/FEC requirements, DSC slice counts, output BPP/type/rate/slots, and output support mirrors in `ms.support`.
- Geometry and memory model: swath widths/heights, DET buffer sizes, compressed buffer size, MALL surface size, VM bytes, DPTE row bytes/heights, meta row bytes/heights, request sizes, PTE/DCC meta buffer support, and MCache/MALL overhead factors.
- Timing and bandwidth: vactive bandwidths, cursor bandwidths, urgent burst factors, urgent/average bandwidth availability and requirements, prefetch bandwidths, VM-row bandwidth, immediate flip bandwidth, p-state vactive fill delays, watermarks, VActive latency hiding, and keepout-related support.
- Support booleans: the final `ModeSupport` and all intermediate flags that explain why a configuration failed.

The only file-scope mutable object visible in the chunk is `core_dcn4_g6_temp_read_blackout_table`, a static table of UCLK thresholds and blackout times. It is read by `get_g6_temp_read_blackout_us()` unless SoC bounding-box overrides are present.

## Dependencies And Integration Points

This chunk depends on the DML2 DCN4 calculation ecosystem:

- `struct dml2_core_internal_display_mode_lib` provides the IP block (`ip`), SoC bounding box (`soc`), mode-support workspace (`ms`), and scratch storage.
- `struct dml2_display_cfg` supplies stream descriptors, plane descriptors, output settings, DCC/GPUVM/HostVM flags, MALL/p-state overrides, scaler parameters, cursor parameters, writeback state, viewport/surface geometry, timing, and display-level overrides.
- `struct dml2_mcg_min_clock_table`, `struct dml2_soc_state_table`, `struct dml2_dram_params`, and DCN4x QoS structs provide clock, bandwidth, DRAM, and latency tables.
- `struct core_display_cfg_support_info` receives the final support report.
- Enumerations such as `dml2_core_internal_soc_state_type`, `dml2_core_internal_bw_type`, `dml2_source_format_class`, `dml2_rotation_angle`, `dml2_uclk_pstate_change_strategy`, `dml2_refresh_from_mall_mode_override`, `dml2_odm_mode`, `dml2_output_encoder`, and `dml2_qos_param_type` control most branches.

Important helper dependencies defined elsewhere in the same file or nearby DML2 sources include:

- Prefetch and timing: `CalculatePrefetchSchedule()`, `CalculateExtraLatency()`, `CalculateTWait()`, `CalculateMaxVStartup()`, `CalculateDCFCLKDeepSleep()`, `CalculateDCFCLKDeepSleepTdlut()`, `CalculateUrgentLatency()`, and `CalculateTripToMemory()`.
- Geometry/memory layout: `CalculateMaxDETAndMinCompressedBufferSize()`, `CalculateBytePerPixelAndBlockSizes()`, `CalculateSwathAndDETConfiguration()`, `CalculateVMRowAndSwath()`, `CalculateSurfaceSizeInMall()`, `calculate_tdlut_setting()`, and `calculate_mcache_setting()`.
- Bandwidth and burst factors: `calculate_bandwidth_available()`, `calculate_avg_bandwidth_required()`, `get_urgent_bandwidth_required()`, `CalculateUrgentBurstFactor()`, `calculate_cursor_req_attributes()`, `calculate_cursor_urgent_burst_factor()`, and `calculate_mall_bw_overhead_factor()`.
- Link/output: `get_stream_output_bpp()`, `PixelClockAdjustmentForProgressiveToInterlaceUnit()`, `CalculateSinglePipeDPPCLKAndSCLThroughput()`, `CalculateODMMode()`, `CalculateOutputLink()`, `RequiredDTBCLK()`, `DSCDelayRequirement()`, `CalculateWriteBackDISPCLK()`, and `CalculateWriteBackDelay()`.

Compile-time integration points matter:

- `__DML_VBA_DEBUG__` enables extensive verbose traces and failure details.
- `DML_GLOBAL_PREFETCH_CHECK` enables aggregate prefetch impact calculation and the prefetch recalculation loop.
- `DML_MODE_SUPPORT_USE_DPM_DRAM_BW` switches whether the second bandwidth availability calculation uses current DPM DRAM bandwidth or max DRAM bandwidth.

The runtime integration point is the AMD display mode validation path. The caller prepares `dml2_core_calcs_mode_support_ex` with a populated `mode_lib`, display config, min clock table, and clock index. This chunk evaluates the config and returns whether the DCN4 model supports it. Later mapping/programming code can consume `out_evaluation_info` and the calculated `mode_lib->ms` state to choose clocks, watermarks, DPP/ODM/DSC setup, MALL usage, prefetch values, and immediate-flip programming.

## Risks And Edge Cases

Several helpers divide by clock, bandwidth, line-time, or byte-rate values that are assumed valid. Zero or stale values in DCFCLK, FCLK, UCLK, DRAM bandwidth, return bus width, urgent bandwidth availability, line time, `VRatio`, `VRatioChroma`, swath dimensions, or surface read bandwidth can produce invalid calculations or assertions. The mode-support path expects min clock tables and display descriptors to be fully initialized before entry.

The prefetch scheduler is very sensitive to rounding. VM, row, prefetch, and register fields are quantized to quarter-line units and capped by U6.2-style limits (`dst_y_prefetch < 64`, `LinesForVM < 32`, `LinesForDPTERow < 16`). Small changes in `VStartup`, scaler delay, extra latency, DCC/MRQ, 3DLUT bytes, or HostVM inefficiency can flip a mode from supported to unsupported.

The equalized schedule selects among four bandwidth cases by comparing derived VM/row transfer times with rounded latency constraints. This branch is non-obvious and high-risk for regressions because the selected case changes both required prefetch bandwidth and the VM/row line allocation. The code also carries `RequiredPrefetchBWMax` even when OTO is not selected to avoid mode-support versus mode-programming mismatches; removing or weakening that propagation can create cross-stage disagreement.

3DLUT and MRQ support are interwoven with GPUVM and DCC. 3DLUT adds PTE bytes, row bytes, drain-time constraints, and DCFCLK deep-sleep delivery. MRQ/DCC influences row timing, metadata bytes, immediate-flip no-bandwidth behavior, and p-state bytes. Modes with GPUVM, HostVM, DCC, MRQ, dynamic metadata, and 3DLUT active together are especially sensitive.

`find_max_impact_plane()` has a notable edge case: if the maximum-impact plane index is `0`, the `if (max_idx <= 0)` branch resets the result to `this_plane_idx` after asserting `max_idx >= 0`. That means plane 0 can be ignored as the impacting plane for other planes in this helper. This may be intentional due to a historical assumption, but it is a risk area for global prefetch correctness.

`get_qos_param_index()` returns `i - 1` for nonzero threshold positions and stops at the first threshold greater than the UCLK or zero. Badly ordered or missing `minimum_uclk_khz` entries can select the wrong QoS bucket. `get_active_min_uclk_dpm_index()` asserts if the selected UCLK is not found exactly in the SoC clock table, so alternate DRAM bandwidth conversion paths must still keep UCLK tables coherent.

`uclk_khz_to_dram_bw_mbps()` with alternate clock conversion uses the first table entry whose `min_uclk_khz >= uclk_khz`; if no entry matches, `bw_mbps` remains zero and asserts. The direction of the comparison and table ordering are therefore part of the contract.

HostVM inefficiency can be amplified to 4x for prefetch when remote IOMMU outstanding translations are below maximum requests. That protects bandwidth modeling, but it can make prefetch support fail abruptly when HostVM/GPUVM configuration or request-count tables change.

Immediate flip support depends on both timing and bandwidth models. `CalculateFlipSchedule()` may output lower-bound flip bandwidth in mode support without calculating actual `dst_y_per_vm_flip` and `dst_y_per_row_flip` values (`use_lb_flip_bw` sets them to 1 as unused). Later paths using actual flip line programming must stay aligned with this support model to avoid accepting modes that cannot program flip safely.

MALL and p-state combinations are constrained by several disqualifying booleans: immediate flip or HostVM with full-frame MALL/phantom pipe, refresh-from-MALL mixed with static screen modes, SubVP without matching phantom pipe, SubVP combined with full-frame MALL, and SubVP refresh above 120 Hz when implicit PMO is disabled. These policy constraints can reject otherwise bandwidth-valid modes.

Outstanding-request support in DCN4x compares modeled outstanding latency from request size and return bus width against average urgent and non-urgent latency. Incorrect request-size selection from swath/DET configuration, especially with chroma or MRQ, can incorrectly fail `OutstandingRequestsSupport` or `OutstandingRequestsUrgencyAvoidance`.

The final mode-support predicate is a large conjunction. A new feature that sets a support flag but forgets to include it in the final predicate, or a new failure flag that is not reset before use, can cause false positives or false negatives. Conversely, because `mode_lib->ms` is zeroed at function entry, any required flag not explicitly set to true will fail if included in the predicate.

## Test Signals

Useful test coverage should exercise both the final mode-support result and intermediate support flags:

- Baseline supported modes across simple RGB, 4:2:0, 4:2:2, RGBE-alpha, DCC-on/off, GPUVM-on/off, HostVM-on/off, MRQ-on/off, and single-plane/multi-plane configurations.
- Prefetch boundary tests with low VBlank/VStartup, high scaler delay, interlace/progressive-to-interlace, dynamic metadata, 3DLUT, high page-table levels, small HostVM page sizes, and high urgent/trip-to-memory latency. Debug traces should show `dst_y_prefetch`, `LinesForVM`, `LinesForDPTERow`, `VRatioPreY/C`, `RequiredPrefetchBWMax`, `NoTimeForPrefetch`, and `NoTimeForDynamicMetadata`.
- Global prefetch tests under `DML_GLOBAL_PREFETCH_CHECK` with at least two active planes and asymmetric detile/swath sizes. Watch `impacted_dst_y_pre[]`, `recalc_prefetch_schedule`, and whether the second prefetch pass converges.
- Immediate flip cases with no flip, one flip plane, multiple flip planes, GPUVM-only, DCC/MRQ-only, and GPUVM plus DCC/MRQ. Validate `final_flip_bw[]`, `ImmediateFlipSupportedForPipe[]`, `ImmediateFlipSupport`, and flip-inclusive urgent bandwidth tables.
- Bandwidth support tests near SDP and DRAM limits, with MALL disabled and enabled, to distinguish `AvgBandwidthSupport`, `UrgVactiveBandwidthSupport`, `PrefetchBandwidthSupported`, and flip bandwidth support.
- Clock/resource tests around max DISPCLK, DPPCLK, DSCCLK, DTBCLK, DPP/OPP/DSC/OTG/writeback/DP2/HDMI-FRL resource limits, DSC slice overrides, and ODM 2:1/3:1/4:1 alignment.
- MALL and p-state policy tests for SubVP main/phantom pairing, full-frame MALL, refresh-from-MALL overrides, HostVM, immediate flip, all-streams-blanked, forced vactive/vblank/DRR/MALL p-state strategies, and high-refresh SubVP.
- G6 temperature-read tests where SoC bounding-box blackout overrides are present versus absent, with UCLK values below, between, and above internal table thresholds.
- QoS/clock-table robustness tests for exact UCLK DPM matching, alternate DRAM bandwidth conversion, DCN3 versus DCN4x QoS types, and min clock table entries with `min_uclk_khz == 0`.
- Failure diagnostics under `__DML_VBA_DEBUG__`; unsupported modes should produce enough logs from `dml2_print_mode_support_info()` and surrounding verbose statements to identify the failing support bit.

Hardware-facing symptoms of model regressions include unexpected mode rejection, accepting a mode that underflows during prefetch, flip glitches, black screen on high-bandwidth or DSC/ODM modes, incorrect DRAM/FCLK p-state change behavior, MALL/SubVP policy mis-selection, stutter or Z8 residency regressions, and mismatched mode-support versus mode-programming prefetch bandwidth.

## Cross-Chunk Notes

This chunk starts in the middle of `CalculatePrefetchSchedule()`. The earlier part of the same function, including its signature, local setup, dynamic metadata timing, setup-time calculation, and initial VM/row trip derivation, must be merged from the previous chunk for a complete per-file report.

This chunk also ends immediately after the `CalculatePixelDeliveryTimes()` signature begins. The body of that function and later display-configuration/programming calculations are outside this chunk and should be covered by the next chunk.

The final per-file synthesis should connect this chunk with earlier DCN4 helper definitions and later programming-output calculations. In particular, the merge should preserve the full data flow from `dml2_core_calcs_mode_support_ex()` through `dml_core_mode_support()`, `dml_core_ms_prefetch_check()`, and the later routines that consume `core_display_cfg_support_info` for actual DML output fields.

### subset-b-001428: lines 9673-13402

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4_calcs.c lines 9673-13402

## Scope And Purpose

This chunk is the DCN4 DML2 mode-programming and register-export tail of `dml2_core_dcn4_calcs.c`. It begins at the body of `CalculatePixelDeliveryTimes()`, then defines timing helpers for meta/PTE/VM scheduling, stutter-efficiency modeling, the large `dml_core_mode_programming()` pass, and the public accessors that translate the calculated model state into DCHUBBUB/DLG/RQ/TTU/ARB/FAMS2 programming and informative reporting.

The code is modeling and register-preparation logic, not direct hardware programming. It consumes a validated display configuration, selected clocks, SOC/IP capability tables, and mode-support results, then fills `mode_lib->mp` (`struct dml2_core_internal_mode_program`) with per-plane and global programming-derived quantities. Later exported helpers read that persistent model state to populate structures used by display core programming or diagnostics.

Major responsibilities in this chunk are:

- Calculate display-pipe line/request delivery times for luma and chroma in active and prefetch phases.
- Convert DCC meta rows, pixel PTE rows, TDLUT groups, and VM groups into nominal, vblank, and immediate-flip time budgets.
- Build the selected-mode programming state, including swath/DET, MALL/mcache, GPUVM/DCC metadata, prefetch, immediate flip, watermarks, delivery timings, VM/meta timings, VStartup, writeback bandwidth, stutter efficiency, and deep-sleep hysteresis.
- Export watermarks, arbiter registers, per-pipe DLG/RQ/TTU registers, sync programming, FAMS2 programming, mcache/MALL allocation, plane/stream support details, and the large `informative` result block.

## Important APIs, Types, And Functions

`CalculatePixelDeliveryTimes()` writes `DisplayPipeLineDeliveryTime*[]` and `DisplayPipeRequestDeliveryTime*[]` arrays. For each plane it uses scaler ratios, swath-width upper bounds, DPP count, pixel clock, PSCL throughput, DPP clock, bytes-per-pixel, and request counts. If the relevant vertical ratio is at or below 1.0 it models delivery through output pixel timing; otherwise it models delivery through scaler throughput and DPP clock. Chroma arrays are zeroed when `BytePerPixelC[k] == 0`.

`CalculateMetaAndPTETimes()` accepts a `struct dml2_core_shared_CalculateMetaAndPTETimes_params`. It derives:

- `DST_Y_PER_PTE_ROW_NOM_L/C[]` and `DST_Y_PER_META_ROW_NOM_L/C[]`.
- DCC meta chunk timing for nominal, vblank, and flip phases when DCC and MRQ are enabled.
- TDLUT group time when a plane is configured for TDLUT.
- PTE group timing for nominal, vblank, and flip phases when GPUVM is enabled.

This helper depends heavily on rotation, row heights, meta chunk sizes, PTE request geometry, `use_one_row_for_frame[]`, and `dst_y_per_row_*[]` outputs from prefetch/flip scheduling.

`CalculateVMGroupAndRequestTimes()` computes `TimePerVMGroupVBlank[]`, `TimePerVMGroupFlip[]`, `TimePerVMRequestVBlank[]`, and `TimePerVMRequestFlip[]`. It counts lower-level VM groups and 64-byte requests from DPDE0 bytes, DCC meta PTE bytes, and TDLUT PTE bytes. The result is a per-plane time slice over `dst_y_per_vm_vblank` or `dst_y_per_vm_flip`. GPUVM disabled produces zeros.

`CalculateStutterEfficiency()` models compressed-buffer, ROB, DET, DCC, zero-size request, row-bandwidth, and stutter burst behavior. It finds the critical non-phantom surface with the shortest luma DET buffering time, computes stutter/Z8 efficiencies with and without vblank, counts bursts per frame, and sets `DCHUBBUB_ARB_CSTATE_MAX_CAP_MODE`.

`dml_core_mode_programming()` is the central internal pass. It takes `struct dml2_core_calcs_mode_programming_ex`, zeros scratch and `mode_lib->mp`, loads selected clocks from `programming->min_clocks`, maps pipes to planes from `cfg_support_info`, and runs the selected-mode calculations. It returns `mode_lib->mp.PrefetchAndImmediateFlipSupported`.

`dml2_core_calcs_mode_programming_ex()` is the public wrapper around `dml_core_mode_programming()`.

`dml2_core_calcs_get_dpte_row_height()` is a standalone exported helper. It recalculates bytes-per-pixel and block geometry for a supplied format/tiling/rotation/pitch, populates only enough `calculate_vm_and_row_bytes_params` scratch state to call `CalculateVMAndRowBytes()`, and returns the requested luma or chroma DPTE row height.

`is_dual_plane()` classifies 4:2:0 formats and `dml2_rgbe_alpha` as dual-plane. `dml_get_plane_idx()` resolves a pipe index through `mode_lib->mp.pipe_plane[]`.

`rq_dlg_get_wm_regs()`, `rq_dlg_get_rq_reg()`, `rq_dlg_get_dlg_reg()`, and `rq_dlg_get_arb_params()` convert modeled timings and limits into DCHUBBUB/DLG/RQ/TTU/ARB register structures. Public wrappers expose these through `dml2_core_calcs_get_watermarks()`, `dml2_core_calcs_get_arb_params()`, and `dml2_core_calcs_get_pipe_regs()`.

`dml2_core_calcs_get_global_sync_programming()` and `dml2_core_calcs_get_stream_programming()` expose VReady/VStartup/VUpdate and p-state keepout timing.

`dml2_core_calcs_get_global_fams2_programming()` and `dml2_core_calcs_get_stream_fams2_programming()` populate DMUB FAMS2 global and per-stream command structures from stage-3 p-state metadata, DML core watermarks, IP FAMS2 capabilities, and selected p-state method.

`dml2_core_calcs_get_mcache_allocation()`, `dml2_core_calcs_get_mall_allocation()`, `dml2_core_calcs_get_plane_support_info()`, `dml2_core_calcs_get_stream_support_info()`, and `dml2_core_calcs_get_informative()` are readout helpers for allocation, support, and diagnostic data.

## Control Flow

The chunk starts with the active body of `CalculatePixelDeliveryTimes()`. The first loop computes line delivery times for each active surface. Luma and chroma use active scaler ratios, while prefetch luma/chroma use `VRatioPrefetchY/C[]`. The second loop divides those line delivery times by request counts to get per-request delivery times.

`CalculateMetaAndPTETimes()` runs in four conceptual phases. First, it computes nominal destination lines per PTE/meta row from row height divided by scaler vertical ratio. Second, for DCC+MRQ planes it computes luma/chroma meta chunks per row, using rotation to choose width versus height request thresholds, and converts row-line windows into time per meta chunk for nominal, vblank, and flip. Third, it computes optional TDLUT group timing. Fourth, when GPUVM is enabled, it computes luma/chroma DPTE group widths, groups per row, applies the small-group `+1` adjustment when groups are at most 2, and converts nominal/vblank/flip row windows to PTE group times. GPUVM disabled or missing chroma zeros the corresponding outputs.

`CalculateVMGroupAndRequestTimes()` walks planes and accumulates lower-VM-stage group/request counts. For page-table levels >= 2 it counts luma and chroma DPDE0 groups. For DCC+MRQ it adds meta PTE groups and one or two MPDE0 groups depending on chroma. TDLUT contributes extra prefetch-only groups and requests, plus a TDPE0 group for multi-level GPUVM. Time outputs are line-window time divided by group or request counts, and are halved when `gpuvm_max_page_table_levels > 2`.

`CalculateStutterEfficiency()` first computes aggregate compressed read bandwidth, zero-size bandwidth, and row bandwidth across non-phantom planes. DCC planes clamp effective luma/chroma compression to 2x or 4x depending on block geometry, swath height, rotation, and max uncompressed block. It then computes average DCC compression and zero-size fraction, derives effective compressed-buffer capacity across compressed buffer, meta FIFO, zero-size buffer, and ROB, and finds the critical surface by minimum luma DET buffering time. With that critical period it computes the burst time needed to refill compressed/ROB/DET and row data, checks whether active writeback disables stutter, computes SR and Z8 efficiencies, adjusts for synchronized same-timing streams when applicable, and sets the C-state max-cap mode flag.

`dml_core_mode_programming()` performs the selected-mode pipeline in a mostly linear sequence:

1. Clear scratch and `mode_lib->mp`, count active planes/pipes, map pipes to planes, load selected active clocks, derive DRAM bandwidth and QoS indices, and map support ODM data to `mode_lib->mp.ODMMode[]`.
2. Copy per-plane DPP and DPPCLK/DSCCLK values, assert required clocks are positive, then calculate maximum DET, nominal DET, compressed-buffer minimum, p-to-i pixel clocks, scaler throughput, bytes-per-pixel/block sizes, swath widths, cursor bandwidth, and active swath bandwidth.
3. Call `CalculateSwathAndDETConfiguration()` to compute swath heights, request sizes, DET allocation, unbounded-request state, compressed-buffer size, and viewport support placeholders for this selected configuration.
4. Compute DSC delay and MALL surface size, build `SurfaceParameters[]`, and call `CalculateVMRowAndSwath()` to populate DPTE, VM, PTE, meta-row, row-bandwidth, PTE-buffer mode, and one-row-for-frame data.
5. Configure mcache and MALL bandwidth overhead when MALL is allocated and MRQ is not present; otherwise default overhead factors to 1.0.
6. Calculate available bandwidth, HostVM inefficiency factors, active DPP counts, TDLUT settings, extra latency, writeback delay, vactive bytes required to hide UCLK p-state latency, excess vactive fill bandwidth, urgent/trip/meta-trip latencies, line-buffer source lines, cursor urgent factors, normal urgent burst factors, and maximum VStartup lines.
7. For multi-plane modes, run `CheckGlobalPrefetchAdmissibility()` to estimate impacted prefetch lines. Then run a single prefetch scheduling pass over every plane, filling `DSTX/YAfterScaler`, destination prefetch windows, `VRatioPrefetch*`, required prefetch bandwidths, dynamic metadata timing, VUpdate/VReady offsets, TDLUT/cursor prefetch terms, and impacted prefetch margin.
8. Reject prefetch support if any plane has no time to prefetch, dynamic metadata cannot fit, `DSTYAfterScaler > 8`, destination prefetch lines under 2, prefetch VRatio above `__DML2_CALCS_MAX_VRATIO_PRE__`, or urgent latency hiding failures. If the schedule is still valid, compute prefetch urgent burst factors, peak bandwidth requirements, and call `check_urgent_bandwidth_support()`.
9. If prefetch is valid, compute immediate-flip bandwidth availability and flip bytes, run `CalculateFlipSchedule()` per plane, recompute peak bandwidth with flip bandwidth included, and call `calculate_immediate_flip_bandwidth_support()`. Per-pipe immediate-flip failures clear global immediate-flip support.
10. Combine prefetch and immediate-flip support. Immediate flip is mandatory when HostVM is enabled or any plane explicitly requests immediate flip.
11. If the combined support flag is true, compute DCC configuration, watermarks and p-state change support, writeback p-state end positions, p-state keepout lines, pixel delivery times, meta/PTE times, VM group/request times, VStartup placement, writeback bandwidth, total data read bandwidth, and stutter efficiency.
12. Always finish by computing minimum return latency in DCFCLK cycles and DCFCLK deep-sleep hysteresis, then return `PrefetchAndImmediateFlipSupported`.

The register-export path is separate from the modeling pass. `dml2_core_calcs_get_pipe_regs()` first fills RQ registers, then DLG/TTU registers, then DET segment size. Those calculations read `mode_lib->mp` data produced by successful mode programming.

`rq_dlg_get_rq_reg()` maps chunk sizes, min chunk sizes, meta chunk sizes, DPTE/MPTE group sizes, linear PTE row height, swath height, expansion modes, unbounded request, and dual-plane DET plane1 base address. The dual-plane DET split mirrors modeled luma/chroma stored swath ratio: phantom pipes split a fixed 1 MB DET region in half; non-phantom dual-plane pipes split half/half unless luma stored swath bytes exceed chroma by more than 1.5x, in which case plane1 starts after a 2/3 luma allocation rounded to 1 KB.

`rq_dlg_get_dlg_reg()` resolves timing, pipe/plane/ODM position, refclk-to-pixel-clock scaling, prefetch destination windows, VM/PTE/meta timing, delivery timing, dynamic metadata timing, and TTU request delivery. It writes fixed-point register encodings, applies saturation to some 23-bit VM/PTE fields, and asserts expected register ranges for scaler offsets, delivery times, TTU fields, and vblank timing.

`dml2_core_calcs_get_informative()` is a large state-copy function. It copies mode-support booleans and per-plane support data from `mode_lib->ms.support`, watermarks and QoS metrics from accessor helpers, aggregate MALL/DPP totals, power-management/stutter values, CRB and miscellaneous model fields, per-plane DPTE/meta/swath/delivery/VM/prefetch/DCC data from `mode_lib->mp`, non-optimized mcache allocation, and a derived ROB urgency-avoidance flag.

## State And Persistence Behavior

`dml_core_mode_programming()` explicitly resets `mode_lib->scratch` and `mode_lib->mp` at entry. Scratch is temporary workspace for large local arrays and parameter structs; `mode_lib->mp` is the persistent result for the selected programming pass. Public getters later rely on this persistent `mp` state, so callers must run mode programming before requesting registers or informative data.

The selected clock state is persisted in `mode_lib->mp.Dcfclk`, `FabricClock`, `dram_bw_mbps`, `uclk_freq_mhz`, `GlobalDPPCLK`, `Dppclk[]`, `DSCCLK[]`, `Dispclk`, and `DCFCLKDeepSleep`. These values are treated as already selected by upstream support/min-clock logic and are asserted to be positive.

Per-plane model state persists in arrays under `mode_lib->mp`: swath widths/heights, DET sizes, DCC block settings, MALL and mcache allocation, DPTE/PTE/meta row geometry, VM/PTE/meta timing, prefetch schedule terms, delivery times, VStartup/VUpdate/VReady values, urgent burst factors, support flags, row bandwidth, total bandwidth, and stutter metrics. Many arrays are indexed by plane, while pipe-level register export maps pipe to plane through `mp.pipe_plane[]`.

`CalculateStutterEfficiency()` uses `scratch->CalculateStutterEfficiency_locals` and zeroes it at entry. It only persists results through output pointers into `mode_lib->mp`.

`dml2_core_calcs_get_dpte_row_height()` mutates `mode_lib->scratch.calculate_vm_and_row_bytes_params` and uses a stack `dummy_integer[]` for unneeded outputs. It does not update `mode_lib->mp`, but it does reuse the shared scratch object, so it is not thread-independent from other DML calculations on the same `mode_lib`.

Export helpers mostly write caller-provided output structures. `rq_dlg_get_dlg_reg()` uses `mode_lib->scratch.rq_dlg_get_dlg_reg_locals` as temporary workspace and zeroes that local block at entry. The helpers do not allocate memory, take locks, or retain pointers into output structures.

`dml2_core_calcs_get_informative()` assumes `out->display_config` is already populated, because it iterates `out->display_config.num_planes` and reads `out->display_config.plane_descriptors->overrides.reserved_vblank_time_ns` when deriving `PrefetchMode[]`. It then fills only the informative/min-clock fields.

## Dependencies And Integration Points

This chunk depends on the surrounding DML2 DCN4 internal data model:

- `struct dml2_core_calcs_mode_programming_ex` supplies the input display config, selected min-clock table/index, support info, mode library, and output programming object.
- `struct dml2_core_internal_display_mode_lib` provides `ip`, `ip_caps`, `soc`, `ms`, `mp`, and `scratch` state.
- `struct dml2_display_cfg`, `struct dml2_plane_parameters`, `struct dml2_stream_parameters`, `struct core_display_cfg_support_info`, and the programming/output register structs define the public inputs and outputs.
- Helper structs in `mode_lib->scratch` carry parameters for `CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport()`, `CalculateVMRowAndSwath()`, `CalculateSwathAndDETConfiguration()`, `CalculateStutterEfficiency()`, `CalculatePrefetchSchedule()`, `CheckGlobalPrefetchAdmissibility()`, `calculate_mcache_setting()`, `calculate_tdlut_setting()`, `CalculateMetaAndPTETimes()`, peak-bandwidth calculation, and vactive latency hiding.
- Enumerations such as `dml2_source_format_class`, `dml2_swizzle_mode`, `dml2_rotation_angle`, `dml2_odm_mode`, `dml2_qos_param_type`, `dml2_pstate_method`, internal output type/rate enums, and DMUB FAMS2 stream types drive branch behavior.
- Math/logging/assert helpers such as `math_ceil2`, `math_floor2`, `math_min2`, `math_max2`, `math_pow`, `math_log2_approx`, `DML_ASSERT`, and `DML_LOG_VERBOSE` are used throughout.

The mode-programming path integrates with earlier code in the same file that performs mode support and min-clock selection. `dml_core_mode_programming()` reads support decisions such as DPP count, ODM segments, DSC enable/slices, selected output BPP, aligned pitch, and selected clocks; it does not re-solve those support choices.

The register getters integrate with DC programming layers outside this file. They provide DCHUB watermark registers, display arbiter registers, per-pipe RQ/DLG/TTU registers, global sync programming, stream programming, FAMS2 DMUB command payloads, MALL allocation, and mcache allocation.

The informative getter integrates with diagnostics and upper layers that need a human/queryable summary of why a mode is or is not supportable and what timing/bandwidth/watermark values were modeled.

## Risks And Edge Cases

Several calculations assume nonzero clocks, ratios, request counts, group sizes, and bandwidths. The code asserts key selected clocks but many divisions rely on upstream initialization of `pixel_clock_khz`, scaler ratios, `req_per_swath_ub_*`, `PTERequestSize*`, `tdlut_groups_per_2row_ub`, `vm_group_bytes`, and return bandwidth arrays.

`CalculateVMGroupAndRequestTimes()` does not reset `num_group_per_lower_vm_stage` and `num_req_per_lower_vm_stage` inside the per-plane loop. The counters are initialized before the loop and accumulate across planes, then each plane's time is divided by the cumulative count so far. If this is intentional, it models shared lower-stage VM pressure; if not, it makes later planes receive smaller per-group/request times than standalone per-plane counts would produce. This is a high-value area for trace comparison.

One chroma VM request count path adds `dpde0_bytes_per_frame_ub_c[k]` without dividing by 64, unlike the luma path and meta chroma path. If units are bytes, this can overcount chroma lower-stage requests by 64x. This may be inherited spreadsheet behavior, but it is a clear risk point.

Several places use `display_cfg->stream_descriptors[k]` instead of indexing through a plane's `stream_index`. In `CalculateStutterEfficiency()` the active writeback count uses `stream_descriptors[k]` inside a loop over planes after checking `stream_visited[plane.stream_index]`. This is only equivalent when plane index and stream index match; multi-plane-per-stream or reordered stream indexes could skew writeback detection.

In `dml_core_mode_programming()`, `SurfaceParameters[k].ViewportXStartC` is assigned from `composition.viewport.plane1.y_start`, and mcache chroma `vp_start_x_c` is also assigned from `plane1.y_start`. That may be a copy/paste bug if the intended source is `plane1.x_start`. It would affect rotated/chroma viewport VM/mcache calculations for dual-plane formats.

Immediate-flip support is forced when HostVM is enabled, even if no plane explicitly requests immediate flip. This is deliberate policy in the code, but it means HostVM modes can fail programming from flip bandwidth/schedule constraints that would otherwise be optional.

The single prefetch scheduling pass does not iterate VStartup choices. It sets each `VStartupMin[k]` to `MaxVStartupLines[k]`, then later uses max VStartup for positioning. If upstream support expected iterative search, this selected-mode programming path may only verify and program the max-VStartup solution.

Register conversion is sensitive to fixed-point scaling and truncation. `rq_dlg_get_dlg_reg()` floors line delivery values, multiplies request delivery by 2^10, line/destination values by 2^2, and ratios by 2^19. Several fields assert range, while VM/PTE group fields saturate. Differences between assert-and-clamp behavior can cause debug-only failures or silent max programming depending on field.

`dml2_core_calcs_get_informative()` computes `PrefetchMode[k]` from `out->display_config.plane_descriptors->overrides.reserved_vblank_time_ns` without indexing `[k]`. That means every plane appears to use plane 0's reserved vblank override for this informative field.

`rq_dlg_get_rq_reg()` treats `dml2_rgbe_alpha` as dual-plane and changes plane1 pixel chunk size to the alpha chunk size. Formats with chroma-like second planes and alpha planes share some paths but may have different hardware expectations.

The FAMS2 stream programming helper returns without touching output when `all_streams_blanked` is set. Callers need to ensure stale FAMS2 output memory is not reused when streams are blanked.

## Test Signals

Useful validation signals include:

- DML debug logs under `__DML_VBA_DEBUG__` for delivery times, PTE/meta/VM timings, prefetch support failures, immediate-flip support, VStartup placement, watermarks, stutter efficiency, DLG/RQ register values, and mcache allocation.
- Mode-programming return value from `dml2_core_calcs_mode_programming_ex()`, especially for cases where mode support succeeded but selected-mode prefetch or immediate flip fails.
- Per-pipe register dumps from `dml2_core_calcs_get_pipe_regs()`: `refcyc_per_*`, `dst_y_*`, `vratio_prefetch*`, RQ chunk/group sizes, DET size, and dual-plane `plane1_base_address`.
- Watermark register outputs from `dml2_core_calcs_get_watermarks()` compared against modeled `mode_lib->mp.Watermark` values and DCHUB refclk overrides.
- FAMS2 command payloads for vactive, vblank, DRR, SubVP, and blanked-stream scenarios.
- Informative fields for mode-support booleans, QoS bandwidth required/available, urgent fractions, stutter/Z8 efficiency, DPTE/meta row heights, delivery times, VM group/request times, DCC block controls, and lowest impacted prefetch margin.

High-risk scenario coverage should include:

- Single-plane and multi-plane configurations, including multiple planes sharing one stream and planes whose index differs from stream index.
- Chroma-less RGB, 4:2:0 dual-plane, and `dml2_rgbe_alpha` formats.
- GPUVM off/on, GPUVM page-table levels 1, 2, and greater than 2, HostVM on, and TDLUT on/off.
- DCC off/on with MRQ present and absent, including small meta chunks and rotated surfaces.
- Linear tiling with GPUVM enabled to exercise linear PTE row-height register programming.
- ODM bypass, 2:1, 3:1, 4:1, and MSO segment modes.
- Immediate flip not requested, explicitly requested, and implicitly required through HostVM.
- MALL unavailable, MALL available without MRQ, static-screen/SubVP cases, and mcache allocation paths.
- Writeback active versus inactive, because writeback affects delay, total bandwidth, p-state endpoints, and stutter eligibility.
- Interlaced timings with and without p-to-i support, because VStartup, frame time, and DLG vblank values are adjusted.

## Cross-Chunk Notes

Earlier chunks of this same source file define most helpers called by `dml_core_mode_programming()`: byte/block sizing, swath/DET allocation, VM row-byte calculation, MALL/mcache logic, available/required bandwidth calculations, prefetch scheduling, flip scheduling, watermarks, p-state keepout, latency helpers, and mode support. The merge lane should join this chunk with those earlier chunks so the final per-file report can describe the complete DCN4 calculation flow from mode-support selection through selected-mode programming and register export.
