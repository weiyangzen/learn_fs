# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 112790-115205

## Purpose

This chunk is a generated AMD DCN 4.1.0 shift/mask register-field slice for DisplayPort PHY/PCS CR2 registers. It contains no executable C; its exported surface is the preprocessor contract of `#define ...__SHIFT` and `#define ..._MASK` constants used by AMDGPU display register helpers to encode, update, and decode hardware bitfields.

The range covers 261 register comment blocks and 2,155 macro definitions. It starts at `DPCSSYS_CR2_LANE3_DIG_RX_STAT_MATCH_CTL1` and ends at `DPCSSYS_CR2_RAWLANE1_DIG_FSM_FAST_RX_STARTUP_CAL`. The chunk boundary is not semantic: lane 3 RX statistic definitions begin in the previous chunk, and raw lane 1 FSM definitions continue after this range.

Although the repository path includes `ceph-client`, this file is AMDGPU DCN display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or direct MMIO operations in this range. The API is the generated bitfield macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a field inside an indirect CR2 register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field inside the same register.

The visible register groups are:

- Lane 3 RX statistic and pattern-match controls: `DPCSSYS_CR2_LANE3_DIG_RX_STAT_MATCH_CTL1` through `STAT_STOP`, including pattern A/B masks, sample count start/done state, seven statistic counters, correlation/stat source selection, clock enable, valid-loss clear, sample-count disable, and stop control.
- Lane 3 digital-to-analog TX controls: `DIG_ANA_TX_OVRD_OUT`, termination-code override/clocking, six TX equalization override output registers, analog status, DCC DAC override outputs, and a second TX override register.
- Lane 3 analog TX registers: override measurement, power override, alternate bus, ATB taps, DCC DAC and DCC control, termination code/control, override clock, miscellaneous controls, select mux, voltage regulator control, and reserved scratch-style registers.
- Raw common CR2 controls: common control, MPLLA/MPLLB override and bandwidth fields, SSC override fields, lane FSM extension, MPLL state, TX calibration code, SRAM init done, OCLA/debug selection, supervisor analog override, PCS/FW ID codes, always-on common RTUNE values for RX/TXDN/TXUP lanes 0-7, SRAM bitline config, power-gating/supervisor/resource override/status, VREF stats, reference-range override, and miscellaneous common config.
- Raw lane 0 PCS/FSM/IRQ/PMA/TX/RX controls: TX/RX PCS override and status paths, TX/RX request/reset/data enable, rate/pstate/width/clock controls, RX adaptation controls and readbacks, TX pre/main/post cursor and EQ controls, termination controls, lane number, ATE overrides, PH2 calibration, lane FSM override/status/fast flags, IRQ status/clear/mask registers, PMA bridge registers, TX/RX controller status, OCLA/UPCS debug registers, and extra ATE/master-MPLL controls.
- Raw lane 1 beginning: PCS TX/RX override and status paths through early FSM monitor state and `FAST_RX_STARTUP_CAL`.

Representative fields include `STAT_CNT_*_EN`, `SMPL_CNT1_DONE`, `SC1_STOP`, `TX_ANA_*`, `TX_TERM_CODE`, `TX_PRE_CURSOR`, `TX_MAIN_CURSOR`, `TX_POST_CURSOR`, `TX_DCC_DAC_*`, `MPLLA_*`, `MPLLB_*`, `RTUNE_*`, `RX_ADAPT_*`, `RX_EQ_*`, `RX_TERM_CTRL`, `TX_TERM_CTRL`, `FSM_*`, `IRQ_MASK`, `IRQ_TYPE`, `IRQ_STATUS`, `IRQ_CLR`, `PMA_*`, `TX_FSM_LANE_RESET`, `RX_FSM_LANE_RESET`, and `OCLA_*`.

Most masks are 16-bit CR register masks with an `L` suffix, for example `0x0001L`, `0x00F0L`, `0x7FFFL`, or `0xFFFFL`. Consumers typically combine these with the matching offset macros and AMD display register helpers such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

