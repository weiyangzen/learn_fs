# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_mode_vba_20.c

## Purpose

`display_mode_vba_20.c` is the DCN 2.0 Display Mode Library VBA implementation used by AMDGPU display code to validate a display configuration and derive the clock, pipe, bandwidth, prefetch, watermark, DSC, DCC, GPUVM, XFC, writeback, and DRAM clock-change parameters needed to program hardware. The file is explicitly described as "HW gospel" generated or supplied from hardware engineering, so it prioritizes formula fidelity over Linux style.

The public flow has two entry points. `dml20_ModeSupportAndSystemConfigurationFull()` evaluates candidate voltage states and MPC-combine choices, records validation failures, chooses the first supported state at or above `VoltageOverrideLevel`, and writes the selected DPP, DISPCLK, DCFCLK, DRAM, fabric, ODM, DSC, and output-BPP values back into `mode_lib->vba`. `dml20_recalculate()` then runs the selected configuration through final bandwidth, pipe, prefetch, watermark, and performance calculations.

## Important APIs, Types, And Functions

- `dml20_recalculate(struct display_mode_lib *mode_lib)`: exported recalculation entry point. It calls shared mode support setup, computes fabric/DRAM bandwidth, adjusts progressive-to-interlace pixel clocks, calculates pipe swaths/DET allocation, then computes final clocks, prefetch, watermarks, immediate flip, and power-management parameters.
- `dml20_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)`: exported full validation/configuration function. It fills `struct vba_vars_st` arrays for all SoC states and MPC-combine options, classifies failure reasons through `enum dm_validation_status`, selects `VoltageLevel`, and commits selected per-plane output state.
- `adjust_ReturnBW()`: constrains return bandwidth for DCC cases using ROB size, pixel chunk size, urgent latency, return bus width, DCFCLK, and the critical-compression point.
- `dscceComputeDelay()` and `dscComputeDelay()`: compute DSC encoder and fixed DSC pipeline delays for 444/422/420 output formats, including slice count, slice width, bits-per-component, and compressed BPP effects.
- `CalculatePrefetchSchedule()`: core timing solver for vblank prefetch. It computes scaler/output offsets, dynamic metadata timing, no-bandwidth time, VM/PTE and row request lines, prefetch bandwidth, prefetch ratios, and required pixel-data bandwidth; it returns an error flag when the schedule is impossible.
- `RoundToDFSGranularityUp()` / `RoundToDFSGranularityDown()`: map requested clocks to DFS granularity using the display PLL VCO speed.
- `CalculatePrefetchSourceLines()`: derives source-line demand and initial prefill lines from vertical ratio, taps, interlace mode, viewport positioning, and swath height.
- `CalculateVMAndRowBytes()`: computes macro-tile dimensions, DCC metadata row bytes, DPTE/PDE/meta-PTE bytes, PTE row heights, and PTE-buffer fit for luma/chroma surfaces under GPUVM and tiling constraints.
- `dml20_DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()`: large selected-mode calculator for DISPCLK/DPPCLK/DSCCLK, return bandwidth, swath widths, read bandwidth, urgent/stutter/writeback watermarks, DET buffering, deep-sleep DCFCLK, prefetch, immediate flip, DRAM clock-change support, XFC parameters, and VStartup.
- `dml20_DisplayPipeConfiguration()`: derives swath heights and DET buffer partitioning for each plane from pixel format, tiling, scan direction, DPP split, ODM combine, and DET size.
- `CalculateTWait()`: maps prefetch mode to the latency budget for DRAM clock change, self-refresh, or urgent-only operation.
- `CalculateRemoteSurfaceFlipDelay()`: computes XFC remote surface flip delay and fill timing.
- `CalculateWriteBackDelay()`: estimates writeback scaler delay from writeback format, ratios, taps, and destination width.
- `CalculateActiveRowBandwidth()`: converts active DCC metadata and GPUVM DPTE row requirements into row-bandwidth terms.
- `CalculateFlipSchedule()`: calculates immediate-flip VM/row request lines, final flip bandwidth, and per-pipe immediate-flip support.
- `TruncToValidBPP()`: clamps HDMI/DP/eDP output BPP to valid uncompressed or DSC-compressed values, returning `BPP_INVALID` when a link cannot carry the mode.

## Control Flow

`dml20_recalculate()` is the shorter production recalculation path. It first invokes shared DML helpers outside this file to initialize mode support and pixel-clock adjustments. It computes `FabricAndDRAMBandwidth`, configures swath heights and DET allocation through `dml20_DisplayPipeConfiguration()`, then runs `dml20_DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` to fill the selected-mode timing and watermark fields.

