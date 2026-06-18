# Research: subset-b-003673

Grouped source research for subset B work item `subset-b-003673`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_sched.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_sched.c

## Purpose
This file implements Nouveau's DRM scheduler integration for software jobs. It wraps `drm_sched_job`, translates Nouveau VM bind and similar operations into scheduler work, handles syncobj dependencies and outputs, and tracks in-flight jobs for orderly scheduler teardown.

## Important APIs, Types, and Functions
Key APIs are `nouveau_job_init`, `nouveau_job_submit`, `nouveau_job_fini`, `nouveau_job_done`, `nouveau_job_free`, `nouveau_sched_create`, and `nouveau_sched_destroy`. Internal helpers cover input dependency lookup, output syncobj/timeline fence preparation and attachment, scheduler backend callbacks, timeout handling, and scheduler/workqueue setup.

## Control Flow
Job initialization copies user-provided wait/signal sync arrays, initializes the DRM scheduler job, and records caller-provided `nouveau_job_ops`. Submit first adds input fences, prepares output sync objects, serializes through `sched->mutex`, runs the operation-specific `submit` callback while failure is still allowed, arms the scheduler job, stores the done fence, optionally calls `armed_submit`, attaches output fences, pushes the job, and optionally waits for synchronous jobs. Scheduler run calls the job's `run` hook; scheduler free calls `nouveau_job_fini`.

## State and Persistence Behavior
State is per job: copied sync arrays, output syncobj references, fence chains, `done_fence`, state enum, client/file pointers, and list membership in `sched->job.list`. Scheduler state includes a DRM scheduler, one entity, an optional owned workqueue, a submit mutex, an in-flight job list, and a waitqueue used by teardown.

## Dependencies and Integration Points
It depends on DRM GPU scheduler, DRM syncobj/timeline sync, dma fences, `drm_gpuvm_exec`, Nouveau client/file state, and operation implementations such as UVMM bind jobs. `nouveau_sched_destroy` waits until `nouveau_job_done` removes every job before finalizing the scheduler.

## Risks
The submit path relies on the operation-specific `submit` hook not failing after jobs are armed. Missing `nouveau_job_done` would hang scheduler destruction. Sync jobs reject explicit in/out sync arrays, so ioctl validation must keep async semantics straight. Output timeline chains must be freed on all error paths.

## Test Signals
Useful signals include async VM bind tests with syncobj waits/signals, timeline syncobj point updates, forced operation submit failures, scheduler timeout injection, synchronous job wait behavior, and driver unload while jobs are still completing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_sched.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_sched.h

## Purpose
This header defines the Nouveau software job and scheduler interface used by UVMM and other submit paths that need DRM scheduler ordering, syncobj handling, and common lifecycle management.

## Important APIs, Types, and Functions
It defines `enum nouveau_job_state`, `struct nouveau_job_args`, `struct nouveau_job`, the embedded `struct nouveau_job_ops`, and `struct nouveau_sched`. It declares job lifecycle functions and scheduler create/destroy helpers. `to_nouveau_job` converts a `drm_sched_job` back to its Nouveau container.

## Control Flow
The header has no executable control flow, but its hook contract is important: `submit` may fail before arming, `armed_submit` is guaranteed after a successful `submit`, `run` executes from the DRM scheduler backend, `free` releases operation-specific state, and `timeout` is optional.

## State and Persistence Behavior
The structures persist copied sync arrays, output syncobj/fence-chain staging, a done fence, job state, client references, scheduler entity state, and a protected in-flight job list.

## Dependencies and Integration Points
It includes DRM GPUVM and GPU scheduler headers and is consumed by `nouveau_sched.c` and UVMM bind job code. It also depends on Nouveau client and DRM file concepts through `nouveau_drv.h`.

## Risks
The hook ordering contract must remain synchronized with the implementation. Callers must set `resv_usage`, `credits`, sync flags, and `ops` consistently or fence publication and reservation locking can be wrong.

## Test Signals
Build coverage catches signature drift. Runtime signals come from VM bind submission, scheduler teardown, timeout handling, and syncobj integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_sgdma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_sgdma.c

## Purpose
This file implements Nouveau's scatter-gather TTM translation-table backend for system/GART memory. It allocates `ttm_tt` state, binds host pages into Nouveau memory objects, maps pre-Tesla GART mappings, and tears the mapping down.

## Important APIs, Types, and Functions
`struct nouveau_sgdma_be` embeds `struct ttm_tt` first for compatibility with Nouveau BO population paths and stores the active `struct nouveau_mem`. Public functions are `nouveau_sgdma_create_ttm`, `nouveau_sgdma_bind`, `nouveau_sgdma_unbind`, and `nouveau_sgdma_destroy`.

## Control Flow
Creation chooses TTM caching from BO coherency, AGP bridge presence, and normal cached memory, then calls `ttm_sg_tt_init`. Bind is idempotent if `nvbe->mem` already exists, converts the TTM pages into a host `nouveau_mem`, and for pre-Tesla non-AGP style mappings maps it into the client VMM. Unbind finalizes the memory object and clears the pointer. Destroy finalizes the embedded TTM object and frees the backend.

## State and Persistence Behavior
The backend persists only while a TTM BO has a translation table. Binding state is represented by `nvbe->mem`; unbind removes GPU-visible mappings and host memory descriptors.

## Dependencies and Integration Points
It integrates with TTM TT allocation, Nouveau BO resource placement, `nouveau_mem_host`, `nouveau_mem_map`, and `nouveau_mem_fini`. It is declared through `nouveau_ttm.h` and used by the Nouveau BO driver.

## Risks
The first-field layout requirement is fragile. Caching selection affects CPU/GPU coherency, especially forced coherent and AGP paths. Failure after pre-Tesla mapping must call `nouveau_mem_fini` to avoid stale VMM state.

## Test Signals
Signals include GART BO creation, bind/unbind under eviction, AGP and non-AGP pre-Tesla paths, coherent GART CPU/GPU readback, and memory pressure during TTM population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_sgdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_svm.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_svm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_svm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_svm.h

## Purpose
This header defines the public SVM/SVMM interface and the `struct nouveau_svmm` state shared between Nouveau client VMM code, channel setup, migration, and SVM fault handling.

## Important APIs, Types, and Functions
`struct nouveau_svmm` contains an mmu notifier, active Nouveau VMM pointer, unmanaged address interval, and mutex. The header declares SVM driver lifecycle hooks, per-client SVMM init/fini, channel join/part, SVM bind/migration ioctl handling, GPU invalidation, and PFN-map allocation/free/map helpers. Disabled builds provide no-op or `-ENOSYS` stubs.

## Control Flow
The header has no executable flow. Its conditional compilation gate means callers can unconditionally call SVM hooks while feature availability is decided by `CONFIG_DRM_NOUVEAU_SVM`.

## State and Persistence Behavior
The declared state ties a process mm to a managed GPU VMM and tracks an unmanaged range that is excluded or partially clipped during invalidation and faults.

## Dependencies and Integration Points
It depends on NVIF OS types, Linux mmu notifier APIs, DRM device/file types, and Nouveau VMM/client code. It is included by `nouveau_svm.c`, `nouveau_vmm.c`, channel code, and migration helpers.

## Risks
Stub behavior must match caller expectations. The header forward-declares `struct mm_struct` only indirectly through included headers for `nouveau_pfns_map`, so include ordering matters.

## Test Signals
Build both with and without `CONFIG_DRM_NOUVEAU_SVM`; exercise ioctl paths, channel creation, VMM teardown, and migration helpers to catch signature or stub mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_svm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ttm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ttm.c

## Purpose
This file initializes and tears down Nouveau's TTM memory managers for VRAM and GART/system memory. It bridges Nouveau memory objects into TTM resource-manager callbacks and records NVIF memory type indices needed by BO placement and mapping.

## Important APIs, Types, and Functions
Resource managers are exposed as `nouveau_vram_manager`, `nouveau_gart_manager`, and `nv04_gart_manager`. Main lifecycle functions are `nouveau_ttm_init` and `nouveau_ttm_fini`. Internal helpers initialize host types, VRAM manager, GTT manager, and their finalizers.

## Control Flow
Initialization first discovers coherent and non-coherent host memory types, optional kind-aware host memory, and a mappable VRAM type for Tesla+ non-SoC devices. It initializes `ttm_device`, records AGP bridge data, reserves BAR1 WC memory type, installs a VRAM manager, adds an MTRR/WC mapping, computes GART size from the client VMM or AGP aperture, installs the TT manager, initializes IO reserve state, and logs available memory. Finalization evicts and removes VRAM/GTT managers, finalizes TTM, and releases WC/MTRR reservations.

## State and Persistence Behavior
Persistent driver state includes `drm->ttm.bdev`, `type_host`, `type_ncoh`, `type_vram`, AGP details, TTM resource managers, IO reserve lists, MTRR handle, and GEM available memory counters. Resource allocation callbacks create `nouveau_mem` objects and, for old GART, reserve VMM PTEs.

