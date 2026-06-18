# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001744`: lines 1-2677, `Docs/researches/chunks/subset-b-001744_research.md`
- `subset-b-001745`: lines 2678-5218, `Docs/researches/chunks/subset-b-001745_research.md`
- `subset-b-001746`: lines 5219-7834, `Docs/researches/chunks/subset-b-001746_research.md`
- `subset-b-001747`: lines 7835-10383, `Docs/researches/chunks/subset-b-001747_research.md`
- `subset-b-001748`: lines 10384-12973, `Docs/researches/chunks/subset-b-001748_research.md`
- `subset-b-001749`: lines 12974-15568, `Docs/researches/chunks/subset-b-001749_research.md`
- `subset-b-001750`: lines 15569-16273, `Docs/researches/chunks/subset-b-001750_research.md`

## Chunk Research

### subset-b-001744: lines 1-2677

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 1-2677

## Purpose

This chunk is the beginning of a generated AMD DCN 3.0.2 register-offset header. It contains no executable C logic; it publishes preprocessor constants that map symbolic display-controller register names to MMIO register offsets and base-index selectors. Consumers pair these `mm...` offsets with matching field shift/mask headers and AMDGPU register access helpers to program display clocks, power domains, firmware mailboxes, display memory hubs, audio, VM contexts, HUBP pipes, cursors, and performance counters.

The requested slice covers lines 1-2677 of a 16,273-line file and contains 2,379 `#define` lines. It starts with the copyright/license, include guard, and legacy VGA/MMHUBBUB definitions, then covers early DCN 3.0.2 blocks: DCCG clock generation, DMU/DMCU/DMCUB control, MCIF writeback, MMHUBBUB/VGAIF, Azalia/HDA audio, DCHUBBUB/VM/HUBBUB memory arbitration, complete HUBP0 and HUBP1 register groups, and the start of HUBP2. The chunk ends mid-`dce_dc_dcbubp2_dispdec_hubp_dispdec` after `mmHUBP2_DCHUBP_REQ_SIZE_CONFIG_BASE_IDX`; later chunks are required for the rest of HUBP2 and subsequent display blocks.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, or allocator paths in this range. The public interface is the generated macro namespace:

- `mm<REGISTER>`: numeric register offset relative to the register aperture selected by the base-index table.
- `mm<REGISTER>_BASE_IDX`: base index used by SOC15-style register macros to choose the correct hardware register base.
- `// addressBlock: ...` and `// base address: ...`: generated grouping metadata from AMD's register database; these comments define the hardware block context but are not consumed by the compiler.

Major macro groups visible in this chunk:

- VGA and VGAIF: `mmVGA_*`, `mmD1VGA_CONTROL` through `mmD6VGA_CONTROL`, legacy CRTC/attribute/graphics/sequencer aliases, `mmVGA_SOURCE_SELECT`, and VGAIF memory-page/latency/debug controls.
- DCCG: PHY pixel-clock resync, DP DTO phase/modulo controls, `DSCCLK*` and `DPPCLK*` DTO parameters, reference/disp/soc/symbol clock gating registers, global timebase divisors, GTC DTO/current counters, soft reset, audio DTO registers, VSYNC latch/counter registers, and `SYMCLK*` enable/disable controls.
- DC perfmon blocks: `DC_PERFMON0`, `DC_PERFMON1`, `DC_PERFMON2`, `DC_PERFMON3`, `DC_PERFMON4`, `DC_PERFMON6`, and `DC_PERFMON7` control/state/value registers for DCCG, DMU, MMHUBBUB, audio, HUBP0, and HUBP1 blocks.
- DMU/DMCU/DMCUB: display power-domain config/status registers, DMCU firmware address/checksum/interrupt/communication registers, interrupt handler controller destinations, RBBMIF timeout/status, DMCUB region-window addresses, inbox/outbox queues, scratch registers, timers, GPINT, fault, memory-power, security, and control/status registers.
- MCIF writeback and MMHUBBUB: writeback buffer manager, Y/C buffer addresses and high bits, pitch, resolution, watermark, VMID, QoS, p-state/self-refresh/clock-gating controls, warmup, MCIF arbiter/debug, and MCIF perf/status registers.
- Azalia/HDA audio: stream index/data pairs for streams 0-15, codec endpoint index/data pairs, input endpoints, controller DMA/DTO/CRC/payload/memory-power registers, and codec root parameters such as vendor/device, channel count, supported rates/formats, power state, reset, converter sync, and audio port connectivity.
- DCHUBBUB/HUBBUB: SDPIF and memory aperture registers, VM framebuffer/AGP/local-HBM address registers, return-path DCC config and CRC, arbitration QoS/watermark registers, self-refresh/DRAM clock-change watermarks, urgent and p-state controls, fault/status/debug registers, and DCN VM context 0-15 page-table control/base/start/end registers plus fault/default address registers.
- HUBP0 and HUBP1: per-pipe surface format/tiling/viewport/request-size controls, request-side surface pitch/address/meta-address/flip/in-use/TTU/prefetch/vblank/flip/nominal/per-line/cursor/timing registers, return-side read-line/control/memory-power/interrupt registers, cursor/DMDATA registers, and per-HUBP perfmon blocks.
- HUBP2 start: the first surface configuration, address, tiling, viewport, and request-size offsets for the third HUBP instance.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to the AMDGPU/DCN register access path:

1. DCN 3.0.2 resource and block code includes this offset header and a matching shift/mask header for the same ASIC revision.
2. Register-list macros in DCN block headers token-paste instance IDs and register names into symbols such as `mmHUBPREQ0_DCSURF_PRIMARY_SURFACE_ADDRESS` or `mmDCCG_AUDIO_DTO0_PHASE`.
3. Resource construction stores those offsets in typed register tables for DCCG, HUBBUB, HUBP, DMCUB, audio, and perfmon blocks.
4. Runtime display code uses register helpers such as `RREG32`, `WREG32`, and SOC15/DC register wrappers to read, write, or update MMIO registers by table entry.

The macros do not encode sequencing. The driver must still handle ordering around clocks, power gating, firmware boot, mailbox setup, VM page-table programming, surface flips, cursor updates, memory watermarks, interrupt clear/ack, and perfmon start/stop.

## State And Persistence Behavior

The file itself stores no software state and persists no data. It names hardware state that lives in DCN MMIO registers:

- Clock state in DCCG registers controls display, DSC, DPP, DP, audio, symbol, GTC, and timebase DTO behavior.
- Power state in DMU, DMCU, DMCUB, Azalia, HUBBUB, HUBPREQ, HUBPRET, cursor, and MCIF registers controls memory-power, clock-gating, self-refresh, and domain power transitions.
- Firmware state in DMCU/DMCUB registers covers firmware image windows, code-window mappings, inbox/outbox ring pointers, scratch registers, timers, GPINT, fault addresses, and security controls.
- Display memory state in HUBBUB/HUBP/HUBPREQ registers covers VM apertures, page-table contexts, surface addresses, metadata addresses, tiling, viewport dimensions, prefetch timing, watermarks, flip status, and fault state.
- Audio state in Azalia registers covers stream/endpoint index-data windows, DMA controls, payload capabilities, codec parameters, DTO configuration, CRC, and power status.
- Diagnostic state in perfmon, CRC, interrupt, debug, timeout, and fault registers can be sticky, self-clearing, write-one-to-clear, or clock-dependent depending on hardware semantics.

Persistence is hardware-defined. Register contents generally survive until a modeset, fast update, power transition, suspend/resume, GPU reset, or explicit driver write changes them. This header does not protect reserved bits or preserve current values; consumers must use the matching masks and register-update helpers when side effects matter.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.2 register database and must remain synchronized with:

- The matching DCN 3.0.2 shift/mask header, which gives field-level bit positions for these offsets.
- Shared AMDGPU register access infrastructure that interprets `mm...` offsets and `_BASE_IDX` values for SOC15 display registers.
- DCN resource constructors and block register-list macros for DCCG, HUBBUB, HUBP, DMU/DMCU/DMCUB, MCIF writeback, audio, and perfmon components.
- Firmware-facing DMCUB code, which uses mailbox, scratch, timer, region, interrupt, and GPINT offsets to communicate with display microcontroller firmware.
- Memory-management and modeset paths, which use HUBBUB VM context registers, HUBPREQ surface/meta address registers, watermarks, and fault/status registers during plane programming and flip handling.

The integration style is purely symbolic and preprocessor-driven. A rename, wrong offset, wrong base index, or missing generated macro is normally caught either by compile failures in register-table initializers or, more dangerously, by runtime MMIO writes landing in the wrong hardware register.

## Risks And Edge Cases

- Offset drift is the primary risk. These constants are untyped integers, so a stale generated value can compile cleanly and corrupt unrelated display hardware state at runtime.
- Base-index drift can be as damaging as offset drift because the same numeric offset can target a different MMIO aperture when `_BASE_IDX` is wrong.
- This chunk crosses many hardware ownership boundaries. A local-looking edit to a DCCG, DMCUB, Azalia, HUBBUB, or HUBP define can break modeset, audio, firmware, memory arbitration, VM fault handling, cursor, or diagnostics.
- Several groups are instance-patterned. `HUBP0`, `HUBP1`, and `HUBP2` offsets are separated by hardware instance bases; copy/paste mistakes may affect only one pipe and only multi-display or multi-plane configurations.
- The DCHUBBUB VM-context block exposes repeated context 0-15 page-table registers. Off-by-one context mappings can produce display VM faults or memory access outside the intended aperture.
- Firmware and mailbox registers are sequencing-sensitive. Wrong DMCUB region, inbox/outbox pointer, scratch, interrupt, or GPINT offsets can cause firmware boot failures, lost commands, stuck waits, or resume-only failures.
- Power and clock controls are timing-sensitive. Misprogramming DTO, clock-gating, memory-power, self-refresh, p-state, or watermark registers can produce underflow, blank display, hangs, or rare corruption under low-power transitions.
- Audio index/data windows and codec endpoint registers require correct pairing. Wrong stream or endpoint offsets can break only particular audio streams, formats, or display connectors.
- The chunk boundary is artificial and stops in the beginning of HUBP2, so the final per-file research must merge later chunks before making complete claims about all HUBP instances.

## Test Signals

Useful validation signals for this chunk are generated-header consistency plus hardware-facing behavior:

- Build AMDGPU/DC with DCN 3.0.2 support enabled; missing or renamed macros should fail in DCN resource table initializers, DMCUB register definitions, audio code, or block register lists.
- Mechanically compare these offsets and `_BASE_IDX` values against AMD's authoritative DCN 3.0.2 register database and adjacent generated headers for related ASIC revisions.
- Check that every `mm<REGISTER>` in this range has the expected paired `mm<REGISTER>_BASE_IDX`, and that repeated instance groups keep the expected stride and naming pattern.
- Exercise display modesets across single and multi-display configurations so DCCG, HUBBUB, HUBP0, HUBP1, and later HUBP2 code paths are active.
- Test plane flips, cursor movement, metadata updates, VM-backed framebuffer scanout, suspend/resume, hotplug, p-state changes, self-refresh, and memory-power transitions while watching for underflow, VM faults, DMCUB timeouts, and display corruption.
- Validate audio over display links with multiple streams and endpoints, including format/rate changes and suspend/resume.
- Use diagnostics such as perfmon counters, CRC registers, interrupt status, DCHUBBUB fault status, DMCUB scratch/fault registers, and kernel logs to catch wrong offsets that compile but misaddress hardware.

## Cross-Chunk Notes

Earlier content is not needed for this file because this chunk starts at line 1 with the include guard. Later chunks continue from the middle of HUBP2 and eventually cover the rest of the generated DCN 3.0.2 offset namespace. The final merged per-file research document should treat this report as the early-register-block summary and combine it with later chunk reports before drawing whole-file conclusions.

### subset-b-001745: lines 2678-5218

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 2678-5218

## Scope

This chunk is a generated AMD DCN 3.0.2 ASIC register-offset header segment. It contains preprocessor constants only: each hardware register has one `mm...` macro for the MMIO register offset and one matching `mm..._BASE_IDX` macro that selects the register base index used by AMDGPU register helpers. The chunk spans 2,541 source lines and contains 1,207 register-offset macros plus 1,207 `_BASE_IDX` macros.

