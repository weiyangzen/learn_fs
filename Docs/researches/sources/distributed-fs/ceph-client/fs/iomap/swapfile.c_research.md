## sources/distributed-fs/ceph-client/fs/iomap/swapfile.c

Purpose: validates and activates iomap-backed swapfiles by translating file extents into page-aligned physical swap extents.

Important types and APIs: `struct iomap_swapfile_info` accumulates contiguous physical iomaps, tracks the swap info, lowest/highest physical pages, total pages, extent count, and file for diagnostics. `iomap_swapfile_activate` is the exported entry point. `iomap_swapfile_add_extent` trims physical byte ranges to page boundaries and calls `add_swap_extent`.

Control flow: activation first `vfs_fsync`s the swap file so mapping metadata is committed. It iterates the page-aligned file size with `IOMAP_REPORT`. `iomap_swapfile_iter` accepts only mapped or unwritten extents, rejects inline, holes, dirty/uncommitted, shared, and non-main-device mappings, and merges physically contiguous ranges before adding extents. After iteration, it adds the final accumulated extent, rejects files with no usable page, and updates `pagespan`, `sis->max`, and `sis->pages`.

State and persistence: the function modifies swap subsystem state through `add_swap_extent` and final `swap_info_struct` fields. It relies on prior fsync to make extent metadata persistent enough for swap use and records physical page span information used by memory management.

Dependencies and integration points: integrates with `swapon`, filesystem iomap reporting, block-device identity, and swap extent accounting. It is intentionally conservative because swap cannot tolerate COW, delayed allocation, holes, or moving extents.

Risks and test signals: risks are accepting unstable extents, mishandling page alignment, off-by-one treatment of the swap header page, and multi-device files. Test with sparse files, unwritten preallocated files, reflink/shared files, dirty delalloc metadata, inline data, extents not page-aligned, files smaller than a page, and files crossing devices.
