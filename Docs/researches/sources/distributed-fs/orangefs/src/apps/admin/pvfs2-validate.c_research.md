<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-validate.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-validate.c

**Purpose:** `pvfs2-validate` is a client-side recursive filesystem validation tool built on fsck utility helpers. It checks object attributes, directories, symlinks, optional server config consistency, stranded objects, symlink targets, and directory-entry naming policy.

**Important APIs, types, and functions:** `parse_args()` fills `struct PINT_fsck_options`. `main()` resolves the start path, validates `-c` root requirements, creates credentials, looks up the start object, calls `PVFS_fsck_initialize`, `PVFS_fsck_check_server_configs`, and eventually `PVFS_fsck_finalize`. `validate_pvfs_object()` dispatches by `PVFS_TYPE_METAFILE`, `PVFS_TYPE_DIRECTORY`, or `PVFS_TYPE_SYMLINK`, using `PVFS_fsck_get_attributes`, `PVFS_fsck_validate_metafile`, `PVFS_fsck_validate_dir`, and `PVFS_fsck_validate_symlink`.

**Control flow:** The tool requires `-d`. It normalizes a trailing slash, initializes PVFS, resolves the target, treats an empty resolved path as `/`, validates option combinations, looks up the start object without following links, initializes fsck state, checks server configs, optionally exits after `-F`, then recursively validates. Directory validation allocates an array sized by `dirent_count`, lets the helper fill it, and recurses into each entry.

**State and persistence:** In the current implementation repair flags are not implemented, so validation is primarily read-only. Fsck helper initialization/finalization may set operational state, but this file does not directly repair objects.

**Dependencies and integration points:** It depends heavily on `fsck-utils.h` and related helper implementations, PVFS sysint, server config consistency checks, and credentials. It should be run when servers are up and clients are quiet per file comments.

**Risks and edge cases:** `validate_pvfs_object()` always returns 0 after reporting errors, so `main()` can report success despite invalid objects. `char new_path[PVFS_SEGMENT_MAX]` can overflow when building recursive full paths. It does not call `PVFS_fsck_finalize` on the `-F` early success path. Directory recursion has no cycle/depth guard. Tests should cover invalid metafiles, bad directories, symlinks, stranded-object root enforcement, server config mismatch, deep paths, and expected nonzero exit behavior if corrected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-validate.c -->