`dml20_DisplayPipeConfiguration()` iterates active planes. For each plane it maps source pixel format to luma/chroma bytes-per-pixel, derives 256-byte block dimensions from format and tiling, chooses maximum/minimum swath heights based on scan direction and tiling, reduces swath width for ODM combine or DPP split, rounds swath byte sizes to hardware granularities, and chooses max or min swath heights depending on whether the combined luma/chroma swath fits half of DET. It then partitions DET entirely to luma, evenly between luma/chroma, or 2:1 between luma/chroma.

`dml20_DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` is a long sequential pipeline. It computes writeback DISPCLK, per-plane scaler throughput and single-DPP DPPCLK, DISPCLK with and without ramping, rounded global DPPCLK, DCC-aware return bandwidth, swath widths, bytes-per-pixel, read bandwidth, active DPP counts, urgent latency, urgent/writeback/DRAM-clock-change watermarks, stutter efficiency, DCFCLK deep-sleep, and urgent latency support. It then calculates DSCCLK and DSC delay, VM/PTE/DCC row bytes, active row bandwidth, writeback delay, maximum VStartup, cursor bandwidth, and iteratively raises `VStartupLines` until prefetch and optional immediate flip are supported or the maximum VStartup limit is exceeded. After that it computes prefetch delivery times, min TTU vblank, DRAM clock-change support, XFC delays, and optional maximum-VStartup overrides.

`CalculatePrefetchSchedule()` is called both by selected-mode calculation and by full validation. It derives post-scaler X/Y offsets from DPP/DISPCLK delays and DSC delay, calculates vupdate/vready setup, accounts for dynamic metadata timing, chooses `Tno_bw` from GPUVM/DCC state, estimates an one-time-only prefetch bandwidth, then turns VM/PTE row fetch times into destination lines. If there is usable prefetch pixel time, it computes luma/chroma prefetch ratios and required prefetch pixel bandwidth. Any zero-clock, insufficient-destination-line, dynamic-metadata, or prefill violation clears all output bandwidth/line fields and returns an error.

`dml20_ModeSupportAndSystemConfigurationFull()` performs a broad validation sweep before committing a state. It checks scaler ratios and taps, source format/tiling/scan compatibility, luma/chroma/read/write bandwidth, DCC presence, per-state fabric/return bandwidth, ROB support, writeback mode/latency/taps, DISPCLK/DPPCLK capacity, swath/viewport limits, DPP and OTG counts, DIO/DSC/FEC/link BPP constraints, DSC clock and unit counts, per-state DSC delay, urgent latency support, prefetch support, immediate flip support, vertical active bandwidth, PTE buffer size, cursor support, and pitch alignment. It then assigns `ModeSupport[i][j]` and `ValidationStatus[i]` for each voltage/MPC option, selects the first supported option, and writes selected DPP count, DPPCLK, DISPCLK, DCFCLK, DRAM speed, fabric clock, SOCCLK, return bandwidth, ODM mode, DSC enable, and output BPP into `mode_lib->vba`.

## State And Persistence Behavior

This file has no external persistence of its own. All state is transient in `struct display_mode_lib`, primarily `mode_lib->vba`, and is consumed later by AMD display validation and programming code. It mutates hundreds of fields, including:

- Selected-mode clocks: `DISPCLK`, `DPPCLK[]`, `DCFCLK`, `SOCCLK`, `DRAMSpeed`, `FabricClock`, `DSCCLK_calculated[]`, rounded DFS clock fields, and deep-sleep DCFCLK fields.
- Configuration selections: `VoltageLevel`, `maxMpcComb`, `DPPPerPlane[]`, `ODMCombineEnabled[]`, `DSCEnabled[]`, `OutputBpp[]`, `ImmediateFlipSupport`, `PrefetchMode[][]`, and `ValidationStatus[]`.
- Surface/pipeline geometry: swath widths/heights, DET sizes, block dimensions, macro-tile widths, bytes-per-pixel, prefetch source lines, initial prefill, and row heights.
- Bandwidth and latency: return bandwidth, read bandwidth, cursor bandwidth, prefetch bandwidth, row bandwidth, urgent/stutter/writeback/DRAM-clock-change watermarks, urgent latency support, non-urgent latency tolerance, and XFC fill/transfer/precharge margins.
- Support booleans and status arrays: scale/taps, source/scan, DIO, DSC, ROB, writeback, DISPCLK/DPPCLK, viewport, pipe count, OTG count, prefetch, vratio-in-prefetch, PTE buffer, cursor, pitch, vertical active bandwidth, and immediate flip.

Because the arrays are reused for both selected-state calculations and all-state validation, ordering matters. Many later formulas read fields populated by earlier loops rather than recomputing them locally.

