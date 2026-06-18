# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 19502-21927

## Scope

This chunk is part of the generated AMD DPCS 3.1.4 ASIC register shift/mask header. It contains preprocessor constants only: each register field is represented by a `...__SHIFT` bit offset and usually a matching `..._MASK` bit mask. There are no C functions, structs, branches, allocations, locks, direct MMIO operations, or persistence mechanisms in this range.

The slice covers 2,426 source lines, 2,155 `#define` entries, and 271 register-comment blocks. It begins inside `DPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P2`, after the first `RX_P2_ANA_AFE_EN__SHIFT` definition, and ends inside `DPCSSYS_CR1_LANE2_DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT`, before that register's mask definitions. Neighboring chunks are needed to reconstruct those two boundary registers completely.

## Purpose

The purpose of this chunk is to publish exact bitfield metadata for DPCS CR1 lane 1 and lane 2 PHY control/status registers. Runtime AMDGPU display/link code combines these generated shift and mask names with companion register-address headers and register helper macros to program or inspect per-lane DisplayPort/PHY hardware without open-coded bit arithmetic.

Major covered areas:

- Tail of lane 1 RX power-state P2 controls, RX power-up timing, VCO calibration controls/status, CDR controls/status, DPLL frequency fields, receiver adaptation controls/status, pattern/statistics counters, MPHY low-speed controls, and analog TX/RX override/status fields.
- Lane 1 analog register aliases for TX override measurement, TX power/term/DCC/misc fields, RX clock/CDR/slicer/power/calibration/test-bus fields.
- Lane 2 ASIC-facing lane/TX/RX override and real input/output fields, including equalization, CDR/VCO, OCLA, lane mapping, transmit drive, receive detection, and calibration handoff fields.
- Lane 2 TX power-state/timing/DCC controls and loopback error-rate test control.
- Lane 2 RX power-state/timing, VCO calibration, CDR/DPLL, adaptation, statistics, MPHY PWM/termination/stable-clock fields.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit position inside a 16-bit DPCS register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used by register-helper update paths.
- Instance prefixes such as `DPCSSYS_CR1_LANE1_` and `DPCSSYS_CR1_LANE2_` are part of the ABI between generated headers and display/PHY register tables. They distinguish two physical lanes with otherwise repeated field layouts.

Important register families in this chunk include:

- Lane 1 RX power and calibration: `DIG_RX_PWRCTL_RX_PSTATE_P2`, `RX_PWRUP_TIME_1/2/3`, `DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0/1/2`, `RX_VCO_CAL_TIME_0/1`, and `RX_VCO_STAT_0/1/2` define AFE, voltage-regulator, clock, CDR, deserializer, VCO reset/calibration, continuous calibration, startup/update/settle timing, calibration-done, VCO counter, too-fast, correct, and up status fields.
- Lane 1 CDR/DPLL and link-test fields: `RX_ALIGN_XAUI_COMM_MASK`, `RX_LBERT_CTL`, `RX_LBERT_ERR`, `RX_CDR_CDR_CTL_0..4`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_0/1` define comma-mask, LBERT mode/sync/error count, phase detector, SSC counters, lock counts, filter settings, edge/status bits, frequency, and bound fields.
- Lane 1 RX adaptation and statistics: `RX_ADPTCTL_ADPT_CFG_0..9`, `RST_ADPT_CFG`, `ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, `DFE_TAP*_STATUS`, slicer/DFE DAC offset controls, CR bank address/data, `RX_STAT_*` match/control/counter registers, and statistic stop fields define equalization/adaptation behavior, loaded values, pattern masks, source selection, sample counts, counter enables, pause/clock/valid-loss controls, and comparator clock timing.
- Lane 1 MPHY and analog overrides: `DIG_MPHY_RX_PWM_CTL`, `TERM_LS_CTL`, `ANA_PWM_CLK_STABLE_CNT`, `DIG_ANA_TX_*`, `DIG_ANA_RX_*`, `DIG_ANA_STATUS_*`, `ANA_TX_*`, and `ANA_RX_*` expose low-speed polarity/termination/stability fields plus digital override outputs for analog TX/RX clocks, data enables, DCC, termination, equalization, AFE/CTLE/VGA/slicer, calibration DACs, phase adjust, signal detect, and test-bus measurements.
- Lane 2 ASIC interface and override fields: `DIG_ASIC_LANE_OVRD_IN`, `DIG_ASIC_TX_OVRD_IN_0..5`, `DIG_ASIC_RX_OVRD_IN_0..6`, `DIG_ASIC_RX_OVRD_EQ_IN_*`, `DIG_ASIC_*_ASIC_IN/OUT`, `DIG_ASIC_RX_CDR_VCO_ASIC_IN_*`, and `DIG_ASIC_OCLA` define the lane's override inputs, hardware-owned ASIC inputs, and observed outputs for power enables, reset lines, DCC, transmit/receive analog enables, CDR/VCO controls, equalization, and observation/logic-analyzer selection.
- Lane 2 TX power and diagnostic controls: `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`, `TX_PWRUP_TIME_0..5`, `DCC_CR_BANK_*`, `DCC_DAC_*`, `TX_CLK_ALIGN_TX_CTL_0`, and `TX_LBERT_CTL` describe per-power-state transmit enable/reset bits, timing delays, DCC DAC access/range/ack/address, clock alignment, and TX LBERT pattern control.
- Lane 2 RX repeated families: `DIG_RX_PWRCTL_*`, `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, `DIG_RX_ADPTCTL_*`, `DIG_RX_STAT_*`, and `DIG_MPHY_RX_*` repeat the lane 1 receiver control/status model for lane 2.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime behavior is indirect:

1. AMDGPU display or PHY code includes this generated shift/mask header with the matching DPCS 3.1.4 register offset/address header.
2. Register descriptor tables pair the DPCS register address with the field constants from this file.
3. Masked read/modify/write helpers use the `_MASK` and `__SHIFT` constants to update individual fields or decode status fields.
4. The actual state transition occurs in DPCS hardware: lane power sequencing, VCO/CDR calibration, link training diagnostics, adaptation, DCC, analog override, or statistics collection.

The represented hardware flow is typically: select ASIC-owned or software-override controls, sequence TX/RX power states and power-up timings, bring up RX AFE/clock/CDR/deserializer and TX analog paths, run VCO/CDR/DCC/adaptation calibration, optionally drive LBERT or statistics collection, and poll status/counter fields to validate lane readiness and signal quality.

## State and Persistence Behavior

The file itself has no mutable state. All state described by these macros lives in hardware registers.

The hardware state represented by this chunk includes:

- Lane power state: TX/RX P0, P0S, P1, and P2 enable/reset fields, power-up delay fields, low-speed MPHY polarity/termination/stable-clock settings, and analog clock/data/refgen/termination enables.
- Calibration state: RX VCO startup/update/settle timing, calibration reset/continuous-calibration bits, VCO FSM state, calibration done, VCO counter result, DCC DAC bank/data/range/ack/address, RX calibration DAC controls, and CDR/DPLL frequency and lock controls.
- Equalization/adaptation state: ATT, VGA, CTLE, DFE tap status, slicer levels, DAC control selection, adaptation configuration, reset configuration, CR bank access, and DFE data/error offset fields.
- Diagnostics and observability: LBERT mode/sync/error count, statistic match patterns and masks, statistic counters, sample-count done bits, valid-loss clear/control, OCLA selection, ASIC input/output mirrors, and analog test-bus measurement fields.
- Override state: digital and ASIC override inputs/outputs for TX, RX, equalization, signal detect, DCC, CDR/VCO, MPHY, phase adjustment, and analog status.

Persistence is limited to hardware register lifetime. Values can be lost or need reprogramming after GPU reset, DPCS or lane reset, display engine reset, power gating, suspend/resume, hotplug-driven retraining, or mode/link reconfiguration. Higher-level driver link state and board/silicon configuration remain the durable source of truth.

## Dependencies

This chunk depends on matching generated DPCS 3.1.4 register-address headers. Shift and mask constants alone do not identify where a register is located.

It also depends on:

- AMD display and PHY register-helper infrastructure that consumes generated `__SHIFT` and `_MASK` names for masked reads, writes, updates, and polling.
- The silicon register database used to generate this header and the companion register offset headers.
- DisplayPort/link encoder, PHY bring-up, power-management, diagnostics, and validation code that programs DPCS CR1 lane registers.
- Correct lane-instance mapping between `LANE1`/`LANE2` macro prefixes and the corresponding hardware lane addresses in generated tables.

Because this is generated silicon metadata, manual edits are risky unless synchronized with the register database, companion offset headers, and every generated register table that references these names.

## Integration Points

Primary integration points are the macro names consumed by AMDGPU register tables and masked register helpers. A consumer naming a field such as `DPCSSYS_CR1_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0__TX_P0_ANA_CLK_EN` or `DPCSSYS_CR1_LANE1_DIG_RX_ADPTCTL_CTLE_STATUS__CTLE_STATUS` relies on this header for the correct bit position and mask.

Integration surfaces include:

- Link/lane power sequencing: TX/RX P-state registers, power-up timers, MPHY low-speed controls, RX AFE/clock/CDR/deserializer enables, and TX analog clock/data/reference/termination enables.
- PHY calibration: RX VCO calibration controls/status, CDR controls/status, DPLL frequency/bounds, DCC DAC bank/data/range/ack/address fields, and RX analog calibration DAC fields.
- Link training and signal integrity: adaptation configuration, VGA/CTLE/DFE/slicer controls and status, signal-detect overrides, equalization ASIC handoff fields, and phase-adjust fields.
- Diagnostics: LBERT controls and error counters, statistic pattern matchers/counters/sample status, OCLA selection, ASIC input/output mirrors, analog status, and test-bus measurement registers.
- Multi-lane mapping: lane 1 and lane 2 have repeated receiver families but different address namespaces, so generated names must stay aligned with the companion address definitions.

## Risks and Failure Modes

- Incorrect shifts or masks can corrupt adjacent fields in a 16-bit lane register, causing failed power sequencing, CDR/VCO calibration failures, bad DPLL settings, broken DCC calibration, or unstable link training.
- Lane-prefix mistakes can compile cleanly while programming the wrong physical lane, producing asymmetric failures that only appear on particular lane-count or lane-mapping configurations.
- Override fields are especially sensitive. Writing the wrong mask can force software ownership of ASIC-controlled TX/RX/AFE/CDR/equalization signals or prevent hardware from taking control after calibration.
- Status and clear fields can have side effects. Misidentifying statistic done bits, valid-loss clear, DCC ack, calibration done, or LBERT error overflow fields can hide real failures or leave stale status latched.
- Power-state and timing fields are order and delay sensitive. Bad masks in `PSTATE` or `PWRUP_TIME` registers can leave analog supplies, clocks, deserializers, or CDR/VCO blocks enabled too early, too late, or not at all.
- Adaptation and equalization masks affect signal margin. Small field errors in CTLE, VGA, DFE, slicer, or DAC selection can present as intermittent DP training failures rather than deterministic build failures.
- This chunk starts and ends mid-register, so any final per-file report must reconcile the missing first lane 1 `RX_P2_ANA_AFE_EN__SHIFT` line and the lane 2 `PWM_CLK_STABLE_CNT` mask lines from neighboring chunks.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DPCS 3.1.4 display/PHY code builds without missing `DPCSSYS_CR1_LANE1_*` or `DPCSSYS_CR1_LANE2_*` shift/mask symbols.
- Generated-table sanity: lane 1 and lane 2 fields are paired with the correct companion DPCS register addresses and retain matching repeated-family layouts where expected.
- DP/link smoke tests: hotplug, modeset, lane-count and lane-rate changes, link retraining, suspend/resume, GPU reset, and power-gating recovery across displays that exercise CR1 lanes 1 and 2.
- PHY bring-up checks: TX/RX P-state transitions, RX AFE/clock/CDR/deserializer enable sequencing, VCO calibration done, DPLL frequency status, DCC DAC ack/status, and calibration timeout behavior.
- Signal-integrity checks: adaptation convergence, ATT/VGA/CTLE/DFE status readback, slicer offset behavior, signal detect, and CDR lock status under varying link rates and cable/sink conditions.
- Diagnostic checks: LBERT mode/error counts, statistic sample counters and match patterns, OCLA/ASIC mirror fields, analog status/readback, and MPHY PWM/termination/stable-clock fields.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create the final per-file synthesis for `dpcs_3_1_4_sh_mask.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.
