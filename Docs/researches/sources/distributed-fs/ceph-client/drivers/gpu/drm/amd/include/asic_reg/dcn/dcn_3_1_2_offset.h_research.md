# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001796`: lines 1-2662, `Docs/researches/chunks/subset-b-001796_research.md`
- `subset-b-001797`: lines 2663-5185, `Docs/researches/chunks/subset-b-001797_research.md`
- `subset-b-001798`: lines 5186-7670, `Docs/researches/chunks/subset-b-001798_research.md`
- `subset-b-001799`: lines 7671-10248, `Docs/researches/chunks/subset-b-001799_research.md`
- `subset-b-001800`: lines 10249-12816, `Docs/researches/chunks/subset-b-001800_research.md`
- `subset-b-001801`: lines 12817-15089, `Docs/researches/chunks/subset-b-001801_research.md`

## Chunk Research

### subset-b-001796: lines 1-2662

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h lines 1-2662

## Scope

This chunk is the opening slice of the generated AMD DCN 3.1.2 register offset header. It covers lines 1-2662 and exports 2,355 preprocessor definitions: 1,178 `reg*` register-offset macros and 1,177 matching `reg*_BASE_IDX` macros. There are no C functions, structs, enums, storage objects, or executable statements in this range.

The chunk starts at the file copyright/header guard and ends inside the `HUBPREQ0` register family at `regHUBPREQ0_VBLANK_PARAMETERS_0`. Whole-file reconciliation should merge this with later chunks to cover the rest of HUBP/HUBPREQ instances, display pipe blocks, stream encoders, timing generators, and the header guard close.

## Purpose

The file gives DCN 3.1.2 display code symbolic names for memory-mapped ASIC register offsets and their SOC15 base segment indexes. Runtime code combines `regFOO_BASE_IDX` with `DCN_BASE__INST0_SEG<idx>` and `regFOO` to form absolute register addresses, usually through helper macros such as `SR`, `SRI`, `REG_OFFSET_EXP`, `RREG32_SOC15`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Major hardware areas represented in this chunk are:

- Azalia/HD-audio controller decode registers, endpoint immediate-command windows, function-0 controller/root/stream/endpoint/input-endpoint blocks, audio DTO/control registers, codec-pin mapping registers, and audio performance-monitor registers.
- Legacy VGA and VGA memory-interface registers, including indexed CRTC/SEQ/ATTR/GRPH/DAC compatibility windows, VGA render/control/status registers, and VGA source selection.
- Display clock generation and clock-gating registers in DCCG, including DISPCLK dentist control, PHYPLL pixel-clock resync, DP DTO phase/modulo, stream clock, symbol clocks, DPPCLK/DSCCLK DTOs, GTC timing, soft reset, and two DCCG perfmon blocks.
- DMU/DMCU/DMCUB control registers, including interrupt status/masking/routing, SMU interrupt controls, power-gating domains, RBBMIF status/timeout, DMCUB memory-region aperture registers, scratch/inbox/outbox/GPINT registers, and DMU perfmon registers.
- Display writeback (`DWB`) top, capture, cursor, warmup, output gamma, and writeback perfmon registers for writeback instance 0.
- MMHUBBUB and MCIF writeback registers for writeback buffer management, buffer addresses/high addresses, arbitration, watermarks, warmup, memory power, clocking, reset, error status, and MMHUBBUB perfmon.
- DCHUBBUB request-arbitration, watermark, VM aperture/context, return-path DCC, SDPIF, timeout, global timer, and perfmon registers.
- The beginning of HUBP0/HUBPREQ0 surface fetch programming: surface format/tiling/viewports, request-size, HUBP control/clock, VM page config, debug, surface pitch, primary/secondary luma/chroma addresses, meta addresses, flip control, in-use/earliest-in-use readback, TTU/QoS, VM aperture, destination dimensions, prefetch settings, and the first vblank-parameter register.

## Important API Surface

The only API exported by this chunk is the generated macro namespace:

- `reg<REGISTER>` gives the register's offset value within the hardware address space used by the AMDGPU SOC15 helpers.
- `reg<REGISTER>_BASE_IDX` selects the `DCN_BASE__INST0_SEG*` base segment that must be added by the consumer.

Important register families in this slice include:

- `regAZCONTROLLER0_*`, `regAZCONTROLLER1_*`, `regAZENDPOINT*`, and `regAZINPUTENDPOINT*` for HDA CORB/RIRB rings, immediate command/response windows, DMA position buffers, wall-clock counters, global status/control, interrupts, and endpoint command windows.
- `regDENTIST_DISPCLK_CNTL`, `regDCCG_*`, `regDP_DTO*`, `regDPPCLK*_DTO_PARAM`, `regDSCCLK*_DTO_PARAM`, `regSYMCLK*`, `regOTG*_PIXEL_RATE_CNTL`, and `regDCCG_PERFMON*` for display clock programming and diagnostics.
- `regDMCU_*`, `regDMCUB_*`, `regRBBMIF_*`, `regDOMAIN*_PG_*`, `regDC_GPU_TIMER_*`, `regDISP_INTERRUPT_STATUS*`, and `reg*_INTERRUPT_DEST*` for firmware-controller control, display interrupt fanout, GPU timer latching, power domains, security/RBBM interface, and mailbox/status handling.
- `regDWB_*` and `regDC_PERFMON3_*` for writeback enablement, capture dimensions, scaling/CSC/gamut/output-gamma programming, cursor metadata, memory power, warmup, and writeback performance counters.
- `regVGA_*`, `regD1VGA_CONTROL` through `regD6VGA_CONTROL`, `regMCIF_*`, `regMCIF_WB_*`, `regMMHUBBUB_*`, and `regWBIF0_*` for legacy VGA scanout detection and memory-interface/writeback-buffer plumbing.
- `regDCHUBBUB_ARB_*`, `regDCHUBBUB_SDPIF_*`, `regDCN_VM_*`, `regDCHUBBUB_RET_PATH_DCC*`, `regDCHUBBUB_TIMEOUT_*`, and `regDC_PERFMON6_*` for display hub memory arbitration, self-refresh/DRAM-clock-change watermarks, VM address translation/fault reporting, DCC return path configuration, and hub performance counters.
- `regHUBP0_*` and `regHUBPREQ0_*` for the first plane's surface fetch configuration, surface addresses, flip state, TTU/QoS, VM, prefetch, and viewport metadata. `amdgpu/gmc_v11_0.c` directly reads `regHUBP0_DCSURF_PRI_VIEWPORT_DIMENSION` and `regHUBPREQ0_DCSURF_SURFACE_PITCH` when estimating VBIOS framebuffer size.

## Control Flow

There is no local control flow in this header. The control flow is generated by consumers that paste register names into helper macros:

- `display/dc/resource/dcn31/dcn31_resource.c` includes this file and defines `SR`, `SRI`, and related macros that compute register addresses from `BASE(reg..._BASE_IDX) + reg...`. Those computed addresses populate DCN 3.1 resource tables for DCCG, HUBBUB, HUBP, DWB, MMHUBBUB, audio, AUX/I2C, DMUB, and IRQ-facing blocks.
- `display/dmub/src/dmub_dcn31.c` includes this file and uses `REG_OFFSET_EXP(reg)` to initialize `dmub_srv_dcn31_regs`, then programs DMCUB reset, GPINT, scratch, mailbox, framebuffer-base, and VM registers through DMUB register helpers.
- `display/dc/irq/dcn31/irq_service_dcn31.c` includes the offset and shift/mask headers to map DCN interrupt source IDs and to build IRQ register descriptors for vblank, vline, page flip, DMUB outbox, HPD, AUX, and related display interrupt paths.
- `amdgpu/gmc_v11_0.c` uses the generated offsets through `RREG32_SOC15(DCE, 0, reg...)` and combines them with shift/mask fields to derive an active framebuffer size when VGA is not using the fixed legacy allocation.

Typical runtime ordering is imposed by the higher-level display code: clock and reset registers are initialized before dependent blocks, DMCUB region/mailbox registers are configured before firmware service traffic, HUBBUB watermarks and VM apertures are set before plane fetch, HUBP/HUBPREQ surface addresses and flip controls are programmed around vertical update timing, and audio/HDMI/DP stream audio state is programmed after stream resources are known.

## State and Persistence

The header itself stores no software state. The named offsets map to hardware state that persists in display IP while the corresponding block remains powered:

- DCCG and DENTIST registers hold live display clock, DTO, gating, reset, and timing state. Bad offsets can produce wrong pixel rates, disabled clocks, or unstable clock transitions.
- DMU/DMCUB/DMCU registers hold firmware boot/control state, mailbox state, scratch values, interrupt masks/destinations, power-domain state, and security/RBBM interface state. These values survive until reset, firmware restart, power transition, or explicit reprogramming.
- HUBBUB/HUBP/HUBPREQ registers hold live scanout memory-fetch state: VM apertures and context page-table roots, surface and meta-surface addresses, pitches, viewport/destination geometry, QoS/TTU timing, watermarks, DCC return-path configuration, and flip/in-use readback.
- DWB and MCIF_WB registers hold writeback capture configuration, buffer addresses, buffer manager status, output gamma RAM selectors/data windows, CSC/gamut settings, cursor settings, and clock/self-refresh controls.
- Azalia registers hold command ring positions, stream endpoint settings, audio DMA state, DTO state, codec endpoint index/data windows, and interrupt/status state.
- Perfmon and interrupt-status registers expose live or sticky measurement/status state; some are clear-on-write or acknowledge paths in their matching shift/mask definitions.

Because this is address metadata, an incorrect macro often causes software to read or write a different persistent hardware register rather than failing at compile time.

## Dependencies and Integration Points

This offset header depends on the matching generated DCN 3.1.2 shift/mask header, `dcn_3_1_2_sh_mask.h`, for field positions and masks. Most consumers also include ASIC base headers such as `yellow_carp_offset.h`, where the SOC-specific base segment constants are defined.

