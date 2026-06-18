# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 17679-19896

## Scope

This chunk is a middle slice of AMDGPU's generated DCN 3.5.1 shift/mask header. It contains preprocessor constants only: no callable functions, structs, enums, storage objects, or local executable control flow. Its exported contract is the usual generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace, where each field macro describes the bit position and already-shifted mask for one DCN 3.5.1 display hardware register field.

The range starts in the tail of the `DC_PERFMON11` monitor block, then covers the DPP2 display pipe from top-level DPP control through CNVC, DSCL, CM, and `DC_PERFMON12`. It then repeats the same kind of register-field surface for DPP3 through CNVC, DSCL, CM, and `DC_PERFMON13`. The chunk ends at the beginning of `FMT0` output formatter fields after clamp, dynamic expansion, formatter control, and the first few bit-depth-control masks. Adjacent chunks own the preceding `DC_PERFMON11` context and the rest of `FMT0`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, network, or persistent-disk behavior.

## Purpose

The purpose of this header range is to provide ASIC-specific field metadata for DCN 3.5.1 display pipe and formatter programming. Runtime display code can refer to logical fields through register-table macros while this generated header supplies exact bit geometry for the DCN 3.5.1 register database.

The covered hardware areas are:

- `DC_PERFMON11` tail fields: monitor counter-off interrupt type, perfmon clock enable, run-enable start/stop selectors, counter interrupt status/ack bits, high current-value bits, and high/low perfmon readback fields.
- `DPP_TOP2` and `DPP_TOP3`: per-pipe DPP clock enable/gate-disable fields, soft resets for CNVC/DSCL/CM/OBUF, DPP CRC capture values/control, and host-read rate control.
- `CNVC_CFG2` and `CNVC_CFG3`: surface pixel format, alpha plane enable, format conversion/bypass/crossbar, floating-point conversion bias/scale, color keyer ranges, alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha fields.
- `CNVC_CUR2` and `CNVC_CUR3`: cursor enable/mode/pixel-alpha/update status and fixed cursor colors plus floating-point cursor scale/bias.
- `DSCL2` and `DSCL3`: scaler coefficient RAM access, scaler mode, tap control, two-tap sharpening, manual replication, horizontal/vertical scale ratios and initial phases, chroma scale/init fields, black color, update/autocal, overscan, OTG blanking, recout/MPC dimensions, line-buffer format/memory partitioning, vertical counters, DSCL memory power/status, and OBUF control/power fields.
- `CM2` and `CM3`: DPP color-management bypass/update, post-CSC matrices, gamut-remap matrices, bias registers, gamma-correction controls and LUT ports, RAM A/B piecewise-region descriptors, HDR multiplier, CM memory power/status, dealpha, and coefficient-format fields.
- `DC_PERFMON12` and `DC_PERFMON13`: performance-counter event selection, counter control, state/readback, perfmon control, current-value comparison, interrupt status/ack, and low/high counter readback.
- `FMT0` beginning: output formatter component clamps, dynamic expansion controls, pixel encoding/subsampling/double-buffer status, and the start of truncation/spatial/temporal dither bit-depth controls.

## Important APIs, Types, And Macros

There are no C APIs or concrete types in this chunk. The important interface is the generated macro pattern:

- `*_SHIFT` gives a field's least-significant bit position.
- `*_MASK` gives the field mask in its final register position.
- Register names encode hardware block and instance, such as `DPP_TOP2_DPP_CONTROL`, `CNVC_CFG2_FORMAT_CONTROL`, `DSCL2_SCL_MODE`, `CM2_CM_GAMCOR_CONTROL`, `DPP_TOP3_DPP_CONTROL`, `CM3_CM_GAMCOR_RAMB_REGION_32_33`, `DC_PERFMON13_PERFCOUNTER_CNTL`, and `FMT0_FMT_CONTROL`.

