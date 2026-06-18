# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/dml2_core/dml2_core_dcn4_calcs.c lines 9673-13402

## Scope And Purpose

This chunk is the DCN4 DML2 mode-programming and register-export tail of `dml2_core_dcn4_calcs.c`. It begins at the body of `CalculatePixelDeliveryTimes()`, then defines timing helpers for meta/PTE/VM scheduling, stutter-efficiency modeling, the large `dml_core_mode_programming()` pass, and the public accessors that translate the calculated model state into DCHUBBUB/DLG/RQ/TTU/ARB/FAMS2 programming and informative reporting.

The code is modeling and register-preparation logic, not direct hardware programming. It consumes a validated display configuration, selected clocks, SOC/IP capability tables, and mode-support results, then fills `mode_lib->mp` (`struct dml2_core_internal_mode_program`) with per-plane and global programming-derived quantities. Later exported helpers read that persistent model state to populate structures used by display core programming or diagnostics.

Major responsibilities in this chunk are:

- Calculate display-pipe line/request delivery times for luma and chroma in active and prefetch phases.
- Convert DCC meta rows, pixel PTE rows, TDLUT groups, and VM groups into nominal, vblank, and immediate-flip time budgets.
- Build the selected-mode programming state, including swath/DET, MALL/mcache, GPUVM/DCC metadata, prefetch, immediate flip, watermarks, delivery timings, VM/meta timings, VStartup, writeback bandwidth, stutter efficiency, and deep-sleep hysteresis.
- Export watermarks, arbiter registers, per-pipe DLG/RQ/TTU registers, sync programming, FAMS2 programming, mcache/MALL allocation, plane/stream support details, and the large `informative` result block.

## Important APIs, Types, And Functions

`CalculatePixelDeliveryTimes()` writes `DisplayPipeLineDeliveryTime*[]` and `DisplayPipeRequestDeliveryTime*[]` arrays. For each plane it uses scaler ratios, swath-width upper bounds, DPP count, pixel clock, PSCL throughput, DPP clock, bytes-per-pixel, and request counts. If the relevant vertical ratio is at or below 1.0 it models delivery through output pixel timing; otherwise it models delivery through scaler throughput and DPP clock. Chroma arrays are zeroed when `BytePerPixelC[k] == 0`.

`CalculateMetaAndPTETimes()` accepts a `struct dml2_core_shared_CalculateMetaAndPTETimes_params`. It derives:

- `DST_Y_PER_PTE_ROW_NOM_L/C[]` and `DST_Y_PER_META_ROW_NOM_L/C[]`.
- DCC meta chunk timing for nominal, vblank, and flip phases when DCC and MRQ are enabled.
- TDLUT group time when a plane is configured for TDLUT.
- PTE group timing for nominal, vblank, and flip phases when GPUVM is enabled.

This helper depends heavily on rotation, row heights, meta chunk sizes, PTE request geometry, `use_one_row_for_frame[]`, and `dst_y_per_row_*[]` outputs from prefetch/flip scheduling.

`CalculateVMGroupAndRequestTimes()` computes `TimePerVMGroupVBlank[]`, `TimePerVMGroupFlip[]`, `TimePerVMRequestVBlank[]`, and `TimePerVMRequestFlip[]`. It counts lower-level VM groups and 64-byte requests from DPDE0 bytes, DCC meta PTE bytes, and TDLUT PTE bytes. The result is a per-plane time slice over `dst_y_per_vm_vblank` or `dst_y_per_vm_flip`. GPUVM disabled produces zeros.

`CalculateStutterEfficiency()` models compressed-buffer, ROB, DET, DCC, zero-size request, row-bandwidth, and stutter burst behavior. It finds the critical non-phantom surface with the shortest luma DET buffering time, computes stutter/Z8 efficiencies with and without vblank, counts bursts per frame, and sets `DCHUBBUB_ARB_CSTATE_MAX_CAP_MODE`.

