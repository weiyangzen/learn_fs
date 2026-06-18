# subset-b-001406 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_mode_vba_21.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_mode_vba_21.c

## Purpose

This file is the DCN 2.1 Display Mode Library VBA implementation used by the AMDGPU display stack to validate a proposed display configuration and to derive clocks, pipe allocation, memory-fetch timing, watermark, DSC, DCC, GPUVM, immediate-flip, XFC, and stutter-efficiency parameters. The file is explicitly marked as "HW gospel" from hardware engineers and intentionally does not follow normal kernel style; changes carry high risk because the math encodes hardware programming guide behavior.

It exports two functions:

- `dml21_recalculate(struct display_mode_lib *mode_lib)`: recalculates derived values for an already selected mode state.
- `dml21_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)`: performs the full support search across voltage states and MPC-combine choices, then writes the selected configuration back into `mode_lib->vba`.

## Important APIs, types, and helpers

Local helper structs:

- `Pipe`: compact per-plane timing/pipeline view passed to `CalculatePrefetchSchedule()`. It carries DPP/DISP/pixel clocks, DPP count, scaler/source scan state, 256-byte block geometry, interlace/cursor/vblank/HTotal data.
- `HostVM`: compact host-VM view with enable flag, max page-table levels, and cached page-table levels.

Constants:

- `BPP_INVALID` and `BPP_BLENDED_PIPE` are sentinel output-BPP values.
- `DCN21_MAX_DSC_IMAGE_WIDTH` and `DCN21_MAX_420_IMAGE_WIDTH` drive ODM combine decisions for wide DSC or 4:2:0 outputs.

Major static helpers:

- `dscceComputeDelay()` and `dscComputeDelay()` compute DSC front-end and core pixel delays based on bpc, bpp, slices, slice width, and output format.
- `CalculatePrefetchSchedule()` is the central per-pipe scheduling routine. It computes scaler-output offsets, vupdate/vready timing, dynamic metadata timing, VM row request timing, prefetch bandwidth, prefetch ratios, required luma/chroma prefetch bandwidth, and register-bounded destination line counts. It returns an error flag and zeros dependent outputs on failure.
- `RoundToDFSGranularityUp()` and `RoundToDFSGranularityDown()` quantize clock values to DFS granularity from VCO speed.
- `CalculateDCCConfiguration()` selects DCC block/request characteristics and maximum compression surface factor from DCC enablement, tiling, bytes per pixel, scan orientation, swath height, and DET capacity.
- `CalculatePrefetchSourceLines()` derives source lines needed before active scanout, respecting interlace/progressive-to-interlace and optional viewport positioning.
- `CalculateVMAndRowBytes()` computes DCC metadata row bytes, pixel PTE bytes per row, PDE/meta PTE frame bytes, macro-tile geometry, PTE request shape, VM/DPTE group bytes, and PTE-buffer fit flags for luma/chroma planes.
- `DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` is the large post-selection recalculation body used by `dml21_recalculate()`.
- `DisplayPipeConfiguration()` derives swath heights and DET splits for the selected configuration.
- `CalculateTWait()`, `CalculateRemoteSurfaceFlipDelay()`, `CalculateWriteBackDelay()`, `CalculateActiveRowBandwidth()`, `CalculateFlipSchedule()`, `TruncToValidBPP()`, and `CalculatePrefetchSchedulePerPlane()` support state search and timing checks.
- `CalculateWatermarksAndDRAMSpeedChangeSupport()`, `CalculateDCFCLKDeepSleep()`, `CalculateDETBufferSize()`, `CalculateUrgentBurstFactor()`, `CalculatePixelDeliveryTimes()`, `CalculateMetaAndPTETimes()`, and `CalculateExtraLatency()` compute lower-level latency, buffer, metadata, and VM timing products.

The implementation also calls shared DML helpers from neighboring files, including `ModeSupportAndSystemConfiguration()`, `PixelClockAdjustmentForProgressiveToInterlaceUnit()`, `CalculateWriteBackDISPCLK()`, `Calculate256BBlockSizes()`, and `CalculateMinAndMaxPrefetchMode()`.

## Control flow

`dml21_recalculate()` runs a compact four-stage path:

1. Calls shared `ModeSupportAndSystemConfiguration(mode_lib)` to prepare baseline mode support/state information.
2. Calls `PixelClockAdjustmentForProgressiveToInterlaceUnit(mode_lib)`.
3. Calls `DisplayPipeConfiguration(mode_lib)` to compute swath heights and DET buffer splits for active planes.
4. Calls `DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation(mode_lib)` to compute clocks, bandwidths, prefetch, immediate flip, watermark, XFC, DCC, and stutter outputs.