## Dependencies and Integration Points
It depends on TTM device/resource-manager APIs, Nouveau memory allocation (`nouveau_mem_*`), NVIF MMU type discovery, BAR1 resource helpers, PCI/AGP information, and architecture WC/MTRR functions.

## Risks
Initialization failure paths after partial setup must avoid leaking managers or WC reservations. Wrong memory type discovery causes BO placement failures. Old pre-Tesla GART allocation reserves GPU VA in the client VMM and must be paired with memory finalization.

## Test Signals
Signals include module load/unload on pre-Tesla, Tesla+, AGP, SoC, and SWIOTLB/DMA32 systems; VRAM/GART BO allocation and eviction; BAR1 WC reservation cleanup; and memory-type discovery failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ttm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ttm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ttm.h

## Purpose
This header exposes Nouveau TTM manager and SGDMA interfaces used by the BO driver and memory-management setup code.

## Important APIs, Types, and Functions
It defines `nouveau_bdev` to recover `struct nouveau_drm` from a TTM device, declares the VRAM/GART resource-manager function tables, SGDMA TT creation/bind/unbind/destroy helpers, and TTM global and per-device init/release functions.

## Control Flow
The header has no executable flow. It wires TTM callback implementations from `nouveau_ttm.c` and `nouveau_sgdma.c` into the rest of the driver.

## State and Persistence Behavior
No state is stored here. The declared functions operate on `drm->ttm`, TTM BOs, TTM resources, and SGDMA translation tables.

## Dependencies and Integration Points
It depends on TTM device, TTM resource manager, TTM TT, Nouveau DRM, and BO driver infrastructure. It is a shared include for TTM init and BO memory backing.

## Risks
Forward declarations must match TTM callback signatures. The `nouveau_bdev` container conversion assumes `ttm.bdev` remains embedded in `struct nouveau_drm`.

## Test Signals
Build coverage plus BO allocation/bind/unbind tests are sufficient to catch most header contract regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ttm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_uvmm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_uvmm.c

## Purpose
This file implements Nouveau's user-mode GPU virtual memory manager built on DRM GPUVM. It creates raw NVIF VMMs, tracks sparse regions, translates VM_BIND ioctls into scheduled map/unmap jobs, coordinates BO reservation fences, and remaps all GPUVAs during BO moves.

## Important APIs, Types, and Functions
External entry points are `nouveau_uvmm_ioctl_vm_init`, `nouveau_uvmm_ioctl_vm_bind`, `nouveau_uvmm_fini`, `nouveau_uvmm_bo_map_all`, and `nouveau_uvmm_bo_unmap_all`. Important internal types are `struct bind_job_op`, `enum vm_bind_op`, `struct nouveau_uvma`, `struct nouveau_uvma_region`, and `struct nouveau_uvmm_bind_job`. Core helpers manage raw VMM get/put/map/unmap/sparse refs, region maple-tree entries, GPUVA split/merge preparation, bind job submit/run/cleanup, and BO validation.

## Control Flow
VM init validates the kernel-managed range, allocates a `nouveau_uvmm`, creates a GPUVM reservation object, initializes a maple tree protected by the UVMM mutex, initializes DRM GPUVM, creates a raw NVIF VMM excluding the kernel-managed range, and stores it on the client. VM bind copies user operations and sync arrays, creates a `nouveau_job`, and submits it through `nouveau_sched`. Bind submit looks up GEM objects, obtains GPUVM BO wrappers, validates ranges and sparse region overlap, then under the UVMM lock creates DRM GPUVA ops, preallocates UVMA objects, reserves VMM page tables, validates BOs through `drm_exec`, links/unlinks GPUVAs under dma_resv locks, and arms fences. Scheduler run performs the actual NVIF VMM map/unmap calls. Cleanup frees GPUVA ops, drops BO/GEM references, releases sparse regions, signals completions, and marks the job done.

## State and Persistence Behavior
Persistent state includes `cli->uvmm.ptr`, DRM GPUVM VA interval state, NVIF raw VMM state, sparse regions in `region_mt`, per-UVMA page shift/kind/region links, GPUVM BO links under GEM reservations, and scheduled bind jobs with completion/kref lifetime. BO move callbacks invalidate GPUVAs and later remap them with the new `nouveau_mem`.

## Dependencies and Integration Points
It depends on DRM GPUVM, DRM exec, GEM reservation objects, Nouveau BO validation, `nouveau_sched`, `nouveau_job`, NVIF VMM raw methods, NVIF memory objects, and userspace `DRM_NOUVEAU_VM_BIND`/`VM_INIT` ioctls.

## Risks
Atomicity depends on holding the UVMM mutex until all failure paths are gone. Sparse region dirty/completion tracking prevents page-table operations from racing, but mistakes can deadlock or return wrong `-ENOENT`/`-ENOSPC`. Page-shift downgrade logic must match BO placement and VMM page capabilities. Cleanup must handle partially initialized `op->ops`, `op->reg`, `op->vm_bo`, and GEM references.

## Test Signals
Signals include VM init bounds tests, map/unmap/remap operations, sparse map/unmap conflict cases, async syncobj fences, BO eviction and remap callbacks, invalid user handles/ranges, concurrent binds, scheduler failure injection, and client teardown with live mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_uvmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_uvmm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_uvmm.h

## Purpose
This header defines the user-mode GPUVM data structures and public functions for Nouveau's DRM GPUVM based VM_BIND implementation.

## Important APIs, Types, and Functions
It defines `struct nouveau_uvmm`, `struct nouveau_uvma_region`, `struct nouveau_uvma`, `struct nouveau_uvmm_bind_job`, and `struct nouveau_uvmm_bind_job_args`. It declares VM init/bind ioctl handlers, UVMM teardown, BO map/unmap-all callbacks, conversion macros, and simple mutex lock/unlock helpers.

## Control Flow
The header has no executable control flow beyond inline locking helpers. It establishes ownership: `nouveau_uvmm` wraps `drm_gpuvm`, `nouveau_uvma` wraps `drm_gpuva`, and bind jobs embed `nouveau_job` for scheduler execution.

## State and Persistence Behavior
The structures persist the raw NVIF VMM, GPUVM object, sparse-region maple tree, UVMM mutex, sparse-region completion/dirty state, UVMA region/kind/page-shift metadata, and bind job operation list/completion/kref.

## Dependencies and Integration Points
It depends on DRM GPUVM and Nouveau driver, BO, memory, and scheduler declarations. It is included by BO move code, ioctl code, and UVMM implementation.

## Risks
The container macros require embedded object layout to remain stable. Lock helpers expose a single mutex that callers must use consistently with DRM GPUVA and GEM reservation locks.

## Test Signals
Build coverage, VM_BIND ioctl tests, BO move remap tests, and teardown with sparse regions verify the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_uvmm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vga.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vga.c

## Purpose
This file integrates Nouveau with VGA arbitration and vga_switcheroo. It controls legacy VGA decode registers, handles hybrid-GPU power switching, and wires hotplug reprobe behavior.

## Important APIs, Types, and Functions
Main entry points are `nouveau_vga_init` and `nouveau_vga_fini`. Internal switcheroo callbacks are `nouveau_switcheroo_set_state`, `nouveau_switcheroo_reprobe`, `nouveau_switcheroo_can_switch`, and `nouveau_vga_set_decode`.

## Control Flow
Initialization exits for non-PCI devices, registers the VGA client decode callback, skips switcheroo for Thunderbolt eGPUs, registers switcheroo callbacks, and optionally installs DSM runtime PM domain ops. Decode writes chipset-family-specific registers and reports which VGA resources remain decoded. Switcheroo ON resumes the PCI device and marks DRM switch state; OFF may skip Optimus/v1 DSM cases or call DSM and suspend.

## State and Persistence Behavior
State lives in PCI driver data, `dev->switch_power_state`, VGA arbiter registration, switcheroo client registration, and optional `drm->vga_pm_domain`. No file-local persistent state exists.

## Dependencies and Integration Points
It depends on Linux VGA arbiter, vga_switcheroo, DRM client hotplug, Nouveau ACPI DSM helpers, runtime PM ops, PCI detection, and NVIF MMIO writes.

## Risks
`can_switch` uses a racy `open_count` check by design. Wrong decode register selection can leave legacy VGA ranges exposed or disabled. Switcheroo state transitions must not fight Optimus DSM runtime PM behavior.

## Test Signals
Hybrid laptop switcheroo tests, runtime PM suspend/resume, VGA arbitration handoff, Thunderbolt eGPU probing, and display hotplug reprobe verify behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vga.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vga.h

## Purpose
This small header declares Nouveau VGA/switcheroo lifecycle hooks.

## Important APIs, Types, and Functions
It exposes `nouveau_vga_init` and `nouveau_vga_fini`.

## Control Flow
No executable flow exists in the header. Driver load/unload code calls these hooks around PCI VGA arbiter and switcheroo registration.

## State and Persistence Behavior
The header stores no state. The implementation mutates VGA arbiter registration, switcheroo registration, and optional runtime PM domain state.

