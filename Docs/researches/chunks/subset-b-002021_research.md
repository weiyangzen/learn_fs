# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h lines 1-2627

## Purpose

This chunk is the beginning of the generated AMDGPU DCN 3.2.1 register offset header. It contains no executable C logic; it publishes preprocessor constants that map symbolic display-core register names to register offsets and DCN base-index selectors.

Each hardware register is represented as paired macros:

- `reg<REGISTER_NAME>` gives the register's offset within the relevant DCN address segment.
- `reg<REGISTER_NAME>_BASE_IDX` gives the segment index used by DCN register-list construction macros to add the runtime base from `ctx->dcn_reg_offsets[]`.

The chunk covers the file prologue, include guard, copyright/license block, and the first 2,364 `#define` entries. Functionally, the covered register map spans display clock generation, DMU/DMCUB, display interrupts, display power gating, writeback, MMHUBBUB, HDA/Azalia display audio, DCHUBBUB memory and VM request registers, HUBP0, HUBP1, and the start of the `CURSOR0_1` block.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or data objects in this header. The API surface is the generated macro namespace consumed by DCN 3.2.1 resource construction code.

Major macro groups in this range are:

- Include guard: `_dcn_3_2_1_OFFSET_HEADER`.
- DCCG/display clock registers: `regDENTIST_DISPCLK_CNTL`, PHY PLL pixel-clock resync controls, `regDP_DTO*_PHASE`, `regDP_DTO*_MODULO`, `regOTG*_PIXEL_RATE_CNTL`, `regOTG*_PHYPLL_PIXEL_RATE_CNTL`, `regDPPCLK*_DTO_PARAM`, `regDSCCLK*_DTO_PARAM`, `regDCCG_*`, `regDPREFCLK_*`, `regSYMCLK*`, `regDCCG_AUDIO_DTO*`, and VSYNC latch/count registers.
- DMU/RBBMIF/IHC/misc/power-gating registers: `regRBBMIF_*`, `regDC_GPU_TIMER_*`, `regDISP_INTERRUPT_STATUS*`, interrupt destination registers for DCCG, DMU, DCHUB, DPP, MPC, OPP, OPTC, OTG, DIG, HPD, AUX, DSC, HPO, and power-domain controls such as `regDOMAIN*_PG_CONFIG`, `regDOMAIN*_PG_STATUS`, and `regDCPG_INTERRUPT_*`.
- DMCUB registers: region offset/top/base-address windows, `regDMCUB_INTERRUPT_*`, fault-address registers, inbox/outbox base/size/read/write pointers, timers, scratch registers, GPINT data registers, memory/security controls, and processor/control registers.
- Display writeback and writeback color pipeline registers: `regDWB_*`, frame-composition controls, CRC controls, gamut remap coefficients, output gamma LUT/index/data/control, RAM A/B piecewise gamma regions, denormal/clamp controls, and format controls.
- MMHUBBUB/writeback memory path registers: MCIF writeback buffer addresses, pitches, sizes, arbiter/QoS controls, watermark and p-state latency registers, warmup controls, VMID controls, MMHUBBUB memory power and clock/reset controls, and debug/error status registers.
- HDA/Azalia audio registers: controller clock/audio DTO/DMA controls, payload/CRC controls, root codec parameters, power/reset/synchronization fields, stream index/data pairs for streams 0-15, endpoint index/data pairs for output endpoints 0-7, and input endpoint index/data pairs 0-7.
- DCHUBBUB registers: display fabric request/outstanding controls, arbitration and QoS watermarks, urgent/pstate/SR/USR retraining watermarks, return-buffer and compbuf sizing, debug/read-state controls, memory power controls/status, SDP interface controls, return-path controls, and VM request interface registers.
- DCN VM context registers: `regDCN_VM_CONTEXT0_*` through `regDCN_VM_CONTEXT15_*`, default address registers, fault control/status, and fault-address registers.
- HUBP/HUBPREQ/HUBPRET/cursor registers for instance 0 and part of instance 1: surface config, address config, tiling, primary/secondary viewport registers, request sizing, MALL config/status, surface address and meta-surface address registers for luma/chroma, flip controls, surface-in-use tracking, TTU/QoS/prefetch/vblank/nominal/flip timing parameters, UCLK p-state force, status registers, return-path controls, cursor surface/position/hotspot/stereo/memory-power controls, and DM data controls.

