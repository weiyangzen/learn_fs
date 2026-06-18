# sources/distributed-fs/ceph-client/arch/sh/mm/Makefile

Purpose: selects SH memory-management implementation objects by CPU family and configuration.

Important variables: baseline `alignment.o cache.o init.o consistent.o mmap.o`, `cacheops-y`, `mmu-y`, `tlb-y`, `debugfs-y`, and conditional objects for hugepages, PMB, NUMA, fixed ioremap, uncached mapping, and SRAM.

Control flow: Kbuild resolves cache and TLB implementations from `CONFIG_CPU_*`, MMU/NOMMU, and optional feature symbols.

State and persistence: build-time object graph only; determines which MM functions and hooks exist in the kernel.

Dependencies and integration: integrates all `arch/sh/mm` files with generic MM and CPU configuration.

Risks: wrong CPU-family selection can bind incompatible cache/TLB register code. Missing optional object selection creates unresolved symbols when configs are enabled.

Test signals: configuration build coverage and boot on each supported SH CPU/cache/TLB family.
