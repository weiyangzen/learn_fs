
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_exec.h

## Purpose
Declares data structures and APIs for Nouveau EXEC jobs. It is the local contract between the DRM ioctl layer, scheduler job implementation, and command submission code.

## Important APIs, Types, and Functions
`struct nouveau_exec_job_args` carries file private data, scheduler, channel, input sync array, output sync array, and push descriptor array. `struct nouveau_exec_job` embeds `struct nouveau_job`, stores the pending Nouveau fence, selected channel, and copied push descriptors. `to_nouveau_exec_job()` converts a generic job to an EXEC job. Declared functions are `nouveau_exec_job_init()` and `nouveau_exec_ioctl_exec()`. The inline `nouveau_exec_push_max_from_ib_max()` computes a conservative push descriptor limit from GPFIFO depth.

## Control Flow
The header's inline push limit reserves half the indirect-buffer ring and leaves one additional slot for the hardware fence, preventing jobs from starving the channel ring between submissions.

## State and Persistence
The types define transient per-ioctl/per-job state only. Persistent state remains in the scheduler, channel, client, and UVMM objects referenced by pointers.

## Dependencies and Integration Points
Includes `nouveau_drv.h` and `nouveau_sched.h`, and relies on UAPI structures such as `drm_nouveau_exec_push` and `drm_nouveau_sync`. It is included by `nouveau_exec.c` and registered through `nouveau_drm.c`.

## Risks and Test Signals
Risks are mostly ABI boundary and ring-capacity related. Tests should cover push count limits for small and large `ib_max`, structure lifetime after userspace array copy, and build coverage when scheduler and VM_BIND support are enabled.
