# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 124925-127329

## Scope

This chunk is part of the generated DCN 4.1.0 ASIC register shift/mask header used by the AMD display driver. It contains preprocessor constants only: each hardware field is represented by a `...__SHIFT` bit offset and a matching `..._MASK` value. There are no C functions, structs, branches, allocations, or direct MMIO operations in this range.

The range starts inside the `DPCSSYS_CR2_RAWLANEX_DIG_FSM_*` register family, covers the rest of the CR2 RAWLANEX digital FSM/IRQ/PMA/TX/RX/PCS bridge definitions, crosses an `addressBlock: dpcssys_cr3_rdpcstxcrind` marker, then covers CR3 supervisor PLL/analog/clock/tuning definitions and the beginning of CR3 lane 0 ASIC interface definitions through `DPCSSYS_CR3_LANE0_DIG_ASIC_TX_OVRD_OUT_1`.

## Purpose

The purpose of this chunk is to publish exact bit positions and masks for DPCS/DPCSSYS PHY-side registers that control fast calibration, interrupt signaling, PMA/PCS crossing, supervisor PLL/common analog resources, and lane 0 TX/RX ASIC handshakes. Runtime driver code combines these macros with matching offset headers and AMD display register helpers so field operations do not hard-code bit arithmetic.

Important covered areas:

- `DPCSSYS_CR2_RAWLANEX_DIG_FSM_*`: fast-path RX/TX calibration controls, continuous calibration/adaptation controls, common MPLL/RCAL status, fast flag/status bits, register/memory lock bits, TX DCC status, OCLA/debug enable, TX equalization update status, and RX IQ phase offset.
- `DPCSSYS_CR2_RAWLANEX_DIG_IRQ_CTL_*`: single-bit RX/TX IRQ status and clear registers plus aggregate IRQ mask registers for reset, request, rate, pstate, adaptation request/disable, lane transceiver mode, phase-2 calibration, loopback, DCC on-demand, and TX request/reset events.
- `DPCSSYS_CR2_RAWLANEX_DIG_PMA_XF_*`: override and live input/output fields crossing between digital control and PMA/MPHY resources, including lane reset/power/rate/width, supervisor clock/reset controls, TX/RX request/acknowledge, adaptation request and figure-of-merit, lane RTUNE, M-PHY controls, and RX adaptation override outputs.
- `DPCSSYS_CR2_RAWLANEX_DIG_TX_CTL_*` and `DIG_RX_CTL_*`: TX/RX FSM control, clock/data-enable overrides, loss-of-signal mask control, continuous DCC/offcan/adaptation status, and OCLA/UPCS observation controls.
- `DPCSSYS_CR2_RAWLANEX_DIG_PCS_XF_*`: PCS-facing ATE/test overrides, RX/TX electrical settings, master MPLL loop selection, PCS RX output overrides, and phase-2 calibration controls.
- `DPCSSYS_CR3_SUP_DIG_*` and `DPCSSYS_CR3_SUP_ANA_*`: CR3 supervisor ID, reference/derived clock overrides, MPLLA/MPLLB override and ASIC input mirrors, SSC parameters, level/bandgap/prescaler/charge-pump controls, analog PLL/regulator/RTUNE controls, MPLL power-control timers/status/calibration, SSC spread type, and analog override/status fields.
- `DPCSSYS_CR3_LANE0_DIG_ASIC_*`: lane 0 ASIC-side lane/TX/RX override inputs, live ASIC input mirrors, output status mirrors, repeater/digital-clock/shift-master controls, and corresponding override-enable bits.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the starting bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the 16-bit register represented in this block.
- Prefixes such as `DPCSSYS_CR2_RAWLANEX`, `DPCSSYS_CR3_SUP`, and `DPCSSYS_CR3_LANE0` are part of the register ABI and must stay aligned with the paired offset header.

Notable register families:

