# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_32.h

Purpose: provides the i386 top-level page-table header, selecting PAE or non-PAE operations and declaring initial kernel page tables and boot paging initialization helpers.

Important APIs, types, and functions: declares `swapper_pg_dir[1024]`, `initial_page_table[1024]`, `initial_pg_pmd[]`, `paging_init()`, and `sync_initial_page_table()`. Includes either `pgtable-3level.h` or `pgtable-2level.h`. Defines `kpte_clear_flush()`, `PAGE_TABLE_SIZE(pages)`, and `LOWMEM_PAGES`.

Control flow: compile-time PAE selection pulls in the appropriate implementation. `kpte_clear_flush()` clears a kernel PTE from `init_mm` then flushes the kernel TLB entry. `PAGE_TABLE_SIZE()` computes `.brk` reservation for enough initial page tables to cover lowmem, accounting for separate PMD pages under PAE.

State and persistence: initial page-table arrays are boot/runtime memory. No persistence exists.

Dependencies and integration points: depends on `pgtable_32_types.h`, processor/thread definitions, TLB flush helpers, and boot lowmem layout. It feeds early page-table allocation and lowmem direct-map setup.

Risks: initial table sizing must cover all lowmem or boot mapping will fail. `LOWMEM_PAGES` avoids assembler overflow warnings and must track `__PAGE_OFFSET`. PAE and non-PAE include selection changes many entry semantics.

Test signals: i386 boot with PAE and non-PAE, highmem direct-map sizing, early page-table reservation, kernel PTE clear/flush behavior, and lowmem boundary mapping tests.
