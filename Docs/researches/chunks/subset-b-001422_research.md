# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core.c lines 5639-9969

## Scope

This chunk covers the backend half of AMD DC DML2 display-mode modeling. It starts at the tail of `CalculateRequiredDispclk()`, then defines clock, bandwidth, DSC, MALL, prefetch, immediate-flip, vstartup, and parameter-packing helpers. The main bodies are `dml_core_mode_support()`, `dml_core_mode_support_partial()`, and most of `dml_core_mode_programming()`. The range ends at the declaration/local setup of `dml_core_get_row_heights()`.

The code is computational and writes its results into `struct display_mode_lib_st` fields:

- `mode_lib->ms`: mode-support state, input/cache config, candidate state arrays, and support booleans.
- `mode_lib->mp`: final mode-programming outputs exposed by getter functions.
- `mode_lib->scratch`: large temporary structs used to keep stack use bounded.

## Purpose

The chunk answers two related questions for a cached display configuration and SOC/IP bounding box:

1. Can this display configuration be supported at the current power/SOC state?
2. If supported, what clocks, pipe split choices, prefetch schedule, memory-watermark values, row/PTE geometry, MALL usage, stutter metrics, and per-plane programming values should DC use?

`dml_core_mode_support()` is the admissibility pass. It evaluates constraints such as scaling/tap legality, source tiling/scan support, writeback limits, DSC/link capacity, ODM/MPC pipe availability, DPP/DISPCLK feasibility, VM row and PTE buffer limits, return bandwidth, ROB safety, MALL policy combinations, prefetch timing, dynamic metadata, immediate flip, pitch alignment, viewport bounds, clock-change watermarks, and USR retraining. It evaluates two candidate states indexed by `j`: no/less MPC combine and MPC combine, then selects `support.MaximumMPCCombine`.

`dml_core_mode_programming()` recomputes and materializes the selected/programmed values using either required, override, or state clocks from `struct dml_clk_cfg_st`. It fills the `mp` interface consumed by DML getters: calculated clocks, row heights, request delivery times, watermark values, vstartup/vready values, DCC block programming, bandwidth metrics, stutter efficiency, and best-case Z8 stutter fields.

## Important APIs, Types, and Helpers

### Public/top-level APIs in this range

- `dml_get_return_bw_mbps_vm_only(const struct soc_bounding_box_st *soc, ...)`: returns the VM-only urgent return bandwidth in MB/s as the minimum of SDP return, fabric, and DRAM paths, with strobe-vs-VM-only DRAM percentages selected from SOC data.
- `dml_get_return_bw_mbps(const struct soc_bounding_box_st *soc, ...)`: returns pixel-data return bandwidth. It picks pixel-only vs pixel-and-VM DRAM efficiency based on `HostVMEnable`.
- `dml_core_mode_support(struct display_mode_lib_st *mode_lib)`: full mode support check and candidate selection. Its return value is `mode_lib->ms.support.ModeIsSupported`.
- `dml_core_mode_support_partial(struct display_mode_lib_st *mode_lib)`: computes only the early max DET/compressed-buffer sizing, P2I pixel-clock adjustment, and return bandwidth; used when callers need partial support-stage values before full support.
- `dml_core_mode_programming(struct display_mode_lib_st *mode_lib, const struct dml_clk_cfg_st *clk_cfg)`: calculates final programming and exported metrics for a mode assumed to be supported.
- `dml_core_get_row_heights(...)`: begins at the end of the chunk. This API is intended to compute DPTE and META row heights from minimal surface/tiling/rotation/pitch input.

### Static helpers defined in this range

