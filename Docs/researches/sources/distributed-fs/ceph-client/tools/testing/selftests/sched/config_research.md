<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched/config

## Purpose

Minimal scheduler config fragment.

## Important APIs, Types, and Functions

Contains CONFIG_SCHED=y.

## Control Flow and Integration

Consumed by kselftest config tooling.

## State and Persistence Behavior

Static metadata only.

## Dependencies and Integration Points

Scheduler core is required for cs_prctl behavior.

## Risks and Edge Cases

Does not explicitly require core scheduling; unsupported kernels still fail/skip at runtime.

## Test Signals

Config merge plus cs_prctl_test execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched/config -->
