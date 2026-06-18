# sources/distributed-fs/orangefs/src/common/misc/pvfs2-win-util.c

Purpose: Windows-specific counterpart to `pvfs2-util.c`, implementing OrangeFS utility behavior with CRT/Win32-compatible path, mount-tab, umask, attrmask, size, and mode helpers while leaving credential code disabled.

Important APIs and functions: Provides `PVFS_util_gen_mntent`, `PVFS_util_parse_pvfstab`, `PVFS_util_add_dynamic_mntent`, `PVFS_util_remove_internal_mntent`, `PVFS_util_get_mntent_copy`, `PVFS_util_resolve`, `PVFS_util_resolve_absolute`, `PVFS_util_init_defaults`, `PINT_release_pvfstab`, `PVFS_util_copy_sys_attr`, `PVFS_util_free_mntent`, `PVFS_util_copy_mntent`, `PVFS_util_sys_to_object_attr_mask`, `PVFS_util_object_to_sys_attr_mask`, `PVFS_util_make_size_human_readable`, `PVFS_util_translate_mode`, and local `basename`/`dirname` replacements. Most credential helpers are inside `#if 0` and are not compiled.

Control flow: Windows tab parsing accepts `PVFS2EP` or a single explicit/`PVFS2TAB_FILE` tabfile rather than searching Unix defaults. It uses a simplified local `struct fstab` parser based on space-separated fields, validates `pvfs2` entries, splits comma-separated server addresses, and parses `flowproto`, `encoding`, and `num_dfiles`. Resolution directly checks internal mount arrays with `PINT_remove_dir_prefix`; canonicalization fallback is disabled by `#if 0`.

State and persistence: `s_stat_tab_array`, `s_stat_tab_count`, `s_stat_tab_mutex`, dynamic mount entries, and cached `_umask` are process-local. Inputs come from `PVFS2EP`, `PVFS2TAB_FILE`, and the specified tabfile. No registry or file writes are performed by this file.

Dependencies and integration points: Includes Windows CRT headers (`io.h`, `_umask`, `_snprintf`) and the same OrangeFS sysint, attr, debug, string, lock, realpath, and security headers as the POSIX version. Integrates with `PVFS_sys_initialize`, `PVFS_sys_fs_add`, and `PVFS_sys_finalize`.

Risks: Several error exits return while holding `s_stat_tab_mutex` in dynamic add/remove paths. The simplified fstab parser uses non-reentrant `strtok` despite a comment claiming thread safety, though the parser is usually under a mutex. Credential functions are disabled, so Windows callers must obtain credentials elsewhere. `memset(cred, 0, sizeof(cred))` in disabled code would be pointer-sized if re-enabled. Option support lacks `bmi_opts` parity with POSIX.

Test signals: Windows tabfile parsing for valid/malformed entries, duplicate dynamic fsids, lock-release behavior on allocation failures, path resolution with drive/relative/slash forms, local basename/dirname edge cases, attrmask parity with POSIX, size formatting via `_snprintf`, and compile checks proving disabled credential code stays excluded or is fixed before enabling.
