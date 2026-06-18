# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 11940-14316

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY registers. It contains no executable logic; it exports preprocessor constants that describe bit positions (`__SHIFT`) and masks (`_MASK`) for indirect DPCS hardware registers.

The requested range spans 2,377 source lines, with 2,124 `#define` entries and 253 register-comment markers. It begins at the first field of `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2` but excludes that register's comment marker at line 11939. It then completes late lane-2 analog RX controls, covers a broad CR0 lane-3 digital/analog lane programming section, moves into CR0 raw common PLL/supervisor and RTUNE controls, and continues through CR0 raw lane0 PCS, PMA, FSM, IRQ, MPHY, and RX-adaptation transfer registers. The last line in this chunk is only the marker for `DPCSSYS_CR0_RAWLANE0_DIG_TX_CTL_TX_FSM_CTL`; that register's field definitions start in the next chunk.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU display hardware metadata. It is not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The public interface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, compose, or update that field.

Major register families covered by this chunk include:

- Lane 2 analog RX tail registers: `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2`, `ANA_RX_SQ`, `ANA_RX_CAL1`, `ANA_RX_CAL2`, `ANA_RX_ATB_REGREF`, `ANA_RX_ATB_MEAS1` through `MEAS4`, `ANA_RX_ATB_FRC`, and `ANA_RX_RESERVED1`. These describe DFE/deserializer/loopback/fast-start enable overrides, squelch response/threshold, RX calibration muxes, regulator/test-bus references, ATB measurement selection, and reserved analog latches.
- Lane 3 ASIC-facing digital override and status registers: `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN`, `DIG_ASIC_TX_OVRD_IN_0` through `_5`, `DIG_ASIC_TX_OVRD_OUT`, `DIG_ASIC_RX_OVRD_OUT_0`, `DIG_ASIC_LANE_ASIC_IN`, `DIG_ASIC_TX_ASIC_IN_*`, `DIG_ASIC_TX_ASIC_OUT`, and `DIG_ASIC_RX_ASIC_OUT_0`. These fields expose request, pstate, rate, width, MPLL select, data-enable, reset, beacon, async, cursor, EQ, deemphasis, termination, loopback, and acknowledge-style handshakes between ASIC control logic and the lane PHY.
- Lane 3 TX power/control and debug registers: `DPCSSYS_CR0_LANE3_DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, `P2`, `TX_PWRUP_TIME_*`, `DCC_CR_BANK_*`, `DCC_DAC_*`, `DIG_TX_CLK_ALIGN_TX_CTL_0`, and `DIG_TX_LBERT_CTL`. These encode pstate-specific TX settings, power-up timing, DCC bank access and DAC selection/acknowledgement, clock alignment, and link built-in error-test controls.
- Lane 3 RX statistics registers: `DPCSSYS_CR0_LANE3_DIG_RX_STAT_*` groups define sample-load values, data masks, match controls, statistic/correlation selectors, sample/stat counters, pause/clock controls, valid-loss handling, calibration comparison clock controls, extended match controls, statistic stop, and related status/control fields.
- Lane 3 digital-to-analog TX/RX surfaces: `DPCSSYS_CR0_LANE3_DIG_ANA_TX_OVRD_OUT`, TX term-code and EQ override groups, `DIG_ANA_STATUS_0`, TX DCC DAC override groups, and `DIG_ANA_TX_OVRD_OUT_2`. The companion analog TX groups `DPCSSYS_CR0_LANE3_ANA_TX_*` cover measurement overrides, power overrides, alternate bus selection, ATB control, DCC DAC/control, termination-code programming, override clocking, slew/vreg/misc controls, and reserved registers.
- CR0 raw common controls: `DPCSSYS_CR0_RAWCMN_DIG_CMN_CTL`, MPLLA/MPLLB override and SSC override groups, lane FSM extension, common control, MPLL state control, TX calibration code, SRAM init status, OCLA, supervisor analog overrides, PCS and firmware ID readbacks, AON RTUNE RX/TXDN/TXUP values for lanes 0-7, SRAM bitline config, AON power-gating overrides, supervisor overrides, VREF statistics, resistor/reference-range overrides, and miscellaneous common configuration.
- CR0 raw lane0 PCS transfer registers: `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_TX_*`, `RX_*`, `RX_ADAPT_*`, directed TX cursor feedback registers, lane number, ATE overrides, RX EQ delta/IQ controls, TX/RX termination controls, and PH2 calibration. These fields model the transfer interface between PCS control and lane PHY state for TX/RX rate, pstate, width, reset, request, data enable, loopback, beacon, adaptation, FOM, and termination behavior.
- CR0 raw lane0 FSM and fast-path controls: `DPCSSYS_CR0_RAWLANE0_DIG_FSM_*` groups define FSM overrides, memory/status monitors, fast RX startup/adapt/AFE/DFE/bypass/reference-level/IQ calibration controls, fast supervisor/TX common-mode/RX detect/RX power-up/VCO wait/VCO calibration controls, MPLL and RCAL calibration status, continuous calibration/adaptation flags, CR lock, TX DCC flags/status, TX EQ update flag, OCLA selection, and RX IQ phase offset.
- CR0 raw lane0 IRQ controls: `DPCSSYS_CR0_RAWLANE0_DIG_IRQ_CTL_*` defines reset-return request, RX reset/request/rate/pstate/adaptation IRQs, corresponding clear registers, IRQ mask and mask-2 fields, lane transceiver-mode IRQs, PH2 calibration request/disable IRQs, serial loopback IRQs, DCC on-demand status, TX reset/request IRQs, and TX clear registers.
- CR0 raw lane0 PMA transfer registers: `DPCSSYS_CR0_RAWLANE0_DIG_PMA_XF_*` groups expose PMA lane and supervisor override inputs/outputs, TX/RX request/reset/data-enable/loopback/beacon/async/DWORD-clock override outputs, TX/RX PMA acknowledgements, lane RTUNE request and acknowledgement, MPHY PWM/termination/asynchronous controls, and RX PMA IQ phase-adjust adaptation override output.

Most masks in this region use low 16-bit values with an `L` suffix, consistent with DPCS indirect register fields. Reserved and `NC` fields are also exported as masks; callers must still treat their semantics as hardware-defined.

## Control Flow

This header has no runtime control flow. It participates in compile-time register metadata setup:

1. AMD display code for the matching ASIC generation includes this DPCS 4.2.2 shift/mask header and the companion offset header.
2. Version-specific register, shift, and mask tables refer to these generated token names, often through register helper macros and token-pasted field names.
3. Runtime driver paths use those tables with helpers such as register read, write, get, set, and update operations.
4. Actual sequencing for lane power, link training, PLL setup, RX adaptation, RX statistic capture, PMA/PCS handshakes, DCC/RTUNE calibration, IRQ clear/mask behavior, and debug capture lives outside this generated header.

The macros describe bit layout only. They do not encode access type, reset value, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, timing requirements, clock-domain restrictions, or power-domain validity.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR0 DPCS lane and raw-lane registers:

- Lane 2 RX analog state includes DFE, deserializer, loopback, fast-start, squelch, calibration mux, ATB measurement/reference, regulator, and reserved analog fields.
- Lane 3 ASIC and lane PHY state includes TX/RX request, reset, pstate, rate, width, MPLL selection, data enable, beacon, async drive, loopback, cursor, pre/main/post EQ, deemphasis, termination, vboost, receive-detect, acknowledgements, and state-machine-facing status.
- Lane 3 TX power state includes pstate-specific TX control values, power-up timing, DCC DAC/bank state, clock alignment, and LBERT test settings.
- Lane 3 RX statistic state includes match masks, match patterns, statistic/correlation source selection, sample counters, statistic counters, done bits, clock/pause controls, valid-loss controls, and stop controls.
- Lane 3 analog TX state includes power overrides, measurement muxes, ATB routing, DCC DAC values, termination codes, override clocks, slew/vreg/peaking controls, and status readbacks.
- Raw common state includes MPLLA/MPLLB override and SSC fields, lane FSM operation extension, MPLL state controls, TX calibration code, SRAM init status, OCLA selection, firmware and PCS IDs, AON RTUNE values across lanes, common power-gating/supervisor/resistor/reference-range controls, and VREF statistics.
- Raw lane0 PCS/PMA/FSM state includes PCS transfer request/reset/data-enable/loopback/rate/pstate/width signals, RX adaptation ACK/FOM and directed TX coefficient feedback, termination controls, PH2 calibration, fast calibration/adaptation enables, continuous adaptation/calibration status, lane IRQ status/clear/mask bits, PMA handshakes, lane RTUNE, MPHY PWM/termination/asynchronous controls, and RX PMA IQ phase adjustment.

Persistence is determined by hardware. Configuration fields generally remain until modeset or link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, ACK, IRQ, statistic, calibration, and handshake fields may be latched, sampled, self-clearing, clear-on-write, or valid only while their lane/common clock and power domains are active. This header does not define those semantics.

## Dependencies And Integration Points

This generated header must stay synchronized with AMD's DPCS 4.2.2 register database and with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`.

