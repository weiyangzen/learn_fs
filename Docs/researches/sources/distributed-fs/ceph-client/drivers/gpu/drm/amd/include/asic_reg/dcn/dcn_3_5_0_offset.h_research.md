# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002050`: lines 1-2738, `Docs/researches/chunks/subset-b-002050_research.md`
- `subset-b-002051`: lines 2739-5274, `Docs/researches/chunks/subset-b-002051_research.md`
- `subset-b-002052`: lines 5275-7886, `Docs/researches/chunks/subset-b-002052_research.md`
- `subset-b-002053`: lines 7887-10409, `Docs/researches/chunks/subset-b-002053_research.md`
- `subset-b-002054`: lines 10410-13005, `Docs/researches/chunks/subset-b-002054_research.md`
- `subset-b-002055`: lines 13006-15279, `Docs/researches/chunks/subset-b-002055_research.md`

## Chunk Research

### subset-b-002050: lines 1-2738

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h lines 1-2738

## Scope

This chunk covers the opening 2,738 lines of the generated AMD DCN 3.5 register-offset header. The source is not executable C logic; it is a compile-time register map made of preprocessor constants under the MIT license guard `_dcn_3_5_0_OFFSET_HEADER`.

The chunk contains 2,327 `#define` entries: 1,312 direct MMIO-style `reg...` constants, 1,014 indirect/indexed `ix...` constants, and 656 matching `reg..._BASE_IDX` entries. The covered blocks span:

- HDA/Azalia controller registers and indirect codec maps for output streams, output endpoints, input endpoints, sink info, audio descriptors, CRC results, and F2 codec verb/register indexes.
- DCCG display clock generator offsets for PHY pixel-clock resync, DP/HDMI stream clocks, DTO phase/modulo controls, DSC clocks, DTB clocks, GTC, timing base divisors, clock gating, and performance monitor hooks.
- DMU/DC power-gating, DMU misc, interrupt hub, RBBM interface, DMCUB memory window, mailbox, interrupt, scratch, timer, GPINT, fault, and security/control registers.
- MMHUBBUB/MCIF writeback and hubbub warmup, watermark, memory power, soft reset, VMID, and perf-monitor registers.
- HDA display-side index/data windows for Azalia streams/endpoints/root/controller registers.
- DCHUBBUB SDPIF VM/security/no-allocate/memory-power offsets and the beginning of return-path memory-power, CRC, and DCC-stat offsets.

## Purpose

The header provides the address-offset half of the DCN 3.5 ASIC register contract. Consumers pair these `reg...`/`ix...` offsets with field definitions from `dcn_3_5_0_sh_mask.h` so register helper macros can issue reads, writes, field updates, and indexed accesses without embedding raw addresses throughout the driver.

The `reg...` macros identify registers visible through AMDGPU/DC display MMIO register access. Each has a `reg..._BASE_IDX` companion that selects the register-base segment used by helper code, for example base index `3` for the HDA controller absolute block, base index `1` for many DCCG display-clock registers, and base index `2` for DMU, DMCUB, MMHUBBUB, HDA display-side, and DCHUBBUB display decoder ranges. The `ix...` macros identify indirect register indexes that are accessed through index/data registers rather than direct MMIO offsets.

## Important APIs, Types, and Constants

There are no C functions, structs, enums, or inline APIs in this chunk. Its API surface is the macro namespace itself.

Important macro forms:

- `regNAME`: a register offset used by `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_UPDATE`, `REG_SET`, and generated register tables.
- `regNAME_BASE_IDX`: the register-base segment selector used with `ctx->dcn_reg_offsets[...]` in DCN 3.5 register initialization.
- `ixNAME`: an indirect register index for indexed Azalia/HDA endpoint, stream, codec, descriptor, sink-info, and CRC spaces.

Representative constants and families:

- HDA controller direct registers: `regGLOBAL_CAPABILITIES`, `regGLOBAL_CONTROL`, `regINTERRUPT_CONTROL`, `regCORB_*`, `regAZCONTROLLER0_RIRB_*`, `regAZCONTROLLER0_IMMEDIATE_*`, `regAZCONTROLLER0_DMA_POSITION_*`, and `regAZCONTROLLER0_WALL_CLOCK_COUNTER_ALIAS`.
- Indirect Azalia stream registers: `ixAZF0STREAM0_AZALIA_FIFO_SIZE_CONTROL` through `ixAZF0STREAM15_AZALIA_CUMULATIVE_REQUEST_COUNT`.
- Indirect output endpoint registers: `ixAZF0ENDPOINT0_...` through `ixAZF0ENDPOINT7_...`, covering converter format, stream ID, digital converter control, GTC embedding, pin sense, widget control, speaker/channel allocation, audio descriptors, sink info, hot-plug control, LPIB snapshot, coding type, format-changed, remote keepalive, audio enable/status, and endpoint fine-grain clock-gating report disable.
- Indirect input endpoint registers: `ixAZF0INPUTENDPOINT0_...` through `ixAZF0INPUTENDPOINT7_...`, covering input converter controls, pin controls, channel allocation, hot-plug, LPIB, input status, and infoframe registers.
- F2 codec index maps: `ixAZALIA_F2_CODEC_ROOT_*`, `ixAZALIA_F2_CODEC_CONVERTER_*`, `ixAZALIA_F2_CODEC_PIN_*`, and `ixAZALIA_F2_CODEC_INPUT_*`.
- DCCG clock/timing offsets: `regPHYPLL[A-E]_PIXCLK_RESYNC_CNTL`, `regDPSTREAMCLK_CNTL`, `regDPREFCLK_CNTL`, `regDCCG_GTC_*`, `regDTBCLK_*`, `regDSCCLK[0-3]_DTO_PARAM`, `regOTG*_PIXEL_RATE_CNTL`, `regDP_DTO*_PHASE`, `regDP_DTO*_MODULO`, `regHDMICHARCLK0_CLOCK_CNTL`, and `regHDMISTREAMCLK*_DTO_PARAM`.
- DMU/DMCUB offsets: `regDOMAIN*_PG_CONFIG/STATUS`, `regDCPG_INTERRUPT_*`, `regDC_GPU_TIMER_*`, `regDISP_INTERRUPT_STATUS_CONTINUE*`, `regDMCUB_REGION*_OFFSET`, `regDMCUB_REGION3_CW*_BASE_ADDRESS/TOP_ADDRESS/OFFSET`, `regDMCUB_INBOX*`, `regDMCUB_OUTBOX*`, `regDMCUB_SCRATCH*`, `regDMCUB_GPINT_*`, `regDMCUB_INTERRUPT_*`, `regDMCUB_SEC_CNTL`, `regDMCUB_MEM_CNTL`, and fault-address registers.
- Writeback and hubbub offsets: `regMCIF_WB_*`, `regMMHUBBUB_*`, `regWBIF0_*`, `regDC_PERFMON4_*`.
- DCHUBBUB offsets: `regDCHUBBUB_SDPIF_*`, `regDCN_VM_*`, `regSDPIF_REQUEST_RATE_LIMIT`, `regDCHUBBUB_RET_PATH_MEM_PWR_*`, `regDCHUBBUB_CRC*`, and `regDCHUBBUB_DCC_STAT*`.

## Control Flow

This chunk has no runtime control flow. Its constants are consumed by generated or macro-expanded driver code that builds register tables and then drives hardware state machines.

