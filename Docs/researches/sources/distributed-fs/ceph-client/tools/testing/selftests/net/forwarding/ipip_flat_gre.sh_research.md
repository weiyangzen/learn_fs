
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_flat_gre.sh

Purpose: IPv4 GRE tunnel selftest for the flat topology without GRE keys. It validates basic IPv4 forwarding through GRE and MTU propagation.

Important APIs/functions: `setup_prepare`, `gre_flat4`, `gre_mtu_change`, `cleanup`; imports `lib.sh` and `ipip_lib.sh`, using `sw1_flat_create gre`, `sw2_flat_create gre`, `ping_test`, and `test_mtu_change`.

Control flow: assigns six interfaces to hosts, overlay, and underlay, enables forwarding and VRF route-rule changes, creates endpoints and flat GRE tunnel topology, waits for links, then runs ping and MTU tests.

State/persistence: creates VRFs, VLAN 111 underlay links, GRE devices `g1a`/`g2a`, IPv4 tunnel endpoint routes, overlay routes, and forwarding sysctls. Cleanup reverses all created state.

Dependencies/integration: depends on `ipip_lib.sh` for IPv4 tunnel topology and on `lib.sh` for VRF and ping harness behavior.

Risks: only one payload family is covered; tc counters are not used, so pass signal is reachability. GRE underlay neighbor resolution and route-rule ordering can still affect results.

Test signals: `ping_test $h1 192.0.2.18` succeeds through GRE, and large ping fails before MTU increase but succeeds after topology MTU is raised.
