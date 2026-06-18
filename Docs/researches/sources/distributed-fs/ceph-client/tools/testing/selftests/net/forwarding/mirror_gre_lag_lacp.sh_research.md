
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_lag_lacp.sh

Purpose: Tests mirror-to-gretap when both switch and receiver underlay paths are LACP team devices and slave transmitability changes.

Important APIs/functions: `vlan_host_create/destroy`, `h3_create_team/destroy_team`, `h3_create/destroy`, `switch_create/destroy`, `test_lag_slave`, `test_mirror_gretap_first`, `test_mirror_gretap_second`.

Control flow: creates VLAN VRFs on `$h1`, LACP team `lag1` on SW, LACP team `lag2` on H3, gretap source `gt4` and destination `gt4-dst`, then installs a VLAN-filtered mirror. Each test removes one receiver slave from team membership, verifies mirroring through the remaining txable slave, removes the other, verifies no traffic, and rebuilds H3 team for next run.

State/persistence: creates two team devices, VRFs, VLANs, gretap devices, routes, tc qdiscs/capture filters, and mirror actions.

Dependencies/integration: requires `teamd`, LACP support, bridge-less routing via team devices, and tc VLAN capture on `gt4-dst`.

Risks: team membership changes are timing-sensitive; comments note mlxsw construction constraints requiring bottom-up team rebuild. This script lacks forwarding_enable because traffic is local/VLAN-routed within VRFs and GRE mirror underlay.

Test signals: `mirror_test` sees 10 mirrored ICMP packets on `gt4-dst` with one txable slave and zero when both slaves are detached.
