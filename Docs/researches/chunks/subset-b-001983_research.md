# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 131968-134365

## Scope

This chunk is a generated AMD DCN 3.2.0 register-field shift/mask header slice. It contains C preprocessor constants only: `_SHIFT` macros for hardware bit positions, `_MASK` macros for raw register masks, and `//<REGISTER>` grouping comments. There are no C functions, structs, enums, local variables, branches, loops, allocations, locks, or filesystem persistence in this range.

The requested range covers 2,398 source lines and 2,163 `#define` lines. It begins in the middle of `C20_PHY_CR2_LANE2_DIG_TX_PWRCTL_TX_PWRUP_TIME_0`, after the `TX_REFGEN_EN_TIME`, `FAST_TX_REFGEN_EN_TIME`, and `TX_CLK_EN_TIME` shift definitions from the prior chunk, and starts here with `FAST_TX_CLK_EN_TIME__SHIFT` plus the masks for that register. It then covers the rest of the lane 2 PHY digital TX power, TX calibration/statistics, TX clock-align, TX LBERT, TX FIFO, TX analog crossbar, ASIC RX override, RX power, RX VCO calibration, RX CDR/DPLL/adaptation/statistics/IQC, and RX analog crossbar fields. It ends inside `C20_PHY_CR2_LANE2_DIG_ANA_XF_RX_AFE_OVRD_IN_2`, after `RX_ANA_AFE_CTLE_ZERO_MASK`; the remaining masks for that register and later RX analog CREG fields are in the next chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display-controller hardware metadata, not Ceph filesystem code. The visible `C20_PHY_CR2_LANE2` namespace identifies Display Core Next 3.2 PHY C20, CR2, lane 2 bit layouts. Runtime behavior comes from AMDGPU Display Core and DMUB/DCN support code that includes this header together with matching offset headers.

## Purpose

The purpose of this chunk is to describe the bit-level ABI for one PHY lane's control and status registers. The matching generated offset header supplies MMIO register addresses; this shift/mask header supplies field positions and masks so AMD display code can pack read/modify/write values, decode volatile hardware status, program calibration state machines, and expose low-level debug/test modes.

The major hardware surfaces represented here are:

- TX power sequencing and pstate timing for lane 2: reference generator, clock enable, VCM hold, VBOOST disable, reset, RX-detect, serial enable, bleeder enable, clock-align skip, DCC DAC writes, request disable, and power-state status.
- TX DCC, statistics, clock alignment, LBERT pattern generation, calibration status, FIFO control, and analog TX override/status/CREG fields.
- ASIC-to-RX override and status plumbing for receiver power, VCO/CDR, EQ/adaptation, DFE taps, calibration, signal detect, and miscellaneous controls.
- RX pstate sequencing, power-up timing, RX clock/digital clock enables, DAC write gates, power-state status, VCO calibration controls/timers/status, LBERT error counting, CDR/DPLL controls, and DPLL frequency bounds.
- RX adaptation control for attenuation, VGA, CTLE, DFE tap configuration/status, DAC override offsets, fast-settle flags, slicer-search-machine configuration, final search status, pattern/stat counters, and IQC reset/config/status.
- RX analog crossbar override/status fields for power, signal detect calibration, VCO override, DAC/calibration control, AFE overrides, scope/slicer/IQ/IQC controls, loopback, AFE update, sample select, termination code, and analog status readback.

These definitions are generated data, but they are not low-risk data. A wrong bit position can still compile and can cause live MMIO writes to enable a different analog control, poll the wrong status bit, leave a calibration FSM stuck, corrupt link-training diagnostics, or disturb receiver adaptation on a physical display link.

## Important APIs, Types, And Macros

This chunk exports the standard AMD register-field convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit index.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register-positioned form.
- `//<REGISTER>` comments group the definitions by hardware register.

There are no callable APIs or C types in this range. Important generated macro families are:

- `C20_PHY_CR2_LANE2_DIG_TX_PWRCTL_*` for TX pstate/timing/control/status.
- `C20_PHY_CR2_LANE2_DIG_TX_DCC_CTL_*` for TX DCC IDAC offset override and DCC FSM status.
- `C20_PHY_CR2_LANE2_DIG_TX_STAT_*` for TX sample/statistic counters and comparator-clock control.
- `C20_PHY_CR2_LANE2_DIG_TX_CLK_ALIGN_*` for TX clock-alignment startup/retrigger/status.
- `C20_PHY_CR2_LANE2_DIG_TX_LBERT_*`, `TX_LVL_CALC_STAT`, and `TX_FIFO_CTL` for link-BERT, TX level calibration, and FIFO bypass/read-pointer control.
- `C20_PHY_CR2_LANE2_DIG_ANA_XF_TX_*` for TX analog crossbar overrides, analog DCC calibration, EQ status overrides/readback, CREG controls, and CREG override strobes.
- `C20_PHY_CR2_LANE2_DIG_ASIC_RX_*` for ASIC-side RX override inputs/outputs, status inputs, EQ controls, and miscellaneous override gating.
- `C20_PHY_CR2_LANE2_DIG_RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_LBERT_*`, `RX_CDR_*`, and `RX_DPLL_*` for RX power, VCO, test, clock-data-recovery, and DPLL programming.
- `C20_PHY_CR2_LANE2_DIG_RX_ADPTCTL_*` for RX equalization/adaptation controls, status, SSM, DCC offset overrides, fast flags, and reset controls.
- `C20_PHY_CR2_LANE2_DIG_RX_STAT_*` for RX pattern matching, sample counters, statistic counters, scope/correlation control, and extended load values.
- `C20_PHY_CR2_LANE2_DIG_RX_IQC_CTL_*` for IQ calibration reset adjustment, configuration, and status.
- `C20_PHY_CR2_LANE2_DIG_ANA_XF_RX_*` for RX analog crossbar power, signal detect, VCO, calibration, DAC, AFE, scope, slicer, IQ/IQC, loopback, update, termination, and status fields.

