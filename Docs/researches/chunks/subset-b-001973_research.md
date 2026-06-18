# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 107595-110029

## Scope

This chunk is a generated AMD DCN 3.2.0 register-field shift/mask header slice. It contains preprocessor constants only: `#define` entries for field bit shifts and register-positioned masks, plus `//<REGISTER>` comments that group definitions by hardware register. There are no C functions, structs, enums, branches, loops, locks, allocations, or software persistence in this range.

The requested range covers 2,435 source lines, 2,127 `#define` lines, 1,064 `_SHIFT` macros, 1,063 `_MASK` macros, and 308 register grouping comments. It begins in the middle of `C20_PHY_CR1_RAWLANE2_DIG_TX_PCS_XF_LANE_IN_0`, where only the last two shift definitions and all four masks are visible. It ends in the middle of `C20_PHY_CR1_RAWLANE3_DIG_RX_FW_XF_OVRD_OUT_0`, after the `ACK` and `ACK_OVRD_EN` masks but before the remaining masks for that register.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU display-controller hardware metadata, not Ceph filesystem logic. The chunk specifically covers DCN 3.2 C20 PHY CR1 raw-lane digital and PMA/FSM register fields for lane 2 and the start of lane 3.

## Purpose

The macros define the bit layout used by AMDGPU Display Core code when programming C20 PHY CR1 raw lanes through MMIO register helpers. Companion offset headers provide register addresses; this file supplies field positions and masks so generated register tables and token-pasting helpers can pack values, update individual fields, decode status, and acknowledge hardware events.

The major hardware surfaces represented here are:

- RAWLANE2 TX PCS transfer interface fields for lane selection, request/reset handshakes, power state, low-power detect, data enable, inversion, clock readiness, beacon/MPLL controls, deskew, recalibration, context selection, acknowledgements, and context configuration.
- RAWLANE2 TX firmware transfer interface fields for reset/request handshakes, power/rate/width controls, common-mode, calibration bypasses, drive swing/pre/post cursor settings, lane mode, term control, RTUNE, unique IDs, valid bits, and lane numbering.
- RAWLANE2 TX IRQ control/status/clear families for rate, reset, request, loopback enable/disable, RTUNE, termination-control, and transceiver-mode events.
- RAWLANE2 TX control/status fields for FSM power state and change gating, clock control, continuous offset cancellation status, rate IRQ acknowledgement, termination code, firmware power-up completion, and MPLL A/B resistor calibration controls.
- RAWLANE2 TX PMA transfer fields for lane/supervisor override, data-valid handshakes, PLL ready state, RTUNE controls, and PMA lane request/status signaling.
- RAWLANE2 RX PCS and firmware transfer interfaces for reset/request, power/rate/width, adaptation, margining, CDR/SSC, DFE bypass, EQ/AFE/CDR/sigdet/context configuration, acknowledgement, `RX_VALID`, FOM, TX coefficient direction, and clock control.
- RAWLANE2 RX IRQ control/status/clear families for reset, request, rate, pstate, adaptation request/disable, termination-control, margin IQ/VDAC start, margin error clear, margin init/finish/global events.
- RAWLANE2 RX control/status fields for termination code, continuous offset cancellation/adaptation status, adaptation mode/select/FOM, PPM drift, CDR detect, PMA misc control, phase adjustment, margin delta/status/error, FSM control, rate IRQ acknowledgement, and IQ/phase code read/write/update paths.
- RAWLANE2 digital FSM control, debug, scratch, lock, fast-path, skip-calibration, and RX calibration status fields.
- The start of equivalent RAWLANE3 TX PCS/TX FW/TX IRQ/TX control/TX PMA/RX PCS/RX FW definitions.

This is generated data, but it is part of the hardware ABI. A wrong shift or mask can compile successfully while causing runtime MMIO writes to touch the wrong lane, field, control bit, status bit, or acknowledgement bit.

## Important Macro Families

The naming convention in this range is the standard generated AMD register layout:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask already shifted into register position.
- `//<REGISTER>` comments mark each register block whose fields follow.

