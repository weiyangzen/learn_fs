# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/bond_stacked_header_parse.sh

Purpose: Regression test for bond transmit hash/header parsing with stacked tunnel/VLAN-style headers.

Important APIs/functions: `bond_test_stacked_header_parse()`, namespace/veth setup, bond creation, encapsulation device setup, traffic generation, and kselftest logging helpers.

Control flow: The script creates a virtual topology, configures a bond and stacked protocol headers, sends traffic that forces the bond xmit path to parse inner headers, and checks expected delivery/hash behavior.

State and persistence: Temporary namespaces and network devices are created and cleaned during the test.

Dependencies and integration points: Requires bonding, veth, tunnel/VLAN parsing support used by the script, and net selftest helpers.

Risks and test signals: Failures indicate regressions in `skb_flow_dissect`/bond hash parsing for encapsulated traffic or missing kernel feature support.
