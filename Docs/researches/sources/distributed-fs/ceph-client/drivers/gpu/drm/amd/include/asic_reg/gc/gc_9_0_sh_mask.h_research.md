# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002615`: lines 1-2417, `Docs/researches/chunks/subset-b-002615_research.md`
- `subset-b-002616`: lines 2418-4814, `Docs/researches/chunks/subset-b-002616_research.md`
- `subset-b-002617`: lines 4815-7180, `Docs/researches/chunks/subset-b-002617_research.md`
- `subset-b-002618`: lines 7181-9637, `Docs/researches/chunks/subset-b-002618_research.md`
- `subset-b-002619`: lines 9638-12160, `Docs/researches/chunks/subset-b-002619_research.md`
- `subset-b-002620`: lines 12161-14705, `Docs/researches/chunks/subset-b-002620_research.md`
- `subset-b-002621`: lines 14706-17177, `Docs/researches/chunks/subset-b-002621_research.md`
- `subset-b-002622`: lines 17178-19721, `Docs/researches/chunks/subset-b-002622_research.md`
- `subset-b-002623`: lines 19722-22327, `Docs/researches/chunks/subset-b-002623_research.md`
- `subset-b-002624`: lines 22328-24771, `Docs/researches/chunks/subset-b-002624_research.md`
- `subset-b-002625`: lines 24772-27122, `Docs/researches/chunks/subset-b-002625_research.md`
- `subset-b-002626`: lines 27123-29720, `Docs/researches/chunks/subset-b-002626_research.md`
- `subset-b-002627`: lines 29721-30033, `Docs/researches/chunks/subset-b-002627_research.md`

## Chunk Research

### subset-b-002615: lines 1-2417

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

### subset-b-002616: lines 2418-4814

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 2418-4814

## Purpose

This chunk is generated AMD GC 9.0 graphics-core register bitfield metadata. It contains no executable C code; it publishes preprocessor `__SHIFT` and `_MASK` constants for fields in 32-bit hardware registers. AMDGPU, AMDKFD, power-management, debug, and profiling code pair these macros with register offsets from `gc_9_0_offset.h` and register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

The selected range starts in the tail of SQC data-share-memory single-write controls, then covers SQC error injection and EDC counters, SQ command/indexed debug and instruction/resource encodings, SQ load-balance and EDC state, SQ thread-trace token word layouts, SQC instruction/data UTCL1 control/status registers, the `gc_shsdec` block for SX and SPI debug/wave-lifetime state, the `gc_tpdec` TD/TA texture control/status block, and the beginning of `gc_gdsdec` GDS configuration/status/fault/EDC registers. Despite the repository path being under `ceph-client`, this file is AMD GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, callbacks, locks, allocations, or direct MMIO operations in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- Consumers compose or decode register values with the matching `mm*`/`reg*` offsets from `gc_9_0_offset.h`.

Major register groups in this range:

- SQC DSM and EDC controls: `SQC_DSM_CNTLB`, `SQC_DSM_CNTL2`, `SQC_DSM_CNTL2A`, `SQC_DSM_CNTL2B`, `SQC_EDC_FUE_CNTL`, `SQC_EDC_CNT2`, `SQC_EDC_CNT3`, and `SQC_EDC_CNT` describe single-write irritator data, error-injection enables/delays, fatal uncorrectable error interrupt flags, and SEC/DED/SED counters for instruction and data tag RAMs, bank RAMs, UTCL1 FIFOs, miss FIFOs, dirty-bit RAMs, and per-CU data paths.
- SQ debug and command registers: `SQ_REG_TIMESTAMP`, `SQ_CMD_TIMESTAMP`, `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_CMD`, `SQ_TIME_HI`, and `SQ_TIME_LO` define timestamp windows, indexed wave/thread reads, force-read/read-timeout controls, command mode/data fields, VMID checking, wave/SIMD/queue targeting, and 64-bit time readback split into high/low registers.
- Shader instruction encoding views: `SQ_DS_*`, `SQ_EXP_*`, `SQ_FLAT_*`, `SQ_GLBL_*`, `SQ_INST`, `SQ_MIMG_*`, `SQ_MTBUF_*`, `SQ_MUBUF_*`, `SQ_SCRATCH_*`, `SQ_SMEM_*`, `SQ_SOP*`, `SQ_VINTRP`, `SQ_VOP*`, `SQ_VOP_DPP`, `SQ_VOP_SDWA`, and `SQ_VOP_SDWA_SDST_ENC` expose bitfield layouts for GC 9 shader instruction words. These include operand registers, offsets, opcodes, encodings, cache-policy bits such as `GLC`/`SLC`, data/number formats, swizzle fields, modifiers, clamp/neg/abs controls, and DPP/SDWA lane-selection fields.
- SQ load-balance, EDC, and trace-word decode: `SQ_LB_CTR_CTRL`, `SQ_LB_DATA[0-3]`, `SQ_LB_CTR_SEL`, `SQ_LB_CTR[0-3]_CU`, `SQ_EDC_SEC_CNT`, `SQ_EDC_DED_CNT`, `SQ_EDC_INFO`, `SQ_EDC_CNT`, `SQ_EDC_FUE_CNTL`, and `SQ_THREAD_TRACE_WORD_*` define load-balance counter controls/data/CU masks, LDS/SGPR/VGPR EDC counters and fault source metadata, fatal error flags, and packed thread-trace token formats for events, instructions, issue groups, register writes, wave state, wave starts, user data, PC halves, perf data, and timestamps.
- Shader resource descriptors and samplers: `SQ_BUF_RSRC_WORD[0-3]`, `SQ_IMG_RSRC_WORD[0-7]`, `SQ_IMG_SAMP_WORD[0-3]`, `SQ_FLAT_SCRATCH_WORD[0-1]`, and `SQ_M0_GPR_IDX_WORD` describe buffer base/stride/format/swap/index bounds, image base/metadata/width/height/depth/pitch/mip/array/swizzle/compression fields, sampler clamp/filter/aniso/LOD/border-color fields, scratch size/offset, and M0 relative-index controls.
- SQC UTCL1 controls and status: `SQC_ICACHE_UTCL1_CNTL1/2`, `SQC_DCACHE_UTCL1_CNTL1/2`, `SQC_ICACHE_UTCL1_STATUS`, and `SQC_DCACHE_UTCL1_STATUS` cover instruction/data cache translation behavior, GPUVM default page size and permission modes, response/fault modes, client ID, LFIFO controls, VMID invalidation fields, force-miss/in-order knobs, reduced FIFO/cache sizing, EDC disable, snoop/ack behavior, perf-event filters, and fault/retry/PRT detection bits.
- `addressBlock: gc_shsdec`: `SX_DEBUG_BUSY` through `SX_DEBUG_BUSY_5` expose shader export/color path busy and valid bits across position banks, write controls, DBIF interfaces, color blend queues, and scoreboard/fifo paths. `SX_DEBUG_1` exposes SX-to-DB credit and debug/optimization disable controls. The SPI portion includes `SPI_PS_MAX_WAVE_ID`, `SPI_START_PHASE`, `SPI_GFX_CNTL`, `SPI_DEBUG_READ`, `SPI_DSM_CNTL`, `SPI_DSM_CNTL2`, `SPI_EDC_CNT`, `SPI_DEBUG_BUSY`, `SPI_CONFIG_PS_CU_EN`, wavefront lifetime limit/status/debug registers, SPI load-balance counters, static CU masks, GDS credits, SX export/scoreboard buffer sizes, CSQ active wave status/counts, per-CU wave data readback, SPIS/BCI debug reads, and trap-screen base/mask/GPR-min registers for P0 and P1.
- `addressBlock: gc_tpdec`: `TD_CNTL`, `TD_STATUS`, `TD_DSM_CNTL`, `TD_DSM_CNTL2`, `TD_SCRATCH`, `TA_CNTL`, `TA_CNTL_AUX`, `TA_STATUS`, and `TA_SCRATCH` define texture data/address controls, busy/empty indicators, DSM injection, scratch windows, non-determinism/perf/texture behavior toggles, anisotropy and LOD controls, gather/border/swizzle controls, deterministic-disable bits, FIFO status, and aggregate TA busy state.
- `addressBlock: gc_gdsdec`: `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ENHANCE2`, `GDS_PROTECTION_FAULT`, `GDS_VM_PROTECTION_FAULT`, `GDS_EDC_CNT`, and the start of `GDS_EDC_GRBM_CNT` describe GDS shader-array phase selection, GDS/GRBM/ordered-append/GWS/DS busy and conflict status, protection-fault attribution fields, VM fault attribution including VMID/TMZ/GWS/OA, and GDS EDC counters.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the driver and hardware:

1. GC 9 code includes `gc_9_0_sh_mask.h` with the companion GC 9 offset header.
2. The caller selects a register offset and uses the field macros here to build or decode a 32-bit register value.
3. AMDGPU/AMDKFD helpers perform direct or indirect register reads/writes.
4. Higher-level GFX, KFD, reset, debug, profiling, and power-management code owns ordering, locking, safe-mode entry, polling, and timeout handling.

The `SQ_CMD` fields are a concrete example of this flow. GC 9 soft-recovery code in `gfx_v9_0.c` builds a command by setting `CMD`, `MODE`, `CHECK_VMID`, and `VM_ID`, enters RLC safe mode, writes `mmSQ_CMD`, and exits safe mode. KFD debug wave-reset code has a matching `union SQ_CMD_BITS` layout and writes equivalent command fields when killing wavefronts for a process VMID. The header only defines the field layout; it does not decide when wave termination is safe.

SQC and GDS status/fault fields participate in diagnostic flows. GC 9 debug register lists include `mmGDS_PROTECTION_FAULT`, `mmGDS_VM_PROTECTION_FAULT`, `mmSQC_DCACHE_UTCL1_STATUS`, and `mmSQC_ICACHE_UTCL1_STATUS`, allowing hang/fault reporting code to sample whether translation faults, retries, PRT events, or GDS protection faults were observed.

The instruction and resource descriptor macros describe packed data formats rather than driver procedures. They may be used by debug decoders, firmware-facing tooling, trace parsing, or hardware validation to interpret instruction words, buffer/image descriptors, sampler descriptors, thread-trace packets, and load-balance counters.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes hardware state in GC 9 registers and packed shader-facing words.

The represented hardware state includes EDC injection configuration, SEC/DED/SED counters, fatal error flags, SQ command targeting, indirect wave/thread debug indices and data, timestamp/time values, instruction encodings, resource descriptors, sampler descriptors, scratch configuration, SQ load-balance counters, EDC fault source metadata, thread-trace token payloads, SQC UTCL1 invalidation and fault state, SX/SPI busy/debug/status state, SPI wave lifetime thresholds and interrupt-sent status, per-CU/static-CU masks, trap-screen base/mask windows, TD/TA texture controls and busy flags, GDS phase controls, GDS busy/conflict/clamp state, GDS protection-fault attribution, and GDS EDC counters.

Persistence is hardware-defined. Configuration fields generally remain until reset, GPU reset, suspend/resume reinitialization, power transition, or explicit reprogramming. Status, busy, counter, and fault fields can change asynchronously while queues, shaders, texture blocks, caches, and GDS pipelines are active. Some fields are action-like or side-effectful, such as error injection enables, counter load/clear/start bits, SQ commands, SQC invalidation toggles, SPI reset-count controls, and interrupt/fault clear paths in surrounding code.

The macros do not encode access permissions, reset values, read-only/write-only behavior, write-one-to-clear behavior, sticky semantics, self-clearing semantics, reserved-bit policy, alignment units, or privileged access rules. Consumers must preserve unrelated bits in mixed registers and follow the ASIC programming guide and local driver sequencing.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`, which supplies matching register offsets and base-index symbols. This mask header is unsafe to pair with another GC generation's offsets even when register names overlap.

Observed and likely integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c`, which includes `gc_9_0_offset.h` and `gc_9_0_sh_mask.h`, lists SQC/GDS/UTCL1 fault registers for diagnostics, applies golden settings for `TA_CNTL_AUX`, and uses `SQ_CMD` fields for ring soft recovery.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v9.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager.c`, which interact with `SQ_CMD` semantics for process wavefront reset and KFD queue/debug control.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v9.c`, `amdgpu_amdkfd_arcturus.c`, `soc15.c`, `mxgpu_ai.c`, `gfxhub_v1_0.c`, PSP v3/v11/v12 paths, and Vega10 powerplay includes, which include the GC 9 generated headers for ASIC-specific register programming.
- GFX 9 golden-register and workaround paths. `TA_CNTL_AUX` and `TD_CNTL` fields in this chunk correspond to texture-address/data knobs that are programmed through SOC15 golden settings for Vega and later GC 9 variants.
- Debugfs, GPU hang analysis, RAS/EDC diagnostics, and crash-dump paths, because SQC/SQ/GDS EDC counters, UTCL1 status, SX/SPI busy bits, and GDS protection-fault fields expose low-level fault or activity state.
- Profiling and trace tooling, because `SQ_THREAD_TRACE_WORD_*`, SPI wave lifetime/status, SQ/SPI load-balance counters, and full-width debug readback registers are decode surfaces for shader trace and performance analysis.
- VM and memory-management integration, because SQC instruction/data UTCL1 controls/status and GDS VM protection-fault fields include VMID, fault/retry/PRT, TMZ, and address fragments.
- Graphics and compute pipeline setup, because shader instruction encodings, buffer/image/sampler descriptors, scratch descriptors, SPI CU masks, GDS credits, and TD/TA controls are on the boundary between command submission, shader execution, and hardware validation.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. These constants are untyped integer macros and can compile while targeting the wrong register block or ASIC revision.
- The chunk starts mid-register in the tail of `SQC_DSM_CNTLB` and ends mid-register at the start of `GDS_EDC_GRBM_CNT`; adjacent chunks are required for a complete per-file view.
- Whole-register writes are dangerous for mixed control/status registers. SQC UTCL1, TD/TA, SPI, and GDS registers contain reserved, unused, status, and control fields in the same word.
- `SQ_CMD` is sequencing-sensitive. Issuing wave kill/debug commands without correct VMID selection, safe-mode handling, queue quiescence, or RLC coordination can kill the wrong waves or destabilize recovery.
- Error-injection fields in SQC/SPI/TD are high impact. Accidentally enabling DSM irritator data or delayed error injection can create artificial SEC/DED/FUE conditions and misleading RAS results.
- EDC counters are small packed fields in several registers. Readers must know saturation, clear, and rollover behavior outside this header before treating values as precise event counts.
- Low/high time or counter windows can race with live hardware updates. `SQ_TIME_HI/LO` and full-width counter/debug data registers may require latching, retry reads, or stop/sample sequencing.
- Instruction/resource descriptor masks are not validation logic. A bit pattern that fits a mask may still be illegal for a shader stage, resource type, format, swizzle mode, alignment, or GPUVM configuration.
- SQC UTCL1 invalidation fields include VMID-specific and all-VMID invalidation toggles. Wrong use can leave stale translations, force excessive misses, or affect other VMIDs.
- Fault/status bits such as `FAULT_DETECTED`, `RETRY_DETECTED`, `PRT_DETECTED`, GDS fault fields, and busy flags are volatile. Diagnostic code must tolerate transitions and clear/observe semantics rather than assuming stable snapshots.
- `TA_CNTL_AUX` contains deterministic-disable and texture behavior fields that are touched by golden settings. Wrong values can affect texture determinism, anisotropy, gather behavior, border color handling, and workload-specific rendering correctness.
- SPI wave lifetime limit/status registers are replicated and threshold-like. Misprogrammed limits or sample periods can create unexpected warning interrupts or hide long-lived wavefronts.
- GDS protection-fault address fields are partial and unit-specific. Decoding must combine fault type, VMID or shader attribution, and address fragments according to the hardware spec.

## Test Signals

Useful validation is mostly build coverage, generated-header consistency, and hardware smoke/debug coverage:

- Build GC 9 AMDGPU, AMDKFD, PSP, GFXHUB, Vega10 powerplay, and SOC15 paths that include `gc_9_0_sh_mask.h`.
- Generated-header checks that every field has coherent `__SHIFT` and `_MASK` definitions, masks align with shifts, fields within a register do not overlap except documented aliases/reserved regions, and registers in this range have matching entries in `gc_9_0_offset.h`.
- Static checks that GC 9 code does not mix `gc_9_0_sh_mask.h` fields with GC 8, GC 10, GC 11, or GC 12 offset headers.
- Soft-recovery and KFD debug tests that issue `SQ_CMD` wave reset/kill commands for selected VMIDs and verify only intended queues/waves are affected.
- GPU hang and fault-dump tests that sample SQC UTCL1 status, GDS protection-fault registers, SX/SPI busy registers, and SQ EDC info after induced or simulated faults.
- RAS/EDC validation that toggles supported injection paths, observes SQC/SPI/GDS counters and FUE flags, then verifies recovery and interrupt behavior.
- VM/cache tests that exercise SQC instruction/data UTCL1 invalidation, fault/retry/PRT reporting, VMID-specific behavior, and suspend/resume or reset reinitialization.
- Shader trace/profiling tests that decode representative `SQ_THREAD_TRACE_WORD_*` packets, SQ/SPI load-balance counter data, wave lifetime status, and full-width debug readback windows.
- Graphics correctness tests around texture sampling and descriptors, especially workloads sensitive to `TA_CNTL_AUX`, image/sampler descriptor encodings, anisotropy, border color, deterministic behavior, and compressed/metadata image fields.
- GDS tests that allocate/use GDS, GWS, and ordered-append resources, stress conflict/clamp paths, trigger or simulate protection faults, and verify busy/status/EDC fields decode plausibly.

### subset-b-002617: lines 4815-7180

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 4815-7180

## Scope

This chunk is a generated bitfield slice from the AMD GC 9.0 register shift/mask header. It starts at the tail of `GDS_EDC_GRBM_CNT`, covers the remainder of the GDS diagnostics block, all of the visible `gc_rbdec` and `gc_rmi_rmidec` blocks in this range, the `gc_utcl2_atcl2dec` block, most of the `gc_utcl2_vml2pfdec` block, and begins the `gc_utcl2_vml2vcdec` VM context-control block through the first fields of `VM_CONTEXT4_CNTL`.

The file contains preprocessor constants only. There are no C functions, structs, variables, allocation paths, locks, I/O routines, or executable branches in this chunk. Its exported interface is the conventional AMD register-field pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position for a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used by `REG_SET_FIELD`, `REG_GET_FIELD`, and direct bit operations.

Major register families covered here include GDS EDC/error-injection fields, DB depth-buffer debug and DFSM controls, CB/color-buffer hardware controls, GB address and tile-mode topology fields, RB disable/redundancy fields, RMI crossbar/UTCL1/scoreboard/status controls, ATC L2 cache/translation controls, GCVM L2 cache and protection-fault controls, ECC/parity counters, and VM context 0-4 control fields.

## Purpose

The purpose of this chunk is to publish the bit-level ABI between GC 9.0 hardware registers and AMDGPU driver code. The sibling `gc_9_0_offset.h` file defines the register addresses; this header defines how to compose and decode the 32-bit register values once the driver has selected an address.

The covered fields fall into several functional groups:

- GDS diagnostics: `GDS_EDC_OA_DED`, `GDS_DSM_CNTL`, `GDS_EDC_OA_PHY_CNT`, `GDS_EDC_OA_PIPE_CNT`, `GDS_DSM_CNTL2`, and `GDS_WD_GDS_CSB` describe GDS on-array/pipe ECC status, single-write/error-injection controls, injection delay selection, and watchdog counter fields.
- DB/CB/RB render backend controls: `DB_DEBUG*`, `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_SUBTILE_CONTROL`, `DB_FREE_CACHELINES`, `DB_FIFO_DEPTH*`, `DB_RMI_CACHE_POLICY`, `DB_DFSM_*`, `CB_HW_CONTROL*`, `CB_HW_MEM_ARBITER_*`, and `CB_DCC_CONFIG` define depth/stencil compression, HiZ/HiS, cache, FIFO, arbitration, DCC, fast-clear, and debug/erratum control bits.
- Graphics backend topology: `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_READ`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `GB_TILE_MODE0`-`31`, `GB_MACROTILE_MODE0`-`15`, `CC_RB_*`, and `GC_USER_RB_*` encode pipe counts, shader engines, render-backend counts, interleave sizes, tile/macro-tile mode tables, backend maps, and harvested/disabled RB state.
- RMI path controls: `RMI_GENERAL_*`, `RMI_SUBBLOCK_STATUS*`, `RMI_XBAR_*`, `RMI_UTCL1_*`, `RMI_TCIW_FORMATTER*_CNTL`, `RMI_SCOREBOARD_*`, `RMI_CLOCK_CNTRL`, `RMI_XNACK_DEBUG`, and `RMI_SPARE*` describe the render-memory interface, UTCL1 probe behavior, XNACK handling, TCIW formatting, crossbar arbitration, scoreboard flush/invalidation state, clock controls, and status/error reporting.
- Translation and VM L2 controls: `ATC_L2_*`, `VM_L2_CNTL*`, `VM_L2_STATUS`, `VM_DUMMY_PAGE_FAULT_*`, `VM_L2_PROTECTION_FAULT_*`, identity aperture registers, MM group return classes, bank-selection reservations, parity controls, clock-gating controls, ECC index/count registers, and `VM_CONTEXT0_CNTL` through the start of `VM_CONTEXT4_CNTL` define address translation cache, VM L2 cache, invalidation, page-fault policy, VMID/context enablement, and fault-interrupt behavior.

Although this repository path is under a `ceph-client` source tree, the content is AMD GPU register metadata and has no Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

This chunk's "API" is the macro namespace consumed by AMDGPU and KFD source files. Typical consumers include:

- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` and `REG_GET_FIELD(value, REGISTER, FIELD)`, which expand through the `__SHIFT` and `_MASK` definitions in this file.
- `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, `SOC15_REG_OFFSET`, and `SOC15_REG_ENTRY_OFFSET`, which perform the actual MMIO accesses to addresses from `gc_9_0_offset.h`.
- GC 9.0 hub setup code in `amdgpu/gfxhub_v1_0.c` and `amdgpu/mmhub_v1_0.c`, which programs VM page-table base registers, system apertures, TLB/cache registers, VMID context control, invalidation, fault-default policy, and clock/power gating.
- GC 9.0 memory-controller and fault paths in `amdgpu/gmc_v9_0.c`, including VM fault interrupt state, processing, TLB flush, PASID mapping, and page-table entry/PDE flag handling.
- KFD GC 9 queue paths such as `amdkfd/kfd_mqd_manager_v9.c` and `amdgpu/amdgpu_amdkfd_gfx_v9.c`, which include this header for compute-queue and VM-related register field definitions.
- Topology save/restore and compatibility code in older generation files such as `amdgpu/cik.c`, where similar `GB_ADDR_CONFIG`, tile-mode, and macro-tile-mode tables illustrate how these hardware tables are saved, restored, or exposed.

