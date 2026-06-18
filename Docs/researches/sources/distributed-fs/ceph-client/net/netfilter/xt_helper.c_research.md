<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_helper.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_helper.c

## Purpose
`xt_helper.c` implements matching on the conntrack helper assigned to a connection, allowing firewall rules to identify flows handled by helpers such as FTP or SIP.

## Important APIs, Types, and Functions
`helper_mt()` is the match function and `helper_mt_check()`/`helper_mt_destroy()` manage conntrack namespace references. The matcher uses `nf_ct_get()`, `nfct_help()`, and RCU dereferencing of `help->helper`. Rule data is `struct xt_helper_info`.

## Control Flow, State, and Persistence
The match retrieves the packet's connection, obtains helper extension state, and reads the assigned helper under RCU. If a helper name is configured, it compares the helper name with the requested string; otherwise it tests for helper presence. The configured invert bit flips the result. The module persists no helper state itself.

## Dependencies and Integration Points
It depends on conntrack helper infrastructure and x_tables registration. Checkentry pins conntrack support for the rule family so helper metadata is available while rules exist.

## Risks and Test Signals
Risks include helper assignment changes under RCU, null helper extensions, namespace reference leaks, and user expectation mismatch when automatic helper assignment is disabled. Tests should cover helper present/absent, exact helper names, inversion, no-conntrack packets, IPv4/IPv6 registration, and rule unload refcount release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_helper.c -->
