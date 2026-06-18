# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/Makefile

## Purpose

This Makefile builds the statmount and listmount syscall selftests.

## Important APIs, Types, and Functions

It sets warning, optimization, debug, and kernel header CFLAGS; declares `TEST_GEN_PROGS := statmount_test statmount_test_ns listmount_test`; and includes `../../lib.mk`.

## Control Flow, State, and Persistence

There is no runtime flow. The kselftest make framework compiles three binaries.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on kernel headers exposing statmount/listmount structs and flags plus common kselftest rules. It integrates syscall ABI tests into the filesystems suite. Risks are older headers missing constants. Passing signal is successful compilation of all three binaries.
