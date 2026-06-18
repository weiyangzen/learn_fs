
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_lib.sh

Purpose: Shared library for GRE/IP-in-IP over IPv6 forwarding tests. It defines flat and hierarchical topologies, host setup, traffic probes, MTU changes, and remote endpoint mutation helpers.

Important APIs/functions: `h1_create/destroy`, `h2_create/destroy`, `sw1_flat_create/destroy`, `sw2_flat_create/destroy`, `sw1_hierarchical_create/destroy`, `sw2_hierarchical_create/destroy`, `test_traffic_ip4ip6`, `test_traffic_ip6ip6`, `topo_mtu_change`, `test_mtu_change`, `flat_remote_change/restore`, `hier_remote_change/restore`.

Control flow: driver scripts source this file after `lib.sh`. Topology creation composes VRFs, VLAN 111 underlay, `ip6gre` tunnels, tunnel remote routes, and overlay routes. Traffic tests install tc clsact filters on underlay and decap egress devices, generate 1000 packets with mausezahn, assert counters, then remove filters.

State/persistence: creates device-level state including `g1a`, `g2a`, dummy underlay endpoints, per-device VRFs, VLANs, neighbor entries, IP routes, and sysctl-backed forwarding via callers. It has no durable persistence beyond kernel network state.

Dependencies/integration: imports `lib.sh` and `tc_common.sh`; expects globals `h1`, `h2`, `ol1`, `ol2`, `ul1`, `ul2`, `TC_FLAG`, `MZ`, and `MZ_DELAY` supplied by callers.

Risks: several destroy routines delete specific routes and addresses; partial setup failures can make cleanup noisy. Tests assume tc counters reflect the intended datapath and that neighbor priming avoids first-packet loss.

Test signals: library functions report through `check_err`, `check_fail`, and `log_test`; callers observe packet counter thresholds and ping/MTU behavior.
