# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 14896-17371

## Scope

This chunk is a generated AMD GC 10.3.0 shift/mask register-header slice. It contains only C preprocessor `#define` constants for register bit positions and masks. There are no functions, structs, enums, global variables, allocations, locks, direct MMIO operations, or executable branches in this range.

The requested lines contain 2,151 `#define` statements: 1,076 `__SHIFT` macros and 1,075 `_MASK` macros. The range starts in the middle of the `SPI_SHADER_USER_DATA_VS_30` group, covers shader-stage programming for VS/GS/ES/HS/LS, compute dispatch and compute resource registers, then enters the `gc_cppdec` command-processor address block. It ends in the middle of `CP_SUSPEND_RESUME_REQ`, after the `SUSPEND_REQ` mask and before the `RESUME_REQ` mask in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_10_3_0_sh_mask.h` describes the bit layout of registers for AMD graphics core 10.3.0. Driver code pairs these field macros with register offsets from `gc_10_3_0_offset.h` and uses AMDGPU helper macros to build, update, and decode 32-bit hardware register values without open-coded bit numbers.

This chunk covers three major surfaces:

- Shader processor interface state for graphics pipeline shader stages. It defines user-data payload registers, shader program base registers, shader program resource fields, request allocation controls, shader checksums, and per-stage user accumulator fields for VS, GS, ESGS, HS, LSHS, and LS related paths.
- Compute dispatch state. It defines compute dispatch initiation bits, dispatch dimensions and starts, per-axis full/partial thread counts, program and packet addresses, scratch-base addresses, compute program resources, VMID, CU destination masks, static thread management per shader engine, temp-ring sizing, restart coordinates, thread tracing, request controls, dispatch IDs, wave restore/relaunch fields, and compute user-data payloads.
- Command processor and CPC state in the `gc_cppdec` address block. It defines ring-buffer bases and controls, read/write pointer fields, doorbell ranges, queue/pipe priorities, interrupt controls and statuses, UTCL1 controls and errors, graphics error surfaces, fatal/ECC/EDC status, CP power and memory sleep controls, VMID reset/preempt/status fields, and early suspend/context-save controls.

## Important APIs, Types, And Macros

The only interface in this chunk is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's in-register bit mask.
- `//<REGISTER>` comments mark generated register boundaries.
- `// addressBlock: gc_cppdec` marks the transition into command processor/CPC register definitions.

There are no callable APIs or C types here. Consumers typically use these constants through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and queue/debug/power-management code that token-pastes register and field names.

Important shader-stage families in this chunk include:

- `SPI_SHADER_USER_DATA_VS_30` and `SPI_SHADER_USER_DATA_VS_31`, followed by `SPI_SHADER_USER_DATA_GS_0..31` and `SPI_SHADER_USER_DATA_HS_0..31`. These expose full 32-bit `DATA` payload fields used as user SGPR inputs to shader stages.
- `SPI_SHADER_REQ_CTRL_VS`, `SPI_SHADER_REQ_CTRL_ESGS`, and `SPI_SHADER_REQ_CTRL_LSHS`. These share allocation-control fields such as `SOFT_GROUPING_EN`, `NUMBER_OF_REQUESTS_PER_CU`, allocation timeout, hard-lock threshold/hysteresis, producer request lockout, global scanning enable, and allocation-rate throttling threshold.
- `SPI_SHADER_USER_ACCUM_VS_0..3`, `SPI_SHADER_USER_ACCUM_ESGS_0..3`, and `SPI_SHADER_USER_ACCUM_LSHS_0..3`. Each exposes a small `CONTRIBUTION` field for accumulated user-data contribution accounting.
- `SPI_SHADER_PGM_LO_*` and `SPI_SHADER_PGM_HI_*` registers for ES_GS, GS, LS_HS, HS, ES, and LS program base addresses. Low halves are full-width; high halves in this chunk use low 8-bit `MEM_BASE` fields.
- `SPI_SHADER_PGM_RSRC1_GS` and `SPI_SHADER_PGM_RSRC1_HS`. These define shader resource metadata including `VGPRS`, `SGPRS`, `PRIORITY`, `FLOAT_MODE`, privilege, DX10 clamp, IEEE mode, CU grouping, memory ordering, forward progress, WGP mode, stage-specific VGPR component count, and FP16 overflow behavior.
- `SPI_SHADER_PGM_RSRC2_GS_VS`, `SPI_SHADER_PGM_RSRC2_GS`, and `SPI_SHADER_PGM_RSRC2_HS`. These cover scratch enable, user SGPR count, trap presence, exception enables, LDS sizing, VGPR component count, off-chip LDS, user SGPR MSB/skip behavior, and shared VGPR count.
- `SPI_SHADER_PGM_RSRC3_GS`, `SPI_SHADER_PGM_RSRC3_HS`, `SPI_SHADER_PGM_RSRC4_GS`, and `SPI_SHADER_PGM_RSRC4_HS`. These define CU enable masks, wave limits, lock thresholds, group FIFO depth, and late allocation fields.
- `SPI_SHADER_PGM_CHKSUM_GS` and `SPI_SHADER_PGM_CHKSUM_HS` expose full-width shader checksum fields.

