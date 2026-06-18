# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 64393-66750

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for display PHY/controller registers. It contains no executable C logic; its public surface is a set of preprocessor constants that encode bit positions (`__SHIFT`) and masks (`_MASK`) for individual fields in DPCS hardware registers.

The requested range contains 2,146 `#define` entries over 2,358 source lines. It starts in the middle of `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN`, with the register's shift definitions immediately before the chunk and its masks at the top of this range. It then covers CR3 supervisor digital and analog PLL/bandgap/RTUNE controls, CR3 lane 0 ASIC/TX/RX power, statistics, analog TX and DCC fields, and the beginning of CR3 lane 1 ASIC override/input fields. It ends at `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2`, with `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_OUT` beginning just after the requested range.

Although this file is under a local `ceph-client` source mirror, the content is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the DPCS register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, compose, or update that field.

The main register-field families in this chunk are:

- CR3 supervisor override inputs and outputs: `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, and `LVL_OVRD_IN` describe prescaler overrides, RTUNE request/ACK overrides, TX calibration code override, reference alternate-clock low-power selection, MPLLA/MPLLB and bandgap state overrides, RX VREF controls, TX Vboost level, and supervisor RX VCO VREF selection.
- CR3 supervisor MPLLA/MPLLB ASIC inputs: `MPLLA_ASIC_IN_0-6` and `MPLLB_ASIC_IN_0-6` provide enable, div5 clock, TX clock divider, V2I, standby, VCO frequency, calibration force, fractional-N enable, multipliers, spread-spectrum enable/up-spread/peak/step-size, PMIX, word-div2, config-update, and clock-sync fields for both common PLL banks.
- Divided and HDMI clock inputs: `MPLLA_DIV_CLK_ASIC_IN`, `MPLLA_HDMI_CLK_ASIC_IN`, `MPLLB_DIV_CLK_ASIC_IN`, and `MPLLB_HDMI_CLK_ASIC_IN` describe divided-clock enable/multiplier and HDMI pixel/clock divider fields.
- Common supervisor digital/level/bandgap and charge-pump controls: `SUP_DIG_ASIC_IN`, `LVL_ASIC_IN`, `BANDGAP_ASIC_IN`, `MPLLA_CP_ASIC_IN`, `MPLLA_CP_GS_ASIC_IN`, `MPLLB_CP_ASIC_IN`, and `MPLLB_CP_GS_ASIC_IN` cover VREF, TX Vboost, RX VCO VREF, bandgap enables, RTUNE calibration/current modes, isolated bandgap/reference controls, and PLL charge-pump proportional/integral settings.
- Supervisor analog controls: `SUP_ANA_PRESCALER_CTRL`, `RTUNE_CTRL`, `BG1/BG2/BG3`, `SWITCH_PWR_MEAS`, and paired `SUP_ANA_MPLLA_*`/`SUP_ANA_MPLLB_*` registers cover prescaler output clock enables, RTUNE range/mode/enable, bandgap voltage/current/offset selections, reference-clock selection, analog test bus selectors, PLL bias/current/CTUNE/loop-filter/lock/window/reserved fields, and PLL analog override surfaces.
- MPLL power, timing, calibration, and SSC controls: paired `SUP_DIG_MPLLA_MPLL_PWR_CTL_*` and `SUP_DIG_MPLLB_MPLL_PWR_CTL_*` registers define MPLL power/clock-calibration requests, lock and power-good status, DAC range, lock/sleep/reset/stable timers, calibration thresholds/timers, analog DAC readback, and SSC generator spread type.
- Supervisor clock/reset and RTUNE state: `CLK_RST_BG_PWRUP_TIME_*`, `CLK_RST_REF_PWRUP_TIME_0`, `CLK_RST_REF_VPHUD`, `RTUNE_CONFIG`, `RTUNE_STAT`, `RTUNE_*_SET_VAL`, `RTUNE_*_STAT`, `RTUNE_CONFIG_CNT*`, and `RTUNE_TX_CAL_CODE` encode bandgap/reference power-up timers, RTUNE request/ack/state/status, RX/TX up/down set values and measured status, counter thresholds, and TX calibration code.
- Digital-to-analog supervisor readback and override outputs: `ANA_MPLLA_OVRD_OUT_*`, `ANA_MPLLB_OVRD_OUT_*`, `ANA_RTUNE_OVRD_OUT`, `ANA_STAT`, `ANA_BG_OVRD_OUT`, and `ANA_MPLLA/MPLLB_PMIX_OVRD_OUT` expose PLL override outputs, RTUNE override outputs, PLL lock/status readbacks, bandgap override outputs, and PMIX override values.
- CR3 lane 0 ASIC lane/TX/RX interface fields: `LANE0_DIG_ASIC_*` includes lane loopback, TX/RX override inputs and outputs, reset, invert, data enable, request/ACK, low-power detect, pstate, rate, width, MPLLB select, receive-detect request/result, disable, beacon, main/pre/post cursor, async data/drive, Vreg driver bypass, RX adaptation/equalization values, RX ref/VCO load values, CDR/align/clock-shift, termination, and TX/RX ASIC input/output fields.
- CR3 lane 0 TX power and DCC controls: `LANE0_DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`, `TX_PWRUP_TIME_0-5`, and `DCC_*` define per-power-state analog refgen, VCM hold, clock, word clock, reset, serial, digital clock, data enable, receive-detect, Vboost, DCC compensation, staged power-up timing, fast RX detect controls, and DCC CR/DAC address/data/control/range/select/ACK fields.
- CR3 lane 0 RX statistics and diagnostics: `LANE0_DIG_RX_STAT_*` describes RX load values, data masks, match controls, statistic count controls, sample count, statistic counters, calibration comparison clock controls, valid-loss controls, and statistic stop/done bits.
- CR3 lane 0 analog TX and DCC surfaces: `LANE0_DIG_ANA_TX_*` and `LANE0_ANA_TX_*` provide digital-to-analog override outputs, termination-code overrides, TX EQ override banks, DCC DAC override banks, analog status, measurement overrides, power overrides, alternate bus and ATB selectors, DCC DAC/control programming, termination-code programming/update/reset, clock override, TX miscellaneous controls, and reserved analog TX fields.
- CR3 lane 1 ASIC fields at the end of the chunk: `LANE1_DIG_ASIC_LANE_OVRD_IN`, `TX_OVRD_IN_0-4`, `TX_OVRD_OUT`, `RX_OVRD_IN_0-5`, `RX_OVRD_EQ_IN_*`, `RX_OVRD_OUT_0`, `LANE_ASIC_IN`, and `TX_ASIC_IN_0-2` mirror the lane-level loopback, TX/RX override, pstate/rate/width, request/ACK, receive-detect, async, equalization, termination, and TX cursor controls seen for lane 0. The following lane 1 TX output and RX ASIC input groups are outside this chunk.

Most values are 16-bit-style masks ending in `L`, matching the DPCS indirect-register field width used by these supervisor and lane blocks.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN/DPCS display code includes the matching DPCS 4.2.0 offset header and this shift/mask header.
2. Register-list and shift/mask-list macros token-paste DPCS register and field names into tables for the ASIC generation that owns this register block.
3. Runtime AMD display code uses register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` with those offset, shift, and mask tables.
4. Hardware sequencing code outside this generated header performs the actual ordering for PLL programming, bandgap/reference startup, RTUNE, lane power-up/down, TX/RX handshakes, receive detect, RX adaptation, DCC calibration, diagnostics, and debug overrides.

