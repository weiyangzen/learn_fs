# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 73541-76006

## Purpose

This chunk is a generated AMD DCN 3.2.0 shift/mask register metadata slice for C20 PHY CR0 raw-lane digital control registers. It contains only preprocessor constants of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`; there are no functions, structs, enums, or executable control flow. The constants are consumed by AMDGPU/DC register access helpers to compose and decode MMIO values for DisplayPort/PHY lane control, interrupt handling, firmware handshakes, calibration, adaptation, and lane-state overrides.

The range starts inside `C20_PHY_CR0_RAWLANE1_DIG_RX_IRQ_CTL_IRQ_MASK`, so the first few low-bit shift definitions for that register are outside this chunk. It then covers the rest of raw lane 1 RX IRQ, RX control, RX PMA interface, and FSM metadata; all of raw lane 2 TX PCS/FW/IRQ/control/PMA, RX PCS/FW/IRQ/control/PMA, and FSM metadata; and it ends inside the raw lane 3 TX PCS override input family after the first masks for `C20_PHY_CR0_RAWLANE3_DIG_TX_PCS_XF_OVRD_IN_1`.

## Register Families Covered

Raw lane 1 RX interrupt/control coverage includes:

- `DIG_RX_IRQ_CTL_IRQ_MASK` and `IRQ_EN_FLAGS`, with mask/enable fields for RX request, rate, pstate, adapt request/disable, reset, termination control, and RX margining events.
- One-bit RX IRQ status and clear registers for reset, request, rate, pstate, adapt request/disable, termination control, margin IQ start, margin VDAC start, margin error clear, margin init, margin finish, and global margin events.
- RX control/status fields for termination code, off-channel/adaptation continuous status, adaptation mode and select, PPM drift, CDR detection, PMA miscellaneous control, adaptation mode override/enable, adaptation figures of merit, reference error, IQ left/right adjustment, phase adjustment linear/map update, margin IQ/VDAC delta, margin status/error, FSM control, rate IRQ ack, IQ code read/write, and phase adjustment update enable.
- RX PMA interface fields for PMA-to-digital outputs and digital-to-PMA override inputs, including pstate/LPD/reset/request/enable style controls.

Raw lane 1 FSM coverage includes:

- General FSM override and control registers such as `FSM_OVRD_CTL`, `FSM_JMP_BANK`, `FSM_CTL_0`, memory breakpoints, memory address/status monitors, firmware config stage, firmware scratch registers 0-11, CR lock, and fast supervisor controls.
- Fast-path controls for TX common mode, TX RXDET, TX startup calibration, TX power-up, RX startup calibration, RX adaptation, RX power-up, VCO wait/calibration, RX continuous calibration/adaptation, and RX continuous adaptation.
- Skip controls for TX DCC rate/startup/continuous/range calibration and a long list of RX startup, continuous, rate, range, adaptation, DCC, IQ, AFE, DFE, phase, signal detect, VGEN, half/full-rate, bypass, VGA, CTLE, ATT, and margining calibration/adaptation steps.
- `RX_CAL_STATUS`, exposing the reset calibration done bit.

Raw lane 2 is the largest part of the chunk and repeats the same generated pattern for both transmit and receive sides:

- TX PCS interface fields: lane loopback/link-number inputs, reset/request/pstate/LPD/data enable/invert/clock ready/beacon/MPLL controls, TX pre/main/post cursor controls, EIE/idle/width/rate/divider/PCS-to-PMA routing fields, output status, and context configuration values for clock source, width, scramble, lane number, fast training pattern, and BIST controls.
- TX firmware interface fields: firmware override input/output bits, lane number, request/rate/pstate/data enable/invert/detect/link/ripple controls, TX pre/main/post values, calibration busy/done state, response, and acknowledgement/status outputs.
- TX interrupt control fields: reset return request, IRQ mask and enable flags, one-bit status/clear pairs for TX rate, reset, request, RX-to-TX parallel loopback enable/disable, RTUNE, TX termination control, and lane transceiver mode.
- TX control and PMA fields: TX FSM control for clock readiness, reset/request/pstate, rate, data path width, MPLL enable, loopback, termination, PLL, calibration, and lane mode; clock control; off-channel status; rate IRQ ack; termination code; firmware power-up done; MPLLA/MPLLB resistor calibration controls; PMA lane override/status; supervisor interface fields; RTUNE controls; and PMA output/input registers.
- RX PCS interface fields: reset/request/pstate/LPD/data enable/invert/rate/width/divider/termination, margining, CDR/DFE/adaptation status, RX/TX loopback, CDREN, PHY ready, context configuration for clock source, width, divider, lane/PCS mapping, path enable, decode/lock behavior, fast training pattern, EQ/encoding settings, and CDREN override behavior.
- RX firmware interface fields: reset/request/rate/pstate/adaptation controls, adaptation mode/select, termination, margining, reference error, TX coefficient direction hints, clock control, adapt acknowledgement/FOM, and firmware output status.
- RX interrupt/control/PMA/FSM fields: a lane 2 copy of the RX IRQ status/clear, RX adaptation/margin/phase/IQ control, RX PMA interface, and FSM override/fast/skip/calibration status registers described above for lane 1.

The final lines enter raw lane 3 TX PCS metadata, covering lane override input 0, lane input 0, override input 0, and the beginning of override input 1. The lane 3 override fields mirror earlier lane controls: parallel/serial loopback, lane link number, reset/request, pstate, low-power detect, data enable, invert, clock ready, beacon enable, and MPLL enable override fields.

## APIs, Types, and Functions

This header chunk exposes a macro-only API:

- `*_SHIFT` constants provide the least-significant bit position for a named register field.
- `*_MASK` constants provide the register-positioned bit mask, usually with an `L` suffix.
- Single-bit control/status/clear registers commonly use field mask `0x0001L` and reserved mask `0xFFFEL`.
- Packed multi-bit fields appear for lane link numbers, pstate, rate, width, divider, TX pre/main/post coefficients, adaptation modes, figures of merit, phase/IQ codes, reference errors, FSM banks/program counters, firmware stage, and BIST/context settings.

Consumers are expected to include this alongside the matching DCN 3.2.0 register address header. The AMD display register helpers typically use these constants to shift field values into place, mask read-modify-write operations, decode latched status bits, and write one-bit clear or ack fields.

## Control Flow and State

There is no direct runtime control flow in this chunk. Runtime behavior is defined by driver or firmware code that writes and reads the MMIO registers represented here.

The main hardware flows represented by these masks are:

- Interrupt flow: mask/enable fields control which lane events interrupt firmware/driver paths; status bits latch events; matching `*_CLR` fields clear the latched state; `RATE_IRQ_ACK` and TX/RX request/reset bits participate in request/ack handshakes.
- TX lane bring-up and mode control: PCS/FW/PMA override inputs can force reset, request, pstate, low-power detect, data enable, invert, clock ready, beacon, MPLL, rate, width, loopback, and coefficient values. Status/output registers report resulting request, rate, pstate, idle, detection, calibration, termination, and lane-mode state.
- RX lane adaptation and margining: RX controls expose adaptation mode/select/enable, continuous/off-channel state, CDR detection, reference error, IQ and phase adjustment values, margining deltas, margin status/error, TX coefficient direction hints, and interrupt events around margining phases.
- FSM sequencing: fast and skip controls alter firmware/hardware calibration sequence execution for TX DCC and RX AFE/DFE/IQ/DCC/phase/VGA/CTLE/ATT/margining steps. Breakpoint, monitor, scratch, and CR lock fields support low-level firmware or bring-up diagnostics.

State is held in hardware registers, not in kernel-owned persistent data structures. Written control bits persist until changed, reset, power-gated, or overwritten by firmware/hardware. Status and IRQ fields may be read-only, sticky, write-one-to-clear, or handshake-driven according to the silicon specification; this `_sh_mask` file documents only positions and masks, not access policy.

## Dependencies and Integration Points

This generated header depends only on the C preprocessor, but it is tightly coupled to the matching DCN 3.2.0 register address definitions and to AMDGPU display register accessor macros. The register naming convention carries the hardware topology: `C20_PHY_CR0`, `RAWLANE1`, `RAWLANE2`, `RAWLANE3`, and sub-blocks such as `DIG_TX_PCS_XF`, `DIG_TX_FW_XF`, `DIG_TX_IRQ_CTL`, `DIG_TX_CTL`, `DIG_TX_PMA_XF`, `DIG_RX_PCS_XF`, `DIG_RX_FW_XF`, `DIG_RX_IRQ_CTL`, `DIG_RX_CTL`, `DIG_RX_PMA_XF`, and `DIG_FSM`.

Important integration points include:

- Display PHY/link training code that programs lane width, rate, pstate, reset/request handshakes, clock readiness, MPLL enable, and TX coefficient controls.
- RX adaptation and margining flows used during link training, diagnostics, equalization, and signal-integrity validation.
- Firmware-assisted PHY management through the TX/RX firmware exchange registers and scratch/config-stage fields.
- Interrupt handling paths for TX/RX rate/reset/request, loopback, termination, transceiver mode, RX adaptation, and RX margining events.
- PMA and PCS boundary controls where digital lane state is translated to physical analog lane behavior.
- Low-level hardware validation and bring-up tooling that may use breakpoint, status monitor, scratch, skip, and fast-mode fields to shorten or inspect calibration sequences.

## Risks

The main risk is silent hardware misprogramming if a generated shift or mask is wrong or used with the wrong lane/register family. These macros are often used in read-modify-write sequences; an incorrect mask can corrupt reserved or adjacent fields, leave a lane stuck in reset, force an unintended pstate/rate, misconfigure TX coefficients, or suppress required interrupts.

The range contains repeated lane families that look mechanically identical but should not be treated as interchangeable without checking the exact macro name. Lane 1 in this chunk covers only RX/FSM tail content, lane 2 covers both TX and RX in full for this slice, and lane 3 starts only at TX PCS. A merge or analysis pass should preserve those chunk boundaries.

Interrupt fields have separate mask, enable, status, clear, and ack concepts. Confusing `IRQ_MASK`, `IRQ_EN_FLAGS`, one-bit status registers, and `*_CLR` registers can lead to either unhandled events or destructive writes that clear diagnostics before they are sampled.

FSM skip and fast controls are especially sensitive. They can bypass analog or digital calibration stages such as DCC, AFE, DFE, IQ, phase, VGA, CTLE, ATT, and margining. These fields are useful for bring-up and firmware flows, but unsafe defaults or incorrect override use can cause marginal links, training failures, or intermittent display loss.

The chunk begins and ends in partial register groups. The opening `RAWLANE1_DIG_RX_IRQ_CTL_IRQ_MASK` lacks its earlier low-bit shift definitions in this document, and the closing `RAWLANE3_DIG_TX_PCS_XF_OVRD_IN_1` lacks the rest of its masks. Final per-file reconciliation should join adjacent chunks before making complete claims about those registers.

## Test Signals

Useful validation signals for changes touching consumers of this metadata include:

- Compile coverage for DCN 3.2 AMDGPU display paths, because missing or renamed macro fields should fail at build time.
- Register trace comparison against AMD DCN 3.2 specifications or known-good traces for lane 1/2/3 C20 PHY CR0 accesses, especially read-modify-write masks and reserved-bit preservation.
- DisplayPort link training on DCN 3.2 hardware, including rate changes, pstate transitions, lane width changes, TX coefficient updates, MPLL readiness, CDR lock, and RX adaptation completion.
- Hotplug, modeset, suspend/resume, and power-state transition tests that exercise lane reset/request handshakes and restoration of PCS/FW/PMA/FSM controls.
- IRQ-path tests for TX/RX rate/reset/request, loopback enable/disable, RTUNE, termination control, lane transceiver mode, RX adaptation request/disable, and RX margining start/error/init/finish/global events.
- PHY margining and equalization diagnostics that inspect IQ/phase adjustment, reference error, adaptation FOM, margin status/error, and TX pre/main/post direction/value fields.
- Hardware bring-up tests that deliberately enable/disable FSM fast or skip bits only under controlled conditions, then verify calibration done/status bits and stable link behavior.
