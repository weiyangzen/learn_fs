# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 144247-145870

## Purpose

This chunk is the final DCN 4.1.0 generated shift/mask metadata for DisplayPort PHY lane control registers. It contains only C preprocessor constants. Each register field is represented as a `__SHIFT` value and a `_MASK` value so AMD display code can build register writes and reads without embedding raw bit positions in functional code.

The covered range is centered on `DPCSSYS_CR3` lane and raw-lane registers:

- `DPCSSYS_CR3_LANEX_DIG_ANA_*` digital-to-analog override outputs for RX signal detect and TX DCC DAC calibration.
- `DPCSSYS_CR3_LANEX_ANA_TX_*` analog TX lane controls for measurement, power override, alternate bus/debug routing, ATB measurement points, DCC DAC programming, termination code, clock override, misc drive/control fields, mux selection, VREG controls, and reserved analog fields.
- `DPCSSYS_CR3_LANEX_ANA_RX_*` analog RX controls for clocks, CDR/deserializer behavior, slicer control, power sequencing, squelch, calibration, ATB/regref measurement, VDAC ranges, CDR/VREG settings, and RX VREG controls.
- `DPCSSYS_CR3_RAWLANEX_DIG_PCS_XF_*` raw-lane PCS crossbar inputs, outputs, overrides, ATE controls, lane number, TX/RX training/adaptation fields, termination controls, phase calibration, and MPLL loop controls.
- `DPCSSYS_CR3_RAWLANEX_DIG_FSM_*` FSM overrides, monitors, fast-path calibration/adaptation step flags, common calibration status, CR lock, TX DCC flags/status, and OCLA observability controls.
- `DPCSSYS_CR3_RAWLANEX_DIG_IRQ_CTL_*` per-lane interrupt status, clear, and mask fields for reset, request, rate, pstate, adaptation, phase calibration, loopback, DCC, and TX events.
- `DPCSSYS_CR3_RAWLANEX_DIG_PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*` PMA crossbar, TX/RX FSM, clock, loss-of-signal masking, continuous adaptation, DCC status, and observation controls.

The line range ends with empty `rdpcstx[0-3]_rdpcstxdebugind` address-block markers and the header guard close. No functions, structs, storage, or inline helpers are declared here.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public contract is the generated register-field macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for that field in the 16-bit lane/debug register view used by these DPCS blocks.
- Prefixes encode block and lane scope. `DPCSSYS_CR3_LANEX_*` names refer to the CR3 lane analog register space, while `DPCSSYS_CR3_RAWLANEX_*` names refer to raw-lane digital PCS/PMA/FSM/IRQ control surfaces.

Important field families include:

- Override/value pairs such as `*_OVRD_VAL` plus `*_OVRD_EN`, or register value plus override enable, for forcing rate, width, pstate, low-power detect, loopback, TX/RX reset/request, signal-detect threshold, RX valid, VCO/ref load values, and TX async/data signals.
- Control/status pairs across PCS and PMA such as `TX_PCS_IN`, `TX_PCS_OUT`, `RX_PCS_IN`, `RX_PCS_OUT`, `TX_PMA_IN`, `RX_PMA_IN`, and `*_OVRD_OUT`, which define how lane state moves between controller, PCS, and analog PHY.
- RX adaptation/training telemetry fields including adaptation request/ack, figure-of-merit, `TXPRE`, `TXMAIN`, `TXPOST` direction fields, PH2 calibration, AFE/DFE/IQ/reflvl calibration fast flags, and continuous adaptation/calibration status.
- Calibration and analog tuning fields for TX DCC DAC selection/control, TX/RX termination code, RX squelch and signal detection thresholds, RX CDR/VCO/VDAC/VREG controls, and ATB measurement muxes.
- Interrupt control fields for status, clear, and mask registers. The mask register covers reset/request/rate/pstate/adaptation/phase-calibration/loopback/DCC/TX event bits, with `_CLR` register fields used to acknowledge specific latched lane events.

Consumers use these constants indirectly through AMD display register helpers and generated register tables. The same source tree contains `display/dmub/src/dmub_dcn401.c`, which includes both `dcn/dcn_4_1_0_offset.h` and this `dcn/dcn_4_1_0_sh_mask.h`; the matching offset header supplies register addresses while this file supplies field positions. Other display components rely on the same generated-name convention when resource, clock, DIO/link, and DMUB code expands per-ASIC register lists.

## Control Flow

This header has no runtime control flow. Runtime behavior is indirect:

1. DCN 4.1 display/DMUB code includes the matching offset and shift/mask headers during compilation.
2. Register-list macros or helper wrappers bind an offset, a shift, and a mask for each selected hardware field.
3. Display code later executes MMIO reads/writes through helpers that combine the symbolic field constants with values produced by link training, clock/power sequencing, firmware mailbox handling, or debug paths.
4. Hardware latches the resulting writes in the DPCS/PHY lane registers, and readback/status helpers decode fields with the same masks.

Within this chunk, the conceptual control surfaces are lane bring-up and link-maintenance state machines: TX/RX request and reset sequencing, rate/width/pstate changes, MPLL selection/enabling, RX adaptation/calibration, DCC calibration, loss-of-signal masking, and interrupt acknowledgment. The header does not implement those sequences; it defines the bit-level ABI that those sequences depend on.

