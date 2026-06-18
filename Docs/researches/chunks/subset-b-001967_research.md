# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 93179-95564

## Scope

This chunk is a generated AMD DCN 3.2.0 shift/mask header slice. It contains preprocessor constants only: register grouping comments, `_SHIFT` macros for field bit positions, and `_MASK` macros for register-positioned field masks. There are no C functions, structs, enums, branches, loops, allocations, locks, or direct file-backed persistence in this range.

The requested range covers 2,386 source lines, 2,173 `#define` lines, and 213 register-group comments. It starts in the middle of `C20_PHY_CR1_LANE0_DIG_ANA_XF_TX_STAT_OUT_0`, where only the tail mask definitions are visible, then covers lane0 TX analog status/control, lane0 ASIC RX override/ASIC interface fields, lane0 RX power/VCO/CDR/adaptation/statistics/IQC/analog-transfer fields, and the beginning of lane1 ASIC TX/lane interface fields. It ends inside `C20_PHY_CR1_LANE1_DIG_ASIC_TX_ASIC_IN_0`, after `CLK_RDY_MASK` and `RESET_MASK`; the remaining masks for that register are in the following chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU Display Core hardware metadata for DCN/DPCS PHY programming, not Ceph filesystem logic.

## Purpose

The purpose of this header range is to describe the bit layout of C20 PHY CR1 lane registers used by AMD display driver code for DCN 3.2.0-era hardware. Matching offset headers provide register addresses; this file provides field positions and masks used by generated register tables and register-helper macros to pack MMIO writes, decode status reads, and preserve unrelated bits during read/modify/write operations.

The major hardware surfaces represented here are:

- Lane0 TX analog transfer status and control fields for clock selection, reset, data enable, serial enable, reference generation, loopback, VCM hold, voltage boost/regulator behavior, TX equalization, DCC calibration, termination, analog test bus selection, oscillator controls, pull-leg control, and override enables.
- Lane0 RX ASIC override and ASIC input/output fields for reset, power state, rate, width, PLL selection, data enable, request/ack handshakes, detector state, signal detect, VCO controls, equalization/adaptation settings, slicer levels, CDR state, calibration status, and miscellaneous override payloads.
- Lane0 RX power, VCO calibration, loopback BERT, CDR/DPLL, adaptation, statistics, IQ calibration, analog transfer, receiver calibration, DAC, AFE, sampler, DFE, term-code, status, and analog CREG fields.
- Lane1 ASIC lane and TX interface fields for loopback mode, transceiver mode, TX clock/reset/data/request/power-state/rate/width/MPLLB controls, TX equalization cursors, DCC bypass/range/update controls, deskew controls, VREG bypass, calibration status, detect-RX results, and the start of non-override ASIC input readback.

These constants are generated data rather than executable logic, but they are still an ABI between driver code, firmware-facing register tables, and display PHY hardware. A wrong shift or mask can compile successfully while causing writes or reads to target the wrong field, with failures appearing as link training problems, PHY bring-up failures, bad equalization, missed handshakes, unstable clock recovery, power sequencing errors, or broken diagnostic readback.

## Important APIs, Types, And Macros

This range exports the standard generated AMD register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register-positioned form.
- `//<REGISTER>` comments group the following definitions by register.

There are no callable APIs or C types in this chunk. Runtime code consumes these macros indirectly through AMD display register-list and mask/shift-list infrastructure, normally paired with register offsets from `dcn_3_2_0_offset.h`.

Important definition families in this chunk are:

- `C20_PHY_CR1_LANE0_DIG_ANA_XF_TX_STAT_OUT_*`, `TX_STAT_EQ_OUT_*`, and `TX_STAT_IN_0`.
- `C20_PHY_CR1_LANE0_DIG_ANA_XF_TX_ANA_CREG00` through `CREG05`, plus `TX_ANA_CREG0_OVRD` and `TX_ANA_CREG1_OVRD`.
- `C20_PHY_CR1_LANE0_DIG_ASIC_RX_OVRD_*`, `RX_ASIC_IN_*`, `RX_ASIC_OUT_0`, `RX_CDR_VCO_ASIC_IN`, and `RX_EQ_ASIC_IN_*`.
- `C20_PHY_CR1_LANE0_DIG_RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_LBERT_*`, `RX_CDR_*`, `RX_DPLL_*`, `RX_ADPTCTL_*`, `RX_STAT_*`, and `RX_IQC_CTL_*`.
- `C20_PHY_CR1_LANE0_DIG_ANA_XF_RX_*` transfer, calibration, sampler, DFE, term-code, status, and analog CREG groups.
- `C20_PHY_CR1_LANE1_DIG_ASIC_LANE_OVRD_IN`, `TX_OVRD_IN_*`, `TX_OVRD_OUT`, `LANE_ASIC_IN`, and the beginning of `TX_ASIC_IN_0`.

## Lane0 TX Analog Status And Control

The chunk begins with tail mask definitions from `C20_PHY_CR1_LANE0_DIG_ANA_XF_TX_STAT_OUT_0`, then provides complete field definitions for the adjacent TX status and analog CREG groups.

`TX_STAT_OUT_1` exposes TX analog data rate, clock loopback enable, RX detect enable, reference selection, voltage boost enable, flyover enable, async reset, word clock enable, and reserved upper bits. `TX_STAT_EQ_OUT_0` through `TX_STAT_EQ_OUT_4` expose TX equalization readback: post cursor, pre cursor, load-clock state, pull-leg direction, and pull-leg enable fields split across 16-bit register words. `TX_STAT_IN_0` exposes input/status bits such as clock-shift acknowledgement, RX detect plus/minus result, and DCC calibration result.

`TX_ANA_CREG00` through `TX_ANA_CREG05` define lane0 TX analog control fields. They cover:

- Clock-shift override and register value, DC-mode enable, RBOOST test enable, VCM hold override/value, loopback override/value, reference generator enable, clock divider enable, data/clock/serial enable, global analog override enable, and clock-loopback override/value.
- Driver-source selection, alternative-bus override, oscillator control for VPH/VPTX/LVT/cell paths, JTAG data, analog test bus selections for ground, DCC comparator, VPTX, IBOOST, VDD, VCM, TXSM/TXSP/TXFM/TXFP, RXDET reference, bias paths, VPH half, VBOOST reference, and VBOOST path.
- Termination-code override and register bits, DCC calibration VDAC analog test bus selections, VREG VPTX/TX controls, regulator reference override, pull-down controls, VP mux selection, VREG boost/bypass/fast-start/bleeder controls, and VPTX bleed/boost behavior.
- PLL clock selection, MPLLA/MPLLB clock-enable register values, TX data-rate register value, RX detect enable override/value, VBOOST override/value, reference selection override/value, flyover override/value, async reset override/value, and word-clock override/value.

`TX_ANA_CREG0_OVRD` and `TX_ANA_CREG1_OVRD` are reserved full-word override placeholders in this range. Even though they expose only `RESERVED_15_0`, they still reserve address space and keep generated register numbering aligned with the hardware database.

## Lane0 RX ASIC Override And ASIC Interface

The `C20_PHY_CR1_LANE0_DIG_ASIC_RX_OVRD_*` groups define software override controls for the lane0 RX interface presented to the PHY logic. The early override registers cover RX reset, power state, rate, width, PLL selection, data enable, request path, signal-detect selector, termination mode, and handoff enable bits. Later override groups cover VCO and equalization/adaptation controls:

- `RX_OVRD_IN_0` through `RX_OVRD_IN_4` provide value/enable pairs for reset, pstate, rate, width, PLL selection, data enable, request, signal-detect selection, termination mode, CDR data enable, CDR phase enable, VCO div2, DFE enable, adaptive enable, calibration run, back-off calibration run, sampler selection, DFE/boost controls, VCO frequency selection, and adaptation mode.
- `RX_OVRD_SIGDET_IN` covers forced signal-detect values and override enable bits.
- `RX_OVRD_VCO_IN` covers VCO calibration range, enable, and control payloads.
- `RX_OVRD_EQ_IN_0` through `RX_OVRD_EQ_IN_4`, and extended `RX_OVRD_EQ_IN_5` through `RX_OVRD_EQ_IN_11`, cover CTLE/VGA/DFE adaptation codes, tap weights, slicer offsets, DCC calibration values, bypass controls, and related override enables.
- `RX_OVRD_OUT_0` exposes overrideable RX output handshake/status values such as RX acknowledgement, signal detect, valid, calibration status, and related enable bits.

