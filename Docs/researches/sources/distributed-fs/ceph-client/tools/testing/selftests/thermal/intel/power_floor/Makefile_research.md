# sources/distributed-fs/ceph-client/tools/testing/selftests/thermal/intel/power_floor/Makefile

## Purpose
Builds the Intel power floor notification selftest on x86 hosts only.

## Important APIs, Types, and Functions
Normalizes `ARCH` values matching `i.86` or `x86_64` to `x86`, sets `TEST_GEN_PROGS := power_floor_test` when `ARCH` is x86, and includes `../../../lib.mk`.

## Control Flow
If not cross-compiling and the normalized architecture is x86, kselftest builds `power_floor_test`. Otherwise no test program is generated from this Makefile.

## State and Persistence Behavior
Only build artifacts are produced. Runtime sysfs state is controlled by the C test, not the Makefile.

## Dependencies and Integration Points
Depends on kselftest `lib.mk` and an x86 build environment. It integrates with the thermal Intel selftest tree.

## Risks and Edge Cases
Cross-compile builds are intentionally skipped. Architecture detection depends on `uname -m` when `ARCH` is unset.

## Test Signals
Signal is generation of `power_floor_test` on native x86 builds and omission elsewhere.
