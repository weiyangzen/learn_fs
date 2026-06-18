# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 97961-100340

## Scope

This chunk is a generated AMD DCN 3.2.0 register-field shift/mask header slice. It contains C preprocessor constants only: register grouping comments and paired `__SHIFT`/`_MASK` macros for MMIO bitfields. There are no C functions, structs, enums, local variables, branches, loops, allocations, locks, or file-backed persistence in this range.

The requested line range covers 2,380 source lines. Every line in the range is either a `//<REGISTER>` grouping comment or a `#define`; there are 204 register groups and 2,176 defines, split exactly into 1,088 shift definitions and 1,088 mask definitions. The range starts inside `C20_PHY_CR1_LANE1_DIG_ANA_XF_RX_ANA_IQ` after the first two shift fields were defined by the previous chunk, then covers the rest of lane 1 RX analog transfer fields and most of the lane 2 C20 PHY CR1 digital/analog register field layout. It ends inside `C20_PHY_CR1_LANE2_DIG_RX_ADPTCTL_RX_DCC_DATA_DIFF_IDAC_OFST`, after the `VAL` and `OVRD_EN` shift definitions and before the reserved shift and mask definitions that appear in the next chunk.

Although the repository path is under a `ceph-client` source mirror, this is AMDGPU display-controller hardware metadata, not Ceph filesystem logic.

## Purpose

The purpose of this header range is to provide bit positions and register-positioned masks for DCN 3.2.0 C20 PHY lane programming. Matching generated offset headers supply MMIO register addresses; this file supplies the field layout used by generated register tables and register helper macros to pack writes, decode reads, acknowledge latched status, and preserve unrelated fields in read/modify/write paths.

The visible hardware surface is concentrated on display PHY lane control:

- The tail of lane 1 RX analog transfer fields for IQ, IQC bypass/data override clocks, calibration DAC control, loopback, AFE update, sample selects, termination code control, RX status, AFE overrides, and analog CREG controls.
- Lane 2 ASIC lane/TX/RX override input, ASIC input, and ASIC output paths, including per-signal override values and enable bits.
- Lane 2 TX power-state and power-up timing controls, TX control/status, TX DCC controls, TX statistic/counter controls, clock-align controls, LBERT pattern generation, TX FIFO, analog TX override/status, TX termination, TX analog DCC calibration, and TX analog CREG controls.
- Lane 2 RX ASIC override and ASIC input/output paths, including RX data/control, equalization, signal detect, VCO/CDR inputs, RX override miscellaneous fields, and extended RX EQ override fields.
- Lane 2 RX power-state, power-up timing, RX control/status, VCO calibration controls/status, RX LBERT error reporting, CDR/DPLL controls/status, and RX adaptive-control configuration/status.
- The beginning of lane 2 RX DCC adaptive offset controls for phase/data differential and common-mode IDAC offsets.

These macros are generated data, but they form a hardware ABI. A wrong numeric value can still compile and can then cause the display driver to write the wrong PHY bit, misread a status field, clear a diagnostic event, or program a lane into an invalid electrical/power/training state.

## Important APIs, Types, And Macros

This chunk exports only generated preprocessor symbols. The naming convention is the API:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register-positioned form.
- `//<REGISTER>` comments group all following field definitions until the next register comment.

There are no callable APIs or C types in this range. The most important macro namespaces are:

- `C20_PHY_CR1_LANE1_DIG_ANA_XF_RX_*` for lane 1 RX analog transfer and CREG fields.
- `C20_PHY_CR1_LANE2_DIG_ASIC_*` for lane 2 ASIC-facing lane, TX, and RX override/input/output fields.
- `C20_PHY_CR1_LANE2_DIG_TX_PWRCTL_*`, `DIG_TX_DCC_CTL_*`, `DIG_TX_STAT_*`, `DIG_TX_CLK_ALIGN_*`, `DIG_TX_LBERT_*`, and `DIG_TX_FIFO_*` for lane 2 TX power, timing, calibration, statistics, align, test, and FIFO fields.
- `C20_PHY_CR1_LANE2_DIG_ANA_XF_TX_*` for lane 2 TX analog transfer override, termination, DCC, status, EQ, and CREG fields.
- `C20_PHY_CR1_LANE2_DIG_RX_PWRCTL_*`, `DIG_RX_VCOCAL_*`, `DIG_RX_LBERT_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, and `DIG_RX_ADPTCTL_*` for lane 2 RX power, VCO calibration, link test, clock/data recovery, DPLL, and adaptive equalization fields.

The field names show common semantic families that consumers must keep distinct:

- `*_OVRD_*`, `*_OVRD_EN`, and `*_OVRD_MISC` fields carry override values and override enables.
- `*_ASIC_IN_*` and `*_ASIC_OUT_*` expose normal hardware path input/output state.
- `*_PSTATE_*`, `*_PWRUP_TIME_*`, `*_CTL`, and `*_STATUS` describe power-sequencing controls and readback.
- `*_STAT_*`, `*_STATUS`, and `*_ERR` expose counters, state-machine state, done bits, error counts, and calibration status.
- `*_CAL_*`, `*_DCC_*`, `*_VCO_*`, `*_CDR_*`, `*_DPLL_*`, `*_ADPT_*`, `*_DFE_*`, `*_CTLE_*`, `*_VGA_*`, and `*_SLICER_*` describe analog calibration, clock/data recovery, equalization, and receiver adaptation internals.

## Lane 1 RX Analog Tail

The lane 1 part of this chunk continues from the prior chunk inside `C20_PHY_CR1_LANE1_DIG_ANA_XF_RX_ANA_IQ`. Visible fields include clock/VRO always-on control, IQ-sync bypass override value/enable, IQ-sync reset override value/enable, and the mask definitions for the entire register including `SENSE_EN` and `SENSE_SEL` that began before this range.

The rest of the lane 1 RX analog tail covers:

- IQC bypass/data override value and enable fields, plus their self-clearing adjust-clock controls.
- RX analog calibration DAC control enable and self-clear-disable fields.
- Loopback clock enable, loopback select, override enables, and DCC calibration enable.
- AFE update enable, update self-clear disable, and update override enable.
- DFE, bypass, and phase sample selects.
- RX termination code override, termination clock, and termination self-clear-disable controls.
- `RX_STAT_OUT_0`, `RX_STAT_OUT_1`, and `RX_STAT_IN_0` fields for readback of clock, AFE, loopback, DFE, data-rate, CDR, VCO, reset, word clock, calibration result, scope data, and VCO counter state.
- AFE override input fields for CTLE zero and TIA bias.
- `RX_ANA_CREG00` through `RX_ANA_CREG11` and CREG override registers, which expose analog control knobs for sample selection, measurement/ATB, DCC, CDR/PLL, calibration, VCO, AFE, CTLE, bias, VCM, probe/test, and override groups.

This is a low-level electrical lane programming surface. Many fields look like ordinary booleans but actually participate in calibration pulses, self-clearing update clocks, or override-enable/value pairs. Correct use depends on the caller sequencing these fields with PHY reset, link training, rate changes, and analog settle timing.

## Lane 2 ASIC Interface

The lane 2 ASIC-interface area defines the digital boundary between higher-level display logic and PHY lane TX/RX controls.

For TX, the chunk includes:

- `LANE_OVRD_IN` for lane-level mux and mode override values/enables.
- `TX_OVRD_IN_0` through `TX_OVRD_IN_5` for TX reset, clock, serial, data, reference generator, VCM hold, RX-detect allowance, vboost, DCC, VREG bleeder, word clock, impedance, preset, coefficient, polarity, rate, lane/link mode, and pattern/control overrides.
- `TX_OVRD_OUT` for TX status and control override output state.
- `LANE_ASIC_IN` and `TX_ASIC_IN_0` through `TX_ASIC_IN_3` for normal non-override input fields.
- `TX_ASIC_OUT` and `TX_OVRD_MISC` for TX output/status and miscellaneous override selection.

For RX, the chunk includes:

- `RX_OVRD_IN_0` through `RX_OVRD_IN_4`, `RX_OVRD_SIGDET_IN`, `RX_OVRD_VCO_IN`, and `RX_OVRD_EQ_IN_0` through `RX_OVRD_EQ_IN_11` for RX reset, clock, data, AFE, DFE, CDR, VCO, signal detect, rate, equalizer, tap, slicer, VCM, bias, and other receiver-side override value/enables.
- `RX_OVRD_OUT_0` for override readback/output.
- `RX_ASIC_IN_0` through `RX_ASIC_IN_3`, `RX_CDR_VCO_ASIC_IN`, and `RX_EQ_ASIC_IN_0` through `RX_EQ_ASIC_IN_2` for normal RX input state.
- `RX_ASIC_OUT_0` and `RX_OVRD_MISC` for RX output/status and miscellaneous override behavior.

The repeated override pattern is important: value fields and enable fields must be paired correctly. Setting an override value without its enable may do nothing; setting an enable with stale value bits may force the lane into an unintended state.

## Lane 2 TX Control, Status, And Analog Transfer

The TX power-control region defines `TX_PSTATE_P0`, `TX_PSTATE_P0S`, `TX_PSTATE_P1`, and `TX_PSTATE_P2` with the same broad set of power-state fields: analog reference generator, VCM hold, analog clock, analog reset, serializer, digital clock, data enable, RX-detect allowance, vboost allowance, analog DCC enable, VREG bleeder enables, and word clock enable. `TX_PWRUP_TIME_0` through `TX_PWRUP_TIME_5` define timing windows and skip/fast-path fields used by power-up sequencing. `TX_CTL` and `TX_STATUS` then expose control bits and readback state for TX power and sequencing.

The TX DCC, stats, and test regions include:

- `TX_DCC_CTL_TX_DCC_DIFF_IDAC_OFST`, `TX_DCC_CTL_TX_DCC_CM_IDAC_OFST`, and `TX_DCC_CTL_STAT` for TX duty-cycle-correction offset overrides and status.
- `TX_STAT_LD_VAL_1`, `TX_STAT_STAT_CTL0`, `TX_STAT_SMPL_CNT1`, `TX_STAT_STAT_CNT_0`, `TX_STAT_CAL_COMP_CLK_CTL`, and `TX_STAT_STAT_STOP` for statistic capture, sample counts, counters, calibration comparison clock control, and stop control.
- `TX_CLK_ALIGN_TX_CTL_0`, `TX_CLK_ALIGN_TX_CTL_1`, and `TX_CLK_ALIGN_CLK_ALIGN_STATUS` for TX clock alignment control and done/status reporting.
- `TX_LBERT_CTL` and `TX_LBERT_PAT1_0` through `TX_LBERT_PAT1_3` for link BERT/test pattern generation.
- `TX_LVL_CALC_STAT` and `TX_FIFO_CTL` for level calculation status and FIFO behavior.

The lane 2 analog TX transfer section includes:

- `ANA_XF_TX_OVRD_OUT_0` through `_3` and TX termination code/clock override fields.
- TX analog DCC enable, config, calibration override enable, calibration comparator enable, calibration control enable/selection, DAC control range, and calibration data.
- `TX_STAT_EQ_OVRD_0` through `_4`, `TX_STAT_OUT_0`, `TX_STAT_OUT_1`, and `TX_STAT_EQ_OUT_0` through `_4` for equalization override/status and analog TX readback.
- `TX_STAT_IN_0` plus `TX_ANA_CREG00` through `TX_ANA_CREG05` and CREG override fields for analog TX configuration and debug/probe/calibration fields.

TX fields are stateful hardware controls, not simple software variables. Power-state fields usually persist until lane reset, power gating, or another hardware sequence changes them. Status and counter fields are volatile readbacks. Calibration and statistic controls may have pulse, latch, or self-clear behavior that is not encoded in the mask names alone.

## Lane 2 RX Power, Calibration, CDR, DPLL, And Adaptation

The lane 2 RX power-control fields mirror the TX structure with RX-specific semantics. `RX_PSTATE_P0`, `RX_PSTATE_P0S`, `RX_PSTATE_P1`, and `RX_PSTATE_P2` cover RX analog clock/AFE/DFE/CDR/VCO/word-clock style enable and reset state. `RX_PWRUP_TIME_0` and `_1` define timing/skip controls, while `RX_CTL` and `RX_STATUS` expose receiver control and readback.

VCO and clock recovery fields include:

- `RX_VCOCAL_RX_VCO_CAL_CTRL_0` through `_2` for VCO calibration control.
- `RX_VCOCAL_RX_VCO_CAL_TIME_0` and `_1` for VCO calibration timing.
- `RX_VCOCAL_RX_VCO_STAT_0` through `_2` for calibration/readback status.
- `RX_LBERT_CTL` and `RX_LBERT_ERR` for receiver-side test/error observation.
- `RX_CDR_CDR_CTL_0` through `_4` and `RX_CDR_STAT` for CDR configuration and status.
- `RX_DPLL_FREQ`, `RX_DPLL_FREQ_BOUND_0`, and `RX_DPLL_FREQ_BOUND_1` for DPLL frequency and bounds.

The RX adaptive-control section is the densest part of the range. `ADPT_CFG_0` through `ADPT_CFG_10` define adaptation configuration for attenuation, VGA, CTLE boost/pole/zero, DFE taps, AFE rate, VCM, bias, step sizes, initialization values, mu values, slicers, and threshold weights. `RST_ADPT_CFG` exposes per-subsystem reset controls for adaptation blocks. Status registers report adaptation code and state for ATT, VGA, CTLE, DFE tap1 through tap5, and ASM/dac-control done/state fields.

DFE and slicer data fields include even/odd high/low VDAC offsets, slicer controls, error slicer levels, and bypass/error VDAC offsets. The range also includes `ADPT_RESET`, `ADPT_CFG_10`, and the start of RX DCC adaptive offset override registers for phase differential/common-mode and data differential offsets.

These fields are tightly coupled to receiver bring-up and link training. A mask drift in DFE tap, CTLE, VGA, CDR, DPLL, or VCO fields can surface as marginal links, intermittent training failures, bit errors, or platform-specific display instability rather than an obvious build failure.

## Control Flow

There is no executable control flow in this header. Runtime flow is supplied by AMDGPU display code that includes this generated header together with the matching DCN 3.2.0 offset header and expands generated register-list macros into register, shift, and mask tables.

Typical runtime usage is:

1. DCN 3.2 display resource, DMUB/DMCUB, link encoder/PHY, IRQ, hardware sequencing, or memory-management code selects a hardware block and lane instance.
2. Generated register-list macros bind a register offset from `dcn_3_2_0_offset.h` with one or more shift/mask symbols from this file.
3. Register helpers such as set, update, get, write, and wait/poll helpers use the mask/shift pair to pack a field, preserve unrelated bits, decode status, or acknowledge an event.
4. Hardware latches configuration, reports status, performs calibration, changes power state, runs link training, updates counters, or clears latched signals according to PHY sequencing rules outside this header.

This file does not encode access width, reset defaults, volatility, write-one-to-clear behavior, self-clear timing, calibration delays, or inter-register ordering. Those constraints live in hardware specifications and in the display driver code that consumes these symbols.

## State And Persistence Behavior

No software state is stored by this file. The macros describe MMIO-backed hardware state whose lifetime is controlled by display hardware, link training, modesets, hotplug, power gating, suspend/resume, GPU reset, PHY reset, and firmware/hardware sequencing.

Persistent or latched configuration fields in this range include lane/TX/RX override values and enables, TX/RX power-state definitions, power-up timing registers, DCC offset overrides, CREG analog controls, CDR/DPLL/VCO calibration controls, LBERT controls, clock-align controls, FIFO controls, and RX adaptation configuration.

Volatile readback fields include TX/RX status registers, statistic counters, calibration comparison data, clock-align status, LBERT error counts, analog status outputs, VCO calibration status, CDR status, DPLL readback/status fields, adaptation status codes, ASM state/done bits, current tap/CTLE/VGA/ATT values, slicer/error levels, and VDAC offset readbacks.

Side-effecting or sequencing-sensitive fields include self-clearing adjust clocks, calibration DAC control enables, AFE update enables, termination clock controls, soft or block reset fields, adaptation reset bits, statistic stop/control fields, calibration start/control fields, LBERT control, and override-enable fields. Treating these as passive booleans can leave a lane stuck in override mode, clear a diagnostic before it is observed, pulse a control at the wrong time, or break receiver/TX analog settle sequencing.

## Dependencies And Integration Points

This chunk depends on the matching generated address definitions in:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`

