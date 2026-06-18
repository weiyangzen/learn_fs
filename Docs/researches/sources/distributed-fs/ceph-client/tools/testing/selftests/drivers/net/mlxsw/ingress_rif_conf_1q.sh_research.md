# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/ingress_rif_conf_1q.sh

## Purpose

Tests ingress RIF configuration order for VLAN-aware bridge VID to FID mappings.

## Important APIs, Types, and Functions

The file mirrors the ingress RIF ordering pattern for a VLAN-aware bridge. It defines `vid_map_rif`, `rif_vid_map`, bridge RIF helpers, host/switch setup, and TC/devlink checks.

## Control Flow

Setup creates VLAN 10 endpoints and a VLAN-aware bridge, controls bridge address generation, configures a routed switch-facing VLAN path, and installs TC counters. Tests exercise both orders: VID mapping before RIF and RIF before VID mapping. Each test validates that packets route in hardware after the final configuration is complete.

## State and Persistence Behavior

State includes bridge VLAN database entries, bridge IP/RIF state, host VLAN interfaces, neighbor entries, route entries, and TC filters.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced.

## Risks and Edge Cases

The test is susceptible to bridge VLAN default PVID behavior, neighbor resolution, and timing of RIF creation after address addition. Any failure to remove VLAN entries can affect the second order test.

## Test Signals

Signals are devlink `rifs` occupancy deltas and TC `skip_sw` packet counts for successful hardware routing.
