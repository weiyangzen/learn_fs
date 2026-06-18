# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 173203-175667

## Purpose

This chunk is a generated AMD DCN 3.2.0 register shift/mask slice. It contains C preprocessor metadata only: `__SHIFT` macros for field low-bit positions, `_MASK` macros for raw bit masks, and `//<REGISTER>` comments that group those fields by hardware register. It defines no executable code, structs, enums, functions, branches, locks, allocations, or direct MMIO operations.

The range covers C20 PHY CR3 raw-lane digital control metadata. It starts in the tail of `C20_PHY_CR3_RAWLANE1_DIG_RX_PCS_XF_CNTX_CFG_7`, continues through raw lane 1 RX PCS context, RX firmware-crossbar, RX IRQ, RX control, RX PMA-crossbar, and FSM fields, then switches to raw lane 2 TX PCS/firmware/IRQ/control/PMA fields and raw lane 2 RX PCS/firmware/IRQ/control/PMA/FSM fields. The final visible register is partial: `C20_PHY_CR3_RAWLANE2_DIG_FSM_SKIP_RX_FULL_RATE_STARTUP_CAL` is missing its reserved mask in this chunk.

The source tree path is under a local `ceph-client` mirror, but this header belongs to the AMDGPU display hardware register metadata set, not to Ceph filesystem logic.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.
- `//<REGISTER>` comments identify the hardware register whose field macros follow.

This assigned window contains 2,465 physical lines, 2,099 `#define` lines, 1,046 shift macros, 1,053 mask macros, and 366 register comment groups. The shift/mask counts differ because the chunk begins and ends inside register definitions.

Major register families visible here include:

- `C20_PHY_CR3_RAWLANE1_DIG_RX_PCS_XF_CNTX_CFG_*`: tail of RX PCS context configuration, including signal detect thresholds, LFPS filtering, termination control, DCC/VREG bypass, continuous adaptation/off-cancel controls, and `UNIQUE_ID`.
- `C20_PHY_CR3_RAWLANE1_DIG_RX_FW_XF_*`: raw lane 1 RX firmware-crossbar reset/request, pstate, low-power detect, rate, width, DFE bypass, adaptation request, delta-IQ, ACK/RX-valid override, adaptation FOM/ACK, TX pre/main/post direction feedback, RX clock gating/reset, and output ACK metadata.
- `C20_PHY_CR3_RAWLANE1_DIG_RX_IRQ_CTL_*`: masks, enables, status bits, and clear bits for RX reset, request, rate, pstate, adaptation request/disable, termination control, and margining events such as IQ start, VDAC start, error clear, init, finish, and global IRQ.
- `C20_PHY_CR3_RAWLANE1_DIG_RX_CTL_*`: receive control/status fields for termination code, off-cancel/adaptation continuous status, adaptation mode/selection, PPM drift, CDR detection, PMA misc control, adaptation FOM/reference errors, IQ adaptation left/right, phase-adjust linear/map values and update controls, margin deltas/status/error, FSM control, rate IRQ acknowledgment, and IQ linear/step code read/write.
- `C20_PHY_CR3_RAWLANE1_DIG_RX_PMA_XF_*`: RX PMA crossbar ACK/RX-valid override and simple reset/request input metadata.
- `C20_PHY_CR3_RAWLANE1_DIG_FSM_*`: firmware state-machine override/jump/control, memory breakpoint and monitor fields, firmware status/config stage, scratch registers, CR lock, fast-mode capability flags, TX/RX fast controls, many `SKIP_*` calibration/adaptation controls, and RX calibration status.
- `C20_PHY_CR3_RAWLANE2_DIG_TX_PCS_XF_*`: raw lane 2 TX PCS lane loopback/link-number overrides, reset/request/pstate/LPD/data/invert/clock-ready/beacon/MPLL controls, deskew/recalibration controls, TX de-emphasis/pre/main/post/electrical-idle symbols, and TX context configuration for EQ, SSC, TX IDs, voltage levels, slew, common-mode, and unique IDs.
- `C20_PHY_CR3_RAWLANE2_DIG_TX_FW_XF_*`: raw lane 2 TX firmware-crossbar reset/request, pstate, LPD, rate, voltage swing, TX pre/main/post, coefficient index/update, ACK override, lane number, input, and output ACK fields.
- `C20_PHY_CR3_RAWLANE2_DIG_TX_IRQ_CTL_*`: reset-return request plus TX IRQ mask/enable/status/clear fields for rate, reset, request, RX-to-TX parallel loopback enable/disable, RTUNE, termination control, and lane transceiver mode.
- `C20_PHY_CR3_RAWLANE2_DIG_TX_CTL_*` and `TX_PMA_XF_*`: TX FSM control, clock control, off-cancel status, rate IRQ acknowledgment, termination code, firmware power-up done, MPLL restart calibration controls, PMA lane/supplemental overrides, RTUNE controls, and TX PMA reset/request handshakes.
- `C20_PHY_CR3_RAWLANE2_DIG_RX_PCS_XF_*`: raw lane 2 RX PCS reset/request, pstate, LPD, data enable, invert, CDR SSC, adaptation request/in-progress, margin IQ/VDAC/in-progress/error clear, recal bank select, context select, ACK override, and RX context configuration for equalization, AFE, DFE, CDR VCO, rate/reference load, width/VCO load, signal detect thresholds, term control, bypasses, continuous adaptation, and unique ID.
- `C20_PHY_CR3_RAWLANE2_DIG_RX_FW_XF_*`, `RX_IRQ_CTL_*`, `RX_CTL_*`, `RX_PMA_XF_*`, and `FSM_*`: raw lane 2 mirrors of the lane 1 RX firmware-crossbar, IRQ, receive-control, PMA-crossbar, and FSM/debug/fast/skip metadata.

