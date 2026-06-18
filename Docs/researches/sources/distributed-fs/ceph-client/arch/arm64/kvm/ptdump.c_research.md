# sources/distributed-fs/ceph-client/arch/arm64/kvm/ptdump.c

Purpose: provides debugfs page-table dumps for arm64 KVM stage-2 page tables, including canonical VM stage-2 tables and nested virtualization shadow stage-2 MMUs. It formats leaf PTE attributes through the generic ptdump machinery and exposes IPA range and level-count metadata.

Important APIs and types: `struct kvm_ptdump_guest_state` holds the target `kvm_s2_mmu`, parser state, IPA markers, and level descriptions. Public creation/removal functions are `kvm_s2_ptdump_create_debugfs()`, `kvm_nested_s2_ptdump_create_debugfs()`, and `kvm_nested_s2_ptdump_remove_debugfs()`. Internal file operations are backed by `kvm_ptdump_guest_show()`, `kvm_ptdump_guest_open()`, `kvm_ptdump_guest_close()`, `kvm_pgtable_range_show()`, `kvm_pgtable_levels_show()`, and shared open/close helpers.

Control flow: debugfs open obtains a safe KVM reference with `kvm_get_kvm_safe()`, allocates a parser state based on the target page table start level, and attaches it to a single-open seq file. The show path initializes `ptdump_pg_state`, takes `kvm->mmu_lock` for writing, and walks the page table from IPA 0 to `BIT(ia_bits)` with a leaf-only walker. Each visited leaf calls `note_page()` with the old PTE. Close frees parser state and drops the KVM reference. Nested debugfs files are named from cached VTTBR, VTCR, and whether virtual stage-2 is enabled.

State and persistence: this file persists only debugfs dentries and per-open parser allocations. `mmu->shadow_pt_debugfs_dentry` is stored for nested MMU removal. It does not modify page-table contents; it reads under `mmu_lock` to provide a stable dump.

Dependencies and integration: depends on `linux/debugfs.h`, `seq_file`, arm64 KVM page-table walkers, generic `ptdump`, stage-2 PTE bit definitions, KVM lifetime reference helpers, and nested-virt capability detection. `nested.c` creates/removes nested ptdump files when shadow MMU contexts are allocated or recycled.

Risks: debugfs lifetime must not outlive the KVM or nested MMU. The safe KVM reference and removal path reduce that risk, but stale `i_private` pointers would be serious. The dump takes a write lock over a full IPA walk, so large sparse VMs can make debugfs reads expensive and block MMU updates. Formatting masks must stay synchronized with stage-2 PTE bit definitions.

Test signals: manual debugfs reads should show `stage2_page_tables`, `ipa_range`, `stage2_levels`, and nested entries when nested virt is available. Tests can validate open/close during VM teardown, nested MMU recycling removing files, and output attribute strings for readable/writable/executable/accessed/block mappings.
