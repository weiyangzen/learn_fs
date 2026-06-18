# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pte-walk.h

Purpose: This header wraps PowerPC page-table walking helpers for locating Linux PTEs and translating kernel vmap/ioremap addresses to physical addresses without locking, including real-mode-safe use cases.

Important APIs/types/functions: `__find_linux_pte` is the underlying walker. `find_linux_pte` checks that IRQs are disabled, calls the walker, and debug-warns if huge-page shift is reported when hugepage configs are disabled. `find_init_mm_pte` walks `init_mm.pgd`. `ppc_find_vmap_phys` resolves a vmalloc/ioremap address to a physical address using the PTE PFN and hugepage/PAGE_SHIFT offset.

Control flow: Callers disable IRQs before general PTE walking, call `find_linux_pte` with optional THP and hugepage shift outputs, and handle a returned PTE pointer. Real-mode or vmap translation code calls `ppc_find_vmap_phys`, which finds the `init_mm` PTE, warns and returns zero if missing, computes PFN physical base, chooses hugepage shift or `PAGE_SHIFT`, and adds the page offset.

State and persistence: The functions read page-table state but do not mutate it. `init_mm` page tables are assumed not to be freed and not to use THP, although huge vmalloc/ioremap pages may exist.

Dependencies and integration points: It depends on scheduler/MM types, page table types/macros, IRQ state checks, `init_mm`, `VM_WARN`, and PTE helpers. It integrates with MMU code, hash/radix page table walking, vmalloc/ioremap translation, and real-mode code paths that cannot take normal locks.

Risks and test signals: Calling with IRQs enabled can race page-table changes. Missing PTEs in `ppc_find_vmap_phys` return zero after warning. Hugepage shift handling must match mapping size or physical offsets are wrong. Tests should cover vmalloc and ioremap translations, huge vmalloc mappings, debug VM warnings, IRQ-disabled callers, and real-mode users.
