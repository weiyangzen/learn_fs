# sources/distributed-fs/ceph-client/tools/testing/selftests/filelock/Makefile

## Purpose
Registers the open-file-description lock test binary.

## Important APIs, Types, And Functions
Defines `TEST_GEN_PROGS := ofdlocks` and includes `../lib.mk`.

## Control Flow
kselftest builds `ofdlocks.c`.

## State And Persistence
Generated binary only.

## Dependencies And Integration Points
Depends on kernel support for `F_OFD_SETLK` and `F_OFD_GETLK`.

## Risks
No special CFLAGS are set; warnings are not elevated.

## Test Signals
Successful build creates `ofdlocks`.
