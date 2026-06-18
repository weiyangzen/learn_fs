# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 68713-71102

## Scope

This chunk is a generated register shift/mask section from the DCN 3.2.0 ASIC register header. It covers the tail of `C20_PHY_CR0_LANE3_DIG_ANA_XF_TX_TERM_CODE_CLK_OVRD_OUT`, then a large block of `C20_PHY_CR0_LANE3` PHY lane 3 transmitter/receiver analog and digital RX fields, and ends at the beginning of `C20_PHY_CR0_RAWLANE0_DIG_TX_PCS_XF_OVRD_IN_1`. Every entry follows the same contract: a register comment names the register, then one `__SHIFT` macro and one `_MASK` macro per bitfield.

## Purpose

The purpose of this chunk is to expose bit positions and masks for low-level display PHY control registers on AMD DCN 3.2 hardware. Driver code includes this header together with the matching `dcn_3_2_0_offset.h` file and uses generic register helpers to pack/unpack field values. These definitions are not algorithms; they are hardware metadata that make register writes less error-prone by centralizing field layout.

The covered fields are mostly 16-bit PHY register fields for C20 PHY CR0:

- Lane 3 TX analog DCC enable/config/calibration fields, TX equalization override/output fields, TX status inputs/outputs, and TX analog control registers `CREG00` through `CREG05`.
- Lane 3 digital ASIC RX override/input/output fields for power, data rate, loopback, phase, equalization, DFE, CDR/VCO controls, and EQ adaptation status.
- Lane 3 RX power control, VCO calibration, LBERT, CDR, DPLL, adaptation-control, statistic-counter, IQC, analog RX control/power/sigdet/VCO/calibration/AFE/slicer/IQ/loopback/status, and analog RX `CREG00` through `CREG11` fields.
- The beginning of raw lane 0 TX PCS crossbar/override definitions for lane loopback, link number, reset/request, pstate, low-power detect, data enable, invert, clock-ready, beacon, and MPLL enable.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or persistent variables in this chunk. The important exported interface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` is the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` is the field mask after shifting into register position.
- Register comment lines such as `//C20_PHY_CR0_LANE3_DIG_RX_ADPTCTL_ADPT_CFG_0` group subsequent macros until the next comment.

The main register groups visible in this chunk are:

- TX analog/DCC: `TX_ANA_DCC_EN`, `TX_ANA_DCC_CONFIG`, `TX_ANA_DCC_CAL_*`, `TX_STAT_EQ_OVRD_*`, `TX_STAT_OUT_*`, `TX_STAT_EQ_OUT_*`, `TX_STAT_IN_0`, and `TX_ANA_CREG00` to `TX_ANA_CREG05`.
- RX ASIC override and ASIC status: `DIG_ASIC_RX_OVRD_IN_*`, `OVRD_SIGDET_IN`, `OVRD_VCO_IN`, `OVRD_EQ_IN_*`, `OVRD_OUT_0`, `ASIC_IN_*`, `CDR_VCO_ASIC_IN`, `EQ_ASIC_IN_*`, `ASIC_OUT_0`, and `OVRD_MISC`.
- RX lane control/calibration: `RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_LBERT_*`, `RX_CDR_*`, `RX_DPLL_*`, and `RX_ADPTCTL_*`.
- RX statistics/IQC: `RX_STAT_*`, `RX_IQC_CTL_*`.
- RX analog crossbar: `ANA_XF_RX_CTL_OVRD_OUT`, `RX_PWR_OVRD_OUT_*`, `RX_SIGDET_*`, `RX_VCO_OVRD_OUT_*`, `RX_CAL_*`, `RX_DAC_CTRL*`, `RX_AFE_OVRD_IN_*`, `RX_SCOPE`, `RX_SLICER_CTRL`, `RX_ANA_IQ`, `RX_ANA_IQC_*`, `RX_ANA_LOOPBACK_CTRL`, `RX_ANA_AFE_UPDATE_EN`, sampler select registers, term-code override registers, RX status registers, and `RX_ANA_CREG00` to `RX_ANA_CREG11`.
- Raw lane 0 TX PCS start: `RAWLANE0_DIG_TX_PCS_XF_LANE_OVRD_IN_0`, `LANE_IN_0`, `OVRD_IN_0`, and part of `OVRD_IN_1`.

Several fields are single-bit enables or override gates, for example `*_OVRD_EN`, `*_SELF_CLR_DISABLE`, `*_RESET`, `*_REQ`, `*_DATA_EN`, `*_LOOPBACK_EN`, and `*_MPLL_EN`. Multi-bit fields include data rates, pstate, link number, TX pre/post equalization values, DFE taps, VCO calibration codes, adaptation thresholds/timers, statistic masks, slicer controls, DAC/IDAC offsets, and CREG trim/configuration values.

