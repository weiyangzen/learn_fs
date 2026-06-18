# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 149061-151480

## Scope

This chunk is a generated AMD DCN 3.2.0 register-field shift/mask header slice. It contains C preprocessor constants only: `_SHIFT` macros for hardware bit positions, `_MASK` macros for register-positioned field masks, and `//<REGISTER>` grouping comments. There are no C functions, structs, enums, branches, loops, allocations, locks, or file-backed persistence in this range.

The requested range covers 2,420 source lines, 2,145 shift/mask `#define` entries, and 275 `C20_PHY_CR2_*` register groups. It begins immediately after `C20_PHY_CR2_RAWLANEAON3_DIG_RX_CAL_IQ_MAX` and continues through the mask definitions for `C20_PHY_CR2_LANEX_DIG_RX_CDR_CDR_CTL_4`. The next chunk is required for the subsequent `RX_CDR_STAT`, `RX_DPLL_FREQ`, DPLL bound, and adaptation-control fields.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display-controller hardware metadata, not Ceph filesystem code.

## Purpose

The purpose of this header range is to expose the bit layout for DCN 3.2.0 `C20_PHY_CR2` DisplayPort/PHY control registers. Companion generated offset headers provide register addresses; this file provides the bit positions and masks that AMDGPU Display Core register-helper macros use to encode MMIO writes and decode MMIO reads.

This chunk is centered on high-speed PHY lane bring-up, calibration, adaptation, override, power sequencing, transmitter analog control, receiver analog control, VCO calibration, built-in link/error test control, and clock-data-recovery tuning. These definitions are hardware ABI data: a wrong mask can still compile but make software program the wrong PHY bit, causing link-training instability, wrong lane polarity or pstate, bad TX equalization, broken RX adaptation, failed VCO/CDR calibration, unreliable signal detection, bad loopback/test results, or display blanking on affected DCN32 hardware.

## Important APIs, Types, And Macros

This range exports the standard generated AMD register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask already shifted into register position.
- `//<REGISTER>` comments group the definitions belonging to one hardware register.

There are no callable APIs or C types in this chunk. The important definition families are the register namespaces below.

## RAWLANEAON3 RX Calibration And Adaptation

The first half of the chunk defines always-on raw lane RX calibration/adaptation fields under `C20_PHY_CR2_RAWLANEAON3_DIG_RX_*`.

The RX IQ/DCC calibration bank section includes:

- `CAL_IQ_MIN`, `CAL_IQ_RESET`, and `CAL_IQ_ADJUST`, which split half-rate/full-rate or bypass/data values into low and high byte fields.
- `DCC_CTRL_RANGE_BANK_0` through `_BANK_3`, with full-rate and half-rate control-range fields plus reserved upper bits.
- Per-bank DCC data, bypass, and phase results for full and half rates, each carrying common-mode and differential values.
- `IQ_CAL_BANK_0` through `_BANK_3`, with half-rate/full-rate IQ calibration values.
- `CAL_DONE_BANK_0` through `_BANK_3`, with separate full-rate and half-rate done bits.
- `CAL_BANK_SEL`, live DCC code readback registers, `IQ_CAL`, and aggregate `CAL_DONE` fields used to select and observe calibration banks.

The adaptation result section defines banked RX equalization state:

- `ADPT_ATT_BANK_0/1`, `ADPT_VGA_BANK_0/1`, and `ADPT_CTLE_BANK_0/1` for attenuation, VGA, CTLE boost/pole/zero, and peak-detect controls.
- `ADPT_DFE_TAP1_BANK_0/1` through `ADPT_DFE_TAP5_BANK_0/1` for decision-feedback equalizer tap values.
- `DFE_DEH/DEL/DOH/DOL/EEH/EEL/EOH/EOL_TAP1_OFST_BANK_0/1` for tap1 offset components across data/error and even/odd/high/low sample paths.
- `DFE_TAP1_OFST_VLD_BANK_0/1` for validity bits covering the offset lanes.
- `ADPT_IQ_BANK_0/1`, `ADPT_REF_ERR_BANK_0/1`, and `ADAPT_DONE_BANK_0/1` for IQ, reference-error, and done-status fields.

The non-banked adaptation-control area includes `IQ_CTL_0`, `IQ_CTL_1`, `ADPT_IQ_LIMIT`, `ADPT_ERR_SLC_MODE`, TX equalization direction/polarity control, TX pre-divider and threshold registers, and `ADPT_CTL_0` through `ADPT_CTL_28`. These fields configure DFE enablement, adaptation step behavior, slew/boost thresholds, floop and scalar controls, calibration mode, delay/settling counters, adaptation load/save behavior, and related knobs. Their bit layouts are consumed by PHY programming tables and sequencing code rather than by functions in this header.

