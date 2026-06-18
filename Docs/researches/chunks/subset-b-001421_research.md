# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core.c

Chunk: `subset-b-001421`
Line range researched: 1-5638 of `display_mode_core.c`

## Purpose

This chunk is the front half of AMD DCN DML 2.0 display mode core math. It defines the local helper surface used later by the public mode-support and mode-programming entry points. The code is not a hardware programming path by itself; it is a deterministic calculator that takes SOC/IP/display configuration parameters and derives feasibility, clock, bandwidth, latency, swath, DET, DCC, VM/PTE, MALL, DSC/link, and ODM/DPP allocation values.

The chunk begins with constants and forward declarations, then implements helpers up through the start of `CalculateRequiredDispclk`. Public exported functions such as `dml_core_mode_support`, `dml_core_mode_programming`, and getter macros appear after this chunk and are not fully in scope here. The helpers in this chunk are nevertheless the main computational building blocks those later entry points call.

Important constants introduced here:

- `DML2_MAX_FMT_420_BUFFER_WIDTH` limits 4:2:0 ODM decisions to 4096-pixel buffer chunks.
- `TB_BORROWED_MAX` and `DML_MAX_VSTARTUP_START` are declared early for later timing/startup logic.
- Several formulas depend on global DML constants from included headers, including `__DML_NUM_PLANES__`, `__DML_MIN_DCFCLK_FACTOR__`, `__DML_MAX_VRATIO_PRE_OTO__`, `__DML_ARB_TO_RET_DELAY__`, and `__DML_DPP_INVALID__`.

## Main APIs And Types

This chunk is dominated by `static` helpers, so its API boundary is internal to `display_mode_core.c`. Shared data is passed through DML parameter structs declared in the companion headers:

- `struct display_mode_lib_scratch_st` carries per-helper temporary storage. Helpers such as `CalculatePrefetchSchedule`, `CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport`, `UseMinimumDCFCLK`, and `CalculateVMRowAndSwath` take `scratch` and use named local-storage substructs to avoid large stack frames.
- `struct CalculatePrefetchSchedule_params_st`, `CalculateVMRowAndSwath_params_st`, `CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport_params_st`, `CalculateStutterEfficiency_params_st`, `CalculateSwathAndDETConfiguration_params_st`, and `UseMinimumDCFCLK_params_st` carry large input/output bundles.
- `struct dml_display_cfg_st` is modified by `PixelClockAdjustmentForProgressiveToInterlaceUnit`.
- Enums drive most branch selection: source pixel formats, swizzle modes, rotations, output encoders, output formats, ODM modes and policies, DSC enable modes, MALL modes, unbounded requesting policy, prefetch support modes, immediate flip requirements, and DRAM/FCLK support result enums.

Important function groups in this chunk:

- Pixel/block/tile geometry: `CalculateBytePerPixelAndBlockSizes`, `CalculateSwathWidth`, `CalculateSwathAndDETConfiguration`, `CalculateSurfaceSizeInMall`.
- DCC/VM/PTE row geometry: `CalculateDCCConfiguration`, `CalculateVMAndRowBytes`, `CalculateVMRowAndSwath`, `CalculateMetaAndPTETimes`, `CalculateVMGroupAndRequestTimes`, `CalculateRowBandwidth`.
- Timing and prefetch: `CalculateVUpdateAndDynamicMetadataParameters`, `CalculatePrefetchSourceLines`, `CalculatePrefetchSchedule`, `CalculateTWait`, `CalculatePrefetchMode`, `CalculateFlipSchedule`.
- Clock/bandwidth/latency: `RoundToDFSGranularity`, `CalculateDCFCLKDeepSleep`, `CalculateUrgentBurstFactor`, `CalculatePixelDeliveryTimes`, `CalculateExtraLatency`, `CalculateExtraLatencyBytes`, `CalculateUrgentLatency`, `UseMinimumDCFCLK`.
- Output/link/ODM: `TruncToValidBPP`, `RequiredDTBCLK`, `dscceComputeDelay`, `dscComputeDelay`, `CalculateOutputLink`, `CalculateODMMode`, and the opening of `CalculateRequiredDispclk`.
- Buffer allocation: `CalculateDETBufferSize`, `CalculateMaxDETAndMinCompressedBufferSize`, `UnboundedRequest`.

## Control Flow Summary

The intended whole-file flow, inferred from this chunk and helper names, is:

