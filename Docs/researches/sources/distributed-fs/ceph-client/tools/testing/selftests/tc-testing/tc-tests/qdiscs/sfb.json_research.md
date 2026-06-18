# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/sfb.json

## Purpose
Defines 12 TDC cases for `sfb`, covering default creation and options `rehash`, `db`, `limit`, `max`, `target`, `increment`, `decrement`, `penalty_rate`, `penalty_burst`, change with `rehash`, and class display.

## Important APIs, Types, and Functions
The JSON drives `tc qdisc add|change|show ... sfb` and class show operations. It validates option parsing and output for stochastic fair blue parameters.

## Control Flow
For each parameter, the harness attaches SFB, checks qdisc output, and deletes it. The change case first creates SFB and then mutates rehash timing.

## State and Persistence Behavior
SFB keeps queue, bin, rehash, and penalty settings in kernel memory while attached. Test state is reset through teardown.

## Dependencies and Integration Points
Depends on `sch_sfb`, `tc`, and namespace support. It integrates with qdisc add/change/display and class dump paths.

## Risks and Edge Cases
Time/rate units may be printed in normalized forms. Because the tests do not inject traffic, they validate configuration more than queue behavior or flow accounting.

## Test Signals
Expected signals are successful parsing and display of each option, working `change`, and class show availability.
