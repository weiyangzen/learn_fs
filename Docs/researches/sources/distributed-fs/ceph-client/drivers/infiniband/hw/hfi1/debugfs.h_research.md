# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/debugfs.h

Purpose: debugfs helper interface for HFI1. It provides seq-file boilerplate macros and the public lifecycle hooks used by the driver to create or destroy global and per-device debugfs entries.

Important APIs/types: `DEBUGFS_SEQ_FILE_OPS(name)`, `DEBUGFS_SEQ_FILE_OPEN(name)`, and `DEBUGFS_FILE_OPS(name)` generate `seq_operations`, open helpers that set `seq->private = inode->i_private`, and file operations. Public functions are `hfi1_dbg_ibdev_init()`, `hfi1_dbg_ibdev_exit()`, `hfi1_dbg_init()`, and `hfi1_dbg_exit()`, with no-op inline stubs when `CONFIG_DEBUG_FS` is disabled.

Control flow: implementation files define `_name_seq_start/next/stop/show`, invoke the macros, and pass the generated file ops to `debugfs_create_file()`. The conditional declarations allow callers to invoke debugfs setup unconditionally while build configuration decides whether anything happens.

State and persistence: no state is stored in this header. It standardizes how seq files preserve the HFI1 object pointer passed as `inode->i_private`.

Dependencies and integration: used by `debugfs.c` and `fault.c`. It relies on Linux `seq_file`, `file_operations`, and `THIS_MODULE` symbols being visible through including translation units.

Risks: the macros assume each caller uses the exact `_name_seq_*` naming convention and that `inode->i_private` remains valid for the lifetime of the open file. Any generated file operation has a fixed `seq_release`, so custom private allocations require separate file ops.

Test signals: build with debugfs enabled and disabled, seq-file read smoke tests for each generated file, and device removal while debugfs files are open to catch lifetime issues.
