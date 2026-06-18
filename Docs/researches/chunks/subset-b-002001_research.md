# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 175668-178124

## Purpose

This chunk is generated AMD DCN 3.2.0 register field metadata for the C20 PHY CR3 digital lane/register interface. It contains C preprocessor constants for bit shifts (`__SHIFT`) and masks (`_MASK`) used to encode and decode hardware fields in the C20 PHY register file. The range is not executable code; it is a hardware ABI layer consumed by AMDGPU display/DMUB/link code together with matching register offsets from `dcn_3_2_0_offset.h`.

The slice contains 2,101 `#define` entries: 1,051 shift constants and 1,050 mask constants. It starts in the tail of `C20_PHY_CR3_RAWLANE2_DIG_FSM_*` RX calibration skip/status fields, covers a broad `C20_PHY_CR3_RAWLANE3` TX/RX PCS, firmware, IRQ, control, PMA, and FSM surface, then enters the `C20_PHY_CR3_RAWLANEAON0` always-on TX/RX firmware and calibration registers. The final line stops inside `C20_PHY_CR3_RAWLANEAON0_DIG_RX_DCC_FULL_DATA_BANK_1`, so adjacent chunks are needed for the complete always-on RX calibration-bank series.

Although this source tree is under a local `ceph-client` mirror, this header belongs to the AMDGPU display driver register database and has no Ceph or distributed-filesystem logic.

## Important APIs, Types, And Register Groups

There are no functions, structs, enums, variables, includes, allocation paths, locks, or callbacks in this chunk. The interface is the generated macro namespace:

- `<register>__<field>__SHIFT`: starting bit position for a hardware field.
- `<register>__<field>_MASK`: bit mask for that field in its register word.
- Reserved fields are also emitted as masks/shifts, documenting register width and layout but not granting safe write permission.

Major register groups in this range:

- `C20_PHY_CR3_RAWLANE2_DIG_FSM_SKIP_RX_*` and `RX_CAL_STATUS`: tail of raw lane 2 FSM controls for skipping RX error, bypass, VGA slicer/buffer, DFE coarse/fine adaptation, DCC range/rate/startup, CTLE/ATT/VGA startup, margining, and reset-calibration done status.
- `C20_PHY_CR3_RAWLANE3_DIG_TX_PCS_XF_*`: TX PCS transfer/override/input/output/context fields for reset/request handshakes, pstate, low-power/data enable, invert, clock ready, beacon, MPLL selection, detect-RX request, clock/lane deskew, recalibration force/skip, lane number, rate, width, DCC, termination, boost, and unique ID.
- `C20_PHY_CR3_RAWLANE3_DIG_TX_FW_XF_*`: firmware-facing TX transfer fields for reset, request, pstate, low-power/data enable, calibration, rate/width, VCO, RX detect, power-on reset, lane mode, termination, and firmware input/output handshakes.
- `C20_PHY_CR3_RAWLANE3_DIG_TX_IRQ_CTL_*` and `TX_CTL_*`: TX interrupt mask/enable/status/clear bits for rate, reset, request, loopback enable/disable, retune, termination, and lane transceiver mode, plus TX FSM control, clock control, off-cancel continuous status, rate IRQ ack, term code, firmware power-up done, and MPLLA/MPLLB restore-calibration controls.
- `C20_PHY_CR3_RAWLANE3_DIG_TX_PMA_XF_*`: TX PMA lane/supervisor override/input/output fields for power/reset/RTUNE/termination/driver controls and support signals.
- `C20_PHY_CR3_RAWLANE3_DIG_RX_PCS_XF_*`: RX PCS override/input/output/context fields for reset, request, pstate, adaptation request, DFE bypass, termination, data enable, invert, rate, width, signal detect, CDR, adaptation FSM, VCO, ref/load values, data-valid controls, power gating, and context configuration.
- `C20_PHY_CR3_RAWLANE3_DIG_RX_FW_XF_*`: RX firmware-facing override/input/output controls, adaptation ack/FOM, TX pre/main/post direction feedback, and RX firmware clock control.
- `C20_PHY_CR3_RAWLANE3_DIG_RX_IRQ_CTL_*` and `RX_CTL_*`: RX interrupt mask/enable/status/clear bits for reset/request/rate/pstate/adaptation and margining events, plus RX term/off-cancel/adaptation status, adaptation mode/select, PPM drift, CDR detect, PMA misc, phase-adjust update, margin delta/status/error, FSM control, IQ code read/write, and rate IRQ ack.
- `C20_PHY_CR3_RAWLANE3_DIG_RX_PMA_XF_*`: RX PMA override/input/output transfer fields for PMA sideband state.
- `C20_PHY_CR3_RAWLANE3_DIG_FSM_*`: firmware sequencer controls, jump bank, FSM control/status, memory breakpoints, monitor address/status, firmware stage and scratch registers, CR lock, fast-path TX/RX controls, skip bits for TX/RX DCC and RX startup/continuous calibration/adaptation phases, and RX calibration status.
- `C20_PHY_CR3_RAWLANEAON0_DIG_TX_*`: always-on TX firmware states, memory breakpoint, SRAM record controls, calibration algorithm controls, fast flags, high-power protection and transceiver mode overrides, initial power-up done, MPLLA/MPLLB DCC range/full/half calibration bank values, calibration done flags, DCC code readbacks, bank selection, and basic TX input.
- `C20_PHY_CR3_RAWLANEAON0_DIG_RX_*`: always-on RX startup calibration/adaptation algorithm controls, continuous algorithm controls, fast flags, VGEN/signal-detect/AFE trim, reference and DFE VDAC offsets, setup IDAC offsets, AFE CTLE/VGA/buffer offsets, IQ calibration limits/reset/adjust, DCC range/full/half data/bypass/phase bank values, and per-bank calibration done flags.

