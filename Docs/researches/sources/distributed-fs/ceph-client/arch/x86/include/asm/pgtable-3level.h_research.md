# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-3level.h

Purpose: implements PAE i386 page-table entry operations, including ordered 64-bit PTE writes on 32-bit CPUs, atomic exchange helpers, PTI-aware PUD setting, swap-PTE encoding using the full 64-bit PTE, and PROT_NONE PFN inversion.

Important APIs, types, and functions: defines diagnostics for PTE/PMD/PGD, `pxx_xchg64()`, `native_set_pte()`, `native_set_pte_atomic()`, `native_set_pmd()`, `native_set_pud()`, `native_pte_clear()`, `native_pmd_clear()`, `native_pud_clear()`, `pud_clear()`, SMP get-and-clear helpers, `pmdp_establish()`, swap macros (`SWP_TYPE_BITS`, `SWP_OFFSET_FIRST_BIT`, `SWP_OFFSET_SHIFT`, `__swp_type()`, `__swp_offset()`, `__swp_entry()`, `__swp_entry_to_pte()`, `__pte_to_swp_entry()`), `_PAGE_SWP_EXCLUSIVE`, and includes `pgtable-invert.h`.

Control flow: present PTE updates write high half first, issue `smp_wmb()`, then write low half so hardware never sees a bogus present entry. Clearing reverses the order by clearing low/present half first. Atomic operations use `try_cmpxchg64()` loops. `pmdp_establish()` avoids expensive cmpxchg64 when installing non-present PMDs.

State and persistence: mutates page-table memory. PTI helper calls can update paired user page tables through `pti_set_user_pgtbl()`.

Dependencies and integration points: used by `CONFIG_X86_PAE` 32-bit builds, swap, THP-like PMD operations, PTI, and generic MM page-table APIs.

Risks: write ordering is critical because hardware may read split 64-bit entries on 32-bit CPUs. Swap encoding inverts offsets to set high physical bits and reduce L1TF-style speculation exposure. PUD/PGD flushing assumptions are documented and must match callers.

Test signals: PAE i386 SMP boot, swap/migration, mprotect and page-fault races, PTI enabled builds, pmdp establishment tests, bad-entry diagnostics, and TLB flush coverage after top-level changes.
