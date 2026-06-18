# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002649`: lines 1-2405, `Docs/researches/chunks/subset-b-002649_research.md`
- `subset-b-002650`: lines 2406-4820, `Docs/researches/chunks/subset-b-002650_research.md`
- `subset-b-002651`: lines 4821-7169, `Docs/researches/chunks/subset-b-002651_research.md`
- `subset-b-002652`: lines 7170-9632, `Docs/researches/chunks/subset-b-002652_research.md`
- `subset-b-002653`: lines 9633-12147, `Docs/researches/chunks/subset-b-002653_research.md`
- `subset-b-002654`: lines 12148-14604, `Docs/researches/chunks/subset-b-002654_research.md`
- `subset-b-002655`: lines 14605-17184, `Docs/researches/chunks/subset-b-002655_research.md`
- `subset-b-002656`: lines 17185-19585, `Docs/researches/chunks/subset-b-002656_research.md`
- `subset-b-002657`: lines 19586-22303, `Docs/researches/chunks/subset-b-002657_research.md`
- `subset-b-002658`: lines 22304-24747, `Docs/researches/chunks/subset-b-002658_research.md`
- `subset-b-002659`: lines 24748-27129, `Docs/researches/chunks/subset-b-002659_research.md`
- `subset-b-002660`: lines 27130-29635, `Docs/researches/chunks/subset-b-002660_research.md`
- `subset-b-002661`: lines 29636-31186, `Docs/researches/chunks/subset-b-002661_research.md`

## Chunk Research

### subset-b-002649: lines 1-2405

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 1-2405

## Purpose

This chunk opens the generated GC 9.2.1 shift/mask header and defines the bitfield layout for the first 2,405 lines of the file. It is register metadata for AMDGPU GC hardware, not executable logic. Each register field is represented as paired preprocessor constants:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the 32-bit register value.

The covered lines include the license, include guard `_gc_9_2_1_SH_MASK_HEADER`, and the beginning of four address blocks:

- `gc_grbmdec`: graphics register bus manager status, control, traps, scratch registers, power/clock controls, read/write/IOV error capture, and UTCL2 invalidation ranges.
- `gc_cpdec`: command processor status, busy/stall diagnostics, micro-engine controls, queue/ring pointer telemetry, FIFO thresholds, scratch access, and command-index/data debug windows.
- `gc_padec`: primitive assembler, vertex geometry/tessellation, work distributor, clipping/setup/scan-converter controls, primitive binning controls, UTCL1 controls, and shader-array or primitive disable masks.
- `gc_sqdec`: beginning of shader queue and shader cache control, LDS/SQ sizing, shader memory bases/configuration, interrupt control, UTCL1 status/control, trap base/mask addresses, and SQC DSM/error-injection fields.

The chunk contains 2,174 `#define` entries. It is one chunk of a much larger generated header; later register blocks after line 2405 are intentionally not summarized here.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or runtime APIs in this range. The API surface is the macro namespace consumed by AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and PowerPlay/SMU helper wrappers.

Important macro families in this chunk are:

- GRBM liveness and error fields:
  - `GRBM_STATUS__GUI_ACTIVE_MASK`, `GRBM_STATUS__CP_BUSY_MASK`, `GRBM_STATUS__CB_BUSY_MASK`, `GRBM_STATUS__DB_BUSY_MASK`, and per-block busy fields for TA/GDS/VGT/IA/SX/WD/SPI/SC/PA.
  - `GRBM_STATUS2__CPF_BUSY_MASK`, `GRBM_STATUS2__CPC_BUSY_MASK`, `GRBM_STATUS2__CPG_BUSY_MASK`, `GRBM_STATUS2__RLC_BUSY_MASK`, `GRBM_STATUS2__UTCL2_BUSY_MASK`, and CP queue pending bits.
  - `GRBM_STATUS_SE0` through `GRBM_STATUS_SE3` mirror clean/busy status per shader engine.
  - `GRBM_READ_ERROR`, `GRBM_READ_ERROR2`, `GRBM_WRITE_ERROR`, `GRBM_IOV_ERROR`, and `GRBM_RSMU_READ_ERROR` decode failing addresses, requester identity, pipe/ME IDs, VMID/VFID, operation, and error-present bits.
- GRBM control fields:
  - `GRBM_CNTL__READ_TIMEOUT_MASK` and `GRBM_CNTL__REPORT_LAST_RDERR_MASK`.
  - `GRBM_PWR_CNTL`, `GRBM_PWR_CNTL2`, `GRBM_GFX_CLKEN_CNTL`, `GRBM_WAIT_IDLE_CLOCKS`, `GRBM_SOFT_RESET`, `GRBM_DSM_BYPASS`, and `GRBM_CHICKEN_BITS`.
  - `GRBM_GFX_CNTL` selects pipe, ME, VMID, and queue context for CP/GFX access.
  - `GRBM_INT_CNTL` controls read-error and GUI-idle interrupts.
  - `GRBM_SCRATCH_REG0` through `GRBM_SCRATCH_REG7` are full-width scratch data fields.
- CP diagnostics and control:
  - `CP_CPC_STATUS`, `CP_CPF_STATUS`, `CP_STAT`, and `CP_BUSY_STAT` expose busy bits for MEC, CPF, CPC, PFP, ME, CE, ROQ, RCIU, TCIU, UTCL2IU, scratch RAM, DMA, query, semaphore, interrupt, and surface-sync subblocks.
  - `CP_CPC_BUSY_STAT`, `CP_CPF_BUSY_STAT`, `CP_STALLED_STAT1`, `CP_STALLED_STAT2`, `CP_STALLED_STAT3`, `CP_CPC_STALLED_STAT1`, and `CP_CPF_STALLED_STAT1` decode detailed wait and stall reasons, including TC confirmations, atomic return data, ROQ/MEQ/STQ waits, partial flushes, append/streamout/pipeline stats, and UTCL1/UTCL2 tag pressure.
  - `CP_ME_CNTL` and `CP_MEC_CNTL` provide instruction-cache invalidation, pipe reset, halt, and single-step bits for graphics and compute micro-engines.
  - `CP_ME_HEADER_DUMP`, `CP_PFP_HEADER_DUMP`, `CP_CE_HEADER_DUMP`, `CP_MEC_ME1_HEADER_DUMP`, and `CP_MEC_ME2_HEADER_DUMP` are full-width debug dump fields.
  - Queue/ring fields cover `CP_RB*_RPTR`, `CP_RB_WPTR_DELAY`, `CP_RB_WPTR_POLL_CNTL`, ROQ/STQ/MEQ thresholds and availability, CEQ availability, and ROQ/CEQ read/write pointer telemetry.
  - `CP_CMD_INDEX` and `CP_CMD_DATA` form a debug command-selection/data pair.
- PA/VGT/WD/IA controls:
  - `VGT_CACHE_INVALIDATION` defines cache invalidation mode, auto-invalidation, GS/ES limits, streamout flush, ping-pong, wave merge, and NGG/legacy flow-control options.
  - `VGT_DMA_CONTROL`, `VGT_DMA_PRIMITIVE_TYPE`, `VGT_DMA_*_FIFO_DEPTH`, and `VGT_DMA_LS_HS_CONFIG` control primitive grouping, instancing optimizations, and DMA/front-end queue sizing.
  - `IA_CNTL_STATUS`, `VGT_CNTL_STATUS`, and `WD_CNTL_STATUS` expose input assembler, geometry/tessellation/primitive generator, and work distributor busy state.
  - `CC_GC_PRIM_CONFIG`, `GC_USER_PRIM_CONFIG`, `CC_GC_SHADER_ARRAY_CONFIG`, and `GC_USER_SHADER_ARRAY_CONFIG` describe inactive primitive/shader-array resources.
  - `WD_UTCL1_CNTL`, `WD_UTCL1_STATUS`, `IA_UTCL1_CNTL`, and `IA_UTCL1_STATUS` expose front-end UTCL1 invalidation, VMID reset/drop/bypass behavior, XNACK retry timing, fault/retry/PRT detection, and UTCL1 IDs.
  - `PA_CL_ENHANCE`, `PA_CL_RESET_DEBUG`, `PA_SU_CNTL_STATUS`, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_ENHANCE_2`, and `PA_SC_DSM_CNTL` are tuning/debug controls for clipping, setup, scan conversion, out-of-order processing, binning, clock-gating workarounds, reset behavior, and DSM forcing.
  - `PA_SC_BINNER_EVENT_CNTL_0` through `_3`, `PA_SC_BINNER_TIMEOUT_COUNTER`, and `PA_SC_BINNER_PERF_CNTL_0` through `_3` define primitive binning event routing, flush/thread-trace/pipeline event actions, timeout threshold, and bin/batch histogram thresholds.
  - `PA_UTCL1_CNTL1` and `PA_UTCL1_CNTL2` provide PA-side GPUVM response, invalidation, shootdown, snoop, perf-event, and fragment handling controls.
- SQ/SQC controls at the start of `gc_sqdec`:
  - `SQ_CONFIG` controls SQ debug modes, soft-clause behavior, flat/LDS bypass behavior, replay sleep, and SP write/thread gating.
  - `SQC_CONFIG`, `LDS_CONFIG`, `SQ_REG_CREDITS`, and `SQ_FIFO_SIZES` define shader-cache and shader-queue sizing, credits, and FIFO capacities.
  - `SQ_DSM_CNTL`, `SQ_DSM_CNTL2`, `SQC_DSM_CNTL`, `SQC_DSM_CNTLA`, `SQC_DSM_CNTLB`, `SQC_DSM_CNTL2`, `SQC_DSM_CNTL2A`, and the start of `SQC_DSM_CNTL2B` expose DSM irritator and error-injection controls for SQ and SQC RAM/FIFO structures.
  - `SH_MEM_BASES`, `SH_MEM_CONFIG`, `CC_GC_SHADER_RATE_CONFIG`, `GC_USER_SHADER_RATE_CONFIG`, `SQ_INTERRUPT_*`, `SQ_UTCL1_CNTL*`, `SQ_UTCL1_STATUS`, `SQ_SHADER_TBA_*`, and `SQ_SHADER_TMA_*` provide shader address, memory, interrupt, fault, trap-base, and trap-mask field definitions.

## Control Flow

There is no runtime control flow in this header fragment. Its only direct compile-time behavior is the include guard that prevents duplicate macro definitions.

Runtime behavior appears when callers compose register values or extract fields using these macros. Typical flows are:

1. Include the ASIC-specific offset and shift/mask headers for GC 9.2.1.
2. Read a hardware register with a SOC15 accessor such as `RREG32_SOC15(GC, 0, mm...)`.
3. Extract or update a field with `REG_GET_FIELD` or `REG_SET_FIELD`, which depend on the exact `__SHIFT` and `_MASK` names defined here.
4. Write the modified value back with `WREG32_SOC15` or a PowerPlay/SMU wrapper.

Examples visible in the tree show this pattern for GC-family headers: `gfxhub_v1_1.c` includes `gc/gc_9_2_1_offset.h` and this shift/mask header before using `REG_GET_FIELD`, while `pm/powerplay/hwmgr/vega12_inc.h` gathers the Vega12 GC 9.2.1 register headers with THM, MP, and NBIO headers for power-management code.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. They do not allocate memory, persist data, perform I/O, or cache state.

The hardware fields they describe are stateful. Important state categories include:

- Volatile busy/idle state in `GRBM_STATUS*`, `CP_*STATUS`, `IA_CNTL_STATUS`, `VGT_CNTL_STATUS`, and `WD_CNTL_STATUS`.
- Error-latch state in `GRBM_READ_ERROR*`, `GRBM_WRITE_ERROR`, `GRBM_IOV_ERROR`, `GRBM_RSMU_READ_ERROR`, and UTCL1 status registers.
- Persistent-until-reset or persistent-until-programmed control state in CP halt/reset controls, GRBM power/clock controls, VGT cache invalidation configuration, PA/SC tuning controls, shader memory base/configuration registers, and UTCL1 invalidation controls.
- Scratch/debug state in GRBM scratch registers, CP scratch/index/data windows, instruction/header dump fields, ring/queue pointer snapshots, and DSM/error-injection controls.

Because these fields target live GPU registers, software sequencing matters. For example, CP halt/reset bits can stop command processing, cache invalidation controls can change graphics synchronization behavior, and error-injection/DSM fields can intentionally perturb hardware paths. This header does not enforce ordering, locking, privilege, or read-modify-write safety; callers must provide that policy.

## Dependencies

This file depends on the generated AMD ASIC register model for GC 9.2.1. It is useful only when paired with matching register offset/default headers and the AMDGPU register helper macros.

Primary dependencies and consumers are:

- `gc_9_2_1_offset.h`, which supplies the corresponding register addresses (`mm*`, `ix*`, or generation-specific aliases).
- AMDGPU SOC15 register access helpers and field helpers that expand names into `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT`.
- ASIC-specific integration headers such as `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h`, which includes this header for Vega12-era PowerPlay code.
- GC 9.2.1 users such as `drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c`, which includes this header alongside the matching offset header before decoding GC register fields.
- Sibling generated GC headers for other generations. Similar names exist in `gc_9_*`, `gc_10_*`, `gc_11_*`, and older `gca/gfx_*` headers, but bit positions and field availability can diverge.

## Integration Points

This chunk integrates with several AMDGPU subsystems:

- Graphics reset and idle detection use GRBM status fields, especially GUI-active and CP/CB/DB/PA/SC/SPI busy masks.
- Power management and SMU/PowerPlay setup use GC 9.2.1 include bundles, plus GRBM power/clock and CP halt/reset fields when quiescing or configuring hardware.
- Command processor initialization, debug, and recovery code uses CP ME/MEC controls, queue/ring pointer fields, busy/stall status, and scratch/header-dump registers.
- GFX VM and fault handling use UTCL1/UTCL2 controls and status fields from WD, IA, PA, SQ, and GRBM invalidation ranges.
- Graphics pipeline setup uses VGT, IA, WD, PA_CL, PA_SU, and PA_SC fields to configure primitive handling, DMA/instancing behavior, cache invalidation, primitive binning, out-of-order scan conversion, and shader-array disable masks.
- Shader/trap/debug paths use SQ/SQC config fields, shader trap base/mask fields, shader memory base/config fields, SQ interrupt controls, and DSM/error-injection controls.

The immediate include tree is source-tree aligned under `drivers/gpu/drm/amd/include/asic_reg/gc/`; this research document is a chunk-level note and should be merged later with other chunks for the full file-level report.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can read the wrong status bit, write reserved bits, or silently change unrelated hardware state.
- Cross-generation reuse is unsafe. Many field names repeat across GC generations, but available bits and masks differ; callers must include the GC 9.2.1 header only for matching ASICs.
- Read-modify-write operations against live registers can race with firmware, interrupts, reset paths, or hardware state changes. This is especially risky for CP halt/reset, GRBM power/clock, cache invalidation, and UTCL invalidation fields.
- Status and error registers may have latch, clear-on-read, or side-effect behavior defined by hardware rather than this header. Consumers must not infer persistence semantics from masks alone.
- Reserved/spare/ECO fields are present in PA/SC/SQ/SQC blocks. Writing them without hardware guidance can trigger unsupported workarounds or destabilize graphics operation.
- DSM and error-injection controls are diagnostic/stress features. Accidental enablement can create artificial faults or memory-path stress that resembles real hardware failure.
- Full-width fields such as scratch, header-dump, timeout, threshold, and command-data masks give no type safety; software must validate values before writing.

## Test Signals

Useful validation is mostly build-time, static, and hardware-smoke oriented:

- Compile AMDGPU configurations that include Vega12/GC 9.2.1 paths, especially `vega12_inc.h` and `gfxhub_v1_1.c`, to catch missing or renamed macros.
- Static consistency checks between `gc_9_2_1_offset.h` and this header: every register used by field helpers should have matching offset and shift/mask definitions.
- Static field-pair checks ensuring every `__SHIFT` macro in this line range has a corresponding `_MASK` macro for the same register field.
- Runtime idle/reset smoke tests on GC 9.2.1 hardware: poll `GRBM_STATUS*` and CP status masks around graphics workload submission, ring idle, reset, and resume.
- CP recovery tests that exercise `CP_ME_CNTL` and `CP_MEC_CNTL` halt/reset/invalidate bits while confirming queues restart and no unexpected hangs occur.
- Fault-path tests that induce or observe GPUVM/UTCL1 faults and verify `WD_UTCL1_STATUS`, `IA_UTCL1_STATUS`, `PA_UTCL1_*`, and `SQ_UTCL1_STATUS` decode correctly.
- Graphics workload tests with primitive binning, streamout, tessellation, geometry, and shader trap/debug paths enabled to catch invalid VGT/PA/SQ field definitions.
- Register readback tests after programming selected fields with `REG_SET_FIELD` and decoding with `REG_GET_FIELD`, limited to non-destructive fields or guarded hardware validation environments.

### subset-b-002650: lines 2406-4820

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

### subset-b-002651: lines 4821-7169

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 4821-7169

## Purpose

This chunk is a generated AMD GC 9.2.1 register bitfield header. It does not implement executable logic; it defines the `_SHIFT` and `_MASK` constants that the AMDGPU driver uses with `REG_SET_FIELD()` and `REG_GET_FIELD()` to compose or decode 32-bit hardware register values. The covered range starts in the middle of the graphics backend tiling table definitions and ends partway through `VM_CONTEXT13_CNTL`.

The chunk covers these register groups:

- `GB_TILE_MODE11` through `GB_TILE_MODE31` and `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15`, which describe graphics backend tile and macrotile layout fields.
- Color buffer controls such as `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_CONTROL_3`, `CB_HW_MEM_ARBITER_RD`, `CB_HW_MEM_ARBITER_WR`, and `CB_DCC_CONFIG`.
- Render backend fuse/harvest controls through `GC_USER_RB_REDUNDANCY` and `GC_USER_RB_BACKEND_DISABLE`.
- `gc_ea_gceadec2` fields for GCEA performance counters, diagnostic/static memory controls, TCC crossbar credits, probe mapping, error status, DRAM arbitration, and SDP credit/backdoor enable controls.
- `gc_rmi_rmidec` fields for RMI request path control, status, UTCL1 interaction, xbar/demux arbitration, scoreboard/invalidation state, clock control, and spare registers.
- `gc_utcl2_atcl2dec` and `gc_utcl2_vml2pfdec` fields for ATC L2, VM L2 cache control, page fault/default page handling, identity aperture mapping, parity controls, and clock gating.
- `gc_utcl2_vml2vcdec` fields for `VM_CONTEXT0_CNTL` through the first part of `VM_CONTEXT13_CNTL`, defining per-VMID page table depth/block size and fault interrupt/default behavior.

## Important APIs, Types, And Macros

There are no functions or C types in this range. The public surface is a set of preprocessor constants named as:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The constants are consumed by the common AMDGPU bitfield helpers in `drivers/gpu/drm/amd/amdgpu/amdgpu.h`:

- `REG_SET_FIELD(orig_val, reg, field, field_val)` clears `reg__field_MASK` in `orig_val` and inserts `field_val << reg__field__SHIFT`.
- `REG_GET_FIELD(value, reg, field)` masks `value` with `reg__field_MASK` and shifts it down by `reg__field__SHIFT`.

The companion address definitions are in `gc_9_2_1_offset.h`. This mask header is included directly by `amdgpu/gfxhub_v1_1.c` and by `pm/powerplay/hwmgr/vega12_inc.h`; `gfxhub_v1_1.c` is the concrete GC 9.2.1 consumer in this tree.

## Register Areas In This Chunk

`GB_TILE_MODE11` through `GB_TILE_MODE31` repeat the same five fields: `ARRAY_MODE`, `PIPE_CONFIG`, `TILE_SPLIT`, `MICRO_TILE_MODE_NEW`, and `SAMPLE_SPLIT`. These are hardware layout encodings used by the graphics backend for tiled surfaces. The range starts with the final two masks for `GB_TILE_MODE10`, so chunk reconciliation needs to account for the split from the previous chunk.

`GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15` define `BANK_WIDTH`, `BANK_HEIGHT`, `MACRO_TILE_ASPECT`, and `NUM_BANKS`. These constants describe the macrotiling memory-bank layout and must remain consistent with the tile mode register offsets and any users that decode tiling metadata.

The `CB_*` section defines color buffer cache, blend, fast-clear, DCC, and memory arbiter controls. Notable fields include cache eviction/tag counts, FIFO depths, several disable/workaround bits, read/write arbiter weights, and DCC overwrite-combiner behavior. These bits affect render target cache behavior and color/depth compression paths.

`GC_USER_RB_REDUNDANCY` and `GC_USER_RB_BACKEND_DISABLE` expose render backend redundancy/disable masks. Other generations read these fields to account for harvested or disabled render backends when deriving active RB topology; the same naming convention enables generation-specific code to use common field helpers.

The `GCEA_*` section covers graphics client/event/address path controls: diagnostic memory single-write/error injection fields, TCC crossbar credit and max-burst fields, probe routing maps, error status bits, DRAM-bank arbitration, and SDP backdoor credit accounting. These are low-level performance, diagnostics, and fabric-credit knobs rather than ordinary runtime state.

The `RMI_*` section describes the request memory interface between graphics clients, render backends, UTCL1/UTCL2, and memory. It includes xbar muxing and arbitration, harvest bits for RB paths, skid FIFO errors, UTCL1 invalidation control, TCIW formatter behavior, scoreboard flush/invalidation status, and clock/spare controls. The scoreboard fields are particularly relevant to VMID invalidation progress and flush completion signals.

The `ATC_L2_*` section defines address translation cache L2 controls and status fields. These cover translation request limits, bank selection, cache update modes, cache data inspection, parity status, memory light sleep, and clock-gating timer/override fields.

The `VM_L2_*` section defines the graphics VM L2 behavior: cache enablement, fragment processing, endian-swap modes, queue sizing, page fault classification, dummy/default page addresses, fault status/address capture, identity aperture low/high bounds, physical offset, MM group request classes, reserved client ID bank selection, parity control, and VM L2 clock gating.

`VM_CONTEXT0_CNTL` through `VM_CONTEXT13_CNTL` are per-context VM controls. Each full context block defines `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry controls, and interrupt/default-enable bits for range, dummy-page, PDE0, valid, read, write, and execute protection faults. The chunk ends inside `VM_CONTEXT13_CNTL`; later lines continue that register and subsequent contexts.

