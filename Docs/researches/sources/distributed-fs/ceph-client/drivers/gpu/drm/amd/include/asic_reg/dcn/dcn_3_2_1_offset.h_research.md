# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002021`: lines 1-2627, `Docs/researches/chunks/subset-b-002021_research.md`
- `subset-b-002022`: lines 2628-5157, `Docs/researches/chunks/subset-b-002022_research.md`
- `subset-b-002023`: lines 5158-7651, `Docs/researches/chunks/subset-b-002023_research.md`
- `subset-b-002024`: lines 7652-10192, `Docs/researches/chunks/subset-b-002024_research.md`
- `subset-b-002025`: lines 10193-12823, `Docs/researches/chunks/subset-b-002025_research.md`
- `subset-b-002026`: lines 12824-14596, `Docs/researches/chunks/subset-b-002026_research.md`

## Chunk Research

### subset-b-002021: lines 1-2627

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

### subset-b-002022: lines 2628-5157

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h lines 2628-5157

## Purpose

This chunk is generated AMD DCN 3.2.1 register-offset metadata. It contains no executable C logic; it exports symbolic preprocessor constants that map display-controller register names to MMIO offsets plus companion base-index selectors. Runtime code combines each `reg...` offset with its matching `reg..._BASE_IDX` through `BASE(...)`/`SRI(...)`/`SRII(...)` style macros before issuing register reads and writes.

The requested range is a middle slice of `dcn_3_2_1_offset.h`. It starts at the tail of cursor instance 1 display metadata registers, covers complete HUBP/HUBPREQ/HUBPRET/cursor blocks for pipe instances 2 and 3, covers DPP/CNVC/DSCL/CM/DPP_TOP blocks for DPP instances 0 through 3, covers MPC/MPCC blend blocks for MPCC instances 0 through 3, and ends after the complete `MPCC_OGAM0` output-gamma block. The next chunk begins at `MPCC_OGAM1`, so this range owns only the first output-gamma MPCC block.

The slice has 2,392 `#define` lines: 1,196 register-offset macros and 1,196 matching `_BASE_IDX` macros. Most entries use base index `2` for DCN display pipe blocks; MPC/MPCC/OGAM entries use base index `3`. Although this tree is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata and has no Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or callbacks in this range. The public surface is the generated macro namespace:

- `reg<block>_<register>`: numeric DCN 3.2.1 MMIO register offset.
- `reg<block>_<register>_BASE_IDX`: base-address segment selector used with the SOC/DCN register-base table.

Major macro families in this chunk:

- Tail of `CURSOR0_1`: display metadata data-mover control, QoS, status, software control, and data registers.
- `HUBP2` and `HUBP3`: surface configuration, address/tiling config, primary and secondary viewport coordinates for luma/chroma planes, request sizing, HUBP clock control, VMPG/MALL controls, MALL status, debug, and clock-measurement windows.
- `HUBPREQ2` and `HUBPREQ3`: surface pitch, VMID, primary/secondary surface and metadata addresses, flip control, in-use and earliest-in-use tracking, TTU/QoS/prefetch parameters, VM aperture/TLB control, blank/destination/vblank/flip/nominal timing parameters, cursor settings, p-state forcing, memory power, and status registers.
- `HUBPRET2` and `HUBPRET3`: HUBP return/read-line controls, memory-power controls/status, interrupts, read-line value/status, and earliest-in-use status.
- `CURSOR0_2` and `CURSOR0_3`: cursor surface addresses, size/control/position/hotspot/destination offsets, chunking, settings, DMDATA VM control, cursor DMDATA surface addresses, control/QoS/status/software data, and cursor cache controls.
- `CNVC_CFG0` through `CNVC_CFG3` and `CNVC_CUR0` through `CNVC_CUR3`: input pixel-format conversion, color-key alpha controls, cursor control/color, cursor LUT access/data, and cursor 2-bit control.
- `DSCL0` through `DSCL3`: scaler tap controls, recout/start/size/viewport setup for luma and chroma, ratio/initial-phase/filter controls, coefficient RAM access/data, manual replication, memory power, and debug registers.
- `CM0` through `CM3`: DPP color-management surface coefficients, bias/scale, pre-CSC and post-CSC coefficient banks, gamut remap, gamma-correction control/LUT/RAM A/B region programming, HDR multiplier, shaper LUT, 3D LUT, memory power, and alpha controls.
- `DPP_TOP0` through `DPP_TOP3`: DPP top control, clock control, CRC control/results, ordering/OBUF controls, boundary color, debug controls, memory power, and double-buffer control.
- `MPCC0` through `MPCC3`: MPCC blend mode, alpha controls, background color, output pipe selection, top/bottom muxing, status, DWB muxing, and debug registers.
- `MPC` shared block: output muxing, clock control, CRC, cursor gating, global flow controls, memory-power controls, debug/status, output CWB muxing, DWB mux, and vupdate lock set/clear/status registers.
- `MPCC_OGAM0`: output gamma control, LUT index/data/control, RAM A/B start/end/slope/base/offset/region registers, and gamut-remap coefficient controls for MPCC output-gamma instance 0.

## Control Flow

This header has no runtime control flow. It participates in a compile-time register-table construction pattern:

1. `dcn321_resource.c` includes `dcn_3_2_1_offset.h` and the matching `dcn_3_2_1_sh_mask.h`.
2. Resource macros such as `SR`, `SRI`, `SRI_ARR`, `SRII`, and `VUPDATE_SRII` paste block and instance IDs into names such as `regHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS`, `regCM3_CM_GAMCOR_LUT_DATA`, or `regMPCC_OGAM0_MPCC_OGAM_CONTROL`.
3. The macros compute an address as `ctx->dcn_reg_offsets[reg..._BASE_IDX] + reg...` and populate typed register tables for HUBP, DPP, MPC, MPCC, timing/hardware sequencing, and related DC blocks.
4. Runtime objects such as `hubp32_construct`, `dpp32_construct`, and `dcn32_mpc_construct` receive those tables. Later display code uses normal DC register helpers to program surface fetch, cursor, scaling, color, blending, gamma, CRC, power, and debug behavior.

The offsets do not encode the required sequencing. Consumers must still order modeset operations correctly: power/clock enablement, plane address flips, VM aperture setup, cursor updates, prefetch/watermark programming, scaler and color pipeline setup, MPCC tree updates, gamma LUT bank updates, vupdate locking, and suspend/resume restoration.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in files. It names MMIO-backed GPU state. The represented hardware state includes:

- Per-pipe HUBP fetch state: surface addresses, metadata addresses, pitch, tiling, viewports, flip state, VMID/aperture/TLB state, request sizing, MALL/VMPG behavior, prefetch/TTU/QoS timing, p-state forcing, memory power, and status/debug counters.
- Cursor state for pipes 1 through 3: cursor addresses, dimensions, position/hotspot, chunking, color/LUT controls, DMDATA fetch/control/QoS/status, cache controls, and software DMDATA access.
- DPP input, scaling, and color state: pixel-format conversion, color keying, scaler ratios/phases/filter coefficients, viewport/recout geometry, color-space conversion matrices, gamma-correction LUTs, HDR/shaper/3D LUT controls, alpha controls, and DPP CRC/debug/memory-power state.
- MPC/MPCC composition state: blend topology, alpha/background configuration, OPP selection, MPCC busy/idle status, DWB/CWB muxes, CRC capture, shared MPC memory power, and vupdate lock state.
- Output-gamma state for `MPCC_OGAM0`: LUT index/data windows, RAM A/B piecewise-linear regions, offsets, gamut remap coefficients, and bank/control selection.

Persistence is hardware-defined. Configuration registers generally retain values until the driver reprograms a mode, flips a plane, changes a color pipeline, gates power, suspends/resumes, or resets the ASIC. Status, interrupt, debug, counter, lock, and memory-power registers may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. This offset header does not describe those semantics; field masks and behavior live in the companion mask header and the consuming DC code.

## Dependencies And Integration Points

The chunk must remain synchronized with AMD's generated DCN 3.2.1 register database and with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h` for field shifts and masks.
- The DCN/SOC register-base tables exposed through `ctx->dcn_reg_offsets[...]`.
- DC resource and block headers that define register-list macros for HUBP, DPP, MPC/MPCC, color, cursor, DSC/timing, and hardware sequencing.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which uses the generated macros while creating the DCN 3.2.1 resource pool. In that file, disabled pipes are skipped based on pipe fuses, but the hardware instance ID is still passed into `dcn321_hubp_create`, `dcn321_dpp_create`, OPP/timing creation, and MPC creation. That makes instance-specific correctness important: pipe 2 and pipe 3 offsets from this chunk can be used even when lower-index pipes are fused off or when resource arrays are compacted around available hardware.

The important runtime integration points are the register tables passed to:

- HUBP construction for surface fetch, flip, cursor, VM, MALL, and prefetch programming.
- DPP construction for CNVC, cursor, DSCL, CM, DPP_TOP, CRC, and memory-power programming.
- MPC construction for MPCC blending, output muxing, CRC, DWB/CWB muxing, vupdate locks, and output gamma.
- Hardware sequencing and diagnostics paths that read status/debug/CRC/lock registers during modesets, validation, and debugging.