The slice begins in the tail of the `HUBP2` block at `mmHUBP2_DCHUBP_REQ_SIZE_CONFIG_C` and ends in the early `CNVC_CFG2` block at `mmCNVC_CFG2_FCNV_FP_SCALE_R`, so both chunk boundaries are partial hardware blocks. Complete file-level analysis must reconcile this chunk with adjacent chunks for the omitted opening `HUBP2` registers and the remaining `DPP2` converter/scaler/color-management registers.

## Purpose

The purpose of this header segment is to provide symbolic register addresses for the DCN 3.0.2 display pipeline. Driver code includes this file so it can populate per-instance register tables for HUBP, HUBPREQ, HUBPRET, cursor, DPP, CNVC, DSCL, CM, and DC perfmon blocks without hard-coding numeric offsets. The companion `dcn_3_0_2_sh_mask.h` header supplies the bit shifts and masks used with these addresses.

This is data-like source rather than executable logic. Its correctness depends on exact correspondence with the DCN 3.0.2 hardware register map and with the generated register-list macros consumed by the DC resource code.

## Address Blocks And Register Surface

Visible HUBP-side blocks:

- Tail of `HUBP2`: request-size config, HUBP control, clock control, virtual memory page config, HUBPREQ debug/debug double-buffer, and measurement window controls.
- `dce_dc_dcbubp2_dispdec_hubpreq_dispdec` at base `0x6e0`: `HUBPREQ2` surface pitch/address/meta-address, flip control, in-use/earliest-in-use readbacks, TTU/QoS, VM aperture/TLB, destination geometry, prefetch, vblank/flip/nominal delivery parameters, cursor settings, and memory power registers.
- `dce_dc_dcbubp2_dispdec_hubpret_dispdec`, `cursor0`, and `hubp_dcperfmon` blocks: `HUBPRET2`, `CURSOR0_2`, and `DC_PERFMON8`.
- Parallel full instance sets for `HUBP3`, `HUBP4`, and `HUBP5`, including `HUBPREQ3` through `HUBPREQ5`, `HUBPRET3` through `HUBPRET5`, `CURSOR0_3` through `CURSOR0_5`, and perfmon blocks `DC_PERFMON9` through `DC_PERFMON11`.

Visible DPP-side blocks:

- `DPP_TOP0`, `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, `CM0`, and `DC_PERFMON6`, rooted at DPP0 base `0x0` plus perfmon base `0x3890`.
- `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, `CM1`, and `DC_PERFMON12`, rooted at DPP1 base `0x5ac` plus perfmon base `0x3e3c`.
- Start of `DPP_TOP2` and `CNVC_CFG2`, rooted at DPP2 base `0xb58`.

The macro-family count in this slice is dominated by two complete color-management blocks (`CM0`, `CM1`, 500 definitions each including offsets and base indices), four HUBPREQ families (`HUBPREQ2`-`HUBPREQ5`, 162 definitions each), DPP converter/scaler families, cursor blocks, perfmon blocks, and repeated HUBP/HUBPRET controls.

## Important Macros And Register Families

`HUBP*_` macros define hub pipe control and data-fetch registers. They cover surface address configuration, viewport and request-size controls, HUBP clock/control registers, VM page configuration, and debug/measurement registers.

`HUBPREQ*_` macros define the request/pre-request side of plane fetch. Important groups include `DCSURF_*` pitch, primary/secondary surface addresses, metadata addresses, surface control, flip control, flip interrupt, in-use/earliest-in-use registers, TTU QoS and cursor TTU controls, VM system aperture and L1 TLB control, destination dimensions and scaler output geometry, prefetch timing, vblank/flip/nominal delivery parameters, per-line delivery, cursor settings, reference-clock to pixel-clock ratio, DRQ limit, and HUBPREQ memory power control/status.

`HUBPRET*_` macros define return/read-line behavior for hub pipe fetch. The visible register set is compact: control, memory power control/status, and read-line control registers.

`CURSOR0_*` macros define per-HUBP cursor surface controls: cursor control, surface address high/low, size, position, hot spot, destination offset, color slots, settings, and memory power control/status.

`DC_PERFMON*` macros define display performance monitor registers for HUBP and DPP instances. Each perfmon block exposes counter control, counter state, perfmon control, current value, and high/low counter registers. In this chunk the HUBP perfmon instances are `DC_PERFMON8`-`DC_PERFMON11`, while DPP perfmon instances include `DC_PERFMON6` and `DC_PERFMON12`.

`DPP_TOP*` macros define top-level DPP controls: DPP control, soft reset, CRC result registers, CRC control, and host read control. These are used for DPP bring-up, reset, diagnostics, and CRC validation.

`CNVC_CFG*` and `CNVC_CUR*` macros define converter configuration and cursor conversion controls. The configuration blocks include surface pixel format, format control, floating-point bias and scale, color keyer alpha/R/G/B, alpha LUT and pre-dealpha, output channel expansion, and memory power control/status. The cursor converter blocks include cursor control and cursor color registers.

`DSCL*` macros define display scaler setup: scaler tap/filter control, viewport start/size, reciprocal and initial-phase values, ratio registers, overscan values, round offset, clamp settings, coefficient RAM tap data/address/control, manual replicate controls, DOUT remap, debug registers, and memory power control/status.

`CM0` and `CM1` macros define DPP color-management registers. They cover gamut remap matrices, color correction, alpha/dealpha, coefficient format, HDR multiplier, de-gamma and regamma LUT control/data/region tables, output CSC matrices, shaper LUT configuration, shaper RAM A/B regions, 3D LUT mode/index/data/read-write controls, output normalization/offset, memory power controls, and debug index/data.

## Control Flow And Runtime Behavior

There is no C control flow in this chunk. Runtime behavior is indirect: `dcn302_resource.c` includes `dcn/dcn_3_0_2_offset.h` and `dcn/dcn_3_0_2_sh_mask.h`, then uses macros such as `HUBP_REG_LIST_DCN30(id)` and `DPP_REG_LIST_DCN30(id)` to initialize static register tables for each hardware instance. Constructors such as `dcn302_hubp_create()` and `dcn302_dpp_create()` pass those tables to HUBP and DPP object constructors, after which the DCN driver accesses the registers through shared `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and related helpers.

The hardware flows represented by these offsets include:

- Plane fetch programming: HUBP/HUBPREQ offsets let the driver program framebuffer and metadata base addresses, surface pitch, VMID/aperture/TLB behavior, surface control, and request sizing.
- Page flip and timing: flip-control, flip-parameter, vblank-parameter, nominal-delivery, prefetch, and in-use registers participate in flip scheduling, address latching, and watermarked memory request timing.
- Cursor composition: cursor address, position, hot spot, color, size, and cursor settings registers define hardware cursor fetch and placement for each pipe.
- Scaling and format conversion: CNVC and DSCL offsets support pixel format conversion, floating-point bias/scale, color-keying, scaler ratios, viewport geometry, filter taps, and output remapping.
- Color pipeline programming: CM offsets support de-gamma, regamma, gamut remap, output CSC, shaper LUTs, and 3D LUT programming for DPP0 and DPP1.
- Diagnostics and validation: DPP CRC registers and perfmon blocks expose counter and CRC signals used by debug, validation, and performance-monitoring paths.
- Memory power management: HUBPREQ, HUBPRET, cursor, CNVC, DSCL, and CM memory power control/status offsets let the driver gate internal memories and observe power state.

## State And Persistence

The macros themselves hold no mutable state and allocate no storage. They describe persistent memory-mapped hardware registers. Writes through these offsets mutate GPU display state until changed again, reset, power-gated, or reinitialized during modeset, suspend/resume, or GPU reset handling.

Several register groups represent stateful hardware handshakes:

- Surface address and flip registers are double-buffered or latched by display timing. Incorrect sequencing can leave stale addresses active or cause visible corruption at vblank boundaries.
- `DCSURF_SURFACE_INUSE*` and `DCSURF_SURFACE_EARLIEST_INUSE*` are readback/status style registers that expose address residency and hardware-use windows rather than ordinary driver-owned state.
- TTU, prefetch, vblank, nominal, and per-line delivery registers encode bandwidth/timing model outputs. They must stay consistent with DML calculations, watermark programming, clock selection, and plane geometry.
- LUT programming registers (`CM*_DEGAM_*`, `CM*_REGAMMA_*`, `CM*_SHAPER_*`, `CM*_3DLUT_*`) are persistent color state. Index/data style programming must preserve ordering, RAM selection, write-enable masks, and mode bits.
- Memory power control/status registers expose power-gating requests and acknowledgement. The offset header does not encode safe polling, delay, or write-one-to-clear semantics; consumers must rely on block-specific code and bitfield masks.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.2 shift/mask header for field-level operations. It also depends on AMDGPU display register-list macros that combine symbolic block names with instance IDs, for example `SRI_ARR(..., HUBPREQ, id)` and DPP/HUBP list macros, to resolve `mmHUBPREQ3_*`, `mmDPP_TOP1_*`, `mmCM0_*`, and similar names.

Confirmed integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`, which includes this header and initializes DCN 3.0.2 resource register tables.
- `dcn302_hubp_create()`, which uses `HUBP_REG_LIST_DCN30(id)` to construct HUBP instances backed by `HUBP*`, `HUBPREQ*`, `HUBPRET*`, and cursor/perfmon offsets from this slice.
- `dcn302_dpp_create()`, which uses `DPP_REG_LIST_DCN30(id)` to construct DPP instances backed by `DPP_TOP*`, `CNVC_*`, `DSCL*`, and `CM*` offsets from this slice.
- DCN register helper infrastructure (`reg_helper.h` and block-specific constructors), which treats these numeric macros as MMIO offsets and pairs them with field masks/shifts for read-modify-write operations.
- Display bring-up, mode programming, plane update, cursor update, color management, CRC, perfmon, and power-management paths that operate on the generated register tables rather than directly including this header at every call site.

Because these macros are compile-time API surface, a missing or renamed macro breaks resource table compilation. A wrong numeric value is more dangerous: it can compile cleanly while redirecting reads or writes to the wrong hardware register.

## Risks And Edge Cases

- Generated-header drift is the primary risk. Any offset mismatch against the DCN 3.0.2 register specification can corrupt unrelated display state, causing plane fetch faults, blank displays, bad flips, color corruption, cursor artifacts, or power-management regressions.
- The chunk contains repeated hardware instances that are intentionally parallel but not independently validated by C type checking. Copy or generation errors between `HUBPREQ2`-`HUBPREQ5`, `CM0`/`CM1`, or `DPP_TOP0`/`DPP_TOP1` can be hard to detect unless instance parity checks exist.
- The first and last blocks are partial. `HUBP2` starts before line 2678, and `CNVC_CFG2` continues after line 5218. Merge-lane research must not treat this slice as complete coverage for those two blocks.
- `_BASE_IDX` values are part of the address resolution contract. Most definitions here use base index `2`, but earlier file sections include other base indices; tooling that assumes all DCN offsets share one base can read or write the wrong MMIO aperture.
- CM LUT and 3D LUT registers use index/data programming patterns. Correct offsets are necessary but not sufficient; write ordering, selected RAM bank, write-enable mask, and 30-bit data mode must also be correct in consuming code.
- Perfmon and CRC registers often have control/status coupling. A stale offset in a diagnostic path may not affect ordinary display output but can invalidate test results or hide hardware failures.
- Power-control and power-status registers are safety-sensitive. Incorrect offsets or instance selection can leave memories powered down while a pipe is active, or prevent low-power entry.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generated-header, and hardware display tests:

- Compile DCN 3.0.2 resource code to catch missing macro names used by `HUBP_REG_LIST_DCN30(id)`, `DPP_REG_LIST_DCN30(id)`, and related register lists.
- Generated-header consistency checks should verify every `mm...` offset in this chunk has a matching `mm..._BASE_IDX`, and that expected repeated instances have equivalent register-name sets where the hardware specification requires parity.
- Compare this offset header with `dcn_3_0_2_sh_mask.h` and any register-list definitions to ensure every table entry has both an address and usable field masks/shifts.
- Display mode-set and page-flip testing should exercise multi-plane fetch, framebuffer address changes, metadata address changes, vblank timing, prefetch/TTU programming, and DML-derived delivery parameters on HUBP2-HUBP5.
- Cursor tests should cover movement, hot spot changes, color cursor formats, memory power transitions, and cursor updates across all visible cursor instances.
- Scaling and color tests should cover CNVC format conversion, DSCL viewport/ratio/filter programming, degamma/regamma/shaper/3D LUT programming, gamut remap, output CSC, HDR multiplier, and alpha/dealpha behavior on DPP0 and DPP1.
- Diagnostics should validate DPP CRC reads, perfmon counter programming, and host-read control on affected DPP and HUBP instances.
- Suspend/resume, GPU reset, and display power-gating tests should confirm HUBPREQ/HUBPRET/cursor/CNVC/DSCL/CM memory power state is restored or reprogrammed correctly.

## Open Questions For Merge Lane

- Confirm the preceding chunk documents the full start of `HUBP2`, including surface address config and viewport registers before `DCHUBP_REQ_SIZE_CONFIG_C`.
- Confirm the following chunk documents the remainder of `CNVC_CFG2` and subsequent DPP2 blocks, so DPP2 is not underrepresented in the final per-file report.
- Check whether any DCN 3.0.2-specific differences from DCN 3.0.1 or DCN 2.1.0 in these offsets are intentional hardware changes; the repeated names are similar across ASIC revisions, but offset shifts exist in earlier headers.

### subset-b-001746: lines 5219-7834

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 5219-7834

## Scope

This chunk covers 2,616 lines from the generated AMD DCN 3.0.2 register-offset header. It contains only C preprocessor constants and generated register block comments; there are no functions, structs, enums, storage objects, or executable statements in this slice.

The slice exports 2,402 `#define` entries: 1,201 MMIO register offset macros and 1,201 matching `_BASE_IDX` macros. Each register offset is paired with a base-segment selector used by AMD display register-table macros to form a full SOC15/DCN MMIO address.

The range starts in the middle of the DPP2 CNVC configuration block, covers most of DPP instances 2-4, covers OPP instances 0-4, then reaches the beginning of the OPTC OTG0 block. The final `dce_dc_optc_otg0_dispdec` address-block comment is a boundary marker only in this chunk; its register definitions begin after line 7834.

## Purpose

This header region maps symbolic DCN 3.0.2 display-pipeline register names to ASIC-specific register offsets. Runtime display code does not use these values directly as standalone physical addresses; it combines `mm<REGISTER>` with `DCN_BASE__INST0_SEG<BASE_IDX>` through macros such as `BASE(mm..._BASE_IDX) + mm...`.

The covered hardware areas are:

- Display Pipe Processor instances 2, 3, and 4: DPP top control/CRC, CNVC format and cursor controls, DSCL scaler/line-buffer controls, CM color-management controls, and per-DPP performance counters.
- Output Pixel Processor instances 0 through 4: FMT output formatting/dither/clamp registers, DPG display pattern generator registers, OPP buffer controls, OPP pipe control, OPP pipe CRC controls/results, and shared OPP top/ABM controls.
- DSC remap controls for OPP to DSC forwarding, one register each for DSCRM0 through DSCRM4.
- OPP-side DC perfmon block 16.
- OPTC ODM input controls for ODM0 through ODM4, including data source selection, format, bytes-per-pixel, width, input clock, memory configuration, and spare registers.

This is a hardware contract file. Its value is precise generated naming and offset data for the DCN 3.0.2 display stack, not algorithmic behavior.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the macro naming convention:

- `mm<REGISTER>` expands to the register offset within the selected DCN base segment.
- `mm<REGISTER>_BASE_IDX` expands to the segment index used by the generated `DCN_BASE__INST0_SEG*` constants.
- Instance-numbered families such as `mmDSCL2_*`, `mmCM3_*`, `mmFMT4_*`, `mmODM1_*`, and `mmOPP_PIPE_CRC0_*` describe repeated hardware instances.

The main register families are:

- `CNVC_CFG2_*`, `CNVC_CFG3_*`, and `CNVC_CFG4_*` for input pixel format conversion, floating-point bias/scale, color keying, alpha handling, pre-CSC coefficient banks, coefficient format, pre-degamma, and pre-realpha. The chunk starts with the last 25 register offsets of `CNVC_CFG2`; the complete `CNVC_CFG3` and `CNVC_CFG4` blocks each contain 31 register offsets.
- `CNVC_CUR2_*`, `CNVC_CUR3_*`, and `CNVC_CUR4_*` for cursor control, cursor colors, and cursor FP scale/bias.
- `DSCL2_*`, `DSCL3_*`, and `DSCL4_*` for scaler coefficient RAM access, scaler modes/taps, horizontal and vertical scale ratios/initial phases for luma/chroma, black color, update/autocal control, overscan, OTG blanking, recout/MPC sizing, line-buffer format and memory controls, memory power controls/status, and output buffer controls.
- `CM2_*`, `CM3_*`, and `CM4_*` for color-management state. Each complete CM block in this range has 250 register offsets covering post-CSC, gamut remap, bias, gamma correction LUTs, region programming, output CSC, degamma/regamma LUTs, 3D LUT controls/data, shaper controls/data, memory controls, debug, and related color-pipeline registers.
- `DC_PERFMON12_*`, `DC_PERFMON13_*`, `DC_PERFMON14_*`, and `DC_PERFMON16_*` for perf counter control, state, current value, high/low counter values, and perfmon control registers.
- `DPP_TOP3_*` and `DPP_TOP4_*` for DPP control, soft reset, CRC values/control, and host read control. DPP2 top appears in the previous chunk; this range resumes after it.
- `FMT0_*` through `FMT4_*` for output formatter clamp component limits, dynamic expansion, format control, bit depth, dither random seeds, clamp control, side-by-side stereo, 4:2:0 memory control, and 4:2:2 control.
- `DPG0_*` through `DPG4_*` for display pattern generator control, ramp, dimensions, RGB/YCbCr color components, offset segment, and status.
- `OPPBUF0_*` through `OPPBUF4_*`, `OPP_PIPE0_*` through `OPP_PIPE4_*`, and `OPP_PIPE_CRC0_*` through `OPP_PIPE_CRC4_*` for OPP buffering, 3D parameters, pipe control, CRC masks, and CRC result registers.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL` for shared OPP top clock and adaptive backlight management control.
- `DSCRM<n>_DSCRM_DSC_FORWARD_CONFIG` for DSC forwarding remap per OPP/DSC instance.
- `ODM0_*` through `ODM4_*` for OPTC input composition and DSC input-segment controls.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro expansion:

1. `dcn302_resource.c` includes `dcn/dcn_3_0_2_offset.h` together with the matching `dcn_3_0_2_sh_mask.h`.
2. Register list macros from hardware blocks such as DPP, OPP, OPTC, IRQ, GPIO, and perfmon expand register tokens into address-table initializers.
3. The local `SR`, `SRI`, `SRII`, and related macros in `dcn302_resource.c` form final offsets as `BASE(mm..._BASE_IDX) + mm...`.
4. Runtime code accesses those table entries through helpers such as `dm_read_reg_func`, `dm_write_reg_func`, `generic_reg_update_ex`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Ordering is still meaningful. Blocks are emitted in instance order: DPP2 partials, DPP3, DPP4, OPP0-4, DSCRM0-4, OPP perfmon, ODM0-4, then the OTG0 boundary marker. Repeated offsets and base indices must stay synchronized with the generated shift/mask header and with resource-table macros that assume these symbolic names exist.

## State And Persistence Behavior

The header itself stores no state and performs no persistence. It describes hardware state that lives in GPU display MMIO registers.

The registers named here control persistent hardware programming until a later driver write, display block reset, power-gate transition, suspend/resume restore, or ASIC reset changes them. Examples include scaler ratios/taps, line-buffer memory controls, color-management LUT configuration, post-CSC/gamut matrices, output format/dither/clamp configuration, OPP pipe routing, ODM segment format/width/source selection, and DSC forwarding selection.

Some registers expose transient or readback state rather than durable configuration, including CRC values/results, perf counter current/high/low values, perf counter state, DSCL memory power status, OPP pipe CRC results, line-buffer counters, DPG status, OPTC underflow/double-buffer status bits through matching field definitions, and clock/status fields. This offset header does not encode access direction; callers must rely on the hardware programming model and the matching shift/mask definitions.

## Dependencies And Integration Points

The primary integration point is the AMD display DCN 3.0.2 resource construction path in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`, which includes this offset header and builds hardware register tables using `BASE(mm..._BASE_IDX) + mm...`.

Important dependencies are:

- `dcn_3_0_2_sh_mask.h`, which supplies the field masks and shifts for the register names mapped here.
- `dimgrey_cavefish_ip_offset.h`, which supplies the `DCN_BASE__INST0_SEG*` constants used by the `_BASE_IDX` selectors for this ASIC.
- DC hardware block headers and register list macros such as `dcn30_dpp.h`, `dcn30_opp.h`, and `dcn30_optc.h`, which concatenate instance numbers with symbolic register names.
- Generic display MMIO helpers in `dm_services.h` and register helper layers that use the resolved addresses for reads, writes, polling, and read-modify-write operations.
- Kernel DRM/AMDGPU display flows for plane scaling, cursor setup, color management, output formatting, pipe CRC, perf monitoring, ODM/DSC routing, and display bring-up on DCN 3.0.2 hardware.

The chunk also relies on cross-generation naming stability. Many names match other DCN generations, but the numeric offsets and sometimes base indices vary by ASIC, so consumers must include the DCN 3.0.2 header for DCN 3.0.2 hardware rather than borrowing a nearby generation's constants.

## Risks And Edge Cases

- The slice begins mid-`CNVC_CFG2` and ends before any OTG0 register definitions. Whole-file reporting must merge adjacent chunks before making complete-block claims for those boundary areas.
- Wrong `_BASE_IDX` values are as dangerous as wrong offsets. The address can compile and still target the wrong MMIO segment.
- Repeated DPP/OPP/ODM instance blocks are mechanically similar. A generator error in one instance can be hard to spot in code review because only the instance number and offset sequence change.
- CM blocks are large and stateful. Bad offsets in gamma, degamma, regamma, shaper, or 3D LUT registers can cause visible color corruption without a simple compile-time signal.
- DSCL programming mixes ratios, init phases, coefficient RAM, line-buffer sizing, and memory power state. Offset drift can present as scaler artifacts, underflow, hangs, or memory-power sequencing failures.
- OPP FMT registers affect output bit depth, dithering, chroma subsampling, clamping, and 4:2:0/4:2:2 behavior. Incorrect addresses may only appear under specific pixel encodings or monitor modes.
- Pipe CRC and DPP CRC registers are often used for validation/debug. Wrong offsets can produce misleading test failures rather than obvious runtime breakage.
- Perfmon registers are counter/control pairs. Misaddressed control or value registers can silently corrupt performance telemetry.
- ODM and DSCRM mappings affect multi-segment output and DSC routing. Mistakes can surface only in multi-display, high-bandwidth, DSC, or ODM split configurations.

## Test Signals

Useful validation is mostly build-time plus hardware/display integration:

- Build the DCN 3.0.2 AMD display path to catch missing macro names in resource-table, IRQ, GPIO, DPP, OPP, and OPTC expansions.
- Preprocess `dcn302_resource.c` and representative register-list macros to confirm `mm...` and `_BASE_IDX` names resolve to the expected `BASE(...) + mm...` expressions.
- Compare this offset chunk with the generated DCN 3.0.2 register database and the matching `dcn_3_0_2_sh_mask.h` to ensure every referenced register has matching field definitions.
- Boot DCN 3.0.2 hardware and exercise display modes across DPP instances 2-4 and OPP/ODM instances 0-4.
- Validate scaler paths with upscaling, downscaling, chroma formats, overscan, line-buffer pressure, and suspend/resume to cover DSCL and CNVC programming.
- Exercise color-management paths: post-CSC, gamut remap, degamma/regamma LUTs, 3D LUT, shaper LUT, HDR/SDR transitions, and LUT memory programming.
- Run pipe CRC and DPP CRC tests and compare stable-frame CRCs across modes to catch wrong CRC result/control offsets.
- Test output formatter modes including RGB, YCbCr, 4:2:0, 4:2:2, dithering/truncation, dynamic expansion, and clamp behavior.
- Exercise DSC and ODM split configurations to validate `DSCRM*` and `ODM*` offsets, especially high-resolution or high-refresh modes that require segmentation.
- Check perfmon readouts for DPP2-4 and OPP perfmon controls to ensure counters start, stop, and report plausible values.

