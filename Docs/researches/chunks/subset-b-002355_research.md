# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 42956-45339

## Scope

This chunk covers lines 42956-45339 of the generated AMD DPCS 4.2.2 shift/mask header. It contains register bitfield definitions only: 1,065 `__SHIFT` macros and 1,083 `_MASK` macros across 254 register/comment groups in a 2,384-line slice. The shift/mask count is intentionally uneven at this boundary because the chunk starts in the middle of `DPCSSYS_CR1_LANEX_DIG_ANA_RX_VCO_OVRD_OUT_2` mask definitions and ends after the first `DPCSSYS_CR2_SUP_ANA_MPLLA_ATB1__meas_iv_wrap__SHIFT` line, before that register group's remaining shifts and masks.

The covered content spans the tail of the `DPCSSYS_CR1` generic lane (`LANEX`) analog and raw-lane control definitions, then begins the `addressBlock: dpcssys_cr2_rdpcstxcrind` section and defines the first part of the `DPCSSYS_CR2` supervisor digital/analog PLL support mask surface. It is declarative C preprocessor data; there are no functions, structs, enums, storage objects, branches, locks, or direct register accesses in this chunk.

## Purpose

`dpcs_4_2_2_sh_mask.h` gives AMDGPU display code symbolic bit positions and masks for indexed DPCS 4.2.2 registers. This chunk defines how callers compose or decode fields for:

- CR1 generic-lane receive analog controls, calibration controls, signal-detect controls, transmit analog controls, and analog measurement/test hooks.
- CR1 raw PCS/PMA/FSM/IRQ/TX/RX lane controls used around lane state machines, interrupt signaling, crossbar/PHY interfaces, ATE paths, and adaptation status.
- CR2 supervisor common digital controls for reference clocks, MPLLA/MPLLB overrides, spread-spectrum parameters, charge-pump values, power/reset state, level controls, and ASIC-facing values.
- CR2 supervisor analog controls for prescaler, RTUNE, bandgap/reference selection, power measurement switching, and initial MPLLA analog override/test fields.

The macros are intended to be used with the matching `dpcs_4_2_2_offset.h` register-offset macros. For example, this chunk's `DPCSSYS_CR1_LANEX_DIG_ANA_RX_CAL__*` fields pair with `ixDPCSSYS_CR1_LANEX_DIG_ANA_RX_CAL`, and `DPCSSYS_CR2_SUP_DIG_MPLLA_OVRD_IN_0__*` pairs with `ixDPCSSYS_CR2_SUP_DIG_MPLLA_OVRD_IN_0`.

## Exported API Surface

The only API exported by this chunk is preprocessor constants. Every complete register group has a family of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. There are no callable APIs.

Important CR1 LANEX analog groups include:

- RX calibration and DAC controls: `DPCSSYS_CR1_LANEX_DIG_ANA_RX_CAL`, `RX_DAC_CTRL`, `RX_DAC_CTRL_OVRD`, `RX_DAC_CTRL_SEL`, `RX_ANA_CAL_DAC_CTRL_EN`, and `RX_ANA_SIGNALS_CHANGES_ENABLE`.
- RX front-end and sampling controls: `RX_AFE_ATT_VGA`, `RX_AFE_CTLE`, `RX_SCOPE`, `RX_SLICER_CTRL`, `RX_ANA_IQ_PHASE_ADJUST`, `RX_ANA_IQ_SENSE_EN`, and `RX_ANA_PHASE_ADJUST_CLK`.
- RX status and termination controls: `DPCSSYS_CR1_LANEX_DIG_ANA_STATUS_0`, `STATUS_1`, `RX_TERM_CODE_OVRD_OUT`, and `RX_TERM_CODE_CLK_OVRD_OUT`.
- MPHY/signal-detect controls: `MPHY_OVRD_OUT`, `SIGDET_OVRD_OUT_1`, and `SIGDET_OVRD_OUT_2`.
- TX DCC/equalization/power/measurement controls: `TX_DCC_DAC_OVRD_OUT`, `TX_DCC_DAC_OVRD_OUT_2`, `TX_OVRD_OUT_2`, `ANA_TX_OVRD_MEAS`, `ANA_TX_PWR_OVRD`, `ANA_TX_ALT_BUS`, `ANA_TX_ATB1`, `ANA_TX_ATB2`, `ANA_TX_DCC_DAC`, `ANA_TX_DCC_CTRL1`, `ANA_TX_TERM_CODE`, `ANA_TX_TERM_CODE_CTRL`, `ANA_TX_OVRD_CLK`, `ANA_TX_MISC1`, `MISC2`, `MISC3`, and reserved TX analog registers.
- RX analog raw controls: `ANA_RX_CLK_1`, `ANA_RX_CLK_2`, `ANA_RX_CDR_DES`, `ANA_RX_SLC_CTRL`, `ANA_RX_PWR_CTRL1`, `ANA_RX_PWR_CTRL2`, `ANA_RX_SQ`, `ANA_RX_CAL1`, `ANA_RX_CAL2`, `ANA_RX_ATB_REGREF`, `ANA_RX_ATB_MEAS1` through `MEAS4`, `ANA_RX_ATB_FRC`, and `ANA_RX_RESERVED1`.

