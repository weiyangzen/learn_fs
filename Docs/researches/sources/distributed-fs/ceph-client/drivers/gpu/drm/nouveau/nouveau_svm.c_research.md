# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_svm.c

## Purpose
This file implements Nouveau shared virtual memory support for replayable GPU faults. It creates per-client managed VMMs, registers mmu notifiers, links channel instance pointers to SVMM contexts, services GPU fault buffers with HMM, maps CPU/device-private pages into GPU page tables, and exposes migration helpers.

## Important APIs, Types, and Functions
Major external functions are `nouveau_svm_init`, `nouveau_svm_fini`, suspend/resume hooks, `nouveau_svmm_init`, `nouveau_svmm_fini`, `nouveau_svmm_join`, `nouveau_svmm_part`, `nouveau_svmm_bind`, `nouveau_svmm_invalidate`, `nouveau_pfns_alloc`, `nouveau_pfns_free`, and `nouveau_pfns_map`. Internal machinery includes `struct nouveau_svm`, fault-buffer state, `struct nouveau_svmm`, `nouveau_svm_fault`, `nouveau_range_fault`, `nouveau_atomic_range_fault`, and fault replay/cancel helpers.

## Control Flow
SVM init selects a supported fault-buffer class, allocates one buffer, maps it, installs an NVIF event, and enables notifications. Per-file SVM initialization creates a managed VMM with replayable faults, records an unmanaged aperture, and registers an mmu notifier against the current mm. Channel join/part maps GPU instance pointers to SVMMs under the global SVM mutex. On a fault event, workqueue code drains hardware fault entries, sorts them by instance/address/access priority, resolves instance pointers to SVMMs, faults or exclusively pins CPU pages through HMM/mmu interval notifiers, issues `NVIF_VMM_V0_PFNMAP`, cancels unhandled faults, and replays handled faults.

## State and Persistence Behavior
Persistent state includes `drm->svm`, the global instance list, per-buffer GET/PUT pointers, cached fault objects, NVIF event/object handles, per-client `cli->svm.vmm`, and the mmu notifier-owned `nouveau_svmm`. Page table state is explicitly invalidated on mmu notifier callbacks except for migration events owned by Nouveau device-private memory.

## Dependencies and Integration Points
It depends on Linux HMM, mmu notifiers, device-private pages, Nouveau dmem migration, NVIF VMM methods, GPU fault-buffer classes, channel setup, and client VMM selection. `nouveau_pfns_map` is used by migration paths to install batches of PFN mappings.

## Risks
Fault handling is concurrency-heavy: mm lifetime, mmu interval retry, SVMM teardown, and GPU fault replay/cancel ordering must all align. The code intentionally disables newer-than-Pascal SVM because recovery is not fixed. Atomic faults use `make_device_exclusive`, so incorrect ownership or unlock ordering can corrupt CPU/GPU memory semantics.

## Test Signals
Signals include SVM init ioctl rejection/acceptance, page fault replay for read/write/atomic/prefetch, CPU unmap invalidation, dmem migration, process exit while faults are pending, suspend/resume fault-buffer disable/enable, and fault cancel recovery for invalid channels.
