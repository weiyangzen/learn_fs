# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h lines 2628-5157

## Purpose

This chunk is generated AMD DCN 3.2.1 register-offset metadata. It contains no executable C logic; it exports symbolic preprocessor constants that map display-controller register names to MMIO offsets plus companion base-index selectors. Runtime code combines each `reg...` offset with its matching `reg..._BASE_IDX` through `BASE(...)`/`SRI(...)`/`SRII(...)` style macros before issuing register reads and writes.

The requested range is a middle slice of `dcn_3_2_1_offset.h`. It starts at the tail of cursor instance 1 display metadata registers, covers complete HUBP/HUBPREQ/HUBPRET/cursor blocks for pipe instances 2 and 3, covers DPP/CNVC/DSCL/CM/DPP_TOP blocks for DPP instances 0 through 3, covers MPC/MPCC blend blocks for MPCC instances 0 through 3, and ends after the complete `MPCC_OGAM0` output-gamma block. The next chunk begins at `MPCC_OGAM1`, so this range owns only the first output-gamma MPCC block.

The slice has 2,392 `#define` lines: 1,196 register-offset macros and 1,196 matching `_BASE_IDX` macros. Most entries use base index `2` for DCN display pipe blocks; MPC/MPCC/OGAM entries use base index `3`. Although this tree is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata and has no Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or callbacks in this range. The public surface is the generated macro namespace:

- `reg<block>_<register>`: numeric DCN 3.2.1 MMIO register offset.
- `reg<block>_<register>_BASE_IDX`: base-address segment selector used with the SOC/DCN register-base table.

Major macro families in this chunk:

- Tail of `CURSOR0_1`: display metadata data-mover control, QoS, status, software control, and data registers.
- `HUBP2` and `HUBP3`: surface configuration, address/tiling config, primary and secondary viewport coordinates for luma/chroma planes, request sizing, HUBP clock control, VMPG/MALL controls, MALL status, debug, and clock-measurement windows.
- `HUBPREQ2` and `HUBPREQ3`: surface pitch, VMID, primary/secondary surface and metadata addresses, flip control, in-use and earliest-in-use tracking, TTU/QoS/prefetch parameters, VM aperture/TLB control, blank/destination/vblank/flip/nominal timing parameters, cursor settings, p-state forcing, memory power, and status registers.
- `HUBPRET2` and `HUBPRET3`: HUBP return/read-line controls, memory-power controls/status, interrupts, read-line value/status, and earliest-in-use status.
- `CURSOR0_2` and `CURSOR0_3`: cursor surface addresses, size/control/position/hotspot/destination offsets, chunking, settings, DMDATA VM control, cursor DMDATA surface addresses, control/QoS/status/software data, and cursor cache controls.
- `CNVC_CFG0` through `CNVC_CFG3` and `CNVC_CUR0` through `CNVC_CUR3`: input pixel-format conversion, color-key alpha controls, cursor control/color, cursor LUT access/data, and cursor 2-bit control.
- `DSCL0` through `DSCL3`: scaler tap controls, recout/start/size/viewport setup for luma and chroma, ratio/initial-phase/filter controls, coefficient RAM access/data, manual replication, memory power, and debug registers.
- `CM0` through `CM3`: DPP color-management surface coefficients, bias/scale, pre-CSC and post-CSC coefficient banks, gamut remap, gamma-correction control/LUT/RAM A/B region programming, HDR multiplier, shaper LUT, 3D LUT, memory power, and alpha controls.
- `DPP_TOP0` through `DPP_TOP3`: DPP top control, clock control, CRC control/results, ordering/OBUF controls, boundary color, debug controls, memory power, and double-buffer control.
- `MPCC0` through `MPCC3`: MPCC blend mode, alpha controls, background color, output pipe selection, top/bottom muxing, status, DWB muxing, and debug registers.
- `MPC` shared block: output muxing, clock control, CRC, cursor gating, global flow controls, memory-power controls, debug/status, output CWB muxing, DWB mux, and vupdate lock set/clear/status registers.
- `MPCC_OGAM0`: output gamma control, LUT index/data/control, RAM A/B start/end/slope/base/offset/region registers, and gamut-remap coefficient controls for MPCC output-gamma instance 0.

## Control Flow

