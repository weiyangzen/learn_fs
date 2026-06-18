# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_1d.sh

Purpose: tests routing through two separate 802.1D bridges built on VLAN uppers of one switch port. Host H1 uses VLANs 100 and 200, while H2 has two routed subnets on a plain interface.

Key functions are `h1_create`, `h2_create`, `router_create`, `config_remaster`, `ping_ipv4`, and `ping_ipv6`. `router_create` creates `$swp1.100` and `$swp1.200`, attaches them to `br1` and `br2`, gives each bridge an L3 address, and configures `$swp2` with two destination-side address pairs. The test harness comes from `lib.sh`; route and VLAN manipulation is done with `ip`, `vlan_create`, `__addr_add_del`, and ping helpers.

Control flow is a straight setup, connectivity check, bridge-slave detach/reattach, connectivity check, and cleanup. State is transient VLAN interfaces, bridges, VRFs, routes, and forwarding. Integration is with the shared forwarding selftest topology through `NUM_NETIFS=4`. Risks are ordering-sensitive cleanup of VLAN uppers and bridge masters, plus remaster races requiring `sleep 2`. Test signals are two IPv4 pings and two IPv6 pings, one per VLAN-backed routed path, before and after remastering.
