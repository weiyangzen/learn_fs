# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h - subset-b-002005

## Scope

- Chunk id: `subset-b-002005`
- Source lines: 185510-187947
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h`
- Observed content: 2,438 source lines with 2,121 `#define` entries, 1,060 `__SHIFT` macros, 1,087 `_MASK` macros, and 317 register block comments.

This chunk is generated AMD DCN 3.2 register field metadata. It defines bit positions and masks for C20 PHY CR3 lane-crossing, raw lane, raw lane always-on, TX/RX, PCS/PMA/FW/IRQ/FSM, calibration, and margining registers. It does not define executable C code, functions, structs, enums, or storage. Its public surface is the preprocessor namespace consumed by AMDGPU/DCN register access code.

## Purpose

The chunk publishes the bit layout contract for a contiguous set of C20 PHY CR3 registers:

- `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_*` covers RX analog crossover controls and status: VCO/CDR override outputs, analog calibration muxes and DAC controls, AFE trim, ATT/VGA/CTLE/bias overrides, scope/slicer controls, IQ/IQC controls, term-code override clocks, analog status in/out, and `ANA_CREG00` through `ANA_CREG11` analog control registers.
- `C20_PHY_CR3_RAWLANEX_DIG_TX_*` covers raw TX PCS, firmware, IRQ, control, and PMA crossbar registers. These include lane loopback/link number controls, reset/request/data/pstate/rate/width/PLL/equalization overrides, firmware handshakes, interrupt masks/status/clear bits, RX-detect allowance by power state, clock selection, term code, PLL resistor calibration, PMA lane/supervisor overrides, and RTUNE request/ack paths.
- `C20_PHY_CR3_RAWLANEX_DIG_RX_*` covers raw RX PCS, firmware, IRQ, control, and PMA crossbar registers. These include reset/request/pstate/LPD/data/invert/CDR/adaptation overrides, margining controls, width/rate/frequency and DFE bypass overrides, FW adaptation feedback and coefficient direction fields, RX interrupt status/clear bits, RX term/adaptation/CDR/margin status controls, IQ and phase-adjust code read/write paths, and PMA request/reset/ack overrides.
- `C20_PHY_CR3_RAWLANEX_DIG_FSM_*` covers firmware state-machine debug and steering: jump address/bank, command start/override enable, breakpoints, memory address/status monitors, firmware stage/scratch registers, CR lock, fast-path flags, skip-calibration flags, and RX calibration status.
- `C20_PHY_CR3_RAWLANEAONX_DIG_TX_*` covers always-on TX firmware state and DCC banks: firmware state snapshots, SRAM recording controls and addresses, CCA loop/wait counters, startup/continuous algorithm skip bits, fast TX flags, HP protection and lane mode overrides, initial power-up done, disable override, and per-bank MPLLA/MPLLB DCC range/full/half common-mode and differential values.

The macros are paired by convention: `REGISTER__FIELD__SHIFT` gives the least-significant bit position and `REGISTER__FIELD_MASK` gives the already-shifted bit mask. Consumers combine these with register offsets from the matching offset header and AMDGPU/DCN MMIO helpers.

## Important APIs, Types, and Macros

There are no normal APIs or C types here. The important exported interface is the generated macro naming scheme.

Important register families in this chunk include:

- RX analog crossover and calibration:
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_VCO_OVRD_OUT_1`, `_2`
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_CAL_0`, `_1`
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_VDAC_RANGE_SEL`
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_DAC_CTRL`, `_OVRD`, `_SEL`
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_DCC_CAL_DAC_CTRL_RANGE`
  - These expose CDR VCO configuration/frequency tuning, calibration muxes, slicer/calibration modes, VDAC range selection, DAC control selection, and DCC calibration DAC ranges.
- RX analog AFE, IQ, slicer, and termination controls:
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_AFE_OVRD_IN_0` through `_2`
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_SCOPE`
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_SLICER_CTRL`
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_ANA_IQ`
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_ANA_IQC_*`
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_TERM_CODE_*`
  - These map ATT, VGA, AFE rate, CTLE pole/boost/zero, bias, VCM, slicer even/odd controls, IQ sync bypass/reset, IQC bypass/data update clocks, loopback, AFE update, DFE/bypass/phase sample select, and RX termination controls.
- RX analog status and control registers:
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_STAT_OUT_0`, `_1`
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_STAT_IN_0`
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_ANA_CREG00` through `_CREG11`
  - `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_ANA_CREG0_OVRD`, `_CREG1_OVRD`
  - These expose analog enable/status bits for RX clocks, DCC, VREG, bleeder, AFE, loopback, bypass slicer, DFE, data rate, CDR/VCO, word clock, async reset, calibration result, scope data, VCO counter, ATB measurement, signal detect, power, deserializer, loopback, term enable, VREG boost, ring control, VDAC common-mode, slicer scope ranges, and reserved override masks.