The visible integration flow is:

1. DCN 3.5 display code includes `dcn/dcn_3_5_0_offset.h` and `dcn/dcn_3_5_0_sh_mask.h`.
2. `dmub_srv_dcn35_regs_init()` expands `DMUB_DCN35_REGS()` from `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.h`.
3. For each register name, `REG_OFFSET_EXP(reg)` computes `BASE(regNAME_BASE_IDX) + regNAME`, where `BASE` resolves through `ctx->dcn_reg_offsets[...]`.
4. Field masks and shifts come from the companion sh/mask header.
5. Runtime code uses the initialized offsets to reset/release DMCUB, configure DMCUB memory windows, set inbox/outbox ring buffers, service GPINT/interrupts, read scratch/fault/timer registers, and translate framebuffer-relative addresses.

For the Azalia portions, direct HDA index/data registers and indirect `ix...` maps imply a two-step flow: select an endpoint/stream/root/controller index through a direct index register, then read or write the associated data register. The header only supplies offsets and indexes; hardware and register helper code implement ordering, polling, and side effects.

## State and Persistence Behavior

The macros are stateless and do not persist data by themselves. Persistence exists in the hardware registers they identify.

State categories exposed in this chunk include:

- Audio/HDA state: CORB/RIRB base addresses, pointers, control/status, immediate command/response interfaces, DMA position buffers, stream FIFO/latency counters, codec pin sense, hot-plug, audio descriptors, sink info, channel allocation, LPIB snapshots, format-change state, and audio enable/disable/format interrupt status.
- Clock/timing state: DCCG clock-gating controls, DTO phase/modulo/increment values, PHY pixel-rate and stream-clock controls, DSC clock DTO parameters, millisecond/microsecond divisors, GTC counters, and vsync interrupt controls.
- Power and reset state: DMU power-gating domain config/status, memory power request/status controls, clock-gating override registers, DMCUB reset/security/memory controls, MMHUBBUB and DCHUBBUB memory power controls, and soft reset registers.
- Firmware communication state: DMCUB inbox/outbox ring-buffer bases, sizes, read/write pointers, GPINT data in/out, interrupt enable/ack/status/type registers, scratch registers, timers, and fault-address registers.
- Memory-window and VM state: DMCUB region offsets/top/base addresses, DCN framebuffer base/top/offset, AGP/HBM address bounds, VMID controls, warmup base/region registers, and SDPIF pipe security/no-allocate levels.
- Diagnostics and validation state: performance counters, DCHUBBUB CRC values, DCC stats, MCIF writeback buffer status/error indications, DMCUB fault addresses, and interrupt status continuations.

Because many registers are control/status pairs or ring-buffer pointers, consumers must preserve the hardware-prescribed sequencing. For example, DMCUB code resets pointers before boot, writes window offsets before enabling top-address windows, clears/acks GPINT interrupts explicitly, and reads scratch registers for firmware status. The header does not encode those sequencing rules.

## Dependencies and Integration Points

Direct compile-time dependencies are minimal: this header is a standalone preprocessor map guarded by `_dcn_3_5_0_OFFSET_HEADER`. Its practical dependency is the companion `dcn_3_5_0_sh_mask.h`, which supplies field masks/shifts for the same register names.

Observed integration points in this source tree:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c` includes this header and initializes DCN 3.5 DMUB register offsets with `REG_OFFSET_EXP`.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.h` enumerates many DMCUB, MMHUBBUB, DCN VM, and DMU registers from this chunk in `DMUB_DCN35_REGS()` and pairs them with field entries in `DMUB_DCN35_FIELDS()`.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c` reuses the DCN 3.5 register list patterns for the DCN 3.5.1 path.
- AMD display register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_UPDATE`, and `REG_SET` depend on the initialized offsets and the companion field metadata.
- HDA/Azalia endpoint constants are integration points for audio-over-display handling and indexed codec access through the display/HDA register windows.

## Risks and Edge Cases

- Generated-header drift is high impact. A wrong offset or `BASE_IDX` can make otherwise correct driver logic read or write an unrelated register.
- Duplicate physical offsets are intentional in places, such as minor/major/global capability aliases and immediate command data/index aliases. Tools that assume one macro per address can report false conflicts.
- `ix...` values are indirect indexes, not MMIO addresses. Treating them as `reg...` offsets would target the wrong access path.
- DMCUB mailbox and memory-window offsets are boot-critical. Misaddressing `DMCUB_REGION3_CW*`, inbox/outbox pointers, `DMCUB_SEC_CNTL`, or reset controls can prevent firmware boot, hang display management, or corrupt command queues.
- Audio endpoint blocks are highly repetitive across 16 streams and 8 endpoints. Copy/paste or generation mistakes can silently affect only one stream/endpoint instance.
- Register names imply several write-one-to-clear, self-clearing, pointer, status, and interrupt-ack interactions, but the offset header cannot express access semantics. Callers must rely on field definitions and hardware programming guides.
- This chunk ends in the middle of the DCHUBBUB return-path block at `regDCHUBBUB_DCC_STAT1`; later chunks must complete the same source file before whole-file conclusions are drawn.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-oriented:

- Compile coverage for DCN 3.5/3.5.1 display and DMUB code verifies that every register referenced by `DMUB_DCN35_REGS()` has a matching `reg...` and `reg..._BASE_IDX` definition and every field has a companion sh/mask entry.
- Booting a DCN 3.5 ASIC with DMUB enabled exercises `DMCUB_CNTL`, `DMCUB_CNTL2`, `DMCUB_SEC_CNTL`, region window, inbox/outbox, scratch, GPINT, and interrupt offsets.
- Display bring-up with DP/HDMI audio exercises Azalia controller, stream, endpoint, root, descriptor, sink-info, hot-plug, and LPIB offsets.
- Clock-change and link-training scenarios exercise DCCG DTO, PHY pixel-rate, stream-clock, DTB, GTC, and clock-gating offsets.
- Writeback/capture paths exercise `MCIF_WB_*`, MMHUBBUB watermark/memory-power, and related perf/status registers.
- GPU/display VM and warmup paths exercise `DCN_VM_*`, AGP/HBM bounds, SDPIF pipe security/no-allocate settings, and MMHUBBUB warmup registers.
- Interrupt tests should observe `DISP_INTERRUPT_STATUS_CONTINUE*`, `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, DMCUB interrupt ack/enable/status, and Azalia interrupt status/control behavior.

### subset-b-002051: lines 2739-5274

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

### subset-b-002052: lines 5275-7886

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h lines 5275-7886

## Purpose

This chunk is generated DCN 3.5 display register offset data for the AMDGPU display stack. It defines `reg...` address offsets and matching `reg..._BASE_IDX` selectors used to build absolute MMIO addresses as `ctx->dcn_reg_offsets[BASE_IDX] + reg...`. The range is not executable code; it is a hardware-address contract consumed by DC resource construction, IRQ setup, GPIO/DDC/HPD translation, AUX engines, DMUB register lookup, and low-level display block programming.

The requested line range begins in the middle of `dce_dc_dpp2_dispdec_cnvc_cfg_dispdec` and ends in the middle of `dce_dc_dio_dp_aux4_dispdec`. Inside the complete requested range, the major covered blocks are DPP pipe 2/3 color, cursor, scaler, and perfmon registers; OPP/FMT/DPG/OPPBUF/CRC/DSCRM blocks for output pipes 0-3; OPTC/ODM/OTG timing-generator blocks 0-3; DIO I2C, misc link, HPD, perfmon, and DP AUX blocks 0-4.

## Important Macros and Register Groups

- DPP2/DPP3 conversion and color path: `regCNVC_CFG2_*` partial at the start, `regCNVC_CUR2_*`, `regDSCL2_*`, `regCM2_*`, `regDPP_TOP3_*`, `regCNVC_CFG3_*`, `regCNVC_CUR3_*`, `regDSCL3_*`, and `regCM3_*`. These provide offsets for pixel format, alpha/keying, pre-CSC, cursor color/control, scaler coefficient RAM and ratios, line-buffer controls, memory power controls, color matrices, gamut remap, 3D LUT, degamma/regamma, gamma correction, bias/scale, and debug index/data registers.
- DPP perfmon: `regDC_PERFMON13_*` for DPP2 and `regDC_PERFMON14_*` for DPP3. Each block has counter control/state, monitor control, current-value, high, and low counter registers.
- OPP pipe instances 0-3: `regFMT{0..3}_*`, `regDPG{0..3}_*`, `regOPPBUF{0..3}_*`, `regOPP_PIPE{0..3}_OPP_PIPE_CONTROL`, and `regOPP_PIPE_CRC{0..3}_*`. These cover output formatter clamp/dynamic-expansion/bit-depth/pixel-encoding/422 controls, DisplayPort generator controls, OPP buffering, pipe enable/control, and CRC capture/result registers.
- Shared OPP and DSC-remap support: `regOPP_TOP_CLK_CONTROL`, `regOPP_ABM_CONTROL`, `regDSCRM{0..3}_DSCRM_DSC_FORWARD_CONFIG`, and `regDC_PERFMON16_*`.
- ODM and OTG timing-generator instances 0-3: `regODM{0..3}_OPTC_INPUT_*` and large `regOTG{0..3}_*` groups. The OTG groups define timing totals and blank/sync windows, dynamic refresh rate min/max/control registers, vertical interrupt positions, trigger controls, CRC windows/results, GSL synchronization, stereo/3D controls, clock controls, status/readback, DSC start, and spare/debug registers.
- OPTC misc and perfmon: `regGSL_SOURCE_SELECT`, `regODM_MEM_PWR_CTRL`, `regOPTC_CLOCK_CONTROL`, `regOPTC_INPUT_CLOCK_CONTROL`, `regOPTC_DATA_SOURCE_SELECT`, `regOPTC_SEG{0,1}_SRC_SEL`, `regOPTC_DATA_FORMAT_CONTROL`, `regOPTC_MISC_SPARE_REGISTER`, and `regDC_PERFMON17_*`.
- DIO DDC/I2C: `regDC_I2C_*` defines software/hardware I2C control, arbitration, data, setup/speed, transaction, status, mask, DDC EDID timing, pin select, and interrupt registers.
- DIO link/misc and HPD: `regDIO_DCN_STATUS`, `regDIO_MEM_PWR_CTRL`, `regDIO_LINK*_CNTL`, and `regHPD{0..4}_DC_HPD_*` define display link status/control and hotplug detect status, interrupt control, control, fast training, and toggle filter offsets.
- DIO perfmon and AUX: `regDC_PERFMON18_*` plus `regDP_AUX{0..4}_AUX_*`. AUX instances define AUX channel control, software control/status/data, link-service status/data, DPHY TX/RX control/status, GTC sync control/status, and PHY wake control. `DP_AUX4` is partial in this chunk; its remaining offsets continue after line 7886.

Every defined register normally appears as a pair: the offset macro and a `_BASE_IDX` macro. In this chunk almost all `_BASE_IDX` values are `2`, tying these display blocks to DCN base segment 2; the explicit address-block comments also show per-instance local base spacing such as OPP `0x0/0x168/0x2d0/0x438`, OTG `0x0/0x200/0x400/0x600`, HPD `0x0/0x20/...`, and AUX `0x0/0x70/...`.

## Integration Points

The primary consumer pattern is the DCN register initializer macros in `display/dc/resource/dcn35` and `display/dc/resource/dcn351`. Their `SRI`, `SRII`, `SRI_ARR`, and related macros expand token-pasted names such as `regOTG2_OTG_V_TOTAL_BASE_IDX` and `regOTG2_OTG_V_TOTAL` into absolute offsets. `dcn351_resource_construct()` then creates HUBP, DPP, OPP, timing generator, AUX, I2C, DSC, ABM, and related resources using static register tables built from these macros.

IRQ setup also depends on these names. `display/dc/irq/dcn351/irq_service_dcn351.c` uses `SRI(reg_name, block, id)` to derive HPD, vblank, vline, page-flip, and other interrupt register addresses. For this chunk, the `HPD{0..4}` and `OTG{0..3}` offsets are the relevant pieces for connector hotplug and timing interrupt routing.

DMUB code uses the same offset/header convention. `display/dmub/src/dmub_dcn35.c` includes `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`, then expands register offsets with `REG_OFFSET_EXP(reg_name) = BASE(reg..._BASE_IDX) + reg...`. The generic `dmub_reg.h` helpers (`REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`) operate on the initialized offsets and field masks.

The offset header must stay synchronized with `dcn_3_5_0_sh_mask.h` and the register-list macros in resource headers. Offset macros define where a register lives; sh/mask macros define how fields inside that register are manipulated. A name mismatch between the two usually becomes a compile-time failure in token-pasted macros, while a wrong numeric offset can compile but program the wrong hardware register.

## Control Flow and State Behavior

This file has no runtime control flow, no functions, and no in-memory state of its own. Its state effect is indirect: at driver initialization, resource constructors fold these constants into per-block register tables. Later display operations mutate hardware state through those tables, including scaler programming, color matrices and LUTs, output formatting, timing generator setup, DRR updates, CRC capture, HPD interrupt ack/mask state, DDC transactions, AUX transactions, clock/power controls, and perf counters.

Persistence is hardware-resident only. Values written through the offsets persist in display hardware registers until reset, power gating, suspend/resume reinitialization, mode-set reprogramming, or another driver path overwrites them. The header itself contributes no saved state, serialization, or recovery logic.

## Dependencies

- AMDGPU DCN 3.5 base-offset discovery via `dc_context::dcn_reg_offsets`.
- `dcn_3_5_0_sh_mask.h` for field shifts and masks corresponding to the registers named here.
- DC resource macros and constructors in `display/dc/resource/dcn35` and `display/dc/resource/dcn351`.
- IRQ service macros in `display/dc/irq/dcn351`.
- DMUB register helper macros in `display/dmub/src/dmub_reg.h` and DCN 3.5 DMUB initialization in `dmub_dcn35.c`.
- Hardware-generation naming conventions: `reg<block><instance>_<register>` plus `reg..._BASE_IDX`.

## Risks

- Numeric offset drift is high impact. A wrong offset may silently program an unrelated display register, causing blank displays, bad color conversion, scaler artifacts, broken VRR/DRR timing, AUX/DDC failures, missed HPD events, CRC test failures, or power-management regressions.
- Instance spacing must remain exact. OPP, OTG, HPD, and AUX blocks are repeated with regular-looking but hardware-defined strides; copying an offset from the wrong instance can route programming to another pipe or connector.
- Partial chunks should not be interpreted as complete hardware blocks. `CNVC_CFG2` starts before line 5275 and `DP_AUX4` continues after line 7886.
- `_BASE_IDX` mismatches are especially dangerous on SoCs with runtime-populated base arrays. Most macros here use segment `2`; an incorrect segment could move accesses to a completely different IP aperture.
- Generated headers are brittle under manual edits. Token-pasted consumers require exact macro spelling, so renames or omissions can break builds. Incorrect but present macros can evade compile-time detection.

## Test Signals

- Compile coverage for DCN 3.5/3.5.1 resource, IRQ, GPIO, AUX, and DMUB objects is the first signal; token-pasted macro use catches missing or misspelled offsets.
- Boot and probe on DCN 3.5-class hardware should create all DPPs, OPPs, timing generators, AUX engines, and I2C engines without `failed to create ...` errors from resource construction.
- Display mode-set tests across all four timing generators should verify stable scanout, correct H/V timing, vblank/vline interrupts, DRR/VRR behavior, and no timing-generator register-access faults.
- Connector tests should cover HPD plug/unplug and HPD RX IRQ behavior on all exposed HPD instances.
- DDC/AUX tests should read EDID and perform DisplayPort AUX transactions across all physical links, including AUX instance 4 whose block crosses the chunk boundary.
- Visual validation should include color-management and scaler paths: cursor rendering, CSC/gamut/regamma/3D LUT behavior, scaling ratios/taps, output formatter depth/encoding, and CRC capture/readback.
- Perfmon/debug smoke tests can validate the `DC_PERFMON13/14/16/17/18` offsets by enabling counters and observing sane counter progression.

### subset-b-002053: lines 7887-10409

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h lines 7887-10409

## Purpose

This chunk is generated AMD DCN 3.5 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic display-controller register names to numeric MMIO offsets and companion base-index selectors. Consumers combine each `reg...` offset with its matching `reg..._BASE_IDX` to form the absolute register address for DCN 3.5 display hardware.

The requested range is a mid-file slice of `dcn_3_5_0_offset.h`. It starts inside the tail of the `DP_AUX4` AUX block, then covers display I/O stream-output register groups for `DIG0` through `DIG4`, `DP0` through `DP4`, `VPG0` through `VPG4`, `AFMT0` through `AFMT4`, and `DME0` through `DME4`. It then covers common DCIO/DIO, GPIO, AUX/DDC, clock/pad, DCIO chip, and UNIPHY register-offset ranges through `DCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED57`.

Although this tree is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locking primitives in this range. The interface is the generated macro namespace:

- `reg<block>_<register>`: a DCN 3.5 MMIO register offset.
- `reg<block>_<register>_BASE_IDX`: the base-address segment selector used by helper macros such as `BASE(reg..._BASE_IDX) + reg...`, `SR(...)`, `SRI(...)`, and DMUB register-offset builders.

The chunk contains 2,394 `#define` lines: 1,197 register-offset macros and 1,197 matching `_BASE_IDX` macros. Every `_BASE_IDX` value in this range is `2`, which is part of the address contract with the SOC/DCN base-address tables; the numeric offset alone is not enough to address hardware safely.

