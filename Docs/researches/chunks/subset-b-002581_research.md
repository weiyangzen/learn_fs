# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 30174-32555

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value for composing or decoding 32-bit GPU register values. There are no functions, structs, enums, global variables, includes, branches, allocations, locks, callbacks, or persistence logic in this range.

The selected lines begin after the final `CB_BLEND7_CONTROL` field masks, then cover primitive assembly, clipper, setup, scan-converter, binner, variable-rate shading, HiZ/HiS, color-buffer target, color memory-policy, and PA/SC enhancement/debug register fields. The chunk ends after the complete `SC_MEM_SCOPE` field definitions and before the next `gc_gfx_se_gfx_se_pfvf_sqdec` address block starts with `SQ_RUNTIME_CONFIG`.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_0_0_sh_mask.h` supplies bit layouts for GC 12.0.0 registers. Driver code pairs these macros with register addresses from the matching offset header and, where available, defaults from the matching default header. Consumers normally use helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` to avoid open-coded bit shifts and masks.

This slice focuses on the graphics front-end, rasterization, render-target, binner, and scan-converter control surface:

- Clipper and setup state, including point radii/size, user clip planes, viewport transform enables, vertex-output side-band enables, NaN/Inf handling, culling, polygon mode, line stipple, small-primitive filtering, over-rasterization, stereo routing, and primitive-rate or vertex-rate VRS combiners.
- Scan-converter state, including scissor/MSAA mode, walk order, tile coverage, sample iteration, anti-alias sample locations and masks, centroid priority, line rasterization, conservative rasterization, shader-control fields, and sample distance.
- Binner and NGG controls, including bin dimensions, context/persistent states per bin, batch limits, ping-pong bin order, light-volume optimizations, ZPP, wave/deallocation limits, event masks, timeout counters, and binner performance thresholds.
- HiZ/HiS and VRS surface metadata, including surface format, swizzle mode, bases, extents, flush/sync controls, tag limits, eviction policy, debug overrides, and memory scope fields.
- Color-buffer target descriptors for `CB_COLOR0` through `CB_COLOR7`, including base address fragments, view slice ranges, mip level, fragment count, FDCC compression policy, dimensions, swizzle/resource metadata, extended base bits, render-target format/type/swap/rounding fields, and temporal read/write hints.
- PA/SC and PA/PH enhancement registers that expose hardware workarounds, clock-gating controls, out-of-order processing knobs, binner/PBB overrides, FIFO sizing, trap-screen write locks, and debug/performance-control fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion GC 12.0.0 offset header, typically as `mm...` macros.
- AMDGPU callers usually combine these with `REG_SET_FIELD`, `REG_GET_FIELD`, MMIO helpers, indexed-register helpers, or PM4/state-emission paths.

Important register families in this slice include:

- `PA_CL_*`, `PA_SU_*`, and `PA_STEREO_*`: point, clip, viewport-transform, vertex-output, culling, primitive filtering, line, polygon offset, stereo, over-rasterization, and VRS-combiner fields.
- `PA_SC_*`: scan-converter mode, AA config, centroid priority, sample locations, AA masks, binner controls, NGG mode, conservative rasterization, shader control, VRS surface control, HiZ/HiS state, enhancement/debug registers, FIFO sizing, event controls, timeout counters, and performance histogram thresholds.
- `DB_HTILE_SURFACE` and `DB_SRESULTS_COMPARE_STATE0/1`: depth/HTILE surface control and stencil-results comparison fields that interact with PA/SC HiZ/HiS behavior.
- `GE_MAX_OUTPUT_PER_SUBGROUP`, `GE_SE_ENHANCE`, `VGT_REUSE_OFF`, `VGT_DRAW_PAYLOAD_CNTL`, `VGT_GS_MAX_VERT_OUT`, `VGT_GS_INSTANCE_CNT`, and `GE_NGG_SUBGRP_CNTL`: geometry, NGG, draw-payload, reuse, and GS-output controls.
- `CB_TARGET_MASK`, `CB_SHADER_MASK`, `CB_COLOR_CONTROL`, `CB_COLORn_*`, and `CB_MEMn_INFO`: color-output masks, blend/ROP control, render-target descriptors, FDCC compression controls, base extension bits, format/type metadata, and temporal read/write policy for eight color targets.
- `PA_SC_HIZ_*`, `PA_SC_HIS_*`, `PA_SC_VRS_SURFACE_CNTL`, `PA_SC_VRS_SURFACE_CNTL_1`, and `SC_MEM_SCOPE`: hierarchical depth/stencil and VRS surface controls, debug overrides, cache/flush/sync behavior, and memory-scope selectors.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 12.0.0 register definitions for the active ASIC.
2. Choose a register address from the matching offset header.
3. Prepare a register value from command-stream state or read an existing register for read-modify-write.
4. Pack or extract fields using the `__SHIFT`/`__MASK` pairs, usually through common AMDGPU field helpers.
5. Emit MMIO writes or PM4 packets as part of draw setup, render-target binding, rasterization setup, binner configuration, reset/resume restore, or diagnostic programming.

