# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4_calcs.c lines 5280-9672

## Scope And Purpose

This chunk covers the central DCN4 DML2 mode-support calculation path. It starts in the middle of `CalculatePrefetchSchedule()`, completes that per-plane prefetch scheduler, then defines helper routines for global prefetch admissibility, urgent/average bandwidth validation, immediate flip scheduling, watermark and clock-change support, p-state latency hiding, DRAM/UCLK/QoS conversion, HostVM inefficiency, G6 temperature-read blackout lookup, and the exported mode-support wrapper. The chunk ends at the start of `CalculatePixelDeliveryTimes()`, so that final function is only a boundary marker for the next chunk.

The main externally visible entry in this range is `dml2_core_calcs_mode_support_ex()`, which calls the internal `dml_core_mode_support()` and, on success, copies `mode_lib->ms.support` into the caller's `out_evaluation_info`. Most other functions are `static` calculation helpers that mutate the `mode_lib->ms` mode-support workspace, arrays in `core_display_cfg_support_info`, or local scratch structures under `struct dml2_core_internal_scratch`.

Functionally, this chunk answers whether a display configuration can run at a given minimum clock table entry. It derives clocks, DPP/OPP/ODM/DSC allocation, swath and DET layout, VM/PTE/meta row traffic, urgent and average bandwidth needs, prefetch timing, immediate flip feasibility, MALL/p-state combinations, watermarks, and a large conjunction of support flags. It is formula-heavy modeling code rather than direct hardware programming.

## Important APIs, Types, And Functions

`CalculatePrefetchSchedule()` is only partially visible in this chunk, but this range contains its final and most important scheduling logic. It computes:

- `DSTXAfterScaler` and `DSTYAfterScaler`, including 4:2:0 and progressive-to-interlace output delay handling.
- Rounded VM and row-trip terms: `Tvm_trips_rounded`, `Tr0_trips_rounded`, and flip variants, quantized to quarter-line units with minimum quarter-line floors.
- `Tno_bw` and `Tno_bw_flip`, the no-bandwidth latency component for deeper GPUVM page-table levels, extra latency, MRQ, and 3DLUT restrictions.
- `prefetch_sw_bytes`, `RequiredPrefetchBWMax`, one-to-one (`oto`) prefetch timing, equalized (`equ`) prefetch timing, VM/row/pixel prefetch bandwidths, cursor prefetch bandwidth, and final `VRatioPrefetchY/C`.
- Failure outputs such as `NoTimeForDynamicMetadata`, `NoTimeForPrefetch`, zeroed prefetch bandwidths, and zeroed VM/row line counts when timing is impossible.

`get_num_lb_source_lines()` estimates line-buffer source lines from maximum line-buffer lines, line-buffer size in bits, DPP count, viewport dimensions, horizontal ratio, and rotation. It switches to viewport height for vertical rotation and assumes 57 bits per pixel in the line buffer model.

`find_max_impact_plane()` and `calculate_impacted_Tsw()` support the global prefetch check. The former chooses the other plane with the largest accumulated return-path delay; the latter sums all prefetch swath bytes except one excluded plane and divides by a bandwidth estimate.

`CheckGlobalPrefetchAdmissibility()` performs an aggregate multi-plane prefetch sanity check when `DML_GLOBAL_PREFETCH_CHECK` is enabled. It estimates return-path pressure from detile-buffer and line-buffer burst sizes, clamps by ROB plus compressed-buffer worst-case occupancy, computes `impacted_dst_y_pre[]`, and requests a prefetch schedule recalculation if the impacted prefetch requirement exceeds the current per-plane `dst_y_prefetch[]`.

`calculate_peak_bandwidth_required()` calls `get_urgent_bandwidth_required()` across `dml2_core_internal_soc_state_max` and `dml2_core_internal_bw_max` for several views of bandwidth: vactive-only urgent bandwidth, urgent bandwidth including prefetch and optional flip, qualification row bandwidth, non-urgent bandwidth, and per-surface average/peak arrays. It uses zero/unity arrays to selectively include or suppress prefetch, cursor, VM-row, flip, and burst-factor terms.

`check_urgent_bandwidth_support()` compares urgent and non-urgent requirements against available SDP/DRAM bandwidth for system-active and, when MALL is allocated, SVP-prefetch states. It outputs nominal and MALL urgent-bandwidth fractions plus separate vactive-only and full-bandwidth support flags.

