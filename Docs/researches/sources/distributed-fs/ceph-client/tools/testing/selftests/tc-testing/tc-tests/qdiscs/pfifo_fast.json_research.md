# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/pfifo_fast.json

## Purpose
Defines five TDC tests for `pfifo_fast`, covering default creation, statistics dump, replacement with a different handle, valid deletion, and invalid handle deletion.

## Important APIs, Types, and Functions
The data uses `tc qdisc add|replace|del|show` against `pfifo_fast`. Verification checks qdisc display and stats output through TDC match fields.

## Control Flow
TDC creates the namespace device, applies or manipulates `pfifo_fast`, runs a show/stats command for verification, then removes the qdisc where applicable. Negative deletion validates handle lookup behavior.

## State and Persistence Behavior
The only runtime state is the qdisc instance and packet counters/statistics. Teardown removes the instance so a default qdisc from the kernel does not confuse later explicit tests.

## Dependencies and Integration Points
Depends on `pfifo_fast` availability in the kernel and `tc` display paths. It integrates with simple qdisc add/replace/delete and stats dump behavior.

## Risks and Edge Cases
`pfifo_fast` may be built in, deprecated, or affected by system default qdisc configuration. Stats output can be absent or formatted differently if the qdisc is not active.

## Test Signals
Signals are visible `pfifo_fast` qdisc output, stats dump success, replacement handle change, successful valid delete, and expected invalid-handle failure.
