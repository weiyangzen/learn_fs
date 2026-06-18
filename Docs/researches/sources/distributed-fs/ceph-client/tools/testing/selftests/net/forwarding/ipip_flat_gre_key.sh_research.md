
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_flat_gre_key.sh

Purpose: Flat IPv4 GRE tunnel test with shared `key 233`, validating keyed GRE over IPv4.

Important APIs/functions: `setup_prepare` invokes `sw1_flat_create gre $ol1 $ul1 key 233` and `sw2_flat_create gre $ol2 $ul2 key 233`; tests are `gre_flat4` and `gre_mtu_change`.

Control flow: creates the flat `ipip_lib.sh` topology, runs one IPv4 reachability test from H1 to H2 through keyed GRE, then runs the common MTU increase test.

State/persistence: sets up VRFs, VLANs, keyed GRE tunnel devices, tunnel endpoint routes, overlay routes, and forwarding sysctls; cleanup calls flat destroy helpers and restores route rules/sysctls.

Dependencies/integration: relies on Linux `ip link add type gre key` support and `ipip_lib.sh` passing extra tunnel arguments.

Risks: shared keyed GRE may fail differently from unkeyed GRE on hardware offload. The script depends on cleanup destroying `g1a`/`g2a` even when setup fails midway.

Test signals: H1 can ping 192.0.2.18 with label "gre flat with key"; MTU behavior matches the common `test_mtu_change` assertions.
