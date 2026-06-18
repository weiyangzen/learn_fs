# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 22381-24801

## Scope

This chunk is a generated AMD GC 10.3.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value used by AMDGPU register helpers to compose or decode 32-bit MMIO/indexed-register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin at the final visible mask for `CB_BLEND3_CONTROL`, then cover complete `CB_BLEND4_CONTROL` through `CB_BLEND7_CONTROL` entries, graphics pipeline state registers, primitive assembly/setup/scissor/rasterizer controls, geometry/tessellation/NGG/streamout controls, depth/color test controls, sample-location state, binner/conservative-raster controls, and color-buffer target state for `CB_COLOR0` through most of `CB_COLOR6`. The chunk ends at the `//CB_COLOR6_CLEAR_WORD1` marker before that register's field macros, so the `CB_COLOR6` render-target slot is intentionally incomplete in this chunk and continues in the next adjacent slice.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 10.3 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_10_3_0_sh_mask.h` supplies the bit layouts for GC 10.3.0 registers. Driver code pairs these macros with register addresses from `gc_10_3_0_offset.h` and, where useful, defaults from `gc_10_3_0_default.h`. Consumers use the constants through helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` so they can change or inspect one hardware field without hard-coding magic bit positions.

This chunk focuses on the graphics draw and render-backend state needed to issue draws and configure rasterization/output-merger behavior:

- Blend-state controls for render targets 4 through 7, including source/destination blend factors, color/alpha combine functions, separate alpha blending, enable, and ROP3 disable.
- Draw and index-fetch controls such as `VGT_DMA_BASE`, `VGT_DMA_BASE_HI`, `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, `VGT_DMA_INDEX_TYPE`, `VGT_DRAW_INITIATOR`, `VGT_IMMED_DATA`, `VGT_EVENT_ADDRESS_REG`, `VGT_DMA_EVENT_INITIATOR`, and multi-primitive reset state.
- Depth, stencil, EQAA, alpha-to-mask, shader depth/export, and color-control fields in `DB_DEPTH_CONTROL`, `DB_EQAA`, `DB_SHADER_CONTROL`, `DB_ALPHA_TO_MASK`, and `CB_COLOR_CONTROL`.
- Clip/setup/rasterization controls under `PA_CL_*`, `PA_SU_*`, and `PA_SC_*`, including clip distance enables, viewport transform enables, vertex output controls, NaN/Inf handling, point and line sizing, line stipple, polygon offset, primitive filtering, conservative rasterization, binner behavior, variable-rate shading, stereo routing, centroid priority, MSAA sample locations, AA masks, and scan-converter behavior.
- Vertex-geometry-tessellation state under `VGT_*` and `GE_*`, including output path, tessellation parameters, LS/HS/GS stage enable/configuration, GS ring offsets/item sizes, NGG subgroup controls, primitive grouping, streamout buffers, instance stepping, primitive ID behavior, and shader-stage enable flags.
- Color-buffer render-target descriptors for `CB_COLOR0` through `CB_COLOR5`, plus most of `CB_COLOR6`, including base addresses, pitch/slice/view geometry, format/type/swap/compression bits, sample/fragment counts, tiling, DCC control, CMASK/FMASK/DCC metadata bases, and fast-clear words.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion offset header, typically with names such as `mmCB_COLOR0_INFO` or `mmVGT_DRAW_INITIATOR` depending on the register space.
- AMDGPU callers normally access these fields through `REG_SET_FIELD`, `REG_GET_FIELD`, read-modify-write MMIO helpers, packet-building code, or PM4/state-emission paths.

The main register families in this slice are:

- `CB_BLEND4_CONTROL` through `CB_BLEND7_CONTROL`: repeated render-target blend layouts. Each has color and alpha source/destination blend fields, color and alpha combine-function fields, `SEPARATE_ALPHA_BLEND`, `ENABLE`, and `DISABLE_ROP3`.
- `CS_COPY_STATE` and `GFX_COPY_STATE`: small state-copy selector registers with `SRC_STATE_ID`.
- Point/clip full-width data registers: `PA_CL_POINT_X_RAD`, `PA_CL_POINT_Y_RAD`, `PA_CL_POINT_SIZE`, `PA_CL_POINT_CULL_RAD`, and guard-band adjust registers all expose 32-bit data fields.
- `DB_DEPTH_CONTROL`, `DB_EQAA`, `DB_SHADER_CONTROL`, and `DB_ALPHA_TO_MASK`: depth/stencil test enables and functions, EQAA sample counts and over-rasterization, shader Z/stencil/export order behavior, alpha-to-mask enable and per-sample offsets.
- `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, `PA_CL_NGG_CNTL`, and `PA_CL_VRS_CNTL`: clipper and viewport-transform control, vertex shader output component enables, NaN/Inf treatment, NGG vertex reuse controls, and VRS rate-combiner policy.
- `PA_SU_SC_MODE_CNTL`, `PA_SU_*`, and `PA_SC_*`: setup and scan-converter controls for culling, polygon mode, provoking vertex, small primitive filtering, over-rasterization, stereo, point/line dimensions, stipple, binner, conservative rasterization, sample locations, AA config, shader control, and viewport/scissor-related behavior.
- `VGT_*` and `GE_*`: draw initiation, DMA/index type, event initiation, output path, hull/tessellation parameters, group primitive/vector formatting, GS mode/on-chip controls, LS/HS config, GS ring/item sizing, streamout setup, primitive ID handling, instance step rates, shader-stage enablement, NGG subgroup sizing, and tessellation distribution.
- `CB_COLORn_*` for `n = 0..5` and partial `n = 6`: render-target state. The repeated layout includes `BASE`, `PITCH`, `SLICE`, `VIEW`, `INFO`, `ATTRIB`, `DCC_CONTROL`, `CMASK`, `CMASK_SLICE`, `FMASK`, `FMASK_SLICE`, `CLEAR_WORD0`, `CLEAR_WORD1`, and `DCC_BASE`. For `CB_COLOR6`, this chunk reaches `CLEAR_WORD0` and the `CLEAR_WORD1` marker, but not the actual `CLEAR_WORD1` shift/mask macros.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 10.3.0 register header for the active ASIC generation.
2. Choose the matching register address from `gc_10_3_0_offset.h`.
3. Read an existing register value or prepare a command-stream register write.
4. Use the `__SHIFT`/`__MASK` pairs, often through field helper macros, to pack a field value or extract a status/configuration field.
5. Submit the resulting MMIO write or PM4 register packet in a larger draw, pipeline-state, streamout, render-target, reset, or resume sequence.

