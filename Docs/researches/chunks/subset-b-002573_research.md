# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 10045-12529

## Scope

This chunk is a large middle section of the generated AMD GC 12.0.0 shader-mask header. It contains C preprocessor constants only: no functions, structs, enums, includes, storage, locks, or executable branches are introduced here. The macros define bit shifts and masks for register fields used by the GC virtual-memory hub, GCVM L2 performance counters and translation controls, and graphics/compute command-processor registers.

The range starts in the middle of the `GCVM_INVALIDATE_ENG2_SEM` definition: line 10045 contains only the `SEMAPHORE_MASK`, while the matching `SEMAPHORE__SHIFT` is in the previous chunk. It then covers:

- `GCVM_INVALIDATE_ENG3_SEM` through `GCVM_INVALIDATE_ENG17_SEM`.
- `GCVM_INVALIDATE_ENG0_REQ` through `GCVM_INVALIDATE_ENG17_REQ`.
- `GCVM_INVALIDATE_ENG0_ACK` through `GCVM_INVALIDATE_ENG17_ACK`.
- `GCVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` through engine 17.
- `GCVM_CONTEXT0..15_PAGE_TABLE_BASE_ADDR`, `START_ADDR`, and `END_ADDR` low/high field masks.
- Per-PF/VF GCVM L2 PTE cache fragment-size fields for the global register and contexts 0 through 15.
- GCVML2, GCMC VM L2, and GCUTCL2 performance-counter result, select, mode, and configuration fields.
- GCUTCL2/GCVM IOMMU, translation-bypass, translation-assist, translation-fault, and compression override controls.
- Command-processor and CPC fields for CU mask programming, EOP queue wait, clock-gating sync, interrupt info/status/control, virtualization status, PASID, GFX errors, UTCL1 controls and errors, ring-buffer programming, doorbells, priorities, debug registers, ECC/EDC reporting, suspend/resume, VMID reset/preempt/status, context save, and DDID control.

The range ends at the `//CP_DDID_CNTL` comment on line 12529. The `CP_DDID_CNTL__*` field definitions that follow that comment are outside this chunk and should be covered by the next chunk.

Although this repository is under a `ceph-client` source tree, this file is AMDGPU DRM hardware metadata for the GC 12.0.0 graphics IP block, not distributed-filesystem code.

## Purpose

`gc_12_0_0_sh_mask.h` is generated register-layout metadata. Each `REGISTER__FIELD__SHIFT` macro tells callers how far to shift a logical field, and each `REGISTER__FIELD_MASK` macro identifies the occupied bits in the 32-bit register value. AMDGPU code combines these macros through helpers such as `REG_SET_FIELD()` and raw mask operations before writing MMIO registers through `WREG32_SOC15*()` helpers, or decodes readback values through matching `REG_GET_FIELD()`-style usage.

The GCVM portion of this chunk supports graphics VM invalidation and address-space programming. Driver code builds invalidation requests by setting per-VMID request bits, flush type, L2 PTE/PDE invalidation bits, L1 PTE invalidation, optional logging, protection-fault address clearing, and optional 4 KiB-only invalidation fields. It also programs per-engine invalidation address ranges and per-context page-table base/start/end address registers. The companion offset header supplies the register addresses; this header supplies the field layout.

The GCVML2/GCMC/GCUTCL2 performance-counter portion provides selector, mode, counter result, and result-control fields for low-level performance collection around graphics VM L2 and UTCL2. The translation-control fields cover VMID translation bypass, GPU host translation enable, GPUVA VMID translation assist, IOMMU control/performance optimization, translation fault control, and compression-enable override behavior.

The CP/CPC portion supports command-processor setup and observability. GC v12 graphics code uses `CP_RB0_CNTL` masks to size and configure the graphics ring buffer, `CP_INT_CNTL_RING0` masks to enable or disable timestamp, generic, busy/empty, idle, privileged-register, privileged-instruction, and opcode-error interrupts, and CPC interrupt masks for KFD compute queue interrupt enablement. Other fields in this chunk define the bit layout for ring pointers, doorbell ranges, queue priorities, debug/status registers, fatal-error and ECC reporting, suspend/resume context save, VMID reset/preempt/status, and DDID controls.

