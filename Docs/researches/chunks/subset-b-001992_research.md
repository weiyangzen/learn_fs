# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h - subset-b-001992

## Scope

- Chunk id: `subset-b-001992`
- Source lines: 153892-156393
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h`
- Observed content: 2,502 lines, 2,063 `#define` entries, 1,032 `__SHIFT` macros, 1,035 `_MASK` macros, 435 comment markers, 434 distinct register macro prefixes, and two explicit `addressBlock:` transitions.

This chunk is generated AMD DCN 3.2 register-field metadata. It does not define executable code, C types, functions, storage, or runtime policy. It publishes bit-position and bit-mask constants for C20 PHY CR2 receiver/control blocks, CR2 always-on firmware/calibration blocks, and LPC PHY pipe message bus blocks for pipe2 lane 0 and lane 1. Consumers pair these masks and shifts with register offsets from `dcn_3_2_0_offset.h` and the AMDGPU/DCN register helper layer.

## Purpose

The chunk covers the tail of a CR2 raw-lane RX control section, the CR2 lane firmware/calibration surface, and the start of pipe2 LPC PHY register definitions for two lanes:

- `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_*`: RX adaptation result/status fields, phase adjustment update paths, margining state, IRQ enables/acks, and RX PMA crossover override/input fields.
- `C20_PHY_CR2_RAWLANEX_DIG_FSM_*`: low-level PHY firmware state machine override, jump, breakpoint, status, scratch, lock, fast-path, skip, and calibration-status controls.
- `C20_PHY_CR2_RAWLANEAONX_DIG_TX_*`: always-on TX firmware state, SRAM recovery, calibration algorithm controls, fast flags, high-power protection, lane transceiver mode inputs, MPLLA/MPLLB DCC calibration banks, calibration-done mirrors, selected bank/code outputs, and TX input status.
- `C20_PHY_CR2_RAWLANEAONX_DIG_RX_*`: always-on RX startup/continuous calibration algorithm controls, fast flags, VGEN/sigdet/AFE/reference/DFE/IQ/DCC calibration storage, per-bank calibration done bits, selected bank/code outputs, adaptation coefficients, TX EQ feedback thresholds, detector/recovery controls, override inputs/outputs, and PMA crossover overrides.
- `C20_PHY_LANE0_PIPE2_UPCSLANE_PIPE_LPC_PHY_*` and `C20_PHY_LANE1_PIPE2_UPCSLANE_PIPE_LPC_PHY_*`: pipe2 lane-local LPC PHY message bus fields for RX margining, elastic buffer/RX/TX/HDP controls, vendor-defined register address/data windows, custom SERDES/HDMI/width/LFPS mode fields, TX equalization overrides, and recalibration/deskeW control.

