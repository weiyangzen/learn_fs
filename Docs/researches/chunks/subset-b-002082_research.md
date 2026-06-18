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
