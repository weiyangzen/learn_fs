# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/port_scale.sh

## Purpose

Scale helper for mlxsw physical port resource exhaustion via devlink port splitting.

## Important APIs, Types, and Functions

Defines `PORT_NUM_NETIFS`, an `unsplit` array, `split_all_ports`, `port_test`, and cleanup that unsplits created ports. It reads splittable ports from `devlink -j port show` and checks `physical_ports` resource occupancy.

## Control Flow

The helper loops over all splittable netdevs, splits each to its lane count, tracks the new split base port for cleanup, then reads devlink resource occupancy and compares it with the expected maximum. Cleanup unsplits all tracked ports.

## State and Persistence Behavior

State is disruptive device port split state and the shell `unsplit` array. It persists at the device level until cleanup or manual unsplit succeeds.

## Dependencies and Integration Points

Depends on `devlink`, `jq`, `$DEVLINK_DEV`, and a device whose ports are splittable. It is normally invoked by hardware-specific wrappers that pass expected maxima.

## Risks and Edge Cases

Port splitting can rename or recreate netdevices and can fail if links are in use. Cleanup references a variable in the error message that may not be set, but the unsplit command uses tracked port names. Wrong expected max values create false failures across hardware revisions.

## Test Signals

Signals are successful split commands and `physical_ports` occupancy equaling the expected maximum.
