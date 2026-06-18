# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 14859-17371

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains C preprocessor constants only: each register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines start in the GDS ordered-append VMID mask family, covering `GDS_OA_VMID4` through `GDS_OA_VMID15`, then describe GDS/GWS resource resets, GDS context-switch status/counters, and GDS memory-clean control. The middle of the chunk switches to `addressBlock: gc_rasdec` for RAS signature-control and signature registers. The rest is the beginning of `addressBlock: gc_gfxdec0`, covering depth-buffer, scan converter, color-buffer, viewport, clip-plane, variable-rate-shading, command-processor context identity, and pixel-shader input-control state. The range ends after the `SPI_PS_INPUT_CNTL_29__USE_DEFAULT_ATTR1_MASK` macro; the remaining masks for `SPI_PS_INPUT_CNTL_29` continue in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 11.5.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_11_5_0_sh_mask.h` supplies bit layouts for GC 11.5.0 registers. AMDGPU code combines these masks with register addresses from the matching `gc_11_5_0_offset.h` header and usually accesses fields through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD`. This lets engine setup, command submission, debug, reset, and state-restore code program one hardware field without embedding raw bit positions.

This chunk focuses on graphics context and render-state metadata:

- GDS and GWS controls for per-VMID ordered-append masks, per-resource reset bits, single-resource reset by ID, OA reset masks by ME/pipe, context-switch read/write status, context-switch up/down pointer counters for CS/PS/GS paths, packer-index selection, and memory clean start/finish bits.
- RAS decode registers for enabling signature collection, masking the input bus, and exposing full-width signatures for SX, DB, PA, SC, SPI, CB, and BCI blocks.
- DB state for depth/stencil render control, z-pass counting, depth view dimensions and slices, depth/stencil compression and override behavior, HTILE and depth/stencil base addresses, depth bounds, clear values, Z/stencil surface formats, cache policy, and VRS center offsets.
- PA/SC state for screen/window/generic/viewport scissors, clip-rectangle rules, edge rules, hardware screen offsets, 16 viewport scissor rectangles, 16 viewport Z min/max pairs, raster configuration, screen extent, tile steering, and VRS surface/feedback base, size, override, and cache policy.
- CB state for target and shader masks, GL2 cache policy, blend constants, FDCC controls, coverage export, and color/depth/stencil interaction.
- PA/CL state for 16 viewport transform groups (`XSCALE`, `XOFFSET`, `YSCALE`, `YOFFSET`, `ZSCALE`, `ZOFFSET`) and six user clip planes with X/Y/Z/W components.
- SPI pixel-shader input controls `SPI_PS_INPUT_CNTL_0` through the partial `SPI_PS_INPUT_CNTL_29`, describing attribute offsets, default values, flat shading, primitive attributes, duplicate handling, FP16 interpolation, secondary-default behavior, and attribute validity.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the 32-bit register value.
- Register-address symbols live in the companion offset header, commonly as `mm...` symbols matching the same register name.
- AMDGPU callers normally combine these with register helpers, MMIO accessors, PM4 packet construction, context-save/restore tables, debug dumps, and register validation paths.

The main macro families in this chunk are:

- `GDS_OA_VMID4..15`: ordered-append VMID mask registers. Each has a 16-bit `MASK` field and high `UNUSED` bits.
- `GDS_GWS_RESET0`, `GDS_GWS_RESET1`, and `GDS_GWS_RESOURCE_RESET`: 64 bit-addressable GWS resource reset bits plus an indexed reset form with `RESET` and `RESOURCE_ID`.
- `GDS_OA_RESET_MASK` and `GDS_OA_RESET`: reset enables for ME0 graphics/compute and ME1/ME2 pipe reset targets, plus an indexed pipe-reset form.
- `GDS_*_CTXSW_STATUS`, `GDS_*_CTXSW_CNT*`, and `GDS_PS_CTXSW_IDX`: context-switch status bits (`R`, `W`), 16-bit `UPDN`/`PTR` counter packing, and a PS packer selector.
- `RAS_SIGNATURE_*` and `RAS_*_SIGNATURE*`: RAS signature enable/mask and full 32-bit signature readouts for shader export, depth buffer, primitive assembly, scan converter, SPI, color buffer, and BCI units.
- `DB_*`: depth/stencil render controls, count controls, view/surface info, address low/high pairs, compression/decompression overrides, clear values, stencil operations, and RMI/L2 cache controls.
- `PA_SC_*`: scissor, clip rectangle, viewport Z range, raster mapping, screen extent, tile steering, VRS override/base/size/cache, and VRS feedback surface fields.
- `CB_*`: color target write masks, shader-output masks, GL2 cache policy, blend constants, FDCC, coverage export, and related color-buffer control fields.
- `PA_CL_VPORT_*` and `PA_CL_UCP_*`: full-width floating-point viewport transforms and user clip-plane coefficients.
- `SPI_PS_INPUT_CNTL_*`: repeated per-attribute pixel-shader input controls. Entries 0-18 include `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `ROTATE_PC_PTR`, `PRIM_ATTR`, `PT_SPRITE_TEX`, `OUT_OF_ORDER_RT`, `DUP`, `FP16_INTERP_MODE`, `USE_DEFAULT_ATTR1`, `DEFAULT_VAL_ATTR1`, `ATTR0_VALID`, and `ATTR1_VALID`. Entries 19-29 use the same layout minus the point-sprite and out-of-order RT fields in this generated slice.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied AMDGPU runtime flow is:

1. Select the GC 11.5.0 register headers for the active ASIC.
2. Select the matching register address from `gc_11_5_0_offset.h`.
3. Read an existing register, prepare a context-state value, build a PM4 packet, or decode a debug/status dump.
4. Use the `__SHIFT` and `__MASK` pair, commonly through register field helpers, to pack or extract the relevant field.
5. Pass the composed value to graphics context setup, render-target/depth-state programming, viewport/scissor setup, VRS setup, shader-input routing, RAS signature checking, GDS/GWS reset, or hang/debug paths.

For render state, driver or userspace-generated command streams program DB, CB, PA/SC, PA/CL, and SPI context registers as part of graphics pipeline state. For GDS and RAS, flows are more diagnostic or maintenance oriented: reset selected GWS/OA resources, poll context-switch state, trigger memory clean, or collect block signatures. The header does not define ordering, synchronization, readback latching, or side-effect semantics; those are encoded in AMDGPU code, firmware interfaces, and the hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, and AMDGPU runtime programming.

GDS/GWS fields represent live global-data-share and global-wave-sync state. Resource reset fields have side effects, OA VMID masks govern which VMIDs can participate in ordered append behavior, and context-switch counters/status bits expose state that can change while engines are active. `GDS_MEMORY_CLEAN` start/finish fields imply a stateful hardware operation and should be treated as volatile rather than static configuration.

RAS signature fields are diagnostic state. `RAS_SIGNATURE_CONTROL__ENABLE` changes whether signatures are captured, `RAS_SIGNATURE_MASK` controls input masking, and the signature registers expose block-dependent values that may be valid only under the expected capture window. These values may be latched or stale according to hardware sequencing outside this header.

DB, CB, PA/SC, PA/CL, and SPI registers are graphics context state. They are programmed by command streams and can be saved/restored across context switches, suspend/resume, reset recovery, or virtualization boundaries. Depth/stencil base addresses and VRS surface bases are split low/high 256-byte address fields; viewport transforms and clip planes are full 32-bit data fields that usually encode floating-point values; scissor and rectangle fields pack signed or unsigned coordinate-like values into low/high halves.

Cache-policy, compression, HTILE, DCC/FDCC, partial-residency, fault-behavior, and no-allocate fields can affect memory traffic, correctness, and performance. Reserved and `UNUSED` fields appear throughout the generated map and should generally be preserved during read-modify-write unless the hardware sequence requires a documented full-register write.

SPI PS input controls define shader linkage state. Incorrect `OFFSET`, default-value, flat-shade, primitive-attribute, FP16 interpolation, duplicate, or attribute-valid bits can cause pixel shaders to read the wrong interpolants, substitute unexpected defaults, or mis-handle primitive/attribute data. The repeated layout means a one-bit drift can affect a single attribute lane while the rest of the pipeline appears healthy.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_default.h`, if present in the same register family, provides default/reset values for many registers.
- AMDGPU common register helper macros provide field packing/extraction and MMIO or command-packet access mechanisms.
- AMDGPU graphics, GDS, CP context, RAS, reset, debug, hang-dump, KFD/compute-adjacent, and power-management paths can include these generated constants.
- Userspace graphics stacks indirectly depend on these fields through kernel command submission, context register validation, and ASIC-specific packet/register programming expectations.

