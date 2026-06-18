# sources/distributed-fs/ceph-client/arch/x86/mm/mm_internal.h

## Purpose
This private x86 mm header shares internal helpers and state between x86 memory-management implementation files without exposing them as public architecture APIs.

## Important APIs, Types, and Functions
- `alloc_low_pages()` and inline `alloc_low_page()` provide early low-memory page allocation for page tables and trampoline/KASLR code.
- `early_ioremap_page_table_range_init()` initializes early fixmap page-table coverage.
- `kernel_physical_mapping_init()` and `kernel_physical_mapping_change()` create or change direct-map page tables.
- `after_bootmem`, `update_cache_mode_entry()`, and `tlb_single_page_flush_ceiling` expose shared state or helpers.
- `x86_numa_init()` is declared when NUMA is enabled.

## Control Flow and State
The header has no runtime control flow. It defines cross-file contracts used during boot and memory hotplug. `after_bootmem` gates whether early or normal allocation paths may be used.

## Dependencies and Integration Points
Consumers include `init_32.c`, `init_64.c`, `kaslr.c`, `mem_encrypt_amd.c`, `ioremap.c`, `numa.c`, and PAT code. The direct-map APIs connect boot memory setup, encryption page-attribute changes, and hotplug.

## Risks
Because these are internal interfaces, signature or semantic changes can break boot ordering across several files. `kernel_physical_mapping_change()` in particular requires callers to understand TLB flush responsibilities.

## Test Signals
Build coverage across 32-bit, 64-bit, NUMA/non-NUMA, PAT, memory encryption, and hotplug configurations validates the header contract. Runtime validation comes from successful boot and direct-map changes without stale TLB faults.
