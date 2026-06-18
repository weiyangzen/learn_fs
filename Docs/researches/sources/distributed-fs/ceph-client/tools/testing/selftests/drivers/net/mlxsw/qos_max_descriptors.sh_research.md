# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/qos_max_descriptors.sh

## Purpose

Validates that mlxsw descriptor pool configuration can absorb a large shaped egress burst without unexpected descriptor drops.

## Important APIs, Types, and Functions

Sources `mlxsw_lib.sh`, computes `MAX_POOL_SIZE`, and defines host/switch setup, `percentage_used`, and `max_descriptors`. It manipulates devlink pool sizes/thresholds, TC ETS/TBF qdiscs, DCB buffers, VLAN qos maps, bridges, and ethtool descriptor/drop counters.

## Control Flow

Setup creates VLAN 111 endpoints and bridge forwarding, enlarges ingress/egress pools, binds priority 1 to selected pools, shapes egress, and configures ETS. The test sends a burst, checks `tc_no_buffer_discard_uc_tc_1` does not increase, reads transmit queue bytes, and verifies descriptor usage percentage is high enough relative to expected capacity.

## State and Persistence Behavior

State includes large devlink pool/threshold changes, qdisc hierarchy, DCB buffer maps, VLAN interfaces, bridge state, and ethtool counters. `defer` restores pool and qdisc settings.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It relies on `mlxsw_max_descriptors_get` for ASIC-specific expectations.

## Risks and Edge Cases

Risk is high because pool sizes, descriptor accounting, and expected percentages are hardware/firmware-specific. Traffic size and shaper rate must be sufficient to pressure descriptors without causing unrelated drops.

## Test Signals

Signals are no increase in egress no-buffer discard counters and descriptor/transmit queue usage percentage meeting the expected threshold.