Consumers normally use these macros indirectly through generated register-table definitions and register-helper macros. In this tree, direct include sites for `dcn_3_2_0_sh_mask.h` include `display/dmub/src/dmub_dcn32.c`, `amdgpu/gmc_v11_0.c`, `display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, `display/dc/gpio/dcn32/hw_translate_dcn32.c`, `display/dc/gpio/dcn32/hw_factory_dcn32.c`, and `display/dc/resource/dcn32/dcn32_resource.c`. The lane-specific PHY constants in this chunk are most relevant to generated DCN 3.2 hardware sequencing and link/PHY programming paths.

## TX Power, Calibration, Statistics, And Analog Crossbar

The first section completes `TX_PWRUP_TIME_0` and then defines TX power-up timing registers `TX_PWRUP_TIME_1` through `TX_PWRUP_TIME_5`. These fields govern staged analog bring-up and shutdown timing: `TX_VCM_HOLD_TIME`, `SKIP_TX_VCM_HOLD_WAIT`, `TX_VBOOST_DIS_TIME`, `TX_RESET_TIME`, `TX_RXDET_TIME`, `FAST_TX_RXDET`, `TX_VREG_FAST_START_TIME`, `TX_VCM_HOLD_GS_TIME`, `TX_SERIAL_EN_TIME`, `FAST_TX_SERIAL_EN_TIME`, and `TX_BLEEDER_EN_TIME`. These values are hardware delays or fast-path bypass flags rather than software timers.

`TX_PWRCTL_TX_CTL` exposes active TX control bits: `TX_CLK_EN`, clock-alignment skip controls, `DTB_SEL`, DCC force/write enable, `TX_REQ_DISABLE`, late-loopback clock enable, and TX calibration DAC override gating. `TX_PWRCTL_TX_STATUS` exposes `TX_RATE_IRQ` and `TX_PWRSM_STATE`, so callers must treat it as volatile readback. The preceding chunk contains complete TX pstate definitions for P0/P0S/P1/P2; this chunk carries the timing and live-control parts used during pstate transitions.

The TX DCC and statistics registers include:

- `TX_DCC_DIFF_IDAC_OFST` and `TX_DCC_CM_IDAC_OFST`, each with an 8-bit `VAL`, `OVRD_EN`, and reserved upper bits.
- `TX_DCC_CTL_STAT`, exposing `TX_DCC_FSM_STATE` and `TX_DCC_DAC_FSM_STATE`.
- `TX_STAT_LD_VAL_1`, `TX_STAT_STAT_CTL0`, `TX_STAT_SMPL_CNT1`, `TX_STAT_STAT_CNT_0`, `TX_STAT_CAL_COMP_CLK_CTL`, and `TX_STAT_STAT_STOP`, which configure and read TX sample/statistic counters and comparator clock controls.

Clock-alignment fields are grouped under `TX_CLK_ALIGN_TX_CTL_0`, `TX_CLK_ALIGN_TX_CTL_1`, and `TX_CLK_ALIGN_CLK_ALIGN_STATUS`. They cover startup delay, 2UI-shift counts for 32b/16b/8b and 40b/20b/10b modes, retrigger control, sticky-late filter disable, shift count, FSM state, and TX clock state.

`TX_LBERT_CTL` and `TX_LBERT_PAT1_0` through `PAT1_3` configure a lane BERT/test-pattern source, including mode selection, injected error trigger, `PAT0`, and a 48-bit or extended pattern split across 16-bit registers. `TX_LVL_CALC_STAT` exposes a 4-bit calibration code. `TX_FIFO_CTL` controls the TX FIFO read pointer start and bypass.

The TX analog crossbar region is broad:

- `ANA_XF_TX_OVRD_OUT_0` through `_3` provide per-signal override values and override enables for analog clocks, MPLLA/MPLLB sources, VREG, DCC, reset, serial enable, data enable, rate, VBOOST, RX detect, VCM hold, refgen, bleeders, and word clock.
- `ANA_XF_TX_TERM_CODE_OVRD_OUT` and `TERM_CODE_CLK_OVRD_OUT` control termination code override and the clock/self-clear behavior for applying it.
- `ANA_XF_TX_ANA_DCC_EN`, `ANA_DCC_CONFIG`, `ANA_DCC_CAL_OVRD_EN`, `ANA_DCC_CAL_COMP_EN`, `ANA_DCC_CAL_CTRL_EN`, `ANA_DCC_CAL_CTRL_SEL`, `ANA_DCC_CAL_DAC_CTRL_RANGE`, and `ANA_DCC_CAL_DATA` define analog DCC calibration sequencing and data.
- `ANA_XF_TX_STAT_EQ_OVRD_0` through `_4` and `ANA_XF_TX_STAT_EQ_OUT_0` through `_4` split EQ-related TX coefficients/status across multiple 16-bit registers. They include pre-driver control, main/post/pre cursors, marginal-control fields, A/B/C coefficient groups, IDs, coefficients, and done flags.
- `ANA_XF_TX_STAT_OUT_0`, `STAT_OUT_1`, and `STAT_IN_0` report analog TX state such as clock enables, reset, serial/data enable, VREG/VBOOST/bleeder/refgen controls, pstate, and calibration result/data.
- `ANA_XF_TX_ANA_CREG00` through `CREG05` and `ANA_CREG0_OVRD`/`ANA_CREG1_OVRD` expose direct analog configuration and override-latch controls, including serializer, clock, calibration, ATB/measurement, rate, VREG, VCM, reset, data enable, and manual tuning fields.

## ASIC RX Override And RX Power/VCO/CDR/DPLL

The `DIG_ASIC_RX_*` families define the interface between digital control logic and RX analog/adaptation logic. `OVRD_IN_0` through `OVRD_IN_4` provide override values and enable bits for RX data rate, CDR, VCO, deserializer, clocking, DFE, bypass slicer, AFE, bleeder, calibration, IQ sync, word clock, async reset, CDR phase update gain, DFE tap controls, and bypass/sample paths. `OVRD_SIGDET_IN`, `OVRD_VCO_IN`, and `OVRD_EQ_IN_0` through `_11` extend this to signal-detect thresholds, VCO frequency/calibration/tuning, EQ/DFE controls, slicer levels, CDR bandwidth/phase-update values, tap adaptation enables, attenuation/VGA/CTLE adaptation, and eye-scan or pattern-control fields. `OVRD_OUT_0`, `ASIC_IN_0` through `_3`, `CDR_VCO_ASIC_IN`, `EQ_ASIC_IN_0` through `_2`, `ASIC_OUT_0`, and `OVRD_MISC` carry status/readback or output override control bits.

The RX power-control section defines `RX_PSTATE_P0`, `P0S`, `P1`, and `P2`, each mostly repeating analog enable bits for bleeder, AFE, clock VREG, div16p5 clock, clock, clock DCC, deserializer, CDR, VCO resets, continuous calibration, digital clock, DFE, and bypass slicer. A notable generated-name wart appears in `RX_PWRCTL_RX_PSTATE_P2`: bit 0 is named `RX_P0_ANA_BLEEDER_EN` even though the register is P2. That may reflect source register XML naming, but any consumer or reviewer should avoid "fixing" it locally without regenerating all paired headers and tables.

`RX_PWRUP_TIME_0` and `RX_PWRUP_TIME_1` define RX staged timing for rate changes, VREG enable/fast start, CDR enable, deserializer enable/disable, clock-DCC enable, and fast clock-DCC enable. `RX_CTL` contains live RX clock/digital clock enables, DCC/equalizer force-DAC-write controls, IQC FSM skip, and calibration DAC gate. `RX_STATUS` reports `RX_RATE_IRQ` and `RX_PWRSM_STATE`.

`RX_VCOCAL_RX_VCO_CAL_CTRL_0` through `_2`, `RX_VCO_CAL_TIME_0` and `_1`, and `RX_VCO_STAT_0` through `_2` describe the VCO calibration engine. Control fields cover integral gain fixed counts, count shifts, bounce counts, bin/int-gain hold disables, coarse-caldone disable, exit-bin-search, VCO override selection, frequency/calibration resets, continuous calibration enable, internal calibration mode disable, DPLL calibration update gain, DTB selection, frequency-tune start values, calibration steps, and skip flags. Status fields expose analog CDR frequency tune, counter power/enable, startup/VCO enable, FSM state, calibration done, DPLL frequency reset, final counter value, too-fast/correct/up flags.

RX LBERT is represented by `RX_LBERT_CTL` and `RX_LBERT_ERR`, with mode, sync, BER select, a 15-bit error count, and overflow. The RX CDR block includes `CDR_CTL_0` through `_4` and `RX_CDR_STAT`, covering phase detector enable/edge/polarity, phase-update gain, wide/fine gain, PI offset and polarity, DAC override values, CDR update/skip controls, CDR control gates, fast-settle controls, and FSM/done status. `RX_DPLL_FREQ`, `RX_DPLL_FREQ_BOUND_0`, and `_1` define DPLL frequency and high/low bounds.

## RX Adaptation, Statistics, IQC, And Analog RX Crossbar

`RX_ADPTCTL_ADPT_CFG_0` through `_12` are adaptation configuration registers for CTLE, VGA, attenuation, DFE, skip modes, reset behavior, target thresholds, sample timing, adaptation enables, saturation limits, and related tuning fields. Status registers such as `ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, and `DFE_TAP1_STATUS` through `DFE_TAP5_STATUS` expose the converged adaptation values. Additional DFE/slicer registers provide explicit DAC or level offsets for data even/odd high/low, error even/odd, bypass even/odd, and even/odd slicer control.

