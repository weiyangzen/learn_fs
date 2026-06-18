# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 136947-139390

## Scope And Purpose

This chunk is part of AMDGPU DCN 4.1.0 generated register metadata. It contains preprocessor definitions for register bit shifts and masks under the `DPCSSYS_CR3_*` namespace, mostly covering DisplayPort/USB-C PHY lane control and status registers for `RAWLANE2`, `RAWLANE3`, `RAWAONLANE0`, and the beginning of `RAWAONLANE1`.

The file is not executable code. Its purpose is to give DCN 4.01 display code stable symbolic names for MMIO bitfield extraction and composition. Each register block comment names a hardware register, and each following pair of `__SHIFT` and `_MASK` macros defines where one field lives inside that register. Runtime behavior comes from users that include this header and pair these masks with matching offset headers and register access helpers.

The line range begins in the middle of `DPCSSYS_CR3_RAWLANE2_DIG_PMA_XF_TX_OVRD_OUT`, runs through a large complete `RAWLANE3` lane-control area, covers many `RAWAONLANE0` analog/always-on calibration fields, and ends at the start of `DPCSSYS_CR3_RAWAONLANE1_DIG_FW_CALIB_CONFIG`.

## Register Areas Covered

The first section finishes `RAWLANE2` PMA/PCS control fields. It includes TX/RX override outputs, PMA input acknowledgements, lane retune request/acknowledge bits, MPHY PWM/termination overrides, RX adaptation override fields, TX/RX clock and FSM controls, LOS mask timing, data-enable override timing, continuous off-cancel/adaptation status, UPCS/OCLA controls, and ATE override fields for rate, width, power state, low-power detect, loopback, VCO/ref lock override values, RX valid override, and TX data/async data override.

The largest middle section defines `RAWLANE3` PCS, FSM, IRQ, PMA, TX control, and RX control fields. It covers normal and override paths for TX/RX requests, resets, acknowledgements, data enables, power states, rates, lane width, MPLL selection, MPLL enable/state override, TX beacon and async paths, detector requests/results, serial and parallel loopback, RX adaptation request/disable paths, EQ feedback/direction fields, lane numbering, reserved scratch registers, phase-2 calibration controls, term-control overrides, and RX EQ override fields.

The `RAWLANE3_DIG_FSM_*` blocks expose fast-sequence and status controls for startup calibration, RX adaptation, AFE/DFE calibration and adaptation, bypass/ref-level/IQ calibration, supervisor steps, TX common mode, TX RX-detect, VCO wait/calibration, continuous calibration/adaptation, CR lock, TX DCC status, TX EQ update flags, common calibration status, and RX IQ phase offset. These are hardware FSM observability and control surfaces rather than C state machines.

The `RAWLANE3_DIG_IRQ_CTL_*` blocks define interrupt status, clear, and mask bits for RX reset/request/rate/pstate/adaptation events, lane transceiver mode changes, phase-2 calibration request/disable events, RX-to-TX serial loopback events, DCC on-demand events, and TX reset/request events. They include separate mask registers for RX-side and TX-side conditions.

The final section moves into always-on analog lane definitions. `RAWAONLANE0` is covered extensively and `RAWAONLANE1` begins with analogous fields. These blocks include AFE and CTLE offset codes, RX adaptation IQ/FOM and per-stage adaptation codes, DFE tap and reference-level values, phase adjust maps, MPLL coarse tune and disable controls, initialization and fast flags, common calibration status, TX/RX overrides, LOS and signal-detect filtering, signal-detect output overrides/status, RX squelch and termination controls, signal-detect calibration/tune codes, VREF generator enable/calibration values, RX DCC calibration codes for I/Q common-mode and differential paths, TX DCC bank address/data/control, firmware configuration words, lane transceiver mode override/status, RX signal-detect config, and TX/RX DCC bypass controls.

## Important APIs, Types, And Macros

There are no functions, structs, or exported C objects in this chunk. The public API is the macro namespace itself:

- `DPCSSYS_CR3_RAWLANE*_DIG_*__FIELD__SHIFT` gives the least-significant bit position for a field.
- `DPCSSYS_CR3_RAWLANE*_DIG_*__FIELD_MASK` gives the field mask in the register value.
- `DPCSSYS_CR3_RAWAONLANE*_DIG_*__FIELD__SHIFT` and `_MASK` do the same for always-on analog lane registers.
- `RESERVED_*` fields document reserved bit ranges. They are still generated as masks, but driver code should not treat them as programmable feature bits unless hardware documentation says otherwise.

The macros are consumed with AMD display register helpers that shift, mask, set, or read MMIO fields. The matching address definitions live in offset headers such as the generated `dcn_4_1_0_offset.h` family and comparable `dpcs_*_offset.h` files. The header itself only describes field layout; it does not identify register addresses.

## Control Flow

This chunk has no direct control flow. In the runtime display driver, the practical flow is:

1. DCN 4.01 code includes `dcn_4_1_0_sh_mask.h`.
2. A register offset macro selects an MMIO register.
3. A shift/mask macro from this header selects a bitfield within the value read from or written to that register.
4. Hardware observes the write or returns status bits through later reads.