## Control Flow

This header has no runtime control flow. The effective control flow appears in users that include this file:

1. Driver code reads or constructs a 32-bit register value.
2. `REG_SET_FIELD()` uses the `_MASK` and `_SHIFT` macros to update a specific field.
3. The driver writes the value with SOC15 register accessors such as `WREG32_SOC15*()`, or decodes a read value with `REG_GET_FIELD()`.

For GC 9.2.1, `gfxhub_v1_1.c` includes this header and the matching offset header. That source uses the same register metadata style for XGMI and graphics hub setup. The VM L2 and context fields in this chunk align with the common gfxhub initialization pattern used across neighboring `gfxhub_v1_2.c` and `mmhub_v1_*` implementations: configure `VM_L2_CNTL*`, initialize `VM_CONTEXT0_CNTL`, program `VM_CONTEXT1_CNTL + i * ctx_distance`, and set `ctx_distance` from adjacent context register offsets.

## State And Persistence Behavior

The file itself has no mutable state. The macros describe persistent hardware register state:

- Tile/macrotile and color buffer fields influence GPU memory layout, render target cache policy, DCC behavior, and render backend availability.
- GCEA/RMI/ATC/VM fields affect request routing, credit accounting, diagnostic injection, cache/parity status, VM invalidation, and fault response.
- `VM_L2_PROTECTION_FAULT_STATUS` and fault address registers describe latched fault state. Fields such as `CLEAR_PROTECTION_FAULT_STATUS_ADDR` and `ALLOW_SUBSEQUENT_PROTECTION_FAULT_STATUS_ADDR_UPDATES` control whether captured fault addresses are cleared or overwritten.
- `VM_CONTEXT*_CNTL` fields persist per VM context until reprogrammed during GPU initialization, reset, suspend/resume, or VM hub reconfiguration.

Because these constants encode a hardware ABI, persistence is in the GPU registers, not in this header. Incorrect masks or shifts can silently write the wrong bit and persist until the next register programming sequence or reset.

## Dependencies And Integration Points

This chunk depends on the AMD GC 9.2.1 hardware register specification and must match `gc_9_2_1_offset.h` register addresses. It also depends on the `REG_SET_FIELD()`/`REG_GET_FIELD()` macro contract, which assumes exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` names.

Primary integration points:

- `amdgpu/gfxhub_v1_1.c` includes `gc/gc_9_2_1_offset.h` and `gc/gc_9_2_1_sh_mask.h`, tying these bit definitions to graphics hub register programming.
- `pm/powerplay/hwmgr/vega12_inc.h` includes this file for Vega12 power management paths that need GC register field names.
- SOC15 register access macros (`RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and offset variants) combine with this header and the offset header to address and manipulate actual MMIO registers.
- VM fault interrupt handling elsewhere in AMDGPU/AMDKFD depends on correctly programmed VM context and VM L2 fault bits, even when the direct handling code uses generation-specific aliases.

## Risks

The main risk is bitfield drift from the hardware specification. A wrong shift or mask can corrupt neighboring fields, for example enabling the wrong VM fault response, misprogramming page table depth/block size, breaking tile layout interpretation, or disabling a color buffer optimization unexpectedly.

This range includes many repeated register families. Copy/paste or generator errors are easy to miss, especially in `GB_TILE_MODE*`, `GB_MACROTILE_MODE*`, and `VM_CONTEXT*_CNTL`, where most blocks are intentionally identical except the register prefix. The range boundary is also split: it starts with two `GB_TILE_MODE10` masks and ends inside `VM_CONTEXT13_CNTL`, so merge tooling must preserve continuity with adjacent chunks.

Several fields are diagnostic or fault-injection controls (`GCEA_DSM_CNTL*`, `GCEA_DSM_CNTL2*`, parity/fault controls). Accidental writes in production paths could create artificial memory/fabric errors or alter fault recovery behavior.

VM fields are high risk because they affect GPU virtual memory isolation and page fault handling. Misprogramming retry/default bits can convert recoverable faults into fatal behavior, suppress interrupts, or route invalid accesses to dummy/default pages.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Kernel build coverage for configurations that compile `gfxhub_v1_1.c` and Vega12 powerplay includes catches missing or renamed macros.
- Boot/probe on GC 9.2.1 ASICs should complete graphics hub setup without register programming failures.
- GPUVM tests should exercise VM context setup, page table depth/block size, VMID invalidation, and fault handling paths.
- Fault injection or negative VM tests should produce expected `VM_L2_PROTECTION_FAULT_STATUS`, fault address, VMID, client ID, read/write/execute, and retry/no-retry behavior.
- Render and display workloads using tiled render targets should validate that tile/macrotile and CB/DCC fields remain compatible with surface layout and compression expectations.
- RAS/parity diagnostics should validate ATC/VM L2 parity status and clear paths where hardware support is available.

### subset-b-002652: lines 7170-9632

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 7170-9632

## Scope

This chunk is a generated AMD GC 9.2.1 register shift/mask header slice. It contains C preprocessor `#define` constants only: each register field is represented as a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, enums, global variables, allocations, locks, direct MMIO operations, or runtime branches in this range.

The selected lines contain 2,127 `#define` statements covering 328 register macro groups. The chunk starts in the middle of `VM_CONTEXT13_CNTL`, then covers complete VM context controls for contexts 14 and 15, VM invalidation semaphore/request/ack/range registers, VM context page-table base/start/end address fields, GC shared VM aperture controls, and a large GCEA address/priority/decode register block. It ends inside `GCEA_IO_WR_PRI_URGENCY_MASK`, so that register's remaining CID shift/mask definitions continue in the next chunk.

Although this repository path is under `sources/distributed-fs/ceph-client`, this header is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem client behavior.

## Purpose

`gc_9_2_1_sh_mask.h` supplies the field-level bit positions and masks for GC 9.2.1 registers. Driver code includes it with the companion `gc_9_2_1_offset.h` so AMDGPU paths can build, update, and decode MMIO register values with symbolic field names rather than hard-coded bit constants.

This chunk focuses on graphics VM and GCEA memory-fabric surfaces:

- VM context enable/fault-policy fields for contexts 13 through 15.
- Context-wide disable bits for VM contexts 0 through 15.
- VM invalidation engines 0 through 17, including semaphore ownership, per-VMID request bits, flush type, L2/L1 PTE/PDE invalidation selectors, protection-fault-status clearing, acknowledgment bits, and optional address-range bounds.
- VM context page-table base, start, and end address fields for contexts 0 through 15.
- Shared VM/MC aperture, framebuffer, AGP, top-of-DRAM, HBM, XGMI local-framebuffer, PCI, steering, cacheable-address, and L1 TLB controls.
- GCEA DRAM and IO client-to-group maps, group-to-VC maps, lazy/CAM/page-burst controls, priority age/queue/fixed/urgency/quantum controls, urgency masks, address normalization, DRAM hole/trichannel settings, bank/misc address decode configuration, address hashing, harvest controls, and two address-decoder instances for chip-select, row, column, bank, and rank-module selection.

## Important APIs, Types, And Macros

The only interface in this chunk is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field's bit mask in the 32-bit register value.
- `// addressBlock:` comments identify generated hardware address blocks. This chunk transitions through `gc_utcl2_vmsharedpfdec`, `gc_utcl2_vmsharedvcdec`, and `gc_ea_gceadec`; it begins in a previous VM block whose address-block marker is outside the selected lines.

There are no callable APIs or C types here. Consumers normally use these definitions through AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`. Register offsets live in `gc_9_2_1_offset.h`; this file only describes field layout inside the register value.

Important register families in this chunk include:

- `VM_CONTEXT14_CNTL` and `VM_CONTEXT15_CNTL`, plus the tail of `VM_CONTEXT13_CNTL`: `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry policy, and fault interrupt/default policy bits for range, dummy-page, PDE0, valid, read, write, and execute faults.
- `VM_CONTEXTS_DISABLE`: one disable bit per context 0 through 15.
- `VM_INVALIDATE_ENG0..17_SEM`, `_REQ`, `_ACK`, `_ADDR_RANGE_LO32`, and `_ADDR_RANGE_HI32`: the field contract for TLB/page-table invalidation engines.
- `VM_CONTEXT0..15_PAGE_TABLE_BASE_ADDR_LO32/HI32`, `START_ADDR_LO32/HI32`, and `END_ADDR_LO32/HI32`: page-directory-entry and logical-page-number fields split into low 32-bit and small high-bit portions.
- `MC_VM_NB_*`, `MC_VM_FB_OFFSET`, `MC_VM_SYSTEM_APERTURE_*`, `MC_VM_STEERING`, `MC_SHARED_VIRT_RESET_REQ`, `MC_MEM_POWER_LS`, `MC_VM_APT_CNTL`, `MC_VM_LOCAL_HBM_*`, and `MC_VM_XGMI_LFB_*`: shared VM aperture and memory-location fields.
- `MC_VM_FB_LOCATION_BASE/TOP`, `MC_VM_AGP_TOP/BOT/BASE`, `MC_VM_SYSTEM_APERTURE_LOW/HIGH_ADDR`, and `MC_VM_MX_L1_TLB_CNTL`: visible VM aperture and TLB configuration fields.
- `GCEA_DRAM_*` and `GCEA_IO_*`: read/write client group maps, virtual-channel maps, lazy/CAM controls, burst controls, priority coefficients, urgency modes, quantum values, combine-flush policy, and per-CID urgency masks.
- `GCEA_ADDRNORM*`, `GCEA_ADDRDEC*`, and `GCEA_ADDRDECDRAM*`: address normalization, DRAM hole, bank/channel/chip-select/rank-module decode, XOR hash, harvest, chip-select base/mask/config, column selection, row/bank selection, and secondary chip-select selection fields.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution of symbolic shift and mask constants into register composition or decode expressions.

The implied runtime flow is:

1. A GC 9.2.1 path selects an `mm...` register offset from `gc_9_2_1_offset.h`.
2. The same path uses this header's `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants, usually through `REG_SET_FIELD` or `REG_GET_FIELD`, to construct or inspect a 32-bit register value.
3. AMDGPU reads or writes the register through SOC15 MMIO helpers, or stores the field definition in a golden-register, debug, RAS, or initialization table.
4. The hardware VM, GCEA, memory-controller, invalidation-engine, address-decoder, or prioritization logic applies the resulting state.

The VM invalidation fields imply higher-level sequencing, but the sequence is not encoded here. Typical code composes a request with a per-VMID invalidate bit, selected flush type, L1/L2 invalidate selectors, and optional address-range registers; writes the request engine; then polls or waits for the matching ACK/semaphore state. This chunk only defines the bit positions needed by that flow.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent and volatile state exists only in the GPU registers whose fields are described here.

Hardware state represented by this chunk includes VM context enablement, page-table depth/block sizing, fault interrupt/default policies, VMID/context disable state, invalidation-engine request and acknowledgment bits, page-table base/start/end address bounds, framebuffer and AGP aperture locations, default system aperture address, L1 TLB behavior, cacheability and HBM/XGMI placement, GCEA client grouping, traffic arbitration coefficients, urgency masks, address normalization windows, DRAM address hashing, harvest overrides, and address-decoder chip-select geometry.

Many programmed values persist until driver reinitialization, VM hub setup, GPU reset, suspend/resume restore, power-gating loss, firmware initialization, or explicit register reprogramming. Invalidation request and acknowledgment fields are transient hardware synchronization state. Fault-policy bits affect later VM fault behavior until changed. Address decode, aperture, and TLB settings are global enough that stale or mismatched state can affect all command queues that issue memory transactions through the corresponding hub.

