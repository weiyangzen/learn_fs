# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 2690-5205

## Purpose

This chunk is generated AMD DCN 3.1.6 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map display-engine register names to MMIO offsets and to the DCN base-segment index used by AMDGPU register helper macros.

Although this file is inside a local `ceph-client` source mirror, the content is AMDGPU display-driver hardware metadata and has no Ceph or distributed filesystem behavior.

The requested range starts at a chunk boundary inside the tail of the DCN VM register block, then covers DC perfmon instance 6, four HUBP/HUBPREQ/HUBPRET/CURSOR pipelines, DC perfmon instances 7-10, and the first two DPP pipelines. The DPP coverage includes converter/configuration (`CNVC_CFG`), converter cursor (`CNVC_CUR`), scaler (`DSCL`), color management (`CM`), DPP top-level, and DPP perfmon instance 11 for DPP0. The chunk ends inside the `CM1_CM_SHAPER_RAMB_REGION_*` sequence, so later CM1 shaper registers continue in the next chunk.

This slice contains 2,392 `#define` lines: 1,196 register-offset macros and 1,196 matching `_BASE_IDX` macros. Every complete register offset in the slice has a companion base-index macro; the first line is only the `_BASE_IDX` for `regDCN_VM_CONTEXT15_PAGE_TABLE_START_ADDR_LO32`, whose offset macro belongs to the previous chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, locks, or direct allocation/persistence APIs in this line range. The public interface is the generated macro convention:

- `reg<REGISTER_NAME>`: register offset within the selected DCN address segment.
- `reg<REGISTER_NAME>_BASE_IDX`: index into the ASIC-specific `DCN_BASE__INST0_SEG*` table.

Important macro families in this chunk:

- DCN VM boundary tail: `regDCN_VM_CONTEXT15_PAGE_TABLE_END_ADDR_*`, `regDCN_VM_DEFAULT_ADDR_*`, `regDCN_VM_FAULT_CNTL`, `regDCN_VM_FAULT_STATUS`, and fault address registers.
- DC perfmon instances: `DC_PERFMON6` through `DC_PERFMON11` counter control, state, run/interrupt control, current-value, high, and low counter registers. Instances 7-10 are attached to HUBP blocks 0-3; instance 11 is attached to DPP0 in this slice.
- HUBP instances 0-3: `HUBP*_DCSURF_SURFACE_CONFIG`, address/tiling config, primary and secondary viewport registers for luma and chroma, request-size config, HUBP control, clock control, VM page config, debug registers, and DCFCLK/DPPCLK measurement windows.
- HUBPREQ instances 0-3: surface pitch, VMID, primary/secondary luma and chroma surface addresses, metadata surface addresses, surface control, flip control and interrupt, in-use/earliest-in-use address readbacks, expansion mode, TTU/QoS controls, DMDATA VM control, system aperture and L1 TLB registers, blank/destination/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor settings, ref-to-pixel frequency conversion, and HUBPREQ memory power control/status.
- HUBPRET instances 0-3: return-path control, memory power control/status, read-line controls, interrupt, read-line value, and read-line status.
- Cursor instances 0-3: cursor control, surface address low/high, size, position, hot spot, stereo control, destination offset, cursor memory power control/status, DMDATA address/control/QoS/status, and software data/control registers.
- DPP0 and DPP1 converter/configuration: `CNVC_CFG*_CNVC_SURFACE_PIXEL_FORMAT`, format control, floating-point bias/scale, color keyer control and color values, alpha LUT, pre-dealpha, pre-CSC mode and matrix coefficients, coefficient format, pre-degamma, and pre-realpha.
- DPP0 and DPP1 converter cursor: `CNVC_CUR*_CURSOR0_CONTROL`, cursor colors, and cursor floating-point scale/bias.
- DPP0 and DPP1 scaler: coefficient RAM selection/data, scaler mode, tap control, DSCL control, 2-tap/manual replicate controls, horizontal/vertical scale ratio and init registers for luma/chroma, black color, update/autocal, overscan, OTG blanking, recout/MPC size, line-buffer data format/memory control, vertical counter, DSCL memory power, and output-buffer memory power.
- DPP0 and DPP1 color management: control, post-CSC matrices, gamut remap matrices, bias, gamma correction LUT controls, RAM A/B start/slope/base/end/offset/region registers, blender gamma LUT controls and regions, HDR multiplier, CM memory power, dealpha, coefficient format, shaper control, shaper offset/scale/LUT/index/write-enable, and shaper RAM A/B region definitions.
- DPP0 top-level: `DPP_TOP0_DPP_CONTROL`, soft reset, CRC values/control, and host read control.

