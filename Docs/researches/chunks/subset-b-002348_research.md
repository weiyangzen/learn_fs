# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 26286-28636

## Scope

This chunk covers lines 26286-28636 of the generated AMD DPCS 4.2.2 shift/mask header. The range contains 2,142 preprocessor definitions: 1,076 `__SHIFT` definitions and 1,066 `_MASK` definitions when counted by suffix-style macro names. It spans 209 comment-delimited register block starts plus one carried-in block at the beginning, because line 26286 starts inside `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_2`. It also ends inside `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1`; the remaining shift definitions and all masks for that register continue after the requested range.

The content is declarative register metadata only. It defines bit positions and masks for DPCS CR1 supervisor analog controls, CR1 lane 0 TX/debug/statistics/analog TX controls, and the first half of CR1 lane 1 TX/RX controls. It contains no C functions, structs, enums, local storage, runtime branching, allocation, locking, or software-owned persistence.

## Purpose

This header fragment provides symbolic bitfield definitions for AMDGPU display code that programs and inspects the DPCS 4.2.2 display PHY. Consumer code pairs these field macros with companion register offsets from `dpcs_4_2_2_offset.h` and AMD display register helper macros to form read-modify-write values without embedding literal bit numbers.

The slice is centered on the CR1 DPCS PHY instance:

- Supervisor analog control and status for MPLLA/MPLLB, RTUNE, bandgap/reference regulator, and PMIX controls.
- Lane 0 ASIC-facing override and mirror registers, TX power-state programming, DCC controls, RX statistic counters, digital analog TX overrides, and direct analog TX controls.
- Lane 1 ASIC-facing override/mirror registers for both TX and RX, TX power controls, RX power/VCO/CDR/DPLL/adaptation controls, and the beginning of lane 1 RX statistic control.

## Exported API Surface

There are no callable APIs or user-defined types. The public interface is the macro namespace itself. Complete field groups generally provide:

- `REGISTER__FIELD__SHIFT`: the bit position used to place or extract the field value.
- `REGISTER__FIELD_MASK`: the bit mask for the same field in the corresponding DPCS register.

Important macro families in this chunk include:

- `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_2`, `DPCSSYS_CR1_SUP_DIG_ANA_MPLLB_OVRD_OUT_*`, `DPCSSYS_CR1_SUP_DIG_ANA_RTUNE_OVRD_OUT`, `DPCSSYS_CR1_SUP_DIG_ANA_STAT`, `DPCSSYS_CR1_SUP_DIG_ANA_BG_OVRD_OUT`, and `DPCSSYS_CR1_SUP_DIG_ANA_MPLL*_PMIX_OVRD_OUT`: CR1 supervisor analog PLL, RTUNE, bandgap, reference regulator, and PMIX override/status fields.
- `DPCSSYS_CR1_LANE0_DIG_ASIC_*`: lane 0 ASIC interface overrides and readbacks for lane loopback, TX request, P-state, rate, width, MPLLB select, data enable, main/pre/post cursor, HDMI mode, clock ready, invert, reset, detect-RX, async data, and low-power detect fields.
- `DPCSSYS_CR1_LANE0_DIG_TX_PWRCTL_*`: lane 0 TX P-state and power-up timing fields, DCC CR-bank address/data windows, DCC DAC control/range/selection/ack/address, TX clock alignment, and LBERT control.
- `DPCSSYS_CR1_LANE0_DIG_RX_STAT_*`: lane 0 RX statistic load value, data mask, pattern match controls, statistic control, counter enables, sample count, counters 0-6, calibration comparison clock control, extra match controls, statistic control extension, and statistic stop bits.
- `DPCSSYS_CR1_LANE0_DIG_ANA_*` and `DPCSSYS_CR1_LANE0_ANA_TX_*`: lane 0 digital-to-analog TX override fields, TX term-code and EQ override fields, analog status, TX DCC DAC override fields, and direct analog TX measurement/power/ATB/DCC/term/miscellaneous controls.
- `DPCSSYS_CR1_LANE1_DIG_ASIC_*`: lane 1 ASIC interface overrides and mirrors. Unlike the lane 0 portion in this chunk, lane 1 includes RX override and RX ASIC input groups for RX enable, termination enable, CDR freeze, adapt requests, rate, width, AFE/VGA/CTLE/DFE controls, calibration, CDR/VCO controls, inversion, squelch, and signal-detect selection.
- `DPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_*`: lane 1 TX P-state, power-up timing, DCC, clock alignment, and LBERT controls.
- `DPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_*`, `DPCSSYS_CR1_LANE1_DIG_RX_VCOCAL_*`, `DPCSSYS_CR1_LANE1_DIG_RX_CDR_*`, `DPCSSYS_CR1_LANE1_DIG_RX_DPLL_*`, and `DPCSSYS_CR1_LANE1_DIG_RX_ADPTCTL_*`: lane 1 RX power states, VCO calibration, receive alignment, LBERT, CDR/DPLL configuration and status, adaptation configuration/status, DFE offsets, slicer controls, adaptation reset, DAC control selection, and adaptation CR-bank address/data.
- `DPCSSYS_CR1_LANE1_DIG_RX_STAT_*`: the beginning of lane 1 RX statistic load/mask/match/control definitions, ending mid-register at `STAT_CLK_EN__SHIFT`.

