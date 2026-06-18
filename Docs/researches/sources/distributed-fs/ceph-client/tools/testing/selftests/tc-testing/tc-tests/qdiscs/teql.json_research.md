# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/teql.json

## Purpose
Defines five TDC cases for `teql`. It covers default creation, use with multiple devices, valid deletion, stats display, and rejection when attempting to add TEQL as a child qdisc.

## Important APIs, Types, and Functions
The JSON drives `tc qdisc add|del|show ... teql` and stats commands. It uses namespace setup to provide one or more test devices.

## Control Flow
TDC prepares devices, attaches TEQL at root, verifies normal or stats output, and deletes state. The child-qdisc case attempts an invalid placement and expects failure.

## State and Persistence Behavior
TEQL creates kernel qdisc state and may create/coordinate with a TEQL virtual device depending on kernel support. Teardown must remove qdisc attachments from all participating devices.

## Dependencies and Integration Points
Depends on `sch_teql`, `tc`, namespace setup, and multiple devices for aggregation coverage. It integrates with qdisc creation, stats display, and parent/child placement validation.

## Risks and Edge Cases
TEQL is uncommon and may not be enabled in all kernels. Multi-device tests are sensitive to setup cleanup, and virtual-device naming can affect matching.

## Test Signals
Signals include successful root TEQL creation on one and multiple devices, stats output availability, valid deletion, and expected failure as a child qdisc.