This generated header does not distinguish read-only, write-only, sticky, clear-on-write, self-clearing, security-sensitive, or reset-default behavior. Consumers must rely on the hardware programming sequence and the companion offset/default headers.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.2.1 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h` supplies matching `mm...` register offsets and base indices for the field names in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h` includes `gc_9_2_1_offset.h` and `gc_9_2_1_sh_mask.h` for Vega12 power-management code.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c` includes this GC 9.2.1 shift/mask header and uses the VM invalidation, aperture, framebuffer, and TLB field macros for the GFX hub.
- Shared AMDGPU VM hub code patterns use these fields with `REG_SET_FIELD` and `REG_GET_FIELD` around `MC_VM_MX_L1_TLB_CNTL`, `VM_INVALIDATE_ENG0_REQ`, `VM_INVALIDATE_ENG0_ACK`, `VM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32`, `MC_VM_FB_LOCATION_BASE/TOP`, `MC_VM_AGP_*`, and `MC_VM_SYSTEM_APERTURE_*`.
- GFX9 family initialization and golden-setting paths program GCEA, GCMC, and VM registers during ASIC bring-up, reset, power-management, and hub setup.
- Display and memory-management code may read or depend on framebuffer/aperture registers such as `MC_VM_FB_LOCATION_BASE/TOP`, `MC_VM_FB_OFFSET`, and `MC_VM_SYSTEM_APERTURE_*` to derive visible VRAM and aperture layout.

Runtime integration points include VM hub setup, GPUVM page-table configuration, VMID invalidation and TLB flush, fault interrupt policy, KFD/compute and graphics queue memory access, framebuffer/AGP/system-aperture programming, XGMI/HBM local-memory placement, golden-register initialization, power-management restore, debug register dumps, and low-level GCEA traffic/address-decode tuning.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can write the wrong hardware bits, silently corrupting VM, aperture, invalidation, or address-decode state.
- The chunk starts mid-register at `VM_CONTEXT13_CNTL`; the earlier `SHIFT` definitions and address-block context for that register are in the previous chunk.
- The chunk ends mid-register at `GCEA_IO_WR_PRI_URGENCY_MASK`; CID14 through CID31 and the corresponding masks continue in the next chunk.
- Repeated families are easy to mis-index. `VM_INVALIDATE_ENG0..17`, `VM_CONTEXT0..15`, `GCEA_ADDRDEC0/1`, `CS01/CS23`, secondary chip-select fields, and `CID0..31` masks depend on consistent generated naming and bit spacing.
- VM invalidation programming is synchronization-sensitive. Wrong `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, L1/L2 invalidate selector, ACK, or semaphore masks can produce stale translations, memory corruption, GPU page faults, or hung queues.
- Page-table address fields are split across low and high registers. Incorrect masks for high-bit fields can truncate or overrun GPU virtual-address bounds.
- Fault-policy fields control interrupt/default behavior for range, dummy-page, PDE0, valid, read, write, and execute faults. Bad values can hide VM faults, flood interrupts, or allow an unsafe default response.
- Aperture and framebuffer fields affect visible VRAM, AGP, system aperture, cacheable memory ranges, HBM, and XGMI layout. Incorrect masks can misplace memory windows or break display, DMA, or page-table access.
- GCEA address-decode and hash fields are topology-sensitive. Incorrect bank, channel, chip-select, row, column, rank-module, harvest, or XOR hash programming can cause hard-to-debug memory faults or severe performance issues.
- Priority and urgency controls influence traffic fairness and latency. Bad coefficients or per-CID masks can create starvation, performance cliffs, or intermittent hangs under mixed graphics/compute/IO traffic.
- The same field names appear across multiple AMD GPU generations with similar but not guaranteed-identical layouts. Cross-ASIC copy/paste must stay tied to the GC 9.2.1 offset and mask pair.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include Vega12/GC 9.2.1 support. Missing, malformed, or renamed macros should surface in `gfxhub_v1_1.c`, Vega12 powerplay files that include `vega12_inc.h`, and shared GFX9 paths.
- Mechanically compare every `__SHIFT` and `_MASK` in this chunk against AMD's authoritative GC 9.2.1 register database.
- Cross-check each register family in this chunk against `gc_9_2_1_offset.h` so every field group has a matching `mm...` register offset.
- Verify repeated counts and spacing: VM contexts 0-15, invalidation engines 0-17, page-table base/start/end low/high pairs, GCEA DRAM/IO CID maps 0-31, address-decoder instances 0/1, and chip-select groups `CS01`, `CS23`, `SECCS01`, and `SECCS23`.
- Exercise GPUVM workloads that create, update, invalidate, and destroy page tables while checking for missing ACKs, stuck invalidation semaphores, page faults, stale translations, and queue hangs.
- Run graphics and compute workloads across reset and suspend/resume paths to confirm VM context, TLB, aperture, and GCEA state is restored correctly.
- Validate display and memory-aperture reporting on Vega12 hardware, especially framebuffer base/top, AGP, system aperture, and default aperture address handling.
- Use register dumps to decode known-good hardware state with these masks and compare decoded fields against reference tools.
- Stress mixed traffic and memory-topology cases if GCEA priority/address-decode programming is changed: graphics, compute, DMA, display scanout, XGMI/HBM, and page-fault injection are useful signals.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002652`. The final per-file research should merge this with neighboring chunks for full `gc_9_2_1_sh_mask.h` coverage. The previous chunk owns the beginning of `VM_CONTEXT13_CNTL`; the next chunk owns the remainder of `GCEA_IO_WR_PRI_URGENCY_MASK` and subsequent GC 9.2.1 field definitions.

### subset-b-002653: lines 9633-12147

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 9633-12147

## Purpose

This chunk is generated-style register field metadata for AMD GC 9.2.1 graphics hardware. It defines preprocessor `__SHIFT` and `_MASK` constants for fields in several GC register address blocks: the tail of GCEA arbitration/priority controls, the `gc_tcdec` texture/cache block, the `gc_shdec` shader/compute context block, and the beginning of the `gc_cppdec` command processor block.

The header does not implement algorithms directly. Its purpose is to let AMDGPU code use symbolic field names with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and table-driven golden-register writes instead of embedding raw bit positions. The requested range starts in the middle of `GCEA_IO_WR_PRI_URGENCY_MASK` and ends in the middle of `CP_FATAL_ERROR`, so the merge lane must reconcile those partial register groups with adjacent chunks.

## Important APIs, Types, And Data

There are no C functions, structs, enums, or runtime object types in this range. The exported API surface is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field lsb.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask, normally with an `L` suffix.
- Register block comments such as `// addressBlock: gc_tcdec`, `// addressBlock: gc_shdec`, and `// addressBlock: gc_cppdec` align the masks with offset definitions in the companion `gc_9_2_1_offset.h`.

Major data groups in this chunk are:

- `GCEA_*`: graphics client/event arbitration fields for IO read/write urgency masks, read/write priority quantization thresholds, SDP arbitration limits, DRAM/GMI/IO priority, virtual-channel credit reservations, request override bits, latency sampling selectors, and two configurable performance counters.
- `TCP_*`, `TC_CFG_*`, `TCI_*`, `TCC_*`, and `TCA_*`: texture/cache control fields for invalidation, status, channel steering, address configuration, credits, L1/L2 load/store/atomic policy, volatile behavior, TCC redundancy/execution disable, DSM controls, L2 writeback/invalidate, soft reset, and cache-array burst controls.
- `SPI_SHADER_*`: per-stage shader program register fields for pixel, vertex, geometry/export, hull/local, and common user data state. The resource masks cover scratch, SGPR/VGPR allocation, priority, float mode, DX10 clamp, debug mode, exception masks, CU group enable/disable, LDS and user-SGPR sizing, TGID/TIDIG component counts, and address fields.
- `COMPUTE_*`: compute dispatch state fields for dispatch dimensions, start/restart coordinates, thread counts, pipeline/perf count enable, program addresses, AQL dispatch packet and scratch base addresses, compute program resource registers, VMID, resource limits, static thread management per shader engine, temporary ring sizing, thread trace, dispatch ID, relaunch, wave restore addresses, checksum, and 16 compute user-data registers.
- `CP_*`, `CPG_*`, `CPC_*`, and `CPF_*`: command processor debug, interrupt, virtual status, graphics error, UTCL1, ring-buffer, and priority/fatal-error fields. The range includes `CP_DFY_*` debug-data fields, `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, `CPC_INT_*`, `CP_VIRT_STATUS`, `CP_GFX_ERROR`, `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, `CPF_UTCL1_CNTL`, `CP_AQL_SMM_STATUS`, ring base/control/read-pointer/write-pointer-poll fields, `CP_INT_CNTL`, `CP_INT_STATUS`, device ID, pipe/ring priority counters, pipe/ring priority selectors, and the first three `CP_FATAL_ERROR` masks.

## Control Flow

This header fragment has no runtime control flow. It participates in control flow only after inclusion by GC 9.2.1-specific drivers or PowerPlay headers:

- Setup paths write register values by composing fields with `REG_SET_FIELD` and the masks from this header.
- Polling paths read status fields such as `TCP_STATUS`, `TCI_STATUS`, `CP_INT_STATUS`, `CP_VIRT_STATUS`, or `CP_DFY_STAT` and branch in the caller.
- Draw/dispatch paths program `SPI_SHADER_*` and `COMPUTE_*` context registers through packets or register writes, after which GPU microcode and hardware execute the actual shader or compute work.
- Ring setup paths program `CP_RB0_BASE`, `CP_RB0_CNTL`, `CP_RB_RPTR_ADDR*`, and `CP_RB_WPTR_POLL_ADDR*`; the CP then consumes indirect buffers and doorbell/write-pointer state asynchronously.
- Interrupt handlers and enable/disable paths use `CP_INT_CNTL` and `CP_INT_STATUS` masks to arm and interpret CP events such as VM doorbell writes, ECC, GPF, timeout, context busy/empty, GFX idle, privileged access, opcode errors, timestamp events, reserved-bit errors, and generic interrupts.

The nearby AMDGPU source tree shows this register family being integrated through `pm/powerplay/hwmgr/vega12_inc.h`, which includes `gc_9_2_1_offset.h` and `gc_9_2_1_sh_mask.h`, and through GC 9.x runtime code that uses the same macro families for ring buffer control and CP interrupt programming.

## State And Persistence Behavior

The macros are compile-time constants and store no state. The state they describe is hardware-owned, mostly volatile, and reset by GPU reset, power-gating, suspend/resume, or ASIC initialization sequences.

Important state classes described by this chunk:

- Arbitration and credit state: `GCEA_*` fields tune priority, burst limits, virtual-channel credits, request chaining, and latency/perf sampling. Bad settings affect request ordering and fairness but are not persisted by this header.
- Cache state: `TCP_INVALIDATE`, `TCC_WBINVL2`, `TCC_SOFT_RESET`, TCC/TCA DSM controls, and L1/L2 policy registers affect cache validity and coherency. Cache contents are hardware state; software must issue the right invalidation/writeback sequence around VM, memory, and shader changes.
- Shader context state: `SPI_SHADER_*` and `COMPUTE_*` fields describe current graphics/compute program addresses, resource allocation, user data, and dispatch parameters. These are context/register state programmed per workload or saved/restored by command processor mechanisms, not by this header.
- Ring state: `CP_RB*_BASE`, `CP_RB*_CNTL`, read-pointer addresses, write-pointer poll addresses, and buffer-size masks bind CP execution to ring buffers in GPU-visible memory. The pointer memory can outlive a register programming sequence, but the register fields are reinitialized by the driver after reset and resume.
- Interrupt/error state: `CP_INT_CNTL` enables events, while `CP_INT_STATUS`, `CP_GFX_ERROR`, and `CP_FATAL_ERROR` report transient hardware conditions. Status and fatal bits must be interpreted with the matching generation's register semantics.

No disk persistence, software serialization, or explicit lifetime management is implemented here.

## Dependencies

This chunk depends on the GC 9.2.1 generated register corpus staying internally synchronized:

- `gc_9_2_1_offset.h` supplies the register offsets for the masks in this file.
- Other generated GC 9.2.1 headers provide defaults and additional address spaces where present.
- AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and golden-register table macros depend on these exact field names.
- The C preprocessor include path must select the GC 9.2.1 header for the target ASIC; using a nearby GC 9.x generation's masks can compile while programming the wrong bits.
- Power-management and graphics initialization code for Vega12/Raven2-class GC 9.x hardware include this header through generation-specific include wrappers, while generic `gfx_v9_0` style code uses matching field families for CP rings, interrupts, cache policy, and shader setup.

## Integration Points

Primary integration points are in the AMDGPU driver tree:

- PowerPlay/SMU include glue: `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h` includes this mask header together with the matching offset header for GC 9.2.1 register programming tables.
- GFX hub and VM/cache integration: GC 9.x GFX hub code uses GC 9.2.1 register masks for address translation, cache, and related register operations on matching ASICs.
- Graphics ring initialization: `CP_RB0_CNTL`, `CP_RB_CNTL`, pointer-address, write-pointer-poll, and buffer-size masks are the field definitions used when the kernel initializes graphics rings and HQD-like queue controls.
- Interrupt integration: `CP_INT_CNTL` and `CP_INT_STATUS` masks connect CP hardware events to AMDGPU interrupt enablement and interrupt-source decoding.
- Shader and compute programming: `SPI_SHADER_*` and `COMPUTE_*` fields line up with command stream state packets and kernel scheduling paths that launch graphics and compute workloads.
- Diagnostics and telemetry: `GCEA_PERFCOUNTER*`, `GCEA_LATENCY_SAMPLING`, `CP_DFY_*`, `CP_GFX_ERROR`, `CP_FATAL_ERROR`, and status masks provide low-level observability for performance, virtualization, and fault handling.

## Risks

- Field drift is high impact: a wrong shift or mask can silently set unrelated hardware bits, especially in dense registers such as `CP_INT_CNTL`, `COMPUTE_PGM_RSRC*`, `SPI_SHADER_PGM_RSRC*`, and `CPF_UTCL1_CNTL`.
- Cross-generation reuse is unsafe. GC 9.2.1 is close to other GC 9.x headers, but offsets, valid bits, and reserved fields can differ across ASIC revisions.
- The chunk boundaries are partial. `GCEA_IO_WR_PRI_URGENCY_MASK` begins before line 9633, and `CP_FATAL_ERROR` continues after line 12147 with additional masks; standalone consumers of this chunk document should not treat those two groups as complete.
- Cache and coherency fields are sensitive. Misprogramming invalidation, volatility, or TCC writeback/invalidate controls can cause stale data, memory-ordering bugs, or GPU hangs.
- Ring-buffer fields encode sizes, alignment, and pointer-address split fields. Errors in `RB_BUFSZ`, `RB_BLKSZ`, `RB_RPTR_ADDR`, or write-pointer poll addresses can make the CP read invalid commands.
- Interrupt masks can create noisy IRQs or hide real faults if status and enable bits are mismatched.
- Shader resource masks control scratch, LDS, SGPR/VGPR allocation, exception behavior, and wave limits; invalid combinations can fail only under specific shader workloads.
- UTCL1 and VM-related fields can affect translation, snooping, invalidation, and dirty-state behavior. These are risky to alter outside known ASIC initialization sequences.

## Test Signals

Useful validation signals for changes touching these definitions are mostly compile-time and hardware/runtime oriented:

- Build coverage for AMDGPU configurations that include `gc_9_2_1_sh_mask.h` through Vega12/GC 9.2.1 include paths.
- Static consistency checks that every register field in this mask header has a matching register offset in `gc_9_2_1_offset.h` and that adjacent generated headers for defaults/offsets agree on register names.
- Boot smoke tests on supported GC 9.2.1 hardware with clean AMDGPU initialization, no invalid register-access warnings, and no early CP/GFX fatal errors.
- Graphics ring tests showing `CP_RB0_CNTL` setup, read/write pointers, doorbells, and fence signaling work after cold boot, GPU reset, and suspend/resume.
- Graphics and compute workload tests that exercise `SPI_SHADER_*` and `COMPUTE_*` state, including scratch-enabled shaders, LDS-heavy kernels, wave limits, and user-data registers.
- VM/cache coherency tests that combine buffer updates, TCC/TCP invalidation/writeback, atomics, and CPU/GPU synchronization.
- Interrupt tests that enable CP context, idle, timestamp, opcode, and fault-related events and confirm `CP_INT_STATUS` bits map to the expected interrupt sources.
- Performance/diagnostic checks for `GCEA_LATENCY_SAMPLING`, `GCEA_PERFCOUNTER*`, CP debug data, and fatal/error status paths where hardware access is available.

### subset-b-002654: lines 12148-14604

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 12148-14604

## Purpose

This chunk is generated AMD GC 9.2.1 register bitfield metadata. It contains no executable C code; its interface is a sequence of `#define` constants that publish hardware register field bit positions (`__SHIFT`) and masks (`_MASK`). AMDGPU, AMDKFD, and power-management code pair these constants with register offsets from `gc_9_2_1_offset.h` to compose, preserve, write, and decode MMIO register values for Vega-era graphics and compute blocks.

The selected range starts in the command processor decode block with ring-buffer VMID/write-pointer/doorbell fields, covers command processor interrupt, ECC, queue, VMID, context, and power controls, crosses `addressBlock: gc_cppdec2` for scheduler doorbells and CP reset/status fields, then covers `gc_spipdec`, `gc_cpphqddec`, `gc_didtdec`, `gc_gccacdec`, and the start of `gc_tcpdec`. It ends after the first `TCP_GATCL1_CNTL` fields, so later TCP cache-control fields are left to the next chunk.

