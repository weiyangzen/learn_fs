# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/pauth/Makefile

## Purpose

The PAUTH Makefile builds the arm64 pointer-authentication selftests only when the compiler can generate the required code. It creates the main `pac` test, helper objects, and the `exec_target` helper program used to observe key changes across `exec()`.

## Important APIs, Types, and Functions

The Makefile sets `CFLAGS += -mbranch-protection=pac-ret`, probes GCC support for `-march=armv8.3-a`, trusts LLVM support, and emits `TEST_GEN_PROGS`, `TEST_GEN_FILES`, and `TEST_GEN_PROGS_EXTENDED`. Custom rules compile PAC-instruction users at ARMv8.3 and the runnable test executables at ARMv8.2.

## Control Flow and Data Flow

Make evaluates compiler support, conditionally registers generated tests, includes `../../lib.mk`, then applies custom object and binary rules. `helper.o` and `pac_corruptor.o` feed into `pac`; `helper.o` also feeds into `exec_target`.

## State and Persistence Behavior

No runtime state is stored. Build outputs are kselftest artifacts in `$(OUTPUT)`.

## Dependencies and Integration Points

It depends on kselftest `lib.mk`, the selected C compiler, branch-protection support, and arm64 architecture levels. The split ARMv8.2/ARMv8.3 targeting allows unsupported hardware to run the binary and report meaningful skips rather than faulting before checks.

## Risks and Edge Cases

The support probe is compiler-sensitive. Building too much code for ARMv8.3 can turn intended runtime skip/failure paths into illegal-instruction crashes on older CPUs. Cross-compile `CC` handling preserves top-level settings unless `CC` is plain `cc`.

## Test Signals

Expected build output includes `pac`, `exec_target`, `pac_corruptor.o`, and `helper.o` when compiler support exists; unsupported compilers should skip these targets cleanly.
