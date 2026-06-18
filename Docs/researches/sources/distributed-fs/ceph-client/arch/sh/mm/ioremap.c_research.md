# sources/distributed-fs/ceph-client/arch/sh/mm/ioremap.c

Purpose: implements SH `ioremap_prot` and `iounmap` across trapped I/O, 29-bit direct segments, early fixmap mappings, PMB mappings, and generic vmalloc page-table mappings.

Important APIs and helpers: exported `ioremap_prot`, exported `iounmap`, `__ioremap_29bit`, and `iomapping_nontranslatable`.

Control flow: mapping first checks trapped I/O, then direct 29-bit P1/P2/P4 segment mappings. Before memory init completes it uses fixed ioremap slots. Later it tries PMB pre-faulted mappings for large ranges, then generic ioremap. Unmap ignores non-translatable direct mappings, then tries fixed ioremap, PMB, and generic unmap in order.

State and persistence: creates/removes kernel virtual mappings, PMB entries, or fixed mappings depending on path.

Dependencies and integration: generic ioremap, trapped I/O, PMB, fixed ioremap, cache/TLB flushes, addrspace macros, and `mem_init_done`.

Risks: direct segment classification must not return cacheable aliases for attributes requiring page-table mappings. PMB error pointers are skipped to generic mapping, so callers see fallback behavior.

Test signals: early boot ioremap users, MMIO driver probes, 29-bit direct mapping cases, PMB large mappings, and unmap path validation.
