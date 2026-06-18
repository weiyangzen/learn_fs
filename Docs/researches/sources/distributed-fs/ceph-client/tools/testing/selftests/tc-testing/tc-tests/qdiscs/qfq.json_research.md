# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/qfq.json

## Purpose
Defines 12 TDC cases for `qfq` and QFQ classes. It tests default qdisc creation, class `weight` and `maxpkt`, boundary values, multiple classes, delete, class show, big/small MTU behavior, and `stab` overhead greater than max packet length.

## Important APIs, Types, and Functions
The data drives `tc qdisc add ... qfq`, `tc class add/show`, and related setup commands. Cases use standard TDC JSON fields to encode expected success and failure.

## Control Flow
The harness installs QFQ, adds one or more classes with supplied parameters, verifies class/qdisc output or failure, then deletes by handle. MTU and `stab` cases prepare device/qdisc settings that affect QFQ admission checks.

## State and Persistence Behavior
QFQ class state, weights, packet-size bounds, and qdisc handles live in the kernel only for the test. Teardown removes the qdisc hierarchy.

## Dependencies and Integration Points
Depends on `sch_qfq`, `tc`, namespace setup, and link/MTU control. It integrates with classful qdisc operations and QFQ parameter validation.

## Risks and Edge Cases
Boundary tests are sensitive to kernel constants and device MTU. `stab` overhead interactions can produce failures that look environmental if link parameters are not reset.

## Test Signals
Expected signals include correct class output for weights/maxpkt, acceptance/rejection at documented bounds, and failure when overhead exceeds feasible packet length.
