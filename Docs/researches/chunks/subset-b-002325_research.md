# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 88173-90528

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask register header fragment. It contains 2,356 lines of preprocessor constants defining bit shifts and masks for DPCS CR4 lane register fields. The chunk starts in the middle of the lane 1 analog RX ATB register block, covers the bulk of lane 2 digital and analog PHY field definitions, and ends in the beginning of lane 3 digital TX override definitions.

The file is not executable code. Its purpose is to provide the bitfield ABI used by low-level display PHY programming code together with the corresponding `dpcs_4_2_0_offset.h` `ixDPCSSYS_...` register offsets. Consumers write or read hardware registers by combining an offset macro with these `__SHIFT` and `_MASK` macros.

## Purpose

The macros describe control and status surfaces for a DisplayPort/PHY lane:

- ASIC-facing lane override and normal input/output fields for TX and RX.
- TX and RX power-state templates and power-up timing.
- TX DCC/DAC calibration control.
- TX clock alignment and loopback/BERT controls.
- RX VCO calibration, DPLL/CDR, DFE/CTLE/VGA adaptation, statistics/scope counters, and loopback/BERT controls.
- Digital-to-analog override outputs for TX/RX analog controls, term codes, equalization, signal detect, MPHY behavior, and analog status.
- Analog TX and RX low-level controls for clocks, power, calibration, ATB measurement, slicers, term codes, and reserved or not-connected fields.

Most definitions are 16-bit hardware fields stored in `0x0000....L` masks. The register naming convention encodes the block hierarchy: `DPCSSYS_CR4_LANE<N>_<DIG|ANA>_<subblock>_<register>__<field>_{SHIFT|MASK}`.

## Important API Surface

This chunk exposes macros, not functions or C types. The important API is the naming/bitfield contract:

- `...__<field>__SHIFT` gives the least-significant bit for a field.
- `...__<field>_MASK` gives the field mask after shifting.
- `RESERVED_*`, `NC*`, and `RSVD_*` fields identify bits that should generally be preserved or avoided unless the hardware programming guide requires otherwise.
- Paired `*_OVRD_EN` fields gate adjacent override values. Writes to override values without asserting the matching enable bit may have no effect; writes with the enable set can bypass automatic PHY control.

Primary register groups in this chunk:

- Boundary lane 1 analog RX ATB: `DPCSSYS_CR4_LANE1_ANA_RX_ATB_REGREF`, `ATB_MEAS1..4`, `ATB_FRC`, and `ANA_RX_RESERVED1`.
- Lane 2 ASIC interface: `DIG_ASIC_LANE_OVRD_IN`, `DIG_ASIC_TX_OVRD_IN_0..5`, `DIG_ASIC_TX_OVRD_OUT(_1)`, `DIG_ASIC_RX_OVRD_IN_0..6`, `DIG_ASIC_RX_OVRD_EQ_IN_0..1`, `DIG_ASIC_RX_OVRD_OUT_0`, `DIG_ASIC_*_ASIC_IN/OUT`, and `DIG_ASIC_OCLA`.
- Lane 2 TX power/control: `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`, `TX_PWRUP_TIME_0..5`, `DCC_*`, `DIG_TX_CLK_ALIGN_TX_CTL_0`, and `DIG_TX_LBERT_CTL`.
- Lane 2 RX power/calibration/control: `DIG_RX_PWRCTL_RX_PSTATE_*`, `RX_PWRUP_TIME_*`, `RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, `RX_LBERT_*`, `RX_ADPTCTL_*`, and `RX_STAT_*`.
- Lane 2 digital-to-analog override/status: `DIG_ANA_TX_*`, `DIG_ANA_RX_*`, `DIG_ANA_SIGDET_*`, `DIG_ANA_MPHY_*`, and `DIG_ANA_STATUS_*`.
- Lane 2 direct analog controls: `ANA_TX_*` and `ANA_RX_*`.
- Boundary lane 3 digital TX override: `DPCSSYS_CR4_LANE3_DIG_ASIC_LANE_OVRD_IN` and `DIG_ASIC_TX_OVRD_IN_0..4` through the `RESET_OVRD_EN_MASK` line.

## Control Flow and Data Flow

There is no runtime control flow in this header. The effective hardware programming flow implied by the macros is:

1. Select an indirect DPCS CR register using an `ixDPCSSYS_CR4_LANE...` offset from the matching offset header.
2. Read the current 16-bit/32-bit register value when preserving reserved or unrelated fields is required.
3. Clear target bits with `_MASK`, place new field values using `__SHIFT`, and write the merged value.
4. For manual PHY programming, assert the relevant `*_OVRD_EN` or `ovrd_*` bit after setting the value field.
5. Poll status fields such as `ACK`, `VALID`, `ASM1_DONE`, `RX_VCO_CAL_DONE`, `SMPL_CNT1_DONE`, `TX_ANA_*_ACK`, or error counters to confirm hardware state.

Several groups encode multi-step flows:

- TX/RX pstate macros describe which analog and digital enables are active in power states `P0`, `P0S`, `P1`, and `P2`. Timing registers then specify waits for refgen, VCM hold, vboost disable, reset, serial enable, RX AFE/vreg/clock/CDR/deserializer, and fast-start paths.
- RX VCO calibration fields control resets, continuous calibration enable, frequency-tune start/step behavior, wait times, and status fields reporting FSM state, calibration done, DPLL reset, final counter value, and direction/correctness.
- RX adaptation fields configure AFE/DFE/CTLE/VGA enablement, thresholds, step sizes, saturation behavior, reset controls, slicer levels, DAC selections, and readback status codes.
- RX statistics/scope fields configure pattern matching, masks, sample counts, counter enables, data delay, clocking, pauses, stop/start, and counter results.
- ATB and scope fields route internal analog measurements for lab/debug visibility.

## State and Persistence

The state represented by these macros is hardware register state, not kernel-owned persistent data:

- Values persist in the PHY register file until reset, power transition, firmware/driver reprogramming, or hardware self-clear behavior changes them.
- Many fields are direct power/clock/reset enables. A bad write can immediately affect lane link state.
- Some controls are explicitly self-clearing or can disable self-clear behavior, including `DAC_CTRL_SELF_CLEAR_DISABLE`, `PHASE_ADJUST_SELF_CLEAR_DISABLE`, `AFE_UPDATE_SELF_CLEAR_DISABLE`, `RX_SCOPE_SELF_CLEAR_DISABLE`, and term/frequency tune clock self-clear disable fields.
- Status and counters such as LBERT error count, RX stat counters, VCO status, analog status, and adaptation status are volatile hardware observations.
- Reserved and NC fields are part of the ABI shape but should not be treated as stable software state.

## Dependencies and Integration Points

This chunk depends on the rest of the generated AMD register headers:

- `dpcs_4_2_0_offset.h` supplies the matching `ixDPCSSYS_CR4_LANE2_...` offsets for the register names defined here.
- Other DPCS 4.2.x mask/offset headers carry nearly identical lane/register surfaces for related ASIC revisions.
- AMD display code normally reaches these registers through DC/DM register access helpers and generated include layering rather than by including this chunk in isolation.

Integration-sensitive areas:

- Lane numbering is embedded in every macro. Lane 2 definitions must be paired with lane 2 offsets; lane 1 and lane 3 fragments in this chunk are boundary spillover and should not be merged into lane 2 programming tables by accident.
- The register surface is duplicated by lane, so generated consistency across lanes matters. Manual edits can silently break one lane while leaving others correct.
- Power sequencing fields interact with link training and PHY bring-up/tear-down code. These are not ordinary software config flags.
- Debug/test controls such as BERT, OCLA, ATB, scope, loopback, and MPHY overrides may conflict with normal display link operation if left enabled.

## Risks

- Incorrect masks or shifts can corrupt adjacent fields, including reserved bits, because callers depend on these constants for read-modify-write operations.
- Setting override enables can bypass hardware state machines for TX/RX clocks, data enable, CDR, VCO, equalization, term codes, signal detect, and analog power. This can cause link loss, unstable training, or bad signal quality.
- Power-state and timing values are highly hardware-specific. Applying lane 2 or DPCS 4.2.0 definitions to a different lane/revision without matching offsets can program the wrong register.
- Self-clearing control bits are easy to mishandle in polling code. A test may pass if the bit clears quickly but fail if software later disables self-clear or assumes the bit remains set.
- Status counters and adaptation readbacks are volatile. Tests must tolerate hardware timing and should not expect deterministic values without a controlled link/test pattern.
- The chunk boundaries split register groups: lane 1 `ANA_RX_ATB_REGREF` lacks its comment header in this slice, and lane 3 `DIG_ASIC_TX_OVRD_IN_4` is incomplete beyond the final mask present here. Merge tooling must rely on line ranges and adjacent chunks for full-file context.

## Test Signals

Useful validation signals for code using these definitions:

- Build-time: headers compile cleanly, no duplicate macro warnings in the intended include order, and generated offset/mask names match exactly.
- Static consistency: for each field, `MASK >> SHIFT` should fit the documented field width and should not overlap unrelated fields except reserved ranges.
- Register-pair consistency: every lane 2 mask register in this chunk should have a matching `ixDPCSSYS_CR4_LANE2_...` offset in `dpcs_4_2_0_offset.h`.
- Lane consistency: corresponding lane 1/lane 2/lane 3 groups should preserve identical field layouts where the hardware is lane-replicated.
- Runtime hardware smoke tests: link bring-up, link training, display modeset, suspend/resume, hotplug, and power-state transitions should not regress.
- PHY/debug tests: LBERT mode/sync/error count, OCLA clock/data enable, RX stat sample counters, VCO calibration done/status, adaptation `ASM1_DONE` statuses, and analog status readbacks are direct indicators that these bit definitions still map to hardware as expected.

## Summary

This chunk is a generated hardware ABI map for DPCS CR4 lane PHY registers, dominated by lane 2. It has no functions or data structures, but it is critical because all low-level display PHY register programming depends on these exact bit positions. The highest-risk surfaces are override enables, power-state templates, VCO/CDR calibration, RX adaptation, and volatile debug/status counters.
