# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 54806-57191

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice. It contains preprocessor constants only: `__SHIFT` and `_MASK` definitions for 16-bit DPCS control-register fields under the `DPCSSYS_CR2` indirect register namespace. There are no C functions, structs, enums, branches, allocations, locks, or software persistence paths in this range.

The slice starts at the final two mask definitions for `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_ATE_TX_OVRD_IN`, covers the remaining RAWLANE1 PCS ATE/override masks, then contains full repeated RAWLANE2 and RAWLANE3 digital PCS, FSM, IRQ, PMA, TX-control, and RX-control field layouts. It ends at the first shift definition for `DPCSSYS_CR2_RAWAONLANE0_DIG_RX_ADPT_ATT`, after starting the RAWAONLANE0 always-on analog calibration/readback field group.

I counted 2,105 macro definitions in the assigned range: 1,052 shift macros and 1,053 mask macros. The one-extra mask count comes from the slice starting after the matching shifts for `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_ATE_TX_OVRD_IN`.

## Purpose

The header gives AMD display driver code symbolic bit positions and masks for DPCS 4.2.2 CR2 raw-lane registers. Companion offset headers identify the indirect CR register addresses, while this shift/mask header defines how callers extract or update individual fields after selecting a register through the DPCS CR address/data access path.

The hardware domains represented here are low-level display PHY and lane-control surfaces:

- PCS crossbar and override fields for TX/RX reset, request, power state, lane power-down, width, rate, MPLL selection, MPLL state, data-enable, async, beacon, loopback, detect-RX, voltage/current boost, RX loss-of-signal threshold, adaptation requests, and calibration continuations.
- Lane FSM monitor and fast-calibration controls/status bits for RX startup, AFE/DFE/bypass/reference-level/IQ/VCO calibration, continuous adaptation, common MPLL/RCAL status, CR register/memory locks, OCLA debug capture, TX DCC status, and TX EQ update flags.
- Per-lane IRQ status, clear, and mask fields for RX/TX reset and request events, RX rate and power-state changes, RX adaptation request/disable, RX phase-2 calibration request/disable, lane transceiver mode, serial loopback, and DCC on-demand events.
- PMA interface override/input/output fields for lane/supervisor MPLL state, TX/RX request/reset/data enables, async/beacon controls, PMA PWM and termination control, RX IQ phase-adjust map override, RTUNE request/ack, and PCS/PMA acknowledgement handshakes.
- TX and RX controller fields for FSM enable, wait timing, clock select/enable, async beacon wait, DCC continuous status, LOS mask, RX data-enable override, off-canonical/continuous adaptation status, and UPCS/OCLA debug enables.
- Always-on lane 0 analog calibration/readback masks for AFE/CTLE/DFE IDAC/VDAC offsets, RX adaptation figure-of-merit and IQ/phase values, MPLLA/MPLLB coarse tune, and initialization power-up done flags.

## Important API Surface

The exported API is the macro namespace. The macros are intended to be paired with register offsets such as `ixDPCSSYS_CR2_RAWLANE2_DIG_PCS_XF_TX_OVRD_IN` from the matching DPCS offset header and with AMD register helper patterns that use `REG_GET`, `REG_SET`, `REG_UPDATE`, or table-generated equivalents.

Important field families in this chunk include:

- `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_*` tail coverage: ATE TX override masks for async enable, TX override input 1 fields for `DETRX_REQ`, `VBOOST_EN`, `IBOOST_LVL`, `TX_BEACON_EN`, serial loopback, and async data; master MPLL loop bits; ATE RX override fields for LOS LFPS/threshold, adaptation request, continuous adaptation, off-canonical continuation, VCO/reference load overrides, RX valid override, and TX async/data override input 2.
- `DPCSSYS_CR2_RAWLANE2_DIG_PCS_XF_*`: complete lane 2 PCS TX/RX override and observed PCS input/output fields. Representative fields include `PSTATE`, `LPD`, `WIDTH`, `RATE`, `MPLLB_SEL`, `MPLL_EN`, `OVRD_EN`, `MSTR_MPLLA_STATE`, `MSTR_MPLLB_STATE`, reset/request overrides, `ACK`, `DETRX_RESULT`, RX adaptation controls, RX VCO/reference load overrides, TX pre/main/post cursor direction registers, lane number, ATE overrides, RX EQ delta/IQ and PH2 calibration, and TX/RX termination control.
- `DPCSSYS_CR2_RAWLANE2_DIG_FSM_*`: lane 2 FSM override, memory/status monitor, fast calibration indicators, continuous calibration/adaptation indicators, `FAST_FLAGS`, CR lock bits, TX DCC flags/status, OCLA capture enables, TX EQ update flag, common MPLL/RCAL init/done flags, and RX IQ phase offset.
- `DPCSSYS_CR2_RAWLANE2_DIG_IRQ_CTL_*`: lane 2 IRQ status registers, corresponding clear registers, `IRQ_MASK` and `IRQ_MASK_2`, and event-specific fields for RX reset/request/rate/pstate/adaptation/PH2 calibration, lane transceiver mode, RX-to-TX serial loopback, DCC on-demand, TX reset, and TX request.
- `DPCSSYS_CR2_RAWLANE2_DIG_PMA_XF_*`: lane 2 PMA lane/supervisor/TX/RX override outputs and PMA inputs, RTUNE control, MPHY PWM/termination override in/out, and RX adaptation override output.
- `DPCSSYS_CR2_RAWLANE2_DIG_TX_CTL_*` and `DPCSSYS_CR2_RAWLANE2_DIG_RX_CTL_*`: lane-local TX/RX controller masks for FSM control, clock control, DCC continuous status, OCLA/UPCS OCLA, LOS masking, RX data-enable override, and adaptation/off-canonical continuous status.
- `DPCSSYS_CR2_RAWLANE3_DIG_*`: the same PCS/FSM/IRQ/PMA/TX/RX control surface repeated for raw lane 3. The lane 3 field names mirror lane 2, which makes generated-name parity a key correctness property.
- `DPCSSYS_CR2_RAWAONLANE0_DIG_*`: always-on lane 0 calibration and status masks for AFE/CTLE IDAC offset, RX adaptation IQ and FOM, DFE summer/phase/data/bypass/error VDAC offsets, even/odd reference levels, phase-adjust linear/map values, MPLLA/MPLLB coarse tune, and `INIT_PWRUP_DONE`/`PH2_PWRUP_DONE`.

Most field layouts are 16-bit wide. Many registers follow a simple paired pattern of value bit plus override-enable bit, while multi-bit fields use contiguous masks such as `PSTATE_MASK 0x00000003L`, `RATE_MASK 0x000000E0L`, `IBOOST_LVL_OVRD_VAL_MASK 0x00000F00L`, `VCO_LD_VAL_OVRD_MASK 0x00001FFFL`, `RX_PMA_TERM_CTL_R_MASK 0x000000C0L`, or 8-bit calibration `data_MASK 0x000000FFL`.

## Control Flow

This header has no executable control flow. The implied control flow exists in driver register access code:

1. Driver code selects an indirect CR2 register offset from the companion DPCS offset header.
2. It reads or writes that register through the DPCS CR address/data access window for the relevant instance.
3. It uses this header's `__SHIFT` and `_MASK` macros to pack field values into the register word or extract status fields from it.
4. Hardware lane state machines, PCS/PMA bridges, IRQ latches, PLL supervisors, adaptation engines, and analog calibration circuits perform the real state transitions.

The repeated RAWLANE2/RAWLANE3 layout means higher-level code can use per-lane tables or generated macros with consistent field semantics across lanes. The slice also shows boundary continuity: lane 1 tail fields precede lane 2, lane 3 repeats lane 2, and RAWAONLANE0 begins immediately after lane 3 ATE tail registers.

## State And Persistence

The file stores no runtime state. Its constants describe hardware-backed state and control bits:

- Override registers can force or bypass normal lane state machine behavior for reset, request, power state, MPLL selection/state, data-enable, async data, beacon, loopback, RX LOS, VCO/reference load, TX/RX termination, PMA PWM, and RX IQ phase mapping.
- Status and monitor fields expose transient hardware state such as ACK, RX valid, RX adaptation FOM, calibration flags, MPLL/RCAL init/done, TX DCC status, TX EQ update, CR lock state, RTUNE ack, and power-up done.
- IRQ status/clear/mask registers can persist event latches or mask decisions in hardware until explicitly cleared, overwritten, or reset by display power-management flows.
- Always-on lane calibration readbacks represent physical calibration values that may survive lane-level power changes but are still hardware-local, not file-backed software state.

