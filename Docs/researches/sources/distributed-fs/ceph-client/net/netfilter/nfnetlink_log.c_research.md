# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_log.c

## Purpose
`nfnetlink_log.c` implements the NFLOG userspace logging backend. It binds per-net logging instances to netlink port ids and groups, accepts configuration for copy mode/range, buffer size, flush timeout, queue threshold, and metadata flags, then batches logged packet metadata and optional payload into nfnetlink unicast messages.

## Important APIs, Types, and Functions
The central state object is `struct nfulnl_instance`, stored in per-net `struct nfnl_log_net::instance_table`. It tracks peer port/user namespace, current batching skb, queue length, timer, copy mode/range, sequence flags, and group number.

Packet logging is `nfulnl_log_packet()` through `struct nf_logger nfulnl_logger`. Message construction is `__build_packet_message()`, with allocation/sending via `nfulnl_alloc_skb()`, `__nfulnl_send()`, and `__nfulnl_flush()`. Instance lifecycle uses `instance_create()`, `instance_lookup_get()`, `instance_destroy()`, `__instance_destroy()`, `instance_put()`, and timer callback `nfulnl_timer()`. Configuration is `nfulnl_recv_config()`.

## Control Flow, State, and Persistence
Userspace binds an instance for a group with `NFULNL_CFG_CMD_BIND`; the creating port id owns subsequent configuration and receives logs. Per-protocol-family bind/unbind commands register or unregister the NFLOG logger for that family. On log events, `nfulnl_log_packet()` resolves the group instance under RCU, computes the netlink message size for requested metadata, applies per-rule qthreshold overrides, and locks the instance.

Copy mode controls payload inclusion: none/meta omit payload, packet copies up to instance range and optional per-rule copy length. Optional flags add local and global sequence numbers and conntrack metadata. Bridge/netdev packets can include VLAN and L2 headers. Socket credentials are translated into the peer user namespace. If the current batching skb lacks tailroom, the instance flushes before appending. Flush occurs when qthreshold is reached or when the timer fires.

Persistent state is per-net group instances, per-instance timers and batched skbs, global sequence atomic counter, procfs status rows, netlink-notifier cleanup on peer release, and nf_logger registration.

## Dependencies and Integration Points
The file integrates nfnetlink subsystem `NFNL_SUBSYS_ULOG`, nf_log core registration, optional bridge netfilter metadata, optional conntrack netlink building via `nfnl_ct_hook`, procfs per-net diagnostics, netlink notifier release events, timers, RCU, spinlocks, netns references, and user namespace credential munging.

## Risks and Test Signals
Risks include batching skb size underestimation, timer/reference lifetime, owner port enforcement, netlink peer release cleanup, copy-range limits from 16-bit nla length, optional conntrack module autoload atomicity, bridge physical/logical ifindex mapping, and credential namespace conversion. Tests should cover bind/unbind, PF logger bind/unbind, all copy modes, qthreshold and timer flush, sequence flags, conntrack flag with and without hook loaded, bridge/VLAN metadata, procfs output, peer socket close destroying instances, and net namespace exit without leaked instances.
