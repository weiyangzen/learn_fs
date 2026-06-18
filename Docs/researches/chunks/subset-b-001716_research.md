# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h lines 1-2694

## Purpose

This chunk is generated AMDGPU DCN 3.0.1 display-controller register address metadata. It contains no executable C logic; its public surface is a large set of preprocessor constants that map symbolic `mm...` register names to register offsets plus paired `mm..._BASE_IDX` constants that select the IP base segment used to form an MMIO address.

The file sits under a local `ceph-client` source mirror, but the content is AMD display-driver hardware metadata, not Ceph filesystem code. The chunk covers the start of the DCN 3.0.1 offset namespace: VGA legacy/display decode registers, HDA/Azalia audio, DCCG clock generation, DMU/DMCU/DMCUB firmware control, MMHUBBUB and DCHUBBUB memory/display hub registers, writeback memory client registers, display interrupt/timer registers, HUBP0/HUBP1 surface fetch blocks, and the beginning of HUBP2.

Every meaningful entry follows the same ABI pattern:

- `mmREGISTER` is the register offset within the selected base segment.
- `mmREGISTER_BASE_IDX` is the base segment selector used by register helper macros.

Consumers combine both pieces through macros such as `REG_OFFSET(reg)` rather than manually adding offsets.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime storage objects in this chunk. The important API is the generated macro namespace consumed by DCN301 register table initializers and low-level register helpers.

The chunk contains 1,188 register-offset macros and 1,187 `_BASE_IDX` macros in lines 1-2694. The minor count mismatch comes from the line range ending in the middle of the `HUBP2` block before the next paired base-index macro appears. The file-level include guard is `_dcn_3_0_1_OFFSET_HEADER`.

Major macro families in this range:

- Legacy VGA and VGA-indexed access: `mmVGA_MEM_WRITE_PAGE_ADDR`, `mmVGA_MEM_READ_PAGE_ADDR`, `mmCRTC8_*`, `mmSEQ8_*`, `mmGRPH8_*`, `mmATTR*`, `mmDAC_*`, `mmGEN*`, `mmVGA_RENDER_CONTROL`, `mmVGA_MODE_CONTROL`, per-pipe `mmD1VGA_CONTROL` through `mmD6VGA_CONTROL`, and VGA status/interrupt/source-select registers.
- HDA/Azalia controller and endpoint registers: CORB/RIRB pointers and controls, immediate command/response interfaces, DMA position addresses, wall-clock alias, stream and endpoint index/data pairs, Azalia controller clock/audio DTO/DMA/CRC/memory-power registers, root codec function parameters, stream instances `AZF0STREAM0-15`, endpoint instances `AZF0ENDPOINT0-7`, and input endpoints `AZF0INPUTENDPOINT0-7`.
- DCCG clock-generation and timing registers: PHY pixel clock resync controls, DP DTO controls and modulo/phase registers, display/reference clock controls, global time-counter DTO/current registers, DSC/DPP clock DTO parameters, audio DTOs, vblank latch/counter registers, DCCG soft reset, force symbol-clock disable, and DCCG perfmon blocks.
- DMU, DMCU, DCPG, IHC, RBBMIF, and DMCUB registers: display power-domain config/status registers, DMU memory/clock controls, DMCU firmware address/checksum/RAM-access/mailbox/interrupt/perfmon/DPRX metadata, display GPU timer and interrupt-status chains, foreground-security and RBBM interface status/timeout controls, and DMCUB region, code window, interrupt, inbox/outbox, timer, scratch, GPINT, fault, security, and memory-power registers.
- MCIF writeback and MMHUBBUB registers: writeback buffer manager controls/status, Y/C buffer addresses and high addresses, pitch, buffer sizes, resolutions, VMID, watermark/minimum time-to-output controls, writeback clock/self-refresh/QoS controls, MMHUBBUB warmup config and addresses, memory power, soft reset, clock, client unit ID, and VGAIF MCIF counters.
- DCHUBBUB global registers: SDPIF config, DCN VM framebuffer/AGP/local-memory aperture registers, DCC return-path config for slices 0-7, CRC controls/results, arbitration outstanding/saturation/QoS/DRAM-state controls, watermark sets A-D, fractional bandwidth/watermark families, VM context 0-15 page-table controls and bounds, default/fault addresses, and fault status/control.
- HUBP/HUBPREQ/HUBPRET/cursor registers for instances 0 and 1, plus the first part of HUBP2: surface configuration, tiling, viewport dimensions, request sizing, clock and VM page config, primary/secondary/meta surface addresses, flip and surface-in-use registers, TTU/QoS timing controls, blank/viewport/prefetch/vblank/flip/nominal delivery parameters, memory-power controls, read-line controls, cursor address/position/size/hotspot/stereo/DMDATA registers, and per-HUBP perfmon blocks.

