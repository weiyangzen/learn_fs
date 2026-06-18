# sources/distributed-fs/ceph-client/include/trace/misc/fs.h

Purpose: Provides reusable filesystem trace formatting helpers for dirent types, open flags, file modes, fcntl commands, lock types, lookup flags, inode attribute-valid flags, and statx masks.

Important APIs/types/functions: Defines `show_fs_dirent_type`, `show_fs_fcntl_open_flags`, `show_fs_fmode_flags`, `show_fs_fcntl_cmd`, `show_fs_fcntl_lock_type`, `show_fs_lookup_flags`, `show_ia_valid_flags`, and `show_statx_mask`. It uses `TRACE_DEFINE_ENUM` and `__print_flags`/`__print_symbolic` style mappings.

Control flow: Trace event headers include this misc helper and use the macros in `TP_printk` expressions. There is no runtime control flow beyond macro expansion into trace formatters.

State/persistence: No state is stored; it defines symbolic presentation for values captured by other events.

Dependencies/integration: Depends on VFS constants from fs/fcntl/stat headers and trace formatting macros. Used across filesystem trace systems to avoid duplicated flag maps.

Risks: These helpers form user-visible string decoding. Missing new flags or stale command values produce misleading traces even when raw values are correct.

Test signals: Build all filesystem trace users and inspect trace format files for complete flag mappings; exercise open/fcntl/lookup/statx traces.
