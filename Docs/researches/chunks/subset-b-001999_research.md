# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h - subset-b-001999

## Scope

- Chunk id: `subset-b-001999`
- Source lines: 170768-173202
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h`
- Observed content: 2,435 lines, 2,126 `#define` entries, 1,066 `__SHIFT` macros, 1,096 `_MASK` macros, and 309 register block comments.

This chunk is part of the generated AMD DCN 3.2 register shift/mask header. It contains no executable logic; it publishes the bit-field layout for C20 PHY CR3 analog, raw-lane PCS/PMA/FW, IRQ, RX/TX control, and FSM registers. The register groups in this slice are mostly 16-bit fields described by paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros.

## Purpose

The chunk starts in the tail of `C20_PHY_CR3_LANE3_DIG_ANA_XF_RX_ANA_CREG08`, completes several lane-3 RX analog CREG blocks, then defines raw-lane 0 and raw-lane 1 register fields under `C20_PHY_CR3_RAWLANE*`. These raw-lane blocks describe PCS and PMA crossbar interfaces, firmware handshakes, interrupt status/clear bits, lane context configuration, RX equalization and margining controls, and a lane-local PHY FSM/debug surface.

The practical purpose is to let DCN 3.2 display and amdgpu code access hardware fields without hard-coded bit positions. Consumers combine these macros with matching offset definitions from `dcn_3_2_0_offset.h` and the AMDGPU/DC register-access helpers to perform field extraction, field insertion, and MMIO read-modify-write operations.

## Important APIs, Types, and Macros

There are no functions, structs, enums, or storage declarations in this chunk. The public interface is the generated preprocessor namespace:

- Lane 3 RX analog tail:
  - `C20_PHY_CR3_LANE3_DIG_ANA_XF_RX_ANA_CREG08` through `_CREG11`
  - `C20_PHY_CR3_LANE3_DIG_ANA_XF_RX_ANA_CREG0_OVRD` and `_CREG1_OVRD`
  - Fields cover RX signal-detect bias, VREG charge-pump/ring/feed-back controls, common-mode selections, loopback-rate selection, slicer/scope ranges, and reserved analog override register placeholders.
- Raw lane 0 TX PCS interface:
  - `C20_PHY_CR3_RAWLANE0_DIG_TX_PCS_XF_LANE_OVRD_IN_0`, `_LANE_IN_0`
  - `C20_PHY_CR3_RAWLANE0_DIG_TX_PCS_XF_OVRD_IN_0` through `_IN_3`
  - `C20_PHY_CR3_RAWLANE0_DIG_TX_PCS_XF_IN_0` through `_IN_2`
  - `C20_PHY_CR3_RAWLANE0_DIG_TX_PCS_XF_OVRD_OUT_0`, `_OUT_0`, and `_CNTX_CFG_0` through `_CNTX_CFG_2`
  - These fields describe loopback enables, link number, reset/request, pstate, low-power detect, data enable, inversion, clock-ready, beacon, MPLL enable/state, RX-detect request/result, deskew, recalibration, context select, rate, width, wide-transfer alignment, VREG/VBOOST/IBOOST, KR driver enable, DCC bypass/range, term control, and TX unique ID.
- Raw lane 0 TX firmware, IRQ, control, and PMA surfaces:
  - `C20_PHY_CR3_RAWLANE0_DIG_TX_FW_XF_*`
  - `C20_PHY_CR3_RAWLANE0_DIG_TX_IRQ_CTL_*`
  - `C20_PHY_CR3_RAWLANE0_DIG_TX_CTL_*`
  - `C20_PHY_CR3_RAWLANE0_DIG_TX_PMA_XF_*`
  - These define firmware override handshakes, lane numbering, TX reset/request/rate/loopback/RTUNE/term/xceiver-mode interrupt bits and clear bits, IRQ enable/mask flags, TX FSM interrupt enables, TX clock select, firmware power-up done, MPLLA/MPLLB resistor calibration enables, PMA lane override inputs/outputs, supervisor state overrides, TX request/reset PMA overrides, and RTUNE request/ack fields.
