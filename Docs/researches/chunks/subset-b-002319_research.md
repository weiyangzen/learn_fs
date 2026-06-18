# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 73859-76242

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for low-level display PHY register fields. It contains no executable C logic; its interface is a dense set of preprocessor constants used by AMDGPU display code to pack and decode bitfields in DPCS registers.

The requested range contains 2,107 `#define` entries: 1,055 `__SHIFT` macros and 1,052 `_MASK` macros. The mismatch is expected from the chunk boundaries. The range starts in the middle of `DPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_RX_RESET_IRQ_CLR`, so the register comment and some adjacent context are just before the chunk. It ends in the middle of `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT`, with the final masks and subsequent RAWLANE3 PMA/TX/RX control registers continuing in the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file belongs to `drivers/gpu/drm/amd/include/asic_reg/dpcs` and describes AMD display hardware, not Ceph or distributed filesystem behavior.

## Register Groups Covered

The line range spans CR3 raw-lane register layouts:

- RAWLANE1 tail: IRQ clear/status/mask fields for RX/TX reset/request, RX rate, pstate, adaptation request/disable, lane transceiver mode, PH2 calibration, lane RX-to-TX serial loopback, and DCC on-demand IRQs; PMA transfer and override registers for MPLLA/MPLLB lane enable, supervisor state, TX/RX request/reset/data-enable overrides, TX beacon/async/clock-sync controls, loopback controls, PMA ACKs, lane RTUNE, MPHY PWM/termination controls, RX adaptation IQ phase adjustment, TX/RX control/status/OCLA fields, ATE PCS override fields, master MPLL loop, and additional ATE/RX override surfaces.
- RAWLANE2 main body: PCS transfer registers for TX and RX pstate/rate/width/MPLL/reset/request/detect-rx/data-enable/loopback/adaptation/equalization/termination/PH2 calibration; FSM status and fast-control fields for startup calibration, RX adaptation, AFE/DFE/bypass/reference-level/IQ calibration, supervisor and TX common-mode steps, RX detect/power-up/VCO wait/VCO cal, continuous calibration/adaptation flags, CR lock, TX DCC flags, OCLA, TX EQ update, RCAL status, and RX IQ phase offset; complete RAWLANE2 IRQ, PMA transfer, TX control, RX control, and ATE override groups.
- RAWLANE3 beginning through PMA RX override: PCS transfer, RX adaptation feedback, lane number/reserved fields, ATE override, RX equalization delta/IQ and termination controls, PH2 calibration, FSM monitor/fast-control/status fields, complete IRQ status/clear/mask groups, PMA lane/supervisor/TX override groups, TX PMA ACK, and the beginning of PMA RX request/reset/loopback/data-enable override fields.

Most fields are 16-bit register payload fields represented as `long`-suffixed mask literals such as `0x0000FFFEL`. The repeated RAWLANE2 and RAWLANE3 layouts are intentionally similar, but the lane number in the macro name remains part of the contract.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO calls in this chunk. The exported API is the generated macro naming convention:

- `DPCSSYS_CR3_RAWLANE<n>_<BLOCK>__<FIELD>__SHIFT` gives the least-significant bit position for a hardware field.
- `DPCSSYS_CR3_RAWLANE<n>_<BLOCK>__<FIELD>_MASK` gives the bit mask for isolating or updating that field.
- `RESERVED_*`, `RSVD_*`, and similar fields preserve exact hardware layout for reserved bit ranges; they are metadata, not permission to write arbitrary values into reserved bits.

Important field families include:

- IRQ control: status, write-clear, and mask bits for RX reset/request/rate/pstate/adaptation, TX reset/request, transceiver-mode changes, PH2 calibration events, RX-to-TX loopback, and DCC on-demand events.
- PCS transfer: TX/RX override inputs and outputs for request, reset, pstate, rate, width, low-power detect, detect-rx request/result, Vboost/Iboost, beacon, async data/drive, lane loopback, MPLL select/enable/state, data enable, RX valid/clock, LOS threshold, VCO/ref-load values, RX equalization status, adaptation controls, directed TX pre/main/post feedback, and lane numbering.
- FSM and calibration: enable/status bits for fast RX startup, adaptation, AFE/DFE/bypass/reference-level/IQ calibration, continuous adaptation/data/phase/AFE calibration, VCO wait/calibration, RX power-up, TX common-mode, RX detect, common MPLL/RCAL status, TX DCC flags/status, CR lock, and RX IQ phase offset.
- PMA transfer: lane MPLLA/MPLLB enable overrides, supervisor MPLL state overrides, TX/RX request and reset overrides, TX beacon/async/clock-sync/data-enable controls, serial/parallel loopback controls, PMA ACK readbacks, RTUNE request/ACK, MPHY PWM/termination overrides, and RX IQ phase adjustment map override.
- TX/RX control and debug: TX FSM wait/allow-rxdet controls, TX clock divider and duty-cycle-continuation status, RX FSM/rate-change controls, RX LOS mask/data-enable override timing, off-cancel/adaptation continuous status, and OCLA/UPCS debug probe enables.
- ATE and validation: ATE RX/TX override inputs, master MPLL loop controls, additional RX override outputs, equalization overrides, and PH2 calibration request/ACK fields used by manufacturing, validation, or deep PHY debug flows.

## Control Flow

This header has no runtime control flow. It participates in compile-time construction of register field tables and read-modify-write helpers:

1. AMD display code includes the DPCS 4.2.0 offset header plus this shift/mask header.
2. Register-list and shift/mask-list macros token-paste register and field names into ASIC-specific tables.
3. Runtime code uses AMDGPU display register helpers, such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, or `REG_UPDATE`, to program or poll the corresponding hardware fields.
4. Hardware, firmware, and display driver sequencing code outside this header perform the real operations: PHY reset, lane power sequencing, link training, RX adaptation, PLL selection, IRQ handling, test/debug collection, and suspend/resume reinitialization.

The macros describe where bits live. They do not encode access direction, write-one-to-clear behavior, self-clearing bits, latch semantics, polling timeouts, clock-domain requirements, or safe programming order.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. The fields name hardware-visible state in DPCS CR3 raw-lane registers:

- Live lane state includes TX/RX request, reset, pstate, rate, width, MPLL selection/enables, low-power detect, detect-rx, beacon, async data, loopback, data enable, RX valid, clock controls, and lane-number reporting.
- Calibration and adaptation state includes RX startup/AFE/DFE/IQ/reference-level calibration, VCO wait/calibration, continuous adaptation/data/phase/AFE calibration, RX equalization values, IQ phase offset/adjustment maps, PH2 calibration, RCAL and common MPLL status, and TX DCC status.
- Interrupt state includes latched status, clear strobes, and mask bits for lane request/reset/rate/pstate/adaptation/PH2/loopback/DCC events.
- Debug and validation state includes OCLA/UPCS selections, ATE override inputs, directed TX coefficient feedback, RX adaptation ACK/FOM, RTUNE, MPHY PWM/termination overrides, and PMA/PCS ACK handshakes.

Persistence is hardware-defined. Configuration and override fields generally persist until rewritten by a modeset, link-training step, PHY reset, power-gate transition, suspend/resume path, GPU reset, or ASIC reinitialization. Status, IRQ, ACK, calibration, and statistic-like fields may be transient, latched, clear-on-write, self-clearing, or valid only when the relevant lane/common power and clock domains are active.

## Dependencies And Integration Points

This generated header is tightly coupled to AMD's DPCS 4.2.0 register database and companion address definitions:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching `ixDPCSSYS_CR3_RAWLANE*` register offsets, such as RAWLANE1 offsets around `0x3140`, RAWLANE2 around `0x3240`, and RAWLANE3 around `0x3340`.
- AMD display DCN/DPCS resource code consumes these macros through generated register, shift, and mask tables for the ASIC generation that owns DPCS 4.2.0.
- Link encoder, PHY, clock-source, AUX/link-training, hotplug, modeset, power-management, and hardware-sequencing code indirectly depends on these constants when programming DPCS lanes.
- Firmware and hardware state machines interact with the same register bits for lane handshakes, PMA/PCS transfers, RX adaptation, PLL/MPLL state, DCC, RTUNE, PH2 calibration, and IRQ latching.

