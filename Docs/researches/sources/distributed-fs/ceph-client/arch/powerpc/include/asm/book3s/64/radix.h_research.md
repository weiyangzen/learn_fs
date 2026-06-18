# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/radix.h

Purpose: defines Book3S64 radix MMU geometry, virtual layout, PTE update primitives, THP support hooks, vmemmap mapping interfaces, kernel mapping, and process-table tree sizing.

Important APIs/types/functions: defines radix bad-bit masks, shift/range constants, kernel/vmalloc/IO/vmemmap ranges, table-size macros, strict RWX hooks, `__radix_pte_update()`, `radix__pte_update()`, `radix__ptep_get_and_clear_full()`, `radix__pte_same()`, `radix__pte_none()`, `radix__set_pte_at()`, PMD/PUD/P4D bad/same helpers, THP helpers, vmemmap functions, `radix__map_kernel_page()`, `radix__get_tree_size()`, and memory-hotplug section mapping functions.

Control flow: PTE updates use an `ldarx/stdcx.` loop on big-endian PTE storage. Set-PTE deliberately avoids `ptesync` for normal PTE stores, relying on tolerated spurious faults except for kernel mappings handled elsewhere. THP availability checks compare hardware page-size shifts to PMD/PUD shifts.

State and persistence: radix page tables, process/partition tables, and vmemmap mappings persist for the boot lifetime. This header stores no private state.

Dependencies and integration points: depends on page-size-specific radix headers, cmpxchg, TLB flush radix helpers, CPU feature checks, memory hotplug, dev_pagemap/DAX vmemmap optimization, and strict kernel RWX.

Risks: radix table geometry must match hardware process table RTS encoding. Missing synchronization in kernel mapping paths can cause unrecoverable kernel faults. Bad-bit masks must catch malformed table pointers without rejecting valid leafs.

Test signals: radix boot on POWER9+, page fault/mprotect stress, kernel ioremap, THP PMD/PUD tests, memory hotplug, DAX vmemmap optimization tests, strict RWX tests, and process table sizing validation.