For override registers, the common hardware pattern is a value field plus an enable field, for example `*_OVRD_VAL` paired with `*_OVRD_EN`. For request/acknowledge paths, a control bit is written or sampled and an `ACK` bit reports hardware completion. Interrupt registers usually have status, clear, and mask variants; clear registers are used to acknowledge latched hardware events, while mask registers suppress interrupt delivery.

## State And Persistence Behavior

The macros do not persist state in memory. The persistent or transient state belongs to hardware registers. Writes through these masks can change PHY lane state until hardware reset, power-gating transitions, firmware programming, or another driver write updates the register.

Important state classes represented by this range include:

- PHY lane power, rate, width, pstate, low-power detect, MPLL selection, and reset/request state.
- RX adaptation, AFE/DFE calibration, VCO/ref lock calibration, phase adjustment, EQ, FOM, and DCC calibration results.
- TX DCC and beacon/async/data-enable state.
- LOS, squelch, VREF, signal-detect, termination, and transceiver-mode configuration.
- Interrupt latch, clear, and mask state for lane events.
- Firmware-owned configuration and calibration words in always-on lane blocks.

Because these definitions target display PHY hardware, incorrect masks can create persistent user-visible display failures across a mode set, link training attempt, hotplug event, or suspend/resume cycle even though no software object is retained by this header.

## Dependencies And Integration Points

This generated header is included by DCN 4.01 display components such as DMUB support, IRQ service, clock manager, GPIO translation/factory code, and resource code. Those users rely on these macro names compiling consistently with the generated register tables for the same ASIC generation.

The chunk depends on:

- Matching generated offset headers for register addresses.
- AMD display MMIO helper macros/functions that accept `*_SHIFT` and `*_MASK` definitions.
- Hardware documentation or generated register databases that define the authoritative field layout.
- The DCN 4.01 resource and link-management stack that decides when PHY lane registers should be read or written.

Integration points are mostly hardware-facing. The `RAWLANE*` definitions integrate with DisplayPort/USB-C PHY bring-up, link training, lane adaptation, retimer/PHY diagnostics, interrupt handling, and low-level debug flows. The `RAWAONLANE*` definitions integrate with always-on analog calibration and signal-detection blocks that can remain relevant across display power transitions.

## Risks And Edge Cases

- The line range starts and ends mid-register-family. A final per-file analysis must reconcile this chunk with adjacent chunks so partially covered registers, especially `RAWLANE2` at the start and `RAWAONLANE1_DIG_FW_CALIB_CONFIG` at the end, are not described as complete here.
- Generated mask drift is high risk. If a shift or mask disagrees with the hardware register database, the driver can program the wrong bits while still compiling cleanly.
- Many fields are value/enable override pairs. Setting an override value without the matching enable bit, or leaving an enable bit asserted after a diagnostic path, can break normal hardware/FW control.
- Reserved masks are present. Accidentally writing reserved bits during read-modify-write sequences can produce undefined hardware behavior.
- IRQ status, clear, and mask fields are easy to confuse. Using a clear mask where a status mask is expected, or failing to mask/clear lane interrupts during hotplug and link transitions, can cause missed or stuck IRQ handling.
- The `RAWLANE3` and `RAWAONLANE0/1` families repeat similar field names with different lane prefixes. Copy/paste mistakes can target the wrong physical lane while looking syntactically valid.
- Some fields are 16-bit lane-register-style masks while other generated DCN registers elsewhere in the file are 32-bit. Access helpers must preserve the intended register width and avoid assuming all masks cover 32-bit display registers.
- These definitions are hardware-generation specific. Reusing them for a related DPCS/DCN revision because names look similar can silently break fields whose offsets or widths changed.

## Test Signals

The strongest validation signal is build coverage for DCN 4.01 display code that includes this header. A missing or renamed macro should fail compilation in DMUB, IRQ, clock, GPIO, or resource code that references it.

Hardware and integration signals include:

- Display link training succeeds across lane counts and link rates that exercise `RAWLANE` rate, width, pstate, request/reset, MPLL, and adaptation fields.
- Hotplug, suspend/resume, and mode-set tests do not leave lane override or IRQ mask state stuck.
- PHY diagnostics or debug register dumps show expected values for lane status, acknowledgements, adaptation/FOM, DCC, VCO/ref lock, LOS, squelch, and signal-detect fields.
- Interrupt tests confirm RX/TX reset/request, rate/pstate, adaptation, transceiver-mode, phase-2 calibration, loopback, and DCC events are masked, latched, cleared, and reported correctly.
- Register-generation consistency checks compare each `__SHIFT`/`_MASK` pair with the authoritative ASIC register database and with matching offset headers.
- Static analysis or code review should verify read-modify-write users do not include `RESERVED_*` masks and do not mix lane prefixes.

Because this chunk is generated static metadata, unit tests against C logic are less useful than compile checks, generated-header consistency checks, and hardware/display bring-up tests that exercise the registers through real MMIO paths.