## Register Areas Covered

The supervisor analog section defines CR1-wide mixed-signal controls. MPLLA and MPLLB override registers expose clock enables, output enables, analog enable, reset, calibration, divider clocks, feedback clock, gearshift, standby, integral/proportional charge-pump fields, and override selection. RTUNE and bandgap/reference regulator fields expose resistor tuning override, comparator reset, tuning mode/value, bandgap startup, async reset, reference regulator fast-start, and reference selection. These fields sit above individual lanes and can affect shared clocking or analog bias behavior.

The lane 0 ASIC interface groups describe the boundary between display/link logic and the lane 0 PHY. Override input fields can replace normal hardware signals for request, power state, link rate, width, MPLLB selection, data enable, main/pre/post cursor, HDMI mode, clock-ready, reset, invert, detect-RX, and async-data paths. Mirrored ASIC input/output groups expose the same style of signals without the override-enable bits, useful for observing the live hardware-facing state.

The lane 0 TX power-control and analog TX groups define the low-level transmitter behavior used during link bring-up, power transitions, and diagnostics. P-state registers cover analog reference generation, VCM hold, analog clocking, power-down, high-Z, termination enable, DCC enable, output enable, serializer enable, divider control, and low-power DCC values. DCC and DAC fields provide CR-bank address/data access, DAC range/selection/ack/address, and direct analog controls for TX measurement, power override, alternate bus, ATB routing, term code, override clocks, and miscellaneous TX settings.

The lane 0 and lane 1 RX statistic blocks expose programmable hardware measurement counters. They include data masks, pattern masks, pattern values, scope delay, statistic source selection, correlation/source shifts, RX clock selection, sample counter load/start, individual counter enables, pause/clock/data-delay controls, valid-loss clearing/control, counter readbacks, calibration comparison clock controls, additional pattern and saturation controls, and explicit statistic stop bits. These are bit contracts for diagnostics and calibration validation, not a software statistics implementation.

The lane 1 RX control section is broader than lane 0 in this chunk. It includes RX override fields for enable/termination/CDR/adaptation, AFE/VGA/CTLE/DFE programming, DFE data/error VDACs, slicers, CDR/VCO controls, calibration request and mode, inversion, common-mode mask, squelch, signal-detect select, and power sequencing. It also maps VCO calibration control/time/status, CDR control/status, DPLL frequency and bounds, adaptation state-machine configuration, adaptation resets, status readbacks for ATT/VGA/CTLE/DFE taps, and CR-bank address/data access.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior is created by driver code that includes these macros and writes or reads the mapped DPCS registers.

The field names imply several hardware state machines and handshakes:

- PLL and common analog control: MPLLA/MPLLB clock enable, output enable, reset, calibration, divider, standby, charge-pump, RTUNE, bandgap, and PMIX fields affect CR1 shared analog state. These controls can influence more than one lane when the lane consumes shared PLL or bias resources.
- Lane request and power sequencing: TX/RX `REQ`, `ACK`, `PSTATE`, power-up timing, reset, disable, high-Z, termination, serializer, output enable, CDR, and clock-ready fields model PHY bring-up, idle, rate changes, and power-down transitions.
- Override ownership: many fields pair a value bitfield with `*_OVRD_EN`, `*_OVRD_VAL`, or an `OVRD_SEL` field. Consumer code must explicitly decide when software takes control from normal ASIC or firmware-owned hardware paths and when it restores normal ownership.
- RX calibration and adaptation: VCO calibration request/mode/status, CDR controls, DPLL frequency bounds, adaptation `START_ASM1`, `ASM1_DONE`, ATT/VGA/CTLE/DFE status codes, VDAC offsets, slicer controls, and adaptation reset expose hardware calibration progress and results.
- Diagnostic measurement: LBERT, RX statistic matchers/counters, OCLA, ATB, DCC DAC, term-code, and analog status fields provide bring-up and validation hooks for link quality and analog behavior.

No software persistence is implemented in this header. Hardware register contents persist or reset according to ASIC power, reset, clock, and firmware ownership domains. Fields named `STATUS`, `STAT`, `ACK`, `DONE`, `RESULT`, `VALID`, `ERR`, `CNT`, and `CODE` are status or readback oriented by naming; fields named `OVRD`, `RESET`, `PSTATE`, `DAC`, `DCC`, `TERM`, `EN`, and `SEL` are control oriented. The macros do not enforce access direction or sequencing.