The non-override ASIC interface registers describe hardware-observed lane input/output fields:

- `RX_ASIC_IN_0` through `RX_ASIC_IN_3` expose RX reset, pstate, rate, width, PLL selection, data enable, request, signal-detect select, termination mode, CDR data/phase enable, VCO div2, DFE enable, adaptation enable, calibration request, sampler selections, VCO frequency selection, and adaptation mode as seen by the PHY.
- `RX_CDR_VCO_ASIC_IN` carries VCO calibration range/control and enable.
- `RX_EQ_ASIC_IN_0` through `RX_EQ_ASIC_IN_2` expose equalization inputs such as boost/DFE values, tap/offset codes, slicer levels, and DCC-related controls.
- `RX_ASIC_OUT_0` exposes RX acknowledgement, signal detect, RX valid, and calibration status readback.
- `RX_OVRD_MISC` provides a generic 8-bit miscellaneous override value with an override-enable bit.

These groups distinguish normal hardware/ASIC inputs from software-forced override paths. Consumers must preserve the value/enable pairing pattern; setting an override value without the corresponding enable bit, or leaving an enable asserted after a diagnostic path, can create PHY behavior that does not match the display link state machine.

## Lane0 RX Power, Calibration, CDR, And Adaptation

The RX control portion provides the generated bit layouts for many stateful PHY sub-blocks:

- `RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, and `P2` define per-power-state values for receiver analog/DCC/clock/VCO/calibration controls, CDR/DFE/adaptation behavior, and related lane state. `RX_PWRUP_TIME_0` and `RX_PWRUP_TIME_1` define power-up timing windows. `RX_PWRCTL_RX_CTL` and `RX_PWRCTL_RX_STATUS` expose power-control knobs and readback/status.
- `RX_VCOCAL_RX_VCO_CAL_CTRL_0` through `CTRL_2`, `RX_VCO_CAL_TIME_0`, `RX_VCO_CAL_TIME_1`, and `RX_VCO_STAT_0` through `STAT_2` define VCO calibration control, timing, result, state, and status fields.
- `RX_LBERT_CTL` and `RX_LBERT_ERR` define lane loopback bit-error-rate test controls and error count/status fields.
- `RX_CDR_CDR_CTL_0` through `CDR_CTL_4`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, `RX_DPLL_FREQ_BOUND_0`, and `RX_DPLL_FREQ_BOUND_1` describe clock-data-recovery configuration/status and DPLL frequency/bounds fields.
- `RX_ADPTCTL_ADPT_CFG_0` through `ADPT_CFG_12`, `RST_ADPT_CFG`, `ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, `DFE_TAP1_STATUS` through `DFE_TAP5_STATUS`, DFE VDAC offset fields, slicer controls, DCC IDAC offset fields, `RX_FAST_FLAGS`, `SSM_SSM_CFG_0` through `SSM_CFG_4`, and `SSM_FINAL_CODE` describe adaptation sequencing, equalizer state, slicer thresholds, DFE tap state, DCC offsets, and state-machine metadata.
- `RX_STAT_*` registers define statistic load values, data masks, match controls, statistic controls, sample counts, statistic counters, calibration compare clock control, stop controls, shadow count, and extended load values.
- `RX_IQC_CTL_RESET_ADJUST`, `RX_IQC_CTL_CONFIG`, and `RX_IQC_CTL_STAT` describe IQ calibration adjustment/reset/configuration and status readback.

