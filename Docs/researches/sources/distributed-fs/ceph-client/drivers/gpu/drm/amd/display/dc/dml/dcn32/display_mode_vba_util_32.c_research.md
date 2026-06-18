# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_mode_vba_util_32.c

## Purpose

`display_mode_vba_util_32.c` is the DCN 3.2 Display Mode Library utility implementation used by AMDGPU display-mode validation and programming calculations. It is a large collection of pure numerical helper routines for the DCN32 VBA model: DSC/link timing, DPP/DISPCLK/DCFCLK clocks, swath and DET sizing, MALL use, GPUVM/DCC metadata request geometry, prefetch and flip schedules, watermarks, stutter efficiency, and bandwidth-support checks.

The file does not drive hardware directly. Instead, it transforms mode, surface, SoC, memory, virtual-memory, compression, rotation, scaling, and output-link inputs into support flags, clock requirements, buffer sizes, watermarks, request timings, and bandwidth numbers consumed by the main DCN32 mode-support code in `display_mode_vba_32.c`.

## Important APIs, Types, And Function Groups

The public surface is declared in `display_mode_vba_util_32.h`; every major function takes scalar inputs plus output pointers or per-surface arrays. Important dependent types come from the DML display headers:

- `struct vba_vars_st`: main VBA model state; used by prefetch, watermark, and DCFCLK routines.
- `DmlPipe`: per-pipe surface/timing/scaler state passed into VM and prefetch helpers.
- `SOCParametersList` and `soc_bounding_box_st`: SoC latency, bandwidth, return-bus, fabric, DRAM, and percentage-efficiency inputs.
- Enums such as `source_format_class`, `output_format_class`, `output_encoder_class`, `dm_swizzle_mode`, `dm_rotation_angle`, `odm_combine_mode`, `dm_use_mall_for_pstate_change_mode`, `dm_prefetch_modes`, `clock_change_support`, and `dm_fclock_change_support`.

Major function groups:

- DSC and link:
  - `dml32_dscceComputeDelay`, `dml32_dscComputeDelay`, `dml32_DSCDelayRequirement`
  - `dml32_CalculateOutputLink`, `dml32_TruncToValidBPP`, `dml32_RequiredDTBCLK`
- Clocking:
  - `dml32_CalculateSinglePipeDPPCLKAndSCLThroughput`
  - `dml32_CalculateDPPCLK`, `dml32_CalculateRequiredDispclk`, `dml32_RoundToDFSGranularity`
  - `dml32_CalculateDCFCLKDeepSleep`, `dml32_UseMinimumDCFCLK`
  - `dml32_CalculateWriteBackDISPCLK`, `dml32_CalculateWriteBackDelay`
- Format, swath, DET, and compression buffer geometry:
  - `dml32_CalculateBytePerPixelAndBlockSizes`
  - `dml32_CalculateSwathAndDETConfiguration`, `dml32_CalculateSwathWidth`
  - `dml32_UnboundedRequest`, `dml32_CalculateDETBufferSize`
  - `dml32_CalculateMaxDETAndMinCompressedBufferSize`
- ODM and output pipe allocation:
  - `dml32_CalculateODMMode`
- MALL, VM, PTE, and DCC metadata:
  - `dml32_CalculateSurfaceSizeInMall`, `dml32_CalculateMALLUseForStaticScreen`
  - `dml32_CalculateVMRowAndSwath`, `dml32_CalculateVMAndRowBytes`
  - `dml32_CalculateRowBandwidth`, `dml32_CalculateMetaAndPTETimes`, `dml32_CalculateVMGroupAndRequestTimes`
  - `dml32_CalculateDCCConfiguration`
- Latency, prefetch, flip, and watermarks:
  - `dml32_CalculateUrgentLatency`, `dml32_CalculateUrgentBurstFactor`
  - `dml32_CalculateExtraLatencyBytes`, `dml32_CalculateExtraLatency`
  - `dml32_CalculateVUpdateAndDynamicMetadataParameters`, `dml32_CalculateTWait`
  - `dml32_CalculatePrefetchSchedule`, `dml32_CalculateFlipSchedule`
  - `dml32_CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport`
- Delivery-time and support predicates:
  - `dml32_CalculatePixelDeliveryTimes`
  - `dml32_CalculateStutterEfficiency`
  - `dml32_CalculateVActiveBandwithSupport`, `dml32_CalculatePrefetchBandwithSupport`
  - `dml32_CalculateBandwidthAvailableForImmediateFlip`, `dml32_CalculateImmediateFlipBandwithSupport`
  - `dml32_CalculateDETSwathFillLatencyHiding`

`IsVertical` is a shared orientation helper used throughout swath, VM, DCC, delivery-time, and stutter calculations.

## Control Flow And Core Calculations

The file is organized as a toolbox rather than a single top-level algorithm. `display_mode_vba_32.c` orchestrates the mode-validation phases and calls these helpers repeatedly across voltage states, prefetch modes, surfaces, and pipes.