- Fast FSM controls: `FAST_SUP`, `FAST_TX_CMN_MODE`, `FAST_TX_RXDET`, `FAST_RX_PWRUP`, `FAST_RX_VCO_WAIT`, `FAST_RX_VCO_CAL`, `FAST_RX_CONT_*`, and `FAST_FLAGS` expose fast startup, calibration, adaptation, RX VCO, TX/RX detector, DCC, VPHUD, VREF, signal-detect, and skip-supervisor-calibration controls/status.
- Common calibration and lock status: `CMNCAL_MPLL_STATUS`, `CMNCAL_RCAL_STATUS`, `CR_LOCK`, `TX_DCC_FLAGS`, `TX_DCC_STATUS`, `TX_EQ_UPDATE_FLAG`, and `RX_IQ_PHASE_OFFSET` describe shared MPLL/RCAL progress, protected CR register/memory state, TX DCC validity, TX EQ update, and RX IQ phase trim fields.
- IRQ control: `RESET_RTN_REQ`, `RX_*_IRQ`, `RX_*_IRQ_CLR`, `TX_*_IRQ`, `TX_*_IRQ_CLR`, `IRQ_MASK`, and `IRQ_MASK_2` form the raw interrupt, clear, and mask surface for lane reset/request/rate/pstate/adaptation/phase-calibration/loopback/DCC/TX events.
- PMA crossing: `PMA_XF_LANE_OVRD_IN/OUT`, `SUP_OVRD_IN`, `SUP_PMA_IN`, `TX_OVRD_OUT`, `TX_PMA_IN`, `RX_OVRD_OUT`, `RX_PMA_IN`, `LANE_RTUNE_CTL`, `MPHY_OVRD_IN/OUT`, and `RX_ADAPT_OVRD_OUT` are the digital-to-PMA boundary for resets, requests, power state, rate/width, clocking, serializer/deserializer, adaptation, and tuning.
- TX/RX controls: `TX_CTL_TX_FSM_CTL`, `TX_CLK_CTL`, `TX_DCC_CONT_STATUS`, `RX_CTL_RX_FSM_CTL`, `RX_LOS_MASK_CTL`, `RX_DATA_EN_OVRD_CTL`, `OFFCAN_CONT_STATUS`, and `ADAPT_CONT_STATUS` expose small but important FSM and continuous-calibration controls.
- PCS/test crossing: `PCS_XF_ATE_*`, `MASTER_MPLL_LOOP`, `PCS_XF_RX_OVRD_OUT_2`, and `PCS_XF_TX_OVRD_IN_2` are used by ATE, PCS handoff, loopback/test, and phase-calibration flows.
- CR3 supervisor PLL and analog resources: `MPLLA_*`, `MPLLB_*`, `SSC_PEAK_*`, `SSC_STEPSIZE_*`, `CP_*`, `GS_*`, `PRESCALER_*`, `LVL_*`, `BANDGAP_*`, `RTUNE_*`, `ANA_MPLLAB_*`, `MPLL_PWR_CTL_*`, and `SSC_GEN_SPREAD_TYPE` describe common clocks, spread spectrum, charge pump, regulator, bandgap, RTUNE, and power/calibration state for the CR3 PHY slice.
- CR3 lane 0 ASIC interface: `ASIC_LANE_OVRD_IN`, `ASIC_TX_OVRD_IN_0..5`, `ASIC_TX_OVRD_OUT`, `ASIC_RX_OVRD_OUT_0`, `ASIC_LANE_ASIC_IN`, `ASIC_TX_ASIC_IN_0..2`, `ASIC_TX_ASIC_OUT`, `ASIC_RX_ASIC_OUT_0`, and `ASIC_TX_OVRD_OUT_1` cover forced values and observed hardware values for lane loopback, TX reset/invert/data enable/request/LPD/pstate/rate/width/MPLLB select/detect-RX/disable, beacon and equalization cursor settings, HDMI mode, VCO/divider controls, RX acknowledge/adaptation status, digital clock/repeater state, lane master state, and shift handshakes.

## Control Flow and Runtime Integration

There is no executable control flow in this header. Runtime behavior is indirect:

1. DCN 4.1.0 display/link code includes generated offset headers and this shift/mask header.
2. Register table macros bind logical register names to offsets and field masks.
3. Display Core helper macros such as register get/set/update/wait helpers use these constants to isolate named fields inside 16-bit DPCS/DPCSSYS registers.
4. Hardware state machines consume the written fields and update status, done, acknowledge, interrupt, and calibration readback fields.

The hardware flow represented by these macros is generally: configure common CR3 supervisor PLL/reference/RTUNE resources, program or clear CR2 raw-lane fast-calibration and PMA/PCS crossing overrides, configure lane 0 request/rate/width/pstate/TX equalization, optionally force override-enable bits for bring-up or diagnostics, start calibration/adaptation/test operations, then poll IRQ/status/acknowledge/done fields and clear interrupts as required.

## State and Persistence Behavior

The header itself has no mutable or persistent state. All state described by this chunk is hardware register state in DPCSSYS CR2/CR3 blocks.

The represented hardware state includes:

- Calibration state: fast RX startup, AFE/DFE/bypass/reference-level/IQ calibration, RX VCO wait/calibration, common MPLL/RCAL done bits, DCC continuous status, phase-2 calibration, and analog MPLL power/calibration timers/status.
- Interrupt state: raw RX/TX event bits, write-to-clear or clear-control bits, and mask state for request/rate/pstate/adaptation/reset/loopback/DCC/TX events.
- Override state: paired value and `*_OVRD_EN` fields can force lane, supervisor, TX, RX, PMA, MPHY, PCS, PLL, clock, charge pump, RTUNE, and analog control signals.
- Power/clock state: CR3 reference clocks, MPLLA/MPLLB div/HDMI clocks, prescaler, MPLL power-control timers, digital clock enable/state, repeater enable, and lane master/shift synchronization fields.
- Link-training and lane state: TX request/ack, detect-RX result, pstate, rate, width, main/pre/post cursor, TX equalization, RX acknowledge/valid/adaptation status, loopback mode, inversion, disable, and low-power controls.

Persistence is limited to the hardware register lifetime. Values may be cleared or reinitialized by GPU reset, display engine reset, DPCS reset, PHY lane reset, power gating, suspend/resume, hotplug, link retraining, or a mode set. Higher-level display code must retain policy state and reprogram these registers when hardware is reinitialized.

## Dependencies

This chunk depends on matching generated address definitions for the same DCN/DPCS generation. The shift/mask macros alone do not identify an MMIO or indirect-register address. They also depend on AMD display register-helper infrastructure that composes offsets, shifts, and masks into register operations.

Semantic dependencies include:

- DCN 4.1.0 DPCS/DPCSSYS hardware register specifications.
- Link encoder and PHY programming code for DisplayPort, HDMI, USB-C/DP-alt-mode, lane power, link training, hotplug recovery, and PHY diagnostics.
- Register-table generation that preserves CR instance and lane prefixes when binding `DPCSSYS_CR2_RAWLANEX`, `DPCSSYS_CR3_SUP`, and `DPCSSYS_CR3_LANE0` symbols.
- Debug/validation paths that inspect OCLA, ATE, PMA/PCS crossing, RTUNE, MPLL, IRQ, and adaptation status fields.

Because these definitions are generated silicon metadata, manual edits are high risk unless they are synchronized with the authoritative register database and all paired offset headers.

## Integration Points

The primary integration point is the macro-name ABI between generated headers and driver code. A consumer naming a field such as `DPCSSYS_CR2_RAWLANEX_DIG_IRQ_CTL_IRQ_MASK__RX_RATE_IRQ_MSK` or `DPCSSYS_CR3_LANE0_DIG_ASIC_TX_ASIC_IN_0__RATE` relies on this file to supply the exact shift and mask for that field.

Important integration surfaces:

- Link training and recovery: fast calibration controls, RX adaptation request/disable interrupts, TX EQ update flags, VCO/MPLL/RCAL status, and TX/RX request/acknowledge fields.
- Power and clock sequencing: supervisor reference clock and MPLL controls, digital clock enable/state, pstate/rate/width fields, TX/RX disable/reset controls, and fast RX power-up/VCO timing fields.
- Protocol and PHY boundary handling: PMA and PCS crossing fields bridge display-link policy with PHY hardware signals, including rate, width, MPLL select, loopback, detect-RX, adaptation, RTUNE, and MPHY behavior.
- Diagnostics and manufacturing test: OCLA, UPCS OCLA, ATE override fields, analog test bus/regulator/RTUNE controls, IRQ masks/clears, and live ASIC/PMA/PCS input/output mirrors.
- Multi-instance correctness: the chunk crosses from CR2 RAWLANEX into CR3 supervisor and CR3 lane 0 symbols, so later merge work must preserve the address-block boundary and not treat all fields as one lane-local block.

## Risks and Failure Modes

- Incorrect shifts or masks can corrupt adjacent control bits in the same 16-bit register, causing failed link training, missed interrupts, stuck calibration, unstable clock recovery, bad TX equalization, or blank display.
- Override-enable fields are especially risky. Leaving `*_OVRD_EN` bits asserted can pin hardware state and defeat normal PHY FSM control, power management, or link-training flows.
- IRQ clear and mask fields have side-effect-sensitive semantics. A wrong mask can hide real link events, repeatedly retrigger interrupts, or clear the wrong condition.
- CR2/CR3 prefix mistakes are plausible because this chunk crosses an address-block marker. Binding a CR3 supervisor or lane 0 field to a CR2 RAWLANEX offset, or vice versa, would produce writes to unrelated hardware.
- Supervisor PLL, charge-pump, bandgap, regulator, RTUNE, and spread-spectrum fields are silicon-sensitive. Bad metadata can create intermittent failures tied to board, cable, sink, link rate, temperature, or power state.
- Lane 0 ASIC fields are structurally repeated elsewhere for other lanes. Copy/paste or generation errors in lane prefixes can show up only for certain lane counts or connector routing.
- Many masks use high bits such as `0x8000L` or full-register masks such as `0xFFFFL`; consumers should keep unsigned-safe register math and avoid assumptions about signed 16-bit temporaries.
- This range starts after earlier CR2 RAWLANEX FSM fields and ends before CR3 lane 0 TX power-control fields, so full per-file conclusions require neighboring chunks.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DCN 4.1.0 display and link/PHY code builds without missing `__SHIFT` or `_MASK` macro names.
- Register-table sanity: generated offsets and field metadata align for `DPCSSYS_CR2_RAWLANEX`, `DPCSSYS_CR3_SUP`, and `DPCSSYS_CR3_LANE0`, including the address-block transition in this range.
- Display link smoke tests: DP and HDMI modes across supported link rates, lane counts, bit depths, hotplug, link retraining, suspend/resume, and GPU reset.
- Link-training diagnostics: TX request/ack, detect-RX result, RX request/rate/pstate/adaptation IRQs, TX EQ update, VCO/MPLL/RCAL done bits, and phase-calibration status.
- Power-management tests: low-power entry/exit, pstate transitions, fast RX power-up/VCO wait/calibration paths, digital clock enable/state changes, and MPLL power-control timer behavior.
- Interrupt tests: mask/unmask and clear RX reset/request/rate/pstate/adaptation, lane mode, loopback, DCC on-demand, TX reset, and TX request events.
- Debug/test coverage: OCLA/UPCS visibility, ATE override operation, PMA/PCS live mirror readback, RTUNE status/readback, analog PLL/regulator status, and lane 0 loopback or repeater/shift synchronization tests.

## Chunk Notes

This chunk begins at `DPCSSYS_CR2_RAWLANEX_DIG_FSM_FAST_SUP` after earlier fast RX calibration definitions and ends at `DPCSSYS_CR3_LANE0_DIG_ASIC_TX_OVRD_OUT_1`. It is a boundary-heavy chunk: it completes several CR2 RAWLANEX subfamilies and starts the CR3 supervisor/lane 0 register map. The final per-file document should reconcile this with neighboring chunks before making whole-file statements about the complete DCN 4.1.0 register header.
