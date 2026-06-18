# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rif_bridge.sh

## Purpose

RIF lifecycle tests for a bridge backed by LAG ports on mlxsw.

## Important APIs, Types, and Functions

Creates two LACP team devices, a VLAN-aware bridge, enslaves LAG1 to the bridge, and attaches SWP1/SWP2 to LAGs. Tests cover bridge RIF add, LAG deslavement/remaster, address handling while enslaved, and physical port deslavement/remaster.

## Control Flow

Each test snapshots devlink `rifs` occupancy, changes address or master state, sleeps for propagation, and checks expected occupancy increase/decrease/no-change. The address test proves a LAG address does not create a separate RIF while enslaved but does when the LAG is removed from the bridge.

## State and Persistence Behavior

State includes team/LAG devices, bridge `br1`, switch-port masters, bridge and LAG addresses, and devlink RIF occupancy. Cleanup deletes teams and bridge and resets ports.

## Dependencies and Integration Points

The script is part of the Linux kselftest networking suite copied under `sources/distributed-fs/ceph-client`. It depends on root privileges, real mlxsw Spectrum-capable switch ports exposed through `NETIFS`, iproute2 tools, `tc` flower offload, `devlink`, `ethtool`, `jq`, `bc`, kselftest helpers from `tools/testing/selftests/net/forwarding`, and traffic tools such as mausezahn or ping where referenced. It requires teamd support through `REQUIRE_TEAMD=yes`.

## Risks and Edge Cases

Occupancy timing is asynchronous and guarded only by sleeps. LAG creation requires teamd and can fail in minimal environments. If a test changes master state and fails before restoration, later tests can see wrong baseline occupancy.

## Test Signals

Signals are exact `rifs` occupancy deltas for each lifecycle operation and `log_test` messages.
