# subset-b-003657 research

Grouped research for Adreno a2xx/a3xx Freedreno register database XML files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a2xx.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a2xx.xml

## Purpose
Defines the Freedreno register database for Qualcomm Adreno A2xx-family GPUs. The file is declarative XML, not executable C: it describes register offsets, bitfields, bitsets, arrays, value enums, and state-object layouts that `drivers/gpu/drm/msm/registers/gen_header.py` converts into `generated/a2xx.xml.h`. The generated header is included by A2xx driver code such as `adreno/a2xx_gpu.h`, `adreno/a2xx_gpu.c`, and `adreno/a2xx_gpummu.c` so C code can use symbolic `REG_A2XX_*` register IDs and `A2XX_*` bit masks instead of open-coded numeric offsets.

The file covers both normal MMIO registers in the `A2XX` domain and texture-state dwords in the `A2XX_SQ_TEX` domain. It provides the binding contract between the command stream, GPU setup code, crash/perf diagnostics, and the hardware register layout for older Yamato/Adreno 2xx hardware.

## Important APIs, types, and functions
- Imports: `freedreno_copyright.xml`, `adreno/adreno_common.xml`, and `adreno/adreno_pm4.xml`. These supply shared copyright metadata and common Adreno enum/bitset types such as compare functions, blend factors, surface endian definitions, stencil fields, draw initiator layouts, and PM4 packet definitions.
- Top-level format/state enums: `a2xx_colorformatx`, `a2xx_sq_surfaceformat`, texture clamp/filter/sign/endian/dimension enums, RB dither/blend/copy mode enums, PA clip/polygon/pixel-center/round/quantization enums, and `perf_mode_cnt`.
- Performance-counter selector enums: `a2xx_su_perfcnt_select`, `a2xx_sc_perfcnt_select`, `a2xx_vgt_perfcount_select`, `a2xx_tcr_perfcount_select`, `a2xx_tp_perfcount_select`, `a2xx_tcm_perfcount_select`, `a2xx_tcf_perfcount_select`, `a2xx_sq_perfcnt_select`, `a2xx_sx_perfcnt_select`, `a2xx_rbbm_perfcount1_sel`, `a2xx_cp_perfcount_sel`, `a2xx_rb_perfcnt_select`, and `a2xx_mh_perfcnt_select`.
- Main domain: `<domain name="A2XX" width="32">` emits register constants and masks for 32-bit A2xx MMIO/register-file accesses.
- Inline bitsets: `a2xx_vgt_current_bin_id_min_max` and the local `adreno_mmu_clnt_beh` enum define packed helper layouts used by multiple registers.
- Register arrays: `VSC_PIPE` describes eight visibility-stream pipe triplets, and large contiguous state regions such as `SQ_CONSTANT_0`, `SQ_FETCH_0`, `SQ_CF_BOOLEANS`, and `SQ_CF_LOOP` anchor shader state spaces.
- Texture domain: `<domain name="A2XX_SQ_TEX" width="32">` defines the six dwords of an A2xx texture fetch constant, including format, base/mip addresses, pitch, dimensions, swizzle, filtering, LOD, anisotropy, border color, and tiling bits.

## Control flow
There is no runtime control flow in this XML file. Its effective flow is build-time data flow:

1. The msm Makefile matches `registers/adreno/a2xx.xml` with the `generated/%.xml.h` rule.
2. `registers/gen_header.py` parses this XML plus imported databases, optionally validates against `rules-fd.xsd`, and emits C defines/structures into `generated/a2xx.xml.h`.
3. A2xx C code includes the generated header and passes emitted register IDs to `gpu_write()`, `gpu_read()`, ringbuffer packet builders, MMU setup, IRQ handling, reset paths, and debug dumps.
4. Command-stream code can refer to register offsets such as `REG_A2XX_RB_SURFACE_INFO` relative to packet-specific register windows, while MMIO code uses the same generated symbolic register names for direct reads/writes.

