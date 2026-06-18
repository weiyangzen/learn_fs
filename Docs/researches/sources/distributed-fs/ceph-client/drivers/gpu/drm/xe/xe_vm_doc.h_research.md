# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_doc.h

## Purpose

`xe_vm_doc.h` is a kernel-doc narrative for the Xe VM subsystem. It explains the conceptual model behind VM creation, scratch pages, VM binds, page-table updates, bind engines, munmap-style unbind semantics, userptr invalidation, compute-mode preempt fences, fault mode, access counters, locking, dma-resv slot usage, and future work.

## Important APIs, Types, and Functions

The file has no executable API. Its important content is the `DOC: Xe VM (user address space)` block. It names uAPI concepts such as `DRM_XE_VM_CREATE_FLAG_SCRATCH_PAGE`, `DRM_XE_VM_BIND_OP_MAP`, `DRM_XE_VM_BIND_OP_UNMAP`, `DRM_XE_VM_BIND_OP_MAP_USERPTR`, `DRM_XE_VM_BIND_FLAG_IMMEDIATE`, and VM bind engine class behavior. It also documents internal synchronization concepts that map directly to `xe_vm.c`: `vm->lock`, VM dma-resv, external BO dma-resv, bind queues, user fences, preempt fences, and `DMA_RESV_USAGE_*` slots.

## Control Flow and State

The document describes VM creation as root page-table allocation plus default bind engine creation. VM bind updates are described as a hybrid CPU/GPU page-table modification sequence: newly allocated page-table pages are initialized on the CPU, while updates into existing page-table structures are submitted through GPU jobs unless immediate CPU update bypass applies. Munmap-style unbinds are modeled as full unbinds plus edge rebinds to preserve large-page correctness.

Compute mode flow is documented as a loop that checks closure, pins userptrs, locks VM and BO reservations, validates evicted BOs, waits for preempt fences, rebinds invalidated or evicted memory, waits for the last rebind fence and kernel slot, installs new preempt fences, resumes engines, and retries on userptr invalidation races. Fault-mode flow is documented as ASID lookup, VMA lookup, backing-store allocation, page pin or BO validation/migration, rebind, TLB invalidation, and page-fault response.

## Dependencies and Integration Points

This documentation ties together `xe_vm.c`, `xe_lrc.c`, `xe_guc_ads.c`, userptr MMU notifiers, page fault workers, access counter workers, bind engines, and dma-resv semantics. It is a design map for reasoning about implementation behavior rather than a compiled dependency.

## Risks and Edge Cases

The doc calls out why fault mode cannot use dma fences, why G2H page fault handling must not allocate or acquire VM locks under CT locks, why munmap-style unbinds need kernel-operation ordering, and why eviction/userptr invalidation in fault mode uses lockless leaf-PTE zapping. These are the main areas where implementation drift can introduce deadlocks, memory corruption windows, or incorrect user-visible synchronization.

## Test Signals

Tests and reviews should compare implementation changes against this documented model. Signals include correct ordering of dma-resv slot waits and installs, correct bind-engine ordering for array binds, correct handling of immediate vs deferred fault-mode binds, correct compute preempt fence replacement, and lockdep coverage for VM global lock, VM reservation lock, external BO reservation locks, CT/G2H workers, and notifier paths.
