# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h lines 2739-5274

## Scope

This chunk is a generated register-offset slice from the AMD DCN 3.5.0 ASIC register header. It covers 2,536 source lines and defines 1,194 register offset macros plus their matching `_BASE_IDX` macros for a middle portion of the DCN display register map. The chunk starts in the DCHUBBUB/COMPBUF area at `regDCHUBBUB_DCC_STAT2` and ends partway through the DPP2 CNVC configuration block at `regCNVC_CFG2_FCNV_FP_SCALE_R`.

The file is not executable code. Its exported interface is a dense set of `#define reg...` constants used by AMDGPU display code to build typed register tables and issue MMIO register accesses through shared register helper macros.

## Purpose

The purpose of this chunk is to provide DCN 3.5.0 register addresses for memory hub, hub pipe, cursor, DPP, scaler, color, and perfmon blocks. Runtime DC code combines these offsets with base-index information and field masks from `dcn_3_5_0_sh_mask.h` to read, write, poll, or initialize hardware registers without duplicating numeric addresses in each component implementation.

Major register families in this chunk are:

- DCHUBBUB arbitration, watermarks, self-refresh/Z8, p-state change, host VM, soft reset, clock, timeout, debug, DET, COMPBUF, and global timer registers.
- DCHUBBUB and HUBP/DPP `DC_PERFMON` counter register windows.
- HUBP0 through HUBP3 register groups, including `DCSURF`, `DCHUBP`, `HUBPREQ`, `HUBPRET`, cursor, timing-to-use, VM, prefetch, flip, status, clock, MALL, and memory-power registers.
- DPP0 and DPP1 full front-end register sets, including DPP top, CNVC pixel format/color conversion, CNVC cursor controls, DSCL scaler controls, CM color management, degamma, regamma/gamma correction RAMs, HDR multiplier, coefficient format, and memory-power/debug registers.
- The beginning of DPP2, covering DPP top and the first CNVC configuration offsets.

## Important APIs, Types, and Constants

There are no functions, structs, or enums in this chunk. The important API is the macro naming contract:

- `reg<REGISTER>` gives the ASIC register offset value, such as `regDCHUBBUB_ARB_DATA_URGENCY_WATERMARK_A` at `0x04fe`.
- `reg<REGISTER>_BASE_IDX` gives the base segment index used by display register helpers. Every macro in this chunk uses base index `2`.
- Address block comments identify the generated hardware block and base address, for example `dce_dc_dcbubp0_dispdec_hubpreq_dispdec` or `dce_dc_dpp1_dispdec_cm_dispdec`.

Representative constants and groups:

- DCHUBBUB watermarks: `regDCHUBBUB_ARB_DATA_URGENCY_WATERMARK_[A-D]`, `regDCHUBBUB_ARB_ALLOW_SR_ENTER_WATERMARK_[A-D]`, `regDCHUBBUB_ARB_ALLOW_SR_EXIT_WATERMARK_[A-D]`, `regDCHUBBUB_ARB_ALLOW_SR_ENTER_WATERMARK_Z8_[A-D]`, `regDCHUBBUB_ARB_ALLOW_SR_EXIT_WATERMARK_Z8_[A-D]`, `regDCHUBBUB_ARB_UCLK_PSTATE_CHANGE_WATERMARK_[A-D]`, and `regDCHUBBUB_ARB_FCLK_PSTATE_CHANGE_WATERMARK_[A-D]`.
- DCHUBBUB policy/control: `regDCHUBBUB_ARB_DF_REQ_OUTSTAND`, `regDCHUBBUB_ARB_SAT_LEVEL`, `regDCHUBBUB_ARB_QOS_FORCE`, `regDCHUBBUB_ARB_DRAM_STATE_CNTL`, `regDCHUBBUB_ARB_HOSTVM_CNTL`, `regDCHUBBUB_ARB_WATERMARK_CHANGE_CNTL`, `regDCHUBBUB_ARB_MALL_CNTL`, `regDCHUBBUB_SOFT_RESET`, and `regDCHUBBUB_CLOCK_CNTL`.
- HUBP surface programming: `regHUBP*_DCSURF_SURFACE_CONFIG`, `ADDR_CONFIG`, `TILING_CONFIG`, viewport start/dimension registers, request size configuration, `DCHUBP_CNTL`, `DCHUBP_VMPG_CONFIG`, `DCHUBP_MALL_CONFIG`, and MALL status.
- HUBPREQ scanout memory request programming: `regHUBPREQ*_DCSURF_*_SURFACE_ADDRESS`, high-address variants, meta-surface address variants, `DCSURF_SURFACE_CONTROL`, flip control and interrupt registers, in-use/earliest-in-use registers, VM aperture and L1 TLB registers, TTU/QoS/prefetch/nominal/flip/vblank parameter registers, per-line delivery registers, cursor settings, and status registers.
- HUBPRET read-line and return path registers: `regHUBPRET*_HUBPRET_CONTROL`, memory power control/status, read-line controls/values/status, and interrupt registers.
- Cursor registers: `regCURSOR0_*_CURSOR_CONTROL`, surface address, size, position, hot spot, stereo control, destination offset, memory power, DMDATA address/control/QoS/status/software registers.
- DPP top and CNVC registers: `regDPP_TOP*_DPP_CONTROL`, soft reset, CRC values/control, host read control, `regCNVC_CFG*_CNVC_SURFACE_PIXEL_FORMAT`, `FORMAT_CONTROL`, FP bias/scale, color keyer, alpha LUT, pre-dealpha, pre-CSC matrix coefficients, coefficient format, pre-degamma, and pre-realpha.
- DSCL scaler registers: coefficient RAM tap select/data, scaler mode/tap/control registers, 2-tap control, manual replicate, horizontal/vertical ratios and initial phases for luma/chroma, black color, update/autocal, overscan, OTG blanking, recout, MPC size, line-buffer data format, and memory power/status.
- CM color-management registers: post-CSC controls and matrices, output CSC mode and matrices, gamut-remap controls/matrices, 3D LUT control/memory, degamma and gamma-correction RAM A/B start/slope/base/end/offset/region registers for B/G/R, HDR multiplier, memory power/status, dealpha, coefficient format, and test-debug index/data.

