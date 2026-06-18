<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/Makefile

## Purpose
This Makefile builds the futex functional test binaries and conditionally links libnuma support for NUMA/MPOL tests.

## Important APIs, Types, And Functions
It detects `pkg-config numa --atleast-version 2.0.18`, sets include paths to futex headers and kselftest headers, enables pthread/time64 flags, links `-lpthread -lrt` and optional `-lnuma`, and declares all functional `TEST_GEN_PROGS`.

## Control Flow
kselftest compiles wait, requeue, PI, waitv, NUMA, private hash, and robust list tests and installs `run.sh`.

## State And Persistence
It creates build outputs only.

## Dependencies And Integration Points
It depends on kernel headers, futex local headers, pthread, rt, optional libnuma, and kselftest `lib.mk`.

## Risks
The `LIBNUMA_VER_*` define changes runtime coverage; without sufficient libnuma the MPOL subtest reports skip. Time64 flags intentionally affect syscall wrapper selection.

## Test Signals
All listed binaries compile, and `futex_numa_mpol` reports MPOL pass only when libnuma is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/Makefile -->
