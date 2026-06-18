
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_flat_keys.sh

Purpose: Flat IPv6-underlay GRE tunnel selftest using directional keys. SW1 uses `ikey 111 okey 222`, SW2 uses the inverse, validating asymmetric key handling.

Important APIs/functions: `setup_prepare`, `gre_flat`, `gre_mtu_change`, `gre_flat_remote_change`, `cleanup`; extra tunnel arguments are passed through `sw1_flat_create`/`sw2_flat_create` in `ip6gre_lib.sh`.

Control flow: builds the same six-interface flat topology as the unkeyed test, then runs traffic validation for both inner IPv4 and IPv6. Remote-change rewrites tunnel endpoints while keeping key configuration unchanged, then restores original endpoints.

State/persistence: modifies forwarding sysctls, VRF rules, VLANs, keyed `ip6gre` devices, tunnel endpoint addresses, IPv6 routes to tunnel remotes, and tc filters/counters used by traffic tests.

Dependencies/integration: relies on bidirectional `ikey`/`okey` matching in kernel GRE-over-IPv6 and on the common `ip6gre_lib.sh` topology and tc-common counter helpers.

Risks: directional keys make directionality explicit; swapping or normalizing keys incorrectly would cause one direction to fail. The MTU function call passes an unused `gre` argument, tolerated by current `test_mtu_change` but a coupling risk if that helper changes.

Test signals: generated IPv4 and IPv6 traffic must be observed on underlay egress and post-decap overlay egress in both original and changed endpoint states; large IPv6 ping behavior validates MTU propagation.
