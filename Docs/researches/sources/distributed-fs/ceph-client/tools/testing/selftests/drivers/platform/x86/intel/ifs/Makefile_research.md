# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/platform/x86/intel/ifs/Makefile

## Purpose
Registers the Intel In Field Scan shell test with kselftest.

## Important APIs, Types, And Functions
Defines `TEST_PROGS := test_ifs.sh` and includes the platform selftest `lib.mk` path. No build products are compiled.

## Control Flow
kselftest runs `test_ifs.sh` directly.

## State And Persistence
No state beyond install/run metadata.

## Dependencies And Integration Points
Depends on `test_ifs.sh` for all runtime probing and on the platform/x86 Intel IFS driver.

## Risks
Shell-only registration means build cannot catch syntax or runtime environment issues.

## Test Signals
Successful install/run exposes `test_ifs.sh` as the single IFS test program.
