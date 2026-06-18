# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 26283-28640

## Scope

This chunk covers lines 26283-28640 of the generated AMD DPCS 4.2.0 shift/mask header. It is a declarative hardware-register field map, not executable driver logic. The range contains 2,138 exact field macros: 1,069 `__SHIFT` definitions and 1,069 `_MASK` definitions. The first line is the trailing mask for `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0__DATA_EN_OVRD_EN`; the matching register header comments and shifts begin just before this chunk boundary.

The range is centered on `DPCSSYS_CR1` lane-level PHY control. It completes much of lane 0 transmitter/receiver/analog coverage, then starts lane 1 and proceeds through TX, RX, adaptation, statistics, MPHY RX, and the beginning of analog TX definitions.

## Purpose

The header exports symbolic bit positions and masks for AMDGPU display code that programs DPCS 4.2.0 PHY registers. Consumers use these constants with the matching offset header and register helper macros to construct read-modify-write values without embedding literal bit numbers.

In this chunk, the hardware surfaces are:

- Lane 0 ASIC override and ASIC-observed TX/RX datapath fields.
- Lane 0 TX power-state, power-up timing, DCC DAC, TX clock-align, LBERT, RX statistic, and TX analog override/status controls.
- Lane 0 analog TX measurement, power override, alternate-test bus, DCC, termination, clock-override, misc, and reserved windows.
- Lane 1 lane/TX/RX ASIC override, ASIC input/output mirror, RX EQ/CDR/VCO input mirror, OCLA control, TX power-state/timing, RX power-state/timing, VCO calibration, CDR/DPLL, RX adaptation, RX statistics, MPHY RX PWM/termination, and the start of analog TX override/termination definitions.

## Exported API Surface

There are no callable APIs, structs, enums, functions, or local variables. The macro names are the public interface. Important macro families in this range include:

- `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_1` through `_IN_5`, `TX_OVRD_OUT`, `TX_OVRD_OUT_1`, and `RX_OVRD_OUT_0`: lane 0 digital override fields for TX request, pstate, rate, width, MPLLB select, data enable, Nyquist data, disable, beacon, TX main/pre/post cursor, async drive, vreg bypass, clock-ready, DETRX, invert, low-power detect, DC coupling, extended FIFO, MPHY mode, reset, repeater master-lane enable, and acknowledge/status readback.
- `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_ASIC_IN_*`, `TX_ASIC_OUT`, and `RX_ASIC_OUT_0`: non-override ASIC mirror fields for the same lane 0 TX/RX request, rate, pstate, data-enable, equalization cursor, async, vreg, ack, DETRX, valid, and adaptation status paths.
- `DPCSSYS_CR1_LANE0_DIG_TX_PWRCTL_*`: lane 0 TX power-state programming (`TX_PSTATE_P0`, `P0S`, `P1`, `P2`) plus power-up timing windows and DCC DAC access registers (`DCC_CR_BANK_ADDR`, `DCC_CR_BANK_DATA`, `DCC_DAC_CTRL`, `DCC_DAC_RANGE`, `DCC_DAC_SEL`, `DCC_DAC_ACK`, `DCC_DAC_ADDR`).
- `DPCSSYS_CR1_LANE0_DIG_RX_STAT_*`: lane 0 receiver statistic/pattern-match support, including load value, data mask, match control pairs for CR1A/CR1B patterns and masks, statistic source/shift selection, sample counter, seven statistic counters, calibration compare clock control, extra delay/sample-disable controls, and statistic stop.
- `DPCSSYS_CR1_LANE0_DIG_ANA_*` and `DPCSSYS_CR1_LANE0_ANA_TX_*`: lane 0 digital-to-analog TX override/status fields for clocks, reset, serial enable, data rate, divider, RX detect, termination code, EQ leg pull enables/directions, pre/post controls, DCC calibration override, fast start, measurement, power override, alternate bus/test bus routing, DCC DAC, misc controls, and reserved analog TX fields.
- `DPCSSYS_CR1_LANE1_DIG_ASIC_*`: lane 1 override and ASIC mirror surfaces. Unlike the lane 0 portion in this chunk, lane 1 includes both TX and RX override inputs, RX EQ override inputs, RX CDR/VCO mirror inputs, OCLA enable, and a richer RX datapath surface.
- `DPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, and `RX_ADPTCTL_*`: lane 1 receiver power-state/timing, VCO calibration controls/status, clock-data recovery control/status, DPLL frequency/bounds, and adaptive equalization configuration/status fields for ATT/VGA/CTLE/DFE/slicer/DAC control.
- `DPCSSYS_CR1_LANE1_DIG_RX_STAT_*` and `DPCSSYS_CR1_LANE1_DIG_MPHY_RX_*`: lane 1 statistic counters and low-speed MPHY RX PWM, termination, and PWM clock-stability controls.

## Control Flow And State Behavior

This file has no control flow. Runtime behavior is imposed by the AMDGPU display code and by hardware state machines behind these memory-mapped registers.

The field names imply these stateful protocols:

- TX override versus live ASIC input: `*_OVRD_IN_*` fields pair a desired control value with an `*_OVRD_EN` bit, while `*_ASIC_IN_*` and `*_ASIC_OUT*` expose the non-overridden or post-mux hardware values. Consumers must enable overrides deliberately and then verify outputs such as `TX_ACK`, `DETRX_RESULT`, `ACK`, `VALID`, or `ADAPT_STS`.
- Lane power sequencing: `PSTATE`, `TX_PSTATE_*`, `RX_PSTATE_*`, and `*_PWRUP_TIME_*` fields encode lane power modes and delays. These values affect suspend/resume, link bring-up, low-power entry/exit, and training recovery.
- Link-rate and width control: `RATE`, `WIDTH`, `MPLLB_SEL`, `DATA_EN`, `REQ`, `DISABLE`, `CLK_RDY`, and lane reset fields are the software-visible knobs and handshake bits for activating and deactivating a lane.
- Equalization and signal-shaping: `TX_MAIN_CURSOR`, `TX_PRE_CURSOR`, `TX_POST_CURSOR`, `TX_TERM_CODE`, `TX_ANA_CTRL_*`, DCC DAC, and DCC calibration fields configure electrical output behavior. Lane 1 RX adaptation fields cover ATT, VGA, CTLE, DFE taps, data/error VDAC offsets, slicer levels, adaptation reset, and DAC control selection.
- Receiver clock recovery and calibration: lane 1 `RX_VCOCAL`, `RX_CDR`, and `RX_DPLL` fields expose calibration controls, counters, resets, lock indicators, frequency measurements, and bounds.
- Diagnostics: LBERT controls, OCLA enable, statistic sample/counter registers, pattern-match controls, and MPHY RX low-speed controls are used for bring-up, validation, error isolation, and hardware debug.

No software persistence is implemented here. Hardware register values persist or reset according to the DPCS/PHY power domains, ASIC reset behavior, and firmware ownership rules. The numerous reserved, status, counter, and latch-like fields must be interpreted from the hardware specification rather than from this header alone.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. This file is normally included with the matching DPCS 4.2.0 offset header, which supplies register addresses, and with AMDGPU/DC register helper macros that combine `__SHIFT` and `_MASK` values.

Integration points are:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC link encoder, PHY bring-up, link training, DPCS access, and display diagnostics.
- DisplayPort/HDMI PHY programming paths that select rate, width, MPLL, data enable, DETRX, reset, polarity/invert, cursor values, and analog TX electrical parameters.
- RX-side calibration/adaptation paths for lane 1, including CDR, DPLL, VCO calibration, CTLE/VGA/DFE, slicer, and statistic counters.
- Hardware debug and manufacturing/validation flows that use LBERT, OCLA, pattern/stat counters, alternate test buses, DCC DAC programming, and analog measurement/override fields.
- Generated-register validation machinery. Field names and bit layouts should stay in lockstep with AMD's register database and nearby DPCS generation headers.

## Risks

- Generated-header drift is the main risk. A one-bit shift or mask error can silently write an adjacent control bit in a PHY register, with symptoms appearing only during link training, suspend/resume, or a specific lane/electrical mode.
- Override registers mix value fields and `*_OVRD_EN` bits. Setting the value without the enable bit may do nothing; setting the enable bit with an unintended value can force hardware away from normal ASIC or firmware control.
- Many fields are status/readback-only or handshake outputs (`ACK`, `VALID`, `ADAPT_STS`, `DPLL_LOCK`, statistic done bits, calibration results) adjacent to writable controls. Consumers need access-direction knowledge from the hardware spec.
- Lane 0 and lane 1 are similar but not identical in this chunk. Lane 1 includes RX override/adaptation/CDR/VCO surfaces that are not mirrored in the lane 0 portion here; copy/paste assumptions across lanes can compile while targeting the wrong fields.
- Electrical fields such as TX cursor, termination code, DCC DAC, EQ leg controls, RX adaptation taps, slicer levels, and VCO/DPLL settings can create link instability or out-of-spec signaling if programmed outside validated tables.
- Reserved masks are exposed as macros because the generator emits every field. Driver code should avoid writing reserved fields unless an ASIC-specific sequence explicitly requires it.

## Test Signals

Useful validation is mostly build-time, register-generation, and hardware-integration oriented:

- Preprocess or compile AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`.
- Static checks that every exact `__SHIFT` in this chunk has a matching exact `_MASK`; this range has 1,069 of each.
- Diff the macros against AMD's authoritative DPCS 4.2.0 register database and the companion `dpcs_4_2_0_offset.h` register names.
- Compare lane 0 and lane 1 repeated groups where they are expected to match, while allowing known lane-specific RX/adaptation differences.
- Runtime display tests on DPCS 4.2.0 hardware: DP/HDMI link training at multiple rates and lane widths, hotplug, DETRX, suspend/resume, low-power transitions, lane reset/recovery, and error recovery.
- Electrical and diagnostic validation: TX cursor/termination programming, DCC calibration, RX CDR/DPLL lock, VCO calibration status, RX adaptation status, LBERT, OCLA capture, statistic counters, and MPHY RX low-speed mode.

## Chunk Notes For Merge

This document intentionally covers only lines 26283-28640. The preceding chunk owns the start of `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0`; the next chunk continues `DPCSSYS_CR1_LANE1_DIG_ANA_TX_TERM_CODE_CLK_OVRD_OUT` and later analog TX fields. The per-file merge should describe the whole file as a generated DPCS 4.2.0 register bitfield map and preserve the lane/instance repetition rather than treating these macros as handwritten logic.
