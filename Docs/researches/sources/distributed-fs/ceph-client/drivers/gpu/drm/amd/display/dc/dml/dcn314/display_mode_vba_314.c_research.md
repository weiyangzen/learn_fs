# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_mode_vba_314.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001413`: lines 1-6839, `Docs/researches/chunks/subset-b-001413_research.md`
- `subset-b-001414`: lines 6840-7367, `Docs/researches/chunks/subset-b-001414_research.md`

## Chunk Research

### subset-b-001413: lines 1-6839

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_mode_vba_314.c

Chunk: `subset-b-001413`
Covered source range: lines 1-6839 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_mode_vba_314.c`

## Purpose

This chunk contains the front and main body of the DCN 3.1.4 Display Mode Library VBA implementation. It is part of the AMD display driver model-validation path: callers populate `struct display_mode_lib`, then this code mutates `mode_lib->vba` with calculated pipe topology, clock requirements, bandwidth use, prefetch schedules, watermark values, power-management capability flags, DSC/link constraints, and the selected SoC voltage state.

The file explicitly notes that it is hardware-provided "HW gospel" and intentionally does not follow normal kernel style. Most logic is formula-oriented and depends on display hardware constants, SoC/IP caps, and per-plane timing/format inputs rather than conventional driver control structures.

The public entry points visible in this chunk are:

- `dml314_recalculate(struct display_mode_lib *mode_lib)`: runs the selected-mode calculation flow after mode support has been determined.
- `dml314_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)`: evaluates whether the requested display configuration can be supported across available voltage states and pipe-combine choices, then selects the operating state.
- `dml314_CalculateWriteBackDISPCLK(...)`: exported helper for writeback DISPCLK demand.

Most other functions are `static` helpers that implement DCN314-specific timing, memory, DCC, VM/PTE, prefetch, immediate-flip, watermark, and stutter-efficiency calculations.

## Important Types And Data

The central state object is `mode_lib->vba` (`struct vba_vars_st`, defined outside this chunk). The code treats it as a large mutable workspace. Inputs such as plane count, pixel clocks, ratios, formats, tiling, viewport sizes, cursor data, writeback parameters, SoC voltage-state tables, and feature-policy flags are read from `v`. Outputs are written back into arrays such as `ModeSupport`, `ValidationStatus`, `DPPPerPlane`, `MPCCombineEnable`, `ODMCombineEnabled`, `DCFCLK`, `ReturnBW`, `PrefetchModePerState`, `ImmediateFlipSupport`, watermark fields, stutter efficiency fields, and many per-plane timing arrays.

The local `Pipe` typedef is a compact snapshot passed into `CalculatePrefetchSchedule()`. It captures only the per-pipe values needed for schedule construction: DPP/DISP/pixel clocks, DCFCLK deep sleep, DPP count, scaler state, ratios, scan orientation, 256-byte block geometry, interlace/cursor/vblank/timing, DCC/ODM/format, bytes per pixel, and progressive-to-interlace state.

Key enums come from included DML/DC headers:

- `enum source_format_class` for source pixel formats such as 444, 420, RGBE, and mono formats.
- `enum output_format_class` and `enum output_encoder_class` for output format and link type.
- `enum dm_swizzle_mode` for tiling/swizzle.
- `enum odm_combine_mode`, `enum unbounded_requesting_policy`, `enum clock_change_support`, and validation status enums.

The chunk also defines DCN314 limits and tuning constants: `DCN314_MAX_DSC_IMAGE_WIDTH`, `DCN314_MAX_FMT_420_BUFFER_WIDTH`, minimum vstartup, ARB-to-RET delay, minimum DCFCLK factor, and sentinel BPP values.

## Major Functions

`dml314_recalculate()` is the high-level recalculation path. It calls `ModeSupportAndSystemConfiguration(mode_lib)`, `PixelClockAdjustmentForProgressiveToInterlaceUnit(mode_lib)`, `DisplayPipeConfiguration(mode_lib)`, and finally `DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation(mode_lib)`. The first two callees are external to this chunk; the latter two are defined here.

`dscceComputeDelay()` and `dscComputeDelay()` compute DSC pipeline delay. The former uses BPC, compressed BPP, slice width/count, output format, and encoder class to produce pixel delay through DSC compression, while the latter adds fixed DSCC/serializer/deserializer delays by output format. These are used both for current selected state and per-voltage-state support checks.

`CalculatePrefetchSchedule()` is one of the most important helpers. It computes scaler/output pipeline offsets, dynamic metadata setup deadlines, VM/PTE fetch time, row fetch time, available prefetch lines, prefetch bandwidth, prefetch V ratios, and required luma/chroma prefetch pixel bandwidth. It returns a boolean error flag and zeroes outputs on failure. It also enforces practical constraints such as positive prefetch pixel-data time, maximum prefetch ratios, vstartup budget, VM/PTE line counts, and dynamic metadata timing.

`CalculateVMAndRowBytes()` computes DCC metadata row bytes, GPU VM PDE/PTE bytes per frame, macro-tile dimensions, pixel PTE request geometry, PTE row byte counts, PTE buffer fit, and VM/DPTE grouping sizes. It accounts for DCC enable, linear versus tiled surfaces, scan direction, GPU VM, host VM, page-table levels, page sizes, PTE buffer request capacity, pitches, and chroma/luma separation.

`DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` computes the active selected-mode values after mode support has chosen `VoltageLevel` and `maxMpcComb`. It recalculates return bandwidth, DISPCLK/DPPCLK, read bandwidth, DCFCLK deep sleep, DSCCLK/DSC delay, VM/PTE bytes, prefetch scheduling, urgent burst factors, immediate flip, unbounded request/compressed-buffer size, watermarks, delivery times, VM/PTE timing groups, min TTU in vblank, DCC configuration, final vstartup adjustments, write bandwidth, and stutter efficiency.

`DisplayPipeConfiguration()` populates final per-plane swath heights and DET buffer split by calling `CalculateBytePerPixelAnd256BBlockSizes()` and `CalculateSwathAndDETConfiguration()` for the selected configuration.

`CalculateBytePerPixelAnd256BBlockSizes()` maps source format and tiling into byte-per-pixel values, DET byte-per-pixel values, and 256-byte block width/height for luma and chroma planes.

`CalculateTWait()` maps prefetch mode to the wait time that must cover DRAM clock change latency, urgent latency, and self-refresh entry/exit latency.

`dml314_CalculateWriteBackDISPCLK()` and `CalculateWriteBackDelay()` estimate writeback clock and latency needs from writeback ratios, taps, dimensions, line-buffer size, and timing.

`CalculateVupdateAndDynamicMetadataParameters()` computes vupdate/vready pixel offsets plus dynamic metadata transfer deadlines using DPPCLK, DISPCLK, DCFCLK deep sleep, pixel clock, vblank, interlace, and metadata byte/line requirements.

`CalculateRowBandwidth()`, `CalculatePixelDeliveryTimes()`, `CalculateMetaAndPTETimes()`, and `CalculateVMGroupAndRequestTimes()` transform metadata/PTE geometry into bandwidth and per-request timing used for TTU/watermark programming.

`CalculateFlipSchedule()` estimates the immediate-flip VM/PTE/row fetch schedule and per-pipe flip bandwidth, then marks `ImmediateFlipSupportedForPipe[k]` based on VM-line and row-line limits plus minimum row time.

`TruncToValidBPP()` validates or chooses an output BPP for HDMI, DP, eDP, and DP 2.0 link budgets, taking DSC, lanes, link bit rate, output format, DSC input BPC, and ODM combine into account. It returns `BPP_INVALID` for impossible link configurations.

`CalculatePrefetchSchedulePerPlane()` is a per-state wrapper around `CalculatePrefetchSchedule()` used by `dml314_ModeSupportAndSystemConfigurationFull()`.

`CalculateWatermarksAndDRAMSpeedChangeSupport()` computes urgent, DRAM-clock-change, writeback, stutter, and Z8 watermarks. It also decides whether DRAM clock changes are supported in vactive, only in vblank, or unsupported for the current prefetch mode and timing margins.

`CalculateDCFCLKDeepSleep()` computes the minimum deep-sleep DCFCLK from per-plane delivery time, bandwidth, return bus width, and pixel clock floors.

`CalculateUrgentBurstFactor()` determines luma/chroma/cursor urgent burst multipliers and flags when DET or cursor buffering cannot hide urgent latency.

`CalculateStutterEfficiency()` estimates stutter and Z8 stutter efficiency from DCC compression, zero-size request fractions, ROB/compressed-buffer capacity, row bandwidth, DET buffering, frame/vactive time, and self-refresh exit costs.

`CalculateSwathAndDETConfiguration()` begins near the end of this chunk and continues beyond line 6839. In this range it calls `CalculateSwathWidth()`, initializes viewport support, and starts deriving min/max swath heights for source format, tiling, and scan direction. The rest of its DET sizing and support logic belongs to the next chunk.

## Mode-Support Control Flow

`dml314_ModeSupportAndSystemConfigurationFull()` is the main support-evaluation function in this chunk.

It first derives allowed prefetch modes and validates basic plane constraints:

- scaler enablement, luma/chroma tap ranges, scale ratios, and chroma scaler limits;
- source format, linear tiling, scan direction, and DCC compatibility;
- per-plane bytes/block sizes, read bandwidth, and writeback bandwidth;
- writeback latency, writeback unit count, writeback scale/tap limits, and writeback line-buffer fit.

It then calculates minimum DPPCLK per plane, maximum swath widths from line-buffer/hardware limits, and initial single-DPP viewport support. For every SoC state `i` and both combine choices `j`, it chooses ODM combine policy, MPC combine, DPP count, required DPPCLK, and required DISPCLK. The logic can force ODM for DSC/FMT buffer limits, split planes for MPC, retry when active DPP count exceeds hardware limits, and record `DISPCLK_DPPCLK_Support` and `TotalAvailablePipesSupport`.

The link/DSC section validates DSC input BPC, chooses DSC slice counts, decides DSC/FEC requirements, computes link BPP for HDMI, DP, eDP, and DP 2.0 UHBR rates, and records `LinkCapacitySupport`, `ODMCombine4To1SupportCheckOK`, `NotEnoughDSCUnits`, and per-state DSC delays.

For each state/combine pair it computes swath/DET geometry, DCFCLK deep sleep, VM/PTE bytes, prefetch source lines, row bandwidth, urgent latency, urgent burst factors, vactive pixel/cursor/meta/PTE bandwidth, writeback delay time, max vstartup, return bandwidth, ROB support, and total vertical-active bandwidth support. If `UseMinimumRequiredDCFCLK` is set it delegates to `UseMinimumDCFCLK()` before return-bandwidth/ROB checks.

The prefetch loop is stateful and iterative. For each state/combine pair it tries prefetch modes and possibly reduced `MaxVStartup` values until either prefetch, dynamic metadata, prefetch V ratio, and immediate-flip requirements pass, or all candidates are exhausted. It calls `CalculatePrefetchSchedulePerPlane()`, recomputes prefetch urgent burst factors, checks total read bandwidth with prefetch, enforces line-count limits (`LinesForMetaPTE < 32`, `LinesForMetaAndDPTERow < 16`, `LineTimesForPrefetch >= 2`), evaluates immediate flip through `CalculateFlipSchedule()`, and computes DRAM clock change support/watermarks for the candidate.

After PTE buffer, cursor, pitch, and viewport-exceeds-surface checks, the function composes `ModeSupport[i][j]` from all boolean gates. It also writes a first-failure style `ValidationStatus[i]` for diagnostics. Finally it walks voltage states from highest index down, selects `VoltageLevel`, `ModeIsSupported`, `maxMpcComb`, final `MPCCombineEnable[]`, `DPPPerPlane[]`, `DCFCLK`, `DRAMSpeed`, `FabricClock`, `SOCCLK`, `ReturnBW`, and `ImmediateFlipSupport`.

## State And Persistence Behavior

There is no durable storage or external persistence in this chunk. The only state mutation is in `mode_lib->vba`, and the state is intended to live for the duration of DML validation/programming. The mutation is broad: many intermediate arrays are both scratch and later inputs to subsequent phases. Examples include `BytePerPixel*`, swath geometry, PTE row metrics, prefetch line counts, urgent burst factors, support flags, watermarks, selected clocks, and final pipe-count fields.

This creates an important ordering dependency. `dml314_recalculate()` assumes mode support and pixel-clock adjustment have populated and selected the relevant fields before display pipe and watermark calculation. `DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` assumes `VoltageLevel`, `maxMpcComb`, `DPPPerPlane`, selected clocks, and combine decisions are already meaningful.

Several helpers mutate `v` even when they look like pure calculators. For example, `CalculateVMAndRowBytes()` writes macro-tile and PTE geometry through output pointers and reads `v->GPUVMMaxPageTableLevels`; `CalculateWatermarksAndDRAMSpeedChangeSupport()` writes global watermark and margin fields in `v`; `CalculateDCFCLKDeepSleep()` writes `v->DCFCLKDeepSleepPerPlane[]`; and `CalculateFlipSchedule()` writes immediate-flip arrays for the current pipe.

## Dependencies And Integration Points

The chunk includes `dc.h`, `display_mode_lib.h`, `display_mode_vba_314.h`, and `dml_inline_defs.h`. It depends heavily on the math helpers/macros from DML such as `dml_min`, `dml_max`, `dml_max3`, `dml_max4`, `dml_max5`, `dml_floor`, `dml_ceil`, `dml_round`, `dml_log2`, `ASSERT`, `DTRACE`, and `dml_print`.

Important external functions/macros referenced but not defined in this chunk include:

- `ModeSupportAndSystemConfiguration()`
- `PixelClockAdjustmentForProgressiveToInterlaceUnit()`
- `CalculateMinAndMaxPrefetchMode()`
- `UseMinimumDCFCLK()`
- `CalculateUnboundedRequestAndCompressedBufferSize()`
- `CalculateSwathWidth()`
- the remainder of `CalculateSwathAndDETConfiguration()` after line 6839

The primary integration point is the AMD display core mode-validation pipeline for DCN314. The calculated `vba` fields feed downstream resource validation and hardware programming choices: clock requests, DPP/MPC/ODM topology, DSC/link enablement, watermarks, VM/PTE timing registers, DCC metadata behavior, immediate flip support, stutter/self-refresh capability, and validation failure reporting.

This file is architecture-versioned under `dc/dml/dcn314`, so its constants and formulas must align with DCN 3.1.4 hardware. Similar DML files for other DCN generations should not be mixed with this one unless the surrounding dispatch layer selects by hardware generation.

## Risks And Edge Cases

The code is formula dense and uses many shared scratch fields. A small ordering change or reused scratch field can corrupt later support decisions without a local compiler warning.

Many calculations divide by clock, bandwidth, ratio, pitch-derived, or geometry-derived values. The code assumes upstream validation prevents zero or nonsensical inputs in many places, though some paths explicitly guard zero DPPCLK/DISPCLK or no GPUVM/DCC cases.

Several loops use SoC state bounds inconsistently in this chunk: most iterate `i < v->soc.num_states`, while validation/status and selection loops include `i = v->soc.num_states`. This may be intentional for a sentinel/highest entry in the VBA data model, but it is a high-value area for bounds checking against the struct definitions.

Failure flags are aggregated across many independent gates. The final `ValidationStatus[i]` records only the first matching reason in a fixed priority order, so it can hide later failures in the same state.

The prefetch loop is sensitive to convergence conditions involving `NextPrefetchModeState`, `NextMaxVStartup`, line-count limits, and immediate-flip requirements. Incorrect changes can lead to accepting invalid schedules, rejecting valid modes, or iterating over stale candidate values.

Host VM and GPU VM paths inflate VM/PTE bytes and latency through host dynamic levels and `HostVMInefficiencyFactor`. Any mismatch in page-size assumptions, group-byte sizes, or return bandwidth can make prefetch and immediate flip validation wrong.

DCC and 420/RGBE/chroma handling often split luma and chroma paths. Format classification bugs can create wrong byte-per-pixel, block-size, swath, PTE row, metadata row, or stutter-efficiency results.

Several debug `dml_print()` calls are unconditional in non-`__DML_VBA_DEBUG__` blocks. If enabled in production builds by macro behavior, this path could be noisy during validation.

The assigned range ends in the middle of `CalculateSwathAndDETConfiguration()`. Any final file-level report must merge this chunk with the following chunk before treating swath/DET sizing and viewport support as fully researched.

## Test Signals

Useful validation signals for this chunk are mode-validation and hardware-facing tests rather than isolated unit tests:

- Build coverage for DCN314 DML with warnings enabled, especially enum/type conversions and array-bound assumptions.
- Golden DML vector tests comparing `ModeSupport`, `ValidationStatus`, selected voltage state, DPP/MPC/ODM topology, clocks, prefetch mode, watermarks, and stutter values against known hardware spreadsheets or prior driver outputs.
- Display mode validation across single-plane, multi-plane, 420, RGBE alpha, mono, linear, tiled, vertical scan, DCC on/off, GPUVM on/off, HostVM on/off, cursor, writeback, DSC, HDMI, DP, eDP, and DP 2.0 UHBR combinations.
- Boundary tests around `DCN314_MAX_DSC_IMAGE_WIDTH`, `DCN314_MAX_FMT_420_BUFFER_WIDTH`, max DPP count, max DSC unit count, line-buffer swath limits, PTE buffer limits, and `VRatioPrefetch` limit of 4.
- Immediate-flip tests that require host VM and tests that do not, verifying `ImmediateFlipSupportedForState`, per-pipe immediate flip support, final flip bandwidth, and VM/row line limits.
- Watermark/power tests validating DRAM clock change support, self-refresh stutter/Z8 efficiency, urgent watermark, writeback watermark, and min TTU in vblank against expected programming.
- Regression tests for `UseMinimumRequiredDCFCLK`, because changing minimum DCFCLK affects return bandwidth, urgent latency hiding, ROB support, and prefetch feasibility.
- Runtime display bring-up tests with page flips, cursor updates, writeback, DSC links, and multi-display synchronized/asynchronized vblank to catch validation results that look numerically valid but fail in hardware behavior.

### subset-b-001414: lines 6840-7367

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_mode_vba_314.c

Chunk: `subset-b-001414`
Covered source range: lines 6840-7367 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/display_mode_vba_314.c`

