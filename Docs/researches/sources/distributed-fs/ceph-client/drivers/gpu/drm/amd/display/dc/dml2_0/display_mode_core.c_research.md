# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001421`: lines 1-5638, `Docs/researches/chunks/subset-b-001421_research.md`
- `subset-b-001422`: lines 5639-9969, `Docs/researches/chunks/subset-b-001422_research.md`
- `subset-b-001423`: lines 9970-10362, `Docs/researches/chunks/subset-b-001423_research.md`

## Chunk Research

### subset-b-001421: lines 1-5638

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

### subset-b-001422: lines 5639-9969

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

### subset-b-001423: lines 9970-10362

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/display_mode_core.c lines 9970-10362

## Scope And Purpose

This chunk is the public-facing tail of the DML2.0 display-mode core implementation. It sits after the large internal mode-support and mode-programming formula paths and exposes their results to the rest of the AMD display driver. The code covered here has three main purposes:

- Finish `dml_core_get_row_heights()`, a minimal helper for computing DPTE and META row heights from source format, tiling, scan direction, pitch, GPUVM page size, and the DML IP buffer limits.
- Prepare and invoke the core mode-support and mode-programming passes through `dml_mode_support()`, `dml_mode_programming()`, and `dml_mode_support_ex()`.
- Define many small getter functions that export calculated watermarks, clock requirements, DLG timing values, VM/PTE/meta request timing, DET sizing, MALL sizing, DCC block information, and related per-surface values from `mode_lib->ms` and `mode_lib->mp`.

The chunk is therefore a boundary layer: the heavy math is performed by earlier functions such as `dml_core_mode_support()`, `dml_core_mode_support_partial()`, `dml_core_mode_programming()`, `CalculateBytePerPixelAndBlockSizes()`, and `CalculateVMAndRowBytes()`, while this code initializes the persistent calculation state and provides typed accessors for downstream DC programming code.

## Important APIs, Types, And Functions

`dml_core_get_row_heights()` is declared in `display_mode_core.h` and implemented just before and within this chunk. The covered portion selects luma or chroma parameters based on `is_plane1`, chooses the matching `dpte_buffer_size_in_pte_reqs_luma` or `dpte_buffer_size_in_pte_reqs_chroma` from `mode_lib->ip`, and calls `CalculateVMAndRowBytes()` with a reduced synthetic configuration. It asks that lower helper to compute only the DPTE and META row heights, sending all other outputs to a local `dummy_integer[16]` array.

`dml_get_soc_state_bounding_box()` is a static state-table accessor. It validates `state_idx` against `states->num_states`, asserts on out-of-range input, and returns `states->state_array[state_idx]` by value. This guards the setup path for every public support/programming call in this chunk.

`cache_ip_soc_cfg()` copies caller-visible DML inputs into `mode_lib->ms`, the mode-support working/persistent struct. It records the selected state index, maximum state index, SOC bounding box, IP parameters, policy, selected state bounding box, and maximum state bounding box.

`cache_display_cfg()` copies the whole `struct dml_display_cfg_st` into `mode_lib->ms.cache_display_cfg`. This cached copy is what the core calculations and getters use after the public entry point returns.

`fetch_socbb_params()` initializes the active clocks in `mode_lib->ms` from the selected SOC state: `SOCCLK`, `DRAMSpeed`, `FabricClock`, and `DCFCLK`. Later mode-support logic can replace some of these, especially when a minimum required DCFCLK policy is used.

`dml_mode_support()` is the single-state support entry point. It refreshes the cached IP/SOC/policy/display configuration, fetches state clocks, calls `dml_core_mode_support(mode_lib)`, and returns the boolean support result. The detailed evaluation data remains in `mode_lib->ms.support`.

`dml_mode_programming()` is the programming-value entry point. It builds a local `struct dml_clk_cfg_st` with `dml_use_required_freq` for DCFCLK, DISPCLK, and every DPPCLK entry, refreshes the same cached state/configuration, optionally runs `dml_core_mode_support_partial()` for standalone use, then calls `dml_core_mode_programming(mode_lib, &clk_cfg)`. It returns `mode_lib->mp.PrefetchAndImmediateFlipSupported`, so callers treat failure as inability to produce a valid programming set for the selected configuration.

`mode_support_pwr_states()` is a private search helper used by `dml_mode_support_ex()`. It scans a closed state-index range from `start_state_idx` to `end_state_idx`, calling `dml_mode_support()` for each state until one succeeds, and writes the first passing index to `*lowest_state_idx`.

`dml_mode_support_ex()` packages the multi-state search for wrapper code. It reads a `struct dml_mode_support_ex_params_st`, searches from `in_start_state_idx` through the highest available state, and on success copies `mode_lib->ms.support` to `*out_evaluation_info`.