This region is especially sequencing-sensitive. These macros do not encode when a field may be written, whether a status field is volatile, whether a calibration bit self-clears, or how long software must wait between state changes. Driver code and hardware documentation supply those rules.

## Lane0 RX Analog Transfer And Analog CREG Fields

The `C20_PHY_CR1_LANE0_DIG_ANA_XF_RX_*` family bridges digital/ASIC-facing RX control with analog front-end controls and readbacks. It includes:

- Override output groups for RX control and power: `RX_CTL_OVRD_OUT`, `RX_PWR_OVRD_OUT_0`, and `RX_PWR_OVRD_OUT_1`.
- Signal-detect calibration groups: `RX_SIGDET_CAL_EN`, `RX_SIGDET_HF_CAL`, and `RX_SIGDET_LF_CAL`.
- VCO override output groups: `RX_VCO_OVRD_OUT_0` through `RX_VCO_OVRD_OUT_2`.
- Calibration and DAC groups: `RX_CAL_0`, `RX_CAL_1`, `RX_VDAC_RANGE_SEL`, `RX_DAC_CTRL`, `RX_ANA_RTRIM`, `RX_DAC_CTRL_OVRD`, `RX_DAC_CTRL_SEL`, and `RX_DCC_CAL_DAC_CTRL_RANGE`.
- AFE and sampler groups: `RX_AFE_OVRD_IN_0`, `RX_AFE_OVRD_IN_1`, `RX_AFE_OVRD_IN_2`, `RX_SCOPE`, `RX_SLICER_CTRL`, `RX_ANA_IQ`, IQC bypass/data override and adjust-clock registers, `RX_ANA_CAL_DAC_CTRL_EN`, `RX_ANA_LOOPBACK_CTRL`, `RX_ANA_AFE_UPDATE_EN`, DFE/bypass/phase sampler selection, and term-code override outputs.
- Status groups: `RX_STAT_OUT_0`, `RX_STAT_OUT_1`, and `RX_STAT_IN_0`, which expose analog RX state such as rate, clocking, DCC/AFE enable, VCO and calibration status, signal detect, and related results.
- `RX_ANA_CREG00` through `RX_ANA_CREG11` define analog control/test fields such as ATB measurement selections, sampler override registers, AFE rate, word clock enable, DCC/AFE enables, regulator/test selections, loopback, bias/reference paths, calibration hooks, and reserved fields.
- `RX_ANA_CREG0_OVRD` and `RX_ANA_CREG1_OVRD` are reserved full-word override placeholders.

The analog transfer names are dense and often similar. For example, sampler, DFE, bypass, phase, DCC, VDAC, and term-code fields appear in both ASIC override/status families and analog transfer families. Generated consistency is important because an apparently plausible but wrong field name can target a different hardware stage.

## Lane1 ASIC TX Beginning

At the end of the chunk, the file transitions from lane0 RX/analog registers to lane1 ASIC lane/TX registers:

- `C20_PHY_CR1_LANE1_DIG_ASIC_LANE_OVRD_IN` defines lane-level override controls for TX-to-RX serial loopback, RX-to-TX parallel loopback, transceiver mode, override enable, and lane override enable.
- `TX_OVRD_IN_0` defines value/enable pairs for TX clock-ready, reset, invert, data enable, request, low-power disable, and pstate.
- `TX_OVRD_IN_1` defines TX rate, width, align-wide-transfer enable, MPLLB selection, detect-RX request, flyover enable, and the corresponding override enables.
- `TX_OVRD_IN_2` defines NYQUIST data, TX disable, beacon enable, IBOOST level, VBOOST enable, and TX override enable.
- `TX_OVRD_IN_3` and `TX_OVRD_IN_4` define TX post/main/pre cursor fields, TX EQ override enable, DCC bypass, bypass-EQ-calc, and their override enables.
- `TX_OVRD_IN_5` defines TX DCC control range, DCC range override enable, async FIFO, lane-to-lane deskew, driver enable for KR, TX clock deskew, VREG TX bypass, DCC update enable, and corresponding override enables.
- `TX_OVRD_OUT` exposes TX acknowledgement, detect-RX result, calibration status, and override enables for those output/status values.
- `LANE_ASIC_IN` exposes non-override lane loopback and transceiver mode inputs.
- `TX_ASIC_IN_0` starts the non-override TX ASIC input layout with clock-ready, reset, invert, data enable, request, low-power disable, pstate, rate, width, align-wide-transfer enable, and MPLLB select shifts. Only the first two masks for this register are in this chunk; the rest belong to the next chunk.