## Purpose

This chunk covers a dense group of DCN 3.1.4 Display Mode Library helper routines used to size display swaths and DET buffers, estimate urgent/extra latency, optionally reduce required DCFCLK per voltage state, compute compressed return buffer allocation, decide whether unbounded requests are enabled, and derive the maximum vertical startup budget. These helpers feed the main DML mode-validation and final timing/watermark calculations for the AMD display driver.

The range starts in the tail of `CalculateSwathAndDETConfiguration()`, then contains full definitions for:

- `CalculateSwathWidth()`
- `CalculateExtraLatency()`
- `CalculateExtraLatencyBytes()`
- `CalculateUrgentLatency()`
- `UseMinimumDCFCLK()`
- `CalculateUnboundedRequestAndCompressedBufferSize()`
- `UnboundedRequest()`
- `CalculateMaxVStartup()`

All routines are file-local `static` helpers. `UseMinimumDCFCLK()` is additionally marked `noinline_for_stack`, reflecting the large local arrays and stack pressure in DML calculations.

## Important APIs, Types, And Data

The helpers use DML's local enum and struct vocabulary:

- `struct display_mode_lib` and its `struct vba_vars_st vba` field are the main state carrier for `UseMinimumDCFCLK()`.
- `enum source_format_class` distinguishes RGB/mono/RGBE/4:2:0 formats, which affects chroma swath width and swath-height choices.
- `enum scan_direction_class` distinguishes normal and vertical scan, swapping whether block width or block height constrains the swath.
- `enum odm_combine_mode` affects per-plane swath width through 2:1 or 4:1 ODM combine limits.
- `enum dm_swizzle_mode` is consumed by the preceding/tail portion of `CalculateSwathAndDETConfiguration()` to decide whether minimum swath height can equal maximum height or must be halved.
- `enum unbounded_requesting_policy` and `enum output_encoder_class` decide whether unbounded request mode is allowed, especially the `dm_unbounded_requesting_edp_only` policy.

