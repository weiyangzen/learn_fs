<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_ecache.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_ecache.h

## Purpose
`nf_conntrack_ecache.h` defines conntrack and expectation event-cache extensions, notifier registration, event report helpers, and per-net delayed work controls.

## Important APIs, types, and functions
It defines `enum nf_ct_ecache_state`, `struct nf_conntrack_ecache`, `struct nf_ct_event`, `struct nf_exp_event`, and `struct nf_ct_event_notifier`. Helpers find/exist/add ecache extensions, cache events, report immediate events, deliver cached events, report expectation events, initialize/finalize pernet ecache, and query delayed-work pending state.

## Control flow
If event listeners exist and the conntrack has an ecache extension, packet/update paths set event bits in the cache and optionally timestamp the first cached event. Confirmation or explicit reporting delivers masks to the registered per-net notifier. Destroy-event failures can be retried by delayed work.

## State and persistence
State is per-conntrack cache bitmask, event masks, missed count, portid, optional timestamp, per-net notifier pointer and delayed dying-list work. Disabled CONFIG builds compile to no-ops.

## Dependencies and integration points
It depends on conntrack, expectations, extensions, net namespace, local64 timestamps, and netlink event consumers. It integrates ctnetlink events, expectation notifications, and conntrack lifecycle.

## Risks and test signals
Risks include missing ecache extension causing silent event loss, event callback RCU/lifetime, timestamp renewal semantics, missed event accounting, destroy retry ordering, and disabled-build behavior. Tests should cover listener registration, cached vs immediate events, expectation events, destroy failure retry, timestamps, and no-listener fast path.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_ecache.h` completely for this pass (187 lines, 4924 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_ecache.h -->
