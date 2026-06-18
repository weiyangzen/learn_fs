# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001890`: lines 1-2689, `Docs/researches/chunks/subset-b-001890_research.md`
- `subset-b-001891`: lines 2690-5205, `Docs/researches/chunks/subset-b-001891_research.md`
- `subset-b-001892`: lines 5206-7703, `Docs/researches/chunks/subset-b-001892_research.md`
- `subset-b-001893`: lines 7704-10281, `Docs/researches/chunks/subset-b-001893_research.md`
- `subset-b-001894`: lines 10282-12823, `Docs/researches/chunks/subset-b-001894_research.md`
- `subset-b-001895`: lines 12824-15508, `Docs/researches/chunks/subset-b-001895_research.md`
- `subset-b-001896`: lines 15509-15686, `Docs/researches/chunks/subset-b-001896_research.md`

## Chunk Research

### subset-b-001890: lines 1-2689

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 1-2689

## Purpose

This chunk is generated AMD DCN 3.1.6 register-offset metadata. It contains no executable driver logic; it publishes C preprocessor constants that map symbolic display-controller register names to MMIO register offsets and to the hardware base segment index used by AMDGPU display register helpers.

The requested range starts at the file license/header guard and covers the first 2,689 lines of a 15,686-line generated header. Within this range there are 2,352 `#define` lines, including 1,176 register-offset style macros, 1,175 `_BASE_IDX` companion macros, and one include-guard macro. The range has 78 generated address-block markers. It ends mid-block in `dce_dc_dchubbubl_hubbub_vmrq_if_dispdec` at `regDCN_VM_DEFAULT_ADDR_MSB`, so the base-index companion and the rest of the VM request interface are owned by following chunks.

Although this repository path is under a local `ceph-client` mirror, this source file is AMDGPU display hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, memory allocations, includes, or runtime APIs in this chunk. Its interface is the generated macro namespace:

- `reg<REGISTER_NAME>`: a register offset value, normally relative to the base segment selected by its companion base-index macro.
- `reg<REGISTER_NAME>_BASE_IDX`: an integer index into the consuming driver's DCN base segment table.
- `// addressBlock: ...` and `// base address: ...`: generated comments that describe the hardware block and source register database base, but do not affect compilation.

Major register families covered in this chunk:

- Azalia/HDA controller decode registers: global capabilities/status/control, CORB/RIRB DMA ring registers, immediate command/response registers, stream synchronization, DMA position, endpoint/root/input endpoint aliases, and eight decoded output stream descriptors.
- Legacy VGA and VGA/MMHUBBUB registers: memory page selection, VGA CRTC/SEQ/ATTR/DAC legacy I/O aliases, render and sequencer controls, memory base/surface registers, VGA security/status/interrupt registers, and VGAIF register access.
- DCCG display clock generation registers: DISPCLK and DPREFCLK controls, PHYPLL pixel-rate resync controls, DP DTO phase/modulo registers, OTG pixel-rate controls, DPPCLK/DSCCLK DTO controls, symbol clock enables, audio DTO registers, vsync latch/count controls, gate/clock-gating controls, soft reset, and DCCG perfmon blocks.
- DMU and DMCU registers: DMCU control/status, firmware start/end/checksum and RAM access registers, interrupt status/masks/selectors, master/slave communication mailboxes, scratch/register communication paths, performance monitor interrupt routing, and DPRX interrupt control.
- DMU/IHC interrupt registers: GPU timer start/read registers, display interrupt status continuation registers, block interrupt-destination registers for DCCG, DMU, DCPG, MMHUBBUB, WB, DCHUB, DPP perf counters, MPC, OPP, OPTC, OTG0-OTG5, DIG, I2C/DDC/HPD, DIO/DCIO, AZ audio, AUX, DSC, and HPO.
- DMU miscellaneous and power gating: display-pipe disable, DMU clock and memory power, SMU interrupt control, zero-sleep/zero-shutter controls and status, domain power-gating config/status registers, DCPG interrupt registers, and `DC_IP_REQUEST_CNTL`.
- DMCUB registers: region offsets/high offsets, region top/base/code-window registers, security and memory controls, inbox/outbox base/size/read/write pointers, timers, scratch0-15, GPINT data, undefined-address fault, low-speed wake interrupt enable, processor ID, and DMCUB control/reset registers.
- DWB writeback and color-processing registers: writeback clock/memory power, frame-capture mode/flow/window/source sizing, update/CRC/output controls, backpressure/overflow/host-read/debug registers, HDR multiplier, gamut-remap coefficient matrices, OGAM LUT index/data/control, RAM A/B start/end/offset registers, and PWL region descriptors 0-33.
- DC perfmon blocks: `DC_PERFMON0` through `DC_PERFMON5` register sets for DCCG, DMU, WB, MMHUBBUB, and Azalia-related performance counters.
- MMHUBBUB and MCIF writeback registers: writeback buffer address/ring/pitch/size/watermark/status/VMID controls, MMHUBBUB warmup, min time-to-off, memory/clock/soft-reset controls, timeout/error/status registers, and client/unit controls.
- Azalia F0 controller/root/stream/endpoint registers: clocking, audio DTO, DMA, CRC, memory power, codec function parameters, stream index/data pairs for streams 0-15, endpoint index/data pairs 0-7, and input endpoint index/data pairs 0-7.
- DCHUBBUB registers: arbitration outstanding request/saturation/QOS/DRAM-state controls, watermark sets A-D, HostVM and watermark-change controls, global timer, surface-check addresses, VTG controls, soft reset, clock/DCFCLK controls, performance measurement, timeout detection, SDPIF VM/framebuffer/AGP/HBM/security controls, return-path DCC/CRC/compression-buffer/DET/memory-power controls, and the beginning of VM context0-15 page-table register definitions.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by consuming AMD display code:

1. A DCN 3.1.6 consumer includes `dcn_3_1_6_offset.h` and the companion `dcn_3_1_6_sh_mask.h`.
2. Register-list macros paste symbolic names into `reg...` and `reg..._BASE_IDX` identifiers.
3. The consumer combines `reg<REGISTER>_BASE_IDX` with ASIC base constants such as `DCN_BASE__INST0_SEG0` through `DCN_BASE__INST0_SEG5`, then adds `reg<REGISTER>` to get an absolute MMIO address.
4. Higher-level helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, and `REG_GET` perform the actual MMIO accesses and apply field masks/shifts from the companion sh/mask header.

The direct DCN 3.1.6 example in this tree is `dmub_dcn316.c`, where `REG_OFFSET_EXP(reg_name)` expands to `BASE(reg##reg_name##_BASE_IDX) + reg##reg_name` while building `dmub_srv_dcn316_regs`.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state:

- HDA/Azalia registers represent audio controller state, stream descriptor DMA state, codec parameters, endpoint access windows, CRC state, memory power, and audio clocking.
- DCCG registers represent clock-source selection, DTO programming, clock gating, soft reset, timing latches, and clock/perf counter readback.
- DMU/DMCU/DMCUB registers represent display microcontroller boot, firmware-memory windows, communication rings, interrupts, scratch state, security controls, power requests, and reset/fault state.
- IHC and interrupt-destination registers represent display interrupt routing and live status for timing, hotplug/AUX/DDC, audio, writeback, DSC/HPO, hub, and performance-counter events.
- DWB and DWB color registers represent writeback capture configuration, live overflow/backpressure/CRC status, output packing, gamut/HDR transforms, and OGAM LUT programming.
- MMHUBBUB, DCHUBBUB, SDPIF, return-path, and VM context registers represent display memory arbitration, watermark timing, compression-buffer/DET/return-path state, VM apertures, page-table base/start/end ranges, security levels, and memory power state.

Persistence is hardware-defined. Many configuration registers persist until modeset reprogramming, suspend/resume, display power gating, DMCUB reset, GPU reset, or ASIC reset. Status, interrupt, fault, counter, pointer, and acknowledgment registers may be read-only, sticky, self-clearing, or write-one-to-clear; this offset header does not encode those access semantics.

## Dependencies And Integration Points

This chunk must remain consistent with AMD's generated DCN 3.1.6 register database and its companion field metadata:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h`
- DCN base segment constants defined by the consumer, including `DCN_BASE__INST0_SEG0` through `DCN_BASE__INST0_SEG5` in `dmub_dcn316.c`.

