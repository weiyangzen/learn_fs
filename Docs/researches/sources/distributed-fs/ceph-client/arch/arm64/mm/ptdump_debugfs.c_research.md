# sources/distributed-fs/ceph-client/arch/arm64/mm/ptdump_debugfs.c

## Purpose
This small file exposes ARM64 page-table dumps through debugfs. It bridges a `seq_file` show callback to the generic ARM64 `ptdump_walk()` implementation.

## Important APIs, Types, and Functions
The important functions are `ptdump_show()` and `ptdump_debugfs_register()`. `DEFINE_SHOW_ATTRIBUTE(ptdump)` creates the debugfs file operations.

## Control Flow
`ptdump_debugfs_register()` creates a read-only debugfs file with mode `0400`, stores the supplied `struct ptdump_info *` as private data, and uses `ptdump_fops`. When read, `ptdump_show()` retrieves that private info and calls `ptdump_walk()`.

## State and Persistence
The debugfs dentry is not stored in this file, but the file persists in debugfs after registration. Runtime state is passed through `seq_file->private`.

## Dependencies and Integration Points
It depends on debugfs, seq_file helpers, and the ARM64 ptdump interface. `ptdump.c` calls `ptdump_debugfs_register()` during device init.

## Risks
This file intentionally has minimal policy. Risks are mostly from debugfs availability and from trusting the lifetime of the supplied `ptdump_info`. Permission `0400` restricts access but does not hide mapping layout from privileged readers.

## Test Signals
With debugfs mounted and ptdump initialized, the registered file should exist and reading it should invoke `ptdump_walk()` without errors.
