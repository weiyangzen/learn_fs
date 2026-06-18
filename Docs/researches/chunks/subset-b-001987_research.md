# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 141616-144082

## Chunk Scope

This chunk is a generated AMD DCN 3.2.0 register-field shift/mask header slice. It contains preprocessor constants only: no functions, structs, enums, storage, runtime branches, loops, locking, or direct MMIO access. The range has 2,096 `#define` entries and 371 register grouping comments for the C20 PHY `CR2` raw-lane digital register namespace.

The first in-scope lines are the mask half of `C20_PHY_CR2_RAWLANE2_DIG_RX_FW_XF_OVRD_IN_1`; the matching shifts and several masks are immediately before this chunk. The last in-scope register is partial as well: `C20_PHY_CR2_RAWLANE3_DIG_FSM_SKIP_RX_DCC_RANGE_RATE_CAL` includes only its shift definitions here, with masks continuing after line 144082. Final file-level research must merge neighboring chunks before documenting either boundary register as complete.

## Purpose

The purpose of this section is to publish the bit-layout ABI for DCN 3.2 C20 PHY `CR2` raw-lane display link hardware. Companion address headers provide register offsets; this shift/mask header provides the field positions that AMDGPU Display Core register helpers use to compose and decode MMIO values.

The hardware surface is concentrated on raw lanes 2 and 3:

- The tail of raw lane 2 RX firmware transfer, IRQ, RX control, PMA transfer, and FSM/debug/policy definitions.
- A complete raw lane 3 TX path covering PCS, firmware transfer, TX IRQ, TX control, and TX PMA transfer fields.
- A large raw lane 3 RX path covering PCS context, firmware/adaptation transfer, RX IRQ, RX control, RX PMA transfer, and the beginning of RX FSM skip/fast controls.

These definitions support low-level DisplayPort/PHY bring-up, link-rate and lane-width changes, reset/request handshakes, RX adaptation, margining, termination control, DCC/IQ/phase calibration, TX retuning, loopback, firmware interaction, and PHY debug instrumentation.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this range. The exported interface is a macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask.
- `//<REGISTER>` comments group all field constants belonging to a hardware register.

Important in-scope macro families:

- `C20_PHY_CR2_RAWLANE2_DIG_RX_FW_XF_*` defines lane 2 RX firmware-transfer fields for request/reset/adaptation handshakes, delta-IQ payloads, acknowledgement and RX-valid overrides, adaptation FOM readback, TX pre/main/post direction feedback, clock enables, and output acknowledgements.
- `C20_PHY_CR2_RAWLANE2_DIG_RX_IRQ_CTL_*` defines lane 2 RX interrupt mask, enable, status, and clear fields. Events include RX reset, request, rate, p-state, adaptation request/disable, termination-control, and margining events for IQ start, VDAC start, error clear, init, finish, and global margining.
- `C20_PHY_CR2_RAWLANE2_DIG_RX_CTL_*` defines lane 2 RX control and readback fields for termination code, off-canonical/continuous adaptation status, adaptation mode/select, PPM drift, CDR detection, PMA miscellaneous controls, adaptation FOM/reference-error values, IQ left/right offsets, phase-adjust map/linear values and update strobes, margin deltas/status/error, FSM control, rate IRQ acknowledgement, and IQ/phase read/write code paths.
- `C20_PHY_CR2_RAWLANE2_DIG_RX_PMA_XF_*` defines lane 2 RX PMA-transfer override/input/output fields for PMA reset/request/rate/valid interactions.
- `C20_PHY_CR2_RAWLANE2_DIG_FSM_*` defines lane 2 raw-lane FSM controls: override and jump-bank controls, memory breakpoints, address/status monitors, firmware configuration stage, scratch registers 0-11, CR lock, fast supervisor/TX/RX path flags, TX/RX calibration skip bits, RX adaptation reload controls, and RX calibration status.
- `C20_PHY_CR2_RAWLANE3_DIG_TX_PCS_XF_*` and `C20_PHY_CR2_RAWLANE3_DIG_RX_PCS_XF_*` define lane 3 PCS-facing transfer fields. These include lane override/input/output signals, mode/rate/width/reset/request/power-state fields, context configuration registers, RX signal-detect thresholds, CDR load values, unique IDs, continuous adaptation/off-canonical controls, and DCC/VREG bypass controls.
- `C20_PHY_CR2_RAWLANE3_DIG_TX_FW_XF_*` and `C20_PHY_CR2_RAWLANE3_DIG_RX_FW_XF_*` define lane 3 firmware-facing transfers for TX/RX reset, request, pstate, rate, width, lane number, acknowledged outputs, RX adaptation request/FOM, delta-IQ, TX pre/main/post direction feedback, and RX firmware clock enables.
- `C20_PHY_CR2_RAWLANE3_DIG_TX_IRQ_CTL_*` and `C20_PHY_CR2_RAWLANE3_DIG_RX_IRQ_CTL_*` define lane 3 interrupt mask/enable/status/clear bitfields. TX events cover rate, reset, request, RX-to-TX parallel loopback enable/disable, rtune, termination-control, and lane transceiver mode. RX events mirror lane 2's reset/request/rate/pstate/adaptation/termination/margining set.
- `C20_PHY_CR2_RAWLANE3_DIG_TX_CTL_*` defines lane 3 TX control fields for FSM control, clock enable/reset, off-canonical continuous status, rate IRQ acknowledgement, termination code, firmware power-up done, and MPLLA/MPLLB restart calibration controls.
- `C20_PHY_CR2_RAWLANE3_DIG_TX_PMA_XF_*` defines lane 3 TX PMA lane/supervisor override and input/output transfer fields, including TX polarity, rate, power state, lane mode, termination, request/reset, standby, differential mode, termination calibration, and rtune controls.
- `C20_PHY_CR2_RAWLANE3_DIG_RX_CTL_*`, `RX_PMA_XF_*`, and `FSM_*` provide lane 3 equivalents of the lane 2 RX control/PMA/FSM surfaces, ending in this chunk partway through RX FSM skip controls.

