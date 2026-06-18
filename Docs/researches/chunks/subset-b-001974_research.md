# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 110030-112525

## Purpose

This chunk is a generated AMD DCN 3.2.0 register shift/mask slice. It contains C preprocessor metadata only: `__SHIFT` macros for register-field low-bit positions, `_MASK` macros for raw bit masks, and `//<REGISTER>` comments that group fields by hardware register. It has no executable functions, structs, enums, branches, allocations, locks, or direct MMIO accesses.

The range covers a DPCS/PHY-oriented part of the DCN register namespace. It starts in the tail of the raw lane 3 receive firmware crossbar output override register, then defines raw lane 3 receive firmware, interrupt, control, PMA-crossbar, and firmware-state-machine fields. It then moves into always-on lane 0 transmit and receive calibration/adaptation fields, and ends in the always-on lane 1 transmit DCC calibration banks. The source tree path is under a local `ceph-client` mirror, but this header is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

The chunk is boundary-partial at both ends. Line 110030 is already inside `C20_PHY_CR1_RAWLANE3_DIG_RX_FW_XF_OVRD_OUT_0` masks whose shifts and register comment begin in the previous chunk. Line 112525 stops after `C20_PHY_CR1_RAWLANEAON1_DIG_TX_MPLLB_DCC_HALF_BANK_2__DIFF_VAL_MASK`; bank 3, calibration-done, code-readback, and lane 1 receive fields continue in the following chunk.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field low bit.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.
- `//<REGISTER>` comments identify the hardware register whose fields follow.

Within this line range there are 2,496 `#define` lines, including 1,033 shift macros and 1,054 mask macros. The shift/mask counts differ because the chunk starts and ends inside larger generated register families.

Major register groups in this chunk include:

- `C20_PHY_CR1_RAWLANE3_DIG_RX_FW_XF_*`: receive firmware crossbar handshake and override fields, including `ADAPT_ACK`, `ADAPT_FOM`, TX pre/main/post direction fields, RX clock enables and resets, and `ACK` output status.
- `C20_PHY_CR1_RAWLANE3_DIG_RX_IRQ_CTL_*`: receive-side IRQ masks, enables, status bits, and clear bits for reset, request, rate, pstate, adapt request/disable, termination control, and RX margining start/init/finish/error/global events.
- `C20_PHY_CR1_RAWLANE3_DIG_RX_CTL_*`: lane 3 receive control/status fields for termination code, off-cancel/adaptation continuous status, adaptation mode/selection, PPM drift, CDR detector state, PMA misc control, margin deltas/status/error, FSM control, rate IRQ acknowledgment, IQ step/linear code read/write, and phase-adjust update enables.
- `C20_PHY_CR1_RAWLANE3_DIG_RX_PMA_XF_*`: PMA crossbar input/output and override fields for reset, request, pstate, low-power detect, rate, width, DFE bypass, adaptation request, delta IQ, and RX-valid/ACK paths.
- `C20_PHY_CR1_RAWLANE3_DIG_FSM_*`: firmware-state-machine override, jump-bank, control, memory breakpoint, address/status monitors, firmware configuration stage, scratch registers, CR lock, fast-mode flags, skip-calibration flags, and RX calibration status.
- `C20_PHY_CR1_RAWLANEAON0_DIG_TX_*`: always-on lane 0 transmit firmware-state, breakpoint, SRAM record, CCA wait/start counters, startup/continuous TX algorithm skip controls, fast TX flags, high-power protection, lane transceiver mode, power-up done, disable override, MPLLA/MPLLB DCC bank values, calibration-done flags, selected DCC code readbacks, calibration bank selection, and TX input disable.
- `C20_PHY_CR1_RAWLANEAON0_DIG_RX_*`: always-on lane 0 receive startup calibration skip controls, startup/continuous adaptation skip controls, fast RX flags, signal-detect/AFE/reference/DFE offsets, VDAC and IDAC trim fields, RX DCC banks, IQ calibration banks, adaptation banks for ATT/VGA/CTLE/DFE taps, DFE tap1 offset-valid banks, adaptation done and reference-error banks, TX equalization direction/threshold controls, raw adaptation control registers, IQ margin range, CDR detector/recovery controls, RX overrides, PMA overrides, and RX input/output handshakes.
- `C20_PHY_CR1_RAWLANEAON1_DIG_TX_*`: beginning of the always-on lane 1 transmit block, mirroring lane 0 TX state, SRAM record, CCA, algorithm-skip, fast TX, high-power protection, lane mode, power-up, disable override, and MPLLA/MPLLB DCC bank definitions through MPLLB bank 2.

