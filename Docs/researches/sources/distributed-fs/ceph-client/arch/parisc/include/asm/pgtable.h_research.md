# sources/distributed-fs/ceph-client/arch/parisc/include/asm/pgtable.h

Purpose: defines the PA-RISC page-table format, page protection bits, address-space geometry, TLB purge serialization, and PTE/PMD/PGD manipulation helpers.

Important APIs/types/functions: includes `purge_tlb_start/end`, `purge_tlb_entries`, `set_pte`, page-table level sizing macros, `_PAGE_*` bit definitions, `PTE_SHIFT`, `PFN_PTE_SHIFT`, protection presets, `pte_*` helpers, and swap/hugepage special-bit handling.

Control flow: fault handlers and mm code build PTEs, update entries with barriers, serialize TLB broadcasts when required, and use PA-RISC `pdtlb/pitlb` instructions to purge stale translations.

State and persistence: PTEs/PMDs/PGDs persist as the authoritative virtual-memory state; TLBs cache derived state. Dependencies and integration: depends on `page.h`, `fixmap.h`, cache/processor helpers, and generic pgtable layers.

Risks and test signals: comments warn TLB miss handlers assume specific bit ordering, so flag changes are high risk. Test with page-fault, COW, swap, hugepage, SMP TLB shootdown, and memory-protection selftests.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