1. Convert display/source configuration into per-plane bytes-per-pixel, 256-byte request block sizes, and macro-tile dimensions.
2. Select ODM/DPP topology and required display clocks based on active width, output format, DSC usage, available pipes, DISPCLK limits, and ODM policy.
3. Compute swath widths/heights, DET allocation, compressed buffer size, and unbounded-request eligibility.
4. Compute VM/PTE/DCC row geometry, prefetch source line counts, meta row bytes, PTE bytes per row, one-row-per-frame eligibility, PTE buffer mode, and row bandwidth.
5. Compute dynamic metadata and vupdate timing, then build prefetch schedules for VM, row, and pixel data within `VStartup`.
6. Compute delivery times, urgent burst factors, watermarks, DRAM/FCLK/USR retraining support, stutter efficiency, and immediate flip support.
7. Compute output link BPP, DSC/FEC requirements, DP/DP2/eDP/HDMI output type/rate, and DTBCLK requirements.

The helpers are highly compositional. For example:

- `CalculateSwathAndDETConfiguration` calls `CalculateSwathWidth`, `UnboundedRequest`, and `CalculateDETBufferSize`, then derives viewport support and DET split between luma/chroma.
- `CalculateVMRowAndSwath` calls `CalculateVMAndRowBytes` for chroma and luma, `CalculatePrefetchSourceLines`, `CalculateMALLUseForStaticScreen`, and `CalculateRowBandwidth`, then sets PTE buffer modes and one-row-for-frame behavior.
- `CalculatePrefetchSchedule` calls `CalculateVUpdateAndDynamicMetadataParameters`, computes `Tvm`, `Tr0`, `Tsw`, and `dst_y_prefetch`, chooses among four bandwidth cases, and returns a boolean error flag after zeroing outputs on schedule failure.
- `CalculateOutputLink` repeatedly calls `TruncToValidBPP` while trying ordered link rates and toggling DSC when `dml_dsc_enable_if_necessary` allows fallback compression.
- `CalculateODMMode` calls `CalculateRequiredDispclk` for bypass, 2:1 combine, and 4:1 combine candidates, then chooses an ODM mode based on policy, output constraints, DSC slice limits, active width, state DISPCLK, and remaining DPP pipe count.

`CalculateRequiredDispclk` starts in this chunk but does not finish before line 5638. This chunk shows it deriving `PixelClockAfterODM` for bypass/2:1/4:1 and beginning DFS-rounded DISPCLK calculations with downspreading and ramping margin; the rest is in the next chunk.

## Function-Level Notes

### DSC And Output Link Helpers

`dscceComputeDelay` calculates DSC codec engine delay in pixels using bpc, compressed BPP, slice width/count, output format, and output encoder. It models pixel containers per clock, initial transmit delay, SSM delay, stall cases, and slice interleaving. `dscComputeDelay` adds fixed pipeline stage delays for 4:2:0, native 4:2:2, and other formats.

`TruncToValidBPP` validates or chooses an output bits-per-pixel value. It computes max link BPP for DP2 with 128b/132b plus FEC framing factors, DP with optional DSC overhead, and legacy link encodings. It enforces legal non-DSC BPP triplets per format and DSC min/max ranges based on input bpc. Return value `__DML_DPP_INVALID__` signals no valid BPP.

`CalculateOutputLink` evaluates HDMI, DP, DP2.0, and eDP. For DP/eDP it tries HBR, HBR2, then HBR3; for DP2 it tries UHBR10, UHBR13.5, then UHBR20. It sets `RequiresDSC`, `RequiresFEC`, `OutBpp`, output type/rate, and required slots. A notable behavior is the conditional DSC retry when link BPP is zero, DSC is "if necessary", and there is no forced BPP.

`RequiredDTBCLK` derives DTBCLK for compressed and uncompressed paths. DSC mode considers pixel word rate, active tribyte rate, blanking/audio overhead, and applies a 1.002 multiplier.

### Prefetch And Timing Helpers

`CalculateVUpdateAndDynamicMetadataParameters` computes vupdate width/offset, vready offset, setup time, dynamic metadata buffer/engine/skin times, and interlace adjustment. These values feed both prefetch scheduling and minimum DCFCLK logic.

`CalculateTWait` maps prefetch mode and MALL/pstate constraints to a wait time. Mode 0 accounts for DRAM clock change plus urgent latency when not using MALL pstate change and not synchronized DRR; mode 1 accounts for FCLK; mode 2 accounts for stutter only; mode 3 falls back to urgent latency.