The macros in this range describe bit layout only. They do not encode access type, reset value, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, latching, clock-domain crossings, or required sequencing.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 supervisor and lane registers:

- Common supervisor state: prescaler/DCO/reference-clock selection, alternate reference low-power selection, RTUNE request/ACK/status and set values, TX calibration code, RX VREF, TX Vboost, supervisor RX VCO VREF, bandgap state, reference power-up timing, and always-on tuning/status fields.
- PLL state: MPLLA/MPLLB enables, dividers, VCO frequency, standby, calibration force, fractional-N, multiplier, SSC peak/step-size/spread type, PMIX, word-div2, charge-pump proportional/integral values, DAC ranges/readbacks, power-good, lock, sleep, reset, stable timers, and analog override/readback fields.
- Lane 0 TX state: request/ACK, pstate, rate, width, MPLLB select, reset, invert, data enable, low-power detect, disable, receive-detect request/result, beacon, async drive/data, pre/main/post cursor values, Vreg bypass, per-pstate power enables, staged power-up timers, DCC compensation, DCC DAC programming, analog TX termination/equalization/clock/refgen/serial controls, and analog test bus selections.
- Lane 0 RX state: request/ACK, data enable, pstate, rate, width, low-power detect, inversion, reset, CDR tracking, CDR SSC, align, clock shift, termination mode, RX ref/VCO load values, adaptation AFE/DFE controls, equalization override values, async/squelch readbacks, and statistic match/mask/count/calibration controls.
- Lane 1 partial state: lane loopback, TX/RX override and ASIC input fields through `TX_ASIC_IN_2`, including request/data-enable/pstate/rate/width, reset/invert/disable, receive-detect, beacon, async, termination, adaptation, equalization, and TX pre/post cursor values.
- Diagnostic and manufacturing state: analog test bus fields, reserved analog hooks, RX statistic counters, DCC CR/DAC controls, PLL analog override outputs, bandgap and RTUNE override outputs, and lane loopback controls.