This header has no runtime control flow. It participates in a compile-time register-table construction pattern:

1. `dcn321_resource.c` includes `dcn_3_2_1_offset.h` and the matching `dcn_3_2_1_sh_mask.h`.
2. Resource macros such as `SR`, `SRI`, `SRI_ARR`, `SRII`, and `VUPDATE_SRII` paste block and instance IDs into names such as `regHUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS`, `regCM3_CM_GAMCOR_LUT_DATA`, or `regMPCC_OGAM0_MPCC_OGAM_CONTROL`.
3. The macros compute an address as `ctx->dcn_reg_offsets[reg..._BASE_IDX] + reg...` and populate typed register tables for HUBP, DPP, MPC, MPCC, timing/hardware sequencing, and related DC blocks.
4. Runtime objects such as `hubp32_construct`, `dpp32_construct`, and `dcn32_mpc_construct` receive those tables. Later display code uses normal DC register helpers to program surface fetch, cursor, scaling, color, blending, gamma, CRC, power, and debug behavior.

The offsets do not encode the required sequencing. Consumers must still order modeset operations correctly: power/clock enablement, plane address flips, VM aperture setup, cursor updates, prefetch/watermark programming, scaler and color pipeline setup, MPCC tree updates, gamma LUT bank updates, vupdate locking, and suspend/resume restoration.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in files. It names MMIO-backed GPU state. The represented hardware state includes:

- Per-pipe HUBP fetch state: surface addresses, metadata addresses, pitch, tiling, viewports, flip state, VMID/aperture/TLB state, request sizing, MALL/VMPG behavior, prefetch/TTU/QoS timing, p-state forcing, memory power, and status/debug counters.
- Cursor state for pipes 1 through 3: cursor addresses, dimensions, position/hotspot, chunking, color/LUT controls, DMDATA fetch/control/QoS/status, cache controls, and software DMDATA access.
- DPP input, scaling, and color state: pixel-format conversion, color keying, scaler ratios/phases/filter coefficients, viewport/recout geometry, color-space conversion matrices, gamma-correction LUTs, HDR/shaper/3D LUT controls, alpha controls, and DPP CRC/debug/memory-power state.
- MPC/MPCC composition state: blend topology, alpha/background configuration, OPP selection, MPCC busy/idle status, DWB/CWB muxes, CRC capture, shared MPC memory power, and vupdate lock state.
- Output-gamma state for `MPCC_OGAM0`: LUT index/data windows, RAM A/B piecewise-linear regions, offsets, gamut remap coefficients, and bank/control selection.

Persistence is hardware-defined. Configuration registers generally retain values until the driver reprograms a mode, flips a plane, changes a color pipeline, gates power, suspends/resumes, or resets the ASIC. Status, interrupt, debug, counter, lock, and memory-power registers may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. This offset header does not describe those semantics; field masks and behavior live in the companion mask header and the consuming DC code.

## Dependencies And Integration Points

The chunk must remain synchronized with AMD's generated DCN 3.2.1 register database and with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h` for field shifts and masks.
- The DCN/SOC register-base tables exposed through `ctx->dcn_reg_offsets[...]`.
- DC resource and block headers that define register-list macros for HUBP, DPP, MPC/MPCC, color, cursor, DSC/timing, and hardware sequencing.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which uses the generated macros while creating the DCN 3.2.1 resource pool. In that file, disabled pipes are skipped based on pipe fuses, but the hardware instance ID is still passed into `dcn321_hubp_create`, `dcn321_dpp_create`, OPP/timing creation, and MPC creation. That makes instance-specific correctness important: pipe 2 and pipe 3 offsets from this chunk can be used even when lower-index pipes are fused off or when resource arrays are compacted around available hardware.

The important runtime integration points are the register tables passed to:

- HUBP construction for surface fetch, flip, cursor, VM, MALL, and prefetch programming.
- DPP construction for CNVC, cursor, DSCL, CM, DPP_TOP, CRC, and memory-power programming.
- MPC construction for MPCC blending, output muxing, CRC, DWB/CWB muxing, vupdate locks, and output gamma.
- Hardware sequencing and diagnostics paths that read status/debug/CRC/lock registers during modesets, validation, and debugging.

## Risks And Edge Cases

