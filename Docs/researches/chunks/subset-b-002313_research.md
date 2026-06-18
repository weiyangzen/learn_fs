# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 59641-62003

## Scope

This chunk covers `dpcs_4_2_0_sh_mask.h` lines 59641-62003, a generated AMD DPCS 4.2.0 register shift/mask header fragment. The range is entirely preprocessor metadata: `#define` constants for register field bit shifts and masks, grouped under `//DPCSSYS_CR2_*` register comments. It contains 223 register-comment groups and about 2,140 macro definitions, split roughly evenly between `__SHIFT` and `_MASK` constants. There are no C functions, structs, enums, storage objects, or executable control flow in this slice.

## Purpose

The fragment supplies symbolic bitfield definitions for Display Core PHY/SerDes programming in the AMDGPU DRM driver. Callers use the constants to pack or extract hardware register fields without hard-coding bit positions. The visible register groups describe two main hardware areas:

- `DPCSSYS_CR2_SUPX_*`: supervisor/global DisplayPort/HDMI PHY controls, including MPLLA/MPLLB PLL override inputs, PLL analog controls, power-control timers/status, spread-spectrum clocking, RTUNE, bandgap/reference power-up, and analog override outputs.
- `DPCSSYS_CR2_LANEX_*`: per-lane PHY controls and status, including lane ASIC override/input/output fields, TX and RX power states and timing, TX DCC DAC access, TX clock alignment and LBERT, RX VCO calibration, RX CDR/DPLL, and RX adaptation/equalization status.

The header is normally paired with address-definition headers for the same ASIC block. Address macros identify a register; this file's `__SHIFT` and `_MASK` macros define how to encode individual fields within that register.

## Important APIs, Types, and Macros

There are no callable APIs or data types. The exported interface is a large set of C preprocessor constants whose naming convention is the contract:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position for `FIELD`.
- `REGISTER__FIELD_MASK` gives the masked field value in register position.
- Register comments such as `//DPCSSYS_CR2_SUPX_DIG_MPLLB_OVRD_IN_0` separate field groups and match the prefix used by the following macros.

Key macro families in this chunk:

- MPLLA/MPLLB digital override and SSC fields: `DPCSSYS_CR2_SUPX_DIG_MPLLA_*` and `DPCSSYS_CR2_SUPX_DIG_MPLLB_*` define enable, divider, multiplier, standby, calibration, fractional-N quotient/remainder/denominator, charge-pump, gear-shift, spread-spectrum peak/step-size, and clock-output fields. The B-side family mirrors the A-side family for dual PLL resources.
- Supervisor digital fields: `DPCSSYS_CR2_SUPX_DIG_SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, `LVL_OVRD_IN`, `ASIC_IN`, `LVL_ASIC_IN`, and `BANDGAP_ASIC_IN` describe prescaler, RTUNE request/acknowledge, bandgap, reference clock, voltage boost/reference, and ASIC-facing global control/status.
- Analog supervisor fields: `DPCSSYS_CR2_SUPX_ANA_*` includes prescaler, RTUNE, bandgap, ATB measurement, MPLLA/MPLLB analog override, miscellaneous PLL controls, PLL control registers, and reserved/vendor-specific knobs.
- MPLL power-control fields: `DPCSSYS_CR2_SUPX_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR2_SUPX_DIG_MPLLB_MPLL_PWR_CTL_*` expose state-machine override, status, timers, calibration, DAC range, analog DAC output, and SSC spread-type fields.
- Analog override outputs: `DPCSSYS_CR2_SUPX_DIG_ANA_MPLLA_OVRD_OUT_*`, `MPLLB_OVRD_OUT_*`, `ANA_RTUNE_OVRD_OUT`, `ANA_BG_OVRD_OUT`, and `ANA_MPLL{A,B}_PMIX_OVRD_OUT` define fields that drive or override analog enable/reset/calibration, charge pump, PMIX, RTUNE, bandgap, and reference regulator behavior.
- Lane ASIC override/input/output fields: `DPCSSYS_CR2_LANEX_DIG_ASIC_*` defines per-lane TX/RX requests, rate, width, pstate, data enable, loopback, inversion, reset, CDR/SSC/alignment, equalizer controls, RX/TX acknowledge/status, and ASIC-facing input/output mirrors.
- TX lane power and diagnostics: `DPCSSYS_CR2_LANEX_DIG_TX_PWRCTL_*`, `TX_CLK_ALIGN_TX_CTL_0`, and `TX_LBERT_CTL` define TX P-state enable/reset/data/RX-detect bits, power-up timing fields, DCC CR-bank/DAC access fields, FIFO bypass/2UI shift controls, and LBERT pattern/error-trigger controls.
- RX lane power, calibration, and adaptation: `DPCSSYS_CR2_LANEX_DIG_RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, `RX_LBERT_*`, and `RX_ADPTCTL_*` define RX P-state power bits, power-up timing, VCO calibration controls/status, CDR coefficients/status, DPLL frequency bounds, adaptation configuration, reset, and CTLE/VGA/ATT/DFE tap status.

## Control Flow

This chunk has no runtime branch, loop, or call flow. Runtime behavior is created by other AMDGPU code that includes this header and performs read/modify/write operations, usually in a pattern equivalent to:

1. Read a DPCS register through the driver's MMIO/register-access helpers.
2. Clear a field with `~FIELD_MASK`.
3. Shift a desired value by `FIELD__SHIFT`.
4. Mask it with `FIELD_MASK`.
5. Write the updated register value back, or test a status field after masking and shifting.

