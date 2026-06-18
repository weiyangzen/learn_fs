# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_1d_lag.sh

Purpose: extends the 802.1D bridge-over-VLAN topology to LACP team devices. Host LAGs carry VLAN 100 and 200 traffic, while router-side LAG2 VLAN uppers feed two bridges and LAG3 VLAN uppers carry the routed destination side.

Important functions include `h1_create`, `h2_create`, `router_create`, `config_remaster_lag2`, `config_deslave_swp*`, `config_enslave_swp*`, `config_wait`, and dual-stack ping tests. It requires `REQUIRE_TEAMD=yes`, eight netifs, `team_create lag* lacp`, `vlan_create`, bridge setup, VRF helpers, and forwarding helpers from `lib.sh`.

The control flow creates four LAGs, VLAN uppers, two bridges, static routes, and L3 addresses, then repeatedly removes and restores individual physical slaves from LAG2/LAG3 and remasters LAG2 bridge VLAN uppers. State is LACP team membership, VLAN upper devices, bridge masters, routes, addresses, and forwarding sysctls. No persistent files are written. Risks are high: teamd availability, LACP convergence timing, slave reattach ordering, and cleanup if a slave is left down or unmastered. Test signals are repeated IPv4/IPv6 pings over VLAN 100 and VLAN 200 after each LAG membership mutation, with `setup_wait_dev lag2/lag3` used as the convergence gate.
