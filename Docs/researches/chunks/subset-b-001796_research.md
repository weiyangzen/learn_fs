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
