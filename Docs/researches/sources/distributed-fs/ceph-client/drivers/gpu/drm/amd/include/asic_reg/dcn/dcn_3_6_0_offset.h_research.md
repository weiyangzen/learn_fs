# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002112`: lines 1-2652, `Docs/researches/chunks/subset-b-002112_research.md`
- `subset-b-002113`: lines 2653-5191, `Docs/researches/chunks/subset-b-002113_research.md`
- `subset-b-002114`: lines 5192-7664, `Docs/researches/chunks/subset-b-002114_research.md`
- `subset-b-002115`: lines 7665-10255, `Docs/researches/chunks/subset-b-002115_research.md`
- `subset-b-002116`: lines 10256-12835, `Docs/researches/chunks/subset-b-002116_research.md`
- `subset-b-002117`: lines 12836-15485, `Docs/researches/chunks/subset-b-002117_research.md`

## Chunk Research

### subset-b-002112: lines 1-2652

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h lines 1-2652

## Scope

This chunk covers the opening 2,652 lines of the generated AMD DCN 3.6.0 register-offset header. The full source file continues after this chunk; this report only describes the address blocks and macros visible in lines 1-2652.

The chunk defines a guarded C preprocessor header, `_dcn_3_6_0_OFFSET_HEADER`, and then emits register address constants for AMD display hardware. There is no executable C logic, no functions, and no runtime data allocation in this chunk. The useful API surface is the macro namespace: each visible hardware register is represented as `reg...` and normally paired with `reg..._BASE_IDX`. In this range I counted 1,183 non-`BASE_IDX` register offset macros and 1,182 `BASE_IDX` macros; the remaining `#define` is the include guard.

## Purpose

The header gives DCN 3.6 display-driver code compile-time names for memory-mapped hardware register offsets. Consumers do not use the raw numeric offsets alone. They combine each `reg...` offset with its `reg..._BASE_IDX` through `ctx->dcn_reg_offsets[]` to compute a final MMIO register address for the active ASIC instance.

This chunk covers these functional areas:

- HDA/Azalia controller, endpoint, stream, and audio codec register windows.
- DCCG display clock generation, DTO, clock-gating, soft-reset, audio DTO, and perfmon registers.
- DMU, RBBMIF, display interrupt controller, display power-gating domains, and DMCUB firmware-visible registers.
- DWB display writeback top/color-pipeline registers, MCIF writeback memory interface registers, and MMHUBBUB registers.
- DCHUBBUB arbitration, SDPIF/VM aperture, return path, VM request interface, and perfmon registers.
- HUBP0 and the beginning of HUBP1 surface-fetch register groups, including HUBPREQ, HUBPRET, cursor, flip, VM, timing, prefetch, and performance registers.

## Macro API And Data Model

Every register definition follows the generated pattern:

- `regNAME` is a register offset, often relative to an address block.
- `regNAME_BASE_IDX` selects a base segment from `ctx->dcn_reg_offsets[]`.
- The address block comments preserve generator metadata: `// addressBlock: ...` and `// base address: ...`.

The key consumer-side expansion pattern is visible in DCN 3.6 code:

- `dmub/src/dmub_dcn36.c` defines `REG_OFFSET_EXP(reg_name)` as `BASE(reg##reg_name##_BASE_IDX) + reg##reg_name`, then fills DMUB register tables in `dmub_srv_dcn36_regs_init`.
- `dc/resource/dcn36/dcn36_resource.c` defines `SR`, `SRI`, `SRII`, `SRII_DWB`, and related helper macros that token-paste these `reg...` names into typed register tables for hardware blocks.
- `dc/irq/dcn36/irq_service_dcn36.c` uses `SRI` and `SRI_DMUB` to build IRQ enable/ack register entries from the same offset/base-index namespace.

The header depends on matching field masks/shifts in `dcn_3_6_0_sh_mask.h`; offsets alone identify register locations, while the sibling mask header identifies bitfields inside those registers.

## Address Block Map In This Chunk

The chunk starts with an absolute-looking HDA/Azalia decoder window at base `0x1300000` and base index `3`, then shifts mostly to display-register base indices `1` and `2`. Some HDA controller aliases also use base indices `0` and `1`. The main block counts are:

- HDA/Azalia decoder blocks: global controller registers, endpoint immediate command data/index windows, input endpoint immediate command windows, CORB/RIRB DMA queues, immediate command/response registers, DMA position buffers, wall clock aliasing, and duplicated controller windows for controller 0 and 1.
- DCCG: 110 visible DCCG display clock registers plus `DENTIST_DISPCLK_CNTL`; includes pixel-rate controls for OTG0-3, DP DTO phase/modulo, PHY PLL resync controls, DSC/DPP/DTB clock DTO controls, clock-gating controls, global timers, audio DTO controls, VSYNC latch/counter registers, soft reset, and SYMCLK controls.
- DC perfmon instances: `DC_PERFMON0` through `DC_PERFMON7` appear at different block bases, each with the standard counter control, state, value, high, and low register pattern.
- DMU/RBBMIF/IHC/power: RBBMIF timeout/status/error status registers, display interrupt status continuation registers `DISP_INTERRUPT_STATUS_CONTINUE` through `CONTINUE25`, interrupt destinations for major display subunits, DMU misc clocks/interrupts/ZSC, and `DOMAIN*_PG_CONFIG`/`DOMAIN*_PG_STATUS` power-gating registers.
- DMCUB: region offsets/top-address registers, region 3 code-window base/top/offset pairs, interrupt enable/ack/status/type, fault addresses, security/memory controls, inbox/outbox base/size/read/write pointers, timer triggers, scratch registers 0-23, GPINT data registers, low-power wake, memory power, processor ID, and control registers.
- DWB and MCIF writeback: DWB clock/memory/update/CRC/output/overflow/soft-reset controls, gamut-remap matrix registers, output gamma LUT control and RAM A/B piecewise region tables, MCIF writeback buffer manager state, buffer addresses and high-address halves, luma/chroma sizes, VMID/security/QOS/P-state/watermark controls.
- MMHUBBUB: warmup config/address region, writeback watermarks, memory power and clock controls, client unit ID, SMU watermark control, outstanding counters, and interface error status.
- Azalia display audio: controller clocking, DTO, DMA, payload, CRC, stream arbiter, memory power, codec root parameters, channel/count/control registers, GTC group offsets, port connectivity, 16 stream index/data windows, 8 output endpoint index/data windows, and 8 input endpoint index/data windows.
- DCHUBBUB: arbitration outstanding/saturation/QOS, per-watermark-set A-D urgency and retraining watermarks, self-refresh enter/exit including Z8 variants, UCLK/FCLK P-state watermarks, fractional urgent bandwidth, host VM, MALL, timeout, global timer, surface-check addresses, VTG controls, soft reset, DCF clock, performance measurement, vline snapshot, and timeout interrupt status.
- DCHUBBUB SDPIF/VM/return-path: SDPIF config, physical VM request, forced IO status, framebuffer and AGP aperture bounds, local HBM address lock/ranges, per-pipe security/noalloc settings, request rate limit, memory power status, return path memory power, CRC values, DCC stats, compbuf/detector controls, debug control, and VM fault registers.
- VM request interface: contexts 0-15 each expose control, page-table base high/low, page-table start high/low, and page-table end high/low. The block also includes default address and fault status/address registers.
- HUBP0 and start of HUBP1: HUBP0 surface config/address/tiling/viewports/request-size/control/clock/MALL/debug/measurement/status registers; HUBPREQ0 surface pitch/address/meta address/flip/in-use/TTU/VM/prefetch/vblank/flip/nominal/per-line/cursor/status registers; HUBPRET0 read-line and interrupt registers; CURSOR0 surface, size, position, hot spot, memory power, and DMDATA registers. The chunk ends in the middle of the HUBP1 block after `regHUBP1_HUBP_MEASURE_WIN_CTRL_DCFCLK`.

## Control Flow

There is no runtime control flow in this header. The effective flow is preprocessor expansion:

1. A DCN 3.6 source file includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. That source defines local token-pasting helpers such as `SR`, `SRI`, `SRII`, or `REG_OFFSET_EXP`.
3. Hardware object register-list macros expand through those helpers.
4. The generated `reg...` and `reg..._BASE_IDX` constants become concrete offsets in driver register tables.
5. Later runtime code reads/writes those computed addresses through the AMD display register access helpers.

Because the addresses are created at compile time and table-initialization time, wrong macros generally manifest as misprogrammed MMIO rather than normal C control-flow failures.

## State And Persistence Behavior

The header itself holds no mutable software state and persists nothing. It names persistent hardware state locations:

- DMCUB inbox/outbox pointers and scratch registers are persistent hardware/firmware communication state while the device is running.
- HUBP/HUBPREQ surface address, flip, in-use, cursor, VM, and prefetch registers describe display scanout state.
- DCHUBBUB arbitration, VM, watermark, P-state, and memory-power registers influence memory fetch behavior and power transitions.
- Azalia CORB/RIRB, stream, endpoint, DTO, and codec registers represent audio command, DMA, stream, and codec state.
- Perfmon and CRC registers expose measurement/test state that can be read by diagnostics.

Reset, suspend/resume, power-gating, display mode set, flip, audio enablement, and DMCUB firmware initialization paths rely on these addresses matching the ASIC register map.

## Dependencies And Integration Points

Primary dependencies:

- `dcn_3_6_0_sh_mask.h` must define compatible bit masks and shifts for the same register names.
- DCN 3.6 resource construction uses this header to populate per-block register tables in `dcn36_resource.c`.
- DMUB service initialization uses DMCUB-visible offsets in `dmub_dcn36.c`.
- DCN 3.6 IRQ setup uses interrupt control/status offsets in `irq_service_dcn36.c`.
- Hardware object headers from DCN 3.5/3.6 families provide register-list macros that expect exact token names such as `HUBP0_DCSURF_SURFACE_CONFIG`, `DMCUB_INBOX0_BASE_ADDRESS`, and `DCHUBBUB_ARB_DATA_URGENCY_WATERMARK_A`.

