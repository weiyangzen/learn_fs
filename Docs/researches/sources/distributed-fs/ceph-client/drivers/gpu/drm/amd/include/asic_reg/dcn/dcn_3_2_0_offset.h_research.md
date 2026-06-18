# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001923`: lines 1-2628, `Docs/researches/chunks/subset-b-001923_research.md`
- `subset-b-001924`: lines 2629-5158, `Docs/researches/chunks/subset-b-001924_research.md`
- `subset-b-001925`: lines 5159-7652, `Docs/researches/chunks/subset-b-001925_research.md`
- `subset-b-001926`: lines 7653-10193, `Docs/researches/chunks/subset-b-001926_research.md`
- `subset-b-001927`: lines 10194-12822, `Docs/researches/chunks/subset-b-001927_research.md`
- `subset-b-001928`: lines 12823-14737, `Docs/researches/chunks/subset-b-001928_research.md`

## Chunk Research

### subset-b-001923: lines 1-2628

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h lines 1-2628

## Scope And Purpose

This chunk is the first 2,628 lines of the DCN 3.2.0 display-core register offset header. It is generated-style hardware metadata for AMDGPU's Display Core Next 3.2 generation, not executable driver logic. The file defines `reg...` address-offset macros and matching `reg..._BASE_IDX` segment selectors for display clock generation, DMU/DMCUB, display writeback, MMHUBBUB, HDA/Azalia audio, DCHUBBUB memory arbitration, VM request handling, and the first two HUBP/HUBPREQ/HUBPRET/cursor instances.

The macros are consumed by DCN32 display and DMUB code through register-list expansion macros. Consumers combine `regFOO_BASE_IDX` with `ctx->dcn_reg_offsets[base_idx]` and then add `regFOO` to produce a final MMIO register address. In `display/dc/resource/dcn32/dcn32_resource.c`, macros such as `SR()`, `SR_ARR()`, `SRI()`, and `SRI_ARR()` expand these names into typed register tables for display components. In `display/dmub/src/dmub_dcn32.c`, `REG_OFFSET_EXP()` performs the same base-plus-offset expansion for DMUB service registers.

This chunk ends at `regCURSOR0_1_DMDATA_ADDRESS_LOW_BASE_IDX`; later lines in the same header continue with additional pipes and display blocks.

## Register Macro Shape

Each register is represented by two preprocessor constants:

- `regNAME`: the block-local register offset, for example `regDENTIST_DISPCLK_CNTL 0x0064`.
- `regNAME_BASE_IDX`: the index into the DCN register base table, commonly `1` for DCCG/display-decode blocks and `2` for most DC/DMU/HUBBUB/HUBP blocks; the VGA memory page registers at the start of the VGA section include base index `0`.

The source comments divide definitions into `addressBlock` groups and list each group's hardware base address. Those comments are important for humans auditing generated offsets, while driver code relies on the macro names and base-index values.

There are no C functions, structs, enums, static data, locks, or direct reads/writes in this header. The API surface is entirely macro symbols used by other headers and C files.

## Address Blocks Covered

The chunk defines these block families:

- DCCG and DCCG DFS: display clocking, pixel-clock resync, DP/DSC/DPP DTOs, clock gating controls, GTC, audio DTOs, vblank latch/counter controls, and soft reset.
- DMU and DMCUB: RBBM interface status, interrupt-hub status and destination registers, power-gating domains, DMCUB region windows, mailboxes, scratch registers, GPINT, firmware status, timer, instruction/cache controls, fault reporting, and debug/status registers.
- DWB0 and DWB color pipeline: display writeback enable, memory power, viewport/scaler, crop, capture rate, CRC, host-read and overflow status, plus output gamut remap and OGAM RAM A/B LUT programming registers.
- MMHUBBUB: VGA legacy aperture/control registers, VGA interface MCIF counters, MCIF writeback buffer and arbitration registers, writeback watermarks, warmup, memory power, clock/reset/status, and SMU watermark control.
- HDA/Azalia: controller clock/audio DTO/DMA/CRC/memory-power registers, root codec parameters and controls, stream index/data pairs for streams 0-15, output endpoint index/data pairs for endpoints 0-7, and input endpoint index/data pairs for endpoints 0-7.
- DCHUBBUB: arbitration watermarks for sets A-D, MALL control, global timer, surface check addresses, VTG controls, timeout detection, SDPIF VM aperture/security controls, ret-path CRC/DCC/DET/compbuf controls, and VM context/page-table/fault registers.
- HUBP/HUBPREQ/HUBPRET/cursor for pipes 0 and 1: surface layout and viewport registers, VMID and surface addresses, meta-surface addresses, flip controls, in-use/earliest-in-use latches, TTU/QoS/prefetch/nominal/flip/vblank timing parameters, memory power/status, read-line controls, cursor address/size/position/hotspot/memory power, and DMDATA addresses.

The block count is large but regular. For example, the DMCUB block contributes 123 registers, the DCHUBBUB VM request block contributes 118 registers, and each HUBPREQ instance contributes 85 registers. Pipe 1 repeats the pipe 0 HUBP/HUBPREQ/HUBPRET/cursor layout with `HUBP1`, `HUBPREQ1`, `HUBPRET1`, and `CURSOR0_1` prefixes.

## Important Integration Points

The most important consumers are the DCN32 resource and DMUB initialization layers:

- `dcn32_resource.c` includes this header with `dcn_3_2_0_sh_mask.h`, then expands component-specific register lists. `SR(AZALIA_CONTROLLER_CLOCK_GATING)`, `SR(DOMAIN0_PG_CONFIG)`, `SR(D1VGA_CONTROL)`, and similar entries rely on this chunk's offsets.
- `dmub_dcn32.c` initializes `struct dmub_srv_dcn32_regs` from this header. DMUB reset, backdoor-load, CW region setup, scratch polling, GPINT, and framebuffer-base translation depend on the DMCUB and VM macros defined here.
- `amdgpu/gmc_v11_0.c`, DCN32 IRQ service, GPIO factory/translation, and clock-manager code also include the header, so these offsets affect memory controller setup, interrupt routing, GPIO/DDC/HPD handling, and display-clock programming.
- The companion `dcn_3_2_0_sh_mask.h` supplies field masks and shifts for the same register names. Offset macros only identify register addresses; field-level operations such as `REG_GET`, `REG_UPDATE`, and `REG_SET_2` need the sh/mask header as well.

The naming convention is part of the ABI between generated hardware headers and hand-written DC code. A missing or renamed macro breaks compile-time expansion rather than failing at runtime.

## Control Flow

This header has no internal control flow. Runtime control flow appears in consumers:

- During DCN32 resource creation, register-list macros expand into register tables. Later component constructors pass those tables to common register helpers, so ordinary DC methods can use symbolic register names rather than raw addresses.
- During DMUB service initialization, `dmub_srv_dcn32_regs_init()` expands DMUB register and field lists, storing offsets, masks, and shifts in the DMUB service object.
- During runtime display programming, register helper macros use those stored offsets for MMIO reads/writes. Examples include DMUB firmware reset and region-window setup through `DMCUB_REGION3_CW*`, framebuffer address translation through `DCN_VM_FB_LOCATION_BASE` and `DCN_VM_FB_OFFSET`, and DCCG/HUBBUB/HUBP programming during modeset, flip, power, cursor, writeback, and audio operations.

Because this header is pure metadata, the effective behavior is an indirect control-flow dependency: incorrect offsets cause otherwise correct component code to access the wrong hardware register.

## State And Persistence Behavior

The header itself persists no state. Its macros describe hardware state locations:

- Clock and DTO registers preserve display clocking state while the display engine is active.
- DMCUB mailbox, scratch, GPINT, region-window, and fault registers hold live firmware communication and boot/runtime state.
- DCHUBBUB arbitration, watermark, MALL, VM context, and timeout registers hold memory-fetch policy and fault state across modeset and power-management transitions until rewritten or reset.
- HUBPREQ surface address, flip, in-use, prefetch, and timing registers represent per-plane scanout state and are updated around commits, page flips, and cursor updates.
- DWB and MCIF writeback registers hold capture/writeback pipeline state, buffer addresses, CRC state, overflow counters, and memory-power status.
- Azalia registers hold audio stream/controller state and endpoint/codec metadata for display audio paths.

Persistence is controlled by hardware reset, power gating, and explicit driver programming in consumers, not by this header.

## Dependencies

This chunk depends on the generated DCN register schema being synchronized with silicon and with companion headers:

- `dcn_3_2_0_sh_mask.h` must expose field names matching the register names used here.
- Register-list macros in DC component headers must use exact symbol names emitted here, including instance prefixes like `HUBPREQ0_`, `HUBPREQ1_`, and `CURSOR0_1_`.
- `ctx->dcn_reg_offsets[]` must provide valid base addresses for every `_BASE_IDX` value used by these macros.
- DCN32-specific C files must include this header before expanding register lists, otherwise generated symbols are unavailable.

No external libraries are involved; these are preprocessor constants compiled into the AMDGPU kernel driver.

## Risks And Edge Cases

The main risks are hardware-address correctness and generated-header drift:

- A wrong `reg...` value can redirect MMIO to a different hardware register, causing silent display corruption, hangs, failed firmware boot, bad watermark programming, VM faults, interrupt storms, or broken audio/writeback/cursor behavior.
- A wrong `_BASE_IDX` can be just as damaging as a wrong offset because the same local offset may be valid in multiple register spaces.
- Repeated instance blocks require exact naming. Pipe 1's `HUBPREQ1_*` offsets are not derived at runtime from pipe 0; they are explicit constants. Copy/paste or generator errors can break only one pipe.
- Legacy VGA definitions include overlapping offsets and different base indices, which is intentional for index/data style and legacy alias registers. Consumers must use the expected symbol rather than assuming one offset maps to one semantic register.
- The chunk mixes operational controls, status registers, interrupt destinations, address registers, and power controls. Tests that only compile the header cannot prove the values are electrically correct.
- Since the header is shared by DC and DMUB paths, changes can affect firmware boot/control and host display programming at the same time.

## Test Signals

Useful validation signals are layered:

- Build-time: AMDGPU/DCN32 compilation catches missing macro names, mismatched register-list names, and missing companion field-mask definitions.
- Boot/init: successful DCN32 display initialization and successful DMUB firmware reset/startup exercise the DMCUB, VM framebuffer-base, scratch, GPINT, and region-window offsets.
- Modeset and flip: multi-plane scanout, page flips, cursor updates, and multiple active pipes exercise HUBP/HUBPREQ/HUBPRET/cursor offsets for pipe 0 and pipe 1.
- Power management: display clock changes, clock gating, domain power gating, memory power status, MALL, and watermark transitions exercise DCCG, DMU/DC PG, DCHUBBUB, MMHUBBUB, HUBPREQ, and DWB memory-power registers.
- Interrupt handling: vblank, flip, HPD/DDC/AUX/audio/DMCUB/DMU/OTG interrupt routing and status handling exercise the IHC and interrupt-destination offsets.
- Display audio: HDMI/DP audio playback and stream enumeration exercise Azalia controller, root, stream, endpoint, and input-endpoint registers.
- Writeback/capture: DWB enable, viewport/scaler/crop, MCIF writeback buffers, CRC values, and overflow counters exercise the DWB and MCIF_WB sections.
- Fault/debug: VM fault reporting, timeout interrupt status, DMCUB fault addresses, DCHUBBUB CRC/DCC stats, and performance/debug counters provide diagnostic signals when offset programming is wrong.

No standalone unit test can fully validate this file. The strongest evidence comes from hardware-backed DCN32 integration tests, boot smoke tests on supported GPUs, display modeset/flip stress, suspend/resume, audio, cursor, writeback, and GPU VM fault-path testing.

### subset-b-001924: lines 2629-5158

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h lines 2629-5158

## Purpose

This chunk is generated AMD DCN 3.2.0 display-controller register offset metadata. It contains no executable C logic; it publishes preprocessor constants for MMIO register offsets (`reg...`) and their register-base selector indices (`reg..._BASE_IDX`). Consumers combine these offsets with `dcn_3_2_0_sh_mask.h`, `ctx->dcn_reg_offsets[]`, and AMD display register-helper macros to build typed register tables for DCN32 hardware blocks.

The requested range starts in the tail of the cursor/DMDATA register set for instance 1, covers the full HUBP/HUBPREQ/HUBPRET/cursor register sets for plane instances 2 and 3, covers DPP pipeline register sets for instances 0 through 3, covers MPC MPCC0 through MPCC3 and MPC common configuration, and ends in the first MPCC output-gamma block (`MPCC_OGAM0`). It defines 2,392 macros in this slice: 1,196 register-offset macros and 1,196 matching `_BASE_IDX` macros.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or direct MMIO accesses in this chunk. The exported interface is the generated macro namespace:

- `reg<REGISTER_NAME>`: register offset within a DCN32 register segment.
- `reg<REGISTER_NAME>_BASE_IDX`: index into `ctx->dcn_reg_offsets[]` for the segment base added to the offset.
- `// addressBlock: ...` and `// base address: ...`: generated grouping comments that identify repeated hardware blocks and their nominal base addresses.

The chunk uses base-index `2` for HUBP/DPP-side display pipeline blocks and base-index `3` for MPC-side compositor blocks. Runtime users compute absolute addresses with helper patterns such as `BASE(reg..._BASE_IDX) + reg...`, where `BASE()` resolves `ctx->dcn_reg_offsets[seg]`.

Major register groups in this range:

- Tail of `CURSOR0_1`: DMDATA control, QoS, status, software control, and software data registers for cursor/DMDATA instance 1.
- `HUBP2` and `HUBP3`: surface format/configuration, tiling, primary/secondary viewport geometry, luma/chroma request sizing, HUBP clock/control, VM page/MALL/SubVP controls, debug, measurement-window controls, and MALL status.
- `HUBPREQ2` and `HUBPREQ3`: plane fetch request registers for pitch, VMID, primary/secondary luma and chroma surface addresses, metadata surface addresses, surface and flip controls, flip interrupts, in-use and earliest-in-use addresses, TTU/QoS/watermark controls, VM aperture/TLB controls, blank/destination/prefetch/vblank/flip/nominal timing parameters, cursor delivery parameters, per-line delivery, ref-to-pixel frequency conversion, DRQ limits, memory power controls/status, UCLK p-state force, and HUBPREQ status registers.
- `HUBPRET2` and `HUBPRET3`: HUBP return/read-line controls, memory power controls/status, read-line values, interrupts, and read-line status.
- `CURSOR0_2` and `CURSOR0_3`: cursor control, surface address high/low, size, position, hot spot, stereo control, destination offset, cursor memory power controls/status, and DMDATA address/control/QoS/status/software registers.
- `CNVC_CFG0` through `CNVC_CFG3`: DPP canvas/format-conversion registers for surface pixel format, format control, floating-point bias/scale, color keyer controls and colors, 2-bit alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0` through `CNVC_CUR3`: DPP cursor overlay controls, cursor colors, and cursor floating-point scale/bias.
- `DSCL0` through `DSCL3`: scaler coefficient RAM select/data, scaler mode and taps, manual replication, horizontal/vertical scaling ratios and initial phases for luma/chroma, black color, update/autocal controls, overscan, OTG blank timing, recout/MPC sizing, line-buffer format/memory, counters, scaler memory power controls/status, and output-buffer controls.
- `CM0` through `CM3`: color-management controls, post-CSC matrices, gamut remap matrices, bias registers, gamma-correction LUT index/data/control, RAMA/RAMB piecewise-linear setup for RGB channels and regions, HDR multiplier coefficients, CM memory power controls/status, dealpha, coefficient format, and CM test/debug index/data.
- `DPP_TOP0` through `DPP_TOP3`: DPP control, soft reset, CRC values/control, and host read control.
- `MPCC0` through `MPCC3`: MPC compositor/blender plane-selection, OPP binding, MPCC control/state-machine control, update-lock selection, top/bottom gain, movable color-management placement, background color, memory power control, and status.
- MPC common config: clock control, soft reset, CRC control/selection/results, bypass background colors, host read control, DPP and miscellaneous pending status, per-pipe address/config/cursor vupdate lock sets, and DWB mux selection.
- `MPCC_OGAM0`: output gamma control, LUT index/data/control, RAMA/RAMB PWL control registers, region tables, gamut-remap coefficient format/mode, and A/B gamut-remap matrix coefficients. This chunk ends after `MPC_GAMUT_REMAP_C33_C34_B`, so later chunks must cover remaining MPCC OGAM instances or any following MPC registers.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by DCN32 display code:

1. DCN32 translation units include `dcn/dcn_3_2_0_offset.h` and `dcn/dcn_3_2_0_sh_mask.h`.
2. Register-list macros in resource and hardware-object code paste symbolic names into generated `reg...` and `reg..._BASE_IDX` names.
3. Helper macros such as `SR`, `SRI`, `SRI_ARR`, `SRII`, and related variants materialize per-block register tables by adding each generated offset to `ctx->dcn_reg_offsets[base_idx]`.
4. Constructed objects such as HUBP, DPP, MPC, IRQ/GPIO, clock-manager, and DMUB-facing components later perform the actual MMIO reads/writes through common register helpers.

The generated constants do not encode programming order. Consumers must still sequence hardware operations around modesets, plane updates, flips, cursor updates, scaler programming, color-management LUT loads, MPC blending-tree updates, update locks, memory power transitions, MALL/SubVP behavior, suspend/resume, reset, and debug/CRC capture.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in memory or files. It describes MMIO-backed GPU state. The represented hardware state includes:

- Plane-fetch state for HUBP/HUBPREQ instances 2 and 3: surface layout, tiling, addresses, metadata addresses, viewport geometry, VMID, VM aperture/TLB state, pitch, request sizing, prefetch/delivery/DRQ/TTU parameters, flip state, in-use addresses, and status.
- Cursor/DMDATA state for cursor instances 1 through 3: cursor image addresses, size/position/hotspot, stereo mode, memory power state, dynamic metadata transport addresses, software data paths, QoS, and status.
- DPP state for four pipeline instances: input format conversion, cursor blend/color controls, scaling coefficients and ratios, line-buffer/output-buffer configuration, color transforms, gamma/PWL LUTs, HDR multiplier coefficients, CRC/debug controls, and memory power controls/status.
- MPC state for four MPCC compositor instances: selected top/bottom sources, output processor assignment, blend/gain/background controls, update-lock routing, movable color-management placement, MPCC memory power state, and MPCC status.
- MPC common state: compositor clocks, reset, CRC capture, pending update status, per-pipe vupdate lock routing, host reads, bypass background, and DWB muxing.
- MPCC output gamma/gamut state for `MPCC_OGAM0`: output-gamma LUT bank/index/data/control, PWL region definitions, and gamut-remap matrix coefficients.

Persistence is hardware-defined. Programmed configuration usually survives until the next modeset, plane reprogramming, power-gating transition, suspend/resume, or ASIC reset. Status, interrupt, CRC, pending, flip, read-line, power-state, debug, and in-use address registers can be transient, latched, sticky, self-clearing, or timing-sensitive. This generated offset header only supplies addresses; it does not describe access type, reset value, volatility, or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.2.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h`, which supplies matching field shifts and masks.
- DCN32 `ctx->dcn_reg_offsets[]` base-address setup, because every `_BASE_IDX` macro is interpreted through that array.
- AMD display register-helper macros in `reg_helper.h` and DC hardware-object register-list macros that token-paste these generated names.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`

Important integration areas:

- `dcn32_resource.c` expands DPP, MPC, and HUBP register-list macros using these offsets while constructing DCN32 resource-pool objects. The resource pool creates HUBPs, DPPs, OPPs, timing generators, MPC/MPCC state, DSC, audio, stream encoders, and DMUB-related services around these tables.
- HUBP/HUBPREQ/HUBPRET offsets integrate with plane programming, surface flips, cursor fetch, VM setup, MALL/SubVP behavior, memory power management, bandwidth/watermark programming, and status/debug reads.
- DPP offsets integrate with format conversion, scaler setup, line-buffer programming, cursor blending, color pipeline programming, gamma/PWL LUT loading, HDR multiplier setup, CRC/debug capture, and DPP power/reset control.
- MPC/MPCC offsets integrate with layer composition, blending trees, secondary DPP pipe insertion/removal, MPCC update locks, 3D LUT/output-gamma placement, CRC capture, pending-update tracking, and writeback muxing.
- DMUB, IRQ, GPIO, and clock-manager code include the same generated header so firmware services, interrupt mapping, GPIO translation, and clock/register diagnostics use DCN32-correct addresses.

## Risks And Edge Cases

- Register drift is the central risk. These are untyped preprocessor constants, so an incorrect offset or `_BASE_IDX` can compile cleanly while directing MMIO to the wrong register or wrong register segment.
- The range starts mid-block in `CURSOR0_1` and ends mid-MPC color pipeline at `MPCC_OGAM0`. Adjacent chunks are required before making whole-file claims about all cursor instances or all MPCC output-gamma blocks.
- Repeated instances are copy-sensitive. HUBP2/HUBP3, DPP0-DPP3, DSCL0-DSCL3, CM0-CM3, and MPCC0-MPCC3 are structurally similar but instance-specific; a single wrong suffix or offset can affect only one pipe, making failures display-topology dependent.
- Base-index mistakes are high impact. HUBP/DPP registers in this chunk use base index `2`, while MPC registers use base index `3`; confusing those segments would produce valid-looking addresses in the wrong hardware block.
- Plane-fetch registers include GPU addresses and metadata addresses. Bad offsets can cause page faults, stale surfaces, corruption, hangs, wrong chroma plane fetches, DCC/meta failures, or security-sensitive reads from unintended memory.
- Flip, in-use, earliest-in-use, interrupt, and vblank parameter registers are timing-sensitive. Wrong offsets can cause missed flips, tearing, stuck flips, incorrect page-flip completion, or resume/modeset-only failures.
- QoS, TTU, prefetch, nominal/vblank/flip timing, DRQ, and UCLK p-state force registers are coupled to DML/watermark calculations. Misaddressing can show up as underflow, stutter, black screens under memory pressure, SubVP regressions, or power/performance anomalies.
- Cursor and DMDATA register errors can be user-visible as missing/misplaced cursors, wrong hotspot/stereo behavior, corrupted cursor images, bad dynamic metadata delivery, or status/QoS misreporting.
- Scaler and color-management offsets are visually sensitive. Wrong DSCL/CNVC/CM/OGAM/gamut-remap addresses can produce incorrect scaling, clipped or shifted color, broken HDR/SDR transforms, bad gamma ramps, or CRC mismatches.
- MPCC and MPC update-lock/composition registers affect blending-tree correctness. Errors can lead to wrong layer ordering, stale composition, bad split-pipe transitions, MPCC state-machine stalls, or changes that take effect on the wrong vupdate.
- Power-control/status registers can be read/write asymmetric or timing-sensitive. The offset header does not document required polling, delays, force bits, or safe access windows.

## Test Signals

Useful validation combines generated-header consistency checks and DCN32 display behavior:

- Build AMDGPU/DC with DCN32 support enabled. Missing or renamed macros should fail in `dcn32_resource.c`, `dcn32_clk_mgr.c`, `irq_service_dcn32.c`, `hw_factory_dcn32.c`, `hw_translate_dcn32.c`, `dmub_dcn32.c`, or shared register-list users.
- Mechanically verify that every register macro in lines 2629-5158 has a matching `_BASE_IDX` macro, and that HUBP/DPP-side entries use base index `2` while MPC-side entries use base index `3`.
- Diff this slice against AMD's authoritative DCN 3.2.0 register database and neighboring generated DCN headers where register layouts are expected to match.
- Exercise display modes using pipes 0 through 3, including single-plane, multi-plane, cursor, MPO/overlay, split-pipe, and secondary-DPP/MPCC composition scenarios.
- Stress page flips, cursor movement, hot cursor format/size changes, dynamic metadata paths, suspend/resume, DPMS, rapid modesets, and plug/unplug while watching for GPU page faults, underflow, missed vblank/page-flip events, stuck pending bits, or display corruption.
- Validate scaling and color paths with CRC-capable tests: identity scaling, up/down scaling, chroma formats, CSC/gamut-remap matrices, gamma ramps, HDR metadata/content, and MPCC OGAM/3D LUT placement.
- Exercise MALL/SubVP and memory-clock-sensitive scenarios, because HUBP/HUBPREQ timing, TTU, prefetch, and UCLK p-state registers directly affect latency tolerance and underflow behavior.
- Use register dumps or debugfs-style DC register inspection to confirm computed addresses for representative `HUBP2`, `HUBPREQ3`, `DPP_TOP0`, `CM3`, `MPCC2`, `MPC_CRC_CTRL`, and `MPCC_OGAM0` entries land in the expected DCN32 register segments.

## Cross-Chunk Notes

Previous chunks own the beginning of the cursor instance 1 block and earlier HUBP/DPP/MPC metadata. This chunk starts with only the DMDATA tail for `CURSOR0_1`.

Later chunks are needed for the rest of the MPC/MPCC output-gamma namespace after `MPCC_OGAM0_MPC_GAMUT_REMAP_C33_C34_B` and for any remaining generated register blocks in `dcn_3_2_0_offset.h`. The final per-file report should merge adjacent chunks before making complete claims about all DCN32 register offsets, all cursor instances, all HUBP/DPP instances, or the full MPC color pipeline.

### subset-b-001925: lines 5159-7652

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h lines 5159-7652

## Scope

This chunk is part of the generated DCN 3.2.0 register offset header used by the AMD display driver. It contains C preprocessor constants for MMIO register offsets and base-index selectors for a large middle slice of the display core register map. The covered source range is lines 5159-7652 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`.

