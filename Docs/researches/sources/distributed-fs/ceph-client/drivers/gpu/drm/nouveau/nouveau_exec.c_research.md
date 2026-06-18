
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_exec.c

## Purpose
Implements the `DRM_NOUVEAU_EXEC` ioctl for the new VM_BIND/EXEC UAPI. It schedules asynchronous push-buffer execution jobs on an ABI16 channel while coordinating GPUVM reservations, syncobjs, scheduler credits, and a Nouveau hardware fence.

## Important APIs, Types, and Functions
External entry points are `nouveau_exec_job_init()` and `nouveau_exec_ioctl_exec()`. The job operation callbacks are `nouveau_exec_job_submit()`, `nouveau_exec_job_armed_submit()`, `nouveau_exec_job_run()`, `nouveau_exec_job_free()`, and `nouveau_exec_job_timeout()`, collected in `nouveau_exec_job_ops`. Helpers `nouveau_exec_ucopy()` and `nouveau_exec_ufree()` copy/free userspace arrays for waits, signals, and push descriptors.

## Control Flow
The ioctl obtains ABI16 state, requires an initialized UVMM, finds the requested channel by CHID, rejects killed or pre-NV50 channels, bounds push count by half the GPFIFO ring minus one fence slot, copies userspace push and sync arrays, and submits a job. Job init validates per-push length against `NV50_DMA_PUSH_MAX_LENGTH`, duplicates push descriptors, attaches scheduler/sync metadata, and initializes the generic Nouveau job. Submit creates a fence but delays emission, locks GPUVM execution state, and validates backing reservations. Armed submit attaches the scheduler done fence to reservations. Run waits for GPFIFO space, pushes each indirect buffer, posts the channel, emits the hardware fence, and returns its `dma_fence`. Timeout kills the channel and asks the scheduler for reset handling.

## State and Persistence
Per-job state is transient in `struct nouveau_exec_job`: generic job base, channel, copied push descriptors, and a hardware fence pointer. Persistent state comes from the per-file `nouveau_cli`, UVMM, ABI16 channel list, channel scheduler, and channel kill flag.

## Dependencies and Integration Points
The file integrates with DRM GPU scheduler through `nouveau_sched`, DRM GPUVM exec validation, syncobjs through the generic job layer, ABI16 channel lookup, Nouveau fences, NVIF GPFIFO submission, UVMM state, and the ioctl table in `nouveau_drm.c`.

## Risks and Test Signals
Risks include mismatched legacy ABI16 channel ownership with new UVMM requirements, malformed userspace arrays, scheduler/fence lifetime errors, GPFIFO credit miscalculation, and timeout channel-kill behavior. Test signals include EXEC with zero and many push buffers, invalid channel IDs, killed channels, pre-NV50 channels, syncobj wait/signal chains, VM_BIND dependency ordering, timeout injection, and userspace pointer fault tests.
