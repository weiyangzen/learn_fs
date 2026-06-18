# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 66751-69107

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for display PHY/controller registers. It contains no executable C logic; its public surface is preprocessor constants that encode DPCS register field bit positions (`__SHIFT`) and bit masks (`_MASK`).

The requested range contains 2,141 `#define` entries across 217 register groups. It starts at the mask tail for `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2`, covers most of the CR3 lane 1 digital ASIC, TX/RX power, RX calibration/adaptation/statistic, digital-to-analog, and analog TX/RX field masks, then begins the corresponding CR3 lane 2 digital ASIC field sequence. The range ends in the `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0` shift definitions; that register's masks continue in the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the DPCS register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, compose, or update that field.

Most complete register groups in this range are 16-bit DPCS register fields. The slice has one artificial boundary at the start, where `TX_PRE_CURSOR` and shift definitions for `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2` are in the previous chunk and this chunk only owns `TX_POST_CURSOR_MASK` plus the reserved high-nibble mask. It has another boundary at the end, where `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0` shifts start here and the masks continue after line 69107.

The main register-field families are:

- Lane 1 ASIC TX/RX interface fields: `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_OUT`, `RX_ASIC_IN_0/1`, `RX_EQ_ASIC_IN_0/1`, `RX_CDR_VCO_ASIC_IN_0/1`, and `RX_ASIC_OUT_0` describe request/ACK, TX acknowledge, receive-detect result, reset, invert, data enable, low-power detect, pstate, rate, width, AFE/DFE adaptation enables, CDR tracking and SSC, RX termination, alignment, EQ attenuation/VGA/CTLE/DFE taps, VCO/ref load values, RX valid, and adaptation status.
- Lane 1 digital override and observation fields: `RX_OVRD_IN_6`, `TX_OVRD_IN_5`, `TX_OVRD_OUT_1`, and `DIG_ASIC_OCLA` expose RX PWM clock/enable and termination overrides, master/other-lane clock and shift handshakes, lane-master overrides, DWORD clock sync overrides, repeated output override fields, and OCLA RX DWORD probe controls.
- Lane 1 TX power-control fields: `DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` encode analog refgen, VCM hold, analog/digital/word clocks, analog reset, serial enable, data enable, receive-detect permission, DCC compensation enable, and Vboost allowance per TX power state. `TX_PWRUP_TIME_0-5` provide staged TX bring-up timing for refgen, VCM, clocks, reset, serial/data enable, RX detect, DCC compensation, skip controls, and fast RX-detect timing.
- Lane 1 TX DCC controls: `DCC_CR_BANK_ADDR`, `DCC_CR_BANK_DATA`, `DCC_DAC_CTRL`, `DCC_DAC_RANGE`, `DCC_DAC_SEL`, `DCC_DAC_ACK`, and `DCC_DAC_ADDR` describe indirect calibration-bank addressing, DCC DAC request/update controls, range, selection, bin-hot fields, ACK, and DAC address selection.
- Lane 1 RX power, VCO calibration, CDR, DPLL, adaptation, and statistics: `DIG_RX_PWRCTL_RX_PSTATE_P0/P0S/P1/P2`, `RX_PWRUP_TIME_1-3`, `RX_VCOCAL_RX_VCO_CAL_CTRL_0-2`, `RX_VCO_CAL_TIME_0-1`, `RX_VCO_STAT_0-2`, `RX_CDR_CDR_CTL_0-4`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, `RX_DPLL_FREQ_BOUND_0/1`, `RX_ADPTCTL_ADPT_CFG_0-9`, `RST_ADPT_CFG`, `ATT/VGA/CTLE/DFE_*_STATUS`, slicer and VDAC-offset registers, `ADPT_RESET`, DAC-control select registers, CR-bank address/data, and `RX_STAT_*` registers cover RX pstate programming, clock/data/reset/slicer/adaptation enable, VCO startup/calibration timing and status, CDR bypass/tracking/rate controls, digital PLL frequency and bounds, adaptation algorithm timing/gains/modes, adaptation status readback, statistic pattern match/mask/counter controls, sample counters, valid-loss controls, and stat stop/done flags.
- Lane 1 MPHY and digital-to-analog bridge fields: `DIG_MPHY_RX_PWM_CTL`, `DIG_MPHY_RX_TERM_LS_CTL`, `DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT`, `DIG_ANA_TX_OVRD_OUT*`, TX termination-code and EQ override outputs, `DIG_ANA_RX_CTL_OVRD_OUT`, `DIG_ANA_RX_PWR_OVRD_OUT`, `DIG_ANA_RX_VCO_OVRD_OUT_0-2`, `DIG_ANA_RX_CAL`, RX DAC-control fields, RX AFE attenuation/VGA/CTLE fields, RX scope/slicer/IQ/cal-DAC/signals-change controls, `DIG_ANA_STATUS_0/1`, RX termination-code overrides, MPHY overrides, signal-detect overrides, and TX DCC DAC override outputs map digital control signals to analog PHY inputs or expose analog status.
- Lane 1 analog TX/RX fields: `ANA_TX_OVRD_MEAS`, `ANA_TX_PWR_OVRD`, `ANA_TX_ALT_BUS`, `ANA_TX_ATB1/2`, `ANA_TX_DCC_DAC`, `ANA_TX_DCC_CTRL1`, `ANA_TX_TERM_CODE`, `ANA_TX_TERM_CODE_CTRL`, `ANA_TX_OVRD_CLK`, `ANA_TX_MISC1-3`, reserved TX registers, `ANA_RX_CLK_1/2`, `ANA_RX_CDR_DES`, `ANA_RX_SLC_CTRL`, `ANA_RX_PWR_CTRL1/2`, `ANA_RX_SQ`, `ANA_RX_CAL1/2`, `ANA_RX_ATB_*`, and `ANA_RX_RESERVED1` define analog test bus selection, TX power/clock/measurement overrides, termination/DCC controls, Vref/slew/peaking/vreg and misc analog controls, RX CDR/VCO clock controls, slicer controls, RX power settings, squelch/signal-detect tuning, calibration values, and analog-test measurement forcing.
- Lane 2 digital ASIC bring-up sequence: the chunk begins `DPCSSYS_CR3_LANE2_DIG_ASIC_LANE_OVRD_IN`, TX override input/output groups, RX override input/EQ/output groups, lane ASIC input, TX ASIC input/output, RX ASIC input/EQ/VCO/output, RX override input 6, TX override input 5, TX override output 1, OCLA, and the first `TX_PSTATE_P0` shift definitions. These largely mirror the lane 1 digital ASIC field names, giving lane 2 its own request, pstate, rate, width, MPLL select, data enable, reset, serial, detect-RX, beacon, async TX, loopback, HDMI/MPHY mode, RX/TX handshakes, EQ, termination, VCO/ref-load, and OCLA field constants.