The chunk is data-only: it exports `#define` macros and contains no C functions, structs, inline helpers, or runtime branches. Each hardware register has a pair of macros:

- `reg<REGISTER_NAME>`: the register offset within the ASIC register namespace.
- `reg<REGISTER_NAME>_BASE_IDX`: the base-address table index used by AMD display register access helpers.

The slice defines 2400 macros across these address blocks:

- `dcn_dc_mpc_mpcc_ogam1_dispdec`, `dcn_dc_mpc_mpcc_ogam2_dispdec`, and `dcn_dc_mpc_mpcc_ogam3_dispdec`: MPCC output gamma instances 1 through 3.
- `dcn_dc_mpc_mpcc_mcm0_dispdec` through `dcn_dc_mpc_mpcc_mcm3_dispdec`: MPCC multi-color-management instances 0 through 3.
- `dcn_dc_mpc_mpc_ocsc_dispdec`: MPC output mux, denormalization, and output color-space-conversion registers.
- `dcn_dc_opp_abm0_dispdec` through `dcn_dc_opp_abm3_dispdec`: adaptive backlight management instances 0 through 3.
- The beginning of output-pixel-processing pipe blocks: `DPG0`, `FMT0`, `OPPBUF0`, `OPP_PIPE0`, `OPP_PIPE_CRC0`, the corresponding instance-1 blocks, `DPG2`, and the first `FMT2` register pair.

The range starts at `regMPCC_OGAM1_MPCC_OGAM_CONTROL` and ends mid-block at `regFMT2_FMT_CLAMP_COMPONENT_R_BASE_IDX`. Earlier chunks cover preceding MPC/MPCC offsets, and later chunks must complete `FMT2` plus the remaining OPP/ODM/display blocks.

## Purpose

The purpose of this header slice is to provide the generated address side of the DCN 3.2.0 register contract for display color, composition, backlight, formatter, pattern-generator, buffer, and CRC blocks. Driver code includes this header so it can name hardware registers symbolically instead of embedding numeric offsets such as `0x0106`, `0x0790`, or `0x1891` at call sites.

These macros are normally consumed together with the matching shift/mask header for the same ASIC revision, likely `dcn_3_2_0_sh_mask.h`. The offset macro identifies the register, while the shift/mask macros identify fields inside that register. AMD display register helper macros then combine them with a base address table selected by `_BASE_IDX`.

This design keeps the runtime display code mostly hardware-revision-neutral. Higher-level DC code can build register lists for DCN 3.2.0 by referencing `reg...` macros, while shared logic uses common helper APIs to write values, poll status bits, and load LUT data.

## Important API Surface

The exported API is a generated macro namespace. There are no typed APIs, but the macro names themselves are an ABI-like contract with the rest of the AMD display driver.

### MPCC OGAM instances 1-3

`MPCC_OGAM1`, `MPCC_OGAM2`, and `MPCC_OGAM3` expose output gamma programming behind MPCC blocks. Each instance has the same shape and uses `_BASE_IDX 3`, indicating the MPC/MPCC register base table entry. The block includes:

- `MPCC_OGAM_CONTROL`: top-level output gamma control.
- `MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM_LUT_DATA`, and `MPCC_OGAM_LUT_CONTROL`: indexed LUT load and access control registers.
- `MPCC_OGAM_RAMA_*` and `MPCC_OGAM_RAMB_*`: two RAM banks for piecewise output gamma curves. Each bank has per-channel start controls, start slope controls, start base controls, end controls, offsets, and region tables from `REGION_0_1` through `REGION_32_33`.
- `MPCC_GAMUT_REMAP_COEF_FORMAT`, `MPCC_GAMUT_REMAP_MODE`, and `MPC_GAMUT_REMAP_Cxx_Cyy_[AB]`: gamut-remap matrix coefficient format, mode, and A/B coefficient banks.

These macros are the register-address half of output gamma and per-MPCC gamut-remap programming. The duplicate OGAM shapes for instances 1, 2, and 3 differ only by register offset and instance prefix.

### MPCC MCM instances 0-3

`MPCC_MCM0` through `MPCC_MCM3` expose multi-color-management/shaper registers for each MPCC MCM instance. Each instance also uses `_BASE_IDX 3`. The block is larger than OGAM and includes:

- `MPCC_MCM_SHAPER_CONTROL`, per-channel offsets and scales, `MPCC_MCM_SHAPER_LUT_INDEX`, `MPCC_MCM_SHAPER_LUT_DATA`, and `MPCC_MCM_SHAPER_LUT_WRITE_EN_MASK`.
- `MPCC_MCM_SHAPER_RAMA_*` and `MPCC_MCM_SHAPER_RAMB_*`: two shaper RAM banks with per-channel start and end controls plus region tables.
- `MPCC_MCM_3DLUT_MODE`, `MPCC_MCM_3DLUT_INDEX`, and `MPCC_MCM_3DLUT_DATA`: 3D LUT programming entry points.
- `MPCC_MCM_3DLUT_DLG_ADJUST*` and `MPCC_MCM_3DLUT_DLG_CONTROL`: de-gamma or distribution/log-grid adjustment controls for the 3D LUT path.
- `MPCC_MCM_3DLUT_LUT_CONTROL`, `MPCC_MCM_3DLUT_READ_WRITE_CONTROL`, `MPCC_MCM_3DLUT_OFFSET`, `MPCC_MCM_3DLUT_SCALE`, `MPCC_MCM_3DLUT_DEBUG`, `MPCC_MCM_3DLUT_CONTROL`, `MPCC_MCM_3DLUT_STATUS`, and `MPCC_MCM_3DLUT_TEST_DEBUG_INDEX/DATA`: LUT access, scaling, debug, status, and test/debug register addresses.
- `MPCC_MCM_CONTROL`, `MPCC_MCM_TEST_DEBUG_INDEX`, `MPCC_MCM_TEST_DEBUG_DATA`, `MPCC_MCM_OUT_ROUND_CONTROL`, `MPCC_MCM_OUT_ROUND_OFFSET`, `MPCC_MCM_DEBUG_MISC`, and `MPCC_MCM_MEM_PWR_CTRL`: top-level enable/debug/output rounding/memory power controls.

