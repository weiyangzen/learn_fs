# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 17259-19693

## Purpose

This chunk is generated AMD GC 11.0.3 register bitfield metadata. It contains no executable C code; it exports `#define` constants for hardware register field shifts and masks. AMDGPU, AMDKFD, MES, IMU, and GFXHUB code combine these constants with matching register offsets from `gc_11_0_3_offset.h` and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` to program and decode command processor, shader processor input, and compute HQD state.

The range starts in the `gc_cpdec` command processor decode block, crosses into `gc_spipdec`, and ends inside the beginning of the `gc_cpphqddec` compute HQD decode block. It covers graphics and compute command rings, CP interrupt enables/status, ME/MEC interrupt families, debug and power/EDC controls, VMID/preemption/suspend/DDID state, graphics HQD state, DMA watch registers, SPI scheduling knobs, and the first compute HQD queue/MQD fields. Although this repository path is under `ceph-client`, this file is GPU driver hardware metadata, not filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or direct MMIO operations in this chunk. The public API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for the same field.
- Consumers pair these macros with `mm*` or `reg*` offset macros from `gc_11_0_3_offset.h`; the masks do not identify register addresses by themselves.

Major register groups in this chunk:

- CP ring control and pointers: `CP_RB{0,1}_CNTL`, `CP_RB_CNTL`, `CP_RB*_BASE`, `CP_RB*_BASE_HI`, `CP_RB*_WPTR`, `CP_RB*_WPTR_HI`, `CP_RB*_RPTR_ADDR`, `CP_RB*_RPTR_ADDR_HI`, `CP_RB_RPTR_WR`, and buffer-size mask registers. These fields describe ring size, block size, secure TMZ state/match, cache policy, kernel queue marking, read/write pointer addresses, and read-pointer writeback control.
- Doorbell and VMID routing: `CP_RB_VMID`, `CP_ME0_PIPE*_VMID`, `CP_RB_DOORBELL_RANGE_*`, `CP_MEC_DOORBELL_RANGE_*`, `CP_RB_DOORBELL_CONTROL`, `CP_RB_DOORBELL_CLEAR`, and `CP_PQ_STATUS` define VMID ownership, doorbell offset ranges, doorbell enable/update/hit state, and host write-pointer notification behavior.
- Interrupt controls and status: top-level `CP_INT_CNTL`/`CP_INT_STATUS`, per-ring `CP_INT_CNTL_RING{0,1}`/`CP_INT_STATUS_RING{0,1}`, `CPC_INT_CNTL`/`CPC_INT_STATUS`, per-ME/per-pipe `CP_ME{1,2}_PIPE{0..3}_INT_CNTL` and matching status/debug registers, plus `CP_ME_F32_INTERRUPT`, `CP_PFP_F32_INTERRUPT`, `CP_MEC{1,2}_F32_INTERRUPT`, and `CP_MEC{1,2}_F32_INT_DIS`. Fields cover timestamp, opcode, privileged register/instruction, reserved-bit, ECC/EDC, GPF, dequeue, queue-message, IQ timer, wave-restore, and SUA violation signaling.
- CP debug, power, and fault state: `CP_FATAL_ERROR`, `CP_GFX_ERROR` context from the prior boundary, `CP_PWR_CNTL`, `CP_ECC_FIRSTOCCURRENCE*`, `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, `CP_DEBUG`, `CP_CPF_DEBUG`, `CP_CPC_DEBUG`, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, and `CP_CPC_GFX_CNTL`. These expose clock/power gating overrides, data-poisoning interrupt suppression, debug bus control, privilege-write inhibition, soft reset, and fatal/first-error indications.
- Scheduler, priority, and microcode entry points: ME/ring priority count and priority registers, `CP_PROCESS_QUANTUM`, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_MAX_DRAW_COUNT`, `CP_PFP/ME/MEC*_PRGRM_CNTR_START{,_HI}`, and `CP_PFP/ME/MEC*_INTR_ROUTINE_START{,_HI}`.
- Queue polling and wait timers: `CP_PQ_WPTR_POLL_CNTL`, `CP_PQ_WPTR_POLL_CNTL1`, and `CP_IQ_WAIT_TIME{1,2,3}` define polling periods, active/enable state, queue masks, and retry/wait buckets for IB offload, atomic offload, WRM offload, GWS, queue sleep, wave scheduling, semaphore rearm, dequeue retry, and suspend queue handling.
- VMID, preemption, suspend, and CWSR support: `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, `CPC_SUSPEND_CTX_SAVE_*`, `CPC_SUSPEND_CNTL_STACK_*`, `CPC_SUSPEND_WG_STATE_OFFSET`, `CPC_SUSPEND_CTX_SAVE_SIZE`, `CPC_OS_PIPES`, `CP_SUSPEND_RESUME_REQ`, and `CP_SUSPEND_CNTL`.
- DDID and HPD blocks: `CPC_DDID_*`, `CP_DDID_*`, `CP_GFX_DDID_*`, and `CP_GFX_HPD_*` provide base addresses, thresholds, size/policy/mode/enable fields, inflight/wptr/rptr/delta counters, high-priority dispatch status/control, and OSPRE fence address/data fields.
- Graphics HQD and MQD state: `CP_GFX_MQD_BASE_ADDR{,_HI}`, `CP_GFX_HQD_ACTIVE`, `CP_GFX_HQD_VMID`, `CP_GFX_HQD_QUEUE_PRIORITY`, `CP_GFX_HQD_QUANTUM`, `CP_GFX_HQD_BASE{,_HI}`, `CP_GFX_HQD_RPTR`, `CP_GFX_HQD_RPTR_ADDR{,_HI}`, `CP_RB_WPTR_POLL_ADDR_*`, `CP_GFX_HQD_CNTL`, `CP_GFX_HQD_DEQUEUE_REQUEST`, `CP_GFX_HQD_MAPPED`, `CP_GFX_HQD_QUE_MGR_CONTROL`, `CP_GFX_HQD_IQ_TIMER`, `CP_GFX_HQD_HQ_STATUS0`, `CP_GFX_HQD_HQ_CONTROL0`, `CP_GFX_MQD_CONTROL`, `CP_HQD_GFX_CONTROL`, and `CP_HQD_GFX_STATUS`.
- DMA watch and status: four `CP_DMA_WATCH{0..3}_ADDR_LO/HI/MASK/CNTL` register groups plus `CP_DMA_WATCH_STAT_ADDR_*` and `CP_DMA_WATCH_STAT` for tagged memory watchpoints, VMID/ATC filters, read/write flags, selected watchpoint ID, and counter/stat address reporting.
- UTCL1 and GCR controls/status: `CPG_UTCL1_ERROR`, `CPC_UTCL1_ERROR`, `CPG_UTCL1_STATUS`, `CPC_UTCL1_STATUS`, `CPF_UTCL1_STATUS`, and `CPF_GCR_CNTL` expose CP-side translation/cache error and bypass/status fields.
- SPI decode registers: `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0`, `SPI_ARB_CYCLES_1`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_USER_ACCUM_VMID_CNTL`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_COMPUTE_QUEUE_RESET`, and `SPI_COMPUTE_WF_CTX_SAVE` define graphics/compute/exp pipeline arbitration, percentage weights, per-VMID debug/accumulation controls, compute queue reset, and wavefront context-save controls.
- Compute HQD decode registers: `CP_HPD_UTCL1_*`, `CP_MQD_BASE_ADDR{,_HI}`, `CP_HQD_ACTIVE`, `CP_HQD_VMID`, `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PIPE_PRIORITY`, `CP_HQD_QUEUE_PRIORITY`, `CP_HQD_QUANTUM`, `CP_HQD_PQ_BASE{,_HI}`, `CP_HQD_PQ_RPTR`, `CP_HQD_PQ_RPTR_REPORT_ADDR{,_HI}`, `CP_HQD_PQ_WPTR_POLL_ADDR{,_HI}`, `CP_HQD_PQ_DOORBELL_CONTROL`, `CP_HQD_PQ_CONTROL`, `CP_HQD_IB_BASE_ADDR{,_HI}`, `CP_HQD_IB_RPTR`, `CP_HQD_IB_CONTROL`, and the beginning of `CP_HQD_IQ_TIMER`.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by code that includes the generated headers:

1. A GC 11.0.3 path includes `gc/gc_11_0_3_offset.h` and `gc/gc_11_0_3_sh_mask.h`.
2. The caller selects a register address through an `mm*` or `reg*` offset macro, often through `SOC15_REG_OFFSET` or an XCC-aware instance selector.
3. The caller composes or decodes a `u32` register value with `REG_SET_FIELD`, `REG_GET_FIELD`, direct shifts, or direct mask tests using these macros.
4. AMDGPU, AMDKFD, or MES register helpers perform the ordered MMIO writes/reads while the relevant queue, ring, interrupt, reset, or power-management path owns sequencing.

Observed consumers in this tree include GC 11.0.3-specific files such as `amdgpu/gfx_v11_0_3.c`, `amdgpu/imu_v11_0_3.c`, and `amdgpu/gfxhub_v3_0_3.c`. Closely related GC 11 paths show the intended patterns: `gfx_v11_0.c` uses `CP_INT_CNTL*` and `CP_ME*_PIPE*_INT_CNTL` fields to enable/disable CP interrupt sources, and composes `CP_HQD_PQ_CONTROL` before loading ring/HQD state. `mes_v11_0.c` builds MES queue descriptors with `CP_HQD_PQ_CONTROL` and then writes `regCP_HQD_PQ_CONTROL`. AMDKFD MQD managers use `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PQ_CONTROL`, `CP_HQD_PQ_DOORBELL_CONTROL`, `CP_HQD_IB_CONTROL`, and `CP_HQD_QUANTUM` to initialize compute queues and context-save/restore state.

