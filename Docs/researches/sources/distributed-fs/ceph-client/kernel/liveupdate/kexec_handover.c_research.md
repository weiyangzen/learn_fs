# sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover.c

## Purpose
`kexec_handover.c` implements Kexec Handover metadata and preserved-memory management. It lets the current kernel mark pages, folios, vmalloc areas, and FDT subtrees for preservation across a kexec, then lets the next kernel discover the KHO FDT, reserve preserved memory in memblock, restore page ownership, recreate vmalloc mappings, and use scratch memory for safe early boot allocation.

## Important APIs, Types, and Functions
Global control includes `kho_enable`, `kho_is_enabled()`, early params `kho=` and `kho_scratch=`, outgoing state `struct kho_out`, incoming state `struct kho_in`, global `kho_scratch`, and `kho_scratch_cnt`. The preservation radix tree uses `struct kho_radix_tree`, `kho_radix_add_page()`, `kho_radix_del_page()`, `kho_radix_walk_tree()`, and helpers to encode/decode physical address plus order into a key.

Memory APIs exported to other subsystems are `kho_preserve_folio()`, `kho_unpreserve_folio()`, `kho_restore_folio()`, `kho_preserve_pages()`, `kho_unpreserve_pages()`, `kho_restore_pages()`, `kho_preserve_vmalloc()`, `kho_unpreserve_vmalloc()`, `kho_restore_vmalloc()`, `kho_alloc_preserve()`, `kho_unpreserve_free()`, and `kho_restore_free()`. FDT subtree APIs are `kho_add_subtree()`, `kho_remove_subtree()`, and `kho_retrieve_subtree()`. Boot/kexec integration includes `kho_memory_init()`, `kho_populate()`, `kho_fill_kimage()`, and `kho_locate_mem_hole()`.

## Control Flow
On cold boot with KHO enabled, `kho_memory_init()` reserves scratch areas using memblock and CMA alignment. Later `kho_init()` allocates the outgoing radix tree root and preserved root FDT, initializes debugfs, writes the KHO FDT root with the physical address of the memory map, creates kexec metadata, initializes scratch pageblocks as CMA, and exposes the outgoing FDT in debugfs.

For an incoming KHO boot, early platform code calls `kho_populate()` with FDT and scratch physical ranges. It validates the FDT header and compatible string, retrieves the preserved memory map pointer, maps scratch descriptors, adds scratch areas to memblock, marks them as KHO scratch, reserves the descriptor array, forces early memblock allocation to scratch only, and records incoming FDT/scratch metadata. Then `kho_memory_init()` releases scratch to CMA-like pageblocks and calls `kho_mem_retrieve()` to walk the prior radix tree and reserve all preserved pages with `KHO_PAGE_MAGIC` and order stored in `page->private`.

Preserving pages inserts encoded PFN/order ranges into the outgoing radix tree, with `kho_preserve_pages()` splitting a range by alignment and NUMA node boundaries. Restoring checks the magic/order in `page->private`, clears it, initializes page or folio refcounts and compound metadata, adjusts managed page counts, and returns the page/folio. Vmalloc preservation serializes physical chunks into preserved `struct kho_vmalloc_chunk` pages and restore reconstructs a vmalloc area from restored pages.

Kexec image setup stores the outgoing FDT physical address in `image->kho.fdt`, copies scratch descriptors into a kexec segment, and constrains regular kexec buffer placement to KHO scratch regions when KHO is active.

## State and Persistence Behavior
Persistent handover state is the KHO root FDT, subtree physical pointers and sizes, the preserved-memory radix tree, preserved page contents, scratch descriptor array, and optional kexec metadata. Page order/magic is reconstructed in the new kernel by reserving preserved pages and writing `page->private`. Runtime outgoing state is protected by mutexes on the FDT and radix tree. KHO deliberately avoids preserving scratch areas and debug mode can detect overlap.

## Dependencies and Integration Points
The file depends on memblock internals, CMA/pageblock migration, kexec file loading, libfdt, early ioremap, vmalloc internals, KASAN vmalloc unpoisoning, kmemleak exclusion, KHO ABI headers, and `kexec_handover_internal.h` debug/debugfs helpers. LUO uses `kho_alloc_preserve()`, FDT subtree APIs, and page/vmalloc preservation for session/file state.

## Risks and Test Signals
Preserved memory reservation is safety-critical: missing a radix entry can let the new kernel overwrite live state, while stale entries leak memory. Radix key encoding must distinguish order and physical address across the full address range. Scratch sizing and reservation failures disable KHO. `kho_restore_page()` trusts magic/order in `page->private` and must reject double restores. Vmalloc restore must exactly match total pages, flags, and order. Tests should cover cold and incoming KHO boots, malformed FDTs, scratch override parsing, lowmem/global/per-node scratch allocation, page/folio/vmalloc preserve-restore-unpreserve cycles, subtree add/remove/retrieve, kexec metadata versioning, crash-kexec bypass, and debug scratch-overlap detection.
