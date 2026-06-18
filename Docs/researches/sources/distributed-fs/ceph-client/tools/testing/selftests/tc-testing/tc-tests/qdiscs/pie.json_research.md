# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/pie.json

## Purpose
Defines a single TDC case for `pie`, specifically testing qdisc limit trimming behavior.

## Important APIs, Types, and Functions
The JSON uses the standard TDC fields to create/configure a PIE qdisc and verify output. The command path targets `tc qdisc` parser support for `pie` and its `limit` handling.

## Control Flow
The harness prepares the device, runs the PIE command under test, validates the resulting qdisc output or error expectation, and deletes qdisc state during teardown.

## State and Persistence Behavior
PIE maintains active queue management parameters and queue state only while attached to the device. The test persists no data outside the static JSON definition.

## Dependencies and Integration Points
Depends on `sch_pie`, `tc`, and namespace setup. It integrates with the PIE qdisc option parser and display code.

## Risks and Edge Cases
The file provides narrow coverage. Kernel or iproute2 changes around minimum/maximum limit trimming can alter output and expected behavior without affecting basic PIE creation.

## Test Signals
The primary signal is the expected limit value after trimming, as reported by `tc qdisc show`, with clean teardown afterward.
