# sources/distributed-fs/ceph-client/arch/arm64/mm/contpte.c

Purpose: implements ARM64 contiguous-PTE folding and unfolding for user mappings, plus wrappers that keep core-MM PTE operations correct when a logical mapping spans a hardware contiguous block.

Important APIs/types/functions: `mm_is_user`, alignment helpers, `contpte_convert`, `__contpte_try_fold`, `__contpte_try_unfold`, `contpte_ptep_get`, `contpte_ptep_get_lockless`, `contpte_set_ptes`, clear/get-clear wrappers, young/dirty clearing wrappers, `contpte_wrprotect_ptes`, and `contpte_ptep_set_access_flags`.

Control flow: folding checks user mm, folio coverage, contiguous PFNs, and matching protections while ignoring young/dirty state, aggregates dirty/young bits, clears the block, optionally flushes depending on BBML2 no-abort support, and reinstalls `CONT_PTE` entries. Unfolding clears `CONT_PTE` and repaints individual entries. Get helpers gather young/dirty state across sub-PTEs; the lockless path retries until it observes a consistent contiguous block. Range operations unfold partial blocks when required or expand operations to whole blocks when core-MM tracks state per folio.

State and persistence: mutates user page tables and TLB-visible attributes. No disk persistence. It deliberately avoids dynamic contiguous-bit changes for kernel and EFI mappings.

Dependencies/integration: core MM PTE APIs, ARM64 TLB flush machinery, folio metadata, BBML2 capability, exported symbols used by page-table helpers, and `CONFIG_ARM64_CONTPTE`.

Risks: contiguous entries require consistent attributes across all sub-PTEs; partial write-protect or access-flag changes can be unpredictable if not unfolded or applied to the whole block. Lockless reads can race with fold/unfold and must retry correctly. TLB flush elision relies on precise Arm BBML behavior.

Test signals: THP/large-folio mappings, fold/unfold under concurrent faults, write-protect/access-flag changes on partial and full blocks, lockless GUP reads during modification, dirty/young tracking, SMMU or no-DBM behavior, and BBML0 vs BBML2 CPUs.
