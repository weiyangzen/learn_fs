# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001680`: lines 1-2665, `Docs/researches/chunks/subset-b-001680_research.md`
- `subset-b-001681`: lines 2666-5203, `Docs/researches/chunks/subset-b-001681_research.md`
- `subset-b-001682`: lines 5204-7718, `Docs/researches/chunks/subset-b-001682_research.md`
- `subset-b-001683`: lines 7719-10374, `Docs/researches/chunks/subset-b-001683_research.md`
- `subset-b-001684`: lines 10375-12949, `Docs/researches/chunks/subset-b-001684_research.md`
- `subset-b-001685`: lines 12950-15501, `Docs/researches/chunks/subset-b-001685_research.md`
- `subset-b-001686`: lines 15502-18022, `Docs/researches/chunks/subset-b-001686_research.md`

## Chunk Research

### subset-b-001680: lines 1-2665

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 1-2665

## Scope

This chunk is the opening 2,665-line slice of the generated AMD DCN 3.0.0 register offset header. It starts with the MIT SPDX marker and `_dcn_3_0_0_OFFSET_HEADER` include guard, then exports preprocessor constants for memory-mapped display registers. The chunk contains no C functions, structs, enums, inline helpers, or executable algorithms. Its API is entirely made of `#define` symbols: `mm...` register offsets and matching `mm..._BASE_IDX` segment selectors.

The visible address blocks cover the first half of the DCN 3.0 display register map:

- VGA legacy/display-decode registers under `dce_dc_mmhubbub_vga_dispdec`.
- DCCG clock generation and display-clock performance monitor blocks.
- DMU, DMCU, DMCUB, IHC, RBBMIF, and DMCUB security/control blocks.
- MCIF writeback, MMHUBBUB, VGAIF, and MMHUBBUB performance monitor blocks.
- Azalia stream, endpoint-index/data, controller, root, and input-endpoint MMIO windows.
- DCHUBBUB SDPIF, return path, main hubbub arbitration, performance monitor, and VM request interface blocks.
- HUBP0 and HUBP1 surface, request, return, cursor, and per-HUBP performance monitor blocks, ending after `mmDC_PERFMON7_PERFCOUNTER_STATE`.

The chunk ends inside `dce_dc_dcbubp1_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`; later lines in the same source file continue the remaining HUBP instances and downstream DCN blocks. This range does not include the later `ix...` Azalia indirect endpoint-index constants.

## Purpose

The file binds DCN 3.0.0 driver code to ASIC-specific register addresses without scattering raw numbers through functional display code. Consumers include this header together with `dcn_3_0_0_sh_mask.h` and an ASIC base-offset header such as `sienna_cichlid_ip_offset.h`. Resource, IRQ, GPIO, clock, DMUB, hubbub, HUBP, and writeback code then expand local register-list macros into typed register tables.

For this chunk, the highest-value coverage is early display infrastructure: clocking, interrupts, firmware mailbox/window setup, display memory arbitration, virtual-memory apertures, writeback buffers, display audio MMIO portals, and the first two plane-fetch pipelines. Those constants are used before and during modeset, flip, cursor, writeback, and DMUB firmware setup, so wrong values can fail display bring-up even when higher-level display logic is correct.

## Important API Surface

The exported API surface is macro names and numeric constants. Important groups include:

- Header and naming contract: `_dcn_3_0_0_OFFSET_HEADER`, direct MMIO offset symbols named `mmREGISTER`, and segment selectors named `mmREGISTER_BASE_IDX`.
- VGA registers: `mmVGA_MEM_WRITE_PAGE_ADDR`, `mmVGA_MEM_READ_PAGE_ADDR`, `mmVGA_RENDER_CONTROL`, `mmVGA_MODE_CONTROL`, surface address/pitch registers, `mmD1VGA_CONTROL` through `mmD6VGA_CONTROL`, legacy CRTC/SEQ/DAC/GEN/ATTR aliases, status/interrupt registers, and `mmVGA_SOURCE_SELECT`.
- DCCG registers: PHY PLL pixel resync controls, DP and DSC DTO parameters, DISPCLK/DPPCLK/DSCCLK controls, gate-disable and clock-gating registers, OTG0-OTG5 pixel-rate and PHYPLL pixel-rate controls, SYMCLK enables, audio DTO registers, VSYNC latch/counter registers, and PHYx SYMCLK force controls.
- Perfmon register families: `mmDC_PERFMON0_*` through this chunk's `mmDC_PERFMON7_*`, with counter control, state, counter value, high, and low registers for DCCG, DMU, MMHUBBUB, Azalia, DCHUBBUB, and HUBP instances.
- DMU/DMCU/DMCUB control: power-gating `mmDOMAIN0_PG_CONFIG` through `mmDOMAIN21_PG_STATUS`, DCPG interrupt controls, DMU clock/memory-power/misc controls, DMCU firmware RAM, interrupt, scratch, and master/slave communication registers, IHC display interrupt status/destination registers, DMCUB region offset/top/base registers, secure reset/control, inbox/outbox pointer registers, GPINT, scratch registers, timer registers, memory-power control, and processor ID.
- Writeback and MMHUBBUB registers: `mmMCIF_WB_*` buffer manager, pitch, status, luma/chroma addresses and high-address halves, buffer size/resolution, arbitration, SCLK/change, NB pstate, clock-gater, self-refresh, QoS, and watermark registers; MMHUBBUB warmup, client ID, memory power, clock, soft-reset, and DMU interface error registers.
- Azalia MMIO windows: stream index/data pairs for streams 0-15, endpoint index/data pairs for endpoints 0-7, input endpoint index/data pairs for input endpoints 0-7, plus controller/root registers for audio DTO, DMA, payload capability, CRC, CORB/RIRB, global control/status, wake, interrupt, wall-clock, codec command/response, and state-change status.
- DCHUBBUB registers: SDPIF VM aperture/location registers, local HBM aperture locks, return-path DCC config and CRC registers, memory-power control/status, arbitration watermarks for urgency, stutter, self-refresh, DRAM-clock change and VM-row behavior, surface-check addresses, VTG0-VTG5 control, DCHUBBUB reset/clock/DCFCLK/performance/debug/status registers, timeout detection, fractional urgent bandwidth, and VM context/page-table programming for contexts 0-15.
- HUBP/HUBPREQ/HUBPRET/CURSOR instances 0 and 1: surface config, address/tiling config, primary/secondary viewport registers for luma and chroma, request-size config, HUBP control/clock/VMPG, surface pitch, VMID settings, primary/secondary and meta-surface addresses, flip control and flip interrupt, surface-in-use and earliest-in-use tracking, TTU/QoS controls, VM system aperture and L1 TLB controls, blank/destination/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor settings, memory power controls, HUBPRET read-line controls/status, cursor surface/position/hotspot/stereo/DMDATA controls, and per-HUBP perf counters.

Most constants in this chunk use `_BASE_IDX` value `2`, while the earliest VGA/DCCG constants use base index `1` and two VGA memory page address constants use base index `0`. That base-index value is as much a part of the ABI as the offset value because consuming macros compute absolute MMIO addresses as `BASE(mm..._BASE_IDX) + mm...`.

## Control Flow

There is no local control flow in the header. Runtime control flow is in the consumers:

1. DCN30 code includes `sienna_cichlid_ip_offset.h`, `dcn_3_0_0_offset.h`, and `dcn_3_0_0_sh_mask.h`.
2. Resource construction in `display/dc/resource/dcn30/dcn30_resource.c` defines expansion helpers such as `SR`, `SRI`, `SRI2`, `SRII`, and `DCCG_SRII`. These paste symbolic register names into the `mm...` and `mm..._BASE_IDX` constants from this header.
3. Object headers such as `dcn30_dccg.h`, `dcn30_hubbub.h`, `dcn30_hubp.h`, and `dcn30_mmhubbub.h` provide register-list macros. Expansion creates typed register tables for DCCG, HUBBUB, HUBP, MCIF writeback, DMUB, audio, IRQ, GPIO, and related blocks.
4. Functional code calls `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and similar helpers against those tables. Hardware sequencing is enforced by the functional modules, not by this generated header.
5. DMUB service code in `display/dmub/src/dmub_dcn30.c` uses this header's DMCUB, DCN VM framebuffer, and region-window offsets to reset DMCUB, translate framebuffer-relative addresses, program code/data windows, and set up inbox/outbox style firmware communication.
6. IRQ code in `display/dc/irq/dcn30/irq_service_dcn30.c` includes the same offsets and maps hardware source IDs such as HUBP flip, DMCUB outbox, vblank, vline, vupdate, HPD, and HPD RX into DAL IRQ sources. The IHC status and interrupt-destination registers in this chunk are part of that interrupt fabric.

## State and Persistence

The header itself has no software state or persistence. It defines compile-time constants. The constants address hardware state that persists in MMIO registers until reset, power-gating, modeset reprogramming, firmware reinitialization, or register-specific clear/ack writes.

State represented by this chunk includes:

- Clock tree and DTO state for display, DPP, DSC, DP, audio, PHYPLL, SYMCLK, and VSYNC counters.
- Power-gating and memory-power state for DMU domains, DMCUB, MMHUBBUB, DCHUBBUB SDPIF/return path, HUBPREQ/HUBPRET, and cursor blocks.
- DMCU and DMCUB firmware state: firmware code windows, RAM access, control/status, interrupts, GPINT mailboxes, inbox/outbox pointers, scratch registers, timers, and security reset controls.
- Display interrupt status and routing state across DCCG, DMU, DCPG, MMHUBBUB, WB, DCHUB, DPP, MPC, OPP, OPTC, OTG, DIG, I2C/DDC/HPD, DCIO, AUX, DSC, and Azalia destinations.
- Writeback buffer manager state, buffer addresses, buffer status, arbitration, QoS, pstate watermark, size, resolution, and self-refresh controls.
- DCHUBBUB arbitration/watermark state, DCC return-path configuration, VM aperture and page-table context state, VM fault controls/status, timeout detection, surface-check registers, and global timer/performance state.
- Per-pipe HUBP state for active surface format, tiling, viewport, base/meta addresses, flip pending/current address state, TTU delivery parameters, cursor plane state, dynamic metadata addressing, VM aperture/TLB controls, and underflow/no-outstanding-request status.
- Azalia display-audio controller, stream, endpoint, input-endpoint, DMA, CORB/RIRB, response, wake, and wall-clock state exposed through direct MMIO index/data portals.

Because these are register addresses, a bad value can cause state to be written into the wrong block. The symptom may persist until a full modeset, DC reset, DMCUB reset, GPU reset, or suspend/resume sequence reinitializes the affected hardware.

## Dependencies and Integration Points

This chunk is tightly coupled to:

- `dcn_3_0_0_sh_mask.h`, which supplies the field masks and shifts for the registers whose offsets appear here.
- `sienna_cichlid_ip_offset.h`, which provides `DCN_BASE__INST0_SEG*` base segments used by `BASE(mm..._BASE_IDX)` expansion in DCN30 resource, IRQ, GPIO, clock, and DMUB code.
- `display/dc/resource/dcn30/dcn30_resource.c`, which includes this header and defines the register expansion macros that convert symbolic register names into absolute offsets.
- `display/dc/dccg/dcn30/dcn30_dccg.h`, whose `DCCG_REG_LIST_DCN30()` consumes DCCG, OTG pixel-rate, HDMI character clock, and PHY SYMCLK constants from this chunk.
- `display/dc/hubbub/dcn30/dcn30_hubbub.h`, whose register list and masks cover DCHUBBUB arbitration, framebuffer aperture, VM, fault, watermark, and fractional urgent bandwidth registers in this chunk.
- `display/dc/hubp/dcn30/dcn30_hubp.h`, which extends DCN21 HUBP lists with `HUBPREQx_DCN_DMDATA_VM_CNTL` and uses the HUBP/HUBPREQ/HUBPRET/CURSOR offsets shown here.
- `display/dc/dcn30/dcn30_mmhubbub.h` and `display/dc/dcn30/dcn30_mmhubbub.c`, which program MCIF writeback buffers, pitches, addresses, watermarks, arbitration, pstate behavior, and writeback control using the MCIF/MMHUBBUB constants in this chunk.
- `display/dmub/src/dmub_dcn30.c` and `display/dmub/src/dmub_dcn302.c`, which use DMCUB, VM framebuffer, and region-window registers from this header for firmware service setup.
- `display/dc/irq/dcn30/irq_service_dcn30.c` and `display/dc/irq/dcn302/irq_service_dcn302.c`, which include this header for DCN 3.0 interrupt status/control register addressing.
- DCN30 GPIO, clock-manager, audio, writeback, hubbub, and HUBP helper code that indirectly relies on register-list tables populated from these constants.

The repeated instance layout is an integration contract. The chunk shows identical families for HUBP0 and HUBP1, HUBPREQ0 and HUBPREQ1, HUBPRET0 and HUBPRET1, cursor0 instance 0 and cursor0 instance 1, Azalia stream 0-15 portals, endpoint 0-7 portals, input endpoint 0-7 portals, and performance monitor instances 0-7. Resource code assumes those families can be generated by token pasting; renaming or de-aligning one instance breaks table expansion or silently targets the wrong block.

## Risks

- Offset drift is high impact. These constants compile into absolute MMIO addresses; if a value is wrong, high-level driver code still builds while programming the wrong hardware register.
- `_BASE_IDX` mistakes are as dangerous as offset mistakes. A correct register offset with the wrong segment index computes the wrong absolute address after `BASE(mm..._BASE_IDX)` expansion.
- The chunk includes several duplicated or aliased offsets by design, such as legacy VGA aliases and `mmFMON_CTRL`/`mmFMON_CTRL_1`. Review tooling should distinguish intentional aliases from accidental duplicate definitions.
- Early boot and firmware setup are sensitive. Bad DMCUB region, security, GPINT, inbox/outbox, scratch, or VM framebuffer offsets can prevent DMUB firmware load or break firmware command exchange.
- Display memory programming has broad blast radius. Incorrect DCHUBBUB, VM context, aperture, TLB, MCIF writeback, or HUBP surface-address registers can cause VM faults, stale scanout, underflow, writeback corruption, or accesses to unintended memory.
- Watermark and clocking registers can fail only under load. DCCG DTO/gating, DCHUBBUB arbitration, MCIF watermarks, pstate controls, and TTU delivery registers may look fine at boot but fail during high-resolution modes, flips, memory-clock changes, multi-display, or writeback.
- Instance-copy errors can be localized and hard to reproduce. A mismatch in only `HUBP1` or `HUBPREQ1` may affect only the second pipe or a multi-plane/multi-display mode.
- Interrupt status/destination offsets are sticky-state sensitive. Wrong IHC or HUBP flip interrupt mapping can drop vblank/vupdate/flip events, fail to acknowledge them, or route events to the wrong handler.
- Power and reset controls have cross-block effects. MMHUBBUB, DCHUBBUB, DMCUB, HUBPREQ/HUBPRET, cursor, and domain power-gating registers can disable active display paths if programmed out of sequence.

## Test Signals

Useful validation signals for this chunk are a mix of compile-time macro coverage and hardware/display behavior:

- Full AMDGPU display builds should catch missing or renamed macros in DCN30 resource, IRQ, GPIO, clock-manager, DMUB, HUBP, HUBBUB, DCCG, and writeback code.
- Generated-register diffs against AMD register database outputs and adjacent headers such as `dcn_3_0_1_offset.h`, `dcn_3_0_2_offset.h`, `dcn_3_0_3_offset.h`, and `dcn_3_0_0_sh_mask.h` should flag unintended offset, base-index, or instance-layout changes.
- DMUB initialization tests should verify firmware load, region/window setup, GPINT command handling, inbox/outbox traffic, DMCUB wake/reset behavior, and DMCUB outbox interrupts.
- Modeset and plane tests should cover HUBP0 and HUBP1 independently: primary and secondary surfaces, chroma planes, metadata/DCC surfaces, tiling modes, flips, flip interrupts, cursor enable/position/hotspot, dynamic metadata access, and VM fault/underflow status.
- Memory and power tests should exercise DCHUBBUB watermarks, stutter/self-refresh, DRAM clock changes, VM row urgency, MCIF writeback, MMHUBBUB power gating, DCHUBBUB timeout detection, and suspend/resume.
- Clock tests should cover DISPCLK/DPPCLK/DSCCLK DTO programming, OTG0-OTG5 pixel-rate controls, PHYPLL pixel-rate controls, SYMCLK force/gating behavior, audio DTOs, and VSYNC latch/counter registers.
- Writeback validation should verify buffer addresses/high bits, pitch, luma/chroma sizes, buffer status, arbitration slice/time-per-pixel, pstate watermarks, slice interrupts, overrun status, and resolution registers.
- Display audio validation should cover Azalia controller/root state, stream index/data windows, endpoint and input-endpoint portals, codec command/response behavior, DMA/CORB/RIRB controls, wall-clock, wake, and state-change status.
- IRQ tests should exercise vblank, vupdate, vline, HUBP page flip, DMCUB outbox, HPD/HPD RX, and interrupt acknowledgement paths to confirm the included interrupt-status and destination registers are mapped correctly.

## Chunk Notes

This is a generated constants-only chunk, so the main research value is the hardware coverage and integration contract. The first 2,665 lines anchor DCN 3.0.0's global display infrastructure and the first two HUBP pipelines. Later chunks must finish the remaining HUBP instances and downstream display I/O blocks before a final whole-file report can describe the full `dcn_3_0_0_offset.h` register map.

### subset-b-001681: lines 2666-5203

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 2666-5203

## Purpose

This chunk is generated AMDGPU DCN 3.0.0 register-offset metadata. It contains no executable C logic; its public surface is a large set of preprocessor constants mapping hardware register names to MMIO register offsets and to register-base-index selectors. The paired pattern is:

- `mmREGISTER_NAME` gives the register offset, in this range from `0x077c` through `0x0f7f`.
- `mmREGISTER_NAME_BASE_IDX` gives the register aperture/base selector, consistently `2` for the chunked display-register blocks here.

The path is under a local `ceph-client` source mirror, but this file is AMD display-driver hardware metadata rather than Ceph or distributed-filesystem logic.

The range starts at the tail of `DC_PERFMON7`, covers DCN hub pipe instances 2 through 5, then covers DPP instance 0 and most of DPP instance 1. It ends at `mmCM1_CM_3DLUT_READ_WRITE_CONTROL_BASE_IDX`; later lines in the same file continue other DCN 3.0.0 generated register blocks.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime objects in this chunk. The important API is the generated macro namespace consumed by AMD display register-list helpers such as `SRI(...)`, `SR(...)`, `REG_READ`, `REG_WRITE`, `REG_UPDATE`, and the DCN resource tables that bind offsets together with masks and shifts from the matching `dcn_3_0_0_sh_mask.h`.

Major macro families in this chunk:

- `DC_PERFMON7_*`, `DC_PERFMON8_*`, `DC_PERFMON9_*`, `DC_PERFMON10_*`, `DC_PERFMON11_*`, and `DC_PERFMON12_*`: display performance-counter control, state, counted value, high/low counter value, and interrupt/misc registers associated with hub pipe and DPP blocks. `DC_PERFMON7` is partial at the start of the chunk.
- `HUBP2_*` through `HUBP5_*`: hub pipe surface configuration, address and tiling configuration, primary and secondary luma/chroma viewport start and dimension registers, request-size configuration, hubp control, clock control, virtual-memory page configuration, debug registers, and DCFCLK/DPPCLK measurement-window controls.
- `HUBPREQ2_*` through `HUBPREQ5_*`: hub request programming for surface pitch, VMID, primary/secondary luma and chroma surface addresses, metadata addresses, surface control, flip control, flip interrupts, current and earliest in-use addresses, expansion modes, TTU/QoS watermarks, VM aperture, L1 TLB control, blanking/scaler/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor TTU, cursor settings, request limits, DMDATA VM control, and memory power controls/status.
- `HUBPRET2_*` through `HUBPRET5_*`: hub return control, DET buffer plane offsets and crossbar selection, memory power control/status, read-line controls and values, read-line status, interrupt mask/type/status/ack registers, and read-line configuration.
- `CURSOR0_2_*` through `CURSOR0_5_*`: cursor control, surface address high/low, size, position, hot spot, stereo control, destination offset, cursor memory power state, and DMDATA address/control/QoS/status/software-data registers.
- `DPP_TOP0_*` and `DPP_TOP1_*`: DPP control, soft reset, and clock-control registers.
- `CNVC_CFG0_*` / `CNVC_CFG1_*` and `CNVC_CUR0_*` / `CNVC_CUR1_*`: conversion and cursor-blending front-end registers for format control, pixel format, alpha LUTs, floating-point bias/scale, color keying, pre-degamma, pre-dealpha, pre-realalpha, pre-CSC matrices for A/B banks, cursor color/control, and cursor scale/bias.
- `DSCL0_*` and `DSCL1_*`: scaler and line-buffer registers for coefficient RAM, scaler mode, tap control, replicate control, horizontal/vertical ratios and inits, black color, scaler update/autocal, overscan, OTG blanking, recout, MPC size, line-buffer data format, line-buffer memory power state, obuf power control, and DSCL memory power controls.
- `CM0_*` and `CM1_*`: color-management registers for dealpha, bias, gamma correction, gamut remap, post CSC, blend gamma, shaper LUT, HDR multiplier, coefficient format, memory power, 3D LUT access, and test/debug registers. The chunk includes both RAM A/RAM B region programming patterns for gamma correction, blend gamma, and shaper LUTs, with per-channel B/G/R start, slope, base, end, offset, and region-pair registers.

## Control Flow

This header chunk has no branches, loops, calls, or initialization sequence. It is declarative hardware address data.

Runtime control flow is in the consumers:

1. DCN 3.0 resource, IRQ, GPIO, clock-manager, and DMUB code includes `dcn_3_0_0_offset.h`.
2. Resource code expands register-list macros such as `HUBP_REG_LIST_DCN30(id)` and `DPP_REG_LIST_DCN30(id)` for instances 0 through 5. For this chunk, `id` values 2 through 5 select the hub pipe and cursor offsets, while `id` values 0 and 1 select the DPP/CNVC/DSCL/CM offsets present here.
3. Generic hubp and dpp implementations use those register tables plus matching masks/shifts to perform MMIO reads and writes during modesets, plane programming, page flips, cursor updates, color pipeline updates, clock/power transitions, diagnostics, and interrupt handling.
4. Hardware sequencing is entirely outside this header. The macros do not say when a field is writable, double-buffered, sticky, read-only, write-one-to-clear, or dependent on clocks/power being enabled.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes GPU display hardware registers that hold volatile MMIO state.

The represented hardware state includes:

- Plane fetch state: surface format, alpha plane enable, tiling/swizzle/address-bank configuration, viewport geometry, luma/chroma pitch, primary/secondary surface addresses, metadata addresses, DCC/protection-related surface control, VMID, and current/earliest in-use addresses.
- Flip and timing state: surface flip control, flip interrupt status/ack paths, blanking and scaler destination parameters, prefetch settings, vblank/flip/nominal PTE and meta-row timing parameters, per-line delivery timing, and request expansion limits.
- VM and memory-system state: VM aperture bounds, L1 TLB control, DMDATA VM control, TTU/QoS watermarks, DRQ limits, request-size config, memory power controls/status, DET buffer state, and hub return read-line/underflow interrupts.
- Cursor and metadata state: cursor enable/mode/pitch, address, size, position, hot spot, stereo state, destination offset, cursor memory power, and DMDATA buffer address/control/QoS/status/software fields.
- DPP image-processing state: pixel format conversion, alpha handling, pre-degamma, color keying, pre-CSC, DSCL ratios/taps/line-buffer settings, color-management gamma/gamut/post-CSC/blend-gamma/shaper/3D-LUT state, HDR multiplier, and memory power status.
- Diagnostics and performance state: perfmon counter control/value registers, debug DB registers, test/debug index/data registers, clock measurement-window controls, read-line status, underflow status, and interrupt status/ack registers.

Persistence is determined by hardware behavior and driver sequencing outside the header. Configuration values usually remain until the next plane update, color update, modeset, power-gating transition, suspend/resume, or ASIC reset. Status and interrupt registers may be sticky, self-clearing, snapshot-like, or read-only. Names containing `*_STATUS`, `*_ACK`, `*_CLEAR`, `*_PENDING`, `*_INUSE`, `*_MEM_PWR_STATUS`, `*_READ_LINE_STATUS`, or `*_UNDERFLOW*` should be treated as side-effect-sensitive by consumers.

## Dependencies And Integration Points

This offset header is paired with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h`, which provides the field shifts and masks for these register offsets.

