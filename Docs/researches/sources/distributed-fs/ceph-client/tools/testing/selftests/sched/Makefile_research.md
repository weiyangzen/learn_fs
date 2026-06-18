<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched/Makefile

## Purpose

Build/register fragment for scheduler selftests in this directory.

## Important APIs, Types, and Functions

Adds CFLAGS with optimization, warnings, debug, KHDR includes and rpath, links pthread, sets TEST_GEN_FILES and TEST_PROGS to cs_prctl_test, and includes ../lib.mk.

## Control Flow and Integration

Common kselftest rules compile cs_prctl_test and run it as the sole sched test program here.

## State and Persistence Behavior

Build metadata only.

## Dependencies and Integration Points

Kernel headers, pthread, lib.mk.

## Risks and Edge Cases

Incorrect rpath/include handling can break out-of-tree selftest builds.

## Test Signals

make/run_tests should build and execute cs_prctl_test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched/Makefile -->