The chunk relies heavily on DML math helpers and constants: `dml_min()`, `dml_max()`, `dml_max3()`, `dml_ceil()`, `dml_floor()`, `dml_round()`, `__DML_ARB_TO_RET_DELAY__`, `DC__NUM_DPP__MAX`, and `DC__VOLTAGE_STATES`. Debug output is guarded by `__DML_VBA_DEBUG__` except for a few unconditional `dml_print()` calls in neighboring code outside these complete helpers.

## Control Flow

`CalculateSwathAndDETConfiguration()` tail computes per-plane minimum and maximum swath sizes and DET partitioning. It rounds luma/chroma swath sizes, with explicit 256-byte rounding for `dm_420_10`, then chooses maximum or minimum luma/chroma swath heights so the selected swath footprint fits within half of the DET buffer. It allocates DET between luma and chroma as all-luma, half/half, or two-thirds/one-third depending on whether chroma exists and whether luma is much larger than chroma. It then marks viewport support false if minimum swath footprint still exceeds the buffer, if requested swath width exceeds luma maximum, or if chroma width exceeds chroma maximum.

`CalculateSwathWidth()` walks each active plane and derives the single-DPP and effective swath widths. For normal scan it starts from viewport width; for vertical scan it starts from viewport height. It finds the main plane's ODM combine mode through `BlendingAndTiming[]`, then constrains effective luma swath width for 4:1 ODM, 2:1 ODM, or two-DPP splitting. Chroma swath width is half luma for 4:2:0 formats and equal to luma otherwise. `ForceSingleDPP` overrides the effective widths back to single-DPP widths. The final upper-bound swath widths are aligned to 256-byte block dimensions and capped by surface dimensions, with vertical scan using block heights as the horizontal-like constraint.