Important compute families include:

- `COMPUTE_DISPATCH_INITIATOR` with dispatch enable and mode bits including partial thread-group enable, ordered append controls, thread-dimension usage, ordering mode, scalar/vector L1 invalidation, tunnel enable, restore, and wave32 enable (`CS_W32_EN`).
- `COMPUTE_DIM_X/Y/Z`, `COMPUTE_START_X/Y/Z`, `COMPUTE_RESTART_X/Y/Z`, `COMPUTE_DISPATCH_ID`, and `COMPUTE_THREADGROUP_ID`, all full-width coordinate or identity fields.
- `COMPUTE_NUM_THREAD_X/Y/Z`, each splitting full and partial thread counts into low and high 16-bit halves.
- `COMPUTE_PGM_LO/HI`, `COMPUTE_DISPATCH_PKT_ADDR_LO/HI`, and `COMPUTE_DISPATCH_SCRATCH_BASE_LO/HI`, which describe shader, packet, and scratch address fields.
- `COMPUTE_PGM_RSRC1`, `COMPUTE_PGM_RSRC2`, and `COMPUTE_PGM_RSRC3`, which define compute shader VGPR/SGPR allocation, priority, float mode, privilege, clamp/IEEE flags, bulky and FP16 behavior, WGP mode, memory ordering, forward progress, scratch, trap, TGID/TG-size enables, thread ID component count, LDS size, exception enables, and shared VGPR count.
- `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_DESTINATION_EN_SE0..3`, and `COMPUTE_STATIC_THREAD_MGMT_SE0..3`, which gate work distribution across shader engines, shader arrays, CUs, waves, and thread groups.
- `COMPUTE_TMPRING_SIZE`, `COMPUTE_REQ_CTRL`, `COMPUTE_USER_ACCUM_0..3`, `COMPUTE_DDID_INDEX`, `COMPUTE_SHADER_CHKSUM`, `COMPUTE_RELAUNCH`, `COMPUTE_RELAUNCH2`, `COMPUTE_WAVE_RESTORE_ADDR_LO/HI`, `COMPUTE_USER_DATA_0..15`, `COMPUTE_DISPATCH_TUNNEL`, `COMPUTE_DISPATCH_END`, and `COMPUTE_NOWHERE`.

Important command-processor families include:

- CP/CPC timing and virtualization: `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, `CP_VIRT_STATUS`, `CP_DEVICE_ID`, `CP_PROCESS_QUANTUM`, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, and instruction-queue wait timers `CP_IQ_WAIT_TIME1/2`.
- Interrupt metadata and error reporting: `CPC_INT_INFO`, `CPC_INT_ADDR`, `CPC_INT_PASID`, `CP_GFX_ERROR`, `CP_FATAL_ERROR`, `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING0..2`, `CP_INT_STATUS_RING0..2`, `CPC_INT_CNTL`, `CPC_INT_STATUS`, `CPC_INT_CNTX_ID`, and F32 interrupt sources/disables for ME, PFP, CE, MEC1, and MEC2.
- UTCL1 translation/cache controls and errors: `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, `CPF_UTCL1_CNTL`, `CPG_UTCL1_ERROR`, and `CPC_UTCL1_ERROR`. These include XNACK redo timers, VMID reset mode, drop/invalidate/fragment-limit modes, force snoop, MTYPE no-PTE mode, force no-execute, permission-fault and TLB-miss flags.
- Ring-buffer and doorbell state: `CP_RB0_BASE`, `CP_RB_BASE`, `CP_RB1_BASE`, `CP_RB2_BASE`, their high-base registers, `CP_RB0_CNTL`, `CP_RB_CNTL`, `CP_RB1_CNTL`, `CP_RB2_CNTL`, `CP_RB_RPTR_WR`, read-pointer writeback addresses, `CP_RB*_BUFSZ_MASK`, `CP_RB*_WPTR`, `CP_RB*_WPTR_HI`, `CP_RB_VMID`, `CP_RB_DOORBELL_RANGE_*`, `CP_MEC_DOORBELL_RANGE_*`, and `CP_PQ_STATUS`.
- Scheduling and priority state: `CP_ME0/ME1/ME2_PIPE_PRIORITY_CNTS`, `CP_RING_PRIORITY_CNTS`, per-pipe priorities for ME0/ME1/ME2, ring priorities, `CP_GFX_QUEUE_INDEX`, and program-counter/interrupt-routine start registers for CE, PFP, ME, MEC1, and MEC2.
- Reliability and power state: `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_ECC_FIRSTOCCURRENCE`, obsolete ring-specific first occurrence registers, `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, `CP_PQ_WPTR_POLL_CNTL`, and `CP_PQ_WPTR_POLL_CNTL1`.
- VM, preemption, and suspend surfaces: `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, `CPC_SUSPEND_CTX_SAVE_BASE_ADDR_LO/HI`, `CPC_SUSPEND_CTX_SAVE_CONTROL`, suspend stack/workgroup offsets and sizes, `CPC_SUSPEND_CTX_SAVE_SIZE`, `CPC_OS_PIPES`, and the start of `CP_SUSPEND_RESUME_REQ`.