## Control Flow

This header has no direct control flow. It affects runtime behavior when included by DCN 3.5 components:

1. A DCN 3.5 component includes `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Register-list macros such as `HUBBUB_REG_LIST_DCN35`, `HUBP_REG_LIST_DCN30_RI`, and `DPP_REG_LIST_DCN35_RI` expand these `reg...` constants into typed register tables.
3. Register helpers compute the final MMIO address as `BASE(reg..._BASE_IDX) + reg...`, where `BASE()` resolves through `ctx->dcn_reg_offsets`.
4. Component code writes or reads hardware through helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, or DMUB register access wrappers.
5. Hardware blocks then execute the requested operation: hubbub watermark changes, VM request behavior, surface flip programming, cursor update, scaler coefficient updates, color transform programming, memory power transitions, or perf counter capture.

The most control-sensitive macro groups are the flip/in-use registers, watermarks, p-state and self-refresh/Z8 thresholds, VM aperture/TLB registers, cursor state registers, DSCL update/autocal registers, CM LUT controls, and soft-reset/clock controls. Incorrect offsets in any of these groups change the runtime sequence even though this file itself only supplies constants.

## State and Persistence Behavior

The macros are compile-time constants and have no persistent state. Persistence exists in the hardware registers addressed by these constants.

State categories exposed by this chunk include:

- Memory hub scheduling state: watermarks, urgent bandwidth fractions, p-state thresholds, DRAM/self-refresh/Z8 controls, outstanding request limits, QoS force controls, and host VM controls.
- Surface state: pitch, primary/secondary addresses, chroma addresses, metadata addresses, tiling/viewport dimensions, surface control, flip control, in-use address snapshots, and earliest-in-use tracking.
- VM and MALL state: VMID settings, aperture low/high, TLB control, VMPG configuration, MALL configuration, MALL sub-viewport, and MALL status.
- Cursor state: cursor buffer addresses, size, position, hot spot, color/CNVC cursor settings, DMDATA controls, and cursor memory power status.
- Scaler and color pipeline state: DSCL ratios, filter phases, coefficient RAM access, line-buffer format, pre/post/output CSC matrices, gamut remap matrices, 3D LUT memory, degamma/regamma/gamma-correction RAMs, HDR multiplier, alpha/dealpha controls, and coefficient formats.
- Debug and observability state: CRC values, perfmon counters, status registers, timeout interrupt/status registers, memory power status registers, test-debug index/data, and surface check address registers.

Many of these registers are programmed during modeset, plane update, page flip, cursor update, power management, and color-management operations. Their values persist in the display engine until overwritten, reset, or lost through hardware power/reset transitions.

## Dependencies and Integration Points

This generated header is standalone at the preprocessor level, guarded by `_dcn_3_5_0_OFFSET_HEADER`, but it is useful only with the AMD DC register-helper ecosystem.

Direct integration points in this tree include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`, which includes this offset header and `dcn_3_5_0_sh_mask.h`, defines `BASE(seg)` through `ctx->dcn_reg_offsets`, and builds resource register tables for DPP, HUBP, HUBBUB, HWSEQ, OPP, DCCG, and related DCN 3.5 blocks.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, where `dmub_srv_dcn35_regs_init()` expands DMUB register lists into stored offsets, masks, and shifts for DMUB-facing DCN 3.5 access.
- `drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`, which includes the same register headers while mapping DCN interrupt source IDs to DAL IRQ sources, including HUBP flip interrupts.
- `drivers/gpu/drm/amd/display/dc/hubbub/dcn35/dcn35_hubbub.h`, whose `HUBBUB_REG_LIST_DCN35` consumes DCHUBBUB, COMPBUF, DCHVM, watermark, clock, and QoS offset names found in this file.
- `drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.h` and inherited DCN30/DCN32 HUBP resource macros, which consume the HUBP/HUBPREQ/HUBPRET/CURSOR offset families.
- `drivers/gpu/drm/amd/display/dc/dpp/dcn35/dcn35_dpp.h` and `drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.h`, which consume DPP top, CNVC, DSCL, and CM offset families through DPP register-list macros.