`CalculateExtraLatency()` is a thin wrapper: it calls `CalculateExtraLatencyBytes()` and converts cycles plus bytes into time using `DCFCLK` and `ReturnBW`. `CalculateExtraLatencyBytes()` computes the reordering, pixel chunk, metadata chunk, and optional GPUVM DPTE byte footprint. When both GPUVM and HostVM are enabled, it chooses the number of dynamic host page-table levels from `HostVMMinPageSize` and `HostVMMaxNonCachedPageTableLevels`; larger host pages reduce dynamic levels. Per-plane DPTE group bytes are multiplied by DPP count, host dynamic-level expansion, and `HostVMInefficiencyFactor`.

`CalculateUrgentLatency()` chooses the maximum of the three urgent latency inputs and optionally adds a fabric-clock adjustment term. This is used both for current-mode calculations and per-voltage-state validation.

`UseMinimumDCFCLK()` loops over every SoC voltage state and the two DPP/ODM candidate columns. It first accumulates max prefetch/flip DPTE row bandwidth, copies the per-plane DPP count for the state, and computes `MinimumTWait`, average-bandwidth DCFCLK need, and extra latency cycles under normal efficiency. For each plane it estimates prefetch pixel DCFCLK cycles, prefetch line time, expected prefetch acceleration, dynamic metadata VM extra latency, and available prefetch time. If the available time is positive, it computes per-plane peak DCFCLK need; otherwise it falls back to the state's maximum DCFCLK. Dynamic metadata adds a second constraint using `CalculateVupdateAndDynamicMetadataParameters()`. After summing per-plane peak needs, it applies a VM/Tsw timing constraint and writes `v->DCFCLKState[i][j]` to the lower of the state maximum and 105% of the larger average/peak requirement.