`CalculatePrefetchMode` converts policy enum values into a min/max prefetch-mode scan range. `*_if_possible` scans modes 0 through 3, while explicit requirements lock min and max to one value.

`CalculatePrefetchSourceLines` calculates `VInitPreFill`, `MaxNumSwath`, and returned prefetch source lines from vratio, taps, interlace mode, swath height, rotation, viewport stationarity, and viewport starts.

`CalculatePrefetchSchedule` is one of the central helpers. It:

- Initializes a large scratch-local struct.
- Computes host VM dynamic trip count.
- Calls dynamic metadata/vupdate timing logic.
- Calculates line time, VM-trip time, dynamic metadata latency, DPP/DISPCLK pipeline delay, and `DSTX/YAfterScaler`.
- Rounds VM and row-request times to quarter-line units.
- Computes prefetch pixel bytes and one-time-only versus equalized schedules.
- Chooses among four bandwidth cases based on whether VM and row fetch times are bandwidth-dominated or latency-dominated.
- Derives `DestinationLinesToRequestVMInVBlank`, `DestinationLinesToRequestRowInVBlank`, `DestinationLinesForPrefetch`, `VRatioPrefetchY/C`, required prefetch pixel data bandwidth, and combined VM/row prefetch bandwidth.
- On any invalid schedule, resets the schedule outputs to zero and returns `true` as an error indicator.

There are several unconditional `dml_print` calls in this function, not only under `__DML_VBA_DEBUG__`, for tracing prefetch and error conditions.

### Pixel, Block, Swath, DET, And MALL

`CalculateBytePerPixelAndBlockSizes` maps source pixel format and tiling to luma/chroma byte sizes, DET byte sizes, 256-byte block width/height, and macro-tile width/height. Special cases include `dml_rgbe_alpha`, 4:2:0 8/10/12-bit, linear surfaces, 64KB swizzles, and larger tiled modes.

`CalculateSwathWidth` computes single-DPP and per-pipe luma/chroma swath widths. It accounts for rotation, ODM combine modes, `ForceSingleDPP`, DPP-per-surface, 4:2:0 chroma halving, viewport stationarity, and read-block alignment. It also returns maximum swath heights and aligned upper-bound swath widths.

`CalculateDETBufferSize` allocates DET buffer in KB. In unbounded mode it sizes the only active surface for two swaths or a DET override and gives the remainder to compressed buffer. Otherwise it:

- Starts from `MaxTotalDETInKByte`.
- Assigns per-surface minimum DET where two swaths fit, respecting overrides and phantom pipes.
- Computes total read bandwidth of non-phantom surfaces.
- Marks surfaces already fairly allocated by bandwidth share.
- Iteratively assigns remaining DET pieces, choosing lower-bandwidth unassigned surfaces and rounding to return-buffer segment size.
- Sets compressed buffer to the minimum compressed buffer size and rescales by final compressed-buffer segment size.

`CalculateMaxDETAndMinCompressedBufferSize` derives `MaxTotalDETInKByte`, nominal DET per DPP, and minimum compressed buffer size from return-buffer config. It allows an explicit nominal DET override.

`CalculateSwathAndDETConfiguration` ties swath geometry and DET allocation together. It derives rounded max swath sizes, detects unbounded request eligibility, allocates DET/compressed buffer, selects full or half swath heights based on DET fit, sets viewport support flags, splits DET between luma/chroma, and computes compressed-buffer reserved space.

`CalculateSurfaceSizeInMall` computes per-surface MALL footprint for static-screen use, including DCC metadata footprint when enabled. It uses tighter viewport-aligned calculations for stationary viewports and expanded viewport+block calculations for moving viewports. It reports `ExceededMALLSize` if enabled static-screen surfaces exceed `MALLAllocatedForDCN`.

`UnboundedRequest` returns true only when the policy permits it, exactly one active DPP is present, no chroma/linear surface blocks it, and the eDP-only policy is satisfied when selected.

`CalculateMALLUseForStaticScreen` is declared in this chunk and called by `CalculateVMRowAndSwath`; its implementation begins after line 5638 and is outside this chunk.

### DCC, VM, PTE, Row, And Request Timing