Observed companion offset anchors include:

- `ixDPCSSYS_CR0_LANE3_DIG_ASIC_TX_OVRD_IN_0` at `0x1301`, matching the lane-3 ASIC transfer area in this chunk.
- `ixDPCSSYS_CR0_RAWCMN_DIG_CMN_CTL` at `0x2000`, matching the raw common section.
- `ixDPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN` at `0x3000`, matching the raw lane0 PCS transfer section.
- `ixDPCSSYS_CR0_RAWLANE0_DIG_TX_CTL_TX_FSM_CTL` at `0x3080`, matching the next register marker at the chunk end.

The macros integrate with AMDGPU display DCN/DPCS resource code through generated register/shift/mask tables rather than through direct local logic in this file. Consumers include low-level display PHY initialization, DisplayPort and HDMI link training, clock and PLL programming, lane power transitions, hotplug and modeset paths, diagnostics, debug register dumps, IRQ handling, suspend/resume restore, and manufacturing or ATE test paths.

Firmware or hardware state machines interact with many of the same fields, especially raw common MPLL/SSC controls, AON RTUNE values, lane FSM fast-path controls, DCC calibration, PMA/PCS request/acknowledge transfers, RX adaptation, PH2 calibration, and IRQ latches. Driver code must use the correct offset namespace and lane instance when pairing these field masks with register addresses.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- The source chunk boundary excludes the `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2` comment marker while including all of that register's field macros. The final line is only the `DPCSSYS_CR0_RAWLANE0_DIG_TX_CTL_TX_FSM_CTL` comment marker; its actual masks and shifts are in the next chunk.
- Several register groups contain repeated pairs such as value plus override-enable, status plus clear, or input plus output. Mixing those masks can force hardware state unintentionally, miss an IRQ clear, or read an override shadow instead of live state.
- Analog RX/TX fields affect electrical behavior. Incorrect masks for DFE, deserializer, squelch, slicers, calibration muxes, ATB, termination, EQ, DCC DACs, vreg, slew, CDR, loopback, or fast-start controls can cause black screens, unstable links, compliance failures, or misleading debug traces.
- Raw common MPLLA/MPLLB and SSC override fields are clock-sensitive. Bad fields around PLL enable/divider, standby, SSC, calibration, or lane FSM extension can cause link lock failures, retraining loops, mode-specific instability, or suspend/resume regressions.
- AON RTUNE and power-gating fields are lane-wide/common resources. A field error can affect multiple lanes even when the broken macro name appears local to one generated block.
- Raw lane0 PCS/PMA override paths can bypass normal state-machine behavior. Misprogramming request/reset/data-enable/loopback/rate/pstate/width/RTUNE/MPHY/PH2 fields can leave a lane in a state that higher-level display code cannot infer correctly.
- IRQ status, clear, and mask groups repeat very similar names. Confusing status with clear or mask fields can drop events, leave stale interrupts latched, or create repeated interrupt storms.
- RX statistic and adaptation controls are easy to validate only under stressed links. Wrong masks may not be visible in basic modes but can break high-rate links, marginal cables, diagnostics, or factory test flows.

