# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 209692-212183

## Scope

This chunk is a generated AMD DCN 3.2.0 register shift/mask slice for the C20 PHY `CR4` raw-lane and always-on raw-lane namespaces. It contains preprocessor constants only: `_SHIFT` macros describe field bit positions and `_MASK` macros describe the corresponding unshifted bit masks. `//<REGISTER>` comments group each set of field macros by hardware register.

There are no C functions, structs, enums, loops, branches, locks, memory allocation paths, direct MMIO calls, or persistence code in this range. Runtime behavior is provided by AMDGPU Display Core users that pair these constants with matching register-address headers and register access helpers.

The range starts inside `C20_PHY_CR4_RAWLANE3_DIG_RX_PCS_XF_CNTX_CFG_1`; its early shift fields and two masks are in the previous chunk. It ends inside `C20_PHY_CR4_RAWLANEAON1_DIG_TX_INIT_PWRUP_DONE`; only the `INIT_PWRUP_DONE__SHIFT` line is present here, while the reserved shift and masks continue in the next chunk. Final per-file reconciliation should merge adjacent chunks before describing either boundary register as complete.

## Purpose And Hardware Surface

This header provides the bit layout used to program and decode DCN 3.2.0 C20 PHY register fields. The source file name indicates the `sh_mask` role: it is the field shift/mask companion to generated register-offset definitions. Display code can compose writes and decode reads without hardcoding magic bit positions.

The hardware surface in this chunk covers CR4 raw lane 3 RX control/FSM registers and CR4 always-on lane 0/1 TX/RX calibration registers:

- `C20_PHY_CR4_RAWLANE3_DIG_RX_PCS_XF_*` covers RX PCS cross-fabric context configuration for equalizer/DFE/CDR/signal-detect/rate/width settings, firmware override/input/output handshakes, adaptation status, TX pre/main/post direction hints, RX clock enables, and ACK status.
- `C20_PHY_CR4_RAWLANE3_DIG_RX_IRQ_CTL_*` defines interrupt masks, enable flags, status bits, and clear bits for RX reset, request, rate, pstate, adaptation request/disable, term-control, and RX margining events.
- `C20_PHY_CR4_RAWLANE3_DIG_RX_CTL_*` defines RX control and readback fields for termination code, continuous off-cancel/adaptation status, adaptation mode/selection, PPM drift, CDR detection, PMA miscellaneous control, adaptation FOM and reference-error readback, IQ/phase-adjust controls, RX margining status/error, FSM control, rate IRQ ACK, and IQ/phase update registers.
- `C20_PHY_CR4_RAWLANE3_DIG_RX_PMA_XF_*` exposes PMA cross-fabric input/override/output fields for adaptation request/enable, continuous adaptation, PSTATE, low-power detect, rate, width, reset, request, ACK, RX valid, and clock control.
- `C20_PHY_CR4_RAWLANE3_DIG_FSM_*` defines PHY firmware/FSM override, jump, status, memory breakpoint/monitor, firmware config-stage and scratch registers, CR lock, fast-path flags, calibration skip controls, and RX calibration status for raw lane 3.
- `C20_PHY_CR4_RAWLANEAON0_DIG_TX_*` defines always-on lane 0 TX firmware state, SRAM recovery controls, CCA counters, startup/continuous algorithm controls, fast flags, high-power protection and lane mode overrides, TX disable input, DCC calibration banks for MPLLA/MPLLB, calibration-done fields, DCC readback codes, and calibration bank selection.
- `C20_PHY_CR4_RAWLANEAON0_DIG_RX_*` defines always-on lane 0 RX startup and continuous calibration/adaptation controls, fast flags, analog offset trims, signal-detect calibration, RX DCC/IQ calibration banks, done/readback codes, IQ/adaptation controls, banked adaptation readbacks, TX equalization steering thresholds, generic adaptation control words, CDR/signal-detect controls, PMA overrides, and RX input/output status.
- `C20_PHY_CR4_RAWLANEAON1_DIG_TX_*` begins the same always-on TX control surface for lane 1, through the first line of `TX_INIT_PWRUP_DONE`.

## Important Definitions

The generated API pattern is consistent throughout the chunk:

- `<REGISTER>__<FIELD>__SHIFT` gives the field least-significant bit.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register position.
- `RESERVED_*` fields document unused bit ranges and help preserve full register layout.

Important macro families include:

- RX PCS context configuration: `RX_PCS_XF_CNTX_CFG_1` through `CNTX_CFG_8` define equalization and link parameters such as `EQ_AFE_BIAS_TIA`, `EQ_AFE_BIAS`, `EQ_AFE_VCM_ADJ`, `EQ_DFE_TAP1`, `DFE_BYPASS`, `ADAPT_SEL`, `ADAPT_MODE`, `DELTA_IQ`, `CDR_VCO_CONFIG`, `DCC_CTRL_RANGE`, `RATE`, `REF_LD_VAL`, `DIV16P5_CLK_EN`, `CDR_PPM_MAX`, `WIDTH`, `VCO_LD_VAL`, signal-detect thresholds, termination control, DCC/VREG bypass, continuous adaptation/off-cancel, and `UNIQUE_ID`.
- RX firmware cross-fabric controls: `RX_FW_XF_OVRD_IN_0..2`, `RX_FW_XF_IN_0`, `RX_FW_XF_OVRD_OUT_0`, `RX_FW_XF_OUT_0`, `RX_FW_XF_ADAPT_ACK`, `RX_FW_XF_ADAPT_FOM`, `RX_FW_XF_TXPRE_DIR`, `RX_FW_XF_TXMAIN_DIR`, `RX_FW_XF_TXPOST_DIR`, and `RX_FW_XF_CLK_CTRL_0` provide reset/request/pstate/LPD/rate/width/DFE-bypass/adaptation override fields, ACK/RX-valid override fields, adaptation FOM, TX coefficient direction outputs, and RX clock enable/reset controls.
- RX interrupt controls: `RX_IRQ_CTL_IRQ_MASK` and `RX_IRQ_CTL_IRQ_EN_FLAGS` provide bit-level mask/enable fields for request, rate, pstate, adaptation, reset, term control, and margining interrupts. Matching one-bit status and clear registers exist for reset, request, rate, pstate, adaptation request/disable, term-control, IQ margin start, VDAC margin start, margin error clear, margin init, margin finish, and global margin events.
- RX control/readback: `RX_CTL_TERM_CODE`, `OFFCAN_CONT_STATUS`, `ADAPT_CONT_STATUS`, `ADAPT_MODE`, `ADAPT_SEL`, `PPM_DRIFT`, `CDR_DET_STATUS`, `PMA_MISC_CTL`, `ADAPT_MODE_OVRD_EN`, `ADAPT_MODE_EN`, `ADAPT_MM_FOM`, `ADAPT_STARTUP_FOM`, even/odd reference-error fields, IQ left/right fields, phase-adjust linear/map controls, margin IQ/VDAC deltas, margin status/error, FSM control, rate IRQ ACK, and IQ/phase update fields.
- RX PMA cross-fabric controls: `RX_PMA_XF_OVRD_OUT_0`, `RX_PMA_XF_IN_0`, and `RX_PMA_XF_OVRD_IN_0` contain ACK/RX-valid clock override output fields and input/override fields for adaptation request, continuous adaptation, reset, request, pstate, LPD, rate, width, and DFE bypass.
- Raw-lane FSM and firmware debug: `FSM_OVRD_CTL`, `FSM_JMP_BANK`, `FSM_CTL_0`, `MEM_BREAKPOINT_0/1`, `MEM_ADDR_MON`, `STATUS_MON`, `FW_CFG_STAGE`, `FW_SCRATCH_0..11`, `CR_LOCK`, and `RX_CAL_STATUS` define direct firmware/FSM control, breakpointing, state observation, scratch communication, and calibration status.
- Fast and skip controls: `FAST_SUP`, `FAST_TX_*`, `FAST_RX_*`, `SKIP_TX_*`, `SKIP_RX_*`, `SKIP_SIGDET_STARTUP_CAL`, and `SKIP_VGEN_STARTUP_CAL` expose many one-bit policy knobs that can shorten or bypass TX/RX startup, rate-change, continuous, DCC, AFE, DFE, IQ, phase, full/half-rate, signal-detect, VGEN, and margining flows.
- Always-on TX lane 0 calibration: `TX_FW_STATES_*`, `TX_MEM_BREAKPOINT_2`, `TX_SRAM_REC_*`, `TX_CCA_*`, `TX_STARTUP_ALGO_CTL_0`, `TX_CONT_ALGO_CTL_0`, `TX_FAST_FLAGS_0`, high-power protection and lane mode override/input registers, `TX_INIT_PWRUP_DONE`, `TX_OVRD_IN_0`, MPLLA/MPLLB DCC control/full/half banks 0-3, per-bank and aggregate calibration-done fields, selected DCC codes, and `TX_CAL_BANK_SEL`.
- Always-on RX lane 0 startup/adaptation controls: `RX_STARTUP_CAL_ALGO_CTL_0/1`, `RX_STARTUP_ADAPT_ALGO_CTL_0`, `RX_CONT_ALGO_CTL`, and `RX_FAST_FLAGS` define skip/fast bits for RX calibration/adaptation phases and TX coefficient feedback.
- Always-on RX lane 0 calibration data: VGEN/signal-detect/AFE/reference/setup/DFE VDAC and IDAC offset registers, `RX_DCC_*_BANK_0..3`, `RX_IQ_CAL_BANK_0..3`, `RX_CAL_DONE_BANK_0..3`, global DCC/IQ code readbacks, `RX_CAL_BANK_SEL`, `RX_IQ_CTL_0/1`, `RX_ADPT_IQ_LIMIT`, and `RX_ADPT_ERR_SLC_MODE`.
- Always-on RX lane 0 adaptation data: banked `RX_ADPT_ATT`, `VGA`, `CTLE`, `DFE_TAP1..5`, DFE tap-1 offset quadrant readbacks, `RX_ADPT_IQ`, `RX_ADPT_REF_ERR`, and `RX_ADAPT_DONE` for banks 0 and 1, plus `RX_ADPT_CTL_0..28` opaque full-width adaptation control words.
- Always-on RX lane 0 link steering and detect controls: `RX_TX_EQ_DIR_POLARITY_CTL`, `RX_TX_PRE_DIV`, TX main/pre/post threshold registers, `RX_IQ_MARGIN_RANGE`, `RX_CDR_DETECTOR_CTL`, `RX_CDR_RECOVERY_TIME`, `RX_OVRD_IN_0`, signal-detect mask/filter controls, RX/PMA override outputs, and RX input/output status.
- Always-on TX lane 1 startup surface: `RAWLANEAON1_DIG_TX_FW_STATES_*`, SRAM recovery, CCA counters, algorithm controls, fast flags, high-power protection, lane transceiver mode controls, and the first `TX_INIT_PWRUP_DONE` bit position.

