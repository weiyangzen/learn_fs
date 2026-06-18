# sources/distributed-fs/ceph-client/drivers/dax/device.c

Purpose: generic device-DAX character driver providing direct `mmap()` access to dev_dax memory.

Important APIs/types/functions: VMA checks, PTE/PMD/PUD fault handlers, `dev_dax_huge_fault()`, `dax_mmap_prepare()`, `dax_get_unmapped_area()`, file operations, `dev_dax_probe()`, and `device_dax_driver`.

Control flow and state: open binds file mappings to the DAX inode and stores `dev_dax`. `mmap_prepare()` verifies alive state, shared mapping, alignment, and DAX-capable file, then installs DAX vm ops. Fault handlers translate pgoff to physical address, enforce alignment/fault-size compatibility, set folio mappings, and insert pages/folios. Probe builds or validates pgmap, reserves each range, sets `MEMORY_DEVICE_GENERIC`, sets `vmemmap_shift` for huge alignments, memremaps pages, adds cdev, marks DAX alive, and registers kill cleanup.

Dependencies and integration: depends on mm fault APIs, memremap_pages, DAX core, cdev, VFS, THP, and DAX bus.

Risks and test signals: private mappings, misalignment, multi-range translation, folio mapping state, huge fault fallback, stale pgmaps, and range reservation are high-risk. Test mmap with PAGE/PMD/PUD alignments, MAP_PRIVATE rejection, unaligned VMA rejection, SIGBUS out-of-range faults, dynamic multi-range devices, unbind/remap, and THP config variants.
