# sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/Makefile

## Purpose
Top-level sparc64 selftest Makefile that only builds/runs on sparc64 and delegates to the `drivers` subdirectory.

## Important APIs, types, and functions
Normalizes `ARCH` by mapping `x86_64` to `x86`. Non-sparc64 defines a silent `nothing` target. On sparc64 it sets `SUBDIRS := drivers` and `TEST_PROGS := run.sh`.

## Control flow
The sparc64 branch includes `../lib.mk`, loops through subdirectories to build into `$(OUTPUT)/<subdir>`, copies subdir test scripts, and overrides install/clean rules to recurse.

## State and persistence
Writes build outputs in per-subdir output directories and installs tests under `$(INSTALL_PATH)`.

## Dependencies and integration points
Integrates sparc64-specific driver tests with kselftest and `drivers/Makefile`.

## Risks
The custom shell loop assumes subdir scripts follow `<subdir>_test.sh`. Non-sparc64 silently does nothing, so missing tests on cross builds may be expected.

## Test signals
On sparc64, successful build creates `drivers/adi-test` and `run.sh` executes the drivers test script.