## Control Flow And State Behavior

This chunk has no executable control flow. The effective control flow appears in callers that use these macros with register helpers such as generated AMD display `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or lower-level MMIO accessors.

Typical runtime flows enabled by this slice are:

1. Link bring-up code programs RX PCS context values for rate, width, CDR VCO/load values, DFE bypass, adaptation mode, signal-detect thresholds, and termination control.
2. Firmware or low-level PHY code coordinates RX handshakes through reset/request/ACK, pstate, LPD, adaptation request, RX valid, and clock-enable fields.
3. Interrupt handlers or polling paths mask, enable, read, and clear RX request/rate/pstate/adaptation/reset/term-control/margining events.
4. RX adaptation and margining code reads FOM/reference-error/IQ/phase/margin status, writes phase or IQ update controls, and acknowledges rate IRQ state.
5. PHY FSM/debug code may override FSM flow, inspect firmware stage/scratch/status registers, set memory breakpoints, or use fast/skip controls to alter calibration sequencing.
6. Always-on TX/RX calibration code selects banks, reads or writes DCC/IQ/VDAC/IDAC calibration values, checks calibration-done bits, and controls startup/continuous algorithm skip bits.
7. Link-training and diagnostics code reads banked adaptation results and TX equalization direction/threshold state to correlate RX measurements with requested TX coefficient changes.

The state represented here is hardware register state:

- Programmed state includes RX context config, override enable/value fields, clock enables, interrupt masks/enables, adaptation mode enables, phase/IQ update controls, FSM overrides, scratch registers, fast and skip bits, SRAM recovery setup, CCA counters, high-power protection and lane-mode overrides, DCC/IQ bank selections, analog trim offsets, signal-detect filter controls, and opaque `RX_ADPT_CTL_*` words.
- Volatile readback includes ACK/RX valid, adaptation ACK/FOM, IRQ status, term/off-cancel/adaptation/CDR/PPM status, FOM/reference-error/IQ readbacks, margin status/error, firmware/FSM stage and memory monitor state, calibration done/status, DCC/IQ code readbacks, adaptation bank results, and RX signal-detect/input/output status.
- Sequencing-sensitive fields include reset/request/ACK handshakes, IRQ clear bits, calibration skip/fast bits, FSM jump/override controls, SRAM recovery enable/control, calibration bank selection, phase/IQ update strobes, rate IRQ ACK, RX/TX disable overrides, and calibration done/readback fields whose meaning depends on hardware state transitions.

## Dependencies And Integration Points

This chunk depends on exact generated consistency with the DCN 3.2.0 C20 PHY hardware specification and the matching register-offset headers. The macro names and numeric values are consumed as a hardware ABI by AMDGPU Display Core code; compilation catches missing names, but wrong masks or shifts can compile cleanly and only fail on hardware.

Important integration points include:

- AMDGPU Display Core link encoder and PHY code that configures C20 PHY CR4 lane rate, width, CDR, DFE, adaptation, signal-detect, termination, TX/RX power-up, and calibration policy.
- DisplayPort link training, retraining, hotplug, suspend/resume, and power-management paths that may change pstate, LPD, rate, width, reset/request handshakes, RX valid, and fast/skip controls.
- Firmware-assisted or DMUB-mediated flows that observe firmware state, scratch registers, adaptation ACK/FOM, SRAM recovery, FSM state, and calibration status.
- RX margining and diagnostics paths that need IRQ/status/clear bits for IQ/VDAC margin events and margin error/init/finish/global signaling.
- PHY calibration routines that use TX MPLLA/MPLLB DCC banks, RX DCC/IQ banks, analog offset trims, calibration-done fields, and bank selection.
- Lab/debug tooling that dumps or overrides FSM state, memory breakpoints, adaptation readbacks, CDR/signal-detect state, PMA inputs/outputs, and firmware scratch data.

## Risks And Maintenance Notes

- Numeric drift is the main risk. These are generated constants for packed hardware registers; an off-by-one shift or wrong mask can corrupt link bring-up, calibration, interrupt handling, or diagnostics without producing a build error.
- Repetition makes copy/paste mistakes easy to miss. The same patterns repeat across lane 3 raw-lane RX/FSM, always-on lane 0 TX/RX, bank 0-3 calibration storage, MPLLA/MPLLB, full/half-rate DCC fields, common-mode/differential values, and lane 1 TX startup fields.
- Many fields are one-bit strobes or enables. Incorrect masks for IRQ clear, reset/request handshakes, phase/IQ update, FSM jump/override, calibration skip, or SRAM recovery can create sequencing bugs that appear only under retrain, hotplug, resume, or marginal signal conditions.
- `RX_ADPT_CTL_0..28` are opaque full-width `VAL` registers in this header. Their bit-level contract is not documented here and likely belongs to the PHY hardware/firmware specification, so consumers should avoid interpreting or modifying them ad hoc.
- Reserved-field masks document register packing and should not be treated as permission to write reserved bits. Register updates should preserve reserved fields unless the hardware specification explicitly requires otherwise.
- Boundary completeness matters for this chunk. `RX_PCS_XF_CNTX_CFG_1` and `TX_INIT_PWRUP_DONE` are split across chunk boundaries; the final merged research document should avoid treating this chunk alone as complete coverage for those registers.

## Test Signals

Useful validation signals for changes touching these macros are mostly build-time and hardware-facing:

- Build coverage for AMDGPU DCN 3.2.0 display code, especially any code that includes `dcn_3_2_0_sh_mask.h` and uses C20 PHY CR4 fields through register helper macros.
- Static comparison against the generated source or hardware register specification to verify every `_SHIFT`/`_MASK` pair, reserved range, and repeated lane/bank family.
- Display link bring-up, hotplug, retrain, suspend/resume, and multi-rate DisplayPort/HDMI testing on DCN 3.2.0 hardware using CR4 lanes.
- PHY calibration diagnostics that confirm TX MPLLA/MPLLB DCC done/code values, RX DCC/IQ done/code values, adaptation bank results, and signal-detect/CDR status match expected hardware behavior.
- Interrupt and margining tests that exercise RX IRQ mask/enable/status/clear fields and RX margin IQ/VDAC start/error/init/finish/global events.
- Register dump comparisons before and after link training to confirm reserved bits remain stable and only intended fields change.
