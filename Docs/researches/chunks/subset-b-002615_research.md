# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 1-2417

## Scope

This chunk is the opening section of AMD's generated GC 9.0 shader-mask header. It contains the license, include guard, and register bitfield `__SHIFT`/`_MASK` macro definitions for early GC 9 graphics-core register blocks:

- Unqualified initial GCEA EDC counters.
- `gc_cppdec2`: command processor front-end/generic/CPC/DC EDC counters.
- `gc_grbmdec`: GRBM control, status, reset, trap, error, scratch, RSMU, interrupt, clock, power, and selected-GFX routing fields.
- `gc_cpdec`: CP/CPC/CPF/MEC/PFP/ME/CE status, queue, ring, stall, interrupt-debug, halt/reset, threshold, counter, and pointer fields.
- `gc_padec`: VGT, IA, WD, PA CL/SU/SC, primitive config, UTCL1, binner event/performance, PBB, and rasterization control fields.
- `gc_sqdec`: SQ/SQC/LDS, shader memory, shader-rate, UTCL1, interrupt, trap address, and SQC DSM fields through the beginning of `SQC_DSM_CNTLB`.

The file is hardware metadata only. It declares no functions, structs, variables, storage, locks, or executable code.

## Purpose

The purpose of this chunk is to expose stable symbolic names for GC 9.0 register bit positions and masks. AMDGPU and KFD code use these macros to compose MMIO register values, extract hardware status fields, apply golden register settings, configure per-VMID shader memory behavior, and interpret error or busy state.

Each register field generally appears as a pair:

- `REGISTER__FIELD__SHIFT`: the low bit used when shifting an unmasked field value into position.
- `REGISTER__FIELD_MASK`: the full bit mask used to isolate, clear, or test the field.

These macros are paired with GC 9.0 offset macros from the matching `gc_9_0_offset.h` and with common field helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.

## Important APIs, Types, And Macros

There are no C APIs or types in the chunk. The exported interface is the macro namespace itself.

Major macro groups include:

- EDC/error counters: `GCEA_EDC_CNT`, `GCEA_EDC_CNT2`, `CPF_EDC_TAG_CNT`, `CPF_EDC_ROQ_CNT`, `CPG_EDC_TAG_CNT`, `CPG_EDC_DMA_CNT`, `CPC_EDC_SCRATCH_CNT`, `CPC_EDC_UCODE_CNT`, and `DC_EDC_*` fields count correctable/uncorrectable or detected memory errors across command, data, tag, page, scratch, and microcode storage.
- GRBM control/status: `GRBM_CNTL`, `GRBM_STATUS`, `GRBM_STATUS2`, `GRBM_STATUS_SE0` through `GRBM_STATUS_SE3`, `GRBM_SOFT_RESET`, `GRBM_READ_ERROR*`, `GRBM_WRITE_ERROR`, `GRBM_IOV_ERROR`, `GRBM_GFX_CNTL`, `GRBM_RSMU_CFG`, `GRBM_INT_CNTL`, `GRBM_TRAP_*`, `GRBM_UTCL2_INVAL_RANGE_*`, and scratch registers describe global graphics bus status, read/write fault attribution, reset targets, trap filtering, per-VM/queue selection, power and clock gating controls, and virtual-function error state.
- CP status and queues: `CP_CPC_STATUS`, `CP_CPC_BUSY_STAT`, `CP_CPC_STALLED_STAT1`, `CP_CPF_STATUS`, `CP_CPF_BUSY_STAT`, `CP_CPF_STALLED_STAT1`, `CP_STALLED_STAT1/2/3`, `CP_BUSY_STAT`, `CP_STAT`, `CP_ME_CNTL`, `CP_MEC_CNTL`, `CP_CNTX_STAT`, `CP_ROQ_*`, `CP_STQ_*`, `CP_MEQ_*`, `CP_CEQ*`, `CP_RB*_RPTR`, and `CP_INT_STAT_DEBUG` fields expose busy/stalled causes, queue occupancy, ring read pointers, firmware parser control, context state, and interrupt assertions.
- PA/VGT/WD/IA fields: `VGT_CACHE_INVALIDATION`, `VGT_RESET_DEBUG`, `VGT_DMA_CONTROL`, `VGT_FIFO_DEPTHS`, `IA_CNTL_STATUS`, `WD_CNTL_STATUS`, `WD_UTCL1_*`, `IA_UTCL1_*`, `PA_CL_ENHANCE`, `PA_SC_BINNER_EVENT_CNTL_0` through `_3`, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, and binner/fifo/perf registers tune primitive assembly, draw/vertex DMA, rasterizer and binner events, cache invalidation, primitive binning, pipeline selection, and UTCL1 behavior.
- SQ/SQC/shader memory fields: `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_RANDOM_WAVE_PRI`, `SQ_REG_CREDITS`, `SQ_FIFO_SIZES`, `SQ_DSM_CNTL*`, `SQ_RUNTIME_CONFIG`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `CC_GC_SHADER_RATE_CONFIG`, `GC_USER_SHADER_RATE_CONFIG`, `SQ_UTCL1_CNTL*`, `SQ_UTCL1_STATUS`, `SQ_SHADER_TBA/TMA_*`, and `SQC_DSM_CNTL*` define shader queue/cache controls, LDS reporting, debug/error injection, shader memory aperture settings, shader-rate overrides, translation-cache invalidation, trap base/mask addresses, and SQC diagnostic single-write controls.

