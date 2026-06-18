# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 105126-107594

## Scope

This chunk is a generated AMD DCN 3.2.0 register shift/mask header segment. It contains preprocessor constants only: each hardware field is represented by a `...__SHIFT` macro and a matching `..._MASK` macro. The range covers 2,469 source lines and 2,095 `#define` entries.

The slice starts inside the CR1 `RAWLANE0` RX firmware transfer block, covers the rest of `RAWLANE0` RX interrupt/control/FSM fields, then covers most of the corresponding `RAWLANE1` TX/RX/firmware/FSM fields, and ends at the beginning of `RAWLANE2` TX PCS lane override fields. Although this tree is under `ceph-client`, this source is AMDGPU display hardware metadata, not Ceph filesystem logic.

## Purpose

The purpose of this chunk is to publish bit positions and masks for DCN 3.2.0 C20 PHY CR1 raw-lane digital registers. Driver code includes this file with `dcn_3_2_0_offset.h` so ASIC-specific table initializers can bind register offsets, masks, and shifts to the common AMD display register helper layer.

The constants describe how to pack and unpack lane control, firmware handshakes, interrupt status/clear bits, RX/TX adaptation controls, PMA/PCS transfer signals, firmware scratch/status registers, and calibration bypass controls. They do not execute code, but an incorrect value can still compile and then misprogram physical display-link lanes, interrupt routing, adaptation/margining state, loopback controls, or calibration sequencing.

## Important APIs, Types, And Macros

There are no callable functions, structs, enums, variables, includes, locks, memory allocations, or persistence APIs in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating the field.
- `//C20_PHY_CR1_RAWLANE...` comments: generated register-name markers for the following field definitions.

Major register families in this chunk:

- `C20_PHY_CR1_RAWLANE0_DIG_RX_FW_XF_*`: tail of the rawlane0 RX firmware transfer interface, including TX pre/main/post direction hints, RX clock enables/resets, and ACK output.
- `C20_PHY_CR1_RAWLANE0_DIG_RX_IRQ_CTL_*`: RX interrupt mask/enable/status/clear fields for reset, request, rate, pstate, adapt request/disable, termination control, global margining, IQ margin start, VDAC margin start, margin-error clear, margin init, and margin finish events.
- `C20_PHY_CR1_RAWLANE0_DIG_RX_CTL_*`: rawlane0 RX control and observation fields for termination code, off-cancellation and adaptation continuous status, adaptation mode/selection, PPM drift, CDR detect status, PMA miscellaneous control, adaptation mode override/enables, adaptation figures of merit, reference errors, IQ-left/right adaptation, phase-adjust linear/map controls and update enables, margining deltas/status/error, RX FSM control, rate IRQ ack, and IQ code read/write windows.
- `C20_PHY_CR1_RAWLANE0_DIG_RX_PMA_XF_*`: RX PMA transfer override/input/output fields for ACK, RX-valid override, reset, request, rate/pstate/low-power/width/DFE-bypass controls, and delta-IQ path input.
- `C20_PHY_CR1_RAWLANE0_DIG_FSM_*`: rawlane0 FSM override/control, jump bank, breakpoint, address/status monitor, firmware configuration stage, scratch registers 0-11, CR lock, fast-supervisor and fast TX/RX sequencing controls, skip bits for TX and RX DCC/calibration/adaptation phases, and RX calibration completion status.
- `C20_PHY_CR1_RAWLANE1_DIG_TX_PCS_XF_*`: rawlane1 TX PCS lane transfer and override fields for RX-to-TX parallel loopback, TX-to-RX serial loopback, lane link number, reset/request, pstate/LPD/data enable/invert/clock-ready/beacon/MPLL, rate/width/disable/encoder mode, transmitter pre/main/post cursor values, ACK/RDY output overrides, input mirrors, and context configuration.
- `C20_PHY_CR1_RAWLANE1_DIG_TX_FW_XF_*`: rawlane1 TX firmware transfer fields for reset/request/pstate/LPD/rate/width/tx-disable/encoded-mode, transmitter cursor values, ACK overrides, lane number, and firmware-visible input/output handshakes.
- `C20_PHY_CR1_RAWLANE1_DIG_TX_IRQ_CTL_*`: rawlane1 TX interrupt mask/enable/status/clear fields for rate, reset, request, RX2TX parallel loopback enable/disable, RTUNE, TX termination control, and lane transceiver mode changes.
- `C20_PHY_CR1_RAWLANE1_DIG_TX_CTL_*` and `TX_PMA_XF_*`: rawlane1 TX FSM/clock/off-cancellation/rate-ack/termination/powerup/MPLL restart-calibration controls plus PMA lane/supervisor override/input/output and RTUNE control fields.
- `C20_PHY_CR1_RAWLANE1_DIG_RX_PCS_XF_*`, `RX_FW_XF_*`, `RX_IRQ_CTL_*`, `RX_CTL_*`, `RX_PMA_XF_*`, and `FSM_*`: rawlane1 RX equivalents of the rawlane0 receive PCS/firmware/IRQ/control/PMA/FSM blocks, including adaptation, margining, calibration skip, firmware scratch, and status fields.
- `C20_PHY_CR1_RAWLANE2_DIG_TX_PCS_XF_LANE_OVRD_IN_0`: the first rawlane2 TX PCS lane override register, containing loopback override bits and lane-link-number override.

