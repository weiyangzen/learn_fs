# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 183118-185509

## Purpose

This chunk is a generated AMD DCN 3.2.0 shift/mask header slice. It contains C preprocessor metadata for hardware register fields only: `__SHIFT` macros encode field low-bit positions and `_MASK` macros encode the corresponding bit masks. The `//<REGISTER>` comments group fields by register. There are no C functions, structs, enums, runtime branches, allocations, locks, or direct MMIO operations in this range.

The range covers the generic `C20_PHY_CR3_LANEX` digital PHY lane area, starting with the tail of `C20_PHY_CR3_LANEX_DIG_ASIC_TX_OVRD_IN_0`, then covering LANEX TX override/input/output, TX power-control, TX DCC/stat/clock-align/LBERT/FIFO, TX analog crossbar and analog control registers, the matching LANEX RX override/input/output and RX power-control/VCO/CDR/adaptation/stat/IQC families, and ending inside `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_VCO_OVRD_OUT_0`.

The source tree path is under a local `ceph-client` mirror, but this header belongs to the AMDGPU display register metadata set, not Ceph or distributed filesystem logic.

This chunk is boundary-partial at both ends. Line 183118 continues `C20_PHY_CR3_LANEX_DIG_ASIC_TX_OVRD_IN_0` from the previous chunk with only the pstate and reserved mask tail visible. Line 185509 stops after the first mask definitions for `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_VCO_OVRD_OUT_0`; the rest of that register continues in the following chunk.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position used by register helper code when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw in-register mask used for masked MMIO updates and reads.
- `//<REGISTER>` comments provide the only local register grouping in this file.

This 2,392-line range contains 2,170 `#define` lines, with 1,085 shift macros and 1,085 mask macros. The equal shift/mask count is a useful local consistency signal, but the range still starts and ends in partial register groups.

Major register families in this chunk include:

- `C20_PHY_CR3_LANEX_DIG_ASIC_TX_*`: lane, TX override, raw TX ASIC input, and TX ASIC output fields. These describe clock-ready, reset, inversion, data enable, request, low-power detect, pstate, rate, width, wide-transfer alignment, MPLLB select, detect-RX request, flyover, disable/beacon, boost levels, equalization cursor values, DCC range/update controls, ACK/detect/calibration status, and miscellaneous override fields.
- `C20_PHY_CR3_LANEX_DIG_TX_PWRCTL_*`: TX power-state templates for `P0`, `P0S`, `P1`, and `P2`, TX power-up timing registers, TX control fields, and TX power-state status. These include analog reference generator, VCM hold, analog/digital clocking, reset, serial/data enable, RX detect permission, VBOOST permission, DCC enable, bleeder controls, word clock enable, timing fast-path bits, skip clock-align controls, DCC DAC write controls, request disable, and power state-machine status.
- `C20_PHY_CR3_LANEX_DIG_TX_DCC_CTL_*`, `TX_STAT_*`, `TX_CLK_ALIGN_*`, `TX_LBERT_*`, `TX_LVL_CALC_STAT`, and `TX_FIFO_CTL`: TX DCC IDAC offset override/status fields, statistic sample/load/count controls, comparison clock controls, clock-align startup/retrigger/status fields, loopback BERT control and pattern fields, calibration code status, and FIFO read pointer/bypass controls.
- `C20_PHY_CR3_LANEX_DIG_ANA_XF_TX_*`: TX analog crossbar override outputs, TX termination-code overrides, TX analog DCC enable/config/calibration controls, analog TX equalization override/status fields, and analog CREG00-CREG05/override fields. These cover MPLLA/MPLLB clocks, analog clock/reset/serial/data/reference/VCM/VREG/VBOOST/word-clock controls, RX detect, reference selection, termination code, DCC calibration DACs, TX equalization status, analog test-bus selection, oscillator and regulator controls, pull-up/down, IBOOST, VPTX, ring control, and slew-rate enable.
- `C20_PHY_CR3_LANEX_DIG_ASIC_RX_*`: RX override inputs, raw RX ASIC inputs/outputs, CDR/VCO and EQ ASIC inputs, signal detect, VCO config, CTLE/VGA/AFE/DFE override fields, ACK/adaptation/valid status, miscellaneous overrides, and extended equalizer controls. These map reset, invert, data enable, request, low-power detect, pstate, rate, width, DFE bypass, reference/VCO load values, DIV16P5 clocking, CDR tracking/SSC, disable, VREG clock bypass, flyover, loopback selection, DCC controls, signal-detect thresholds/filter, CTLE/VGA/AFE gains, DFE taps 1-5 and additional comparator/slicer offsets.
- `C20_PHY_CR3_LANEX_DIG_RX_PWRCTL_*`: RX power-state templates for `P0`, `P0S`, `P1`, and `P2`, RX power-up timing, RX control, and RX status fields. These include AFE, clock regulator, DIV16P5 clock, analog clock/DCC, deserializer, CDR, VCO reset/calibration/continuous calibration, digital clock, DFE, bypass SLC, bleeder, fast VREG, DCC/EQ DAC write forcing, IQC skip, and power state-machine status.
- `C20_PHY_CR3_LANEX_DIG_RX_VCOCAL_*`, `RX_CDR_*`, and `RX_DPLL_*`: RX VCO calibration controls/timers/status, CDR phase-detector and SSC gain controls/status, DPLL frequency value, and upper/lower frequency bounds.
- `C20_PHY_CR3_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation configuration, reset, status, DFE/slicer offsets, DCC IDAC offsets, fast flags, and SSM configuration/final-code fields. These describe CTLE/VGA/ATT/DFE enable masks, thresholds, adaptation step/mu values, error initializers, tap reset selectors, adaptation status readbacks, even/odd data and error slicer controls, DCC phase/data/bypass differential/common-mode offsets, SSM thresholds/counters, and final equalization codes.
- `C20_PHY_CR3_LANEX_DIG_RX_STAT_*` and `RX_IQC_CTL_*`: RX statistic load/mask/match/control/sample/count registers, extended load values, IQC reset adjustment, IQC configuration, and IQC FSM status fields.
- `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_*`: RX analog crossbar override outputs for data-rate/divider/DFE/bypass/reset controls, RX analog power override outputs, signal-detect calibration fields, and the beginning of RX analog VCO override output fields.

Common field patterns are value/enable override pairs (`*_OVRD_VAL` / `*_OVRD_EN`, or value plus `*_OVRD_EN`), status-plus-override pairs for hardware outputs, banked or per-tap calibration/status values, `FAST_*` and `SKIP_*` shortcuts, power-state templates, and explicit reserved masks such as `RESERVED_15_10_MASK`.

## Control Flow

There is no executable control flow in this header. Runtime behavior is indirect:

1. DCN 3.2.0 driver code includes the companion offset header for register addresses and this mask header for field positions.
2. Display Core register-list macros or block-specific register tables bind offsets, shifts, and masks into typed hardware access helpers.
3. MMIO helper macros such as register read, write, get, set, and update helpers use these constants to preserve unrelated fields while manipulating the requested bit range.
4. The actual sequencing for TX/RX power-up, DCC/IQ calibration, receiver adaptation, CDR/VCO calibration, signal detect, link training, loopback BERT, and status polling lives in consuming driver and firmware-facing code, not in this generated file.

The macros do not encode access type or ordering. A field that looks writable in this header may be read-only status, write-one-to-clear, self-clearing trigger, firmware-owned scratch, or reserved according to the hardware register specification.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It names hardware-backed MMIO fields whose state belongs to the DCN 3.2 PHY lane hardware:

- TX state includes override latches, raw ASIC inputs and outputs, per-power-state templates, timing controls, DCC offset controls, statistic counters, clock alignment state, loopback BERT patterns, FIFO mode, analog crossbar override outputs, and analog calibration/control registers.
- RX state includes override latches, raw ASIC inputs and outputs, signal-detect settings, VCO/CDR/DPLL controls and status, adaptation coefficients and status, DFE/slicer/DCC offsets, statistic counters, IQC configuration/status, analog power/control overrides, and signal-detect/VCO analog calibration controls.
- Power-state template fields can persist across mode transitions until reprogrammed or reset, while status fields reflect live hardware state-machine outputs or latched completion/error states.

Side effects and retention are hardware-defined. Some fields may survive ordinary modesets or retrains; others reset on PHY, link, power, suspend/resume, or ASIC reset events. This header does not describe reset values, volatility, ownership, or whether a consumer must preserve reserved bits, so those rules must come from the register database and surrounding driver logic.

## Dependencies And Integration Points

This header must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which provides the matching DCN 3.2.0 register offsets. Shift/mask drift can compile cleanly while causing masked MMIO operations to read or write the wrong bit fields.

Direct include sites for `dcn_3_2_0_sh_mask.h` visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`