`dml_get_is_phantom_pipe()` maps a pipe index to a plane index through `mode_lib->mp.pipe_plane[pipe_idx]` and checks whether that plane's cached `UseMALLForPStateChange` mode is `dml_use_mall_pstate_change_phantom_pipe`.

The two local getter macros define most of the exported API surface:

- `dml_get_var_func(name, type, expr)` creates whole-mode getters such as `dml_get_wm_urgent()`, `dml_get_return_bw()`, and `dml_get_total_immediate_flip_bytes()`.
- `dml_get_per_surface_var_func(name, type, array)` creates per-surface getters. Despite the parameter name `surface_idx`, the implementation treats the incoming index as a DML pipe index, maps it through `mode_lib->mp.pipe_plane[surface_idx]`, and returns the corresponding plane-array value.

The generated getters in this chunk fall into several groups:

- Watermark and latency getters: urgent, stutter, Z8 stutter, DRAM clock change, FCLK change, USR retraining, writeback urgent, writeback DRAM clock change, urgent latency, urgent extra latency, and max active FCLK/DRAM clock-change latency.
- Clock and bandwidth getters: DCFCLK deep sleep, calculated DISPCLK, calculated DPPCLK/DSCCLK, total data read bandwidth, return bandwidth, return DRAM bandwidth, and `TCalc`.
- Buffer and chunk getters: compressed buffer size, pixel/alpha/meta chunk sizes, minimum pixel/meta chunk bytes, DET buffer sizes, DPTE group size, VM group size, total immediate-flip bytes, PTE buffer mode, and BIGK fragment size.
- Prefetch/DLG timing getters: VStartup, VUpdate/VReady offsets, prefetch ratios, destination lines for VM/row requests in vblank and immediate flip, line/request delivery times, cursor request delivery times, metadata chunk times, and PTE-group times.
- Surface-geometry and compression getters: swath heights, DPTE/META row heights, DST after scaler, MALL static-screen use, MALL surface size, and DCC max/independent block values for luma and chroma.

## Control Flow

The first covered block is inside `dml_core_get_row_heights()`. The function has already declared luma/chroma byte, block, and macro-tile locals before line 9970. In this chunk it:

1. Calls `CalculateBytePerPixelAndBlockSizes()` using `SourcePixelFormat` and `SurfaceTiling`.
2. Selects the luma or chroma byte/block/macro-tile values based on `is_plane1`.
3. Selects the luma or chroma DPTE buffer request limit from `mode_lib->ip`.
4. Calls `CalculateVMAndRowBytes()` with enough fixed inputs to force the VM/PTE/META row-height calculations: viewport is treated as non-stationary, DCC is enabled, one DPP is used, GPUVM is enabled, max page-table levels is hardcoded as four, swath width and viewport dimensions are zero, and `pitch`/`GPUVMMinPageSizeKBytes` are caller-provided.
5. Captures only `*dpte_row_height` and `*meta_row_height`; every other output is intentionally discarded into `dummy_integer`.

The support/programming entry points follow a repeated setup pattern. `dml_mode_support()` and `dml_mode_programming()` both call `cache_ip_soc_cfg()`, `cache_display_cfg()`, and `fetch_socbb_params()` before invoking core calculation. This means every public pass resets `mode_lib->ms` to match the selected state, current top-level bounding boxes, policy, and display configuration before formula code runs.

`dml_mode_programming()` has an extra standalone branch. When `call_standalone` is true, it pre-seeds `mode_lib->ms.support.ImmediateFlipSupport` to true and runs `dml_core_mode_support_partial()`. This provides the subset of support fields required by programming when the caller did not first run a complete support check. After that, all programming outputs are computed by `dml_core_mode_programming()` into `mode_lib->mp`.

`mode_support_pwr_states()` validates the requested search range with assertions, initializes the output lowest state to `end_state_idx`, then scans upward. The first state for which `dml_mode_support()` returns true becomes the selected lowest supported state. If none pass, the function returns false and leaves `*lowest_state_idx` at the end-state default.

`dml_mode_support_ex()` uses that helper to implement the usual "find the lowest supporting voltage/SOC state" flow. On success, it copies the populated `mode_lib->ms.support` summary into the caller-provided `out_evaluation_info`. On failure, it does not refresh `out_evaluation_info`, which keeps failed evaluations from being mistaken for valid support data.

The getter section has no branching beyond pipe-to-plane mapping. Whole-mode getters return scalar fields directly. Per-surface getters translate the input DML pipe index through `mode_lib->mp.pipe_plane[]` and then index the stored plane arrays. This mapping is critical for ODM, MPC combine, phantom pipes, and other cases where DML pipe indices and logical plane indices are not identical.

## State And Persistence Behavior

All persistent state is held inside the caller-owned `struct display_mode_lib_st`; this chunk does not allocate memory, acquire locks, or program hardware.