Several register families imply hardware state-machine sequencing even though the header does not implement it. For example, `REQ`/`ACK`, `OVRD_EN`, `*_PSTATE_*`, `*_PWRUP_TIME_*`, `*_CAL_*`, `RTUNE_*`, and `ASM1_DONE` fields are intended to be used by link bring-up, power transition, PLL calibration, receiver adaptation, and diagnostics flows elsewhere in the driver.

## State and Persistence Behavior

The macros are compile-time constants and do not persist state. The state they name is hardware-resident:

- PLL state: MPLLA/MPLLB enable, reset, standby, fractional-N values, charge-pump settings, DAC/calibration outputs, and spread-spectrum parameters are latched in PHY registers.
- Supervisor/reference state: bandgap, prescaler, reference clock, RTUNE, and analog override controls affect common PHY resources shared across lanes.
- Per-lane TX/RX state: lane request, power state, rate, width, TX cursor values, RX CDR/VCO/adaptation settings, DCC DAC selection, and status bits live in per-lane DPCS registers.
- Diagnostic state: LBERT, OCLA, ATB measurement, DPLL frequency, and adaptation status fields expose transient hardware measurement or test state.

Persistence across suspend/resume, hotplug, link retraining, or GPU reset is not handled in this header. Any required save/restore or reprogramming must be implemented by the display/PHY code that consumes these constants.

## Dependencies

The fragment depends only on the C preprocessor and inclusion by driver source. Its semantic dependencies are external:

- Register address headers for DPCS 4.2.0 provide register offsets that pair with these field definitions.
- AMDGPU display code and DC/DM PHY programming paths provide register read/write helpers, link-rate policy, DP/HDMI mode selection, PLL programming formulas, and sequencing.
- Hardware documentation or generated register databases define the authoritative bit layouts. The repetitive shape and `_sh_mask.h` suffix indicate this file is generated rather than manually authored.

Because it is a header-only constant table, include order matters only insofar as consumers need both address macros and field macros visible before using them.

## Integration Points

Likely integration points are display link bring-up, PHY tuning, power management, and diagnostics inside the AMDGPU DRM driver:

- DP/HDMI clock programming code uses the MPLLA/MPLLB multiplier, fractional-N, divider, SSC, PMIX, and output-enable fields when selecting and enabling PHY clocks.
- Link training and mode-setting paths use per-lane TX/RX override, rate, width, cursor, CDR, VCO, and equalization/adaptation fields.
- Runtime power management and reset paths use `*_PSTATE_*`, `*_PWRUP_TIME_*`, `MPLL_PWR_CTL_*`, bandgap/reference power-up, and reset/standby fields.
- Debug, validation, and factory-test paths may use LBERT, OCLA, ATB, DCC DAC, RTUNE status, DPLL frequency, and adaptation-status masks.

The `LANEX` naming indicates the same macros are intended to be applied to lane-indexed register instances. Consumers must combine these field definitions with the correct lane-specific register address.

## Risks and Edge Cases

- Bitfield drift is high impact. If a shift or mask differs from the actual DPCS 4.2.0 hardware database, consumers can corrupt adjacent fields such as reset, override-enable, clock-enable, or calibration controls.
- Reserved fields are explicitly represented. Callers should preserve them in read/modify/write sequences unless hardware documentation says otherwise; writing mask-derived values blindly across a whole register can alter reserved bits.
- Many fields are paired with override-enable bits. Setting the data bit without the corresponding `*_OVRD_EN` bit may have no effect; setting override-enable without a coherent value can force the PHY into a bad link/power state.
- A-side and B-side PLL families are highly similar. Copy/paste errors between `MPLLA` and `MPLLB` consumers can select the wrong PLL or clock output.
- Per-lane `LANEX` fields must be used with the correct lane instance. Applying a lane mask to the wrong lane register can disturb another link lane or fail link training.
- Multiword fields are split across registers in several places, such as SSC peak/step-size and TX/RX timing values. Consumers must assemble high and low parts consistently.
- Status fields such as ACK, calibration done, VCO status, DPLL frequency, and adaptation done are transient hardware signals. Polling code must account for timeouts and reset/hotplug races.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Compile coverage: all include paths using DPCS 4.2.0 masks build without undefined macro references.
- Static consistency checks: every `__SHIFT` has a matching `_MASK` for the same register field, mask widths match the documented field width, and A/B PLL families remain symmetric where intended.
- Register write review: read/modify/write call sites preserve reserved bits and pair value fields with their override-enable bits.
- Hardware/link tests: DP and HDMI modes at multiple link rates train successfully, including lane-width changes, PLL A/B selection, SSC on/off, suspend/resume, hotplug, and GPU reset.
- Power tests: TX/RX P-state transitions, PLL power-up/down, bandgap/reference power sequencing, and RTUNE sequences complete without timeout.
- Diagnostic tests: LBERT/OCLA/ATB/DCC DAC paths can enable, report expected status, and return hardware to normal operation.

## Unresolved Cross-Chunk References

This range starts in the middle of the MPLLA SSC definitions; `DPCSSYS_CR2_SUPX_DIG_MPLLA_SSC_PEAK_1` begins before line 59641. It also ends in the middle of `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS`, with the remaining masks likely following after line 62003. The merged per-file report should reconcile this chunk with adjacent chunks to describe the complete DPCS 4.2.0 mask header and verify boundary register groups are complete.