This is the most substantial macro family in the chunk. It covers the MMIO addresses used for shaper LUTs, 3D LUT programming, output rounding, and memory power control in the MPCC color pipeline.

### MPC output mux and output CSC

`dcn_dc_mpc_mpc_ocsc_dispdec` uses `_BASE_IDX 3` and defines output-stage MPC registers:

- `MPC_OUT0_MUX` through `MPC_OUT3_MUX`: output mux selection for four MPC outputs.
- `MPC_OUT[0-3]_DENORM_CONTROL`, `MPC_OUT[0-3]_DENORM_CLAMP_G_Y`, and `MPC_OUT[0-3]_DENORM_CLAMP_B_CB`: output denormalization and clamp controls.
- `MPC_OUT_CSC_COEF_FORMAT`: coefficient format for output CSC matrices.
- `MPC_OUT[0-3]_CSC_MODE`: per-output CSC mode control.
- `MPC_OUT[0-3]_CSC_C11_C12_A` through `MPC_OUT[0-3]_CSC_C33_C34_B`: per-output color-space-conversion matrix coefficients, with A and B coefficient banks.

These offsets are the MPC-side registers used when routing composed display data into output pipes and applying final output color-space conversion.

### ABM instances 0-3

`ABM0` through `ABM3` use `_BASE_IDX 3` and expose adaptive backlight management and histogram/luma-statistics register addresses. Each instance contains:

- `BL1_PWM_AMBIENT_LIGHT_LEVEL`, `BL1_PWM_USER_LEVEL`, `BL1_PWM_TARGET_ABM_LEVEL`, `BL1_PWM_CURRENT_ABM_LEVEL`, `BL1_PWM_FINAL_DUTY_CYCLE`, and `BL1_PWM_MINIMUM_DUTY_CYCLE`: PWM and brightness level inputs/outputs.
- `BL1_PWM_ABM_CNTL`, `BL1_PWM_BL_UPDATE_SAMPLE_RATE`, and `BL1_PWM_GRP2_REG_LOCK`: ABM PWM control, sample-rate, and register-lock addresses.
- `DC_ABM1_CNTL` and `DC_ABM1_IPCSC_COEFF_SEL`: ABM control and input CSC coefficient selection.
- `DC_ABM1_ACE_OFFSET_SLOPE_0` through `_4`, `DC_ABM1_ACE_THRES_12`, `DC_ABM1_ACE_THRES_34`, and `DC_ABM1_ACE_CNTL_MISC`: ambient contrast enhancement curve and threshold controls.
- `DC_ABM1_HGLS_REG_READ_PROGRESS`, `DC_ABM1_HG_MISC_CTRL`, `DC_ABM1_HG_SAMPLE_RATE`, and `DC_ABM1_LS_SAMPLE_RATE`: histogram/luma-statistics control and progress registers.
- `DC_ABM1_LS_SUM_OF_LUMA`, `DC_ABM1_LS_MIN_MAX_LUMA`, `DC_ABM1_LS_FILTERED_MIN_MAX_LUMA`, `DC_ABM1_LS_PIXEL_COUNT`, `DC_ABM1_LS_MIN_MAX_PIXEL_VALUE_THRES`, `DC_ABM1_LS_MIN_PIXEL_VALUE_COUNT`, and `DC_ABM1_LS_MAX_PIXEL_VALUE_COUNT`: luma statistic readback registers.
- `DC_ABM1_HG_BIN_*` and `DC_ABM1_HG_RESULT_1` through `DC_ABM1_HG_RESULT_24`: histogram bin configuration and result readbacks.
- `DC_ABM1_BL_MASTER_LOCK`: ABM/backlight master lock register.

These macros are used by backlight, power, and image-quality code paths that configure automatic brightness and query frame-derived statistics.

### OPP DPG/FMT/OPPBUF/pipe/CRC start

The end of the chunk begins OPP register coverage. These blocks use `_BASE_IDX 2`, distinguishing the OPP base table from the MPC/ABM base table:

- `DPG0`, `DPG1`, and `DPG2`: display pattern generator control, ramp control, dimensions, RGB/YCbCr color registers, offset segment, and status.
- `FMT0` and `FMT1`: formatter clamp component registers, dynamic expansion, control, bit-depth control, dither random seeds, clamp control, side-by-side stereo control, 4:2:0 memory control, and 4:2:2 control.
- `FMT2`: only `FMT_CLAMP_COMPONENT_R` appears in this chunk; the rest of FMT2 is in the next chunk.
- `OPPBUF0` and `OPPBUF1`: OPP buffer control, 3D parameter registers, and secondary control.
- `OPP_PIPE0` and `OPP_PIPE1`: OPP pipe control.
- `OPP_PIPE_CRC0` and `OPP_PIPE_CRC1`: CRC control, mask, and result registers.

The OPP macros are used during pipe bring-up, formatter programming, test-pattern generation, buffer configuration, and CRC validation.

## Control Flow and Runtime Behavior

This header has no executable control flow. The effective control flow appears in caller code that uses these offsets in register sequences. The macro layout reveals several important sequencing patterns:

- LUT programming uses index/data/control triplets. OGAM, MCM shaper, and MCM 3D LUT paths all expose indexed access registers. Runtime code must set an index, write or read data, and use control/status bits from the paired shift/mask header to manage the transaction.
- Dual-bank programming is a recurring pattern. OGAM and MCM shaper curves have `RAMA` and `RAMB` register families; gamut remap and output CSC matrices also expose A/B coefficient banks. Driver code can stage a new curve or matrix in one bank while the other is active, then flip hardware selection at a synchronized point.
- Instance replication drives loop-based register-list construction. OGAM instances 1-3, MCM instances 0-3, ABM instances 0-3, and OPP instances are structurally repeated. Higher-level AMD DC code normally selects the instance by pipe or MPCC index and then uses a per-instance register table populated from these macros.
- ABM statistics are hardware-produced state. Histogram and luma-statistics result registers are readbacks derived from displayed frames. Callers must program sample rates and wait for valid frame/statistic periods before treating the values as current.
- OPP CRC is a programmed measurement path. Callers configure CRC control/mask, wait for result availability according to field semantics in the shift/mask header, and read `RESULT0`, `RESULT1`, and `RESULT2`.
- DPG and FMT programming participates in mode-set sequencing. Pattern generator dimensions/colors, formatter bit depth, dither seeds, clamp settings, stereo/420/422 controls, and OPP buffer registers are normally written before enabling or validating an output pipe.

Because this is an offset header, the macros do not encode whether a register is read-only, write-only, status, clear-on-write, latched, or double-buffered. Those semantics are provided by hardware documentation, the matching field header, and the calling DC code.

## State and Persistence Behavior

The macros themselves are compile-time constants and have no persistence. The hardware registers they address represent volatile ASIC state:

- Color pipeline configuration persists in the display engine until rewritten, reset, power-gated, or reinitialized by a mode set. This includes OGAM curves, MCM shaper/3D LUT state, gamut remap matrices, MPC output CSC matrices, formatter state, and OPP buffer controls.
- Indexed LUT contents are hardware memory state. Writes to `*_LUT_DATA` or `*_3DLUT_DATA` update internal LUT RAM rather than ordinary CPU memory. The corresponding index/control/status registers define how persistent those writes are across power transitions.
- ABM brightness levels and ACE configuration are hardware configuration, while luma and histogram result registers are live measurement/readback state.
- Lock registers such as `BL1_PWM_GRP2_REG_LOCK` and `DC_ABM1_BL_MASTER_LOCK` imply grouped or synchronized updates. Incorrect sequencing can leave shadow values pending or expose partially updated brightness configuration.
- Memory power control registers in MCM (`MPCC_MCM_MEM_PWR_CTRL`) can affect retention or availability of color-management RAM blocks. Callers must coordinate power gating with LUT programming and enable state.
- OPP CRC result registers are transient validation state. They should be treated as tied to a programmed capture interval and current pipe contents, not as persistent configuration.

The `_BASE_IDX` value is also state-adjacent in the register access model. `_BASE_IDX 3` is used throughout the MPC/MPCC/ABM blocks in this chunk, while `_BASE_IDX 2` is used for OPP blocks. A wrong base index can make a correct offset target the wrong register aperture.

## Dependencies and Integration Points

This file depends on the generated AMD DC register naming convention. The key dependencies are:

- The matching DCN 3.2.0 shift/mask header, which provides field-level constants for these same register names.
- AMD display register access helpers that accept register offsets and base indices, commonly through generated register-list structures and macros.
- DCN 3.2.0 hardware sequencing code that populates per-block register tables for MPC, MPCC, ABM, OPP, and color-management components.
- Build configuration that selects the DCN 3.2.0 register set only for ASICs whose register layout matches this generated header.

Important integration points include:

- MPCC and MPC color-management code that loads OGAM curves, shaper LUTs, 3D LUTs, gamut remap matrices, denormalization clamps, and output CSC matrices.
- Hardware sequencer and resource code that builds pipe-specific register lists for MPCC/MPC/OPP instances during mode set, stream enable, pipe split, and plane composition.
- ABM/backlight code that controls PWM levels, automatic brightness, ACE parameters, histogram/luma sampling, and master lock behavior.
- Debug and validation code paths that use DPG test patterns and OPP pipe CRC readbacks to verify pixel pipeline behavior.
- Formatter paths that program bit depth, dithering, clamp, stereo, 4:2:0, and 4:2:2 behavior before pixels leave the display pipe.

The repeated instance layout makes this header sensitive to code generation consistency. Register lists in runtime code often assume that instance `n` has the same semantic registers as instance `n+1` with only address and prefix changes.

## Risks and Edge Cases

