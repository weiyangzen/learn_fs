# sources/distributed-fs/ceph-client/arch/loongarch/kvm/mmu.c

Purpose: implements LoongArch KVM second-stage GPA-to-host-physical page tables, dirty/access tracking, hugepage support, memslot invalidation, and guest page fault handling.

Important APIs, types, and functions: exports `kvm_pgd_alloc()`, `kvm_arch_prepare_memory_region()`, `kvm_arch_commit_memory_region()`, `kvm_arch_flush_shadow_all()`, `kvm_arch_flush_shadow_memslot()`, `kvm_unmap_gfn_range()`, `kvm_age_gfn()`, `kvm_test_age_gfn()`, `kvm_handle_mm_fault()`, `kvm_arch_mmu_enable_log_dirty_pt_masked()`, and `kvm_arch_flush_remote_tlbs_memslot()`. Core internals include `kvm_populate_gpa()`, page-table walkers, `kvm_map_page_fast()`, `kvm_map_page()`, `host_pfn_mapping_level()`, and `kvm_split_huge()`.

Control flow: fast faults update existing young/dirty bits under `mmu_lock`. Slow faults resolve the memslot/HVA/PFN under SRCU, top up MMU page-cache pages, guard against MMU notifier invalidations, choose cacheability and permissions, optionally install PMD-sized mappings, split hugepages on write faults under dirty logging, install PTEs, and mark dirty pages. Flush walkers clear mappings, update stats, collect freed page-table pages, and request remote TLB flushes.

State and persistence: per-VM state includes `arch.pgd`, root level, invalid PTE tables, pte shifts, stats for pages/hugepages, memslot arch flags, and shadow page-table pages. Per-vCPU state includes the MMU page cache and `flush_gpa` request.

Dependencies and integration points: depends on generic KVM memory slots, MMU notifier sequencing, PFN fault-in helpers, dirty logging, memslot flags, LoongArch PTE helpers, TLB flush requests, and exit handling for GPA faults.

Risks: races with host MMU invalidation are guarded but complex. Hugepage alignment, dirty logging, and split behavior are high risk. `kvm_unmap_gfn_range()` initializes a free list but caller-side freeing must be considered with walker behavior. Cache attributes differ for valid RAM PFNs versus device PFNs.

Test signals: guest memory stress, dirty-log migration, hugepage mapping/splitting, MMU notifier invalidation during COW/unmap, readonly memslots, MMIO fallback, access aging, and remote TLB shootdown tests.