## Dependencies and Integration Points
It is included by Nouveau driver initialization code and depends on `struct nouveau_drm` being visible to callers.

## Risks
The risk is signature drift or forgotten fini calls, which would leave VGA/switcheroo registrations active after device removal.

## Test Signals
Build coverage and PCI driver load/unload on VGA-capable systems validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vmm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vmm.c

## Purpose
This file manages the older per-client Nouveau VMM and per-BO VMA references. It allocates GPU virtual address ranges, maps/unmaps `nouveau_mem`, shares mappings for repeated BO/VMM pairs, and destroys associated SVMM state during VMM teardown.

## Important APIs, Types, and Functions
Entry points are `nouveau_vma_new`, `nouveau_vma_del`, `nouveau_vma_find`, `nouveau_vma_map`, `nouveau_vma_unmap`, `nouveau_vmm_init`, and `nouveau_vmm_fini`.

## Control Flow
`nouveau_vma_new` first reuses an existing BO/VMM VMA and bumps refs. Otherwise it allocates a VMA, links it to the BO list, and either reserves a lazy mapped range for non-system memory with matching page size or reserves PTEs for deferred mapping. On failure it deletes the partially built VMA. `nouveau_vma_del` decrements refs, puts the NVIF VMA if allocated, unlinks, and frees. VMM init creates an unmanaged NVIF VMM; fini tears down SVM and the NVIF VMM.

## State and Persistence Behavior
Per-VMA state includes VMM pointer, refcount, BO list link, GPU VA, mapped `nouveau_mem`, and optional fence pointer. Per-VMM state includes client pointer, NVIF VMM object, and optional SVMM.

## Dependencies and Integration Points
It depends on NVIF VMM get/put/map/unmap, Nouveau BO resource state, Nouveau memory mapping, and SVM teardown. It is used by fence memory mapping and classic BO GPU VA management.

## Risks
Reference counting must match all callers or GPU VA ranges leak or are freed early. The lazy mapping path assumes resource memory page size matches BO page preference. `nouveau_vma_unmap` only clears `mem`, so callers must ensure VMM address lifetime is separately released.

## Test Signals
Signals include repeated VMA lookup/ref/drop, BO move map/unmap, fence BO mapping on nv84+, VMM teardown with SVM enabled, and error injection in `nvif_vmm_get`/`nouveau_mem_map`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vmm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vmm.h

## Purpose
This header declares Nouveau's classic VMM and VMA structures and helper functions.

## Important APIs, Types, and Functions
It defines `struct nouveau_vma` with VMM pointer, refs, list link, address, mapped memory, and fence pointer. It defines `struct nouveau_vmm` with client, NVIF VMM, and SVMM pointers. It declares VMA find/new/del/map/unmap and VMM init/fini.

## Control Flow
The header has no executable flow; it describes the state contract used by `nouveau_vmm.c`, BO code, and fence code.

## State and Persistence Behavior
VMA state persists while a BO has a GPU VA in a client VMM. VMM state persists for the client lifetime and may own an SVM manager.

## Dependencies and Integration Points
It includes NVIF VMM declarations and forward-declares Nouveau BO and memory. It integrates with BO VMA lists, memory mapping, fence tracking, and SVM.

## Risks
Any layout changes affect container users and list management. Callers must preserve refcount discipline and avoid stale fence/mem pointers.

## Test Signals
Build coverage and BO/fence VMA allocation tests validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vmm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv04_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv04_fence.c

## Purpose
This file implements the earliest Nouveau fence backend using the NV_SW object reference register on NV04-era hardware.

## Important APIs, Types, and Functions
It defines private/channel fence wrappers and the public `nv04_fence_create`. Internal operations are `nv04_fence_emit`, `nv04_fence_read`, `nv04_fence_sync`, context new/delete, and destroy.

## Control Flow
Creation allocates `drm->fence` and installs context callbacks. Each channel context allocates a `nouveau_fence_chan`, sets emit/read/sync methods, and stores it on the channel. Emit waits for push space, writes the sequence through NV_SW method `0x0150`, and kicks. Read issues `NV04_NVSW_GET_REF` on the channel software object. Cross-channel sync is unsupported and returns `-ENODEV`.

## State and Persistence Behavior
Global state is only the allocated fence private object. Per-channel state is the generic fence context. Fence progress persists in the hardware/software reference value read from `chan->nvsw`.

## Dependencies and Integration Points
It depends on Nouveau push macros, `nouveau_fence_context_*`, NVIF object method calls, and the NV_SW class interface.

## Risks
No cross-channel sync means callers need fallback waits. Push space failures propagate from emit. Read uses `WARN_ON` on method failure and returns possibly stale `args.ref`.

## Test Signals
Signals include fence emit/read on NV04-class hardware, channel context teardown, unsupported sync handling, and push-buffer exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv04_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv10_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv10_fence.c

## Purpose
This file implements the NV10 fence backend using the user channel reference register and shared helpers later reused by NV17/NV50 fence implementations.

## Important APIs, Types, and Functions
Public helpers are `nv10_fence_emit`, `nv10_fence_read`, `nv10_fence_context_del`, `nv10_fence_destroy`, and `nv10_fence_create`. The private context creation function installs generic fence callbacks.

## Control Flow
Fence creation allocates `nv10_fence_priv`, sets destructor and context callbacks, and initializes the sequence lock. Per-channel context allocation creates `nv10_fence_chan`, initializes generic fence state, and sets emit/read/sync. Emit writes `SET_REFERENCE` with the sequence number and kicks. Read returns the `REFERENCE` register. Sync is unsupported on bare NV10 and returns `-ENODEV`.

## State and Persistence Behavior
`drm->fence` owns global fence private state, optional semaphore BO pointer used by later variants, a lock, and sequence counter. Per-channel contexts hold a semaphore object slot even if NV10 itself does not construct one.

## Dependencies and Integration Points
It depends on NVIF push006c, NV06E class methods, Nouveau fence context helpers, BO unpin/delete during destroy, and the shared `nv10_fence.h` structures.

## Risks
Destroy unconditionally calls `nouveau_bo_unpin_del(&priv->bo)`, so the helper must tolerate a NULL BO for base NV10. Cross-channel sync is unavailable. Register class assumptions must match channel user object class.

## Test Signals
Signals include NV10 fence sequence emission/readback, context allocation/free, module unload with NULL semaphore BO, and unsupported sync fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv10_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv10_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv10_fence.h

## Purpose
This header shares NV10-family fence private structures across NV10, NV17, and NV50 fence implementations.

## Important APIs, Types, and Functions
`struct nv10_fence_chan` embeds the generic fence channel and an NVIF semaphore object. `struct nv10_fence_priv` embeds the generic fence private object, semaphore BO pointer, spinlock, and sequence counter.

## Control Flow
No executable control flow exists. The structure layout lets later implementations reuse NV10 emit/read and generic context deletion while adding semaphore objects.

## State and Persistence Behavior
State covers per-channel semaphore object lifetime and global semaphore BO/sequence allocation for cross-channel synchronization on NV17/NV50.

## Dependencies and Integration Points
It includes `nouveau_fence.h` and `nouveau_bo.h` and is included by NV10, NV17, and NV50 fence code.

## Risks
Shared layout changes can break multiple chipset backends. The semaphore object is optional by variant, so cleanup must stay NULL-safe.

## Test Signals
Build all three backends and run fence context creation/destruction on NV10, NV17, and NV50-class devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv10_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv17_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv17_fence.c

## Purpose
This file extends NV10 fences with VRAM-backed semaphore synchronization for NV17-class channels.

## Important APIs, Types, and Functions
Public functions are `nv17_fence_sync`, `nv17_fence_resume`, and `nv17_fence_create`. It reuses `nv10_fence_emit`, `nv10_fence_read`, and `nv10_fence_context_del`.

## Control Flow
Creation allocates `nv10_fence_priv`, creates a one-page VRAM semaphore BO, installs resume and context callbacks, and clears the BO. Context creation constructs a DMA object covering the semaphore BO and sets sync to `nv17_fence_sync`. Sync tries to lock the client mutex, reserves two sequence increments under the spinlock, programs acquire/release semaphore operations into the previous channel and the target channel, kicks both, and unlocks.

## State and Persistence Behavior
The global sequence counter is persisted in the semaphore BO on resume via `nouveau_bo_wr32`. Per-channel semaphore DMA objects are destroyed with the channel context.

## Dependencies and Integration Points
It depends on NV176E semaphore methods, NVIF DMA object construction, Nouveau BO allocation/mapping, client mutex serialization, and generic fence context helpers.

## Risks
`mutex_trylock` can return `-EBUSY`, so callers must tolerate retry. The function returns 0 even after push programming errors are stored in `ret`, which looks suspicious and can hide sync failures. Semaphore BO placement must be valid VRAM.

## Test Signals
Signals include cross-channel fence sync, suspend/resume sequence restoration, push failure injection, client mutex contention, and semaphore BO allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv17_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv50_display.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv50_display.h

## Purpose
This header declares the NV50 display creation entry point and includes display/register dependencies needed by NV50-era display and fence code.