`get_bandwidth_available_for_immediate_flip()` returns the smaller leftover bandwidth between SDP and DRAM for the selected SoC state after non-flip urgent requirements. `calculate_immediate_flip_bandwidth_support()` validates flip-inclusive urgent and non-urgent bandwidth against the available table and emits `frac_urg_bandwidth_flip` plus `flip_bandwidth_support_ok`.

`CalculateFlipSchedule()` derives per-plane immediate flip timing and bandwidth. It handles two modes:

- `use_lb_flip_bw == true`: mode-support lower-bound flip bandwidth, based on max flip time, VM bytes, two row fetches, register limits, and whether immediate flip is requested.
- `use_lb_flip_bw == false`: bandwidth is apportioned from total available flip bandwidth by per-pipe flip bytes, then VM/row flip times and register line counts are tested.

`CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport()` computes urgent, stutter, Z8, USR retraining, DRAM clock-change, FCLK-change, writeback, and G6 temperature-read watermarks. It then derives per-plane active latency hiding from line-buffer lines, DET buffering, scaler/output delay, multi-surface sharing penalty, writeback limits, and reserved vblank overrides. Outputs include `DRAMClockChangeSupport[]`, `FCLKChangeSupport[]`, global clock-change flags, `SubViewportLinesNeededInMALL[]`, `VActiveLatencyHidingMargin[]`, `VActiveLatencyHidingUs[]`, `g6_temp_read_support`, and `MaxActiveFCLKChangeLatencySupported`.

`calculate_bytes_to_fetch_required_to_hide_latency()` computes luma/chroma bytes needed in vactive to hide a latency interval, including pixel swaths, optional DCC meta rows under MRQ, and optional GPUVM DPTE rows.

`calculate_vactive_det_fill_latency()` derives an informative vactive DET fill delay from the excess of peak over average bandwidth, splitting effective excess between luma and chroma according to their read bandwidth and DRAM DCC overhead factors.

`calculate_excess_vactive_bandwidth_required()` converts a per-plane override `max_vactive_det_fill_delay_us[dml2_pstate_type_uclk]` into extra luma/chroma bandwidth requirements.

Clock/QoS helpers in this chunk include:

- `uclk_khz_to_dram_bw_mbps()`, which converts UCLK to DRAM bandwidth directly from DRAM channel geometry or through an alternate bandwidth table.
- `dram_bw_kbps_to_uclk_mhz()`, the inverse direct conversion used when the min clock table has no explicit UCLK.
- `get_qos_param_index()`, which selects the previous QoS-parameter bucket for a UCLK threshold table.
- `get_active_min_uclk_dpm_index()`, which finds the exact UCLK entry in `mode_lib->soc.clk_table.uclk`.
- `calculate_hostvm_inefficiency_factor()`, which derives HostVM bandwidth inefficiency from pixel+VM versus VM-only urgent bandwidth and enforces a prefetch factor of at least 4 when remote IOMMU outstanding translations are below maximum requests.
- `get_g6_temp_read_blackout_us()` and `get_max_urgent_latency_us()`, which provide blackout and worst urgent-latency terms for DCN4x QoS/watermarks.

`dml_core_ms_prefetch_check()` is the dedicated prefetch, flip, watermark, and p-state support sub-pass inside mode support. It prepares 3DLUT settings, extra latency, per-plane `CalculatePrefetchSchedule()` calls, optional global prefetch recalculation, prefetch urgent bandwidth, immediate flip bandwidth, and watermarks.

`dml_core_mode_support()` is the main internal mode-support engine. It clears scratch and mode-support state, maps the requested clock table index into DCFCLK/FCLK/UCLK/DRAM bandwidth/QoS indexes, runs front-end format/link/pipe/resource checks, builds swath and VM-row state, calculates average and urgent bandwidth availability, invokes `dml_core_ms_prefetch_check()`, checks ROB and outstanding-request support, and finally produces `mode_lib->ms.support.ModeSupport`.

`dml2_core_calcs_mode_support_ex()` is the public wrapper in this chunk. It returns the internal mode-support result and copies the support info out only when the mode is supported.

## Control Flow

The visible tail of `CalculatePrefetchSchedule()` first converts scaler/output delay into integer destination lines and pixels. It then quantizes VM and row latency trips to quarter-line boundaries. GPUVM-enabled paths use measured VM/row trips; non-GPUVM paths fall back to extra latency, urgent latency, trip-to-memory, DCC MRQ, 3DLUT, or a quarter-line minimum depending on active features.