- `CalculateSinglePipeDPPCLKAndSCLThroughput()`: computes luma/chroma scaler throughput and minimum single-DPP DPPCLK. It handles 4:2:0/RGBE-alpha chroma cases and enforces at least `2 * PixelClock` when tap counts exceed 6.
- `CalculateDPPCLK()`: derives per-plane `Dppclk[]` from single-DPP requirements and `DPPPerSurface[]`, applies downspread, selects global max, rounds global DPPCLK to DFS granularity, then quantizes per-plane DPPCLK to 1/255 of global.
- `CalculateMALLUseForStaticScreen()`: greedily enables static-screen MALL on eligible surfaces. It starts with explicitly enabled surfaces, then adds smallest eligible `optimize` surfaces while total size fits `MALLAllocatedForDCNFinal`.
- `dml_get_return_dram_bw_mbps()`: DRAM-only counterpart to the return-bandwidth public helpers.
- `DSCDelayRequirement()`: computes DSC pipeline delay from DSC enablement, ODM mode, input BPC, output BPP, horizontal active/total, slice count, output format/encoder, and backend pixel clock. ODM 2:1 and 4:1 divide slices per DSC engine.
- `CalculateVActiveBandwithSupport()`: sums urgent-adjusted active luma/chroma/cursor plus meta/DPTE row bandwidth across surfaces and compares against `ReturnBW`.
- `CalculatePrefetchBandwithSupport()`: calculates worst-case prefetch bandwidth as the per-plane maximum of VM row, active-row, and prefetch-pixel demands. It also computes a version excluding phantom-pipe MALL prefetch.
- `CalculateBandwidthAvailableForImmediateFlip()`: subtracts the greater of active-read and prefetch-read demand from `ReturnBW`, leaving bandwidth for flip PTE/meta traffic.
- `CalculateImmediateFlipBandwithSupport()`: sums immediate-flip bandwidth demand across planes, replacing normal row traffic with `final_flip_bw` when required; also computes a non-MALL-prefetch variant.
- `MicroSecToVertLines()` and `CalculateMaxVStartup()`: convert nominal vblank timing to lines and clamp maximum vstartup by actual vblank, vblank-nom, vsync position, writeback delay, interlace behavior, and `DML_MAX_VSTARTUP_START`.
- `set_calculate_prefetch_schedule_params()`: packs support-stage arrays into `CalculatePrefetchSchedule_params_st` for one candidate `j` and plane `k`.
- `dml_prefetch_check()`: nested candidate/prefetch/vstartup search used by `dml_core_mode_support()`.
- `set_vm_row_and_swath_parameters()`: packs mode-support state into `CalculateVMRowAndSwath_params_st`.

### Important structs/enums referenced

- `struct display_mode_lib_st`: central context. This chunk relies on `ms`, `mp`, `scratch`, and top-level `policy`.
- `struct dml_core_mode_support_locals_st` and `struct dml_core_mode_programming_locals_st`: scratch-local fields including candidate search state, dummy arrays, DML pipe parameters, SOC parameter packs, and intermediate totals.
- Parameter-pack structs in `mode_lib->scratch`: `CalculatePrefetchSchedule_params_st`, `CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport_params_st`, `CalculateVMRowAndSwath_params_st`, `CalculateSwathAndDETConfiguration_params_st`, `CalculateStutterEfficiency_params_st`, `UseMinimumDCFCLK_params_st`.
- `struct DmlPipe`: per-plane pipe description passed to scheduling/VM helpers.
- Enums: `dml_source_format_class`, `dml_swizzle_mode`, `dml_rotation_angle`, `dml_odm_mode`, `dml_output_format_class`, `dml_output_encoder_class`, `dml_use_mall_for_pstate_change_mode`, `dml_use_mall_for_static_screen_mode`, `dml_immediate_flip_requirement`, prefetch/watermark clock-change support enums, and clock option enums in `dml_clk_cfg_st`.

## Control Flow

### Backend helper flow

Clock and bandwidth helpers are pure calculations over arrays and SOC/IP fields. They generally follow the DML style of passing output pointers or output arrays, mutating caller-provided storage, and using `dml_min`, `dml_max`, `dml_ceil`, `dml_floor`, and DFS rounding utilities. Debug builds emit extensive `dml_print()` traces under `__DML_VBA_DEBUG__`.

The return-bandwidth helpers model three bottlenecks:

1. DCFCLK return bus: `return_bus_width_bytes * DCFCLK`.
2. Fabric: `fabricclk * fabric_datapath_to_dcn_data_return_bytes`.
3. DRAM: `dram_speed * num_chans * dram_channel_width_bytes`.

The minimum is scaled by SOC efficiency percentages that differ for pixel-only, pixel+VM, VM-only, and strobe cases.

### `dml_prefetch_check()`

`dml_prefetch_check()` loops over `j = 0..1` candidate DPP/MPC states. For each candidate it:

1. Restores per-candidate swath, DET, DPP, compressed-buffer, and unbounded-request values from `*_all_states[j]`.
2. Checks vactive bandwidth with urgent burst factors.
3. Computes VM-only return bandwidth, host-VM inefficiency, and extra latency.
4. Initializes candidate prefetch modes and maximum vstartup.
5. Iterates over combinations of `MaxVStartup` and per-plane `PrefetchMode`.
6. For each plane, builds a `DmlPipe`, packs prefetch-schedule parameters, and calls `CalculatePrefetchSchedule()`.
7. Recomputes prefetch urgent burst factors and cursor prefetch bandwidth.
8. Checks prefetch bandwidth, destination line limits, dynamic metadata, and prefetch vertical ratio caps.
9. If prefetch is plausible, computes bandwidth available for immediate flip, total flip bytes, per-pipe flip schedule, and immediate-flip bandwidth support.
10. Adjusts the search: reduce vstartup when VM/row lines are too large, otherwise advance prefetch modes.
11. After the search, computes watermarks and DRAM/FCLK/USR support for that candidate.

