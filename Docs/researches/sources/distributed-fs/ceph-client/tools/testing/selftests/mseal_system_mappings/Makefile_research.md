<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/Makefile

## Purpose
Builds the `sysmap_is_sealed` selftest for mseal-protected system mappings.

## Important APIs, Types, and Functions
- `CFLAGS += -std=c99 -pthread -Wall $(KHDR_INCLUDES)`.
- `TEST_GEN_PROGS := sysmap_is_sealed`.
- Includes `../lib.mk`.

## Control Flow
Kselftest compiles one generated test program with C99, pthreads, warnings, and kernel header includes.

## State and Persistence Behavior
Only build artifacts are produced.

## Dependencies and Integration Points
Depends on kselftest `lib.mk`, kernel headers, pthread support, and the corresponding source file outside this subset.

## Risks and Edge Cases
The makefile assumes the `sysmap_is_sealed` source exists in the directory. Runtime behavior depends on mseal system mapping support requested by config.

## Test Signals
Build success creates the `sysmap_is_sealed` binary; runtime signals come from that binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/Makefile -->