`CalculateUnboundedRequestAndCompressedBufferSize()` rounds the DET buffer size to a 64 KiB multiple, calls `UnboundedRequest()`, subtracts either active-DPP DET usage or maximum-DPP DET usage from the configured return buffer, and scales the remainder by the compressed-buffer segment size over 64. `UnboundedRequest()` permits unbounded requests only when the policy is not disabled, exactly one DPP is active, and no chroma planes exist; the `edp_only` policy further requires `Output[0] == dm_edp`.

`CalculateMaxVStartup()` computes the line time, actual blanking, default nominal blanking in lines, and available blanking. Interlaced timings without progressive-to-interlace conversion get half the blanking. Other modes subtract at least one line, or enough lines to cover writeback delay, from the selected blanking. The result is capped at 1023 lines.

## State And Persistence Behavior

Most helpers are pure calculations over input arrays and output pointers. They do not allocate memory, retain static state, or perform I/O beyond optional debug printing. Persistence happens through caller-provided arrays or through `mode_lib->vba` fields:

- `CalculateSwathWidth()` writes swath width arrays, maximum swath heights, and aligned swath-width upper bounds.
- The tail of `CalculateSwathAndDETConfiguration()` writes selected swath heights, DET luma/chroma byte allocations, per-plane viewport support, and aggregate viewport support.
- `CalculateExtraLatency()` and `CalculateUrgentLatency()` return scalar timing values used by surrounding mode calculations.
- `UseMinimumDCFCLK()` mutates `v->DCFCLKState[i][j]` for every voltage-state/candidate pair, which directly affects later return-bandwidth, ROB, vertical-active-bandwidth, prefetch, and watermark checks.
- `CalculateUnboundedRequestAndCompressedBufferSize()` writes `UnboundedRequestEnabled` and `CompressedBufferSizeInkByte`.
- `CalculateMaxVStartup()` returns a bounded line count stored by callers in current-mode or per-state startup arrays.

