# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/fcntl.h

## Purpose

`fcntl.h` mirrors Linux-specific file-control and `*at(2)` constants used by `fcntl`, open/stat/unlink/rename/name-handle APIs, pidfd/nsfs helpers, and directory notifications. Perf trace beauty uses it to print commands, seals, write-life hints, directory notify masks, special fd constants, and `AT_*` path flags.

## Important APIs, Types, and Constants

The header includes `<asm/fcntl.h>`, `<linux/openat2.h>`, and `<linux/types.h>`. It defines Linux-specific `fcntl` commands from `F_LINUX_SPECIFIC_BASE`, including leases, `F_NOTIFY`, fd duplication queries, created queries, cancel-lock, close-on-exec duplication, pipe sizing, seals, write-life hints, and delegations. It defines seal flags, `RWH_WRITE_LIFE_*` values plus `RWF_WRITE_LIFE_NOT_SET`, `struct delegation`, `DN_*` dnotify masks, `AT_FDCWD`, pidfd self constants, pidfs/nsfs root fd selectors, `FD_INVALID`, generic `AT_*` flags, statx sync flags, recursive flags, rename flags, and syscall-specific overlapping flags such as `AT_EACCESS`, `AT_REMOVEDIR`, and `AT_HANDLE_FID`.

## Control Flow and Integration

Runtime behavior depends on syscall context. `fcntl(fd, cmd, arg)` interprets `arg` according to `cmd`; `F_NOTIFY` uses `DN_*` masks; and `openat`, `statx`, `unlinkat`, `renameat2`, `name_to_handle_at`, `faccessat`, and exec-check calls use `AT_*` flags. Perf trace must decode overlapping constants by syscall, not by a single global table.

## State and Persistence Behavior

Leases, pipe sizes, seals, write-life hints, and delegations can persist on an open file description, inode, memfd, pipe, or filesystem object depending on command. Dnotify state persists on an fd. `AT_*` flags are per-call selectors. Special fd constants select implicit kernel objects.

## Dependencies and Integration Points

The important dependency is `F_LINUX_SPECIFIC_BASE` from `asm/fcntl.h`. The file integrates with VFS locking, memfd sealing, pipes, dnotify, pidfs, nsfs, statx, openat2 path resolution, and file-handle syscalls. Perf uses it for `fcntl` and `*at` syscall flag decoding.

## Risks

Per-syscall `AT_*` flags intentionally overlap numerically, so generic decoders can print misleading names. Seal and hint values are ABI. `FD_INVALID` and other negative fd selectors must not be collapsed into `AT_FDCWD`. `struct delegation` contains MBZ fields that should be visible but not overinterpreted.

## Test Signals

Decode leases, pipe sizing, seals, write-life hints, `F_NOTIFY` masks, and special fd constants. Verify `0x200` prints as `AT_EACCESS`, `AT_REMOVEDIR`, or `AT_HANDLE_FID` depending on syscall.
