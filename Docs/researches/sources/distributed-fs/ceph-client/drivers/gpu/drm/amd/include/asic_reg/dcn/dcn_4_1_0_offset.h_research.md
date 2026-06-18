# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002144`: lines 1-2613, `Docs/researches/chunks/subset-b-002144_research.md`
- `subset-b-002145`: lines 2614-5117, `Docs/researches/chunks/subset-b-002145_research.md`
- `subset-b-002146`: lines 5118-7579, `Docs/researches/chunks/subset-b-002146_research.md`
- `subset-b-002147`: lines 7580-10140, `Docs/researches/chunks/subset-b-002147_research.md`
- `subset-b-002148`: lines 10141-12728, `Docs/researches/chunks/subset-b-002148_research.md`
- `subset-b-002149`: lines 12729-15420, `Docs/researches/chunks/subset-b-002149_research.md`
- `subset-b-002150`: lines 15421-16662, `Docs/researches/chunks/subset-b-002150_research.md`

## Chunk Research

### subset-b-002144: lines 1-2613

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 1-2613

## Purpose

This chunk is the opening slice of AMD's generated DCN 4.1.0 register-offset header. It has no executable C logic; it publishes preprocessor constants that map symbolic DCN register names to MMIO offsets and to a `_BASE_IDX` selector used by AMDGPU display register-table macros.

The requested range covers the license/header guard opening and 1,389 `#define reg...` entries when counting both offset macros and matching `_BASE_IDX` macros. It starts with DCCG clock-generation offsets and ends at the first register of the `HUBPRET1` block. The rest of the 16,662-line header continues in later chunks.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The exported interface is a generated macro namespace:

- `reg<REGISTER>`: register offset within the selected DCN base segment.
- `reg<REGISTER>_BASE_IDX`: selector passed to `BASE(reg<REGISTER>_BASE_IDX)` in DCN 4.1.0 consumers. In this chunk, DCCG/DFS entries use base index `1`, while most display-decoder, DMU, DWB, HDA, hubbub, VM, HUBP, HUBPREQ, HUBPRET, and cursor entries use base index `2`.

The main register families in this range are:

- DCCG and DCCG DFS: `DENTIST_DISPCLK_CNTL`, PHY PLL pixel-clock resync controls, DP/DSC/DPP clock DTO phase/modulo/parameter registers, OTG pixel-rate controls for OTG0-OTG5, symbol-clock enables for PHY lanes A-G, HDMI stream/char clock controls, clock-gating controls, time-base dividers, soft reset, and VSYNC latch/counter registers.
- DMU, RBBMIF, IHC, DCPG, and DMCUB: display interrupt status and destination routing, GPU timer positions, power-gating domain controls and status, DMUB/DMCUB reset/control/status, memory-region address/window registers, mailbox and outbox base/size/read/write pointers, scratch registers, GPINT registers, fault registers, timer registers, and register inbox/outbox command registers.
- DWB and DWB color pipeline: display writeback top controls, frame-composition window/source registers, CRC controls and values, overflow/backpressure/debug registers, HDR multiplier, gamut remap matrices, OGAM LUT controls, and RAM A/B piecewise gamma registers.
- MMHUBBUB and MCIF writeback: writeback memory interface address/stride/pitch/watermark/arbitration/debug registers, MMHUBBUB clock, memory power, warmup VMID, error status, and outstanding-counter registers.
- HDA/Azalia: controller clocking, DTO, DMA controls, payload capabilities, audio CRC controls, root codec parameters, miscellaneous audio clock/power straps, 16 stream index/data windows, 8 output endpoint index/data windows, and 8 input endpoint index/data windows.
- DCHUBBUB and VM request interface: arbitration watermarks for sets A/B, urgent bandwidth fractions, self-refresh and P-state transition watermarks, SAT/QOS controls, global timer/CRC/debug/status/memory-power controls, VM framebuffer/AGP/default address registers, VM fault registers, and VM context 0-15 page-table control/base/start/end address registers.
- HUBP/HUBPREQ/HUBPRET/cursor instances: complete register groups for HUBP0 and the beginning of HUBP1, including surface configuration, tiling, viewport, request sizing, MALL/cache/debug controls, primary/secondary surface addresses, flip controls, surface-in-use tracking, TTU/QOS/prefetch/nominal/flip/vblank timing parameters, VM aperture/TLB settings, HUBPREQ memory power/status, HUBPRET read-line controls, and CURSOR0 position, hot spot, size, color, address, and 3DLUT-related registers.

Several blocks are mechanically repeated by instance. Examples include OTG0-OTG5 clock controls, AZF0STREAM0-15, AZF0ENDPOINT0-7, AZF0INPUTENDPOINT0-7, HUBP0/HUBP1, and HUBPREQ0/HUBPREQ1. The chunk boundary is artificial and cuts off `dcn_dcec_dcbubp1_dispdec_hubpret_dispdec` after `regHUBPRET1_HUBPRET_READ_LINE0`.

## Control Flow

This header has no runtime control flow. The runtime path is supplied by AMDGPU display code:

1. DCN 4.1.0 modules include this offset header together with `dcn_4_1_0_sh_mask.h`.
2. Register-list macros such as `SR(...)`, `SRI_ARR(...)`, `HUBP_SF(...)`, and block-specific lists token-paste symbolic register names into offset, shift, and mask table initializers.
3. Consumers compute an address as `BASE(reg<name>_BASE_IDX) + reg<name>`. For example, `dmub_dcn401.c` defines `REG_OFFSET_EXP(reg_name)` this way with `DCN_BASE__INST0_SEG2`, while `dcn401_clk_mgr.c` does the same for clock-manager registers with `DCN_BASE__INST0_SEG1`.
4. Runtime paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers use the constructed tables to program the actual MMIO registers.

The macros do not encode sequencing rules. Consumers must still order clock changes, DMCUB reset/boot/mailbox setup, interrupt acknowledgement, writeback setup, HDA stream/endpoint programming, hubbub watermark programming, VM/page-table setup, plane flips, cursor updates, and power transitions correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware state in DCN 4.1.0 registers:

- Clock and timing state for DISPCLK, DPPCLK, DSCCLK, DP stream clocks, HDMI stream/char clocks, PHY symbol clocks, OTG pixel rates, time-base dividers, and VSYNC latch/counter values.
- Firmware-controller state for DMCUB boot, reset, mailbox windows, ring pointers, scratch registers, GPINT command/response registers, timer registers, and instruction/data/undefined-address fault registers.
- Interrupt routing and status state for display, DCCG, DMU, DCPG, DCHUB, MMHUBBUB, DPP, MPC, OPP, OPTC/OTG, DIG, I2C/DDC/HPD, HDCP, DIO/DCIO, AZ, AUX, DSC, HPO, and DMCUB interrupt destinations.
- Writeback and color-pipeline state for frame capture geometry, flow control, CRC, overflow, gamut remap, HDR multiplier, and output gamma LUT/RAM programming.
- Audio state for Azalia clocking, DMA, payload capability, CRC, stream index/data windows, endpoint index/data windows, root codec identity/capabilities, and hotplug-facing audio connectivity.
- Memory and hub state for MMHUBBUB/MCIF arbitration, warmup, memory-power controls, DCHUBBUB watermarks, urgent bandwidth, self-refresh, P-state change handling, VM page-table contexts, fault reporting, and HUBP/HUBPREQ surface, flip, cursor, prefetch, TTU, MALL, cache, and power registers.

Persistence is hardware-defined. Configuration fields generally survive until modeset reprogramming, power-gating, DMCUB reset, suspend/resume restore, driver reset, or ASIC reset. Status, counter, pointer, interrupt, and fault fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while related clocks and power domains are active. This generated header does not encode those access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 4.1.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h`, which provides the matching field shifts and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c`, which includes this header and builds `dmub_srv_dcn401_regs` for DMCUB reset, boot windows, mailboxes, GPINT, timer, diagnostics, and register inbox/outbox access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, which includes this header for DCN401 clock-manager register tables and uses the `DENTIST_DISPCLK_CNTL`, DCCG, DTO, and related clock-control offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` and `.h`, which include or consume DCN401 register-list macros for resource construction, hubbub, audio, timing, and related display blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn401`, `dc/hubp/dcn401`, `dc/gpio/dcn401`, `dc/irq/dcn401`, and related DCN401 modules that rely on these symbolic offsets through block-specific register tables.

The most direct behavioral integrations from this exact chunk are DCN401 display clock programming, DMUB firmware control/mailboxes, display interrupt routing, display writeback, HDMI/DP audio controller access, hubbub watermark/VM programming, and the first two HUBP/HUBPREQ plane-fetch instances.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong offset or `_BASE_IDX` can compile cleanly while directing `REG_*` helpers to the wrong MMIO address.
- The file is generated metadata. Manual edits can diverge from the authoritative AMD register database, the paired shift/mask header, firmware expectations, and silicon documentation.
- `_BASE_IDX` is as important as the offset. DCCG entries in this chunk use segment index `1`; most later entries use segment index `2`. Mixing these produces plausible-looking but wrong physical addresses.
- The chunk contains a visible formatting anomaly on `regPHYPLLE_PIXCLK_RESYNC_CNTL_BASE_IDX`, where the line has an extra trailing `1`. Because the macro replacement still begins with `1`, this may compile if only used in simple numeric contexts, but it is a generator-quality signal worth checking against the authoritative source.
- Repeated instances can hide one-off errors. AZF0 stream/endpoint windows, VM contexts, OTG clock controls, and HUBP/HUBPREQ instances are mostly mechanical, so one working instance does not prove all sibling offsets are correct.
- The chunk boundary is artificial. It ends inside the `HUBPRET1` block, so whole-file conclusions about all HUBP/HUBPRET instances require later chunks.
- DMCUB mailbox, GPINT, scratch, reset, and fault registers are sequencing-sensitive. Incorrect offsets can cause firmware boot failures, stuck waits, missed responses, or writes into unrelated display registers.
- Hubbub watermark, VM, and HUBPREQ address/prefetch registers are bandwidth- and memory-safety-sensitive. Wrong offsets can manifest as underflow, black frames, page faults, memory corruption symptoms, or resume-only failures.
- Audio and writeback registers are interoperability-sensitive. Wrong Azalia stream/endpoint, DMA, payload, or CRC offsets can produce silent HDMI/DP audio, hotplug issues, bad format changes, or broken capture/writeback diagnostics.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support with DCN401 enabled. Missing or renamed macros should fail in DCN401 DMUB, clock-manager, GPIO, IRQ, hubbub, hubp, and resource register-table construction.
- Mechanically verify that every non-`_BASE_IDX` `reg...` macro in lines 1-2613 has a matching `_BASE_IDX` macro in the same chunk, except for the final artificial boundary where `regHUBPRET1_HUBPRET_READ_LINE0` appears without its `_BASE_IDX` before line 2614.
- Compare this range against AMD's authoritative DCN 4.1.0 register database and nearby generated headers such as `dcn_4_2_0_offset.h` where compatible blocks should retain expected offsets or only have documented deltas.
- Exercise DCN401 hardware through boot, modeset, hotplug, suspend/resume, display clock changes, DMCUB reset/boot, mailbox traffic, GPINT command/response, and display interrupt handling.
- Validate hubbub/HUBP behavior with multiple planes, cursor updates, flips, VM-enabled surfaces, MALL/cache paths, prefetch pressure, P-state changes, and low-power memory states; watch for underflow, VM fault, stale surface-in-use, or blanking glitches.
- Validate HDMI/DP audio across plug/unplug, stream enable/disable, format changes, multichannel and HBR formats, and suspend/resume; watch for HDA timeouts, bad endpoint index/data access, missing hotplug responses, or silent audio.
- Validate display writeback by enabling DWB, checking CRC/debug/overflow counters, and confirming output geometry/color programming survives clock and power transitions.