- Raw TX PCS/FW/IRQ/control/PMA registers:
  - `C20_PHY_CR3_RAWLANEX_DIG_TX_PCS_XF_*`
  - `C20_PHY_CR3_RAWLANEX_DIG_TX_FW_XF_*`
  - `C20_PHY_CR3_RAWLANEX_DIG_TX_IRQ_CTL_*`
  - `C20_PHY_CR3_RAWLANEX_DIG_TX_CTL_*`
  - `C20_PHY_CR3_RAWLANEX_DIG_TX_PMA_XF_*`
  - These cover lane loopbacks, reset/req/data-enable/invert/rate/width/pstate/LPD/MPLLB/PLL/equalization overrides, ACK outputs, context config, firmware request/ack and lane number, TX rate/req/reset/loopback/RTUNE/term/lane-mode IRQ mask/status/clear bits, FSM IRQ enables, TX clock select, term code, FW power-up done, MPLLA/MPLLB resistor calibration, PMA PLL enables, and RTUNE handshakes.
- Raw RX PCS/FW/IRQ/control/PMA registers:
  - `C20_PHY_CR3_RAWLANEX_DIG_RX_PCS_XF_*`
  - `C20_PHY_CR3_RAWLANEX_DIG_RX_FW_XF_*`
  - `C20_PHY_CR3_RAWLANEX_DIG_RX_IRQ_CTL_*`
  - `C20_PHY_CR3_RAWLANEX_DIG_RX_CTL_*`
  - `C20_PHY_CR3_RAWLANEX_DIG_RX_PMA_XF_*`
  - These cover RX reset/request/pstate/LPD/data/invert/CDR SSC/adaptation, margin IQ/in-progress/error/recal controls, width/rate/vco/DFE bypass/eq fields, FW adaptation acknowledgment and figure-of-merit/direction controls, margin IRQs, term code, continuous adaptation status, PPM drift, CDR detect state, PMA miscellaneous controls, adaptation mode enables, IQ/phase/margin code registers, rate IRQ ACK, and PMA request/reset/ack overrides.
- Raw lane FSM and always-on TX registers:
  - `C20_PHY_CR3_RAWLANEX_DIG_FSM_*`
  - `C20_PHY_CR3_RAWLANEAONX_DIG_TX_*`
  - These expose debug steering, firmware scratch state, breakpoint and memory monitors, fast/skip bits for TX/RX calibration paths, RX calibration status, SRAM recording, CCA counters, startup/continuous algorithm controls, HP protection, lane transceiver mode, initial power-up completion, disable override, and MPLLA/MPLLB DCC value banks.

## Control Flow

There is no runtime control flow in this chunk. Control flow is external and usually follows this pattern:

1. A DCN 3.2 component includes `dcn_3_2_0_offset.h` and this shift/mask header.
2. The caller selects an offset macro for a C20 PHY CR3 register and selects one or more `__SHIFT`/`_MASK` field macros from this header.
3. The AMDGPU/DCN register helper inserts or extracts a field value, typically through a read-modify-write sequence for MMIO registers.
4. Hardware interprets the written bits as PHY overrides, power and reset requests, firmware handshakes, IRQ controls, analog calibration knobs, margining controls, or status query selectors.

The register names imply several hardware flows even though the sequencing is not implemented in this file:

- Override programming generally requires writing a value field and its matching `*_OVRD_EN`, `*_OVRD_VAL`, or aggregate override enable field.
- IRQ handling has mask/enable/status/clear/ack register pairs for TX and RX events such as rate, reset, request, loopback, RTUNE, term control, lane mode, adaptation, and margining.
- Calibration and margining flows use request/start/update fields, done/status/error fields, and optional fast/skip controls in the FSM namespace.
- Firmware and PMA handshakes use `REQ`, `ACK`, `RESET`, power-up done, lane number, supervisor state, PLL enable, and RTUNE request/ack bits.

## State and Persistence Behavior

The macros themselves are stateless compile-time constants. They describe hardware state whose lifetime depends on the underlying register:

- Persistent configuration until reset or reprogramming: override enables, lane link number, pstate/rate/width settings, clock selects, term codes, adaptation modes, PMA miscellaneous controls, analog CREG settings, VREG boost/ring/trim controls, DCC range/full/half bank values, and fast/skip calibration flags.
- Transient command or pulse-like state: update clocks, start/clear bits, IRQ clear bits, FSM command start, RTUNE request, margining start/error-clear, SRAM record enable, and calibration enable fields. Some fields explicitly include `SELF_CLEAR_DISABLE`, indicating hardware normally self-clears a strobe unless disabled.
- Status and observation state: IRQ status bits, ACKs, FW state snapshots, firmware scratch registers, calibration result, scope data, VCO counter, CDR detect state, PPM drift valid, adaptation FOM, phase/IQ readback, memory monitor, FSM status, RX calibration status, and DCC bank readback-style values.
- Reserved fields are represented with masks, often covering the majority of a 16-bit register. Their presence supports generated table completeness, but they should not be treated as safe writable fields by ordinary driver code.

## Dependencies

This header chunk depends on the AMDGPU/DCN generated register stack:

- Matching register offsets in `drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`.
- AMDGPU/DCN field access macros and helpers that expect the generated `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming convention.
- The generated DCN 3.2 hardware register database for C20 PHY CR3.
- Consumers in AMD display, DMUB, GPIO, IRQ, clock, resource, and low-level GPU initialization code that include the DCN 3.2 register headers.

The chunk is source-tree aligned with the Linux AMDGPU display driver. It is not Ceph-specific despite living under `sources/distributed-fs/ceph-client`; the path reflects the repository corpus layout.

## Integration Points

Likely integration points are:

- Link bring-up and power sequencing, where TX/RX reset, request, pstate, rate, width, data enable, PLL selection, and power-up done fields are programmed or observed.
- Display PHY training and calibration, where CDR/VCO, DCC, IQ/IQC, CTLE/VGA/ATT, DFE, slicer, termination, VREG, and adaptation fields affect signal integrity.
- Firmware-mediated PHY control, where FW crossbar fields and FSM scratch/status registers synchronize host, firmware, and PMA/PCS state.
- Interrupt service paths for TX/RX rate, reset, request, loopback, term-code, lane-mode, adaptation, and margining events.
- Debug and validation tools that use loopback, scope, ATB measurement, SRAM recording, breakpoints, FSM override/jump, fast-path flags, skip-calibration flags, margining deltas, and status counters to isolate PHY problems.
- Always-on TX calibration retention, where `RAWLANEAONX` DCC bank values and state snapshots may survive across lower-power lane transitions depending on hardware reset domain behavior.

## Risks and Edge Cases

- Generated mask/shift drift would silently corrupt MMIO field access. This is high-risk for PHY reset, PLL, VCO/CDR, DCC, analog CREG, margining, IRQ clear, and FSM override fields.
- Many controls are value/enable pairs. Setting only the value does nothing; leaving the enable set can pin hardware away from automatic firmware or PCS/PMA control.
- Directional suffixes matter. `OVRD_IN`, `OVRD_OUT`, `IN`, `OUT`, `STAT_IN`, `STAT_OUT`, `FW_XF`, `PCS_XF`, and `PMA_XF` describe different hardware sides of a crossing and can be easy to confuse in call sites.
- Register fields are mostly 16-bit but not uniformly single-bit. Multi-bit fields such as VCO config, PPM drift, margin deltas, term code, breakpoints, ATB measurements, and DCC banks require masking before shifting.
- `*_CLR` and `*_ACK` fields may have write-one-to-clear or handshake semantics controlled by hardware. Blind read-modify-write behavior can lose events if callers do not follow the hardware protocol.
- `SELF_CLEAR_DISABLE` bits change strobe behavior. Diagnostic code that disables self-clear must restore expected behavior or later calibration/margining pulses may remain asserted.
- FSM override and jump controls are powerful debug hooks. Incorrect use can halt or redirect PHY firmware state machines and break link training or recovery.
- Always-on DCC banks are repeated across MPLLA/MPLLB and bank 0-3 with very similar names. Copy/paste mistakes can program the wrong PLL or bank while still compiling cleanly.
- Reserved-bit masks should not be used as normal fields. Full-register writes need known reset/default values to avoid toggling reserved hardware behavior.

## Test Signals

Useful validation signals for code using this chunk:

- Compile coverage for DCN 3.2 with this header and the matching offset header to catch renamed or missing generated macros.
- Generated consistency checks that verify each non-reserved field has both a `__SHIFT` and `_MASK`, masks align with shifts, and fields in a register do not overlap unexpectedly.
- Representative field insert/extract tests for multi-bit fields: RX VCO config, RX AFE CTLE/VGA/ATT controls, term code, TX/RX pstate/rate/width, PPM drift, margin deltas, FSM jump address, breakpoint address, and DCC CM/DIFF bank values.
- Hardware smoke tests for link training, hotplug, mode set, suspend/resume, and display link recovery to catch stale override enables and incorrect power/reset sequencing.
- IRQ tests that assert status, mask, clear, and ACK behavior for TX/RX rate/reset/request, adaptation, and margining events.
- PHY diagnostics that exercise loopback, RTUNE, VCO/CDR/DCC/IQC calibration, margin IQ/VDAC starts, SRAM recording, and FSM status reads.
- Register readback or trace validation confirming that `RAWLANEX` and `RAWLANEAONX` repeated bank fields are written to the intended PLL/bank combination.

## Chunk Boundary Notes

The first visible lines complete `C20_PHY_CR3_LANEX_DIG_ANA_XF_RX_VCO_OVRD_OUT_0`, whose earlier shift definitions are in the previous chunk. The last visible block ends inside `C20_PHY_CR3_RAWLANEAONX_DIG_TX_MPLLB_DCC_HALF_BANK_3`; its remaining mask definitions are expected in the following chunk. The merge/reconciliation lane should combine this report with adjacent chunks before producing the final per-file research document for `dcn_3_2_0_sh_mask.h`.