The DPP top fields are the gate and reset boundary for the per-pipe blocks. `DPP_TOP*_DPP_CONTROL` exposes `DPP_CLOCK_ENABLE`, multiple `DPPCLK`/`DISPCLK` gate-disable fields, and `DPP_TEST_CLK_SEL`. `DPP_TOP*_DPP_SOFT_RESET` exposes reset bits for `CNVC`, `DSCL`, `CM`, and `OBUF`. The `DPP_TOP*_DPP_CRC_*` registers describe CRC result components and a control register with enable, continuous/one-shot, source, stereo, interlace, pixel format, cursor format, and mask fields.

The CNVC groups describe the input converter stage. `CNVC_CFG*_FORMAT_CONTROL` is the main control surface for format expansion, 16-bit conversion, alpha enable, converter bypass and MSB alignment, positive clamps, update-pending readback, and RGB channel crossbar selection. `FCNV_FP_BIAS_*` and `FCNV_FP_SCALE_*` provide 19-bit-style bias/scale fields used by DCN 3.5 DPP code for floating-point conversion. The color keyer registers pack low/high thresholds into 16-bit halves for alpha/red/green/blue, and `ALPHA_2BIT_LUT` packs four 8-bit alpha entries into one register.

The CNVC pre-processing fields include pre-dealpha/realpha enable controls, `PRE_CSC_MODE` current-mode readback, two banks of packed 16-bit pre-CSC matrix coefficients, coefficient-format selection, and pre-degamma mode/select fields. Cursor fields under `CNVC_CUR*` expose hardware cursor enable/mode/ROM/pixel-alpha/update status and 24-bit colors plus packed scale/bias.

The DSCL groups are the scaler programming surface. `SCL_COEF_RAM_TAP_SELECT` selects tap pair, phase, and filter type; `SCL_COEF_RAM_TAP_DATA` packs even/odd tap coefficients and coefficient enable bits. `SCL_MODE` carries DSCL mode, coefficient RAM selection/current readback, chroma/alpha coefficient modes, and read selector. `SCL_TAP_CONTROL` programs luma and chroma horizontal/vertical tap counts, while `DSCL_2TAP_CONTROL` programs two-tap hardcoded coefficient and sharpening controls. Scale ratio and init registers use wide fixed-point masks for luma/chroma horizontal/vertical paths, including bottom-field variants.

The DSCL geometry and buffering fields describe how the scaler presents data downstream. Overscan and blanking fields pack start/end or left/right/top/bottom values; `RECOUT_*` and `MPC_SIZE` describe output rectangles; `LB_DATA_FORMAT` and `LB_MEMORY_CTRL` describe line-buffer format and partitioning; `LB_V_COUNTER` exposes luma/chroma vertical counters. `DSCL_MEM_PWR_CTRL` and `DSCL_MEM_PWR_STATUS` enumerate force/disable/state fields for LUT memory and six line-buffer groups, plus `LB_MEM_PWR_MODE`. `OBUF_CONTROL` and `OBUF_MEM_PWR_CTRL` cover output-buffer bypass/full-buffer/hold-count and memory-power controls.

The CM groups describe the color-management block. Post-CSC and gamut-remap matrices pack pairs of 16-bit coefficients, including alternate `_B_` banks. `CM_CONTROL`, `CM_POST_CSC_CONTROL`, `CM_GAMUT_REMAP_CONTROL`, and `CM_GAMCOR_CONTROL` carry bypass, update-pending, mode, select, PWL-disable, and current-mode/current-select status fields. Bias registers provide packed Y/G and Cb/B values plus a separate Cr/R value. `CM_HDR_MULT_COEF` contains the HDR multiplier coefficient.

The gamma-correction interface is indexed and banked. `CM*_CM_GAMCOR_LUT_INDEX`, `CM*_CM_GAMCOR_LUT_DATA`, and `CM*_CM_GAMCOR_LUT_CONTROL` define LUT index, data, write-color mask, read-color selection, host selection, and config mode. RAM A and RAM B each have per-channel start, start slope, start base, end base, end/slope, and offset registers. Region-pair registers from `REGION_0_1` through `REGION_32_33` pack LUT offsets and segment counts for two PWL regions into one register.