## Open Cross-Chunk Questions

- The later merge lane should combine this with the preceding chunk to describe the complete DPP2 top and CNVC_CFG2 blocks.
- The later merge lane should combine this with the following chunk to describe the full OTG0 timing-generator register block.
- Whole-file reconciliation should verify that the expected five-pipe DCN 3.0.2 topology is complete across DPP, OPP, DSCRM, ODM, OPTC, DIO, and perfmon sections.

### subset-b-001747: lines 7835-10383

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 7835-10383

## Purpose

This chunk is generated AMDGPU DCN 3.0.2 display-controller register address metadata. It contains no executable C code; its public interface is a set of preprocessor constants that bind symbolic `mm...` register names to MMIO register offsets, with a paired `mm..._BASE_IDX` constant for each register.

The path is under a local `ceph-client` source mirror, but this file is AMD display hardware metadata, not Ceph filesystem logic. This slice covers the output timing generator and display I/O portions of the DCN302 offset namespace:

- The full `OTG0` register family, followed by full `OTG1` through `OTG4` timing-generator families.
- OPTC misc registers and the OPTC-side display perfmon block.
- DIO I2C, DIO misc, HPD0 through HPD4, DIO perfmon, and DP AUX0 through AUX4 blocks.
- DIG/VPG/AFMT/DME stream-encoder-related blocks for DIO instances 0, 1, and 2.
- Full DP0 and DP1 link/stream/secondary-data blocks, and the first 74 DP2 registers through `mmDP2_DP_GSP8_CNTL`.

Every register entry follows the generated ABI pattern used throughout AMD DC:

- `mmREGISTER` is the register's offset value.
- `mmREGISTER_BASE_IDX` selects the ASIC IP base segment used to compute the final MMIO address.

Consumers are expected to combine both pieces through register-list macros such as `SR()` and `SRI()` rather than hard-coding numeric addresses.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or runtime APIs in this chunk. The important API is the generated macro namespace consumed by DCN302 display resource construction and register helper layers.

This line range contains 2,416 `#define` entries: 1,208 register-offset macros and 1,208 matching `_BASE_IDX` macros. All visible base-index values in this chunk are `2`, meaning these offsets are resolved through the DCN base segment selector used by the local `BASE(mm..._BASE_IDX)` helper in DCN302 resource code.

Major macro families:

- OTG timing generators: `mmOTG0_*` through `mmOTG4_*` define horizontal/vertical totals, blanking, sync, trigger controls, status counters, stereo/interlace state, snapshot controls, update locks, vertical interrupts, CRC windows/results, static screen and 3D controls, global sync lock controls, dynamic refresh-rate controls, DTO constants, DSC start position, and pipe update status.
- OPTC misc: `mmDWB_SOURCE_SELECT`, `mmGSL_SOURCE_SELECT`, `mmOPTC_CLOCK_CONTROL`, and ODM memory power/status/spare registers define cross-pipe output timing support outside a single OTG instance.
- OPTC perfmon: `mmDC_PERFMON17_*` defines counter control/state/current/high/low registers for output timing performance monitoring.
- DIO I2C and misc: `mmDC_I2C_*`, `mmDC_I2C_DDC1_*` through `mmDC_I2C_DDC5_*`, `mmDIO_SCRATCH*`, `mmDIO_MEM_PWR_*`, `mmDIO_CLK_CNTL`, `mmDIO_TEST_DEBUG_*`, and generic interrupt registers define display data channel access, DIO block memory/clock/power control, debug, scratch, and interrupt surfaces.
- Hotplug detect: `mmHPD0_*` through `mmHPD4_*` define HPD interrupt status/control, control, RX interrupt timer, and toggle filter controls for five connectors.
- DIO AUX: `mmDP_AUX0_*` through `mmDP_AUX4_*` define AUX control, timing, address, command, reply, software data, latency, GTC sync, DPHY TX, and PHY wake controls.
- VPG instances: `mmVPG0_*`, `mmVPG1_*`, and `mmVPG2_*` define generic packet access/data, frame/immediate update controls, status, memory power, ISRC data, and MPEG info registers.
- AFMT instances: `mmAFMT0_*`, `mmAFMT1_*`, and `mmAFMT2_*` define audio/VBI/infoframe packet controls, 60958 channel status, audio CRC, ramp controls, interrupt/status, audio source selection, and memory power.
- DME instances: `mmDME0_*`, `mmDME1_*`, and `mmDME2_*` define control and memory control for each DME block.
- DIG instances: `mmDIG0_*`, `mmDIG1_*`, and `mmDIG2_*` define front-end control, output CRC, test/clock/random patterns, FIFO status, HDMI metadata/audio/ACR/infoframe/generic-packet controls, TMDS controls, lane enable, version, and force-disable controls.
- DP instances: `mmDP0_*`, `mmDP1_*`, and partial `mmDP2_*` define DP link/video stream, pixel format, MSA, DPHY training/scramble/CRC/fast-training, secondary data packets, audio M/N, timestamp, MST/MSE allocation, MSO/DSC, metadata, ALPM, data bypass, GSP, and related status/control registers.

Address-block coverage in this chunk:

- `OTG0` starts at line 7835, but its `addressBlock` comment is just before the chunk. The register range is `mmOTG0_OTG_H_TOTAL` through `mmOTG0_OTG_SPARE_REGISTER`.
- `dce_dc_optc_otg1_dispdec`, base `0x200`, has 107 register offsets from `mmOTG1_OTG_H_TOTAL` to `mmOTG1_OTG_SPARE_REGISTER`.
- `dce_dc_optc_otg2_dispdec`, base `0x400`, has 107 register offsets from `mmOTG2_OTG_H_TOTAL` to `mmOTG2_OTG_SPARE_REGISTER`.
- `dce_dc_optc_otg3_dispdec`, base `0x600`, has 107 register offsets from `mmOTG3_OTG_H_TOTAL` to `mmOTG3_OTG_SPARE_REGISTER`.
- `dce_dc_optc_otg4_dispdec`, base `0x800`, has 107 register offsets from `mmOTG4_OTG_H_TOTAL` to `mmOTG4_OTG_SPARE_REGISTER`.
- `dce_dc_optc_optc_misc_dispdec`, base `0x0`, has 8 register offsets from `mmDWB_SOURCE_SELECT` to `mmOPTC_MISC_SPARE_REGISTER`.
- `dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec`, base `0x79a8`, has 9 register offsets from `mmDC_PERFMON17_PERFCOUNTER_CNTL` to `mmDC_PERFMON17_PERFMON_LOW`.
- `dce_dc_dio_dout_i2c_dispdec`, base `0x0`, has 26 register offsets from `mmDC_I2C_CONTROL` to `mmDC_I2C_READ_REQUEST_INTERRUPT`.
- `dce_dc_dio_dio_misc_dispdec`, base `0x0`, has 19 register offsets from `mmDIO_SCRATCH0` to `mmDIO_GENERIC_INTERRUPT_CLEAR`.
- HPD0 through HPD4 each have 5 register offsets, with per-instance bases `0x0`, `0x20`, `0x40`, `0x60`, and `0x80`.
- `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec`, base `0x7d10`, has 9 register offsets from `mmDC_PERFMON18_PERFCOUNTER_CNTL` to `mmDC_PERFMON18_PERFMON_LOW`.
- AUX0 through AUX4 each have 19 register offsets, with per-instance bases `0x0`, `0x70`, `0xe0`, `0x150`, and `0x1c0`.
- DIG0, DIG1, and DIG2 each have VPG, AFMT, DME, DIG, and DP address blocks. DIG0 and DIG1 each include complete 78-register DP blocks in this chunk. DIG2 includes VPG/AFMT/DME/DIG and the first 74 registers of DP2.

## Control Flow

This header chunk has no direct control flow. It is declarative MMIO address data.

The runtime flow that uses these constants is provided by AMD DC code:

1. DCN302-specific resource code includes `dimgrey_cavefish_ip_offset.h`, `dcn/dcn_3_0_2_offset.h`, and `dcn/dcn_3_0_2_sh_mask.h`.
2. `dcn302_resource.c` defines `BASE(seg)` and register-table helpers such as `SR(reg_name)` and `SRI(reg_name, block, id)`.
3. Register-list macros expand symbolic names from this header into absolute register addresses, for example `BASE(mmOTG0_OTG_H_TOTAL_BASE_IDX) + mmOTG0_OTG_H_TOTAL`.
4. DCN302 resource constructors assign those populated tables to hardware block objects: timing generators, DIO, VPG, AFMT, audio, stream encoders, AUX engines, and I2C engines.
5. Runtime display paths use generic helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET` through those tables to program mode timing, vertical interrupts, updates, HDMI/DP metadata, audio packets, AUX transactions, I2C transfers, and hotplug state.

The macros themselves do not encode sequencing. Correct ordering, waits, locking, and side-effect handling live in higher-level DC timing-generator, stream-encoder, AUX, I2C, hotplug, and link-training code.

## State And Persistence Behavior

This file stores no software state and persists nothing. It names MMIO-backed GPU display hardware state.

Hardware state represented by this chunk includes:

- Timing-generator programming: mode totals, blanking, sync polarity/positions, interlace/stereo, counters, master enable, update locks, global sync lock, DRR/VRR timing, DSC start position, and pipe update state.
- Interrupt and status surfaces: vertical interrupt positions/control registers, vtotal/vsync/DRR interrupt status, HPD interrupt status/control, DIO generic interrupt status/clear, AUX reply/status, DIG FIFO status, DP stream/link/training status, and perfmon counter state.
- CRC, readback, and diagnostics: OTG CRC windows/results, DIG output CRC, DP DPHY CRC, display perfmon counters, DIO debug and scratch registers.
- Display I/O sideband access: DDC/I2C setup/speed/status/transaction/data registers, AUX command/data/address/timing registers, HPD filter/timer controls.
- Stream-encoder and link state: HDMI packet/audio/ACR/generic/infoframe controls, TMDS controls, DP MSA timing, DP secondary-data packet controls, MST/MSE scheduling state, DSC/MSO/ALPM/GSP controls, and video stream enable/configuration.
- Memory and power controls: ODM memory power, DIO memory/clock control, VPG/AFMT memory power, and DME memory control.

Persistence is hardware-defined. Configuration registers generally remain effective until reprogramming, reset, or power-gating loss. Status, interrupt, FIFO, training, CRC, AUX, HPD, and perfmon registers may be read-only, sticky, write-one-to-clear, self-clearing, or side-effect-sensitive depending on the matching field definitions in `dcn_3_0_2_sh_mask.h` and the hardware programming guide.

## Dependencies And Integration Points

Primary dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h` supplies matching field shift/mask constants for these register offsets.

