# Research: subset-b-001404

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_mode_vba_20v2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_mode_vba_20v2.c

## Purpose

`display_mode_vba_20v2.c` is the DCN 2.0v2 Display Mode Library VBA implementation for AMD Display Core. It consumes a populated `struct display_mode_lib` and mutates `mode_lib->vba` with mode-validation results, selected voltage state, pipe topology decisions, display clock requirements, prefetch schedules, watermarks, stutter/p-state support, DSC link requirements, immediate-flip support, DET/swath sizing, and related per-plane timing quantities.

The file is intentionally a hardware formula translation. Its own comment says it is "HW gospel" and should usually remain as-is. Most logic is numeric modeling over arrays indexed by active plane, voltage state, and MPC-combine option; it does not perform register programming directly.

## Important APIs, Types, And Functions

- `dml20v2_recalculate(mode_lib)`: public recalculation entry. It runs generic mode support/system configuration, fabric/DRAM bandwidth derivation, progressive-to-interlace pixel-clock adjustment, DCN20v2 pipe configuration, and final clock/prefetch/watermark/performance calculation.
- `dml20v2_ModeSupportAndSystemConfigurationFull(mode_lib)`: public full validation and selection pass. It tests source format, scale ratio, bandwidth, clocks, DIO/DSC, writeback, cursor, pitch, prefetch, PTE buffer, pipe/OTG count, and then selects `VoltageLevel`, `maxMpcComb`, `DPPPerPlane`, clocks, ODM, DSC, and output bpp.
- `dml20v2_DisplayPipeConfiguration(mode_lib)`: derives swath heights and DET luma/chroma buffer split from pixel format, tiling, scan direction, ODM combine, DPP split, viewport dimensions, and the configured DET buffer size.
- `dml20v2_DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation(mode_lib)`: final selected-state calculation for DISPCLK/DPPCLK/DSCCLK, return bandwidth, urgent/stutter/DRAM-clock watermarks, DCFCLK deep sleep, VM/PTE/DCC rows, prefetch, immediate flip, DRAM-clock-change support, and XFC values.
- Helper formulas include `adjust_ReturnBW`, `dscceComputeDelay`, `dscComputeDelay`, `CalculateDelayAfterScaler`, `CalculatePrefetchSchedule`, `RoundToDFSGranularityUp`, `RoundToDFSGranularityDown`, `CalculatePrefetchSourceLines`, `CalculateVMAndRowBytes`, `CalculateTWait`, `CalculateRemoteSurfaceFlipDelay`, `CalculateWriteBackDelay`, `CalculateActiveRowBandwidth`, `CalculateFlipSchedule`, and `TruncToValidBPP`.
- Key data is almost entirely in `struct vba_vars_st`, reached as `mode_lib->vba` or `locals`, plus SoC/IP limits under `mode_lib->vba.soc`, `mode_lib->soc`, and `mode_lib->ip`.

## Control Flow

`dml20v2_recalculate` is the small runtime entry: it invokes a common `ModeSupportAndSystemConfiguration`, computes `FabricAndDRAMBandwidth`, applies interlace pixel-clock adjustments, derives pipe swath/DET configuration, then computes final clocks, prefetch parameters, watermarks, and performance outputs. This assumes `mode_lib->vba` already contains input mode state and selected-state fields from the broader DML pipeline.

`dml20v2_ModeSupportAndSystemConfigurationFull` is the exhaustive support pass. It first validates scaler ratios/taps, source pixel format/tiling/scan combinations, writeback latency/mode/scaler limits, and basic source read/write bandwidth. It then loops over all SoC voltage states and two MPC-combine choices to derive return bandwidth, ROB support, required DISPCLK/DPPCLK, ODM combine enablement, number of DPPs per plane, viewport support, pipe and OTG support, DIO link bpp, DSC/FEC requirements, DSC delay, urgent-latency support, prefetch support, immediate-flip support, vertical-active bandwidth support, PTE buffer size support, cursor support, and pitch alignment. Each state/combine pair gets a validation status. The first valid state at or above `VoltageOverrideLevel` is selected, with MPC combine enabled only if the j=1 state is needed or policy says to use it when possible.

