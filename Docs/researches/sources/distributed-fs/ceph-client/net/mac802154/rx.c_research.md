# sources/distributed-fs/ceph-client/net/mac802154/rx.c

Purpose: implements the mac802154 receive path from driver-provided skb to monitor delivery, per-interface filtering, LLSEC decrypt, MAC-command/beacon work dispatch, and data-frame delivery.

Important APIs and functions: `ieee802154_rx_irqsafe()` queues RX skbs from interrupt context. `ieee802154_rx()` handles suspension, optional FCS synthesis/checking, monitor clones, CRC removal, and interface fanout. `ieee802154_subif_frame()` applies destination/PAN filtering, decrypts, updates stats, and dispatches beacon/MAC/data frames. `mac802154_rx_beacon_worker()` and `mac802154_rx_mac_cmd_worker()` process queued management frames.

Control flow and state: packets are parsed into `mac_cb`, cloned per running non-monitor interface under RCU, filtered against required hardware/software levels, decrypted with per-interface LLSEC state, then either delivered to the network stack or queued to `local->rx_beacon_list`/`rx_mac_cmd_list` for `mac_wq`. Monitor interfaces receive full frames before CRC stripping.

Dependencies and integration: depends on CRC helpers, IEEE header parsing, LLSEC, scan/association handlers in `scan.c`, netif receive, tasklets, RCU interface lists, and workqueues initialized by `main.c`.

Risks and test signals: queued beacon/MAC lists are manipulated without an explicit local lock in this file, so single-threaded `mac_wq` assumptions matter. Decryption occurs before monitor-safe header rewriting, noted by TODO. Test signals include bad FCS drop, filtering by PAN/address, scan-only beacon acceptance, MAC command dispatch, and stats increments only on accepted frames.
