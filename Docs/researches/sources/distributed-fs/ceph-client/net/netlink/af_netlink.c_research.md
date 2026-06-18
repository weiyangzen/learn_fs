# sources/distributed-fs/ceph-client/net/netlink/af_netlink.c

## Purpose

`af_netlink.c` is the core Linux `PF_NETLINK` socket implementation. It registers the netlink protocol family, creates user and kernel netlink sockets, manages per-protocol port ID lookup tables, multicast listener state, socket options, unicast and broadcast delivery, dump continuations, ACK/error replies, proc/BPF iteration, tap devices, and per-network-namespace proc setup.

This file is the common substrate used by rtnetlink, generic netlink, sock_diag, netfilter, xfrm, audit-style protocols, and any kernel subsystem creating a netlink kernel socket.

## Important APIs, Types, and Functions

The main persistent objects are `struct netlink_sock`, `struct netlink_table`, `struct listeners`, and the global `nl_table`. Socket creation uses `netlink_create()` for userspace sockets and `__netlink_kernel_create()` for kernel endpoints. Binding and addressing are handled by `netlink_bind()`, `netlink_connect()`, `netlink_autobind()`, `netlink_insert()`, `netlink_remove()`, and `netlink_lookup()`.

Delivery APIs include `netlink_unicast()`, `netlink_broadcast_filtered()`, `netlink_broadcast()`, `nlmsg_notify()`, `netlink_attachskb()`, `netlink_sendskb()`, and `netlink_detachskb()`. Message framing and control replies are built by `__nlmsg_put()`, `netlink_ack()`, `netlink_ack_tlv_len()`, and `netlink_ack_tlv_fill()`.

Long-running dumps use `__netlink_dump_start()` and the internal `netlink_dump()` state machine stored in `nlk->cb`. Userspace receive/send paths are `netlink_sendmsg()` and `netlink_recvmsg()`. Socket option handling lives in `netlink_setsockopt()` and `netlink_getsockopt()`.

Exported capability checks include `netlink_ns_capable()`, `netlink_capable()`, `netlink_net_capable()`, and `netlink_strict_get_check()`.

## Control Flow

Initialization runs from `netlink_proto_init()`: it registers `netlink_proto`, allocates `nl_table`, initializes one rhashtable per netlink protocol number, creates the usersock table entry, registers `PF_NETLINK`, installs pernet proc/tap operations, and calls `rtnetlink_init()`.

User socket creation validates type/protocol, optionally requests a module, captures protocol callbacks from `nl_table`, and allocates a `struct netlink_sock`. Bind either inserts an explicit `nl_pid` or autobinds to the task TGID and then negative IDs on collision. Multicast membership updates allocate the group bitmap, call protocol-specific bind/unbind hooks, maintain `subscriptions`, update `mc_list`, and refresh aggregate listener masks.

`netlink_sendmsg()` parses destination address or connected defaults, autobinds the sender if needed, allocates an skb, copies user data, runs LSM filtering, multicasts if `dst_group` is set, and unicasts to `dst_portid`. `netlink_unicast()` looks up the peer, handles direct kernel-socket callbacks, applies socket filters, performs receive-buffer backpressure in `netlink_attachskb()`, and queues to the receive queue. Broadcast walks `mc_list`, clones or references the skb per listener, filters, annotates peer netns IDs, and records congestion or delivery failures.

Dump start copies the original request skb, resolves the requester socket, installs callback state under `nl_cb_mutex`, optionally runs `control->start`, and invokes `netlink_dump()`. Each receive call can resume a running dump once receive memory drops below half the socket buffer. Completion emits `NLMSG_DONE`, optional extended ACK TLVs, calls `done`, drops the module reference, and clears `cb_running`.

## State and Persistence Behavior

Per-socket state persists in `struct netlink_sock`: `portid`, default destination, group bitmap, subscriptions, `max_recvmsg_len`, congestion bit, flags, callback state, and protocol callbacks. Per-protocol state persists in `nl_table[protocol]`: rhashtable, multicast list, listener masks, callbacks, registered count, module pointer, and group count.

The port lookup table is an RCU-protected rhashtable keyed by network namespace and port ID. Multicast listeners are kept in `mc_list` with bitmaps on each socket and an aggregate `listeners->masks` table for fast `netlink_has_listeners()`. Dump callback state persists across `recvmsg()` calls and is explicitly torn down on socket release.

Reference and lifetime management are delicate: table insertion takes a socket reference, removal drops it after rhashtable deletion, release uses `call_rcu()` to free groups and socket storage, and generic netlink release synchronization uses `genl_sk_destructing_cnt`.

## Dependencies and Integration Points

This file depends on sockets, skbuffs, rhashtable, RCU, network namespaces, procfs, BPF iterators, LSM hooks, credentials/SCM, notifier chains, and netlink policy dumping for extended ACKs. It integrates directly with `genetlink.c` through `genl_sk_destructing_cnt`, with `policy.c` via `netlink_policy_dump_attr_size_estimate()` and `netlink_policy_dump_write_attr()`, with rtnetlink through early `rtnetlink_init()`, and with netlink taps through ARPHRD_NETLINK devices.

## Risks and Edge Cases

Backpressure and congestion behavior must preserve references when sleeping and retrying delivery. Autobind races are tolerated, but port visibility relies on paired `WRITE_ONCE()`, `READ_ONCE()`, and barriers. Multicast group changes mix table locks, protocol callbacks, and RCU listener masks. Dump callbacks run under per-socket callback mutexes and module references; missing cleanup leaks skb/module state or leaves `cb_running` stuck. ACK TLV offsets must be checked against the original message payload to avoid reporting invalid pointers.

## Test Signals

Useful signals include `tools/testing/selftests/net/netlink_*`, generic netlink controller dumps (`genl ctrl list`, `nlctrl` policy dumps), `ss -A netlink`, `/proc/net/netlink`, `NETLINK_EXT_ACK` error messages, multicast membership changes, namespace multicast tests, BPF iterator build coverage, and socket diag dumps for `AF_NETLINK`.
