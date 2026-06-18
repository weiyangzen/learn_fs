<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/verification/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/verification/Makefile

## Purpose
Registers the runtime-verification KTAP wrapper as a kselftest program.

## Important APIs, Types, and Functions
TEST_PROGS=verificationtest-ktap, TEST_FILES=test.d settings, EXTRA_CLEAN logs, ../lib.mk.

## Control Flow
Common kselftest Makefile wrapper with no local compilation.

## State and Persistence
No runtime state except logs under OUTPUT/logs.

## Dependencies and Integration Points
Depends on ../ftrace/ftracetest and runtime verification test data.

## Risks and Edge Cases
Wrapper assumes relative ftrace/verification directories exist.

## Test Signals
kselftest runs verificationtest-ktap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/verification/Makefile -->