`cache_ip_soc_cfg()` refreshes the mode-support state from top-level fields on every public call. It copies `mode_lib->soc`, `mode_lib->ip`, and `mode_lib->policy` into `mode_lib->ms`, then snapshots both the selected state and maximum state. Because these are value copies, subsequent changes to top-level bounding boxes do not affect the current calculation pass unless the public entry point is called again.

`cache_display_cfg()` copies the full display configuration into `mode_lib->ms.cache_display_cfg`. The rest of the mode-support/programming flow reads that cached version, not the caller's pointer. This is important for persistence: getters such as `dml_get_is_phantom_pipe()` inspect cached plane policy after calculations complete, and downstream code can use those values without retaining the original `display_cfg` object.

`fetch_socbb_params()` seeds the active clocks in `mode_lib->ms`. Those fields are calculation state, not hardware state. Later support logic can update DCFCLK, return bandwidth, and related fields while testing policies and state combinations.

`dml_mode_support()` persists evaluation results under `mode_lib->ms`, especially `mode_lib->ms.support`, return bandwidth fields, swath/DET values, and pipe-plane mapping inputs used later by programming and getters. `dml_mode_support_ex()` persists the same state for the lowest passing state and additionally copies `ms.support` to the caller's output structure.

`dml_mode_programming()` persists programming outputs under `mode_lib->mp`. These include watermarks, DLG timing values, calculated clocks, prefetch parameters, DPTE/META row heights, DCC block sizes, MALL sizing, immediate-flip byte counts, and `pipe_plane[]`. Most getters in this chunk are thin reads of that persisted `mp` state.

`dml_core_get_row_heights()` is an exception: it only writes the two caller-provided output pointers. It uses `mode_lib->ip` for constants, but it does not mutate `mode_lib`.

## Dependencies And Integration Points

The chunk depends on the DML2.0 core types defined in `display_mode_core_structs.h`:

- `struct display_mode_lib_st` owns top-level `soc`, `ip`, `policy`, `states`, mode-support state `ms`, mode-programming state `mp`, and scratch storage.
- `struct dml_display_cfg_st` is the display-mode input copied into `ms.cache_display_cfg`.
- `struct soc_states_st` and `struct soc_state_bounding_box_st` define voltage/SOC state arrays and clock limits.
- `struct mode_support_st` holds cached inputs, selected state data, support summary, swath/DET state, return bandwidth, and other support outputs.
- `struct mode_program_st` holds programming outputs consumed by DCHUB/RQ/DLG programming and DC bandwidth state.
- `struct dml_mode_support_ex_params_st` packages the extended mode-support search input and output pointers.

The chunk also depends on local calculation helpers defined earlier in `display_mode_core.c`: `CalculateBytePerPixelAndBlockSizes()`, `CalculateVMAndRowBytes()`, `dml_core_mode_support()`, `dml_core_mode_support_partial()`, and `dml_core_mode_programming()`. The getter declarations mirror `display_mode_core.h`, so adding, renaming, or changing a getter here requires the header to stay synchronized.

Driver integration is visible in nearby DML2 files:

- `dml2_wrapper_fpu.c` maps a DC state into `struct dml_display_cfg_st`, calls the extended support path, maps resources, and then calls `dml_mode_programming()` with the selected lowest state. It also clears `mode_lib->ms` and `mode_lib->mp` around validations, so the persistence described above is per validation/programming pass.
- `dml2_utils.c` uses these getters to copy DML results into DC structures. For example, `dml2_extract_watermark_set()` converts microsecond watermarks from `dml_get_wm_*()` to nanoseconds, `dml2_extract_writeback_wm()` reads writeback watermarks, and `dml2_calculate_rq_and_dlg_params()` uses per-pipe getters for VStartup/VUpdate/VReady, DET buffer size, DPP clock, and MALL surface size.
- `dml_display_rq_dlg_calc.c` consumes the same `mode_lib` state to derive RQ/DLG/TTU register fields, so the row-height and timing getters need to agree with those lower-level register extraction helpers.
- MALL/SubVP code such as `dml2_mall_phantom.c` relies on phantom-pipe and VStartup-related outputs to program phantom pipes and MALL-backed p-state-change behavior.

The functions here are pure model/translation APIs within the AMD display driver. They do not call DRM core APIs, memory-management APIs, or hardware register writes directly; those effects occur after DC wrapper code consumes the DML outputs.

## Risks And Edge Cases

State index validation is assert-only. `dml_get_soc_state_bounding_box()` asserts when `state_idx >= num_states`, and `mode_support_pwr_states()` asserts for reversed or out-of-range search ranges. In production builds where assertions may be less fatal or compiled differently, invalid state inputs could still produce undefined behavior if not caught by callers.

