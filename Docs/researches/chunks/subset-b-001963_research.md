# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 83453-85847

## Purpose

This chunk is a generated DCN 3.2.0 shift/mask header segment for the `C20_PHY_CR0_LANEX` display PHY lane register block. It provides C preprocessor constants for bit positions (`__SHIFT`) and bit masks (`_MASK`) used to access 16-bit lane-side PHY registers through AMDGPU display MMIO helper paths.

The range contains 2,167 `#define` entries under 228 register comment sections. It starts in the middle of `C20_PHY_CR0_LANEX_DIG_ASIC_TX_ASIC_IN_0`, covers a large contiguous transmit and receive lane-control slice, and ends immediately after the first field shift of `C20_PHY_CR0_LANEX_DIG_ANA_XF_RX_SLICER_CTRL`. The missing start/end of those two boundary registers must be supplied by adjacent chunks during merge.

This is data rather than executable logic. Its purpose is to keep generated field layouts for DCN 3.2.0 PHY lane registers synchronized with the matching offset header and with the higher-level display/link code that performs register reads and writes.

## Important APIs, Types, and Register Groups

There are no C functions, structs, enums, or inline helpers in this chunk. The exported API surface is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` identifies the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` identifies the already-shifted bit mask for the same field.
- Register names are instance-specific and start with `C20_PHY_CR0_LANEX`, meaning PHY instance C20, clock-recovery lane group CR0, lane X, digital lane register space.
- These macros pair with `ixC20_PHY_CR0_LANEX_*` register-address macros from `dcn_3_2_0_offset.h` or similarly generated DPCS offset headers.

Major register groups visible in this chunk:

- ASIC TX interface registers: `DIG_ASIC_TX_ASIC_IN_0..3`, `DIG_ASIC_TX_ASIC_OUT`, and `DIG_ASIC_TX_OVRD_MISC` expose lane TX request/ack state, reset/data enable, link rate/width/pstate, MPLL selection, RX detection, beacon/vboost, main/pre/post cursor values, DCC range, and calibration status.
- TX power-control registers: `DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, `P2`, `TX_PWRUP_TIME_0..5`, `TX_CTL`, and `TX_STATUS` define per-power-state analog/digital enable recipes, startup/disable timing windows, request-disable and skip controls, DCC write controls, debug-bus selection, and TX power-state/rate interrupt status.
- TX calibration, statistics, and diagnostics: `DIG_TX_DCC_CTL_*`, `DIG_TX_STAT_*`, `DIG_TX_CLK_ALIGN_*`, `DIG_TX_LBERT_*`, `DIG_TX_LVL_CALC_STAT`, and `DIG_TX_FIFO_CTL` cover DCC IDAC overrides, DCC FSM status, sample/stat counters, comparator clock setup, clock-align startup and retrigger controls, link BERT pattern programming, level-calculation output, and FIFO bypass/read pointer controls.
- TX analog transfer registers: `DIG_ANA_XF_TX_OVRD_OUT_0..3`, term-code overrides, TX DCC controls, TX equalization override/output/status registers, and `TX_ANA_CREG00..05` expose analog clock/reset/serial/data enables, VCM/vboost/regulator controls, termination codes, DCC calibration data, equalization taps, leg pull enables/directions, ATB/test muxes, oscillator/regulator controls, JTAG data, ring/boost controls, and miscellaneous analog override enables.
- ASIC RX override and ASIC input/output registers: `DIG_ASIC_RX_OVRD_IN_0..4`, `OVRD_SIGDET_IN`, `OVRD_VCO_IN`, `OVRD_EQ_IN_0..11`, `OVRD_OUT_0`, `ASIC_IN_0..3`, `CDR_VCO_ASIC_IN`, `EQ_ASIC_IN_0..2`, `ASIC_OUT_0`, and `OVRD_MISC` cover RX clock/data enable, reset, pstate/rate/width, DFE/AFE/VCO/sigdet/equalizer override values and enables, lock/frequency-done status, calibration status, and adaptation/equalizer handoff signals.
- RX power and VCO calibration registers: `DIG_RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, `P2`, `RX_PWRUP_TIME_0..1`, `RX_CTL`, `RX_STATUS`, and `DIG_RX_VCOCAL_*` define RX analog enable recipes, power-up/down timing, continuous VCO calibration, VCO counter timing, VCO FSM state, VCO correction/up/too-fast indicators, and DPLL reset/calibration controls.
- RX CDR, DPLL, and LBERT registers: `DIG_RX_LBERT_*`, `DIG_RX_CDR_CDR_CTL_0..4`, `DIG_RX_CDR_STAT`, `DIG_RX_DPLL_FREQ`, and frequency bounds define BERT mode/error state, CDR lock timeouts, free-run/forced-lock controls, frequency-update enable, filter settings, lock status, DPLL operating frequency, and frequency boundaries.
- RX adaptation controls: `DIG_RX_ADPTCTL_ADPT_CFG_0..12`, `RST_ADPT_CFG`, status registers for ATT/VGA/CTLE/DFE taps, DFE VDAC offset registers, slicer-level registers, DCC offset ranges, fast flags, SSM config/final-code registers, and adaptation reset controls expose the receiver equalization/adaptation state machine, startup reload behavior, adaptation mode selection, DFE tap updates, IQ/phase controls, slicer settings, and settled state indicators.
- RX statistics and IQC controls: `DIG_RX_STAT_*` and `DIG_RX_IQC_CTL_*` expose RX pattern-match masks, scope/correlation/stat counter configuration, sample counters, extended load values, counter freeze/auto controls, IQC reset adjustment, IQC configuration, and IQC status.
- RX analog transfer registers: `DIG_ANA_XF_RX_CTL_OVRD_OUT`, `RX_PWR_OVRD_OUT_0..1`, sigdet calibration, VCO overrides, RX calibration controls, VDAC/DAC controls, AFE trim, DCC DAC range, AFE override inputs, scope controls, and the start of slicer controls map digital override bits to analog RX blocks.

