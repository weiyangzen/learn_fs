# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 74175-76587

## Purpose

This chunk is a generated AMD DCN 4.1.0 register shift/mask slice. It contains preprocessor constants only: no C functions, structs, enums, runtime storage, or executable logic. Its exported interface is a set of `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros used with the matching DCN 4.1.0 offset header and AMD Display Core register helpers to access individual MMIO bitfields.

The requested range contains 2,149 `#define` entries, split into 1,074 shift macros and 1,115 mask macros, plus 264 register comments. It starts mid-register at the tail of `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_ATE_TX_OVRD_IN`, covers the end of raw lane 0 PCS ATE fields, full raw lane 1 and raw lane 2 digital PCS/FSM/IRQ/PMA/TX/RX control field groups, and ends mid-register in raw lane 3 at `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_RX_OVRD_IN_1`. The line boundaries are artificial chunk boundaries, not semantic hardware boundaries.

Although this file lives under a local `ceph-client` source mirror, this range is AMDGPU Display Core hardware metadata. It does not implement Ceph, a distributed filesystem, block I/O, or persistent storage behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The only API surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a field inside a DCN/DPCS register.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate or update that field.

The main register families covered here are:

- `DPCSSYS_CR0_RAWLANE0_*`: partial lane 0 PCS ATE tail, including TX override fields, master MPLL loop enables, RX LOS/adaptation/VCO/reference-load ATE overrides, RX-valid override, and TX data/async/loopback override fields.
- `DPCSSYS_CR0_RAWLANE1_DIG_PCS_XF_*`: complete lane 1 PCS crossover fields for TX and RX reset/request handshakes, P-state/LPD/width/rate/MPLL selection, TX/RX override outputs, PCS inputs/outputs, adaptation acknowledgement and figure-of-merit, equalizer settings, TX pre/main/post direction, lane number, ATE override controls, termination controls, RX EQ override controls, and phase-2 calibration request/acknowledgement.
- `DPCSSYS_CR0_RAWLANE1_DIG_FSM_*`: lane 1 digital state-machine controls and observability, including FSM jump/break/start override, command/status monitors, fast RX startup/adapt/AFE/DFE/bypass/reference/IQ/VCO sequences, common MPLL/RCAL status, continuous calibration/adaptation flags, clock-recovery locks, TX DCC flags/status, OCLA debug enables, TX EQ update flag, and RX IQ phase offset.
- `DPCSSYS_CR0_RAWLANE1_DIG_IRQ_CTL_*`: lane 1 IRQ latch, clear, and mask fields for RX reset/request/rate/P-state/adaptation/phase-2-calibration events, lane transceiver mode, RX-to-TX loopback, DCC on-demand, and TX reset/request events.
- `DPCSSYS_CR0_RAWLANE1_DIG_PMA_XF_*`: lane 1 PMA crossover fields for lane MPLL enables, supervisor state override/readback, TX/RX reset/request/data/async/beacon/loopback override outputs, PMA acknowledgements, RTUNE request/acknowledgement, MPHY PWM/term/async overrides, and RX adaptation IQ phase adjust mapping.
- `DPCSSYS_CR0_RAWLANE1_DIG_TX_CTL_*` and `DPCSSYS_CR0_RAWLANE1_DIG_RX_CTL_*`: lane 1 higher-level TX/RX control and status fields for TX FSM timing/RXDET permissions, TX clock select/enable/beacon wait, DCC continuous status, TX/RX OCLA taps, RX FSM enable/rate-change behavior, RX LOS mask count, RX data-enable override count, off-canonical continuous status, and adaptation continuous status.
- `DPCSSYS_CR0_RAWLANE2_*`: a matching full lane 2 PCS/FSM/IRQ/PMA/TX/RX control layout, repeated with the `RAWLANE2` prefix.
- `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_*`: beginning of lane 3 PCS crossover fields through `RX_OVRD_IN_1`, including TX override/PCS handshake fields, TX status outputs, RX override fields, and the first part of RX reset/request/LOS/adaptation overrides.

## Control Flow

This header slice has no local control flow. Runtime behavior comes from AMD Display Core code that includes `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`, token-pastes register and field names into register tables, and then calls register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

A typical use model is:

1. DCN401 display code includes the DCN 4.1.0 offset and shift/mask headers.
2. Generated register-list macros select the `DPCSSYS_CR0_RAWLANE*` register offsets and the field-level shift/mask constants from this file.
3. Link encoder, PHY, GPIO, IRQ, DMUB, resource, or diagnostic code reads or updates selected lane fields during link bring-up, training, reset, power-state transition, interrupt handling, or debug collection.
4. Hardware, not this header, performs the actual FSM transitions, IRQ latching, calibration, adaptation, loopback, and PMA/PCS handshakes.

The macros do not encode ordering rules. Consumers still need to respect hardware sequencing around reset/request/ack handshakes, MPLL state changes, TX/RX data enables, RX adaptation, IRQ clear ordering, and PMA/PCS crossing points.

## State And Persistence Behavior

This chunk stores no software state. It describes state held in DCN 4.1.0 display/link hardware registers:

- PCS TX/RX state: reset/request, acknowledge, P-state, LPD, lane width, link rate, MPLL select/enable/state, DETRX request/result, TX/RX data enable, async enable/data, beacon enable, and loopback controls.
- RX adaptation/equalization state: AFE/DFE adaptation enables, adaptation request/continuous bits, off-canonical continuous bits, LOS threshold/LFPS overrides, VCO/reference load overrides, RX-valid override, equalizer attenuation/VGA/CTLE/DFE fields, adaptation acknowledgement, FOM, and RX IQ phase offset.
- Lane FSM state: fast calibration/adaptation shortcuts, startup/power-up/VCO wait flags, common calibration status, command/status monitor fields, clock-recovery locks, TX DCC status, and OCLA/debug enable state.
- IRQ state: per-lane interrupt latch bits, clear bits, and masks for RX/TX and adaptation events.
- PMA crossover state: lane MPLL enables, supervisor readback, TX/RX PMA reset/request/data/async/beacon/loopback overrides, RTUNE handshakes, MPHY PWM/termination controls, and RX PMA adaptation override mapping.
- TX/RX controller state: TX FSM wait times and RXDET allowances, TX clock enable/select, async beacon wait timing, RX FSM enable/rate-change behavior, LOS masking counters, RX data-enable override counters, and continuous calibration/adaptation status.

Persistence is hardware-defined. Configuration fields generally remain until link reprogramming, a modeset, hotplug/link retrain, runtime power transition, suspend/resume, GPU reset, or ASIC reset changes them. Status, acknowledgement, interrupt, clear, calibration-done, and debug-observation fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the lane block is powered. This generated header does not identify those access semantics.

## Dependencies And Integration Points

- The definitions must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`, which supplies the matching register offsets.
- DCN401 display sources include this header directly, including DMUB setup, resource construction, IRQ service, clock manager, GPIO factory, and GPIO translation code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/`.
- The lane register names mirror DPCS-generation headers such as `dpcs_4_2_0_sh_mask.h`, `dpcs_4_2_2_sh_mask.h`, and `dpcs_4_2_3_sh_mask.h`; that is useful for drift checks, but wrong-generation mixing can still compile when names overlap.
- Link-encoder and PHY-oriented code use these field definitions indirectly through generated shift/mask tables. Related older code references fields such as `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_RX_OVRD_IN_2__VCO_LD_VAL_OVRD` and `REF_LD_VAL_OVRD` for RX CDR/VCO/reference-load override handling.
- IRQ service code depends on the lane IRQ latch/clear/mask field shapes when wiring display/link interrupts for DCN401.
- Debug and validation tooling depend on FSM monitor, OCLA, calibration status, DCC status, RX FOM, lane number, and PMA/PCS readback fields to interpret lane state.

## Risks And Edge Cases

- These are untyped preprocessor constants. An incorrect mask or shift can compile cleanly while writing the wrong MMIO bits, corrupting adjacent fields, or silently leaving a lane feature unprogrammed.
- Offset/header drift is the main integrity risk. Correct masks paired with stale offsets, or correct offsets paired with stale masks, can misprogram display link hardware without a compile-time failure.
- Chunk boundaries are not semantic. The first `RAWLANE0` register starts before this range, and the final `RAWLANE3_DIG_PCS_XF_RX_OVRD_IN_1` register continues after line 76587.
- Lane repetition hides copy or generator mistakes. RAWLANE1 and RAWLANE2 have complete near-identical layouts here, while RAWLANE0 and RAWLANE3 are partial in this chunk; tests that exercise only one physical lane can miss instance-specific drift.
- Full-register writes are risky because control, status, clear, mask, reserved, and hardware-owned bits are packed into the same 16-bit field maps. Read-modify-write helpers are expected for ordinary field updates.
- Reset/request/ack and IRQ clear fields are sequencing-sensitive. Clearing interrupts too early, masking the wrong event, forcing reset/request overrides, or ignoring acknowledgement bits can produce stuck link training, missed hotplug/link events, or repeated IRQ storms.
- MPLL/P-state/rate/width fields are link- and power-sensitive. Wrong values can break DP/HDMI link bring-up, clock recovery, lane power management, runtime power transitions, or suspend/resume recovery.
- ATE, loopback, OCLA, and FSM override controls are dangerous outside controlled test/debug flows. Leaving overrides enabled can bypass normal hardware state machines or force non-production TX/RX behavior.
- RX adaptation and equalizer fields can fail only under specific cable, sink, data-rate, or signal-integrity conditions. Incorrect field definitions may appear stable at low rates while causing high-rate link training or long-run error issues.

## Test Signals

- Build AMDGPU DCN401 display code with this header and `dcn_4_1_0_offset.h` enabled; missing or malformed generated symbols should fail in register-table expansion.
- Mechanically compare this range against the authoritative DCN 4.1.0 register database and the adjacent DPCS generation headers, paying special attention to RAWLANE1/RAWLANE2 repetition and the partial RAWLANE0/RAWLANE3 boundaries.
- Run static checks that every complete field group has matching `__SHIFT` and `_MASK` entries and that reserved masks cover only the intended unused bits.
- Exercise link bring-up, retrain, hotplug, modeset, suspend/resume, runtime power management, and GPU reset across connectors and lane counts that use lanes 1 and 2, not only lane 0.
- Validate DP/HDMI operation at multiple rates, widths, P-states, and power states; check for link-training failures, CRC/link-error counters, underruns, and stuck reset/request/ack status.
- Test IRQ behavior by triggering RX/TX reset/request, rate/P-state changes, adaptation requests, phase-2 calibration events, lane mode changes, DCC on-demand events, and loopback transitions; verify latch, clear, and mask behavior.
- Use register dumps or hardware diagnostics to confirm FSM monitor/status, common calibration, DCC status, OCLA, RX FOM, adaptation acknowledgement, and PMA/PCS readback fields report plausible values before and after link transitions.
- Include debug/ATE/loopback negative testing where available to ensure override bits are cleared after diagnostics and normal link operation is restored.

## Cross-Chunk Notes

The previous chunk contains the beginning of `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_ATE_TX_OVRD_IN`. The next chunk continues `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_RX_OVRD_IN_1` and later raw lane 3 fields. The final per-file research document should reconcile adjacent chunks before making whole-file claims about all `DPCSSYS_CR0_RAWLANE*` registers or complete lane coverage.