The generated shift/mask values must stay synchronized with that offset header and with the authoritative DCN 3.2.0 register database. The same or similar field families also appear in generated DPCS headers, which is a useful comparison source when checking generation consistency, but this DCN header is the one included by DCN 3.2 display paths.

Direct include points visible in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`

Practical integration areas are:

- DCN 3.2 resource construction and generated register/shift/mask table setup for PHY lane instances.
- Link encoder and PHY sequencing for TX/RX power-up, reset, training, lane mode, rate changes, polarity, preset/coefficient programming, and termination.
- Receiver calibration and adaptation flows for VCO, CDR, DPLL, CTLE, DFE, VGA, ATT, slicer levels, AFE settings, VCM, and bias controls.
- Debug and validation paths that use LBERT, statistic counters, calibration comparators, analog status outputs, CREG probes, and readback status.
- Interrupt or fault-analysis paths indirectly affected by PHY state, because link failures and training instability can originate from these fields even when the IRQ macros live elsewhere.

Because the header contains only constants, missing or renamed symbols usually fail at compile time in generated table users. Incorrect masks, shifts, swapped field names, or wrong instance prefixes usually compile cleanly and appear only as hardware behavior changes.

## Risks And Edge Cases

- The chunk boundaries are artificial. The first register, `C20_PHY_CR1_LANE1_DIG_ANA_XF_RX_ANA_IQ`, is partial because `SENSE_EN` and `SENSE_SEL` shift definitions are in the previous chunk. The final register, `C20_PHY_CR1_LANE2_DIG_RX_ADPTCTL_RX_DCC_DATA_DIFF_IDAC_OFST`, is partial because its reserved shift and masks are in the next chunk.
- Generated lane/register families are highly repetitive. Lane 1 versus lane 2, TX versus RX, ASIC input versus override input, and value versus enable fields are easy to swap in generation or manual edits.
- Override registers are dangerous when value and enable fields drift apart. A wrong mask can force analog clocks, resets, data enables, equalizer controls, or calibration paths in ways that bypass normal sequencing.
- Power-state and power-up timing fields are sequencing-sensitive. Incorrect values can leave a lane powered down, held in reset, clock-gated, or enabled before analog settle time has elapsed.
- Calibration fields for DCC, VCO, CDR, DPLL, CTLE, DFE, VGA, ATT, slicer, and AFE controls may fail only under specific rates, cable conditions, monitors, or temperature/voltage corners.
- Status and counter fields are volatile. Using the wrong mask can make diagnostics appear clean while hardware is reporting errors, or can make polling loops wait on an unrelated bit.
- Some controls are self-clearing, latch-on-write, or pulse-like in practice even though this header cannot express that semantic. Register helper code must know when not to perform blind read/modify/write cycles.
- Reserved masks are present for many 16-bit PHY registers. Consumers should preserve reserved bits unless the hardware sequence explicitly requires otherwise.
- Numeric masks are 16-bit-looking `L` constants in this region, but they are consumed by generic register helpers. Scripts should not infer access width solely from mask size.
- Generated names ending in `_MASK` can be mechanically ambiguous with the suffix used by mask definitions; tooling should parse by the full `__SHIFT` and `_MASK` convention rather than by loose substring matching.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU Display Core with DCN 3.2 support enabled. Missing or malformed symbols should fail in consumers that include `dcn_3_2_0_sh_mask.h` and generated register tables.
- Mechanically compare lines 97961-100340 with a regenerated `dcn_3_2_0_sh_mask.h` from the authoritative DCN 3.2.0 register database, accounting for the partial first and final registers.
- For every complete register group in the range, verify each field has a matching `__SHIFT` and `_MASK`, masks do not overlap unexpectedly, reserved masks cover the unused bits, and repeated P-state/override/status layouts match the hardware spec.
- Compare lane 2 families against corresponding lane 0/1/3 generated layouts where the hardware spec expects symmetry; differences should be intentional and traceable.
- Exercise display link training and modesets across rates and lane counts, including hotplug, link retraining, suspend/resume, GPU reset, and runtime power-management transitions.
- Validate TX behavior through power-state transitions, DCC calibration, clock alignment, LBERT pattern generation, FIFO behavior, termination override paths, and analog TX status readback.
- Validate RX behavior through signal detect, VCO calibration, CDR/DPLL lock, LBERT error reporting, CTLE/DFE/VGA/ATT adaptation, slicer/error level readback, adaptation reset, and RX DCC offset override paths.
- Use register dumps before and after PHY bring-up, link training, rate changes, and power transitions to confirm packed writes affect only intended bits and that status decoding matches hardware observations.
- Include negative or fault-injection tests where available: force override values, hold reset/clock bits, provoke LBERT errors, and verify status/counter fields report the expected state without corrupting adjacent fields.

## Cross-Chunk Notes

The previous chunk owns the beginning of `C20_PHY_CR1_LANE1_DIG_ANA_XF_RX_ANA_IQ`. This chunk includes the remaining shifts and all masks for that register but not the first two shifts. The next chunk owns the rest of `C20_PHY_CR1_LANE2_DIG_RX_ADPTCTL_RX_DCC_DATA_DIFF_IDAC_OFST` and continues into later RX adaptive-control/SSM fields. The final merged per-file report should reconcile these boundary registers and should not treat this chunk alone as complete coverage for either boundary family.
