# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 151481-153891

## Purpose

This chunk is a generated ASIC register bitfield mask/shift section for DCN 3.2.0 C20 PHY CR2 lane digital and raw-lane PHY blocks. It does not define executable code. Instead, it exports preprocessor constants that let AMDGPU DCN driver code compose, update, and decode 16-bit register fields without hard-coded bit positions.

The covered range starts in the receive CDR/DPLL lane block, then moves through receive adaptation, statistics, IQ correction, analog receive transfer/override registers, raw-lane TX PCS/FW/IRQ/control/PMA interfaces, and raw-lane RX PCS/FW/IRQ/control interfaces. These constants are intended to be paired with register address definitions from the same ASIC register family and with AMDGPU register access helpers/macros that shift and mask field values.

## Important APIs, Types, And Definitions

There are no functions, structs, enums, storage objects, or runtime APIs in this chunk. The public surface is the macro namespace:

- `C20_PHY_CR2_LANEX_DIG_RX_*__...__SHIFT` and `..._MASK` constants for lane-indexed RX CDR, DPLL, adaptation, statistics, IQ correction, and analog-facing controls.
- `C20_PHY_CR2_RAWLANEX_DIG_TX_*__...__SHIFT` and `..._MASK` constants for raw-lane TX PCS, firmware handoff, IRQ, control FSM, clock, termination, MPLL calibration, and PMA transfer controls.
- `C20_PHY_CR2_RAWLANEX_DIG_RX_*__...__SHIFT` and `..._MASK` constants for raw-lane RX PCS, firmware handoff, IRQ, adaptation, margining, termination, CDR status, and PMA miscellaneous controls.

Each register field appears as a pair: one `__SHIFT` value naming the least-significant bit position and one `_MASK` value naming the unshifted register mask. Reserved fields are represented explicitly, which is useful for generated table consistency but should generally not be written by functional code.

## Register Groups Covered

The first block covers RX clock recovery and adaptation state:

- CDR/DPLL fields include `PHUG_VALUE`, `FRUG_VALUE`, `VAL`, `FREQ_BOUND_EN`, `UPPER_FREQ_BOUND`, and `LOWER_FREQ_BOUND`.
- Adaptation configuration registers `ADPT_CFG_0` through `ADPT_CFG_12` describe ASM1 timing, test pattern generation, CTLE/VGA/ATT/DFE enable bits, adaptation thresholds, mu/step controls, saturation limits, and initial slicer/error levels.
- Reset and status registers expose per-subsystem resets and adaptation results: `RST_ADPT_ATT`, `RST_ADPT_VGA`, `RST_ADPT_CTLE_BOOST`, DFE tap resets, `ATT_ADPT_CODE`, `VGA_ADPT_CODE`, CTLE and DFE tap status, `ASM1_DONE`, and FSM state fields.
- DFE and slicer offset registers capture even/odd data, error, and bypass VDAC offsets and slicer control levels.
- DCC offset registers provide `VAL` plus `OVRD_EN` fields for phase/data/bypass differential and common-mode IDAC offsets.
- SSM registers configure scan/search behavior with threshold offset, DAC selection, destination selection, step counts, initial DAC code, wait periods, direction, sticky/LPF bypass behavior, and final code/status fields such as `SSM_DONE`, abort causes, and FSM state.

The RX statistics and IQ-correction region supplies counters and finite-state status:

- Statistic control fields define load values, masks, match controls, statistic mode, sample counters, stop control, and shadow counter values.
- `CAL_COMP_CLK_CTL` controls compensation clock behavior.
- IQ correction fields include reset adjustment, `STEP_SIZE`, jump divider bits, bypass/data enables, `USE_DFE_BYPASS`, and `RX_IQC_FSM_STATE`.

The analog RX transfer (`ANA_XF_RX`) section is the largest lane-indexed group in this chunk:

- Override-out registers control analog clock enable, data rate, dividers, DFE/bypass enables, async reset, AFE/CDR/deserializer power, fast-start, clock/VREG/DCC enables, signal-detect calibration, VCO startup/config/frequency tuning, calibration muxes, VDAC ranges, DAC control, and termination code override.
- Override-in/status registers expose AFE override inputs, analog scope/slicer controls, IQ controls, loopback, AFE update enables, sample selections, status outputs, and status inputs.
- `ANA_CREG00` through `ANA_CREG11` provide compact 16-bit control/status fields for analog calibration and debug, including calibration VREF, BIAS/VREG trims, CDR/VCO measurement taps, loopback selection, signal-detect controls, DFE/deserializer enables, termination gates, ATB measurement selection, and scope range fields. `ANA_CREG0_OVRD` and `ANA_CREG1_OVRD` are all-reserved in this slice.

The raw-lane TX region defines PCS, firmware, IRQ, control, and PMA transfer fields:

- TX PCS lane fields control RX-to-TX parallel loopback, TX-to-RX serial loopback, lane link number, reset/req handshakes, P-state/LPD/data/invert/clock-ready/beacon/MPLL states, master MPLL state, detector request, clock and lane deskew, recalibration force/skip, context selection, ack/detect result, rate/width/context configuration, and voltage/pre-emphasis/main/post settings.
- TX firmware fields mirror override/input/output handshakes and lane number values used for firmware-mediated lane management.
- TX IRQ fields include masks, enable flags, one-bit pending registers, and clear registers for rate, reset, request, loopback enable/disable, RTUNE, term-control, and lane transceiver mode events.
- TX control fields configure the TX FSM, clock select, off-canonical continuous status, rate IRQ acknowledgement, termination code, firmware power-up done, and MPLLA/MPLLB resistor calibration enables.
- TX PMA transfer fields cover lane MPLLA/MPLLB override input/output, PMA supervisor state, request/reset handshakes, RTUNE request/ack, and PMA supervisor inputs.

