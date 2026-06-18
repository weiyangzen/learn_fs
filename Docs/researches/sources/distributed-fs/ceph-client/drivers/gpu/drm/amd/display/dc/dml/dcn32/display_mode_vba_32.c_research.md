# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn32/display_mode_vba_32.c

## Purpose

`display_mode_vba_32.c` is the DCN 3.2 Display Mode Library (DML) VBA-derived mode support and mode programming implementation. It validates whether a proposed display configuration can be supported by a DCN32 display engine, chooses the minimum supported voltage/state and MPC combination, and computes the clock, bandwidth, prefetch, immediate flip, watermark, MALL, DET, DCC, VM/PTE, and stutter-efficiency parameters stored in `struct display_mode_lib::vba`.

The file is not a general utility library. It is the DCN32 generation-specific solver plugged into the DML dispatch table. It depends on the caller having populated `mode_lib->vba` with SoC bounding-box values, IP capabilities, timing, surface, output-link, writeback, MALL, VM, and policy inputs. Almost all results are returned by mutating fields and arrays under `mode_lib->vba`.

## Important APIs, Types, And Functions

- `dml32_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)` is the public validation entry point. It computes support booleans for scale ratios, source formats, writeback, link/DSC/DTBCLK, pipe allocation, ODM/MPC, DET/swath buffers, VM row bytes, return bandwidth, ROB, vertical active bandwidth, prefetch, dynamic metadata, immediate flip, watermarks, cursor, pitch, and MALL combinations. It then calls `mode_support_configuration()` to combine those gates into `ModeSupport[i][j]`, selects `VoltageLevel` and `maxMpcComb`, and copies the chosen state into current programming outputs such as `DCFCLK`, `DRAMSpeed`, `FabricClock`, `SOCCLK`, `ReturnBW`, `DISPCLK`, `DPPPerPlane`, `MPCCombineEnable`, `ODMCombineEnabled`, `DSCEnabled`, `FECEnable`, `OutputBpp`, and selected watermarks.
- `dml32_recalculate(struct display_mode_lib *mode_lib)` is the public recalculate/programming path. It first calls the generic `ModeSupportAndSystemConfiguration(mode_lib)` wrapper, recalculates maximum DET and compressed buffer sizing with `dml32_CalculateMaxDETAndMinCompressedBufferSize()`, applies `PixelClockAdjustmentForProgressiveToInterlaceUnit()`, then invokes the static runtime calculation routine for the selected state.
- `DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` is a large static mode-programming calculation. It recomputes selected-state clocks, DPPCLKs, byte/block sizes, swath widths, DET allocation, DCFCLK deep sleep, DSC clocks/delay, MALL surface sizes, VM row and swath metadata, urgent latency, prefetch schedule, immediate flip schedule, watermarks, delivery times, metadata/PTE timing, DCC programming, TTU/vstartup timing, total read/write bandwidth, and stutter efficiency.
- `mode_support_configuration(struct vba_vars_st *v, struct display_mode_lib *mode_lib)` is the final support gate combiner. It iterates voltage states and the two MPC-combine choices and sets `ModeSupport[i][j]` only if all previously computed capability and bandwidth checks pass.
- The main shared type is `struct vba_vars_st`, reached as `mode_lib->vba`; it contains all scalar inputs, policy settings, current selected outputs, and multi-dimensional intermediate matrices. The implementation also uses `DmlPipe`, `SOCParametersList`, and dummy scratch structs/arrays under `v->dummy_vars`.

## Control Flow

The validation path in `dml32_ModeSupportAndSystemConfigurationFull()` starts by choosing `start_state`: state 0 normally, or only the highest state when `mode_lib->validate_max_state` is set. It validates scaler ratios/taps and source tiling/scan constraints, calculates bytes-per-pixel and block geometry for each active surface, computes read/write bandwidth, and checks writeback latency, writeback unit count, and writeback scaler constraints.

The next phase computes per-surface DPP throughput, maximum swath widths, and a single-DPP DET/swath baseline. It detects incompatible MPC policies, then loops over voltage states `i` and MPC-combine choices `j` to calculate ODM mode, output link requirements, DSC/FEC/BPP, DPP counts, required DISPCLK and DPPCLK, total active DPP count, and pipe availability. If `j == 1` and unbounded request is not available, it opportunistically combines the highest-bandwidth non-combined surfaces until DPP capacity or single-DPP surfaces are exhausted.