`dml_core_mode_programming()` is the central internal pass. It takes `struct dml2_core_calcs_mode_programming_ex`, zeros scratch and `mode_lib->mp`, loads selected clocks from `programming->min_clocks`, maps pipes to planes from `cfg_support_info`, and runs the selected-mode calculations. It returns `mode_lib->mp.PrefetchAndImmediateFlipSupported`.

`dml2_core_calcs_mode_programming_ex()` is the public wrapper around `dml_core_mode_programming()`.

`dml2_core_calcs_get_dpte_row_height()` is a standalone exported helper. It recalculates bytes-per-pixel and block geometry for a supplied format/tiling/rotation/pitch, populates only enough `calculate_vm_and_row_bytes_params` scratch state to call `CalculateVMAndRowBytes()`, and returns the requested luma or chroma DPTE row height.

`is_dual_plane()` classifies 4:2:0 formats and `dml2_rgbe_alpha` as dual-plane. `dml_get_plane_idx()` resolves a pipe index through `mode_lib->mp.pipe_plane[]`.

`rq_dlg_get_wm_regs()`, `rq_dlg_get_rq_reg()`, `rq_dlg_get_dlg_reg()`, and `rq_dlg_get_arb_params()` convert modeled timings and limits into DCHUBBUB/DLG/RQ/TTU/ARB register structures. Public wrappers expose these through `dml2_core_calcs_get_watermarks()`, `dml2_core_calcs_get_arb_params()`, and `dml2_core_calcs_get_pipe_regs()`.

`dml2_core_calcs_get_global_sync_programming()` and `dml2_core_calcs_get_stream_programming()` expose VReady/VStartup/VUpdate and p-state keepout timing.

`dml2_core_calcs_get_global_fams2_programming()` and `dml2_core_calcs_get_stream_fams2_programming()` populate DMUB FAMS2 global and per-stream command structures from stage-3 p-state metadata, DML core watermarks, IP FAMS2 capabilities, and selected p-state method.

`dml2_core_calcs_get_mcache_allocation()`, `dml2_core_calcs_get_mall_allocation()`, `dml2_core_calcs_get_plane_support_info()`, `dml2_core_calcs_get_stream_support_info()`, and `dml2_core_calcs_get_informative()` are readout helpers for allocation, support, and diagnostic data.

## Control Flow

The chunk starts with the active body of `CalculatePixelDeliveryTimes()`. The first loop computes line delivery times for each active surface. Luma and chroma use active scaler ratios, while prefetch luma/chroma use `VRatioPrefetchY/C[]`. The second loop divides those line delivery times by request counts to get per-request delivery times.

`CalculateMetaAndPTETimes()` runs in four conceptual phases. First, it computes nominal destination lines per PTE/meta row from row height divided by scaler vertical ratio. Second, for DCC+MRQ planes it computes luma/chroma meta chunks per row, using rotation to choose width versus height request thresholds, and converts row-line windows into time per meta chunk for nominal, vblank, and flip. Third, it computes optional TDLUT group timing. Fourth, when GPUVM is enabled, it computes luma/chroma DPTE group widths, groups per row, applies the small-group `+1` adjustment when groups are at most 2, and converts nominal/vblank/flip row windows to PTE group times. GPUVM disabled or missing chroma zeros the corresponding outputs.

`CalculateVMGroupAndRequestTimes()` walks planes and accumulates lower-VM-stage group/request counts. For page-table levels >= 2 it counts luma and chroma DPDE0 groups. For DCC+MRQ it adds meta PTE groups and one or two MPDE0 groups depending on chroma. TDLUT contributes extra prefetch-only groups and requests, plus a TDPE0 group for multi-level GPUVM. Time outputs are line-window time divided by group or request counts, and are halved when `gpuvm_max_page_table_levels > 2`.

`CalculateStutterEfficiency()` first computes aggregate compressed read bandwidth, zero-size bandwidth, and row bandwidth across non-phantom planes. DCC planes clamp effective luma/chroma compression to 2x or 4x depending on block geometry, swath height, rotation, and max uncompressed block. It then computes average DCC compression and zero-size fraction, derives effective compressed-buffer capacity across compressed buffer, meta FIFO, zero-size buffer, and ROB, and finds the critical surface by minimum luma DET buffering time. With that critical period it computes the burst time needed to refill compressed/ROB/DET and row data, checks whether active writeback disables stutter, computes SR and Z8 efficiencies, adjusts for synchronized same-timing streams when applicable, and sets the C-state max-cap mode flag.

