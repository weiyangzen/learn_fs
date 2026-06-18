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
