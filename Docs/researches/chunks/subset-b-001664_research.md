# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 19860-22381

## Scope

This chunk is a generated AMDGPU DCN 2.1 register shift/mask header slice. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. The exported surface is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macro contract used by AMD display register helpers to pack, update, and decode DCN 2.1 hardware register fields.

The range has 2,522 source lines, including 2,114 `#define` entries: 1,055 shift constants and 1,059 mask constants, plus 382 register/address-block comments. It starts in the middle of the `CM3_CM_SHAPER_RAMB_REGION_10_11` field group, covers the tail of DPP3 color-management shaper and 3DLUT fields, then moves through DPP3 perfmon, MPCC0-MPCC7, MPC global control/status/output fields, and MPCC OGAM0-2 output-gamma PWL/LUT fields. The chunk ends inside `MPCC_OGAM2_MPCC_OGAM_RAMB_END_CNTL2_B`, so some OGAM2 RAMB end fields continue in the following chunk.

## Purpose

The purpose of this slice is to describe exact bit positions and masks for several DCN 2.1 display pipeline blocks:

- `CM3_CM_SHAPER_RAMB_REGION_*`, `CM3_CM_MEM_PWR_*`, and `CM3_CM_3DLUT_*`: DPP3 color-management shaper RAM-B region metadata, shaper/HDR 3DLUT memory power state, 3DLUT mode/index/data/read-write control, output normalization, RGB output offset/scale, and CM test/debug access.
- `DC_PERFMON14_*`: DPP3 display performance counter and perfmon control/status/value registers.
- `MPCC0_MPCC_*` through `MPCC7_MPCC_*`: repeated multi-plane compositor combiner instances, including input selection, output pipe binding, blend mode, alpha/gain settings, stereo/multiview controls, update-lock status, background color, OGAM memory power control, stall interrupt status, and idle/busy/error status.
- `MPC_*`: global MPC clock/reset, CRC configuration/results, perfmon event enable, bypass background color, stall grace window, host-read throttling, update pending/taken/ack status, vertical-update lock set bits, and four MPC output mux/denormalization blocks.
- `MPCC_OGAM0_*`, `MPCC_OGAM1_*`, and the first part of `MPCC_OGAM2_*`: per-MPCC output gamma LUT mode/index/data/RAM control plus RAM-A and RAM-B piecewise-linear region layout for RGB channels.

The header lets generic display code name logical fields while this ASIC-specific file supplies the Renoir/DCN 2.1 bit layout. It is metadata for MMIO programming; it does not itself implement color, blending, CRC, perfmon, or update-lock behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important interface is the generated macro schema:

- `*_SHIFT` constants hold the low bit position of a named field.
- `*_MASK` constants hold the already-positioned bit mask for the same field.
- Register comments such as `//MPCC3_MPCC_CONTROL` group field macros by hardware register.
- Address-block comments such as `// addressBlock: dce_dc_mpc_mpcc3_dispdec` mark repeated hardware register windows.

Important field families include:

- Shaper/3DLUT fields: `CM3_CM_SHAPER_RAMB_REGION_12_13__CM_SHAPER_RAMB_EXP_REGION12_LUT_OFFSET`, `...NUM_SEGMENTS`, `CM3_CM_MEM_PWR_CTRL2__SHAPER_MEM_PWR_FORCE`, `CM3_CM_MEM_PWR_STATUS2__HDR3DLUT_MEM_PWR_STATE`, `CM3_CM_3DLUT_MODE__CM_3DLUT_MODE`, `CM3_CM_3DLUT_READ_WRITE_CONTROL__CM_3DLUT_WRITE_EN_MASK`, `CM3_CM_3DLUT_READ_WRITE_CONTROL__CM_3DLUT_CONFIG_STATUS`, and RGB output offset/scale fields.
- Perfmon fields: `DC_PERFMON14_PERFCOUNTER_CNTL__PERFCOUNTER_EVENT_SEL`, `...INC_MODE`, `...INT_EN`, `...ACTIVE`, `DC_PERFMON14_PERFCOUNTER_STATE`, `DC_PERFMON14_PERFMON_CNTL`, value high/low counters, and C-value interrupt/status fields.
- MPCC compositor fields: `MPCCn_MPCC_TOP_SEL`, `MPCCn_MPCC_BOT_SEL`, `MPCCn_MPCC_OPP_ID`, `MPCCn_MPCC_CONTROL__MPCC_MODE`, `...ALPHA_BLND_MODE`, `...GLOBAL_ALPHA`, `...GLOBAL_GAIN`, `MPCCn_MPCC_SM_CONTROL`, `MPCCn_MPCC_UPDATE_LOCK_SEL`, `MPCCn_MPCC_MEM_PWR_CTRL`, `MPCCn_MPCC_STALL_STATUS`, and `MPCCn_MPCC_STATUS`.
- MPC global fields: `MPC_SOFT_RESET__MPCC0_SOFT_RESET` through `MPCC3_SOFT_RESET`, `MPC_CRC_CTRL__MPC_CRC_EN`, `...SRC_SEL`, `...ONE_SHOT_PENDING`, `...UPDATE_LOCK`, `MPC_CRC_RESULT_AR/GB/C`, `MPC_PENDING_TAKEN_STATUS_REG1`, `MPC_PENDING_TAKEN_STATUS_REG3`, `MPC_UPDATE_ACK_REG5`, per-pipe `*_VUPDATE_LOCK_SET*`, and `MPC_OUT0_*` through `MPC_OUT3_*`.
- MPCC OGAM fields: `MPCC_OGAMn_MPCC_OGAM_MODE`, `...LUT_INDEX`, `...LUT_DATA`, `...LUT_RAM_CONTROL`, per-channel RAMA/RAMB start/slope/end controls, and repeated `RAMA_REGION_0_1` through `RAMA_REGION_32_33` plus `RAMB_REGION_*` region offset/segment masks.

