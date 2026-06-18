<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/verification/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/verification/config

## Purpose
Declares CONFIG_RV as required for verification tests.

## Important APIs, Types, and Functions
CONFIG_RV=y.

## Control Flow
Static config fragment only.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Used by kselftest config tooling.

## Risks and Edge Cases
Runtime also needs ftrace test infrastructure.

## Test Signals
Config tooling requests runtime verification support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/verification/config -->