## Control Flow

This header has no runtime control flow. Runtime sequencing comes from AMDGPU display code that includes this generated offset header and its companion shift/mask header.

Typical flow:

1. DCN316 resource and DMUB code include `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`.
2. `dcn316_resource.c` defines `DCN_BASE__INST0_SEG*`, then expands register-list macros such as `DPP_REG_LIST_DCN30(id)` and `HUBP_REG_LIST_DCN30(id)` into per-instance register tables.
3. Helper macros such as `SR`, `SRI`, and related variants combine `BASE(reg..._BASE_IDX)` with `reg...` offsets to produce absolute register addresses for AMDGPU DC objects.
4. Runtime code uses those populated tables through register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` while programming planes, flips, cursors, scaler state, color transforms, LUTs, memory power, perfmon counters, and fault/status paths.

The offset constants encode only addresses. They do not encode write ordering, double-buffering rules, read-only/write-one-to-clear semantics, or timing constraints. Those remain in the DC/HUBP/DPP implementation and hardware documentation.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It names MMIO-backed hardware state in the display controller:

- VM state: DCN VM context 15 end address, default fault target, fault control/status, and fault address registers.
- Plane surface state: HUBP/HUBPREQ surface pixel format, tiling/address config, pitches, luma/chroma primary and secondary surface addresses, metadata addresses, TMZ/DCC controls, flip controls, pending/in-use readbacks, viewport coordinates and dimensions, and cursor destination integration.
- Memory request and timing state: prefetch, vblank, flip, nominal delivery, TTU/QoS, destination-after-scaler, blank offsets, ref-to-pixel conversion, DMDATA VM handling, system aperture, and L1 TLB controls.
- Cursor state: cursor enable/mode, cursor surface address, size, position, hot spot, stereo behavior, memory power, DMDATA request state, and software data path.
- HUBPRET state: read-line tracking, return-path control, memory power, and interrupt/status registers.
- DPP conversion/scaling state: pixel format conversion, floating-point bias/scale, alpha/color keying, pre-CSC, pre-degamma/re-alpha, scaler coefficients, tap/ratio/init values, recout/MPC geometry, line-buffer format, and output-buffer/DSCL memory power.
- Color pipeline state: post-CSC, gamut remap, gamma-correction LUTs, blender gamma LUTs, shaper LUTs, HDR multiplier, dealpha, 3D LUT setup for DPP0, and CM memory power/status. The DPP1 CM shaper block is incomplete at this chunk boundary.
- Diagnostic state: DC perfmon controls/counters and DPP/HUBP debug/CRC/measurement registers.

Persistence is hardware-defined. Configuration usually survives until modeset reprogramming, power-gating, suspend/resume restore, or ASIC reset. Status, fault, interrupt, counter, and memory-power state may be sticky, self-clearing, read-only, write-one-to-clear, or sampled by hardware. This header does not describe those access classes.

## Dependencies And Integration Points

Companion generated metadata:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h`

Direct include sites found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`

Key integration points:

- `dcn316_resource.c` builds four DPP register tables with `DPP_REG_LIST_DCN30(id)` and four HUBP register tables with `HUBP_REG_LIST_DCN30(id)`. This chunk contains all HUBP/HUBPREQ/HUBPRET/CURSOR offsets for instances 0-3 and DPP offsets for instances 0-1; DPP instances 2-3 are outside this range.
- `dcn316_resource.c` pairs these offsets with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT/_MASK)` and `HUBP_MASK_SH_LIST_DCN31(__SHIFT/_MASK)`, so this chunk must remain synchronized with the DCN316 shift/mask header and the common DCN30/DCN31 DPP/HUBP field-list macros.
- `dmub_dcn316.c` includes the same generated namespace and expands DMUB register and field macros into `dmub_srv_dcn316_regs`; even where this exact chunk is not DMUB-specific, the base-index convention and generated names must remain consistent for the shared DCN316 register namespace.
- HUBP implementations such as the DCN10/DCN21/DCN31 HUBP code use fields from these offset families when setting surface addresses, metadata addresses, VMID, pitch, surface control, flip parameters, cursor state, and readback status.
- DPP implementations use the CNVC, DSCL, CM, DPP_TOP, and perfmon offsets when programming input pixel conversion, scaling, line-buffer layout, color transforms, gamma/blender/shaper LUTs, memory power state, CRC, and diagnostics.

