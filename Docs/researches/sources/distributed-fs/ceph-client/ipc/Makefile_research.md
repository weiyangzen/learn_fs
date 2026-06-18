# sources/distributed-fs/ceph-client/ipc/Makefile

## Purpose

`sources/distributed-fs/ceph-client/ipc/Makefile` selects Linux IPC objects for the kernel build. It maps configuration symbols to System V IPC, POSIX mqueue, IPC namespace, sysctl, and compatibility support. The source was read as a complete 12-line file.

## Important APIs, Types, and Functions

There are no C APIs. Build rules add `compat.o` for `CONFIG_SYSVIPC_COMPAT`; `util.o`, `msgutil.o`, `msg.o`, `sem.o`, `shm.o`, and `syscall.o` for `CONFIG_SYSVIPC`; `ipc_sysctl.o` for `CONFIG_SYSVIPC_SYSCTL`; `mqueue.o` and `msgutil.o` for `CONFIG_POSIX_MQUEUE`; `namespace.o` for `CONFIG_IPC_NS`; and `mq_sysctl.o` for `CONFIG_POSIX_MQUEUE_SYSCTL`.

## Control Flow

Build-time flow is controlled by Kconfig. `msgutil.o` is deliberately shared by System V IPC and POSIX mqueue because it provides common message allocation/copy/free helpers and `init_ipc_ns`/`mq_lock` support for configurations that may compile only one IPC family.

## State and Persistence Behavior

The Makefile owns no runtime state. It determines which object files define IPC namespace state, sysctl registration, message helpers, and syscall entry points.

## Dependencies and Integration Points

This file integrates Kconfig with the IPC source directory. It must remain consistent with exported helpers across `msg.c`, `sem.c`, `shm.c`, `mqueue.c`, `namespace.c`, `ipc_sysctl.c`, and `mq_sysctl.c`.

## Risks and Edge Cases

The main risk is missing shared objects under unusual config combinations, especially `msgutil.o` when POSIX mqueue is enabled without full SysV IPC, or compatibility objects when old multiplexed syscall paths are enabled. Incorrect object selection can appear as link failures or, worse, missing namespace/sysctl initialization in a valid config.

## Test Signals

Build matrix coverage should include SysV IPC only, POSIX mqueue only, both together, IPC namespaces enabled and disabled, sysctl variants, compat syscall variants, and all-disabled configurations.
