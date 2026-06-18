<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-xattr.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-xattr.c

**Purpose:** `pvfs2-xattr` gets or sets extended attributes on OrangeFS or Unix files, with special handling for OrangeFS meta hints and mirroring attributes.

**Important APIs, types, and functions:** `struct options` stores key/value arrays, source file, get/set mode, text output, and key count. `file_object` abstracts Unix and PVFS2 targets. `parse_args()` builds `PVFS_ds_keyval` arrays and allocates value buffers. `permit_set()` blocks writes to `system.`, `trusted.`, and `security.` namespaces. `modify_val()` translates textual meta-hint operations such as `+immutable`, `-append`, and `=noatime` into flag bits. `pvfs2_eattr()` dispatches to `fgetxattr`/`fsetxattr`, `PVFS_sys_geteattr`, `PVFS_sys_geteattr_list`, or `PVFS_sys_seteattr`.

**Control flow:** `main()` parses options, initializes PVFS, resolves/open the target, verifies a namespace prefix, optionally fetches current meta-hint value before setting, checks set permission, modifies special values, performs the xattr operation, and formats text output for meta hints, mirror handles/copies/status/mode, or generic key/value strings.

**State and persistence:** Get mode is read-only. Set mode persists xattrs and can change file flags or mirroring policy. For `user.pvfs2.meta_hint`, the program merges changes into current flags while preserving non-user-settable mirror flags.

**Dependencies and integration points:** It depends on Unix xattr APIs, PVFS sysint eattr calls, xattr key constants, `pvfs2-mirror.h` modes, `PINT_statfs_fd_lookup`, and PVFS metadata attributes.

**Risks and edge cases:** `parse_args()` assumes `-k` appears before numeric `-v` for mirror keys. `PVFS_sys_geteattr_list` response allocations are not freed. Unix set opens files read-only, so `fsetxattr` may fail depending on platform permissions. Text output can treat binary values as strings. Tests should cover each namespace, meta-hint mutations, mirror mode/copies validation, handle/status list reads, Unix fallback, missing xattrs, and option ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-xattr.c -->