The fields are mostly 16-bit register layouts. Many registers include explicit reserved fields such as `RESERVED_15_4`, `RESERVED_15_8`, or `RESERVED_15_1`, which matter for masked writes because they document bits that should not be unintentionally changed by generated helpers.

## Control Flow

There is no runtime control flow in this header. Runtime use is indirect and table-driven:

1. DCN 3.2.0 code includes `dcn_3_2_0_offset.h` for register addresses and this file for matching field masks and shifts.
2. Register-list and field-list macros in display code expand these definitions into per-block register tables or firmware-visible field tables.
3. Driver helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET` use the generated numeric constants when programming MMIO registers.
4. Hardware state machines, firmware interfaces, and interrupt/status latches implement the real sequencing and side effects.

The macros themselves do not encode ordering. Consumers still have to sequence raw-lane reset/request/ack handshakes, rate and pstate changes, RX adaptation requests, margining operations, IRQ mask/enable/clear operations, PMA override setup, FSM debug/override operations, SRAM recording, CCA waits, DCC calibration bank selection, and calibration done/status reads according to the DPCS/PHY programming model.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state in the display PHY:

- Raw lane 3 RX firmware-crossbar state for reset/request/ACK, adaptation request/FOM/ACK, RX valid override, RX clock enables, pstate/rate/width/DFE bypass overrides, and TX equalization direction feedback.
- Raw lane 3 IRQ state for masking, enabling, clearing, and observing RX reset, request, rate, pstate, adaptation, termination, and margining events.
- Raw lane 3 RX control state for CDR, PPM drift, margining, phase-adjustment, IQ code, adaptation mode/selection, PMA misc controls, and rate IRQ acknowledgment.
- Raw lane 3 FSM debug/configuration state for breakpoint registers, firmware scratch registers, CR locking, fast-mode capability flags, skip-calibration flags, and RX calibration status.
- Always-on lane 0 TX/RX calibration and adaptation state, including DCC banked full/half/common-mode/differential values, calibration-done flags, IQ calibration values, receiver offset/trimming values, adaptation coefficients, DFE tap offsets, TX equalization thresholds, CDR detection/recovery settings, and override inputs/outputs.
- Always-on lane 1 TX calibration setup state through the early MPLLB DCC bank definitions visible in this slice.

Persistence and side effects are hardware-defined. Some fields are configuration bits that may persist until modeset, link retrain, power gating, suspend/resume, or ASIC reset. Other fields are status, sticky interrupt, write-one-to-clear, self-clearing trigger, read-only telemetry, or firmware-owned scratch/breakpoint state. This generated mask header does not state access type, reset value, volatility, or side-effect rules; those properties must come from the register specification and the driver code that sequences access.

## Dependencies And Integration Points

This chunk must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which supplies the corresponding DCN 3.2.0 register offsets. A shift/mask mismatch can compile cleanly while causing masked writes or reads to touch the wrong bits.

Direct include sites for the DCN 3.2.0 offset and mask headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`