The DCC offset override group covers phase/data/bypass diff and common-mode IDAC offsets: `RX_DCC_PHASE_DIFF_IDAC_OFST`, `RX_DCC_PHASE_CM_IDAC_OFST`, `RX_DCC_DATA_DIFF_IDAC_OFST`, `RX_DCC_DATA_CM_IDAC_OFST`, `RX_DCC_BYPASS_DIFF_IDAC_OFST`, and `RX_DCC_BYPASS_CM_IDAC_OFST`. These use the same pattern as TX DCC offsets: an 8-bit value, override enable, and reserved bits. `RX_FAST_FLAGS` exposes fast AFE/DFE settle and SSM DAC settle.

The slicer-search-machine section, `RX_ADPTCTL_SSM_SSM_CFG_0` through `_4` and `SSM_FINAL_CODE`, defines threshold offsets, DAC/destination selection, start, linear/bin step counts, initial DAC code, bin hold, SSM threshold, wait counts, LPF bypass, sticky/direction controls, and final code/done/abort/FSM-state readback. This block is state-machine oriented: software programs parameters and start bits, then observes completion and abort/status fields.

The RX statistics section defines pattern masks, pattern values, data masks, correlation/stat source selections, sample counters, seven statistic counters, extended sample-count/load-value registers, counter-freeze controls, and stop controls. Important families include `RX_STAT_LD_VAL_1`, `DATA_MSK`, `MATCH_CTL0` through `MATCH_CTL6`, `STAT_CTL0` through `STAT_CTL2`, `SMPL_CNT1`, `SMPL_CNT1_29DN15`, `SMPL_CNT1_44DN30`, `STAT_CNT_0` through `_6`, `STAT_CNT_N_SHD`, `SMPL_CNT2`, and `LD_VAL_EXT_1/2`. Many count registers reuse the high bit as a `*_DONE` flag, so decoders must mask the count and done bit separately.

