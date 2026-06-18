# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 32569-34980

## Scope

This chunk is a large middle section of AMD's generated GC 12.1.0 shift/mask register-layout header. It contains C preprocessor constants only: no functions, structs, enums, variables, locks, allocation paths, or executable branches are introduced here. Each register field is represented by a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro.

The range starts inside `PA_SC_ENHANCE_2`: the first lines in this chunk contain the tail of that register's masks, while the corresponding register comment and early field shifts are in the previous chunk. It then covers complete or near-complete field layouts for these hardware areas:

- Pixel/scissor and primitive-binner controls: `PA_SC_ENHANCE_3`, `PA_SC_BINNER_CNTL_OVERRIDE`, `PA_SC_PBB_OVERRIDE_FLAG`, `PA_SC_DSM_CNTL`, `PA_SC_TILE_STEERING_CREST_OVERRIDE`, SC/PH FIFO sizing, packer wave-ID controls, attribute-management controls, binner event controls 0-3, binner timeout/performance controls, VRS/HiZ/HiS surface and debug controls, and SC memory scope.
- User-accessible shader queue and shader memory registers: `SQ_RUNTIME_CONFIG`, global SQ debug status, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `SQ_DEBUG`, trap base/memory address registers, `SQ_IND_INDEX_USER`, `SQ_CMD_USER`, and `SQ_IND_DATA_USER`.
- PF-only SPI debug/configuration registers: CDBG enables, global wave stall/trap controls, reset debug, GDS maximum wave ID, arbiter/feature/resource-limit controls, PC config controls, and compute wavefront context-save busy status.
- PF-only UTCL1 controls: `UTCL1_CTRL_0`, invalidation-request disable, `UTCL1_CTRL_2`, FIFO sizing, GCRD target/credit controls, and `UTCL1_IDENTITY_MODE0` through `UTCL1_IDENTITY_MODE7`.
- PF-only TCP/TXA/LDS controls: TCP invalidate/status/control registers, compression and arbitration controls, TCP-UTCL0 controls/status, request-ID hash and set-hash programming, `TCP_CNTL3`, `LDS_CONFIG`, per-CU resource-reserve controls, resource-reserve enables, thrashing/retry counters, TXA controls/status/arbitration, TCP credit controls, congestion control, and TDM controls.
- Graphics-user registers: tessellation/off-chip parameters, GE position/primitive ring base and size, line stipple and screen extents, P3D/HP3D/SC trap-screen controls, thread-trace user data, SQC cache invalidation, TA CS base address, DB occlusion counters, SPI config/throttle/attribute-ring/SQG/WGS/group-launch/GOG/TCP controls.

The range ends in the middle of `SPI_TCP_CNTL`: it includes the shifts for `DEFAULT_LDS_PARTITIONS`, `MIN_LDS_PARTITIONS`, `MAX_LDS_PARTITIONS`, `IDLE_ALLOC_OPT_DIS`, `PARTIAL_DRAIN_DIS`, `LDS_PINGPONG_DIS`, and only the `DEFAULT_LDS_PARTITIONS_MASK`. The remaining `SPI_TCP_CNTL__*` masks are outside this chunk and must be merged from the next chunk for a complete per-file report.

Although this repository path is under `ceph-client`, this file is AMDGPU DRM hardware metadata for the GC 12.1.0 graphics IP block, not distributed-filesystem code.

## Purpose

