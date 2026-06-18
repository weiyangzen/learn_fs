# sources/distributed-fs/ceph-client/arch/arm64/mm/Makefile

Purpose: selects ARM64 MM subsystem objects for DMA cache maintenance, exception fixups, fault handling, init, cache routines, page copy, flush, ioremap, mmap, page tables, context switching, page attributes, fixmap, and optional features.

Important APIs/types/functions: `obj-y` base list, optional `contpte.o`, `hugetlbpage.o`, `ptdump.o`, `trans_pgd.o`, `physaddr.o`, `mteswap.o`, `gcs.o`, `kasan_init.o`, and KASAN sanitizer disables for `physaddr.o` and `kasan_init.o`.

Control flow: Kbuild links the base MM objects unconditionally and adds feature-specific objects according to ARM64 config symbols.

State and persistence: no runtime state. It controls build-time composition of MM code.

Dependencies/integration: depends on Kbuild and config symbols including `CONFIG_ARM64_CONTPTE`, `CONFIG_HUGETLB_PAGE`, `CONFIG_PTDUMP`, `CONFIG_TRANS_TABLE`, `CONFIG_DEBUG_VIRTUAL`, `CONFIG_ARM64_MTE`, `CONFIG_ARM64_GCS`, and `CONFIG_KASAN`.

Risks: missing optional object inclusion can silently disable feature support or break symbols. Sanitizer settings are important for early MM and physical address debugging code.

Test signals: ARM64 config build matrix, feature-specific boot tests for CONTPTE/MTE/GCS/KASAN/PTDUMP, and linker symbol checks.