The file-level contract is a generated register ABI: each register comment is followed by `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants. The macros describe how software packs and extracts bitfields when programming display PHY hardware.

## Important APIs, Types, and Macros

There are no callable APIs or C data structures in this chunk. The important public surface is the preprocessor namespace.

Key macro families:

- RX adaptation and margining results:
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_ADAPT_MM_FOM`
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_ADAPT_STARTUP_FOM`
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_ADPT_REF_ERR_EVEN`
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_ADPT_REF_ERR_ODD`
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_RX_ADPT_IQ_LEFT`
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_RX_ADPT_IQ_RIGHT`
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_MARGIN_IQ_DELTA`
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_RX_MARGIN_VDAC_DELTA`
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_RX_MARGIN_STATUS`
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_RX_MARGIN_ERROR`
- RX control interrupts and PMA handshakes:
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_FSM_CTL` exposes IRQ enables for lane rate, width, VCO frequency, misc, termination, DCC, DFE bypass, EQ, and calibration-done events.
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_RATE_IRQ_ACK` acknowledges rate IRQ state.
  - `C20_PHY_CR2_RAWLANEX_DIG_RX_PMA_XF_OVRD_OUT_0`, `C20_PHY_CR2_RAWLANEX_DIG_RX_PMA_XF_IN_0`, and `C20_PHY_CR2_RAWLANEX_DIG_RX_PMA_XF_OVRD_IN_0` define request/reset/ack value and override-enable fields for the RX PMA crossing.
- Firmware state machine debug/control:
  - `C20_PHY_CR2_RAWLANEX_DIG_FSM_FSM_OVRD_CTL`, `FSM_JMP_BANK`, `FSM_CTL_0`, `FSM_MEM_BREAKPOINT_0`, `FSM_MEM_BREAKPOINT_1`, `FSM_MEM_ADDR_MON`, and `FSM_STATUS_MON` support forced jumps, command start, override enable, breakpoints, current memory address, state, command-ready, ALU, wait, and write-mask status.
  - `C20_PHY_CR2_RAWLANEX_DIG_FSM_FW_CFG_STAGE` and `FW_SCRATCH_0` through `FW_SCRATCH_11` expose firmware configuration and scratch storage fields.
  - `C20_PHY_CR2_RAWLANEX_DIG_FSM_FAST_*` and `C20_PHY_CR2_RAWLANEX_DIG_FSM_SKIP_*` provide fast-mode and skip-mode bits for TX common mode, RX detect, TX/RX startup calibration, continuous calibration/adaptation, DCC range/full/half calibration, VCO wait/calibration, IQ, AFE, DFE, CTLE, ATT, VGA, signal detect, VGEN, margining, and adaptation reload.
- Always-on TX calibration and recovery:
  - `C20_PHY_CR2_RAWLANEAONX_DIG_TX_FW_STATES_0` and `_1` expose TX firmware stage/state slots.
  - `C20_PHY_CR2_RAWLANEAONX_DIG_TX_MEM_BREAKPOINT_2`, `TX_SRAM_REC_CTRL`, `TX_SRAM_REC_MAX_ITER`, `TX_SRAM_REC_BASE_ADDR`, `TX_SRAM_REC_ADDR`, `TX_SRAM_REC_ITER`, and `TX_SRAM_REC_EN` define SRAM recovery and debug controls.
  - `C20_PHY_CR2_RAWLANEAONX_DIG_TX_STARTUP_ALGO_CTL_0`, `TX_CONT_ALGO_CTL_0`, and `TX_FAST_FLAGS_0` gate or summarize TX startup and continuous algorithms.
  - `C20_PHY_CR2_RAWLANEAONX_DIG_TX_MPLLA_DCC_*_BANK_0..3` and `TX_MPLLB_DCC_*_BANK_0..3` store per-bank DCC range/full/half calibration values for MPLLA and MPLLB.
  - `C20_PHY_CR2_RAWLANEAONX_DIG_TX_MPLLA_CAL_DONE_BANK_0..3`, `TX_MPLLB_CAL_DONE_BANK_0..3`, aggregate `TX_MPLLA_CAL_DONE`, `TX_MPLLB_CAL_DONE`, and `TX_CAL_DONE` describe calibration completion.
- Always-on RX calibration and adaptation:
  - `C20_PHY_CR2_RAWLANEAONX_DIG_RX_STARTUP_CAL_ALGO_CTL_0`, `_1`, `RX_STARTUP_ADAPT_ALGO_CTL_0`, and `RX_CONT_ALGO_CTL` contain dense skip/enable controls for RX AFE, reference, ATT, VGA, CTLE, IQ, phase, DFE, error, bypass, DCC, VGEN, signal-detect, DFE coarse/fine, reload, continuous calibration, and adaptation flows.
  - `C20_PHY_CR2_RAWLANEAONX_DIG_RX_FAST_FLAGS`, `RX_VGEN_VDAC_OFST`, `RX_SIGDET_CAL`, `RX_AFE_RTRIM`, reference/DFE VDAC offset registers, and setup IDAC offset registers publish fast-path status and stored analog calibration values.
  - `C20_PHY_CR2_RAWLANEAONX_DIG_RX_DCC_CTRL_RANGE_BANK_0..3`, `RX_DCC_FULL_*_BANK_0..3`, `RX_DCC_HALF_*_BANK_0..3`, `RX_IQ_CAL_BANK_0..3`, and `RX_CAL_DONE_BANK_0..3` define banked RX DCC/IQ calibration state.
  - `C20_PHY_CR2_RAWLANEAONX_DIG_RX_ADPT_ATT_BANK_0..1`, `RX_ADPT_VGA_BANK_0..1`, `RX_ADPT_CTLE_BANK_0..1`, `RX_ADPT_DFE_TAP1..5_BANK_0..1`, `RX_DFE_*_TAP1_OFST_BANK_0..1`, `RX_ADPT_IQ_BANK_0..1`, `RX_ADPT_REF_ERR_BANK_0..1`, and `RX_ADAPT_DONE_BANK_0..1` define banked adaptation coefficients and completion bits.
  - `C20_PHY_CR2_RAWLANEAONX_DIG_RX_ADPT_CTL_0` through `_28` are byte-wide generic adaptation control values.
  - `C20_PHY_CR2_RAWLANEAONX_DIG_RX_OVRD_IN_0`, `RX_OVRD_OUT_0`, `RX_PMA_OVRD_OUT_0`, `RX_IN_0`, and `RX_OUT_0` expose RX override, PMA, and lane input/output handshake fields.
- Pipe2 LPC PHY message bus registers:
  - Lane 0 block begins at `addressBlock: c20_phy_lane0_pipe2_rdpcspipemsgbusind`.
  - Lane 1 block begins at `addressBlock: c20_phy_lane1_pipe2_rdpcspipemsgbusind`.
  - Both lanes define matching families for `RX_MARGIN_CONTROL0/1`, `ELASTIC_BUFFER_CONTROL`, `RX_CONTROL0/1/3/4`, `TX_CONTROL2..8`, `HDP_TX_CONTROL2..5/8`, `COMMON_CONTROL0`, `C20_VDR_WR_*`, `C20_VDR_RD_*`, `C20_VDR_CUSTOM_SERDES_RATE`, `C20_VDR_HDMI_RATE`, `VDR_CUSTOM_WIDTH`, `C20_VDR_LFPS_CTRL`, `VDR_*_OVRD`, `HDP_VDR_*_OVRD`, `C20_VDR_RECAL_BANK_SEL`, `C20_VDR_RECAL_FORCE_EN`, `C20_VDR_RECAL_SKIP_EN`, and lane-0-only-in-this-chunk `C20_VDR_DESKEW_EN` plus `C20_VDR_RECAL_OVRD`.

## Control Flow

There is no C control flow in this header. The implied control flow is in the consumers:

1. A DCN 3.2 component includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Driver code selects a register offset and a field pair from this header.
3. Register helper macros/functions shift and mask values for field insert, field extract, or read-modify-write operations.
4. Hardware interprets the result as a PHY firmware FSM command, override state, calibration setting, status read, or message-bus transaction.

Within the hardware contract, the names suggest sequencing constraints. Startup/continuous calibration skip bits affect later calibration state. Bank-selection fields choose which stored calibration bank is active. Done/status fields should be checked after initiating calibration or recovery. `*_OVRD_VAL` fields only matter when paired override-enable fields are asserted. Message-bus VDR address/data fields are likely used as ordered low/high address and low/high data accesses, followed by mode/rate/recalibration controls.

## State and Persistence Behavior

The macros themselves are compile-time constants and have no persistence. They describe state stored in C20 PHY hardware registers:

- Configuration-like state: FSM override/jump controls, firmware configuration stage, CR lock, fast/skip mode fields, startup/continuous calibration algorithm controls, TX/RX override inputs, RX detector/recovery settings, LPC PHY mode/rate/width/LFPS fields, and TX equalization override fields.
- Banked calibration state: MPLLA/MPLLB TX DCC control/range/full/half banks, RX DCC full/half data/bypass/phase banks, RX IQ banks, RX calibration bank selection, RX/TX calibration done bank fields, and VDR recalibration bank selection.
- Diagnostic/debug state: firmware state monitors, breakpoints, memory address monitor, scratch registers, SRAM recovery counters/addresses/iteration counters, RX margin error/status, adaptation result coefficients, and lane/PMA input/output mirrors.
- Transient or latch-like state: IRQ enable/ack fields, calibration done bits, RX/TX fast flags, `INIT_PWRUP_DONE`, `ADAPT_DONE`, `ACK`, `REQ`, `RESET`, and status outputs. Consumers need to respect hardware-specific clear, latch, and polling semantics outside this header.

Reserved masks are included as generated field metadata, but they do not imply those bits are safe to write. Full-register writes should preserve reserved bits unless the hardware programming guide or generated access table says otherwise.

## Dependencies

This chunk depends on the AMDGPU/DCN register-access ecosystem:

- Matching register offsets in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`.
- AMD display register helper macros that expect `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming.
- DCN 3.2 C20 PHY hardware layout generated from AMD register specifications.
- Display PHY firmware and PMA behavior for CR2 raw-lane, always-on, and LPC PHY message-bus blocks.

Local include users of `dcn_3_2_0_sh_mask.h` include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`