Because DML is a numerical model, these writes are not persistent across boots or driver reloads, but they are persistent within a single validation pass and form dependencies for later acceptance/rejection decisions.

## Dependencies And Integration Points

`CalculateSwathWidth()` is called earlier in the main `DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` path after byte-per-pixel/block-size derivation, and also by `CalculateSwathAndDETConfiguration()` for state-specific DET sizing. Its outputs feed read bandwidth, urgent burst factors, DET support checks, and prefetch bandwidth calculations.

`CalculateExtraLatency()` is called during the main mode path to populate urgent extra latency and again during per-state prefetch checks using `v->DCFCLKState[i][j]` and `v->ReturnBWPerState[i][j]`. `UseMinimumDCFCLK()` calls `CalculateExtraLatencyBytes()` directly so it can apply normal-efficiency adjustments while searching for a lower state DCFCLK.

`CalculateUrgentLatency()` is used when filling `v->UrgentLatency` for the selected fabric clock and `v->UrgLatency[i]` for each voltage state. These values feed urgent burst-factor checks, prefetch timing, DCFCLK minimization, and watermarks.

`UseMinimumDCFCLK()` is called only when `v->UseMinimumRequiredDCFCLK` is true, after per-state DCFCLK values are initialized to `v->DCFCLKPerState[i]` and before return bandwidth, ROB support, vertical active bandwidth, and prefetch validation are evaluated. This makes it an integration point between the policy knob for minimum DCFCLK and the rest of the state feasibility model.