Direct include points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`

The closest register-table consumers are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`, which instantiates six `hubp_regs` entries with `HUBP_REG_LIST_DCN30(id)` and six `dpp_regs` entries with `DPP_REG_LIST_DCN30(id)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn30/dcn30_hubp.h`, which layers DCN 3.0 hubp registers over DCN 2.1 hubp lists and adds `HUBPREQ*_DCN_DMDATA_VM_CNTL`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h`, which uses `SRI(..., id)` to bind the DPP_TOP, CNVC_CFG, CNVC_CUR, DSCL, CURSOR0, and CM register names represented here.

The same generated offsets are also mirrored across nearby DCN 3.0.x offset headers such as `dcn_3_0_1_offset.h`, `dcn_3_0_2_offset.h`, and `dcn_3_0_3_offset.h`, making this chunk part of an ASIC-family hardware contract rather than isolated application logic.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong offset or base index will compile cleanly but can write the wrong MMIO register, producing blank scanout, corrupt planes, stuck flips, broken cursor state, incorrect color output, clock/power failures, or interrupt storms.
- Repeated instance blocks create drift risk. `HUBP2` through `HUBP5`, `HUBPREQ2` through `HUBPREQ5`, `HUBPRET2` through `HUBPRET5`, and `CURSOR0_2` through `CURSOR0_5` are mostly cloned with fixed instance stride. A single stale macro can fail only when enough displays or planes are active to use the affected pipe.
- DPP blocks are similarly repeated but this chunk ends partway through DPP instance 1. Whole-file research must merge later chunks before making complete claims about `CM1` or later DPP/display blocks.
- Surface and metadata address registers are split across low/high, luma/chroma, primary/secondary, and metadata variants. Mixing these offsets can scan out stale or wrong memory, break multi-plane formats, corrupt compressed surfaces, or trigger VM faults.
- Flip, interrupt, status, and clear/ack registers have side effects not represented in an offset header. Full-register writes or reads in the wrong sequence can lose an event, clear a pending flip, miss an underflow, or leave an interrupt asserted.
- QoS, prefetch, TTU, per-line delivery, DRQ, and timing registers are workload-sensitive. Offset mistakes may appear only under high resolution, high refresh, scaling, multiple planes, low memory clocks, or cursor-heavy workloads.
- Color pipeline registers include indexed LUTs, RAM A/B banks, per-channel start/end/slope/base fields, region pairs, and 3D-LUT data/control registers. Wrong offsets can cause subtle color errors that pass basic modeset testing but fail gamma, gamut, HDR, or color-management validation.
- Memory power and clock-control registers require sequencing with the DC power-management paths. Accesses while a block is gated or memories are powered down can return stale values or drop writes.

## Test Signals

Useful validation is a mix of compile-time table coverage and DCN 3.0 hardware behavior:

- Build AMDGPU/DC with DCN 3.0 support; missing or renamed macros should fail in `dcn30_resource.c`, hubp, dpp, IRQ, GPIO, clock-manager, or DMUB include paths.
- Diff this generated range against the authoritative AMD register database and sibling DCN 3.0.x headers, especially for instance stride consistency across hub pipe instances 2 through 5 and DPP instances 0 through 1.
- Exercise DCN 3.0 hardware with enough active pipes to use HUBP/CURSOR instances 2, 3, 4, and 5. Validate modesets, plane enable/disable, page flips, cursor movement, cursor size/format changes, hotplug, DPMS, suspend/resume, and multi-monitor layouts.
- Test RGB and YUV formats, luma/chroma plane programming, primary and secondary surfaces, metadata/DCC surfaces, protected/TMZ-capable paths where applicable, and VM fault reporting for bad surface addresses.
- Stress flip and timing paths: immediate flips, vblank-synchronized flips, flip interrupts, flip-away handling, triple-buffer-like paths, prefetch timing, low memory clock, high refresh, scaling, and multi-plane composition.
- Validate DSCL and DPP color behavior with scaling ratios, scaler taps, overscan, pre-CSC, pre-degamma, gamma correction, gamut remap, post CSC, blend gamma, shaper LUT, HDR multiplier, and 3D LUT programming.
- Use perfmon/debug tooling to start/stop the affected `DC_PERFMON*` counters, read high/low values, and check interrupt/status/ack behavior.
- Watch kernel logs and display diagnostics for hubp underflow, VM faults, DCC errors, missed flips, IRQ storms, cursor corruption, color regressions, power-gating resume failures, and pipe-specific failures.

## Cross-Chunk Notes

The first lines of this chunk are only the tail of the `DC_PERFMON7` offset block. The chunk also stops immediately after `CM1_CM_3DLUT_READ_WRITE_CONTROL_BASE_IDX`, so DPP instance 1 and the rest of the generated DCN 3.0.0 offset namespace continue in later chunks. The final per-file research document should reconcile adjacent chunks before presenting complete file-level coverage.

### subset-b-001682: lines 5204-7718

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 5204-7718

## Purpose

This chunk is generated AMDGPU DCN 3.0 register-offset metadata. It has no executable C logic; its API is a preprocessor namespace of MMIO register address offsets and per-register `*_BASE_IDX` constants for display pipe processor (DPP) blocks. The path sits under a local `ceph-client` source mirror, but the content is AMD display-driver hardware metadata rather than distributed filesystem code.

The range starts in the tail of the DPP1 color-management (`CM1`) block, at `CM_3DLUT` output and debug offsets. It then covers DPP2, DPP3, and DPP4 top/control, converter/cursor (`CNVC`), scaler (`DSCL`), color-management (`CM`), and DPP-local performance monitor blocks. The final section begins DPP5 and reaches into `CM5_CM_BLNDGAM_RAMA_*`; the remaining DPP5 blend-gamma offsets continue after this chunk.

All visible register offsets in this slice use `BASE_IDX` value `2`. The address-block comments identify instance base addresses for DPP2 at `0xb58`, DPP3 at `0x1104`, DPP4 at `0x16b0`, and DPP5 at `0x1c5c`; the associated DPP-local perfmon blocks use separate bases such as `0x3e3c`, `0x43e8`, `0x4994`, and `0x4f40`.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime storage objects in this range. The important surface is the macro contract consumed by AMD display register-list code:

- `mmDPP_TOP{2,3,4,5}_*`: DPP clock/control, soft reset, CRC value/control, and host-read control registers.
- `mmCNVC_CFG{2,3,4,5}_*`: converter and formatter offsets for surface pixel format, format control, floating-point scale/bias, color keyer, alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha.
- `mmCNVC_CUR{2,3,4,5}_*`: cursor control and cursor color/scale-bias offsets for cursor 0 within each DPP instance.
- `mmDSCL{2,3,4,5}_*`: scaler coefficient RAM, scaler mode/tap control, DSCL control/autocal/update, overscan, OTG blanking, recout/MPC size, line-buffer format and memory control/status, DSCL memory power, output-buffer control, and OBUF memory power offsets.
- `mmCM{2,3,4}_*`: complete color-management register groups for DPP instances 2 through 4, including CM control, de-alpha, post-CSC, gamut remap, bias, gamma correction (`GAMCOR`), blend gamma (`BLNDGAM`), shaper LUT, CM memory power/status, 3D LUT, and debug-index/data offsets.
- `mmCM5_*`: the beginning of the DPP5 color-management group, from `CM5_CM_CONTROL` through partial `CM5_CM_BLNDGAM_RAMA_*` coverage.
- `mmCM1_*`: only the tail of the DPP1 CM block in this chunk, covering `CM_3DLUT_OUT_NORM_FACTOR`, output offsets, and CM test debug index/data.
- `mmDC_PERFMON13_*` through `mmDC_PERFMON16_*`: DPP-local display performance monitor offsets for counter control, counter state, perfmon control, counted-value interrupt/misc, and low/high counter value registers.

These offsets are paired with the matching generated field header `dcn_3_0_0_sh_mask.h`. Resource code expands them through macros such as `SRI(...)` and DPP register-list definitions, while runtime DPP code uses generic `REG(...)`, `REG_READ`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` helpers against instance-specific register tables.

