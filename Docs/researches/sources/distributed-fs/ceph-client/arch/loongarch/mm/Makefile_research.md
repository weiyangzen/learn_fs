# sources/distributed-fs/ceph-client/arch/loongarch/mm/Makefile

Purpose: declares LoongArch memory-management object composition.

Important APIs, types, and functions: core objects include `init.o`, `cache.o`, `tlb.o`, `tlbex.o`, `extable.o`, `fault.o`, `ioremap.o`, `maccess.o`, `mmap.o`, `pgtable.o`, `page.o`, and `pageattr.o`; optional objects include `highmem.o`, `hugetlbpage.o`, and `kasan_init.o`. `KASAN_SANITIZE_kasan_init.o := n` disables instrumentation for KASAN bootstrap code.

Control flow: Kbuild selects objects based on `CONFIG_HIGHMEM`, `CONFIG_HUGETLB_PAGE`, and `CONFIG_KASAN`.

State and persistence: build metadata only; determines which MM implementation files are linked.

Dependencies and integration points: connects architecture MM code to generic memory management, KASAN, hugetlb, highmem, exception tables, TLB refill, and page attribute management.

Risks: omitting an object breaks architecture MM functionality or link symbols. KASAN init must remain unsanitized to avoid recursive instrumentation during sanitizer setup.

Test signals: MM config matrix builds, boot memory initialization, KASAN boot tests, hugetlb/highmem tests, page attribute and fault handling selftests.