Although this repository path is under `ceph-client`, this file is GPU driver hardware metadata and has no distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or C control-flow constructs in this range. The macro contract is:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field within a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register position.
- Consumers combine the shift/mask macros with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` from `gc_9_2_1_offset.h`, then use AMD register access helpers and read-modify-write patterns.

Major register groups in this chunk:

- CP ring-buffer and doorbell controls: `CP_RB_VMID`, `CP_ME0_PIPE*_VMID`, `CP_RB*_WPTR`, `CP_RB*_WPTR_HI`, `CP_RB*_BASE`, `CP_RB*_BASE_HI`, `CP_RB*_CNTL`, `CP_RB*_RPTR_ADDR`, `CP_RB*_RPTR_ADDR_HI`, `CP_RB*_ACTIVE`, `CP_RB_DOORBELL_CONTROL`, `CP_RB_DOORBELL_RANGE_*`, `CP_MEC_DOORBELL_RANGE_*`, and scheduler-specific `CP_RB_DOORBELL_CONTROL_SCH_0` through `_SCH_7`. These define VMIDs, queue base addresses, write/read pointer addresses, buffer sizing, cache policy, read-pointer update controls, doorbell offsets, enable/hit bits, and doorbell address ranges.
- CP/CPC/CPG fault and interrupt controls: `CP_INT_CNTL_RING0/1/2`, `CP_INT_STATUS_RING0/1/2`, `CP_ME1_PIPE0-3_INT_CNTL`, `CP_ME2_PIPE0-3_INT_CNTL`, matching `*_INT_STATUS` registers, `CPC_INT_CNTL`, `CPC_INT_STATUS`, `CPC_INT_CNTX_ID`, `CPG_UTCL1_ERROR`, `CPC_UTCL1_ERROR`, `CPG_UTCL1_STATUS`, `CPC_UTCL1_STATUS`, `CPF_UTCL1_STATUS`, and `CP_HPD_UTCL1_*`. Common fields cover dequeue requests, ECC, SUA violations, GPF, WRM poll timeouts, privileged instruction/register errors, opcode errors, timestamps, reserved-bit errors, generic interrupts, UTCL1 fault/retry/PRT detection, and VMID/address context for faults.
- CP power, reset, context, and microcode entry controls: `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_IQ_WAIT_TIME1/2`, `CP_CE/PFP/ME/MEC*_PRGRM_CNTR_START`, `CP_CE/PFP/ME/MEC*_INTR_ROUTINE_START`, `CP_CPC_IC_BASE_*`, and `CP_CPC_IC_OP_CNTL`. These encode clock halt bits, memory light/deep sleep knobs, sub-block enables, soft reset selectors, context limits, IQ wait timers, program-counter and interrupt-routine starts, CPC instruction-cache base/VMID/cache policy, and cache invalidate/prime status bits.
- Queue scheduling, priority, and VMID controls: `CP_ME1/ME2_PIPE_PRIORITY_CNTS`, `CP_ME1/ME2_PIPE*_PRIORITY`, `CP_PQ_WPTR_POLL_CNTL`, `CP_PQ_WPTR_POLL_CNTL1`, `CP_PQ_STATUS`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, `CP_MEC1/2_F32_INT_DIS`, `CP_CPC_GFX_CNTL`, `CP_GFX_MQD_CONTROL`, `CP_GFX_MQD_BASE_ADDR*`, `CP_MQD_BASE_ADDR*`, and `CP_MQD_CONTROL`. These describe priority counters, queue masks, write-pointer polling, VMID reset/preempt/status vectors, interrupt-disable bits, graphics queue mapping, and MQD fetch/processing controls.
- SPI arbitration, debug, trap, and resource reservation fields in `gc_spipdec`: `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0/1`, `SPI_CDBG_SYS_GFX`, `SPI_CDBG_SYS_HP3D`, `SPI_CDBG_SYS_CS0/1`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_GDBG_WAVE_CNTL`, `SPI_GDBG_TRAP_CONFIG`, `SPI_GDBG_TRAP_MASK`, `SPI_GDBG_WAVE_CNTL2/3`, `SPI_GDBG_TRAP_DATA0/1`, `SPI_COMPUTE_QUEUE_RESET`, `SPI_RESOURCE_RESERVE_CU_0` through `_15`, `SPI_RESOURCE_RESERVE_EN_CU_0` through `_15`, `SPI_COMPUTE_WF_CTX_SAVE`, and `SPI_ARB_CNTL_0`. These fields tune pipeline arbitration, wave limits, compute/debug trap mode, compute queue reset, per-CU reservation of VGPR/SGPR/LDS/waves/barriers, reservation enable/type/queue masks, and compute wavefront context-save status.
- HQD/HPD queue descriptor fields in `gc_cpphqddec`: `CP_HQD_GFX_CONTROL`, `CP_HQD_GFX_STATUS`, `CP_HPD_ROQ_OFFSETS`, `CP_HPD_STATUS0`, `CP_HQD_ACTIVE`, `CP_HQD_VMID`, `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PIPE_PRIORITY`, `CP_HQD_QUEUE_PRIORITY`, `CP_HQD_QUANTUM`, `CP_HQD_PQ_*`, `CP_HQD_IB_*`, `CP_HQD_IQ_*`, `CP_HQD_DEQUEUE_REQUEST`, `CP_HQD_OFFLOAD`, `CP_HQD_SEMA_CMD`, `CP_HQD_MSG_TYPE`, atomic preop registers, HQ scheduler/status/control registers, `CP_HQD_EOP_*`, context-save address/size registers, `CP_HQD_GDS_RESOURCE_STATE`, `CP_HQD_ERROR`, and `CP_HQD_AQL_CONTROL`. These macros define the persistent state and live status for hardware queues, packet queues, indirect buffers, interrupt queues, end-of-pipe queues, context save/restore, GDS resource ownership, AQL controls, and detailed queue error reporting.
- DIDT/CAC/EDC/throttle fields in `gc_didtdec` and `gc_gccacdec`: `DIDT_IND_INDEX`, `DIDT_IND_DATA`, `DIDT_INDEX_AUTO_INCR_EN`, `GC_CAC_CTRL_1/2`, `GC_CAC_AGGR_*`, `PCC_PERF_COUNTER`, `GC_CAC_SOFT_CTRL`, `GC_DIDT_CTRL0/1/2`, `GC_DIDT_WEIGHT`, `GC_EDC_CTRL`, `GC_EDC_THRESHOLD`, `GC_DIDT_DROOP_CTRL*`, `GC_EDC_DROOP_CTRL`, `GC_THROTTLE_CTRL`, and CAC/SE indirect index/data windows. These govern current/activity counter capture, dynamic inductive droop throttling, electrical design current controls, droop thresholds, power weights, PCC throttling, and indirect register access.
- TCP watchpoint/cache fields in `gc_tcpdec`: `TCP_WATCH0-3_ADDR_H`, `TCP_WATCH0-3_ADDR_L`, `TCP_WATCH0-3_CNTL`, and the visible start of `TCP_GATCL1_CNTL`. These describe four texture/cache watchpoint address/mask/VMID/ATC/mode/valid slots and cache behavior flags such as invalidate-all-VMID, force miss, force in-order, and reduced FIFO/cache depth.

Field names are hardware-descriptive. `*_EN` and `*_ENABLE` fields gate behavior, `*_STATUS` fields expose live or sticky status, `*_HIT` and `*_UPDATED` fields report doorbell events, `*_BASE*` and `*_ADDR*` fields carry aligned addresses, `*_HI` fields carry high address bits, `*_RPTR`/`*_WPTR` fields are queue read/write pointers, and full-width `0xFFFFFFFFL` fields usually represent data, counters, indirect windows, or opaque scheduler/control payloads.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is supplied by driver code that includes the GC 9.2.1 offset and shift/mask headers:

1. ASIC-specific driver code selects a register by its `mm*` offset macro.
2. The driver composes or decodes individual fields using the `__SHIFT` and `_MASK` macros from this header.
3. The driver performs MMIO reads or writes through AMDGPU register helpers, often with read-modify-write preservation for unrelated and reserved bits.
4. Hardware blocks, firmware, CP/MEC microcode, RLC, KFD queue management, debug tooling, or power-management flows provide the actual sequencing, polling, reset, and interrupt handling.

The chunk describes fields used in stateful flows such as queue setup, MQD load/processing, doorbell enablement, write-pointer polling, VMID reset/preemption, interrupt enable/status handling, UTCL1 fault diagnosis, compute queue reset, SPI trap/debug control, HQD dequeue/offload/EOP processing, context save/restore, GDS ownership, and DIDT/EDC throttling. It does not encode the legal programming order, required delays, register access type, firmware ownership, or reset/power-gating constraints.

## State And Persistence Behavior

The file stores no software state and performs no persistence. It describes hardware state accessed through GC 9.2.1 registers.

The represented hardware state is highly persistent and live at the device level: ring-buffer bases and pointers, doorbell mappings and hits, interrupt masks and sticky status, ECC first-occurrence metadata, VMID reset/preempt vectors, CP clock/memory sleep controls, MQD/HQD queue descriptors, HQD packet/IB/IQ/EOP pointers, context-save addresses and sizes, GDS resource allocation, SPI wave/debug/trap configuration, per-CU resource reservations, DIDT/EDC/CAC power and throttle settings, and TCP watchpoint controls. Values may survive until changed by the driver, reset by GPU reset, cleared by queue teardown, lost during suspend or power-gating, or advanced asynchronously by hardware.

Many fields in this chunk are not durable configuration values. Doorbell hit bits, queue-active bits, interrupt status bits, fault-detected bits, processing/busy flags, EOP empty/available fields, queue-idle fields, and cache-primed fields can be live, sticky, write-one-to-clear, or self-clearing depending on the hardware definition. Full-width data and indirect windows are especially sensitive because the macro alone does not indicate whether a register is read-only, write-only, latched, indexed, or hardware-owned.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h`, which provides matching register offsets and base indices. The same generated ASIC register database also has enum/default-value material used by nearby GFX9 code.

Known include users in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h`

GC 9.2.1 is also selected through GFX9 ASIC-specific paths such as `gfx_v9_0.c`, which contains Vega12 golden-setting tables and ASIC dispatch. Integration points include GFX hub setup, Vega12 power-management register access, graphics/compute queue initialization, AMDKFD MQD/HQD programming, command processor interrupt handling, GPU reset/recovery, VMID management, doorbell configuration, debug/trap support, profiling or register-dump tooling, and hardware validation scripts.

This chunk is expected to be used with offset macros from the same ASIC generation. Mixing it with another GC 9.x shift/mask or offset header can still compile because names are often similar, but the resulting register writes can target wrong fields or incompatible bit layouts.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong literal in a `__SHIFT` or `_MASK` macro silently changes hardware programming and may only fail on the GC 9.2.1 ASIC or a specific queue/power/debug path.
- Header/offset pairing must stay exact. `gc_9_2_1_sh_mask.h` fields must be paired with `gc_9_2_1_offset.h` offsets, not a neighboring GFX9/GFX10 variant.
- The macros are untyped constants. They do not encode access mode, reset value, W1C behavior, self-clearing behavior, alignment requirements, index/data coupling, firmware ownership, or legal values.
- Queue programming is sequencing-sensitive. Ring bases, RPTR report addresses, WPTR polling addresses, doorbells, PQ/IB/IQ/EOP controls, MQD/HQD active bits, dequeue requests, and context-save controls must be ordered with queue quiesce/load/activate/deactivate flows.
- Interrupt and fault fields are easy to misuse. Enabling CP/CPC/MEC interrupts without clearing or preserving status can cause spurious interrupts, while writing status registers with ordinary masks may clear sticky fault evidence.
- VMID reset/preempt fields are broad bit vectors. A wrong shift or unchecked write can reset or preempt the wrong VMID and affect unrelated processes or queues.
- Power and reset fields can disturb active hardware. `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, DIDT/EDC, and throttle controls interact with clocking, power gating, and running queues.
- Debug/trap/watchpoint fields can perturb workloads. SPI trap mode, compute queue reset, resource reservations, context-save controls, and TCP watchpoints may change scheduling, wave residency, cache behavior, or fault routing.
- Full-width `0xFFFFFFFFL` masks are not automatically safe writes. Several represent opaque scheduler fields, indirect data windows, pointer/data registers, or hardware-owned status payloads.
- Reserved fields appear in control and status registers. Consumers must preserve reserved bits unless the hardware guide explicitly requires writing a value.
- The chunk boundary is artificial. It begins after `CP_FATAL_ERROR` shift definitions from the previous chunk and ends in `TCP_GATCL1_CNTL`; adjacent chunks are required for a complete per-file report.

## Test Signals

Useful validation is mostly build, static, and hardware smoke coverage:

- Build AMDGPU and powerplay paths that include `gc_9_2_1_offset.h` and `gc_9_2_1_sh_mask.h`, especially `gfxhub_v1_1.c`, Vega12 power-management includes, and GFX9 ASIC selection paths.
- Static generated-header checks that every visible `__SHIFT` has a corresponding `_MASK`, every mask is aligned to its shift, and register names match entries in `gc_9_2_1_offset.h`.
- Diff checks against AMD's authoritative GC 9.2.1 register database and neighboring generated GC 9.x headers where register layouts are expected to remain compatible.
- Queue smoke tests that initialize graphics and compute queues, program MQD/HQD state, enable doorbells, submit packets, observe WPTR/RPTR movement, process EOP events, and tear queues down without stuck active/busy/dequeue bits.
- Interrupt and fault tests that enable selected CP/CPC/MEC interrupt sources, trigger controlled doorbell/dequeue/timestamp or error conditions where possible, verify status/context fields, and confirm clear/disable sequencing.
- VMID and preemption tests that exercise VMID reset/preempt/status paths while multiple queues or processes are active, checking that only the intended VMID is affected.
- Reset, suspend/resume, runtime power-management, and GPU recovery tests around CP soft reset, clock halt, memory sleep, MQD/HQD state, doorbell state, and DIDT/EDC/throttle controls.
- Debug/profiling tests for SPI trap controls, compute queue reset, resource reservation fields, wavefront context save, and TCP watchpoints, watching for hangs, false faults, missed traps, or cache/watchpoint misattribution.
- Regression indicators include stuck queue-active or queue-idle bits, doorbell hits not observed, write pointers not polled, spurious CP interrupts, lost ECC/UTCL1 fault context, GPU hangs during queue teardown, unexpected throttling, or failures limited to Vega12/GC 9.2.1 hardware.

### subset-b-002655: lines 14605-17184

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 14605-17184

## Scope

This chunk covers a generated AMD GC 9.2.1 shader/register mask header range. It starts inside the mask half of `TCP_GATCL1_CNTL`, then covers complete TCP UTCL1/perf-counter, GDS, RAS, depth-buffer, rasterizer, viewport, color-buffer, command-processor context, and pixel-shader-input groups through line 17184. The range ends inside `SPI_PS_INPUT_CNTL_18`; the remaining masks for that register continue in the next source lines and must be reconciled by the later merge lane.

The chunk contains 2,139 `#define` macros and 435 comment anchors. The public surface is entirely preprocessor constants, following the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pattern. There are no C functions, structs, enums, or executable statements in this range.

## Purpose

`gc_9_2_1_sh_mask.h` provides compile-time bit positions and masks for GC 9.2.1 graphics-core registers used by the AMDGPU driver and related generated register programming tables. This slice describes several important hardware state domains:

- Texture/cache and VM controls for TCP/GATCL1/UTCL1, including invalidate, force-miss, fault/retry/PRT status, cache size/FIFO throttling, clock gating, GPUVM response behavior, and texture performance-counter filtering.
- Global Data Share (GDS), Global Wave Sync (GWS), and Ordered Append (OA) resource partitioning across VMIDs, plus reset, restore, and context-switch counters.
- RAS signature capture masks for multiple graphics blocks.
- Depth buffer (DB), stencil, HTILE, scissor, viewport, raster configuration, color write-mask, DCC, blend constants, coherent destination, and primitive reset state for the graphics pipeline.
- Pixel shader input-control registers `SPI_PS_INPUT_CNTL_0` through the start of `SPI_PS_INPUT_CNTL_18`, which define attribute offset, defaulting, interpolation, point-sprite, fp16 interpolation, duplicate, and attribute-valid fields.

The header does not decide policy. It encodes the hardware contract that other code uses when composing 32-bit register values from higher-level driver state, firmware tables, or command streams.

## Important API Surface

- `TCP_GATCL1_CNTL` trailing masks include invalidation, force miss, in-order behavior, FIFO-depth reduction, and cache-size reduction bits. Because this chunk starts mid-register, the matching shifts and earlier masks are outside this slice.
- `TCP_GATCL1_DSM_CNTL`, `TCP_CNTL2`, `TCP_UTCL1_CNTL1`, `TCP_UTCL1_CNTL2`, and `TCP_UTCL1_STATUS` describe texture cache/debug controls, clock-disable fields, GPUVM page-size/default permission behavior, invalidation VMID selection/toggle, snooping, forced GPUVM invalidation acknowledgements, and fault/retry/PRT status bits.
- `TCP_PERFCOUNTER_FILTER` and `TCP_PERFCOUNTER_FILTER_EN` define filter criteria and enable bits for texture/perf monitoring: buffer, flat, dimension, data format, numeric format, software mode, sample count, opcode type, GLC/SLC, compression, and address mode.
- The `gc_gdspdec` block defines per-VMID GDS base and size registers for VMIDs 0-15, GWS base/size partitions for VMIDs 0-15, OA masks for VMIDs 0-15, 64 individual GWS resource reset bits split across `GDS_GWS_RESET0` and `GDS_GWS_RESET1`, and targeted reset controls in `GDS_GWS_RESOURCE_RESET`, `GDS_OA_RESET_MASK`, and `GDS_OA_RESET`.
- `GDS_ENHANCE` and `GDS_OA_CGPG_RESTORE` expose control bits for GDS enhancement, clock/power-gating restore, queue identity, ME/pipe identity, and VMID restore state.
- `GDS_CS_CTXSW_STATUS`, `GDS_GFX_CTXSW_STATUS`, and the repeated `GDS_*_CTXSW_CNT0..3` groups expose context-switch read/write status and up/down pointer counters for compute, graphics, VS, PS0-PS7, and GS domains.
- The `gc_rasdec` block contains signature control/mask registers and signature result fields for SX, DB, PA, VGT, SQ, SC0-7, IA, SPI, TA, TD, CB, and BCI units.
- The `gc_gfxdec0` block starts with DB state: `DB_RENDER_CONTROL`, `DB_COUNT_CONTROL`, `DB_DEPTH_VIEW`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, HTILE base/high, depth size/bounds, stencil/depth clear values, `DB_Z_INFO`, `DB_STENCIL_INFO`, read/write base-high pairs, `DB_DFSM_CONTROL`, and EPITCH helpers in `DB_Z_INFO2` and `DB_STENCIL_INFO2`.
- Scissor and viewport registers include screen, window, generic, clip-rect, and 16 viewport scissor pairs; each top-left register can include a `WINDOW_OFFSET_DISABLE` bit while coordinates are split across low/high halfwords.
- Viewport depth and clip transform state includes `PA_SC_VPORT_ZMIN_0..15`, `PA_SC_VPORT_ZMAX_0..15`, `PA_CL_VPORT_X/Y/Z{SCALE,OFFSET}` for viewports 0-15, `PA_CL_UCP_0..5_{X,Y,Z,W}`, and `PA_CL_PROG_NEAR_CLIP_Z`.
- Raster and routing controls include `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_SCREEN_EXTENT_CONTROL`, `PA_SC_TILE_STEERING_OVERRIDE`, grid registers, `PA_SC_EDGERULE`, and `PA_SU_HARDWARE_SCREEN_OFFSET`.
- Command processor context fields include `CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, and `CP_VMID`.
- Color/depth integration fields include `CB_TARGET_MASK`, `CB_SHADER_MASK`, `CB_BLEND_{RED,GREEN,BLUE,ALPHA}`, `CB_DCC_CONTROL`, `DB_STENCIL_CONTROL`, `DB_STENCILREFMASK`, and `DB_STENCILREFMASK_BF`.
- `SPI_PS_INPUT_CNTL_0` through the partial `SPI_PS_INPUT_CNTL_18` expose repeated per-attribute shader input routing fields: `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `CYL_WRAP`, `PT_SPRITE_TEX`, `DUP`, `FP16_INTERP_MODE`, `USE_DEFAULT_ATTR1`, `DEFAULT_VAL_ATTR1`, `PT_SPRITE_TEX_ATTR1`, and attribute-valid bits. The chunk stops after `SPI_PS_INPUT_CNTL_18__USE_DEFAULT_ATTR1_MASK`.

## Control Flow

There is no direct control flow in this header. Runtime flow is in consumers that include this generated mask file:

1. Pick a register address from the companion GC 9.2.1 address header.
2. Derive a 32-bit value from higher-level driver state.
3. Shift each field using `REGISTER__FIELD__SHIFT`.
4. Mask or replace fields using `REGISTER__FIELD_MASK`.
5. Emit the resulting register value through MMIO writes, PM4 packets, context/clear-state restore, golden-register programming, performance-counter setup, or debug decode paths.

The repeated families strongly suggest table-driven or looped consumers: VMID-indexed GDS/GWS/OA allocation, viewport-indexed scissor and clip transform programming, PS-stage repeated context counters, and pixel-shader input control for up to at least 19 attributes in this chunk.

## State and Persistence

The macros themselves are stateless and are resolved at compile time. The underlying registers they describe are persistent GPU state:

- TCP and UTCL1 fields persist until explicitly reprogrammed or reset. Incorrect invalidation, fault-response, cache-reduction, or snoop fields can affect texture cache behavior, GPUVM fault handling, and performance-counter visibility across subsequent work.
- GDS/GWS/OA allocation registers persist per VMID and resource slot. Context-switch status/counter registers represent live engine state and may be used during save/restore or debug flows.
- RAS signature registers are persistent diagnostic state for error detection, logging, or signature comparison. Consumers must preserve expected mask/control behavior when enabling or reading signatures.
- DB and CB registers persist as graphics context state. Depth/stencil metadata bases, HTILE bases, depth/stencil read/write bases, coherent destination bases, and DCC controls describe GPU memory surfaces and metadata.
- PA scissor, viewport, clip, edge, grid, and raster configuration state persists across draws until the command stream changes it. Bad values can clip all primitives, corrupt viewport transforms, or route screen tiles to the wrong backend.
- `SPI_PS_INPUT_CNTL_*` values are part of the shader ABI between compiler-selected PS inputs and hardware interpolation/routing. They must match the compiled shader's expected attribute layout.

Because this file provides constants only, all validation of field ranges, alignment, register sequencing, and hardware generation compatibility must happen outside the header.

## Dependencies and Integration Points

- Depends on the generated AMD GC 9.2.1 register specification. The masks must remain synchronized with companion address and offset headers in `drivers/gpu/drm/amd/include/asic_reg/gc/`, especially the matching `gc_9_2_1_d.h` style address definitions.
- Integrated by AMDGPU SOC15/GC register programming code, command submission paths, golden-register tables, clear-state/context-state restore paths, perf-counter setup, RAS diagnostics, and debug register decoders.
- Ties directly to GPUVM and memory-management code where base/high fields such as `DB_HTILE_DATA_BASE(_HI)`, `DB_Z_READ_BASE(_HI)`, `DB_STENCIL_READ_BASE(_HI)`, `DB_Z_WRITE_BASE(_HI)`, `DB_STENCIL_WRITE_BASE(_HI)`, `TA_BC_BASE_ADDR(_HI)`, and `COHER_DEST_BASE*` are populated from GPU addresses.
- Bridges graphics API state to hardware: viewport arrays, scissors, clip planes, depth/stencil clears, depth bounds, stencil operations, color write masks, blend constants, primitive restart index, and pixel shader input interpolation all eventually depend on these bit definitions.
- The `CP_*` context identifiers integrate with command processor queue/ring/VMID attribution and performance monitoring.
- The GDS/GWS/OA sections integrate with compute and graphics queue resource management, VMID partitioning, context switching, and reset/restore sequencing.

## Risks

- Bitfield drift is the main risk. If any mask or shift differs from the GC 9.2.1 hardware specification or the companion address header, consumers will silently program wrong bits.
- The chunk has boundary-partial registers. `TCP_GATCL1_CNTL` is only represented by trailing masks here, and `SPI_PS_INPUT_CNTL_18` is missing its final masks in this range. Merge tooling should avoid treating either as fully documented by this chunk alone.
- Repeated indexed families are copy/paste sensitive. Off-by-one use in `GDS_VMIDn_*`, `GDS_GWS_VMIDn`, `GDS_OA_VMIDn`, `PA_SC_VPORT_SCISSOR_n`, `PA_SC_VPORT_ZMIN/ZMAX_n`, `PA_CL_VPORT_*_n`, or `SPI_PS_INPUT_CNTL_n` can alter the wrong VMID, viewport, or shader input.
- Address-bearing DB/TA/coherency fields have high blast radius. Wrong base/high fields or alignment assumptions can cause GPUVM faults, metadata corruption, or writes to the wrong depth/stencil/coherency surface.
- TCP/UTCL1 invalidation and fault-response fields are low-level cache/VM controls. Incorrect programming can hide faults, force excessive misses, create stale translations, or distort performance-counter results.
- GDS/GWS/OA reset and allocation masks can disrupt synchronization or append resources for unrelated queues if VMID/resource identity is wrong.
- DB override and compression bits such as force dirty/valid, preserve compression, decompress-on-flush, clear-disallowed, allow expclear, HTILE, DCC, and stencil/depth compression flags are visually and correctness sensitive.
- Raster configuration and tile steering fields are ASIC-topology sensitive. Incorrect values can send work to invalid shader engines/render backends or cause subtle load-balancing and rendering failures.
- Pixel shader input controls must match compiler/driver ABI expectations. Incorrect `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `CYL_WRAP`, `PT_SPRITE_TEX`, fp16 interpolation, or validity bits can produce wrong interpolants without an obvious kernel-side failure.

## Test Signals

- Build coverage: compiling AMDGPU with this header included catches malformed macros, duplicate definitions, missing guards, and preprocessing errors.
- Generated-header consistency: compare this range against the GC 9.2.1 source register database and the matching address header to confirm all `__SHIFT` and `_MASK` pairs, field widths, and boundary registers.
- Register decode validation: decode known-good command streams or register dumps using these masks for `TCP_UTCL1_*`, `GDS_*`, `DB_*`, `PA_SC_*`, `PA_CL_*`, `CB_*`, and `SPI_PS_INPUT_CNTL_*` and compare against expected state.
- GPUVM/cache smoke tests: run texture-heavy workloads, page-fault/PRT scenarios, and perf-counter collection while checking for VM faults, stale data, unexpected retries, or counter filter mismatches.
- GDS/GWS/OA stress: run compute and graphics workloads that use GDS, ordered append, wave synchronization, queue context switching, reset paths, and multi-VMID scheduling.
- RAS diagnostics: exercise RAS signature enable/read paths and verify stable signatures or expected error reporting on supported GC 9.2.1 hardware.
- Graphics conformance: Vulkan/OpenGL CTS coverage for depth/stencil clears and tests, depth bounds, HTILE/compression paths, stencil front/back operations, scissor and viewport arrays, clip planes, primitive restart, color write masks, blend constants, DCC behavior, point sprites, flat shading, and shader interpolation should exercise the main register surfaces in this chunk.
- Runtime monitoring: run display plus 3D workloads on GC 9.2.1 hardware and watch for GPU hangs, RAS events, VM faults, rendering corruption, or golden-register mismatches.

### subset-b-002656: lines 17185-19585

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 17185-19585

## Scope

This chunk covers a generated section of the AMD GC 9.2.1 shader/register mask header. It starts in the `SPI_PS_INPUT_CNTL_18`/`SPI_PS_INPUT_CNTL_19` area and ends at the `CB_COLOR2_BASE` comment, before the field definitions for color target 2 continue in the next chunk.

The range defines preprocessor constants only. There are no C functions, structs, variables, memory allocations, or runtime branches in this chunk. Every meaningful item is a register-field pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose that field.

## Purpose

The purpose of this header slice is to encode the GC 9.2.1 graphics pipeline register ABI for shader input interpolation, shader exports, blend and render-target state, depth/stencil state, primitive assembly, tessellation/geometry state, streamout, rasterization, and the first color-buffer target descriptors. AMDGPU code uses these definitions with the matching register-address header and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and packet-building paths that write context registers.

This chunk is therefore compile-time metadata for MMIO/packet register programming. The behavior belongs to the hardware blocks and to the AMDGPU code that consumes these masks.

## Important Macro Families

### SPI Pixel Shader Inputs and Exports

The chunk begins in the repeated `SPI_PS_INPUT_CNTL_n` family, covering `SPI_PS_INPUT_CNTL_19` through `SPI_PS_INPUT_CNTL_31` after the tail of input control 18. These registers map pixel-shader parameters and interpolation behavior. Fields include `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `CYL_WRAP` where present, point-sprite texture controls, duplicate/FP16 interpolation controls, default-attribute controls, and attribute-valid bits.

The later SPI registers describe shader-stage export and pixel-shader input requirements:

- `SPI_VS_OUT_CONFIG` exposes vertex-shader export count and half-pack behavior.
- `SPI_PS_INPUT_ENA` and `SPI_PS_INPUT_ADDR` describe which perspective, linear, position, front-face, ancillary, sample coverage, and fixed-point inputs are enabled and addressable.
- `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, and `SPI_BARYC_CNTL` configure flat shading, point-sprite override, interpolation count, off-chip parameter behavior, barycentric center/centroid policy, position-float location, and front-face bit export.
- `SPI_TMPRING_SIZE`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT` define temporary-ring sizing and position/Z/color export formats.

### SX and CB Blend State

The SX block controls color export conversion and blend optimization:

- `SX_PS_DOWNCONVERT` packs downconvert modes for MRT0 through MRT7.
- `SX_BLEND_OPT_EPSILON` packs per-MRT epsilon selections.
- `SX_BLEND_OPT_CONTROL` has per-MRT color/alpha optimization disable bits plus `PIXEN_ZERO_OPT_DISABLE`.
- `SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT` expose color and alpha source/destination optimization choices and combine functions.

The CB blend-control family then provides per-render-target blend equations:

- `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL` share the same layout: color source blend, color combine function, color destination blend, alpha source blend, alpha combine function, alpha destination blend, separate-alpha enable, blend enable, and ROP3 disable.
- `CB_MRT0_EPITCH` through `CB_MRT7_EPITCH` expose per-MRT `EPITCH`.
- `CB_COLOR_CONTROL` later in the chunk controls color-buffer mode, ROP3, degamma, and dual-quad behavior.

### Copy State, Draw Initiation, and Index DMA

`CS_COPY_STATE` and `GFX_COPY_STATE` define small source-state IDs for copying pipeline state. The VGT draw/index path includes:

- `VGT_DMA_BASE_HI`, `VGT_DMA_BASE`, `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, `VGT_DMA_INDEX_TYPE`, and `VGT_DMA_NUM_INSTANCES`, which describe indexed-draw buffer base, size, maximum size, index type, swap/buffer type, request policy, primitive-generation enable, not-EOP behavior, request path, and instance count.
- `VGT_DRAW_INITIATOR`, with source select, major mode, sprite enable, not-EOP, opaque draw, unrolled instance, GRBM skew behavior, and render-target index fields.
- `VGT_IMMED_DATA`, `VGT_EVENT_ADDRESS_REG`, `VGT_EVENT_INITIATOR`, and `VGT_DMA_EVENT_INITIATOR`, which pack immediate draw/event payloads and event address high/low fields.

### Depth, Stencil, EQAA, and Shader DB Controls

Depth-buffer state in this chunk includes:

- `DB_DEPTH_CONTROL`, covering stencil enable, Z enable/write enable, depth bounds, Z compare function, backface enable, front/back stencil functions, and color-write behavior on depth pass/fail.
- `DB_EQAA`, with anchor sample, pixel-shader iteration sample, mask export sample, alpha-to-mask sample, intersection, interpolation, static association, overrasterization, and post-Z overrasterization controls.
- `DB_SHADER_CONTROL`, with Z/stencil export enables, Z order, kill, coverage-to-mask, mask export, hierarchical fail/no-op execution, alpha-to-mask disable, depth-before-shader, conservative-Z export, dual-quad disable, primitive ordered pixel shader, overlap execution, and overlap sample count fields.
- `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0`, `DB_SRESULTS_COMPARE_STATE1`, and `DB_PRELOAD_CONTROL`, which define HTILE preload/cache/alignment behavior, shader-results compare tests, and preload window coordinates.
- `DB_ALPHA_TO_MASK`, defining alpha-to-mask enable, four offsets, and offset rounding.

### PA Clip, Setup, Rasterization, and AA State

The PA register families define viewport transform, clipping, culling, primitive setup, rasterizer, antialiasing, centroid, and conservative-raster state:

- `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, and `PA_CL_NANINF_CNTL` cover user clip planes, clip/cull distance exports, viewport scale/offset enables, clip-space policy, rasterization kill, Z clip disable/programmed near, vertex-output side-band enables, and NaN/Inf handling.
- `PA_SU_SC_MODE_CNTL`, `PA_SU_LINE_STIPPLE_CNTL`, `PA_SU_LINE_STIPPLE_SCALE`, `PA_SU_PRIM_FILTER_CNTL`, `PA_SU_SMALL_PRIM_FILTER_CNTL`, `PA_SU_OVER_RASTERIZATION_CNTL`, `PA_SU_POINT_SIZE`, `PA_SU_POINT_MINMAX`, `PA_SU_LINE_CNTL`, `PA_SU_VTX_CNTL`, and polygon-offset registers define culling, face selection, polygon mode, polygon offset, line/point dimensions, line stipple, primitive filtering/expansion, small-primitive filtering, overrasterization, and vertex control.
- `PA_SC_MODE_CNTL_0`, `PA_SC_MODE_CNTL_1`, `PA_SC_LINE_STIPPLE`, `PA_SC_CENTROID_PRIORITY_0/1`, `PA_SC_LINE_CNTL`, `PA_SC_AA_CONFIG`, the `PA_SC_AA_SAMPLE_LOCS_PIXEL_*` families, `PA_SC_AA_MASK_*`, `PA_SC_SHADER_CONTROL`, `PA_SC_BINNER_CNTL_0/1`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, and `PA_SC_NGG_MODE_CNTL` describe scan-converter MSAA, viewport scissor, tile/supertile walk, out-of-order primitive handling, centroid priorities, AA sample locations and masks, binning, conservative rasterization, shader quad realignment/collision diagnostics, and NGG deallocation limits.

### VGT Tessellation, Geometry, Primitive ID, and Streamout

The VGT definitions cover vertex/geometry/tessellation topology and streamout:

- `VGT_OUTPUT_PATH_CNTL`, `VGT_HOS_CNTL`, `VGT_HOS_MAX_TESS_LEVEL`, `VGT_HOS_MIN_TESS_LEVEL`, `VGT_HOS_REUSE_DEPTH`, `VGT_TESS_DISTRIBUTION`, `VGT_LS_HS_CONFIG`, and `VGT_TF_PARAM` configure tessellation mode, levels, reuse depth, distribution, patch/control-point counts, partitioning, topology, donut-disable, request policy, and distribution mode.
- `VGT_GROUP_PRIM_TYPE`, `VGT_GROUP_FIRST_DECR`, `VGT_GROUP_DECR`, `VGT_GROUP_VECT_0/1_CNTL`, and `VGT_GROUP_VECT_0/1_FMT_CNTL` describe grouped primitive/component packing, retained ordering/quads, component enables, stride/shift, conversion, and offsets.
- `VGT_GS_MODE`, `VGT_GS_ONCHIP_CNTL`, `VGT_GS_PER_ES`, `VGT_ES_PER_GS`, `VGT_GS_PER_VS`, `VGT_GSVS_RING_OFFSET_1/2/3`, `VGT_GS_OUT_PRIM_TYPE`, `VGT_ESGS_RING_ITEMSIZE`, `VGT_GSVS_RING_ITEMSIZE`, `VGT_GS_MAX_PRIMS_PER_SUBGROUP`, `VGT_GS_MAX_VERT_OUT`, `VGT_GS_VERT_ITEMSIZE*`, and `VGT_GS_INSTANCE_CNT` configure geometry-shader mode, cut behavior, on-chip mode, ring sizing/offsets, output primitive type per stream, subgroup sizing, vertex item sizes, and GS instancing.
- `VGT_SHADER_STAGES_EN` enables LS/HS/ES/GS/VS stage combinations, dispatch draw, deallocation accumulators, VS wave IDs, primitive generation, ordered ID mode, maximum primitive groups per wave, and GS fast launch.
- `VGT_PRIMITIVEID_EN`, `VGT_PRIMITIVEID_RESET`, `VGT_DRAW_PAYLOAD_CNTL`, `VGT_DISPATCH_DRAW_INDEX`, `VGT_INSTANCE_STEP_RATE_0/1`, `VGT_REUSE_OFF`, `VGT_VTX_CNT_EN`, `VGT_VERTEX_REUSE_BLOCK_CNTL`, and `VGT_OUT_DEALLOC_CNTL` control primitive-ID generation/reset, draw payload fields, dispatch index matching, instance stepping, vertex reuse, vertex count enable, reuse depth, and output deallocation distance.
- `VGT_STRMOUT_BUFFER_SIZE_0..3`, `VGT_STRMOUT_VTX_STRIDE_0..3`, `VGT_STRMOUT_BUFFER_OFFSET_0..3`, `VGT_STRMOUT_DRAW_OPAQUE_*`, `VGT_STRMOUT_CONFIG`, and `VGT_STRMOUT_BUFFER_CONFIG` define streamout buffer sizes, strides, offsets, opaque draw counters/stride, stream enables, raster stream, primitives-needed count, and per-stream buffer enables.

### Color Target Descriptor State

The chunk ends in the color target descriptor families:

- `CB_COLOR0_BASE`, `CB_COLOR0_BASE_EXT`, `CB_COLOR0_ATTRIB2`, `CB_COLOR0_VIEW`, `CB_COLOR0_INFO`, `CB_COLOR0_ATTRIB`, `CB_COLOR0_DCC_CONTROL`, `CB_COLOR0_CMASK`, `CB_COLOR0_CMASK_BASE_EXT`, `CB_COLOR0_FMASK`, `CB_COLOR0_FMASK_BASE_EXT`, `CB_COLOR0_CLEAR_WORD0/1`, `CB_COLOR0_DCC_BASE`, and `CB_COLOR0_DCC_BASE_EXT`.
- The same family for color target 1: `CB_COLOR1_*`.
- The range reaches the `CB_COLOR2_BASE` comment but not its field definitions.

These registers encode base addresses, address extensions, mip dimensions, slice view, format/number type/component swap, fast clear, compression, blend options, FMASK/DCC enablement, CMASK address type, resource type, sample/fragment counts, swizzle modes, alignment flags, DCC block sizing, lossy precision, constant encode controls, metadata bases, and clear words.

## Control Flow and State Behavior

There is no control flow in this header chunk. Its effect is indirect: C code includes the macros and uses them to compose 32-bit values for hardware context registers, command packets, or MMIO writes.

The state represented here is persistent hardware pipeline state until overwritten by command submission, context restore, reset, suspend/resume reinitialization, or firmware-managed sequencing. Important persistent state includes PS input interpolation mappings, shader export formats, blend equations and optimization choices, depth/stencil/alpha-to-mask behavior, clip/raster/MSAA state, tessellation and geometry-shader topology, streamout buffer configuration, draw/index DMA controls, and CB color target descriptors including DCC/CMASK/FMASK metadata addresses.

