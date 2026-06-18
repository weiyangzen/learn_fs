# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_syncobj.h

## Purpose
Declares the MSM syncobj helper interface shared by command submit and VM_BIND code.

## Important APIs, Types, and Functions
- `struct msm_syncobj_post_dep` stores an output syncobj ref, target timeline point, and optional `dma_fence_chain`.
- `msm_syncobj_parse_deps()` parses input dependency descriptors and adds them to a scheduler job.
- `msm_syncobj_reset()` clears selected input syncobjs.
- `msm_syncobj_parse_post_deps()` parses output syncobj descriptors.
- `msm_syncobj_process_post_deps()` installs a job fence into output syncobjs or timeline chains.

## Control Flow
The header defines declarations only. Callers parse input dependencies before arming/pushing a DRM scheduler job, parse post-dependencies before queuing, then after successful queueing reset requested input syncobjs and publish the output fence.

## State and Persistence
No state is stored by this header. It describes temporary helper data and persistent syncobj mutations performed by `msm_syncobj.c`.

## Dependencies and Integration Points
Includes DRM device, syncobj, and GPU scheduler headers. Used by `msm_gem_submit.c` and `msm_gem_vma.c`.

## Risks
The interface requires callers to free returned arrays, put syncobj refs, and free any unused `dma_fence_chain` entries. Misordered calls can expose fences too early or fail to reset input syncobjs.

## Test Signals
Build coverage for submit and VM_BIND users, plus runtime syncobj dependency/reset/post-dep tests through both ioctls.
