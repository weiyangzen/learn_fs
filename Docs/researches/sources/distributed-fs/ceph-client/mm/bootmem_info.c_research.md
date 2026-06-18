# sources/distributed-fs/ceph-client/mm/bootmem_info.c

## Purpose
`bootmem_info.c` tracks boot-time metadata pages so they are not freed prematurely and can be released correctly during memory hotplug teardown. It registers pgdat and sparsemem section metadata as reserved bootmem-backed pages.

## Important APIs, types, and functions
Public functions are `get_page_bootmem`, `put_page_bootmem`, and `register_page_bootmem_info_node`. The internal helper `register_page_bootmem_info_section` registers `mem_section` usage metadata. It uses `bootmem_type`, `page_private`, page refcounts, and kmemleak physical-range freeing.

## Control flow
`get_page_bootmem` encodes an info value and bootmem type into `page_private`, sets `PagePrivate`, and increments the page refcount. `put_page_bootmem` validates the type and, when the reference drops to one, clears private state, reinitializes the list head, tells kmemleak about the freed physical page, and releases it as a reserved page. Node registration marks the `pglist_data` pages and iterates valid sparsemem sections belonging to the node.

## State and persistence
Metadata ownership persists in `page_private` and elevated refcounts until hotplug or teardown calls `put_page_bootmem`. There is no on-disk state.

## Dependencies and integration points
It depends on sparsemem section helpers, memblock-era metadata, memory hotplug type ranges, kmemleak, and page allocator reserved-page release. It is compiled when `HAVE_BOOTMEM_INFO_NODE` is selected.

## Risks and test signals
Risks include bad type encoding, reference leaks that keep bootmem pages reserved forever, double release, registering PFNs assigned to multiple nodes, and mismatches with preinitialized vmemmap sections. Test signals include memory hotplug add/remove, sparsemem section metadata release, kmemleak noise checks, multi-node boot with overlapping early PFN ownership, and debug page refcount validation.