Representative field conventions:

- Many transfer registers use value/override-enable pairs such as `*_OVRD_EN`, allowing firmware or diagnostic paths to force a hardware signal instead of letting the sequencer drive it.
- IRQ families are split into mask/enable/status and one-bit clear registers, so the same field concept appears in both observation and write-to-clear contexts.
- Calibration fields usually expose algorithm enable/skip controls, banked result storage, status/done bits, and final code values rather than high-level policy.
- Most CR3 raw-lane registers in this chunk are 16-bit field maps, with reserved masks such as `0xFFF0L` or `0xFF00L`; the generated constants still use C integer literals with `L` suffixes.

## Control Flow

This header has no runtime control flow. The effective runtime flow is supplied by AMDGPU display and firmware-support code:

1. DCN 3.2 code includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Register helper macros pair an offset such as `ixC20_PHY_CR3_RAWLANE3_DIG_TX_IRQ_CTL_IRQ_MASK` from the offset header with the shift/mask constants from this file.
3. Link encoder, BIOS transmitter-control, DMUB, or diagnostic code chooses a PHY, lane, link rate, pstate, or calibration action.
4. The chosen code path writes control/override fields, polls status/done/ack fields, handles interrupt bits, or reads calibration/statistic results using these generated masks.

The chunk itself does not encode sequencing. Hardware sequencing requirements remain in the consumer: lane reset ordering, pstate changes, firmware ownership boundaries, TX/RX request/ack handshakes, clock readiness, calibration skip/done handling, write-one-to-clear IRQ behavior, and preservation of reserved bits must all be implemented outside this header.

## State And Persistence Behavior

The file stores no software state and persists nothing to disk. It describes MMIO-backed C20 PHY state, including:

- TX/RX PCS and firmware handshakes for reset, request, ack, data enable, pstate, low-power state, rate/width, clock readiness, data validity, loopback, signal detect, and CDR/VCO state.
- Interrupt state for TX and RX events, including mask bits, enable flags, sticky status bits, and explicit clear bits.
- TX/RX control state for FSM control, rate IRQ ack, term codes, off-cancel/adaptation status, margining, PPM drift, IQ code read/write, and PMA miscellaneous state.
- Firmware sequencer state, including jump bank, breakpoints, monitor/status, firmware stage, scratch registers, CR lock, and fast/skip controls for calibration and adaptation paths.
- Always-on calibration state, including TX MPLLA/MPLLB DCC banked values, calibration done flags, DCC code readbacks, RX VDAC/IDAC offsets, IQ calibration ranges, DCC full/half data/bypass/phase values, and per-bank done flags.

Persistence is hardware-defined. Configuration and override bits may remain until another MMIO write, link disable/re-enable, power gating, suspend/resume, firmware reinitialization, or ASIC reset. Status, IRQ, clear, done, and monitor fields may be read-only, sticky, self-clearing, or write-one-to-clear depending on the register. This chunk only provides bit positions and masks, so consumers must know the side effects from hardware documentation or established driver sequences.