Important CR1 raw-lane digital groups include:

- PCS crossbar interfaces: `RAWLANEX_DIG_PCS_XF_TX_OVRD_IN`, `TX_OVRD_IN_1`, `TX_PCS_IN`, `TX_OVRD_OUT`, `TX_PCS_OUT`, `RX_OVRD_IN`, `RX_OVRD_IN_1` through `RX_OVRD_IN_3`, `RX_PCS_IN` through `RX_PCS_IN_4`, `RX_OVRD_OUT`, and `RX_PCS_OUT`.
- Adaptation and directed-control status: `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, `RX_TXPOST_DIR`, `LANE_NUMBER`, `ATE_OVRD_IN`, `RX_EQ_DELTA_IQ_OVRD_IN`, `TXRX_TERM_CTRL_OVRD_IN`, `TXRX_TERM_CTRL_IN`, `RX_OVRD_OUT_1`, `RX_EQ_OVRD_IN_1`, `RX_EQ_OVRD_IN_2`, and `RX_PH2_CAL`.
- Lane FSM programming/status: `FSM_FSM_OVRD_CTL`, `FSM_MEM_ADDR_MON`, `FSM_STATUS_MON`, many `FSM_FAST_*` calibration/adaptation step registers, `FSM_CMNCAL_MPLL_STATUS`, `FSM_FAST_FLAGS`, `FSM_CR_LOCK`, `FSM_TX_DCC_FLAGS`, `FSM_TX_DCC_STATUS`, `FSM_OCLA`, `FSM_TX_EQ_UPDATE_FLAG`, `FSM_CMNCAL_RCAL_STATUS`, and `FSM_RX_IQ_PHASE_OFFSET`.
- IRQ status/clear/mask controls: reset, request, rate, p-state, adaptation request/disable, phase-2 calibration, loopback, DCC-on-demand, TX reset/request, corresponding clear registers, `IRQ_MASK`, and `IRQ_MASK_2`.
- PMA crossbar and TX/RX controller controls: `PMA_XF_LANE_OVRD_IN`, `PMA_XF_LANE_OVRD_OUT`, `PMA_XF_SUP_OVRD_IN`, `PMA_XF_SUP_PMA_IN`, `PMA_XF_TX_OVRD_OUT`, `PMA_XF_TX_PMA_IN`, `PMA_XF_RX_OVRD_OUT`, `PMA_XF_RX_PMA_IN`, `PMA_XF_LANE_RTUNE_CTL`, `PMA_XF_MPHY_OVRD_IN`, `PMA_XF_MPHY_OVRD_OUT`, `PMA_XF_RX_ADAPT_OVRD_OUT`, `TX_CTL_*`, and `RX_CTL_*`.
- ATE and secondary PCS views: `PCS_XF_ATE_RX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN_1`, `PCS_XF_MASTER_MPLL_LOOP`, `PCS_XF_ATE_RX_OVRD_IN_1` through `IN_3`, `PCS_XF_RX_OVRD_OUT_2`, and `PCS_XF_TX_OVRD_IN_2`.

Important CR2 supervisor groups include:

- Identification and clocks: `SUP_DIG_IDCODE_LO`, `SUP_DIG_IDCODE_HI`, `SUP_DIG_REFCLK_OVRD_IN`, `MPLLA_DIV_CLK_OVRD_IN`, `MPLLA_HDMI_CLK_OVRD_IN`, `MPLLB_DIV_CLK_OVRD_IN`, and `MPLLB_HDMI_CLK_OVRD_IN`.
- MPLL override/programming: `MPLLA_OVRD_IN_0` through `MPLLA_OVRD_IN_5`, `MPLLA_SSC_PEAK_1`, `MPLLA_SSC_PEAK_2`, `MPLLA_SSC_STEPSIZE_1`, `MPLLA_SSC_STEPSIZE_2`, `MPLLA_CP_OVRD_IN`, `MPLLA_CP_GS_OVRD_IN`, and parallel `MPLLB_*` groups.
- Supervisor overrides and ASIC inputs: `SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, `LVL_OVRD_IN`, `DEBUG`, `MPLLA_ASIC_IN_0` through `MPLLA_ASIC_IN_6`, `MPLLB_ASIC_IN_0` through `MPLLB_ASIC_IN_6`, DIV/HDMI clock ASIC inputs, `ASIC_IN`, `LVL_ASIC_IN`, `BANDGAP_ASIC_IN`, and MPLL charge-pump ASIC input groups.
- Supervisor analog controls: `SUP_ANA_PRESCALER_CTRL`, `SUP_ANA_RTUNE_CTRL`, `SUP_ANA_BG1`, `SUP_ANA_BG2`, `SUP_ANA_SWITCH_PWR_MEAS`, `SUP_ANA_BG3`, `SUP_ANA_MPLLA_MISC1`, `SUP_ANA_MPLLA_MISC2`, `SUP_ANA_MPLLA_OVRD`, and the first line of `SUP_ANA_MPLLA_ATB1`.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior is created by AMD display code that includes this header, uses the matching offset header to select a register, and then applies these masks and shifts through register read/modify/write helpers.

