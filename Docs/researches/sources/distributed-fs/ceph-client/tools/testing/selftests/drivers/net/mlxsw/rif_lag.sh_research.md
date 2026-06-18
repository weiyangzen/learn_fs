# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_lag.sh

## Purpose

RIF lifecycle tests for a standalone LAG netdevice.

## Important APIs, Types, and Functions

Creates a LACP team `lag1` with one switch port and tests `lag_rif_add`, `lag_rif_nomaster`, `lag_rif_remaster`, and `lag_rif_nomaster_addr` using devlink RIF occupancy.

## Control Flow

Setup creates the LAG, disables address generation, assigns the LAG MAC, and enslaves SWP1. Tests add an IP address to create a RIF, remove the physical port to drop the RIF, re-enslave the port to recreate it, and verify address/master interactions. Cleanup deletes the LAG and resets ports.

## State and Persistence Behavior

State includes team/LAG device, port master state, LAG IP addresses, and devlink RIF counters.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It requires teamd/LACP support.

## Risks and Edge Cases

Asynchronous RIF creation/destruction and teamd availability are main risks. Port down/up ordering matters when remastering. Leftover addresses can keep RIF occupancy elevated.

## Test Signals

Signals are expected RIF occupancy deltas after address addition, port deslavement, and port reenslavement.