Incorrect writes using these masks can leave a lane forced into reset, request, test/ATE, loopback, disabled data, altered calibration, masked IRQ, or wrong MPLL/termination state until the display driver reinitializes the block or the ASIC resets.

## Dependencies And Integration Points

This generated header depends only on the C preprocessor, but it must stay synchronized with several generated and handwritten layers:

- The matching `dpcs_4_2_2_offset.h` register-address macros for `ixDPCSSYS_CR2_RAWLANE{1,2,3}_...` and `ixDPCSSYS_CR2_RAWAONLANE0_...`.
- AMD display register helper macros and generated register-table code that combine offsets, shifts, and masks.
- DPCS/RDPCS/HPO DisplayPort link encoder paths that program lane reset/request/rate/width/power-state, MPLL selection, TX/RX enables, equalization, link training, and PHY diagnostic state.
- PHY initialization and power-management logic that uses FSM, PMA, TX_CTL, RX_CTL, IRQ_CTL, and ATE/test fields when bringing links up, retraining, entering low-power states, or collecting debug status.
- ASIC-generation comparison headers such as DPCS 4.2.0, 4.2.3, 3.1.4, and DCN 4.1.0 shift/mask headers. Similar names appear across generations, but mask formatting and exact field widths can differ, so consumers must include the correct ASIC header.

## Risks

- Generated mask/shift drift is the main risk. A single incorrect bit position in reset, request, PLL, data-enable, IRQ clear, or calibration fields can break link bring-up in a lane-specific way.
- RAWLANE2 and RAWLANE3 are large repeated blocks. Copy-generation errors are easy to miss because neighboring lanes may still work.
- This chunk starts and ends mid-register group. File-level reconciliation must preserve context from adjacent chunks before deciding whether a register family is complete.
- Override-enable fields are hazardous because setting an override value without the intended enable bit, or leaving an enable bit set after test/debug use, can make hardware ignore normal PCS/PMA/FSM control.
- IRQ status/clear/mask families use very similar names. Mixing status, clear, and mask macros can silently lose interrupts, create interrupt storms, or hide adaptation/reset events.
- Reserved masks occupy many upper bits. Code should preserve reserved bits unless hardware documentation explicitly permits writes.
- Always-on calibration fields often use generic `data` names. Misinterpreting signedness, lane ownership, or calibration units can cause bad diagnostics or incorrect tuning decisions.
- Several fields are test/ATE or OCLA oriented. Exposing them through normal runtime paths without strict gating can force loopback, async data, beacon, PMA PWM, or debug capture behavior during active links.

## Test Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware/display behavior:

- Build all AMD display configurations that include DPCS 4.2.2 register headers; missing or renamed macros should fail at compile time.
- Generated-header checks should confirm every `*_MASK` is consistent with its matching `__SHIFT` and field width, especially 16-bit reserved masks and multi-bit fields like `RATE`, `WIDTH`, `PSTATE`, `VCO_LD_VAL_OVRD`, `IBOOST_LVL_OVRD_VAL`, `RX_PMA_TERM_CTL_R`, and calibration `data`.
- Compare RAWLANE2 and RAWLANE3 macro families for expected parity, excluding only lane-number prefixes and any documented lane-specific exceptions.
- Cross-check this shift/mask slice with the matching offset header so every register block named here has the expected `ixDPCSSYS_CR2_*` address and no stale field family exists without an address.
- Hardware smoke tests should exercise DisplayPort link bring-up, lane rate/width changes, retraining, low-power transitions, RX adaptation, EQ update, TX/RX reset/request handshakes, MPLL switching, and IRQ mask/clear handling.
- Debug tests can read FSM/IRQ/PMA/TX_CTL/RX_CTL status after link training and verify expected `ACK`, calibration done, power-up done, RX valid, DCC, RTUNE, and adaptation status transitions.
- Failure signatures include lane 2 or lane 3 only link failures, stuck reset/request/ACK bits, masked or uncleared PHY IRQs, continuous adaptation not starting or not stopping, wrong TX/RX data-enable state, broken loopback/test-mode cleanup, invalid calibration readbacks, or regressions limited to DPCS 4.2.2 while neighboring DPCS generations still pass.