## Important APIs, Types, and Functions
It declares `nv50_display_create(struct drm_device *)`.

## Control Flow
There is no executable flow. The declaration allows higher-level driver code to instantiate NV50 display support.

## State and Persistence Behavior
The header stores no state. The implementation creates display state elsewhere.

## Dependencies and Integration Points
It includes `nouveau_display.h` and `nouveau_reg.h`. Fence files include it for chipset-era shared declarations even though they primarily handle fences.

## Risks
The risk is limited to signature drift and unnecessary include coupling between display and fence code.

## Test Signals
Build coverage and NV50 display initialization tests catch interface breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv50_display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv50_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv50_fence.c

## Purpose
This file provides the NV50 fence backend, mostly reusing NV17 semaphore logic with the NV50 DMA object class variant.

## Important APIs, Types, and Functions
Main entry point is `nv50_fence_create`. Internal context creation constructs the semaphore DMA object and installs NV10 emit/read plus NV17 sync callbacks.

## Control Flow
Creation allocates `nv10_fence_priv`, sets destructor/resume/context callbacks, initializes the lock, creates a one-page VRAM semaphore BO, and clears it. Context creation allocates a channel fence context, initializes generic fence state, points emit/read/sync to NV10/NV17 helpers, and constructs `NvSema` with `NV_DMA_IN_MEMORY` targeting the semaphore BO.

## State and Persistence Behavior
Global state is the semaphore BO and sequence lock in `drm->fence`. Per-channel state is `nv10_fence_chan` plus an NVIF semaphore object.

## Dependencies and Integration Points
It depends on NVIF class and DMA object APIs, Nouveau BO mapping, NV10/NV17 fence helpers, and generic fence infrastructure.

## Risks
Semaphore BO allocation failure must destroy partially initialized state. The DMA object range is based on the BO resource start and size, so incorrect placement would break sync. Error handling delegates to shared NV10 cleanup.

## Test Signals
Signals include NV50 fence emit/read, cross-channel sync, context construction failure, suspend/resume through NV17 resume helper, and driver unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv50_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv84_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv84_fence.c

## Purpose
This file implements the NV84+ fence backend using per-channel semaphore slots in a shared BO and GPU virtual mappings rather than the older DMA object approach.

## Important APIs, Types, and Functions
Public functions include `nv84_fence_context_new` and `nv84_fence_create`. Internal helpers emit and wait on 32-bit semaphore values, compute channel IDs, read/write fence slots, suspend/resume slot contents, and destroy contexts/private state.

## Control Flow
Creation allocates `nv84_fence_priv`, chooses VRAM if available or coherent GART fallback, allocates a BO sized at 16 bytes per channel, and installs uevent-capable fence callbacks. Context creation allocates `nv84_fence_chan`, initializes callbacks, seeds the sequence from the BO slot, maps the fence BO into the channel VMM under a mutex, and stores the VMA. Emit writes a release method to the current channel's slot. Sync writes an acquire operation against the previous channel's slot. Context deletion writes the final sequence, drops the VMA, and frees the context.

## State and Persistence Behavior
State includes the shared fence BO, per-channel 16-byte slots, per-context VMA references, current sequence values, a mutex protecting VMA creation/deletion, and optional suspend snapshot array.

## Dependencies and Integration Points
It depends on Nouveau VMM/VMA helpers, BO read/write/mapping, NV826F push methods, channel runlist/chid base, and generic fence infrastructure.

## Risks
System-memory fallback must be coherent or fence polling can lose updates. Channel ID slot computation must match runlist layout. Suspend snapshot allocation failure reports false and may prevent safe suspend. VMA lifetime must match channel context lifetime.

## Test Signals
Signals include fence signaling on VRAM and coherent GART fallback, cross-channel sync, suspend/resume slot preservation, runlist channel ID correctness, and context teardown under active fences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv84_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvc0_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvc0_fence.c

## Purpose
This file adapts the NV84 fence backend to Fermi/NVC0 semaphore method encodings.

## Important APIs, Types, and Functions
Main entry point is `nvc0_fence_create`. Internal helpers `nvc0_fence_emit32`, `nvc0_fence_sync32`, and `nvc0_fence_context_new` override the NV84 per-channel emit/sync function pointers.

## Control Flow
Creation delegates to `nv84_fence_create`, then replaces the global context-new hook. Context creation delegates to `nv84_fence_context_new` and swaps the per-context `emit32` and `sync32` methods. Emit programs NV906F release with WFI and 16-byte release size; sync programs NV906F acquire greater-or-equal with acquire switch enabled.

## State and Persistence Behavior
State is inherited from NV84: shared fence BO, per-channel slots, VMA refs, and suspend data. This file only changes method encodings.

## Dependencies and Integration Points
It depends on NV906F push methods, NV84 fence structures/functions, and generic Nouveau fence infrastructure.

## Risks
Incorrect method flags can cause fences to signal before work is complete or fail to wait. Since state is inherited, NV84 BO and VMA lifecycle bugs affect NVC0 too.

## Test Signals
Signals include NVC0 fence release/acquire ordering, non-stall interrupt behavior, cross-channel synchronization, and regression tests shared with NV84.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvc0_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/Kbuild

## Purpose
This Kbuild fragment lists the NVIF object files included in the Nouveau build.

## Important APIs, Types, and Functions
It populates `nvif-y` with object, client, connector, device, display, driver, event, FIFO, head, memory, MMU, output, timer, VMM, channel class, and usermode class object files.

## Control Flow
There is no runtime control flow. The build system includes this fragment to compile the NVIF layer into the driver.

## State and Persistence Behavior
No runtime state exists. Build state is the ordered object list assigned to `nvif-y`.

## Dependencies and Integration Points
It is consumed by the parent Nouveau Kbuild and mirrors source modules under `nvif/`.

## Risks
Missing an object here causes unresolved symbols or silent feature loss. Adding a source without updating the fragment will not compile it.

## Test Signals
Kernel build coverage and link-time symbol checks validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chan.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chan.c

## Purpose
This file implements generic NVIF GPFIFO/push-buffer channel mechanics shared by class-specific channel implementations.

## Important APIs, Types, and Functions
Public functions are `nvif_chan_gpfifo_post`, `nvif_chan_gpfifo_push`, `nvif_chan_gpfifo_wait`, `nvif_chan_gpfifo_ctor`, and `nvif_chan_dma_wait`. Internal push callbacks handle kick and wait integration.

## Control Flow
Push kick optionally posts a semaphore marker, computes the push-buffer offset, emits a GPFIFO entry, and kicks the channel. Wait first reserves push-buffer space, then polls the hardware GET pointer for GPFIFO free space with a timeout. DMA wait wraps the push buffer when the GET pointer advances and updates `push->bgn/cur/end`.

## State and Persistence Behavior
State lives in mapped userd, GPFIFO, push buffer pointers, cached free count, current GPFIFO index, push address, and function table pointers.

## Dependencies and Integration Points
It depends on class-specific `nvif_chan_func` methods, NVIF mapped IO helpers, push macros, and udelay polling. `chan506f`, `chan906f`, and `chanc36f` provide concrete functions.

## Risks
Pointer arithmetic assumes mapped push memory and sizes are correct. Timeout loops are busy waits. Incorrect post-size accounting can overwrite push or GPFIFO space.

## Test Signals
Signals include push-buffer wraparound, GPFIFO full/empty behavior, semaphore post paths, timeout handling, and class-specific channel constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chan506f.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chan506f.c

## Purpose
This file implements NV50-style 506F channel GPFIFO operations.

## Important APIs, Types, and Functions
It provides `nvif_chan506f_gpfifo_kick`, `nvif_chan506f_gpfifo_push`, `nvif_chan506f_ctor`, and static GET-pointer readers for GPFIFO and push buffer.

## Control Flow
Push writes a two-dword GPFIFO entry with address, main/non-main flag, size, and no-prefetch bit, advances the ring pointer, decrements free entries, and clamps push end when full. Kick executes a write memory barrier and writes PUT to userd offset `0x8c`. Push GET reads top-level GET registers when valid and caches the derived push offset.

## State and Persistence Behavior
State is in `chan->gpfifo.cur/free/max`, mapped GPFIFO/userd memory, and cached `push->hw.get`.

## Dependencies and Integration Points
It plugs into the generic channel constructor through a `nvif_chan_func` table and is reused by newer class implementations.

## Risks
Register offsets and GPFIFO bit fields are class-specific. Missing barriers can let the GPU see stale entries. Full-ring handling relies on generic wait code.

## Test Signals
Signals include GPFIFO push/kick on NV50 channels, no-prefetch entries, top-level GET cache updates, and ring-full wait recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chan506f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chan906f.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chan906f.c

## Purpose
This file implements 906F channel behavior, adding semaphore-backed GPFIFO post/read state to the 506F push format.

## Important APIs, Types, and Functions
Public functions include `nvif_chan906f_gpfifo_post`, `nvif_chan906f_gpfifo_read_get`, `nvif_chan906f_read_get`, `nvif_chan906f_ctor_`, and `nvif_chan906f_ctor`. Internal `nvif_chan906f_sem_release` emits an NV906F semaphore release.

