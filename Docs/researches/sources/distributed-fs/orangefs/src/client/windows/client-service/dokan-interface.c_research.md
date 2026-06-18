# sources/distributed-fs/orangefs/src/client/windows/client-service/dokan-interface.c

## Purpose
This file is the Windows Dokan bridge for OrangeFS. It registers Dokan filesystem callbacks, converts Windows paths/attributes/security requests to OrangeFS operations, maps errors, resolves per-request credentials, caches open-context credentials/object references, and starts the long-running Dokan mount loop.

## Important APIs, types, and functions
- Debug/error helpers: `client_debug`, `error_map`.
- Encoding/path helpers: `convert_wstring`, `convert_mbstring`, `get_fs_path`, `convert_pvfstime`, `convert_filetime`.
- Credential path: `get_requestor_credential`, `get_credential`, `add_context`, `get_context_entry`, `remove_context`, `cred_compare`.
- Permission helpers: `check_perm`, `check_create_perm`, `PVFS_sys_attr_to_file_info`.
- Dokan callbacks: `PVFS_Dokan_create_file`, `create_directory`, `open_directory`, `close_file`, `cleanup`, `read_file`, `write_file`, `flush_file_buffers`, `get_file_information`, `set_file_attributes`, `find_files_with_pattern`, `delete_file`, `delete_directory`, `move_file`, `lock_file`, `set_end_of_file`, `set_allocation_size`, `set_file_time`, security callbacks, `unmount`, `get_disk_free_space`, `get_volume_information`.
- Entrypoint: `dokan_loop` builds `DOKAN_OPTIONS`/`DOKAN_OPERATIONS` and repeatedly calls `DokanMain`.

## Control flow
`dokan_loop` initializes a qhash context cache and mutex, maps service debug settings into global flags and Dokan options, converts the mount point, assigns callbacks, and enters a retry loop around `DokanMain`, sleeping 30 seconds after each exit.

For each filesystem callback, paths are converted from wide chars to multibyte and resolved through `fs_resolve_path`. Credentials are fetched either from `DokanFileInfo->Context` via `context_cache` or from the requestor token with `DokanOpenRequestorToken`. Cache misses are resolved through list-mode user cache, proxy certificate mode, LDAP mode, server/user certificate mode, or system credentials. Open/create callbacks generate a unique context and cache a copied credential. Close removes context and applies delete-on-close removal.

Read/write use an IO cache when enabled: the first operation resolves object refs with `fs_lookup`, then subsequent operations use `fs_read2`/`fs_write2` by object ref. Attribute and directory callbacks translate PVFS attributes to Windows `BY_HANDLE_FILE_INFORMATION`/`WIN32_FIND_DATAW`. Delete operations only validate lookup and defer actual removal to close. Move maps to `fs_rename`; allocation size maps to `fs_truncate`; set-file-time maps FILETIME values into PVFS setattr masks.

## State and persistence behavior
Persistent state is the mounted OrangeFS namespace. Runtime state includes global debug flags, global `goptions`, `context_cache` keyed by Dokan context ids with copied credentials and open flags, optional IO cache entries keyed by context, and the Dokan mount loop. File metadata changes persist through `fs_setattr`, writes persist through `fs_write2`/`fs_write`, deletes through `fs_remove`, and renames through `fs_rename`.

## Dependencies and integration points
The file integrates Dokan 0.6-style APIs, Windows token/SID/security APIs, OrangeFS/PVFS2 filesystem wrapper functions from `fs.h`, credential/cert/user-cache/LDAP helpers, quickhash/gen-locks, gossip debug logging, and IO cache support. It is the primary consumer of `ORANGEFS_OPTIONS` produced by `config.c`.

## Risks and edge cases
- `dokan_loop` retries forever and cleanup code after the loop is unreachable under normal operation.
- Context ids from `QueryPerformanceCounter` can collide in theory and are not checked for existing qhash entries.
- `get_requestor_credential` calls `CloseHandle(htoken)` even after the no-requestor branch may leave `htoken` invalid or uninitialized in some paths.
- `PVFS_Dokan_delete_directory` calls `add_context` before `PVFS_Dokan_delete_file`, while `DokanFileInfo->Context` may be zero; qhashing context zero can collide with other uninitialized contexts.
- Permission checks are client-side approximations and server mode intentionally returns permission if any class has the bit, relying on server enforcement.
- `PVFS_Dokan_set_end_of_file` returns success without truncating; Windows callers may expect EOF changes to persist.
- `PVFS_Dokan_move_file` ignores `ReplaceIfExisting`.
- `PVFS_Dokan_get_file_security` is marked crash-prone and not registered for get, while set security is a no-op success.
- Several buffer copies use `wcscpy`/`wcsncpy` without checking destination sizes from Dokan buffers.
- IO cache cleanup/update code in `PVFS_Dokan_cleanup` is disabled, so cached IO entries may rely on external cleanup behavior and access times may not update on reads.

## Test signals
Run Dokan mount smoke tests for create/open/read/write/flush/close/delete, delete-on-close for files and directories, rename with existing target and `ReplaceIfExisting`, set allocation and EOF semantics, directory listing with wildcard patterns and more than 60 entries, permission-denied cases for owner/group/other, credential cache hit/miss across Windows users, service startup before network availability, and forced `DokanMain` failures to observe retry behavior.