The base-index indirection is a critical integration point. For example, many visible display registers use base index `2`, DCCG registers often use base index `1`, and the initial HDA decoder window uses base index `3`. Consumers must initialize `ctx->dcn_reg_offsets[]` correctly for the ASIC; this header assumes that mapping is valid.

## Risks

- Offset/base-index drift: If a `reg...` offset is correct but its `BASE_IDX` is wrong, the computed MMIO address targets the wrong segment. This is especially risky where similar numeric offsets recur under different base indices, such as the HDA/Azalia decoder and display-register windows.
- Token-name contract: Consumer macros rely on token pasting. Renaming or omitting a generated macro breaks compilation or silently excludes a register from a table if a higher-level list macro changes.
- Cross-header mismatch: `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h` must be generated from the same register source. A stale mask header can compile but write wrong bitfields into otherwise correct offsets.
- Repeated instance patterns: Blocks such as Azalia streams/endpoints, VM contexts 0-15, perfmon instances, and HUBP instances are easy to mis-generate by one index. The visible HUBP1 block is incomplete in this chunk, so whole-file reconciliation must verify later chunks finish the repeated HUBP1 pattern and subsequent instances.
- Hardware behavior risk: Many macros address memory power, clock gating, power-gating, VM page tables, security levels, and firmware communication. Wrong values in these areas can cause display hangs, memory faults, audio failures, or suspend/resume regressions.
- Generated-file review risk: The file is large and mostly repetitive, so line-by-line human review is unlikely. Automated diffing against authoritative register XML or previous ASIC headers is more important than style review.

## Test Signals

Useful validation signals for this chunk are mostly build-time, boot-time, and hardware-display behavior:

- Compile DCN 3.6 display code with `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`; token-paste macros in DMUB, IRQ, and resource initialization should resolve without missing-register errors.
- Compare generated offsets/base indices against AMD's source register database or adjacent DCN headers for expected deltas. Spot checks in this chunk show common anchors shared with nearby ASIC generations, such as `regDMCUB_INBOX0_BASE_ADDRESS` at `0x01d0`, `regDCHUBBUB_ARB_DATA_URGENCY_WATERMARK_A` at `0x04fe`, and `regHUBP0_DCSURF_SURFACE_CONFIG` at `0x05e5`.
- Exercise display mode set, page flip, cursor movement, DMCUB command submission, hotplug/HPD interrupt handling, and audio stream enablement on DCN 3.6 hardware.
- Check debug/perf counters, CRC registers, DMCUB outbox interrupts, VM fault status, and DCHUBBUB timeout status under stress tests for signs of bad register targeting.
- Run suspend/resume and power-management tests that cover DCCG clock gating, DMCUB memory power, DCHUBBUB/HUBPREQ memory power, DCPG domains, and Azalia memory power controls.

## Chunk Boundary Notes

The chunk begins at the SPDX/license/header guard and ends after the first 21 register macros in `dce_dc_dcbubp1_dispdec_hubp_dispdec`. Later chunks must continue HUBP1 and likely additional HUBP/DPP/OPP/OTG/DIO/DSC-related register blocks. Merge should preserve that this chunk establishes the global header shape, base-index convention, and the early display/audio/memory/firmware register groups.

### subset-b-002113: lines 2653-5191

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h lines 2653-5191

## Purpose

This chunk is generated AMD DCN 3.6 register-offset metadata. It contains no executable driver logic; it exports `#define reg...` constants for MMIO register offsets plus matching `..._BASE_IDX` constants for the AMD display register helper layer. Consumers include this file with `dcn_3_6_0_sh_mask.h` so register tables can combine offsets, shifts, and masks for DCN 3.6 hardware blocks.

The requested range starts near the end of HUBP instance 1 and then covers HUBPREQ/HUBPRET/cursor/perfmon blocks for HUBP instances 1 through 3, followed by DPP instances 0 through 3. The DPP coverage includes CNVC format conversion, CNVC cursor color programming, DSCL scaler registers, CM color-management/gamma-correction registers, DPP top control/CRC registers, and DPP perfmon blocks. Although the path is under a local `ceph-client` mirror, this is AMDGPU display hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, callbacks, or direct I/O operations in this chunk. The interface is the generated macro namespace:

- `regBLOCK_INSTANCE_REGISTER`: register offset used by AMD display `REG_*`, `SRI`, `SRII`, and related token-pasting macros.
- `regBLOCK_INSTANCE_REGISTER_BASE_IDX`: base-address segment selector, `2` throughout this chunk.

This range has 2,387 `#define reg...` macros: 1,193 register-offset macros and 1,194 base-index macros. The one-count difference comes from the chunk starting in the middle of the preceding HUBP1 block, where the matching non-base macro for `regHUBP1_HUBP_MEASURE_WIN_CTRL_DCFCLK_BASE_IDX` is outside this range.

Major macro families:

- `HUBP1`, `HUBP2`, `HUBP3`: per-pipe HUBP surface configuration, tiling/address configuration, primary/secondary viewport dimensions, request sizing, clock control, virtual-memory page configuration, MALL configuration/status, and HUBPREQ debug/measurement windows. This chunk has only the tail of HUBP1 but complete HUBP2 and HUBP3 sections.
- `HUBPREQ1`, `HUBPREQ2`, `HUBPREQ3`: per-pipe request-side surface fetch controls. These include luma/chroma surface pitch, VMID settings, primary/secondary surface and metadata addresses, flip control, surface-in-use and earliest-in-use registers, TTU/QoS controls, VM aperture and L1 TLB controls, vblank/flip/nominal prefetch parameters, per-line delivery, cursor request settings, UCLK p-state force, memory power controls, and status registers.
- `HUBPRET1`, `HUBPRET2`, `HUBPRET3`: return/read-line controls, memory power controls/status, read-line interrupt/status/value registers.
- `CURSOR0_1`, `CURSOR0_2`, `CURSOR0_3`: per-pipe cursor control, address high/low, size, position, hot spot, stereo control, destination offset, cursor memory power, and DMDATA address/control/QoS/status/software data registers.
- `DC_PERFMON8`, `DC_PERFMON9`, `DC_PERFMON10`: HUBP perfmon blocks for the three HUBP instances represented here. Each exposes counter control, counter state, perfmon control, current-value interrupt/misc, and high/low counter value registers.
- `CNVC_CFG0` through `CNVC_CFG3`: DPP format/conversion configuration, surface pixel format, FP bias/scale, color keyer, alpha LUT, pre-dealpha, pre-CSC matrices for A/B paths, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0` through `CNVC_CUR3`: DPP-side cursor color/control and FP scale/bias registers.
- `DSCL0` through `DSCL3`: scaler coefficient RAM, scaler mode/tap controls, horizontal/vertical ratios and initial phases for luma/chroma, black color, DSCL update/autocal, overscan, OTG blanking, recout/MPC size, line-buffer format and memory control/status, and output-buffer controls.
- `CM0` through `CM3`: DPP color-management controls. Each instance maps post-CSC matrices, gamut remap A/B matrices, gamma-correction LUT index/data/control, RAMA/RAMB start/slope/base/end/offset/region registers for B/G/R channels, HDR multiplier coefficient, memory power control/status, dealpha, coefficient format, test-debug windows, and DPP CRC values.
- `DPP_TOP0` through `DPP_TOP3`: DPP control, soft reset, CRC control, and host-read control.
- `DC_PERFMON11` through `DC_PERFMON14`: DPP perfmon blocks. The chunk ends after `DC_PERFMON14_PERFMON_CVALUE_LOW`; later `DC_PERFMON14` high/low value registers are outside this range.

Address-block anchors in this chunk show repeated hardware instance layout. HUBP instance bases are `0x370`, `0x6e0`, and `0xa50` for instances 1-3. DPP instance bases are `0x0`, `0x5ac`, `0xb58`, and `0x1104` for instances 0-3. Perfmon blocks use separate base comments such as `0x1de4`, `0x2154`, `0x24c4`, `0x3890`, `0x3e3c`, `0x43e8`, and `0x4994`.

## Control Flow

This header has no runtime control flow. Runtime behavior is introduced by consumers that token-paste these generated names into register tables:

1. DCN 3.6 modules include `dcn_3_6_0_offset.h` with `dcn_3_6_0_sh_mask.h`.
2. `dcn36_resource.c` builds resource register arrays. In the visible integration path, `hubp_regs_init(id)` expands `HUBP_REG_LIST_DCN30_RI(id)` into per-instance HUBP/HUBPREQ/HUBPRET/cursor offsets, while the resource constructor creates HUBP and DPP objects for each active pipe.
3. DPP creation uses shared DCN 3.5/3.x DPP code and register-list macros that bind CNVC, DSCL, CM, DPP top, and perfmon offsets to generic DPP helper functions.
4. Runtime modeset, plane update, cursor update, scaling, color-management, flip, and power-management paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and `REG_WAIT`. Those helpers use the offset constants from this file and field masks/shifts from the companion header.
5. `dmub_dcn36.c` also includes this header pair and computes DMUB-visible register offsets using `BASE(reg..._BASE_IDX) + reg...`. This chunk is not the primary DMUB register set, but the same generated base-index contract applies.
6. `irq_service_dcn36.c` includes the same header pair for interrupt register initialization. Plane-flip entries for pipes 1-3 and DC underflow/vblank/vline entries can indirectly depend on these per-pipe address patterns, although the specific interrupt status/ack registers mostly live outside this chunk.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in files or memory. It describes MMIO-backed display engine state.

Represented hardware state includes active surface and metadata addresses, viewport geometry, pitch and tiling configuration, VMID/aperture/TLB configuration, flip and surface-in-use state, TTU/QoS and prefetch timing, cursor image addresses and position, DMDATA request state, scaler coefficients and ratios, line-buffer/output-buffer settings, color-space conversion matrices, gamut remap matrices, gamma-correction LUT contents, DPP CRC capture values, perfmon counters, memory power control/status, and debug/test windows.

Persistence is hardware-defined. Most programmed configuration lasts until the next modeset, plane update, power-gating transition, suspend/resume restore, soft reset, or ASIC reset. Status, interrupt, perfmon, flip, surface-in-use, read-line, memory-power-status, and CRC-value registers may be read-only, sticky, edge-triggered, self-clearing, latched, or write-one-to-clear depending on the field definitions in the matching sh/mask header and hardware spec. Because this file is untyped offsets only, users must rely on block-specific helper code for correct ordering, polling, and access restrictions while clocks or memories are gated.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.6 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h` for bit shifts and masks for the same register names.
- AMD display register helper macros such as `REG`, `REG_*`, `SRI`, `SRI_ARR`, `SRII`, `BASE`, `FD_MASK`, and `FD_SHIFT`.
- The `dc_context` `dcn_reg_offsets` table used by `BASE(reg..._BASE_IDX)` when converting generated offsets into real MMIO addresses.

