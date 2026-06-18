# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond-lladdr-target.sh

Purpose: Regression test that a bond using IPv6 link-local `ns_ip6_target` can come up and pass traffic.

Important APIs/functions: `cleanup()`, `wait_lladdr_dad()`, `wait_bond_up()`, `ip netns`, bridge/veth setup, bond `arp_interval`, `ns_ip6_target`, IPv6 DAD state, and `ping6`.

Control flow: The script builds a small namespace bridge topology with veth ports, assigns IPv6 link-local addressing, creates a bond with neighbor-solicitation monitoring target, waits for DAD and bond carrier/up state, then validates connectivity.

State and persistence: Temporary namespaces, bridge, veth, and bond are cleaned on exit. State lives in kernel link and IPv6 neighbor/DAD state during the run.

Dependencies and integration points: Requires IPv6, bonding, bridge/veth, iproute support for `ns_ip6_target`, and root privileges.

Risks and test signals: Failures point at IPv6 monitor target parsing, DAD wait handling, bond carrier state, or IPv6 neighbor solicitation behavior.
