# sources/distributed-fs/ceph-client/fs/lockd/procfs.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/procfs.h` declares optional procfs setup and teardown for lockd, with no-op stubs when procfs is disabled. The source was read as a complete 27-line header.

## Important APIs, Types, and Functions

It exposes `lockd_create_procfs` and `lockd_remove_procfs`. When `CONFIG_PROC_FS` is disabled, inline stubs return success and do nothing.

## Control Flow

There is no direct runtime flow beyond the compile-time branch. Lockd init/exit can call these functions unconditionally.

## State and Persistence Behavior

No state is owned. Real proc entries are created in `procfs.c` only when procfs support is compiled in.

## Dependencies and Integration Points

The header is included by lockd init/exit code to hide `CONFIG_PROC_FS` conditionals from callers.

## Risks and Edge Cases

The no-op create stub returns 0, so callers must not assume proc entries exist in procfs-disabled builds. Prototype drift with `procfs.c` would fail builds.

## Test Signals

Build matrix coverage with `CONFIG_PROC_FS=y` and disabled, plus lockd init/exit smoke tests in both configurations.