## Control Flow

This header segment has no local branches, loops, function calls, or runtime execution. Runtime control flow is created by code that includes the generated offset and shift/mask headers, builds register tables, and then calls AMD display register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, or lower-level indexed MMIO accessors.

For this specific `C20_PHY_CR0_LANEX` lane block, driver control flow is generally indirect. Direct source references to these exact macro names are mostly in generated offset/sh-mask headers; hand-written DC display code tends to program PHY/link state through link encoder, DPCS, DMUB, or BIOS/firmware sequencing abstractions. The constants in this range still control the final bit-level behavior whenever DCN 3.2.0 code reads or writes the corresponding PHY lane registers.

Representative runtime sequences enabled by this chunk include:

- TX bring-up selects rate/width/pstate, enables reference/analog/digital clocks, deasserts reset, enables serial/data paths, waits timing fields from `TX_PWRUP_TIME_*`, and observes `TX_PWRSM_STATE` or `TX_ACK`.
- TX equalization and calibration write main/pre/post cursor fields, DCC override fields, DCC calibration controls, term-code overrides, and analog CREG fields before or during link training.
- RX bring-up selects rate/width/pstate, enables analog AFE/CDR/deserializer paths through `RX_PSTATE_*`, waits `RX_PWRUP_TIME_*`, and checks lock/calibration status.
- RX CDR/VCO calibration drives `RX_VCO_CAL_CTRL_*` and observes `RX_VCO_STAT_*`, `RX_CDR_STAT`, DPLL frequency, and frequency-bound registers.
- RX adaptation configures `ADPT_CFG_*`, DFE/slicer/DCC registers, SSM controls, and IQC controls, then reads adaptation/tap/status fields to judge receiver convergence.
- Diagnostic paths can enable LBERT, stat counters, scope/correlation logic, comparator clocks, FIFO/clock-align status, and calibration status fields for hardware validation.

## State and Persistence Behavior

The file itself persists no state. The macro values describe hardware register state that persists in the DCN PHY until reset, power-gating, link retraining, mode set, firmware intervention, or another MMIO write changes it.

State domains represented in this chunk include:

- TX lane state: reset/data/serial enables, request/ack handshake, pstate/rate/width, MPLL selection, vboost/iboot, equalization cursors, DCC calibration settings, power-state recipes, startup timing, FIFO alignment, and TX FSM/status bits.
- TX analog state: override enables for clocks, reset, VCM hold, regulator/bleeder/fast-start paths, termination codes, DCC calibration, analog test bus selection, oscillator/regulator trim, pull-up/down controls, and equalization leg directions/enables.
- RX lane state: reset, detect/lock/ack status, CDR/VCO state, pstate/rate/width, AFE/VGA/CTLE/DFE settings, RX adaptation state-machine fields, slicer and VDAC offsets, DCC offsets, and IQC adjustment state.
- RX analog state: AFE/CDR/deserializer clock enables, signal-detect calibration, VCO override/frequency tune, analog calibration muxes and DAC controls, AFE trims, CTLE/boost/bias/VCM overrides, and scope/slicer controls.
- Diagnostic state: stat counters, sample counters, match masks, LBERT error state, DPLL frequency/bounds, clock-align FSM status, DCC FSM status, VCO-calibration done/correct/up/too-fast indicators, and calibration comparator clock settings.

Many fields are paired value/override-enable controls. For example, analog transfer and ASIC override registers commonly expose both `*_OVRD_VAL` or functional value fields and `*_OVRD_EN` bits. A caller must program both halves consistently; setting only an override value without enabling the override, or leaving an override enabled after link training, can leave the lane in a hard-to-debug state.

## Dependencies and Integration Points

This chunk depends on generated register-address definitions from the matching DCN 3.2.0 offset header, especially `dcn_3_2_0_offset.h`, where `ixC20_PHY_CR0_LANEX_*` offsets identify the actual indexed registers. The same logical PHY lane families also appear in generated DPCS headers, such as `dpcs_4_2_0_offset.h` and `dpcs_4_2_3_sh_mask.h`, indicating a shared PHY/DPCS register schema across generated ASIC register packages.

