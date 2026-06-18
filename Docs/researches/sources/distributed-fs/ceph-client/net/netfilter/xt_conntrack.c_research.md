<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_conntrack.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_conntrack.c

## Purpose
`xt_conntrack.c` is the full-featured x_tables conntrack match. It matches connection state, direction, NAT status, original and reply tuples, protocol, ports, and expiration time, subsuming the simpler `state` match.

## Important APIs, Types, and Functions
`conntrack_mt()` is the shared matcher for revisions 1, 2, and 3 via `conntrack_mt_v1()`, `conntrack_mt_v2()`, and `conntrack_mt_v3()`. It consumes `struct xt_conntrack_mtinfo1`, `xt_conntrack_mtinfo2`, or `xt_conntrack_mtinfo3`. Helpers include `conntrack_addrcmp()`, `conntrack_mt_origsrc()`, `conntrack_mt_origdst()`, `conntrack_mt_replsrc()`, `conntrack_mt_repldst()`, `ct_proto_port_check()`, `ct_proto_port_check_v3()`, and `port_match()`.

## Control Flow, State, and Persistence
The match first calls `nf_ct_get()` and maps the result to `XT_CONNTRACK_STATE_BIT()`, `XT_CONNTRACK_STATE_UNTRACKED`, or `XT_CONNTRACK_STATE_INVALID`. When state matching is enabled it augments the state mask with SNAT/DNAT bits from `ct->status`. If no `nf_conn` exists, only state-only matches can succeed. Otherwise it checks direction via `CTINFO2DIR()`, masked original/reply addresses, protocol and ports, status bits, and `nf_ct_expires(ct) / HZ`. Revision 3 adds port ranges; older revisions compare exact tuple ports.

## Dependencies and Integration Points
The module pins conntrack support per network namespace and family through `nf_ct_netns_get()`/`nf_ct_netns_put()`. It reads `struct nf_conn` tuple hashes, status bits, protocol number, and expiration state, and registers an NFPROTO_UNSPEC match so the same code serves IPv4 and IPv6.

## Risks and Test Signals
Risks include inversion logic on every match flag, invalid/untracked state handling, IPv6 mask comparisons, byte-order differences between revision 2 exact ports and revision 3 port ranges, and expiration granularity in seconds. Tests should cover invalid, untracked, new, established, related, SNAT, DNAT, original/reply tuple matches, inverted address/status/protocol/port checks, IPv6 masks, v3 ranges, no-conntrack packets, and namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_conntrack.c -->
