# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 187948-190430

## Scope

This chunk is a generated DCN 3.2.0 register shift/mask slice for AMD display C20 PHY register fields. It contains C preprocessor constants only: `_SHIFT` macros define bit positions and `_MASK` macros define the unshifted field masks used by AMDGPU Display Core register helper code. There are no functions, structs, enums, branches, loops, allocations, locks, or direct MMIO operations in this range.

The range starts in the middle of `C20_PHY_CR3_RAWLANEAONX_DIG_TX_MPLLB_DCC_HALF_BANK_3`; only the two mask definitions for `CM_VAL` and `DIFF_VAL` are in this chunk, while its comment and shift definitions are immediately before the start. The range ends at the first shift definition for `C20_PHY_CR4_SUP_DIG_MPLLA_MPLL_PWR_CTL_STAT`; the rest of that status register's shifts and masks continue after line 190430. Merge-time reconciliation should treat both boundary register groups as partial.

## Purpose And Hardware Surface

The header provides the bitfield layout half of the DCN 3.2.0 generated register ABI. Companion address headers identify register offsets; this `*_sh_mask.h` file lets display driver code compose writes and decode reads through register access helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and lower-level MMIO wrappers.

This chunk covers three main C20 PHY areas:

- `C20_PHY_CR3_RAWLANEAONX_DIG_TX_*` and `C20_PHY_CR3_RAWLANEAONX_DIG_RX_*`: raw-lane always-on TX/RX calibration, adaptation, DCC/IQ, override, CDR, signal-detect, and status fields for CR3.
- `C20_PHY_LANE0_PIPE3_UPCSLANE_PIPE_LPC_PHY_*` and `C20_PHY_LANE1_PIPE3_UPCSLANE_PIPE_LPC_PHY_*`: PIPE3 lane message-bus/LPC PHY fields for lane 0 and lane 1, including RX margining, RX/TX/HDP control, VDR indirect access, custom SERDES/HDMI rate, width, LFPS, VDR coefficient overrides, recalibration, and deskew controls.
- `C20_PHY_CR4_SUP_DIG_*`: CR4 supervisor digital fields for ID code, reference clock overrides, MPLLA/MPLLB dividers, HDMI mode, MPLL override/ASIC inputs, SSC/VCO programming, supervisor override input/output, ASIC input/output status, level/termination controls, MPLLB calibration, RTUNE, bandgap/reference clock-reset timing, and the start of MPLLA power-control calibration/status.

## Important Definitions

The generated naming convention is consistent across the chunk:

- `<REGISTER>__<FIELD>__SHIFT` is the least-significant bit index of `FIELD`.
- `<REGISTER>__<FIELD>_MASK` is the field mask in register position.
- `//<REGISTER>` comments group the following field definitions until the next register comment.
- `// addressBlock: ...` comments mark transitions into generated address blocks such as `c20_phy_lane0_pipe3_rdpcspipemsgbusind`, `c20_phy_lane1_pipe3_rdpcspipemsgbusind`, and `c20_phy_cr4_rdpcspipecrind`.

Important CR3 raw-lane TX/RX families:

- TX calibration completion and DCC readback: `TX_MPLLA_CAL_DONE_BANK_0..3`, `TX_MPLLB_CAL_DONE_BANK_0..3`, aggregate `TX_MPLLA_CAL_DONE`, `TX_MPLLB_CAL_DONE`, `TX_CAL_DONE`, `TX_DCC_CTRL_RANGE_CODE`, `TX_DCC_CODE`, `TX_DCC_DIFF_CODE`, `TX_DCC_CM_CODE`, `TX_CAL_BANK_SEL`, and `TX_IN_0` expose full/half-rate calibration completion, common-mode/differential DCC code readback, selected recalibration bank, and TX disable input.
- RX startup and continuous calibration controls: `RX_STARTUP_CAL_ALGO_CTL_0`, `RX_STARTUP_CAL_ALGO_CTL_1`, `RX_STARTUP_ADAPT_ALGO_CTL_0`, and `RX_CONT_ALGO_CTL` define skip bits for AFE, reference, ATT, VGA, CTLE, IQ, phase, DFE, error, bypass, VGEN, signal-detect, DCC data/phase/range, full-rate/half-rate, adaptation reload, TX increment/decrement, FOM, and margining paths.
- RX fast flags and analog trim/offsets: `RX_FAST_FLAGS`, `RX_VGEN_VDAC_OFST`, `RX_SIGDET_CAL`, `RX_AFE_RTRIM`, `RX_REF_*_VDAC_OFST`, `RX_DFE_*_VDAC_OFST`, `RX_SETUP_*_IDAC_OFST`, `RX_VDAC_RANGE_SEL`, and `RX_AFE_*_IDAC_OFST` describe fast-start controls, signal-detect calibration, AFE trim, reference/DFE VDAC offsets, setup IDAC offsets, and analog range selection.
- RX DCC/IQ calibration storage: `RX_DCC_CTRL_RANGE_BANK_0..3`, `RX_DCC_FULL_DATA/BYP/PHASE_BANK_0..3`, `RX_DCC_HALF_DATA/BYP/PHASE_BANK_0..3`, `RX_IQ_CAL_BANK_0..3`, `RX_CAL_DONE_BANK_0..3`, `RX_CAL_BANK_SEL`, `RX_DCC_*_CODE`, `RX_IQ_CAL`, `RX_CAL_DONE`, `RX_IQ_CTL_0`, `RX_IQ_CTL_1`, `RX_ADPT_IQ_LIMIT`, and `RX_ADPT_ERR_SLC_MODE` provide banked and selected DCC/IQ calibration values and done signals.
- RX adaptation readback and control: `RX_ADPT_ATT_BANK_0..1`, `RX_ADPT_VGA_BANK_0..1`, `RX_ADPT_CTLE_BANK_0..1`, `RX_ADPT_DFE_TAP1..5_BANK_0..1`, DFE tap-1 offset quadrants (`DEH`, `DEL`, `DOH`, `DOL`, `EEH`, `EEL`, `EOH`, `EOL`), `RX_DFE_TAP1_OFST_VLD_BANK_0..1`, `RX_ADPT_IQ_BANK_0..1`, `RX_ADPT_REF_ERR_BANK_0..1`, `RX_ADAPT_DONE_BANK_0..1`, and full-width `RX_ADPT_CTL_0..28` expose adaptation results and opaque hardware/firmware control words.
- RX-assisted TX equalization and receive status: `RX_TX_EQ_DIR_POLARITY_CTL`, `RX_TX_PRE_DIV`, `RX_TX_MAIN_ATT_THRESHOLD`, `RX_TX_MAIN_VGA_THRESHOLD`, `RX_TX_POST_BOOST_THRESHOLD`, `RX_TX_POST_TAP1_THRESHOLD`, `RX_IQ_MARGIN_RANGE`, `RX_CDR_DETECTOR_CTL`, `RX_CDR_RECOVERY_TIME`, `RX_OVRD_IN_0`, `RX_SIGDET_EN_MASK_CTL`, `RX_SIGDET_FILT_CTL`, `RX_OVRD_OUT_0`, `RX_PMA_OVRD_OUT_0`, `RX_IN_0`, and `RX_OUT_0` define adaptation-driven TX coefficient steering, IQ margin range, CDR mode/timing, RX override enables/values, signal-detect filter/hold timing, PMA override status, and signal-detect/RX state readback.

Important PIPE3 lane message-bus families:

- `RX_MARGIN_CONTROL0/1` expose receiver margining controls such as margin enable, clear, sample count, software delay, request/error controls, and margining state.
- `RX_CONTROL0/1/3/4` define RX reset, width, polarity, term enable, equalization training, PMA power state, adaptation request, and low-power state fields.
- `TX_CONTROL2..8` and `HDP_TX_CONTROL2..8` define TX coefficient, post/pre/main level, de-emphasis, polarity, reset, width, state, and HPD-specific TX control fields.
- `COMMON_CONTROL0` and VDR access registers (`C20_VDR_WR_ADDRESS_*`, `C20_VDR_WR_DATA_*`, `C20_VDR_RD_ADDRESS_*`, `C20_VDR_RD_DATA_*`) provide common lane controls and indirect vendor-defined register access.
- `C20_VDR_CUSTOM_SERDES_RATE`, `C20_VDR_HDMI_RATE`, `VDR_CUSTOM_WIDTH`, `C20_VDR_LFPS_CTRL`, `VDR_OVRD`, `VDR_PRE/MAIN/POST_OVRD`, `VDR_PRE/MAIN/POST_OVRD_2`, and `HDP_VDR_*_OVRD` define custom protocol/rate/width handling and TX coefficient override controls.
- `C20_VDR_RECAL_BANK_SEL`, `C20_VDR_RECAL_FORCE_EN`, `C20_VDR_RECAL_SKIP_EN`, `C20_VDR_DESKEW_EN`, and `C20_VDR_RECAL_OVRD` provide lane recalibration-bank selection, per-calibration force/skip controls, deskew enable, and recalibration override bits.

Important CR4 supervisor families:

- Identification and reference clock: `IDCODE_LO`, `IDCODE_HI`, `REFCLK_OVRD_IN_0`, and `REFCLK_OVRD_IN_1` define ID readback and reference-clock override enables/values for clock source, reference range/multiply/divide, PLL reference clock routing, and related clock gating.
- PLL, HDMI, SSC, and VCO override/ASIC inputs: `MPLLA_DIV_CLK_OVRD_IN`, `MPLLB_DIV_CLK_OVRD_IN`, `HDMI_OVRD_IN`, `MPLLA_OVRD_IN_0/1`, `MPLLA_BW_*_OVRD_IN`, `MPLLA_SSC_OVRD_IN_0..6`, `MPLLB_OVRD_IN_0/1`, `MPLLB_VCO_OVRD_IN_0..2`, `MPLLB_SSC_OVRD_IN_0..6`, and matching `*_ASIC_IN_*` definitions expose the paired override values and native ASIC-provided values for PLL/SSC/VCO/HDMI configuration.
- Supervisor input/output and analog level controls: `SUP_OVRD_IN_0..2`, `SUP_OVRD_OUT`, `LVL_OVRD_IN`, `ASIC_IN_0/1`, `ASIC_OUT_0`, `LVL_ASIC_IN`, `SUP_OVRD_MISC`, `TXUP_TERM_OFFSET_ASIC_IN`, and `TXDN_TERM_OFFSET_ASIC_IN` define supervisor override values/enables, observed output state, RX/TX analog levels, reference-clock detect, power/reset, lane mode, and termination offsets.
- MPLLB calibration and RTUNE: `MPLLB_CAL_OVRD_IN`, `MPLLB_CAL_ASIC_IN`, `RTUNE_CONFIG`, `RTUNE_STAT`, `RTUNE_RX_SET_VAL`, `RTUNE_TXDN_SET_VAL`, `RTUNE_TXUP_SET_VAL`, `RTUNE_RX_STAT`, `RTUNE_TXDN_STAT`, `RTUNE_TXUP_STAT`, `RTUNE_TX_TERM_CODE_0/1`, and `RTUNE_FAST_FLAGS` define calibration force/standby/DAC code overrides, RX/TX termination calibration enables, RTUNE state/status, set values, measured values, averaged/up-down TX termination code, and fast-RTUNE control.
- Clock/reset and MPLLA power-control timing: `CLK_RST_BG_PWRUP_TIME_0..2`, `CLK_RST_REF_PWRUP_TIME_0`, `CLK_RST_BG_STATE_STATUS`, `MPLLA_MPLL_PWR_CTL_CAL_CTRL_0`, `MPLLA_MPLL_PWR_CTL_CAL_CTRL_1`, and the partial `MPLLA_MPLL_PWR_CTL_STAT` define bandgap/reference power-up timing, fast wait/retrigger controls, state readback, external MPLL calibration controls, fast MPLL power/lock fields, debug/test-bus selection, and the first status bit for the MPLLA power-control FSM.