Major macro families in this slice:

- `DP_AUX4` tail: AUX software/low-speed status and data, AUX DPHY TX/RX controls and status, GTC sync control/status/error registers, and PHY wake control.
- `VPG0` through `VPG4`: generic packet access/data, generic-stream-packet frame/immediate update controls, generic status, memory power, ISRC access/data, and MPEG info registers used for stream secondary-data packet generation.
- `AFMT0` through `AFMT4`: audio/VBI packet control, audio info, IEC 60958 channel-status words, ramp controls, audio CRC, status/interrupt, audio source selection, infoframe control, and AFMT memory power.
- `DME0` through `DME4`: Display Micro Engine control and memory-control offsets.
- `DIG0` through `DIG4`: stream-encoder front-end/back-end enable/clock/control, output CRC, test and clock patterns, FIFO controls, HDMI metadata/audio/ACR/generic-packet/control/status registers, AFMT bridge control, TMDS controls/symbols, lane enable, version, and force-disable registers.
- `DP0` through `DP4`: DisplayPort stream and link controls including MSA colorimetry/timing/VBID fields, video `M/N`, DPHY/link framing, video interrupt control, training and lane status, PHY test/debug controls, secondary-data packet controls, MST and payload allocation, CRC, pixel format, and AUX-less ALPM controls.
- Common DIO/DCIO registers: link controls for links A through E, DIO clock control, DIO memory power control, DCIO debug/mux and test debug registers, clock/pad controls, soft reset, AUX/I2C status, AFE low-power controls, PHY power status, and intercept control.
- GPIO and pad-control registers: DC GPIO masks/data/enables for generic DC GPIO, sync, generation lock, swap lock, DDC, HPD, DP AUX, and related pad-pull/pad-power-good controls.
- UNIPHY families: legacy `UNIPHYA/B/C/D/E` test/debug/data/indirect-access names plus `DCIO_UNIPHY0` through partial `DCIO_UNIPHY4` macro-control reserved offsets. The requested range ends at `regDCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED57` and the matching base-index line is outside the chunk.

## Control Flow

This header has no runtime control flow. Runtime code supplies the sequencing:

1. DCN 3.5 resource, IRQ, DIO, GPIO, and DMUB code includes `dcn_3_5_0_offset.h` together with the matching shift/mask header.
2. Register-list macros paste instance IDs into names such as `regDIG3_HDMI_CONTROL`, `regDP2_DP_LINK_CNTL`, `regVPG1_VPG_GENERIC_PACKET_DATA`, or `regAFMT4_AFMT_AUDIO_PACKET_CONTROL`.
3. Helper macros add the base segment selected by `*_BASE_IDX` to the offset and store the result in per-block register tables.
4. Driver code later uses those tables with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, wait/poll helpers, or DMUB register structures to program links, packet generators, audio formatting, AUX/DDC, GPIO, panel/link power, and display debug paths.

The macros do not encode ordering requirements. Consumers must still sequence clock enablement, memory/power gating, stream enable/disable, link training, AUX arbitration, hotplug handling, audio packet setup, packet double-buffer updates, interrupt clear/ack behavior, and suspend/resume restoration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes MMIO-backed GPU state. The represented hardware state includes:

- AUX channel state for DisplayPort DPCD/EDID transactions, low-speed data movement, DPHY TX/RX status, GTC sync, wake control, and AUX status reporting.
- Stream encoder state for HDMI/TMDS and DP output: front-end/back-end enablement, lane enables, clocking, test patterns, output CRC capture, FIFO state, HDMI metadata and generic packets, audio clock regeneration, TMDS symbols, and force-disable/version registers.
- DP stream/link state for timing, colorimetry, VBID, video `M/N`, framing, link training, lane status, MST payload allocation, secondary-data packets, PHY debug, CRC, and AUX-less ALPM.
- Infoframe/audio packet state in `VPG*` and `AFMT*`, including generic packets, ISRC/MPEG metadata, audio-info fields, channel-status words, CRC/status, and memory-power state.
- DCIO and GPIO state for link routing, DIO clocking, DIO memory power, debug muxes, pad controls, DDC/AUX/HPD GPIO masks/data/enables, pull-up/power-good configuration, and UNIPHY macro-control reserved registers.

