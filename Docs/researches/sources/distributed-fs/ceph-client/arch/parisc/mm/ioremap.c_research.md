# sources/distributed-fs/ceph-client/arch/parisc/mm/ioremap.c

Purpose: implements PA-RISC `ioremap_prot()` and exports it for mapping physical I/O ranges into kernel virtual address space.

Important API: `void __iomem *ioremap_prot(phys_addr_t phys_addr, size_t size, pgprot_t prot)` maps an I/O physical range with caller-supplied page protection. `EXPORT_SYMBOL(ioremap_prot)` makes it available to drivers and architecture code.

Control flow: with `CONFIG_EISA`, the function detects selected EISA physical address windows and extends them with `F_EXTEND(0xfc000000)`. It then rejects attempts to remap normal unreserved RAM below `high_memory` by walking pages over the requested range and returning `NULL` if any page is not reserved. Valid mappings fall through to `generic_ioremap_prot()`.

State and persistence: creates persistent vmalloc/ioremap mappings through the generic ioremap layer. It does not store private state.

Dependencies and integration: used via `asm/io.h` ioremap macros, including write-combining mappings with `_PAGE_IOREMAP`. Depends on Linux vmalloc/io/mm helpers, `high_memory`, page reserved flags, and PA-RISC EISA address extension.

Risks: `phys_addr + size - 1` can overflow if unchecked by callers. The normal-RAM rejection depends on `PageReserved` being accurate. EISA address-window boundaries must match hardware expectations or drivers may map the wrong bus address.

Test signals: map reserved device memory, reject ordinary RAM, exercise EISA windows with and without `CONFIG_EISA`, validate `ioremap_wc` paths, and test zero or overflow-prone sizes through callers.
