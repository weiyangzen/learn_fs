<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netmem_priv.h -->
# sources/distributed-fs/ceph-client/net/core/netmem_priv.h

## Purpose
Private inline helpers for manipulating page-pool metadata stored in `netmem_ref` backing descriptors, including page-pool identity, DMA address fields, and compressed DMA index bits.

## APIs, Types, and Functions
Helpers include `netmem_get_pp_magic()`, `netmem_is_pp()`, `netmem_set_pp()`, `netmem_set_dma_addr()`, `netmem_get_dma_index()`, and `netmem_set_dma_index()`. They operate through `netmem_to_nmdesc()` and account for `NET_IOV` encoded references.

## Control Flow, State, and Persistence
State is stored directly in the netmem/page descriptor fields `pp`, `pp_magic`, and `dma_addr`. `netmem_is_pp()` clears the `NET_IOV` tag and casts to `struct page` because current `page_type` layout is shared between `struct page` and `struct net_iov`. DMA index helpers warn and no-op for net_iov references because the index side table is page-based.

## Dependencies and Integration
Depends on page-pool bit definitions such as `PP_DMA_INDEX_MASK` and `PP_DMA_INDEX_SHIFT`, PageNetpp flags, netmem conversion helpers, and the page-pool DMA mapping xarray in `page_pool.c`.

## Risks and Test Signals
Risks are layout-sensitive: comments explicitly note the cast relies on shared offsets between page and net_iov. DMA index overflow or misuse on net_iov should trigger WARNs. Test signals include PageNetpp set/clear on page-backed netmem, DMA index round trips preserving non-index magic bits, and no corruption when net_iov references pass through unsupported index helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netmem_priv.h -->
