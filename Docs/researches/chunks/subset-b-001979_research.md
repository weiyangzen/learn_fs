# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 122339-124776

## Purpose

This chunk is generated AMD DCN 3.2.0 register bitfield metadata for C20 PHY register blocks. It contains C preprocessor constants only: each hardware register field is represented as a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro. Runtime display-driver code combines these definitions with the matching `dcn_3_2_0_offset.h` register-address macros and AMDGPU DC register helpers to read, update, and decode individual MMIO or indirect-message-bus fields.

The range starts in the middle of `C20_PHY_CR1_RAWLANEAONX_DIG_RX_ADAPT_DONE_BANK_1`, then finishes the CR1 raw-lane receiver/adaptation control cluster. It then covers the `c20_phy_lane0_pipe1_rdpcspipemsgbusind` and `c20_phy_lane1_pipe1_rdpcspipemsgbusind` address blocks for lane-local PIPE1/LPC PHY controls, followed by the start and most of the `c20_phy_cr2_rdpcspipecrind` supervisor/PLL/analog-control block. The chunk ends in the middle of `C20_PHY_CR2_SUP_DIG_ANA_XF_MPLLB_ANA_CREG05`, so the final merged file research must reconcile the continuation in the next chunk.

## Major Register Areas

The opening CR1 receiver section describes digital RX adaptation, equalization, signal-detect, CDR, and override fields for a raw-lane always-on block:

- `C20_PHY_CR1_RAWLANEAONX_DIG_RX_TX_EQ_DIR_POLARITY_CTL`, `RX_TX_PRE_DIV`, and TX-main/post threshold registers define polarity inversion and adaptation threshold parameters used by RX-driven TX equalization decisions.
- `C20_PHY_CR1_RAWLANEAONX_DIG_RX_ADPT_CTL_0` through `_28` are full 16-bit `VAL` fields, indicating a dense bank of adaptation-control words where the bit semantics are opaque to this generated header.
- `RX_IQ_MARGIN_RANGE`, `RX_CDR_DETECTOR_CTL`, and `RX_CDR_RECOVERY_TIME` describe margin range, CDR detector enable/PPM monitor/disable-in-adaptation bits, and recovery timing.
- `RX_OVRD_IN_0`, `RX_OVRD_OUT_0`, `RX_PMA_OVRD_OUT_0`, `RX_IN_0`, and `RX_OUT_0` map override-value/override-enable pairs and live input/output fields for RX disable, termination, AC/DC termination, low/high-frequency signal detect, HF filter disable, VREF generation, and PMA termination/VREF controls.
- `RX_SIGDET_EN_MASK_CTL` and `RX_SIGDET_FILT_CTL` provide signal-detect mask/filter counters and hold behavior.

The lane0 and lane1 PIPE1 LPC PHY sections are structurally repeated. Each lane block exposes 8-bit fields rather than the 16-bit CR1/CR2 style, and covers:

- RX margining controls: `RX_MARGIN_CONTROL0` starts/stops margining, chooses voltage versus timing margining, resets error/sample counts, and enables destructive margining; `RX_MARGIN_CONTROL1` supplies margin offset and direction.
- RX datapath controls: elastic-buffer depth and mode, RX polarity, RX equalization training, IO recalibration, RX EQ valid/in-progress status, invalid request status, block alignment, and elastic-buffer reset.
- TX controls: de-emphasis split across `TX_CONTROL2` through `TX_CONTROL4`, preset coefficient request, full-swing (`FS`) and low-frequency (`LF`) values, TX margin/swing, and `DISABLE_SINGLE_TX`.
- HDP TX controls mirror the normal TX controls with `HDP_TX_CONTROL2` through `HDP_TX_CONTROL8`.
- Common and vendor-defined register access controls: `COMMON_CONTROL0`, VDR write/read address and data low/high halves, custom SERDES rate, HDMI rate, custom width, LFPS control, global VDR override, pre/main/post override coefficients, HDP VDR override coefficients, and recalibration/deskw controls.

The CR2 supervisor block begins with identity and clock/PLL override input registers:

