# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 12373-14858

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header slice. It contains only C preprocessor `#define` constants for register bit positions and masks. There are no functions, structs, enums, global variables, allocations, locks, direct MMIO operations, or executable branches in this range.

The requested lines contain 2,158 `#define` statements: 1,079 `__SHIFT` macros and 1,079 `_MASK` macros. The range starts in the middle of `CP_ECC_FIRSTOCCURRENCE`, continues through command-processor and compute/graphics queue register fields, crosses into SPI scheduling/debug fields, then into CP HQD queue fields, TCP watchpoint fields, and GDS VMID/GWS/OA resource fields. It ends inside `GDS_OA_VMID3`, before the rest of the per-VMID OA masks and later GDS reset fields.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_11_5_0_sh_mask.h` describes the bit layout of GC 11.5.0 registers. Driver code pairs these field macros with register offsets from `gc_11_5_0_offset.h` and uses AMDGPU helper macros to compose and decode 32-bit hardware register values without open-coded bit numbers.

This chunk covers five main surfaces:

- Command processor reliability, interrupt, queue scheduling, suspend/resume, DDID, graphics HQD, DMA watchpoint, timestamp, UTCL1 status, soft reset, and security-domain controls in the `gc_cppdec` area.
- SPI arbitration, work-conserving launch percentages, per-VMID shader debug/trap controls, compute queue reset, and compute wavefront context-save controls in the `gc_spipdec` area.
- Compute HQD/MQD state in the `gc_cpphqddec` area, including MQD/HQD base addresses, VMID/VQID, queue priorities, quantum, PQ/IB/EOP rings, doorbells, timers, dequeue/offload/semaphore/atomic controls, scheduler/status registers, context-save sizing, GDS resource state, error reporting, AQL control, and DDID counters.
- TCP watchpoint programming in the `gc_tcpdec` area, with four watch address/control slots and VMID/mode/valid fields.
- GDS per-VMID partitioning in the `gc_gdspdec` area, covering `GDS_VMID0..15_BASE`, `GDS_VMID0..15_SIZE`, `GDS_GWS_VMID0..15`, and the beginning of `GDS_OA_VMID0..3`.

## Important APIs, Types, And Macros

The only interface in this chunk is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's in-register bit mask.
- `//<REGISTER>` comments mark generated register boundaries.
- `// addressBlock: ...` comments mark transitions between generated address blocks.

There are no callable APIs or C types here. Consumers normally use these constants through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `WREG32_FIELD15`.

Important command-processor families in this chunk include:

- Reliability and debug fields: the tail of `CP_ECC_FIRSTOCCURRENCE`, obsolete ring first-occurrence registers, `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, and `CP_CPC_DEBUG`.
- Queue write-pointer polling: `CP_PQ_WPTR_POLL_CNTL` and `CP_PQ_WPTR_POLL_CNTL1`, including poll period, one-shot behavior, active status, enable bit, and queue mask.
- Repeated ME pipe interrupt controls and statuses: `CP_ME1_PIPE0..3_INT_CNTL`, `CP_ME2_PIPE0..3_INT_CNTL`, `CP_ME1_PIPE0..3_INT_STATUS`, and `CP_ME2_PIPE0..3_INT_STATUS`. These share fields for compare-query status, dequeue request, CP ECC, SUA violation, GPF, WRM poll timeout, privileged register, opcode error, timestamp, reserved-bit error, and generic interrupt sources.
- Scheduling and context controls: `CP_GFX_QUEUE_INDEX`, per-ME pipe priority counters and priorities, program-counter and interrupt-routine start registers for PFP/ME/MEC, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_IQ_WAIT_TIME1..3`, `CP_RB0_BASE_HI`, `CP_RB1_BASE_HI`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, and `CP_VMID_STATUS`.
- CPC interrupt and suspend fields: `CPC_INT_CNTL`, `CPC_INT_STATUS`, `CPC_INT_CNTX_ID`, `CPC_SUSPEND_CTX_SAVE_*`, `CPC_SUSPEND_CNTL_STACK_*`, `CPC_SUSPEND_WG_STATE_OFFSET`, `CPC_OS_PIPES`, `CP_SUSPEND_RESUME_REQ`, and `CP_SUSPEND_CNTL`.
- DDID and graphics HQD state: `CPC_DDID_*`, `CP_DDID_*`, `CP_GFX_DDID_*`, `CP_GFX_HPD_*`, `CP_GFX_MQD_*`, `CP_GFX_HQD_*`, `CP_RB_WPTR_POLL_ADDR_*`, and `CP_RB_DOORBELL_CONTROL`.
- CP DMA/watch and misc diagnostics: `CP_DMA_WATCH0..3_*`, `CP_DMA_WATCH_STAT*`, `CP_PFP_JT_STAT`, `CP_MEC_JT_STAT`, busy hysteresis registers, `CP_RB_DOORBELL_CLEAR`, ring active/status registers, RCIU CAM data, GPU timestamp offset, SDMA completion/request fields, `CPF_GCR_CNTL`, `CPG_UTCL1_STATUS`, `CPC_UTCL1_STATUS`, `CPF_UTCL1_STATUS`, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, and `CP_CPC_GFX_CNTL`.