No callable APIs or C types are declared here. The important register namespaces are the lane-scoped C20 PHY raw-lane families below.

## RAWLANE2 TX PCS And TX Firmware Interfaces

The RAWLANE2 TX PCS transfer interface starts with the tail of `C20_PHY_CR1_RAWLANE2_DIG_TX_PCS_XF_LANE_IN_0`, including loopback enable masks and `LANE_LINK_NUM`. Complete PCS groups then define:

- `DIG_TX_PCS_XF_OVRD_IN_0..3` for overriding reset/request, pstate, low-power detect, data enable, polarity inversion, clock ready, beacon enable, MPLL enable, master MPLL A/B state, detect-RX request, clock/lane deskew, recalibration force/skip, and context select.
- `DIG_TX_PCS_XF_IN_0..2` for the non-override reset/request, pstate, low-power detect, data enable, inversion, clock ready, beacon/MPLL, master MPLL, detect-RX, deskew, recalibration, and context select inputs.
- `DIG_TX_PCS_XF_OVRD_OUT_0` and `DIG_TX_PCS_XF_OUT_0` for acknowledgement and detect-RX result readback/override.
- `DIG_TX_PCS_XF_CNTX_CFG_0..2` for per-context transmit rate, width, wide-transfer alignment, MPLL B select, TX regulator bypass, voltage/current boost, KR driver enable, continuous offset cancellation, misc bits, DCC range/bypass, termination control, and TX unique ID.

The TX firmware transfer interface mirrors part of the PCS handshake while exposing firmware-oriented lane controls:

- `DIG_TX_FW_XF_OVRD_IN_0..2` for overriding reset/request, pstate, rate, width, common-mode, DCC calibration bypass, calibration-load enable, voltage boost, current boost, driver enable, pre/main/post cursor values, low-power detect, and term control.
- `DIG_TX_FW_XF_LANE_NUMBER` and `DIG_TX_FW_XF_IN_0` for lane identity, reset/request, pstate, rate, width, common-mode, calibration bypass/load, boost/drive values, LPD, and term control.
- `DIG_TX_FW_XF_OVRD_OUT_0` and `DIG_TX_FW_XF_OUT_0` for acknowledgement, lane transceiver mode, RTUNE, and valid/status signals.

Together these fields describe the control plane used by driver/firmware sequencing to prepare a PHY TX lane for a selected link rate and width, choose PLL behavior, configure electrical drive parameters, and exchange request/acknowledge state.

## RAWLANE2 TX IRQ, Control, And PMA

The RAWLANE2 TX IRQ control block defines interrupt masking, enable flags, status bits, and clear bits:

- `DIG_TX_IRQ_CTL_RESET_RTN_REQ` exposes reset-return request and pstate-return status.
- `DIG_TX_IRQ_CTL_IRQ_MASK` and `DIG_TX_IRQ_CTL_IRQ_EN_FLAGS` cover masks and enables for rate, reset, request, RX-to-TX parallel loopback enable/disable, RTUNE, TX term control, and lane transceiver mode events.
- Individual `*_IRQ` and `*_IRQ_CLR` registers expose status/count or write-to-clear fields for each event class.

The TX control block defines sequencing state and calibration controls:

- `DIG_TX_CTL_FSM_CTL` carries TX pstate and pstate-change disable.
- `DIG_TX_CTL_CLK_CTL` controls TX clock, fractional divide, and clock enable.
- `DIG_TX_CTL_OFFCAN_CONT_STATUS`, `DIG_TX_CTL_RATE_IRQ_ACK`, `DIG_TX_CTL_TERM_CODE`, and `DIG_TX_CTL_FW_PWRUP_DONE` expose continuous offset-cancellation status, rate IRQ acknowledgement, termination code, and firmware power-up status.
- `DIG_TX_CTL_MPLLA_RSTR_CAL_CTL` and `DIG_TX_CTL_MPLLB_RSTR_CAL_CTL` define MPLL A/B resistor calibration read/write selection, reset, enable, and code fields.

