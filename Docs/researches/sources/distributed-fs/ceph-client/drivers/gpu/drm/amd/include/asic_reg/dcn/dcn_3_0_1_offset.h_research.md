# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001716`: lines 1-2694, `Docs/researches/chunks/subset-b-001716_research.md`
- `subset-b-001717`: lines 2695-5217, `Docs/researches/chunks/subset-b-001717_research.md`
- `subset-b-001718`: lines 5218-7845, `Docs/researches/chunks/subset-b-001718_research.md`
- `subset-b-001719`: lines 7846-10422, `Docs/researches/chunks/subset-b-001719_research.md`
- `subset-b-001720`: lines 10423-13004, `Docs/researches/chunks/subset-b-001720_research.md`
- `subset-b-001721`: lines 13005-13271, `Docs/researches/chunks/subset-b-001721_research.md`

## Chunk Research

### subset-b-001716: lines 1-2694

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

### subset-b-001717: lines 2695-5217

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h lines 2695-5217

## Purpose

This chunk is generated AMD DCN 3.0.1 register-offset metadata. It contains no executable C functions, structs, enums, variables, locking, allocation, or persistence logic. Its exported interface is a dense set of preprocessor constants that map symbolic DCN display-controller register names to numeric MMIO offsets and matching base-address segment selectors.

The requested range is a middle slice of `dcn_3_0_1_offset.h`. It starts at the tail of the HUBP2 block with `mmHUBP2_DCSURF_SEC_VIEWPORT_DIMENSION_C_BASE_IDX`, then covers:

- The remainder of HUBP2 top-level plane-fetch controls.
- Complete HUBPREQ2, HUBPRET2, CURSOR0_2, and HUBP2 performance-monitor blocks.
- Complete HUBP3, HUBPREQ3, HUBPRET3, CURSOR0_3, and HUBP3 performance-monitor blocks.
- DPP instance 0 top/CNVC/CNVC cursor/DSCL/CM/perfmon blocks.
- DPP instance 1 top/CNVC/CNVC cursor/DSCL/CM/perfmon blocks.
- DPP instance 2 top/CNVC/CNVC cursor/DSCL and the beginning of CM2, ending at `mmCM2_CM_SHAPER_RAMA_REGION_10_11_BASE_IDX`.

The chunk has 2,419 `#define` lines: 1,209 complete register-offset macros and 1,210 `_BASE_IDX` macros. The one extra base-index macro is the opening line for a register whose matching offset appears in the previous chunk. All visible `_BASE_IDX` values are `2`, so consumers address these registers through DCN base segment 2 plus the generated offset.

Although this repository path is under `sources/distributed-fs/ceph-client`, the file is AMDGPU display-driver hardware metadata. It does not implement Ceph, filesystem, network, or storage behavior.

## Important APIs, Types, And Macros

The API surface is the generated macro namespace:

- `mm<block><instance>_<register>`: a DCN 3.0.1 MMIO register offset.
- `mm<block><instance>_<register>_BASE_IDX`: the base segment selector paired with that offset.
- Register-list expansion macros in consumers paste register names into those symbols and compute absolute addresses as `BASE(mm..._BASE_IDX) + mm...`.

There are no locally declared C types or functions. The important contract is exact spelling, instance numbering, numeric offset value, and `_BASE_IDX` pairing.

Major macro families in this range:

- `HUBP2_*` and `HUBP3_*`: surface configuration, address and tiling configuration, primary and secondary viewport start/dimension registers for luma and chroma planes, request-size configuration, HUBP control, clock control, virtual-memory page-gating configuration, debug registers, and DCFCLK/DPPCLK measurement windows.
- `HUBPREQ2_*` and `HUBPREQ3_*`: surface pitch, VMID settings, primary and secondary surface addresses and high halves, chroma-plane address variants, primary and secondary metadata surface addresses, surface control, flip control, flip interrupt, in-use and earliest-in-use tracking, expansion mode, TTU/QoS controls for surface and cursor fetches, VM DMDATA control, system aperture low/high addresses, L1 TLB control, blank/destination/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor settings, reference-to-pixel-frequency ratio, DRQ limit, and memory-power control/status.
- `HUBPRET2_*` and `HUBPRET3_*`: return-path control, memory-power control/status, read-line controls, read-line values/status, and return-path interrupt registers.
- `CURSOR0_2_*` and `CURSOR0_3_*`: cursor control, surface address/high address, size, position, hot spot, stereo control, destination offset, memory-power control/status, and DMDATA address/control/QoS/status/software data registers.
- `DC_PERFMON8_*`, `DC_PERFMON9_*`, `DC_PERFMON10_*`, and `DC_PERFMON11_*`: per-block performance counter control, secondary control, state, global perfmon control, current-value misc/low, high, and low counter registers for HUBP2, HUBP3, DPP0, and DPP1.
- `DPP_TOP0_*`, `DPP_TOP1_*`, and `DPP_TOP2_*`: DPP control, soft reset, CRC readback/control, and host-read control registers.
- `CNVC_CFG0_*`, `CNVC_CFG1_*`, and `CNVC_CFG2_*`: surface pixel format, format conversion, FP bias/scale, color-keyer controls and color bounds, alpha LUT, pre-dealpha, pre-CSC mode/matrix coefficients including B variants, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0_*`, `CNVC_CUR1_*`, and `CNVC_CUR2_*`: formatter-side cursor control, cursor colors, and FP scale/bias.
- `DSCL0_*`, `DSCL1_*`, and `DSCL2_*`: scaler coefficient RAM access, scaler mode, tap control, DSCL control, 2-tap control, manual replicate control, horizontal and vertical scale ratios/initial phases for luma and chroma, black color, update/autocal, overscan, OTG blanking, recout start/size, MPC size, line-buffer format and memory control, vertical counter, DSCL memory-power control/status, output-buffer control, and OBUF memory-power control.
- `CM0_*` and `CM1_*`: complete DPP color-management blocks, including CM control, post-CSC, gamut remap, bias, gamcor controls and LUTs, gamcor RAMA/RAMB PWL region programming, blend-gamma controls and LUTs, HDR multiplier, memory-power controls, dealpha, coefficient format, shaper controls/LUTs/RAMA/RAMB regions, 3D LUT mode/index/data/read-write controls, output normalization and offsets, and debug index/data registers.
- `CM2_*`: the same color-management pattern as CM0/CM1 through the start of the shaper RAMA region list. This chunk stops before the rest of CM2's shaper RAMA/RAMB, memory-power2, 3D LUT, and debug offsets.

## Control Flow

This header has no local runtime control flow. It participates in driver control flow through inclusion and macro expansion:

1. DCN301 display resource code includes `dcn_3_0_1_offset.h`, `dcn_3_0_1_sh_mask.h`, and the ASIC IP base-offset header.
2. `dcn301_resource.c` defines expansion helpers such as `SR`, `SRI`, `SRII`, and related variants. These paste block and instance tokens into symbols such as `mmHUBPREQ2_DCSURF_SURFACE_PITCH_BASE_IDX` and `mmHUBPREQ2_DCSURF_SURFACE_PITCH`.
3. Resource tables are built for four DPP instances and four HUBP instances. The visible chunk supplies all of the register offsets needed for HUBP/HUBPREQ/HUBPRET/CURSOR instances 2 and 3, and most of the DPP/CNVC/DSCL/CM register coverage for DPP instances 0 through 2.
4. Functional modules later use populated register tables with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, `REG_WAIT`, and related helpers. The sequencing for plane flips, cursor updates, scaler programming, color LUT programming, memory-power transitions, and performance-counter reads lives in those modules, not in this generated header.
5. DMUB DCN301 service code includes the same offset and mask headers, although this particular range is mostly display-pipe register metadata rather than the DMCUB register family used by `dmub_dcn301.c`.

The macros do not encode ordering. Consumers must still enable clocks, ungate memories, program double-buffered state in the correct phase, handle read-only/status/ack fields correctly, and synchronize register writes with modeset or flip timing.

## State And Persistence Behavior

The chunk stores no software state. It describes MMIO-backed hardware state whose persistence is defined by the display engine. Register contents generally persist until a modeset reprograms the pipe, a block is reset or power-gated, a suspend/resume path restores state, or a full GPU reset clears the engine.

Hardware state addressed by this range includes:

- Plane-fetch state for HUBP2 and HUBP3: surface format, address configuration, tiling, luma/chroma viewports, surface pitch, primary/secondary addresses, metadata addresses, VMID, VM aperture/TLB control, DMDATA addressing, flip control, flip interrupt status, current/in-use surface tracking, and prefetch/nominal/vblank/flip timing parameters.
- Request and return-path state: HUBPREQ TTU/QoS delivery controls, per-line delivery, DRQ limits, cursor timing parameters, memory-power controls/status, HUBPRET read-line tracking, and return-path interrupt/status state.
- Cursor state for pipe instances 2 and 3: cursor enable/mode, surface address, dimensions, position, hot spot, stereo mode, memory-power state, dynamic metadata address/control/QoS/status, and software DMDATA register access.
- DPP formatter state: pixel format, alpha-plane enable, format expansion, fixed-point bias/scale conversion, color-key ranges, alpha 2-bit LUT, pre-dealpha/re-alpha, pre-CSC matrices, and formatter cursor colors/scale/bias.
- DSCL scaler state: filter taps and coefficient RAM, scaler mode, horizontal/vertical ratios and initial phases for luma/chroma, line-buffer format and memory power, recout/MPC sizing, overscan, autocalculated parameters, blanking, and output-buffer power.
- CM color-management state: post-CSC, gamut-remap matrices, gamma-correction and blend-gamma LUTs, PWL region tables, shaper LUTs, HDR multiplier, dealpha, coefficient formats, 3D LUT state for CM0/CM1, memory-power controls/status, and test/debug index/data.
- Perfmon state: control bits, counter state, current-value registers, and high/low counter storage for the visible HUBP and DPP perfmon blocks.

Because the constants are address metadata, a wrong offset or base index can redirect writes into another register block. That can leave persistent hardware state corrupted until the affected pipe, DPP, HUBP, or full display engine is reinitialized.

## Dependencies And Integration Points

This chunk is tightly coupled to generated and hand-written display code:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h` supplies field shifts and masks for the register offsets in this file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vangogh_ip_offset.h` supplies DCN base segment macros used by DCN301 code.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c` includes this header and builds resource register tables. Its `BASE`, `SR`, `SRI`, and array-initializer macros are the direct consumers of the `mm...` and `_BASE_IDX` naming contract.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h` defines `DPP_REG_LIST_DCN30_COMMON()` and `DPP_REG_LIST_DCN30()`, which consume the `DPP_TOP`, `CNVC_CFG`, `CNVC_CUR`, `DSCL`, and `CM` families visible here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.c`, `dcn10_dpp_dscl.c`, and `dcn10_dpp_cm.c` use the populated register tables to program formatter, scaler, gamma, gamut, shaper, and LUT behavior.
- HUBP register-list macros used by DCN301 resource construction consume the `HUBP2`, `HUBP3`, `HUBPREQ2`, `HUBPREQ3`, `HUBPRET2`, `HUBPRET3`, `CURSOR0_2`, and `CURSOR0_3` symbols from this range.
- IRQ services across DCN generations map HUBP flip source IDs, including HUBP2 and HUBP3, onto DAL IRQ sources; this chunk supplies the corresponding per-pipe flip-interrupt offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c` includes the DCN301 offset and mask headers for DMUB register tables; adjacent chunks provide more of the DMUB-specific offsets.

The repeated instance layout is an important integration point. `dcn301_resource.c` constructs arrays for four DPPs and four HUBPs; instance 2 and 3 symbols must follow the same spelling and layout as earlier instances or table construction either fails at compile time or silently targets the wrong hardware block.

## Risks And Edge Cases

- Offset drift is the central risk. The constants are untyped compile-time numbers; a wrong value can compile cleanly while driving the wrong MMIO register.
- `_BASE_IDX` drift is equally dangerous. Every visible register belongs to base segment 2 in this chunk. A correct offset paired with an incorrect base selector computes the wrong absolute address.
- Chunk boundaries are artificial. The first line is only a `_BASE_IDX` from the previous HUBP2 register, and the final line stops inside CM2 shaper RAMA programming. A final per-file report must merge adjacent chunks before making whole-file claims.
- Instance-copy mistakes are easy to miss. HUBP2/HUBPREQ2/HUBPRET2/CURSOR0_2 and HUBP3/HUBPREQ3/HUBPRET3/CURSOR0_3 are nearly identical families. A single typo may only fail on the third or fourth pipe, multi-display modes, or specific plane assignments.
- Plane-address and VM registers are high impact. Bad HUBPREQ surface, metadata, aperture, or TLB offsets can cause blank scanout, stale flips, DCC/metadata corruption, VM faults, or unintended memory accesses.
- Flip and interrupt offsets are timing-sensitive. Incorrect flip control or surface-flip-interrupt addresses can produce missed page-flip completion, stuck interrupts, incorrect vblank synchronization, or hangs in atomic commit paths.
- Scaler and formatter errors may be format-specific. DSCL and CNVC offset mistakes can appear only for scaling, YUV/chroma formats, cursor blending, alpha planes, color-keying, or high-bit-depth paths.
- Color-management registers are stateful and table-heavy. Gamcor, blend gamma, shaper, and 3D LUT programming uses index/data and region registers; an address mismatch can corrupt color output without obvious kernel errors.
- Memory-power controls can fail by sequencing. HUBPREQ/HUBPRET/CURSOR/DSCL/CM memory-power control and status registers must be read or written only when the block is clocked and expected to respond.
- Performance counter registers may be read-only, sticky, or clear-on-write depending on fields. This header cannot express those side effects; functional perfmon code must use the companion mask semantics and hardware programming guide assumptions.

## Test Signals

Useful validation for this chunk combines generated-header consistency checks with real display behavior:

- Build AMDGPU display code with DCN301 support enabled. Missing, misspelled, or renamed macros should surface in `dcn301_resource.c`, DPP/HUBP register-list expansion, DMUB register-table construction, and related display modules.
- Mechanically verify that every complete non-`_BASE_IDX` macro in lines 2695-5217 has a matching `_BASE_IDX` macro, accounting for the first line being a carry-over base-index macro from the previous chunk.
- Verify that every visible `_BASE_IDX` value remains `2`.
- Diff the range against AMD's generated DCN 3.0.1 register database and nearby compatible headers such as `dcn_3_0_0_offset.h`, `dcn_3_0_2_offset.h`, and `dcn_3_0_3_offset.h` to catch unintended offset or instance-layout drift.
- Exercise modesets that allocate HUBP/DPP instances 2 and 3: multi-monitor, multi-plane, cursor, scaling, YUV/chroma, DCC/metadata, page-flip, and suspend/resume scenarios.
- Validate flip completion and interrupt handling for HUBP2 and HUBP3, including atomic commits, cursor-only updates, vblank synchronization, and recovery from disabled/re-enabled pipes.
- Run scaler validation for DPP0, DPP1, and DPP2: luma/chroma scaling, 2-tap and multi-tap filters, coefficient RAM programming, overscan, recout/MPC sizing, and bypass paths.
- Run color-management validation for CM0 and CM1, and partial CM2 coverage visible here: post-CSC, gamut remap, gamma correction, blend gamma, shaper LUTs, HDR multiplier, 3D LUT, dealpha, and power-gated memory restore.
- Watch kernel logs and display diagnostics for VM faults, underflow, stale flips, blank outputs, incorrect cursor rendering, scaling artifacts, color banding, broken HDR/color transforms, stuck interrupts, and resume failures.
- Perfmon validation should confirm HUBP2/HUBP3/DPP0/DPP1 counter control and readback operate on the intended block and do not alias adjacent perfmon instances.

## Cross-Chunk Notes

Adjacent chunks are required for a complete `dcn_3_0_1_offset.h` file report. The previous chunk owns the start of HUBP2 and the register paired with this chunk's opening `_BASE_IDX`; the next chunk must finish CM2 after `CM_SHAPER_RAMA_REGION_10_11` and cover the remaining DCN301 register-offset namespace. This chunk should be merged later as one source-aligned contribution, not treated as a standalone final per-file report.

### subset-b-001718: lines 5218-7845

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h lines 5218-7845

## Purpose

This chunk is generated AMD DCN 3.0.1 register-offset metadata. It contains no executable C logic; it exports preprocessor constants that map symbolic display-controller register names to numeric MMIO offsets plus companion base-index selectors. DCN 3.0.1 driver code combines each `mm...` offset with the matching `mm..._BASE_IDX` through `BASE(...)`, `SR(...)`, `SRI(...)`, or DMUB `REG_OFFSET(...)` helpers to build concrete register tables.

The requested range starts inside the DPP2 color-management block at `CM2` shaper/3D LUT registers, covers a complete DPP3 processing pipe, covers OPP/FMT/DPG/OPPBUF/OPP pipe and CRC instances 0 through 3, covers OPTC/ODM and OTG timing generators 0 through 3, then enters DIO with I2C/DDC, HPD, AUX channel 0 through 3, VPG0, AFMT0, DME0, and the beginning of DIG0 HDMI output registers. The range contains 2,400 `#define` lines: 1,200 register-offset macros and 1,200 matching `_BASE_IDX` macros. All `_BASE_IDX` values in this range are `2`.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocations, locks, or error paths in this chunk. Its API is the generated macro namespace:

- `mm<block>_<register>`: a DCN 3.0.1 MMIO register offset.
- `mm<block>_<register>_BASE_IDX`: the base-address segment selector for the same register.

Every visible non-`_BASE_IDX` macro in lines 5218-7845 has exactly one matching `_BASE_IDX` macro. The numeric offset alone is not sufficient; the base index is part of the address contract with `DCN_BASE__INST0_SEG2` and related generated SOC base definitions.

Major macro families in this chunk:

- `CM2` tail: shaper RAM A/B region controls, color-management memory power, 3D LUT index/data/read-write/output normalization, and CM test-debug access for DPP instance 2.
- `DC_PERFMON12`: DPP2 perfmon counter control, state, current value, and high/low counter registers.
- `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, and `CM3`: DPP3 top reset/CRC/read controls, pixel-format conversion, keying, pre-CSC/pre-degamma, cursor controls, scaler coefficient RAM and filter controls, line-buffer and output-buffer memory power, post-CSC, gamut remap, gamma-correction RAM A/B, blend gamma RAM A/B, HDR multiplier, shaper LUT/RAM, 3D LUT, and debug access.
- `DC_PERFMON13`: DPP3 perfmon counter controls and values.
- `FMT0` through `FMT3`: output formatter clamp, dynamic expansion, bit depth, dither seeds, side-by-side stereo, 4:2:0 map-memory control, and 4:2:2 control.
- `DPG0` through `DPG3`: display pattern generator control, ramp, dimensions, RGB/YUV color values, offset segment, and status.
- `OPPBUF0` through `OPPBUF3`, `OPP_PIPE0` through `OPP_PIPE3`, and `OPP_PIPE_CRC0` through `OPP_PIPE_CRC3`: OPP buffer controls, 3D parameters, pipe control, pipe CRC mask and result registers.
- `OPP_TOP`, `DSCRM0` through `DSCRM2`, and `DC_PERFMON14`: OPP clock/ABM controls, DSC forward-routing controls, and OPP perfmon counters.
- `ODM0` through `ODM3`: OPTC input global control, data-source select, data-format and bytes-per-pixel controls, width, input clock, memory config, and spare registers.
- `OTG0` through `OTG3`: timing-generator horizontal/vertical totals, blanking, sync, trigger, flow, stereo, status/readback, counters, snapshots, interrupts, update lock, double buffering, master enable, blank colors, CRC windows/data, static-screen/3D/GSL/global-sync controls, dynamic refresh-rate controls, DTO constants, request control, DSC start position, and pipe update status.
- `OPTC` misc: DWB/GSL source selection, OPTC clock control, ODM memory power control/status, spare register, and `DC_PERFMON15`.
- `DC_I2C`, `DIO`, `HPD0` through `HPD3`, and `DC_PERFMON16`: DIO I2C/DDC control, arbitration, interrupt/status, DDC speed/setup, transactions/data, EDID-detect/read-request interrupt, DIO scratch and power/clock/interrupt registers, hot-plug-detect status/control/filtering, and DIO perfmon counters.
- `DP_AUX0` through `DP_AUX3`: AUX control, software control/status/data, low-speed status/data, arbitration, interrupt, DPHY TX/RX control and status, GTC sync controls/status, error controls, controller status, and PHY wake control.
- `VPG0`, `AFMT0`, `DME0`, and partial `DIG0`: generic-packet and ISRC/MPEG packet registers, audio formatter packet/info/status/CRC/ramp/source/memory-power registers, DME control/memory control, and the first DIG0 front-end, CRC, pattern, FIFO, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet registers.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by DCN resource, link, timing, color, AUX/I2C, HPD, audio, and DMUB code:

1. DCN 3.0.1 code includes `dcn_3_0_1_offset.h` with `dcn_3_0_1_sh_mask.h` and the SOC base-offset header.
2. Resource-table macros paste register names and instance numbers into symbols such as `mmCM3_CM_3DLUT_DATA`, `mmOTG2_OTG_UPDATE_LOCK`, `mmDP_AUX1_AUX_SW_DATA`, or `mmAFMT0_AFMT_AUDIO_PACKET_CONTROL`.
3. `BASE(mm..._BASE_IDX) + mm...` is evaluated into register-table fields.
4. Hardware-specific code later uses those tables with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, wait/poll helpers, and DMUB service code to program display pipes.

The macros do not encode ordering requirements. Consumers still need to sequence DPP color programming, scaler coefficient updates, OPP/OTG double-buffered updates, pipe locking, timing-generator enable/disable, vblank/vertical-interrupt handling, dynamic refresh-rate changes, AUX/I2C arbitration, HPD interrupt clears, audio/infoframe packet updates, and suspend/resume restoration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in files. It names MMIO-backed GPU state. The represented hardware state includes:

- Color-management and scaler state in DPP2/DPP3: gamma/blend/shaper RAM contents, 3D LUT data, CSC/gamut matrices, cursor state, scaler taps/ratios/init values, line-buffer and output-buffer power state, and debug-indexed access.
- Output-pipe state in OPP/FMT/DPG/OPPBUF: formatter pixel processing, dither and bit-depth settings, generated test patterns, OPP buffer controls, DSC-forward routing, ABM control, and OPP pipe CRC capture.
- Timing-generator state in ODM/OTG/OPTC: source routing, timing totals, blanking/sync, triggers, master enable, double-buffer/update locks, vblank/vertical interrupts, CRC capture windows, snapshots, GSL/global sync, dynamic refresh-rate parameters, DTO constants, DSC start, and memory-power status.
- DIO state: I2C/DDC transactions and status, EDID detection, scratch registers, power/clock controls, DIG soft reset, HPD interrupts/filtering/fast-train controls, AUX transaction/status/PHY/GTC/wake state, VPG packet-generator state, AFMT audio packet/infoframe/CRC state, DME controls, and initial DIG0 HDMI stream-encoder state.
- Perfmon state for DPP2, DPP3, OPP, OPTC, and DIO local counters.

Persistence is hardware-defined. Configuration registers generally retain values until modeset, pipe reprogramming, block power gating, suspend/resume, or ASIC reset. Status, interrupt, counter, debug, wake, and power-status registers may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while clocks are enabled. This offset header does not describe those semantics; they come from the companion shift/mask header, hardware documentation, and consuming driver code.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.1 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h` for field shifts and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`, which includes this offset header and defines `BASE`, `SR`, `SRI`, `SRI2`, `SRIR`, `SRII`, and `SRII2` helpers that materialize register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`, which includes this header and uses `REG_OFFSET(reg)` through `dmub_reg.h`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h`, where `REG_OFFSET(reg_name)` expands to `BASE(mm##reg_name##_BASE_IDX) + mm##reg_name`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/vangogh_ip_offset.h`, included by the DCN301 resource and DMUB code to provide the matching IP segment base constants.

The likely consumers of these specific register families are DCN301 resource construction, DPP color/scaler objects, OPP/OPTC timing objects, DIO stream/link encoder paths, DCE AUX/I2C/HPD helpers, audio/infoframe packet code, and DMUB service initialization. Their integration pattern is compile-time token pasting; a register name typo or missing macro normally breaks the build, while a wrong numeric value compiles and fails only on hardware.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. The macros are untyped constants, so an incorrect numeric value can compile cleanly while directing MMIO to the wrong register.
- Chunk boundaries are artificial. The first line starts in the middle of `CM2` shaper RAM A definitions, and the final line stops after `mmDIG0_HDMI_GENERIC_PACKET_CONTROL6`; adjacent chunks are required for full-file claims.
- Repeated instance families are copy-sensitive. `FMT0`-`FMT3`, `DPG0`-`DPG3`, `OPPBUF0`-`OPPBUF3`, `OTG0`-`OTG3`, `HPD0`-`HPD3`, and `DP_AUX0`-`DP_AUX3` have similar register layouts but instance-specific offsets. A one-instance mistake may only appear with particular pipes, connectors, or multi-display topologies.
- Color pipeline programming is stateful. Bad CM/3D LUT/shaper/gamma/scaler offsets can cause wrong color conversion, HDR or gamut errors, cursor artifacts, invalid scaling, line-buffer failures, or blank/underflow conditions.
- Timing-generator and update-lock registers are high impact. Wrong OTG/ODM/OPTC offsets can cause missed vblank, stuck update locks, incorrect dynamic refresh-rate behavior, bad CRC captures, global-sync failures, or display modeset hangs.
- AUX/I2C/HPD registers are side-effect-sensitive. Incorrect interrupt/status/clear/wake/arbitration offsets can break EDID reads, DPCD transactions, hotplug detection, link training, wake from low power, or cause interrupt storms.
- Audio and packet registers affect protocol-visible stream metadata. Wrong VPG/AFMT/DIG HDMI offsets can corrupt infoframes, generic packets, audio clock regeneration, channel status, CRC reporting, or HDMI metadata packets.
- Power and memory-control offsets should only be used when the corresponding clocks and power domains are valid; writing while blocks are gated or reset can be ignored or produce hard-to-debug display bring-up failures.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN301 support enabled. Missing or renamed macros should fail in `dcn301_resource.c`, DMUB DCN301 register initialization, and hardware-object register-list construction.
- Mechanically verify this chunk's invariant: lines 5218-7845 contain 1,200 non-`_BASE_IDX` `mm...` macros, 1,200 matching `_BASE_IDX` macros, no unmatched pairs, and all base-index values are `2`.
- Diff `dcn_3_0_1_offset.h` and `dcn_3_0_1_sh_mask.h` against AMD's authoritative DCN 3.0.1 register source and against neighboring DCN headers where compatibility is expected.
- Exercise DPP3 and the tail of DPP2 color paths: modesets with color management, gamma/gamut/shaper/3D LUT programming, HDR output, cursor composition, scaling, CRC/debug reads, and suspend/resume.
- Exercise OPP/OPTC instances 0 through 3: multi-display modesets, pipe splitting or ODM use where supported, timing changes, vblank/vertical interrupt delivery, update locks, CRC capture, dynamic refresh rate, global sync, and DSC start-position programming.
- Exercise DIO paths represented here: DDC/EDID reads, AUX DPCD reads/writes, HPD plug/unplug and IRQ handling on connectors mapped to AUX/HPD 0 through 3, low-power wake, and link training.
- Validate VPG/AFMT/DIG0 stream metadata: HDMI/DP audio playback, infoframes, generic packets, MPEG/ISRC packets, audio CRC/status, ACR packet programming, and HDMI metadata packet updates.
- Watch kernel logs and display diagnostics for AUX timeouts, HPD storms, EDID failures, link-training failures, blank displays, vblank misses, update-lock stalls, underflow, CRC mismatches, audio dropouts, and resume failures.

## Cross-Chunk Notes

Previous chunks own the beginning of the DPP2 `CM2` color-management block before `CM2_CM_SHAPER_RAMA_REGION_12_13`. Later chunks continue the DIG0 HDMI/generic-packet and stream-encoder register set after `mmDIG0_HDMI_GENERIC_PACKET_CONTROL6` and likely cover additional DIG/DP/VPG/AFMT/DME instances. The final per-file research document should merge adjacent chunks before making complete claims about all DPP, OPP, OPTC, DIO, or DIG register coverage in `dcn_3_0_1_offset.h`.

### subset-b-001719: lines 7846-10422

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h lines 7846-10422

## Scope

This chunk is a generated AMD DCN 3.0.1 register offset slice. It contains preprocessor constants only: no functions, structs, enums, local storage, or executable branches. The exported contract is the `mm...` register-offset macro plus its paired `mm..._BASE_IDX` macro, consumed by AMD display register-table builders to form absolute MMIO register addresses.

The assigned range starts in the middle of the `DIG0` HDMI/TMDS register group and ends in the middle of `MPCC_OGAM0` output-gamma RAM A region definitions. It contains 1205 register-offset macros and 1204 visible `_BASE_IDX` companions; the last visible macro, `mmMPCC_OGAM0_MPCC_OGAM_RAMA_REGION_6_7`, is cut off before its `_BASE_IDX` line in the next chunk.

## Purpose

The purpose of this chunk is to map DCN 3.0.1 display hardware blocks to register offsets for display engine programming. The values are not policy and do not implement algorithms; they provide ASIC-specific address metadata for display link, audio/video packet, GPIO/AUX/DDC, DSC compression, writeback, display VM, and MPC composition paths.

Major hardware areas represented here are:

- DIO stream/link instances: tail of `DIG0`, then `DIG1`, `DIG2`, and `DIG3` front-end/HDMI/TMDS registers; `DP0` through `DP3` link, main-stream-attribute, DPHY, secondary-data packet, MST MSE, DSC, ALPM, and GSP registers.
- Video packet/audio formatter blocks for links 1-3: `VPG1` through `VPG3`, `AFMT1` through `AFMT3`, and small `DME1` through `DME3` memory/control register groups.
- DCIO top and chip registers: generic DCIO clocks, reference clock, UNIPHY link/channel xbar controls, panel power sequencing, backlight PWM, genlock/swaplock pads, soft reset, GPIO/DDC/HPD/PWRSEQ pad controls, AUX controls, and AUX/I2C pad power status.
- UNIPHY macro reserved ranges for `DCIO_UNIPHY1`, `DCIO_UNIPHY2`, and `DCIO_UNIPHY3`, each exposing reserved register slots 0-47 for PHY macro access.
- DSC instances 0-2: `DSC_TOP`, `DSCCIF`, `DSCC` configuration/PPS/error/rate-buffer registers and `DC_PERFMON17` through `DC_PERFMON19`.
- Writeback instance 0: DWB top/flow-control/CRC/overflow/host-read/reset/debug registers, `DC_PERFMON20`, and DWB color-processing registers for HDR multiplier, gamut remap A/B matrices, and output-gamma RAM A/B PWL descriptors.
- Display HVM: `DCHVM_CTRL0`, `DCHVM_CTRL1`, clock/memory controls, and RIOMMU control/status offsets.
- MPC/MPCC start: `MPCC0` through `MPCC3` composition selector/control/gain/background/memory/status registers and the start of `MPCC_OGAM0` output-gamma LUT/RAM A definitions.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro namespace:

- `mm<REGISTER>` gives the per-ASIC offset for a display register.
- `mm<REGISTER>_BASE_IDX` gives the base segment index to pass through `BASE(...)`.
- Address block comments document the hardware block and local base address that generated each group.

Every complete register entry is intended to be consumed as `BASE(mmREG_BASE_IDX) + mmREG`. In DCN 3.0.1 display resource code, `dcn301_resource.c` includes this header and defines helpers such as `SR`, `SRI`, `SRII`, and `SRII2` that paste register names into resource-specific register tables. DMUB code also includes the same header and uses `REG_OFFSET(reg)` through `dmub_reg.h` to populate firmware-service register offsets.

Representative macro families in this chunk include:

- Link programming: `mmDP0_DP_LINK_CNTL` through `mmDP3_DP_GSP_EN_DB_STATUS`, covering DP link setup, pixel format, MSA, stream timing, training patterns, CRC, audio secondary-data packets, MST allocation, DSC enable/control, ALPM, and generic stream packets.
- HDMI/TMDS and audio packet programming: `mmDIG1_HDMI_CONTROL`, `mmDIG2_HDMI_GENERIC_PACKET_CONTROL*`, `mmDIG3_TMDS_CNTL`, `mmAFMT*_AFMT_AUDIO_*`, and `mmVPG*_VPG_GENERIC_PACKET_*`.
- DCIO/pads: `mmDCIO_CLOCK_CNTL`, `mmDC_REF_CLK_CNTL`, `mmUNIPHY[A-D]_LINK_CNTL`, `mmPANEL_PWRSEQ*_CNTL`, `mmBL_PWM*_CNTL`, `mmDC_GPIO_DDC*_MASK/A/EN/Y`, `mmDC_GPIO_HPD_*`, `mmDC_GPIO_AUX_CTRL_*`, and `mmAUXI2C_PAD_ALL_PWR_OK`.
- DSC: `mmDSC_TOP*_DSC_TOP_CONTROL`, `mmDSCCIF*_DSCCIF_CONFIG*`, `mmDSCC*_DSCC_CONFIG*`, `mmDSCC*_DSCC_PPS_CONFIG0..22`, error counters, rate-buffer fullness, and debug-bus rotation.
- Writeback: `mmDWB_ENABLE_CLK_CTRL`, `mmFC_MODE_CTRL`, `mmDWB_CRC_*`, `mmDWB_OVERFLOW_*`, `mmDWB_HDR_MULT_COEF`, `mmDWB_GAMUT_REMAP*`, and `mmDWB_OGAM_*`.
- MPC/MPCC: `mmMPCC0_MPCC_TOP_SEL` through `mmMPCC3_MPCC_STATUS` and the opening `mmMPCC_OGAM0_MPCC_OGAM_*` LUT/RAM A offsets.

## Control Flow

This chunk has no local control flow. Runtime control flow lives in the display driver objects that include the offset header and companion `dcn_3_0_1_sh_mask.h`.

Important flows represented by these offsets are:

1. DCN301 resource construction builds per-block register tables by expanding macros such as `SR`, `SRI`, and `SRII` over hardware-object register lists. The generated table values become addresses used by register helpers like `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.
2. DMUB service setup includes this header in `dmub_dcn301.c` and initializes common DMUB register offsets with `REG_OFFSET(reg)`, using `BASE(mmREG_BASE_IDX) + mmREG`.
3. Link encoder and stream encoder flows program DP/HDMI/TMDS registers during modeset and link training. The DP offsets drive link count, pixel format, MSA, training-pattern, DPHY, secondary-data, MST allocation, DSC, and ALPM programming for link instances 0-3.
4. Audio/video packet flows use VPG and AFMT offsets to write generic packets, infoframes, HDMI audio/ACR controls, VBI packets, audio info/channel-status data, CRC controls, source selection, and memory-power controls.
5. DCIO GPIO/AUX/DDC/HPD flows read or write pad mask, data, enable, and output registers, plus panel/backlight sequencing registers, to support display detection, AUX/I2C transactions, hotplug handling, eDP panel power, and backlight PWM.
6. DSC flows program PPS/config registers, observe status/error/rate-buffer registers, and use per-DSC perfmon registers for compression and performance diagnostics.
7. DWB flows configure writeback clock/memory, frame-composition window/source sizes, CRC, overflow reporting, host reads, color conversion, gamut remap, and output gamma RAM descriptors.
8. MPC/MPCC flows configure composition source selection, OPP association, blending gains, background color, update-lock selection, memory power, and OGAM LUT state for composed output.

The macros do not encode hardware sequencing, volatile/status semantics, write-one-to-clear behavior, polling timeouts, lock ordering, or frame-boundary update rules. Callers must follow those rules in the DC, DIO, DSC, DWB, DCIO, DMUB, and MPC implementation files.

## State And Persistence Behavior

The header stores no software state and persists nothing by itself. It describes MMIO register locations whose hardware state persists until changed by the driver, firmware, reset, power gating, suspend/resume, display off/on transitions, or modeset reprogramming.

State represented by this chunk includes:

- Per-link DP/HDMI/TMDS state: link framing, pixel format, MSA timing/colorimetry, stream enable, training pattern, DPHY scrambler/CRC/test patterns, audio timing, secondary-data packet scheduling, MST stream-allocation table values, DSC link enable, ALPM control, and generic stream packet status.
- Per-link VPG/AFMT state: generic packets, GSP frame/immediate update controls, ISRC/MPEG info data, HDMI/DP audio packet controls, audio info/channel status, CRC, interrupts, source selection, and memory power.
- DCIO physical-interface state: UNIPHY link routing, channel crossbar selection, reference clocks, panel power sequencing, backlight PWM periods/duty controls, pad strength, GPIO/DDC/HPD/PWRSEQ direction and output values, AUX controls, and pad power-good status.
- DSC state: top-level enable/debug settings, DSCCIF config, DSCC PPS registers, memory power, compressor error accumulation, rate buffer fullness, and debug/perfmon counters.
- DWB state: flow-control source/window sizing, update control, CRC masks/values, host read controls, overflow counters, soft reset/debug, gamut-remap matrices, HDR multiplier, OGAM LUT index/data/control, and A/B PWL region descriptors.
- DCHVM state: display HVM control, clock/memory behavior, and RIOMMU control/status.
- MPC state: MPCC top/bottom input selection, OPP routing, blend control, gains, background color, memory power, status, and the beginning of MPCC OGAM LUT/RAM A state.

Many of these registers are live hardware controls or status registers. Some are double-buffered, banked, or synchronized to frame updates by surrounding display code. A wrong offset can therefore produce intermittent link, color, timing, or power bugs rather than a clean compile-time failure.

## Dependencies And Integration Points

The companion field-layout header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h`. This offset header supplies register addresses; the shift/mask header supplies bit positions and masks inside those registers. Both are required for meaningful register access.

Primary integration points visible in this repository are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`, which includes this header, defines `BASE`, `SR`, `SRI`, `SRII`, and related table-expansion helpers, and wires DCN301 hardware objects to generated register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`, which includes this header and initializes DMUB service register offsets.
- DCN30/DCN301 DIO stream/link encoder, VPG, AFMT, DSC, DWB, DCIO, panel control, AUX/I2C, and MPC code that receives generated register tables from resource construction.
- ASIC base-address metadata such as `vangogh_ip_offset.h`, which provides `DCN_BASE__INST0_SEG*` values consumed by `BASE(mm..._BASE_IDX)`.
- Register helper macros in the AMD display stack, which turn the generated offsets and companion masks into MMIO reads, writes, updates, and waits.

Although this path is under `sources/distributed-fs/ceph-client`, the chunk is AMDGPU display hardware metadata. It has no Ceph filesystem behavior, no distributed protocol logic, and no persistent storage semantics beyond hardware register state.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A bad offset or base-index constant usually compiles cleanly but sends a register write/read to the wrong address. The result can be a visibly broken display, a power-management failure, or diagnostics that report plausible but wrong data.

Instance repetition is a major edge case. DP/DIG/VPG/AFMT/DME instances follow repeated address patterns with per-instance offsets, while DCIO and DSC/DWB blocks switch to different address ranges. Copy-generation mistakes can affect only one link or one DSC/DWB instance, producing connector-specific or mode-specific failures.

The chunk starts mid-`DIG0` and ends mid-`MPCC_OGAM0`; adjacent chunks are needed to validate complete DIG0 and MPCC_OGAM0 coverage. The visible final macro lacks its `_BASE_IDX` in this chunk, so any chunk-local checker must treat that as a range boundary artifact rather than a malformed header.

DP/DIG risks include failed link training, wrong pixel format or MSA values, blank screens, unstable audio, bad HDMI infoframes, MST allocation errors, DSC-on-link failures, ALPM regressions, TMDS test-pattern failures, or status polling against the wrong lane/link register.

DCIO/GPIO risks include missed hotplug events, broken AUX/I2C/DDC transactions, incorrect panel/backlight sequencing, stuck GPIO direction/output state, wrong UNIPHY routing, and suspend/resume bugs where pad or PHY state is restored to the wrong register.

DSC risks include invalid PPS programming, compressor status reads from the wrong instance, incorrect error/rate-buffer diagnostics, and failures only on modes requiring DSC bandwidth savings.

DWB risks include corrupted writeback frames, bad CRC/overflow diagnostics, incorrect source/window sizing, color conversion or gamma errors, and host-read/debug accesses hitting unrelated registers.

MPC/MPCC risks include wrong composition routing, incorrect blend gains or background colors, memory-power/status reads from wrong MPCCs, and output-gamma LUT corruption. Because the MPCC range changes `_BASE_IDX` from 2 to 3, base-index mistakes around line 10242 are especially high impact.

## Test Signals

Useful validation signals are a mix of generated-header checks and display behavior:

- Build coverage for DCN301 display and DMUB code that includes `dcn_3_0_1_offset.h` and `dcn_3_0_1_sh_mask.h`.
- Generated consistency checks that every complete `mmREG` macro has a matching `mmREG_BASE_IDX`, every register used by DCN301 register-list macros exists, and companion shift/mask definitions exist for fields used by code.
- Address-pattern checks across repeated instances: `DP0..DP3`, `DIG1..DIG3`, `VPG1..VPG3`, `AFMT1..AFMT3`, `DME1..DME3`, `DSC0..DSC2`, `DSCC0..DSCC2`, and `MPCC0..MPCC3` should match expected per-instance strides unless hardware metadata documents a deviation.
- Runtime link tests across all physical outputs: DP link training at multiple rates/lane counts, HDMI/TMDS modes, audio/ACR/infoframe behavior, MST, DSC-over-DP, ALPM, and hotplug/replug.
- AUX/DDC/panel/backlight tests: EDID reads, HPD interrupt handling, eDP panel power sequencing, backlight PWM changes, suspend/resume, runtime PM, and display off/on cycles.
- DSC tests with modes that require and do not require DSC, checking visual output, PPS programming, rate-buffer/error counters, and perfmon counters.
- DWB tests that capture known frame content, verify CRC and overflow behavior, exercise host reads, and validate gamut/OGAM paths.
- MPC/MPCC tests for multi-plane composition, blending, OPP routing, background color, output gamma, update locks, and transitions during modeset.

Regression symptoms from this chunk include black screens, link-training failures, connector-specific failures, missing audio or malformed infoframes, hotplug/DDC/AUX failures, panel/backlight sequencing problems, DSC-only mode failures, corrupted writeback output, bad gamma or blend output, stuck register waits, and misleading debug/performance counters.

## Cross-Chunk Notes

This is an artificial line-range slice of a large generated constants header. The final per-file report should merge this with adjacent chunks to describe complete DCN 3.0.1 offset coverage, especially the preceding `DIG0` register block and the continuation of `MPCC_OGAM0` after line 10422.

### subset-b-001720: lines 10423-13004

# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h lines 10423-13004

## Scope

This chunk covers lines 10423-13004 of the generated DCN 3.0.1 register-offset header. The content is preprocessor data: `#define` constants mapping AMD display hardware register names to register offsets, plus matching `*_BASE_IDX` selector constants for MMIO base table selection. There are no C functions, types, or executable control-flow constructs in this span.

Within this chunk there are 2390 preprocessor defines: 1613 register/index offset macros and 777 `*_BASE_IDX` companion macros. The first line continues the previous `MPCC_OGAM0` block, and the final line ends mid-pattern inside the `azf0endpoint7_endpointind` block; whole-file reconciliation must account for neighboring chunks.

## Purpose

The header gives the AMDGPU DC display driver stable symbolic names for DCN 3.0.1 hardware registers. Driver code can refer to register names such as `mmMPC_CLOCK_CONTROL`, `mmABM0_BL1_PWM_USER_LEVEL`, or `ixAZF0ENDPOINT6_AZALIA_F0_CODEC_PIN_CONTROL_LPIB` without embedding numeric offsets directly. The `mm` names are memory-mapped display registers; the `ix` names are indexed/indirect register offsets used through an index/data access path.

This chunk specifically covers late MPC/MPCC color-processing registers, ABM backlight/statistics registers, legacy VGA indexed registers, and Azalia/HD-audio codec, stream, CRC, and endpoint register indices.

## Main Register Groups

- `MPCC_OGAM0` tail: starts at the continuation of output gamma RAM A/B region and gamut remap macros, including `RAMA_REGION_*`, `RAMB_START_*`, `RAMB_END_*`, `RAMB_OFFSET_*`, `RAMB_REGION_*`, and `MPC_GAMUT_REMAP_*` definitions.
- `MPCC_OGAM1`, `MPCC_OGAM2`, and `MPCC_OGAM3`: complete repeated output-gamma blocks at base addresses `0x200`, `0x400`, and `0x600`. Each block exposes LUT index/data/control, RAM A/B piecewise gamma controls for B/G/R channels, region tables, gamut remap format/mode, and two banks of 3x4 remap coefficients.
- `MPC_CFG`: global MPC control/status registers such as clock control, soft reset, CRC control/results, perfmon event selection, bypass background values, host read control, DPP pending status, pending misc status, VUPDATE lock sets 0-3, and DWB mux selection.
- `MPC_OCSC`: output mux, denormalization clamp, and output color-space-conversion definitions for outputs 0-3. The repeated `MPC_OUT*_CSC_*` macros define mode and coefficient banks A/B.
- `MPC_RMU`: retiming/mapping unit color pipeline registers including RMU control/memory power, shaper LUT controls, shaper RAM A/B controls and regions for RMU0/RMU1, and 3D LUT mode/index/data/output normalization/offset registers.
- `DC_PERFMON21`: display performance counter and monitor control/state/value macros for perfmon instance 21.
- `ABM0` through `ABM3`: OPP adaptive backlight management blocks at base addresses `0x0`, `0x104`, `0x208`, and `0x30c`. Each exposes PWM ambient/user/target/current/final/minimum levels, ABM control, update sample rate, register lock, histogram/gather controls, luma statistics, histogram result bins 1-24, and backlight master lock.
- `vga_*ind`: indexed VGA sequencer, CRT controller, graphics controller, and attribute controller register indices.
- `azendpoint_f2codecind`, `azinputendpoint_f2codecind`, and `azroot_f2codecind`: Azalia function 2 codec, input codec, pin, root, converter, power, stream format, multichannel, sink-info, LPIB, coding, format-change, and keepalive indices.
- `azendpoint_descriptorind` and `azendpoint_sinkinfoind`: audio descriptor and audio sink metadata index constants.
- `azf0controller_*crc*ind`: Azalia input/output CRC result channel index constants.
- `azf0stream0` through `azf0stream15`: repeated FIFO size and latency counter indices for 16 Azalia streams.
- `azf0endpoint0` through `azf0endpoint7`: repeated endpoint register index maps. This chunk fully covers endpoints 0-6 and starts endpoint 7, with converter capability/control, pin capability/control, descriptor, multichannel, sink, hot-plug, channel-status override, LPIB, coding, format-change, wireless display, remote keepalive, and audio enable/interrupt status indices.

## Important APIs, Types, and Macros

The exported API surface is entirely macro names consumed by register access helpers elsewhere in the AMD display driver. Important naming conventions:

- `mm...` macros map direct MMIO register names to offsets in the selected ASIC register base space.
- `ix...` macros map indirect/indexed register names to index values.
- `..._BASE_IDX` macros, all visible examples in this chunk using value `3`, identify the register base index used by generated access macros and register tables.
- Instance numbers are encoded in the macro name, for example `MPCC_OGAM1`, `MPC_OUT3`, `ABM2`, `AZF0STREAM15`, and `AZF0ENDPOINT6`.
- Repeated hardware blocks preserve the same local register layout while shifting the direct MMIO offsets by block instance. For example, `MPCC_OGAM1` begins at `0x0180`, `MPCC_OGAM2` at `0x0200`, and `MPCC_OGAM3` at `0x0280`.

There are no structs, enums, inline functions, function pointers, or C symbols with storage duration in this chunk.

## Control Flow and Data Flow

This header chunk has no runtime control flow. Its data flow is compile-time substitution:

1. The C preprocessor expands symbolic register names into numeric offsets.
2. Register-access macros or generated register lists in the display driver pair those offsets with `*_BASE_IDX` values.
3. The driver then performs MMIO or indexed register reads/writes against the GPU display hardware.

The effective runtime behavior is therefore defined by consumer code, not by this header. Typical consumers will program color pipelines, backlight behavior, audio endpoints, or collect diagnostics by reading/writing the offsets declared here.

## State and Persistence

The file itself maintains no software state and has no persistence behavior. The constants address hardware state:

- MPCC/MPC OGAM, CSC, shaper, gamut remap, and 3D LUT registers hold display color-pipeline configuration.
- MPC status, CRC, perfmon, pending, and VUPDATE lock registers expose transient display-controller state and synchronization controls.
- ABM registers hold or report backlight control levels, luma statistics, histogram bins, and lock state.
- Azalia stream, endpoint, codec, CRC, and sink-info indices represent audio hardware or monitor/codec state exposed through indexed register windows.

Incorrect constants can persistently affect the live display session until the driver reprograms hardware or the device is reset, even though the constants themselves are stateless.

## Dependencies and Integration Points

This chunk depends on the AMD DCN 3.0.1 hardware register layout generated from ASIC register descriptions. It integrates with:

- AMDGPU display core register access helpers that concatenate register base addresses, offsets, masks, and shifts.
- DC color-management code that writes OGAM, gamut remap, output CSC, shaper, and 3D LUT registers.
- MPC/MPCC composition and output-pipeline setup code that programs muxes, resets, clocks, CRC, and update locks.
- OPP/ABM code that programs adaptive backlight behavior and reads histogram/luma statistics.
- Display audio/Azalia code that uses `ix` indexed constants for codec, pin, stream, endpoint, sink, and CRC operations.
- Diagnostic and validation code reading CRC/perfmon/status registers.

The neighboring offset and shift/mask headers must remain in sync with this file. A register offset without matching mask/shift definitions, or vice versa, is a strong signal of generator or integration drift.

## Risks

- The file is generated-style hardware ABI data; hand edits are risky because a one-value mismatch can redirect a register write to unrelated hardware.
- Repeated blocks are easy to misalign. A missing or shifted macro in one instance of `MPCC_OGAM*`, `ABM*`, stream, or endpoint blocks could affect only one display pipe/audio endpoint and be hard to notice in broad tests.
- The chunk starts and ends inside larger repeated patterns, so merge/reconciliation must not infer completeness from this chunk alone.
- Direct `mm` offsets and indirect `ix` indices are different address spaces; using an `ix` value through a direct MMIO path, or an `mm` value through an indexed path, would be a consumer bug with potentially confusing symptoms.
- `*_BASE_IDX` value consistency matters. The visible direct-register base index value is consistently `3`; changing this would alter address-base selection for consumers.
- ABM and color-pipeline register errors can manifest as visible color/gamma/backlight defects rather than compile failures.
- Azalia endpoint/index errors can manifest as HDMI/DP audio failures, incorrect sink capabilities, stale LPIB snapshots, or missed audio enable/format-change interrupts.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build tests that include DCN 3.0.1 display headers and compile AMDGPU register access users without undefined macro errors.
- Generator consistency checks comparing this offset header against its corresponding mask/shift header and source ASIC register database.
- Display color-management tests exercising OGAM LUT programming, gamut remap, output CSC, shaper LUTs, and 3D LUT paths on DCN 3.0.1 hardware.
- Multi-pipe display tests covering MPCC OGAM instances 0-3 and output CSC instances 0-3.
- ABM/backlight tests on panels supporting adaptive backlight, checking PWM level programming, luma histogram reads, sample rates, and lock behavior across ABM0-ABM3.
- CRC/perfmon diagnostics validating `MPC_CRC_*`, `DC_PERFMON21_*`, and Azalia CRC result indices.
- HDMI/DP audio tests covering codec root/function parameters, converter format, channel/stream IDs, hot-plug/audio-enable interrupts, LPIB snapshots, sink info, multichannel controls, HBR, and endpoints 0-7.
- Runtime register tracing can confirm that consumers write expected offsets and do not mix direct MMIO and indexed-register access paths.

## Open Questions for Merge

- The prior chunk should include the start of `MPCC_OGAM0`, including its control, LUT, RAMA start/end, and early region macros before this chunk begins at `RAMA_REGION_6_7_BASE_IDX`.
- The following chunk should complete `azf0endpoint7_endpointind`, because this chunk ends after the early endpoint-7 pin-control/audio-descriptor definitions.
- Whole-file synthesis should verify how many MPCC OGAM, ABM, Azalia stream, and endpoint instances are expected for DCN 3.0.1 and flag any missing instance only after all chunks are available.

### subset-b-001721: lines 13005-13271

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h lines 13005-13271

## Scope And Purpose

This chunk is the final segment of AMD's generated DCN 3.0.1 register-offset header. It contains C preprocessor constants only; it does not define functions, structs, enums, executable branches, or mutable storage. The source path is inside a local `ceph-client` mirror, but this file is AMDGPU display-driver hardware metadata rather than Ceph filesystem logic.

The covered range starts in the tail of the `azf0endpoint7_endpointind` address block, beginning at `ixAZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR5`, and completes output endpoint 7 through `ixAZF0ENDPOINT7_AZALIA_F0_AUDIO_FORMAT_CHANGED_INT_STATUS`. It then defines complete input endpoint indirect-register blocks for `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint7_inputendpointind` and closes the header guard with `#endif`.

All values in this range are `ix...` indirect register indices with `base address: 0x0`. They are not direct MMIO offsets. Runtime code writes these small index values, such as `0x0038`, `0x0054`, or `0x0068`, into an Azalia endpoint index register and transfers payloads through the matching endpoint data register.

## Important Definitions

The output endpoint 7 tail exposes endpoint-local HDMI/DisplayPort audio pin and status indices:

- `ixAZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR5` through `...AUDIO_DESCRIPTOR13` at `0x002d` through `0x0035`, continuing the EDID/ELD-derived audio descriptor slots started before this chunk.
- `...MULTICHANNEL_ENABLE`, `...RESPONSE_LIPSYNC`, and `...RESPONSE_HBR` at `0x0036` through `0x0038`, used for channel routing, latency reporting, and high bit rate audio capability or enable state.
- `...SINK_INFO0` through `...SINK_INFO8` at `0x003a` through `0x0042`, used by the display audio path to publish sink manufacturer/product/port/name information.
- `...HOT_PLUG_CONTROL`, `...UNSOLICITED_RESPONSE_FORCE`, `...RESPONSE_CONFIGURATION_DEFAULT`, `...MULTICHANNEL_ENABLE2`, and `...MULTICHANNEL_MODE` at `0x0054` through `0x0058`.
- `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` at `0x0059` through `0x0061`, covering IEC 60958 channel-status override payload registers.
- `...CODEC_PIN_ASSOCIATION_INFO`, `...DIGITAL_OUTPUT_STATUS`, LPIB snapshot/readback/timer indices, `...CODING_TYPE`, `...FORMAT_CHANGED`, `...WIRELESS_DISPLAY_IDENTIFICATION`, `...REMOTE_KEEPALIVE`, and audio enable/disabled/format-changed interrupt status indices at `0x0062` through `0x006e`.

Each input endpoint block `0..7` repeats the same 22-index layout:

- Input converter indices at `0x0001` through `0x0006`: audio widget capabilities, converter format, channel/stream ID, digital converter control, stream formats, and supported size/rates.
- Input pin indices at `0x0020` through `0x0024`: input pin widget capabilities, pin capabilities, unsolicited response control, input pin sense response, and widget control.
- Multichannel, HBR, channel allocation, hot-plug/audio state, forced unsolicited response, configuration default, LPIB snapshot/readback/timer, input status control, and infoframe indices at `0x0036` through `0x0068`.

The repeated `ixAZF0INPUTENDPOINTn_AZALIA_F0_CODEC_INPUT_*` names are the exported compile-time API for endpoint-local input audio registers. The input endpoint layout is smaller than the output endpoint layout because it omits output-only sink-info, audio descriptor, channel-status override, digital-output status, coding type, wireless display, keepalive, and audio format-change interrupt groups.

## Control Flow

There is no local control flow in this header. The effective runtime flow is created by AMD display/audio register helpers:

1. `display/dc/resource/dcn301/dcn301_resource.c` includes `dcn/dcn_3_0_1_offset.h` and constructs `audio_regs[]` with `AUD_COMMON_REG_LIST(id)` for audio instances 0 through 6.
2. `AUD_COMMON_REG_LIST(id)` in `display/dc/dce/dce_audio.h` maps `AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_ENDPOINT_DATA` through the per-instance `AZF0ENDPOINT{id}` direct MMIO register pair.
3. `dcn301_create_audio()` passes the selected `audio_regs[inst]` plus shift/mask tables to `dce_audio_create()`.
4. `display/dc/dce/dce_audio.c` uses `AZ_REG_READ()` and `AZ_REG_WRITE()` macros that expand an indirect name to `ix<name>`, write the index through `AZALIA_F0_CODEC_ENDPOINT_INDEX.AZALIA_ENDPOINT_REG_INDEX`, and read or write `AZALIA_F0_CODEC_ENDPOINT_DATA.AZALIA_ENDPOINT_REG_DATA`.
5. Higher-level audio setup programs endpoint registers for HBR, lipsync, hotplug/audio enable, speaker and channel allocation, audio descriptors, and sink-info fields. The endpoint 7 constants in this chunk are the instance-specific generated names for the same indirect index space.

The input endpoint constants in this chunk are available to code that needs input/capture endpoint metadata, input activity state, channel layout, or infoframe-derived channel information. The common DC display audio path seen in this tree primarily exercises output endpoint programming, so input endpoint runtime coverage may depend on hardware and feature paths outside the usual HDMI/DP playback setup.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. They do not store state and cannot perform hardware I/O on their own.

The hardware registers selected by these indices are stateful. Output endpoint 7 can retain audio descriptor slots, multichannel routing, HBR and lipsync state, sink metadata, hotplug/audio enable state, forced unsolicited-response state, configuration defaults, channel-status overrides, LPIB snapshots, coding and format-change status, wireless display identification, keepalive control, and audio interrupt status. Input endpoints can retain converter format, stream/channel identifiers, digital converter flags, pin capabilities, input sense, multichannel routing, channel allocation, HBR state, hotplug/audio state, configuration defaults, LPIB snapshots, input activity, channel layout, and infoframe validity.

Persistence is governed by the GPU display/audio block, HDA/Azalia controller behavior, display hotplug, stream start/stop, suspend/resume, power gating, and GPU/display resets. Some indices select configuration state, some select readback/status state, and some select action or interrupt-related registers. This offset header does not encode access type, reset value, write-one-to-clear behavior, reserved-bit policy, or required sequencing.

## Dependencies And Integration Points

This chunk depends on the DCN 3.0.1 ASIC register database that generated `dcn_3_0_1_offset.h`. It must remain aligned with:

- `dcn_3_0_1_sh_mask.h`, which supplies bit shifts and masks for the endpoint payload registers selected by these indices.
- `display/dc/resource/dcn301/dcn301_resource.c`, which includes this offset header and builds the DCN 3.0.1 audio resource tables.
- `display/dc/dce/dce_audio.h`, especially `AUD_COMMON_REG_LIST`, `AUD_COMMON_MASK_SH_LIST_BASE`, and the `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` contracts.
- `display/dc/dce/dce_audio.c`, where `write_indirect_azalia_reg()`, `read_indirect_azalia_reg()`, `AZ_REG_READ()`, and `AZ_REG_WRITE()` implement the index/data access pattern.
- AMD register helper macros such as `SR`, `SRI`, `SF`, `REG_SET`, `REG_READ`, `set_reg_field_value`, and `get_reg_field_value`.

The file is also included by `display/dmub/src/dmub_dcn301.c` for DCN 3.0.1 DMUB register definitions, though this specific Azalia endpoint tail is most directly relevant to display audio rather than DMUB command processing.

## Risks And Edge Cases

The main risk is treating these constants as direct MMIO offsets. The `ix...` values are endpoint-local indices, and using them outside the Azalia index/data path would target the wrong address space.

Wrong index values are hardware ABI bugs. They can compile cleanly while redirecting a descriptor, sink-info, HBR, hotplug, LPIB, status, or infoframe operation to the wrong endpoint-local register. Symptoms may be missing HDMI/DP audio, wrong channel count or channel allocation, absent HBR formats, stale monitor audio names, bad lipsync values, stuck audio enable state, or incorrect input activity reporting.

The chunk boundary is artificial. Output endpoint 7 begins before line 13005, so this range only covers descriptor 5 onward and the later pin/status registers. Final per-file reconciliation should merge this with the previous chunk before describing endpoint 7 as a complete block.

The input endpoint blocks are highly repetitive. Copy or generator drift affecting only `AZF0INPUTENDPOINT3` or another single instance would be easy to miss in review and may only fail on hardware paths that expose that input endpoint. Structural checks should compare all eight input endpoint blocks for identical names and index values aside from the instance number.

Status, interrupt, snapshot, and force registers may have side effects that are not visible in this offset file. In particular, unsolicited response force, audio enabled/disabled/format-changed interrupt status, input status control, and LPIB snapshot controls must be used with the access semantics from the hardware specification and companion mask header.

## Test Signals

High-signal build checks include compiling DCN 3.0.1 display code that includes `dcn_3_0_1_offset.h`, especially `dcn301_resource.c`, `dmub_dcn301.c`, `dce_audio.h`, and `dce_audio.c`. Missing or renamed macros should surface through token-concatenated `SRI`, `SF`, and `IX_REG` usage.

Generated-header validation should verify that each `ixAZF0ENDPOINT7_...` and `ixAZF0INPUTENDPOINT0..7_...` index in this range has a matching field layout in the companion shift/mask header, and that all eight input endpoint blocks are structurally identical.

Runtime validation requires DCN 3.0.1-class hardware. Useful signals include HDMI/DP audio playback across exposed audio endpoints, hotplug/replug behavior, modeset and suspend/resume audio restoration, HBR and multichannel playback, EDID audio descriptor publication, sink manufacturer/name fields visible through the audio stack, and stable `HOT_PLUG_CONTROL` / audio enable state.

For the input endpoint constants, useful signals include input activity changes, channel-layout/status infoframe changes, `INFOFRAME_VALID` readback, HBR and channel-allocation behavior where supported, and LPIB snapshot/timer consistency during active input streams. Negative signals include endpoint-specific audio failures, wrong advertised audio capabilities, repeated unsolicited responses, stale LPIB snapshots, or failures isolated to one generated input endpoint instance.
