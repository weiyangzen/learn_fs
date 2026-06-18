# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002081`: lines 1-2727, `Docs/researches/chunks/subset-b-002081_research.md`
- `subset-b-002082`: lines 2728-5263, `Docs/researches/chunks/subset-b-002082_research.md`
- `subset-b-002083`: lines 5264-7875, `Docs/researches/chunks/subset-b-002083_research.md`
- `subset-b-002084`: lines 7876-10402, `Docs/researches/chunks/subset-b-002084_research.md`
- `subset-b-002085`: lines 10403-12994, `Docs/researches/chunks/subset-b-002085_research.md`
- `subset-b-002086`: lines 12995-15259, `Docs/researches/chunks/subset-b-002086_research.md`

## Chunk Research

### subset-b-002081: lines 1-2727

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h lines 1-2727

## Purpose

This chunk is the opening slice of AMD's generated DCN 3.5.1 register-offset header. It has no executable C logic; it publishes preprocessor constants that name DCN 3.5.1 MMIO registers, indirect-register indices, and register-base selector indices for display, audio, DMU/DMCUB, clock, writeback, hub, and interrupt-routing blocks. Driver code combines these offsets with the companion `dcn_3_5_1_sh_mask.h` shift/mask header so register-list macros can construct per-ASIC register tables.

The requested range covers the license, header guard opening, and the first 2,337 `#define` entries in a 15,259-line file. Within this range there are 1,322 `reg*` defines, 1,014 `ix*` indirect-index defines, and one header-guard define. The `reg*` entries appear as offset/base-index pairs, where `regFOO` gives a register offset and `regFOO_BASE_IDX` selects the base segment used by the AMD display register helpers. The `ix*` entries are indirect register indices used through paired index/data windows, especially Azalia codec endpoint, stream, and function nodes.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The exported interface is the generated macro namespace:

- `reg<REGISTER>`: numeric MMIO register offset within the corresponding DCN register segment.
- `reg<REGISTER>_BASE_IDX`: segment selector passed through `BASE(reg..._BASE_IDX)` style macros before adding the register offset.
- `ix<INDIRECT_REGISTER>`: index value for an indirect register reached through an index/data pair.

The main macro families in this line range are:

- HDA/Azalia global controller offsets for capabilities, version fields, payload capacities, global control/status, wake and state-change status, interrupt control/status, wall-clock counter, CORB/RIRB ring base addresses and pointers, immediate command/response windows, and DMA position buffer addresses.
- Azalia sink and diagnostics indirect indices for manufacturer/product ID, port IDs, sink-description bytes, input CRC result channels, output CRC result channels, and per-stream FIFO/latency counters for streams 0-15.
- Azalia F0 endpoint indirect indices for output endpoints 0-7. Each endpoint has the same converter and pin-control shape: widget capabilities, stream formats, supported rates, converter format, channel/stream ID, digital-converter control, GTC embedding and deltas, pin capabilities, unsolicited responses, pin sense, widget control, speaker/channel allocation, audio descriptors 0-13, multichannel controls, lipsync, HBR, sink info, hotplug, IEC 60958 channel-status override indices, LPIB snapshots, coding type, format-change state, wireless display identification, remote keepalive, audio enable status, and endpoint interrupt status.
- Azalia F0 input-endpoint indirect indices for input endpoints 0-7. These cover input converter format, channel/stream ID, digital-converter state, supported formats/rates, input pin capabilities, unsolicited response, input pin sense, widget control, multichannel enables, HBR, channel allocation, hotplug, LPIB snapshots, input status control, and infoframe indices.
- Function-2 codec indirect verb indices for root, output endpoint, and input endpoint paths. These map HDA verb-like codec controls and parameters such as vendor/device ID, revision, power state, subsystem ID, converter synchronization, converter controls, pin controls, descriptor data, sink info access, multichannel enablement, IEC channel-status overrides, and input channel-status registers.
- DCCG display clock offsets for PHYPLL pixel-clock resync, DP and HDMI stream DTOs, DSC/DPP clock DTOs, display/reference/SOC/symbol clock gate controls, GTC counters, DTBCLK DTOs, OTG pixel-rate controls for OTG0-3, audio DTO source/phase/module registers, vsync latch/counter registers, soft reset, and symbol-clock force-disable controls.
- DC performance monitor offsets for DCCG/DMU/MMHUBBUB/HDA perfmon instances 0, 1, 2, 4, and 5.
- DMU and power-management offsets for display power-gate domain config/status registers, DCPG interrupt status/control registers, memory/global power request registers, DMU clock and SMU interrupt controls, ZSC controls/status, deep-sleep force control, GPU timer start/read registers, display interrupt status continuations, and interrupt destination routing registers for DCCG, DMU, DCPG, MMHUBBUB, WB, DCHUB, DPP, MPC, OPP, OPTC, OTG, DIG, DDC/HPD, DIO, DCIO, HPD, AZ, AUX, DSC, and HPO.
- DMCUB offsets for region offsets/high offsets/top addresses, region 3 code-window base/top/offset registers, DMCUB interrupt enable/ack/status/type, external interrupt status/context/ack, instruction/data/undefined-address fault registers, security and memory controls, inbox/outbox mailboxes, timer triggers/window/current time, scratch registers, GPINT registers, low-power wake interrupt enable, memory power control, processor ID, control registers, and TMR AXI-space mapping.
- MMHUBBUB and MCIF writeback offsets for writeback buffer manager control/status, buffer pitch/status/address/high-address/resolution, arbitration, p-state and watermark controls, security/VMID controls, warmup config/base/region controls, memory power, clock, soft reset, DMU interface error status, and outstanding counters.
- HDA display-space windows for Azalia stream, endpoint, input-endpoint, controller, root, clock, memory-power, and audio perfmon registers.
- DCHUBBUBL SDPIF and return-path offsets for VM framebuffer/AGP/local HBM address programming, security levels for pipe/data/cursor/GPUVM paths, SDPIF request rate limiting, SDPIF memory power, return-path memory power, CRC values, DCC stats, compbuf control, and DET0-2 controls. The chunk ends at `regDCHUBBUB_DET2_CTRL_BASE_IDX`.

## Control Flow

This header has no runtime branches, calls, or sequencing. The runtime flow is supplied by AMDGPU display code:

1. DCN 3.5.1 code includes `dcn/dcn_3_5_1_offset.h` and `dcn/dcn_3_5_1_sh_mask.h`.
2. Register-list macros token-paste symbolic names into offset, shift, and mask initializers.
3. For DMUB, `dmub_srv_dcn351_regs_init()` in `display/dmub/src/dmub_dcn351.c` uses `REG_OFFSET_EXP(reg_name)` as `BASE(reg##reg_name##_BASE_IDX) + reg##reg_name`, then expands `DMUB_DCN35_REGS()` and `DMCUB_INTERNAL_REGS()` into `dmub->regs_dcn35`.
4. Runtime DMUB/DCN paths then use the initialized register tables through helper macros and functions to reset DMCUB, program code windows, set up inbox/outbox mailboxes, issue GPINTs, configure memory mappings, inspect firmware boot state, route interrupts, and access display/audio hardware.

For the Azalia indirect indices, the runtime sequencing is external to this header: consumers must program the relevant stream, endpoint, root, or codec index register and then read or write the paired data register. The index values here do not encode ordering requirements for HDA ring setup, codec verb submission, audio endpoint programming, or interrupt acknowledgement.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes hardware state surfaces:

- HDA/Azalia controller state for global capabilities, stream payload limits, wake/status/interrupt bits, CORB/RIRB DMA rings, immediate command response handling, and DMA position buffers.
- Azalia codec, stream, endpoint, input-endpoint, sink-info, CRC, and audio timing state used for HDMI/DisplayPort audio enumeration, format programming, hotplug signaling, multichannel/HBR output, LPIB snapshots, and audio diagnostics.
- Clock-generator state for pixel clocks, stream clocks, reference clocks, DSC/DPP clocks, DTBCLK, audio DTOs, GTC timebase, vsync latches, clock gating, and soft reset.
- DMU/DMCUB state for power domains, display interrupts, interrupt routing, GPU timer reads, DMCUB memory windows, mailbox pointers, scratch registers, GPINTs, firmware-visible control/status registers, fault addresses, low-power wake, and memory power controls.
- MMHUBBUB/MCIF writeback and DCHUBBUBL state for memory-hub warmup, writeback buffers, VM address apertures, security levels, request throttling, CRC capture, DCC stats, and DET/compbuf controls.

