<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/hotplug_test.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/hotplug_test.h

## Purpose

Header support file for sched_ext tests: shared flags for sched_ext hotplug exit reasons.

## Important APIs, Types, and Functions

defines HOTPLUG_EXIT_RSN and HOTPLUG_ONLINING bit flags

## Control Flow and Integration

included by hotplug BPF and C sides to decode restart/onlining versus offlining exits

## State and Persistence Behavior

Static compile-time declarations only.

## Dependencies and Integration Points

Included by paired sched_ext BPF/userspace files.

## Risks and Edge Cases

Enum or flag drift breaks C/BPF agreement.

## Test Signals

Covered by compilation and the paired runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/hotplug_test.h -->
