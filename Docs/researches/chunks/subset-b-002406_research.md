# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 48596-51027

## Scope and Purpose

This chunk is part of AMDGPU's generated DPCS 4.2.3 shift/mask register metadata. It defines C preprocessor constants for bit shifts and bit masks in a contiguous slice of `DPCSSYS_CR2` display PHY/DPCS registers. The definitions are data-only: they do not execute code, allocate state, or implement register programming sequences by themselves. Their purpose is to provide the field layout used by AMD display register helpers when paired with the matching address definitions in `dpcs_4_2_3_offset.h`.

The covered range starts in the lane-2 analog TX/RX tail, covers most lane-3 digital/analog TX control and status fields, covers raw common (`RAWCMN`) digital PLL/common control fields, and begins raw lane 0 (`RAWLANE0`) PCS/FSM/IRQ/PMA/TX-control definitions. These names describe a C20/DPCS-style PHY view for clocking, TX/RX lane control, link training helper paths, analog test bus selection, DCC/termination/equalization controls, PHY micro-FSM status, interrupt latches and clear bits, and PCS/PMA override handshakes.

The mapped work item is `subset-b-002406`, chunk index 21 for this source file, with source lines 48596-51027 and output path `Docs/researches/chunks/subset-b-002406_research.md`.

## Important API Surface

This header exposes macros, not functions or types. The practical API is the generated naming contract:

- `DPCSSYS_CR2_<register>__<field>__SHIFT` gives the least-significant bit position for a field.
- `DPCSSYS_CR2_<register>__<field>_MASK` gives the already-shifted field mask.
- Register comment markers such as `//DPCSSYS_CR2_RAWLANE0_DIG_PMA_XF_TX_OVRD_OUT` delimit each register's field block.
- The corresponding register address names are in `dpcs_4_2_3_offset.h` with `ixDPCSSYS_CR2_*` names; for example this source tree maps `ixDPCSSYS_CR2_LANE2_ANA_TX_ATB1` to `0x12e3`, `ixDPCSSYS_CR2_RAWLANE0_DIG_PMA_XF_TX_OVRD_OUT` to `0x3064`, and `ixDPCSSYS_CR2_RAWLANE0_DIG_TX_CTL_TX_FSM_CTL` to `0x3080`.

Consumers normally do not refer to these constants manually. The AMD display code folds generated shifts and masks into register tables via macros such as `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`, then uses the normal DC register access helpers to update fields. In this tree, `dcn316_resource.c` includes both `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`, defines DPCS base segments, and appends `DPCS_DCN31_REG_LIST(id)` to link-encoder register tables.

## Register Families Covered

### Lane 2 Analog Tail

The first part completes `DPCSSYS_CR2_LANE2_ANA_TX_*` and `DPCSSYS_CR2_LANE2_ANA_RX_*` definitions:

- TX analog test bus and measurement selection: `ANA_TX_ATB1`, `ANA_TX_ATB2`, `ANA_TX_ALT_BUS`.
- TX DCC and termination controls: `ANA_TX_DCC_DAC`, `ANA_TX_DCC_CTRL1`, `ANA_TX_TERM_CODE`, `ANA_TX_TERM_CODE_CTRL`.
- TX clock and miscellaneous analog knobs: `ANA_TX_OVRD_CLK`, `ANA_TX_MISC1`, `ANA_TX_MISC2`, `ANA_TX_MISC3`.
- RX clock/CDR/slicer/power/squelch/calibration controls: `ANA_RX_CLK_1`, `ANA_RX_CLK_2`, `ANA_RX_CDR_DES`, `ANA_RX_SLC_CTRL`, `ANA_RX_PWR_CTRL1`, `ANA_RX_PWR_CTRL2`, `ANA_RX_SQ`, `ANA_RX_CAL1`, `ANA_RX_CAL2`.
- RX analog test bus and measurement controls: `ANA_RX_ATB_REGREF`, `ANA_RX_ATB_MEAS1` through `ANA_RX_ATB_MEAS4`, and `ANA_RX_ATB_FRC`.
- Reserved or no-connect placeholders: `ANA_TX_RESERVED2` through `ANA_TX_RESERVED4` and `ANA_RX_RESERVED1`.

Most of these are 16-bit CR-style fields. Upper byte reservations commonly use `RESERVED_15_8_MASK 0xFF00L`; low-byte functional fields include one-bit controls and small multi-bit selectors. This is important because register writes must preserve reserved bits unless hardware documentation explicitly requires a forced value.

### Lane 3 ASIC/Digital Interface

The chunk then switches to `DPCSSYS_CR2_LANE3_DIG_ASIC_*` blocks. These define override inputs and ASIC-observed outputs for lane-level, TX, and RX control:

- `LANE_OVRD_IN` covers serial and parallel loopback control plus an override enable path.
- `TX_OVRD_IN_0` through `TX_OVRD_IN_5` cover TX request, pstate, rate, width, MPLL selection, data enable, reset, receiver-detect request, voltage/current boost, beacon, equalization pre/main/post cursor values, termination calibration, DCC, and TX common-mode controls.
- `TX_OVRD_OUT` and `TX_OVRD_OUT_1` expose or override output-side handshake and status-style fields such as ACKs, data enable, asynchronous mode, DCC, EQ update, RX detect result, and TX-on state.
- `RX_OVRD_OUT_0` carries RX request/reset/rate/pstate/adaptation and data enable override outputs.
- `LANE_ASIC_IN`, `TX_ASIC_IN_*`, `TX_ASIC_OUT`, and `RX_ASIC_OUT_0` mirror the non-override ASIC-side versions of the same lane/TX/RX interface signals.

The common pattern is value-plus-enable pairing: a `*_OVRD_VAL` or functional value field is adjacent to a `*_OVRD_EN` bit. Bad pair programming can leave a lane pinned in an override state or write a value that hardware ignores because the enable bit is not asserted.

### Lane 3 TX Power, DCC, RX Statistics, and Analog Bridge

The lane-3 middle section defines:

- TX power-state profiles: `TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2`, with per-state TX power, data, reset, receiver-detect, voltage boost, current boost, beacon, and power-good/DCC timing fields.
- TX power-up timing registers: `TX_PWRUP_TIME_0` through `TX_PWRUP_TIME_5`, including wait and debounce counters.
- DCC bank/DAC controls and ACK/address fields: `DCC_CR_BANK_ADDR`, `DCC_CR_BANK_DATA`, `DCC_DAC_CTRL`, `DCC_DAC_RANGE`, `DCC_DAC_SEL`, `DCC_DAC_ACK`, and `DCC_DAC_ADDR`.
- TX clock alignment and LBERT controls: `TX_CLK_ALIGN_TX_CTL_0` and `TX_LBERT_CTL`.
- RX statistics/match/control counters: `RX_STAT_LD_VAL_1`, `DATA_MSK`, `MATCH_CTL0` through `MATCH_CTL5`, `STAT_CTL0` through `STAT_CTL2`, `STAT_STOP`, `SMPL_CNT1`, `STAT_CNT_0` through `STAT_CNT_6`, and `CAL_COMP_CLK_CTL`.
- Digital-to-analog TX output controls: `DIG_ANA_TX_OVRD_OUT`, termination-code override/clock override, EQ override outputs, analog status, TX DCC DAC override outputs, and `DIG_ANA_TX_OVRD_OUT_2`.
- Lane-3 analog TX controls equivalent to the lane-2 tail: `ANA_TX_OVRD_MEAS`, `ANA_TX_PWR_OVRD`, `ANA_TX_ALT_BUS`, `ANA_TX_ATB1/2`, `ANA_TX_DCC_*`, `ANA_TX_TERM_CODE*`, `ANA_TX_OVRD_CLK`, `ANA_TX_MISC*`, and reserved blocks.

These fields are likely used during PHY bring-up, diagnostics, link training support, hardware validation, and low-level recovery. They are not ordinary framebuffer/display-mode state; they are PHY-side control knobs that can directly affect link electrical behavior.

### Raw Common Digital Controls

`DPCSSYS_CR2_RAWCMN_DIG_*` definitions describe common PHY state shared across lanes:

- `CMN_CTL` exposes `PHY_FUNC_RST`.
- `MPLLA_OVRD_IN`, `MPLLB_OVRD_IN`, bandwidth override, and SSC control fields define MPLL A/B word-divide, TX-clock-divide, div8/div10 clock, bandwidth, spread-spectrum range/clock/en, and override-enable paths.
- `LANE_FSM_OP_XTND`, `CMN_CTL_1`, `MPLL_STATE_CTL`, `TX_CAL_CODE`, `SRAM_INIT_DONE`, and `OCLA` cover common control/status and observability.
- `SUP_ANA_OVRD`, `PCS_RAW_ID_CODE`, and firmware ID code registers expose supervisor/analog override and identity fields.
- `AON_CMN_RTUNE_RX_VAL_*`, `AON_CMN_RTUNE_TXDN_VAL_*`, and `AON_CMN_RTUNE_TXUP_VAL_*` define always-on resistor tuning values for eight slots.
- `AON_CMN_SRAM_BL_CFG`, power-gating override in/out, supervisor override in, VREF stats, resistance override in/out, reference-range override, and miscellaneous config fields support always-on calibration, power gating, and common analog control.

The raw-common block is a high-risk area for manual changes because PLL and tuning fields usually have sequencing requirements outside this header. The macros expose field packing only; they do not document the timing or dependency constraints for MPLL/SSC/power-gating changes.

