# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_mode_vba_31.c lines 6775-7252

## Scope And Purpose

This chunk is the tail of the DCN 3.1 Display Mode Library VBA implementation. It closes the swath/DET sizing helper and then defines a small set of shared calculation helpers used by the mode-support and display-configuration paths:

- `CalculateSwathWidth()` derives per-plane luma/chroma swath widths, single-DPP widths, maximum swath heights, and upper-bound aligned swath widths.
- `CalculateExtraLatency()` and `CalculateExtraLatencyBytes()` estimate urgent extra latency from round-trip fabric cycles, reorder buffering, pixel/meta chunks, and GPUVM/HostVM page-table traffic.
- `CalculateUrgentLatency()` selects the worst urgent-latency class and optionally adjusts it by fabric clock.
- `UseMinimumDCFCLK()` computes a lower DCFCLK requirement per voltage-state/DPP-combine option when `UseMinimumRequiredDCFCLK` is enabled.
- `CalculateUnboundedRequestAndCompressedBufferSize()` and `UnboundedRequest()` decide whether unbounded requesting can be used and how much compressed-buffer capacity remains after DET allocation.

These routines are not externally exported. They operate as internal formula blocks for AMD's DML model, mutating arrays and fields in `struct vba_vars_st` or returning scalar timing/bandwidth estimates that later determine mode support, prefetch support, watermarks, stutter efficiency, and DRAM clock-change behavior.

## Important APIs, Types, And Functions

`CalculateSwathWidth()` takes source format/scan/viewport/surface/timing arrays and writes:

- `SwathWidthSingleDPPY[]` and `SwathWidthSingleDPPC[]`, the source swath span before DPP splitting.
- `SwathWidthY[]` and `SwathWidthC[]`, the per-DPP or ODM-limited luma/chroma swath span.
- `MaximumSwathHeightY[]` and `MaximumSwathHeightC[]`, selected from 256-byte block dimensions depending on scan orientation.
- `swath_width_luma_ub[]` and `swath_width_chroma_ub[]`, block-aligned upper bounds clipped to the aligned surface dimension.

The function uses `enum source_format_class` to detect 4:2:0 formats, `enum scan_direction_class` to distinguish vertical scan from normal scan, `enum odm_combine_mode` to limit swath width for ODM 2:1 or 4:1, and `DPPPerPlane[]`/`ForceSingleDPP` to choose split versus full-width behavior.

`CalculateExtraLatency()` is a thin wrapper around `CalculateExtraLatencyBytes()`. It converts byte pressure into time using `ReturnBW` and adds fixed fabric/request latency:

`(RoundTripPingLatencyCycles + __DML_ARB_TO_RET_DELAY__) / DCFCLK + ExtraLatencyBytes / ReturnBW`

`CalculateExtraLatencyBytes()` computes the byte component as reorder bytes plus active-DPP pixel chunks and DCC meta chunks. If GPUVM is enabled, it adds each plane's DPP count times `dpte_group_bytes[]`, scaled by HostVM dynamic page-table levels and `HostVMInefficiencyFactor`. HostVM dynamic levels are derived from `HostVMMinPageSize`: small pages keep all non-cached levels, 2 KB to below 1 MB subtracts one level, and 1 MB or larger subtracts two, clamped to zero.

`CalculateUrgentLatency()` returns the maximum of pixel-only, pixel+VM, and VM-only urgent latencies. When urgent-latency adjustment is enabled, it adds a fabric-clock correction term proportional to `UrgentLatencyAdjustmentFabricClockReference / FabricClock - 1`.

`UseMinimumDCFCLK()` is marked `noinline_for_stack`, reflecting the large local arrays and formula-heavy stack use. It walks all SOC voltage states and both DPP-combine options (`j = 0..1`), reads previously populated `mode_lib->vba` arrays, and writes `v->DCFCLKState[i][j]`. Its main inputs include per-state DPP counts, prefetch lines, VM/PTE/meta row byte counts, DCC-active DPP counts, urgent latency, VStartup limits, DCFCLK maximums, DPP/DISP clocks, bandwidth totals, and page-table settings.

`CalculateUnboundedRequestAndCompressedBufferSize()` computes `*UnboundedRequestEnabled` through `UnboundedRequest()` and then subtracts rounded DET allocation from `ConfigReturnBufferSizeInKByte`. If unbounded requesting is enabled, it reserves DET only for `TotalActiveDPP`; otherwise it reserves DET for `MaxNumDPP`. The remaining capacity is scaled by `CompressedBufferSegmentSizeInkByteFinal / 64`.

