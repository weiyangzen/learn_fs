# sources/distributed-fs/ceph-client/include/uapi/drm/i915_drm.h

## Purpose

`i915_drm.h` is the Intel i915 DRM userspace ABI contract. It defines legacy DRI1 ioctls, GEM BO management, execbuffer submission, context/VM configuration, perf/OA streams, PMU and uevent names, engine and memory discovery queries, and protected-content/object creation extensions. The complete 3916-line header was read for this report.

## Important APIs, Types, and Functions

There are no functions; the public API is ioctl numbers/macros, enums, structs, and flags. Key payload families are `drm_i915_getparam`, GEM create/read/write/mmap/domain/cache/tiling/wait/busy/madvise structs, `drm_i915_gem_execbuffer2` with `drm_i915_gem_exec_object2`, relocations, sync-file fences, syncobj fence arrays and timeline-fence extensions, `drm_i915_gem_context_create_ext`, `drm_i915_gem_context_param`, SSEU and engine-map extension structs, `drm_i915_gem_vm_control`, i915 perf stream/config records, `drm_i915_query`/`drm_i915_query_item`, engine/topology/perf/memory-region/GUC query structs, and `drm_i915_gem_create_ext` memory-region/protected-content/PAT extensions. `struct i915_user_extension` is the common linked-extension base.

## Control Flow

Runtime flow is ioctl-sequenced: query capabilities with `GETPARAM`/`QUERY`, create BOs, obtain mmap offsets, set domains/cache/tiling when supported, configure contexts and engine maps, submit batches through `GEM_EXECBUFFER2`, then synchronize through waits, sync_file fds, syncobjs, busy checks, or perf stream reads. Query APIs commonly use a size-probe call followed by a fill call.

## State and Persistence Behavior

FD-scoped persistent state includes GEM handles, contexts, VM IDs, perf stream fds, BO placement, engine maps, and protected-content context/object state. Context persistence can allow work to survive process exit; non-persistent contexts cancel outstanding requests. Madvise can drop BO backing under memory pressure. PXP teardown invalidates protected contexts/objects. Reserved fields and unknown flags are MBZ compatibility state.

## Dependencies and Integration Points

Depends on `drm.h`. Integrates with i915 ioctl dispatch, Mesa/Intel userspace, DRM GEM, dma-buf/PRIME, KMS scanout, sync_file, DRM syncobj/timeline syncobj, perf PMU, GuC firmware, PXP protected content, and device uevent consumers.

## Risks and Edge Cases

ABI stability risk is very high: ioctl numbers, field order, type widths, removed IDs, and reserved bits must not drift. Legacy pointer fields require compat32. Execbuffer flags can bypass implicit sync or relocations, so validation mistakes can cause data corruption, hangs, or fd leaks. Discrete/local-memory platforms change cache/domain behavior. Query/extension chains require robust length, pointer, MBZ, and loop validation.

## Test Signals

Strong signals include struct layout tests on 32/64-bit builds, ioctl number checks, invalid flag/MBZ rejection, compat ioctl coverage, GEM create/mmap/cache/domain/tiling/madvise tests, execbuffer fences and timeline fences, context engine map/load-balance/bond/parallel-submit tests, memory-region and small-BAR placement tests, perf/OA stream tests, protected-content failure injection, and GPU reset/userptr invalidation coverage.