## Important APIs, Types, And Macros

There are no callable APIs or C data types in this chunk. The exported interface is the macro naming contract consumed by AMDGPU and KFD source files that include `gc/gc_12_0_0_sh_mask.h`.

Important macro families include:

- `GCVM_INVALIDATE_ENGn_SEM__SEMAPHORE_MASK` and `GCVM_INVALIDATE_ENGn_SEM__SEMAPHORE__SHIFT` for invalidation-engine ownership/semaphore fields. This chunk contains a partial engine-2 entry plus full engine-3 through engine-17 entries.
- `GCVM_INVALIDATE_ENGn_REQ__PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0/1/2`, `INVALIDATE_L1_PTES`, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and `INVALIDATE_4K_PAGES_ONLY` fields. These are repeated for engines 0 through 17.
- `GCVM_INVALIDATE_ENGn_ACK__PER_VMID_INVALIDATE_ACK` and `GCVM_INVALIDATE_ENGn_ACK__PAGE_TABLE_ID` fields for invalidation completion/status.
- `GCVM_INVALIDATE_ENGn_ADDR_RANGE_LO32__ADDR_RANGE_LO32`, `__SYSTEM_ACCESS_MODE`, and `__ENABLE` plus `GCVM_INVALIDATE_ENGn_ADDR_RANGE_HI32__ADDR_RANGE_HI32` for range-limited invalidations.
- `GCVM_CONTEXTn_PAGE_TABLE_BASE_ADDR_LO32/HI32`, `START_ADDR_LO32/HI32`, and `END_ADDR_LO32/HI32` fields for contexts 0 through 15. These expose low/high halves of page-table base and virtual-address range registers.
- `GCVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `GCVM_L2_CONTEXTn_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` fields for PF/VF-specific PTE cache fragment sizing. The repeated fields are `VF0`, `VF1`, and `VF2`.
- `GCVML2_PERFCOUNTER2_0_SELECT`, `GCVML2_PERFCOUNTER2_1_SELECT`, `*_SELECT1`, and `*_MODE` fields for selecting up to four events, counter modes, performance modes, and counter-mode options.
- `GCMC_VM_L2_PERFCOUNTERn_CFG`, `GCUTCL2_PERFCOUNTERn_CFG`, and their result-control registers for selecting sources, increments, client IDs, read counts, clear behavior, and pulse width.
- `GCUTCL2_TRANSLATION_BYPASS_BY_VMID`, `GCVM_IOMMU_GPU_HOST_TRANSLATION_ENABLE`, `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`, `GCVM_IOMMU_CONTROL_REGISTER`, `GCVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`, `GCUTC_TRANSLATION_FAULT_CNTL0/1`, and `GCUTCL2_COMP_EN_OVERRIDES`.
- `CP_CU_MASK_ADDR_LO/HI` and `CP_CU_MASK_CNTL` for command-processor compute-unit mask location and control.
- `CP_RB0_CNTL` and `CP_RB_CNTL`, with fields such as `RB_BUFSZ`, `RB_BLKSZ`, `BUF_SWAP`, `MIN_AVAILSZ`, `MIN_IB_AVAILSZ`, `CACHE_POLICY`, `RB_NO_UPDATE`, and `RB_RPTR_WR_ENA`.
- `CP_RB0_BASE`, `CP_RB_BASE`, `CP_RB0_BASE_HI`, `CP_RB0_WPTR`, `CP_RB_WPTR`, `CP_RB0_RPTR_ADDR`, `CP_RB_RPTR_ADDR`, and high-half variants for graphics ring-buffer base, write pointer, and read-pointer writeback addresses.
- `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING0`, `CP_INT_STATUS_RING0`, `CPC_INT_CNTL`, and `CPC_INT_STATUS` for command-processor interrupt enables and status bits.
- `CP_GFX_ERROR`, `CP_FATAL_ERROR`, `CP_ECC_FIRSTOCCURRENCE`, `CP_ECC_FIRSTOCCURRENCE_RING0`, `GB_EDC_MODE`, and `CC_GC_EDC_CONFIG` for error and EDC/ECC reporting.
- `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, `CPF_UTCL1_CNTL`, `CPG_UTCL1_ERROR`, and `CPC_UTCL1_ERROR` for command-processor UTCL1 controls and error observability.
- `CP_VIRT_STATUS`, `CPC_INT_PASID`, `CP_RB_VMID`, `CP_ME0_PIPE0_VMID`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, and `CP_VMID_STATUS` for virtualization, PASID/VMID attribution, reset, preemption, and status.
- `CP_ME0_PIPE_PRIORITY_CNTS`, `CP_RING_PRIORITY_CNTS`, `CP_ME1_PIPE_PRIORITY_CNTS`, `CP_ME0_PIPE0_PRIORITY`, `CP_RING0_PRIORITY`, `CP_ME1_PIPE0_PRIORITY`, and `CP_ME1_PIPE1_PRIORITY` for queue and pipe priority programming.
- `CP_DEBUG`, `CP_DEBUG_2`, `CP_CPF_DEBUG`, `CP_CPC_DEBUG`, `CP_ME3_INT_STAT_DEBUG`, and `CP_ME1_INT_STAT_DEBUG` for debug snapshots.
- `CPC_SUSPEND_CTX_SAVE_BASE_ADDR_LO/HI`, `CPC_SUSPEND_CTX_SAVE_CONTROL`, stack/state offsets and sizes, `CP_SUSPEND_RESUME_REQ`, `CP_SUSPEND_CNTL`, and `CP_IQ_WAIT_TIME3` for CPC/CP suspend and resume handling.
- `CPC_DDID_BASE_ADDR_LO/HI`, `CP_DDID_BASE_ADDR_LO/HI`, and `CPC_DDID_CNTL`. The chunk reaches the `CP_DDID_CNTL` comment but not its field definitions.