Functional integration points include:

- DCN32 resource and register descriptor construction, where generated offset/shift/mask constants are bound to Display Core blocks.
- DMUB and Display Core initialization paths that need exact register field metadata for firmware-visible hardware setup.
- PHY/link-training paths that program TX and RX pstate, rate, width, reset, request, VBOOST, DCC, CDR/VCO, adaptation, signal-detect, and equalization controls.
- Diagnostics and debug features that read power-state machine status, calibration completion, DCC/IQ/adaptation codes, CDR/VCO status, statistic counters, LBERT error counts, and raw ASIC input/output mirrors.
- Override and test flows that intentionally force analog/digital TX/RX controls away from their normal firmware or hardware state-machine values.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can compile and link while corrupting live PHY programming, link training, power transitions, calibration, or debug decoding.
- The chunk is not a complete logical unit. It starts in the mask tail of `C20_PHY_CR3_LANEX_DIG_ASIC_TX_OVRD_IN_0` and ends in the middle of `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_VCO_OVRD_OUT_0`.
- `LANEX` generic lane definitions can be confused with lane-specific `RAWLANEAON*` definitions from adjacent chunks. Names may look similar but refer to different register blocks or hardware ownership.
- Override-enable bits are hazardous. Leaving a `*_OVRD_EN` bit asserted can force reset, clocks, power, VCO/CDR, DFE, equalization, signal detect, or analog regulator behavior and fight firmware or hardware state machines.
- Power-state template fields must match the intended pstate and link mode. Swapping `P0`, `P0S`, `P1`, or `P2` field meanings can produce failures only during idle, fast wake, retrain, hotplug, or suspend/resume paths.
- CDR/VCO/DPLL and adaptation fields are rate-, width-, and signal-quality-sensitive. A bad mask can appear only at specific DisplayPort/eDP rates, lane counts, spread-spectrum settings, cable conditions, temperatures, or voltage corners.
- TX and RX analog crossbar fields expose low-level analog controls. Accidental writes to regulator, bleeder, oscillator, termination, VBOOST, IBOOST, VPTX, or test-bus bits can create unstable or hard-to-debug PHY behavior.
- Status, counter, clear, trigger, configuration, and reserved fields are indistinguishable at the preprocessor level. Consumers need external access-type knowledge before writing fields such as status counters, done bits, final codes, FSM states, and reserved masks.
- Many statistic and sample counters include done/overflow bits in the high bit. Decoding or clearing them with the wrong mask can mix a count value with completion or overflow state.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU Display Core with DCN32 support enabled. Symbol or include breakage should surface in DCN32 resource, DMUB, IRQ, GPIO, clock, and low-level register users.
- Mechanically compare this range against the authoritative AMD register database or regenerated `dcn_3_2_0_sh_mask.h`; each field should retain the expected shift and mask, including reserved fields.
- Cross-check the companion `dcn_3_2_0_offset.h` so every visible `C20_PHY_CR3_LANEX_DIG_*` register name remains aligned between offsets and masks.
- On DCN32 hardware, exercise DisplayPort/eDP link bring-up, hotplug, retrain, lane-count/rate changes, pstate transitions, suspend/resume, and low-power entry/exit.
- Validate TX/RX calibration telemetry around DCC, VCO, CDR, adaptation, DFE tap status, signal-detect calibration, statistic counters, and power state-machine status. Decoded values should be stable and plausible across retrains.
- Exercise diagnostic and test paths that use LBERT, loopback, manual overrides, fast/skip calibration modes, and statistic counters; these are the paths most likely to depend on rarely used fields in this generated range.
- Compare register dumps before and after masked updates. Only intended field bits should change, reserved bits should remain stable unless the hardware specification requires otherwise, and override-enable bits should be cleared when a test or debug flow ends.

## Cross-Chunk Notes

The final per-file report should merge this chunk with `subset-b-002003` for the beginning of `C20_PHY_CR3_LANEX_DIG_ASIC_TX_OVRD_IN_0` and with the following chunk for the rest of `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_VCO_OVRD_OUT_0`. This document is intentionally limited to the assigned source range and should be treated as the chunk artifact for `subset-b-002004`.
