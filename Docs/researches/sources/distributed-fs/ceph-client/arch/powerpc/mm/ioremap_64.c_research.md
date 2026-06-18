# sources/distributed-fs/ceph-client/arch/powerpc/mm/ioremap_64.c

Purpose: implements 64-bit PowerPC `__ioremap_caller()` and `iounmap()` with early upward allocation from `ioremap_bot`.

Important APIs and control flow: it rejects mappings using the unsupported `H_PAGE_4K_PFN` hack, page-aligns physical addresses and offsets, rejects zero/physical-null mappings, uses `generic_ioremap_prot()` after slab is available, and otherwise warns and installs early page mappings at the current `ioremap_bot`, advancing it upward with a guard page. `iounmap()` ignores pre-slab calls and later delegates to `generic_iounmap()`.

State and dependencies: state is the shared `ioremap_bot`; dependencies include generic vmalloc ioremap, `early_ioremap_range()`, page-table protection encodings, and slab availability. Risks are early mapping leaks, incorrect handling of page-offset returns, overlap with vmalloc reservation, and refusing legitimate callers that accidentally pass 4K PFN flags. Test signals include early MMIO users, 64-bit PCI/firmware mappings, `ioremap_prot()` attribute tests, and boot logs for early-use warnings.