`dml20v2_DISPCLKDPPCLKDCFCLKDeepSleepPrefetchParametersWatermarksAndPerformanceCalculation` works on the chosen mode. It calculates writeback DISPCLK, per-plane scaler throughput, single-DPP DPPCLK, selected DISPCLK with and without ramping, rounded DFS clock values, global DPPCLK, DCC-aware return bandwidth, read bandwidth, active DPP totals, urgent latency and watermarks, writeback watermarks, stutter efficiency, DCFCLK deep sleep, urgent latency tolerance, DSCCLK and DSC delay, VM/PTE/meta bytes, prefetch source lines, active row bandwidth, writeback delay, maximum vstartup, cursor bandwidth, prefetch schedules, immediate flip schedules, TTU/vblank policy, DRAM-clock-change support, and XFC timing/fill margins. It increments `VStartupLines` until prefetch and optional immediate flip pass or the maximum startup limit is exceeded.

The prefetch path is a layered calculation. `CalculateVMAndRowBytes` estimates meta/PTE frame bytes and row bytes from DCC, GPUVM, tiling, macro tile size, scan direction, viewport, pitch, page size, and hardware buffer limits. `CalculatePrefetchSourceLines` computes source lines and initial prefill. `CalculateDelayAfterScaler` models pipe delay and updates the last-pixel watermark. `CalculatePrefetchSchedule` computes VUPDATE/VREADY offsets, time allocated to metadata/PTE/row/pixel prefetch, prefetch ratios, required pixel bandwidth, and error flags. `CalculateFlipSchedule` then reserves bandwidth for immediate flip metadata and row fetches.

## State And Persistence Behavior

The file has no on-disk persistence and does not write hardware registers. Its persistent effects are mutations to the in-memory `mode_lib->vba` object that later DML/DC layers read. Important outputs include:

- Selected mode fields: `VoltageLevel`, `maxMpcComb`, `DPPPerPlane[]`, `DISPCLK`, `DPPCLK[]`, `DCFCLK`, `DRAMSpeed`, `FabricClock`, `SOCCLK`, `ReturnBW`, `ODMCombineEnabled[]`, `DSCEnabled[]`, and `OutputBpp[]`.
- Validation state: `ModeSupport[][]`, `ValidationStatus[]`, `ScaleRatioAndTapsSupport`, `SourceFormatPixelAndScanSupport`, `DIOSupport[]`, `PrefetchSupported[][]`, `ImmediateFlipSupportedForState[][]`, `PTEBufferSizeNotExceeded[][]`, and many failure-specific booleans.
- Timing and watermark outputs: urgent/stutter/writeback/DRAM-clock watermarks, `MinTTUVBlank[]`, `AllowDRAMClockChangeDuringVBlank[]`, `AllowDRAMSelfRefreshDuringVBlank[]`, `DRAMClockChangeSupport[][]`, `VStartup[]`, `VUpdateOffsetPix[]`, `VUpdateWidthPix[]`, and `VReadyOffsetPix[]`.
- Per-plane memory model outputs: swath width/height, DET split, bytes per pixel, read bandwidth, meta row bytes, DPTE row bytes, row bandwidths, prefetch bandwidth, vratio prefetch, VM/row request line counts, immediate flip line counts, XFC delays, and DSC delay.

Because nearly every field is reused by later helpers and other files through generated accessors, stale values and partial recalculations can be dangerous. The implementation often writes scratch fields such as `ProjectedDCFCLKDeepSleep[0][0]`, `PrefetchLinesY[0][0][k]`, and `PDEAndMetaPTEBytesPerFrame[0][0][k]` while iterating state/combine candidates.

## Dependencies And Integration Points

The file includes `display_mode_lib.h`, `display_mode_vba_20v2.h`, and `dml_inline_defs.h`. It depends on shared DML math helpers (`dml_min`, `dml_max`, `dml_floor`, `dml_ceil`, `dml_round`, `dml_pow`, `dml_log2`, `dml_max3`, `dml_max5`), debug helpers (`DTRACE`, `dml_print`, `ASSERT`), and common DML routines such as `ModeSupportAndSystemConfiguration`, `PixelClockAdjustmentForProgressiveToInterlaceUnit`, `CalculateWriteBackDISPCLK`, `Calculate256BBlockSizes`, and `CalculateMinAndMaxPrefetchMode`.

