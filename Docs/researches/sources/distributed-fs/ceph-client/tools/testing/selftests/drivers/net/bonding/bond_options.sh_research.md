# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_options.sh

Purpose: Broad option matrix selftest for bonding modes active-backup, balance-tlb, and balance-alb using a three-link topology.

Important APIs/functions: `skip_prio()`, `skip_ns()`, `active_slave_changed()`, `check_active_slave()`, `prio_test()`, `prio_miimon()`, `prio_arp()`, `prio_ns()`, `arp_validate_test()`, `arp_validate_mcast()`, `garp_test()`, `num_grat_arp()`, fail-over-MAC check helpers, `do_active_backup_failover()`, `vlan_over_bond_arp()`, `vlan_over_bond_ns()`, `vlan_over_bond()`, and `tests_run`.

Control flow: The script sources `bond_topo_3d1c.sh`, prepares a server/gateway/client topology, then runs `ALL_TESTS`. Priority cases reset bonds with miimon/ARP/NS monitoring and primary reselection modes, validate per-slave priority, active slave choices, and connectivity. ARP validate cases inspect MII state and multicast group joins. GARP cases count gratuitous ARP packets via TC filters. Fail-over-MAC cases validate MAC inheritance under all policy modes. VLAN cases verify ARP and IPv6 NS monitoring over VLAN devices.

State and persistence: Uses temporary namespaces, bond resets, TC clsact/flower filters, VLAN devices, multicast memberships, and link state transitions. Cleanup is inherited from the topology.

Dependencies and integration points: Requires bonding options support in kernel and iproute2, `jq`, TC flower, IPv6, VLAN, bridge/veth, and forwarding test helpers.

Risks and test signals: This is timing-sensitive around failover and monitoring intervals. Failures map to option parsing, active slave selection, monitor target handling, multicast membership propagation, GARP counts, fail-over-MAC semantics, or VLAN encapsulation handling.