## Cross-Chunk Notes

This is the first chunk of `dcn_4_1_0_offset.h`. Later chunks continue `HUBPRET1` and then cover additional DCN 4.1.0 display, plane, timing, link, compression, audio indexed-register, and other register namespaces. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 4.1.0 registers or all repeated block instances.

### subset-b-002145: lines 2614-5117

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 2614-5117

## Purpose

This chunk is a generated AMD DCN 4.1.0 register-offset slice. It contains no executable logic; it exports C preprocessor constants mapping display-controller register names to MMIO register offsets, plus matching `<register>_BASE_IDX` constants used by DCN register-helper macros to select the correct base segment. The companion `dcn_4_1_0_sh_mask.h` file supplies field shifts and masks; this chunk supplies the address side of those register accesses.

The requested range contains 2,395 `#define` entries: 1,197 register-offset definitions and 1,198 `_BASE_IDX` definitions, organized under 28 address-block comments. The slice starts in the middle of the `HUBPRET1` register group and ends in the early `CM3` color-management group, so both boundaries are chunking artifacts rather than complete hardware-block boundaries.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It is not Ceph or distributed-filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this range. The public interface is the generated macro namespace:

- `reg<REGISTER>` expands to the register's DCN 4.1.0 offset value.
- `reg<REGISTER>_BASE_IDX` expands to the base segment index, almost always `2` in this chunk.
- Address-block comments document the generated hardware block name and the block-local base address used by the generator.

Important register families in this chunk are:

- Tail of `HUBPRET1_*`: read-line registers for HUBP1/HUBPRET1, including read-line slots, interrupt, read-line value, and read-line status.
- `CURSOR0_1_*`: cursor and DMDATA registers for the cursor block attached to HUBP1, including cursor control, surface address high/low, size, position, hot spot, stereo control, destination offset, cursor memory power control/status, dynamic metadata address/control/QoS/status/software registers, and HUBP 3D LUT address/control/DLG registers.
- `HUBP2_*` and `HUBP3_*`: display HUBP surface configuration, address/tiling configuration, primary/secondary viewport start and dimensions, request-size configuration, HUBP clock/control, VMPG, MALL, MCACHE ID, debug, measure-window, and MALL status registers for HUBP instances 2 and 3.
- `HUBPREQ2_*` and `HUBPREQ3_*`: surface pitch, VMID, primary/secondary surface address high/low for luma/chroma planes, surface/flip control, surface flip interrupt, in-use and earliest-in-use addresses, TTU/QoS controls, VM aperture and fault/default controls, cursor settings, display page table base, VM context, pstate force, and prefetch/deadline/per-channel delivery registers for HUBPREQ instances 2 and 3.
- `HUBPRET2_*` and `HUBPRET3_*`: HUBP vblank/read-line interrupt and status registers for instances 2 and 3.
- `CURSOR0_2_*` and `CURSOR0_3_*`: cursor/DMDATA/HUBP 3D LUT registers for HUBP instances 2 and 3, mirroring the `CURSOR0_1_*` shape.
- `CNVC_CFG0_*` through `CNVC_CFG3_*`: DPP converter configuration for DPP0-DPP3, covering surface pixel format, format control, floating-point format scale/bias, color keying, alpha LUT, pre-dealpha, pre-CSC matrix coefficients for main and B paths, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0_*` through `CNVC_CUR3_*`: converter cursor overlay registers for DPP0-DPP3, including cursor control, color registers, and cursor floating-point scale/bias.
- `DSCL0_*` through `DSCL3_*`: DPP scaler registers for DPP0-DPP3, including coefficient RAM, scaler mode, tap control, manual replication, horizontal/vertical ratios, chroma ratios, initial phases, black color, update/autocal, overscan, OTG blanking, recout/MPC size, line-buffer format and memory controls, DSCL/OBUF memory power, EASF/scaler matrix controls, ring-estimation controls, BF/PWL segments, iSharp controls, and iSharp LUT memory power.
- `CM0_*`, `CM1_*`, `CM2_*`, and beginning of `CM3_*`: DPP color-management registers for post-CSC, post-CSC B path, bias, gamma-correction control, gamut remap coefficients, gamma LUT index/data/control, gamma RAM A/B start/end/slope/base/offset/region metadata, HDR multiplier, memory power, coefficient format, dealpha, debug index/data, and DPP CRC. The range ends after `regCM3_CM_GAMCOR_CONTROL`.
- `DPP_TOP0_*` through `DPP_TOP2_*`: DPP top-level control, clock control, debug, CRC control/value, output buffer memory control, DISPCLK current count, shared memory power, and DSC memory power controls for DPP0-DPP2. DPP3 top-level registers are outside this chunk.

The macro families are mechanically repeated by instance. For example, DPP0 at base address `0x0`, DPP1 at `0x5ac`, DPP2 at `0xb58`, and DPP3 at `0x1104` expose nearly the same CNVC, cursor, DSCL, and CM register names with different numeric suffixes.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this generated header:

1. DCN 4.1.0 consumers include `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`.
2. Register-list macros token-paste names such as `regHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS` and `regHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS_BASE_IDX`.
3. Helper macros add the selected base segment to the generated offset, producing absolute MMIO addresses stored in per-block register tables.
4. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers combine this offset table with shift/mask definitions from the companion header.

The macros do not encode ordering. Consumers still need to program HUBP surfaces, cursor memory, DPP format conversion, scaler ratios/taps, color-management LUTs, CRC, interrupts, memory-power state, and flip/deadline state in the hardware-defined sequence and update window.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It names hardware-visible registers whose values live in DCN display hardware:

- HUBP surface and viewport state for scanout address, tiling, pitch, VMID, primary/secondary plane addresses, in-use and earliest-in-use latches, MCACHE/MALL/VMPG behavior, and request sizing.
- HUBPREQ state for surface flips, TTU/QoS, VM apertures, page-table base, VM context, pstate forcing, cursor request settings, and deadline/prefetch delivery parameters.
- HUBPRET state for vblank and read-line interrupt timing/status.
- Cursor state for enablement, mode, address, dimensions, position, hot spot, stereo, destination offset, DMDATA, memory-power state, and HUBP-attached 3D LUT access.
- DPP converter state for pixel format, alpha/dealpha/realpha, color keying, pre-CSC, pre-degamma, and cursor overlay color/scale/bias.
- DSCL state for filter coefficients, scaler mode, taps, phase/ratio programming, overscan, recout/MPC size, line-buffer behavior, DSCL/OBUF memory power, EASF, BF/PWL, and iSharp controls.
- CM state for post-CSC, gamut remap, gamma RAM A/B programming, LUT access, HDR multiplier, dealpha, coefficient format, debug, memory power, and DPP CRC.
- DPP top-level state for control, clock/debug, CRC capture, output buffer memory, shared memory power, and DSC memory power.

Persistence is hardware-defined. Configuration fields generally remain until a modeset, plane update, pipe reset, power-gating transition, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, CRC, debug, in-use, earliest-in-use, memory-power-status, and counter-like fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the owning pipe and clocks are enabled. This offset header does not describe access semantics; those rules must come from silicon documentation and block-specific driver code.

## Dependencies And Integration Points

This generated header must stay synchronized with AMD's DCN 4.1.0 register database and the companion shift/mask header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h` provides matching field masks and shifts.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c` includes both generated headers and builds DMUB register/field tables through `REG_OFFSET_EXP`, `FD_MASK`, and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c` includes both headers and uses token-pasted `SRI`/`SRI_DMUB` forms to construct IRQ source register addresses and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` includes both headers and defines `SR`, `SRI`, `SRI_ARR`, `SRII`, and related macros that expand these generated names into resource-pool register tables. The same file references `DPP_TOP0_DPP_CRC_*` registers from this chunk in the hardware-sequencer register list.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.c`, `hw_factory_dcn401.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c` include the generated headers for DCN 4.1.0 GPIO and clock-manager register access.
- Shared AMD display block implementations for HUBP, DPP, DSCL, cursor, color management, IRQ, DMUB, hardware sequencing, and register helpers consume these constants through generated register-list macros rather than manually spelling most offsets at call sites.

The most direct behavioral integration from this slice is plane scanout and pixel processing for HUBP instances 1-3 and DPP instances 0-3: surface flips, cursor programming, scaling, color conversion, gamma/gamut programming, CRC/debug, MALL/MCACHE interaction, VM page-table programming, and power/memory state management.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset or base index can compile successfully while reading or writing the wrong MMIO register.
- The file is generated. Manual edits risk diverging from the authoritative register database, matching shift/mask definitions, firmware assumptions, and silicon documentation.
- Chunk boundaries are not semantic. The first complete offset in this range is `regHUBPRET1_HUBPRET_READ_LINE1`, but the preceding `HUBPRET1_HUBPRET_READ_LINE0` offset appears before line 2614 while its `_BASE_IDX` appears in this chunk. The range ends at `regCM3_CM_GAMCOR_CONTROL`, with most CM3 registers continuing in the next chunk.
- Repeated HUBP/HUBPREQ/HUBPRET/CURSOR/DPP instance layouts make generator drift hard to catch. DPP0 or HUBP2 working does not prove DPP1-DPP3 or HUBP3 offsets are correct.
- Base-index mistakes are especially high impact. Consumers add `ctx->dcn_reg_offsets[BASE_IDX]` or a compiled base segment to the offset; an incorrect `_BASE_IDX` can move otherwise correct register offsets into the wrong MMIO segment.
- Surface address, pitch, VM, page-table, aperture, and flip registers are scanout-critical. Bad offsets can lead to blank displays, page faults, stale flips, incorrect in-use latches, invalid memory fetches, or display underflow.
- Cursor address, size, position, hot-spot, stereo, and DMDATA offsets are user-visible and frequently updated. Errors can cause missing cursors, corruption, hot-spot mismatch, stereo placement bugs, or metadata delivery failures.
- DSCL ratio, tap, coefficient RAM, phase, line-buffer, EASF, BF/PWL, and iSharp offsets are precision-sensitive. A small mapping error can show up as blur, ringing, chroma displacement, crop mistakes, or scaler memory-power failures.
- CM, CSC, gamut, gamma RAM, HDR multiplier, and coefficient-format offsets affect color correctness. Regressions may be subtle and missed by simple modeset or boot tests.
- Interrupt/status/ack, CRC/debug, memory-power, and pstate-force registers can have side effects. Confusing a status, clear, enable, or power-control register can cause interrupt storms, missed vblank/read-line events, stuck power state, bad CRC reads, or resume-only failures.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.1.0 hardware behavior:

- Build AMDGPU display with DCN 4.1.0/DCN401 enabled. Missing or renamed constants should fail in DMUB, IRQ, GPIO, clock-manager, resource, hardware-sequencer, HUBP, DPP, or register-table construction.
- Mechanically compare this range against AMD's authoritative DCN 4.1.0 register source and the adjacent `dcn_4_1_0_sh_mask.h` names. Verify that each complete register group has both an offset and a `_BASE_IDX`, allowing for the artificial chunk boundaries.
- Check that repeated instance families preserve expected stride/base patterns: HUBP/HUBPREQ/HUBPRET/CURSOR instances around `0x370`, `0x6e0`, and `0xa50`, and DPP instances around `0x0`, `0x5ac`, `0xb58`, and `0x1104`.
- Exercise plane enable/disable, primary/secondary surface flips, viewport changes, tiling/pitch variants, VMID/page-table changes, MALL/MCACHE paths, pstate-force paths, suspend/resume, and rapid modesets.
- Exercise cursor enable/disable, movement, hotspot changes, size and pitch changes, stereo cursor modes, DMDATA programming, cursor memory power, and 3D LUT cursor-adjacent paths for pipes 1-3.
- Exercise scaler paths across identity scale, up/downscale, fractional scaling, chroma formats, overscan, recout changes, line-buffer pressure, coefficient RAM reload, EASF/BF/iSharp controls, and DSCL/OBUF memory-power transitions.
- Validate color paths with CRC or visual/color tests for pre-CSC, post-CSC, gamut remap, gamma correction RAM A/B, HDR multipliers, alpha/dealpha/realpha, color keying, and pixel-format conversion across DPP0-DPP3.
- Watch kernel logs and display diagnostics for page faults, underflows, stuck flips, missed vblank/read-line interrupts, cursor corruption, scaler artifacts, CRC mismatches, color regressions, memory-power transition failures, and resume-only display artifacts.

## Cross-Chunk Notes

The previous chunk contains the beginning of the `HUBPRET1` read-line group. The next chunk continues the `CM3` color-management register set after `CM3_CM_GAMCOR_CONTROL`. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 4.1.0 register offsets or all HUBP/DPP instances.

### subset-b-002146: lines 5118-7579

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 5118-7579

## Scope

This chunk is a middle slice of AMDGPU's generated DCN 4.1.0 register-offset header. It contains preprocessor constants only: no functions, structs, enums, storage objects, or local executable control flow. Each exported pair follows the generated register contract: `reg<INSTANCE>_<REGISTER>` gives the register offset and `reg<INSTANCE>_<REGISTER>_BASE_IDX` gives the register-base table index used by AMD display register helpers.

The range starts inside the DPP3 color-management block, at the gamma-correction LUT and RAM A/B region descriptors for `CM3`. It then covers the DPP3 top block, four MPCC blend-tree instances, MPC global configuration, four MPCC output-gamma (`MPCC_OGAM`) instances, and most of four MPCC movable color-management (`MPCC_MCM`) instances. It ends inside `MPCC_MCM3`, after the first three registers of the second gamut-remap matrix, so the following chunk owns the tail of `MPCC_MCM3` and the later MPC output CSC blocks.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, network, or persistent-disk behavior.

## Purpose

The purpose of this header range is to bind DCN 4.1.0 display-driver logical register names to ASIC-specific MMIO offsets. Runtime DCN401 code constructs register tables from these constants, then uses common `REG_*` helpers to program display pipe color, blending, timing-independent MPC routing, and diagnostics.

The covered hardware areas are:

- Tail of `dcn_dcec_dpp3_dispdec_cm_dispdec`: DPP3 `CM_GAMCOR` indexed LUT access, RAM A/B PWL region configuration, HDR multiplier, CM memory-power status/control, dealpha, coefficient format, and CM test-debug ports.
- `dcn_dcec_dpp3_dispdec_dpp_top_dispdec`: DPP3 top-level control, soft reset, CRC readback/control, and host-read throttling.
- `dcn_dcec_mpc_mpcc0_dispdec` through `mpcc3`: four MPCC blender slices, each with top/bottom selection, OPP routing, MPCC control/state-machine control, update-lock selection, alpha/multiplier controls, background color, clamping, memory-power control, movable-CM location, and MPCC debug index/data registers.
- `dcn_dcec_mpc_mpc_cfg_dispdec`: global MPC and HUBP routing/configuration registers, including `MPC_CONTROL`, mux mapping, active-size and memory power controls, clock-gating controls, CRC controls, output mux diagnostics, OUT handshake/status, MPCC request/init state, and per-HUBP output mux selectors.
- `dcn_dcec_mpc_mpcc_ogam0_dispdec` through `mpcc_ogam3`: four MPCC output-gamma/color-remap blocks, each with OGAM control, LUT index/data/control, RAM A/B PWL region descriptors, gamut-remap coefficient format/mode, matrix coefficient banks A/B, memory power, and test-debug ports.
- `dcn_dcec_mpc_mpcc_mcm0_dispdec` through `mpcc_mcm3`: four movable color-management blocks, each with shaper LUT control, shaper offset/scale/index/data/write-enable controls, RAM A/B PWL descriptors, 3DLUT mode/read-write/LUT data/control, 1DLUT control/index/data/RAM A/B descriptors, first and second gamut-remap coefficient formats/modes, matrix banks A/B, memory power, and 3DLUT fast-load select/status registers. The `MPCC_MCM3` second-remap list is incomplete in this chunk.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro namespace:

- `regCM3_*` offsets use base index `2`, matching the DPP/CM register-base group for the fourth DPP instance.
- `regDPP_TOP3_*` offsets also use base index `2`, matching DPP3 top-level registers.
- `regMPCC0_*` through `regMPCC3_*`, `regMPC_*`, `regHUBP*_MPC_OUT_MUX`, `regMPCC_OGAM*_*`, and `regMPCC_MCM*_*` use base index `3`, matching the MPC/MPCC register-base group.

The visible macro families are table-driven. Resource headers paste logical names onto these instance names through macros such as `SRI_ARR`, `SRII`, and `SRI`, while field-table macros from the companion `dcn_4_1_0_sh_mask.h` provide masks and shifts for the same register names.

Important register groups in this slice include:

- `regCM3_CM_GAMCOR_LUT_INDEX`, `regCM3_CM_GAMCOR_LUT_DATA`, and `regCM3_CM_GAMCOR_LUT_CONTROL`: indexed DPP3 gamma LUT programming ports.
- `regCM3_CM_GAMCOR_RAMA_*` and `regCM3_CM_GAMCOR_RAMB_*`: DPP3 gamma PWL RAM A/B start, slope, base, end, offset, and region-pair registers.
- `regDPP_TOP3_DPP_CONTROL`, `regDPP_TOP3_DPP_SOFT_RESET`, `regDPP_TOP3_DPP_CRC_*`, and `regDPP_TOP3_HOST_READ_CONTROL`: top-level DPP3 enable/reset/CRC/read controls.
- `regMPCC{0..3}_MPCC_TOP_SEL`, `BOT_SEL`, `OPP_ID`, `CONTROL`, `SM_CONTROL`, `UPDATE_LOCK_SEL`, `ALPHA_*`, `BG_*`, `MEM_PWR_CTRL`, and `MOVABLE_CM_LOCATION_CONTROL`: MPCC blend graph, plane selection, alpha, background, update synchronization, power, and movable color-management placement.
- `regMPC_*`: global MPC mux, clock-gating, CRC, output, memory-power, MPCC request/init, and HUBP routing controls.
- `regMPCC_OGAM{0..3}_MPCC_OGAM_*` and `regMPCC_OGAM{0..3}_MPC_GAMUT_REMAP_*`: output-gamma LUT/PWL and MPCC OGAM gamut-remap controls.
- `regMPCC_MCM{0..3}_MPCC_MCM_SHAPER_*`, `3DLUT_*`, `1DLUT_*`, `FIRST_GAMUT_REMAP_*`, `SECOND_GAMUT_REMAP_*`, `MEM_PWR_CTRL`, and `3DLUT_FAST_LOAD_*`: movable color-management shaper, 3D LUT, post 1D LUT, dual gamut remap, memory power, and fast-load status controls.

## Control Flow

This header range has no local control flow. Runtime behavior is created by consumers that include `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`, build register tables, then perform MMIO reads and writes through display register helpers.

A typical DCN401 path is:

1. DCN401 resource construction includes the DCN 4.1.0 generated offset and shift/mask headers.
2. Register-list macros expand logical names into instance-specific macros, for example `SRII(MPCC_MCM_FIRST_GAMUT_REMAP_MODE, MPCC_MCM, inst)` expands to `regMPCC_MCM0_MPCC_MCM_FIRST_GAMUT_REMAP_MODE` for instance 0.
3. The generated offsets are stored in DCN401 register structures such as `dcn401_mpc_registers`, while field shifts/masks are stored in matching shift/mask structures.
4. Runtime code calls helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, and `REG_GET_3`; those helpers combine the register offset from this header with field masks/shifts from the companion header.
5. Higher-level display code sequences the actual hardware programming around modeset, plane composition, color-management updates, LUT loading, update locks, blanking, memory power, and hardware initialization.

Concrete visible consumers include `display/dc/resource/dcn401/dcn401_resource.h`, which lists DPP `CM_GAMCOR_*` registers and MPC/MPCC register arrays; `display/dc/mpc/dcn401/dcn401_mpc.h`, which defines DCN401 MPC register arrays and field lists for `MPCC_MCM_*` features; `display/dc/mpc/dcn401/dcn401_mpc.c`, which programs 3DLUT fast-load select/status, shaper/3DLUT/1DLUT modes, and MPCC MCM gamut-remap matrices; and `display/dc/hwss/dcn401/dcn401_hwseq.c`, which programs first/second MCM gamut remap and OGAM gamut remap during pipe color setup.

## State And Persistence Behavior

The file itself stores no runtime state and persists nothing. It describes hardware register state whose lifetime is controlled by display hardware programming, pipe enable/disable, modesets, power transitions, suspend/resume, and GPU reset.

