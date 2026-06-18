# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/Makefile

## Purpose

This Makefile registers the FAT/vfat filesystem selftest script and builds its helper program.

## Important APIs, Types, and Functions

`TEST_PROGS := run_fat_tests.sh` marks the shell test as the executable test entry. `TEST_GEN_PROGS_EXTENDED := rename_exchange` builds the helper used by the script. `CFLAGS` enables optimization, debug info, warnings, and kernel header includes before including `../../lib.mk`.

## Control Flow, State, and Persistence

There is no runtime flow in the Makefile. The kselftest framework builds `rename_exchange` as an extended generated program and runs `run_fat_tests.sh`.

## Dependencies, Integration Points, Risks, and Test Signals

The Makefile depends on common kselftest make rules and kernel headers for `renameat2` constants. It integrates the FAT rename-exchange regression into the filesystems selftests suite. Build risks are missing headers or unsupported `renameat2` declarations. Passing build signals are the generated helper and script being present in the test output.