The file then performs global display I/O and DSC checks: OTG/DP2.0/HDMI FRL counts, DSC input BPC, multistream slot limits, link capacity, incompatible DP link-rate declarations, MST-over-HDMI/eDP invalid cases, MSO/ODM split restrictions, DTBCLK, ODM+link support, DSC clock, DSC units, and DSC slices. For each state/MPC combination it calculates DSCDelay, swath/DET state snapshots, MALL surface sizes, VM/PTE row metadata, PTE/DCC meta buffer fit, urgent latency, urgent burst factors, DCFCLK deep sleep, writeback delay, maximum vstartup, optional minimum DCFCLK, return bandwidth, ROB support, and vertical active bandwidth support.

The prefetch-support loop is the densest state search. For each state and MPC choice it restores that state's swath/DET/DPP values, calculates active-bandwidth support and DET swath fill latency hiding, computes extra latency and host-VM inefficiency, then iterates `PrefetchModePerState[i][j]` and `MaxVStartup`. For each surface it builds a `DmlPipe`, calls `dml32_CalculatePrefetchSchedule()`, computes prefetch urgent burst factors, checks prefetch bandwidth, rejects too few prefetch lines, too many VM/PTE lines, too high prefetch ratios, no-time-for-prefetch, and dynamic metadata timing failures. If prefetch is viable, it calculates immediate flip bandwidth and per-pipe flip schedules. The loop exits when prefetch, dynamic metadata, vratio, and immediate flip/host-VM requirements are satisfied, or when all prefetch modes are exhausted.

After cursor, pitch, and viewport checks, `mode_support_configuration()` combines all gates into `ModeSupport`. The final selection walks states from `v->soc.num_states` down to `start_state`; when any state/MPC entry is supported, it updates the selected `VoltageLevel`, `ModeIsSupported`, and `MaximumMPCCombine`. The selected state is then copied from per-state matrices into current programming fields.

The recalculate path is shorter but performs a full selected-state recomputation. `DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation()` computes final DISPCLK/DPPCLK/writeback clocks, byte/block sizes, swath widths, selected DET layout, DCFCLK deep sleep, DSC clocks and delays, immediate flip eligibility, MALL size, VM row/PTE data, return-bandwidth inefficiency, urgent and writeback latencies, max vstartup, prefetch mode and schedule, immediate flip schedule, watermarks, pixel/PTE/VM delivery timings, MinTTUVBlank, DCC configuration, vstartup adjustment, read/write bandwidth, and stutter efficiency.

## State And Persistence Behavior

There is no independent persistence, allocation, reference counting, I/O, or hardware programming in this file. Persistence is entirely through mutations of `mode_lib->vba`. The code writes many per-surface arrays, per-state arrays, and selected-current outputs:

- Per-state matrices: examples include `ModeSupport`, `ModeIsSupported`, `RequiredDISPCLK`, `RequiredDPPCLK`, `NoOfDPP`, `MPCCombine`, `ODMCombineEnablePerState`, `ReturnBWPerState`, `DCFCLKState`, `PrefetchModePerState`, `PrefetchSupported`, `ImmediateFlipSupportedForState`, `DRAMClockChangeSupport`, `FCLKChangeSupport`, `USRRetrainingSupport`, `SwathWidth*AllStates`, `SwathHeight*AllStates`, and `DETBufferSize*AllStates`.
- Per-surface selected outputs: examples include `DPPPerPlane`, `MPCCombineEnable`, `SwathHeightY/C`, `DETBufferSizeY/C`, `ODMCombineEnabled`, `DSCEnabled`, `FECEnable`, `OutputBpp`, `VStartup`, `MinTTUVBlank`, `DCC*Block`, `ReadBandwidthSurface*`, and delivery-time arrays.
- Selected global outputs: examples include `VoltageLevel`, `maxMpcComb`, `DCFCLK`, `DRAMSpeed`, `FabricClock`, `SOCCLK`, `ReturnBW`, `DISPCLK`, `DCFCLKDeepSleep`, `UrgentWatermark`, `DRAMClockChangeWatermark`, `Stutter*Watermark`, `StutterEfficiency`, and `ModeIsSupported`.