## Risks And Edge Cases

- Generated-offset drift is the primary risk. A wrong offset or base index compiles cleanly but can program the wrong MMIO register, corrupt another pipeline, or make readback/status misleading.
- The chunk begins mid-register group. `regDCN_VM_CONTEXT15_PAGE_TABLE_START_ADDR_LO32_BASE_IDX` appears without its offset macro in this range, and the remaining VM macros are only the tail of a larger VM block.
- The chunk ends mid-register group. `CM1_CM_SHAPER_RAMB_REGION_14_15` is the last register here; later `CM1_CM_SHAPER_RAMB_REGION_*` entries and any following DPP1/DPP2 state must be merged from later chunks.
- HUBP/HUBPREQ offsets are plane-critical. Mistakes in surface addresses, metadata addresses, pitch, tiling, DCC/TMZ controls, viewport geometry, VMID, or flip controls can cause page faults, underflow, stale scanout, corruption, blanking, or secure-memory violations.
- Flip and in-use registers are sequencing-sensitive. Driver code must respect update locks, vblank timing, pending status, triple-buffering/GSL behavior, and hardware readback semantics; the generated offsets cannot enforce those rules.
- TTU/QoS/prefetch/vblank/nominal timing registers are tightly coupled to DML calculations. Incorrect offsets can produce memory underflow, late flips, or unstable high-refresh/multi-plane modes.
- Cursor and DMDATA registers mix visible cursor state, memory fetch state, QoS, and software data paths. Wrong programming can affect cursor composition without changing primary plane state.
- DPP scaler and color registers are dense and indexed. Coefficient RAM, gamma/blender/shaper LUT index/data pairs, RAM A/B regions, 3D LUT controls, and color matrix registers require correct ordering and banking; offset errors can produce color shifts, banding, or corrupted LUT loads.
- Memory power control/status registers are side-effectful. Writing control bits without waiting for matching status can race later register access, especially across suspend/resume and power-gating transitions.
- Perfmon registers are diagnostic but still stateful. Incorrect counter control or acknowledge offsets can leave interrupts asserted or make performance data invalid.

## Test Signals

Useful validation combines generated-header consistency checks, builds, and hardware behavior:

- Build AMDGPU/DC with DCN316 enabled. Missing or renamed macros should fail in `dcn316_resource.c`, `dmub_dcn316.c`, and common HUBP/DPP code that consumes DCN316 tables.
- Mechanically verify that every `reg...` offset macro in lines 2690-5205 has a matching `reg..._BASE_IDX` macro in the same range, while allowing the known leading boundary exception where a `_BASE_IDX` appears without its offset.
- Compare DCN316 offsets against AMD's authoritative generated register database and adjacent DCN 3.1.x headers where the same block instances are expected to align.
- Exercise plane enable/disable, primary and chroma address programming, metadata/DCC, flips, triple-buffering, VMID changes, cursor enable/move/format changes, and secure-surface/TMZ paths on DCN316 hardware. Watch for faults, underflow, stale frames, corruption, and missing flip completion.
- Exercise multi-plane and multi-display modes that use HUBP instances 0-3 and DPP instances 0-1, including scaling, chroma formats, rotation/tiling variants, and high-bandwidth modes that stress prefetch/TTU/QoS registers.
- Exercise DPP color features: pre-CSC/post-CSC, gamut remap, gamma correction, blender gamma, shaper LUTs, HDR multiplier, dealpha, color keying, and 3D LUT setup for DPP0. Validate visual output and LUT load completion/readback where available.
- Exercise suspend/resume, runtime power management, and memory power transitions for HUBPREQ/HUBPRET/CURSOR/DSCL/CM blocks. Check that status bits settle and that post-resume scanout, cursor, scaler, and color state are restored.
- Exercise perfmon and CRC/debug readbacks for the listed DC perfmon instances and DPP top-level registers. Confirm counters run/stop/ack correctly and diagnostics point to the expected hardware instance.

## Cross-Chunk Notes

This is a middle chunk of `dcn_3_1_6_offset.h`. It starts with the tail of a VM block and ends inside DPP1 CM shaper RAMB region offsets. The final per-file research document should merge this with neighboring chunks before making complete-file claims about all DCN VM registers, all DPP instances, or the full CM1 shaper/3D-LUT register coverage.
