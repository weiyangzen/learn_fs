# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 49101-51572

## Scope

This chunk is a generated AMD DCN 3.1.4 shift/mask header segment. It contains preprocessor constants only: each register field is represented by a `...__SHIFT` macro and a matching `..._MASK` macro. The slice has 2,472 source lines and about 2,134 `#define` lines, with 16 generated address-block markers.

The chunk starts in the middle of the DSC0 DSCC PPS field definitions at `DSCC0_DSCC_PPS_CONFIG13`, covers the rest of DSC0 rate/PPS/status masks, complete DSC1, DSC2, and DSC3 mask families, DC perfmon blocks 17 through 21, and the first part of DWB0 writeback/color-processing masks. It ends in the middle of the DWB output-gamma RAMA region table: `DWB_OGAM_RAMA_REGION_26_27` begins immediately after the requested line range, so the DWB OGAM RAMA and RAMB field families continue in the next chunk.

## Purpose

The purpose of this header segment is to provide bitfield positions and masks for DCN 3.1.4 display-compression and display-writeback hardware registers. Driver code combines these constants with companion register-offset macros from `dcn_3_1_4_offset.h` and with AMDGPU register helper macros to perform read-modify-write operations without hard-coding numeric bit layouts.

This is data-like source rather than executable logic. Its correctness is still critical: an incorrect shift or mask can silently program the wrong hardware bits while all C code still compiles.

## Register Families And Important Macros

The DSC/DSCC portion defines masks for Display Stream Compression instances:

- `DSC_TOP1_DSC_TOP_CONTROL`, `DSC_TOP2_DSC_TOP_CONTROL`, and `DSC_TOP3_DSC_TOP_CONTROL` cover per-instance DSC clock enable and clock-gating control. Each instance also has `DSC_DEBUG_CONTROL` masks for debug enable and test-clock mux selection.
- `DSCCIF1_DSCCIF_CONFIG*`, `DSCCIF2_DSCCIF_CONFIG*`, and `DSCCIF3_DSCCIF_CONFIG*` describe the DSC compressor input interface: underflow recovery/status/interrupt enable, input pixel format, bits per component, YCbCr 4:2:0/4:2:2 mode, and slice-width-minus-one fields.
- `DSCC1_DSCC_CONFIG*`, `DSCC2_DSCC_CONFIG*`, and `DSCC3_DSCC_CONFIG*` cover compressor configuration such as ICH reset timing, slices per line, alternate ICH encoding, vertical slice count, and the DSCC rate-control buffer model size.
- `DSCC*_DSCC_STATUS` provides the double-buffer update-pending bit.
- `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` provides overflow/underflow status and interrupt-enable masks for four rate buffers and four rate-control buffer models.
- `DSCC*_DSCC_PPS_CONFIG0` through `PPS_CONFIG22` map the DSC picture parameter set into hardware fields: DSC version, PPS identifier, line buffer depth, bits per component/pixel, VBR/simple/native 4:2:2/4:2:0 modes, chunk size, picture and slice dimensions, initial transmit/decode delays, scale increment/decrement intervals, BPG offsets, initial/final offsets, flatness QP limits, RC model size, RC quantization limits, target offsets, RC buffer thresholds 0-13, and range table entries 0-14.
- `DSCC*_DSCC_MEM_POWER_CONTROL` defines low-power state, force/disable, observed power state, and native 4:2:2 memory power-control fields.
- `DSCC*_DSCC_R_Y/G_CB/B_CR_SQUARED_ERROR_*` and `DSCC*_DSCC_MAX_ABS_ERROR*` expose error/statistics readback fields for DSC quality or validation paths.
- `DSCC*_DSCC_RATE_BUFFER*_MAX_FULLNESS_LEVEL` and `DSCC*_DSCC_RATE_CONTROL_BUFFER*_MAX_FULLNESS_LEVEL` define fullness counters or maximum fullness observations for four compressor lanes/models.
- `DSCC*_DSCC_TEST_DEBUG_BUS_ROTATE` defines rotate selectors for four DSC debug buses.

The perfmon blocks are structurally repeated for DSC instances and DWB:

- `DC_PERFMON17_*`, `DC_PERFMON18_*`, `DC_PERFMON19_*`, and `DC_PERFMON20_*` sit after DSC0 through DSC3 respectively.
- `DC_PERFMON21_*` sits after the DWB0 top block.
- Each perfmon block defines counter-control fields, counter state, clock-enable and counter-enable control, event-selection masks, trigger/enable/status fields, current-value interrupt selection, and low/high counter readback masks.

The DWB0 top and color-processing portion defines masks for display writeback:

- `DWB_ENABLE_CLK_CTRL` and `DWB_MEM_PWR_CTRL` cover DWB top enable, clock gating, test-clock selection, and OGAM LUT memory power state.
- `FC_MODE_CTRL`, `FC_FLOW_CTRL`, `FC_WINDOW_START`, `FC_WINDOW_SIZE`, and `FC_SOURCE_SIZE` describe frame-capture enable/rate, crop window, stereo-eye selection, new-content status, first-pixel delay, and source/window dimensions.
- `DWB_UPDATE_CTRL` exposes update lock and pending state.
- `DWB_CRC_CTRL`, `DWB_CRC_MASK_R_G`, `DWB_CRC_MASK_B_A`, `DWB_CRC_VAL_R_G`, and `DWB_CRC_VAL_B_A` provide writeback CRC control, channel masks, and channel signature readbacks.
- `DWB_OUT_CTRL` defines output format, denorm, max, and min fields.
- `DWB_MMHUBBUB_BACKPRESSURE_CNT_*`, `DWB_HOST_READ_CONTROL`, `DWB_OVERFLOW_STATUS`, `DWB_OVERFLOW_COUNTER`, `DWB_SOFT_RESET`, and `DWB_DEBUG_CTRL` cover memory-hub backpressure, host-read throttling, overflow status/clearing/interrupt enable, overflow counters, soft reset, and debug selection.
- `DWB_HDR_MULT_COEF`, `DWB_GAMUT_REMAP_MODE`, `DWB_GAMUT_REMAP_COEF_FORMAT`, and `DWB_GAMUT_REMAPA/B_*` define HDR multiplier and A/B gamut-remap matrix fields.
- `DWB_OGAM_CONTROL`, `DWB_OGAM_LUT_INDEX`, `DWB_OGAM_LUT_DATA`, `DWB_OGAM_LUT_CONTROL`, and `DWB_OGAM_RAMA_*` define output-gamma LUT mode/select/current state, LUT index/data access, channel write/read controls, RAMA start/end/base/slope/offset fields, and RAMA region-pair LUT-offset/segment-count fields through region pair 24-25 in this chunk.

## Control Flow And Runtime Behavior

There is no direct C control flow in this header. Runtime behavior is through generated register tables and register access helpers. DCN314 resource code includes `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`, then builds per-block tables whose fields are populated from these macros.

For DSC, `dcn314_resource.c` constructs `struct dcn20_dsc` instances with `dsc2_construct(...)`, passing `dsc_regs[inst]`, `dsc_shift`, and `dsc_mask`. The field list comes from `display/dc/dsc/dcn20/dcn20_dsc.h`, where `DSC_REG_LIST_SH_MASK_DCN20(__SHIFT)` and `DSC_REG_LIST_SH_MASK_DCN20(_MASK)` select fields such as `DSCC_PPS_CONFIG*`, rate-buffer overflow/underflow bits, error counters, memory power state, and debug-bus rotation.

For DWB, `dcn314_resource.c` includes `dcn30/dcn30_dwb.h`, builds `dwbc30_shift` and `dwbc30_mask` via `DWBC_COMMON_MASK_SH_LIST_DCN30(__SHIFT)` and `DWBC_COMMON_MASK_SH_LIST_DCN30(_MASK)`, then constructs `struct dcn30_dwbc` with `dcn30_dwbc_construct(...)`. DWB color-management code in `dcn30_dwb_cm.c` consumes these shifts/masks when programming OGAM/gamut-remap state and when mapping common gamma helper fields onto DWB-specific register fields.

The hardware flows represented by this chunk are:

- DSC enable/configuration, PPS programming, rate-control configuration, double-buffer update observation, error/statistics readback, rate-buffer fullness monitoring, underflow/overflow interrupt handling, and memory power control.
- Per-block perf counter selection, enablement, trigger/status handling, and counter readback for DSC and DWB diagnostics.
- DWB frame-capture setup, crop/source geometry, update locking, CRC generation, output format and denorm range programming, backpressure/overflow observation, soft reset, HDR/gamut remap, and output-gamma LUT/RAMA curve programming.

## State And Persistence

The macros themselves hold no state and allocate no storage. They describe persistent hardware bitfields. Values written through consumers persist in the DCN display hardware until a later register write, hardware reset, power-gating transition, suspend/resume restore, or full display reprogramming changes them.

Several represented fields have stateful behavior:

- DSC PPS and DSCC configuration fields are part of the active compression stream setup. Incorrect writes can affect the compressed stream immediately or at the next double-buffered update point.
- `DSCC_DOUBLE_BUFFER_REG_UPDATE_PENDING` is read as hardware state and is used to observe when pending DSC programming has taken effect.
- DSC interrupt/status fields can be latched by hardware for overflow and underflow conditions; clear/enable sequencing is handled by consumers outside this header.
- DSC rate-buffer and error/max-error fields are readback/statistical state maintained by hardware.
- DSC and DWB memory-power fields include requested and observed power states, so they interact with display power sequencing.
- DWB `DWB_UPDATE_LOCK` and `DWB_UPDATE_PENDING` coordinate when writeback register changes become visible to the hardware pipeline.
- DWB overflow, backpressure, CRC, and perfmon fields expose live or latched diagnostic state.
- DWB OGAM programming is index/data and bank/region based; consumers must select the intended mode, host path, channel, and region before writing LUT or piecewise-linear curve parameters.