Representative integration points in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes this header and creates DCN 3.6 resource pools. Its `hubp_regs_init(id)` uses `HUBP_REG_LIST_DCN30_RI(id)`, and its constructor creates `dcn35_hubp_create(ctx, i)` and `dcn35_dpp_create(ctx, i)` for each pipe.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn30` and `dcn35` code consume the HUBP/HUBPREQ/HUBPRET/cursor register tables for surface programming, flips, VM setup, request scheduling, MALL behavior, cursor programming, and memory power control.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10` and `dcn32` code consumes DPP-side CNVC, DSCL, CM, LUT, CRC, and memory-power registers. For example, DSCL helper code programs scaler modes/ratios and waits on DSCL memory power status; DPP color-management code reads or writes CM and LUT registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_hw_sequencer.c` schedules DPP color-management programming and references DSCL state in update sequencing; the actual MMIO access routes through DPP register tables populated from generated headers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes this header and computes DMUB register offsets via `REG_OFFSET_EXP(reg)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes this header pair for DCN 3.6 interrupt source setup, including pflip/vblank/vline entries for four display pipes.

## Risks And Edge Cases

- Offset drift is the primary risk. These macros are untyped constants; a wrong offset or base index can compile cleanly while causing MMIO reads/writes to hit the wrong register.
- The chunk has artificial boundaries. It starts in the tail of `HUBP1` and ends before the final `DC_PERFMON14` value registers, so complete per-file conclusions require adjacent chunks.
- Instance repetition is copy-sensitive. HUBP/HUBPREQ/HUBPRET/cursor instances 1-3 and DPP instances 0-3 should preserve regular spacing. A single bad instance offset can create pipe-specific failures that only occur on one display pipe or one plane assignment.
- Surface address, metadata address, VMID, aperture, and TLB offsets are high impact. Errors can fetch from the wrong memory, break page translation, corrupt display output, trigger GPU faults, or expose stale frame contents.
- Flip and surface-in-use offsets are sequencing-sensitive. Bad offsets can cause page-flip interrupts, earliest-inuse tracking, or surface latching to malfunction, leading to flicker, stale frames, missed vblank-synchronized flips, or hangs in wait paths.
- Prefetch, TTU, QoS, UCLK p-state force, and per-line delivery offsets affect bandwidth scheduling. Mistakes may only appear under high-resolution, high-refresh, multi-plane, or memory-clock-transition workloads.
- Cursor and DMDATA offsets are pipe-specific. Bad cursor addresses or hot-spot/position offsets can show as missing cursors, wrong cursor colors, stereo cursor errors, or corrupted DMDATA transactions while normal primary planes still work.
- DSCL offsets are mode-sensitive. Incorrect scaler ratio, init, tap, line-buffer, or autocal offsets can break only scaled modes, chroma subsampling, 4:2:0 content, overscan, or viewport changes.
- CM and gamma LUT offsets can silently degrade color. A wrong post-CSC, gamut-remap, gamma RAM, HDR multiplier, dealpha, or coefficient-format offset may produce wrong color only for color-managed, HDR, or LUT-enabled paths.
- Memory-power control/status offsets are access-order sensitive. Wrong DSCL, CM, cursor, HUBPREQ, or HUBPRET memory power registers can leave memories powered unnecessarily, power them down while active, or make `REG_WAIT` loops time out.
- Perfmon and CRC offsets are diagnostic-sensitive. Incorrect perfmon/CRC registers may make validation or debug tools misleading even when ordinary display output appears usable.

## Test Signals

Useful validation signals are a mix of build-time and hardware behavior:

- Build AMDGPU/DC with DCN 3.6 enabled. Missing, renamed, or malformed offset macros should fail in `dcn36_resource.c`, `dmub_dcn36.c`, `irq_service_dcn36.c`, or shared HUBP/DPP register-list construction.
- Mechanically verify every non-base `reg...` macro in lines 2653-5191 has the expected `..._BASE_IDX` pair inside the same chunk or an adjacent chunk where the assignment boundary splits a pair.
- Diff this range against AMD's authoritative DCN 3.6 register database and nearby generated DCN headers, paying special attention to repeated instance spacing for HUBP1-3 and DPP0-3.
- Exercise multi-pipe modesets and plane assignment: single display, multi-monitor, plane promotion/demotion, overlay planes, cursor movement, page flips, VRR/fast updates, suspend/resume, display off/on, and runtime power management.
- Validate surface fetch paths with different tiling, formats, modifiers, primary/secondary planes, chroma planes, metadata/DCC surfaces, and VMID configurations. Watch for page faults, underflows, stale frames, and pipe-specific failures.
- Exercise scaler paths with unscaled, upscaled, downscaled, 4:2:0/chroma, overscan, viewport crop, and high-refresh modes. DSCL mistakes often show as only scaled-output artifacts.
- Exercise color-management paths with degamma/regamma LUTs, post-CSC, gamut remap, HDR multiplier, dealpha, and CRC capture. Compare register dumps and visual/CRC output to expected programming.
- Check memory-power and low-power transitions by cycling display idle, MALL/sub-viewport scenarios, runtime PM, and suspend/resume while watching for `REG_WAIT` timeouts, hangs, unexpected power draw, or failure to restore display.
- Use DC perfmon and DPP CRC register dumps for `DC_PERFMON8-14`, `DPP_CRC_VAL_*`, HUBPREQ status, and DSCL/CM memory status to confirm diagnostic registers map to the intended hardware pipe.

## Cross-Chunk Notes

Earlier chunks own HUBP0 and the beginning of HUBP1, including the `HUBP1_HUBP_MEASURE_WIN_CTRL_DCFCLK` non-base macro whose base-index macro appears at the start of this range. Later chunks continue after `DC_PERFMON14_PERFMON_CVALUE_LOW` and are needed for the rest of DPP3 perfmon and subsequent DCN 3.6 address blocks. The final per-file research document should merge adjacent chunks before making complete claims about all DCN 3.6 HUBP, DPP, perfmon, IRQ, or DMUB register coverage.

### subset-b-002114: lines 5192-7664

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h lines 5192-7664

## Scope

- Chunk id: `subset-b-002114`
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`
- Source lines: 5192-7664
- Observed content: 2,473 generated header lines containing 2,405 `#define` entries. All entries are `reg*` register-offset macros; 1,202 of them are `_BASE_IDX` companions.

This chunk is a generated AMD DCN 3.6.0 register-offset slice. It has no executable C logic. The range begins with the final two `DC_PERFMON14` counter-value registers, then covers MPC compositor, MPCC routing, MPCC output gamma, MPCC multi-color-management, output CSC, ABM0, and most of ABM1. The final line is `regABM1_DC_ABM1_BL_MASTER_LOCK`; the matching `_BASE_IDX` appears after this chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The chunk publishes compile-time MMIO offsets and base-index selectors for DCN 3.6 display composition and panel/backlight blocks. Driver code combines these values with `dcn_3_6_0_sh_mask.h` field masks so register-list macros can build per-ASIC register tables for the Display Core resource pool, hardware sequencer, DMUB service, IRQ service, MPC color/composition code, and ABM/backlight code.

The covered hardware surface is display-pipeline stateful hardware:

- `DC_PERFMON14` tail and complete `DC_PERFMON15` offsets for display performance counters.
- `MPCC0` through `MPCC3` compositor instances for top/bottom plane selection, OPP routing, blending gains, update-lock selection, background color, memory power, and status.
- Global `MPC` configuration registers for clock/reset, CRC, perfmon event selection, background bypass, host reads, pending status, vupdate-lock groups, CRC results, and DWB mux selection.
- `MPCC_OGAM0` through `MPCC_OGAM3` output gamma and gamut-remap register sets.
- `MPCC_MCM0` through `MPCC_MCM3` multi-color-management register sets, including shaper LUTs, 3D LUTs, 1D LUTs, gamut remap matrices, and memory-power control.
- `MPC_OUT0` through `MPC_OUT3` output mux, denormalization, output CSC coefficient, and coefficient-format registers.
- `ABM0` complete and `ABM1` nearly complete adaptive backlight modulation blocks for PWM input/output, ambient-light/user levels, ACE controls, luma statistics, histogram programming/readback, sample rates, and master locks.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The exported API surface is the generated macro namespace:

- `reg<REGISTER>`: numeric MMIO register offset within the selected DCN register segment.
- `reg<REGISTER>_BASE_IDX`: segment selector consumed by AMD display register helpers before adding the offset.
- `// addressBlock: ...` and `// base address: ...`: generated block comments that identify repeated hardware instances and their hardware database bases.

Important macro families in this range include:

- `regMPCC{0..3}_MPCC_*`: MPCC routing, blending, update lock, background color, memory power, and status offsets.
- `regMPC_*`, `regADR_*_VUPDATE_LOCK_SET*`, `regCFG_VUPDATE_LOCK_SET*`, and `regCUR_VUPDATE_LOCK_SET*`: global MPC control/status, CRC, pending state, writeback muxing, and vupdate-lock routing.
- `regDC_PERFMON15_*`: per-block performance counter control, state, counter value, and monitor high/low offsets.
- `regMPCC_OGAM{0..3}_*`: MPCC output-gamma LUT access, RAMA/RAMB piecewise-linear curve programming, offsets, region descriptors, LUT control, and gamut remap coefficient registers.
- `regMPCC_MCM{0..3}_*`: MCM shaper control and LUT windows, 3D LUT index/data/control, 1D LUT control and RAMA/RAMB piecewise-linear tables, gamut-remap matrix controls, and memory-power controls.
- `regMPC_OUT{0..3}_*`: output muxing, denormalization clamps, CSC mode and matrix coefficients for coefficient banks A/B, plus `regMPC_OUT_CSC_COEF_FORMAT`.
- `regABM0_*` and `regABM1_*`: backlight PWM levels, ambient/user/target/current/final/minimum duty cycle controls, ABM algorithm control, ACE slopes/thresholds, luma-statistic registers, histogram bin/result registers, sample rates, and master-lock registers.

The repeated families are part of the ABI between generated ASIC headers and token-pasting register-list macros. For example, DCN36 resource setup reuses shared DCN3.2-style MPC register lists such as `MPC_REG_LIST_DCN3_2_RI(inst)` and `MPC_OUT_MUX_REG_LIST_DCN3_0_RI(inst)`, which expand names like `regMPCC2_MPCC_TOP_SEL`, `regMPCC_MCM2_MPCC_MCM_SHAPER_CONTROL`, and `regMPC_OUT2_CSC_MODE`.

## Control Flow

This header chunk has no local control flow. Runtime behavior comes from AMDGPU Display Core:

1. DCN36-specific code includes `dcn/dcn_3_6_0_offset.h` and `dcn/dcn_3_6_0_sh_mask.h`.
2. Resource and service code expands register-list macros, token-pasting symbolic register names into offset-table initializers.
3. Helpers compute addresses as `BASE(reg..._BASE_IDX) + reg...` and store them in per-block tables.
4. Runtime display code uses those tables through `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, indexed LUT helpers, and block-specific wrappers.
5. Hardware performs the actual work: MPCC composition, gamma/LUT access, MCM color transforms, output CSC, update-lock synchronization, CRC/perfmon capture, and ABM backlight decisions.

Concrete integration observed in this tree includes `dmub_srv_dcn36_regs_init()` in `display/dmub/src/dmub_dcn36.c`, which initializes DCN36 DMUB register offsets from this generated header, and `display/dc/resource/dcn36/dcn36_resource.c`, which includes the same header and builds DCN36 resource/hardware-sequencer tables. The MPC/MPCC/MCM/output-CSC names in this chunk are also consumed through shared DCN3.x register-list macros in `display/dc/resource/dcn32/dcn32_resource.h`.

The header does not encode sequencing. Consumers must still obey hardware ordering for update locks, LUT index/data writes, RAM bank selection, color-transform enablement, MPCC tree updates, clock/memory power control, CRC/perfmon start/stop, and ABM lock/update flows.

## State And Persistence Behavior

The macros are stateless constants. State exists in the hardware registers they name:

- MPCC registers hold current compositor topology, top/bottom plane inputs, OPP selection, blending gains, background color, update-lock routing, stall/status, and MPCC memory-power state.
- MPC global registers hold clock/reset state, CRC configuration/results, perfmon event selection, DPP pending-status observations, vupdate-lock group routing, and DWB mux state.
- MPCC OGAM registers expose indexed LUT windows and RAMA/RAMB piecewise-linear curve memory. Writes mutate hardware color RAM and related mode/configuration state.
- MPCC MCM registers expose shaper LUT memory, 3D LUT memory, 1D LUT memory, gamut-remap matrix state, and memory-power controls for per-MPCC color management.
- MPC OCSC registers hold output mux, denormalization, and output CSC coefficients for each output path.
- ABM registers hold panel/backlight control state, ambient-light and user-level inputs, duty-cycle targets/current values, ACE thresholds/slopes, luma-statistic observations, histogram readbacks, and master-lock state.
- Perfmon registers hold counter controls, latched values, and monitor state.

Persistence is hardware-defined. Configuration values may survive until a modeset, block reset, power-gating event, suspend/resume transition, GPU reset, or ASIC reset. Status, CRC, histogram, perfmon, pending, and current backlight values may be volatile, latched, sticky, or valid only while the corresponding display pipe, OPP, MPC, or ABM power/clock domain is active. The offset header carries no access-type metadata; consumers must rely on the companion shift/mask header, register specs, and block-specific programming sequences.

## Dependencies And Integration Points

Direct dependencies and consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h`, which supplies the matching field shifts and masks for the offsets in this file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, which includes this header and initializes DCN36 DMUB register offsets with `REG_OFFSET_EXP(reg_name)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` and `dcn36_resource.h`, which include this header and build DCN36 resource, hardware-sequencer, hub, clock, interrupt, MPC, and output register tables.
- Shared DCN3.x MPC register-list definitions in `display/dc/resource/dcn32/dcn32_resource.h`, including MPCC, MPCC OGAM, MPCC MCM, MPC output mux, output CSC, and ABM helper lists.
- AMD display color-management interfaces in `display/dc/dc.h` and hardware-type enums in `display/dc/dc_hw_types.h`, which expose concepts corresponding to MPCC OGAM, MPCC MCM, RMCM, and output CSC programming.
- ASIC enum headers such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h`, which define symbolic field values for MPC/MPCC OGAM/MCM/OCSC modes selected through these offsets.

Integration points visible to users include multi-plane composition, HDR/output gamma, 3D LUT and color-space conversion paths, CRC diagnostics, display performance monitoring, writeback muxing, panel brightness and adaptive backlight behavior, suspend/resume restore, and display power-management transitions.

## Risks And Edge Cases

- Numeric drift is the primary risk. A wrong offset or `_BASE_IDX` can compile cleanly while causing a register helper to read or write the wrong MMIO address.
- This range has artificial chunk boundaries. It starts after the beginning of `DC_PERFMON14` and ends one line before `regABM1_DC_ABM1_BL_MASTER_LOCK_BASE_IDX`, so the merge lane must combine adjacent chunks before making complete-file claims.
- Repeated instance parity matters. `MPCC0` through `MPCC3`, `MPCC_OGAM0` through `MPCC_OGAM3`, `MPCC_MCM0` through `MPCC_MCM3`, `MPC_OUT0` through `MPC_OUT3`, and `ABM0/ABM1` are structurally parallel with shifted offsets. A generation error can break one pipe/output/backlight instance while adjacent instances still work.
- Base-index mistakes are as damaging as offset mistakes. Nearly all registers in the main display blocks use base index `3`, while the leading `DC_PERFMON14` tail uses base index `2`; helpers must not treat raw offsets as absolute addresses.
- LUT and RAM access registers are stateful index/data windows. Wrong sequencing or wrong offsets can corrupt color tables even if individual writes look valid.
- MPCC routing and update-lock registers affect atomic modeset behavior. Incorrect offsets can cause tearing, stale plane composition, wrong OPP routing, or deadlocks waiting for update/status bits.
- Color-management registers are visually sensitive. Errors in OGAM/MCM/OCSC offsets may show up only on HDR, color-managed, wide-gamut, 3D LUT, or multi-plane blending paths.
- ABM registers combine control, locks, live sensor/statistic state, and algorithm results. Bad offsets can cause incorrect brightness, flicker, stuck backlight levels, resume-only panel brightness failures, or misleading luma/histogram diagnostics.
- Perfmon, CRC, pending-status, and histogram values can be transient or latched. Tests must account for timing and power state rather than assuming stable readback.

## Test Signals

Useful validation combines generated-header checks with DCN36 hardware behavior:

- Build AMDGPU display support with DCN36 enabled. Missing or renamed macros should fail in `dmub_dcn36.c`, `dcn36_resource.c`, IRQ setup, and shared MPC/ABM register-list expansions.
- Mechanical header checks: every non-boundary `reg*` offset in this chunk should have a matching `_BASE_IDX`, repeated instance layouts should match expected deltas, and all names should have matching shift/mask entries in `dcn_3_6_0_sh_mask.h`.
- Cross-generation diff checks against nearby DCN3.x offset headers where DCN36 intentionally reuses shared MPC, MPCC, MCM, OCSC, ABM, and perfmon layouts.
- Modeset and composition testing on DCN36 hardware with one through four active pipes, multi-plane blending, MPCC top/bottom paths, OPP routing, update-lock behavior, and DWB mux use.
- Color-path tests covering degamma/gamma, MPCC OGAM LUT programming, MCM shaper/3D LUT/1D LUT use, gamut remap, output CSC banks A/B, HDR metadata workflows, and suspend/resume color-state restore.
- CRC/perfmon diagnostics that start/stop counters, read high/low values, select MPC events, and confirm counter values are coherent across power and modeset transitions.
- ABM/backlight tests covering enable/disable, ambient-light/user-level inputs, min/current/target/final duty cycle transitions, histogram/luma-stat readbacks, master-lock handling, panel blank/unblank, and suspend/resume brightness restore.
- Power-management tests for MPCC/MCM memory-power controls, clock/reset state, repeated modesets, runtime power gating, GPU reset recovery, and static-screen/idle transitions.

## Chunk Boundary Notes

Lines 5192-5197 are the tail of the preceding `DC_PERFMON14` block. Lines 5198-7543 cover complete MPCC0-3, MPC config, DC_PERFMON15, MPCC_OGAM0-3, MPCC_MCM0-3, MPC OCSC, and ABM0 groups. Lines 7544-7664 cover ABM1 through `regABM1_DC_ABM1_BL_MASTER_LOCK`; the companion `_BASE_IDX` and any following ABM blocks must be read from the next chunk before final per-file synthesis.

### subset-b-002115: lines 7665-10255

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h lines 7665-10255

## Purpose

This chunk is generated AMD DCN 3.6 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic display-controller register names to numeric register offsets and companion base-index selectors. Consumers combine each `reg...` offset with its matching `reg..._BASE_IDX` through resource, IRQ, and DMUB register-list macros to compute the actual MMIO address for DCN 3.6 display hardware.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

The requested range is a large mid-file slice. It starts at the tail of the `ABM1` block with only `regABM1_DC_ABM1_BL_MASTER_LOCK_BASE_IDX`, covers complete `ABM2` and `ABM3` adaptive-backlight blocks, covers OPP/formatter/output-buffer/DPG/DSCRM register families for four OPP pipes, covers ODM and OTG/OPTC timing-generator register families for four timing generators, covers OTG CRC32 readout blocks, covers HPD instances 0 through 4, covers DP/DIG link and stream-encoder register families for instances 0 and 1, and ends inside the `DP2` block at `regDP2_DP_DPHY_FAST_TRAINING_BASE_IDX`. The range contains 2,383 `#define` lines: 1,191 register-offset macros and 1,192 `_BASE_IDX` macros because the chunk begins with a lone base-index line from the previous block.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locks in this range. The exported interface is the generated macro namespace:

- `reg<block><instance>_<register>` or `reg<global_register>` constants provide DCN 3.6 register offsets.
- `reg..._BASE_IDX` constants select the base-address segment used by `BASE(reg..._BASE_IDX) + reg...`.
- Address-block comments document the generated register database grouping and per-instance base offset, for example `dce_dc_opp_abm2_dispdec` at base `0x208`, `dce_dc_optc_otg3_dispdec` at base `0x600`, and `dce_dc_dio_dp2_dispdec` at base `0x920`.

Major register families in this chunk:

- `ABM2` and `ABM3`: backlight/PWM level registers, ambient/user/target/current ABM levels, final/minimum duty cycle, ABM control, sample rates, register locks, ACE slopes/thresholds, luma statistics, histogram bins/results, and master lock. The first line is the unmatched `_BASE_IDX` for the previous `ABM1` master-lock offset.
- `DPG0` through `DPG3`, `FMT0` through `FMT3`, `OPPBUF0` through `OPPBUF3`, `OPP_PIPE0` through `OPP_PIPE3`, and OPP pipe CRC registers: output-pixel processing control, dynamic pixel generation/test-pattern support, formatter clamping, 4:2:2 control, OPP buffer control, and pipe CRC controls/results.
- `DSCRM0` through `DSCRM3`: DSC forward configuration for each OPP-side slice/router path.
- Global OPP/top/perfmon symbols: OPP clock/top/ABM controls, GSL source select, OPTC/DLPC/ODM memory power controls/status, spare registers, and DC perfmon counter/control/high/low registers.
- `ODM0` through `ODM3`: OPTC input global/clock/data-source controls, data format, bytes per pixel, width, memory config, RSMU underflow, and underflow thresholds.
- `OTG0` through `OTG3`: timing-generator totals, blanks, syncs, controls, status, vertical interrupts, CRC windows/readbacks, dynamic refresh rate controls, global sync/lock, manual triggers, DSC start position, keepout, and spare registers.
- `OTG_CRC320` through `OTG_CRC323`: 32-bit CRC readout data for OTG CRC channels 0 through 3.
- `HPD0` through `HPD4`: hotplug status/control/toggle-filter registers.
- `DP0`, `DP1`, and partial `DP2`: DisplayPort link, pixel format, MSA, stream timing, video `M/N`, DPHY training/scrambling/CRC/status, MST/secondary packet controls, ALPM, symbol-count status/control, and link-training/test registers.
- `DIG0` and `DIG1`: digital stream encoder front-end/back-end controls, output CRC, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet controls, HDMI status, AFMT bridge control, TMDS controls, sync patterns, DC balancer, and version.

The key consuming types are register-table structs allocated by the DC resource layer, such as `struct dce_abm_registers`, `struct dcn10_timing_generator`, `struct dcn10_link_enc_registers`, `struct dcn10_link_enc_hpd_registers`, `struct dcn10_stream_enc_registers`, and `struct dce110_opp_registers`. These structs receive computed addresses through token-pasting macros rather than by directly naming the generated macros in ordinary C expressions.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMD display code that includes this offset header with the matching `dcn_3_6_0_sh_mask.h` field header.

The main flow is:

1. DCN 3.6 resource construction includes this header and defines helper macros such as `SR`, `SRI`, `SRI_ARR`, `SRI2_ARR`, and `SR_ARR`.
2. Resource register-list macros paste block names and instance IDs into generated symbols. Examples include `SRI_ARR(DC_ABM1_HG_SAMPLE_RATE, ABM, id)`, `SRI_ARR(OPTC_INPUT_GLOBAL_CONTROL, ODM, inst)`, `SRI_ARR(OTG_H_TOTAL, OTG, inst)`, `SRI_ARR(DC_HPD_INT_STATUS, HPD, id)`, and `SRI_ARR(DP_LINK_CNTL, DP, id)`.
3. Each expansion computes `BASE(reg..._BASE_IDX) + reg...`, where `BASE()` indexes `ctx->dcn_reg_offsets[]`.
4. The computed addresses are stored in per-object register tables for ABM, OPP, timing generators, link encoders, stream encoders, HPD, and DMUB support.
5. Later hardware code uses the populated tables with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, polling, IRQ ack, and DMUB register-helper paths.

Observed direct include sites in this tree are `display/dmub/src/dmub_dcn36.c`, `display/dc/irq/dcn36/irq_service_dcn36.c`, and `display/dc/resource/dcn36/dcn36_resource.c`. `dmub_dcn36.c` initializes DMUB register offsets through `REG_OFFSET_EXP(reg_name)`. `irq_service_dcn36.c` builds IRQ enable/ack/status addresses for HPD and OTG interrupts through `SRI(...)`. `dcn36_resource.c` builds the broader DC resource register tables during `dcn36_resource_construct()`.

## State And Persistence Behavior

The macros themselves are compile-time constants and store no software state. The state they describe is MMIO-backed display hardware state:

- ABM state includes programmed backlight levels, PWM duty-cycle limits, ambient-light/user inputs, adaptive brightness controls, luma statistics, histogram results, and register-lock/master-lock state.
- OPP/DPG/FMT/OPPBUF/CRC state includes formatter clamp and 4:2:2 configuration, output buffer state, pattern/DPG controls, and output-pipe CRC capture/results.
- ODM/OTG state includes active timing totals, sync and blank windows, vertical interrupt positions, master-update locks, global sync, CRC windowing, dynamic refresh control, DSC start positioning, underflow thresholds, and timing-generator status.
- HPD state includes hotplug sense/status, interrupt controls, and debounce/toggle filtering.
- DP/DIG state includes link training, stream timing and MSA values, scrambling/CRC/status, MST secondary packet controls, HDMI and DP packet generation, audio clock regeneration, TMDS controls, and stream encoder CRC/test-pattern state.
- Perfmon symbols describe DC performance counter state for OPP/OPTC blocks.

Persistence is hardware-defined. Configuration registers generally retain values until rewritten by modeset, link reconfiguration, power gating, suspend/resume restore, or ASIC reset. Status, interrupt, clear/ack, CRC, perfmon, lock, and counter registers may be sticky, read-only, self-clearing, write-one-to-clear, or sampling-sensitive. This offset header does not encode those access semantics; the companion shift/mask header and consuming display code provide field-level meaning and access ordering.

## Dependencies And Integration Points

This chunk depends on consistency across the generated DCN 3.6 register database:

- `dcn_3_6_0_sh_mask.h` must define matching field masks/shifts for the registers named here.
- `ctx->dcn_reg_offsets[]` must provide correct base addresses for the `_BASE_IDX` segment values. This chunk uses base index `3` for OPP/ABM/OPTC-side blocks and base index `2` for DIO/DP/DIG/HPD-side blocks.
- `display/dc/resource/dcn36/dcn36_resource.c` defines the resource-layer macros that turn these symbols into concrete register tables. Relevant initializers include `abm_regs_init()`, `opp_regs_init()`, `optc_regs_init()`, `hpd_regs_init()`, `link_regs_init()`, and `stream_enc_regs_init()`.
- `display/dc/irq/dcn36/irq_service_dcn36.c` consumes HPD and OTG offsets when constructing IRQ source information for HPD, HPD RX, vblank, vupdate, and vline interrupts.
- `display/dmub/src/dmub_dcn36.c` uses the same offset/base-index contract to initialize DMUB-side register definitions for firmware-assisted operations.
- Common hardware modules under `display/dc/dce`, `display/dc/dcn35`, `display/dc/dio`, `display/dc/optc`, and `display/dc/opp` consume the resulting register tables rather than this generated chunk directly.