Persistence is hardware-defined. Many configuration registers survive until a modeset, block reset, power-gating event, suspend/resume transition, GPU reset, or ASIC reset. Status, interrupt, counter, CRC, mailbox pointer, and fault-address registers may be volatile, sticky, write-one-to-clear, self-clearing, or only valid while the relevant display, audio, hub, or DMCUB power/clock domain is active. This generated offset header does not carry access-type metadata; consumers must rely on the paired shift/mask definitions, register specifications, and block-specific driver code for side-effect rules.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h`, which supplies the matching field shifts and masks for these symbolic register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which directly includes this header and initializes DCN351 DMUB offsets via `dmub_srv_dcn351_regs_init()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.h`, whose `DMUB_DCN35_REGS()` and `DMUB_DCN35_FIELDS()` macro lists define the shared register-table shape used by DCN35/DCN351 DMUB code.
- DCN 3.5.1 display resource, DIO/audio, clock, hub, IRQ, writeback, and DMUB paths that consume these generated symbols directly or indirectly through AMD display register helper macros.

The strongest direct integration in this exact range is DMUB and DMCUB initialization: many `DMCUB_*`, `CC_DC_PIPE_DIS`, `MMHUBBUB_SOFT_RESET`, `DCN_VM_FB_LOCATION_BASE`, `DCN_VM_FB_OFFSET`, and `DMU_CLK_CNTL` offsets in this chunk are referenced by the shared DCN35 DMUB register table that DCN351 reuses. The Azalia and HDA families provide the register-addressing substrate for HDMI/DP audio control and diagnostics, while DCCG, DMU, MMHUBBUB, and DCHUBBUBL families support clocking, power, interrupt, memory-hub, writeback, and VM setup.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong offset or base index can compile cleanly while directing a register helper to the wrong MMIO address or segment.
- The file is generated metadata. Manual edits can diverge from AMD's authoritative register database, the matching shift/mask header, firmware expectations, and silicon documentation.
- `reg*` macros are only half of an address. Consumers must add the correct base selected by `_BASE_IDX`; using a raw `reg*` value as an absolute address is wrong for segmented DCN register spaces.
- Indirect `ix*` values require the correct index/data aperture. Reusing an endpoint index with a stream, root, input-endpoint, or function-2 data window can silently read or write unrelated hardware state.
- Repeated stream, endpoint, input-endpoint, code-window, mailbox, scratch, and perfmon families are mechanically similar. A generator error in one instance can affect only that instance, so stream 0 or endpoint 0 working does not prove streams/endpoints 1-15 or 1-7 are correct.
- Audio registers are interoperability-sensitive. Wrong HDA ring, immediate command, converter format, IEC channel-status, HBR, multichannel, sink-info, or hotplug offsets can cause silent HDMI/DP audio, channel mapping errors, bad sample-rate reporting, stuck hotplug state, or codec command timeouts.
- DMCUB offsets are boot- and firmware-critical. Wrong code-window, top-address, mailbox, GPINT, scratch, or fault/status offsets can prevent firmware boot, corrupt command queues, hide boot diagnostics, or break reset/release flows.
- Interrupt destination and status offsets are side-effect-sensitive. Misrouting or acknowledging the wrong display interrupt can cause missed events, interrupt storms, or resume-only failures.
- Memory aperture, VM, security, and writeback buffer offsets can affect isolation and data integrity. Incorrect values around `DCN_VM_*`, `DCHUBBUB_SDPIF_*_SEC_LVL`, `MCIF_WB_*_ADDR*`, DMCUB regions, or top-address registers can produce invalid DMA, display corruption, firmware faults, or security boundary violations.
- The chunk boundary is artificial. It ends in the middle of the DCHUBBUBL return-path register family, so later chunks must be merged before making whole-file claims about all DCN 3.5.1 hub, pipe, timing, link, or display-engine registers.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support with DCN 3.5.1 enabled. Missing or renamed macros should fail where `dmub_dcn351.c` expands `DMUB_DCN35_REGS()`, `DMCUB_INTERNAL_REGS()`, and related shift/mask tables.
- Mechanically verify that each `reg*` entry in this chunk has the expected `reg*_BASE_IDX` companion and that no `ix*` indirect index is accidentally paired with a base-index macro.
- Diff this range against AMD's authoritative DCN 3.5.1 generated register database and compare nearby families with `dcn_3_5_0_offset.h` where DCN35 and DCN351 are expected to share layouts.
- Boot on DCN351 hardware and verify DMUB firmware reset/release, backdoor load, code-window setup, inbox/outbox pointers, GPINT acknowledgement, scratch/status reads, fault-address diagnostics, and low-power wake behavior.
- Exercise HDMI and DisplayPort audio across plug/unplug, modeset, suspend/resume, stream enable/disable, format changes, multichannel LPCM, HBR/compressed formats, and sink changes. Watch for HDA command timeouts, bad sink descriptors, stale LPIB snapshots, CRC mismatches, missed audio enabled/disabled interrupts, and silent audio after resume.
- Validate DCCG and timing behavior across display clock changes, DP/HDMI stream-clock DTO changes, DSC/DPP clock programming, DTBCLK transitions, GTC reads, vsync latch/counter paths, and clock-gating transitions.
- Validate power and interrupt paths by checking DCPG domain transitions, DMU/SMU interrupts, display interrupt continuation registers, interrupt destination routing, memory power controls, and suspend/resume logs.
- Exercise writeback and hub paths that use MCIF/MMHUBBUB/DCHUBBUBL offsets, including writeback buffer programming, p-state/watermark changes, VM aperture setup, SDPIF security-level programming, CRC capture, DCC stats, and DET/compbuf behavior.

## Cross-Chunk Notes

This is the first chunk of `dcn_3_5_1_offset.h`. Later chunks continue from DCHUBBUBL return-path registers and cover the rest of the DCN 3.5.1 register-offset namespace. The final per-file research document should merge adjacent chunks before drawing conclusions about complete block coverage, all display pipes, all timing generators, all link encoders, or the full DCN351 register map.

### subset-b-002082: lines 2728-5263

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h lines 2728-5263

## Purpose

This chunk is generated AMD DCN 3.5.1 register-offset metadata. It contains no executable C logic; it exports symbolic `reg...` preprocessor constants for display-controller MMIO offsets plus a matching `reg..._BASE_IDX` constant for each offset. Consumers combine the numeric offset with the selected DCN base segment to initialize per-block register tables used by the AMDGPU display driver.

The requested range covers 1,194 concrete register-offset macros and 1,194 matching `_BASE_IDX` macros. Every `_BASE_IDX` value in this chunk is `2`. The chunk starts inside the tail of the DCHUBBUB memory/debug area, continues through DCHUBBUB arbitration/perfmon and display VM request registers, covers HUBP/HUBPREQ/HUBPRET/cursor register maps for instances 0 through 3, and then covers DPP pipeline register maps for complete DPP instances 0 and 1 plus the beginning of DPP instance 2. It ends inside the `CNVC_CFG2` block at `regCNVC_CFG2_COLOR_KEYER_RED`, so adjacent chunks are required for the rest of DPP2.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this range. The interface is the generated macro namespace:

- `reg<block>_<register>`: a DCN 3.5.1 register offset.
- `reg<block>_<register>_BASE_IDX`: the base-address segment selector used by `BASE(...) + reg...` register-list expansion macros.

Major macro families in this slice:

- DCHUBBUB tail and arbitration: `regDCHUBBUB_DET3_CTRL`, memory power, compbuf controls, `DCHUBBUB_ARB_*` outstanding request, saturation, QoS, DRAM-state, watermark sets `A` through `D`, self-refresh/Z8 enter/exit watermarks, UCLK/FCLK p-state change watermarks, fractional urgent bandwidth, host-VM, MALL, timeout, global timer, VTG controls, soft reset, DCFCLK, ctrl/status, FMON, and test debug registers.
- DCHUBBUB perfmon: `regDC_PERFMON6_*` counter control, current value, high/low counter, and perfmon control/status registers.
- Display VM request interface: `regDCN_VM_CONTEXT0_*` through `regDCN_VM_CONTEXT15_*` context control and page-table base/start/end address registers, plus context select, invalidate control/status, VM protection fault status and fault address registers.
- HUBP instances 0-3: `regHUBP[0-3]_DCSURF_*` surface config, address config, tiling, primary/secondary viewport start/dimension for luma and chroma, request sizing, HUBP control, clock control, VM page config, MALL config/sub-viewport/status, and debug/measurement windows.
- HUBPREQ instances 0-3: surface pitch, VMID settings, primary/secondary surface and meta-surface addresses for luma/chroma, flip control/interrupt, surface-in-use tracking, expansion mode, TTU/QoS/prefetch/vblank/flip/nominal parameters, aperture and TLB controls, cursor TTU, destination dimensions, request deadlines, DCC control, VM status, cursor VM status, page-table base, fault address, flip pinning, and hubpreq status registers.
- HUBPRET instances 0-3: return-path controls, status/debug registers, compbuf watermark controls, and read-line status.
- Cursor instances 0-3: cursor control, surface address high/low, size, settings, position, hot spot, destination offset, color words, and DM data control/sw-data registers.
- HUBP perfmon instances: `regDC_PERFMON7_*` through `regDC_PERFMON10_*` for the four HUBP pipes.
- DPP top instances 0-2: DPP control, soft reset, CRC values/control, and host-read control.
- CNVC instances 0-2: surface pixel format, format control, FP bias/scale, color-keyer registers, alpha LUT, pre-dealpha, pre-CSC matrix banks, coefficient format, pre-degamma, and pre-realpha. Instance 2 is partial in this chunk.
- DSCL instances 0-1: scaler coefficient RAM select/data, mode/tap controls, horizontal/vertical scale ratios and initial phases for luma/chroma, black color, update/autocal, overscan, OTG blanking, recout/MPC size, line-buffer format, DSCL/LB/OBUF memory power and status.
- CM instances 0-1: color-management control, post-CSC and gamut-remap matrices, bias, gamma-correction LUT/index/data/control, RAM A/B start/end/slope/base/offset/region tables, HDR multiplier, memory power/status, dealpha, coefficient format, and debug access.
- DPP perfmon instances: `regDC_PERFMON11_*` and `regDC_PERFMON12_*`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.5.1 resource, IRQ, DMUB, and hardware-block code includes this header with the matching `dcn_3_5_1_sh_mask.h`.
2. Register-list macros token-paste logical block names and instance IDs into symbols such as `regHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS`, `regCURSOR0_3_CURSOR_POSITION`, or `regCM1_CM_GAMCOR_RAMB_REGION_30_31`.
3. DCN helper macros in `dcn351_resource.c` expand those names through patterns such as `SR`, `SRI`, `SR_ARR`, and `SRI_ARR`, computing `BASE(reg..._BASE_IDX) + reg...` from `ctx->dcn_reg_offsets`.
4. The initialized register tables are later used by helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, and `REG_GET` to program display memory fetch, VM, cursor, scaling, color, perfmon, and low-power behavior.

The macros do not encode ordering. Consumers must still sequence VM setup, hubbub watermarks, p-state/self-refresh policy, flip programming, cursor updates, MALL/sub-viewport state, scaler coefficient loading, color LUT programming, clock/power gating, debug counter access, and interrupt/status handling correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It names MMIO-backed hardware state in DCN 3.5.1 display blocks:

- DCHUBBUB arbitration and memory-system state, including urgent watermarks, self-refresh/Z8/p-state thresholds, outstanding request policy, MALL behavior, timeout detection, and global timing controls.
- Display VM state for up to 16 contexts, including page-table bounds, invalidation status, context selection, and VM fault reporting.
- Per-pipe HUBP/HUBPREQ/HUBPRET state for surface addresses, meta/DCC addresses, VMID selection, tiling, viewport geometry, request sizing, flip tracking, prefetch/TTU/deadline parameters, cursor fetch, and memory-return buffering.
- Per-pipe cursor state for cursor surface address, sizing, color, position, hot spot, destination offsets, and DM data.
- Per-DPP state for pixel conversion, pre-CSC, scaler/filter, line-buffer/OBUF memory, post-CSC, gamut remap, gamma correction, HDR multiplier, color memory power, CRC, and debug/perfmon counters.

Persistence is hardware-defined. Configuration registers generally retain values until modeset reprogramming, pipe disable, power gating, suspend/resume, driver reset, or ASIC reset. Status, interrupt, fault, counter, debug-index/data, memory-power, and clear/ack-style registers may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while clocks and power domains are active. This offset header does not encode those semantics; the companion shift/mask header, hardware spec, and consumers provide field-level behavior.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h` for field shifts and masks.
- SOC/DCN base-address initialization that populates `ctx->dcn_reg_offsets[seg]`, especially segment `2`, which is used by every `_BASE_IDX` in this range.
- AMD display register helpers in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, where `BASE`, `SR`, `SRI`, `SR_ARR`, `SRI_ARR`, and related token-paste macros consume `reg...` and `reg..._BASE_IDX`.
- DMUB DCN 3.5.1 initialization in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which includes this header and initializes firmware-visible register offsets through `REG_OFFSET_EXP`.
- DCN 3.5.1 resource construction, which advertises four timing generators, four video planes, four DPP/HUBP-style pipes, four DSC blocks, five stream/audio/DDC-related resources, and 16 VMIDs; this chunk aligns with the four HUBP/HUBPREQ/HUBPRET/cursor instances and the beginning of the DPP register namespace.

The most important integration pattern is compile-time token pasting. A renamed, missing, or numerically incorrect macro usually appears as either a build failure in a register-list initializer or a runtime MMIO access to the wrong hardware register.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. These are untyped constants; a wrong `reg...` value or `_BASE_IDX` can compile while silently targeting the wrong MMIO address.
- The repeated per-pipe maps are copy-sensitive. HUBP/HUBPREQ/HUBPRET/cursor instances 0-3 and DPP instances 0-2 are structurally similar but not interchangeable; instance-specific mistakes may only reproduce on a particular pipe or multi-display layout.
- The chunk boundaries are artificial. The first lines are only the tail of a DCHUBBUB block, and the last lines stop inside `CNVC_CFG2`; final file-level analysis must merge adjacent chunks before making complete claims about DCHUBBUB or DPP2 coverage.
- VM and address registers are high impact. Incorrect page-table bounds, VM context selection, surface/meta addresses, VMID settings, aperture/TLB controls, or fault registers can cause GPU faults, blank scanout, stale frames, or hard-to-debug memory access errors.
- Watermark, TTU, prefetch, p-state, self-refresh, and MALL offsets affect timing and power management. Bad values can present as underflow, flicker, p-state switching failures, high power, or suspend/resume instability.
- Flip and cursor registers are sequencing-sensitive. Wrong flip control/status/interrupt, surface-in-use, cursor address, hotspot, or position offsets can break page flips, cursor movement, cursor format, or atomic commit completion.
- Scaler and color-management offsets are format-sensitive. Incorrect DSCL, CNVC, CM, gamma RAM, CSC, gamut, HDR, and coefficient registers can cause wrong colors, corrupted scaling, bad HDR behavior, or failures limited to specific pixel formats.
- Memory power and debug/perfmon registers may require clocks or ungated blocks. Accessing them while a block is powered down can produce invalid reads, ignored writes, timeouts, or misleading diagnostics.