Direct integration points in this source tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c` includes this header and builds the `dmub_srv_dcn316_regs` register table using `DMUB_DCN31_REGS()` and `DMCUB_INTERNAL_REGS()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.h` exposes `dmub_srv_dcn316_regs`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c` selects `dmub_srv_dcn316_regs` for `DMUB_ASIC_DCN316`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c` maps DCN 3.1.6 hardware to `DMUB_ASIC_DCN316` and names the `amdgpu/dcn_3_1_6_dmcub.bin` firmware.
- The broader DCN 3.1.6 display stack under `display/dc/` creates DCN316 resources and clock-management paths; those paths rely on coherent register tables and DMUB initialization even when they do not include this generated offset header directly.

The DMCUB subset in this chunk is the most directly exercised by the in-tree DCN 3.1.6 DMUB table. Other register families are generated in the same ASIC offset header for consistency with AMD register tooling and may be consumed by common display modules, generated tables, diagnostics, or future feature paths.

## Risks And Edge Cases

- Offset drift is the central risk. A wrong offset or base index compiles cleanly but can read or write the wrong hardware register.
- The chunk boundary is artificial. It begins at the file start and ends after `regDCN_VM_DEFAULT_ADDR_MSB` without the companion `_BASE_IDX`, so adjacent chunks are required before making complete claims about the VM request interface or full file coverage.
- Base index errors are as dangerous as offset errors. The same numeric offset under the wrong DCN base segment can target a different block.
- HDA/Azalia stream and CORB/RIRB registers are DMA- and firmware-visible. Incorrect offsets can break audio enumeration, stream playback/capture, codec command responses, or DMA position reporting.
- DCCG clock and DTO registers are sequencing-sensitive. Misprogramming can cause unstable display clocks, bad audio DTO timing, failed pixel-rate changes, or resume/modeset failures.
- Interrupt status and destination registers are high risk because incorrect routing or acknowledgment can lose vblank/page-flip/HPD/AUX/DMCUB/writeback events or cause interrupt storms.
- DMU, DMCU, DMCUB, power-gating, and memory-power registers depend on reset and clock state. Access at the wrong time can be ignored or leave firmware-visible state inconsistent.
- DMCUB region, code-window, inbox/outbox, scratch, GPINT, and fault registers are critical to DMUB boot and command processing. Bad addresses or pointers can prevent firmware initialization or silently corrupt command exchange.
- DWB and DWB color-processing register errors may only show up in writeback, capture, CRC, color-management, or virtual-display workflows, not ordinary scanout.
- MMHUBBUB/DCHUBBUB watermark, VM, arbitration, compression, and return-path offsets can create subtle underflow, page-fault, memory-power, or bandwidth failures that only occur under specific display modes, memory clocks, or multi-plane workloads.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU display support with DCN 3.1.6 and DMUB enabled; missing or renamed macros should fail in `dmub_dcn316.c` and the shared DMUB register-list macros.
- Mechanically verify each complete `reg...` definition in this range has a matching `reg..._BASE_IDX`, allowing for the include guard and the known final partial `regDCN_VM_DEFAULT_ADDR_MSB`.
- Diff this chunk against AMD's authoritative DCN 3.1.6 register database and against adjacent DCN 3.1.x offset headers where compatibility is expected.
- Boot DCN 3.1.6 hardware and verify DMUB firmware load, DMCUB reset release, command submission, inbox/outbox pointer movement, GPINT handling, scratch/debug state, and outbox interrupts.
- Exercise modeset, suspend/resume, display clock changes, multiple display pipes, vblank/vline/page-flip events, HPD plug/unplug, HPD RX, AUX/DDC activity, DSC/HPO-capable links, and audio over display outputs.
- Exercise writeback/capture paths where exposed: enable/disable capture, alter source/window sizes, check CRC values, trigger host reads, monitor overflow/backpressure counters, and validate OGAM/gamut/HDR transforms with known ramps.
- Exercise memory-pressure and bandwidth-sensitive display scenarios: plane flips, high-resolution/multi-monitor modes, DRAM clock changes, stutter/self-refresh transitions, VM-enabled scanout, and compressed-surface return paths.
- Watch kernel logs, display diagnostics, and hardware counters for DMUB boot failures, timeout/fault registers, lost interrupts, HPD storms, AUX timeouts, audio stream failures, underflows, page faults, writeback overflows, CRC mismatches, and resume failures.

## Cross-Chunk Notes

This chunk owns the file prologue and the first generated offset families for DCN 3.1.6. Later chunks are needed to complete the VM request interface that starts here and to cover the rest of the ASIC register map. The final per-file research document should reconcile this chunk with adjacent offset chunks and with the companion `dcn_3_1_6_sh_mask.h` field-layout research.

### subset-b-001891: lines 2690-5205

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 2690-5205

## Purpose

This chunk is generated AMD DCN 3.1.6 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map display-engine register names to MMIO offsets and to the DCN base-segment index used by AMDGPU register helper macros.

Although this file is inside a local `ceph-client` source mirror, the content is AMDGPU display-driver hardware metadata and has no Ceph or distributed filesystem behavior.

The requested range starts at a chunk boundary inside the tail of the DCN VM register block, then covers DC perfmon instance 6, four HUBP/HUBPREQ/HUBPRET/CURSOR pipelines, DC perfmon instances 7-10, and the first two DPP pipelines. The DPP coverage includes converter/configuration (`CNVC_CFG`), converter cursor (`CNVC_CUR`), scaler (`DSCL`), color management (`CM`), DPP top-level, and DPP perfmon instance 11 for DPP0. The chunk ends inside the `CM1_CM_SHAPER_RAMB_REGION_*` sequence, so later CM1 shaper registers continue in the next chunk.

This slice contains 2,392 `#define` lines: 1,196 register-offset macros and 1,196 matching `_BASE_IDX` macros. Every complete register offset in the slice has a companion base-index macro; the first line is only the `_BASE_IDX` for `regDCN_VM_CONTEXT15_PAGE_TABLE_START_ADDR_LO32`, whose offset macro belongs to the previous chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, locks, or direct allocation/persistence APIs in this line range. The public interface is the generated macro convention:

- `reg<REGISTER_NAME>`: register offset within the selected DCN address segment.
- `reg<REGISTER_NAME>_BASE_IDX`: index into the ASIC-specific `DCN_BASE__INST0_SEG*` table.

Important macro families in this chunk:

- DCN VM boundary tail: `regDCN_VM_CONTEXT15_PAGE_TABLE_END_ADDR_*`, `regDCN_VM_DEFAULT_ADDR_*`, `regDCN_VM_FAULT_CNTL`, `regDCN_VM_FAULT_STATUS`, and fault address registers.
- DC perfmon instances: `DC_PERFMON6` through `DC_PERFMON11` counter control, state, run/interrupt control, current-value, high, and low counter registers. Instances 7-10 are attached to HUBP blocks 0-3; instance 11 is attached to DPP0 in this slice.
- HUBP instances 0-3: `HUBP*_DCSURF_SURFACE_CONFIG`, address/tiling config, primary and secondary viewport registers for luma and chroma, request-size config, HUBP control, clock control, VM page config, debug registers, and DCFCLK/DPPCLK measurement windows.
- HUBPREQ instances 0-3: surface pitch, VMID, primary/secondary luma and chroma surface addresses, metadata surface addresses, surface control, flip control and interrupt, in-use/earliest-in-use address readbacks, expansion mode, TTU/QoS controls, DMDATA VM control, system aperture and L1 TLB registers, blank/destination/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor settings, ref-to-pixel frequency conversion, and HUBPREQ memory power control/status.
- HUBPRET instances 0-3: return-path control, memory power control/status, read-line controls, interrupt, read-line value, and read-line status.
- Cursor instances 0-3: cursor control, surface address low/high, size, position, hot spot, stereo control, destination offset, cursor memory power control/status, DMDATA address/control/QoS/status, and software data/control registers.
- DPP0 and DPP1 converter/configuration: `CNVC_CFG*_CNVC_SURFACE_PIXEL_FORMAT`, format control, floating-point bias/scale, color keyer control and color values, alpha LUT, pre-dealpha, pre-CSC mode and matrix coefficients, coefficient format, pre-degamma, and pre-realpha.
- DPP0 and DPP1 converter cursor: `CNVC_CUR*_CURSOR0_CONTROL`, cursor colors, and cursor floating-point scale/bias.
- DPP0 and DPP1 scaler: coefficient RAM selection/data, scaler mode, tap control, DSCL control, 2-tap/manual replicate controls, horizontal/vertical scale ratio and init registers for luma/chroma, black color, update/autocal, overscan, OTG blanking, recout/MPC size, line-buffer data format/memory control, vertical counter, DSCL memory power, and output-buffer memory power.
- DPP0 and DPP1 color management: control, post-CSC matrices, gamut remap matrices, bias, gamma correction LUT controls, RAM A/B start/slope/base/end/offset/region registers, blender gamma LUT controls and regions, HDR multiplier, CM memory power, dealpha, coefficient format, shaper control, shaper offset/scale/LUT/index/write-enable, and shaper RAM A/B region definitions.
- DPP0 top-level: `DPP_TOP0_DPP_CONTROL`, soft reset, CRC values/control, and host read control.

## Control Flow

This header has no runtime control flow. Runtime sequencing comes from AMDGPU display code that includes this generated offset header and its companion shift/mask header.

Typical flow:

1. DCN316 resource and DMUB code include `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`.
2. `dcn316_resource.c` defines `DCN_BASE__INST0_SEG*`, then expands register-list macros such as `DPP_REG_LIST_DCN30(id)` and `HUBP_REG_LIST_DCN30(id)` into per-instance register tables.
3. Helper macros such as `SR`, `SRI`, and related variants combine `BASE(reg..._BASE_IDX)` with `reg...` offsets to produce absolute register addresses for AMDGPU DC objects.
4. Runtime code uses those populated tables through register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` while programming planes, flips, cursors, scaler state, color transforms, LUTs, memory power, perfmon counters, and fault/status paths.

The offset constants encode only addresses. They do not encode write ordering, double-buffering rules, read-only/write-one-to-clear semantics, or timing constraints. Those remain in the DC/HUBP/DPP implementation and hardware documentation.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It names MMIO-backed hardware state in the display controller:

- VM state: DCN VM context 15 end address, default fault target, fault control/status, and fault address registers.
- Plane surface state: HUBP/HUBPREQ surface pixel format, tiling/address config, pitches, luma/chroma primary and secondary surface addresses, metadata addresses, TMZ/DCC controls, flip controls, pending/in-use readbacks, viewport coordinates and dimensions, and cursor destination integration.
- Memory request and timing state: prefetch, vblank, flip, nominal delivery, TTU/QoS, destination-after-scaler, blank offsets, ref-to-pixel conversion, DMDATA VM handling, system aperture, and L1 TLB controls.
- Cursor state: cursor enable/mode, cursor surface address, size, position, hot spot, stereo behavior, memory power, DMDATA request state, and software data path.
- HUBPRET state: read-line tracking, return-path control, memory power, and interrupt/status registers.
- DPP conversion/scaling state: pixel format conversion, floating-point bias/scale, alpha/color keying, pre-CSC, pre-degamma/re-alpha, scaler coefficients, tap/ratio/init values, recout/MPC geometry, line-buffer format, and output-buffer/DSCL memory power.
- Color pipeline state: post-CSC, gamut remap, gamma-correction LUTs, blender gamma LUTs, shaper LUTs, HDR multiplier, dealpha, 3D LUT setup for DPP0, and CM memory power/status. The DPP1 CM shaper block is incomplete at this chunk boundary.
- Diagnostic state: DC perfmon controls/counters and DPP/HUBP debug/CRC/measurement registers.

Persistence is hardware-defined. Configuration usually survives until modeset reprogramming, power-gating, suspend/resume restore, or ASIC reset. Status, fault, interrupt, counter, and memory-power state may be sticky, self-clearing, read-only, write-one-to-clear, or sampled by hardware. This header does not describe those access classes.

## Dependencies And Integration Points

Companion generated metadata:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h`

Direct include sites found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`

Key integration points:

- `dcn316_resource.c` builds four DPP register tables with `DPP_REG_LIST_DCN30(id)` and four HUBP register tables with `HUBP_REG_LIST_DCN30(id)`. This chunk contains all HUBP/HUBPREQ/HUBPRET/CURSOR offsets for instances 0-3 and DPP offsets for instances 0-1; DPP instances 2-3 are outside this range.
- `dcn316_resource.c` pairs these offsets with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT/_MASK)` and `HUBP_MASK_SH_LIST_DCN31(__SHIFT/_MASK)`, so this chunk must remain synchronized with the DCN316 shift/mask header and the common DCN30/DCN31 DPP/HUBP field-list macros.
- `dmub_dcn316.c` includes the same generated namespace and expands DMUB register and field macros into `dmub_srv_dcn316_regs`; even where this exact chunk is not DMUB-specific, the base-index convention and generated names must remain consistent for the shared DCN316 register namespace.
- HUBP implementations such as the DCN10/DCN21/DCN31 HUBP code use fields from these offset families when setting surface addresses, metadata addresses, VMID, pitch, surface control, flip parameters, cursor state, and readback status.
- DPP implementations use the CNVC, DSCL, CM, DPP_TOP, and perfmon offsets when programming input pixel conversion, scaling, line-buffer layout, color transforms, gamma/blender/shaper LUTs, memory power state, CRC, and diagnostics.