Some fields are action/event payloads rather than long-lived mode state. Examples include `VGT_EVENT_INITIATOR`, `VGT_DMA_EVENT_INITIATOR`, `VGT_DRAW_INITIATOR`, `VGT_IMMED_DATA`, and `VGT_PRIMITIVEID_RESET`. Consumers must follow the sequencing and packet rules in the caller and hardware specification; the mask header only supplies field positions.

## Dependencies and Integration Points

This file depends on the generated AMD register-header convention:

- `gc_9_2_1_offset.h` supplies the register addresses and base indices corresponding to these field names.
- `gc_9_2_1_default.h` supplies reset/default values where generated.
- AMDGPU helper macros and PM4 packet-building paths consume the `__SHIFT` and `_MASK` values.

Integration points are broad because these are core graphics context registers:

- RadeonSI/AMDGPU user-mode command streams and kernel validation paths ultimately program these graphics context registers through PM4 packets.
- Kernel GFX initialization and resume/reset paths include GC-family headers to restore safe defaults and ring state.
- KFD/GFX compute and dispatch paths may interact with shared draw/dispatch, shader-stage, scratch, and export state where graphics and compute register programming overlap.
- Display and render tests exercise CB/DB/SX/SPI/PA/VGT behavior indirectly through real rendering workloads.
- The merge lane should connect this chunk with preceding `SPI_PS_INPUT_CNTL_*` definitions and following `CB_COLOR2_*` through later color-target families for a complete per-file view.

## Risks

- A wrong shift or mask can silently program the wrong bit field in hardware. In this chunk that can produce incorrect interpolation, broken shader exports, bad blend/depth results, rendering corruption, GPU hangs, or lost streamout data.
- Repeated families are vulnerable to mechanical drift. `SPI_PS_INPUT_CNTL_n`, `SX_MRTn_BLEND_OPT`, `CB_BLENDn_CONTROL`, streamout buffer `0..3`, AA sample-location registers, and `CB_COLORn_*` families are similar but not always globally complete within this chunk.
- Color target fields are address- and compression-sensitive. Incorrect base, base extension, DCC/CMASK/FMASK, swizzle, alignment, sample count, fragment count, or clear-word masks can corrupt render-target memory or metadata.
- DB and PA state affects API-visible correctness. Incorrect depth/stencil compare, alpha-to-mask, conservative rasterization, sample locations, centroid priority, polygon offset, clip, or NaN/Inf handling can create subtle conformance failures.
- VGT stage and geometry/tessellation fields are topology-sensitive. Incorrect ring item sizes, subgroup limits, shader-stage enables, primitive-ID behavior, or streamout strides can break specific pipeline combinations while simpler draws still pass.
- The chunk begins and ends mid-family. Any final per-file report must avoid treating this chunk as the complete source of `SPI_PS_INPUT_CNTL_*` or `CB_COLOR*` state.

## Test and Validation Signals

Useful validation is mostly build and hardware/integration coverage:

- Compile AMDGPU and KFD code that includes `gc/gc_9_2_1_sh_mask.h`; this catches missing or renamed macros and malformed preprocessor definitions.
- Run graphics conformance or piglit/deqp-style rendering tests that cover interpolation qualifiers, point sprites, flat shading, FP16 interpolation, shader position/Z/color export formats, and clip/cull distance outputs.
- Exercise blend, ROP, alpha-to-coverage, MRT, DCC, CMASK/FMASK, fast-clear, and render-target format tests to validate SX/CB field usage.
- Run depth/stencil, EQAA/MSAA, conservative rasterization, polygon offset, small-primitive filtering, line stipple, sample-location, and centroid tests to validate DB/PA/SC programming.
- Exercise tessellation, geometry shader, NGG-adjacent, primitive ID, instancing, indirect/indexed draw, and streamout workloads to validate VGT field composition.
- Reset, suspend/resume, and GPU recovery tests should verify that saved/restored context registers using these masks return the device to a valid graphics state.

### subset-b-002657: lines 19586-22303

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

### subset-b-002658: lines 22304-24747

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 22304-24747

## Scope

This chunk covers generated shift and mask macros from the AMD GC 9.2.1 register mask header. It starts in the `gc_perfsdec` address block at command-processor performance counter selectors and continues through graphics block performance selectors, RLC streaming performance monitor fields, ATC/VM L2 performance counter control, and the first large part of the `gc_rlcpdec` RLC control/status block. The slice ends at `RLC_PG_DELAY_3`, immediately before subsequent RLC SRM/GPM fields in the next chunk.

The file is a pure C preprocessor hardware register description. It defines no functions, structs, globals, persistence containers, or executable control flow. Each register field is represented by the generated pair `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

## Purpose

These macros are the bitfield ABI between AMDGPU driver code and GC 9.2.1 hardware registers. The paired `gc_9_2_1_offset.h` header provides register addresses such as `mmRLC_CNTL`, `mmRLC_SAFE_MODE`, and other GC register offsets; this file provides field offsets and masks used by helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

For this specific range, the primary purpose is to support:

- Selection and mode programming for graphics pipeline performance counters.
- Command processor and RLC performance-monitor state control.
- RLC SPM ring-buffer configuration and sample mux programming.
- UTCL2/VM L2 performance counter configuration/result behavior.
- RLC firmware enable, safe-mode entry, status polling, timers, clock counts, clock gating, power gating, CU load balancing, SERDES access, scratch/general registers, and SMU-facing control messages.

## Important Macro Families

### Graphics and Command Processor Performance Counters

The chunk begins with `CPF_PERFCOUNTER*`, `CPC_PERFCOUNTER*`, `CPG_PERFCOUNTER*`, and `CP_PERFMON_CNTL`. These fields choose counter events (`CNTR_SEL*`), SPM mode, counter mode, global perfmon state, and sample enable state. Window and latency selectors such as `CPF_TC_PERF_COUNTER_WINDOW_SELECT`, `CPG_TC_PERF_COUNTER_WINDOW_SELECT`, and `CPF/CPG/CPC_LATENCY_STATS_SELECT` add index, clear, always, and enable fields for more constrained measurement windows.

Most graphics front-end and shader/backend blocks then expose regular selector groups:

- `GRBM_PERFCOUNTER0/1_SELECT` and `GRBM_SE0..SE3_PERFCOUNTER_SELECT` include event selector fields plus many per-block busy/clean user-defined mask bits for DB, CB, VGT, TA, SX, SPI, SC, PA, GRBM, CP, IA, GDS, BCI, RLC, TC, WD, UTCL2, EA, and RMI.
- `WD`, `IA`, `VGT`, `PA_SU`, `PA_SC`, `SPI`, `SQ`, `SX`, `GDS`, `TA`, `TD`, `TCP`, `TCC`, `TCA`, `CB`, `DB`, and `RMI` counter selectors provide `PERF_SEL` or `CNTR_SEL` fields plus mode fields. The repeated `*_SELECT1` registers extend packed selector slots for additional events.
- `SQ_PERFCOUNTER0_SELECT` through `SQ_PERFCOUNTER15_SELECT` are especially dense: each has SIMD-mask, SQC bank mask, CNTR mode, and performance mode fields. `SQ_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_MASK`, and `SQ_PERFCOUNTER_CTRL2` add wave/bank masking and counter arbitration/control.
- `CB_PERFCOUNTER_FILTER` is filter-oriented rather than only selector-oriented. It carries fields for operation, format, clear, MRT, sample-count, and fragment-count filtering.
- `RMI_PERF_COUNTER_CNTL` adds transaction/event/TC enable selection, window masks, CID/VMID filters, burst length threshold, soft reset, and SPM selection.

These macros are consumed by profiling, debug, and performance-monitor setup code. Event IDs and sequencing are hardware-defined; the header only describes how to place those values into 32-bit registers.

### Draw Object and Draw Window Control

`CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_MASK_HI`, `CP_DRAW_WINDOW_HI`, `CP_DRAW_WINDOW_LO`, and `CP_DRAW_WINDOW_CNTL` describe command-processor draw filtering/window registers. They expose object IDs, object counts, high/low window bounds, and disables for individual low/high window comparisons. These fields are relevant to draw-window scoped perf/debug collection.

### RLC Streaming Performance Monitor

`RLC_SPM_PERFMON_CNTL` controls SPM ring mode and sample interval. `RLC_SPM_PERFMON_RING_BASE_LO/HI`, `RLC_SPM_PERFMON_RING_SIZE`, `RLC_SPM_RING_RDPTR`, `RLC_SPM_PERFMON_SEGMENT_SIZE`, and `RLC_SPM_SEGMENT_THRESHOLD` describe the memory ring and segment layout used for streamed samples.

`RLC_SPM_SE_MUXSEL_ADDR/DATA` and `RLC_SPM_GLOBAL_MUXSEL_ADDR/DATA` provide indirect mux-selection programming windows for shader-engine and global sample sources. Per-block sample delay registers cover CPG, CPC, CPF, CB, DB, PA, GDS, IA, SC, TCC, TCA, TCP, TA, TD, VGT, SPI, SQG, SX, and RMI; each uses an 8-bit delay plus reserved upper bits. `RLC_SPM_PERFMON_SAMPLE_DELAY_MAX` defines the maximum delay field.

`RLC_SPM_MC_CNTL`, `RLC_SPM_INT_CNTL`, and `RLC_SPM_INT_STATUS` later in the chunk connect SPM traffic with memory-client behavior, VMID, policy, memory type override, and interrupt enable/status.

### RLC Local Perfmon and IOV Perf Counters

`RLC_PERFMON_CLK_CNTL_UCODE`, `RLC_PERFMON_CLK_CNTL`, and `RLC_PERFMON_CNTL` expose RLC perfmon clock state, local perfmon state, and sample enable bits. `RLC_PERFCOUNTER0_SELECT` and `RLC_PERFCOUNTER1_SELECT` select RLC-local events.

`RLC_GPU_IOV_PERF_CNT_CNTL`, `RLC_GPU_IOV_PERF_CNT_WR_ADDR/DATA`, and `RLC_GPU_IOV_PERF_CNT_RD_ADDR/DATA` define a small virtual-function performance counter access path. They include enable, mode select, reset, VFID, counter ID, and 4-bit data fields. These are virtualization-sensitive and should be treated as privileged/SR-IOV plumbing rather than normal queue configuration.

### ATC and VM L2 Performance Counters

The chunk transitions into `gc_utcl2_atcl2pfcntldec` for `ATC_L2_PERFCOUNTER0_CFG`, `ATC_L2_PERFCOUNTER1_CFG`, and `ATC_L2_PERFCOUNTER_RSLT_CNTL`. These fields configure ATC L2 event selection, counter mode, compare enable/mask, and result control.

The `gc_utcl2_vml2pldec` block provides `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG` plus `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`. The VM L2 configuration registers share event, counter mode, compare, and compare-mask fields, while result control selects counter ID and behavior for reading/clearing or result handling.

### RLC Core Control, Safe Mode, Timers, and Status

The `gc_rlcpdec` block starts with RLC firmware/core controls:

- `RLC_CNTL` defines RLC enable, force retry, read-cache disable, and step mode.
- `RLC_STAT` exposes aggregate busy state for RLC, SRM, GPM, SPM, MC, and RLC threads 0-2.
- `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, and `RLC_SMU_SAFE_MODE` share command, message, response, and reserved fields. GFX code writes `CMD` and a message value to enter or leave safe mode, then polls `CMD` to clear.
- `SMU_RLC_RESPONSE`, `RLC_SMU_MESSAGE`, `RLC_SMU_GRBM_REG_SAVE_CTRL`, and `RLC_RLCV_COMMAND` are command/response channels between RLC, SMU, and virtualization firmware paths.

Timer and interrupt fields include `RLC_GPM_TIMER_INT_0..3`, `RLC_GPM_TIMER_CTRL`, `RLC_GPM_TIMER_STAT`, `RLC_INT_STAT`, and `RLC_GPM_CP_DMA_COMPLETE_T0/T1`. They describe timer values, enable/synchronized status bits, last CP/RLC interrupt ID, pending interrupt state, and CP DMA completion flags for GPM threads.

Clock/time fields include `RLC_REFCLOCK_TIMESTAMP_LSB/MSB`, `RLC_GPU_CLOCK_COUNT_LSB/MSB`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_CLK_COUNT_GFXCLK_LSB/MSB`, `RLC_CLK_COUNT_REFCLK_LSB/MSB`, `RLC_CLK_COUNT_CTRL`, `RLC_CLK_COUNT_STAT`, `RLC_GPU_CLOCK_32_RES_SEL`, and `RLC_GPU_CLOCK_32`. These back clock-count capture, enable, accumulation, and status reporting.

### RLC Clock Gating, Power Gating, and CU Load Balancing

Power-management fields are a major part of the RLC region:

- `RLC_MEM_SLP_CNTL` controls RLC memory light/deep sleep enables, busy override, and on/off delays.
- `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_RAMP_CTRL` describe medium-grain clock gating, CGCG/CGLS override/enables, idle thresholds, compensation delay, sleep mode, and ramp timing.
- `RLC_PG_CNTL` includes GFX power-gating enable/source, dynamic and static per-CU power gating, pipeline power gating, CP PG disable, SMU slowdown/handshake controls, voltage-reduction handshake control, and reserved fields.
- `RLC_PG_DELAY`, `RLC_PG_DELAY_2`, and `RLC_PG_DELAY_3` define power-up/down, command propagation, memory sleep, SERDES, CGCG/CGPG, and other hysteresis delay fields.
- `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_STATIC_PG_STATUS`, `RLC_CU_STATUS`, `RLC_LB_INIT_CU_MASK`, `RLC_LB_ALWAYS_ACTIVE_CU_MASK`, `RLC_PG_ALWAYS_ON_CU_MASK`, `RLC_MAX_PG_CU`, `RLC_LB_PARAMS`, `RLC_LB_CNTL`, `RLC_LB_CNTR_*`, `RLC_LOAD_BALANCE_CNTR`, and `RLC_THREAD1_DELAY` describe per-CU power state, pending work, load-balancing masks/counters, sampling, and idle-delay tuning.
- `RLC_AUTO_PG_CTRL` coordinates automatic power gating, GRBM register save on idle, auto wakeup, and thresholds.

Cross-generation AMDGPU GFX code uses these exact macro families to enable/disable RLC, enter safe mode before changing clock/power state, program CGCG/CGLS thresholds, and toggle GFX power-gating bits. For GC 9.2.1, the mask definitions are included directly by `amdgpu/gfxhub_v1_1.c` and by Vega12 power-management include plumbing via `pm/powerplay/hwmgr/vega12_inc.h`.

### RLC GPM, SERDES, Scratch, and General Registers

`RLC_GPM_THREAD_RESET`, `RLC_GPM_THREAD_PRIORITY`, `RLC_GPM_THREAD_ENABLE`, and the large `RLC_GPM_STAT` register expose GPM thread reset, priority, enable, busy/wait state, sleep, DMA, interrupt, queue, and scheduling status. `RLC_UCODE_CNTL`, `RLC_FIREWALL_VIOLATION`, `RLC_JUMP_TABLE_RESTORE`, and `RLC_GPM_LOG_SIZE` are firmware/control diagnostics.

SERDES access is represented by `RLC_SERDES_RD_PENDING`, `RLC_SERDES_RD_MASTER_INDEX`, `RLC_SERDES_RD_DATA_0..2`, `RLC_SERDES_WR_CU_MASTER_MASK`, `RLC_SERDES_WR_NONCU_MASTER_MASK`, `RLC_SERDES_WR_NONCU_MASTER_MASK_1`, `RLC_SERDES_WR_CTRL`, `RLC_SERDES_WR_DATA`, `RLC_SERDES_CU_MASTER_BUSY`, `RLC_SERDES_NONCU_MASTER_BUSY`, and `RLC_SERDES_NONCU_MASTER_BUSY_1`. These encode CU/non-CU master selection, read data windows, write/read command bits, power-up/down command bits, BPM address/data, SRBM override, and busy masks.

`RLC_GPM_GENERAL_0..7`, `RLC_GPM_SCRATCH_ADDR`, and `RLC_GPM_SCRATCH_DATA` provide generic firmware-visible scratch or mailbox-style storage windows. Their state is hardware/firmware state, not software persistence in this header.

## Control Flow and State Behavior

There is no C control flow in this chunk. Runtime behavior is created by driver code that includes this header and writes or reads MMIO registers using the generated constants.

The state described here is persistent hardware state until reset, firmware reinitialization, suspend/resume restore, or another MMIO write changes it. Examples include performance counter event selection, SPM ring base/size and read pointer, VM L2 perf counter configuration, RLC enable state, safe-mode command/response state, timer enables, CG/PG configuration, CU masks, load-balancing counters, SERDES command/busy state, scratch contents, and interrupt/status bits.

Some fields are ordinary configuration bits, while others are command strobes, sticky status, read-only status, or indirect-address/data windows. Examples requiring sequencing include safe-mode `CMD` polling, SPM mux address/data programming, VM/ATC performance counter result control, RLC clock-count capture, GPM thread reset, timer status/enable synchronization, SMU/RLC message exchange, and SERDES read/write command with busy/read-pending checks.

## Dependencies and Integration Points

This chunk depends on the generated GC 9.2.1 register set:

- `gc_9_2_1_offset.h` supplies the matching register offsets.
- Other generated GC headers provide defaults or adjacent bitfields outside this line range.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` naming convention.

Observed integration points in this source tree include:

- `drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c`, which includes `gc/gc_9_2_1_offset.h` and `gc/gc_9_2_1_sh_mask.h` for GC 9.2.1 register field access.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h`, included by Vega12 power, thermal, BACO, and SMU manager code, which brings in the GC 9.2.1 offsets and masks.
- GFX generation code such as `gfx_v9_0.c`, which uses the same RLC macro families to test `RLC_CNTL__RLC_ENABLE_F32_MASK`, issue `RLC_SAFE_MODE` commands, program `RLC_CGCG_CGLS_CTRL`, and coordinate clock/power gating. That code demonstrates the expected sequencing pattern even when the exact include selected for a build depends on ASIC/IP version.
- Profiling/debug paths that configure graphics block performance counters, CP/RLC perfmon state, and SPM streaming buffers.

## Risks

- Bit layout drift between GC revisions is a real risk. The macro names are similar across GC 9, 10, 11, and 12, but field widths and semantics can differ. Code must include the GC 9.2.1 header only for matching hardware.
- Reserved fields are explicitly mapped but should not be programmed with arbitrary nonzero values unless the hardware specification or existing driver sequence requires it.
- RLC safe-mode, SMU message, SERDES, SPM mux, and VM/ATC result-control fields are sequencing-sensitive. Incorrect ordering can leave firmware busy, return stale samples, or hang waiting for a status bit.
- Power-gating and clock-gating fields affect live graphics hardware. Incorrect thresholds, masks, or enable bits can cause hangs, missed wakeups, unstable performance, or broken suspend/resume.
- Performance counter fields often pack multiple event selectors and modes into one register. Using the wrong mask/shift can silently count the wrong event rather than failing visibly.
- SR-IOV/IOV perf counter fields include VFID addressing. Incorrect use can leak, corrupt, or misattribute virtual-function performance state.

## Test Signals

- Build coverage: compile configurations that include `gfxhub_v1_1.c` and Vega12 power-management paths should catch missing or renamed macros.
- Register helper correctness: code using `REG_SET_FIELD`/`REG_GET_FIELD` with these macros should preserve unrelated bits and extract expected values in unit-style register composition tests where available.
- Runtime RLC health: GFX initialization should enable RLC, enter and leave safe mode without timeout, and report sane `RLC_STAT`/`RLC_GPM_STAT` values.
- Clock/power tests: suspend/resume, runtime power management, BACO, and clock-gating/power-gating toggles should not produce GPU resets or timeout waiting for RLC/SMU responses.
- Perf tests: block perf counters, RLC perfmon, SPM ring collection, ATC L2, and VM L2 counters should produce nonzero and stable counts for known workloads and should reset/clear according to result-control programming.
- Virtualization tests: SR-IOV or VF-aware paths should verify VFID counter read/write isolation and correct behavior of RLC GPU IOV perf counter controls.
- Diagnostics: dmesg should remain free of RLC safe-mode timeout, CP/RLC interrupt storm, GPU reset, and SMU response timeout messages when exercising the fields in this chunk.

### subset-b-002659: lines 24748-27129

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 24748-27129

## Scope

This chunk covers a generated AMD GC 9.2.1 shader/register mask header range. It contains 2,176 `#define` macros under 204 register comment anchors. The slice starts at `RLC_GPR_REG1` and moves through RLC scratch, save/restore, SMU, UTCL1, interrupt/status, clock-gating, and low-power controls before entering the `gc_pwrdec` address block for CGTS power-decoder controls. It ends in the shift half of `CGTS_CU14_TCPI_CTRL_REG`, so the adjacent chunk is needed for the remaining masks and later CU power-control definitions.

The file is not executable code. Its public surface is a collection of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` preprocessor constants used with matching register-address definitions elsewhere in the AMDGPU generated register headers.

## Purpose

`gc_9_2_1_sh_mask.h` provides compile-time bitfield positions and masks for AMD GC 9.2.1 graphics-core registers. This chunk focuses on firmware/power-management-facing graphics microcontroller state:

- RLC GPR, GPM, SPM, SRM, RLCV, CSIB, SMU-command, semaphore, interrupt, and GPU-clock-count registers.
- RLC UTCL1/UTCL2 translation controls, status, error reporting, prewalker address/size/trigger controls, and DSM/R2I control words.
- RLC clock-gating and light-sleep controls for 3D, plus deep-sleep busy-mask control.
- `gc_pwrdec` CGTS controls for shader-array power gating, TCC disable masks, readback muxes, and per-CU block override/state controls.

The constants let AMDGPU code build, decode, and validate 32-bit register values without embedding raw bit numbers. For this range, correctness is especially relevant to power gating, firmware save/restore, GPU virtual-memory fault diagnostics, SMU/RLC handshakes, and compute-unit block power-state control.

## Important API Surface

- `RLC_GPR_REG1`, `RLC_GPR_REG2`, `RLC_GPM_GENERAL_8` through `RLC_GPM_GENERAL_15`, and `RLC_R2I_CNTL_0` through `RLC_R2I_CNTL_3` are full-width data registers. Consumers treat them as opaque 32-bit firmware or microcode scratch/control values.
- `RLC_SRM_CNTL`, `RLC_SRM_ARAM_ADDR/DATA`, `RLC_SRM_DRAM_ADDR/DATA`, `RLC_SRM_GPM_COMMAND`, `RLC_SRM_RLCV_COMMAND`, status registers, index-control address/data slots 0-7, and `RLC_SRM_GPM_ABORT` describe the RLC save/restore manager command interface. Key fields include enable, auto-increment, operation, size, start offset, destination memory, FIFO empty/full status, and abort.
- `RLC_CSIB_ADDR_LO/HI` and `RLC_CSIB_LENGTH` expose a command-stream instruction buffer pointer and length split across low/high address fields.
- `RLC_SMU_COMMAND`, `RLC_SMU_ARGUMENT_1` through `_4`, and `RLC_SMU_CLK_REQ` define RLC-to-SMU command and argument payload fields, including a clock-request bit.
- `RLC_CP_SCHEDULERS`, `RLC_CP_EOF_INT`, `RLC_CP_EOF_INT_CNT`, `RLC_SPARE_INT`, `RLC_SPARE_INT_1`, `RLC_RLCV_SPARE_INT`, and `RLC_RLCV_SPARE_INT_1` cover scheduler selection and interrupt status/force/count-like state.
- `RLC_GPM_UTCL1_CNTL_0` through `_2`, `RLC_SPM_UTCL1_CNTL`, and `RLC_PREWALKER_UTCL1_CNTL` share the same UTCL1 policy layout: `XNACK_REDO_TIMER_CNT`, `DROP_MODE`, `BYPASS`, `INVALIDATE`, `FRAG_LIMIT_MODE`, `FORCE_SNOOP`, and `FORCE_SD_VMID_DIRTY`.
- `RLC_UTCL1_STATUS` and `RLC_UTCL1_STATUS_2` provide fault, retry, partial-residency, busy, and stall-on-transaction bits, including UTCL1 IDs for fault/retry/PRT sources. `RLC_SPM_UTCL1_ERROR_*` and `RLC_GPM_UTCL1_TH{0,1,2}_ERROR_*` expose per-thread client-ID and address fields for UTCL1 errors.
- `RLC_PREWALKER_UTCL1_TRIG`, address LSB/MSB, and size LSB/MSB fields describe a prewalk operation with VMID, read/write/execute permissions, prime mode, ready, address, and size fields.
- `RLC_CGCG_CGLS_CTRL_3D`, `RLC_CGCG_RAMP_CTRL_3D`, `RLC_DS_CNTL`, `RLC_LBPW_CU_STAT`, and `RLC_UTCL2_CNTL` define graphics clock-gating/light-sleep behavior, ramp timing, deep-sleep busy masks, live CU status, and UTCL2 no-PTE memory-type handling.
- `CGTS_SM_CTRL_REG`, `CGTS_RD_CTRL_REG`, `CGTS_RD_REG`, `CGTS_TCC_DISABLE`, and `CGTS_USER_TCC_DISABLE` are `gc_pwrdec` shader/tile-cache control and diagnostic registers.
- `CGTS_CU0_*` through the partial `CGTS_CU14_TCPI_CTRL_REG` family provides repeated per-CU power/override control for SP0, LDS/SQ, TA/SQC, SP1, TD/TCPF, and TCPI blocks. Repeated fields include block state bits, `*_OVERRIDE`, `*_BUSY_OVERRIDE`, `*_LS_OVERRIDE`, and `*_SIMDBUSY_OVERRIDE`.

There are no structs, enums, functions, or inline helpers in this chunk. The API is entirely macro names and their numeric shift/mask values.

## Control Flow

There is no direct C control flow in the header. Runtime control flow happens in consumers:

1. Select a GC 9.2.1 register offset from the matching address header.
2. Compose a 32-bit value by shifting caller-selected field values with `REGISTER__FIELD__SHIFT`.
3. Apply `REGISTER__FIELD_MASK` when preserving, clearing, or extracting fields.
4. Write or read the register via SOC15/MMIO accessors, PM4 packets, RLC firmware programming paths, golden-register setup, or debug dumps.

The repeated families imply table-driven callers. SRM index-control address/data slots can be iterated over 0-7; GPM UTCL1 thread controls and errors are indexed over threads 0-2; CGTS per-CU controls are naturally iterated by CU number and sub-block type when power-gating or diagnostic code walks a shader array.

## State and Persistence

The macros are stateless build artifacts, but the hardware registers they describe are persistent GPU state until changed by firmware, driver register programming, power-management transitions, suspend/resume, reset, or context restore.

RLC SRM and RLCV command fields affect firmware-managed save/restore movement between internal memories and destination memory. Incorrect command size, start offset, destination memory, FIFO-status handling, or abort programming can leave RLC state partially saved or restored.

UTCL1/UTCL2 and prewalker controls affect GPU virtual-memory translation behavior for RLC/GPM/SPM/prewalker traffic. XNACK retry timing, bypass/drop/invalidate policy, forced snooping, VMID, access permissions, and address/size fields can persist across diagnostic or firmware operations and influence fault visibility or recovery.

Clock-gating, light-sleep, deep-sleep, and CGTS fields persist as power-management policy. Overrides can force blocks on or off, override busy/light-sleep/SIMD-busy signals, disable TCC slices, or alter sequencing delays. Incorrect persistence here can produce higher idle power, missed power savings, or unstable entry/exit from gated states.

Interrupt, semaphore, scheduler, SMU-command, and GPU-clock-count registers are synchronization state between RLC, CP, SMU, and driver code. Their values may be sampled by firmware or interrupt handlers rather than by ordinary draw/dispatch state emission.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.2.1 register database. The masks in this header must stay synchronized with companion address headers such as `gc_9_2_1_d.h` and neighboring generated `*_sh_mask.h` files under `drivers/gpu/drm/amd/include/asic_reg/gc/`.
- Integrated through AMDGPU SOC15 register access helpers, RLC initialization, power-management setup, SMU/RLC messaging, golden-register tables, debugfs/register dumps, and GPU reset/suspend/resume paths.
- Ties into VM/fault handling through UTCL1 status and error fields, including fault/retry/PRT detection, UTCL1 IDs, client IDs, and prewalker address/permission programming.
- Ties into firmware save/restore through SRM, RLCV, ARAM/DRAM, GPM, and index-control registers.
- Ties into power management through RLC CGCG/CGLS/ramp/deep-sleep controls and `gc_pwrdec` CGTS per-CU block controls.
- Uses plain C preprocessor constants only. Callers must perform all range validation, reserved-bit handling, register-address selection, indexing, sequencing, and read/modify/write locking themselves.

## Risks

- Generated bitfield drift is the main risk. If a mask or shift diverges from the GC 9.2.1 hardware specification or the companion address header, callers silently program the wrong bits.
- This chunk ends mid-register-family at `CGTS_CU14_TCPI_CTRL_REG`. Merge tooling must avoid treating the TCPI CU family or the file-level CGTS coverage as complete from this chunk alone.
- SRM/RLCV command fields have high state-corruption risk because operation, size, offset, destination memory, FIFO, and abort fields control firmware save/restore movement.
- UTCL1 and prewalker fields are sensitive. Bad VMID, permission, address, size, retry, invalidation, or bypass/drop settings can hide VM faults, produce false fault attribution, or destabilize RLC-side memory accesses.
- Power-control overrides can mask real busy/idle state. Incorrect `CGTS_CU*_..._OVERRIDE`, `*_BUSY_OVERRIDE`, `*_LS_OVERRIDE`, or `*_SIMDBUSY_OVERRIDE` usage can cause hangs during power transitions or block expected clock/power gating.
- Repeated per-CU/per-block macros create indexing and copy/paste hazards. A CU index, block name, or high/low half mismatch can affect a different shader block than intended.
- Reserved masks are present but not enforced. Callers that do read/modify/write without preserving reserved bits, or that write reserved bits from stale tables, can trigger hardware-specific behavior.

## Test Signals

- Build coverage: compiling AMDGPU with this generated header catches syntax errors, duplicate definitions, and missing include dependencies.
- Register-generation validation: compare lines 24748-27129 against the GC 9.2.1 register source/spec and matching address header to verify every `__SHIFT` has the expected `_MASK`, bit width, and register association.
- Power-management smoke tests: boot/resume/reset a GC 9.2.1 device and watch for golden-register warnings, RLC/SMU handshake failures, GPU hangs, or elevated idle power after CGCG/CGLS/CGTS programming.
- VM/fault diagnostics: exercise GPUVM fault, retry/XNACK, PRT, and prewalker paths while decoding `RLC_UTCL1_STATUS*` and `RLC_*_UTCL1_*ERROR*` fields with these masks.
- Firmware save/restore validation: stress suspend/resume, GPU reset, power-gating transitions, and RLC firmware reload paths that use SRM/RLCV command/status fields.
- Register-dump validation: decode known-good dumps for `RLC_SRM_*`, `RLC_GPM_UTCL1_CNTL_*`, `RLC_PREWALKER_UTCL1_*`, `RLC_CGCG_*`, `RLC_DS_CNTL`, `CGTS_SM_CTRL_REG`, and representative `CGTS_CU*_CTRL_REG` entries.

### subset-b-002660: lines 27130-29635

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 27130-29635

## Scope

This chunk covers a generated AMD GC 9.2.1 shader/register mask header range. It starts inside the mask definitions for `CGTS_CU14_TCPI_CTRL_REG`, contains complete definitions for many clock-gating, VM, virtualization, microcode, RLC, and GC CAC register groups, and ends inside `GC_CAC_OVRD_TCC` immediately after the `GC_CAC_OVRD_TA` override fields. The range contains 2,152 `#define` macros, including 1,074 `__SHIFT` constants and 1,080 `_MASK` constants, plus register/address-block comment anchors.

## Purpose

`gc_9_2_1_sh_mask.h` provides compile-time bit positions and masks for GC 9.2.1 graphics-core registers used by the AMDGPU kernel driver and Vega12 PowerPlay support. This slice describes fields for shader/graphics clock gating and test overrides, VM and SR-IOV per-VF aperture/ATS controls, privileged command-processor and RLC microcode windows, GPU IOV scheduling/status registers, and graphics-core CAC counters and override selectors.

The file has no executable behavior. Its purpose is to keep C code from embedding raw bit positions when building or decoding hardware register values. Companion offset definitions in `gc_9_2_1_offset.h` provide the matching `mm...` or `ix...` register numbers, and driver code combines those offsets with these masks through SOC15 MMIO helpers, indirect-register helpers, and register-field macros.

## Important API Surface

- `CGTS_CU15_TCPI_CTRL_REG` and the preceding tail of `CGTS_CU14_TCPI_CTRL_REG` define TCPI control, override, busy, load/store, SIMDBUSY, and reserved bits for compute-unit test/clock-control state.
- `CGTT_*_CLK_CTRL`, `CGTX_SPI_DEBUG_CLK_CTRL`, `SQ_*_CLK_CTRL`, `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `DB_CGTT_CLK_CTRL_0`, `CB_CGTT_SCLK_CTRL`, `TCC_CGTT_SCLK_CTRL`, `TCA_CGTT_SCLK_CTRL`, `RMI_CGTT_SCLK_CTRL`, `SE_CAC_CGTT_CLK_CTRL`, `GC_CAC_CGTT_CLK_CTRL`, `GRBM_CGTT_CLK_CNTL`, and `GCEA_CGTT_CLK_CTRL` expose clock-gating delay, hysteresis, soft-stall override, core/group override, RAM FGCG, read/write-clock override, and register override fields for most GC sub-blocks.
- `MC_VM_FB_SIZE_OFFSET_VF0` through `MC_VM_FB_SIZE_OFFSET_VF15` provide per-virtual-function framebuffer size and offset fields. `MC_VM_MARC_BASE_*`, `MC_VM_MARC_RELOC_*`, and `MC_VM_MARC_LEN_*` describe MARC base, relocation, and length windows. `VM_IOMMU_CONTROL_REGISTER`, `VM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`, `VM_PCIE_ATS_CNTL`, and `VM_PCIE_ATS_CNTL_VF_*` define IOMMU and PCIe ATS enable/optimization fields.
- `CP_HYP_*_UCODE_ADDR`, `CP_*_UCODE_DATA`, `CP_ME_RAM_*`, `CP_CE_UCODE_*`, `CP_MEC_ME*_UCODE_*`, and related checksum registers define fields for loading or inspecting PFP, ME, CE, and MEC microcode through hypervisor-visible and normal command-processor windows.
- `GRBM_GFX_INDEX_SR_*`, `GRBM_GFX_CNTL_SR_*`, `GRBM_CAM_*`, and `GRBM_HYP_CAM_*` expose SR selection/data and CAM index/data fields used around graphics register-broadcast, shadowing, or virtualization contexts.
- `RLC_GPU_IOV_*`, `RLC_RLCV_TIMER_*`, `RLC_HYP_SEMAPHORE_*`, `RLC_CLK_CNTL`, and `RLC_GPU_IOV_SDMA*_STATUS/BUSY_STATUS` define SR-IOV scheduling, VF enable/mask, active function, timer interrupt/status, doorbell status/set/clear, scratch, firmware, reset, SDMA, SMU/RLC response, interrupt disable/force, semaphore, and clock-control fields owned by the RLC/virtualization path.
- `GC_CAC_CNTL`, `GC_CAC_OVR_SEL`, `GC_CAC_OVR_VAL`, `GC_CAC_WEIGHT_*`, `GC_CAC_ACC_*`, and `GC_CAC_OVRD_*` define graphics-current/activity counter configuration, per-block signal weights, 32-bit or split 40-bit accumulators, and per-block override select/value fields for BCI, CB, CP, DB, GDS, IA, LDS, PA, PC, SC, SPI, CU, SQ, SX, SXRB, TA, and the beginning of TCC.

There are no C types, functions, structs, or inline helpers in this chunk. The exported interface is the preprocessor namespace of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants.

## Control Flow

There is no direct control flow in the header. Runtime consumers follow a consistent pattern:

1. Select a register offset from `gc_9_2_1_offset.h`, such as `mmCGTT_SPI_PS_CLK_CTRL`, `mmMC_VM_FB_SIZE_OFFSET_VF0`, `mmCP_HYP_PFP_UCODE_ADDR`, or indirect CAC offsets such as `ixGC_CAC_CNTL`.
2. Read or compose a 32-bit register value.
3. Clear or test bits with `REGISTER__FIELD_MASK`.
4. Insert or extract field values by shifting with `REGISTER__FIELD__SHIFT`, commonly through `REG_SET_FIELD` and `REG_GET_FIELD`.
5. Write through SOC15 MMIO helpers, command-processor upload paths, PowerPlay/CGS register helpers, or GC CAC indirect-index/data helpers.

The repeated families imply table-driven or indexed consumers: clock-gating setup can walk many `CGTT_*` registers; SR-IOV code can iterate VF-specific `MC_VM_FB_SIZE_OFFSET_VFn` and `VM_PCIE_ATS_CNTL_VF_n` fields; microcode loaders stream words through address/data windows; CAC/powertune code programs selector, weight, accumulator, and override registers through `mmGC_CAC_IND_INDEX`/`mmGC_CAC_IND_DATA`.

## State and Persistence

The macros are stateless compile-time constants, but they describe persistent GPU hardware state. Register values remain in effect until another driver path, firmware sequence, power transition, virtualization event, GPU reset, or context restore rewrites them.

Clock-gating controls affect live power and timing behavior for SPI, PC, BCI, VGT, IA, WD, PA, SC, SQ, SX, TD, TA, TCP, TCI, GDS, DB, CB, TCC, TCA, CP, CPF, CPC, RLC, RMI, SE CAC, GC CAC, GRBM, and EA blocks. VM and IOMMU fields persist as per-function aperture, relocation, MARC, and ATS state. CP and RLC microcode address/data registers are transient access windows but are part of a persistent firmware-load sequence. GC CAC weight, selector, accumulator, and override registers persist as power/activity telemetry and control state used by power-management code.

The AMDGPU SOC15 layer exposes locked GC CAC indirect accessors in `soc15.c` using `mmGC_CAC_IND_INDEX` and `mmGC_CAC_IND_DATA`, so CAC register programming is serialized at the software access point. The masks in this chunk do not provide locking, validation, range checking, or ordering; those responsibilities belong to the callers.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.2.1 register specification and must remain synchronized with `gc_9_2_1_offset.h`, where this range maps to offsets such as `mmCGTS_CU15_TCPI_CTRL_REG`, `mmCGTT_SPI_PS_CLK_CTRL`, `mmMC_VM_FB_SIZE_OFFSET_VF0`, `mmCP_HYP_PFP_UCODE_ADDR`, `ixGC_CAC_CNTL`, and `ixGC_CAC_OVRD_TA`.
- Included by `amdgpu/gfxhub_v1_1.c` for GC 9.2.1 graphics-hub register access and by `pm/powerplay/hwmgr/vega12_inc.h`, which aggregates Vega12 THM, MP, GC, and NBIO generated register headers for power-management code.
- Integrates with SOC15 register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`.
- CAC registers integrate with indirect access paths in `soc15_gc_cac_rreg()` and `soc15_gc_cac_wreg()` and with PowerPlay/CGS code paths that use `CGS_IND_REG_GC_CAC`.
- VM/IOMMU and per-VF fields integrate with SR-IOV and XGMI/GMC setup code. CP and RLC microcode fields integrate with firmware upload and virtualization sequences in neighboring GFX generations and the same generated register model.

