# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable-2level.h

Purpose: implements native page-table entry operations and swap-PTE encoding for traditional non-PAE i386 two-level paging.

Important APIs, types, and functions: defines `pte_ERROR()` and `pgd_ERROR()` diagnostics, `native_set_pte()`, `native_set_pmd()`, no-op `native_set_pud()`, `native_set_pte_atomic()`, `native_pmd_clear()`, `native_pud_clear()`, `native_pte_clear()`, SMP-aware `native_ptep_get_and_clear()`, `native_pmdp_get_and_clear()`, `native_pudp_get_and_clear()`, `pte_bitop()`, swap macros `SWP_TYPE_BITS`, `_SWP_TYPE_MASK`, `_SWP_TYPE_SHIFT`, `SWP_OFFSET_SHIFT`, `MAX_SWAPFILES_CHECK()`, `__swp_type()`, `__swp_offset()`, `__swp_entry()`, `__pte_to_swp_entry()`, `__swp_entry_to_pte()`, `_PAGE_SWP_EXCLUSIVE`, and non-inverting PROT_NONE helpers.

Control flow: native setters directly store entry values. SMP get-and-clear uses `xchg()`; UP uses local generic helpers. Swap entry encode/decode places type and offset into the limited 32-bit PTE format.

State and persistence: mutates page-table memory only. No external persistence exists.

Dependencies and integration points: included by `pgtable_32.h` when `CONFIG_X86_PAE` is off. It integrates with swap, userfaultfd/anon-exclusive swap markers through shared flags, and generic MM page-table operations.

Risks: 32-bit swap encoding has limited type bits and no inverted PFN protection. Direct stores are safe only under the generic MM locking rules. `native_pudp_*` is structurally present but effectively folded/no-op.

Test signals: non-PAE i386 boot, swap in/out, anon-exclusive swap markers, SMP page-table clear races, mprotect/mmap tests, and bad-entry diagnostics.
