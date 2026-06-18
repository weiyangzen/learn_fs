# sources/distributed-fs/ceph-client/drivers/net/ntb_netdev.c

Purpose: provides an Ethernet netdevice over PCIe Non-Transparent Bridge transport queue pairs, exposing NTB links as network interfaces.

Important APIs/types/functions: `struct ntb_netdev` owns the pci/client device, netdev, queue count, and queue array. `struct ntb_netdev_queue` stores a transport QP, qid, and tx reaper timer. `ntb_netdev_probe()`/`remove()` manage device lifetime. `ntb_netdev_open()`/`close()`, `ntb_netdev_start_xmit()`, RX/TX handlers, MTU change, and ethtool channel ops implement data path and configuration.

Control flow: probe allocates an Ethernet netdev with up to 64 queues, creates default QPs, sets real queues and MTU from transport max size, registers the netdev, and stores drvdata. Open fills each QP with RX buffers, initializes timers, stops tx, and brings NTB links up. RX handler converts completed buffers into skbs for `netif_rx()` and immediately posts replacements. TX enqueues skb data to the QP and stops/wakes subqueues based on free descriptors, tx timer, and link events. Channel changes create or free QPs and resize real queues, with rollback on failure.

State and persistence: queue/QP pointers, timers, queue count, and netdev stats are volatile. Module parameters `tx_time`, `tx_start`, and `tx_stop` tune queue wake/stop thresholds.

Dependencies and integration: depends on NTB transport client APIs, PCI device metadata, netdev and ethtool ops, timers, and Ethernet helpers. It registers as an NTB transport client in late init.

Risks: RX buffer refill failures can leave the device short of buffers or inoperable after MTU growth failure. TX flow control relies on memory barriers around free-entry checks. Channel resize while running must coordinate subqueue state, QP link state, timers, and queue publication order.

Test signals: probe with NTB transport, open/close links, transmit under descriptor pressure, force link events, change MTU below/above transport max, increase/decrease ethtool combined channels while running, and verify removal frees QPs and timers.
