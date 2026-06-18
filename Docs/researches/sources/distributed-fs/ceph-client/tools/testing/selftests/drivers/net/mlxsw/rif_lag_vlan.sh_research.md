# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_lag_vlan.sh

## Purpose

RIF lifecycle tests for VLAN subinterfaces on a LAG.

## Important APIs, Types, and Functions

This is the VLAN-on-LAG variant of `rif_lag.sh`. It creates a LAG, a VLAN upper, and tests RIF add/drop/remaster behavior for the VLAN RIF with `lag_rif_add`, `lag_rif_nomaster`, `lag_rif_remaster`, and `lag_rif_nomaster_addr`.

## Control Flow

Setup creates team/LAG state, enslaves the switch port, creates the VLAN upper, and disables uncontrolled address generation. Tests add addresses to the VLAN interface, remove/readd master relationships, and compare devlink RIF occupancy before and after each operation.

## State and Persistence Behavior

State includes team device, VLAN upper, switch-port master state, VLAN RIF address, and devlink RIF occupancy. Cleanup removes VLAN/LAG and restores ports.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It requires teamd and VLAN support.

## Risks and Edge Cases

VLAN upper lifetime adds cleanup risk: removing the LAG before VLAN cleanup can cascade errors. Occupancy checks can race with delayed mlxsw RIF updates.

## Test Signals

Signals are precise `rifs` occupancy changes and successful remaster/deslavement operations.
