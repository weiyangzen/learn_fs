# sources/distributed-fs/ceph-client/net/bluetooth/6lowpan.c

## Purpose
This module implements IPv6 6LoWPAN over Bluetooth Low Energy L2CAP IPSP. It creates virtual `bt%d` 6LoWPAN net_devices, maps BLE peers to IPv6 link-layer addresses, compresses/decompresses IPv6 packets, and exposes debugfs controls for enabling, connecting, and disconnecting peers.

## Important APIs, Types, And Functions
Important state types are `lowpan_btle_dev` for one virtual 6LoWPAN device per HCI controller, `lowpan_peer` for one L2CAP peer, and `skb_cb` for transmit routing metadata in `skb->cb`. The main data paths are `chan_recv_cb()`, `recv_pkt()`, `iphc_decompress()`, `bt_xmit()`, `setup_header()`, `send_pkt()`, and `send_mcast_pkt()`. Control and lifecycle functions include `bt_6lowpan_connect()`, `bt_6lowpan_disconnect()`, `bt_6lowpan_listen()`, `chan_ready_cb()`, `chan_close_cb()`, `setup_netdev()`, `disconnect_all_peers()`, debugfs handlers, and module init/exit.

## Control Flow
When enabled through debugfs, work in `do_enable_set()` toggles `enable_6lowpan`, closes any old listener, optionally disconnects existing peers, and creates a listening LE credit-flow L2CAP channel on IPSP. A new connection allocates or finds the HCI-scoped virtual netdev, adds a peer derived from the channel destination address, schedules neighbor notification, and opens the netdev. RX packets arrive from L2CAP, locate the peer and device, validate 6LoWPAN type, decompress IPHC or strip uncompressed IPv6 dispatch, and feed an aligned copy into `netif_rx()`. TX packets are unshared, compressed with `lowpan_header_compress()`, mapped to a peer by route/gateway/neighbour cache for unicast or cloned to all peers for multicast, and sent through `l2cap_chan_send()`.

## State, Persistence, And Dependencies
Global runtime state consists of `bt_6lowpan_devices`, `devices_lock`, `enable_6lowpan`, `listen_chan`, and `set_lock`. Peer objects are RCU-list entries freed by `kfree_rcu()` and hold L2CAP channel references plus derived EUI-48 and IPv6 addresses. Device objects live in lowpan netdev private data and are removed through unregister paths or delayed work. There is no persistent storage; debugfs state and connections are runtime-only.

## Integration Points
The module integrates with Bluetooth HCI/L2CAP, Linux 6LoWPAN compression, IPv6 routing and neighbor lookup, net_device registration, debugfs under `bt_debugfs`, and the netdevice notifier chain. It depends on `CONFIG_BT_LE` and generic `6LOWPAN` support through Kconfig.

## Risks
The code mixes RCU iteration, `devices_lock`, L2CAP channel locking, module reference counting, and asynchronous work, so teardown ordering is the main risk. `send_mcast_pkt()` clones and immediately frees clones after `send_pkt()`, relying on L2CAP send behavior and `chan->data` use. Debugfs parsing preserves a historical address-type mismatch for disconnect commands, which can surprise users. TX route selection uses cached gateway information in `skb->cb`, so missing routes or stale neighbours can drop packets.

## Test Signals
Test signals include creating and removing `bt%d` devices on connect/disconnect, correct debugfs enable/listen behavior, IPv6 ping over BLE with compressed and uncompressed packets, multicast neighbor discovery reaching all peers, queue stop/wake on L2CAP suspend/resume, netdev unregister cleanup without leaks, and lockdep/KASAN under repeated enable/disable and peer churn.