The scheduler computes `Tno_bw` only for GPUVM cases where page-table levels require extra no-bandwidth latency. For flip, `Tno_bw_flip` is retained only if MRQ is present or there are at least three GPUVM page-table levels, because the comment explicitly excludes 3DLUT from immediate flip.

The function then builds byte counts for prefetch:

1. Pixel swath bytes are calculated from prefetch source lines, swath widths, bytes per pixel, and MALL prefetch SDP overhead.
2. Base VM bytes are augmented with 3DLUT PTE bytes and an extra TDPE term when 3DLUT setup and GPUVM are enabled.
3. 3DLUT row bytes are modeled as half the 3DLUT frame bytes, rounded up.
4. Minimum swath line requirements for one-to-one and equalized schedules are capped by prefetch source line ratios, 3DLUT drain time, and a two-line floor.

The one-to-one path estimates a baseline prefetch bandwidth from vactive swath bandwidth and one-line-per-line-time pixel fetch rate, applies MALL overhead, caps it by the minimum swath time, and then raises it to satisfy VM and row register-limit lower bounds. It derives `Tvm_oto`, `Tr0_oto`, line counts, `dst_y_prefetch_oto`, optional global prefetch impact, and `Tpre_oto`.

The equalized path derives available `dst_y_prefetch_equ` from `VStartup`, setup time, calculation time, wait time, and scaler-output delay. It applies the U6.2 register limit of `63.75`, optionally adjusts around global impacted prefetch, rounds to quarter-line units, and computes `Tpre_rounded`. It then tries four bandwidth cases:

- Case 1: VM plus two row fetches plus swath bytes share the whole prefetch interval.
- Case 2: VM plus swath bytes share time after two row-trip latencies.
- Case 3: two row fetches plus swath bytes share time after VM latency.
- Case 4: only swath bytes use the time left after VM and two row latencies.

Cases 1 to 3 are accepted only if their derived VM and row transfer times land on the expected side of the rounded latency constraints. The selected `prefetch_bw_equ` is raised by VM and row register-limit lower bounds. `Tvm_equ` and `Tr0_equ` are then derived from the selected bandwidth and feature presence.

The function chooses the more stressful schedule by comparing `dst_y_prefetch_oto` and `dst_y_prefetch_equ`. For OTO it writes OTO VM/row times and line counts. For EQU it writes equalized times, may promote `dst_y_prefetch` to the impacted value, and updates `RequiredPrefetchBWMax` so mode support and mode programming do not disagree when a later path chooses a different schedule. It then derives lines available for pixel prefetch (`Lsw`), cursor prefetch bandwidth, swath prefetch time, prefetch ratios, and luma/chroma prefetch data bandwidth. Any impossible timing, invalid row/VM line count, insufficient `Lsw`, or zero equalized bandwidth sets `NoTimeToPrefetch` and resets the outputs to zero.

`CheckGlobalPrefetchAdmissibility()` is called only after per-plane prefetch succeeds, only for multi-plane configurations, and only when the compile-time global check is enabled. Its output can force one more pass through the `dml_core_ms_prefetch_check()` do/while loop: `impacted_dst_y_pre[]` is fed back into `CalculatePrefetchSchedule()`, `s->recalc_prefetch_done` prevents repeated recalculation, and `s->recalc_prefetch_schedule` drives the loop condition.

`dml_core_ms_prefetch_check()` performs the following sequence:

1. Set `TimeCalc` from deep-sleep DCFCLK and derive HostVM inefficiency factors.
2. Iterate active planes to count 3DLUT use and call `calculate_tdlut_setting()`.
3. Compute extra latency from QoS, ROB, request size, DPTE groups, 3DLUT bytes, HostVM/GPUVM, page sizes, and return bandwidth.
4. Clear impacted prefetch inputs and enter the optional recalculation loop.
5. For each plane, populate a `struct dml2_core_internal_DmlPipe`, assemble `CalculatePrefetchSchedule_params`, call `CalculatePrefetchSchedule()`, and fold each plane's result into `ms.support.PrefetchSupported`.
6. Recompute DCFCLK deep sleep with 3DLUT delivery and prefetch swath time.
7. Enforce register/timing limits: `dst_y_prefetch >= 2`, `LinesForVM < 32`, `LinesForDPTERow < 16`, no per-plane prefetch failure, and `DSTYAfterScaler <= 8`.
8. Validate dynamic metadata and prefetch ratios.
9. If prefetch still passes, compute prefetch urgent burst factors, urgent bandwidth requirements without flip, urgent bandwidth support, optional global prefetch admissibility, and then immediate flip bandwidth/schedule/support.
10. Build `mSOCParameters`, call watermark/clock-change support, calculate p-state keepout destination lines, and return to the main mode-support pass.