## Risks

- Bitfield drift is the highest risk. If any `__SHIFT` or `_MASK` value diverges from the GC 9.2.1 hardware spec or companion offset header, the driver can silently program the wrong bits.
- The chunk is boundary-partial. It begins after the start of `CGTS_CU14_TCPI_CTRL_REG` and ends before the full `GC_CAC_OVRD_TCC` group, so merge tooling should not treat those two register groups as completely covered here.
- Clock-gating override mistakes can cause power regressions, performance loss, timing-sensitive hangs, or blocks that fail to wake because `SOFT_STALL_OVERRIDE`, `CORE*_OVERRIDE`, `GRP*_OVERRIDE`, `REG_OVERRIDE`, delay, and hysteresis fields are hardware-control bits.
- VM and SR-IOV fields have high isolation risk. Incorrect per-VF framebuffer size/offset, MARC relocation/length, IOMMU, ATS, VF mask, active-function, scheduler, doorbell, or reset fields can break guest isolation, route traffic to the wrong aperture, or cause VM faults.
- Microcode address/data window fields have sequencing risk. Writing the wrong CP/RLC address, checksum, data, or firmware-version field can corrupt firmware loading or leave engines running incompatible code.
- GC CAC weights, accumulators, and overrides affect power telemetry and control decisions. Incorrect selectors or override values can mis-measure block activity, skew power-tuning data, or force activity states that hide real workload behavior.

## Test Signals

- Build coverage: compile AMDGPU with GC 9.2.1/Vega12 support to catch syntax errors, duplicate macros, missing includes, and consumers that expect a different field name.
- Generated-header validation: compare this range against the GC 9.2.1 register source/spec and `gc_9_2_1_offset.h`; verify every field has the intended width, shift, mask, and `mm`/`ix` register pairing.
- Runtime register smoke: boot a Vega12/GC 9.2.1 system, exercise suspend/resume, runtime power management, display plus graphics workloads, and check for GPU hangs, VM faults, bad power-state transitions, or clock-gating warnings.
- Virtualization coverage: on SR-IOV-capable hardware, validate VF framebuffer apertures, ATS/IOMMU behavior, VF scheduling/masks, doorbell status, virtual reset requests, and SDMA busy/status reporting.
- Firmware-path coverage: verify CP/RLC firmware upload, checksum/version programming, and post-load command submission on systems using the hypervisor-visible microcode windows.
- Power/CAC validation: compare GC CAC accumulator readings and Powertune behavior against known-good driver traces, especially `GC_CAC_CNTL`, `GC_CAC_WEIGHT_*`, `GC_CAC_ACC_*`, and `GC_CAC_OVRD_*` accesses through the GC CAC indirect register path.

### subset-b-002661: lines 29636-31186

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 29636-31186

## Scope

This chunk is the final range of the generated GC 9.2.1 shader/register mask header. It starts inside the mask definitions for `GC_CAC_OVRD_TA`, then covers complete register-field mask/shift groups for late GC CAC power-accounting registers, SE CAC indirect controls, SQ wave debug/readback registers, and DIDT/EDC throttling controls. It ends with `DIDT_TCP_EDC_THRESHOLD` and the header's closing `#endif`.

The range contains 1,330 `#define` macros and 212 comment anchors, including three explicit address-block transitions: `secacind`, `sqind`, and `didtind`. The macros are generated-style constants named `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`; there are no C functions, structs, or runtime branches in this slice.

## Purpose

`gc_9_2_1_sh_mask.h` is a hardware contract for AMDGPU GC 9.2.1 register programming. This chunk supplies the bit positions and masks needed to compose, decode, or update 32-bit register values for:

- GC CAC counters and overrides for graphics/cache blocks, including TCC, TCP, TD, VGT, WD, UTCL2 router/VML2/walker, and BCI accumulator groups.
- PCC stall-pattern and throttle pattern registers used by throttling logic.
- SE CAC indirect block controls for selecting and overriding CAC signals per shader engine.
- SQ indirect debug state for wave status, wave mode, trap status, hardware identity, resource allocation, instruction-buffer state, PC/instruction words, TTMP registers, `M0`, `EXEC`, and SQ interrupt words.
- DIDT indirect controls for SQ, DB, TD, and TCP domains, including enable/reset bits, stall/tuning controls, auto-release controls, stall patterns, multi-power-delta scaling, throttle controls, weight tables, EDC controls, EDC stall patterns/delays, event counters, min/max power limits, and EDC thresholds.

The header does not implement policy. Power-management, debug, trap, and register-access code include these constants so they can avoid hard-coded bit numbers when talking to the GPU register file.

## Important API Surface

- The chunk begins boundary-partial with only the two masks for `GC_CAC_OVRD_TA`; the corresponding comment and shifts are in the previous chunk. Complete `GC_CAC_OVRD_*` groups then define `OVRRD_SELECT` and `OVRRD_VALUE` fields for TCC, TCP, TD, VGT, WD, UTCL2 router, UTCL2 VML2, and UTCL2 walker.
- `GC_CAC_WEIGHT_UTCL2_*` registers pack 16-bit signal weights. Router weights cover signals 0-9 across five registers; VML2 and walker weights cover signals 0-4 across three registers each.
- `GC_CAC_ACC_*` registers expose full-width `ACCUMULATOR_31_0` fields for BCI, UTCL2 ATCL2, router slots 0-9, VML2 slots 0-4, and walker slots 0-4. These are telemetry-style fields rather than configuration bitfields.
- `PCC_STALL_PATTERN_*` packs seven 15-bit stall patterns, two per register except the final single-pattern register. `PCC_THROT_REINCR_FIRST_PATN_*` and `PCC_THROT_DECR_FIRST_PATN_*` encode compact first-pattern selections for reincrement and decrement behavior.
- `SE_CAC_CNTL`, `SE_CAC_OVR_SEL`, and `SE_CAC_OVR_VAL` form the `secacind` block. They expose CAC force-disable, threshold, block ID, signal ID, override-select, and override-value fields.
- `SQ_DEBUG_STS_GLOBAL` and `SQ_DEBUG_STS_LOCAL` expose SQ FIFO, busy, interrupt-message, and wave-level status fields.
- `SQ_WAVE_*` registers under `sqind` describe wave readback/debug state: mode bits, status bits, trap status, hardware ID tuple, VGPR/SGPR allocation, LDS allocation, instruction-buffer counters/status, PC, instruction dwords, TTMP0-15, `M0`, and `EXEC_LO/HI`.
- `SQ_INTERRUPT_WORD_*` registers describe auto/common/wave interrupt payload encodings, including thread-trace, timestamp, overflow, SE ID, wave ID, SIMD ID, CU ID, VM ID, privilege, and encoding fields.
- `DIDT_{SQ,DB,TD,TCP}_CTRL0` groups define the primary DIDT enable/reset/clock/stall/tuning/event bits, including `DIDT_CTRL_EN`, `DIDT_CTRL_RST`, `DIDT_STALL_CTRL_EN`, `DIDT_TUNING_CTRL_EN`, `DIDT_STALL_AUTO_RELEASE_EN`, `DIDT_HI_POWER_THRESHOLD`, `DIDT_AUTO_MPD_EN`, `DIDT_STALL_EVENT_EN`, and `DIDT_STALL_EVENT_COUNTER_CLEAR`.
- `DIDT_*_CTRL2`, `DIDT_*_STALL_CTRL`, `DIDT_*_TUNING_CTRL`, `DIDT_*_STALL_AUTO_RELEASE_CTRL`, and `DIDT_*_CTRL3` define power-delta, stall delay, maximum stall, auto-release, throttle-policy, level-combine, stall-select, force-stall, and delay-enable behavior.
- `DIDT_*_STALL_PATTERN_*`, `DIDT_*_MPD_SCALE_FACTOR`, `DIDT_*_THROTTLE_CNTL*`, `DIDT_*_WEIGHT*`, and `DIDT_*_EDC_*` define the table-like data used by DIDT and EDC throttling across SQ, DB, TD, and TCP domains.
- `DIDT_*_STALL_EVENT_COUNTER` registers expose full-width 32-bit event counters for SQ, DB, TD, TCP, and DBR domains. The chunk also defines per-domain `CTRL1` min/max power fields and EDC threshold registers for SQ, DB, TD, and TCP.

There are no local C types or functions. The public API is the preprocessor namespace, used with companion `gc_9_2_1_offset.h` offsets and common AMDGPU register helpers such as `REG_SET_FIELD`, `CGS_WREG32_FIELD_IND`, and indirect DIDT/SQ register accessors in consuming code.

## Control Flow

This header has no executable control flow. Runtime behavior appears in consumers that use the masks:

1. Select an ASIC-appropriate offset from `gc_9_2_1_offset.h`, usually an `ix...` indirect register for `secacind`, `sqind`, or `didtind`.
2. Read the current 32-bit register value if only some fields are being changed.
3. Clear a field with `REGISTER__FIELD_MASK`, shift the new value by `REGISTER__FIELD__SHIFT`, and merge it into the register word.
4. Write the result through the relevant MMIO or indirect-register accessor.
5. For readback/debug paths, mask and shift hardware values to decode wave state, interrupt payloads, CAC accumulators, or DIDT counters.

PowerTune code for nearby GC generations shows the intended pattern: tables list `ixDIDT_*` offsets together with `DIDT_*__FIELD_MASK`, `DIDT_*__FIELD__SHIFT`, and programmed values; enable/disable paths use indirect DIDT writes to toggle `DIDT_CTRL_EN`, `EDC_EN`, and `EDC_SW_RST`. SQ wave debug paths similarly read `ixSQ_WAVE_STATUS` and related `SQ_WAVE_*` registers when dumping or preserving wave state.

## State and Persistence

The macros are stateless compile-time constants, but the hardware state they describe is persistent until the GPU, power-management code, debug code, context restore, or reset path changes it.

GC CAC and SE CAC registers describe power-accounting configuration and telemetry. Weight and override fields alter how block-level CAC signals contribute to accounting; accumulator fields expose hardware-maintained counters. These counters are volatile hardware state and can wrap because the masks are full-width 32-bit fields.

SQ wave registers describe live execution state. `SQ_WAVE_STATUS`, `SQ_WAVE_MODE`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_HW_ID`, `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_PC_*`, instruction words, TTMP registers, `M0`, and `EXEC` represent per-wave state visible through the SQ indirect debug interface. Reads are snapshots of live GPU execution, and writes or debug actions in this area can affect trapping, halt behavior, replay, and wave scheduling.

DIDT and EDC registers are power-management state. Enables, stall policies, thresholds, weights, delays, and throttle controls can persist across workloads while the ASIC is powered and directly influence throttling behavior for SQ, DB, TD, TCP, and related DBR telemetry. Event counters persist until reset or explicit clear via the relevant `DIDT_STALL_EVENT_COUNTER_CLEAR` fields. EDC reset semantics are visible in consumers that set `EDC_EN` and invert `EDC_SW_RST` when enabling or disabling EDC.

No disk persistence or software cache is implemented here. The stateful behavior belongs to the GPU register file and to runtime drivers that program these fields.

## Dependencies

- Depends on AMD's generated GC 9.2.1 register specification. Manual edits risk diverging from the ASIC hardware contract.
- Must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h`, which supplies the matching register offsets.
- Consumers depend on AMDGPU register helper macros and indirect register spaces for GC, SE CAC, SQ, and DIDT access.
- Power-management integration depends on PowerPlay/DPM code that programs DIDT/EDC tables and toggles ramping capabilities.
- Debug and trap integration depends on SQ wave debug readers and KFD CWSR/trap code understanding the same wave status and register-state layout.
- The masks are generation-specific. Similar names appear in GC 9.0, GC 9.1, GC 10.x, and later headers, but fields and offsets can differ, so cross-generation reuse must include the correct header pair.

## Integration Points

- AMDGPU power tuning uses DIDT masks to build initialization tables and runtime writes for SQ, DB, TD, and TCP ramping. The same programming model controls EDC thresholds, EDC enables, stall patterns, throttle release behavior, and event-counter clearing.
- SQ debug paths use wave registers to read live wave information for diagnostics, hang analysis, shader debugging, and wave dumps. The fields in this chunk line up with concepts also handled by KFD trap/CWSR assembly, such as wave status, halt, trap, SPI priority, ECC error, TTMP registers, and `EXEC`.
- Telemetry and diagnostics can use CAC accumulator and DIDT event-counter fields to inspect power/throttle activity. Because these are hardware counters, sampling code must handle wraparound and coordination with clear/reset operations.
- Register decode tools and golden-register validation can use the shift/mask pairs to verify emitted state against known-good programming sequences.
- The include path is architecture-specific: this header is pulled by GC 9.2.1 users such as Vega12-era power-management include code, not by generic code that should be ASIC-agnostic.

## Risks

- Bitfield drift is the primary risk. A wrong shift or mask silently updates the wrong hardware bits, which can misprogram power throttling, corrupt debug reads, or break CAC accounting.
- This chunk is boundary-partial at the start. `GC_CAC_OVRD_TA` is not fully represented here, so merge tooling should combine it with the previous chunk for complete per-register documentation.
- DIDT/EDC controls have high operational impact. Incorrect values for enable, reset, stall delay, throttle policy, thresholds, or weight registers can over-throttle the GPU, fail to throttle during droop events, trigger performance regressions, or destabilize the device.
- SQ wave debug fields are sensitive live state. Misdecoding `SQ_WAVE_STATUS`, trap status, `EXEC`, TTMP, or PC fields can mislead hang/debug analysis; accidental writes through SQ indirect paths could alter a running wave.
- Counter and accumulator fields are full 32-bit values with no type safety. Readers must handle wraparound and avoid racing with code that clears DIDT event counters.
- Repeated register families are copy/paste prone. SQ, DB, TD, and TCP DIDT groups share many field names; using a mask from the wrong domain can produce a compile-time-valid but hardware-wrong access.
- Cross-generation similarity is dangerous. GC 9.2.1 masks resemble GC 9.0/9.1/10.x masks, but fields such as DIDT controls and EDC controls evolve between generations.

## Test Signals

- Build coverage: compile AMDGPU code paths that include `gc_9_2_1_sh_mask.h` to catch syntax errors, duplicate macros, and missing companion definitions.
- Static consistency: verify each `REGISTER__FIELD__SHIFT` in this range has the expected `REGISTER__FIELD_MASK`, and that each register has a matching offset in `gc_9_2_1_offset.h`.
- Register-generation checks: compare this chunk against AMD's GC 9.2.1 register source/spec and against adjacent generated headers to detect accidental manual drift.
- Power-management runtime tests: on matching GC 9.2.1 hardware, enable and disable DIDT/EDC ramping paths and watch for invalid register accesses, GPU resets, performance cliffs, or thermal/power telemetry anomalies.
- Counter tests: sample `DIDT_*_STALL_EVENT_COUNTER` and CAC accumulator registers under controlled workloads, then clear/reset where supported and verify expected counter behavior and wraparound-safe decoding.
- SQ debug tests: trigger wave dumps or hang diagnostics and confirm `SQ_WAVE_*` fields decode plausible wave IDs, SIMD/CU/SE identity, status, PC, instruction words, `EXEC`, and TTMP values.
- Graphics and compute stress: run shader-heavy, texture-heavy, depth-heavy, and mixed workloads to exercise SQ/TD/TCP/DB throttling domains while monitoring for hangs, VM faults, throttling instability, or debug-register decode failures.
