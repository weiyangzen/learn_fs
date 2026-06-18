# sources/distributed-fs/ceph-client/include/uapi/drm/lima_drm.h

## Purpose

`lima_drm.h` is the UAPI for the Lima driver for Arm Mali-400/Mali-450 GPUs. It defines GPU parameter queries, GEM BO create/info/wait, GP and PP frame submission layouts, explicit syncobj submission, and context create/free. The complete 176-line header was read.

## Important APIs, Types, and Functions

Public ioctls are `GET_PARAM`, `GEM_CREATE`, `GEM_INFO`, `GEM_SUBMIT`, `GEM_WAIT`, `CTX_CREATE`, and `CTX_FREE`. Important types include `drm_lima_get_param`, `drm_lima_gem_create`, `drm_lima_gem_info`, submit BO entries, GP/M400 PP/M450 PP frame structs, `drm_lima_gem_submit`, `drm_lima_gem_wait`, and context structs. `LIMA_BO_FLAG_HEAP` marks dynamically backed heap buffers.

## Control Flow

Userspace queries GPU ID and version data, creates a context and BOs, obtains GPU VA and mmap offsets, builds GP or PP frame data, submits with BO table and optional explicit syncobjs, waits for BO read/write completion before CPU access, then frees the context.

## State and Persistence Behavior

Context IDs persist until `CTX_FREE`; GEM handles persist under DRM GEM lifetime. Heap BO backing can grow when GP tasks run out of heap memory, bounded by the declared size. Syncobj handles are external DRM synchronization state referenced by submissions.

## Dependencies and Integration Points

Depends on `drm.h`. Integrates with the Lima scheduler/MMU, Mesa Lima userspace, DRM GEM/mmap, DRM syncobj, and Mali-400/450 GP/PP hardware frame formats.

## Risks and Edge Cases

Key risks are GP versus PP pipe validation, Mali-400 versus Mali-450 frame size/layout validation, heap upper-bound enforcement, BO read/write flag correctness, fixed explicit fence slots, absolute timeout behavior, and padding/unknown flag rejection.

## Test Signals

Cover all get-param values, normal and heap BO create/info, context lifetime, GP and PP submit variants, explicit syncobj in/out behavior, BO wait read/write timeouts, and invalid pipe/frame/BO/sync/padding cases.
