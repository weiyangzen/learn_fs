# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/binderfs/Makefile

## Purpose
Build metadata for binderfs selftests.

## Important APIs, Types, And Functions
Adds `$(KHDR_INCLUDES) -pthread` to `CFLAGS`, defines `TEST_GEN_PROGS := binderfs_test`, and includes `../../lib.mk`.

## Control Flow
kselftest builds the threaded binderfs C test.

## State And Persistence
Generated binary only.

## Dependencies And Integration Points
Pairs with config enabling Android binderfs and binder IPC.

## Risks
Requires pthread support and Android binder UAPI headers.

## Test Signals
Successful build creates `binderfs_test`.
