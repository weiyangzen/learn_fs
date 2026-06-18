# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/Makefile

## Purpose
This Makefile builds the ublk selftest userspace daemon `kublk`, the `metadata_size` utility, and a large suite of shell-driven ublk tests. It also defines convenience targets for running test groups sequentially or in parallel.

## Important APIs, Types, and Functions
It sets `CFLAGS` with optimization, warnings, UAPI include path, and optional `-Werror`; links pthread, math, and liburing; declares many `TEST_PROGS`; sets `TEST_GEN_PROGS_EXTENDED = kublk metadata_size`; and defines `run_<group>` and `run_all` targets parameterized by `JOBS`.

## Control Flow
`kublk` is built from all `.c` files except `metadata_size.c`; `metadata_size` is a standalone utility. The `check` target runs shellcheck. Group targets derive groups from `test_<group>_<num>.sh` names and either run through kselftest `RUN_TESTS` or `xargs -P` for parallel execution.

## State and Persistence
Build outputs are generated in the selftest output directory. Test runs create runtime devices and temporary files through shell scripts, not through this Makefile directly.

## Dependencies and Integration Points
It depends on liburing, pthreads, UAPI headers, kselftest `lib.mk`, shellcheck for `check`, and all adjacent ublk C/shell files.

## Risks
Parallel execution intentionally ignores aggregate `xargs` failure with `|| true`, so group parallel targets may need external result collection. The generated group list is naming-convention-dependent.

## Test Signals
Build success for `kublk` and `metadata_size` plus kselftest registration of shell scripts are the primary signals. Group targets provide operator-level smoke/stress execution.