The macros are typically consumed indirectly by AMD register helper macros such as field descriptor builders and `REG_SET`, `REG_UPDATE`, `REG_GET`, or `REG_WAIT` style operations. Exact helper names live outside this generated header.

## Control Flow

This header has no executable control flow. Runtime sequencing occurs in AMDGPU Display Core, link-encoder, PHY, IRQ, and firmware-assisted paths that include this header and combine these field constants with register offsets.

The implied control surfaces in this chunk are significant:

1. PCS/FW/PMA transfer fields let driver or firmware code move reset, request, rate, width, pstate, loopback, lane-mode, and PMA-valid signals between display controller logic, firmware, PCS, and PMA.
2. IRQ mask/enable/status/clear fields control event flow for link-rate changes, resets, requests, adaptation events, margining phases, loopback transitions, rtune, termination-control, and transceiver-mode changes.
3. RX control fields expose adaptation mode selection, CDR/PPM state, FOM/reference-error readbacks, IQ and phase-adjust code access, and margining state/errors that higher layers can poll or snapshot.
4. FSM controls and scratch/breakpoint/status registers provide debug and firmware-control hooks. Fast and skip bits can shorten or bypass parts of startup, continuous calibration, DCC calibration, AFE/DFE/IQ/phase/VGA/CTLE/ATT/SIGDET/VGEN calibration, adaptation reload, and margining.

The header only names bit locations. Ordering rules, delays, polling timeouts, interrupt acks, and error recovery policy are implemented elsewhere or embedded in PHY firmware/hardware state machines.

## State And Persistence Behavior

The macros are compile-time constants and have no storage. The state they describe resides in hardware registers. Some fields are programmed configuration, some are volatile readback, and some are side-effecting control bits.

Persistent or programmed hardware state includes:

- PCS/FW/PMA override enable/value fields for reset, request, rate, pstate, width, low-power disable, DFE bypass, lane mode, loopback, termination, rtune, standby, polarity, and PMA valid signals.
- IRQ mask and enable flags for TX/RX PHY events.
- RX adaptation mode/select fields, PMA miscellaneous controls, phase/IQ write codes, margin deltas, TX/RX FSM control bits, firmware scratch registers, CR lock, and skip/fast policy bits.
- TX control values for clock enable/reset, termination code, firmware power-up done, and MPLL restart calibration controls.

Volatile or status-oriented state includes:

- IRQ status registers, with separate clear registers for latched events.
- RX adaptation status, off-canonical status, PPM drift, CDR detection, adaptation FOM, reference-error values, phase/IQ readback codes, RX margin status/error, RX valid/acknowledge signals, and RX calibration status.
- TX off-canonical continuous status, rate IRQ acknowledgement state, firmware power-up done readback, PMA output status, FSM memory address/status monitors, and firmware configuration stage.

Side-effecting fields include IRQ clear bits, rate IRQ acknowledgements, phase-update strobes, FSM override/jump/breakpoint controls, CR lock controls, MPLLA/MPLLB restart calibration controls, self-directed fast/skip calibration bits, and adaptation reload/disable interactions. The register specification or caller behavior is needed to classify reset defaults, write-one-to-clear semantics, sticky status, and read-only/write-only behavior; this generated mask header does not encode those attributes.

## Dependencies And Integration Points

This chunk depends on exact consistency with the generated DCN 3.2 C20 PHY register-address headers and the ASIC register database. It is useful only when paired with the matching address definitions and AMD display register helper layer.

Integration points include:

- AMDGPU Display Core DCN 3.2 link and PHY programming code, which configures PHY lanes during modeset, DisplayPort link training, hotplug recovery, link-rate changes, lane-count changes, and suspend/resume.
- Firmware and DMUB-assisted flows that communicate through `*_FW_XF_*`, `*_FSM_*`, firmware stage, scratch, adaptation FOM, request/ack, lane-number, and power-up completion registers.
- IRQ service paths that depend on the TX/RX IRQ mask, enable, status, and clear bit definitions for PHY link events.
- PHY diagnostic and lab/debug tooling that reads/writes FSM monitors, breakpoints, scratch registers, margining status, adaptation results, IQ/phase code fields, CDR/PPM state, and PMA transfer outputs.
- Register generation and reconciliation lanes that merge this chunk with adjacent ranges to create a coherent per-file view of `dcn_3_2_0_sh_mask.h`.

## Risks And Edge Cases

- Numeric mask/shift drift is the core risk. A wrong constant can compile cleanly while writing the wrong hardware bits, leading to unstable link training, failed hotplug recovery, intermittent blanking, bad margining results, or broken suspend/resume.
- Boundary registers are incomplete in this chunk. `RAWLANE2_DIG_RX_FW_XF_OVRD_IN_1` starts before line 141616, and `RAWLANE3_DIG_FSM_SKIP_RX_DCC_RANGE_RATE_CAL` continues after line 144082.
- Reserved-bit handling matters. Many fields include `RESERVED_*` masks; callers should preserve reserved bits unless the hardware specification permits writing them.
- Lane-copy hazards are high. Raw lane 2 and raw lane 3 blocks are structurally similar, but using a lane 2 field name with a lane 3 address, or vice versa, would target the wrong lane semantics.
- TX/RX and PCS/FW/PMA naming is dense and repetitive. Confusing status vs clear registers, override value vs override enable fields, input vs output transfer fields, or TX vs RX PMA paths can produce difficult hardware failures.
- Side-effecting fields need precise masks. IRQ clears, rate acknowledgements, phase updates, FSM jumps, CR locks, MPLL restart calibration, and skip/fast controls can change hardware state machines immediately.
- Calibration skip controls can mask real PHY problems. Incorrect skip bits may pass simple boot tests but fail at high link rates, after temperature drift, after resume, or during retraining.
- Firmware/hardware ABI compatibility is implicit. These generated names and bit positions are part of a contract between kernel driver code, firmware-assisted flows, and the DCN 3.2 PHY hardware.

## Test Signals

Useful validation signals for this chunk combine compile-time checks, generated-header consistency, and hardware behavior:

- Build AMDGPU Display Core with DCN 3.2 support enabled and ensure all referenced `C20_PHY_CR2_RAWLANE2` and `C20_PHY_CR2_RAWLANE3` field symbols resolve through the register helper macros.
- Run generated-register checks that paired `_SHIFT` and `_MASK` definitions exist for complete in-scope registers, masks fit expected register widths, repeated raw-lane families are lane-consistent, and boundary registers are reconciled with adjacent chunks.
- Compare numeric values against the authoritative C20 PHY register database, with extra focus on IRQ clear/ack bits, PMA transfer fields, firmware handshake fields, RX margining/adaptation controls, and FSM skip/fast bits.
- Exercise DisplayPort link training and retraining across supported rates and lane counts on DCN 3.2 hardware, including hotplug, link loss/recovery, MST where available, high-bandwidth modes, suspend/resume, and power-cycle paths.
- Validate IRQ behavior by masking, enabling, triggering, acknowledging, and clearing TX/RX rate/reset/request/adaptation/margining/loopback/rtune/termination/lane-mode events; failures may appear as missed events or stuck interrupt status.
- Inspect register dumps before and after PHY power-up, retraining, and power-down to confirm that persistent override/control fields and volatile readback fields decode coherently through these masks.
- Stress RX adaptation and margining by checking FOM, reference-error, IQ/phase code readbacks, margin deltas/status/errors, CDR detection, and PPM drift after link-rate changes.
- Validate TX-side PMA and calibration paths by observing rtune, termination, lane mode, reset/request, clock control, firmware power-up done, and MPLL restart calibration fields during mode changes and resume.

## Chunk-Specific Summary

Lines 141616-144082 define generated DCN 3.2.0 C20 PHY `CR2` raw-lane bit positions and masks for the end of raw lane 2 RX/FSM control and the beginning-to-middle of raw lane 3 TX/RX/FSM control. The content is a register ABI, not executable logic. Correctness depends on exact generated values, careful reserved-bit preservation, lane-instance consistency, and hardware validation across PHY link training, firmware handshakes, RX adaptation, margining, interrupts, PMA transfers, calibration shortcuts, and suspend/resume.
