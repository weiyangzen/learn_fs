<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/safesetid/safesetid-test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/safesetid/safesetid-test.sh

## Purpose

Shell wrapper that gates the SafeSetID binary on root privileges and returns kselftest skip when not runnable.

## Important APIs, Types, and Functions

Uses id -u/root check, ksft_skip=4 convention, and executes ./safesetid-test.

## Control Flow and Integration

If not root it exits with skip. Otherwise it launches the generated C binary and propagates its status.

## State and Persistence Behavior

No state beyond the C binary state changes.

## Dependencies and Integration Points

Depends on generated safesetid-test, root privileges, and kselftest exit-code conventions.

## Risks and Edge Cases

Wrapper cannot protect against the C binary mutating passwd/group/securityfs; it only avoids non-root false failures.

## Test Signals

Pass/skip/fail status mirrors root availability and C binary result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/safesetid/safesetid-test.sh -->
