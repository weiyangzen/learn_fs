<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-remove-object.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-remove-object.c

**Purpose:** `pvfs2-remove-object` is a low-level administrative removal tool. It can delete a raw object by `fsid,handle` or delete a directory entry by parent handle plus dirent name. It bypasses normal pathname-level semantics and is intended for repair/cleanup workflows.

**Important APIs, types, and functions:** `options_t` records operation mode, object handle, parent handle, fsid, and dirent name. `parse_args()` handles short and long options for `--object`, `--parent`, `--dirent`, and `--fsid`. `main()` builds a `PVFS_object_ref`, initializes PVFS defaults, generates credentials, then calls either `PVFS_mgmt_remove_object` or `PVFS_mgmt_remove_dirent`.

**Control flow:** The parser accepts independent options and relies on `main()` validation to require fsid and either object handle or parent plus dirent. Object-only mode is selected by `-o`; otherwise the tool expects `-p` and `-d`. After validation, it initializes the system, creates credentials, logs the attempted destructive action, performs the management removal, prints PVFS errors if needed, frees options, and returns the PVFS result.

**State and persistence:** This tool permanently mutates OrangeFS metadata/storage by removing an object or directory entry. Removing an object alone can orphan namespace entries; removing a dirent alone can strand the target object. It does not call `PVFS_sys_finalize`, so process teardown must clean up sysint state.

**Dependencies and integration points:** It depends on `pvfs2-mgmt.h` administrative APIs, normal PVFS credential defaults, numeric handle/fsid knowledge from another diagnostic tool, and server-side management authority.

**Risks and edge cases:** There is no confirmation prompt, no path-based safety, no cross-check that a parent contains the requested object, and no repair sequencing. `strtoull` errors are not checked, so malformed numbers can become null/zero handles. Tests should cover object-only removal, dirent-only removal, invalid fsid/handle validation, missing dirent names, long dirent truncation, and expected behavior when server permissions reject management removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-remove-object.c -->