Direct DCN302 include and base-address integration:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c` includes this offset header, the matching sh/mask header, and `dimgrey_cavefish_ip_offset.h`.
- The same file defines `BASE(seg)`, `SR(reg_name)`, and `SRI(reg_name, block, id)`, which are the core contracts that combine `mm..._BASE_IDX` and `mm...` into register addresses.
- `res_cap_dcn302` declares five timing generators, five audio blocks, five stream encoders, and five DDC engines; this matches the chunk's five OTG, HPD, I2C/DDC, AUX, and partially visible stream/link instance families.

Block construction paths that consume this chunk:

- `dcn302_timing_generator_create()` uses `optc_regs[]`, populated by `OPTC_COMMON_REG_LIST_DCN3_0(id)`. That register list consumes the `OTG*` timing/update/DRR/CRC macros, ODM/OPTC data-format and memory macros from adjacent chunks, and `DWB_SOURCE_SELECT` from this chunk.
- `dcn302_dio_create()` uses `DIO_REG_LIST_DCN10()`, which currently references `DIO_MEM_PWR_CTRL`.
- `dcn302_i2c_hw_create()` uses `I2C_HW_ENGINE_COMMON_REG_LIST(id)`, which consumes `DC_I2C_DDC{id}_SETUP`, `DC_I2C_DDC{id}_SPEED`, `DC_I2C_DDC{id}_HW_STATUS`, shared `DC_I2C_*` transaction/data/control registers, and time-base metadata from another chunk.
- `dcn302_aux_engine_create()` uses AUX engine register tables based on the DP AUX families, including `DP_AUX{id}_AUX_CONTROL`, command/address/data/reply/status/timing, and DPHY TX control.
- `dcn302_vpg_create()` uses `VPG_DCN3_REG_LIST(id)`, consuming generic status, packet access/data, and frame/immediate update controls from the `VPG0` through `VPG2` blocks in this chunk for the visible instances.
- `dcn302_afmt_create()` uses `AFMT_DCN3_REG_LIST(id)`, consuming AFMT infoframe, VBI/audio packet, source, 60958, and memory-power registers.
- `dcn302_stream_encoder_create()` maps `ENGINE_ID_DIGA` through `ENGINE_ID_DIGE` to VPG/AFMT/DIG instances and uses `SE_DCN3_REG_LIST(id)`. For instances visible in this chunk, this consumes DIG HDMI/TMDS/front-end/FIFO registers and DP link/MSA/secondary-data/DSC/MST packet registers.
- `dcn302_create_audio()` uses `AUD_COMMON_REG_LIST(id)`. Audio endpoint and DCCG audio DTO registers are defined in other chunks, while this chunk contributes the stream-side AFMT, HDMI, and DP secondary audio surfaces used with the audio path.

Important downstream behavior:

- Timing-generator code under `display/dc/optc/` uses these register tables for mode timing, update lock, CRC, DRR, global sync, and DSC/ODM handoff.
- Stream-encoder and link code under `display/dc/dio/` and `display/dc/link/` use the DIG/DP/VPG/AFMT/AUX/I2C/HPD offsets to configure HDMI, DisplayPort, sideband link management, audio packets, metadata packets, and hotplug detection.
- Interrupt service code for DCN302 uses the same hardware namespace when mapping source IDs and servicing HPD, vertical blank/update, and related display interrupts.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong offset or wrong `_BASE_IDX` can compile cleanly while redirecting a register access to unrelated MMIO, causing blank displays, incorrect mode timing, missed vblank/HPD interrupts, failed AUX/I2C transfers, bad audio packets, link-training failure, or unstable power behavior.
- Offset and base-index macros are a pair. Changing one without the other breaks the `BASE(mm..._BASE_IDX) + mm...` address calculation used by `SR()` and `SRI()`.
- This chunk is highly instance-repetitive. OTG0 through OTG4, HPD0 through HPD4, AUX0 through AUX4, and DIG/DP/VPG/AFMT/DME instances differ mostly by numeric instance and base offset, making generated-header drift or off-by-one copy errors especially hazardous.
- The chunk starts after the `dce_dc_optc_otg0_dispdec` address-block comment. Merge/reconciliation should preserve that OTG0 belongs to the OTG0 block even though the comment is just outside this line range.
- The chunk ends inside the `dce_dc_dio_dp2_dispdec` block at `mmDP2_DP_GSP8_CNTL`. Later chunk research is required for the remaining DP2 register offsets and the rest of the DIO/DIG instance coverage.
- Several registers are access portals or sequenced state machines rather than ordinary storage, especially `*_ACCESS_CTRL`/`*_DATA`, I2C transaction/data registers, AUX command/data/reply registers, HPD interrupt status/control, and perfmon counters. Incorrect read/write ordering can target stale indexed state, clear events unexpectedly, or wedge sideband transactions.
- Timing-generator registers are often double-buffered or synchronized to vblank/update windows. The offsets do not reveal which writes must be update-locked, master-update-locked, or synchronized across pipes.
- HPD and AUX/I2C state is connector-facing. Bad offsets can look like monitor, cable, EDID, or link-training failures rather than an obvious register-table bug.
- DP secondary-data, GSP, DSC, MST/MSE, and metadata registers interact with stream timing. Inconsistent offsets can produce subtle failures such as missing HDR metadata, incorrect audio timing, broken DSC PPS packets, MST bandwidth allocation errors, or intermittent blanking.
- Access semantics and bit layout are not represented in this file. Callers must use the matching `dcn_3_0_2_sh_mask.h` fields and established programming sequences.

## Test Signals

Useful validation signals are compile-time register-table expansion plus hardware behavior on DCN302-class devices:

- Build AMDGPU display code with DCN302 enabled. Missing or renamed macros should fail where `dcn302_resource.c` expands `OPTC_COMMON_REG_LIST_DCN3_0`, `DIO_REG_LIST_DCN10`, `VPG_DCN3_REG_LIST`, `AFMT_DCN3_REG_LIST`, `SE_DCN3_REG_LIST`, AUX, I2C, and audio register lists.
- Diff this chunk against AMD's authoritative DCN 3.0.2 register database or adjacent generated headers to catch offset/base-index drift in OTG, DIO, AUX, HPD, DIG, and DP families.
- Exercise basic modesets on one through five active timing generators, verifying horizontal/vertical timing, vblank, page flips, update locks, DRR/VRR behavior, and DSC start position when DSC is enabled.
- Validate CRC capture/readback and perfmon paths where available, including OTG CRC windows/results and `DC_PERFMON17/18` counter registers.
- Test connector hotplug and unplug across all five HPD instances. Watch for missed HPD interrupts, interrupt storms, stale toggle-filter behavior, or incorrect source mapping.
- Read EDID and perform DDC operations across all five I2C engines; failures may show as EDID read errors, I2C arbitration timeouts, or incorrect DDC engine selection.
- Exercise DisplayPort AUX transactions across AUX0 through AUX4, including link training, DPCD reads/writes, sideband operations for MST where supported, and timeout/retry paths.
- Test HDMI and DP stream encoding on DIG0 through DIG2 at minimum, including HDMI infoframes, audio ACR, generic packets, DP MSA timing, secondary data packets, DSC PPS/GSP packets, and MST/MSE behavior.
- Run audio playback over HDMI and DisplayPort, checking AFMT audio packet generation, 60958 channel status, DP secondary audio M/N and timestamp paths, and underrun/log signals.
- Monitor kernel logs for DCN underflow, HPD/AUX/I2C timeout, link-training failure, page-flip timeout, vblank timeout, DSC metadata/PPS issues, MST allocation errors, FIFO errors, and display/audio corruption after any generated offset update.

## Cross-Chunk Notes

This is chunk 4 of `dcn_3_0_2_offset.h`, covering lines 7835-10383 of a larger generated header. The previous chunk contains the address-block comment immediately preceding `OTG0` and earlier DCN302 display-pipe blocks. The next chunk continues from line 10384, starting after `mmDP2_DP_GSP8_CNTL_BASE_IDX`, and is needed to complete DP2 and later generated register families. The final per-file research document should merge all chunks before making complete claims about DCN 3.0.2 offset coverage.

### subset-b-001748: lines 10384-12973

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 10384-12973

## Scope

This chunk is a generated register-offset slice from the AMDGPU DCN 3.0.2 ASIC register header. It covers line 10384 through line 12973 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h`. The content is almost entirely `#define` constants of the form `mm<REGISTER_NAME>` plus a matching `mm<REGISTER_NAME>_BASE_IDX`.

The chunk contains 1,203 register-offset macros and 1,203 matching base-index macros. Most of the range uses `_BASE_IDX 2`, while the MPC/MPCC blocks at the end use `_BASE_IDX 3`. There are no functions, data structures, includes, or executable control paths in this chunk.

## Purpose

The purpose of this header slice is to provide compile-time MMIO register identifiers for the DCN 3.0.2 display engine. Driver code elsewhere includes this file, combines these offsets with AMDGPU register access helpers and field-mask/shift headers, and programs display hardware blocks without hard-coding raw offsets at call sites.

This chunk maps several major display hardware areas:

- DIO/DIG/DP/VPG/AFMT/DME instances 3 through 5 for display output links, HDMI/DP packet generation, audio formatting, DisplayPort stream control, and link training.
- DCIO global and chip-level registers for reference clocks, UNIPHY link controls, GPIO/DDC/HPD/AUX pins, panel power sequencing, and backlight PWM.
- DSC compressor instances 0 through 4, including top-level control, DSCCIF, DSCC PPS programming, quality/error counters, debug buses, and perfmon blocks.
- DWB writeback blocks, including flow control, CRC, host read, overflow reporting, color/gamut/remap, and output gamma tables.
- MPC/MPCC compositor blocks, including MPCC pipe selection, gains, background color, memory power, status, and the start of MPCC output gamma/gamut-remap blocks.

## Important Macro Families

### DIO, DIG, DP, VPG, AFMT, and DME

The chunk begins in the tail of a DP2 generic-stream-packet area, with `mmDP2_DP_GSP9_CNTL` through `mmDP2_DP_GSP_EN_DB_STATUS`, so the previous chunk owns most of the DP2 block. It then fully defines display output instances 3, 4, and 5:

- `mmVPG3_*`, `mmVPG4_*`, and `mmVPG5_*` cover video packet generator access/data registers, generic packet update controls, generic status, memory power, ISRC packet access/data, and MPEG info registers.
- `mmAFMT3_*`, `mmAFMT4_*`, and `mmAFMT5_*` cover HDMI/DP audio formatter packet control, audio info, IEC 60958 channel status words, audio CRC, ramp controls, status, interrupt status, audio source selection, and memory power.
- `mmDME3_*` and `mmDME4_*` provide DME control and memory-control registers. There is no visible `DME5` block in this line range.
- `mmDIG3_*`, `mmDIG4_*`, and `mmDIG5_*` define front-end/back-end DIG control, test and CRC registers, HDMI control/status/metadata/audio/ACR/VBI/infoframe/generic-packet registers, TMDS registers, lane enable, DIG version, and force-disable registers.
- `mmDP3_*`, `mmDP4_*`, and `mmDP5_*` define DisplayPort link control, pixel format, MSA fields, DPHY training, CRC, secondary-data packet/audio/timestamp registers, MST MSE rate and slot allocation registers, MSO/DSC/metadata/ALPM/GSP controls, and double-buffer control.

The instance spacing is regular: DIG/DP instance 3 uses the `0x23xx`/`0x24xx` range, instance 4 uses `0x24xx`/`0x25xx`, and instance 5 uses `0x25xx`/`0x26xx`. These macros are likely consumed by instance-specific register-list initializers in DCN link encoder, stream encoder, audio, VPG, and DP code.

### DCIO Global and Chip-Level Blocks

The `dce_dc_dcio_dcio_dispdec` block defines global DCIO registers such as:

- `mmDC_GENERICA`, `mmDC_GENERICB`
- `mmDCIO_CLOCK_CNTL`, `mmDC_REF_CLK_CNTL`
- `mmUNIPHYA_*` through `mmUNIPHYE_*` link and channel crossbar controls
- `mmLVTMA_PWRSEQ_*` panel power sequence controls and state
- `mmBL_PWM_*` backlight PWM controls and lock
- `mmDCIO_GSL_GENLK_PAD_CNTL`, `mmDCIO_GSL_SWAPLOCK_PAD_CNTL`
- `mmDCIO_SOFT_RESET`

The `dce_dc_dcio_dcio_chip_dispdec` block defines GPIO and pad controls for generic GPIO, DDC1 through DDC5, DDCVGA, GENLK, HPD, PWRSEQ, pad strengths, AUX control, RX enable, pull-up enable, and `mmAUXI2C_PAD_ALL_PWR_OK`. These offsets are integration points for GPIO/DDC/AUX/HPD helpers, panel power sequencing, link detection, and display bring-up paths.

### DSC and DC Perfmon

The DSC portion covers compressor instances 0 through 4. Each instance follows the same pattern:

- `mmDSC_TOP<n>_DSC_TOP_CONTROL` and `mmDSC_TOP<n>_DSC_DEBUG_CONTROL`
- `mmDSCCIF<n>_DSCCIF_CONFIG0/1`
- `mmDSCC<n>_DSCC_CONFIG0/1`, `STATUS`, and `INTERRUPT_CONTROL_STATUS`
- `mmDSCC<n>_DSCC_PPS_CONFIG0` through `PPS_CONFIG22`
- memory power, squared-error accumulators, max absolute error, rate-buffer fullness, rate-control-buffer fullness, and test/debug index/data registers

