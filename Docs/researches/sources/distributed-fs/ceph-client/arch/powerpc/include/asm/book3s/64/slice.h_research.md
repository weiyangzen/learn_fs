# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/slice.h

Purpose: defines hash-MMU slice sizing and public helpers for selecting unmapped areas and page sizes across a Book3S64 process address space.

Important APIs/types/functions: defines `HAVE_ARCH_HUGETLB_UNMAPPED_AREA`, `HAVE_ARCH_UNMAPPED_AREA`, and `HAVE_ARCH_UNMAPPED_AREA_TOPDOWN` for hash MMU configs. Slice constants include `SLICE_LOW_SHIFT`, `SLICE_LOW_TOP`, `SLICE_NUM_LOW`, `GET_LOW_SLICE_INDEX`, `SLICE_HIGH_SHIFT`, `SLICE_NUM_HIGH`, `GET_HIGH_SLICE_INDEX`, and `SLB_ADDR_LIMIT_DEFAULT`. Declares `slice_get_unmapped_area()`, `get_slice_psize()`, `slice_set_range_psize()`, `slice_init_new_context_exec()`, and `slice_setup_new_exec()`.

Control flow: implementation code uses these declarations to choose bottom-up or top-down unmapped areas and to set page-size classes over address ranges. Low slices cover 256MB chunks below 4GB; high slices cover 1TB chunks.

State and persistence: slice page-size masks persist in each hash `mm_context_t`, while `SLB_ADDR_LIMIT_DEFAULT` seeds address limits for new contexts.

Dependencies and integration points: included by `mmu-hash.h`; integrates with mmap layout, hugetlb unmapped-area selection, process exec setup, and SLB segment/page-size programming.

Risks: slice indexes must match the hash MMU segment scheme. Incorrect page-size range updates can create SLB entries incompatible with PTE/HPTE size expectations.

Test signals: mmap and top-down allocation tests, hugetlb unmapped-area tests, exec context reset tests, high-address mappings above 1TB, and SLB miss coverage.
