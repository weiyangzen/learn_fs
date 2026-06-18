# Research: subset-b-001408

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_mode_vba_30.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_mode_vba_30.c

## Purpose

`display_mode_vba_30.c` is the DCN 3.0 Display Mode Library VBA implementation used by AMD Display Core to validate a proposed display configuration and derive the clocks, pipe splits, bandwidth budgets, prefetch timing, watermarks, DSC/link settings, DCC/DET layout, VM/PTE timing, and stutter/self-refresh metrics needed by later hardware programming. It is explicitly treated as hardware-sourced "gospel": the comment near the top warns that the code is generated or supplied by hardware engineers, is not Linux-style, and should only be changed for clear correctness issues.

The file is stateful but not persistent: it reads and writes `mode_lib->vba`, a large scratch/result structure shared by the DML pipeline. `dml30_recalculate()` runs the selected-state calculation path, while `dml30_ModeSupportAndSystemConfigurationFull()` performs the full feasibility search across voltage states and MPC-combine options.

## Important APIs, Types, And Functions

- `typedef Pipe`: local per-plane snapshot passed into prefetch scheduling. It carries DPP/DISP/pixel clocks, DPP split count, scaler/cursor state, scan direction, block sizes, blanking, DCC, interlace, and ODM-combine state.
- `dml30_recalculate(mode_lib)`: exported recalculation entry. It invokes generic DML support setup, progressive-to-interlace pixel-clock adjustment, local display-pipe configuration, and final clock/prefetch/watermark calculation.
- `dml30_ModeSupportAndSystemConfigurationFull(mode_lib)`: exported full mode-support solver. It tests scaler/tap constraints, source/scan compatibility, writeback, clocks, pipe resources, DSC/DIO, bandwidth, ROB, prefetch, immediate flip, PTE buffer size, cursor, pitch, viewport bounds, and chooses `VoltageLevel`, `maxMpcComb`, `DPPPerPlane`, `MPCCombineEnable`, `DCFCLK`, `DRAMSpeed`, `FabricClock`, `SOCCLK`, and `ReturnBW`.
- `dml30_CalculateBytePerPixelAnd256BBlockSizes(...)`: exported format/tiling helper. It maps source pixel format and swizzle mode to luma/chroma bytes per pixel in DET, integer bytes per pixel, and 256-byte block width/height.
- `dml30_CalculateWriteBackDISPCLK(...)`: exported writeback clock helper. It computes the max of horizontal, vertical, and line-buffer-limited writeback DISPCLK needs.
- DSC helpers: `dscceComputeDelay()`, `dscComputeDelay()`, and `TruncToValidBPP()` calculate DSC encoder delay and link-limited bits per pixel for HDMI/DP/eDP paths.
- Prefetch and flip helpers: `CalculatePrefetchSchedule()`, `CalculatePrefetchSourceLines()`, `CalculateTWait()`, `CalculateFlipSchedule()`, and `CalculateDynamicMetadataParameters()` derive vblank schedules, VM/PTE row fetch time, prefetch bandwidth, dynamic metadata timing, and immediate-flip feasibility.
- Memory-layout helpers: `CalculateDCCConfiguration()`, `CalculateVMAndRowBytes()`, `CalculateRowBandwidth()`, `CalculateSwathWidth()`, and `CalculateSwathAndDETConfiguration()` derive DCC block behavior, PTE/meta bytes, swath dimensions, DET partitioning, and viewport-size support.
- Clock and bandwidth helpers: `RoundToDFSGranularityUp/Down()`, `CalculateDCFCLKDeepSleep()`, `CalculateUrgentBurstFactor()`, `CalculateExtraLatency()`, `CalculateExtraLatencyBytes()`, `CalculateUrgentLatency()`, and `UseMinimumDCFCLK()` derive rounded display clocks, deep-sleep DCFCLK, urgent burst factors, latency budgets, and optional minimum required DCFCLK per state.
- Output timing helpers: `CalculateWatermarksAndDRAMSpeedChangeSupport()`, `CalculatePixelDeliveryTimes()`, `CalculateMetaAndPTETimes()`, `CalculateVMGroupAndRequestTimes()`, and `CalculateStutterEfficiency()` populate watermark, TTU, request-delivery, VM group, meta/PTE, DRAM-clock-change, and stutter metrics.

## Control Flow

`dml30_recalculate()` is the shorter selected-state path. It calls common DML functions outside this file, then `DisplayPipeConfiguration()` to compute bytes-per-pixel, swath heights, and DET splits for the current selected topology, then `DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` to compute the current-state output values.

`DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` starts from the already selected `VoltageLevel` and `maxMpcComb`. It recomputes return bandwidth from DCFCLK, DRAM speed, fabric clock, and host-VM efficiency. It then calculates writeback DISPCLK, luma/chroma PSCL throughput, single-DPP DPPCLK, DISPCLK with and without ramping, DFS-rounded DISPCLK, per-plane DPPCLK, bytes/block sizes, swath widths, active read bandwidth, DCFCLK deep sleep, DSCCLK, and DSC delay. After that it computes VM/PTE/meta bytes for luma and chroma, prefetch source lines, row bandwidth, active DPP counts, urgent extra latency, writeback delay, maximum VStartup, final urgent latency, and iteratively increases `VStartupLines` until prefetch and immediate-flip requirements pass or the maximum startup budget is exhausted. Once a valid schedule is found it calculates watermarks, writeback DRAM-clock-change end positions, pixel delivery times, meta/PTE times, VM group/request times, `MinTTUVBlank`, DCC block configuration, total read bandwidth, VStartup margin, and stutter efficiency.

`dml30_ModeSupportAndSystemConfigurationFull()` is the broad feasibility pass. It begins at either state 0 or the max state depending on `validate_max_state`, calculates allowed prefetch-mode range, and runs one-time support checks for scaler ratios/taps, source format and scan direction, active read/write bandwidth, writeback units/mode/latency/taps, minimum DPPCLK, maximum swath width, and single-DPP viewport support. It then loops over voltage states and two MPC-combine choices. In those loops it decides ODM combine policy, forced ODM for DSC image-width or 4:2:0 buffer limits, MPC combine, DPP count, required DISPCLK/DPPCLK, total DPP usage, output link BPP, DSC/FEC requirements, DIO support, DSC unit count, per-state DSC delay, per-state swath/DET, row/meta/PTE bytes, urgent burst factors, DCFCLK deep sleep, return bandwidth, ROB support, vertical-active bandwidth, and prefetch/immediate-flip feasibility. The final mode-support predicate is a conjunction of all accumulated support flags. The best supported voltage/MPC-combine state is copied back into selected fields in `vba`.

`CalculatePrefetchSchedule()` is the densest local routine. It models dynamic metadata setup, scaler/DISP/DSC pipeline delay, VM walks, row fetches, one-to-one and equalized prefetch schedules, vblank line allocation for VM and meta/DPTE rows, luma/chroma prefetch ratios, prefetch pixel bandwidth, and VM/row bandwidth. It returns an error when the schedule has no usable pixel-fetch lines, exceeds timing constraints, or cannot allocate VM/row fetches; callers use that to reject prefetch modes.

The lower-level helpers are mostly pure calculations over arguments, but several also update `mode_lib->vba` fields for diagnostics or downstream consumers, especially `CalculateDCFCLKDeepSleep()`, `CalculateWatermarksAndDRAMSpeedChangeSupport()`, and `CalculatePrefetchSchedule()`.

## State And Persistence Behavior

There is no on-disk persistence and no allocation ownership in this file. The persistent working state is the caller-owned `struct display_mode_lib`, especially `mode_lib->vba`. The file mutates many `vba` arrays and scalars, including:

- Mode-selection state: `ModeSupport`, `ModeIsSupported`, `VoltageLevel`, `maxMpcComb`, `MPCCombineEnable`, `DPPPerPlane`, `DCFCLK`, `DRAMSpeed`, `FabricClock`, `SOCCLK`, `ReturnBW`, and per-state support matrices.
- Clock results: `DISPCLK_calculated`, `DPPCLK_calculated`, `GlobalDPPCLK`, `DSCCLK_calculated`, `DCFCLKDeepSleep`, `ProjectedDCFCLKDeepSleep`, and `DCFCLKState`.
- Memory/layout results: bytes-per-pixel, block dimensions, swath widths/heights, DET luma/chroma sizes, DCC max/independent block sizes, macro-tile widths, PTE/meta request geometry, VM group bytes, and DPTE group bytes.
- Timing and bandwidth results: read bandwidth, cursor bandwidth, prefetch bandwidth, row bandwidth, urgent burst factors, VStartup, VUpdate/VReady offsets, DST after scaler, watermarks, TTU values, stutter metrics, and immediate-flip scheduling fields.
- Support/failure flags: scaler/tap support, source/scan support, DIO support, DSC unit support, ROB support, viewport size support, prefetch support, dynamic metadata support, pitch support, PTE buffer support, urgent-latency hiding, immediate-flip support, and final mode support.

