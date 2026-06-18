# sources/distributed-fs/ceph-client/fs/filesystems.c

## Purpose

`sources/distributed-fs/ceph-client/fs/filesystems.c` maintains the kernel registry of filesystem drivers. It supports registration/unregistration, module reference acquisition, legacy `sysfs(2)` filesystem queries, `/proc/filesystems`, block-device filesystem name listing, and module autoload through `get_fs_type()`. The complete 295-line file was read for this report.

## Important APIs, Types, and Functions

Exported APIs are `register_filesystem()`, `unregister_filesystem()`, and `get_fs_type()`, with `get_filesystem()` and `put_filesystem()` managing module refs. Internal helpers include `find_filesystem()`, `__get_fs_type()`, legacy `fs_index()`, `fs_name()`, `fs_maxindex()`, `list_bdev_fs_names()`, and `filesystems_proc_show()`.

## Control Flow

Filesystem registration validates parameter descriptions, rejects names containing `.`, prevents double-linking, and inserts into the global singly linked list under `file_systems_lock`. Unregistration removes the exact object, clears `next`, then waits for RCU readers. Lookup parses optional subtype suffixes, tries the current registry under read lock with `try_module_get()`, calls `request_module("fs-%.*s")` if missing, and rejects subtype use unless `FS_HAS_SUBTYPE` is set.

## State and Persistence Behavior

The only persistent runtime state is the global `file_systems` list protected by `file_systems_lock`. Registry contents last until module unload or built-in lifetime. `/proc/filesystems` and legacy syscall output are live views of that list.

## Dependencies and Integration Points

This file integrates with module ownership, `fs_parser` parameter validation, `/proc`, seq_file, kernel module autoloading, the mount path's filesystem type lookup, and init-time block filesystem enumeration.

## Risks and Edge Cases

Risks include module reference handling while walking the registry, duplicate registrations, subtype parsing mistakes, `/proc/filesystems` racing with unregister, and stale success from `request_module()` that still leaves no registered filesystem. Registration forbids names with dots because dot suffixes represent subtypes.

## Test Signals

Coverage should include module filesystem load/unload, duplicate registration failure, subtype mount behavior, `/proc/filesystems` output, `sysfs(2)` if configured, autoload success/failure, and lockdep/KCSAN around concurrent mount lookup and unregister.