Representative direct consumers in this repository include:

- `amdgpu/gfxhub_v2_1.c`, where `gfxhub_v2_1_get_invalidate_req()` builds a `GCVM_INVALIDATE_ENG0_REQ` value with `REG_SET_FIELD()` and where hub initialization records the offsets and spacing for `GCVM_INVALIDATE_ENG0_SEM`, `REQ`, `ACK`, and address-range registers.
- `amdgpu/gfxhub_v2_1.c`, where `gfxhub_v2_1_program_invalidation()` writes all 18 invalidation engines' address ranges using `mmGCVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` plus the generated engine address stride.
- `amdgpu/gfx_v12_0.c`, where graphics-ring setup uses `CP_RB0_CNTL` field macros to write ring-buffer size and block size before programming base, read pointer, and write pointer registers.
- `amdgpu/gfx_v12_0.c`, where interrupt handlers use `CP_INT_CNTL_RING0` fields for context busy/empty, compare busy, graphics idle, timestamp, generic, privileged register, opcode error, and privileged instruction interrupts.
- `amdgpu/amdgpu_amdkfd_gfx_v12.c`, where KFD enables CPC timestamp and opcode-error interrupts using `regCPC_INT_CNTL` plus the corresponding CP interrupt-mask bits.
- `amdkfd/kfd_mqd_manager_v12.c` and `amdkfd/kfd_device_queue_manager_v12.c`, which include this header for GC v12 queue-management field definitions used alongside `v12_structs.h` and `soc24_enum.h`.

## Control Flow

This header has no runtime control flow. The direct behavior is compile-time macro substitution.

The implied runtime flow for GCVM invalidation is:

1. GC v12 gfxhub initialization records the base offsets for context page-table registers and invalidation engine 0, plus register distances between contexts and engines.
2. The driver programs page-table base/start/end registers for each VM context using the offset header for addresses and this header's field layout for packing values when field helpers are used.
3. The driver initializes invalidation address ranges for engines 0 through 17, commonly to a broad range when full-range invalidations are expected.
4. On a TLB/cache invalidation request, the driver builds a `GCVM_INVALIDATE_ENG0_REQ` value with the requested VMID bit, flush type, L2 PTE/PDE invalidation bits, L1 PTE invalidation bit, and related controls.
5. The VM hub invalidation code writes the selected engine request register, waits for the corresponding `ACK` state through the vmhub machinery, and uses semaphore/engine spacing to coordinate repeated requests.

The implied flow for GC v12 graphics-ring setup is:

1. `gfx_v12_0` switches to the target graphics pipe under SRBM serialization.
2. The driver computes the ring-buffer size as a power-of-two log value.
3. `REG_SET_FIELD(0, CP_RB0_CNTL, RB_BUFSZ, rb_bufsz)` and `REG_SET_FIELD(..., RB_BLKSZ, rb_bufsz - 2)` pack the ring-control value.
4. The driver writes `regCP_RB0_CNTL`, resets `CP_RB0_WPTR`/`CP_RB0_WPTR_HI`, programs read-pointer writeback addresses, write-pointer polling addresses, and writes ring base low/high values.
5. Later runtime ring updates use doorbells and write-pointer registers defined in this generated register family.

The implied flow for command-processor interrupt programming is:

1. The driver maps a ME/pipe to the proper CP interrupt-control register, such as `regCP_INT_CNTL_RING0`.
2. It reads the register, updates selected fields with `REG_SET_FIELD()` using `CP_INT_CNTL_RING0__*` masks and shifts, then writes the value back.
3. Different IRQ sources toggle different fields: timestamp/generic interrupts for fence/event paths, busy/empty/idle signals for scheduling and queue state, and privileged-register/opcode/privileged-instruction interrupts for fault reporting.
4. KFD compute paths can select a MEC/pipe through SRBM and write CPC interrupt-control bits for queue-level timestamp and opcode-error handling.

Performance-counter and debug-control macros follow similar write-read sequences: a consumer programs select/config/mode fields, triggers or lets counters run, then reads low/high result registers and decodes result-control/status fields. This chunk only supplies the bit layout; it does not implement PMU scheduling, counter ownership, reset sequencing, or user-space exposure.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe fields in hardware registers whose state is owned by the GPU and by the AMDGPU runtime.

GCVM page-table base/start/end fields represent persistent per-context hardware configuration while the device is initialized and while a VM context remains active. Wrong masks here can redirect GPU virtual-address translation, expand or shrink an address range incorrectly, or cause VM faults under otherwise valid workloads.

GCVM invalidation request, semaphore, ACK, and address-range fields are transient synchronization and cache-control state. Request bits initiate hardware work; ACK bits report completion or status; semaphore fields coordinate engine use. The address-range registers may persist as part of invalidation-engine configuration until reprogrammed. A stale or incorrectly packed request can leave old PTE/PDE translations in GCVM L1/L2 caches, which is a high-impact correctness failure because subsequent command-processor or shader memory accesses can use obsolete mappings.

Performance-counter select, mode, and config fields persist while a profiling session is active. Result low/high registers are hardware-updated observations. Result-control fields can clear, pulse, or select result behavior; incorrect writes can silently corrupt profiling data or interfere with another owner of the counter block.

Translation-bypass, IOMMU, GPUVA translation-assist, translation-fault, and compression override fields alter memory-translation behavior. These are not ordinary debug bits. They can change whether VMIDs bypass translation, whether GPU host translation is enabled, how faults are controlled/reported, and whether compression behavior is overridden. A bad field definition or cross-generation mismatch can break isolation, fault attribution, or host-memory access behavior.

CP ring-buffer control and pointer fields are persistent command-processor configuration. `CP_RB0_CNTL`, base address, read-pointer writeback address, write pointer, doorbell range, and VMID fields define how the hardware consumes commands from memory. Incorrect `RB_BUFSZ`, `RB_BLKSZ`, `RB_RPTR_WR_ENA`, base high/low, or pointer masks can lead to command stream stalls, reads from the wrong memory, lost fences, or GPU resets.

Interrupt control fields persist until disabled or reset. Interrupt status fields are hardware-reported and may be write-to-clear or otherwise side-effected depending on the register. These masks are used around scheduling, fence/event signaling, KFD queue errors, privileged access faults, opcode errors, ECC/EDC errors, and debug notifications.

Suspend/resume and context-save fields persist across CP/CPC suspend windows and are tied to GPU queue preemption and recovery state. Address, offset, size, policy, and enable bits must be packed exactly or context save areas and workgroup state can be misaddressed.