## Control Flow
The constructor delegates to generic GPFIFO setup, then records mapped semaphore memory and address. Posting writes a packed GPFIFO pointer and push-buffer pointer to the semaphore through channel methods. GET readers decode the same semaphore word. The function table reuses 506F push/kick while adding post and sem release hooks.

## State and Persistence Behavior
State persists in `chan->sema`, GPFIFO pointer bits, push-buffer pointer bits, and class function table callbacks.

## Dependencies and Integration Points
It depends on NV906F method encodings, generic channel code, 506F GPFIFO push/kick, and mapped semaphore memory used by newer channels.

## Risks
The fixed bit split limits GPFIFO and push-buffer sizes. Incorrect semaphore payload packing breaks both free-space accounting and post synchronization.

## Test Signals
Signals include semaphore post updates, GET pointer decoding, constructor setup with mapped sema memory, and push wait behavior at size limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chan906f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chanc36f.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chanc36f.c

## Purpose
This file implements C36F/Hopper-era channel behavior using usermode doorbells and updated semaphore method encodings.

## Important APIs, Types, and Functions
Main entry point is `nvif_chanc36f_ctor`. Internal helpers are `nvif_chanc36f_gpfifo_kick` and `nvif_chanc36f_sem_release`; the function table reuses 906F GET/post readers and 506F GPFIFO entry format.

## Control Flow
Constructor delegates to 906F setup with the C36F function table, then records usermode object and doorbell token. Kick writes the GPFIFO PUT, uses a barrier and readback to flush BAR1 writes to video memory, then rings the usermode doorbell. Semaphore release emits C36F SEM_ADDR/PAYLOAD/EXECUTE methods.

## State and Persistence Behavior
State includes mapped userd/sema/push/GPFIFO memory, a usermode object pointer, and doorbell token.

## Dependencies and Integration Points
It depends on NVIF usermode doorbell functions, C36F method definitions, and generic/906F channel support.

## Risks
Ordering is critical: doorbell before BAR1 flush can make the GPU read incomplete GPFIFO state. Doorbell tokens must match channel allocation.

## Test Signals
Signals include doorbell submission, BAR1 flush ordering, semaphore post, C36F channel construction, and timeout behavior under full rings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chanc36f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/client.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/client.c

## Purpose
This file implements NVIF client construction, destruction, suspend, and resume wrappers.

## Important APIs, Types, and Functions
Public functions are `nvif_client_ctor`, `nvif_client_dtor`, `nvif_client_suspend`, and `nvif_client_resume`.

## Control Flow
Constructor creates an `NVIF_CLASS_CLIENT` object either as a child of a parent client or as the root client, copies the driver pointer, marks the object handle as root, and stores the client backpointer. Suspend/resume delegate to the selected NVIF driver backend using the root object private pointer. Destructor destroys the NVIF object and clears the driver pointer.

## State and Persistence Behavior
State includes the client NVIF object, driver vtable pointer, object handle, object client backpointer, and backend private pointer.

## Dependencies and Integration Points
It depends on NVIF object construction, the NVIF driver interface, and client class ABI structures. It is used by `nvif_driver_init` and nested client creation.

## Risks
Root client construction uses `parent == client` special handling. Driver pointer propagation must be correct or later ioctls/suspend calls dereference NULL or the wrong backend.

## Test Signals
Signals include root and child client creation, suspend/resume delegation, destructor idempotence, and backend init failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/conn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/conn.c

## Purpose
This file wraps NVIF display connector objects and hotplug event creation.

## Important APIs, Types, and Functions
Public functions are `nvif_conn_ctor`, `nvif_conn_dtor`, and `nvif_conn_event_ctor`.

## Control Flow
Connector construction sends an `NVIF_CLASS_CONN` new request with an ID, stores the ID, and translates firmware/kernel connector type values into NVIF connector info enums. Event construction builds an event argument with requested HPD types and creates an event object tied to the connector ID.

## State and Persistence Behavior
State lives in the `nvif_conn` object, connector ID, translated connector type, and optional event object.

## Dependencies and Integration Points
It depends on NVIF display objects, event construction, connector class ABI, and display hotplug handling.

## Risks
Unknown connector types are silently left at default values. Event type masks must match backend-supported HPD bits.

## Test Signals
Signals include connector enumeration, type translation, HPD event creation/block/allow, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/device.c

## Purpose
This file wraps the root NVIF device object, device info query, MMIO mapping, device time reads, usermode teardown, and runlist cache cleanup.

## Important APIs, Types, and Functions
Public functions are `nvif_device_ctor`, `nvif_device_dtor`, `nvif_device_map`, and `nvif_device_time`.

## Control Flow
Constructor creates the device object, initializes runlist/usermode fields, then queries `NV_DEVICE_V0_INFO` into `device->info`. Time reads either call the usermode fast path or issue `NV_DEVICE_V0_TIME`. Destructor destroys usermode state, frees runlist cache, and destroys the device object.

## State and Persistence Behavior
State includes device object mapping, `device->info`, optional runlist array, runlist count, and optional usermode object/function table.

## Dependencies and Integration Points
It depends on NVIF client/object APIs, device class methods, usermode helpers, and FIFO runlist discovery.

## Risks
Time fallback warns on method failure but still returns the possibly unchanged time. Constructor failure after object creation must be handled by callers via destructor.

## Test Signals
Signals include device construction/info query, device map/unmap, usermode and non-usermode time reads, runlist cache allocation/free, and device teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/disp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/disp.c

## Purpose
This file constructs and destroys NVIF display objects across supported display class generations.

## Important APIs, Types, and Functions
Public functions are `nvif_disp_ctor` and `nvif_disp_dtor`.

## Control Flow
Constructor selects a supported display class from newest to oldest using `nvif_sclass`, creates the display object, then stores connector, output, and head masks returned by the backend. Destructor destroys the object.

## State and Persistence Behavior
State includes the display NVIF object and enumeration masks for connectors, outputs, and heads.

## Dependencies and Integration Points
It depends on NVIF device/object APIs, display class IDs, display ABI structures, and later connector/output/head constructors.

## Risks
Unsupported requested class returns an error before object construction. Mask interpretation must match subsequent enumeration code.

## Test Signals
Signals include display class selection on multiple GPU generations, mask correctness, object destruction, and failure for unsupported classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/disp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/driver.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/driver.c

## Purpose
This file initializes the NVIF driver backend and root client object.

## Important APIs, Types, and Functions
The single public function is `nvif_driver_init`.

## Control Flow
Initialization selects the built-in `nvif_driver_nvkm` backend, calls its `init` hook with name, device, cfg, and debug strings to obtain backend private state, then constructs the root NVIF client.

## State and Persistence Behavior
State is stored in the provided `nvif_client`: driver vtable pointer and object private pointer from backend initialization.

## Dependencies and Integration Points
It depends on NVIF client construction and the NVKM backend driver implementation.

## Risks
The `drv` parameter is currently ignored, so only the NVKM backend is selected. If client construction fails after backend init, cleanup responsibilities must be handled by callers/backend.

## Test Signals
Signals include driver init success/failure, root client construction, debug/cfg option propagation, and later ioctl dispatch through the selected backend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/event.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/event.c

## Purpose
This file wraps NVIF event object creation, block/allow control, and destruction.

## Important APIs, Types, and Functions
Public functions are `nvif_event_ctor_`, `nvif_event_block`, `nvif_event_allow`, and `nvif_event_dtor`.

## Control Flow
Constructor fills default event args when none are supplied, sets version and wait mode, creates an `NVIF_CLASS_EVENT` object, and stores the callback function. Block and allow issue event methods only if the event is constructed. Destructor destroys the event object.

## State and Persistence Behavior
State lives in the event object and callback pointer. Backend state controls whether notifications are blocked or allowed.

## Dependencies and Integration Points
It depends on NVIF object method APIs, event class ABI, and object construction. Connector/head/SVM code builds on this wrapper.

## Risks
Callbacks are stored but invoked by backend event routing elsewhere; stale event objects can call stale callbacks if not blocked/destroyed. Wait-mode behavior affects list insertion on the NVKM side.

## Test Signals
Signals include event construction with custom/default args, block/allow transitions, destruction while blocked/allowed, and HPD/vblank/SVM event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/fifo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/fifo.c

## Purpose
This file queries and caches FIFO runlist-to-engine mappings for a device.

## Important APIs, Types, and Functions
Public function is `nvif_fifo_runlist`. Internal `nvif_fifo_runlists` performs the device info query and allocation.

## Control Flow
The first runlist request allocates a query structure, asks `NV_DEVICE_V0_INFO` for host runlists and per-runlist engine masks, computes the number of runlists, allocates `device->runlist`, and caches engine masks. `nvif_fifo_runlist` then returns a bitmask of runlists containing the requested engine bit.

## State and Persistence Behavior
State persists in `device->runlists` and the allocated `device->runlist` array until device destruction.