## Test Signals

Useful validation is mostly generated-header consistency plus DCN 3.5.1 hardware behavior:

- Build AMDGPU/DC with DCN 3.5.1 enabled; resource, IRQ, DMUB, HUBP, DPP, VMID, scaler, and color register-table construction should fail if required macros are missing or renamed.
- Mechanically verify that every non-`_BASE_IDX` `reg...` macro in lines 2728-5263 has exactly one matching `_BASE_IDX` macro and that all base-index values remain `2`.
- Diff this chunk against AMD's authoritative DCN 3.5.1 register database and related generated headers such as `dcn_3_5_0_offset.h` or neighboring DCN 3.x versions where compatibility is expected.
- Exercise four-pipe display configurations: single display, multi-display, mirrored/extended layouts, pipe changes, high-resolution modes, suspend/resume, hotplug, and atomic page flips.
- Validate VM and memory fetch paths with framebuffer formats that use luma/chroma planes, DCC metadata, primary/secondary addresses, cursor surfaces, and MALL/sub-viewport behavior.
- Stress watermark and power behavior with p-state changes, Z8/self-refresh residency, memory-clock transitions, underflow detection, and bandwidth-heavy modes.
- Test cursor programming across all active pipes, including movement, hotspot changes, color formats, size changes, and enable/disable transitions.
- Validate DPP behavior for scaling, overscan, chroma scaling, line-buffer/OBUF operation, color keying, pre/post CSC, gamut remap, gamma correction, HDR multiplier, degamma/re-alpha/de-alpha, and CRC capture.
- Watch kernel logs, debugfs counters, perfmon values, VM fault registers, underflow reports, flip completion, cursor glitches, color mismatches, and resume failures for signs of incorrect offsets.

## Cross-Chunk Notes

Previous chunks own the beginning of DCHUBBUB and earlier DCN 3.5.1 register-offset definitions. Later chunks continue `CNVC_CFG2` after `regCNVC_CFG2_COLOR_KEYER_RED`, then cover the rest of DPP2 and later DCN 3.5.1 blocks. The final per-file document should reconcile adjacent chunks before describing the complete `dcn_3_5_1_offset.h` register map.

### subset-b-002083: lines 5264-7875

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h lines 5264-7875

## Scope

This chunk is a generated AMD DCN 3.5.1 register-offset header slice. It contains preprocessor constants only: 2,377 `#define` entries, of which 1,189 are register offsets and 1,188 are matching `_BASE_IDX` constants inside the requested line range. There are no C functions, structs, enums, variables, branches, allocations, locks, direct MMIO reads/writes, or filesystem persistence paths in this chunk.

The chunk begins in the middle of `dce_dc_dpp2_dispdec_cnvc_cfg_dispdec`: lines 5242-5263 define the first CNVC CFG2 offsets, while this chunk starts at `regCNVC_CFG2_COLOR_KEYER_GREEN`. It also ends in the middle of `dce_dc_dio_dp_aux4_dispdec`: the final line in scope is `regDP_AUX4_AUX_DPHY_TX_CONTROL`, and the matching `_BASE_IDX` plus the remaining AUX4 registers continue after line 7875. Final file-level research should merge neighboring chunks before making whole-block completeness claims for CNVC CFG2 or DP AUX4.

Although this repository path is under a local `ceph-client` source mirror, the file itself is AMDGPU Display Core hardware metadata for the DCN 3.5.1 display engine.

## Purpose And Hardware Surface

`dcn_3_5_1_offset.h` supplies symbolic MMIO register offsets for the DCN 3.5.1 ASIC register map. Runtime display code combines each `reg...` value with `ctx->dcn_reg_offsets[reg..._BASE_IDX]` to produce final MMIO addresses. The paired `dcn_3_5_1_sh_mask.h` file supplies the matching field shifts and masks.

This range covers the second half of the display pipe frontend and a large part of the backend/link timing surface:

- Tail of DPP2 converter configuration, then DPP2 cursor, DSCL, color-management, and DPP perfmon registers.
- Full DPP3 top, converter configuration, cursor, DSCL, color-management, and DPP perfmon registers.
- OPP instances 0-3, including FMT output formatting, DPG pattern generation, OPP buffer control, pipe control, pipe CRC, top-level OPP control, DSCRM forward configuration, and OPP perfmon.
- OPTC/ODM/OTG instances 0-3, including timing generator totals/blanking/sync, vertical interrupt controls, global swap/sync, CRC, DRR/VTOTAL min/max, stereo, memory power, test/debug, global swap lock source selection, and OPTC perfmon.
- DIO registers for I2C/DDC, DIO miscellaneous link controls/status, HPD0-4 hotplug blocks, DIO perfmon, and DP AUX0-4 control/status/PHY/sync registers.

The numeric offsets in this chunk are not generic register IDs; they are part of the ASIC ABI. Incorrect values compile cleanly if names still exist, but they drive the display driver to the wrong hardware address at runtime.

## Important Definitions

The exported interface is a mechanically generated macro namespace:

- `reg<NAME>`: register offset within a generated base segment.
- `reg<NAME>_BASE_IDX`: index into `ctx->dcn_reg_offsets[]`, used by DCN351 resource and IRQ code to add the correct base address.

The consuming macros in `dcn351_resource.c` and `irq_service_dcn351.c` build final offsets with token pasting. Examples include `SR(reg_name)`, `SRI(reg_name, block, id)`, `SRI_ARR(reg_name, block, id)`, and `SR_ARR(reg_name, id)`, all of which evaluate to:

```c
BASE(reg..._BASE_IDX) + reg...
```

Important register families in this chunk:

- `CNVC_CFG2`, `CNVC_CUR2`, `DSCL2`, `CM2`: DPP2 color conversion, cursor color, scaling/filtering/line-buffer controls, post-CSC/gamut/gamma/degamma/shaper/3D LUT/HDR multiplier/debug controls, and DPP2 perfmon 13.
- `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, `CM3`: the same DPP frontend surface for pipe 3, with DPP3 perfmon 14.
- `FMT0-3`: output formatter clamp/dynamic expansion/dither/bit-depth/random-seed/alpha/420/422 format-control registers.
- `DPG0-3`: display pattern generator color components, ramps, bit-depth, stereo, and status registers.
- `OPPBUF0-3`, `OPP_PIPE0-3`, `OPP_PIPE_CRC0-3`: OPP buffer controls, pipe control, and output CRC control/window/result registers.
- `OPP_TOP`, `DSCRM0-3`, `DC_PERFMON16`: top-level OPP clock/ABM controls, DSC forward configuration per OPP, and OPP perf counters.
- `ODM0-3`: OPTC input/global control, data source selection, memory control/status, and spare registers.
- `OTG0-3`: 115 registers per timing generator instance, covering timing totals, active/display regions, blanking, sync, controls, stereoscopy, vertical interrupts, global sync/swap lock, CRC, DRR timing, underrun, double-buffer status, memory power, and debug.
- `GSL_SOURCE_SELECT`, `GSL_GROUP_SELECT`, `GSL_CONTROL`, `OPTC_DATA_SOURCE_SELECT`, `OPTC_INPUT_CLOCK_CONTROL`, `OPTC_INPUT_GLOBAL_CONTROL`, `OPTC_MISC_SPARE_REGISTER`: OPTC-wide misc/global-swap-lock selection and input control.
- `DC_PERFMON17`, `DC_PERFMON18`: OPTC and DIO display perfmon blocks.
- `DC_I2C_*`: DIO DDC/I2C software control, arbitration, transaction setup, speed, setup/hold timing, data, DDC setup, EDID detection, reset, and interrupt registers.
- `DIO_*` and `DIO_LINK[A-F]_CNTL`: DIO status, stream encoder count, memory power, stream encoder clock controls, power control, symbol clock controls, and per-link controls.
- `HPD0-4`: hotplug interrupt status/control, HPD control, filter, and toggle-filter registers.
- `DP_AUX0-4`: DisplayPort AUX control, software control/status/data, arbitration, interrupt control, LS status/data, PHY TX/RX controls/status, GTC sync controls/status, and PHY wake controls. AUX4 is partial in this chunk.

## Address-Block Inventory

The generated block comments in this range identify the following address blocks and line spans. Register counts exclude `_BASE_IDX` lines.

| Lines | Address block | Base | Registers | Notes |
| --- | --- | --- | ---: | --- |
| 5264-5303 | `dce_dc_dpp2_dispdec_cnvc_cfg_dispdec` | `0xb58` | 20 in-scope | Partial leading block; starts at green/blue color-keyer and pre-CSC tail. |
| 5308-5314 | `dce_dc_dpp2_dispdec_cnvc_cur_dispdec` | `0xb58` | 4 | Cursor control and colors for DPP2. |
| 5320-5386 | `dce_dc_dpp2_dispdec_dscl_dispdec` | `0xb58` | 34 | DPP2 scaler coefficients, ratios, recout/MPC sizing, line buffer, and memory power. |
| 5392-5610 | `dce_dc_dpp2_dispdec_cm_dispdec` | `0xb58` | 110 | DPP2 color management, LUTs, HDR multiplier, and debug. |
| 5616-5632 | `dce_dc_dpp2_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` | `0x43e8` | 9 | DPP2 perfmon 13. |
| 5638-6022 | `dce_dc_dpp3_dispdec_*` | `0x1104` | 185 | Full DPP3 top, CNVC, DSCL, and CM coverage. |
| 6028-6044 | `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` | `0x4994` | 9 | DPP3 perfmon 14. |
| 6050-6371 | `dce_dc_opp_*0-3_dispdec` | `0x0`, `0x168`, `0x2d0`, `0x438` | 124 | Repeated FMT, DPG, OPPBUF, OPP pipe, and pipe CRC blocks for four OPP instances. |
| 6377-6403 | OPP top and `DSCRM0-3` | mixed | 6 | OPP top controls and DSC forward selection. |
| 6409-6425 | `dce_dc_opp_opp_dcperfmon_dc_perfmon_dispdec` | `0x6af8` | 9 | OPP perfmon 16. |
| 6431-6505 | `dce_dc_optc_odm0-3_dispdec` | `0x0`..`0xc0` | 32 | ODM input/source/memory controls. |
| 6511-7441 | `dce_dc_optc_otg0-3_dispdec` | `0x0`, `0x200`, `0x400`, `0x600` | 460 | Four complete OTG timing-generator instances. |
| 7447-7459 | `dce_dc_optc_optc_misc_dispdec` | `0x0` | 7 | GSL and OPTC-wide input controls. |
| 7465-7481 | `dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec` | `0x79a8` | 9 | OPTC perfmon 17. |
| 7487-7591 | `dce_dc_dio_dout_i2c_dispdec` and `dce_dc_dio_dio_misc_dispdec` | `0x0` | 51 | I2C/DDC and DIO link/control/status registers. |
| 7597-7661 | `dce_dc_dio_hpd0-4_dispdec` | `0x0`..`0x80` | 25 | Five HPD interrupt/control/filter blocks. |
| 7667-7683 | `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec` | `0x7d10` | 9 | DIO perfmon 18. |
| 7689-7875 | `dce_dc_dio_dp_aux0-4_dispdec` | `0x0`..`0x1c0` | 86 in-scope | AUX0-3 complete; AUX4 partial at the end. |

## Control Flow And Runtime Behavior

This header has no runtime control flow. Behavior appears only after the generated constants are included by DCN351 code and expanded into register tables:

1. `dcn351_resource.c` includes `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`, defines `BASE(seg)` as `ctx->dcn_reg_offsets[seg]`, and expands register-list macros into typed structures.
2. `dpp_regs_init(id)` uses `DPP_REG_LIST_DCN35_RI(id)` to populate `struct dcn3_dpp_registers dpp_regs[4]`. The DPP2 and DPP3 offsets in this chunk feed pipe instances 2 and 3 for color conversion, scaling, color management, and diagnostics.
3. `opp_regs_init(id)` uses `OPP_REG_LIST_DCN35_RI(id)` to populate `struct dcn35_opp_registers opp_regs[4]` from the FMT/DPG/OPPBUF/OPP pipe/CRC definitions in this chunk.
4. `optc_regs_init(id)` uses `OPTC_COMMON_REG_LIST_DCN3_5_RI(id)` to populate `struct dcn_optc_registers optc_regs[4]` from the ODM/OTG/OPTC misc definitions in this chunk.
5. `aux_regs_init(id)`, `hpd_regs_init(id)`, and `aux_engine_regs_init(id)` build link/AUX/HPD register structures for five physical link-side instances. The AUX and HPD constants in this chunk are the address side of DDC, DP AUX, HPD interrupt, and link training support.
6. `irq_service_dcn351.c` uses the same `BASE(reg..._BASE_IDX) + reg...` pattern for HPD, HPD RX, VUPDATE, VBLANK, and VLINE0 interrupt source table entries. The `HPD0-4` and `OTG0-3` registers in this range are therefore part of interrupt enable/ack/status mapping.
7. Runtime display code calls register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_UPDATE`, and `REG_WAIT` through those typed structures. The offsets here choose the target register; the paired shift/mask header chooses the field inside that register.