Because `mode_lib->vba` is reused across calculations, callers must treat functions as ordered passes rather than independent stateless helpers. The selected-state pass assumes that earlier support/configuration code has populated active plane count, timing, format, SoC limits, and selected voltage/MPC fields.

## Dependencies And Integration Points

The file includes `dc.h`, `../display_mode_lib.h`, `display_mode_vba_30.h`, and `../dml_inline_defs.h`. It depends on DML math helpers and macros such as `dml_max*`, `dml_min*`, `dml_ceil`, `dml_floor`, `dml_round`, `dml_log2`, `ASSERT`, `DTRACE`, and `dml_print`, plus common DML routines declared elsewhere such as `ModeSupportAndSystemConfiguration()`, `PixelClockAdjustmentForProgressiveToInterlaceUnit()`, and `CalculateMinAndMaxPrefetchMode()`.

The main external data contract is `struct vba_vars_st`, which supplies all active display timings, source formats, scaling ratios, cursor state, writeback state, DSC/link settings, DCC/GPUVM/HostVM settings, SoC clock/bandwidth tables, resource limits, and debug policy fields. It integrates with AMD DC mode validation and resource selection: higher layers fill `mode_lib->vba`, invoke the DCN30 DML functions, then consume the selected clocks, DPP/ODM/MPC topology, watermarks, VM request timing, DCC programming limits, immediate-flip support, and DRAM clock-change support for commit planning and hardware programming.

The exported helper functions are also reusable by adjacent DML/DCN code that needs writeback DISPCLK or format/block-size calculation without running the full solver.

## Risks And Edge Cases

- The file is algorithmically fragile and hardware-derived. Small arithmetic changes can alter mode validation, clocks, or watermarks across many display topologies.
- Many calculations divide by clocks, ratios, bandwidths, swath widths, and block dimensions. The caller must provide nonzero, internally consistent timing, format, and SoC inputs.
- `mode_lib->vba` scratch fields are heavily reused across nested voltage/MPC/prefetch loops. Reordering calls or consuming intermediate fields outside their intended phase can observe stale values from another state.
- Support checks are conjunctive and sometimes use sentinel values such as `BPP_INVALID`, zero bandwidth, or very large margins. A missed flag can make an unsupported mode appear valid or reject a valid high-end mode.
- GPUVM plus HostVM paths multiply VM/PTE bytes and latency by host dynamic levels and efficiency ratios. These paths are especially sensitive to min page size, page-table level, and urgent-latency settings.
- Prefetch scheduling is bounded by hardware register limits, including `DST_Y_PREFETCH` clamping, VM lines under 32, row lines under 16, destination prefetch lines at least 2, and VRatio prefetch no more than 4.
- Immediate flip support shares remaining bandwidth across planes. If `TotImmediateFlipBytes` or bandwidth allocation is inconsistent, per-pipe flip bandwidth can be wrong.
- DSC and output BPP logic depends on DP/HDMI/eDP link rates, lanes, DSC input BPC, slice counts, ODM combine mode, and output format. Invalid BPP propagation can break DIO support.
- The code has deliberate style exceptions, dummy variables, unused-argument casts, and generated-like structures. Mechanical cleanup risks changing behavior or stack layout assumptions; `UseMinimumDCFCLK()` is explicitly marked `noinline_for_stack`.

## Test Signals

- Build tests for AMDGPU/DC DML should catch declaration mismatches, enum/type drift, and stack/layout issues.
- Golden DML validation vectors are the most important signal: exercise single and multi-plane, 4:4:4 and 4:2:0, RGBE alpha, linear and tiled swizzles, horizontal and vertical scan, DCC on/off, GPUVM and HostVM combinations, writeback on/off, DSC on/off, HDMI/DP/eDP links, ODM 2:1 and 4:1, MPC split, immediate flip required, and dynamic metadata enabled.
- Regression checks should compare selected `VoltageLevel`, `DPPPerPlane`, `MPCCombineEnable`, `ODMCombineEnablePerState`, required DISPCLK/DPPCLK/DCFCLK, `ReturnBW`, prefetch mode, watermarks, DRAM clock-change support, stutter efficiency, and `ModeSupport` against known-good outputs.
- Boundary tests should target maximum DSC image width, maximum 4:2:0 buffer width, 1/2/4 DSC slice decisions, VM line and row line register limits, VStartup exhaustion, PTE buffer size exhaustion, cursor 64 bpp support, pitch alignment failures, and viewport larger than surface.
- Runtime failure signals include `ASSERT(v->PrefetchModeSupported)`, debug `dml_print()` messages for prefetch schedule violations, bandwidth violations, dynamic metadata time failures, unsupported BPP, and mode-support flags unexpectedly false at high voltage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_mode_vba_30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_mode_vba_30.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_mode_vba_30.h