## Dependencies and Integration Points
It depends on NVIF device info methods and is used by channel/runlist setup to select compatible runlists.

## Risks
The fixed stack of 64 runlist entries must cover backend reports. Query failure returns an empty mask. Cached results are not refreshed after creation.

## Test Signals
Signals include runlist discovery on multi-engine GPUs, query failure paths, device destructor freeing, and engine-to-runlist selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/head.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/head.c

## Purpose
This file wraps NVIF display head objects and vblank event creation.

## Important APIs, Types, and Functions
Public functions are `nvif_head_ctor`, `nvif_head_dtor`, and `nvif_head_vblank_event_ctor`.

## Control Flow
Head construction creates an `NVIF_CLASS_HEAD` object for a display head ID. Vblank event construction creates an event object for that head ID with caller-selected wait behavior. Destructor destroys the head object.

## State and Persistence Behavior
State is the head NVIF object and any event object managed by callers.

## Dependencies and Integration Points
It depends on NVIF display/object/event APIs and the display head class ABI. DRM/KMS vblank handling uses the event wrapper.

## Risks
Invalid head IDs fail at object construction. Event wait semantics must match the caller's interrupt handling.

## Test Signals
Signals include head enumeration, vblank event delivery/block/allow, and teardown during display disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/head.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/mem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/mem.c

## Purpose
This file constructs, maps, and destroys NVIF memory objects selected from MMU-advertised memory types.

## Important APIs, Types, and Functions
Public functions are `nvif_mem_ctor`, `nvif_mem_ctor_type`, `nvif_mem_ctor_map`, and `nvif_mem_dtor`.

## Control Flow
`nvif_mem_ctor` scans MMU memory types for one containing all requested flags and delegates to `nvif_mem_ctor_type`. The typed constructor builds variable-size args on stack or heap, creates the memory object, and records returned type/page/address/size. `nvif_mem_ctor_map` requests mappable memory and maps the object, destroying it on map failure.

## State and Persistence Behavior
State persists in `struct nvif_mem`: object handle, type flags, page shift, address, size, and optional object map.

## Dependencies and Integration Points
It depends on NVIF MMU type discovery, memory class constructors, object mapping, and callers such as TTM/Nouveau memory allocation.

## Risks
Type matching picks the last matching type if multiple matches continue while `ret` is nonzero. Variable argument sizing must avoid stack overflow and preserve backend data. Map failure cleanup must prevent leaked memory objects.

## Test Signals
Signals include VRAM/host/mappable/coherent type allocation, invalid type rejection, map failure cleanup, and constructor argument size boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/mmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/mmu.c

## Purpose
This file constructs and destroys the NVIF MMU object and discovers supported heaps, memory types, compression kinds, and memory object class.

## Important APIs, Types, and Functions
Public functions are `nvif_mmu_ctor` and `nvif_mmu_dtor`.

## Control Flow
Constructor creates the MMU object, records DMA bits and counts, selects a supported memory class, allocates heap/type/kind arrays, queries each heap and type, translates type booleans into `NVIF_MEM_*` flags, optionally queries kind data, and tears down on failure. Destructor frees arrays and destroys the object if constructed.

## State and Persistence Behavior
State includes `dmabits`, memory object class, heap/type/kind arrays, kind inversion value, and object handle. It persists for the client/device lifetime.

## Dependencies and Integration Points
It depends on NVIF object methods, MMU class ABI, memory class IDs, and memory constructors that consume type/kind metadata.

## Risks
Partial allocation failure must free all arrays. Backend count values drive allocation sizes. Kind query handling must preserve `kind_inv` even when there are no kinds.

## Test Signals
Signals include MMU construction on NV04/NV50/GF100 class backends, type flag correctness, kind discovery, low-memory failure injection, and destructor idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/object.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/object.c

## Purpose
This file is the core NVIF object wrapper. It formats ioctl packets, creates/destroys objects, invokes methods, queries supported child classes, and maps/unmaps backend objects.

## Important APIs, Types, and Functions
Public functions include `nvif_object_ioctl`, `nvif_object_ctor`, `nvif_object_dtor`, `nvif_object_mthd`, `nvif_object_sclass_get`, `nvif_object_sclass_put`, `nvif_object_map`, `nvif_object_unmap`, `nvif_object_map_handle`, and `nvif_object_unmap_handle`.

## Control Flow
Ioctl fills the target object handle and delegates to the client driver. Constructor initializes local object fields and, for non-root objects, sends a NEW ioctl through the parent and stores returned private data/client pointer. Method and map helpers allocate stack/heap packets as needed, copy arguments in/out, and call ioctl. Destructor unmaps first, sends DEL, and clears the client pointer.

## State and Persistence Behavior
Object state includes name, handle, class, parent/root relation, client pointer, backend private pointer, and optional map pointer/size. Mapping can be direct virtual address or an IO mapping returned by the driver.

## Dependencies and Integration Points
It depends on NVIF ioctl ABI, NVIF client driver vtable, object handle rules, and all higher-level NVIF wrappers.

## Risks
Handle assignment and root-object special cases are central to correctness. Map failure must unmap backend handles. Argument size overflow checks prevent undersized ioctl buffers. Destructor must be safe on partially constructed objects.

## Test Signals
Signals include object create/delete, method round trips, class queries, IO and VA mapping paths, constructor failures, and repeated destructor calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/outp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/outp.c

## Purpose
This file wraps NVIF display output objects and exposes methods for DisplayPort, HDMI, LVDS, backlight, output-resource acquisition, inherited state, load detection, EDID, and detection.

## Important APIs, Types, and Functions
Key APIs include `nvif_outp_ctor/dtor`, DP MST/SST/drive/train/rates/AUX/power helpers, HDMI/infoframe/HDA ELD helpers, LVDS/backlight helpers, acquire/release helpers, inherit helpers, `nvif_outp_load_detect`, `nvif_outp_edid_get`, and `nvif_outp_detect`.

## Control Flow
Constructor creates an output object, translates backend type/protocol data into NVIF info fields, records heads/DDC/connector, and initializes OR state. Most helpers build a versioned method struct, call `nvif_mthd` or `nvif_object_mthd`, log errors, and return backend status or data. Acquire/inherit update `outp->or` from backend responses; release clears it.

## State and Persistence Behavior
Persistent state includes output ID, type/protocol capabilities, DP link info, head/DDC/connector masks, and current OR ID/link. EDID allocation returns a caller-owned buffer.

## Dependencies and Integration Points
It depends on NVIF display output ABI, DRM DP constants, display/KMS code, AUX/I2C/EDID code, and audio/infoframe paths.

## Risks
Many helpers trust caller-provided buffer sizes and protocol compatibility. AUX transfer copies back only the original requested size even if backend changes `args.size`. Constructor destroys the object on unknown type/protocol. OR state must be released on modeset failures.

## Test Signals
Signals include DP link training/MST VCPI, AUX transactions, EDID reads, HDMI infoframes/audio ELD, backlight get/set, output acquire/release, load detect, and protocol inheritance during takeover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/outp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/timer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/timer.c

## Purpose
This file provides a small helper for polling elapsed GPU device time with timeout and stalled-clock detection.

## Important APIs, Types, and Functions
Public functions are `nvif_timer_wait_init` and `nvif_timer_wait_test`.

## Control Flow
Initialization stores the device, nanosecond limit, and resets read count. Each test reads `nvif_device_time`, initializes the baseline on first read, detects repeated identical timestamps for up to 16 reads, checks elapsed time against the limit, and returns elapsed time or `-ETIMEDOUT`.

## State and Persistence Behavior
State lives in caller-provided `struct nvif_timer_wait`: device, limit, first time, last time, and repeated-read count.

## Dependencies and Integration Points
It depends on `nvif_device_time` and is used by polling loops that prefer GPU time over CPU time.

## Risks
If device time stalls, timeout is triggered after repeated reads. If time wraps or is non-monotonic, elapsed comparisons may be wrong depending on counter width.

## Test Signals
Signals include normal elapsed polling, forced stalled time, timeout limit behavior, and usermode vs method-backed device time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/user.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/user.c

## Purpose
This file constructs and destroys NVIF usermode objects used for fast device time reads and doorbell submission on newer GPUs.

## Important APIs, Types, and Functions
Public functions are `nvif_user_ctor` and `nvif_user_dtor`.

## Control Flow
Constructor returns early if usermode is already available, selects a supported usermode class from Blackwell through Volta, creates the object, maps it, and stores the class function table. Destructor destroys the usermode object and clears the function pointer if present.

## State and Persistence Behavior
State persists in `device->user.object`, mapped object memory, and `device->user.func`.

## Dependencies and Integration Points
It depends on NVIF object class selection, usermode class IDs, object mapping, and `nvif_userc361` function implementation. Channel C36F code uses doorbells from this interface.

## Risks
The return value from `nvif_object_map` is ignored, so a function table can be installed even if mapping failed. Unsupported classes return the class-selection error.