The highest-value field groups for runtime integration are:

- `GB_ADDR_CONFIG__NUM_PIPES`, `PIPE_INTERLEAVE_SIZE`, `MAX_COMPRESSED_FRAGS`, `NUM_SHADER_ENGINES`, and `NUM_RB_PER_SE`, because later GFX code reads these fields to derive graphics topology.
- `GB_TILE_MODE*` and `GB_MACROTILE_MODE*`, because they define the hardware tiling table that surface-addressing code and firmware-visible register state depend on.
- `VM_L2_CNTL*`, `VM_L2_PROTECTION_FAULT_CNTL*`, and `VM_CONTEXT*_CNTL`, because hub setup code uses these fields to enable VM contexts, configure page-table depth/block size, classify faults, select retry/default behavior, and enable or suppress fault interrupts.
- `ATC_L2_*` and `RMI_UTCL1_*`, because they sit on the translation/cache path used by ATS, UTCL1 probes, XNACK, VMID invalidation, and memory-system status reporting.
- `GDS_*_EDC*` and `VM_L2_*ECC*`, because RAS paths can use them for SEC/DED counters, ECC index selection, and error-count reporting.

## Control Flow

The header has no direct control flow. Runtime sequencing is imposed by driver code and the hardware blocks that consume the composed register values.

Typical VM hub setup driven by these macros follows this pattern:

1. `gfxhub_v1_0` or `mmhub_v1_0` writes page-table base, aperture, and default page registers using offsets from the matching offset header.
2. The driver composes `VM_L2_CNTL`, `VM_L2_CNTL2`, `VM_L2_CNTL3`, and `VM_L2_CNTL4` values to enable the L2 cache, select cache/invalidation behavior, set bank selection, and configure page-cache sizing.
3. It programs `VM_CONTEXT0_CNTL` and later contexts with `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry policy, default-fault behavior, and interrupt enables.
4. It programs `VM_L2_PROTECTION_FAULT_CNTL` and related registers to decide which faults default, which generate interrupts, whether subsequent status-address updates are allowed, and where default fault addresses point.
5. TLB invalidation and fault processing code later reads status registers, writes invalidation requests, and uses the configured masks to interpret protection-fault status and VM context state.

Typical render-backend and topology flow is more static:

1. Firmware, BIOS, or early driver init establishes `GB_ADDR_CONFIG`, tile-mode, macro-tile-mode, backend-map, and harvested RB state.
2. Driver code reads those registers and decodes field values to populate ASIC topology and surface-addressing decisions.
3. DB/CB/RMI tuning or golden-register programming may write selected debug, cache-policy, FIFO, arbitration, DCC, and clock-control fields during init, resume, reset, or workaround setup.
4. Rendering, depth/stencil, compression, fast-clear, and memory-interface behavior then follows the programmed hardware state.

Error and diagnostic flows use the same constants to poll or clear status fields. Examples include RMI busy/error bits, ATC/VM L2 parity information, VM protection-fault status/address registers, and GDS/VM L2 ECC counters.

## State And Persistence Behavior

This header stores no software state. It defines encodings for hardware state that may be persistent across a GPU power state, reset domain, or driver save/restore boundary depending on the owning block.

Important hardware state represented by this chunk includes:

- Persistent or semi-persistent configuration: GB address topology, tile/macro-tile mode tables, RB redundancy/backend-disable masks, DB/CB hardware-control tuning, RMI crossbar/arbitration settings, ATC/VM L2 cache policy, VM context enablement, page-table depth/block size, and protection-fault defaults.
- Transient status: DB/RMI FIFO/busy signals, RMI scoreboard and flush progress, ATC L2 busy/parity status, VM L2 busy/context-domain status, fault status, and XNACK/UTCL1 detection bits.
- Latched or counted diagnostics: GDS EDC SEC/DED counters, VM L2 ECC counts, parity error information, and protection-fault status/address registers.
- Command-like bits: cache/TLB invalidation bits, fault-status clear/update-control bits, error-injection controls, clock-gating overrides, and RMI configuration-update bits.

Consumers must treat status, counter, and strobe fields differently from durable configuration fields. For example, `VM_L2_PROTECTION_FAULT_CNTL__CLEAR_PROTECTION_FAULT_STATUS_ADDR` is a control action, while `VM_L2_PROTECTION_FAULT_STATUS` reports a captured event; `VM_CONTEXT*_CNTL` fields persist as context policy until reprogrammed; and `VM_L2_MEM_ECC_CNT` is a hardware-maintained count read through the selected ECC index.

## Dependencies And Integration Points

This chunk depends on the AMD generated-register-header convention and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`, which supplies matching GC 9.0 register addresses.
- Any GC 9.0 default/golden-register tables that assume these fields retain the generated layout.
- Core AMDGPU MMIO helpers and field helpers, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.
- `amdgpu/gfxhub_v1_0.c` and `amdgpu/mmhub_v1_0.c`, where hub initialization programs `VM_L2_*`, `VM_CONTEXT*_CNTL`, fault handling, invalidation, and clock/power-related fields.
- `amdgpu/gmc_v9_0.c`, which owns GC 9 memory management, page fault interrupts, TLB flushes, PASID mappings, VM PDE/PTE flag generation, ECC interrupt handling, and hub selection.
- `amdgpu/gfx_v9_0.c`, KFD GC 9 code, and SOC15 discovery/setup paths that include `gc_9_0_sh_mask.h` for queue, graphics, compute, and topology register work.
- Hardware or firmware programming of GB tile/macro-tile tables and RB harvest state. The driver-side masks must match the values loaded by firmware/BIOS and the expectations of surface-address calculations.

The chunk is source-tree-aligned to one generated header. It should be merged with adjacent chunks for whole-file conclusions because it starts with only the final `GDS_EDC_GRBM_CNT__UNUSED_MASK` line and ends partway through the `VM_CONTEXT4_CNTL` field list.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly but write the wrong hardware bits. The most severe cases are VM L2/context/fault fields, where misprogramming can cause page faults, lost interrupts, bad fault attribution, VMID isolation failures, or GPU hangs.
- Repeated register families are mechanically fragile. `GB_TILE_MODE0`-`31`, `GB_MACROTILE_MODE0`-`15`, and `VM_CONTEXT0_CNTL`-`4` have near-identical layouts; a one-register drift is easy to miss in review.
- Tile and topology fields must match the ASIC's actual fuse/harvest layout. Incorrect `GB_ADDR_CONFIG`, RB disable/redundancy, or backend map values can break surface addressing, compression, render backend routing, or user-visible topology reporting.
- Debug and workaround fields are not harmless. `DB_DEBUG*`, `CB_HW_CONTROL*`, `DB_DFSM_*`, RMI arbitration, and cache-policy fields can disable optimizations, force cache misses, alter compression/decompression, or change memory-request behavior.
- VM fault fields combine default action and interrupt behavior. Enabling defaults without interrupts can hide faults; enabling interrupts without correct status-clear/update sequencing can flood or lose fault records.
- Status and strobe bits require sequencing. Invalidation, fault-status clear, RMI config update, and error-injection controls need the polling/ordering rules from the owning driver code and hardware spec; the macros do not encode those rules.
- RAS counters and ECC index fields can be read from the wrong register bank or instance if the consumer uses the wrong hub, xcc/instance, or SOC15 block index.
- The chunk boundary hides neighboring definitions. The final report must connect this chunk to the previous GDS fields and the following remainder of `VM_CONTEXT4_CNTL` plus subsequent VM context registers before claiming complete coverage.

## Test Signals

Useful validation signals are mostly integration and hardware bring-up tests:

- Build AMDGPU and KFD with GC 9 support enabled. Missing or renamed macros should fail in `gfxhub_v1_0.c`, `mmhub_v1_0.c`, `gmc_v9_0.c`, `gfx_v9_0.c`, and GC 9 KFD queue-management files.
- Boot GC 9 hardware and verify GART/VM initialization succeeds: VM contexts enable, page-table depth/block size match expectations, GPU virtual memory mappings work, and TLB flush paths complete without timeout.
- Exercise VM fault handling through invalid, permission, read, write, execute, dummy-page, and range faults. Check that `VM_L2_PROTECTION_FAULT_STATUS` and address registers identify the expected VMID/client/fault type and that interrupts/default handling follow policy.
- Run graphics rendering with tiled, compressed, MSAA, depth/stencil, fast-clear, and DCC surfaces. Incorrect GB/DB/CB/RB masks would show as corruption, hangs, failed clears, bad compression, or mismatched topology.
- Validate suspend/resume and GPU reset paths, because tile-mode/topology tables, VM L2 controls, context controls, and fault policy must be restored consistently after reset-domain loss.
- Run RAS/ECC diagnostics where available, including GDS EDC and VM L2 ECC count queries, and verify SEC/DED counters move in the expected fields.
- Check RMI/UTCL1/XNACK behavior under compute memory pressure and page migration/retry scenarios. Relevant signals include RMI busy/error status, scoreboard flush state, UTCL1 fault/retry/PRT detection, and XNACK-per-VMID reporting.

## Cross-Chunk Notes

This chunk starts in the middle of the GDS EDC area at `GDS_EDC_GRBM_CNT__UNUSED_MASK`, so complete GDS analysis needs the previous chunk. It ends after the first seven `VM_CONTEXT4_CNTL` shift definitions and before the corresponding masks and later VM context registers, so complete VM context-control analysis needs the next chunk. The merge/reconciliation lane should join those boundaries before producing the final per-file research document.

### subset-b-002618: lines 7181-9637

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 7181-9637

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains only C preprocessor constants: hardware register fields are represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for composing and decoding 32-bit graphics-core register values. There are no functions, structs, enums, includes, local variables, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin inside the tail of `VM_CONTEXT4_CNTL`, then cover most of the GPUVM context-control and invalidate-engine field definitions, UTCL2/VM memory-aperture controls, TCP/TCI/TCC/TCA cache and coherency controls, and the start of shader-program state for pixel and vertex shaders. The chunk ends in the middle of `SPI_SHADER_PGM_RSRC2_VS`; the remaining VS resource masks continue in a later chunk. Although the path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_9_0_sh_mask.h` supplies the bit layouts for GC 9.0 graphics IP registers. AMDGPU code pairs these masks with register addresses from the matching GC 9.0 offset header and uses common helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, and `SOC15_REG_OFFSET` to avoid hard-coded bit positions in VM setup, TLB invalidation, shader setup, cache configuration, reset, diagnostics, and hang analysis.

This chunk describes several major hardware surfaces:

- GPUVM contexts 4 through 15, including context enablement, page-table depth and block size, retry behavior, and protection-fault interrupt/default controls for range, dummy page, PDE0, valid, read, write, and execute faults.
- `VM_CONTEXTS_DISABLE`, which provides per-context disable and preserve-mode controls for contexts 0 through 15.
- Invalidate engines 0 through 17, including semaphore state, invalidate request fields, acknowledge fields, and optional invalidate address-range low/high halves.
- VM page-table base, start, and end addresses for contexts 0 through 15.
- VM shared/decode controls for MMIO, PCI, DRAM, framebuffer, system aperture, HBM aperture, virtual reset, memory low-power, steering, and L1 TLB behavior.
- TCP/TCI/TCC/TCA cache hierarchy controls, status, invalidation, channel steering, address hashing, load/store/atomic policy fields, volatile markers, EDC counters, DSM controls, redundancy, execution disable, writeback/invalidate, soft reset, and burst controls.
- Shader processor interface state for PS and VS: program resource descriptors, program-address low/high fields, user-data dword windows, CU masks, wave limits, late allocation, SGPR/VGPR sizing, float/debug/trap/exception controls, scratch, stream-out, and draw/dispatch enable bits.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index of a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw bit mask for that field.
- Register address macros live in the companion GC 9.0 offset header and are consumed alongside these field definitions.

Important macro families in this chunk include:

- `VM_CONTEXT4_CNTL` tail and `VM_CONTEXT5_CNTL` through `VM_CONTEXT15_CNTL`: repeated per-VMID context controls. Fields include `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry controls, and interrupt/default enables for protection-fault classes.
- `VM_CONTEXTS_DISABLE`: `DISABLE_CONTEXT0` through `DISABLE_CONTEXT15` plus matching `PRESERVE_CONTEXT*` fields, used to gate or preserve VM contexts across programming sequences.
- `VM_INVALIDATE_ENG*_SEM`: one-bit semaphore fields for invalidate engines 0 through 17.
- `VM_INVALIDATE_ENG*_REQ`: invalidate-request fields for each engine, including `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0/1/2`, `INVALIDATE_L1_PTES`, and `CLEAR_PROTECTION_FAULT_STATUS_ADDR`.
- `VM_INVALIDATE_ENG*_ACK`: per-VMID invalidate acknowledge masks.
- `VM_INVALIDATE_ENG*_ADDR_RANGE_LO32/HI32`: range-invalidation address fragments, with low dword fields split into a 12-bit reserved/alignment field and a 20-bit base field, and high dword fields carrying the upper address bits.
- `VM_CONTEXT*_PAGE_TABLE_BASE_ADDR_LO32/HI32`, `VM_CONTEXT*_PAGE_TABLE_START_ADDR_LO32/HI32`, and `VM_CONTEXT*_PAGE_TABLE_END_ADDR_LO32/HI32`: context page-table roots and aperture boundaries.
- `MC_VM_*`, `MC_SHARED_VIRT_RESET_REQ`, and `MC_MEM_POWER_LS`: VM shared aperture, PCI/DRAM/framebuffer, HBM, steering, reset, and memory low-power register fields.
- `MC_VM_MX_L1_TLB_CNTL`: L1 TLB enable, system-access, request, arbitration, invalidation, fragment, and policy fields.
- `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, `TCP_CHAN_STEER_LO/HI`, `TCP_ADDR_CONFIG`, `TCP_CREDIT`, `TCP_BUFFER_ADDR_HASH_CNTL`, and `TCP_EDC_CNT`: texture cache invalidation, status, control, steering, address, credit, hash, and EDC fields.
- `TC_CFG_L1_LOAD_POLICY*`, `TC_CFG_L1_STORE_POLICY`, `TC_CFG_L2_LOAD_POLICY*`, `TC_CFG_L2_STORE_POLICY*`, `TC_CFG_L2_ATOMIC_POLICY`, `TC_CFG_L1_VOLATILE`, and `TC_CFG_L2_VOLATILE`: cache policy and volatile-state layouts for L1/L2 load, store, and atomic behavior.
- `TCI_STATUS`, `TCI_CNTL_1`, and `TCI_CNTL_2`: texture cache interface status and control fields.
- `TCC_CTRL`, `TCC_CTRL2`, `TCC_EDC_CNT`, `TCC_EDC_CNT2`, `TCC_REDUNDANCY`, `TCC_EXE_DISABLE`, `TCC_DSM_CNTL*`, `TCC_WBINVL2`, and `TCC_SOFT_RESET`: L2 cache control, counters, redundancy/repair, data-share module policy, writeback/invalidate, and reset fields.
- `TCA_CTRL`, `TCA_BURST_MASK`, `TCA_BURST_CTRL`, `TCA_DSM_CNTL*`, and `TCA_EDC_CNT`: texture cache arbiter control, burst behavior, DSM control, and EDC fields.
- `SPI_SHADER_PGM_RSRC3_PS`, `SPI_SHADER_PGM_LO_PS`, `SPI_SHADER_PGM_HI_PS`, `SPI_SHADER_PGM_RSRC1_PS`, `SPI_SHADER_PGM_RSRC2_PS`, and `SPI_SHADER_USER_DATA_PS_0` through `SPI_SHADER_USER_DATA_PS_31`: pixel-shader program address, resources, CU/wave controls, scratch/trap/exception controls, LDS sizing, and 32 dword user-data windows.
- `SPI_SHADER_PGM_RSRC3_VS`, `SPI_SHADER_LATE_ALLOC_VS`, `SPI_SHADER_PGM_LO_VS`, `SPI_SHADER_PGM_HI_VS`, `SPI_SHADER_PGM_RSRC1_VS`, and the visible beginning of `SPI_SHADER_PGM_RSRC2_VS`: vertex-shader CU/wave controls, program address, resource sizing, VGPR component count, CU group enable, scratch, user SGPR, trap, on-chip LDS, stream-out base enable, exception, PC-base, dispatch/draw, and user-SGPR packing fields.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 9.0 generated register headers for the detected ASIC.
2. Obtain a register address from the matching offset header or an IP-specific register table.
3. Use these `__SHIFT` and `_MASK` constants, usually through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract fields.
4. Read or write the register via MMIO helpers, SOC15 address helpers, indexed access, command packets, firmware-mediated programming, debugfs, or register-dump paths.

For GPUVM setup, driver code programs per-context page-table base/start/end registers and context control fields, then uses invalidate engine request and acknowledge registers to flush stale PTE/PDE/TLB state. The visible `gmc_v9_0_get_invalidate_req()` consumer pattern builds `VM_INVALIDATE_ENG0_REQ` values by setting per-VMID invalidate, flush type, L2 PTE/PDE invalidation, L1 PTE invalidation, and protection-fault-status clear fields. `gfxhub_v1_0` style setup also derives per-context and per-engine register distances from the context and invalidate register families, so the repeated layouts in this chunk are part of an array-like hardware programming model.

For the MC, TCP, TCI, TCC, and TCA sections, initialization, golden-register, power-management, reset, and diagnostic code read or write cache, TLB, steering, coherency, EDC, DSM, burst, redundancy, and reset controls. The macros define bit positions only; they do not encode ordering constraints such as cache idle waits, writeback/invalidate completion, soft-reset pulse sequencing, or reserved-bit preservation.

For the SPI shader-program registers, graphics pipeline setup writes program base addresses, per-stage resource descriptors, user SGPR counts, scratch/trap/exception controls, stream-out enables, CU masks, wave limits, and user-data registers before shader waves are launched. These fields are normally driven by command streams, compiler metadata, firmware, or driver state setup rather than by standalone logic in this header.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware-visible register state whose lifetime is controlled by GPU reset, power management, context programming, firmware, command submission, and driver reinitialization.

GPUVM context control, page-table base/start/end, VM aperture, and L1 TLB control registers persist until reprogrammed or reset. They define which VMIDs are enabled, how deep their page tables are, which address ranges are legal, where their page tables live, and how protection faults are surfaced. Bad values can prevent address translation, misroute faults, disable contexts, point VMIDs at the wrong page tables, or hide faults behind default behavior.

Invalidate request, acknowledge, semaphore, and address-range fields are synchronization surfaces. Request bits can be written to initiate flushes, acknowledge bits report completion, and semaphore fields coordinate invalidate engine ownership. These registers are volatile and side-effecting from the driver's perspective; stale polling, wrong VMID masks, or incorrect range packing can leave stale translations active or make the driver wait on the wrong completion bits.

MC shared/aperture and cache hierarchy controls are persistent hardware policy. TCP/TCI/TCC/TCA status and EDC counters are live or sticky observation state, while invalidate, writeback, reset, DSM, redundancy, and execution-disable fields can have immediate side effects. Full-register writes are risky because many controls share registers with reserved or unrelated policy bits.

Shader program registers are persistent graphics pipeline state for the current draw or context. Program address low/high halves, resource descriptors, CU/wave limits, VGPR/SGPR sizing, scratch enablement, trap/exception settings, stream-out enables, late allocation, and user-data dwords must match the compiled shader and command stream. A single shifted field error can allocate the wrong resources, corrupt user SGPR mapping, launch the wrong code address, enable the wrong stream-out bases, or make traps and exceptions unobservable.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.0 register set remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` supplies matching register offsets and base-index metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_default.h`, where present for related registers, supplies generated reset/default values.
- AMDGPU field helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` consume the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming pattern.
- MMIO and SOC15 helpers such as `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, and IP-version dispatch tables provide the register access path around these constants.

Concrete integration points include:

- `gmc_v9_0` VM invalidation code, which composes `VM_INVALIDATE_ENG0_REQ` fields for per-VMID TLB/PTE/PDE flushes.
- `gfxhub_v1_0` setup code, which maps GC VM context, page-table, invalidate request, and acknowledge registers into the generic AMDGPU VM hub abstraction and relies on the repeated register spacing.
- GART/VMID setup, fault interrupt configuration, page-table programming, context disable/preserve handling, and GPU reset recovery.
- Golden-register and power-management paths that program MC aperture, TCP/TCC/TCA cache, TLB, low-power, EDC, redundancy, or soft-reset controls.
- Register dump, debugfs, hang triage, and performance diagnostics that decode TCP/TCC/TCA status/counters, invalidate acknowledgements, and shader resource state.
- Graphics command submission and shader setup paths that program PS/VS `SPI_SHADER_PGM_*` and `SPI_SHADER_USER_DATA_*` registers from compiler output and command stream state.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes or decodes the wrong hardware bit.
- The chunk starts and ends mid-family. It begins after the `VM_CONTEXT4_CNTL` marker and early fields, and it ends before the remaining `SPI_SHADER_PGM_RSRC2_VS` masks. Adjacent chunks are required for complete family-level documentation.
- The VM context controls are highly repetitive. Copy/paste or generator errors in one context can affect only specific VMIDs, making failures workload- or process-dependent.
- Invalidate engine fields are synchronization-critical. Mispacking `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, L1/L2 invalidation bits, or acknowledge masks can leave stale translations active, clear the wrong fault address status, or hang invalidate waits.
- Address fields are split into low/high halves and may have alignment or unit constraints not represented by full masks. `0xFFFFFFFFL` or broad address masks do not mean arbitrary byte addresses are valid.
- Context disable/preserve bits can interact badly with reset, suspend/resume, SR-IOV, or VM fault recovery if callers treat them as passive state.
- Cache/TLB/DSM/EDC/redundancy/reset fields can be volatile, sticky, write-one-to-clear, pulse-style, or side-effecting depending on hardware semantics not encoded here.
- TCP/TCC/TCA policy registers affect coherency and performance. Wrong load/store/atomic policy, volatile, hash, credit, burst, or DSM fields may cause subtle data hazards or severe performance regressions rather than immediate crashes.
- Shader resource descriptors must match compiler metadata. Incorrect VGPR/SGPR counts, float mode, exception bits, scratch enable, LDS sizing, user SGPR count, or stream-out enables can corrupt execution, lose traps, or break draws only for specific shader stages.
- Reserved bits appear throughout these dense registers. Consumers should preserve reserved bits during read-modify-write unless a documented programming sequence requires a full-register value.

## Test Signals

Useful validation combines generated-data checks, build coverage, and hardware runtime behavior:

- Build AMDGPU code paths that include `gc_9_0_sh_mask.h` and `gc_9_0_offset.h`; missing or renamed macros should fail at compile time.
- Mechanically compare this line range against AMD's authoritative GC 9.0 register database. Every visible field should have aligned `__SHIFT` and `_MASK` entries.
- Cross-check registers in this chunk against `gc_9_0_offset.h` for matching address definitions and expected repeated spacing for VM contexts, invalidate engines, and shader user-data windows.
- Static sanity checks for repeated families: VM contexts 5-15 should share the same control layout, invalidate engines 0-17 should share request/ack/semaphore layouts, context page-table base/start/end pairs should have consistent low/high fields, and `SPI_SHADER_USER_DATA_PS_0` through `_31` should remain full-width data fields.
- GPUVM tests should cover GART enable/disable, VMID setup, per-VMID invalidate request/ack polling, range invalidation where supported, protection-fault reporting, and reset/suspend/resume recovery.
- Memory stress tests should verify no stale translations or coherency failures after PTE/PDE updates, context disable/preserve transitions, and cache/TLB invalidations.
- Cache and coherency validation should exercise TCP/TCC/TCA invalidation, writeback/invalidate, EDC counter readout, DSM policy, volatile policy, and soft reset paths while watching for stuck busy/status bits or repeated GPU resets.
- Shader execution tests should cover PS and VS resource programming, user SGPR/user-data mapping, scratch usage, trap/exception behavior, stream-out paths, CU masks, wave limits, late allocation, and program-address packing.
- Debug and hang-triage signals include correct decode of invalidate acknowledgements, VM fault status, TCP/TCC/TCA status/counters, shader resource registers, and absence of unexpected protection-fault storms, rendering corruption, shader launch failures, cache incoherency, or reset loops.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002618`. It covers lines 7181-9637 of `gc_9_0_sh_mask.h`. The previous chunk owns the beginning of `VM_CONTEXT4_CNTL`, and a later chunk owns the remainder of `SPI_SHADER_PGM_RSRC2_VS` plus following shader/register definitions. The final per-file research should reconcile those artificial boundaries before describing the complete generated GC 9.0 shift/mask map.

### subset-b-002619: lines 9638-12160

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 9638-12160

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains C preprocessor constants only: hardware register fields are represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for packing and decoding 32-bit register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines start inside `SPI_SHADER_PGM_RSRC2_VS`, after the corresponding shift definitions and the first masks from the previous chunk, then cover shader user-data and shader-program-resource fields for VS/GS/ES/HS/LS/common shader stages, compute dispatch/program-resource fields, and a large command-processor (`gc_cppdec`) block. The range ends in the `gc_cppdec2` block after `CP_SD_CNTL`; the next register, `CP_SOFT_RESET_CNTL`, starts immediately after the selected range. This boundary matters because several register families are split across adjacent chunks.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM graphics-core hardware metadata and is unrelated to Ceph or distributed filesystem logic.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for GC 9.0 graphics hardware. Driver code pairs these masks with register addresses from the matching GC 9.0 offset header and uses helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` instead of open-coded shifts and masks.

This chunk covers three broad programming surfaces:

- Shader stage setup for graphics pipelines. The macros describe user SGPR payload registers, shader program base addresses, shader resource registers, LDS/scratch/trap controls, CU/SIMD enable masks, wave limits, exception masks, stream-out controls, and stage-to-stage VGPR component counts for vertex, geometry, export, hull, and local shader paths.
- Compute dispatch state. The macros describe dispatch initiator flags, grid dimensions, start/restart coordinates, thread-group dimensions, pipeline-stat/perfcount enables, compute program address and resources, VMID, resource limits, static thread-management masks per shader engine, temporary-ring sizing, thread tracing, dispatch identifiers, relaunch state, wave-restore addresses, and 16 compute user-data registers.
- Command processor state. The macros describe deferred-write/data-fabric registers, CP interrupt control and status, UTCL1 controls and errors, graphics and compute ring-buffer bases/control/read and write pointers, doorbell controls and ranges, priority and VMID mapping, active-ring state, per-ring and per-pipe interrupts, ECC first-occurrence reporting, program-counter and interrupt-routine start addresses, context/VMID/preemption controls, CPC instruction-cache controls, MEC interrupt-disabling fields, VMID preemption status, scheduler doorbells, MQD base/control fields, and CP-side UTCL1 status.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the raw mask for that field inside the 32-bit register value.
- Matching register addresses are supplied by the sibling GC 9.0 offset header. Consumers include this file from GFX9 AMDGPU and KFD code such as `gfx_v9_0.c`, `soc15.c`, `amdgpu_amdkfd_gfx_v9.c`, `kfd_mqd_manager_v9.c`, `gmc_v9_0.c`, `gfxhub_v1_0.c`, `mxgpu_ai.c`, and Vega10 power-management include paths.
- AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, `SOC15_REG_OFFSET`, and direct mask tests rely on these shift/mask names being exact.

Important register groups in this range include:

- `SPI_SHADER_USER_DATA_VS_0` through `SPI_SHADER_USER_DATA_VS_31`, `SPI_SHADER_USER_DATA_ES_0` through `SPI_SHADER_USER_DATA_ES_31`, `SPI_SHADER_USER_DATA_LS_0` through `SPI_SHADER_USER_DATA_LS_31`, `SPI_SHADER_USER_DATA_COMMON_0` through `SPI_SHADER_USER_DATA_COMMON_31`, and `COMPUTE_USER_DATA_0` through `COMPUTE_USER_DATA_15`: full-width user-data payload registers passed to shader stages or compute dispatches.
- `SPI_SHADER_PGM_LO_*` and `SPI_SHADER_PGM_HI_*` for ES, GS, LS, and HS: low and high fragments of shader program base addresses. The high fragments in this chunk expose 8-bit `MEM_BASE` fields.
- `SPI_SHADER_PGM_RSRC1_GS` and `SPI_SHADER_PGM_RSRC1_HS`: shader resource fields for VGPR/SGPR allocation, priority, floating-point mode, privilege, DX10 clamp, debug/IEEE modes, CU group enable, component count, CDBG user bit, and FP16 overflow behavior.
- `SPI_SHADER_PGM_RSRC2_GS_VS`, `SPI_SHADER_PGM_RSRC2_GS`, and `SPI_SHADER_PGM_RSRC2_HS`: scratch enable, user SGPR count, trap presence, exception enables, LDS sizing, on-chip LDS enable, user SGPR skipping, and high-bit SGPR count fields. GS variants also encode GS/ES or GS/VS VGPR component-count details.
- `SPI_SHADER_PGM_RSRC3_GS` and `SPI_SHADER_PGM_RSRC3_HS`: CU enable, wave limit, lock-low threshold, and SIMD disable fields. The GS layout places `CU_EN` in low bits, while HS places wave/lock/SIMD fields in low bits and `CU_EN` in the high half.
- `SPI_SHADER_PGM_RSRC4_GS` and `SPI_SHADER_PGM_RSRC4_HS`: late allocation and FIFO-depth style controls, including GS group FIFO depth and shader late allocation.
- `COMPUTE_DISPATCH_INITIATOR`, `COMPUTE_DIM_X/Y/Z`, `COMPUTE_START_X/Y/Z`, `COMPUTE_NUM_THREAD_X/Y/Z`, and `COMPUTE_RESTART_X/Y/Z`: compute dispatch dimensions, offsets, thread-group sizes, restart coordinates, and initiation flags such as order mode, thread tracing, force-start, compute-shader WAVES, and ordered append-enable bits.
- `COMPUTE_PGM_LO`, `COMPUTE_PGM_HI`, `COMPUTE_DISPATCH_PKT_ADDR_*`, `COMPUTE_DISPATCH_SCRATCH_BASE_*`, `COMPUTE_WAVE_RESTORE_ADDR_*`: compute program, packet, scratch, and wave-restore address fields.
- `COMPUTE_PGM_RSRC1` and `COMPUTE_PGM_RSRC2`: compute shader resource allocation and behavior fields, including VGPRs, SGPRs, priority, float mode, private/debug/IEEE bits, bulk VGPR fields, scratch, user SGPRs, trap, TGID enable bits, LDS size, TIDIG component count, exception enables, TG size enable, and temporary ring enable.
- `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_STATIC_THREAD_MGMT_SE0` through `SE3`, and `COMPUTE_TMPRING_SIZE`: CU masking, wave limits, SIMD distribution, per-SE static thread management, and scratch wave/item sizing.
- `COMPUTE_THREAD_TRACE_ENABLE`, `COMPUTE_MISC_RESERVED`, `COMPUTE_DISPATCH_ID`, `COMPUTE_THREADGROUP_ID`, `COMPUTE_RELAUNCH`, and `COMPUTE_NOWHERE`: debug/trace, dispatch identification, threadgroup tracking, relaunch, and sink-register fields.
- `CP_DFY_*`: command-processor deferred-write/data-fabric address, data, control, status, and command fields.
- `CPC_INT_INFO`, `CPC_INT_ADDR`, `CPC_INT_PASID`, `CPC_INT_CNTL`, `CPC_INT_STATUS`, and `CPC_INT_CNTX_ID`: CPC interrupt context, ring ID, VMID, PASID, and interrupt enable/status fields.
- `CP_GFX_ERROR`, `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, `CPF_UTCL1_CNTL`, `CPG_UTCL1_ERROR`, `CPC_UTCL1_ERROR`, and the `gc_cppdec2` `*_UTCL1_STATUS` registers: CP-side GPU virtual memory, retry, PRT, fault, no-execute, snoop, invalidate, and halt/error reporting.
- `CP_RB0_BASE`, `CP_RB_BASE`, `CP_RB1_BASE`, `CP_RB2_BASE`, their `_HI`, `_CNTL`, read-pointer-address, write-pointer, buffer-size, active, and VMID registers: graphics ring-buffer placement, sizing, cache policy, pointer update, and activity state.
- `CP_RB_DOORBELL_CONTROL`, `CP_RB_DOORBELL_RANGE_LOWER/UPPER`, `CP_MEC_DOORBELL_RANGE_LOWER/UPPER`, `CP_RB_DOORBELL_CONTROL_SCH_0` through `SCH_7`, and `CP_RB_DOORBELL_CLEAR`: doorbell offset, enable, hit, BIF drop, valid-range, scheduler queue, and clear fields.
- `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING0/1/2`, `CP_INT_STATUS_RING0/1/2`, `CP_ME1_PIPE*_INT_CNTL/STATUS`, `CP_ME2_PIPE*_INT_CNTL/STATUS`, `CP_ME1_INT_STAT_DEBUG`, and `CP_ME2_INT_STAT_DEBUG`: command-processor interrupt enable/status bitmaps for timestamp, opcode, privilege, reserved-bit, GPF, ECC, queue/dequeue, query, context, generic, and idle/busy events.
- `CP_ME*_PIPE_PRIORITY_CNTS`, `CP_RING_PRIORITY_CNTS`, `CP_ME*_PIPE*_PRIORITY`, and `CP_RING*_PRIORITY`: ring and pipe priority counters and priority selectors.
- `CP_FATAL_ERROR`, `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_ECC_FIRSTOCCURRENCE*`, `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, `CP_CPF_DEBUG`, `CP_PQ_WPTR_POLL_CNTL*`: fatal-error gating, power/sleep controls, ECC capture, EDC configuration, CPF debug, and write-pointer polling controls.
- `CP_CE_PRGRM_CNTR_START`, `CP_PFP_PRGRM_CNTR_START`, `CP_ME_PRGRM_CNTR_START`, `CP_MEC1_PRGRM_CNTR_START`, `CP_MEC2_PRGRM_CNTR_START`, and the matching interrupt-routine start registers: micro-engine program-counter and interrupt entry-point address fields.
- `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_IQ_WAIT_TIME1/2`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, `CP_PQ_STATUS`, and `CP_CPC_IC_*`: context-switching, queue/preemption, VMID reset/status, PQ status, and CPC instruction-cache base/control/operation fields.
- `CP_MEC1_F32_INT_DIS` and `CP_MEC2_F32_INT_DIS`: disable bits for MEC fatal/interrupt sources such as EDC ROQ/TC/GDS/scratch/DMA/SR memory errors, privilege/reserved-bit errors, wave restore, SUA violation, IQ timer, GPF CPF/DMA/CPC, queue message, and fatal EDC error.
- `CP_GFX_MQD_CONTROL`, `CP_GFX_MQD_BASE_ADDR`, `CP_GFX_MQD_BASE_ADDR_HI`, `CP_RB_STATUS`, and `CP_SD_CNTL`: scheduler/graphics MQD VMID and execution/cache policy, MQD base address, ring doorbell status, and CP sub-block enable bits for CPF, CPG, CPC, RLC, SPI, WD, IA, PA, RMI, and EA.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Include the GC 9.0 register offset and shift/mask headers for a GFX9 ASIC.
2. Select a hardware register address such as `mmCP_INT_CNTL_RING0`, `mmCP_RB_DOORBELL_CONTROL`, or a compute/shader register from the offset header.
3. Use this file's shift/mask macros, usually through `REG_SET_FIELD` or `REG_GET_FIELD`, to compose or decode a register value.
4. Read or write the register through MMIO, RLC-safe accessors, KFD queue-loading paths, command-stream programming, debugfs/register dump code, firmware setup, reset flows, or power-management sequences.

Representative GFX9 consumers show the pattern: `gfx_v9_0_enable_gui_idle_interrupt()` reads `mmCP_INT_CNTL_RING0`, sets `CNTX_BUSY_INT_ENABLE`, `CNTX_EMPTY_INT_ENABLE`, `CMP_BUSY_INT_ENABLE`, and sometimes `GFX_IDLE_INT_ENABLE`, then writes the register back. `gfx_v9_0` ring setup programs `mmCP_RB_DOORBELL_CONTROL` by writing `DOORBELL_OFFSET` and `DOORBELL_EN`, then programs the lower and upper doorbell ranges. KFD MQD setup uses compute and CP queue masks such as `COMPUTE_PGM_RSRC2__TRAP_PRESENT__SHIFT`, `COMPUTE_RESOURCE_LIMITS__FORCE_SIMD_DIST_MASK`, and HQD/doorbell fields from the same generated header family.

Ordering requirements are outside this file. For example, programming a ring buffer requires memory allocation, write-pointer backing storage, base address writes, buffer-size control, doorbell range setup, and enable sequencing in driver code. This header only names the bits used by those sequences.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- Shader program, resource, and user-data registers are context/programming state for graphics shader stages. Values persist in the relevant hardware context until rewritten, context-switched, reset, or power-gated. User-data registers are full 32-bit payloads whose interpretation depends on shader ABI and command-stream setup.
- Compute dispatch and program-resource registers are per-dispatch or queue/context state. Dimensions, start/restart coordinates, dispatch IDs, scratch bases, wave-restore addresses, resource limits, static thread-management masks, and user data are live state consumed by compute scheduling and shader execution.
- CP ring-buffer base/control, read-pointer, write-pointer, buffer-size, polling, active, priority, and VMID fields are persistent queue-management state until the driver reprograms the ring, disables it, resets CP, or the GPU loses state.
- Doorbell enable, offset, hit, range, and scheduler-control bits are hardware interface state shared with CPU-visible doorbell writes. `HIT` and status-like fields may be set asynchronously by hardware when doorbells arrive.
- CP interrupt enable fields are persistent masks until changed or reset; status fields represent live or sticky hardware events depending on the specific register semantics. This header does not state whether a bit is write-one-to-clear, clear-on-read, sticky, or level-sensitive.
- UTCL1 error/status registers expose GPU virtual memory, retry, and PRT events from CP sub-blocks. Status can change asynchronously with memory traffic and fault handling.
- ECC, EDC, fatal-error, and first-occurrence fields expose error capture and error-routing state. Incorrect writes can suppress critical error reporting or leave stale captured state.
- Program-counter and interrupt-routine start registers configure CP micro-engine execution surfaces and persist until microcode reload, CP reset, or driver/firmware reprogramming.
- `CP_SD_CNTL` enables or disables major command-processor sub-blocks; these bits are high-impact persistent controls rather than passive status.

Reserved or undocumented fields appear throughout this generated range. Callers should preserve reserved bits during read-modify-write unless the hardware programming guide provides a full-register value.

## Dependencies And Integration Points

Primary dependencies:

- The matching GC 9.0 offset header supplies register addresses; this file supplies only bit layout.
- AMDGPU's common register-field helpers depend on the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` spelling.
- The generated values must remain synchronized with AMD's GC 9.0 register database and the actual ASIC stepping targeted by the including driver path.

Integration points in this repository include:

- `amdgpu/gfx_v9_0.c`: core GFX9 graphics-ring setup, CP interrupt toggling, GUI idle interrupt handling, ring buffer and doorbell programming, reset/resume paths, and register access through `RREG32_SOC15`/`WREG32_SOC15`.
- `amdgpu/amdgpu_amdkfd_gfx_v9.c` and `amdkfd/kfd_mqd_manager_v9.c`: KFD queue/MQD setup, compute queue doorbells, HQD loading, compute trap/user-resource setup, resource limits, and force-SIMD-distribution policy.
- `amdgpu/soc15.c`, `gmc_v9_0.c`, and `gfxhub_v1_0.c`: SOC15/GFX9 initialization and memory-management paths that include the same generated masks for VM/fault/status handling.
- `amdgpu/mxgpu_ai.c` and `amdgpu/amdgpu_amdkfd_arcturus.c`: virtualization and ASIC-specific GFX9-family paths.
- `pm/powerplay/hwmgr/vega10_inc.h`: Vega10 power-management code that includes GC 9.0 register definitions for graphics-core power/clock interactions.
- Hardware firmware and command processor microcode expectations. CP micro-engine program-counter, interrupt-routine, instruction-cache, ring, and MQD fields must agree with firmware ABI and register database definitions.

## Risks

- Bitfield drift is the main risk. If a shift or mask differs from the hardware register database, `REG_SET_FIELD` can silently program the wrong bits, affecting shader execution, queue scheduling, interrupts, VM fault handling, or doorbell delivery.
- Split chunk boundaries can hide incomplete register definitions. This range begins after part of `SPI_SHADER_PGM_RSRC2_VS` and ends before `CP_SOFT_RESET_CNTL`; merge tooling must combine adjacent chunk research before treating the whole file as covered.
- Full-width user-data and address fields are easy to misuse because the header does not encode address alignment, high/low address composition, GPU virtual-vs-physical address rules, or shader ABI interpretation.
- Doorbell fields are sensitive. Wrong offsets, ranges, or enable bits can make rings fail to wake, receive another queue's doorbell, drop BIF doorbells, or leave stale hit state.
- CP ring-buffer sizing and pointer fields control command fetch. Incorrect buffer-size masks, read/write pointer addresses, cache policy, or no-update bits can cause hangs, lost command processing, or memory corruption.
- Interrupt masks and status fields are high impact. Enabling the wrong interrupt can flood IRQ handling; disabling privilege, opcode, GPF, ECC, EDC, or reserved-bit error reporting can hide hardware or userspace faults.
- VMID, PASID, preemption, and context-control fields cross process isolation boundaries. Misprogramming these fields can attribute faults incorrectly, preempt the wrong context, or break queue isolation.
- `CP_SD_CNTL`, fatal-error, reset, and EDC/ECC controls can alter global graphics-core behavior. They should be changed only inside validated initialization, reset, or recovery flows.
- The generated header lacks type checking. A macro from a similarly named but different ASIC generation or register family can compile while programming an incompatible bit layout.

## Test Signals

Useful validation signals for changes touching this area include:

- Build coverage for GFX9 AMDGPU/KFD paths with this header included, catching missing or renamed generated macros at compile time.
- Boot or module-load logs for GFX9 ASICs such as Vega, Raven, or Arcturus showing successful graphics and KFD initialization without CP, RLC, ring, VM, or firmware errors.
- Graphics ring tests that submit command buffers and verify fences, write pointers, read pointers, timestamp interrupts, and GUI idle interrupt behavior.
- KFD compute queue tests that create/destroy queues, ring doorbells, dispatch kernels, exercise trap-present and resource-limit paths, and validate MQD/HQD programming.
- Doorbell tests or diagnostics that confirm configured doorbell offsets/ranges match ring and queue indices and that doorbell-hit/status bits behave as expected.
- GPU VM fault tests that exercise CPG/CPC/CPF UTCL1 fault, retry, PRT, PASID, and VMID reporting without corrupting unrelated queue state.
- Suspend/resume, GPU reset, and hang-recovery tests, because ring buffer, CP context, interrupt masks, doorbells, and shader/compute state must be reprogrammed correctly after state loss.
- Error-injection or RAS tests for ECC/EDC/fatal-error paths, especially first-occurrence and MEC F32 interrupt-disable fields.
- Register-dump/debugfs checks comparing programmed CP ring, interrupt, VMID, and doorbell fields against expected decoded values from `REG_GET_FIELD`.

### subset-b-002620: lines 12161-14705

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 12161-14705

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for packing and decoding 32-bit GPU register values. There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the tail of command processor soft-disable/reset/control fields, then cover generated address blocks for `gc_spipdec`, `gc_cpphqddec`, `gc_didtdec`, `gc_gccacdec`, `gc_tcpdec`, `gc_gdspdec`, `gc_rasdec`, and the beginning of `gc_gfxdec0`. Across lines 12161-14705 the chunk defines 2,152 macros for 370 distinct register names. The dominant register families are `GDS`, `SPI`, `CP`, `DB`, `TCP`, `GC`, `PA`, and `RAS`. Although this file lives under a `ceph-client` source mirror, this path is AMDGPU DRM hardware metadata, not Ceph filesystem logic.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for the AMD graphics core 9.0 register set. Driver code combines these field definitions with register addresses from the matching `gc_9_0_offset.h` header and uses AMDGPU register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to build MMIO values, command-packet payloads, queue descriptors, golden-register settings, debug reads, and status decoders.

This chunk describes several hardware areas:

- Command processor disable/reset and graphics/compute queue state: `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, `CP_CPC_GFX_CNTL`, and a large `CP_HQD_*` block for hardware queue descriptors.
- SPI arbitration, debug/trap, wave-control, compute-queue reset, resource reservation, and compute wave context-save controls.
- DIDT/CAC/EDC power, droop, clock-gating, and indirect access registers for graphics-core power/thermal control.
- TCP cache/watchpoint, GATCL1, UTCL1, and perf-counter filter fields.
- GDS, GWS, and OA per-VMID base/size/mask allocation registers, reset masks, context-switch status/counters, and max-wave/resource state.
- RAS signature controls and signature capture registers for major GC blocks.
- Depth-buffer, stencil, PA scissor/clip/window, coherent destination, texture border-color base, and color-target mask fields in the start of `gc_gfxdec0`.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask, usually within a 32-bit register.
- Companion register-address macros come from `gc_9_0_offset.h`; default/reset values come from `gc_9_0_default.h` where generated.

Important macro groups in this chunk are:

- `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, and `CP_CPC_GFX_CNTL`: enable/disable bits for CPF/CPG/CPC/RLC/SPI/WD/IA/PA/RMI/EA, compute and graphics soft-reset controls, HQD register/doorbell reset bits, and CPC queue/pipe/ME/valid selection.
- `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_*`, `SPI_CDBG_SYS_*`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_GDBG_*`, `SPI_RESET_DEBUG`, `SPI_COMPUTE_QUEUE_RESET`, `SPI_RESOURCE_RESERVE_CU_*`, `SPI_RESOURCE_RESERVE_EN_CU_*`, `SPI_COMPUTE_WF_CTX_SAVE`, and `SPI_ARB_CNTL_0`: SPI scheduling, pipe allocation, debug/trap matching, VMID stall/trap selection, compute queue reset, CU reservation masks/enables, context-save enablement, and arbitration controls.
- `CP_HQD_*`, `CP_HPD_*`, and `CP_MQD_*`: hardware queue descriptor control and status, MQD base address and processing state, VMID/VQID selection, persistent queue state, pipe/queue priority, quantum, packet queue base/read/write pointers, doorbell control, indirect buffer control, IQ timers, dequeue requests, DMA/offload controls, semaphores, HQ scheduler/status/control, EOP buffer state, context-save backing addresses/sizes, GDS resource state, UTCL1 error reporting, AQL controls, and PQ write pointers.
- `DIDT_IND_*`, `GC_CAC_*`, `GC_DIDT_*`, `GC_EDC_*`, `GC_*_DROOP_CTRL`, and `SE_CAC_*`: indirect index/data paths, current/activity counters, TDP and CAC windows, DIDT/EDC enables, reset/clock overrides, power thresholds, weightings for SQ/DB/TD/TCP/DBR, rolling droop/power status, overflow counters, and shader-engine CAC clock/indirect controls.
- `TCP_WATCH[0-3]_*`, `TCP_GATCL1_*`, `TCP_UTCL1_*`, `TCP_CNTL2`, `TCP_ATC_EDC_GATCL1_CNT`, and `TCP_PERFCOUNTER_FILTER*`: texture cache watchpoint address/mask/VMID/mode/valid fields, GATCL1 invalidation/force-miss/order/cache-size controls, UTCL1 page-size/permission/response/invalidation/client/ack/snoop behavior, low-power clock disable bits, EDC counts, and perf-counter matching/enables for buffer/flat/dimension/format/sample/opcode/cache/compression/address-mode fields.
- `GDS_VMID*_BASE`, `GDS_VMID*_SIZE`, `GDS_GWS_VMID*`, `GDS_OA_VMID*`, `GDS_GWS_RESET*`, `GDS_GWS_RESOURCE_RESET`, `GDS_COMPUTE_MAX_WAVE_ID`, `GDS_OA_RESET_MASK`, `GDS_OA_RESET`, `GDS_ENHANCE`, `GDS_OA_CGPG_RESTORE`, `GDS_*_CTXSW_STATUS`, and `GDS_*_CTXSW_CNT*`: GDS memory partitioning by VMID, global wave sync allocation, ordered-append resource masks, reset controls, compute max wave ID, context-switch watermarks/status, counter pointers, and OA clock/power-gating restore settings.
- `RAS_SIGNATURE_CONTROL`, `RAS_SIGNATURE_MASK`, and `RAS_*_SIGNATURE*`: signature collection enable/mask and full-width signature registers for SX, DB, PA, VGT, SQ, SC, IA, SPI, TA, TD, CB, and BCI blocks.
- `DB_RENDER_CONTROL`, `DB_COUNT_CONTROL`, `DB_DEPTH_VIEW`, `DB_RENDER_OVERRIDE*`, `DB_HTILE_DATA_BASE*`, `DB_DEPTH_SIZE`, `DB_*_CLEAR`, `DB_Z_INFO*`, `DB_STENCIL_INFO*`, `DB_*_READ_BASE*`, `DB_*_WRITE_BASE*`, and `DB_DFSM_CONTROL`: depth/stencil clear/copy/decompress, zpass/fail counters, slice/mip/read-only view state, HiZ/HiS/render overrides, HTILE and Z/stencil backing memory, clear values, surface format/swizzle/PRT/fault/expclear/tile settings, and punchout/overflow behavior.
- `TA_BC_BASE_ADDR*`, `COHER_DEST_BASE*`, `PA_SC_*`, `PA_SU_HARDWARE_SCREEN_OFFSET`, and `CB_TARGET_MASK`: texture border-color base addresses, coherent destination base high/low fields, viewport/window/generic clip rectangle and edge-rule fields, screen offset, and per-render-target channel write masks. The final line in this chunk stops inside the `CB_TARGET_MASK` family, so adjacent chunks are needed for the remaining masks.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select GC 9.0 register headers for the detected ASIC.
2. Choose a register address from `gc_9_0_offset.h`.
3. Read an existing register, prepare an indexed/debug operation, or construct a command/MMIO write value.
4. Use the `__SHIFT` and `__MASK` constants, commonly through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract field values.
5. Apply the value during graphics/compute queue setup, KFD queue management, GDS allocation, power/thermal programming, TLB/cache control, golden-register initialization, suspend/resume, reset/recovery, debugfs reads, perf monitoring, hang dumps, or draw/dispatch state programming.

For the `CP_HQD_*` block, runtime code typically programs MQD/HQD base addresses and queue metadata, establishes VMID and priority, configures PQ/IB/EOP buffers and doorbells, enables the queue, and later observes status/error/read-pointer fields during scheduling, preemption, dequeue, or recovery. The masks also support context-save and GDS resource handoff state used when queues are suspended or restored.

For SPI and TCP debug/status/control fields, consumers sequence selectors and enable bits around live hardware. Trap/debug masks, VMID filters, resource reservation registers, and perf-counter filters persist as programmed policy, while busy/fault/retry/PRT/status fields can change asynchronously with GPU execution.

For DIDT/CAC/EDC, initialization and power-management code programs thresholds, windows, weights, and clock overrides. Status and overflow fields are then sampled to determine throttle/droop behavior. The indirect index/data registers imply ordered index-then-data accesses; the header does not encode that sequencing.

For GDS/GWS/OA, queue and KFD paths program per-VMID allocations and reset masks. Context-switch counters/status fields are read or restored around queue switches. Incorrect sequencing can expose one VMID's GDS/GWS/OA resources to another or leave resources allocated after reset.

For DB/PA/CB start-of-gfxdec state, draw setup paths program depth/stencil surfaces, clear values, scissor/clip/window rules, coherent destination bases, and target write masks before rasterization and export. These fields become persistent graphics pipeline state until the next command stream changes them or the GPU is reset.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, command submission, and AMDGPU initialization/recovery code.

Queue and command-processor fields are persistent queue state. Base addresses, high-address halves, read/write pointers, doorbell offsets, EOP buffers, context-save backing stores, priorities, VMIDs, and cache policies must stay coherent with MQD memory and command processor expectations. Status/error bits such as UTCL1 faults, queue idle, pending semaphore, dequeue state, and doorbell hit are live or sticky hardware state and may require hardware-specific clearing outside this header.

SPI resource reservation, trap, debug, wave context-save, and compute reset bits can affect wave scheduling and debug behavior across queues. Some fields are selector/configuration state; others trigger reset or dequeue behavior when written. The header only gives bit positions, not side-effect semantics.

DIDT/CAC/EDC fields persist as power/thermal policy. Bad windows, weights, thresholds, or clock overrides can cause excessive throttling, disabled protection, power/performance regressions, or hard-to-debug hangs under load.

TCP and UTCL1 fields persist as cache/TLB policy. Invalidation toggles, force-miss/snoop/order controls, page-size defaults, fault response modes, and cache-size/fifo reductions affect memory-system coherency and performance. Watchpoint registers are debug state keyed by address, mask, VMID, ATC, mode, and valid bits.

GDS/GWS/OA fields persist as per-VMID resource allocation and reset state. Context-switch counters and status fields expose transient save/restore state, while base/size/mask registers define the hardware-visible resource partitioning for queues.

RAS signature registers expose captured diagnostic state. The full-width signature fields should be treated as hardware-generated values, while `RAS_SIGNATURE_CONTROL` and `RAS_SIGNATURE_MASK` alter what is captured.

DB/PA/CB fields persist as graphics pipeline state. Surface base addresses, formats, swizzle modes, PRT/fault behavior, clear/decompress/copy controls, scissor rectangles, clip rules, and target masks must match the command stream and memory layout. Several DB fields can also preserve or invalidate compression metadata and hierarchical depth/stencil state.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.0 register set remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_default.h` provides reset/default values for related registers where generated.
- Common AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, indirect register helpers, and golden-register programming tables consume these field definitions.
- Runtime integration includes AMDGPU GFX 9 initialization, compute ring and KFD queue setup, MQD/HQD management, graphics and compute preemption, doorbell programming, VMID/TLB fault handling, GDS allocation, RAS diagnostics, power management, perf counters, debugfs/hang dumps, and draw-state emission.

The queue fields integrate with MES/KFD and kernel queue scheduling paths that create MQDs, map doorbells, program HQDs, and recover stuck queues. The TCP/UTCL1 fields integrate with GPUVM fault handling, cache invalidation, memory attribute policy, and performance monitoring. The GDS/GWS/OA fields integrate with KFD resource allocation and context switching. The DB/PA/CB fields integrate with graphics command emission and render-backend/depth-buffer programming.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles successfully but writes the wrong hardware bits or decodes status incorrectly.
- This chunk starts after the first `CP_SD_CNTL` field and ends mid-`CB_TARGET_MASK`; adjacent chunks are required for complete family context.
- Similar repeated families are not interchangeable. `SPI_RESOURCE_RESERVE_CU_*`, `GDS_VMID*`, `GDS_GWS_VMID*`, `GDS_OA_VMID*`, `TCP_WATCH*`, and per-stage GDS context-switch counters follow patterns but still encode distinct hardware registers.
- Full-width address/data masks do not imply arbitrary values are valid. Many address fields have alignment, aperture, high/low split, VMID, cache policy, or command-packet ordering constraints outside this header.
- Doorbell, queue pointer, EOP, and context-save fields can corrupt scheduling state if programmed while a queue is active or if the MQD/HQD memory image disagrees with the hardware registers.
- Reset and dequeue fields can have write-triggered side effects. The macros do not identify write-one-to-clear, sticky, clear-on-read, or self-clearing behavior.
- UTCL1/TCP invalidation and fault-response fields are coherency-sensitive. Misprogramming can produce stale memory, spurious GPUVM faults, PRT/retry anomalies, or performance collapse.
- DIDT/CAC/EDC controls affect power safety and throttling. Incorrect thresholds or disabled enables may only fail under high-power workloads.
- GDS/GWS/OA partitioning mistakes can cause inter-VMID resource leakage, failed queue launches, deadlocks around ordered append/global wave sync, or stale allocation state after reset.
- DB render override, compression, expclear, PRT, swizzle, and base-address fields can cause rendering corruption rather than immediate crashes.
- RAS signature values are diagnostic and may be volatile or capture-window dependent; tests should not assume stable values without controlling the input mask and workload.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for AMDGPU files that include `gc_9_0_sh_mask.h`, especially GFX 9 queue, KFD, GPUVM, GDS, RAS, power-management, perf-counter, reset, and graphics draw-state paths.
- Mechanical comparison against AMD's authoritative GC 9.0 register database to confirm every `__SHIFT` and `__MASK` in lines 12161-14705.
- Cross-checks that every register family in this chunk has matching address macros in `gc_9_0_offset.h` and expected reset/default entries in `gc_9_0_default.h` where generated.
- Static mask/shift sanity checks: masks align with shifts, fields do not overlap unexpectedly, repeated VMID/watchpoint/context-counter families stay internally consistent, full-width fields use `0xFFFFFFFFL`, and high/low address halves have expected widths.
- Queue bring-up tests for CP HQD/MQD/PQ/IB/EOP/doorbell programming, including KFD compute queues, graphics queues, dequeue/preemption, context save/restore, and GPU reset recovery.
- Fault and diagnostic tests that exercise `CP_HPD_UTCL1_ERROR`, `CP_HQD_ERROR`, TCP/UTCL1 fault/retry/PRT status, and RAS signature capture under controlled workloads.
- SPI scheduling/debug tests that validate arbitration fields, compute queue reset, CU resource reservation, trap masks, wave context-save behavior, and debug selector reads.
- Power and throttling tests for CAC/DIDT/EDC programming under sustained graphics/compute workloads, checking throttle levels, droop status, overflow counters, and clock override recovery across suspend/resume.
- GDS/GWS/OA tests covering per-VMID base/size/mask allocation, ordered append/global wave sync resources, reset masks, max wave ID, and context-switch counters.
- TCP/cache tests covering watchpoints, GATCL1/UTCL1 invalidation, forced miss/snoop/order controls, page-size defaults, perf-counter filters, and memory-coherency stress.
- Graphics rendering tests covering depth/stencil clear/copy/decompress, HTILE, depth bounds, expclear, PRT/fault behavior, scissor/clip/window rules, coherent destination bases, and color target masks.
- Runtime warning signals include stuck queues, doorbell hits not advancing write pointers, HQD UTCL1 errors, stale or leaked GDS resources, unexpected throttling, TCP fault/retry/PRT spikes, corrupted depth/stencil output, and repeated GPU resets.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002620`. It covers lines 12161-14705 of `gc_9_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to restore the beginning of the `CP_SD_CNTL` family before line 12161 and the remaining `CB_TARGET_MASK`/following `gc_gfxdec0` fields after line 14705.

### subset-b-002621: lines 14706-17177

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 14706-17177

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains C preprocessor constants only: each register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for composing or decoding 32-bit GPU register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the tail of `CB_TARGET_MASK` mask definitions, then cover a large graphics-pipeline state block: color-buffer target and shader masks, scissor and viewport state, raster/tile steering, command-processor context IDs, color/depth/stencil/blend controls, viewport transforms, user clip planes, pixel shader interpolation inputs, SPI shader export formats, SX blend optimizations, draw initiator fields, depth/color shader controls, clipping/setup controls, and the beginning of VGT tessellation state. Although the path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata, not Ceph filesystem logic.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for the GC 9.0 graphics IP. Driver code pairs these masks with register addresses from the matching `gc_9_0_offset.h` header and uses AMDGPU register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to pack fields before MMIO writes, command-packet programming, or firmware setup, and to decode status/debug reads.

This chunk describes the late fixed-function and shader-interface state used by draw setup:

- CB target/shader output enable masks and per-MRT blend constants, blend equations, color control, DCC overwrite-combiner behavior, down-conversion, blend optimization epsilon/control, MRT blend optimization, and expanded pitch.
- PA/SC scissor, viewport Z bounds, raster mapping, screen extents, tile steering, grid quantization, line stipple, point/line sizing, primitive filtering, small-primitive filtering, over-rasterization, and setup/clipping modes.
- CP pipe/ring/VMID and performance-monitor context fields that associate packet execution with hardware context state.
- DB stencil, stencil reference/masks, depth test/write control, EQAA/sample control, and pixel-shader depth/stencil/coverage export policy.
- PA/CL viewport scale/offset registers for 16 viewports, six user clip-plane vectors, clip control, viewport transform enablement, vertex output control, NaN/Inf policy, object/primitive ID control, NGG control, and early tessellation path fields.
- SPI pixel-shader input control for up to 32 parameters, VS output export count, pixel shader input enable/address masks, interpolation control, barycentric control, temporary ring size, and shader export formats.
- VGT draw state such as multi-primitive reset index, DMA base, draw initiator, immediate data, event address, output path selection, and beginning hull/tessellation state.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- Register-address symbols are provided by the companion GC 9.0 offset header and are consumed by AMDGPU MMIO helpers, packet builders, golden-register programming, command submission, and debug paths.

Notable macro families in this slice are:

- `CB_TARGET_MASK` tail and `CB_SHADER_MASK`: per-render-target write enables and per-shader-output enables for MRT color export routing.
- `PA_SC_GENERIC_SCISSOR_*` and `PA_SC_VPORT_SCISSOR_{0..15}_*`: top-left/bottom-right scissor windows with `WINDOW_OFFSET_DISABLE` on the top-left registers.
- `COHER_DEST_BASE_{0,1}`: full-width destination base fields used by coherency/copy paths.
- `PA_SC_VPORT_ZMIN_{0..15}` and `PA_SC_VPORT_ZMAX_{0..15}`: full-width viewport depth bounds.
- `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_SCREEN_EXTENT_CONTROL`, and `PA_SC_TILE_STEERING_OVERRIDE`: render-backend, packer, shader-engine, screen-slice, and tile-steering mapping fields.
- `CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, and `CP_VMID`: command processor context/performance and queue identity fields.
- `PA_SC_RIGHT_VERT_GRID`, `PA_SC_LEFT_VERT_GRID`, and `PA_SC_HORIZ_GRID`: grid-quarter/half fields used by rasterization quantization.
- `VGT_MULTI_PRIM_IB_RESET_INDX`, `VGT_DMA_BASE_HI`, `VGT_DMA_BASE`, `VGT_DRAW_INITIATOR`, `VGT_IMMED_DATA`, `VGT_EVENT_ADDRESS_REG`, `VGT_OUTPUT_PATH_CNTL`, `VGT_HOS_CNTL`, `VGT_HOS_MAX_TESS_LEVEL`, `VGT_HOS_MIN_TESS_LEVEL`, and the start of `VGT_HOS_REUSE_DEPTH`: draw setup, event, path, and tessellation fields.
- `CB_BLEND_RED/GREEN/BLUE/ALPHA`, `CB_BLEND{0..7}_CONTROL`, `CB_COLOR_CONTROL`, `CB_DCC_CONTROL`, `CB_MRT{0..7}_EPITCH`, `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, and `SX_MRT{0..7}_BLEND_OPT`: color output, blending, ROP, DCC, pitch, format conversion, and blend optimization fields.
- `DB_STENCIL_CONTROL`, `DB_STENCILREFMASK`, `DB_STENCILREFMASK_BF`, `DB_DEPTH_CONTROL`, `DB_EQAA`, and `DB_SHADER_CONTROL`: stencil operations/references, depth/stencil testing, sample/anchor configuration, depth export, kill/coverage/mask export, POPS, and early/late Z policy.
- `PA_CL_VPORT_{X,Y,Z}{SCALE,OFFSET}_{0..15}` and `PA_CL_UCP_{0..5}_{X,Y,Z,W}`: full-width viewport transform and user clip-plane coefficients.
- `SPI_PS_INPUT_CNTL_{0..31}`: pixel shader parameter interpolation metadata. Inputs 0-19 include offset/default/flat-shade/cylindrical-wrap/point-sprite/duplicate/FP16/default-attr1/valid fields, while inputs 20-31 omit the cylindrical-wrap and point-sprite texture fields in this slice.
- `SPI_VS_OUT_CONFIG`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, `SPI_BARYC_CNTL`, `SPI_TMPRING_SIZE`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT`: shader export counts, pixel input component enable/address bits, interpolation mode, barycentric behavior, temporary ring sizing, and position/depth/color export formats.
- `PA_CL_CLIP_CNTL`, `PA_SU_SC_MODE_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, `PA_SU_LINE_STIPPLE_CNTL`, `PA_SU_PRIM_FILTER_CNTL`, `PA_SU_SMALL_PRIM_FILTER_CNTL`, `PA_CL_OBJPRIM_ID_CNTL`, `PA_CL_NGG_CNTL`, `PA_SU_OVER_RASTERIZATION_CNTL`, `PA_SU_POINT_SIZE`, `PA_SU_POINT_MINMAX`, and `PA_SU_LINE_CNTL`: clip/cull/setup, vertex transform, vertex-output sideband use, NaN/Inf policy, primitive filtering, NGG vertex reuse, over-rasterization, point size, and line size/state.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 9.0 generated register headers for the detected ASIC.
2. Choose a register address from the matching offset header.
3. Read the current register value, construct a draw-state packet value, or prepare a direct MMIO write.
4. Use these `__SHIFT` and `__MASK` constants, typically through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract field values.
5. Apply the value during graphics pipeline setup, golden-register programming, command submission, context switching, reset/recovery, debugfs, hang analysis, or performance telemetry.

For viewport and scissor state, runtime command streams program up to 16 independent viewport rectangles and depth ranges. Clip/setup state then uses the viewport transform, clip-plane, scissor, culling, primitive-filter, and over-rasterization fields while PA/SC routes primitives to shader engines, packers, and render backends.

For pixel-shader input and export state, compiler and command-buffer setup cooperate: VS/GS output counts and formats, PS input enable/address masks, `SPI_PS_INPUT_CNTL_*`, interpolation and barycentric controls, shader color/Z/position export formats, and CB/DB shader-control bits must agree with the compiled shader's parameter exports and pixel shader inputs.

For DB/CB/SX state, the graphics path programs depth/stencil tests, sample/EQAA policy, coverage/mask/depth export policy, color write masks, DCC overwrite-combiner settings, ROP/color control, per-MRT blend functions, blend constants, down-conversion, and blend optimization before drawing. These macros do not express the packet ordering, cache flushes, synchronization, or hardware-specific validation that higher-level AMDGPU and Mesa/UMD command generation must provide.

For VGT draw and tessellation state, the command processor and graphics ring write index-buffer reset values, DMA base fields, draw initiator bits, immediate data, event addresses, output path, and hull/tessellation settings as part of draw launch. This chunk ends immediately after the `VGT_HOS_REUSE_DEPTH__REUSE_DEPTH__SHIFT` definition; the matching mask is outside the chunk.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, kernel command submission, user-mode graphics drivers, and AMDGPU initialization/recovery code.

Most registers in this slice are persistent draw or context state. Scissor rectangles, viewport transforms, user clip planes, raster config, setup control, SPI interpolation state, CB/DB/SX color/depth/blend controls, and VGT draw/tessellation controls persist until a later command stream, context switch, reset, or init path overwrites them. Incorrect read-modify-write handling can preserve stale bits across draws or lose reserved bits that the hardware expects to remain unchanged.

Some fields represent live or context-identifying state. `CP_PIPEID`, `CP_RINGID`, `CP_VMID`, performance-monitor enablement, event addresses, and draw initiator fields connect register programming to queue identity, VM context, event signaling, and command processor execution. Stale or mismatched values can make debug data misleading or direct operations to the wrong context.