## Control Flow

This header has no runtime control flow. Runtime behavior is created by consumers that include generated offset and shift/mask headers:

1. DCN401 display code includes `dcn/dcn_4_1_0_sh_mask.h` and expands register-field lists into arrays of masks and shifts.
2. For direct DCN registers, the paired include is `dcn_4_1_0_offset.h`; for the CR2 PHY/PCS indirect names in this chunk, the matching register addresses are visible in the DPCS offset header family, notably `dpcs_3_1_4_offset.h`.
3. Display, DMUB, IRQ, GPIO, link-training, or PHY-control code calls common AMD register helpers. Those helpers token-paste register and field names into offsets, masks, and shifts.
4. The actual sequencing for training, reset, adaptation, PLL power-up, interrupt servicing, and debug capture lives in driver logic and hardware firmware. This generated slice only supplies the bit positions that those paths require.

The repeated lane naming is part of the compile-time contract. Lane 0 and lane 1 raw register layouts are largely isomorphic, while lane 3 analog/statistic names refer to a separate instance. A mistaken instance prefix can still compile if the same field exists on another lane.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It defines encodings for hardware-visible PHY and PCS state:

- RX statistic state: pattern-match configuration, sample window timing, statistic counter enables, sample-complete flags, correlation/statistic source selection, valid-loss clear, and stop bits.
- TX analog state: clock enables, reset, serial/data enable, data-rate selection, divider/RX-detect enable, override enables, equalization cursor values, termination values, DCC DAC values, and analog status.
- Common PHY state: MPLL override, spread-spectrum control, lane FSM extension, SRAM initialization state, TX calibration, supervisor analog overrides, RTUNE values, power-gating/resource override state, VREF stats, and common ID/version codes.
- Lane PCS state: TX/RX request/reset/data enable, rate, width, pstate, beacon, TX EQ, RX adaptation request/ack/FOM, EQ gain/tap/CTLE values, termination controls, phase calibration, lane number, and ATE override values.
- FSM, IRQ, and debug state: lane FSM command override and status, fast calibration/adaptation flags, reset/request/rate/pstate/adaptation/PH2/loopback/DCC/TX IRQ status-clear-mask fields, PMA bridge state, OCLA selection, and controller status bits.

Persistence is hardware-defined. Override/configuration fields generally remain until reprogrammed by link training, modeset, power management, firmware, suspend/resume, GPU reset, or ASIC reset. Status, acknowledge, interrupt, clear, sample-done, calibration, and debug fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the relevant PHY lane, common PLL, or always-on block is powered and clocked. This header does not encode those access rules.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus AMD's generated register-header convention. This file must remain synchronized with the authoritative AMD DCN/DPCS register database and the matching offset headers. The CR2 register offsets for representative names in this chunk appear in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`, for example lane 3 `RX_STAT_MATCH_CTL1` at `0x1383`, lane 3 `DIG_ANA_TX_OVRD_OUT` at `0x13a0`, `RAWCMN_DIG_CMN_CTL` at `0x2000`, raw lane 0 `PCS_XF_TX_OVRD_IN` at `0x3000`, and raw lane 1 `FSM_FAST_RX_STARTUP_CAL` at `0x3123`.