## Control Flow

This header has no runtime control flow. It affects runtime behavior only when C code expands these macros while composing or decoding register values.

The typical implied flow is:

1. Driver code selects a GC 10.3.0 register offset from the companion offset header.
2. It reads, writes, or read-modify-writes a register through AMDGPU MMIO/SOC15 helpers.
3. It uses the `__SHIFT` and `_MASK` pair, often via `REG_SET_FIELD` or `REG_GET_FIELD`, to isolate the intended field.
4. Hardware command processor, shader processor interface, compute dispatch, ring-buffer, VM, interrupt, or power-management state machines execute the real operation.

For shader and compute dispatch programming, higher-level AMDGPU/KFD paths program shader program bases, resource registers, user-data registers, scratch/temporary-ring controls, VMID association, and dispatch initiator bits in a required hardware order. This chunk only provides the field layout; it does not define queue setup order, cache invalidation order, wave launch ordering, or trap/relaunch sequencing.

For CP/CPC rings, higher-level code programs ring-buffer bases and sizes, read-pointer writeback addresses, write pointers, VMIDs, doorbell apertures, and control bits before queue execution. Interrupt handlers and fault paths then read CP/CPC status, error, PASID, address, VMID, and ring-specific interrupt fields to attribute and clear events. The header does not specify clear-on-read, write-one-to-clear, polling, or reset timing semantics.

## State And Persistence Behavior

The macros are stateless compile-time constants. Persistent and volatile state exists only in GPU hardware registers, firmware-managed queue state, ring buffers, doorbell pages, and memory-backed save/restore areas.

Hardware state described by the shader and compute portions includes shader program addresses, shader resource allocation, user SGPR/user-data payloads, trap/exception enable bits, LDS and scratch requirements, CU and shader-engine targeting masks, compute dimensions, dispatch IDs, relaunch payloads, wave restore addresses, and thread tracing/performance counter enables. These values normally persist until queue teardown, shader stage reprogramming, graphics or compute pipeline state change, GPU reset, power-gating loss, suspend/resume reinitialization, or firmware intervention.

Hardware state described by the CP/CPC portions includes ring-buffer base addresses, read/write pointer fields, writeback addresses, queue VMID assignment, doorbell ranges and status, interrupt masks and latched statuses, UTCL1 control/error state, ECC/EDC first occurrence fields, power and memory sleep configuration, VMID reset/preempt status, and suspend context-save addresses and sizes. Some are ordinary configuration registers; some are live status bits; some are hardware-updated counters or first-fault latches; some are self-clearing command bits; and some may be clear-on-write or write-one-to-clear depending on the register. This generated shift/mask header does not encode access permissions or side-effect classes.

Reserved fields appear in several registers. Consumers must preserve reserved bits during read-modify-write unless hardware documentation or existing driver sequences say otherwise.

## Dependencies And Integration Points

This chunk depends on the generated GC 10.3.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h` supplies matching offsets for the register names in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_default.h` supplies reset/default values for related registers where generated defaults exist.
- AMDGPU helper macros provide the actual bitfield operations and MMIO access.
- GC 10.3.0 consumers in this tree include `amdgpu/amdgpu_amdkfd_gfx_v10_3.c`, `amdgpu/gfxhub_v2_1.c`, `amdgpu/sdma_v5_2.c`, `amdgpu/amdgpu_sdma.c`, and `pm/swsmu/smu11/vangogh_ppt.c`, which include this shift/mask header directly or alongside the matching offset header.
- Similar register families exist in neighboring generation headers such as GC 10.1.0, GC 9.x, GC 11.x, and GC 12.x. Names are intentionally familiar, but layouts are not guaranteed to be identical.