Color/depth state has strong cross-register persistence. For example, CB target masks, shader masks, shader export formats, blend controls, CB color control, DB shader control, depth/stencil control, and EQAA fields all describe one coherent pixel-output contract. A value may be individually well-formed but still wrong if it does not match the current shader, render target formats, sample count, or depth/stencil surface state.

Viewport, clipping, and setup fields also form a coupled persistent contract. `PA_CL_VPORT_*`, `PA_SC_VPORT_SCISSOR_*`, `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_SU_SC_MODE_CNTL`, point/line size registers, and primitive filters determine where primitives rasterize and which vertex sideband values are consumed. Bad field packing can silently cull geometry, choose the wrong viewport/render target index, or change DirectX/OpenGL clip-space behavior.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_default.h`, where present, provides reset/default values for related registers.
- Common AMDGPU helpers, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, packet-building helpers, and golden-register programming helpers, consume these field definitions.
- GC 9.0 AMDGPU code that includes this header includes graphics initialization, rings, command processor setup, reset/recovery, debug/hang dump paths, power-management golden settings, and KFD/graphics interop paths.

Integration points include graphics pipeline state emission from user-mode drivers, AMDGPU kernel validation and context management, render-backend and depth-buffer programming, shader compiler export/input metadata, graphics ring command packet generation, perf/debug register reads, GPU reset recovery, suspend/resume reinitialization, and golden-register tables for Vega-era GC 9.0 ASICs.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading diagnostics.
- The chunk starts and ends mid-family. It begins with only the final `CB_TARGET_MASK` target masks and ends after the `VGT_HOS_REUSE_DEPTH` shift without its mask. Adjacent chunks are required for complete per-file context.
- Repeated register families are easy to misindex. Viewport 0-15, scissor 0-15, pixel inputs 0-31, MRTs 0-7, blend controls 0-7, and clip planes 0-5 have similar layouts but not always identical fields.
- `SPI_PS_INPUT_CNTL_20` through `SPI_PS_INPUT_CNTL_31` have fewer fields than inputs 0-19 in this chunk. Code that assumes all 32 input-control registers accept cylindrical-wrap or point-sprite texture fields can set nonexistent bits.
- Full-width masks such as blend constants, viewport scale/offset, user clip-plane coefficients, immediate data, and tessellation levels do not imply unconstrained semantics. Values still need correct floating-point encoding, address units, alignment, shader ABI expectations, or packet sequencing.
- CB/DB/SX state must match render target and shader metadata. Mismatched color export formats, write masks, DCC settings, blend functions, ROP mode, depth/stencil exports, or EQAA sample fields can produce rendering corruption, disabled writes, incorrect alpha-to-coverage, or depth/stencil misbehavior.
- Raster and viewport state can cause silent data loss. Bad scissor bounds, viewport Z min/max, clip disable bits, cull modes, primitive filters, small-primitive filters, over-rasterization, point/line sizes, or NaN/Inf policy can make valid draws disappear or render outside expected regions.
- `CP_*` and event-address fields are context-sensitive. Incorrect VMID, ring/pipe identity, or event-address packing can corrupt debugging/perf attribution or signal the wrong memory address.
- Reserved and absent bits should be preserved unless a hardware programming sequence explicitly requires a full-register value. This generated mask header does not encode write-one-to-clear, read-only, sticky, or reserved-bit behavior.
- NGG, object/primitive ID, viewport/render-target index, GS cut flag, and line-width sideband bits depend on shader output conventions. Incorrect `PA_CL_VS_OUT_CNTL` or `PA_CL_OBJPRIM_ID_CNTL` programming can misroute primitives only on pipelines that use those sideband outputs.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for AMDGPU files that include `gc_9_0_sh_mask.h`, especially GC 9.0 graphics initialization, command processor, rings, reset, debug, KFD interop, and power-management paths.
- Mechanical comparison against AMD's authoritative GC 9.0 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that registers in this chunk have matching address macros in `gc_9_0_offset.h` and expected reset/default entries where generated.
- Static mask/shift sanity checks: masks align with shifts, repeated viewport/MRT/input families stay consistent, adjacent fields do not overlap unexpectedly, full-width fields use `0xFFFFFFFFL`, and sparse/reserved bits are intentional.
- Graphics bring-up and suspend/resume tests that verify golden-register writes for PA/SC, PA/CL, SPI, DB, CB, SX, and VGT state do not leave the GPU hung or produce unexpected busy/debug status.
- Render tests covering multiple render targets, color write masks, blend constants, per-MRT blending, ROP3, DCC, down-conversion, depth/stencil operations, stencil front/back masks, depth bounds, EQAA/MSAA, alpha-to-coverage, mask exports, and conservative/depth-before-shader behavior.
- Viewport/scissor tests for all 16 viewports, window-offset disable, viewport Z ranges, multi-viewport/render-target-index sideband outputs, clip/cull distances, user clip planes, DX clip-space definitions, rasterization kill, point size, line width, and line stipple.
- Shader interface tests that exercise PS input parameters 0-31, default attributes, flat shade, duplicate, FP16 interpolation, point sprites, barycentric control, input enable/address masks, VS export counts, position/Z/color export formats, and temporary ring sizing.
- Draw path tests for multi-primitive index-buffer reset, indirect/DMA base programming, immediate data, event address signaling, output path selection, tessellation min/max levels, and HOS reuse depth once the adjacent chunk supplies the full register.
- Runtime warning signals include missing color writes, incorrect blending, depth/stencil regressions, sample-count artifacts, geometry unexpectedly clipped or culled, viewport-index/render-target-index errors, shader interpolation corruption, point/line rasterization differences, event signaling faults, and GPU reset loops after graphics-state programming.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002621`. It covers lines 14706-17177 of `gc_9_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the `CB_TARGET_MASK` context before line 14706 and the `VGT_HOS_REUSE_DEPTH` mask and following VGT state after line 17177.

### subset-b-002622: lines 17178-19721

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 17178-19721

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for composing or decoding 32-bit GPU register values. There are no functions, structs, enums, global variables, includes, allocations, callbacks, locks, or executable branches in this range.

The selected lines begin at the tail of `VGT_HOS_REUSE_DEPTH`, then cover a large graphics pipeline state block: VGT primitive/group/tessellation/streamout controls, PA scan-converter/rasterizer controls, DB HTILE/stencil preload controls, color-buffer target state for `CB_COLOR0` through `CB_COLOR7`, and finally the beginning of the `gc_gfxudec` command-processor block through `CP_DRAW_INDX_INDR_ADDR`. Although the path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata, not Ceph filesystem code.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for Graphics Core 9.0 registers. AMDGPU code pairs these field macros with register-address macros from the matching `gc_9_0_offset.h` header, then uses common register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` or packet construction paths to pack fields for MMIO writes, command-stream state, clear-state tables, hang dumps, and status decoding.

This chunk describes several hardware areas:

- VGT geometry and vertex reuse state: primitive grouping, GS mode/on-chip controls, ES/GS/VS ratios, GS ring offsets and item sizes, primitive ID behavior, DMA/index draw sizing, draw payload controls, instance stepping, tessellation distribution, shader-stage enablement, LS/HS configuration, TF parameters, streamout setup, and geometry shader output sizing.
- PA scan-converter and setup state: MSAA, viewport/scissor, line stipple and line control, centroid priority, vertex quantization, clip/discard adjustment constants, sample locations/masks for four pixel positions, shader/rasterizer control, binner control, conservative rasterization, NGG mode, vertex reuse block, and output deallocation controls.
- DB/color-related context state: HTILE surface policy, stencil-results compare state, preload control, and alpha-to-mask.
- Eight color target slots, `CB_COLOR0` through `CB_COLOR7`, each with base/ext address fields, dimensions/view, format/number type/component swap/blend options, DCC/compression controls, CMASK/FMASK/DCC metadata bases, and clear words.
- `gc_gfxudec` command-processor state: EOP done/fence addresses and data, streamout and pipeline-stat counter addresses, 64-bit primitive/invocation counters, scratch registers, append/atomic/GDS preop registers, ME memory read/write address/data registers, semaphore wait/signal addresses, CP DMA controls and address/command fields, coherency/invalidation controls, ring/IB/CE/ST offsets and buffer sizes, EOP done event/data controls, PFP/CE completion status, predicate status, metadata base addresses, and the first indirect draw address register.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a register field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- Register addresses are defined separately in `gc_9_0_offset.h`, for example `mmVGT_GS_MODE`, `mmCB_COLOR0_INFO`, `mmCP_DMA_ME_COMMAND`, and `mmCP_DRAW_INDX_INDR_ADDR`.

Important macro families in this slice include:

- `VGT_GROUP_*`, `VGT_GS_MODE`, `VGT_GS_ONCHIP_CNTL`, `VGT_GS_PER_ES`, `VGT_ES_PER_GS`, `VGT_GS_PER_VS`, `VGT_GSVS_RING_OFFSET_*`, `VGT_GS_OUT_PRIM_TYPE`, and `VGT_GS_MAX_*`: geometry/primitive grouping, GS execution mode, on-chip GS sizing, and GS/VS ring layout.
- `VGT_DMA_*`, `VGT_PRIMITIVEID_*`, `VGT_DRAW_PAYLOAD_CNTL`, `VGT_INSTANCE_STEP_RATE_*`, `VGT_REUSE_OFF`, `VGT_VTX_CNT_EN`, `VGT_SHADER_STAGES_EN`, `VGT_LS_HS_CONFIG`, `VGT_TESS_DISTRIBUTION`, and `VGT_TF_PARAM`: draw indexing, primitive ID reset/generation, tessellation and shader-stage selection, vertex reuse, and instance-rate state.
- `VGT_STRMOUT_*`, `VGT_DMA_EVENT_INITIATOR`, and `VGT_STRMOUT_DRAW_OPAQUE_*`: streamout buffer sizing, stride, offsets, opaque draw accounting, stream/buffer enable masks, and event generation.
- `PA_SC_MODE_CNTL_*`, `PA_SC_LINE_CNTL`, `PA_SC_AA_CONFIG`, `PA_SC_CENTROID_PRIORITY_*`, `PA_SC_AA_SAMPLE_LOCS_PIXEL_*`, `PA_SC_AA_MASK_*`, `PA_SC_SHADER_CONTROL`, `PA_SC_BINNER_CNTL_*`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, and `PA_SC_NGG_MODE_CNTL`: scan conversion, sample placement, MSAA exposure, rasterization, binning, and NGG behavior.
- `PA_SU_*` and `PA_CL_GB_*`: setup/rasterizer point/line/polygon offset and guard-band clip/discard adjustment state.
- `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE*`, `DB_PRELOAD_CONTROL`, and `DB_ALPHA_TO_MASK`: depth/stencil metadata policy, preload thresholds, stencil compare state, and alpha-to-coverage behavior.
- `CB_COLOR{0..7}_BASE`, `*_BASE_EXT`, `*_ATTRIB2`, `*_VIEW`, `*_INFO`, `*_ATTRIB`, `*_DCC_CONTROL`, `*_CMASK`, `*_FMASK`, `*_DCC_BASE`, `*_CLEAR_WORD0`, and `*_CLEAR_WORD1`: per-render-target color-buffer addresses, metadata addresses, dimensions, slice/mip view, format, compression/DCC policy, swizzle modes, sample/fragment counts, and clear values.
- `CP_EOP_*`, `CP_STREAM_OUT_*`, `CP_NUM_PRIM_*`, `CP_PIPE_STATS_*`, and `CP_*INVOC_COUNT*`: command-processor writeback addresses/data and pipeline-stat counter plumbing.
- `SCRATCH_REG*`, `SCRATCH_UMSK`, `SCRATCH_ADDR`, `CP_APPEND_*`, `CP_ATOMIC_*`, `CP_GDS_ATOMIC*`, and `CP_ME_GDS_ATOMIC*`: CP scratch, append, and pre-operation data surfaces.
- `CP_SIG_SEM_*`, `CP_WAIT_SEM_*`, `CP_WAIT_REG_MEM_TIMEOUT`, `CP_DMA_*`, `CP_COHER_*`, `CP_RB_OFFSET`, `CP_IB*_OFFSET`, `CP_CE_*`, `CP_ST_*`, `CP_EOP_DONE_*`, `CP_PFP_COMPLETION_STATUS`, `CP_CE_COMPLETION_STATUS`, and `CP_PRED_NOT_VISIBLE`: synchronization, DMA copy/fill, coherency/invalidation, ring/IB/CE/ST command buffers, EOP completion, and predicate status.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 9.0 generated register headers for the detected ASIC.
2. Choose a register address from `gc_9_0_offset.h`.
3. Read the current register value or build a context/command-packet value.
4. Use these `__SHIFT` and `__MASK` constants, commonly through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract field values.
5. Write the value through MMIO, program it into a context/clear-state packet, emit it in a command stream, or decode it during diagnostics.

For VGT/PA/DB/CB context registers, normal flow is graphics pipeline setup before draw execution. The driver or userspace command stream programs vertex/index/tessellation/geometry/streamout, rasterization/MSAA/binning, depth/stencil metadata, and render-target descriptors so the hardware can launch and rasterize work with the expected target layout.

For the CP block, normal flow is command-processor synchronization and writeback setup. Runtime code programs EOP fence and event destinations, streamout/pipeline-stat counter writeback addresses, semaphore wait/signal targets, DMA source/destination/command fields, coherency flush ranges/actions, ring and indirect-buffer offsets, CE/ST command buffers, and completion/predicate status handling. The macros do not encode the required packet ordering, cache flush waits, VMID ownership, or engine-specific sequencing.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, ring initialization, command submission, and context switching.

VGT, PA, DB, and CB registers are mostly draw/context state. Values persist until another context or packet rewrites them, a clear-state sequence restores defaults, or the GPU resets. Incorrect render-target base/ext fields, metadata bases, swizzle modes, DCC/CMASK/FMASK settings, sample counts, slice/mip views, or clear words can corrupt memory, render into the wrong address, produce incorrect colors, or break compression/decompression. VGT/PA mistakes can produce malformed primitive assembly, missing geometry, incorrect streamout counters, wrong tessellation or GS behavior, bad sample coverage, and rasterizer/binning artifacts.

The CP registers represent command-processor state, counters, addresses, synchronization, and command-buffer bookkeeping. Fence and EOP writeback addresses/data, append/atomic preop registers, semaphore addresses, DMA source/destination addresses, coherency base/size/action fields, ring/IB offsets, CE buffer bases/sizes, and metadata/indirect-draw addresses persist until reprogrammed. Status fields such as completion, predicate, coherency status, DMA FIFO state, and read tags are live hardware state and may change while engines run.

Many full-width masks in this range are still semantically constrained. Address fields are split into low/high registers and frequently use alignment units such as 256-byte or 4-byte granularity. Counter and data fields may be latched or written by hardware. Control fields can trigger side effects, including DMA execution, cache invalidation/writeback, semaphore signaling/waiting, EOP writeback, and command-buffer loading.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.0 register set remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` provides matching register addresses and base indices.
- Other generated GC 9.0 headers, including defaults and enums where present, provide reset values and symbolic field values that consumers may pair with these masks.
- Common AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, command-packet builders, golden-register tables, and clear-state arrays consume these definitions.
- `drivers/gpu/drm/amd/amdgpu/clearstate_gfx9.h` contains clear-state values for related registers such as `VGT_GS_MODE`, `PA_SC_BINNER_CNTL_0`, and `CB_COLOR0_INFO`.

Integration points include graphics ring setup, context/clear-state emission, draw and indirect draw paths, tessellation/geometry/NGG setup, streamout, pipeline statistics queries, render-target and DCC/CMASK/FMASK metadata programming, MSAA sample position setup, depth/stencil metadata setup, CP DMA packets, EOP fence/event handling, semaphore synchronization, cache coherency events, indirect-buffer/ring management, constant-engine command buffers, predicate control, and hang/debug dumps.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading status.
- The chunk starts and ends mid-family. It begins after `VGT_HOS_REUSE_DEPTH__REUSE_DEPTH__SHIFT` and ends at `CP_DRAW_INDX_INDR_ADDR`; adjacent chunks are required for the complete HOS/tessellation context before line 17178 and the rest of the CP indirect draw/index/sample/GDS definitions after line 19721.
- The eight `CB_COLOR*` register families are structurally repetitive but target different render slots. Copy/paste or indexing mistakes can bind one slot's base/metadata/format to another slot.
- Full-register writes can damage reserved bits or unrelated fields. Many context registers should be updated through field helpers or known-good packet values rather than ad hoc constants.
- Address fields with `_BASE_256B`, `_ADDR_LO`, `_ADDR_HI`, or shifted low-address masks require correct alignment and high/low splitting. Incorrect packing can cause GPU writes to arbitrary memory.
- DCC, CMASK, FMASK, fast clear, blend optimization, sample/fragment count, swizzle mode, and pipe/RB alignment fields must match the actual BO layout and metadata allocation. Mismatches may appear as subtle corruption, not immediate faults.
- VGT GS/tessellation/streamout fields must match shader compiler output and pipeline state. Bad ring sizes, item sizes, stream masks, primitive IDs, or tessellation distribution can hang or lose geometry.
- PA sample-location, AA mask, centroid, conservative-raster, binner, and NGG fields affect coverage and primitive distribution; small field errors can create workload-specific rendering differences.
- CP DMA, coherency, semaphore, EOP, and IB/CE/ST fields have side effects. Misprogramming can lead to stale cache data, missed fences, stuck waits, invalid command buffer fetches, out-of-order memory visibility, or GPU reset loops.
- Live status/counter fields may be volatile or hardware-updated. Diagnostic reads need appropriate synchronization if they are used as test or recovery signals.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for AMDGPU paths that include `gc_9_0_sh_mask.h`, especially GC 9.0 graphics, clear-state, ring, CP DMA, fence, query, debug, reset, and KFD/compute integration paths.
- Mechanical comparison against AMD's authoritative GC 9.0 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that every register family in this chunk has matching address macros in `gc_9_0_offset.h` and expected default/clear-state entries where applicable.
- Static mask/shift sanity checks: masks align with shifts, fields in each register do not overlap unexpectedly, full-width fields use `0xFFFFFFFFL`, 256-byte and 4-byte address-unit fields have the expected low-bit masks, and repeated `CB_COLOR{0..7}` definitions stay slot-consistent.
- Graphics draw tests covering indexed and indirect draws, primitive ID reset/generation, tessellation, GS/on-chip GS, streamout, vertex reuse, NGG mode, binner transitions, conservative rasterization, line/point/polygon offset, MSAA sample locations, centroid selection, alpha-to-mask, and viewport/scissor behavior.
- Render-target stress tests covering all eight color slots, multiple mips/slices, MSAA fragments/samples, DCC enablement, fast clears, CMASK/FMASK metadata, clear words, swizzle modes, resource types, RB/pipe alignment, and blend optimization paths.
- Depth/stencil/HTILE tests that exercise HTILE surface policy, stencil compare state, preload controls, and interactions with color/alpha-to-mask output.
- Query and streamout tests that validate `CP_NUM_PRIM_*`, `CP_VGT_*`, `CP_PA_*`, `CP_SC_*`, `CP_PIPE_STATS_*`, streamout filled-size counters, and opaque streamout draw state.
- Synchronization tests for EOP fence writeback, event data selection, semaphore signal/wait, predicate state, PFP/CE completion status, CP DMA source/destination/cache policy, coherency base/size/action fields, and ring/IB/CE/ST buffer offsets.
- Runtime warning signals include bad render-target output, DCC/metadata corruption, lost streamout data, incorrect query counters, stuck CP coherency status, CP DMA FIFO saturation, missed EOP fences, semaphore timeouts, invalid indirect draw addresses, and repeated GPU resets.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002622`. It covers lines 17178-19721 of `gc_9_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the surrounding HOS/tessellation definitions before this range and the remaining command-processor indirect draw/index/GDS/sample-status definitions after this range.

### subset-b-002623: lines 19722-22327

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 19722-22327

## Scope

This chunk is a generated AMD GC 9.0 register shift/mask header slice. It contains C preprocessor `#define` constants only: for each named hardware register field, one `<REGISTER>__<FIELD>__SHIFT` macro and one `<REGISTER>__<FIELD>_MASK` macro define the field position and bit mask inside a 32-bit register value.

The selected range contains 2,123 `#define` statements covering 471 register-field groups. There are no functions, structs, enums, global variables, allocations, locks, direct MMIO operations, persistence formats, or executable branches in this range.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata. It is unrelated to Ceph filesystem protocols or storage behavior except by source-tree placement.

## Purpose

`gc_9_0_sh_mask.h` gives AMDGPU GC 9.0 code symbolic field positions for graphics-core registers. Driver code combines these masks with register offsets from `gc_9_0_offset.h` and SOC15 MMIO helpers to compose, read, decode, or modify register values without embedding raw bit numbers.

This chunk starts in the `gc_gfxudec` user/config command-processor and draw-state field definitions, then crosses these major surfaces:

- CP indirect draw/dispatch/index address fields, index type, GDS backup address fields, sample-status bits, and ME coherency command base/size/status fields.
- RLC GPM performance counter selector fields and `GRBM_GFX_INDEX`, which selects shader engine, shader array, and instance targets for indexed/broadcast register writes.
- VGT, WD, IA, PA, and screen/trap draw-state fields for primitive/index type, streamout filled sizes, index ranges, tessellation factor memory, work distributor buffers, multi-VGT setup, line stipple, screen extents, and trap-screen counters.
- SQ thread trace buffer, token, performance, mode, status, watermark, counter, and userdata fields.
- SQC cache/writeback controls, texture constant base fields, DB occlusion/Z-pass counters, and GDS read/write/atomic/GWS/OA fields.
- SPI configuration controls before the chunk switches into generated performance-counter address blocks.
- `gc_perfddec` performance-counter data fields for CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA/TD/TCP/TCC/TCA, CB, DB, RLC, and RMI counter low/high registers.
- UTCL2/ATCL2 and VM L2 counter fields for `ATC_L2_PERFCOUNTER_*` and `MC_VM_L2_PERFCOUNTER_*`.
- `gc_perfsdec` performance-counter selector, mode, window, filter, and global control fields for the same GC sub-blocks.
- The beginning of RLC streaming performance monitor fields: `RLC_SPM_PERFMON_CNTL`, ring base/size, and segment sizing.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` is the bit offset for `FIELD`.
- `<REGISTER>__<FIELD>_MASK` is the already-positioned bit mask for `FIELD`.
- `// addressBlock:` comments mark generated register-database block boundaries such as `gc_perfddec`, `gc_utcl2_atcl2pfcntrdec`, `gc_utcl2_vml2prdec`, and `gc_perfsdec`.

