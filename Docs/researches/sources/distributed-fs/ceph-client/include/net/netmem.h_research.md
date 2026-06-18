# sources/distributed-fs/ceph-client/include/net/netmem.h

Purpose: Introduces `netmem_ref`, an abstract networking memory reference that can represent either a normal `struct page` or a non-page `struct net_iov` memory-provider chunk, while exposing common page-pool fields.

Important APIs/types/functions: `netmem_desc` mirrors page-pool fields in `struct page`; `net_iov` and `net_iov_area` represent slab-allocated network I/O chunks from providers such as dmabuf or io_uring. Helpers include owner/index/init, page/iov/netmem conversions, refcount/PFN/address/PFMemalloc queries, page-pool descriptor access, DMA address access, devmem type check, `get_netmem`, `put_netmem`, DMA unmap address macro, and `netmem_dma_unmap_page_attrs`.

Control flow: Page-pool and networking code carry `netmem_ref`; the low bit distinguishes net_iov from page pointers. Helpers branch to page or provider-specific logic for references, DMA, NUMA, addressability, and page-pool fields. Unsafe helpers are available for page-only hot paths.

State and persistence: Runtime memory descriptors track page-pool pointer, DMA address, and page-pool refcount. Static assertions enforce layout aliasing with `struct page`.

Dependencies/integration: Depends on page_pool field layout, DMA mapping, mm page APIs, static keys for memory providers, debug warnings, and provider implementations for `__get_netmem/__put_netmem`.

Risks/test signals: Layout drift is critical. Test static assertions, low-bit pointer tagging assumptions, unsafe helper misuse on net_iovs, refcount symmetry, DMA unmap suppression for provider memory, address queries returning NULL for iovs, and provider-enabled/disabled configs.
