# sources/distributed-fs/ceph-client/arch/riscv/kvm/mmu.c

Purpose: This file connects generic KVM memory-slot/MMU operations to RISC-V G-stage page tables. It maps guest faults to host PFNs, validates memory regions, supports dirty logging and aging, handles IO remaps such as IMSIC VS-files, allocates/frees VM G-stage roots, and programs HGATP for vCPUs.

Important APIs/types/functions: Key functions include `kvm_riscv_mmu_ioremap`, `kvm_riscv_mmu_iounmap`, `kvm_arch_mmu_enable_log_dirty_pt_masked`, `kvm_arch_commit_memory_region`, `kvm_arch_prepare_memory_region`, `kvm_unmap_gfn_range`, `kvm_age_gfn`, `kvm_test_age_gfn`, `kvm_riscv_mmu_map`, `kvm_riscv_mmu_alloc_pgd`, `kvm_riscv_mmu_free_pgd`, and `kvm_riscv_mmu_update_hgatp`. Helpers handle memory-slot write-protection, THP alignment, host page-table size discovery, and huge-page adjustment.

Control flow: Fault handling validates/top-ups the vCPU page-table cache, inspects the host VMA for page size and PFNMAP/logging restrictions, snapshots `mmu_invalidate_seq`, faults in the PFN, acquires `mmu_lock`, retries if invalidation raced, optionally adjusts to THP PMD size, marks writable pages dirty, and maps through `kvm_riscv_gstage_map_page`. Memory-region preparation rejects GPAs outside the selected G-stage address space, writable slots backed by read-only VMAs, and dirty logging on PFNMAP IO regions. Dirty logging write-protects memslots by clearing G-stage write bits and flushing remote TLBs.

State and persistence: The VM owns `arch.pgd`, `pgd_phys`, and `pgd_levels`; this file allocates and frees that root and updates `HGATP` with mode, VMID, and PPN. Per-vCPU `mmu_page_cache` persists preallocated page-table pages. Dirty logging state is reflected by write-protected G-stage PTEs and KVM dirty bitmaps.

Dependencies and integration points: It depends on Linux VMA/mmap locking, KVM memory slots, dirty-ring/dirty-log APIs, host page-table walkers, RISC-V G-stage primitives in `gstage.c`, VMID helpers, NACL CSR writes, and TLB invalidation. AIA IMSIC hardware acceleration uses `ioremap/iounmap` to map guest IMSIC GPAs to hardware VS-file pages.

Risks and test signals: Race handling around host MMU invalidation and page-table promotion is subtle; `get_hva_mapping_size` deliberately reads entries once with IRQs disabled. Tests should cover memory-slot validation, read-only slots, PFNMAP IO slots, dirty logging enable/disable, THP and hugetlb mappings, HWPOISON signaling, `mmu_invalidate_seq` retry, aging queries, IMSIC IO remaps, and HGATP updates with and without VMID hardware.
