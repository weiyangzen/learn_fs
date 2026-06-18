# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 104914-107500

## Purpose

This chunk is part of AMDGPU's generated DPCS 4.2.3 shift/mask register header. The requested range contains C preprocessor constants that name bit positions for C20 PHY CR0 lane and raw-lane registers. It is hardware metadata, not executable driver logic, and it exists so display code, diagnostics, and hardware bring-up paths can refer to ASIC register fields by stable generated names instead of raw bit numbers.

The range covers 2,587 source lines with 2,084 `#define` statements, all using the `__SHIFT` suffix, and 503 generated register comment boundaries. It starts in the middle of `C20_PHY_CR0_LANE3_DIG_ASIC_TX_OVRD_IN_4`, then covers a large lane 3 TX/RX digital and analog field map, rawlane0 TX/RX PCS/PMA/FW/IRQ/control/FSM fields, and begins rawlane1 TX PCS crossing fields. There are no `_MASK` definitions in this exact range; this slice belongs to the shift-definition portion of the generated header.

Although the source tree path is under `ceph-client`, this file is AMD display hardware register metadata. It does not implement distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, memory allocations, exported symbols, or direct MMIO operations in this chunk. The only interface is the generated macro convention:

- `C20_PHY_CR0_<block>__<field>__SHIFT`: least-significant bit position for a field inside a C20 PHY CR0 indexed register.
- `//C20_PHY_CR0_<block>` comments: generated register boundaries matching companion offset definitions and later mask sections.

The main register families in this range are:

- `C20_PHY_CR0_LANE3_DIG_ASIC_TX_*`: lane 3 ASIC TX override, ASIC input, and ASIC output fields for clock-ready, reset, invert, data enable, request, low-power detect, pstate, rate, width, MPLL selection, RX detect, disable, beacon, boost, TX cursor/equalization, DCC bypass/range/update, deskew, TX ack, detected-RX result, and calibration status.
- `C20_PHY_CR0_LANE3_DIG_TX_PWRCTL_*`: lane 3 TX pstate definitions for `P0`, `P0S`, `P1`, and `P2`; power-up timing registers; TX control/status; DCC offset/control status; statistic counter controls; clock alignment; LBERT pattern generation; TX level calculation; and TX FIFO controls.
- `C20_PHY_CR0_LANE3_DIG_ANA_XF_TX_*`: digital-to-analog TX crossing fields for analog override outputs, termination code override, DCC enable/config/calibration controls, equalization override/status, TX status input/output, and TX analog configuration registers `CREG00` through `CREG05`.
- `C20_PHY_CR0_LANE3_DIG_ASIC_RX_*`: lane 3 ASIC RX override, ASIC input/output, CDR/VCO, and EQ fields for clocking, reset, pstate, rate, termination, signal-detect, VCO, VGA/DFE/CTLE/slicer controls, calibration status, adaptation controls, and miscellaneous override values.
- `C20_PHY_CR0_LANE3_DIG_RX_PWRCTL_*`: lane 3 RX pstate, power-up timing, control, and status fields for analog front-end, CDR, deserializer, DFE, slicers, EQ, VCO, CDR lock, and fast power-up/readiness behavior.
- `C20_PHY_CR0_LANE3_DIG_RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, and `RX_IQC_*`: VCO calibration controls/status, CDR tuning/status, DPLL frequency bounds, and IQ correction reset/config/status.
- `C20_PHY_CR0_LANE3_DIG_RX_ADPTCTL_*`: RX adaptation configuration and status fields for ATT, VGA, CTLE, DFE taps, slicer offsets/levels, DCC offsets, fast flags, SSM configuration, final codes, and adaptation reset.
- `C20_PHY_CR0_LANE3_DIG_RX_STAT_*` and `TX_STAT_*`: statistic/match/load/sample/count controls, counters, stop bits, and calibration compare clock controls for lane-level measurement.
- `C20_PHY_CR0_LANE3_DIG_ANA_XF_RX_*`: analog RX crossing controls for power, signal-detect calibration, VCO override, RX calibration, DAC controls, AFE overrides, scope/slicer/IQ/IQC behavior, loopback, DCC calibration, sample selection, termination, status, and RX analog configuration registers `CREG00` through `CREG11`.
- `C20_PHY_CR0_RAWLANE0_DIG_TX_*` and `RAWLANE0_DIG_RX_*`: rawlane0 PCS/FW/PMA crossing, lane-number, request/ack, pstate/rate/width, loopback, detect-RX, data-enable, reset, adaptation, margining, IRQ mask/enable/status/clear, TX/RX control, termination, clock, and PMA input/output metadata.
- `C20_PHY_CR0_RAWLANE0_DIG_FSM_*`: rawlane0 FSM override, jump, memory breakpoint/monitor, status monitor, firmware scratch/debug, CR lock, fast startup/power-up controls, and many skip flags for TX/RX startup, continuous calibration, DCC, DFE, IQ, AFE, VGA, CTLE, ATT, margining, and adaptation reload flows.
- `C20_PHY_CR0_RAWLANE1_DIG_TX_PCS_XF_*`: the beginning of rawlane1 TX PCS crossing definitions, including lane loopback/link-number overrides, reset/request overrides, pstate/LPD/data/invert/clock/beacon/MPLL overrides, master MPLL state, detect-RX, deskew, recalibration controls, context selection, and the start of direct TX PCS input fields.

Field-name patterns encode hardware intent: `OVRD`, `OVRD_EN`, `ASIC_IN`, `ASIC_OUT`, `ANA_XF`, `PCS_XF`, `PMA_XF`, `FW_XF`, `PSTATE`, `RATE`, `WIDTH`, `REQ`, `ACK`, `IRQ`, `IRQ_CLR`, `MASK`, `RESET`, `CLK_RDY`, `DATA_EN`, `LPD`, `DETRX`, `MPLL`, `DCC`, `VCO`, `CDR`, `DFE`, `CTLE`, `VGA`, `SLICER`, `SIGDET`, `ADPT`, `LBERT`, `FIFO`, `TERM`, `MARGIN`, `FAST`, `SKIP`, and `RESERVED`.

## Control Flow

This header has no runtime control flow. It affects runtime only after C code includes it and uses the macros to build register table metadata or to compose/read register fields.

The normal consuming flow is:

1. Driver/resource code selects a DPCS 4.2.3 register offset or indexed C20 PHY register from the matching generated offset header.
2. Register helpers combine an offset with `__SHIFT` and, where available from the matching mask section, `_MASK` metadata.
3. Runtime display code performs read/modify/write, polling, or decode operations through MMIO or DPCS CR access paths.
4. Hardware and firmware state machines handle the actual TX/RX power sequencing, PLL behavior, adaptation, calibration, link training, interrupt signaling, and debug sampling.

The sequencing implied by these fields lives outside this file. Examples include enabling TX/RX pstate bits in the right order, waiting for clock/VCO/CDR/calibration status, clearing IRQ fields, forcing or releasing override controls, reading statistic counters, and using rawlane FSM skip/fast flags only under hardware-aware procedures.

## State And Persistence Behavior

The macros are stateless compile-time constants. They describe bit positions for hardware state, but they do not store state and do not define reset values, legal enum values, access widths, write-one-to-clear behavior, retention, ownership, or timing.

Hardware state named by this chunk includes:

- Lane 3 TX control state: resets, clock readiness, data enable, rate/width/pstate, TX cursor/equalization, DCC, deskew, TX power state enables, TX power-up timing, TX DCC status, clock alignment, LBERT pattern generation, FIFO controls, analog TX override outputs, and TX analog configuration.
- Lane 3 RX control state: resets, clock readiness, pstate/rate, RX power state enables, VCO and CDR calibration/status, adaptation configuration/status, DFE/VGA/CTLE/slicer status, signal detect, DPLL bounds, IQ correction, statistics, analog RX override outputs, DAC controls, and RX analog configuration.
- Rowlane0 bridge state: TX/RX PCS, PMA, and firmware handoff values, request/ack status, loopback, link number, lane mode, termination controls, adaptation handshakes, RX margining controls, and PMA input/output mirrors.
- Rowlane0 interrupt state: RX/TX reset/request/rate/pstate/adaptation/margining/termination/lane-mode/loopback/DCC events, with separate mask, enable, status, and clear fields.
- Rowlane0 FSM/debug state: firmware scratch/debug registers, memory breakpoint/monitor fields, CR lock, fast power-up/startup/adaptation flags, and skip controls for startup, rate, continuous, and margin-related calibration flows.
- Rowlane1 TX PCS state at the tail of the range: TX PCS override and direct-input fields for reset/request, pstate, LPD, data enable, inversion, clock readiness, beacon, MPLL state, detect-RX, deskew, recalibration, and context selection.

Persistence is hardware-defined. Register contents may be reset or changed by GPU reset, display-engine reset, DPCS/PHY reset, power gating, suspend/resume, hotplug link retraining, modeset, link-rate or lane-count change, firmware handoff, calibration/adaptation state-machine transitions, or diagnostic tools.

## Dependencies And Integration Points

This chunk depends on the generated DPCS 4.2.3 register database and must stay aligned with the matching `dpcs_4_2_3_offset.h` file and later `_MASK` macro definitions in this same header. The shift names are not portable across unrelated ASIC register generations unless the hardware database explicitly says the field layout is identical.

In this repository, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` directly includes both `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`. That file builds DCN316 link encoder/resource metadata with `DPCS_DCN31_REG_LIST(id)` plus `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`. Most fields in this chunk are lower-level C20 PHY/lane metadata beyond the small link-encoder table expansion, but they are in the same generated namespace available to AMD display, PHY validation, debug, and bring-up code.