Repository search did not show direct C references to the representative field names in this chunk beyond the generated header itself. That suggests these fields may be consumed indirectly through generated tables, reserved for firmware/debug tooling, or currently unused by normal host-driver paths in this source tree snapshot.

## Integration Points

The integration surface is low-level hardware bring-up, link training, diagnostics, and debug:

- Display PHY initialization and recovery paths can use the FSM, fast, skip, and calibration fields to control CR2 behavior.
- Link-training and PHY margining diagnostics can inspect RX adaptation FOM, reference-error, IQ, margin VDAC, and error/status fields.
- Firmware/debug paths can use FSM jump, breakpoint, scratch, memory monitor, SRAM recovery, and firmware state fields.
- Calibration flows can read or select TX MPLLA/MPLLB DCC banks, RX DCC/IQ/adaptation banks, done flags, and recalibration bank/force/skip controls.
- DP/HDMI/FRL mode programming can use the pipe2 LPC PHY fields for custom SERDES rate, HDMI rate, custom width, pixel clock gating, DisplayPort/FRL flags, LFPS control, RX/TX control, HDP TX control, and VDR equalization overrides.
- PMA crossover fields connect digital RX/TX logic to lower PHY blocks through request/reset/ack and override-enabled handshake surfaces.

## Risks and Edge Cases

