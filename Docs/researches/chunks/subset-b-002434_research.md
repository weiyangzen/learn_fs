# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 118172-120745

## Scope

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice for `C20_PHY_CR1` display PHY registers. It covers lines 118172 through 120745 and contains 2,116 `#define` lines, all of them `__SHIFT` macro definitions. There are 458 visible register-group comments in the range. The apparent `_MASK` text inside the range is part of field names such as `DIS_APB_TIMEOUT_MASK__SHIFT`, not emitted mask constants.

The chunk starts in the middle of `C20_PHY_CR1_SUP_DIG_ANA_XF_MPLLA_ANA_CREG03`, after that register's group comment and earlier field definitions. It then covers supervisor analog-to-digital transfer fields, raw common/AON common control fields, lane 0 TX and RX fields, and the start of lane 1 TX fields. It ends inside `C20_PHY_CR1_LANE1_DIG_ANA_XF_TX_OVRD_OUT_1`; the rest of that register group and the matching `_MASK` definitions are outside this chunk.

Although the local source path is under a `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`dpcs_4_2_3_sh_mask.h` provides symbolic bit positions and masks for AMD Display Core PHY Services registers. Consumers pair these macros with `dpcs_4_2_3_offset.h` register offsets and AMD display register helpers so driver code can compose, update, and decode memory-mapped or indexed DPCS CR registers without hard-coding raw bit numbers.

This slice focuses on CR1 common and lane-local PHY control:

- MPLLA/MPLLB analog control shifts for PLL enable/reset/calibration, clocking, voltage regulator controls, charge-pump and bias controls, gear shift, standby/test modes, and reserved analog words.
- Raw common digital control shifts for PHY reset, CREG clock gating, MPLL calibration/SSC/HDMI/RTUNE control, ATE ALU registers, firmware/static configuration status, PLL recalibration bank overrides, context restore, context selection, debug words, and supervisor/MPLL context configuration.
- Always-on common control shifts for SRAM/ROM and power-gating behavior, MPLLA/MPLLB tune banks and calibration bank selection, MPLL and RTUNE recalibration status, RTUNE RX/TX calibration values for multiple lanes, firmware/raw version registers, APB timeout settings, common clock/power status, and SRAM recovery metadata.
- Lane 0 TX shifts for ASIC lane/TX overrides, TX ASIC input/output mirrors, power-state templates, power-up timers, TX DCC controls, TX statistic counters, clock alignment, LBERT pattern generation, FIFO control, digital-to-analog TX override outputs, TX DCC calibration, TX equalization override/readback, and TX analog CREG controls.
- Lane 0 RX shifts for RX ASIC overrides, signal-detect and CDR/VCO/equalization controls, RX ASIC input/output mirrors, extended DFE and AFE equalization overrides, RX power-state templates, RX power-up timers, RX VCO calibration controls/status, RX LBERT, CDR/DPLL control, RX adaptation and statistic/control groups.
- Lane 1 TX shifts for the corresponding ASIC lane/TX overrides, TX ASIC mirrors, power-state templates, power-up timers, DCC/statistic/clock-alignment/LBERT/FIFO controls, and the beginning of TX analog override outputs.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, global variables, allocation paths, locks, includes, or inline helpers in this chunk. The exported surface is the generated preprocessor macro pattern:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field within a DPCS register.

The requested range does not include the corresponding `<REGISTER>__<FIELD>_MASK` definitions for these fields. Those are later in the generated header and must be reconciled at the whole-file or adjacent-chunk level.

Major macro namespaces in this slice are:

- `C20_PHY_CR1_SUP_DIG_ANA_XF_MPLLA_ANA_*` and `C20_PHY_CR1_SUP_DIG_ANA_XF_MPLLB_ANA_*`: common analog PLL control fields. MPLLA is represented by the tail of `CREG03` plus `CREG04`, `CREG05`, and an override word; MPLLB includes `CREG00` through `CREG07` and two override words.
- `C20_PHY_CR1_RAWCMN_DIG_*`: raw common digital control/status registers for reset, clock gate, MPLL input/configuration, firmware status, static configuration status, common calibration, async clock overrides, fractional update, CREG access, context restore, context selection, debug, and supervisor/MPLL context data.
- `C20_PHY_CR1_RAWCMN_DIG_AON_*`: always-on common registers for SRAM, MPLL tune banks, calibration bank select, tune done, recalibration, power-gating overrides, supervisor request/ack handshakes, RTUNE values, firmware versioning, SRAM boot/recovery addresses, APB configuration, and common status.
- `C20_PHY_CR1_LANE0_DIG_ASIC_*`: lane 0 ASIC-facing lane/TX/RX control, override, input, and output fields. These include TX/RX reset, invert, request, low-power detect, pstate, rate, width, data enable, loopback, PLL selection, RX detect, TX equalization cursors, DCC range/update/bypass, RX CDR/VCO load values, signal detect thresholds, DFE/CTLE/VGA/AFE equalization, and adaptation acknowledgement/status.
- `C20_PHY_CR1_LANE0_DIG_TX_*` and `C20_PHY_CR1_LANE0_DIG_RX_*`: lane 0 TX/RX power-control, timing, calibration, debug, LBERT, CDR/DPLL, adaptation, and statistic fields.
- `C20_PHY_CR1_LANE0_DIG_ANA_XF_TX_*`: lane 0 digital-to-analog TX override, DCC, equalization, status, and TX analog CREG transfer fields.
- `C20_PHY_CR1_LANE1_DIG_*`: lane 1 TX-facing mirror of the lane 0 TX-oriented sections through the beginning of `ANA_XF_TX_OVRD_OUT_1`.

## Control Flow

This header slice has no runtime control flow. It is declarative compile-time metadata.

At runtime, control flow exists in consumers that include the generated headers:

1. DCN316 resource code includes `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`.
2. DPCS register-list and shift/mask-list macros, such as `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`, token-paste generated names into resource tables.
3. Display link encoder and PHY code use AMD register helpers to read, write, update, or poll DPCS registers through those tables.
4. Hardware state machines, firmware, and PHY analog logic interpret the bitfields described by this header.

The macros do not encode ordering rules. Consumers must still sequence common PLL bring-up, RTUNE, AON power and clock requests, lane TX/RX power-state transitions, DCC/VCO/equalization calibration, link training, and suspend/resume restoration according to hardware programming requirements.

## State And Persistence Behavior

No software state is stored in this chunk. The constants describe hardware-backed register state whose persistence is defined by the ASIC reset, power, clock, and firmware domains.

Important state represented by this range includes:

- Common PLL and analog state: MPLLA/MPLLB enable, reset, calibration, feedback clock, charge-pump, VREG, ring, divider, standby, test, and gear-shift controls.
- Common raw/AON state: PHY reset, CREG clock gate, MPLL init-cal-disable and SSC inputs, HDMI mode, RTUNE request flow, ATE ALU operands/results, firmware/static configuration done flags, common calibration done flags, recalibration bank selection, context restore/configuration words, SRAM/ROM boot configuration, firmware version, APB timeout, and power/clock status.
- Lane TX state: request/ack handshakes, reset, pstate, rate, width, data and clock enables, PLL source, RX detect, TX equalization cursors, VBOOST, DCC range/bypass/update, TX power-state templates for P0/P0S/P1/P2, power-up timer fields, clock alignment state, LBERT patterns, FIFO bypass/start pointer, TX analog override values, DCC calibration data, and TX equalization/status readbacks.
- Lane RX state: reset/request/pstate/rate/width, DFE bypass, CDR tracking and SSC, VCO and reference load values, signal-detect thresholds, CTLE/VGA/AFE/DFE equalization and offsets, RX adaptation status, RX power-state templates, RX timing controls, RX VCO calibration FSM/status, RX LBERT/error counting, CDR/DPLL controls, and RX statistic/adaptation registers.

Names ending in `*_STATUS`, `*_STAT`, `*_OUT`, `*_ACK`, `*_DONE`, `*_VERSION`, or `*_ASIC_OUT` are readback-oriented by naming convention, while names with `*_OVRD_IN`, `*_OVRD_EN`, `*_ASIC_IN`, `*_PSTATE_*`, `*_TIME_*`, `*_CTRL`, or `*_CFG` are generally control/configuration-oriented. This generated header does not provide access permissions, sticky-bit behavior, clear-on-read behavior, write-one-to-clear behavior, or reset values.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk must stay synchronized with AMD's generated DPCS 4.2.3 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` supplies matching register offsets such as `ixC20_PHY_CR1_*`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` directly includes both DPCS 4.2.3 generated headers and initializes DPCS register, shift, and mask tables using DCN31-family macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines the `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST` patterns consumed by DCN31-family resource code.

Behaviorally, these definitions integrate with DisplayPort and HDMI link encoder paths, PHY bring-up, hotplug recovery, link-rate changes, lane power management, RX detect and signal-detect flows, PLL/RTUNE calibration, DCC and VCO calibration, link test/pattern generation, hardware validation, and register dump/debug tooling.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A single wrong shift can make a read-modify-write touch the wrong PLL, AON, TX, RX, calibration, or override bit while still compiling cleanly.
- This chunk contains only shift definitions. Any validation that expects shift/mask pairs must include later file ranges and must account for chunk boundaries.
- The first and last register groups are incomplete. The range starts after the `MPLLA_ANA_CREG03` comment and earlier fields, and it ends before the completion of `LANE1_DIG_ANA_XF_TX_OVRD_OUT_1`.
- Common registers are shared by the CR1 PHY block. Errors in MPLL, RTUNE, AON power, SRAM/firmware, clock, or common calibration fields can affect multiple lanes and connectors rather than one lane.
- Lane 0 has both TX and RX surfaces in this slice, while lane 1 is represented mostly by TX-facing fields. A bad generator row can therefore appear as lane-specific link training, calibration, or debug behavior.
- Override value and override-enable fields are densely repeated. Setting a value without the paired enable has no intended effect; leaving an enable asserted can hold hardware in a forced test or recovery state across later modesets or resume.
- Status and control fields are represented with the same preprocessor shape. Callers need hardware documentation or generated access metadata to avoid writing read-only/status bits, polling the wrong done/ack bit, or clearing sticky state unexpectedly.
- Timing and calibration fields are sequencing-sensitive. Incorrect shifts in TX/RX power-up times, VCO calibration, DCC calibration, CDR/DPLL, equalization, or RTUNE can cause failures that only appear at high link rates, after low-power transitions, or on marginal boards.

## Test Signals

Useful validation is mostly build-time, generator-level, and hardware-integration oriented:

- Build AMDGPU display code with DCN316 enabled so `dcn316_resource.c` includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Mechanically verify the full generated header, not only this chunk, for expected shift/mask pairing. This specific chunk should be treated as a shift-only range with known boundary exceptions at `C20_PHY_CR1_SUP_DIG_ANA_XF_MPLLA_ANA_CREG03` and `C20_PHY_CR1_LANE1_DIG_ANA_XF_TX_OVRD_OUT_1`.
- Cross-check each visible `C20_PHY_CR1_*` register group against the matching `dpcs_4_2_3_offset.h` offset names and the authoritative DPCS 4.2.3 register database.
- Diff related generated variants, especially nearby DPCS/DCN revisions that expose `C20_PHY_CR1` fields, to catch accidental lane, field-width, or reserved-bit drift.
- Exercise hardware using this DPCS revision across DP and HDMI paths: hotplug, link training, link-rate and lane-count changes, RX detect, signal detect, suspend/resume, GPU reset, low-power entry/exit, and repeated modesets.
- Inspect register dumps during bring-up and recovery for expected MPLL/RTUNE/AON status, firmware/static configuration done bits, power/clock stability, TX/RX pstate transitions, TX/RX calibration completion, CDR/VCO state, DCC status, equalization/adaptation status, and cleanup of override-enable bits.
- Watch kernel/display diagnostics for link training failures, calibration timeouts, stuck ack/done polling, blank displays after resume, unstable high-rate links, repeated retrains, or failures isolated to CR1 lane 0 or lane 1 TX programming.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 118172-120745 of `dpcs_4_2_3_sh_mask.h`. The final per-file document should merge this with adjacent chunks before making whole-file claims about all `C20_PHY_CR1` fields or all DPCS 4.2.3 shift/mask pairs. Earlier chunks own the beginning of the CR1 supervisor sections and the start of `MPLLA_ANA_CREG03`; later chunks own the rest of lane 1, subsequent lanes/raw-lane sections, and the mask definitions that correspond to many shift macros described here.
