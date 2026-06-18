## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_job.h

Purpose: declares the AMDGPU scheduler job structure, internal kernel job identifiers, preamble/preemption flags, and job lifecycle API.

Important APIs/types: `struct amdgpu_job` embeds `struct drm_sched_job` and carries VM, explicit sync, HW fences, gang fence, VMID/PASID, GDS/GWS/OA allocation ranges, VM generation, user fence metadata, shadow/CSA/GDS virtual addresses, isolation flags, run counter, and a flexible array of IBs. `AMDGPU_KERNEL_JOB_ID_*` reserves descending `u64` IDs for internal jobs such as VM updates, TTM moves, TLB flush, KFD GART map, ring tests, and cleaner shader. `amdgpu_job_ring()` maps a job to its scheduler ring.

Control flow contract: callers allocate with `amdgpu_job_alloc()` or `_with_ib()`, fill IBs/resources, optionally set gang leader, submit through scheduler or direct ring path, and release with `amdgpu_job_free()` on unsubmitted/error paths. Scheduler callbacks in `amdgpu_job.c` own cleanup after normal scheduled submission.

State and persistence: job state is transient per submission. Fence state persists only as kernel synchronization objects until all references drop. The generation field records VM generation at allocation and is used to cancel jobs after VRAM loss.

Dependencies/integration: includes DRM GPU scheduler, AMDGPU sync, and ring definitions. Used broadly by command submission, ring tests, VM updates, media tests, and reset/recovery.

Risks: flexible array sizing requires accurate `num_ibs`. The inline ring accessor assumes `base.entity` and scheduler queue are initialized, so it is not valid for all direct-submit jobs. Internal job ID space must avoid collision with userspace client IDs.

Test signals: compile coverage for command submission and ring-test paths, leak tests for allocation failure, scheduler tests for fence signaling and job free callback, and VM generation tests after recovery.
