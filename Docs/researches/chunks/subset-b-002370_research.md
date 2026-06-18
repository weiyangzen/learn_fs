# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 78675-81068

## Purpose

This chunk is part of the generated AMD DPCS 4.2.2 register bitfield header. It defines `*_SHIFT` and `*_MASK` constants for DPCSSYS CR3 registers, with no executable code, structs, or functions. The constants describe how callers pack and extract fields from 16-bit DPCS PHY/control registers when using the matching register-offset header.

The range starts in the tail of `DPCSSYS_CR3_RAWAONLANE3_DIG_RX_SIGDET_CAL`, then covers the remaining CR3 raw always-on lane 3 fields, the lane-X raw always-on fields, shared/supervisor `SUPX` PLL and analog control fields, and the beginning of lane-X ASIC-facing TX/RX interface fields.

## Important APIs, Types, And Macros

The API surface is macro-only:

- `DPCSSYS_CR3_*__FIELD__SHIFT` gives the least significant bit position for a hardware register field.
- `DPCSSYS_CR3_*__FIELD_MASK` gives the bit mask for that field.
- Reserved fields are explicitly represented as `RESERVED...` masks/shifts, which helps generated register tables preserve full register layout even when driver code should not write those bits.

Main register groups covered:

- `DPCSSYS_CR3_RAWAONLANE3_DIG_*`: lane 3 RX signal-detect calibration, VREF generator enable, calibration code latches, RX/TX DCC calibration/bank controls, MPLL bandgap timing, signal-detect overrides, firmware configuration fields, lane transceiver mode, and RX signal-detect filter configuration.
- `DPCSSYS_CR3_RAWAONLANEX_DIG_*`: lane-indexed common form of adaptation and calibration state, including AFE/CTLE offsets, RX IQ/FOM/adaptation values, DFE tap and slicer controls, MPLL/RCAL status, `ADPT_CTL_0..7`, fast flags, LOS/signal-detect filtering, statistics, RX override outputs, DCC controls, firmware configuration, and lane mode fields.
- `DPCSSYS_CR3_SUPX_DIG_*`: shared/supervisor digital controls for ID code, reference clock overrides, MPLLA/MPLLB override inputs, SSC peak and step-size fields, charge-pump controls, supervisor/prescaler/lane-level controls, ASIC input mirrors, MPLL power-control status/timers/calibration, RTUNE configuration/status/set values, and digital-to-analog override outputs.
- `DPCSSYS_CR3_SUPX_ANA_*`: shared analog controls for prescaler, RTUNE, bandgap, MPLLA/MPLLB misc/override/ATB/control/reserved registers, and switch power measurement.
- `DPCSSYS_CR3_LANEX_DIG_ASIC_*`: lane-X ASIC bridge fields for lane loopback, TX override input/output, RX override input/output, TX ASIC input/output, RX ASIC input, and RX equalization ASIC input fields.

There are no local C types. Consumers normally combine these field constants with offset macros from `dpcs_4_2_2_offset.h`, such as `ixDPCSSYS_CR3_RAWAONLANEX_DIG_ADPT_CTL_0`, `ixDPCSSYS_CR3_SUPX_DIG_MPLLA_OVRD_IN_0`, and `ixDPCSSYS_CR3_LANEX_DIG_ASIC_TX_ASIC_IN_0`.

## Control Flow

There is no runtime control flow in this header. The effective flow is compile-time token substitution:

1. A display or DMUB register helper names a register and field.
2. Helper macros such as `FD_SHIFT(reg, field)` and `FD_MASK(reg, field)` concatenate tokens into `reg__field__SHIFT` and `reg__field_MASK`.
3. The constants in this header provide the numeric shift/mask pair used to build or decode MMIO register values.
4. The matching offset macro supplies the register address, while the DC resource layer supplies the DPCS base segment for the ASIC instance.

This makes spelling and bit-position stability part of the ABI between generated ASIC headers and hand-written display code.

## State And Persistence Behavior

The file itself has no persistent state. It documents hardware state that persists in DPCS registers until hardware reset, power-gating, firmware action, or later MMIO writes change it. The fields in this chunk cover several state classes:

- Calibration and adaptation latches: RX signal-detect thresholds/codes, DCC calibration codes, IOFF/ICONST/VREFGEN codes, RX adaptation values, DFE tap values, slicer controls, FOM/statistics, and common calibration status.
- Override state: lane/TX/RX override enable/value pairs, MPLLA/MPLLB override inputs, reference clock/divider/HDMI clock overrides, analog override outputs, and ASIC bridge override controls.
- Power/clock/PLL state: MPLLA/MPLLB enable, dividers, standby, VCO/fractional-N/SSC fields, power-control status/timers, bandgap and RTUNE controls.
- Link lane operational state: TX/RX reset, invert, data enable, request/ack, low-power disable, pstate, rate, width, termination, CDR tracking/SSC, alignment, equalization, and detect-RX result fields.

