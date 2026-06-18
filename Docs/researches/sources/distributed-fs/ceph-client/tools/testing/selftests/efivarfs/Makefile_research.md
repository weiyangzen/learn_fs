# sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/Makefile

## Purpose
Builds helper binaries and registers the efivarfs shell test.

## Important APIs, Types, And Functions
Sets `CFLAGS = -Wall`, `TEST_GEN_FILES := open-unlink create-read`, `TEST_PROGS := efivarfs.sh`, and includes `../lib.mk`.

## Control Flow
kselftest compiles `open-unlink.c` and `create-read.c`, then runs `efivarfs.sh`.

## State And Persistence
Generated helper binaries are placed in the output tree.

## Dependencies And Integration Points
Pairs with `config` requesting efivarfs and with shell tests that call the helpers from the working directory.

## Risks
No explicit `KHDR_INCLUDES`; helper compile relies on system headers for `linux/fs.h`.

## Test Signals
Successful build produces `open-unlink`, `create-read`, and the runnable shell test.