AMDGPU code normally consumes these macros through helpers such as `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` and `REG_GET_FIELD(value, REGISTER, FIELD)`, together with `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, `WREG32_SOC15_RLC_SHADOW`, `SOC15_REG_OFFSET`, and golden-register table macros.

Representative field families in this range include:

- Address low/high pairs: `CP_DRAW_INDX_INDR_ADDR_HI`, `CP_DISPATCH_INDR_ADDR`, `CP_INDEX_BASE_ADDR`, `CP_GDS_BKUP_ADDR`, `VGT_TF_MEMORY_BASE`, `WD_*_BUF_BASE`, `SQ_THREAD_TRACE_BASE`, `TA_CS_BC_BASE_ADDR`, and `RLC_SPM_PERFMON_RING_BASE_*`.
- Coherency fields: `CP_ME_COHER_CNTL` destination enables for generic bases, color-buffer destinations, DB destination, and additional destination bases; `CP_ME_COHER_SIZE*`, `CP_ME_COHER_BASE*`, and `CP_ME_COHER_STATUS`.
- Indexed addressing fields: `GRBM_GFX_INDEX__INSTANCE_INDEX`, `SH_INDEX`, `SE_INDEX`, and broadcast-write bits.
- Draw-state fields: `VGT_INDEX_TYPE`, `VGT_MULTI_PRIM_IB_RESET_EN`, `VGT_HS_OFFCHIP_PARAM`, `IA_MULTI_VGT_PARAM`, and line/screen/trap-state fields in `PA_SC_*` and `PA_SU_*`.
- SQ thread-trace fields: buffer size/base masks, token/perf masks, control/mode, status bits such as `BUSY`, `UTC_ERROR`, `FINISH_PENDING`, `DROPPED_CNTR`, and high-water/counter/userdata fields.
- GDS fields: direct read/write address/data/burst fields, atom control/source/destination/readback fields, GWS resource fields, and ordered-append counter/address/ring fields.
- Performance-counter data registers: almost all counter data fields are full-width 32-bit `PERFCOUNTER_*` low/high values, with repeated pairs by block and counter index.
- Performance-counter selector registers: repeated `PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`, `CNTR_MODE`, and `PERF_MODE*` fields across CPG/CPC/CPF/GRBM/WD/IA/VGT/PA/SPI/SQ/SX/GDS/TA/TD/TCP/TCC/TCA/CB/DB blocks.
- Filter and SPM fields: `CB_PERFCOUNTER_FILTER` operation/format/clear/MRT/sample/fragment filters, `SQ_PERFCOUNTER_CTRL*`, `SQ_PERFCOUNTER_MASK`, `CP_PERFMON_CNTL`, `CPF/CPG_TC_PERF_COUNTER_WINDOW_SELECT`, latency-stat selectors, and RLC SPM ring/sample/segment fields.

## Control Flow

This header has no runtime control flow. It only gives compile-time constants to code that performs register programming or decoding.

The implied runtime flow is:

1. GC 9.0 driver code chooses a register offset from the matching offset header and a field macro from this shift/mask header.
2. The code builds or extracts a field value with `REG_SET_FIELD`, `REG_GET_FIELD`, or explicit mask/shift arithmetic.
3. SOC15 register helpers issue the MMIO read, write, shadowed write, or indirect access against the selected GC instance.
4. The command processor, graphics pipeline, shader core, GDS, performance monitor, or RLC block interprets the resulting register value.

For draw-state and CP registers, the actual sequencing is owned by command submission, ring setup, fence/coherency emission, KFD compute queue setup, and graphics pipeline programming. For GRBM indexed writes, callers must select the correct SE/SH/instance or broadcast scope before accessing registers behind the GRBM index. For performance counters and thread trace, external profiling/debug paths handle counter selection, trace-buffer setup, sampling, start/stop, and readback; this chunk only names the bitfields.

## State And Persistence Behavior

The macros are stateless compile-time constants. Persistent or volatile state exists only in the GPU registers and in memory objects whose addresses are programmed through those registers.

State represented by this chunk includes indirect draw/dispatch/index pointers, ME coherency command windows, selected GRBM target instance, VGT/IA/WD/PA draw parameters, SQ thread-trace buffers and status, GDS read/write/atomic/OA/GWS control state, SPI configuration knobs, performance counter data and selection state, latency-stat selectors, counter windows, CB filtering, and RLC SPM ring/segment layout.

Some represented registers are durable configuration until rewritten, context-switched, power-gated, reset, or restored during suspend/resume. Others are counters, latches, status bits, command registers, readback FIFOs, or self-clearing controls. This generated header does not encode read-only, write-only, write-one-to-clear, sticky, privilege, broadcast, clock-domain, reset-default, or sequencing semantics; those rules live in hardware documentation and in the code paths that use these fields.

The mask definitions themselves must match the register database exactly. A stale mask can compile successfully while silently corrupting adjacent fields, missing high bits, or causing code to poll/decode the wrong status condition.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` supplies matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_default.h` and nearby generated headers provide related reset/default metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h` provides enum values for some GC 9.0 concepts, including SQ thread-trace token/mode types.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c` includes this header for GC 9.0 graphics initialization, golden settings, GRBM indexed targeting, RLC SPM programming, and register access setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v9.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v9.c` include it for KFD/compute queue and MQD-related GC 9.0 register programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.c`, `gfxhub_v1_0.c`, `gmc_v9_0.c`, `mxgpu_ai.c`, and `soc15.c` also include the GC 9.0 mask header.
- PowerPlay Vega10 integration includes it through `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`.

Observed direct use patterns in this source tree include `GRBM_GFX_INDEX` field composition in `gfx_v9_0.c` and `amdgpu_amdkfd_gfx_v9.c`, golden settings for `SPI_CONFIG_CNTL_1` and RLC SPM-related registers in `gfx_v9_0.c`, and explicit RLC SPM mask/shift arithmetic in `gfx_v9_0.c` around SPM VMID selection. Many performance-counter and SQ thread-trace definitions are integration points for profiling, debugging, and register-dump decoding even when they are not all referenced by current in-tree code.

Runtime integration points include graphics command submission, compute/KFD queue setup, GRBM broadcast and per-instance register access, GPU profiling/perfmon, SQ thread tracing, GDS atomics/OA/GWS diagnostics, cache/coherency events, streamout/tessellation/draw setup, RLC streaming performance monitor capture, debug register dumps, SR-IOV-capable GC 9.0 paths, reset, suspend/resume, and golden-register programming.

## Risks And Edge Cases

- Generated-header drift is the main risk. Wrong shifts or masks compile cleanly and can corrupt register fields at runtime.
- This chunk starts mid logical `gc_gfxudec` sequence at `CP_DRAW_INDX_INDR_ADDR_HI`; the low half `CP_DRAW_INDX_INDR_ADDR` is in the previous chunk.
- This chunk ends mid RLC SPM sequence at `RLC_SPM_PERFMON_SEGMENT_SIZE`; `RLC_SPM_SE_MUXSEL_*` and later SPM fields continue in the next chunk.
- Address-pair fields must be programmed consistently. Low/high masks for CP, VGT, WD, SQ trace, TA, and RLC SPM ring base registers can truncate or misplace GPU addresses if paired incorrectly.
- `GRBM_GFX_INDEX` controls broadcast versus per-SE/SH/instance access. A mask error or stale selected index can write only one hardware instance when broadcast was intended, or broadcast a per-instance update globally.
- Coherency fields in `CP_ME_COHER_*` are command-submission critical. Incorrect destination-enable or base/size masks can leave CB/DB or memory ranges unflushed, or flush the wrong range.
- Draw-state fields in VGT/IA/WD/PA are tightly coupled to packet streams and hardware primitive assembly. Mask errors can present as rendering corruption, hangs, missing primitives, or incorrect streamout/tessellation behavior.
- SQ thread trace and performance counter fields are mostly debug/profiling-facing, but they interact with trace buffer memory, sampling modes, high-water status, and dropped-counter indicators. Bad field definitions can lose trace data or mislead performance tooling.
- GDS read/write/atomic/OA/GWS fields affect shared GPU data resources. Incorrect atom size/base/operation/resource masks can corrupt GDS state or break synchronization diagnostics.
- Counter families are highly repetitive. Per-block/per-index selector fields differ subtly in width, especially between CB 9-bit event selectors and 10-bit selectors used by many other blocks.
- `RESERVED` fields appear in several registers. Callers should avoid relying on generated reserved masks as permission to write arbitrary values unless the hardware programming sequence explicitly requires it.
- Full-width `0xFFFFFFFFL` masks rely on C integer promotion behaving as intended in the existing kernel macro environment. Consumers should keep values unsigned where needed.

## Test Signals

Useful validation is mostly generated-data consistency plus GC 9.0 hardware exercise:

- Build AMDGPU configurations that include GC 9.0 support. Missing or malformed macros should surface in `gfx_v9_0.c`, KFD GC 9 code, SOC15 code, and PowerPlay Vega10 includes.
- Mechanically compare every shift/mask pair in this chunk against AMD's authoritative GC 9.0 register database.
- Cross-check every register field here against a matching register offset in `gc_9_0_offset.h`, especially at the chunk boundaries and address-block transitions.
- Verify repeated families for expected count and naming consistency: SQ thread-trace registers, GDS atom/OA/GWS registers, performance counter low/high pairs, selector/select1 variants, GRBM SE0-3 selectors, SQ counter selectors 0-15, and CB/DB counter selectors.
- Exercise `GRBM_GFX_INDEX` selection through debugfs or driver paths that target all instances versus one SE/SH/instance, confirming indexed writes land on the expected hardware block.
- Run graphics workloads that use indirect draw/dispatch, indexed draws, primitive restart, instancing, tessellation factor memory, streamout, scissor/screen extent state, and line/trap-related PA state.
- Exercise compute/KFD workloads that use queues, dispatch, GDS, and coherency operations on GC 9.0 ASICs.
- Run profiling and tracing paths that program SQ thread trace, performance counters, latency stats, CB filters, and RLC SPM ring capture; confirm counters increment, status bits decode correctly, trace buffers fill as expected, and dropped/error indicators are meaningful.
- Include reset, suspend/resume, preemption, and power/clock-gating cycles while checking that GRBM index, RLC SPM, SQ trace, and perf-counter state is saved, restored, or reinitialized by the appropriate driver paths.
- Decode known-good GC 9.0 register dumps with these masks and compare field extraction against reference tools.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002623`. The final per-file research should merge it with neighboring chunks for full `gc_9_0_sh_mask.h` coverage. The previous chunk owns the start of the indirect draw address group and earlier CP EOP/PFP/CE metadata fields. The next chunk continues the RLC SPM field definitions after `RLC_SPM_PERFMON_SEGMENT_SIZE`.

### subset-b-002624: lines 22328-24771

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 22328-24771

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is exposed as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for composing and decoding 32-bit MMIO register values. There are no functions, structs, enums, variables, includes, allocation sites, locks, callbacks, or executable branches in this line range.

The selected lines start in the middle of the `RLC_SPM_PERFMON_SEGMENT_SIZE` definition, after that register's field shifts were emitted by the previous chunk. They then cover RLC streaming performance monitor selection, sample-delay, ring, and perf-counter controls; RMI, ATC L2, and MC VM L2 performance counter fields; a large `gc_rlcpdec` RLC management/power/register-save block; and the beginning of the `gc_pwrdec` CGTS power-control register set through `CGTS_CU8_LDS_SQ_CTRL_REG`. The range ends mid-register, after `CGTS_CU8_LDS_SQ_CTRL_REG__SQ_OVERRIDE_MASK`, so the remaining masks for that register and later CGTS CU entries belong to a later chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM graphics-core hardware metadata and is unrelated to Ceph or distributed filesystem behavior.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for AMD graphics core 9.0 hardware registers. Driver code combines these macros with the matching register-offset definitions from `gc_9_0_offset.h` and AMDGPU helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` instead of hard-coding bit positions.

This chunk focuses on runtime graphics management and observability surfaces:

- RLC SPM configuration: segment sizes, per-block sample delays, mux select address/data windows, ring read pointers, segment thresholds, interrupt control/status, and memory-controller controls used by the streaming performance monitor path.
- RLC and RMI perf counters: RLC perfmon enable/state/sample controls, RLC counter selectors, RLC GPU IOV performance counter addressing/data fields, RMI performance counter selectors, modes, VMID/CID filters, event windows, burst thresholds, soft reset, and SPM selection.
- ATC L2 and MC VM L2 performance counters: counter configuration, range selection, enable/clear bits, result counter selection, trigger fields, clear-all, enable-any, and saturate-stop controls.
- RLC control and status: RLC enable/status/safe-mode handshakes, SMU/RLCV command and response fields, reference-clock timestamps, GPM timers, interrupt status, load-balancing, microcode flags, GPM thread reset/priority/enable, CP DMA completion bits, firewall violation capture, GPU clock counters, and power-gating status/control.
- RLC power, clock, and register-save machinery: MGCG/CGCG/CGLS controls, clock-gating overrides, power-gating delays and masks, dynamic/static CU power status and requests, SERDES register-save master masks/busy state, scratch/general registers, SRM command windows, CSIB address/length fields, SMU messages/arguments, prewalker UTCL1 programming, R2I controls, UTCL2 controls, and double-shift/load-balance status.
- RLC UTCL1 translation controls and errors: GPM/SPM/prewalker UTCL1 control registers, busy/stall status, translated request error code/VMID/address fields for SPM and GPM threads, and XNACK redo/drop/bypass/invalidate/snoop controls.
- CGTS power controls: top-level CGTS slow mode/read controls, TCC disable masks, and repeated per-CU control registers for shader processors, LDS/SQ, TA/SQC, and TD/TCPF low-power/busy override controls.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw bit mask for that field inside a 32-bit register value.
- Register addresses and base-index metadata come from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`.
- Consumers normally use these symbols through AMDGPU register helpers, including field pack/unpack helpers, `RREG32*`/`WREG32*` MMIO accessors, SOC15 offset helpers, indexed register accessors, power-management paths, profiling paths, firmware/RLC code, and debugfs/register-dump tooling.

Important register groups in this range include:

- `RLC_SPM_PERFMON_SEGMENT_SIZE`, `RLC_SPM_*_PERFMON_SAMPLE_DELAY`, `RLC_SPM_SE_MUXSEL_*`, `RLC_SPM_GLOBAL_MUXSEL_*`, `RLC_SPM_RING_RDPTR`, `RLC_SPM_SEGMENT_THRESHOLD`, `RLC_SPM_MC_CNTL`, `RLC_SPM_INT_CNTL`, and `RLC_SPM_INT_STATUS`: RLC SPM sizing, selection, sampling, ring, memory, and interrupt fields.
- `RLC_PERFMON_CLK_CNTL`, `RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER0_SELECT`, `RLC_PERFCOUNTER1_SELECT`, and `RLC_GPU_IOV_PERF_CNT_*`: RLC-local performance monitor state, counter selectors, and virtualization-aware counter read/write windows keyed by VFID and counter ID.
- `RMI_PERFCOUNTER*_SELECT`, `RMI_PERFCOUNTER*_SELECT1`, and `RMI_PERF_COUNTER_CNTL`: RMI performance event selection, counter modes, event windows, CID/VMID filters, burst thresholds, reset, and SPM routing.
- `ATC_L2_PERFCOUNTER*_CFG`, `ATC_L2_PERFCOUNTER_RSLT_CNTL`, `MC_VM_L2_PERFCOUNTER*_CFG`, and `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`: ATC and VM L2 performance counter programming surfaces.
- `RLC_CNTL`, `RLC_STAT`, `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `RLC_RLCV_COMMAND`, `RLC_SMU_COMMAND`, `RLC_SMU_MESSAGE`, `SMU_RLC_RESPONSE`, `RLC_SMU_ARGUMENT_1`, and `RLC_SMU_ARGUMENT_2`: RLC enable/status and command/response handshakes among RLC, RLCV, and SMU.
- `RLC_REFCLOCK_TIMESTAMP_*`, `RLC_GPM_TIMER_INT_*`, `RLC_GPM_TIMER_CTRL`, `RLC_GPM_TIMER_STAT`, `RLC_GPU_CLOCK_COUNT_*`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_GPU_CLOCK_32_RES_SEL`, and `RLC_GPU_CLOCK_32`: timestamp, timer, and clock-count capture fields.
- `RLC_GPM_STAT`, `RLC_PG_CNTL`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_STATIC_PG_STATUS`, `RLC_CU_STATUS`, `RLC_LB_INIT_CU_MASK`, `RLC_LB_ALWAYS_ACTIVE_CU_MASK`, `RLC_PG_ALWAYS_ON_CU_MASK`, `RLC_MAX_PG_CU`, `RLC_AUTO_PG_CTRL`, and `RLC_LBPW_CU_STAT`: power-gating, CU mask, load-balance, and live status fields.
- `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_CGCG_CGLS_CTRL_3D`, and `RLC_CGCG_RAMP_CTRL_3D`: medium-grain/coarse-grain clock-gating and light-sleep control, override, and ramp parameters.
- `RLC_SERDES_*`, `RLC_SRM_*`, `RLC_GPM_SCRATCH_*`, `RLC_GPM_GENERAL_*`, `RLC_CSIB_*`, and `RLC_JUMP_TABLE_RESTORE`: RLC register-save, scratch/general data, context-save instruction buffer, and restore-address fields.
- `RLC_GPM_UTCL1_CNTL_*`, `RLC_SPM_UTCL1_CNTL`, `RLC_PREWALKER_UTCL1_*`, `RLC_UTCL1_STATUS`, `RLC_UTCL1_STATUS_2`, `RLC_UTCL2_CNTL`, and `RLC_*_UTCL1_*ERROR_*`: RLC-facing translation/cache control and fault decode fields.
- `CGTS_SM_CTRL_REG`, `CGTS_RD_CTRL_REG`, `CGTS_RD_REG`, `CGTS_TCC_DISABLE`, `CGTS_USER_TCC_DISABLE`, and `CGTS_CU0_*` through the visible part of `CGTS_CU8_LDS_SQ_CTRL_REG`: CGTS slow-mode/readback, TCC disable, and per-CU block override/busy/light-sleep/SIMD-busy controls.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 9.0 generated register headers for the active ASIC.
2. Select a register address from `gc_9_0_offset.h`.
3. Use this file's shift/mask macros, usually through field helpers, to compose or decode a register value.
4. Read or write the register through MMIO, indexed register access, RLC-safe access, firmware/SMU-mediated flows, profiling paths, power-management paths, or debug tooling.

For RLC/SPM/perfmon code, higher-level consumers program selectors, sample delays, ring parameters, counter modes, and result triggers around profiling sessions or diagnostics. For RLC power management, consumers sequence safe-mode commands, SMU/RLC handshakes, power-gating masks, clock-gating controls, GPM thread state, and register-save operations during GPU bring-up, runtime power transitions, suspend/resume, and reset. For CGTS, consumers write per-CU override fields to force or observe low-power/busy states for shader/TCP/LDS/SQ/TA/SQC blocks. This file does not encode ordering constraints, polling loops, access permissions, clear-on-read/write-one-to-clear semantics, or side effects.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- RLC SPM mux selections, sample delays, segment thresholds, ring pointers, interrupt enables, perfmon state, and performance counter selections are persistent hardware programming state until reset, power-gating loss, or driver reprogramming. Counter values and ring pointers can change while profiling is active.
- RLC safe-mode, RLCV, and SMU command/response registers are handshake surfaces. Their fields can transition asynchronously as firmware and hardware accept commands.
- RLC timestamps, GPU clock counters, GPM timer status, interrupt status, CP DMA completion bits, firewall violation address, power-gating status, UTCL1 status, and SERDES/SRM busy fields are live observation state. Some may be sticky or clear-sensitive according to hardware semantics outside this header.
- RLC power-gating, CU mask, clock-gating, ramp, delay, load-balance, GPM thread, SRM, and prewalker fields are control state that persists until overwritten, reset, firmware reinitialization, or a power-management transition.
- UTCL1/UTCL2 control fields affect translation behavior for RLC, GPM, SPM, and prewalker traffic. Error fields capture translated request error code, VMID, and address fragments for diagnostics.
- CGTS control registers persist as block-level power/busy/low-power override controls for individual CUs and functional units. Their status-like fields can reflect live hardware state and may differ across shader arrays or harvested CUs.

Reserved fields appear throughout the chunk. Consumers should preserve reserved bits during read-modify-write unless a hardware programming guide explicitly defines a full-register write value.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`, which supplies matching offsets and base-index metadata. This generated shift/mask file must stay synchronized with the GC 9.0 register database and with the offset header.

Likely integration points in AMDGPU include:

- RLC firmware initialization, safe-mode entry/exit, RLCV command paths, SMU command/response flows, and reset recovery code that program `RLC_CNTL`, `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, and related command/response registers.
- GFX power management code that controls RLC power-gating, CU power masks, load balancing, CGCG/CGLS/MGCG, 3D clock-gating controls, and CGTS per-CU overrides.
- Profiling and performance-monitoring code that configures RLC SPM, RLC perfmon counters, RMI counters, ATC L2 counters, and MC VM L2 counters.
- Virtualization or SR-IOV-aware graphics code using `RLC_GPU_IOV_PERF_CNT_*` fields to select virtual functions and counter IDs.
- Register-save/restore and context-management code that uses RLC SERDES, SRM, CSIB, scratch, and general registers.
- GPUVM and RLC translation diagnostics that decode RLC UTCL1/UTCL2 status and translated request error fields.
- Debugfs, register-dump, hang-triage, and hardware validation tools that decode live RLC status, timer, interrupt, power, busy, and CGTS per-CU state.

Because this is generated hardware metadata, concrete behavior lives in consumers through AMDGPU register-access wrappers and in firmware/hardware documentation rather than in this file.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can compile cleanly while programming or decoding the wrong hardware bit.
- This chunk starts and ends mid-definition family. It starts with only the masks for `RLC_SPM_PERFMON_SEGMENT_SIZE`, and it ends inside `CGTS_CU8_LDS_SQ_CTRL_REG`; file-level research must reconcile these boundaries with adjacent chunks.
- Many registers are control or handshake surfaces, not passive data. Misprogramming RLC safe mode, SMU/RLCV commands, SRM commands, power-gating masks, or CGTS overrides can hang graphics, break firmware communication, or corrupt register-save flows.
- Performance counter layouts are repetitive but not identical. RMI counters 0 and 2 have extra selector registers for multiple events, while counters 1 and 3 are simpler; assuming a uniform layout can select the wrong events.
- ATC L2 and MC VM L2 counter result controls have trigger, enable-any, clear-all, and stop-on-saturate bits. Incorrect clear/enable sequencing can produce stale or lost profiling samples.
- Address fragments appear in multiple places: RLC CSIB high addresses are only 16 bits, UTCL1 error MSB fields are narrow, and prewalker address/size fields are split. Consumers must use the documented packing, not generic 64-bit assumptions.
- Some fields are one-bit pulses or sticky status bits, such as capture, reset, force, abort, interrupt, and completion fields. The shift/mask macros do not describe clear or pulse semantics.
- Reserved masks are large in many power-management and CGTS registers. Read-modify-write paths should preserve reserved values to avoid enabling undocumented hardware behavior.
- Per-CU CGTS registers are highly repetitive. Off-by-one register selection or copy/paste mistakes can affect the wrong CU or wrong functional unit, especially with harvested/disabled CUs.
- UTCL1 control fields include bypass, invalidate, drop, snoop, and VMID-dirty controls. Misuse can hide translation faults, force incorrect snooping, or interfere with XNACK retry behavior.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware/runtime diagnostics:

- Build AMDGPU code paths that include `gc_9_0_sh_mask.h` and `gc_9_0_offset.h`; missing, renamed, or malformed macros should surface at compile time.
- Mechanically compare this line range against AMD's authoritative GC 9.0 register database. Each complete field should have a matching shift and mask, and masks should align with the declared shift/width.
- Cross-check every register named in this chunk against `gc_9_0_offset.h` for matching address definitions and base indices.
- Run static consistency checks for repeated families: RLC SPM per-block sample delays, RMI counter selectors, ATC/MC VM L2 counter config registers, GPM timer fields, GPM thread fields, SRM index address/data windows, UTCL1 per-thread error registers, and CGTS per-CU control registers.
- Exercise GPU initialization, RLC firmware load, safe-mode handshakes, suspend/resume, runtime power transitions, and GPU reset on GC 9.0 hardware. Signals include successful RLC/SMU command completion, no stuck RLC busy status, stable clock/power status, and clean reset recovery.
- Validate profiling flows by programming RLC SPM, RLC/RMI counters, ATC L2 counters, and MC VM L2 counters against controlled workloads and checking that counters move, clear, and stop as expected.
- Test SR-IOV or virtualization paths, where available, by selecting VFID/counter IDs through `RLC_GPU_IOV_PERF_CNT_*` and verifying per-VF results.
- Stress power-gating and clock-gating transitions while sampling `RLC_GPM_STAT`, `RLC_CU_STATUS`, `RLC_DYN_PG_STATUS`, `RLC_STATIC_PG_STATUS`, and CGTS override/status fields for expected transitions.
- Inject or reproduce controlled GPUVM/RLC translation faults and verify that UTCL1 error code, VMID, and address fragments decode consistently with firmware or hardware traces.
- Run register-save/restore validation that exercises SERDES/SRM/CSIB fields and checks FIFO busy/empty, abort, and restored-state signals.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002624`. The previous chunk owns the beginning of `RLC_SPM_PERFMON_SEGMENT_SIZE`, including its register marker and shifts. This chunk then covers RLC SPM/perfmon, RMI/ATC/MC VM L2 performance counters, most of a dense RLC management and power block, and the beginning of CGTS per-CU power-control definitions. The next chunk should complete `CGTS_CU8_LDS_SQ_CTRL_REG` and continue the remaining `gc_pwrdec` CGTS register definitions. The final per-file research should merge these artificial chunk boundaries before describing the complete `gc_9_0_sh_mask.h` register map.

### subset-b-002625: lines 24772-27122

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 24772-27122

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains C preprocessor constants only: hardware register fields are represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for composing and decoding 32-bit GPU register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected range begins at the tail of `CGTS_CU8_LDS_SQ_CTRL_REG`, after the corresponding register marker and shift definitions in the previous chunk, then covers the rest of the compute-unit clock/test/status override definitions for CU8 through CU15 and all TCPI controls for CU0 through CU15. It then defines a broad set of GC clock-gating/throttle controls, crosses `gc_ea_pwrdec`, `gc_utcl2_vmsharedhvdec`, and starts `gc_hypdec`. The final line is only the `CP_ME_RAM_WADDR__ME_RAM_WADDR__SHIFT` macro; the matching mask and following CP microcode/RAM fields are in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM graphics-core hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for GC 9.0 graphics-core registers. Driver code pairs these constants with register-address symbols from `gc_9_0_offset.h` and uses AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, and SOC15 register accessors to avoid hard-coded bit positions.

This chunk is mainly concerned with power, clock, virtualization, and CP firmware access surfaces:

- Per-CU `CGTS_*` controls for shader processor, LDS/SQ, texture address/SQC, texture data/TCPF, and TCPI subblocks. These fields expose subblock status bits plus override, busy override, light-sleep override, and SIMD-busy override controls.
- Per-block `CGTT_*` and related `*_CGTT_*` clock-throttling/clock-gating controls for SPI, primitive/geometry front-end blocks, scan converter, shader, shader export, texture/data/address/cache blocks, DB/CB/backend blocks, CP/CPF/CPC/RLC, RMI, TCPF, GCEA, and UTCL2.
- RLC resource-management validity state through `RLC_GFX_RM_CNTL`.
- SR-IOV / virtualization and IOMMU-visible memory window controls in `gc_utcl2_vmsharedhvdec`, including per-VF framebuffer size/offset pairs, MARC base/relocation/length windows, IOMMU enable/performance bits, PCIe ATS enable fields, and UTCL2 clock-gating controls.
- The beginning of CP hypervisor/microcode access definitions for PFP and ME firmware/RAM windows, including PFP ucode address/data and ME ucode/read/write address fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's raw 32-bit mask.
- Matching register addresses are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`.
- Consumers normally use these macros through AMDGPU register helpers rather than directly shifting by hand.

Notable macro groups in this range include:

- `CGTS_CU8_LDS_SQ_CTRL_REG` tail plus `CGTS_CU8_*` through `CGTS_CU15_*`: per-compute-unit CGTS controls for `SP00`, `SP01`, `LDS`, `SQ`, `TA`, `SQC`, `SP10`, `SP11`, `TD`, and `TCPF`. Repeated fields include 7-bit state slices and override bits at low and high halfword positions.
- `CGTS_CU0_TCPI_CTRL_REG` through `CGTS_CU15_TCPI_CTRL_REG`: per-CU TCPI state and override fields, with the same `TCPI`, `TCPI_OVERRIDE`, `TCPI_BUSY_OVERRIDE`, `TCPI_LS_OVERRIDE`, and `TCPI_SIMDBUSY_OVERRIDE` layout.
- `CGTT_SPI_CLK_CTRL`, `CGTT_PC_CLK_CTRL`, `CGTT_BCI_CLK_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_IA_CLK_CTRL`, `CGTT_WD_CLK_CTRL`, `CGTT_PA_CLK_CTRL`, `CGTT_SC_CLK_CTRL0/1`, `CGTT_SQ_CLK_CTRL`, and `CGTT_SQG_CLK_CTRL`: graphics front-end and shader clock-gating controls with on-delay/off-hysteresis, debug/perf enables, group/core overrides, register overrides, and soft-stall override bits.
- `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, `SQ_LDS_CLK_CTRL`, `SQ_POWER_THROTTLE`, and `SQ_POWER_THROTTLE2`: shader subblock clock and power throttle fields.
- `CGTT_SX_CLK_CTRL0` through `CGTT_SX_CLK_CTRL4`: shader-export clock-gating controls for export/position/index banks, blend queues, request paths, and related subblock overrides.
- `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `CGTT_TCPI_CLK_CTRL`, `CGTT_TCI_CLK_CTRL`, `CGTT_GDS_CLK_CTRL`, `DB_CGTT_CLK_CTRL_0`, `CB_CGTT_SCLK_CTRL`, `TCC_CGTT_SCLK_CTRL`, `TCA_CGTT_SCLK_CTRL`, `RMI_CGTT_SCLK_CTRL`, and `CGTT_TCPF_CLK_CTRL`: texture, global data share, depth/color backend, cache, memory-interface, and texture-cache frontend clock controls.
- `CGTT_CP_CLK_CTRL`, `CGTT_CPF_CLK_CTRL`, `CGTT_CPC_CLK_CTRL`, and `CGTT_RLC_CLK_CTRL`: command processor, command processor front-end, compute processor, and RLC clock gating/soft-stall overrides.
- `GCEA_CGTT_CLK_CTRL`: graphics/EA power-decoder clock-gating control with return/register override fields.
- `MC_VM_FB_SIZE_OFFSET_VF0` through `MC_VM_FB_SIZE_OFFSET_VF15`: per-virtual-function framebuffer size and offset fields, each split into 16-bit `VF_FB_SIZE` and `VF_FB_OFFSET`.
- `VM_IOMMU_MMIO_CNTRL_1`, `MC_VM_MARC_BASE_*`, `MC_VM_MARC_RELOC_*`, `MC_VM_MARC_LEN_*`, `VM_IOMMU_CONTROL_REGISTER`, `VM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`, and `VM_PCIE_ATS_CNTL*`: IOMMU/MARC/ATS controls for memory aperture remapping and PCIe address translation services. Low MARC address/length fields use bit-12 alignment, high fields use 20-bit masks, and relocation low fields also include enable/read-only bits.
- `UTCL2_CGTT_CLK_CTRL`: UTCL2 clock-gating delay, soft override, MGLS override, and soft-stall override fields.
- `CP_HYP_PFP_UCODE_ADDR`, `CP_PFP_UCODE_ADDR`, `CP_HYP_PFP_UCODE_DATA`, `CP_PFP_UCODE_DATA`, `CP_HYP_ME_UCODE_ADDR`, `CP_ME_RAM_RADDR`, and the partial `CP_ME_RAM_WADDR`: CP microcode and ME RAM address/data window fields. In `gfx_v9_0.c`, the ME firmware loading path writes `mmCP_ME_RAM_WADDR`, streams data through `mmCP_ME_RAM_DATA`, then writes the ME firmware version back to `mmCP_ME_RAM_WADDR`.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Detect/select a GC 9.0 ASIC path and include the matching generated register headers.
2. Choose a register address from `gc_9_0_offset.h`.
3. Compose or decode a register value with these shift/mask definitions, commonly through `REG_SET_FIELD` or `REG_GET_FIELD`.
4. Access the register through MMIO, RLC-safe accessors, SOC15 helpers, firmware loading paths, SR-IOV virtualization setup, power-management code, or diagnostic register dumps.

For CGTS and CGTT families, initialization, golden-register, power-management, debug, and recovery code can read status or program clock-gating/override policy. This header does not encode the hardware sequencing needed to safely change clock-gating bits, clear stalls, or sample transient busy state.

For VM/IOMMU/MARC/ATS registers, virtualization and memory-management code configures per-VF apertures, remap windows, IOMMU enablement, performance optimizations, and PCIe ATS behavior. The header only defines bit positions; it does not validate VF ownership, aperture bounds, PCIe/IOMMU capability state, or ordering relative to TLB/cache invalidations.

For CP hypervisor and microcode windows, firmware-loading code writes address selectors and then streams data through paired data registers. Indexed RAM/ucode windows require strict sequencing and size bounds in the consumer. The partial `CP_ME_RAM_WADDR` definition at the chunk end must be merged with the following chunk before describing the complete CP RAM window family.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware register fields whose values live in the GPU until reset, power-gating loss, firmware reinitialization, driver reprogramming, or virtualization teardown.

CGTS fields can expose or force per-CU subblock state for SP, LDS, SQ, TA, SQC, TD, TCPF, and TCPI. Status-style bits may change while waves and memory operations run; override bits persist until cleared or reset and can intentionally hold blocks out of normal clock/light-sleep behavior.

CGTT fields persist as graphics-core clock-gating and throttle policy. `ON_DELAY` and `OFF_HYSTERESIS` tune gating latency; `SOFT_STALL_OVERRIDE*`, `SOFT_OVERRIDE*`, `REG_OVERRIDE`, `CORE*_OVERRIDE`, `MGLS_OVERRIDE`, debug/perf enables, and all-clock-on fields can materially change power, performance, and hang behavior. Some fields are reserved or spare and should be preserved during read-modify-write unless a hardware sequence explicitly defines them.

The VM/IOMMU/MARC/ATS fields persist as virtualization and address-translation state. Per-VF framebuffer offset/size fields define guest-visible framebuffer apertures. MARC base, relocation, enable, read-only, and length fields define remap windows. ATS and IOMMU bits control whether transactions can use address translation services. Misconfigured values can survive long enough to affect multiple queues, VFs, or DMA streams until reset or reconfiguration.

CP PFP/ME ucode address/data and ME RAM address fields are persistent selector/data windows during firmware upload and inspection. Their contents and selected indices interact with CP firmware state; address selector writes are not just passive values when paired with following data writes.

## Dependencies And Integration Points

The primary dependency is the matching generated offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`, which defines addresses such as `mmCGTS_CU8_TA_SQC_CTRL_REG`, `mmCGTT_SPI_CLK_CTRL`, `mmMC_VM_FB_SIZE_OFFSET_VF*`, `mmMC_VM_MARC_*`, `mmVM_PCIE_ATS_CNTL*`, `mmCP_HYP_PFP_UCODE_ADDR`, and `mmCP_ME_RAM_WADDR`.

AMDGPU integration points include:

- GFX 9.0 initialization, golden-register programming, suspend/resume, GPU reset, and gfxoff/power-management code that needs GC clock-gating and soft-stall override definitions.
- Hang triage and register-dump code that decodes CGTS per-CU status or broad CGTT clock-gating state to determine whether shader, texture, backend, RLC, CP, or memory-interface blocks are stuck or forced on.
- RLC and command processor bring-up paths using `CGTT_RLC_CLK_CTRL`, `RLC_GFX_RM_CNTL`, and CP/CPF/CPC clock controls.
- CP firmware loading and inspection paths. `gfx_v9_0.c` directly writes `mmCP_ME_RAM_WADDR` during ME firmware upload; adjacent CP PFP/ME ucode fields in this chunk describe the indexed windows around that flow.
- SR-IOV and virtualization setup that configures per-VF framebuffer windows, MARC remapping, IOMMU enablement, and ATS enablement.
- GPUVM, IOMMU, PCIe ATS, and UTCL2-related code paths where translation policy and clock-gating behavior affect memory access correctness and performance.
- Common register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, and RLC-shadowed or indexed register accessors.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but can program a different hardware bit, corrupt diagnostics, or change power/virtualization policy.
- This chunk starts and ends mid-register context. It begins with only three masks for `CGTS_CU8_LDS_SQ_CTRL_REG`, and it ends after only `CP_ME_RAM_WADDR__ME_RAM_WADDR__SHIFT`. Adjacent chunks are required for full register-family context.
- CGTS and CGTT families are highly repetitive. Copy/paste or generator errors can swap CU numbers, subblocks, group numbers, or override bits while still looking structurally plausible.
- Clock-gating and soft-stall overrides can hide idle/hang symptoms or create new hangs if set while a block is active. Full-register writes risk changing reserved/spare bits, debug enables, or performance overrides.
- `ON_DELAY` and `OFF_HYSTERESIS` fields are small delay controls, not arbitrary counters. Incorrect values can cause power regressions, clock chatter, or delayed wake behavior that only appears under workload stress.
- Per-VF framebuffer size/offset fields and MARC relocation windows are security-sensitive in SR-IOV contexts. Off-by-one VF indexing, wrong size units, or mispacked high/low address fields can expose memory across guests or block valid guest access.
- MARC low fields are aligned at bit 12 while high fields are only 20 bits. Ad hoc address packing can silently drop low address bits or overflow the intended aperture.
- `MARC_ENABLE` and `MARC_READONLY` bits share relocation-low registers with address bits; consumers must not overwrite control bits when updating relocation addresses.
- ATS/IOMMU enable bits depend on platform and PCIe/IOMMU capability state. Enabling ATC at the wrong time can cause translation faults or stale translations if invalidation sequencing is missing.
- CP microcode and ME RAM address/data windows require ordered indexed writes. A bad address mask or missing bounds check in a consumer can load firmware at the wrong RAM location or overwrite version/address selector state.

## Test Signals

Useful validation combines generated-data checks, build coverage, and hardware/runtime behavior:

- Build AMDGPU code paths that include `gc_9_0_sh_mask.h` and `gc_9_0_offset.h`; missing, renamed, or malformed macros should surface at compile time.
- Mechanically compare this line range against AMD's authoritative GC 9.0 register database. Complete fields should have matching `__SHIFT` and `_MASK` entries, masks should align with shifts, and repeated CU/VF families should remain structurally consistent.
- Cross-check every register family in this chunk against `gc_9_0_offset.h` for matching address symbols and base-index entries.
- Static sanity checks should verify repeated `CGTS_CU8` through `CGTS_CU15` layouts, `CGTS_CU0_TCPI` through `CGTS_CU15_TCPI`, per-block `CGTT_*` override bit positions, per-VF framebuffer size/offset pairs, four MARC base/reloc/length windows, and sixteen ATS VF enable registers.
- Runtime bring-up tests on GC 9.0 hardware should cover graphics initialization, golden-register programming, gfxoff/power transitions, suspend/resume, and GPU reset without stuck busy bits or unexpected clock-gating overrides.
- Power/performance tests should compare clock-gating behavior, wake latency, and idle power before and after any generated-register update that touches CGTT/CGTS fields.
- SR-IOV tests should validate VF framebuffer aperture isolation, MARC remapping, read-only behavior, ATS enablement, and guest memory access under reset and migration-like teardown/reinit paths.
- GPUVM/IOMMU stress tests should watch for translation faults, stale ATS entries, bad aperture boundaries, or UTCL2 clock-gating side effects.
- CP firmware-loading tests should verify PFP/ME firmware upload succeeds, CP rings start, firmware version writes/readbacks are sane, and no ME RAM window bounds or address-selector regressions occur.
- Hang/debug register-dump tests should decode CGTS/CGTT state during known workloads and compare against expected busy/idle/override states.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002625`. The previous chunk owns the beginning of `CGTS_CU8_LDS_SQ_CTRL_REG`, while this chunk starts at its final masks. The next chunk must complete `CP_ME_RAM_WADDR`, then continue the CP hypervisor/microcode address/data definitions. The final per-file research should merge these boundaries before presenting a whole-file view of `gc_9_0_sh_mask.h`.

### subset-b-002626: lines 27123-29720

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 27123-29720

## Scope

This chunk covers a generated AMD GC 9.0 shift/mask header segment. It contains preprocessor constants only: bit `__SHIFT` values and `_MASK` values used by AMDGPU, AMDKFD, and power-management code to compose and decode 32-bit graphics-core register values.

The requested range contains 2,145 `#define` entries: 1,074 shift macros and 1,071 mask macros. The count is intentionally unbalanced because the chunk starts at the mask for `CP_ME_RAM_WADDR__ME_RAM_WADDR` while its shift is on the previous line, and it ends inside `DIDT_TCP_EDC_STALL_DELAY_4`, before the corresponding masks for TCP12-TCP15.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU DRM graphics metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_9_0_sh_mask.h` supplies bitfield layouts for GC 9.0 graphics-core registers. This chunk covers several independent hardware namespaces:

- CP and RLC microcode access fields for ME, CE, MEC1, MEC2, and RLC GPM RAM/register windows.
- GRBM graphics-index, graphics-control, and CAM remapping selectors used to target shader engines, shader arrays, instances, pipes, MEs, VMIDs, and queues.
- RLC GPU IOV, RLCV timer, hypervisor semaphore, clock-control, scratch, firmware, function, interrupt, doorbell, virtual reset, SDMA status, and busy-status fields used by SR-IOV/PF-VF scheduling and virtualization flows.
- `gccacind` and `secacind` indirect CAC registers for graphics-core and shader-engine power/activity counters, weights, override selection/value fields, and accumulator readback across BCI, CB, CBR, CP, DB, DBR, GDS, IA, LDS, PA, PC, SC, SPI, SQ, SX, SXRB, TA, TCC, TCP, TD, VGT, WD, CU, EA, RMI, UTCL2/ATCL2, UTCL2 router, VML2, and walker blocks.
- `sqind` indirect shader queue debug and wave-state fields for wave mode/status/trap status, hardware IDs, GPR/LDS allocation, instruction buffer status/debug, program counter, instruction words, temporary trap registers, execution masks, and SQ interrupt-word encodings.
- `didtind` dynamic inductive/droop throttling fields for SQ, DB, TD, and TCP blocks, including control, thresholds, power windows, stall delays, stall patterns, weights, EDC control, EDC thresholds, EDC status, EDC stall patterns, and EDC per-lane delay registers.

Driver code pairs these macros with register offsets from `gc_9_0_offset.h` and uses helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15 MMIO helpers, indirect-register helpers, CGS power-management accessors, and KFD MQD setup code to program or inspect hardware without hard-coding bit positions.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for isolating or preserving that field.
- Register comments such as `//RLC_GPU_IOV_CFG_REG1` and address-block comments such as `// addressBlock: didtind` preserve grouping from the hardware register database.
- Consumers normally pair these field definitions with `reg*`, `mm*`, or `ix*` offsets from the matching generated offset header.

Important field families in this chunk include:

- Microcode windows: `CP_HYP_ME_UCODE_DATA`, `CP_ME_RAM_DATA`, `CP_CE_UCODE_ADDR/DATA`, `CP_HYP_CE_UCODE_ADDR/DATA`, `CP_HYP_MEC1/2_UCODE_*`, `CP_MEC_ME1/2_UCODE_*`, `RLC_GPM_UCODE_ADDR`, and `RLC_GPM_UCODE_DATA`.
- GRBM selector fields: `GRBM_GFX_INDEX_SR_DATA` fields for instance/SH/SE indices and broadcast writes; `GRBM_GFX_CNTL_SR_DATA` fields for pipe, ME, VMID, and queue; and `GRBM_CAM_DATA`/`GRBM_HYP_CAM_DATA` address/remap fields.
- RLC IOV fields: VF enable/count, context size/location/offset, VM busy status, doorbell status/set/clear/mask, scheduler block identity/version/size, command type/execute/interrupt/function ID/next function ID, command status, active functions, active PF/VF identity, RLC IOV microcode and scratch access, F32 enable/reset, SDMA0/SDMA1 preempted/saved/restored status, SMU/RLC responses, virtual reset request bits, interrupt disable/force, and SDMA VM busy masks.
- CAC fields: global and SE `CAC_ENABLE`, thresholds, block/signal IDs, override select/value registers, per-block 16-bit signal weights, 32-bit accumulators, and override selectors/values with block-dependent widths.
- SQ wave debug fields: mode bits for FP rounding/denorms, DX10 clamp, IEEE, debug and exception enable, perf disable, GPR index, VSKIP, CSP; status bits for SCC, priorities, privilege, traps, export readiness, EXECZ/VCCZ, barriers, halt, valid, ECC, replay, and fatal halt; trap status, hardware attribution, allocation sizes, instruction buffer counters/debug states, PC and instruction words, TTMP0-TTMP15, M0, EXEC masks, and interrupt word encodings.
- DIDT/EDC fields: `DIDT_*_CTRL0/1/2/3`, stall/tuning/auto-release controls, stall pattern registers, weight registers, `DIDT_*_EDC_CTRL`, EDC thresholds, EDC stall patterns, EDC status, EDC delay registers, overflow counters, and rolling power delta fields for SQ, DB, TD, and TCP. The DB family has only `DIDT_DB_EDC_STALL_DELAY_1` in this chunk, while SQ, TD, and TCP expose delay groups for up to 16 lanes or instances.

