# sources/distributed-fs/ceph-client/arch/x86/include/asm/page.h

## Purpose
Provides the main x86 kernel page header wrapper: architecture page includes, physical/virtual address conversion macros, page copy helpers, PFN mapping declarations, and canonical-address helpers.

## Important APIs, Types, And Functions
Includes `page_types.h` and either `page_64.h` or `page_32.h`. Declares `pfn_mapped[]`, `nr_pfn_mapped`, `copy_user_page()`, `vma_alloc_zeroed_movable_folio()`, `__pa()`, `__pa_nodebug()`, `__pa_symbol()`, `__va()`, `__boot_va()`, `__boot_pa()`, `virt_to_page()`, `virt_addr_valid()`, `pfn_to_kaddr()`, `__canonical_address()`, `__is_canonical_address()`, and `HAVE_ARCH_HUGETLB_UNMAPPED_AREA`.

## Control Flow
Callers convert between kernel virtual and physical addresses, validate direct-map addresses, copy pages, and canonicalize virtual addresses using sign extension based on address width. The selected 32-bit or 64-bit page header supplies low-level implementations.

## State And Persistence
State is global PFN mapping ranges and memory model data declared elsewhere. Address conversions are pure calculations.

## Dependencies And Integration Points
Depends on page type definitions, generic memory model, getorder helpers, folio allocation, and architecture page headers. It integrates with memory management, boot mappings, hugetlb, direct map, and low-level address validation.

## Risks And Edge Cases
`__pa_symbol()` hides relocation arithmetic from compiler overflow assumptions. `virt_to_page()` is valid only if `virt_addr_valid()` is true. Canonical-address helpers must match LA48/LA57 rules.

## Test Signals
Memory hotplug, debug-virtual checks, hugetlb tests, canonical address tests, direct-map validation, and 32-bit/64-bit builds are useful.
