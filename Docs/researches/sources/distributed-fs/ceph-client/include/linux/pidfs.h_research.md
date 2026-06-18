# sources/distributed-fs/ceph-client/include/linux/pidfs.h

## Purpose
PID filesystem integration API. It associates `struct pid` objects with filesystem dentries/files and supports pidfd allocation plus coredump integration.

## Important APIs, Types, and Functions
Declares `pidfs_alloc_file()`, `pidfs_init()`, `pidfs_prepare_pid()`, `pidfs_add_pid()`, `pidfs_remove_pid()`, `pidfs_exit()`, optional `pidfs_coredump()`, `pidfs_dentry_operations`, `pidfs_register_pid()`, and `pidfs_free_pid()`.

## Control Flow
PID lifecycle code prepares/registers PID filesystem state when PIDs are created, adds/removes them as tasks live and exit, allocates pidfd files for userspace handles, and releases pidfs data when the PID object is freed.

## State and Persistence
Persistent state is stored in `struct pid` fields declared in `pid.h`: inode number, hash node, stashed dentry, and pidfs attributes. The header itself declares operations.

## Dependencies and Integration Points
Integrates PID core, VFS files/dentries, pidfd, task exit, and coredump paths.

## Risks
VFS lifetime and PID lifetime must be synchronized to avoid stale dentries or leaked pidfs attributes. Coredump hooks must not outlive task/PID state.

## Test Signals
Pidfd creation tests, `/proc` or pidfs lookup tests where applicable, task exit cleanup tests, coredump path tests, and filesystem lifetime leak checks.