## Dependencies And Integration Points

This chunk depends on the rest of the generated DCN 3.1.4 register set:

- `dcn_3_1_4_offset.h` supplies the companion MMIO register offsets used with these field masks.
- `display/dc/dsc/dcn20/dcn20_dsc.h` defines the common DSC register, shift, and mask table layout consumed by DCN314 DSC construction.
- `display/dc/resource/dcn314/dcn314_resource.c` includes this generated header and binds DCN314 resources to `dsc_shift`, `dsc_mask`, `dwbc30_shift`, and `dwbc30_mask`.
- `display/dc/dwb/dcn30/dcn30_dwb.h` defines DWB register/field table macros and `struct dcn30_dwbc_shift` / `struct dcn30_dwbc_mask`.
- `display/dc/dwb/dcn30/dcn30_dwb_cm.c` uses the DWB OGAM and gamut-remap masks to program writeback color management.
- Higher-level DSC paths use DRM DSC types from `drm/display/drm_dsc.h` and AMD DSCC types from `display/dc/dsc/dscc_types.h`; those semantic values are packed into hardware fields described by this header.

The generated macro names form a compile-time API. Renaming or deleting a field macro breaks the table initializers. Changing a numeric shift or mask can compile cleanly but corrupt runtime register programming.

## Risks And Edge Cases

- Generated-header drift is the main risk. A single wrong mask width or shift can mispack DSC PPS data, interrupt enables, memory power controls, DWB crop/output fields, or OGAM/gamut-remap coefficients.
- The chunk begins and ends on partial logical blocks. DSC0 `PPS_CONFIG13` starts before line 49101, and DWB OGAM RAMA continues after line 51572. The merge lane must not treat either family as complete based only on this chunk.
- Instance parity matters for DSC1, DSC2, and DSC3. The masks are structurally repeated; an instance-specific generation error can affect only one compressor and may appear only on displays using that DSC engine.
- Some fields are status or latch bits, not plain configuration bits. Consumers need the correct clear/read/enable order for DSCC overflow/underflow, DWB overflow, CRC, and perfmon state.
- DSC PPS fields have tight bit-width expectations from the DSC specification and DRM DSC structures. Truncation or signedness mistakes in caller code can be hidden by a valid-looking mask.
- DWB OGAM LUT and RAMA fields are only part of the complete curve programming surface in this chunk. Region pairs 26-27 through 32-33 and RAMB fields continue later, so documentation and validation must join adjacent chunks.
- Power-control fields combine force, disable, requested low-power state, and observed state. Programming them outside the intended DCN314 power sequencing can leave DSC or DWB memory unavailable during active use.

## Test Signals

Useful validation signals are mostly build-time, generation-time, and hardware/display regression signals:

- Build AMDGPU DCN314 display code to catch missing or renamed `DSCC*`, `DC_PERFMON*`, and `DWB*` shift/mask macros.
- Compare `dcn_3_1_4_sh_mask.h` against `dcn_3_1_4_offset.h` and the register-list macros so every field referenced by `DSC_REG_LIST_SH_MASK_DCN20` and `DWBC_COMMON_MASK_SH_LIST_DCN30` exists with the expected name.
- Run generated-header parity checks across DSC1/DSC2/DSC3 field families and across perfmon17/18/19/20 blocks where the layout is expected to repeat.
- Exercise DSC enable/disable modes, native 4:2:2/4:2:0 modes, VBR/simple 4:2:2 modes, slice count/dimension programming, PPS generation, suspend/resume restore, and DSC power-gating paths.
- Monitor DSCC overflow/underflow interrupt status, rate-buffer maximum fullness, rate-control-buffer maximum fullness, and error/max-error readbacks under high-bandwidth DSC modes.
- Exercise DWB frame capture with crop windows, multiple output formats, CRC enable/readback, host-read throttling, backpressure/overflow counters, soft reset, and update-lock sequencing.
- Exercise DWB color-management paths for HDR multiplier, gamut remap A/B matrices, OGAM bypass/RAMA modes, LUT index/data writes, and RAMA region programming; adjacent chunks are needed for full RAMA/RAMB coverage.
- Read perfmon17 through perfmon21 counters with known event selections and verify enable, trigger, current-value interrupt, low/high readback, and rollover behavior.

## Open Questions For Merge Lane

- Confirm the previous chunk contains the start of DSC0 `DSCC_PPS_CONFIG13` and earlier DSC0 field definitions.
- Confirm the next chunk completes `DWB_OGAM_RAMA_REGION_26_27` through `DWB_OGAM_RAMA_REGION_32_33` and the DWB RAMB field family.
- In the final per-file report, avoid describing this chunk as a complete DWB writeback mask surface; it is only the DWB top/DWBCP opening portion.
