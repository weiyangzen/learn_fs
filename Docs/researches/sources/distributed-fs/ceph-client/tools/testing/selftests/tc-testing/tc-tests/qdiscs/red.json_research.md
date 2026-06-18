# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/red.json

## Purpose
Defines nine TDC cases for `red`. It covers creation with no flags, `adaptive`, `ecn`, combinations with `harddrop` and `nodrop`, rejection of invalid `nodrop` alone, and class display.

## Important APIs, Types, and Functions
The cases exercise `tc qdisc add ... red` option parsing for RED thresholds/probability/flags and `tc class show` for the class view.

## Control Flow
TDC attaches RED with each flag combination, verifies the resulting display or expected parser failure, then tears down the qdisc. The invalid case expects nonzero exit rather than output match success.

## State and Persistence Behavior
RED stores queue thresholds, probability, and ECN/drop policy in kernel qdisc state. No persistent state exists outside the JSON.

## Dependencies and Integration Points
Depends on `sch_red`, `tc`, and namespace setup. It integrates with RED parser/display and class dump paths.

## Risks and Edge Cases
RED output may normalize thresholds and probabilities. Flag compatibility is semantic; parser changes around `nodrop` and `ecn` combinations can change expected failures.

## Test Signals
Signals include correct flag display for valid combinations, failure for `nodrop` without required context, and working class show.