## Control Flow

This header has no local runtime control flow. Its direct behavior is compile-time macro substitution.

The implied driver flow is:

1. GC 9.0 AMDGPU, AMDKFD, or power-management code includes `gc_9_0_offset.h` and `gc_9_0_sh_mask.h`.
2. Code selects a register offset, sometimes through direct SOC15 MMIO and sometimes through indirect index/data windows such as GC CAC, SE CAC, SQ, or DIDT.
3. Code composes or decodes field values using these shift/mask constants through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_DIDT`, `WREG32_DIDT`, `cgs_read_ind_register`, and `cgs_write_ind_register`.
4. Runtime paths use the resulting values to load firmware, select GRBM targets, manage SR-IOV and RLC virtualization state, inspect wave/debug state, configure power/throttling tables, collect counters, or handle reset and preemption state.

Concrete include users in this tree include `amdgpu/gfx_v9_0.c`, `amdgpu/soc15.c`, `amdgpu/mxgpu_ai.c`, `amdgpu/gfxhub_v1_0.c`, `amdgpu/gmc_v9_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v9.c`, `amdgpu/amdgpu_amdkfd_arcturus.c`, `amdkfd/kfd_mqd_manager_v9.c`, and `pm/powerplay/hwmgr/vega10_inc.h`. Power-management files such as `vega10_powertune.c`, `smu7_powertune.c`, and `kv_dpm.c` use the DIDT and CAC field macros to build tuning tables and toggle droop/throttling controls.

The generated header does not encode ordering requirements, side-effect semantics, access permissions, polling timeouts, firmware ownership, read-only/write-only status, clear-on-read behavior, write-one-to-clear behavior, or reset sequencing. Those rules come from hardware documentation and the consuming AMDGPU/AMDKFD/PM code.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state in GC 9.0 registers:

- CP and RLC microcode address/data windows affect firmware upload or firmware-visible RAM/register windows. Values are transient during load and debug flows, but wrong field packing can corrupt the loaded microcode stream or address window.
- GRBM selectors route later indexed or broadcast operations to specific shader engines, shader arrays, instances, pipes, MEs, VMIDs, and queues. Their values are control state that can affect subsequent register accesses until changed.
- RLC GPU IOV fields describe persistent virtualization scheduler state, active PF/VF identity, context allocation, VF doorbell masks/status, interrupt routing, virtual function reset requests, and SDMA save/restore/preempt progress. These values matter across SR-IOV scheduling, reset, and preemption windows.
- CAC weight, override, and accumulator fields represent power/activity modeling state. Weight and override values are programmed policy; accumulators are live counters or sampled state that power-management code may read, clear, or use for telemetry.
- SQ wave debug fields expose live shader execution context: current wave mode/status, trap state, attribution, register allocation, instruction buffer state, PC/instruction data, TTMP registers, EXEC masks, and interrupt payload fields. They are diagnostic hardware state, not driver-owned persistent storage.
- DIDT control and EDC fields configure throttling and power response for SQ, DB, TD, and TCP blocks. Thresholds, intervals, stall patterns, weights, forced-stall controls, EDC enables/resets, and per-unit stall delays are persistent hardware policy until reset or reprogramming.
- Overflow, rolling power delta, EDC status, busy status, response, and interrupt status fields are live telemetry or latched hardware state. This header cannot identify which fields require special access sequences to clear or sample correctly.

Because this is a generated shift/mask file, it cannot show whether a register is privileged, shadowed, per-instance, per-SE, PF-only, VF-visible, saved by firmware, restored by reset code, or safe for read-modify-write. Consumers must preserve reserved fields unless the programming guide or local driver code says otherwise.

## Dependencies And Integration Points

This chunk depends on synchronization with AMD's GC 9.0 register database and companion generated files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` for matching MMIO and indirect register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_default.h` for generated defaults where applicable.
- AMDGPU register helper infrastructure, including SOC15 accessors, indirect CAC/SQ/DIDT accessors, `REG_SET_FIELD`, `REG_GET_FIELD`, and CGS power-management register wrappers.

Primary integration points are:

- `amdgpu/gfx_v9_0.c`, which programs GC 9.0 graphics, CP/RLC, GRBM, wave debug, reset, and firmware-facing state.
- `amdgpu/mxgpu_ai.c` and other SR-IOV paths, which rely on RLC GPU IOV masks for PF/VF scheduling, virtual reset, doorbells, and function attribution.
- `amdkfd/kfd_mqd_manager_v9.c` and `amdgpu/amdgpu_amdkfd_gfx_v9.c`, which include the GC 9.0 register namespace for KFD queue integration.
- `amdgpu/gfxhub_v1_0.c`, `amdgpu/gmc_v9_0.c`, and `amdgpu/soc15.c`, which include GC 9.0 field definitions for memory hub, SOC initialization, reset, and register access support.
- `pm/powerplay/hwmgr/vega10_powertune.c`, `pm/powerplay/hwmgr/smu7_powertune.c`, and `pm/legacy-dpm/kv_dpm.c`, which consume DIDT and CAC fields to build power-tuning tables, enable/disable DIDT blocks, and configure EDC behavior.
- Hardware diagnostics, profiling, debugfs, RAS, SR-IOV, and reset paths that decode SQ debug, wave, interrupt, CAC, DIDT, RLC, and GRBM state.

## Risks And Edge Cases

- Generated-data drift is the main risk. A wrong shift or mask can compile cleanly while writing the wrong hardware bits.
- The chunk starts and ends inside register definitions. `CP_ME_RAM_WADDR` is missing its shift in this chunk, and `DIDT_TCP_EDC_STALL_DELAY_4` is missing all four masks. Adjacent chunks are required before making whole-register completeness claims.
- The RLC GPU IOV fields are virtualization-sensitive. Incorrect VF enable, VF number, PF/VF identity, doorbell mask/status, active-function, command, interrupt, or virtual-reset masks can misroute work, break isolation, or make PF/VF reset handling unreliable.
- GRBM index and broadcast fields are high-risk because they route later writes. An incorrect index or broadcast bit can program the wrong shader engine, shader array, instance, pipe, ME, VMID, or queue.
- CP/RLC/MEC microcode address/data fields are firmware-critical. Address mask errors can truncate firmware upload addresses or write data to an unintended window.
- CAC and DIDT tables are repetitive and policy-sensitive. Copy/paste or generator errors can affect only a specific block such as TCP, TD, DB, SQ, UTCL2 router, or CU, which may appear as workload-dependent throttling, power, or telemetry anomalies rather than immediate boot failures.
- SQ debug and wave-state fields expose live execution context. Mis-decoding these fields can mislead hang analysis, wave dumps, shader debugging, trace decoding, or exception attribution.
- Some status, accumulator, interrupt, overflow, and response fields may be latched or have side effects on access. This header cannot distinguish ordinary status bits from clear-on-read, write-one-to-clear, or sample-triggered registers.
- Reserved and unused masks are explicit throughout the chunk. Read-modify-write code must preserve them unless the hardware programming guide specifies a safe value.
- Field names include generated spelling and casing quirks such as `Sch_Block_ID`, `Time_Quanta_Def`, `OVRRD_SELECT`, and compact SQ interrupt masks. Consumers must match the generated identifiers exactly.

## Test Signals

Useful validation should combine static generated-data checks, build coverage, and hardware/runtime testing:

- Build AMDGPU, AMDKFD, and power-management code with GC 9.0 support. Missing or renamed macros should surface in `gfx_v9_0.c`, KFD MQD/queue code, SR-IOV code, and powertune tables.
- Mechanically diff this range against AMD's authoritative GC 9.0 register database and verify both shift values and masks.
- Verify shift/mask pairing for complete registers in the chunk, allowing the known boundary exceptions for `CP_ME_RAM_WADDR` and `DIDT_TCP_EDC_STALL_DELAY_4`.
- Cross-check repeated CAC weight/accumulator/override groups and DIDT SQ/DB/TD/TCP families for consistent field widths, unused ranges, and expected per-block differences.
- Exercise GC 9.0 firmware load and reset paths. Relevant signals include successful CP/RLC/MEC initialization, no firmware load failures, and clean ring bring-up after reset.
- Run SR-IOV/PF-VF tests where hardware and firmware support are available. Watch VF enable/count, active function ID, doorbell status/masks, virtual reset requests, SDMA preempt/save/restore status, and busy-status attribution.
- Run graphics and compute workloads while exercising GRBM-targeted register paths. Failures may present as wrong per-SE/per-SH state, hangs, or inconsistent debug dumps.
- Run power-management tests around Vega10/GC9 DIDT and EDC enable/disable, including suspend/resume, clock changes, and throttling events. Expected signals are stable clocks, plausible power telemetry, no forced-stall leakage, and no performance collapse under normal loads.
- Validate CAC accumulators and weights with power-tuning table programming. Check for plausible activity counter movement across SQ, TCP, TD, TCC, CU, UTCL2, and related blocks.
- Exercise shader debugging, wave dumps, trap/exception handling, and thread trace. Check SQ wave status, trap status, hardware ID attribution, PC/instruction values, TTMP data, EXEC masks, and SQ interrupt word decoding.
- Run GPU reset, hang recovery, and preemption scenarios. RLC, GRBM, SQ, and DIDT state should return to expected defaults or driver-programmed values after recovery.

## Cross-Chunk Notes

The previous chunk owns the beginning of the CP/RLC microcode field area, including `CP_ME_RAM_WADDR__ME_RAM_WADDR__SHIFT`. This chunk continues CP/RLC/GRBM definitions, fully covers the RLC GPU IOV block and the GC/SE CAC and SQ debug blocks in this range, then covers DIDT SQ, DB, TD, and most of TCP EDC delay definitions. The next chunk must complete `DIDT_TCP_EDC_STALL_DELAY_4` masks and continue with subsequent DIDT DBR fields.

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002626_research.md`; whole-file research for `gc_9_0_sh_mask.h` should be produced later by merging all chunk documents for the source file.

### subset-b-002627: lines 29721-30033

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 29721-30033

## Scope

This chunk is the final segment of the generated AMD GC 9.0 shift/mask register header. It contains C preprocessor constants only: hardware register fields are represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for composing and decoding 32-bit GPU register values. There are no functions, structs, enums, variables, allocations, locks, branches, or callbacks in this range.

The selected range begins at the tail of `DIDT_TCP_EDC_STALL_DELAY_4`, after the corresponding shift definitions from the previous chunk, then covers the complete DBR DIDT/EDC control families, DIDT stall event counters, and the final texture/cache EDC counter registers (`TA_EDC_CNT`, `TCI_EDC_CNT`, `TCP_EDC_CNT_NEW`, and `TD_EDC_CNT`). It ends with the file's `#endif`.

Although the repository is under a `ceph-client` mirror, this file is AMDGPU DRM graphics-core hardware metadata and is unrelated to Ceph distributed filesystem behavior.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for GC 9.0 graphics hardware. Driver code pairs these macros with register addresses from the matching GC 9.0 offset header and uses AMDGPU field helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, indexed-register helpers, and MMIO accessors to pack or extract field values without hard-coding bit positions.

This chunk describes two related hardware surfaces:

- DIDT and EDC control for the DBR block and the tail of TCP EDC state. DIDT is dynamic power/throttle logic; EDC tracks error/power-delta/throttle state and can force or qualify stalls through programmable patterns and delays.
- End-of-file EDC counter decoding for TA, TCI, TCP, and TD memories/FIFOs. These fields are consumed by AMDGPU RAS/EDC reporting tables to name and extract correctable, detectable, and double-error counters from GC register dumps.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the raw mask for that field inside the 32-bit register.
- Register address symbols live in the matching GC 9.0 offset header, for example `ixDIDT_DBR_EDC_CTRL` for DIDT indirect registers and `mmTA_EDC_CNT`/`mmTCP_EDC_CNT_NEW` for SOC15 GC registers.

Important macro groups in this range include:

- `DIDT_TCP_EDC_STALL_DELAY_4` masks for `EDC_STALL_DELAY_TCP12` through `EDC_STALL_DELAY_TCP15`, plus `DIDT_TCP_EDC_OVERFLOW` and `DIDT_TCP_EDC_ROLLING_POWER_DELTA`. These are the tail of the TCP EDC family and expose per-TCP stall delay bytes, rolling power-delta overflow state, throttle-level overflow count, and the full 32-bit rolling power-delta value.
- `DIDT_DBR_CTRL0`, `DIDT_DBR_CTRL1`, `DIDT_DBR_CTRL2`, `DIDT_DBR_STALL_CTRL`, `DIDT_DBR_TUNING_CTRL`, `DIDT_DBR_STALL_AUTO_RELEASE_CTRL`, and `DIDT_DBR_CTRL3`. These define DBR DIDT enable/reset/clock override fields, phase offset, stall and tuning enables, high/min/max power thresholds, interval sizing, long-term ratio, stall delays, max stall counts, throttle policy, level-combine enables, stall qualification, force-stall, and stall-delay enable bits.
- `DIDT_DBR_STALL_PATTERN_1_2` through `DIDT_DBR_STALL_PATTERN_7`. These pack seven 15-bit stall patterns across four registers, with reserved upper bits where only one pattern is present.
- `DIDT_DBR_WEIGHT0_3`, `DIDT_DBR_WEIGHT4_7`, and `DIDT_DBR_WEIGHT8_11`. These expose twelve 8-bit weights used by DBR DIDT power/throttle calculations.
- `DIDT_DBR_EDC_CTRL`, `DIDT_DBR_EDC_THRESHOLD`, `DIDT_DBR_EDC_STALL_PATTERN_1_2` through `DIDT_DBR_EDC_STALL_PATTERN_7`, `DIDT_DBR_EDC_STATUS`, `DIDT_DBR_EDC_STALL_DELAY_1`, `DIDT_DBR_EDC_OVERFLOW`, and `DIDT_DBR_EDC_ROLLING_POWER_DELTA`. These mirror the EDC control/status surface for DBR: enable/reset/clock override/force-stall, trigger throttle low bit, stall pattern size, write-power-delta permission, GC and shader-engine level combine, stall policy, 32-bit threshold, seven 15-bit stall patterns, FSM state, throttle level, two 3-bit DBR stall delays, overflow state, overflow counter, and rolling power delta.
- `DIDT_SQ_STALL_EVENT_COUNTER`, `DIDT_DB_STALL_EVENT_COUNTER`, `DIDT_TD_STALL_EVENT_COUNTER`, `DIDT_TCP_STALL_EVENT_COUNTER`, and `DIDT_DBR_STALL_EVENT_COUNTER`. Each is a full-width 32-bit stall-event counter for one DIDT-controlled graphics block.
- `TA_EDC_CNT`. This register defines 2-bit counters for TA front-end FIFO and RAM events: `TA_FS_DFIFO_SEC_COUNT`, `TA_FS_DFIFO_DED_COUNT`, `TA_FS_AFIFO_SED_COUNT`, `TA_FL_LFIFO_SED_COUNT`, `TA_FX_LFIFO_SED_COUNT`, and `TA_FS_CFIFO_SED_COUNT`.
- `TCI_EDC_CNT`. In this GC 9.0 header it exposes only `WRITE_RAM_SED_COUNT` as a 2-bit field.
- `TCP_EDC_CNT_NEW`. This decodes 2-bit counters for TCP cache RAM, LFIFO RAM, command FIFO, VM FIFO, DB RAM, and UTCL1 LFIFO0/LFIFO1 events. Cache/LFIFO/VM/UTCL1 fields have paired SEC/DED counters where present; command FIFO and DB RAM are single SED counters in this header.
- `TD_EDC_CNT`. This defines 2-bit counters for TD shader-stream FIFO low/high SEC/DED events and a CS FIFO SED event.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in consumers is:

1. Select the GC 9.0 register offset and shift/mask headers for the active ASIC.
2. Pick a register address, either from DIDT indirect-register names such as `ixDIDT_DBR_EDC_CTRL` or SOC15 GC names such as `mmTCP_EDC_CNT_NEW`.
3. Read the current value or prepare a full-register programmed value.
4. Use these shift/mask macros through helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, or `SOC15_REG_FIELD`.
5. Write control registers, decode status/counter registers, or build RAS/diagnostic tables.

Concrete consumers found in this tree include `vega10_powertune.c`, where `vega10_didt_set_mask()` toggles DBR DIDT and DBR EDC fields through `CGS_WREG32_FIELD_IND`, `cgs_read_ind_register()`, `REG_SET_FIELD()`, and `cgs_write_ind_register()`. The same file programs TCP EDC stall pattern, delay, and threshold register lists that border this chunk. `gfx_v9_0.c` consumes the TA/TCI/TCP/TD counter masks through `SOC15_REG_FIELD()` inside EDC/RAS counter tables and uses matching `SOC15_REG_ENTRY()` entries to enumerate the registers for reads.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware state owned by the GPU, firmware, and driver:

- DBR DIDT control fields persist in the DIDT indirect register space until reset, power-gating loss, firmware reinitialization, or explicit driver reprogramming. Enable, reset, clock override, stall control, tuning, auto-release, threshold, interval, and policy fields directly affect hardware throttle behavior.
- DBR/TCP EDC status, overflow, rolling power delta, and stall-event counters are live hardware observation points. Some values can change asynchronously while graphics workloads run.
- Stall pattern, weight, delay, and threshold registers are programmable policy state. Drivers can write whole-register values during power-management setup, but later read-modify-write paths should preserve reserved fields unless the hardware programming sequence specifies otherwise.
- TA/TCI/TCP/TD EDC count registers are hardware-maintained error counters. The masks only decode packed 2-bit fields; counter lifetime, clearing semantics, overflow behavior, and RAS aggregation policy live in hardware and higher-level AMDGPU code.
- The chunk ends at `#endif`, closing the include guard for the whole generated header.

## Dependencies And Integration Points

This chunk depends on generated GC 9.0 register metadata remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` supplies the matching register addresses and base-index information.
- AMDGPU field helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, and SOC15 register-entry helpers consume the shift/mask names.
- DIDT indirect register access uses CGS helpers and the `CGS_IND_REG__DIDT` space in power-management code.
- RAS/EDC reporting in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c` uses the TA, TCI, TCP, and TD counter fields to attach names and SEC/DED/SED field masks to hardware counters.
- Vega10 power-management code in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.c` uses this DIDT family when platform capabilities such as DBR ramping and DIDT EDC are enabled.
- Nearby GC 9.x headers are similar but not interchangeable. For example, later GC 9.4 variants add or rename several EDC counter fields, so consumers must include the header that matches the detected IP version.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can compile cleanly while enabling the wrong throttle bit, clearing the wrong reset bit, or decoding the wrong error counter.
- The chunk starts mid-register family. `DIDT_TCP_EDC_STALL_DELAY_4` shift definitions are in the previous chunk, while this chunk begins with only the four masks. Final file-level research must merge that boundary.
- DIDT/EDC control fields are side-effect sensitive. Enable/reset, force-stall, clock override, auto-release, throttle policy, and stall-delay fields can alter live GPU power and scheduling behavior.
- Several DBR control registers contain reserved or `UNUSED_*` fields. Full-register writes must be limited to documented programming tables or preserve reserved bits during read-modify-write.
- Pattern fields are 15 bits, not 16 bits, even though they are paired in 16-bit lanes with one reserved bit. Treating them as two full 16-bit values would set reserved bits.
- EDC stall delays differ by block. TCP delay fields in the tail of the previous family are 8-bit lanes, while DBR EDC delay fields in this chunk are two 3-bit fields plus reserved bits.
- Overflow and event counters can be live, sticky, saturating, or clear-sensitive depending on hardware semantics not encoded in this header. Sampling order matters for diagnostics.
- GC 9.0 EDC counter naming differs from later GC 9.4 headers. For example, this chunk has `TA_FS_AFIFO_SED_COUNT` and `TCI_WRITE_RAM_SED_COUNT`, while newer headers split some events into SEC/DED pairs. Blindly sharing decode tables across IP versions can misreport RAS events.
- The final `#endif` means accidental edits around this chunk can break the include guard for every GC 9.0 consumer, not just DIDT or RAS code.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware/runtime behavior:

- Build AMDGPU code paths that include `gc_9_0_sh_mask.h`, especially `gfx_v9_0.c`, `gmc_v9_0.c`, `soc15.c`, AMDKFD GFX v9 files, and Vega10 power-management files. Missing or renamed field macros should fail at compile time.
- Mechanically compare this range against AMD's authoritative GC 9.0 register database. Every complete field should have matching shift and mask values, masks should align to shifts, and reserved masks should cover only documented unused bits.
- Cross-check every register family in this chunk against `gc_9_0_offset.h` for matching `ixDIDT_*` or `mm*` address definitions.
- Run static sanity checks for repeated layouts: DBR stall-pattern registers should use 15-bit pattern masks plus one reserved bit per lane, DBR weight registers should contain four 8-bit lanes, and full-width counters should use `0xFFFFFFFFL`.
- Exercise Vega10 DIDT enable/disable paths with DBR ramping and DIDT EDC platform capabilities enabled. Expected signals include successful `PPSMC_MSG_ConfigureGfxDidt`, stable graphics operation, no unexpected forced stalls, and no reset loops.
- Validate EDC/RAS counter decoding on GC 9.0 hardware or simulator traces by injecting or observing TA, TCI, TCP, and TD SEC/DED/SED events and confirming the named fields in `gfx_v9_0.c` report the expected packed 2-bit values.
- During graphics stress and power-management tests, sample DIDT stall-event counters, EDC overflow state, throttle level, and rolling power delta to verify fields move plausibly and do not report impossible reserved-bit values.
- Regression signals include GPU hangs during DIDT setup, unexpected throttling or performance collapse, incorrect RAS counter names/counts, stale overflow reporting, or compile failures in SOC15 field helpers.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002627`. It covers lines 29721-30033 of `gc_9_0_sh_mask.h`, the final chunk of the file. The previous chunk owns the beginning of `DIDT_TCP_EDC_STALL_DELAY_4` and earlier TCP EDC definitions. The final per-file research should reconcile that artificial boundary and then treat this chunk as the DBR DIDT/EDC and terminal EDC-counter section of the generated GC 9.0 shift/mask header.