Because many registers include both value and `*_OVRD_EN` bits, stale override enables can force PHY behavior after the intended programming sequence has ended. Callers need to explicitly clear override enables when handing control back to normal hardware or firmware sequencing.

## Dependencies

Direct dependencies are generated-header conventions rather than C includes:

- `dpcs_4_2_2_offset.h` supplies the matching `ix...` register addresses. In the companion offset file, this chunk's RAWAONLANEX registers occupy the `0x701c..0x7051` range, SUPX registers occupy the `0x8000..0x8096` range, and LANEX ASIC bridge registers begin at `0x9000`.
- AMD display register helper macros consume these names through token concatenation, including patterns like `FD_SHIFT(reg_name, field)`, `FD_MASK(reg_name, field)`, `FN(reg_name, field)`, and register update/read helpers.
- `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both `dpcs/dpcs_4_2_2_offset.h` and this shift/mask header for DCN 3.1.5 resource setup, alongside DPCS base segment definitions.
- Neighbor generated headers for DPCS 4.2.0, DPCS 4.2.3, and DCN 4.1.0 contain the same logical register families with formatting and mask-width differences, so cross-version copy or regeneration must preserve the target ASIC's exact constants.

## Integration Points

The chunk integrates into the AMDGPU display stack as a register-definition source for Display Core and DMUB code. It is not called directly; instead, it enables generic register access code to remain readable by spelling fields symbolically. For example, a caller can name a DPCS register field such as `DPCSSYS_CR3_SUPX_DIG_MPLLA_OVRD_IN_0__MPLLA_EN` indirectly through helper macros and get the correct DPCS 4.2.2 mask and shift at compile time.

Hardware integration points represented by the fields include:

- Display PHY lane signal detection and loss-of-signal filtering.
- RX adaptation/DFE/equalization telemetry and controls.
- MPLLA/MPLLB clock generation, spread-spectrum clocking, PLL power sequencing, and status reporting.
- Analog PHY blocks such as bandgap, RTUNE, prescaler, charge pump, and MPLL analog controls.
- ASIC-to-lane handshake signals for TX/RX request, acknowledgement, reset, data enable, low-power state, pstate/rate/width, termination, CDR, alignment, loopback, and equalization.

## Risks And Edge Cases

- Incorrect shift or mask values can silently program the wrong PHY bits, causing link training failures, display hotplug instability, bad PLL programming, or broken low-power transitions.
- Several fields are tightly coupled value/enable override pairs. Setting a value without its enable bit has no effect; leaving the enable bit set can keep hardware forced into a diagnostic or firmware-bypass state.
- Reserved masks are present but should not be treated as writable feature bits. Read-modify-write helpers must preserve reserved bits unless hardware documentation says otherwise.
- The range begins and ends mid-register: line 78675 starts with masks for `DPCSSYS_CR3_RAWAONLANE3_DIG_RX_SIGDET_CAL`, whose shift definitions are just before the chunk, and line 81068 ends after the first two shifts for `DPCSSYS_CR3_LANEX_DIG_ASIC_RX_EQ_ASIC_IN_1`, whose remaining fields continue later. Merge/reconciliation must keep neighboring chunks together for full per-register analysis.
- Cross-ASIC headers are similar but not identical. DPCS 4.2.3 uses shorter-looking 16-bit mask literals in many equivalent places, while this DPCS 4.2.2 range mostly uses zero-extended `0x0000....L` masks. Mechanical substitution across versions is risky.
- The macros are consumed through token concatenation, so renaming or typo fixes that look cosmetic can break compilation in distant register-table code.

## Test Signals

Useful validation signals are mostly build-time and hardware/regression oriented:

- Compile AMDGPU display code that includes `dcn315_resource.c`; undefined `FD_SHIFT`/`FD_MASK` expansions catch missing or misspelled macros.
- Compare this header against the matching ASIC register database or regenerated `dpcs_4_2_2_*` files to confirm bit positions and masks for CR3 RAWAONLANEX, SUPX, and LANEX blocks.
- Run display bring-up/link-training tests that exercise DisplayPort/HDMI modes using DCN 3.1.5 resources, watching for HPD, link training, PLL lock, clock switching, and low-power state regressions.
- On hardware, inspect MMIO readback around offsets `0x7024`, `0x8007`, and `0x9011` to verify field packing through the helper macros matches expected register values.
- KUnit-style or compile-only tests can validate macro arithmetic for representative fields, for example `PSTATE`, `RATE`, `WIDTH`, MPLL enable/divider fields, and RX equalization masks.