For draw setup, higher-level code programs VGT/IA/GE shader-stage and DMA/index state before draw initiation. For rasterization, PA/SC/SU state controls clipping, sample positions, binner/conservative-raster behavior, VRS, culling, line/point/polygon details, and primitive filtering. For output-merger state, DB and CB registers configure depth/stencil behavior, blending, alpha-to-mask, color target formats, compression, metadata, and clear values. This file does not define ordering constraints, packet sequences, cache flushes, waits, or hardware side effects; those are owned by the surrounding AMDGPU pipeline code and hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware and by the AMDGPU command stream.

Most fields in this chunk represent graphics pipeline context state. Values persist in the GPU context or hardware register file until overwritten by later command packets, context switch restore, graphics IP reset, suspend/resume reinitialization, power-gating loss, or driver/firmware reprogramming.

The `CB_COLORn_*` registers describe render-target surfaces and associated metadata. `BASE`, `CMASK`, `FMASK`, and `DCC_BASE` fields are GPU address fragments in 256-byte units. `PITCH`, `SLICE`, `VIEW`, `INFO`, and `ATTRIB` encode image geometry, format, tiling, samples/fragments, compression, and view selection. `CLEAR_WORD0/1` store fast-clear color words. Incorrect persistence or stale restore of these fields can make later draws write the wrong surface, use the wrong compression mode, or interpret metadata incorrectly.

Depth/stencil, sample-location, streamout, and shader-stage registers are also stateful. Some fields are pure configuration; others initiate events or describe DMA/draw operations, such as `VGT_DRAW_INITIATOR`, `VGT_DMA_EVENT_INITIATOR`, and related VGT DMA fields. The shift/mask header does not encode whether a field is read-only, write-only, pulse-style, sticky, clear-on-read, or preserved across resets, so callers must rely on the hardware specification and established AMDGPU programming sequences.

Reserved bits and partial-register fields should be preserved during read-modify-write unless a documented full-register value is being emitted. This is especially important for PA/SC/VGT feature controls and CB/DCC compression state, where undocumented or generation-specific bits can change behavior.

## Dependencies And Integration Points

