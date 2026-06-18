# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-debugfs.h

## Purpose

This header declares the UFS debugfs integration points and provides no-op stubs when debugfs is disabled.

## Important APIs, Types, and Functions

It forward-declares `struct ufs_hba` and declares `ufs_debugfs_init()`, `ufs_debugfs_exit()`, `ufs_debugfs_hba_init()`, `ufs_debugfs_hba_exit()`, and `ufs_debugfs_exception_event()`.

## Control Flow

There is no runtime control flow in the header. Compile-time `CONFIG_DEBUG_FS` selects real declarations or inline empty stubs.

## State and Persistence Behavior

The header owns no state. It controls whether callers need conditional compilation around debugfs hooks.

## Dependencies and Integration Points

It integrates `ufshcd.c` and other core code with `ufs-debugfs.c` while preserving clean builds without debugfs.

## Risks and Test Signals

Risks are signature drift between stubs and implementation and callers assuming side effects when debugfs is disabled. Test signals are builds with and without `CONFIG_DEBUG_FS`.
