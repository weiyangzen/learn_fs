# sources/distributed-fs/ceph-client/virt/kvm/pfncache.c

## Purpose
This file implements KVM's `gfn_to_pfn_cache`, a small one-page cache for kernel or guest-mode access to guest memory. It caches the GPA/HVA, memslot generation, PFN, and kernel mapping for a page, invalidates on MMU notifier events, and supports GPA-based or direct-HVA-based activation.

## Important APIs, Types, And Functions
`gfn_to_pfn_cache_invalidate_start()` scans `kvm->gpc_list` and marks overlapping caches invalid. `kvm_gpc_check()` validates active state, memslot generation, HVA, length within one page, and valid PFN. `kvm_gpc_refresh()` recomputes the HVA/PFN mapping when stale. `kvm_gpc_init()` initializes locks and sentinel state. `kvm_gpc_activate()` and `kvm_gpc_activate_hva()` add the cache to the VM invalidation list and refresh it. `kvm_gpc_deactivate()` removes it, clears validity, and unmaps the old PFN. Internal helpers map PFNs through `kmap()` or `memremap()`, use `hva_to_pfn()`, and retry around MMU notifier sequence changes.

## Control Flow And State
Activation validates that the requested range fits within one page, takes `refresh_lock`, links the cache into `kvm->gpc_list`, marks it active under the rwlock, and refreshes. Refresh updates GPA/HVA/memslot generation, invalidates the cache before dropping the write lock, resolves the PFN outside the lock, maps a kernel address, retries if an MMU notifier raced, then publishes `valid`, `pfn`, and offset-adjusted `khva`. Deactivation reverses the active/valid state before unlinking so concurrent invalidation or refresh cannot miss the cache.

## Dependencies And Integration Points
The cache depends on `kvm_mm.h` for `hva_to_pfn()`, KVM MMU notifier sequencing (`mn_active_invalidate_count`, `mmu_invalidate_seq`), memslot generations from `kvm_main.c`, and Linux highmem/IOMEM mapping helpers. `kvm_main.c` initializes each VM's `gpc_list` and calls invalidation from MMU notifier range start before zapping secondary MMUs.

## Risks And Test Signals
Risks include stale kernel mappings after HVA changes, invalidation windows between list insertion and active state, missing sequence retries, misuse for multi-page accesses, and wrong release behavior for refcounted versus remapped PFNs. Tests should cover activation by GPA and HVA, memslot generation changes, `munmap`/`mprotect` invalidation, PFNMAP/IOMEM paths where supported, deactivation during concurrent refresh, and one-page length validation.
