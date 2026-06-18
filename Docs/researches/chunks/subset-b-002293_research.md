# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 11944-14320

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for display PHY/controller register fields. It contains no executable C logic; its public surface is a set of preprocessor constants that encode bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCS hardware register fields.

The requested range contains 2,122 `#define` entries over 2,377 lines. It starts immediately after the `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN` shift definitions, so the first lines are that register's masks. It then covers lane 3 ASIC/TX/RX power, analog TX, raw common PLL/control, raw lane PCS/PMA, FSM, IRQ, TX/RX control, and ATE override fields. The range ends at `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_ATE_TX_OVRD_IN_1`, with the next register `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_MASTER_MPLL_LOOP` beginning just after the requested chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the DPCS register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or update that field.

The main register-field families in this chunk are:

- Lane 3 ASIC interface and override fields: `DPCSSYS_CR0_LANE3_DIG_ASIC_*` describes TX/RX request, ACK, pstate, rate, width, MPLL select, data enable, reset, invert, low-power detect, receive-detect request/result, beacon, async drive/data, loopback, HDMI mode, MPHY mode, clock-ready, and cross-lane clock/sync handshakes.
- Lane 3 TX power and timing fields: `TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` carry analog refgen, VCM hold, clock, word clock, reset, serial enable, digital clock, data enable, receive-detect allowance, Vboost allowance, and DCC compensation bits. `TX_PWRUP_TIME_0-5` encode staged enable/reset/rxdet timing, skip controls, and fast receive-detect controls. The DCC CR bank and DCC DAC registers expose address/data, control/range/select, request/update, bin-hot, ACK, and DAC address fields.
- Lane 3 RX statistic and diagnostic fields: `RX_STAT_LD_VAL_1`, `DATA_MSK`, `MATCH_CTL0-5`, `STAT_CTL0-2`, `SMPL_CNT1`, `STAT_CNT_0-6`, `CAL_COMP_CLK_CTL`, and `STAT_STOP` define sample-count start/stop, pattern masks/matches, data masks, counter enables, source selectors, clock controls, valid-loss clear/control, calibration comparison precharge/reference divider, and done bits.
- Lane 3 digital-to-analog TX override/readback fields: `DIG_ANA_TX_OVRD_OUT`, termination-code overrides, TX equalization override banks, DCC DAC override banks, `DIG_ANA_STATUS_0`, and `DIG_ANA_TX_OVRD_OUT_2` expose analog clock/data/refgen/reset/serial/MPLL enable controls, EQ leg pull enables/directions, pre/post/equalization mux controls, DCC calibration controls, RX detect readbacks, clock-shift ACK, loopback, ACJTAG, and fast-start controls.
- Lane 3 raw analog TX fields: `ANA_TX_OVRD_MEAS`, `ANA_TX_PWR_OVRD`, `ANA_TX_ALT_BUS`, `ANA_TX_ATB1/2`, `ANA_TX_DCC_DAC`, `ANA_TX_DCC_CTRL1`, `ANA_TX_TERM_CODE`, `ANA_TX_TERM_CODE_CTRL`, `ANA_TX_OVRD_CLK`, `ANA_TX_MISC1-3`, and reserved registers describe analog test bus selection, forced ATB signals, alt-bus/JTAG/ring oscillator hooks, DCC DAC programming, termination-code programming and update/reset strobes, MPLL/word-clock/loopback overrides, Vref selection, peaking/slew/vreg controls, and reserved/NC bits.
- Raw common control and MPLL fields: `RAWCMN_DIG_CMN_CTL`, `MPLLA_*`, `MPLLB_*`, `CMN_CTL_1`, `MPLL_STATE_CTL`, `TX_CAL_CODE`, `SRAM_INIT_DONE`, `OCLA`, `SUP_ANA_OVRD`, ID-code registers, firmware ID registers, AON RTUNE values, AON SRAM/power-gate/supervisor/resistor/reference-range overrides, VREF stats, and MPLL power-down time fields. These govern common PHY reset, MPLLA/MPLLB divider/BW/SSC/fractional override inputs, HDMI mode override, RTUNE request, PWM clock selection, MPLL state timing, SRAM init completion, debug probe selection, analog supervisor overrides, calibration codes, and always-on common tuning state.
- Raw lane PCS transfer fields: `RAWLANE0_DIG_PCS_XF_TX_*` and `RX_*` describe TX/RX pstate, low-power detect, width, rate, MPLL select/enable, master MPLL states, reset/request/detect-rx overrides, Vboost/iboost/beacon overrides, PCS input/output ACKs, RX adaptation controls, RX data-enable override, RX LOS threshold, VCO/ref load values, equalization status, RX valid/clock controls, adaptation ACK/FOM, directed TX pre/main/post cursor feedback, lane number, ATE override inputs, RX EQ override values, TX/RX termination controls, and PH2 calibration signals.
- Raw lane FSM and IRQ fields: `RAWLANE0_DIG_FSM_*` covers FSM override, memory/status monitors, fast RX startup/adaptation/AFE/DFE/bypass/reflvl/IQ calibration enables and status, fast supervisor/TX common-mode/RX detect/RX power-up/VCO wait/VCO cal controls, common calibration status, continuous adaptation/calibration flags, CR lock, TX DCC flags/status, OCLA, TX EQ update, RCAL status, and RX IQ phase offset. `RAWLANE0_DIG_IRQ_CTL_*` covers RX/TX reset and request IRQs, RX rate/pstate/adaptation IRQs, clear registers, masks, lane transceiver-mode IRQs, PH2 calibration IRQs, loopback IRQs, and DCC on-demand IRQ.
- Raw lane PMA and TX/RX control fields: `PMA_XF_*` describes lane MPLLA/MPLLB enable overrides, supervisor state overrides, TX/RX PMA override outputs, PMA ACKs, lane RTUNE request/ACK, MPHY PWM/termination overrides, RX adaptation IQ phase adjustment, TX FSM/clock controls, TX DCC continuous status, TX/RX OCLA probes, RX FSM enable/rate-change behavior, LOS mask timing, RX data-enable override timing, and continuous off-cancel/adaptation status.
- ATE-specific PCS override fields at the end of the chunk: `PCS_XF_ATE_RX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN`, and `PCS_XF_ATE_TX_OVRD_IN_1` mirror normal RX/TX rate/width/pstate/loopback/MPLL/beacon/Vboost/iboost/detect-rx/async-data controls for automated test or manufacturing/debug flows.

