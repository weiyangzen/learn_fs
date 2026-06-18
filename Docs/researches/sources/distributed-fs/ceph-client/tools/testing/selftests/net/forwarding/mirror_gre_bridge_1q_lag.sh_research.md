
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_bridge_1q_lag.sh

Purpose: Tests mirror-to-gretap when a VLAN-aware bridge underlay egress is a team/LAG device in loadbalance mode.

Important APIs/functions: `vlan_host_create/destroy`, host helpers, `switch_create/destroy`, `test_lag_slave`, `test_mirror_gretap_first`, `test_mirror_gretap_second`; requires `teamd` and `arping`.

Control flow: creates two VLAN VRFs on `$h1` for H1/H2 roles, H3/H4 underlay receivers, bridge `br1`, team `lag` over `$swp3/$swp4`, route to GRE remote via bridge, and tunnel `gt4`. Each test downs one LAG slave, primes neighbor with arping, verifies mirror traffic reaches the active host, then downs both and verifies no mirror traffic.

State/persistence: creates VLANs 333/555, VRFs, bridge, team device, gretap, routes, forwarding sysctls, trap filters on H3/H4, and mirror/ARP tc filters.

Dependencies/integration: depends on `teamd`, `arping`, bridge/LAG driver behavior, tc counters, and mirror helpers.

Risks: LAG failover and neighbor priming are timing-sensitive. The topology reuses `$h1` for both logical H1 and H2 via VLANs, making route isolation critical.

Test signals: mirror counters on selected host device are `>=10` with one slave active and zero on both H3/H4 when neither slave is usable.