The TX PMA transfer interface then covers the analog/PMA-side handshake:

- `DIG_TX_PMA_XF_LANE_OVRD_IN_0`, `DIG_TX_PMA_XF_LANE_OVRD_OUT_0`, and `DIG_TX_PMA_XF_LANE_RTUNE_CTL` override lane valid and RTUNE behavior and expose/drive lane valid and RTUNE values.
- `DIG_TX_PMA_XF_SUP_OVRD_IN_0`, `DIG_TX_PMA_XF_SUP_IN_0`, and `DIG_TX_PMA_XF_SUP_IN_1` carry supervisor request, PLL ready state, and retune request controls.
- `DIG_TX_PMA_XF_OVRD_OUT_0` and `DIG_TX_PMA_XF_IN_0` expose PMA output valid and lane request signaling.
- `DIG_TX_PMA_XF_LANE_RTUNE_CTL_1` contains an additional reserved/RTUNE-related mask region.

These definitions are sequencing-sensitive because firmware and driver code need to distinguish event status, event clear, enable, mask, data-valid, and override-enable fields.

## RAWLANE2 RX PCS And RX Firmware Interfaces

The RAWLANE2 RX PCS interface defines receive-side handshake, adaptation, margining, and context fields:

- `DIG_RX_PCS_XF_OVRD_IN_0..4` override reset/request, pstate, low-power detect, data enable, inversion, CDR SSC enable, adaptation request/in-progress, margin IQ, margin VDAC, margin in-progress/error clear, recalibration bank select, context select, rate, and width.
- `DIG_RX_PCS_XF_IN_0..3` provide the non-override equivalents for reset/request, pstate, low-power/data/invert/CDR/adaptation/margin fields, margin VDAC/error/recalibration fields, and context select.
- `DIG_RX_PCS_XF_OVRD_OUT_0` and `DIG_RX_PCS_XF_OUT_0` define acknowledgement override/readback.
- `DIG_RX_PCS_XF_CNTX_CFG_0..8` define receive equalization and CDR context state: attenuation level, VGA gain, CTLE offset/boost/pole/zero, AFE rate/bias/VCM, DFE tap1, DFE bypass, adaptation mode/select, misc bits, delta IQ, CDR VCO config, DCC range, rate, reference load value, divide-by-16.5 clock enable, CDR PPM max, width, VCO load value, signal-detect thresholds/filtering, termination control, DCC bypass, clock regulator bypass, continuous adaptation/offset-cancellation, and unique ID.

The RAWLANE2 RX firmware interface provides firmware-visible controls and status:

- `DIG_RX_FW_XF_OVRD_IN_0..2` override reset/request, pstate, low-power detect, rate, width, DFE bypass, adaptation request, and delta IQ.
- `DIG_RX_FW_XF_IN_0` carries reset/request and delta IQ.
- `DIG_RX_FW_XF_OVRD_OUT_0` and `DIG_RX_FW_XF_OUT_0` handle acknowledgement and `RX_VALID` readback/override.
- `DIG_RX_FW_XF_ADAPT_ACK`, `DIG_RX_FW_XF_ADAPT_FOM`, and `DIG_RX_FW_XF_TXPRE_DIR`/`TXMAIN_DIR`/`TXPOST_DIR` expose adaptation acknowledgement, figure of merit, and requested TX coefficient direction hints.
- `DIG_RX_FW_XF_CLK_CTRL_0` controls RX clock selection, fractional divide, and clock enable.

These fields sit at the boundary between receive PCS state machines, firmware adaptation algorithms, and higher-level link training.

## RAWLANE2 RX IRQ, Control, And PMA

The RAWLANE2 RX IRQ block mirrors the TX model with receive-specific events:

- `DIG_RX_IRQ_CTL_IRQ_MASK` and `DIG_RX_IRQ_CTL_IRQ_EN_FLAGS` cover RX reset, request, rate, pstate, adaptation request/disable, termination-control, margin IQ start, margin VDAC start, margin error clear, margin init, margin finish, and global margin interrupts.
- Individual `*_IRQ` and `*_IRQ_CLR` registers provide event status/count and clear fields.