### Raw Lane 0 PCS Interface

`DPCSSYS_CR2_RAWLANE0_DIG_PCS_XF_*` starts the raw-lane0 PCS crossbar/interface definitions:

- TX PCS override inputs: `TX_OVRD_IN`, `TX_OVRD_IN_1`, TX PCS input, TX override output, and TX PCS output. Fields include pstate, low-power detect, width, rate, MPLL select/en, master MPLL state override, TX async enable, reset/request/detect-RX request overrides, VBOOST/IBOOST, beacon, EQ cursor controls, ack/data-enable, and power-good signaling.
- RX PCS override inputs: `RX_OVRD_IN` through `RX_OVRD_IN_3`, RX PCS input blocks, RX PCS output, adaptation ACK/FOM, TXPRE/TXMAIN/TXPOST direction indicators, lane number, reserved slots, ATE override input, RX EQ delta/IQ overrides, TX/RX termination control override/input, RX override output, RX EQ override inputs, and RX phase-2 calibration.

The PCS fields describe the protocol-control side of the PHY lane. Many fields are handshake or request/ack pairs; others are diagnostic or adaptive-equalization signals. Consumers should treat this as a register contract between PCS logic and PMA/ASIC-facing lane logic.

### Raw Lane 0 FSM, IRQ, PMA, and TX Control

The final section covers the raw lane-0 micro-FSM, interrupt, PMA interface, and the first TX-control registers:

- `DIG_FSM_FSM_OVRD_CTL` defines micro-FSM jump address, jump enable, command start, override enable, and break fields.
- `DIG_FSM_MEM_ADDR_MON` and `STATUS_MON` expose monitored FSM program address and status bits such as command ready, ALU overflow, zero result, wait counter, and mask-disabled flags.
- `DIG_FSM_FAST_*` blocks define fast-path calibration/adaptation sequences for RX startup, RX adaptation, AFE/DFE/ref-level/IQ calibration, supervisor, TX common-mode, TX RX-detect, RX power-up, VCO wait/cal, continuous calibration/adaptation, and fast flags.
- `DIG_FSM_CMNCAL_MPLL_STATUS`, `CR_LOCK`, `TX_DCC_FLAGS`, `TX_DCC_STATUS`, `OCLA`, `TX_EQ_UPDATE_FLAG`, `CMNCAL_RCAL_STATUS`, and `RX_IQ_PHASE_OFFSET` expose calibration, lock, DCC, observability, EQ-update, RCAL, and phase offset status.
- `DIG_IRQ_CTL_*` defines individual RX/TX/reset/request/rate/pstate/adaptation/phase-calibration/loopback/DCC interrupt latch fields, clear fields, and mask registers.
- `DIG_PMA_XF_*` defines PMA cross-interface lane/supervisor override and state fields, TX/RX request-reset-data-enable override outputs, TX/RX PMA ACK inputs, lane RTUNE request/ack, MPHY override input/output, and RX adaptation PMA IQ phase adjust override.
- `DIG_TX_CTL_TX_FSM_CTL`, `TX_CLK_CTL`, `TX_DCC_CONT_STATUS`, `TX_CTL_OCLA`, and the beginning of `TX_CTL_UPCS_OCLA` expose TX-control FSM timing, RX-detect allowance by power state, TX clock enable/select, async beacon wait time, DCC continuous status, and OCLA data/clock observability.

The line range ends mid-family at `DPCSSYS_CR2_RAWLANE0_DIG_TX_CTL_UPCS_OCLA`; the next chunk continues with its masks and subsequent RX-control registers.

## Control Flow

There is no C control flow in this chunk. The effective flow appears only when generated constants are consumed by AMD display register helpers:

1. ASIC/resource code includes the matching offset and shift/mask headers.
2. Resource constructors build register, shift, and mask tables for the DCN/DPCS link encoder blocks.
3. Runtime display code calls register helper macros such as `REG_SET`, `REG_UPDATE`, or their structure-specific variants.
4. Those helpers use a register address plus a field shift and mask to read-modify-write MMIO/indexed register fields.

This chunk supplies step 2/3 metadata only. It does not enforce ordering, locking, polling, delays, or safe power-state transitions. Those responsibilities live in the display hardware sequencing code and the hardware specification.

## State and Persistence Behavior

The macros are compile-time constants with no process state. The state they describe exists in hardware registers:

- Override-enable/value fields can persist in the PHY register block until reset or until software clears them.
- Interrupt latch and clear registers describe transient hardware event state; clear-bit writes are typically write-one-to-clear style, but the exact semantics must come from the hardware programming guide or surrounding driver code.
- Status monitor, ACK, calibration, RTUNE, VREF, power-good, and FSM status fields reflect hardware state and can change asynchronously relative to software.
- Reserved and `NC*` fields must be treated conservatively. They are defined with masks because generated headers expose bit layout, but their values are not part of a software-owned stable contract.