`CalculateDCCConfiguration` determines DCC max uncompressed/compressed/independent block sizes for luma and chroma. It computes DET-limited viewport bounds, effective surface extents, full swath byte counts for horizontal/vertical access, whether 128-byte requests are needed, and whether 128-byte requests are contiguous or non-contiguous. It handles unknown scan-direction programming by taking both horizontal and vertical requirements, otherwise it uses rotation to choose the active path. Outputs are zeroed when DCC is disabled, and chroma outputs are zeroed when no chroma plane exists.

`CalculateVMAndRowBytes` is the low-level row byte calculator. It computes:

- Meta request width/height, meta row width/height, and meta row byte count.
- DCC meta surface byte footprint and meta PTE bytes per frame.
- DPDE0 bytes and extra PDE bytes for GPUVM page table levels.
- Total PDE/meta PTE bytes per frame.
- Pixel PTE request width/height and request size for linear, 4KB, and larger page sizes.
- One-row-per-frame DPTE row dimensions and bytes.
- Active DPTE row height/width/bytes for linear, tiled horizontal, and tiled vertical rotations.
- Linear row height programming value.

If GPUVM is disabled, pixel PTE bytes per row are zeroed. If DCC is disabled, meta row/PTE bytes are zeroed. The function returns combined PDE/meta PTE bytes before host VM multiplier.

`CalculateVMRowAndSwath` orchestrates VM row computation per active surface. It chooses `vm_group_bytes` and `dpte_group_bytes` based on host VM/GPUVM and vertical rotation, splits PTE buffer request counts between luma/chroma for multi-plane formats, calls `CalculateVMAndRowBytes` for chroma then luma, computes prefetch source lines, combines host-VM-expanded PDE/meta PTE bytes, checks PTE buffer fit, checks one-row-per-frame fit, invokes MALL static-screen selection, derives `PTE_BUFFER_MODE`, `BIGK_FRAGMENT_SIZE`, `use_one_row_for_frame`, `use_one_row_for_frame_flip`, DCC meta buffer support, host-VM-expanded row bytes, total pixel PTE bytes per row, and row bandwidth.

One subtle risk in this helper is that `PTE_BUFFER_MODE` is first assigned from override fields, then immediately overwritten by the computed expression. If that is intentional, the override only has transient effect and should be verified against downstream expectations.

`CalculateRowBandwidth` computes metadata and DPTE row bandwidth from row bytes, row heights, vratio, chroma vratio, line time, and DCC/GPUVM enablement.

`CalculateMetaAndPTETimes` converts row geometry into nominal/vblank/flip time per meta chunk and PTE group. It computes chunks per row from meta chunk size and minimum meta chunk size, handles luma/chroma separately, handles vertical rotation widths, and halves group counts in one-row-for-frame mode.

`CalculateVMGroupAndRequestTimes` computes VM group/request times for vblank and flip. It counts lower-stage VM groups and 64-byte requests from DPDE0 and meta PTE bytes, with separate branches for DCC disabled, DCC enabled with one page-table level, and DCC enabled with multiple levels. For GPUVM page table levels above 2, it halves the computed times.

### Watermarks, Latency, DCFCLK, And Stutter

`CalculateWatermarksMALLUseAndDRAMSpeedChangeSupport` computes urgent, USR retraining, DRAM/FCLK change, stutter, Z8 stutter, and writeback watermarks. It then computes line-buffer latency hiding, effective DET buffering, active DRAM/FCLK/USR margins, writeback margins, maximum active DRAM/FCLK latency support, synchronized surface relationships, FCLK support enum, DRAM clock change support enum including MALL full-frame/subviewport variants, and subviewport lines needed in MALL.

`CalculateDCFCLKDeepSleep` computes per-surface deep-sleep DCFCLK based on luma/chroma delivery time and aggregate read bandwidth over return bus width. It enforces a minimum of 8 and at least pixel clock / 16 per surface.

`CalculateUrgentBurstFactor` computes cursor, luma, and chroma urgent burst factors from buffer time divided by buffer time minus urgent latency. It sets `NotEnoughUrgentLatencyHiding` and zero burst factor if the corresponding buffer cannot hide urgent latency. Phantom pipes use an effectively huge DET size.

`CalculatePixelDeliveryTimes` computes line delivery and request delivery times for luma, chroma, prefetch luma/chroma, and cursor. It selects pixel-clock based formulas for ratios <= 1 and DPPCLK/PSCL throughput formulas for ratios > 1. Request delivery time divides by aligned requests per swath.

