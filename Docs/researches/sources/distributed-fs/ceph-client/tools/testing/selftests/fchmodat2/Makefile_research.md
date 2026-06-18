# sources/distributed-fs/ceph-client/tools/testing/selftests/fchmodat2/Makefile

## Purpose
Builds the `fchmodat2_test` binary with sanitizer instrumentation.

## Important APIs, Types, And Functions
Adds `-Wall -O2 -g -fsanitize=address -fsanitize=undefined $(KHDR_INCLUDES)` to `CFLAGS`, adds `-static-libasan` for non-LLVM builds, sets `TEST_GEN_PROGS := fchmodat2_test`, and includes `../lib.mk`.

## Control Flow
kselftest make compiles the C test; gcc gets static ASAN runtime handling while clang relies on its default static sanitizer behavior.

## State And Persistence
Generated binary only.

## Dependencies And Integration Points
Requires compiler sanitizer support and kernel headers for `__NR_fchmodat2`.

## Risks
Static ASAN linkage can fail on toolchains without sanitizer runtime. Sanitizers can affect portability in minimal environments.

## Test Signals
Successful build produces sanitizer-instrumented `fchmodat2_test`.
