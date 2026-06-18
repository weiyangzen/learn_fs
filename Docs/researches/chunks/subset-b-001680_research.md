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
