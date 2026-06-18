# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_mode_vba_util_32.h

## Purpose
This header declares the DCN32 Display Mode Library utility surface used by the VBA-derived mode validation and bandwidth calculators. It is a broad math/API contract rather than an implementation file: callers feed SoC/IP limits, pipe geometry, timing, tiling, compression, VM, MALL, and link parameters, and receive derived clocks, swath/DET layout, request sizing, prefetch timings, watermarks, bandwidth support decisions, and register-facing timing quantities.

## Important APIs, Types, And Functions
The file depends on `display_mode_enums.h`, `dc_features.h`, `display_mode_structs.h`, and `display_mode_vba.h`, especially `DmlPipe`, `SOCParametersList`, `soc_bounding_box_st`, and `vba_vars_st`. API clusters are:

- DSC/link: `dml32_dscceComputeDelay`, `dml32_dscComputeDelay`, `dml32_CalculateOutputLink`, `dml32_TruncToValidBPP`, `dml32_RequiredDTBCLK`, and `dml32_DSCDelayRequirement`.
- Format and swath geometry: `IsVertical`, `dml32_CalculateBytePerPixelAndBlockSizes`, `dml32_CalculateSwathAndDETConfiguration`, `dml32_CalculateSwathWidth`, `dml32_UnboundedRequest`, `dml32_CalculateDETBufferSize`, and `dml32_CalculateDCCConfiguration`.
- Clock calculation: `dml32_CalculateSinglePipeDPPCLKAndSCLThroughput`, `dml32_CalculateODMMode`, `dml32_CalculateRequiredDispclk`, `dml32_RoundToDFSGranularity`, `dml32_CalculateDPPCLK`, `dml32_CalculateDCFCLKDeepSleep`, `dml32_UseMinimumDCFCLK`, and `dml32_CalculateWriteBackDISPCLK`.
- VM/PTE/meta timing: `dml32_CalculateSurfaceSizeInMall`, `dml32_CalculateVMRowAndSwath`, `dml32_CalculateVMAndRowBytes`, `dml32_CalculatePrefetchSourceLines`, `dml32_CalculateRowBandwidth`, `dml32_CalculateMetaAndPTETimes`, and `dml32_CalculateVMGroupAndRequestTimes`.
- Latency, prefetch, flip, and bandwidth gates: `dml32_CalculateUrgentLatency`, `dml32_CalculateUrgentBurstFactor`, `dml32_CalculateExtraLatencyBytes`, `dml32_CalculateExtraLatency`, `dml32_CalculateVUpdateAndDynamicMetadataParameters`, `dml32_CalculateTWait`, `dml32_CalculatePrefetchSchedule`, `dml32_CalculateFlipSchedule`, `dml32_CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport`, `dml32_CalculateVActiveBandwithSupport`, `dml32_CalculatePrefetchBandwithSupport`, `dml32_CalculateBandwidthAvailableForImmediateFlip`, `dml32_CalculateImmediateFlipBandwithSupport`, and `dml32_CalculateDETSwathFillLatencyHiding`.

## Control Flow And State
There is no local control flow or persistent state in this header. The declared functions are called by DCN32 DML validation and recalculation code to populate `vba_vars_st` and per-pipe derived arrays, then downstream RQ/DLG code reads those derived values to pack hardware register fields. Most APIs follow a large input-array plus output-pointer pattern, with array dimensions tied to `DC__NUM_DPP__MAX`, `DC__NUM_PIPES__MAX`, or active surface counts.

## Dependencies And Integration Points
The contract bridges high-level display validation and low-level hardware programming. It consumes enums for source/output formats, rotations, MALL policy, ODM policy, prefetch modes, flip requirements, and clock-change support. It integrates with `dcn32/display_rq_dlg_calc_32.c`, which reads VBA helper values produced by these calculations; with `display_mode_lib.c`, which binds DCN32 validation/recalculation; and with ASIC FPU files that seed `soc_bounding_box_st`/`ip_params_st`.

## Risks
The risk surface is high because the APIs encode hardware timing and register assumptions through untyped arrays and many parallel output buffers. Dimension mismatches, wrong enum families, stale SoC limits, or caller-provided arrays in the wrong pipe/surface order can silently produce invalid bandwidth or register values. Many outputs are fixed-point or hardware-limited quantities used later with asserts/clamps, so precision and rounding changes require hardware-oriented regression coverage.

## Test Signals
Useful test signals are DML validation pass/fail status, RQ/DLG register dumps, display underflow/flip failures, DSC link-mode selection, MALL/pstate/stutter decisions, and comparisons against known spreadsheet/VBA reference vectors for DCN32 modes. Edge cases should include dual-plane 4:2:0/RGBE alpha, rotated surfaces, ODM combine, DSC, immediate flip, HostVM/GPUVM, MALL static and pstate-change modes, and low-vblank/high-refresh timings.
