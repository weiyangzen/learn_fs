<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/cp-library/orangefs-client.c -->
# sources/distributed-fs/orangefs/src/client/cp-library/orangefs-client.c

## Purpose
Implements a Windows-oriented exported C client library wrapping OrangeFS/PVFS system-interface operations for initialization, lookup, creation, removal, rename, attributes, directory listing, I/O, statfs, and credential management.

## Important APIs, Types, And Functions
Exports the functions declared in `orangefs-client.h`: `orangefs_initialize`, `orangefs_lookup`, `orangefs_lookup_follow_links`, `orangefs_get_symlink_attr`, `orangefs_create`, `orangefs_create_h`, `orangefs_remove`, `orangefs_remove_h`, `orangefs_rename`, `orangefs_getattr`, `orangefs_setattr`, `orangefs_mkdir`, `orangefs_io`, `orangefs_flush`, `orangefs_find_files`, `orangefs_get_diskfreespace`, `orangefs_finalize`, credential helpers, and debug helpers. `split_path` is a local path utility. Globals include `mntents`, `tab`, and `MVS_DEBUGGING`.

## Control Flow
Initialization derives a tabfile path relative to the executable, repeatedly initializes PVFS, parses the tab file, and adds the first filesystem until success. Most path operations split parent/name, resolve parents with link-following lookup, then call the matching `PVFS_sys_*` operation. I/O builds contiguous memory requests and calls `PVFS_sys_io`. Directory listing uses `PVFS_sys_readdirplus`, copies names and attributes, follows symlink targets, and releases allocated attr fields.

## State And Persistence
Runtime state includes PVFS system-interface initialization, parsed tabfile data, copied mount entry, debug output sinks, allocated credential group/signature/issuer fields, and output attribute buffers. It writes no local persistent files.

## Dependencies And Integration Points
Depends on Windows APIs for initialization/debug behavior, OrangeFS/PVFS sysint and utility APIs, `gossip`, `pint-util`, `cred.h`, and exported DLL decoration. It bridges external Windows callers to OrangeFS internal C APIs.

## Risks And Test Signals
Risks include unimplemented `orangefs_load_tabfile`, uninitialized `tabfile`/`malloc_flag` paths, incorrect pointer casts such as `(PVFS_fs_id) fs_id` instead of `*fs_id` in handle variants, `orangefs_rename` using uninitialized parent lookup responses, possible attr lifetime bugs after copying and releasing fields, `vsprintf` into fixed buffer, and retry loop without cancellation. Test signals are DLL build, initialization from a tabfile, create/remove/rename/mkdir/io/list/statfs, symlink following, credential group management, debug modes, and negative path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/cp-library/orangefs-client.c -->