## Test Signals
Signals include usermode construction on Volta+ GPUs, mapping failure injection, device time via usermode, C36F doorbell submission, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/userc361.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/userc361.c

## Purpose
This file implements the C361 usermode function table for time reads and doorbell writes.

## Important APIs, Types, and Functions
It defines `nvif_userc361_time`, `nvif_userc361_doorbell`, and exports `const struct nvif_user_func nvif_userc361`.

## Control Flow
Time reading loops until the high 32-bit timer value is stable around the low read, then returns a 64-bit timestamp. Doorbell writes the token to offset `0x90` in the mapped usermode object.

## State and Persistence Behavior
No independent state exists. It operates on the mapped `nvif_user` object.

## Dependencies and Integration Points
It depends on NVIF mapped IO helpers and is selected by `nvif_user_ctor` for Volta and newer usermode classes.

## Risks
Register offsets are class-specific. If the mapped object is invalid, reads/writes fail at the MMIO abstraction level. Time read can spin if high register is unstable, though the loop is normally short.

## Test Signals
Signals include monotonic time reads, high/low rollover correctness, and doorbell-triggered channel submissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/userc361.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/vmm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/vmm.c

## Purpose
This file wraps NVIF virtual memory manager objects and provides classic and raw get/put/map/unmap/sparse operations.

## Important APIs, Types, and Functions
Public APIs include `nvif_vmm_ctor`, `nvif_vmm_dtor`, `nvif_vmm_get`, `nvif_vmm_put`, `nvif_vmm_map`, `nvif_vmm_unmap`, `nvif_vmm_raw_get`, `nvif_vmm_raw_put`, `nvif_vmm_raw_map`, `nvif_vmm_raw_unmap`, and `nvif_vmm_raw_sparse`.

## Control Flow
Constructor builds a VMM object with type UNMANAGED, MANAGED, or RAW, records start/limit/page count, allocates page capability descriptors, and queries each page type. Classic get/put/map/unmap use versioned VMM methods and `struct nvif_vma`. Raw helpers issue `NVIF_VMM_V0_RAW` with explicit address, size, shift, memory handle, sparse, and argument pointers.

## State and Persistence Behavior
State persists in the VMM object, start/limit, page capability array, and allocated VMAs returned to callers. Destructor frees page metadata and destroys the object.

## Dependencies and Integration Points
It depends on NVIF MMU object construction, memory object handles, VMM class ABI, and callers in classic VMM, SVM, UVMM, and TTM paths.

## Risks
Raw map passes a kernel pointer value in the ioctl arguments, so backend expectations must match in-kernel NVIF usage. Constructor failure must tear down partially allocated objects. Page capability selection affects UVMM page-shift decisions.

## Test Signals
Signals include VMM construction for all types, page capability enumeration, get/put/map/unmap success and failure, raw sparse refs, and UVMM/SVM raw mapping flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/vmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/Kbuild

## Purpose
This Kbuild fragment includes the NVKM subtrees that make up Nouveau's kernel-mode hardware backend.

## Important APIs, Types, and Functions
It includes Kbuild fragments for `core`, `nvfw`, `falcon`, `subdev`, and `engine`.

## Control Flow
There is no runtime flow. The build system expands these included fragments to populate NVKM object lists.

## State and Persistence Behavior
No runtime state exists. Build state is the set of included subdirectories.

## Dependencies and Integration Points
It is included by Nouveau's parent Kbuild and aggregates NVKM backend source selection.

## Risks
Missing or misordered includes can omit whole backend classes or break object list definitions.

## Test Signals
Kernel build and link coverage validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/Kbuild

## Purpose
This Kbuild fragment lists the NVKM core object files compiled into Nouveau.

## Important APIs, Types, and Functions
It assigns `nvkm-y` entries for client, engine, enum, event, firmware, gpuobj, interrupt, ioctl, memory, memory manager, object, proxy object, option parsing, RAM hash table, subdevice, and user event support.

## Control Flow
There is no runtime control flow. It controls build composition for NVKM core services.

## State and Persistence Behavior
No runtime state exists. Build state is the object list.

## Dependencies and Integration Points
It is included by `nvkm/Kbuild`; many listed objects are prerequisites for subdev and engine code.

## Risks
Omitting a core object causes link errors or missing backend functionality. Adding a source without Kbuild integration leaves code unused.

## Test Signals
Build and link coverage are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/client.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/client.c

## Purpose
This file implements NVKM client objects, including root client creation and user-visible child client construction.

## Important APIs, Types, and Functions
Main public function is `nvkm_client_new`. Internal pieces include `nvkm_uclient_new`, `nvkm_client_child_get`, `nvkm_client_child_new`, and `nvkm_client_dtor`.

## Control Flow
`nvkm_client_new` allocates a client, constructs its root NVKM object, records name/device/debug options, initializes object tree and memory lists, and stores the event callback. The user-client class constructor unpacks NVIF args, creates a child client sharing the parent device/event callback, inherits debug level, and returns it as an object. Child class lookup exposes client and device classes.

## State and Persistence Behavior
State includes client name, device handle, debug level, root object tree, object lock, event callback, user memory list, and lock.

## Dependencies and Integration Points
It depends on NVKM object construction, option parsing, NVIF client/device ABI, and ioctl child-class enumeration.

## Risks
Child client creation must preserve parent event and debug state. Object tree locking is initialized here and later used by ioctl/object lookup. Invalid unpacked args reject construction.

## Test Signals
Signals include root client creation, nested client creation through NVIF, object tree insert/delete, debug option parsing, and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/engine.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/engine.c

## Purpose
This file provides the common NVKM engine wrapper around subdevice lifecycle, interrupts, reset, tile updates, and references.

## Important APIs, Types, and Functions
Public functions include `nvkm_engine_ctor`, `nvkm_engine_new_`, `nvkm_engine_ref`, `nvkm_engine_unref`, `nvkm_engine_reset`, `nvkm_engine_tile`, and `nvkm_engine_chsw_load`. It exposes `const struct nvkm_subdev_func nvkm_engine`.

## Control Flow
Engine construction initializes the embedded subdevice, sets the use refcount to zero, honors config options that can disable the engine, and initializes the lock. Subdevice callbacks delegate preinit/oneinit/init/fini/intr/info/dtor to engine-specific function pointers. Init also reapplies framebuffer tile regions. Reset calls engine reset if present or power-cycles the subdevice.

## State and Persistence Behavior
State includes the engine function table, embedded subdev, lock, and subdev use refcount. Tile state comes from framebuffer subdev and is programmed into engines.

## Dependencies and Integration Points
It depends on NVKM subdev, device option parsing, framebuffer tiling, and engine-specific implementations. Ioctl class creation may take engine references.

## Risks
Config-disabled engines return `-ENODEV`. Fallback reset can disrupt state if engine-specific reset is required. Tile replay assumes framebuffer tile data is initialized.

## Test Signals
Signals include engine init/fini/reset, config option disablement, interrupt delegation, tile updates, ref/unref behavior, and engine-specific oneinit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/engine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/enum.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/enum.c

## Purpose
This file provides small formatting helpers for NVKM enum and bitfield tables.

## Important APIs, Types, and Functions
Public functions are `nvkm_enum_find` and `nvkm_snprintbf`.

## Control Flow
`nvkm_enum_find` linearly scans a sentinel-terminated enum table for a matching value. `nvkm_snprintbf` scans a bitfield table and appends names for set bits into a caller buffer separated by spaces, then null-terminates.

## State and Persistence Behavior
No persistent state exists.

## Dependencies and Integration Points
It depends on NVKM enum/bitfield table definitions and is used by logging/debug paths.

## Risks
`nvkm_snprintbf` only prints known set bits and ignores unknown bits. Buffer size handling relies on `scnprintf`; output truncation is possible but null-terminated.

## Test Signals
Signals include table lookup hits/misses, bitfield formatting with multiple bits, empty values, and small buffer truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/enum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/event.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/event.c

## Purpose
This file implements NVKM kernel event notification management. It tracks enabled event references per index/type, maintains notifier lists, gates hardware init/fini for events, and dispatches callbacks.

## Important APIs, Types, and Functions
Public functions include `__nvkm_event_init`, `nvkm_event_fini`, `nvkm_event_ntfy_add`, `nvkm_event_ntfy_del`, `nvkm_event_ntfy_allow`, `nvkm_event_ntfy_block`, `nvkm_event_ntfy`, and `nvkm_event_ntfy_valid`.

## Control Flow
Event init allocates a reference-count array sized by index and type count. Allowing a notifier atomically changes allowed state, increments per-type refs under `refs_lock`, calls backend init on first ref, and inserts wait-mode notifiers. Blocking reverses this and may remove wait-mode notifiers. Dispatch walks the notifier list under read lock and calls matching allowed callbacks.

## State and Persistence Behavior
State includes backend event function table, subdev pointer, refs array, notifier list, list lock, refs lock, notifier allowed/running flags, id, bits, wait flag, and callback.

## Dependencies and Integration Points
It depends on NVKM subdev logging and backend event init/fini functions. NVKM user events and NVIF events build on this layer.