`gc_12_1_0_sh_mask.h` supplies the bit-level contract used by GC 12.1.0 AMDGPU and KFD code when packing and decoding MMIO register values. The companion `gc_12_1_0_offset.h` header gives register addresses; this file gives the bit positions inside those registers. Callers normally combine these macros through helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` before using SOC15 register accessors such as `RREG32_SOC15()` and `WREG32_SOC15()`.

The PA/SC/PH portion describes rasterization, primitive binning, packed-primitive behavior, VRS detail-rate handling, HiZ/HiS surface behavior, FIFO sizing, binner event inclusion, and performance-counter sampling controls. These fields influence draw batching, context-state grouping, event behavior inside binned rendering, depth/stencil hierarchical tests, clock gating, and debug overrides.

The SQ/SPI portions describe shader memory configuration, debug/trap controls, indirect user wave access, global SQ status, trap-handler base addresses, shader processor debug/stall controls, wave launch behavior, allocation/resource limits, and context-save busy state. In GC 12.1.0 consumers, nearby masks are used by `gfx_v12_1.c` and `amdgpu_amdkfd_gfx_v12_1.c` for trap enablement, KFD debug behavior, and device initialization.

The UTCL1/TCP/TXA portion describes translation-cache, texture/cache, memory-permission, XNACK, retry, hash, compression, credit, and arbitration controls. These fields are tied to shader memory access, VM translation/invalidation, atomic support, write-ack behavior, scratch/spill cache behavior, cache hashing, texture aligner behavior, and timeout/thrashing protection.

The graphics-user tail covers shader-stage ring buffers and debug-visible graphics state: tessellation factor and off-chip parameters, geometry-engine position and primitive rings, screen extents, trap-screen coordinates/counters, SQ thread-trace user-data registers, SQC cache invalidation status, TA base address, DB occlusion counters, and SPI scheduling/throttle/attribute-ring/group-launch controls.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The exported interface is the generated macro namespace consumed by AMDGPU/KFD GC 12.1.0 source files that include `gc/gc_12_1_0_sh_mask.h`.

Important macro families include:

- `PA_SC_ENHANCE_2__*` tail masks for SC/BCI/SPI early wakeup, break-batch behavior, PBB timeout and reset handling, null-primitive batching, and reserved bits. This chunk does not contain the full register definition.
- `PA_SC_ENHANCE_3__*` fields for PBB workload mode, EOP packet filtering, null-primitive and z-prepass optimizations, pixel wait/sync counters, packer force-EOV behavior, VRS AA-mask handling, and SC GL1X clock-gating disables.
- `PA_SC_BINNER_CNTL_OVERRIDE__*`, `PA_SC_PBB_OVERRIDE_FLAG__*`, `PA_SC_DSM_CNTL__*`, and `PA_SC_TILE_STEERING_CREST_OVERRIDE__*` for binning mode overrides, persistent/context states per bin, FPOVs per batch, pipe/RB/SA/SE tile steering, and forced EOV resources.
- `PA_SC_FIFO_SIZE__*`, `PA_SC_IF_FIFO_SIZE__*`, `PA_PH_INTERFACE_FIFO_SIZE__*`, `PA_SC_PACKER_WAVE_ID_CNTL__*`, `PA_SC_ATM_CNTL__*`, and `PA_SC_PKR_WAVE_TABLE_CNTL__*` for internal primitive/tile/interface FIFO depths, packer wave limits, attribute limits, and fine/coarse clock-gating controls.
- `PA_SC_BINNER_EVENT_CNTL_0..3__*` for how events such as streamout stats sampling, cache flushes, partial flushes, context-done, wait-sync, perf counter start/stop/sample, pipeline stat start/stop/sample, streamout flush, break-batch, and debug/trap events interact with binning.
- `PA_SC_BINNER_TIMEOUT_COUNTER__*` and `PA_SC_BINNER_PERF_CNTL_0..3__*` for timeout and performance histogram thresholds.
- `PA_SC_P3D_TRAP_SCREEN_HV_LOCK`, `PA_SC_HP3D_TRAP_SCREEN_HV_LOCK`, `PA_SC_TRAP_SCREEN_HV_LOCK`, and later matching `*_HV_EN`, `*_H`, `*_V`, `*_OCCURRENCE`, and `*_COUNT` fields for trap-screen write protection, enablement, coordinates, occurrence limits, and counters.
- `PA_SC_VRS_SURFACE_CNTL_1__*`, `PA_SC_HIZ_SURFACE_CNTL__*`, `PA_SC_HIS_SURFACE_CNTL__*`, `PA_SC_HIZ_DEBUG__*`, `PA_SC_HIS_DEBUG__*`, and `SC_MEM_SCOPE__*` for VRS rate/debug behavior, hierarchical Z/stencil cache flush/filter/prefetch/debug behavior, and surface memory scopes.
- `SQ_RUNTIME_CONFIG`, `SQ_DEBUG_STS_GLOBAL`, `SQ_DEBUG_STS_GLOBAL2`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, and `SQ_DEBUG` for SQ runtime/debug state and shader memory address/alignment/prefetch/retry controls. `gfx_v12_1.c` defines `DEFAULT_SH_MEM_CONFIG` from `SH_MEM_CONFIG__ADDRESS_MODE__SHIFT`, `SH_MEM_CONFIG__ALIGNMENT_MODE__SHIFT`, and `SH_MEM_CONFIG__INITIAL_INST_PREFETCH__SHIFT`.
- `SQ_SHADER_TBA_LO/HI` and `SQ_SHADER_TMA_LO/HI` for trap-handler base and memory addresses, including the `SQ_SHADER_TBA_HI__TRAP_EN` bit.
- `SQ_IND_INDEX_USER`, `SQ_CMD_USER`, and `SQ_IND_DATA_USER` for user indirect SQ access: wave/workitem selection, auto-increment, command mode, VMID/queue targeting, and data transfer.
- `SPI_CDBG_SYS_GFX`, `SPI_CDBG_SYS_HP3D`, `SPI_CDBG_SYS_CS0`, `SPI_GDBG_WAVE_CNTL`, `SPI_GDBG_TRAP_CONFIG`, `SPI_GDBG_WAVE_CNTL3`, and `SPI_RESET_DEBUG` for shader-pipe debug enables, global wave stalls, trap routing, per-stage wave stalls, and reset-status snapshots.
- `GDS_COMPUTE_MAX_WAVE_ID`, `SPI_ARB_CNTL_0`, `SPI_FEATURE_CTRL`, `SPI_SHADER_RSRC_LIMIT_CTRL`, `PC_CONFIG_CNTL_0/1`, and `SPI_COMPUTE_WF_CTX_SAVE_STATUS` for compute wave limits, SPI arbitration/features/resource limits, primitive/PC configuration, and per-pipe/per-queue context-save busy bits.
- `UTCL1_CTRL_0`, `UTCL1_UTCL0_INVREQ_DISABLE`, `UTCL1_CTRL_2`, `UTCL1_FIFO_SIZING`, `GCRD_SA0_TARGETS_DISABLE`, `GCRD_SA1_TARGETS_DISABLE`, `GCRD_CREDIT_SAFE`, and `UTCL1_IDENTITY_MODE0..7` for UTCL1 invalidation, duplicate detection, translation fault locking, range invalidation, credits, target disablement, and identity-mode return attributes such as snoop, fragment size, permissions, XNACK, PTE TMZ/no-PTE, SPA, IOSTEER, memory type, dirty/prefetch/TEE/HDM flags.
- `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, `TCP_CNTL2`, `TCP_CREDIT`, `TCP_DEBUG_DATA`, `TCP_COMPRESSION_CNTL`, `TCP_ARB`, `TCP_UTCL0_CNTL1`, `TCP_UTCL0_CNTL2`, and `TCP_UTCL0_STATUS` for texture/cache invalidation, busy/status reporting, cache behavior, compression overrides, atomic/permission response behavior, invalidation toggles, XNACK/retry/protection status, and fine/coarse clock gating. `gfx_v12_1.c` uses `TCP_UTCL0_CNTL1__ATOMIC_REQUESTER_EN`, `TCP_CNTL3__DISABLE_EARLY_WRITE_ACK`, and `TCP_CNTL__TCP_SPILL_CACHE_DISABLE` through `REG_SET_FIELD()`.
- `TCP_RQID_HASH_CNTL`, `TCP_SET_HASH_CFG`, and `TCP_SET_HASH_MASK_*` for request-ID/set hash programming across 64, 128, 192, 256, 320, 384, and 448-entry mask families.
- `TCP_CNTL3`, `LDS_CONFIG`, `SPI_RESOURCE_RESERVE_CU_0..15`, and `SPI_RESOURCE_RESERVE_EN_CU_0..15` for TCP priority/coalescing/write-ack behavior, LDS configuration, and per-CU VGPR/SGPR/LDS/wave/barrier reserve settings plus enable/type/queue masks.
- `TCP_UTCL0_THRASHING_CTRL`, retry threshold counters, `TCP_UTCL0_XNACK_RETRY`, retry timer thresholds, `TXA_CNTL`, `TXA_CNTL_AUX`, `TXA_CNTL2`, `TXA_STATUS`, `TXA_TDM_ARB_CNTL`, `TCP_CREDIT2`, `VC_CONGESTION_CONTROL`, and `TXA_TDM_CNTL` for VM thrash/retry protection, XNACK retry accounting, texture aligner credits, determinism disables, busy status, TDM arbitration, and congestion limits.
- `VGT_TF_RING_SIZE`, `VGT_HS_OFFCHIP_PARAM`, `GE_POS_RING_BASE/SIZE`, and `GE_PRIM_RING_BASE/SIZE` for tessellation/off-chip and graphics-engine position/primitive ring configuration.
- `PA_SU_LINE_STIPPLE_VALUE`, `PA_SC_LINE_STIPPLE_STATE`, `PA_SC_SCREEN_EXTENT_MIN/MAX_0/1`, and the P3D/HP3D/SC trap-screen field families for draw-state, screen-region, and trap-screen programming.
- `SQ_THREAD_TRACE_USERDATA_0..7`, `SQC_CACHES`, `TA_CS_BC_BASE_ADDR`, `TA_CS_BC_BASE_ADDR_HI`, and `DB_OCCLUSION_COUNT0..3_LOW/HI` for thread-trace annotations, SQC cache invalidate/complete bits, texture-address base, and 63-bit occlusion query counters.
- `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_CNTL_2`, `SPI_GS_THROTTLE_CNTL1/2`, `SPI_ATTRIBUTE_RING_BASE/SIZE`, `SPI_SQG_EVENT_CTL`, `SPI_COMPUTE_WGS_CONTROL`, `SPI_GRP_LAUNCH_GUARANTEE_ENABLE/CTRL`, `SPI_GOG_ALLOCATION_CTRL`, and the partial `SPI_TCP_CNTL` definition for SPI scheduling, context-save timing, throttling, attribute-ring memory, SQG events, WGS, launch guarantees, allocation retry/timeout, and TCP/LDS partition behavior.

