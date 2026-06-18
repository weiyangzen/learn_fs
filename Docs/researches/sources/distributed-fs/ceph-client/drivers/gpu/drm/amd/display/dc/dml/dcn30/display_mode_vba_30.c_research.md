# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn30/display_mode_vba_30.c

## Purpose

`display_mode_vba_30.c` is the DCN 3.0 Display Mode Library VBA implementation used by AMD Display Core to validate a proposed display configuration and derive the clocks, pipe splits, bandwidth budgets, prefetch timing, watermarks, DSC/link settings, DCC/DET layout, VM/PTE timing, and stutter/self-refresh metrics needed by later hardware programming. It is explicitly treated as hardware-sourced "gospel": the comment near the top warns that the code is generated or supplied by hardware engineers, is not Linux-style, and should only be changed for clear correctness issues.

The file is stateful but not persistent: it reads and writes `mode_lib->vba`, a large scratch/result structure shared by the DML pipeline. `dml30_recalculate()` runs the selected-state calculation path, while `dml30_ModeSupportAndSystemConfigurationFull()` performs the full feasibility search across voltage states and MPC-combine options.

## Important APIs, Types, And Functions

- `typedef Pipe`: local per-plane snapshot passed into prefetch scheduling. It carries DPP/DISP/pixel clocks, DPP split count, scaler/cursor state, scan direction, block sizes, blanking, DCC, interlace, and ODM-combine state.
- `dml30_recalculate(mode_lib)`: exported recalculation entry. It invokes generic DML support setup, progressive-to-interlace pixel-clock adjustment, local display-pipe configuration, and final clock/prefetch/watermark calculation.
- `dml30_ModeSupportAndSystemConfigurationFull(mode_lib)`: exported full mode-support solver. It tests scaler/tap constraints, source/scan compatibility, writeback, clocks, pipe resources, DSC/DIO, bandwidth, ROB, prefetch, immediate flip, PTE buffer size, cursor, pitch, viewport bounds, and chooses selected clock/resource state.
- `dml30_CalculateBytePerPixelAnd256BBlockSizes(...)`: exported format/tiling helper for luma/chroma bytes per pixel and 256-byte block dimensions.
- `dml30_CalculateWriteBackDISPCLK(...)`: exported writeback clock helper that computes the max of horizontal, vertical, and line-buffer-limited writeback DISPCLK needs.
- Major private helpers cover DSC delay/BPP, prefetch and flip scheduling, DCC/VM/PTE row geometry, swath and DET configuration, DCFCLK deep sleep, urgent burst factors, watermarks, pixel delivery times, meta/PTE times, VM request times, stutter efficiency, extra latency, urgent latency, and minimum required DCFCLK.

## Control Flow

`dml30_recalculate()` is the selected-state path. It calls common DML functions outside this file, then `DisplayPipeConfiguration()` to compute bytes-per-pixel, swath heights, and DET splits for the current selected topology, then `DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` to compute the current-state output values.

The final calculation function recomputes return bandwidth, writeback DISPCLK, PSCL throughput, DPPCLK/DISPCLK, bytes/block sizes, swath widths, active read bandwidth, DCFCLK deep sleep, DSCCLK, DSC delay, VM/PTE/meta bytes, prefetch source lines, row bandwidth, urgent extra latency, writeback delay, maximum VStartup, final urgent latency, prefetch/immediate-flip feasibility, watermarks, pixel delivery times, meta/PTE times, VM group/request times, DCC block configuration, total read bandwidth, VStartup margin, and stutter efficiency.

`dml30_ModeSupportAndSystemConfigurationFull()` is the broad feasibility pass. It checks scaler ratios/taps, source format and scan direction, active read/write bandwidth, writeback units/mode/latency/taps, minimum DPPCLK, maximum swath width, single-DPP viewport support, voltage-state clock support, DPP/ODM/MPC topology, pipe resource count, DIO/DSC/FEC support, DSC delay, per-state swath/DET, row/meta/PTE bytes, urgent burst factors, DCFCLK deep sleep, return bandwidth, ROB support, vertical-active bandwidth, prefetch, dynamic metadata, VRatio prefetch, immediate flip, PTE buffers, cursor, pitch, and viewport bounds. The final mode-support predicate is a conjunction of those flags, and the best supported voltage/MPC-combine state is copied back into selected fields.

