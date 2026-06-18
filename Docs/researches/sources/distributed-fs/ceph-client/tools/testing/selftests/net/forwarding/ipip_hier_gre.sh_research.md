
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_hier_gre.sh

Purpose: IPv4 GRE tunnel selftest for hierarchical topology without keys, where tunnel devices are bound through underlay dummy devices in separate VRFs.

Important APIs/functions: `setup_prepare` uses `sw1_hierarchical_create gre` and `sw2_hierarchical_create gre`; tests are `gre_hier4` and `gre_mtu_change`.

Control flow: maps six interfaces, enables forwarding/VRF rules, creates host endpoints and hierarchical switch state, then runs IPv4 ping through GRE and common MTU behavior validation.

State/persistence: creates VRFs, dummy underlay endpoints, VLAN 111 links, GRE tunnels, overlay routes, underlay routes, and forwarding sysctls. Cleanup destroys hierarchical switch state before host and VRF cleanup.

Dependencies/integration: depends on `ipip_lib.sh` hierarchical functions and on `lib.sh` for VRFs/pings.

Risks: topology relies on route separation between overlay and underlay VRFs; wrong route deletion can leave persistent rules/devices. Hardware may not support hierarchical GRE offload equivalently to software.

Test signals: H1 ping to 192.0.2.18 succeeds through hierarchical GRE; MTU test sees expected failure before and success after increasing topology MTU.
