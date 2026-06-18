# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 33983-36433

## Chunk Scope

This chunk is part of the generated AMD DPCS 4.2.3 register shift/mask header. It contains C preprocessor constants only: each register field has a `__SHIFT` macro and, when the field has an explicit bit mask in this header slice, a matching `_MASK` macro. There are no functions, structs, executable statements, or storage declarations in this chunk.

The slice starts inside `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_TXRX_TERM_CTRL_OVRD_IN`, covers the remaining RAWLANE2 CR1 digital PCS/FSM/IRQ/PMA/CTL groups, covers the full RAWLANE3 CR1 digital lane group from PCS transfer registers through PMA and lane control registers, then enters the RAWAONLANE0 always-on analog/digital calibration register block and the beginning of RAWAONLANE1. The final line is only the comment header for `DPCSSYS_CR1_RAWAONLANE1_DIG_INIT_PWRUP_DONE`; its fields are outside this chunk.

## Purpose

The macros describe how software should pack and unpack bitfields in DPCS indirect registers for the DCN 3.1.6 display resource path. The paired offset header `dpcs_4_2_3_offset.h` supplies `ix...` register indices, while this file supplies bit positions and masks for fields within those 16-bit DPCS register payloads. Display code can combine these constants with AMD register helpers to set or read PHY lane state without embedding magic bit numbers in C logic.

The hardware areas represented here are:

- RAWLANE2 tail: RX/TX termination, RX equalization override, phase-2 calibration, FSM observation/override, fast calibration flags, interrupt status/mask/clear bits, PMA bridge controls, TX/RX controller status, and ATE override registers.
- RAWLANE3 full digital lane block: TX/RX PCS request, reset, pstate, link width/rate, MPLL selection/enables, adaptation controls, loopback, termination, equalization, phase calibration, FSM controls, interrupts, PMA handoff, MPHY/PWM controls, and lane TX/RX controller controls.
- RAWAONLANE0 analog/always-on block: adaptation readbacks, DFE/CTLE/VGA/ATT offsets, phase adjust values, MPLL coarse tune, power-up flags, fast calibration flags, adaptation control words, signal-detect filters and codes, DCC calibration codes, TX DCC bank access, firmware configuration words, and lane transceiver mode fields.
- RAWAONLANE1 beginning: mirrors the first analog/adaptation offset and readback registers for the next always-on lane.

## Important APIs, Types, and Macros

There are no typed APIs. The exported surface is the macro namespace:

- `DPCSSYS_CR1_RAWLANE2_DIG_*__FIELD__SHIFT` / `_MASK`: tail of lane 2 CR1 digital register definitions. Important groups include `DIG_FSM_*`, `DIG_IRQ_CTL_*`, `DIG_PMA_XF_*`, `DIG_TX_CTL_*`, `DIG_RX_CTL_*`, and `DIG_PCS_XF_ATE_*`.
- `DPCSSYS_CR1_RAWLANE3_DIG_PCS_XF_*`: PCS transfer and override fields for lane 3. These include TX and RX override inputs/outputs, raw PCS inputs/outputs, RX adaptation status/FOM, TX pre/main/post direction hints, lane number, reserved registers, ATE overrides, equalization override fields, termination control, and phase-2 calibration request/acknowledge.
- `DPCSSYS_CR1_RAWLANE3_DIG_FSM_*`: lane 3 FSM override/status/fast calibration fields. `FSM_FSM_OVRD_CTL` exposes jump address, jump enable, command start, override enable, and break bits. `FSM_STATUS_MON` exposes state, command-ready, ALU flags, wait-counter, and read/write mask-disable indicators. The numerous `FSM_FAST_*` registers are single-bit fast-path calibration or adaptation gates/status fields.
- `DPCSSYS_CR1_RAWLANE3_DIG_IRQ_CTL_*`: per-lane interrupt status and clear bits for RX reset/request/rate/pstate/adaptation, phase-2 calibration, lane loopback, DCC on-demand, TX reset/request, plus `IRQ_MASK` and `IRQ_MASK_2` fields controlling which events are masked.
- `DPCSSYS_CR1_RAWLANE3_DIG_PMA_XF_*`: PMA transfer bridge fields for MPLL lane enables, supervisor state, TX/RX request/reset/beacon/async/data-enable overrides, loopback, RTUNE request/ack, MPHY PWM/termination controls, and RX adaptation phase-adjust override output.
- `DPCSSYS_CR1_RAWLANE3_DIG_TX_CTL_*` / `DIG_RX_CTL_*`: lane-local controller fields for TX FSM timing, RX-detect allowances by power state, TX clock select/enable and async beacon wait, DCC continuous status, OCLA/UPCS debug visibility, RX FSM enable/rate-change behavior, LOS mask count, RX data-enable override timing, and continuous off-cancel/adaptation status.
- `DPCSSYS_CR1_RAWAONLANE0_DIG_*`: always-on lane 0 analog calibration and readback fields. Key groups include DFE data/ref/phase offsets, RX adaptation values (`RX_ADPT_*`, `RX_ADAPT_DONE`, `RX_ADAPT_FOM`), fast calibration flags, lane common-calibration status, signal detect calibration/filtering, DCC calibration codes, TX DCC bank address/data/continuous enable, firmware config words, and lane transceiver mode override/input.
- `DPCSSYS_CR1_RAWAONLANE1_DIG_*`: beginning of the same always-on lane pattern for lane 1, through `MPLLB_COARSE_TUNE`; `INIT_PWRUP_DONE` is only introduced by a comment at the chunk boundary.

All masks in this chunk use `L` integer constants and mostly fit 16-bit payloads, for example `0xFFFFL`, `0x8000L`, or narrower masks such as `0x03FFL`. The generated pattern is field-local and does not define composed values or enums for legal field values.

