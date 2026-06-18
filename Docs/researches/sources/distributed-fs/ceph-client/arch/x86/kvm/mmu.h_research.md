# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu.h

Purpose: Declares shared KVM x86 MMU constants, helpers, and entry points used by paging, shadow paging, TDP/NPT/EPT, page-fault handling, nested translation, MMIO SPTE encoding, and memory-slot accounting. The file is a compact contract between the MMU implementation and vCPU/core x86 code rather than a full implementation.

Important APIs/types/functions:

- Page table bit definitions: `PT_PRESENT_MASK`, writable/user/PWT/PCD/accessed/dirty/page-size/PAT/global/NX masks and shifts, root-level constants for 5-level, 4-level, 32-bit, and PAE paging, and role-bit masks for CR0, CR4, and EFER define the guest paging metadata that feeds MMU roles and permissions.
- `rsvd_bits()` builds inclusive reserved-bit masks while compile-time checking constant ranges. It is used by paging code that validates guest entries and constructs reserved-bit masks.
- `kvm_mmu_max_gfn()` returns the maximum GFN KVM should map, based on host MAXPHYADDR for TDP or 52-bit GPAs for non-TDP shadow paging.
- MMU setup declarations include `kvm_mmu_get_max_tdp_level()`, MMIO/SPTE mask setters, memory encryption SPTE mask setup, EPT mask setup, `kvm_init_mmu()`, `kvm_init_shadow_npt_mmu()`, and `kvm_init_shadow_ept_mmu()`.
- Fault and root lifecycle APIs include `kvm_can_do_async_pf()`, `kvm_handle_page_fault()`, `kvm_mmu_load()`, `kvm_mmu_unload()`, `kvm_mmu_reload()`, `kvm_mmu_free_obsolete_roots()`, `kvm_mmu_sync_roots()`, `kvm_mmu_sync_prev_roots()`, and `kvm_mmu_track_write()`.
- Permission helpers include `kvm_get_pcid()`, `kvm_get_active_pcid()`, `kvm_get_active_cr3_lam_bits()`, `kvm_mmu_load_pgd()`, `kvm_mmu_refresh_passthrough_bits()`, and `permission_fault()`.
- VM/MMU lifecycle and accounting declarations include `kvm_mmu_post_init_vm()`, `kvm_mmu_pre_destroy_vm()`, `kvm_shadow_root_allocated()`, `kvm_memslots_have_rmaps()`, `gfn_to_index()`, `kvm_mmu_slot_lpages()`, and `kvm_update_page_stats()`.
- Nested/direct-private helpers include `translate_nested_gpa()`, `kvm_translate_gpa()`, `kvm_tdp_mmu_map_private_pfn()`, `kvm_has_mirrored_tdp()`, `kvm_gfn_direct_bits()`, `kvm_is_addr_direct()`, and `kvm_is_gfn_alias()`.

Control flow:

The common vCPU run path calls `kvm_mmu_reload()` before entering the guest when requests or invalid roots require reload. That helper first handles `KVM_REQ_MMU_FREE_OBSOLETE_ROOTS`, then checks `vcpu->arch.mmu->root.hpa`; if no valid root exists, it calls `kvm_mmu_load()`. When a guest memory access faults, x86 fault handling enters `kvm_handle_page_fault()`, which relies on the role/permission helpers and implementation functions declared here.

Permission checking flows through `permission_fault()`. The caller supplies a page table access mask, pkey, and page-fault access bits. The helper strips nested paging details, reads guest RFLAGS for SMAP override state, refreshes passthrough CR0.WP-derived metadata when TDP may have stale state, indexes the MMU permissions table, then layers PKRU checks if `mmu->pkru_mask` is active. It returns zero for allowed access or a synthesized page-fault error code for denied access.

Nested translation flows through `kvm_translate_gpa()`. Normal MMUs return the GPA unchanged; the nested MMU path calls `translate_nested_gpa()` to translate L2 GPA through L1-controlled nested paging and fill an exception if translation fails. Direct-bit helpers support private/shared memory encodings, including TDX mirrored TDP handling.

State and persistence behavior:

- The header itself stores no state, but it defines access to persistent per-vCPU MMU roots (`vcpu->arch.mmu->root.hpa`, root role, guest/nested MMU pointers), per-VM shadow-root allocation state, page stats, memory-slot sizes, private/direct GFN bits, and global MMU feature booleans such as `enable_mmio_caching`, `tdp_enabled`, and `tdp_mmu_enabled`.
- `kvm_shadow_root_allocated()` uses acquire ordering so readers that observe the flag also observe related shadow-root pointers, paired with release storage in the allocator.
- `kvm_memslots_have_rmaps()` encodes whether reverse maps must exist, depending on TDP MMU enablement and whether shadow roots have ever been allocated.
- Page statistics are updated through `kvm_update_page_stats()` with atomic64 counters indexed by page level.

Dependencies and integration points:

- Includes `linux/kvm_host.h`, `kvm_cache_regs.h`, `x86.h`, and `cpuid.h`; depends on common x86 state helpers such as `kvm_read_cr3()`, `kvm_is_cr4_bit_set()`, `guest_cpu_cap_has()`, `kvm_x86_call()`, and host capability metadata.
- Integrates with EPT/NPT/TDP MMU implementations, legacy shadow paging, nested virtualization, async page faults, MMIO emulation, memory encryption, TDX private memory mapping, PKU/PKRU, SMAP/SMEP/WP permission modeling, large page accounting, and VM init/destroy paths.
- Uses Linux/KVM memory-slot structures and KVM hugepage level macros for reverse-map and large-page indexing.

Risks:

- Permission modeling is security-sensitive. Mistakes in `permission_fault()` or its inputs can allow illegal guest access or inject incorrect page faults, especially with SMAP, CR0.WP passthrough, PKU, nested MMU, or implicit supervisor accesses.
- `kvm_mmu_max_gfn()` intentionally uses host MAXPHYADDR for TDP. Changing that contract can cause KVM to install SPTEs for GPAs hardware cannot represent, or reject valid non-TDP shadow translations.
- Root reload logic assumes `root.hpa` validity is sufficient even with mirror roots. Any future root representation changes must preserve the documented invariant.
- Memory ordering around `shadow_root_allocated` prevents readers from seeing uninitialized shadow-root state; weakening it could create rare races in memslot/rmap decisions.
- Direct/private GFN helpers are small but important for confidential-computing guests. Misclassifying direct bits or aliases can map private/shared pages incorrectly.

Test signals:

- KVM unit/selftests for page faults, MMIO SPTEs, reserved-bit faults, CR0.WP, CR4.SMAP/SMEP/PKE, PKRU, NX, PCID, LAM CR3 bits, and async page faults.
- Nested virtualization tests for EPT/NPT shadow MMUs and `translate_nested_gpa()` exception behavior.
- TDP MMU and non-TDP builds/runs, including 5-level paging, huge pages, rmap allocation, obsolete-root freeing, root reload after invalidation, and memory-slot resizing.
- Confidential-computing/private-memory tests for mirrored TDP, direct GFN bits, aliases, and `kvm_tdp_mmu_map_private_pfn()`.
- Runtime signals include correct `kvm->stat.pages[]` accounting, absence of reserved-bit fault regressions, successful VM init/destroy, and stable guest boot under memory pressure and migration.
