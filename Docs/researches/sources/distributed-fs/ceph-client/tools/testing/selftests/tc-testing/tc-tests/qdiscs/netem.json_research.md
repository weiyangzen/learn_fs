# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/netem.json

## Purpose
Defines 20 TDC cases for the `netem` qdisc. It covers default creation, `limit`, delay distributions, corruption, duplication, loss modes, reorder, rate and slot options, change/replace/delete paths, class display, and duplicate-netem restrictions in qdisc trees.

## Important APIs, Types, and Functions
The file drives `tc qdisc add|change|replace|del|show` with `netem` options and uses `matchPattern`/`matchJSON` verification. Several cases build nested qdisc trees to validate kernel restrictions on duplicate netem instances.

## Control Flow
Each case creates the namespace device, optionally prepares parent/child qdiscs, runs the netem command, verifies `tc` output or expected error, and deletes the qdisc tree. Tree-duplication cases test both root and non-root paths and across branches.

## State and Persistence Behavior
The kernel maintains delay/loss/corruption/reorder/rate/slot parameters while the qdisc exists. The JSON is static, and teardown must clear nested trees so later tests do not see existing handles.

## Dependencies and Integration Points
Depends on `sch_netem`, qdisc class/graft support, `tc`, and namespace plugin support. It integrates deeply with netem option parsing and kernel duplicate detection.

## Risks and Edge Cases
Netem output includes normalized units and optional fields, making regex matching fragile across versions. Distribution support may require installed distribution files or kernel support. Duplicate restriction tests are sensitive to qdisc tree setup correctness.

## Test Signals
Strong signals include correct display of configured impairment parameters, successful change/replace behavior, rejection of illegal duplicate netem placement, and clean deletion by handle.
