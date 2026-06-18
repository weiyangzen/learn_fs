# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/fat/rename_exchange.c

## Purpose

`rename_exchange.c` is a small helper that atomically swaps two paths with `renameat2(..., RENAME_EXCHANGE)`. It exists so the FAT shell test can exercise vfat rename-exchange behavior through a compiled helper.

## Important APIs, Types, and Functions

`print_usage` emits the required two-argument form. `main` validates `argc == 3`, calls `renameat2(AT_FDCWD, argv[1], AT_FDCWD, argv[2], RENAME_EXCHANGE)`, reports errors with `perror`, and exits success or failure.

## Control Flow, State, and Persistence

The program has one direct path: parse arguments, call the syscall wrapper exposed by libc with directory-relative current working directory fds, and exit. It persists only the filesystem namespace change produced by the atomic exchange.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on `_GNU_SOURCE`, `fcntl.h` exposing `renameat2` and `RENAME_EXCHANGE`, and kernel filesystem support for exchange rename. It integrates with `run_fat_tests.sh` against a mounted vfat image. Risks are missing libc declaration, unsupported syscall, or filesystem-specific exchange bugs. Passing signal is the two files trading names without content loss.
