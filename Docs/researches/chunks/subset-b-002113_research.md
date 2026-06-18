# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h lines 2653-5191

## Purpose

This chunk is generated AMD DCN 3.6 register-offset metadata. It contains no executable driver logic; it exports `#define reg...` constants for MMIO register offsets plus matching `..._BASE_IDX` constants for the AMD display register helper layer. Consumers include this file with `dcn_3_6_0_sh_mask.h` so register tables can combine offsets, shifts, and masks for DCN 3.6 hardware blocks.

The requested range starts near the end of HUBP instance 1 and then covers HUBPREQ/HUBPRET/cursor/perfmon blocks for HUBP instances 1 through 3, followed by DPP instances 0 through 3. The DPP coverage includes CNVC format conversion, CNVC cursor color programming, DSCL scaler registers, CM color-management/gamma-correction registers, DPP top control/CRC registers, and DPP perfmon blocks. Although the path is under a local `ceph-client` mirror, this is AMDGPU display hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, callbacks, or direct I/O operations in this chunk. The interface is the generated macro namespace:

- `regBLOCK_INSTANCE_REGISTER`: register offset used by AMD display `REG_*`, `SRI`, `SRII`, and related token-pasting macros.
- `regBLOCK_INSTANCE_REGISTER_BASE_IDX`: base-address segment selector, `2` throughout this chunk.

This range has 2,387 `#define reg...` macros: 1,193 register-offset macros and 1,194 base-index macros. The one-count difference comes from the chunk starting in the middle of the preceding HUBP1 block, where the matching non-base macro for `regHUBP1_HUBP_MEASURE_WIN_CTRL_DCFCLK_BASE_IDX` is outside this range.

Major macro families:

- `HUBP1`, `HUBP2`, `HUBP3`: per-pipe HUBP surface configuration, tiling/address configuration, primary/secondary viewport dimensions, request sizing, clock control, virtual-memory page configuration, MALL configuration/status, and HUBPREQ debug/measurement windows. This chunk has only the tail of HUBP1 but complete HUBP2 and HUBP3 sections.
- `HUBPREQ1`, `HUBPREQ2`, `HUBPREQ3`: per-pipe request-side surface fetch controls. These include luma/chroma surface pitch, VMID settings, primary/secondary surface and metadata addresses, flip control, surface-in-use and earliest-in-use registers, TTU/QoS controls, VM aperture and L1 TLB controls, vblank/flip/nominal prefetch parameters, per-line delivery, cursor request settings, UCLK p-state force, memory power controls, and status registers.
- `HUBPRET1`, `HUBPRET2`, `HUBPRET3`: return/read-line controls, memory power controls/status, read-line interrupt/status/value registers.
- `CURSOR0_1`, `CURSOR0_2`, `CURSOR0_3`: per-pipe cursor control, address high/low, size, position, hot spot, stereo control, destination offset, cursor memory power, and DMDATA address/control/QoS/status/software data registers.
- `DC_PERFMON8`, `DC_PERFMON9`, `DC_PERFMON10`: HUBP perfmon blocks for the three HUBP instances represented here. Each exposes counter control, counter state, perfmon control, current-value interrupt/misc, and high/low counter value registers.
- `CNVC_CFG0` through `CNVC_CFG3`: DPP format/conversion configuration, surface pixel format, FP bias/scale, color keyer, alpha LUT, pre-dealpha, pre-CSC matrices for A/B paths, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0` through `CNVC_CUR3`: DPP-side cursor color/control and FP scale/bias registers.
- `DSCL0` through `DSCL3`: scaler coefficient RAM, scaler mode/tap controls, horizontal/vertical ratios and initial phases for luma/chroma, black color, DSCL update/autocal, overscan, OTG blanking, recout/MPC size, line-buffer format and memory control/status, and output-buffer controls.
- `CM0` through `CM3`: DPP color-management controls. Each instance maps post-CSC matrices, gamut remap A/B matrices, gamma-correction LUT index/data/control, RAMA/RAMB start/slope/base/end/offset/region registers for B/G/R channels, HDR multiplier coefficient, memory power control/status, dealpha, coefficient format, test-debug windows, and DPP CRC values.
- `DPP_TOP0` through `DPP_TOP3`: DPP control, soft reset, CRC control, and host-read control.
- `DC_PERFMON11` through `DC_PERFMON14`: DPP perfmon blocks. The chunk ends after `DC_PERFMON14_PERFMON_CVALUE_LOW`; later `DC_PERFMON14` high/low value registers are outside this range.

Address-block anchors in this chunk show repeated hardware instance layout. HUBP instance bases are `0x370`, `0x6e0`, and `0xa50` for instances 1-3. DPP instance bases are `0x0`, `0x5ac`, `0xb58`, and `0x1104` for instances 0-3. Perfmon blocks use separate base comments such as `0x1de4`, `0x2154`, `0x24c4`, `0x3890`, `0x3e3c`, `0x43e8`, and `0x4994`.

## Control Flow

This header has no runtime control flow. Runtime behavior is introduced by consumers that token-paste these generated names into register tables:

1. DCN 3.6 modules include `dcn_3_6_0_offset.h` with `dcn_3_6_0_sh_mask.h`.
2. `dcn36_resource.c` builds resource register arrays. In the visible integration path, `hubp_regs_init(id)` expands `HUBP_REG_LIST_DCN30_RI(id)` into per-instance HUBP/HUBPREQ/HUBPRET/cursor offsets, while the resource constructor creates HUBP and DPP objects for each active pipe.
3. DPP creation uses shared DCN 3.5/3.x DPP code and register-list macros that bind CNVC, DSCL, CM, DPP top, and perfmon offsets to generic DPP helper functions.
4. Runtime modeset, plane update, cursor update, scaling, color-management, flip, and power-management paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and `REG_WAIT`. Those helpers use the offset constants from this file and field masks/shifts from the companion header.
5. `dmub_dcn36.c` also includes this header pair and computes DMUB-visible register offsets using `BASE(reg..._BASE_IDX) + reg...`. This chunk is not the primary DMUB register set, but the same generated base-index contract applies.
6. `irq_service_dcn36.c` includes the same header pair for interrupt register initialization. Plane-flip entries for pipes 1-3 and DC underflow/vblank/vline entries can indirectly depend on these per-pipe address patterns, although the specific interrupt status/ack registers mostly live outside this chunk.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in files or memory. It describes MMIO-backed display engine state.

Represented hardware state includes active surface and metadata addresses, viewport geometry, pitch and tiling configuration, VMID/aperture/TLB configuration, flip and surface-in-use state, TTU/QoS and prefetch timing, cursor image addresses and position, DMDATA request state, scaler coefficients and ratios, line-buffer/output-buffer settings, color-space conversion matrices, gamut remap matrices, gamma-correction LUT contents, DPP CRC capture values, perfmon counters, memory power control/status, and debug/test windows.

Persistence is hardware-defined. Most programmed configuration lasts until the next modeset, plane update, power-gating transition, suspend/resume restore, soft reset, or ASIC reset. Status, interrupt, perfmon, flip, surface-in-use, read-line, memory-power-status, and CRC-value registers may be read-only, sticky, edge-triggered, self-clearing, latched, or write-one-to-clear depending on the field definitions in the matching sh/mask header and hardware spec. Because this file is untyped offsets only, users must rely on block-specific helper code for correct ordering, polling, and access restrictions while clocks or memories are gated.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.6 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h` for bit shifts and masks for the same register names.
- AMD display register helper macros such as `REG`, `REG_*`, `SRI`, `SRI_ARR`, `SRII`, `BASE`, `FD_MASK`, and `FD_SHIFT`.
- The `dc_context` `dcn_reg_offsets` table used by `BASE(reg..._BASE_IDX)` when converting generated offsets into real MMIO addresses.

Representative integration points in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes this header and creates DCN 3.6 resource pools. Its `hubp_regs_init(id)` uses `HUBP_REG_LIST_DCN30_RI(id)`, and its constructor creates `dcn35_hubp_create(ctx, i)` and `dcn35_dpp_create(ctx, i)` for each pipe.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn30` and `dcn35` code consume the HUBP/HUBPREQ/HUBPRET/cursor register tables for surface programming, flips, VM setup, request scheduling, MALL behavior, cursor programming, and memory power control.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10` and `dcn32` code consumes DPP-side CNVC, DSCL, CM, LUT, CRC, and memory-power registers. For example, DSCL helper code programs scaler modes/ratios and waits on DSCL memory power status; DPP color-management code reads or writes CM and LUT registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_hw_sequencer.c` schedules DPP color-management programming and references DSCL state in update sequencing; the actual MMIO access routes through DPP register tables populated from generated headers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes this header and computes DMUB register offsets via `REG_OFFSET_EXP(reg)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes this header pair for DCN 3.6 interrupt source setup, including pflip/vblank/vline entries for four display pipes.

## Risks And Edge Cases