The field layouts are mostly 16-bit register layouts. Explicit reserved masks such as `RESERVED_15_1`, `RESERVED_15_4`, `RESERVED_15_8`, `RESERVED_15_10`, and `RESERVED_15_14` document bits that masked-write helpers should preserve unless the hardware specification says otherwise.

## Control Flow

There is no runtime control flow in this header. Runtime use is indirect:

1. DCN 3.2.0 display code includes generated offset and shift/mask headers for the ASIC generation.
2. Register-table macros and low-level helpers combine register addresses from `dcn_3_2_0_offset.h` with these masks and shifts.
3. Driver helpers such as field-update/read macros use the constants to build masked MMIO reads and writes.
4. The actual sequencing is implemented by display/link/PHY code, firmware, and hardware state machines.

The macros in this chunk do not encode ordering. Consumers must still sequence reset/request/ACK handshakes, pstate/rate/width transitions, DFE bypass, clock gating, deskew/recalibration, TX voltage/coefficient programming, RX adaptation, margining, interrupt mask/enable/status/clear operations, PMA override setup, FSM debug controls, and calibration skip/fast paths according to the PHY programming model.

## State And Persistence Behavior

This file stores no software state and persists nothing by itself. It describes MMIO-backed display PHY state:

- Raw lane 1 RX PCS context, firmware-crossbar, interrupt, receive-control, PMA-crossbar, and FSM/debug state.
- Raw lane 2 TX PCS, TX firmware-crossbar, TX IRQ, TX control, and TX PMA state.
- Raw lane 2 RX PCS, RX firmware-crossbar, RX IRQ, RX control, RX PMA, and FSM/debug state.
- Banked or staged hardware behavior implied by context select, recalibration bank select, firmware scratch registers, breakpoint/monitor fields, fast-mode flags, and `SKIP_*` calibration/adaptation fields.

Side effects are hardware-defined and not represented by the macro names alone. Some fields are persistent configuration bits, some are status or telemetry, some are sticky IRQ latches, some are write-one-to-clear fields, some may be self-clearing triggers, and some are firmware-owned scratch/debug state. Correct persistence expectations must come from the register spec and the driver code that accesses the registers.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which supplies the corresponding register offsets. A valid-looking shift/mask macro paired with the wrong offset, lane prefix, or field name can compile cleanly while programming the wrong PHY bit.