The offset macros are paired with field definitions in `dcn_3_5_0_sh_mask.h`. Offset-only correctness is insufficient: a consumer must use the offset from this file with the matching mask/shift from the same ASIC-generation header.

## Risks and Edge Cases

- Generated-header drift: if this file is regenerated from a hardware database that does not match `dcn_3_5_0_sh_mask.h` or the DCN 3.5 resource macros, code can compile while programming the wrong register fields.
- Instance alignment: HUBP0-3 and DPP0-2 offsets are repeated with fixed instance spacing. Copying an offset from the wrong instance can route a plane, cursor, scaler, or color update to the wrong pipe.
- Partial chunk boundary: this research chunk starts after earlier DCHUBBUB definitions and ends in the middle of DPP2 CNVC configuration. The final merged per-file research must combine adjacent chunks before drawing whole-file conclusions.
- Base-index dependence: every macro here uses `_BASE_IDX 2`; if platform base-offset tables are wrong, all addresses in this slice resolve incorrectly even though the raw `reg...` constants look correct.
- Surface address hazards: primary/secondary/meta surface address registers and in-use snapshots are timing-sensitive. Wrong offsets can produce scanout from stale or invalid memory.
- Watermark and p-state hazards: DCHUBBUB urgent, self-refresh, Z8, UCLK, and FCLK thresholds directly affect underflow risk and power transitions.
- Cursor and flip hazards: cursor surface/position registers and `DCSURF_FLIP_CONTROL`/interrupt registers are visible in common desktop workflows. Mistakes can produce cursor corruption, missed flips, or IRQ storms.
- Color/scaler hazards: CNVC/DSCL/CM offsets affect pixel format conversion, CSC matrices, scaling ratios, LUT programming, HDR multiplier, and gamma correction. A wrong offset can produce incorrect colors or blank/unstable output without an obvious kernel fault.
- Memory-power sequencing: HUBPREQ/HUBPRET/CURSOR/DSCL/CM memory power control and status registers need proper order and polling. Offset drift may manifest only on suspend/resume, idle, or low-power transitions.
- Perfmon/debug ambiguity: perfmon windows are repeated by block and instance. Using a valid perfmon offset for the wrong block can silently collect misleading diagnostics.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Build coverage for DCN 3.5, DCN 3.5.1, and DCN 3.6 resource paths that reuse these register-list patterns; missing or renamed macros should fail during compilation.
- Static comparison against the generated register database and neighboring ASIC headers such as `dcn_3_5_1_offset.h` and `dcn_3_6_0_offset.h` to catch unexpected offset shifts.
- Modeset and plane-update tests on DCN 3.5 hardware, including primary and overlay planes, tiled/DCC surfaces, chroma formats, page flips, and viewport changes.
- Cursor tests covering native cursor movement, size changes, hot-spot changes, cursor offload, and MALL-for-cursor behavior.
- Suspend/resume and display idle tests that exercise HUBP, HUBPREQ, HUBPRET, DSCL, CM, DCHUBBUB, and COMPBUF memory power control/status registers.
- Power-management tests around self-refresh, Z8, UCLK/FCLK p-state changes, and watermark lowering/raising.
- Color-management tests for pre-CSC, post/output CSC, gamut remap, 3D LUT, degamma/regamma/gamma correction RAM programming, HDR multiplier, and alpha/dealpha paths.
- Scaler tests for luma/chroma ratios, filter coefficient RAM programming, overscan, recout, line-buffer format, and autocal/update behavior.
- Diagnostic tests for DPP CRCs, HUBP/DPP/DC perfmon counters, DCHUBBUB timeout detection/status, and test-debug index/data access.

## Summary

This chunk is a generated DCN 3.5.0 register-address map for the display memory hub, first four hub pipes, first two complete DPP pipes, and the beginning of DPP2. Its practical value is providing stable `reg...` and `_BASE_IDX` names that DCN 3.5 resource, HUBBUB, HUBP, DPP, DMUB, and IRQ code use to construct MMIO register tables. The main engineering risks are stale generated data, offset/mask generation mismatch, wrong instance selection, and subtle hardware failures in watermarks, flips, cursor, VM, scaler, color, and low-power paths.