Within the XML itself, declarations are ordered from common value spaces to concrete domains. Enums are defined before registers that reference them. The `A2XX` domain starts with RBBM/CP/MMU control, continues through RBBM status/interrupt/performance registers, memory hub configuration, visibility stream setup, shader core debug/state setup, render backend state, draw/viewport/rasterizer state, copy/clear state, and finally performance counter register banks. The `A2XX_SQ_TEX` domain then describes per-texture constant dwords.

## State and persistence behavior
The XML does not persist state at runtime, but the generated definitions describe persistent GPU state programmed by the kernel and command streams. Registers such as `MH_MMU_CONFIG`, `MH_MMU_PT_BASE`, `MH_MMU_INVALIDATE`, `RBBM_PM_OVERRIDE*`, `RBBM_INT_*`, `RBBM_STATUS`, `SQ_PROGRAM_CNTL`, `RB_COLOR_INFO`, `RB_DEPTH_INFO`, `RB_DEPTHCONTROL`, `RB_BLEND_CONTROL`, and `PA_SU_SC_MODE_CNTL` map directly to state that remains in the GPU until reset or reprogramming.

The `A2XX_SQ_TEX` domain describes state objects stored in command buffers or GPU-visible state memory rather than simple MMIO registers. Base-address fields use shifts such as `shr="12"` for page-aligned texture/mipmap pointers, and pitch fields use shifts such as `shr="5"` to express hardware alignment. Those annotations become generated helpers/macros and are part of the ABI between driver state emission and hardware interpretation.

## Dependencies and integration points
- Build integration is through `drivers/gpu/drm/msm/Makefile`, which lists `generated/a2xx.xml.h` and declares dependencies on this XML, common Adreno XML, PM4 XML, copyright XML, `gen_header.py`, and `rules-fd.xsd`.
- Parser integration is through `registers/gen_header.py`, which understands `database`, `import`, `domain`, `enum`, `value`, `reg32`, `bitfield`, `bitset`, `array`, `doc`, numeric offsets, shifts, signed/fixed/float types, and generated C names.
- Driver integration includes `a2xx_gpu.c` for initialization, reset, idle checks, ringbuffer emission, and debug dumps; `a2xx_gpummu.c` for GPUMMU page table base/range programming and `MH_MMU_INVALIDATE`; and shared Adreno helpers that branch on `adreno_is_a2xx()`.
- Shared type dependencies include `adreno_reg_xy`, `adreno_rb_depth_format`, `adreno_rb_surface_endian`, `adreno_compare_func`, `adreno_stencil_op`, `adreno_rb_blend_factor`, `adreno_rb_dither_mode`, `adreno_pa_su_sc_draw`, `adreno_rb_stencilrefmask`, and `vgt_draw_initiator`.
- Hardware integration is broad: RBBM, CP, MH/MMU, VSC, PA/GRAS, SQ, TC/TCR/TCM/TCF, TP/TPC, SX, RB, VGT, and performance-monitor blocks all consume definitions from this file.

## Risks
- Register offsets and bitfield widths are hardware ABI. A wrong value can silently misprogram the GPU, break command submission, mask real interrupts, corrupt render targets, or make recovery/debug reads misleading.
- Some comments document uncertainty, for example the A2xx-only nature of `MH_MMU_CONFIG` at offset `0x0040` and the uncertain width of `CP_PERFMON_CNTL.PERF_MODE_CNT`. These should be treated as hardware-reverse-engineering risk areas.
- Several registers have aliases or generation-specific names at the same offset, such as `GRAS_DEBUG_CNTL` and `PA_SU_DEBUG_CNTL`, and A220/A225-specific registers mixed into the common A2xx domain. Consumers must know which GPU subgeneration supports which names.
- Address and pitch shifts (`shr`) must match the C code's alignment and memory layout assumptions. Incorrect shifts in generated macros can cause bad base addresses for render targets, depth buffers, copies, textures, or shader state.
- Performance-counter enums are large and sparsely valued. Incorrect selectors may not affect normal rendering but can break profiling, busy accounting, debugfs/perf tooling, or crash diagnostics.
- The XML depends on imported common enums. Renaming or changing shared enum values can change generated names used by old A2xx code.