## Control Flow

This header chunk is declarative data and contains no branches, loops, calls, callbacks, or allocation paths. Runtime control flow is created by the AMD display driver around these constants:

1. DCN 3.0 resource setup includes `dcn_3_0_0_offset.h` and `dcn_3_0_0_sh_mask.h`, then builds per-instance DPP register tables with generated names such as `CNVC_CFG2_*`, `DSCL2_*`, and `CM2_*`.
2. Plane and pipe programming paths select a DPP instance and use the table to program pixel format, alpha behavior, pre-CSC, scaler parameters, recout size, line-buffer state, color transforms, gamma/3D LUTs, and cursor formatting.
3. Color-management paths in the DCN 3.0 DPP implementation read current LUT modes, choose RAM A or RAM B, write LUT index/data registers, update control registers, and manage CM memory power before and after programming.
4. Scaling paths program DSCL mode, taps, filter coefficients, scale ratios, initial phases, overscan, blanking, and memory power/status through the DSCL offsets.
5. Diagnostics and validation paths can read DPP CRC registers, host-read controls, perfmon counters, and CM debug index/data registers.

The offsets do not encode sequencing. Consumers must know when the DPP clock is enabled, when soft reset is allowed, when memory power has reached the expected state, and when double-buffered color or scaler changes latch.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It names MMIO-backed display hardware state.

The represented hardware state includes:

- DPP control state: clock enable/gating controls, block soft reset bits, CRC controls and CRC result registers, and host-read throttling.
- Converter and cursor state: surface pixel format, alpha-plane enablement, pre-dealpha/re-alpha, floating-point conversion scale/bias, color keying values, pre-CSC matrix registers, cursor mode/colors, and cursor scale/bias.
- Scaler state: coefficient RAM tap selection/data, horizontal and vertical scale ratios, initial phases, chroma/luma filter setup, manual replication, black color, overscan, recout and MPC dimensions, line-buffer format, line-buffer memory power/status, DSCL LUT memory power/status, and output-buffer behavior.
- Color pipeline state: CM bypass/control, dealpha and bias controls, post-CSC matrices, gamut remap matrices, `GAMCOR`, `BLNDGAM`, shaper, and 3D LUT index/data/control registers, LUT RAM A/B region descriptors, offsets, slopes, base values, and memory power/status registers.
- Performance and debug state: per-DPP perf counter control/state/value registers and CM debug index/data windows.

Persistence is hardware-defined. Configuration registers generally remain until a modeset, plane update, power-gating transition, suspend/resume, soft reset, or ASIC reset changes them. Registers named `*_STATUS`, `*_CURRENT`, `*_UPDATE_PENDING`, `*_CRC_VAL_*`, `*_PERFMON_*`, `*_TEST_DEBUG_*`, and memory-power fields may be read-only, sticky, snapshot, self-clearing, or side-effect-sensitive depending on the matching field definitions and hardware specification.

## Dependencies And Integration Points