`dml_core_mode_support()` is a single-state evaluator keyed by `in_out_params->min_clk_index`. Its high-level order is:

1. Clear scratch and `mode_lib->ms`, set plane count, output BPPs, and clock/bandwidth fields from `min_clk_table`.
2. Select DCN4x QoS parameter and active UCLK DPM indexes.
3. Compute max DET/compressed buffer capacity and progressive-to-interlace adjusted backend clocks.
4. Run scale/taps, source-format/rotation, byte/block-size, vactive bandwidth, cursor bandwidth, writeback bandwidth/latency, writeback scaler, viewport, pitch, and surface bounds checks.
5. Run a single-DPP swath/DET pass to learn whether each viewport can fit in one pipe.
6. Determine DSC slices, ODM mode with and without DSC, output link requirements, pipe allocation, DPP/OPP totals, DISPCLK/DPPCLK requirements, and output resource limits.
7. Validate link policy, DSC clocks/units/slices, DTBCLK, DP/MSO lane constraints, and DSC/ODM slice alignment.
8. Re-run swath/DET with final DPP and ODM decisions.
9. Calculate MALL surface size, DCC active DPP count, VM/PTE/meta row geometry, PTE/DCC meta buffer support, and p-state bytes to fetch.
10. Calculate urgent latency, trip-to-memory, cursor and surface urgent burst factors, deep-sleep DCFCLK, writeback delay, VStartup limits, MALL/p-state combination validity, outstanding request latency support, MCache/MALL overhead factors, bandwidth availability, average bandwidth support, and urgent latency hiding support.
11. Invoke `dml_core_ms_prefetch_check()`.
12. Check ROB support, compute informative vactive DET fill delay, evaluate the final large conjunction of support flags, and mirror selected outputs into `ms.support`.

The final `ModeSupport` condition is intentionally strict. It requires all major support flags to be true and all disqualifying flags to be false, including scale/taps, source format/scan, viewport size, link/DSC/resource constraints, MALL combinations, ROB, outstanding requests, clocks, writeback, cursor, pitch, prefetch, average bandwidth, dynamic metadata, PTE/DCC meta buffers, MALL size, G6 temp read, and immediate flip support when HostVM or immediate flip is required.

## State And Persistence Behavior

This code uses persistent state only within the DML mode-support object; it does not allocate kernel memory, acquire locks, issue MMIO, program hardware, or persist state outside the caller-provided structures.

`dml_core_mode_support()` begins with:

- `memset(&mode_lib->scratch, 0, sizeof(...))`
- `memset(&mode_lib->ms, 0, sizeof(...))`

That makes every invocation a fresh calculation pass. Outputs persist in `mode_lib->ms` after the function returns, and `dml2_core_calcs_mode_support_ex()` copies `mode_lib->ms.support` out only when the mode is supported. If the mode is unsupported, the caller can still inspect `mode_lib->ms` and debug logs, but `out_evaluation_info` is not refreshed by the wrapper.

Scratch-local structures store large temporary arrays and parameter blocks:

- `dml_core_mode_support_locals` holds intermediate arrays such as scaler delay, line times, swath bytes, VM page dimensions, metadata row heights, p-state byte requirements, dummy arrays, output BPPs, and MALL/p-state booleans.
- `CalculatePrefetchSchedule_params`, `calculate_peak_bandwidth_params`, `CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport_params`, `CalculateVMRowAndSwath_params`, and related structs are reused and overwritten during the pass.
- Many helper outputs are direct pointers into `mode_lib->ms` arrays, so prefetch, bandwidth, flip, watermark, and support state is accumulated in place.

Important persistent fields produced in this chunk include:

