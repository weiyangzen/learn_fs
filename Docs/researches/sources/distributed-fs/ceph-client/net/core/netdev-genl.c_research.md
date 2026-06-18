<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev-genl.c -->
# sources/distributed-fs/ceph-client/net/core/netdev-genl.c

## Purpose
Generic-netlink control plane for the netdev family. It exposes device capabilities, NAPI configuration, queue topology, queue statistics, dmabuf-backed netmem bindings, and dynamic RX queue leasing/creation to user space, and emits multicast notifications for netdev add/delete/change events.

## APIs, Types, and Functions
The dump cursor is `struct netdev_nl_dump_ctx`. Main command handlers include `netdev_nl_dev_get_doit/dumpit()`, `netdev_nl_napi_get_doit/dumpit()`, `netdev_nl_napi_set_doit()`, `netdev_nl_queue_get_doit/dumpit()`, `netdev_nl_qstats_get_dumpit()`, `netdev_nl_bind_rx_doit()`, `netdev_nl_bind_tx_doit()`, and `netdev_nl_queue_create_doit()`. Helpers fill nested netlink attributes for device XDP/XSK features, NAPI IRQ/threading/defer timers, RX/TX queue NAPI IDs, queue leases, memory providers, AF_XDP pools, and queue stats. `netdev_stat_queue_sum()` is exported for drivers to combine disabled queue counters into base stats.

## Control Flow, State, and Persistence
GET commands allocate a reply skb, lock the addressed netdev or NAPI object, serialize attributes, unlock, then reply. Dumps persist ifindex and queue/NAPI indexes in callback context. NAPI SET mutates threaded mode and defer/timeout knobs under the netdev lock. RX dmabuf bind parses a nested queue bitmap, verifies all selected queues share one DMA device, creates a `net_devmem_dmabuf_binding`, binds each queue, and stores socket-owned bindings in `struct netdev_nl_sock`. Queue creation validates a virtual destination device, resolves a physical lease device possibly in a peer netns, locks virtual then physical devices, creates an RX queue through driver `queue_mgmt_ops`, and links the virtual/physical RX queues. Socket-private destroy walks bindings and unbinds them with device locking.

## Dependencies and Integration
Depends on generated `netdev-genl-gen.h`, generic netlink, rtnetlink/netdev locks, `netdev_queue_mgmt_ops`, queue-stat ops, AF_XDP pool state, XDP metadata ops, dmabuf devmem support, page-pool memory-provider callbacks, network namespace peer IDs, and the netdevice notifier chain. `subsys_initcall()` registers both notifier and netlink family.

## Risks and Test Signals
High-risk areas are lock ordering across virtual and physical devices, rollback after partial dmabuf queue binding, dump cursor correctness, stats omission via all-`0xff` sentinel structs, namespace ID allocation in lease reporting, and driver callback failures during queue creation. Useful test signals include genetlink GET/DUMP coverage with small skb buffers, NAPI set/get round trips, queue lease across netns, dmabuf bind/unbind on socket close, `-EOPNOTSUPP` paths for devices without ops locks or netmem TX, and notifier delivery for register/unregister/XDP feature changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev-genl.c -->