It integrates with the rest of AMD DC through the Display Mode Library API. Other DML files and generation-specific DC code use the selected clocks, watermarks, swath/DET geometry, DPP/ODM/DSC decisions, prefetch results, and validation status to decide whether a mode can be committed and how hubbub, hubp, dlg/ttu, dsc, dpp, dccg, and timing generator state should be programmed.

`display_rq_dlg_calc_20.c` consumes many of the final timing quantities through accessor functions such as `get_wm_urgent`, `get_clk_dcf_deepsleep`, `get_dst_y_prefetch`, `get_dst_y_per_vm_vblank`, `get_vratio_prefetch_l`, `get_dsc_delay`, and related DML accessors.

## Risks And Edge Cases

- This code relies heavily on nonzero divisors: clocks, bandwidths, ratios, swath widths, DET sizes, htotal, page sizes, pitch, DPP counts, DSC slices, and row heights. Some assertions exist, but many divisions assume validated inputs.
- Many arrays are indexed by `NumberOfActivePlanes`, `soc.num_states`, and `VoltageLevel`. If `VoltageLevel` remains `soc.num_states + 1` because no mode is valid, later indexing can become unsafe unless callers check validation before using selected outputs.
- Several helpers use `unsigned int` return types while manipulating fractional bpp values, especially `TruncToValidBPP`; this mirrors existing code but can silently truncate fractional DSC bpp semantics.
- `CalculateFlipSchedule` divides by `TotImmediateFlipBytes` when GPUVM/DCC immediate flip bytes are present. It depends on the caller's source-format filtering to avoid zero totals.
- `CalculateDelayAfterScaler` takes a `ReturnBW` argument but uses `mode_lib->vba.ReturnBW` internally, which makes it sensitive to the global selected state rather than the argument in candidate-state contexts.
- The state/combine prefetch pass reuses several `[0][0]` scratch arrays while iterating all `i,j` candidates. That is part of the inherited formula structure, but it is easy to break if refactored.
- DCC with 4:2:0 is rejected in support checks, but chroma/DCC-related paths still contain fallbacks and TODOs. Test coverage should include unsupported combinations to ensure they fail validation, not register programming later.
- ODM/DSC/image-width limits are hard-coded (`DCN20_MAX_DSC_IMAGE_WIDTH`, `DCN20_MAX_420_IMAGE_WIDTH`) and must match the DCN20v2 hardware guide.
- Numerous formulas use rounded fixed granularity and magic thresholds (`VRatioPrefetch <= 4`, VM lines `< 8`, row lines `< 16`, initial `VStartupLines = 13`). Regressions can appear as borderline validation changes rather than compile failures.

## Test Signals

- Build coverage for AMDGPU display should catch prototype/type drift with `display_mode_vba_20v2.h`, missing helper declarations, enum changes, and structure field renames.
- DML validation tests should cover valid and invalid combinations for scale ratios/taps, source tiling and scan, DCC, GPUVM page size, pitch alignment, cursor sizes, writeback modes, DSC input bpc, DP/HDMI/eDP link bpp, FEC, DSC unit count, DPP count, OTG count, and ODM combine.
- Golden-output tests are valuable for representative DCN20v2 modes: single RGB plane, YUV420 plane, DCC enabled, GPUVM enabled, writeback enabled, multiple planes sharing timing, MPC combine, ODM combine, DSC on DP/eDP, HDMI no-DSC, interlace/progressive-to-interlace, and XFC remote flip.
- Runtime signals include `ValidationStatus[]`, `ModeSupport[][]`, `PrefetchModeSupported`, `ImmediateFlipSupported`, `DRAMClockChangeSupport`, `DML_FAIL_*` values, `DTRACE` clock/watermark output, `dml_print` prefetch failures, and assertions on DFS VCO speed and register/timing bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_mode_vba_20v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_mode_vba_20v2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_mode_vba_20v2.h

## Purpose

`display_mode_vba_20v2.h` is the small public interface for the DCN 2.0v2 VBA implementation. It declares the two generation-specific entry points implemented in `display_mode_vba_20v2.c` so other DML/DC files can run the DCN20v2 recalculation and full mode-support/system-configuration pass.