- Clock state: `SOCCLK`, `DCFCLK`, `FabricClock`, `MaxDCFCLK`, `MaxFabricClock`, `RequiredDISPCLK`, `RequiredDPPCLK[]`, `GlobalDPPCLK`, `dcfclk_deepsleep`, `uclk_freq_mhz`, `dram_bw_mbps`, `max_dram_bw_mbps`, `qos_param_index`, and `active_min_uclk_dpm_index`.
- Plane allocation: `ODMMode[]`, `MPCCombine[]`, `NoOfDPP[]`, `NoOfOPP[]`, DPP/OPP totals, DSC/FEC requirements, DSC slice counts, output BPP/type/rate/slots, and output support mirrors in `ms.support`.
- Geometry and memory model: swath widths/heights, DET buffer sizes, compressed buffer size, MALL surface size, VM bytes, DPTE row bytes/heights, meta row bytes/heights, request sizes, PTE/DCC meta buffer support, and MCache/MALL overhead factors.
- Timing and bandwidth: vactive bandwidths, cursor bandwidths, urgent burst factors, urgent/average bandwidth availability and requirements, prefetch bandwidths, VM-row bandwidth, immediate flip bandwidth, p-state vactive fill delays, watermarks, VActive latency hiding, and keepout-related support.
- Support booleans: the final `ModeSupport` and all intermediate flags that explain why a configuration failed.

The only file-scope mutable object visible in the chunk is `core_dcn4_g6_temp_read_blackout_table`, a static table of UCLK thresholds and blackout times. It is read by `get_g6_temp_read_blackout_us()` unless SoC bounding-box overrides are present.

## Dependencies And Integration Points

This chunk depends on the DML2 DCN4 calculation ecosystem:

- `struct dml2_core_internal_display_mode_lib` provides the IP block (`ip`), SoC bounding box (`soc`), mode-support workspace (`ms`), and scratch storage.
- `struct dml2_display_cfg` supplies stream descriptors, plane descriptors, output settings, DCC/GPUVM/HostVM flags, MALL/p-state overrides, scaler parameters, cursor parameters, writeback state, viewport/surface geometry, timing, and display-level overrides.
- `struct dml2_mcg_min_clock_table`, `struct dml2_soc_state_table`, `struct dml2_dram_params`, and DCN4x QoS structs provide clock, bandwidth, DRAM, and latency tables.
- `struct core_display_cfg_support_info` receives the final support report.
- Enumerations such as `dml2_core_internal_soc_state_type`, `dml2_core_internal_bw_type`, `dml2_source_format_class`, `dml2_rotation_angle`, `dml2_uclk_pstate_change_strategy`, `dml2_refresh_from_mall_mode_override`, `dml2_odm_mode`, `dml2_output_encoder`, and `dml2_qos_param_type` control most branches.

Important helper dependencies defined elsewhere in the same file or nearby DML2 sources include:

- Prefetch and timing: `CalculatePrefetchSchedule()`, `CalculateExtraLatency()`, `CalculateTWait()`, `CalculateMaxVStartup()`, `CalculateDCFCLKDeepSleep()`, `CalculateDCFCLKDeepSleepTdlut()`, `CalculateUrgentLatency()`, and `CalculateTripToMemory()`.
- Geometry/memory layout: `CalculateMaxDETAndMinCompressedBufferSize()`, `CalculateBytePerPixelAndBlockSizes()`, `CalculateSwathAndDETConfiguration()`, `CalculateVMRowAndSwath()`, `CalculateSurfaceSizeInMall()`, `calculate_tdlut_setting()`, and `calculate_mcache_setting()`.
- Bandwidth and burst factors: `calculate_bandwidth_available()`, `calculate_avg_bandwidth_required()`, `get_urgent_bandwidth_required()`, `CalculateUrgentBurstFactor()`, `calculate_cursor_req_attributes()`, `calculate_cursor_urgent_burst_factor()`, and `calculate_mall_bw_overhead_factor()`.
- Link/output: `get_stream_output_bpp()`, `PixelClockAdjustmentForProgressiveToInterlaceUnit()`, `CalculateSinglePipeDPPCLKAndSCLThroughput()`, `CalculateODMMode()`, `CalculateOutputLink()`, `RequiredDTBCLK()`, `DSCDelayRequirement()`, `CalculateWriteBackDISPCLK()`, and `CalculateWriteBackDelay()`.

Compile-time integration points matter:

- `__DML_VBA_DEBUG__` enables extensive verbose traces and failure details.
- `DML_GLOBAL_PREFETCH_CHECK` enables aggregate prefetch impact calculation and the prefetch recalculation loop.
- `DML_MODE_SUPPORT_USE_DPM_DRAM_BW` switches whether the second bandwidth availability calculation uses current DPM DRAM bandwidth or max DRAM bandwidth.