## Dependencies And Integration Points

The direct syntactic dependency is only the C preprocessor. The practical dependency is the matching DPCS 4.2.2 offset header, because these macros identify bitfields while `dpcs_4_2_2_offset.h` identifies register addresses such as CR1 supervisor analog registers at offsets `0x008c`-`0x0096`, lane 0 registers beginning at `0x1000`, and lane 1 registers beginning at `0x1100`.

AMDGPU DCN 3.1.5 display resource construction includes both `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`. In `dcn315_resource.c`, DPCS base segments are defined, `DPCS_DCN31_REG_LIST(id)` contributes DPCS registers to link encoder register lists, and `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`/`DPCS_DCN31_MASK_SH_LIST(_MASK)` contribute these shift and mask values to the `dcn10_link_enc_shift` and `dcn10_link_enc_mask` tables. The macros in this chunk therefore integrate with the display link encoder, PHY programming, and link diagnostics paths for DCN 3.1.5-era hardware.

Other integration points visible from naming are DisplayPort/HDMI link training and mode set paths (`RATE`, `WIDTH`, `PSTATE`, `HDMIMODE`, cursor/pre/post EQ, data enable, DETRX, MPLL fields), suspend/resume and hotplug recovery paths (power states, reset, clock ready, signal detect), and hardware diagnostic paths (RX statistics, LBERT, CDR/DPLL/VCO/adaptation status, DCC/ATB/OCLA/RTUNE-style controls).

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently write or read an adjacent hardware bit during register helper operations, causing display link failures without compile-time errors.
- This chunk begins at line 26286 inside `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_2`; the register comment is just before the chunk. It ends at line 28636 inside `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1`; later shifts and masks are outside this chunk. Per-chunk validators must account for these boundary effects.
- Field names can contain `MSK` or `MASK` as semantic field text, for example RX statistic data-mask fields. Counting masks by substring can overcount; generated-data checks should match the macro suffix pattern.
- Lane 0 and lane 1 blocks are structurally similar but not identical. Lane prefix, RX/TX direction, field width, or mask-copy mistakes can affect one lane while nearby lanes still work.
- Override-enable fields are adjacent to value fields. Accidentally enabling an override can seize normal hardware control; failing to enable one can make a programmed value ineffective.
- Supervisor analog and PLL fields can have shared-resource effects. MPLL, RTUNE, bandgap/reference regulator, PMIX, reset, and calibration writes can destabilize multiple lanes if ownership and sequencing are wrong.
- Reserved fields are explicitly mapped. Consumer code should preserve reserved bits during read-modify-write unless the hardware specification requires a defined write value.
- Status/readback and writable controls are intermixed in one generated namespace. Consumers cannot infer safe writeability from the existence of a mask macro alone.

## Test Signals

Useful validation is mostly build-time, generated-data, and hardware-integration oriented:

- Preprocess or compile AMDGPU display code that includes `dpcs_4_2_2_sh_mask.h`, especially the DCN 3.1.5 resource path that builds DPCS link encoder register, shift, and mask tables.
- Validate this chunk against the authoritative DPCS 4.2.2 register database and `dpcs_4_2_2_offset.h`, accounting for the partial first and last register groups.
- Check that complete register groups in the range have matching shift and mask definitions for each field, while `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1` is intentionally incomplete in this chunk.
- Compare repeated CR1 lane 0/lane 1 families and neighboring generated variants such as `dpcs_4_2_0_sh_mask.h`, `dpcs_4_2_3_sh_mask.h`, and `dcn_4_1_0_sh_mask.h` where the hardware database expects stable layouts.
- Runtime display tests on DPCS 4.2.2/DCN 3.1.5 hardware: DisplayPort and HDMI link training, rate/width changes, hotplug, suspend/resume, lane power transitions, and multi-lane operation that exercises CR1 lane 0 and lane 1 separately.
- PHY diagnostic tests that read back TX ACK/clock-ready, RX adaptation done/status codes, VCO/CDR/DPLL status, DFE tap values, RX statistic counters, LBERT error paths, analog status, DCC DAC ack, and signal-detect/detect-RX results.
- Recovery tests around override fields: enable overrides only in controlled debug or bring-up paths, restore normal ASIC ownership, and confirm stale overrides do not survive link reconfiguration or power transitions.

## Chunk Notes For Merge

This document intentionally covers only lines 26286-28636 of `dpcs_4_2_2_sh_mask.h`. The later per-file merge should describe the full header as a generated DPCS 4.2.2 register bitfield map used by AMDGPU display code, not handwritten driver logic. Adjacent chunks are needed for the preceding MPLLA override fields and the remaining lane 1 RX statistic definitions after `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1__STAT_CLK_EN__SHIFT`.
