# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a4xx.xml

## Purpose

`a4xx.xml` is a Freedreno register database for Qualcomm Adreno A4xx GPUs. It is declarative source for generated register, bitfield, enum, and packet helper definitions used by the MSM/Adreno DRM driver stack and related tooling. The file imports common Freedreno copyright, Adreno common register types, and PM4 packet definitions, then specializes the A4xx generation with A4xx color, texture, vertex, depth, tiling, performance counter, shader, render backend, vertex fetch, texture, SSBO, and bus interface layouts.

The primary domain is `A4XX`, a 32-bit MMIO register map covering render backend (`RB`), register bus/block manager (`RBBM`), command processor (`CP`), shader processor (`SP`), vertex/primitive blocks (`VFD`, `VPC`, `VSC`, `PC`), texture processor (`TPL1`), raster/triangle setup (`GRAS`), unified cache (`UCHE`), high-level sequencer (`HLSQ`), and VBIF memory-bus registers. Additional domains describe packed state records emitted to command streams: `A4XX_TEX_SAMP`, `A4XX_TEX_CONST`, `A4XX_SSBO_0`, and `A4XX_SSBO_1`.

## Important APIs, Types, and Generated Surface

This file does not define C functions; its API is the generated symbolic interface consumed by driver code and debug tools. Important generated symbols include:

- Format enums: `a4xx_color_fmt`, `a4xx_vtx_fmt`, `a4xx_tex_fmt`, `a4xx_depth_format`, and `a4xx_tile_mode`. These map Gallium/DRM texture, render-target, vertex-buffer, depth/stencil, and tiling choices into hardware numeric encodings.
- Performance counter selector enums for major blocks: `a4xx_ccu_perfcounter_select`, `a4xx_cp_perfcounter_select`, `a4xx_gras_ras_perfcounter_select`, `a4xx_gras_tse_perfcounter_select`, `a4xx_hlsq_perfcounter_select`, `a4xx_pc_perfcounter_select`, `a4xx_rb_perfcounter_select`, `a4xx_rbbm_perfcounter_select`, `a4xx_sp_perfcounter_select`, `a4xx_tp_perfcounter_select`, `a4xx_uche_perfcounter_select`, `a4xx_vbif_perfcounter_select`, `a4xx_vfd_perfcounter_select`, `a4xx_vpc_perfcounter_select`, and `a4xx_vsc_perfcounter_select`.
- Register families in `A4XX`: `RB_MRT[8]`, `RB_VPORT_Z_CLAMP[16]`, `CP_PROTECT[16]`, `CP_SCRATCH[23]`, shader output/varying arrays such as `SP_VS_OUT[16]`, `SP_VS_VPC_DST[8]`, `SP_FS_MRT[8]`, `SP_DS_OUT[16]`, `SP_DS_VPC_DST[8]`, `SP_GS_OUT[16]`, `SP_GS_VPC_DST[8]`, VSC pipe arrays, and `VFD_FETCH[32]`/`VFD_DECODE[32]`.
- Inline/reusable bitsets: `a4xx_sp_vs_fs_ctrl_reg0` for shader-stage thread/register-footprint controls and `a4xx_xs_control_reg` for HLSQ per-stage shader enable, object offset, SSBO enable, and instruction length state.
- Interrupt and status bitsets: `A4XX_INT0`, `RBBM_STATUS`, `RBBM_POWER_CNTL_IP`, and `RBBM_POWER_STATUS`, which expose idle, fault, timeout, cache, and power signals.
- Texture/SSBO state domains: `A4XX_TEX_SAMP` encodes filter, wrap, aniso, compare, normalized-coordinate, and LOD state; `A4XX_TEX_CONST` encodes texture format, swizzle, dimensions, pitch, type, layer size, and base address; `A4XX_SSBO_0`/`A4XX_SSBO_1` encode buffer/image base, pitch, array pitch, format, dimensions, and bytes-per-pixel metadata.