- Generated ABI drift: a wrong mask or shift can silently corrupt hardware programming. The highest-risk areas are calibration banks, recalibration force/skip controls, RX/TX overrides, PHY mode/rate fields, and FSM override/jump controls.
- Chunk boundary incompleteness: the first visible lines are the mask half of `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_ADAPT_MM_FOM`; the matching shifts are immediately before the chunk. The final visible register, `C20_PHY_LANE1_PIPE2_UPCSLANE_PIPE_LPC_PHY_C20_VDR_RECAL_SKIP_EN`, continues after line 156393. Consumers need the whole header, and the merge lane needs adjacent chunk context.
- Reserved-bit hazards: many registers expose `RESERVED_*` masks. These should not be used as ordinary writable fields, especially in analog PHY and message-bus registers.
- Value/enable pairing: override registers frequently split a value bitfield from an enable bitfield. Setting only the value has no effect; leaving the enable asserted can pin hardware away from firmware or automatic control.
- Bank mismatch: many TX and RX calibration values are banked. Selecting the wrong bank or mixing done bits from a different bank can make diagnostics look valid while applying stale calibration data.
- Lane and pipe specificity: the LPC PHY blocks are lane 0 and lane 1 under pipe2. Multi-lane code must use the corresponding offset namespace and must not assume lane 0 fields apply to lane 1 offsets by arithmetic unless the generated offset table supports it.
- Debug register danger: FSM jump, breakpoint, CR lock, SRAM recovery, and skip/fast controls are powerful debug surfaces. Accidental writes can bypass calibration, interrupt firmware sequencing, or leave the PHY in a state that normal hotplug/modeset paths cannot recover.
- Status read semantics: calibration done, IRQ ack, margin status, firmware state, and PMA handshake fields may be latched or clear-on-write/read depending on hardware behavior not expressed by this header.

## Test Signals

Useful validation for code consuming this chunk:

- Build coverage: compile DCN 3.2 display/amdgpu code that includes `dcn_3_2_0_sh_mask.h` with the paired offset header.
- Generated consistency checks: verify every non-boundary field has paired `__SHIFT` and `_MASK` definitions, masks align with shifts, and field masks do not overlap unexpectedly inside a register.
- Representative field access tests: exercise helper macros with `RX_CTL_FSM_CTL`, `FSM_STATUS_MON`, `TX_STARTUP_ALGO_CTL_0`, `RX_STARTUP_CAL_ALGO_CTL_0`, `RX_DCC_CTRL_RANGE_BANK_*`, `RX_ADPT_*_BANK_*`, and `C20_VDR_CUSTOM_SERDES_RATE`.
- Hardware or simulation bring-up: validate that normal link training, hotplug, suspend/resume, and modeset paths do not leave override enables, skip bits, or recalibration force bits asserted unexpectedly.
- Diagnostic tests: read FSM state, scratch, SRAM recovery counters, calibration-done banks, RX margin status/error, adaptation done/result fields, and PMA ACK/REQ/RESET mirrors after controlled operations.
- Protocol-mode tests: exercise DP, HDMI, FRL, custom width, pixel-clock-gate, and TX equalization override scenarios on pipe2 lane 0 and lane 1 to catch lane/pipe offset mismatches.

## Chunk Boundary Notes

Line 153892 starts after the `__SHIFT` definitions for `C20_PHY_CR2_RAWLANEX_DIG_RX_CTL_ADAPT_MM_FOM`; only the mask definitions for that register are inside this chunk. Line 156393 ends inside `C20_PHY_LANE1_PIPE2_UPCSLANE_PIPE_LPC_PHY_C20_VDR_RECAL_SKIP_EN`, after its first three shift macros. The remaining shift and mask macros for that register are expected in the next chunk. The final per-file research document should reconcile these partial register blocks with adjacent chunk reports.
