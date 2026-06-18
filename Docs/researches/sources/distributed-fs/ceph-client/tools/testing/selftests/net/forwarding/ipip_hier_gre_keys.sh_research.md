
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_hier_gre_keys.sh

Purpose: Hierarchical IPv4 GRE test with asymmetric `ikey`/`okey`, validating directional keys across separated underlay and overlay VRFs.

Important APIs/functions: `setup_prepare`, `gre_hier4`, `gre_mtu_change`, `cleanup`; calls `sw1_hierarchical_create gre ... ikey 111 okey 222` and inverse keys on SW2.

Control flow: builds the standard six-interface hierarchical GRE topology, runs reachability through the keyed tunnel, performs the MTU increase test, and cleans up in reverse.

State/persistence: mutates VRF devices/tables, dummy devices, GRE tunnels, VLANs, IPv4 routes, and forwarding sysctls.

Dependencies/integration: depends on `ipip_lib.sh` tunnel creation accepting directional key arguments and `lib.sh` test harness semantics.

Risks: one-way key mismatch is the central risk; ICMP ping includes reply direction but does not isolate which direction failed. Hierarchical route setup is more sensitive to partial cleanup than flat tests.

Test signals: successful ping labeled "gre hierarchical with ikey/okey" and passing common GRE MTU-change test.
