<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_core.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_core.h

## Purpose
`nf_conntrack_core.h` exposes conntrack core functions shared by standalone conntrack and compatibility users: packet entry, init/cleanup, tuple inversion/find, confirmation, locks, timeout/status mutation, and tuple printing.

## Important APIs, types, and functions
Key APIs are `nf_conntrack_in`, net/proto init-cleanup functions, `nf_ct_invert_tuple`, `nf_conntrack_find_get`, `__nf_conntrack_confirm`, inline `nf_conntrack_confirm`, `nf_confirm`, `print_tuple`, global lock arrays, `nf_conntrack_expect_lock`, `__nf_ct_set_timeout`, `__nf_ct_change_timeout`, `__nf_ct_change_status`, and `nf_ct_change_status_common`.

## Control flow
Netfilter hooks call `nf_conntrack_in`; later confirm hooks call `nf_conntrack_confirm`, which inserts unconfirmed conntracks and then delivers cached events when present. Timeout mutation stores relative time while unconfirmed and absolute jiffies once confirmed.

## State and persistence
State is in conntrack entries, global lock arrays, expect lock, per-net/protocol initialization, and cached event extensions.

## Dependencies and integration points
It depends on netfilter hooks, conntrack, event cache, and L4 protocol APIs. It integrates packet hook processing, hash confirmation, and event delivery.

## Risks and test signals
Risks include double confirmation, cached events delivered after skb nfct changes, timeout unit confusion, lock contention across 1024 locks, expectation lock ordering, and cleanup ordering. Tests should cover unconfirmed-to-confirmed transitions, event delivery, timeout changes pre/post confirmation, tuple find, and namespace cleanup.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_core.h` completely for this pass (108 lines, 3241 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_core.h -->