## Purpose

`display_mode_vba_30.h` is the public declaration header for the DCN 3.0 VBA implementation. It exposes the small set of functions in `display_mode_vba_30.c` that other DML/DCN code can call: the selected-state recalculation entry, the full mode-support solver, and two reusable helper calculations for writeback DISPCLK and source-format block geometry.

The header deliberately contains no implementation logic and no persistent state. It is a source-tree-aligned contract between the DCN30 DML implementation and its callers.

## Important APIs, Types, And Functions

- `dml30_recalculate(struct display_mode_lib *mode_lib)`: runs the selected-mode DCN30 recalculation path and writes results into `mode_lib->vba`.
- `dml30_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)`: runs full DCN30 mode validation and system-configuration selection across voltage/resource states.
- `dml30_CalculateWriteBackDISPCLK(enum source_format_class WritebackPixelFormat, double PixelClock, double WritebackHRatio, double WritebackVRatio, unsigned int WritebackHTaps, unsigned int WritebackVTaps, long WritebackSourceWidth, long WritebackDestinationWidth, unsigned int HTotal, unsigned int WritebackLineBufferSize)`: computes writeback DISPCLK demand from scaling taps, ratios, timing, destination width, source width, and line-buffer size.
- `dml30_CalculateBytePerPixelAnd256BBlockSizes(enum source_format_class SourcePixelFormat, enum dm_swizzle_mode SurfaceTiling, ...)`: maps source format and swizzle mode to luma/chroma byte counts and 256-byte block dimensions through output pointers.

The declared types come from the DML/DC display headers: `struct display_mode_lib`, `enum source_format_class`, and `enum dm_swizzle_mode`.

## Control Flow

The header only declares entry points. Normal call flow is that an owning DML/DCN module includes the necessary common DML type definitions, includes this header, fills `struct display_mode_lib`, then calls either `dml30_ModeSupportAndSystemConfigurationFull()` for validation/selection or `dml30_recalculate()` for selected-state result recomputation. The helper declarations can be called independently when a caller only needs writeback clock demand or format block-size metadata.

## State And Persistence Behavior

The header itself owns no state. The two main entry points mutate the caller-owned `struct display_mode_lib`, especially `mode_lib->vba`; the helper functions return values through their return value or output pointer parameters. There is no allocation, reference ownership, file IO, or cross-call persistence in the header.

## Dependencies And Integration Points

The include guard is `__DML30_DISPLAY_MODE_VBA_H__`. The header does not include `display_mode_lib.h` or any enum/type headers itself, so it assumes callers include it in a context where `struct display_mode_lib`, `enum source_format_class`, and `enum dm_swizzle_mode` are already known. In `display_mode_vba_30.c`, this is satisfied by including `../display_mode_lib.h` before this header.

Integration is limited but important: generation-specific DML code and AMD Display Core mode-validation code use these prototypes to invoke the DCN30 VBA solver and shared helper calculations.

## Risks And Edge Cases

- The header is not standalone because it relies on prior type declarations/definitions from DML headers. Including it before the common DML type headers can produce compiler errors, especially for enum parameters.
- The helper functions use many output pointers. Callers must pass non-NULL pointers for every output of `dml30_CalculateBytePerPixelAnd256BBlockSizes()`.
- The function names are generation-specific. Accidentally mixing DCN30 declarations with another generation's implementation can silently produce wrong validation behavior even if signatures are similar.
- The main entry points mutate `mode_lib->vba`; callers must not treat them as pure queries.

## Test Signals

- Compile coverage from files that include `display_mode_vba_30.h` verifies include ordering, type visibility, and prototype/definition agreement.
- API-level tests can call `dml30_CalculateBytePerPixelAnd256BBlockSizes()` for representative formats and tilings and verify byte/block outputs.
- Writeback clock tests can compare `dml30_CalculateWriteBackDISPCLK()` against known vectors for horizontal-limited, vertical-limited, and line-buffer-limited cases.
- Integration validation should exercise both declared main entry points through the normal DCN30 DML mode-validation path and confirm expected `mode_lib->vba` results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_mode_vba_30.h -->