The early pipeline determines link and pixel-processing feasibility. DSC functions compute encoder and DSCC delay in pixels, accounting for bpc, bits-per-pixel, slice width/count, pixel format, ODM split/combine, and blanking expansion. Link selection tries HDMI, DP/eDP, and DP2 rates in increasing capability order, calls `dml32_TruncToValidBPP`, and sets DSC/FEC, output type/rate, output bpp, and required DP slots. DISPCLK and DPPCLK routines round requested clocks to DFS granularity and fan out a global DPPCLK to per-surface DPP clocks.

Surface geometry starts with `dml32_CalculateBytePerPixelAndBlockSizes`, which maps DML source formats and tiling modes to luma/chroma bytes per pixel, DET byte accounting, 256-byte block sizes, and macro-tile dimensions. Swath width then follows source rotation, viewport stationarity, ODM combining, DPP-per-surface, blend/timing ownership, YUV420 chroma halving, and block rounding. `dml32_CalculateSwathAndDETConfiguration` combines the swath geometry with ROB/compressed-buffer policy, decides whether unbounded requests are legal, sizes DET per pipe, splits DET between luma/chroma, and reports viewport-size support.

DET allocation is multi-stage. For unbounded request mode, only the first surface is allocated enough DET to fit two swaths, and the compressed buffer uses the remainder. Otherwise, each non-phantom surface receives a minimum DET allocation sufficient for swaths when possible, optional overrides are honored, and remaining DET is redistributed based on read bandwidth while respecting nominal per-pipe limits. Compressed-buffer size is then quantized by the final segment size.

MALL and VM calculations compute cache footprint and metadata/PTE request geometry. `dml32_CalculateSurfaceSizeInMall` estimates luma/chroma and DCC metadata bytes for stationary and non-stationary viewports, then checks static-screen and SubVP footprints separately against allocated MALL. `dml32_CalculateVMRowAndSwath` invokes `dml32_CalculateVMAndRowBytes` for luma and chroma, computes prefetch source lines, chooses one-row-per-frame behavior for forced, static-screen, SubVP, phantom, and large-page cases, checks PTE and DCC metadata buffers, and derives row bandwidths.

`dml32_CalculateVMAndRowBytes` is the central VM geometry routine. It determines metadata request width/height, metadata row width/height, metadata row bytes, metadata PTE bytes, PDE bytes, DPDE bytes, PTE request size, PTE request width/height, one-row-per-frame values, DPTE row height/width, and per-row PTE bytes. Branches depend on linear versus tiled surfaces, vertical versus non-vertical rotation, viewport stationarity, DPP count, GPUVM/HostVM enablement, page-table levels, and GPUVM page size.

Prefetch scheduling is one of the densest flows. `dml32_CalculatePrefetchSchedule` first calculates dynamic metadata timing and scaler/DSC/ODM output delay, then derives memory-trip latencies for VM and row fetches. It compares "oto" and "equ" prefetch schedules, computes candidate prefetch bandwidth formulas, chooses a candidate based on VM/row timing constraints, converts VM and row fetch time to destination-line counts, calculates prefetch luma/chroma ratios and required pixel-data bandwidth, and returns an error flag after zeroing outputs when there is not enough usable prefetch time.

Watermark and clock-change support calculations mutate `v->Watermark`, calculate urgent, USR retraining, DRAM, FCLK, stutter, Z8, and writeback watermarks, then compare line-buffer plus DET latency hiding against those watermarks. They classify DRAM clock-change support as vactive, vblank, MALL full-frame, MALL SubVP, or unsupported; classify FCLK support; compute SubVP lines needed in MALL; and return per-surface active DRAM latency margins.

Stutter efficiency first derives compressed and row bandwidths, effective compression rates, zero-size-request behavior, and effective compressed-buffer capacity. It then selects the critical surface with the shortest DET buffering period, computes burst time needed to refill data and row requests, derives SR and Z8 efficiencies and burst counts, accounts for synchronized timings and vblank, and sets `DCHUBBUB_ARB_CSTATE_MAX_CAP_MODE` from a specific single-surface double-plane/double-pipe chunk-alignment case.

The final support predicates aggregate bandwidth across active, prefetch, and immediate-flip scenarios. They apply urgent burst factors, cursor bandwidth, metadata/PTE row bandwidth, prefetch VM/row bandwidth, final flip bandwidth, and return bandwidth to produce boolean support flags and urgent-bandwidth fractions.

## State And Persistence Behavior

This file has no file I/O, no static mutable state, no locks, no heap allocation, and no persistent storage. It is deterministic for a given set of scalar, array, and struct inputs, subject to floating-point rounding behavior.

State mutation occurs through:

- Explicit output pointers and output arrays supplied by callers.
- In-place updates to selected fields of `struct vba_vars_st`, most notably `v->Watermark` and arrays read from `v`.
- Debug-only printing under `__DML_VBA_DEBUG__`.

