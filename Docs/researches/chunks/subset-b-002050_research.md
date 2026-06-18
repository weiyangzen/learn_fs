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
