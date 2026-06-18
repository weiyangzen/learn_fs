# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_mac_profiles_occ.sh

## Purpose

Occupancy and consolidation tests for the mlxsw RIF MAC profile resource.

## Important APIs, Types, and Functions

Defines `create_max_rif_mac_profiles`, replacement, consolidation, shared replacement, and edit tests under `rif_mac_profile_edit_test`. It reads `rif_mac_profiles` resource size/occupancy and uses `devlink_reload` to reset baseline state.

## Control Flow

Setup disables IPv6 auto-addressing, brings two ports up, and reloads devlink. Tests create the maximum number of distinct profiles, replace one profile, consolidate profiles by making two RIFs share a MAC, verify a shared profile cannot be replaced beyond limits, and edit profile users while checking occupancy.

## State and Persistence Behavior

State includes VLAN/RIF devices with assigned MACs, devlink resource occupancy, and device reload state. Cleanup removes devices and resets links.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

Resource accounting must be exact. Consolidation assertions can race with delayed occupancy updates. Devlink reload is disruptive and should run only on isolated test hardware. Shared replacement expected-failure logic depends on correct max-profile creation.

## Test Signals

Signals are resource occupancy equaling max, decreasing after consolidation, failing expected shared replacement, and `log_test` per edit scenario.
