# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 2406-4820

## Purpose

This chunk is generated-style register metadata for the AMD GC 9.2.1 graphics core. It defines bit shifts and masks for fields in shader, cache, texture, global-data-share, depth-buffer, render-backend, and graphics-backend registers. The definitions are compile-time constants only; they let AMDGPU code use symbolic names with register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15 register accessors instead of embedding raw bit positions.

The range starts in the tail of `SQC_DSM_CNTL2B`, then covers a large `SQ` region for shader instruction encodings, indirect wave access, thread trace token layouts, buffer/image/sampler resource descriptors, flat scratch setup, and SQC instruction/data cache UTCL1 controls. It then crosses address-block boundaries into `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, and `gc_rbdec`, ending partway through graphics backend tile-mode definitions at `GB_TILE_MODE10`.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or storage declarations in this range. The API surface is the macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field's low-bit position.
- `REGISTER__FIELD_MASK` gives the field's unshifted 32-bit mask.
- Full-width fields such as `SQ_IND_DATA__DATA_MASK`, `SQ_TIME_HI__TIME_MASK`, `SQ_TIME_LO__TIME_MASK`, `SQ_BUF_RSRC_WORD0__BASE_ADDRESS_MASK`, and `SQ_IMG_RSRC_WORD7__META_DATA_ADDRESS_MASK` expose entire register words.
- Address-block comments such as `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, and `gc_rbdec` mark hardware decode domains, not C namespaces.

Important groups in this chunk include:

- Shader queue control and instruction encodings: `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_CMD`, `SQ_DS_*`, `SQ_EXP_*`, `SQ_FLAT_*`, `SQ_GLBL_*`, `SQ_MIMG_*`, `SQ_MTBUF_*`, `SQ_MUBUF_*`, `SQ_SCRATCH_*`, `SQ_SMEM_*`, `SQ_SOP*`, `SQ_VINTRP`, `SQ_VOP*`, `SQ_VOP_DPP`, and `SQ_VOP_SDWA`. These describe bit layouts for wave/register access and instruction words.
- Thread-trace token formats: `SQ_THREAD_TRACE_WORD_*` macros identify token type, time delta, shader/CU/SIMD/wave IDs, PC fragments, userdata fragments, issue slots, performance counters, register write records, timestamps, and wave-start metadata.
- Shader resource descriptors: `SQ_BUF_RSRC_WORD0..3`, `SQ_IMG_RSRC_WORD0..7`, `SQ_IMG_SAMP_WORD0..3`, `SQ_FLAT_SCRATCH_WORD0..1`, and `SQ_M0_GPR_IDX_WORD` define descriptor fields used by shader memory/image/sampler operations.
- SQC UTCL1 controls and status: `SQC_ICACHE_UTCL1_CNTL1/2`, `SQC_DCACHE_UTCL1_CNTL1/2`, and matching status registers define GPUVM page-size behavior, response/fault modes, VMID invalidation, force-miss/in-order controls, snooping, performance-event selection, FIFO/cache-size reduction, and fault/retry/PRT status bits.
- SH/SPI controls: `SX_DEBUG_1`, `SPI_PS_MAX_WAVE_ID`, `SPI_START_PHASE`, `SPI_GFX_CNTL`, `SPI_DSM_CNTL*`, `SPI_DEBUG_BUSY`, `SPI_CONFIG_PS_CU_EN`, wave lifetime limit/status arrays, load-balance counter selectors/data, trap-screen fields, GDS credits, export/scoreboard buffer sizes, and compute-shader queue wave-active counters.
- Texture and address blocks: `TD_CNTL`, `TD_STATUS`, `TA_CNTL`, `TA_CNTL_AUX`, and `TA_STATUS` define texture-data/address behavior, performance/determinism toggles, FIFO state, and busy bits.
- GDS controls: `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_PROTECTION_FAULT`, `GDS_VM_PROTECTION_FAULT`, `GDS_DSM_CNTL*`, and `GDS_WD_GDS_CSB` describe shared-data-store phases, busy/conflict flags, fault identity, VM fault identity, and error-injection controls.
- DB/RB/GB controls: `DB_DEBUG*`, `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_SUBTILE_CONTROL`, FIFO/cacheline depths, exception/ring controls, RMI cache policy, DFSM watchdog/flush controls, `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `CC_RB_DAISY_CHAIN`, `GB_ADDR_CONFIG_READ`, and `GB_TILE_MODE0..10`.

## Control Flow

This header chunk has no runtime control flow. Its effect is purely through preprocessing: including files compile the constants into register read-modify-write expressions, golden-setting tables, debug paths, and field extraction logic.

Typical runtime control flow in consumers is:

1. Select GC 9.2.1-specific offset and mask headers through the ASIC include tree.
2. Read or write a 32-bit hardware register via SOC15 helpers.
3. Use the generated `__SHIFT`/`_MASK` pair, often through AMDGPU field macros, to isolate or construct a field value.

Examples visible in the tree include `gfxhub_v1_1.c`, which directly includes `gc_9_2_1_offset.h` and `gc_9_2_1_sh_mask.h` for GC register field extraction, and `vega12_inc.h`, which exposes the same header set to Vega12 PowerPlay code. `gfx_v9_0.c` also has GC 9.2.1 golden settings that program registers covered by this range, including `DB_DEBUG2`, `GB_GPU_ID`, `TA_CNTL_AUX`, and, in the Vega12 variant, `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_READ`, and `TD_CNTL`.

## State And Persistence Behavior

The macros themselves are stateless and do not persist data. The state they describe lives in GPU hardware registers and descriptor words.

Several hardware-state categories are represented:

- Volatile command/debug state: `SQ_CMD`, `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_REG_TIMESTAMP`, `SQ_CMD_TIMESTAMP`, and `SQ_TIME_*` are used around wave inspection, timestamping, and command/debug operations.
- Persistent-until-reset configuration: `SQC_*_CNTL*`, `SPI_*`, `TD_CNTL`, `TA_CNTL*`, `GDS_CONFIG`, `DB_*`, `GB_ADDR_CONFIG`, and `GB_TILE_MODE*` fields affect hardware behavior until overwritten by driver initialization, power-management sequences, reset, or GPU power transitions.
- Read-only or status-like observation: `SQC_*_STATUS`, `SPI_DEBUG_BUSY`, `SPI_WF_LIFETIME_STATUS_*`, `TA_STATUS`, `GDS_CNTL_STATUS`, `GDS_*_PROTECTION_FAULT`, `DB_DFSM_*_IN_FLIGHT`, and `GB_ADDR_CONFIG_READ` represent hardware-reported condition or snapshot fields.
- Error-injection and DSM controls: `SQC_DSM_CNTL2B`, `SPI_DSM_CNTL*`, `TD_DSM_CNTL*`, and `GDS_DSM_CNTL*` can intentionally alter memory/RAM paths for design-for-test or validation. Those are not ordinary production tuning fields.

No disk state, kernel heap persistence, locks, or reference-counted resources are implemented here. Persistence concerns are entirely about whether consuming code writes destructive or sticky hardware fields and whether reset/suspend/resume paths reprogram them.

## Dependencies

This chunk depends on the rest of the generated GC 9.2.1 register family:

- `gc_9_2_1_offset.h` supplies the matching register offsets.
- Other `gc_9_2_1_*` generated headers provide defaults and adjacent register definitions outside this line range.
- AMDGPU SOC15 helpers and field macros provide the C-level operators that combine these shifts and masks with register reads/writes.
- Generation-specific driver files such as `gfx_v9_0.c`, `gfxhub_v1_1.c`, and Vega12 PowerPlay includes depend on the GC 9.2.1 names matching the target ASIC.

The definitions are hardware-contract data. They must stay synchronized with the GC 9.2.1 register specification and with sibling generated headers. Similar names exist across GC 9.x, 10.x, 11.x, and 12.x, but field layouts differ; cross-generation reuse is unsafe unless the exact register layout has been checked.

## Integration Points

Primary integration points are:

- Wave/register debug paths that build `SQ_IND_INDEX` values using wave, SIMD, thread, index, force-read, and auto-increment fields before reading `SQ_IND_DATA`.
- Shader and trace tooling that decodes `SQ_THREAD_TRACE_WORD_*` tokens or constructs shader resource descriptors using the `SQ_*_RSRC_WORD*` and `SQ_IMG_SAMP_WORD*` masks.
- MMU/cache handling that invalidates SQC instruction/data UTCL1 state by VMID, checks fault/retry/PRT status, or forces ordering/miss behavior during diagnostics.
- Golden settings and ASIC initialization paths that program `TD_CNTL`, `TA_CNTL_AUX`, `DB_DEBUG2`, `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_READ`, and `GB_GPU_ID`.
- Power-management and validation code exposed through `vega12_inc.h`, where GC masks are available alongside thermal, MP, and NBIO register definitions.
- Render/depth backend setup and debugging through DB, RB, and GB fields, including backend disable/redundancy, address configuration, backend maps, and tile-mode layouts.

## Risks

- A wrong shift or mask silently targets the wrong hardware bits. In this kind of header, that can cause incorrect wave debug reads, bad shader descriptor decoding, cache invalidation failures, texture/addressing bugs, or render-backend misconfiguration.
- The range mixes normal runtime tuning fields with debug and error-injection fields. Accidentally enabling DSM injection, force-miss, compression disables, or debug bypasses can create severe performance or correctness regressions.
- Several fields are status or sticky fault indicators. Consumers must understand clear-on-write, reset, or destructive-read behavior from the hardware spec before adding writes around them.
- `GB_ADDR_CONFIG` and `GB_TILE_MODE*` fields encode memory tiling/topology. Incorrect values can break surface layout interpretation across the graphics pipeline.
- `SQ_THREAD_TRACE_WORD_*` token masks include 16-bit and 32-bit layouts. Trace decoders must handle multi-word tokens, high/low fragments, and field width differences without assuming every token is a full 32-bit flat record.
- Cross-generation macro names are deceptively similar. For example, later GC generations add or move fields in `SQ_IND_INDEX`, `SPI_DEBUG_BUSY`, `DB_DEBUG`, and backend address configuration. Including the wrong ASIC header can compile cleanly but misprogram hardware.
- Manual edits are high risk because this file is generated register metadata. Changes should usually come from regenerated AMD ASIC register sources rather than hand-written adjustments.

## Test Signals

Useful validation signals include:

- Build coverage for AMDGPU configurations that include GC 9.2.1 headers, especially `gfxhub_v1_1.c`, Vega12 PowerPlay, and `gfx_v9_0.c` GC 9.2.1 golden-setting tables.
- Static consistency checks that every register in this chunk has matching offset definitions in `gc_9_2_1_offset.h` and, where applicable, matching defaults in the generated default header.
- Runtime smoke tests on GC 9.2.1/Vega12-class hardware that boot, initialize GFX, apply golden settings, and complete suspend/resume without invalid register access warnings.
- Wave debug tests that read a selected wave or register through `SQ_IND_INDEX`/`SQ_IND_DATA` and verify force-read/auto-increment behavior.
- GPUVM/cache invalidation tests that exercise SQC instruction/data UTCL1 invalidation by VMID and check the fault/retry/PRT status bits remain sane under memory pressure.
- Graphics workloads that stress depth/stencil compression, HTILE, texture sampling, GDS, and tiled surface layouts, because those paths depend on `TA_*`, `TD_*`, `GDS_*`, `DB_*`, `GB_ADDR_CONFIG`, and `GB_TILE_MODE*` fields.
- Trace/profiling validation that decodes `SQ_THREAD_TRACE_WORD_*` records into stable wave, SIMD, CU, PC, timestamp, register, and perf-counter data.