- Offset or base-index drift is the main risk. These macros are untyped constants; a wrong value can compile cleanly while targeting the wrong MMIO register or base segment.
- The base-index split matters. HUBP/HUBPREQ/HUBPRET/CURSOR/DPP macros in this range use base index `2`, while MPC/MPCC/OGAM macros use base index `3`. Mixing those segments would redirect otherwise plausible offsets into the wrong hardware aperture.
- Repeated pipe families are copy-sensitive. `HUBP2`/`HUBP3`, `HUBPREQ2`/`HUBPREQ3`, `CURSOR0_2`/`CURSOR0_3`, `CNVC`/`DSCL`/`CM`/`DPP_TOP` instances 0 through 3, and `MPCC0` through `MPCC3` are structurally similar but must remain instance-accurate.
- The range boundaries are artificial. The first lines are only the tail of `CURSOR0_1`, and the next chunk begins with `MPCC_OGAM1`; adjacent chunk reports are needed before making whole-file claims.
- Surface-address, VM, metadata, and flip registers are high impact. Bad offsets can produce page faults, stale scanout, corrupted compressed metadata, wrong plane content, or failures only during flips, multi-plane composition, or suspend/resume.
- Timing and prefetch registers are sensitive to bandwidth and power states. Errors in TTU, vblank/flip/nominal parameters, MALL, memory power, or p-state forcing can appear as intermittent underflow, flicker, blanking, or clock/power-management regressions.
- Color-pipeline and gamma registers are visually subtle. Wrong CM/DSCL/OGAM offsets can cause color-space conversion errors, bad HDR tone mapping, broken LUT programming, banding, or instance-local color regressions that basic modeset tests may miss.
- MPC/MPCC topology and vupdate locks affect atomic updates. Incorrect blend mux, status, OPP, DWB/CWB, or lock registers can break plane stacking, writeback, cursor composition, CRC validation, or atomic update synchronization.

## Test Signals

Useful validation combines generated-header consistency with display behavior:

- Build AMDGPU/DC with DCN 3.2.1 support enabled; missing or renamed macros should fail in `dcn321_resource.c` or block register-list expansion.
- Mechanically verify that every non-`_BASE_IDX` `reg...` macro in lines 2628-5157 has exactly one matching `_BASE_IDX` macro. This range should contain 1,196 offset macros and 1,196 base-index macros.
- Verify base-index distribution: 1,015 `_BASE_IDX` entries with value `2` and 181 with value `3` in this range.
- Diff these offsets against AMD's authoritative DCN 3.2.1 register source and nearby generated headers such as `dcn_3_2_0_offset.h` and `dcn_3_6_0_offset.h` where block layout is expected to match.
- Exercise modesets and page flips using at least four pipes where hardware allows, with special attention to pipes 2 and 3 because their HUBP/HUBPREQ/HUBPRET/cursor blocks are fully covered here.
- Validate cursor movement, cursor format/color/LUT behavior, cursor DMDATA, and cursor cache paths on multiple pipes.
- Test scaler and viewport paths: luma/chroma viewport changes, scaling ratios, filter coefficient updates, recout changes, rotation/format combinations, and multi-plane updates.
- Validate color-management paths: pre-CSC/post-CSC matrices, gamut remap, gamma correction, HDR multiplier, shaper LUT, 3D LUT, alpha controls, and output gamma on MPCC 0.
- Exercise composition and synchronization: multi-plane alpha blending, MPCC tree changes, OPP remapping, vupdate lock set/clear, DWB/CWB muxing, CRC capture, and atomic updates under load.
- Watch kernel logs and display diagnostics for page faults, underflow, flip timeouts, vupdate lock stalls, pipe-specific blanking, color regressions, CRC mismatches, memory-power status failures, and resume failures.

## Cross-Chunk Notes

Earlier chunks own the beginning of `CURSOR0_1` and prior HUBP/DPP/MPC register blocks. Later chunks continue with `MPCC_OGAM1` and the remaining DCN 3.2.1 register-offset namespace. The final per-file research document should merge adjacent chunks before claiming complete coverage of all HUBP instances, all DPP/CM/DSCL instances, all MPCC output-gamma instances, or the complete `dcn_3_2_1_offset.h` hardware map.
