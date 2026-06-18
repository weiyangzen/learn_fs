<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/tsync.h -->
# sources/distributed-fs/ceph-client/security/landlock/tsync.h

## Purpose

`tsync.h` declares Landlock's internal thread-synchronization entry point used when userspace requests `LANDLOCK_RESTRICT_SELF_TSYNC`.

## Important APIs, Types, and Functions

- `landlock_restrict_sibling_threads(const struct cred *old_cred, const struct cred *new_cred)` synchronizes the prepared Landlock credential update to sibling threads and returns `0`, a restart code, or another negative errno.

## Control Flow

The header has no runtime flow. It connects `syscalls.c`, which owns the user-facing restrict-self operation, to `tsync.c`, which owns the task-work synchronization algorithm.

## State and Persistence Behavior

No state is declared here. The credential pointers passed through the function are managed by the caller and by the implementation's task-work protocol.

## Dependencies and Integration Points

It includes `<linux/cred.h>` for `struct cred`. Any Landlock file wanting TSYNC behavior should use this declaration rather than duplicating internals from `tsync.c`.

## Risks and Edge Cases

The function contract is narrow: callers must pass the current old credentials and an uncommitted prepared credential. Passing already-committed or unrelated credentials would break the implementation's optimization and safety assumptions.

## Test Signals

Build coverage plus `landlock_restrict_self(..., LANDLOCK_RESTRICT_SELF_TSYNC)` runtime tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/tsync.h -->
