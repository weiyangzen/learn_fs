# sources/distributed-fs/ceph-client/drivers/net/ovpn/main.c

Purpose: registers and configures the `ovpn` rtnl link type and module lifecycle for OpenVPN data channel offload.

Important APIs/types/functions: `ovpn_setup()` initializes netdev properties. `ovpn_newlink()` sets mode, initializes private state, keepalive work, carrier, and registers the device. `ovpn_dellink()` cancels keepalive work and frees peers. `ovpn_net_init()`/`uninit()` manage GRO cells and MP peer container allocation. `ovpn_dev_is_valid()` identifies ovpn devices. `ovpn_init()`/`ovpn_cleanup()` handle module registration.

Control flow: module init registers rtnl link ops, registers the ovpn generic netlink family, and initializes TCP support. Device setup configures ARPHRD_NONE, point-to-point/noarp flags, no queue, dst retention, features, MTU bounds adjusted by `OVPN_HEAD_ROOM`, and tailroom. Newlink accepts P2P or MP mode, initializes locks and work, sets MP carrier on or P2P carrier off, then registers the netdev. Delling frees peers with teardown reason before unregistering.

State and persistence: `struct ovpn_priv` stores dev pointer, mode, lock, peer collection pointer, GRO cells, and keepalive work. MP mode allocates hash tables for peer lookups; P2P uses simpler peer state elsewhere. State is volatile.

Dependencies and integration: integrates with rtnl link ops, generic netlink registration, GRO cells, IPv4 redirect sysctl adjustment for MP mode, peer management, TCP/UDP transports, and ethtool.

Risks: MP allocation disables redirects on the interface and globally for the netns, which is intentional but broad. Peer cleanup and delayed keepalive cancellation must precede unregister. `netns_refund = false` affects namespace ref behavior.

Test signals: create P2P and MP ovpn links, inspect rtnl mode fill-info, verify carrier behavior, allocate/free MP peer tables, check MTU/headroom values, register/unregister netlink family, and teardown with active peers/keepalive work.
