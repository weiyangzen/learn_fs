# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ib.c

## Purpose
`amdgpu_ib.c` manages indirect buffer allocation, scheduling, testing, and debug reporting. IBs hold GPU command streams allocated from suballocator pools and are wrapped with VM flushes, HDP flush/invalidate, context-control packets, secure frame control, fences, conditional execution, and scheduler/job metadata when submitted to rings.

## Important APIs, types, and functions
Public functions are `amdgpu_ib_get()`, `amdgpu_ib_free()`, `amdgpu_ib_schedule()`, `amdgpu_ib_pool_init()`, `amdgpu_ib_pool_fini()`, `amdgpu_ib_ring_tests()`, and `amdgpu_debugfs_sa_init()`. The debugfs show helper dumps delayed, immediate, and direct SA pools.

## Control flow
IB allocation uses `amdgpu_sa_bo_new()` from the selected pool, maps CPU and GPU addresses, and defaults to `AMDGPU_IB_FLAG_EMIT_MEM_SYNC`. Scheduling validates ring readiness, VMID presence for VM jobs, and secure-submission support. It allocates ring space, determines context switch and pipeline sync requirements, emits VM flushes, begins the IB frame, inserts optional start packets, memory sync, high-priority wave limit, GFX shadow state, conditional execution, HDP flush, context-control, secure frame controls, each IB packet, HDP invalidate, user fence, shadow cleanup, hardware fence, optional end/switch-buffer/wave-limit cleanup, and commits the ring. Ring tests iterate ready rings with ASIC test hooks, use longer timeouts for SR-IOV/runtime/XGMI cases, and disable failed non-primary rings.

## State and persistence behavior
IB memory comes from runtime SA BO managers in `adev->ib_pools[]`. Scheduling updates ring write pointers, current context, fence metadata, VM fence packet offsets, job flags, and emitted hardware fences. Debugfs only reads live allocator state. There is no persistent storage.

## Dependencies and integration points
The file depends on SA BO managers, AMDGPU rings and ring funcs, DRM scheduler jobs/entities, VM flush logic, DMA fences, HDP coherency helpers, secure TMZ submission support, tracepoints, debugfs, and SR-IOV/XGMI runtime configuration. It is on the hot path for user command submission and kernel jobs.

## Risks and edge cases
`amdgpu_ib_schedule()` is dense and sensitive to ordering: VM flush must precede IBs, HDP flush/invalidate must bracket command execution, secure frame transitions must match IB flags, and fences must be emitted even with optional packets. `cond_exec` is patched unconditionally after optional initialization, so ring funcs must provide coherent behavior. Failure after ring allocation generally relies on pre-validation; error unwinding is limited. Primary GFX IB test failure disables acceleration.

## Test signals
IB pool init/fini, allocation failure injection, secure and mixed secure/nonsecure IB submissions, VM flush and context switch paths, user fence writes, high-priority ring wave limits, GFX shadow state, guilty context skip offsets, SR-IOV and XGMI ring tests, debugfs SA dump, and timeout-induced ring disabling are key tests.
