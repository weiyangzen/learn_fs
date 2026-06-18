# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 144083-146570

## Purpose

This chunk is a generated AMD DCN 3.2.0 shift/mask header slice. It contains C preprocessor definitions only: `__SHIFT` constants for field bit positions, `_MASK` constants for in-register bit masks, and `//<REGISTER>` comments that group fields by hardware register. There are no functions, structs, enums, branches, loops, allocations, locks, or direct MMIO operations in this range.

The range describes C20 PHY CR2 raw-lane and always-on lane register fields used by DCN/DPCS display PHY programming. It starts at the tail of the raw lane 3 firmware-state-machine receive calibration skip/status area, then covers always-on lane 0 TX and RX calibration/adaptation blocks, then mirrors always-on lane 1 TX calibration and starts always-on lane 1 RX calibration/adaptation. The source path is under a local `ceph-client` mirror, but this code is AMDGPU display hardware metadata, not distributed filesystem logic.

This is a boundary-partial chunk. The first visible line is the remaining `_MASK` for `C20_PHY_CR2_RAWLANE3_DIG_FSM_SKIP_RX_DCC_RANGE_RATE_CAL`, whose register heading and shifts are in the previous chunk. The last visible line ends at `C20_PHY_CR2_RAWLANEAON1_DIG_RX_DFE_DOH_TAP1_OFST_BANK_0__DFE_DOH_TAP1_OFST_MASK`; the reserved mask and later lane 1 RX DFE offset/adaptation registers continue in the following chunk.

## Important APIs, Types, And Macros

The exported interface is the generated register-field macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw mask for the field.
- `//<REGISTER>` comments identify the hardware register whose field macros follow.

This assigned line range has 2,074 `#define` lines: 1,036 shift macros and 1,038 mask macros, grouped under 414 visible register headings. The counts are uneven because the range begins and ends inside larger generated register families.

Major macro groups in this chunk include:

- `C20_PHY_CR2_RAWLANE3_DIG_FSM_*`: receive calibration skip controls for DCC range, VGA, CTLE, ATT, and margining, plus `RX_CAL_STATUS` with `RST_CAL_DONE`.
- `C20_PHY_CR2_RAWLANEAON0_DIG_TX_*`: always-on lane 0 TX firmware state bits, TX memory breakpoint, SRAM recording controls/counters/addresses, CCA loop/wait counters, startup/continuous TX algorithm skip bits, fast TX capability flags, high-power protection input/override fields, lane transceiver mode fields, power-up done, disable override, MPLLA/MPLLB DCC bank values, per-bank calibration done flags, aggregate calibration done status, selected DCC code readbacks, calibration bank selection, and TX input disable.
- `C20_PHY_CR2_RAWLANEAON0_DIG_RX_*`: always-on lane 0 RX startup calibration and adaptation skip controls, continuous algorithm controls, fast RX flags, signal-detect and AFE/reference/DFE offset controls, VDAC/IDAC trim fields, DCC and IQ calibration banks, calibration done banks, selected DCC/IQ code readbacks, adaptation banks for ATT/VGA/CTLE/DFE taps, DFE tap1 offset banks, adaptation-done/reference-error banks, TX equalization polarity/threshold controls, `ADPT_CTL_0` through `ADPT_CTL_28`, IQ margin range, CDR detector/recovery controls, RX override input/output fields, signal-detect filters, PMA override output, and RX input/output status bits.
- `C20_PHY_CR2_RAWLANEAON1_DIG_TX_*`: always-on lane 1 TX definitions mirroring lane 0 TX, including firmware state, SRAM recording, CCA counters, startup/continuous algorithm controls, fast flags, high-power and transceiver mode controls, DCC banks for MPLLA/MPLLB, calibration done flags, DCC code readbacks, bank selection, and TX input disable.
- `C20_PHY_CR2_RAWLANEAON1_DIG_RX_*`: beginning of always-on lane 1 RX, covering startup calibration/adaptation skip controls, continuous algorithm controls, fast flags, offset/trim controls, RX DCC/IQ calibration banks through bank 3, selected DCC/IQ/cal-done readbacks, IQ/adaptation limits, initial bank 0 adaptation values, and the start of DFE tap1 offset banks.

Most registers in this range are 16-bit PHY control/status layouts. Common field shapes include one-bit enable/status fields, 2-4 bit selectors or range codes, 6-13 bit adaptation/tap values, paired common-mode/differential 8-bit values, half/full-rate 8-bit values, and explicit reserved masks such as `RESERVED_15_1`, `RESERVED_15_4`, `RESERVED_15_8`, and `RESERVED_15_12`.

## Control Flow

There is no runtime control flow in this header. Runtime behavior is indirect:

1. DCN 3.2.0 display code includes this file for field masks/shifts and `dcn_3_2_0_offset.h` for register offsets.
2. Register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_GET_FIELD`, and local field-list helpers combine register addresses with these masks and shifts.
3. The display driver, DMUB-facing code, link encoder/PHY code, IRQ setup, GPIO/resource construction, and diagnostics decide the actual sequencing.
4. Hardware and firmware implement the state machines, calibration algorithms, adaptation loops, interrupt/status behavior, and side effects.

The macros do not encode ordering requirements. Consumers must still sequence TX/RX power-up, calibration skip settings, CCA waits, DCC bank selection, calibration done polling, RX adaptation, DFE tap handling, signal-detect overrides, CDR settings, PMA overrides, and link training according to the PHY programming model.

## State And Persistence Behavior

This chunk stores no software state and has no persistence of its own. It describes MMIO-backed display PHY state:

- TX firmware/debug state: firmware state bits, memory breakpoint enable/address, SRAM recording state, CCA wait counters, fast-mode flags, high-power protection, transceiver mode, and disable/power-up controls.
- TX calibration state: MPLLA/MPLLB DCC range/full/half banks, common-mode and differential DCC values, per-bank calibration done flags, aggregate done bits, selected DCC code readback, and calibration bank selection.
- RX calibration state: startup calibration skip bits, DCC range/data/bypass/phase banks, half/full-rate DCC and IQ values, calibration done flags, selected code readbacks, and IQ calibration controls.
- RX adaptation state: ATT/VGA/CTLE/DFE tap adaptation values, DFE tap1 offset banks, adaptation done and reference-error banks, `ADPT_CTL_*` tuning registers, TX EQ direction/threshold fields, CDR detector/recovery fields, margin range, and signal-detect controls.
- Override and status state: RX/TX disable, termination, signal-detect, PMA override, VREF, RX input/output, and lane transceiver mode fields.

The persistence lifetime is hardware-defined. Some fields are configuration bits that may persist until link retrain, modeset, power gating, suspend/resume, or ASIC reset. Others are read-only status, sticky status, write-one-to-clear bits, trigger/self-clearing fields, firmware-owned scratch/debug state, or calibration readbacks. This generated header does not declare access type, reset values, volatility, ownership, or write side effects.

## Dependencies And Integration Points

This file is part of the generated DCN 3.2.0 register ABI and must remain aligned with the corresponding address definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h` and the hardware register database used to generate both files. The offset header exposes nearby CR2 raw-lane IRQ and lane status offsets, while many long calibration/adaptation field names in this slice are not directly referenced by handwritten C code in this repository; they are still part of the generated namespace available to table-driven or low-level register helpers.

Direct include sites for `dcn_3_2_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`

Functional integration points include:

- DCN32 resource and hardware factory code that builds register/field tables for display blocks.
- DMUB/DCN32 initialization paths that expose register fields to firmware-mediated display control.
- Display PHY/link bring-up, retraining, and diagnostics that use TX/RX calibration, DCC, signal-detect, CDR, and adaptation fields.
- Debug workflows that rely on firmware state, SRAM recording, breakpoint, calibration done, and DFE/adaptation readback fields.
- IRQ and status infrastructure that shares the same generated field namespace, even when a specific long PHY calibration macro is not directly referenced by a handwritten call site.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can compile successfully but read or write the wrong PHY bit, causing link training, calibration, power management, or debug failures.
- The chunk is not standalone. It starts with the tail of a previous raw lane 3 FSM register and ends mid-way through lane 1 RX DFE offset definitions.
- Lane naming is easy to confuse. `RAWLANE3`, `RAWLANEAON0`, and `RAWLANEAON1` refer to different lane/address domains; using a valid macro from the wrong lane can silently program or decode the wrong hardware lane.
- TX and RX calibration families repeat similar names for MPLLA/MPLLB, bank 0-3, full/half rate, common-mode/differential, data/bypass/phase, and selected code readbacks. Off-by-one bank selection or mixing full/half values can produce plausible but wrong calibration state.
- `SKIP_*` and `FAST_*` fields trade bring-up speed for calibration coverage. Incorrect values can create temperature-, voltage-, rate-, or resume-dependent failures that do not appear in simple boot tests.
- Override fields can fight firmware or hardware state machines. Misusing disable, transceiver mode, signal-detect, termination, VREF, PMA, or high-power protection overrides can block link bring-up or keep PHY state latched incorrectly.
- Status/done fields and configuration fields share similar names. Treating done/readback bits as writable controls, or treating controls as status, can hide failures during diagnostics.
- Reserved masks are explicit and should be preserved on writes unless the hardware specification says otherwise.
- Access type is absent from this header. Consumers need external register documentation or known driver patterns to avoid write-one-to-clear, self-clearing trigger, read-only, firmware-owned, and sticky-status hazards.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU/DCN32 display code with warnings enabled; malformed generated names or missing field macros should surface in DCN32 include users.
- Mechanically compare lines 144083-146570 against the authoritative AMD register database or a regenerated `dcn_3_2_0_sh_mask.h`; every field should have the expected shift and mask.
- Cross-check the generated address/header set so CR2 lane/register names, offsets, shifts, and masks remain synchronized.
- On DCN32 hardware, exercise DisplayPort/PHY link bring-up, hotplug, retrain, link-rate changes, lane-width changes, power transitions, suspend/resume, and recovery after failed link training.
- Inspect register dumps around TX/RX calibration. DCC banks, IQ values, calibration bank selection, done flags, and selected readback codes should change consistently and remain lane-local.
- Run margining/adaptation diagnostics where available. ATT/VGA/CTLE/DFE values, DFE tap1 offsets, reference-error banks, adaptation done bits, CDR detector/recovery fields, and signal-detect output should decode with the expected masks.
- Verify masked writes preserve reserved bits and affect only the intended fields, especially for override, skip-calibration, fast-mode, and bank-selection registers.
- Exercise suspend/resume and low-power entry/exit paths to catch stale calibration, forced override, or incorrectly persisted PHY fields.

## Cross-Chunk Notes

The final per-file report should merge this chunk with the preceding CR2 raw lane 3 FSM definitions and the following lane 1 RX DFE/adaptation continuation. This document is intentionally limited to `subset-b-001988` and the assigned source range.
