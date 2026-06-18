# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/devlink_trap_tunnel_ipip6.sh

## Purpose

IPv6-under-IPv4 or IPv6 IPIP tunnel decapsulation error trap tests for mlxsw.

## Important APIs, Types, and Functions

This is the IPv6-flavored counterpart of the IPIP tunnel trap test. It defines H1/VRF2/switch setup, `ipip_payload_get`, `ecn_payload_get`, `ecn_decap_test`, `no_matching_tunnel_test`, and top-level `decap_error_test`, using forwarding helpers, `tc_common.sh`, and `devlink_lib.sh`.

## Control Flow

The control flow mirrors the IPv4 IPIP test: create underlay and overlay reachability, install TC filters, generate crafted encapsulated packets, and assert that invalid ECN or missing tunnel state increments the decap-error trap instead of being forwarded. Cleanup removes filters, VRFs, routes, and traffic processes.

## State and Persistence Behavior

The script mutates only runtime network namespace/device state: VRFs, addresses, routes, filters, forwarding toggles, and devlink counters. It does not persist test artifacts.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The main risk is protocol ambiguity: small payload construction changes can make the packet fail earlier or later than the expected mlxsw trap. IPv6 route and neighbor state must be stable before packet injection. Counter idle tests can race with slow hardware updates.

## Test Signals

Signals are `devlink_trap_drop_test` success for decap-error cases and absence of lingering traffic or filters after cleanup.