The lane1 transition is a chunk boundary artifact. The final merged file-level report should treat lane1 TX as a larger repeated lane family spanning adjacent chunks.

## Control Flow

There is no executable control flow in this header. Runtime flow is supplied by AMDGPU display code that includes this generated mask file, includes the matching generated offset file, and then expands register helper macros or generated register-table macros.

Typical runtime usage is:

1. DCN 3.2 display, DMUB, GPIO, IRQ, clock, or resource code selects a hardware block/lane instance and a generated register offset.
2. Generated register-list macros or helper tables bind the register offset to one or more `_SHIFT` and `_MASK` symbols from this file.
3. Register helpers perform packed writes, read/modify/write updates, status reads, polls, or acknowledgement writes using those shift/mask pairs.
4. PHY hardware latches configuration, applies override paths, changes clock/power/calibration state, runs adaptation or CDR/VCO logic, reports status, or participates in link training and diagnostic tests.

This file does not encode reset values, valid field enumerations, write-one-to-clear behavior, volatile semantics, required delays, polling timeouts, or dependencies between power, clock, reset, calibration, adaptation, and equalization fields.

## State And Persistence Behavior

No software state is stored by this file. It describes MMIO-backed hardware state whose lifetime is governed by GPU reset, display link initialization, link training, modesets, power management, suspend/resume, hotplug handling, PHY calibration, and diagnostic routines.

Persistent or latched hardware configuration fields in this chunk include TX/RX override enables and values, lane transceiver and loopback modes, TX equalization cursors, TX/RX power-state values, VCO calibration controls and timing, CDR/DPLL configuration, adaptation configuration, statistics controls, IQC configuration, analog CREG controls, calibration DAC selections, sampler selections, and lane1 TX override controls.

Volatile readback/status fields include TX status outputs, RX acknowledgement, signal detect, RX valid, calibration status, VCO status, CDR status, adaptation/equalizer status, DFE tap status, statistic counters, IQC status, RX analog status outputs, TX detect-RX result, TX acknowledgement, and calibration status.

Side-effecting or sequencing-sensitive fields include reset controls, override enables, calibration run/enable controls, DCC update controls, statistic load/stop controls, loopback/BERT controls, clock/data enable controls, pstate controls, and status/ack-style handshakes. Treating these as ordinary static booleans can leave a PHY lane forced into a test state, hide real ASIC inputs behind stale overrides, or break the software/hardware handshake expected by link training.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.2.0 offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`

The offset and mask headers must be generated from the same hardware register database. This chunk also has structurally matching C20 PHY content in the DPCS generated header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h`