The runtime integration point is the AMD display mode validation path. The caller prepares `dml2_core_calcs_mode_support_ex` with a populated `mode_lib`, display config, min clock table, and clock index. This chunk evaluates the config and returns whether the DCN4 model supports it. Later mapping/programming code can consume `out_evaluation_info` and the calculated `mode_lib->ms` state to choose clocks, watermarks, DPP/ODM/DSC setup, MALL usage, prefetch values, and immediate-flip programming.

## Risks And Edge Cases

Several helpers divide by clock, bandwidth, line-time, or byte-rate values that are assumed valid. Zero or stale values in DCFCLK, FCLK, UCLK, DRAM bandwidth, return bus width, urgent bandwidth availability, line time, `VRatio`, `VRatioChroma`, swath dimensions, or surface read bandwidth can produce invalid calculations or assertions. The mode-support path expects min clock tables and display descriptors to be fully initialized before entry.

The prefetch scheduler is very sensitive to rounding. VM, row, prefetch, and register fields are quantized to quarter-line units and capped by U6.2-style limits (`dst_y_prefetch < 64`, `LinesForVM < 32`, `LinesForDPTERow < 16`). Small changes in `VStartup`, scaler delay, extra latency, DCC/MRQ, 3DLUT bytes, or HostVM inefficiency can flip a mode from supported to unsupported.

The equalized schedule selects among four bandwidth cases by comparing derived VM/row transfer times with rounded latency constraints. This branch is non-obvious and high-risk for regressions because the selected case changes both required prefetch bandwidth and the VM/row line allocation. The code also carries `RequiredPrefetchBWMax` even when OTO is not selected to avoid mode-support versus mode-programming mismatches; removing or weakening that propagation can create cross-stage disagreement.

3DLUT and MRQ support are interwoven with GPUVM and DCC. 3DLUT adds PTE bytes, row bytes, drain-time constraints, and DCFCLK deep-sleep delivery. MRQ/DCC influences row timing, metadata bytes, immediate-flip no-bandwidth behavior, and p-state bytes. Modes with GPUVM, HostVM, DCC, MRQ, dynamic metadata, and 3DLUT active together are especially sensitive.

`find_max_impact_plane()` has a notable edge case: if the maximum-impact plane index is `0`, the `if (max_idx <= 0)` branch resets the result to `this_plane_idx` after asserting `max_idx >= 0`. That means plane 0 can be ignored as the impacting plane for other planes in this helper. This may be intentional due to a historical assumption, but it is a risk area for global prefetch correctness.

`get_qos_param_index()` returns `i - 1` for nonzero threshold positions and stops at the first threshold greater than the UCLK or zero. Badly ordered or missing `minimum_uclk_khz` entries can select the wrong QoS bucket. `get_active_min_uclk_dpm_index()` asserts if the selected UCLK is not found exactly in the SoC clock table, so alternate DRAM bandwidth conversion paths must still keep UCLK tables coherent.

`uclk_khz_to_dram_bw_mbps()` with alternate clock conversion uses the first table entry whose `min_uclk_khz >= uclk_khz`; if no entry matches, `bw_mbps` remains zero and asserts. The direction of the comparison and table ordering are therefore part of the contract.

HostVM inefficiency can be amplified to 4x for prefetch when remote IOMMU outstanding translations are below maximum requests. That protects bandwidth modeling, but it can make prefetch support fail abruptly when HostVM/GPUVM configuration or request-count tables change.

Immediate flip support depends on both timing and bandwidth models. `CalculateFlipSchedule()` may output lower-bound flip bandwidth in mode support without calculating actual `dst_y_per_vm_flip` and `dst_y_per_row_flip` values (`use_lb_flip_bw` sets them to 1 as unused). Later paths using actual flip line programming must stay aligned with this support model to avoid accepting modes that cannot program flip safely.

MALL and p-state combinations are constrained by several disqualifying booleans: immediate flip or HostVM with full-frame MALL/phantom pipe, refresh-from-MALL mixed with static screen modes, SubVP without matching phantom pipe, SubVP combined with full-frame MALL, and SubVP refresh above 120 Hz when implicit PMO is disabled. These policy constraints can reject otherwise bandwidth-valid modes.

