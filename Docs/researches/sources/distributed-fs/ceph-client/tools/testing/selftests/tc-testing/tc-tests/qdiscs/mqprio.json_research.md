# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/mqprio.json

## Purpose
Defines five TDC tests for `mqprio`, focused on multiqueue creation, deletion edge cases, single-queue rejection, and class display.

## Important APIs, Types, and Functions
The cases use the TDC JSON schema and call `$TC qdisc add ... mqprio`, delete, and class show commands. Setup provisions multiqueue or single-queue devices through namespace/netdev helpers.

## Control Flow
For valid cases, setup creates an eight-queue device, `mqprio` is attached as root, and class output is checked. Invalid cases attempt deletion before creation, double deletion, or attachment to a single-queue device.

## State and Persistence Behavior
The kernel owns the qdisc and traffic class mapping while the test runs. Teardown must remove qdisc/device state because mqprio maps traffic classes to hardware queues.

## Dependencies and Integration Points
Depends on `sch_mqprio`, multiqueue netdevices, netdevsim or equivalent test setup, `tc`, and `nsPlugin`. It reaches both the qdisc parser and class dump paths.

## Risks and Edge Cases
Queue count and hardware-offload defaults can differ across environments. Class output can be sensitive to default mapping chosen by iproute2/kernel when optional parameters are omitted.

## Test Signals
Successful add on eight queues, expected failure on single queue or missing delete, and stable class dump output are the primary signals.