The loop terminates once prefetch, dynamic metadata, VRatio, and immediate-flip requirements are met, or every prefetch-mode/vstartup combination is exhausted.

### `dml_core_mode_support()`

The support function is a long staged filter:

1. Count active planes and calculate maximum DET/min compressed buffer sizing.
2. Adjust pixel clocks for progressive-to-interlace when relevant.
3. Check scaler ratios/taps, source tiling/scan support, and per-format byte/block sizes.
4. Compute single-DPP swath widths and luma/chroma read bandwidth.
5. Compute writeback bandwidth and validate writeback latency, unit count, ratios, taps, and line-buffer use.
6. Compute minimum single-DPP DPPCLK/scaler throughput per plane.
7. Derive maximum swath width constraints from tiling, rotation, chroma, RGBE-alpha, DCC, and line-buffer capacity.
8. Choose DSC slice counts, then run a single-DPP swath/DET pass for viewport-size feasibility.
9. Detect incompatible MPC policies.
10. For each candidate `j`, select ODM mode and output link/DSC/FEC settings, then decide `NoOfDPP[j][k]`, MPC combine, total active DPPs, DISPCLK/DPPCLK requirements, DSCCLK support, DTBCLK support, DSC units/slices, DSC delay, swath/DET configuration, MALL surface sizes, VM row geometry, PTE/DCC meta buffer support, urgent latency, urgent burst factors, DCFCLK deep sleep, writeback delay, maximum vstartup, optional minimum DCFCLK, return bandwidth, ROB support, and total vactive bandwidth.
11. Call `dml_prefetch_check()` for detailed prefetch, immediate flip, dynamic metadata, and watermark checks.
12. Check cursor, pitch alignment, and viewport bounds.
13. Compose final `ModeSupport[j]` from all support flags and policy requirements.
14. Pick `support.MaximumMPCCombine` when candidate 1 is necessary or better for requested P-state/FCLK behavior, otherwise candidate 0.
15. Copy selected candidate values back into user-facing support outputs and the persistent `ms` runtime fields (`DCFCLK`, `ReturnBW`, `DPPPerSurface`, swath heights, DET sizes, output type/rate/BPP, DSC/FEC state).

The final `ModeIsSupported` is true if either candidate supports the mode.

### `dml_core_mode_support_partial()`

This is intentionally small. It prepares DET/compressed-buffer sizing, applies P2I pixel-clock adjustment, and updates `ms.ReturnBW` from the current `ms.DCFCLK`, `ms.FabricClock`, and `ms.DRAMSpeed`. It does not populate the full support decision matrix.

### `dml_core_mode_programming()`

Programming repeats several calculations with final hardware choices from `cache_display_cfg.hw` and clock options from `clk_cfg`:

1. Count active planes/pipes and compute pipe-plane mapping.
2. Choose DCFCLK from support result or override.
3. Compute required or selected DISPCLK and DPPCLK, then byte/block sizes and swath widths.
4. Recompute read bandwidth and full swath/DET configuration.
5. Compute DCFCLK deep sleep, DSCCLK, DSC delay, surface MALL sizes, VM/PTE/meta row geometry, host-VM inefficiency, total active DPP counts, urgent extra latency, writeback delay, urgent latency, and urgent burst factors.
6. Search for a programming prefetch solution by iterating `VStartupLines` upward from `__DML_VBA_MIN_VSTARTUP__` and advancing prefetch modes when the vstartup range is exhausted. It caps with an assertion after 2500 iterations.
7. During each iteration, it schedules prefetch per plane, computes prefetch bandwidth, enforces VRatio/destination-line/dynamic-metadata constraints, and optionally schedules immediate flip if mode support said immediate flip is supported.
8. Once a solution is found or all modes are exhausted, it calculates watermarks and writes them to `mp.Watermark` via `memmove()`.
9. It computes display pipe delivery times, meta/PTE times, VM group/request times, `MinTTUVBlank`, DCC configuration, vstartup adjustment, `MIN_DST_Y_NEXT_START`, `VREADY_AT_OR_AFTER_VSYNC`, read/write bandwidth totals, and stutter efficiency.
10. For `__DML_VBA_ALLOW_DELTA__`, it also computes best-case Z8 stutter assuming zero compressed-buffer reserved space; otherwise best-case values mirror normal Z8 values.

