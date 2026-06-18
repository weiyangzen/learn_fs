<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_nfacct.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_nfacct.c

## Purpose
`xt_nfacct.c` implements the `nfacct` match, which attaches packet and byte accounting to named nfnetlink accounting objects.

## Important APIs, Types, and Functions
`nfacct_mt()` accounts matching packets through the object stored in `struct xt_nfacct_match_info`. `nfacct_mt_checkentry()` looks up and pins an accounting object by name, and `nfacct_mt_destroy()` releases it. Registration is via `nfacct_mt_reg`.

## Control Flow, State, and Persistence
Rule insertion resolves the configured accounting object and stores the pointer in match info. Every packet reaching the rule updates that object's packet and byte counters and returns true. Counters persist in nfnetlink accounting state, not in this module.

## Dependencies and Integration Points
The file depends on x_tables and `nfnetlink_acct`. It bridges iptables rule traversal with named accounting objects visible through nfnetlink tooling.

## Risks and Test Signals
Risks include missing accounting objects, refcount leaks, counter width/overflow expectations, and namespace object lifetime. Tests should cover successful lookup, missing object rejection, packet and byte increments, concurrent packets, destroy release, and IPv4/IPv6 protocol-unspecified use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_nfacct.c -->
