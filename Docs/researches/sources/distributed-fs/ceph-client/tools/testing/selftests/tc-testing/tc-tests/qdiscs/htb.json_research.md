# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/htb.json

## Purpose
Defines 12 `tdc` JSON test cases for the `htb` qdisc and HTB classes. The file exercises root HTB creation, `default`, `r2q`, `direct_qlen`, class rate/burst/mpu/prio/ceil/cburst/mtu/quantum options, and deletion by handle.

## Important APIs, Types, and Functions
This is data consumed by `tdc.py`, not executable code. Important schema fields are `id`, `name`, `category`, `plugins.requires`, `setup`, `cmdUnderTest`, `expExitCode`, `verifyCmd`, `matchPattern` or `matchJSON`, and `teardown`. The commands target `$TC qdisc` and `$TC class` operations against namespace-managed `$DEV0`.

## Control Flow
`tdc.py` loads the array, substitutes `NAMES` variables, lets `nsPlugin` create the test namespace/veth topology, runs setup, executes the HTB command under test, verifies `tc` output, and tears down qdiscs/classes. Class tests first install the parent HTB qdisc before adding class `1:1`.

## State and Persistence Behavior
State is transient kernel traffic-control state attached to the test device. The JSON persists no runtime state; successful runs rely on teardown deleting the qdisc so later tests do not inherit handles, defaults, or classes.

## Dependencies and Integration Points
Depends on the `sch_htb` kernel module, `/sbin/tc`, namespace support through `nsPlugin`, and TDC variable substitution. It integrates with HTB parser/kernel validation through `tc qdisc add`, `tc class add`, `tc qdisc show`, and `tc class show`.

## Risks and Edge Cases
The tests are sensitive to exact iproute2 formatting and HTB unit normalization. Some option combinations such as `quantum`, `mtu`, or `mpu` are accepted but may display rounded values. Missing `sch_htb` or namespace setup turns parser coverage into environment failure.

## Test Signals
Good signals are expected zero exit codes for valid add/delete cases, matching class/qdisc show output for configured options, and clean deletion by handle without residual HTB state.