Integration points:

- AMD display code includes `dcn/dcn_3_2_0_offset.h` and `dcn/dcn_3_2_0_sh_mask.h` in DCN 3.2-specific components. For example, DMUB DCN 3.2 code includes both generated files when initializing register offsets, shifts, and masks for firmware mailbox and diagnostic paths.
- Link encoder and DPCS paths use generated register tables plus MMIO helper macros rather than hard-coding bit positions. This chunk provides the low-level constants those tables ultimately rely on for PHY lane control.
- Firmware and hardware sequencing can own some PHY programming, so these constants are also integration boundaries between kernel-side debug/diagnostic paths and display firmware or BIOS-programmed defaults.
- The offset/mask split is important: address macros select the register, and this chunk's shift/mask macros select fields inside the 16-bit register payload.

Because this is a generated header, the strongest integration contract is name stability. If a macro is renamed, moved to a different generated block, or generated with a different field spelling, downstream table initialization fails at compile time. If a macro keeps the same name but gets the wrong numeric mask or shift, the failure is usually runtime-only.

## Risks

- Bit drift is the primary risk. A wrong shift or mask can program the wrong lane bit while still compiling cleanly, causing failed link training, no display, intermittent hotplug failures, clock recovery failures, or poor signal integrity.
- Boundary risk exists for this chunk: it starts after the first fields of `ASIC_TX_ASIC_IN_0` and ends before the masks/rest of `ANA_XF_RX_SLICER_CTRL`. The merge lane must combine adjacent chunks before treating the register coverage as complete.
- Power sequencing fields are fragile. Incorrect `TX_PSTATE_*`, `RX_PSTATE_*`, or power-up timing masks can break reset release, analog clock/refgen sequencing, VCM hold timing, RX CDR/deserializer enable timing, or suspend/resume behavior.
- Override-enable pairs can force stale analog settings. Wrong masks around `*_OVRD_EN`, `*_OVRD_VAL`, DCC ranges, VCO settings, or AFE/CTLE/VGA fields can leave forced values active after calibration or prevent firmware/hardware FSMs from taking control.
- TX equalization and RX adaptation fields are signal-quality sensitive. Bad masks for cursor values, DFE taps, slicer offsets, DCC IDAC offsets, CTLE boost/pole, ATT/VGA gain, or VCO/DPLL controls can produce monitor-specific failures rather than deterministic software errors.
- Status and counter fields may have clear-on-write, latch, or done-bit behavior outside this header. Treating status masks as ordinary writable fields can accidentally clear diagnostics or hide incomplete calibration.
- Instance naming is easy to confuse. This is `C20_PHY_CR0_LANEX`; nearby chunks contain other PHY/CR/lane instances with nearly identical field names. A generated copy/paste or table mapping error can target the wrong lane.

## Test Signals

Useful validation is mostly build, hardware, and display-link oriented:

- Build coverage: DCN 3.2.0 AMDGPU display code compiles with no missing `C20_PHY_CR0_LANEX` shift/mask names and no generated header mismatch against offset definitions.
- Header consistency checks: every field in this range should have a matching shift/mask pair except for intentional chunk boundaries; masks should fit in 16 bits and align with their shifts and field widths.
- Link bring-up smoke tests: displays using the relevant DCN 3.2 PHY lane train successfully across supported link rates and lane widths.
- Mode-set and hotplug tests: repeated enable/disable, link retraining, suspend/resume, and dock/USB-C DP transitions do not leave TX/RX power-state or request/ack status stuck.
- Signal-quality tests: TX cursor programming, DCC calibration, RX CTLE/VGA/DFE adaptation, slicer offsets, and VCO/CDR calibration converge on hardware validation rigs.
- Diagnostic tests: LBERT, stat counters, sample counters, DPLL frequency reads, VCO calibration status, DCC FSM status, and clock-align status produce plausible values and can be cleared or rearmed as intended.
- Firmware coexistence tests: DMUB/firmware-owned PHY sequences continue to operate when kernel-side debug or diagnostic reads use the generated DCN 3.2.0 masks.

## Cross-Chunk Notes

- The first lines in this chunk are the tail of `C20_PHY_CR0_LANEX_DIG_ASIC_TX_ASIC_IN_0`; the comment heading and first fields such as `CLK_RDY`, `RESET`, `INVERT`, and `DATA_EN` are expected in the previous chunk.
- The final line only defines `C20_PHY_CR0_LANEX_DIG_ANA_XF_RX_SLICER_CTRL__RX_ANA_SLICER_CTRL_E__SHIFT`; its mask and additional slicer fields are expected in the next chunk.
- Later merge/reconciliation should preserve this source path and synthesize the per-file report from all chunks for `dcn_3_2_0_sh_mask.h`, rather than treating this chunk as a standalone final file report.