## Control Flow

This chunk has no runtime control flow. Control behavior is implicit in hardware protocols represented by the fields:

- Request/acknowledge pairs appear throughout TX/RX PCS and PMA transfer registers, such as `REQ`, `ACK`, `RESET`, `RX_ADAPT_ACK`, `LANE_RTUNE_REQ`, and `RTUNE_ACK`.
- Override registers usually split into value and enable bits, for example `*_OVRD_VAL` plus `*_OVRD_EN`. Driver code must set both appropriately when forcing a hardware path and should clear enable bits when returning to autonomous hardware control.
- Interrupt handling uses status-like macros and matching clear macros. For lane 3 this chunk defines RX/TX reset/request, RX rate/pstate, adaptation request/disable, phase-2 calibration request/disable, loopback, DCC on-demand, and the mask registers.
- FSM control fields expose a debug/override path: jump address, command start, override enable, and break. Runtime code that uses these fields is effectively commanding a hardware micro-FSM, but that sequencing is not implemented in this header.

## State and Persistence

The state described by these macros lives in DPCS hardware registers, not in kernel memory. Values persist according to hardware register lifetime: they may survive until reset, power-gate, link reinitialization, or a later register write, depending on the register block. The header itself contributes no persistent storage.

State categories visible in this chunk include:

- Lane mode and link parameters: pstate, low-power detect, width, rate, MPLL selection/enables, master MPLL state, and lane transceiver mode.
- Calibration and adaptation state: RX AFE/DFE/CTLE/VGA/ATT values, DFE taps, IQ/phase-adjust values, reference levels, signal detect thresholds/codes, VCO/ref load values, DCC calibration code banks, and fast calibration flags.
- Handshake/interrupt state: request, acknowledge, reset, valid, interrupt, clear, and mask bits.
- Debug and test state: ATE override controls, loopback enables, OCLA/UPCS debug visibility, firmware configuration words, and reserved registers.

Reserved masks are explicitly emitted for many registers. Writers should preserve reserved bits unless the documented hardware programming sequence says otherwise.

## Dependencies and Integration Points

The direct include site found in this tree is `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both `dpcs/dpcs_4_2_3_offset.h` and this shift/mask header. That resource file sets up DCN 3.1.6 display resources and needs DPCS register definitions for the display link PHY programming tables and helper macros used elsewhere in the AMD display stack.

This header depends on:

- The matching offset header, especially `ixDPCSSYS_CR1_RAWLANE3_*` and `ixDPCSSYS_CR1_RAWAONLANE0_*` definitions. For example, RAWLANE3 PCS/FSM/IRQ/PMA offsets in the paired header span roughly `0x3300` through `0x33c8`, and RAWAONLANE0 begins at `0x4000`.
- AMD DC register access conventions that combine register offsets, base instances, shifts, and masks. Those helpers are outside this chunk, but the naming convention is compatible with generated `REG_FIELD`, `REG_SET`, `REG_GET`, and table-style register programming patterns used in AMD display code.
- Hardware documentation or generator input for DPCS 4.2.3. The comments and macro names are generated register descriptions, not hand-written semantic documentation.

Neighboring generated headers for DPCS 3.1.4, 4.2.0, 4.2.2, and DCN 4.1.0 contain closely matching symbols. That makes cross-generation comparisons useful for detecting accidental generator drift, but also raises the risk of using a same-named field from the wrong ASIC generation.

## Risks and Maintenance Notes

- The chunk begins mid-register. The first visible lines are the masks for `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_TXRX_TERM_CTRL_OVRD_IN`; the corresponding shifts are immediately before the chunk start. Any merged file-level report must account for the boundary.
- These are generated hardware constants. Manual edits are high risk because a single bad mask or shift can misprogram a display PHY lane, affecting link training, signal integrity, hotplug/retrain behavior, or display stability.
- Many registers use value/enable override pairs. A caller that sets an override value without the enable bit, or leaves an enable bit asserted after diagnostics, can get misleading behavior.
- Interrupt clear fields are separate from interrupt status fields. Writing the wrong register or mask could lose edge/level events or leave an interrupt stuck.
- RAWLANE2, RAWLANE3, RAWAONLANE0, and RAWAONLANE1 names are visually similar. Copy/paste mistakes between lane numbers are plausible and may only show up on specific connectors or lane mappings.
- Reserved field macros are present and easy to accidentally include in writes. Register writes should mask and preserve reserved bits unless the programming guide requires a whole-register write.
- Some fields are calibration or factory/test oriented (`ATE`, `DCC`, `OCLA`, firmware config, raw analog offsets). They should be treated as hardware-sequence sensitive and may require strict ordering or link-idle conditions even though this header cannot express those constraints.

## Test Signals

Useful validation signals for changes involving this chunk include:

- Compile coverage for DCN 3.1.6 resource code that includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Static checks that every referenced `DPCSSYS_CR1_RAWLANE3_*` or `RAWAONLANE*` shift/mask macro matches a corresponding `ix...` register offset in `dpcs_4_2_3_offset.h`.
- Cross-generation diffing against nearby generated headers (`dpcs_4_2_0`, `dpcs_4_2_2`, `dpcs_3_1_4`, and `dcn_4_1_0`) to distinguish intentional ASIC changes from formatting or generator mistakes.
- Hardware/display smoke tests: boot with affected AMD ASIC, enumerate connectors, train DisplayPort/USB-C links at multiple rates and lane widths, suspend/resume, hotplug, mode-set repeatedly, and verify no link-training, IRQ storm, or blank-screen regressions.
- Diagnostics around RX adaptation and signal detect: monitor adaptation done/ack/FOM, LOS mask behavior, DCC continuous status, and interrupt clear/mask behavior when exercising link retraining or low-power transitions.