Outstanding-request support in DCN4x compares modeled outstanding latency from request size and return bus width against average urgent and non-urgent latency. Incorrect request-size selection from swath/DET configuration, especially with chroma or MRQ, can incorrectly fail `OutstandingRequestsSupport` or `OutstandingRequestsUrgencyAvoidance`.

The final mode-support predicate is a large conjunction. A new feature that sets a support flag but forgets to include it in the final predicate, or a new failure flag that is not reset before use, can cause false positives or false negatives. Conversely, because `mode_lib->ms` is zeroed at function entry, any required flag not explicitly set to true will fail if included in the predicate.

## Test Signals

Useful test coverage should exercise both the final mode-support result and intermediate support flags:

- Baseline supported modes across simple RGB, 4:2:0, 4:2:2, RGBE-alpha, DCC-on/off, GPUVM-on/off, HostVM-on/off, MRQ-on/off, and single-plane/multi-plane configurations.
- Prefetch boundary tests with low VBlank/VStartup, high scaler delay, interlace/progressive-to-interlace, dynamic metadata, 3DLUT, high page-table levels, small HostVM page sizes, and high urgent/trip-to-memory latency. Debug traces should show `dst_y_prefetch`, `LinesForVM`, `LinesForDPTERow`, `VRatioPreY/C`, `RequiredPrefetchBWMax`, `NoTimeForPrefetch`, and `NoTimeForDynamicMetadata`.
- Global prefetch tests under `DML_GLOBAL_PREFETCH_CHECK` with at least two active planes and asymmetric detile/swath sizes. Watch `impacted_dst_y_pre[]`, `recalc_prefetch_schedule`, and whether the second prefetch pass converges.
- Immediate flip cases with no flip, one flip plane, multiple flip planes, GPUVM-only, DCC/MRQ-only, and GPUVM plus DCC/MRQ. Validate `final_flip_bw[]`, `ImmediateFlipSupportedForPipe[]`, `ImmediateFlipSupport`, and flip-inclusive urgent bandwidth tables.
- Bandwidth support tests near SDP and DRAM limits, with MALL disabled and enabled, to distinguish `AvgBandwidthSupport`, `UrgVactiveBandwidthSupport`, `PrefetchBandwidthSupported`, and flip bandwidth support.
- Clock/resource tests around max DISPCLK, DPPCLK, DSCCLK, DTBCLK, DPP/OPP/DSC/OTG/writeback/DP2/HDMI-FRL resource limits, DSC slice overrides, and ODM 2:1/3:1/4:1 alignment.
- MALL and p-state policy tests for SubVP main/phantom pairing, full-frame MALL, refresh-from-MALL overrides, HostVM, immediate flip, all-streams-blanked, forced vactive/vblank/DRR/MALL p-state strategies, and high-refresh SubVP.
- G6 temperature-read tests where SoC bounding-box blackout overrides are present versus absent, with UCLK values below, between, and above internal table thresholds.
- QoS/clock-table robustness tests for exact UCLK DPM matching, alternate DRAM bandwidth conversion, DCN3 versus DCN4x QoS types, and min clock table entries with `min_uclk_khz == 0`.
- Failure diagnostics under `__DML_VBA_DEBUG__`; unsupported modes should produce enough logs from `dml2_print_mode_support_info()` and surrounding verbose statements to identify the failing support bit.

Hardware-facing symptoms of model regressions include unexpected mode rejection, accepting a mode that underflows during prefetch, flip glitches, black screen on high-bandwidth or DSC/ODM modes, incorrect DRAM/FCLK p-state change behavior, MALL/SubVP policy mis-selection, stutter or Z8 residency regressions, and mismatched mode-support versus mode-programming prefetch bandwidth.

## Cross-Chunk Notes

This chunk starts in the middle of `CalculatePrefetchSchedule()`. The earlier part of the same function, including its signature, local setup, dynamic metadata timing, setup-time calculation, and initial VM/row trip derivation, must be merged from the previous chunk for a complete per-file report.

This chunk also ends immediately after the `CalculatePixelDeliveryTimes()` signature begins. The body of that function and later display-configuration/programming calculations are outside this chunk and should be covered by the next chunk.

The final per-file synthesis should connect this chunk with earlier DCN4 helper definitions and later programming-output calculations. In particular, the merge should preserve the full data flow from `dml2_core_calcs_mode_support_ex()` through `dml_core_mode_support()`, `dml_core_ms_prefetch_check()`, and the later routines that consume `core_display_cfg_support_info` for actual DML output fields.
