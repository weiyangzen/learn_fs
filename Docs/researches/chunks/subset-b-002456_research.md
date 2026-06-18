# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 17384-19837

## Purpose

This chunk is a generated AMD GFX 10.1.0 shift/mask header slice. It contains C preprocessor constants that describe bit positions and masks for graphics/compute command processor and shader processor interface registers. It has no executable code, data structures, or runtime side effects by itself; its purpose is to let AMDGPU code compose, update, and decode hardware register values without open-coded bit numbers.

The requested range contains 2,163 `#define` statements across 289 generated register names: 1,083 `__SHIFT` macros and 1,080 `_MASK` macros. It starts inside the compute user-data register block at `COMPUTE_USER_DATA_0__DATA__SHIFT` and continues through compute dispatch sentinel registers, the `gc_cppdec` command-processor address block, and the beginning of the `gc_spipdec` shader-processor-interface block. It ends inside the `SPI_RESOURCE_RESERVE_CU_5` group, after the `SGPR` mask, with the remaining `LDS`, `WAVES`, and `BARRIERS` masks for that register in the next chunk.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, locks, allocations, direct MMIO operations, or exported symbols in this range. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field in the register value.
- `//<REGISTER>` comments: generated register boundaries.
- `// addressBlock: gc_cppdec` and `// addressBlock: gc_spipdec`: generated address-block boundaries that align these field macros with companion offset/default headers for the same GFX IP generation.

Major macro families in this chunk include:

- Compute dispatch/user payload registers: `COMPUTE_USER_DATA_0` through `COMPUTE_USER_DATA_15`, `COMPUTE_DISPATCH_TUNNEL`, `COMPUTE_DISPATCH_END`, and `COMPUTE_NOWHERE`. The user-data registers expose full 32-bit `DATA` fields; dispatch tunnel/end/nowhere fields support compute dispatch packet and sentinel behavior.
- Command processor core controls and telemetry: `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, `CP_VIRT_STATUS`, `CP_DEVICE_ID`, `CP_PROCESS_QUANTUM`, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, and `CP_CPC_GFX_CNTL`.
- CP/CPC interrupt and error surfaces: `CPC_INT_INFO`, `CPC_INT_ADDR`, `CPC_INT_PASID`, `CP_GFX_ERROR`, `CP_FATAL_ERROR`, `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING0..2`, `CP_INT_STATUS_RING0..2`, `CPC_INT_CNTL`, `CPC_INT_STATUS`, `CPC_INT_CNTX_ID`, `CP_ME1_PIPE*_INT_CNTL`, `CP_ME1_PIPE*_INT_STATUS`, `CP_ME2_PIPE*_INT_CNTL`, `CP_ME2_PIPE*_INT_STATUS`, `CP_ME1_INT_STAT_DEBUG`, `CP_ME2_INT_STAT_DEBUG`, and `CP_MEC1/2_F32_INT_DIS`.
- UTCL1 translation/cache controls and error/status reporting: `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, `CPF_UTCL1_CNTL`, `CPG_UTCL1_ERROR`, `CPC_UTCL1_ERROR`, `CPG_UTCL1_STATUS`, `CPC_UTCL1_STATUS`, and `CPF_UTCL1_STATUS`. These expose XNACK redo timers, invalidate/bypass/drop/force-snoop controls, VMID reset mode, no-PTE behavior, force-no-execute, request credits, permission-fault flags, miss-bypass counters, active flags, and TLB-miss status.
- Ring-buffer and queue plumbing: `CP_RB0_BASE`, `CP_RB_BASE`, `CP_RB1_BASE`, `CP_RB2_BASE`, corresponding high-address registers, `CP_RB0_CNTL`, `CP_RB_CNTL`, `CP_RB1_CNTL`, `CP_RB2_CNTL`, read/write pointers, read-pointer writeback addresses, buffer-size masks, `CP_RB_VMID`, `CP_RB_DOORBELL_RANGE_*`, `CP_MEC_DOORBELL_RANGE_*`, `CP_RB_DOORBELL_CONTROL`, `CP_RB_DOORBELL_CLEAR`, `CP_RB*_ACTIVE`, and `CP_RB_STATUS`.
- Pipe, ME, ring, and priority scheduling definitions: `CP_ME0/1/2_PIPE_PRIORITY_CNTS`, `CP_RING_PRIORITY_CNTS`, `CP_ME0_PIPE0..2_PRIORITY`, `CP_ME1_PIPE0..3_PRIORITY`, `CP_ME2_PIPE0..3_PRIORITY`, `CP_RING0..2_PRIORITY`, and `CP_GFX_QUEUE_INDEX`.
- Program counter and interrupt routine start registers: `CP_CE_PRGRM_CNTR_START`, `CP_PFP_PRGRM_CNTR_START`, `CP_ME_PRGRM_CNTR_START`, `CP_MEC1_PRGRM_CNTR_START`, `CP_MEC2_PRGRM_CNTR_START`, plus matching `*_INTR_ROUTINE_START` registers.
- Suspend/resume, preemption, context-save, and DDID plumbing: `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, `CPC_SUSPEND_CTX_SAVE_BASE_ADDR_*`, `CPC_SUSPEND_CTX_SAVE_CONTROL`, suspend stack/workgroup offsets and sizes, `CPC_OS_PIPES`, `CP_SUSPEND_RESUME_REQ`, `CP_SUSPEND_CNTL`, `CPC_DDID_BASE_ADDR_*`, `CP_DDID_BASE_ADDR_*`, `CPC_DDID_CNTL`, `CP_DDID_CNTL`, and `CP_GFX_DDID_*` counters/pointers.
- GFX HQD/MQD queue state: `CP_GFX_MQD_BASE_ADDR*`, `CP_GFX_HQD_ACTIVE`, `CP_GFX_HQD_VMID`, `CP_GFX_HQD_QUEUE_PRIORITY`, `CP_GFX_HQD_QUANTUM`, `CP_GFX_HQD_BASE*`, `CP_GFX_HQD_RPTR*`, `CP_GFX_HQD_WPTR*`, `CP_GFX_HQD_DEQUEUE_REQUEST`, `CP_GFX_HQD_MAPPED`, `CP_GFX_HQD_QUE_MGR_CONTROL`, `CP_GFX_HQD_HQ_STATUS0`, `CP_GFX_HQD_HQ_CONTROL0`, `CP_GFX_MQD_CONTROL`, `CP_HQD_GFX_CONTROL`, `CP_HQD_GFX_STATUS`, and the corresponding CE queue registers under `CP_GFX_HQD_CE_*`.
- Debug, watchpoint, and trace-style definitions: `CP_DMA_WATCH0..3_ADDR_*`, `CP_DMA_WATCH0..3_MASK`, `CP_DMA_WATCH0..3_CNTL`, `CP_DMA_WATCH_STAT*`, `CP_PFP_JT_STAT`, `CP_CE_JT_STAT`, `CP_MEC_JT_STAT`, `CPG_RCIU_CAM_*`, `CPF_GCR_CNTL`, `CP_GFX_INDEX_MUTEX`, and `CC_GC_EDC_CONFIG`.
- Shader processor interface controls: `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0/1`, `SPI_WCL_PIPE_PERCENT_GFX`, `SPI_WCL_PIPE_PERCENT_HP3D`, `SPI_WCL_PIPE_PERCENT_CS0..7`, `SPI_GDBG_WAVE_CNTL`, `SPI_GDBG_TRAP_CONFIG`, `SPI_GDBG_TRAP_MASK`, `SPI_GDBG_WAVE_CNTL2`, `SPI_GDBG_WAVE_CNTL3`, `SPI_GDBG_TRAP_DATA0/1`, `SPI_COMPUTE_QUEUE_RESET`, and `SPI_RESOURCE_RESERVE_CU_0..5`.

Common field names encode the intended hardware semantics: `RB_BASE`, `RB_RPTR`, `RB_WPTR`, `RB_BUFSZ`, `RB_BLKSZ`, `DOORBELL`, `VMID`, `PASID`, `QUEUE`, `PIPE`, `ME`, `MEC`, `HQD`, `MQD`, `ACTIVE`, `MAPPED`, `DEQUEUE`, `QUANTUM`, `PRIORITY`, `INTERRUPT`, `TIME_STAMP`, `PRIV_REG`, `BAD_OPCODE`, `ECC`, `EDC`, `UTCL1`, `XNACK`, `BYPASS`, `INVALIDATE`, `PERMISSION_FAULT`, `SUSPEND`, `RESUME`, `PREEMPT`, `DDID`, `HPD`, `OSPRE_FENCE`, `WATCH`, `SOFT_RESET`, `ARB`, `WCL`, `TRAP`, `STALL`, `VGPR`, `SGPR`, `LDS`, `WAVES`, and `BARRIERS`.

## Control Flow

This header has no direct control flow. It influences driver behavior only when included by AMDGPU source that expands these constants while building register values. Typical use is:

1. Consumer code selects a GFX 10.1.0 register offset from the matching generated offset header.
2. The consumer clears, inserts, tests, or extracts a bitfield using a `*_MASK` and `*__SHIFT` pair from this header.
3. AMDGPU register helpers perform the read/modify/write, direct write, polling loop, debug dump, or interrupt/status decode.
4. Hardware command-processor, queue, translation, interrupt, and shader-interface state machines perform the actual work.

The sequencing implied by the field names is outside this file. Examples include programming ring-buffer base/control/read-pointer writeback before enabling a queue; setting doorbell ranges and doorbell controls before user or kernel queues submit work; decoding CP/CPC interrupts after an interrupt handler reads status; clearing or masking interrupt sources in ring or pipe-specific registers; saving/restoring context state around suspend, preemption, or reset; and reserving SPI compute-unit resources before waves are admitted.

## State And Persistence Behavior

The macros are stateless compile-time constants. They describe hardware state but do not store it. Actual state lives in GFX command-processor and SPI registers, queue descriptors, memory-backed ring buffers, doorbell pages, writeback buffers, and hardware/firmware state machines.

Hardware-visible state described by this chunk includes:

- Compute user SGPR/user-data payload values and dispatch tunnel/end sentinel fields.
- CP ring-buffer bases, buffer/block sizes, read/write pointers, read-pointer writeback addresses, VMID association, buffer swap/cache/volatile/no-update controls, active/status bits, and queue execution bits.
- Doorbell aperture ranges, queue doorbell enable/source/offset bits, and doorbell clear controls.
- Interrupt masks, status bits, and error-reporting fields for CP, CPC, per-ring sources, ME1/ME2 pipe sources, bad opcodes, protected-mode faults, privilege faults, timestamp events, cache-flush events, VM faults, and ECC/EDC conditions.
- UTCL1 translation/cache controls, fault indicators, miss bypass counters, request credit state, TLB miss state, invalidation controls, and no-execute/no-PTE behavior.
- CP power, memory sleep, clock-gating/sleep-delay, soft-reset, and shader-dispatch control bits.
- Queue manager state for GFX HQDs and CE HQDs: MQD base, active/mapped state, VMID, priority, quantum, ring base and pointer fields, dequeue requests, queue manager controls, HQ status/control, and CE mirror queue state.
- Suspend/resume and preemption state, including VMID reset/preempt/status bits, suspend context-save addresses, stack/workgroup offsets and sizes, OS pipe selection, and resume request/control fields.
- DDID queue/counter state, high-priority dispatch status/control/fence fields, and OSPRE fence addresses/data.
- Debug/watch state for DMA watchpoints, watch status, jump table status, RCIU CAM access, GCR controls, and index mutex ownership.
- SPI arbitration, workload pipe-percent controls, graphics debug wave stall/trap controls, compute queue reset, and resource reservations per CU for VGPR, SGPR, LDS, waves, and barriers.

Persistence is determined by the hardware block, reset domain, power state, and firmware/driver ownership. Some registers are ordinary configuration state, some are read-only status, some are write-one-to-clear interrupt bits, some are self-clearing commands, some point to memory that persists across queues, and some are reset by GPU reset, command-processor reset, suspend/resume, power gating, or queue teardown. This header does not provide reset defaults, access permissions, legal enumerations, polling timeouts, or ordering rules; those come from hardware documentation, firmware contracts, and AMDGPU implementation code.

## Dependencies And Integration Points

This generated header must stay synchronized with the same GFX 10.1.0 register database as:

- `drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which provides the register offsets that pair with these field definitions.
- `drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h`, which provides reset/default values for many registers.
- Neighboring GC/GFX generation headers such as `gc_9_0_*`, `gc_10_3_0_*`, `gc_11_0_0_*`, and later `gc_12_*` headers. Their register families are similar but not layout-identical.
- AMDGPU GFX, KFD, queue, interrupt, reset, suspend/resume, VM fault, debug, and register-dump code that token-pastes or directly references register, field, shift, and mask names.
- CP firmware and microcode expectations for HQD/MQD layout, CP program counter and interrupt routine starts, suspend/context-save areas, doorbell behavior, and preemption/DDID paths.
- Hardware interrupt and fault plumbing that reports CP/CPC/UTCL1/ECC/EDC errors through DRM/KFD interrupt handlers and diagnostic paths.
- SPI scheduling/debug paths that control wave trapping/stalling, compute queue reset, arbitration, workload distribution, and per-CU resource reservation.