`dml_core_mode_programming()` performs the selected-mode pipeline in a mostly linear sequence:

1. Clear scratch and `mode_lib->mp`, count active planes/pipes, map pipes to planes, load selected active clocks, derive DRAM bandwidth and QoS indices, and map support ODM data to `mode_lib->mp.ODMMode[]`.
2. Copy per-plane DPP and DPPCLK/DSCCLK values, assert required clocks are positive, then calculate maximum DET, nominal DET, compressed-buffer minimum, p-to-i pixel clocks, scaler throughput, bytes-per-pixel/block sizes, swath widths, cursor bandwidth, and active swath bandwidth.
3. Call `CalculateSwathAndDETConfiguration()` to compute swath heights, request sizes, DET allocation, unbounded-request state, compressed-buffer size, and viewport support placeholders for this selected configuration.
4. Compute DSC delay and MALL surface size, build `SurfaceParameters[]`, and call `CalculateVMRowAndSwath()` to populate DPTE, VM, PTE, meta-row, row-bandwidth, PTE-buffer mode, and one-row-for-frame data.
5. Configure mcache and MALL bandwidth overhead when MALL is allocated and MRQ is not present; otherwise default overhead factors to 1.0.
6. Calculate available bandwidth, HostVM inefficiency factors, active DPP counts, TDLUT settings, extra latency, writeback delay, vactive bytes required to hide UCLK p-state latency, excess vactive fill bandwidth, urgent/trip/meta-trip latencies, line-buffer source lines, cursor urgent factors, normal urgent burst factors, and maximum VStartup lines.
7. For multi-plane modes, run `CheckGlobalPrefetchAdmissibility()` to estimate impacted prefetch lines. Then run a single prefetch scheduling pass over every plane, filling `DSTX/YAfterScaler`, destination prefetch windows, `VRatioPrefetch*`, required prefetch bandwidths, dynamic metadata timing, VUpdate/VReady offsets, TDLUT/cursor prefetch terms, and impacted prefetch margin.
8. Reject prefetch support if any plane has no time to prefetch, dynamic metadata cannot fit, `DSTYAfterScaler > 8`, destination prefetch lines under 2, prefetch VRatio above `__DML2_CALCS_MAX_VRATIO_PRE__`, or urgent latency hiding failures. If the schedule is still valid, compute prefetch urgent burst factors, peak bandwidth requirements, and call `check_urgent_bandwidth_support()`.
9. If prefetch is valid, compute immediate-flip bandwidth availability and flip bytes, run `CalculateFlipSchedule()` per plane, recompute peak bandwidth with flip bandwidth included, and call `calculate_immediate_flip_bandwidth_support()`. Per-pipe immediate-flip failures clear global immediate-flip support.
10. Combine prefetch and immediate-flip support. Immediate flip is mandatory when HostVM is enabled or any plane explicitly requests immediate flip.
11. If the combined support flag is true, compute DCC configuration, watermarks and p-state change support, writeback p-state end positions, p-state keepout lines, pixel delivery times, meta/PTE times, VM group/request times, VStartup placement, writeback bandwidth, total data read bandwidth, and stutter efficiency.
12. Always finish by computing minimum return latency in DCFCLK cycles and DCFCLK deep-sleep hysteresis, then return `PrefetchAndImmediateFlipSupported`.

The register-export path is separate from the modeling pass. `dml2_core_calcs_get_pipe_regs()` first fills RQ registers, then DLG/TTU registers, then DET segment size. Those calculations read `mode_lib->mp` data produced by successful mode programming.

