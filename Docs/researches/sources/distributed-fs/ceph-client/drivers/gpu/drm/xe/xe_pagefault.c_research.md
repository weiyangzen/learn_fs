
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pagefault.c

## Purpose

`xe_pagefault.c` implements the consumer side of Xe device page fault handling. Producers parse hardware/firmware fault messages into `struct xe_pagefault`; this file queues those records, services them by resolving VM/VMA mappings, and calls producer acknowledgements with success or error.

## Important APIs, Types, and Functions

- Public API: `xe_pagefault_init()`, `xe_pagefault_reset()`, and `xe_pagefault_handler()`.
- Queue management: `xe_pagefault_queue_init()`, `xe_pagefault_queue_pop()`, `xe_pagefault_queue_work()`, `xe_pagefault_queue_reset()`, and `xe_pagefault_queue_full()`.
- Service path: `xe_pagefault_service()`, `xe_pagefault_asid_to_vm()`, `xe_pagefault_handle_vma()`, `xe_pagefault_begin()`, and `xe_pagefault_access_is_atomic()`.
- Diagnostics/persistence: `xe_pagefault_print()` and `xe_pagefault_save_to_vm()`.

## Control Flow

Initialization creates a high-priority unbound workqueue when USM is enabled and sizes each page-fault queue from total EU count plus engine count. Producers call `xe_pagefault_handler()` from IRQ or process context; it hashes by ASID, copies the compact fault record into a circular byte queue, and schedules work. The worker pops faults for up to a bounded runtime, skips reset-squashed records, services each fault, records failures into the VM fault list, logs non-prefetch failures, acknowledges through producer ops, and requeues itself if the time budget expires.

Service resolves ASID to a VM only if the VM is in fault mode or has scratch, takes the VM write lock, locates the VMA, checks read-only access, delegates CPU-address mirrors to SVM handling, otherwise validates/migrates the BO and rebinds the VMA on the faulting tile. It waits for the rebind fence before acknowledging success.

## State and Persistence Behavior

The device owns `xe->usm.pf_wq` and `xe->usm.pf_queue[]` while USM is enabled. Queue head/tail/data persist until teardown and are protected by spinlock. VM state can persist successful `last_fault_vma` updates and failure fault entries via `xe_vm_add_fault_entry_pf()`. Reset marks pending faults for a GT by nulling `pf->gt`.

## Dependencies and Integration Points

This layer integrates with USM ASID mappings, VM/VMA locks, BO validation/migration, userptr repinning, SVM mirror faults, TTM/DRM exec locking, validation retry logic, scheduler fences, GT stats, tracepoints, and producer-specific acknowledgement callbacks.

## Risks and Edge Cases

- Queue sizing assumes worst-case EU/engine fault count with an empirical multiplier; overflow returns `-ENOSPC` and warns.
- Worker service waits for fences and may requeue on runtime budget; long fault storms can increase latency.
- VM lookup rejects non-fault-mode VMs except scratch-capable VMs.
- DONTNEED/purged BOs fail faults for non-scratch VMs to avoid repopulating reclaimable pages.
- Atomic faults require VRAM for some VMAs and reject userptr VMAs needing VRAM movement.
- Reset squashing by setting `pf->gt = NULL` must race safely with queued copies.

## Test Signals

Signals include queue sizing/overflow tests, ASID lookup failure, read-only write faults, prefetch failure accounting, purged/DONTNEED BO behavior, userptr repin retry, SVM mirror delegation, VMA rebind success/failure, reset squashing, ack callback invocation, and workqueue time-budget requeue behavior.
