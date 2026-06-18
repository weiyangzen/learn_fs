# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 214674-217136

## Scope

This chunk is a generated register shift/mask portion of the AMD DCN 3.2 ASIC register header. It covers 2,463 lines of preprocessor constants for C20 PHY CR4 Display Core Next PHY registers, centered on raw always-on lanes 2 and 3 plus lane-X digital ASIC, TX power-control, TX statistics, LBERT, FIFO, and analog cross-forward TX register views.

The file is not executable code: it exposes register field metadata as `#define` constants. Each register block is introduced by a comment such as `//C20_PHY_CR4_RAWLANEAON3_DIG_RX_STARTUP_CAL_ALGO_CTL_0`, followed by one or more `__FIELD__SHIFT` constants and corresponding `__FIELD_MASK` constants. Most masks describe 16-bit register fields, including explicit `RESERVED_*` regions.

## Purpose

The purpose of this chunk is to provide compile-time bit positions and masks for DCN 3.2 display PHY programming. Driver code includes this header alongside `dcn_3_2_0_offset.h` so register access helpers can combine an address/offset macro with a field shift and mask macro. The constants let the AMD display and DMUB paths configure or inspect PHY calibration, adaptation, signal-detect, TX power state, TX equalization, loopback, clock alignment, and analog interface status without hard-coding raw bit numbers at every call site.

The scoped region is especially concerned with:

- `C20_PHY_CR4_RAWLANEAON2_DIG_RX_*`: tail of raw lane AON2 RX/TX equalization, adaptation controls, signal detect, CDR detection/recovery, RX override input/output, PMA override, and RX input/output observation.
- `C20_PHY_CR4_RAWLANEAON3_DIG_TX_*`: raw lane AON3 TX firmware state, SRAM recovery, startup/continuous calibration controls, fast flags, override inputs, DCC calibration bank values, calibration completion flags, and DCC code readbacks.
- `C20_PHY_CR4_RAWLANEAON3_DIG_RX_*`: raw lane AON3 RX startup/continuous calibration and adaptation skip controls, VDAC/IDAC offsets, DCC/IQ calibration banks, adaptation result banks, DFE tap offsets, signal-detect controls, CDR controls, and RX override/input/output observation.
- `C20_PHY_CR4_LANEX_DIG_ASIC_*`: lane-X digital ASIC-facing lane and TX override/input/output registers.
- `C20_PHY_CR4_LANEX_DIG_TX_PWRCTL_*`: TX power-state bit maps for P0/P0S/P1/P2 and power-up timing registers.
- `C20_PHY_CR4_LANEX_DIG_TX_*`: TX DCC/stat/clock-align/LBERT/FIFO register masks.
- `C20_PHY_CR4_LANEX_DIG_ANA_XF_TX_*`: digital-to-analog cross-forward TX overrides, DCC calibration controls, TX equalization override/status, and analog TX status outputs.

## Important APIs, Types, and Constants

There are no C functions, structs, enums, or runtime APIs in this chunk. Its API surface is the macro naming contract consumed by AMDGPU/DCN register access code.

Important macro forms:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset used to place or extract a field value.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate the field.
- `RESERVED_...` fields: generated masks documenting unused or reserved bits that should normally be preserved or ignored by driver writes.

Representative register families:

- RX adaptation and equalization: `DIG_RX_ADPT_CTL_0` through `_28`, `DIG_RX_ADPT_ATT_BANK_*`, `DIG_RX_ADPT_VGA_BANK_*`, `DIG_RX_ADPT_CTLE_BANK_*`, `DIG_RX_ADPT_DFE_TAP1_BANK_*` through `TAP5`, `DIG_RX_ADPT_IQ_*`, and `DIG_RX_ADPT_REF_ERR_*`.
- RX startup/continuous algorithm gating: `DIG_RX_STARTUP_CAL_ALGO_CTL_0/1`, `DIG_RX_STARTUP_ADAPT_ALGO_CTL_0`, `DIG_RX_CONT_ALGO_CTL`, and `DIG_RX_FAST_FLAGS`.
- RX calibration storage and readback: `DIG_RX_DCC_CTRL_RANGE_BANK_*`, `DIG_RX_DCC_FULL_*`, `DIG_RX_DCC_HALF_*`, `DIG_RX_IQ_CAL_BANK_*`, `DIG_RX_CAL_DONE_BANK_*`, `DIG_RX_DCC_*_CODE`, and `DIG_RX_CAL_DONE`.
- TX calibration storage and readback: `DIG_TX_MPLLA_DCC_*_BANK_*`, `DIG_TX_MPLLB_DCC_*_BANK_*`, `DIG_TX_MPLLA_CAL_DONE*`, `DIG_TX_MPLLB_CAL_DONE*`, `DIG_TX_DCC_*`, `DIG_TX_CAL_BANK_SEL`, and `DIG_TX_CAL_DONE`.
- RX/TX override surfaces: `DIG_RX_OVRD_IN_0`, `DIG_RX_OVRD_OUT_0`, `DIG_RX_PMA_OVRD_OUT_0`, `DIG_TX_OVRD_IN_0`, `DIG_ASIC_LANE_OVRD_IN`, `DIG_ASIC_TX_OVRD_IN_0` through `_5`, and `DIG_ANA_XF_TX_OVRD_OUT_0` through `_3`.
- TX power and timing: `DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, `P2`, `DIG_TX_PWRCTL_TX_PWRUP_TIME_0` through `_5`, `DIG_TX_PWRCTL_TX_CTL`, and `DIG_TX_PWRCTL_TX_STATUS`.
- TX diagnostics: `DIG_TX_STAT_*`, `DIG_TX_CLK_ALIGN_*`, `DIG_TX_LBERT_*`, `DIG_TX_LVL_CALC_STAT`, and `DIG_TX_FIFO_CTL`.

## Control Flow

This chunk has no direct control flow. It influences control flow indirectly by giving driver code named bit positions for hardware state-machine controls.

The likely runtime flow is:

1. DCN 3.2 display, DMUB, clock, GPIO, IRQ, resource, or lower-level GPU code includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Register helper macros/functions compute a register address from an offset macro.
3. Field values are shifted and masked with this header's constants for read-modify-write or field extraction.
4. Hardware state machines, not this header, execute the requested operation: lane power-up, DCC calibration, RX adaptation, CDR recovery, clock alignment, signal detection, TX/RX loopback, or diagnostic capture.

The skip/fast/control fields are notable because they change PHY sequencing: startup calibration skip bits can bypass RX AFE/ref/ATT/VGA/CTLE/IQ/phase/DFE/error/bypass/DCC routines; TX startup/continuous skip bits can bypass DCC calibration; fast flags select shortened calibration or power-up sequences. Completion/status masks then let callers poll whether calibration, adaptation, TX power-up, DCC compensation, or clock alignment finished.

## State and Persistence Behavior

The macros themselves are stateless. Persistence exists only in hardware registers programmed through these masks.

State categories exposed by this chunk:

- Configuration state: override enable/value pairs, skip bits, pstate bit fields, timing counters, CDR detector mode, signal-detect filter counters, DCC range selections, and LBERT/FIFO controls.
- Calibration result state: full/half-rate DCC codes, CM/differential values, IQ calibration values, per-bank calibration-done bits, VDAC/IDAC offsets, and DFE tap offsets.
- Adaptation result state: ATT/VGA/CTLE/DFE/IQ adaptation values, reference error samples, and per-bank adaptation-done bits.
- Observability state: RX/TX input/output mirrors, analog TX status, TX statistic counters, clock-align status, signal-detect outputs, and calibration status.

Several fields are named `SELF_CLEAR_DISABLE` or represent load/clock strobes, implying that the underlying register may self-clear unless explicitly disabled. Callers must follow the hardware programming guide's expected write/poll/order sequence; this header only names the bits.

## Dependencies and Integration Points

Direct compile-time dependencies are minimal: this header contains standalone preprocessor definitions and depends on consumers to include it in a C translation unit.

Key integration points found in the source tree include:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`

These consumers include both `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`, which is the standard AMD register-header pairing: offsets identify registers and this file supplies field masks/shifts. The same lane macro patterns also appear for raw lane AON0/AON1 and lane AONX elsewhere in the header, indicating this chunk is one slice of a repeated generated register map for multiple PHY lanes.

## Risks and Edge Cases

- Generated header drift: if offsets, masks, or shifts are regenerated from a different hardware database version without matching driver expectations, writes can silently target wrong bits.
- Reserved bits: many registers define `RESERVED_*` masks. Callers should avoid writing reserved bits and should use read-modify-write helpers when changing a single field.
- Lane specificity: AON2, AON3, and LANEX names are similar but not interchangeable. Using an AON3 mask with an AON2 offset, or a lane-X aggregate mask with a raw-lane offset, can corrupt unrelated PHY state.
- Bank selection: DCC, IQ, RX adaptation, and calibration completion fields are repeated across banks 0-3. Code that changes `*_CAL_BANK_SEL` or reads per-bank results must keep bank selection and readback macros aligned.
- Override enable/value coupling: many override registers have paired value and enable fields. Setting a value without its `*_OVRD_EN` bit may have no effect; setting enable with an unintended stale value can force bad PHY behavior.
- Timing fields: TX power-up timing masks include large counters and fast-path bits. Incorrect values can cause unstable link bring-up, missed RX detect, or power sequencing issues.
- Self-clearing controls: fields such as load clocks, term-code clocks, and calibration controls may be pulse-like. Tests need to account for write-one/self-clear behavior rather than expecting a stable readback value.
- Hardware-only validation: most behavioral correctness cannot be proven by unit tests because the final effect is a PHY state-machine transition on specific DCN 3.2 ASICs.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware integration oriented:

- Build coverage for all DCN 3.2 consumers that include `dcn_3_2_0_sh_mask.h`; missing/renamed macros should fail at compile time.
- Static checks that paired `__SHIFT` and `_MASK` values cover expected field widths and do not overlap unexpectedly, especially in generated update reviews.
- Hardware smoke tests for display link bring-up on DCN 3.2 boards, including hotplug, modeset, suspend/resume, and link retraining.
- PHY-specific debug validation of RX signal detect, CDR recovery, RX adaptation completion, TX calibration completion, DCC code readback, and TX power state transitions.
- Regression tests around fast flags and skip controls, because those fields directly alter calibration sequencing.
- Diagnostics that exercise LBERT, clock alignment, TX statistic counters, FIFO status, and analog TX status readback when available on test hardware.

## Summary

This chunk is a dense generated bitfield map for DCN 3.2 C20 PHY CR4 lane-level RX/TX control and observability. Its practical value is naming hardware register fields precisely enough for AMD display and GPU code to program calibration, adaptation, power sequencing, overrides, and diagnostics through shared register helper infrastructure. The main engineering risks are wrong-lane macro use, reserved-bit writes, stale generated data, bank-selection mistakes, and misunderstanding override or self-clearing field semantics.
