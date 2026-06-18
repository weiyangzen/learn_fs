# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-ln.c

Purpose: `pvfs2-ln.c` implements symlink creation for OrangeFS paths. Hard links are explicitly unsupported; callers must pass `-s`.

Important APIs, types, and functions: `struct options` stores link target, link name, and verbosity. The main operations use `PVFS_util_init_defaults`, `PVFS_util_resolve`, `PVFS_util_gen_credential_defaults`, `PINT_remove_base_dir`, `PINT_lookup_parent`, and `PVFS_sys_symlink`. OrangeFS types include `PVFS_credential`, `PVFS_fs_id`, `PVFS_sys_attr`, `PVFS_object_ref`, and `PVFS_sysresp_symlink`.

Control flow: `parse_args` accepts `-s`, `-V`/`--verbose`, `-v`/`--version`, and help. It rejects calls without `-s` or without exactly `TARGET LINK_NAME`. `main` initializes sysint defaults, resolves the link name into filesystem id and PVFS-relative path, generates default credentials, and calls `make_link`. `make_link` builds symlink attributes from credential owner/group and mode `0777`, extracts the final link basename, rejects root creation, looks up the parent handle, and invokes `PVFS_sys_symlink` with the user-supplied target string.

State and persistence: the persistent effect is a new symlink object in the OrangeFS namespace. No local files are written. The target string is stored in the symlink object and is not resolved by this tool.

Dependencies and integration points: it follows the same admin utility sysint pattern as other tools in this directory and relies on internal helpers from `pint-sysint-utils.h` and `pvfs2-internal.h`. Credential generation uses the default environment/config-driven OrangeFS credential path.

Risks: error text after `PVFS_util_resolve` mentions `pszLinkTarget` even though resolving the link name failed. `PVFS_sys_finalize` is not called on all error paths. Attributes use all settable fields even though only owner, group, and perms are initialized; zeroed timestamps may be interpreted depending on sysint expectations. The code uses internal `PINT_*` helpers with TODO comments saying they should become public utility APIs. It does not implement POSIX `ln` option compatibility beyond `-s`.

Test signals: cover missing `-s`, hard-link rejection, bad argument count, link name outside pvfstab, missing parent directory, existing link name, successful symlink to absolute and relative targets, verbose output, version output, and permission-denied credentials.
