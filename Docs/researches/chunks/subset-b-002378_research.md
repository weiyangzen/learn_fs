# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 97715-100131

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment for the CR4 register instance. It contains only C preprocessor constants: `__SHIFT` macros define field bit positions and `_MASK` macros define corresponding field masks for 16-bit DPCS CR registers. The range starts in the middle of `DPCSSYS_CR4_RAWAONLANE2_DIG_RX_SIGDET_FILT_CTRL`, finishes the remaining raw always-on lane 2 fields, covers the full raw always-on lane 3 and raw always-on lane X template blocks, then moves into shared `SUPX` digital and analog control for ID code, reference clocks, MPLLA/MPLLB overrides, ASIC input mirrors, prescaler, RTUNE, bandgap, shared analog levels, PLL analog controls, MPLL power-control/status, SSC spread type, and shared clock/reset timing. It ends in the middle of `DPCSSYS_CR4_SUPX_DIG_RTUNE_CONFIG`.

The chunk includes about 2,101 macro definitions across 317 register groups. The major groups are raw always-on lane 2 tail content, raw lane 3, raw lane X, `SUPX_DIG`, and `SUPX_ANA`.

## Purpose

The header provides compile-time bitfield metadata used by AMDGPU display/PHY code when programming DPCS 4.2.2 hardware. Consumers pair these masks and shifts with matching address macros from the companion DPCS offset header and with AMD display register-access helpers to assemble read-modify-write values without open-coding numeric bit positions.

In this range, the fields describe:

- Tail-end CR4 raw always-on lane 2 receiver signal-detect, squelch, VREF, calibration code, DCC code, TX DCC bank, MPLL background control, firmware configuration, transceiver-mode, and signal-detect configuration registers.
- Complete CR4 raw always-on lane 3 and raw lane X layouts for RX adaptation, DFE/slicer/phase offsets, MPLL coarse tuning, initialization and fast-calibration flags, common calibration status, TX/RX override inputs, signal-detect control, VREF/calibration/DCC code readback, TX DCC bank access, firmware configuration, and lane transceiver-mode programming.
- Shared CR4 `SUPX_DIG` control for ID code readback, reference-clock override, MPLLA/MPLLB divider and HDMI-clock override, PLL multiplier/SSC/fractional-N/charge-pump parameters, ASIC-provided PLL/reference control mirrors, global PHY reset/reference/RTUNE handshake, prescaler, level override, and debug fields.
- Shared CR4 `SUPX_ANA` control for prescaler analog settings, RTUNE analog settings, bandgap/reference-voltage selection, power measurement switching, MPLLA/MPLLB analog override, ATB measurement, loop-filter/charge-pump/VREG/DLL controls, and reserved analog tuning fields.
- MPLLA/MPLLB power-control status and timing registers, including override selection, fast power-up/lock bits, DTB selection, clock enable state, calibration/reset/lock status, DAC range/output, lock/stable timers, PCLK power timing, MPLL calibration override, and SSC spread type.
- Shared clock/reset timing for bandgap and reference power-up plus the beginning of RTUNE debug/configuration fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, or callable APIs in this chunk. The public interface is the generated macro naming contract:

- `DPCSSYS_CR4_RAWAONLANE*_...__FIELD__SHIFT`: bit offset for `FIELD` in a raw always-on lane register.
- `DPCSSYS_CR4_RAWAONLANE*_...__FIELD_MASK`: mask for the same raw lane field.
- `DPCSSYS_CR4_SUPX_DIG_...__FIELD__SHIFT` and `_MASK`: shared digital/register-interface bit metadata.
- `DPCSSYS_CR4_SUPX_ANA_...__FIELD__SHIFT` and `_MASK`: shared analog-control bit metadata.
- Register delimiter comments such as `//DPCSSYS_CR4_SUPX_DIG_MPLLA_OVRD_IN_0` mark groups that correspond to address macros in `dpcs_4_2_2_offset.h`.

Notable raw always-on lane groups include:

- `DIG_AFE_*`, `DIG_DFE_*`, `DIG_RX_ADPT_*`, `DIG_RX_ADAPT_*`, `DIG_RX_SLICER_*`, `DIG_RX_PHSADJ_*`, and `DIG_RX_IQ_PHASE_ADJUST`: RX adaptation, CTLE/VGA/ATT, DFE tap/ref-level offsets, slicer DAC offsets, phase adjustment, figure-of-merit, and adaptation-done readback fields.
- `DIG_FAST_FLAGS` and `DIG_FAST_FLAGS_2`: fast or skip controls for PLL, TX/RX DCC, RX continuous calibration, TX RTUNE, RX VPHUD/VREF, RX signal detect, adaptation, and related calibration paths.
- `DIG_INIT_PWRUP_DONE`, `DIG_LANE_CMNCAL_MPLL_STATUS`, and `DIG_LANE_CMNCAL_RCAL_STATUS`: initialization, MPLL common calibration, and RCAL status bits.
- `DIG_MPLL_DISABLE`, `DIG_MPLLA_COARSE_TUNE`, `DIG_MPLLB_COARSE_TUNE`, and `DIG_MPLL_BG_CTL`: lane-local MPLL disable/coarse-tune/background-state wait controls.
- `DIG_TXRX_OVRD_IN`, `DIG_LANE_XCVR_MODE_OVRD_IN`, and `DIG_LANE_XCVR_MODE_IN`: override and readback fields for RX/TX disable and lane transceiver mode.
- `DIG_RX_SIGDET_*`, `DIG_SIGDET_OUT_*`, `DIG_RX_LOS_MASK_CTL`, `DIG_STATS`, and `DIG_RX_OVRD_OUT_*`: signal-detect filtering/calibration/output override, loss-of-signal mask count, RX PMA squelch/VREF/termination/sigdet override, and RX status fields.
- `DIG_CAL_*`, `DIG_RX_DCC_CAL_*`, `DIG_TX_DCC_*`, and `DIG_TX_DCC_CONFIG`: calibration code readbacks and TX/RX duty-cycle-correction bank/configuration fields.
- `DIG_FW_MM_CONFIG`, `DIG_FW_ADPT_CONFIG`, and `DIG_FW_CALIB_CONFIG`: firmware-facing configuration fields for memory-management, adaptation, and calibration behavior.

Notable `SUPX_DIG` groups include:

- `IDCODE_LO` and `IDCODE_HI`: 16-bit ID-code halves.
- `REFCLK_OVRD_IN`, `ASIC_IN`, `BANDGAP_ASIC_IN`, `LVL_OVRD_IN`, and `LVL_ASIC_IN`: reference-clock, PHY reset, bandgap, RTUNE handshake, voltage/reference level, and ASIC mirror fields.
- `MPLLA_*` and `MPLLB_*` override/input groups: enable, dividers, HDMI pixel clock, multiplier, VCO frequency, standby, calibration force, SSC enable/up-spread, PMIX, word-divide, fractional-N quotient/remainder/denominator, SSC peak/step-size, clock-sync, and charge-pump proportional/integral gain controls.
- `SUP_OVRD_IN`, `SUP_OVRD_OUT`, and `PRESCALER_OVRD_IN`: prescaler override, RTUNE request/ack, TX calibration code override, alternate low-power reference-clock selection, MPLLA/MPLLB and bandgap state override/readback, DCO range/fine-tune, reference dividers, and clock-detect controls.
- `MPLLA_MPLL_PWR_CTL_*` and `MPLLB_MPLL_PWR_CTL_*`: shared MPLL power FSM override/status, timers, DAC, calibration, and analog DAC readout fields.
- `CLK_RST_*`, `RTUNE_DEBUG`, and `RTUNE_CONFIG`: shared bandgap/reference power-up timing, VPHUD reference control, manual RTUNE debug, and RTUNE enable/configuration fields.

Notable `SUPX_ANA` groups include:

- `PRESCALER_CTRL` and `RTUNE_CTRL`: analog prescaler ATB/measurement/fast-start/VREG settings and RTUNE ATB, DAC mode/chop, force-continuous, and feedback-divider control.
- `BG1`, `BG2`, `BG3`, and `SWITCH_PWR_MEAS`: shared bandgap/reference-voltage selectors, temperature/power measurement, ATB switch, VPHUD/reference selection, and TX swing/RX calibration reference fields.
- `MPLLA_*` and `MPLLB_*` analog groups: matching analog controls for override enable/calibration/reset/feedback clock, ATB measurement, loop filter, charge pump, SPO calibration, VREG bypass/gain, DLL/divider reserved controls, and analog tuning.

## Control Flow

This header contributes no runtime control flow. Runtime sequencing lives in AMDGPU display and PHY code that uses these constants to read, mask, shift, and write indexed DPCS CR registers.

The implied hardware sequences in this chunk are sensitive PHY bring-up and diagnostic paths: lane RX adaptation and calibration, signal-detect calibration/filtering, TX/RX disable override, DCC bank programming, transceiver-mode selection, shared reference-clock selection, bandgap startup, MPLLA/MPLLB divider/SSC/fractional-N programming, charge-pump and analog tuning, RTUNE handshakes, MPLL power FSM transitions, and shared clock/reset timing.

## State And Persistence

The macros are stateless compile-time constants. The mutable state they describe lives in volatile DPCS hardware registers. That state can be changed by display link training, modesets, hotplug handling, PHY reinitialization, suspend/resume, GPU reset recovery, power gating, and debug or validation tools.

