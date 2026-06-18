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