Persistence is hardware-defined. Configuration registers usually retain values until modeset, link reconfiguration, display-block power gating, suspend/resume, ASIC reset, or firmware/driver reprogramming. Status, interrupt, debug, counter, clear/ack, wake, and power-status registers may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. This offset header does not distinguish those behaviors; the companion shift/mask header and consuming driver code provide field-level semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h` for field shifts and masks.
- SOC/DCN base-address definitions consumed by `BASE(reg..._BASE_IDX)`.
- The stream encoder, link encoder, GPIO, IRQ, resource, and DMUB register-list macros that construct typed register tables from these generated names.

Direct include sites found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`

The primary integration pattern is token-pasting register construction. `dcn35_resource.h` defines register-list macros for `VPG`, `AFMT`, `DIG`, stream encoder, link encoder, DIO, and DC global register blocks; those macros expand through `SR`, `SRI`, `SR_ARR`, and `SRI_ARR` style helpers to pair offsets from this header with masks from the matching `dcn_3_5_0_sh_mask.h`. `dmub_dcn35.c` includes this header and uses `REG_OFFSET_EXP(reg_name)`, `DMUB_SR(reg)`, and related macros to populate DMUB-facing register offsets.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. These macros are untyped constants, so a wrong `reg...` value or `_BASE_IDX` can compile cleanly while programming the wrong MMIO register or segment.
- Repeated instance families are copy-sensitive. `DIG0`-`DIG4`, `DP0`-`DP4`, `VPG0`-`VPG4`, `AFMT0`-`AFMT4`, and `DME0`-`DME4` are structurally similar but not interchangeable; an instance-specific typo may only fail on one connector, one pipe, or a multi-display configuration.
- The chunk boundaries are artificial. The first line is only the `regDP_AUX4_AUX_SW_STATUS_BASE_IDX` tail of a block that starts before line 7887. The final line is `regDCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED57`; its `_BASE_IDX` pair and the following PWRSEQ block are outside this chunk.
- AUX/DDC, HPD, GPIO, pad, and wake registers are side-effect-sensitive. Incorrect status/interrupt/clear/wake handling can break hotplug, EDID reads, DPCD transactions, panel wake, low-power resume, or pad-power sequencing.
- Link-training and stream-packet registers interact with timing and link state outside this header. Bad DP/TMDS/HDMI/AFMT/VPG offsets can cause blank displays, audio loss, CRC mismatch, infoframe corruption, MST payload errors, or failures limited to specific link rates and lane counts.
- DCIO, DIO memory-power, clock, soft-reset, and UNIPHY macro-control offsets are high risk because writes may be ignored or harmful when the relevant display block is gated, reset, firmware-owned, or clock-disabled.
- Reserved `DCIO_UNIPHY*_*RESERVED*` names provide addresses without semantic field names. They are especially dependent on matching the generated database and companion mask definitions; ad hoc writes are risky unless guided by ASIC documentation or existing driver code.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.5 support enabled; missing or renamed macros should fail in resource, IRQ, DIO, GPIO, stream-encoder, link-encoder, and DMUB register-table construction.
- Mechanically verify that every non-`_BASE_IDX` macro in lines 7887-10409 has exactly one matching `_BASE_IDX` macro and that all base-index values remain `2`. The requested chunk intentionally ends before the `_BASE_IDX` for `regDCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED57`, so the full-file or adjacent-chunk reconciliation should validate that pair across the boundary.
- Diff this slice against AMD's authoritative DCN 3.5 register database and nearby generated headers where compatibility is expected.
- Exercise systems with enough active displays to use high-numbered instances: DP/HDMI link training on `DIG`/`DP` instances 0 through 4, hotplug, EDID/DDC, AUX DPCD reads/writes, MST, link-rate/lane-count changes, and suspend/resume.
- Validate stream packets and audio: HDMI and DP audio playback, audio clock regeneration, infoframes, metadata packets, generic packets, ISRC/MPEG metadata, CRC capture, and packet update timing.
- Test GPIO/DCIO paths for DDC/AUX/HPD pad routing, genlock/swaplock pins, pull-up controls, pad power-good reporting, DIO clock/memory-power transitions, and low-power wake.
- Watch kernel logs and display diagnostics for AUX timeouts, hotplug storms, link-training failures, audio dropouts, CRC mismatches, FIFO/underflow issues, MST payload failures, stuck interrupts, and resume failures.

## Cross-Chunk Notes

Previous chunks own the start of `DP_AUX4`, including `AUX_CONTROL`, `AUX_SW_CONTROL`, `AUX_ARB_CONTROL`, `AUX_INTERRUPT_CONTROL`, and the `regDP_AUX4_AUX_SW_STATUS` offset paired with this chunk's first `_BASE_IDX` line. Later chunks own the `_BASE_IDX` for `regDCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED57` and continue into the PWRSEQ register blocks. The final per-file research document should merge adjacent chunks before making complete claims about all AUX channels, all UNIPHY instances, or the complete `dcn_3_5_0_offset.h` hardware map.

### subset-b-002054: lines 10410-13005

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h lines 10410-13005

## Purpose

This chunk is a generated AMD DCN 3.5.0 register-offset header slice. It has no executable C logic; it exports preprocessor constants that name MMIO register offsets and the base-index selector used to resolve those offsets through `ctx->dcn_reg_offsets[]` in AMDGPU display code. The companion `dcn_3_5_0_sh_mask.h` supplies field shifts and masks for the same symbolic register names.

The requested range contains 2,376 `#define` lines, mostly one offset macro plus one `_BASE_IDX` macro per register. The slice begins at an artificial chunk boundary with the final `_BASE_IDX` for a prior DCIO UNIPHY register, then covers display panel power sequencing, DSC/DSCC instances, writeback, DCHVM, HPO DisplayPort stream/link encoder blocks, MPCC pipe-composition registers, MPCC output-gamma/remap registers, and the first MPC config registers. Of the `_BASE_IDX` values in this range, 773 point at base index `2` and 415 point at base index `3`, reflecting two DCN address spaces used by the generated register helpers.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or runtime APIs in this chunk. The exported interface is the generated register namespace:

- `reg<REGISTER_OR_BLOCKED_REGISTER>`: numeric register offset.
- `reg<REGISTER_OR_BLOCKED_REGISTER>_BASE_IDX`: index into the per-ASIC DCN base-address array.
- `ix...`: no `ix` indexed-register constants are introduced by this chunk; this range is all `reg...` macros after the carry-over DCIO line.

The major register families are:

- Boundary carry-over: `regDCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED57_BASE_IDX` is the last macro from the preceding DCIO/UNIPHY block and should be reconciled with the previous chunk before making whole-block conclusions.
- Panel power sequencing: `PWRSEQ0` and `PWRSEQ1` expose GPIO enables/control/masks, panel power-sequence control/state/delay/reference-divider registers, backlight PWM control/period/lock registers, and spare registers.
- DSC/DSCC compression: four DSC instances (`DSC_TOP0-3`, `DSCCIF0-3`, `DSCC0-3`) expose top-level control/debug, CIF config, DSCC config/status/interrupt status, PPS config registers `0-22`, memory power control, squared-error counters, max absolute error counters, rate-buffer fullness counters, rate-control fullness counters, and test/debug-bus rotation registers.
- DSC perfmon: `DC_PERFMON19-22` provide counter control, state, monitor control, current-value, high, and low registers for DSC-related performance monitoring.
- Writeback: `DWB` top registers cover clock enable, memory power, soft reset, overflow status/counter, CRC control/masks/values, output control, and host-read controls. `DWBCP` covers HDR multiplier, gamut remap A/B coefficient groups, MMHUBBUB backpressure controls, output gamma LUT access/control, two OGAM RAM banks, per-channel start/end/slope/base/offset programming, and RAM region descriptors.
- DCHVM: `DCHVM_CTRL0`, clock/memory controls, RIOMMU control, and RIOMMU status describe the display client HVM/RIOMMU register surface in this slice.
- HPO DisplayPort stream encoder instances `0-3`: each instance has stream encoder clock/control/status/spare registers, APG control/status/memory/payload/video/MPEG info registers, DME control/status/memory registers, VPG generic packet access/config/status/video/audio/MPEG info registers, and DP SYM32 encoder control/status/link-training/test/debug/CRC/spare registers.
- HPO DP link/DPHY: link encoder `0-1` clock/control/spare macros and DPHY SYM32 control/status/test/debug/CRC/count macros are present for PHY-side high-performance DP paths. Instances `2-3` in this chunk include stream/APG/DME/VPG/SYM32 macros but no matching link-encoder/DPHY blocks before the chunk moves into MPC.
- MPC/MPCC: `MPCC0-3` expose top/bottom mux selection, control/control2, status/idle/status-size, ALPHA/GLOBAL/GLOBAL_ALPHA values, and debug-index/data registers.
- MPCC OGAM and gamut remap: `MPCC_OGAM0-3` expose output gamma control, LUT index/data/control, two OGAM RAM banks (`RAMA`, `RAMB`) with B/G/R start, slope, base, end, offset, and region descriptors, plus gamut-remap coefficient format/mode and A/B coefficient matrix registers.
- MPC config start: `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, and `MPC_CRC_CTRL` start the global MPC config block; the rest of this address block continues in later chunks.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this generated metadata:

1. DCN35 initialization code includes `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Register-list macros token-paste names such as `regDSCC0_DSCC_CONFIG0`, `regDP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_CONTROL`, or `regMPCC0_MPCC_CONTROL` into offset-table initializers.
3. Helper macros add the selected base address: for example, DCN35 resource code uses `SR`, `SRI`, `SRI_ARR`, and related macros shaped as `BASE(reg..._BASE_IDX) + reg...`.
4. Hardware block constructors store the computed addresses in typed register tables for DSC, HPO DP stream encoders, HPO DP link encoders, writeback, MMHUBBUB/MCIF writeback, MPC/MPCC, DCCG, power control, and related DCN35 components.
5. Runtime paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, IRQ helpers, and block-specific programming functions. Those helpers use the computed offsets from this header and the field definitions from the shift/mask header.

The macros do not encode sequencing. Consumers still have to order panel power-up/down, backlight PWM changes, DSC setup/PPS programming, writeback enable/disable, HPO DP training and packet programming, MPCC mux/blend updates, OGAM LUT updates, gamut-remap updates, CRC collection, soft resets, and clock/power transitions correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on its own. It describes hardware state in DCN 3.5.0 registers:

- Panel and backlight state in PWRSEQ instances: GPIO routing, panel sequencing delays, state observation, reference dividers, PWM period/control, and register lock behavior.
- DSC compression state: top/control flags, CIF config, DSCC config/status, PPS programming, memory power, rate-buffer counters, error counters, and test/debug state for four DSC engines.
- Performance counter state for DSC and writeback perfmon blocks.
- Writeback state: DWB enable/clock/reset state, overflow counters, CRC collection, output control, host-read state, color/HDR/gamut-remap coefficients, OGAM LUT RAM contents, and MMHUBBUB backpressure controls.
- DCHVM/RIOMMU state: clock/memory controls and RIOMMU control/status bits relevant to display memory virtualization.
- HPO DP state: stream/link clocking, stream encoder status, APG/VPG packet state, DME memory/control state, SYM32 link-training/test/debug/CRC state, and DPHY control/status.
- MPC/MPCC state: pipe mux topology, composition controls, alpha/global-alpha values, idle/status signals, per-MPCC OGAM LUTs, and gamut-remap matrices.
- Global MPC state beginning with clock control, soft reset, and CRC control.

Persistence is hardware-defined. Configuration values generally remain until a modeset, plane update, link retrain, writeback reconfiguration, power-gate cycle, suspend/resume, driver reset, or ASIC reset. Status, perf counter, CRC, overflow, interrupt/status, and debug registers may be read-only, sticky, self-clearing, write-one-to-clear, or only valid while their block clocks and power domains are enabled. This offset header does not describe those access semantics.

## Dependencies And Integration Points

This generated header must stay synchronized with AMD's DCN 3.5.0 register database and with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h`, which defines the field shifts and masks for the same register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`, which includes both DCN35 generated headers and builds register tables with token-pasted offset macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, where `REG_OFFSET_EXP(reg_name)` resolves generated offsets through `BASE(reg..._BASE_IDX) + reg...` for DMUB-facing register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`, which uses the same generated offset/shift/mask model for DCN35 IRQ register tables, even though this particular chunk is mostly display block programming rather than the main HPD/vblank IRQ register set.
- Hardware object headers included by `dcn35_resource.c`: DSC register-list macros, `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST_RI`, `DCN3_1_HPO_DP_LINK_ENC_REG_LIST_RI`, `DWBC_COMMON_REG_LIST_DCN30_RI`, `MCIF_WB_COMMON_REG_LIST_DCN3_5_RI`, `MPC_REG_LIST_DCN3_2_RI`, and their shift/mask list counterparts.

The direct code integration visible in `dcn35_resource.c` maps this chunk into:

- `dsc_regs[4]`, `dsc_shift`, and `dsc_mask` for DSC engines.
- `hpo_dp_stream_enc_regs[4]`, `hpo_dp_se_shift`, and `hpo_dp_se_mask` for HPO DP stream encoders.
- `hpo_dp_link_enc_regs[2]`, `hpo_dp_le_shift`, and `hpo_dp_le_mask` for HPO DP link encoders.
- `dwbc35_regs[1]`, `dwbc35_shift`, and `dwbc35_mask` for display writeback.
- `mcif_wb35_regs[1]`, `mcif_wb35_shift`, and `mcif_wb35_mask` for MCIF/MMHUBBUB writeback integration.
- `mpc_regs`, `mpc_shift`, and `mpc_mask` for MPCC/MPC composition, mux, CRC, OGAM, and gamut-remap programming.

One notable local integration detail is that `dcn35_resource.c` defines `DSCC0_DSCC_CONFIG0__ICH_RESET_AT_END_OF_LINE__SHIFT` and `_MASK` immediately after including the generated DCN35 headers. That suggests the generated shift/mask header or shared DSC macro list needed a local compatibility patch for this DSC field, while the offset macro `regDSCC0_DSCC_CONFIG0` still comes from this offset header.

## Risks And Edge Cases

