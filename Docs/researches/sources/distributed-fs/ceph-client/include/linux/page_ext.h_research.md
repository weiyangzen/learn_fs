<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_ext.h -->
# sources/distributed-fs/ceph-client/include/linux/page_ext.h

## Purpose
This header declares optional per-page extension storage used by page owner, page idle, page table check, and other clients needing metadata outside `struct page`.

## Important APIs, types, and functions
With `CONFIG_PAGE_EXTENSION`, `struct page_ext_operations` describes each client's offset, size, need/init callbacks, and shared flag usage. `enum page_ext_flags` defines shared flags such as owner allocated and optional young/idle bits. `struct page_ext` contains shared flags. Globals and APIs include `early_page_ext`, `page_ext_size`, `pgdat_page_ext_init()`, `early_page_ext_enabled()`, init functions for sparse/flatmem, `page_ext_get()`, `page_ext_from_phys()`, `page_ext_put()`, `page_ext_lookup()`, `page_ext_data()`, `page_ext_next()`, iterator struct and helpers, and `for_each_page_ext()`. Disabled stubs return `NULL`/false or no-op.

## Control flow
Boot or memory hotplug allocates page_ext arrays when any client needs them. Clients locate a page's extension by page, PFN, or physical address, access their private area by registered offset, and put references if required. Iteration must run under RCU read lock and can fast-step within a memory section or relookup at section boundaries.

## State and persistence
Page extension arrays persist per page descriptor after allocation. Shared flags and client data persist for page lifetime or until memory hotplug teardown. `early_page_ext` indicates early allocation mode.

## Dependencies and integration points
It depends on mmzone, stacktrace, sparsemem section layout, RCU locking discipline, memory hotplug, page owner, page idle, page table check, and page allocator initialization.

## Risks and test signals
Risks include missing RCU read lock during iteration, stale extension pointers across memory sections/hotplug, offset/size overlap between clients, shared flag collisions, and assuming page_ext exists when disabled or not needed. Test page owner/page idle/page table check configs, sparsemem and flatmem, memory hotplug add/remove, physical lookup, RCU iterator range scans, and disabled `CONFIG_PAGE_EXTENSION` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page_ext.h -->