## Control Flow And Runtime Behavior

The header has no runtime control flow. Runtime behavior is supplied by consumers of the generated register tables:

1. DCN 3.2 code includes `dcn_3_2_0_offset.h` and this shift/mask header.
2. Register list macros paste symbolic register and field names into ASIC-specific table initializers. Offsets come from the offset header; shifts and masks come from this file.
3. Runtime display, DMUB, IRQ, GPIO, clock, memory-controller, and diagnostics paths use AMD register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and `REG_WRITE` through those tables.
4. If a runtime path targets these C20 PHY fields, writes program raw-lane PCS/PMA/FW/FSM/IRQ state and reads decode lane status, IRQ status, adaptation state, calibration status, or firmware scratch values.

Concrete integration in this tree includes `display/dc/resource/dcn32/dcn32_resource.c`, `display/dmub/src/dmub_dcn32.c`, `display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/gpio/dcn32/hw_translate_dcn32.c`, `display/dc/gpio/dcn32/hw_factory_dcn32.c`, `display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, and `amdgpu/gmc_v11_0.c`, all of which include `dcn_3_2_0_offset.h` and/or `dcn_3_2_0_sh_mask.h`. Those files provide the compile-time entry points that pull generated DCN 3.2.0 register metadata into the driver.

The generated header does not define interrupt handlers, calibration algorithms, or link-training policy. It only defines the bit layout those higher-level paths must use when they touch these registers.

## State And Persistence Behavior

The macros hold no software state and persist nothing. They describe stateful hardware registers whose values live in the display PHY until later writes, link retraining, mode set reprogramming, power gating, suspend/resume restore, soft reset, or ASIC reset changes them.

State represented by this chunk includes:

- RX/TX request, reset, ACK, RDY, clock-enable, low-power, data-enable, width, rate, pstate, and lane-number transfer state between PCS/PMA/firmware/FSM agents.
- RX interrupt mask, enable, latched status, and clear state for request/rate/pstate/reset/adaptation/termination/margining events.
- TX interrupt mask, enable, latched status, and clear state for request/rate/reset/loopback/RTUNE/termination/transceiver-mode events.
- RX adaptation and margining state: adaptation mode/selection, figures of merit, reference errors, IQ left/right data, phase-adjust linear/map values, update strobes, IQ and VDAC margin deltas, margin status, and margin error.
- TX electrical/control state: TX pre/main/post cursor fields, termination code, RTUNE controls, MPLL restart calibration controls, and firmware power-up completion.
- FSM debug/control state: override controls, jump bank, breakpoint addresses, monitored addresses/status, firmware stage, scratch registers, CR lock, fast-mode enables, skip bits for calibration/adaptation phases, and RX calibration done status.
- PMA/PCS override state for loopback, pstate, LPD, data enable, inversion, clock readiness, beacon, MPLL, reset/request, and output-valid/ACK forcing.

Many fields are not plain configuration. `*_IRQ` bits may be latched status, `*_IRQ_CLR` bits may be write-one-to-clear or self-clearing strobes, and `*_OVRD_EN` fields alter normal hardware/FW ownership. The generated mask header does not encode access type, ordering, reset values, or whether a field is read-only, sticky, write-one-to-clear, or self-clearing.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which supplies matching register offsets such as the C20 PHY raw-lane register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`, which includes the DCN 3.2 generated headers and builds resource/register metadata for the DCN32 display stack.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`, which exposes selected DCN32 register fields to DMUB service code.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`, which uses the same generated register namespace for DCN32 interrupt handling, even if most PHY-lane IRQ details are consumed by lower-level link/PHY paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c` and `hw_factory_dcn32.c`, which depend on DCN32 generated register metadata for hardware object wiring.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`, which include this ASIC register namespace for clock/display/memory-controller integration.
- Peer generated headers such as `dpcs_4_2_3_sh_mask.h`, which contain nearly identical C20 PHY raw-lane field layouts and are useful for generated-header consistency checks.