Important SPI families include:

- `SPI_ARB_PRIORITY` and `SPI_ARB_CYCLES_0/1`, which define time-slice ordering and duration fields.
- `SPI_WCL_PIPE_PERCENT_GFX`, `SPI_WCL_PIPE_PERCENT_HP3D`, and `SPI_WCL_PIPE_PERCENT_CS0..7`, which provide launch/work allocation percentage fields for graphics, HP3D, and compute pipes.
- `SPI_USER_ACCUM_VMID_CNTL`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_COMPUTE_QUEUE_RESET`, and `SPI_COMPUTE_WF_CTX_SAVE`, which drive per-VMID accumulation, shader debug/trap mode, compute queue reset, and wavefront context-save initiation/status.

Important compute HQD/MQD families include:

- Queue identity and lifecycle: `CP_MQD_BASE_ADDR*`, `CP_HQD_ACTIVE`, `CP_HQD_VMID`, `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PIPE_PRIORITY`, `CP_HQD_QUEUE_PRIORITY`, `CP_HQD_QUANTUM`, `CP_MQD_CONTROL`, and dequeue status/request registers.
- Packet queue and doorbell state: `CP_HQD_PQ_BASE*`, `CP_HQD_PQ_RPTR`, read-pointer report addresses, write-pointer poll addresses, `CP_HQD_PQ_DOORBELL_CONTROL`, `CP_HQD_PQ_CONTROL`, and `CP_HQD_PQ_WPTR_LO/HI`.
- Indirect buffer, instruction queue, and offload/semaphore controls: `CP_HQD_IB_*`, `CP_HQD_IQ_TIMER`, `CP_HQD_IQ_RPTR`, `CP_HQD_DMA_OFFLOAD`, `CP_HQD_OFFLOAD`, `CP_HQD_SEMA_CMD`, `CP_HQD_MSG_TYPE`, and atomic pre-operation registers.
- Scheduler, status, EOP, and save/restore state: `CP_HQD_HQ_SCHEDULER0/1`, `CP_HQD_HQ_STATUS0/1`, `CP_HQD_HQ_CONTROL0/1`, `CP_HQD_EOP_*`, `CP_HQD_CTX_SAVE_*`, `CP_HQD_CNTL_STACK_*`, `CP_HQD_WG_STATE_OFFSET`, suspend stack/workgroup offsets, and `CP_HQD_CTX_SAVE_SIZE`.
- GDS and error fields: `CP_HQD_GDS_RESOURCE_STATE`, `CP_HQD_ERROR`, `CP_HQD_AQL_CONTROL`, and `CP_HQD_DDID_*`.

Important watchpoint and GDS families include:

- `TCP_WATCH0..3_ADDR_H`, `TCP_WATCH0..3_ADDR_L`, and `TCP_WATCH0..3_CNTL`, which encode address, mask, VMID, mode, and valid bits for TCP-level watchpoints.
- `GDS_VMID0..15_BASE` and `GDS_VMID0..15_SIZE`, which partition GDS address space per VMID.
- `GDS_GWS_VMID0..15`, which partition global wave sync resources per VMID.
- `GDS_OA_VMID0..3`, which begin the per-VMID ordered-append resource mask series continued in the next chunk.

## Control Flow

This header has no runtime control flow. It affects runtime behavior only when C code expands these macros while composing or decoding register values.

The typical implied flow is:

1. Driver code selects a GC 11.5.0 register offset from the companion offset header.
2. It reads, writes, or read-modify-writes a 32-bit register through AMDGPU SOC15 MMIO helpers.
3. It uses a `__SHIFT` and `_MASK` pair, often through `REG_SET_FIELD` or `REG_GET_FIELD`, to isolate the intended field.
4. GPU hardware command-processor, SPI, HQD, TCP, GDS, VM, interrupt, trap, reset, or context-save state machines execute the real operation.

For CP/CPC/ME interrupt handling, higher-level code enables specific interrupt sources, reads corresponding status registers, attributes the event to a pipe/queue/VMID/context/PASID when supported, and clears or masks the source using register-specific semantics. This header defines field locations only; it does not specify clear-on-read, write-one-to-clear, self-clearing, or ordering rules.

For HQD/MQD queue setup, runtime code programs MQD bases, VMID/VQID, queue priority/quantum, packet queue base and size, read/write-pointer report and poll addresses, doorbell offset and enable, IB/EOP rings, context-save memory, and control bits before activating a queue. Dequeue, suspend, preemption, EOP, DDID, and relaunch-related fields are interpreted by firmware and hardware queue schedulers.

For SPI debug, KFD/debug paths program `SPI_GDBG_PER_VMID_CNTL` to enable traps, exception masks, launch modes, and trap-on-start/end behavior for a target VMID. For GDS and TCP watchpoints, runtime code writes per-VMID resource slices or watch slots; the actual access checks occur in hardware.

## State And Persistence Behavior

The macros are stateless compile-time constants. Persistent and volatile state exists only in GPU registers, firmware-managed queue objects, ring buffers, doorbell pages, writeback memory, context-save memory, debug/watchpoint state, and GDS resource allocation.

Hardware state described by the CP/CPC portion includes interrupt enables and latched statuses, ECC/EDC first-fault metadata, queue polling configuration, priority and wait timers, VMID reset/preempt state, suspend context-save addresses and sizes, DDID buffers/counters, HPD/HQD/MQD queue state, ring doorbell controls, DMA watchpoints, timestamp offsets, UTCL1 status bits, security-domain enables, and soft-reset controls. Some fields are configuration, some are live status, some are hardware-updated pointers/counters, and some are command bits with side effects.

Hardware state described by the SPI portion includes arbitration timing, launch/work allocation percentages, per-VMID trap and exception behavior, compute queue reset request state, and wavefront context-save busy/done state.

Hardware state described by the HQD portion includes active/busy state, queue VMID/VQID, priority and quantum, persistent state flags, PQ/IB/EOP ring bases and pointers, doorbell state, scheduler/status words, context-save layout, GDS resource ownership, AQL control, DDID counters, and dequeue/suspend state. These values normally persist until queue teardown, preemption, suspend/resume, reset, firmware reinitialization, or explicit reprogramming.

Hardware state described by the TCP/GDS portion includes watchpoint address/mask/VMID/mode/valid configuration and per-VMID GDS/GWS/OA resource partitions. GDS partition state is process/VMID-visible and must be reset or reallocated carefully when VMIDs are reused.

Reserved or unused fields appear in many registers. Consumers should preserve them during read-modify-write unless the hardware sequence explicitly requires a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` supplies matching register offsets.
- This tree does not contain a `gc_11_5_0_default.h`; GC 11.5.0 users that need reset values must use local defaults or other generation-specific sources.
- AMDGPU helper macros in the surrounding DRM code provide the bitfield operations and MMIO access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c` directly includes this shift/mask header and its offset header. Within the examined direct consumer, the visible use of this chunk is `CP_DEBUG__CPG_UTCL1_ERROR_HALT_DISABLE` during gfxhub initialization; many other fields in this chunk are part of the same generated ABI for queue, SPI, TCP, and GDS code paths.
- Shared field names are also used by other GC 11-era files such as `gfx_v11_0.c`, `mes_v11_0.c`, and `amdgpu_amdkfd_gfx_v11.c` against their selected offset/header mappings. Those files are useful behavioral references, but they do not directly include the GC 11.5.0 header pair in this tree.

Runtime integration points include VM/gfxhub setup, command-processor interrupt handling, KFD compute queue and MES/HQD programming, graphics queue setup, shader debug/trap control, suspend/resume and preemption, queue reset/relaunch, doorbell submission, ring writeback, DDID tracking, TCP watchpoint debugging, GDS/GWS/OA allocation, ECC/EDC reporting, and GPU reset/hang diagnosis.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong shift or mask can compile cleanly while setting, clearing, or decoding the wrong hardware bit.
- This work item starts and ends inside register groups. The previous chunk owns the beginning of `CP_ECC_FIRSTOCCURRENCE`; this chunk begins at `CP_ECC_FIRSTOCCURRENCE__VMID_MASK`. The next chunk continues `GDS_OA_VMID3` and the remaining GDS OA/reset definitions.
- Repeated register families are easy to update inconsistently. ME1/ME2 pipe interrupt controls/statuses, `CP_DMA_WATCH0..3`, `TCP_WATCH0..3`, `GDS_VMID0..15`, `GDS_GWS_VMID0..15`, and GDS OA per-VMID masks should be mechanically compared for intended symmetry.
- CP/HQD queue fields are liveness-critical. Incorrect queue size, block size, read/write pointer, doorbell, cache policy, VMID/VQID, EXE-disable, privilege, or KMD queue fields can cause lost submissions, stuck fences, bad queue ownership, or hangs.
- Interrupt and status fields can be latched, masked, clear-sensitive, or hardware-updated. Using a status mask as an enable mask, or vice versa, can hide faults or create interrupt storms.
- Suspend, context-save, preemption, and dequeue fields interact with firmware-owned state. Wrong offsets, sizes, policy bits, or request/status decoding can resume queues with corrupt state or fail to quiesce active work.
- `SPI_GDBG_PER_VMID_CNTL` is debugger- and trap-sensitive. Bad exception masks, trap-on-start/end bits, launch modes, or stale VMID selection can trap the wrong process or miss debug events.
- TCP watchpoint and CP DMA watchpoint fields are address-alignment sensitive. Low-address bits are reserved or omitted, so consumers must supply aligned addresses and correct masks.
- GDS/GWS/OA fields are resource-partitioning and isolation-sensitive. VMID reuse, partial reset, or incorrect base/size/mask programming can leak or deny resources across processes.
- Security-domain, soft-reset, and UTCL1 status/error fields should not be treated as ordinary data fields. Full-register writes can reset active domains, drop diagnostics, or change fault handling.
- There is no access-type metadata in this header. It does not tell consumers whether a field is read-only, write-only, write-one-to-clear, sticky, self-clearing, privileged, or firmware-owned.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include GC 11.5.0 support. Missing, renamed, or malformed macros should surface as compile failures in `gfxhub_v11_5_0.c` or code that adopts this generated header.
- Mechanically compare every `__SHIFT` and `_MASK` in this chunk against AMD's authoritative GC 11.5.0 register database.
- Cross-check that every register group in this chunk has a matching offset entry in `gc_11_5_0_offset.h`.
- Run mask/shift consistency checks: masks should align with shifts, full-width fields should be `0xFFFFFFFFL`, high address fields should use the expected reduced width, and repeated ME/HQD/watchpoint/GDS families should differ only where the hardware definition says so.
- Boot affected hardware and validate gfxhub initialization, especially the `CP_DEBUG` halt-disable bit used by `gfxhub_v11_5_0.c`, VM fault handling, TLB invalidation, and reset paths.
- Exercise compute and graphics queue creation/destruction, MES/HQD programming, packet queue doorbells, read/write pointer polling and writeback, EOP handling, IB execution, dequeue/preemption/suspend/resume, and queue reset/relaunch.
- Exercise KFD debugger paths that program `SPI_GDBG_PER_VMID_CNTL`, including trap enable, exception masks, trap-on-start/end, and wave launch mode.
- Exercise TCP and CP DMA watchpoints with aligned and boundary addresses, VMID-specific and any-VMID modes, read/write watches, and status reporting.
- Exercise GDS/GWS/OA allocation and release across multiple VMIDs, VMID reuse, GPU reset, and process teardown.
- Check runtime diagnostics: DRM/KFD logs, CP/CPC/ME pipe interrupt status, `CP_HQD_ERROR`, UTCL1 fault/retry/PRT status, ECC/EDC first occurrence fields, DDID counters, HQD dequeue/status fields, and GDS resource state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002554`. The final per-file research should merge this with neighboring chunks for full `gc_11_5_0_sh_mask.h` coverage. The previous chunk contains the start of `CP_ECC_FIRSTOCCURRENCE`; the next chunk completes `GDS_OA_VMID3` and continues the remaining GDS OA and reset/resource definitions.
