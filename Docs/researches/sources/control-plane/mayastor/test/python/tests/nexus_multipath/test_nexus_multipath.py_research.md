# sources/control-plane/mayastor/test/python/tests/nexus_multipath/test_nexus_multipath.py

## Purpose
Imperative pytest coverage for multi-path nexus behavior, NVMe reservation registrations, and adding/removing paths.

## Important APIs, Types, And Functions
Fixtures create nexuses without immediate destroy, second/third path nexuses, connected devices, pools, replicas, controller IDs, reservation keys, fio workload, and path verification. Tests cover reservation report with two controllers, adding a third path, removing a third path, and removing all paths.

## Control Flow
The suite creates two replicas, publishes one or more nexuses over the same children from different nodes, connects them with `nvme_connect`, verifies they map to one namespace, inspects `nvme list-subsys` path counts/states, and checks `nvme resv-report` registration keys and controller status bits.

## State And Persistence
State includes pools, replicas, multiple nexuses sharing children, kernel NVMe multipath controllers, reservation state on child replicas, and fio IO. Cleanup disconnects and destroys resources through fixtures.

## Dependencies And Integration Points
Depends on common `Volume`, `MayastorHandle`, NVMe helpers, fio, retrying, Docker fixtures, and `mayastor_pb2` enums.

## Risks
Reservation report ordering, path state values, and multipath timing are kernel and load dependent. Several fixtures intentionally delay cleanup until after path manipulation, so failed tests can leave controllers behind.

## Test Signals
Passing tests show correct namespace coalescing, reservation key registration across controllers, and path add/remove behavior.