## Risks And Edge Cases

- Generated-offset drift is the primary risk. A wrong offset or base index compiles cleanly but can program the wrong MMIO register, corrupt another pipeline, or make readback/status misleading.
- The chunk begins mid-register group. `regDCN_VM_CONTEXT15_PAGE_TABLE_START_ADDR_LO32_BASE_IDX` appears without its offset macro in this range, and the remaining VM macros are only the tail of a larger VM block.
- The chunk ends mid-register group. `CM1_CM_SHAPER_RAMB_REGION_14_15` is the last register here; later `CM1_CM_SHAPER_RAMB_REGION_*` entries and any following DPP1/DPP2 state must be merged from later chunks.
- HUBP/HUBPREQ offsets are plane-critical. Mistakes in surface addresses, metadata addresses, pitch, tiling, DCC/TMZ controls, viewport geometry, VMID, or flip controls can cause page faults, underflow, stale scanout, corruption, blanking, or secure-memory violations.
- Flip and in-use registers are sequencing-sensitive. Driver code must respect update locks, vblank timing, pending status, triple-buffering/GSL behavior, and hardware readback semantics; the generated offsets cannot enforce those rules.
- TTU/QoS/prefetch/vblank/nominal timing registers are tightly coupled to DML calculations. Incorrect offsets can produce memory underflow, late flips, or unstable high-refresh/multi-plane modes.
- Cursor and DMDATA registers mix visible cursor state, memory fetch state, QoS, and software data paths. Wrong programming can affect cursor composition without changing primary plane state.
- DPP scaler and color registers are dense and indexed. Coefficient RAM, gamma/blender/shaper LUT index/data pairs, RAM A/B regions, 3D LUT controls, and color matrix registers require correct ordering and banking; offset errors can produce color shifts, banding, or corrupted LUT loads.
- Memory power control/status registers are side-effectful. Writing control bits without waiting for matching status can race later register access, especially across suspend/resume and power-gating transitions.
- Perfmon registers are diagnostic but still stateful. Incorrect counter control or acknowledge offsets can leave interrupts asserted or make performance data invalid.

## Test Signals

Useful validation combines generated-header consistency checks, builds, and hardware behavior:

- Build AMDGPU/DC with DCN316 enabled. Missing or renamed macros should fail in `dcn316_resource.c`, `dmub_dcn316.c`, and common HUBP/DPP code that consumes DCN316 tables.
- Mechanically verify that every `reg...` offset macro in lines 2690-5205 has a matching `reg..._BASE_IDX` macro in the same range, while allowing the known leading boundary exception where a `_BASE_IDX` appears without its offset.
- Compare DCN316 offsets against AMD's authoritative generated register database and adjacent DCN 3.1.x headers where the same block instances are expected to align.
- Exercise plane enable/disable, primary and chroma address programming, metadata/DCC, flips, triple-buffering, VMID changes, cursor enable/move/format changes, and secure-surface/TMZ paths on DCN316 hardware. Watch for faults, underflow, stale frames, corruption, and missing flip completion.
- Exercise multi-plane and multi-display modes that use HUBP instances 0-3 and DPP instances 0-1, including scaling, chroma formats, rotation/tiling variants, and high-bandwidth modes that stress prefetch/TTU/QoS registers.
- Exercise DPP color features: pre-CSC/post-CSC, gamut remap, gamma correction, blender gamma, shaper LUTs, HDR multiplier, dealpha, color keying, and 3D LUT setup for DPP0. Validate visual output and LUT load completion/readback where available.
- Exercise suspend/resume, runtime power management, and memory power transitions for HUBPREQ/HUBPRET/CURSOR/DSCL/CM blocks. Check that status bits settle and that post-resume scanout, cursor, scaler, and color state are restored.
- Exercise perfmon and CRC/debug readbacks for the listed DC perfmon instances and DPP top-level registers. Confirm counters run/stop/ack correctly and diagnostics point to the expected hardware instance.

## Cross-Chunk Notes

This is a middle chunk of `dcn_3_1_6_offset.h`. It starts with the tail of a VM block and ends inside DPP1 CM shaper RAMB region offsets. The final per-file research document should merge this with neighboring chunks before making complete-file claims about all DCN VM registers, all DPP instances, or the full CM1 shaper/3D-LUT register coverage.

### subset-b-001892: lines 5206-7703

# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 5206-7703

## Scope

This chunk is a generated AMD DCN 3.1.6 register-offset header segment. It contains C preprocessor constants only: `reg...` register offsets and matching `reg..._BASE_IDX` segment selectors. There are no functions, structs, enums, or runtime branches in this range. Runtime behavior comes from other AMD display code that includes this header and expands the macros into MMIO register tables.

The range begins in the middle of the DPP1 color-management (`CM1`) block and then covers DPP1 top/perfmon, full DPP2 and DPP3 pixel-processing blocks, MPC/MPCC compositor blocks, MPCC output-gamma blocks, and the beginning of the MPC output CSC block.

## Purpose

The purpose is to bind symbolic DCN316 display-pipeline register names to hardware addresses. DCN display code uses these constants to populate per-IP register-table structs, then `REG_READ`, `REG_SET`, `REG_UPDATE`, and related helpers program display hardware without hard-coding numeric addresses in the functional code.

The `_BASE_IDX` value is as important as the offset value. In DCN316 resource setup, macros such as `SR`, `SRI`, and `SRII` compute an absolute register address as `BASE(reg..._BASE_IDX) + reg...`. For this chunk, DPP-side registers mostly use base segment index `2`, while MPC/MPCC-side registers use base segment index `3`.

## Register Blocks Covered

Visible block map in this chunk:

| Lines | Address block | Base address comment | Register coverage |
| --- | --- | --- | --- |
| 5206-5251 | Tail of DPP1 `CM1` color-management block | inherited from prior chunk | shaper RAMB region tail, secondary CM memory power, 3D LUT access/output offsets, CM debug index/data |
| 5253-5266 | `dce_dc_dpp1_dispdec_dpp_top_dispdec` | `0x5ac` | `DPP_TOP1` control, soft reset, CRC values/control, host read control |
| 5269-5288 | `dce_dc_dpp1_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` | `0x3e3c` | `DC_PERFMON12` counter control/state/value registers |
| 5291-5942 | DPP2 CNVC/CUR/DSCL/CM/DPP top/perfmon blocks | mostly `0xb58`, perfmon `0x43e8` | full DPP2 conversion, cursor, scaler, color-management, top, and perfmon offsets |
| 5983-6672 | DPP3 CNVC/CUR/DSCL/CM/DPP top/perfmon blocks | mostly `0x1104`, perfmon `0x4994` | full DPP3 conversion, cursor, scaler, color-management, top, and perfmon offsets |
| 6675-6800 | `dce_dc_mpc_mpcc0..3_dispdec` | `0x0`, `0x80`, `0x100`, `0x180` | four MPCC composition pipes, including top/bottom selection, OPP selection, alpha/gain/background, memory power, status |
| 6803-6872 | `dce_dc_mpc_mpc_cfg_dispdec` | `0x0` | global MPC clock/reset/CRC/perfmon/host-read/pending/vupdate-lock/DWB mux registers |
| 6875-6894 | `dce_dc_mpc_mpc_dcperfmon_dc_perfmon_dispdec` | `0x1901c` | `DC_PERFMON15` counter control/state/value registers |
| 6897-7614 | `dce_dc_mpc_mpcc_ogam0..3_dispdec` | `0x0`, `0x200`, `0x400`, `0x600` | four MPCC output-gamma blocks with OGAM LUT, RAM A/B region controls, and gamut-remap matrices |
| 7617-7703 | Start of `dce_dc_mpc_mpc_ocsc_dispdec` | `0x0` | MPC output mux/denorm for outputs 0-3 plus output CSC format and CSC matrix registers for outputs 0-1 |

The final `MPC_OUT` block is incomplete in this chunk: it stops at `regMPC_OUT1_CSC_C33_C34_B`. Output 2/3 CSC definitions should be expected in the next chunk.

## Important APIs, Types, And Macros

This file segment exports macros, not callable APIs. The important exported names are the register identifiers consumed by display resource tables:

- `regDPP_TOP1_*`, `regDPP_TOP2_*`, `regDPP_TOP3_*`: DPP top-level control, soft reset, CRC, and host-read registers.
- `regDC_PERFMON12_*`, `regDC_PERFMON13_*`, `regDC_PERFMON14_*`, `regDC_PERFMON15_*`: performance monitor counter controls and values for DPP1/DPP2/DPP3/MPC-related blocks.
- `regCNVC_CFG2_*`, `regCNVC_CFG3_*`: format conversion, floating-point bias/scale, color-key, alpha, pre-CSC, pre-degamma, and pre-realpha registers for DPP instances 2 and 3.
- `regCNVC_CUR2_*`, `regCNVC_CUR3_*`: cursor control/color/floating-point scale-bias registers.
- `regDSCL2_*`, `regDSCL3_*`: scaler coefficient RAM, mode, taps, scale ratios, filter init, overscan, recout, line-buffer, memory power, and output-buffer control registers.
- `regCM2_*`, `regCM3_*`: large color-management blocks, including post-CSC, gamut remap, degamma, regamma, blender gamma, HDR multiplier, shaper LUT/RAM, 3D LUT, memory power, and debug registers.
- `regMPCC0_*` through `regMPCC3_*`: four multi-plane composition cells.
- `regMPC_*`: global MPC clock/reset/CRC/perfmon/pending/update-lock/DWB and output mux/CSC registers.
- `regMPCC_OGAM0_*` through `regMPCC_OGAM3_*`: per-MPCC output gamma and gamut-remap register blocks.

Integration code observed in `display/dc/resource/dcn316/dcn316_resource.c` includes this header together with `dcn_3_1_6_sh_mask.h`. It defines `BASE`, `SR`, `SRI`, `SRII`, and related macros, then uses higher-level register-list macros such as `DPP_REG_LIST_DCN30(id)`, `MPC_REG_LIST_DCN3_0(inst)`, and `MPC_OUT_MUX_REG_LIST_DCN3_0(inst)` to initialize `dcn3_dpp_registers`, `dcn30_mpc_registers`, `dcn20_opp_registers`, and related tables.

`display/dmub/src/dmub_dcn316.c` also includes this offset header. DMUB uses the same `BASE(reg..._BASE_IDX) + reg...` pattern through `REG_OFFSET_EXP()` to fill `dmub_srv_dcn316_regs` for firmware-service register access.

## Control Flow

There is no executable control flow in this chunk. The effective control flow is compile-time macro expansion:

1. A DCN316 source file includes `dcn_3_1_6_offset.h`.
2. The source defines the DCN base-segment constants, for example `DCN_BASE__INST0_SEG2` and `DCN_BASE__INST0_SEG3`.
3. Register-list macros in functional headers expand symbolic names into struct initializers.
4. Each initializer combines `BASE_IDX` with the raw offset to produce an absolute register address.
5. Runtime display code uses the populated structs through common register helpers to read or write MMIO.

This separation lets most display logic share DCN generation code while swapping in ASIC-specific offset and field-mask headers.

## State And Persistence Behavior

The macros themselves hold no state and persist only as compile-time constants. The state they address is hardware state:

- DPP CNVC/DSCL/CM registers configure per-plane pixel conversion, cursor color interpretation, scaling, LUTs, CSC matrices, alpha handling, and memory-power state.
- DPP top and perfmon registers expose control/reset, CRC readback, host-read behavior, and performance counters.
- MPCC registers define composition routing: which DPP feeds the top/bottom of each MPCC, which OPP consumes the result, blending/gain/background controls, update-lock selection, memory power, and status.
- MPC global registers expose compositor clock/reset, CRC, pending status, vertical update lock sets for plane/config/cursor/address state, and DWB muxing.
- MPCC OGAM and MPC output CSC registers persist programmed output color transforms until changed, reset, or power-gated.

The persistence boundary is therefore the display hardware block, not any software object in this header. Incorrect constants can corrupt live hardware programming, but the header itself does not allocate memory or store runtime data.

## Dependencies

Direct dependencies are structural rather than included from this chunk:

- `dcn_3_1_6_sh_mask.h` supplies field masks and shifts for the same symbolic register names.
- DCN316 resource setup defines base segments used by `_BASE_IDX`.
- `reg_helper.h` and display register helper macros consume the resolved register addresses.
- DPP register-list definitions in `display/dc/dpp/dcn30/dcn30_dpp.h` reference many `CNVC`, `CUR`, `DSCL`, `CM`, and `DPP_TOP` names from this chunk.
- MPC register-list definitions in `display/dc/mpc/dcn30/dcn30_mpc.h` reference the `MPCC`, `MPC`, `MPCC_OGAM`, and `MPC_OUT` names from this chunk.
- DMUB DCN316 register setup consumes this same ASIC offset map for firmware service access.

The numeric constants are also implicitly coupled to AMD hardware register specifications and to sibling generated headers for other ASIC versions. Similar symbolic names appear in other DCN offset headers, but some numeric offsets differ by ASIC generation.

## Integration Points

Primary integration points:

- `display/dc/resource/dcn316/dcn316_resource.c`: builds DCN316 register tables for DPP, OPP, MPC, HUBP, HUBBUB, DCCG, AUX, DSC, DWB, and related display components. This chunk directly feeds the DPP and MPC portions visible in that file.
- `display/dc/dpp/dcn30/dcn30_dpp.c` and related DPP headers: functional code programs CM shaper regions, LUTs, CSC coefficients, scaler controls, and DPP top controls through register-table fields backed by this header.
- `display/dc/mpc/dcn10/dcn10_mpc.c`, `dcn20_mpc.c`, and `dcn30_mpc.c`: shared MPC code reads/writes MPCC routing, blending, mux, and status registers. For example, `MPCC_TOP_SEL` is used to attach/detach DPP inputs and to snapshot MPCC state.
- `display/dmub/src/dmub_dcn316.c`: exposes a DCN316-specific register map to DMUB service code.

The chunk is part of a larger single header, so adjacent chunks provide earlier DPP0/DPP1 definitions and later MPC output CSC continuation plus other display blocks. A final per-file report should merge these cross-chunk relationships.

## Risks And Edge Cases

- Generated-address drift: if any offset or `_BASE_IDX` is wrong, the driver will access the wrong MMIO register. Effects range from bad color/scaling to display hangs.
- Segment-index errors are high impact because the offset may look plausible but resolve into the wrong DCN base segment.
- DPP2/DPP3 blocks are repetitive but not interchangeable. Copy/paste or generator mistakes can silently route instance 2 operations to instance 3 addresses or vice versa.
- The chunk starts mid-`CM1` block. Any chunk-level analysis must avoid treating the visible CM1 subset as the full DPP1 color-management register set.
- The chunk ends mid-`MPC_OUT` block. Output 0 and 1 CSC definitions are visible here, but output 2 and 3 CSC definitions are outside this range.
- Color pipeline registers often require coordinated programming order and update locks. This header does not encode those sequencing rules; they live in DPP/MPC functional code.
- Performance monitor and CRC registers are readback/control surfaces. Wrong offsets can create misleading diagnostics even when normal display output appears functional.
- Many registers have paired mask/shift definitions in `dcn_3_1_6_sh_mask.h`; offset names must remain synchronized with those field definitions.

## Test Signals

Useful validation signals for this chunk:

- Build coverage: compile DCN316 display code that includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`; missing or misspelled macros should fail at compile time in resource table initializers.
- Register-table sanity: confirm `dcn316_resource.c` initializes DPP instances 0-3 and MPC/MPCC instances 0-3 without unresolved symbols from `DPP_REG_LIST_DCN30`, `MPC_REG_LIST_DCN3_0`, or `MPC_OUT_MUX_REG_LIST_DCN3_0`.
- Hardware smoke tests: exercise multi-plane composition, scaling, cursor, color management, output CSC, and display wake/reset paths on DCN316 hardware.
- Visual/color tests: verify degamma/regamma, shaper LUT, 3D LUT, gamut remap, HDR multiplier, and output CSC behavior with known test patterns.
- Diagnostic tests: read DPP/MPC CRC and perfmon counters to ensure the register map supports expected debug telemetry.
- Power-management tests: validate `*_MEM_PWR_CTRL` and `*_MEM_PWR_STATUS` behavior across blanking, idle, suspend/resume, and display reconfiguration.

## Chunk-Specific Notes For Merge

This report should be merged with adjacent chunks for the final per-file document. Important cross-chunk boundaries:

- The visible `CM1` definitions are only the tail of DPP1 color management.
- DPP2 and DPP3 appear complete in this range.
- MPCC0-3, MPC global config, DC_PERFMON15, and MPCC_OGAM0-3 appear complete in this range.
- `MPC_OUT` is partial and continues after line 7703.

### subset-b-001893: lines 7704-10281

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 7704-10281

## Scope

This chunk is a middle slice of the generated DCN 3.1.6 register offset header `dcn_3_1_6_offset.h`. It contains C preprocessor constants only: `reg*` address offsets, matching `reg*_BASE_IDX` segment selectors, and address-block comments. There are no C functions, structs, enums, branches, allocations, or software-owned data structures in this range.

The slice starts on the `_BASE_IDX` macro for the preceding `regMPC_OUT1_CSC_C33_C34_B` definition, then covers MPC output CSC tail registers, the MPC RMU shaper/3D LUT blocks, four ABM/OPP instances, OPP formatter and CRC surfaces, ODM input blocks, four OTG timing generators, miscellaneous OPTC/OPP registers, five HPD blocks, DP0/DIG0 link-encoder registers, and the beginning of DP1. It ends at `regDP1_DP_SEC_FRAMING2` before that register's `_BASE_IDX`, so both boundaries depend on neighboring chunks for complete macro pairs.

## Purpose And Hardware Surface

The purpose of this header range is to provide the address side of the AMDGPU Display Core hardware ABI for DCN 3.1.6. Driver code and DMUB register tables use these macros with the companion `dcn_3_1_6_sh_mask.h` field definitions to calculate MMIO addresses and field encodings without embedding raw offsets at call sites.

Major hardware areas represented here:

- MPC output color-space conversion and output CSC debug registers. The chunk finishes `MPC_OUT2` and `MPC_OUT3` CSC mode/matrix coefficient A/B registers and exposes `MPC_OCSC_TEST_DEBUG_INDEX/DATA`.
- `dce_dc_mpc_mpc_rmu_dispdec` registers. Two RMU instances provide shaper LUT programming, RAM A/B start/end/region tables, 3D LUT index/data windows, 30-bit data, read/write control, output normalization, and RGB output offsets.
- `dce_dc_opp_abm[0-3]_dispdec` registers. Four ABM blocks define PWM levels, ABM control, IPCSC coefficient selection, ACE slopes/thresholds, histogram/luma statistics readback, sample-rate controls, histogram bin metadata/results, and backlight master locks.
- OPP per-pipe output blocks for instances 0-3: display pattern generator (`DPG`), formatter (`FMT`), OPP buffer (`OPPBUF`), pipe control, and pipe CRC registers.
- DSC forwarding/control surfaces: `DSCRM0..2_DSCRM_DSC_FORWARD_CONFIG`, `OPP_TOP_CLK_CONTROL`, `OPP_ABM_CONTROL`, and `DC_PERFMON16_*`.
- ODM and OTG blocks. `ODM0..3` select OPTC input source/format/width/clock/memory settings. `OTG0..3` define timing, trigger, status, snapshot, interrupt, update-lock, CRC, static-screen, 3D, GSL, DRR, DTO, DSC start-position, pipe-update, and spare registers.
- Miscellaneous OPTC/OPP registers: `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_*`, `OPTC_MISC_SPARE_REGISTER`, and `DC_PERFMON17_*`.
- DIO hotplug and link encoder blocks. `HPD0..4` expose interrupt status/control, control, and toggle filtering. `DP0` and the beginning of `DP1` cover DisplayPort link/video/DPHY/secondary-data/audio/info/GSP controls, and `DIG0` covers DIG front/back-end, HDMI, AFMT, TMDS, CRC, test-pattern, FIFO, and force-disable registers.

## Important Definitions

The exported API is the generated macro convention:

- `reg<NAME>` is the DCN 3.1.6 register offset.
- `reg<NAME>_BASE_IDX` selects the base segment used by `BASE(reg<NAME>_BASE_IDX)`.
- Address comments such as `// addressBlock: dce_dc_optc_otg0_dispdec` identify the hardware block whose registers follow.
- Runtime code normally computes an MMIO address as `BASE(regFOO_BASE_IDX) + regFOO`, as shown by `REG_OFFSET_EXP` in `display/dmub/src/dmub_dcn316.c`.

Important register families in this chunk:

- `regMPC_OUT2_CSC_*` and `regMPC_OUT3_CSC_*` provide output CSC mode and packed matrix coefficient addresses for two MPC outputs. Each output has A and B coefficient banks for rows `C11_C12` through `C33_C34`.
- `regMPC_RMU_CONTROL`, `regMPC_RMU_MEM_PWR_CTRL`, `regMPC_RMU0_*`, and `regMPC_RMU1_*` describe RMU control, memory power, two shaper LUTs, dual RAM region tables, and two 3D LUT programming windows from offsets `0x0680` through `0x0701`, all in base index 3.
- `regABM0_*` through `regABM3_*` repeat the same 60-register ABM layout at offsets `0x0e7a..0x0eb6`, `0x0ebb..0x0ef7`, `0x0efc..0x0f38`, and `0x0f3d..0x0f79`. The repeated stride maps independent ABM/OPP instances.
- `regDPG[0-3]_*`, `regFMT[0-3]_*`, `regOPPBUF[0-3]_*`, `regOPP_PIPE[0-3]_OPP_PIPE_CONTROL`, and `regOPP_PIPE_CRC[0-3]_*` repeat per-output-pipe control, formatting, buffering, test pattern, and CRC capture surfaces in base index 2.
- `regODM[0-3]_OPTC_*` define OPTC input-side global control, data source, data format, bytes per pixel, width, input clock, memory config, and spare registers.
- `regOTG[0-3]_OTG_*` are the largest group in this chunk. Each OTG instance has 105 registers covering horizontal/vertical totals, blank/sync timing, variable refresh totals, trigger controls, flow/stereo/interlace state, counters, snapshots, vertical interrupts, CRC windows/results/masks, static-screen detection, global sync, GSL, DRR, M/N DTO, request control, DSC start position, and pipe update status.
- `regHPD[0-4]_DC_HPD_*` provide five hotplug-detect interrupt/control/filter register sets.
- `regDP0_DP_*` includes DP link control, pixel format, MSA metadata, video timing/N/M, DPHY training/scrambling/CRC, secondary-data/audio/MSE/SST/MST controls, GTC sync, ALPM, and GSP controls. `regDIG0_*` maps the paired digital encoder/HDMI/TMDS block. The chunk then starts the equivalent `regDP1_DP_*` block at base address `0x400`.

## Control Flow And State Behavior

This header has no executable control flow. Runtime behavior appears only when Display Core, DMUB, or lower register helpers expand these macros into MMIO reads and writes.

A typical path is:

1. DCN316 support selects `dmub_srv_dcn316_regs`.
2. The register table expands names through `REG_OFFSET_EXP(reg_name)`.
3. `REG_OFFSET_EXP` uses the offset and base index from this header to calculate a physical register address.
4. Field packing/extraction comes from the companion `dcn_3_1_6_sh_mask.h` header.
5. Hardware latches, reports, clears, or samples the corresponding display state.

The state represented here is hardware state rather than persistent software state:

- Persistent configuration includes CSC matrices, RMU shaper/3D LUT contents, ABM PWM/user/target levels, ACE and histogram setup, formatter clamp/dither/420/422 controls, OPP buffer and pipe controls, ODM input routing, OTG timing totals, interrupt positions, update locks, global sync, DRR, DP link/stream configuration, HDMI/AFMT/TMDS setup, and HPD filtering.
- Volatile readback/status includes ABM current/final levels and histogram/luma results, OPP/OTG CRC results, OTG counters and positions, snapshot/status registers, perfmon counters, HPD interrupt/status bits, DP DPHY CRC/training/status, HDMI status, DIG FIFO status, and GSP double-buffer status.
- Side-effecting or sequencing-sensitive registers include LUT index/data windows, RMU/ABM memory power controls, ABM lock registers, OTG update/master locks, interrupt/status controls, counter resets, manual triggers, HPD interrupt acknowledge/control paths, DPHY training controls, DP secondary-data enables, and HDMI/AFMT packet controls.

The sequencing rules are not encoded in the offsets. Callers must still obey display power gating, clock availability, vblank/update-lock timing, double-buffering rules, link-training state, audio packet timing, HPD interrupt ordering, and instance ownership.

## Dependencies And Integration Points

This chunk depends on the companion field-layout header `dcn_3_1_6_sh_mask.h`; offsets from this file are useful only when paired with masks and shifts for the same register revision. It also depends on the base segment constants used by `BASE()` in DCN316 code. In `display/dmub/src/dmub_dcn316.c`, those base constants are `DCN_BASE__INST0_SEG0` through `DCN_BASE__INST0_SEG5`, and `REG_OFFSET_EXP` combines `BASE_IDX` plus offset to populate `dmub_srv_dcn316_regs`.

Known integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which directly includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h` and builds the DCN316 DMUB register table.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c`, which selects `dmub_srv_dcn316_regs` for `DMUB_ASIC_DCN316`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c`, which maps the ASIC to `DMUB_ASIC_DCN316` and names the `amdgpu/dcn_3_1_6_dmcub.bin` firmware.
- DCN316 resource, clock-manager, link-encoder, timing-generator, ABM/backlight, audio/HDMI, HPD interrupt, and diagnostics code that uses generated register lists or DMUB table entries to program these hardware blocks indirectly.
- Cross-revision generated headers in the same `asic_reg/dcn` directory. Similar blocks exist for other DCN revisions, but the exact offsets, instance count, and base-index mapping must remain DCN 3.1.6-specific.

Because this file is generated, missing or misspelled macros often fail at compile time in register-list expansions. Wrong numeric offsets or base indices can compile cleanly and instead misdirect live MMIO accesses.

## Risks And Maintenance Notes

- Numeric drift from the authoritative DCN 3.1.6 register database is the main risk. A wrong offset can program a valid but unrelated register, especially in dense repeated OTG/OPP/DP blocks.
- Base-index drift is as dangerous as offset drift. Most MPC/RMU/ABM registers in this chunk use base index 3, while OPP/OPTC/DIO blocks use base index 2. Copying an offset without its matching `_BASE_IDX` changes the calculated MMIO segment.
- This chunk starts and ends on incomplete macro pairs. The merge lane should join it with adjacent chunks before making whole-file claims about `regMPC_OUT1_CSC_C33_C34_B` or `regDP1_DP_SEC_FRAMING2`.
- Repeated instance names are easy to confuse. `ABM0..3`, `DPG0..3`, `FMT0..3`, `OPPBUF0..3`, `OPP_PIPE_CRC0..3`, `ODM0..3`, `OTG0..3`, `HPD0..4`, and `DP0/DP1` use similar register names with shifted offsets.
- Timing-generator registers affect active display timing. Incorrect `OTG_*` totals, locks, trigger controls, vertical interrupt positions, or DRR ranges can cause blanking, underrun-like symptoms, missed vblank events, or broken variable refresh behavior.
- LUT and histogram programming registers are index/data style surfaces. Callers must sequence index, data, write-enable/readback, and lock registers correctly; offsets alone do not protect against stale or partial updates.
- HPD and link-encoder registers interact with external displays. Wrong HPD interrupt or DP training offsets can break hotplug detection, link training, MST/SST setup, secondary-data packets, audio, or ALPM/GSP behavior.
- HDMI/AFMT/TMDS registers are adjacent to DIG front/back-end controls. Mistaking packet-control, ACR, generic-packet, TMDS, or DIG disable addresses can create display audio or signaling failures that are hard to attribute to an offset error.
- OPP and OTG CRC registers are diagnostic but are also used for validation. Incorrect offsets may produce false CRC mismatches or mask real display corruption.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Full AMDGPU Display Core build with DCN316 enabled. This catches missing macro names, malformed generated definitions, and broken include dependencies.
- Regeneration or static diff against the authoritative DCN 3.1.6 register source, checking both `reg*` offsets and `reg*_BASE_IDX` values.
- Cross-revision comparison against neighboring DCN offset headers for blocks expected to be layout-compatible, while confirming DCN316-specific deltas are intentional.
- Boot/runtime testing on DCN 3.1.6 hardware with DMUB enabled, verifying that `dmub_srv_dcn316_regs` initializes and basic display bring-up succeeds.
- Display timing tests across multiple pipes: mode set, vblank interrupt delivery, variable refresh/DRR behavior, GSL/global sync if available, OTG update-lock behavior, and CRC readback sanity.
- Backlight/ABM tests: PWM level changes, ABM enable/disable, histogram/luma readback, no stuck ABM locks or update-pending state, and stable brightness transitions.
- Color pipeline tests: CSC updates, RMU shaper/3D LUT programming, formatter dither/clamp/420/422 behavior, and visual or CRC confirmation that only intended pipes are affected.
- Hotplug/link tests for HPD0-4 and DP0/DP1: connect/disconnect interrupts, DP link training, MST/SST streams, secondary-data packets, audio infoframes/ACR, HDMI/TMDS output, and ALPM/GSP behavior where supported.
- Register dumps before and after representative operations. Calculated addresses should land in the expected base segment and adjacent instance offsets should not change unexpectedly.

## Open Questions For Merge

- Earlier chunks are needed to describe the beginning of the MPC OUT CSC table and the complete header-level include guard/license context.
- Later chunks are needed to finish `regDP1_DP_SEC_FRAMING2_BASE_IDX` and the remaining DP/DIG/HDMI/audio blocks for other link instances.
- This chunk documents register addresses only. The final merged report should connect these addresses to actual register-list consumers and field semantics from `dcn_3_1_6_sh_mask.h` without inferring bit-level behavior from offsets alone.

### subset-b-001894: lines 10282-12823

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 10282-12823

## Scope

This chunk is a generated AMD DCN 3.1.6 register-offset header segment. It contains preprocessor constants only: each hardware register has a `reg...` offset macro and a paired `reg..._BASE_IDX` macro used by AMDGPU display code to compute the final MMIO address from a DCN base segment plus a per-register offset.

The requested slice covers 2,542 source lines and 2,390 `#define` lines: 1,195 register-offset macros and 1,195 matching base-index macros. All base-index values in this slice are `2`, meaning the consumers add the offsets to `DCN_BASE__INST0_SEG2` through the local `BASE(reg..._BASE_IDX)` expansion in DCN316 resource and DMUB code.

The chunk starts in the middle of the `DP1` DisplayPort encoder register family at `regDP1_DP_SEC_FRAMING2_BASE_IDX`, then covers the tail of `DP1`, complete `DIG1`, `DP2`, `DIG2`, `DP3`, `DIG3`, `DP4`, and `DIG4` blocks, AFMT/DME/VPG blocks for DIG0-DIG4, AUX0-AUX4, DOUT I2C, DIO misc/perfmon, DCIO common/chip GPIO, complete UNIPHY0-UNIPHY4 reserved macro-control ranges, and the first half of UNIPHY5. It ends at `regDCIO_UNIPHY5_UNIPHY_MACRO_CNTL_RESERVED30`; the `_BASE_IDX` for that register and UNIPHY5 reserved registers 31-57 continue after the requested range.

## Purpose

The purpose of this header segment is to give DCN316 display code compile-time names for MMIO offsets in the digital I/O path. These offsets are the address side of the generated register API; companion shift/mask headers define field packing. Driver code uses these macros to populate register tables for DisplayPort, HDMI/TMDS, stream encoders, audio metadata, AUX/I2C engines, GPIO/HPD/DDC pads, DCIO link routing, and UNIPHY link encoders.

