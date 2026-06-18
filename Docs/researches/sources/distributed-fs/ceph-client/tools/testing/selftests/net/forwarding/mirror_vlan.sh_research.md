
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_vlan.sh

Purpose: Tests mirroring to a VLAN device using the generic mirror topology, including tagged traffic preservation.

Important APIs/functions: `setup_prepare`, `test_vlan_dir`, `test_vlan`, `test_tagged_vlan_dir`, `test_tagged_vlan`.

Control flow: creates generic mirror topology, VLAN 555 on `$swp3` and `$h3`, matchall sink on `$h3.555`, VLAN 111 on H1/H2 data path, then mirrors ingress/egress traffic from `$swp1` to `$swp3.555`. Tagged tests verify VLAN 111 traffic appears on H3 VLAN device and not as VLAN 555 payload.

State/persistence: creates VLAN devices, bridge VLAN entries, trap filter on H3, matchall sink qdisc/filter, and tc mirror filters.

Dependencies/integration: uses `mirror_lib.sh`, `mirror_topo_lib.sh`, tc VLAN capture helpers, and VRF/ping helpers from `lib.sh`.

Risks: VLAN stacking/counter interpretation can differ across devices. Tagged test depends on skip_hw capture filters and correct bridge VLAN membership.

Test signals: ICMP direction counters on `$h3.555`, VLAN 111 capture count `>=10`, and VLAN 555 capture count zero for tagged mirror cases.