The RX control and status registers expose the live tuning state:

- `DIG_RX_CTL_TERM_CODE`, `OFFCAN_CONT_STATUS`, `ADAPT_CONT_STATUS`, `ADAPT_MODE`, `ADAPT_SEL`, `PPM_DRIFT`, and `CDR_DET_STATUS` cover termination, continuous calibration/adaptation, adaptation mode selection, drift, and CDR detect status.
- `DIG_RX_CTL_PMA_MISC_CTL` and `DIG_RX_CTL_ADAPT_MODE_OVRD_EN`/`ADAPT_MODE_EN` provide PMA misc and adaptation-mode override gating.
- `DIG_RX_CTL_ADAPT_MM_FOM`, `ADAPT_STARTUP_FOM`, `ADPT_REF_ERR_EVEN`, `ADPT_REF_ERR_ODD`, `RX_ADPT_IQ_LEFT`, and `RX_ADPT_IQ_RIGHT` expose adaptation quality and error measurements.
- `DIG_RX_CTL_PHSADJ_LIN`, `PHSADJ_MAP`, and their update registers control or report phase adjustment codes.
- `DIG_RX_CTL_MARGIN_IQ_DELTA`, `RX_MARGIN_VDAC_DELTA`, `RX_MARGIN_STATUS`, and `RX_MARGIN_ERROR` expose margining offsets and result/error status.
- `DIG_RX_CTL_FSM_CTL`, `RATE_IRQ_ACK`, `IQ_LIN_CODE_WR/RD`, `IQ_STEP_CODE_WR/RD`, and `PHSADJ_LIN_UPDATE_EN` support FSM control, event acknowledgement, and IQ/phase code programming.

The RX PMA transfer interface includes `DIG_RX_PMA_XF_OVRD_OUT_0`, `DIG_RX_PMA_XF_IN_0`, and `DIG_RX_PMA_XF_OVRD_IN_0` for valid, lane request, RX valid, and PMA-side override handshakes.

## RAWLANE2 Digital FSM

The RAWLANE2 digital FSM region is a dense set of control, debug, scratch, fast-path, and skip-calibration registers:

- `DIG_FSM_FSM_OVRD_CTL`, `DIG_FSM_FSM_JMP_BANK`, and `DIG_FSM_FSM_CTL_0` control FSM override, jump bank selection, and state control.
- `DIG_FSM_MEM_BREAKPOINT_0`, `MEM_BREAKPOINT_1`, `MEM_ADDR_MON`, and `STATUS_MON` expose debug breakpoint/address/status monitors.
- `DIG_FSM_FW_CFG_STAGE` and `DIG_FSM_FW_SCRATCH_0..11` provide firmware-visible configuration stage and scratch fields.
- `DIG_FSM_CR_LOCK` controls or reports control-register locking.
- `DIG_FSM_FAST_SUP`, `FAST_TX_*`, and `FAST_RX_*` fields enable or configure fast supervisor, common-mode, RX detect, TX startup calibration, TX/RX power-up, RX VCO wait/calibration, RX continuous calibration/adaptation, and related bypass paths.
- `DIG_FSM_SKIP_TX_*` and many `DIG_FSM_SKIP_RX_*` registers selectively skip TX/RX DCC, AFE, DFE, IQ, phase, signal-detect, VGEN, half/full-rate, error, bypass, VGA, CTLE, attenuation, adaptation reload, and margining operations.
- `DIG_FSM_RX_CAL_STATUS` provides receive calibration status.

This area is especially risky for generic transformations because many fields are intentional one-bit controls with similar names but very different calibration effects.

## RAWLANE3 Start

The second part of the chunk begins equivalent RAWLANE3 definitions:

- TX PCS lane override/input, PCS override/input/output, and PCS context configuration.
- TX firmware override/input/output, lane number, TX IRQ masks/enables/status/clears, TX control, and TX PMA interface.
- RX PCS override/input/output and RX PCS context configuration.
- The start of RX firmware override/input/output fields, ending midway through `C20_PHY_CR1_RAWLANE3_DIG_RX_FW_XF_OVRD_OUT_0`.

The RAWLANE3 fields follow the same structural pattern as RAWLANE2. Instance alignment is an important validation signal: after replacing `RAWLANE2` with `RAWLANE3`, matching complete families should generally retain field names, shifts, and masks unless the hardware specification intentionally differs.

## Control Flow

This header has no executable control flow. Runtime control flow is supplied by AMDGPU display code that includes the matching generated offset and mask headers and expands generated register lists into access helpers.

Typical runtime use is:

1. Link training, PHY bring-up, firmware, or diagnostics code selects the lane and register instance.
2. Generated register-list macros pair an address symbol from an offset header with one or more `_SHIFT`/`_MASK` symbols from this header.
3. Register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WRITE`, and poll/wait helpers pack or decode fields.
4. Hardware latches configuration, advances request/acknowledge handshakes, reports status, raises or clears interrupts, performs calibration/adaptation, updates firmware scratch/status values, or changes PMA/PCS/FSM state.

The ordering rules are not encoded here. Driver code and the hardware programming guide define when to assert reset, request, override-enable, clear, skip-calibration, rate-change, pstate-change, or power-up fields.

## State And Persistence Behavior

The macros are stateless compile-time constants. The state they describe lives in MMIO-backed C20 PHY lane hardware and is affected by modesets, link training, firmware sequencing, hotplug, suspend/resume, PHY reset, power gating, diagnostics, and fault recovery.

Persistent or latched configuration fields in this chunk include pstate/rate/width/context selections, PLL selection/state, TX drive/pre/main/post settings, calibration bypass/skip controls, DFE/CTLE/AFE/CDR/EQ configuration, signal-detect thresholds, clock-control fields, FSM fast-path and skip bits, scratch values, termination controls, and interrupt masks/enables.

Volatile readback/status fields include acknowledgements, valid bits, RX valid, lane requests, PLL ready, transceiver mode, RTUNE status, offcan/adaptation status, PPM drift, CDR detect, adaptation FOM/reference errors, IQ/phase readback, margin status/error, breakpoint/address/status monitors, calibration status, and IRQ event/status fields.

Side-effecting or sequencing-sensitive fields include reset, request, override-enable, IRQ clear, rate IRQ acknowledgement, adaptation request/disable, margin error clear, FSM override/jump/control fields, control-register lock, power-up done/status controls, calibration load/reset/enable controls, and the many skip-calibration bits. Treating these as ordinary stable booleans can lose events, clear diagnostics, force invalid state transitions, or skip required PHY calibration.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.2.0 register address definitions, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`

The shift/mask header and offset header must be generated from the same register database. The integration points are mainly in AMDGPU Display Core and hardware sequencing code, including:

- DCN 3.2 resource/register table construction for C20 PHY lane instances.
- Link encoder, PHY, and hardware sequencer paths that program DisplayPort/USB-C PHY lane rate, width, pstate, PLL, TX swing, and calibration settings.
- Firmware or microcontroller coordination paths that use the `*_FW_XF_*`, scratch, request/acknowledge, valid, and FOM fields.
- IRQ service and diagnostic paths that mask, enable, read, and clear TX/RX lane interrupts.
- Link training and margining logic that uses RX adaptation, margin IQ/VDAC, TX coefficient direction, CDR, equalization, and FOM fields.
- Suspend/resume and power-management paths that must preserve or reprogram lane state, pstate, clock, reset, and calibration controls.
- Debug tooling that reads FSM status, breakpoints, scratch registers, adaptation measurements, calibration status, and raw lane status.

Because these are preprocessor constants, missing or renamed macros usually fail at build time. Incorrect numeric values, swapped lane prefixes, or shifted masks can compile cleanly and only appear as hardware bring-up, training, calibration, or interrupt failures.

