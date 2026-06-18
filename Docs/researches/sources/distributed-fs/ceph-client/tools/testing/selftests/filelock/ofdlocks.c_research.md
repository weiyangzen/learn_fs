# sources/distributed-fs/ceph-client/tools/testing/selftests/filelock/ofdlocks.c

## Purpose
Tests open-file-description lock conflict and query behavior, including `F_OFD_GETLK` with `F_UNLCK` and length-zero ranges.

## Important APIs, Types, And Functions
Uses `fcntl(F_OFD_SETLK)`, `fcntl(F_OFD_GETLK)`, `struct flock`, and helpers `lock_set()` and `lock_get()`.

## Control Flow
The program creates `/tmp/aa`, opens it twice, unlinks it, sets a read lock on the first fd, verifies another read lock does not conflict, verifies write lock query conflicts, queries lock info from the locking fd with `F_UNLCK`, compares length-one and length-zero queries, and verifies the second fd does not report its own lock.

## State And Persistence
Creates and unlinks `/tmp/aa`, keeping the file alive through open fds only.

## Dependencies And Integration Points
Requires OFD lock support in the kernel and writable `/tmp`.

## Risks
The test uses `assert()` for open failures and returns `-1` on failures rather than full kselftest result accounting. `/tmp/aa` name can collide if already present, because open uses `O_EXCL`.

## Test Signals
Printed `[SUCCESS]` lines and zero exit indicate correct OFD lock behavior; failures return nonzero after mismatch.
