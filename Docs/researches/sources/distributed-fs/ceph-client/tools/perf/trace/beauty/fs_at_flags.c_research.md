# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fs_at_flags.c

## Purpose
This formatter decodes `AT_*` flags for filesystem syscalls and special-cases `faccessat2` where `AT_EACCESS` reuses a value that can mean something else in other contexts.

## Important APIs, Types, And Functions
It includes generated `fs_at_flags_array.c`, defines `strarray__fs_at_flags`, and implements `syscall_arg__scnprintf_fs_at_flags()` plus `syscall_arg__scnprintf_faccessat2_flags()`. It defines `AT_EACCESS` fallback value `0x200` for older headers.

## Control Flow
Generic `fs_at` formatting delegates to `strarray__scnprintf_flags()`. `faccessat2__scnprintf_flags()` first detects `AT_EACCESS`, emits `EACCESS` with optional `AT_` prefix, clears the bit, then appends any remaining flags through the generated strarray formatter.

## State, Dependencies, And Integration
No state is persisted. The generated array is built by `fs_at_flags.sh`. The functions are exposed through `SCA_FS_AT_FLAGS` and `SCA_FACCESSAT2_FLAGS` in `beauty.h`.

## Risks And Test Signals
Several `AT_*` values are context-specific aliases; using the generic formatter in the wrong syscall can produce misleading names. Tests should cover `AT_EACCESS` for faccessat2 and common directory/symlink/stat flags for generic filesystem syscalls.