The sequencing rules are not encoded here. Higher-level DCN code must still order plane setup, scaler programming, color pipeline programming, timing generator enable, output formatter enable, link/AUX transactions, interrupt acknowledgement, and power transitions correctly.

## State And Persistence Behavior

This chunk stores no software state. It describes hardware register state that lives in DCN 3.5.1 display, timing, output, and link blocks.

Programmed hardware state represented by these offsets includes:

- DPP converter and color-management state: color keying, pre/post CSC matrices, degamma/gamma/shaper control, 3D LUT access, gamut remap, HDR multiplier, alpha/dealpha/realpha, and cursor colors.
- DPP scaler state: coefficient RAM access, taps, scale ratios, filter initial conditions, overscan, recout/MPC sizing, line-buffer format and memory control.
- OPP output state: clamp, bit-depth expansion, dithering seeds and control, output format controls, display pattern generator values, pipe controls, OPP buffer settings, ABM control, and pipe CRC windows/results.
- OPTC/OTG timing state: horizontal/vertical totals, blanking, sync widths, active/display areas, control/status, stereo, CRC windows/results, dynamic refresh timing, global swap/sync settings, vertical interrupt position/ack/enable, and memory power controls.
- DIO link-side state: I2C/DDC transaction parameters and data, link clock/control registers, HPD filters and interrupt state, DP AUX transaction state, AUX PHY controls/status, and AUX GTC synchronization.
- Perfmon counter state for DPP, OPP, OPTC, and DIO instrumentation blocks.

Persistence is hardware-defined. Configuration generally survives until the next modeset, plane update, link retraining, hotplug event, power-gating transition, suspend/resume, driver reset, or ASIC reset. Status, interrupt, CRC, perfmon, busy, done, and clear registers are volatile and may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the relevant clock and power domain is active. The generated offset header does not encode any of those access semantics.

## Dependencies And Integration Points

This chunk depends on name and numeric consistency across the generated DCN 3.5.1 register header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h` must provide matching field names, shifts, and masks for the registers referenced here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c` consumes these offsets for DCN351 resource construction. Relevant local initializers include `dpp_regs_init`, `opp_regs_init`, `optc_regs_init`, `aux_regs_init`, `hpd_regs_init`, and `aux_engine_regs_init`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c` consumes HPD and OTG offsets for IRQ source enable/ack/status tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c` includes the same offset header for DMUB register initialization, although the specific lines in this chunk are primarily display pipe/link register families rather than the core DMCUB mailbox register set.
- Shared block headers such as `dcn35_dpp.h`, `dcn35_opp.h`, `dcn35_optc.h`, `dce_aux.h`, `dce_i2c.h`, and DIO/link encoder headers define the register-list and field-list macros that token-paste these generated names.

The base-index pattern is a key integration constraint. Most constants in this chunk have `_BASE_IDX` value `2`, but some address-block comments expose local base offsets such as `0xb58`, `0x1104`, `0x6af8`, or `0x79a8`. Runtime code must use both pieces: the generated offset and the base segment selected by `_BASE_IDX`.

## Risks And Maintenance Notes

- Generated-offset drift is the main risk. A wrong numeric offset can target a valid but unrelated MMIO register, producing display corruption, missed interrupts, stuck link transactions, or power-management failures without a compile-time error.
- The chunk has partial block boundaries. `CNVC_CFG2` starts before this range and `DP_AUX4` continues after it; any completeness audit needs adjacent chunks.
- Repeated instance families can hide one-instance errors. DPP2/DPP3, OPP0-3, ODM0-3, OTG0-3, HPD0-4, and DP_AUX0-4 should follow intentional instance strides. A single bad offset can affect only one pipe or connector.
- DPP color pipeline registers are user-visible and precision-sensitive. Bad CSC, LUT, degamma/gamma, HDR multiplier, or alpha offsets can cause incorrect color, banding, broken HDR/SDR conversion, cursor color issues, or failures only on specific pixel formats.
- DSCL and line-buffer offsets are timing-sensitive. Incorrect scale ratio, filter init, recout/MPC size, or line-buffer memory offsets can cause black screens, underflow, corrupted scaling, or resume-only failures.
- OPP/FMT dither and format offsets affect sink-visible output. Errors can produce wrong bit depth, broken YCbCr 4:2:0/4:2:2 output, CRC mismatch, or display artifacts that may not appear on simple RGB modes.
- OTG registers include interrupt, timing, global sync, DRR, and swap-lock controls. Bad offsets can cause vblank/vline interrupt loss, page-flip timing bugs, tearing, variable-refresh issues, stereo issues, or blanking/sync misprogramming.
- HPD and AUX registers are hotplug/link-training critical. Wrong HPD status/ack/control or AUX SW data/status/PHY offsets can cause missed hotplug, interrupt storms, DP link-training timeouts, failed DPCD/EDID reads, or unreliable wake from low power.
- Perfmon and CRC registers are diagnostics but still side-effect-sensitive. Incorrect counter-control or CRC-control offsets can make validation misleading or disturb active display diagnostics.
- The generated names are untyped macros. Renaming or deleting a macro often fails at build time, but changing the number behind a stable name may only fail on actual DCN351 hardware.

## Test Signals

Useful validation should combine generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU Display Core with DCN351 enabled and confirm `dcn351_resource.c`, `irq_service_dcn351.c`, and `dmub_dcn351.c` compile against `dcn_3_5_1_offset.h` and the paired shift/mask header.
- Mechanically check every in-scope register has a matching `_BASE_IDX` where the pair lies inside the chunk; allow the known trailing boundary exception for `regDP_AUX4_AUX_DPHY_TX_CONTROL`, whose `_BASE_IDX` is outside the requested range.
- Diff this range against AMD's authoritative generated register database and nearby generated headers such as `dcn_3_5_0_offset.h` and `dcn_3_6_0_offset.h` where register layouts are expected to be compatible.
- Verify repeated-instance strides and register counts for DPP2/DPP3, OPP0-3, ODM0-3, OTG0-3, HPD0-4, and DP_AUX0-4; investigate any non-uniformity that is not documented by the hardware spec.
- Exercise four-pipe display modes on DCN351 hardware, including plane scaling, cursor enable, color transformations, HDR metadata/color pipeline changes, degamma/gamma LUT updates, 3D LUT access, and mixed pixel formats.
- Exercise OPP/FMT output paths across RGB and YCbCr modes, 6/8/10/12 bpc, dithering, 4:2:0 and 4:2:2 output, CRC capture, pattern generator output, and ABM interaction.
- Exercise OTG timing paths with modeset, blank/unblank, page flip, vblank/vline interrupts, variable refresh/DRR, stereo where available, global swap lock, suspend/resume, and multi-display sync scenarios.
- Exercise DIO link-side paths: HPD plug/unplug and HPD RX, DP AUX DPCD reads/writes, EDID over DDC/I2C, link training, low-power wake, and connector combinations that use AUX/HPD instances 0 through 4.
- Monitor kernel logs, debugfs diagnostics, vblank counters, page-flip completion, AUX timeout counters, HPD storm handling, CRC/perfmon output, underflow reporting, and resume/hotplug recovery after display power transitions.

## Chunk-Specific Summary

Lines 5264-7875 define DCN 3.5.1 register offsets for DPP2 tail registers, full DPP3 frontend registers, four OPP backend instances, four OPTC/OTG timing instances, and a large DIO/HPD/AUX link-control range. The content is generated register ABI rather than executable logic. Correctness depends on exact offset/base-index values, consistent repeated-instance layout, synchronization with `dcn_3_5_1_sh_mask.h`, and validation on real DCN351 display/link hardware across color, scaling, timing, output-format, hotplug, AUX/DDC, interrupt, CRC, perfmon, and power-management scenarios.

### subset-b-002084: lines 7876-10402

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h lines 7876-10402

## Purpose

This chunk is a generated AMD DCN 3.5.1 register-offset header slice. It has no executable C logic; it publishes preprocessor constants that name memory-mapped display-register offsets and their register-base index for DCN351 hardware. Driver code combines these offsets with `dcn_3_5_1_sh_mask.h` field definitions and AMD display register-helper macros to build typed register tables for DIO, stream encoders, link encoders, IRQ service, DMUB service, GPIO/DDC/HPD handling, and panel power sequencing.

The requested range starts in the tail of the `DP_AUX4` AUX-channel register group, then covers the main repeated DIO instance layout for `DIG0` through `DIG4`, common DCIO and GPIO/link-control registers, UNIPHY reserved macro-control ranges for instances 1-4, and the first registers of `PWRSEQ0`. Within lines 7876-10402 there are 2,394 `#define` entries: 1,197 register-offset macros and 1,197 matching `_BASE_IDX` macros. Every `_BASE_IDX` value in this chunk is `2`, meaning these symbols are interpreted through DCN351 base segment index 2 by consumers that compute `BASE(reg..._BASE_IDX) + reg...`.