State represented by this chunk includes:

- DPP3 CM gamma state: indexed LUT position/data/control, RAM A/B PWL region descriptors, HDR multiplier, coefficient format, dealpha, and CM memory-power state.
- DPP3 top state: DPP enable/control, soft-reset state, CRC capture/readback state, and host-read control.
- MPCC composition state: top/bottom source selection, OPP assignment, alpha and multiplier controls, blend state-machine control, update-lock binding, background colors, clamp limits, memory-power control, debug index/data, and movable color-management placement.
- MPC global state: mux mappings, active dimensions, stereo mux, global/3D LUT memory power, CRC selection and readback, clock-gating controls, output mux and handshake status, MPCC request/init controls, and HUBP-to-MPC-output routing.
- MPCC OGAM state: per-MPCC output gamma LUTs, RAM A/B PWL descriptors, color-remap matrix banks, mode/current-mode selection, memory power, and debug ports.
- MPCC MCM state: shaper LUTs, 3DLUT contents/mode/read-write selection, 1DLUT contents and bank selection, dual gamut remap matrices, memory-power controls, and 3DLUT fast-load select/status.

Indexed and banked LUT registers are particularly stateful. The `*_LUT_INDEX`, `*_LUT_DATA`, read/write control, bank-select, and RAM A/B descriptor registers together determine which table entries are modified and which table bank is active. Bad ordering or wrong offsets can leave a valid-looking but visually incorrect LUT bank programmed.

Many state bits are live hardware controls rather than passive descriptors. MPCC muxing, OPP IDs, movable-CM placement, memory-power controls, and gamut-remap mode selections directly affect scanout composition or block availability until reprogrammed or reset.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h`, which supplies the field masks and shifts for these offsets. The offset and shift/mask headers must be paired for DCN 4.1.0/DCN401; nearby DCN 3.x, DCN 4.2, or other generated headers may share names but are not interchangeable.

Important integration points are:

- `display/dc/resource/dcn401/dcn401_resource.h`: declares the runtime register lists that pull in `CM_GAMCOR_*`, MPCC, MPC, OGAM, and MCM register offsets from this generated header.
- `display/dc/resource/dcn401/dcn401_resource.c`: constructs the DCN401 resource pool and binds register tables used by display pipes and MPC.
- `display/dc/dpp/dcn401/dcn401_dpp.h`: maps DPP color-management fields such as `CM_GAMCOR_LUT_*` onto generated DCN 4.1.0 names.
- `display/dc/dpp/dcn30/dcn30_dpp_cm.c`: common DPP color-management code programs `CM_GAMCOR_LUT_INDEX`, `CM_GAMCOR_LUT_DATA`, and `CM_GAMCOR_LUT_CONTROL`; for DCN401, the register table resolves those logical operations to offsets like the DPP3 `CM3` macros in this chunk.
- `display/dc/mpc/dcn401/dcn401_mpc.h` and `display/dc/mpc/dcn401/dcn401_mpc.c`: define and use the DCN401 MPC register arrays for MPCC MCM gamut remap, LUT modes, 3DLUT fast-load select/status, and banked LUT controls.
- `display/dc/hwss/dcn401/dcn401_hwseq.c`: sequences pipe-level gamut-remap setup by calling MPC functions for `MPCC_MCM_FIRST_GAMUT_REMAP`, `MPCC_MCM_SECOND_GAMUT_REMAP`, and `MPCC_OGAM_GAMUT_REMAP`.
- `display/dmub/src/dmub_dcn401.c` and `display/dmub/src/dmub_dcn401.h`: include the same generated DCN 4.1.0 headers for DMUB register programming, though this particular chunk is mostly display-pipe/MPC color and routing rather than mailbox registers.

The chunk also depends on AMD display common infrastructure: `reg_helper.h` for MMIO helper macros, `dcn10_cm_common.h`/`dcn30_cm_common.h` color-matrix and LUT helpers, DC plane/stream color state, and hardware sequencing code that decides when it is safe to update color or composition registers.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong offset or base index compiles cleanly but can target the wrong register, wrong instance, or wrong base aperture. Symptoms may look like sequencing, color, or power bugs rather than a generated-header issue.

Chunk-boundary risk is high here. The chunk starts after the beginning of the `CM3` block, so whole-DPP3 CM conclusions require the previous chunk. It also ends in the middle of `MPCC_MCM3` second gamut-remap registers, so whole-MCM3 and MPC-output conclusions require the following chunk.

Instance alignment is critical. `CM3`/`DPP_TOP3` offsets use base index `2`, while MPC/MPCC/OGAM/MCM offsets use base index `3`. Mixing the base index or copying offsets across instances can direct a register helper to a different block even when the logical register name looks correct.

Color-management registers are precision-sensitive. Gamma PWL regions, shaper LUTs, 1DLUTs, 3DLUTs, HDR multiplier, coefficient-format registers, and dual gamut-remap matrices directly affect output color. Errors can cause color shifts, banding, broken HDR/gamut transforms, or LUT updates that appear to succeed but select the wrong bank.

Composition and routing fields can blank or corrupt scanout. MPCC top/bottom selection, OPP ID, alpha/multiplier controls, MPC mux controls, HUBP output mux controls, and movable-CM location must match the pipe topology chosen by resource and hardware-sequencing code.

Power controls are hazardous. `CM_MEM_PWR_CTRL`, `MPCC_MEM_PWR_CTRL`, `MPC_*MEM_PWR*`, `MPCC_OGAM_MEM_PWR_CTRL`, and `MPCC_MCM_MEM_PWR_CTRL` interact with low-power modes and active display blocks. Incorrect offsets can power down memories while active, prevent blocks from idling, or produce stuck status bits.

Fast-load and status registers can hide data integrity problems. `MPCC_MCM_3DLUT_FAST_LOAD_SELECT` chooses a HUBP source for fast loading, while status reports done/underflow conditions. Wrong offsets or masks can report success while the intended 3DLUT bank was not populated correctly.

Debug and CRC registers are diagnostic-sensitive. Bad constants for CRC, OUT mux, handshake, init status, and test-debug registers may not break normal display output but can mislead validation, hardware bring-up, and failure triage.

## Test Signals

Useful validation is generated-header, build, and hardware-behavior oriented:

- Compile coverage for DCN401 resource construction, DPP color management, MPC/MPCC code, hardware sequencing, and DMUB users that include the DCN 4.1.0 generated headers.
- Generated-register consistency checks that every register referenced by `dcn401_resource.h` and `dcn401_mpc.h` exists in `dcn_4_1_0_offset.h`, has the expected `*_BASE_IDX`, and has matching fields in `dcn_4_1_0_sh_mask.h`.
- Cross-generation or database diffing against AMD's authoritative DCN 4.1.0 register database, with expected differences from DCN 3.2/3.5 and DCN 4.2 reviewed explicitly.
- DPP3 tests for gamma LUT programming/readback, PWL RAM A/B selection, HDR multiplier, dealpha, coefficient format, CM memory power, DPP soft reset, CRC capture, and host reads.
- MPCC composition tests for multi-plane blending, top/bottom tree selection, OPP routing, per-plane alpha, global alpha/multipliers, background color, update locks, clamp behavior, and movable-CM placement.
- MPC routing tests for HUBP-to-MPC output muxing, MPCC request/init state, active-size programming, output mux status, stereo mux, memory power, and CRC paths.
- OGAM tests for output gamma LUT loading, RAM A/B bank switching, gamut remap banks A/B, mode/current-mode readback, memory power, and debug-port accessibility across MPCC0-3.
- MCM tests for shaper LUT, 3DLUT 9x9x9/17x17x17 modes, 1DLUT, first and second gamut remap, fast-load select/status, memory low-power transitions, bank switching, and restore after suspend/resume or GPU reset.
- End-to-end visual tests for SDR/HDR, ICC/gamut remap, color temperature matrices, plane color transforms, scaled/rotated planes, multi-plane overlays, cursor interactions, and hotplug/modeset transitions on DCN401 hardware.

Regression symptoms from bad constants include blank output, wrong plane routing, blend errors, incorrect alpha, visible color shifts, banding, HDR or gamut failures, stuck update locks, failed memory-power transitions, incorrect CRC/readback/debug data, false 3DLUT fast-load success, or failures isolated to the fourth DPP/MPCC instances.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dcn_4_1_0_offset.h`. The previous chunk owns the start of DPP3 `CM3` and DSCL3 context before line 5118. The following chunk owns the rest of `MPCC_MCM3` and later MPC output CSC/register blocks after line 7579. The merge/reconciliation lane should treat this document as the DPP3 CM tail plus DPP3 top, MPCC0-3, MPC config, MPCC OGAM0-3, and most of MPCC MCM0-3 for the full DCN 4.1.0 offset contract.

### subset-b-002147: lines 7580-10140

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 7580-10140

## Purpose

This chunk is a generated AMD DCN 4.1.0 display-controller register-offset slice. It contains no executable C logic; it exports C preprocessor constants that map symbolic register names to MMIO register offsets and companion `_BASE_IDX` values used by AMDGPU display register helper tables.

The requested range contains 2,388 `#define` entries. Each hardware register normally appears as a pair: `reg...` for the offset and `reg..._BASE_IDX` for the register base index. The slice starts in the middle of MPCC MCM3 color-management definitions, covers MPC output color-space conversion, OPP/ABM/format/output-pipe/timing/DIO register blocks for instances 0 through 3 or 0 through 1 depending on the block, and ends in the middle of the `DP2` DisplayPort encoder register block. The line boundaries are therefore artificial chunk boundaries rather than complete hardware-block boundaries.

Although this file is under a local `ceph-client` source mirror, this chunk is AMDGPU DCN display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or direct I/O operations in this range. The public interface is the generated macro naming convention:

- `reg<block>_<REGISTER>`: register offset used by AMD display MMIO helpers.
- `reg<block>_<REGISTER>_BASE_IDX`: base-index selector used with generated register tables to choose the correct address aperture/base for the register.

The main register families in this chunk are:

- `MPCC_MCM3_*`: tail of MPCC MCM instance 3 color-management offsets, including second gamut-remap coefficients, MCM memory power control, and 3D LUT fast-load select/status.
- `MPC_OUT0` through `MPC_OUT3` plus `MPC_OCSC_*`: MPC output mux, denormalization clamp/control, output CSC coefficient format, per-output CSC modes, A/B coefficient banks, and OCSC debug index/data.
- `ABM0` through `ABM3`: adaptive backlight management and BL1 PWM offsets for ambient light, user level, target/current ABM level, duty-cycle bounds, sample-rate/update controls, register locks, histogram controls/data, luminance controls, debug/status, and master lock registers.
- `DPG0` through `DPG3`: display pattern generator control, dimensions, offset, background color, test pattern color, ramp, and status offsets.
- `FMT0` through `FMT3`: output formatter clamp, dynamic expansion, bit-depth control, dithering/randomization, temporal dither pattern, memory power, CRC, debug, and 4:2:2 control offsets.
- `OPPBUF0` through `OPPBUF3`, `OPP_PIPE0` through `OPP_PIPE3`, and `OPP_PIPE_CRC0` through `OPP_PIPE_CRC3`: output-pipe buffer, pipe control, and per-pipe CRC control/result offsets.
- `DSCRM0` through `DSCRM3`: DSC stream/forwarding configuration offsets.
- `OPP_TOP_*` and `OPP_ABM_CONTROL`: top-level OPP clock and ABM coordination offsets.
- `ODM0` through `ODM3`: OPTC input/global and output-data-mapping control offsets, including memory power, debug bus, double-buffer control, and spare register offsets.
- `OTG0` through `OTG3`: timing-generator offsets for horizontal/vertical totals, sync, blanking, border, interrupt controls, vline/vupdate/vready/state, stereo, 3D structure, CRC, test pattern, global swap lock, vertical count, frame count, manual flow control, static-screen, double-buffer, trigger, underflow, and spare registers.
- `OPTC`/`GSL` miscellaneous offsets: global swap-lock source selection, timing control, underflow controls, OTG clock-control/status, and miscellaneous spare registers.
- `DP0` and `DP1`: complete DisplayPort link/stream offsets for each DIO DP block in this slice, including link control, pixel format, MSA, stream enable, DPHY training/symbol/CRC/fast-training, transfer-unit control, secondary-data/audio packet controls, MST/MSE controls, ALPM, stream/link symbol counters, and panel replay control.
- `DIG0` and `DIG1`: digital front-end/back-end, HDMI, audio-format, HDCP/I2C, TMDS, CRC, FIFO, test-pattern, packet-control, ACR, and version offsets.
- `DP2`: beginning of the third DisplayPort block, from `DP_LINK_CNTL` through `DP_DPHY_INTERNAL_CTRL` within this requested slice.

Most families are mechanically repeated across hardware instances with different register offsets. For example, `OTG0` starts at `0x1b2a`, `OTG1` at `0x1baa`, `OTG2` at `0x1c2a`, and `OTG3` at `0x1caa`; `DP0` starts at `0x211e`, `DP1` at `0x2242`, and the partial `DP2` block starts at `0x2366`.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this generated offset header alongside the matching DCN 4.1.0 shift/mask header:

1. DCN 4.1 display components include `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`.
2. Register-list macros token-paste these symbolic register names into per-block register tables for resource construction, IRQ service setup, DMUB register access, clock/gpio helpers, timing generators, encoders, MPC/OPP blocks, and output formatters.
3. Runtime display paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers combine the offsets from this file with masks/shifts from the companion generated header.
4. Hardware sequencing, locking, blanking windows, double-buffering, power transitions, and interrupt handling are controlled by the consumer code and the hardware specification, not by this header.

The macros do not encode programming order. Consumers still need to program timing, output format, color conversion, ABM, DisplayPort/HDMI packets, link training, CRC, and power state in valid hardware sequences.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It names hardware-visible DCN 4.1.0 register state:

- MPC/MPCC color pipeline state for output muxing, denormalization, CSC/gamut-remap coefficient banks, memory power, and LUT fast-load state.
- OPP state for ABM/PWM, pattern generation, output formatting, pipe buffering, DSC forwarding, output CRC, and top-level OPP control.
- OPTC/OTG state for display timing, blanking/sync geometry, interrupt windows, stereo/3D signaling, CRC, test patterns, frame and vertical counters, global swap lock, underflow, and trigger/update behavior.
- DIO state for DisplayPort and HDMI/DIG blocks, including link configuration, stream attributes, main-stream attributes, DPHY training and diagnostics, audio/secondary packets, MST/MSE allocation, ALPM, panel replay, TMDS, HDCP, and ACR timing.

Persistence is hardware-defined. Configuration registers generally remain until modeset, link retraining, plane/stream reprogramming, power-gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, CRC, counter, interrupt, debug, and fast-training registers may be read-only, sticky, write-one-to-clear, self-clearing, clock-gated, or valid only while the relevant display block is powered. This offset header does not describe those access semantics; consumers must rely on the register specification and block-specific driver code.

## Dependencies And Integration Points

This file must stay synchronized with AMD's generated DCN 4.1.0 register database and its companion generated files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h` supplies the matching field shifts and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c` includes the DCN 4.1.0 generated headers for DMUB-facing register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c` includes them for IRQ source setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` includes them while constructing DCN 4.1 display resources and register lists.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.c` and `hw_factory_dcn401.c` include them for GPIO translation/factory behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c` includes them for DCN 4.1 clock-manager register access.

The behavioral integration points represented by this chunk are output composition and scanout after DPP/MPC processing: MPC output color programming, OPP formatting and ABM, timing generation, CRC/test diagnostics, DisplayPort link/stream programming, HDMI/TMDS/DIG packet handling, and display interrupt/status paths.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset or base index can compile cleanly while directing register helpers to the wrong MMIO address.
- The file is generated. Manual edits risk divergence from the authoritative register database, companion shift/mask definitions, firmware expectations, and silicon documentation.
- The chunk boundaries are not semantic. The first definitions continue the `MPCC_MCM3` group that began before line 7580, and the `DP2` block continues after line 10140.
- Repeated instance layouts make generator drift hard to detect. `OTG0` working does not prove `OTG1` through `OTG3` offsets are correct; similarly, `DP0` and `DP1` can diverge independently from the partial `DP2` block.
- Color-management and CSC offsets are precision-sensitive and user-visible. Wrong MPC/MPCC offsets can cause incorrect color conversion, wrong LUT/gamut-remap bank updates, or failed fast-load status polling.
- ABM/PWM offsets affect panel backlight behavior. Mistakes can produce brightness jumps, stuck ABM levels, bad ambient-light response, or failure to respect user brightness limits.
- Timing-generator offsets are display-critical. Wrong OTG total/sync/blanking/update/trigger offsets can cause blank screens, unstable modesets, underflow, missed vblank/vupdate interrupts, bad stereo/3D signaling, or CRC/test-pattern misdiagnosis.
- DIO offsets affect link training and protocol packets. Wrong DP/DIG offsets can break DisplayPort link training, MST/MSE allocation, ALPM, panel replay, HDMI audio/video infoframes, HDCP I2C handling, TMDS output, or audio clock regeneration.
- Status and interrupt registers can have side effects. Confusing a status, clear, acknowledge, or enable register through a bad offset may cause missed interrupts, stuck interrupt status, or interrupt storms.
- Power and clock-gated blocks may reject or drop MMIO accesses if consumers use the offsets outside the required enable sequence; this header cannot protect against those ordering errors.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.1 hardware behavior:

- Build AMDGPU display support with DCN 4.1 enabled. Missing or renamed constants should fail in DCN401 DMUB, IRQ, resource, GPIO, clock-manager, and display-block register-table construction.
- Mechanically compare this range against AMD's authoritative DCN 4.1.0 register source and the adjacent `dcn_4_1_0_sh_mask.h` names. Treat the start and end of the requested line slice as artificial boundaries.
- Run static checks that each non-`_BASE_IDX` register macro has a corresponding `_BASE_IDX` macro and that repeated instance groups have expected stride/pattern relationships.
- Exercise ABM/backlight paths across user brightness changes, ambient-light updates, panel idle/static-screen transitions, suspend/resume, and rapid modesets.
- Exercise MPC output CSC/gamut remap/LUT fast-load paths with visual color tests or CRC-based validation for multiple pipes and coefficient-bank updates.
- Exercise OPP formatter paths across bit depths, dithering modes, dynamic expansion, 4:2:2 output, output CRC capture, pattern generation, and DSC forwarding.
- Exercise OTG modesets over multiple timings, vblank/vline/vupdate interrupts, stereo/3D modes, test patterns, global swap lock, frame counters, underflow detection, and double-buffered update triggers on OTG0 through OTG3.
- Exercise DisplayPort and HDMI/DIG paths for DP0/DP1 and adjacent DP2 coverage: link training, stream enable/disable, MSA programming, audio/secondary packets, MST/MSE, ALPM, panel replay, HDCP, TMDS, ACR, hotplug, suspend/resume, and link retraining.
- Watch kernel logs and display diagnostics for MMIO register-access failures, missed vblank/update interrupts, underflows, CRC mismatches, link-training failures, audio packet loss, HDCP failures, ABM brightness anomalies, and resume-only display artifacts.

## Cross-Chunk Notes

The previous chunk contains the beginning of the `MPCC_MCM3` color-management register group, including earlier 1D LUT region and first/second gamut-remap definitions. The next chunk continues the `DP2` DisplayPort block after `DP_DPHY_INTERNAL_CTRL`. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 4.1.0 offset definitions, all MPCC instances, or all DIO DP/DIG instances.

### subset-b-002148: lines 10141-12728

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 10141-12728

## Purpose

This chunk is a generated AMD DCN 4.1.0 register-offset table for the display I/O, DisplayPort, auxiliary-channel, hot-plug-detect, DSC, PHY mux, and the first HPO top-level register blocks. It contains no executable functions or C types; its API surface is the C preprocessor contract of `#define reg...` numeric offsets and matching `#define reg..._BASE_IDX` segment selectors.

Within lines 10141-12728 the file defines 1,190 register offset macros and 1,190 paired base-index macros. Most entries use `_BASE_IDX 2`, which is resolved by DCN401 code through `ctx->dcn_reg_offsets[2]` or the compile-time `DCN_BASE__INST0_SEG2` base. The final `HPO_TOP_*` entries use `_BASE_IDX 3`, marking the transition from legacy DIO/DCOH display blocks into HPO address space.

## Hardware Surface

The chunk begins inside the `dcn_dcec_dio_dp2_dispdec` block and then covers these major address blocks:

- `DP2` and `DP3` DisplayPort stream/link encoder registers: link control, pixel format, MSA colorimetry/misc/timing, stream control, steer FIFO, TU control, DPHY training/scrambler/CRC/status, secondary data packets, audio M/N, MST/MSE slots, ALPM, symbol counters, panel replay, MSO, and generalized sideband packet controls.
- `DIG2` and `DIG3` digital encoder front/back-end registers: FE enable/clock/CRC, back-end clock/control/enable, TMDS/HDMI control, HDMI generic/info/audio packet registers, HDMI GCP/ACR/ACR status, AFMT control, HDCP interrupt and I2C controls, and per-DIG version registers.
- `DIG0` through `DIG3` AFMT blocks: audio format control, channel status, infoframe and generic packet controls, 60958/60958 CS values, HBR packetization, audio CRC, VBI packet controls, SPD and HDR metadata packet programming, and double-buffer control.
- `DIG0` through `DIG3` DME and VPG blocks: metadata engine control/status/register set and video packet generator generic packet/header/subpacket controls.
- DIO support blocks: HDCP 1.x/HDCP 2.x control/status, DOUT I2C setup/speed/EDID/multisync/sw-status registers, DIO misc memory-power and clock gating, stream mapper control, and DCIO/uniphy lane/PHY control registers.
- Panel and compression blocks: PWRSEQ0 panel power sequencing/blacklight/PWM/ALPM/thermal-override registers and DSC0-DSC3 DSCC, DSCCIF, and DSC top registers.
- DCOH blocks: top-level DCOH controls, PHY mux0-3 controls, DP_AUX0-3 AUX engines, and HPD0-3 hot-plug interrupt/control/filter registers.
- HPO start: `HPO_TOP_CLOCK_CONTROL` and `HPO_TOP_HW_CONTROL`, both in base index 3.

