# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/skbprio.json

## Purpose
Defines four TDC cases for `skbprio`: default creation, creation with `limit`, change with `limit`, and class display.

## Important APIs, Types, and Functions
The JSON invokes `tc qdisc add|change|show ... skbprio` and `tc class show`, with expected matches on displayed parameters.

## Control Flow
TDC attaches `skbprio`, checks default or configured limit output, mutates the limit for the change case, and cleans up.

## State and Persistence Behavior
The qdisc maintains packet priority queues and a queue limit in kernel state. The JSON persists only static test definitions.

## Dependencies and Integration Points
Depends on `sch_skbprio`, `tc`, and namespace setup. It integrates with qdisc add/change and class show.

## Risks and Edge Cases
Coverage is configuration-only and does not validate actual priority dequeue behavior. Output formatting for defaults can vary with kernel/iproute2 versions.

## Test Signals
Signals are successful add/change operations, expected `limit` display, and working class show.