Although the repository path is under a local `ceph-client` tree, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The exported interface is the generated macro namespace:

- `reg<NAME>`: a DCN351 register offset within a hardware address block.
- `reg<NAME>_BASE_IDX`: the base-address segment selector used by AMD register helpers when producing the final MMIO address.

The major register families in this range are:

- `regDP_AUX4_*` tail registers at lines 7876-7894: AUX4 DPHY TX/RX control and status, GTC sync control/status/error registers, and AUX PHY wake control. The chunk starts mid-family, so earlier AUX4 software-control, arbitration, interrupt, and data registers are outside this range.
- `regVPG0_*` through `regVPG4_*`: five Video Packet Generator blocks. Each instance exposes generic packet access/data, generic-stream packet frame/immediate update controls, generic status, memory power, ISRC access/data, and MPEG info registers.
- `regAFMT0_*` through `regAFMT4_*`: five audio formatter blocks. Each instance includes ACP, VBI/audio-packet controls, HDMI/DP audio info, IEC 60958 channel status registers, CRC controls/results, ramp controls, infoframe control, interrupt status, audio source control, and memory-power control.
- `regDME0_*` through `regDME4_*`: small Data Mapping Engine groups with `DME_CONTROL` and `DME_MEMORY_CONTROL`.
- `regDIG0_*` through `regDIG4_*`: five digital front-end/back-end and HDMI/TMDS encoder blocks. Each repeated group includes FE clock/enable/control, output CRC/test-pattern/FIFO controls, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet/DB controls, AFMT coupling, BE controls, TMDS control/pattern/DC-balancer registers, and `DIG_VERSION`.
- `regDP0_*` through `regDP4_*`: five DisplayPort link/stream encoder groups. Each instance covers link control, pixel format, MSA colorimetry/config/misc/timing parameters, video stream control, DPHY internal/training/symbol/scrambler/CRC/fast-training controls, secondary-data packet/audio timestamp controls, MST/MSE slot allocation and status, MSO/DSC controls, DP DB control, metadata transmission, ALPM and AUX-less ALPM controls, GSP controls, and stream/link symbol count status/control.
- Common `regDC_*`, `regDCIO_*`, `regUNIPHYA_*` through `regUNIPHYE_*`, and `regINTERCEPT_STATE` registers: generic DC scratch/control registers, DCIO clock/reference clock and write-command delay, link and channel crossbar controls, DCIO pattern generator, global swaplock/genlock pad control, soft reset, and global DCIO spare/pinstrap state.
- GPIO, DDC, HPD, AUX, and pad-power registers: `DC_GPIO_GENERIC`, `DDC1` through `DDC5`, `DDCVGA`, `GENLK`, `HPD`, drive-strength, power-sequence GPIO enables, pad-strength, AUX PHY control, TX impedance, TX12/RX/pull-up/AUX controls, and `AUXI2C_PAD_ALL_PWR_OK`.
- `regDCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57`, repeated for UNIPHY1, UNIPHY2, UNIPHY3, and UNIPHY4. `dce_dc_dcio_dcio_uniphy0_dispdec` is present as an address-block marker in this chunk but has no defines in this slice.
- The opening of `regPWRSEQ0_*`: `DC_GPIO_PWRSEQ_EN`, `DC_GPIO_PWRSEQ_CTRL`, `DC_GPIO_PWRSEQ_MASK`, `DC_GPIO_PWRSEQ_A_Y`, and `PANEL_PWRSEQ_CNTL`. The rest of the panel power-sequencer block continues after this chunk.

The repeated DIO register layout is especially important: `DIGn`, `DPn`, `VPGn`, `AFMTn`, and `DMEn` advance together for instances 0-4. DCN351 resource code reports five stream encoders and five digital link encoders, and it initializes arrays such as `stream_enc_regs[5]`, `link_enc_aux_regs[5]`, `link_enc_hpd_regs[5]`, and `link_enc_regs[5]` from these generated register names.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this header and consumes its constants:

1. DCN351-specific modules include `dcn_3_5_1_offset.h` together with `dcn_3_5_1_sh_mask.h`.
2. Register-list macros token-paste symbolic names into offset, shift, and mask initializers.
3. Constructors build hardware-block register tables. In `dcn351_resource.c`, this includes DIO construction, stream encoder creation, link encoder creation, VPG/AFMT sub-block creation, and resource-pool wiring for five DIO/link instances. In `irq_service_dcn351.c`, interrupt-source tables are initialized from generated offsets and fields. In `dmub_dcn351.c`, `dmub_srv_dcn351_regs_init()` computes DMUB register offsets as `BASE(reg..._BASE_IDX) + reg...`.
4. Runtime helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use those tables to touch the actual MMIO registers during modeset, link training, audio setup, hotplug handling, AUX/DDC transactions, power sequencing, interrupt handling, suspend/resume, and DMUB communication.

The offsets do not encode ordering. Consumers still must sequence hardware operations correctly: enable and reset DIG/DP blocks at the right time, program HDMI/DP packets after stream format selection, perform DP link training before stream enable, synchronize secondary data packets with active streams, manage HPD/DDC/AUX pads around hotplug and low-power states, and follow panel power/backlight timing rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It names hardware state held in DCN351 display registers:

- DIG/HDMI/TMDS state: encoder enablement, clocking, test patterns, FIFO controls, metadata packets, generic packets, audio clock regeneration, TMDS control characters, output CRC, and back-end state.
- DP link and stream state: link configuration, pixel format, main-stream attributes, video timing, link framing, training pattern and DPHY controls, scrambler/CRC/test controls, MST/MSE allocation, DSC/MSO, secondary-data/audio packets, ALPM, GSP, and symbol counters.
- VPG/AFMT/DME state: packet payload staging, generic/ISRC/MPEG info, audio infoframes, IEC 60958 channel status, CRC diagnostics, ramp controls, audio source selection, and memory-power controls.
- DCIO/link state: display clock/reference controls, UNIPHY channel crossbars, pattern generator, genlock/swaplock pads, soft-reset state, pinstraps, GPIO/HPD/DDC/AUX pad controls, pad drive strength, AUX power readiness, and reserved UNIPHY macro-control space.
- Power-sequencer state at the chunk boundary: GPIO power-sequencer enable/control/mask/data and the first panel power-sequencer control register.

Persistence is hardware-defined. Programmed values may survive until a modeset, stream/link teardown, power-gating event, panel power sequence, suspend/resume, GPU reset, or ASIC reset. Status and interrupt-related registers may be read-only, sticky, write-one-to-clear, self-clearing, or only valid while the relevant clock/power domain is enabled. The generated offset header does not express access semantics, reset values, side effects, or required delays; those come from the hardware spec and the consuming DCN/DCE code.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN351 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h`, which supplies field shifts and masks for the registers named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which includes the offset and shift/mask headers and constructs DCN351 DIO, stream encoder, link encoder, VPG, AFMT, HPO, IRQ, and resource-pool objects. The chunk's five `DIGn`/`DPn`/`VPGn`/`AFMTn`/`DMEn` layouts align with `res_cap_dcn351.num_stream_encoder = 5` and `num_dig_link_enc = 5`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`, which includes these generated headers and initializes DCN351 interrupt-source register metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, where `dmub_srv_dcn351_regs_init()` computes DMUB-visible offsets from `BASE(reg..._BASE_IDX) + reg...`.
- DCN35/DCE shared encoder implementations such as `dcn35_dio_stream_encoder`, `dcn35_dio_link_encoder`, `dcn31_hpo_dp_stream_encoder`, `dcn31_hpo_dp_link_encoder`, and inherited DCE/DIO helpers that expect the generated register tables to match their local register-list macros.
- GPIO, I2C/DDC, AUX, HPD, panel power, link training, audio, MST, DSC/MSO, ALPM, and DMUB paths that indirectly rely on these constants through register tables rather than manually spelling offsets.

The source-tree alignment is important: this is a DCN351 display-register chunk. The final per-file synthesis should merge it with adjacent chunks before making whole-file claims about all offset macros in `dcn_3_5_1_offset.h`.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong offset or base index can compile successfully while reads and writes target the wrong MMIO register.
- All base indices in this chunk are `2`. If a generator or manual edit changes one `_BASE_IDX`, `BASE(reg..._BASE_IDX) + reg...` computations could silently move only one register family to a different MMIO segment.
- The chunk begins and ends at artificial boundaries. It starts after earlier `DP_AUX4` registers and stops at `PWRSEQ0_PANEL_PWRSEQ_CNTL`; callers need adjacent chunks to understand the full AUX4 and panel power-sequencer register groups.
- Repeated instance groups are easy to misalign. A single bad `DIG3`, `DP4`, `AFMT2`, or `VPG1` offset can break one physical connector/encoder path while other ports still work, making failures appear board- or connector-specific.
- HDMI/DP packet registers are timing-sensitive. Incorrect VPG, AFMT, HDMI generic packet, infoframe, audio, ACR, or metadata offsets can lead to missing HDR/VRR/audio metadata, silent HDMI/DP audio, wrong sample-rate reporting, or receiver-specific interoperability failures.
- DP link registers are link-training-sensitive. Bad DPHY, scrambler, CRC, fast-training, MSA, MST/MSE, ALPM, DSC, or symbol-count offsets can cause failed link training, flicker, MST bandwidth allocation bugs, DSC bring-up failures, or low-power display wake issues.
- GPIO, HPD, DDC, AUX, and pad-strength registers interact with physical pins. Wrong offsets can cause missed hotplug events, failed EDID reads, AUX/I2C timeouts, excessive pad drive, or improper pad power handling.
- UNIPHY reserved macro-control offsets are especially risky because names do not describe semantics. They should be treated as generated silicon metadata and not repurposed without authoritative documentation.
- Panel power-sequencer registers can affect display panel safety and resume behavior. Incorrect `PWRSEQ0` offsets or ordering can produce blank internal panels, backlight glitches, or resume-only failures.

## Test Signals

Useful validation combines static generated-header checks with DCN351 hardware coverage:

- Build AMDGPU display support with DCN351 enabled. Missing or renamed macros should fail where `dcn351_resource.c`, `irq_service_dcn351.c`, and `dmub_dcn351.c` instantiate register tables.
- Mechanically verify this range has 1,197 register-offset macros and 1,197 matching `_BASE_IDX` macros, and that every `_BASE_IDX` value is `2`.
- Diff this chunk against AMD's authoritative DCN 3.5.1 register database and nearby generated DCN headers. Pay special attention to repeated `DIG0-4`, `DP0-4`, `VPG0-4`, `AFMT0-4`, `DME0-4`, and `DCIO_UNIPHY1-4` instance strides.
- Exercise all five physical DIO/link instances where hardware exposes them: HDMI, DisplayPort SST, DisplayPort MST, USB-C/DP alt-mode paths, hotplug/unplug, EDID reads, link retraining, suspend/resume, and GPU reset recovery.
- Validate HDMI/DP audio and metadata: ACR programming, infoframes, generic packets, HDR metadata, ISRC/MPEG packets, audio enable/disable, sample-rate changes, multichannel formats, and receiver compatibility.
- Exercise DP-specific features covered here: training patterns, fast training, DPHY CRC, MST MSE allocation/status, DSC enablement, MSO controls, ALPM/AUX-less ALPM, GSP controls, and symbol-count status reporting.
- Watch kernel logs and display diagnostics for AUX/DDC timeouts, HPD storms or missed HPD events, DMUB register access failures, IRQ misrouting, link-training failures, CRC mismatches, stuck secondary-data packets, panel power/backlight sequencing issues, and connector-specific failures that map to one repeated register instance.

