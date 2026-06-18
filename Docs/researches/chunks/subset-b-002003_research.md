# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 180624-183117

## Purpose

This chunk is a generated AMD DCN 3.2.0 shift/mask header slice. It contains C preprocessor register-field metadata only: `__SHIFT` macros for field low-bit positions, `_MASK` macros for raw bit masks, and `//<REGISTER>` comments that group the macros by hardware register. There are no C functions, structs, enums, runtime branches, allocations, locks, or direct MMIO accesses in this range.

The range covers DPCS/PHY `C20_PHY_CR3` register metadata. It starts in the tail of always-on lane 2 receive startup calibration control, then defines the rest of lane 2 receive calibration, adaptation, status, override, and input/output fields. It then covers always-on lane 3 transmit calibration/control definitions and a large portion of lane 3 receive calibration/adaptation definitions. The final lines enter generic `C20_PHY_CR3_LANEX_DIG_ASIC_*` lane/TX override metadata and stop part-way through `C20_PHY_CR3_LANEX_DIG_ASIC_TX_OVRD_IN_0`.

The source tree path is under a local `ceph-client` mirror, but this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

This chunk is boundary-partial at both ends. Line 180624 is already inside the mask tail of `C20_PHY_CR3_RAWLANEAON2_DIG_RX_STARTUP_CAL_ALGO_CTL_0`; its register comment and shift definitions are in the previous chunk. Line 183117 stops after `C20_PHY_CR3_LANEX_DIG_ASIC_TX_OVRD_IN_0__LPD_OVRD_EN_MASK`; the rest of that register and following LANEX ASIC fields continue in the next chunk.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field low bit.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.
- `//<REGISTER>` comments identify the hardware register whose fields follow.

Within this 2,494-line range there are 2,072 `#define` lines, including 1,036 shift macros and 1,042 mask macros. The shift/mask counts differ because the range starts and ends in the middle of larger register definitions.

Major register families in this chunk include:

- `C20_PHY_CR3_RAWLANEAON2_DIG_RX_*`: always-on lane 2 receive startup calibration/adaptation skip controls, continuous algorithm skip controls, fast-mode flags, VGEN/signal-detect/AFE/reference/DFE offset registers, VDAC/IDAC trim fields, DCC and IQ calibration banks 0-3, selected DCC/IQ code readbacks, calibration done bits, IQ controls, adaptation limits/modes, ATT/VGA/CTLE/DFE tap adaptation banks 0-1, DFE tap1 offset-valid bits, adaptation done/reference-error banks, TX equalization direction and thresholds, raw `ADPT_CTL_0..28` values, IQ margin range, CDR detector/recovery controls, RX/PMA overrides, and RX input/output status.
- `C20_PHY_CR3_RAWLANEAON3_DIG_TX_*`: always-on lane 3 transmit firmware state, breakpoint, SRAM record controls, CCA loop/wait counters, startup/continuous algorithm skip controls, fast TX flags, high-power-protection and transceiver-mode inputs/overrides, initial power-up done, TX disable override, MPLLA/MPLLB DCC bank values 0-3, MPLLA/MPLLB calibration-done banks, aggregate TX calibration done bits, selected DCC code readbacks, calibration bank select, and TX input disable.
- `C20_PHY_CR3_RAWLANEAON3_DIG_RX_*`: always-on lane 3 receive metadata that mirrors the lane 2 RX family through startup/continuous algorithm controls, offsets, DCC/IQ calibration banks, selected code readbacks, IQ controls, adaptation banks 0-1, TX equalization thresholds, `ADPT_CTL_0..28`, IQ margin, CDR controls, RX/PMA overrides, and RX input/output status.
- `C20_PHY_CR3_LANEX_DIG_ASIC_*`: generic lane and TX ASIC override fields at the end of the slice. Visible fields include lane loopback/transceiver-mode overrides and the beginning of TX override input 0 for clock-ready, reset, invert, data-enable, request, low-power-detect, and pstate override value/enable bits.

Common field categories include `SKIP_*` calibration/adaptation controls, `FAST_*` acceleration flags, banked calibration data (`BANK_0..BANK_3`), selected code readbacks (`*_CODE`), `CAL_DONE` and `ADAPT_DONE` status, override value/enable pairs (`*_OVRD_VAL` / `*_OVRD_EN`), PMA override output controls, raw input/status mirrors, and explicit reserved fields such as `RESERVED_15_8` or `RESERVED_15_14`.

## Control Flow

There is no executable control flow in this header. Runtime behavior is indirect:

1. DCN 3.2.0 driver code includes `dcn_3_2_0_offset.h` for register addresses and this file for matching field shifts and masks.
2. Display Core and DMUB register-list macros expand these constants into per-block register tables or field descriptors.
3. Register helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use the numeric constants when building masked MMIO operations.
4. Hardware state machines, link-training code, firmware, and interrupt/status logic provide the actual ordering and side effects.

The macros do not encode sequencing. Consumers must still perform PHY bring-up, calibration, adaptation, bank selection, CDR detection, margining, override programming, and status polling in the order required by the hardware programming model.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state for the DCN 3.2 PHY:

- Lane 2 and lane 3 RX startup/continuous calibration controls, fast modes, signal-detect settings, analog offset/trim values, DCC/IQ calibration banks, selected calibration code readbacks, adaptation coefficients, DFE tap offsets, CDR detector/recovery controls, and RX/PMA override/input/output latches.
- Lane 3 TX firmware state, SRAM recording/debug registers, CCA counters, calibration skip and fast-mode controls, high-power and lane-mode override inputs, MPLLA/MPLLB DCC calibration banks, calibration done status, selected DCC code readbacks, and TX input disable state.
- Generic LANEX lane/TX override state for loopback, transceiver mode, clock readiness, reset, inversion, data enable, request, low-power detect, and pstate controls.

Persistence and side effects are hardware-defined. Some fields are configuration bits that may remain until a modeset, retrain, power transition, suspend/resume, or ASIC reset. Other fields are status latches, read-only telemetry, write-one-to-clear bits, self-clearing triggers, firmware-owned scratch/debug state, or banked calibration data selected by rate or operating mode. This generated mask file does not encode access type, reset value, volatility, or ownership.

## Dependencies And Integration Points

This header must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which supplies the corresponding DCN 3.2.0 register offsets. Shift/mask drift can compile successfully while making masked register reads or writes touch the wrong hardware bits.

Direct include sites for the DCN 3.2.0 offset and mask headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`

Functional integration points include:

- DCN32 resource construction, where generated register/field constants are gathered into display block descriptors.
- DMUB/DCN32 initialization, where register-field metadata is exposed to firmware-facing helpers.
- Display PHY and link-training paths that program TX/RX startup, power state, rate/width, DCC/IQ calibration, receiver adaptation, CDR, and margining controls.
- Diagnostic and debug paths that inspect firmware states, SRAM recording controls, calibration done bits, selected DCC/IQ codes, adaptation banks, and override/input/output mirrors.
- Generic LANEX ASIC override handling, where lane/TX override value and enable pairs can force behavior normally driven by firmware or hardware state machines.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A single wrong shift or mask can build cleanly while corrupting PHY programming, calibration readback, override behavior, link training, or debug output.
- This range is not a standalone logical unit. It starts in the tail of lane 2 RX startup calibration control and ends in the middle of LANEX TX override input 0.
- Lane domains are easy to confuse. `RAWLANEAON2`, `RAWLANEAON3`, and `LANEX` are distinct namespaces; a syntactically valid macro from the wrong lane family can silently target the wrong hardware state.
- Banked calibration fields must be kept aligned with bank selection and rate/mode context. Mixing `BANK_0..BANK_3`, full/half-rate DCC fields, differential/common-mode readbacks, or lane 2/lane 3 definitions can produce plausible but wrong calibration data.
- `SKIP_*` and `FAST_*` fields trade initialization latency against calibration/adaptation coverage. Wrong values can create failures that only reproduce at specific link rates, lane widths, temperatures, voltage corners, retrain paths, or suspend/resume cycles.
- Override value/enable pairs can force reset, request, power, transceiver-mode, PMA, RX signal-detect, and TX behavior. Leaving override-enable bits asserted can fight firmware or hardware state machines.
- Status, done, clear, trigger, configuration, and firmware-owned fields look identical at the preprocessor level. Callers need external access-type knowledge before writing to fields such as `CAL_DONE`, `ADAPT_DONE`, CDR status, and override outputs.
- Reserved masks are explicit in the generated output. Masked writes should preserve reserved bits unless the hardware specification explicitly requires otherwise.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU Display Core with DCN32 support enabled. Broken generated symbols should surface in DCN32 resource, DMUB, IRQ, GPIO, clock, and low-level register users.
- Mechanically compare this range against the authoritative AMD register database or a regenerated `dcn_3_2_0_sh_mask.h`; every visible field should have the expected shift and mask.
- Cross-check the companion `dcn_3_2_0_offset.h` so `C20_PHY_CR3_RAWLANEAON2`, `C20_PHY_CR3_RAWLANEAON3`, and `C20_PHY_CR3_LANEX` register names remain aligned between offsets and masks.
- On DCN32 hardware, exercise DisplayPort/eDP link bring-up and retraining across rates, lane widths, pstate changes, hotplug, suspend/resume, and low-power transitions.
- Inspect DCC/IQ calibration and adaptation telemetry before and after link training. Banked calibration values, selected code readbacks, `CAL_DONE`, `ADAPT_DONE`, CDR state, and RX output status should decode consistently.
- Test paths that use fast or skip calibration modes, because bad masks may only appear when a feature path bypasses normal calibration sequencing.
- Use register dumps around PHY bring-up, retrain, power transitions, and debug/override operations. Masked writes should affect only intended fields, reserved bits should remain stable, and lane 2/lane 3/LANEX values should not be swapped.

## Cross-Chunk Notes

The final per-file report should merge this chunk with the previous chunk for the beginning of `C20_PHY_CR3_RAWLANEAON2_DIG_RX_STARTUP_CAL_ALGO_CTL_0` and with the following chunk for the rest of `C20_PHY_CR3_LANEX_DIG_ASIC_TX_OVRD_IN_0` and subsequent LANEX ASIC fields. This document is intentionally limited to the assigned source range and should be treated as the source-tree-aligned chunk artifact for `subset-b-002003`.
