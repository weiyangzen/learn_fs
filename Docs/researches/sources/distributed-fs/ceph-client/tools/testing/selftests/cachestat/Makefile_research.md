# sources/distributed-fs/ceph-client/tools/testing/selftests/cachestat/Makefile

## Purpose

This Makefile builds the cachestat syscall kselftest program.

## Important APIs, Types, and Functions

It sets `TEST_GEN_PROGS := test_cachestat`, appends `$(KHDR_INCLUDES)` and `-Wall` to `CFLAGS`, links `-lrt`, and includes `../lib.mk`.

## Control Flow

Kselftest `lib.mk` compiles `test_cachestat.c` into the generated test binary using kernel headers.

## State and Persistence Behavior

No runtime state is owned. Build artifacts are produced by kselftest.

## Dependencies and Integration Points

It depends on exported kernel headers containing cachestat syscall types and on librt availability. It integrates with the selftests build/run framework.

## Risks and Test Signals

Risks are stale headers or missing syscall definitions on older trees. Signals are successful compilation and execution of `test_cachestat`.
