# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_mode_vba_20v2.c

## Purpose

`display_mode_vba_20v2.c` is the DCN 2.0v2 Display Mode Library VBA implementation for AMD Display Core. It consumes a populated `struct display_mode_lib` and mutates `mode_lib->vba` with mode-validation results, selected voltage state, pipe topology decisions, display clock requirements, prefetch schedules, watermarks, stutter/p-state support, DSC link requirements, immediate-flip support, DET/swath sizing, and related per-plane timing quantities.

The file is intentionally a hardware formula translation. Its own comment says it is "HW gospel" and should usually remain as-is. Most logic is numeric modeling over arrays indexed by active plane, voltage state, and MPC-combine option; it does not perform register programming directly.

## Important APIs, Types, And Functions

- `dml20v2_recalculate(mode_lib)`: public recalculation entry. It runs generic mode support/system configuration, fabric/DRAM bandwidth derivation, progressive-to-interlace pixel-clock adjustment, DCN20v2 pipe configuration, and final clock/prefetch/watermark/performance calculation.
- `dml20v2_ModeSupportAndSystemConfigurationFull(mode_lib)`: public full validation and selection pass. It tests source format, scale ratio, bandwidth, clocks, DIO/DSC, writeback, cursor, pitch, prefetch, PTE buffer, pipe/OTG count, and then selects `VoltageLevel`, `maxMpcComb`, `DPPPerPlane`, clocks, ODM, DSC, and output bpp.
- `dml20v2_DisplayPipeConfiguration(mode_lib)`: derives swath heights and DET luma/chroma buffer split from pixel format, tiling, scan direction, ODM combine, DPP split, viewport dimensions, and the configured DET buffer size.
- `dml20v2_DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation(mode_lib)`: final selected-state calculation for DISPCLK/DPPCLK/DSCCLK, return bandwidth, urgent/stutter/DRAM-clock watermarks, DCFCLK deep sleep, VM/PTE/DCC rows, prefetch, immediate flip, DRAM-clock-change support, and XFC values.
- Helper formulas include `adjust_ReturnBW`, `dscceComputeDelay`, `dscComputeDelay`, `CalculateDelayAfterScaler`, `CalculatePrefetchSchedule`, `RoundToDFSGranularityUp`, `RoundToDFSGranularityDown`, `CalculatePrefetchSourceLines`, `CalculateVMAndRowBytes`, `CalculateTWait`, `CalculateRemoteSurfaceFlipDelay`, `CalculateWriteBackDelay`, `CalculateActiveRowBandwidth`, `CalculateFlipSchedule`, and `TruncToValidBPP`.
- Key data is almost entirely in `struct vba_vars_st`, reached as `mode_lib->vba` or `locals`, plus SoC/IP limits under `mode_lib->vba.soc`, `mode_lib->soc`, and `mode_lib->ip`.

## Control Flow

`dml20v2_recalculate` is the small runtime entry: it invokes a common `ModeSupportAndSystemConfiguration`, computes `FabricAndDRAMBandwidth`, applies interlace pixel-clock adjustments, derives pipe swath/DET configuration, then computes final clocks, prefetch parameters, watermarks, and performance outputs. This assumes `mode_lib->vba` already contains input mode state and selected-state fields from the broader DML pipeline.

`dml20v2_ModeSupportAndSystemConfigurationFull` is the exhaustive support pass. It first validates scaler ratios/taps, source pixel format/tiling/scan combinations, writeback latency/mode/scaler limits, and basic source read/write bandwidth. It then loops over all SoC voltage states and two MPC-combine choices to derive return bandwidth, ROB support, required DISPCLK/DPPCLK, ODM combine enablement, number of DPPs per plane, viewport support, pipe and OTG support, DIO link bpp, DSC/FEC requirements, DSC delay, urgent-latency support, prefetch support, immediate-flip support, vertical-active bandwidth support, PTE buffer size support, cursor support, and pitch alignment. Each state/combine pair gets a validation status. The first valid state at or above `VoltageOverrideLevel` is selected, with MPC combine enabled only if the j=1 state is needed or policy says to use it when possible.

