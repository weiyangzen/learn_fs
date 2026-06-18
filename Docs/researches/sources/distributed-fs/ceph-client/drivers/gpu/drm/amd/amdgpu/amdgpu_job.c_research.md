## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_job.c

Purpose: implements AMDGPU job allocation, scheduler backend callbacks, direct IB submission, timeout recovery, resource cleanup, and forced job poisoning. It connects DRM GPU scheduler jobs to AMDGPU rings, VMID assignment, fences, resets, and coredumps.

Important APIs/functions: `amdgpu_job_alloc()` and `amdgpu_job_alloc_with_ib()` allocate flexible `struct amdgpu_job` objects with HW and VM fences. `amdgpu_job_submit()` arms a DRM scheduler job and pushes it; `amdgpu_job_submit_direct()` bypasses entity scheduling and calls `amdgpu_ib_schedule()`. Backend ops are `amdgpu_job_prepare_job()`, `amdgpu_job_run()`, `amdgpu_job_timedout()`, and `amdgpu_job_free_cb()`. `amdgpu_job_stop_all_jobs_on_sched()` drains queued and pending jobs with `-EHWPOISON`.

Control flow: scheduled jobs first run `prepare_job`, which checks entity errors, handles gang switching, enforces isolation, and grabs a VMID if needed. `run_job` validates VM generation and gang resubmit policy, schedules IBs to the target ring, increments `job_run_counter`, and frees IB resources against the proper fence. Timeout handling first records IP state and coredumps non-SRIOV devices, attempts soft recovery when supported, then tries per-queue reset, otherwise marks the finished fence with `-ETIME` and calls full GPU recovery if allowed. When recovery is disabled or unsuitable, the scheduler is suspended and SRIOV TDR debug is marked.

State and persistence: jobs hold VM pointer, explicit sync, fences, IBs, PASID/VMID, preamble/preemption flags, user fence address/sequence, shadow/CSA/GDS virtual addresses, generation, and isolation flags. State is transient but error status is propagated through DMA fences and coredump infrastructure.

Dependencies/integration: depends on DRM scheduler, DMA fences, AMDGPU IB/ring/fence, VM generation/VMID, reset domain, XGMI hive handling, coredump, KFD/PASID task info, and GPU recovery policy.

Risks: timeout paths are concurrency-heavy and touch scheduler state, reset state, coredumps, XGMI hive locks, and fences; ordering bugs can deadlock or double signal. `amdgpu_job_stop_all_jobs_on_sched()` is explicitly documented as duplicated and racy, retained only temporarily. Direct submission transfers ownership by freeing the job after successful IB scheduling, so callers must not reuse it after success.

Test signals: scheduler unit/integration tests should cover normal submit, direct ring tests, VMID wait fences, gang submit, isolation fences, timeout soft recovery, per-queue reset, full GPU recovery, SRIOV no-coredump behavior, and job cleanup under error allocation paths.
