# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/tbf.json

## Purpose
Defines nine TDC cases for `tbf`, covering default creation, `mtu`, `peakrate`, `latency`, `overhead`, `linklayer`, replace with `mtu`, change with latency time, and class show.

## Important APIs, Types, and Functions
The JSON invokes `tc qdisc add|replace|change|show ... tbf` and `tc class show`. It validates token bucket parser/display behavior for rate, burst, latency, and link-layer accounting options.

## Control Flow
The harness attaches TBF with one option variation, verifies qdisc/class output, and tears down. Replace/change cases start from an existing TBF qdisc.

## State and Persistence Behavior
TBF keeps token bucket rates, burst/latency/MTU, peakrate, and link-layer adjustment state in kernel memory while attached. The JSON has no runtime persistence.

## Dependencies and Integration Points
Depends on `sch_tbf`, `tc`, and namespace setup. It integrates with rate-table calculations and qdisc/class display.

## Risks and Edge Cases
Rate and time values are often normalized or rounded, so output matching can be brittle. Link-layer and overhead behavior depends on stable iproute2/kernel accounting semantics.

## Test Signals
Signals are successful add/replace/change operations, expected display of configured parameters, class show success, and clean deletion.