The perfmon groups use a repeated field contract. `DC_PERFMON12_*` and `DC_PERFMON13_*` define event selection, counted current-value source, increment mode, hardware control, run-enable mode, restart, interrupt enable, off-mask, active status, and counter selector fields. They also expose counter state for counters 0-7, perfmon state/report-count/control bits, counter-off interrupt status/ack, current-value compare status/ack bits, and low/high readback fields.

The `FMT0` fields at the end are output-formatter metadata. Clamp component registers pack lower/upper limits for R/G/B. `FMT_DYNAMIC_EXP_CNTL` enables dynamic expansion and selects expansion mode. `FMT_CONTROL` defines stereo sync override, spatial-dither frame-counter behavior, pixel encoding, subsampling mode/order, CbCr bit-reduction bypass, and double-buffer update-pending status. `FMT_BIT_DEPTH_CONTROL` begins the truncation and dither field list but is not complete in this chunk.

## Control Flow

This header range has no local control flow. Runtime behavior is created by consumers that include `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`, build register tables, and use display register helpers for MMIO reads and writes.

A typical DCN 3.5.1 path is:

1. DCN351 resource, IRQ, DMUB, and related display code includes the DCN 3.5.1 offset and shift/mask headers.
2. Resource construction macros such as `SRI_ARR(reg_name, block, id)` paste logical register names onto generated instance names such as `regCNVC_CFG2_FORMAT_CONTROL`, `regDSCL3_SCL_MODE`, or `regFMT0_FMT_CONTROL`, while field macros such as `TF_SF(...)` paste logical field names onto `REGISTER__FIELD_MASK` or `REGISTER__FIELD__SHIFT`.
3. Runtime helpers such as `REG_READ`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, and related `reg_helper.h` operations use the table-built offsets, masks, and shifts to perform read/modify/write operations.
4. Higher-level DPP, DSCL, CM, OPP, IRQ, and DMUB code sequences those operations around pipe enable, update locks, blanking, power transitions, LUT programming, or status polling.

Visible examples in this tree include `dcn351_resource.c`, which includes the DCN 3.5.1 headers and defines base/offset/field expansion macros; `dcn35_dpp.c`, which programs DPP clock enable and `FCNV_FP_BIAS_*`/`FCNV_FP_SCALE_*` fields through DPP register helpers; and `dmub_dcn351.c`, where `dmub_srv_dcn351_regs_init()` expands DCN35 register and field lists using the DCN 3.5.1 offset and shift/mask headers. The header itself does not encode sequencing rules, waits, or policy decisions.

## State And Persistence Behavior

The file itself stores no runtime state and persists nothing. It describes hardware register state whose lifetime is controlled by display pipe programming, DPP/OPP power, modesets, plane updates, cursor updates, suspend/resume, and GPU reset.

State represented by this chunk includes:

- DPP clock, clock-gating, soft-reset, CRC, and host-read state for DPP2 and DPP3.
- CNVC conversion state: input pixel format, alpha plane, format expansion/conversion/bypass, channel crossbar, FP bias/scale, color keying, alpha LUT, pre-CSC/pre-degamma/pre-dealpha/pre-realpha, and cursor color/format state.
- DSCL scaler state: filter taps and coefficient RAM contents, scaler mode, scale ratios, initial phases, two-tap sharpening, overscan, output rectangles, line-buffer partitioning, update-pending/autocal state, and memory-power state.
- CM color state: post-CSC and gamut-remap matrices, gamma-correction LUT index/data/configuration, PWL RAM A/B region descriptors, biases, HDR multiplier, memory-power state, and dealpha/coefficient-format controls.
- Perfmon diagnostic state: selected events, run/stop selectors, active/restart/interrupt controls, compare-value interrupt status, counter states, and counter readback values.
- FMT0 formatter state for clamp, dynamic expansion, pixel encoding, subsampling, double-buffer status, and the start of truncation/dither controls.

