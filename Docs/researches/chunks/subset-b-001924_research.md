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
