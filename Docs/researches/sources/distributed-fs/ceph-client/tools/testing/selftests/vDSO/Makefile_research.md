<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/Makefile

## Purpose
Builds the vDSO selftest suite, including parser-linked tests, x86 nolibc standalone test, getrandom, and architecture ChaCha assembly validation.

## Important APIs, Types, and Functions
TEST_GEN_PROGS, CFLAGS_NOLIBC, per-target dependencies, vgetrandom-chacha.S target includes.

## Control Flow
Includes Makefile.arch, lists vDSO test binaries, wires parse_vdso.c into symbol-lookup tests, configures nolibc flags for x86 standalone, and adds include paths for getrandom/chacha tests.

## State and Persistence
No runtime state; generated binaries are kselftest artifacts.

## Dependencies and Integration Points
Depends on tools/include, arch headers, kernel UAPI headers, and common selftest lib.mk.

## Risks and Edge Cases
Conditional x86 standalone and arch assembly include paths must match source tree layout.

## Test Signals
Build success for each target and kselftest execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vDSO/Makefile -->
