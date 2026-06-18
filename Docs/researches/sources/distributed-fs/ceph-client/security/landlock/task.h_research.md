<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/task.h -->
# sources/distributed-fs/ceph-client/security/landlock/task.h

## Purpose

`task.h` is the small internal declaration header for Landlock task-related hooks. It exposes only the initialization entry point needed by Landlock setup code.

## Important APIs, Types, and Functions

- `landlock_add_task_hooks()` is declared as an `__init` function. Its implementation in `task.c` registers Landlock ptrace, Unix socket, signal, and file-owner signal hooks.

## Control Flow

The header itself has no runtime control flow. During Landlock initialization, setup code includes this header and calls `landlock_add_task_hooks()`, which installs the task hook list into the LSM framework.

## State and Persistence Behavior

No state is defined here. Hook registration state is owned by the LSM core after `security_add_hooks()` runs in `task.c`.

## Dependencies and Integration Points

The header is guarded by `_SECURITY_LANDLOCK_TASK_H` and is consumed by Landlock initialization code. It intentionally avoids pulling in heavier task or socket headers.

## Risks and Edge Cases

The main risk is interface drift: if the hook registration implementation changes signature or init ordering, this declaration and callers must be updated together. Because it is an internal header, ABI stability is not a concern.

## Test Signals

Build coverage is the relevant signal. Runtime coverage comes indirectly from tests that confirm Landlock task hooks are present after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/task.h -->
