# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/move_mount/Makefile

## Purpose

This Makefile builds `move_mount_test`, focused on `MOVE_MOUNT_BENEATH` semantics.

## Important APIs, Types, and Functions

It sets warning, optimization, debug, and kernel header flags, declares `TEST_GEN_PROGS := move_mount_test`, lists local headers `../wrappers.h ../utils.h ../statmount/statmount.h`, includes `../../lib.mk`, and links `move_mount_test` with `../utils.c`.

## Control Flow, State, and Persistence

There is no runtime logic. The Makefile wires wrapper and utility dependencies into the generated test.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on local wrappers/utilities, statmount helpers, kselftest rules, and current kernel headers. It integrates the move_mount regression into the selftest suite. Risks are missing newer constants in older headers. Passing signals are successful compile and test binary generation.
