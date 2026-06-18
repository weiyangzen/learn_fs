# sources/distributed-fs/ceph-client/arch/xtensa/mm/kasan_init.c

Purpose: Initializes Xtensa KASAN shadow mappings during early boot and switches from shared early shadow to real writable shadow pages.

Important APIs, types, and functions: `kasan_early_init()`, `populate()`, `kasan_init()`, `kasan_early_shadow_pte`, `kasan_early_shadow_page`, and `kasan_init_generic()`.

Control flow: Early init maps the entire shadow range through the shared early shadow page. Full init validates address constants, allocates page-table entries and backing pages for VMALLOC-to-KSEG shadow coverage, flushes TLBs, zeroes the new shadow, write-protects the early shadow page, resets it, clears current task KASAN depth, and enables generic KASAN reporting.

State and persistence: Allocates permanent shadow page tables/pages via memblock, updates PMD/PTE entries, changes early shadow PTE protections, flushes TLBs, and initializes task KASAN depth.

Dependencies and integration: Requires early MMU/page table setup, memblock allocation, KASAN generic code, Xtensa shadow address constants, and disabled KASAN instrumentation for this file.

Risks: Any shadow range mismatch breaks memory instrumentation; allocation failures panic; this code must not be KASAN-instrumented before KASAN is ready; TLB flushes are required after remapping.

Test signals: KASAN-enabled boot, intentional out-of-bounds report after boot, VMALLOC shadow coverage, and early boot without recursive KASAN faults.