Consumers generally do not reference these long macro names directly in algorithmic code. They are fed through helper macros such as `SF`, `SR`, `SRI`, `SRII`, `FD_MASK`, and `FD_SHIFT` to build register, shift, and mask tables for DCN objects.

## Control Flow

This header has no local control flow. Runtime behavior occurs in AMD display code that includes `dcn_2_1_0_offset.h` with this shift/mask header and then issues MMIO register reads/writes through register helper macros.

A typical control path is:

1. DCN 2.1 resource or block code includes the generated offset and mask headers.
2. Register-list macros in DPP, MPC, MPCC, OPP, IRQ, GPIO, audio, and DMUB-adjacent code paste register and field names into generated macro names.
3. Code constructs register/shift/mask tables for a hardware object instance, such as DPP3, MPCC3, MPC output 1, or MPCC OGAM1.
4. Runtime helpers such as `REG_SET`, `REG_SET_N`, `REG_UPDATE`, `REG_GET`, and indexed table loaders use the offsets from `dcn_2_1_0_offset.h` and the shifts/masks from this file to program or inspect hardware fields.

Control-sensitive flows represented by this slice include DPP shaper/3DLUT programming, DPP perf counter selection and sampling, MPCC tree composition and blend parameter updates, MPCC update-lock coordination, MPC CRC capture, update-pending/ack polling, vupdate lock set operations, MPC output mux/denormalization setup, and MPCC OGAM LUT/PWL programming.

The macros do not encode operation ordering, access permissions, volatility, write-one-to-clear semantics, double-buffering rules, or synchronization requirements. Callers must still know which fields are live status, sticky interrupt state, self-clearing command bits, read-only capability/status, or safe to update only while a pipe, MPCC, or LUT bank is idle/locked.

## State And Persistence Behavior

The file itself stores no state and performs no persistence. It describes hardware register state that persists in the display engine until changed by driver writes, hardware state machines, power management, modeset reprogramming, or reset.

State represented in this range includes:

- DPP color state: shaper RAM-B region offsets and segment counts, shaper/HDR 3DLUT SRAM power controls/status, 3DLUT mode and size, 3DLUT RAM selection/write enables, 30-bit access mode, output normalization, and RGB output offset/scale.
- DPP perfmon state: event selection, counter run/stop/interrupt control, counter current value selection, high/low counter values, C-value interrupt metadata, and perfmon state bits.
- Per-MPCC composition state: top/bottom inputs, OPP destination, blend mode, alpha blending mode, premultiplied-alpha flag, active-overlap behavior, background bit depth/color, bottom gain mode, global alpha/gain, stereo/multiview controls, update-lock selection/status, OGAM SRAM power state, stall interrupt state, and idle/busy/disabled/error flags.
- Global MPC state: clock-gating test controls, soft reset bits, CRC enable/source/stereo/interlace/update lock controls, CRC results, perfmon event enable, bypass background color, stall grace timing, host-read rate limiting, update pending/taken/ack state, vertical-update lock latches, output mux routing, and denormalization clamp/mode values.
- MPCC OGAM state: output-gamma mode, LUT index/data, RAM bank selection/write mask/config status, per-channel PWL start/end/slope/base controls, and RAMA/RAMB region offset/segment tables.

Some values are configuration latches, some are live hardware status, and some represent SRAM/LUT programming windows. Incorrect values can persist until the next full pipe programming sequence, LUT reload, modeset, suspend/resume recovery, power reset, or GPU reset.

## Dependencies And Integration Points

The direct companion for this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which provides matching register addresses and base indices. This file provides the bit layout inside those addresses.

Visible include sites for the DCN 2.1 generated header pair include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which builds Renoir/DCN 2.1 display resources and register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which uses generated register fields for interrupt source setup and acknowledge paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `hw_translate_dcn21.c`, which include the generated header for GPIO translation.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes the DCN 2.1 register definitions for DMUB-facing display support.

Important generic consumers and integration layers include:

- DPP color code and definitions under `display/dc/dpp/dcn10` and later DPP implementations, where `CM_3DLUT_*` and `CM_SHAPER_RAMB_*` fields are part of color pipeline register structures and LUT-loading sequences.
- MPC/MPCC code under `display/dc/mpc/dcn10`, `dcn20`, `dcn30`, and later versions, where MPCC control/status, output mux, CRC, denormalization, and OGAM fields are abstracted into `struct dcn*_mpc_registers`, `struct dcn*_mpc_shift`, and `struct dcn*_mpc_mask` tables.
- Hardware-sequencer and CRC diagnostics, which expose MPC CRC result registers through debug or validation paths.
- DC state/debug capture in `display/dc/dc.h`, where MPCC control and OGAM state are recorded as part of hardware state snapshots.

Although this repository path sits under `sources/distributed-fs/ceph-client`, the chunk is AMD display hardware metadata. It has no Ceph filesystem, distributed storage, networking, or on-disk persistence behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong mask or shift can compile cleanly but write the wrong bit, truncate a value, preserve stale bits during read/modify/write, fail to observe a status bit, or acknowledge the wrong event.

Color pipeline fields are visually sensitive. Incorrect `CM3_CM_SHAPER_RAMB_*`, `CM3_CM_3DLUT_*`, or MPCC OGAM masks can corrupt color management, HDR 3DLUT programming, shaper/OGAM PWL segmentation, LUT bank selection, or SRAM write enables. Symptoms may be subtle, such as banding or wrong gamma, or severe, such as bad HDR output after a modeset.

MPCC and MPC fields are topology-sensitive. Bad `MPCC_TOP_SEL`, `MPCC_BOT_SEL`, `MPCC_OPP_ID`, blend mode, alpha/gain, or output mux masks can route planes to the wrong compositor/output, break overlay blending, leave MPCCs busy/disabled, or produce black screens only for multi-plane, stereo, or multi-display configurations.

Update-lock, pending/taken, and ack fields are synchronization-sensitive. Misprogramming `MPCC_UPDATE_LOCK_SEL`, `MPC_PENDING_TAKEN_STATUS_REG*`, `MPC_UPDATE_ACK_REG5`, or `*_VUPDATE_LOCK_SET*` can make software believe an update was accepted before hardware has latched it, or leave updates blocked until a later vupdate/modeset.

Status and interrupt-like fields are easy to misuse. `MPCC_STALL_STATUS`, `MPCC_STATUS`, CRC one-shot pending/update lock, and perfmon interrupt/status fields include live or sticky state. A generic read/modify/write with a wrong mask can miss a stall, clear or fail to clear a condition, or poll forever on a status bit.

The repeated generated layouts are copy-regeneration hazards. MPCC0-MPCC7 should remain structurally aligned, and MPCC_OGAM0/1/2 RAMA/RAMB regions repeat the same field pattern. Any one-off width, shift, or mask difference should be treated as suspicious unless the ASIC register database explicitly documents it.

Chunk boundaries are artificial. This range starts after the beginning of `CM3_CM_SHAPER_RAMB_REGION_10_11` and ends at the beginning of `MPCC_OGAM2_MPCC_OGAM_RAMB_END_CNTL2_B`; the final file-level document should merge adjacent chunks before drawing conclusions about complete CM3 or MPCC_OGAM2 coverage.

## Test Signals

Useful validation signals are a mix of generated-header checks and DCN 2.1 display behavior:

- Build coverage for DCN 2.1 resource, IRQ, GPIO, DMUB, DPP, MPC, and hardware-sequencer code that includes `dcn_2_1_0_sh_mask.h`.
- Generated-register validation that every field in this chunk has a matching register address in `dcn_2_1_0_offset.h`, every mask is consistent with its shift and field width, and repeated MPCC/OGAM instances remain structurally consistent.
- DPP color tests covering shaper LUT/PWL programming, 3DLUT enable/disable, 30-bit LUT writes, HDR and SDR modes, color-management bypass, and suspend/resume or modeset LUT reload.
- MPCC composition tests with single-plane, overlay, cursor, alpha blending, global alpha/gain, background color, multi-display routing, and stereo/multiview modes.
- MPC output tests covering mux selection, denormalization clamps/modes, bypass background color, and output pipe changes across hotplug and full modesets.
- CRC and perfmon validation that one-shot and continuous CRC modes produce plausible changing results, perf counters count selected events, interrupts/status bits clear as expected, and update-lock status does not hang.
- Update synchronization tests that inspect pending/taken/ack state around surface, config, cursor, MPCC, and OPP updates, especially during vblank/vupdate, fast flips, and pipe enable/disable transitions.
- Power-management tests for shaper/HDR 3DLUT and MPCC OGAM memory power state across idle, display off/on, runtime power management, and resume.

Regression symptoms from bad constants include wrong colors, broken HDR/3DLUT/OGAM output, failed overlays or plane blending, black screens on specific pipe topologies, stale or stuck update locks, bad CRC/debug output, stuck perfmon counters, MPCC stall/error reports, or failures that affect only one repeated MPCC or OGAM instance.

## Cross-Chunk Notes

This is a generated constants-only chunk in the middle of `dcn_2_1_0_sh_mask.h`. Adjacent chunks own the beginning of the CM3 shaper RAM-B block and the continuation of MPCC_OGAM2 RAMB/end-region fields. The merge lane should treat this document as a source-tree-aligned slice of the full DCN 2.1 register-layout contract rather than as a standalone module.
