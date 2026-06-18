<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/scx_test.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/scx_test.h

## Purpose

Header support file for sched_ext tests: shared header defining the sched_ext selftest registration ABI and assertion helpers.

## Important APIs, Types, and Functions

declares enum scx_test_status, struct scx_test callbacks, REGISTER_SCX_TEST constructor macro, SCX_ERR/FAIL/assertion macros, enum compatibility helpers, and SCX_BUG_ON behavior

## Control Flow and Integration

all sched_ext C tests include it so failures are reported consistently and runner registration is automatic

## State and Persistence Behavior

Static compile-time declarations only.

## Dependencies and Integration Points

Included by paired sched_ext BPF/userspace files.

## Risks and Edge Cases

Enum or flag drift breaks C/BPF agreement.

## Test Signals

Covered by compilation and the paired runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/scx_test.h -->
