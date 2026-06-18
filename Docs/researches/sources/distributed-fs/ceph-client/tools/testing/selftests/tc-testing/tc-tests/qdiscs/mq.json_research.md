# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/mq.json

## Purpose
Defines eight TDC cases for the `mq` qdisc on multi-queue and single-queue devices. It verifies valid creation on four-queue and 256-queue netdevsim devices, duplicate add rejection, missing/double delete behavior, single-queue rejection, class dump, and invalid parent replacement.

## Important APIs, Types, and Functions
The JSON relies on `nsPlugin` and netdevsim-related setup commands to create devices with specific queue counts. Commands exercise `$TC qdisc add dev ... root mq`, delete, replace, and class show operations.

## Control Flow
Setup creates a device with the required queue topology, the harness installs or manipulates `mq`, then verification reads `tc` qdisc/class output. Negative tests deliberately run operations on absent qdiscs, single-queue devices, or invalid parent handles.

## State and Persistence Behavior
Runtime state is the kernel qdisc tree and per-TX-queue child qdisc structure. JSON state is static. Teardown removes qdiscs and netdevsim devices to avoid queue topology leakage into later tests.

## Dependencies and Integration Points
Depends on netdevsim, multiqueue netdevice support, `sch_mq`, `tc`, and namespace management. It integrates with qdisc grafting and class enumeration for hardware transmit queues.

## Risks and Edge Cases
Environment support is the main risk: netdevsim creation and queue counts must work. Output can vary with default child qdisc selection. The 256-queue case is useful for scaling but may expose kernel or userspace formatting limits.

## Test Signals
Signals include successful root `mq` creation on multiqueue devices, correct class list generation, explicit rejection on single-queue devices, and failure for duplicate or invalid-parent operations.
