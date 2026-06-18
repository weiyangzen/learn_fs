# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_vxlan_ipv6.sh

## Purpose

VXLAN IPv6 tunnel decapsulation trap tests for malformed IPv6-underlay VXLAN traffic.

## Important APIs, Types, and Functions

This mirrors the IPv4 VXLAN trap suite but uses IPv6 underlay addresses and IPv6 payload encodings. It defines H1/switch/VRF setup, ECN/reserved-bits/short/corrupted payload generators, `decap_error_test`, `mc_smac_payload_get`, and `overlay_smac_is_mc_test`.

## Control Flow

Setup prepares IPv6 reachability and VXLAN decap context, then tests malformed VXLAN traffic by injecting crafted frames and checking devlink trap counters. The overlay SMAC case verifies that a multicast source MAC inside a decapsulated VXLAN packet is classified as the `overlay_smac_is_mc` drop.

## State and Persistence Behavior

State is kernel networking state only: IPv6 addresses, routes, VXLAN devices, VRFs, TC filters, trap counters/actions, and traffic PIDs.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

IPv6 neighbor discovery, parser ordering, and VXLAN option support are common failure causes. Tests can be flaky if hardware counters lag traffic generation or if the IPv6 underlay route is not fully resolved before injection.

## Test Signals

Signals are successful devlink drop-trap checks for malformed VXLAN packets and multicast overlay source MAC, with TC counters confirming traffic reached the observed point.