- The constants are untyped preprocessor values. A wrong offset or `_BASE_IDX` can compile cleanly and route a register access to the wrong block, wrong instance, or wrong address space.
- This is generated metadata. Manual edits can diverge from AMD's authoritative register database, firmware assumptions, and the matching shift/mask header.
- The chunk boundary is artificial. It starts with a dangling DCIO/UNIPHY `_BASE_IDX` from the previous block and ends after only the first three MPC config registers. Whole-block conclusions require adjacent chunks.
- Repeated instances are copy-sensitive. DSC0-3, HPO stream encoders 0-3, APG/VPG/DME instance IDs, SYM32 encoder IDs, MPCC0-3, and MPCC_OGAM0-3 use similar names but different offsets and base addresses.
- HPO DP instance coverage is asymmetric in this range: link encoder and DPHY SYM32 macros are present for the first two HPO DP link paths, while stream/SYM32 encoder macros continue for instances 2-3. Consumers must use the resource table's actual instance counts rather than infer all link-side blocks from stream-side blocks.
- DSC programming is field- and sequence-sensitive. Bad offsets can corrupt PPS programming, memory-power control, rate-buffer telemetry, or error-counter reads, causing DSC link failures, corruption, blanking, or misleading diagnostics.
- Writeback and DWBCP registers include CRC, overflow, backpressure, color, HDR, gamut, and OGAM programming. Misaddressing can produce bad captured frames, stalls, silent color conversion errors, or hard-to-debug overflow behavior.
- MPCC and MPC registers control display pipe composition. Wrong mux, alpha, OGAM, or gamut-remap offsets can swap pipes, break blending, produce color errors, or disturb atomic updates.
- Panel power/backlight PWRSEQ registers are user-visible and potentially timing-sensitive. Incorrect offsets may leave eDP panels dark, flicker during enable/disable, or mishandle backlight PWM register locking.
- Status/debug/perf registers may have side effects or validity constraints not represented here. Test/debug, CRC, perfmon, overflow, and status reads should be treated according to the programming guide and block power state.

## Test Signals

Useful validation combines generated-header consistency with DCN35 hardware behavior:

- Build AMDGPU with DCN35 display support enabled. Missing or renamed macros should fail in `dcn35_resource.c`, `dmub_dcn35.c`, IRQ service compilation, or hardware object register-list expansion.
- Mechanically compare this range against the matching `dcn_3_5_0_sh_mask.h` and AMD's generated register database, checking that every consumed offset macro has a matching base-index macro and that consumers do not request registers absent from this slice or adjacent chunks.
- Diff equivalent blocks against nearby generated variants such as `dcn_3_5_1_offset.h`, `dcn_3_6_0_offset.h`, and `dcn_4_2_0_offset.h` to catch accidental instance swaps or unexpected base-index changes.
- Exercise eDP panel power and backlight transitions on DCN35 hardware: cold boot, modeset, DPMS off/on, suspend/resume, brightness changes, and panel power sequencing.
- Validate DSC on supported links with multiple bpc/format/refresh modes, MST where applicable, hotplug/retrain cycles, suspend/resume, and error-counter/perfmon reads.
- Exercise HPO DP stream/link paths: high-bandwidth DP modes, link training, test-pattern generation, APG/VPG info packets, MPEG/audio/video packet updates, CRC/debug status reads, and link retraining after hotplug.
- Exercise writeback paths: enable/disable DWB, capture frames, stress MMHUBBUB backpressure, monitor overflow counters, validate CRC values, and verify HDR/gamut/OGAM effects in captured output.
- Exercise MPCC/MPC composition paths: multi-plane blending, alpha and global-alpha changes, plane reordering, pipe split/merge, color-management changes, OGAM LUT programming, gamut remap, and MPC CRC reads.
- Watch kernel logs and display diagnostics for register timeout messages, blank displays, missed page flips, link training failures, writeback overflows, DSC corruption, color mismatches, stuck soft resets, and resume-only failures.

## Cross-Chunk Notes

This is a middle chunk of `dcn_3_5_0_offset.h`. Earlier chunks contain the file prologue and many preceding DCN35 blocks; the first line here belongs to a preceding DCIO/UNIPHY block. Later chunks continue the MPC config block and the rest of the generated DCN35 register-offset namespace. The final per-file research document should merge adjacent chunks before making complete claims about all DCN35 register offsets, all HPO DP link paths, or the full MPC/MPC config register surface.

### subset-b-002055: lines 13006-15279

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h lines 13006-15279

## Purpose

This chunk is generated AMD DCN 3.5.0 register-offset metadata. It contains C preprocessor constants only: each visible hardware register has a `reg...` address macro and a paired `reg..._BASE_IDX` macro. There are no executable functions, structs, enums, branches, allocations, locks, or direct MMIO accesses in this range.

The range covers the late display-pipe output and stream-encoder portion of `dcn_3_5_0_offset.h`. It starts inside the MPC configuration block, continues through MPC output color-space conversion, display performance counters, HPO HDMI/DP stream/link encoder blocks, ABM instances, MPCC MCM color-management blocks, DLPC, DPIA microcontroller registers, HDA aliases, DIO DPIA muxes, and DIG stream mapper offsets, then ends at the header guard `#endif`. Although the path is under a local `ceph-client` source mirror, this is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

The requested range has 2,274 source lines and 2,150 `#define` lines: 1,075 register-offset definitions and 1,075 matching `BASE_IDX` definitions. It is boundary-partial at the beginning: line 13006 starts after the `dce_dc_mpc_mpc_cfg_dispdec` address-block comment and after the first MPC config registers, so the complete MPC config block must be reconciled with the previous chunk.

## Important APIs, Types, And Macros

The public interface is the generated macro namespace:

- `reg<REGISTER>`: numeric register offset used by AMDGPU display register helpers.
- `reg<REGISTER>_BASE_IDX`: base-index selector used with DC register-base tables.
- `// addressBlock:` and `// base address:` comments: generator metadata grouping registers by hardware block and block base.

Major register families in this chunk include:

- MPC configuration tail: CRC selection/result registers, perfmon event control, bypass background, host read, DPP/pending status, vertical-update lock sets 0-3, and `MPC_DWB0_MUX`.
- MPC output CSC/denorm: `MPC_OUT0` through `MPC_OUT3` mux, denormalization, clamp, CSC mode, and A/B coefficient registers.
- DC performance monitor: `DC_PERFMON15_*` and HPO perfmon counter/control/value registers.
- HPO HDMI stream support: AFMT5 audio packet/60958/CRC registers, VPG5 generic/secondary data packet registers, DME5 metadata packet registers, HDMI stream encoder clock/input/FIFO controls, HDMI transport/bypass encoder packet, ACR, CRC, encryption, mode, buffer, and metadata controls, plus HDMI link and FRL encoder control/status/memory registers.
- HPO top and DP stream mapping: top-level HPO clock and hardware control plus `DP_STREAM_MAPPER_CONTROL0..3`.
- ABM instances 0-3: backlight PWM levels and duty-cycle controls, ABM control, ACE offset/slope/threshold controls, histogram/luma statistics, sample rates, histogram result bins, and backlight master locks.
- MPCC MCM instances 0-3: shaper LUT controls, RAM A/B shaper regions, 3D LUT mode/index/data/read-write/out-normalization/out-offset registers, 1D LUT control/index/data/RAM A/B piecewise region programming, and memory power control.
- DLPC: enable, current count, OPTC snapshot, power-up, OTG resync, ZSC/LONO power-up, spare, and counter-init registers.
- DPIA MU: per-port clock/reset controls for ports 0-3, TPI status, credit count, interrupt control/status/ack, RBBMIF timeout/status, microsecond reference, port adapter status, glue control, and perf-count registers.
- HDA/Azalia aliases: controller CORB/RIRB, immediate command/response, DMA position, wall-clock alias, endpoint immediate command, and input-endpoint immediate command registers.
- DIO and stream mapping: DPIA mux controls for muxes 0-3 and `DIG0` through `DIG4_STREAM_MAPPER_CONTROL`.