## Test signals
- Build: `generated/a2xx.xml.h` is regenerated without parser/schema errors, and C files including `a2xx.xml.h` compile without missing `REG_A2XX_*` or `A2XX_*` symbols.
- Smoke runtime: A2xx initialization writes RBBM power/reset, MMU, CP microcode, interrupt, and render-state registers without register access faults; `a2xx_idle()` observes `RBBM_STATUS` busy bits clearing.
- MMU tests: `a2xx_gpummu_map()` and `a2xx_gpummu_unmap()` can program page-table entries and use `REG_A2XX_MH_MMU_INVALIDATE` with `INVALIDATE_ALL` and `INVALIDATE_TC` successfully.
- Command submission: ringbuffer register packets using generated offsets for RB, PA, SQ, VGT, and copy state render simple geometry, clears, depth/stencil, blending, and textured draws.
- Diagnostics: debug dumps and IRQ handling report meaningful `RBBM_STATUS`, `RBBM_INT_STATUS`, `MASTER_INT_SIGNAL`, `MH_INTERRUPT_STATUS`, and selected perf counters.
- Regression checks should include subgeneration-specific A220/A225 paths, GMEM/binning state through `VSC_PIPE`, shader constant/fetch state, texture formats/swizzles, and boundary alignment for shifted base/pitch fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a2xx.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a3xx.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a3xx.xml

## Purpose
Defines the Freedreno register database for Qualcomm Adreno A3xx-family GPUs. Like the A2xx database, it is declarative XML consumed by `registers/gen_header.py` to generate `generated/a3xx.xml.h`. The generated header is included by `adreno/a3xx_gpu.h` and used heavily by `adreno/a3xx_gpu.c` for hardware initialization, command submission, interrupt handling, register protection, crash-state capture, performance counters, busy accounting, and reset recovery.

The file models the A3xx pipeline more explicitly than the A2xx file. The main `A3XX` domain includes RBBM, CP, GRAS, RB, PC, HLSQ, VFD, VPC, SP, TPL1, VBIF, VSC, UCHE, TP, and perf-counter blocks. Separate domains describe texture sampler state and texture constant state, which are emitted into command streams or state blocks rather than accessed only as MMIO registers.

## Important APIs, types, and functions
- Imports: `freedreno_copyright.xml`, `adreno/adreno_common.xml`, and `adreno/adreno_pm4.xml`, which supply shared Adreno enums and PM4 packet definitions used by A3xx registers and command submission.
- Format/layout enums: `a3xx_tile_mode`, `a3xx_state_block_id`, `a3xx_cache_opcode`, `a3xx_vtx_fmt`, `a3xx_tex_fmt`, `a3xx_color_fmt`, `a3xx_intp_mode`, and `a3xx_repl_mode`.
- Performance-counter selector enums: `a3xx_cp_perfcounter_select`, `a3xx_gras_tse_perfcounter_select`, `a3xx_gras_ras_perfcounter_select`, `a3xx_hlsq_perfcounter_select`, `a3xx_pc_perfcounter_select`, `a3xx_rb_perfcounter_select`, `a3xx_rbbm_perfcounter_select`, `a3xx_sp_perfcounter_select`, `a3xx_tp_perfcounter_select`, `a3xx_vfd_perfcounter_select`, `a3xx_vpc_perfcounter_select`, and `a3xx_uche_perfcounter_select`.
- Main interrupt bitset: `A3XX_INT0`, used as the type for `RBBM_INT_SET_CMD`, `RBBM_INT_CLEAR_CMD`, `RBBM_INT_0_MASK`, and `RBBM_INT_0_STATUS`. C code composes `A3XX_INT0_MASK` from generated interrupt bits.
- Main domain: `<domain name="A3XX" width="32">` defines 32-bit register constants and masks for hardware blocks.
- Register arrays: `CP_PROTECT`, `RB_MRT`, `HLSQ_CL_GLOBAL_WORK`, `HLSQ_CL_KERNEL_GROUP`, `VFD_FETCH`, `VFD_DECODE`, `VPC_VARYING_INTERP`, `VPC_VARYING_PS_REPL`, `SP_VS_OUT`, `SP_VS_VPC_DST`, `SP_FS_MRT`, `SP_FS_IMAGE_OUTPUT`, `VSC_PIPE`, and `GRAS_CL_USER_PLANE`.
- Inline bitsets: `a3xx_hlsq_vs_fs_control_reg`, `a3xx_hlsq_const_vs_fs_presv_range_reg`, `a3xx_vs_fs_length_reg`, `sp_vs_fs_obj_offset_reg`, `a3xx_tpl1_tp_vs_fs_tex_offset`, and `a3xx_vbif_perf_cnt`.
- Texture domains: `A3XX_TEX_SAMP` describes two sampler dwords with filtering, wrap, compare, anisotropy, normalized-coordinate, and LOD fields; `A3XX_TEX_CONST` describes four texture-constant dwords with tiling, swizzle, mip levels, MSAA, format, texture type, dimensions, pitch, mipmap-state index, swap, depth, and layer-size fields.