Because this is an ASIC register header, persistence is primarily MMIO/register persistence across driver operations, low-power transitions, and hardware reset domains. The header itself stores nothing.

## Dependencies and Integration Points

Primary dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` supplies register addresses that match the field names in this header.

Observed integration:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- The same file defines DPCS base segments and incorporates DPCS register, shift, and mask lists into DCN 3.1.6 link encoder resources through `DPCS_DCN31_REG_LIST(id)`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, and `DPCS_DCN31_MASK_SH_LIST(_MASK)`.
- Related generated headers such as `dpcs_4_2_0_sh_mask.h`, `dpcs_4_2_2_sh_mask.h`, `dpcs_3_1_4_sh_mask.h`, and `dcn_4_1_0_sh_mask.h` contain similar or mirrored register families. They are useful for drift checks but should not be substituted for this version.

The file is generated-style hardware metadata. Downstream code depends on exact macro spelling, exact bit positions, and the paired offset/header version staying aligned.

## Risks and Failure Modes

- **Offset/mask version mismatch:** Including `dpcs_4_2_3_sh_mask.h` with another DPCS offset header can compile if macro names overlap, but would target wrong bits or wrong indexed registers.
- **Reserved-bit corruption:** Many fields reserve upper bits such as `RESERVED_15_8_MASK 0xFF00L` or high-bit ranges such as `RESERVED_15_11_MASK 0xF800L`. Full-register writes that do not preserve reserved bits can cause undefined PHY behavior.
- **Override pair misuse:** Many register families use value/en pairs. Setting a value without the corresponding enable has no effect; leaving enables set can pin a lane or PLL in test/override mode.
- **Electrical/link-training instability:** TX EQ, termination, DCC, PLL, SSC, VBOOST/IBOOST, RX CDR/slicer, and adaptation fields affect physical link behavior. Incorrect values can break DP/HDMI training, cause intermittent link loss, or increase power/noise.
- **Asynchronous status assumptions:** ACK, interrupt, FSM, calibration, and tuning fields can change independently of CPU flow. Polling logic must use appropriate timeouts and cannot infer stable state from this header alone.
- **Cross-generation copy/paste drift:** Similar names appear in DPCS 4.2.0/4.2.2 and DCN 4.1.0 headers. Some fields differ in spelling, width, or semantic availability; generated definitions should be compared mechanically rather than hand-merged.
- **Partial-chunk boundary:** This chunk ends at the start of `RAWLANE0_DIG_TX_CTL_UPCS_OCLA`; any final per-file research must merge with the next chunk before drawing conclusions about the complete TX/RX control block.

## Test and Validation Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Build coverage for DCN 3.1.6/AMDGPU display code that includes `dcn316_resource.c`, verifying that all `DPCS_DCN31_*` generated macro references resolve.
- Static consistency checks between `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`: each field block in this chunk should have a corresponding `ixDPCSSYS_CR2_*` register offset.
- Cross-generation diffs against `dpcs_4_2_2_sh_mask.h` and `dcn_4_1_0_sh_mask.h` for families expected to match, with explicit review for intended differences such as field spelling/case or changed analog measurement fields.
- Register helper unit or compile tests that exercise `REG_SET`/`REG_UPDATE` mask packing for representative fields, especially multi-bit fields like `RATE`, `WIDTH`, `TX_CLK_SEL`, `RX_PMA_TERM_CTL_R`, `TX_WAIT_MPLL_OFF_TIME`, and `RX_PMA_IQ_PHASE_ADJUST_MAP_OVRD_VAL`.
- Hardware smoke tests on a DCN 3.1.6 platform: link encoder initialization, DisplayPort/HDMI hotplug, link training at multiple rates/widths, suspend/resume, low-power transitions, and interrupt handling.
- Debug validation for dangerous fields should rely on readback/polling and hardware documentation, not just the macro names. In particular, PLL/SSC changes, DCC/termination updates, FSM override commands, RTUNE requests, and IRQ clear writes need behavior-level testing.

## Summary

Lines 48596-51027 define a dense generated bitfield contract for DPCS 4.2.3 CR2 PHY registers. The chunk spans lane-specific analog/TX/RX controls, lane-3 ASIC and diagnostic paths, raw-common PLL/tuning/power-gating controls, and raw-lane0 PCS/FSM/IRQ/PMA/TX-control fields. The key engineering concern is exact pairing of this shift/mask header with the matching offset header and with ASIC-specific register tables. The macros are passive compile-time metadata, but they describe hardware fields that can affect PHY reset, clocking, link training, calibration, interrupts, and low-level analog behavior.