The broader DCN401 stack includes `dcn_4_1_0_sh_mask.h` from files such as `display/dmub/src/dmub_dcn401.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, and `display/dc/gpio/dcn401/hw_translate_dcn401.c`. Those files demonstrate the integration pattern: register-field lists are expanded into masks/shifts through macros like `FD_MASK`, `FD_SHIFT`, and direct `REGISTER__FIELD_MASK` references.

Functional integration points are DP link bring-up and maintenance, PHY reset/power sequencing, TX equalization, RX adaptation, PLL/common-lane configuration, interrupt/status servicing, ATE/manufacturing hooks, and OCLA/debug capture. Higher-level display code depends on these constants when programming or observing PHY/PCS state during hotplug, link training, modeset, suspend/resume, diagnostics, and reset recovery.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing unrelated hardware bits or decoding plausible but incorrect status.
- The file is generated. Manual edits risk divergence from the hardware register database, paired DPCS/DCN offset headers, firmware assumptions, and silicon documentation.
- The chunk boundaries are partial. The previous chunk contains lane 3 RX statistic load/data/match-control lead-in fields, and the next chunk continues raw lane 1 FSM fast flags and later lane blocks.
- CR2 PHY/PCS registers are indirect hardware-facing state, often only 16 bits wide. Code that assumes ordinary 32-bit DCN MMIO semantics, ignores CR address/data access ordering, or mixes direct and indirect offset families can fail subtly.
- Repeated raw lane layouts make lane drift hard to spot. A copy/paste or token-paste error between raw lane 0, raw lane 1, and lane 3 analog/statistic names may only affect a specific physical lane or connector configuration.
- Override enables are hazardous. Fields ending in `_OVRD_EN`, `_ATE_OVRD_EN`, or similar can force reset, request, data-enable, termination, equalization, clocking, or calibration behavior outside normal firmware control.
- Interrupt and clear fields are side-effect-sensitive. Wrong masks for `IRQ`, `IRQ_CLR`, `IRQ_MASK`, or `IRQ_TYPE` can leave reset/request/rate/pstate/adaptation/PH2/TX events stuck, dropped, or acknowledged incorrectly.
- Training and signal-integrity fields are protocol-visible. Bad masks for TX pre/main/post cursors, DCC, termination, RX EQ/adaptation, MPLL, SSC, RTUNE, or PH2 calibration can produce link-training failures, marginal links, intermittent display dropouts, or board/ASIC-specific failures.
- Status/debug fields can be timing-dependent. Reads during power gating, PLL transitions, calibration, adaptation, or lane reset may be stale or invalid unless driver sequencing checks hardware readiness.

## Test Signals

Useful validation signals are generated-header consistency checks plus display/link runtime behavior:

- Build DCN401 AMDGPU display code with the generated DCN/DPCS headers together. Missing or renamed field macros should fail in register-list expansion or direct mask/shift references.
- Mechanically compare this range against AMD's authoritative DCN 4.1.0/DPCS 3.1.4 register source, treating the first and last registers as partial chunk boundaries.
- Static-check that each `__SHIFT` has a matching `_MASK`, that masks are aligned with shifts, and that reserved-field masks do not overlap named active fields.
- Compare repeated raw lane 0 and raw lane 1 PCS/FSM field sets for expected isomorphism while accounting for the fact that raw lane 1 is incomplete in this chunk.
- Exercise DisplayPort hotplug and link training on ports using the affected CR2 lanes, including multiple link rates, lane counts, retraining, suspend/resume, GPU reset, and rapid unplug/replug.
- Validate TX/RX PHY behavior with diagnostics or hardware tools where available: stable clock/PLL state, expected TX equalization levels, RX adaptation completion, PH2 calibration handshakes, and no stuck FSM states.
- Check interrupt behavior around lane reset/request/rate/pstate/adaptation/PH2/DCC/TX events. Expected signals are no unhandled IRQ storms, no masked required events, and clear registers acknowledging only the intended source.
- Use debug/OCLA paths cautiously to confirm that selected signals match expected lane/common state without perturbing link bring-up.

## Cross-Chunk Notes

The previous chunk supplies the lane 3 RX statistic prelude, including `LD_VAL_1`, `DATA_MSK`, and `MATCH_CTL0`. This chunk finishes the lane 3 RX statistic block, covers lane 3 TX analog/common CR2 controls, covers raw common controls, covers raw lane 0 through extra PCS/ATE controls, and starts raw lane 1. The next chunk is required before making complete claims about raw lane 1 or later raw lanes.