Each DSC instance also has an adjacent DC perfmon block:

- `mmDC_PERFMON19_*` for DSC0
- `mmDC_PERFMON20_*` for DSC1
- `mmDC_PERFMON21_*` for DSC2
- `mmDC_PERFMON22_*` for DSC3
- `mmDC_PERFMON23_*` for DSC4

The PPS register run is particularly important because DSC programming depends on writing the correct picture parameter set into a fixed sequence of hardware registers. Missing or shifted offsets here would corrupt compressed-display setup rather than producing an obvious compile error.

### DWB Writeback

The DWB top block begins at `mmDWB_ENABLE_CLK_CTRL` and includes memory power, flow-control window/source sizing, update control, CRC mask/value registers, output control, backpressure count, host-read control, overflow status/counter, and soft reset.

The writeback perfmon block is `mmDC_PERFMON24_*`.

The DWB color-processing block begins at `mmDWB_HDR_MULT_COEF` and covers:

- gamut remap mode and coefficient format
- A and B gamut remap matrices
- output gamma control, LUT index/data/control
- RAM A and RAM B start/end/offset/region registers for B/G/R channels

This block is register-dense and sequential. Gamma and gamut programming code usually relies on these offsets being contiguous and correctly paired with field definitions.

### MPC and MPCC

The chunk then switches to base index 3 for MPC/MPCC registers. It defines MPCC instances 0 through 4:

- `MPCC_TOP_SEL`, `MPCC_BOT_SEL`
- `MPCC_OPP_ID`
- `MPCC_CONTROL`, `MPCC_SM_CONTROL`
- `MPCC_UPDATE_LOCK_SEL`
- top and bottom gain registers
- background color registers
- `MPCC_MEM_PWR_CTRL`
- `MPCC_STATUS`

The final visible block starts the MPCC output-gamma/gamut-remap area:

- `mmMPCC_OGAM0_*` is complete in this chunk, covering control, LUT access, RAM A/B region programming, and gamut remap A/B matrix registers.
- `mmMPCC_OGAM1_*` begins at line 12916 and continues past the end of this chunk. The next chunk must complete the MPCC_OGAM1 register family.

## APIs, Types, and Functions

This chunk defines no C APIs, types, functions, structs, enums, or inline helpers. Its exported surface is the preprocessor macro namespace:

- `mm...` macros resolve to register offsets.
- `mm..._BASE_IDX` macros identify the register base aperture/index used by AMDGPU register access macros.

The effective API contract is naming and numeric stability. Callers can use these constants directly or through register-list macros that are expanded into DCN hardware structures.

## Control Flow

There is no runtime control flow in this file. The operational control flow occurs in downstream driver code:

1. DCN resource construction selects an ASIC-specific register header.
2. Register-list macros bind these `mm...` constants into encoder, link, audio, DSC, DWB, DCIO, or MPC structures.
3. Runtime display code writes or reads the selected register through MMIO helpers.
4. Hardware state changes according to the written register values.

Because this file has no executable checks, offset correctness is only validated indirectly by compile-time macro resolution and hardware behavior.

## State and Persistence Behavior

The header itself has no persistent state. It names registers that control persistent hardware state while the GPU/display engine is powered:

- Link/output state: DIG, DP, HDMI, TMDS, DPHY, MST, DSC-over-DP, ALPM, and generic packet controls.
- Audio and metadata state: AFMT, VPG, HDMI infoframes, DP secondary data, GSP controls, ISRC, MPEG info, and metadata transmission.
- Board/panel state: DCIO clocks, UNIPHY crossbars, GPIO/DDC/AUX/HPD, panel power sequence, and backlight PWM.
- Compression state: DSC PPS/config/status/debug/error counters and memory power.
- Writeback state: DWB flow control, CRC, host read, overflow, color transforms, and OGAM LUTs.
- Composition state: MPCC routing, gains, background color, update locking, memory power, status, and MPCC OGAM/gamut remap.

Persistence is hardware-scoped: values may survive until reset, power-gating, mode-set reprogramming, or driver teardown depending on the block. The `*_MEM_PWR*`, `*_SOFT_RESET`, `*_UPDATE_*`, `*_DB_*`, and `*_STATUS` register families are especially state-sensitive.

## Dependencies and Integration Points

This chunk depends on the generated ASIC register model matching DCN 3.0.2 hardware documentation. It is normally used together with companion headers that provide field masks/shifts and with DCN source files that define per-block register lists.

Likely integration points include:

- Link encoder and stream encoder code for `DIG<n>`, `DP<n>`, HDMI, TMDS, lane-enable, and force-disable programming.
- DisplayPort link training, MST, DSC-over-DP, and secondary-data packet paths for `DP<n>_*`.
- Audio and infoframe paths for `AFMT<n>_*`, HDMI packet controls, and DP secondary audio registers.
- AUX/DDC/HPD/GPIO/panel/backlight code for `DC_GPIO_*`, `PHY_AUX_CNTL`, `DC_GPIO_AUX_CTRL_*`, `LVTMA_PWRSEQ_*`, and `BL_PWM_*`.
- DSC resource and validation paths for `DSC_TOP<n>_*`, `DSCCIF<n>_*`, and `DSCC<n>_*`.
- Perfmon/debug code for `DC_PERFMON19` through `DC_PERFMON24`.
- Writeback/capture paths for `DWB_*`.
- MPC compositor and color-management paths for `MPCC<n>_*`, `MPCC_OGAM0_*`, and the beginning of `MPCC_OGAM1_*`.

The `_BASE_IDX` split is part of this integration contract: most display I/O, DCIO, DSC, and DWB registers use base index 2, while MPC/MPCC registers use base index 3.

## Risks

- Numeric offset drift is high impact. A wrong register value can program the wrong hardware block while still compiling cleanly.
- Repeated instance blocks make copy/paste or generator errors plausible. DIG/DP/VPG/AFMT instances 3 through 5 and DSC instances 0 through 4 should preserve consistent per-instance spacing and matching register families.
- The chunk begins and ends in the middle of larger logical families: it starts at the tail of DP2 GSP registers and ends inside MPCC_OGAM1. Merge/reconciliation must include neighboring chunks for complete whole-file conclusions.
- `mmAFMT4_*` lacks a visible `base address` comment in this chunk even though surrounding AFMT3 and AFMT5 blocks include one. This may be harmless generated-comment variance, but it is a signal to compare against neighboring generated headers if auditing.
- Base index changes from 2 to 3 at the MPC/MPCC region. Any register-list code that assumes a uniform base index across the source file would misaddress MPCC registers.
- Long sequential LUT/region/PPS register runs are fragile. Missing one macro or shifting one offset can affect a large programmed table.
- Hardware behavior is often only observable on the target ASIC and with real displays, so normal build tests cannot prove register correctness.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage that includes AMDGPU DCN 3.0.2 paths and fails on missing/renamed macros.
- Static comparison against AMD-generated register databases or adjacent known-good DCN headers to confirm offsets, instance spacing, and `_BASE_IDX` values.
- Mode-setting tests across DP and HDMI connectors using DIG/DP instances 3 through 5, including audio, infoframes, metadata packets, DSC, MST, and link-training scenarios.
- AUX/DDC/HPD tests that exercise `DC_GPIO_*`, `PHY_AUX_CNTL`, and `DC_GPIO_AUX_CTRL_*` paths.
- Backlight and panel power-sequence tests for `LVTMA_PWRSEQ_*` and `BL_PWM_*` registers.
- DSC validation with compressed modes, checking PPS programming, interrupt/status behavior, and visual output.
- Writeback tests that verify DWB flow control, CRC values, overflow counters, host read, gamut remap, and output gamma behavior.
- MPC composition tests with multiple planes and color-management changes, checking MPCC routing, gains, background color, OGAM LUT programming, and update locks.
- Perfmon/debug tests that verify `DC_PERFMON19` through `DC_PERFMON24` counters can be selected, started, read, and stopped.

## Chunk Boundary Notes

The preceding chunk should cover the full DP2 block before `mmDP2_DP_GSP9_CNTL`. The following chunk should continue `mmMPCC_OGAM1_*` after `mmMPCC_OGAM1_MPCC_OGAM_RAMA_REGION_10_11_BASE_IDX`. A whole-file merge should treat this document as a partial view of generated register mappings, not as a complete source-file report.

### subset-b-001749: lines 12974-15568

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 12974-15568

## Scope

This chunk is a generated AMD DCN 3.0.2 register-offset header segment. It contains preprocessor register address macros only: each memory-mapped register normally has a `mm...` offset macro plus a matching `..._BASE_IDX`, while indexed legacy/VGA/Azalia codec spaces use `ix...` register-index macros without base-index companions. The slice spans 2,595 source lines and contains 2,398 `#define` lines: 1,410 register/index macros and 988 `BASE_IDX` macros.

The chunk begins in the middle of the `MPCC_OGAM1` block, covers several complete MPC/OPP/HDA/VGA/Azalia blocks, and ends in the middle of `azf0endpoint1_endpointind`. The file-level merge must therefore combine this note with adjacent chunks before drawing whole-file completeness conclusions.

## Purpose

The purpose of this header segment is to provide symbolic register offsets for AMDGPU DCN 3.0.2 display, color, backlight, audio, and legacy display register programming. Driver code can use these names with generated register lists and register access helpers instead of embedding numeric offsets or indirect register indexes.

This chunk is data-like source rather than executable logic. Correctness depends on exact agreement with AMD hardware register specifications and with the companion DCN 3.0.2 field mask/header files. A single wrong offset can redirect a read-modify-write operation to a different hardware register.

## Address Blocks And Register Surface

Covered or partially covered address blocks:

- Partial `dce_dc_mpc_mpcc_ogam1_dispdec`: tail of MPCC output gamma instance 1. The slice starts at `mmMPCC_OGAM1_MPCC_OGAM_RAMA_REGION_12_13`, continues through RAMA/RAMB piecewise-linear region, start, slope, base, end, and offset registers, then includes gamut remap format/mode and matrix coefficient registers.
- `dce_dc_mpc_mpcc_ogam2_dispdec`, `dce_dc_mpc_mpcc_ogam3_dispdec`, `dce_dc_mpc_mpcc_ogam4_dispdec`: complete MPCC output gamma instances at bases `0x400`, `0x600`, and `0x800`. Each has 88 register offsets covering OGAM control, LUT index/data/control, RAMA/RAMB curve programming, and A/B gamut-remap matrices.
- `dce_dc_mpc_mpc_cfg_dispdec`: MPC top-level configuration, including clock, soft reset, pending/status, host read, bypass background, CRC selection/result/control, vupdate/cursor/address locks, DPP pending status, perfmon event selection, and DWB muxing.
- `dce_dc_mpc_mpc_ocsc_dispdec`: output color-space conversion for MPC outputs 0 through 4. Each output has a mux, denorm controls, coefficient format, mode, and A/B matrix coefficient offsets.
- `dce_dc_mpc_mpc_rmu_dispdec`: RMU shaper and 3D LUT register surface for RMU instances 0 through 2. It exposes RMU control/memory registers and repeated shaper/3D LUT index, data, control, start/end/offset/region, and output offset offsets.
- `dce_dc_mpc_mpc_dcperfmon_dc_perfmon_dispdec`: DC perfmon 25 counter-control/counter/high/low offsets plus adjacent `DME5_DME_CONTROL` and `DME5_DME_MEMORY_CONTROL`.
- `dce_dc_hpo_hdmi_stream_enc0_hdcp2_hdcp2_dispdec`: declared at base `0x264f8` in this chunk, but no register macros appear before the next address-block marker.
- `dce_dc_hpo_hpo_top_dispdec`: HPO top clock control and DC perfmon 26 control/counter/high/low offsets.
- `dce_dc_opp_abm0_dispdec` through `dce_dc_opp_abm4_dispdec`: five Adaptive Backlight Modulation instances at bases `0x0`, `0x104`, `0x208`, `0x30c`, and `0x410`. Each instance has 60 register offsets for BL1 PWM/ambient-light inputs and DC ABM1 configuration, lookup tables, thresholds, current/min/max/backlight state, debug, and master lock.
- `dce_dc_hda_azcontroller_azdec`: HDA/Azalia controller registers for CORB/RIRB pointers, DMA position, immediate command output/input interfaces, response queues, wall clock, state-change status, and codec-pin control response paths.
- `dce_dc_hda_azendpoint_azdec` and `dce_dc_hda_azinputendpoint_azdec`: immediate command output/input data and index register offsets.
- Legacy indexed VGA blocks: `vga_vgaseqind`, `vga_vgacrtind`, `vga_vgagrphind`, and `vga_vgaattrind` define sequencer, CRT controller, graphics controller, and attribute controller indexes.
- Azalia indexed codec blocks: `azendpoint_f2codecind`, descriptor and sink-info blocks, input/output CRC result blocks, `azinputendpoint_f2codecind`, root codec parameters, 16 `azf0stream*_streamind` stream-latency/fifo counter blocks, full `azf0endpoint0_endpointind`, and partial `azf0endpoint1_endpointind`.

