# sources/distributed-fs/ceph-client/arch/sh/kernel/kdebugfs.c

Purpose: creates the architecture debugfs root directory for SH.

Important APIs and control flow: global `arch_debugfs_dir` is exported for other SH code to place debugfs entries under. `arch_kdebugfs_init()` calls `debugfs_create_dir("sh", NULL)` and stores the returned dentry. The initializer runs through `arch_initcall()`.

State, dependencies, and risks: persistent state is the exported `arch_debugfs_dir` pointer. Dependencies include debugfs availability and initcall ordering relative to users that create child entries. The code does not check for `ERR_PTR` or NULL, so child users must tolerate unavailable debugfs. Test signals are `/sys/kernel/debug/sh` presence when debugfs is mounted and module/built-in users successfully creating child files.