- Offset drift is the primary risk. These macros are untyped constants; a wrong offset or base index can compile cleanly while causing MMIO reads/writes to hit the wrong register.
- The chunk has artificial boundaries. It starts in the tail of `HUBP1` and ends before the final `DC_PERFMON14` value registers, so complete per-file conclusions require adjacent chunks.
- Instance repetition is copy-sensitive. HUBP/HUBPREQ/HUBPRET/cursor instances 1-3 and DPP instances 0-3 should preserve regular spacing. A single bad instance offset can create pipe-specific failures that only occur on one display pipe or one plane assignment.
- Surface address, metadata address, VMID, aperture, and TLB offsets are high impact. Errors can fetch from the wrong memory, break page translation, corrupt display output, trigger GPU faults, or expose stale frame contents.
- Flip and surface-in-use offsets are sequencing-sensitive. Bad offsets can cause page-flip interrupts, earliest-inuse tracking, or surface latching to malfunction, leading to flicker, stale frames, missed vblank-synchronized flips, or hangs in wait paths.
- Prefetch, TTU, QoS, UCLK p-state force, and per-line delivery offsets affect bandwidth scheduling. Mistakes may only appear under high-resolution, high-refresh, multi-plane, or memory-clock-transition workloads.
- Cursor and DMDATA offsets are pipe-specific. Bad cursor addresses or hot-spot/position offsets can show as missing cursors, wrong cursor colors, stereo cursor errors, or corrupted DMDATA transactions while normal primary planes still work.
- DSCL offsets are mode-sensitive. Incorrect scaler ratio, init, tap, line-buffer, or autocal offsets can break only scaled modes, chroma subsampling, 4:2:0 content, overscan, or viewport changes.
- CM and gamma LUT offsets can silently degrade color. A wrong post-CSC, gamut-remap, gamma RAM, HDR multiplier, dealpha, or coefficient-format offset may produce wrong color only for color-managed, HDR, or LUT-enabled paths.
- Memory-power control/status offsets are access-order sensitive. Wrong DSCL, CM, cursor, HUBPREQ, or HUBPRET memory power registers can leave memories powered unnecessarily, power them down while active, or make `REG_WAIT` loops time out.
- Perfmon and CRC offsets are diagnostic-sensitive. Incorrect perfmon/CRC registers may make validation or debug tools misleading even when ordinary display output appears usable.

## Test Signals

Useful validation signals are a mix of build-time and hardware behavior:

- Build AMDGPU/DC with DCN 3.6 enabled. Missing, renamed, or malformed offset macros should fail in `dcn36_resource.c`, `dmub_dcn36.c`, `irq_service_dcn36.c`, or shared HUBP/DPP register-list construction.
- Mechanically verify every non-base `reg...` macro in lines 2653-5191 has the expected `..._BASE_IDX` pair inside the same chunk or an adjacent chunk where the assignment boundary splits a pair.
- Diff this range against AMD's authoritative DCN 3.6 register database and nearby generated DCN headers, paying special attention to repeated instance spacing for HUBP1-3 and DPP0-3.
- Exercise multi-pipe modesets and plane assignment: single display, multi-monitor, plane promotion/demotion, overlay planes, cursor movement, page flips, VRR/fast updates, suspend/resume, display off/on, and runtime power management.
- Validate surface fetch paths with different tiling, formats, modifiers, primary/secondary planes, chroma planes, metadata/DCC surfaces, and VMID configurations. Watch for page faults, underflows, stale frames, and pipe-specific failures.
- Exercise scaler paths with unscaled, upscaled, downscaled, 4:2:0/chroma, overscan, viewport crop, and high-refresh modes. DSCL mistakes often show as only scaled-output artifacts.
- Exercise color-management paths with degamma/regamma LUTs, post-CSC, gamut remap, HDR multiplier, dealpha, and CRC capture. Compare register dumps and visual/CRC output to expected programming.
- Check memory-power and low-power transitions by cycling display idle, MALL/sub-viewport scenarios, runtime PM, and suspend/resume while watching for `REG_WAIT` timeouts, hangs, unexpected power draw, or failure to restore display.
- Use DC perfmon and DPP CRC register dumps for `DC_PERFMON8-14`, `DPP_CRC_VAL_*`, HUBPREQ status, and DSCL/CM memory status to confirm diagnostic registers map to the intended hardware pipe.

## Cross-Chunk Notes

Earlier chunks own HUBP0 and the beginning of HUBP1, including the `HUBP1_HUBP_MEASURE_WIN_CTRL_DCFCLK` non-base macro whose base-index macro appears at the start of this range. Later chunks continue after `DC_PERFMON14_PERFMON_CVALUE_LOW` and are needed for the rest of DPP3 perfmon and subsequent DCN 3.6 address blocks. The final per-file research document should merge adjacent chunks before making complete claims about all DCN 3.6 HUBP, DPP, perfmon, IRQ, or DMUB register coverage.
