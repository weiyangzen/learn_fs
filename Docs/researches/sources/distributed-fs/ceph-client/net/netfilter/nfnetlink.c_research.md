# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink.c

## Purpose
`nfnetlink.c` is the NETLINK_NETFILTER core. It owns the per-net netlink socket, subsystem registry, per-subsystem mutexes, multicast helper APIs, message dispatch, and atomic batch commit/abort machinery used by nftables, conntrack, queue, log, acct, osf, cthelper, cttimeout, and hook listing subsystems.

## Important APIs, Types, and Functions
Subsystem APIs are `nfnetlink_subsys_register()`, `nfnetlink_subsys_unregister()`, `nfnl_lock()`, `nfnl_unlock()`, and `lockdep_nfnl_is_held()`. Send-side APIs are `nfnetlink_has_listeners()`, `nfnetlink_send()`, `nfnetlink_set_err()`, `nfnetlink_unicast()`, and `nfnetlink_broadcast()`.

Receive logic is `nfnetlink_rcv()`, `nfnetlink_rcv_msg()`, `nfnetlink_rcv_skb_batch()`, and `nfnetlink_rcv_batch()`. The registry is `table[NFNL_SUBSYS_COUNT]`, mapping subsystem ids to `struct nfnetlink_subsystem` under RCU and a per-subsystem mutex. Batch error tracking uses `struct nfnl_err`.

## Control Flow, State, and Persistence
Normal receive first validates message framing and `CAP_NET_ADMIN`. `nfnetlink_rcv_msg()` verifies the `nfgenmsg` header, loads a subsystem by module autoload if needed, finds the message callback, parses attributes into a bounded stack array capped by `NFNL_MAX_ATTR_COUNT`, and then dispatches by callback type: RCU callbacks run under `rcu_read_lock()`, mutex callbacks validate that the subsystem/callback did not change after acquiring `nfnl_lock()`.

Batch receive starts at `NFNL_MSG_BATCH_BEGIN`, parses an optional generation id, clones the skb, locks the subsystem long enough to validate it supports `valid_genid`, `commit`, and `abort`, then processes only `NFNL_CB_BATCH` messages for that subsystem. It accumulates ack/error reports without stopping on ordinary per-message failures. Successful batches call subsystem `commit`; malformed or failed batches call `abort` with validation or failure action. `-EAGAIN` can replay the entire batch after module autoload or generation changes.

Persistent state includes one `struct sock *nfnl` per net namespace, per-subsystem registered callbacks under RCU, per-subsystem lock classes, and optional conntrack-listener bit state for event fast paths.

## Dependencies and Integration Points
This file integrates kernel netlink core, module autoload (`nfnetlink-subsys-%d`), network namespaces, netfilter subsystem ids/message types, and conntrack event listener state. Every assigned nfnetlink module registers a `struct nfnetlink_subsystem` here.

## Risks and Test Signals
Risks include attr-count stack overflow prevention, callback replacement races across RCU/mutex transitions, batch replay correctness, module refcounting during batch processing, error-list memory pressure, generation-id validation, capability enforcement, and listener bitmap accuracy. Tests should cover unknown subsystem autoload, invalid attr counts, mutex versus RCU callbacks, mixed-subsystem batches, batch begin/end malformed cases, commit and abort replay, per-message ack ordering, per-net socket teardown, and group bind/unbind side effects.
