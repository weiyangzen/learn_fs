# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/ntsync/Makefile

## Purpose
Builds the `ntsync` kselftest binary.

## Important APIs, Types, And Functions
Sets `TEST_GEN_PROGS := ntsync`, adds `$(KHDR_INCLUDES)` to `CFLAGS`, links pthread via `LDLIBS += -lpthread`, and includes `../../lib.mk`.

## Control Flow
kselftest make compiles `ntsync.c` and links with pthread support for the threaded wait tests.

## State And Persistence
No runtime state beyond generated binary output.

## Dependencies And Integration Points
Pairs with `config`, which requests `CONFIG_WINESYNC=y`, and with the Linux UAPI header `linux/ntsync.h`.

## Risks
The SPDX tag has `SPDX-LICENSE-IDENTIFIER` spelling rather than the normal `SPDX-License-Identifier`, which affects metadata scanners but not build behavior.

## Test Signals
Successful build produces the `ntsync` executable linked against pthread.