## State And Persistence Behavior

The file stores no software state and persists nothing. It names bit layouts for hardware state exposed by GC 11.0.3 registers.

The represented hardware state is broad:

- Ring state includes base addresses, high address words, read/write pointers, writeback addresses, queue size, block size, cache policy, execution enable/disable, privilege, TMZ security mode, and kernel-queue marking.
- Doorbell state includes per-ring and MEC doorbell ranges, per-HQD doorbell offsets, doorbell enable/mode/source/hit bits, and doorbell update status.
- Interrupt state includes masks/enables, pending status, debug assertion state, and fine-grained F32 interrupt source bits for PFP, ME, MEC1, MEC2, ring, and CPC paths.
- Queue and scheduler state includes VMIDs, queue priorities, pipe priorities, process/HQD quantum state, maximum context settings, queue manager control, dequeue requests, IQ timer state, and active/mapped status.
- Suspend/preemption/DDID state includes VMID reset/preempt requests and status, CPC context-save base/size/offset registers, suspend/resume control, DDID ring base/control/count pointers, and HPD fence/reporting fields.
- Error, debug, and maintenance state includes ECC first occurrence, fatal error, EDC configuration, UTCL1 error/status, DMA watchpoint configuration/status, soft reset, SD control, busy hysteresis, and RCIU CAM access.
- SPI scheduling state includes arbitration priorities/cycles, pipe percentage controls, per-VMID user accumulation/debug controls, compute queue reset, and compute wavefront context-save controls.

