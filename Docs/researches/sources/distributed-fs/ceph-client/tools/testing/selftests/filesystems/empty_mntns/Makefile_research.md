# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/Makefile

## Purpose
Build metadata for empty mount namespace selftests.

## Important APIs, Types, And Functions
Adds `-Wall -O2 -g $(KHDR_INCLUDES) $(TOOLS_INCLUDES)` to `CFLAGS`, links libcap, defines `TEST_GEN_PROGS := empty_mntns_test overmount_chroot_test clone3_empty_mntns_test`, includes `../../lib.mk`, and adds dependencies on `../utils.c`.

## Control Flow
kselftest builds three C binaries, linking each with filesystem utility helpers.

## State And Persistence
Generated binaries only.

## Dependencies And Integration Points
Requires statmount/listmount headers/helpers, clone3 selftest headers, and libcap utilities through `../utils.c`.

## Risks
The tests require newer kernel APIs; build can succeed while runtime skips unsupported flags.

## Test Signals
Successful build creates all three empty mount namespace test executables.