`UnboundedRequest()` is the final policy predicate: unbounded requesting is allowed only when the policy is not disabled, exactly one DPP is active, and there are no chroma planes. The `dm_unbounded_requesting_edp_only` policy further restricts the output encoder to eDP.

## Control Flow

The chunk starts in the final branch of `CalculateSwathAndDETConfiguration()`. After earlier code selects luma/chroma swath heights and rounded swath byte counts, lines 6775-6816 divide the per-plane DET buffer between luma and chroma:

- Chroma-less planes receive all rounded DET bytes in `DETBufferSizeY[k]` and zero chroma DET.
- If luma swath bytes are no more than 1.5x chroma swath bytes, DET is split evenly.
- Otherwise luma receives two thirds, floored to a 1 KB boundary, and chroma receives one third.
- The function marks `ViewportSizeSupportPerPlane[k]` and global `*ViewportSizeSupport` false when minimum luma+chroma swath sizes exceed half the effective DET, luma swath width exceeds the maximum luma swath width, or chroma swath width exceeds the maximum chroma swath width.

`CalculateSwathWidth()` then supplies the width and maximum-height inputs consumed by that DET sizing function. For each active plane it chooses the single-DPP span from viewport width or height depending on scan direction, finds the main plane's ODM mode through `BlendingAndTiming[]`, and applies ODM or DPP splitting. 4:2:0 chroma widths are half luma widths; other formats keep chroma equal to luma. `ForceSingleDPP` overrides split widths back to the single-DPP values. The final aligned upper bounds are computed against either surface width/block width or surface height/block height depending on scan direction.

The latency helpers are called in both single-active-configuration and per-state support paths. The active configuration uses `CalculateExtraLatency()` around line 2491 to populate `v->UrgentExtraLatency`, and `CalculateUrgentLatency()` around line 2579 to populate `v->UrgentLatency`. The full mode-support loop computes per-state `v->UrgLatency[i]` around line 4911, optionally adjusts `v->DCFCLKState[i][j]` via `UseMinimumDCFCLK()` around line 5046, and later computes per-state `v->ExtraLatency` around line 5154 before prefetch and immediate-flip validation.

`UseMinimumDCFCLK()` has a nested state/control-flow structure:

1. Convert `PercentOfIdealFabricAndSDPPortBWReceivedAfterUrgLatency` into `NormalEfficiency`.
2. For each voltage state and DPP combination, calculate maximum prefetch/flip DPTE row bandwidth from DPP count and `DPTEBytesPerRow`.
3. Copy the per-plane DPP counts into a local array for `CalculateExtraLatencyBytes()`.
4. Compute `MinimumTWait`, non-DPTE bandwidth, DPTE bandwidth, average-bandwidth DCFCLK requirement, extra-latency bytes, and extra-latency cycles.
5. For each plane, estimate pixel DCFCLK cycles required during prefetch, total DCFCLK cycles including VM/PTE/meta row terms, prefetch pixel-line time, expected prefetch bandwidth acceleration, dynamic metadata VM latency, and available prefetch time.
6. If enough prefetch time exists, compute a per-plane peak-bandwidth DCFCLK requirement from expected prefetch ratio and acceleration; otherwise fall back to the state's maximum DCFCLK.
7. If dynamic metadata is enabled, call `CalculateVupdateAndDynamicMetadataParameters()` and require enough VStartup time to hide urgent extra latency, again falling back to the state's maximum DCFCLK when time is insufficient.
8. Sum per-plane peak requirements and apply additional VM/two-row timing constraints.
9. Store `v->DCFCLKState[i][j]` as the lower of the hardware state DCFCLK and a 5% margin over the maximum of average and peak requirements.

The unbounded-request helpers are called after prefetch/immediate-flip support decisions in active configuration and per-state evaluation. Their outputs feed watermark, compressed-buffer, and stutter calculations by controlling whether the compressed buffer can be treated as extra buffering for unbounded requests.

## State And Persistence Behavior

Most state in this chunk is transient calculation state stored in caller-provided arrays or in `mode_lib->vba`; there is no allocation, reference counting, locking, or hardware programming here.