## Control Flow And State Behavior

This header has no executable control flow. Runtime behavior is created by code that combines these constants with register offsets and register access helpers.

Typical flows using this chunk are:

1. Link bring-up or retraining code chooses CR3 TX/RX startup and continuous calibration policy by programming skip bits, fast flags, override enables, and bank selection fields.
2. TX calibration code reads MPLLA/MPLLB per-bank and aggregate done bits, decodes full-rate/half-rate common-mode and differential DCC codes, and selects recalibration banks.
3. RX calibration and adaptation code reads DCC/IQ calibration banks, done bits, adaptation banks, DFE tap values, offset validity, reference error, and CDR/signal-detect status, then may tune full-width `RX_ADPT_CTL_*` words or IQ limits.
4. PIPE3 lane control code configures lane 0 and lane 1 RX/TX state, reset, polarity, widths, equalization training, HPD TX controls, margining, VDR indirect access, custom rate/width modes, TX coefficient overrides, recalibration force/skip, deskew, and LFPS controls.
5. Supervisor and PHY power code programs or observes CR4 reference-clock, PLL, SSC, VCO, HDMI, supervisor override, level, termination, RTUNE, bandgap/reference timing, and MPLL power-control state.

The state represented here is hardware register state:

- Persistent programmed state includes algorithm skip bits, fast flags, override values/enables, RX/TX disable and termination controls, CDR and signal-detect settings, adaptation control words, TX equalization thresholds, VDR indirect access and override values, recalibration force/skip/deskew controls, CR4 PLL/SSC/VCO/HDMI override values, RTUNE set/config values, and clock/reset timing controls.
- Volatile readback includes calibration done bits, DCC/IQ codes, RX adaptation bank values, DFE offset validity, CDR/signal-detect outputs, RX/PMA override outputs, PIPE3 margining state, VDR read data, supervisor output state, ASIC input/output state, RTUNE measurements/state, bandgap/reference FSM states, and MPLL power-control status.
- Sequencing-sensitive fields include calibration skip/force bits, recalibration-bank selection, CDR disable-in-adaptation, signal-detect hold/filter timing, RX/TX reset and power-state controls, VDR indirect register access address/data pairs, PLL override enables, RTUNE enable/fast flags, clock/reset timing fields, and MPLL external calibration done/tune fields.

## Dependencies And Integration Points

The definitions depend on exact numeric agreement with the DCN 3.2.0 C20 PHY hardware specification and with the matching generated register offset headers. A missing macro normally fails compilation; a wrong shift or mask can compile cleanly and misprogram hardware.

Primary integration points are:

- AMDGPU Display Core link encoder and PHY code that programs C20 PHY lanes for DisplayPort/HDMI bring-up, retraining, suspend/resume, power transitions, hotplug, and lane disable paths.
- DisplayPort link training and receiver adaptation code that interprets CR3 RX adaptation results, DFE taps, IQ/ref-error values, CDR status, signal-detect status, and TX coefficient steering thresholds.
- PHY calibration code that handles TX MPLLA/MPLLB DCC calibration, RX DCC/IQ calibration, calibration-done polling, recalibration-bank selection, and VDR recalibration force/skip controls.
- PIPE3 message-bus access code and debug/lab tooling that use lane 0/lane 1 VDR indirect access, margining controls, custom SERDES/HDMI rates, TX coefficient overrides, deskew, and LFPS fields.
- Supervisor power/clock code that configures or diagnoses CR4 reference clock, PLL dividers, MPLLA/MPLLB override versus ASIC inputs, SSC/VCO settings, HDMI mode, RTUNE, bandgap/reference clock-reset timing, and MPLL power-control state.