## Important Macros And Register Families

`mmMPCC_OGAM*_...` is the dominant color-pipeline register family in the opening portion. The registers describe MPCC output gamma LUT access, piecewise-linear curve memory (`RAMA` and `RAMB`), per-channel start/end/slope/base/offset controls, region pairs from 0-1 through 32-33, and gamut-remap coefficient matrices. Instances 2, 3, and 4 are complete in this slice; instance 1 is continued from the prior chunk.

`mmMPC_*` covers top-level Multi-Plane Compositor controls. The configuration block contains global reset, clock, pending, CRC, vupdate-lock, cursor-lock, address-lock, DPP pending, and DWB mux offsets. The OCSC block exposes per-output color conversion for five outputs. The RMU block exposes shaper and 3D LUT programming paths for three RMU instances, which are used by color-management flows that need more than simple gamma/gamut matrices.

`mmDC_PERFMON25_*` and `mmDC_PERFMON26_*` provide display performance counter controls and counter readout offsets. They integrate with diagnostics and performance monitoring rather than normal scanout setup.

`mmABM*_...` covers OPP adaptive backlight modulation. Important families include `BL1_PWM_*` ambient/backlight observation registers and `DC_ABM1_*` registers for algorithm control, IIR filters, hysteresis, backlight min/max/current, target/current pixel luminance, master override, debug select, and LUT programming.

`mmCORB_*`, `mmRIRB_*`, `mmAZALIA_*`, `mmIMMEDIATE_COMMAND_*`, `mmDMA_POSITION_*`, `mmWALL_CLOCK_*`, and `mmAZENDPOINT_*` cover the HDA controller-facing register surface. These offsets are used for command/response ring buffers, immediate codec commands, DMA position tracking, wall-clock timing, stream synchronization, codec state-change interrupts, and endpoint immediate command access.

`ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` are indexed legacy VGA register constants. They are not MMIO offsets with base-index metadata; they are selector values used through the VGA indirect access mechanism.

`ixAZALIA_F2_*`, `ixAUDIO_DESCRIPTOR*`, `ixSINK_DESCRIPTION*`, `ixAZALIA_INPUT_CRC*`, `ixAZALIA_CRC*`, `ixAZF0STREAM*`, and `ixAZF0ENDPOINT*` describe indexed Azalia codec and stream state. They include converter format, stream/channel IDs, pin capabilities, ELD/sink information, audio descriptors, CRC readbacks, FIFO/latency counters, pin widget controls, channel speaker mapping, HBR/lipsync, multichannel mode, codec status overrides, LPIB snapshots, coding type, wireless display identification, keepalive, and audio enable/format-change interrupt status.

## Control Flow And Runtime Behavior

There is no C control flow in this chunk. Runtime behavior is indirect: AMDGPU display code includes generated register-offset headers and passes these symbols to register access macros/tables. For `mm...` macros, the companion `..._BASE_IDX` value identifies the register base segment used by the access helper. For `ix...` macros, the value is an indirect register index in a legacy VGA or Azalia codec/register space.

The hardware-oriented flows represented by these offsets are:

- Color programming: MPCC OGAM and MPC RMU paths expose LUT index/data/control registers, curve segment parameters, 3D LUT access, and matrix coefficient registers. Driver code programs these while enabling color transforms, HDR/gamut remap, or per-plane/output correction.
- MPC composition and output routing: MPC mux, OCSC, denorm, bypass background, DPP pending, DWB mux, and vupdate-lock registers coordinate compositor output routing and synchronized register updates.
- Validation and diagnostics: MPC CRC and DC perfmon registers expose hardware counters, CRC results, and event selection used to validate display output or collect performance data.
- Backlight modulation: ABM registers carry ambient-light/PWM inputs and algorithm state used to compute or clamp panel backlight values.
- Audio command and stream handling: HDA/Azalia controller and indexed endpoint registers support codec command submission, response retrieval, stream format/channel setup, audio descriptors, ELD/sink reporting, CRC checks, latency counters, and audio enable/disable/format-change notification.
- Compatibility access: VGA indexed constants preserve access to legacy sequencer, CRT, graphics, and attribute controller registers where the hardware still exposes or emulates those spaces.

## State And Persistence

The macros themselves hold no mutable state and allocate no storage. They describe persistent hardware registers or indirect register indexes. Writes through consumers of these macros can remain effective until the display block is reprogrammed, reset, power-gated, or restored after suspend/resume.

Several represented register groups have stateful or handshake behavior:

- LUT and curve programming registers are index/data based. Consumers must program indexes and data in the correct order and select the intended RAM bank or color channel via companion field definitions.
- Vupdate, cursor, and address lock registers gate when pending display state becomes visible to scanout hardware. Incorrect lock/unlock sequencing can leave pending state unapplied or applied at the wrong frame boundary.
- RMU/OGAM and gamut-remap coefficient sets have A/B register banks in several places, implying double-buffered or selectable coefficient sets whose active bank is controlled by fields outside this offset-only chunk.
- ABM registers include live sensor/algorithm state, current backlight values, min/max constraints, and master-lock controls. These are persistent hardware control values and also carry runtime observations.
- CORB/RIRB and immediate-command registers are queue/handshake state for HDA command transport. Pointer and response registers must be synchronized with hardware ownership rules.
- Azalia endpoint, stream, CRC, and interrupt-status indexed registers expose latched stream status, counter values, sink data, pin state, and audio enable/format-change conditions.

## Dependencies And Integration Points

This chunk depends on the broader generated DCN 3.0.2 register header set:

- Companion `dcn_3_0_2_sh_mask.h` field definitions provide bit shifts and masks for the offsets named here.
- Register-list tables in AMDGPU DC code combine offset macros, base indices, masks, and shifts into typed per-block access structures.
- ASIC-version dispatch code chooses the DCN 3.0.2 layout for compatible GPUs.
- Enumeration headers such as AMD GPU SOC enum headers define symbolic values for MPCC OGAM, RMU, ABM, and Azalia fields that are programmed through these offsets.

Likely consumers include AMDGPU display color-management code, MPC/OPP resource setup, ABM/backlight management, display diagnostics/perfmon paths, HDMI/DP audio setup, Azalia codec command handling, and low-level VGA/HDA compatibility access paths. The generated names are compile-time API surface: renaming or deleting a macro breaks any consumer that references that register symbol, while changing a numeric value can compile cleanly but misprogram hardware.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A stale or wrong offset can read or write the wrong MMIO location or indirect register, with failures ranging from subtle color errors to blank display, broken audio, bad backlight behavior, or stuck hardware queues.
- This slice has partial block boundaries. `MPCC_OGAM1` is already in progress at line 12974, and `azf0endpoint1_endpointind` continues after line 15568. Reviewers must not treat those two blocks as complete based only on this chunk.
- Instance parity matters. `MPCC_OGAM2`, `MPCC_OGAM3`, and `MPCC_OGAM4` are structurally parallel with 88 register offsets each, and ABM0 through ABM4 are structurally parallel with 60 register offsets each. Any off-by-one generation error in one instance would be easy to miss in manual review but can affect only a subset of outputs/pipes.
- `BASE_IDX` values are part of the access contract. Most DCN MMIO macros in this chunk use base index `3`, but several nearby HPO/perfmon macros use other base indices. Consumers that assume a single base for the whole chunk would be wrong.
- The HPO HDCP2 address-block marker appears without register definitions in this slice. That may be a valid empty generated block or a boundary artifact; the merge lane should verify against adjacent chunks and generated source metadata.
- Indexed `ix...` constants are semantically different from `mm...` offsets. Tooling that expects every register macro to have a `BASE_IDX` partner will falsely flag VGA and Azalia indexed entries.
- HDA queue pointers, interrupt statuses, ABM locks, and color LUT index/data registers have hardware-specific ordering and acknowledgement semantics that are not expressible in an offset-only header. Consumers must rely on the companion masks and hardware programming sequence.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generation-time, and hardware/display regression signals:

- Compile AMDGPU DCN 3.0.2 display paths to catch missing or renamed offset macros.
- Generated-header checks should verify that every `mm...` register in this slice has the expected `..._BASE_IDX`, while `ix...` indexed registers are exempt.
- Cross-check offsets against `dcn_3_0_2_sh_mask.h` and register-list tables so each used register has matching field masks and no consumer points at a missing symbol.
- Instance-parity tests can compare MPCC OGAM2/3/4 and ABM0/1/2/3/4 layouts where hardware is expected to be repeated, while allowing documented base-address differences.
- Display color tests should exercise OGAM, gamut remap, OCSC, RMU shaper, and 3D LUT programming on multiple pipes/outputs.
- Backlight and panel tests should cover ABM enable/disable, ambient-light input handling, PWM/backlight min/max/current transitions, master lock, suspend/resume restore, and debug/status readbacks.
- Audio tests should cover HDA CORB/RIRB command transport, immediate codec commands, audio stream format/channel assignment, ELD/audio descriptor reads, HBR/lipsync/multichannel paths, CRC counters, latency counters, and audio enable/disable/format-change interrupts.
- Diagnostics should read MPC CRC results and DC perfmon 25/26 counters and verify event selection and counter rollover behavior.

## Open Questions For Merge Lane

- Confirm the previous chunk contains the start of `MPCC_OGAM1` and that the next chunk completes `azf0endpoint1_endpointind`.
- Verify whether the empty `dce_dc_hpo_hdmi_stream_enc0_hdcp2_hdcp2_dispdec` block is intentionally empty for this generated header or split by a generation/chunking boundary.
- Identify concrete AMDGPU call sites for the OGAM/RMU/ABM/Azalia groups before the final per-file report names specific functions or structs.

### subset-b-001750: lines 15569-16273

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 15569-16273

## Scope

This chunk is the closing Azalia/audio endpoint section of the generated AMD DCN 3.0.2 register offset header. It contains preprocessor constants only. Each `ix...` macro names an indirect Azalia codec endpoint register index, not a direct MMIO address. The chunk starts in the tail of `azf0endpoint1_endpointind`, covers complete output endpoint index maps for `AZF0ENDPOINT2` through `AZF0ENDPOINT7`, then covers complete input endpoint index maps for `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7`, and ends with the header guard `#endif`.