This file does not implement algorithms. Its correctness is still operationally critical: if a generated offset or base index is wrong, higher-level C code can compile cleanly while programming the wrong hardware register.

## Register Families And Important Macros

The DisplayPort and stream-encoder portion covers:

- Tail of `DP1`, from secondary-data packet framing/audio timestamp registers through MSE/MST rate and slot-allocation table registers, MSA timing registers, MSO/DSC control, ALPM, generic secondary-packet controls `GSP8`-`GSP11`, and double-buffer status.
- Complete `DP2`, `DP3`, and `DP4` families, each with link control, pixel format, MSA colorimetry/misc/VBID, video stream control, DPHY training/scrambling/CRC/fast-training, secondary-data packet/audio registers, MST/MSE controls, MSO and DSC controls, metadata transmission, ALPM, and generic secondary packet controls.
- Complete `DIG1` through `DIG4` families, each with front-end control, output CRC, clock/test/random patterns, FIFO status, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet controls, HDMI general control/status, TMDS control characters/sync/DC-balancer/control-bit registers, version, and force-disable.
- `AFMT0` through `AFMT4` audio-format blocks, including VBI/audio packet controls, audio info, IEC 60958 channel-status words, audio CRC, ramp controls, status, interrupt status, audio source control, and AFMT memory power.
- `DME0` through `DME4` with `DME_CONTROL` and `DME_DATA`, and `VPG0` through `VPG4` with generic-packet control/status, `VPG_GSP_FRAME_UPDATE`, and generic packet header/sub registers 0-7.

The link-side support blocks cover:

- `DP_AUX0` through `DP_AUX4`, each with AUX arbitration, control, software data, software control/reply data, interrupt control, transaction status, firmware status, low-level debug, PHY wake, and timeout-period registers.
- `dce_dc_dio_dout_i2c_dispdec`, including DDC/AUX software status for channels 1-5, DC GPIO AUX control registers, and HPD enable/rx interrupt/generic control registers for HPD1-HPD5.
- `dce_dc_dio_dio_misc_dispdec`, including `DIG_BE_CLK_CNTL`, `DIO_MEM_PWR_CTRL`, `DIO_INTERRUPT_CNTL`, display clock/gating control, test debug data/control, DCIO test debug index/data, DCIO debug clock control, DCFE/DCHUBBUB debug remap, DCIO debug control, and DCIOMON config/data.
- `DC_PERFMON18`, with performance monitor counter control/state, clock and counter enable, event selection, trigger/status, current-value interrupt, current-value low/high, and sampled low/high counter registers.

The DCIO and PHY-facing portion covers:

- `dce_dc_dcio_dcio_dispdec`, with generic DC registers, DCIO and reference-clock control, UNIPHYA through UNIPHYG link control and channel crossbar controls, write-command delay, DC pinstraps, intercept state, global swaplock/genlock pad control, backlight PWM frame-start display selection, and DCIO soft reset.
- `dce_dc_dcio_dcio_chip_dispdec`, with generic GPIO, DDC1-DDC5 and DDCVGA GPIO mask/A/enable/Y registers, genlock GPIO, HPD GPIO, panel power-sequence enables, pad strength, PHY AUX control, TX/RX/pullup controls, AUX control 0-5, and `AUXI2C_PAD_ALL_PWR_OK`.
- `dce_dc_dcio_dcio_uniphy0_dispdec` through `uniphy4`, each defining contiguous `DCIO_UNIPHYx_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57` offsets.
- The beginning of `dce_dc_dcio_dcio_uniphy5_dispdec`, defining `DCIO_UNIPHY5_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED30` at the chunk boundary.

## Important APIs, Types, And Consumers

There are no functions, structs, or callable APIs in this header segment. The generated macro names are nevertheless consumed as a compile-time API by table-building macros in DCN316 code.

Important consumers found in the source tree include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes `dcn/dcn_3_1_6_offset.h` and `dcn/dcn_3_1_6_sh_mask.h`.
- The local `SR`, `SRI`, `SRII`, and related macros in `dcn316_resource.c`, which expand names like `regDP2_DP_LINK_CNTL` and `regDP2_DP_LINK_CNTL_BASE_IDX` into final register addresses.
- `stream_enc_regs[]`, populated by `SE_DCN3_REG_LIST(id)`, which uses the `DIG*` and `DP*` register families for stream encoder construction.
- `audio_regs[]`, `vpg_regs[]`, and `afmt_regs[]`, populated by `AUD_COMMON_REG_LIST`, `VPG_DCN31_REG_LIST`, and `AFMT_DCN31_REG_LIST`.
- `link_enc_aux_regs[]`, `aux_engine_regs[]`, and `i2c_hw_regs[]`, populated by AUX and I2C common register-list macros for connector discovery, DDC, AUX transactions, and link training support.
- `link_enc_regs[]`, populated by `LE_DCN31_REG_LIST`, `UNIPHY_DCN2_REG_LIST`, and DPCS lists; this is where the DCIO/UNIPHY link-control offsets participate in link encoder setup.
- `dio_regs`, populated by `DIO_REG_LIST_DCN10()`, which uses the DIO misc offsets such as `DIO_MEM_PWR_CTRL`.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which includes the same offset and sh/mask headers and builds `dmub_srv_dcn316_regs` with `REG_OFFSET_EXP(reg_name)`.

## Control Flow And Runtime Behavior

This header has no direct control flow. Runtime behavior appears when constructors bind these offsets into block-specific register tables and later hardware-object methods read or write those addresses through AMDGPU register helpers.

The typical flow is:

1. DCN316 resource construction includes the generated offset/sh/mask headers and defines `DCN_BASE__INST0_SEG*` values.
2. Register-list macros expand into static register-table instances, combining `BASE(reg..._BASE_IDX)` with `reg...` offsets.
3. Resource constructors pass those tables to hardware-object constructors such as `dcn10_dio_construct`, `dcn31_link_encoder_construct`, `dcn30_dio_stream_encoder_construct`, `dce_audio_create`, `vpg31_construct`, `afmt31_construct`, `dce110_aux_engine_construct`, and `dcn2_i2c_hw_construct`.
4. Link detection, HPD handling, DP AUX/DDC transactions, DisplayPort link training, HDMI/TMDS programming, secondary packet setup, audio-infoframe programming, VPG packet generation, and DCIO/UNIPHY link routing use the stored addresses through register-helper calls.
5. DMUB service initialization similarly turns selected macro names into the DCN316 register map used by firmware-facing display microcontroller code.

The hardware flows represented by this chunk include DP link/stream configuration, DP training/debug/CRC, MST slot allocation and rate programming, DSC/MSO transport controls, HDMI packet and ACR programming, audio packet/AFMT control, generic secondary packet transmission, AUX/DDC/I2C transactions, HPD and GPIO control, DCIO memory/clock/reset/debug control, performance counter reads, and UNIPHY link macro access.

## State And Persistence

The macros themselves hold no state and allocate no storage. They name registers whose values are persistent hardware state after writes by consumers.

Stateful hardware represented by this chunk includes:

- DisplayPort link configuration, training pattern selection, scrambler state, CRC enable/results, fast-training status, MST/MSE slot-allocation tables, MSO/DSC transport controls, ALPM controls, and secondary packet configuration.
- HDMI/TMDS state including metadata, audio, ACR, VBI/infoframe, generic-packet, general-control, and TMDS control-character programming.
- AFMT audio packet, IEC 60958, ramp, CRC, interrupt, source-control, and memory-power state.
- VPG packet headers/sub-packets and generic-packet update state.
- AUX and I2C engine transaction status, software reply data, interrupt controls, arbitration controls, timeout periods, and firmware/PHY wake status.
- HPD/DDC/GPIO register state, including input/output enable/mask/value registers and pad controls.
- DIO/DCIO clock, memory power, soft-reset, debug, pinstrap, genlock/swaplock, and reference-clock controls.
- `DC_PERFMON18` counter configuration and sampled counter state.
- UNIPHY macro-control reserved register values, which are low-level PHY/link state even though this generated header exposes them under reserved names.

These values persist until overwritten, reset by display or GPU reset paths, affected by power-gating/suspend-resume sequencing, or reinitialized during mode set, link retraining, connector hotplug handling, or DMUB/DC resource reconstruction.

## Dependencies And Integration Points

This chunk depends on the rest of the generated DCN316 register set and on common display block abstractions:

- `dcn_3_1_6_sh_mask.h` supplies companion field shifts and masks for the same registers.
- `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h` are included alongside this header for DPCS link encoder registers in DCN316 resource construction.
- `dcn316_resource.c` defines the base-segment constants and the `BASE(...)` expansion needed to turn `_BASE_IDX` values into final addresses.
- Stream encoder, link encoder, AUX, I2C, DIO, audio, AFMT, VPG, APG, HPD, and DPCS register-list macros come from the AMD display block headers included by `dcn316_resource.c`.
- `amdgpu_dm.c` selects the DCN316 resource pool and DMUB firmware path for matching ASICs, so this generated register map is part of the platform bring-up path.
- `dmub_dcn316.c` uses the same offset naming convention to create DMUB's DCN31-family register descriptor table.

The macro names are the integration contract. Removing or renaming a macro referenced by a register-list initializer causes a build failure. Changing a numeric offset or base index can pass compilation but break runtime register programming.

## Risks And Edge Cases

- The chunk starts and ends on partial logical families. The previous chunk contains the beginning of `DP1`, and the next chunk contains the paired `_BASE_IDX` for `regDCIO_UNIPHY5_UNIPHY_MACRO_CNTL_RESERVED30` plus the remaining UNIPHY5 reserved range. Merge documentation should not treat either family as complete from this chunk alone.
- Instance parity matters. `DP2`-`DP4`, `DIG1`-`DIG4`, `AFMT0`-`AFMT4`, `VPG0`-`VPG4`, `AUX0`-`AUX4`, HPD/DDC channels, and UNIPHY0-5 are structurally repeated. A generation error affecting only one instance may appear only on a specific connector, stream encoder, or PHY lane.
- Offsets and base indices are coupled. Every offset in this range pairs with base index `2`; changing either side can silently move accesses into unrelated MMIO space.
- Some registers are status or latch registers rather than plain configuration. AUX transaction status, HPD interrupt state, DP CRC results, perfmon counters, AFMT interrupts, and DIO/DCIO debug readback require correct read/clear/enable ordering in consumers.
- Reserved UNIPHY macro-control registers are especially risky because their semantic meaning is not visible in the generated name. Code should rely on the established link encoder/PHY abstractions instead of open-coding writes to those offsets.
- DP and HDMI packet-control registers affect protocol-visible data. Incorrect offsets can break audio, infoframes, HDR/metadata transport, MST allocation, DSC/MSO transport, or link training in ways that may depend on monitor capability.
- AUX/I2C and HPD/GPIO offsets are on the connector-discovery path; mistakes can look like EDID read failures, hotplug failures, or intermittent link training rather than a straightforward register-map bug.