`CalculateExtraLatencyBytes` and `CalculateExtraLatency` account for reordering bytes, active DPP pixel chunks, DCC meta chunks, GPUVM DPTE groups, host VM dynamic levels, and fabric return bandwidth. `CalculateHostVMDynamicLevels` reduces dynamic levels as host page size grows.

`CalculateUrgentLatency` selects the max of pixel-only, mixed, and VM-only urgent latencies, with optional fabric-clock adjustment.

`UseMinimumDCFCLK` computes two candidate DCFCLK states. For each state it estimates average bandwidth, extra latency cycles, per-surface prefetch pixel cycles, required peak bandwidth, dynamic metadata constraints, and maximum prefetch timing. It caps the chosen state at `DCFCLKPerState` and applies a 1.05 multiplier to the max of average and peak requirements.

`CalculateStutterEfficiency` calculates DCC-compressed bandwidth, zero-size request effects, effective compressed buffer size, critical surface DET buffering period, stutter burst time, stutter efficiencies with and without vblank, Z8 variants, stutter burst counts, and `DCHUBBUB_ARB_CSTATE_MAX_CAP_MODE`. Writeback disables stutter efficiency in this model. The function uses the most restrictive non-phantom surface as the critical surface.

### Immediate Flip And Writeback

`CalculateFlipSchedule` derives immediate-flip VM and row request destination lines, final flip bandwidth, and per-pipe support. It accounts for host VM trips, one-row-for-frame flip, PDE/meta/PTE bytes, immediate flip bandwidth share, line-time quarter-line rounding, source format chroma rules, row-time minimums, and hard register-like limits: VM lines must be below 32 and row lines below 16.

`CalculateWriteBackDISPCLK` returns the DFS-rounded maximum of horizontal, vertical, and line-buffer writeback DISPCLK constraints. `CalculateWriteBackDelay` computes writeback output delay from vinit, destination/source dimensions, line length, and HTotal.

### Pixel Clock And DFS Helpers

`PixelClockAdjustmentForProgressiveToInterlaceUnit` sets `PixelClockBackEnd[k]` to the original timing pixel clock and doubles `timing.PixelClock[k]` for interlaced timings when progressive-to-interlace is supported. This mutates `display_cfg` in place.

`RoundToDFSGranularity` rounds a clock to DFS granularity using `VCOSpeed * 4 / floor(...)` for round-up and `/ ceil(...)` for round-down. Zero or negative input returns zero.

### ODM

`CalculateODMMode` determines DPP count and ODM mode per surface. It forces or rejects certain ODM modes for 4:2:0 width limits and HDMI/DP/eDP restrictions. It evaluates bypass, 2:1 combine, and 4:1 combine required DISPCLK values. It selects 4:1 combine for forced 4:1 or combine-as-needed cases where 2:1 is insufficient, DSC line limits are exceeded, or DSC slices exceed 8. It selects 2:1 combine for forced 2:1 or combine-as-needed cases where bypass exceeds state DISPCLK but 2:1 fits, DSC line limit is exceeded, or slice counts are 5-8. It rejects configurations when available DPP pipes would be exceeded.

## State And Persistence Behavior

This chunk has no durable persistence, file IO, or hardware register writes. State is carried through:

- Output pointer parameters and arrays in the parameter structs.
- `mode_lib`/display config structures passed from later code, especially `display_cfg` mutation in `PixelClockAdjustmentForProgressiveToInterlaceUnit`.
- `display_mode_lib_scratch_st` local scratch substructures used as temporary working storage.
- Debug/log output through `dml_print`.
- Assertions through `ASSERT`.

Several helpers initialize scratch locals explicitly at entry, but many array outputs are only assigned on active branches. Callers must provide correctly sized arrays and valid per-surface counts. Because most functions operate on `NumberOfActiveSurfaces`, stale values beyond that count are intentionally untouched.

## Dependencies And Integration Points

Direct includes:

- `display_mode_core.h` for public structs, enums, and function declarations.
- `display_mode_util.h` for math helpers such as `dml_max`, `dml_min`, `dml_floor`, `dml_ceil`, `dml_round`, `dml_log2`, `dml_is_vertical_rotation`, and plane count helpers.
- `display_mode_lib_defines.h` for constants and limits.
- `dml_assert.h` for `ASSERT`.

The calculations are integrated with the AMD DRM display stack through the DML mode support/programming path. Later whole-file functions use these helpers to decide whether a display configuration can be supported, what clocks/watermarks/pipe topology are required, and what programming values should be exposed through getter helpers.

