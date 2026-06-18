<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/util.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/util.h

## Purpose

Header for shared sched_ext file-write utility.

## Important APIs, Types, and Functions

Declares int file_write_long(const char *path, long val).

## Control Flow and Integration

Included by tests that need to write numeric sysfs controls while keeping implementation in util.c.

## State and Persistence Behavior

No state.

## Dependencies and Integration Points

Requires util.c to be linked into runner, which the Makefile does explicitly.

## Risks and Edge Cases

Prototype drift would break callers at compile time.

## Test Signals

Covered by sched_ext runner link and tests using file_write_long.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/util.h -->
