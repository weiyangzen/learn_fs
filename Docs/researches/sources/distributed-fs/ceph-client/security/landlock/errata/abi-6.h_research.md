# sources/distributed-fs/ceph-client/security/landlock/errata/abi-6.h

## Purpose

This ABI errata header documents and registers erratum 2 for Landlock ABI 6: overly restrictive scoped signal handling between threads in the same process.

## Important APIs, Types, and Functions

The file expands `LANDLOCK_ERRATUM(2)` and explains the user-visible effect for multithreaded programs using Landlock thread synchronization.

## Control Flow

Included by `errata.h` with ABI 6, it adds an entry to the boot-time errata table. `setup.c` publishes the corresponding bit when ABI compatibility allows it.

## State and Persistence Behavior

No local runtime state exists. The global errata bitmask records whether the fix is available.

## Dependencies and Integration Points

The fix relates to scoped signal checks in Landlock task/file ownership code, including same-thread-group allowances in `fs.c` and task hooks outside this work item.

## Risks and Test Signals

Without the fix, multithreaded programs that synchronize Landlock policies across existing threads may lose expected intra-process signal behavior. Test `LANDLOCK_SCOPE_SIGNAL`, sibling threads in different domains, `pthread_kill`, async I/O ownership, and ABI errata reporting.