Debug, ECC, fatal-error, UTCL1 error, PASID, VMID, preempt, and status registers expose live hardware state. Readback values can change while queues run. Diagnostic consumers should treat them as snapshots unless they have quiesced, halted, or reset the relevant engine.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.0.0 register family being used consistently:

- `gc_12_0_0_offset.h` supplies the corresponding `reg...` and `mm...` register offsets. This chunk supplies only field shifts and masks.
- `soc24_enum.h` supplies enum values for some GC v12/SOC24 register fields, including DDID-related modes and sizes.
- `soc15_common.h` and AMDGPU register helpers provide `REG_SET_FIELD()`, `REG_GET_FIELD()`-style field manipulation and `RREG32_SOC15*()`/`WREG32_SOC15*()` MMIO access.
- `amdgpu/gfxhub_v2_1.c` integrates GCVM invalidation masks with the generic `amdgpu_vmhub` layout, engine spacing, context spacing, invalidation request construction, and fault-control plumbing.
- `amdgpu/gfx_v12_0.c` integrates CP ring, interrupt, debug, error, power, and queue fields with graphics-engine initialization, IRQ state transitions, fence signaling, queue scheduling, and reset recovery.
- `amdgpu/amdgpu_amdkfd_gfx_v12.c` integrates CPC interrupt fields with KFD compute queue handling under SRBM engine selection.
- `amdkfd/kfd_mqd_manager_v12.c` and `amdkfd/kfd_device_queue_manager_v12.c` integrate GC v12 mask definitions with MQD setup, CU masks, queue properties, SDMA/compute queue setup, and process-device cache policy.
- Runtime consumers rely on include selection matching the active ASIC/IP generation. Logical register names such as `CP_RB0_CNTL`, `CP_INT_CNTL_RING0`, and `GCVM_INVALIDATE_ENG0_REQ` recur across GC versions, but masks can vary by generation.

The chunk is intentionally low level. It does not decide which VMID to invalidate, how long to poll, which CP interrupt sources are enabled for a given workload, how KFD prioritizes queues, how performance counters are multiplexed, or how debug/status values are presented to users. Those policy decisions live in AMDGPU, KFD, PMU, and debug code.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong mask or shift compiles cleanly but packs or decodes the wrong hardware bits.
- The chunk starts mid-register and ends before the `CP_DDID_CNTL__*` field definitions. File-level research must merge adjacent chunks to avoid treating `GCVM_INVALIDATE_ENG2_SEM` or `CP_DDID_CNTL` as complete in this chunk alone.
- The invalidation-engine families are repeated for 18 engines. Copy/paste or generation errors in a single engine's `REQ`, `ACK`, or address-range fields can affect only some VM hub invalidation paths, making failures intermittent.
- `PER_VMID_INVALIDATE_REQ` and `PER_VMID_INVALIDATE_ACK` are 16-bit VMID bitmaps. Callers must avoid shifting beyond the represented VMID width and must preserve the expected VMID-to-bit mapping.
- Invalidation address ranges are split into low/high registers with enable and system-access-mode fields in the low half. Mis-pairing high/low fields or leaving range enable in the wrong state can make invalidation too broad, too narrow, or inactive.
- Page-table base/start/end fields are split across low/high registers and are page-aligned. Incorrect masking of low address bits can produce subtle VM faults or aliasing rather than an immediate build failure.
- Performance-counter fields include selectors, modes, clear controls, pulse widths, and client IDs. A counter may appear to work while counting the wrong event or wrong client if only selector packing is wrong.
- Translation-bypass and IOMMU control fields can affect VM isolation and fault behavior. These fields should not be casually reused from another GC generation.
- CP ring-buffer fields are sensitive during initialization. Wrong `RB_BUFSZ`/`RB_BLKSZ` packing can make hardware consume the wrong ring size, while wrong pointer high/low masks can break 64-bit GPU addresses.
- Interrupt enable/status macros share many similarly named fields across `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING0`, `CP_INT_STATUS_RING0`, `CPC_INT_CNTL`, and `CPC_INT_STATUS`. Mixing status masks with control registers or generic CP masks with ring-specific masks can suppress interrupts or create interrupt storms.
- The KFD GC v12 code writes `regCPC_INT_CNTL` using timestamp and opcode-error mask names from the CP interrupt ring layout. That pattern relies on compatible bit positions; any generated-layout divergence must be reviewed carefully.
- Debug, fatal-error, ECC/EDC, PASID, VMID, and preempt/status readbacks are volatile. Interpreting them without quiescing the relevant engine can create inconsistent diagnostic snapshots.
- Suspend/resume context save fields combine addresses, offsets, sizes, policy, and enable bits. Off-by-alignment errors can corrupt context save buffers or make preemption/resume fail only under load.
- Doorbell range and write-pointer-poll fields are security- and stability-sensitive because they bound user/queue signaling into the command processor.
- Cross-generation copy/paste is risky. GC v9/v10/v11/v12 headers share names but are not interchangeable; the active `gc_12_0_0_*` offset and mask headers must be paired.

