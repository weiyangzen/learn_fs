## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_dump_flush.c

Purpose: kselftest harness validating ctnetlink dump and flush operations filtered by conntrack zone, including the default zone, for IPv4 and IPv6 entries.

Important APIs and types: uses libmnl (`mnl_socket_open/bind/sendto/recvfrom`, `mnl_nlmsg_put_header`, `mnl_attr_put`, `mnl_attr_nest_start/end`, `mnl_cb_run`), NETLINK_NETFILTER, `NFNL_SUBSYS_CTNETLINK`, `IPCTNL_MSG_CT_NEW/GET/DELETE`, `CTA_TUPLE_*`, `CTA_PROTOINFO_TCP`, `CTA_ZONE`, and `kselftest_harness.h` fixtures.

Control flow: helper builders construct IPv4/IPv6 original and reply tuples and TCP established protoinfo. `conntrack_data_insert()` sends create requests with ACK handling, treating `EEXIST` as acceptable. `conntracK_count_zone()` sends a dump with `CTA_ZONE` and counts reply messages; `conntrack_flush_zone()` sends a delete request with `CTA_ZONE`. Fixture setup opens and binds netlink, skips on permission or unsupported zone filtering, inserts two entries in zone 123, two in 124, two in 125, and two in default zone, then verifies the selected zone has exactly two entries. Tests assert zone-specific dump count, flushing non-default zone does not remove adjacent/default zones, and flushing default zone does not remove non-default zones.

State and persistence: creates conntrack entries in the current network namespace with long timeouts; the shell wrapper runs under `unshare -n` to isolate them. Dependencies are root or CAP_NET_ADMIN, ctnetlink, conntrack zones, libmnl. Risks include old kernels that ignore zone filter, time-based netlink sequence reuse, and no explicit teardown flush. Test signals are kselftest EXPECT/SKIP output and process exit.