At runtime, graphics setup code programs PA/SC/SU/VGT/GE state before draws, then CB and DB-related state controls color and depth/stencil output. Binner, PBB, VRS, HiZ, and HiS settings influence how primitives are tiled, culled, shaded, and compressed. This header does not define packet ordering, cache flush requirements, waits, register access methods, or hardware side effects; those responsibilities stay in the AMDGPU programming sequences and hardware specification.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose values live in hardware context state, MMIO-visible registers, or command-stream state until overwritten, restored during context switch, reset during GPU reset, lost during power transitions, or reinitialized on suspend/resume.

Most fields in this chunk are persistent graphics context state: clipper controls, rasterizer modes, sample locations, binner policy, render-target descriptors, VRS/HiZ/HiS surface controls, and PA/SC enhancement bits. Incorrectly restored or stale state can affect later draws even if the current draw does not explicitly touch the same feature.

`CB_COLORn_*` registers are especially stateful. `BASE` and `BASE_EXT` encode GPU-address fragments, `VIEW`/`VIEW2` select slices and mips, `ATTRIB*` define fragment count, dimensions, swizzle mode, resource type, and speculative-read behavior, `FDCC_CONTROL` selects compression behavior, and `INFO` defines format/number type/component swap/rounding. A stale or mispacked color-target field can redirect rendering, corrupt metadata, break blending, or make one MRT slot behave differently from the others.

HiZ/HiS and VRS surface fields also persist across draw sequences. Base, extent, format, swizzle, flush, eviction, sync, tag-limit, and debug override fields must match depth/stencil/VRS metadata allocation and synchronization policy. `SC_MEM_SCOPE` adds memory-scope selectors for VRS rate, VRS feedback, HiZ, and HiS surfaces.

The header does not encode whether individual hardware fields are read-only, write-only, pulse-style, sticky, reset-only, privileged, or safe for read-modify-write. Callers must preserve reserved bits unless a documented full-register value is being emitted, especially for enhancement, debug, cache/sync, and workaround registers.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register set staying internally consistent:

- The matching `gc_12_0_0_offset.h` provides register addresses for these field macros.
- The matching `gc_12_0_0_default.h`, when generated for the same register families, provides reset/default values.
- Common AMDGPU register helpers provide the packing, extraction, MMIO, indexed-register, and command-packet mechanisms.
- Graphics IP initialization, ring/PM4 state emission, reset/suspend/resume restore, debugfs or diagnostics, KFD interactions, and userspace command-stream assumptions rely on these bit layouts matching the hardware database.

Integration points include draw payload setup, GS/NGG configuration, primitive culling/filtering, clip/viewport transform, point/line/polygon rasterization, scissor and tile walk order, MSAA sample positions, centroid selection, VRS rate selection and surface feedback, conservative rasterization, binner/PBB policy, depth/stencil HiZ/HiS acceleration, color target binding, FDCC compression, temporal memory policy, and PA/SC hardware-workaround programming.