The raw-lane RX region defines corresponding PCS, firmware, IRQ, and control fields:

- RX PCS override/input fields control reset/req, P-state, low-power detect, data enable, invert, CDR SSC enable, adaptation request/in-progress, margin IQ/VDAC values, margin error clear, recalibration controls, bank selection, loopback selection, context selection, ack outputs, and rate/width/context configuration.
- RX firmware fields expose override/input/output handshakes, adaptation acknowledge/FOM, TX pre/main/post direction hints, and clock control fields.
- RX IRQ fields include aggregate mask and enable registers plus one-bit pending/clear registers for reset, req, rate, P-state, adapt request/disable, termination control, margin IQ start, margin VDAC start, margin error clear, margin init, margin finish, and margin global events.
- RX control fields expose termination code, continuous offset/adaptation status enables, adaptation mode/select, PPM drift and valid bit, CDR detect state, PMA miscellaneous controls such as `RX_CDR_TRACK_EN` and `RX_DFE_TAP1_ADAPT_OVRD_EN`, adaptation mode override enables, adaptation mode enable, and the beginning of `RX_ADAPT_MM_FOM` at the chunk boundary.

## Control Flow

There is no local control flow. At compile time, these macros are substituted into register read/write expressions elsewhere in the AMDGPU DCN stack. Runtime control flow is owned by callers that decide when to program training, adaptation, power, IRQ, margining, loopback, or firmware handshake registers.

The visible protocol implied by naming is register-driven:

- Writers set `*_OVRD_EN` alongside override values when firmware or driver code must take control from hardware sequencers.
- Handshake style fields use request/ack pairs such as `REQ`, `ACK`, `TX_RATE_IRQ_ACK`, RTUNE request/ack, and firmware power-up done.
- IRQ fields are split into mask registers, enable flags, pending status bits, and clear bits. Correct caller flow is normally mask/enable, observe pending bit, perform associated service, then write the matching clear/ack bit.
- Adaptation/margin flows include start/request fields, in-progress/done/status fields, error-clear fields, and final code/FOM fields.

## State And Persistence Behavior

The macros themselves have no state and do not persist anything. The state they describe lives in hardware MMIO/register space and is scoped to PHY lane/register instances. Many fields are hardware-latched or status-like, including adaptation codes, FSM states, IRQ pending bits, PPM drift validity, margin completion, and CDR detect state. Other fields are controls that persist in hardware registers until reset, power transition, firmware reprogramming, or driver writes update them.

Because this is a generated mask header, persistence correctness depends on callers preserving reserved bits and unrelated fields during read-modify-write operations. Writing full 16-bit values without masking can corrupt adjacent control or reserved fields.

## Dependencies And Integration Points

This chunk depends on the surrounding generated register address header and on AMDGPU/DCN helper macros that apply `SHIFT` and `MASK` values. Typical integration points are:

- DCN PHY/link initialization code that configures CDR/DPLL, analog RX, TX/RX PCS, and PMA control fields.
- Link training, rate-change, lane power-state, and DisplayPort/PHY bring-up paths that use PCS/FW handshake fields.
- Firmware handoff code that observes or overrides `*_FW_XF_*` registers.
- IRQ handling paths that use the raw-lane TX/RX IRQ mask, enable, status, clear, and acknowledge fields.
- Diagnostics, margining, calibration, and link-quality tooling that reads status/FOM/counter fields or programs margin IQ/VDAC and SSM/IQC controls.

The constants use the C preprocessor only; there are no include-time dependencies visible in this chunk beyond conventional inclusion from AMDGPU DCN source files.

## Risks And Edge Cases

- Generated field accuracy is critical. A wrong shift or mask can silently program the wrong PHY bit, causing link training failures, display blanking, unstable high-rate links, or broken power transitions.
- Several registers contain adjacent value and override-enable fields. Setting an override value without the matching enable, or leaving an enable asserted after training/debug, can create hard-to-debug lane behavior.
- IRQ handling requires using the correct pending/clear pair. Clearing the wrong one-bit register can leave interrupts asserted or lose a transition.
- Reserved fields are explicit and wide in many registers. Driver code should preserve them through read-modify-write helpers and avoid using reserved macros as functional controls.
- Boundary risk: this chunk starts in the middle of `C20_PHY_CR2_LANEX_DIG_RX_CDR_CDR_CTL_4` and ends before the full `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_ADAPT_MM_FOM` mask pair is visible. The merge lane must combine adjacent chunks for complete per-register coverage.
- Names are long and mechanically similar across TX/RX, PCS/PMA/FW, and status/clear registers. Copy/paste mistakes between `LANEX` and `RAWLANEX`, TX and RX, or pending and clear macros are a realistic integration risk.

## Test Signals

Useful validation signals for changes touching this generated area include:

- Build coverage for AMDGPU DCN sources that include `dcn_3_2_0_sh_mask.h`, catching missing or malformed macro names.
- Static checks that every functional field has matching `__SHIFT` and `_MASK` definitions and that masks match the declared bit width/shift.
- Link bring-up and mode-set tests across lanes and rates, especially rate changes that exercise DPLL/CDR, PCS context configuration, and TX/RX IRQ paths.
- DisplayPort compliance or hardware validation tests for link training, margining, loopback, CDR tracking, PPM drift reporting, and adaptation/margin IRQ handling.
- Register readback tests on supported ASICs to verify that write helpers preserve reserved bits and that override enable/value pairs take effect as expected.
- Suspend/resume and power-state transition tests that cover AFE/CDR/deserializer power, MPLL calibration, firmware power-up done, and lane reset/request/ack handshakes.