The runtime integration points are broad: graphics shader-stage programming, compute queue setup, KFD process/queue dispatch, ring submission, doorbell programming, VM fault attribution, CP interrupt handling, GPU reset and hang diagnosis, power/clock/memory sleep configuration, ECC/EDC reporting, preemption, suspend/resume, and context save/restore.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong shift or mask can compile successfully while programming the wrong hardware bit.
- This work item starts and ends inside register groups. The first visible line belongs to `SPI_SHADER_USER_DATA_VS_30`, whose register comment and possibly earlier paired context are in the previous chunk. The last visible register, `CP_SUSPEND_RESUME_REQ`, is incomplete until the next chunk provides `RESUME_REQ_MASK`.
- Many families are repeated with small differences. `SPI_SHADER_PGM_RSRC2_GS_VS`, `SPI_SHADER_PGM_RSRC2_GS`, `SPI_SHADER_PGM_RSRC2_HS`, and `COMPUTE_PGM_RSRC2` look similar but encode different stage-specific fields. CP ring controls likewise differ between `CP_RB0_CNTL`, `CP_RB_CNTL`, `CP_RB1_CNTL`, and `CP_RB2_CNTL`.
- Full-width `DATA`, address, ID, and mask registers are easy to treat as interchangeable, but their consumers have different ordering, alignment, VMID, and firmware-ownership rules.
- Shader program resource fields control occupancy, scratch, LDS, exception, trap, WGP mode, forward-progress, and memory-order behavior. Bad field widths or stale generation assumptions can cause shader launch failures, hangs, trap misbehavior, or performance regressions.
- Compute dispatch fields are sequencing-sensitive. Misprogramming dispatch dimensions, thread counts, scratch base, relaunch payloads, or restore addresses can corrupt queue execution or make hangs hard to attribute.
- Ring-buffer and doorbell fields are queue-liveness critical. Incorrect size, block size, pointer, writeback, cache policy, VMID, or doorbell range masks can lead to lost submissions, stuck fences, pointer drift, or command processor faults.
- CP/CPC interrupt/status fields can be latched, masked, or clear-sensitive. Wrong masks can miss GPU faults, fail to clear an interrupt, create interrupt storms, or report errors against the wrong ring, pipe, queue, VMID, or PASID.
- UTCL1 and VM/PASID fields are isolation-sensitive. Mis-decoding or misprogramming fault, no-PTE, no-execute, bypass-PASID, or VMID-reset bits can hide real address-space faults or break process attribution.
- Power, memory sleep, and clock halt fields can interact with active queues. Consumers must follow established enable/disable sequencing and avoid full-register writes that trample reserved bits.
- Suspend, resume, preempt, and context-save fields are cross-boundary state. Offsets and sizes must match firmware/hardware expectations or queues can resume with corrupted or incomplete state.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU/KFD configurations that include GC 10.3.0 support. Missing, renamed, or malformed macros should surface as compile failures in queue, VM, interrupt, SDMA/GFXHUB, or power-management code.
- Mechanically compare every `__SHIFT` and `_MASK` in this chunk against AMD's authoritative GC 10.3.0 register database.
- Cross-check that each register group has matching offset entries in `gc_10_3_0_offset.h` and, where applicable, reset/default entries in `gc_10_3_0_default.h`.
- Run mask/shift consistency checks: masks should align with shifts, full-width `DATA` fields should be `0xFFFFFFFFL`, high address fields should use the expected reduced width, and repeated CP interrupt/pipe families should differ only where the hardware definition says so.
- Boot affected hardware and run graphics plus compute workloads that exercise shader program resource programming, compute dispatch dimensions, user SGPR/user-data payloads, scratch/LDS usage, wave32 mode, traps, relaunch/restore, and thread tracing.
- Exercise KFD queue creation/destruction, process VM faults, doorbell submissions, ring write-pointer updates, read-pointer writeback, fence progress, and multi-ring interrupt handling.
- Exercise GPU reset, suspend/resume, queue preemption, VMID reset, context save/restore, power gating, and memory sleep transitions while checking for stuck rings or corrupted queue state.
- Check runtime diagnostics: DRM/KFD logs, CP fatal error and `CP_GFX_ERROR`, UTCL1 permission/TLB errors, ECC/EDC first occurrence fields, ring-specific interrupt status, MEC F32 interrupt/disables, VMID preempt status, and suspend context-save status.
- Decode known-good register dumps with these masks and compare against reference tooling or hardware documentation, especially for shader resource fields, compute dispatch state, CP ring controls, doorbells, interrupt attribution, PASID/VMID fields, and suspend/preempt state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002482`. The final per-file research should merge this with neighboring chunks for full `gc_10_3_0_sh_mask.h` coverage. In particular, the previous chunk owns the beginning of `SPI_SHADER_USER_DATA_VS_30`, and the next chunk completes `CP_SUSPEND_RESUME_REQ` before continuing later CP/DDID/HQD and subsequent register families.