The register grouping is encoded by generated comments of the form `// addressBlock: ...` and `// base address: ...`. Within this chunk, the base-index values are mostly `0`, `1`, or `2`; they are not arbitrary software categories but selectors for ASIC IP base arrays.

## Control Flow

This header chunk has no control flow. It is declarative hardware address data.

Runtime use follows this pattern:

1. DCN301-specific code includes `dcn/dcn_3_0_1_offset.h` with the matching `dcn/dcn_3_0_1_sh_mask.h` field header and an ASIC IP offset header such as `vangogh_ip_offset.h`.
2. Register table macros expand symbolic register names through `REG_OFFSET(reg)`, which resolves to `BASE(mm##reg##_BASE_IDX) + mm##reg`.
3. Component constructors receive populated register tables and matching shift/mask tables.
4. Runtime display code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` against those tables to program clocks, memory hub state, scanout surfaces, cursor state, audio DTOs, DMUB mailboxes, interrupts, and power-management controls.
5. Firmware-facing DMUB code uses DMCUB offsets for inbox/outbox, scratch, region, interrupt, and GPINT registers; display resource and block code uses the same offset namespace through DCN301-specific register-list macros.

The macros do not encode ordering requirements. Correct sequencing is provided by higher-level display, DMUB, power, and audio code.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes addresses of MMIO-backed GPU display hardware state.

The represented hardware state includes:

- VGA legacy decode and page-memory controls.
- Display clock and DTO programming state in DCCG, including display, DPP, DSC, DP reference, PHY symbol, audio, and timebase controls.
- DMU/DMCU/DMCUB firmware state: firmware load windows, RAM access, mailbox data, scratch registers, interrupts, timers, security/memory controls, GPINT state, and fault reporting.
- Display interrupt aggregation state and GPU timer start/read controls.
- HDA/Azalia command rings, stream/index/data accessors, audio DTO/control, endpoint codec state, CRC controls/results, memory power, and DMA-related state.
- MCIF writeback buffer addresses, buffer manager status, VMID, pitch, size, resolution, self-refresh, QoS, and watermark state.
- MMHUBBUB/DCHUBBUB VM address aperture, arbitration, watermarks, return-path DCC, CRC, page-table, and fault state.
- HUBP scanout state for pipe instances: surface layout, tiling, viewport, addresses, flips, in-use/earliest-in-use tracking, TTU/QoS timing, prefetch/vblank/nominal parameters, cursor state, read-line status, memory power, and perfmon counters.

Persistence is hardware-defined. Some configuration registers remain programmed until reset, power-gating loss, or explicit reprogramming. Status, interrupt, timer, counter, fault, and mailbox pointer registers may be read-only, sticky, write-one-to-clear, side-effect-sensitive, or self-clearing depending on the corresponding register specification and field masks in `dcn_3_0_1_sh_mask.h`.

## Dependencies And Integration Points

Primary dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h` supplies the matching field shift/mask metadata for these offsets.

Important direct include point:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c` includes this offset header, the matching sh/mask header, and `vangogh_ip_offset.h`. It builds `dmub_srv_dcn301_regs` by expanding `DMUB_COMMON_REGS()` and `DMCUB_INTERNAL_REGS()` through `REG_OFFSET(reg)`.

Important helper contract:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h` defines `REG_OFFSET(reg_name)` as a combination of `BASE(mm..._BASE_IDX)` and `mm...`. This is the central reason every register offset macro must have the correct paired base-index macro.

DCN301 display integration appears through component register-list headers and resource construction code, including:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn301/dcn301_dccg.h`, whose `DCCG_REG_LIST_DCN301()` references DCCG offsets from this chunk, such as `DPPCLK_DTO_CTRL`, `DPPCLK*_DTO_PARAM`, `REFCLK_CNTL`, `DISPCLK_FREQ_CHANGE_CNTL`, and timebase/gate controls.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn301/dcn301_hubbub.h`, which extends DCN30 hubbub register lists and depends on the same generated offset/field namespace for memory-hub programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`, which creates the DCN301 resource pool and wires blocks such as hubbub, hubps, DIO, OPP, timing generators, DSC, writeback, MMHUBBUB, AUX, and I2C. Those block constructors ultimately consume generated register lists built from headers like this one.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c` selects `dmub_srv_dcn301_regs` for `DMUB_ASIC_DCN301`, tying the generated DMCUB offsets in this chunk to firmware communication and diagnostics.