## RAWLANEAON3 RX Override, Signal, And Status

The end of the RAWLANEAON3 section provides RX observation and override fields:

- `IQ_MARGIN_RANGE` defines margin range fields.
- `CDR_DETECTOR_CTL` and `CDR_RECOVERY_TIME` provide detector timeout and recovery timing fields.
- `OVRD_IN_0` includes data-enable, RX request, and low-power-detect input override values and enable bits.
- `SIGDET_EN_MASK_CTL` and `SIGDET_FILT_CTL` expose signal-detect masking and filter controls.
- `OVRD_OUT_0` and `PMA_OVRD_OUT_0` carry reset, data-rate, pstate, DFE, CDR enable, signal-detect, and PLL/CDR/VCO related override outputs.
- `IN_0` and `OUT_0` expose live input/output handshake/status bits such as data enable, request, low-power detect, acknowledge, signal detect, and disable indication.

These definitions are important for board bring-up, lane debug, link-training diagnostics, and any code path that temporarily overrides the normal PHY state machine.

## LANEX ASIC TX Interface And TX Power Control

The chunk then moves to per-lane `LANEX` digital ASIC/TX interface fields:

- `ASIC_LANE_OVRD_IN` exposes lane-level power-state override value/enable fields.
- `ASIC_TX_OVRD_IN_0` through `_5` provide override value and override-enable pairs for reset, data rate, ref select, MPLL selection, tx request, disable, beacon, detect-RX request, iboost, vboost, main/pre/post cursor, DCC control range, flyover, polarity, and miscellaneous TX control.
- `ASIC_TX_OVRD_OUT`, `ASIC_LANE_ASIC_IN`, `ASIC_TX_ASIC_IN_0` through `_3`, `ASIC_TX_ASIC_OUT`, and `ASIC_TX_OVRD_MISC` define the non-overridden live interface between digital control logic and TX analog PHY.

`TX_PWRCTL` definitions model the lane transmitter power-state sequencer:

- `TX_PSTATE_P0`, `TX_PSTATE_P0S`, `TX_PSTATE_P1`, and `TX_PSTATE_P2` repeat the same per-state controls for refgen, VCM hold, analog clock, analog reset, serializer, digital clock, data enable, RX-detect allowance, vboost allowance, analog DCC, voltage-regulator bleed, and word clock.
- `TX_PWRUP_TIME_0` through `_5` define refgen, clock, VCM, vboost, reset, RX-detect, VREG fast-start, DCC, data-enable, serializer, and fast-path timing fields.
- `TX_CTL` includes control bits for power request gating, forced serializer behavior, low-speed override handling, fast pstate transitions, DCC behavior, and comparator overrides.
- `TX_STATUS` exposes TX request, power-state-machine state, previous/current TX pstate, RX-detect request, vboost, and power-state-change interrupt indication.

These fields influence display link electrical behavior and sequencing latency. The repeated pstate layouts must remain aligned because higher-level code can select per-state register instances while applying the same field semantics.

## LANEX TX DCC, Statistics, LBERT, FIFO, And Analog Transfer

The TX-side calibration/debug section defines:

- `TX_DCC_CTL_TX_DCC_DIFF_IDAC_OFST`, `TX_DCC_CTL_TX_DCC_CM_IDAC_OFST`, and `TX_DCC_CTL_STAT` for TX duty-cycle-correction offsets, control-range selection, ready indication, and current calibration state.
- `TX_STAT_LD_VAL_1`, `TX_STAT_STAT_CTL0`, `TX_STAT_SMPL_CNT1`, `TX_STAT_STAT_CNT_0`, `TX_STAT_CAL_COMP_CLK_CTL`, and `TX_STAT_STAT_STOP` for TX statistic/load counters and calibration comparator clock control.
- `TX_CLK_ALIGN_TX_CTL_0`, `TX_CLK_ALIGN_TX_CTL_1`, and `TX_CLK_ALIGN_CLK_ALIGN_STATUS` for TX clock alignment start/reset/selection and completion/status bits.
- `TX_LBERT_CTL` and `TX_LBERT_PAT1_0` through `_3` for link built-in error-rate test mode, sync, pattern selection, PRBS selection, and user pattern words.
- `TX_LVL_CALC_STAT` for TX level-calculation status.
- `TX_FIFO_CTL` for FIFO read pointer start and bypass control.

The `ANA_XF_TX_*` definitions describe the digital-to-analog transfer/override interface:

- `OVRD_OUT_0` through `_3`, termination code override registers, and DCC enable/config/calibration controls expose analog TX clock, reset, serializer, data, refgen, VCM, VREG, data-rate, loopback, RX detect, ref select, vboost, word-clock, misc, termination, and DCC calibration values.
- `STAT_EQ_OVRD_0` through `_4`, `STAT_OUT_0/1`, `STAT_EQ_OUT_0` through `_4`, and `STAT_IN_0` expose TX analog equalization override values, status readback, cursor/post/pre/deemphasis behavior, load-clock controls, status mode, reset, and ack/detect/calibration state.
- `ANA_CREG00` through `ANA_CREG05` and `ANA_CREG0_OVRD`/`ANA_CREG1_OVRD` define analog configuration-register fields for clock enables, DCC, reset, high-Z, IB/VB controls, comparator and IDAC selections, VCM/VREG behavior, DCC calibration, termination, spare bits, and override enables.

These definitions are usually exercised by link-training, PHY tune tables, manufacturing diagnostics, and low-level debug paths.

## LANEX ASIC RX Interface, RX Power, VCO, LBERT, And CDR

The RX-side LANEX section defines the digital ASIC/RX control surface:

- `ASIC_RX_OVRD_IN_0` through `_4` provide override value/enable fields for RX reset, invert, data enable, request, low-power detect, pstate, DFE bypass, data rate, CDR enable, CDR select, PI offset, VGA, peak, DFE tap1-5, and IQ/VCO controls.
- `ASIC_RX_OVRD_SIGDET_IN`, `ASIC_RX_OVRD_VCO_IN`, and `ASIC_RX_OVRD_EQ_IN_0` through `_11` cover signal-detect, VCO calibration, equalization control, CTLE, DFE, tap offsets, DCC, IQ, reference error, and adaptation done override inputs.
- `ASIC_RX_OVRD_OUT_0`, `ASIC_RX_ASIC_IN_0` through `_3`, `ASIC_RX_CDR_VCO_ASIC_IN`, `ASIC_RX_EQ_ASIC_IN_0` through `_2`, `ASIC_RX_ASIC_OUT_0`, and `ASIC_RX_OVRD_MISC` expose live non-overridden RX interface fields and status.

`RX_PWRCTL` mirrors the transmitter pstate structure for the receiver:

- `RX_PSTATE_P0`, `RX_PSTATE_P0S`, `RX_PSTATE_P1`, and `RX_PSTATE_P2` define per-state CDR enable, input buffer enable, VCO enable, VCO counter power-down/enable, analog clock, PI/DR/DAC/CDR/VGA/DFE enable, PBB power-down, CTLE/VGA/DFE clock gating, and DCC enable fields.
- `RX_PWRUP_TIME_0` and `RX_PWRUP_TIME_1` define VCO, input-buffer, CDR, deserializer, and RX clock-DCC timing with fast-path enable fields.
- `RX_CTL` controls RX clock, digital clock, forced DAC write, DCC/EQ DAC writes, IQ calibration bypass, and calibration DAC override gating.
- `RX_STATUS` exposes rate interrupt and RX power-state-machine state.

The VCO calibration fields include `RX_VCO_CAL_CTRL_0` through `_2`, `RX_VCO_CAL_TIME_0/1`, and `RX_VCO_STAT_0` through `_2`. They control internal gain calibration count behavior, VCO override/reset/continuous calibration, DPLL calibration update gain, frequency-tune start/step/skip fields, VCO update/counter/startup timings, and status readback for analog CDR frequency tune, VCO counter state, startup/VCO enables, FSM state, calibration done, final counter value, too-fast indication, correctness, and direction.

The RX test and clock recovery tail includes `RX_LBERT_CTL`, `RX_LBERT_ERR`, and `RX_CDR_CDR_CTL_0` through `_4`. These fields configure RX LBERT mode/sync/BER counter selection and error count/overflow, then define CDR phase detector enables/edge/polarity, SSC on/off counters, phase/frequency update gains, DPLL-gain override, and spread-spectrum on/off PHUG/FRUG settings. The chunk ends at `RX_CDR_CDR_CTL_4` mask definitions.

## Control Flow

There is no runtime control flow in this header. Control flow is indirect and arises when DCN32 display, link, DMUB, clock, GPIO, IRQ, and memory-controller code includes this generated header and passes its symbols into AMD register-helper macros. Those helpers typically combine address macros from the matching offset header with `_SHIFT` and `_MASK` definitions from this file to perform read/modify/write register programming or status extraction.

For this chunk, the effective hardware flow represented by the fields is:

1. Select or override lane power state, clock/reset/data enable, pstate, and request bits.
2. Program TX/RX pstate timing and analog enable sequencing.
3. Run or bypass calibration/adaptation FSMs for RX IQ, DCC, DFE/CTLE/VGA, TX DCC, VCO, and CDR.
4. Read banked done/status values, live ASIC in/out values, LBERT counters, and calibration status.
5. Optionally apply debug/manufacturing overrides through paired value and override-enable fields.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. They do not allocate memory, retain kernel state, or persist data to disk.

The hardware fields they describe are persistent only as MMIO-visible PHY register state while the GPU/display block is powered. Many fields are state-machine controls or readbacks whose behavior depends on PHY power, display link state, and firmware/display-driver sequencing. The chunk contains many paired override-value and override-enable fields; leaving an override-enable bit set can make hardware ignore normal state-machine inputs until cleared. Banked calibration fields preserve hardware calibration results across the relevant PHY state until reset, recalibration, pstate transition, or power gating invalidates them.

## Dependencies

This header depends on the generated AMDGPU register model:

- Matching DCN 3.2.0 offset headers provide the register addresses for these field definitions.
- AMD Display Core register helpers expect `_SHIFT` and `_MASK` naming to be mechanically consistent.
- The `C20_PHY_CR2_*` namespace must match the register names produced by AMD hardware description tooling.
- Reserved fields are still defined with masks, but production code should avoid intentionally programming reserved bits unless hardware documentation or generated tables require a value.

The file is included directly by DCN32-specific AMDGPU code such as `display/dmub/src/dmub_dcn32.c`, `amdgpu/gmc_v11_0.c`, `display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/gpio/dcn32/hw_translate_dcn32.c`, `display/dc/gpio/dcn32/hw_factory_dcn32.c`, `display/dc/resource/dcn32/dcn32_resource.c`, and `display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`. These particular PHY symbols are mostly referenced through generated include tables and macro expansion rather than frequent direct string references in handwritten C.

## Integration Points

This chunk integrates with:

- DCN32 PHY/link training code that configures TX equalization, RX adaptation, lane polarity, data-rate selection, and pstate behavior.
- Display Core resource and clock-manager code that coordinates lane power, clocks, resets, and low-power states.
- DMUB/DMCUB-assisted display sequencing where firmware or driver code may program generated register tables.
- GPIO/HPD/AUX/link-detection flows that rely on working signal detect, RX request/ack, RX-detect, and lane power transitions.
- Diagnostic and manufacturing paths using LBERT, loopback, statistic counters, DCC/VCO/CDR status, and analog override/readback registers.

Because this is generated hardware metadata, the main integration contract is exact symbol spelling and exact numeric field layout. A rename, mask typo, or field-width change breaks consumers at compile time if the symbol disappears, but can create runtime-only link failures if the symbol remains valid but encodes the wrong bits.

## Risks

- Bit-layout drift from the hardware specification can silently corrupt MMIO programming. Most failures would appear as display link instability, training failures, clock-recovery failures, or intermittent blank displays rather than compiler errors.
- Many registers contain paired `VAL`/`OVRD_EN` or value/override-enable fields. Mixing these fields can force analog PHY behavior unintentionally.
- Banked calibration fields are repetitive across banks 0-3 or 0-1; copy-generation errors are plausible and can make code read the wrong calibration bank.
- TX and RX pstate definitions repeat near-identical fields across P0/P0S/P1/P2. A single mismatched shift in one pstate can affect only certain power transitions, making failures hard to reproduce.
- Reserved-bit masks are present. Helper code must preserve or intentionally set reserved bits according to the ASIC programming guide; blind writes risk undefined hardware behavior.
- The range starts after the complete `CAL_IQ_MAX` definition and ends before later RX CDR/DPLL/adaptation registers. File-level reasoning needs neighboring chunks for complete CR2 PHY coverage.

## Test Signals

Useful validation signals for changes touching this chunk are:

- Build coverage for AMDGPU DCN32 users, ensuring generated symbols still compile through DMUB, IRQ, GPIO, resource, clock-manager, and GMC include paths.
- Static comparison against the authoritative generated register database or upstream AMDGPU `dcn_3_2_0_sh_mask.h` for the exact lines.
- Link-training and modeset tests on DCN 3.2 hardware, especially DisplayPort high-rate modes, multi-lane configurations, pstate transitions, suspend/resume, hotplug, and low-power entry/exit.
- Hardware register readback traces confirming TX/RX pstate, DCC/IQ/DFE/VCO/CDR calibration done bits, signal-detect status, and RX/TX ASIC in/out fields match expected sequencing.
- Diagnostic LBERT or loopback tests for TX/RX pattern generation/checking and error counters.
- Regression tests around display blanking, HPD reconnect, fast link training, RX-detect behavior, and clock recovery after power transitions.