Direct integration points visible in this tree include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which binds DCN 3.1 hardware blocks to register tables by expanding these offset macros.
- `drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`, which uses the same generated register metadata for interrupt source registration and control.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`, which builds the DMUB DCN31 register table and uses visible chunk registers such as `DCN_VM_FB_LOCATION_BASE`, `DCN_VM_FB_OFFSET`, and DMCUB control/mailbox registers.
- `drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`, which directly uses `regD1VGA_CONTROL`, `regHUBP0_DCSURF_PRI_VIEWPORT_DIMENSION`, and `regHUBPREQ0_DCSURF_SURFACE_PITCH` to size the firmware-reserved framebuffer aperture.
- Adjacent generated offset headers for related ASIC revisions (`dcn_3_1_5_offset.h`, `dcn_3_2_0_offset.h`, `dcn_3_2_1_offset.h`, `dcn_3_5_0_offset.h`, `dcn_4_1_0_offset.h`, and `dcn_4_2_0_offset.h`) provide comparison points; many names repeat while some offsets drift by generation.

Functional consumers beyond the direct includes are the DCN31 hubbub, HUBP, DCCG, DWB, MMHUBBUB, audio, IRQ, DMUB, and resource-construction code reached through those register tables.

## Risks

- Offset/base-index mismatches are high impact because helper macros silently compute a valid but wrong MMIO address. A bad `BASE_IDX` can target the wrong SOC15 segment even when the offset value looks correct.
- Hardware-generation drift is easy to miss. DCN 3.1.2 offsets overlap heavily with nearby DCN 3.1.5, 3.2.x, 3.5, and 4.x headers, but visible comparison points show differences in DCHUBBUB watermarks and later HUBP layout. Copying between generations can create board-specific failures.
- DMCUB region, mailbox, GPINT, and interrupt-control offsets are boot-critical. Incorrect values can prevent display firmware reset/startup, lose mailbox messages, or wedge interrupt handling.
- HUBBUB and HUBPREQ VM/address registers affect scanout memory access. Wrong offsets can read or program bad framebuffer/meta addresses, page-table contexts, VM apertures, or fault controls, with symptoms ranging from blank scanout to memory faults.
- Watermark, TTU, QoS, and DRAM-clock-change registers are timing-sensitive. Address errors can appear only under bandwidth stress, flips, low-power entry/exit, or multiple display streams.
- DWB/MCIF_WB buffer address and gamma/CSC registers affect writeback correctness. Mistakes can corrupt captured frames, route writes to wrong buffers, or create color-output mismatches.
- VGA and VBIOS framebuffer-size probing relies on a small set of offsets in this chunk. Wrong values can make the driver reserve too little or too much stolen/firmware framebuffer memory.
- Perfmon and interrupt registers often combine status, mask, clear, destination, and counter-state semantics. Offsets that cross those roles can drop sticky events, clear the wrong source, or produce misleading diagnostics.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build AMDGPU with DCN31/Yellow Carp display enabled to catch renamed or missing `reg*` and `reg*_BASE_IDX` symbols in resource, IRQ, DMUB, GMC, DCCG, HUBP, HUBBUB, DWB, MMHUBBUB, and audio paths.
- Static generated-header validation against the vendor register database: every `regFOO` should have one matching `regFOO_BASE_IDX`, and offsets should match the corresponding DCN 3.1.2 base block.
- Cross-generation diff checks against nearby DCN offset headers to identify intentional versus accidental differences in repeated families such as DCHUBBUB, DMCUB, AZALIA, and HUBP0/HUBPREQ0.
- Display bring-up and modeset tests on DCN 3.1.2 hardware, covering clock programming, hotplug/AUX interrupts, vblank/vline/page-flip IRQs, DMUB firmware reset/mailbox traffic, audio stream enablement, and multi-monitor operation.
- Plane scanout tests that exercise HUBP0/HUBPREQ0 with linear and tiled surfaces, stereo/secondary addresses, meta surfaces, flips, VM contexts, prefetch, QoS/TTU, and cursor interactions.
- Suspend/resume, runtime power-management, and display idle tests that verify DCCG, DMCUB, MMHUBBUB, DCHUBBUB, MCIF_WB, and Azalia state is restored correctly after power and clock transitions.
- Writeback validation that captures frames through DWB0 and checks buffer manager state, output gamma/CSC/gamut programming, memory power, and writeback perfmon counters.
- Fault-injection or stress tests for VM fault status, DCHUBBUB timeout detection, RBBMIF timeouts, DMCUB interrupt ack/status, and perfmon readback.

## Chunk Notes

This is generated register metadata rather than hand-written logic. The main research value is mapping the register surfaces covered by this early DCN 3.1.2 slice: display clocks, firmware/DMUB control, interrupts, audio, VGA, writeback, hub memory arbitration/VM, and the beginning of HUBP0 fetch programming. The final merged file report should connect this slice with later chunks to describe complete per-instance register families and the closing include guard.

### subset-b-001797: lines 2663-5185

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h lines 2663-5185

## Scope

This chunk covers 2,523 lines from the generated AMD DCN 3.1.2 register-offset header. The slice contains only preprocessor constants and generated address-block comments; there are no C functions, structs, enums, variables, or executable statements.

The range begins in the tail of the `dce_dc_dcbubp0_dispdec_hubpreq_dispdec` block at `regHUBPREQ0_VBLANK_PARAMETERS_1` and ends in the early part of the `dce_dc_dpp2_dispdec_dscl_dispdec` block at `regDSCL2_SCL_BLACK_COLOR`. Adjacent chunks are required to complete both the start-side `HUBPREQ0` register group and the end-side `DSCL2`/following DPP2 color-management blocks.

Within this range there are 1,196 non-`BASE_IDX` register-offset macros plus paired `*_BASE_IDX` macros. The lowest offset in the chunk is `0x064b` for `regHUBPREQ0_VBLANK_PARAMETERS_1`; the highest is `0x0fe0` for `regDSCL2_SCL_BLACK_COLOR`. Every address in this chunk uses DCN base segment index `2` after the initial file-level `BASE(reg..._BASE_IDX)` expansion.

## Purpose

This header region provides the DCN 3.1.2 symbolic MMIO offset contract for display pipe front-end and pixel-processing hardware. AMD display code includes this file with the matching `dcn_3_1_2_sh_mask.h` field header so register-table macros can resolve hardware addresses by token concatenation rather than by raw numeric constants.

The chunk maps three broad areas:

- HUBP/HUBPREQ/HUBPRET/CURSOR registers for plane pipes 0 through 3, including viewport, request-size, VMID, surface address, flip timing, prefetch, vblank/nominal delivery, cursor, metadata, line-read, memory power, and perf counter registers.
- DPP pipe registers for DPP0 and DPP1, including converter/cursor (`CNVC_CFG`, `CNVC_CUR`), scaler (`DSCL`), color-management (`CM`), DPP top, CRC, and per-DPP perfmon registers.
- The beginning of DPP2, covering `CNVC_CFG2`, `CNVC_CUR2`, and the first part of `DSCL2`.

This is a hardware description input to the driver. Its value is exact macro names and numeric offsets, not local algorithmic behavior.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro naming convention:

- `reg<block><instance>_<REGISTER>` gives the register offset relative to the selected DCN base segment.
- `reg<block><instance>_<REGISTER>_BASE_IDX` gives the base-index selector used by `BASE(...)` or equivalent macros in AMD display code.
- Address-block comments identify the generated hardware block and the block-local base address used by the register generator.

The most important register families in this range are:

- `regHUBPREQ0_*`, starting at `VBLANK_PARAMETERS_1`, `FLIP_PARAMETERS_*`, `NOM_PARAMETERS_*`, `PER_LINE_DELIVERY*`, `CURSOR_SETTINGS`, `REF_FREQ_TO_PIX_FREQ`, `DST_Y_DELTA_DRQ_LIMIT`, and HUBPREQ memory power registers. The earlier part of `HUBPREQ0` is outside this chunk.
- Complete `HUBP1`, `HUBP2`, and `HUBP3` front-end blocks for surface config, address/tiling config, primary/secondary viewport starts and dimensions, request-size config, clock control, VMPG config, debug registers, and measurement-window controls.
- Complete `HUBPREQ1`, `HUBPREQ2`, and `HUBPREQ3` blocks for surface pitch, VMID, primary/secondary luma and chroma surface addresses, metadata addresses, surface-in-use/earliest-in-use tracking, flip control, DCC/TMZ surface control, QoS, TTU, prefetch, vblank, flip, nominal, delivery, cursor settings, VM aperture, TLB, and memory power registers.
- `HUBPRET0` through `HUBPRET3` line-buffer/control blocks, including control, memory power, read-line controls, read-line values/status, and interrupt registers.
- `CURSOR0_0` through `CURSOR0_3` cursor blocks, including cursor control, surface address high/low, size, position, hot spot, stereo control, destination offset, cursor memory power, and display metadata data/address/QoS/status/software-control registers.
- `DC_PERFMON7` through `DC_PERFMON10` associated with the HUBP side, plus `DC_PERFMON11` and `DC_PERFMON12` associated with DPP0 and DPP1. Each perfmon block exposes counter control, counter state, perfmon control, current-value, high, and low registers.
- `CNVC_CFG0`, `CNVC_CFG1`, and `CNVC_CFG2`, covering surface pixel format, format control, floating-point bias/scale channels, color-keyer control and values, alpha 2-bit LUT, pre-dealpha, pre-CSC mode and coefficients, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0`, `CNVC_CUR1`, and `CNVC_CUR2`, covering cursor control, cursor colors, and cursor floating-point scale/bias.
- `DSCL0` and `DSCL1` complete scaler blocks, plus the first part of `DSCL2`, covering coefficient RAM access, scaler mode, tap control, DSCL control, 2-tap control, manual replicate control, horizontal/vertical luma/chroma scale ratios and initial phases, black color, update/autocal, overscan, OTG blanking, recout/MPC sizes, line-buffer format/memory, DSCL/OBUF memory power, and output-buffer control.
- `CM0` and `CM1` complete color-management blocks, including dealpha, memory power/status, bias, gamma correction control/LUT, gamut remap A/B matrices, post-CSC A/B matrices, degamma/blend-gamma/shaper RAM A/B start/slope/end/base/region registers, LUT index/data/control registers, HDR multiplier coefficient, 3D LUT control/data/offset registers, and debug index/data registers.
- `DPP_TOP0` and `DPP_TOP1`, covering DPP control, soft reset, CRC values/control, and host-read control.

## Control Flow

The chunk has no runtime control flow. Its effective flow is compile-time macro expansion:

1. DCN 3.1 display code includes `yellow_carp_offset.h`, `dcn/dcn_3_1_2_offset.h`, and `dcn/dcn_3_1_2_sh_mask.h`.
2. Consumer macros such as `SR`, `SRI`, `SRIR`, and `SRII` concatenate a block name, instance id, and register name to select one of the `reg...` macros from this header.
3. The same expression adds `BASE(reg..._BASE_IDX)` to the selected offset to produce an absolute register address stored in generated register tables.
4. Runtime paths use those tables through register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Concrete consumers include `display/dc/resource/dcn31/dcn31_resource.c`, which builds the `hubp_regs[]`, DPP register lists, HWSEQ registers, shifts, and masks for Yellow Carp/DCN 3.1 resources; `display/dc/irq/dcn31/irq_service_dcn31.c`, which includes the same offset/mask headers for IRQ register-table expansion; and `display/dmub/src/dmub_dcn31.c`, which uses the same include pair for DMUB register and field tables. The HUBP-specific field lists in `display/dc/hubp/dcn31/dcn31_hubp.h` and DPP lists in `display/dc/dpp/dcn30/dcn30_dpp.h` show the token names that must match these generated offsets.

## State And Persistence Behavior

The header itself stores no state and performs no persistence. It describes MMIO registers whose state is owned by DCN 3.1.2 display hardware.

The mapped HUBP/HUBPREQ/HUBPRET registers control or report plane-fetch state: surface addresses, metadata addresses, VMID selection, memory aperture/TLB behavior, request chunking, swath/viewport dimensions, flip and vblank timing, TTU/QoS behavior, prefetch timing, DCC/TMZ control, cursor fetch state, line-read state, underflow/blanking behavior, and per-block memory power. These values are normally programmed by the DC resource and hardware-sequencer paths during plane enable, flip, cursor update, bandwidth/programming updates, power transitions, and reset/recovery.

The mapped DPP/CNVC/DSCL/CM registers control or report per-pipe pixel processing: input format conversion, cursor color conversion, scaler taps and filter coefficients, viewport/output sizing, overscan and blanking, line-buffer state, color-space matrices, degamma/gamma/blend/shaper LUT RAMs, HDR multiplier, 3D LUT state, CRC, top-level DPP reset/control, and DPP-side perf counters. Writable settings persist according to hardware reset and power-gating behavior, while status/perf/readback registers can change asynchronously as scanout and processing progress.

Because this file only provides offsets, it does not encode register access permissions, volatile behavior, write-one-to-clear semantics, update-lock sequencing, or safe programming order. Those rules live in the display driver logic and the hardware programming model.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.1.2 register family staying synchronized:

- `dcn_3_1_2_sh_mask.h` must define matching field shifts and masks for the register names used by `REG_GET`, `REG_SET`, `FD_MASK`, and `FD_SHIFT`.
- `yellow_carp_offset.h` supplies the base-segment macros such as `DCN_BASE__INST0_SEG2` that turn each `*_BASE_IDX` into an absolute MMIO base.
- `reg_helper.h` and local macros in `dcn31_resource.c`, `irq_service_dcn31.c`, and `dmub_dcn31.c` depend on the exact `reg...` and `reg..._BASE_IDX` token spellings.
- HUBP register setup in `dcn31_resource.c` uses `HUBP_REG_LIST_DCN30(id)` for instances 0-3. The slice provides most of the instance-specific `HUBP*`, `HUBPREQ*`, `HUBPRET*`, and `CURSOR0_*` offsets needed by those tables.
- DPP register setup uses `DPP_REG_LIST_DCN30(id)`, which expects `CNVC_CFG*`, `CNVC_CUR*`, `DSCL*`, `CM*`, and `DPP_TOP*` offsets. This chunk contains complete DPP0/DPP1 coverage for those prefixes and partial DPP2 coverage.
- Higher-level display subsystems integrate through hardware object constructors such as HUBP and DPP construction paths, plane programming, cursor programming, color pipeline programming, scaler programming, perf counter/debug paths, IRQ handling, DMUB setup, and HWSEQ CRC/readback logic.

The integration contract is primarily compile-time. Missing or renamed macros fail during compilation when token concatenation cannot resolve a register name. Incorrect numeric offsets are more dangerous because they can compile cleanly while programming or reading the wrong MMIO register.

## Risks And Edge Cases

- The range starts mid-`HUBPREQ0` and ends mid-`DSCL2`; whole-file analysis must merge adjacent chunks before claiming full coverage for those blocks.
- The file is generated and highly repetitive. A one-instance offset drift, especially among `HUBPREQ1/2/3`, `CURSOR0_1/2/3`, or `CM0/CM1`, can be hard to catch by visual review.
- `SRI`-style token concatenation is sensitive to prefix conventions such as `CURSOR0_` versus `CURSOR`, `CNVC_CFG`, `CNVC_CUR`, `DPP_TOP`, and `DC_PERFMON`. A local rename or generation change can break consumers even if the hardware address is unchanged.
- Many registers in this range drive live scanout timing and memory fetch behavior. Bad offsets for `VBLANK_PARAMETERS_*`, `FLIP_PARAMETERS_*`, `PREFETCH_SETTINGS*`, `NOM_PARAMETERS_*`, `PER_LINE_DELIVERY*`, request-size config, or TTU/QoS registers can produce underflow, missed flips, visible corruption, or hangs under bandwidth pressure.
- Surface, metadata, VM aperture, VMID, DCC, and TMZ registers have security and memory-isolation implications. An offset mismatch can direct a pipe to stale memory, an incorrect VMID, or incorrectly protected surfaces.
- Cursor and DMDATA registers combine visible cursor state with metadata fetch/control state. Wrong offsets can leave cursors invisible, corrupt, stale after flips, or can break metadata delivery.
- DSCL coefficient RAM and CM LUT/RAM accesses are index/data style programming surfaces. Incorrect offsets or missing update sequencing can corrupt color/scaler tables without obvious compile-time symptoms.
- Memory power control/status registers appear for HUBPREQ, HUBPRET, cursor, DSCL/OBUF, and CM. Power-gating interactions require correct polling and sequencing; this header does not identify status-vs-control behavior.
- DPP0/DPP1 have full color-management blocks in this chunk, but DPP2 is partial. Tests or audits focused only on this chunk should not infer that DPP2 color, memory power, and top/perfmon definitions are absent from the whole file.

## Test Signals

Useful validation signals are build-time, generated-header consistency, and hardware behavior oriented:

- Compile AMDGPU display code for the DCN 3.1/Yellow Carp configuration to catch unresolved `reg...` and `reg..._BASE_IDX` tokens in HUBP, DPP, DMUB, HWSEQ, and IRQ register tables.
- Preprocess `dcn31_resource.c`, `dmub_dcn31.c`, and `irq_service_dcn31.c` to confirm `SRI`/`SR` expansions resolve to expected `BASE(2) + offset` expressions for representative `HUBPREQ`, `HUBP`, `CURSOR0_`, `CNVC_CFG`, `DSCL`, `CM`, and `DPP_TOP` registers.
- Compare this header against the matching AMD register database or generated sibling headers to ensure every `reg...` in this range has a paired `*_BASE_IDX` and matching shift/mask definitions where the driver uses field helpers.
- Exercise plane enable/disable, page flip, vblank, cursor update, DCC/TMZ surfaces, VM fault/underflow recovery, and suspend/resume on DCN 3.1.2 hardware while watching HUBP underflow, flip-pending, no-outstanding-request, VM fault, and memory power status behavior.
- Validate scaler paths with no scaling, luma/chroma scaling, 4:2:0, fractional ratios, coefficient programming, overscan, and recout/MPC sizing to cover `DSCL*` offsets.
- Validate color-management paths including degamma, gamma correction, gamut remap, post-CSC, HDR multiplier, shaper/blend gamma, and 3D LUT programming to cover `CM0`/`CM1` and the DPP2 definitions completed in adjacent chunks.
- Use CRC and perfmon debug paths to confirm `DPP_TOP*_DPP_CRC_*` and `DC_PERFMON*` offsets read sensible values and do not alias unrelated blocks.
- Include multi-pipe tests that activate pipe instances 0 through 3, because many defects in this header would only appear when programming nonzero instances.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to describe the complete `HUBPREQ0` block, including the surface, VM, TTU, and first vblank parameter registers before line 2663.
- The merge lane should combine this with the next chunk to complete `DSCL2`, `CM2`, DPP2 top/perfmon, and any subsequent DPP instances present in the whole DCN 3.1.2 offset file.
- Whole-file reconciliation should verify the expected number of HUBP/DPP pipe instances for this ASIC and check whether later instances are present, intentionally omitted, or handled by other generated files.

### subset-b-001798: lines 5186-7670

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h lines 5186-7670

## Purpose

This chunk is generated register-address metadata for the AMD DCN 3.1.2 display engine. It contains C preprocessor `#define`s that map symbolic DCN display-block register names to MMIO offsets plus matching `*_BASE_IDX` segment selectors. The driver combines each register offset with `DCN_BASE__INST0_SEG<idx>` through register-list macros such as `SR`, `SRI`, `SRII`, and `SRII_MPC_RMU` in the DCN31 resource code.

The covered range starts in the tail of the DPP2 scaler (`DSCL2`) block, then defines most of DPP2 color-management (`CM2`), DPP3 converter/scaler/color-management/top/perfmon blocks, and a large part of the MPC composition pipeline: MPCC0-3 blending controls, MPC global configuration, MPC perfmon, per-MPCC output-gamma/gamut blocks, output mux/output CSC blocks, and the start of the RMU 3D-LUT block. It has no executable code, functions, structs, or algorithms. Its importance is that every macro is part of the hardware programming ABI for Yellow Carp/DCN 3.1.2 display support.

## Important APIs, Types, And Register Groups

- The chunk contains 2401 `#define`s. Each hardware register normally has a pair: `reg<NAME>` gives the register offset and `reg<NAME>_BASE_IDX` selects the DCN base segment used to form the final MMIO address.
- The opening lines are a chunk-boundary continuation of `dce_dc_dpp2_dispdec_dscl_dispdec`. They include `regDSCL2_SCL_BLACK_COLOR_BASE_IDX` and the remaining DPP2 scaler/window/output-buffer registers: `DSCL_UPDATE`, `DSCL_AUTOCAL`, overscan, OTG blanking, recout/MPC sizing, line-buffer format/memory control/status, scaler memory power control/status, and output-buffer control/power.
- `dce_dc_dpp2_dispdec_cm_dispdec` (`regCM2_*`, base address `0xb58`) defines DPP2 color-management registers. It covers CM bypass/update control, post-CSC matrix pairs and B-bank matrix pairs, gamut-remap matrix pairs and B-bank pairs, output bias, gamma-correction control, LUT index/data/control, RAMA/RAMB start/slope/base/end/offset controls, many RAMA/RAMB region tables, decompression and RGB-to-YUV style conversion tables, alpha/color-key related controls, and test/debug registers.
- `dce_dc_dpp2_dispdec_dpp_top_dispdec` (`regDPP_TOP2_*`, base `0xb58`) defines DPP2 top-level controls: DPP control, clock control, SRAM clock gating, DPP_CONTROL2, CRC control/readback, and host-read control.
- `dce_dc_dpp2_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` (`regDC_PERFMON13_*`, base `0x43e8`) defines the DPP2 perfmon counter control, counter state, interrupt/status, and high/low readback offsets.
- `dce_dc_dpp3_dispdec_cnvc_cfg_dispdec` (`regCNVC_CFG3_*`, base `0x1104`) defines DPP3 converter-format configuration: surface pixel format, format control, alpha/2-bit-alpha LUT, expansion, keying, de-alpha, pre-CSC mode and coefficient pairs including B-bank coefficients, coefficient-format control, pre-degamma, and pre-realpha.
- `dce_dc_dpp3_dispdec_cnvc_cur_dispdec` (`regCNVC_CUR3_*`, base `0x1104`) defines DPP3 converter-side cursor controls: cursor enable/mode/control, cursor color registers, and cursor floating-point scale/bias.
- `dce_dc_dpp3_dispdec_dscl_dispdec` (`regDSCL3_*`, base `0x1104`) mirrors the DPP scaler block for pipe 3. It includes coefficient RAM selection/data, scaler and tap controls, sharpness, manual replicate factors, horizontal/vertical scale ratios and initial phases for luma/chroma/top/bottom, black color, update/autocal, overscan, OTG blanking, recout/MPC sizing, line-buffer state, scaler memory power, and OBUF state.
- `dce_dc_dpp3_dispdec_cm_dispdec` (`regCM3_*`, base `0x1104`) mirrors the DPP color-management set for pipe 3. Its register families match `CM2`: post-CSC, gamut-remap, bias, gamma LUT access, RAMA/RAMB piecewise regions, decompression/color-space conversion controls, and test/debug.
- `dce_dc_dpp3_dispdec_dpp_top_dispdec` (`regDPP_TOP3_*`, base `0x1104`) and `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` (`regDC_PERFMON14_*`, base `0x4994`) provide DPP3 top-level and perfmon offsets.
- `dce_dc_mpc_mpcc0_dispdec` through `dce_dc_mpc_mpcc3_dispdec` (`regMPCC0_*` ... `regMPCC3_*`, bases `0x0`, `0x80`, `0x100`, and `0x180`) define four MPCC blending/composition slices. Each slice has top/bottom selection, control, alpha, multiplied-alpha, background color, pre-multiplied alpha, output size, status/control, debug, line-buffer control, denorm, mux selection, mux status, and status registers.
- `dce_dc_mpc_mpc_cfg_dispdec` (`regMPC_*`, base `0x0`) defines global MPC controls: clock and memory power, output muxes, CRC control/results, gamut-remap memory power/status, debug-data mux/readback, ALU control, output-size programming, memory low-power/read-margin controls, and DWB muxing.
- `dce_dc_mpc_mpc_dcperfmon_dc_perfmon_dispdec` (`regDC_PERFMON15_*`, base `0x1901c`) defines the MPC perfmon control/status/readback registers.
- `dce_dc_mpc_mpcc_ogam0_dispdec` through `dce_dc_mpc_mpcc_ogam3_dispdec` (`regMPCC_OGAM0_*` ... `regMPCC_OGAM3_*`, bases `0x0`, `0x200`, `0x400`, and `0x600`) define per-MPCC output gamma and gamut-remap blocks. Each instance contains OGAM control, LUT index/data/control, RAMA/RAMB start/end/region registers, memory power control/status, B-state controls, and MPC gamut-remap matrix pairs for A/B banks.
- `dce_dc_mpc_mpc_ocsc_dispdec` (`regMPC_OUT*`, base `0x0`) defines four MPC output mux and output CSC groups. Each output has an `OUTn_MUX`, an `OUTn_CSC_MODE`, and A/B-bank CSC coefficient-pair registers for the 3x4 color matrix.
- `dce_dc_mpc_mpc_rmu_dispdec` (`regMPC_RMU*`, base `0x0`) begins the RMU global and RMU0 block. In this chunk it includes global RMU control and memory power, RMU0 shaper controls, shaper offsets/scales, shaper LUT index/data/write-enable mask, shaper RAMA/RAMB start/end/region tables, and the start of RMU0 3D-LUT programming through `MPC_RMU0_3DLUT_OUT_OFFSET_G_BASE_IDX`.