## APIs, Types, And Macros

The important exported symbols are the generated register macros themselves. Each usable hardware register is represented by two macros:

- `reg<block>_<REGISTER>`: the register's offset within the generated address space, for example `regDP2_DP_TU_CNTL`, `regDIG2_DIG_FE_CNTL`, `regDIG2_TMDS_CNTL`, `regDP_AUX0_AUX_CONTROL`, `regHPD0_DC_HPD_INT_STATUS`, and `regHPO_TOP_CLOCK_CONTROL`.
- `reg<block>_<REGISTER>_BASE_IDX`: the segment selector passed to `BASE(...)`, for example `regDP_AUX0_AUX_CONTROL_BASE_IDX` and `regHPD0_DC_HPD_INT_STATUS_BASE_IDX`.

There are no locally declared structs, enums, inline helpers, or functions in this chunk. Runtime objects such as `aux_engine_regs`, `link_enc_aux_regs`, `link_enc_hpd_regs`, `link_enc_regs`, `stream_enc_regs`, `vpg_regs`, `afmt_regs`, `dsc_regs`, and HPO encoder register tables are populated by other DCN401 source files using the names defined here.

## Control Flow

This header has no runtime control flow. Its control-flow role is compile-time macro expansion:

1. DCN401 source includes `dcn_4_1_0_offset.h` with the paired `dcn_4_1_0_sh_mask.h`.
2. A consumer defines `BASE(seg)` as either `ctx->dcn_reg_offsets[seg]` or a compile-time segment constant such as `DCN_BASE__INST0_SEG2`.
3. Register-list macros expand with helpers such as `SR`, `SRI`, `SRI_ARR`, or `REG`, forming addresses as `BASE(reg..._BASE_IDX) + reg...`.
4. The populated register tables are handed to shared AMD display constructors and access helpers, which later perform MMIO reads/writes through the normal display core paths.

The naming convention is therefore part of the control path: `SRI(DC_HPD_INT_STATUS, HPD, 0)` expands to `regHPD0_DC_HPD_INT_STATUS_BASE_IDX` plus `regHPD0_DC_HPD_INT_STATUS`, while `SRI_ARR(DP_LINK_CNTL, DP, 2)` expands through the `regDP2_*` symbols.

## State And Persistence

The header itself stores no state and persists nothing. It maps symbolic names to hardware MMIO offsets. The persistent state affected by users of this chunk lives in display hardware registers: link training state, HPD interrupt status and acknowledgement bits, AUX transaction control/status, HDMI/DP packet generator configuration, DSC enable/status, panel power sequencing, PHY mux selection, clock gating, memory power control, and HPO top-level clock/hardware controls.

Because some registers are status or acknowledgement registers, incorrect offsets can have lasting runtime effects even though the header is static: HPD interrupts can be missed or left asserted, AUX transactions can time out, link training can program the wrong lane or DPHY block, and display stream/audio metadata can be emitted incorrectly.

## Dependencies And Integration Points

Direct dependencies are limited to the C preprocessor and the generated AMD register-header convention. The functional dependency is the paired shift/mask file, `dcn_4_1_0_sh_mask.h`; offset names here must match bitfield mask and shift names there.

Observed DCN401 integration points include:

- `display/dc/resource/dcn401/dcn401_resource.c` includes this header and uses `BASE(reg..._BASE_IDX) + reg...` in `SR`, `SRI`, and array variants to initialize AUX, I2C, DIO, link encoder, HPD, stream encoder, VPG, AFMT, APG, HPO, DSC, and hardware sequencer register tables.
- `dcn401_aux_engine_create()` initializes four AUX engines from the `DP_AUX0-3` register families before constructing `dce110_aux_engine` instances.
- `dcn401_link_encoder_create()` initializes AUX, HPD, and link encoder register tables, using the `DP_AUX*`, `HPD*`, `DIG*`, `DCIO`, and PHY-related symbols in this chunk for physical connector and link-encoder control.
- `dcn401_stream_encoder_create()`, `dcn401_vpg_create()`, and `dcn401_afmt_create()` map DIO stream encoder instances to the `DIG*`, VPG, and AFMT register families in this chunk.
- `dcn401_hpo_dp_stream_encoder_create()` and `dcn401_hpo_dp_link_encoder_create()` sit at the HPO transition; this chunk contributes `HPO_TOP_*`, while later file chunks continue the HPO stream/link encoder register space.
- `display/dc/irq/dcn401/irq_service_dcn401.c` uses `SRI(DC_HPD_INT_STATUS, HPD, n)` and related HPD control symbols to build HPD and HPD RX interrupt source entries.
- `display/dc/gpio/dcn401/hw_translate_dcn401.c` includes the same generated offset/mask pair for GPIO/HPD/DDC offset translation, although its specific GPIO register names mostly come from earlier parts of the header.
- `display/dmub/src/dmub_dcn401.c`, the DCN401 clock manager, and the GPIO factory also include this header, so generated-symbol compatibility is shared across display core, firmware mailbox, clocks, interrupts, and connector setup.

## Risks

The primary risk is silent hardware misprogramming. These macros are compile-time constants, so an incorrect offset or base index can still compile cleanly while reads and writes target the wrong MMIO register. That is especially dangerous for paired register families where names differ only by instance number, such as `DP2` versus `DP3`, `DIG2` versus `DIG3`, `DP_AUX0-3`, `HPD0-3`, and `DSC0-3`.

Base-index drift is another high-impact risk. Most entries in this range use segment 2, but `HPO_TOP_CLOCK_CONTROL` and `HPO_TOP_HW_CONTROL` use segment 3. If a consumer assumes one segment for the whole chunk, HPO registers resolve to the wrong address space.

The chunk also contains several cross-generation-looking layouts. Some offsets match DCN 3.5/3.6/4.2 families while others, notably DP AUX and HPD offsets, differ from older DCN 3.x files. Reusing register lists across ASIC versions without the exact generation's offset header can compile and fail only at hardware bring-up time.

Register-family completeness matters. Constructors initialize fixed arrays for four AUX engines, four HPD blocks, four DIO stream encoders, multiple VPG/AFMT instances, and four DSC blocks. Missing or renamed generated macros break builds; wrong but present symbols can cause instance aliasing.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/display runtime checks:

- Compile DCN401 display code with `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h` together; missing macro errors in resource, IRQ, DMUB, GPIO, or clock-manager code are immediate generated-header regressions.
- Add or run register-table sanity checks that compare initialized DCN401 table entries against expected `ctx->dcn_reg_offsets[base_idx] + offset` values for representative symbols such as `DP_AUX0_AUX_CONTROL`, `HPD0_DC_HPD_INT_STATUS`, `DIG2_DIG_FE_CNTL`, `DP2_DP_LINK_CNTL`, and `HPO_TOP_CLOCK_CONTROL`.
- Exercise connector hotplug and HPD RX paths; expected signals are HPD interrupts mapping to the right `DC_IRQ_SOURCE_HPDx`/`HPDxRX` entries, acknowledgement clearing the interrupt, and no stuck HPD status bits.
- Exercise AUX/DDC transactions for all physical connectors; expected signals are successful EDID reads, DP DPCD reads, timeout behavior only on absent sinks, and no cross-connector AUX aliasing.
- Exercise DP and HDMI modes on DIG2/DIG3-era mappings, including audio, infoframes, MST/MSO, DSC, ALPM/panel replay where supported, and link training. Failures often appear as blank display, unstable link training, missing audio, wrong colorimetry, or malformed secondary data packets.
- Exercise DSC0-DSC3 and HPO display paths separately, because the HPO top registers in this chunk switch to base index 3 and later HPO blocks continue outside this chunk.

### subset-b-002149: lines 12729-15420

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 12729-15420

## Purpose

This chunk is a generated AMD DCN 4.1.0 register-offset slice. It contains no executable C functions or types; its API is a large set of preprocessor constants that map symbolic display/audio/debug register names to MMIO offsets plus companion `<name>_BASE_IDX` constants. DCN 4.0.1 display code combines these offsets with `dcn_4_1_0_sh_mask.h` field masks and register helper macros to build ASIC-specific register tables.

The covered range starts at the high-performance output (HPO) DisplayPort stream mapper and HDMI/FRL encoder blocks, then enumerates repeated HPO DP stream, APG audio-packet-generator, DME metadata, VPG generic-packet, DP Sym32 stream encoder, DP link encoder, and DP DPHY Sym32 blocks for instances 0-3. It then covers DLPC and DPCS/RDPCSTX PHY/control offsets, host HDA/Azalia controller and stream descriptor offsets, duplicate HDA `*_1` offsets in the high address range, an empty HDCP 1.x key database address block marker, and the beginning of indirect debug-index (`ix*`) registers for CNVC, CM, MCIF writeback, MPC OCSC, MPCC, MPCC OGAM, and MPCC MCM.

## Important APIs and register groups

