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