The public "API" surface here is purely macro-based. Callers do not invoke functions from this file; they include it alongside `dcn_3_1_2_sh_mask.h` so generated register-list macros can build address, shift, and mask tables for DC objects.

## Control Flow

There is no C control flow in this header. Runtime control flow occurs in the AMD display driver code that consumes these symbols:

1. DCN31 resource setup includes this offset header and the matching shift/mask header.
2. Register-list macros concatenate block names and instance IDs into symbols such as `regCM3_CM_CONTROL`, `regMPCC1_MPCC_CONTROL`, or `regMPC_RMU0_3DLUT_MODE`.
3. The macros calculate a final MMIO address as `BASE(reg..._BASE_IDX) + reg...`, where the base index maps to a DCN segment from the ASIC base-address header.
4. Hardware object constructors store those final addresses in typed register tables for DPP, MPC, MPCC, RMU, perfmon, DMUB, and IRQ/resource paths.
5. Runtime paths use register helpers to write configuration registers, poll status registers, or read debug/perf counters.

The hardware programming sequences implied by this chunk include DPP scaler setup before pipe enable, DPP post-CSC/gamut/gamma programming before color-managed output, MPCC top/bottom mux and alpha programming before MPC composition, output CSC programming before stream output, and RMU shaper/3D-LUT programming when advanced color blocks are enabled.

## State And Persistence Behavior

The macros are compile-time constants and do not store runtime state. The registers they name represent persistent device state until changed by MMIO writes, reset, power-gating transitions, suspend/resume, or display mode reprogramming.

Important hardware state represented in this range includes scaler ratios/phases/taps and coefficient RAM selection, line-buffer and OBUF memory state, color matrices and B-bank matrix state, gamma LUT indices/data/control, piecewise gamma region tables, DPP CRC/perfmon state, MPCC blend topology and alpha values, MPC output mux routing, MPC CRC results, MPC and RMU memory power controls/statuses, per-output CSC matrices, and RMU shaper/3D-LUT tables.

Many registers are not ordinary one-shot configuration. Names ending in `STATUS`, `READBACK`, `RESULT`, `DEBUG_DATA`, `PERFCOUNTER_*`, `UPDATE`, `LUT_DATA`, `LUT_INDEX`, or memory-power `STATUS` reflect readback, indexed state, counters, or asynchronous hardware state. The offset header does not encode read-only, write-one-to-clear, indexed-LUT, double-buffer, or power-state sequencing rules; those rules must come from the hardware spec and the corresponding driver logic.

## Dependencies And Integration Points

- `display/dc/resource/dcn31/dcn31_resource.c` includes `yellow_carp_offset.h`, this `dcn_3_1_2_offset.h`, and `dcn_3_1_2_sh_mask.h`. Its `SR`, `SRI`, `SRII`, `SRII_MPC_RMU`, and related macros are the main bridge from generated offsets to typed DC register tables.
- `display/dmub/src/dmub_dcn31.c` includes this header to build DMUB service register/field tables through `REG_OFFSET_EXP`, `DMUB_DCN31_REGS()`, and field-mask/shift helpers.
- `display/dc/irq/dcn31/irq_service_dcn31.c` includes this header with the shift/mask header so interrupt service code can use the correct DCN31 register map.
- The chunk's DPP2/DPP3 symbols integrate with DPP register-list macros such as `DPP_REG_LIST_DCN30` and the DPP color/scaler code that programs CNVC, DSCL, CM, top, CRC, and perfmon registers.
- The MPCC, MPC, OCSC, and RMU symbols integrate with MPC register-list macros such as `MPC_REG_LIST_DCN3_0`, `MPC_OUT_MUX_REG_LIST_DCN3_0`, `MPC_RMU_GLOBAL_REG_LIST_DCN3AG`, and `MPC_RMU_REG_LIST_DCN3AG`.
- The `*_BASE_IDX` values are as important as offsets. DPP2/DPP3 display-pipe registers use base index 2 in this chunk, while the MPC/MPCC/RMU registers use base index 3. A correct offset with the wrong base index would target the wrong MMIO segment.

This file also depends structurally on adjacent generated headers for the same ASIC family: the matching shift/mask header defines bit positions, and other offset chunks in this same file define earlier/later instances. Similar offset headers for DCN 3.1.4, 3.1.5, 3.1.6, 3.2.x, 3.5.x, and 4.x preserve many names but may differ in addresses or available blocks.

## Risks And Edge Cases

- This chunk starts in the middle of a generated register pair: it begins with `regDSCL2_SCL_BLACK_COLOR_BASE_IDX`, while the corresponding `regDSCL2_SCL_BLACK_COLOR` offset is in the previous chunk. The merge lane must reconcile this boundary before treating the DSCL2 group as complete.
- This chunk ends in the middle of the RMU0 block at `regMPC_RMU0_3DLUT_OUT_OFFSET_G_BASE_IDX`; later RMU0/RMU1 3D-LUT registers continue in the next chunk. Research consumers should not infer that only one RMU instance or only the visible 3D-LUT registers exist.
- The file is generated and highly repetitive. Copy-generation drift between DPP2 and DPP3, MPCC0-3, MPCC_OGAM0-3, or MPC_OUT0-3 can compile cleanly while routing MMIO writes to the wrong instance.
- Offset/base-index mistakes are high impact because the driver composes final addresses mechanically. A wrong `*_BASE_IDX` can move an otherwise plausible register offset into a different aperture.
- Indexed LUT registers such as gamma, shaper, and 3D-LUT index/data pairs require strict index/data ordering and bank selection. The offset constants cannot prevent stale indices, partial LUT programming, or writes to the wrong RAM bank.
- Double-buffered color matrices and B-bank registers must be synchronized with the hardware's update semantics. A valid address can still produce visual corruption if the caller flips banks or update controls at the wrong time.
- Memory power control registers appear for DSCL/OBUF, MPC gamut-remap memory, MPCC OGAM memory, and RMU memory. Callers must coordinate power state with active fetch/composition/LUT use; the offset header provides no readiness or polling policy.
- Output mux, MPCC topology, and output CSC programming are tightly coupled. Misrouting an MPCC or MPC output mux can produce blank output, swapped planes, or color conversion on the wrong output even when all individual register writes are valid.
- Perfmon and CRC/debug registers can be read or reset by diagnostic paths. Incorrect offsets may not be noticed in normal display operation but can break validation, telemetry, or automated bring-up diagnostics.

## Test Signals

- Build coverage: malformed or missing macros should break compilation in DCN31 resource, DMUB, IRQ, DPP, MPC, and register-list users.
- Generated-header validation: compare all offsets and base indices against the vendor register database for DCN 3.1.2, with special checks for duplicated instance families (`CM2`/`CM3`, `MPCC0-3`, `MPCC_OGAM0-3`, and `MPC_OUT0-3`).
- Modeset and plane-composition tests: multi-plane enable/disable, z-order changes, alpha blending, MPCC split/merge, MPC output mux routing, and multi-display output exercise the MPCC and MPC groups.
- Color-management tests: post-CSC, output CSC, gamut remap, gamma correction, OGAM, RMU shaper, and RMU 3D-LUT programming should be validated with known pixel-output patterns or CRC comparisons.
- Scaling tests: luma/chroma scaling, tap-count changes, overscan, recout size changes, line-buffer partition changes, and OBUF modes cover the DSCL2 tail and DSCL3 block.
- Power-management tests: display idle, memory low-power entry/exit, suspend/resume, and active-pipe power transitions should observe the DSCL, OBUF, MPC, OGAM, and RMU power-control/status registers.
- Debug/perf tests: DPP2/DPP3/MPC perfmon counters, DPP CRC, MPC CRC, debug-data muxes, and host-read control paths verify the diagnostic offsets that ordinary modeset tests may not touch.

### subset-b-001799: lines 7671-10248

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h lines 7671-10248

## Scope

This chunk is a generated AMD DCN 3.1.2 register-offset header slice. It contains no executable C logic, types, functions, storage objects, includes, allocation paths, or runtime branches. Its exported surface is 2,386 preprocessor definitions: 1,193 `reg...` register-offset macros and 1,193 paired `reg..._BASE_IDX` macros. The range spans 2,578 source lines and 48 generated `addressBlock` sections.

The chunk begins at the final `MPC_RMU0_3DLUT_OUT_OFFSET_B` offset pair, covers the full `MPC_RMU1` shaper/3DLUT offset group, four ABM/backlight instances, four OPP/DPG/FMT/OPPBUF/OPP pipe groups, ODM and OTG timing groups for instances 0-3, OPTC miscellaneous/perfmon registers, HPD instances 0-4, DP link instances 0-1, DIG/HDMI/TMDS instance 0, and most of DIG instance 1 through `DIG1_TMDS_CTL0_1_GEN_CNTL`. The next source line after this chunk continues `DIG1`.

Although the repository path includes `ceph-client`, this header is AMDGPU display-controller hardware metadata, not distributed filesystem code.

## Purpose

The purpose of this range is to map symbolic DCN 3.1.2 display register names to hardware offsets and base-index selectors. Runtime driver code should not hard-code these numeric offsets; it builds register tables from names such as `regOTG1_OTG_H_TOTAL` and `regDP0_DP_LINK_CNTL`, then combines each offset with its matching `reg..._BASE_IDX` through register helper macros.

The covered hardware areas are:

- MPC/RMU color-management registers for shaper LUT and 3D LUT programming.
- ABM/backlight registers for PWM levels, ambient/user/target/current brightness, adaptive brightness processing, ACE controls, luma/histogram sampling, grouped locks, and master locks.
- OPP output-pixel-processor blocks, including DPG, FMT, OPP buffer, pipe, pipe CRC, DSC rate-match, top-level OPP, and OPP perfmon registers.
- ODM and OTG/OPTC timing-generator blocks for display timing, vblank/vsync, vertical interrupts, update locks, CRC windows/results, stereo, trigger, global sync lock, DRR, DTO, DSC start position, and pipe-update status.
- HPD hotplug-detect registers for five physical connectors.
- DP and DIG encoder/link registers for DisplayPort link training, MSA/MST/MSO/DSC/secondary packets/audio, HDMI packets/audio clock regeneration, AFMT, TMDS, CRC, test patterns, and FIFO/status handling.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The API surface is the generated macro namespace:

- `regREGISTER`: register offset within a hardware register aperture.
- `regREGISTER_BASE_IDX`: base-address segment selector for that register.
- `// addressBlock: ...` and `// base address: ...`: generated grouping comments that document the owning hardware block and replicated instance base.

Important macro families in this chunk:

- `regMPC_RMU1_SHAPER_*` and `regMPC_RMU1_3DLUT_*`: shaper control, per-channel offsets/scales, LUT index/data/write-enable mask, RAM A/B start/end controls, 34 region pairs for each RAM bank, 3D LUT mode/index/data/30-bit data, read/write control, output normalization, and RGB output offsets. The chunk also includes the final offset pair for `MPC_RMU0_3DLUT_OUT_OFFSET_B`.
- `regABM[0-3]_*`: repeated ABM/backlight layout with BL1 PWM level/duty-cycle controls, `DC_ABM1_*` control/ACE/histogram/luma/statistics/sample-rate/readback registers, panel mask, backlight current/target/final fractional registers, and master lock.
- `regDPG[0-3]_*`, `regFMT[0-3]_*`, `regOPPBUF[0-3]_*`, `regOPP[0-3]_*`, and `regOPP_PIPE_CRC[0-3]_*`: per-OPP data-path, formatter, buffer, and CRC offsets used by OPP register-list macros.
- `regDSCRM[0-2]_*`, `regOPP_*`, `regDWB_*`, and `regDC_PERFMON17_*`: DSC rate-match memory-power state, OPP memory power/reset/top controls, DWB clock control, and OPP/OPTC performance-counter offsets.
- `regODM[0-3]_*` and `regOTG[0-3]_*`: output data merger memory power/control and full per-OTG timing-generator offsets for timing totals, sync/blank windows, trigger controls, counters, status, update locks, interrupts, CRC windows/results, global sync, DRR, DTO, DSC, and pipe update status.
- `regHPD[0-4]_*`: hotplug interrupt status/control, HPD control, fast-train control, and toggle filter control.
- `regDP[0-1]_*`: DisplayPort link, video, DPHY, secondary packet/audio, MSE/SAT, MSA timing, MSO, DSC, DB, VBID, metadata, ALPM, GSP, and status offsets.
- `regDIG0_*` and `regDIG1_*`: digital front/back-end, output CRC, patterns, HDMI metadata/audio/infoframe/generic packets, HDMI ACR, AFMT, TMDS, and FIFO/status offsets. `DIG1` continues after this chunk.

## Control Flow

This header chunk has no runtime control flow. Runtime use is indirect:

1. DCN31-specific code includes `dcn_3_1_2_offset.h` with the matching `dcn_3_1_2_sh_mask.h` and ASIC base definitions.
2. Register-list macros paste symbolic names into offset lookups, pairing `reg...` with `reg..._BASE_IDX`.
3. Component-specific register tables are constructed for ABM, OPP, OTG, HPD, stream encoders, AUX/link encoders, DMUB, IRQ handling, and related DC blocks.
4. Runtime code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET` against those tables to program timing, link, audio/packet, backlight, color-management, and interrupt state.

Ordering and side-effect rules are not represented here. Higher-level display, link, DMUB, IRQ, power, and mode-setting code must still sequence clocks, resets, power gates, update locks, LUT programming, HPD debounce, DP training, HDMI packet setup, ABM locks, and interrupt acknowledgements correctly.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes addresses of MMIO-backed GPU display hardware state.

The represented hardware state includes:

- RMU shaper/3DLUT LUT RAM contents, index/data portals, bank/region descriptors, and output normalization/offset state.
- ABM PWM brightness state, target/current/final levels, ambient/user inputs, ACE coefficients, histogram/luma samples, grouped lock state, panel mask, and master lock state.
- OPP formatter, buffer, pipe CRC, DSC rate-match, memory-power, reset, and performance-monitor state.
- OTG/OPTC timing totals, sync/blank windows, counters, interrupts, update-lock state, CRC state, global sync lock windows, DRR range/change/window state, DTO constants, DSC start position, and pipe-update status.
- HPD interrupt/status/filter/fast-train state.
- DP/DIG link, training, stream, packet, audio, MST/MSO, DSC, HDMI, TMDS, AFMT, CRC, FIFO, and metadata state.

Some of these registers are normal read/write controls, while others are status, readback, sticky interrupt, clear/ack, self-clearing, indexed data, or lock registers. The offset macros do not encode access type, reset value, field width, or side effects; callers need the matching shift/mask header and hardware programming model.

## Dependencies And Integration Points

Primary generated dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h` supplies field shift/mask metadata for these offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/yellow_carp/yellow_carp_offset.h` supplies the ASIC base segment definitions used with `reg..._BASE_IDX`.

Observed direct include sites for the DCN 3.1.2 offset/mask pair:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`

Important integration patterns:

- `dcn31_resource.c` builds `abm_regs`, `vpg_regs`, `afmt_regs`, `stream_enc_regs`, `opp_regs`, `aux_engine_regs`, and DWB/HPD/link-related register tables from generated register-list macros. The ABM, OPP, HPD, DP/DIG, and timing names in this chunk feed those tables.
- `dmub_dcn31.c` defines `REG_OFFSET_EXP(reg_name)` as `BASE(reg##reg_name##_BASE_IDX) + reg##reg_name`, then expands DMUB register tables from this generated namespace.
- `irq_service_dcn31.c` includes this header with the matching masks so IRQ code can map and program interrupt/status registers for HPD, OTG/vblank/vline/vupdate, page flips, and DMUB outbox events.
- DC helper headers and common block implementations consume these offsets through register-list macros for OPP (`OPP_REG_LIST_DCN30`), ABM (`ABM_MASK_SH_LIST_DCN30` paired with ABM register lists), HPD (`HPD_REG_LIST`), stream encoders, AFMT/VPG, and DIO/link encoder logic.

## Risks And Edge Cases

- Offset metadata is hardware ABI. A wrong numeric offset or `_BASE_IDX` compiles cleanly but can redirect reads/writes to the wrong register or IP segment, causing blank displays, bad timing, corrupt color, bad brightness, link-training failure, audio/packet regressions, interrupt storms, or resume failures.
- The chunk starts and ends inside logical groups. It begins with only the final `MPC_RMU0_3DLUT_OUT_OFFSET_B` pair, and it ends before the last `DIG1` TMDS/version/force-disable offsets. Whole-file conclusions must merge adjacent chunks.
- Repeated register families are copy-sensitive. ABM0-3, OPP0-3, ODM0-3, OTG0-3, HPD0-4, DP0-1, and DIG0-1 differ largely by instance number and base offset; an instance drift can break only multi-display, connector-specific, or higher-pipe configurations.
- LUT and indexed data registers are stateful. Incorrect RMU shaper/3DLUT offsets can corrupt color only when HDR, gamma, shaper, or 3D LUT paths are exercised.
- ABM registers combine backlight control, histogram readback, ACE curves, update locks, and firmware-managed behavior. Incorrect offsets can produce brightness jumps, flicker, stuck locks, bad histogram data, or suspend/resume divergence.
- OTG and DP/DIG blocks contain timing, interrupt, and packet registers with strict sequencing requirements. Address correctness alone does not protect update-lock, vblank, DP training, MST/MSO allocation, DSC, secondary packet, HDMI ACR, or TMDS programming order.
- HPD and interrupt status/control registers may have sticky or write-one-to-clear behavior. Treating them as ordinary storage can lose events or leave interrupts asserted.
- Some offsets in this file use base index `3` for display/MMIO-style blocks, while DIO DP/DIG/HPD blocks use base index `2`. Pairing an offset with the wrong base-index selector is as damaging as a wrong offset.

## Test Signals

Useful validation combines compile-time checks, generated-header comparison, and hardware exercise:

- Build AMDGPU/DC with DCN31 enabled. Missing or renamed macros should fail while expanding resource, DMUB, IRQ, OPP, ABM, HPD, DP/DIG, and timing-generator register lists.
- Mechanically verify that every non-`_BASE_IDX` `reg...` macro in lines 7671-10248 has an immediately matching `reg..._BASE_IDX` macro. This chunk has a balanced 1,193/1,193 split.
- Diff the chunk against AMD's authoritative DCN 3.1.2 register database and adjacent DCN versions where layouts should be compatible.
- Exercise RMU color paths with shaper LUT and 3D LUT programming, HDR/gamma transitions, modesets, plane updates, and suspend/resume.
- Exercise ABM/backlight on eDP panels: user brightness changes, ABM level changes, ambient-level input, PWM fraction/current/target/final readback, histogram/ACE readback, panel-mask selection, lock/unlock paths, and resume restoration.
- Exercise OPP/OTG paths with multi-pipe and multi-display modesets, vblank/vline/vupdate IRQs, update locks, DRR/VRR changes, CRC capture, stereo/interlace where supported, DSC start position, and pipe-update status.
- Exercise HPD and DP/DIG paths: hotplug/unplug, HPD debounce, DP link training and retraining, MST/SAT/MSO, DSC over DP, ALPM/GSP where supported, HDMI modes, HDMI audio/ACR, infoframes/generic packets, AFMT, TMDS, and output CRC/test-pattern paths.
- Monitor kernel logs and display diagnostics for DMUB timeouts, IRQ storms, missed HPD events, blank display, bad timings, page-flip timeout, underflow, bad color, audio loss, malformed infoframes, brightness flicker, and resume regressions.

## Cross-Chunk Notes

The previous chunk is required for complete `MPC_RMU0` coverage. The next chunk is required for the rest of `DIG1` and the following `DP2` register block. The final per-file research document should reconcile this chunk with neighboring chunks before making claims about complete RMU, DIG, DP, or DCN 3.1.2 offset-header coverage.

### subset-b-001800: lines 10249-12816

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h lines 10249-12816

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.1.2 register offset header. It exports preprocessor constants that map named display-controller registers to MMIO offsets, paired with `<register>_BASE_IDX` constants. The companion `dcn_3_1_2_sh_mask.h` header supplies field shifts and masks; this offset header supplies register addresses consumed by AMD display resource construction, link/stream encoders, AUX/DDC helpers, DMUB support, IRQ tables, panel control, DSC, and diagnostic register helpers.

The requested range is a large generated block covering DCN display I/O and early DSC offsets. It starts at the tail of DIG1 TMDS/version/disable definitions, then covers DP/DIG transmitter instances 2 through 4, AFMT audio packet blocks for DIG0 through DIG4, DME and VPG metadata blocks for DIG0 through DIG4, DP AUX instances 0 through 4, the shared DOUT I2C block, DIO miscellaneous and DIO perfmon offsets, shared DCIO and GPIO/DCIO-chip offsets, UNIPHY macro reserved offsets for UNIPHY1 through UNIPHY4, two panel power-sequencer instances, DSC encoder instances 0 and 1, associated DSCCIF/top/perfmon blocks, and the beginning of DSC encoder instance 2.

