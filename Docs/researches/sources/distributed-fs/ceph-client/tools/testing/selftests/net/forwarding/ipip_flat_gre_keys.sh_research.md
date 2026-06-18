
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ipip_flat_gre_keys.sh

Purpose: Flat IPv4 GRE tunnel selftest with asymmetric keys, validating directional key mapping in an IPv4 underlay.

Important APIs/functions: `setup_prepare`, `gre_flat4`, `gre_mtu_change`, `cleanup`; SW1 is created with `ikey 111 okey 222`, SW2 with `ikey 222 okey 111`.

Control flow: identical to the unkeyed flat GRE test except tunnel creation uses paired directional keys. It performs one H1-to-H2 IPv4 ping through the tunnel and the common large-packet MTU transition test.

State/persistence: creates directional-key GRE tunnels, VLAN underlay, routes, VRFs, and forwarding sysctls. It uses `ipip_lib.sh` cleanup to remove all tunnel and route state.

Dependencies/integration: depends on kernel GRE `ikey`/`okey` support and common kselftest functions in `lib.sh`.

Risks: directionality errors produce blackholes despite correct topology. The test does not explicitly test reverse ping, but ICMP replies exercise the opposite key direction.

Test signals: successful ping to 192.0.2.18 labeled "gre flat with ikey/okey" and passing MTU increase check.
