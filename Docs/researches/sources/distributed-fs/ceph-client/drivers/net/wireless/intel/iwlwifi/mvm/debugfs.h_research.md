# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/debugfs.h

## Purpose

Provides macro helpers for defining MVM debugfs file operations with typed private data and bounded text write buffers.

## Important APIs, Types, and Functions

`MVM_DEBUGFS_READ_FILE_OPS(name)` creates read-only ops. `MVM_DEBUGFS_WRITE_WRAPPER(name, buflen, argtype)` generates a userspace-copying write wrapper that casts `file->private_data` to `argtype *`. `_MVM_DEBUGFS_READ_WRITE_FILE_OPS()` and `_MVM_DEBUGFS_WRITE_FILE_OPS()` compose read/write or write-only operation tables.

## Control Flow

Implementation files bind wrapper aliases to a private-data type such as `struct iwl_mvm` or `struct ieee80211_vif`. On write, the generated wrapper copies at most `buflen - 1` bytes into a zeroed stack buffer and dispatches to `iwl_dbgfs_<name>_write()`.

## State and Persistence Behavior

No state is stored. The macros define how much input reaches handlers and how debugfs private data is interpreted.

## Dependencies and Integration Points

Depends on Linux `file_operations`, `copy_from_user()`, `simple_open`, and `generic_file_llseek`. Used by `debugfs.c` and `debugfs-vif.c`.

## Risks

Handler names/signatures must match macro expansion. Input truncation is intentional but handlers must treat it as bounded. Debugfs file creation must pass private data matching the wrapper type.

## Test Signals

Compile coverage catches macro signature drift. Runtime tests should verify NUL-terminated bounded writes, `-EFAULT` on bad user pointers, and correct private-data types per file.