There are no functions, structs, branches, loops, or direct runtime side effects in this chunk. The exported surface is generated register metadata. Runtime behavior is produced when DCN 3.1 resource code expands register-list macros into tables and later code uses `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `AUX_REG_*`, and related helper macros against those tables.

The range has partial logical boundaries. It begins in the last few DIG1 definitions from a previous address block and ends in the middle of `dce_dc_dsc2_dispdec_dscc_dispdec`, after `regDSCC2_DSCC_RATE_BUFFER2_MAX_FULLNESS_LEVEL_BASE_IDX`. The remaining DSCC2 fullness, rate-control fullness, debug, DSCCIF2, DSC_TOP2, perfmon, and later blocks continue after this chunk.

## Register Blocks Covered

The chunk opens with three tail definitions for DIG1: `regDIG1_TMDS_CTL2_3_GEN_CNTL`, `regDIG1_DIG_VERSION`, and `regDIG1_FORCE_DIG_DISABLE`. These are the last TMDS control/version/disable offsets for the DIG1 stream-encoder block whose earlier registers are outside this range.

`dce_dc_dio_dp2_dispdec`, `dce_dc_dio_dp3_dispdec`, and `dce_dc_dio_dp4_dispdec` provide DisplayPort link offsets for DP instances 2, 3, and 4. Each repeated instance includes link control, pixel format, MSA colorimetry/misc/timing parameters, video stream control, steering FIFO, DPHY internal/control/training/symbol registers, 8b/10b and PRBS/scrambler controls, CRC controls/results, fast training, secondary-data packet/audio timestamp controls, MST/MSE rate and slot allocation registers, HBR2 pattern controls, MSO controls, DSC handoff controls, metadata transmission, DSC bytes-per-pixel, ALPM, GSP packet controls 8 through 11, and GSP double-buffer status.

`dce_dc_dio_dig2_dispdec`, `dce_dc_dio_dig3_dispdec`, and `dce_dc_dio_dig4_dispdec` provide DIG stream-encoder offsets for instances 2 through 4. Each repeated block includes front-end control, output CRC control/result, clock/test/random patterns, FIFO status, HDMI metadata/control/status, HDMI audio/ACR/VBI/infoframe/generic packet controls, HDMI GC and DB controls, ACR N/CTS programming and status for 32/44/48 kHz families, AFMT top control, DIG backend enable/control, TMDS control characters/patterns/DC balance/control-bit registers, DIG version, and force-disable.

`dce_dc_dio_dig0_afmt_afmt_dispdec` through `dce_dc_dio_dig4_afmt_afmt_dispdec` provide AFMT offsets for audio and auxiliary packet formatting per DIG instance 0 through 4. Each instance carries VBI packet control, audio packet control, packed audio info registers, IEC 60958 channel-status registers, audio CRC control/result, ramp controls, AFMT status, infoframe control, interrupt status, audio source control, and AFMT memory-power offset.

`dce_dc_dio_dig0_dme_dme_dispdec` through `dce_dc_dio_dig4_dme_dme_dispdec` provide one `DME_CONTROL` offset per DIG instance. `dce_dc_dio_dig0_vpg_vpg_dispdec` through `dce_dc_dio_dig4_vpg_vpg_dispdec` provide Video Pattern Generator and metadata-packet offsets per DIG instance: generic packet control/status, generic packet update, GSP frame update, and two SMU generic packet status registers.

`dce_dc_dio_dp_aux0_dispdec` through `dce_dc_dio_dp_aux4_dispdec` provide DP AUX channel offsets for instances 0 through 4. Each AUX block includes AUX control, software control, arbitration, interrupt control, SW/link-service status, SW/link-service data registers, DPHY TX reference/control, DPHY RX control 0/1, DPHY TX/RX status, GTC sync control/error/controller/status, and PHY wake control.

`dce_dc_dio_dout_i2c_dispdec` provides the shared display-output I2C/DDC engine offsets. It includes controller/arbitration/interrupt/SW status, DDC1 through DDC5 hardware status, per-DDC speed and setup registers, transaction descriptors 0 through 3, data, EDID-detect control, and read-request interrupt.

`dce_dc_dio_dio_misc_dispdec` provides shared DIO scratch and control offsets. It includes scratch registers 0 through 7, DIO memory-power status/control, DIO clock controls, DIO power-management control, DIG soft reset, HDMI RX-status timer control, generic interrupt message/clear, and link-type controls for DIO links A through F. `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec` provides the DIO perfmon 18 offsets: counter control, counter state, perfmon control, threshold/current-value misc, and high/low readback.

`dce_dc_dcio_dcio_dispdec` provides shared DCIO offsets such as `DC_GENERICA/B`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, UNIPHYA through UNIPHYE link and channel-xbar controls, write-command delay, pinstraps, intercept state, BL PWM frame-start display selection, genlock/swaplock pad controls, and DCIO soft reset.

`dce_dc_dcio_dcio_chip_dispdec` provides GPIO and pad-control offsets used around DDC, HPD, AUX, and panel power. It includes generic GPIO mask/A/EN/Y registers, DDC1 through DDC5 and DDCVGA GPIO register sets, genlock and HPD GPIO sets, PWRSEQ0/PWRSEQ1 enables, pad strengths, PHY AUX control, TX12 enable, AUX controls 0 through 5, RX enable, pullup enable, and AUX/I2C pad power-good status.

`dce_dc_dcio_dcio_uniphy1_dispdec` through `dce_dc_dcio_dcio_uniphy4_dispdec` are repeated UNIPHY macro reserved ranges. Each instance exposes `regDCIO_UNIPHYx_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57`, with base offsets spaced by UNIPHY instance. These are not self-describing functional registers in the generated names; they are reserved PHY macro control slots whose field meanings, if any, are handled by lower-level PHY programming or silicon documentation.

`dce_dc_pwrseq0_dispdec_pwrseq_dispdec` and `dce_dc_pwrseq1_dispdec_pwrseq_dispdec` provide panel power-sequencer offsets for two instances. Each instance includes power-sequence GPIO enable/control/mask/A/Y, panel sequence control/state/delays/reference dividers, backlight PWM control/control2/period, PWM group register lock, a second reference divider, and spare register.

`dce_dc_dsc0_dispdec_dscc_dispdec` and `dce_dc_dsc1_dispdec_dscc_dispdec` provide complete DSCC offset sets for DSC encoder instances 0 and 1. Each includes DSCC config 0/1, status, interrupt-control/status, PPS config 0 through 22, DSCC memory-power control, squared-error readbacks for R/Y, G/Cb, and B/Cr channels, maximum absolute-error registers, rate-buffer maximum-fullness registers 0 through 3, rate-control-buffer maximum-fullness registers 0 through 3, and debug bus rotate.

`dce_dc_dsc0_dispdec_dsccif_dispdec` and `dce_dc_dsc1_dispdec_dsccif_dispdec` provide DSCCIF config 0/1 offsets. `dce_dc_dsc0_dispdec_dsc_top_dispdec` and `dce_dc_dsc1_dispdec_dsc_top_dispdec` provide DSC top control and debug control offsets. `dce_dc_dsc0_dispdec_dsc_dcperfmon_dc_perfmon_dispdec` and `dce_dc_dsc1_dispdec_dsc_dcperfmon_dc_perfmon_dispdec` provide DC perfmon 19 and 20 offsets for DSC instances 0 and 1.

The final block begins `dce_dc_dsc2_dispdec_dscc_dispdec` at base address `0x2e0` and covers DSCC2 config/status/interrupt, PPS config 0 through 22, memory-power control, squared-error registers, max-absolute-error registers, and rate-buffer maximum-fullness registers 0 through 2 before the chunk ends.

## Important APIs, Types, And Macros

The important API is the generated naming contract:

- `reg<block/register>` gives the register offset in the DCN 3.1.2 address space.
- `reg<block/register>_BASE_IDX` gives the segment/base index passed through `BASE()` or register-list helper expansion.
- Address-block comments such as `// addressBlock: dce_dc_dio_dp2_dispdec` and `// base address: 0x800` delimit generated hardware blocks and help correlate offsets with hardware instances.
- Instance prefixes are part of the API: `DP2`/`DP3`/`DP4`, `DIG2`/`DIG3`/`DIG4`, `AFMT0` through `AFMT4`, `DME0` through `DME4`, `VPG0` through `VPG4`, `DP_AUX0` through `DP_AUX4`, `PWRSEQ0`/`PWRSEQ1`, `DSCC0` through the beginning of `DSCC2`, and `DC_PERFMON18` through `DC_PERFMON20`.

`display/dc/resource/dcn31/dcn31_resource.c` is the main DCN display consumer. It includes `dcn/dcn_3_1_2_offset.h` and `dcn/dcn_3_1_2_sh_mask.h`, then expands these generated offsets into static register tables. The relevant tables in or touching this chunk include `AFMT_DCN31_REG_LIST(id)`, `VPG_DCN31_REG_LIST(id)`, `APG_DCN31_REG_LIST(id)` where adjacent APG/VPG metadata paths depend on the same stream-encoder ecosystem, `SE_DCN3_REG_LIST(id)`, `DCN2_AUX_REG_LIST(id)`, `LE_DCN31_REG_LIST(id)`, `UNIPHY_DCN2_REG_LIST(phyid)`, `DPCS_DCN31_REG_LIST(id)`, and `DSC_REG_LIST_DCN20(id)`.

`display/dc/dcn31/dcn31_afmt.h` maps the AFMT register-list interface to generated names such as `AFMTx_AFMT_INFOFRAME_CONTROL0`, `AFMTx_AFMT_VBI_PACKET_CONTROL`, `AFMTx_AFMT_AUDIO_PACKET_CONTROL`, `AFMTx_AFMT_60958_0/1/2`, and `AFMTx_AFMT_MEM_PWR`. The corresponding shift/mask list uses instance-0 field names from the companion sh/mask header while per-instance addresses come from this offset header.

`display/dc/dio/dcn31/dcn31_dio_link_encoder.h` maps link-encoder register lists to this chunk's DP, DIG, DIO link, AUX, and UNIPHY offsets. `LE_DCN31_REG_LIST(id)` adds `DPx_DP_DPHY_INTERNAL_CTRL` plus shared DIO link-control offsets A through F; the DCN31 link-encoder mask list includes DP FEC fields, TMDS control bits, AUX DPHY timing fields, and HPO encoder selection fields. `UNIPHY_DCN2_REG_LIST(phyid)` binds UNIPHY link/xbar registers for transmitter routing.

`display/dc/dio/dcn30/dcn30_dio_stream_encoder.h` and related stream-encoder code consume the DIG, HDMI, TMDS, AFMT, and DME-style offsets through stream-encoder register structures. Runtime code programs HDMI infoframes/audio, audio clocking, generic packet memory, DME metadata enable/requestor/stream type, and TMDS/DP encoder behavior through these generated addresses.

`display/dc/dsc/dcn20/dcn20_dsc.h` defines `DSC_REG_LIST_DCN20(id)` and `DSC_REG_LIST_SH_MASK_DCN20(...)`. In `dcn31_resource.c`, three DSC instances are constructed using `dsc2_construct(dsc, ctx, inst, &dsc_regs[inst], &dsc_shift, &dsc_mask)`. The DSCC0/1/2 offsets in this chunk are therefore the hardware register addresses used by the generic DCN20 DSC implementation for DCN 3.1 hardware.

`display/dc/dcn301/dcn301_panel_cntl.h` and `display/dc/dcn301/dcn301_panel_cntl.c` define/use the panel-control register-list pattern for `PANEL_PWRSEQx_*` registers. DCN31 resource construction inherits the panel-control model; the offsets here are the PWRSEQ-side addresses for panel power, DIGON/BLON sequencing, reference dividers, and backlight PWM state.

`display/dmub/src/dmub_dcn31.c` also includes this header and its sh/mask companion. It uses the generated `reg...` and `reg..._BASE_IDX` symbols through `REG_OFFSET_EXP(reg_name)` to build `dmub_srv_dcn31_regs` for DMUB firmware service access. Not every register in this chunk is necessarily in the DMUB register macro list, but this file is part of the same generated DCN31 register-address namespace.

`display/dc/irq/dcn31/irq_service_dcn31.c` includes the same generated headers for DCN31 IRQ registration. IRQ sources that refer to DIO, AUX, HPD, DSC, or other generated DCN31 registers depend on the offset/mask contract remaining synchronized.

## Functional Register Groups

The DP transmitter groups are the low-level address surface for link encoding. Link control, MSA timing, video stream enable, DPHY lane/training controls, CRC, fast training, secondary-data packets, MSE/MST allocation, MSO, DSC, metadata, and ALPM registers are the hardware endpoints for modesetting, link training, DSC-over-DP setup, MST scheduling, compliance patterns, and link diagnostics.

The DIG stream-encoder groups are the address surface for HDMI/TMDS and generic digital-output programming. They include HDMI metadata and audio packet controls, ACR timing registers, infoframe and generic packet controls, TMDS pattern/DC-balance registers, output CRC, test/random pattern generators, and front-end/backend enable controls. These offsets matter for HDMI audio, HDMI/DVI/TMDS output, generic infoframes, pixel packing, and output validation.

