# sources/distributed-fs/ceph-client/fs/notify/fdinfo.h

## Purpose

`fdinfo.h` is the small declaration gate for fsnotify fdinfo support. It exposes fanotify and inotify fdinfo hooks to their file operation tables when procfs support is enabled and provides `NULL` fallbacks when procfs is disabled.

## Important APIs, Types, and Functions

The header declares `inotify_show_fdinfo(struct seq_file *, struct file *)` under `CONFIG_INOTIFY_USER` and `fanotify_show_fdinfo(struct seq_file *, struct file *)` under `CONFIG_FANOTIFY`. Without `CONFIG_PROC_FS`, both names are defined as `NULL` so file operation initializers remain simple.

## Control Flow

There is no executable control flow. Preprocessor branches select declarations or null constants based on build configuration.

## State and Persistence Behavior

The file owns no state and only controls compile-time linkage of procfs diagnostics.

## Dependencies and Integration Points

It depends on `linux/proc_fs.h` and forward declarations of `seq_file` and `file`. It integrates with `inotify_user.c` and `fanotify_user.c` file operation tables, and with `fdinfo.c` for the actual implementations.

## Risks and Edge Cases

The main risk is build-configuration mismatch: references to fdinfo functions must disappear cleanly when procfs or either notifier is disabled. The `NULL` fallback is intentional for file operations that accept a missing fdinfo hook.

## Test Signals

Kernel build coverage with `CONFIG_PROC_FS` on and off, and with inotify/fanotify individually enabled or disabled, is the primary signal. Runtime fdinfo tests only apply when procfs and the relevant notifier are enabled.
