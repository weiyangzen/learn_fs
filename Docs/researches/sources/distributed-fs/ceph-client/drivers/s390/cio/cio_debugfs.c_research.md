# sources/distributed-fs/ceph-client/drivers/s390/cio/cio_debugfs.c

## Purpose
This small file creates the shared CIO debugfs directory used by optional CIO debugging interfaces.

## Important APIs, Types, and Functions
It defines global `struct dentry *cio_debugfs_dir` and `cio_debugfs_init()`, which calls `debugfs_create_dir("cio", arch_debugfs_dir)` during `subsys_initcall`.

## Control Flow
At subsystem init time, the file creates `/sys/kernel/debug/s390/cio` under the architecture debugfs directory and returns success. Other files can then create files below `cio_debugfs_dir`.

## State and Persistence
The only state is the debugfs dentry pointer. Debugfs entries are runtime-only and disappear at unmount/reboot.

## Dependencies and Integration Points
It depends on Linux debugfs and `cio_debug.h`. `cio_inject.c` uses this directory for `enable_inject` and `crw_inject`.

## Risks and Test Signals
Risk areas include debugfs being unavailable or `arch_debugfs_dir` not initialized as expected; the function does not check for an error dentry. Test signals are the presence of `/sys/kernel/debug/s390/cio`, successful creation of child debugfs files, and boot ordering relative to `cio_inject_init()`.