## Risks And Maintenance Notes

- This file is generated hardware ABI. Manual edits to shifts or masks are high risk because register helpers will still compile while writing or decoding the wrong bits.
- Repeated families invite copy/paste drift: bank 0-3, MPLLA/MPLLB, lane 0/lane 1 PIPE3, VDR pre/main/post, HDP versus non-HDP controls, SSC override versus ASIC input, and CR3 versus neighboring CR lanes must remain numerically consistent with the source register spec.
- Dense 16-bit register packing means reserved masks, one-bit override enables, and adjacent multi-bit values can overlap if a mask is wrong. Such defects often appear only on certain links, rates, PHY lanes, boards, or resume/retrain paths.
- Opaque full-width fields such as `RX_ADPT_CTL_0..28` and VDR indirect register payloads cannot be understood from this header alone. Their meaning belongs to the hardware/firmware contract, so test coverage must focus on observed behavior and spec consistency.
- Calibration skip/fast/force fields are sequencing-sensitive. Bad masks can silently skip required training, force stale calibration data, or assert deskew/recalibration at the wrong time, causing intermittent link failures, black screens, flicker, or marginal signal integrity.
- Boundary completeness matters. The chunk starts after the `TX_MPLLB_DCC_HALF_BANK_3` shifts and ends before the full `MPLLA_MPLL_PWR_CTL_STAT` field/mask set; final file-level documentation should merge adjacent chunks before claiming complete coverage of either register.

## Test Signals

Useful validation signals include:

- Build AMDGPU Display Core with DCN 3.2 enabled and confirm all in-scope `C20_PHY_CR3_RAWLANEAONX`, `C20_PHY_LANE0_PIPE3`, `C20_PHY_LANE1_PIPE3`, and `C20_PHY_CR4_SUP_DIG` macros resolve with the matching address headers.
- Run generated-register consistency checks: each complete register in this range should have paired `_SHIFT` and `_MASK` definitions, masks should fit within 16-bit register width, fields should not overlap unless documented, and repeated lane/bank/MPLL families should match the authoritative register spec.
- Compare numeric shifts and masks against the DCN 3.2.0 C20 PHY register source, prioritizing calibration done bits, DCC/IQ banks, RX adaptation/DFE fields, CDR/signal-detect fields, PIPE3 lane controls, VDR access and recalibration fields, CR4 PLL/SSC/VCO overrides, RTUNE, clock/reset timing, and boundary registers.
- Exercise DisplayPort and HDMI link bring-up, retraining, hotplug, link-loss recovery, suspend/resume, and high-bandwidth modes on hardware that uses these C20 PHY lanes; monitor link-training failures, flicker, black screens, repeated PHY resets, and unexpected HPD or signal-detect transitions.
- Capture register dumps before and after training, recalibration, power-down, resume, and link-rate changes; decode CR3 TX/RX calibration/adaptation fields, PIPE3 VDR/recalibration fields, and CR4 supervisor/RTUNE/PLL fields through these masks to confirm coherent state transitions.
- Validate RX margining and VDR indirect access on lane 0 and lane 1 where supported, including read/write address/data sequencing and expected margining state/error reporting.
- Validate RTUNE and supervisor clock/reset behavior by checking programmed RTUNE set values against status readbacks, bandgap/reference FSM states, and MPLLA/MPLLB power/calibration status during normal and fast-path power-up flows.

## Chunk-Specific Summary

Lines 187948-190430 define generated bitfield masks and shifts for the tail of CR3 TX DCC calibration state, the bulk of CR3 RX calibration/adaptation/control/status state, PIPE3 lane 0 and lane 1 LPC PHY/message-bus controls, and the beginning of CR4 supervisor digital PLL/clock/RTUNE/power-control state. The content is data-only register ABI. Correctness depends on exact generated values, repeated-family consistency, careful treatment of partial boundary registers, and hardware validation through link training, calibration, VDR access, RTUNE, and suspend/resume flows.
