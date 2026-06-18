# sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan.h

Purpose: Defines shared data structures, constants, inline helpers, and cross-file function declarations for the ipvlan driver.

Important APIs and types: Constants define driver name/version, address hash sizes, MAC filter bitmap size, and multicast backlog limit. `ipvl_hdr_type` classifies IPv4, IPv6, ICMPv6, and ARP headers. `struct ipvl_pcpu_stats` stores per-CPU RX/TX counters with sync protection. `struct ipvl_dev` represents an ipvlan netdev, `struct ipvl_addr` tracks per-device L3 addresses in hash/list form, `struct ipvl_port` represents the lower-device port and address hash tables, and `struct ipvl_skb_cb` stores skb control metadata. Inline helpers retrieve `ipvl_port` under RCU/BH/RTNL and manipulate PRIVATE/VEPA flags.

Control flow and integration: The header connects `ipvlan_core`, `ipvlan_main`, optional `ipvlan_l3s`, and ipvtap-facing code. RX handlers use `ipvlan_handle_frame()`, address lookup uses the port hash table helpers, TX uses `ipvlan_queue_xmit()`, multicast backlog processing uses workqueue state in `ipvl_port`, and rtnetlink setup uses link creation/deletion/register declarations. Optional L3S functions compile to real declarations or harmless stubs depending on `CONFIG_IPVLAN_L3S`.

State and persistence: Runtime state is in `ipvl_port` lower-device attachment, RCU-protected address tables, per-device address lists, per-CPU statistics, MAC filter bitmaps, backlog queues, IDA allocation, and netdevice tracking. No durable persistence exists; state follows netdev lifecycle and network namespace movement.

Dependencies and integration points: Includes core networking, RCU, notifier, netdevice, VLAN, IPv4/IPv6 route/address, netfilter, rtnetlink, l3mdev, and namespace headers. It integrates with Linux rx_handler attachment, rtnl link operations, per-CPU stats, workqueues, and optional L3S netfilter hook behavior.

Risks: RCU/RTNL accessor choice matters; using the wrong helper can race port teardown. Address hash/list mutation is guarded by `addrs_lock` and must coordinate with RCU freeing. `skb->cb` overlay must not conflict with other users along the path. Backlog limit and multicast processing affect memory pressure and delivery ordering. Optional L3S stubs return success for init/cleanup but `ipvlan_l3s_register()` returns `-ENOTSUPP`, so callers must tolerate feature absence.

Test signals: Build with and without `CONFIG_IPVLAN_L3S`; create/delete ipvlan links in L2/L3/L3S modes; add/remove IPv4 and IPv6 addresses; exercise RX demux, TX queueing, multicast backlog, PRIVATE/VEPA flags, namespace migration, statistics accounting, and lower-device teardown under traffic.