## Dependencies And Integration Points

This chunk depends on the generated DCN/DPCS register ecosystem:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h` supplies the matching indirect register offsets for C20 PHY CR3. In the nearby offset block, `C20_PHY_CR3_RAWLANE3_DIG_TX_IRQ_CTL_IRQ_MASK` maps to `0x2621` and `C20_PHY_CR3_RAWLANE3_DIG_RX_IRQ_CTL_IRQ_MASK` maps to `0x26c0`; this chunk supplies the fields inside those registers and many neighboring CR3 registers.
- AMD display register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and generation-specific `SF(...)`/register-list macros depend on the offset and shift/mask headers agreeing exactly.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c` includes the DCN 3.2 offset and shift/mask headers to build DMUB register metadata. The exact C20 PHY fields in this chunk are low-level hardware definitions rather than common high-level call-site names, but they share that generated include path.
- Link/resource/BIOS paths around DCN 3.2 assign link encoders and route transmitter-control requests. Those paths carry PHY IDs, link rates, lane counts, signal type, and power-transition state that ultimately determine whether host code, BIOS, or DMUB firmware owns PHY programming.
- The same style of C20 PHY field definitions appears in generated DPCS headers in the AMDGPU tree, so consistency between DCN and DPCS views is important for firmware/debug tooling and indirect register access.

## Risks And Edge Cases

- Shift/mask drift is the main risk. These are untyped preprocessor constants; an incorrect bit position can compile cleanly while forcing the wrong reset, pstate, clock, calibration, or interrupt field.
- Lane-copy errors are plausible. CR3 raw lanes share repeated register families, and this chunk crosses from raw lane 2 tail fields to raw lane 3 plus always-on state. A copied macro mismatch can affect only one lane or one PHY instance.
- Override-enable fields are high impact. Bad masks can leave reset, request, data enable, pstate, VCO, CDR, signal detect, deskew, recalibration, termination, or PMA state forcibly overridden after a modeset or suspend/resume transition.
- IRQ and clear registers are side-effect-sensitive. Mis-masked clear bits can drop real events or fail to clear sticky status, causing missed training/margining events or timeout loops.
- Calibration-bank fields are stateful and easy to misread. TX MPLLA/MPLLB DCC banks and RX IQ/DCC/VDAC/IDAC banks need correct bank selection, done-bit interpretation, and full/half-rate pairing.
- Reserved masks are generated for completeness. Software must not write reserved fields unless the hardware specification explicitly allows it; read-modify-write helpers should preserve reserved bits.
- The chunk boundaries are artificial. The first line is already inside a raw lane 2 register group, and the final line stops inside the always-on RX DCC full-data bank 1 group. The final per-file report should merge adjacent chunks before making complete claims about CR3 raw-lane or always-on calibration coverage.

## Test Signals

Useful validation signals are primarily build, register-generation, and hardware-integration signals:

- Build coverage: AMDGPU display/DCN 3.2 and DMUB code compiles with no missing, renamed, or duplicate generated C20 PHY field macros.
- Generated-header consistency: every shift in this slice has the expected matching mask, and the field names align with the corresponding `dcn_3_2_0_offset.h`/DPCS register database entries.
- Register-table sanity: generated offset/shift/mask tables keep CR3 raw lane 2, CR3 raw lane 3, and `RAWLANEAON0` entries in the correct PHY/lane namespace.
- Link bring-up: DP/HDMI/eDP links using CR3 PHY lanes train reliably across link rates, lane counts, hotplug, blank/unblank, and modeset transitions.
- PHY power behavior: pstate changes, suspend/resume, idle power, panel/link wake, and firmware PHY-init waits do not leave lanes stuck in reset, request, low-power, or missing-clock states.
- Calibration behavior: TX DCC, MPLLA/MPLLB calibration done flags, RX DCC, RX IQ calibration, VGEN/signal-detect, AFE/DFE offset calibration, and margining status converge without unexpected timeout or sticky abort/IRQ bits.
- Interrupt behavior: TX/RX rate/reset/request/adaptation/margining IRQ status bits can be masked, enabled, observed, and cleared without spurious repeats or lost events.
- Firmware ownership behavior: configurations where DMUB or BIOS owns PHY programming continue to initialize displays, confirming that host-side metadata and firmware-side register expectations remain compatible.
