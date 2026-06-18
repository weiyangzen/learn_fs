# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_macvlan_ipvlan.sh

Purpose: Tests macvlan and ipvlan devices layered over a bond in active-backup, balance-tlb, and balance-alb modes.

Important APIs/functions: `bond_topo_2d1c.sh`, `cleanup()`, `check_connection()`, `xvlan_over_bond()`, `bond_reset()`, `ip link add link bond0 type macvlan/ipvlan`, namespace moves, IPv4/IPv6 ping, and `log_test`.

Control flow: It creates the common 2-downlink bond topology plus two extra namespaces. For each bond mode, it resets the bond, creates two macvlan bridge-mode or ipvlan l2 devices on the server bond, moves them into namespaces, assigns IPv4/IPv6 addresses, and checks bidirectional connectivity among client, server, and xvlan namespaces.

State and persistence: Temporary namespaces and virtual devices are cleaned on exit. Neighbor caches are flushed between scenarios.

Dependencies and integration points: Requires bonding, macvlan, ipvlan, IPv6, veth, bridge, and the shared topology helper.

Risks and test signals: Failures identify layered L2/L3 forwarding issues over bond modes or stale neighbor/MAC learning behavior.