- `regDP_STREAM_MAPPER_CONTROL0` through `CONTROL5` expose HPO DP stream-to-link mapping controls under base index 3. These are top-level HPO mapper registers used to route up to six streams or mapper slots.
- `regHDMI_LINK_ENC_*`, `regHDMI_FRL_ENC_*`, `regHDMI_STREAM_ENC_*`, `regAFMT4_*`, `regDME4_*`, `regVPG4_*`, and `regHDMI_TB_ENC_*` describe the HPO HDMI path: link/clock control, FRL configuration and meter-buffer status, stream input mux and clock-ramp FIFO status, audio formatter packets and CRC/ramp status, DME metadata controls, VPG generic/ISRC/MPEG packet access, and transport-bus packet/ACR/buffer/CRC/encryption/timing controls.
- `regDP_STREAM_ENC[0-3]_DP_STREAM_ENC_*` define per-DP-stream encoder controls: stream clock, input mux, audio enable/control, FIFO ramp status, and spare registers.
- `regAPG[0-3]_APG_*` define DisplayPort audio packet generator offsets for each stream instance: control, debug generator, packet control, ACP/audio info/IEC60958 debug payloads, audio CRC controls/results, ramp controls, status/status2, audio DTO debug, memory power, and spare.
- `regDME[5-8]_DME_*` provide DME control and memory-control offsets associated with the four DP stream encoder instances.
- `regVPG[5-8]_VPG_*` expose generic-packet and ISRC/MPEG packet access for DP stream instances: access/data registers, frame/immediate update controls, status, and VPG memory power.
- `regDP_SYM32_ENC[0-3]_DP_SYM32_ENC_*` are the largest repeated groups in this chunk. Each instance includes video FIFO control, MSA double buffering, pixel format, MSA0-8, hblank control, generic secondary-data packet controls `SDP_GSP_CONTROL0` through `14`, SDP audio/metadata/framing/ATP controls, idle pattern, MSA/VBID/video stream controls, panel replay controls, video CRC controls/results/status, symbol counters, ALPM sleep/wake/request/ready/hardware/status/start/interrupt controls, memory power, and spare.
- `regDP_LINK_ENC[0-3]_DP_LINK_ENC_*` define minimal per-link encoder clock-control and spare offsets for HPO DP links.
- `regDP_DPHY_SYM32[0-3]_DP_DPHY_SYM32_*` describe the 32-symbol DP PHY block for each link: control/status, encryption config, SAT update and virtual-channel rate/count/status registers for VC0-5, eDP/ASSR registers, ALPM sleep/wake/control, test-pattern configuration, PRBS seeds, square-pulse/custom pattern words, error/default override, and symbol-count status/control.
- `regDLPC_*` covers display low-power/controller counters and power-up/resync controls, including current count, OPTC snapshot, DCN ZSC/LONO power-up, spare, and counter init value.
- `regDPCSSYS_CR[0-3]_DPCSSYS_CR_ADDR/DATA` and `regRDPCSTX[0-3]_*` cover DPCS/RDPCS transmitter access and PHY controls. RDPCSTX instances include control/clock/interrupt, PLL update data, CR address/data, SRAM control, scratch/spare registers, pattern detect/debug controls, PHY control 0-17, PHY fuses, RX load value, RDPCS control, and PLL update override address/data.
- `regAZCONTROLLER0_*`, `regAZENDPOINT0_*`, `regAZINPUTENDPOINT0_*`, `regAZROOT0_*`, and `regAZSTREAM[0-7]_0_*` define host HDA/Azalia controller and stream descriptor offsets in low base-index ranges. They include CORB/RIRB pointers/control/status/size, immediate command/response interfaces, DMA position base address, wall-clock alias, endpoint command interfaces, and eight output stream descriptors.
- `regAZALIA_F0_*`, `regAZENDPOINT*_1_*`, `regAZROOT*_1_*`, and `regAZSTREAM[0-7]_1_*` repeat HDA/Azalia codec, endpoint, root, and stream descriptor offsets in the high `0x4b70xx` address region using base index 3. The stream descriptor pattern includes control/status, link position, cyclic buffer length, last valid index, FIFO size/format aliasing, BDL pointer lower/upper, and link-position aliases.
- `ixID2_CNVC_*`, `ixID*_CM_*`, `ixID*_WB_*`, `ixID*_MPC_OUT*`, `ixMPCC[0-3]_*`, `ixMPCC_OGAM[0-3]_*`, and `ixMPCC_MCM[0-2]_*` are indirect debug-index constants rather than normal MMIO register names. They name debug selector IDs for converter, color-management, writeback, MPC output CSC, MPCC composition state, MPCC output gamma, and MPCC MCM 3D LUT/gamut-remap debug views.

## Control flow and usage model

There is no local control flow. These constants are consumed at compile time by register-table initializers and by token-pasting helper macros.

The common usage model in DCN 4.0.1 code is:

1. Include `dcn_4_1_0_offset.h` with `dcn_4_1_0_sh_mask.h`.
2. Define a `BASE(seg)`/`BASE_INNER(seg)` mapping, such as `DCN_BASE__INST0_SEG2` in DCN 4.0.1 consumers.
3. Build offsets as `BASE(regNAME_BASE_IDX) + regNAME` or `BASE(regBLOCKid_REGISTER_BASE_IDX) + regBLOCKid_REGISTER`.
4. Pair the offset with generated shift/mask fields from the matching sh/mask header.
5. Use Display Core, GPIO, IRQ, DMUB, or encoder helper code to read/update/write the resulting hardware register.

Concrete consumers in this tree include `display/dmub/src/dmub_dcn401.c`, `display/dc/gpio/dcn401/hw_factory_dcn401.c`, `display/dc/gpio/dcn401/hw_translate_dcn401.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, and `display/dc/resource/dcn401/dcn401_resource.c`. The specific registers in this chunk are mostly exercised by display output, link, audio, packet, debug, and HDA/HPO paths rather than by the DMUB reset/window subset shown in `dmub_dcn401.c`.

## State and persistence behavior

The header itself has no mutable state. The named offsets address state held by display, audio, PHY, and debug hardware. That state persists according to GPU/display IP lifetime: boot and firmware initialization, resource-pool construction, modeset, stream enable/disable, link training, audio enablement, runtime power management, suspend/resume, and GPU or display reset.

Important stateful areas are:

- HPO HDMI and DP controls are programming state for active display links. Stream mapper, input mux, link encoder clock, FRL configuration, transport-bus mode, packet controls, encryption controls, and stream/video controls must be sequenced with link setup and teardown.
- AFMT/APG, VPG, DME, and HDMI/DP packet registers hold sideband and audio packet configuration. Some associated status/CRC/result registers are hardware-produced and can change while the stream is running.
- DP Sym32 stream encoder state includes MSA timing/colorimetry, pixel format, SDP scheduling, metadata, panel replay, CRC, symbol counters, ALPM, and memory-power controls. Many controls are per-instance and must match the stream-to-link mapping.
- DP DPHY Sym32 state includes encryption, virtual-channel/SAT allocation, eDP ASSR, ALPM, test patterns, PRBS/custom pattern state, error status, and symbol counters. Training or diagnostic controls are live PHY/link state and may be unsafe to change during active video.
- RDPCSTX/DPCSSYS registers include transmitter PLL/CR access, PHY controls, fuses, debug, scratch, and override state. These can affect physical output and low-level link stability.
- HDA/Azalia controller state includes CORB/RIRB queues, immediate command/response paths, DMA position buffers, wall-clock aliases, stream descriptor control/status, BDL base addresses, cyclic buffer lengths, and link position aliases. Descriptor registers bridge display audio programming with host audio DMA semantics.
- `ix*` debug IDs are selector values for indirect debug reads. They do not store state by themselves, but selecting an ID exposes live debug state from CNVC, CM, writeback, MPC/MPCC, OGAM, and MCM blocks.

## Dependencies and integration points

- Must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h`. Offset macros identify registers; sh/mask macros identify fields. Either side drifting breaks generated register tables.
- Depends on AMDGPU Display Core register helpers such as `REG`, `REGI`, `SRI`, `REG_OFFSET_EXP`, `REG_READ`, `REG_WRITE`, `REG_UPDATE`, and generated table macros that paste `reg`/block/id tokens into names from this header.
- Integrates with DCN 4.0.1 resource setup, IRQ service, GPIO/HPD/DDC factory and translation, clock manager, DMUB register table setup, HPO HDMI/DP stream/link encoder code, audio packet programming, and HDA/Azalia display-audio handling.
- The `_BASE_IDX` values select address segments. In this chunk, base index 2 is common for DCN/DPCS/HPO DP blocks, base index 3 appears for HPO HDMI and high HDA/Azalia addresses, base index 0/1 appears in host HDA low-register and alias regions, and the `ix*` entries are indirect debug IDs without `_BASE_IDX` companions.
- Repeated instance naming is part of the contract. DP stream/Sym32/link/DPHY groups are encoded as explicit instance numbers; generic code should use the proper per-instance tables rather than deriving offsets arithmetically outside the generated macros.
- The HDA stream descriptors intentionally contain address aliases, such as FIFO size and format sharing the same offset and link-position alias registers using a different base index/address. Consumers must rely on the paired field masks to distinguish packed or aliased meanings.

## Risks and edge cases

- Generated-header drift is the main risk. A stale offset paired with correct field masks can silently target the wrong register, and a correct offset paired with stale masks can corrupt adjacent fields in packed registers.
- Segment/base-index mistakes are especially hazardous because the same numeric offset can mean different hardware depending on `BASE_IDX`. HDA low-register aliases and high `0x4b70xx` addresses make this visible in the same chunk.
- Several register names deliberately alias the same offset, including HDA CORB/RIRB control/status/size groupings, immediate command data/index, stream descriptor FIFO size/format, and link-position aliases. Full-register writes can clobber unrelated packed fields.
- Per-instance repetition creates copy/paste hazards. Using `APG1` with `DP_STREAM_ENC0`, `VPG8` with the wrong stream, or `DP_DPHY_SYM322` with the wrong link would compile if names exist but misprogram the hardware path.
- Status/result registers should not be handled like stable controls. Meter-buffer status, FIFO status, AFMT/APG CRC results, VPG generic status, DP Sym32 CRC/status/symbol counters, DPHY error/status/SAT status, RDPCSTX debug/fuse values, and Azalia link position are hardware-owned or diagnostic.
- ALPM and panel replay controls cross timing, link, and power domains. Incorrect sleep/wake/request/ready sequencing can produce link wake failures, blank frames, or missed interrupts.
- DPHY test-pattern and PRBS/custom pattern registers are powerful diagnostics. Accidentally enabling test patterns or stale custom seeds during active video can break link training or visible output.
- RDPCSTX PHY fuse/control/PLL override writes can affect physical-layer calibration. Tests should avoid changing these outside hardware bring-up or tightly controlled link-training paths.
- The chunk has boundary truncation: it begins after the previous HPO top block and ends at the `mpcc_mcm3_mpcc_mcmdebugind` address-block header before its `ixMPCC_MCM3_*` defines. Final per-file reconciliation should join adjacent chunks for complete block coverage.

## Test signals

