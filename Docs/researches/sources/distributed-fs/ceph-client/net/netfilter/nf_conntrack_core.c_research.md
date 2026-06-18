# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_core.c

## Purpose
`nf_conntrack_core.c` is the central implementation of netfilter connection tracking. It parses packet tuples, allocates and confirms conntrack objects, maintains the global hash table, performs lockless RCU lookups, handles expectations, dispatches protocol trackers, manages accounting/events/extensions, resolves insertion clashes, runs garbage collection and early drop, exposes netlink tuple helpers, and owns global/per-net initialization and cleanup.

## Important APIs, Types, And Functions
Global state includes `nf_conntrack_hash`, `nf_conntrack_htable_size`, `nf_conntrack_max`, `nf_conntrack_locks[]`, `nf_conntrack_expect_lock`, `nf_conntrack_generation`, and `conntrack_gc_work`. Hashing uses siphash over tuple, zone id, and netns mix. Tuple helpers include `nf_ct_get_tuplepr()`, `nf_ct_get_tuple()`, `nf_ct_get_tuple_ports()`, `get_l4proto()`, `nf_ct_invert_tuple()`, and `nf_ct_get_id()`.

Core lifecycle functions are `nf_conntrack_alloc()`, `nf_conntrack_free()`, `init_conntrack()`, `resolve_normal_ct()`, `nf_conntrack_in()`, `__nf_conntrack_confirm()`, `nf_conntrack_hash_check_insert()`, `nf_ct_delete()`, and `nf_ct_destroy()`. Lookup and collision handling use `____nf_conntrack_find()`, `__nf_conntrack_find_get()`, `nf_conntrack_find_get()`, `nf_conntrack_tuple_taken()`, and clash-resolution helpers. Cleanup/resize/init flows include iterate cleanup, hash resize, global init/end, per-net init, and cleanup start/end.

## Control Flow
`nf_conntrack_in()` ignores already tracked or untracked packets, derives L4 protocol and offset, handles ICMP error packets specially, then calls `resolve_normal_ct()`. Resolution parses a tuple, looks for it under the template-derived zone, and allocates a new conntrack if no match exists. New allocation builds the reply tuple, applies template timeout/account/timestamp/label/event extensions, checks expectations, attaches master/helper state for expected flows, and associates the unconfirmed object with the skb.

Protocol-specific packet handlers update state and timeout. Confirmation later inserts original and reply tuplehashes into the global table under ordered bucket locks after duplicate and chain-length checks. If insertion races, clash resolution may reattach the skb to the winner or insert a reply-only fixed-timeout NAT clash entry. Destruction marks entries dying, reports destroy events, unlinks from hash lists, handles missed-event retry via ecache if needed, removes expectations/helpers/NAT bysource state, and frees after references drain.

## State And Persistence
Conntrack state is in-memory per net namespace and globally hashed. Each `nf_conn` stores original/reply tuples, status bits, timeout, optional extensions, master relationship, protocol-private state, zone, and netns pointer. The hash table is RCU-visible and uses `SLAB_TYPESAFE_BY_RCU`, so refcount-after-lookup revalidation and confirmed-bit ordering are central invariants.

## Dependencies And Integration Points
This file integrates protocol trackers, helpers, expectations, extension allocation, accounting, timestamps, labels, synproxy, NAT hooks, BPF kfunc registration, netlink tuple encoding, nf_queue cleanup, net namespace lifecycle, RCU, workqueues, seqcount-protected hash resize, and exported `nf_ct_hook` operations.

## Risks
This is high-risk concurrency code. Correctness depends on dual-bucket lock ordering, `nf_conntrack_locks_all` during resize, generation seqcount retry, RCU nulls-list restarts, confirmed-bit publication after hash insertion, extension generation validation, and refcount-zero semantics for `SLAB_TYPESAFE_BY_RCU`. Behavioral risks include tuple parsing with fragments/extensions, expectation races, NAT clash handling, table-full early drop, destroy event retry ownership, cleanup loops blocked on references, and BPF registration cleanup order.

## Test Signals
Test IPv4/IPv6 TCP/UDP/ICMP/SCTP/GRE tracking, fragments and IPv6 extension headers, expected related connections, helper assignment, accounting/timestamp/event extensions, confirmation races with cloned broadcast skbs, NAT tuple clashes, table-full early drop, GC expiry, hash resize during traffic, net namespace teardown, nf_queue reinjection during cleanup, BPF kfunc use, netlink tuple filters, and destroy-event listener congestion.
