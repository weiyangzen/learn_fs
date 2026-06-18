# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/prio.json

## Purpose
Defines 15 TDC cases for the classful `prio` qdisc. It covers normal egress add, maximum and invalid handles, unsupported arguments, band counts, priomap validation, replacement, duplicate add, nonexistent/double delete, invalid handle formats, and class display.

## Important APIs, Types, and Functions
The cases use `tc qdisc add|replace|del|show` and `tc class show` for `prio`. Validation is expressed through expected exit codes and `matchPattern`/`matchJSON` data.

## Control Flow
For each case, TDC prepares a device, applies the `prio` operation, verifies output or expected failure, then deletes the qdisc. Priomap tests intentionally vary array length and values to exercise parser and kernel constraints.

## State and Persistence Behavior
The qdisc stores band count and priority-to-band mapping while attached. The JSON file itself is immutable test input. Teardown must remove handles so duplicate-add tests remain isolated.

## Dependencies and Integration Points
Depends on `sch_prio`, `tc`, and namespace setup. It integrates with classful qdisc creation, parser bounds checking, and class dump code.

## Risks and Edge Cases
Priomap constraints are tightly coupled to `TC_PRIO_MAX` and `TCQ_PRIO_BANDS`; kernel constant changes require test updates. Exact error text and handle formatting can vary by iproute2 version.

## Test Signals
Signals include valid prio creation, correct class output, successful replacement with eight bands, and expected rejection of invalid bands, priomap, duplicate, and handle cases.