Other integration points include:

- AMDGPU Display Core link, resource, PHY, and encoder code that programs DPCS/DCN registers for DisplayPort/HDMI link operation.
- DPCS CR indexed-register access helpers that pair generated register offsets with shift/mask metadata.
- Hardware/firmware lane control, power, calibration, adaptation, and interrupt state machines.
- Diagnostics and validation flows using LBERT, statistics counters, rawlane FSM debug/scratch fields, analog test/crossing registers, margining, DCC/VCO/CDR/IQ calibration readback, and interrupt observation.

## Risks And Edge Cases

- A wrong `__SHIFT` value can compile successfully while programming or decoding the wrong hardware bit.
- This range contains only shift definitions. Code that requires masks must use the matching `_MASK` definitions from the appropriate generated section; inventing masks ad hoc risks wrong field widths, especially for reserved and multi-bit fields.
- The first register is split: this chunk starts after the `C20_PHY_CR0_LANE3_DIG_ASIC_TX_OVRD_IN_4` comment and after earlier fields owned by the previous chunk.
- The last register is split: this chunk ends at `C20_PHY_CR0_RAWLANE1_DIG_TX_PCS_XF_IN_1__LANE2LANE_DSKW_EN__SHIFT`, before the rest of that register's fields.
- Override value and override enable fields are adjacent in many groups. Confusing them can force clocks, resets, pstate/rate/width, data-enable, loopback, MPLL ownership, deskew, recalibration, adaptation, DCC, or analog controls away from normal hardware/firmware control.
- IRQ status, mask, enable, and clear fields are sequencing-sensitive. Incorrect definitions can cause missed lane events, interrupt storms, stuck status, link-training timeouts, or unreliable suspend/resume and hotplug recovery.
- TX/RX analog, DCC, VCO, CDR, DPLL, IQ, slicer, CTLE, VGA, DFE, signal-detect, termination, and margining fields are silicon- and board-sensitive. Errors can appear only at particular link rates, voltage/temperature corners, cable/sink combinations, or after repeated retraining.
- FSM fast/skip controls can bypass calibration/adaptation steps. They should be treated as hardware validation/debug controls unless normal display code has explicit ASIC guidance.
- `RESERVED` fields are named throughout the range. Consumers should preserve them or leave them untouched unless authoritative programming documentation for this ASIC revision says otherwise.
- Repeated lane and rawlane names make copy/paste errors easy. Mixing lane 3 fields with rawlane0/rawlane1 fields, or using a DPCS 4.2.3 shift with another generation's offset, may still compile but target the wrong register semantics.

## Test Signals

Useful validation signals for this generated range and its consumers include:

- Build AMDGPU display code for DCN316/DPCS 4.2.3 paths that include `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`; missing or renamed consumed macros should fail at compile time.
- Mechanically compare all 2,084 shift definitions in this range against the authoritative DPCS 4.2.3 register database.
- Cross-check register names in this chunk against the matching offset header, with explicit exceptions for split boundary registers.
- Pair this shift-only range with the corresponding mask definitions and verify field widths for multi-bit controls such as pstate, rate, width, counters, timers, DCC offsets, VCO/CDR/DPLL fields, adaptation values, IRQ masks, context selectors, and firmware/debug registers.
- Diff repeated lane 3 and rawlane0/rawlane1 field families against neighboring generated DPCS versions only as a generator-drift check; version differences may be intentional.
- Exercise hardware scenarios that stress these fields: boot display, hotplug, modeset, link-rate changes, lane-count changes, blank/unblank, DisplayPort link training, suspend/resume, GPU reset, and recovery after failed training.
- Monitor register dumps and logs for TX/RX request/ack timeouts, stuck reset/data/clock overrides, bad pstate transitions, VCO/CDR lock failures, RX adaptation or DFE/VGA/CTLE anomalies, DCC failures, unstable signal detect, FIFO/stat counter anomalies, margining failures, and repeated or missing rawlane IRQs.
- Use known-good register dumps or vendor validation tools to decode representative lane 3 TX/RX and rawlane0/rawlane1 registers with these shifts and compare against documented bit positions.

## Cross-Chunk Notes

This document intentionally covers only lines 104914-107500 of `dpcs_4_2_3_sh_mask.h`. The previous chunk owns the start of `C20_PHY_CR0_LANE3_DIG_ASIC_TX_OVRD_IN_4`; this chunk resumes at `TX_PRE_CURSOR` and completes the following lane 3 TX/RX, analog, adaptation, statistic, power, and rawlane0 FSM/control families. The next chunk must continue `C20_PHY_CR0_RAWLANE1_DIG_TX_PCS_XF_IN_1` after `LANE2LANE_DSKW_EN` and cover the rest of rawlane1 and later generated C20 PHY CR0 definitions.
