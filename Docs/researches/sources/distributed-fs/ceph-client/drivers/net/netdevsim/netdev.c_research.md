# sources/distributed-fs/ceph-client/drivers/net/netdevsim/netdev.c

Purpose: implements the core simulated Ethernet net_device for netdevsim, including PF/VF netdev ops, peer forwarding, NAPI queues, page pools, XDP/BPF hooks, VLAN tracking, queue reset testing, and module registration.

Important APIs/types/functions: `nsim_create()`/`nsim_destroy()` allocate and free devices. `nsim_start_xmit()` forwards packets to a peer or loopback path after IPsec/PSP checks. `nsim_open()`/`nsim_stop()` manage NAPI and carrier. `nsim_queue_*` functions implement receive queue allocation and queue-management restart scenarios. Netdev ops include VF configuration, MTU, TC/BPF, VLAN add/kill, stats, and shaper stubs.

Control flow: PF initialization creates a mock PHC, UDP tunnel info, receive queues, BPF/MACsec/IPsec hooks, registers the netdevice, initializes PSP, and optional debug notifier. Transmit selects loopback or RCU peer, validates PSP/IPsec, maps skb to a receive queue, linearizes when configured HDS disallows nonlinear data, timestamps, queues to peer NAPI, starts a short hrtimer, and updates stats. NAPI drains queued skbs, optionally runs generic XDP, GRO-receives, and wakes peer tx queues. Destroy disconnects peers, unregisters, tears down feature modules, frees queues, validates VLAN cleanup, releases held page-pool page, and frees netdev.

State and persistence: `struct netdevsim` stores peer RCU pointer, queues, feature substructures, VF config references, VLAN bitmaps, debugfs dentries, page-pool hold state, and counters. All state is volatile per simulated device.

Dependencies and integration: integrates with net core, RTNL/netdev locking, NAPI, page_pool, XDP, BPF, TC, UDP tunnel offload, MACsec, IPsec, PSP, ethtool, devlink port assignment, debugfs, and rtnl link registration under kind `netdevsim`.

Risks: peer forwarding relies on RCU and queue count compatibility; queue-reset debugfs intentionally exercises unusual NAPI add/delete ordering. Page-pool hold/debug paths require running device state. Feature teardown ordering is important because several modules store netdev pointers or debugfs entries.

Test signals: create PF/VF ports, connect peers, run loopback and peer traffic, attach XDP/BPF, exercise queue reset modes 0-3, hold/release page-pool pages, add/remove VLAN filters, change MTU under XDP constraints, configure VFs, and verify destroy warnings for leaked VLANs/pages.
