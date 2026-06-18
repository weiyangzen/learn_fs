## sources/distributed-fs/ceph-client/arch/mips/kvm/mmu.c

Purpose: Manages the MIPS KVM GPA page tables used to map guest physical addresses to host physical pages and supports dirty/access tracking, unmapping, and root TLB fault handling.

Important APIs, types, and functions: Allocation helpers are `kvm_pgd_alloc()` and `kvm_mmu_free_memory_caches()`. Page-table walking uses `kvm_mips_walk_pgd()` and `kvm_mips_pte_for_gpa()`. Flush and tracking APIs include `kvm_mips_flush_gpa_pt()`, `kvm_mips_mkclean_gpa_pt()`, `kvm_arch_mmu_enable_log_dirty_pt_masked()`, `kvm_unmap_gfn_range()`, `kvm_age_gfn()`, and `kvm_test_age_gfn()`. Fault handling is in `_kvm_mips_map_page_fast()`, `kvm_mips_map_page()`, and `kvm_mips_handle_vz_root_tlb_fault()`. VCPU scheduling hooks are `kvm_arch_vcpu_load()` and `kvm_arch_vcpu_put()`.

Control flow: GPA PGDs are initialized to invalid PTE/PMD tables. Fault handling first tries a fast path under `mmu_lock` to mark old pages young or writable clean pages dirty. Slow path tops up the VCPU MMU cache, samples `mmu_invalidate_seq`, faults in a PFN through KVM core, retries on invalidation races, allocates GPA page-table levels, installs a PTE with readable/cacheable/writeable bits, marks dirty on write faults, and releases the page reference. Root TLB faults map the GPA page then invalidate the matching host TLB entry.

State and persistence: VM state is `kvm->arch.gpa_mm.pgd`, a GPA page-table hierarchy. Per-VCPU state includes `arch.mmu_page_cache`, `last_sched_cpu`, and callback-owned CPU register state. Page dirty/young bits persist in GPA PTEs until flushed, aged, or cleaned.

Dependencies and integration points: Depends on Linux KVM MMU notifier sequencing, SRCU, `kvm_faultin_pfn()`, dirty-page APIs, MIPS page-table helpers, TLB invalidation in `tlb.c`, and backend callbacks for VCPU load/put. Called by `mips.c` memory-slot and VCPU lifecycle code.

Risks: Page-table walking/allocation assumes MIPS folding configuration and uses `BUG()` for unexpected `pgd_none()`. Range flush functions must free lower-level tables only when full ranges are removed. The slow path requires correct memory barriers around `mmu_invalidate_seq` to avoid stale PFNs. `kvm_arch_mmu_enable_log_dirty_pt_masked()` converts a bit mask into a continuous start/end range, so sparse masks may write-protect pages between set bits.

Test signals: GPA faults for present, absent, readonly, clean writeable, old, dirty, and MMIO/noslot pages; concurrent MMU notifier invalidation; dirty logging enable and masked updates; aging/test-age; full and partial memslot unmap; VCPU migration hrtimer restart; and root TLB fault invalidation.
