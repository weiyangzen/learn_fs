# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 97718-100127

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask register-field map. It contains no executable logic; it defines C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for 16-bit DPCS register fields. Driver code combines these definitions with the matching DPCS offset header to read, write, or update individual hardware fields safely.

The covered range has three main areas:

- The tail of the `DPCSSYS_CR4_RAWAONLANE3_*` namespace for always-on raw lane 3 receiver adaptation, DFE, signal-detect, DCC, and firmware/configuration fields.
- A parallel `DPCSSYS_CR4_RAWAONLANEX_*` namespace that repeats the same raw always-on lane register schema for an indexed/generic lane-X view.
- The start and most of the `DPCSSYS_CR4_SUPX_*` supervisor/common PHY namespace, including reference clock overrides, MPLLA/MPLLB control, spread-spectrum clocking, bandgap/reference analog controls, RTUNE calibration, PLL power-control state/timers, and analog override/status outputs. The final lines begin the `DPCSSYS_CR4_LANEX_*` lane-X ASIC override namespace.

## Important Definitions

The file section is entirely `#define` constants. There are no functions, structs, enums, or exported symbols beyond macro names. The important API surface is the naming contract:

- `<register>__<field>__SHIFT` gives the right-shift amount for a field.
- `<register>__<field>_MASK` gives the register-word mask for that field.
- Most registers are 16-bit logical fields with masks bounded by `0x0000FFFFL`; reserved regions are explicitly named `RESERVED_*`.

Lane 3 and lane-X raw always-on receiver definitions cover:

- AFE/DFE calibration values such as `DIG_AFE_*_IDAC_OFST`, `DIG_DFE_*_VDAC_OFST`, even/odd reference levels, bypass/error offsets, and DFE tap adaptation values.
- RX adaptation and status fields such as `DIG_RX_ADPT_ATT`, `DIG_RX_ADPT_VGA`, `DIG_RX_ADPT_CTLE`, `DIG_RX_ADPT_DFE_TAP1` through `TAP5`, `DIG_RX_ADAPT_DONE`, and `DIG_RX_ADAPT_FOM`.
- Phase and IQ controls such as `DIG_RX_PHSADJ_LIN`, `DIG_RX_PHSADJ_MAP`, `DIG_RX_IQ_PHASE_ADJUST`, and `DIG_RX_ADPT_IQ`.
- Fast-path bring-up flags in `DIG_FAST_FLAGS` and `DIG_FAST_FLAGS_2`, including startup/adapt/calibration bypass controls and VCO/power-up shortcuts.
- Signal-detect and LOS handling in `DIG_RX_LOS_MASK_CTL`, `DIG_RX_SIGDET_FILT_CTRL`, `DIG_RX_SIGDET_CAL`, `DIG_RX_SIGDET_*_CODE`, `DIG_SIGDET_OUT_OVRD`, and `DIG_SIGDET_OUT_IN`.
- Override outputs for receiver PMA/squelch/termination/vref/signal-detect paths in `DIG_RX_OVRD_OUT_1`, `DIG_RX_OVRD_OUT_2`, and `DIG_RX_OVRD_OUT_3`.
- DCC and calibration storage fields such as `DIG_RX_DCC_CAL_*_CODE_[0|1]`, `DIG_TX_DCC_BANK_ADDR`, `DIG_TX_DCC_BANK_DATA`, `DIG_TX_DCC_CONT`, and `DIG_TX_DCC_CONFIG`.
- Firmware and mode plumbing through `DIG_FW_MM_CONFIG`, `DIG_FW_ADPT_CONFIG`, `DIG_FW_CALIB_CONFIG`, `DIG_LANE_XCVR_MODE_OVRD_IN`, and `DIG_LANE_XCVR_MODE_IN`.

The supervisor/common `SUPX` definitions cover:

- Identification and input override registers: `DIG_IDCODE_LO`, `DIG_IDCODE_HI`, `DIG_REFCLK_OVRD_IN`, `DIG_SUP_OVRD_IN`, `DIG_PRESCALER_OVRD_IN`, `DIG_SUP_OVRD_OUT`, `DIG_LVL_OVRD_IN`, and ASIC input mirrors.
- MPLLA/MPLLB digital controls: divider/HDMI clock overrides, `MPLLA/MPLLB_OVRD_IN_0..5`, SSC peak/step-size fields, fractional-N quotient/remainder/denominator fields, charge-pump override fields, and corresponding ASIC input fields.
- Analog support controls: prescaler, RTUNE control, bandgap/reference selection, power-measure switch, PLL misc/override/ATB/control/reserved fields for both MPLLA and MPLLB.
- MPLL power-control fields: override, state, DAC max range, lock/stable timers, gearshift/preset timers, PCLK stable and power-down timings, calibration override, analog DAC output, and SSC spread type for both MPLLA and MPLLB.
- Clock/reset and RTUNE sequencing: bandgap and reference power-up timers, VPHUD reference controls, RTUNE enable/fast mode, set/stat values for RX/TX pull-up/down tuning, RTUNE counter timings, and TX calibration code.
- Analog override/status outputs: MPLLA/MPLLB clock/output/reset/calibration override outputs, RTUNE analog override output, analog status, bandgap override output, and PMIX override outputs.