Local include searches show direct DCN 3.2.0 consumers in:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`

Practical integration points include:

- DCN 3.2 resource construction, where generated register, shift, and mask tables are assembled for hardware blocks.
- Display link and PHY bring-up paths that program lane power state, TX/RX enables, rate/width, PLL selection, equalization, adaptation, DCC, and calibration fields.
- Clock and power-management paths that sequence PHY clock, reset, power state, and status polling.
- DMUB and display firmware interaction paths that rely on generated register metadata for low-level hardware programming.
- Diagnostic and validation paths that inspect BERT, statistic counters, signal detect, calibration status, VCO/CDR/adaptation state, and analog readback fields.

Because this file contains only constants, missing or renamed symbols are likely to fail at build time. Incorrect numeric values, swapped lane prefixes, or wrong masks usually compile cleanly and only appear as hardware misbehavior.

## Risks And Edge Cases

- The chunk begins and ends inside register definitions. `TX_STAT_OUT_0` is partial at the beginning, and `TX_ASIC_IN_0` is partial at the end. Adjacent chunks are required for complete register-family analysis.
- Generated bitfield drift from the authoritative DCN 3.2.0 register database is the main risk. A wrong mask or shift can silently corrupt PHY MMIO programming.
- Lane and block prefixes are highly repetitive. Confusing `LANE0` with `LANE1`, `TX` with `RX`, `ASIC` with `ANA_XF`, or override registers with ASIC input registers may compile but control the wrong path.
- Override registers use value/enable pairs. Setting a value without its enable bit has no effect, while leaving an enable bit asserted can mask normal hardware inputs and break link training or recovery.
- RX adaptation, CDR, VCO, DFE, CTLE, VGA, DCC, sampler, and slicer fields are calibration-sensitive. Wrong definitions may cause unstable links, poor eye margin, intermittent hotplug failures, or data corruption under marginal signal conditions.
- Power-state and reset fields are sequencing-sensitive. Incorrect masks can leave lanes held in reset, powered down, clock-disabled, or reporting stale status across suspend/resume and runtime power transitions.
- Status/counter fields are volatile. Polling or decoding them with stale masks can create false pass/fail results in calibration, BERT, CDR lock, signal-detect, or statistic tests.
- Full-word reserved registers such as `*_CREG0_OVRD`, `*_CREG1_OVRD`, and `RX_ANA_CREG11` should not be removed or normalized away. They preserve generated address/register layout even when no named hardware fields are exposed.
- Names include many near-duplicates and abbreviations such as `OVRD`, `ASIC_IN`, `STAT_OUT`, `STAT_IN`, `VDAC`, `IDAC`, `DCC`, `DFE`, `CTLE`, `VGA`, and `SSM`. Text-based refactors or script generation must not infer semantics from partial name matches alone.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU Display Core with DCN 3.2.0 support enabled. Missing or malformed macros should fail in DCN 3.2 resource, DMUB, GPIO, IRQ, clock, or link/PHY code that expands generated tables.
- Mechanically compare lines 93179-95564 against a regenerated `dcn_3_2_0_sh_mask.h` or the authoritative DCN 3.2.0 register database, accounting for the partial first and last registers.
- Run generated-header consistency checks for complete registers in this range: every non-reserved field should have matching `_SHIFT` and `_MASK`, masks should correspond to the stated shift/width, fields should not overlap unexpectedly, and reserved masks should cover the remaining bits.
- Compare repeated C20 PHY lane layouts against the corresponding generated `dpcs_4_2_3_sh_mask.h` content where the hardware database expects parity.
- Exercise link training and modeset paths across supported rates/widths, checking TX data/clock/serial enables, TX EQ cursor programming, RX rate/width, PLL selection, request/ack handshakes, and detect-RX/signal-detect readback.
- Validate suspend/resume and runtime power transitions with register dumps around RX/TX pstate, reset, clock/data enable, VCO calibration, and status fields.
- Run PHY calibration and adaptation diagnostics that observe VCO status, CDR lock/status, DFE tap status, CTLE/VGA status, DCC offsets, slicer levels, and RX fast flags.
- Exercise BERT/statistics paths where available, confirming sample counts, match controls, statistic counters, stop/load behavior, and error counters decode correctly.
- Test override-only paths under controlled diagnostics, verifying that enabling and then clearing override bits restores normal ASIC input behavior.
- Use hardware register dumps before and after link training, hotplug, power transitions, and diagnostic tests to confirm packed writes affect only intended bits and status decoding matches hardware observations.

## Cross-Chunk Notes

The previous chunk owns the beginning of `C20_PHY_CR1_LANE0_DIG_ANA_XF_TX_STAT_OUT_0`; this chunk only contains its tail masks. The next chunk owns the remaining masks for `C20_PHY_CR1_LANE1_DIG_ASIC_TX_ASIC_IN_0` and later lane1 TX fields. The final merged report for `dcn_3_2_0_sh_mask.h` should reconcile those boundaries and should treat this chunk as one part of a much larger generated DCN/DPCS PHY register description.
