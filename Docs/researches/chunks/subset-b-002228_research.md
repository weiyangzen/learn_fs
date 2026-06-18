# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 25253-27781

## Scope

This chunk is a generated AMD DCN 4.2.0 register shift/mask header slice. It contains C preprocessor constants only: every exported symbol maps a hardware register field to either a bit shift (`__SHIFT`) or a bit mask (`_MASK`). There are no functions, structs, enums, storage objects, branches, or direct runtime side effects in this slice.

The slice starts in the tail of the `DC_PERFMON10_PERFCOUNTER_CNTL2` field definitions, then covers the DPP1 display-pipe register field metadata, and ends at the start of `DSCL2_DSCL_EASF_V_RINGEST_3TAP_CNTL3`. It is therefore a chunk-level view of a larger file; adjacent chunks are needed for the full `DC_PERFMON10` start and the rest of the DPP2 scaler/EASF block.

## Purpose

The header gives the AMD display driver compile-time knowledge of DCN 4.2.0 register bit layouts. Driver code combines these `_MASK` and `__SHIFT` macros with register-address macros and register helper macros to read, update, and compose values for display controller hardware.

Within this chunk, the hardware domains are:

- `DC_PERFMON10` and `DC_PERFMON11`: display performance monitor counter controls, state, current-value, interrupt status/ack, read select, and low/high counter values.
- `DPP_TOP1` and `DPP_TOP2`: display pipe processor top-level clock gating, soft reset, DPP CRC, and host-read rate control fields.
- `CNVC_CFG1` and `CNVC_CFG2`: converter pixel format, format expansion/conversion, alpha, color keying, pre-dealpha, pre-color-space conversion matrices, coefficient format, pre-degamma, and pre-realpha fields.
- `CM_CUR1` and `CM_CUR2`: cursor enable/mode/color, cursor floating-point scale/bias, and two cursor matrix banks.
- `DSCL1` and the beginning of `DSCL2`: scaler coefficient RAM, scaler mode, tap counts, fixed-point scale ratios and initial phases, chroma/luma variants, black color, update/autocal controls, overscan, blanking, recout/MPC sizes, line-buffer and output-buffer controls, memory power state, EASF sharpening/ring-estimation controls, image-sharpening controls, and LUT memory power fields.
- `CM1`: color management bypass/update, post-CSC matrices, bias, gamma correction LUT and piecewise region programming for RAM A/B, HDR multiplier, memory power, dealpha, debug, histogram collection/status, and histogram interrupt fields.

## Important APIs, Types, And Macros

This chunk exports macro constants following the generated naming contract:

- `REGISTER__FIELD__SHIFT`: bit offset of `FIELD` within `REGISTER`.
- `REGISTER__FIELD_MASK`: bit mask of `FIELD` within `REGISTER`.

The most important macro families in this chunk are:

- Performance monitor macros such as `DC_PERFMON10_PERFCOUNTER_STATE__PERFCOUNTER_CNT0_STATE_MASK`, `DC_PERFMON10_PERFMON_CNTL__PERFMON_CNTOFF_INT_ACK_MASK`, and the parallel `DC_PERFMON11_*` symbols.
- DPP top-level control macros such as `DPP_TOP1_DPP_CONTROL__DPP_CLOCK_ENABLE_MASK`, `DPP_TOP1_DPP_SOFT_RESET__DSCL_SOFT_RESET_MASK`, `DPP_TOP1_DPP_CRC_CTRL__DPP_CRC_SRC_SEL_MASK`, and the same `DPP_TOP2_*` family.
- Converter macros such as `CNVC_CFG1_FORMAT_CONTROL__CNVC_BYPASS_MASK`, `CNVC_CFG1_COLOR_KEYER_*`, `CNVC_CFG1_PRE_CSC_*`, and matching `CNVC_CFG2_*` symbols.
- Cursor macros such as `CM_CUR1_CURSOR0_CONTROL__CUR0_ENABLE_MASK`, `CM_CUR1_CUR0_MATRIX_MODE__CUR0_MATRIX_MODE_CURRENT_MASK`, and matrix-bank constants for `_A` and `_B`, plus the `CM_CUR2_*` mirror.
- Scaler macros such as `DSCL1_SCL_MODE__DSCL_MODE_MASK`, `DSCL1_SCL_TAP_CONTROL__SCL_H_NUM_TAPS_MASK`, `DSCL1_SCL_HORZ_FILTER_SCALE_RATIO__SCL_H_SCALE_RATIO_MASK`, `DSCL1_DSCL_MEM_PWR_CTRL__LB_MEM_PWR_MODE_MASK`, `DSCL1_OBUF_MEM_PWR_CTRL__OBUF_MEM_PWR_STATE_MASK`, `DSCL1_DSCL_EASF_*`, and the opening `DSCL2_*` mirror.
- Color-management macros such as `CM1_CM_POST_CSC_*`, `CM1_CM_GAMCOR_CONTROL__CM_GAMCOR_MODE_MASK`, `CM1_CM_GAMCOR_LUT_*`, `CM1_CM_GAMCOR_RAMA_REGION_*`, `CM1_CM_GAMCOR_RAMB_REGION_*`, `CM1_CM_HIST_STATUS__CM_HIST_COUNT_OVERFLOW_MASK`, and `CM1_CM_HIST_INT_CONTROL__CM_HIST_RDY_INT_EN_MASK`.

The header itself defines no helper API, but the macro names are designed for AMD display register helpers that concatenate register and field names, commonly through local `FN(reg_name, field_name)` macros and `REG_GET`, `REG_SET`, `REG_UPDATE`, or related register-access wrappers in the display driver.

## Control Flow

There is no executable control flow. The effective runtime flow happens in consumers:

1. A DCN 4.2 component includes this mask header together with the matching register-address header.
2. The component's register tables or helper macros reference a `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` pair.
3. The register helper reads or writes a MMIO register, masking and shifting the field into or out of the register value.
4. The hardware changes display pipeline state, reports status, or returns latched counter/histogram data depending on the specific register field.

The ordering in this chunk is hardware-address-block oriented. DPP1 blocks are grouped as top, converter, cursor, scaler, color management, and DPP-local perfmon. DPP2 then begins with the same repeated structure, indicating multiple display pipes with identical or near-identical bit layouts under different register instances.

## State And Persistence Behavior

The macros do not persist state. They describe persistent hardware register fields whose values live in GPU display controller registers while the device is powered and configured.

State-bearing hardware represented by this chunk includes:

- Perfmon control and counter state: enable/state bits, counter active flags, interrupt enable/status/ack bits, counted-value selectors, counter low/high values, and current-value high/low fields.
- DPP pipeline state: clock enable/gating-disable bits, soft-reset bits for converter/scaler/color/output-buffer/histogram subblocks, and CRC control/readback state.
- Converter and cursor state: pixel format, alpha plane enable, color key and alpha LUT configuration, pre-CSC matrices and current selection bits, cursor enable/update-pending bits, cursor colors, and cursor matrix banks.
- Scaler state: coefficient RAM selection/current bits, phase and ratio registers, autocal pipe identifiers, viewport/blanking/recout sizes, line-buffer partitioning, memory power state/status, output-buffer status, EASF/sharpening controls, and sharpening LUT memory power state.
- Color-management state: post-CSC matrices and current mode bits, gamma LUT index/data/control, RAM A/B gamma region programming, memory power status, histogram lock/index/data/status fields, and histogram ready interrupt enable/status.

Because these are MMIO field definitions, persistence is hardware-specific. Values may be reset by GPU reset, display pipe reset, power-gating, mode set reprogramming, or explicit writes by the display manager. `*_UPDATE_PENDING`, `*_CURRENT`, `*_STATUS`, and `*_STATE` fields are especially sensitive to hardware sequencing and may reflect latched or asynchronous state rather than a simple software-owned value.

## Dependencies

