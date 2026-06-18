# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_vxlan.sh

## Purpose

VXLAN IPv4 tunnel decapsulation trap tests for malformed VXLAN and multicast overlay source MAC packets.

## Important APIs, Types, and Functions

Builds a VXLAN-capable topology and defines payload builders for ECN mismatch, reserved VXLAN bits, short VXLAN packets, corrupted packets, and multicast source MAC. Top-level tests are `decap_error_test` and `overlay_smac_is_mc_test`, using `devlink_trap_drop_test`, TC filters, and mausezahn raw payload injection.

## Control Flow

Setup creates H1, switch ports, a VRF for overlay routing, and VXLAN-related addressing. `decap_error_test` runs several malformed payload checks that should hit decap-error traps. `overlay_smac_is_mc_test` sends an encapsulated Ethernet frame with multicast SMAC and verifies the separate overlay SMAC trap. Cleanup tears down VXLAN/VRF state and filters.

## State and Persistence Behavior

Runtime state includes VXLAN devices, bridge or VRF memberships, routes, TC clsact filters, trap actions/stats, and background traffic.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Malformed-packet tests are brittle by design: if VXLAN parser validation order changes, a packet may hit a different trap. VXLAN offload requires exact options such as checksum behavior and UDP port. Multicast SMAC tests depend on the inner frame being decapsulated far enough to inspect the overlay Ethernet header.

## Test Signals

Signals are per-payload trap hits, TC packet counters, and `log_test` results for decap errors and overlay multicast SMAC.
