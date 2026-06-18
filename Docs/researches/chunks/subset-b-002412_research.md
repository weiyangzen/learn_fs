# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 63232-65642

## Purpose

This chunk is generated AMDGPU Display Core register-field metadata for the DPCS 4.2.3 `DPCSSYS_CR3` register window. It defines C preprocessor constants only: `__SHIFT` macros give bit positions and `_MASK` macros give the corresponding already-shifted bit masks for 16-bit DPCS CR register payloads. There are no executable functions, structs, variables, locks, memory allocations, or direct MMIO operations in this range.

The range belongs to the `dpcssys_cr3_rdpcstxcrind` address block. It starts cleanly at `DPCSSYS_CR3_LANE0_DIG_ANA_TX_OVRD_OUT_2`, covers the tail of lane 0 analog TX field metadata, then covers a full lane 1 register span from digital ASIC override/input/output through TX/RX power, VCO/CDR/DPLL, RX adaptation/statistics, M-PHY, digital-to-analog override/status, and analog TX/RX controls. It then begins lane 2 with digital ASIC override input and equalization metadata, ending after the first shift of `DPCSSYS_CR3_LANE2_DIG_ASIC_RX_OVRD_OUT_0`.

Within the requested 2,411 source lines there are 236 register comment blocks, 1,205 shift macros, 981 mask macros, and 439 reserved or no-connect field lines. The repository path is under `sources/distributed-fs/ceph-client`, but this header is GPU display PHY register metadata from the AMD Linux driver tree, not Ceph filesystem logic.

## Important APIs, Types, And Macros

The public interface is the generated macro naming ABI:

- `DPCSSYS_CR3_<lane-or-block>_<register>__<field>__SHIFT` identifies the least-significant bit index for a field.
- `DPCSSYS_CR3_<lane-or-block>_<register>__<field>_MASK` identifies the field mask at its register position.
- Register comments such as `//DPCSSYS_CR3_LANE1_DIG_RX_ADPTCTL_ADPT_CFG_0` delimit the field constants for one hardware register.
- `RESERVED_*` and `NC*` fields expose generated bit ranges but should not be treated as writable feature definitions.

Major groups covered:

