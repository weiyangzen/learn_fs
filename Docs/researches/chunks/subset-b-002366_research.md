# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 69114-71473

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY register fields. It contains no executable C logic. Its exported surface is a large set of preprocessor constants that encode bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCS indirect hardware registers.

The requested range contains 2,137 `#define` entries across 2,360 lines and 223 register comment markers. It is entirely inside the `dpcssys_cr3_rdpcstxcrind` register window and covers CR3 lane-local PHY control/status fields. The chunk starts in the mask half of `DPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1`, continues through the rest of lane 2 digital ASIC, TX power, RX power, VCO calibration, CDR/DPLL, RX adaptation, RX statistic, MPHY, digital-to-analog override, and analog TX/RX fields, then starts lane 3 and reaches the first masks of `DPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1`.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The interface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, compose, decode, or update that field.

The main register-field families are:

- Lane 2 digital ASIC tail and PHY handshakes: the range begins with the final masks for `DPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1`, including TX async enable/data/driver enable and VREG driver bypass fields whose shift definitions are in the previous chunk. It then covers `TX_ASIC_IN_2`, `TX_ASIC_OUT`, RX ASIC input/output words, RX equalization ASIC inputs, RX CDR/VCO ASIC inputs, RX override input 6, TX override input/output words, and OCLA enable fields. These macros describe reset/request/data enable, low-power detect, pstate/rate/width, main/pre/post cursor values, RX adaptation enables, RX termination, TX/RX acknowledgements, and lane override handshakes.
- Lane 2 TX power and timing: `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_*` defines TX power-state templates for P0, P0s, P1, and P2 plus power-up timing registers. The fields control analog reference generation, VCM hold, analog and word clocks, reset, serial enable, digital clock enable, data enable, RX detect allowance, VBOOST allowance, DCC compensation calibration, reference-clock enable timing, VCM/VBOOST timing, RX detect timing, and serial-enable timing.
- Lane 2 TX DCC and TX diagnostic controls: `DCC_CR_BANK_ADDR`, `DCC_CR_BANK_DATA`, `DCC_DAC_CTRL`, `DCC_DAC_RANGE`, `DCC_DAC_SEL`, `DCC_DAC_ACK`, and `DCC_DAC_ADDR` define the indirect DCC bank/DAC interface. `TX_CLK_ALIGN_TX_CTL_0` defines 16b/20b shift-count and FIFO-bypass controls, while `TX_LBERT_CTL` defines LBERT mode, error trigger, and pattern fields.
- Lane 2 RX power, VCO calibration, CDR, and DPLL fields: `DIG_RX_PWRCTL_RX_PSTATE_*` and `RX_PWRUP_TIME_*` define RX power-state templates and timing. `RX_VCOCAL_*` controls VCO calibration request, bypass, force, reference-load and VCO-load values, timing, result/status, and binary-window fields. `RX_CDR_*`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_*` expose clock/data recovery, SSC/bypass/update behavior, gain/frequency controls, status, and DPLL frequency boundaries.
- Lane 2 RX adaptation and equalization state: `DIG_RX_ADPTCTL_ADPT_CFG_0` through `ADPT_CFG_9`, reset configuration, ATT/VGA/CTLE/DFE tap status, DFE data/error VDAC offsets, slicer controls, error slicer level, adaptation reset, DAC control selectors, and adaptation CR bank address/data fields describe RX equalization policy and observed adaptation values.
- Lane 2 RX statistic engine: `DIG_RX_STAT_*` registers define sample/load values, data masks, pattern match controls, statistic/correlation source selection, sample counters, statistic counters 0 through 6, calibration-comparison clock control, additional match controls, statistic control 2, and stop control. These are used for PHY debug, pattern matching, and adaptation/statistic sampling rather than normal filesystem-style state.
- Lane 2 MPHY and digital analog override outputs: `DIG_MPHY_RX_PWM_CTL`, `DIG_MPHY_RX_TERM_LS_CTL`, and `DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT` describe MPHY PWM and low-speed termination controls. `DIG_ANA_*` fields expose digital override outputs into analog TX/RX logic: TX override values and enables, TX termination-code overrides, TX EQ overrides, RX control and power overrides, RX VCO overrides, RX calibration/DAC/slicer/AFE/CTLE/scope/IQ controls, analog-change enables, analog status words, RX termination-code overrides, MPHY overrides, signal-detect overrides, TX DCC DAC overrides, and a second TX override word.
- Lane 2 analog TX/RX registers: `DPCSSYS_CR3_LANE2_ANA_TX_*` and `DPCSSYS_CR3_LANE2_ANA_RX_*` describe analog-side measurement overrides, power overrides, alternate/ATB buses, TX DCC DAC and DCC control, TX termination code and control, TX override clocks, TX miscellaneous/reserved words, RX clock controls, CDR deserializer controls, slicer controls, RX power controls, squelch, RX calibration, ATB register/reference/measurement controls, ATB force, and RX reserved state.
- Lane 3 partial digital ASIC and TX power window: the chunk starts lane 3 at `DPCSSYS_CR3_LANE3_DIG_ASIC_LANE_OVRD_IN` and covers lane override, TX override inputs 0 through 5, TX override outputs, RX override output 0, lane ASIC input, TX ASIC inputs/outputs, RX ASIC output 0, TX power-state templates, TX power-up timing, TX DCC bank/DAC interface, TX clock alignment, and TX LBERT.
- Lane 3 partial RX statistic window: the range ends inside `DPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1`. It fully covers `RX_STAT_LD_VAL_1`, `RX_STAT_DATA_MSK`, and `RX_STAT_MATCH_CTL0`; for `MATCH_CTL1`, the chunk includes the shift fields and the first three masks, while the remaining masks and later lane 3 RX statistic controls are in the next chunk.

Most masks in this range are 16-bit-style values with an `L` suffix, matching the DPCS indirect register width used by these lane-local CR3 blocks. Several registers are full 16-bit data/address words, while many fields are single-bit enables, override-enable bits, clear/start/update bits, acknowledge bits, or compact multi-bit analog calibration values.

## Control Flow

This header has no runtime control flow. It participates in compile-time register access setup:

1. AMD display code for the matching DPCS/DCN generation includes the DPCS 4.2.2 offset header and this shift/mask header.
2. Version-specific register, shift, and mask tables use generated names from this header and companion `ixDPCSSYS_*` offsets.
3. Runtime driver code uses register helpers and those tables to read, write, set, clear, poll, or decode hardware fields during PHY bring-up, link training, modeset, diagnostics, interrupt/debug handling, low-power transitions, suspend/resume, and reset recovery.
4. Hardware and firmware state machines perform the actual lane sequencing; this header only names bit positions and masks.

The macros do not encode access type, reset value, polling order, write-one-to-clear behavior, self-clearing behavior, clock-domain restrictions, power-domain validity, or whether a field is read-only, write-only, or reserved.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 lane 2 and lane 3 registers:

- Lane control state includes TX/RX reset, request, data-enable, disable, low-power-detect, pstate, rate, width, MPLL/clock selection, TX cursor coefficients, TX/RX acknowledgement, detect-RX result, loopback/test pattern, OCLA, and lane-master/shift synchronization fields.
- Power sequencing state includes TX/RX power-state templates, reference generator and clock enables, analog reset/serial/data enables, VCM hold, VBOOST, RX detect allowance, DCC compensation calibration, and the timing counters used to sequence those transitions.
- Calibration state includes TX DCC bank/DAC request and acknowledgement, RX VCO calibration request/force/bypass/load/status values, RX CDR/DPLL control/status, RX adaptation policy and status, DFE tap status, slicer and VDAC offsets, RX analog calibration controls, and ATB measurement/force state.
- Statistic/debug state includes RX statistic pattern masks, match controls, source selectors, sample counters, statistic counters, calibration-comparison clock control, stop/start controls, LBERT mode/pattern/error trigger, OCLA enables, analog status words, signal detect overrides, and MPHY PWM/termination debug controls.
- Analog state includes digital override outputs into analog TX/RX blocks, TX/RX termination codes, TX EQ and DCC DAC controls, RX AFE/CTLE/slicer/IQ/phase controls, squelch, RX clocks, RX power controls, and analog test bus selection.

Persistence is hardware-defined. Configuration and override fields generally last until another modeset/link-training sequence, PHY power transition, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization changes them. Status, ACK, statistic, calibration, start/update, clear, and handshake fields may be latched, sampled, write-one-to-clear, self-clearing, or valid only when the corresponding lane power and clocks are active. This generated header does not specify those behaviors.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the matching CR3 register offsets. In that file, the relevant address block is the CR3 DPCS TX/RX indirect register window.
- Lane 2 registers covered here map from the tail of `ixDPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1` at `0x1212` through `ixDPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_2` at `0x1213`, TX power control at `0x1220` through `0x1232`, RX power/VCO/CDR/DPLL/adaptation/statistics at `0x1240` through `0x1297`, digital analog override outputs at `0x12a0` through `0x12c4`, and analog TX/RX registers at `0x12e0` through `0x12ff`.
- Lane 3 starts at `ixDPCSSYS_CR3_LANE3_DIG_ASIC_LANE_OVRD_IN` at `0x1300`, covers the partial digital ASIC region through `0x131e`, TX power control through `ixDPCSSYS_CR3_LANE3_DIG_TX_LBERT_CTL` at `0x1332`, and reaches RX statistic registers from `0x1380` through `ixDPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1` at `0x1383`.
- AMD display link encoder, PHY sequencing, link-training, mode-setting, hotplug, low-power, debug, and reset-recovery paths consume these constants indirectly through generated register tables and register helper macros.
- Firmware/hardware state machines share ownership of many of these fields, especially reset/request handshakes, TX/RX power-state sequencing, RX adaptation, DCC and VCO calibration, CDR/DPLL lock behavior, MPHY PWM/termination paths, analog override paths, and RX statistic/debug sampling.

Behaviorally, this chunk sits below user-facing display code. It describes the bit layout needed to configure, override, and observe CR3 lane 2 and early lane 3 PHY operation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk starts mid-register. `DPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1` shift definitions and early masks are in the previous chunk; this range only contains the later masks for TX async/VREG/reserved fields.
- The chunk ends mid-register. `DPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1` still has `PTTRN_CR1A_ADPT_EN_MASK` and `RESERVED_15_12_MASK` immediately after the requested range, and the rest of lane 3 RX statistic controls continue in the next chunk.
- Repeated lane layouts are copy-sensitive. Lane 2 and lane 3 names must pair with their matching `0x12xx` and `0x13xx` offsets; a generator issue can affect one lane while neighboring lanes appear correct.
- Status, request, acknowledge, update, start, clear, and mask-style fields have similar names but different hardware semantics. Using a status mask as a writable control mask, or assuming a request bit is persistent configuration, can create stuck handshakes or misleading debug reads.
- Power-state and timing fields are sequencing-sensitive. Incorrect masks around TX/RX P0/P0s/P1/P2 templates, VCM/VBOOST timing, RX detect allowance, analog reset, data enable, or serial enable can cause link bring-up failures or unstable low-power transitions.
- Calibration and adaptation fields are analog-sensitive. Bad masks for DCC DAC selection, RX VCO load/status, CDR/DPLL controls, AFE/VGA/CTLE/DFE tap status, slicer levels, IQ/phase adjustment, squelch, or termination codes can produce rate-specific display failures, poor eye margins, or incorrect compliance behavior.
- OCLA, LBERT, statistic, ATB, MPHY, and manufacturing-style override fields are intended for debug/test/diagnostic flows. Accidentally enabling them during normal operation can change lane behavior without obvious high-level driver state.
- Reserved masks are emitted. Consumers should not treat reserved fields as safe software-owned configuration fields unless hardware documentation explicitly says so.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that complete fields in this range have consistent `__SHIFT` and `_MASK` pairs, allowing the known boundary exceptions for `DPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1` at the start and `DPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1` at the end.
- Cross-check every complete register group against `dpcs_4_2_2_offset.h`, especially lane-local offset spacing: lane 2 around `0x1200` and lane 3 around `0x1300`.
- Diff against AMD's source register database and nearby DPCS generated variants where lane layouts are expected to match.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, lane counts, and power states. Expected signals are stable link training, completed RX adaptation/calibration, no stuck reset/request handshakes, and no unexpected lane debug/statistic anomalies.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in TX/RX power control, VCO calibration, CDR/DPLL, RX adaptation, statistic/debug, MPHY, and analog override fields.
- Use register dumps or PHY debug traces during failing links to confirm that TX/RX ACKs, DCC DAC ACK, RX VCO status, CDR status, DPLL frequency bounds, adaptation status, DFE tap values, slicer offsets, statistic counters, analog status words, and ATB/MPHY/OCLA/LBERT controls decode correctly.
- Exercise diagnostic paths where available: OCLA, LBERT, RX statistic matching, DCC bank/DAC access, VCO calibration debug, CDR/DPLL debug, MPHY PWM/termination overrides, analog test bus measurements, signal-detect overrides, and manufacturing/test override flows.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1` and earlier lane 2 digital ASIC override/input fields. This chunk finishes the lane 2 register window through `DPCSSYS_CR3_LANE2_ANA_RX_RESERVED1`, then starts lane 3 and covers its early digital ASIC, TX power/DCC/LBERT, and initial RX statistic registers. The next chunk should finish `DPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1` and continue the rest of lane 3 RX statistic/debug and later lane 3 PHY fields. The final per-file research document should reconcile these artificial boundaries before making whole-file claims about all DPCS 4.2.2 CR3 lane registers.
