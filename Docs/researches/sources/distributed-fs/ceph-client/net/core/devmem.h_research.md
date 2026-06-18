# sources/distributed-fs/ceph-client/net/core/devmem.h

Purpose: Internal header for dma-buf backed network device memory. It defines the binding object shared by netlink, RX queue memory providers, TX lookup, and `net_iov` ownership, plus inline helpers and stubs for builds without `CONFIG_NET_DEVMEM`.

Important APIs, types, and functions: `struct net_devmem_dmabuf_binding` owns the dma-buf, attachment, sg table, associated net_device, gen_pool, bound RX queue xarray, binding id, DMA direction, TX vector, mutex, percpu ref, netlink list node, and deferred unbind work. `struct dmabuf_genpool_chunk_owner` ties gen_pool chunks to `net_iov_area` metadata and base DMA addresses. Inline helpers map `net_iov` values to owners, bindings, binding ids, virtual addresses, and percpu-ref get/put. Prototypes cover bind, queue bind, lookup, unbind, `net_iov` ref management, allocation/free, TX binding lookup, and virtual-address lookup.

Control flow and state: The header documents the intended lifetime: userspace holds a binding reference through netlink, each page pool holds a reference, and individual `net_iov` users can hold references so the dma-buf mapping outlives skbs in flight. Virtual addresses are synthetic offsets within the dma-buf, computed from owner base plus `net_iov_idx() << PAGE_SHIFT`; DMA addresses are derived in the C file from each chunk owner.

Dependencies and integration points: It depends on `net/netmem.h`, `net/netdev_netlink.h`, netlink extack types, dma-buf types, xarray, gen_pool, page-pool memory provider parameters, and sockets for TX binding lookup. With `CONFIG_NET_DEVMEM` disabled, it returns `-EOPNOTSUPP`, `NULL`, or no-op stubs so callers can compile without feature-specific ifdefs.

Risks: The binding struct is shared across asynchronous paths, so field ownership must be respected. `binding->dev` is protected by `binding->lock` for updates but read with `READ_ONCE()` in TX lookup. Stubs must preserve caller expectations: disabled builds should fail cleanly rather than silently allowing devmem behavior. Virtual address arithmetic assumes page-sized `net_iov` slots.

Test signals: Build coverage with `CONFIG_NET_DEVMEM=y` and disabled is essential. Runtime signals are correct netlink bind/unbind reporting, stable binding ids, correct `net_iov` to binding/id mapping, and no stale binding access when queue uninstallation clears the device pointer.