Integration points are generated-register consumers in AMDGPU Display Core and DMUB/DCN32 code. Direct include users for the DCN 3.2.0 generated register headers in this tree include DCN32 resource setup, DMUB DCN32 support, IRQ service setup, GPIO translation/factory code, clock manager code, and some GMC code. Functional users are the low-level display/link/PHY paths that perform link bring-up, retraining, power transitions, firmware handshakes, margining diagnostics, and calibration debug.

The same C20 PHY/DPCS-style register naming is mirrored in other generated AMD register headers, especially DPCS shift/mask headers for nearby ASIC blocks. That makes cross-header comparison useful for detecting generator drift, but also increases the risk of copying a valid macro from the wrong lane, CR instance, or block.

## Risks And Edge Cases

- Generated-header drift is the central risk. Wrong shifts or masks can compile but corrupt PHY configuration, IRQ handling, link training, margining, or calibration readback.
- The chunk is not standalone. It starts after the shift definitions for `RAWLANE1_DIG_RX_PCS_XF_CNTX_CFG_7` and ends before the final reserved mask for `RAWLANE2_DIG_FSM_SKIP_RX_FULL_RATE_STARTUP_CAL`.
- Lane prefixes are easy to misread. `RAWLANE1` and `RAWLANE2` describe distinct hardware lanes within `C20_PHY_CR3`; a correct field name with the wrong lane prefix can silently target the wrong register instance.
- TX and RX IRQ blocks contain separate mask, enable, status, and clear registers. Mixing status and clear fields, or clearing before sampling sticky state, can hide rate, reset, request, loopback, RTUNE, termination, pstate, adaptation, or margining events.
- Override fields can force behavior normally owned by firmware or hardware FSMs. Reset, request, pstate, rate, width, voltage, TX coefficient, DFE bypass, adaptation request, ACK, RX-valid, loopback, and lane-mode overrides can destabilize link training if applied at the wrong time.
- Calibration skip and fast-mode flags can reduce bring-up coverage. Incorrect `SKIP_*` or `FAST_*` values may only fail under particular rates, lane widths, connectors, temperature/voltage corners, suspend/resume, or retraining cases.
- Reserved masks are explicit and should be preserved by masked writes. Blind full-register writes risk changing undocumented hardware behavior.
- Access type is not encoded here. Read-only status, firmware scratch, write-one-to-clear IRQ, self-clearing trigger, and persistent configuration fields all look like ordinary mask/shift macros in this file.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU Display Core with DCN32 support enabled so malformed generated symbols surface in resource, DMUB, IRQ, clock, GPIO, and low-level register users.
- Mechanically compare this line range against the authoritative AMD register database or a regenerated `dcn_3_2_0_sh_mask.h`.
- Cross-check `dcn_3_2_0_offset.h` so every visible `C20_PHY_CR3_RAWLANE1` and `C20_PHY_CR3_RAWLANE2` register name has the expected address and field layout pairing.
- Compare mirrored C20 PHY/DPCS generated headers for equivalent lane/register families when investigating generator or copy drift.
- On DCN32 hardware, exercise DisplayPort/PHY link bring-up, retraining, hotplug, lane-width changes, rate changes, power-state transitions, suspend/resume, and DFE-bypass/adaptation paths.
- Validate TX and RX IRQ behavior by inducing or observing reset, request, rate, pstate, loopback, RTUNE, termination, adaptation, and margining events; mask, enable, status, and clear bits should decode consistently.
- Run margining and calibration diagnostics where available, watching RX margin IQ/VDAC/init/finish/error/global events, RX adaptation FOM/reference errors, IQ code readbacks, CDR detector status, and calibration skip/fast-mode effects.
- Inspect register dumps before and after PHY bring-up, retrain, power transitions, and debug operations. Masked writes should affect only intended fields, reserved bits should remain stable, and lane 1/lane 2 values should not be swapped.

## Cross-Chunk Notes

The merge lane should combine this with the previous chunk for the full `C20_PHY_CR3_RAWLANE1_DIG_RX_PCS_XF_CNTX_CFG_7` definition and with the following chunk for the completed `C20_PHY_CR3_RAWLANE2_DIG_FSM_SKIP_RX_FULL_RATE_STARTUP_CAL` definition plus the remaining raw lane 2 FSM skip/status fields. This document is intentionally limited to `subset-b-002000`.