Most masks in this range are 16-bit style values ending in `L`, matching the DPCS indirect-register field width used by these lane, raw common, and raw lane blocks.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 4.2 resource/display code includes the matching DPCS 4.2.0 offset header and this shift/mask header.
2. Register-list and shift/mask-list macros token-paste DPCS register and field names into tables used by AMD display resource, link encoder, PHY, AUX/link-training, clock-source, and hardware-sequencing code.
3. Runtime display code uses AMD register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` with those offset, shift, and mask tables.
4. Hardware and driver code outside this generated header perform the actual sequencing for lane power, PLL programming, link training, RX adaptation, DCC calibration, IRQ handling, and debug/statistic readback.

The macros in this chunk describe where bits live; they do not encode which fields are read-only, write-one-to-clear, self-clearing, latched, sequencing-sensitive, or clock-domain dependent.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR0 lane 3, raw common, and raw lane 0 DPCS registers:

- TX lane state: pstate programming, analog and digital clock enables, refgen/VCM/word-clock/reset/serial/data enable, receive-detect timing, Vboost and DCC compensation policy, PLL select/enable, beacon/async drive state, lane master/cross-lane sync, and TX equalization/termination values.
- RX lane state: request/reset/ACK handshakes, rate/width/pstate, RX valid/clock, low-power-detect, LOS thresholds, adaptation request/continuous/off-cancel controls, VCO/ref load values, equalization status and override values, IQ phase offset/adjustment, and RX data-enable override timing.
- Common PHY state: functional reset, MPLLA/MPLLB divider, bandwidth, SSC, fractional controls, init-calibration disables, RTUNE request and values, HDMI mode, PWM clocking, MPLL state timing/bank selection, SRAM init done, firmware and PCS ID readbacks, AON power-gate/supervisor/resistor/reference-range overrides, VREF stats, and MPLL power-down time.
- Diagnostic and test state: RX statistic match/mask/counter registers, sample counters, valid-loss controls, OCLA debug selectors, analog test bus selectors, alternate bus/JTAG hooks, DCC DAC debug controls, ATE override surfaces, PH2 calibration request/ACK, and directed TX coefficient feedback.
- Interrupt state: RX and TX reset/request/rate/pstate/adaptation/PH2/lane-mode/loopback/DCC IRQ status, clear, and mask fields.

Persistence is hardware-defined. Configuration fields generally remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, ACK, IRQ, statistics, calibration, and handshake fields may be latched, clear-on-write, sampled, self-clearing, or valid only while the relevant lane/common clock and power domains are active. This generated header does not record those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching `ixDPCSSYS_*` register offsets for the field names described here.
- AMD display DCN/DPCS resource code includes generated offset and shift/mask headers to initialize register, shift, and mask tables for the display engine version that owns DPCS 4.2.0.
- Link encoder, PHY, AUX/link-training, clock-source, and hardware-sequencing code consume those initialized tables indirectly when programming display PHY lanes, shared MPLL/reference-clock state, lane training, and debug or interrupt paths.
- Firmware and hardware state machines interact with the same register fields, especially for MPLL state, SRAM init, RX adaptation/calibration, DCC, RTUNE, IRQ latching, ATE, and PMA/PCS handshakes.

Behaviorally, this range sits below the user-facing display stack. It describes the low-level bit layout used when the driver enables or powers down TX/RX lanes, selects MPLLA/MPLLB clocking, configures HDMI/DisplayPort PHY behavior, runs receiver calibration/adaptation, handles lane-level interrupts, or reads low-level diagnostic counters.

## Risks And Edge Cases

- These constants are untyped preprocessor values. An incorrect shift or mask can compile cleanly while writing the wrong DPCS field, corrupting a reserved bit, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from the authoritative AMD register database, the matching offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are artificial. This slice starts with masks for `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN`; the matching shifts are in the previous chunk. The next chunk continues with `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_MASTER_MPLL_LOOP` and later raw-lane fields.
- Lane 3 and raw lane 0 naming are both present in the same range. Consumers must pair these masks with the correct offset and register-list macro; assuming that all fields in the chunk belong to one lane numbering scheme would be wrong.
- Power, PLL, and calibration fields are sequencing-sensitive. Bad masks for pstate enables, MPLL dividers/BW/SSC/fractional controls, DCC DAC handshakes, VCO/ref load values, RTUNE, or RX adaptation controls can cause link-training failure, unstable clocks, blank displays, high error rates, or resume-only regressions.
- ACK, IRQ, clear, and mask fields are side-effect-sensitive. Confusing status, clear, and mask bits can produce missed lane events, repeated interrupts, stuck ACK waits, or failure to observe adaptation/rate/pstate changes.
- Raw PCS/PMA override and ATE fields can bypass normal state-machine control. Incorrect masks may force reset/request/data-enable/loopback/MPLL/termination behavior that is difficult to diagnose from higher-level display state.
- Analog and diagnostic fields are high-risk despite being debug-oriented. Wrong ATB, termination, DCC, equalization, Vref, or alt-bus masks can hide debug evidence or alter PHY electrical behavior.
- Repeated lane and PLL register groups are copy-sensitive. A generator or merge error can affect only one lane, one PLL bank, or one status block while nearby groups appear correct.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.0. Missing or renamed macros should fail where register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in this range has an expected `__SHIFT`/`_MASK` pair, allowing the known boundary exception where `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN` shifts are just before this chunk.
- Cross-check this slice against `dpcs_4_2_0_offset.h` so every complete register group in the chunk has a corresponding `ixDPCSSYS_*` offset.
- Diff against AMD's authoritative DPCS 4.2.0 register database and nearby generated variants such as `dpcs_4_0_0_sh_mask.h`, `dpcs_4_1_0_sh_mask.h`, or older DPCS headers where register layouts are expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across available PHY lanes, rates, widths, and power states. Expected signals are stable link training, correct lane power transitions, correct MPLL selection, no false lane IRQs, and no stuck ACK/status bits.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in power, pstate, PLL, calibration, IRQ, and AON common fields.
- Validate high-bandwidth and clock-sensitive modes that stress MPLLA/MPLLB divider, bandwidth, SSC, fractional, HDMI-mode, and PWM clock controls. Watch for blank displays, PHY lock failures, retraining loops, display corruption, or audio/video timing instability.
- Use register dumps or PHY debug traces during failing links to confirm RX adaptation, VCO/ref load, equalization, DCC status, RTUNE, FSM status, IRQ clear/mask, and statistic counter fields decode correctly.
- Exercise diagnostic paths where available: OCLA, RX statistic match/count controls, analog test bus/readback fields, directed TX coefficient feedback, PH2 calibration, loopback controls, and ATE overrides.

## Cross-Chunk Notes

The previous chunk owns the `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN` shift definitions and the preceding lane 2 analog RX tail. This chunk begins with that register's masks and then covers a large CR0 lane 3/raw-common/raw-lane section. The next chunk should begin with `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_MASTER_MPLL_LOOP` and continue the raw lane PCS RX override fields. The final per-file research document should reconcile these boundaries before making whole-file claims about all DPCS 4.2.0 register groups.
