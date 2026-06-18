# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fcntl.c

## Purpose
This formatter improves `fcntl` tracing by decoding command values, formatting the third argument according to the command, setting return-value formatters, and masking ignored arguments.

## Important APIs, Types, And Functions
Important helpers are `fcntl__scnprintf_getfd()`, `syscall_arg__scnprintf_fcntl_getfd()`, `fcntl__scnprintf_getlease()`, `syscall_arg__scnprintf_fcntl_getlease()`, `syscall_arg__scnprintf_fcntl_cmd()`, and `syscall_arg__scnprintf_fcntl_arg()`. It uses `F_GETFL`, `F_GETFD`, `F_DUPFD_CLOEXEC`, `F_DUPFD`, `F_GETOWN`, `F_GETLEASE`, `F_GET_SEALS`, `F_GETSIG`, `F_SETFD`, `F_SETFL`, `F_SETOWN`, `F_SETLEASE`, lock commands, RW hint commands, and helpers such as `open__scnprintf_flags()` and `syscall_arg__set_ret_scnprintf()`.

## Control Flow
When formatting the command argument, the code installs specialized return-value formatters for commands whose return value is flags, fd flags, fd, pid, or lease type. It masks the third argument for commands that ignore it. When formatting the third argument, it switches on the previously captured command and chooses fd, fd flags, open flags, pid, lease, pointer-as-hex, or long formatting.

## State, Dependencies, And Integration
Runtime state changes occur through `arg->mask` and return-format callback installation. It depends on `linux/fcntl.h` and `beauty.h`. `builtin-trace.c` supplies the fcntl command strarrays and hooks these formatters into syscall metadata.

## Risks And Test Signals
Command coverage must track kernel UAPI. Incorrect mask behavior can hide useful arguments or show meaningless ones. Tests should cover representative get/set/dup/lock commands and return-value formatting.