- Lane 0 TX analog tail: `DIG_ANA_TX_OVRD_OUT_2` fast-start, TX clock loopback, and AC JTAG bits, followed by `ANA_TX_*` measurement, power override, alternate bus, ATB, DCC DAC/control, termination code/control, clock override, miscellaneous VREG/slew/inversion, and reserved trim words.
- Lane 1 digital ASIC interface: `DIG_ASIC_LANE_OVRD_IN`, TX/RX override inputs and outputs, live ASIC input/output mirrors, TX/RX EQ and CDR/VCO fields, loopback, OCLA, request/acknowledge, reset, pstate, rate, width, MPLL select, data enable, invert, low-power-detect, HDMI/MPHY mode, async TX, VREG bypass, and RX adaptation status fields.
- Lane 1 TX power and timing: `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`, TX power-up timers, DCC CR-bank/DAC control, DCC range/selector/ack/address, TX clock alignment, and TX LBERT control.
- Lane 1 RX power, calibration, CDR, DPLL, and adaptation: `DIG_RX_PWRCTL_*`, `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, `DIG_RX_ADPTCTL_*`, including RX pstate timing, VCO calibration controls/status, CDR frequency/track/SSC settings, DPLL frequency bounds, adaptation configuration, ATT/VGA/CTLE/DFE status, slicer controls, VDAC offsets, reset, and CR-bank selectors.
- Lane 1 RX statistics and M-PHY: `DIG_RX_STAT_*` load, mask, match, sample, counter, calibration-comparator clock, and stop controls plus `DIG_MPHY_RX_*` PWM, low-speed termination, and analog PWM stable-count fields.
- Lane 1 digital-to-analog and direct analog controls: `DIG_ANA_TX_*`, `DIG_ANA_RX_*`, `DIG_ANA_STATUS_*`, signal-detect, RX/TX termination, M-PHY override, TX DCC override, and `ANA_TX_*` / `ANA_RX_*` analog-side clock, CDR/deserializer, slicer, power, squelch, calibration, ATB measurement, and reserved fields.
- Lane 2 opening digital ASIC sequence: lane override, TX override inputs 0-4 and output, RX override inputs 0-5, RX EQ override inputs 0-1, and the first `RX_OVRD_OUT_0__ACK__SHIFT`.

These macros are useful only when paired with the matching address definitions in `dpcs_4_2_3_offset.h`. In that companion file the relevant offsets include lane 0 tail registers around `0x10c4` and `0x10e0`-`0x10ef`, lane 1 from `0x1100` through `0x11ff`, and lane 2 starting at `0x1200`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is indirect:

1. DCN 3.1.6 resource code includes `dpcs/dpcs_4_2_3_offset.h` and this `dpcs/dpcs_4_2_3_sh_mask.h`.
2. AMD display register helpers and generated register tables token-paste symbolic register and field names into offset, shift, and mask constants.
3. Link encoder, PHY, clock, power, training, diagnostics, and suspend/resume paths use those constants through AMD display helper macros such as register set/update/get field operations.
4. The DPCS/PHY hardware and firmware perform the actual state transitions: lane request/ack handshakes, PLL and VCO calibration, TX/RX power-state sequencing, RX adaptation, signal detect, DCC/termination calibration, and debug capture.

The macro file does not encode ordering requirements. Consumers still need hardware-specific sequences, such as enabling reference clocks before link use, polling calibration/status fields before enabling data paths, pairing override values with override-enable bits, and releasing diagnostic overrides when firmware should resume ownership.

## State And Persistence Behavior

The macros are compile-time constants and persist only in object code as immediate values used by register helpers. The state described by the fields lives in hardware registers.

State represented in this chunk includes:

- TX analog state: fast-start, loopback clock, AC JTAG, power override, refgen/clock/data/serial enables, DCC DAC values, termination codes, VREG boost, word/MPLL clock enable overrides, slew/inversion/pre/post controls, alternate bus selection, and ATB measurement muxing.
- Lane 1 digital link state: TX/RX request and acknowledge, reset, pstate, rate, width, MPLL select, data enable, detect-RX, invert, low-power-detect, HDMI/MPHY mode, async drive, VREG bypass, loopback, and OCLA probe enables.
- RX analog/digital state: CDR tracking/SSC, VCO/ref load values, DPLL frequency and bounds, RX termination, alignment, AFE/DFE adaptation enables, ATT/VGA/CTLE/DFE tap status, slicer levels, IQ/phase controls, squelch and signal-detect controls, and RX valid/loss statistic counters.
- Calibration and debug state: VCO calibration timing/status, DCC DAC bank/range/selector/ack/address, RX statistic match/sample/count registers, LBERT controls/errors, M-PHY PWM/termination controls, ATB measurement selection, and analog status readbacks.

Persistence and access semantics are hardware-defined. Configuration and override fields can survive until the driver reprograms the link, the lane or DPCS instance is reset, the PHY is power-gated, firmware retakes ownership, or suspend/resume restore rewrites state. Status, counter, ACK, interrupt-like, and clear-style fields may be read-only, sticky, self-clearing, write-one-to-clear, or otherwise side-effect-sensitive; this shift/mask header intentionally does not describe those access rules.

## Dependencies And Integration Points

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` supplies the matching `ixDPCSSYS_CR3_*` offsets. The shift/mask and offset headers must remain generated from the same hardware database.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes both DPCS 4.2.3 headers, selecting this register metadata for the DCN 3.1.6 display resource stack.
- AMD Display Core register helper infrastructure is the practical consumer. A missing macro causes build failures; an incorrect mask or shift can compile cleanly but program the wrong hardware bit.
- Functional integration points include DisplayPort/HDMI PHY bring-up, link training, lane power-state transitions, RX adaptation, DCC and VCO calibration, signal detection, loopback/LBERT diagnostics, M-PHY modes, suspend/resume restore, and manufacturing/debug features such as ATB, AC JTAG, and OCLA.
- Neighboring generated headers for DPCS 4.2.0, DPCS 4.2.2, and DCN aggregate register maps have similar field families. They are useful for drift checks, but consumers must not mix generation-specific offset and mask headers unless the ASIC register source explicitly guarantees equivalence.