`RX_IQC_CTL_RESET_ADJUST`, `RX_IQC_CTL_CONFIG`, and `RX_IQC_CTL_STAT` define IQ-calibration reset adjustment, enable/reset/delay/override behavior, selected calibrations, and status. The `CONFIG` register includes disable, enable, reset, sample selection, skew, and delay fields; `STAT` exposes final bypass/data values and done state.

The RX analog crossbar block starts with `ANA_XF_RX_CTL_OVRD_OUT` and `ANA_XF_RX_PWR_OVRD_OUT_0/_1`, then continues through signal detect, VCO, calibration, DAC, AFE, scope, slicer, IQ, IQC, loopback, AFE update, sample select, termination, and status fields:

- Power/control override registers cover analog CDR/VCO/clock/deserializer/AFE/DFE/loopback/bleeder/VREG/word-clock/reset controls and their override enables.
- `SIGDET_CAL_EN`, `SIGDET_HF_CAL`, and `SIGDET_LF_CAL` configure high/low-frequency signal-detect calibration.
- `VCO_OVRD_OUT_0` through `_2` override CDR VCO, frequency tune, VCO counter controls, calibration result, and DPLL/VCO reset/enable controls.
- `CAL_0`, `CAL_1`, `VDAC_RANGE_SEL`, `DAC_CTRL`, `ANA_RTRIM`, `DAC_CTRL_OVRD`, `DAC_CTRL_SEL`, and `DCC_CAL_DAC_CTRL_RANGE` configure analog calibration and DAC range/control selection.
- `AFE_OVRD_IN_0` and `_1` provide AFE rate, CTLE, TIA, attenuation, VGA, DFE tap, and related override fields; the chunk ends inside `AFE_OVRD_IN_2`, after `RX_ANA_AFE_CTLE_ZERO_MASK`.
- `SCOPE`, `SLICER_CTRL`, `ANA_IQ`, `ANA_IQC_BYP_OVRD`, `ANA_IQC_BYPASS_ADJUST_CLK`, `ANA_IQC_DATA_OVRD`, `ANA_IQC_DATA_ADJUST_CLK`, `ANA_CAL_DAC_CTRL_EN`, `ANA_LOOPBACK_CTRL`, `ANA_AFE_UPDATE_EN`, `ANA_DFE_SAMP_SEL`, `ANA_BYP_SAMP_SEL`, and `ANA_PHS_SAMP_SEL` cover low-level measurement, slicer, IQ sync/bypass, self-clearing adjust clocks, calibration DAC control, loopback, AFE update, and sample-source selects.
- `RX_TERM_CODE_OVRD_OUT` and `RX_TERM_CODE_CLK_OVRD_OUT` program termination code override and its apply/self-clear clock.
- `RX_STAT_OUT_0`, `RX_STAT_OUT_1`, and `RX_STAT_IN_0` expose analog RX state such as deserializer/loopback, clocks, DCC, VREG, bleeder, AFE, bypass slicer, DFE, data rate, IQ sync reset/bypass, calibration LPF bypass, CDR phase-update gain, CDR/VCO controls, fast-start, flyover, async reset, word clock, calibration result, scope data, and VCO counter.

## Control Flow And State

There is no executable control flow in this header. The effective control flow occurs in code that uses these macros to perform MMIO access:

1. Include generated address and shift/mask headers for DCN 3.2.0.
2. Select a register instance for PHY C20 CR2 lane 2.
3. Compose values with `<FIELD>__SHIFT` and `<FIELD>_MASK`, often through generated helper macros.
4. Write MMIO registers or perform read/modify/write updates.
5. Poll or decode status fields such as TX/RX power state, DCC/VCO/CDR/SSM FSM state, calibration done bits, LBERT errors, sample counter done bits, and analog status readbacks.

Hardware state is persistent only in the sense that MMIO writes alter device registers until reset, power-gating, firmware sequencing, or a later write changes them. Some fields are command-like or self-clearing, such as adjust-clock, calibration/update, reset, start, clear, or clock-latch bits. Others are volatile status readbacks, counters, or FSM state. This header does not encode access type, reset values, write-one-to-clear behavior, or sequencing constraints; those semantics must come from the generated register database, hardware documentation, firmware contracts, and consuming driver code.