Several fields are status-only or status-like readbacks, such as update-pending, current-mode/current-select, memory-power state, perfmon active/status bits, and double-buffer update-pending. Several others are write controls that affect live hardware immediately or at a later synchronized update point. Indexed LUT registers are especially stateful: writes through `CM_GAMCOR_LUT_INDEX` and `CM_GAMCOR_LUT_DATA` modify table entries and the current index influences following accesses.

Bad register values can persist until the affected pipe is reprogrammed, reset, power-cycled, or the GPU is reset. Some display programming is restored during modeset or suspend/resume paths, but this generated header has no restore logic; it only defines the bit layout that restore/programming code depends on.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides matching register offsets and base indices. These shift/mask macros are only correct when paired with the DCN 3.5.1 offset header and the DCN351 register-instance layout.

Important visible integration points include:

- `display/dc/resource/dcn351/dcn351_resource.c`, which includes `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`, then expands `SR`, `SRI`, `SRI_ARR`, and related macros to build register tables using `ctx->dcn_reg_offsets`.
- `display/dc/dpp/dcn35/dcn35_dpp.h` and `display/dc/dpp/dcn35/dcn35_dpp.c`, which inherit DCN3 DPP field lists and add DCN35-specific DPP control fields. Runtime code uses the generated field masks/shifts to program DPP clock control and CNVC FP bias/scale.
- `display/dc/resource/dcn32/dcn32_resource.h` and later resource list patterns, which show how logical DPP registers such as `CM_GAMCOR_*`, `DSCL_*`, `FORMAT_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, `DPP_CONTROL`, `FCNV_FP_*`, and `FMT_*` are table-driven by generated instance names.
- `display/dmub/src/dmub_dcn351.c`, where `dmub_srv_dcn351_regs_init()` fills DMUB register offsets, masks, and shifts by expanding register and field lists over this header.
- `display/dc/irq/dcn351/irq_service_dcn351.c`, which includes the same DCN 3.5.1 generated headers for IRQ source metadata.
- OPP/formatter code through common `FMT` register lists, because this chunk begins the `FMT0` field layout used for output formatting, dithering, and pixel-encoding programming.

The generated namespace is cross-generation but not interchangeable. Nearby headers such as `dcn_3_5_0_sh_mask.h`, `dcn_3_2_1_sh_mask.h`, `dcn_3_6_0_offset.h`, and later DCN 4.x headers carry many similar names, but field availability, offsets, and exact masks may differ. Consumers must bind the correct offset and mask header pair for the target ASIC.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Shift and mask constants compile cleanly even when wrong, but a bad constant can update the wrong field, leave stale bits behind, truncate coefficient data, corrupt a neighboring field, or decode status incorrectly.

Chunk-boundary risk is real here. The first lines are only the tail of the `DC_PERFMON11` block, and the final lines stop before the rest of `FMT0_FMT_BIT_DEPTH_CONTROL` and later formatter fields. The final per-file report must merge adjacent chunks before making whole-block claims about perfmon11 or FMT0.

Instance pairing is critical. Fields named with `2` must match `DPP_TOP2`, `CNVC_CFG2`, `DSCL2`, `CM2`, and the corresponding generated offsets; fields named with `3` must match the DPP3/CNVC3/DSCL3/CM3 offsets. Copying a mask from one generation or instance into another table can create display failures that look like runtime sequencing bugs.

Color-management fields are precision-sensitive. Matrix coefficient masks, gamma LUT data widths, RAM A/B region offsets, segment counts, HDR multiplier, and coefficient-format bits directly affect visible output. Incorrect masks can cause color shifts, gamut errors, banding, broken HDR behavior, or LUT programming that appears to succeed but produces the wrong transfer curve.

Scaler and geometry fields can fail only for specific modes. Bad scale ratios, initial phases, tap counts, coefficient RAM selectors, overscan, recout/MPC dimensions, line-buffer partitions, or chroma fields can cause distortion, chroma misalignment, clipping, underflow, or blanking that appears only with certain pixel formats, rotations, scaling ratios, or multi-plane layouts.

Power and reset fields can be hazardous. DPP clock enable/gating, DPP soft reset, DSCL memory power, OBUF memory power, and CM memory power controls interact with live hardware availability. Incorrect programming can force memories off while active, leave blocks in reset, or make status bits appear stuck.

Indexed LUT programming has sequencing risk. The header defines index/data/control field geometry but not the ordering requirements for host selection, color write masks, config modes, double buffering, update locks, or pipe blanking. Callers must follow DC and hardware programming rules.

Perfmon fields are diagnostic-sensitive. Event selection, counter select, counter-off comparison, interrupt enable/status/ack, and readback masks may return plausible values even when the wrong event or counter is selected. That can hide performance regressions or mislead debug work without directly breaking display output.

`FMT0` fields at the end are incomplete in this chunk. Truncation and dithering controls are packed near high bits and often interact with random seed and temporal pattern registers in later lines. Partial review of this chunk alone is not enough to validate all output formatter behavior.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Compile coverage for DCN351 resource construction, IRQ service, DMUB register initialization, DPP programming, and OPP/formatter users that include the generated DCN 3.5.1 headers.
- Generated-register consistency checks that every `*_MASK` has a matching `*_SHIFT`, every mask width matches the hardware register database, and every register referenced by resource lists exists in `dcn_3_5_1_offset.h`.
- Cross-generation diffs against AMD's authoritative DCN 3.5.1 register database and nearby DCN 3.5.0/3.6/4.x headers, with expected differences explicitly reviewed.
- DPP clock/reset tests that exercise DPP2/DPP3 enable, clock gating, soft reset, CRC capture, host reads, runtime PM, display idle, modeset, and suspend/resume.
- CNVC tests for pixel formats, alpha plane enable, format expansion/conversion, bypass, channel crossbar, color keying, FP bias/scale, pre-CSC, pre-degamma, pre-dealpha/realpha, and cursor color/alpha behavior.
- DSCL tests for bypass, upscaling/downscaling, non-integer ratios, 4:2:0 chroma paths, coefficient RAM programming, two-tap sharpening, overscan, recout/MPC changes, multi-pipe layouts, and line-buffer partitioning.
- CM tests for post-CSC, gamut remap, gamma correction RAM A/B programming, HDR multiplier, bias, dealpha, coefficient format, LUT readback, current-mode readback, and restore after suspend/resume.
- Memory-power tests for DSCL LUT/LB groups, OBUF, and CM/GAMCOR power force/disable/state fields under active display, idle, hotplug, and reset paths.
- Perfmon tests that select known events, start/stop/restart counters, validate low/high readback, compare-value interrupt behavior, status/ack bits, and counter-state fields.
- FMT0 tests for clamp, dynamic expansion, pixel encoding, subsampling, truncation, spatial/temporal dither, and double-buffer update-pending once the following chunk's formatter fields are included.

Regression symptoms from bad constants include blank display output, distorted or clipped scaling, chroma errors, cursor artifacts, alpha/color-key mistakes, visible color shifts or banding, HDR/gamut failures, stuck update-pending bits, failed memory-power transitions, broken CRC capture, incorrect dithering, misleading perf counters, or failures that appear only on DCN 3.5.1 ASICs.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dcn_3_5_1_sh_mask.h`. The preceding chunk owns the beginning of the `DC_PERFMON11` context before line 17679. The following chunk owns the rest of `FMT0_FMT_BIT_DEPTH_CONTROL` and subsequent formatter/register blocks after line 19896. The merge/reconciliation lane should treat this document as the DPP2/DPP3 CNVC/DSCL/CM/perfmon middle portion plus the start of FMT0 for the full DCN 3.5.1 shift/mask contract.