Integration points include GWS resource reset and cleanup, ordered-append behavior, GDS context-switch diagnostics, RAS signature collection, depth/stencil target setup, HTILE and Z/stencil base programming, color target write masks, DCC/FDCC behavior, GL2/RMI cache policy, VRS rate and feedback surface setup, rasterizer/scissor/viewport state emission, user clip-plane programming, command-processor context identity registers (`CP_PIPEID`, `CP_RINGID`, `CP_VMID`), performance-monitor context enablement, primitive restart index state, and pixel-shader interpolant setup.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can write the wrong hardware bits or decode misleading state.
- This chunk starts and ends mid-family. It begins after the first GDS OA VMID entries and ends before the last masks for `SPI_PS_INPUT_CNTL_29`; adjacent chunk research is needed for complete file-level conclusions.
- Repeated register families are easy to validate superficially but still risk single-index errors: GDS VMID masks, viewport scissors, viewport transforms, clip planes, and SPI input controls all repeat similar layouts.
- Reset fields such as `GDS_GWS_RESET*`, `GDS_GWS_RESOURCE_RESET`, and `GDS_OA_RESET*` have hardware side effects. Treating them like passive status fields can lose active synchronization resources or disrupt queues.
- Split address fields such as DB Z/stencil/HTILE bases and VRS base/feedback bases are 256-byte based with separate high registers. Incorrect alignment or high-word composition can point hardware at the wrong memory.
- DB compression, decompression, HTILE, DCC/FDCC, fault-behavior, partial-residency, and cache-policy fields affect correctness under render compression, sparse residency, reset recovery, and memory-fault conditions.
- Scissor, viewport, clip rectangle, and raster configuration masks determine screen-space clipping and shader export behavior. Incorrect sign/width assumptions can produce subtle rendering corruption rather than hard failures.
- RAS signatures are only useful when capture enable, input mask, block activity, and read timing match the hardware diagnostic sequence. This header cannot express those timing requirements.
- `UNUSED`, `RESERVED_FIELD_*`, and `DB_RESERVED_REG_*` macros expose bit positions but do not make those bits safe to program arbitrarily.
- `SPI_PS_INPUT_CNTL_*` fields are shader ABI sensitive. Attribute routing errors can manifest as wrong interpolation, incorrect primitive attributes, broken flat shading, or rendering failures isolated to particular pixel-shader inputs.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware/runtime graphics diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_11_5_0_sh_mask.h`, especially GC 11.5.0 graphics, GDS, RAS, reset, debug, and context-state paths.
- Mechanical comparison against AMD's authoritative GC 11.5.0 register database to confirm every `__SHIFT` and `__MASK` value in lines 14859-17371.
- Cross-checks that registers in this chunk have matching address macros in `gc_11_5_0_offset.h` and expected defaults in the matching default header where generated.
- Static sanity checks that masks align with shifts, full-width data fields use `0xFFFFFFFFL`, split address high/low widths match the register specification, and repeated families remain structurally consistent across indices.
- Render tests covering depth/stencil clear/copy/decompress, HTILE, depth bounds, stencil front/back operations, color target masks, shader output masks, blend constants, and coverage export.
- Viewport and rasterization tests covering all 16 viewports, screen/window/generic/viewport scissors, clip rectangles, user clip planes, primitive restart, edge rules, raster configuration, and tile steering.
- VRS tests covering override modes, rate surfaces, feedback surfaces, cache-policy fields, base/high address composition, and size fields.
- Pixel-shader interpolation tests that exercise flat shading, default attribute values, primitive attributes, duplicate inputs, FP16 interpolation, point-sprite coordinates, and attribute-valid bits across the `SPI_PS_INPUT_CNTL_*` range.
- GDS/GWS tests or debug traces that reset selected resources, validate OA VMID masks, observe context-switch counters, and confirm memory-clean start/finish behavior.
- RAS or diagnostic tests that enable signature capture, apply input masks, and compare SX/DB/PA/SC/SPI/CB/BCI signatures under controlled workloads.
- Runtime warning signals include rendering corruption, wrong depth/stencil behavior, broken VRS feedback/rate images, incorrect shader interpolants, GDS resource reset side effects, bad RAS signatures, GPU hangs during context restore, or debug dumps with impossible context/viewport/scissor state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002555`. It covers lines 14859-17371 of `gc_11_5_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the earlier `GDS_OA_VMID*` family and the trailing `SPI_PS_INPUT_CNTL_29` masks, and to place these GDS/RAS/GFXDEC0 definitions in the full GC 11.5.0 register map.
