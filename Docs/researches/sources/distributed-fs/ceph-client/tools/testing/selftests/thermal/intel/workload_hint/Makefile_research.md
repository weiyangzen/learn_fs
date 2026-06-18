# sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/workload_hint/Makefile

## Purpose
Builds the Intel workload hint selftest on x86 hosts only.

## Important APIs, Types, and Functions
Normalizes `ARCH` to `x86`, sets `TEST_GEN_PROGS := workload_hint_test` for x86, and includes `../../../lib.mk`.

## Control Flow
The kselftest build includes this program only when not cross-compiling and when the normalized architecture is x86.

## State and Persistence Behavior
Only build artifacts are produced. Runtime workload-hint sysfs state is managed by the C program.

## Dependencies and Integration Points
Depends on kselftest `lib.mk` and an x86 native build. Integrates with Intel thermal workload hint tests.

## Risks and Edge Cases
No program is built for cross-compile or non-x86 contexts even if target hardware could expose compatible sysfs.

## Test Signals
Signal is generation of `workload_hint_test` on native x86 builds.
