# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_mode_vba_31.c

Chunk: `subset-b-001410`
Covered source range: lines 1-6774 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn31/display_mode_vba_31.c`

## Purpose

This chunk contains most of the DCN 3.1 Display Mode Library VBA implementation used by the AMD display driver to decide whether a display configuration is supported and to derive timing, bandwidth, clock, prefetch, watermark, DCC, VM/PTE, DET, stutter, and immediate-flip parameters. The file is explicitly described as hardware-engineer supplied "HW gospel"; it intentionally does not follow normal kernel style and is kept close to the reference model.

The central data object is `struct display_mode_lib *mode_lib`, especially `mode_lib->vba` (`struct vba_vars_st`). Functions in this chunk consume already-populated SoC, IP, plane, timing, output-link, surface, writeback, scaling, VM, and policy inputs from `vba`, then write many derived values and support booleans back into the same structure. There is no independent persistent storage in this range.

## Public And Important Entry Points

- `dml31_recalculate(struct display_mode_lib *mode_lib)`: public recalculation entry point. It calls `ModeSupportAndSystemConfiguration(mode_lib)`, `PixelClockAdjustmentForProgressiveToInterlaceUnit(mode_lib)`, `DisplayPipeConfiguration(mode_lib)`, and finally `DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation(mode_lib)`.
- `dml31_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)`: public full mode-support evaluator for DCN 3.1. It iterates voltage states and MPC-combine choices, computes required clocks and bandwidths, validates link/DSC/ODM/MPC/writeback/prefetch/VM/DET constraints, and selects `VoltageLevel`, `maxMpcComb`, active clocks, return bandwidth, DPP allocation, and immediate-flip support.
- `dml31_CalculateWriteBackDISPCLK(...)`: public helper that computes required writeback display clock from pixel clock, writeback horizontal/vertical ratios, taps, source/destination width, total pixels, and line buffer size.

Most other routines in this chunk are `static` helper calculations used by those public functions.

## Local Types, Constants, And Macros

- `Pipe`: compact per-plane working struct passed to `CalculatePrefetchSchedule()`. It carries DPP/DISP/pixel/DCF clocks, DPP count, scaler state, ratios, scan direction, 256-byte block geometry, interlace/cursor/vblank/HTotal/DCC/ODM/source-format/bytes-per-pixel fields, and progressive-to-interlace state.
- `BPP_INVALID` and `BPP_BLENDED_PIPE`: output bits-per-pixel sentinels.
- `DCN31_MAX_DSC_IMAGE_WIDTH` and `DCN31_MAX_FMT_420_BUFFER_WIDTH`: DSC and 4:2:0 formatter width constraints that can force ODM combine or reject a mode.
- `DCN3_15_MIN_COMPBUF_SIZE_KB` and `DCN3_15_MAX_DET_SIZE`: DCN 3.15-specific compressed-buffer/DET sizing constants used when `mode_lib->project == DML_PROJECT_DCN315`.
- `__DML_VBA_MIN_VSTARTUP__`, `__DML_ARB_TO_RET_DELAY__`, and `__DML_MIN_DCFCLK_FACTOR__`: tuning constants for prefetch startup search, return-latency modeling, and minimum DCFCLK deep sleep calculation.

The file depends heavily on DML math helpers from `dml_inline_defs.h`, such as `dml_min`, `dml_max`, `dml_ceil`, `dml_floor`, and `dml_log2`, plus debugging/assertion hooks `dml_print`, `DTRACE`, and `ASSERT`.

## Major Helper Functions

- `dscceComputeDelay()` and `dscComputeDelay()` estimate DSC encode/compression pipeline delay in pixels/cycles for bpc, BPP, slice width/count, output format, and output type. ODM combine scales the result in callers.
- `TruncToValidBPP()` selects or validates link BPP against HDMI/DP/DP2/eDP link rate, lane count, DSC enablement, output format, DSC input bpc, and ODM mode. Invalid results use `BPP_INVALID`.
- `RoundToDFSGranularityUp()` and `RoundToDFSGranularityDown()` quantize clocks to DFS granularity using `DISPCLKDPPCLKVCOSpeed`.
- `CalculateDCCConfiguration()` derives luma/chroma max uncompressed block, max compressed block, and independent block size from DCC enablement, pixel format, surface dimensions, DET budget, request height, tiling, bytes per pixel, and scan orientation.
- `CalculatePrefetchSourceLines()` computes scaler-prefill source-line demand and max swath count, with different behavior when viewport positioning is ignored.
- `CalculateVMAndRowBytes()` computes DCC meta row bytes, pixel PTE row bytes, macro tile width, PTE request geometry, PTE buffer fit, DPDE/meta PTE frame bytes, VM group bytes, and DPTE group bytes for a luma or chroma plane.
- `CalculatePrefetchSchedule()` is the core prefetch scheduler. It computes vupdate/dynamic-metadata timing, scaler/output delay, VM and row request timing, required prefetch bandwidth, destination lines for prefetch, VM/row lines in vblank, prefetch V ratios, and required luma/chroma pixel-data bandwidth. It returns a boolean error and zeroes output bandwidth/timing fields on failure.
- `CalculatePrefetchSchedulePerPlane()` adapts `vba` state arrays for one voltage-state/MPC-combine/plane tuple into a `Pipe` and calls `CalculatePrefetchSchedule()`.
- `CalculateTWait()` maps prefetch mode to required wait time for DRAM clock change, self-refresh enter/exit, and urgent latency.
- `CalculateRowBandwidth()` converts meta row bytes and DPTE row bytes into recurring row bandwidth for luma/chroma.
- `CalculateFlipSchedule()` computes VM/row timing and bandwidth for immediate flip and sets `ImmediateFlipSupportedForPipe[k]`.
- `CalculateVupdateAndDynamicMetadataParameters()` computes vupdate/vready offsets and dynamic metadata timing (`TSetup`, `Tdmbf`, `Tdmec`, `Tdmsks`).
- `CalculateWatermarksAndDRAMSpeedChangeSupport()` computes urgent, DRAM clock change, writeback, stutter, and Z8 watermarks, active DRAM clock-change margins, and returns a `clock_change_support` classification.
- `CalculateDCFCLKDeepSleep()` derives DCFCLK deep-sleep minimum from per-plane delivery times and aggregate read bandwidth.
- `CalculateUrgentBurstFactor()` computes urgent burst multipliers for cursor/luma/chroma and flags insufficient urgent latency hiding.
- `CalculatePixelDeliveryTimes()`, `CalculateMetaAndPTETimes()`, and `CalculateVMGroupAndRequestTimes()` generate timing observability values used by downstream programming: delivery times per swath/request, nominal/vblank/flip meta chunk times, PTE group times, and VM request/group times.
- `CalculateStutterEfficiency()` estimates stutter/Z8 efficiency and burst counts from compression, DET/ROB/compbuf capacity, row bandwidth, DCC zero-size behavior, writeback, vblank synchronization, and critical-plane timing.
- `CalculateSwathAndDETConfiguration()` begins at line 6633 and continues beyond this chunk. This chunk covers its setup and early per-plane swath-height/DET sizing logic through line 6774; the function body is incomplete here and must be merged with the later chunk before whole-function conclusions are final.

## Main Control Flow

`dml31_recalculate()` is the high-level sequence for a selected mode. First the mode-support path determines whether any voltage/MPC combination can support the mode and selects the active state. Next pixel clocks are adjusted for progressive-to-interlace behavior, the pipe DET/swath configuration is populated, and the final selected-state performance pass computes clocks, prefetch, watermarks, and observable timing values.

`dml31_ModeSupportAndSystemConfigurationFull()` is the most important control-flow block in this chunk:

1. Determine the min/max prefetch mode from `AllowDRAMSelfRefreshOrDRAMClockChangeInVblank`.
2. Validate scaler ratios/taps, source format/tiling/scan constraints, writeback latency, writeback unit count, and writeback scaling/taps.
3. Compute byte-per-pixel/block dimensions through `dml30_CalculateBytePerPixelAnd256BBlockSizes()`, single-DPP read bandwidth, write bandwidth, PSCL factors, minimum single-DPP DPPCLK, and maximum swath width.
4. For each voltage state and MPC-combine option, choose ODM combine or MPC split policy, compute DPP count and required DPPCLK/DISPCLK, force additional splitting for special DCN315 DET override cases, and check clock and pipe-count support.
5. Compute DSC slice counts, link BPP/FEC/DSC requirements for HDMI, DP, eDP, and DP 2.0 rates, then check link capacity, DSC input bpc, 4:2:2 native DSC support, 4:1 ODM support, and DSC unit count.
6. For each state/combination, compute swath/DET geometry, projected DCFCLK deep sleep, VM/meta/PTE bytes, row bandwidths, urgent latency and burst factors, writeback delay, max vstartup, return bandwidth, ROB support, vertical-active bandwidth support, prefetch support, dynamic metadata support, prefetch V-ratio support, immediate flip support, unbounded request/compressed buffer sizing, and DRAM clock-change support.
7. Check PTE buffer size, cursor format support, pitch alignment, and viewport-versus-surface bounds.
8. Set `ModeSupport[i][j]` only when all support predicates pass, then select `VoltageLevel`, `ModeIsSupported`, `ImmediateFlipSupport`, `MPCCombineEnable[]`, `DPPPerPlane[]`, `DCFCLK`, `DRAMSpeed`, `FabricClock`, `SOCCLK`, `ReturnBW`, and `maxMpcComb`.

`DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` then performs the selected-state detailed pass. It recomputes return bandwidth, writeback/DISPCLK/DPPCLK, byte-per-pixel values, swath width, read bandwidth, DCFCLK deep sleep, DSCCLK and DSC delay, VM/PTE/meta rows, urgent extra latency, writeback delay, max vstartup, and urgent latency. It searches `VStartupLines` from `__DML_VBA_MIN_VSTARTUP__` to the maximum available lines until prefetch and required immediate flip are supported. After the loop it computes unbounded request and compressed buffer size, watermarks, pixel/meta/PTE/VM timing, min TTU in vblank, DCC configuration, vstartup adjustment, total read bandwidth, and stutter efficiency.

## State And Persistence Behavior

This chunk has no file-static mutable state, no allocation, and no I/O persistence. All state is in caller-owned `mode_lib->vba`, and almost every function writes derived values into it or into arrays passed by pointer.

Important persisted `vba` outputs in this chunk include:

- Mode selection: `ModeSupport[][]`, `ModeIsSupported`, `VoltageLevel`, `maxMpcComb`, `MPCCombineEnable[]`, `DPPPerPlane[]`.
- Clocks and bandwidth: `DISPCLK`, `DPPCLK[]`, `GlobalDPPCLK`, `DCFCLK`, `DCFCLKDeepSleep`, `DRAMSpeed`, `FabricClock`, `SOCCLK`, `ReturnBW`, per-state `ReturnBWPerState[][]`, and required clock arrays.
- Link/compression: `OutputBppPerState[][]`, `RequiresDSC[][]`, `RequiresFEC[][]`, `NumberOfDSCSlices[]`, `DSCDelay[]`, `DSCDelayPerState[][]`.
- Prefetch and flip: `PrefetchSupported[][]`, `PrefetchModePerState[][]`, `VRatioPreY/C`, selected `VRatioPrefetchY/C`, `DestinationLinesForPrefetch`, VM/row request lines, `PrefetchBandwidth`, `prefetch_vmrow_bw`, `ImmediateFlipSupportedForState[][]`, `ImmediateFlipSupportedForPipe[]`, `final_flip_bw[]`.
- VM/PTE/DCC geometry: `PDEAndMetaPTEBytesFrame`, `MetaRowByte`, `PixelPTEBytesPerRow`, `dpte_row_height`, `meta_row_height`, `meta_req_width/height`, `MacroTileWidthY/C`, PTE request sizes, VM/DPTE group bytes, DCC block sizes.
- DET/swath and latency: `SwathWidth*`, `SwathHeight*`, `DETBufferSize*`, `UrgentWatermark`, `DRAMClockChangeWatermark`, stutter/Z8 watermarks, `MinTTUVBlank`, delivery times, meta/PTE/VM request times, and stutter efficiency fields.

Because outputs are accumulated in arrays indexed by voltage state, MPC-combine setting, and plane, stale input or inconsistent dimensions can propagate into many later decisions. The routines generally assume inputs are valid and nonzero where hardware requires them; only selected conditions are guarded by support flags or `ASSERT`.

## Dependencies And Integration Points

This implementation includes `dc.h`, `display_mode_lib.h`, `dcn30/display_mode_vba_30.h`, `display_mode_vba_31.h`, and `dml_inline_defs.h`. It directly calls shared DML routines such as:

- `ModeSupportAndSystemConfiguration()` and `PixelClockAdjustmentForProgressiveToInterlaceUnit()`, likely wrappers/dispatchers declared outside this file.
- `CalculateMinAndMaxPrefetchMode()`, used to map policy into prefetch-mode search bounds.
- `dml30_CalculateBytePerPixelAnd256BBlockSizes()`, used repeatedly for source-format and tiling geometry.

The integration contract is with the AMD display DC/DML mode validation and programming path. Higher-level display code populates `display_mode_lib` from requested streams, planes, link caps, SoC/IP caps, policy settings, and memory/VM characteristics. This file then returns support decisions and programming values used to pick a voltage state, DPP/ODM/MPC topology, bandwidth budgets, watermarks, DET buffer allocation, clock requirements, DSC/link parameters, and flip/prefetch constraints.

The helper `PatchDETBufferSizeInKByte()` is a DCN315-specific integration point. For multiple active planes without explicit DET override, it derives a shared DET size from `ip.config_return_buffer_size_in_kbytes`, subtracting reserved compressed-buffer space and distributing the remainder per total pipe count with 64 KiB granularity and a maximum DET size cap.

## Risks And Edge Cases

- This code is formula-heavy hardware model code. Small changes to constants, rounding direction, integer versus double conversion, or state indexing can alter mode support or watermarks and cause display blanking, underflow, excessive clocks, or missed low-power opportunities.
- Many calculations divide by clocks, ratios, bandwidths, byte-per-pixel values, `HTotal`, pitch, swath width, and buffer sizes. Most are assumed nonzero by construction; malformed inputs can produce undefined or nonsensical derived values.
- `CalculatePrefetchSchedule()` uses a boolean error result but also mutates many output pointers before failure. It zeroes several outputs on `MyError`, so callers must treat the error flag and zeroed bandwidth/timing values together.
- The prefetch search depends on both `NextPrefetchModeState` and decreasing `NextMaxVStartup`. Off-by-one changes around `__DML_VBA_MIN_VSTARTUP__`, max vstartup, or lines-for-VM/row thresholds can reject otherwise valid modes or accept unsafe ones.
- Immediate flip support is tied to host VM, required flip policy, available bandwidth after active/prefetch traffic, VM/PTE row timing, and per-pipe row-time constraints. Regressions here can appear only under GPUVM/HostVM/immediate-flip combinations.
- Link BPP selection in `TruncToValidBPP()` silently returns `BPP_INVALID` for unsupported combinations. Caller checks must remain aligned with output type and DSC/FEC state, especially for DP 2.0 UHBR rates and forced BPP.
- `ModeSupport` selection loops from `soc.num_states` down to zero and includes a special `i == v->soc.num_states` condition while reading mode-support arrays. This is inherited VBA logic and should be treated carefully because array bounds and sentinel-state behavior depend on surrounding definitions.
- Several debug messages are copy/paste inaccurate in failure reporting, for example multiple distinct support failures print `DSC422NativeNotSupported`. This can mislead diagnosis even if the actual support booleans are correct.
- The assigned range ends mid-`CalculateSwathAndDETConfiguration()`. Any final per-file research must include the continuation after line 6774, especially the remaining DET size selection, viewport-size support, `CalculateSwathWidth()`, extra latency, minimum DCFCLK, unbounded request, and `UnboundedRequest()` definitions.

## Test Signals

Useful validation signals for this chunk are display-mode and hardware-integration tests rather than isolated unit tests:

- Build coverage for `display_mode_vba_31.c` with warnings enabled enough to catch signature drift against `display_mode_vba_31.h` and shared DML helpers.
- Mode validation matrices across voltage states, one/two/four DPP, ODM 2:1/4:1, MPC combine enabled/disabled, DCN31 versus DCN315 DET behavior, and max pipe/DSC limits.
- Link tests for HDMI, DP, eDP, and DP 2.0 with forced and automatic BPP, DSC enabled/disabled, FEC requirements, 4:2:0/4:4:4/native 4:2:2 formats, and large DSC image widths.
- Plane tests for linear and 64 KiB tiled surfaces, vertical and horizontal scan, DCC enabled/disabled, RGB/RGBE/4:2:0 formats, chroma and no-chroma paths, pitch alignment boundaries, viewport exceeding surface, and cursor 64 bpp support.
- Prefetch stress cases varying GPUVM, HostVM, page-table levels, page sizes, DCC, dynamic metadata, vstartup limits, urgent latency, DRAM clock-change policy, self-refresh policy, and immediate-flip requirements.
- Watermark and power tests checking urgent, DRAM clock-change, stutter/Z8, writeback, and MinTTU values against known-good DML spreadsheets or hardware traces.
- Runtime display tests watching for underflow, pstate switch failures, page faults, flip deadline misses, incorrect DSC/link training choices, and regressions in `ModeIsSupported` for known monitor/plane configurations.