The header contains only license text, an include guard, and function declarations. It intentionally does not expose the many static helper formulas used by the implementation file.

## Important APIs, Types, And Functions

- `dml20v2_recalculate(struct display_mode_lib *mode_lib)`: recomputes selected-mode clocks, pipe configuration, prefetch, watermarks, and performance values after the common mode support and setup steps.
- `dml20v2_ModeSupportAndSystemConfigurationFull(struct display_mode_lib *mode_lib)`: runs the full DCN20v2 validation/selection pass and updates `mode_lib->vba` with support flags, selected voltage state, DPP/ODM/DSC decisions, clocks, and output bpp.
- `struct display_mode_lib`: used as an incomplete type in the prototypes. The defining declaration is supplied by including `display_mode_lib.h` before or alongside this header in translation units that call the functions.

## Control Flow

The header itself has no executable control flow. Its integration role is compile-time linkage: callers include it, pass a configured `struct display_mode_lib *`, and rely on the `.c` file to mutate `mode_lib->vba`. The include guard `_DCN20V2_DISPLAY_MODE_VBA_H_` prevents duplicate declarations during nested includes.

The two declared functions represent different stages. `dml20v2_ModeSupportAndSystemConfigurationFull` is the broader validation and configuration selector. `dml20v2_recalculate` is the recalculation path used after mode inputs and selected configuration are established.

## State And Persistence Behavior

The header stores no state and has no persistence behavior. All stateful behavior belongs to the implementation functions and the caller-owned `struct display_mode_lib`. Since the header only forward-references `struct display_mode_lib` in parameter lists, it does not force a layout dependency by itself.

## Dependencies And Integration Points

The file depends on the C compiler seeing a compatible declaration for `struct display_mode_lib` in any translation unit using the prototypes. The implementation includes this header from `display_mode_vba_20v2.c`; generation dispatch code elsewhere in the Display Mode Library can include it to call the DCN20v2 formulas.

The naming convention ties it to `drivers/gpu/drm/amd/display/dc/dml/dcn20/` and to sibling DCN20 DML files such as request/deadline calculation and display-mode accessors. It is not a standalone API for external kernel subsystems.

## Risks And Edge Cases

- If a caller includes this header without a prior visible declaration of `struct display_mode_lib`, C permits an incomplete struct type in the prototype, but mismatched declarations elsewhere would be a compile-time or ABI risk.
- The header does not include `display_mode_lib.h`, so include-order assumptions must stay consistent across callers.
- Any signature change in the `.c` file must be reflected here or callers will fail to compile or link.
- The broad mutating behavior of both functions is not documented in the header, so callers must know from DML conventions that `mode_lib->vba` is updated in place.

## Test Signals

- Kernel build and sparse/compiler checks catch missing prototypes, signature drift, duplicate include issues, and missing `struct display_mode_lib` visibility.
- Link tests catch cases where generation dispatch references either declared function but the implementation object is not compiled.
- Functional testing is indirect: any DML mode-validation test that calls the declared functions exercises the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_mode_vba_20v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20.c

## Purpose

`display_rq_dlg_calc_20.c` converts DCN 2.0 display-mode results and per-pipe source/destination parameters into request-queue, deadline, and TTU register structures. It bridges the high-level DML timing/bandwidth model and the register fields used by HUBP/DLG/TTU programming.

The file computes requestor geometry that is mostly register-definition agnostic, then extracts encoded register values. It separately computes DLG/TTU timing fields from pipe timing, scaling, prefetch, watermarks, RQ metadata/PTE row information, cursor state, cstate and pstate policy.

## Important APIs, Types, And Functions

