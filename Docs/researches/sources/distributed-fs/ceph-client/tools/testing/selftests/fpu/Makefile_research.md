<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/Makefile

## Purpose
This Makefile builds and registers the kernel FPU selftest helper.

## Important APIs, Types, And Functions
It links with `-lm`, declares `TEST_GEN_PROGS := test_fpu`, `TEST_PROGS := run_test_fpu.sh`, and includes `../lib.mk`.

## Control Flow
kselftest builds `test_fpu` and runs the shell wrapper, which loads the kernel module and invokes many user-space helper instances.

## State And Persistence
The Makefile only produces build artifacts.

## Dependencies And Integration Points
It depends on libm for fenv functions and kselftest `lib.mk`.

## Risks
Missing math library linkage breaks `fesetround()`/`feenableexcept()` references.

## Test Signals
Successful compilation of `test_fpu` and execution through `run_test_fpu.sh` validate the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/Makefile -->
