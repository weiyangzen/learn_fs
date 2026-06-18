# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_flowlabel_mgr.c

Purpose: Management-plane test for `IPV6_FLOWLABEL_MGR`, validating create/get/put, exclusivity, sharing scopes, linger reuse, and process/user ownership behavior.

Important APIs and types: Uses `setsockopt(IPV6_FLOWLABEL_MGR)` with `struct in6_flowlabel_req`, actions `IPV6_FL_A_GET` and `IPV6_FL_A_PUT`, shares `IPV6_FL_S_ANY`, `IPV6_FL_S_EXCL`, `IPV6_FL_S_USER`, `IPV6_FL_S_PROCESS`, flags `IPV6_FL_F_CREATE` and `IPV6_FL_F_EXCL`, `fork`, `wait`, and optional `setuid`.

Control flow: `run_tests` checks that nonexistent labels cannot be fetched or put, over-20-bit labels fail, normal labels can be acquired multiple times and released exactly the expected number of references, exclusive labels cannot be shared, optional long-running mode checks linger delay before reuse, user-private labels are visible to same-user child but not after setuid, and process-private labels are not visible to a child process.

State and persistence: Flowlabel references live on the test socket and kernel flowlabel manager. Optional linger state persists briefly in-kernel but not in files.

Dependencies and integration: Run by `ipv6_flowlabel.sh` inside its own namespace. Requires IPv6 flowlabel manager support and permission for optional `setuid` branch.

Risks: The `__expect` macro inverts the raw expression so test readability depends on `expect_pass`/`expect_fail`. Long-running linger is off by default to avoid time cost.

Test signals: Process exit zero confirms reference accounting, exclusivity, and ownership rules.
