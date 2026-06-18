# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 127330-129728

## Scope

This chunk is part of the generated DCN 4.1.0 ASIC shift/mask header used by the AMD display driver. It contains preprocessor constants only: every hardware field is represented by a `...__SHIFT` bit offset and a matching `..._MASK` value. There are no C functions, structs, branches, allocations, locks, or direct MMIO operations in this line range.

The range starts in `DPCSSYS_CR3_LANE0` transmit power-control definitions, continues through lane 0 RX statistics and TX analog override/trim metadata, crosses into `DPCSSYS_CR3_LANE1` ASIC interface definitions, and ends at the beginning of lane 1 digital analog status. It is lane-level metadata for CR3 DPCS/DPCSSYS PHY registers.

## Purpose

The purpose of this chunk is to publish exact bit positions and masks for CR3 lane 0 and lane 1 PHY-side register fields. Runtime AMD display code includes this header with matching generated offset headers, then uses register-helper macros to build read/modify/write operations without embedding raw bit arithmetic in driver logic.

Important covered areas:

- `DPCSSYS_CR3_LANE0_DIG_TX_PWRCTL_*`: TX pstate programming for P0, P0S, P1, and P2; TX power-up timing; RX-detect timing; TX DCC CR-bank and DAC control; clock alignment; and TX LBERT controls.
- `DPCSSYS_CR3_LANE0_DIG_RX_STAT_*`: RX statistic load values, data masks, pattern-match controls, statistic source and counter controls, sample counters, statistic counters, calibration comparator clock control, and statistic stop.
- `DPCSSYS_CR3_LANE0_DIG_ANA_*` and `DPCSSYS_CR3_LANE0_ANA_TX_*`: TX analog override outputs, TX termination and equalization override fields, TX DCC DAC override fields, analog TX measurement, power, alternate bus, ATB, DCC, termination, mux, voltage-regulator, and reserved trim fields.
- `DPCSSYS_CR3_LANE1_DIG_ASIC_*`: lane 1 digital ASIC override inputs/outputs and live ASIC input/output mirrors for lane loopback, TX/RX request, reset, pstate, rate, width, clock ready, inversion, data enable, detect-RX, HDMI mode, EQ, CDR/VCO, low-power, PWM, termination, and multi-lane clock/shift handshakes.
- `DPCSSYS_CR3_LANE1_DIG_TX_PWRCTL_*` and `DIG_RX_PWRCTL_*`: lane 1 TX and RX pstate definitions plus power-up timing for analog clocks, data, serial/deserial, reset, DCC, AFE, CDR, VCO, and digital clocks.
- `DPCSSYS_CR3_LANE1_DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, and `DIG_RX_ADPTCTL_*`: VCO calibration, CDR controls/status, DPLL frequency bounds, adaptation configuration/status, DFE VDAC offsets, slicer controls, reset, and CR-bank access.
- `DPCSSYS_CR3_LANE1_DIG_RX_STAT_*`, `DIG_MPHY_RX_*`, and `DIG_ANA_*`: RX statistic controls, M-PHY PWM/low-speed termination timing, TX/RX analog override outputs, RX calibration DACs, AFE/CTLE, scope, slicer, IQ phase adjust, update strobes, and the first analog status bits.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask inside the 16-bit register represented by this part of the DPCS register map.
- The `DPCSSYS_CR3_LANE0` and `DPCSSYS_CR3_LANE1` prefixes are part of the ABI. They bind otherwise similar repeated lane fields to a specific CR3 lane instance.

Notable field families:

- TX pstate fields: `TX_P*_ANA_REFGEN_EN`, `TX_P*_ANA_VCM_HOLD`, `TX_P*_ANA_CLK_EN`, `TX_P*_ANA_WORD_CLK_EN`, `TX_P*_ANA_RESET`, `TX_P*_ANA_SERIAL_EN`, `TX_P*_DIG_CLK_EN`, `TX_P*_DATA_EN`, `TX_P*_ALLOW_RXDET`, `TX_P2_ALLOW_VBOOST`, and `TX_P*_ANA_DCC_COMP_CAL_EN`.
- Power sequencing and DCC: `TX_REFGEN_EN_TIME`, `TX_CLK_EN`, `TX_VCM_HOLD_TIME_*`, `TX_VBOOST_DIS_TIME_*`, `FAST_TX_RXDET`, `TX_RESET_TIME`, `TX_SERIAL_EN_TIME`, `DCC_CR_BANK_ADDR/DATA`, `DCC_DAC_CTRL`, `DCC_DAC_RANGE`, `DCC_DAC_SEL`, `DCC_DAC_ACK`, and `DCC_DAC_ADDR`.
- RX pstate and timing: lane 1 `RX_P*_ANA_*`, `RX_P*_DIG_CLK_EN`, `RX_P*_DATA_EN`, `RX_P*_CLK_RDY`, `RX_P*_ANA_DCC_COMP_CAL_EN`, `RX_VCO_EN_TIME`, `RX_AFE_EN_TIME`, `RX_CDR_EN_TIME`, `RX_DESERIAL_EN_TIME`, `RX_DATA_EN_TIME`, and `RX_ADPT_EN_TIME`.
- ASIC override and mirror registers: `DIG_ASIC_TX_OVRD_IN_*`, `RX_OVRD_IN_*`, `RX_OVRD_EQ_IN_*`, `TX_OVRD_OUT*`, `RX_OVRD_OUT_0`, `LANE_ASIC_IN`, `TX_ASIC_IN_*`, `TX_ASIC_OUT`, `RX_ASIC_IN_*`, `RX_EQ_ASIC_IN_*`, `RX_CDR_VCO_ASIC_IN_*`, and `RX_ASIC_OUT_0`.
- Link, training, and diagnostic controls: `TX_LBERT_CTL`, `RX_LBERT_CTL`, `RX_LBERT_ERR`, `RX_ALIGN_XAUI_COMM_MASK`, `TX_CLK_ALIGN_TX_CTL_0`, `DIG_ASIC_OCLA`, and RX statistic match/count registers.
- Calibration and recovery: `RX_VCO_CAL_CTRL_*`, `RX_VCO_CAL_TIME_*`, `RX_VCO_STAT_*`, `CDR_CTL_*`, `CDR_STAT`, `RX_DPLL_FREQ`, `RX_DPLL_FREQ_BOUND_*`, and `ADPT_CFG_*`.
- Analog override and trim: TX override, termination, equalization, DCC DAC, ATB, mux, VREG, RX control/power/VCO override, RX calibration DAC, AFE, CTLE, scope, slicer, IQ phase, and update-enable registers.

## Control Flow and Runtime Integration

There is no executable control flow in this header. Runtime behavior is indirect:

1. DCN 4.1.0 display and PHY source includes generated register offset headers together with this shift/mask header.
2. Register tables are assembled with macro patterns such as `SR`, `SRI`, `SF`, `FN`, or `FD`, pairing address constants with these field constants.
3. Display core, link encoder, DPCS, and PHY code calls register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, and `REG_WAIT`.
4. The helpers combine register addresses, shift values, and masks to isolate or update only the requested hardware fields.
5. Actual state transitions happen in CR3 lane hardware registers. This file only provides compile-time metadata for those operations.

The represented programming flow is generally: select a CR3 lane, set TX/RX rate/width/pstate and power sequencing, optionally force override-enable fields, program analog trims or calibration parameters, start VCO/CDR/DPLL/adaptation/statistic operations, then poll status, counter, done, valid, ack, or error fields.

## State and Persistence Behavior

The header has no mutable state and persists no runtime data. All state described by the macros is hardware register state.

The represented hardware state includes:

- Power state: pstate-specific enables and resets for TX and RX analog/digital clocks, refgen, VCM hold, serial/deserial blocks, data paths, AFE, CDR, VCO, and DCC calibration.
- Override state: value plus `*_OVRD_EN` fields can force TX/RX request, reset, pstate, rate, width, data enable, inversion, clock readiness, HDMI mode, detect-RX, EQ, CDR tracking, low-power, PWM, termination, clock-shift, and analog controls.
- Calibration state: VCO calibration control/timing/status, CDR frequency tune, DPLL frequency and bounds, DCC DAC request/ack/update, RX adaptation settings and done bits, slicer controls, VDAC offsets, and calibration DAC routing.
- Diagnostic state: LBERT mode/error state, OCLA enables, RX statistic pattern masks, sample windows, statistic source selection, counter enables, sample-done bits, and statistic counters.
- Analog trim state: TX termination, equalization leg controls, DCC, ATB routing, VREG, RX AFE/CTLE, slicer, scope, IQ phase, and update strobes.

Persistence is limited to the hardware register lifetime. Values may be reset by GPU reset, display engine reset, lane reset, PHY power-gating, suspend/resume, hotplug retraining, mode set, or DPCS reinitialization. Higher-level driver code must remain the source of truth for reprogramming these registers.

## Dependencies

This chunk depends on the matching DCN 4.1.0 generated offset headers. Shift/mask macros alone do not identify MMIO or indirect-register addresses.

Other dependencies include:

- AMD display register-helper infrastructure that consumes generated field macros.
- DCN 4.1.0 DPCS/DPCSSYS hardware specifications and register-generation inputs.
- Link encoder and PHY programming code for DP/HDMI/USB-C lane bring-up, link training, power management, diagnostics, and recovery.
- Register table generation that keeps `CR3`, `LANE0`, and `LANE1` prefixes aligned with the corresponding address offsets.
- Debug and validation tools that inspect LBERT, OCLA, VCO/CDR/DPLL, RX adaptation, RX statistic, DCC, ATB, and analog status fields.

Because this is generated silicon metadata, manual edits are high risk unless synchronized with the hardware register database and the companion offset header.

## Integration Points

The primary integration point is the macro-name ABI between generated headers and AMD display hardware code. A consumer naming a field such as `DPCSSYS_CR3_LANE1_DIG_RX_CDR_CDR_CTL_0__CDR_FREQ_UPDATE` or `DPCSSYS_CR3_LANE0_DIG_TX_PWRCTL_TX_PSTATE_P2__TX_P2_ALLOW_VBOOST` relies on the corresponding shift and mask here to touch the correct bits.

Protocol and subsystem integration surfaces include:

- DP/HDMI PHY setup: TX/RX rate, width, pstate, data enable, clocking, inversion, HDMI mode, cursor/equalization, termination, and detect-RX controls.
- Link training and recovery: VCO calibration, CDR tracking and SSC controls, DPLL bounds, RX adaptation, AFE/CTLE/DFE status, slicer controls, and valid/ack status.
- Power management: P0/P0S/P1/P2 lane states, fast-start and wait-skip bits, clock/data/serial enable timing, DCC DAC handshakes, and low-power entry/exit behavior.
- Multi-lane coordination: lane master selection, repeater enable, other-lane digital clock state, clock-shift request/ack signals, and TX dword clock sync override.
- Diagnostics: TX/RX LBERT, RX statistic counters, calibration compare clock control, OCLA clock/data enables, ATB routing, scope controls, and analog status bits.

## Risks and Failure Modes

- Incorrect shifts or masks can corrupt adjacent 16-bit register fields. In this area that can break pstate sequencing, analog clocking, TX output, RX CDR lock, VCO calibration, or adaptation.
- Lane-prefix mistakes are particularly risky because lane 0 and lane 1 contain many repeated field names. A prefix/offset mismatch can affect only specific link widths or physical lane assignments.
- Stale override-enable fields can pin hardware state and defeat normal link-training, calibration, power-management, or recovery flows.
- Self-clearing and handshake fields such as update clocks, request/ack bits, reset bits, sample start/stop, and calibration strobes require correct write semantics. Treating them as persistent configuration can wedge hardware flows or hide failures.
- Analog trim fields are silicon-sensitive. Bad metadata for termination, equalization, DCC DAC, VREG, AFE, CTLE, slicer, IQ phase, or VCO/CDR tune fields can produce intermittent failures tied to board, cable, sink, rate, temperature, or power state.
- High-bit masks such as `0x8000L` are common. Consumers should avoid signed narrow arithmetic assumptions when composing register values.
- The chunk begins and ends inside larger repeated lane blocks. Final per-file conclusions need neighboring chunks to reconstruct the full CR3 lane map.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DCN 4.1.0 display code builds without missing or renamed `__SHIFT`/`_MASK` macros.
- Register-table sanity: generated CR3 lane 0 and lane 1 register tables match companion offsets and preserve expected lane ordering.
- Display link smoke tests: DP and HDMI bring-up across supported rates, lane counts, bit depths, connectors, and link widths.
- Link-training diagnostics: TX detect-RX result, TX ack, RX ack/valid, VCO calibration done/correct/up, CDR frequency update, DPLL bound status, and adaptation done/status fields.
- Power-management coverage: P0/P0S/P1/P2 transitions, suspend/resume, hotplug retraining, GPU reset, lane reset, and fast/normal lane power-up timing.
- PHY tuning validation: TX main/pre/post cursor, termination, DCC DAC request/ack, RX AFE/CTLE/DFE settings, slicer controls, IQ phase adjust, and analog status readback.
- Diagnostic paths: TX/RX LBERT error counts and overflow, RX statistic pattern/counter operation, OCLA visibility, scope controls, ATB routing, and calibration comparator clock behavior.
- Multi-lane tests: one-lane, two-lane, and four-lane configurations to catch lane-index, master-lane, or cross-lane clock/shift mismatches.

## Chunk Notes

This chunk starts at `DPCSSYS_CR3_LANE0_DIG_TX_PWRCTL_TX_PSTATE_P0` and ends after the first `DPCSSYS_CR3_LANE1_DIG_ANA_STATUS_0` fields. Neighboring chunks are needed for the complete CR3 lane 0 and lane 1 register maps before a final per-file report is produced.