## Risks
Reference counting must stay balanced or hardware events remain enabled/disabled incorrectly. Callback dispatch occurs under read lock/irq state, so callbacks must be safe. `nvkm_event_ntfy_valid` currently always returns true.

## Test Signals
Signals include allow/block ref transitions, wait-mode insertion/removal, concurrent dispatch and deletion, backend init/fini calls, and event teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/firmware.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/firmware.c

## Purpose
This file loads NVIDIA firmware blobs and wraps firmware images as NVKM memory objects suitable for DMA or VMM mapping.

## Important APIs, Types, and Functions
Public APIs include `nvkm_firmware_get`, `nvkm_firmware_put`, `nvkm_firmware_load_name`, `nvkm_firmware_load_blob`, `nvkm_firmware_ctor`, and `nvkm_firmware_dtor`. Internal memory methods expose scatterlist, size, physical address, page shift, target, and map behavior.

## Control Flow
Firmware get lowercases the chip name and requests `nvidia/<chip>/<fwname>[-ver].bin` without warning. Blob load copies firmware data and releases the firmware. Firmware constructor copies source bytes into RAM, DMA noncoherent memory, or vmalloc-backed SGT depending on function type, prepares DMA/scatterlist mappings, and constructs an NVKM memory wrapper. Destructor releases allocations and DMA mappings according to type.

## State and Persistence Behavior
State includes firmware name, device, length, image pointer, physical DMA address, scatterlist/table, and embedded NVKM memory object. Loaded blobs store copied data and size.

## Dependencies and Integration Points
It depends on Linux firmware loading, DMA mapping APIs, NVKM device/subdev logging, NVKM memory/VMM mapping, and firmware consumers in subdevs/falcons.

## Risks
Path buffers are fixed size. DMA/SGT constructors must unwind partially built mappings. SGT images use vmalloc pages and must map every page. Tegra devices return non-coherent host target.

## Test Signals
Signals include firmware present/missing paths, versioned names, RAM/DMA/SGT constructors and destructors, VMM mapping of firmware memory, and DMA mapping failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/gpuobj.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/gpuobj.c

## Purpose
This file implements NVKM GPU object allocation, suballocation, mapping, read/write access, and wrapping of existing memory.

## Important APIs, Types, and Functions
Public APIs include `nvkm_gpuobj_new`, `nvkm_gpuobj_del`, `nvkm_gpuobj_wrap`, `nvkm_gpuobj_memcpy_to`, and `nvkm_gpuobj_memcpy_from`. Internal function tables handle heap-backed objects, suballocated objects, fast kmap access, slow memory access, and VMM mapping.

## Control Flow
Constructor either suballocates from a parent GPU object heap using head/tail alignment rules or allocates instance memory directly. It sets function tables, address, size, optionally zeroes memory through kmap/write helpers, and initializes a child heap. Acquire tries to kmap the parent/memory and switches to fast direct IO access if successful; release restores the base table and drops the kmap. Delete frees parent heap nodes, child heap, memory refs, and the object.

## State and Persistence Behavior
State includes parent or instance memory reference, heap allocator, allocation node, GPU address, size, mapped pointer, and active function table.

## Dependencies and Integration Points
It depends on NVKM memory, instance memory, memory manager, BAR/kmap helpers, VMM mapping, and engines/subdevs that need GPU-visible objects.

## Risks
Suballocation alignment and zeroing must not write outside the parent node. Fast/slow function table switching must be balanced with acquire/release. `nvkm_gpuobj_memcpy_from` appears to write through `((u32 *)src)` instead of `dst`, which is suspicious.

## Test Signals
Signals include parent suballocation/free, direct instance allocation, kmap fast and slow paths, zeroing, VMM mapping, wrap behavior for legacy GART, and memcpy helper validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/gpuobj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/intr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/intr.c

## Purpose
This file implements NVKM interrupt controller registration, top-level IRQ handling, interrupt source translation, handler lists, arm/unarm, and per-handler allow/block controls.

## Important APIs, Types, and Functions
Public APIs include `nvkm_intr_ctor`, `nvkm_intr_install`, `nvkm_intr_dtor`, `nvkm_intr_add`, `nvkm_intr_rearm`, `nvkm_intr_unarm`, `nvkm_intr_allow`, `nvkm_intr_block`, `nvkm_inth_add`, `nvkm_inth_allow`, and `nvkm_inth_block`.

## Control Flow
Interrupt providers call `nvkm_intr_add` with leaf count, data mapping, and backend ops. Handlers call `nvkm_inth_add`, which translates subdevice/vector type into leaf/mask and adds the handler to a priority list. IRQ handling locks, unarms top-level sources, rearms MSI, samples pending masks, checks device presence, dispatches allowed handlers by priority, blocks unhandled pending bits to avoid storms, then rearms. Rearm lazily adds legacy subdev handlers from topology.

## State and Persistence Behavior
Device state includes the provider list, priority handler lists, lock, armed flag, IRQ number, allocation flag, and legacy initialization flag. Provider state includes stat/mask arrays. Handler state includes leaf/mask, allowed flag, callback, and list node.

## Dependencies and Integration Points
It depends on NVKM device, subdev, PCI MSI, topology discovery, backend interrupt ops, and subdev interrupt callbacks.

## Risks
IRQ handling runs under a device spinlock, so callbacks must be appropriate. Unhandled bits are blocked, which protects from storms but can mask real interrupts. Translation must match topology and legacy data tables.

## Test Signals
Signals include IRQ install/free, provider add/remove, handler allow/block, pending interrupt dispatch by priority, MSI rearm, unhandled-storm blocking, and legacy topology handler registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/intr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/ioctl.c

## Purpose
This file is the NVKM backend implementation of the NVIF ioctl protocol. It routes class queries, object creation/deletion, method calls, map/unmap, and unsupported read/write/nop requests.

## Important APIs, Types, and Functions
Main public API is `nvkm_ioctl`. Internal dispatchers include `nvkm_ioctl_sclass`, `nvkm_ioctl_new`, `nvkm_ioctl_del`, `nvkm_ioctl_mthd`, `nvkm_ioctl_map`, `nvkm_ioctl_unmap`, `nvkm_ioctl_path`, and class enumeration helper `nvkm_ioctl_sclass_`.

## Control Flow
Top-level ioctl unpacks version 0 headers, finds the target object by handle, and dispatches by type. Class query counts or copies child classes, including uevent class if supported. New finds a matching child class, refs an engine if present, calls its constructor, initializes the object, links it into the parent tree and client handle tree, and returns backend data through the `hack` pointer. Delete finalizes and deletes an object and returns 1 to suppress normal data extraction. Methods and maps delegate to object functions.

## State and Persistence Behavior
State changes include object tree insertion/removal, object initialization/finalization, engine references, client temporary `data` for created objects, and object mapping handles.

## Dependencies and Integration Points
It depends on NVIF ioctl ABI, NVKM object lifecycle, engine refs, user-event construction, and client object lookup.

## Risks
Object creation has many staged failure paths requiring fini/delete. The special return value 1 changes top-level cleanup behavior. Class enumeration and object handle uniqueness are security-sensitive for userspace APIs.

## Test Signals
Signals include ioctl class query sizing, object new/delete, duplicate handle rejection, method dispatch, map/unmap, unsupported rd/wr/nop errors, and engine ref failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/memory.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/memory.c

## Purpose
This file implements common NVKM memory reference counting, instance-memory allocation, and framebuffer compression tag allocation tracking.

## Important APIs, Types, and Functions
Public functions include `nvkm_memory_ctor`, `nvkm_memory_ref`, `nvkm_memory_unref`, `nvkm_memory_new`, `nvkm_memory_tags_get`, and `nvkm_memory_tags_put`.

## Control Flow
Memory construction installs a function table and initializes a kref. Unref drops the kref and calls the backend destructor before freeing. `nvkm_memory_new` supports instance-memory targets, selecting whether contents must be preserved across suspend/resume, and delegates to `nvkm_instobj_new`. Compression tag get locks framebuffer tag state, reuses compatible existing tags or allocates a new tag object and MM node, optionally clears hardware tags, and records empty tags when allocation fails. Put decrements and frees MM nodes/tags on last ref.

## State and Persistence Behavior
State includes memory function table, kref, optional compression tags pointer, tag MM node, tag refcount, and backend-specific memory allocations. Tag state persists on the memory object and framebuffer tag allocator.

## Dependencies and Integration Points
It depends on NVKM framebuffer tag allocator, instance memory subdev, NVKM MM allocator, and memory backend destructors. GPU object and firmware memory code use this interface.

## Risks
Compression tag compatibility is enforced by requested tag count; mismatches return `-EINVAL`. Empty tags intentionally represent failed hardware tag allocation and force uncompressed mappings later. Missing instmem returns `-ENOSYS`.

## Test Signals
Signals include memory ref/unref destructor calls, instance allocation for preserve and non-preserve targets, compression tag reuse/free, incompatible tag requests, allocation failure fallback, and concurrent tag access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/memory.c -->