## Cross-Chunk Notes

This is a middle chunk of `dcn_3_5_1_offset.h`. Earlier chunks define preceding AUX, audio, GPIO, and other display blocks. Later chunks continue `PWRSEQ0` and additional DCN351 offset families. The merge/reconciliation lane should combine this document with neighboring chunk research before producing the final per-file report.

### subset-b-002085: lines 10403-12994

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h lines 10403-12994

## Scope

This chunk is a generated AMD DCN 3.5.1 register-offset header slice. It contains C preprocessor constants only: `reg...` symbols for hardware register offsets and paired `reg..._BASE_IDX` symbols for selecting the register base segment used by the AMDGPU display register-access helpers. There are no functions, structs, enums, branches, loops, allocations, locks, syscalls, or software persistence paths in this range.

The requested range covers 2,592 source lines and 2,376 `#define reg...` lines. It starts inside the `dce_dc_pwrseq0_dispdec_pwrseq_dispdec` block at `regPWRSEQ0_PANEL_PWRSEQ_CNTL_BASE_IDX`, after the actual `regPWRSEQ0_PANEL_PWRSEQ_CNTL` offset was defined on the previous line. It then covers PWRSEQ1, four DSC/DSCC instances, DSC perfmon blocks 19 through 22, display writeback, DCHVM, HPO DisplayPort stream/link/PHY encoder blocks, four MPCC compositor blocks, four MPCC output-gamma blocks, and the first registers of MPC global config. It ends at `regMPC_PERFMON_EVENT_CTRL_BASE_IDX`, before the remaining MPC config registers in the next chunk.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU Display Core hardware metadata for DCN 3.5.1 display hardware, not Ceph filesystem code.

## Purpose

The purpose of this range is to map DCN 3.5.1 display-engine register names to numeric register offsets and register-base indices. Runtime AMDGPU display code uses these generated constants, together with matching shift/mask definitions from `dcn_3_5_1_sh_mask.h`, to build ASIC-specific register tables for low-level MMIO programming.

The hardware surfaces represented here include:

- Panel power sequencing and backlight PWM registers for PWRSEQ0/PWRSEQ1.
- Display Stream Compression control, PPS, status, memory power, error-statistic, rate-buffer, and perfmon registers for DSC instances 0 through 3.
- Display writeback top-level, flow-composition, CRC, overflow, reset, perfmon, gamut-remap, and output-gamma registers.
- Display Core host virtual memory and RIOMMU control/status registers.
- HPO DisplayPort stream encoders 0 through 3, APG audio-packet generators, DME blocks, VPG generic-packet/ISRC/MPEG packet blocks, 32-symbol stream encoders, link encoders for links 0 and 1, and 32-symbol DP PHY blocks 0 and 1.
- MPC MPCC compositor registers for MPCC0 through MPCC3.
- Per-MPCC output gamma and gamut-remap register windows for MPCC_OGAM0 through MPCC_OGAM3.
- The beginning of MPC global clock/reset/CRC/perfmon event control.

The constants are generated data, but they are a hardware ABI for the driver. A wrong offset or base index can compile cleanly and still make the driver program the wrong display engine, read stale status, reset the wrong block, misconfigure DSC, corrupt gamma/color state, or lose DisplayPort packet/audio behavior.

## Important APIs, Types, And Macros

This chunk exports the standard AMD generated offset naming convention:

- `reg<block>_<register>` gives the register offset value.
- `reg<block>_<register>_BASE_IDX` gives the base-index selector used by generated register-access macros.
- `// addressBlock: ...` comments identify the generated hardware address block.
- `// base address: ...` comments document the register database's block base before translation to the exported offset namespace.

There are no callable APIs or C data types in this chunk. Runtime code consumes these symbols through Display Core register lists, register-sequence tables, and `REG_*` helper macros that pair offsets from this file with field shifts/masks from the corresponding generated mask header.

Important macro families in this range include:

- `regPWRSEQ0_*` tail entries and complete `regPWRSEQ1_*` panel sequencing/backlight register pairs.
- `regDSC_TOP[0-3]_*`, `regDSCCIF[0-3]_*`, and `regDSCC[0-3]_*` for DSC top control, CIF config, PPS, status, error metrics, rate-buffer telemetry, memory power, and debug bus rotation.
- `regDC_PERFMON19_*` through `regDC_PERFMON22_*` for DSC perfmon, plus `regDC_PERFMON3_*` for writeback perfmon.
- `regDWB_*` and `regFC_*` for display writeback, flow-composition, CRC, overflow, host-read, soft-reset, gamut-remap, and output-gamma registers.
- `regDCHVM_*` for host-virtual-memory and RIOMMU control/status.
- `regDP_STREAM_ENC[0-3]_*`, `regAPG[0-3]_*`, `regDME[6-9]_*`, `regVPG[6-9]_*`, `regDP_SYM32_ENC[0-3]_*`, `regDP_LINK_ENC[0-1]_*`, and `regDP_DPHY_SYM32[0-1]_*` for HPO DisplayPort output.
- `regMPCC[0-3]_*` for per-compositor selection, blending, background, memory-power, and status registers.
- `regMPCC_OGAM[0-3]_*` for per-compositor output gamma LUTs, region tables, RAM A/B curve coefficients, offsets, and gamut-remap matrices.
- `regMPC_*` for the first global MPC clock/reset/CRC/perfmon event registers visible at the end of the chunk.

Most registers in this chunk have `BASE_IDX` value `2`, corresponding to display decoder/MMIO blocks in this generated header. MPC/MPCC/MPCC_OGAM registers use `BASE_IDX` value `3`, which is a distinct generated register-base domain. Mixing the two is an offset translation bug, not just a naming issue.

## Address Block Inventory

The chunk includes full or partial coverage of these generated address blocks:

- Partial `dce_dc_pwrseq0_dispdec_pwrseq_dispdec`, from `PANEL_PWRSEQ_CNTL_BASE_IDX` through `PWRSEQ_SPARE`.
- Complete `dce_dc_pwrseq1_dispdec_pwrseq_dispdec`.
- DSC instance blocks `dce_dc_dsc[0-3]_dispdec_dsc_top_dispdec`, `dsccif`, `dscc`, and `dsc_dcperfmon_dc_perfmon`.
- DWB blocks `dce_dc_wb0_dispdec_dwb_top_dispdec`, `wb_dcperfmon_dc_perfmon`, and `dwbcp`.
- `dce_dc_dchvm_hvm_dispdec`.
- HPO DP stream encoder blocks for stream encoders 0 through 3, with APG, DME, and VPG sub-blocks.
- HPO DP symbol encoder blocks `dce_dc_hpo_dp_sym32_enc[0-3]_dispdec`.
- HPO DP link encoder blocks for link encoders 0 and 1 only in this range.
- HPO DP PHY symbol blocks `dce_dc_hpo_dp_dphy_sym320_dispdec` and `dce_dc_hpo_dp_dphy_sym321_dispdec` only in this range.
- MPCC blocks `dce_dc_mpc_mpcc[0-3]_dispdec`.
- MPCC output gamma blocks `dce_dc_mpc_mpcc_ogam[0-3]_dispdec`.
- Partial `dce_dc_mpc_mpc_cfg_dispdec`, from `MPC_CLOCK_CONTROL` through `MPC_PERFMON_EVENT_CTRL_BASE_IDX`.

The largest repeated families are MPCC/OGAM and HPO DP. The chunk has 704 `regMPCC_OGAM...` macros, 120 `regMPCC[0-3]...` macros, 588 `regDP...` macros, 208 `regDWB...` macros, and 360 DSCC instance macros, plus smaller APG, VPG, DME, PWRSEQ, DCHVM, FC, and MPC groups.

## Power Sequencing And Backlight

The first visible line is a boundary artifact: `regPWRSEQ0_PANEL_PWRSEQ_CNTL_BASE_IDX` is included, but its matching offset macro appears one line earlier outside the requested range. The rest of the PWRSEQ0 tail includes panel state, delay registers, reference dividers, backlight PWM control and period, PWM group lock, and spare register entries.

PWRSEQ1 is complete in this chunk. It includes GPIO enable/control/mask/output registers, panel power-sequence control/state/delay/reference-divide registers, backlight PWM controls, PWM period, group-lock, and spare. These offsets feed panel bring-up, panel power-down, and embedded-panel backlight control code. Because the header only supplies addresses, ordering and timing semantics must come from the panel/power-sequencer driver logic and hardware spec.

## DSC And DSCC Blocks

DSC instances 0 through 3 are represented by top-control, DSCCIF, DSCC, and perfmon sub-blocks. Each instance has:

- `DSC_TOP*_DSC_TOP_CONTROL` and `DSC_DEBUG_CONTROL`.
- `DSCCIF*_DSCCIF_CONFIG0/1`.
- `DSCC*_DSCC_CONFIG0/1`, `DSCC_STATUS`, and `DSCC_INTERRUPT_CONTROL_STATUS`.
- `DSCC*_DSCC_PPS_CONFIG0` through `DSCC_PPS_CONFIG22`, which hold the packetized parameter set programmed for compressed streams.
- `DSCC*_DSCC_MEM_POWER_CONTROL`.
- Squared-error and max-absolute-error readbacks for R/Y, G/Cb, and B/Cr paths.
- Rate-buffer and rate-control-buffer maximum fullness telemetry.
- `DSCC*_DSCC_TEST_DEBUG_BUS_ROTATE`.
- One DC perfmon block per DSC instance: `DC_PERFMON19` for DSC0, `DC_PERFMON20` for DSC1, `DC_PERFMON21` for DSC2, and `DC_PERFMON22` for DSC3.

These registers integrate with mode validation and stream programming for DSC-enabled HDMI/DP paths. The PPS offsets are especially sensitive: a mismatched register list can produce a valid-looking compressed stream with bad slice, rate-control, or buffer behavior.

## Display Writeback And DCHVM

The writeback top-level block covers clock enable, memory power, flow-composition mode/flow/window/source size, update control, CRC controls/masks/results, output control, MMHUBBUB backpressure counter enable/value, host-read control, overflow status/counter, and soft reset. The associated `DC_PERFMON3` block supplies the standard perf counter control/state/current/low/high registers for writeback.

The `dwbcp` color-processing section includes HDR multiplier, gamut-remap mode/format, two gamut-remap coefficient banks, output gamma control/index/data/control, and a full RAM A/RAM B piecewise curve set for blue, green, and red channels. It includes start controls, start slopes, start bases, end controls, offsets, and region selectors 0 through 33 for each RAM bank.

`DCHVM` contributes host virtual memory and RIOMMU control/status registers: `DCHVM_CTRL0`, `DCHVM_CTRL1`, `DCHVM_CLK_CTRL`, `DCHVM_MEM_CTRL`, `DCHVM_RIOMMU_CTRL0`, and `DCHVM_RIOMMU_STAT0`. These are display memory-management surfaces and are sequencing-sensitive around power, memory access, and host-visible readback paths.

## HPO DisplayPort Blocks

The HPO DisplayPort section covers four stream encoders. Each stream encoder has clock control, input mux, audio control, clock-ramp-adjuster FIFO status/control registers, and spare register entries. Each stream also has:

- APG registers for audio-packet generation control/debug, packet control, audio CRC control/result, status/status2, memory power, and spare state. `APG1_APG_PACKET_CONTROL` appears twice with the same offset value `0x3707`, which looks like generated-header duplication and should be treated carefully by any tooling that assumes unique macro names.
- DME control and memory-control registers for DME6 through DME9.
- VPG registers for generic packet access/data, GSP frame/immediate update control, generic status, memory power, ISRC access/data, and MPEG info packets.
- DP symbol encoder registers covering stream/video control, video FIFO, double-buffering, pixel format, MSA0 through MSA8, HBlank control, SDP GSP controls 0 through 14, SDP audio controls, metadata packet control, VBID, panel replay, video CRC control/results/status, symbol count status/control, memory power, and spare.

The chunk also includes DP link encoder clock/spare registers for link encoders 0 and 1. Link encoders 2 and 3 are not present in this requested range, even though stream/symbol encoder blocks 0 through 3 are present.

The DP PHY symbol blocks are present for PHY instances 0 and 1. They include control/status, SAT update, VC rate controls 0 through 3, SAT VC state/status for virtual channels 0 through 3, training-pattern config, PRBS seeds, square-pulse and custom training-pattern registers, error status, symbol override, symbol count status/control, CRC config/status/count, and related debug/test surfaces. These offsets are used during link training, UHBR/HPO DP symbol handling, error diagnostics, and CRC/symbol-count validation.

## MPC, MPCC, Output Gamma, And Gamut Remap

The MPCC blocks `MPCC0` through `MPCC3` each include top and bottom pipe selectors, OPP ID, control, state-machine control, update-lock selection, top/bottom gain, movable color-management location control, background color components, memory-power control, and status. These registers describe how Display Core composes planes before the output pixel processor.

The four MPCC_OGAM blocks are highly repetitive and complete in this range. Each block has output-gamma control, LUT index/data/control, RAM A and RAM B curve descriptors, region selectors 0 through 33, per-channel offsets, gamut-remap coefficient format/mode, and two banks of 3x4 gamut-remap matrix coefficients. These are color-management state surfaces: wrong offsets can misprogram transfer functions or color-conversion matrices while leaving the rest of the display path apparently operational.

The final `dce_dc_mpc_mpc_cfg_dispdec` block is partial. This chunk includes global MPC clock control, soft reset, CRC control/selection/result registers, and perfmon event control. It stops before bypass background, host read, pending status, vupdate lock, mux, status, and other MPC configuration registers that follow in the source file.

## Control Flow

There is no executable control flow in this header. Runtime flow is supplied by AMDGPU Display Core code that includes this generated offset file and expands register-access helpers against ASIC-specific register tables.

Typical usage is:

1. DCN 3.5.1 resource construction selects register-list structures for a block such as DSC, DWB, HPO DP, MPCC, or MPC.
2. The selected table binds offset macros from this file with field shifts/masks from `dcn_3_5_1_sh_mask.h`.
3. Runtime display code executes modeset, link training, DSC programming, writeback setup, plane composition, color-management updates, interrupt/status handling, power management, diagnostics, or CRC/perfmon reads.
4. `BASE_IDX` tells the lower register helper which base-address segment to use for the register offset.
5. The hardware latches configuration, updates status/counters/CRC values, generates events, or changes power/clock/reset state.

This file does not encode reset values, field widths, valid values, write-one-to-clear behavior, ordering requirements, delays, locking rules, or power-domain prerequisites. Those semantics must come from the matching shift/mask header, surrounding driver code, and hardware documentation.

## State And Persistence Behavior

No software state is stored by this file. It describes MMIO-backed hardware state whose lifetime is governed by GPU reset, display modesets, link training, panel power transitions, suspend/resume, runtime power management, display hotplug, interrupt handling, and diagnostic reads.

Configuration/latching state represented in this chunk includes panel/backlight sequencing controls, DSC PPS/config/memory-power state, DWB flow/composition/output/color state, DCHVM and RIOMMU controls, HPO DP stream/audio/packet/link/PHY controls, APG/VPG/DME memory power, MPCC composition and blending configuration, output gamma LUT/curve/register banks, gamut-remap matrices, and MPC clock/reset/CRC/perfmon selection.

Volatile or readback-oriented state includes panel power state, DSC status and compression error statistics, rate-buffer fullness telemetry, perfmon counters, DWB CRC results, DWB overflow/backpressure counters, RIOMMU status, HPO DP packet/status/error/symbol/CRC counters, MPCC status, MPC CRC results, and other status/control registers whose side effects are not specified by the offset header.

Sequencing-sensitive registers include soft reset, memory-power controls, clock controls, update locks, panel power sequence delays, PWM locks, DSC interrupt/status and PPS programming, DWB update controls, HPO DP link/PHY training and CRC/symbol count controls, APG/VPG packet update controls, MPCC composition selectors, OGAM LUT index/data windows, and MPC global reset/clock controls.

## Dependencies And Integration Points

This chunk depends on the rest of the generated DCN 3.5.1 register headers, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h` for the adjacent offset definitions outside this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h` for field positions and masks that make these offsets usable for read/modify/write operations.

The generated offset and mask headers must come from the same hardware register database. A version skew between offset and mask headers can make a helper write the right bitfield shape into the wrong register or use the right register with stale bit definitions.

Expected Display Core integration points include DCN 3.5.1 resource construction, link encoder and HPO DP programming, DSC programming, writeback, MPC/MPCC plane composition, color management, CRC/perfmon diagnostics, memory/power sequencing, panel/backlight control, and DMUB/display firmware interactions that depend on ASIC-specific register addresses.

The most important runtime consumers are hardware-specific register table initializers under AMDGPU Display Core, plus helper paths for DP link training, DSC enable/disable, display writeback, color pipeline programming, audio/generic packet generation, panel power sequencing, and register diagnostics.

## Risks And Edge Cases

- The chunk starts with `PWRSEQ0_PANEL_PWRSEQ_CNTL_BASE_IDX` but not the corresponding offset macro. Any per-chunk parser must merge with the previous chunk to reconstruct complete PWRSEQ0 register pairs.
- The chunk ends halfway through MPC config. A file-level report must merge with the next chunk for the remaining global MPC registers.
- `APG1_APG_PACKET_CONTROL` is duplicated with the same value in this chunk. C preprocessing tolerates identical duplicate definitions, but generated-doc or register-database tooling that assumes one definition per name may miscount or flag this.
- Offset/base-index mismatch is the key risk. Many visually similar blocks use `BASE_IDX 2`, while MPCC/MPC/MPCC_OGAM use `BASE_IDX 3`.
- HPO DP blocks are highly repetitive across stream encoders 0 through 3, but link encoder and PHY coverage is asymmetric in this range. Copying a stream index into a link/PHY path can target absent or wrong hardware.
- DSC blocks are repetitive across four instances. A wrong `DSCCN` prefix can program a different compressor than the stream uses.
- MPCC and MPCC_OGAM blocks are repetitive and color-sensitive. Wrong instance selection can apply blending, gamma, or gamut-remap state to the wrong composed pipe.
- LUT access registers such as `*_LUT_INDEX` and `*_LUT_DATA` require driver-side ordering. The header cannot prevent stale index/data sequencing or concurrent access problems.
- Status, CRC, perfmon, interrupt, and counter registers may be clear-on-read, write-one-to-clear, latched, or sampled by update controls. The offset header does not describe those semantics.
- Power, clock, memory-power, and reset registers can affect block availability. Incorrect writes can make later status reads time out or produce misleading diagnostics.
- Panel power and backlight PWM programming is timing-sensitive. Offsets alone do not encode panel delay requirements or power-rail sequencing.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for any DCN 3.5.1 display code that includes `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`.
- Static generation checks that every non-boundary `reg...` offset in this chunk has a matching `_BASE_IDX` line and that offset/mask headers are generated from the same register database version.
- Register-table initialization checks that PWRSEQ, DSC, DWB, HPO DP, MPCC, MPCC_OGAM, and MPC register lists point to DCN 3.5.1 symbols, not nearby DCN revisions.
- Hardware smoke tests for embedded-panel power on/off, backlight PWM changes, DP modesets, DSC enable/disable at compressed modes, DWB capture, and plane composition.
- DP link-training and packet tests using HPO paths, including symbol-count/CRC/error-status readbacks and audio/generic packet validation.
- Color-management tests that load OGAM LUTs and gamut-remap matrices on each MPCC instance and verify CRC or visual output changes on the intended pipe.
- DSC stress tests that compare PPS programming, status, error counters, rate-buffer fullness, and perfmon counters across all four DSC instances.
- Suspend/resume and runtime power-management tests that exercise clock, memory-power, soft-reset, DCHVM, APG/VPG/DME, DWB, and MPCC state restoration.
- Register-dump sanity checks for duplicate macro handling, especially `regAPG1_APG_PACKET_CONTROL`, and for boundary completeness across adjacent chunks.

### subset-b-002086: lines 12995-15259

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h lines 12995-15259

## Scope And Purpose

This chunk is the final large section of AMD's generated DCN 3.5.1 register offset header. It contains C preprocessor constants only: each hardware register offset macro is paired with a matching `_BASE_IDX` macro that selects a segment from `ctx->dcn_reg_offsets[]` when DCN351 display code builds runtime MMIO addresses.

The requested range contains 2,140 `#define reg...` lines: 1,070 register offset macros and 1,070 base-index macros. The first 26 register offsets are the tail of the preceding `dce_dc_mpc_mpc_cfg_dispdec` address block because the chunk starts after that block's comment header. After that tail, the range includes complete address blocks for MPC output color-space conversion, MPC perfmon, HPO HDMI/DP support, ABM instances 0-3, MPCC MCM instances 0-3, DLPC, DPIA MU, HDA audio controller/endpoint aliases, DIO DPIA muxes, and DIG stream mapper registers. The range ends with the file's closing `#endif`.

This header is not executable driver logic. Its purpose is to bind DCN 3.5.1 register names to generated numeric offsets so higher-level display code can construct register tables for MPC composition/color, adaptive backlight management, audio/stream encoders, high-performance output paths, DisplayPort-over-USB4 DPIA plumbing, and low-level diagnostics.

## Important Register Areas

The initial tail of `dce_dc_mpc_mpc_cfg_dispdec` covers MPC global controls after the block header from the prior chunk: bypass background color registers, host read control, DPP/MPC pending status, VUPDATE lock sets 0-3, and `MPC_DWB0_MUX`. These support MPC-wide clock/reset/CRC/status programming and synchronization between address/config/cursor updates and vertical update timing.

`dce_dc_mpc_mpc_ocsc_dispdec` provides MPC output mux and output color-space conversion registers. It defines `MPC_OUT0` through `MPC_OUT3` muxes, denorm controls, clamp registers, one shared `MPC_OUT_CSC_COEF_FORMAT`, and full CSC mode/coefficient bank A/B registers for all four MPC outputs. These offsets back output mux selection and post-blend color conversion before OPP/stream output.

`dce_dc_mpc_mpc_dcperfmon_dc_perfmon_dispdec` and `dce_dc_hpo_hpo_dcperfmon_dc_perfmon_dispdec` expose display performance monitor instances 15 and 23. Each includes perfcounter control, state, high/low counter values, counter-off controls, interrupt status/acknowledge, and high/low perfmon readback. They are diagnostic counters rather than normal scanout programming registers.