The chunk is low-level hardware metadata. Its user-visible impact appears indirectly as display link stability, correct power transitions, reliable hotplug/modeset behavior, and useful PHY debug telemetry.

## Risks And Edge Cases

- Incorrect masks or shifts compile cleanly but can program the wrong hardware bit, corrupt a reserved field, miss a status bit, or clear/mask the wrong interrupt.
- This is generated metadata. Manual edits can diverge from the authoritative AMD register database, companion offset headers, firmware assumptions, and silicon documentation.
- The chunk starts and ends mid-register-group. The previous chunk owns the `RAWLANE1_DIG_IRQ_CTL_RX_RESET_IRQ_CLR` comment and earlier fields; the next chunk owns the remaining `RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT` masks and subsequent PMA/TX/RX control groups.
- RAWLANE1, RAWLANE2, and RAWLANE3 macros are not interchangeable even when field layouts match. Using a lane 2 mask with a lane 3 offset, or vice versa, may silently target the wrong hardware lane.
- IRQ status, clear, and mask registers are side-effect-sensitive. Confusing status bits with clear strobes or mask bits can produce repeated interrupts, missed lane events, stuck waits, or failure to observe link-training transitions.
- Override fields are sequencing-sensitive. Leaving PMA/PCS/ATE override enables asserted can bypass normal state-machine control of request/reset/data-enable/MPLL/loopback/termination behavior.
- Power, PLL, calibration, and adaptation fields affect link integrity. One-bit mistakes in VCO, RX adaptation, DCC, RTUNE, PH2 calibration, pstate, or MPLL-related fields can cause blank displays, unstable high-rate links, repeated retraining, resume-only failures, or difficult-to-debug PHY lock problems.
- Reserved masks are emitted for layout completeness. Driver writes should preserve reserved bits unless hardware documentation explicitly requires a value.

## Test Signals

Useful validation for this chunk combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.0. Missing or renamed macros should fail where register, shift, and mask tables are initialized.
- Mechanically verify that each complete field has a matching `__SHIFT` and `_MASK`, allowing the known boundary exceptions at the start and end of this chunk.
- Cross-check every complete register group in this range against `dpcs_4_2_0_offset.h` and against AMD's authoritative DPCS 4.2.0 register source.
- Compare repeated RAWLANE2 and RAWLANE3 field layouts where hardware expects them to match, while preserving lane-specific macro names and offsets.
- Exercise DisplayPort and HDMI link bring-up across available lanes, rates, widths, and power states. Good signals are stable link training, correct lane power transitions, expected MPLL selection, no stuck ACK/status bits, and no false or missing lane IRQs.
- Run hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence and reinitialization problems around IRQ, pstate, PMA/PCS override, calibration, and adaptation fields.
- Use register dumps or PHY debug traces on failures to confirm IRQ clear/mask, RX adaptation ACK/FOM, TX directed coefficient feedback, VCO/ref-load, DCC status, RTUNE, FSM status, PH2 calibration, and OCLA/UPCS fields decode as expected.
- Exercise manufacturing/debug paths where available, including ATE overrides, PMA loopback, RX/TX termination controls, RX EQ overrides, master MPLL loop controls, and OCLA probes.

## Cross-Chunk Notes

The previous chunk should provide the beginning of RAWLANE1 IRQ clear definitions, including the comment and earlier fields for `DPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_RX_RESET_IRQ_CLR`. This chunk then covers the RAWLANE1 tail, the complete RAWLANE2 PCS/FSM/IRQ/PMA/control/ATE span, and RAWLANE3 through the beginning of PMA RX override output. The next chunk should resume with the remaining `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT` masks and continue RAWLANE3 PMA, TX control, RX control, and later groups. The final per-file report should reconcile these boundaries before making whole-file completeness claims.