## Test Signals

Useful validation is a mix of generated-data checks, build coverage, and hardware/runtime behavior:

- Build AMDGPU and KFD configurations that include `gc/gc_12_0_0_sh_mask.h`, especially `gfx_v12_0.c`, `gfxhub_v2_1.c`, `amdgpu_amdkfd_gfx_v12.c`, `kfd_mqd_manager_v12.c`, and `kfd_device_queue_manager_v12.c`. This catches missing or renamed macros but not wrong numeric masks.
- Mechanically compare this chunk against AMD's authoritative GC 12.0.0 register database, with special attention to repeated engine/context families, split low/high registers, and fields that recur across CP/CPC interrupt control and status registers.
- Validate that `gc_12_0_0_offset.h` and `gc_12_0_0_sh_mask.h` are from the same generated source version. Offset/mask mismatches are especially dangerous for `GCVM_INVALIDATE_ENGn_*`, `GCVM_CONTEXTn_*`, `CP_RB0_*`, and interrupt registers.
- Exercise VM map/unmap, BO eviction, VM fault, GPU reset, and multi-VMID workloads on GC v12 hardware. Healthy signals include completed TLB invalidations, no stale-mapping faults after unmap/remap, correct fault attribution, and no invalidation timeouts.
- Check invalidation-engine programming through debug traces or register dumps: engine address ranges should match the intended broad or targeted invalidation range, and ACK bitmaps should correspond to requested VMIDs.
- Run graphics-ring initialization and command submission tests. Expected signals include correct ring pointer writeback, advancing write/read pointers, completed fences, no unexpected command processor hangs, and stable operation across suspend/resume or reset.
- Exercise IRQ enable/disable paths for timestamp, generic, idle, busy/empty, privileged-register, privileged-instruction, and opcode-error interrupts. Regressions show up as missed fences/events, unexpected IRQ floods, or lost fault reports.
- Run KFD compute queue tests with timestamp and opcode-error handling enabled. Signals include correct queue error reporting, no unexpected CPC interrupt masking, and stable queue teardown/recreation.
- Run performance-counter collection for GCVML2/GCMC/GCUTCL2 blocks and verify event selection, clear behavior, result low/high pairing, and client/source selection against known workloads.
- Test IOMMU/GPUVA translation-assist and translation-fault paths where supported. Expected behavior includes correct fault status, no unauthorized bypass, and correct behavior under host-memory translation modes.
- Exercise CP/CPC suspend, resume, preemption, and VMID reset paths. Useful signals include successful context save/restore, sane `CP_VMID_STATUS` values, no stuck preempt status, and no corrupted context-save buffers.
- Inspect GPU hang/debug dumps for plausible `CP_GFX_ERROR`, `CP_FATAL_ERROR`, `CP_DEBUG*`, `CP_CPF_DEBUG`, `CP_CPC_DEBUG`, UTCL1 error, PASID, VMID, and ECC/EDC values.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002573`. It covers lines 10045-12529 of `gc_12_0_0_sh_mask.h`. The previous chunk contains the opening `GCVM_CONTEXTS_DISABLE` tail plus complete `GCVM_INVALIDATE_ENG0_SEM`, `ENG1_SEM`, and most of `ENG2_SEM`. The next chunk begins with the `CP_DDID_CNTL__*` fields that are introduced by the final comment in this chunk. The final per-file research should merge those adjacent pieces with this chunk to present a complete GC 12.0.0 field-mask map.
