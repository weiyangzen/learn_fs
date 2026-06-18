<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/Makefile

## Purpose
Builds user_events ABI, dynamic-events, ftrace, and perf kselftests.

## Important APIs, Types, and Functions
TEST_GEN_PROGS=ftrace_test dyn_test perf_test abi_test; TEST_FILES=settings; CFLAGS/LDLIBS; ../lib.mk.

## Control Flow
Adds trace/user_events include flags and links rt, pthread, and math libraries through common kselftest rules.

## State and Persistence
No runtime state except generated binaries.

## Dependencies and Integration Points
Depends on kernel headers exposing linux/user_events.h and kselftest build infrastructure.

## Risks and Edge Cases
Build success does not guarantee tracefs mount or root privileges at runtime.

## Test Signals
All four generated tests compile and are discoverable by kselftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/Makefile -->
