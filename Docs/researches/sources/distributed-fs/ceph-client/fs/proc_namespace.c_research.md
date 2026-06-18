# sources/distributed-fs/ceph-client/fs/proc_namespace.c

## Purpose
`proc_namespace.c` implements `/proc/<pid>/mounts`, `/proc/<pid>/mountinfo`, and `/proc/<pid>/mountstats`, formatting a task's mount namespace through seq_file operations.

## Important APIs, types, and functions
Important functions are `mounts_open_common`, `mounts_poll`, `show_vfsmnt`, `show_mountinfo`, `show_vfsstat`, `show_sb_opts`, `show_vfsmnt_opts`, `mangle`, and `mounts_release`. It fills `struct proc_mounts` with a referenced `mnt_namespace`, root path, and selected show callback.

## Control flow
Open resolves the target task, pins its mount namespace and fs root under `task_lock`, opens a private seq_file using `mounts_op`, and records the namespace event counter for polling. Iteration is delegated to mount namespace seq operations; each mount is formatted in legacy mounts, modern mountinfo, or mountstats syntax. Release drops the saved root path and namespace reference.

## State and persistence
The state is a per-open snapshot of task root and namespace reference, while poll observes live namespace event changes through `ns->event` and `ns->poll`. No persistent storage is written.

## Dependencies and integration points
It integrates procfs task lookup, VFS namespace internals, `security_sb_show_options`, superblock show hooks, path escaping, idmapped mount display, propagation tags, and filesystem-specific statistics hooks.

## Risks and test signals
Risks include namespace lifetime races, chroot-relative path hiding via `SEQ_SKIP`, incorrect escaping of mount fields, stale poll events, and discrepancies between mount option sources. Test signals include bind/shared/slave/unbindable mounts, idmapped mounts, chrooted readers, filesystems with custom `show_devname`/`show_options`/`show_stats`, and poll after namespace mutation.
