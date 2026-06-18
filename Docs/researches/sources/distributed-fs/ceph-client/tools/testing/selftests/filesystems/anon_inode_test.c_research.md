# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/anon_inode_test.c

## Purpose
Verifies that anonymous inode file descriptors returned by the new mount API `fsopen()` reject unsupported file operations: chown, chmod, exec, and procfd reopen.

## Important APIs, Types, And Functions
Uses wrapper `sys_fsopen("tmpfs", 0)`, `fchown`, `fchmod`, `execveat(..., AT_EMPTY_PATH)`, `dup2`, `open("/proc/self/fd/500")`, and kselftest harness.

## Control Flow
Each test opens a tmpfs fs context fd. It then attempts one unsupported operation and asserts the expected errno: `EOPNOTSUPP` for chown/chmod, `EACCES` for exec, and `ENXIO` for reopening through procfd after dup2.

## State And Persistence
Creates anonymous fs context fds only; closes them after each test.

## Dependencies And Integration Points
Requires new mount API support and wrappers from `wrappers.h`.

## Risks
Tests assume procfd number 500 is available for `dup2`. Missing fsopen support fails setup rather than skipping.

## Test Signals
Four kselftest cases pass on exact unsupported-operation errno values.
