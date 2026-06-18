# sources/distributed-fs/ceph-client/arch/sparc/mm/init_32.c

Purpose: SPARC32 memory initialization, bootmem/memblock setup, highmem accounting, ramdisk reservation, valid physical address bitmap construction, cache flush exports, and VMA protection map.

Important APIs/functions: globals `phys_base`, `pfn_base`, `sp_banks`, `highstart_pfn`, `highend_pfn`, `last_valid_pfn`. Functions include `calc_highpages`, `bootmem_init`, `paging_init`, `arch_mm_preinit`, `sparc_flush_page_to_ram`, `sparc_flush_folio_to_ram`, and `DECLARE_VM_GET_PAGE_PROT`.

Control flow: `bootmem_init` adds PROM-discovered physical banks to memblock, honors `cmdline_memory_size` by trimming banks, computes kernel end/start PFNs, detects highmem above `SRMMU_MAXMEM`, reserves initrd and kernel image, limits memblock allocations to lowmem, and returns max PFN. `paging_init` delegates SRMMU page-table setup then builds device tree and scans devices. `arch_mm_preinit` validates fixmap/pkmap separation, allocates `sparc_valid_addr_bitmap`, zeros it, and marks real pages. Flush helpers call lower-level cache routines for pages/folios.

State and persistence: initializes global physical memory bank state, memblock memory/reserved ranges, highmem PFNs, valid address bitmap, initrd virtual/physical addresses, and protection map used by VM page protections.

Dependencies/integration: includes memblock, initrd, highmem, SRMMU/TLB/prom/leon headers, and `mm_32.h`. Requires `sp_banks` and base PFNs populated earlier by platform setup.

Risks: bank trimming for `mem=` must keep sentinel entries valid. Highmem split uses bank ordering and `SRMMU_MAXMEM`; holes can affect `calc_max_low_pfn`. Valid address bitmap sizes are derived from `last_valid_pfn` and 1MB chunks. Initrd address normalization handles bootloader quirks and can reserve wrong memory if `phys_base` is wrong.

Test signals: SPARC32 boot with multiple memory banks, `mem=` limits, initrd present/absent, highmem systems, pkmap/fixmap overlap assertions, valid-address checks, and page/folio cache flush callers. `/proc/iomem`/memblock logs should reflect trimmed/reserved ranges.
