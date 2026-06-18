# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/config

## Purpose

This config fragment declares kernel configuration prerequisites for the FAT selftests.

## Important APIs, Types, and Functions

It requires `CONFIG_BLK_DEV_LOOP=y` for loopback mounting disk images and `CONFIG_VFAT_FS=y` for the vfat filesystem implementation.

## Control Flow, State, and Persistence

There is no control flow. The fragment is consumed by kselftest or kernel test configuration tooling as static requirement metadata.

## Dependencies, Integration Points, Risks, and Test Signals

The fragment integrates with `run_fat_tests.sh`, which formats a vfat image and mounts it with `-o loop`. Without either option, the test cannot mount its target filesystem. Passing signals are a loop-backed vfat mount succeeding and the test not skipping or failing due to absent kernel support.