`dml21_ModeSupportAndSystemConfigurationFull()` is the exhaustive validation path. It starts with global feasibility checks for scale ratio/taps, source format/scan/tiling/DCC combinations, bandwidth, writeback latency/mode/taps, ROB capacity, cursor, pitch, DIO/DSC/FEC, DSC unit count, viewport size, available pipes, OTG count, PTE-buffer fit, prefetch, immediate flip, and vertical-active bandwidth. It loops across SoC voltage states and two MPC-combine choices. For each candidate it derives required DISPCLK/DPPCLK, DPP split count, ODM combine state, swath geometry, DCFCLK deep sleep, VM/PTE/meta bytes, prefetch scheduling, urgent-burst factors, immediate-flip support, and watermarks.

The support search then assigns `ModeSupport[i][j]` and `ValidationStatus[i]` using ordered failure precedence. Finally it chooses the first valid voltage state from `VoltageOverrideLevel` upward, selects whether to use MPC combine based on support and `WhenToDoMPCCombine`, then writes selected `VoltageLevel`, `ImmediateFlipSupport`, `DPPPerPlane[]`, local `DPPCLK[]`, `DISPCLK`, `maxMpcComb`, `DCFCLK`, `DRAMSpeed`, `FabricClock`, `SOCCLK`, `ReturnBW`, `ODMCombineEnabled[]`, `DSCEnabled[]`, and `OutputBpp[]`.

`DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` assumes a selected state and computes final programming values. It computes writeback DISPCLK, per-plane scaler throughput and DPPCLK, DISPCLK rounding, global DPPCLK, swath widths, bytes per pixel, read bandwidth, DCFCLK deep sleep, DSCCLK/DSC delay, prefetch source lines, VM/PTE/meta row bytes, active row bandwidth, extra urgent latency, writeback delay, available vstartup, prefetch schedule iteration, immediate flip bandwidth/support, watermarks, pixel delivery times, meta/PTE times, min TTU vblank, DCC configuration, XFC parameters, and stutter efficiency.

## State and persistence behavior

The file has no persistent storage, no device register writes, and no heap allocation. All state is transient and stored in the caller-owned `struct display_mode_lib`, primarily `mode_lib->vba`. The functions mutate many scalar and array fields in place. Some local arrays live inside `struct vba_vars_st` and are reused as scratch and output storage, so callers must treat `mode_lib->vba` as the single state carrier.

Important mutation targets include support booleans and validation status, voltage/clock selections, DPP and ODM assignments, DSC enablement and output bpp, swath and DET sizes, bandwidth totals, urgent/stutter/DRAM watermarks, prefetch and immediate-flip line counts, XFC timing/fill levels, PTE/meta timing values, and DCC block metadata.

The code relies on pre-populated input fields in `mode_lib->vba` such as active plane count, timing, format, tiling, VM/DCC flags, cursor/writeback settings, SoC state tables, clock limits, memory bus properties, latency constants, and policy fields. There is little defensive validation for zero divisors or malformed inputs beyond support checks and a few assertions, so the surrounding DML setup code is responsible for sane initialization.

## Dependencies and integration points

Includes:

- `../display_mode_lib.h`: core DML library types and function table integration.
- `../dml_inline_defs.h`: math helpers such as `dml_max`, `dml_min`, `dml_ceil`, `dml_floor`, `dml_round`, and trace/print/assert helpers.
- `../display_mode_vba.h`: shared VBA routines used by DCN version implementations.
- `display_mode_vba_21.h`: public declarations for this DCN 2.1 implementation.

The file is integrated through `drivers/gpu/drm/amd/display/dc/dml/display_mode_lib.c`, where the DCN 2.1 function table maps `.validate` to `dml21_ModeSupportAndSystemConfigurationFull` and `.recalculate` to `dml21_recalculate`. It is part of the display-mode validation layer under AMD DC rather than a standalone driver component.

External consumers depend on the selected values written into `mode_lib->vba` to decide whether a display mode is legal and how to program display hardware clocks, DPP/ODM/DSC choices, watermarks, prefetch registers, VM row timing, and power-saving behavior.

## Risks and edge cases