## Risks And Edge Cases

- Offset or base-index drift is the main risk. These macros are untyped constants; a wrong value can compile cleanly while targeting the wrong MMIO register or base segment.
- The base-index split matters. HUBP/HUBPREQ/HUBPRET/CURSOR/DPP macros in this range use base index `2`, while MPC/MPCC/OGAM macros use base index `3`. Mixing those segments would redirect otherwise plausible offsets into the wrong hardware aperture.
- Repeated pipe families are copy-sensitive. `HUBP2`/`HUBP3`, `HUBPREQ2`/`HUBPREQ3`, `CURSOR0_2`/`CURSOR0_3`, `CNVC`/`DSCL`/`CM`/`DPP_TOP` instances 0 through 3, and `MPCC0` through `MPCC3` are structurally similar but must remain instance-accurate.
- The range boundaries are artificial. The first lines are only the tail of `CURSOR0_1`, and the next chunk begins with `MPCC_OGAM1`; adjacent chunk reports are needed before making whole-file claims.
- Surface-address, VM, metadata, and flip registers are high impact. Bad offsets can produce page faults, stale scanout, corrupted compressed metadata, wrong plane content, or failures only during flips, multi-plane composition, or suspend/resume.
- Timing and prefetch registers are sensitive to bandwidth and power states. Errors in TTU, vblank/flip/nominal parameters, MALL, memory power, or p-state forcing can appear as intermittent underflow, flicker, blanking, or clock/power-management regressions.
- Color-pipeline and gamma registers are visually subtle. Wrong CM/DSCL/OGAM offsets can cause color-space conversion errors, bad HDR tone mapping, broken LUT programming, banding, or instance-local color regressions that basic modeset tests may miss.
- MPC/MPCC topology and vupdate locks affect atomic updates. Incorrect blend mux, status, OPP, DWB/CWB, or lock registers can break plane stacking, writeback, cursor composition, CRC validation, or atomic update synchronization.

## Test Signals

Useful validation combines generated-header consistency with display behavior:

- Build AMDGPU/DC with DCN 3.2.1 support enabled; missing or renamed macros should fail in `dcn321_resource.c` or block register-list expansion.
- Mechanically verify that every non-`_BASE_IDX` `reg...` macro in lines 2628-5157 has exactly one matching `_BASE_IDX` macro. This range should contain 1,196 offset macros and 1,196 base-index macros.
- Verify base-index distribution: 1,015 `_BASE_IDX` entries with value `2` and 181 with value `3` in this range.
- Diff these offsets against AMD's authoritative DCN 3.2.1 register source and nearby generated headers such as `dcn_3_2_0_offset.h` and `dcn_3_6_0_offset.h` where block layout is expected to match.
- Exercise modesets and page flips using at least four pipes where hardware allows, with special attention to pipes 2 and 3 because their HUBP/HUBPREQ/HUBPRET/cursor blocks are fully covered here.
- Validate cursor movement, cursor format/color/LUT behavior, cursor DMDATA, and cursor cache paths on multiple pipes.
- Test scaler and viewport paths: luma/chroma viewport changes, scaling ratios, filter coefficient updates, recout changes, rotation/format combinations, and multi-plane updates.
- Validate color-management paths: pre-CSC/post-CSC matrices, gamut remap, gamma correction, HDR multiplier, shaper LUT, 3D LUT, alpha controls, and output gamma on MPCC 0.
- Exercise composition and synchronization: multi-plane alpha blending, MPCC tree changes, OPP remapping, vupdate lock set/clear, DWB/CWB muxing, CRC capture, and atomic updates under load.
- Watch kernel logs and display diagnostics for page faults, underflow, flip timeouts, vupdate lock stalls, pipe-specific blanking, color regressions, CRC mismatches, memory-power status failures, and resume failures.

## Cross-Chunk Notes

Earlier chunks own the beginning of `CURSOR0_1` and prior HUBP/DPP/MPC register blocks. Later chunks continue with `MPCC_OGAM1` and the remaining DCN 3.2.1 register-offset namespace. The final per-file research document should merge adjacent chunks before claiming complete coverage of all HUBP instances, all DPP/CM/DSCL instances, all MPCC output-gamma instances, or the complete `dcn_3_2_1_offset.h` hardware map.

### subset-b-002023: lines 5158-7651

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h - subset-b-002023

## Scope

- Chunk id: `subset-b-002023`
- Source lines: 5158-7651
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`
- Observed content: 2,494 generated header lines covering 24 address-block comments, 1,200 register-offset macros, and 1,200 matching `_BASE_IDX` macros.

This chunk is part of the generated AMD DCN 3.2.1 register-offset header. It has no executable C logic; it publishes MMIO register offsets and base-index selectors for DCN321 display blocks. The slice starts at MPCC OGAM instance 1, covers OGAM instances 1-3, MPCC MCM instances 0-3, MPC OCSC, ABM instances 0-3, OPP/DPG/FMT/OPPBUF/OPP pipe CRC instances 0-2, and ends at the first `FMT2` register.

## Purpose

The chunk provides symbolic register-address constants used by the AMDGPU display core to construct per-ASIC register tables. Each hardware register has two generated macros:

- `reg...`: the register's offset within the DCN register aperture.
- `reg..._BASE_IDX`: an index into `ctx->dcn_reg_offsets[]`, allowing the same source-level register list macros to resolve to ASIC-specific segment bases.

At runtime, DCN321 resource creation includes this header and combines the offset and base-index macros through helpers such as `SRI`, `SRII`, and `REG`. For example, `dcn321_resource.c` includes `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`; `dcn321_mpc_create()` expands `dcn_mpc_regs_init()`, and `dcn321_opp_create()` expands `opp_regs_init()` for OPP instances. The effect is that shared DCN32 MPC/OPP/ABM code can call register helpers without hard-coding DCN321 addresses.

## Important APIs, Types, and Macros

There are no functions, structs, enums, or storage definitions in this chunk. Its public API is the generated preprocessor namespace:

- `regMPCC_OGAM1_*`, `regMPCC_OGAM2_*`, and `regMPCC_OGAM3_*`: 88 registers per instance for output gamma on MPCC pipes. These include `MPCC_OGAM_CONTROL`, LUT index/data/control registers, RAM A and RAM B start/end/offset/region programming registers for B/G/R channels, gamut remap control/mode, and matrix coefficient registers `C11_C12` through `C33_C34` for banks A and B.
- `regMPCC_MCM0_*` through `regMPCC_MCM3_*`: 139 registers per instance for multi-color management. Each instance includes shaper control/offset/scale/LUT programming, shaper RAM A/B region registers, 3D LUT mode/index/data/control/output normalization/offset registers, 1D LUT control/index/data/control, 1D LUT RAM A/B start/slope/base/end/offset/region registers, and `MPCC_MCM_MEM_PWR_CTRL`.
- `regMPC_OCSC_*`: 69 MPC output color-space-conversion registers. The block includes coefficient-format/mode control plus coefficient registers for banks A and B.
- `regABM0_*` through `regABM3_*`: 60 registers per Adaptive Backlight Management instance. Each instance exposes backlight PWM levels and duty-cycle controls, ABM control, ACE offset/slope and threshold controls, histogram/luma statistic registers, sample-rate registers, histogram-bin shift controls, 24 histogram-result registers, and `DC_ABM1_BL_MASTER_LOCK`.
- `regDPG0_*`, `regDPG1_*`, and `regDPG2_*`: 8 Display Pattern Generator registers per visible instance, including control, ramp control, dimensions, RGB/YCbCr colors, offset/segment, and status.
- `regFMT0_*`, `regFMT1_*`, and the beginning of `regFMT2_*`: formatter clamp, dynamic expansion, control, bit-depth, dither seed, side-by-side stereo, 4:2:0 memory-map, and 4:2:2 control registers. The chunk ends after `regFMT2_FMT_CLAMP_COMPONENT_R`.
- `regOPPBUF0_*` and `regOPPBUF1_*`: output-pixel-processor buffer control and 3D parameter registers.
- `regOPP_PIPE0_OPP_PIPE_CONTROL` and `regOPP_PIPE1_OPP_PIPE_CONTROL`: per-pipe OPP control registers.
- `regOPP_PIPE_CRC0_*` and `regOPP_PIPE_CRC1_*`: OPP pipe CRC control, mask, and result registers.

The base-index pattern is meaningful: the MPC/MPCC and ABM groups in this chunk use base index `3`, while the OPP/DPG/FMT/OPPBUF/CRC groups use base index `2`. Consumers must add the correct base segment before touching hardware.

## Control Flow

This header chunk has no local branches or calls. Runtime flow is supplied by the display-core resource and register-helper layers:

1. DCN321 resource construction includes the generated offset and shift/mask headers.
2. Register-list macros in component headers, such as DCN32 MPC lists, DCN20 OPP lists, and DCN32 ABM lists, are expanded with DCN321's `SRI`/`SRII` helpers.
3. The helpers compute absolute register addresses as `ctx->dcn_reg_offsets[reg..._BASE_IDX] + reg...`.
4. Component constructors store those computed addresses in register tables for MPC, OPP, ABM, and related display blocks.
5. Shared component code later uses `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and wait helpers with the computed register table plus matching field masks/shifts from `dcn_3_2_1_sh_mask.h`.