Some fields represent latched or sampled hardware status, such as adaptation done, initialization done, RCAL and MPLL common-calibration status, RX PMA squelch/status, signal-detect readback, RTUNE acknowledgement, reference-clock acknowledgement, MPLLA/MPLLB state, MPLL FSM state, clock-enable state, calibration/reset state, lock status, and analog DAC output. Other fields are override values or override enables; leaving override enables asserted after diagnostics can persistently redirect normal PHY control until the register is restored or reset.

The many reserved masks are part of the hardware contract. Consumers should preserve reserved bits during read-modify-write operations unless a hardware sequence explicitly documents otherwise. This is especially important here because most groups are 16-bit CR registers and many analog/shared-control fields affect the complete CR4 PHY instance rather than a single lane.

## Dependencies

This chunk depends on the AMD ASIC register-generation pipeline remaining synchronized with the DPCS 4.2.2 hardware specification. It is normally consumed together with:

- `dpcs_4_2_2_offset.h`, which supplies the `ixDPCSSYS_CR4_RAWAONLANE*_*` and `ixDPCSSYS_CR4_SUPX_*` register addresses for the field groups described here.
- AMDGPU display/DC register access helpers that combine address, mask, and shift constants for indexed DPCS CR MMIO operations.
- Display link training, PHY power management, receiver adaptation, DCC calibration, signal-detect, shared PLL/refclk setup, RTUNE, and low-level hardware bring-up code in the AMD GPU driver.

The file is part of an imported Linux GPU driver tree under this repository and has no direct dependency on Ceph filesystem logic.

## Integration Points

The definitions integrate with AMD display PHY initialization and runtime link management for the CR4 instance. Raw lane 3 and raw lane X content is lane-oriented, while `SUPX_DIG` and `SUPX_ANA` content is shared across the CR4 PHY. Correct integration requires pairing each mask with the matching lane or shared register address. A raw lane 3 field must not be applied to raw lane X or lane 2 addresses unless the caller is intentionally using the generic lane-X template with the matching address mapping. Similarly, `SUPX` fields should be treated as shared controls and not as per-lane-only state.

ASIC-version specificity matters: these layouts are for `dpcs_4_2_2` and should not be mixed with neighboring DPCS versions without explicit hardware gating. The MPLLA/MPLLB mirrored groups are structurally similar, but they control separate PLL instances; copy-paste use must keep the A/B prefix aligned with the corresponding address and link clock source.

## Risks

- The range starts in the middle of `DPCSSYS_CR4_RAWAONLANE2_DIG_RX_SIGDET_FILT_CTRL`; the preceding chunk is required for that register's first shift definitions.
- The range ends in the middle of `DPCSSYS_CR4_SUPX_DIG_RTUNE_CONFIG`; the following chunk is required for that register's remaining masks and subsequent RTUNE fields.
- Generated mask/shift mistakes would compile cleanly but can silently program the wrong PHY bit.
- Shared `SUPX` fields can affect reference clocks, bandgap, PLLs, RTUNE, and PHY reset behavior across more than one lane. Incorrect writes can produce broad link-training failures, blank display, unstable HDMI/DP clocking, or failed recovery after suspend/resume.
- Override fields usually have separate value and enable bits. Setting values without enables may do nothing; leaving enables asserted after debug or validation can block normal ASIC control.
- MPLLA/MPLLB and raw lane 3/lane X groups are repetitive. Applying an A-side mask to a B-side address, or a lane-template mask to the wrong lane address, is an easy integration error.
- Reserved fields must be preserved. Accidentally writing reserved bits in these 16-bit DPCS CR registers can change undocumented analog or clock behavior.
- RTUNE, charge-pump, SSC, fractional-N, bandgap, and MPLL timer fields are timing and analog quality sensitive; incorrect values may only fail at high link rates, with specific monitors, or after thermal/voltage changes.

## Test Signals

Useful validation signals for changes touching this generated header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_2_sh_mask.h`.
- Static checks that each field has a matching `__SHIFT` and `_MASK`, masks match their shifts and widths, and DPCS CR fields stay within the expected 16-bit register shape unless hardware documentation says otherwise.
- Display bring-up on hardware using DPCS 4.2.2, including boot display, hotplug, modesets, suspend/resume, GPU reset recovery, and multi-monitor operation.
- Link-training stress across lane counts and link rates, with attention to CR4 lane 3/lane-X RX adaptation, DFE/slicer/phase, signal-detect, TX/RX override, DCC calibration, and firmware-configuration paths.
- Clocking validation for both MPLLA and MPLLB, including divider and HDMI-clock paths, SSC, fractional-N settings, charge-pump settings, MPLL power FSM transitions, lock status polling, and PCLK power timing.
- PHY diagnostics that exercise RTUNE request/ack, prescaler clock detect, bandgap and reference power-up timing, analog ATB/power-measurement selections, signal-detect output override/readback, calibration-code readback, and reserved-bit-preserving read-modify-write behavior.