## State And Persistence Behavior

The file itself stores no state and persists nothing. The represented hardware fields map to stateful lane registers:

- Persistent-until-reprogrammed or reset controls include TX/RX override enables, pstate/rate/width override values, MPLL selection, TX/RX data and async-data overrides, signal-detect threshold overrides, TX DCC DAC calibration controls, analog TX/RX VREG and termination settings, PMA/PCS crossbar overrides, and OCLA enable bits.
- Volatile status/readback fields include RX adaptation acknowledge/FOM, TX pre/main/post direction, PH2 calibration indications, FSM status monitor fields, common calibration status, CR lock, DCC status, continuous adaptation/off-cancellation status, RX valid, interrupt status bits, and lane-number readback.
- Self-clearing or write-to-clear semantics are implied by the `*_IRQ_CLR` groups; the macros only expose bit positions, while the register programming code must preserve hardware-specific clear behavior.
- Reserved fields are explicitly masked throughout the chunk. Callers should avoid writing nonzero values into reserved masks unless a hardware sequence explicitly requires it.

Incorrect masks can leave a lane in a forced override state, hold calibration disabled/enabled, acknowledge the wrong interrupt, or write reserved bits that persist until the lane, PHY, display block, or GPU is reset.

## Dependencies And Integration Points

The primary dependency is the matching DCN 4.1.0 offset header, `dcn_4_1_0_offset.h`, which defines the addresses for these register names. The generated shift/mask header must remain synchronized with that offset file and with the ASIC register specification; name drift or bit drift breaks compile-time macro expansion or silently corrupts hardware programming.

Important integration points in the AMD display stack are:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c`, which directly includes the DCN 4.1.0 offset and shift/mask headers for DMUB register access. DMUB initialization, reset, mailbox, GPINT, firmware status, and diagnostic paths use the generated register-access model.
- DCN 4.1 clock/resource/link code under `drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401`, `dc/resource/dcn401`, and related DIO/link encoder paths, which share the ASIC-specific register convention for programming display clocks, links, and PHY-facing blocks.
- DPCS/PHY lane training flows, which depend on PCS/PMA state, rate/width/pstate transitions, MPLL selection, TX/RX request/reset handshakes, DCC calibration, RX adaptation, and loss-of-signal behavior.
- Hardware debug and validation paths using ATE, ATB, alternate bus, OCLA, FSM monitor, and IRQ status fields to inspect or force lane behavior.

The chunk also mirrors address-block structure seen in DPCS register offset headers, so reconciliation should treat these symbols as part of a generated hardware ABI rather than hand-authored driver logic.

## Risks

- Generated-header drift: a stale shift or mask can compile cleanly but program the wrong PHY bit, causing lane training failures, blank displays, link flaps, or hard-to-localize DMUB/display failures.
- Override hazards: many fields pair an override value with an override enable. Setting the enable bit with a stale value can force bad rate, width, pstate, reset, request, loopback, RX valid, signal-detect, or calibration state.
- Calibration fragility: TX DCC DAC, RX VCO/CDR, VDAC, termination, squelch, IQ/DFE/AFE, and continuous-adaptation fields are analog-sensitive. Wrong masks may degrade signal integrity instead of producing an immediate deterministic failure.
- Interrupt clear/mask mistakes: status, clear, and mask registers are adjacent and similarly named. A bad field definition or caller mix-up can drop lane events, fail to clear latched interrupts, or mask a real reset/rate/adaptation problem.
- Reserved-bit writes: most 16-bit registers include high reserved masks. Bulk updates must preserve those bits; writing reserved ranges can trigger undocumented hardware behavior.
- Instance/lane assumptions: `CR3` and `LANEX` naming implies a replicated lane design. If software assumes identical layouts across lanes or ASIC revisions when one lane differs, failures may appear only on specific connectors, link widths, or PHY assignments.
- Debug-only field exposure: ATE/ATB/OCLA and alternate-bus fields are useful for validation but unsafe for normal modeset paths unless tightly controlled.

## Test Signals

Direct unit testing of this chunk is limited because it is compile-time metadata. Useful validation signals are hardware and integration oriented:

- Successful AMDGPU build with `dcn_4_1_0_sh_mask.h` and `dcn_4_1_0_offset.h` included by DCN 4.1/DMUB code, with no missing or duplicate generated field names.
- DCN 4.1 display bring-up across links that use CR3/DPCS lanes, including cold boot, modeset, hotplug, suspend/resume, and GPU reset recovery.
- DisplayPort/eDP link training at multiple rates, lane widths, pstate transitions, and low-power states, watching for rate-change, request/reset, RX adaptation, and LOS-related failures.
- Tests that exercise DMUB reset/release, firmware boot status, GPINT/mailbox traffic, and diagnostic collection on DCN 4.1 hardware.
- PHY validation or lab tests that read ATE/ATB/OCLA/FSM monitor data, RX adaptation FOM/ack, TX pre/main/post direction, DCC status, and common calibration status.
- Interrupt tests that provoke and clear RX reset/request/rate/pstate/adaptation/PH2 calibration/loopback/DCC/TX request events and confirm mask/clear behavior.
- Regression checks for reserved-bit preservation in register update helpers, especially for 16-bit DPCS lane registers with broad `RESERVED_*` masks.