The functions assume caller-owned arrays are sized for at least `NumberOfActiveSurfaces` or DCN maximum constants such as `DC__NUM_DPP__MAX`. Most outputs are fully assigned on successful paths, but callers still need to respect function-specific preconditions, especially nonzero clocks, dimensions, ratios, and bandwidth denominators.

## Dependencies And Integration Points

Direct includes:

- `display_mode_vba_util_32.h`: function declarations and enum/struct imports.
- `../dml_inline_defs.h`: math helpers such as `dml_min`, `dml_max`, `dml_ceil`, `dml_floor`, `dml_round`, `dml_log2`, and multi-argument min/max helpers.
- `display_mode_vba_32.h`: DCN32 VBA state and constants used by the main model.
- `../display_mode_lib.h`: shared DML library definitions.

Key constants and macros include `DCN32_MAX_FMT_420_BUFFER_WIDTH`, `DC__NUM_DPP__MAX`, `DC__VOLTAGE_STATES`, `DC__NUM_CURSOR__MAX`, `BPP_INVALID`, `__DML_MIN_DCFCLK_FACTOR__`, `__DML_ARB_TO_RET_DELAY__`, `__DML_VBA_MAX_DST_Y_PRE__`, `__DML_MAX_VRATIO_PRE__`, and `__DML_MAX_BW_RATIO_PRE__`.

The main integration point is `display_mode_vba_32.c`, which calls these utilities during:

- mode-support and system-configuration validation;
- clock selection for DISPCLK, DPPCLK, DCFCLK, DTBCLK, and writeback DISPCLK;
- output-link capability checks;
- swath, DET, and compressed-buffer sizing;
- VM/PTE/DCC metadata sizing;
- prefetch, flip, watermark, and stutter calculations;
- final bandwidth-support predicates per voltage and prefetch state.

The computed outputs ultimately influence whether a display mode is accepted and what clock/buffer/watermark programming values the AMD display stack derives for DCN32 hardware.

## Risks And Edge Cases

- Many formulas intentionally mirror the original VBA spreadsheet/model. Small changes to rounding, integer-vs-floating arithmetic, or order of operations can change mode-support decisions.
- Several calculations divide by clocks, ratios, bandwidths, row heights, swath widths, or active-surface totals. The caller is expected to provide valid nonzero mode inputs.
- `dml32_CalculatePrefetchSchedule` has many interdependent outputs; on `MyError` it clears the main schedule and bandwidth outputs, so callers must treat the returned boolean as authoritative.
- HostVM scaling multiplies VM/PTE byte counts by dynamic-level factors. Incorrect HostVM minimum page-size thresholds can over- or under-estimate memory-trip latency.
- Rotation and viewport-stationary branches affect swath, metadata, and PTE row dimensions. Misclassified rotation changes whether width or height is rounded and can produce wrong buffer-fit conclusions.
- DET and compressed-buffer allocation relies on per-surface bandwidth shares and DPP counts. Override values and phantom pipes can produce zero or atypical allocations that downstream formulas must handle.
- DCC and stutter efficiency rely on compression-rate and zero-size-request assumptions. Invalid or extreme DCC rates can create divide-by-zero or unrealistic effective-buffer values.
- Some function names use the existing `Bandwith` spelling. Renaming them would require coordinated header and caller changes.
- Debug format strings sometimes print floating values with integer-like labels; they are debug-only but can mislead when diagnosing precision-sensitive behavior.

## Test Signals

Useful validation signals for changes to this file:

- Build the AMDGPU display subtree with DCN32 DML enabled and treat warnings in this file as regressions.
- Run existing DML/display mode validation suites, especially any golden-output tests comparing clock, bandwidth, watermark, and support decisions.
- Exercise representative mode matrices:
  - RGB/444, RGBE, RGBE alpha, 420 8/10/12, n422, and mono formats.
  - Linear, 64KB, and larger tiling modes.
  - 0/90/180/270 and mirrored rotations.
  - one and multiple active surfaces, blended surfaces, ODM 2:1/4:1, MSO/split modes, and writeback.
  - GPUVM off/on, HostVM off/on, 4KB/64KB/large GPUVM pages, DCC on/off, MALL static screen, SubVP, full-frame, and phantom-pipe modes.
  - HDMI, DP, eDP, DP2 UHBR10/UHBR13.5/UHBR20, forced BPP, DSC enabled/disabled, and FEC requirements.
- Check edge-mode outputs for monotonicity and boundaries: BPP truncation, DFS clock rounding, DET fits two swaths, PTE/DCC metadata buffer flags, prefetch destination-line counts, immediate-flip support, DRAM/FCLK support classification, and stutter efficiency staying finite and within expected percentage ranges.
- For precision-sensitive changes, compare before/after dumps from `__DML_VBA_DEBUG__` on the same mode set, focusing on rounding points in DFS granularity, VM/PTE row sizes, prefetch candidate bandwidths, and compressed-buffer/stutter calculations.
