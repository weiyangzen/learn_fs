<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_client.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_client.c

## Purpose
`xe_drm_client.c` implements per-DRM-client memory and engine runtime reporting for `/proc/<pid>/fdinfo`, plus client object lifetime and private BO tracking.

## Important APIs, types, and functions
`xe_drm_client_alloc()` initializes a kref and, with procfs, `bos_lock` and `bos_list`. `__xe_drm_client_free()` releases the client. `xe_drm_client_add_bo()` and `xe_drm_client_remove_bo()` attach internal BOs to client accounting. `bo_meminfo()` classifies BO memory as private/shared, resident, active, and purgeable. `show_meminfo()` aggregates public GEM objects and internal client BOs. `show_run_ticks()` samples queue runtime and total GPU timestamp. `xe_drm_client_fdinfo()` prints memory and run-tick sections.

## Control flow and integration points
Memory reporting walks the DRM file object IDR under `file->table_lock`; if a BO reservation cannot be trylocked it temporarily refs the BO, drops the table lock, locks the BO, samples it, and reacquires. Internal BOs are walked under `client->bos_lock` with deferred put batching. Runtime reporting waits for pending queue removal to complete, takes runtime PM and forcewake on any engine, updates all file exec queues, reads a hardware timestamp, then prints class-specific cycle keys and capacities.

## State and persistence behavior
Client state persists for the DRM file lifetime and owns refs from BO client links. `xef->run_ticks[]` accumulates queue runtime deltas; pending queue removal uses an atomic wait variable to avoid fdinfo racing context-switch-out accounting.

## Dependencies, risks, and test signals
Dependencies include DRM fdinfo/memory stats, Xe BO/ref helpers, exec queue runtime updates, forcewake, runtime PM, hardware engine timestamp reads, and procfs configuration. Risks include lock-order regressions, BO UAF during list walks, inaccurate parallel-queue accounting, VF omission of total cycles, and stalled fdinfo waits. Test signals are fdinfo memory totals by region, shared/imported object accounting, queue create/destroy while reading fdinfo, SR-IOV VF output, and runtime PM/forcewake leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_drm_client.c -->