`rq_dlg_get_rq_reg()` maps chunk sizes, min chunk sizes, meta chunk sizes, DPTE/MPTE group sizes, linear PTE row height, swath height, expansion modes, unbounded request, and dual-plane DET plane1 base address. The dual-plane DET split mirrors modeled luma/chroma stored swath ratio: phantom pipes split a fixed 1 MB DET region in half; non-phantom dual-plane pipes split half/half unless luma stored swath bytes exceed chroma by more than 1.5x, in which case plane1 starts after a 2/3 luma allocation rounded to 1 KB.

`rq_dlg_get_dlg_reg()` resolves timing, pipe/plane/ODM position, refclk-to-pixel-clock scaling, prefetch destination windows, VM/PTE/meta timing, delivery timing, dynamic metadata timing, and TTU request delivery. It writes fixed-point register encodings, applies saturation to some 23-bit VM/PTE fields, and asserts expected register ranges for scaler offsets, delivery times, TTU fields, and vblank timing.

`dml2_core_calcs_get_informative()` is a large state-copy function. It copies mode-support booleans and per-plane support data from `mode_lib->ms.support`, watermarks and QoS metrics from accessor helpers, aggregate MALL/DPP totals, power-management/stutter values, CRB and miscellaneous model fields, per-plane DPTE/meta/swath/delivery/VM/prefetch/DCC data from `mode_lib->mp`, non-optimized mcache allocation, and a derived ROB urgency-avoidance flag.

## State And Persistence Behavior

`dml_core_mode_programming()` explicitly resets `mode_lib->scratch` and `mode_lib->mp` at entry. Scratch is temporary workspace for large local arrays and parameter structs; `mode_lib->mp` is the persistent result for the selected programming pass. Public getters later rely on this persistent `mp` state, so callers must run mode programming before requesting registers or informative data.

The selected clock state is persisted in `mode_lib->mp.Dcfclk`, `FabricClock`, `dram_bw_mbps`, `uclk_freq_mhz`, `GlobalDPPCLK`, `Dppclk[]`, `DSCCLK[]`, `Dispclk`, and `DCFCLKDeepSleep`. These values are treated as already selected by upstream support/min-clock logic and are asserted to be positive.

Per-plane model state persists in arrays under `mode_lib->mp`: swath widths/heights, DET sizes, DCC block settings, MALL and mcache allocation, DPTE/PTE/meta row geometry, VM/PTE/meta timing, prefetch schedule terms, delivery times, VStartup/VUpdate/VReady values, urgent burst factors, support flags, row bandwidth, total bandwidth, and stutter metrics. Many arrays are indexed by plane, while pipe-level register export maps pipe to plane through `mp.pipe_plane[]`.

`CalculateStutterEfficiency()` uses `scratch->CalculateStutterEfficiency_locals` and zeroes it at entry. It only persists results through output pointers into `mode_lib->mp`.

`dml2_core_calcs_get_dpte_row_height()` mutates `mode_lib->scratch.calculate_vm_and_row_bytes_params` and uses a stack `dummy_integer[]` for unneeded outputs. It does not update `mode_lib->mp`, but it does reuse the shared scratch object, so it is not thread-independent from other DML calculations on the same `mode_lib`.

Export helpers mostly write caller-provided output structures. `rq_dlg_get_dlg_reg()` uses `mode_lib->scratch.rq_dlg_get_dlg_reg_locals` as temporary workspace and zeroes that local block at entry. The helpers do not allocate memory, take locks, or retain pointers into output structures.

`dml2_core_calcs_get_informative()` assumes `out->display_config` is already populated, because it iterates `out->display_config.num_planes` and reads `out->display_config.plane_descriptors->overrides.reserved_vblank_time_ns` when deriving `PrefetchMode[]`. It then fills only the informative/min-clock fields.

## Dependencies And Integration Points

This chunk depends on the surrounding DML2 DCN4 internal data model:

- `struct dml2_core_calcs_mode_programming_ex` supplies the input display config, selected min-clock table/index, support info, mode library, and output programming object.
- `struct dml2_core_internal_display_mode_lib` provides `ip`, `ip_caps`, `soc`, `ms`, `mp`, and `scratch` state.
- `struct dml2_display_cfg`, `struct dml2_plane_parameters`, `struct dml2_stream_parameters`, `struct core_display_cfg_support_info`, and the programming/output register structs define the public inputs and outputs.
- Helper structs in `mode_lib->scratch` carry parameters for `CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport()`, `CalculateVMRowAndSwath()`, `CalculateSwathAndDETConfiguration()`, `CalculateStutterEfficiency()`, `CalculatePrefetchSchedule()`, `CheckGlobalPrefetchAdmissibility()`, `calculate_mcache_setting()`, `calculate_tdlut_setting()`, `CalculateMetaAndPTETimes()`, peak-bandwidth calculation, and vactive latency hiding.
- Enumerations such as `dml2_source_format_class`, `dml2_swizzle_mode`, `dml2_rotation_angle`, `dml2_odm_mode`, `dml2_qos_param_type`, `dml2_pstate_method`, internal output type/rate enums, and DMUB FAMS2 stream types drive branch behavior.
- Math/logging/assert helpers such as `math_ceil2`, `math_floor2`, `math_min2`, `math_max2`, `math_pow`, `math_log2_approx`, `DML_ASSERT`, and `DML_LOG_VERBOSE` are used throughout.

The mode-programming path integrates with earlier code in the same file that performs mode support and min-clock selection. `dml_core_mode_programming()` reads support decisions such as DPP count, ODM segments, DSC enable/slices, selected output BPP, aligned pitch, and selected clocks; it does not re-solve those support choices.

The register getters integrate with DC programming layers outside this file. They provide DCHUB watermark registers, display arbiter registers, per-pipe RQ/DLG/TTU registers, global sync programming, stream programming, FAMS2 DMUB command payloads, MALL allocation, and mcache allocation.

The informative getter integrates with diagnostics and upper layers that need a human/queryable summary of why a mode is or is not supportable and what timing/bandwidth/watermark values were modeled.

## Risks And Edge Cases

Several calculations assume nonzero clocks, ratios, request counts, group sizes, and bandwidths. The code asserts key selected clocks but many divisions rely on upstream initialization of `pixel_clock_khz`, scaler ratios, `req_per_swath_ub_*`, `PTERequestSize*`, `tdlut_groups_per_2row_ub`, `vm_group_bytes`, and return bandwidth arrays.

`CalculateVMGroupAndRequestTimes()` does not reset `num_group_per_lower_vm_stage` and `num_req_per_lower_vm_stage` inside the per-plane loop. The counters are initialized before the loop and accumulate across planes, then each plane's time is divided by the cumulative count so far. If this is intentional, it models shared lower-stage VM pressure; if not, it makes later planes receive smaller per-group/request times than standalone per-plane counts would produce. This is a high-value area for trace comparison.

One chroma VM request count path adds `dpde0_bytes_per_frame_ub_c[k]` without dividing by 64, unlike the luma path and meta chroma path. If units are bytes, this can overcount chroma lower-stage requests by 64x. This may be inherited spreadsheet behavior, but it is a clear risk point.

Several places use `display_cfg->stream_descriptors[k]` instead of indexing through a plane's `stream_index`. In `CalculateStutterEfficiency()` the active writeback count uses `stream_descriptors[k]` inside a loop over planes after checking `stream_visited[plane.stream_index]`. This is only equivalent when plane index and stream index match; multi-plane-per-stream or reordered stream indexes could skew writeback detection.

In `dml_core_mode_programming()`, `SurfaceParameters[k].ViewportXStartC` is assigned from `composition.viewport.plane1.y_start`, and mcache chroma `vp_start_x_c` is also assigned from `plane1.y_start`. That may be a copy/paste bug if the intended source is `plane1.x_start`. It would affect rotated/chroma viewport VM/mcache calculations for dual-plane formats.

Immediate-flip support is forced when HostVM is enabled, even if no plane explicitly requests immediate flip. This is deliberate policy in the code, but it means HostVM modes can fail programming from flip bandwidth/schedule constraints that would otherwise be optional.