Persistence is hardware-defined. Some fields are configuration that lasts until reset, power-gating, suspend/resume, queue teardown, or explicit reprogramming. Other fields are live counters/status, sticky error indicators, write-one/self-clearing requests, active queue state, or hardware-owned pointers that change while the GPU is running. The masks themselves do not encode read-only versus writeable semantics, clearing rules, required ordering, or power-domain restrictions.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`, which supplies the register offsets matching these shift/mask definitions. The definitions also depend on the common AMDGPU register helper macros in the driver tree for field packing/unpacking and SOC15 instance addressing.

Integration points include:

- GC 11.0.3 ASIC support in `amdgpu/gfx_v11_0_3.c`, `amdgpu/imu_v11_0_3.c`, and `amdgpu/gfxhub_v3_0_3.c`.
- Generic GC 11 GFX and MES queue setup paths that program HQD/MQD, CP ring, interrupt, and doorbell registers.
- AMDKFD compute queue creation/update/load/destroy paths. MQD code writes fields such as `CP_HQD_PERSISTENT_STATE__PRELOAD_REQ`, `CP_HQD_PERSISTENT_STATE__QSWITCH_MODE`, `CP_HQD_PQ_CONTROL__QUEUE_SIZE`, `CP_HQD_PQ_CONTROL__NO_UPDATE_RPTR`, `CP_HQD_PQ_CONTROL__SLOT_BASED_WPTR`, `CP_HQD_PQ_CONTROL__QUEUE_FULL_EN`, `CP_HQD_PQ_DOORBELL_CONTROL__DOORBELL_OFFSET`, and `CP_HQD_IB_CONTROL__MIN_IB_AVAIL_SIZE`.
- Interrupt enable/disable and interrupt decode paths for timestamp, privileged access faults, opcode/reserved-bit errors, ECC/EDC, GPF, dequeue, and queue-message events.
- GPU reset, soft reset, VMID reset/preempt, suspend/resume, CWSR, and queue preemption flows.
- Debug/profiling and validation paths for DMA watchpoints, DDID counters, HPD fence reporting, CP debug buses, RCIU CAM reads, SPI arbitration, and compute queue reset.
- Security and virtualization boundaries through VMID fields, privilege bits, TMZ fields, doorbell offsets/ranges, and queue manager controls.

## Risks And Edge Cases

- Header/offset mismatch is the main correctness risk. Pairing `gc_11_0_3_sh_mask.h` with a different GC generation's offset header can compile while writing the wrong bits.
- The chunk boundary is artificial. It begins after the `CP_RB0_CNTL` shift fields and ends before the full `CP_HQD_IQ_TIMER` block is complete; adjacent chunks are needed for the full register-map narrative.
- The macros are untyped constants. Using a mask with the wrong register family, a stale field name, or a wrong generation can silently alter queue execution, interrupt routing, security policy, or reset behavior.
- Several registers mix enable bits, request bits, active/status bits, counters, and configuration. Whole-register writes can accidentally clear status, assert reset/dequeue/preempt requests, disable interrupts, change VMID ownership, or disturb reserved bits.
- Doorbell and pointer fields are alignment-sensitive. For example, read-pointer and write-pointer report/poll address fields start at bit 2 or 3, and doorbell offsets start at bit 2. Incorrect shifting can point hardware at the wrong memory or doorbell slot.
- Queue size fields are encoded sizes, not raw byte counts. AMDKFD/MES/GFX callers derive these from ring sizes; off-by-one or unit mistakes can cause queue wrap, underrun, stale read pointers, or hangs.
- TMZ, privilege, VMID, and KMD queue bits affect isolation. Incorrect programming can expose queues to the wrong address space, make user queues privileged, or break secure-memory matching.
- Interrupt enable/status families are similar but not identical across top-level CP, ring, CPC, and ME/MEC pipe registers. Reusing one register's masks for another can miss sources such as dequeue/SUA or enable unsupported bits.
- Live status such as HQD active, IQ timer active, processing IQ/IB, preempt/dequeue status, DDID inflight counts, and DMA watch stats can race with firmware, scheduler, reset, or user queue activity unless the caller owns the relevant queue selection and synchronization.
- Debug and power fields can override clock gating, soft reset CP subblocks, suppress interrupts, or change busy filtering. These are high-risk outside bring-up, recovery, or validated workarounds.
- Full-width masks such as `0xFFFFFFFFL` often describe pointer/counter/data fields, not necessarily safe write payloads.

## Test Signals

Useful validation signals for code using this chunk include:

- Build coverage for GC 11.0.3 include users, catching missing or mismatched `__SHIFT`/`_MASK` macro names.
- Queue bring-up tests that submit graphics, compute, and MES-managed work on GC 11.0.3 hardware and verify ring write/read pointer progress, doorbell hits, and absence of CP hangs.
- AMDKFD queue tests for AQL and PM4 queues, including queue size encoding, read-pointer reporting, write-pointer polling, doorbell offset programming, CWSR enablement, and queue priority behavior.
- Interrupt tests that enable timestamp, opcode/reserved-bit, privileged access, dequeue, ECC/EDC, GPF, and queue-message paths and confirm expected status bits and interrupt routing.
- Preemption, VMID reset, queue destroy, and suspend/resume tests that watch `CP_HQD_ACTIVE`, dequeue request status, IQ timer state, VMID preempt/status fields, and CWSR save-area programming.
- Security/isolation tests for VMID, TMZ, privilege, and KMD queue fields, especially mixed secure/non-secure queues and user versus kernel queue programming.
- GPU reset/recovery tests that exercise `CP_SOFT_RESET_CNTL`, CP debug/fatal/error state, and reinitialization of CP rings and HQDs after reset.
- DMA watchpoint and DDID/HPD diagnostics that confirm address alignment, VMID filtering, counters, and fence reports behave as decoded by the masks.
- Register trace comparison against known-good GC 11.0.3 hardware initialization tables for CP interrupt, SPI arbitration, HQD, MQD, and doorbell registers.