`CalculateSwathWidth()` writes per-plane arrays that persist through the rest of the DML calculation pass. In the active path these are `v->SwathWidthSingleDPPY`, `v->SwathWidthSingleDPPC`, `v->SwathWidthY`, `v->SwathWidthC`, `v->swath_width_luma_ub`, and `v->swath_width_chroma_ub`. In mode-support loops the same logic feeds per-state "this state" and "all states" arrays through `CalculateSwathAndDETConfiguration()`. Later code uses these values for read bandwidth, prefetch scheduling, urgent burst factors, DET residency, stutter efficiency, and viewport support checks.

The tail of `CalculateSwathAndDETConfiguration()` persists `DETBufferSizeY[]`, `DETBufferSizeC[]`, `SwathHeightY[]`, `SwathHeightC[]`, `ViewportSizeSupportPerPlane[]`, and the aggregate viewport support flag. These values are central to whether a mode is declared supportable and to how much buffering is available for watermark calculations.

`UseMinimumDCFCLK()` mutates `v->DCFCLKState[i][j]` for all voltage states. This is persistent within the mode-support pass: subsequent return-bandwidth calculations use the reduced `DCFCLKState`, which can change `ReturnBWPerState`, prefetch feasibility, immediate-flip feasibility, watermarks, and final voltage-state selection. When `UseMinimumRequiredDCFCLK` is false, callers initialize `DCFCLKState[i][j]` directly from `DCFCLKPerState[i]` and skip this adjustment.

`CalculateUnboundedRequestAndCompressedBufferSize()` writes boolean and integer outputs rather than global state directly, but callers store them in `v->UnboundedRequestEnabled`, `v->CompressedBufferSizeInkByte`, or per-state locals. Those values persist into `CalculateWatermarksAndDRAMSpeedChangeSupport()` and `CalculateStutterEfficiency()`.

## Dependencies And Integration Points

This chunk depends on the surrounding DML/VBA infrastructure:

- `struct display_mode_lib` and `struct vba_vars_st` from the DML headers hold all modeled display, SOC, IP, and per-plane state.
- Enumerations such as `enum source_format_class`, `enum scan_direction_class`, `enum odm_combine_mode`, `enum output_encoder_class`, and `enum unbounded_requesting_policy` define source/policy cases.
- Constants such as `DC__NUM_DPP__MAX`, `DC__VOLTAGE_STATES`, `__DML_ARB_TO_RET_DELAY__`, and the DCN 3.1 IP/SOC fields bound array sizes and fixed-latency terms.
- Math helpers from `dml_inline_defs.h` (`dml_min`, `dml_max`, `dml_max3`, `dml_ceil`, `dml_floor`, `dml_round`) are used throughout and preserve the spreadsheet-derived DML formulas.
- `CalculateTWait()` and `CalculateVupdateAndDynamicMetadataParameters()` are local helpers outside this chunk that provide prefetch wait-time and dynamic metadata timing terms for `UseMinimumDCFCLK()`.
- `dml30_CalculateBytePerPixelAnd256BBlockSizes()` runs before these helpers in caller paths to populate bytes-per-pixel and 256-byte block dimensions.

The main integration points are the two large DML flows:

- `dml31_ModeSupportAndSystemConfigurationFull()` calls these helpers while testing every voltage state and DPP split option. It uses their outputs to compute viewport support, DCFCLK requirements, return bandwidth, prefetch support, dynamic metadata support, immediate-flip support, unbounded request policy, watermarks, and stutter efficiency.
- The display-configuration/watermark path around `DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` calls the same helpers for the selected operating point, storing active `vba` outputs consumed by DC programming and diagnostics.

Although the file lives under the AMDGPU display driver, this chunk is modeling code rather than kernel resource-management code. It does not call DRM, DC hardware programming, memory-management, or synchronization APIs directly.

## Risks And Edge Cases

Swath and DET sizing are sensitive to integer rounding and scan orientation. `CalculateSwathWidth()` switches from width/block-width alignment to height/block-height alignment for vertical scan. A mismatch here can overstate or understate the swath upper bound, which propagates into DET sizing, bandwidth, urgent-burst factors, and viewport support. The half-width chroma handling for 4:2:0 and zero-chroma handling via `BytePerPixC[k] <= 0` are also important edge cases.

ODM and blending relationships are subtle. `CalculateSwathWidth()` uses `BlendingAndTiming[k]` to inherit the main plane's ODM mode before applying 4:1 or 2:1 width limits. Incorrect blending/timing indexes or failure to keep overlay planes aligned with their main timing can produce inconsistent swath widths across planes sharing an OTG.