The single prefetch scheduling pass does not iterate VStartup choices. It sets each `VStartupMin[k]` to `MaxVStartupLines[k]`, then later uses max VStartup for positioning. If upstream support expected iterative search, this selected-mode programming path may only verify and program the max-VStartup solution.

Register conversion is sensitive to fixed-point scaling and truncation. `rq_dlg_get_dlg_reg()` floors line delivery values, multiplies request delivery by 2^10, line/destination values by 2^2, and ratios by 2^19. Several fields assert range, while VM/PTE group fields saturate. Differences between assert-and-clamp behavior can cause debug-only failures or silent max programming depending on field.

`dml2_core_calcs_get_informative()` computes `PrefetchMode[k]` from `out->display_config.plane_descriptors->overrides.reserved_vblank_time_ns` without indexing `[k]`. That means every plane appears to use plane 0's reserved vblank override for this informative field.

`rq_dlg_get_rq_reg()` treats `dml2_rgbe_alpha` as dual-plane and changes plane1 pixel chunk size to the alpha chunk size. Formats with chroma-like second planes and alpha planes share some paths but may have different hardware expectations.

The FAMS2 stream programming helper returns without touching output when `all_streams_blanked` is set. Callers need to ensure stale FAMS2 output memory is not reused when streams are blanked.

## Test Signals

Useful validation signals include:

- DML debug logs under `__DML_VBA_DEBUG__` for delivery times, PTE/meta/VM timings, prefetch support failures, immediate-flip support, VStartup placement, watermarks, stutter efficiency, DLG/RQ register values, and mcache allocation.
- Mode-programming return value from `dml2_core_calcs_mode_programming_ex()`, especially for cases where mode support succeeded but selected-mode prefetch or immediate flip fails.
- Per-pipe register dumps from `dml2_core_calcs_get_pipe_regs()`: `refcyc_per_*`, `dst_y_*`, `vratio_prefetch*`, RQ chunk/group sizes, DET size, and dual-plane `plane1_base_address`.
- Watermark register outputs from `dml2_core_calcs_get_watermarks()` compared against modeled `mode_lib->mp.Watermark` values and DCHUB refclk overrides.
- FAMS2 command payloads for vactive, vblank, DRR, SubVP, and blanked-stream scenarios.
- Informative fields for mode-support booleans, QoS bandwidth required/available, urgent fractions, stutter/Z8 efficiency, DPTE/meta row heights, delivery times, VM group/request times, DCC block controls, and lowest impacted prefetch margin.

High-risk scenario coverage should include:

- Single-plane and multi-plane configurations, including multiple planes sharing one stream and planes whose index differs from stream index.
- Chroma-less RGB, 4:2:0 dual-plane, and `dml2_rgbe_alpha` formats.
- GPUVM off/on, GPUVM page-table levels 1, 2, and greater than 2, HostVM on, and TDLUT on/off.
- DCC off/on with MRQ present and absent, including small meta chunks and rotated surfaces.
- Linear tiling with GPUVM enabled to exercise linear PTE row-height register programming.
- ODM bypass, 2:1, 3:1, 4:1, and MSO segment modes.
- Immediate flip not requested, explicitly requested, and implicitly required through HostVM.
- MALL unavailable, MALL available without MRQ, static-screen/SubVP cases, and mcache allocation paths.
- Writeback active versus inactive, because writeback affects delay, total bandwidth, p-state endpoints, and stutter eligibility.
- Interlaced timings with and without p-to-i support, because VStartup, frame time, and DLG vblank values are adjusted.

## Cross-Chunk Notes

Earlier chunks of this same source file define most helpers called by `dml_core_mode_programming()`: byte/block sizing, swath/DET allocation, VM row-byte calculation, MALL/mcache logic, available/required bandwidth calculations, prefetch scheduling, flip scheduling, watermarks, p-state keepout, latency helpers, and mode support. The merge lane should join this chunk with those earlier chunks so the final per-file report can describe the complete DCN4 calculation flow from mode-support selection through selected-mode programming and register export.
