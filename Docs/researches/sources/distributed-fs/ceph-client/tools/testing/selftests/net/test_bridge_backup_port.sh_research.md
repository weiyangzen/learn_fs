# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_bridge_backup_port.sh

## Purpose
`test_bridge_backup_port.sh` validates Linux bridge backup port and backup nexthop ID behavior for VXLAN-backed VTEP-style topologies. It verifies failover forwarding, backup nexthop encapsulation choice, invalid nexthop handling, bidirectional ping, and churn resilience.

## Important APIs, Types, And Functions
Setup functions include `setup_topo_ns()`, `setup_topo()`, `setup_sw_common()`, `setup_sw1()`, `setup_sw2()`, `setup()`, and `cleanup()`. Test functions are `backup_port()`, `backup_nhid()`, `backup_nhid_invalid()`, `backup_nhid_ping()`, `backup_nhid_add_del_loop()`, and `backup_nhid_torture()`. Utility functions include `log_test()`, `run_cmd()`, `tc_check_packets()`, and `bridge_link_check()`.

## Control Flow
The script creates two namespaces connected by a veth underlay, each with a VLAN-aware bridge, dummy access port `swp1`, VXLAN port `vx0`, bridge VLAN 10, and underlay routes. Tests install static FDB entries, tc flower counters, and optional FDB nexthop groups. They send synthetic packets with `mausezahn`, toggle carrier or administrative state on `swp1`, and inspect egress/ingress packet counters to confirm traffic uses `swp1`, `vx0`, a VXLAN FDB entry, or a backup nexthop as expected. The torture test continuously deletes/replaces a nexthop group while sending traffic for 30 seconds.

## State, Persistence, And Dependencies
State is temporary namespaces, bridge/vxlan/veth/dummy devices, nexthop objects, FDB entries, tc qdiscs/filters, and packet counters. It depends on root, `ip`, `bridge`, `tc`, `mausezahn`, `jq`, and iproute2 support for `backup_nhid`. Cleanup removes the namespaces.

## Integration Points
The test links bridge forwarding, link state, VXLAN external mode, FDB nexthops, tc counter visibility, and nexthop object lifecycle. It directly exercises bridge link attributes `backup_port`, `nobackup_port`, and `backup_nhid`.

## Risks
Packet counter expectations are exact and can be affected by stray packets unless the topology is isolated. The invalid-nexthop test relies on VXLAN tx drop counters changing by one. The torture test is success-by-no-crash and has a fixed 30-second runtime. Tool support checks are essential because older iproute2 lacks required attributes.

## Test Signals
Passing signals include expected forwarding counters on `swp1`/`vx0`, backup nexthop ingress counters on the peer, tx-drop increments for invalid nexthops, ping success only while backup nhid is configured, and no crash during nexthop add/delete churn.