## Control flow
There is no runtime branching in this XML file. The operational flow is:

1. The msm Makefile selects the `generated/%.xml.h` rule for `registers/adreno/a3xx.xml`.
2. `gen_header.py` parses this file and its imports, validates if requested, and emits C register offsets, masks, enum values, and helper macros into `generated/a3xx.xml.h`.
3. `a3xx_gpu.c` and related headers use the generated constants to program hardware in init, submit, IRQ, recovery, state capture, and performance paths.
4. Command-stream helpers and `gpu_write()`/`gpu_read()` callers rely on the generated names to keep register programming synchronized with the XML hardware database.

The XML declaration order mirrors hardware bring-up and render state. It starts with format and counter selector enums, then defines RBBM hardware identity, busy/status, wait-idle, interrupt, and top-level perf registers. CP microcode, ROQ/MEQ, protection, and fault registers follow. The graphics pipeline state then proceeds through GRAS clip/raster state, RB render/depth/stencil/copy state, PC binning and primitive state, HLSQ shader/thread/compute state, VFD vertex fetch/decode state, VPC varying interpolation/replacement state, SP vertex/fragment shader object and output state, TPL1 texture table pointers, VBIF memory-interface QoS/perf state, VSC binning, UCHE cache controls, and block-specific perf selectors. Texture sampler and texture constant domains are defined after the main register domain.

## State and persistence behavior
The file itself persists no runtime state, but the generated header defines persistent GPU state programmed by kernel init code and command buffers. Key persistent state includes:

- RBBM status, clock, wait-idle, hang-detect, interrupt, and performance-counter control.
- CP microcode loading, hardware fault, AHB fault, and `CP_PROTECT` register access protection ranges.
- RB render mode, GMEM bypass/based addresses, MRT color buffers, blend controls, copy resolve state, depth/stencil formats, pitches, clear values, and sample count state.
- GRAS clipping, viewport, scissor, polygon offset, culling, raster mode, and user clip planes.
- HLSQ, VFD, VPC, and SP shader interface state, including register IDs, shader lengths, constant ranges, interpolation modes, varying destinations, private memory parameters, shader object starts, and compute NDRANGE/group registers.
- VBIF and UCHE memory-system controls and performance counters.
- Texture sampler and texture constant state objects, which persist in emitted state blocks until replaced by later command stream state.

Shift annotations on address and pitch fields are part of the persistence contract. Examples include GMEM and system-memory base fields in RB copy/MRT/depth/stencil state, texture layer sizes and pitches, and shader private memory object addresses.