- Build tests with DCN 4.0.1 enabled should compile all consumers that include `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`, especially `dmub_dcn401.c`, `dcn401_resource.c`, `irq_service_dcn401.c`, and the DCN401 GPIO factory/translate code.
- Static generation checks should verify every `reg*` offset used by a DCN401 register-table macro has a matching `_BASE_IDX`, and every field use has a matching sh/mask entry in `dcn_4_1_0_sh_mask.h`.
- Instance-layout checks should compare repeated DP stream encoder, APG, DME, VPG, DP Sym32, DP link encoder, DP DPHY, RDPCSTX, and Azalia stream groups for expected stride and intentional aliases.
- Display validation should exercise HPO HDMI FRL and HPO DP output on all supported instances, including stream mapper routing, input mux changes, MSA/pixel-format programming, sideband packet delivery, metadata packets, panel replay, and stream disable/re-enable.
- Audio validation should cover AFMT/APG packet programming, IEC60958/audio-info paths, audio CRC diagnostics, HDA stream descriptors, BDL pointer programming, link-position reporting, and DMA position buffer aliases.
- Link diagnostics should cover DP DPHY training/test-pattern paths, PRBS/custom pattern registers, encryption/SAT/VC controls, DPHY error status, stream/link symbol counters, and ALPM sleep/wake/resume.
- Packet validation should verify VPG generic packets, ISRC, MPEG info, HDMI transport-bus generic packets, ACR packets, metadata packet controls, and update/status behavior across vblank updates.
- PHY and DPCS bring-up tests should validate RDPCSTX clock/control, CR address/data access, PLL update override, SRAM control, pattern detect, PHY control/fuse readouts, and debug-config behavior.
- Suspend/resume and GPU reset tests should confirm HPO link/stream state, memory-power controls, HDA stream descriptors, ALPM state, and packet-generator state are restored or reset as expected.
- Debug tooling tests should verify `ix*` indirect debug IDs select the intended CNVC, CM, writeback, MPC OCSC, MPCC, OGAM, and MCM views without treating them as direct MMIO offsets.

### subset-b-002150: lines 15421-16662

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 15421-16662

## Purpose

This chunk is a generated AMD DCN 4.1.0 register-offset slice. It contains preprocessor constants only: no C functions, structs, enums, storage, or executable control flow. The exported surface is `ix*` indirect-register index macros for display timing-generator debug windows and Azalia/HDA display-audio codec, stream, endpoint, CRC, descriptor, and sink-info windows.

The range starts with five continuation macros from the previous `mpcc_mcm3_mpcc_mcmdebugind` block (`ixMPCC_MCM3_ID8...ID12`), then covers OTG debug indirect registers for OTG0-OTG3, and then a large Azalia Function 0 audio register map. It ends at the file's closing `#endif`, so this is the tail chunk of `dcn_4_1_0_offset.h`. Although the repository root path includes `distributed-fs/ceph-client`, this header is AMDGPU Display Core hardware metadata and has no Ceph, filesystem, network, or persistent-storage behavior.

## Important APIs, Types, And Macros

The only API is generated macro constants:

- `ix*` names define indirect register indices inside a block-specific indexed register space.
- Address-block comments name the hardware index aperture, for example `otg0_otgdebugind`, `azendpoint_f2codecind`, `azf0stream0_streamind`, and `azf0endpoint7_endpointind`.
- Every visible address block in this chunk declares `base address: 0x0`; consumers combine these indices with the appropriate indirect access mechanism or register table rather than adding `reg*_BASE_IDX` segment bases as done for direct `reg*` MMIO offsets.

The chunk contains 1,061 `#define` lines. The visible block inventory is:

- `mpcc_mcm3_mpcc_mcmdebugind` continuation: five MCM debug entries for 3DLUT float conversion and gamut remap IDs.
- `otg0_otgdebugind`, `otg1_otgdebugind`, `otg2_otgdebugind`, `otg3_otgdebugind`: OTG debug data registers `OTG_DBG_DATA1..10`, scaler/output interface debug selectors, and, for OTG2, a small `DCIO_DEBUG*` group.
- `azendpoint_f2codecind`: Function 2 codec converter and pin-control verbs/parameters, including converter format, stream/channel ID, digital converter controls, pin sense, default configuration, speaker/channel allocation, HBR, lipsync, LPIB snapshot registers, coding/format-change status, wireless-display identification, and remote keepalive.
- `azendpoint_descriptorind` and `azendpoint_sinkinfoind`: audio descriptor slots, manufacturer/product IDs, sink description length, port IDs, and sink description words.
- `azf0controller_azinputcrc0resultind`, `azf0controller_azinputcrc1resultind`, `azf0controller_azcrc0resultind`, `azf0controller_azcrc1resultind`: eight-channel CRC result windows for input and output/controller audio CRC diagnostics.
- `azinputendpoint_f2codecind` and `azroot_f2codecind`: Function 2 input endpoint and root codec verb/parameter indices, including converter capabilities, stream formats, supported rates, pin capabilities, unsolicited response, input pin sense, HBR, and root node/function group metadata.
- `azf0stream0_streamind` through `azf0stream15_streamind`: sixteen repeated stream indirect blocks, each with stream descriptor control, status, link position-in-buffer, cyclic-buffer length, and stream FIFO size.
- `azf0endpoint0_endpointind` through `azf0endpoint7_endpointind`: eight repeated display-audio output endpoint blocks, each with converter controls, pin controls, speaker/channel allocation, ELD/sink-info access, ACP index/data, audio descriptors, infoframe/status registers, LPIB snapshot, coding/format-change, wireless-display, and endpoint fine-grain clock-gating reporting disable.
- `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint7_inputendpointind`: eight repeated input endpoint blocks with input converter format/stream/digital controls, supported rates/formats, input pin capabilities, unsolicited response, input pin sense, widget control, multichannel/HBR/channel allocation, hot-plug control, LPIB snapshot, input status, and infoframe indices.

There are no local C types. Runtime code normally reaches these constants through AMD Display Core register-list and indirect-access helpers, paired with the matching `dcn_4_1_0_sh_mask.h` field encodings where field-level access is needed.

## Control Flow And Usage Model

This header has no local control flow. It contributes compile-time constants to code that builds hardware register tables and then performs MMIO or indirect register operations at runtime.

A typical DCN 4.1.0 flow in this tree is:

1. DCN401 source files include `dcn/dcn_4_1_0_offset.h` and `dcn/dcn_4_1_0_sh_mask.h`.
2. Register-list macros in resource, DMUB, IRQ, clock, GPIO, audio, and block-specific code expand generated names into concrete offsets, masks, and shifts.
3. Runtime helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `AZ_REG_READ`, `AZ_REG_WRITE`, or indexed debug/audio helpers use those generated constants to access the selected hardware register.

Direct local include anchors for this generation are `display/dmub/src/dmub_dcn401.c`, `display/dc/resource/dcn401/dcn401_resource.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, `display/dc/gpio/dcn401/hw_factory_dcn401.c`, and `display/dc/gpio/dcn401/hw_translate_dcn401.c`. The audio-specific `ixAZALIA*`, `ixAZF0STREAM*`, `ixAZF0ENDPOINT*`, and `ixAZF0INPUTENDPOINT*` names align with common DCE/DC audio code that programs Azalia/HDA display-audio endpoints through endpoint register tables rather than hard-coded numeric indices.

## State And Persistence Behavior

The macros are immutable compile-time constants and persist nothing. The state they describe lives in hardware registers:

- OTG debug data/interface registers expose live timing-generator and display-output diagnostic state.
- Azalia codec converter, stream, pin-control, descriptor, sink-info, and endpoint registers hold display-audio configuration and status across a mode/audio configuration lifetime until the display engine, codec function, power-management path, or GPU reset reinitializes them.
- Stream LPIB, cyclic-buffer, FIFO, and CRC registers are runtime diagnostic/status surfaces tied to active audio streams.
- Endpoint and input-endpoint hotplug, unsolicited response, pin sense, infoframe, HBR, multichannel, and format-change registers are hardware-owned or software-programmed state used during connector audio setup, sink updates, and stream reconfiguration.

Persistence is hardware lifetime persistence, not filesystem persistence. Suspend/resume, runtime power gating, display IP reset, GPU reset, or audio re-enumeration can clear or rewrite the described register state.

## Dependencies And Integration Points

- The companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h`, which provides field shifts and masks for these register names when field-level access is required.
- DCN401 register-table code includes this header in DMUB service setup, resource construction, IRQ service construction, clock manager setup, and GPIO factory/translation paths. `dmub_dcn401.c` demonstrates the direct-offset pattern with `REG_OFFSET_EXP()`, while indexed audio/debug constants are consumed by block-specific indirect access paths.
- Common display-audio code under `display/dc/dce/` uses generated audio register tables and `struct dce_audio`-style register/shift/mask mappings to configure Azalia endpoints, ELD/sink data, audio info support, stream format/channel selection, and endpoint pin-control state.
- The repeated endpoint and stream namespaces are hardware instance contracts. Resource construction must keep audio endpoint counts, stream counts, and generated table entries aligned with the ASIC's exposed blocks.
- Similar constants appear across older `dce_*_offset.h` and `dcn_*_offset.h` generations, which is useful for drift comparison but also means a wrong-generation include can compile if names overlap while still targeting the wrong hardware layout.

## Risks And Edge Cases

- Offset/header pairing is critical. `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h` must come from the same hardware generation; stale offsets with valid masks can silently misprogram audio or debug registers.
- Repetition hides instance-specific mistakes. Sixteen stream blocks, eight output endpoints, and eight input endpoints share near-identical layouts. A copied numeric value or table entry that targets the wrong endpoint may only fail on one connector/audio instance.
- Indirect indices are not direct MMIO addresses. Treating `ix*` values as direct `reg*` offsets would access the wrong register path.
- The chunk starts mid-block and ends the file. Whole-file reconciliation must merge the preceding chunk for complete `MPCC_MCM3` debug context, and accidental edits near the closing `#endif` can break all consumers of this generated header.
- Audio register effects are hardware- and sink-dependent. Wrong `CHANNEL_STREAM_ID`, converter format, HBR, multichannel enable, speaker/channel allocation, ELD/sink-info, or pin-sense indices can produce failures only with particular HDMI/DP sinks, sample rates, channel layouts, or hotplug sequences.
- Status and control names are adjacent. `LPIB`, CRC result, input status, pin sense, format-changed, hot-plug, unsolicited-response, and keepalive registers should not be treated as ordinary persistent configuration words.
- Clock-gating reporting disable fields are power/diagnostic sensitive. Incorrect endpoint `FGCG_REP_DIS` indices can mask clock-gating telemetry or interfere with power-debug signals.

## Test Signals

- Build AMDGPU DC with DCN401 enabled so all include sites compile against `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`; missing or renamed generated symbols should fail at compile time in register-list expansion.
- Static consistency checks should compare repeated `azf0stream0..15`, `azf0endpoint0..7`, and `azf0inputendpoint0..7` index layouts and flag unintended divergence.
- HDMI/DP audio testing should cover hotplug, mode set, suspend/resume, runtime power management, sample-rate/format changes, HBR, multichannel layouts, ELD/sink-info updates, and endpoint counts high enough to exercise endpoints beyond instance 0.
- Diagnostic testing should read OTG debug windows and Azalia CRC/LPIB/status registers during active display and audio playback to verify that indirect indices reach the expected hardware windows.
- Register-dump comparison against the DCN 4.1.0 ASIC register specification is the most direct validation for this generated tail chunk, especially around the repeated endpoint blocks and the file-ending `#endif`.