`CalculateUnboundedRequestAndCompressedBufferSize()` is called in the main validation path after prefetch/immediate-flip support is found, and again in later per-state calculations. `UnboundedRequest()` is also used directly in a support check that rejects configurations when unbounded requesting is required by buffer sizing but not allowed by policy/topology.

`CalculateMaxVStartup()` is called for the active voltage level using `v->WritebackDelay[v->VoltageLevel][k]` and later for every voltage-state/candidate pair using `v->WritebackDelayTime[k]`. Its output bounds the VStartup search space and prefetch timing feasibility.

## Risks

- The chunk is formula-heavy and sensitive to unit consistency. Many formulas combine bytes, KiB, lines, clocks, microsecond-like DML times, and bandwidth terms. A wrong divisor such as `ReturnBW`, `ReturnBusWidth`, `DCFCLK`, or efficiency percentage can silently skew mode validation.
- `CalculateSwathAndDETConfiguration()` uses integer variables for rounded byte sizes, while upstream widths and byte-per-pixel-in-DET values include doubles. Large surfaces or unusual formats risk truncation or overflow if assumptions about dimensions change.
- Several branches divide by values assumed nonzero: `DCFCLK`, `ReturnBW`, `ReturnBusWidth`, `PixelClock[k]`, `HTotal[k] / PixelClock[k]`, `NoOfDPPState[k]`, and prefetch line/cycle terms. Callers must ensure DML validation initializes sane nonzero timing and topology values before these helpers run.
- `CalculateSwathWidth()` has a suspicious unreachable-looking condition: inside a branch that requires formats `dm_444_64`, `dm_444_32`, `dm_444_16`, `dm_mono_16`, `dm_mono_8`, or `dm_rgbe`, it checks `SourcePixelFormat[k] == dm_444_8`. This may be copied VBA logic, but if intentional support for `dm_444_8` was expected, it is worth reviewing in the whole-file merge.
- `UseMinimumDCFCLK()` can clamp to `v->DCFCLKPerState[i]` on negative/insufficient prefetch windows or dynamic metadata windows. That is conservative, but it can mask which plane or timing term caused minimum-clock reduction to fail unless debug traces are enabled.
- `UseMinimumDCFCLK()` references `v->ImmediateFlipRequirement[0]` rather than a per-plane aggregate in two places. That may match DML's model, but it is a coupling risk if immediate-flip requirements vary per plane.
- Unbounded request eligibility uses only `Output[0]` for the `edp_only` policy. Multi-output or blended timing cases depend on caller conventions that put the relevant output in slot zero.
- `CalculateMaxVStartup()` subtracts an unsigned/double-derived value from `vblank_size` into an unsigned result. If writeback delay exceeds available blanking, underflow would wrap before the 1023 cap. Callers may rely on input constraints, but this is a notable edge-case risk.

