# sources/distributed-fs/ceph-client/include/net/page_pool/memory_provider.h

Purpose: declares the page_pool external memory-provider interface used for netmem/net_iov backed RX buffers, including queue binding and provider lifecycle hooks.

Important APIs and types: `struct memory_provider_ops` supplies provider allocation, release, init/destroy, netlink fill, and uninstall callbacks. Helpers set DMA address and page_pool backpointers on net_iov objects, open/close RX queue memory providers, and place accounted netmem directly into the page_pool allocation cache from provider allocation paths.

Control flow: netdev queue setup binds a memory provider via `netif_mp_open_rxq()`, page_pool calls provider `alloc_netmems()` and `release_netmem()`, netlink can query provider state through `nl_fill()`, and queue teardown invokes close/uninstall/destroy.

State and persistence: provider-private state is referenced by `mp_priv`; page_pool records provider ops/private pointers and net_iov metadata. Configuration persists only as runtime queue binding.

Dependencies and integration points: integrates page_pool, netmem/net_iov, netdev RX queues, netlink extack, and skbuff netlink reporting.

Risks and test signals: risks include placing netmem into a full cache, mismatched page_pool/net_iov backpointers, stale DMA address metadata, queue close races, and drivers reading unreadable netmem. Test provider bind/unbind, allocation/release loops, netlink dumps, unreadable buffer RX paths, DMA address setup, and queue teardown under traffic.
