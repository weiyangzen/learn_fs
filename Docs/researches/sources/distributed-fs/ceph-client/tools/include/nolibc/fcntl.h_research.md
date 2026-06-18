# sources/distributed-fs/ceph-client/tools/include/nolibc/fcntl.h

## Purpose
Provides nolibc file-open wrappers and fcntl/open constants from Linux UAPI.

## APIs, Types, and Functions
Defines `_sys_openat`, `openat`, `_sys_open`, and `open`, with varargs mode handling for creation flags. It includes `<linux/fcntl.h>` for flag definitions.

## Control Flow, State, and Persistence
`openat()` and `open()` pick up an optional `mode_t` vararg when needed, issue `openat` or legacy `open` syscalls depending on availability, and return through `__sysret`. No state is persisted except kernel file descriptors returned to callers.

## Dependencies and Integration
Depends on `arch.h`, `stdarg.h`, `types.h`, and syscall numbers. It integrates with `stdio.h`, `dirent.h`, and general filesystem access in nolibc tools.

## Risks and Test Signals
Risks are varargs misuse when creation flags are present, missing legacy syscalls on modern architectures, and fd leaks in callers. Test signals are open/openat success and permission failures, mode creation tests, `O_CLOEXEC` behavior, and architecture builds with only `openat`.
