# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/wait-pipe-sandbox.c

## Purpose

`wait-pipe-sandbox.c` is a synchronized helper for Landlock audit-exec tests. It waits with a parent, verifies inherited signal scoping, adds additional filesystem and signal-scoped Landlock layers, and verifies each layer blocks the expected operation.

## Important APIs, Types, and Functions

It uses `sync_with()` for one-byte pipe handshakes, `landlock_create_ruleset()`, `landlock_restrict_self()`, `kill(getppid(), 0)`, `open("/")`, `close()`, and `atoi()`. `wrappers.h` supplies direct Landlock syscalls.

## Control Flow and State

The program expects child and parent pipe FDs. It first synchronizes and checks a parent-provided layer blocks signaling the parent, then synchronizes again, adds a filesystem `READ_DIR` handling layer that denies opening `/`, synchronizes a third time, adds `LANDLOCK_SCOPE_SIGNAL`, and checks both filesystem and signal denials. The persistent state is the process's accumulated Landlock layers.

## Dependencies and Integration Points

It depends on the parent test having already set `PR_SET_NO_NEW_PRIVS`, inherited pipe descriptors, Landlock filesystem and signal-scope support, and audit tests that observe behavior across exec.

## Risks and Test Signals

Risks are desynchronization, wrong inherited no-new-privs assumptions, or adding layers in the wrong order. Signals are nonzero exit on any unexpected successful `kill()` or `open("/")`, plus stderr messages identifying the violated restriction.