The AFMT groups provide per-DIG audio formatting and packet-insertion offsets. Runtime code uses the AFMT controls for audio info updates, audio source selection, channel enable/layout, IEC 60958 channel-status values, audio sample send, audio CRC diagnostics, and AFMT memory power. These registers interact with both HDMI and DP audio packet paths.

The DME and VPG groups are metadata-generation endpoints. DME control enables and routes dynamic metadata, while VPG generic packet controls/status/update registers schedule and report generated packet state. The nearby SMU generic packet status offsets indicate integration with firmware-managed packet/state reporting.

The AUX groups are the DP AUX/DDC-over-AUX physical and protocol control surface. AUX control, software control, arbitration, interrupt status, SW/LS data/status, DPHY timing/status, GTC sync, and wake controls are used during connector detection, EDID reads, DisplayPort link training, sideband transactions, and AUX wake/power transitions.

The DOUT I2C group is the non-AUX DDC engine address surface. It exposes per-DDC speed/setup, transaction descriptors, data, arbitration, interrupt/status, EDID-detect control, and read-request interrupt state. It is shared across physical DDC lines rather than replicated per DIG encoder.

The DIO miscellaneous and perfmon groups expose shared state around scratch registers, memory-power control/status, clock control, soft reset, generic interrupts, link-type controls, HDMI RX-status timing, and DIO performance counters. These are not per-stream encoder addresses, but shared display I/O control and telemetry endpoints.

The DCIO and DCIO-chip groups expose top-level pin, PHY, pad, GPIO, HPD, DDC, AUX, genlock/swaplock, backlight frame-start, reference-clock, and soft-reset offsets. These provide integration points between logical display links and physical pins/connectors.

The UNIPHY reserved macro-control ranges are per-PHY address windows. The generated names do not expose semantic fields, so direct named consumers are limited compared with DP/DIG/AUX/AFMT. They still define stable offsets for PHY macro access, register dumps, low-level bring-up, debug, or PHY programming sequences that address reserved slots.

The PWRSEQ groups are the panel power and backlight sequencing address surface. They describe GPIO power-sequence controls, panel target/current state, power-up/down delays, reference dividers, PWM enable/period/control, lock, and spare state for two panel sequence instances. They are particularly important for eDP or embedded-panel power sequencing.

The DSCC/DSCCIF/DSC_TOP groups provide the Display Stream Compression register-address surface. DSCC config, PPS config, memory power, interrupt/status, error counters, and fullness counters map to the generic DSC implementation. DSCCIF config addresses represent the input interface, and DSC_TOP addresses represent top-level DSC clock/debug control. The associated perfmon blocks expose DSC performance counter readback and control.

## Control Flow And State Behavior

This header has no direct control flow. The runtime flow is table driven: DCN31 resource construction expands the generated offset macros into register-address structures, passes those structures plus sh/mask tables into block constructors, and later hardware blocks use helper macros to perform MMIO reads/writes.

Most state described by these offsets is hardware register state. Configuration registers persist until reprogrammed, reset, power-gated, or overwritten by firmware/hardware sequencing. Examples include DP link setup, MSA timing, DIG/HDMI packet controls, AFMT audio controls, DME/VPG metadata configuration, AUX DPHY timing, DDC speed/setup, DIO clocks/resets, DCIO pin routing, PWRSEQ delays/PWM settings, DSC PPS parameters, and DSCC memory-power controls.

Status and telemetry registers are live hardware state. Examples include DP CRC/status, fast-training status, MSE slot-allocation status, DIG output CRC/FIFO/status, AFMT status/CRC/interrupt state, AUX SW/LS/DPHY/GTC status, I2C HW/SW status, DIO memory-power status, perfmon counter state/readback, panel power-sequence state, DSCC status/interrupt, DSC error counters, and maximum-fullness counters.

Several groups are ordering-sensitive. DP link training and AUX PHY setup require programming the correct channel instance and transmitter/UNIPHY route before training transactions. HDMI/AFMT packet updates often involve double-buffered packet memory and update bits. DME metadata programming has comments in the stream-encoder path requiring OTG master update lock when changing DME configuration. DSC PPS and slice/topology state must be coherent before enabling compressed output. Panel PWRSEQ delays and PWM controls must respect panel power timing and backlight sequencing.

State is also distributed across separate generated blocks. A display link can involve DIG stream-encoder offsets, DP link offsets, AUX offsets, DCIO UNIPHY/link/xbar offsets, HPD/GPIO offsets, AFMT offsets, VPG/DME offsets, and possibly PWRSEQ or DSC offsets. A correct runtime sequence depends on those register tables pointing to the same physical/logical instance mapping.

## Dependencies And Integration Points

This file must remain synchronized with `dcn_3_1_2_sh_mask.h`. Offset macros name the registers and their addresses; sh/mask macros name the fields in those registers. Register-list initializers often use offset macros from this file and field macros from the companion header in separate structures, so mismatch can produce compile failures or, worse, valid builds that write the wrong register or bit field.

The DCN31 display resource path is the main integration point. `dcn31_resource.c` includes this header, builds register arrays for AFMT, VPG, stream encoders, AUX, HPD, link encoders, HPO encoders, DSC, DWBC/MCIF writeback, and other DCN blocks, and constructs hardware block objects from those tables. For this chunk, the highest-impact covered tables are AFMT, AUX, link encoder, stream encoder/DME/VPG, PWRSEQ-related panel control, and DSC.

The link-encoder path integrates DP/DIG/AUX/DCIO/UNIPHY offsets with VBIOS connector information. Runtime transmitter routing relies on `TRANSMITTER_UNIPHY_A` through `TRANSMITTER_UNIPHY_E` mapping to `link_enc_regs[]`, while AUX channel selection uses `enc_init_data->channel - 1` to index the AUX register table. Any generated offset/index mismatch can route training or AUX transactions to the wrong physical connector.

The AFMT and stream-encoder paths integrate with audio, HDMI infoframe, and generic-packet code. AFMT registers are constructed separately from the core stream-encoder registers but act on the same DIG instance. The packet/audio code therefore depends on AFMT instance ordering matching DIG instance ordering.

The AUX and I2C/DDC paths integrate with connector discovery, EDID, DisplayPort training, sideband communication, and HPD behavior. AUX offsets are per-channel, while DOUT I2C registers are shared controller resources with per-DDC speed/setup/status offsets. These offsets also intersect with DCIO-chip GPIO and AUX pad controls.

The panel-control path integrates PWRSEQ offsets with embedded-panel power and backlight behavior. The DCN301 panel-control code reads/writes PWRSEQ target/current state, DIGON/BLON state, and BL PWM reference divider; DCN31 resource construction reuses that family of hardware programming for panel control.

The DSC path integrates DSCC offsets with the generic DCN20 DSC implementation. Higher-level mode validation and Display Mode Library code decide DSC feasibility and clocking; `dsc2_construct()` binds the generated offsets and masks so the DSC implementation can program PPS/config/status/memory-power and read telemetry for instances 0 through 2 on DCN31.

The DMUB path integrates generated offsets into firmware service register access. `dmub_dcn31.c` builds a DCN31 DMUB register table using `BASE(reg..._BASE_IDX) + reg...`; this makes generated address correctness important for firmware reset, inbox/outbox, interrupts, and any DMUB-visible DCN register operations.

The IRQ path integrates generated offsets/masks into DCN31 interrupt source tables. AUX, HPD, DIO, DSC, or related interrupt sources depend on this generated address namespace matching the silicon register map.

## Risks And Edge Cases

The primary risk is generated-header drift from the hardware register specification or from the companion sh/mask header. An incorrect offset can compile cleanly if the macro name still exists, but runtime code may program the wrong MMIO register. In this chunk, high-impact failures include broken DP link training, AUX/DDC timeouts, HDMI audio/infoframe corruption, incorrect DIG/UNIPHY routing, panel power sequencing failures, backlight PWM errors, DSC mode failures, or misleading diagnostic counters.

Instance ordering is a recurring edge case. DP2/3/4, DIG2/3/4, AFMT0-4, AUX0-4, and UNIPHY A-E style resources are assembled into arrays and indexed by engine/channel/transmitter IDs. Off-by-one mapping between logical DIG, physical transmitter, AUX channel, HPD source, and connector metadata can make a register table look valid while affecting a different port.

The chunk starts and ends inside larger logical groups. The DIG1 tail must be reconciled with the previous chunk for a full DIG1 report, and DSCC2 is incomplete here. The merge lane should not treat this chunk alone as complete coverage for DIG1 or DSC instance 2.

UNIPHY reserved macro-control registers are opaque. Their generated `RESERVED0` through `RESERVED57` names do not document field semantics, so the safest interpretation is address-window coverage rather than functional behavior. Tests or documentation that infer behavior solely from these names risk overclaiming.

DP and AUX programming is timing-sensitive. AUX DPHY timing registers, wake controls, arbitration, and interrupt/status registers are involved in transactions that can fail due to incorrect thresholds, stale status, power state, or wrong channel routing. DP link training also depends on coherent DP DPHY, MSA, link framing, FEC, MST/MSE, and physical UNIPHY state.

HDMI/AFMT packet programming is stateful and often double-buffered. Wrong offsets for generic packet controls, infoframes, audio source/control, or 60958 channel status can produce silent audio loss, incorrect infoframes, or display compliance failures without a kernel crash.

Panel PWRSEQ offsets are high risk because wrong panel power or PWM register writes can create black screen, flicker, long delays, or unsafe sequencing around embedded panels. Target-state and current-state readbacks must be interpreted with the correct instance and timing.

DSC programming is dense and cross-field dependent. PPS config offsets, slice/config registers, memory-power controls, and interrupt/status registers must match the sh/mask definitions and the selected DSC mode. Wrong DSCC offsets can show up as compressed-stream corruption, underflow/overflow, stuck update status, or invalid telemetry rather than a simple fault.

Perfmon and CRC/status registers are diagnostic state, not pure configuration. Tests must clear/select/enable/read them in the correct order. Stale DIO/DSC perfmon values or CRC state can mislead validation even when offsets are correct.

## Test Signals

Build-time coverage should catch missing or renamed macros in `dcn31_resource.c`, `dcn31_dio_link_encoder.h`, `dcn31_afmt.h`, `dcn30_dio_stream_encoder.h`, `dcn20_dsc.h`, `dmub_dcn31.c`, and `irq_service_dcn31.c`. High-signal compile failures include missing `regDP2_*`, `regDIG2_*`, `regAFMT*_AFMT_*`, `regDP_AUX*_AUX_*`, `regDIO_LINK*_CNTL`, `regUNIPHY*_LINK_CNTL`, `regPWRSEQ*_PANEL_PWRSEQ_*`, or `regDSCC*_DSCC_*` symbols.

DisplayPort validation should exercise DCN31 outputs on DP2/3/4-capable routes, including link training at multiple rates/lane counts, FEC where supported, MST/MSE allocation, DSC-over-DP, MSO where supported, ALPM, HPD events, suspend/resume, and AUX transactions. Useful signals are successful modesets, stable link training, no AUX timeouts, correct DPCD/EDID reads, and no unexpected DP CRC/training/status errors.

HDMI/TMDS validation should exercise DIG2/3/4 HDMI or DVI paths, including audio setup, ACR values, infoframe send/update, generic packets, TMDS output, output CRC/test patterns, and hotplug. Expected signals are correct audio playback/channel status, correct AVI/audio/vendor infoframes, no FIFO/CRC errors, and valid sink behavior across modes.

AFMT/VPG/DME validation should cover audio packet programming, 60958 channel-status updates, AFMT memory-power transitions, dynamic metadata enable/disable, VPG generic packet update/status, and metadata packet delivery. Runtime signals include correct packet captures on the sink/analyzer, no stale update status, and no AFMT interrupt anomalies.

