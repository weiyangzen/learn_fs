<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/exit_test.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/exit_test.h

## Purpose

Header support file for sched_ext tests: shared enum for exit callback injection points.

## Important APIs, Types, and Functions

defines EXIT_SELECT_CPU, EXIT_ENQUEUE, EXIT_DISPATCH, EXIT_ENABLE, EXIT_INIT_TASK, EXIT_INIT, and NUM_EXITS

## Control Flow and Integration

included by exit.bpf.c and exit.c so userspace and BPF agree on rodata exit_point values

## State and Persistence Behavior

Static compile-time declarations only.

## Dependencies and Integration Points

Included by paired sched_ext BPF/userspace files.

## Risks and Edge Cases

Enum or flag drift breaks C/BPF agreement.

## Test Signals

Covered by compilation and the paired runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/exit_test.h -->