The repeated `*_BASE_IDX` macros are as important as the offsets. Consumers construct real MMIO addresses with patterns like `BASE(regFOO_BASE_IDX) + regFOO`; a correct offset with the wrong base index points at the wrong segment.

## Control Flow

This header has no runtime control flow. The only processing is C preprocessor substitution.

Runtime flow appears in consumers such as `display/dc/resource/dcn321/dcn321_resource.c`, which includes this file and the matching `dcn_3_2_1_sh_mask.h`. That source defines register-list construction helpers such as `SR`, `SRI`, `SRI_ARR`, and related variants. Those helpers expand offsets from this header into register tables for hardware blocks:

1. A resource constructor selects a DCN 3.2.1 hardware object, such as DCCG, hubbub, HUBP, DWBC, MMHUBBUB, audio, stream encoder, or DIO.
2. Register-list macros expand symbolic register names into addresses by adding `ctx->dcn_reg_offsets[reg*_BASE_IDX]` to the `reg*` offset.
3. The object constructor receives the populated register table plus field shift/mask tables from `dcn_3_2_1_sh_mask.h`.
4. Later hardware operations use `reg_helper.h` accessors and block-specific methods to read, write, poll, or update these hardware registers.

The chunk's line boundary is not a hardware boundary. Line 2627 stops after `regCURSOR0_1_DMDATA_ADDRESS_LOW_BASE_IDX`; later lines continue the `CURSOR0_1` block and the rest of the DCN register map.

## State And Persistence Behavior

The header stores no software state and has no persistence mechanism. It describes hardware state held in DCN 3.2.1 display registers.

The hardware state represented by this chunk includes display clock programming, DTO phase/modulo state, clock gating controls, interrupt status and routing, GPU display timer state, display power-domain state, DMCUB firmware memory windows and mailbox pointers, DMCUB scratch/interrupt/fault state, writeback pipeline configuration, MCIF writeback buffers and QoS watermarks, display audio DMA/codec/stream state, DCHUBBUB arbitration and VM context state, HUBP surface addresses and flip/prefetch timing, cursor state, and memory-power controls/status for several display blocks.

Persistence is hardware- and reset-domain-specific. Some registers are volatile status snapshots, some are sticky interrupt/fault/status registers, and many are control registers programmed during display resource bring-up, mode set, flip, audio setup, DMCUB boot, suspend/resume, power-gating transitions, or GPU reset recovery. The offset header does not encode read/write permissions, reset values, write-one-to-clear behavior, locking requirements, or safe sequencing; those semantics live in hardware specs and the block drivers that consume these constants.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register naming contract for DCN 3.2.1. Its direct companion is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`

The direct include point found in this tree is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`

That resource file uses this offset header to build register tables for DCN 3.2.1 display objects. Examples visible in the source include `hubbub_reg_init()`, `vmid_regs_init()`, `hubp_regs_init()`, `dwbc_regs_dcn3_init()`, and `mcif_wb_regs_dcn3_init()`, which feed constructors such as `hubbub32_construct()`, `hubp32_construct()`, `dcn30_dwbc_construct()`, and `dcn32_mmhubbub_construct()`.

The register tables integrate with the broader AMD display stack through `reg_helper.h`, DC resource-pool creation, DMCUB firmware loading, display clock management, DCHUBBUB/HUBP programming, writeback, audio, interrupt handling, power management, and mode-set/flip paths. Although the repository path sits under a `ceph-client` source mirror, this file is AMDGPU Linux kernel display-driver hardware metadata and has no Ceph filesystem or distributed-storage behavior.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. A wrong register offset or `_BASE_IDX` can compile successfully while causing a consumer to read or write the wrong display register. Because this file is generated and highly repetitive, errors can be hard to detect in review.

High-risk areas in this chunk include:

- Clock and DTO registers such as `regDENTIST_DISPCLK_CNTL`, `regDISPCLK_FREQ_CHANGE_CNTL`, `regDP_DTO*_PHASE`, `regDP_DTO*_MODULO`, `regDPPCLK*_DTO_PARAM`, and `regDSCCLK*_DTO_PARAM`; bad offsets can break display clocks, link clocks, DSC clocks, audio clocks, or timing stability.
- Interrupt and timer registers such as `regDISP_INTERRUPT_STATUS*`, `reg*_INTERRUPT_DEST`, and `regDC_GPU_TIMER_*`; bad mappings can lose or misroute vblank, flip, HPD, AUX, DSC, DMCUB, or other display interrupts.
- DMCUB mailbox, region, and fault registers; incorrect offsets can corrupt firmware communication, region setup, scratch exchange, interrupt acks, or fault reporting.
- DCHUBBUB and DCN VM context registers; wrong addresses can break page-table setup, VM fault diagnostics, display memory fetches, QoS/watermark programming, p-state transitions, or memory power gating.
- HUBP/HUBPREQ surface and flip registers; wrong mappings can display stale frames, flip at the wrong time, fetch wrong luma/chroma/meta addresses, corrupt cursor state, or cause underflow.
- Writeback and MCIF_WB registers; incorrect buffer, pitch, QoS, or watermark offsets can corrupt captured frames or cause backpressure/overflow.
- HDA/Azalia registers; wrong stream/endpoint offsets can break display audio, stream mapping, DMA, payload capability reporting, or CRC diagnostics.

Chunk boundaries are another edge case for downstream research merging. This document covers the start of the file through part of `CURSOR0_1`; later chunks must complete the remaining cursor and display-pipe instances rather than treating the line 2627 stop as an intentional omission.

## Test Signals

Useful validation signals are mostly compile-time, register-map, and hardware-behavior oriented:

- Kernel build coverage for DCN 3.2.1 resource code; missing or malformed macros should fail compilation in `dcn321_resource.c`.
- Static comparison of `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h` against AMD's generated register database, checking every offset and `_BASE_IDX` used by DCN 3.2.1 register-list macros.
- Boot and display bring-up on DCN 3.2.1 ASICs, confirming resource-pool construction, DMCUB firmware load, display clock initialization, and basic modeset.
- Multi-display mode-set, vblank, flip, and cursor tests that exercise HUBP/HUBPREQ/HUBPRET and interrupt status/destination registers.
- Suspend/resume, runtime power management, and display power-gating tests that touch DCCG, DCHUBBUB, HUBP, cursor, DMCUB, MMHUBBUB, and DCPG power/status registers.
- DMCUB mailbox and scratch diagnostics that verify inbox/outbox pointer, interrupt, timer, fault-address, and scratch registers behave as expected.
- Writeback/capture tests for DWBC and MCIF_WB paths, checking buffer addresses, pitch/size, CRC, gamut/gamma, overflow, and watermark behavior.
- Display audio tests over HDMI/DP that validate Azalia DTO, stream, endpoint, DMA, payload, and CRC register programming.
- VM fault and memory-fetch stress tests that exercise DCN VM contexts, surface/meta-surface addressing, MALL settings, QoS/prefetch/TTU parameters, and underflow recovery.

Regression symptoms from bad constants include blank displays, wrong refresh rate, clock-programming failures, lost vblank or HPD interrupts, DMCUB boot or mailbox timeouts, repeated VM faults, page flips using stale buffers, cursor corruption, display underflow, writeback overflow/corruption, broken HDMI/DP audio, or failures only on specific pipe instances because repeated `HUBP0`/`HUBP1` style macro groups diverge.

## Cross-Chunk Notes

Earlier lines in this same source are fully covered here because this is the first chunk of `dcn_3_2_1_offset.h`. Later chunks continue from the partial `CURSOR0_1` block and cover the rest of the DCN 3.2.1 register offset namespace. The final per-file research document should treat the whole header as one generated hardware register-layout contract used by DCN 3.2.1 resource construction, not as independent algorithms.