The companion direct endpoint index/data windows and the start of `AZF0ENDPOINT0`/`AZF0ENDPOINT1` are outside this chunk. For DCN 3.0.2, `dcn302_resource.c` includes this offset header and uses the direct `AZF0ENDPOINT{id}_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `...DATA` registers to build `dce_audio_registers`; the indirect `ix...` values in this chunk are the per-endpoint indices subsequently written through those windows by the DC audio code.

## Purpose

The purpose of these constants is to provide stable symbolic indices for the GPU display audio codec's HD-Audio/Azalia endpoint register space. Driver code does not access the endpoint controls by normal direct-register names. Instead, it selects an endpoint-local index through `AZALIA_F0_CODEC_ENDPOINT_INDEX` and reads or writes `AZALIA_F0_CODEC_ENDPOINT_DATA`. These `ixAZF0ENDPOINT*` and `ixAZF0INPUTENDPOINT*` values are the selected indices.

The output endpoint blocks describe HDMI/DP audio sink capabilities and runtime state advertised to, or consumed by, the audio stack: converter format and stream ID, pin capabilities, speaker/channel allocation, supported audio descriptors, lipsync, high-bit-rate audio, sink identity, hot-plug/audio enable, channel-status overrides, LPIB snapshots, coding/format-change state, wireless display identification, and audio enable/disable interrupt status.

The input endpoint blocks describe a smaller capture/input surface: input converter format and stream ID, input pin capabilities, unsolicited response and pin sense, multichannel enables, HBR response, channel allocation, hot-plug/audio enable, default configuration, LPIB snapshots, input activity/status control, and input infoframe fields.

## Important Macros And Register Families

Output endpoint coverage:

- `ixAZF0ENDPOINT1_*` at lines 15569-15605 is the tail of endpoint 1. It includes `RESPONSE_HBR`, `SINK_INFO0..8`, `HOT_PLUG_CONTROL`, unsolicited response force, default configuration response, multichannel enable/mode, channel-status override slots 0 through 8, association info, digital output status, LPIB snapshot registers, coding/format-change flags, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status.
- `ixAZF0ENDPOINT2_*` through `ixAZF0ENDPOINT7_*` repeat the full output endpoint layout with endpoint-specific macro names. Each complete block maps converter controls at indices `0x0001..0x000e`, pin controls at `0x0020..0x006e`, audio descriptor slots `0x0028..0x0035`, sink-info slots `0x003a..0x0042`, channel-status override slots `0x0059..0x0061`, and endpoint status/interrupt registers `0x006b..0x006e`.

Input endpoint coverage:

- `ixAZF0INPUTENDPOINT0_*` through `ixAZF0INPUTENDPOINT7_*` repeat the input endpoint layout. Each block maps input converter controls at `0x0001..0x0006`, input pin controls at `0x0020..0x0038`, channel allocation at `0x0053`, hot-plug/audio enable and default configuration at `0x0054..0x0056`, LPIB snapshot registers at `0x0064..0x0066`, input status control at `0x0067`, and input infoframe at `0x0068`.

Important endpoint-local indices are intentionally reused across instances. For example, every output endpoint's `...CODEC_PIN_CONTROL_RESPONSE_HBR` is `0x0038`, and every input endpoint's `...CODEC_INPUT_PIN_CONTROL_INFOFRAME` is `0x0068`; the instance is selected by the direct endpoint index/data MMIO window, while the `ix` value selects the endpoint-local register.

## APIs, Types, And Consumers

This chunk defines no C functions, structs, enums, or storage. Its API surface is the macro namespace consumed by generated register helpers and display audio code.

Relevant consumers and integration types observed nearby:

- `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` in `display/dc/dce/dce_audio.h` describe the direct endpoint index/data window and bitfield masks used by the audio object.
- `AUD_COMMON_REG_LIST(id)` in `dce_audio.h` expands to the per-instance `AZF0ENDPOINT{id}_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `...DATA` direct registers. This is the direct register path used to access the indirect `ix` values defined here.
- `dcn302_resource.c` includes `dcn/dcn_3_0_2_offset.h` and `dcn/dcn_3_0_2_sh_mask.h`, creates `audio_regs[]` entries for output endpoints 0 through 6, and wires `dcn302_create_audio()` to `dce_audio_create()`.
- `dce_audio.c` defines `AZ_REG_READ(reg_name)` and `AZ_REG_WRITE(reg_name, value)` as wrappers around `read_indirect_azalia_reg()` and `write_indirect_azalia_reg()`. Those helpers write an `ix...` index to `AZALIA_F0_CODEC_ENDPOINT_INDEX`, then read/write `AZALIA_F0_CODEC_ENDPOINT_DATA`.
- Companion `dcn_3_0_2_sh_mask.h` provides field masks and shifts for the registers named in this offset chunk, such as HBR capable/enable bits, hot-plug/audio enable bits, input infoframe validity, LPIB fields, and default configuration fields.

The generic DC audio code mostly references uninstanced names such as `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR`; preprocessor indirection and resource tables bind those logical names to the selected audio instance's endpoint window. This chunk provides the instance-specific generated names needed for the DCN 3.0.2 register set.

## Control Flow And Runtime Behavior

There is no executable control flow in this header. Runtime behavior appears when these indices are passed through the indirect Azalia access sequence:

1. A DCN 3.0.2 resource pool creates a `struct audio` for an endpoint instance using `audio_regs[inst]`.
2. Audio code selects an indirect endpoint register by writing an `ix...` value into the endpoint's `AZALIA_F0_CODEC_ENDPOINT_INDEX` field.
3. Audio code reads or writes `AZALIA_F0_CODEC_ENDPOINT_DATA` to observe or update the selected endpoint-local register.
4. Higher-level audio flows use those reads/writes to enable or disable audio, program sink capabilities, advertise HBR support, set HDMI/DP connection type, program speaker allocation, write audio descriptor slots, set lipsync values, and publish monitor/sink identity.

Representative flows represented by this chunk:

- Audio enable/disable: `dce_aud_az_enable()` and `dce_aud_az_disable()` manipulate `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, which corresponds to the `ixAZF0ENDPOINT*_...HOT_PLUG_CONTROL` index `0x0054` for output endpoints.
- HBR exposure: `dce_aud_az_disable_hbr_audio()` and `set_high_bit_rate_capable()` read/write `...RESPONSE_HBR` at `0x0038`.
- HDMI/DP sink programming: `dce_aud_az_configure()` programs `...CHANNEL_SPEAKER`, `...AUDIO_DESCRIPTOR0 + format_index`, `...SINK_INFO0..8`, and `...RESPONSE_LIPSYNC`. Those indirect indices are provided for every output endpoint block in this chunk.
- Status and progress snapshots: LPIB snapshot/control/timer indices (`0x0064..0x0066`) allow software to observe audio buffer position state. Output endpoints also expose audio enabled/disabled/format-changed interrupt status at `0x006c..0x006e`.
- Input audio reporting: input endpoints expose input activity/channel layout, infoframe validity, and channel allocation through `INPUT_STATUS_CONTROL`, `INFOFRAME`, and `CHANNEL_ALLOCATION`.

## State And Persistence

The macros themselves are compile-time constants and hold no mutable state. They name hardware-backed registers whose values persist in the display audio hardware until explicitly changed, reset, power-gated, or reinitialized during modeset/resume paths.

Important state categories:

- Configuration state: converter format, stream ID, digital converter control, widget control, channel/speaker allocation, multichannel enable state, multichannel mode, HBR enable/capability, coding type, and input infoframe fields.
- Sink capability state: output endpoint audio descriptors, supported size/rate parameters, pin capabilities, lipsync responses, sink information, wireless display identification, and default configuration response.
- Event/status state: pin sense, unsolicited response controls, format-changed state, digital output status, audio enable/disable interrupt status, audio format change interrupt status, input activity, and infoframe validity.
- Snapshot/counter state: LPIB and LPIB timer snapshot registers are read/lock style hardware state used to correlate buffer position and timing.
- Power/clock gating adjacency: hot-plug control includes clock gating and audio enabled semantics in companion masks; incorrect state can keep the endpoint inactive or prevent low-power behavior.

Because endpoint-local indices are reused across output and input instances, persistence is per selected endpoint window. Writing index `0x0054` through endpoint 2 affects endpoint 2 hot-plug/audio enable state; writing the same index through endpoint 5 affects endpoint 5.

## Dependencies And Integration Points

Primary dependencies:

- Generated DCN 3.0.2 direct register offset macros in the same header, especially `regAZF0ENDPOINT*_AZALIA_F0_CODEC_ENDPOINT_INDEX`, `regAZF0ENDPOINT*_AZALIA_F0_CODEC_ENDPOINT_DATA`, and corresponding input endpoint windows outside this chunk.
- Generated field masks and shifts in `dcn_3_0_2_sh_mask.h`.
- Register helper macros in the DC display code (`REG_SET`, `REG_READ`, `REG_WRITE`, `set_reg_field_value`, `get_reg_field_value`) that combine direct register offsets, field masks, and indirect indices.
- DCN 3.0.2 resource construction in `display/dc/resource/dcn302/dcn302_resource.c`, which selects the correct generated offset/mask headers for this ASIC version.
- `display/dc/dce/dce_audio.c`, which implements HDMI/DP audio capability programming, HBR capability decisions, lipsync programming, sink info publication, and audio enable/disable through these indirect Azalia registers.

Broader integration points include the DRM connector/EDID audio pipeline that fills `struct audio_info`, DisplayPort link information used to limit supported sample rates, HDMI timing calculations, suspend/resume reinitialization, hot-plug handling, and hardware diagnostics for audio enable/status interrupts.

## Risks And Edge Cases

- Generated-header drift is the largest risk. If any `ix` value is wrong, the driver will read or write the wrong endpoint-local register through a valid direct endpoint window. That kind of error may compile cleanly but corrupt audio capabilities, enable state, sink identity, or status handling.
- The chunk begins mid-`AZF0ENDPOINT1`. File-level reconciliation must include the previous chunk for the full endpoint 1 map and endpoint 0 context.
- `dcn302_resource.c` constructs output audio objects for endpoints 0 through 6, while this generated header also exposes output endpoint 7 and input endpoints 0 through 7. The final file report should distinguish generated hardware surface from currently instantiated DCN 3.0.2 resource objects.
- Output and input endpoint maps are similar but not interchangeable. Input endpoints omit sink-info and audio descriptor arrays and instead expose input-specific channel allocation, input status control, and infoframe state. Generic tooling must not assume every `AZF0*ENDPOINT` block has the same register set.
- Several logical register names are used by loops or arithmetic, especially `AUDIO_DESCRIPTOR0 + format_index`. Descriptor indices must remain contiguous from `0x0028` through `0x0035`; a gap or off-by-one would silently program the wrong audio format descriptor.
- Status and force registers have hardware-specific write semantics not expressed in this offset header. Examples include unsolicited response force, interrupt status, format-changed status, and LPIB snapshot locking. Consumers need the companion mask/spec semantics, not only the index values.
- Audio enable sequencing toggles clock-gating disable around writes to hot-plug control. Wrong hot-plug index or mask pairing can leave audio disabled, force clocks on, or race with power management.
- Reused endpoint-local indices require correct endpoint instance selection. A stale or wrong `audio_regs[inst]` direct window would make correct `ix` values operate on the wrong physical audio endpoint.

## Test Signals

Useful validation signals for this chunk are mostly build-time generated-header checks plus hardware display/audio tests:

- Compile DCN 3.0.2 AMDGPU display code with `dcn302_resource.c` including `dcn_3_0_2_offset.h` and `dcn_3_0_2_sh_mask.h`; missing or renamed macros should fail at build time.
- Generated-header consistency checks should verify that output endpoints 2 through 7 have identical local index values for matching register names, that input endpoints 0 through 7 have identical local index values for matching input register names, and that companion sh/mask definitions exist for each generated register where fields are expected.
- HDMI audio tests should verify audio enable/disable, speaker allocation, supported audio descriptor programming, lipsync reporting, HBR capability exposure, and sink name/manufacturer/port ID publication through `SINK_INFO0..8`.
- DisplayPort and eDP audio tests should exercise DP connection selection, HBR exposure under bandwidth constraints, MST audio capability programming, and sample-rate filtering from `dce_audio.c`.
- Hot-plug and modeset tests should watch `HOT_PLUG_CONTROL`, pin sense, default configuration, audio enabled/disabled interrupt status, and format-changed interrupt status across connect/disconnect and mode changes.
- Suspend/resume and runtime power tests should verify that endpoint state is restored after reset or power gating and that clock-gating disable is not left asserted.
- For input endpoints, validation should check channel allocation, input activity/channel layout status, infoframe validity, and LPIB snapshot behavior where hardware and driver paths support audio input.

## Open Questions For Merge Lane

- Confirm from adjacent chunks the complete endpoint 0 and endpoint 1 maps, including the first half of `AZF0ENDPOINT1` before line 15569.
- Determine whether DCN 3.0.2 intentionally exposes output endpoint 7 and all input endpoints without creating corresponding `struct audio` objects in `dcn302_resource.c`, or whether those are reserved/generated-for-parity surfaces.
- Cross-check `dcn_3_0_2_offset.h` against `dcn_3_0_2_sh_mask.h` for every output/input endpoint register in this chunk, especially status/interrupt and force registers where field semantics matter.