The macro names are the compile-time API. Missing or renamed macros usually fail the build when a register table references them. Wrong numeric constants are more dangerous because the build can remain clean while hardware ownership, interrupts, calibration, or PHY lane signaling break at runtime.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the `RAWLANE0_DIG_RX_FW_XF_ADAPT_FOM` register began in the previous chunk and stops immediately after `RAWLANE2_DIG_TX_PCS_XF_LANE_OVRD_IN_0`; the remaining rawlane2 TX PCS fields continue in the next chunk.
- Rawlane0 and rawlane1 contain many structurally repeated RX/FSM definitions. Copy-generation drift between lanes can affect only one lane, creating connector-, lane-, or link-width-specific failures.
- Interrupt fields are sequencing-sensitive. Confusing mask, enable, status, and clear bits can leave RX/TX PHY events unreported, permanently masked, or repeatedly retriggered.
- Override-enable fields transfer control away from normal hardware/FW paths. Incorrect masks for `*_OVRD_EN` or override value fields can wedge reset/request handshakes, force invalid ACK/RDY state, or leave loopback, low-power, pstate, rate, width, data enable, inversion, beacon, or MPLL state under the wrong owner.
- RX adaptation and margining fields affect link quality. Bad masks for adaptation mode, IQ/VDAC margin delta, phase-adjust update, reference-error, FOM, or DFE/CTLE/VGA skip controls can cause marginal links, training failures, or errors that appear only at high rates or under signal-integrity stress.
- Calibration skip and fast-mode bits bypass hardware bring-up work. Incorrect values can pass simple compile tests while causing intermittent display link failures after hotplug, resume, retrain, rate change, or low-power exit.
- Firmware scratch and stage fields are easy to treat as generic storage, but they may be part of a firmware/driver contract. Width or shift errors can corrupt diagnostics or coordination between host driver and PHY firmware.
- Status and clear fields do not carry access semantics in the header. Driver code must know which fields are read-only, write-one-to-clear, sticky, or self-clearing from register specs or established access paths.

## Test Signals

Useful validation combines generated-header consistency checks, build coverage, and hardware behavior:

- Build AMDGPU/DC with DCN32 enabled. Missing or renamed symbols should fail in DCN32 resource, DMUB, IRQ, GPIO, clock-manager, or GMC integration files that include the generated DCN 3.2.0 headers.
- Mechanically verify that every `__SHIFT` macro in lines 105126-107594 has the expected companion `_MASK` macro and that masks align with their shifts and field widths.
- Diff this C20 PHY CR1 raw-lane slice against compatible generated layouts such as `include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h`, and against neighboring DCN ASIC revisions where lane PHY layout parity is expected.
- Exercise display hotplug, link training, link retraining, suspend/resume, low-power entry/exit, and rate/width changes on DCN32 hardware with multiple connectors and lane counts.
- Validate high-rate links and marginal-signal scenarios where RX adaptation, DFE/CTLE/VGA, IQ/phase adjustment, CDR detect, PPM drift, and margining fields are active.
- Exercise loopback, RTUNE, termination, MPLL restart calibration, and PMA/PCS override diagnostics where available.
- Monitor kernel logs and hardware status for PHY IRQ storms, missed link-training events, stuck reset/request/ACK handshakes, calibration timeout, margining errors, CDR detection failures, display underflow, hotplug regressions, or resume-only link failures.
- If PHY firmware diagnostics expose scratch/stage/status registers, confirm the decoded values match expected firmware progress through reset, startup calibration, continuous adaptation, and power-up phases.

## Cross-Chunk Notes

The previous chunk should be consulted for the beginning of the rawlane0 RX firmware transfer block, including the fields immediately before `TXPRE_DIR`. This chunk completes rawlane0 RX/FSM coverage and covers most of rawlane1 TX/RX/FSM coverage. The next chunk owns the rest of rawlane2 TX PCS and later rawlane2/rawlane3 fields. The final per-file report should merge adjacent chunks before making complete claims about the full C20 PHY raw-lane namespace.