## State and Persistence Behavior

The code does not allocate persistent objects or perform I/O beyond debug printing. Persistence is in-place mutation of `mode_lib`.

Important state writes:

- `mode_lib->ms.support.*`: every support flag and final selected support outputs.
- `mode_lib->ms.*PerState`, `*ThisState`, and `*AllStates`: candidate-state arrays for clocks, DPP counts, swaths, DET sizes, VM row bytes, prefetch lines, return bandwidth, and watermarks.
- `mode_lib->ms.DRAMSpeed`, `FabricClock`, `SOCCLK`, `DCFCLK`, `ReturnBW`, `ReturnDRAMBW`: selected current operating values after support.
- `mode_lib->mp.*`: mode-programming outputs exposed by the getter layer, including calculated clocks, watermarks, urgent latency, row heights/bytes, delivery times, vstartup, DCC block limits, bandwidth totals, stutter metrics, and MALL/static-screen results.
- `mode_lib->scratch.*`: reused parameter packs and local arrays. These are transient, but because they live in `mode_lib`, callers must not assume scratch fields preserve previous calculation data.

The support pass copies some values into `mp` early for getter compatibility, for example `mode_lib->mp.UrgentLatency`. Programming later fills the full `mp` interface. Watermarks are copied with `memmove()` because the source and destination may alias.

## Dependencies and Integration Points

This chunk depends on earlier functions in the same file:

- Geometry and tiling: `CalculateBytePerPixelAndBlockSizes()`, `CalculateSwathAndDETConfiguration()`, `CalculateSwathWidth()`, `CalculateVMRowAndSwath()`, `CalculateSurfaceSizeInMall()`, `CalculateDCCConfiguration()`.
- Timing/scheduling: `CalculatePrefetchSchedule()`, `CalculatePrefetchMode()`, `CalculateTWait()`, `CalculateFlipSchedule()`, `CalculateVUpdateAndDynamicMetadataParameters()`, `CalculatePixelDeliveryTimes()`, `CalculateMetaAndPTETimes()`, `CalculateVMGroupAndRequestTimes()`.
- Clocks/watermarks: `CalculateRequiredDispclk()`, `RoundToDFSGranularity()`, `CalculateDCFCLKDeepSleep()`, `UseMinimumDCFCLK()`, `CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport()`, `CalculateUrgentBurstFactor()`, `CalculateUrgentLatency()`, `CalculateExtraLatency()`.
- Output/link: `CalculateODMMode()`, `CalculateOutputLink()`, `RequiredDTBCLK()`, `TruncToValidBPP()`, `dscceComputeDelay()`, `dscComputeDelay()`.
- Final metrics: `CalculateStutterEfficiency()`.

It also relies on DML math/macros and constants such as `dml_min3`, `dml_max4`, `dml_ceil`, `dml_floor`, `ASSERT`, `DML_MAX_VSTARTUP_START`, `__DML_VBA_MIN_VSTARTUP__`, `__DML_MAX_VRATIO_PRE__`, and `__DML_MAX_VRATIO_PRE_ENHANCE_PREFETCH_ACC__`.

Externally, this is integrated into the AMD display driver DML path. Callers cache IP/SOC/display config into `mode_lib`, run support, then run programming with selected/overridden clock config. The generated `ms.support` and `mp` values are consumed by later DML getter functions and hardware programming layers.

## Risks and Edge Cases