Representative consumers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c`, which includes this header, uses `SH_MEM_CONFIG__ALIGNMENT_MODE__SHIFT` while initializing compute VMIDs, uses `GRBM_STATUS__*` and `GRBM_STATUS2__RLC_BUSY` to decide soft-reset targets, and programs `SQ_CONFIG`, `SQC_CONFIG`, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, and `PA_SC_BINNER_EVENT_CNTL_3` golden values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v9.c`, which builds per-process `qpd->sh_mem_config` from `SH_MEM_CONFIG__ALIGNMENT_MODE__SHIFT`, `SH_MEM_CONFIG__RETRY_DISABLE__SHIFT`, and generation-specific shader-memory bits.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c`, whose golden-register path special-cases writes to `PA_SC_BINNER_EVENT_CNTL_3`, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, and `SH_MEM_CONFIG` through the RLC access path.
- Other direct include sites: `gmc_v9_0.c`, `gfxhub_v1_0.c`, `mxgpu_ai.c`, `amdgpu_amdkfd_gfx_v9.c`, `amdgpu_amdkfd_arcturus.c`, `kfd_mqd_manager_v9.c`, and `pm/powerplay/hwmgr/vega10_inc.h`.

## Control Flow

The chunk has no intrinsic control flow. Runtime control flow is created when driver code reads or writes GC registers using the matching offset macros and these masks/shifts.

Common patterns are:

1. Compose a register value by shifting a field value with `REGISTER__FIELD__SHIFT` or by calling `REG_SET_FIELD(value, REGISTER, FIELD, field_value)`.
2. Select the target engine, queue, VMID, shader engine, or hardware instance with SOC15/GRBM helpers when the register is instance- or VMID-scoped.
3. Write the composed value with `WREG32_SOC15()`, `WREG32_SOC15_RLC()`, `WREG32_RLC()`, or related AMDGPU MMIO helpers.
4. Poll or inspect a register with `RREG32_SOC15()` and test `_MASK` bits directly, or call `REG_GET_FIELD()` for multi-bit fields.
5. Branch into reset, idle-wait, debug, trap, interrupt, or queue-management flows based on the decoded fields.

For example, `gfx_v9_0_soft_reset()` reads `mmGRBM_STATUS` and tests masks such as `GRBM_STATUS__PA_BUSY_MASK`, `GRBM_STATUS__SC_BUSY_MASK`, `GRBM_STATUS__CP_BUSY_MASK`, and `GRBM_STATUS__CP_COHERENCY_BUSY_MASK`. It then sets `GRBM_SOFT_RESET` fields with `REG_SET_FIELD()` and checks `GRBM_STATUS2.RLC_BUSY` to include the RLC in reset handling. Similarly, compute VMID initialization selects each VMID with `soc15_grbm_select()` and writes `SH_MEM_CONFIG`/`SH_MEM_BASES` using the shader-memory field definitions from this chunk.

## State And Persistence Behavior

This header does not hold software state. It defines how software addresses and interprets persistent or transient state inside GC 9 hardware registers.

The state represented by these fields includes:

- Transient busy, pending, stalled, idle, FIFO, queue, and read/write pointer state in GRBM, CP, CPC, CPF, PA, VGT, WD, IA, SQ, and SQC blocks.
- Persistent configuration until changed or reset, such as shader memory apertures (`SH_MEM_BASES`, `SH_MEM_CONFIG`), cache/UTCL1 response and invalidation behavior, PBB/binner/rasterization controls, SQ/SQC cache behavior, clock/power knobs, and golden-register overrides.
- Error and diagnostic state, including EDC counters, GRBM read/write/IOV fault attribution, CP interrupt-debug bits, UTCL1 fault/retry/PRT status, DSM/error-injection settings, and trap address/data masks.
- Per-VMID or selected-context state, especially shader memory config and registers affected by GRBM/SRBM selection. Incorrect selection can update or observe the wrong VMID/queue/context even when the field mask is correct.

Persistence is hardware-defined. Some fields are sticky until cleared or reset, some are live status snapshots, and some are programming knobs that survive until rewritten by driver initialization, reset, power-management, virtualization, queue setup, or firmware paths.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.0 register database and must stay synchronized with:

- `gc_9_0_offset.h`, which gives the register addresses for the bitfields defined here.
- SOC15 register helpers and accessors, including `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, `WREG32_SOC15_RLC()`, `WREG32_RLC()`, `REG_SET_FIELD()`, and `REG_GET_FIELD()`.
- AMDGPU GC 9 initialization, reset, golden-register programming, queue management, GPUVM/GMC setup, virtualization, and debug paths.
- KFD v9 queue/MQD setup, where `SH_MEM_CONFIG` and `SH_MEM_BASES` are part of persisted process/queue state.
- RLC-mediated register programming. `soc15.c` routes specific GC registers in this chunk through `WREG32_RLC()`, so changes to masks or offsets can affect whether firmware-safe access paths are used.
- Hardware generation boundaries. Nearby GC 9.x, GC 10.x, GC 11.x, and GC 12.x headers have similarly named fields but not always identical layouts or feature sets.

