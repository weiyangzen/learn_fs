# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_64.h

Purpose: provides x86-64 page-table operations and boot page-table declarations, including 4/5-level folding, PTI-aware top-level entry writes, swap-entry encoding, kernel virtual mapping helpers, and assembler macros for early identity mappings.

Important APIs, types, and functions: declares boot tables such as `level4_kernel_pgt`, `level4_ident_pgt`, `level3_kernel_pgt`, `level2_kernel_pgt`, fixmap tables, and `init_top_pgt`. Defines `swapper_pg_dir`, `paging_init()`, error diagnostics, `mm_p4d_folded()`, `set_pte_vaddr_p4d()`, `set_pte_vaddr_pud()`, native setters/clearers/get-and-clear for PTE/PMD/PUD/P4D/PGD, swap macros `SWP_TYPE_BITS`, `__swp_type()`, `__swp_offset()`, `__swp_entry()`, conversions to PTE/PMD, `cleanup_highmap()`, unmapped-area feature flags, `PAGE_AGP`, kcore address conversions, `vmemmap`, extra mapping init helpers, and `gup_fast_permitted()`. Assembler side defines `l4_index()`, `pud_index()`, page-aligned symbol macro, and `PMDS()`.

Control flow: native setters use `WRITE_ONCE`; top-level P4D/PGD setters account for PTI by updating user shadow page tables when necessary. Swap entries store type in high bits and inverted offset in middle bits. `gup_fast_permitted()` rejects ranges above the virtual mask.

State and persistence: mutates kernel and user page-table memory. Boot tables and highmap cleanup affect runtime address translation.

Dependencies and integration points: depends on `pgtable_64_types.h`, fixmap, PTI, kcore, vmemmap, GUP-fast, boot assembly, and generic MM.

Risks: PTI mirroring and 5-level folding are subtle. Swap encoding must avoid A/D/L/G conflicts and speculative PFN exposure. Boot table symbols must match head_64.S layout.

Test signals: x86-64 boot with LA57/PTI/KASLR, swap and migration entries, GUP-fast boundary tests, kcore reads, highmap cleanup, fixmap setup, page-table dump validation, and early identity mapping assembly checks.