The code is heavily coupled to DCN hardware concepts: DPP, DSC, ODM, DET, MALL, ROB, DCC, GPUVM/HostVM, PTE/DPTE, FCLK/UCLK/DCFCLK/DISPCLK/DPPCLK/DTBCLK, DP/eDP/HDMI/DP2 link rates, and vblank/vstartup timing.

## Risks And Edge Cases

- Division-by-zero risk exists if caller-provided clocks, line totals, ratios, widths, byte sizes, chunk sizes, or group counts are zero where formulas assume valid hardware inputs. Some branches guard zero clocks or disabled features, but not every denominator is locally validated.
- `CalculatePrefetchSchedule` returns `true` on error and `false` on success, which is easy to invert in callers.
- Several unconditional `dml_print` calls may produce noisy logs even outside `__DML_VBA_DEBUG__`, especially in prefetch, VM row, DET allocation, DCFCLK, and stutter paths.
- `CalculateVMRowAndSwath` appears to overwrite `PTE_BUFFER_MODE` after applying `PTEBufferModeOverrideEn/Val`; this may defeat the override unless later chunks compensate.
- Many calculations cast floating-point results to unsigned integer types after rounding. Off-by-one and precision behavior is significant, and comments mention VBA rounding/precision differences.
- Host VM multipliers can greatly inflate PTE byte counts using `(1 + 8 * HostVMDynamicLevels)`. Overflow should be considered for extreme page-table/surface inputs.
- `CalculateDETBufferSize` assumes meaningful total bandwidth when allocating by bandwidth share. Zero total bandwidth would make share formulas unsafe.
- `CalculateDCCConfiguration` uses effective viewport limits, request classifications, and scan-direction assumptions. Mismatches between DCC programming scan direction and actual rotation could produce wrong block size programming.
- Output link selection treats `OutBpp == 0` as no valid link candidate in several branches, while `TruncToValidBPP` returns `__DML_DPP_INVALID__` for invalid BPP. Callers should verify how that sentinel compares with zero in downstream logic.
- 4:2:0 active-width ODM restrictions can force ODM policy changes or reject combinations for HDMI/DP/eDP. Regression tests need coverage for boundary widths around 4096, 8192, and 16384.
- The chunk ends mid-function in `CalculateRequiredDispclk`; whole-file interpretation of required DISPCLK requires the next chunk.

## Test Signals

Useful test and review signals for this chunk:

- Golden DML vector tests comparing mode-support outputs against known AMD/VBA spreadsheet or firmware reference values.
- Boundary tests for source pixel formats: 4:4:4 64/32/16/8, mono, RGBE, RGBE alpha, 4:2:0 8/10/12, and native 4:2:2 output formats.
- Tiling and rotation matrix tests for linear, 64KB, larger tiled modes, horizontal versus vertical rotation, stationary versus moving viewports.
- DCC enabled/disabled tests checking luma/chroma max compressed block outputs and meta row byte behavior.
- GPUVM/HostVM tests across page table levels, host page sizes, GPUVM min page sizes, 4KB versus large page paths, and one-row-for-frame mode.
- Prefetch schedule tests where `VStartup` barely fits or barely fails, including dynamic metadata enabled/disabled and dynamic metadata VM enabled.
- Immediate flip tests for VM-line >= 32, row-line >= 16, and min-row-time violations.
- DET allocation tests with overrides, phantom pipes, unbounded request, multiple surfaces with unequal bandwidth, chroma formats, and segment-size rounding.
- Link tests for HDMI, DP HBR/HBR2/HBR3, eDP, and DP2 UHBR10/UHBR13.5/UHBR20 with forced BPP, DSC required, DSC-if-necessary fallback, FEC expectation, and required slots.
- ODM tests for forced bypass/2:1/4:1/split/MSO, combine-as-needed, DSC slice thresholds, max DPP exhaustion, and 4:2:0 width thresholds.
- Stutter efficiency tests with DCC, zero-size fractions, writeback enabled, synchronized versus unsynchronized timings, Z8 paths, and single-plane/single-pipe cap mode.

## Chunk Boundary Notes

The assigned range fully covers the declarations and implementations through `CalculateODMMode`. It includes only the beginning of `CalculateRequiredDispclk`; the remainder of that function, DPPCLK helpers, return bandwidth helpers, full mode-support/programming entry points, and getter functions are outside this chunk and must be reconciled by later chunk reports before the final per-file report is produced.