The register families imply hardware sequencing even though no sequencing is encoded here: LUT programming uses index/data/control patterns; double-buffered gamma and color-management flows select RAM A or RAM B; ABM collects luma/histogram state before programming backlight/PWM responses; OPP DPG/FMT/CRC blocks are configured during test-pattern, mode-set, color-depth, and CRC-capture paths.

## State and Persistence Behavior

The macros themselves are compile-time constants with no storage or persistence. They describe MMIO registers whose state is owned by hardware:

- MPCC OGAM and MCM state persists in hardware registers and LUT RAMs until reset, power-gating, or explicit reprogramming. This includes gamma modes, RAM bank selection, LUT entries, region definitions, shaper LUTs, 3D LUT content, 1D LUT content, gamut remap coefficients, and memory power-control state.
- MPC OCSC state persists as matrix format/mode and coefficient banks. It affects output color-space conversion after pipe composition.
- ABM state includes persistent configuration such as PWM user/current/target levels, duty-cycle limits, ACE thresholds, sample rates, and master locks, plus live or latched telemetry such as luma sums, min/max luma, pixel counts, histogram bins, and read-progress flags.
- OPP state includes formatter clamp/dither/depth and 4:2:0/4:2:2 settings, DPG test-pattern parameters, OPPBUF active/3D geometry, and CRC control/mask state. CRC result registers are readback state produced by the display pipe.
- `_BASE_IDX` constants are not hardware state; they select the base segment used for address translation. A wrong base index would redirect all subsequent register operations for that block.

## Dependencies

This chunk depends on AMDGPU/DC generated-register conventions:

- Matching field layout definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`.
- DCN321 resource glue in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, especially the `BASE`, `SRI`, `SRII`, and `REG` macros that turn these constants into absolute addresses.
- Register-list macros and component structs in DC display code, including DCN32 MPC, DCN20 OPP, and DCN32 ABM definitions.
- The DC context's populated `dcn_reg_offsets[]` table. The generated offsets are relative values and are only valid after adding the correct base segment.
- Low-level AMDGPU MMIO helpers and display-core register access macros that expect the `regNAME` and `regNAME_BASE_IDX` naming convention.

The header is generated data, not a hand-authored API. Correctness depends on the hardware register database, generator, offset header, shift/mask header, and component register lists staying in lockstep.

## Integration Points

Primary integration points are:

- `dcn321_resource.c`: includes this header and initializes register tables for DCN321 resource objects. `dcn321_mpc_create()` builds the MPC register table used by `dcn32_mpc_construct()`, while `dcn321_opp_create()` builds OPP register tables for OPP instances 0-3. ABM register arrays are also initialized through DCN32 ABM register-list macros.
- `dc/mpc/dcn32/dcn32_mpc.c`: consumes MPCC MCM and OGAM addresses to control LUT memory power, program shaper LUTs, program 1D LUTs, program 3D LUTs, and manage color/gamut remap behavior.
- `dc/opp/dcn10` and `dc/opp/dcn20`: consume FMT, DPG, OPPBUF, and OPP pipe CRC addresses for clamping, dither/bit-depth behavior, test-pattern generation, 3D output buffering, CRC capture, and state readback.
- `dc/dce/dmub_abm_lcd.c` and ABM resource/hwseq paths: use ABM register addresses for histogram/luma setup, PWM/backlight level tracking, ABM pipe binding, and DMUB-managed backlight commands.
- User-visible display flows: mode sets, color-management updates, HDR/color-space programming, panel self-refresh/backlight behavior, debug test patterns, and CRC validation all depend on these offsets being correct for DCN321 hardware.

## Risks and Edge Cases

- Offset drift is high impact. A one-register error in an OGAM/MCM LUT, ABM PWM register, FMT register, or CRC result register can silently program the wrong hardware and produce color corruption, broken backlight behavior, invalid CRCs, or display instability.
- The base-index value is as important as the offset. MPC/ABM blocks in this chunk use base index `3`, while OPP-related blocks use base index `2`; swapping these would address a different register aperture even if the relative offset is correct.
- The chunk starts after OGAM instance 0 and ends in the middle of the FMT2 block. Final per-file analysis must merge adjacent chunks before making complete claims about all instances.
- Repeated register families invite copy/paste mistakes. OGAM1-3, MCM0-3, ABM0-3, and OPP instances have very similar names but different offsets and base-address comments.
- LUT and matrix programming has ordering requirements outside this header. Index/data/control registers must be used in the sequence expected by hardware; this file only gives addresses.
- ABM telemetry registers and read-progress flags can be live or latched. Consumers need to honor existing read/clear/update semantics to avoid stale histogram/luma data or missed-frame indicators.
- OPP CRC result registers are diagnostic outputs, not configuration. Code must avoid treating them like ordinary writable controls.
- Generated headers can compile successfully while still being semantically wrong for a new ASIC stepping. Hardware validation is required in addition to build coverage.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Build coverage for DCN321 resource construction and every register-list macro that references OGAM, MCM, ABM, DPG, FMT, OPPBUF, OPP pipe, and CRC registers.
- Generated-header consistency checks verifying that each `reg...` macro has a matching `reg..._BASE_IDX` macro and that register-list macros refer only to names present in both offset and shift/mask headers.
- Address-table spot checks for representative instances: `MPCC_OGAM1_MPCC_OGAM_CONTROL`, `MPCC_MCM0_MPCC_MCM_SHAPER_CONTROL`, `MPCC_MCM3_MPCC_MCM_MEM_PWR_CTRL`, `ABM0_BL1_PWM_USER_LEVEL`, `ABM3_DC_ABM1_HG_RESULT_24`, `DPG2_DPG_STATUS`, `FMT1_FMT_422_CONTROL`, `OPPBUF1_OPPBUF_CONTROL1`, and `OPP_PIPE_CRC1_OPP_PIPE_CRC_RESULT2`.
- Hardware or emulator tests for color-management programming: output gamma bank switching, MCM shaper/1D LUT/3D LUT programming, gamut-remap coefficients, and memory power-control transitions.
- ABM tests covering PWM level writes/readbacks, histogram/luma sampling, missed-read progress clearing, DMUB ABM commands, suspend/resume, and eDP panel backlight transitions.
- OPP tests covering test-pattern generation, formatter clamp/bit-depth/dither behavior, 4:2:0/4:2:2 modes, OPPBUF 3D/segmentation parameters, and pipe CRC enable/mask/result readback.

## Chunk Boundary Notes

Line 5158 begins at `dce_dc_mpc_mpcc_ogam1_dispdec`; OGAM instance 0 is outside this chunk. Line 7651 stops after `regFMT2_FMT_CLAMP_COMPONENT_R_BASE_IDX`; the rest of FMT2 and later OPP instance 2/3 blocks continue in the following chunk. The merge/reconciliation lane should combine this report with adjacent chunk reports for complete per-file coverage of `dcn_3_2_1_offset.h`.

### subset-b-002024: lines 7652-10192

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h lines 7652-10192

## Scope

This chunk is a middle slice of the generated AMD DCN 3.2.1 register offset header. It contains C preprocessor constants only: no functions, structs, enums, or executable control flow are defined in these lines. The constants map display controller hardware register names to MMIO register offsets and pair nearly every offset with a `_BASE_IDX` selector used to choose a base address from `ctx->dcn_reg_offsets[]`.

The chunk starts inside the `dce_dc_opp_fmt2_dispdec` block at `regFMT2_FMT_CLAMP_COMPONENT_G` and ends inside the `dce_dc_dio_dig4_dispdec` block at `regDIG4_HDMI_ACR_44_0`. Because both boundaries are partial, the merge lane must combine adjacent chunks to recover the complete `FMT2` and `DIG4` block inventories.

## Purpose

The purpose of these lines is to provide ASIC-specific register addresses for several display pipeline areas:

- OPP/FMT/OPPBUF/DPG/DSCRM registers for output processing, format control, output buffers, pipe CRC, display pattern generation, DSC forwarding, ABM, and OPP top clock control.
- OPTC/ODM/OTG registers for timing generation, output data merger input control, global sync lock, CRC windows/results, dynamic refresh-rate control, vertical interrupts, update locks, and timing status.
- DIO HPD, DP, and DIG registers for hot-plug detection, DisplayPort link/stream programming, HDMI/AFMT metadata/audio packet controls, TMDS controls, stream encoder startup, and test/CRC features.

Downstream AMD display code includes this header from `display/dc/resource/dcn321/dcn321_resource.c` together with `dcn_3_2_1_sh_mask.h`. The resource code uses macros such as `SR`, `SRI`, and `SRI_ARR` to combine these offset constants with `ctx->dcn_reg_offsets[reg..._BASE_IDX]` and populate per-block register tables. Runtime code then accesses those tables through `REG_READ`, `REG_UPDATE`, `REG_SET`, `REG_GET`, `REG_WAIT`, and related register helper macros.

## Register Inventory In This Chunk

This slice contains 2,393 `#define reg...` lines: 1,197 register offset constants and 1,196 `_BASE_IDX` constants. The one-count mismatch is expected for this isolated chunk because the first complete register pair in view follows a missing prior line from the same `FMT2` block.

