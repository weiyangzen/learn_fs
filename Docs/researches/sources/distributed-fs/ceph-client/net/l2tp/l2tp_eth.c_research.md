# sources/distributed-fs/ceph-client/net/l2tp/l2tp_eth.c

## Purpose
Implements the L2TPv3 Ethernet pseudowire. It creates one virtual Ethernet net_device per L2TP Ethernet session, transmits Ethernet frames through `l2tp_xmit_skb`, and injects received L2TP payloads into the network stack as Ethernet frames.

## Important APIs, types, and functions
- `struct l2tp_eth` is netdev private state and points to the core session.
- `struct l2tp_eth_sess` is session private state and stores the RCU-protected net_device pointer.
- `l2tp_eth_dev_setup`, `l2tp_eth_dev_init`, and `l2tp_eth_dev_uninit` configure the Ethernet net_device, random MAC, stats, lockdep classes, and RCU pointer clearing.
- `l2tp_eth_dev_xmit` sends outbound frames via `l2tp_xmit_skb`.
- `l2tp_eth_dev_recv` validates `ETH_HLEN`, resets outer tunnel metadata, forwards the skb to the net_device, and updates stats.
- `l2tp_eth_create` is the netlink pseudowire create callback.
- `l2tp_eth_delete` unregisters the net_device on session close.

## Control flow
Module init registers `l2tp_eth_nl_cmd_ops` for `L2TP_PWTYPE_ETH`. Netlink session creation calls `l2tp_eth_create`, which creates a core session with private storage, allocates and configures a net_device, sets session callbacks, registers the session and device under RTNL, stores the device name in the session, publishes the RCU device pointer, and pins the module. TX from the netdev calls the core transmit path. RX from the core callback strips tunnel metadata and forwards the frame through `dev_forward_skb`.

## State and persistence behavior
State is runtime-only: one net_device plus one core session per pseudowire. The device pointer in session private data is RCU protected and cleared during netdev uninit. The module reference is incremented on successful create and decremented after unregister in delete. MTU is adjusted from tunnel destination MTU, IP/UDP overhead, Ethernet header, and L2TP session header length.

## Dependencies and integration points
Depends on the L2TP core, generic netlink pseudowire registration, net_device APIs, RTNL, Ethernet helpers, RCU, per-cpu dstats, and tunnel socket MTU helpers. Debugfs integration is optional through `session->show`.

## Risks and test signals
Risks include create/delete races between session and device registration, MTU under/overflow when route MTU is unknown or small, RCU pointer lifetime, module reference balance, and handling malformed short Ethernet payloads. Test signals include netlink creation producing an `l2tpeth*` interface, successful bridge/IP use, TX/RX stats movement, unregister on session delete, custom ifname handling, and debugfs interface output.
