# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-fs-dump.c

## Purpose
`pvfs2-fs-dump.c` is a filesystem inspection utility. It puts OrangeFS servers into admin mode, enumerates all in-use handles, traverses the directory tree from `/`, verifies that directory data handles and metafile datafiles exist in the handle list, prints either text or Graphviz dot output, reports remaining handles, and restores normal server mode.

## Important APIs, Types, And Functions
Important functions are `main`, `build_handlelist`, `traverse_directory_tree`, `descend`, `verify_dirdatahandles`, `verify_datafiles`, `analyze_remaining_handles`, handle-list helpers, print helpers, `parse_args`, and `get_type_str`. It uses `PVFS_mgmt_count_servers`, `PVFS_mgmt_get_server_array`, `PVFS_mgmt_setparam_list`, `PVFS_mgmt_statfs_list`, `PVFS_mgmt_iterate_handles_list`, `PINT_cached_config_map_to_server`, `PVFS_sys_lookup`, `PVFS_sys_getattr`, `PVFS_sys_readdir`, `PVFS_mgmt_get_dirdata_array`, and `PVFS_mgmt_get_dfile_array`.

## Control Flow
`main` parses `-m`, `-d`, `-k`, `-f`, and `-v`, initializes PVFS, resolves the mount, gets credentials and server addresses, switches IO/meta servers to admin mode, builds the global handle list from server stats and batched handle iteration, emits a header, traverses the tree, analyzes leftover handles, emits a trailer, finalizes the handle list, restores normal mode, and finalizes PVFS. Directory traversal looks up root, validates it as a directory, prints/removes it from the handle list, verifies root dirdata, recursively reads directory entries, prints each object, verifies file datafiles or nested dirdata, and removes seen handles from the list. Leftover analysis classifies remaining handles as internal, preallocated data/metafiles, unknown, or all-accounted-for.

## State And Persistence
The intended persistent filesystem state is read-only, but server operational mode is changed to admin and then back to normal. Runtime state is a module-global handle list split by server, parsed output options, credentials, and server address arrays. `handlelist_finalize` is empty in this implementation, so the handle-list memory is not freed.

## Dependencies And Integration Points
It is tightly integrated with OrangeFS management APIs, cached configuration handle-to-server mapping, sysint directory traversal, and server admin mode semantics. Dot output integrates with Graphviz for visual inspection.

## Risks And Test Signals
Risks include leaving servers in admin mode on unexpected assertion/exit paths, heavy use of `assert(0)` for runtime filesystem inconsistencies, O(n) handle lookup/removal, memory leaks, possible incorrect `calloc(server_count, sizeof(PVFS_handle))` for pointer arrays, and incomplete cleanup on errors. Tests should run against a small known filesystem, verify text and dot output, inject missing datafile/dirdata scenarios if possible, check normal-mode restoration after failures, and compare handle counts to server stats.
