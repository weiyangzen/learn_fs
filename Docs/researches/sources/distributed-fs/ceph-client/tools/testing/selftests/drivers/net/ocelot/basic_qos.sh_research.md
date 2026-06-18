# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ocelot/basic_qos.sh

Purpose: Tests basic QoS classification on Ocelot switch ports for default port priority, VLAN PCP, and IP DSCP.

Important APIs/functions: Sources forwarding `tc_common.sh` and `lib.sh`. Topology helpers create host interfaces, VLAN subinterfaces, and a bridge over `swp1/swp2`. `run_test` sends IPv4 and IPv6 traffic and checks priority behavior. `port_default_prio_get`, `test_port_default`, `test_vlan_pcp`, and `test_ip_dscp` implement the scenarios.

Control flow: Setup brings host/switch ports up, creates bridge and VLAN devices, and installs egress filters to shape packet priority markings. Tests alter default priority, VLAN PCP, or DSCP markings, send traffic across the bridge, and log separate IPv4/IPv6 results. Cleanup removes qdiscs, VLANs, hosts, and bridge.

State and persistence: Mutates live switch port state, bridge membership, VLAN interfaces, and TC filters. All state is transient and removed by `trap cleanup EXIT`.

Dependencies and integration: Requires an Ocelot hardware test topology with exported `h1`, `h2`, `swp1`, `swp2`, `tc`, `bridge`, and forwarding library variables.

Risks: Hardware counters/classification can be timing-sensitive. Test correctness depends on the topology being wired as expected. DSCP-to-ToS conversion and VLAN priority propagation must match Ocelot offload semantics.

Test signals: Expected logs show IPv4 and IPv6 traffic classified with the configured priority source for default port, VLAN PCP, and DSCP cases.
