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
