
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipmr.c

Purpose: C kselftest for IPv4 multicast routing (`ipmr`) socket and netlink control-plane behavior, added with Google copyright.

Important APIs/types/functions: `FIXTURE(ipmr)`, `FIXTURE_VARIANT(ipmr, ipv4)`, `struct mfc_attr`, `nl_add_rtattr`, `nl_sendmsg_mfc`, fixture setup/teardown, and tests for `MRT_INIT`, VIF add/delete, MFC add/delete, netlink routes, proxy entries, no-VIF errors, netns dismantle, and table flush.

Control flow: fixture unshares a network namespace, opens NETLINK_ROUTE and raw IGMP sockets, creates a veth pair, and records `veth0` ifindex. Tests exercise `setsockopt` multicast routing options and custom RTM_NEWROUTE/RTM_DELROUTE messages with `RTNL_FAMILY_IPMR`, then inspect `/proc/net/ip_mr_vif` or `/proc/net/ip_mr_cache`.

State/persistence: all state is inside the temporary netns: raw socket multicast router state, VIFs, MFC cache entries, veth device, and table-specific multicast routing data. Teardown closes sockets; netns cleanup removes remaining devices/routes.

Dependencies/integration: integrates with `kselftest_harness.h`, Linux multicast routing UAPI headers, rtnetlink, and shell `ip`/`cat`/`grep` via `system`.

Risks: tests depend on root or sufficient namespace privileges and kernel multicast routing support. Netlink helper has a fixed 4 KiB buffer and asserts ACK shape. `pkill` is not used; isolation is stronger than shell tests.

Test signals: kselftest assertions validate zero or expected negative errors (`-ENFILE`, `-ENODEV`, `EADDRNOTAVAIL`) and expected `/proc` entries for VIF/MFC state.