## Control Flow

This header has no runtime control flow. Its role is compile-time register metadata:

1. DCN 3.1 resource code includes `dpcs_4_2_0_offset.h` and this `dpcs_4_2_0_sh_mask.h` header.
2. Register-list and shift/mask-list macros expand token-pasted DPCS names into typed register, shift, and mask tables.
3. Runtime AMD display code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` through those tables.
4. Actual sequencing for PHY lane power, link training, CDR/VCO calibration, DCC, RX adaptation, statistics, and diagnostics is implemented in display resource, link encoder, PHY, AUX/link-training, and hardware-sequencing code outside this generated file.

The constants here describe where bits live. They do not encode access direction, write-one-to-clear behavior, self-clearing behavior, clock-domain requirements, calibration ordering, or timeout rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 DPCS lane registers:

- TX state: pstate-specific analog and digital enable bits, refgen/VCM/word-clock/reset/serial/data controls, receive-detect enable and timing, Vboost/DCC policy, TX pre/post cursor masks, termination-code and EQ override fields, DCC DAC request/update/range/selection/ACK, beacon and async-drive/data controls, loopback, lane-master and cross-lane shift/clock synchronization.
- RX state: reset, inversion, data enable, request, low-power detect, pstate/rate/width, adaptation AFE/DFE enable, CDR tracking/SSC/alignment, termination controls, EQ attenuation/VGA/CTLE/DFE taps, CDR/VCO/ref load values, RX valid/ACK/adaptation status, slicer/VDAC controls, squelch/signal-detect and IQ phase controls.
- Calibration and adaptation state: VCO calibration control/timing/status, CDR control/status, DPLL frequency/bounds, adaptation algorithm configuration, reset and status readbacks for attenuation, VGA, CTLE, DFE taps, and DAC-control selection.
- Diagnostic state: RX statistic match/data mask controls, statistic sample and count registers, valid-loss controls, OCLA enable/data controls, analog test bus and measurement-selection fields, scope/slicer debug fields, MPHY PWM/termination controls, and status/readback bits.
- Lane duplication: line 68624 starts CR3 lane 2 digital ASIC fields. These are separate hardware lane states even when field layouts mirror lane 1.

Persistence is hardware-defined. Configuration fields generally remain until reprogrammed by modeset/link-training code, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization. ACK, status, IRQ-like, statistic, calibration, and handshake fields may be latched, sampled, clear-on-write, self-clearing, or only valid while the relevant lane power and clock domains are active. This generated header does not record those semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching `ixDPCSSYS_*` offsets for the register groups described here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes both the DPCS 4.2.0 offset and shift/mask headers and uses generated list macros such as `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST` to populate link-encoder/AUX-related register tables.
- AMD display register helpers consume the populated offset/shift/mask tables when programming display PHY lanes, link encoders, AUX/DPCS access paths, HPO/DP link encoder paths, and low-level hardware sequencing.
- Firmware and hardware state machines interact with the same register fields for power-state transitions, CDR/VCO calibration, DCC compensation, receiver adaptation, analog override/debug paths, and lane handshakes.

Behaviorally, this chunk sits below the user-facing display stack. Bad constants here are observed as PHY/link failures, incorrect register dumps, broken debug paths, or lane-specific regressions rather than as normal C control-flow bugs.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while writing the wrong DPCS field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from the authoritative AMD register database, the companion offset header, silicon documentation, and firmware assumptions.
- Chunk boundaries split two register groups. `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2` is only partially represented at the start, and `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0` is only partially represented at the end. Whole-register claims need reconciliation with adjacent chunks.
- Lane 1 and lane 2 fields are similar but not interchangeable. Copying a mask into the wrong lane's register-table entry can produce a lane-local failure that may only appear on particular connectors, link widths, or routing configurations.
- Power and clock fields are sequencing-sensitive. Incorrect pstate, refgen, VCM, analog/digital clock, reset, serial/data enable, DCC, VCO, CDR, or DPLL masks can cause blank displays, link-training failure, CDR unlock, unstable clocks, high bit error rates, or suspend/resume-only failures.
- Adaptation and analog override fields are electrically sensitive. Bad attenuation, VGA, CTLE, DFE, slicer, squelch, signal-detect, termination, TX EQ, Vref, or DCC masks can degrade signal integrity while the software path appears to have completed normally.
- ACK/status/readback fields are side-effect-sensitive. Confusing input override, output override, ACK, valid, statistic, or calibration-status fields can lead to stuck waits, false success, false timeout, or misleading debug captures.
- Reserved and `NC` fields are present throughout the analog blocks. Incorrect masks that overlap reserved bits may have undocumented effects on specific ASIC revisions.
- Repeated generated lane/register families are copy-sensitive. A generator or merge error can affect only one pstate, one lane, one DFE tap, one calibration field, or one status counter while nearby groups remain correct.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build the AMDGPU display code path that includes `dcn31_resource.c`. Missing or renamed DPCS macros should fail where DPCS register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in this slice has a matching `__SHIFT`/`_MASK` pair, allowing the known boundary exceptions for `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2` and `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0`.
- Cross-check every complete `DPCSSYS_CR3_LANE1_*` and `DPCSSYS_CR3_LANE2_*` register group in this range against `dpcs_4_2_0_offset.h` for a corresponding `ixDPCSSYS_*` offset.
- Diff the generated field layout against AMD's authoritative DPCS 4.2.0 register source and nearby generated variants such as `dpcs_4_2_2_sh_mask.h` or `dpcs_4_2_3_sh_mask.h` where layouts are expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across available CR3 lane mappings, rates, widths, and power states. Expected signals are stable link training, correct pstate transitions, no stuck ACK/status bits, and no unexpected retraining.
- Run hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence and reinitialization mistakes in lane power, TX/RX reset, CDR/VCO calibration, DCC, and adaptation fields.
- Use register dumps or PHY debug traces during known-good and failing links to confirm TX/RX pstate, DCC, CDR/VCO, DPLL, adaptation, EQ, statistic, and analog override fields decode as expected.
- If available, exercise diagnostic paths for OCLA, RX statistic counters, analog test bus/readback, DCC DAC debug controls, MPHY PWM/termination controls, and loopback/ATE-style overrides.

## Cross-Chunk Notes

The previous chunk owns most of `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_2`; this chunk begins with its final masks. The next chunk should continue `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0` masks and then proceed through the rest of the lane 2 power/adaptation/analog sequence. The final per-file research document should reconcile these artificial chunk boundaries before making whole-file claims about all DPCS 4.2.0 register groups.
