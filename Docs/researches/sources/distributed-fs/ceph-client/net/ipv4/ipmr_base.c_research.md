# sources/distributed-fs/ceph-client/net/ipv4/ipmr_base.c

## Purpose
`ipmr_base.c` contains multicast-routing helpers shared by IPv4 `ipmr` and IPv6 `ip6mr`: VIF initialization, multicast routing table allocation/freeing, generic MFC lookup helpers, proc sequence traversal, rtnetlink route dump formatting, and fib notifier dump helpers.

## Important APIs, Types, And Functions
Key APIs are `vif_device_init()`, `mr_table_alloc()`, `mr_table_free()`, `mr_mfc_find_parent()`, `mr_mfc_find_any_parent()`, `mr_mfc_find_any()`, `mr_fill_mroute()`, `mr_table_dump()`, `mr_rtm_dumproute()`, and `mr_dump()`. Proc builds also export `mr_vif_seq_idx()`, `mr_vif_seq_next()`, `mr_mfc_seq_idx()`, and `mr_mfc_seq_next()`.

## Control Flow
Protocol-specific code allocates an `mr_table` with hash parameters, an expiration timer callback, and a table insertion callback. MFC lookup helpers search the protocol-supplied rhltable and apply parent/VIF wildcard semantics. Dump helpers walk resolved lists under RCU and unresolved lists under the caller-supplied spinlock, invoking a protocol-specific route-fill callback.

## State And Persistence
The file owns no persistent global state. It initializes fields inside `struct mr_table` and `struct vif_device`, queues table destruction through `queue_rcu_work()`, and reads per-MFC counters, TTL arrays, flags, and last-use timestamps when producing rtnetlink data.

## Dependencies And Integration Points
It depends on `linux/mroute_base.h`, rhashtable/rhltable APIs, RCU workqueues, seq_file, rtnetlink attributes, and fib notifier callbacks. IPv4 and IPv6 provide the address-specific key, fill, iteration, and locking pieces.

## Risks
Risks include lock imbalance in sequence traversal when switching from resolved to unresolved lists, incorrect dump cursor updates across multipart netlink dumps, stale VIF device pointers, and mismatch between protocol-specific rhashtable compare keys and generic lookup helpers.

## Test Signals
Tests should cover table allocation failure and cleanup, wildcard parent lookup semantics, route dump filtering by device and route type, unresolved-entry dump flags, proc iteration over empty and mixed resolved/unresolved tables, and fib notifier dumps containing VIF and MFC entries.