`dml20v2_DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation` works on the chosen mode. It calculates writeback DISPCLK, per-plane scaler throughput, single-DPP DPPCLK, selected DISPCLK with and without ramping, rounded DFS clock values, global DPPCLK, DCC-aware return bandwidth, read bandwidth, active DPP totals, urgent latency and watermarks, writeback watermarks, stutter efficiency, DCFCLK deep sleep, urgent latency tolerance, DSCCLK and DSC delay, VM/PTE/meta bytes, prefetch source lines, active row bandwidth, writeback delay, maximum vstartup, cursor bandwidth, prefetch schedules, immediate flip schedules, TTU/vblank policy, DRAM-clock-change support, and XFC timing/fill margins. It increments `VStartupLines` until prefetch and optional immediate flip pass or the maximum startup limit is exceeded.

The prefetch path is a layered calculation. `CalculateVMAndRowBytes` estimates meta/PTE frame bytes and row bytes from DCC, GPUVM, tiling, macro tile size, scan direction, viewport, pitch, page size, and hardware buffer limits. `CalculatePrefetchSourceLines` computes source lines and initial prefill. `CalculateDelayAfterScaler` models pipe delay and updates the last-pixel watermark. `CalculatePrefetchSchedule` computes VUPDATE/VREADY offsets, time allocated to metadata/PTE/row/pixel prefetch, prefetch ratios, required pixel bandwidth, and error flags. `CalculateFlipSchedule` then reserves bandwidth for immediate flip metadata and row fetches.

## State And Persistence Behavior

The file has no on-disk persistence and does not write hardware registers. Its persistent effects are mutations to the in-memory `mode_lib->vba` object that later DML/DC layers read. Important outputs include:

- Selected mode fields: `VoltageLevel`, `maxMpcComb`, `DPPPerPlane[]`, `DISPCLK`, `DPPCLK[]`, `DCFCLK`, `DRAMSpeed`, `FabricClock`, `SOCCLK`, `ReturnBW`, `ODMCombineEnabled[]`, `DSCEnabled[]`, and `OutputBpp[]`.
- Validation state: `ModeSupport[][]`, `ValidationStatus[]`, `ScaleRatioAndTapsSupport`, `SourceFormatPixelAndScanSupport`, `DIOSupport[]`, `PrefetchSupported[][]`, `ImmediateFlipSupportedForState[][]`, `PTEBufferSizeNotExceeded[][]`, and many failure-specific booleans.
- Timing and watermark outputs: urgent/stutter/writeback/DRAM-clock watermarks, `MinTTUVBlank[]`, `AllowDRAMClockChangeDuringVBlank[]`, `AllowDRAMSelfRefreshDuringVBlank[]`, `DRAMClockChangeSupport[][]`, `VStartup[]`, `VUpdateOffsetPix[]`, `VUpdateWidthPix[]`, and `VReadyOffsetPix[]`.
- Per-plane memory model outputs: swath width/height, DET split, bytes per pixel, read bandwidth, meta row bytes, DPTE row bytes, row bandwidths, prefetch bandwidth, vratio prefetch, VM/row request line counts, immediate flip line counts, XFC delays, and DSC delay.

Because nearly every field is reused by later helpers and other files through generated accessors, stale values and partial recalculations can be dangerous. The implementation often writes scratch fields such as `ProjectedDCFCLKDeepSleep[0][0]`, `PrefetchLinesY[0][0][k]`, and `PDEAndMetaPTEBytesPerFrame[0][0][k]` while iterating state/combine candidates.

## Dependencies And Integration Points

The file includes `display_mode_lib.h`, `display_mode_vba_20v2.h`, and `dml_inline_defs.h`. It depends on shared DML math helpers (`dml_min`, `dml_max`, `dml_floor`, `dml_ceil`, `dml_round`, `dml_pow`, `dml_log2`, `dml_max3`, `dml_max5`), debug helpers (`DTRACE`, `dml_print`, `ASSERT`), and common DML routines such as `ModeSupportAndSystemConfiguration`, `PixelClockAdjustmentForProgressiveToInterlaceUnit`, `CalculateWriteBackDISPCLK`, `Calculate256BBlockSizes`, and `CalculateMinAndMaxPrefetchMode`.