The source path is under a `ceph-client` mirror, but the content is AMD GPU driver metadata and has no Ceph or distributed-filesystem behavior.

## Risks And Edge Cases

- These macros are untyped preprocessor constants. A wrong mask or shift compiles cleanly and can silently program the wrong hardware bit.
- Multi-bit fields need both correct shift and correct value range. Overwide values can spill into adjacent fields if call sites shift manually instead of using `REG_SET_FIELD()`.
- Generation-specific fields are easy to misuse because macro names recur across ASIC generations. Applying GC 9.0 bit layouts to GC 9.4.x, GC 10+, or older GCA headers can break reset, memory, cache, and debug behavior.
- Status registers are volatile. Polling `GRBM_STATUS`, CP queue state, UTCL1 status, SQ/SQC state, or binner event fields can race with active hardware, firmware, preemption, or reset.
- Per-VMID and selected-GFX writes depend on correct GRBM/SRBM selection and locking. The GC 9 path uses `adev->srbm_mutex` around VMID programming; missing selection discipline could corrupt another VMID's shader memory aperture.
- Golden-register and RLC paths are sensitive. Fields such as `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_BINNER_EVENT_CNTL_3`, `SQC_CONFIG`, and `SQ_CONFIG` encode hardware workarounds and performance toggles; changing definitions can regress hangs, rendering correctness, or power/performance without obvious compile failures.
- Error-injection/DSM fields can be dangerous if accidentally enabled outside diagnostics, because they can force stalls, single writes, or injected errors in SQ/SQC/PA logic.
- This chunk ends mid-register at `SQC_DSM_CNTLB`. Whole-file research must merge later chunks before making complete statements about the SQC DSM block or the full GC 9.0 mask namespace.

## Test Signals

Useful validation signals include:

- Build AMDGPU and KFD with GC 9 support enabled. Missing or renamed macros should fail in `gfx_v9_0.c`, KFD v9 queue/MQD code, `soc15.c`, and related include sites.
- Boot on GC 9 hardware and verify `gfx_v9_0` initialization reaches idle without GRBM timeout, VMID setup errors, RLC register-access failures, or golden-register warnings.
- Exercise compute queue creation and teardown through KFD/ROCm paths. Incorrect `SH_MEM_CONFIG` or `SH_MEM_BASES` fields can show up as GPUVM faults, XNACK/retry misbehavior, bad scratch/LDS apertures, or process queue failures.
- Trigger or simulate GPU hangs and reset paths. `gfx_v9_0_soft_reset()` should classify busy blocks correctly from `GRBM_STATUS`/`GRBM_STATUS2` and reset CP/GFX/RLC as intended.
- Run graphics workloads that stress primitive binning, streamout, depth/color cache flushes, and PBB/PA_SC event flows; incorrect PA/VGT/SC masks can cause rendering corruption, hangs, or performance regressions.
- Validate ECC/EDC telemetry and error paths where available. EDC counter fields should decode plausible SEC/DED/SED counts and not overlap adjacent counters.
- Compare the generated macros mechanically against AMD's authoritative GC 9.0 register specification and sibling generated headers, allowing only expected ASIC-version differences.

## Cross-Chunk Notes

This is the first chunk of `gc_9_0_sh_mask.h`. Later chunks are needed for the remainder of `SQC_DSM_CNTLB` and the rest of the GC 9.0 mask namespace. The final per-file document should treat this file as generated hardware metadata paired with `gc_9_0_offset.h`, not as handwritten driver logic.