- Arithmetic uses mixed integer and floating types. Several divisions depend on nonzero pixel clock, backend pixel clock, `ReturnBW`, `DPPPerSurface`, DSC slices, and line time inputs. The code assumes earlier configuration validation prevents zero divisors.
- `CalculateSinglePipeDPPCLKAndSCLThroughput()` uses expressions such as `VTaps / 6` with integer `VTaps`; that preserves existing DML behavior but can be surprising for values below 6.
- `CalculateMALLUseForStaticScreen()` uses `MALLAllocatedForDCNFinal * 1024 * 1024` in `dml_uint_t`; very large MALL sizes could overflow if the type is narrow.
- Many arrays are indexed by `num_active_planes`, `j < 2`, and hardware max limits. Correctness depends on cached config arrays being sized to DML maximums.
- The support and programming prefetch searches mutate shared `ms`/`mp` arrays while probing candidates. Later steps rely on the selected candidate being copied back consistently.
- The mode-support immediate-flip condition comments mention HostVM invalidation, but one termination condition in `dml_prefetch_check()` uses `s->ImmediateFlipRequiredFinal` directly in an `||`; this is subtle and should be regression-tested when changing iflip policy logic.
- `dml_core_mode_programming()` asserts if prefetch search exceeds 2500 iterations. Pathological timing or policy combinations can trip this hard failure.
- There are multiple debug-only and unconditional `dml_print()` calls in hot computational paths. Logging behavior may affect trace volume in kernels/configurations where `dml_print` is enabled.
- `dml_core_mode_programming()` assumes the mode is already supported. If callers skip support or mutate cached config afterward, programming may still run into impossible schedules or assertions.
- MALL policy validation is spread across support checks: full-frame, sub-viewport, phantom-pipe, static-screen optimize/enable/disable, HostVM, and immediate flip combinations must remain synchronized with hardware policy definitions.
- The chunk contains comments marked `VBA_DELTA` and `VBA_ERROR`, signaling intentional deviations or known parity fixes versus the spreadsheet/VBA model; edits in these areas need extra care.

## Test Signals

Useful validation signals for this chunk include:

- Mode-support return and final flags: `ModeIsSupported`, `ModeSupport[0/1]`, `MaximumMPCCombine`, `DPPPerSurface[]`, `MPCCombineEnable[]`, `ODMMode[]`, `DSCEnabled[]`, `FECEnabled[]`, `OutputBpp[]`, `OutputRate[]`.
- Clock outputs: `RequiredDISPCLK[]`, `RequiredDPPCLKPerSurface[][]`, `DISPCLK_DPPCLK_Support[]`, `DCFCLKState[]`, `ProjectedDCFCLKDeepSleep[]`, programmed `mp.Dispclk_calculated`, `mp.Dppclk_calculated[]`, `mp.DSCCLK_calculated[]`.
- Bandwidth outputs: `ReturnBWPerState[]`, `ReturnDRAMBWPerState[]`, `VActiveBandwithSupport[]`, `PrefetchSupported[]`, `FractionOfUrgentBandwidth`, `FractionOfUrgentBandwidthImmediateFlip`, total data/read/write bandwidth fields.
- Scheduling outputs: `NoTimeForPrefetch[][]`, `DynamicMetadataSupported[]`, `VRatioInPrefetchSupported[]`, `DestinationLinesForPrefetch`, `DestinationLinesToRequestVMInVBlank`, `DestinationLinesToRequestRowInVBlank`, immediate flip destinations, `VStartup`, `VStartupMin`, `VUpdateOffsetPix`, `VUpdateWidthPix`, `VReadyOffsetPix`, `VREADY_AT_OR_AFTER_VSYNC`, `MIN_DST_Y_NEXT_START`.
- Memory/VM geometry outputs: `PTEBufferSizeNotExceeded[]`, `DCCMetaBufferSizeNotExceeded[]`, `dpte_row_height`, `meta_row_height`, `PixelPTEBytesPerRow`, `PDEAndMetaPTEBytesFrame`, `MetaRowByte`, `use_one_row_for_frame`, `use_one_row_for_frame_flip`.
- Watermark and power-state signals: `Watermark.*`, `DRAMClockChangeSupport`, `FCLKChangeSupport`, `USRRetrainingSupport`, `MaxActiveDRAMClockChangeLatencySupported`, `SubViewportLinesNeededInMALL`.
- MALL and DCC signals: `ExceededMALLSize`, `SurfaceSizeInMALL`, `UsesMALLForStaticScreen`, DCC max compressed/uncompressed and independent block outputs.
- Stutter metrics: `StutterEfficiency`, `StutterEfficiencyNotIncludingVBlank`, `NumberOfStutterBurstsPerFrame`, `Z8StutterEfficiency`, `Z8StutterEfficiencyBestCase`, `StutterPeriod`, `DCHUBBUB_ARB_CSTATE_MAX_CAP_MODE`.

Regression cases should cover single and multi-plane configs; 4:4:4, 4:2:0, mono, RGBE-alpha; linear and tiled surfaces; rotated surfaces; DCC on/off; HostVM/GPUVM on/off; writeback on/off; DSC disabled/2:1/4:1 ODM; DP/HDMI/FRL links; immediate flip required/not required; MALL full-frame/sub-viewport/phantom/static-screen modes; DRR/interlace/P2I; and max-power-state policy exceptions for DRAM/FCLK change support.
