# sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/drivers/Makefile

## Purpose
Builds the sparc64 ADI privileged driver selftest binary and registers its wrapper script.

## Important APIs, types, and functions
Sets include path `-I.`, `CFLAGS` with warnings, optimization, and debug info, `TEST_GEN_FILES := adi-test`, and `TEST_PROGS := drivers_test.sh`.

## Control flow
The custom `$(OUTPUT)/adi-test: adi-test.c` target is handed to kselftest `../../lib.mk` for build/install orchestration.

## State and persistence
Only build outputs are produced.

## Dependencies and integration points
Depends on `adi-test.c`, local `kselftest.h` include path, and the parent sparc64 Makefile.

## Risks
Only meaningful on sparc64 with the ADI driver available.

## Test signals
Build emits `adi-test`; runtime wrapper reports skip/ok/fail around module loading and binary execution.