## Test Signals

Useful validation should combine generated-header checks with real display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in lines 11940-14316 has a matching `__SHIFT` and `_MASK` definition, allowing the known boundary cases for the missing `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2` comment and the marker-only `DPCSSYS_CR0_RAWLANE0_DIG_TX_CTL_TX_FSM_CTL`.
- Cross-check all complete register groups against `dpcs_4_2_2_offset.h`, especially the transitions from lane2 analog RX to lane3 digital/analog, then to raw common, then to raw lane0 PCS/FSM/IRQ/PMA areas.
- Diff this generated region against AMD's source register database and nearby DPCS variants such as 4.2.0 and 4.2.3 where layouts are expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, lanes, pstate transitions, hotplug, stream disable/enable, suspend/resume, and GPU reset. Expected signals are stable link training, correct MPLL selection, no stuck PMA/PCS ACK bits, clean IRQ clear/mask behavior, and no unexpected retraining loops.
- Validate high-bandwidth and clock-sensitive modes that stress MPLLA/MPLLB override, SSC, RTUNE, pstate, RX adaptation, TX EQ, DCC, and analog termination fields. Watch for blank displays, PHY lock failures, corruption, audio/video timing instability, rate-specific failures, or compliance regressions.
- Use register dumps or PHY debug traces during failures to confirm that DFE/deserializer/squelch/calibration, RX statistic counters, DCC DAC/status, RTUNE values, FSM status, IRQ status/clear/mask bits, PMA/PCS transfer state, MPHY controls, and RX adaptation FOM/ACK decode correctly.
- Exercise diagnostic paths where available: LBERT, OCLA, RX statistic match/count controls, analog test bus/readback fields, directed TX coefficient feedback, PH2 calibration, loopback controls, ATE overrides, and MPHY low-speed controls.

## Cross-Chunk Notes

The previous chunk ends immediately before this range with `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL1` and the comment marker for `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2`. This chunk owns all `PWR_CTRL2` field definitions and continues through lane2 RX analog tail, lane3 digital/analog controls, raw common controls, and raw lane0 PCS/FSM/IRQ/PMA transfer surfaces. The next chunk should start with the actual `DPCSSYS_CR0_RAWLANE0_DIG_TX_CTL_TX_FSM_CTL` field definitions and continue raw lane0 TX/RX control coverage. The final per-file report should reconcile those artificial boundaries before making whole-file claims.
