## sources/distributed-fs/ceph-client/arch/s390/mm/page-states.c

Purpose: hooks page allocation and free paths into s390 CMMA page-state instructions for guest page hinting of unused and stable pages.

Important APIs, types, and functions: exported global `cmma_flag` selects whether page-state instructions are active and which stable mode to use. `arch_free_page()` calls `__set_page_unused()` for freed pages. `arch_alloc_page()` calls `__set_page_stable_dat()` or `__set_page_stable_nodat()` for allocated pages.

Control flow: both hooks return immediately when `cmma_flag` is zero. On free, the entire buddy order range is marked unused. On allocation, the same range is marked stable; `cmma_flag < 2` selects DAT-aware stable marking, otherwise no-DAT stable marking.

State and persistence: persistent state is boot-preserved `cmma_flag`. Page state is maintained in hardware/firmware metadata through s390 page-state instructions.

Dependencies and integration points: depends on generic page allocator arch hooks, s390 page-state primitives, and boot setup that initializes `cmma_flag`.

Risks: incorrect order/range conversion could hint the wrong memory range. The hooks must remain cheap because they run in allocator paths. Behavior depends on host support and boot-time CMMA enablement.

Test signals: allocation/free stress under CMMA-enabled guests, host page hint counters if available, and boot with CMMA disabled to confirm hooks become no-ops.
