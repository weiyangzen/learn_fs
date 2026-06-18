<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/maybe_null_fail_dsp.bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/maybe_null_fail_dsp.bpf.c

## Purpose

Negative verifier fixture for sched_ext dispatch nullable task pointers.

## Important APIs, Types, and Functions

Defines maybe_null_running and a dispatch callback that dereferences the possibly-null dispatch task argument without a guard, then exposes sched_ext_ops maybe_null_fail.

## Control Flow and Integration

Loaded only by maybe_null.c as a skeleton expected to fail verification/open-and-load.

## State and Persistence Behavior

No persistent state; a successful load would be a regression.

## Dependencies and Integration Points

Depends on BPF verifier PTR_MAYBE_NULL semantics and sched_ext struct_ops types.

## Risks and Edge Cases

If verifier annotations change, the expected failure mode can need adjustment.

## Test Signals

maybe_null.c passes only when this skeleton fails to load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/maybe_null_fail_dsp.bpf.c -->
