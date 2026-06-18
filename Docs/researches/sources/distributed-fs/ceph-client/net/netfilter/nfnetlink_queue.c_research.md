# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_queue.c

## Purpose
`nfnetlink_queue.c` implements NFQUEUE, the userspace verdict path for netfilter packets. It creates per-net queue instances owned by netlink sockets, serializes queued packet metadata/payload to userspace, receives verdicts and optional packet modifications, reinjects packets into the hook pipeline, and flushes queued packets when devices, hooks, namespaces, or userspace sockets disappear.

## Important APIs, Types, and Functions
The central state is `struct nfqnl_instance`, with a queue list, packet-id sequence, rhashtable mapping ids to `struct nf_queue_entry`, peer port id, max length, copy mode/range, flags, and drop counters. It is stored in per-net `struct nfnl_queue_net`.

Queue integration is through `struct nf_queue_handler nfqh` and `nfqnl_enqueue_packet()`. Message building is `nfqnl_build_packet_message()`. Reinjection uses `nfqnl_reinject()` and `nf_reinject()`. Verdict callbacks are `nfqnl_recv_verdict()` and `nfqnl_recv_verdict_batch()`. Configuration is `nfqnl_recv_config()`. Lifecycle and cleanup use `instance_create()`, `instance_destroy()`, `instance_destroy_work()`, `nfqnl_flush()`, device and netlink notifiers, and per-net procfs sequence operations.

## Control Flow, State, and Persistence
Userspace binds a queue with `NFQNL_CFG_CMD_BIND`, then sets copy mode, copy range, max length, and flags such as fail-open, conntrack, GSO, UID/GID, and secctx. When a rule queues a packet, `nfqnl_enqueue_packet()` finds the queue under RCU, rejects copy-none queues, normalizes skb protocol for IPv4/IPv6, rejects unsafe unconfirmed conntrack sharing, and either enqueues the skb or segments GSO packets unless GSO passthrough is enabled.

`nfqnl_build_packet_message()` sizes and fills an nfnetlink packet message with packet id pointer, hook, ifindexes, mark, priority, hardware header, bridge/VLAN metadata, timestamp, UID/GID, cgroup classid, secctx, conntrack attributes, captured length, checksum/GSO flags, and optional zerocopy payload. `__nfqnl_enqueue_packet()` assigns an id, inserts the entry into the rhashtable before unicast, and handles full queues or unicast failure by dropping or fail-opening.

Verdicts are accepted only from the owning port id. Single verdict lookup dequeues by id, optionally parses conntrack/expectation data, applies bridge VLAN/L2 edits, mangles payload length/content, updates mark/priority, then reinjects. Batch verdict dequeues every queued id up to a max id and applies the same verdict/mark/priority. Reinjection updates conntrack first, re-routes local-output packets if address/mark changed, resumes hook iteration after the original hook, and finally calls `okfn`, queues again, steals, or frees.

Persistent state includes queue instances, queued entries and id map, rcu-work destruction, ordered cleanup workqueue, procfs diagnostics, registered queue handler, netdevice notifier for flushing downed-device packets, netlink notifier for peer close, and per-net instance hash buckets.

## Dependencies and Integration Points
The file integrates nf_queue core, nfnetlink subsystem `NFNL_SUBSYS_QUEUE`, IPv4/IPv6 rerouting, bridge netfilter metadata, GSO segmentation, conntrack update and netlink build/parse hooks, LSM secctx, cgroup classid, netdevice and netlink notifiers, rhashtable, procfs, and per-net namespace lifecycle.

## Risks and Test Signals
Risks include queue id wrap/batch ordering, rhashtable/list consistency, fail-open semantics, userspace port ownership, packet mangle length validation, checksum/GSO handling, unconfirmed conntrack parallelism, reinjection hook index correctness, local-output reroute after modifications, and cleanup ordering with RCU work. Tests should bind/configure/unbind queues, enqueue under every copy mode, hit maxlen and unicast failure with/without fail-open, send single and batch verdicts, modify payload/mark/priority/VLAN/L2 headers, exercise GSO segmentation, conntrack metadata round-trip, device-down flush, peer close destruction, procfs counters, and namespace teardown.
