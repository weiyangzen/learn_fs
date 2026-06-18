# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/config

Purpose: Specifies kernel configuration needed by the team driver selftests.

Important entries: Requires bonding, dummy, IPv6, macvlan, netdevsim module, GRE, team core, team modes (`ACTIVEBACKUP`, `BROADCAST`, `LOADBALANCE`, `RANDOM`, `ROUNDROBIN`), and veth.

Control flow: No executable logic. Kselftest config tooling can merge these symbols into a test kernel.

State and persistence: No runtime state; it enables modules/features that team scripts create dynamically.

Dependencies and integration: Supports team, bonding/LAG helper, namespace, GRE-over-bond-over-team, and veth-based topology tests.

Risks: Userspace requirements such as `teamnl`, `teamd`, `tcpdump`, `mz`, `ping`, and `iproute2` are not represented. Some tests can run in IPv4 mode but IPv6 is still a default requirement.

Test signals: A configured kernel should allow creation of team devices/modes, veth peers, dummy/macvlan devices, GRE devices, and bonding stacks used by the tests.
