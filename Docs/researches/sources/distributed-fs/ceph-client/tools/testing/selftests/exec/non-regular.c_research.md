# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/non-regular.c

## Purpose
Checks that executing non-regular files fails with the expected errno. It covers symlinks with `execv`, directories, block devices, character devices, FIFOs, and sockets with `fexecve`.

## Important APIs, Types, And Functions
Uses kselftest fixtures/variants, `symlink`, `mkdir`, `mknod`, `mkfifo`, `socket`, `execv`, and `fexecve`. Setup helpers include `rm()`, `setup_link()`, `setup_dir()`, `setup_node()`, and `setup_fifo()`.

## Control Flow
For each file variant, setup creates a path named `S_IF*.test`, the test calls `execv()` and checks errno, then teardown removes the path. Socket fixture separately creates an AF_INET stream socket and verifies `fexecve()` returns `EACCES`.

## State And Persistence
Creates temporary files/directories/nodes in the current directory and removes them. Device-node tests may skip if not root.

## Dependencies And Integration Points
Requires `/bin/true` or `/usr/bin/true` for symlink target, root for mknod variants, and kselftest harness.

## Risks
Symlink execution expects `ELOOP`, which depends on using `execv` on a symlink path in this context. Device-node setup can fail under restricted containers.

## Test Signals
Expected errno values are `ELOOP` for symlink and `EACCES` for directory, devices, FIFO, and socket.
