# sources/distributed-fs/ceph-client/arch/arm64/mm/ptdump.c

## Purpose
This file implements ARM64 kernel page-table dumping and W+X/non-UXN validation. It formats page-table ranges by protection attributes, registers a debugfs dump for kernel page tables, and provides `ptdump_check_wx()` to detect insecure writable-executable or executable kernel mappings.

## Important APIs, Types, and Functions
Important data includes `pte_bits[]`, `kernel_pg_levels[]`, and `kernel_ptdump_info`. Main functions are `dump_prot()`, `note_prot_uxn()`, `note_prot_wx()`, `note_page()` and its level wrappers, `note_page_flush()`, `ptdump_walk()`, `ptdump_check_wx()`, and initcall `ptdump_init()`.

## Control Flow
`ptdump_init()` builds address markers for the linear map, optional KASAN shadow, modules, vmalloc, vmemmap, PCI I/O, and fixmap ranges; initializes per-level masks from `pte_bits[]`; and registers `kernel_page_tables` through `ptdump_debugfs_register()`.

`ptdump_walk()` builds a `ptdump_pg_state` and delegates to `arm64_ptdump_walk_pgd()`, which increments `arm64_ptdump_lock_key` while walking. `note_page()` coalesces consecutive ranges with the same level and protection bits, emits marker headers, formats range size units, and invokes W+X/non-UXN checks when enabled. `ptdump_check_wx()` performs a non-printing walk over the kernel range and returns false if insecure pages are found.

## State and Persistence
The debugfs info and address markers persist after device init. During a walk, state is local in `ptdump_pg_state`. The static key `arm64_ptdump_lock_key` coordinates with page-table freeing code in `mmu.c` so freed tables are not raced by a dump.

## Dependencies and Integration Points
This file integrates with generic `ptdump_walk_pgd()`, debugfs registration, ARM64 page-table bit definitions, KASAN layout, virtual memory layout constants, and `mmu.c` page-table free synchronization.

## Risks
Incorrect bit masks can misreport page protections or miss W+X mappings. Walk synchronization is important because debugfs can dump while kernel page tables are being freed. Marker ordering must match the virtual layout, especially with variable `vabits_actual` and optional KASAN.

## Test Signals
Reading debugfs `kernel_page_tables` should produce coherent ranges and markers. `ptdump_check_wx()` should pass after rodata protections are applied. Tests should include KASAN and non-KASAN layouts, memory hotplug/table-free activity while dumping, and configurations with folded page-table levels.
