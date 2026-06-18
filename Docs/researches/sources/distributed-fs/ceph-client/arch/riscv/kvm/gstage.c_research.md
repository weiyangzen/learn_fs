# sources/distributed-fs/ceph-client/arch/riscv/kvm/gstage.c

Purpose: This file implements RISC-V KVM G-stage page-table primitives. It detects supported HGATP modes, walks and edits guest-physical translations, maps pages and huge pages, splits huge mappings for dirty logging, write-protects or clears ranges, and issues the corresponding HFENCE invalidations.

Important APIs/types/functions: Global `kvm_riscv_gstage_max_pgd_levels` records the selected G-stage depth. Helpers include `gstage_pte_index`, `gstage_page_size_to_level`, `gstage_level_to_page_order/size`, `kvm_riscv_gstage_get_leaf`, `gstage_tlb_flush`, `kvm_riscv_gstage_set_pte`, `kvm_riscv_gstage_map_page`, `kvm_riscv_gstage_split_huge`, `kvm_riscv_gstage_op_pte`, `kvm_riscv_gstage_unmap_range`, `kvm_riscv_gstage_wp_range`, and `kvm_riscv_gstage_mode_detect`.

Control flow: Mapping starts by converting a requested page size into a page-table level, choosing read/write/execute protections with A/D bits set, and checking for an existing leaf. Existing huge mappings are split downward when dirty logging needs 4K tracking; compatible existing leaves only have protection updated. New mappings allocate intermediate tables from the KVM MMU cache and install a leaf. Clear/write-protect operations recursively walk page tables and operate at leaf granularity, freeing child tables during clear. Mode detection writes candidate HGATP modes from largest to smallest and records the first supported depth.

State and persistence: Persistent state is the VM's G-stage page-table tree rooted at `kvm->arch.pgd`; this file mutates PTEs but does not own the root allocation. `KVM_GSTAGE_FLAGS_LOCAL` selects local versus remote flush behavior. Mapping state persists until memory-slot invalidation, shadow flush, or VM teardown clears it.

Dependencies and integration points: It depends on Linux PTE/page helpers, `struct kvm_gstage` from architecture headers, KVM MMU memory caches, and TLB/HFENCE functions from `tlb.c`. It is used by MMU fault handling, AIA IMSIC MMIO remapping, dirty logging, aging, and memory-slot invalidation.

Risks and test signals: Huge-page splitting and write-protecting must preserve PFN offsets and permissions exactly. `gstage_level_to_page_order` treats invalid levels conservatively, but callers must pass supported levels. Tests should cover Sv32x4/Sv39x4/Sv48x4/Sv57x4 detection, 4K and huge mappings, dirty-log write-protection, unmap of sparse ranges, page-table free recursion, local versus remote HFENCE paths, and retry behavior when a huge mapping already exists.