- `IDCODE_LO` and `IDCODE_HI` expose low/high identity words.
- `REFCLK_OVRD_IN_*`, `MPLLA_DIV_CLK_OVRD_IN`, `MPLLB_DIV_CLK_OVRD_IN`, and `HDMI_OVRD_IN` define override values and enable bits for reference clocks, divided PLL clocks, HDMI clocking, FB clock, ref-range, TxAck selection, and pixel-clock selection.
- `MPLLA_OVRD_IN_*`, `MPLLA_BW_*_OVRD_IN`, and `MPLLA_SSC_OVRD_IN_0` through `_6` expose MPLLA multiplier, bandwidth, fractional/spread-spectrum, and modulation controls with override enable bits.
- `MPLLB_OVRD_IN_*`, `MPLLB_VCO_OVRD_IN_*`, and `MPLLB_SSC_OVRD_IN_0` through `_6` provide the corresponding MPLLB/UPLL multiplier, VCO, and spread-spectrum controls.
- `SUP_OVRD_IN_*`, `LVL_OVRD_IN`, and related ASIC-in/ASIC-out mirrors map supervisor-level overrides, calibration request/ack, power-down, lane sync, bandgap/refclk/VREF/flyover controls, level-conversion controls, and async reset behavior.

The CR2 tuning and power-management section covers termination tuning and PLL power finite-state-machine metadata:

- `RTUNE_CONFIG`, `RTUNE_STAT`, `RTUNE_*_SET_VAL`, `RTUNE_*_STAT`, `RTUNE_TX_TERM_CODE_*`, and `RTUNE_FAST_FLAGS` describe RX/TXUP/TXDN tuning references, compare/result flags, override values, set values, status values, and fast calibration flags.
- `CLK_RST_BG_PWRUP_TIME_*`, `CLK_RST_REF_PWRUP_TIME_0`, and `CLK_RST_BG_STATE_STATUS` define bandgap/reference-clock power-up timing and state/status fields.
- `MPLLA_MPLL_PWR_CTL_CAL_CTRL_*`, `MPLLA_MPLL_PWR_CTL_STAT`, `MPLLA_MPLL_PWR_CTL_MPLL_PWRUP_TIME_*`, `MPLLA_MPLL_PWR_CTL_MPLL_TUNE_VAL`, `MPLLA_MPLL_PWR_CTL_MPLL_SKIPCAL_TUNE`, and `MPLLA_MPLL_PWR_CTL_MPLL_PWR_FSM_CFG_*` cover MPLLA calibration override, FSM state, lock/output/feedback/analog enable/reset bits, lock/stable/geareshift/powerdown/PCLK timing, tune values, skip-calibration values, and configurable state-machine behavior.
- `MPLLA_SSC_FRAC_OUT`, `MPLLA_SSC_SSC_RAMP`, and `MPLLA_SSC_CONFIG` expose spread-spectrum output override values and bypass/clock-selection controls.
- `MPLLB_UPLL_PWR_CTL_CAL_CTRL_*`, `MPLLB_UPLL_PWR_CTL_STAT`, `MPLLB_UPLL_PWR_CTL_MPLL_PWRUP_TIME_*`, `MPLLB_UPLL_PWR_CTL_MPLL_ANA_DAC_STATUS`, and MPLLB SSC registers provide the analogous UPLL/MPLLB calibration, status, power timing, DAC status, and spread-spectrum controls.

The final CR2 analog-transfer section describes the digital-to-analog boundary:

- `ANA_XF_STAT_IN` and `ANA_XF_STAT_OUT` expose analog comparator, clock-detect, MPLLB lock/EOC/DAC, bandgap/reference/RT controls, term controls, flyover, and async reset fields.
- `ANA_XF_MPLLA_STAT_OUT` and `ANA_XF_MPLLB_STAT_OUT` publish analog enable/cal/reset/feedback-clock/power-mixer and VREG/PLL control status fields.
- `ANA_XF_BG_OVRD_OUT`, `ANA_XF_REF_OVRD_OUT`, `ANA_XF_SUP_VREF_CTL`, `ANA_XF_*_OVRD_OUT_*`, `ANA_XF_*_PMIX_OVRD_OUT_*`, `ANA_XF_RTUNE_OVRD_OUT`, `ANA_XF_SUP_OVRD_OUT`, and `ANA_XF_MPLLA_TUNE_OVRD_OUT_0` define override output fields crossing into analog bandgap, reference clock, supervisor VREF, MPLLA/MPLLB, PMIX, RTUNE, and tuning controls.
- `ANA_XF_SUP_ANA_CREG00` through `_03` and `_OVRD`, plus `ANA_XF_MPLLA_ANA_CREG00` through `_05` and `_OVRD`, provide analog configuration register layouts for supervisor and MPLLA-specific controls.
- The chunk ends while defining `ANA_XF_MPLLB_ANA_CREG00` through the beginning of `_CREG05`; this includes MPLLB analog override, enable/cal/reset, measurement, VREG, test-clock, PLL ring, bias, charge-pump, V2I, divider, and partial SPO/PLL-speed/RC-filter fields.