Representative direct consumers in this repository include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.c`, which includes this header, builds `DEFAULT_SH_MEM_CONFIG` from `SH_MEM_CONFIG` fields, enables TCP atomics with `TCP_UTCL0_CNTL1`, disables early write ACK with `TCP_CNTL3`, disables TCP spill cache with `TCP_CNTL`, and enables per-VMID debug traps using SPI debug fields outside but adjacent to this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12_1.c`, which includes this header and maps KFD debug trap masks through GC 12.1 SPI debug-control fields, using the same generated-mask contract as the SQ/SPI debug families in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_1.c`, `imu_v12_1.c`, `gfxhub_v12_1.c`, `sdma_v7_1.c`, `soc_v1_0.c`, and KFD queue/MQD files, which include the GC 12.1.0 generated register headers and rely on offset/mask consistency for low-level register programming.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime pattern for fields in this chunk is:

1. GC 12.1.0 initialization or a debug/performance path selects the target GC instance/XCC, often through `GET_INST(GC, xcc_id)` and SOC15 register helpers.
2. The driver reads or initializes a 32-bit register value.
3. It uses `REG_SET_FIELD()` with one of these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pairs to pack a field value, or uses `REG_GET_FIELD()` to decode a readback value.
4. It writes the packed value to the register offset from `gc_12_1_0_offset.h` or interprets the readback as a status/debug snapshot.

For GC 12.1 golden-register setup, `gfx_v12_1_init_golden_registers()` iterates over active XCCs. It calls helper functions that read `regTCP_UTCL0_CNTL1`, set `ATOMIC_REQUESTER_EN`, read `regTCP_CNTL3`, set `DISABLE_EARLY_WRITE_ACK`, read `regTCP_CNTL`, set `TCP_SPILL_CACHE_DISABLE`, and write the values back. Those runtime branches live in `gfx_v12_1.c`; this chunk only defines the bit locations used by the field helpers.

For KFD and debug flows, consumers program SPI/SQ debug registers to enable traps, stall wave launch, map software exception masks to hardware exception fields, and issue SQ commands. The `SQ_IND_INDEX_USER`, `SQ_CMD_USER`, `SQ_IND_DATA_USER`, `SPI_GDBG_WAVE_CNTL`, `SPI_GDBG_TRAP_CONFIG`, and `SPI_GDBG_WAVE_CNTL3` field definitions describe the user/privileged debug transport and stall/trap surfaces; the actual command sequencing and synchronization live in AMDGPU/KFD code.

For rasterization and binning, state setup or generated clearstate packets can write PA/SC/PH controls before or during graphics pipeline initialization. Runtime draw submission then depends on those programmed binner, FIFO, VRS, HiZ/HiS, and screen/trap-state registers while hardware processes primitives, events, and depth/stencil tests.

For memory/cache behavior, TCP/UTCL1/TXA/SQC fields are used when the driver changes cache-invalidation, atomics, translation, retry, XNACK, compression, hashing, spill, and write-ack policies. Some fields are configuration state written during initialization; others are trigger/status fields such as `TCP_INVALIDATE__START`, `TCP_STATUS__*`, `TCP_UTCL0_STATUS__*`, `TXA_STATUS__*`, or `SQC_CACHES__COMPLETE`.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware register state owned by the GPU and programmed by AMDGPU/KFD.

PA/SC/PH fields generally persist as graphics pipeline configuration until rewritten, reset, or restored from context state. Binning mode, FIFO sizing, VRS surface behavior, HiZ/HiS controls, event inclusion, and clock-gating overrides can affect many draws after a single write. Incorrect masks here can cause overbroad or underbroad binning, missed synchronization events, depth/stencil culling errors, invalid VRS rate handling, or performance regressions that appear workload-dependent.

SQ/SPI debug and trap fields are live hardware debug state. Trap-handler base addresses, trap enable bits, wave-stall controls, SQ command fields, and indirect user data affect trap/debug behavior for selected waves, queues, VMIDs, or shader stages. Readback status such as `SQ_DEBUG_STS_GLOBAL` or `SPI_COMPUTE_WF_CTX_SAVE_STATUS` is volatile and should be treated as a snapshot unless the caller has quiesced the relevant engine.

Shader memory configuration fields such as `SH_MEM_BASES` and `SH_MEM_CONFIG` persist as shader-visible memory mode state. Wrong address mode, alignment mode, prefetch, retry, or base packing can break shader memory semantics across graphics and compute workloads.

UTCL1/TCP/TXA fields include both persistent policy and transient status. Translation-cache duplicate detection, invalidation filtering, identity-mode return attributes, TCP compression, hash masks, credits, atomic enablement, early-write-ack behavior, XNACK/retry, thrashing thresholds, and TXA determinism controls remain in force until changed. Status and counter fields such as TCP busy bits, UTCL0 fault/retry/PRT/timeout detection, retry counters, TXA busy bits, and SQC cache complete bits are hardware-updated observations.

Resource reservation fields for `SPI_RESOURCE_RESERVE_CU_0..15` and `SPI_RESOURCE_RESERVE_EN_CU_0..15` persist per CU/resource slot and can change how VGPR, SGPR, LDS, wave, barrier, type, and queue resources are reserved. Bad packing can reduce occupancy, starve queues, or create fairness/performance bugs.

Graphics-user ring, screen, trace, cache, TA, DB, and SPI fields persist as graphics pipeline or debug/performance configuration. GE ring base/size fields describe memory-backed hardware buffers; thread-trace user-data fields become diagnostic annotations; DB occlusion counters are hardware-updated query results split into low and high halves; SPI attribute-ring fields describe memory size and cache policy for shader interpolation/attribute storage.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register family being used consistently:

- `gc_12_1_0_offset.h` supplies the matching `reg...`, `mm...`, and `ix...` register offsets. This chunk supplies only field shifts and masks.
- `soc24_enum.h` supplies enum values used by GC 12.1.0 code for register fields and packet definitions.
- AMDGPU SOC15 helpers and common register helpers provide `RREG32_SOC15()`, `WREG32_SOC15()`, `SOC15_REG_OFFSET()`, `REG_SET_FIELD()`, and `REG_GET_FIELD()`.
- `gfx_v12_1.c` integrates `SH_MEM_CONFIG`, TCP, and SPI/SQ generated masks with initialization, ring setup, debug trap enablement, golden-register programming, and XCC selection.
- `amdgpu_amdkfd_gfx_v12_1.c`, `kfd_mqd_manager_v12_1.c`, and `kfd_device_queue_manager_v12_1.c` integrate the same generated mask header with KFD queue setup and debugger/trap behavior.
- `mes_v12_1.c` and `imu_v12_1.c` include the generated GC 12.1.0 headers for micro-engine and initialization behavior; they rely on the header set being synchronized even when they do not use every field in this specific chunk.
- Clearstate and packet-generation paths can program PA/SC/SPI/GE/DB state via packet streams rather than direct MMIO. The field definitions still describe the hardware layout used when code needs to pack or decode those registers.

The chunk is intentionally low level. It does not decide which binner settings are selected for a workload, when to enable KFD traps, which cache policy is correct for a buffer, when to invalidate TCP/SQC caches, or how performance/debug data is surfaced to user space. Those policies live in AMDGPU, KFD, Mesa/userspace command streams, firmware, and hardware initialization data.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong numeric shift or mask compiles cleanly but programs or decodes the wrong hardware bits.
- The range is not register-aligned at either end. `PA_SC_ENHANCE_2` is incomplete at the start, and `SPI_TCP_CNTL` is incomplete at the end. Whole-file research must merge adjacent chunks before making complete claims about those registers.
- Many fields are single-bit disables or overrides. Inverting the meaning in documentation or code review is easy: names such as `DISABLE_*`, `FORCE_*`, `*_OVERRIDE`, and `*_NOFILL` require careful reading at each call site.
- PA/SC binner event controls use many 2-bit fields for event treatment. Mixing event fields or treating them as booleans can make binned rendering miss flushes, break batches unnecessarily, or include the wrong synchronization events.
- FIFO, wave-limit, credit, timeout, and threshold fields directly affect hardware flow control. Incorrect masks can create hangs, underutilization, starvation, or workload-specific performance cliffs.
- VRS, HiZ, and HiS fields affect visible rendering correctness. Wrong mask usage can change shading rate, depth/stencil culling, flush behavior, or prefetch behavior without an obvious kernel error.
- SQ/SPI debug fields are security- and stability-sensitive because they affect trap routing, wave stalls, user indirect access, and per-VMID/queue debug behavior. Incorrect field layout can stall unrelated workloads or leak misleading debug state.
- Shader memory fields affect address mode, alignment, prefetch, retry, private/shared bases, and trap addresses. A bad mask can break shader memory semantics across many queues.
- UTCL1 identity-mode fields encode permission, XNACK, TMZ, no-PTE, SPA, IOSTEER, MTYPE, dirty, prefetch, TEE, and HDM return attributes. Cross-generation reuse or partial packing errors can compromise fault behavior or memory isolation.
- TCP/TXA controls include atomic enablement, compression bypass/disable, write-combining, early write ACK, illegal PCIe atomic handling, XNACK retry, and deterministic behavior. These are not cosmetic performance bits; wrong values can change correctness and coherency.
- `TCP_SET_HASH_MASK_*` families are repetitive. A generation or copy/paste error in a single set size can affect only certain cache hash geometries, making failures hard to reproduce.
- Per-CU resource reservation fields repeat for 16 CUs and include matching enable registers. Array-like programming must keep data and enable registers aligned by CU index.
- DB occlusion counters are split into low and high registers with a 31-bit high mask. Readback consumers must handle split-counter consistency and rollover.
- Thread-trace user-data registers are full-width data fields; they are easy to treat as harmless, but they affect diagnostic correlation and trace interpretation.
- Cross-generation names are reused heavily. GC 12.1.0 masks must be paired with GC 12.1.0 offsets and not borrowed from GC 12.0.0, GC 11, GC 10, or GCA headers even when macro names match.

## Test Signals

Useful validation combines generated-data checks, build coverage, and hardware/runtime behavior:

- Build AMDGPU and KFD with GC 12.1.0 support enabled. This catches missing or renamed macros in `gfx_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `mes_v12_1.c`, `imu_v12_1.c`, `gfxhub_v12_1.c`, `sdma_v7_1.c`, `soc_v1_0.c`, `kfd_mqd_manager_v12_1.c`, and `kfd_device_queue_manager_v12_1.c`.
- Mechanically compare this chunk against AMD's authoritative GC 12.1.0 register database, focusing on repeated families such as `PA_SC_BINNER_EVENT_CNTL_*`, `UTCL1_IDENTITY_MODE*`, `TCP_SET_HASH_MASK_*`, `SPI_RESOURCE_RESERVE_CU_*`, and `SPI_RESOURCE_RESERVE_EN_CU_*`.
- Verify that `gc_12_1_0_offset.h` and `gc_12_1_0_sh_mask.h` come from the same generated source revision. Offset/mask mismatches are especially dangerous for TCP/UTCL1, SQ/SPI debug, GE ring, SQC cache, and PA/SC binner controls.
- Exercise GC 12.1 initialization on hardware and confirm that golden-register writes for `TCP_UTCL0_CNTL1`, `TCP_CNTL3`, and `TCP_CNTL` apply the expected fields: atomics enabled, early write ACK disabled when intended, and TCP spill cache disabled when intended.
- Run graphics workloads that stress primitive binning, streamout, partial flushes, pipeline stats, perf counter start/stop/sample events, VRS, HiZ, HiS, line stipple, screen extents, and occlusion queries. Regressions may show as rendering corruption, missed occlusion counts, hangs, or large performance shifts.
- Run KFD debugger/trap tests on GC 12.1 hardware. Healthy signals include correct trap-on-start/trap-on-end behavior, correct exception-mask mapping, no unrelated VMID stalls, and sane wave launch mode behavior.
- Exercise shader memory configuration and trap-handler paths, including private/shared memory bases, retry behavior, trap address programming, and indirect SQ user access where supported.
- Exercise VM invalidation, atomics, XNACK/retry, and translation-fault workloads that stress UTCL1/TCP fields. Expected signals include correct fault attribution, no illegal stale translations, no retry storms, and correct atomic behavior.
- Test TCP cache behavior with workloads sensitive to compression, write-combining, spill cache, hash-set selection, and early write acknowledgement. Incorrect masks often appear as data corruption, intermittent shader faults, or performance cliffs rather than compile errors.
- Validate SQ thread trace and SQC cache invalidate flows. Thread traces should carry expected user-data values, and SQC invalidate sequences should observe the `COMPLETE` status as expected.
- Read DB occlusion counter low/high pairs under controlled query workloads and verify monotonic, plausible counter values with correct high-half masking.
- Run suspend/resume, GPU reset, and queue preemption tests with active graphics and compute workloads. SPI context-save status, TCP/UTCL1 state, and PA/SC state should recover without persistent stalls or corrupted rendering.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002605`. It covers lines 32569-34980 of `gc_12_1_0_sh_mask.h`. The previous chunk contains the beginning of `PA_SC_ENHANCE_2`; this chunk starts at that register's tail masks. The next chunk must provide the remaining `SPI_TCP_CNTL__*` masks after `DEFAULT_LDS_PARTITIONS_MASK`. The final per-file research document should merge these adjacent chunks to present complete register definitions and avoid treating the boundary partials as whole-register coverage.