## Test Signals

Useful validation signals for this chunk are mostly build, generated-header parity, and hardware display tests:

- Build the DCN316 AMDGPU display objects to catch missing or renamed `DP*`, `DIG*`, `AFMT*`, `VPG*`, `DP_AUX*`, `DC_GPIO*`, `DCIO*`, and `UNIPHY*` macros referenced by register-list initializers.
- Run generated-header consistency checks that every `reg...` offset in this range has a matching `reg..._BASE_IDX`, paying special attention to the line-range boundary where `regDCIO_UNIPHY5_UNIPHY_MACRO_CNTL_RESERVED30_BASE_IDX` is outside this chunk.
- Compare repeated instance families for expected stride/parity: `DP2`/`DP3`/`DP4`, `DIG1`/`DIG2`/`DIG3`/`DIG4`, `AFMT0`-`AFMT4`, `VPG0`-`VPG4`, `AUX0`-`AUX4`, and UNIPHY reserved blocks.
- Exercise connector hotplug, HPD interrupt handling, EDID reads over DDC/AUX, DP link training at multiple link rates/lane counts, AUX retry/timeout paths, and suspend/resume connector rediscovery.
- Exercise DP MST, MSE slot-allocation updates, MSO and DSC transport control, ALPM, DP secondary data/audio timestamps, metadata transmission, and DP CRC/debug paths.
- Exercise HDMI/TMDS output with audio, ACR for 32/44.1/48 kHz families, AVI/audio/vendor infoframes, generic packets, deep color, and TMDS test/CRC/debug paths.
- Exercise AFMT and VPG packet paths, including audio CRC/status/interrupt handling and generic packet frame-update behavior.
- Exercise DCIO/UNIPHY link encoder routing on every physical transmitter and validate that channel crossbar/link-control programming matches the selected connector.
- Use perfmon18 readback with a known event selection to validate counter enable/trigger/current-value/high-low register addressing.

## Open Questions For Merge Lane

- Confirm the previous chunk documents the start of `DP1` through `regDP1_DP_SEC_FRAMING2`.
- Confirm the next chunk completes `UNIPHY5` reserved registers 30-57 and captures the missing base-index macro for `RESERVED30`.
- In the final per-file report, group this slice as part of the DCN316 DIO/DCIO/link-encoder offset map rather than as standalone executable code.

### subset-b-001895: lines 12824-15508

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 12824-15508

## Purpose

This chunk is generated AMD DCN 3.1.6 register-offset metadata. It has no executable C logic; it publishes preprocessor constants that map display, DSC, HPO link, VGA, and Azalia audio register names to numeric offsets and, for MMIO-style `reg*` entries, to a `*_BASE_IDX` segment selector. Driver code combines these constants with DCN316 base-address tables and the matching `dcn_3_1_6_sh_mask.h` field definitions to build hardware register tables and perform read/write access.

The requested range covers 2,685 source lines and 2,345 `#define` entries. Within the chunk there are 713 `reg*` offset definitions, 714 companion `*_BASE_IDX` definitions, and 918 `ix*` indirect-index definitions. The count is intentionally not symmetric because the chunk starts inside `DCIO_UNIPHY5_UNIPHY_MACRO_CNTL_RESERVED30_BASE_IDX` and ends inside `azf0inputendpoint1_inputendpointind`.

Although the source path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or exported runtime symbols in this range. The public surface is the generated macro naming convention:

- `reg<REGISTER>`: DCN display-engine register offset within a base segment.
- `reg<REGISTER>_BASE_IDX`: index into the ASIC base segment table used by helper macros such as `BASE(reg..._BASE_IDX)`.
- `ix<REGISTER>`: indirect register index, commonly for VGA and Azalia codec/stream/endpoint spaces rather than direct DCN MMIO.

Major macro groups in this chunk:

- Tail of `DCIO_UNIPHY5` and full `DCIO_UNIPHY6`: reserved UNIPHY macro-control offsets with base index 2.
- `PWRSEQ0` and `PWRSEQ1`: panel/display power sequencing GPIO, delay, light-sleep, control, state/debug, and spare offsets.
- `DSCC0` through `DSCC2`, `DSCCIF0` through `DSCCIF2`, and `DSC_TOP0` through `DSC_TOP2`: DSC encoder configuration, PPS parameters, range-min/max/BPG tables, debug and status registers, DSCC interface config, top-level DSC control, and per-DSC perfmon counters `DC_PERFMON19` through `DC_PERFMON21`.
- HPO top and stream mapper: `HPO_TOP_CLOCK_CONTROL`, `HPO_TOP_HW_CONTROL`, and `DP_STREAM_MAPPER_CONTROL0` through `CONTROL3`.
- HPO HDMI and DP stream encoding: `AFMT5`, `DME5`, and `VPG5` for the HPO HDMI stream encoder; `DP_STREAM_ENC0` through `DP_STREAM_ENC3`, `APG0` through `APG3`, `DME6` through `DME9`, and `VPG6` through `VPG9` for HPO DP stream encoders.
- HPO DP symbol/link physical layers: `DP_SYM32_ENC0` through `DP_SYM32_ENC3`, `DP_LINK_ENC0`/`1`, and `DP_DPHY_SYM320`/`321` offsets for control, training-pattern, SAT/VC-rate, CRC, debug, and spare registers.
- `DCHVM`: host-VM/IOMMU-facing display registers such as `DCHVM_CTRL0`, fault address, and RIOMMU status.
- VGA indirect spaces: sequencer, CRT controller, graphics controller, and attribute-controller `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` indices.
- Azalia audio indirect spaces: root/function parameters, F2 codec converter/pin registers, descriptor and sink-info windows, input/output CRC channel results, 16 F0 stream windows, 8 F0 output endpoint windows, and the beginning of F0 input endpoint windows.

## Control Flow

This header has no runtime control flow. The effective control flow is supplied by DCN316 display and DMUB code that includes this offset header:

1. DCN316-specific C files include both `dcn/dcn_3_1_6_offset.h` and `dcn/dcn_3_1_6_sh_mask.h`.
2. Base helper macros expand `reg..._BASE_IDX` through DCN base-segment constants, then add the corresponding `reg...` offset. In `dmub_dcn316.c`, for example, `REG_OFFSET_EXP(reg_name)` expands to `BASE(reg##reg_name##_BASE_IDX) + reg##reg_name`.
3. Higher-level display code uses generated offset/mask/shift tables to program power sequencing, DSC compression, HPO stream/link encoders, DisplayPort symbol PHY paths, audio packet generation, and DMUB-visible register access.
4. `ix*` indirect indices are consumed through indirect-register access paths, where the numeric index selects a VGA or Azalia codec/stream/endpoint register inside an indexed aperture rather than a direct MMIO offset.

The constants do not encode programming order, lock ownership, polling requirements, sticky status behavior, write-one-to-clear behavior, or indirect-index address/data sequencing. Those rules live in the display driver and ASIC specification.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk or in memory. It describes hardware register locations whose values live in the GPU display/audio hardware.

Hardware state represented by the offsets includes:

- Panel power state and sequencing state for `PWRSEQ0`/`PWRSEQ1`, including GPIO control, delays, light sleep, debug, and spare state.
- DSC encoder state for three DSCC instances: slice/PPS programming, rate-control tables, buffer model values, interrupt/status/debug registers, and DSC top-level control.
- HPO output state: stream mapper routing, HDMI audio/video packet formatting, DP stream encoder clocks and VID timing, APG/VPG packet-generator state, DME memory/control registers, and DP symbol encoder state.
- DP link/PHY state: DPHY enable/reset, lane/mode selection, training pattern control, SAT stream allocation, VC rate control, CRC results, and debug counters.
- DCHVM/IOMMU-facing state such as display VM control, fault addresses, and RIOMMU status.
- Legacy VGA indexed state and Azalia audio codec state, including converter formats, stream/channel IDs, pin-sense/configuration defaults, ELD/audio descriptors, sink info, hot-plug/audio-enable status, LPIB snapshots, CRC channel results, and unsolicited response controls.

Persistence is hardware-defined. Configuration values generally remain until modeset, stream disable, power-gating transition, suspend/resume restore, audio endpoint reset, or ASIC reset changes them. Status, CRC, fault, hot-plug, LPIB, and interrupt fields may be volatile, sticky, latched, self-clearing, or write-one-to-clear depending on the register. This offset header only names where such registers are.

## Dependencies And Integration Points

