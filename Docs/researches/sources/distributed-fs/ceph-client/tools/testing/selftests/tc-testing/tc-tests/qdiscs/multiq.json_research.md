# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/multiq.json

## Purpose
Defines five TDC cases for the legacy `multiq` qdisc. It checks creation on an eight-queue device, class listing, missing/double delete behavior, and rejection on single-queue devices.

## Important APIs, Types, and Functions
The JSON uses `cmdUnderTest` entries for `$TC qdisc add ... multiq`, `$TC class show`, and delete operations. `plugins.requires` ties the tests to namespace/device setup.

## Control Flow
TDC creates the requested device, applies `multiq`, verifies the class view, and cleans up. Negative tests run operations when no qdisc exists or when the device does not expose multiple queues.

## State and Persistence Behavior
Runtime state is the classful `multiq` qdisc bound to hardware queues. No test data is persisted beyond the JSON file; cleanup should remove qdisc and device resources.

## Dependencies and Integration Points
Depends on `sch_multiq`, multiqueue device support, `tc`, and TDC plugins. It integrates with the qdisc creation, delete, and class enumeration paths.

## Risks and Edge Cases
Single-queue behavior and default child qdisc formatting can differ across kernel/iproute2 versions. Failing teardown can contaminate later qdisc tests on the same test device.

## Test Signals
Expected pass signals are successful attach and class list on a multiqueue device plus expected nonzero exits for absent qdisc and single-queue cases.