Visible block boundaries and representative contents:

- `dce_dc_opp_oppbuf2_dispdec`, base `0x2d0`: `regOPPBUF2_OPPBUF_CONTROL`, 3D parameter registers, and `OPPBUF_CONTROL1`.
- `dce_dc_opp_opp_pipe2_dispdec`, base `0x2d0`: `regOPP_PIPE2_OPP_PIPE_CONTROL`.
- `dce_dc_opp_opp_pipe_crc2_dispdec`, base `0x2d0`: pipe CRC control, mask, and result registers.
- `dce_dc_opp_dpg3_dispdec`, base `0x438`: DPG control, ramp, dimensions, RGB/YCbCr color, offset segment, and status registers.
- `dce_dc_opp_fmt3_dispdec`, base `0x438`: FMT clamp, dynamic expansion, format control, bit-depth control, dither seed, stereo, 4:2:0 memory, and 4:2:2 control registers.
- `dce_dc_opp_oppbuf3_dispdec`, `opp_pipe3`, and `opp_pipe_crc3`, base `0x438`: OPPBUF, pipe control, and CRC registers for pipe 3.
- `dce_dc_opp_dscrm0` through `dscrm3`: one `DSCRM_DSC_FORWARD_CONFIG` register per instance.
- `dce_dc_opp_opp_top_dispdec`: `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`.
- `dce_dc_optc_odm0` through `odm3`: per-ODM input global control, source select, data format, bytes-per-pixel, width, input clock, memory config, and spare registers.
- `dce_dc_optc_otg0` through `otg3`: large repeated timing generator blocks containing horizontal/vertical timing, trigger, force-count, flow, stereo, interlace, status, snapshot, interrupt, update-lock, master-enable, CRC, static-screen, 3D, GSL, DRR, DTO, request, DSC start, pipe update, and spare registers.
- `dce_dc_optc_optc_misc_dispdec`: GSL source select, OPTC clock control, ODM memory power control/status, and misc spare register.
- `dce_dc_dio_hpd0` through `hpd4`: HPD interrupt status/control, HPD control, fast training, and toggle filter control registers.
- `dce_dc_dio_dp0` through `dp4`: repeated DisplayPort link blocks covering link control, pixel format, MSA fields, stream control, DPHY training/test/CRC, secondary-data packets, audio N/M, MST/MSE slot allocation, MSO/DSC, DB, metadata, ALPM, GSP, and AUX-less ALPM registers.
- `dce_dc_dio_dig0` through `dig3`: repeated stream encoder blocks covering DIG front-end control, output CRC, clock/test/random patterns, FIFO controls, HDMI metadata/audio/ACR/VBI/infoframe/generic packets, AFMT, backend enable, TMDS, version, and forced disable.
- `dce_dc_dio_dig4`: begins in this chunk at base `0x1000`, but only runs through `regDIG4_HDMI_ACR_44_0`; later DIG4 HDMI ACR, AFMT, backend, and TMDS symbols are outside this chunk.

## Important APIs, Types, And Macros

The chunk itself exports register-name macros. Important naming forms are:

- `reg<block><instance>_<REGISTER>`: the register offset within the ASIC register map, for example `regOTG0_OTG_H_TOTAL`, `regDP0_DP_LINK_CNTL`, `regDIG0_DIG_FE_CNTL`, and `regHPD0_DC_HPD_INT_STATUS`.
- `reg<block><instance>_<REGISTER>_BASE_IDX`: index into `ctx->dcn_reg_offsets[]`; all constants in this chunk use base index `2`.
- Address block comments: generated metadata documenting the hardware address block and its local base address. These comments are not consumed by C code but are useful for validating instance spacing and generated output.

The consumer-side APIs are not defined here, but this chunk is designed for these integration macros in `dcn321_resource.c`:

- `BASE(reg..._BASE_IDX)` resolves the ASIC segment base using `ctx->dcn_reg_offsets`.
- `SRI(reg_name, block, id)` constructs one register address from a block instance, for example `SRI(OTG_H_TOTAL, OTG, inst)` expands toward `regOTG<inst>_OTG_H_TOTAL`.
- `SRI_ARR(reg_name, block, id)` stores per-instance addresses into register arrays.
- `REG(reg_name)` handles non-instanced addresses by adding `ctx->dcn_reg_offsets[...]` and `reg...`.

Those populated register tables are used by hardware object headers and implementations such as:

- OPP paths: `dc/opp/dcn10/dcn10_opp.h` maps `FMT_CONTROL` and `OPPBUF_CONTROL`; `dcn10_opp.c` updates format, dithering, clamping, pixel encoding, and output-buffer width fields.
- OPTC paths: `dc/optc/dcn10/dcn10_optc.h` and `dcn32_optc.h` map OTG registers; `dcn10_optc.c` writes and reads timing registers such as `OTG_H_TOTAL`.
- DIO link paths: `dc/dio/dcn30/dcn30_dio_link_encoder.h` maps `DP_LINK_CNTL`; DCE/DCN link encoder implementations update `DP_LINK_TRAINING_COMPLETE`.
- DIO stream encoder paths: `dc/dio/dcn30/dcn30_dio_stream_encoder.h` maps `DIG_FE_CNTL`; stream encoder code starts/stops DIG, selects sources, configures TMDS/HDMI encoding, and waits on symbol-clock state.
- HPD/GPIO/IRQ paths: HPD register macros feed IRQ services and GPIO HPD register tables through `DC_HPD_INT_STATUS` and related control/status registers.

## Control Flow

There is no runtime control flow in this header chunk. The effective flow is compile-time and initialization-time:

1. `dcn321_resource.c` includes this offset header and the matching shift/mask header.
2. Register-list macros in DCN resource and hardware object headers token-paste symbolic names into concrete constants from this file.
3. DCN321 resource construction populates register address structures for OPP, OPTC, DIO link encoders, stream encoders, HPD, IRQ, HW sequencer, and related blocks.
4. Runtime display paths call register helper macros against those tables. The helpers read/write MMIO registers, update bitfields defined by the shift/mask header, and may poll hardware status.

For example, an `SRI_ARR(DP_LINK_CNTL, DP, id)` use resolves to `BASE(regDP<id>_DP_LINK_CNTL_BASE_IDX) + regDP<id>_DP_LINK_CNTL`, and stream/link encoder code later manipulates the resolved address through register helper APIs.

## State And Persistence Behavior

The constants in this chunk have no in-memory mutable state and perform no persistence. Their only state-like behavior is their contribution to immutable register-address tables initialized during driver setup.

Hardware state lives outside the header in the GPU registers addressed by these constants. Writes through downstream `REG_UPDATE` or `REG_SET` calls persist in hardware until overwritten, reset, power-gated, or reinitialized. Status and result registers in this chunk, such as OTG CRC results, HPD status, DP DPHY CRC/status, DIG output CRC, and OPP pipe CRC results, expose current hardware state to the driver.

Because all visible `_BASE_IDX` values are `2`, this chunk depends on DCN321 platform setup assigning the correct MMIO segment base to `ctx->dcn_reg_offsets[2]`. A bad base-index table causes every register derived from these constants to target the wrong MMIO region even if the offsets are individually correct.

## Dependencies

Direct dependencies are preprocessor-level:

- The include guard and offset macro names from the same generated header.
- `dcn_3_2_1_sh_mask.h`, which must define matching bit shifts and masks for fields within the registers named here.
- `dcn321_resource.c` macro definitions that use `reg...` and `reg..._BASE_IDX` names.
- Resource and hardware object headers that refer to these names through `SRI`, `SRI_ARR`, `SF`, `SE_SF`, `LE_SF`, `OPP_SF`, and related macros.
- `reg_helper.h` and DC register helper infrastructure for actual MMIO access after resource construction.

External dependencies are hardware/ASIC contracts:

- The DCN 3.2.1 register map must match these offsets exactly.
- The block instance spacing implied by repeated bases must match the silicon layout: OTG instances step through offset groups from `0x1b2a` to `0x1d21`, DP instances from `0x2108` to `0x2567`, DIG instances from `0x208b` onward, and HPD instances from `0x1f14` through `0x1f38`.
- DisplayPort, HDMI, DSC, MST/MSE, ALPM, GSL, DRR, CRC, and HPD behavior depends on register semantics defined outside this header.

## Integration Points

Key integration points visible from this chunk:

- `display/dc/resource/dcn321/dcn321_resource.c`: includes this header and converts constants into typed register tables.
- `display/dc/resource/dcn32/dcn32_resource.h`: defines many of the register list macros that reference names in this chunk, including DIO, HPD, DP, OPP, and OTG lists.
- `display/dc/opp/*`: consumes FMT and OPPBUF addresses to program clamping, dither, pixel encoding, stereo, 4:2:0/4:2:2 handling, and output-buffer parameters.
- `display/dc/optc/*`: consumes OTG/ODM/GSL/DRR/CRC addresses to program timing, update locks, vertical interrupts, global sync, dynamic refresh, CRC readback, and timing status.
- `display/dc/dio/*`: consumes DP and DIG addresses for link training, stream enable/disable, TMDS/HDMI packet programming, DP secondary data, DSC/MSO/MST, audio timing, and low-power features.
- `display/dc/irq/*` and `display/dc/gpio/*`: consume HPD addresses to detect cable state and service HPD interrupts.

## Risks And Edge Cases

- **Generated-header drift:** If this offset header and the matching shift/mask header are regenerated from different hardware descriptions, code may compile but manipulate wrong fields or addresses.
- **Wrong base index:** The visible `_BASE_IDX` constants are all `2`; if `ctx->dcn_reg_offsets[2]` changes meaning or is initialized incorrectly, the entire OPP/OPTC/DIO region addressed here is wrong.
- **Partial chunk boundaries:** This report cannot claim complete coverage of the `FMT2` or `DIG4` blocks. The final merged per-file research must reconcile previous and following chunks.
- **Instance-copy errors:** Repeated OTG, DP, DIG, and HPD blocks are mechanically similar. A single offset typo in one instance can affect only that pipe/connector and may appear as a monitor-specific or pipe-specific failure.
- **Cross-generation similarity:** Nearby headers such as DCN 3.2.0, 3.1.x, 3.5.x, 3.6.0, 4.1.0, and 4.2.0 contain similar symbols with some offset differences. Copying values across generations is risky even when names match.
- **Status/result side effects:** Some downstream reads/writes to interrupt, CRC, training, snapshot, or lock registers may have clear-on-read, latch, or timing-sensitive behavior defined by hardware, not by this header.
- **Power-gating interactions:** Registers under OPP, OPTC, DIO, and ODM may be inaccessible or stale when their blocks are power-gated; callers must rely on resource/hwseq sequencing rather than the constants alone.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Compile-time success of DCN321 resource code, especially token-pasted register list macros such as `SRI_ARR(OTG_H_TOTAL, OTG, inst)`, `SRI_ARR(DP_LINK_CNTL, DP, id)`, `SRI_ARR(DIG_FE_CNTL, DIG, id)`, and `SRI_ARR(DC_HPD_INT_STATUS, HPD, id)`.
- Static comparison against generated register-map sources or adjacent known-good DCN headers to ensure instance offsets and `_BASE_IDX` values are expected for DCN 3.2.1.
- Display bring-up tests across all exposed pipes/connectors: HPD detection, mode set, blank/unblank, DP link training, HDMI output, audio packet programming, DSC/MSO/MST paths, and stream encoder start/stop.
- Timing validation through OTG status/readback and vertical interrupt behavior, including DRR, GSL, update-lock, and CRC windows where supported.
- CRC/debug paths: OPP pipe CRC, OTG CRC, DIG output CRC, and DP DPHY CRC should produce stable expected values under controlled test patterns.
- Suspend/resume and power-gating tests to catch address mistakes in memory power control, clock control, and block reinitialization paths.
- Multi-instance coverage: tests should exercise OTG0-OTG3, DP0-DP4, DIG0-DIG4, and HPD0-HPD4 rather than validating only instance 0.

### subset-b-002025: lines 10193-12823

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h lines 10193-12823

## Purpose

This chunk is a generated AMD DCN 3.2.1 register-offset header slice. It contains C preprocessor constants only: `reg...` macros for register offsets and paired `reg..._BASE_IDX` macros for selecting the base address segment used by the AMDGPU Display Core register helpers. There are no C functions, structs, enums, branches, allocation paths, locks, MMIO calls, or runtime persistence logic in this range.

The source tree path is under a local `ceph-client` mirror, but this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic. The macros in this chunk support the DCN321 display resource layer and its lower-level DIO, DCIO, DSC, HPO, AFMT, VPG, APG, AUX, I2C, and stream encoder blocks.

The range is boundary-partial at both ends. It begins in the tail of the `DIG4` HDMI/TMDS encoder register block, after the block comment and base address from the previous chunk, and starts with `regDIG4_HDMI_ACR_44_0_BASE_IDX` followed by the remaining HDMI audio-clock-regeneration, AFMT, DIG backend, TMDS, version, and force-disable offsets. It ends inside the HPO DP stream encoder 3 VPG block at `regVPG9_VPG_MEM_PWR`; the rest of VPG9 and the following DP SYM32 encoder 3 block continue in the next chunk.

Within lines 10193-12823 there are 2,368 `#define` lines: 1,184 register offset macros and 1,184 matching `_BASE_IDX` macros. All visible `_BASE_IDX` values are `2`, except the range starts after a prior `DIG4` register value and includes the paired base-index macro for that prior register. Address-block comments identify 66 complete or partial hardware blocks after the initial `DIG4` continuation.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `reg<REGISTER_OR_BLOCKED_REGISTER>` expands to a hardware register offset value.
- `reg<REGISTER_OR_BLOCKED_REGISTER>_BASE_IDX` expands to a base-index selector, used by `BASE(reg..._BASE_IDX)` in DCN resource code.
- `// addressBlock:` and `// base address:` comments document the generated hardware register block and its nominal base.

The main macro families in this chunk are:

- `regDIG4_*`: the tail of DIO stream encoder instance 4 HDMI/TMDS state. Visible registers include HDMI ACR `32/44/48` values and status, `AFMT_CNTL`, backend enable/control, TMDS control characters, sync/DC-balancer patterns, generated control bits, version, and force-disable.
- `regAFMT0_*` through `regAFMT5_*`: audio formatting blocks for DIO DIG0-DIG4 plus HPO HDMI stream encoder 0. Each block has VBI packet control, audio packet controls, audio info registers, IEC 60958 channel status words, audio CRC control/result/status, ramp controls, infoframe control, interrupt status, audio source control, and memory power.
- `regDME0_*` through `regDME9_*`: data/meta engine control and memory-control registers for DIO stream encoders, HPO HDMI, and HPO DP stream encoders.
- `regVPG0_*` through partial `regVPG9_*`: video packet generator blocks. VPG0-VPG8 are complete in the chunk and include generic packet access/data, frame and immediate update controls, generic status, memory power, ISRC access/data, and MPEG info registers. VPG9 is partial and stops at `VPG_MEM_PWR`.
- `regDP_AUX0_*` through `regDP_AUX4_*`: five AUX channel register blocks with AUX control, arbitration, software control, reply/data FIFOs, interrupt control, LS status and data, GTC sync, debug/status, and PHY wake control.
- `regDC_I2C_*`, `regDC_I2C_DDC*`, `regDC_I2C_EDID*`, and related macros: DOUT I2C control, arbitration, setup, speed, sw status, transaction, data, DDC/EDID detect and setup, and interrupt registers.
- `regDIO_*`: DIO scratch registers, global swap lock, stream encoder control, DIO memory power, interrupt status/control, and link E/F control.
- `regDC_GENERICA` through `regDCIO_SOFT_RESET`: DCIO top-level generic, GPIO, interrupt, clock, power, debug, and reset registers.
- `regDC_GPIO_*`, `regDCIO_*`, `regUNIPHY*`, `regAUXI2C_PAD_*`, `regPHY_*`, and `regBL_PWM_*`: DCIO chip/pad control, hotplug and sync GPIO masks, AUX/I2C pad control, generic output masks, backlight PWM/BLON/VARY_BL control, UNIPHY clock and GPIO power gates, and pad power status.
- `regDCIO_UNIPHY0_*` through `regDCIO_UNIPHY4_*`: five UNIPHY macro-control reserved register banks, each exposing reserved offsets 0-57. These are generated placeholders or opaque DCIO/PHY control locations rather than typed behavior in this header.
- `regDC_GPIO_PWRSEQ_*`, `regPWRSEQ_*`, and `regPANEL_PWRSEQ_*`: panel/power-sequencer GPIO enables, masks, power control, backlight control, ref-divider values, status, reset/debug/debug index/data, and spare state.
- `regDSCC0_*` through `regDSCC3_*`: four Display Stream Compression controller blocks. Each includes config, picture size, slice dimensions, bits-per-pixel, rate-control buffers/offsets/scales/ranges, mux, status, debug, memory power, and test-debug registers.
- `regDSCCIF0_*` through `regDSCCIF3_*`: small DSC controller interface config pairs.
- `regDSC_TOP0_*` through `regDSC_TOP3_*`: DSC top-level control and debug-control pairs.
- `regHPO_TOP_*` and `regDP_STREAM_MAPPER_*`: HPO top clock/hardware control and four DP stream mapper controls.
- `regDP_STREAM_ENC0_*` through `regDP_STREAM_ENC3_*`: HPO DP stream encoder clock, input mux, audio control, clock-ramp-adjuster FIFO status controls, and spare registers.
- `regAPG0_*` through `regAPG3_*`: HPO DP audio packet generator control, debug generator, packet control, audio CRC controls/results, status/status2, memory power, and spare registers.
- `regDP_SYM32_ENC0_*` through `regDP_SYM32_ENC2_*`: HPO DP 32-symbol encoder blocks for instances 0-2. Each block includes encoder control, video FIFO, double-buffer controls, pixel format, video MSA0-MSA8, hblank control, SDP/GSP controls 0-14, audio and metadata packet controls, MSA/VBID/stream/panel-replay controls, video CRC controls/results/status, memory power, and spare registers.