## Risks And Edge Cases

- Bitfield drift is the primary risk. These are untyped preprocessor constants, so a wrong mask or shift can silently alter lane power, PLL selection, RX adaptation, analog trim, signal-detect, or debug behavior.
- The range has an end boundary inside `DPCSSYS_CR3_LANE2_DIG_ASIC_RX_OVRD_OUT_0`: only `ACK__SHIFT` is included here, while the remaining shifts and masks continue in the next chunk. Whole-register conclusions for that lane 2 output register require reconciliation.
- Override value and override-enable pairs are frequent. Writing a value without its enable has no intended effect; leaving enable bits asserted after diagnostics can conflict with firmware or autonomous PHY sequencing.
- Reserved and `NC` masks are numerous. Full-register writes that do not preserve reserved fields can disturb undocumented analog, calibration, or power-control behavior.
- Lane naming is repetitive. Lane 0, lane 1, and lane 2 field families often differ only by the `LANE*` prefix and offset range, so copy/paste mistakes can target the wrong lane while still compiling.
- Status, ACK, statistic counter, DCC, and calibration fields can have side effects or sticky semantics that are not visible in this header. Misusing clear or status masks can hide training failures or leave stale diagnostics.
- TX/RX power, VCO/CDR/DPLL, and analog termination fields are sequencing-sensitive. Incorrect use can present as blank displays, intermittent high-rate failures, stuck link training, lane-specific errors, suspend/resume regressions, or elevated display power.

## Test Signals

- Build AMDGPU Display Core for the DCN 3.1.6 configuration that includes `dcn316_resource.c`; this catches include selection, macro spelling, and token-pasting failures.
- Run generated-header consistency checks: every complete non-reserved field should have matching `__SHIFT` and `_MASK` definitions, masks should fit the expected 16-bit CR payload, and known chunk-boundary exceptions should be limited to `DPCSSYS_CR3_LANE2_DIG_ASIC_RX_OVRD_OUT_0`.
- Cross-check every register comment in this chunk against a corresponding `ixDPCSSYS_CR3_*` offset in `dpcs_4_2_3_offset.h`, especially the lane 1 span from `0x1100` through `0x11ff` and lane 2 start at `0x1200`.
- Diff the generated field layout against AMD's authoritative DPCS 4.2.3 register source and compatible sibling generated headers where the hardware database expects symmetry.
- Exercise display hardware across DP and HDMI modes: hotplug, link training at multiple rates and lane counts, modeset, multi-monitor, suspend/resume, and any supported loopback/LBERT or PHY diagnostics.
- Inspect hardware-facing evidence for failures: VCO/CDR/DPLL status reaches expected values, RX adaptation ACK/status and EQ taps are plausible, statistic counters behave with cable/link changes, DCC and termination calibration do not remain stuck, signal-detect and squelch track physical state, and no lane-specific power or reset ACK remains asserted unexpectedly.

## Chunk Boundary Notes

The previous chunk owns `DPCSSYS_CR3_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT_2`; this chunk starts immediately after it at `DPCSSYS_CR3_LANE0_DIG_ANA_TX_OVRD_OUT_2`. This chunk fully covers the lane 0 analog TX tail and the lane 1 CR3 lane register span, then starts lane 2 digital ASIC overrides. The next chunk must continue `DPCSSYS_CR3_LANE2_DIG_ASIC_RX_OVRD_OUT_0` beginning with `ACK_OVRD_EN__SHIFT` and reconcile the rest of lane 2 before final per-file conclusions are made.
