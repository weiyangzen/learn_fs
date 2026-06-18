# sources/distributed-fs/ceph-client/arch/arm64/mm/fixmap.c

Purpose: initializes and manipulates ARM64 fixmap page tables and provides early FDT remapping through fixmap slots.

Important APIs/types/functions: bootstrap page table arrays `bm_pte`, `bm_pmd`, `bm_pud`, `early_fixmap_init`, `__set_fixmap`, and `fixmap_remap_fdt`.

Control flow: early init populates fixmap P4D/PUD/PMD/PTE tables using `__pa_symbol` because normal virtual-to-physical helpers are not available yet. `__set_fixmap` validates the fixed-address index, sets or clears the corresponding PTE, and flushes the kernel TLB when clearing. `fixmap_remap_fdt` validates physical FDT alignment, maps the first page, verifies magic and total size, rejects oversized blobs, and extends the mapping if the FDT crosses the first page.

State and persistence: owns early boot fixmap page-table arrays and mutates fixmap PTEs. No disk persistence.

Dependencies/integration: early boot memory setup, device tree parsing, fixed-address definitions, page-table population helpers, TLB flush, and PCI I/O region layout assertions.

Risks: runs very early, so wrong physical address conversion or table population can break boot. `__set_fixmap` can be called in IRQ context, limiting future TLB broadcast mechanisms. FDT remap must avoid accepting misaligned, invalid, or oversized blobs.

Test signals: early boot on page-table-level/page-size variants, FDT physical alignment and size checks, fixmap set/clear TLB behavior, 16K page configuration where kernel/fixmap share top-level entries, and IRQ-context fixmap users such as GHES.