The macro names are consumed through token-pasting register-table definitions rather than as traditional APIs. Callers usually write `REG(...)`, `SR(...)`, `SRII(...)`, `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, or related helper calls that expand into these generated offsets plus field definitions from `dcn_3_5_0_sh_mask.h`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU Display Core:

1. DCN 3.5 code includes `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Resource and block-construction macros paste symbolic register names into `reg...` offset constants and matching mask/shift constants.
3. Display block objects store the resolved offsets in register tables for MPC, ABM, HPO, DMUB, IRQ, and resource code.
4. Modeset, link-training, color-management, audio, backlight, power, interrupt, and diagnostics code use DC register helpers to read or write the underlying MMIO registers in hardware-defined order.

The offsets do not encode sequencing. Correct behavior still depends on external code ordering clocks, resets, stream encoder setup, packet programming, ABM locks, LUT bank selection, memory power transitions, DPIA routing, HDA command-ring setup, and status polling.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes MMIO-backed hardware state. The represented state includes:

- MPC output routing, denormalization/clamp/CSC programming, CRC results, pending-update state, and vupdate lock configuration.
- HPO HDMI/DP stream routing, audio/video info packets, ACR values, generic packets, metadata packets, encryption/mode state, FRL encoder state, FIFO/status values, and HPO clock/hardware enable state.
- ABM backlight/PWM configuration, target/current/final duty levels, adaptive brightness controls, histogram/luma statistics, and lock state.
- MPCC MCM color pipeline state for shaper LUTs, 3D LUTs, 1D LUTs, RAM A/RAM B bank selection and region data, output offsets, and LUT memory power control.
- DLPC counter/snapshot/resync/power state.
- DPIA microcontroller clock/reset, interrupt, timeout, TPI credit/status, perf counter, and mux/routing state.
- HDA/Azalia command/response ring aliases and immediate command/response state.

Persistence is hardware-defined. Configuration registers normally retain values until overwritten, reset, power-gated, or restored during resume. Status, counter, CRC, histogram, FIFO, interrupt, timeout, and command-ring registers can be volatile, sticky, self-clearing, read-only, write-one-to-clear, or firmware-owned depending on the block. This offset header does not state access type, reset value, side effects, or required polling delays.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h`, which supplies the matching field shifts and masks.
- Other DCN 3.5 generated headers and register-base tables used by AMDGPU Display Core.
- The DCN 3.5 hardware register database that defines block base addresses, instance layout, and per-register access semantics.

Direct include sites for the DCN 3.5 offset and mask headers in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn35/dcn35_resource.c`

Functional integration points include:

- DCN35 resource construction, including HPO DP stream/link encoder setup, ABM instance registration, audio/stream encoder resources, and comments noting DCN3.5 DPIA topology.
- DMUB DCN35 support, where generated offsets contribute to firmware-facing display register access.
- DCN35 IRQ service setup, which depends on generated register constants for interrupt-source register tables.
- MPC/MPCC color-management code inherited from DCN3.x paths, especially 1D LUT, shaper LUT, 3D LUT, memory-power, and RAM A/RAM B programming paths.
- Backlight and ABM code that programs PWM levels, ACE controls, histogram/luma collection, and lock registers.
- HPO HDMI/DP and DPIA routing code that controls stream mapping, FRL/link/transport encoders, packet generation, audio metadata, and DPIA muxing.

## Risks And Edge Cases

- Generated-offset drift is the main risk. A wrong offset or `BASE_IDX` compiles cleanly but sends a valid register-helper call to the wrong MMIO address.
- The chunk starts mid-address-block. Complete claims about `dce_dc_mpc_mpc_cfg_dispdec` require the previous chunk for `MPC_CLOCK_CONTROL`, soft reset, and CRC control context.
- Repeated instances are copy-sensitive. ABM0-3, MPCC_MCM0-3, DPIA ports 0-3, DIO DPIA muxes 0-3, and DIG stream mappers use structurally similar names; one instance index error can affect only a subset of pipes or connectors.
- `BASE_IDX` values vary by address domain. Most display-register entries here use base index 3, but DLPC/DIO/DIG entries use base index 2 and HDA alias entries use base index 0 or 1. A base-index mismatch can target a wrong register aperture even if the register offset looks plausible.
- LUT programming is banked and stateful. MPCC MCM shaper/1D LUT RAM A/RAM B registers require correct host selection, index setup, write masks, and mode updates; stale bank selection can produce valid-looking but wrong color output.
- ABM and histogram registers mix configuration, locks, live statistics, and PWM output state. Updating them without respecting lock/update sequencing can cause visible brightness jumps or stale histogram feedback.
- HDMI/HPO packet, ACR, CRC, FIFO, encryption, FRL, and metadata registers are timing-sensitive. Programming them while a stream is active or clocks are gated can cause audio/video packet errors, black screens, or link retraining.
- DPIA MU and DIO mux registers are routing and interrupt sensitive. Incorrect clock/reset or mux programming can break USB-C/DP Alt Mode paths or produce hard-to-diagnose hotplug/link failures.
- HDA aliases use overlapping offsets for different CORB/RIRB/immediate-command views. Consumers need the field-level mask header and HDA access semantics to avoid treating aliases as independent storage.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU Display Core with DCN35 enabled; malformed, missing, or renamed macros should fail in `dmub_dcn35.c`, `irq_service_dcn35.c`, `dcn35_resource.c`, and register-table users.
- Mechanically compare this range against AMD's authoritative DCN 3.5.0 register database or a regenerated `dcn_3_5_0_offset.h`; every visible `reg...` should have exactly one matching `reg..._BASE_IDX`.
- Cross-check every register family against `dcn_3_5_0_sh_mask.h` so offset names and field-mask names remain aligned.
- Exercise DCN35 display modes across HDMI FRL, HPO DP, and DPIA/USB-C paths: hotplug, modeset, link-rate changes, blank/unblank, suspend/resume, and runtime power transitions.
- Validate HDMI/HPO audio and packet behavior with audio playback, infoframe/metadata changes, HDR or variable metadata paths, CRC/status reads, and high-bandwidth FRL modes.
- Validate ABM/backlight behavior by changing brightness, enabling/disabling adaptive brightness, checking PWM duty-cycle registers, and watching histogram/luma statistics update without jumps or stalls.
- Validate color-management paths by loading 1D LUT, shaper LUT, and 3D LUT state on all MPCC instances, switching RAM banks, and checking output visually or through CRC/reference captures.
- Monitor kernel logs and debug dumps for HPO FIFO underflow, FRL/link encoder faults, DPIA MU interrupts/timeouts, HDA command-ring failures, ABM lock/update stalls, MPCC MCM memory-power timeout, and unexpected stream mapper routing.

## Cross-Chunk Notes

The previous chunk owns the beginning of the MPC configuration address block and the immediately preceding MPCC OGAM/gamut remap offsets. This chunk owns the remainder of the file through `#endif`, including all visible MPCC MCM instance blocks and late HPO/DPIA/HDA/DIO stream mapping offsets. The final per-file report should merge this document with adjacent chunks before making complete claims about the full `dcn_3_5_0_offset.h` register map.