Persistence is hardware-defined. Configuration fields generally remain until modeset or link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, ACK, statistic, calibration, and diagnostic fields may be sampled, latched, read-only, write-one-to-clear, self-clearing, or valid only while the relevant supervisor, PLL, or lane clock/power domain is active. This generated header does not describe those semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and companion offset definitions:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching `ixDPCSSYS_*` offsets for the fields described by this shift/mask header.
- AMD display resource and hardware-sequencing code includes generated offset and shift/mask headers to initialize register, shift, and mask tables for the relevant DCN/DPCS generation.
- Link encoder, PHY, clock-source, AUX/link-training, power-management, and diagnostics code consume those tables indirectly when programming common PLLs, reference clocks, lane power, DisplayPort/HDMI link behavior, RX adaptation, DCC, RTUNE, and analog debug paths.
- Firmware and hardware state machines interact with the same registers, especially for MPLL lock/power state, bandgap/reference startup, RTUNE, DCC calibration, RX adaptation, receive-detect, and lane request/ACK handshakes.

Behaviorally, this chunk sits below the user-facing display stack. It provides the bit definitions used when the driver brings up CR3 common resources, selects and programs MPLLA/MPLLB clocking, powers TX/RX lanes, trains or retrains links, enters low-power PHY states, reads diagnostic counters, or forces overrides for hardware validation.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while writing the wrong DPCS bit, corrupting a reserved bit, or decoding a hardware status field incorrectly.
- The file is generated metadata. Manual edits risk divergence from the authoritative AMD register database, the matching offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are artificial. This slice starts with masks for `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN`; the matching shift definitions are immediately before line 64393. It ends after `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2`; the following lane 1 TX output and RX ASIC input fields are in the next chunk.
- Supervisor and lane naming is dense and repetitive. A generator or merge error can affect only one PLL bank, one lane, or one override/status pairing while nearby groups appear correct.
- PLL, bandgap, reference-clock, and RTUNE fields are sequencing-sensitive. Bad masks for enables, standby, dividers, SSC, fractional-N, charge pump, power-up timers, RTUNE requests, or calibration codes can cause PLL lock failure, unstable PHY clocks, link-training failure, blank displays, high error rates, or suspend/resume-only regressions.
- Lane power and handshake fields are also sequencing-sensitive. Confusing request, ACK, reset, data-enable, low-power, pstate, rate, width, MPLL select, receive-detect, or disable bits can lead to stuck handshakes, false receive-detect results, lane bring-up failures, or incorrect power state transitions.
- Analog override and debug fields can bypass normal hardware control. Incorrect DCC DAC, termination, equalization, Vboost, VREF, bandgap, ATB, PMIX, or PLL analog masks may alter electrical behavior or hide the debug evidence needed to diagnose link problems.
- Reserved fields are explicitly named in many registers. Register update helpers must preserve reserved bits according to hardware requirements; broad writes built from incorrect masks could unintentionally toggle reserved silicon behavior.
- Status and counter fields need access-semantics knowledge outside this header. RX statistic counters, calibration status, PLL lock/power-good status, RTUNE status, and DCC ACK/readback fields may be stale or invalid if read while the associated domain is off or transitioning.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.0. Missing or renamed macros should fail where register, shift, and mask tables are initialized.
- Mechanically verify that complete fields in this range have expected `__SHIFT`/`_MASK` pairs, allowing the known start boundary where `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN` shifts are before this chunk.
- Cross-check this range against `dpcs_4_2_0_offset.h` so each complete `DPCSSYS_CR3_SUP_*`, `DPCSSYS_CR3_LANE0_*`, and partial `DPCSSYS_CR3_LANE1_*` register group has a matching offset.
- Diff the chunk against AMD's authoritative DPCS 4.2.0 register database and nearby generated DPCS variants where the CR3 supervisor and lane layouts are expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, and lane power states. Expected signals are stable PLL lock, correct MPLL selection, clean lane request/ACK transitions, successful receive-detect, and no repeated retraining caused by bad pstate/rate/width or calibration fields.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, runtime power management, and GPU reset paths to catch persistence or reinitialization mistakes in supervisor, PLL, RTUNE, lane power, DCC, and analog override fields.
- Validate clock-sensitive modes that stress MPLLA/MPLLB divider, SSC, fractional-N, HDMI divider, reference-clock, and bandgap timing controls. Watch for blank displays, PHY lock failures, audio/video timing instability, symbol errors, or clock recovery issues.
- Use register dumps or PHY debug traces during failing links to confirm RTUNE, MPLL lock/power, bandgap/reference startup, DCC ACK/readback, RX adaptation/equalization, RX statistic counters, and lane TX/RX handshake fields decode correctly.
- Exercise diagnostic paths where available: RX statistic match/count controls, analog test bus selections, DCC DAC controls, termination and EQ override readbacks, async/loopback controls, and PLL/bandgap/RTUNE analog override outputs.

## Cross-Chunk Notes

The previous chunk owns the `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN` shift definitions and earlier CR3 supervisor charge-pump override fields. This chunk begins with that register's masks, then covers a large CR3 supervisor and lane 0 section plus the beginning of CR3 lane 1 ASIC definitions. The next chunk should begin with `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_OUT` and continue lane 1 TX/RX ASIC fields. The final per-file research document should reconcile these boundaries before making whole-file claims about CR3 register coverage.
