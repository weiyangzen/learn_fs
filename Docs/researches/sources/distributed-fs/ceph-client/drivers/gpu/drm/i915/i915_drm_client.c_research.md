# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_drm_client.c

## Purpose
`i915_drm_client.c` tracks per-DRM-file client accounting for fdinfo and internal object attribution. It allocates `i915_drm_client` objects, manages references, reports memory and engine runtime statistics, and associates internal context objects with a client when `/proc` support is enabled.

## Important APIs, Types, and Functions
Public functions are `i915_drm_client_alloc()`, `__i915_drm_client_free()`, `i915_drm_client_fdinfo()`, `i915_drm_client_add_object()`, `i915_drm_client_remove_object()`, and `i915_drm_client_add_context_objects()`. Internal helpers include `obj_meminfo()`, `show_meminfo()`, `busy_add()`, and `show_client_class()`. `uabi_class_names[]` maps render, copy, video, video-enhance, and compute engine classes to fdinfo keys.

## Control Flow
Open paths allocate a client with initialized kref, context list lock, and optional object list lock. fdinfo first accounts public GEM handles from `file->object_idr`, then internal objects from the client's RCU-protected `objects_list`, and prints DRM memory stats by memory region. For gen8+ it then sums closed-context runtime from `client->past_runtime[class]` with live context runtime gathered under RCU from each context's engines, printing per-engine-class time and capacity. Object add/remove updates `obj->client` and the RCU list under `objects_lock`. Context object attribution adds context state objects and non-legacy ring backing objects.

## State and Persistence Behavior
Client state persists for the lifetime of a DRM file and may outlive object list removal under RCU. `past_runtime[]` accumulates runtime from closed contexts. `ctx_list` links live contexts to the client. Under `CONFIG_PROC_FS`, `objects_list` tracks driver-internal objects attributed to a client in addition to public handles. Object client references are kref-managed and released after RCU deletion.

## Dependencies and Integration Points
This file integrates with DRM fdinfo (`drm_show_fdinfo`), GEM object IDRs, GEM object memory regions, dma-resv activity tests, i915 GEM contexts and engines, `intel_context_get_total_runtime_ns()`, memory region UABI names, and `/proc` conditional compilation. It is called from `i915_gem_open()`, context lifecycle code, object lifecycle code, and `i915_driver.c` through `.show_fdinfo`.

## Risks
Accounting must tolerate concurrent object/context teardown. The object list uses RCU plus object ref acquisition; missing refs can cause use-after-free. Runtime totals can race with engine/context changes but are intended as stats, not synchronization. `I915_LAST_UABI_ENGINE_CLASS` must cover all indexed classes or fdinfo arrays can be undersized. Memory stats distinguish shared/private via GEM helpers and may underreport internal objects when `/proc` is disabled.

## Test Signals
Check `/proc/<pid>/fdinfo/<drm-fd>` for `drm-memory-*`, `drm-engine-*`, and capacity fields; verify public and internal object accounting across create/close; run workloads on each engine class and observe runtime growth; close contexts and verify runtime migrates into `past_runtime`; use KCSAN/lockdep/RCU debug to exercise concurrent object removal.