`CalculatePrefetchSchedule()` is the densest routine. It models dynamic metadata setup, scaler/DISP/DSC pipeline delay, VM walks, row fetches, one-to-one and equalized prefetch schedules, vblank line allocation for VM and meta/DPTE rows, luma/chroma prefetch ratios, prefetch pixel bandwidth, and VM/row bandwidth. It returns an error when timing or bandwidth cannot be allocated.

## State And Persistence Behavior

There is no on-disk persistence and no allocation ownership in this file. The persistent working state is the caller-owned `struct display_mode_lib`, especially `mode_lib->vba`.

The file mutates mode-selection fields, clock results, memory-layout fields, timing and bandwidth fields, watermark and TTU fields, DCC programming fields, stutter metrics, and many support/failure flags. Because `mode_lib->vba` is reused across calculations, callers must treat the functions as ordered passes rather than independent stateless helpers.

## Dependencies And Integration Points

The file includes `dc.h`, `../display_mode_lib.h`, `display_mode_vba_30.h`, and `../dml_inline_defs.h`. It depends on DML math helpers/macros, `ASSERT`, `DTRACE`, `dml_print`, and common DML routines such as `ModeSupportAndSystemConfiguration()`, `PixelClockAdjustmentForProgressiveToInterlaceUnit()`, and `CalculateMinAndMaxPrefetchMode()`.

The main external data contract is `struct vba_vars_st`, which supplies active display timings, source formats, scaling ratios, cursor state, writeback state, DSC/link settings, DCC/GPUVM/HostVM settings, SoC clock/bandwidth tables, resource limits, and debug policy fields. Higher layers consume the selected clocks, topology, watermarks, VM request timing, DCC limits, immediate-flip support, and DRAM clock-change support for commit planning and hardware programming.

## Risks And Edge Cases

- The file is algorithmically fragile and hardware-derived; small arithmetic changes can alter validation, clocks, and watermarks across many topologies.
- Many calculations divide by clocks, ratios, bandwidths, swath widths, and block dimensions. Inputs must be nonzero and internally consistent.
- `mode_lib->vba` scratch fields are reused across nested voltage/MPC/prefetch loops, so stale values are a risk if call ordering changes.
- GPUVM plus HostVM paths multiply VM/PTE bytes and latency by host dynamic levels and efficiency ratios.
- Prefetch scheduling is bounded by hardware register limits: `DST_Y_PREFETCH` clamping, VM lines under 32, row lines under 16, destination prefetch lines at least 2, and VRatio prefetch no more than 4.
- DSC and output BPP logic depends on link rate, lanes, DSC BPC, slice counts, ODM combine, and output format.
- Generated-like style, dummy variables, and `noinline_for_stack` should not be mechanically cleaned up without validation.

## Test Signals

- Build tests for AMDGPU/DC DML should catch declaration mismatches, enum/type drift, and stack/layout issues.
- Golden DML vectors should cover single/multi-plane, 4:4:4 and 4:2:0, RGBE alpha, linear/tiled swizzles, horizontal/vertical scan, DCC, GPUVM/HostVM, writeback, DSC, HDMI/DP/eDP, ODM 2:1/4:1, MPC split, immediate flip, and dynamic metadata.
- Regression checks should compare selected voltage, DPP count, MPC/ODM combine, required clocks, return bandwidth, prefetch mode, watermarks, DRAM clock-change support, stutter efficiency, and mode-support flags.
- Boundary tests should target DSC image-width limits, 4:2:0 buffer limits, VM/row line register limits, VStartup exhaustion, PTE buffer exhaustion, cursor 64 bpp support, pitch alignment failures, and viewport larger than surface.
