<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/page_pool_priv.h -->
# sources/distributed-fs/ceph-client/net/core/page_pool_priv.h

## Purpose
Private declarations and inlines shared between page-pool core, page-pool netlink user exposure, and netdev RX queue memory-provider code.

## APIs, Types, and Functions
Declares `page_pools_lock`, `page_pool_inflight()`, `page_pool_list()`, `page_pool_detached()`, `page_pool_unlist()`, `page_pool_set_pp_info()`, `page_pool_clear_pp_info()`, and `page_pool_check_memory_provider()`. Provides `page_pool_set_dma_addr_netmem()` and `page_pool_set_dma_addr()` for DMA address storage, including 32-bit architecture compression for 64-bit DMA addresses.

## Control Flow, State, and Persistence
The DMA helper stores either the full address or a page-shifted compressed address in netmem descriptor state and returns true when compression cannot round-trip exactly. `CONFIG_PAGE_POOL` stubs make metadata and provider checks no-ops when the feature is unavailable.

## Dependencies and Integration
Depends on page-pool helper types, `netmem_priv.h`, DMA address width macros, and netdev/RX queue declarations. It is the private contract connecting `page_pool.c`, `page_pool_user.c`, and `netdev_rx_queue.c`.

## Risks and Test Signals
Risks are mostly ABI/layout and architecture related: incorrect compressed DMA storage on 32-bit systems with 64-bit DMA would corrupt mappings. Test signals include round-trip tests for page-aligned DMA addresses, failure on unrepresentable DMA addresses, build coverage with and without `CONFIG_PAGE_POOL`, and memory-provider validation calls from queue reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/page_pool_priv.h -->