The `gc_gfx_se_gfx_se_pfvf_padec` address-block marker in the middle of the slice indicates that later registers in the chunk belong to a PA decode area separate from the preceding context-state-style groups. Merge-level research should keep that block boundary because it often maps to different register ranges or access paths in the offset header.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask compiles successfully but writes the wrong hardware bits, causing rendering corruption, hangs, missing primitives, bad depth/stencil results, broken VRS, or one-target-only MRT failures.
- The chunk starts mid-family after `CB_BLEND7_CONTROL`; final per-file research must merge the preceding chunk to capture the full blend-control family.
- Repeated `CB_COLOR0` through `CB_COLOR7` layouts invite generator or copy errors. Slot-specific mismatches can affect only one render target and may escape broad smoke tests.
- Address fields such as `BASE_256B` and `BASE_EXT` are not raw byte addresses. Incorrect alignment or unit conversion can program plausible but wrong GPU addresses.
- Compression and metadata fields are high risk: FDCC compression controls, HiZ/HiS base/size/format fields, VRS surface controls, temporal hints, and cache/flush/sync knobs must agree with memory allocation, metadata layout, and cache-management sequences.
- PA/SC enhancement and debug registers expose many workaround, clock-gating, out-of-order, reset, binner, and performance knobs. Full-register writes that do not preserve reserved or ASIC-specific bits can cause subtle performance or correctness regressions.
- MSAA, sample locations, centroid priority, AA masks, VRS rates, conservative rasterization, and exposed/detail sample counts are tightly coupled. Inconsistent programming can produce coverage artifacts that are difficult to diagnose from a single register.
- Event-mask and binner controls can alter batching and synchronization behavior. Treating these as passive state without respecting hardware ordering can cause missed flushes, premature batch breaks, or stale metadata visibility.
- Several fields occupy high bits or full 32-bit masks. Consumers should use unsigned 32-bit arithmetic and helper macros rather than signed shifts or hand-written constants.

## Test Signals

Useful validation is primarily build coverage, generated-data consistency, and hardware/runtime rendering coverage:

- Kernel build coverage for AMDGPU files that include `gc_12_0_0_sh_mask.h`, especially GC 12 graphics initialization, command submission, reset, suspend/resume, and diagnostics.
- Mechanical comparison against AMD's authoritative GC 12.0.0 register database for every `__SHIFT`/`__MASK` pair in this chunk.
- Cross-checks that all registers in this slice have matching address macros in `gc_12_0_0_offset.h` and expected defaults in `gc_12_0_0_default.h` where defaults are generated.
- Static sanity checks that masks align with shifts, repeated `CB_COLORn_*`, `CB_MEMn_INFO`, and AA sample-location layouts remain consistent across slots/pixels, and full-width data registers use `0xFFFFFFFFL`.
- Rendering tests for MRT color output, color masks, blend/ROP interaction, target format/type/component swap, FDCC/compression behavior, fast clears where adjacent registers provide clear state, and suspend/resume or reset restore of render-target state.
- Rasterization tests for clipping, point and line rendering, line stipple, polygon offset, culling, small-primitive filtering, conservative rasterization, MSAA sample positions, centroid interpolation, VRS, stereo/view routing, and viewport/scissor behavior.
- Binner/PBB/NGG tests that exercise bin sizing, batch limits, primitive grouping, event controls, timeout paths, light-volume optimizations, ZPP, and out-of-order PA/SC controls.
- Depth/stencil and metadata tests covering HiZ/HiS enablement, base/extent programming, flush/invalidate/sync behavior, debug override registers, and mixed depth/stencil/VRS workloads.
- Runtime warning signals include GPU hangs around draws or batch transitions, corrupted render targets, incorrect coverage or sample interpolation, broken VRS rates, bad depth/stencil culling, metadata corruption, unexpected performance cliffs from binner/enhancement settings, and regressions isolated to one color target or one MSAA mode.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002581`. It covers lines 30174-32555 of `gc_12_0_0_sh_mask.h`. The final per-file document should merge this with adjacent chunks to complete the preceding `CB_BLEND7_CONTROL` context and continue with the following SQ runtime configuration block.