This chunk depends on the generated GC 10.3.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` provides the matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` provides default/reset values for many of the same registers.
- AMDGPU GC 10.3 graphics code, command submission paths, KFD/compute integration, Mesa/userspace command-stream producers, debug tooling, and suspend/resume/reset code rely on the same hardware bit assignments being accurate.
- Common AMDGPU register helpers provide the actual packing, extraction, MMIO, and command-packet emission mechanisms.

Integration points include draw packet emission, index-buffer setup, primitive assembly, NGG/GS/tessellation enablement, streamout, depth/stencil tests, MSAA/EQAA/VRS, conservative rasterization, viewport/clip setup, render-target binding, fast clears, DCC/CMASK/FMASK metadata programming, GPU reset restoration, and hardware bring-up diagnostics. The repeated `CB_COLORn_*` layout is particularly important for render-target arrays and MRT rendering because userspace and kernel code must agree on slot numbering and field packing.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits, which can present as rendering corruption, hangs, incorrect blending, broken depth tests, bad compression metadata, or performance regressions.
- The chunk starts and ends mid-family. It starts with only the last visible `CB_BLEND3_CONTROL` mask and ends before `CB_COLOR6_CLEAR_WORD1` field macros, so file-level conclusions must be merged with adjacent chunks.
- Repeated render-target layouts invite copy/paste or generator errors. `CB_COLOR0` through `CB_COLOR6` should remain structurally aligned where hardware requires it, but a single slot-specific mismatch can affect only one MRT target.
- Address fields are expressed as base units, commonly `BASE_256B`, not raw byte addresses. Consumers that shift or align addresses incorrectly can program plausible but invalid GPU addresses.
- Compression-related fields are high risk: `DCC_ENABLE`, `DCC_COMPRESS_DISABLE`, CMASK/FMASK base and slice fields, lossy precision, independent block settings, and fast-clear words must match the surface metadata layout and cache/flush protocol.
- DB/CB/PA/SC/VGT registers interact. For example, MSAA sample counts, sample locations, EQAA settings, alpha-to-mask, FMASK attributes, and color/depth target state must be mutually consistent.
- Event/draw initiator and DMA fields can have command-like side effects. Treating them as passive state or performing unsafely ordered writes may trigger wrong draws/events or undefined hardware behavior.
- Reserved fields and undocumented bits appear throughout this generated map. Full-register writes that do not preserve these bits can break generation-specific behavior.
- Some fields use high bits, full-width masks, or packed repeated nibbles. Callers should use unsigned 32-bit intermediates and helper macros rather than signed arithmetic or ad hoc constants.

## Test Signals

Useful validation is primarily build coverage, generated-data consistency, and hardware/runtime rendering coverage:

- Kernel build coverage for AMDGPU files that include `gc_10_3_0_sh_mask.h`, especially GC 10.3/Navi 2x graphics, display-interacting render paths, KFD, reset, and suspend/resume code.
- Mechanical comparison against AMD's authoritative GC 10.3.0 register database to confirm each `__SHIFT` and `__MASK` value and each repeated register family.
- Cross-checks that all registers in this slice have matching address macros in `gc_10_3_0_offset.h` and expected defaults in `gc_10_3_0_default.h` where defaults are generated.
- Static mask/shift sanity checks: masks should align with shifts, repeated `CB_COLORn_*` and `CB_BLENDn_CONTROL` layouts should be consistent across slots, and full-width data fields should use `0xFFFFFFFFL`.
- Render tests covering MRT blending, separate alpha blend, ROP3 behavior, depth/stencil compare and writes, alpha-to-mask, MSAA/EQAA sample positions, VRS, conservative rasterization, line/point rendering, polygon offset, and clip/guard-band behavior.
- Streamout, GS, tessellation, NGG, primitive ID, indirect/indexed draw, and multi-instance draw tests that exercise the VGT/GE fields in this chunk.
- Fast-clear and compression tests for color targets using CMASK/FMASK/DCC, including suspend/resume and GPU-reset restore paths.
- Runtime warning signals include GPU hangs during draw initiation, corrupted render targets, bad MRT slot output, incorrect depth/stencil behavior, mismatched fast-clear colors, DCC/metadata corruption, unexpected fallback to uncompressed rendering, or workload-specific regressions around binner/conservative-raster/VRS features.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002485`. It covers lines 22381-24801 of `gc_10_3_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial `CB_BLEND3_CONTROL` and `CB_COLOR6` families and to place this draw/raster/render-target state in the full GC 10.3.0 register map.