It integrates with the rest of AMD DC through the Display Mode Library API. Other DML files and generation-specific DC code use the selected clocks, watermarks, swath/DET geometry, DPP/ODM/DSC decisions, prefetch results, and validation status to decide whether a mode can be committed and how hubbub, hubp, dlg/ttu, dsc, dpp, dccg, and timing generator state should be programmed.

`display_rq_dlg_calc_20.c` consumes many of the final timing quantities through accessor functions such as `get_wm_urgent`, `get_clk_dcf_deepsleep`, `get_dst_y_prefetch`, `get_dst_y_per_vm_vblank`, `get_vratio_prefetch_l`, `get_dsc_delay`, and related DML accessors.

## Risks And Edge Cases

- This code relies heavily on nonzero divisors: clocks, bandwidths, ratios, swath widths, DET sizes, htotal, page sizes, pitch, DPP counts, DSC slices, and row heights. Some assertions exist, but many divisions assume validated inputs.
- Many arrays are indexed by `NumberOfActivePlanes`, `soc.num_states`, and `VoltageLevel`. If `VoltageLevel` remains `soc.num_states + 1` because no mode is valid, later indexing can become unsafe unless callers check validation before using selected outputs.
- Several helpers use `unsigned int` return types while manipulating fractional bpp values, especially `TruncToValidBPP`; this mirrors existing code but can silently truncate fractional DSC bpp semantics.
- `CalculateFlipSchedule` divides by `TotImmediateFlipBytes` when GPUVM/DCC immediate flip bytes are present. It depends on the caller's source-format filtering to avoid zero totals.
- `CalculateDelayAfterScaler` takes a `ReturnBW` argument but uses `mode_lib->vba.ReturnBW` internally, which makes it sensitive to the global selected state rather than the argument in candidate-state contexts.
- The state/combine prefetch pass reuses several `[0][0]` scratch arrays while iterating all `i,j` candidates. That is part of the inherited formula structure, but it is easy to break if refactored.
- DCC with 4:2:0 is rejected in support checks, but chroma/DCC-related paths still contain fallbacks and TODOs. Test coverage should include unsupported combinations to ensure they fail validation, not register programming later.
- ODM/DSC/image-width limits are hard-coded (`DCN20_MAX_DSC_IMAGE_WIDTH`, `DCN20_MAX_420_IMAGE_WIDTH`) and must match the DCN20v2 hardware guide.
- Numerous formulas use rounded fixed granularity and magic thresholds (`VRatioPrefetch <= 4`, VM lines `< 8`, row lines `< 16`, initial `VStartupLines = 13`). Regressions can appear as borderline validation changes rather than compile failures.

## Test Signals

- Build coverage for AMDGPU display should catch prototype/type drift with `display_mode_vba_20v2.h`, missing helper declarations, enum changes, and structure field renames.
- DML validation tests should cover valid and invalid combinations for scale ratios/taps, source tiling and scan, DCC, GPUVM page size, pitch alignment, cursor sizes, writeback modes, DSC input bpc, DP/HDMI/eDP link bpp, FEC, DSC unit count, DPP count, OTG count, and ODM combine.
- Golden-output tests are valuable for representative DCN20v2 modes: single RGB plane, YUV420 plane, DCC enabled, GPUVM enabled, writeback enabled, multiple planes sharing timing, MPC combine, ODM combine, DSC on DP/eDP, HDMI no-DSC, interlace/progressive-to-interlace, and XFC remote flip.
- Runtime signals include `ValidationStatus[]`, `ModeSupport[][]`, `PrefetchModeSupported`, `ImmediateFlipSupported`, `DRAMClockChangeSupport`, `DML_FAIL_*` values, `DTRACE` clock/watermark output, `dml_print` prefetch failures, and assertions on DFS VCO speed and register/timing bounds.