Primary companion dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h`, which provides field shifts and masks for the register names declared here.

Observed integration sites in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c` includes this offset header and the matching mask header, defines DCN316 base segments, and builds `dmub_srv_dcn316_regs` from `DMUB_DCN31_REGS()` and `DMUB_DCN31_FIELDS()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes the same generated headers while constructing DCN316 display resources and register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c` selects DCN316 DMUB register support through `DMUB_ASIC_DCN316`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c` maps the ASIC to `DMUB_ASIC_DCN316` and references the `amdgpu/dcn_3_1_6_dmcub.bin` firmware name.

Broader integration is with AMDGPU DC resource construction, DMUB service register tables, DSC programming, HPO DP/HDMI output paths, audio endpoint handling, and diagnostic paths that read CRC, perfmon, debug, or fault registers. The `reg*` entries must remain aligned with the DCN316 base segment constants, and the `ix*` entries must remain aligned with their indirect address/data access mechanisms.

## Risks And Edge Cases

- Offset drift is the main risk. These are untyped preprocessor constants, so an incorrect offset or base index can compile cleanly while directing writes to the wrong hardware register.
- This chunk begins in the middle of the `DCIO_UNIPHY5` reserved register list and ends in the middle of `azf0inputendpoint1_inputendpointind`. Final file-level reconciliation must merge neighboring chunks before making complete-instance claims for those two blocks.
- `reg*` and `ix*` macros have different access models. Treating an indirect `ixAZALIA*`, `ixCRT*`, or `ixATTR*` index like a direct MMIO `reg*` offset would target the wrong bus/aperture.
- Repeated instances are copy-generated. A single bad instance number or base index in `DSCC0`-`2`, `DP_STREAM_ENC0`-`3`, `DP_SYM32_ENC0`-`3`, `APG0`-`3`, `VPG5`-`9`, or `AZF0ENDPOINT0`-`7` can appear only on a specific display pipe, link, stream, or audio endpoint.
- DSC offsets cover compression PPS and rate-control state. Misaddressed writes can cause visual corruption, DSC negotiation failures, buffer underflow/overflow interrupts, or blank output only on compressed-link modes.
- HPO DP symbol/DPHY offsets control training patterns, virtual-channel rate, SAT allocation, and CRC/debug state. Errors can break high-bandwidth DisplayPort link training or MST-style stream mapping while leaving simpler paths unaffected.
- Azalia audio offsets include pin-sense, hot-plug, ELD/sink info, LPIB snapshots, stream IDs, and audio format changed status. Bad index values can lead to HDMI/DP audio enumeration failures, stale sink capabilities, missed format-change interrupts, or incorrect audio-channel routing.
- Reserved UNIPHY and spare registers should not be assumed safe for arbitrary use. Their presence in a generated header does not imply stable semantics across ASIC revisions.

## Test Signals

Useful validation signals are mostly integration and hardware-facing rather than unit-test oriented:

- Build coverage for DCN316 display and DMUB code should catch missing macro names, duplicate definitions, or broken token-pasting with `REG_OFFSET_EXP`, `FD_MASK`, and `FD_SHIFT`.
- Register-table sanity checks should verify that DCN316 offsets use the intended base segment and that repeated instances advance consistently across DSC, HPO stream, symbol encoder, DPHY, and audio endpoint blocks.
- Display smoke tests should include panel power sequencing, modesets using DSC, HPO DP/HDMI output, multi-stream or multi-pipe routing, suspend/resume, and hotplug.
- Link diagnostics should exercise DP link training, CRC/debug reads, and HPO stream mapper paths.
- Audio tests should cover HDMI/DP audio enumeration, ELD/sink-info propagation, stream format changes, LPIB snapshots, hot-plug audio enable/disable status, and multi-channel/HBR-capable paths.
- Runtime logs or diagnostics showing DSC underflow/overflow, DPHY training failures, audio format changed interrupts, RIOMMU faults, or unexpected CRC deltas are strong signals to re-check these offsets against the generated source and ASIC tables.

### subset-b-001896: lines 15509-15686

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 15509-15686

## Purpose

This chunk is the closing section of AMD's generated DCN 3.1.6 register offset header. It contains no executable C logic; it publishes preprocessor constants for Azalia function 0 input-endpoint indexed registers. The values are the indirect register offsets selected through each endpoint's `AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` register before reading or writing the matching `AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA` window.

The requested range contains 178 source lines, 151 `#define` entries, six generated `addressBlock` comments for complete input endpoints 2 through 7, and the final `#endif` for the header guard. It starts inside the tail of `azf0inputendpoint1_inputendpointind`, then covers complete indexed-offset maps for `azf0inputendpoint2_inputendpointind` through `azf0inputendpoint7_inputendpointind`.

Although this path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locks, or direct register accesses in this chunk. The exported interface is a generated macro namespace:

- `ixAZF0INPUTENDPOINT<N>_AZALIA_F0_CODEC_INPUT_*`: indirect Azalia codec input-endpoint register offsets for endpoint instances 1 through 7.
- `// addressBlock: azf0inputendpoint<N>_inputendpointind`: generated grouping comments for indexed register blocks. In this chunk, endpoint 1 is only the inherited tail from the previous block; endpoint 2 through endpoint 7 have visible block comments.
- The closing `#endif` terminates `_dcn_3_1_6_OFFSET_HEADER`.

Endpoint 1 coverage starts after the converter and early pin registers and includes the tail pin-control indexed offsets:

- `..._WIDGET_CONTROL` at `0x0024`.
- Multichannel, HBR, channel-allocation, hot-plug, unsolicited-response-force, default-configuration, LPIB snapshot/readback, input-status, and infoframe offsets from `0x0036` through `0x0068`.

Endpoints 2 through 7 repeat the same complete 23-offset input-endpoint map:

- Converter parameter/control offsets: audio widget capabilities `0x0001`, converter format `0x0002`, channel/stream ID `0x0003`, digital converter `0x0004`, stream formats `0x0005`, and supported size/rates `0x0006`.
- Input pin parameter/control offsets: audio widget capabilities `0x0020`, pin capabilities `0x0021`, unsolicited response `0x0022`, input pin sense `0x0023`, and widget control `0x0024`.
- Multichannel and high-bit-rate audio offsets: multichannel enable `0x0036`, multichannel enable2 `0x0037`, and HBR response `0x0038`.
- Audio metadata and event offsets: channel allocation `0x0053`, hot-plug control `0x0054`, unsolicited-response-force `0x0055`, and response default configuration `0x0056`.
- Runtime position/status offsets: LPIB snapshot control `0x0064`, LPIB `0x0065`, LPIB timer snapshot `0x0066`, input status control `0x0067`, and infoframe `0x0068`.

The bit-level meanings for these indexed registers live in the companion `dcn_3_1_6_sh_mask.h` file under the matching `AZF0INPUTENDPOINT<N>_...` register names. This offset chunk only says which indexed register number to select.

## Control Flow

This header has no runtime control flow. The intended runtime sequence is supplied by AMDGPU display/audio code and the generic register helpers:

1. DCN 3.1.6 translation units include `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`.
2. Direct MMIO offset macros elsewhere in this same header identify each input endpoint's index/data pair, for example `regAZF0INPUTENDPOINT2_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` at `0x0442` and `regAZF0INPUTENDPOINT2_AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA` at `0x0443`, both with base index `2`.
3. A consumer selects an `ixAZF0INPUTENDPOINT<N>_...` value by writing the endpoint index window, then reads or writes the endpoint data window.
4. Field masks and shifts from `dcn_3_1_6_sh_mask.h` are applied to pack or extract individual HDA/Azalia fields.

The macros do not encode any sequencing rule. Consumers must still order codec probing, stream-format selection, audio enablement, infoframe handling, hotplug/unsolicited-response processing, LPIB snapshots, and status reads according to hardware requirements.

## State And Persistence Behavior

The macros store no software state and persist nothing in memory or files. They describe MMIO-backed GPU display-audio state reachable through indexed endpoint windows.

The hardware state represented by the indexed offsets includes:

- Input converter capability and format state: channel count, sample width/rate encoding, stream ID, channel ID, stream format support, and supported size/rate reporting.
- Input digital-converter state for audio-valid/status-channel attributes and keepalive behavior.
- Input pin capabilities and controls, including unsolicited response configuration, pin sense, widget enablement, and multichannel lane enable/mute/channel-ID state.
- HBR capability/enablement, channel allocation, hotplug/audio-enable control, forced unsolicited-response payloads, and HDA default pin configuration.
- LPIB position and timer snapshot state, cyclic-buffer wrap count, input activity, channel layout, infoframe-change unsolicited-response enables, and decoded audio infoframe fields.

Persistence and side effects are hardware-defined. Some fields are configuration values that remain until reprogrammed, reset, power-gated, or restored after suspend/resume. Others are live status, latched status, snapshot, self-clearing, or event-generation controls. This offset header does not identify access type, reset value, or write side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.6 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h`, which provides the matching field masks and shifts for the same `AZF0INPUTENDPOINT<N>` logical registers.
- The direct index/data register offsets earlier in this file, including `regAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` through `regAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA`.
- DCN base-address definitions used by DCN 3.1.6 code, such as the `DCN_BASE__INST0_SEG*` constants in `display/dmub/src/dmub_dcn316.c`.
- AMD display register helpers and table-building macros that combine generated offsets with masks/shifts.

Direct include sites for the generated DCN 3.1.6 offset/mask pair in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`

The main display-audio integration point is DCN316 resource construction. `dcn316_resource.c` builds audio register tables with `audio_regs(...)`, creates audio objects through `dce_audio_create(...)`, and constructs stream encoders, VPG, AFMT, and APG blocks used for HDMI/DP audio programming. The visible audio table in `dcn316_resource.c` references output endpoint index/data masks, while this chunk supplies the generated input-endpoint indexed-offset side of the same Azalia function 0 register map for hardware paths or diagnostics that need input endpoint access.

## Risks And Edge Cases

- Generated offset drift is the main risk. These constants are untyped numeric macros, so an incorrect `ix...` value can compile cleanly while selecting the wrong indexed endpoint register at runtime.
- The range starts mid-block. Endpoint 1's converter offsets and early pin offsets are in the previous chunk; only endpoint 2 through endpoint 7 are complete here.
- The range ends at the file-level `#endif`. There is no later chunk for this file after endpoint 7, so merge/reconciliation should treat this as the final offset-header slice.
- Input endpoint instances are repetitive but not interchangeable. Using endpoint 5 offsets through endpoint 4's index/data window, or using an input endpoint offset with an output endpoint window, can silently program or read the wrong HDA node.
- Offset and mask headers must match. Combining `dcn_3_1_6_offset.h` with a different ASIC's `*_sh_mask.h` can produce correct-looking names with wrong hardware semantics.
- Indexed access is sequencing-sensitive. A stale index selection, concurrent access to the same index/data window, or a missing readback/snapshot step can return data for the wrong logical register.
- Audio status and event fields can be live or latched. Misprogramming unsolicited response, hotplug, input activity, HBR, or infoframe offsets can cause missed audio events, spurious notifications, incorrect channel layout reporting, or broken HDMI/DP audio detection.
- LPIB and timer snapshot offsets describe position-related state. Reading them without the expected snapshot/lock protocol can produce inconsistent position data.

## Test Signals

Useful validation signals are mostly build-time, generated-header consistency, and hardware audio behavior:

- Build AMDGPU display code with DCN 3.1.6 enabled to catch missing or renamed generated macros in include paths used by `dcn316_resource.c` and `dmub_dcn316.c`.
- Mechanically verify that every `ixAZF0INPUTENDPOINT<N>_...` offset in this range has a matching logical register family in `dcn_3_1_6_sh_mask.h`.
- Check parity across endpoint 2 through endpoint 7: each complete endpoint should expose the same 23 indexed offsets with identical numeric values.
- Verify that the direct index/data windows earlier in `dcn_3_1_6_offset.h` exist for every input endpoint 0 through 7 and use the expected base index.
- Diff this slice against AMD's authoritative DCN 3.1.6 register database or nearby compatible DCN headers where endpoint layouts are expected to match.
- Exercise HDMI/DP audio paths on DCN316 hardware: stream setup, sample-rate/bit-depth changes, multichannel layouts, HBR audio, hotplug, unplug/replug, suspend/resume, and rapid modesets.
- Monitor kernel logs and audio behavior for missed hotplug/unsolicited-response events, wrong channel allocation, invalid infoframe reporting, LPIB position anomalies, audio silence, or spurious audio-enable/disable transitions.

## Cross-Chunk Notes

The previous chunk must be merged to complete `AZF0INPUTENDPOINT1` because this range starts at `ixAZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`. This chunk completes the file by covering all visible indexed offsets for input endpoints 2 through 7 and the closing header guard.
