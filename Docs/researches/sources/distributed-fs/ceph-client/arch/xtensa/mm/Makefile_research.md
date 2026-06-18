# sources/distributed-fs/ceph-client/arch/xtensa/mm/Makefile

Purpose: Selects Xtensa memory-management objects and disables KASAN instrumentation for sensitive early/fault/MMU files.

Important APIs, types, and functions: `obj-y := init.o misc.o`, `obj-$(CONFIG_PFAULT)`, `obj-$(CONFIG_MMU)`, `obj-$(CONFIG_HIGHMEM)`, `obj-$(CONFIG_KASAN)`, and `KASAN_SANITIZE_* := n`.

Control flow: Always builds memory init and assembly helpers; conditionally builds page fault, cache/ioremap/mmu/tlb, highmem, and KASAN initialization objects based on configuration.

State and persistence: No runtime state; controls which MM symbols exist in the final image.

Dependencies and integration: Kbuild, architecture config symbols, and early boot/fault code that must run before KASAN is fully initialized.

Risks: Instrumenting page-fault or MMU setup with KASAN could recurse before shadow mappings are ready; missing optional objects would break config-specific APIs.

Test signals: Build matrix for MMU/noMMU, PFAULT, HIGHMEM, KASAN, and fault-path boot tests with KASAN enabled.