The HPO/HDMI blocks cover stream encoder support for the high-performance output path. `AFMT5`, `VPG5`, and `DME5` provide audio/infoframe packet, generic packet, and metadata engine registers for HPO HDMI stream encoder 0. `HDMI_LINK_ENC`, `HDMI_FRL_ENC`, `HDMI_STREAM_ENC`, and `HDMI_TB_ENC` cover link control, fixed-rate link encoding, stream clock/character counter control, test bus controls, CRC controls, and status. `HPO_TOP_CLOCK_CONTROL`, `HPO_TOP_HW_CONTROL`, and `DP_STREAM_MAPPER_CONTROL0-3` connect HPO stream/link routing and top-level HPO enablement.

`dce_dc_opp_abm0_dispdec` through `abm3` define four repeated ABM instances, each with 60 offsets. They cover ambient-light/PWM input state, minimum and target backlight, current gain, manual gain, hysteresis and variance controls, histogram bins/thresholds, debug/select registers, BL/ABM memory power controls, software lock registers, and master lock registers. DCN351 resource setup allocates four ABM register tables even though actual panel/backlight availability is platform dependent.

`dce_dc_mpc_mpcc_mcm0_dispdec` through `mcm3` are the largest part of this chunk. Each MPCC MCM instance contributes 139 offsets for movable color management after MPCC blending: shaper control, shaper offset/scale/LUT index/data/write mask, shaper RAM A/B region programming, 3D LUT index/data/read-write/out normalization and offset registers, 1D LUT index/data/control registers, 1D LUT RAM A/B start/slope/base/end/offset/region registers, and `MPCC_MCM_MEM_PWR_CTRL`. These offsets allow DCN32/DCN35 MPC code reused by DCN351 to program per-MPCC shaper, 3DLUT, 1DLUT, and gamut/color management memories.

The final display/output plumbing blocks include `DLPC_*` display low-power counter/resync registers; `DPIA_MU_*` clock, reset, TPI status, credit, interrupt, RBBMIF timeout/status, microsecond reference, ADP status, glue, and perf-counter registers for the DPIA microcontroller interface; HDA `AZCONTROLLER1`, `AZENDPOINT1`, and `AZINPUTENDPOINT1` aliases for command/response rings and immediate command/data paths; four `DIO_DPIA_MUX*_DIO_DPIA_MUX_CONTROL` registers; and five `DIG*_STREAM_MAPPER_CONTROL` registers for mapping DIG stream encoders to link targets.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. The public interface is the generated macro namespace:

- `regNAME` is the register's generated offset within the ASIC register database.
- `regNAME_BASE_IDX` selects the base-address segment used by `BASE(regNAME_BASE_IDX)`.
- Address block comments preserve the hardware IP block and nominal base address that produced the generated offsets.

The main consumers are compile-time register-list macros in the AMD display stack. `display/dc/resource/dcn351/dcn351_resource.c` includes this header with `dcn_3_5_1_sh_mask.h`, defines `BASE(seg)` as `ctx->dcn_reg_offsets[seg]`, and expands helper macros such as `SR`, `SRI`, `SRII`, `VUPDATE_SRII`, and `SRII_DWB` into concrete `uint32_t` MMIO addresses stored in resource-specific register structs.

Important consumer structures initialized from this chunk include `struct dcn30_mpc_registers` through `MPC_REG_LIST_DCN3_2_RI`, `MPC_OUT_MUX_REG_LIST_DCN3_0_RI`, and `MPC_DWB_MUX_REG_LIST_DCN3_0_RI`; `struct dce_abm_registers` through `ABM_DCN32_REG_LIST_RI`; `struct dce_audio_registers` through `AUD_COMMON_REG_LIST_RI`; `struct dcn31_vpg_registers` and `struct dcn31_afmt_registers` for packet/audio metadata; `struct dcn10_stream_enc_registers` through `SE_DCN35_REG_LIST_RI`; and HPO stream/link encoder register tables through DCN31 HPO macros.

The paired `dcn_3_5_1_sh_mask.h` supplies field shifts and masks. This offset chunk only identifies where registers live; field layout, legal values, and side effects are defined by the shift/mask header, common display block headers, and hardware documentation.

## Control Flow And Runtime Behavior

This file has no local control flow. Runtime behavior starts when DCN351 resource construction expands the register-list macros and passes the resulting tables into hardware object constructors such as `dcn32_mpc_construct`, `dce_audio_create`, `dcn35_dio_stream_encoder_construct`, `dcn31_hpo_dp_stream_encoder_construct`, and `hpo_dp_link_encoder31_construct`.

The implied MPC programming flow is table driven. Resource initialization builds the MPC register table; MPC functions then use the offsets to control MPCC blending topology, MPC output muxes, output CSC matrices, VUPDATE locking, DWB muxing, and MCM color blocks. MPCC MCM programming is index/data-register heavy: software selects LUT indices or RAM regions, writes data/control values, and coordinates memory power and active bank state through the MPC register helper layer.

ABM control is similarly table driven. DCN351 creates four ABM register tables from the repeated ABM offset blocks, and the ABM/DMUB backlight path uses those addresses to coordinate histogram collection, gain/backlight targets, PWM behavior, and lock/update registers. Higher-level ABM commands and panel policy decide whether the registers are actively used.

Stream output construction maps stream encoder instances to VPG, AFMT, DME, DIG stream mapper, HPO, and audio blocks. For regular DIG encoders, `DIG*_STREAM_MAPPER_CONTROL` participates in mapping a stream encoder to a link target. For HPO paths, `DP_STREAM_MAPPER_CONTROL0-3`, HPO top controls, HPO HDMI stream/link/FRL/test-bus registers, and AFMT/VPG/DME instance 5 offsets support HDMI/DP high-bandwidth output programming.

The DPIA and DIO mux registers are low-level plumbing for DP-over-USB4/USB-C style routing. Clock/reset controls, TPI credit/status, local interrupts, RBBMIF timeout/status, and DIO DPIA mux controls are programmed by display link and hardware sequencing code outside this header.

## State And Persistence

The header stores no mutable state. It defines addresses for state that persists in hardware registers and internal memories while the display IP is powered.

Persistent hardware state represented in this chunk includes MPC output mux selection, output denorm/clamp and CSC coefficient banks, VUPDATE lock selection, ABM histogram/gain/backlight state, HPO packet/audio/link/FRL/test-bus state, MPCC MCM shaper/3DLUT/1DLUT RAM contents, memory power controls, DLPC counter/resync state, DPIA MU interrupt/status/perf counter state, HDA command/response ring pointers and immediate command state, and stream-to-link routing state.

Several areas have side-effecting or timing-sensitive behavior. Perfmon interrupt acknowledge registers clear status. HDA CORB/RIRB pointers and immediate command/status registers participate in hardware command queues. MPCC MCM LUT index/data registers mutate internal SRAM or staged LUT data. VUPDATE lock registers synchronize updates with scanout timing. Memory power controls can affect whether LUT or shaper memory contents are retained.

The generated offsets themselves are static build-time data. Their correctness depends on the DCN 3.5.1 register database and the runtime base arrays supplied by the DC context; changing either side without the other can produce valid C code that points at the wrong MMIO address.

## Dependencies And Integration Points

This chunk depends on the enclosing include guard from `dcn_3_5_1_offset.h` and on the matching generated `dcn_3_5_1_sh_mask.h` for bitfield access. It is DCN351-specific and should not be mixed with DCN 3.5.0, DCN 3.2, or DCN 4.x shift/mask headers without a full generated-register validation.

Primary integration points observed in the tree are:

- `display/dc/resource/dcn351/dcn351_resource.c`, which includes the header and expands most of these offsets into DCN351 resource register tables.
- `display/dc/irq/dcn351/irq_service_dcn351.c`, which includes the header for interrupt register address construction, although the IRQ table mostly uses other OTG/HPD/HUBP/DMUB registers outside this exact chunk.
- `display/dmub/src/dmub_dcn351.c`, which includes the header and initializes DMUB-visible DCN35/DCN351 register offsets through `DMUB_DCN35_REGS()` and related macros.
- Common DCN32/DCN35 headers such as `display/dc/resource/dcn32/dcn32_resource.h`, `display/dc/dio/dcn35/dcn35_dio_stream_encoder.h`, `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`, `display/dc/dce/dce_audio.h`, and ABM helper headers, which define the register-list macros that concatenate `reg...` symbols.

The base-index values in this chunk are not uniform. Most MPC, HPO, ABM, MPCC MCM, and DPIA MU offsets use base index 3; DLPC and DIO/DIG mapper offsets use base index 2; HDA AZ controller/endpoint aliases in this chunk use base index 0 or 1 depending on the alias. Correct `ctx->dcn_reg_offsets[]` initialization is therefore part of the address contract.

## Risks And Edge Cases

Generated-header drift is the main risk. A wrong offset or `_BASE_IDX` compiles successfully but redirects register writes into unrelated hardware, leading to display corruption, missing backlight control, broken audio packet programming, lost HPO routing, invalid DPIA muxing, or hard-to-debug power and interrupt failures.

The chunk starts in the middle of an address block. The first 26 macros should be interpreted as the continuation of `dce_dc_mpc_mpc_cfg_dispdec`, not as an anonymous block. Whole-file reconciliation must merge this with the preceding chunk to document the full MPC config block cleanly.

Repeated-instance consistency is a useful validation signal and a likely failure mode. ABM0-3 should be structurally parallel with offsets spaced by their block bases, and MPCC_MCM0-3 should each expose the same 139-register MCM layout. Any one-instance mismatch can show up only on a particular pipe, plane blend path, or panel backlight instance.

Index/data and memory-power registers require sequencing discipline. MPCC MCM shaper/3DLUT/1DLUT data paths, ABM histogram/backlight controls, HDA ring pointers, perfmon ack registers, and DPIA interrupt/status registers can have write-side effects. Direct ad hoc access to these macros outside existing register helpers risks stale banks, lost acknowledgements, or scanout-visible artifacts.

HPO and DPIA support is platform and policy dependent. Resource caps in DCN351 report five stream encoders, four HPO DP stream encoders, two HPO DP link encoders, and five DIG link encoders; not every board or connector exposes every route. Tests need to cover both active and inactive-path behavior.

## Test And Validation Signals

Compile coverage should include DCN351 resource construction, MPC, ABM, audio, DIG stream encoder, HPO stream/link encoder, IRQ, and DMUB register initialization. Missing or renamed offset macros usually fail at compile time through the register-list macros.

Static validation should compare this chunk against the authoritative DCN 3.5.1 generated register database, verify every non-`_BASE_IDX` macro has exactly one matching `_BASE_IDX`, check base-index values against address block expectations, and diff repeated ABM and MPCC MCM instances for layout consistency.

Runtime validation signals include successful modesets across all four timing/OPP/MPC paths, correct plane blending and MPC output CSC behavior, working DWB mux selection if writeback is enabled, correct color output with MPCC MCM shaper/3DLUT/1DLUT paths, stable ABM/backlight behavior on supported panels, audio packet/infoframe correctness, working HPO DP/HDMI routing, reliable DPIA/USB-C display bring-up, stable suspend/resume and runtime power transitions, valid perfmon readback/interrupt acknowledgement, and no register-access faults from incorrect base-index computation.

## Research Notes

This is source-tree-aligned chunk research only for `subset-b-002086`. It intentionally writes only `Docs/researches/chunks/subset-b-002086_research.md`; the later merge/reconciliation lane should combine it with adjacent chunks before producing whole-file research for `dcn_3_5_1_offset.h`.
