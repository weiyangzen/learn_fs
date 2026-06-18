# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 19586-22303

## Scope

This chunk covers a generated AMD GC 9.2.1 shader/register mask header range. It starts at `CB_COLOR2_BASE` and continues through complete color-buffer register families for MRTs 2-7, a large `gc_gfxudec` block of command processor and graphics pipeline state, performance counter data registers, UTCL2/VM L2 counter data registers, and the beginning of `gc_perfsdec` performance counter select registers. The range contains 2,104 `#define` macros and 604 register/comment anchors, all following the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` convention.

## Purpose

`gc_9_2_1_sh_mask.h` provides compile-time bit positions and masks for AMD GC 9.2.1 graphics registers. This slice is a hardware contract rather than executable C: it lets AMDGPU, power management, debug, and register-programming paths compose and decode 32-bit register values without duplicating literal bit positions.

The chunk focuses on three main domains:

- Color buffer render-target state for MRTs 2-7, including base addresses, metadata bases, view/mip fields, format fields, DCC/CMASK/FMASK controls, clear words, swizzle modes, sample/fragment counts, and render-target resource type/alignment flags.
- Command processor and graphics pipeline state in `gc_gfxudec`, including EOP fence/data addresses, streamout and pipeline statistics counters, scratch registers, CP atomic/preop addresses, CP DMA controls, coherency controls, indirect buffer metadata, draw/dispatch/index addresses, VGT/PA/SQ/SQC/GDS/SPI state, and thread trace controls.
- Performance observation state in `gc_perfddec`, `gc_utcl2_atcl2pfcntrdec`, `gc_utcl2_vml2prdec`, and the start of `gc_perfsdec`, including low/high counter readouts and select registers for CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, texture/cache, CB, DB, RLC, RMI, ATC L2, and VM L2 blocks.

## Important API Surface

- `CB_COLOR2_*` through `CB_COLOR7_*` define per-render-target color-buffer fields. Each MRT has `BASE`/`BASE_EXT`, `ATTRIB2`, `VIEW`, `INFO`, `ATTRIB`, `DCC_CONTROL`, `CMASK`, `CMASK_BASE_EXT`, `FMASK`, `FMASK_BASE_EXT`, `CLEAR_WORD0`, `CLEAR_WORD1`, `DCC_BASE`, and `DCC_BASE_EXT` masks. Important fields include `FORMAT`, `NUMBER_TYPE`, `COMP_SWAP`, `FAST_CLEAR`, `COMPRESSION`, `DCC_ENABLE`, `CMASK_ADDR_TYPE`, `COLOR_SW_MODE`, `FMASK_SW_MODE`, `RESOURCE_TYPE`, `RB_ALIGNED`, `PIPE_ALIGNED`, DCC block sizing, lossy precision, and constant encode control.
- `CP_EOP_*`, `CP_APPEND_*`, `CP_*FENCE*`, `CP_STREAM_OUT_*`, and `CP_PIPE_STATS_*` expose command processor memory addresses, fence values, event completion data, streamout counters, and pipeline-statistics buffers. These constants are paired with address-header offsets and PM4/MMIO programming paths.
- `SCRATCH_REG0` through `SCRATCH_REG7`, `SCRATCH_UMSK`, `SCRATCH_ADDR`, `CP_SCRATCH_INDEX`, and `CP_SCRATCH_DATA` describe CP scratch storage and indexed scratch access used by command streams and firmware-visible state.
- `CP_PFP_*`, `CP_ME_*`, `CP_ATOMIC_*`, and `CP_GDS_ATOMIC*` groups describe atomic pre-operation addresses/data, GDS atomics, memory-controller read/write address/data registers, semaphore wait/signaling addresses, and timeout controls.
- `CP_DMA_PFP_CONTROL`, `CP_DMA_ME_CONTROL`, `CP_DMA_*_SRC_ADDR`, `CP_DMA_*_DST_ADDR`, `CP_DMA_*_COMMAND`, `CP_DMA_CNTL`, and `CP_DMA_READ_TAGS` define DMA engine source/destination, command, cache policy, synchronization, and tag fields.
- `CP_COHER_*` and `CP_ME_COHER_*` define coherency range base/size/status/control fields. The masks cover operation modes, engine selection, TC/CB/DB actions, destination base selection, and status bits.
- `CP_PFP_IB_CONTROL`, `CP_PFP_LOAD_CONTROL`, `CP_IB*`, `CP_CE_IB*`, `CP_ST_*`, `CP_*_METADATA_BASE_ADDR*`, `CP_DRAW_INDX_INDR_ADDR*`, `CP_DISPATCH_INDR_ADDR*`, and `CP_INDEX_BASE_ADDR*` describe indirect buffer, CE buffer, state table, metadata, draw, dispatch, and index-buffer pointers.
- `GRBM_GFX_INDEX`, `VGT_*`, `WD_*`, and `IA_MULTI_VGT_PARAM` define broadcast/index selection, primitive/index types, streamout filled sizes, vertex index bounds, tessellation factor memory, offchip parameters, watchdog/input buffer bases, instance base, and multi-VGT dispatch behavior.
- `PA_*` groups define line stipple, stereo state, screen extents, and trap-screen coordinates/counts for scan-converter and setup logic.
- `SQ_THREAD_TRACE_*`, `SQC_CACHES`, and `SQC_WRITEBACK` define shader thread-trace buffer base/size/masks/status/high-water/counter/userdata fields plus shader cache invalidate/writeback controls.
- `TA_CS_BC_BASE_ADDR*`, `DB_OCCLUSION_COUNT*`, `DB_ZPASS_COUNT*`, and `GDS_*` define texture address fields, depth/occlusion counters, and global data share read/write/burst/atomic/GWS/OA controls.
- `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_CNTL_2`, and `SPI_WAVE_LIMIT_CNTL` expose shader processor input/launch/wave-limit configuration fields.
- `*_PERFCOUNTER*_LO` and `*_PERFCOUNTER*_HI` macros in `gc_perfddec` expose counter readback halves. Most are full-width 32-bit low/high fields, while ATC L2 and VM L2 high registers split `COUNTER_HI` from `COMPARE_VALUE`.
- `CPG_PERFCOUNTER*_SELECT` and `CPC_PERFCOUNTER*_SELECT*` at the end define event selector and counter mode fields used to configure performance counters. The chunk ends inside `CPC_PERFCOUNTER0_SELECT1`, so later masks for that register are completed in the next chunk.

There are no C functions, structs, or enums in this slice. The public surface is the preprocessor namespace of generated mask and shift constants.

## Control Flow

This header has no runtime control flow. Consumer flow is table-driven or helper-driven:

1. Select a GC 9.2.1 register offset from `gc_9_2_1_offset.h` or related SOC15 address helpers.
2. Compose field values by shifting with `REGISTER__FIELD__SHIFT`.
3. Mask or update fields with `REGISTER__FIELD_MASK`.
4. Emit the value through MMIO, PM4 packets, golden-register programming, clear-state programming, power-management initialization, debug register decode, or performance counter setup.

The repeated register families imply indexed consumer behavior. Color-buffer setup iterates MRT slots 2-7 in this chunk; streamout/pipeline-statistics code iterates counter slots; performance tooling iterates per-block counter pairs; and shader/thread-trace code programs base/size/mask/status registers as a coordinated sequence.

## State and Persistence

The macros themselves are stateless build artifacts, but they describe persistent GPU register state. Programmed values remain active until overwritten by a command stream, context switch/restore, golden-register sequence, power transition, mode reset, or GPU reset.

Persistent state described here includes:

- Render-target storage and metadata layout. `CB_COLORn_BASE`, `*_BASE_EXT`, `CMASK`, `FMASK`, `DCC_BASE`, and related control fields bind GPU memory ranges and compression metadata for MRTs 2-7.
- Command processor synchronization state. EOP addresses, fence words, semaphore addresses, append fences, scratch registers, and wait-timeout fields persist across command streams according to CP ownership rules.
- DMA and coherency state. `CP_DMA_*` and `CP_COHER_*` fields control GPU memory copies, cache actions, and coherency ranges; bad persistence can affect later command streams beyond the immediately emitted packet.
- Draw and dispatch pointer state. Indirect draw/dispatch addresses, index base/type, IB state, CE state, state table bases, and metadata bases must match command buffer layout and GPU virtual address mappings.
- Shader and graphics pipeline debug state. Thread trace buffers, SQC cache controls, trap-screen controls, and SPI config fields affect debugging, tracing, shader launch, and cache behavior.
- Counter state. Performance counter selectors, low/high readout registers, pipeline statistics counters, occlusion counters, z-pass counters, and GDS OA/GWS registers expose accumulated hardware state and must be sampled/reset in the correct order.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.2.1 register specification and must stay synchronized with `drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h`.
- Included by Vega12/GC 9.2.1 integration paths such as `pm/powerplay/hwmgr/vega12_inc.h`, `amdgpu/gfxhub_v1_1.c`, and GC 9.2.1 paths in `amdgpu/gfx_v9_0.c`.
- Integrates with SOC15 register access helpers, PM4 packet emission, clear-state tables, golden-register tables, perf counter setup/readback, RLC/CP firmware-facing state, and debug register dump/decode tooling.
- Higher-level graphics state from Mesa/Vulkan/OpenGL ultimately maps into the CB, VGT, PA, SPI, SQ, DB, and CP fields documented here, while memory management provides the GPU virtual addresses split into low/high/base-extension fields.
- Uses plain C preprocessor constants only. The header cannot validate field ranges, address alignment, GPU generation compatibility, counter selector legality, or ordering requirements around cache/coherency operations.

## Risks

- Bitfield drift is the main risk. If a mask/shift differs from the GC 9.2.1 hardware definition or matching offset header, drivers silently write the wrong bits.
- This chunk has boundary partials. It begins immediately after `CB_COLOR1_DCC_BASE_EXT`, so MRTs 0-1 are documented in earlier chunks, and it ends inside `CPC_PERFCOUNTER0_SELECT1`, with remaining masks in the next chunk.
- Render-target address and compression fields have high blast radius. Incorrect `CB_COLORn_*` base, extension, CMASK/FMASK/DCC, swizzle, sample, fragment, or DCC control fields can corrupt render targets, metadata, or unrelated GPU memory.
- CP DMA, coherency, semaphore, atomic, and fence fields are synchronization-sensitive. Wrong values can create stale caches, lost fences, memory corruption, hangs, or timeouts that are difficult to attribute to the original bitfield.
- Pointer fields for IBs, CE buffers, state tables, draw/dispatch indirect buffers, index buffers, thread trace buffers, and GDS/OA state require alignment and GPU VM validity that this header does not enforce.
- Performance counter registers are block-specific. Reusing a selector or readout mask across CP/GRBM/IA/VGT/PA/SPI/SQ/cache/CB/DB/RLC/RMI/UTCL2 blocks can produce plausible but wrong measurements.
- Generated macro names are very broad and untyped. Copy/paste mistakes between repeated `CB_COLORn`, `CP_DMA_ME`/`CP_DMA_PFP`, `*_PERFCOUNTERn_LO/HI`, and `*_SELECT` families will compile cleanly.

## Test Signals

- Build coverage catches syntax errors, duplicate definitions, missing include guards, and broken includes in AMDGPU and power-management paths that include `gc_9_2_1_sh_mask.h`.
- Generator/spec diffing should compare this line range against the GC 9.2.1 register database and `gc_9_2_1_offset.h`, verifying each field width, shift, mask, and register family index.
- Render tests should exercise MRTs 2-7, format/number-type/comp-swap combinations, fast clears, DCC/CMASK/FMASK metadata, MSAA sample/fragment settings, mips/slices, and multi-render-target blending to detect CB field regressions.
- Command processor smoke tests should cover EOP fences, semaphores, scratch registers, CP DMA copies, indirect draw/dispatch, index buffers, streamout, pipeline statistics, coherency operations, and append/atomic paths.
- Performance tooling tests should program and sample CPG/CPC/CPF/GRBM/WD/IA/VGT/PA/SPI/SQ/SX/GDS/TA/TD/TCP/TCC/TCA/CB/DB/RLC/RMI/ATC L2/VM L2 counters and verify stable low/high read sequencing and selector behavior.
- Debug/tracing tests should validate SQ thread trace buffer programming, SQC invalidate/writeback behavior, SPI wave limits, and register-dump decode output against known-good traces.
- Runtime failure signals include GPU hangs, VM faults, corrupted render targets, missing primitives, stale data after DMA/coherency operations, invalid performance readings, and golden-register warnings on Vega12/GC 9.2.1 hardware.
