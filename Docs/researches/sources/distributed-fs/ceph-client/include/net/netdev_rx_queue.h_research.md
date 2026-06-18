<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_rx_queue.h -->
# sources/distributed-fs/ceph-client/include/net/netdev_rx_queue.h

## Purpose
`netdev_rx_queue.h` defines the per-RX-queue object, sysfs attribute wrapper, RX queue index helpers, lease lookup, and restart/lease management functions.

## Important APIs, types, and functions
It defines `struct netdev_rx_queue`, `struct rx_queue_attribute`, `__netif_get_rx_queue`, `get_netdev_rx_queue_index`, lease direction enum, `__netif_get_rx_queue_lease`, `netdev_rx_queue_restart`, `netdev_rx_queue_lease`, and `netdev_rx_queue_unlease`.

## Control flow
Network core stores one `netdev_rx_queue` per RX queue with XDP RXQ info, optional RPS/XSK state, sysfs kobject, NAPI pointer, queue config, page-pool memory-provider parameters, and optional bidirectional lease link. Restart and lease helpers coordinate physical and virtual queues.

## State and persistence
Runtime state is per queue and ops-protected below the kobject/device fields: XDP/RPS/XSK/page-pool settings, NAPI binding, queue config, memory-provider params, lease pointer, and netdevice trackers.

## Dependencies and integration points
It depends on kobject/sysfs, netdevice, XDP, page_pool, RPS, and queue config types. It integrates RX queue sysfs, XDP, AF_XDP, page pools, and queue leasing.

## Risks and test signals
Risks include queue index calculation after resize, lease pointer lifetime, tracker mismatches, restarting an active queue with unreadable memory provider, and sysfs access during teardown. Tests should cover queue resize, sysfs reads/writes, XDP/XSK attach, queue lease/unlease both directions, and restart error paths.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netdev_rx_queue.h` completely for this pass (84 lines, 2301 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_rx_queue.h -->
