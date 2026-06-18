<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/Makefile

## Purpose
Builds POSIX message queue correctness and performance selftests.

## Important APIs, Types, and Functions
- `CFLAGS += -O2`.
- `LDLIBS = -lrt -lpthread -lpopt`.
- `TEST_GEN_PROGS := mq_open_tests mq_perf_tests`.
- Includes `../lib.mk`.

## Control Flow
Kselftest compiles both C programs and links realtime, pthread, and popt libraries.

## State and Persistence Behavior
Only build artifacts are generated.

## Dependencies and Integration Points
Requires POSIX mqueue library support, pthreads, popt, and kselftest infrastructure.

## Risks and Edge Cases
The runtime tests need root to adjust mqueue sysctls and resource limits; build success alone does not imply they can run fully.

## Test Signals
Build creates `mq_open_tests` and `mq_perf_tests`; runtime output comes from those programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mqueue/Makefile -->
