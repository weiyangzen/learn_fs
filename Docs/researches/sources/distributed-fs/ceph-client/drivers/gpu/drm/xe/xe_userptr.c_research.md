# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_userptr.c

Purpose: Implements userptr VMA setup, MMU interval notifier invalidation, page pinning through DRM GPUSVM, repin/rebind list management, and test-only forced invalidation.

Important APIs/types/functions: Public APIs include `xe_vma_userptr_check_repin`, `__xe_vm_userptr_needs_repin`, `xe_vma_userptr_pin_pages`, `xe_vm_userptr_pin`, `xe_vm_userptr_check_repin`, `xe_userptr_setup`, `xe_userptr_remove`, `xe_userptr_destroy`, and optional `xe_vma_userptr_force_invalidate`. Notifier callbacks are `xe_vma_userptr_invalidate_start` and `xe_vma_userptr_invalidate_finish`; internal helpers include `xe_vma_userptr_invalidate_pass1`, `xe_vma_userptr_do_inval`, and `xe_vma_userptr_complete_tlb_inval`.

Control flow: Setup initializes list links and inserts an MMU interval notifier for the current process range. Pinning uses `drm_gpusvm_get_pages` under VM lock with read-only/device-private context. On MMU invalidation, start callback rejects non-blockable ranges, takes the GPUSVM notifier write lock, advances the notifier sequence, moves non-fault-mode VMAs to `invalidated`, enables/waits for reservation fences as needed, optionally defers via embedded `finish`, invalidates TLBs for fault-mode initially-bound VMAs, and unmaps GPUSVM pages. Finish callback completes deferred TLB wait or invalidation. VM repin moves invalidated entries into `repin_list`, pins pages, and schedules VMA rebinds; on error it restores pending entries.

State and persistence behavior: Per-VM state includes `invalidated` and `repin_list`. Per-userptr state includes notifier, GPUSVM pages, embedded finish object, TLB invalidation batch, `finish_inuse`, `tlb_inval_submitted`, and `initial_bind`. Invalidations mutate lists and page mappings under combinations of VM lock, notifier lock, invalidated spinlock, and reservation locks. Removal frees pages then removes notifier only after GPU access is safe.

Dependencies and integration points: Depends on DRM GPUSVM, Linux MMU interval notifiers, DMA reservation fences, Xe SVM/private-page ownership, VM/VMA helpers, TLB invalidation batching, VM invalidate/rebind paths, and BO tracepoints (`trace_xe_vma_userptr_invalidate*`).

Risks: Lock ordering is subtle and enforced with lockdep assertions. Non-blockable invalidations return false, forcing notifier core behavior. Deferred invalidation uses one embedded finish per userptr; concurrent use falls back to synchronous invalidation. `-EFAULT` during repin requires unbinding/invalidation cleanup to avoid stale GPU access. Fault-mode and non-fault-mode paths differ significantly.

Test signals: MMU notifier stress with mmap/munmap/mprotect while GPU binds are active, non-fault and fault-mode VMs, concurrent exec/rebind workers, forced invalidation with `CONFIG_DRM_XE_USERPTR_INVAL_INJECT`, page fault injection, `-EFAULT` repin handling, lockdep, and tracepoint observation for invalidate/invalidate-complete.