- `dml20_rq_dlg_get_rq_reg(mode_lib, rq_regs, pipe_param)`: public RQ entry. It zeros output registers, calculates `display_rq_params_st`, encodes RQ sizing/swath/DET fields, and prints the result.
- `dml20_rq_dlg_get_dlg_reg(mode_lib, dlg_regs, ttu_regs, e2e_pipe_param, num_pipes, pipe_idx, cstate_en, pstate_en, vm_en, ignore_viewport_pos, immediate_flip_support)`: public DLG/TTU entry. It gathers system watermark values through DML accessors, computes local RQ params, and fills `display_dlg_regs_st` and `display_ttu_regs_st`.
- `dml20_rq_dlg_get_rq_params`: derives luma/chroma RQ parameters for a pipe source.
- `dml20_rq_dlg_get_dlg_params`: main deadline/TTU calculation and register assignment function.
- `get_bytes_per_element`, `is_dual_plane`, `get_refcyc_per_delivery`, and `get_blk_size_bytes`: local format, request timing, and tile-size helpers.
- `extract_rq_sizing_regs` and `extract_rq_regs`: convert byte-sized request groups/chunks and swath geometry into register encodings.
- `handle_det_buf_split`: decides luma/chroma DET buffer allocation and request size behavior.
- `get_meta_and_pte_attr` and `get_surf_rq_param`: compute swath width, full swath bytes, meta request rows/chunks, meta PTE frame bytes, DPTE request rows/groups, and related sizing values.
- `calculate_ttu_cursor`: computes per-request TTU delivery timing for up to two cursors.

## Control Flow

The RQ path starts in `dml20_rq_dlg_get_rq_reg`. It clears `display_rq_regs_st`, calls `dml20_rq_dlg_get_rq_params` on `pipe_param->src`, then calls `extract_rq_regs`. The parameter pass identifies YUV420/10bpc formats, computes luma surface parameters, optionally computes chroma parameters for dual-plane formats, and calls `handle_det_buf_split`. Surface parameter calculation sets fixed chunk defaults, delegates most geometry to `get_meta_and_pte_attr`, and stores the results in luma/chroma `sizing`, `dlg`, and `misc` structs. Register extraction encodes chunk, min chunk, meta chunk, dpte group, mpte group, PTE row height, swath height, expansion modes, and `plane1_base_address` for the chroma DET split.

`get_meta_and_pte_attr` is the core RQ geometry routine. It determines bytes per element and 256-byte block dimensions, handles linear vs tiled and horizontal vs vertical scan, calculates swath width upper bounds and request counts, computes full swath bytes, derives meta row dimensions and chunk counts, estimates meta surface and meta PTE bytes per frame, determines virtual memory page shape, chooses DPTE request shape, derives DPTE row height/width/request count, sets DPTE bytes per row, chooses reduced DPTE grouping for a vertical tiled special case, and stores groups per row.

The DLG/TTU path starts in `dml20_rq_dlg_get_dlg_reg`. It gathers `display_dlg_sys_params_st` from accessor functions such as urgent watermark, deep sleep DCFCLK, extra latency, memory-trip watermark, dram-clock-change watermark, stutter watermark, and immediate-flip totals. It then recalculates RQ params for the selected pipe and calls `dml20_rq_dlg_get_dlg_params`.

`dml20_rq_dlg_get_dlg_params` reads the selected pipe's source, destination, output, clocks, scale ratio, and taps. It computes reference-to-pixel frequency ratios, htotal/vblank fields, min TTU vblank, vupdate/vready behavior, pipeline delay after scaler/DSC, line wait based on urgent/cstate/pstate, prefetch line allocation from DML accessors, luma/chroma active delivery timing, TTU request delivery for luma/chroma and cursors, and then writes fixed-point register fields. It asserts many register-width assumptions and clamps some nominal delivery fields to maximum register values.

## State And Persistence Behavior

This file does not persist state and does not directly program hardware. It mutates only caller-provided output structures:

- `display_rq_regs_st`: RQ chunk sizes, min chunk sizes, meta chunk sizes, DPTE/MPTE group sizes, PTE row height, swath height, expansion modes, and chroma plane base address.
- `display_dlg_regs_st`: reference frequency ratios, htotal/vblank timing, after-scaler offsets, prefetch line counts, VM/row request timing, vratio prefetch fields, PTE/meta group delivery fields, nominal row timing, line delivery timing, cursor DLG defaults, and QoS-related DLG fields.
- `display_ttu_regs_st`: per-request delivery timing for luma/chroma/cursors, QoS watermarks/levels, ramp-disable flags, and min TTU vblank.

Scratch state is local (`display_rq_params_st rq_param`, `display_dlg_sys_params_st dlg_sys_param`). The computations depend on stable `mode_lib` accessor outputs and the caller's `display_e2e_pipe_params_st` array.

