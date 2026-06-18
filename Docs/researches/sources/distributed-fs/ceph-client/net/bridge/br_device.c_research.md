<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_device.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_device.c

Purpose: implements the bridge net_device operations, transmit path from the bridge device, device initialization/uninitialization, open/stop behavior, ethtool reporting, netpoll support, slave add/delete hooks, forward-path reporting, and bridge private structure setup.

Important APIs, types, and functions: `br_dev_xmit` is the bridge master transmit routine. Lifecycle helpers are `br_dev_init`, `br_dev_uninit`, `br_dev_open`, `br_dev_stop`, `br_change_mtu`, `br_set_mac_address`, and `br_dev_setup`. Netpoll helpers include `br_netpoll_enable` and `br_netpoll_disable` when configured. `br_add_slave` and `br_del_slave` call port attach/detach code. `br_fill_forward_path` describes hardware/software forwarding paths for upper stack consumers. `nf_br_ops` is an exported RCU pointer for bridge netfilter hooks.

Control flow: transmit validates Ethernet header, clears bridge skb control state, lets bridge netfilter intercept, accounts TX stats, strips the Ethernet header, validates VLAN ingress, optionally performs ARP/ND proxy suppression, then classifies destination as broadcast, multicast, known unicast, or unknown unicast. Broadcast and unknown unicast flood, multicast consults snooping/MDB/querier state, and known unicast forwards to the FDB destination port. Device init builds FDB/MDB/VLAN/multicast stats state with unwind on errors. Open starts the queue, enables STP and multicast; stop disables them and stops the queue. Setup initializes netdev ops, features, flags, bridge lists, locks, STP defaults, netfilter fake route, timers, multicast, and FDB garbage collection work.

State and persistence: persistent bridge state is allocated in `netdev_priv(dev)` as `struct net_bridge`. It owns port, FDB, frame type, MRP, CFM, and hash lists; locks; options; timers; multicast/VLAN/FDB/MDB data; STP bridge IDs and timers; and per-CPU stats. MTU changes set `BROPT_MTU_SET_BY_USER`. Netpoll state attaches to ports while enabled.

Dependencies and integration points: integrates with net_device ops, bridge FDB/MDB/VLAN/multicast/STP/netlink/ioctl code, bridge netfilter, netpoll, ethtool, switchdev forwarding path API, neighbor suppression helpers, and optional CFM/MRP list initialization.

Risks: `br_dev_xmit` runs with BH disabled and relies on RCU-protected bridge data. Incorrect skb header movement or VLAN ingress handling can corrupt forwarding. Multicast logic must free or forward skb exactly once. Init/uninit unwind must mirror allocations. `br_fill_forward_path` mutates VLAN stack context and can underflow if caller state is inconsistent.

Test signals: bridge forwarding tests for broadcast/multicast/known/unknown unicast, VLAN ingress filtering, neighbor suppression on locally originated packets, multicast snooping/MDB paths, MTU and MAC changes, open/stop STP transitions, netpoll setup/cleanup, add/delete slave operations, ethtool link settings, and device teardown leak/UAF checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_device.c -->