- The calculations are dense hardware-derived formulas. Small arithmetic changes can silently reject valid modes, accept invalid modes, or generate timing/watermark values that cause underflow, flicker, hangs, or power regressions.
- There are many divisions by clock, bandwidth, line-time, swath, pitch, and page-size values. Incorrectly initialized inputs can produce divide-by-zero or nonsensical outputs; the file generally assumes upstream validation/setup.
- Mixed integer/double arithmetic and casts are pervasive. Rounding direction is hardware-visible because many values map to register granularity and buffer limits.
- `CalculatePrefetchSchedule()` has a large output surface and zeroes outputs on error. Callers must honor the returned error flag; stale values would be dangerous.
- The support-status precedence in `dml21_ModeSupportAndSystemConfigurationFull()` exposes only one final validation failure per state, so a later failure can be masked by an earlier one.
- The code contains TODO/comments where behavior may not match a programming guide exactly, especially around XFC remote surface flip delay and historical cursor/XFC prefetch handling.
- The code intentionally duplicates similar logic between full validation and recalculation paths. Fixes in one path can require careful mirrored updates in the other.
- Array bounds depend on `NumberOfActivePlanes`, SoC state counts, and DML maximums matching allocated `vba` arrays. No local bounds clamps are applied in these loops.
- Header declaration for `struct display_mode_lib` relies on prior inclusion of the core DML header by users; this is normal in-tree but fragile for standalone inclusion.

## Test signals

Useful validation signals include:

- Kernel build coverage for `drivers/gpu/drm/amd/display/dc/dml` with DCN 2.1 enabled.
- Existing DML unit or golden-vector tests, if available in the tree, comparing mode validation status, selected voltage state, clocks, DPP/ODM/DSC decisions, watermarks, prefetch lines, immediate-flip support, and stutter efficiency against known-good hardware spreadsheet/reference outputs.
- Mode-set regression tests covering HDMI, DP, eDP, DSC enabled/disabled, ODM combine, 4:2:0, 4:2:2, RGB/4:4:4, writeback enabled, DCC enabled, GPUVM/HostVM enabled, cursor-heavy modes, interlace/progressive-to-interlace, and XFC.
- Runtime smoke tests on DCN 2.1 hardware for high-bandwidth multi-display modes, wide DSC modes above `DCN21_MAX_DSC_IMAGE_WIDTH`, 4:2:0 modes above `DCN21_MAX_420_IMAGE_WIDTH`, immediate flips, vblank/self-refresh transitions, and DRAM clock change behavior.
- Trace/debug checks from `DTRACE` and `dml_print()` around calculated clocks, bandwidth violations, prefetch failures, DSC delay, VM/PTE bytes, and remote-surface flip delay.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_mode_vba_21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_mode_vba_21.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_mode_vba_21.h

## Purpose

This header is the public DCN 2.1 Display Mode Library VBA interface. It exposes the two entry points implemented in `display_mode_vba_21.c` so the common DML library can bind DCN 2.1 validation and recalculation callbacks.

## Important APIs and types

The header declares:

- `void dml21_recalculate(struct display_mode_lib *mode_lib);`
- `void dml21_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib);`

It does not define `struct display_mode_lib`; users are expected to include it in a context where the core DML headers have already declared the type. The include guard is `__DML21_DISPLAY_MODE_VBA_H__`.

## Control flow and integration

The header itself has no executable control flow. It is included by the DCN 2.1 implementation and by the common DML dispatch setup. In `display_mode_lib.c`, these functions populate the DCN 2.1 function table entries for `.validate` and `.recalculate`.

`dml21_ModeSupportAndSystemConfigurationFull()` is the full mode-validation/state-selection entry point. `dml21_recalculate()` is the recalculation path for a chosen state. Both operate on the mutable `mode_lib->vba` state block owned by the caller.

## State and persistence behavior

The header stores no state and declares no globals. State changes happen only through the implementation functions and the passed `struct display_mode_lib *`.

## Dependencies

This file has no direct includes besides its guard. Its declarations depend on `struct display_mode_lib` being visible to translation units that include it, usually through `display_mode_lib.h` or neighboring DML headers included first.

## Risks and edge cases

- Because the header does not include or forward-declare `struct display_mode_lib`, include order matters. In-tree usage appears to satisfy that ordering, but standalone inclusion would trigger compiler diagnostics.
- The closing comment uses `_DML21_DISPLAY_MODE_VBA_H_`, which differs from the actual guard macro `__DML21_DISPLAY_MODE_VBA_H__`; this is cosmetic but can confuse readers.
- Any signature change must be coordinated with `display_mode_lib.c` callback binding and all DCN 2.1 callers.

## Test signals

Relevant checks are compile-time rather than runtime:

- Build the DML objects that include this header.
- Confirm `display_mode_lib.c` resolves `dml21_ModeSupportAndSystemConfigurationFull` and `dml21_recalculate` for the DCN 2.1 function table.
- Confirm no standalone or reordered include path relies on this header to define `struct display_mode_lib`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn21/display_mode_vba_21.h -->