## Address-Block Coverage

The generated block layout in this chunk is regular and instance-oriented:

- DIO stream/audio packet path: tail of `DIG4`, AFMT0-AFMT4, DME0-DME4, VPG0-VPG4.
- DIO sideband path: DP_AUX0-DP_AUX4, DOUT I2C, and DIO miscellaneous controls.
- DCIO path: DCIO top-level, DCIO chip/pad controls, and UNIPHY0-UNIPHY4 reserved macro-control banks.
- Panel and compression path: PWRSEQ0, DSC controller/interface/top blocks for DSC0-DSC3.
- HPO path: HPO top, DP stream mapper, HPO HDMI stream encoder 0 AFMT/DME/VPG, HPO DP stream encoders 0-3, APG0-APG3, DME6-DME9, VPG6-partial VPG9, and DP SYM32 encoders 0-2.

The complete block list observed after the initial `DIG4` continuation is:

`dce_dc_dio_dig0_afmt_afmt_dispdec`, `dce_dc_dio_dig1_afmt_afmt_dispdec`, `dce_dc_dio_dig2_afmt_afmt_dispdec`, `dce_dc_dio_dig3_afmt_afmt_dispdec`, `dce_dc_dio_dig4_afmt_afmt_dispdec`, `dce_dc_dio_dig0_dme_dme_dispdec`, `dce_dc_dio_dig0_vpg_vpg_dispdec`, `dce_dc_dio_dig1_dme_dme_dispdec`, `dce_dc_dio_dig1_vpg_vpg_dispdec`, `dce_dc_dio_dig2_dme_dme_dispdec`, `dce_dc_dio_dig2_vpg_vpg_dispdec`, `dce_dc_dio_dig3_dme_dme_dispdec`, `dce_dc_dio_dig3_vpg_vpg_dispdec`, `dce_dc_dio_dig4_dme_dme_dispdec`, `dce_dc_dio_dig4_vpg_vpg_dispdec`, `dce_dc_dio_dp_aux0_dispdec`, `dce_dc_dio_dp_aux1_dispdec`, `dce_dc_dio_dp_aux2_dispdec`, `dce_dc_dio_dp_aux3_dispdec`, `dce_dc_dio_dp_aux4_dispdec`, `dce_dc_dio_dout_i2c_dispdec`, `dce_dc_dio_dio_misc_dispdec`, `dce_dc_dcio_dcio_dispdec`, `dce_dc_dcio_dcio_chip_dispdec`, `dce_dc_dcio_dcio_uniphy0_dispdec`, `dce_dc_dcio_dcio_uniphy1_dispdec`, `dce_dc_dcio_dcio_uniphy2_dispdec`, `dce_dc_dcio_dcio_uniphy3_dispdec`, `dce_dc_dcio_dcio_uniphy4_dispdec`, `dce_dc_pwrseq0_dispdec_pwrseq_dispdec`, `dce_dc_dsc0_dispdec_dscc_dispdec`, `dce_dc_dsc0_dispdec_dsccif_dispdec`, `dce_dc_dsc0_dispdec_dsc_top_dispdec`, `dce_dc_dsc1_dispdec_dscc_dispdec`, `dce_dc_dsc1_dispdec_dsccif_dispdec`, `dce_dc_dsc1_dispdec_dsc_top_dispdec`, `dce_dc_dsc2_dispdec_dscc_dispdec`, `dce_dc_dsc2_dispdec_dsccif_dispdec`, `dce_dc_dsc2_dispdec_dsc_top_dispdec`, `dce_dc_dsc3_dispdec_dscc_dispdec`, `dce_dc_dsc3_dispdec_dsccif_dispdec`, `dce_dc_dsc3_dispdec_dsc_top_dispdec`, `dce_dc_hpo_hpo_top_dispdec`, `dce_dc_hpo_dp_stream_mapper_dispdec`, `dce_dc_hpo_hdmi_stream_enc0_afmt_afmt_dispdec`, `dce_dc_hpo_hdmi_stream_enc0_dme_dme_dispdec`, `dce_dc_hpo_hdmi_stream_enc0_vpg_vpg_dispdec`, `dce_dc_hpo_dp_stream_enc0_dispdec`, `dce_dc_hpo_dp_stream_enc0_apg_apg_dispdec`, `dce_dc_hpo_dp_stream_enc0_dme_dme_dispdec`, `dce_dc_hpo_dp_stream_enc0_vpg_vpg_dispdec`, `dce_dc_hpo_dp_sym32_enc0_dispdec`, `dce_dc_hpo_dp_stream_enc1_dispdec`, `dce_dc_hpo_dp_stream_enc1_apg_apg_dispdec`, `dce_dc_hpo_dp_stream_enc1_dme_dme_dispdec`, `dce_dc_hpo_dp_stream_enc1_vpg_vpg_dispdec`, `dce_dc_hpo_dp_sym32_enc1_dispdec`, `dce_dc_hpo_dp_stream_enc2_dispdec`, `dce_dc_hpo_dp_stream_enc2_apg_apg_dispdec`, `dce_dc_hpo_dp_stream_enc2_dme_dme_dispdec`, `dce_dc_hpo_dp_stream_enc2_vpg_vpg_dispdec`, `dce_dc_hpo_dp_sym32_enc2_dispdec`, `dce_dc_hpo_dp_stream_enc3_dispdec`, `dce_dc_hpo_dp_stream_enc3_apg_apg_dispdec`, `dce_dc_hpo_dp_stream_enc3_dme_dme_dispdec`, and partial `dce_dc_hpo_dp_stream_enc3_vpg_vpg_dispdec`.

## Control Flow

This header has no executable control flow. The runtime flow is indirect through generated register-list expansion:

1. `display/dc/resource/dcn321/dcn321_resource.c` includes `dcn/dcn_3_2_1_offset.h` and `dcn/dcn_3_2_1_sh_mask.h`.
2. Resource macros such as `SR`, `SR_ARR`, `SRI`, and `SRI_ARR` expand register names into actual offsets using `BASE(reg..._BASE_IDX) + reg...`.
3. DCN321 constructors populate per-block register tables for AUX engines, I2C engines, VPG, AFMT, APG, DIO stream encoders, HPO DP stream encoders, DSC blocks, DWB/MMHUBBUB, and other resource objects.
4. Runtime display code calls block-specific helpers, which use those tables with register helpers such as read/write/update/get/set wrappers to perform MMIO operations.
5. Hardware and firmware state machines, not this header, determine ordering for AUX transactions, I2C transactions, HDMI/TMDS packet generation, DSC programming, stream mapping, link enablement, HPO DP packet generation, panel power sequencing, and DCIO/PHY control.

Because this file only supplies numeric constants, sequencing rules are external. Consumers must still follow the DCN hardware programming model for power-up, link training, stream encoder setup, DSC configuration, audio packet programming, panel power transitions, HPO DP stream mapping, and suspend/resume.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It names MMIO-backed hardware registers whose values live in display hardware:

- AFMT, VPG, APG, DME, DIG, and stream encoder registers hold packet, audio, metadata, clock, video-stream, CRC, FIFO, status, spare, and memory-power state.
- AUX and I2C registers hold sideband transaction setup, data, arbitration, interrupt, status, and debug state for DP AUX, DDC, and EDID access.
- DCIO and UNIPHY registers hold pad, GPIO, power, clock, interrupt, reset, and opaque PHY macro-control state.
- PWRSEQ and panel registers hold panel power, reset, backlight, BLON, ref-divider, status, and debug state.
- DSC controller/interface/top registers hold compression configuration, rate-control, slice/picture, memory-power, status, and debug state.
- HPO top, DP stream mapper, HPO DP stream encoders, APG, VPG, DME, and DP SYM32 encoders hold high-performance output mapping, audio/video packet, Main Stream Attribute, VBID, SDP/GSP, metadata, panel replay, CRC, and memory-power state.

Persistence and side effects are hardware-defined. Some registers are configuration values that remain until a modeset, link retrain, power transition, suspend/resume, or ASIC reset. Others are status latches, FIFOs, clear-on-read or write-one-to-clear interrupt bits, self-clearing triggers, firmware-owned debug/scratch state, or power-gated memory controls. The generated offset header does not encode access type, reset value, volatility, locking, ownership, or required delays.

## Dependencies And Integration Points

This header must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`, which supplies matching field shifts and masks. Offset/mask drift can compile successfully while causing masked reads or writes to target the wrong hardware register or bit fields.

The direct source include site found for this DCN 3.2.1 offset header is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`

Important integration points visible from that resource code include:

- `BASE(seg)`, `SR`, `SR_ARR`, `SRI`, `SRI_ARR`, `SR_ARR_I2C`, and `SRI_ARR_I2C`, which combine the generated `_BASE_IDX` and offset macros into concrete register table values.
- `dcn321_aux_engine_create()`, which instantiates five AUX engines using AUX register lists that map to `regDP_AUX0_*` through `regDP_AUX4_*`.
- `dcn321_i2c_hw_create()`, which instantiates five I2C hardware engines using DOUT I2C register constants.
- `dcn321_vpg_create()`, which initializes VPG instances 0-9. This chunk includes complete VPG0-VPG8 register offsets and the beginning of VPG9.
- `dcn321_afmt_create()`, which initializes AFMT instances 0-5. The chunk contains AFMT0-AFMT5 register-offset blocks.
- `dcn321_apg_create()`, which initializes APG0-APG3 for HPO DP audio packet generation.
- `dcn321_stream_encoder_create()`, which maps DIO engine IDs to VPG/AFMT/DIG register blocks and constructs DCN32 DIO stream encoders.
- `dcn321_hpo_dp_stream_encoder_create()`, which maps `ENGINE_ID_HPO_DP_0..3` to HPO stream encoder instances, VPG instances 6-9, and APG instances 0-3.
- `dcn321_dsc_create()`, which instantiates DSC0-DSC3 from the DSCC, DSCCIF, and DSC_TOP register families in this chunk.
- DCIO/link encoder construction and GPIO/pad translation paths, which consume DCIO, UNIPHY, HPD, AUX/I2C pad, backlight, and panel power-sequence register constants through shared DCN32/DCN321 helpers.

Functional dependencies include the AMDGPU register-helper layer, Display Core resource construction, DIO and HPO stream encoder implementations, AUX/I2C sideband engines, DCN32 DSC support, DCIO GPIO/pad helpers, panel/backlight control, and the hardware register database that generated this file.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong offset or `_BASE_IDX` can compile cleanly but direct MMIO reads/writes to the wrong display register.
- This chunk is not a standalone logical unit. It starts in the middle of the `DIG4` HDMI/TMDS block and ends in the middle of `VPG9`; merge/reconciliation must combine adjacent chunks for complete per-file coverage.
- Instance numbering is dense and easy to mis-map. DIO VPG/AFMT/DME instances 0-4, HPO HDMI instance 5, HPO DP VPG instances 6-9, APG instances 0-3, and DP SYM32 instances 0-2 in this range are related but not interchangeable.
- The HPO DP stream encoder mapping is asymmetric: HPO DP stream encoder `n` uses VPG `n + 6` and APG `n`. A correct-looking VPG macro from the wrong instance can send SDP/metadata/audio packet state to the wrong HPO stream.
- All visible base indices are `2`, but resource code still depends on `_BASE_IDX` macros. If a future generated file changes base-index assignment, hardcoded assumptions would break.
- AUX and I2C registers include transaction FIFOs, arbitration, reply, timeout, interrupt, and status registers. Writing a status or FIFO offset as though it were ordinary configuration can lose sideband transactions or mask hotplug/DDC failures.
- DCIO/UNIPHY blocks expose many reserved macro-control registers. Reserved or opaque registers should not be used without hardware documentation, even when generated offsets exist.
- Power and memory-power registers appear across AFMT, VPG, APG, DP SYM32, DIO, DCIO, DSC, and panel blocks. Incorrect programming can cause failures that only reproduce across display hotplug, suspend/resume, PSR/panel replay, backlight transitions, or clock/power gating.
- DSC rate-control and picture/slice offsets are highly parameter-sensitive. Offset drift can produce link-visible corruption rather than an immediate kernel failure.
- Status, interrupt, clear, control, data, and debug registers are indistinguishable at the preprocessor level. Callers need field masks and hardware access-type knowledge before writing to them.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU Display Core with DCN321 support enabled. Missing or renamed generated macros should surface in `dcn321_resource.c` and the shared DIO/HPO/DSC/AUX/I2C register-list expansion paths.
- Mechanically compare lines 10193-12823 against the authoritative AMD register database or a regenerated `dcn_3_2_1_offset.h`. Every visible register macro should have the expected offset and exactly one matching `_BASE_IDX`.
- Cross-check corresponding field definitions in `dcn_3_2_1_sh_mask.h` for AFMT, VPG, APG, AUX, I2C, DCIO, PWRSEQ, DSCC, DP_STREAM_ENC, and DP_SYM32 register names.
- On DCN321 hardware, exercise DIO HDMI/TMDS and DP outputs across modesets, hotplug, audio enable/disable, infoframe/metadata updates, and suspend/resume.
- Exercise DP AUX and DDC/EDID paths on all five AUX/I2C instances. Monitor AUX reply/data/status registers, I2C arbitration, DDC detection, EDID detection, and interrupt behavior.
- Validate HPO DP stream encoder paths for all four HPO DP engines, paying special attention to the VPG6-VPG9 and APG0-APG3 instance mapping.
- Test DSC enablement across multiple streams and slice/rate-control configurations. Register dumps should show DSCC0-DSCC3 and DSCCIF/DSC_TOP offsets matching the selected instance.
- Test panel power and backlight sequences, including suspend/resume and blank/unblank, because PWRSEQ, BL PWM, BLON, and panel status registers in this chunk affect user-visible display bring-up.
- Use register dumps before and after modeset, link retrain, audio packet update, DSC programming, HPO stream mapping, and power transitions. Writes should land in the intended instance, reserved registers should remain stable, and memory-power/status bits should behave consistently with hardware documentation.

## Cross-Chunk Notes

The final per-file report should merge this chunk with the previous chunk for the complete `DIG4` HDMI/TMDS block and with the following chunk for the rest of `VPG9` plus `DP_SYM32_ENC3` and later DCN321 offset definitions. This document is intentionally limited to the assigned source range and should be treated as the source-tree-aligned chunk artifact for `subset-b-002025`.

### subset-b-002026: lines 12824-14596

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h lines 12824-14596

## Purpose

This chunk is the final slice of the generated AMD DCN 3.2.1 register-offset header. It contains C preprocessor constants that map display, audio, VGA, and Azalia indexed register names to numeric offsets or indirect indexes used by the AMDGPU display driver. The range is not executable code; it is a hardware ABI description consumed together with `dcn_3_2_1_sh_mask.h` by DCN 3.2.1 resource, stream encoder, link encoder, and audio register-table code.

The chunk contains 1,522 `#define` entries: 453 `reg*` macros for direct MMIO-style register offsets and their `_BASE_IDX` selectors, plus 1,069 `ix*` macros for indexed VGA/Azalia/codec register spaces. It starts in the tail of HPO DP stream encoder 3 VPG definitions, covers HPO DP `SYM32` stream encoder 3, HPO DP link/DPHY symbol blocks 0 and 1, and then switches to HDA/Azalia controller, output streams, VGA indexed registers, Azalia codec verb indexes, audio descriptors, CRC result indexes, stream latency counters, endpoint indexes, and input endpoint indexes. The file ends at line 14596 with the `#endif`, so this work item closes the header.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display-driver register metadata. It has no distributed-filesystem logic.

## Important APIs, Types, And Register Groups

There are no functions, structs, enums, variables, includes, locks, allocations, or callbacks in this chunk. Its public interface is the macro namespace:

- `reg<block>_<register>`: a direct register offset value.
- `reg<block>_<register>_BASE_IDX`: a register-base selector, mostly `2` for DCN display register apertures in this slice, `0` for HDA controller/stream registers, and `1` for selected alias offsets.
- `ix<register>`: an indexed-register address used through an index/data register pair or legacy indexed IO-style interface.

Major register blocks in the exact line range:

- `dce_dc_hpo_dp_sym32_enc3_dispdec` at base `0x1b664`: HPO DP symbol stream encoder 3 registers. It defines video FIFO control, MSA double-buffering, pixel format, `VID_MSA0` through `VID_MSA8`, horizontal blank control, secondary data packet controls, audio SDP controls, metadata packet control, VBID/stream/panel replay controls, CRC control/result/status, memory power, and spare registers.
- `dce_dc_hpo_dp_link_enc0_dispdec` and `dce_dc_hpo_dp_link_enc1_dispdec`: HPO DP link encoder clock-control and spare registers for link encoder instances 0 and 1.
- `dce_dc_hpo_dp_dphy_sym320_dispdec` and `dce_dc_hpo_dp_dphy_sym321_dispdec`: HPO DP DPHY/SYM32 transport registers for two instances. Each defines control/status, SAT update, virtual-channel rate controls, SAT VC slots/status, test-pattern configuration, PRBS seeds, square pulse, custom test-pattern payloads, error status, symbol override, and CRC config/status/count.
- `dce_dc_hda_azcontroller_azdec`: core HDA/Azalia controller register offsets for CORB/RIRB pointers, controls, statuses, sizes, immediate command/response interfaces, DMA position base addresses, and a wall-clock alias.
- `dce_dc_hda_azendpoint_azdec`, `dce_dc_hda_azinputendpoint_azdec`, and `dce_dc_hda_azroot_azdec`: immediate command data/index register aliases for endpoint, input endpoint, and root nodes.
- `dce_dc_hda_azstream0_azdec` through `dce_dc_hda_azstream7_azdec`: output stream descriptor offsets. Each stream repeats control/status, link position in current buffer, cyclic buffer length, last valid index, FIFO size/format, BDL pointer lower/upper base, and an alias for link position.
- `vga_vgaseqind`, `vga_vgacrtind`, `vga_vgagrphind`, and `vga_vgaattrind`: legacy VGA sequencer, CRT controller, graphics controller, and attribute-controller indexed register numbers.
- `azendpoint_f2codecind`: Azalia F2 output codec converter and pin-control verb indexes, including converter format, stream/channel ID, digital converter controls, size/rate/stream-format parameters, pin sense/configuration defaults, speaker/channel allocation, audio descriptors, multichannel enables, lipsync/HBR, sink information, channel-status overrides, LPIB snapshots, format-change/wireless-display/keepalive status, and pin capabilities.
- `azendpoint_descriptorind` and `azendpoint_sinkinfoind`: audio descriptor entries and sink description/port-ID indexed registers.
- `azf0controller_azinputcrc0resultind`, `azinputcrc1resultind`, `azcrc0resultind`, and `azcrc1resultind`: per-channel CRC result indexes for input and output audio paths.
- `azinputendpoint_f2codecind` and `azroot_f2codecind`: F2 input converter/pin controls and root/function parameter/control verb indexes.
- `azf0stream0_streamind` through `azf0stream15_streamind`: per-stream FIFO size and latency counter control/result indexes.
- `azf0endpoint0_endpointind` through `azf0endpoint7_endpointind`: repeated F0 output endpoint indexed registers for converter capabilities/control, pin capabilities/control, audio descriptors, multichannel modes, sink info, hotplug/unsolicited response forcing, channel-status overrides, LPIB snapshots, format-change/wireless-display/remote-keepalive state, and audio enable/disable/format-change interrupt status.
- `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint7_inputendpointind`: repeated F0 input endpoint indexed registers for input converter capabilities/control, pin capabilities/control, multichannel/HBR/channel allocation, hotplug/unsolicited response, LPIB snapshots, input status, and infoframe data.

## Control Flow

This header has no runtime control flow. The effective control flow is created by AMDGPU display code that includes this header and uses its constants in register helper macros:

1. DCN 3.2.1 resource code includes `dcn/dcn_3_2_1_offset.h` and `dcn/dcn_3_2_1_sh_mask.h`.
2. Resource macros such as `SR`, `SRI`, `SRI_ARR`, and `SF` expand these offsets and field masks into register tables for a specific ASIC generation.
3. HPO DP stream/link encoder code uses the `DP_SYM32_ENC*` and `DP_DPHY_SYM32*` register table entries through `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` style helpers to program stream MSA, secondary data packets, DPHY mode, test patterns, SAT/VC allocation, CRC, and link state.
4. Audio code uses Azalia controller/endpoint index/data register definitions to expose HDMI/DP audio capabilities, configure converter stream formats, maintain channel and speaker allocation data, service hotplug/unsolicited response status, and report buffer/latency counters.

The chunk itself does not enforce sequencing. Ordering requirements such as DP stream blanking, MSA double buffering, SAT update polling, DPHY reset/enable transitions, HDA CORB/RIRB setup, immediate command handshakes, BDL programming, and indexed endpoint reads/writes live in the consuming driver code and hardware specifications.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It defines addresses for hardware state:

- HPO DP stream state: video timing metadata, pixel format, stream enable, VBID, panel replay, secondary data packets, audio packets, metadata packets, CRC result/status, and memory-power controls.
- HPO DP link/DPHY state: clock control, DPHY enable/reset/mode/lane configuration, SAT/VC allocation, VC rate programming, link test-pattern payloads, PRBS seeds, error status, symbol override, and CRC counters.
- HDA/Azalia controller state: CORB/RIRB ring pointers and controls, immediate command/response state, DMA position buffer addresses, wall-clock state, output stream descriptors, BDL pointers, FIFO/format state, and stream position aliases.
- Indexed VGA state: legacy sequencer/CRT/graphics/attribute registers exposed as indexes rather than normal `reg*` offsets.
- Azalia codec state: root/function parameters, converter format and stream IDs, pin sense/default configuration, audio descriptors, channel/speaker allocation, multichannel and HBR flags, sink info, channel status overrides, LPIB snapshots, format-change status, keepalive state, CRC result channels, FIFO size, latency counters, and endpoint interrupt/status indexes.

Persistence is hardware-defined. Some programmed values survive until another register write, stream reset, link reconfiguration, audio engine reset, suspend/resume, power-gating transition, or ASIC reset. Status and interrupt-style values may be read-only, sticky, self-clearing, or write-to-clear depending on the target register. The header only supplies numeric offsets/indexes and base selectors, so side effects must be understood by the register access path that uses them.

## Dependencies And Integration Points

Key dependencies and consumers visible in this source tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c` includes both `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`. Its register-table macros include Azalia endpoint index/data fields and audio DTO/controller clock-gating fields, making this header part of the DCN 3.2.1 resource object layout.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` and related HPO stream encoder code use the same `DP_SYM32_ENC` naming pattern defined here to instantiate per-instance stream encoder register lists.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.h` declares `DP_DPHY_SYM320` field lists that pair with the `DP_DPHY_SYM320` offsets in this chunk. The corresponding implementation programs DPHY control, test-pattern, SAT, and VC-rate fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` models Azalia endpoint index/data access, while generation resource files map `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `_DATA` fields through `SF(...)`.
- The generated shift/mask companion `dcn_3_2_1_sh_mask.h` must agree with every `reg*` entry that is accessed through field helpers. Offset-only `ix*` entries depend on the correct index/data access convention rather than normal MMIO field extraction.
- Similar VGA/Azalia endpoint index definitions appear across older `dce_*_offset.h` and `dcn_*_offset.h` headers, indicating this chunk preserves a cross-generation hardware interface that audio and display code expect to remain structurally stable.

## Risks And Edge Cases

- Generated offset drift is the main risk. A wrong numeric offset can compile cleanly while directing a register helper at the wrong MMIO word or indexed codec verb.
- `_BASE_IDX` mistakes are high impact because the same offset value can refer to a different aperture or alias depending on the selected base. This chunk mixes base index `2` display registers, base index `0` HDA registers, and base index `1` aliases.
- The chunk crosses unrelated hardware domains. HPO DP, HDA/Azalia, VGA, codec endpoint, CRC, and latency-counter definitions sit next to each other; bulk regeneration or manual edits can accidentally move, rename, or duplicate macros across domains.
- Indexed-register definitions are easy to misuse. `ix*` values are not normal MMIO offsets; consumers must write the correct index register and then read/write the paired data register, often with endpoint/node context already selected.
- Repeated endpoint and stream blocks invite copy/paste or generator-template errors. Output endpoints 0-7, input endpoints 0-7, streams 0-15, and CRC channel 0-7 definitions should remain identical except for instance prefixes and expected base/index offsets.
- Audio stream descriptor aliases share names and addresses with primary descriptor state. Incorrect alias handling could break position reporting, latency accounting, or interrupt/debug reads.
- DP DPHY SAT/VC and test-pattern registers affect link bring-up and compliance testing. Wrong offsets can manifest as training failures, bad MST payload allocation, failed PRBS/custom pattern tests, or incorrect CRC/error reporting.
- Legacy VGA indexes are retained for compatibility. Accidentally treating them as DCN MMIO registers would target invalid or unrelated hardware state.

## Test Signals

Useful validation signals are mostly build, generated-header consistency, and hardware integration signals:

- Build coverage: DCN 3.2.1 display code compiles with no missing `reg*`, `ix*`, `_BASE_IDX`, or shift/mask companion macros.
- Register-table sanity: `dcn321_resource.c` can instantiate its audio, stream encoder, link encoder, and hub/resource register tables using the generated offsets from this file.
- HPO DP behavior: displays using DP 2.x/HPO paths train reliably, program MSA and secondary data packets correctly, update SAT/VC allocation without timeout, and pass test-pattern/CRC diagnostics.
- Audio behavior: HDMI/DP audio endpoints enumerate expected capabilities, program stream formats and channel allocation, maintain correct LPIB/position reporting, and handle hotplug/format-change/enable-disable status.
- Indexed access behavior: Azalia endpoint/root/input endpoint reads return expected codec parameters through index/data registers rather than invalid MMIO reads.
- Suspend/resume and power transitions: audio streams, DP link encoders, DPHY state, aliases, and memory-power controls recover after suspend, display blank/unblank, GPU reset, and hotplug.
- Cross-generation regression checks: repeated stream, endpoint, input endpoint, VGA, and codec indexes remain consistent with adjacent DCN/DCE generated headers unless hardware-specific deltas are intentional.
- Static generation checks: every direct `reg*` macro that should have a `_BASE_IDX` companion has one, repeated instance blocks preserve expected address spacing, and the header terminates cleanly with the final `#endif`.
