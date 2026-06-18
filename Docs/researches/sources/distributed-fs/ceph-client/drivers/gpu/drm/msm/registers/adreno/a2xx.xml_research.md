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