## Dependencies And Integration Points

The file includes `display_mode_lib.h`, `display_mode_vba.h`, `display_rq_dlg_calc_20.h`, and `dml_inline_defs.h`. It depends on DML math/debug helpers (`dml_log2`, `dml_floor`, `dml_ceil`, `dml_round_to_multiple`, `dml_min`, `dml_max`, `dml_pow`, `dml_print`, `ASSERT`) and common DML geometry functions such as `Calculate256BBlockSizes`.

It also depends on accessor functions and print helpers declared elsewhere in DML: `get_wm_urgent`, `get_clk_dcf_deepsleep`, `get_urgent_extra_latency`, `get_wm_memory_trip`, `get_wm_dram_clock_change`, `get_wm_stutter_enter_exit`, `get_total_immediate_flip_bw`, `get_total_immediate_flip_bytes`, `get_tcalc`, `get_min_ttu_vblank`, `get_dsc_delay`, `get_dst_x_after_scaler`, `get_dst_y_after_scaler`, `get_dst_y_prefetch`, `get_dst_y_per_vm_vblank`, `get_dst_y_per_row_vblank`, `get_dst_y_per_vm_flip`, `get_dst_y_per_row_flip`, `get_vratio_prefetch_l`, `get_vratio_prefetch_c`, and the `print__*` diagnostics.

Integration-wise, this is the DCN20 register-preparation side of DML. Higher-level AMD Display Core code builds `display_pipe_params_st` or `display_e2e_pipe_params_st`, calls these functions, and later uses the resulting register structures to program HUBP/DLG/TTU state through hardware abstraction layers.

## Risks And Edge Cases

- The code assumes many values are nonzero and power-of-two compatible: chunk bytes, meta chunk bytes, group bytes, swath heights, DPTE row heights, request counts, pitches, htotal, pixel/ref clocks, dppclk, dispclk, and cursor scaling ratios.
- Register-width assertions catch many overflow cases in debug builds (`refcyc_per_*`, `dst_y_*`, min TTU vblank), but release builds may continue with truncated values unless upstream validation prevents the mode.
- `extract_rq_regs` encodes `pte_row_height_linear` as `floor(log2(dpte_row_height)) - 3`; heights below 8 would underflow unsigned fields.
- `handle_det_buf_split` assumes the incoming configuration fits in DET. If it does not, it chooses 128-byte luma requests or DET splits but does not independently fail validation.
- `get_meta_and_pte_attr` computes meta surface bytes using viewport height even for vertical scan, matching the inherited formulas but making scan/pitch correctness sensitive to the hardware guide.
- The DLG path accepts `vm_en`, `ignore_viewport_pos`, and `immediate_flip_support` parameters but casts them unused. It relies on mode_lib/e2e accessor state rather than these booleans.
- There are several explicit TODOs and comments about inherited behavior: full recout width in hsplit, min_vblank mismatch, DCC for 4:2:0, chroma nominal meta timing, and magic thresholds for tiny `htotal`.
- Cursor support asserts `cur_src_width <= 256`; invalid cursor sizes can stop debug builds.
- Integer casts of fixed-point values can round down. Boundary cases near register limits need golden tests.

## Test Signals

- Build coverage catches structure/member drift with `display_rq_dlg_calc_20.h`, DML accessor declarations, and enum changes for source formats, tiling, macro tile size, scan direction, and cursor bpp.
- Unit or golden DML tests should compare RQ/DLG/TTU register outputs for linear RGB, tiled RGB, YUV420 8bpc, YUV420 10bpc, horizontal and vertical scan, DCC on/off, GPUVM page sizes, 4KB/64KB/256KB macro tiles, one and two cursors, ODM combine, hsplit/MPC combine, DSC enabled, interlaced timing, cstate and pstate enabled/disabled, and immediate flip metadata.
- Runtime diagnostics include `DML_DLG` prints of RQ sizing/regs, system params, delivery timing, prefetch lines, vratio prefetch, cursor timing, and warnings around `full_recout_width` or `vstartup_start >= min_vblank`.
- Assertions around reference cycles, prefetch relationships, register widths, cursor width, and line allocations are important failure signals during hardware bring-up or simulator validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn20/display_rq_dlg_calc_20.c -->
