# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/Makefile

## Purpose

This Makefile builds nsfs ioctl selftests.

## Important APIs, Types, and Functions

`TEST_GEN_PROGS := owner pidns iterate_mntns` declares the three generated programs. `CFLAGS := -Wall -Werror` turns warnings into build failures, and `../../lib.mk` supplies the kselftest rules.

## Control Flow, State, and Persistence

There is no runtime flow in the Makefile. It persists build intent for the nsfs test directory.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on common kselftest rules and headers available to each C file. It integrates owner, pid namespace parent, and mount namespace iteration tests. Risks are warning drift breaking `-Werror`. Passing signal is successful generation of all three binaries.