The XML references imported common types including `a3xx_rop_code`, `a3xx_color_swap`, `adreno_rb_dither_mode`, `adreno_rb_blend_factor`, `a3xx_rb_blend_opcode`, `adreno_compare_func`, `adreno_stencil_op`, `adreno_reg_xy`, `adreno_cp_protect`, `a3xx_regid`, `a3xx_threadmode`, `a3xx_threadsize`, `adreno_pa_su_sc_draw`, `a4xx_tess_spacing`, and `a3xx_render_mode`.

## Control Flow and Hardware Sequencing

The XML itself has no runtime control flow, but it models the register state required by the A4xx draw/dispatch pipeline:

- Command submission starts in CP state: ringbuffer base/control/read/write pointers, indirect buffers, microcode RAM address/data registers, scratch registers, protected register ranges, fault/status registers, and CP performance selectors.
- Tiling/binning state is coordinated through `RB_MODE_CONTROL`, `RB_RENDER_CONTROL`, `PC_BINNING_COMMAND`, `PC_BIN_BASE`, `VSC_BIN_SIZE`, VSC pipe configuration/address/length registers, and `RB_BIN_OFFSET`.
- Vertex input flows through `VFD_CONTROL_*`, `VFD_FETCH[32]`, and `VFD_DECODE[32]`, where fetch size, stride, instancing, register IDs, vertex formats, component masks, byte shifts, and switch-next bits configure the hardware vertex fetch/decode path.
- Shader state is split between SP and HLSQ. SP registers describe shader object starts, lengths, private-memory settings, register footprints, output mappings, MRT outputs, and stage-specific parameters. HLSQ registers describe thread mode, coord/face/sample register IDs, per-stage control, compute ND-range dimensions, workgroup constants, and update control.
- Rasterization and fragment output are configured through GRAS clipping, viewport, scissor, point, polygon offset, culling, depth/MSAA controls, then RB depth/stencil, MRT format/base/stride/blending, clear, copy/resolve, blend constants, alpha test, component masks, and sample count behavior.
- Texturing and memory-backed resources use TPL1 base/count registers plus the separate packed texture sampler/constant and SSBO domains. UCHE and VBIF registers provide cache, invalidate, trap, and bus performance/control integration.
- Performance monitoring is two-part: selector registers choose block-local countables, while `RBBM_PERFCTR_*_LO/HI` and VBIF counter low/high registers expose latched counter values.

## State and Persistence Behavior

The represented state is volatile GPU register state or command-stream state, not durable filesystem state. Register writes persist only until overwritten, reset, power collapse, context switch, or GPU reset. Important persistence boundaries include:

- CP ringbuffer, scratch, protect, microcode, and fault registers are device-global command processor state and must be initialized or restored by the kernel driver around GPU startup, reset, and protected execution setup.
- Per-draw and per-batch state such as MRTs, depth/stencil, blend constants, VFD fetch/decode records, SP/HLSQ stage controls, VPC varying layout, and GRAS/PC controls is normally emitted into command streams by the graphics driver and must be consistent with the active shader and framebuffer.
- Performance counter selector and value registers are shared hardware resources. The file provides selector encodings, but software must still serialize users, reset/load counters, and read low/high pairs coherently.
- Cache and memory-interface registers (`UCHE_INVALIDATE*`, `UCHE_CACHE_MODE_CONTROL`, VBIF limits/QOS/counters) affect memory visibility and throughput. Incorrect sequencing can produce stale reads, writeback hazards, or misleading measurements.
- Packed texture and SSBO domains describe persistent command-buffer records while a submitted command stream is executing; base address fields use shifted encodings and depend on external BO/GPU-address allocation.

## Dependencies and Integration Points

This file depends on the Freedreno XML schema and imported register definitions from `freedreno_copyright.xml`, `adreno/adreno_common.xml`, and `adreno/adreno_pm4.xml`. The generated output is expected to integrate with:

