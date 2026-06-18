<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-touch.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-touch.c

**Purpose:** `pvfs2-touch` creates one or more empty OrangeFS files, with optional random or explicit datafile-server layout.

**Important APIs, types, and functions:** `struct options` stores random/list layout flags and filenames. `main()` builds a `PVFS_sys_layout`, resolves each target path with `PVFS_util_resolve`, gets parent directory and filename via PINT string helpers, creates credentials, looks up parent with `PVFS_sys_lookup`, constructs `PVFS_sys_attr`, optionally resolves comma-separated server addresses using `BMI_addr_lookup`, and calls `PVFS_sys_create`.

**Control flow:** After parsing, PVFS is initialized once. For each file the layout is reset, target is resolved, parent and basename are derived, credentials and attributes are built, and create is attempted. `-r` selects `PVFS_SYS_LAYOUT_RANDOM`; `-l` mutates the server list string with `strtok`, resolves addresses, and selects `PVFS_SYS_LAYOUT_LIST`.

**State and persistence:** It creates persistent files and metadata in OrangeFS. It can influence datafile placement through layout. It does not update timestamps on existing files like POSIX `touch`; existing target behavior depends on `PVFS_sys_create`.

**Dependencies and integration points:** It depends on sysint create, PINT path helpers, BMI address lookup, PVFS credential defaults, umask translation, and server layout support.

**Risks and edge cases:** Credentials are regenerated per file. A failure breaks out and leaves already-created files. `strtok` destructively modifies `server_list`, so multiple file creation with `-l` can fail after the first iteration. The basename is derived from the user path rather than the resolved PVFS path. Tests should cover multiple files, existing targets, root-directory targets, random/list layout, invalid server addresses, and cleanup after partial creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-touch.c -->
