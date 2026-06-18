<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/Makefile

## Purpose

Build/register fragment for seccomp selftests.

## Important APIs, Types, and Functions

Adds no-as-needed linker flag, warnings and KHDR includes, links libcap, and declares TEST_GEN_PROGS seccomp_bpf and seccomp_benchmark.

## Control Flow and Integration

lib.mk compiles both seccomp binaries and exposes them to kselftest install/run.

## State and Persistence Behavior

Build metadata only.

## Dependencies and Integration Points

Kernel headers, libcap, seccomp_bpf source in same directory, common lib.mk.

## Risks and Edge Cases

Linker flag ordering matters for tests that depend on library constructors/symbol retention.

## Test Signals

Build should produce seccomp_bpf and seccomp_benchmark; run_tests should execute both.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/Makefile -->