## Test Signals

Useful validation signals for this chunk are numerical and integration-oriented:

- DML golden-vector comparisons for swath width, swath height, DET luma/chroma allocation, viewport support, urgent latency, extra latency, unbounded request status, compressed buffer size, and max VStartup across known DCN 3.1.4 modes.
- Format/tiling coverage for RGB, mono, RGBE, RGBE alpha, 4:2:0 8/10/12-bit, linear tiling, 64 KiB swizzles, normal scan, and vertical scan.
- ODM and DPP topology coverage for no ODM, 2:1 ODM, 4:1 ODM, one DPP, two DPPs, and `ForceSingleDPP`.
- VM coverage with GPUVM disabled, GPUVM only, GPUVM plus HostVM, host page sizes below 2 KiB, 2 KiB to below 1 MiB, and at least 1 MiB, checking `CalculateExtraLatencyBytes()` and prefetch feasibility.
- `UseMinimumDCFCLK()` regression tests comparing `v->DCFCLKState[i][j]` with and without `UseMinimumRequiredDCFCLK`, including dynamic metadata enabled, immediate flip required, and tight VStartup cases.
- Boundary tests for `CalculateUnboundedRequestAndCompressedBufferSize()` with single-DPP/no-chroma/eDP, single-DPP/no-chroma/non-eDP, multi-DPP, chroma-present, disabled policy, and small return-buffer sizes.
- `CalculateMaxVStartup()` edge tests for zero `VBlankNom`, small blanking, interlace without progressive-to-interlace conversion, large writeback delay, and the 1023-line cap.