- Generated offset drift is high impact. If a single numeric offset is wrong, the driver can write a valid-looking register macro to the wrong hardware address, causing color corruption, black screen, backlight misbehavior, or hard-to-debug display hangs.
- `_BASE_IDX` mismatches are as dangerous as wrong offsets. Most of this chunk uses base index 3, but the OPP section switches to base index 2. Mixing these in a register table would redirect otherwise correct offsets.
- Chunk boundaries split logical hardware blocks. This chunk starts at OGAM1 rather than OGAM0 and ends after only the first FMT2 register pair. Any final per-file research must reconcile adjacent chunks before claiming whole-file coverage of OGAM, FMT, or OPP instance sets.
- Repeated blocks invite copy/paste or generator skew. OGAM1-3, MCM0-3, ABM0-3, and OPP0-2 follow similar patterns. A single missing register or wrong instance prefix can affect only one pipe and escape broad compile checks.
- Indexed LUT registers require strict ordering. Writing data before setting the index/control register, using the wrong bank, or ignoring hardware status can corrupt gamma/shaper/3D-LUT contents.
- Color matrix A/B banks and RAMA/RAMB banks can be confused. Callers must know which bank is active and whether update selection is double-buffered before switching curves or matrices during a live frame.
- ABM has mixed configuration and readback registers. Histogram/luma result registers, read-progress registers, lock registers, and brightness level registers have different semantics; generic read-modify-write patterns can be wrong if field-level clear, latch, or lock behavior is ignored.
- Some OPP state is validation-only or mode-test-only. DPG and CRC registers may be compiled into production drivers but primarily used by tests, debugfs paths, or diagnostics. Incorrect enable sequencing can interfere with normal frame output.
- ASIC specificity matters. DCN 3.2.0 offsets should not be reused for other DCN generations even when register names look similar.

## Test Signals

Useful signals for validating code that consumes this chunk include:

- Compile coverage for DCN 3.2.0 display code, proving each referenced `reg...` macro and `_BASE_IDX` macro resolves with the expected generated name.
- Register-list construction tests or build-time checks that ensure MPC/MPCC/ABM register tables use base index 3 and OPP register tables use base index 2.
- Color-management tests that load OGAM curves for MPCC instances 1-3, MCM shaper LUTs and 3D LUTs for MPCC MCM instances 0-3, then verify expected output through CRC or visual pipeline validation.
- Gamut remap and output CSC tests that program A/B coefficient banks for MPCC and MPC output paths, switch modes, and confirm no stale bank is used.
- Backlight and ABM tests that update user/target/current/final PWM levels, configure ACE thresholds/slopes, collect histogram and luma statistics, and verify lock/update behavior does not leave stale values.
- OPP pipe tests that use DPG generated patterns, FMT bit-depth/dither/clamp settings, OPP buffer configuration, and `OPP_PIPE_CRC0/1` result registers to validate known pixel outputs.
- Multi-pipe tests across at least four MPC/ABM instances and the visible OPP instances to catch one-instance register offset or prefix mistakes.
- Power-management tests around `MPCC_MCM_MEM_PWR_CTRL` that verify LUT contents and color behavior across memory power state changes.

## Open Questions for Merge

- The chunk does not include OGAM0, so the final per-file report should check adjacent chunks to determine whether OGAM0 has the same register family and how instances are ordered.
- The FMT2 block is split after `FMT_CLAMP_COMPONENT_R`; later chunk research must complete FMT2 and likely cover additional FMT/OPP instances.
- This offset header should be reconciled with the matching `dcn_3_2_0_sh_mask.h` chunks to distinguish ordinary configuration registers from read-only status, clear-on-write, double-buffered, or indexed access registers.

### subset-b-001926: lines 7653-10193

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h lines 7653-10193

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.2.0 register-offset header. It contains C preprocessor constants only: `reg...` symbols for MMIO register offsets and matching `reg..._BASE_IDX` symbols used by the Display Core register-access helpers. There are no functions, structs, enums, branches, loops, allocations, locks, or software-owned state objects in this range.

The chunk starts in the middle of the OPP/FMT2 register block at `regFMT2_FMT_CLAMP_COMPONENT_G` and ends in the middle of the DIG4 HDMI audio-clock-recovery block at `regDIG4_HDMI_ACR_44_0`. Within those boundaries it covers the later OPP pipe/output formatter registers, ODM/OPTC input and timing-generator registers, HPD interrupt/control registers, and five DisplayPort/DIG link encoder instances. The constants are hardware ABI: they bind DCN32 display code to concrete register addresses for modeset timing, output-pixel formatting, hotplug handling, stream encoding, link training, DisplayPort secondary-data packets, HDMI packets, CRC/debug readback, and related power/clock controls.

The range contains 2,393 `#define` lines: 1,197 register-offset macros and 1,196 `_BASE_IDX` macros. Almost every register offset has a paired base-index macro. The one-count difference is due to the chunk boundary starting after `regFMT2_FMT_CLAMP_COMPONENT_R_BASE_IDX` and before `regFMT2_FMT_CLAMP_COMPONENT_G`.

## Hardware Surface Covered

The first portion finishes output-pixel-processor coverage for pipe instances 2 and 3:

- `FMT2` and `FMT3` formatter registers for clamp components, dynamic expansion, bit depth, dither seeds, clamp control, side-by-side stereo, 4:2:0 memory mapping, and 4:2:2 handling.
- `OPPBUF2` and `OPPBUF3` output buffer control and 3D parameter registers.
- `OPP_PIPE2` and `OPP_PIPE3` pipe-control registers.
- `OPP_PIPE_CRC2` and `OPP_PIPE_CRC3` CRC control, mask, and result registers.
- `DPG3` display pattern generator control, ramp, dimensions, color, offset, and status.
- `DSCRM0` through `DSCRM3` DSC forward-configuration registers.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL` top-level OPP clock and ABM control surfaces.

The middle portion covers OPTC/ODM display timing and composition input:

- `ODM0` through `ODM3` input global control, data-source select, data-format control, bytes-per-pixel, width control, input clock, memory config, and spare registers.
- `OTG0` through `OTG3`, each with 104 offset macros for horizontal/vertical timing, blanking, sync, total/min/max/mid, trigger controls, stereo/interlace, pixel readback, status/counters, vertical interrupts, CRC windows/data/masks, static screen detection, 3D structure, global sync lock/control, GSL windows, VUPDATE keepout, DRR timing/control, DTO, request control, DSC start position, pipe update status, and spare registers.
- `GSL_SOURCE_SELECT`, `GSL_GROUP_ENABLE`, `GSL_MASTER_UPDATE_LOCK`, and OPTC misc/debug/spare registers.

The last portion covers DIO hotplug and stream/link encoder registers:

- `HPD0` through `HPD4` hotplug interrupt status, RX interrupt timer, RX interrupt control, HPD control, and toggle filter control.
- `DP0` through `DP4`, each with 83 DisplayPort register offsets. These include link control, training pattern selection, voltage/pre-emphasis pattern controls, DPHY control/status/CRC/fast-training, MSA timing and colorimetry, video M/N and stream controls, secondary-data packet controls, audio M/N, timestamps, MST/MSE rate and slot-allocation registers, DSC/MSO controls, metadata transmission, ALPM and AUX-less ALPM registers, generic SDP controls, and DP database controls.
- `DIG0` through `DIG3`, each with 53 stream encoder register offsets for DIG front-end control, output CRC/test patterns, FIFO controls, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic-packet controls, guard-band control, AFMT control, backend enable/control, TMDS controls, stereosync, sync character patterns, clock control, and force-disable.
- `DIG4` is partial in this chunk. It starts at `regDIG4_DIG_FE_CNTL` and reaches `regDIG4_HDMI_ACR_44_0`; its later HDMI ACR, AFMT, backend, TMDS, clock, and force-disable definitions continue after line 10193.

## Important Macros And API Shape

The exported API is the generated macro namespace consumed by DCN32 resource tables:

- `reg<INSTANCE>_<REGISTER>` gives the register offset value, for example `regOTG0_OTG_H_TOTAL`, `regODM0_OPTC_INPUT_GLOBAL_CONTROL`, `regDP0_DP_LINK_CNTL`, `regDIG0_DIG_FE_CNTL`, and `regHPD0_DC_HPD_INT_STATUS`.
- `reg<INSTANCE>_<REGISTER>_BASE_IDX` gives the register base index used by low-level MMIO helpers to select the right address space/base. In this chunk the display engine blocks use base index `2`.
- Address-block comments document the generated hardware block grouping and base address for each repeated instance.
- The register-offset header must be paired with the matching `dcn_3_2_0_sh_mask.h` field layout. Offset macros locate registers; shift/mask macros describe fields inside those registers.

The main instance families are regular and index-driven:

- OPP/FMT/DPG/OPPBUF definitions are used to build per-OPP register tables.
- ODM/OTG definitions are used to build per-OPTC register tables.
- HPD definitions are used to build per-connector hotplug GPIO/register tables.
- DP and DIG definitions are used to build link encoder and stream encoder register tables.

The chunk has partial boundaries. `FMT2` lacks the preceding `FMT_CLAMP_COMPONENT_R` line in this work item, and `DIG4` lacks the final part of the instance. Merge/reconciliation should combine neighboring chunks before treating those blocks as complete.

## Control Flow And State Behavior

This header has no executable control flow. Runtime flow is table-driven:

1. DCN32 resource code includes `dcn/dcn_3_2_0_offset.h`.
2. Register-list macros such as `OPP_REG_LIST_DCN30_RI(id)`, `OPTC_COMMON_REG_LIST_DCN3_2_RI(inst)`, `HPD_REG_LIST_RI(id)`, `SE_DCN32_REG_LIST_RI(id)`, and `LE_DCN31_REG_LIST_RI(id)` expand to generated register-offset symbols from this header.
3. Resource initialization fills register-address structures such as `dcn20_opp_registers`, `dcn_optc_registers`, `dcn10_link_enc_hpd_registers`, `dcn10_stream_enc_registers`, and `dcn10_link_enc_registers`.
4. Display Core objects perform read/write or read/modify/write operations through those tables, while companion shift/mask tables determine bit packing.
5. Hardware latches configuration or exposes status through the addressed registers.

The state represented by this chunk is hardware state, not persistent software state. Persistent or semi-persistent hardware configuration includes timing generator totals/sync/blanking, ODM input source and pixel format, OPP formatter bit depth/dither/clamp setup, DSC forwarding selection, DP link/training/MSA/video-stream controls, HDMI packet and audio clock-regeneration configuration, HPD filtering/control, and clock/power gating settings. Volatile state includes OTG frame/count/status readbacks, CRC results, HPD interrupt status, DP DPHY status/CRC/fast-training status, MSE status, HDMI status, DIG output CRC results, and debug/readback registers.

The macros do not encode sequencing, access width, polling requirements, clear-on-write behavior, or read-only/write-only semantics. Callers must still observe modeset locks, link-training order, vblank/update-lock sequencing, HPD interrupt rules, and register field preservation.

## Dependencies And Integration Points

Primary local users include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`, which includes this offset header and initializes DCN32 register tables for AFMT, stream encoders, HPD, link encoders, OPP, and OPTC.
- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h`, which defines the `*_RI` register-list macros that expand to register-offset/base-index symbols from this generated header.
- `drivers/gpu/drm/amd/display/dc/opp/dcn20` and `display/dc/dcn30/dcn30_opp.h`, which define OPP/DPG register structures and field tables consumed by `OPP_REG_LIST_DCN30_RI(id)`.
- `drivers/gpu/drm/amd/display/dc/optc/dcn30` and related OPTC code, which consume the OTG/ODM timing, update-lock, CRC, DRR, and GSL registers exposed through `OPTC_COMMON_REG_LIST_DCN3_2_RI(inst)`.
- `drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`, which defines link encoder register and field lists for DP/DIG link-control surfaces.
- `drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.h` and stream encoder code, which integrate HDMI/DP packet, audio, metadata, MSA, and DIG front-end registers.
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c` and IRQ code, which include this header for HPD and interrupt register mapping.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`, `display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/gpio/dcn32/*`, and `amdgpu/gmc_v11_0.c`, which also include the DCN32 generated offset header for low-level DCN32 register access or service initialization.

These offsets are meaningful only in combination with the matching generated shift/mask header and the DCN register access macros (`SR`, `SRI`, `SR_ARR`, `SRI_ARR`, and related RI variants). A compile can succeed with wrong numeric offsets, so behavioral validation matters as much as symbol presence.

## Risks And Maintenance Notes

- Numeric drift from the authoritative DCN 3.2.0 register database is the main risk. A wrong offset or base index can program the wrong MMIO register while still compiling.
- Repeated instances are easy to corrupt during generation or manual patching. Swapping `DP2`/`DP3`, `DIG3`/`DIG4`, `OTG1`/`OTG2`, or `ODM` instance numbers would misroute a display pipe or link encoder.
- This chunk starts inside `FMT2` and ends inside `DIG4`; final per-file research should not infer complete FMT2 or DIG4 coverage from this chunk alone.
- OTG/ODM registers are modeset-critical. Incorrect timing, blanking, sync, update-lock, DRR, or DSC-start-position offsets can cause blank screens, page-flip stalls, tearing, underflow, or timing interrupts in the wrong place.
- DP/DIG registers are link-critical. Incorrect link-control, training, DPHY, MSA, DSC, metadata, ALPM, or HDMI packet offsets can break link training, MST allocation, DSC streams, audio, HDR/metadata packets, or low-power entry/exit.
- HPD registers are interrupt-sensitive. Misaddressed status/control/toggle-filter registers can cause missed hotplug events, interrupt storms, or failure to debounce RX/HPD transitions.
- CRC and status registers are often used for diagnostics and automated tests. Wrong offsets can make validation tools report false failures or mask real display corruption.
- `_BASE_IDX` values are part of the address calculation contract. Treating them as boilerplate can break access on blocks that share names but live under different register bases.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build coverage for AMDGPU Display Core with DCN32 enabled. This catches missing or malformed generated symbols used by resource table expansion.
- Generated-header comparison against the authoritative DCN 3.2.0 register specification, with special attention to repeated `OTG0..3`, `ODM0..3`, `HPD0..4`, `DP0..4`, and `DIG0..4` instance strides.
- Boot and modeset smoke tests on DCN32 hardware with all available pipes: single-display, multi-display, clone/extend, resolution and refresh-rate changes, suspend/resume, and page-flip stress.
- DisplayPort link-training tests across lane counts/rates, MST and SST, DSC enabled/disabled, fast training, ALPM/AUX-less ALPM, and retraining after hotplug.
- HDMI tests covering video modes, audio clock regeneration, infoframes, generic packets, metadata packets, and TMDS/DIG backend enable/disable.
- HPD tests for plug/unplug, short pulses, RX interrupt handling, debounce/toggle filtering, and interrupt storm resistance.
- CRC/debug tests using OPP pipe CRC, OTG CRC windows/data, DP DPHY CRC, and DIG output CRC to confirm register dumps and validation tooling read the intended blocks.
- Variable refresh/DRR and vblank/update-lock tests, since this chunk includes OTG vertical interrupt, DRR, master update lock, GSL, and timing-status registers.

## Open Questions For Merge

- Merge should connect this chunk to the previous FMT2/OPP blocks and the next DIG4 continuation so partial-boundary blocks are described accurately at the per-file level.
- The final report should distinguish DCN32 legacy stream/DIG/DP encoder coverage from HPO DP encoder coverage, because this chunk covers the DP/DIG path while DCN32 resource code also initializes HPO-specific tables outside this address range.

### subset-b-001927: lines 10194-12822

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h lines 10194-12822

## Scope

This chunk is part of the generated DCN 3.2.0 register offset header used by the AMD display driver. It covers the middle of the DCN32 display register map, starting in the tail of the legacy `DIG4` HDMI/TMDS register block and ending at the first register of the HPO DP stream encoder 3 DME block. The range contains 2,369 `#define` lines: 1,184 register-offset macros plus 1,185 `_BASE_IDX` macros. The extra base-index line is the opening `regDIG4_HDMI_ACR_44_0_BASE_IDX`, whose register macro is in the previous chunk.

The covered address blocks are:

- Legacy DIO output sideband/audio blocks: `AFMT0` through `AFMT4`, `DME0` through `DME4`, `VPG0` through `VPG4`, and the tail of `DIG4`.
- AUX/DDC and DIO/DCIO support: `DP_AUX0` through `DP_AUX4`, DOUT I2C, DIO misc/link controls, DCIO generics, GPIO/DDC/HPD/PWRSEQ/AUX pad controls, and `DCIO_UNIPHY0` through `DCIO_UNIPHY4` reserved macro-control registers.
- Embedded-panel and compression blocks: `PWRSEQ0`, `DSC_TOP0..3`, `DSCCIF0..3`, and `DSCC0..3`.
- HPO stream-output blocks: HPO top, DP stream mapper, HPO HDMI stream encoder 0 sideband blocks (`AFMT5`, `DME5`, `VPG5`), full HPO DP stream encoder instances 0 through 2 (`DP_STREAM_ENC`, `APG`, `DME`, `VPG`, `DP_SYM32_ENC`), and the start of HPO DP stream encoder instance 3 (`DP_STREAM_ENC3`, `APG3`, `DME9_DME_CONTROL`).

The file has no executable C code. Its purpose is to provide ASIC-specific symbolic MMIO offsets and register-base-index selectors for DCN 3.2.0. Runtime code combines these macros with companion field shift/mask macros from `dcn_3_2_0_sh_mask.h`.

## Important API Surface

The API surface is the generated macro namespace:

- `reg<block>_<register>` expands to a register offset.
- `reg<block>_<register>_BASE_IDX` expands to the register base index used by AMD register helpers. Most macros in this slice use base index `2`; the HPO HDMI stream encoder 0 and HPO top/mapper registers use base index `3`.

Important register families in this chunk include:

- `regDIG4_*`: HDMI audio clock regeneration (`HDMI_ACR_*`), AFMT backend coupling, DIG backend enable/control, TMDS control characters, DC balancer controls, DIG version, and forced DIG disable for legacy encoder 4.
- `regAFMT[0-5]_AFMT_*`: audio formatter VBI packet control, audio packet controls, HDMI/DP audio info words, IEC 60958 channel status words, audio CRC control/result/status, ramp controls, infoframe control, interrupt status, audio source selection, and AFMT memory power.
- `regDME[0-9]_DME_*`: metadata-engine control and memory-control registers. In this slice, legacy DIO uses `DME0..4`, HPO HDMI uses `DME5`, HPO DP instances 0 through 2 use `DME6..8`, and instance 3 begins with `DME9_DME_CONTROL`.
- `regVPG[0-8]_VPG_*`: video packet generator generic packet access/data, frame and immediate update controls, generic status, memory power, ISRC access/data, and MPEG info packet words.
- `regDP_AUX[0-4]_AUX_*`: AUX engine control, software control/status/data, link-service status/data, DPHY TX/RX controls and statuses, GTC sync controls/statuses, and PHY wake control for five AUX/DDC-capable links.
- `regDC_I2C_*`, `regDIO_*`, and `regDCIO_*`: DOUT I2C arbitration/status, DIO memory/clock/power/soft-reset/link controls, DCIO reference/clock controls, channel crossbar controls, pin straps, pattern generation, genlock/swaplock pad controls, and soft reset.
- `regDC_GPIO_*`, `regPHY_AUX_CNTL`, and `regAUXI2C_PAD_ALL_PWR_OK`: GPIO mask/value/output-enable/readback registers for generic, DDC, VGA DDC, genlock, HPD, PWRSEQ, AUX, pad-drive, pull-up, RX-enable, and pad power-good handling.
- `regDCIO_UNIPHY[0-4]_UNIPHY_MACRO_CNTL_RESERVED*`: per-UNIPHY reserved macro-control offsets. The header does not describe field semantics, but the stable generated names allow shared link-encoder code to address PHY-instance register space if a field list references them.
- `regPANEL_PWRSEQ_*`, `regBL_PWM_*`, and `regDC_GPIO_PWRSEQ_*`: panel power sequencing, delay/reference-divisor programming, backlight PWM controls, lock/update grouping, and PWRSEQ GPIO controls.
- `regDSC_TOP[0-3]_*`, `regDSCCIF[0-3]_*`, and `regDSCC[0-3]_*`: DSC top control/debug, DSC interface config, DSC compressor config/status/interrupts, PPS config words 0 through 22, memory power, squared-error/readback counters, max absolute error, rate-buffer fullness, rate-control-buffer fullness, and debug bus/data registers.
- `regHPO_TOP_*` and `regDP_STREAM_MAPPER_CONTROL[0-3]`: HPO clock/hardware control and mapping of DP streams to HPO link targets.
- `regDP_STREAM_ENC[0-3]_*`: HPO DP stream encoder clock, pixel input mux, audio mux, clock-ramp FIFO status/control, and spare registers.
- `regAPG[0-3]_*`: audio packet generator controls, debug generation, packet control, audio CRC control/result, status, memory power, and spare registers for HPO DP streams.
- `regDP_SYM32_ENC[0-2]_*`: HPO DP 128b/132b-oriented symbol stream controls, video FIFO, MSA double-buffer and MSA words, pixel-format double buffering, hblank control, generic secondary-data packet controls, SDP/audio/metadata controls, VBID and stream control, Panel Replay control, video CRC control/results/status, memory power, and spare.

## Control Flow and State Behavior

There is no local control flow in this header. The control flow is generated indirectly when resource constructors and hardware blocks token-paste these macro names into register tables, then call common read/write helpers.

Important sequencing modeled by this offset slice includes:

- Stream sideband programming is instance-oriented. Legacy `AFMT0..4`, `DME0..4`, and `VPG0..4` correspond to DIO/DIG instances; HPO HDMI uses `AFMT5/DME5/VPG5`; HPO DP stream instances use `DP_STREAM_ENC0..3`, `APG0..3`, `VPG6..8` in this slice, and `DME6..9`. Resource code must map stream encoders to the correct sideband blocks rather than assuming all suffixes match.
- AUX and I2C offsets are used by transaction state machines. The registers named here expose software command/data paths, arbitration, interrupts, DPHY controls, TX/RX status, and wake controls. Runtime code sequences requests by programming control/data registers, waiting on status/interrupt bits defined in the shift/mask header, and handling retries/timeouts.
- PWRSEQ and backlight state is latched by panel-power and PWM hardware. `BL_PWM_GRP1_REG_LOCK`, panel delay/reference registers, target/current state registers, and GPIO PWRSEQ controls represent persistent hardware state that must be programmed in the right order around panel power on/off and backlight enable/disable.
- DSC programming is double-buffered and status-driven. `DSCC_CONFIG*`, `DSCC_PPS_CONFIG*`, `DSCC_STATUS`, and `DSCC_INTERRUPT_CONTROL_STATUS` are consumed by DSC setup paths that configure slice/PPS/rate-control state, wait for update completion, and monitor rate-buffer overflow/underflow/error signals.
- HPO DP stream enablement spans several blocks. The stream mapper chooses the HPO link target, `DP_STREAM_ENC*` selects pixel/audio sources and FIFO behavior, `DP_SYM32_ENC*` programs pixel format/MSA/SDP/VBID/CRC, `APG*` drives audio packet state, and `VPG*`/`DME*` carry video packets and metadata. A mode set that changes one part without the matching block can route packets or audio to the wrong stream.
- Memory power registers appear in AFMT, VPG, DME, APG, DP_SYM32, and DSCC families. They model low-power state separate from pure functional configuration; register writes may be ignored or delayed if the relevant memory block is not powered as expected.

## Dependencies and Integration Points

This header is paired with `dcn_3_2_0_sh_mask.h`. The offset macros provide register addresses, while the shift/mask header provides field-level bit positions. Both are included directly by DCN32-specific code such as `display/dmub/src/dmub_dcn32.c` and `display/dc/irq/dcn32/irq_service_dcn32.c`.

The main display-resource integration is `display/dc/resource/dcn32/dcn32_resource.c`, which expands these symbols into typed register tables:

- `VPG_DCN3_REG_LIST_RI(id)` initializes `vpg_regs[10]`, covering legacy `VPG0..4`, HPO HDMI `VPG5`, and HPO DP VPG instances.
- `AFMT_DCN3_REG_LIST_RI(id)` initializes `afmt_regs[6]`, covering `AFMT0..5`.
- `APG_DCN31_REG_LIST_RI(id)` initializes `apg_regs[4]`, covering `APG0..3`.
- `SE_DCN32_REG_LIST_RI(id)` initializes legacy stream encoder registers such as the `DIG4` tail present at the beginning of this chunk.
- `DCN2_AUX_REG_LIST_RI(id)` initializes five AUX register sets, matching `DP_AUX0..4`.
- `LE_DCN31_REG_LIST_RI(id)` and `UNIPHY_DCN2_REG_LIST_RI(id, phyid)` integrate DIO link encoder and UNIPHY/DCIO register offsets.
- `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST_RI(id)` initializes four HPO DP stream encoder register sets from `DP_STREAM_MAPPER_CONTROL*`, `DP_STREAM_ENC*`, and `DP_SYM32_ENC*`.
- `DSC_REG_LIST_DCN20_RI(id)` initializes four DSC register sets from `DSC_TOP*`, `DSCCIF*`, and `DSCC*`.

Other integration points include:

- `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`, whose register-list macro consumes `DP_STREAM_MAPPER_CONTROL*`, `DP_STREAM_ENC*`, and `DP_SYM32_ENC*` offsets and whose mask/shift list consumes the companion field macros.
- `display/dc/dsc/dcn20/dcn20_dsc.h`, which defines the shared DSC register list used by DCN32 resource code for `DSC_TOP`, `DSCC`, and `DSCCIF`.
- `display/dc/dce/dce_link_encoder.h` and DCN link-encoder headers, which provide AUX, HPD, link, and UNIPHY register-list patterns.
- `display/dc/gpio/dcn32/*`, `display/dc/dio/dcn32/*`, `display/dc/hpo/dcn32/*`, panel/backlight paths, and IRQ handling, which rely on these generated offsets through resource-created register structures.

## State and Persistence

The macros themselves do not store state, but they name hardware state that persists in MMIO registers until rewritten, reset, power-gated, or latched by display timing:

- GPIO, HPD, DDC, AUX, DIO, and DCIO registers persist physical I/O configuration, pad state, arbitration state, and soft-reset state.
- Panel power sequence and backlight PWM registers persist panel enable, target power state, delay timing, PWM period/duty behavior, and lock/update settings across the panel sequence.
- AFMT, APG, VPG, and DME registers persist packet-generator, audio, metadata, CRC, status, interrupt, and memory-power state per stream-sideband block.
- DSC registers persist compressor configuration, PPS payload values, memory-power state, status, overflow/underflow state, and debug/error counters.
- HPO mapper, stream encoder, and SYM32 encoder registers persist HPO DP stream routing, pixel/audio source selection, MSA/pixel format, SDP behavior, CRC setup, Panel Replay control, and stream enable-related state.

Because these offsets are generated for one ASIC revision, they are effectively an internal ABI between DCN32 register tables and the hardware. A wrong offset or base index can compile cleanly while targeting the wrong MMIO aperture.

## Risks and Edge Cases

- The chunk starts and ends mid-block. `DIG4_HDMI_ACR_44_0` is split from its `_BASE_IDX` at the beginning, and `DME9_DME_CONTROL` is split from `DME9_DME_MEMORY_CONTROL` at the end. The final per-file report must reconcile adjacent chunks before claiming complete DIG4 or HPO stream encoder 3 coverage.
- Instance numbering is nontrivial. Legacy DIO uses `AFMT/DME/VPG0..4`; HPO HDMI uses suffix 5; HPO DP stream encoder 0 uses `DME6` and `VPG6`, stream encoder 1 uses `DME7` and `VPG7`, stream encoder 2 uses `DME8` and `VPG8`, and stream encoder 3 begins with `DME9`. Code must follow resource mapping, not numeric intuition.
- Base-index drift is high impact. Most offsets here use `_BASE_IDX 2`, but HPO top/mapper and HPO HDMI stream encoder sideband blocks use `_BASE_IDX 3`. Incorrect base indices can point an otherwise correct offset at the wrong register aperture.
- Reserved UNIPHY macro-control registers are opaque. They are useful for generated access tables, but without field semantics they should not be casually programmed outside established link-encoder sequences.
- Status, interrupt, acknowledge, and clear semantics are not visible in the offset header. AUX, AFMT/APG CRC/status, DIO/DCIO soft reset, PWRSEQ, DSC interrupt/status, and HPO CRC/status registers require the companion shift/mask header and hardware programming sequence to avoid read-modify-write mistakes.
- Generated repetition makes review hard. AFMT, VPG, AUX, DSCC, HPO DP stream encoder, APG, DME, and DP_SYM32 blocks differ mostly by instance suffix and offset stride; a single generator error could affect only one connector, stream, DSC instance, or HPO path.
- DSC registers include diagnostic/error counters and underflow/overflow state. Treating them as ordinary configuration registers can hide compression failures or accidentally clear diagnostic signals depending on field semantics in the companion header.

## Test Signals

Useful validation signals for code paths using this slice include:

- Build coverage for DCN32 with `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h` included, catching missing or renamed `regAFMT*`, `regVPG*`, `regDME*`, `regDP_AUX*`, `regDCIO_UNIPHY*`, `regDSCC*`, `regDP_STREAM_ENC*`, `regAPG*`, and `regDP_SYM32_ENC*` symbols.
- Resource-table sanity checks in `dcn32_resource.c` confirming expected instance counts and offsets for five AUX engines, five legacy stream encoders, five link encoders, six AFMT blocks, ten VPG blocks, four APG blocks, four HPO stream encoders, and four DSC blocks.
- Connector bring-up tests across legacy DIO paths that exercise AUX/DDC, HPD/GPIO, DIG4 HDMI/TMDS, AFMT audio/infoframe, VPG generic packets, and DME metadata without link-training or packet-routing regressions.
- eDP/panel tests that cycle panel power, backlight PWM, PWRSEQ GPIO, and BL PWM lock/update paths while checking for correct panel state and no stuck power-sequence status.
- DSC mode-set tests on all four DSC instances that program PPS/config registers, enable compressed output, watch `DSCC_STATUS` and interrupt/status fields, and verify no rate-buffer underflow/overflow events.
- HPO DP 2.0/UHBR tests using stream encoders 0 through 2 fully and stream encoder 3 through the next chunk, validating stream mapper targets, pixel/audio muxing, SYM32 MSA/pixel-format/SDP programming, APG audio packets, VPG packets, DME metadata, CRC readback, and memory-power transitions.
- Suspend/resume and display hotplug tests that cover AUX wake/status, DCIO/DIO soft reset, GPIO/HPD state, and HPO/DSC memory-power restoration.

### subset-b-001928: lines 12823-14737

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h lines 12823-14737

## Purpose

This chunk is the tail of the generated AMD DCN 3.2.0 register-offset header. It contains no executable code; it publishes C preprocessor constants that name hardware register offsets and indirect-register indexes for DCN 3.2 display, HPO DisplayPort, DPCS/PHY, legacy VGA, and Azalia/HDA audio blocks.

The requested range contains 1,620 `#define` entries across 73 address blocks. Of those, 476 are `reg*` register-offset or `_BASE_IDX` macros and 1,144 are `ix*` indirect index macros. The block begins at the final `DME9_DME_MEMORY_CONTROL` entry from the prior DME block, covers HPO DP stream/link/PHY offsets, then shifts into DPCS pipe indirect indexes and the HDA/Azalia controller, stream, endpoint, input endpoint, CRC, descriptor, sink-info, and C20 PHY indirect index spaces. Although this file lives under a mirrored `ceph-client` source tree, the content is AMDGPU display-driver ASIC metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocation paths, or exported C symbols in this range. The API surface is the generated macro namespace:

- `reg<REGISTER>` gives an MMIO register offset relative to the base segment identified by the companion macro.
- `reg<REGISTER>_BASE_IDX` selects the entry in `ctx->dcn_reg_offsets[]` that must be added to the offset by DCN register-list construction code.
- `ix<REGISTER>` gives an indirect register index written through an index/data register pair rather than directly added to a DCN base offset.

Major macro families in this chunk:

- HPO DP stream encoder packet-generation offsets: `regVPG9_*` for generic packet access/data, GSP frame/immediate update controls, generic status, memory power, ISRC access/data, and MPEG info registers.
- HPO DP 32-symbol stream encoder offsets: `regDP_SYM32_ENC3_*` for stream control, video FIFO, MSA double buffering, pixel format, MSA0-8, hblank control, sideband/generic/audio/metadata packet controls, VBID, panel replay, video CRC, memory power, and spare registers.
- HPO DP link and PHY offsets: `regDP_LINK_ENC0_*`, `regDP_LINK_ENC1_*`, `regDP_DPHY_SYM320_*`, and `regDP_DPHY_SYM321_*` for link clocks/spares, DPHY enable/reset/status, stream allocation table (`SAT`) updates, virtual-channel rates, test-pattern configuration, PRBS/custom patterns, symbol override, error/status, deskew, lane enablement, memory power, and flow-control/status registers.
- DPCS pipe indirect offsets: `ixRDPCSPIPE[0-4]_*` for pipe clock and pipe resets at per-pipe base offsets.
- HDA/Azalia controller offsets: `regCORB_*`, `regRIRB_*`, immediate command/response interface registers, DMA position base registers, wall-clock alias, and endpoint/root/input endpoint immediate command aliases.
- HDA output stream descriptors: `regAZSTREAM[0-7]_*` for stream control/status, link position, cyclic-buffer length, last-valid index, FIFO size, format, BDL lower/upper base, and link-position aliases.
- Legacy VGA indirect register indexes: `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` for sequencer, CRT controller, graphics, and attribute register spaces.
- Azalia codec and sink indexes: `ixAZALIA_F2_*`, audio descriptors, sink manufacturer/product/port/description entries, output/input CRC channel result indexes, function parameter indexes, and latency/FIFO counters for `AZF0STREAM0` through `AZF0STREAM15`.
- Repeated Azalia endpoint indexes: `ixAZF0ENDPOINT0_*` through `ixAZF0ENDPOINT7_*` for converter parameters, converter controls, stream IDs, digital converter controls, stripe/ramp/GTC controls, pin capabilities, pin sense, speaker/channel allocation, audio descriptors, sink info, hot-plug, unsolicited response force, codec status, LPIB snapshots, coding/format-change/wireless/keepalive fields, and audio enable/disable/format-change interrupt status.
- Repeated Azalia input endpoint indexes: `ixAZF0INPUTENDPOINT0_*` through `ixAZF0INPUTENDPOINT7_*` for input converter controls, input pin controls, multichannel/HBR status, channel allocation, hot-plug, LPIB snapshots, input status, and infoframe.
- C20 PHY indirect indexes: `ixC20_PHY_CR[0-4]_*` for per-lane VGA adaptation status and raw-lane TX/RX interrupt mask indexes, plus lane-X aggregate aliases.

## Control Flow

This header has no direct control flow. Runtime sequencing is supplied by AMD display code that includes this generated header and its paired shift/mask header:

1. DCN 3.2 code includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Resource setup macros such as `SR`, `SR_ARR`, `SRI`, and `SRI_ARR` token-paste register names into `reg...` and `reg..._BASE_IDX`, then compute absolute MMIO offsets from `ctx->dcn_reg_offsets[]`.
3. Register helper macros such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET` use those offsets, and indirect helpers use `ix...` indexes through endpoint/index-data windows.
4. Higher-level DCN code performs modeset, HPO DP enablement, link training/test-pattern setup, audio endpoint programming, CRC reads, stream descriptor setup, interrupt handling, and power-management sequencing.

The macros only provide addresses and indexes. They do not encode required ordering, access permissions, polling rules, write-one-to-clear behavior, or timing boundaries for display/audio hardware updates.

## State And Persistence Behavior

The file stores no software state and persists nothing on disk. It describes MMIO-backed and indirect-indexed hardware state. The represented state includes:

- HPO DP packet, stream, and link state: packet payload access, GSP/update timing, MSA/pixel format/VBID, sideband packet routing, panel replay controls, video CRC results/status, memory-power controls, link clocks, PHY reset/enable/status, lane configuration, VC rates, SAT programming, test patterns, symbol override, and flow control.
- DPCS and PHY state: per-pipe clock/reset controls, per-lane adaptation status, and raw-lane TX/RX interrupt mask indexes.
- HDA/Azalia DMA and command state: CORB/RIRB buffers, immediate command/response windows, DMA position buffers, wall-clock reads, output stream descriptors, FIFO size, stream format, BDL base addresses, link-position aliases, and latency counters.
- Codec endpoint and pin state: audio widget capabilities, converter format/stream ID/digital converter settings, audio descriptors, sink information, channel and speaker allocation, lip-sync/HBR/multichannel controls, hot-plug and unsolicited response state, pin sense, LPIB snapshots, coding type, format-change status, keepalive, and audio enable/disable interrupts.
- Diagnostic state: input/output audio CRC channel indexes, DP video CRC registers, DPHY error/status registers, and PHY interrupt masks.

Persistence is hardware-defined. Configuration registers usually retain state until reprogramming, power gating, suspend/resume restore, or ASIC reset. Status, CRC, interrupt, link-position, command-response, FIFO, latency, snapshot, and `*_STATUS` registers can be read-only, sticky, self-clearing, or side-effect-sensitive depending on the hardware register specification; the offset header does not classify those semantics.

## Dependencies And Integration Points

This chunk must match the corresponding DCN 3.2.0 shift/mask header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h`, and the generated symbol names expected by DCN 3.2 display code.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`

Specific downstream consumers include `dcn32_resource.h` register-list macros for audio endpoint registers and HPO DP DPHY/SYM32 register arrays. The `dcn32_hpo_dp_link_encoder.h` field-list macros reference the `DP_DPHY_SYM320_*` naming in this range, while `dcn32_resource.c` uses Azalia endpoint index/data macros for audio resource construction. Older DCE code in the same tree shows the common use pattern for `ixAZALIA_*` indexes through `RREG32_AUDIO_ENDPT` and `WREG32_AUDIO_ENDPT` helpers, even though this chunk provides the DCN 3.2 generated index namespace.

## Risks And Edge Cases

- Generated offset drift is the central risk. A wrong value or `_BASE_IDX` can compile cleanly but point register helpers at the wrong hardware block.
- `reg*` and `ix*` macros are different address spaces. Treating an indirect `ixAZF0ENDPOINT*` or `ixC20_PHY*` value as an MMIO offset, or adding a DCN base to it, would access the wrong register path.
- HPO DP register families are highly replicated. `DP_SYM32_ENC3`, `DP_LINK_ENC0/1`, and `DP_DPHY_SYM320/321` names differ by instance; token-paste mistakes can route one stream or link lane set to the wrong encoder instance.
- Audio endpoint families are also highly replicated. `AZF0ENDPOINT0-7`, `AZF0INPUTENDPOINT0-7`, and `AZF0STREAM0-15` share nearly identical local indexes, so generator or caller mix-ups can affect only one display/audio function and be hard to diagnose.
- Some offsets alias multiple logical registers at one numeric address, such as HDA stream `FIFO_SIZE` and `FORMAT` or controller `RIRB_*` and response interrupt/status fields. Correct behavior depends on field masks and access size/semantics outside this offset header.
- Status and interrupt registers are side-effect-sensitive. CRC result/status, audio enable/disable/format-change interrupt status, LPIB snapshots, hot-plug/unsolicited response, command status, and PHY IRQ mask/status paths need access helpers that preserve clear/ack semantics.
- HPO link/PHY test-pattern, PRBS, symbol override, lane-enable, and reset registers can disturb active links if programmed out of sequence. The header provides no guard against writes during live display.
- The chunk boundary starts at the tail of a DME instance and ends at `#endif`, so complete per-file conclusions must reconcile this range with prior chunks for the earlier DCN 3.2.0 offset map.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Build AMDGPU/DC with DCN 3.2 support enabled so token-pasted `reg...`, `reg..._BASE_IDX`, and `ix...` names resolve in `dcn32_resource.c`, `dmub_dcn32.c`, HPO DP encoder code, GPIO, IRQ, clock-manager, and GMC paths.
- Mechanically verify that every `reg*` entry used by DCN 3.2 register-list macros has a companion `_BASE_IDX` and that every generated base index maps to a valid `ctx->dcn_reg_offsets[]` slot for the target ASIC.
- Compare these offsets and indirect indexes against AMD's authoritative DCN 3.2.0 register database or a known-good generated header.
- Exercise HPO DP modesets across stream/link encoder instances, including sideband packet programming, MSA/pixel-format changes, VBID, panel replay, video CRC reads, DPHY enable/reset, SAT updates, VC rate changes, and link training/test patterns.
- Exercise display audio through HDMI/DP sinks: stream descriptor setup, CORB/RIRB command flow, immediate command-response access, channel allocation, audio descriptors, HBR/multichannel modes, hot-plug handling, LPIB snapshot reads, and format-change interrupts.
- Validate DPCS/C20 PHY paths with lane-level status reads and TX/RX IRQ mask programming during link bring-up, link retraining, suspend/resume, and display hotplug.
- Run power-management and resume tests around VPG/SYM32/DPHY/Azalia memory-power or clock-gating controls to catch offsets that only fail when blocks are gated or restored.
- Run CRC and diagnostic tests for DP video CRC, Azalia input/output CRC channels, latency counters, and stream link-position aliases to catch wrong indirect indexes or address aliases.

## Cross-Chunk Notes

Earlier chunks in `dcn_3_2_0_offset.h` contain the preceding DCN 3.2 register-offset families that lead into the `DME9` tail seen at the top of this range. This chunk reaches the file terminator and completes the offset/index namespace with HPO DP, DPCS/PHY, VGA, HDA/Azalia, endpoint, input endpoint, and C20 PHY indirect definitions. The final per-file research document should merge adjacent chunk notes before making complete claims about all DCN 3.2.0 display, audio, PHY, and memory/controller register coverage.