The names in this chunk imply several hardware state machines and sequencing requirements:

- RX analog bring-up and calibration: AFE attenuation/VGA, CTLE boost, slicer control, IQ phase adjust, calibration MUX/DAC, scope capture, signal-detect thresholds, and VCO counter/status fields are typically programmed and then observed during receiver enablement or diagnostics.
- TX analog/DCC sequencing: TX DCC DAC, term-code, power override, equalization/measurement, and clock override fields expose low-level transmitter tuning surfaces that must align with link-rate and lane-power transitions.
- PCS/PMA lane handshakes: raw PCS/PMA override/input/output fields represent the boundary between digital control logic and PHY analog state. Request/ack, p-state, rate, loopback, and lane mode fields should be treated as ordered hardware handshakes, not plain memory bits.
- FSM control and observation: `FSM_FAST_*`, `FSM_STATUS_MON`, common calibration status, lock bits, DCC flags/status, OCLA, and TX EQ update flags represent calibration/adaptation state-machine checkpoints.
- Interrupt management: IRQ status, clear, and mask fields expose lane reset/request/rate/p-state/adaptation/phase-calibration/TX events. Consumers must distinguish status bits from write-one-clear or mask bits.
- MPLLA/MPLLB programming: CR2 fields configure reference clocks, divider clocks, HDMI clocks, SSC peak/step size, fractional-N enable, charge pump settings, standby/reset/calibration controls, and ASIC input mirrors. These values influence link-clock generation and must be programmed in a hardware-defined order.
- Analog supervisor support: prescaler, RTUNE, bandgap/reference, power-measurement switch, and analog PLL override fields affect common PHY support circuits shared by lanes.

There is no software persistence in this file. The macros persist only as compiled constants. Hardware state persists according to DPCS power, reset, and clock domains, and higher-level driver code must restore or reprogram those registers across GPU reset, display suspend/resume, link retraining, and hotplug paths.

## Dependencies And Integration Points

Direct dependencies are limited to the C preprocessor and the include guard defined near the top of the file. This chunk is part of the generated DPCS 4.2.2 register-description pair:

- `dpcs_4_2_2_offset.h` supplies `ixDPCSSYS_*` register offsets.
- `dpcs_4_2_2_sh_mask.h` supplies the field shifts and masks documented here.

The visible source-tree integration point is `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes both DPCS 4.2.2 headers and defines the `DPCS_BASE__INST0_SEG*` base segments. That resource file also expands DPCS register and mask/shift list macros for the DCN 3.1.5 resource table layer, so these generated constants feed the AMD display register table infrastructure rather than standalone code in this header.

Functional integration areas include:

- AMDGPU DCN display resource initialization for ASICs using DPCS 4.2.2.
- DisplayPort/HDMI PHY link-clock and lane bring-up code using CR indexed register access.
- Link training, lane adaptation, signal-integrity tuning, receiver calibration, and TX DCC/equalization routines.
- IRQ handling or diagnostics that inspect and clear raw lane events.
- Firmware, ATE, OCLA, and analog-test paths using raw PCS/PMA/FSM/ATB register views.

## Risks And Edge Cases

- Generated-register drift is the dominant risk. Incorrect masks or shifts can corrupt adjacent analog/PLL fields and cause link training failures, unstable clocks, or PHY calibration timeouts.
- This chunk is cut at non-register boundaries. Automated per-chunk counts must account for incomplete `RX_VCO_OVRD_OUT_2` and `MPLLA_ATB1` field pairs; a simple one-to-one shift/mask check inside only this range will report a false mismatch.
- Many field names expose overrides, raw views, ATE controls, OCLA hooks, or reserved bits. Those fields are sensitive and may only be valid in firmware-defined sequences, lab diagnostics, or ASIC bring-up flows.
- Status, clear, mask, request, acknowledge, enable, and override bits are adjacent in several families. Treating every macro as a plain writable configuration bit can accidentally clear events, mask interrupts, or fight hardware state machines.
- CR1 `LANEX` and `RAWLANEX` names are generic lane aliases. Callers must select the correct indexed lane/register aperture and cannot infer a fixed physical lane solely from the macro name.
- CR2 supervisor fields affect common PLL/support circuitry, including both MPLLA and MPLLB. Wrong programming can break multiple lanes or display links, not just one lane.
- Some comparable fields in nearby DPCS revisions use different literal formatting or naming case. Consumers should include the exact IP-version header chosen by the resource code instead of mixing definitions from `dpcs_4_2_0`, `dpcs_4_2_3`, or DCN umbrella headers.

## Test Signals

Useful validation signals are mostly build-time, generated-header, and hardware-integration oriented:

- Compile AMDGPU display code that includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`, especially `dcn315_resource.c`.
- Regenerate DPCS 4.2.2 headers from the source register database and diff this chunk for changed field names, shifts, and masks.
- Cross-check complete register groups outside the chunk boundary to ensure every field has the expected paired shift and mask; for this exact slice, expect 1,065 shifts and 1,083 masks because of boundary cuts.
- Run display bring-up, hotplug, suspend/resume, and GPU reset recovery tests on hardware using DCN 3.1.5/DPCS 4.2.2.
- Exercise DisplayPort and HDMI link-rate changes, link training, lane disable/enable, loopback, and PHY calibration paths; failures can indicate bad PLL, AFE/CTLE, DCC, p-state, or handshake masks.
- Check IRQ paths by provoking lane reset/request/rate/p-state/adaptation events and confirming status, clear, and mask bits behave as expected.
- Use hardware register readback or debug traces during PHY bring-up to confirm VCO, MPLL, RTUNE, bandgap, FSM lock/status, DCC status, and adaptation fields transition through expected values.

## Chunk Notes For Merge

The final per-file report should treat this source as a generated ASIC bitfield map, not handwritten driver logic. This chunk is centered on CR1 generic-lane low-level PHY controls and the start of CR2 supervisor PLL/common controls. Earlier and later chunks are needed to describe the full DPCS 4.2.2 register surface, especially the complete CR1 context before `RX_VCO_OVRD_OUT_2` and the continuation of CR2 after `SUP_ANA_MPLLA_ATB1`.