## Dependencies and integration points
- Build integration is through `drivers/gpu/drm/msm/Makefile`, which generates `generated/a3xx.xml.h` from this file plus shared Adreno XML files, `gen_header.py`, and `rules-fd.xsd`.
- Parser integration relies on `gen_header.py` support for XML imports, domains, arrays, inline bitsets, docs, shifted fields, typed bitfields, and generated C symbol naming.
- C driver integration is direct in `a3xx_gpu.c`: `A3XX_INT0_*` bits build the interrupt mask; `REG_A3XX_VBIF_*`, `REG_A3XX_RBBM_*`, `REG_A3XX_UCHE_*`, `REG_A3XX_CP_PROTECT*`, and `REG_A3XX_CP_PFP_UCODE_*` are used during hardware init; `REG_A3XX_RBBM_STATUS` is used for idle/recovery/state capture; `REG_A3XX_RBBM_PERFCTR_RBBM_1_LO` is used for busy cycles; and SP counter registers are exposed through performance-counter plumbing.
- Command submission uses A3xx register definitions through PM4 packets and state-block programming. The XML includes `VGT_DRAW_INITIATOR` and `VGT_IMMED_DATA` compatibility with shared draw initiator definitions.
- Hardware integration spans A3xx variants in `a3xx_catalog.c`; init code selects variant-specific VBIF/clock/cache/protection values but relies on one generated A3xx register map.

## Risks
- Register and bitfield definitions are hardware ABI. Incorrect offsets, enum values, or masks can break GPU initialization, leave interrupts unmasked, damage render/depth state, or make CP register protection too permissive or too restrictive.
- The file contains explicit reverse-engineering uncertainty in comments, including guessed bit widths, guessed register names such as PC versus VGT bin registers, unknown always-written registers, uncertain cache opcode widths, and possible differences between fields such as texture layer sizes. Those are high-risk when refactoring generated definitions.
- CP protection definitions are security and stability sensitive. If generated `REG_A3XX_CP_PROTECT(n)` values drift, userspace command streams may gain access to registers that should remain protected or lose access to safe ranges required by Mesa.
- Format enums are shared with userspace expectations through driver command emission. Missing or incorrect texture/color/vertex formats can produce rendering corruption that only appears under specific GL/Vulkan formats, compressed textures, NV12/I420 paths, or integer/normalized/float combinations.
- Address and pitch shifts must match GMEM, system-memory, texture, shader object, and private-memory alignment rules. Wrong shifts can cause out-of-bounds memory access or hard-to-debug GPU faults.
- Performance-counter selectors are numerous and block-specific. Mistakes may only surface in perf tools, devcoredump analysis, or busy-time accounting rather than in normal rendering.

## Test signals
- Build: `generated/a3xx.xml.h` regenerates cleanly, schema validation passes when `lxml` is available, and A3xx C files compile with all referenced `REG_A3XX_*`, `A3XX_*`, enum, and bit mask symbols.
- Hardware initialization: A3xx probe/init writes VBIF, RBBM, UCHE, CP protection, interrupt mask, PFP microcode, and GMEM base registers without faults, and `a3xx_idle()` observes `A3XX_RBBM_STATUS_GPU_BUSY` clearing.
- IRQ/recovery: generated `A3XX_INT0_*` masks correctly handle CP opcode/reserved-bit/hw-fault, CP IB/ringbuffer events, cache flush timestamps, UCHE OOB, and AHB/reg-timeout paths; reset via `RBBM_SW_RESET_CMD` recovers from injected hangs.
- Rendering coverage: simple clear, draw, blend, depth/stencil, MSAA resolve, GMEM bypass/GMEM render pass, binning, primitive restart, point size, flat/smooth interpolation, and MRT cases program the expected RB/GRAS/PC/HLSQ/VFD/VPC/SP fields.
- Texture coverage: sampler wrap/filter/LOD/compare/aniso and texture constant format/swizzle/tile/pitch/mipmap/layer fields work for uncompressed, compressed, YUV, integer, normalized, float, cube, 3D, and MSAA textures.
- Diagnostics/perf: devcoredump and debug logs show meaningful RBBM status/fault registers, busy-cycle sampling reads the intended RBBM perf counter pair, and block-specific performance counters select valid CP/GRAS/HLSQ/PC/RB/RBBM/SP/TP/VFD/VPC/UCHE events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a3xx.xml -->