Reserved fields are explicitly represented in many registers. Normal driver code should preserve reserved bits on read/modify/write and avoid assigning meaning to `RESERVED_*` names. The generated masks use 16-bit-style values with an `L` suffix throughout this C20 PHY slice, which is consistent with PHY register windows but still relies on callers using the appropriate access width and address from the paired offset header.

## Dependencies And Integration Points

This file depends on the generated DCN 3.2 register schema being internally consistent across:

- `dcn_3_2_0_sh_mask.h`, which supplies the field shifts and masks.
- Matching DCN 3.2 offset/address headers, which supply register addresses and instances.
- Generated `reg_helper`-style tables and macros in AMDGPU Display Core that expect exact macro names.
- DCN 3.2 link/PHY, DMUB, clock, IRQ, GPIO, and resource code that includes this header.

The relevant integration points are hardware-facing, not filesystem-facing:

- Display link training and PHY bring-up/tear-down can use the TX/RX pstate, timing, DCC, CDR, VCO, DPLL, and adaptation fields.
- Diagnostic and factory/debug paths can use LBERT, statistic counters, scope/slicer controls, DTB selects, and analog CREG/override fields.
- Firmware or low-level sequencing code can use the same fields to coordinate calibration, pstate transitions, reset strobes, and status polling.
- Higher-level display resource and link management code depends on the generated DCN 3.2 macro namespace compiling against register lists for the ASIC family.

Because the macros are preprocessor constants, failures usually surface at compile time only if a macro is missing or renamed. Incorrect numeric values are much harder: they appear as runtime link failures, display blanking, unstable high-rate links, failed sleep/resume, calibration timeouts, or inconsistent diagnostics.

## Risks

- Chunk-boundary incompleteness: this range starts in the middle of `TX_PWRUP_TIME_0` and ends in the middle of `RX_AFE_OVRD_IN_2`. Per-file reconciliation must merge adjacent chunks before making register-completeness claims.
- Generated-name drift: consumers rely on exact macro names. Renaming typo-like fields such as `RX_P0_ANA_BLEEDER_EN` inside the P2 register or `NUN_BIN_STEPS` inside SSM config would break the generated ABI unless all generated artifacts and consumers change together.
- Mask/shift mismatch: a field can have a syntactically valid shift and mask that do not correspond. Such bugs will compile and may only appear as bad PHY behavior.
- Reserved-bit damage: if callers use these masks without read/modify/write preservation, reserved bits or adjacent analog controls can be disturbed.
- Access-type ambiguity: this header does not tell callers whether a bit is status-only, write-one-to-clear, self-clearing, latch-on-write, pulse, or retained configuration.
- State-machine sequencing: VCO, CDR, DCC, SSM, IQC, pstate, and AFE update fields likely require specific ordering and delay/poll behavior. The header cannot enforce that.
- Lane/instance copy risk: this is lane 2 under `C20_PHY_CR2`. Similar generated lanes may have near-identical fields, so manual edits can accidentally paste the wrong lane or CR namespace.
- Test-mode exposure: LBERT, DTB, scope, analog CREG, override, and forced-DAC controls can disrupt normal links if enabled outside controlled debug or validation paths.

## Test Signals

Useful validation signals for changes touching this chunk or its generated source are:

- Build coverage for AMDGPU DCN 3.2 include users, including `display/dmub/src/dmub_dcn32.c`, `display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, GPIO/resource code, and `amdgpu/gmc_v11_0.c`.
- Generated-header consistency checks that every field has a matching `_SHIFT` and `_MASK`, masks are compatible with shifts and field widths, and no duplicate register-field names are introduced.
- Cross-check against the paired DCN 3.2 offset header and original register database for `C20_PHY_CR2_LANE2` register ordering and field values.
- Runtime display link tests on DCN 3.2 hardware: hotplug, link training at multiple rates, suspend/resume, modeset, DSC/non-DSC displays, and multi-monitor configurations that exercise PHY lane programming.
- PHY calibration/link diagnostics: verify VCO/CDR/DCC/IQC/SSM completion bits, power-state FSM values, RX/TX statistic counters, and absence of calibration timeout logs.
- Debug/test-mode sanity tests, where available, for LBERT pattern/error paths, scope/stat counters, and analog override restoration after use.
- Regression monitoring for black screen, flicker, intermittent HPD/link failures, high-rate link instability, display resume failures, and unexpected power-management behavior.