## APIs, Types, and Functions

This chunk declares no functions, structs, unions, enums, or storage. Its interface is the macro namespace consumed by AMD display driver register-access helpers. The important contracts are:

- `*_SHIFT` macros give the least-significant bit index for a field.
- `*_MASK` macros give the already-shifted mask that should be used for read-modify-write preservation or field extraction.
- Many CR1/CR2 registers are 16-bit register images with masks such as `0xFFFFL`, `0x7FFFL`, `0x8000L`, and `0xFFFCL`; lane-local PIPE1/LPC PHY registers commonly use 8-bit masks such as `0xFFL`, `0x3FL`, `0x80L`, and `0xFCL`.
- Repeated fields encode hardware instance and path in the symbol name, for example `LANE0_PIPE1` versus `LANE1_PIPE1`, `MPLLA` versus `MPLLB`, `OVRD_IN` versus `ASIC_IN`, and `ANA_XF_*_OVRD_OUT` versus `ANA_XF_*_STAT_OUT`.
- Full-word `VAL`, `IDCODE`, `FBDIV`, and address/data fields are intentionally opaque in this header; consumers must rely on the hardware programming sequence or register database for semantic subfields.

Typical generated-register helper code uses these macros by clearing `MASK`, shifting a requested value by `SHIFT`, applying the mask, and writing the result to the register address from the companion offset header. Status paths read a register, mask the field, shift it down, and interpret the resulting value according to the PHY/PLL programming code.

## Control Flow and State

There is no C control flow in the header itself. Control-flow implications appear in the hardware sequences that use these fields:

- RX adaptation and signal-detect code can enable detectors, select PPM monitor mode, start/observe adaptation, manipulate CDR recovery timing, force override values, and observe live signal-detect outputs.
- Lane margining code writes `START_MARGIN`, margin type, offset, direction, and reset bits, then reads sample/error or status fields through associated lane/VDR paths. `ENABLE_DESTR_MARGINING` indicates that some margining sequences can intentionally disturb the link and must be coordinated with link state.
- Link-training and PHY tuning paths program RX polarity, elastic-buffer mode/depth, RX EQ training, TX de-emphasis, local preset coefficient requests, FS/LF coefficients, TX margin/swing, and HDP-specific variants. Status bits such as `RX_EQ_IN_PROGRESS`, `RX_EQ_VAL`, and `INVALID_REQUEST` are used for polling and diagnostics.
- Vendor-defined register access uses split low/high address and data fields. Driver or firmware code must preserve write/read ordering around `C20_VDR_WR_ADDRESS_*`, `WR_DATA_*`, `RD_ADDRESS_*`, and `RD_DATA_*` because this header only defines fields and does not enforce transaction sequencing.
- PLL control code programs override values and enable bits for MPLLA/MPLLB dividers, multipliers, bandwidth, VCO, SSC, PCLK, FB clocks, resets, calibration, power-up times, and FSM configuration. It then polls lock, calibration, output-enable, lane-sync, and state fields.
- Analog-crossing code drives or observes bandgap, reference clock, VREF, RTUNE, MPLLA/MPLLB analog, PMIX, and supervisor analog controls. These fields sit at a sensitive boundary between digital register programming and analog PHY behavior.

State is entirely hardware state. Register writes persist until overwritten, reset, power-gated, or changed by PHY firmware/hardware side effects. Some fields are likely read-only status, some are override enables, some are writeable control knobs, and some may be latched or self-clearing. The header does not encode access policy, ordering requirements, reset defaults, side effects, or whether reserved bits must retain reset values.

## Dependencies and Integration Points

This header depends only on the C preprocessor, but its symbols are tightly coupled to the matching DCN 3.2.0 register-offset header and to AMDGPU DC/DCN32 register programming conventions. Relevant integration points include:

- DCN 3.2 PHY/link code that configures DisplayPort/HDMI PHY lanes, CDR, signal detect, equalization, transmitter swing/de-emphasis, and lane polarity.
- Firmware or driver paths that issue C20 PHY indirect-message-bus transactions through CR1, lane, and CR2 address blocks.
- Display link training, link retraining, hotplug recovery, and diagnostics that need lane margining, RX EQ status, TX preset coefficients, and invalid-request/error signals.
- Clock and PHY bring-up code that powers up MPLLA/MPLLB, programs PLL multipliers and spread spectrum, controls feedback/PCLK/output enables, and polls lock/calibration/state bits.
- Power management and suspend/resume flows that must restore PLL power FSM timing, skip-calibration/tune values, bandgap/reference power-up timing, analog reset, and override state.
- Hardware validation and board bring-up tools that read IDCODE, RTUNE, analog status, DAC status, VDR fields, and analog CREG values for low-level PHY characterization.

Because this is a generated ASIC register header, most direct consumers are not visible in the header itself. The practical dependency is naming consistency: any register table or helper macro that names a field such as `MPLLB_ANA_LOCK`, `RX_SIGDET_HF`, `TX_DEEMPH_17_12`, or `MPLL_LOCK` expects the exact generated symbol spelling and bit layout provided here.

## Risks

The main correctness risk is silent hardware misprogramming. A wrong shift or mask can preserve the wrong bits, overwrite reserved/neighbor fields, poll the wrong status bit, or program analog/PLL values outside the intended field width. In this chunk that risk is especially high for PLL, SSC, RTUNE, and analog controls because errors can prevent PHY lock, produce unstable clocks, or make link training unreliable.

Reserved fields are prominent. Many registers include large `RESERVED_*` masks, and some configuration registers are entirely reserved in this chunk. Consumers should not infer that reserved fields are safe to write just because masks are present; generated headers expose layout, not write policy. Read-modify-write helpers should preserve reserved bits unless the hardware specification says otherwise.

The lane0/lane1 and MPLLA/MPLLB families are similar but not identical. For example, lane PHY fields are 8-bit while CR2 supervisor fields are usually 16-bit; MPLLA power timing includes a longer set of `MPLL_PWRUP_TIME_0` through `_8`, while the MPLLB UPLL section shown here has a shorter timing/status set. Copying layouts across instances without checking the generated macro name can corrupt programming sequences.

Override fields often come in value/enable pairs. Programming an override value without its enable bit, or leaving an override enable set after link training, can cause persistent PHY behavior that is hard to diagnose. Conversely, clearing an enable bit while stale override values remain in the register may change behavior after a later power transition if code re-enables the override.

This chunk has boundary risks. The first visible lines are the tail of `C20_PHY_CR1_RAWLANEAONX_DIG_RX_ADAPT_DONE_BANK_1`, so complete interpretation of that register requires the previous chunk. The final visible lines stop during `C20_PHY_CR2_SUP_DIG_ANA_XF_MPLLB_ANA_CREG05`, so the next chunk is required before documenting the complete MPLLB analog CREG05 layout.

## Test Signals

Useful validation for code that consumes these macros includes:

- Compile coverage for DCN 3.2 AMDGPU display paths, catching renamed or missing C20 PHY shift/mask symbols.
- Register trace comparison against AMD's DCN 3.2.0 register database for the exact CR1 raw-lane, lane0/lane1 PIPE1 LPC PHY, and CR2 supervisor/PLL/analog field positions.
- DisplayPort and HDMI link bring-up on DCN 3.2 hardware, including HPD, AUX/DDC, link training, retraining, mode set, and sustained stream stability.
- PHY margining exercises that toggle `START_MARGIN`, voltage/timing selection, margin offset/direction, sample/error resets, destructive margin enable, and verify expected status/error-count behavior.
- RX/TX equalization tests that program TX de-emphasis, FS/LF, preset coefficient request, RX EQ training, polarity, elastic-buffer controls, and observe `RX_EQ_IN_PROGRESS`, `RX_EQ_VAL`, and `INVALID_REQUEST`.
- PLL and spread-spectrum tests that program MPLLA/MPLLB overrides, power-up timing, SSC fractional/ramp values, VCO controls, and then verify lock, calibration, output-enable, lane-sync, and clock quality.
- Suspend/resume and power-gating tests that confirm C20 PHY override state, PLL FSM configuration, RTUNE set/status values, bandgap/reference timing, and analog-crossing controls are restored or reset intentionally.
- Low-level hardware diagnostics that read IDCODE, RTUNE status, MPLL DAC status, analog comparator/clock-detect/lock fields, and VDR readback fields after link failures.