- MSM/Adreno kernel code that programs A4xx MMIO registers for boot, ringbuffer setup, interrupts, fault handling, power collapse, performance counters, and GPU reset recovery.
- Userspace Mesa/Freedreno code that emits A4xx draw/dispatch command streams using the same register names, format enums, texture constants, sampler constants, and shader-state encodings.
- Debugging and tracing tools such as register decoders, command-stream dumps, and performance counter utilities that rely on generated symbolic names and enum values.
- Shared A3xx/Adreno definitions for blend factors, compare funcs, stencil ops, register IDs, color swaps, surface endian, render modes, thread modes, draw primitive types, and CP protect register layout.

The file is a contract between reverse-engineered hardware behavior and generated C/header consumers. Any enum numeric change, bitfield shift, register offset, or array length change has direct ABI-like impact on all generated users.

## Risks and Maintenance Notes

Several definitions are intentionally reverse-engineered and partially uncertain. Comments flag guessed or weakly validated fields, including `RB_RENDER_CONTROL2` interpolation bits, `RB_MRT.BUF_INFO.COLOR_TILE_MODE`, `RB_MRT.CONTROL3.STRIDE`, `RB_FS_OUTPUT.SAMPLE_MASK`, `RB_COPY_CONTROL` bit widths, depth/stencil analogies to older generations, SP instruction-cache TODOs, `SP_FS_OUTPUT_REG.DEPTH_REGID`, `VFD_DECODE.CONSTFILL`, `GRAS_SC_CONTROL` bit widths, HLSQ control assumptions inherited from A3xx, and `A4XX_TEX_SAMP.LOD_BIAS` width.

Performance counter selectors also carry risk: comments say many A4xx countable numbers came from `AMD_performance_monitor` logs, while earlier A3xx values sometimes disagreed with the technical reference manual. Counters are useful test signals but should not be treated as authoritative without hardware validation.

The register map includes an explicit unknown block for offsets such as `UNKNOWN_0CC5`, `UNKNOWN_0D01`, `UNKNOWN_21C3`, `UNKNOWN_21E6`, `UNKNOWN_22D7`, and `UNKNOWN_2352`, many documented only by observed constant values. These may be required magic state, unused DX11-era features, or incomplete reverse engineering.

Address and stride fields frequently use `shr` encodings (`BASE`, `PITCH`, `GMEM_BASE`, `DEPTH_BASE`, `STENCIL_BASE`, texture/SSBO base/layer fields). Off-by-shift mistakes are high risk because they silently program wrong GPU addresses or pitches. Format enums also have sparse/reserved holes; conversion code must reject unsupported formats rather than assuming dense mappings.

There is a minor naming hygiene hazard: `RBBM_CLOCK_CTL_UCHE ` contains a trailing space in the XML `name` attribute. Generators or downstream code that do not normalize names could produce awkward or inconsistent identifiers.

## Test Signals and Validation Ideas

Useful validation signals for this file are mostly generated-code, decode, and hardware-behavior checks:

- XML/schema generation should succeed and produce stable register macros/enums for `A4XX`, `A4XX_TEX_SAMP`, `A4XX_TEX_CONST`, `A4XX_SSBO_0`, and `A4XX_SSBO_1`.
- Compile tests should catch missing imported types and invalid generated identifiers, especially around the trailing-space register name and inline bitsets.
- Command-stream decode tests should verify common draws exercise expected registers: MRT format/stride/base, depth/stencil state, blend constants, VFD fetch/decode state, SP/HLSQ shader controls, VPC varyings, GRAS scissor/viewport, and TPL1 texture counts.
- Hardware or trace replay tests should compare register dumps against known-good blob/Freedreno traces for binning, GMEM rendering, bypass rendering, MSAA resolves, depth/stencil clears, multiple render targets, instanced vertex fetch, sRGB formats, compressed textures, and compute dispatch.
- Performance counter tests should at least validate `CP_ALWAYS_COUNT`, RBBM always-on/busy counters, and representative RB/SP/TP/UCHE/VBIF selectors for monotonicity and plausible activity deltas under targeted workloads.
- Fault-path tests should decode `A4XX_INT0`, `RBBM_STATUS`, `CP_HW_FAULT`, `CP_PROTECT_STATUS`, and UCHE out-of-bounds signals after intentionally invalid command streams or protected-register writes.
