# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/Makefile

## Purpose

This Makefile builds overlayfs selftests for mapping device/inode reporting and fd-based layer configuration.

## Important APIs, Types, and Functions

It adds warning and kernel header CFLAGS, links with `-lcap`, lists local headers `../wrappers.h log.h`, and declares `TEST_GEN_PROGS := dev_in_maps set_layers_via_fds`. The `set_layers_via_fds` target also compiles with `../utils.c`.

## Control Flow, State, and Persistence

There is no runtime flow. Build metadata ensures the tests have wrapper, logging, utility, and libcap support.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are overlayfs-capable kernel headers, libcap, wrappers, utils, and kselftest rules. It integrates overlayfs new mount API tests into the suite. Risks include missing libcap development files. Passing signals are successful compile and link of both generated programs.
