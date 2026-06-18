# sources/distributed-fs/ceph-client/arch/arm64/kvm/mmu.c

## Purpose
This file is the host-side ARM64 KVM MMU implementation. It initializes hyp and stage-2 page tables, manages hyp mappings and pKVM sharing, maps guest RAM/device memory on abort, handles memory-slot changes, dirty logging, hugepage splitting, MTE tag preparation, guest external abort routing, TLB/cache maintenance, and MMU notifier callbacks.

## Important APIs, Types, and Functions
- Global hyp state: `hyp_pgtable`, `kvm_hyp_pgd_mutex`, `hyp_idmap_*`, `__hyp_va_bits`, and `io_map_base`.
- Stage-2 lifecycle: `kvm_init_stage2_mmu()`, `kvm_uninit_stage2_mmu()`, `kvm_free_stage2_pgd()`, `stage2_unmap_vm()`, `kvm_stage2_unmap_range()`, and `kvm_stage2_flush_range()`.
- Hyp mapping APIs: `__create_hyp_mappings()`, `create_hyp_mappings()`, `hyp_alloc_private_va_range()`, `create_hyp_stack()`, `create_hyp_io_mappings()`, `create_hyp_exec_mappings()`, `kvm_share_hyp()`, and `kvm_unshare_hyp()`.
- Fault handling: `kvm_handle_guest_abort()`, `user_mem_abort()`, `gmem_abort()`, `pkvm_mem_abort()`, `handle_access_fault()`, and `kvm_handle_guest_sea()`.
- Dirty logging and split helpers: `kvm_stage2_wp_range()`, `kvm_arch_mmu_enable_log_dirty_pt_masked()`, `kvm_mmu_wp_memory_region()`, and `kvm_mmu_split_huge_pages()`.
- Memory-region hooks: `kvm_arch_prepare_memory_region()`, `kvm_arch_commit_memory_region()`, and `kvm_arch_flush_shadow_memslot()`.
- Cache/TLB controls: `kvm_arch_flush_remote_tlbs()`, `kvm_arch_flush_remote_tlbs_range()`, `kvm_set_way_flush()`, and `kvm_toggle_cache()`.

## Control Flow
Initialization builds hyp idmap metadata, allocates a hyp page table, maps the hyp init text executable, records hyp VA bits, initializes stage-2 VTCR/PGD state, allocates per-CPU last-vCPU state, and configures eager split caches. Hyp mappings are either created by the host-owned hyp page table, delegated to pKVM hyp calls, or expressed through share/unshare PFN refcounting depending on kernel-in-hyp/protected mode.

Stage-2 range operations chunk large ranges at minimum block granularity and optionally drop/reacquire `mmu_lock` to avoid stalls. Dirty logging write-protects and optionally splits memory slots. Memory-slot deletion/move unmaps stage-2 ranges and nested stage-2 mappings. I/O mapping maps device PAs into guest IPA as device memory when protected KVM is not enabled.

Guest abort handling first routes SEAs, validates IPA range, traces the fault, supports translation/permission/access-flag/exclusive-atomic faults, resolves nested stage-2 translations when applicable, locates the memory slot/HVA, sends invalid slot or readonly write faults to instruction/data abort or MMIO handling, handles access-flag faults by making the PTE young, then dispatches to pKVM, guest_memfd, or userspace-VMA backed mapping.

`user_mem_abort()` tops up the MMU cache, captures VMA metadata and invalidation sequence, faults in a PFN, validates device/cacheability and MTE requirements, computes stage-2 permissions, decides mapping size including hugetlb/THP/nested constraints, sanitizes MTE tags, maps or relaxes permissions under the fault lock, releases the pinned page, and marks dirty pages. `gmem_abort()` maps private guest memory from guest_memfd with invalidation sequence protection. `pkvm_mem_abort()` pins long-term anonymous/shmem pages and maps them through pKVM stage-2.

## State and Persistence
Persistent state includes hyp page tables, stage-2 page tables, VTCR/PGD physical addresses, per-CPU `last_vcpu_ran`, split-page memory caches, protected hyp memcaches, RB-tree reference counts for shared hyp PFNs, memory-slot metadata, dirty bitmaps, MTE page-tag state, and vCPU fault/stat state. The file uses `mmu_lock`, `slots_lock`, `config_lock`, SRCU, `mmap_read_lock`, RCU callbacks, invalidation sequence counters, and page pins/refcounts to coordinate with Linux memory management.

## Dependencies and Integration Points
It depends on the page-table engine in `hyp/pgtable.c`, pKVM hyp calls and protected VM state, Linux MM/VMA/GUP/memslot APIs, MTE helpers, cache maintenance primitives, nested virtualization translation helpers, MMIO handling, fault injection, tracepoints, arch timer and ACPI/system headers, and KVM generic MMU notifier interfaces.

## Risks and Edge Cases
Major risks are stale stage-2 mappings after MMU invalidation, mapping the wrong PFN when HVA/IPA alignment differs, dirty logging with huge mappings, cache incoherency for uncached guest mappings without FWB, unsafe cacheable PFNMAP mappings, missing MTE tag initialization, pKVM memslot mutation after protected VM creation, private/shared memory confusion, and nested translation permission mismatches. The code mitigates these with invalidation sequence checks, block-mapping alignment tests, VMA cacheability validation, mapping-size caps, permission relaxation rules, and explicit protected-VM restrictions.

## Test Signals
Run KVM selftests for stage-2 faults, dirty logging, THP/hugetlb mapping, memslot create/move/delete, MMU notifier invalidation, access aging, MTE, guest_memfd/private memory, pKVM, nested virtualization, device PFNMAP MMIO, cache maintenance trapping, and SEA userspace exits. Kernel signals include tracepoints for guest faults and cache toggles, lockdep, RCU stalls, page refcount leaks, HWPOISON behavior, and data-integrity stress under concurrent memory reclaim.