- Raw lane 0 RX PCS, firmware, IRQ, control, and PMA surfaces:
  - `C20_PHY_CR3_RAWLANE0_DIG_RX_PCS_XF_*`
  - `C20_PHY_CR3_RAWLANE0_DIG_RX_FW_XF_*`
  - `C20_PHY_CR3_RAWLANE0_DIG_RX_IRQ_CTL_*`
  - `C20_PHY_CR3_RAWLANE0_DIG_RX_CTL_*`
  - `C20_PHY_CR3_RAWLANE0_DIG_RX_PMA_XF_*`
  - Fields cover RX reset/request/pstate/data/invert/CDR SSC/adaptation, margin IQ/VDAC/in-progress/error-clear, recalibration bank/force/skip, loopback select, EQ context configuration, CTLE/VGA/AFE/DFE controls, CDR VCO config, rate/ref/VCO load values, signal-detect thresholds, term/DCC/VREG/adaptation/offcan controls, firmware adaptation ACK/FOM and TX pre/main/post directions, RX interrupt status/clear groups, PPM drift, CDR detect status, adaptation mode/select/FOM/reference-error/IQ limits, phase-adjust maps, margin deltas/status/errors, IQ code read/write, and PMA request/reset/ack overrides.
- Raw lane 0 FSM and firmware-debug surface:
  - `C20_PHY_CR3_RAWLANE0_DIG_FSM_FSM_OVRD_CTL`, `_FSM_JMP_BANK`, `_FSM_CTL_0`
  - `C20_PHY_CR3_RAWLANE0_DIG_FSM_MEM_BREAKPOINT_*`, `_MEM_ADDR_MON`, `_STATUS_MON`
  - `C20_PHY_CR3_RAWLANE0_DIG_FSM_FW_CFG_STAGE`, `_FW_SCRATCH_0` through `_FW_SCRATCH_11`
  - `C20_PHY_CR3_RAWLANE0_DIG_FSM_CR_LOCK`, `FAST_*`, `SKIP_*`, and `_RX_CAL_STATUS`
  - These fields expose jump/bank/command override, breakpoints, monitored memory address, FSM state and ALU/wait/mask status, firmware configuration stage, scratch registers, control-register lock, fast-path flags, many startup/continuous calibration skip knobs, and RX calibration done status.
- Raw lane 1 TX and RX beginning:
  - `C20_PHY_CR3_RAWLANE1_DIG_TX_PCS_XF_*`, `TX_FW_XF_*`, `TX_IRQ_CTL_*`
  - `C20_PHY_CR3_RAWLANE1_DIG_RX_PCS_XF_OVRD_IN_*`, `_IN_*`, `_OUT_*`, and `_CNTX_CFG_0` through the start of `_CNTX_CFG_7`
  - These largely mirror the lane 0 PCS/FW/IRQ field families for lane 1. The chunk ends inside lane 1 RX PCS context configuration, after the first visible `_CNTX_CFG_7` mask.

## Control Flow

This header chunk has no local control flow. Runtime sequencing is imposed by the code that includes it and by the C20 PHY hardware:

1. A DCN 3.2 component includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. The component selects a register offset and a field mask/shift pair from this generated namespace.
3. Register helper macros/functions assemble field values or extract status bits.
4. MMIO reads/writes program the PHY, observe status, acknowledge IRQs, clear latch bits, or force debug/override behavior.

The register names imply several hardware flows: PCS and firmware interfaces use request/ack style handshakes; override registers usually pair a forced value with an `*_OVRD_EN` bit; IRQ blocks separate status bits, mask/en flags, and clear registers; calibration and adaptation controls have separate enable, skip, fast-path, status, and error fields.

## State and Persistence Behavior

The macros themselves are compile-time constants and have no persistence. They describe state stored in hardware registers:

- Configuration-like state persists until reset or reprogramming: lane link number, context select, rate/width, MPLL selection, pstate, DCC range/bypass, term code, VREG/VBOOST/IBOOST, EQ/AFE/CTLE/DFE settings, signal-detect thresholds, CDR/VCO load values, adaptation mode, phase-adjust maps, and FSM skip/fast flags.
- Handshake and status state is transient or latched: request/ack bits, power-up done, RTUNE ACK, RX adaptation ACK/FOM, PPM drift valid, CDR detect state, margin status/error, IQ readback, FSM state/status, and RX calibration done.
- IRQ state is likely latch-and-clear: the chunk defines many one-bit IRQ registers and matching `*_IRQ_CLR` registers for TX reset/request/rate/loopback/RTUNE/term/xceiver-mode and RX reset/request/rate/pstate/adaptation/term/margin events.
- Override state is hazardous if left enabled. Many `OVRD_IN`, `OVRD_OUT`, and PMA/FW override groups have explicit `*_OVRD_EN` bits; stale enables can pin a lane away from normal PCS, firmware, or PMA control.
- Reserved fields are explicitly defined but should not be treated as ordinary writable fields. They document layout occupancy and protect field math, not policy for full-register writes.

## Dependencies

This chunk depends on AMDGPU/DCN generated-register conventions:

- Matching register offsets in `include/asic_reg/dcn/dcn_3_2_0_offset.h`.
- AMDGPU and display-core register helpers that expect the generated `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming pattern.
- DCN 3.2 hardware semantics for C20 PHY CR3 raw lanes and analog lane blocks.
- Include sites that select this ASIC register namespace for DCN 3.2, including `dmub_dcn32.c`, `irq_service_dcn32.c`, `hw_translate_dcn32.c`, `hw_factory_dcn32.c`, `dcn32_clk_mgr.c`, `dcn32_resource.c`, and `gmc_v11_0.c`.

The exact field macros appear to be generated data, not hand-maintained API. Correctness depends on the generator and hardware description staying aligned with the ASIC register map.

## Integration Points

The fields in this slice integrate with:

- Link training and lane bring-up code that configures rate, width, pstate, reset, request, clock-ready, MPLL selection, VREG/VBOOST/IBOOST, CDR/VCO, and EQ/adaptation context.
- Power-management and firmware handoff paths that coordinate PCS, PMA, and firmware crossbar request/ack signals.
- IRQ handling and diagnostic paths that inspect or clear lane events for TX/RX rate changes, resets, requests, loopbacks, term changes, RTUNE, adaptation, and margining.
- PHY calibration and debug flows that use DCC, RTUNE, CDR, VCO, CTLE, VGA, ATT, DFE, IQ, phase-adjust, margin, fast, and skip controls.
- Low-level validation tooling that may use the FSM override, breakpoint, scratch, lock, and status-monitor registers to debug PHY micro-sequencer behavior.
- Multi-lane code that must choose lane-specific register names and offsets consistently. This chunk covers CR3 raw lane 0 and the beginning of raw lane 1; adjacent chunks cover neighboring lane ranges.

## Risks and Edge Cases

- Generated mask/shift drift can silently corrupt PHY programming. A wrong bit position in rate, width, pstate, reset, MPLL, CDR/VCO, DCC, EQ, or override enable fields can break link bring-up or produce unstable display links.
- The chunk has many value/enable pairs. Writing only a forced value without its enable bit has no effect; leaving an enable bit set after diagnostics can keep hardware in an unintended manual-control mode.
- IRQ clear registers are easy to confuse with IRQ status registers because names differ only by `_CLR`. Code must use the clear field only for the intended write-to-clear action.
- TX/RX and PCS/PMA/FW directions are semantically significant. Similar `IN`, `OUT`, `OVRD_IN`, and `OVRD_OUT` names should not be substituted across interfaces.
- Raw lane 0 and raw lane 1 names are structurally similar. Copying code between lanes without changing both offsets and field macros can address the wrong lane.
- FSM override, jump, breakpoint, fast, and skip controls are high-risk debug knobs. They can bypass calibration or steer the PHY sequencer away from normal firmware/hardware sequencing.
- Margining and adaptation fields expose intermediate values and error state. Reading without respecting done/in-progress/error-clear semantics can produce stale or partial diagnostics.
- Reserved masks occupy many high bits. Full-register writes should preserve reset/default values and avoid intentional writes to reserved bits unless the generated access layer has verified semantics.
- The chunk begins and ends mid-register-family. Merge/reconciliation must combine this report with adjacent chunk reports before making final per-file conclusions about the full C20 PHY CR3 register map.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Build coverage for DCN 3.2 include sites to catch missing or renamed generated macros.
- Generated-header consistency checks verifying that each writable/status field has aligned `__SHIFT` and `_MASK` definitions and that masks correspond to the declared shift and expected width.
- Representative register-helper tests for inserting and extracting fields such as TX PCS rate/width, TX IRQ clear, TX PMA RTUNE request/ack, RX PCS EQ context, RX CDR/VCO configuration, RX margin IQ/VDAC, RX adaptation mode/FOM, and FSM status bits.
- Hardware link-training, hotplug, suspend/resume, and mode-set testing to catch stale override enables, incorrect pstate/rate/width programming, and broken calibration sequencing.
- Diagnostic tests for IRQ latch/clear behavior, RTUNE handshakes, firmware request/ack flows, margin in-progress/error handling, CDR detect state, and FSM breakpoint/status monitoring.
- Negative/regression checks that debug code clears override enables and skip/fast flags when returning lanes to normal automatic operation.

## Chunk Boundary Notes

Line 170768 is inside `C20_PHY_CR3_LANE3_DIG_ANA_XF_RX_ANA_CREG08`; that register block began before this chunk. The final visible block is `C20_PHY_CR3_RAWLANE1_DIG_RX_PCS_XF_CNTX_CFG_7`, which continues beyond line 173202. The final per-file research document should merge this with adjacent chunks for complete lane-family coverage.
