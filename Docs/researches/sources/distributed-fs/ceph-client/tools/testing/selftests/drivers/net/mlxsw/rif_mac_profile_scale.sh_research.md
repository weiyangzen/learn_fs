# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_mac_profile_scale.sh

## Purpose

Scale helper for exhausting or validating RIF MAC profile resources.

## Important APIs, Types, and Functions

Defines `RIF_MAC_PROFILE_NUM_NETIFS`, `rif_mac_profiles_create`, `rif_mac_profile_test`, setup, and cleanup. It creates VLAN RIFs with distinct MAC addresses from a generated `ip -b` batch and checks `rif_mac_profiles` resource occupancy.

## Control Flow

Setup disables IPv6 on the two ports to avoid automatic link-local RIF creation, then brings links up. The test creates `count` VLAN devices with different MAC addresses and IPv4 addresses, optionally expecting failure, then reads devlink resource occupancy and expects it to equal `count`.

## State and Persistence Behavior

State includes many VLAN devices, unique MAC addresses, IPv6 disable sysctls, link state, and devlink resource counters.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Generated MAC octets must stay valid for the requested count. IPv6 link-local suppression is required; otherwise unexpected RIF profiles inflate occupancy. Resource sizes vary by ASIC, so wrappers must pass correct expected counts.

## Test Signals

Signals are `ip -b` success/failure according to expectation and `rif_mac_profiles` occupancy matching the requested count.