The same register names also appear in the generated DPCS 4.2.3 shift/mask header under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h`, indicating that this portion of the DCN header mirrors DPCS/PHY register metadata.

Functional integration points include:

- DCN32 resource construction, where generated register and field values are assembled into display block descriptors.
- DMUB/DCN32 initialization, where field masks and shifts are exposed to firmware-facing register helpers.
- IRQ service setup for DCN32, where shared generated field definitions are part of the register ABI used by interrupt tables, even though this PHY lane IRQ family is not necessarily referenced by hand-written long macro names.
- Display PHY/link-training and low-level bring-up paths that need reset/request/ACK handshakes, pstate/rate/width/DFE-bypass settings, adaptation requests, margining events, DCC calibration, and calibration status decoding.
- Debug and diagnostic paths using FSM breakpoints, address/status monitors, firmware scratch registers, SRAM recording controls, margining status/error fields, and calibration telemetry.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can build successfully but corrupt PHY programming, IRQ handling, link-training state, calibration readback, or debug output.
- This range is not a standalone logical module. The first visible lines are the mask tail of `C20_PHY_CR1_RAWLANE3_DIG_RX_FW_XF_OVRD_OUT_0`, and the last visible lines stop mid-way through the lane 1 TX DCC bank family.
- The repeated lane/register patterns are easy to misindex. `RAWLANE3`, `RAWLANEAON0`, and `RAWLANEAON1` name distinct lane/address domains; using a valid macro from the wrong lane can silently target the wrong hardware lane.
- Interrupt fields mix mask, enable, status, and clear registers. Treating a status bit as a clear bit, or clearing before reading expected sticky state, can hide RX reset/rate/pstate/adaptation/margining events.
- Override fields can force hardware-controlled behavior. Misprogramming reset, request, pstate, rate, width, DFE bypass, adaptation request, RX valid, or TX high-power protection override bits can interfere with firmware state machines and link training.
- Calibration skip and fast-mode bits trade bring-up latency against calibration coverage. Incorrect `SKIP_*` or `FAST_*` fields can leave RX/TX calibration incomplete and cause failures that only appear under specific link rates, temperatures, voltage corners, suspend/resume cycles, or retraining paths.
- DCC and IQ calibration banks are banked by rate/selection. Mixing bank indices, half/full-rate values, common-mode/differential fields, or selected code readbacks can produce valid-looking but wrong calibration state.
- Reserved masks are explicit in the generated output. Driver writes must preserve reserved bits unless the hardware specification says otherwise.
- Access type is not encoded here. Status, clear, trigger, done, override, scratch, and configuration fields require external knowledge to avoid self-clearing, write-one-to-clear, or firmware-owned-state hazards.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU Display Core with DCN32 support enabled. Malformed generated symbols should surface in DCN32 resource, DMUB, IRQ, clock, GPIO, and low-level register users.
- Mechanically compare this range against the authoritative AMD register database or a regenerated `dcn_3_2_0_sh_mask.h`; every visible field should have the expected shift and mask.
- Cross-check the companion `dcn_3_2_0_offset.h` so `C20_PHY_CR1_*` register names, offsets, masks, and shifts stay aligned.
- Compare the mirrored DPCS 4.2.3 shift/mask definitions for the same `C20_PHY_CR1_RAWLANE3` and `RAWLANEAON*` register names when investigating generator drift.
- On DCN32 hardware, exercise DisplayPort link bring-up and retraining across rates, lane widths, power states, hotplug, suspend/resume, and DFE-bypass/adaptation scenarios.
- Check RX IRQ behavior around reset, request, rate change, pstate, adaptation request/disable, termination control, and margining events; status, mask, enable, and clear fields should decode consistently.
- Run margining and calibration diagnostics where available, watching RX margin start/init/finish/error/global events, margin status/error fields, IQ step/linear code readbacks, and DCC/IQ calibration banks.
- Inspect register dumps before and after PHY bring-up, retrain, power transitions, and debug operations. Masked writes should affect only intended fields, reserved bits should remain stable, and lane 0/lane 1/lane 3 values should not be accidentally swapped.

## Cross-Chunk Notes

The final per-file report should merge this chunk with the previous lines for the complete raw lane 3 firmware crossbar override definitions and with the following lines for the remainder of always-on lane 1 TX calibration and RX calibration/adaptation definitions. This document is intentionally limited to the assigned source range and should be treated as the source-tree-aligned chunk artifact for `subset-b-001974`.
