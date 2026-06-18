<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev_rx_queue.c -->
# sources/distributed-fs/ceph-client/net/core/netdev_rx_queue.c

## Purpose
RX queue lease and memory-provider lifecycle support. It links virtual RX queues to physical RX queues, redirects memory-provider operations through leases, and restarts/reconfigures RX queues when provider settings change.

## APIs, Types, and Functions
Queue lease APIs are `netdev_rx_queue_lease()`, `netdev_rx_queue_unlease()`, `netif_rxq_is_leased()`, `netif_is_queue_leasee()`, and `__netif_get_rx_queue_lease()`. Memory-provider APIs are `netif_rxq_has_unreadable_mp()`, `netif_rxq_has_mp()`, `netif_mp_open_rxq()`, `netif_mp_close_rxq()`, `__netif_mp_uninstall_rxq()`, and `netif_rxq_cleanup_unlease()`. `netdev_rx_queue_restart()` is exported in the `NETDEV_INTERNAL` namespace.

## Control Flow, State, and Persistence
Leasing stores reciprocal `rxq->lease` pointers and holds the physical device with a tracker; unlease clears both sides and drops the hold after memory-provider cleanup. RX queue reconfig allocates new and old driver memory blobs, calls driver allocate/stop/start/free callbacks, and attempts to restore old state if starting the new queue fails. Memory-provider open validates HDS/TCP data split state, absence of XDP programs and AF_XDP pools, queue support for `rx_page_size`, then stores `rxq->mp_params`, validates effective queue config, and reconfigures the queue. Close verifies the old provider identity, clears params, and reconfigures back.

## Dependencies and Integration
Depends on netdev locks, `queue_mgmt_ops`, ethtool HDS config, XDP program counts, page-pool memory-provider validation, AF_XDP pool state, and page-pool private helpers. Lease cleanup integrates with queue unlease so a provider installed through a virtual queue is removed from the physical queue.

## Risks and Test Signals
Risks include failure recovery if `ndo_queue_start()` cannot restore old memory, WARN-only handling for provider identity mismatches, lease direction mistakes, races with device unregister, and policy coupling to TCP data split. Test signals are successful reconfiguration on running and down devices, injected callback failures with old queue restoration, provider open/close through leased queues, unlease cleanup of physical provider state, AF_XDP/XDP/HDS rejection paths, and restart behavior returning `-ENETDOWN` only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netdev_rx_queue.c -->