Because the code uses many dummy scratch arrays under `v->dummy_vars`, callers must treat `mode_lib->vba` as a mutable working area, not as immutable input. Reentrancy is limited to one caller per `display_mode_lib` instance; concurrent use of the same instance would race through shared `vba` scratch and output fields.

## Dependencies And Integration Points

The file includes `dc.h`, `display_mode_lib.h`, `display_mode_vba_32.h`, `dml_inline_defs.h`, and `display_mode_vba_util_32.h`. It relies heavily on DC/DML enums and helpers such as `dm_odm_combine_mode_*`, `dm_mpc_*`, `dm_use_mall_*`, `dm_dram_clock_change_*`, output/link/pixel-format enums, `IsVertical()`, `dml_max*`, `dml_min*`, `dml_ceil()`, and `dml_floor()`.

Most formulas are delegated to DCN32 utility functions in `display_mode_vba_util_32.c`, including clock/throughput helpers, surface/layout helpers, link/DSC helpers, bandwidth/latency helpers, and schedule/watermark helpers such as `dml32_CalculatePrefetchSchedule()`, `dml32_CalculateFlipSchedule()`, `dml32_CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport()`, and `dml32_CalculateStutterEfficiency()`.

The integration registration is in `display_mode_lib.c`, where the DCN32 function table assigns `.validate = dml32_ModeSupportAndSystemConfigurationFull` and `.recalculate = dml32_recalculate`. The object is built through the DML makefile entry for `dcn32/display_mode_vba_32.o`. DCN32 FPU code includes the header, so this solver participates in AMD display mode validation and programming calculations rather than standalone driver I/O.

## Risks And Edge Cases

- The implementation is extremely stateful. A missed initialization or stale array entry can affect later state/MPC choices because many loops reuse `mode_lib->vba` arrays as both intermediate and final storage.
- Several loops use `NumberOfActiveSurfaces - 1` style unsigned bounds. The normal DML contract likely requires at least one surface; zero active surfaces would be risky.
- The selected voltage-state loop starts from `v->soc.num_states` and indexes `ModeSupport[i]` only after checking `i == v->soc.num_states`. This sentinel-like pattern is intentional but fragile if rearranged.
- In both validation and recalculate paths, immediate flip support is tied to host VM. If `HostVMEnable` is true, flip support is needed for invalidation even without a user-visible immediate flip requirement.
- MALL P-state combinations are constrained: sub-viewport and phantom-pipe methods must appear together, and full-frame cannot be combined with sub-viewport; static-screen MALL choices also conflict with some P-state MALL modes.
- Prefetch support can fail for line-count, bandwidth, dynamic metadata, VM/PTE row, and vratio reasons. The validation path searches prefetch modes and vstartup limits, while the recalculate path mostly uses the selected state and increments vstartup until support or max-vstartup exhaustion.
- Watermark values are computed into the `Watermark` struct and then copied into legacy VBA scalar fields so existing getters work. Changing one side without the copy-out would create stale public results.
- This code relies on many hard-coded DCN32 constants from the header, such as minimum vstartup, max prefetch ratio, strobe thresholds, and extra prefetch requirements. These are generation-specific and should not be silently reused for another DCN revision.

## Test Signals

Useful test coverage should exercise both the validate and recalculate entry points through the DML public interface:

- known-good single display, multi-display, DSC, DP2.0, HDMI/eDP, MST, writeback, and cursor configurations should produce stable `ModeIsSupported`, selected clocks, DPP counts, link BPP, DSC/FEC flags, and watermarks;
- negative mode tests should trigger individual support gates such as invalid scaler taps, viewport exceeds surface, pitch alignment failure, insufficient pipes, insufficient DSC units/slices, unsupported DSC BPC, invalid MST/link-rate declarations, writeback latency overflow, MALL combination conflicts, ROB support failure, prefetch failure, and immediate flip failure with host VM;
- boundary tests should cover max vstartup clamping at 1023, minimum vstartup, MEM_STROBE/DCFCLK extra prefetch thresholds, 420/interlace restrictions, 2:1 and 4:1 ODM constraints, and unbounded request fallback with MPC combine;
- regression tests should compare computed DML outputs against known DCN32 golden data, especially `DCFCLK`, `DISPCLK`, `DPPCLK`, `ReturnBW`, `PrefetchModePerState`, `VStartup`, `UrgentWatermark`, `DRAMClockChangeWatermark`, `StutterEfficiency`, and `DPPPerPlane`.