The DET split logic assumes effective DET size rounded up to a 64 KB granularity and then makes half/two-thirds allocations. Boundary cases around `RoundedUpMinSwathSizeBytesY + RoundedUpMinSwathSizeBytesC > actDETBufferSizeInKByte * 1024 / 2` can flip viewport support. Off-by-one rounding or unit mistakes between KB and bytes can reject valid modes or accept modes that will not fit in DET.

Latency calculation has division risks if callers pass zero `DCFCLK`, `ReturnBW`, `NormalEfficiency`, or bandwidth denominators. In normal DML flow these are expected to be valid SOC/model values, but corrupted tables or incomplete initialization would produce invalid results rather than explicit error returns.

HostVM/GPUVM handling depends on page-size thresholds and page-table-level counts. `CalculateExtraLatencyBytes()` changes dynamic HostVM levels at 2 KB and 1 MB page sizes and scales DPTE traffic by `(1 + 8 * HostVMDynamicLevels)`. Wrong page-size units or stale `HostVMMaxNonCachedPageTableLevels` values can materially alter urgent-extra-latency and DCFCLK requirements.

`UseMinimumDCFCLK()` is formula-dense and writes a global per-state result. If any upstream arrays such as `PrefetchLinesY/C`, `MaximumVStartup`, `DPTEBytesPerRow`, `PDEAndMetaPTEBytesPerFrame`, `MetaRowBytes`, `swath_width_*_all_states`, or bandwidth totals are not populated before the call, the function can compute artificially low or high DCFCLK. The fallback to `v->DCFCLKPerState[i]` is protective when time budgets are impossible, but not when inputs are subtly stale.

Dynamic metadata tightens DCFCLK requirements in two places: extra VM latency reduces prefetch time, and `CalculateVupdateAndDynamicMetadataParameters()` determines the time left to hide urgent extra latency. Modes with HDR dynamic metadata, GPUVM, HostVM, high page-table levels, or small VBlank/VStartup margins are therefore high-risk regression cases.

Unbounded requesting is deliberately narrow. It is disabled for multi-DPP, chroma, non-eDP under eDP-only policy, or explicit disable policy. Bugs in the `NoChroma`/`NoChromaPlanes` input can incorrectly grant compressed-buffer credit to formats that should not receive it, affecting stutter and watermark estimates.

## Test Signals

Useful validation signals are mostly indirect because this code is internal DML math:

- Mode validation outcomes for large viewports, rotated/vertical-scan surfaces, 4:2:0 formats, RGBE/RGBE-alpha formats, and DPP split or ODM 2:1/4:1 configurations. Regressions may appear as unexpected mode rejection, unexpected mode acceptance, or bandwidth validation changes.
- DML debug output under `__DML_VBA_DEBUG__`, especially swath widths, surface aligned bounds, extra latency bytes/time, unbounded-request state, and compressed-buffer size.
- Watermark and stutter changes after toggling `UseMinimumRequiredDCFCLK`, GPUVM, HostVM, page-table levels, dynamic metadata, immediate flip, or DRAM clock-change policy.
- Hardware/display symptoms from bad calculations: underflow, flicker during prefetch or immediate flip, incorrect DRAM clock-change support, self-refresh/stutter efficiency changes, black screen on high-bandwidth modes, or modes that only fail with chroma or vertical scan.
- Boundary tests around one active DPP versus multiple DPPs, chroma-less versus chroma formats, eDP versus DP/HDMI outputs under `dm_unbounded_requesting_edp_only`, and DET sizes near minimum swath-fit thresholds.
- Per-voltage-state traces should show `DCFCLKState[i][j]` no greater than `DCFCLKPerState[i]` after `UseMinimumDCFCLK()`, with a 5% margin over the larger of average and peak modeled requirements unless the formulas fall back to the state maximum.

## Cross-Chunk Notes

The earlier part of this same file defines the prototypes, top-level DML entry points, byte/block-size setup, swath/DET caller loops, prefetch scheduling, VM/PTE/meta row byte calculations, urgent burst factor logic, watermark calculation, and stutter-efficiency formulas that consume this chunk's outputs. The merge lane should combine this chunk with the preceding chunks for `display_mode_vba_31.c` so the final per-file report can explain the complete DML pipeline from input mode/SOC state through mode support, clock selection, prefetch validation, watermarks, and final display configuration.