## Dependencies And Integration Points

The file includes `display_mode_lib.h`, `display_mode_vba_20.h`, and `dml_inline_defs.h`. It depends on the central DML data model: `struct display_mode_lib`, `struct vba_vars_st`, source/output/tiling/scan/encoder enums, clock-limit tables, and the many fixed-size arrays sized by display core constants such as `DC__NUM_DPP__MAX`.

It calls shared DML helpers from surrounding files: `ModeSupportAndSystemConfiguration()`, `PixelClockAdjustmentForProgressiveToInterlaceUnit()`, `CalculateWriteBackDISPCLK()`, `Calculate256BBlockSizes()`, `CalculateMinAndMaxPrefetchMode()`, `dml_min/max/max3/max5`, `dml_floor/ceil/round/log2/pow`, `DTRACE`, `dml_print`, and `ASSERT`.

The outputs feed the AMD Display Core mode validation and hardware programming path. Link/DIO validation uses DP/eDP/HDMI link lanes, PHY clock, downspread, FEC, DSC enablement, and output format. Memory-system validation uses SoC clock states, fabric/DRAM bandwidth, return bus width, ROB, DCC, GPUVM, DET, PTE buffer, and DCFCLK. Pipe topology integration uses `BlendingAndTiming`, ODM combine, MPC combine, DPP split count, OTG count, writeback, and cursor fields.

## Risks And Edge Cases

- The implementation is formula-dense and mutation-heavy; reordering loops or "simplifying" expressions can silently change hardware validation results.
- Many divisions assume non-zero clocks, ratios, line totals, swath widths, return bandwidths, and totals. `CalculatePrefetchSchedule()` guards zero DPPCLK/DISPCLK, but many other helpers rely on upstream validation and initialized SoC data.
- `dml20_ModeSupportAndSystemConfigurationFull()` sets `VoltageLevel` to `soc.num_states + 1` before selecting a supported state, then indexes selected-state arrays after the search. If no state is supported, callers must ensure the wider DML flow handles that invalid level before these selected fields are trusted.
- `TruncToValidBPP()` returns `unsigned int` while DSC paths can return fractional sixteenth-BPP values; this mirrors the source but is a precision-sensitive area for link/DSC validation.
- Several comments flag uncertainty or inherited issues, including the remote-surface flip delay not matching the programming guide and a "Let's do this calculation again??" return-bandwidth pass.
- Array dimensions are implicit. Loops often run through `NumberOfActivePlanes`, `soc.num_states`, and two MPC-combine choices while indexing multidimensional VBA arrays; malformed input counts would be unsafe.
- There are repeated or inconsistent-looking assignments in the full validation path, such as `MaximumReadBandwidthWithoutPrefetch` using `MaximumReadBandwidthWithPrefetch` in its accumulation and chroma DET line calculations using luma bytes in one branch. These may be intentional spreadsheet translations, but they are high-risk to touch.
- Support status is first computed per `i,j`, but `ValidationStatus[i]` is assigned inside the `j` loop; only the last `j` status remains visible per state.
- Debug prints in prefetch and XFC helpers can be noisy when DML tracing is enabled.

## Test Signals

- Kernel build coverage should catch prototype mismatches, missing enum names, and DML structure-field drift between this file and shared headers.
- DML unit or golden-vector tests should compare full `dml20_ModeSupportAndSystemConfigurationFull()` and `dml20_recalculate()` outputs against AMD spreadsheet/reference results for representative DCN 2.0 modes.
- Validation vectors should cover RGB and 420 formats, horizontal and vertical scan, linear/4KB/64KB/256KB tiling, DCC on/off, GPUVM on/off, multiple page-table levels, DPP split, ODM combine, MPC combine, multiple voltage states, and unsupported/no-state cases.
- Link tests should cover HDMI, DP, eDP, DSC enabled/disabled, FEC overhead, 270/540/810 MHz DP rates, 420/422/444 formats, invalid DSC input BPC, and output BPP truncation.
- Timing tests should exercise dynamic metadata, interlace and progressive-to-interlace, XFC enabled, cursor bandwidth, writeback enabled, immediate flip enabled, DRAM self-refresh/clock-change prefetch modes, and VStartup expansion until support or failure.
- Runtime failure signals include `ValidationStatus[]` values such as `DML_FAIL_PREFETCH_SUPPORT`, `DML_FAIL_DISPCLK_DPPCLK`, `DML_FAIL_PTE_BUFFER_SIZE`, `DML_FAIL_TOTAL_V_ACTIVE_BW`, `DML_FAIL_DIO_SUPPORT`, debug `DML: CalculatePrefetchSchedule ***failed***` prints, and ASSERTs for invalid clock assumptions.