The direct companion for this offset chunk is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h`

Observed include and consumer points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`, which includes the DCN 3.0 offset/mask headers and defines `SRI(reg_name, block, id)` for instance-specific register table construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.c`, which programs and reads CM, CNVC, and DSCL registers through generic DPP register tables. This includes gamma, blend gamma, shaper, 3D LUT, memory power, pixel format, and scaler behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h`, which defines the DPP register and field table shapes that bind generated offset macros with generated shift/mask macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`, which include the same generated DCN 3.0 register contract for IRQ and DMUB-facing display hardware access.

Higher-level integration is through DC plane, color, cursor, scaling, and mode-setting code. DML bandwidth calculations model DPP/CNVC/DSCL timing, while DPP runtime code turns selected plane state into MMIO writes using these generated offsets.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong offset or wrong instance suffix can compile cleanly while programming the wrong DPP, causing blank planes, incorrect colors, bad scaling, cursor artifacts, missed CRC/perfmon reads, or hangs during power transitions.
- The repeated DPP2, DPP3, DPP4, and DPP5 blocks are copy-patterned. Instance drift is a major risk: one bad `CM3` or `DSCL4` offset may only appear with enough active displays or planes to use that instance.
- This chunk has artificial boundaries. It starts after most DPP1 CM offsets and ends before the complete DPP5 CM blend-gamma block, so whole-file analysis must merge adjacent chunks before claiming full instance coverage.
- LUT programming is stateful. `*_LUT_INDEX`, `*_LUT_DATA`, `*_LUT_CONTROL`, RAM A/B selection, region descriptors, and current-mode bits require careful sequencing; racing updates or selecting the active RAM can show visible color corruption.
- Power and reset offsets are side-effect-sensitive. `DPP_SOFT_RESET`, `DPP_CONTROL`, `CM_MEM_PWR_CTRL*`, `DSCL_MEM_PWR_CTRL`, and `OBUF_MEM_PWR_CTRL` interact with clock gating and memory power states; writes while a block is disabled may be dropped or stall.
- DSCL programming is timing-sensitive. Incorrect scaler ratio, filter-init, recout, blanking, or line-buffer offsets can fail only for scaled, 4:2:0, high refresh, rotated, or multi-plane modes.
- Color pipeline registers are packed by function but not by safety. Mixing post-CSC, gamut remap, gamma correction, blend gamma, shaper, and 3D LUT offsets across instances can produce subtle color-management failures that are hard to distinguish from userspace color bugs.
- Debug, CRC, and perfmon registers may have read side effects or latch requirements. Generic polling or full-register writes to diagnostic registers should be checked against the field header and hardware programming guide.

## Test Signals

Useful validation is compile-time plus DCN 3.0 display behavior:

- Build AMDGPU/DC with DCN 3.0 enabled; missing or renamed macros should fail in `dcn30_resource.c`, `dcn30_dpp.*`, IRQ service code, or DMUB DCN 3.0 code.
- Diff the generated offsets against AMD's DCN 3.0 register database and adjacent DCN family headers to catch per-instance drift across `DPP_TOP`, `CNVC_CFG`, `CNVC_CUR`, `DSCL`, `CM`, and `DC_PERFMON` groups.
- Exercise multi-pipe hardware with enough active planes/displays to use DPP2, DPP3, DPP4, and DPP5. Validate modesets, hotplug, DPMS, suspend/resume, plane enable/disable, page flips, cursor movement, and cursor format changes.
- Test scaler-heavy modes: up/down scaling, 4:2:0 content, chroma scaling, overscan, recout sizing, line-buffer pressure, high refresh, and multiple active planes. Watch for underflow, flicker, cropping, or corruption.
- Test color-management paths: post-CSC, gamut remap, degamma/gamma, blend gamma, shaper LUT, 3D LUT, RAM A/B switching, bypass modes, and memory power transitions.
- Use CRC and perfmon/debug paths where available to confirm `DPP_TOP*_DPP_CRC_*`, `CM*_CM_TEST_DEBUG_*`, and `DC_PERFMON13` through `DC_PERFMON16` offsets map to the expected DPP instances.
- Monitor kernel logs for DC underflow, timeout, page fault, IRQ storm, power-gating, or pipe-specific errors that appear only on higher-numbered DPP instances.

## Cross-Chunk Notes

Previous chunks define the earlier DPP1 and likely DPP0/DPP1 top, CNVC, DSCL, and CM offsets. Later chunks continue the DPP5 color-management block after `CM5_CM_BLNDGAM_RAMA_END_CNTL2_B`. The merge lane should combine adjacent chunks before making complete claims about all DCN 3.0 DPP instances or the full DPP5 CM register set.

### subset-b-001683: lines 7719-10374

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 7719-10374

## Scope

This chunk is a generated AMD DCN 3.0 register-offset header segment. It contains preprocessor register address macros, not executable C logic. The range starts in the middle of the DPP5 color-management block at `mmCM5_CM_BLNDGAM_RAMA_END_CNTL1_G` and ends mid-way through the DIO DisplayPort AUX2 block at `mmDP_AUX2_AUX_GTC_SYNC_ERROR_CONTROL_BASE_IDX`.

The chunk defines 2,396 macros: 1,198 `mm...` register-offset macros and 1,198 matching `..._BASE_IDX` macros. Every visible register offset has a paired base-index macro, and all visible `_BASE_IDX` values are `2`, meaning consumers combine each register offset with segment 2 of the DCN base table.

## Purpose

The purpose of this header region is to provide ASIC-specific symbolic addresses for DCN 3.0 display hardware. These symbols let the AMDGPU display stack build register tables for:

- DPP5 color management and gamma/shaper/3D LUT programming.
- DPP5 DC performance counters.
- Six OPP output-pixel-processing instances, including FMT, DPG, OPPBUF, OPP pipe control, and OPP pipe CRC blocks.
- OPP top-level controls, DSC remap forwarding, and OPP performance counters.
- Six ODM input instances and six OTG timing-generator instances.
- OPTC miscellaneous and performance counter registers.
- DIO I2C/DDC, DIO scratch/power/clock/interrupt registers, six HPD instances, DIO performance counters, and the first three DP AUX register groups, with the third group truncated by the chunk boundary.

The macros are consumed by DC, DMUB, IRQ, GPIO, resource, DIO, OPP, and OPTC code through register-list and bitfield-list macros. They form the numeric address layer beneath typed structures such as OPP, OPTC, AUX, HPD, and IRQ services.

## Important Macro Families

### DPP5 Color Management

Lines 7719-7984 finish the DPP5 `CM5` register set. They cover blend gamma RAM A/B control and region registers, HDR multiplier, color-management memory power control/status, dealpha and coefficient format, shaper offset/scale/LUT access, shaper RAM A/B region programming, 3D LUT mode/index/data/read-write controls, output normalization and offsets, and test debug index/data registers.

These names match color-management helper patterns used elsewhere in the display code, where generated `REG(...)` values are assigned into gamma/shaper/LUT register tables. The visible chunk only covers instance 5; earlier chunks should contain `CM0` through `CM4` and the beginning of `CM5`.

### DC Performance Counters

The chunk contains three performance monitor groups:

- `DC_PERFMON17_*` for DPP5 performance counting.
- `DC_PERFMON18_*` for OPP performance counting.
- `DC_PERFMON20_*` for DIO performance counting.

Each group contains counter control, secondary control, state, monitor control, current-value, high, and low result registers. These offsets are used by generic DC perf counter code to select hardware blocks and read accumulated values.

### OPP/FMT/DPG/OPPBUF/CRC Instances

Lines 8007-8498 define six repeated OPP instance groups using base addresses `0x0`, `0x168`, `0x2d0`, `0x438`, `0x5a0`, and `0x708`.

For each instance `0` through `5`, the chunk provides:

- `FMTn_*` registers for clamp components, dynamic expansion, format control, bit-depth control, dither random seeds, clamp control, side-by-side stereo, 4:2:0 memory control, and 4:2:2 control.
- `DPGn_*` registers for display pattern generator control, ramp control, dimensions, color channels, offset segment, and status.
- `OPPBUFn_*` registers for OPP buffer control and 3D parameters.
- `OPP_PIPEn_OPP_PIPE_CONTROL`.
- `OPP_PIPE_CRCn_*` control, mask, and three result registers.

These definitions are integration-critical for output formatting, dithering, test-pattern generation, output-buffer behavior, CRC validation, and pipe-level status/control.

### OPP Top, DSCRM, ODM, and OTG

The OPP top block exposes `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`, followed by `DSCRM0` through `DSCRM5` DSC-forwarding configuration registers. These are routing/forwarding controls around the output processor and display stream compression path.

The ODM input blocks, `ODM0` through `ODM5`, each define global control, source select, data format, bytes-per-pixel, width, input clock, memory config, and spare registers. Their base addresses advance by `0x40`. These symbols support output data merger configuration, especially multi-pipe or high-bandwidth display modes.

The OTG blocks, `OTG0` through `OTG5`, are the largest portion of the chunk. Each repeated instance covers horizontal and vertical totals, blanking, sync, trigger controls, force-count, flow, stereo, control, blanking, interlace, readback, status, counters, snapshot, interrupts, update locks, double buffering, master enable, blank color, CRC windows/results, static-screen detection, 3D structure, global sync lock, manual triggers, DRR timing, DTO constants, request control, DSC start position, pipe update status, and spare registers.

These are timing-generator registers. Display mode programming, vblank/vertical interrupt scheduling, dynamic refresh-rate changes, stereo/interlace handling, CRC capture, and global-sync coordination all depend on these offsets being correct.

### DIO, HPD, I2C/DDC, and AUX

The DIO portion begins at line 10047. It defines:

- `DC_I2C_*` control, arbitration, interrupt, software status, six DDC hardware status registers, six DDC speed/setup pairs, transaction slots, data, EDID detection, and read-request interrupt.
- `DIO_*` scratch registers, memory power controls/status, clock controls, power-management control, generic interrupt message/clear, and `DIG_SOFT_RESET`.
- `HPD0` through `HPD5` interrupt status/control, HPD control, fast-train control, and toggle filter controls, with instance base addresses stepping by `0x20`.
- `DP_AUX0`, `DP_AUX1`, and the start of `DP_AUX2` AUX-control groups, including software/low-speed data and status, arbitration, interrupt control, DPHY TX/RX controls and status, GTC sync controls/status, and PHY wake control where the full instance is visible.

The chunk ends before completing `DP_AUX2`; later chunks should contain the rest of AUX2 plus additional AUX instances if present.

## APIs, Types, and Functions

This header segment declares no C functions, structs, enums, or storage. Its API surface is preprocessor-only:

- `mm<block>_<register>` expands to a register offset.
- `mm<block>_<register>_BASE_IDX` expands to the DCN base segment index used with the offset.
- Consumers commonly transform these through macros such as `REG_OFFSET(reg_name)`, `REG(reg)`, `BASE(...)`, `OPP_SF(...)`, `AUX_SF(...)`, `LE_SF(...)`, and `SF(...)`.

Observed in-tree integration examples include:

- `dmub/src/dmub_dcn30.c` and `dmub/src/dmub_dcn302.c` include this header and use `REG_OFFSET_EXP`/`BASE_INNER` to build DMUB register offsets.
- `dc/irq/dcn30/irq_service_dcn30.c`, `dc/gpio/dcn30/*`, `dc/resource/dcn30/dcn30_resource.c`, and `dc/clk_mgr/dcn30/dcn30_clk_mgr.c` include this header directly for DCN 3.0 register programming.
- `dc/opp/dcn10/dcn10_opp.h` references fields under registers such as `FMT0_FMT_CONTROL`.
- `dc/optc/dcn30/dcn30_optc.h` references OTG timing registers such as `OTG0_OTG_H_TOTAL`.
- `dc/dce/dce_aux.h` and `dc/dio/dcn10/dcn10_link_encoder.h` reference AUX and HPD fields under registers such as `DP_AUX0_AUX_CONTROL` and `HPD0_DC_HPD_INT_STATUS`.

## Control Flow

There is no runtime control flow in this chunk. Runtime behavior emerges when driver code expands these macros into register tables and then calls MMIO read/write helpers. The effective flow is:

1. A DCN 3.0 source file includes this offset header and the matching shift/mask header.
2. Register-list macros instantiate per-block register address tables.
3. Hardware object constructors attach those tables to block-specific objects such as OPP, OPTC, AUX, HPD, IRQ, GPIO, and DMUB interfaces.
4. Mode-setting, link training, hotplug, color-management, CRC, perfmon, or interrupt code reads or writes the computed MMIO addresses.

Because the header is generated and flat, the important control-flow invariant is compile-time naming consistency: the same symbolic register names must exist in offset, shift, and mask headers and must match the register-table macros expected by consumers.

## State and Persistence Behavior

The macros themselves are stateless and create no persistence. They describe persistent hardware register locations whose values live in the GPU display engine until changed by driver writes, hardware state machines, reset, power gating, or suspend/resume transitions.

Important hardware state represented by this chunk includes:

- DPP5 color LUT/gamma/shaper/3D LUT state.
- OPP format, dithering, clamp, buffer, CRC, and pattern-generator state.
- OTG mode timing, vertical interrupt, CRC, global sync, DRR, and update-lock state.
- ODM input routing/format/clock/memory configuration.
- DIO I2C transaction state, HPD sense/interrupt state, AUX transaction/PHY/GTC sync state, and DIO power/clock state.
- Performance counter configuration and accumulated counter values.

Driver suspend/resume, display mode transitions, link retraining, HPD handling, and color pipeline updates must restore or reprogram these hardware registers through higher-level DC code. The header only provides addresses for that work.

## Dependencies

This chunk depends on the rest of the generated DCN 3.0 ASIC register set:

- Earlier/later chunks of `dcn_3_0_0_offset.h` for other blocks, full include guards, and complete macro coverage.
- Matching `dcn_3_0_0_sh_mask.h` or related generated shift/mask headers for bit positions and masks.
- DCN base-address definitions such as `DCN_BASE__INST0_SEG2` and `BASE(...)` macros in consumers.
- Register access abstractions in AMDGPU DC and DMUB code.
- Hardware documentation or generation inputs that guarantee the numeric offsets match the ASIC.

All visible `_BASE_IDX` values are `2`, so any consumer using these macros must provide a valid base segment 2. A mismatch between base segment values and these offsets would shift every register access in this chunk to the wrong address range.

## Integration Points

Key integration points by subsystem:

- DPP/color: gamma, blend gamma, shaper, 3D LUT, HDR multiplier, and color-memory power control programming.
- OPP/output: FMT output format controls, dithering, clamp, 420/422 behavior, DPG test patterns, OPPBUF, OPP pipe control, and OPP CRC readback.
- OPTC/OTG: timing programming, vblank interrupts, update locks, global sync, DRR, CRC windows, snapshots, stereo/interlace state, and DSC timing alignment.
- ODM: multi-pipe output-merger input routing, format, width, and memory configuration.
- DIO/link: DDC/I2C EDID access, HPD interrupt/sense handling, AUX transactions, link encoder reset/fast training, and DIO clock/power controls.
- Perfmon: DC performance counter selection and readback for DPP, OPP, and DIO blocks.
- DMUB: firmware-side or DMUB-mediated register offset tables for DCN 3.0/3.0.2 paths that include this offset header.

## Risks and Failure Modes

- Incorrect numeric offsets can silently write the wrong hardware register, causing display corruption, failed modesets, broken link training, missed hotplug interrupts, bogus CRCs, or hangs.
- Missing or mismatched `_BASE_IDX` macros break `BASE(mm..._BASE_IDX) + mm...` expansion or send accesses to the wrong segment.
- Instance repetition creates copy/paste or generator risks: one bad stride among `FMTn`, `OTGn`, `HPDn`, or `DP_AUXn` instances could affect only a subset of pipes/connectors and be hard to detect.
- This chunk starts and ends mid-block. The first visible `CM5` macros require earlier chunk context for the start of the DPP5 color-management block, and `DP_AUX2` requires later chunk context for full AUX2 coverage.
- Field definitions are not present here. A correct offset with an incorrect shift/mask definition in the companion header can still corrupt register programming.
- Some register names are shared conceptually across DCN generations but not always at the same offset. Cross-generation reuse must include the correct generated header for the active ASIC family.
- Power-gated or clock-gated blocks such as DPP/OPP/DIO can reject or lose register accesses unless higher-level code sequences power and clocks correctly before using these offsets.

## Test Signals

Useful validation signals for this chunk include:

- Build-time success for DCN 3.0 and DCN 3.0.2 display code that includes `dcn_3_0_0_offset.h`; missing macro names should fail compilation in register-list initializers.
- Static generated-header checks that every `mm...` register macro in this range has exactly one matching `_BASE_IDX`, and that visible base indices are expected for DCN segment 2.
- Display modeset smoke tests across all six pipes to exercise `OTG0` through `OTG5`, `FMT0` through `FMT5`, and `OPP_PIPE_CRC0` through `OPP_PIPE_CRC5` address tables.
- CRC tests using OPP pipe CRC and OTG CRC registers to confirm readback changes with known test patterns.
- Hotplug and HPD interrupt tests across six connectors where available, checking `HPD0` through `HPD5` sense and interrupt behavior.
- DDC/EDID and DisplayPort AUX transaction tests covering `DC_I2C_*`, `DP_AUX0`, `DP_AUX1`, and, after later chunk completion, full `DP_AUX2` and remaining AUX instances.
- Color pipeline tests that program DPP5 blend gamma, shaper LUT, and 3D LUT state and compare output CRCs or visual/colorimetry results.
- Suspend/resume and power-gating tests that verify DPP/OPP/OTG/DIO register state is restored through higher-level DC programming.

## Cross-Chunk Notes

This is only one chunk of a larger generated header. The final per-file research report should merge this with adjacent chunks to recover:

- Header-level include guards and generation provenance.
- Earlier DCN base segment and register-block definitions.
- The full DPP5 block start before line 7719.
- The remainder of `DP_AUX2` and any later DIO/AUX/link-encoder blocks after line 10374.
- Whole-file comparisons against companion shift/mask headers and DCN 3.0 resource table construction.

### subset-b-001684: lines 10375-12949

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 10375-12949

## Purpose

This chunk is generated AMD DCN 3.0 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic display-controller register names to numeric MMIO offsets and companion base-index selectors. Consumers combine each `mm...` offset with its matching `mm..._BASE_IDX` to form the absolute register address for DCN 3.0 display hardware.

The range is a mid-file slice of `dcn_3_0_0_offset.h`. It starts at the tail of the `DP_AUX2` AUX/GTC/wake registers, covers complete `DP_AUX3` through `DP_AUX5` blocks, covers the repeated stream-output families for DIG/DP/VPG/AFMT/DME instances 0 through 5, covers DCIO GPIO/DDC/AUX pad control, and then enters the DSC register map for DSC instance 0 and the beginning of DSC instance 1. The requested range contains 2,410 `#define` lines: 1,205 register-offset macros and 1,205 matching `_BASE_IDX` macros.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locking primitives in this range. The interface is the generated macro namespace:

- `mm<block>_<register>`: a DCN 3.0 MMIO register offset.
- `mm<block>_<register>_BASE_IDX`: the base-address segment selector used by helper macros such as `BASE(mm..._BASE_IDX) + mm...`, `SR(...)`, `SRI(...)`, and DMUB `REG_OFFSET(...)`.

Every visible register offset in this chunk has a matching `_BASE_IDX`, and all `_BASE_IDX` values in the requested range are `2`. That value is part of the ABI between this generated header and the SOC15/DCN base-address tables; the numeric offset alone is not enough to address hardware safely.

Major macro families in this slice:

- `DP_AUX2` tail and complete `DP_AUX3`, `DP_AUX4`, `DP_AUX5`: AUX transaction control, software/low-speed status and data, DPHY TX/RX controls and status, GTC sync control/status/error registers, interrupt control, arbitration, and PHY wake control.
- `VPG0` through `VPG5`: generic packet access/data, generic-stream-packet frame/immediate update controls, status, memory power, ISRC access/data, and MPEG info registers used for secondary-data packet generation.
- `AFMT0` through `AFMT5`: audio/VBI packet control, HDMI/DP audio info, IEC 60958 channel status words, ramp controls, audio CRC, interrupt/status, audio source selection, infoframe control, and AFMT memory power.
- `DME0` through `DME5`: Display Micro Engine control and memory-control offsets.
- `DIG0` through `DIG5`: front-end/back-end control, output CRC, test and clock patterns, FIFO status, HDMI packet/audio/ACR/control/status registers, AFMT bridge control, TMDS control and symbols, lane enable, version, and forced disable.
- `DP0` through `DP5`: DisplayPort link and stream configuration, MSA colorimetry/timing/misc/VBID, video `M/N`, DPHY and link framing, HBR2 pattern, video interrupt control, training/lane/PHY status and test registers, secondary-data packet control, DPCSTX debug and PHY-control registers, MST and SEC packet controls, CRC, pixel-format, and VC payload-allocation registers.
- `DCIO`, `LVTMA`, `UNIPHYA` through `UNIPHYF`, and `DC_GPIO*`: link/backlight/panel-power, DCIO debug/mux, pad-strength and polarity controls, GPIO masks/data/enable/pull-up/AUX controls, and AUX/I2C pad power-good state.
- `DSC_TOP0`, `DSCCIF0`, `DSCC0`, `DC_PERFMON21`, `DSC_TOP1`, `DSCCIF1`, and partial `DSCC1`: display stream compression top/control/debug, DSC client interface config, compressor config/status/interrupt, PPS config registers, memory power, error counters, rate-buffer fullness counters, debug bus selectors/data, and DSC-local perfmon registers.

## Control Flow

This header has no runtime control flow. Runtime code supplies the sequencing:

1. DCN 3.0 resource, IRQ, GPIO, DIO, DSC, and DMUB code includes `dcn_3_0_0_offset.h` together with the matching `dcn_3_0_0_sh_mask.h`.
2. Register-list macros paste instance IDs into names such as `mmDIG4_HDMI_CONTROL`, `mmDP2_DP_LINK_CNTL`, `mmVPG1_VPG_GENERIC_PACKET_DATA`, or `mmDSCC0_DSCC_PPS_CONFIG0`.
3. Helper macros add the base segment selected by `*_BASE_IDX` to the offset and store the result in per-block register tables.
4. Driver code later uses those tables with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and wait/poll helpers to program links, packet generators, audio formatting, AUX/DDC, GPIO, panel power, and DSC.

The macros do not encode ordering requirements. Consumers must still sequence clock/power enablement, link training, AUX arbitration, hotplug handling, audio packet setup, double-buffered packet updates, DSC PPS programming, interrupt clear/ack behavior, and suspend/resume restoration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing. It describes MMIO-backed GPU state. The represented hardware state includes:

- AUX channel state for DisplayPort DPCD/EDID transactions, low-speed data movement, DPHY TX/RX status, GTC sync, interrupts, arbitration, and wake control.
- Stream encoder state for HDMI/TMDS and DP output: lane enable, front-end/back-end control, test patterns, CRC capture, FIFO status, HDMI generic packets, metadata packets, audio clock regeneration, TMDS symbols, and DP link/stream/secondary-packet/MST controls.
- Infoframe/audio packet state in `VPG*` and `AFMT*`, including generic packets, ISRC/MPEG metadata, audio-info fields, channel-status words, CRC/status, and memory-power state.
- DCIO and GPIO state for link routing, panel/backlight power, AUX/DDC pad control, GPIO masks/data/enables, pull-up configuration, mux/debug selection, and pad power-good reporting.
- DSC state for compressor enable/config, PPS payload registers, memory power, interrupt/status, rate-buffer fullness, error counters, debug buses, and DSC perfmon counters.

Persistence is hardware-defined. Configuration registers usually retain values until modeset, link reconfiguration, power gating, suspend/resume, or ASIC reset. Status, interrupt, debug, counter, clear/ack, wake, and power-status registers may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. This header does not distinguish those behaviors; the companion mask header and consuming driver code provide the field-level semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h` for field shifts and masks.
- SOC15/DCN base-address headers that define `DCN_BASE__INST0_SEG2` and related segment constants consumed by `BASE(mm..._BASE_IDX)`.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

The primary integration pattern is token-pasting register construction. DCN resource files define macros such as `SR(reg_name)` and `SRI(reg_name, block, id)` that expand to `BASE(mm..._BASE_IDX) + mm...`. DMUB uses `REG_OFFSET(reg_name)` in `dmub_reg.h` with the same address contract. GPIO translate/factory code maps logical pins, AUX channels, DDC lines, HPD lines, panel power, and backlight control to concrete `mmDC_GPIO*`, `mmAUX*`, and DCIO offsets.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. These macros are untyped constants, so a wrong `mm...` value or `_BASE_IDX` can compile cleanly while programming the wrong MMIO register or segment.
- Repeated instance families are copy-sensitive. `DIG0`-`DIG5`, `DP0`-`DP5`, `VPG0`-`VPG5`, `AFMT0`-`AFMT5`, and `DME0`-`DME5` are structurally similar but not interchangeable; an instance-specific typo may only fail on one connector or multi-display configuration.
- The chunk boundaries are artificial. The first lines are only the tail of `DP_AUX2`, and the final line stops inside `DSCC1_PPS_CONFIG11`; adjacent chunks are required for full file-level coverage.
- AUX/DDC and GPIO registers are side-effect-sensitive. Incorrect status/interrupt/clear/wake handling can break hotplug, EDID reads, DPCD transactions, panel wake, or low-power resume.
- Link-training and packet registers interact with timing and link state outside this header. Bad DP/TMDS/HDMI/AFMT/VPG offsets can cause blank displays, audio loss, CRC mismatch, infoframe corruption, MST payload errors, or failures limited to specific link rates and lane counts.
- DSC programming is stateful and format-sensitive. Wrong PPS, memory-power, status, interrupt, or debug offsets can produce compressed-stream corruption, link bandwidth failures, or pipe-specific issues when DSC is enabled.
- Power and memory-control offsets are high risk because writes may be ignored or harmful when the relevant display block is gated, reset, or clock-disabled.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.0.2 support enabled; missing or renamed macros should fail in resource, IRQ, GPIO, DIO, DSC, and DMUB register-table construction.
- Mechanically verify that every non-`_BASE_IDX` `mm...` macro in lines 10375-12949 has exactly one matching `_BASE_IDX` macro and that all base-index values remain `2`.
- Diff this chunk against AMD's authoritative DCN 3.0 register database and nearby generated headers such as `dcn_2_1_0_offset.h` or later DCN 3.x headers where compatibility is expected.
- Exercise systems with enough active displays to use high-numbered instances: DP/HDMI link training on `DIG`/`DP` instances 0 through 5, hotplug, EDID/DDC, AUX DPCD reads/writes, MST, link-rate/lane-count changes, and suspend/resume.
- Validate stream packets and audio: HDMI and DP audio playback, audio clock regeneration, infoframes, generic packets, ISRC/MPEG metadata, CRC capture, and packet update timing.
- Test GPIO/DCIO paths for panel power, backlight, DDC/AUX pad routing, HPD behavior, pull-up controls, and low-power wake.
- Enable DSC on capable panels and verify modesets, PPS programming, stream stability, rate-buffer/fullness counters, interrupt/status handling, and visual integrity at high bandwidth.
- Watch kernel logs and display diagnostics for AUX timeouts, hotplug storms, link-training failures, audio dropouts, CRC mismatches, underflow, DSC errors, stuck interrupts, and resume failures.

## Cross-Chunk Notes

Previous chunks own the beginning of the DCN 3.0 DIO/AUX area, including most of `DP_AUX2`. Later chunks continue `DSCC1` after `DSCC1_PPS_CONFIG11` and cover the remaining DCN 3.0 register-offset namespace. The final per-file research document should merge adjacent chunks before making complete claims about all AUX channels, all DSC instances, or the complete `dcn_3_0_0_offset.h` hardware map.

### subset-b-001685: lines 12950-15501

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 12950-15501

## Purpose

This chunk is part of AMDGPU's generated DCN 3.0.0 register-offset header. It maps symbolic `mm...` register names to MMIO offsets plus `..._BASE_IDX` values for several display engine blocks. The values are not executable logic; they are compile-time constants consumed by display-core register-list macros so higher-level DCN code can use `REG_SET`, `REG_UPDATE`, `REG_GET`, `SR`, `SRI`, `SRII`, and field-mask helpers without hard-coding addresses.

The covered slice starts in the middle of DSC encoder instance 1 and then covers DSC instances 2-5, DWB0, MPC MPCC instances 0-5, MPC output gamma and output CSC blocks, and the beginning of the MPC RMU shaper table block.

## Register Blocks Covered

- DSC / DSCC:
  - Tail of `DSCC1_DSCC_*`, beginning at `DSCC_PPS_CONFIG12`, through rate-buffer fullness and debug registers.
  - Full repeated blocks for `DSC_TOP2` through `DSC_TOP5`, `DSCCIF2` through `DSCCIF5`, `DSCC2` through `DSCC5`, and per-DSC performance monitors `DC_PERFMON22` through `DC_PERFMON25`.
  - These define PPS packet fields, compression status, interrupt/status registers, memory power control, error counters, and rate-buffer fullness/debug registers for display stream compression.
- DWB0:
  - `DWB_ENABLE_CLK_CTRL`, memory power, frame-capture controls, window/source geometry, CRC controls, output format/denorm controls, MMHUBBUB backpressure counters, host-read and reset controls.
  - `DWBCP` color-processing registers for HDR multiplier, gamut remap matrices, output gamma LUT access, RAMA/RAMB region programming, and debug hooks.
- MPC / MPCC:
  - `MPCC0` through `MPCC5` blending pipes, each with mux, control, status, top/bottom gain, memory power, background color, ALU status, and debug registers.
  - `MPCC_OGAM0` through `MPCC_OGAM5` output-gamma and gamut-remap blocks, including LUT index/data/control, coefficient-format/remap mode, matrix coefficients, RAMA/RAMB piecewise-linear region parameters, offsets, base/slope/end controls, memory power, and debug registers.
- MPC configuration and output:
  - `MPC_MUX`, `MPC_OUT_MUX`, cursor vupdate lock, DWB mux selection, debug/status, and clock-gating configuration.
  - `MPC_OUT0` through `MPC_OUT5` output CSC matrix registers, with A/B coefficient banks for each output.
- MPC RMU:
  - The chunk ends after the start of `dce_dc_mpc_mpc_rmu_dispdec`, covering `MPC_RMU_CONTROL`, `MPC_RMU_MEM_PWR_CTRL`, and early `MPC_RMU0_SHAPER_*` registers through RAMA region programming.

## Important APIs, Types, and Macros

There are no functions or C types defined in this chunk. The important interface is the naming contract:

- `#define mm<block>_<register> <offset>` gives a register offset.
- `#define mm<block>_<register>_BASE_IDX <idx>` selects the register-base segment used by `BASE(...)`.
- Consumers combine the two as `BASE(mm..._BASE_IDX) + mm...`, typically through macros such as `SR(...)`, `SRI(...)`, `SRII(...)`, and DCN-specific variants.
- Field positions and masks are supplied separately by `dcn_3_0_0_sh_mask.h`.

Observed integration points include:

- `display/dc/dsc/dcn20/dcn20_dsc.h` builds DSC register lists with `SRI(DSC_TOP_CONTROL, DSC_TOP, id)`, `SRI(DSCC_PPS_CONFIG*, DSCC, id)`, and `SRI(DSCCIF_CONFIG*, DSCCIF, id)`. `dcn20_dsc.c` then programs PPS, slice geometry, rate-control fields, clock enables, and status reads through `REG_SET_*`, `REG_UPDATE`, and `REG_GET`.
- `display/dc/dwb/dcn30/dcn30_dwb.h` builds the DWB register table from these offsets, and `dcn30_dwb.c` uses them to enable/disable writeback, lock updates, program frame capture, color processing, denorm, CRC, and status reads.
- `display/dc/mpc/dcn30/dcn30_mpc.h` builds MPCC, MPC output, DWB mux, and RMU register tables from this chunk. The MPC code uses the resulting tables for plane composition, blending, output color conversion, output gamma, RMU shaper/3D LUT programming, and memory-power state checks.
- `display/dmub/src/dmub_dcn30.c` and `dmub_dcn302.c` include this offset header for DMUB-facing DCN 3.0 register access.

## Control Flow

The header itself has no runtime control flow. Runtime flow is indirect:

1. DCN 3.0 resource construction expands register-list macros into per-block `uint32_t` register tables.
2. Display algorithms select instances such as DSC2, MPCC4, DWB0, or MPC_OUT3.
3. Register helpers read or write `BASE(base_idx) + offset`.
4. Paired mask/shift definitions isolate fields inside each register.

The repeated instance layout is central to that flow. DSC instance offsets progress by instance base (`0x2e0`, `0x450`, `0x5c0`, `0x730` in this slice for instances 2-5), MPCC blocks are spaced by instance base (`0x0`, `0x80`, `0x100`, ...), MPCC_OGAM blocks are spaced by larger blocks (`0x0`, `0x200`, ...), and MPC_OUT CSC registers are contiguous per output.

## State and Persistence Behavior

All state controlled by these definitions lives in GPU display hardware registers, not in kernel memory owned by this header. Persistence is therefore hardware/register-lifetime state:

- DSC PPS/config/status registers affect active Display Stream Compression programming until reprogrammed, reset, or power-gated.
- DWB update-lock and frame-capture bits gate when writeback changes become active. DWB CRC and backpressure counters expose hardware diagnostic state.
- MPCC control, mux, alpha/gain, background color, and OGAM LUT/region registers define active composition and color pipeline state for each MPCC instance.
- MPC output CSC registers hold output color-space conversion coefficients per output.
- RMU shaper LUT and memory-power registers preserve color-management table state while the relevant memory is powered and valid.

The `_BASE_IDX` values matter because they place the same logical register names into the correct MMIO aperture. A wrong base index can write a valid-looking offset into the wrong hardware block.

## Dependencies

- Paired field metadata from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h`.
- DCN register-access macro framework in AMD display core (`REG_SET`, `REG_UPDATE`, `REG_GET`, `SR`, `SRI`, `SRII`, and related instance helpers).
- Hardware-specific base-address mapping behind `BASE(idx)`.
- Block-level DCN implementations for DSC, DWB, MPC, MPCC, OGAM, and RMU.
- Generated-register naming consistency across offset, mask/shift, and driver register-list headers.

## Risks and Edge Cases

- This chunk begins and ends inside logical blocks: it starts after earlier `DSCC1` PPS registers and ends in the middle of `MPC_RMU0_SHAPER_*`. Any final per-file summary must reconcile adjacent chunks for complete block coverage.
- Offset or base-index drift between `dcn_3_0_0_offset.h` and `dcn_3_0_0_sh_mask.h` can silently corrupt field writes, because the compiler only sees integer constants.
- Instance-copy mistakes are high impact. The repeated DSC, MPCC, OGAM, and MPC_OUT patterns differ mainly by prefix and base address, so a wrong instance macro can program the wrong pipe or compressor.
- Color-management registers are table-oriented and double-buffered/status-sensitive in consumers. Misordered LUT index/data/control writes can produce wrong gamma, gamut, or shaper state even when offsets compile.
- DWB controls include update locks, capture enable, CRC, and backpressure counters. Bugs here may manifest as missed captures, stale writeback frames, or misleading diagnostics.
- Memory-power registers for DSCC, DWB OGAM, MPCC OGAM, and RMU must align with code that waits for or checks power state. Bad offsets can look like timeout, blank output, or color-pipeline failure.

## Test Signals

- Build coverage: compile AMDGPU display code for DCN 3.0 paths to catch missing or renamed macros in DSC, DWB, MPC, and DMUB consumers.
- Register-table sanity: compare generated register tables against expected ASIC register maps, especially repeated instance spacing for `DSCC2-5`, `MPCC0-5`, `MPCC_OGAM0-5`, and `MPC_OUT0-5`.
- Display Stream Compression validation: modes requiring DSC should program PPS registers, enable DSC clocks, and avoid DSCC rate-buffer overflow/underflow interrupt/status bits.
- DWB validation: enable/update/disable writeback paths should toggle `DWB_ENABLE` and `FC_FRAME_CAPTURE_EN`, honor `DWB_UPDATE_LOCK`, produce expected CRC values, and avoid unexpected MMHUBBUB backpressure.
- Composition validation: multi-plane blending, alpha/gain programming, and MPCC mux changes should affect the intended MPCC instance only.
- Color validation: output CSC, MPCC OGAM, DWB OGAM, and RMU shaper programming should be checked with color pipeline tests or CRC/reference-frame comparisons.
- Power-management validation: suspend/resume, display idle, and memory power-gating tests should not lose required LUT/config state or hang while polling memory-power/status fields.

### subset-b-001686: lines 15502-18022

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 15502-18022

## Purpose

This chunk is the tail of the generated AMDGPU DCN 3.0 register offset header. It contains no executable logic; its public interface is preprocessor constants mapping symbolic display/audio hardware register names to register offsets plus companion `*_BASE_IDX` constants used by AMD display register-table macros.

The path is under a local `ceph-client` source mirror, but this file is AMD display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

The range starts in the middle of the MPC RMU color pipeline register table, then covers DC performance monitor instances, AFMT/VPG/DME audio packet blocks, HPO clock control, six ABM blocks, Azalia controller and endpoint registers, legacy VGA indirect register offsets, Azalia stream descriptors, eight Azalia output endpoints, eight Azalia input endpoints, and the final `#endif` for the include guard.

Within lines 15502-18022 there are 2,286 `#define` entries: 1,677 register-address macros and 609 `*_BASE_IDX` macros.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime storage objects in this chunk. The important API surface is the generated macro namespace consumed by DCN 3.0 register descriptors:

- `mmMPC_RMU0_*`, `mmMPC_RMU1_*`, and `mmMPC_RMU2_*`: remaining multi-plane compositor RMU shaper and 3D LUT offsets. This includes shaper offsets/scales, LUT index/data/write masks, RAM A/B start/end/region controls, 3D LUT mode/index/data/read-write controls, output normalization, and output RGB offsets. The chunk begins in the middle of RMU0 shaper entries and later includes RMU1/RMU2 entries.
- `mmDC_PERFMON28_*` and `mmDC_PERFMON29_*`: DC performance counter control, state, count value, high/low counter, and interrupt/misc offsets.
- `mmAFMT6_*`, `mmVPG6_*`, and `mmDME6_*`: display audio packet formatter, video packet generator, and DME offsets for instance 6. These cover audio info packets, IEC 60958 channel-status data, CRC controls/results, ramp controls, generic packet access/data/status, ISRC/MPEG info, and memory power controls.
- `mmHPO_TOP_CLOCK_CONTROL`: high-performance output top clock-control offset. This is referenced by DCN hardware sequencing code for HDMI stream clock gating fields through the matching mask header.
- `mmABM0_*` through `mmABM5_*`: adaptive backlight management register offsets for six instances. Each instance maps PWM user/target/current/final/minimum duty state, ABM control, update sample rate, group lock, ACE slope/threshold controls, histogram/luma statistics controls/results, sample rates, histogram bin shift indexes, 24 histogram result registers, and backlight master lock.
- `mmAZALIA_*`, `mmAUDIO_*`, `mmCORB_*`, `mmRIRB_*`, `mmIMMEDIATE_COMMAND_*`, `mmWALL_CLOCK_*`, `mmDMA_*`, and `mmRESPONSE_*`: Azalia/HDA controller register offsets for global capabilities, stream position, input/output payload capability, wake, state change, GCTL, CORB/RIRB, immediate commands, wall clock, SSYNC, DMA position lower-base, interrupt control/status, and response interrupt count.
- `mmAZF0ENDPOINT_*` and `mmAZF0INPUTENDPOINT_*`: top-level Azalia endpoint and input endpoint index/data offsets used to access codec endpoint-indirect register spaces.
- `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*`: legacy VGA sequencer, CRT controller, graphics-controller, and attribute-controller indirect offsets.
- `ixAZENDPOINT_*`, `ixAZINPUTENDPOINT_*`, `ixAZROOT_*`, `ixAZF0STREAM*_*`, `ixAZF0ENDPOINT*_*`, and `ixAZF0INPUTENDPOINT*_*`: Azalia codec/function/stream/endpoint/input-endpoint indirect offsets. These cover codec function parameters, stream descriptor controls, endpoint converter and pin widgets, ELD/sink info, audio descriptors, multichannel control, HBR capability, channel allocation, hotplug/audio-enable control, unsolicited responses, configuration defaults, LPIB snapshots, input activity, and infoframe state.

Names prefixed with `mm` are normal memory-mapped register offsets. Names prefixed with `ix` are indirect register indexes used through an index/data register pair. The companion `*_BASE_IDX` value selects a generated register base via the display driver's `BASE(...)` macro before the offset is added.

## Control Flow

This header chunk has no local control flow. It is declarative register layout data used by code that constructs tables and then performs MMIO or indirect register accesses.

Runtime use follows this broad pattern:

1. DCN 3.0 display code includes `dcn_3_0_0_offset.h` with `dcn_3_0_0_sh_mask.h`.
2. Resource files expand macros such as `SR(...)`, `SRI(...)`, `SRII(...)`, and `SRII_MPC_RMU(...)` into absolute register offsets by adding `BASE(mm..._BASE_IDX)` to the generated `mm...` offset.
3. Subsystems pass those register tables to typed display objects such as MPC, AFMT, audio, IRQ, GPIO, clock-manager, and DMUB helpers.
4. Runtime helpers use `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET_FIELD`, `AZ_REG_READ`, and `AZ_REG_WRITE` against those tables and the matching shift/mask metadata.

For indirect Azalia and VGA entries, this file only defines the index values. The actual sequence is performed by consumers: write the desired `ix...` index to the endpoint/index register, then read or write the paired data register.

The macros do not encode sequencing rules. Clock enablement, power gating, register locking, double-buffer latching, interrupt acknowledgement, and index/data access ordering are enforced by the consuming driver code and the hardware specification, not by this generated header.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. It describes hardware-visible state held in DCN 3.0 display and audio registers.

The represented hardware state includes:

- MPC/RMU color state: shaper LUT programming, RAM A/B piecewise-linear region definitions, 3D LUT mode/index/data, 30-bit 3D LUT access, output normalization, output RGB offsets, and RMU memory/pipeline state accessed through adjacent register tables.
- Performance-monitor state: perf counter selection/control, active counter state, current counter values, high/low readback words, and interrupt/misc status for `DC_PERFMON28` and `DC_PERFMON29`.
- Audio packet state: AFMT audio info, IEC 60958 channel-status words, packet controls, CRC generation/checking, ramp controls, source control, status/interrupt state, and AFMT/VPG/DME memory power state.
- ABM/backlight state: ambient/user/target/current/final duty levels, minimum duty cycle, ABM enable/control state, sample rates, group locks, ACE tone-mapping coefficients/thresholds, histogram/luma-statistic accumulators, histogram result bins, and backlight master locks.
- HDA/Azalia controller state: CORB/RIRB command rings, immediate command/response registers, wall clock, stream synchronization, DMA position buffer base, interrupt controls/status, global controller state, stream position, and payload capability.
- Azalia endpoint state: converter formats, stream/channel IDs, digital converter controls, pin capabilities, hotplug/audio-enable state, ELD and sink info, audio descriptors, channel allocation, HBR and multichannel settings, unsolicited responses, configuration defaults, LPIB snapshots, input activity, and infoframe data.
- Legacy VGA indirect state: indexed sequencer, CRT controller, graphics-controller, and attribute-controller registers retained for compatibility paths.

Persistence is entirely hardware-dependent. Some registers are stable configuration until modeset, suspend/resume, power-gating transition, audio reconfiguration, or ASIC reset. Others are counters, snapshots, status bits, sticky interrupts, command ring pointers, write-one-to-clear acknowledgements, or index/data windows with side effects. Names containing `STATUS`, `INTERRUPT`, `ACK`, `RIRB`, `CORB`, `IMMEDIATE_COMMAND`, `LPIB`, `CRC`, `RESULT`, `READ_PROGRESS`, `CLOCK`, `MEM_PWR`, and `LOCK` should be treated as side-effect-sensitive unless the consumer path proves otherwise.

## Dependencies And Integration Points

The required companion for this offset header is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h`

Direct include points for the DCN 3.0 offset/mask pair in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Notable consumers and integration paths:

- `dcn30_resource.c` and related DCN 3.0/3.02 resource files use `SR`, `SRI`, `SRII`, and `SRII_MPC_RMU` macros to build typed register tables from this header's `mm...` and `*_BASE_IDX` definitions.
- `display/dc/mpc/dcn30/dcn30_mpc.h` declares the MPC/RMU register and field list shapes used to program shaper LUTs and 3D LUTs. DCN 3.x resource files instantiate RMU register lists for RMU instances using this offset header.
- `display/dc/dce/dce_audio.c` uses audio and Azalia abstractions such as `AZ_REG_READ` and `AZ_REG_WRITE` for endpoint/pin-indirect accesses. It depends on endpoint index/data offsets plus the indirect `ixAZ...` register numbers represented in this chunk.
- `display/dc/hwss/dce/dce_hwseq.h` includes hardware sequencer register fields for `AZALIA_AUDIO_DTO`, `AZALIA_CONTROLLER_CLOCK_GATING`, and `HPO_TOP_CLOCK_CONTROL`; this chunk contains the HPO top clock-control offset used with the matching field masks.
- IRQ, GPIO, clock-manager, and DMUB files include the same generated pair so interrupt source setup, pin translation, clock programming, and firmware-mediated display control use one register contract for the ASIC generation.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong offset or base index can compile cleanly while redirecting reads/writes to the wrong register, producing blank displays, incorrect color transforms, audio loss, bad hotplug behavior, broken backlight control, interrupt storms, or register access hangs.
- The chunk starts mid-table for MPC RMU0. Complete RMU coverage requires adjacent chunks; this chunk alone should not be treated as the full RMU register map.
- Repeated instance blocks create copy/paste drift risk. `MPC_RMU0/1/2`, `ABM0` through `ABM5`, `AZF0STREAM0` through `AZF0STREAM15`, `AZF0ENDPOINT0` through `AZF0ENDPOINT7`, and `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` are highly regular. A single instance-specific offset error may only fail on one pipe, one link, or one audio endpoint.
- `mm` and `ix` namespaces are not interchangeable. Treating an indirect codec index as an MMIO offset, or skipping the endpoint index/data access sequence, can read or write unrelated hardware state.
- `*_BASE_IDX` is part of the address calculation. Using an offset without its base, or using the wrong base index, is especially risky in this chunk because it spans MPC, OPP/ABM, HPO, HDA, AFMT/VPG/DME, and indirect spaces.
- Audio command rings and stream pointers are side-effect-sensitive. CORB/RIRB, immediate command, stream descriptor, DMA position, LPIB, and unsolicited response registers require ordering and acknowledgement discipline outside this header.
- ABM and backlight registers affect visible panel brightness and content-adaptive processing. Bad offsets can cause flicker, incorrect brightness, stuck ABM locks, invalid histogram/luma reads, or user brightness controls that appear to work only on some instances.
- RMU shaper and 3D LUT registers affect color pipeline programming. Errors can produce subtle color inaccuracies, failed LUT loads, stale RAM bank reads, or corruption limited to particular planes or RMU instances.
- HPO and audio clock-control offsets are tied to power management. Accessing clock-gated or memory-powered-down blocks at the wrong time can return stale data or drop writes.
- Legacy VGA indirect offsets are compatibility state. Even though modern display paths rarely depend on them, accidental changes can regress boot console, VGA fallback, or low-level diagnostic paths.

## Test Signals

Useful validation is a mix of compile-time checks and hardware behavior:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.02 support. Missing or renamed macros should fail at resource, IRQ, GPIO, clock-manager, DMUB, MPC, audio, and hardware-sequencer table initializers.
- Diff this generated range against AMD's source register database and adjacent DCN generation headers to catch instance drift across RMU, ABM, AFMT/VPG/DME, stream, endpoint, and input-endpoint blocks.
- Exercise hardware with enough active displays and audio endpoints to use AFMT/VPG/DME instance 6, multiple ABM instances, and multiple Azalia endpoints. Validate modeset, hotplug, DPMS, suspend/resume, and audio route changes.
- Run color-management tests that program shaper LUTs and 3D LUTs through MPC/RMU, including 30-bit LUT paths, bank switching, readback where supported, and multi-plane or multi-pipe configurations.
- Validate ABM and backlight behavior: user brightness changes, content-adaptive brightness transitions, histogram/luma-statistic reads, lock/unlock behavior, and resume from low-power states.
- Test HDMI/DP audio: stream format changes, channel allocation, HBR formats, multichannel layout, ELD/sink info updates, hotplug audio enable/disable, unsolicited response handling, and LPIB snapshot/readback.
- Stress HDA controller command paths: CORB/RIRB traffic, immediate command responses, interrupt status/ack handling, stream reset/run transitions, and DMA position buffer updates.
- Use perfmon/debug tooling to configure `DC_PERFMON28` and `DC_PERFMON29`, start and stop counters, read high/low values, and verify interrupt/status behavior.
- Monitor kernel logs and display diagnostics for register access failures, audio timeouts, underflow/flicker, unexpected hotplug events, IRQ storms, backlight regressions, color LUT mismatches, and resume failures.

## Cross-Chunk Notes

Lines before 15502 define the earlier part of the MPC RMU0/RMU2 register tables and other DCN 3.0 offset namespaces. This chunk begins at `mmMPC_RMU0_SHAPER_RAMA_REGION_4_5_BASE_IDX`, so the RMU0 shaper list is incomplete at the top boundary. The chunk ends with the file's include-guard `#endif`, so there is no later source chunk for this header after line 18022.
