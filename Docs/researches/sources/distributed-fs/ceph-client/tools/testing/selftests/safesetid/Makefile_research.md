<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/safesetid/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/safesetid/Makefile

## Purpose

Builds and registers SafeSetID selftests.

## Important APIs, Types, and Functions

Sets CFLAGS=-Wall -O2, LDLIBS=-lcap, TEST_PROGS=safesetid-test.sh, TEST_GEN_FILES=safesetid-test, and includes ../lib.mk.

## Control Flow and Integration

Common kselftest make rules compile safesetid-test and install/run the shell wrapper.

## State and Persistence Behavior

Build metadata only.

## Dependencies and Integration Points

Requires libcap headers/library and kselftest lib.mk.

## Risks and Edge Cases

Missing libcap causes build failure; wrapper depends on generated binary name.

## Test Signals

A successful make produces safesetid-test and run_tests invokes the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/safesetid/Makefile -->
