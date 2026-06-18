# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu.h

## Purpose
Defines the common MSM GPU abstraction shared by Adreno-specific implementations, submit queues, ringbuffers, MMU/VMA code, devfreq, crash dumps, and debug paths. It is the central contract for GPU operations and per-file context state.

## Important APIs, Types, and Functions
- `struct msm_gpu_funcs` is the generation-specific virtual function table for params, hardware init, firmware upload, PM, submit/flush, IRQ, recovery, state dump, frequency control, VM creation, ring read pointer, progress detection, and sysprof setup.
- `struct msm_gpu` stores the common GPU instance: `drm_device`, platform device, funcs, SMMU private data, rings, locks, power resources, devfreq, workers, hangcheck, memptrs, crashstate, APRIV and relocation policy.
- `struct msm_context` stores per-DRM-file queues, VM, entity table, context labels, sysprof setting, memory/accounting counters, and cumulative elapsed/cycle stats.
- `struct msm_gpu_submitqueue` models a userspace queue with id, flags, ring, faults, last fence, IDR fence map, lock, refcount, and scheduler entity.
- `struct msm_gpu_state` and `struct msm_gpu_fault_info` describe crash/development diagnostic data.
- Inline helpers include `dev_to_gpu()`, `adreno_smmu_has_prr()`, `msm_context_is_vmbind()`, `msm_gpu_convert_priority()`, `msm_gpu_active()`, register read/write helpers, context/queue ref helpers, and crashstate get/put helpers.

## Control Flow
This header does not implement large flows, but its inline helpers shape them. `msm_gpu_convert_priority()` maps userspace priority to ring and DRM scheduler priority. `msm_gpu_active()` scans ring fences to determine active/idle transitions. Register helpers emit `trace_msm_gpu_regaccess` and perform 32-bit MMIO access. Context and queue helpers wrap krefs. Crashstate helpers serialize access with `gpu->lock`.

## State and Persistence
The types here define all durable in-memory GPU state for the driver: submitqueue lists, per-context VM ownership, ring arrays, power and devfreq state, fault counters, crash captures, and per-context accounting. State lifetime is controlled by krefs, DRM file close, GPU cleanup, and devcoredump release.

## Dependencies and Integration Points
Includes DRM scheduler, MSM GEM, MSM fence, ringbuffer, trace, devfreq, regulator, clock, interconnect, OPP, and Adreno SMMU private interfaces. It is included by submit, ringbuffer, devfreq, IOMMU, debug, and generation-specific GPU code.

## Risks
Since this header encodes shared contracts, changes can break ABI-facing behavior indirectly. Risks include priority mapping mismatches, stale context pointers avoided by `cur_ctx_seqno`, incorrect register width assumptions, sysprof PM/refcount imbalance, and VM_BIND mode checks being bypassed by direct `ctx->vm` access.

## Test Signals
Build coverage across all MSM GPU generations is essential. Runtime signals include correct priority-to-ring mapping, fdinfo stats, VM_BIND gating, crashstate lifecycle, tracepoint register access events, and clean context/submitqueue destruction under file close.
