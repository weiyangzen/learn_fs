# sources/distributed-fs/ceph-client/include/uapi/drm/msm_drm.h

## Purpose

`msm_drm.h` defines the Qualcomm/Adreno MSM DRM UAPI for parameters, GEM allocation and metadata, CPU synchronization, command stream submission, fence waits, madvise, submitqueues, and explicit VM_BIND mode. The complete 529-line header was read.

## Important APIs, Types, and Functions

Ioctls include `GET_PARAM`, `SET_PARAM`, `GEM_NEW`, `GEM_INFO`, `GEM_CPU_PREP`, `GEM_CPU_FINI`, `GEM_SUBMIT`, `WAIT_FENCE`, `GEM_MADVISE`, submitqueue new/close/query, and `VM_BIND`. Important structs are `drm_msm_param`, GEM new/info/prep/fini, syncobj, submit reloc/cmd/BO/submit, VM bind op/request, wait fence, madvise, and submitqueue query/create structs.

## Control Flow

Classic userspace creates BOs, assigns or queries IOVAs, prepares CPU access, submits command buffers with BO and command tables plus sorted relocations, and waits with sequence fences, fence fds, or syncobjs. VM_BIND flow is enabled once with `MSM_PARAM_EN_VM_BIND` before BO or VM_BIND queue creation; userspace then owns IOVA allocation, maps/unmaps with `VM_BIND`, and submits without a resident BO table.

## State and Persistence Behavior

GEM handles, submitqueue IDs, fences, private BO reservation state, and VM_BIND enablement are fd/context state. VM_BIND enablement is write-once and cannot be disabled. Async VM_BIND failures or GPU faults can make the VM unusable, causing later submit to fail with `-EPIPE`. Madvise can discard BO backing and report retention.

## Dependencies and Integration Points

Depends on `drm.h`. Integrates with MSM/Adreno scheduling, per-process page tables, GEM/dma-buf, KMS scanout, sync_file fds, DRM syncobj/timeline syncobj, Mesa freedreno/turnip, and GPU fault/debug accounting.

## Risks and Edge Cases

Risks include mixed classic/VM_BIND mode rejection, pointer/length handling in `GEM_INFO`, relocation ordering and presumed IOVA writeback, synchronization flag combinations, private BO sharing restrictions, async VM unusable transitions, op/stride validation, and absolute timeout handling.

## Test Signals

Cover parameter permissions and VM_BIND write-once behavior, GEM flags/cache modes, `GEM_INFO` scalar and pointer metadata paths, CPU prep/fini, submit reloc sorting and fence/syncobj combinations, submitqueue priority/preempt, VM_BIND map/unmap/map-null/multi-op/async failure, madvise retention, and fault query paths.