AUX/I2C/DDC validation should cover EDID reads over AUX and DDC, repeated hotplug/unplug, AUX wake behavior, I2C transaction status, interrupt handling, and error recovery. Good signals are deterministic EDID/DPCD reads, bounded retry counts, and clean status after failed transactions.

Panel-control validation should exercise eDP panel power-up/down, backlight PWM enable/period/brightness, DIGON/BLON sequencing, suspend/resume, and panel off/on cycles. Useful signals are correct panel state readback, no excessive delays, stable brightness, and no black-screen regressions.

DSC validation should exercise compressed modes on DSC instances 0 through 2 where routing permits. Signals include correct PPS register dumps, successful modesets at DSC-required bandwidths, no DSCC underflow/overflow interrupts, no stuck update-pending/status bits, and sane DSCC fullness/error counters.

Diagnostic validation should include DIO and DSC perfmon counter clear/enable/readback flows and DP/DIG/AFMT CRC readback flows. These tests should assert that counters change only when expected and that clear/status sequencing prevents stale readbacks.

### subset-b-001801: lines 12817-15089

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h lines 12817-15089

## Purpose

This chunk is the final generated offset slice for the DCN 3.1.2 register-address header. It contains C preprocessor constants that map symbolic AMD display/audio register names to MMIO register offsets or indirect-register indices, plus companion `*_BASE_IDX` constants for directly addressed display registers. The range starts at the tail of the DSC2 compressor block, covers HPO top/stream/link/audio packet blocks, then ends with VGA and Azalia/HD-audio indirect index definitions through `azf0inputendpoint7_inputendpointind`.

The file has no executable code. Its purpose is to provide the address half of the generated ASIC register ABI used by the AMDGPU DC display stack. Runtime code includes this header together with generated shift/mask headers and register-list macros so it can program DCN 3.1.2 display hardware without hard-coding numeric offsets in functional C code.

## Important APIs, Types, And Register Groups

- `regDSCC2_*`, `regDSCCIF2_*`, `regDSC_TOP2_*`, and `regDC_PERFMON21_*` finish DSC instance 2. The visible DSCC tail covers rate-buffer and rate-control maximum fullness levels plus debug-bus rotate; DSCCIF and DSC top expose configuration/control/debug offsets; the DSC perfmon block exposes counter control, state, interrupt/misc current value, and high/low readback registers.
- `regHPO_TOP_*`, `regDP_STREAM_MAPPER_CONTROL0..3`, and `regDC_PERFMON22_*` define the high-performance output top-level clock/hardware control, stream mapper routing controls, and HPO perfmon counter/readback registers.
- `regAFMT5_*`, `regDME5_*`, and `regVPG5_*` describe the HPO HDMI stream encoder 0 sideband/audio packet path. AFMT5 covers VBI/audio packet controls, audio info, IEC 60958 words, CRC, ramp controls, status, infoframe control, interrupt status, source control, and memory power. DME5 provides DME control and memory control. VPG5 covers generic packet access/data, generic packet frame/immediate updates, status, memory power, ISRC access/data, and MPEG info registers.
- `regDP_STREAM_ENC0_*` through `regDP_STREAM_ENC3_*` define four HPO DP stream encoder instances. Each stream encoder has clock control, input mux, audio control, clock-ramp-adjuster FIFO status controls, and a spare register.
- `regAPG0_*` through `regAPG3_*`, `regDME6_*` through `regDME9_*`, and `regVPG6_*` through `regVPG9_*` attach APG audio packet generators, DME blocks, and VPG packet generators to the DP stream encoders. The APG instances expose main/debug/packet controls, audio CRC controls/results, status/status2, memory power, and spare offsets.
- `regDP_SYM32_ENC0_*` through `regDP_SYM32_ENC3_*`, `regDP_LINK_ENC0_*`/`regDP_LINK_ENC1_*`, and `regDP_DPHY_SYM320_*`/`regDP_DPHY_SYM321_*` describe HPO DP transport/link hardware. They include stream packer controls, link/lane/frame controls, SDP and MST controls, HDCP/metadata/secondary-data controls, FIFO/debug/state/status registers, PHY symbol controls, DPHY misc/clock-pattern/skew controls, and DPHY test/debug registers.
- `regDCHVM_*` provides display HVM/DCHVM clock/reset, page table, control/status, debug, register-read data, and test-debug bus offsets. Unlike most nearby HPO blocks, this block has base address `0x0` and `BASE_IDX` 1 in the visible definitions.
- `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` are legacy VGA indexed-register constants. They are indirect indices rather than direct MMIO offsets and cover sequencer, CRT controller, graphics controller, and attribute controller registers.
- `ixAZALIA_*`, `ixAUDIO_DESCRIPTOR*`, and `ixSINK_DESCRIPTION*` define Azalia/HD-audio codec and sink-info indirect indices, including converter and pin parameters/control, audio descriptors 0-13, sink info 0-8, hotplug/unsolicited/configuration response controls, LPIB snapshot registers, audio enable/format interrupt status, and root/audio function-group metadata.
- `ixAZF0STREAM0_*` through `ixAZF0STREAM15_*` define per-stream indirect indices for stream descriptor status/control, link position in current buffer, cyclic buffer length, FIFO size, and format.
- `ixAZF0ENDPOINT0_*` through `ixAZF0ENDPOINT7_*` repeat the output endpoint codec converter and pin-control register index set for eight endpoints. `ixAZF0INPUTENDPOINT0_*` through `ixAZF0INPUTENDPOINT7_*` repeat the smaller input endpoint converter/input-pin index set for eight input endpoints.

The direct `reg*` macros use generated MMIO offsets and, for this chunk, mainly `BASE_IDX` 2 or 3 depending on address space. The `ix*` macros are indirect register indices and intentionally do not have `BASE_IDX` companions.

## Control Flow

There is no C control flow in this chunk. The effective runtime flow is created by display and audio driver code that:

1. Selects the correct generated register list for DCN 3.1.2.
2. Chooses an instance-specific macro such as a DP stream encoder, APG, VPG, link encoder, DPHY, DSC, perfmon, or Azalia endpoint constant.
3. Combines the offset with the selected base index or indirect-access path.
4. Uses AMDGPU/DC register helpers to perform MMIO reads/writes, read-modify-write operations with shift/mask macros, or indexed Azalia/VGA accesses.
5. Polls or clears status/interrupt/debug registers where required by the block programming sequence.

The register families imply several hardware programming sequences even though the header does not encode them: HPO top clocks and hardware control before stream/link programming; stream mapper and input mux routing before enabling DP/HDMI encoders; APG/VPG/AFMT packet memory and packet controls before sending audio/infoframes; link encoder and DPHY setup before training or enabling DP transport; perfmon counter selection before reading high/low values; and Azalia converter/pin setup through indirect command/index paths before exposing display audio streams.

## State And Persistence Behavior

The macros themselves are compile-time constants and have no mutable state. The hardware registers they identify hold device state until changed by driver writes, hardware events, reset, suspend/resume, power gating, or a new modeset/audio reconfiguration.

Persistent or stateful hardware surfaced by this chunk includes DSC rate-control fullness/debug state, HPO clock/hardware enable state, DP stream routing, HDMI/DP audio packet generator state, infoframe/generic packet memory contents, APG/AFMT/VPG/DME memory power state, stream encoder FIFO/status/debug state, DP link encoder and DPHY lane/symbol/test state, DCHVM page-table/control/status registers, VGA indexed state, and Azalia codec endpoint/stream/pin state.

Several constants name readback or event registers rather than ordinary configuration registers, for example `*_STATUS`, `*_INTERRUPT_STATUS`, `*_CRC_RESULT`, `*_PERFCOUNTER_STATE`, `*_PERFMON_LOW`, `*_PERFMON_HI`, `*_TEST_DEBUG_*`, `*_LPIB`, and audio enable/format interrupt status indices. Access semantics such as read-only, write-one-to-clear, latched readback, or indirect-index side effects are defined by the hardware spec and the functional driver code, not by this offset header.

## Dependencies And Integration Points

This header is included by DCN 3.1 code paths such as DMUB support, IRQ service setup, and DCN 3.1 resource construction. It is useful only with the matching generated DCN 3.1.2 shift/mask headers and AMD display register-helper machinery. The generated names must match register-list initializers and macro expansions used throughout the AMD display stack.

The direct HPO/DSC/DCHVM definitions integrate with MMIO register access paths. Their `BASE_IDX` values select the correct register aperture in the generated register infrastructure. The Azalia and VGA `ix*` definitions integrate through indexed register access paths, where the value is an index written to an indirect register interface rather than an MMIO address.

The chunk is also tied to hardware instance topology. It defines DP stream encoders 0-3, APG instances 0-3, VPG instances 5-9, DME instances 5-9, DP link encoders 0-1, DPHY symbol blocks 320-321, Azalia streams 0-15, output endpoints 0-7, and input endpoints 0-7. Higher-level code can abstract instance selection, but build correctness depends on the generated per-instance names and offsets remaining exact.

## Risks And Edge Cases

- Offset drift is high impact: a single incorrect numeric value can direct a write to the wrong hardware register while still compiling cleanly.
- The chunk mixes direct MMIO offsets and indirect indices. Treating an `ix*` Azalia/VGA constant as a direct `reg*` offset, or losing a `BASE_IDX` on a direct register, would route access through the wrong mechanism.
- Repeated instance blocks are vulnerable to generation or copy drift. DP stream encoders, APG/VPG/DME instances, Azalia streams, and endpoint/input-endpoint sets should remain structurally consistent except where the hardware intentionally differs.
- HPO DP/HDMI blocks are sequencing-sensitive. Programming stream encoders, packet generators, link encoders, or DPHY registers while clocks, memory power, stream mapping, or link state are wrong can cause blank displays, bad infoframes/audio, CRC failures, link-training failures, or hangs.
- Packet and audio registers have externally visible behavior. Bad AFMT/APG/VPG/Azalia offsets can produce missing audio, wrong channel allocation, incorrect infoframes, stale ISRC/MPEG metadata, or spurious hotplug/unsolicited responses.
- Perfmon, CRC, and debug registers may be readback or latched state. Misclassifying status/ack behavior in caller code can leave interrupts asserted or produce misleading diagnostics.
- The chunk starts in the middle of the DSCC2 register list. Whole-file reconciliation must combine this with the previous chunk to present DSC2 as a complete block.

## Test Signals

- Build coverage should catch missing, renamed, or malformed macro names in DCN 3.1.2 register-list consumers, including DMUB, IRQ, and resource code that includes this header.
- Generated-header comparison against the ASIC register database should validate numeric offsets, base indices, and repeated instance consistency across DP stream encoders, APG/VPG/DME blocks, Azalia streams, and endpoint sets.
- Display runtime tests should include HPO DP and HDMI modesets, stream remapping, multi-stream DP/MST configurations, link training, suspend/resume, hotplug, and mode changes that exercise stream encoder, link encoder, DPHY, and HPO top registers.
- Audio validation should cover HDMI/DP audio enable/disable, channel allocation, high bit rate audio, infoframe updates, unsolicited response/hotplug behavior, stream descriptor programming, and endpoint/input-endpoint codec state.
- Packet-path tests should verify VPG generic packets, ISRC and MPEG metadata, AFMT audio/infoframe packet controls, CRC result readback, and memory power transitions for APG/VPG/AFMT/DME blocks.
- Debug and performance tests should exercise DSC/HPO perfmon counter programming and high/low reads, DP link/DPHY debug status, DCHVM debug/register-read paths, and VGA/Azalia indirect access sanity checks.