The range crosses two generated address blocks. The first part completes compute user-data and dispatch definitions from the previous address block; the middle and largest part is `gc_cppdec` for CP/CPC/CPG/CPF command-processor registers; the tail begins `gc_spipdec` for SPI arbitration, debug, queue reset, and CU resource reservation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while silently programming or decoding the wrong hardware bit.
- The file is generated. Manual edits risk divergence from AMD's register source, companion offset/default headers, firmware assumptions, and existing GFX generation comparisons.
- The requested first line is inside the `COMPUTE_USER_DATA_0` group after its register comment. The previous chunk is needed for the complete start-of-register context.
- The requested last line is inside `SPI_RESOURCE_RESERVE_CU_5`; the `LDS`, `WAVES`, and `BARRIERS` masks for that register are outside this work item.
- Many register families are repeated with small differences: `CP_RB0_CNTL` versus `CP_RB_CNTL` versus `CP_RB1_CNTL`/`CP_RB2_CNTL`, global interrupt controls versus ring-specific controls, ME1 versus ME2 pipe interrupt definitions, HQD versus CE HQD fields, and `CPG`/`CPC`/`CPF` UTCL1 controls. Copying a field across a similar register can be wrong even when names look interchangeable.
- Ring-buffer and doorbell fields are sequencing-sensitive. Bad masks can cause lost submissions, write-pointer/read-pointer drift, writeback corruption, queues that never become active, or queues that cannot be unmapped.
- Interrupt/status/clear/mask fields can be edge-sensitive or write-one-to-clear in consumer code. Incorrect decoding can cause missed GPU faults, interrupt storms, stale status, false hang attribution, or failure to clear fatal error sources.
- VMID, PASID, bypass-PASID, app-VMID, permission-fault, no-execute, no-PTE, and UTCL1 fields are security and isolation sensitive. A bitfield mismatch can misattribute faults or break address-space isolation.
- Suspend/resume, preemption, context save, and DDID fields are stateful across queue lifecycle transitions. Misprogramming can leave queues suspended, lose context state, corrupt resumed queues, or wedge command processor firmware.
- Power, memory sleep, clock gating, soft reset, and shader-dispatch control fields may interact with in-flight queues. Consumers must preserve reserved bits and follow hardware sequencing.
- SPI debug and trap controls intentionally stall or redirect waves. Incorrect masks can hang graphics/compute work, trap the wrong VMID/queue, or make debug features affect normal workloads.
- SPI resource reservation fields influence occupancy. Wrong field widths can reserve too much or too little VGPR/SGPR/LDS/wave/barrier capacity and create performance loss or scheduling failures that only appear under specific shader mixes.