## Risks And Edge Cases

- The chunk boundaries are artificial. The first visible register is partial (`RAWLANE2_DIG_TX_PCS_XF_LANE_IN_0`), and the final register is partial (`RAWLANE3_DIG_RX_FW_XF_OVRD_OUT_0`).
- RAWLANE2 and RAWLANE3 contain highly repetitive families. A generator or manual merge error can swap lane prefixes while preserving valid C macro syntax.
- Request, acknowledge, override value, and override-enable fields are adjacent throughout the PCS/FW/PMA transfer interfaces. Confusing value bits with enable bits can force hardware state instead of reporting it.
- IRQ masks, enables, status fields, and clear fields are separate registers with similar names. Generic tooling must not collapse them.
- TX and RX rate/width/pstate fields are repeated across PCS context, firmware input, override input, and FSM/control paths. The correct consumer depends on lane state and sequencing.
- Calibration skip and fast-path fields may be useful for debug or special bring-up flows but risky in normal operation. Wrong masks can disable required TX DCC, RX AFE/DFE/IQ/phase/VCO/sigdet/VGEN, or margining operations.
- Analog PHY fields such as TX drive levels, term control, RTUNE, MPLL calibration, EQ/CTLE/DFE/AFE/CDR settings, and signal-detect thresholds affect physical link quality. A wrong bit can cause intermittent link training, display flicker, or compliance failures.
- Margining and adaptation status fields are diagnostic signals. Clearing or misdecoding them can hide link-quality regressions.
- Several reserved masks occupy high bits. Driver code should preserve reserved bits according to register-helper conventions and hardware requirements.
- Generated names containing `MASK` may legitimately produce C macro names ending in `_MASK_MASK`; scripts should treat those as generated field-mask constants, not duplicate suffix errors.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU Display Core with DCN 3.2.0/C20 PHY support enabled. Missing, malformed, or renamed symbols should fail in generated register tables or PHY/link code.
- Mechanically compare this range against a regenerated `dcn_3_2_0_sh_mask.h` or the authoritative DCN 3.2.0 register database, preserving the partial start and end register families.
- Run generated-header consistency checks: each complete register should have expected `_SHIFT` and `_MASK` pairs, masks should match their shift/width, fields should not overlap unexpectedly, and reserved fields should cover only documented holes.
- Compare RAWLANE2 and RAWLANE3 complete families for structural equivalence after lane-prefix substitution, allowing only documented instance differences.
- Exercise link bring-up and retraining at multiple link rates and lane widths, checking TX pstate/rate/width, TX drive settings, PLL selection, and request/acknowledge progress.
- Exercise RX adaptation and margining flows, including adaptation request/ack, FOM readback, TX pre/main/post direction hints, IQ/VDAC margin start/finish/error/global events, and status clear behavior.
- Validate IRQ handling by enabling/masking/clearing TX rate/reset/request/loopback/RTUNE/term/transceiver-mode events and RX reset/request/rate/pstate/adaptation/margin events.
- Run suspend/resume and hotplug tests that require reinitializing C20 PHY lanes, clocks, resets, pstate, and calibration state.
- Use hardware register dumps around link training, rate changes, margining, and fault injection to verify packed writes affect only intended bits and status decoding matches observed hardware behavior.
- For diagnostics, read FSM scratch, breakpoint, status monitor, calibration status, adaptation FOM/error, and PMA/PCS valid signals before and after controlled PHY state transitions.

## Cross-Chunk Notes

The previous chunk owns the beginning of `C20_PHY_CR1_RAWLANE2_DIG_TX_PCS_XF_LANE_IN_0`; this chunk only sees the tail shifts and masks for that register. The next chunk owns the remaining masks for `C20_PHY_CR1_RAWLANE3_DIG_RX_FW_XF_OVRD_OUT_0` and the subsequent RAWLANE3 RX firmware/IRQ/control/PMA/FSM definitions. The final per-file report should reconcile those boundaries and should not treat this chunk alone as complete coverage for either boundary register.
