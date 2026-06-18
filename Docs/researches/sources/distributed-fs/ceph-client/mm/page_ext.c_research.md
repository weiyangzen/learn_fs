# Research: sources/distributed-fs/ceph-client/mm/page_ext.c

## Purpose

`sources/distributed-fs/ceph-client/mm/page_ext.c` implements the generic `struct page_ext` facility: optional per-page extension storage allocated outside `struct page`. It lets debug and instrumentation features attach metadata to each physical page without enlarging the core `struct page` for every kernel build. The file decides whether extensions are needed at boot, lays out per-client extension areas, allocates flatmem or sparsemem backing arrays, handles memory hotplug, and exposes RCU-protected lookup/get/put helpers.

## Important APIs, Types, and Functions

The main public state is `page_ext_size`, the computed bytes per page extension entry, and `early_page_ext`, controlled by the `early_page_ext` boot parameter or forced by memory allocation profiling debug. Clients register through `struct page_ext_operations` objects in the local `page_ext_ops[]` array. Supported clients in this copy include page owner, page idle flags on 32-bit, memory allocation profiling tags, page table check, and IOMMU debug page allocation.

Important helpers include `invoke_need_callbacks()`, `invoke_init_callbacks()`, `get_entry()`, `page_ext_lookup()`, `page_ext_get()`, `page_ext_from_phys()`, and `page_ext_put()`. Flatmem builds use `page_ext_init_flatmem()`, `page_ext_init_flatmem_late()`, `pgdat_page_ext_init()`, `lookup_page_ext()`, and `alloc_node_page_ext()`. Sparsemem builds use `page_ext_init()`, `alloc_page_ext()`, `init_section_page_ext()`, `online_page_ext()`, `offline_page_ext()`, `page_ext_callback()`, `__invalidate_page_ext()`, and `__free_page_ext()`.

## Control Flow

Initialization begins by calling `invoke_need_callbacks()`. The first pass checks whether any client needs shared flags and reserves the base `struct page_ext` size when needed. The second pass assigns each active client an offset in the extension entry, adds its requested size, and returns whether any extension storage is required. If no client needs extensions, allocation is skipped entirely.

On flatmem, `page_ext_init_flatmem()` allocates one node-sized extension table per online node using memblock. It accounts the table as memmap boot pages and stores the base pointer in `NODE_DATA(nid)->node_page_ext`. `lookup_page_ext()` computes an index by subtracting a rounded-down node start PFN so buddy checks near node boundaries can safely address the extra alignment space. Late initialization invokes client init callbacks.

On sparsemem, `page_ext_init()` iterates memory nodes and valid sections, allocating one extension table per section through `alloc_pages_exact_nid()` or `vzalloc_node()`. `init_section_page_ext()` stores a biased pointer in `section->page_ext`, so `lookup_page_ext()` can compute an entry directly from PFN via `get_entry(section->page_ext, pfn)`. A memory notifier allocates extension storage on `MEM_GOING_ONLINE` and invalidates/frees it on `MEM_OFFLINE` or cancelled online.

Sparsemem offlining is deliberately three-phase. `offline_page_ext()` first marks each section's pointer invalid by setting a low-bit sentinel, then calls `synchronize_rcu()`, then frees the backing storage. This allows existing `page_ext_get()` users that started before invalidation to finish without use-after-free.

Runtime access uses RCU. `page_ext_lookup()` requires the caller already holds the RCU read lock. `page_ext_get()` takes the RCU read lock, performs lookup, and returns NULL while dropping RCU if no extension exists. Successful callers must later call `page_ext_put()`. `page_ext_from_phys()` validates a physical address with `pfn_to_online_page()` before delegating to `page_ext_get()`.

## State and Persistence Behavior

Page extension state is volatile kernel memory. It is allocated at boot or memory hotplug time and freed on sparsemem offlining. `total_usage` tracks allocated bytes for logging, while memmap page accounting is adjusted through `memmap_boot_pages_add()` or `memmap_pages_add()`.

Client offsets in `struct page_ext_operations` are assigned during initialization and remain the ABI for clients during the boot lifetime. Extension contents are owned by clients such as page owner, allocation tagging, page idle, page table check, and IOMMU debug code. This file only owns allocation, lifetime, and lookup.

## Dependencies and Integration Points

Dependencies include MM core headers, memblock, memory hotplug notifiers, vmalloc, kmemleak, RCU, sparsemem/flatmem topology, page owner, page idle, page table check, allocation profiling tags, and IOMMU debug page allocation. Boot parameter integration is through `early_param("early_page_ext", ...)`.

The allocator integration is important: page allocator sanity checks can call into `lookup_page_ext()` before extension arrays are allocated during early boot or hotplug, so lookup must tolerate NULL bases. Allocation profiling can require page extensions before the first page allocation to avoid missing early allocation tags.

## Risks and Edge Cases

The highest risk is lifetime during memory hotplug. Sparsemem section pointers can be valid, invalid-sentinel, or NULL; callers must hold RCU across use, and offlining must wait for a grace period before freeing. Incorrect pointer biasing or invalid-bit handling would produce wrong entries or free the wrong base address.

Allocation failure policy differs by phase. Boot-time extension allocation panics on failure once any client requires page extensions; hotplug returns notifier errors. Large systems can allocate significant memory because `page_ext_size` is multiplied by every present PFN or section, so client `need()` callbacks must be accurate.

Flatmem node-boundary padding is subtle. The table may include an extra `MAX_ORDER_NR_PAGES` span when node PFNs are not aligned, because buddy checks can inspect nearby PFNs. Removing that padding can break allocator boundary checks.

## Test Signals

Useful tests include booting with and without clients such as `CONFIG_PAGE_OWNER`, `CONFIG_PAGE_TABLE_CHECK`, `CONFIG_MEM_ALLOC_PROFILING`, and `CONFIG_PAGE_IDLE_FLAG`; booting with `early_page_ext`; memory hotplug online/offline cycles under concurrent page owner or page table check lookups; kmemleak noise checks around biased section pointers; sparsemem and flatmem build coverage; physical-address lookup tests for MMIO, holes, ZONE_DEVICE, offline memory, and normal RAM; and allocation failure injection for hotplug extension allocation.
