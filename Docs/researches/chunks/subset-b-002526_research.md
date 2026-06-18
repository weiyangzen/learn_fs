# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 1-2557

## Scope

This chunk is the opening segment of the generated AMD GC 11.0.3 shift/mask header. It contains the copyright/license block, include guard `_gc_11_0_3_SH_MASK_HEADER`, and the beginning of the `gc_sdma0_sdma0dec` address block. The range is entirely C preprocessor metadata: `#define` constants named `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

The chunk covers SDMA0 global/control/status fields from `SDMA0_DEC_START` through `SDMA0_FED_STATUS`, then the per-queue SDMA0 RLC register families for queues 0 through 6, and the beginning of queue 7. The assigned range ends at `SDMA0_QUEUE7_RB_AQL_CNTL__AQL_ENABLE__SHIFT`; the remaining queue 7 AQL, minor pointer, preempt, and mid-command definitions continue after this chunk.

## Purpose

`gc_11_0_3_sh_mask.h` is generated hardware metadata for AMDGPU's GC 11.0.3 ASIC register map. This header does not implement SDMA behavior; it gives driver code stable field positions and bit masks for programming or decoding SDMA0 registers through the matching GC 11.0.3 offset header.

Within this chunk, the purpose is SDMA0 register field interpretation:

- global SDMA0 control bits for traps, interrupts, preemption, protected/TMZ mid-command handling, page-fault notifications, data/fence swapping, and restore behavior;
- SDMA0 status and health fields for idle/full/stall conditions, command state, clock gating, FED state, ECC/EDC counters, XNACK fault metadata, GPU IOV violations, AQL status, and queue reset state;
- UTCL1 page translation/cache-control fields for response mode, redo delay, writeback mode, page options, fault address/vector/status capture, invalidation, and XNACK read/write reporting;
- memory layout and address-translation support fields such as GB address config, tiling config, hash selection, physical address capture, hole address capture, and TLBI/GCR credit controls;
- repeated queue register layouts for SDMA0 queues 0-7, including ring buffer control, ring/IB base addresses and pointers, doorbell programming, context status, schedule quantum, preemption, write-pointer polling, AQL settings, and mid-command save/restore data.

## Important APIs, Types, And Macros

There are no functions, structs, enums, typedefs, storage objects, or inline helpers in this chunk. The exported interface is the generated macro namespace.

The core macro convention is:

- `<REG>__<FIELD>__SHIFT`: the least-significant bit position of a hardware field.
- `<REG>__<FIELD>_MASK`: the field mask in the 32-bit register value.
- Matching register address macros are expected from `gc_11_0_3_offset.h`, commonly named `reg<REG>`.
- Consumers combine these macros with AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask tests, `RREG32`, `WREG32`, and `SOC15_REG_OFFSET`.

Notable SDMA0 global groups in this chunk:

- `SDMA0_CNTL`: trap enable, semaphore-wait interrupt, data/fence swap, mid-command and TMZ mid-command preemption, page retry/null/fault interrupts, CP MES interrupt, world-switch, restore, context-empty, frozen, IB-preempt, and RB-preempt interrupt bits.
- `SDMA0_CHICKEN_BITS` and `SDMA0_CHICKEN_BITS_2`: tuning and workaround fields for stalls, burst sizes, 256-byte combine behavior, raw checks, copy overlap, F32 command delay, ucode buffer behavior, watermarks, clock-gating overrides, and PIO VFID source.
- `SDMA0_STATUS_REG`, `SDMA0_STATUS1_REG`, `SDMA0_STATUS2_REG`, `SDMA0_STATUS3_REG`, `SDMA0_STATUS4_REG`, `SDMA0_STATUS5_REG`, `SDMA0_STATUS6_REG`, and `SDMA0_FED_STATUS`: status decode fields for idle/full/empty/stall state, command operation state, exception/TLBI/GCR/invalidation idleness, outstanding requests, polling activity, fatal error detection, and per-queue busy/selected state.
- `SDMA0_UTCL1_CNTL`, `SDMA0_UTCL1_WATERMK`, `SDMA0_UTCL1_TIMEOUT`, `SDMA0_UTCL1_PAGE`, `SDMA0_UTCL1_RD_STATUS`, `SDMA0_UTCL1_WR_STATUS`, `SDMA0_UTCL1_INV0`, `SDMA0_UTCL1_INV1`, `SDMA0_UTCL1_INV2`, and `SDMA0_UTCL1_*_XNACK*`: translation-cache, fault, invalidation, queueing, and XNACK field definitions used around SDMA memory translation and retry handling.
- `SDMA0_RELAX_ORDERING_LUT`: relaxed-ordering policy bits for copy, write, fence, poll-memory, conditional execute, atomic, const-fill, PTE/PDE, timestamp, world-switch, read-pointer writeback, write-pointer polling, IB fetch, and RB fetch operations.
- `SDMA0_QUEUE_STATUS0` and `SDMA0_QUEUE_RESET_REQ`: packed four-bit queue status/reset request fields for queues 0-7.
- `SDMA0_GPU_IOV_VIOLATION_LOG` and `SDMA0_GPU_IOV_VIOLATION_LOG2`: violation status, multiple-violation, address, write-operation, VF/VFID, and initiator-id decode fields for virtualization/I/O violation reporting.
- `SDMA0_RLC_CGCG_CTRL`, `SDMA0_CLOCK_GATING_STATUS`, and `SDMA0_POWER_CNTL`: clock/power gating controls and status fields.

Notable per-queue families in this chunk:

- `SDMA0_QUEUE<N>_RB_CNTL` for queues 0-7: ring buffer enable, size, write-pointer polling, swap controls, F32 write-pointer polling, read-pointer writeback, writeback timer, privilege, and VMID fields.
- `SDMA0_QUEUE<N>_RB_BASE`, `_RB_BASE_HI`, `_RB_RPTR`, `_RB_RPTR_HI`, `_RB_WPTR`, `_RB_WPTR_HI`, `_RB_RPTR_ADDR_HI`, `_RB_RPTR_ADDR_LO`: queue ring base, read/write pointer, and read-pointer writeback address fields.
- `SDMA0_QUEUE<N>_IB_CNTL`, `_IB_RPTR`, `_IB_OFFSET`, `_IB_BASE_LO`, `_IB_BASE_HI`, `_IB_SIZE`, `_IB_SUB_REMAIN`: indirect-buffer enable, swap, VMID, privilege, base, size, pointer, and remaining-size fields.
- `SDMA0_QUEUE<N>_CONTEXT_STATUS`: selected, idle, expired, exception, context-switchable, preempt-disable, read-pointer writeback idle, write-pointer update pending, and update-failure-count fields.
- `SDMA0_QUEUE<N>_DOORBELL`, `_DOORBELL_LOG`, `_DOORBELL_OFFSET`: doorbell enable/capture, logged data/error, and aligned doorbell offset fields.
- `SDMA0_QUEUE<N>_CSA_ADDR_LO`, `_CSA_ADDR_HI`, and `_SCHEDULE_CNTL`: context-save-area address fields and global/process/local/context-quantum scheduling fields.
- `SDMA0_QUEUE<N>_PREEMPT`, `_RB_PREEMPT`, `_MINOR_PTR_UPDATE`: IB/RB preemption and minor pointer update controls.
- `SDMA0_QUEUE<N>_RB_AQL_CNTL`: AQL enable, packet size, packet step, mid-command preemption, data restore, and overlap bits. This chunk includes the complete queue 0-6 AQL masks but only the first queue 7 AQL shift line.
- `SDMA0_QUEUE<N>_MIDCMD_DATA0` through `_MIDCMD_DATA10` and `_MIDCMD_CNTL`: mid-command state payload and control fields for data validity, copy mode, split state, and preempt allowance.

Queue 0 has a `USE_IB` field in `SDMA0_QUEUE0_CONTEXT_STATUS`; queues 1-7 in this chunk have the otherwise similar context-status layout without that field. Consumers should use generated field names rather than assuming all queue context words are bit-identical.

## Control Flow

This header has no runtime control flow. Inclusion only makes preprocessor constants available to C translation units.

The implied consumer flow is:

1. Include `gc_11_0_3_offset.h` and `gc_11_0_3_sh_mask.h` for the active GC 11.0.3 hardware path.
2. Compute a register address using a `regSDMA0_*` offset macro plus SOC15 base selection or a per-engine/per-queue offset.
3. Read, write, or read-modify-write the register with AMDGPU register access helpers.
4. Use the shift/mask macros either through `REG_SET_FIELD`/`REG_GET_FIELD` or through direct bit masking.

The KFD SDMA queue load/unload path illustrates how queue fields in this chunk drive real sequencing. `amdgpu_amdkfd_gfx_v11.c` computes an SDMA RLC queue offset, clears `SDMA0_QUEUE0_RB_CNTL__RB_ENABLE_MASK`, polls `SDMA0_QUEUE0_CONTEXT_STATUS__IDLE_MASK`, programs doorbell offset/enable, writes RB read/write pointers and base addresses, toggles `SDMA0_QUEUE0_MINOR_PTR_UPDATE`, and then sets `RB_ENABLE`. The dump path iterates contiguous queue register ranges from `regSDMA0_QUEUE0_RB_CNTL` through mid-command control.

The MQD update path in `kfd_mqd_manager_v11.c` composes `sdmax_rlcx_rb_cntl` with `SDMA0_QUEUE0_RB_CNTL__RB_SIZE__SHIFT`, `RB_VMID__SHIFT`, `RPTR_WRITEBACK_ENABLE__SHIFT`, `RPTR_WRITEBACK_TIMER__SHIFT`, and `F32_WPTR_POLL_ENABLE__SHIFT`; it also encodes doorbell offset and schedule quantum with the corresponding queue 0 macros. Hardware queue instances use queue 0 field names with an offset computed from the selected SDMA engine and queue.

## State And Persistence

The header itself stores no software state and has no persistence behavior. It allocates no memory, performs no I/O, and cannot change hardware.

The state described by the macros is hardware-resident SDMA0 state:

- global control registers persist across ordinary CPU execution until changed by driver, firmware, reset, suspend/resume, or runtime power-management flows;
- queue RB/IB base, pointer, doorbell, schedule, AQL, and context-status registers are the live hardware queue state used by AMDGPU and KFD to submit and manage SDMA work;
- UTCL1/XNACK/fault registers expose transient memory-translation and retry state;
- status, EDC/ECC, GPU IOV, FED, clock-gating, and watchdog fields are diagnostic or policy state used during initialization, error handling, and hang/debug paths.

Because these definitions describe a hardware ABI, persistence concerns are mostly about keeping generated masks synchronized with the actual ASIC register layout and with saved MQD fields. A wrong shift or mask can cause software to persist a malformed queue control word, restore a queue with a bad VMID or address bit alignment, miss a fault/status bit, or poll the wrong idle field.

## Dependencies And Integration Points

This chunk belongs to the generated GC 11.0.3 register-description set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` supplies the matching `regSDMA0_*` register offsets used with these masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_default.h` supplies matching reset/default values for the same ASIC register namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c` includes this header with the GC 11.0.3 offset header and uses generated RLC/FED fields for GC/SDMA fatal-error interrupt handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c` includes this header and uses GC 11.0.3 register names/masks in IMU/RLC RAM golden programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c` uses the SDMA queue register offsets and masks from this register family to load, dump, stop, and inspect KFD SDMA queues.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c` uses queue 0 shift/mask definitions to build the SDMA MQD words later programmed into the selected engine/queue instance.
- SDMA version code such as `sdma_v6_0.c` and adjacent GC 11 files use the same macro style for UTCL1 status, control programming, interrupt/trap setup, and diagnostics, even when the exact include path is selected by ASIC generation.

The integration contract is compile-time but hardware-critical: the offset header chooses the register word, this mask header chooses the field location inside that word, and runtime code assumes both come from the same generated hardware database and ASIC revision.

## Risks And Edge Cases

- Generated-header drift is the main risk. If `gc_11_0_3_sh_mask.h`, `gc_11_0_3_offset.h`, and any default/header consumers are regenerated from different hardware descriptions, code can compile while programming the wrong bits.
- Queue register blocks are repetitive but not perfectly safe to infer manually. Queue 0 has a `USE_IB` context-status bit that the later queues in this chunk do not expose. The chunk boundary also splits queue 7's AQL field list after the first shift definition.
- Address fields have alignment-implied low bits: several low address fields start at bit 2, IB base low starts at bit 5, and doorbell offsets start at bit 2. A consumer that shifts unaligned CPU/GPU addresses incorrectly can silently drop low bits or write invalid queue state.
- Full-width `0xFFFFFFFFL` masks are common for pointer, data, and timestamp registers. Callers must handle 64-bit values by programming paired low/high registers in the documented order; the macros only define the 32-bit pieces.
- Several fields are packed multi-bit status or policy fields rather than booleans, including burst/watermark fields, exception fields, queue status nibbles, command operation status, VMID fields, schedule quantum, and GPUVM invalidation fields. Treating every mask as a single flag would corrupt decode or programming logic.
- Fault and retry fields such as XNACK fault address/vector/status, page retry/null/fault interrupt enables, and UTCL1 invalidation fields affect error handling. Incorrect masks can hide page-fault causes or trigger wrong recovery paths.
- Virtualization and RAS integration depends on exact decode of GPU IOV and FED status fields. A wrong field name or bit position can send poison/error handling to the wrong block or miss an SR-IOV violation.
- The header has no local validation and no semantic comments beyond register names. Many names encode hardware behavior that must be interpreted together with the hardware specification and the matching driver code.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are build, generation, and hardware-integration checks:

- Build AMDGPU with GC 11.0.3 paths enabled so include sites in `gfx_v11_0_3.c`, `imu_v11_0_3.c`, KFD, and SDMA queue code resolve all generated field names.
- Compile-time failures from `REG_SET_FIELD`, `REG_GET_FIELD`, or direct mask uses are the first signal of renamed or missing generated macros.
- Header-regeneration checks should compare this file against the authoritative ASIC register database and verify that offsets, masks, defaults, and queue register ordering stay synchronized.
- KFD SDMA queue tests should create, load, preempt/stop, dump, and destroy SDMA queues, exercising `RB_CNTL`, doorbell, pointer, context-status, schedule, and mid-command fields.
- Suspend/resume and GPU reset tests should verify that SDMA queues and global SDMA control state can be restored without stale pointer, VMID, doorbell, or preemption state.
- SDMA memory fault and retry scenarios should validate UTCL1/XNACK status capture, page-fault interrupt enables, and recovery logs.
- RAS/FED interrupt testing on GC 11.0.3 hardware should validate `RLC_RLCS_FED_STATUS` decode paths that classify SDMA versus GFX fatal-error events.
- SR-IOV or VF test coverage should verify GPU IOV violation logging fields and poison/error handling behavior when virtualization is active.
