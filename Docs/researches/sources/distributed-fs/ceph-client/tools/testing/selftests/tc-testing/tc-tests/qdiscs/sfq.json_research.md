# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/sfq.json

## Purpose
Defines 15 TDC cases for `sfq`. It covers default creation, `limit`, `perturb`, `quantum`, `divisor`, `flows`, `depth`, `headdrop`, `redflowlimit`, class show, and rejection of invalid or derived limit/perturb values.

## Important APIs, Types, and Functions
The file uses TDC JSON to run `tc qdisc add ... sfq`, `tc class show`, and negative parser/kernel validation cases. Expected outcomes are encoded through exit code and match fields.

## Control Flow
Each case creates an SFQ qdisc with one parameter variation or invalid combination, verifies output or failure, and tears it down. Derived-limit cases combine `limit`, `depth`, `flows`, or `divisor` to trigger kernel validation.

## State and Persistence Behavior
SFQ stores hashing, flow, depth, perturb timer, and optional RED-flow state in the kernel. No data persists beyond qdisc lifetime.

## Dependencies and Integration Points
Depends on `sch_sfq`, `tc`, namespace support, and class display. It integrates with SFQ option parsing and validation logic.

## Risks and Edge Cases
Boundary cases are coupled to SFQ internal constraints. Perturb timer validation depends on signed/integer parsing and may produce version-specific error text.

## Test Signals
Signals include successful option display, class show success, and expected rejections for limit of one, derived limit of one, negative perturb, and too-large perturb.