Direct dependencies are limited to the C preprocessor and the surrounding generated register header set. The include guard and SPDX/copyright header live outside this chunk, but this slice depends on the whole file being included as a normal header.

Runtime consumers depend on:

- Matching DCN 4.2.0 register address headers that define the register offsets corresponding to these field masks.
- AMD display register helper infrastructure that uses mask/shift pairs to perform safe field updates.
- Hardware register specifications for DCN 4.2.0, because the correctness of every constant is defined by the ASIC register map rather than by local source logic.

Repository usage search shows `dcn_4_2_0_sh_mask.h` is included by DCN 4.2 display paths such as DMUB support, IRQ service, and GPIO translation/factory code. Broader DC register programming patterns use `FN()` and `REG_*` helpers to bind generated field names into component-specific register tables.

## Integration Points

This chunk integrates with:

- DCN 4.2 display enablement code that constructs per-block register structures for DPP, CNVC, DSCL, CM, cursor, perfmon, and related display subblocks.
- Display mode programming paths that set scaler ratios, taps, phase initialization, viewport/recout sizing, color conversion, degamma/gamma/post-CSC, cursor format, and alpha behavior.
- Diagnostics and validation paths that read CRC values, performance counters, histogram data/status, debug data, and memory power status.
- Power-management and reset sequencing through DPP clock-gating fields, DPP soft reset bits, scaler/color/output-buffer memory power control fields, and related state/status masks.
- Interrupt/status handling for perfmon counter interrupts and CM histogram-ready interrupts.

The repeated `*1` and `*2` register families indicate per-pipe integration: DPP1 and DPP2 use the same software programming model with different physical register instances. This lets shared display code operate on an indexed pipe by selecting the right generated register addresses and field masks.

## Risks And Edge Cases

- Generated constant drift is the primary risk. A wrong mask or shift can silently write the wrong bits in a hardware register, corrupting adjacent fields such as clock gating, reset, color conversion, scaler phase, or interrupt ack bits.
- Several fields are write-one-to-clear or ack-like by convention (`*_ACK`, interrupt status/ack, update-pending/current fields). Consumers must know hardware semantics; the mask alone does not encode whether a bit is read-only, write-one-to-clear, self-clearing, or latched.
- Packed matrix, gamma, PWL, and scaler fields often share 32-bit registers as two 16-bit values or multiple narrower values. Incorrect value range checks in callers can overflow into neighboring fields even when masks are correct if helpers are bypassed.
- DPP1 and DPP2 families are near-identical. Copy/paste or table-index mistakes can program one pipe using another pipe's register address set even though the field masks look valid.
- This chunk begins and ends mid-family. Whole-file analysis must reconcile the incomplete `DC_PERFMON10_PERFCOUNTER_CNTL2` lead-in and the incomplete `DSCL2_DSCL_EASF_V_RINGEST_3TAP_CNTL3` tail with adjacent chunks.
- Large generated headers can hide duplicate or inconsistent symbols across ASIC versions. Build coverage catches syntax/name collisions, but hardware validation is needed to catch semantically wrong bit positions.

## Test Signals

Useful validation signals for this chunk are:

- C build coverage for all DCN 4.2 include consumers, proving the generated macro names, include guard, and integer constants compile.
- Static checks that every `__SHIFT` has a corresponding `_MASK` for the same register field and that masks align with shifts and expected field widths.
- Cross-version diffs against nearby DCN mask headers, especially repeated DPP1/DPP2/CNVC/DSCL/CM fields, to flag unexpected layout changes.
- Register programming tests or hardware bring-up logs showing DPP clock/reset, scaler ratios/taps, cursor setup, color conversion/gamma, CRC readback, histogram readback, and perfmon interrupts operate on DCN 4.2 hardware.
- Runtime debugfs or driver traces confirming `REG_UPDATE`/`REG_GET` calls compose values that stay within these masks and do not disturb adjacent fields.
- Display validation tests for mode set, scaling, color management, cursor, CRC, histogram, and power-gating scenarios, because those are the hardware behaviors represented by this field metadata.
