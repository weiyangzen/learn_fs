<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack.h

## Purpose
`nf_conntrack.h` is the main netfilter connection tracking data model and public core API. It defines `struct nf_conn`, per-netns conntrack state, protocol-private storage, tuple access helpers, timeout/reference helpers, allocation/hash APIs, accounting refresh/kill APIs, and statistics macros.

## Important APIs, types, and functions
Important types include `union nf_conntrack_proto`, `struct nf_conntrack_net_ecache`, `struct nf_conntrack_net`, and `struct nf_conn`. Key helpers/functions include `nf_ct_get`, `nf_ct_put`, `nf_ct_netns_get/put`, hash allocation/resize, tuple parsing, refresh/acct/kill, iteration cleanup/destroy, allocation/free, template allocation, status tests, expiry helpers, `nf_conntrack_get_ht`, `nf_ct_set`, `nf_ct_pernet`, fragment helpers, and stats macros.

## Control flow
Packet paths attach conntrack pointers and info bits into skb nfct storage, create unconfirmed conntracks from tuples, optionally alter reply tuples before confirmation, insert into hash tables, refresh timeouts on traffic, deliver accounting/events, and destroy when refcount reaches zero or GC marks expired confirmed entries. Namespace users enable/disable protocol families to load conntrack hooks.

## State and persistence
State is per-connection refcount, lock, timeout, zone, original/reply tuple hashes, status bits, netns pointer, optional NAT/source hash, master expectation link, mark/secmark, extension area, and protocol-private data. Global/pernet state includes conntrack hash, generation seqcount, max count, and per-net counters/users/sysctls/events.

## Dependencies and integration points
It depends on net namespaces, skb nfct storage, tuple definitions, L4 protocol headers, NAT optional support, conntrack extensions, refcounts, atomics, and netfilter common UAPI. It integrates conntrack, NAT, helpers, expectations, events, labels, timeouts, and flow actions.

## Risks and test signals
Risks include refcount vs raw `nf_ct_get` confusion, timeout wrap/ordering, confirmed/unconfirmed hash invariants, hash resize under RCU, template misuse, loopback packet classification, namespace user leaks, and extension lifetime. Tests should cover new flow creation/confirmation, hash resize, GC expiry, skb attach/detach refs, template flows, namespace enable/disable, fragment handling, and accounting refresh.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack.h` completely for this pass (384 lines, 10754 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack.h -->