The final register group in scope starts `DPCSSYS_CR4_LANEX_DIG_ASIC_LANE_OVRD_IN` and `DPCSSYS_CR4_LANEX_DIG_ASIC_TX_OVRD_IN_0`, indicating the next chunk continues generic lane-X ASIC lane/TX override fields.

## Control Flow

There is no control flow in this header. Runtime control flow is external:

1. AMDGPU display/DCN code includes the generated DPCS offset header and this shift/mask header.
2. Register helper code calculates the target MMIO address from the offset macro.
3. The helper uses these shift/mask macros to assemble, mask, extract, or update individual bitfields.
4. Hardware state machines in the DPCS/PHY block interpret those fields to control lane adaptation, signal detection, PLL bring-up, bandgap/reference power, and RTUNE calibration.

Because this is a generated register contract, correctness depends on exact field names, shifts, and masks matching the ASIC register database. The header itself does not enforce sequencing, valid values, polling intervals, or reserved-bit preservation.

## State And Persistence

The macros are compile-time constants only. They do not allocate memory or persist software state.

The state they describe is hardware-resident:

- RAWAON lane registers reflect or control per-lane always-on receiver/DFE/adaptation state.
- SUPX registers reflect or control common PHY supervisor state, including reference clocks, bandgap/reference generation, MPLL A/B configuration, PLL lock/power FSM status, and RTUNE calibration state.
- Many fields are override-enable/value pairs. Persistent hardware behavior depends on whether firmware or driver code leaves override bits asserted across link training, suspend/resume, hotplug, or power-gating transitions.
- Reserved masks mark bit ranges that should be preserved during read-modify-write operations unless the ASIC programming guide explicitly says otherwise.

## Dependencies

Primary dependencies are structural rather than call-based:

- `dpcs_4_2_0_offset.h` supplies the register addresses that pair with these field definitions.
- AMDGPU display code includes this header through DCN 3.1 resource setup, notably Yellow Carp/DCN 3.1-era DPCS register support.
- Register access helpers elsewhere in `drivers/gpu/drm/amd/display` depend on the generated mask/shift naming convention to build register-field descriptors.
- The definitions depend on AMD's internal ASIC register database. Hand edits are risky because downstream code expects generated names and exact bit positions.

## Integration Points

This chunk is most relevant to code paths that configure or inspect:

- Display link PHY lane receiver bring-up and adaptation on CR4 RAWAON lane 3 or generic lane-X paths.
- Signal-detect, loss-of-signal masking/filtering, PMA squelch, termination, VREF generation, and DCC calibration.
- MPLLA/MPLLB common PLL setup for DisplayPort/HDMI link clocks, including fractional-N and SSC programming.
- Bandgap/reference and RTUNE calibration used by the PHY before stable link operation.
- Debug or diagnostic paths that read PLL FSM state, lock bits, RTUNE status, DFE tap values, adaptation done bits, or analog status fields.

The lane-specific `LANE3` names and generic `LANEX` names must remain aligned with their corresponding offset ranges. A mismatch between lane 3 offsets and lane-X field masks would compile cleanly but program the wrong hardware bits.

## Risks

- A single incorrect shift or mask can silently corrupt adjacent fields in a hardware register, especially where multiple control bits share one 16-bit word.
- Override-enable/value pairs are easy to misuse: setting a value without the enable bit has no effect, while leaving an enable bit set can bypass firmware or hardware-managed sequencing.
- Reserved-bit masks show many high-bit regions. Runtime writes that do not preserve reserved bits can cause undocumented behavior on real hardware.
- PLL and reference-clock fields are high impact. Wrong MPLLA/MPLLB divider, fractional-N, SSC, power-control, or timer fields can prevent link clock lock or destabilize display output.
- Fast flags and calibration bypass fields can reduce bring-up latency but may hide required calibration time, causing marginal links or intermittent failures.
- This header is generated. Manual fixes in only this file can drift from the matching offset header, other ASIC revisions, or regenerated upstream files.

## Test Signals

Useful validation signals for changes touching this range:

- Preprocess or build AMDGPU/DCN code that includes `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`; macro-only errors surface at compile time.
- Diff regenerated output against AMD's authoritative DPCS 4.2.0 register database and neighboring ASIC variants to catch accidental field drift.
- On hardware, verify link training and modesets across DP/HDMI paths that exercise MPLLA/MPLLB and raw lane receiver adaptation.
- Confirm PLL lock/status fields (`MPLL_LOCK`, FSM state, output/FB/PCLK enables), RTUNE stat/set fields, and RX adaptation done/FOM/tap values through existing display debug tooling where available.
- Exercise suspend/resume, hotplug, and fast link reconfiguration paths to ensure override and fast calibration bits do not leave stale hardware state.
- Check read-modify-write call sites for reserved-bit preservation when using masks from this range.

## Chunk Boundary Notes

This document covers only lines 97718-100127 of `dpcs_4_2_0_sh_mask.h`. Earlier chunks should cover the preceding lane 3 RAWAON definitions before `DIG_AFE_CTLE_IDAC_OFST`; later chunks should continue from `DPCSSYS_CR4_LANEX_DIG_ASIC_TX_OVRD_IN_0` through the rest of the generic lane-X register definitions. The final per-file report should merge all chunks before making complete statements about the whole DPCS 4.2.0 register namespace.