## Control Flow And State

This header contributes no direct control flow. The effective flow is in consumers:

1. A DCN 3.2 component includes `dcn_3_2_0_sh_mask.h` and the matching offset header.
2. Local `SR`, `SRI`, `SF`, `FN`, or `FD` macros map register and field names into register tables or helper calls.
3. `REG_SET`, `REG_UPDATE`, `REG_GET`, or related helpers combine the mask and shift constants with MMIO read/write operations.
4. Hardware persists the written state in the target PHY/register block until reset, power sequencing, firmware, or later driver writes change it.

The macros themselves are compile-time constants and do not store state. State and persistence belong to the underlying DCN/C20 PHY registers. Many covered fields are explicitly about transient hardware sequencing, including self-clearing calibration controls, status/ack bits, power-state controls, VCO/CDR calibration state, adaptation state-machine controls, and statistic counters.

## Dependencies And Integration Points

The chunk depends on the generated DCN register model being consistent across the paired headers:

- `dcn_3_2_0_offset.h` supplies register addresses.
- `dcn_3_2_0_sh_mask.h` supplies field masks and shifts.
- AMD display register helpers in files such as `display/dc/inc/reg_helper.h` and `display/dmub/src/dmub_reg.h` consume these constants through `FN`/`FD` style macros.

Repository search shows `dcn_3_2_0_sh_mask.h` is included by DCN 3.2 display integration code such as DMUB support, IRQ service, GPIO translation/factory, clock manager, resource construction, and GMC code. The exact C20 PHY field names in this chunk also appear in the generated `dpcs_4_2_3_sh_mask.h`, which indicates shared or mirrored display PHY register descriptions across DCN/DPCS register namespaces.

This particular chunk's exact C20 PHY lane symbols do not appear to be directly referenced outside generated mask headers in the scanned tree. They may still be required for build-time completeness, future bring-up code, register-table generation, debug tooling, or indirect macro expansion in code that constructs field names.

## Risks

- Incorrect masks or shifts can silently corrupt adjacent PHY fields during read/modify/write operations. This is high risk because many registers include reserved bits next to enables, calibration controls, and analog trim values.
- The chunk starts and ends inside larger logical groups. Line 68713 continues the previous `TX_TERM_CODE_CLK_OVRD_OUT` register, and line 71102 stops before the final masks of `RAWLANE0_DIG_TX_PCS_XF_OVRD_IN_1`; merge/reconciliation must preserve chunk boundaries when synthesizing the full-file report.
- `SELF_CLR_DISABLE`, calibration trigger, reset, power, and override-enable bits are sequencing-sensitive. A valid mask can still be dangerous if a caller writes it in the wrong order or fails to restore override gates.
- Many fields are lane-specific (`LANE3`) while the chunk ends by switching to `RAWLANE0`. Copy/paste or generated-name mistakes across lane indices can make code act on the wrong physical lane.
- Reserved masks are listed explicitly. Consumers should avoid writing nonzero values into reserved regions unless hardware documentation requires it.
- Because this is generated hardware metadata, manual edits are risky. The practical source of truth should be the ASIC register database/generator, with this header regenerated rather than hand-maintained.

## Test Signals

Useful validation signals for this chunk are mostly build and hardware/register-behavior checks:

- Compile coverage for DCN 3.2 users that include `dcn_3_2_0_sh_mask.h`; malformed macro names, duplicate definitions, or missing masks/shifts will surface as C preprocessor or compile errors.
- Static consistency checks that every non-reserved field has both `__SHIFT` and `_MASK`, masks fit expected 16-bit or 32-bit register width, and mask low bit equals the corresponding shift.
- Diff checks against generated sibling headers such as `dpcs_4_2_3_sh_mask.h` where the same C20 PHY fields are expected to match.
- Hardware smoke tests covering display link bring-up, link training, HPD/IRQ paths, mode setting, suspend/resume, clock/power transitions, and PHY loopback/debug flows.
- Targeted register readback tests for fields with status mirrors, such as TX/RX status outputs, CDR/VCO calibration status, adaptation status, statistic counters, and IQC status.

## Research Notes

This chunk was read as lines 68713-71102 of the source file. The content is generated preprocessor metadata only; therefore the substantive behavior is in how AMD DCN 3.2 display and DMUB code uses the constants through register helper abstractions and in the hardware side effects of the corresponding PHY registers.
