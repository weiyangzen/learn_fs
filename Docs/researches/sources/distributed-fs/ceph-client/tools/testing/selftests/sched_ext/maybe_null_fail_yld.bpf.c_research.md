<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/maybe_null_fail_yld.bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/maybe_null_fail_yld.bpf.c

## Purpose

Negative verifier fixture for sched_ext yield nullable target pointers.

## Important APIs, Types, and Functions

Defines maybe_null_running and yield callback that dereferences the nullable `to` task argument without checking, then exposes sched_ext_ops maybe_null_fail.

## Control Flow and Integration

Loaded by maybe_null.c solely to confirm verifier rejection.

## State and Persistence Behavior

No persistent state.

## Dependencies and Integration Points

BPF verifier nullability tracking for sched_ext yield callback arguments.

## Risks and Edge Cases

Verifier or callback signature changes can alter the expected rejection.

## Test Signals

maybe_null.c expects open_and_load to return NULL/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/maybe_null_fail_yld.bpf.c -->