The chunk also depends on structural instance alignment. DCN 3.6 resource capabilities in `dcn36_resource.c` expose four timing generators/OPPs and five DIG/link encoders. This range covers complete OPP/OTG instances 0-3, HPD instances 0-4, complete DP/DIG instances 0-1, and the beginning of DP instance 2; adjacent chunks are required for the remaining DIO/link register namespace.

## Risks And Edge Cases

- Offset or base-index drift is the main risk. These are untyped preprocessor constants, so a wrong `reg...` value or `_BASE_IDX` can compile while directing reads/writes to the wrong MMIO segment or register.
- The range has artificial boundaries. It begins with the lone `ABM1` master-lock `_BASE_IDX` and ends at `DP2_DP_DPHY_FAST_TRAINING_BASE_IDX`; a file-level report must merge neighboring chunks before making complete claims about ABM1 or DP2.
- Repeated-instance families are copy-sensitive. OPP, ODM, OTG, HPD, DP, and DIG blocks are structurally similar, but one bad offset can affect only a specific pipe, connector, timing generator, or link encoder and escape broad testing.
- ABM and backlight registers affect visible brightness and panel power behavior. Bad offsets can cause wrong brightness levels, ineffective adaptive brightness, flicker, or lock/update sequencing failures.
- OTG/ODM mistakes can cause severe display symptoms: bad timings, failed vblank/vupdate interrupts, underflows, broken dynamic refresh, incorrect DSC start position, CRC readback failures, or update-lock deadlocks.
- HPD and DIO mistakes can break connector detection, short-pulse handling, EDID/DPCD flows through the link stack, link training, MST payloads, HDMI packet generation, audio, or suspend/resume hotplug recovery.
- Status, clear, lock, CRC, and perfmon registers are side-effect-sensitive. Accessing the wrong address may clear an event, sample stale state, or leave interrupts asserted.
- The header gives no read/write permissions. Consumers must know from hardware specs and field masks which registers are read-only, write-only, write-one-to-clear, double-buffered, or power/clock-gated.

## Test Signals

Useful validation signals include:

- Build AMDGPU/DC with DCN 3.6 enabled; missing or renamed symbols should fail in `dcn36_resource.c`, `irq_service_dcn36.c`, or `dmub_dcn36.c`.
- Mechanically verify that each non-`_BASE_IDX` `reg...` macro in this range has a matching `_BASE_IDX`, accounting for the known initial `ABM1` tail line, and compare offsets/base indices against AMD's authoritative DCN 3.6 register database.
- Exercise four-pipe display configurations to cover OPP/ODM/OTG instances 0 through 3, including modesets, vblank/vupdate interrupts, update locks, dynamic refresh changes, CRC capture, and DSC-enabled modes.
- Validate ABM/backlight behavior on panels that support it: user brightness changes, adaptive brightness transitions, PWM duty-cycle limits, suspend/resume restore, and register-lock behavior.
- Test connector paths for HPD0 through HPD4, including plug/unplug, short-pulse handling, debounce/toggle filtering, resume, and IRQ ack behavior.
- Exercise DP and HDMI links on DIG/DP instances covered by this chunk: link training, lane/rate changes, MST, MSA programming, secondary packets, HDMI generic/infoframe/audio/ACR packets, TMDS output, stream CRC, and ALPM where supported.
- Watch kernel logs and display diagnostics for hotplug storms, stuck IRQs, AUX/link-training timeouts, blank displays, underflow, CRC mismatch, audio dropouts, incorrect brightness, and resume regressions.

## Cross-Chunk Notes

Earlier chunks own the start of the ABM register sequence, including most of `ABM1`. Later chunks continue `DP2` and the remaining DIO/link/output register namespace. The final per-file research document should reconcile this chunk with adjacent chunks before summarizing the complete `dcn_3_6_0_offset.h` hardware map.

### subset-b-002116: lines 10256-12835

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h lines 10256-12835

## Purpose

This chunk is a generated AMD DCN 3.6.0 register-offset header slice. It contains preprocessor constants for display-controller MMIO offsets and the associated `_BASE_IDX` selector used by AMDGPU display register helpers. It has no executable C logic, but it is part of the ABI between the generated ASIC register database and DCN36 display code.

The requested range contains 2,381 `#define` lines: 1,191 register-offset macros and 1,190 `_BASE_IDX` macros. Every `_BASE_IDX` value in this slice is `2`, so consumers resolve these registers through `ctx->dcn_reg_offsets[2]` before adding the generated offset. The slice starts inside the DP2 block, then covers DIG2/DIG3/DIG4, AFMT/DME/VPG packet blocks for DIG0-DIG4, AUX0-AUX4, DPIA mux controls, DIO/I2C/misc/perfmon/DCIO/UNIPHY metadata, PWRSEQ0/PWRSEQ1, and the beginning of DSC/DSCC instances 0-2.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or runtime APIs in this chunk. The exported interface is the generated macro namespace:

- `reg<REGISTER_OR_BLOCKED_REGISTER>` gives a numeric MMIO offset.
- `reg<REGISTER_OR_BLOCKED_REGISTER>_BASE_IDX` gives the DCN base-address-array index used when constructing a final address.
- No `ix...` indexed-register macros appear in this range.

Important register families in this slice:

- DP2 tail: `regDP2_*` exposes late DisplayPort encoder/PHY controls including DPHY fast-training/CRC status, secondary-data-packet controls, audio M/N readback, MSE rate/SAT controls and status, MSA timing, MSO, DSC control, ALPM/auxless ALPM, generic SDP enable/status, and stream/link symbol counters.
- DIG2-DIG4: each DIG front-end block exposes `DIG_FE_*`, output CRC, clock/test/random pattern, FIFO, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic packet/GC/DB controls, TMDS controls, DP video/config/pixel/link/steer/security/DPHY/CRC/MST/MSE/MSA/MSO/DSC/ALPM registers, and DIG back-end controls.
- AFMT0-AFMT4: audio formatter and packet registers cover `AFMT_CNTL`, memory power, audio source/dto/crc/infoframe, 60958 channel status words, VBI/ACP/audio packet controls, interrupt controls, ramp controls, and status.
- DME0-DME4 and VPG0-VPG4: metadata engine controls/memory and video packet generator memory, generic packet, GSP, MPEG, and ISRC controls.
- AUX0-AUX4: DP AUX control, arbitration, software data, LS status, GTC sync, DPHY RX/TX/ref/timer/status/debug registers, interrupt controls, and AUX PHY control.
- DPIA mux and DIO shared blocks: `DPIA_MUX0-3_*`, DIO I2C/DDC controls and status, DIO scratch registers, ALPM wake interrupt status, memory-power status/control, clock control, power management, HDMI RX-status timer, PSP interrupt status/clear, link A-F controls, stream mapper controls, and `DC_PERFMON18`.
- DCIO and GPIO/chip registers: generic DCIO controls, reference/clock controls, UNIPHY A-E link/channel crossbar controls, pinstraps, pattern generator, backlight PWM display select, GSL/genlock/swaplock pad controls, soft reset, DDC/generic GPIO controls, HPD pads, AUX PHY control, and four UNIPHY macro reserved register ranges.
- PWRSEQ0/PWRSEQ1: panel power sequencing GPIO, sequence control/state/delay/reference-divider registers, backlight PWM controls/period/lock, and spare registers.
- DSC/DSCC start: `DSCC0` and `DSCC1` are complete in this chunk, with config/status/interrupt, PPS config 0-22, memory power, squared-error counters, max absolute error counters, rate-buffer fullness, rate-control fullness, and debug-bus rotation registers. `DSCCIF0/1`, `DSC_TOP0/1`, and `DC_PERFMON19/20` are also complete. `DSCC2` begins at the end of the chunk and continues in the next chunk.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU display code that includes this generated metadata:

1. DCN36 resource, IRQ, and DMUB code include `dcn_3_6_0_offset.h` with `dcn_3_6_0_sh_mask.h`.
2. Register-list macros in display block headers token-paste names such as `regDIG2_DIG_FE_CNTL`, `regDP_AUX2_AUX_CONTROL`, `regAFMT3_AFMT_AUDIO_PACKET_CONTROL`, or `regDSCC1_DSCC_PPS_CONFIG0`.
3. Address-construction helpers add the relevant base address, for example `BASE(reg..._BASE_IDX) + reg...`, where `BASE_INNER(seg)` expands to `ctx->dcn_reg_offsets[seg]`.
4. DCN36 resource construction fills static register tables for DIO, link encoders, stream encoders, audio, VPG/AFMT/DME sub-blocks, AUX/I2C, DSC engines, hardware sequencing, IRQ service, and DMUB-facing tables.
5. Runtime hardware objects then access these addresses through register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, AUX helpers, stream-encoder helpers, audio helpers, DSC helpers, IRQ helpers, and DMUB register access.

The macros do not encode sequencing. Consumers still have to order DP link training, HDMI/DP packet programming, audio setup, DME/VPG metadata updates, AUX transactions, I2C/DDC transfers, HPD/PSP interrupt handling, UNIPHY/DCIO routing, panel power/backlight sequencing, DSC PPS programming, DSC power transitions, CRC/perf counter reads, and soft-reset or clock/power transitions correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It names hardware registers whose state is owned by DCN 3.6.0 display blocks:

- DP/DIG state includes stream encoder setup, HDMI packet/audio/infoframe state, TMDS controls, DP training/test/CRC/debug state, MST/MSE scheduling state, MSA/MSO/DSC controls, ALPM controls, and stream/link symbol counters.
- AFMT/DME/VPG state includes audio formatter configuration, metadata packet memory, generic SDP/GSP/MPEG/ISRC packet controls, and interrupt state.
- AUX/I2C/DIO state includes AUX transaction control/status/data, DPHY analog/digital controls, DDC speed/setup/transaction/data registers, DIO memory-power and clock state, stream mapping, link routing, and interrupt/status registers.
- DCIO/UNIPHY state includes physical link routing, channel crossbars, GPIO/HPD/DDC pad state, PHY AUX controls, soft reset, pattern generation, backlight PWM display selection, and reserved macro control storage.
- PWRSEQ state includes panel GPIO configuration, panel power sequencing delays and state, PWM backlight period/duty/control, and PWM lock state.
- DSC state includes compressor config, PPS payload programming, memory power, status/interrupt state, error counters, rate-buffer/fullness telemetry, and perfmon counters.