## Test Signals

Useful validation signals for this generated header and its consumers include:

- Build AMDGPU configurations that include GFX 10.1.0 support. Missing or renamed macros should surface as compile failures in register programming tables, GFX code, KFD queue code, interrupt paths, or debug code.
- Mechanically compare this range against the authoritative GFX 10.1.0 register database, checking that each field has the expected shift, mask, and register width.
- Cross-check register names against `gc_10_1_0_offset.h` and default values against `gc_10_1_0_default.h`, especially for CP ring, interrupt, UTCL1, HQD/MQD, doorbell, suspend/resume, and SPI resource registers.
- Diff repeated families against adjacent GFX generations to catch generator drift while allowing intentional layout changes, particularly in `CP_RB*_CNTL`, `CP_INT_*`, `CP_ME*_PIPE*_INT_*`, `CP_GFX_HQD_*`, `CP_GFX_HQD_CE_*`, `CPG/CPC/CPF_UTCL1_*`, and `SPI_GDBG_*`.
- Boot and run graphics/compute workloads on affected hardware with ring submission, doorbell writes, VM faults, queue creation/destruction, KFD workloads, and graphics queues enabled.
- Exercise suspend/resume, GPU reset, CP soft reset, queue preemption, queue eviction/restore, process teardown, VMID reset, and repeated workload start/stop cycles.
- Monitor DRM/KFD logs, interrupt counters, ring read/write pointers, fence progress, VM fault reporting, ECC/EDC reporting, CP fatal error status, and UTCL1 permission/miss status.
- Decode known-good register dumps using these masks and compare against reference tools or hardware documentation for CP ring state, interrupt masks/status, HQD/MQD state, doorbells, suspend/DDID state, debug watchpoints, and SPI trap/resource controls.
- Run shader-debug/trap and compute-queue-reset scenarios carefully, confirming that trap selection by ME/pipe/queue/VMID and wave-stall controls affect only the intended queues and recover cleanly.

## Cross-Chunk Notes

The previous chunk owns the register comment for `COMPUTE_USER_DATA_0` and likely earlier compute register definitions. This chunk starts at that register's `DATA` shift/mask pair, covers `COMPUTE_USER_DATA_1..15`, and then moves into the `gc_cppdec` command-processor address block.

This chunk stops partway through `SPI_RESOURCE_RESERVE_CU_5`. The next chunk should continue that CU resource-reservation group before covering later SPI resource or debug definitions.