`cache_ip_soc_cfg()` assumes `mode_lib->states.num_states > 0` because it sets `max_state_idx` to `num_states - 1` and fetches the max-state bounding box. An empty state table would underflow the index and trip the later assertion. Correct SoC initialization is therefore a hard prerequisite.

`dml_core_get_row_heights()` intentionally calls `CalculateVMAndRowBytes()` with synthetic values: DCC enabled, GPUVM enabled, one DPP, four GPUVM page-table levels, zero viewport/swath dimensions, and zero DCC meta pitch. This is suitable for row-height discovery but not a general row-byte calculation. A caller expecting exact row bytes, DPTE storage, or frame metadata from this helper would get discarded/dummy data.

The row-height helper selects chroma values when `is_plane1` is true. Formats without chroma still rely on `CalculateBytePerPixelAndBlockSizes()` to produce sane chroma outputs. If callers pass `is_plane1` for a format that does not have a valid plane 1, the returned row heights may not correspond to a real plane.

The getter macros perform no bounds checks. Whole-mode getters assume the relevant support or programming pass has already populated `mode_lib->ms` or `mode_lib->mp`. Per-surface getters assume `surface_idx` is a valid DML pipe index and that `mode_lib->mp.pipe_plane[surface_idx]` contains a valid plane index. A stale or uninitialized `pipe_plane[]` mapping can redirect every per-surface getter to the wrong plane or beyond valid arrays.

`dml_get_is_phantom_pipe()` has the same mapping risk and also depends on `ms.cache_display_cfg` matching the programming state. If programming is run with one display config and getters are read after another support pass, cached policy and `mp.pipe_plane[]` could describe different configurations.

`dml_mode_programming()` returns only `PrefetchAndImmediateFlipSupported`. That is a practical success signal for programming, but it means callers must not infer that every support-policy field is valid unless they either ran full support first or used `call_standalone` to trigger the partial support setup. The standalone path also assumes immediate flip support before the partial pass, which is a deliberate optimistic seed for calculating programming fields.

`mode_support_pwr_states()` initializes `*lowest_state_idx` to `end_state_idx` even when no state passes. Callers must check the returned boolean before using the index. `dml_mode_support_ex()` follows this rule by copying `out_evaluation_info` only on success.

Several getters return values with unit conventions that differ from downstream DC structures. Watermark getters return DML units that `dml2_utils.c` multiplies by 1000 to store nanoseconds. Clock getters often return MHz and are converted to kHz elsewhere. Unit mistakes at call sites can lead to large over/under-programming errors.

## Test Signals

Useful validation signals for this chunk are mostly integration-level because the functions are glue around large DML calculations:

- Mode validation should select the lowest passing SOC state through `dml_mode_support_ex()`. Tests should cover start indices other than zero, unsupported configurations, and configurations that first pass at a higher state.
- A full support-then-programming flow and a standalone programming flow should produce coherent programming outputs for the same valid configuration, especially prefetch/immediate-flip status, watermarks, DCFCLK deep sleep, VStartup/VUpdate/VReady values, and DET sizes.
- DML debug builds with `__DML_RQ_DLG_CALC_DEBUG__` should show row-height helper inputs and outputs that track source format, tiling, rotation, pitch, page size, and luma/chroma DPTE buffer request limits.
- Per-pipe DC programming should receive the expected plane values when ODM, MPC combine, SubVP phantom pipes, or multiple pipes per surface are active. This specifically exercises the `mp.pipe_plane[]` mapping used by the getter macros.
- Watermark extraction in `dml2_extract_watermark_set()` should show expected unit conversion from DML microsecond-style outputs to DC nanoseconds, including urgent, stutter, DRAM/FCLK p-state, USR retraining, and Z8 watermarks.
- Writeback watermark extraction should remain stable for configurations with and without DWB enabled, using `dml_get_wm_writeback_urgent()` and `dml_get_wm_writeback_dram_clock_change()`.
- Phantom-pipe tests should confirm `dml_get_is_phantom_pipe()` and MALL-related getters agree with `UseMALLForPStateChange` policy and that phantom pipes get zero DET/unbounded-request treatment in downstream code.
- Negative or boundary tests should exercise invalid state ranges under assertion-enabled builds, zero or one SOC state, maximum pipe/surface indices, and unsupported modes where `dml_mode_support_ex()` returns false without refreshing `out_evaluation_info`.

## Cross-Chunk Notes

The preceding chunks of this same file contain the formula-heavy support and programming engines that populate the state exposed here: swath/DET setup, VM/PTE/META row-byte calculation, prefetch scheduling, urgent burst factors, watermarks, DRAM/FCLK clock-change support, stutter efficiency, and DLG/RQ values. The following chunks continue the getter surface beyond line 10362. The final per-file report should treat this chunk as the API/export boundary for DML2.0 core calculations rather than as a standalone calculation engine.
