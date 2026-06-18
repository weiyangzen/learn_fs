# sources/distributed-fs/ceph-client/net/appletalk/aarp.c

Purpose: implements AppleTalk Address Resolution Protocol for EtherTalk plus proxy AARP support and optional procfs reporting. It resolves AppleTalk network/node addresses to Ethernet MAC addresses and queues DDP frames while resolution is pending.

Important APIs, types, and functions: `struct aarp_entry` stores refcount, queued packets, status, expiry, target address, device, hardware address, retransmit count, and hash linkage. Global tables `resolved`, `unresolved`, and `proxies` are protected by `aarp_lock`. Externally used functions include `aarp_proto_init`, `aarp_cleanup_module`, `aarp_send_ddp`, `aarp_device_down`, `aarp_probe_network`, `aarp_proxy_probe_network`, and `aarp_proxy_remove`.

Control flow: `aarp_send_ddp` handles LocalTalk and PPP directly, sends AppleTalk broadcast frames to the multicast address, looks up resolved Ethernet mappings, queues packets on unresolved entries, and sends AARP requests. The timer expires resolved/proxy entries and retransmits unresolved queries until `sysctl_aarp_retransmit_limit`. `aarp_rcv` handles AARP replies, requests, and probes; replies resolve queued packets, while requests/probes for local or proxy addresses trigger replies and may flush stale cache entries.

State and persistence: global hash tables and the timer are module-local. Tunables `sysctl_aarp_expiry_time`, `sysctl_aarp_tick_time`, `sysctl_aarp_retransmit_limit`, and `sysctl_aarp_resolve_time` are mutable via sysctl when enabled. State is runtime-only and scoped to `init_net`.

Dependencies and integration points: depends on SNAP registration (`register_snap_client`), DDP datalink operations, netdevice notifier events, AppleTalk interface lookup from DDP, Ethernet helpers, timers, and optional proc seq operations (`aarp_seq_ops`).

Risks: one global rwlock protects all tables and is used in softirq contexts with atomic allocations. `unresolved_count` must stay balanced; unresolved entries queue skbs and can drop traffic under memory pressure. Proxy probing temporarily releases and reacquires locks while retaining entry references. The code does not use generic neighbour infrastructure.

Test signals: AARP request/reply/probe exchange, duplicate address detection, proxy add/remove, device down purging, sysctl timer changes, proc `atalk/arp` iteration, queued packet release on resolution, retransmit-limit expiry, and non-init-net packet rejection.