The line range itself ends inside the `dce_dc_dcbubp2_dispdec_hubp_dispdec` block. Later chunks are required for the rest of HUBP2 and subsequent display blocks.

## Risks And Edge Cases

- These macros are hardware ABI metadata. A wrong offset or `_BASE_IDX` compiles cleanly but can read or write the wrong register, causing display blanking, bad clocks, bad memory arbitration, missed interrupts, corrupt firmware communication, cursor corruption, audio failure, GPU page faults, or unstable power management.
- Offset and base-index macros are a pair. Changing one without the other can redirect a register to the wrong IP segment even if the numeric offset looks plausible.
- Many repeated instance families differ only by instance number and base offset, such as `AZF0STREAM0-15`, `AZF0ENDPOINT0-7`, `HUBP0/1/2`, `HUBPREQ0/1`, `CURSOR0_1`, VM contexts 0-15, and DCHUBBUB watermark sets A-D. Off-by-one instance drift is a major generated-header risk.
- The chunk ends mid-block at `mmHUBP2_DCSURF_SEC_VIEWPORT_DIMENSION_C`; whole-file or whole-HUBP2 conclusions require later chunks.
- Some register names are indexed access portals (`*_INDEX`/`*_DATA`) rather than direct state registers. Incorrect sequencing around index/data pairs can target the wrong indirect register.
- Mailbox and ring registers such as DMCUB inbox/outbox base, size, read pointer, and write pointer are shared with firmware. Incorrect offsets can desynchronize host and DMUB and make recovery difficult.
- Interrupt-status chains and timer registers are side-effect-sensitive in many display IPs. Treating status/ack registers as ordinary storage can clear pending events or hide faults.
- Address macros alone do not identify field width, access type, reset value, or write-one-to-clear semantics. Consumers must use the matching `dcn_3_0_1_sh_mask.h` data and hardware programming sequences.
- The path is within a broader source mirror; updating this file manually instead of regenerating it from the ASIC register database risks divergence from other DCN301 generated files.

## Test Signals

Useful validation is compile-time plus hardware/simulator behavior:

- Build AMDGPU display and DMUB code with DCN301 enabled; missing, renamed, or malformed macros should fail in register-table expansion through `REG_OFFSET`, `FD_MASK`, or `FD_SHIFT`.
- Diff this chunk against AMD's authoritative DCN 3.0.1 register database and adjacent generated headers to catch offset/base-index drift in DCCG, DMCUB, HUBBUB, HDA, MCIF writeback, and HUBP families.
- Boot DCN301/Vangogh-class hardware and verify DMUB initialization: region setup, inbox/outbox pointers, scratch reads, GPINT handling, firmware boot/status, and debug register collection.
- Exercise display mode set and clock transitions to cover DCCG display/DPP/reference clock DTO programming and timebase registers.
- Run multi-plane scanout, page flips, cursor movement, viewport changes, VMID changes, and memory power transitions on HUBP0 and HUBP1; later chunks should cover the full HUBP2 path.
- Exercise memory-hub watermark and arbitration programming under pstate changes, self-refresh, VM page-table changes, and fault injection where available.
- Validate HDA/DisplayPort audio playback and hotplug/stream changes so Azalia stream, endpoint, DTO, DMA, and CRC paths are touched.
- Exercise writeback/capture paths that use MCIF writeback buffers, Y/C addresses, pitch, size, and watermark controls.
- Monitor kernel logs for DMUB timeout, DMCUB fault, display underflow, VM fault, IRQ storm, audio underrun, hotplug/AUX failure, cursor corruption, and page-flip timeout signals after any generated-register update.

## Cross-Chunk Notes

This is the first chunk of `dcn_3_0_1_offset.h`. It establishes the include guard and begins the generated register-offset namespace, but it covers only lines 1-2694 of a 13,271-line header. Later chunks continue HUBP2 and cover additional display pipe, timing, DPP, MPC, OPP, DIO, AUX/I2C, panel/backlight, and indirect-register sections. The final per-file research document should merge all chunks before making complete claims about DCN 3.0.1 offset coverage.
