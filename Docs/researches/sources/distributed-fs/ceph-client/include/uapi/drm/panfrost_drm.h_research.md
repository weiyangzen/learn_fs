# sources/distributed-fs/ceph-client/include/uapi/drm/panfrost_drm.h

## Purpose

`panfrost_drm.h` defines the Panfrost DRM UAPI for Arm Mali Midgard/Bifrost job-manager GPUs. It covers job submission, BO lifecycle and waits, parameter discovery, madvise, BO labels/sync/info, JM context priorities, coredump formats, and unstable debug performance counters. The complete 476-line header was read.

## Important APIs, Types, and Functions

Stable ioctls include `SUBMIT`, `WAIT_BO`, `CREATE_BO`, `MMAP_BO`, `GET_PARAM`, `GET_BO_OFFSET`, `MADVISE`, `SET_LABEL_BO`, `JM_CTX_CREATE/DESTROY`, `SYNC_BO`, and `QUERY_BO_INFO`. `PERFCNT_ENABLE/DUMP` are explicitly unstable and gated by `unstable_ioctls`. Important structs include submit/wait/create/mmap/get-param/get-offset/perfcnt/madvise/label/sync/query-info structs, coredump object/register structs, and JM context create/destroy.

## Control Flow

Userspace queries GPU features, creates BOs, obtains GPU and CPU mmap offsets, submits a job descriptor with referenced BO handles and optional syncobjs/JM context, waits for BO completion, labels BOs, performs cache syncs, and creates/destroys priority JM contexts. Perfcnt flow is debug-only: enable a counter set and dump to a userspace buffer.

## State and Persistence Behavior

BO handles and fd-private GPU offsets persist under GEM lifetime. JM context handles persist until destroyed. Madvise may discard backing pages and reports retention. BO labels persist until cleared or object destruction. Coredump structures represent persisted crash artifacts for decoding.

## Dependencies and Integration Points

Depends on `drm.h`. Integrates with Panfrost scheduling, GEM/shmem and dma-buf import, DRM syncobj, Mesa Panfrost, Mali feature registers, cache maintenance paths, and GPU coredump tooling.

## Risks and Edge Cases

Risks include relying on unstable perfcnt ioctls, invalid BO flag combinations such as heap with WB mmap, imported BO coherency, privileged priority checks, syncobj validation, job descriptor/BO array validation, native-endian coredumps, and BO sync range rounding/overflow.

## Test Signals

Cover parameter queries, BO create/mmap/offset/query-info for normal/heap/noexec/WB/imported BOs, submit with syncobjs and JM contexts, wait timeouts, madvise retained status, label limits, BO sync ranges, priority permission checks, perfcnt gating, and coredump decoding.