Persistence is hardware-defined. Configuration values generally remain until a modeset, link retrain, panel power transition, DSC reconfiguration, power-gate cycle, suspend/resume, driver reset, or ASIC reset. Status, interrupt, CRC, perfmon, error, overflow, and debug registers may be read-only, sticky, self-clearing, write-one-to-clear, or only meaningful while the corresponding block is powered and clocked. This offset header does not describe those access semantics.

## Dependencies And Integration Points

This generated header must remain synchronized with AMD's DCN 3.6.0 register database and with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h`, which provides field shifts and masks for the same symbolic register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c`, which includes this header and constructs DCN36 register tables with token-pasting helpers such as `SR`, `SRI`, `SRI_ARR`, `SR_ARR_I2C`, and `SRI_ARR_ALPHABET`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, where `dmub_srv_dcn36_regs_init()` resolves generated offsets through `REG_OFFSET_EXP(reg_name)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c`, which uses the same offset/shift/mask model for DCN36 interrupt source tables.
- DIO/link/stream/audio helper modules such as `dcn35_dio_stream_encoder`, `dcn35_dio_link_encoder`, `dcn31_dio_link_encoder`, `dce_audio`, `dce_aux`, `dce_i2c`, `dcn30_vpg`, `dcn31_vpg`, `dcn31_afmt`, and `dcn35_dsc`.

Direct local integration visible in `dcn36_resource.c` includes:

- `audio_regs_init(id)` for five exposed audio/AFMT instances plus additional audio table entries.
- `VPG_DCN31_REG_LIST_RI(id)` and `AFMT_DCN31_REG_LIST_RI(id)` for VPG and AFMT sub-blocks used by stream encoders and HPO stream encoders.
- `stream_enc_regs_init(id)` for five DIG stream encoder instances.
- `DCN2_AUX_REG_LIST_RI(id)` and AUX/I2C register-list macros for five AUX/DDC engines.
- `UNIPHY_DCN2_REG_LIST_RI(id, phyid)` for five digital link encoders backed by UNIPHY/DCIO controls.
- `DIO_REG_LIST_DCN10()` and `DIO_MASK_SH_LIST()` for shared DIO memory-power and clock controls.
- `DSC_REG_LIST_DCN20_RI(id)` and `DSC_REG_LIST_SH_MASK_DCN35()` for four DSC engines; this chunk fully covers DSC0 and DSC1 register names and starts DSC2.

## Risks And Edge Cases

- The constants are untyped preprocessor values. A wrong offset or `_BASE_IDX` can compile cleanly and route MMIO to the wrong block, wrong instance, or wrong address space.
- The chunk boundary is artificial. It starts in the middle of the DP2 register family and ends in the middle of `DSCC2`; adjacent chunks are required for whole-block conclusions.
- All base indices in this chunk are `2`. A single accidental base-index change would silently move an otherwise plausible register offset into a different DCN base segment.
- Repeated instance families are copy-sensitive. DIG2-DIG4, AFMT0-AFMT4, DME0-DME4, VPG0-VPG4, AUX0-AUX4, PWRSEQ0-1, UNIPHY1-4 reserved ranges, and DSCC0-2 use very similar macro names with different offsets.
- DIG/DP registers are central to link bring-up. Misaddressing can break DP training, MST/MSE allocation, DSC-over-DP enablement, ALPM, HDMI packet emission, TMDS setup, CRC diagnostics, or symbol counter reads.
- AFMT/DME/VPG mistakes can produce missing or stale audio, HDR/static metadata, MPEG/ISRC data, or generic SDP packets. These may present as sink-specific failures rather than immediate driver errors.
- AUX/I2C offsets are high-risk because they affect HPD/EDID/DPCD access, link training sideband transactions, LTTPR discovery, backlight control over AUX, and sink capability reads.
- DIO/DCIO/UNIPHY/link control mistakes can swap or disable physical links, misroute streams, mishandle HPD/DDC GPIO, or leave PHY/pad state inconsistent across suspend/resume.
- PWRSEQ and PWM registers are user-visible and timing-sensitive. Bad offsets can cause dark panels, flicker, incorrect brightness, or broken panel power sequencing.
- DSC offsets are field- and sequence-sensitive. Bad PPS/config/memory-power/status offsets can cause compressed-link corruption, blanking, link retraining failures, or misleading error/perf telemetry.
- Reserved UNIPHY macro registers should be treated as generated hardware metadata. Consumers should not infer semantics from their names without the ASIC programming guide.

## Test Signals

Useful validation combines generated-header consistency with DCN36 hardware behavior:

- Build AMDGPU display code with DCN36 enabled. Missing or renamed macros should fail in `dcn36_resource.c`, `dmub_dcn36.c`, `irq_service_dcn36.c`, or hardware-object register-list expansion.
- Mechanically compare this range with `dcn_3_6_0_sh_mask.h` and AMD's generated register database, checking that every consumed offset macro has a matching `_BASE_IDX` macro and field definitions where needed.
- Diff equivalent blocks against adjacent ASIC headers such as `dcn_3_5_0_offset.h`, `dcn_3_5_1_offset.h`, and later DCN headers to catch accidental instance swaps or unexpected offset/base-index shifts.
- Exercise DP and HDMI outputs on DCN36 hardware: hotplug, cold boot, modeset, high-refresh modes, MST, DSC, MSO where supported, link retraining, test patterns, CRC reads, ALPM transitions, and suspend/resume.
- Exercise audio and metadata paths: HDMI/DP audio, ACR/N/M readback, infoframes, generic packets, HDR metadata, MPEG/ISRC packets, and DME/VPG memory updates.
- Exercise AUX/DDC paths: EDID reads, DPCD reads/writes, LTTPR discovery, link training transactions, I2C-over-AUX, native I2C/DDC transfers, HPD storms, and AUX timeout/error recovery.
- Exercise panel power and backlight flows on eDP systems: panel enable/disable, DPMS, brightness changes, PWM locking, backlight-over-AUX fallback, and suspend/resume.
- Exercise DSC: enable/disable across multiple formats, bpc values, refresh rates, MST cases, error-counter reads, perfmon reads, power-gating transitions, and fallback to uncompressed modes.
- Monitor kernel logs and display diagnostics for register timeout messages, failed AUX/I2C transactions, missing EDID, link training failures, blank or flickering panels, audio dropouts, bad metadata, DSC corruption, HPD/PSP interrupt issues, and resume-only failures.

## Cross-Chunk Notes

This is chunk 5 of 6 for `dcn_3_6_0_offset.h`. Earlier chunks contain the file prologue and preceding DCN36 display register blocks, including the beginning of DP2. The next chunk continues `DSCC2` and the remaining generated register-offset namespace. The final per-file research document should merge adjacent chunks before making complete claims about all DCN36 DP/DIG instances, all PWRSEQ/DSC instances, or the full DCIO/UNIPHY register surface.

### subset-b-002117: lines 12836-15485

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h lines 12836-15485

## Purpose

This chunk is generated AMD DCN 3.6.0 register-offset metadata. It contains no executable C logic; it exports `#define` constants for MMIO register offsets, per-register base-index selectors, and indirect-register indexes. Consumers pair these offsets with `dcn_3_6_0_sh_mask.h` field masks/shifts so AMDGPU display register-helper macros can build typed register tables for DCN 3.6 hardware.

The requested range starts inside the `DSCC2` Display Stream Compression block, then covers `DSCCIF2`, `DSC_TOP2`, `DC_PERFMON21`, full `DSCC3`/`DSCCIF3`/`DSC_TOP3`/`DC_PERFMON22`, HPO top and HDMI/DisplayPort stream/link encoder blocks, DLPC/DCHVM/DPIA control blocks, and Azalia audio endpoint/index spaces through input endpoint 7. Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata and does not implement Ceph or distributed filesystem behavior.

The slice contains 2,307 `#define` lines: 1,293 `reg*` MMIO offset/base-index macros and 1,014 `ix*` indirect register-index macros. The first line is a chunk-boundary continuation, `regDSCC2_DSCC_PPS_CONFIG2_BASE_IDX`, whose matching offset macro appears just before this range. The last macro is `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`, followed by the header guard close.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or direct I/O operations in this chunk. The exported interface is the generated macro namespace:

- `reg<block>_<REGISTER>`: a numeric MMIO register offset relative to the base selected by the companion base-index macro.
- `reg<block>_<REGISTER>_BASE_IDX`: the DCN register-base segment index used by `BASE(...)`/`BASE_INNER(...)` style token-paste helpers.
- `ix<block>_<REGISTER>`: an indirect register index, usually accessed through an endpoint or stream index/data window rather than direct MMIO.

Major macro families in this range:

- `DSCC2`, `DSCCIF2`, and `DSC_TOP2`: the tail of DSC instance 2. The covered registers include PPS config words 3-22, memory power control, squared-error and max-absolute-error telemetry, rate-buffer fullness telemetry, DSCCIF config, DSC top control, and DSC debug control.
- `DC_PERFMON21` and `DC_PERFMON22`: performance counter controls, state, high/low counter values, current-value interrupt/misc status, and per-block perfmon control for DSC instances 2 and 3.
- `DSCC3`, `DSCCIF3`, and `DSC_TOP3`: the complete offset block for DSC instance 3, including config/status, interrupt control/status, PPS config words 0-22, memory power, error metrics, rate-buffer fullness levels, interface config, top control, and debug control.
- HPO common and stream-mapper registers: `HPO_TOP_*`, `HPO_DP_STREAM_MAPPER_CONTROL*`, and stream-clock generation/enable registers for high-performance output routing.
- HPO HDMI instance 0: `HDMI_*`, `HDMI_FRL_*`, `HDMI_GC`, `HDMI_ACR*`, `HDMI_VBI_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL*`, `HDMI_GENERIC_PACKET_CONTROL*`, `AFMT5_*`, `DME5_*`, `VPG5_*`, and `HDMI_TB_*` offsets. These cover HDMI link encoding, Fixed Rate Link encoding, stream encoding, audio/video infoframes, generic packets, audio formatter state, data-mapping engine state, video packet generator state, and timing bridge control.
- HPO DisplayPort stream encoders 0-3: repeated `DP_STREAM_ENC*`, `APG*`, `DME6-9`, `VPG6-9`, and `DP_SYM32_ENC*` groups. Each instance has video control/timing, M/N, MSA timing/colorimetry, secondary-data packet controls, VSC/DSC/PPS payload areas, audio packet registers, DSC/DB control, DME/VPG controls, and 32-bit symbol encoder controls.
- HPO DP link encoders 0-1 and DP PHY symbol blocks: `DP_LINK_ENC*` and `DP_DPHY_SYM32*` control, status, training, PRBS, debug, FIFO, CRC, and DPCSTX data/clock-lane controls.
- `DCHVM`, `DLPC`, and `DPIA_MU0`: host-VM control/flush, low-power/control-status, DPIA doorbell, request, reply, and command data offsets.
- Azalia output/audio indirect spaces: function-2 codec registers, audio descriptor registers 0-13, sink-description registers 0-17, sink info, input/output CRC result registers, input endpoint root/function parameters, stream latency/FIFO indexes for streams 0-15, and output endpoint 0-7 codec endpoint registers.
- Azalia input endpoint 0-7 indexes: input converter capability/control registers, input pin capability/control registers, multichannel/HBR/channel-allocation/hot-plug/configuration-default/LPIB/input-status/infoframe indexes.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes the generated offset and shift/mask headers, then token-pastes names into register tables:

1. DCN 3.6 support includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h` from `dcn36_resource.c`, `irq_service_dcn36.c`, and `dmub_dcn36.c`.
2. Register-list macros such as `SR`, `SRI`, `SRII`, `SRII2`, `HWS_SF`, and stream-encoder/audio helper macros expand symbolic names into `BASE(reg..._BASE_IDX) + reg...` offsets and matching field masks/shifts.
3. Resource construction initializes DCN 3.6 tables for hardware sequencing, DIO, audio, stream encoders, clock/power control, VMID, IRQ handling, and DMUB service access.
4. Runtime paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT`; those helpers use these constants to address the correct DCN 3.6 MMIO or indirect register.
5. Sequencing for DSC programming, HDMI/DP stream enable, packet/audio setup, HPO link training, DPIA mailbox traffic, hotplug handling, and interrupt acknowledgement lives in the consumers. This generated header only supplies addresses.

The macro names are part of the ABI between AMD's generated register database and the handwritten display driver tables. A typo or offset drift here is usually not caught by types; it either fails at compile time when a referenced macro is missing or silently targets the wrong hardware register.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in memory or files. It describes hardware state reachable through DCN 3.6 direct MMIO and indirect index/data windows.

Represented hardware state includes DSC PPS/configuration and error telemetry, DSC interface/top/debug state, perfmon counter state, HPO output routing and clocking, HDMI FRL and stream/audio/infoframe packet state, DisplayPort stream timing/MSA/secondary-data/audio/DSC packet state, HPO DP link training and PHY symbol status, DCHVM host-VM flush/control state, DLPC low-power control/status, DPIA mailbox command/reply state, and Azalia codec/audio endpoint state.

Persistence is hardware-defined. Configuration registers usually retain programmed values until modeset reprogramming, stream teardown, clock/power gating, suspend/resume restore, GPU reset, or ASIC reset. Status, interrupt, error, counter, mailbox, sink, LPIB, CRC, and training registers may be read-only, sticky, write-one-to-clear, self-clearing, latched, or valid only while the relevant clock/power domain is enabled. This offset header does not encode those access semantics; consuming code and the hardware register specification must provide them.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.6.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h`, which provides matching field shifts and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c`, which includes this header pair and builds DCN 3.6 register, shift, and mask tables for resource-pool and hardware-sequencer use.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c`, which includes this header pair for DCN 3.6 IRQ source register initialization.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, which initializes DMUB-visible DCN 3.6 register offsets with `BASE(reg..._BASE_IDX) + reg...`.
- Shared DIO and stream-encoder helpers under `display/dc/dio` and `display/dc/dce`, which consume HPO/DP/HDMI/AFMT-style register names through token-pasted register-list macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`, whose Azalia endpoint register-list pattern maps endpoint index/data windows and codec capabilities onto generated `AZF0ENDPOINT` names.
- DSC helper code and register tables that consume `DSCC`, `DSCCIF`, and `DSC_TOP` offsets for programming PPS values, reading DSC state, and collecting compression diagnostics.

The most direct behavioral integration points for this slice are display compression setup, HPO HDMI/DP stream and link programming, HDMI/DP audio packetization, Azalia codec/endpoint discovery, DPIA communication, display low-power/host-VM control, and perfmon/debug telemetry.

## Risks And Edge Cases

- Generated offsets are untyped integer macros. A wrong value can compile cleanly while sending register reads/writes to the wrong block, wrong instance, or wrong indirect index.
- The range starts at an artificial boundary. `regDSCC2_DSCC_PPS_CONFIG2_BASE_IDX` is present without its matching offset macro in this chunk, so adjacent chunks are required for complete `DSCC2` coverage.
- Instance repetition is high-risk. DP stream encoders 0-3, APG/DME/VPG instances, endpoint 0-7 groups, and stream 0-15 groups are mechanically similar; a single instance-specific generator error can create connector-specific or stream-specific failures.
- HPO HDMI/DP offsets are sequencing-sensitive. Incorrect stream encoder, link encoder, symbol encoder, FRL, MSA, audio, infoframe, DSC/PPS, or generic-packet offsets can cause blank displays, bad link training, malformed packets, missing DSC enablement, or receiver-specific interoperability failures.
- Audio offsets affect both direct HDMI/DP packet generation and Azalia codec state. Incorrect AFMT, descriptor, sink-info, endpoint, HBR, multichannel, LPIB, hotplug, or input-status indexes can produce silent audio, wrong channel layout, bad sample-rate reporting, stale hotplug state, or broken position reporting.
- DSC and perfmon registers include status/counter/debug surfaces. Misaddressed error counters can hide compression faults or make diagnostics misleading even when normal modesets appear to work.
- DPIA mailbox and DCHVM/DLPC registers can have side effects. Wrong offsets can corrupt command/reply handshakes, host-VM flush behavior, low-power transitions, or interrupt/status acknowledgement.
- Base-index mismatches are as dangerous as offset mismatches. `*_BASE_IDX` values select the MMIO segment used by `BASE(...)`; a correct-looking register offset with the wrong base index can target a different address space.
- Access while a block is power gated or clock gated can hang, timeout, or return stale values. The header does not indicate which offsets require clocks, power domains, or reset deassertion.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display with DCN 3.6 enabled. Missing or renamed macros should fail in `dcn36_resource.c`, `irq_service_dcn36.c`, `dmub_dcn36.c`, and shared DIO/audio/stream-encoder table construction.
- Mechanically verify that each `reg*` offset in this range has the expected `reg*_BASE_IDX` pair, allowing the known chunk-boundary exception at the first line, and that all paired base indexes match the intended address block.
- Diff this range against AMD's authoritative DCN 3.6.0 register database and neighboring generated DCN headers where block layouts are expected to be compatible.
- Exercise DSC on every supported pipe/instance with compressed DisplayPort modes, DSC PPS programming, modeset/fast-modeset transitions, suspend/resume, and error telemetry reads.
- Exercise HPO HDMI FRL and HPO DP paths across link training, high bit rate modes, DSC, HDR/infoframe updates, generic packet sends, stream enable/disable, hotplug, MST/SST where applicable, and multi-display configurations.
- Validate HDMI/DP audio across plug/unplug, EDID/audio descriptor discovery, 2-channel and multichannel LPCM, HBR/compressed formats, sample-rate changes, mute/unmute, audio packet control, endpoint hotplug state, LPIB snapshots, and suspend/resume.
- Exercise DPIA paths with USB4/DP tunneling scenarios, mailbox request/reply traffic, virtual-link creation, unplug/replug, and error handling. Watch for command timeouts or mismatched reply data.
- Use register dumps or debug traces for representative `DSCC3`, `HPO_TOP`, `HDMI_*`, `DP_STREAM_ENC*`, `DP_LINK_ENC*`, `DPIA_MU0`, and `AZF0ENDPOINT*` offsets to confirm programmed addresses match expected base-index plus offset calculations.
- Monitor kernel logs for `REG_WAIT` timeouts, IRQ storms, missed hotplug/audio events, bad DSC state, link-training failures, FIFO/CRC/perfmon anomalies, and resume-only display or audio regressions.

## Cross-Chunk Notes

Earlier chunks contain the start of `dcn_3_6_0_offset.h`, including the beginning of `DSCC2` and the offset partner for this chunk's first `DSCC2` base-index macro. This chunk reaches the end of the file and closes the header guard. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.6.0 offsets or all repeated DSC, HPO, DPIA, and Azalia instances.
