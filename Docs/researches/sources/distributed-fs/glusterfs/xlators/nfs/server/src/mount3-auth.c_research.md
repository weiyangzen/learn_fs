# sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3-auth.c

## Purpose
Implements host authorization for NFS MOUNTv3 and subsequent NFS file operations. It loads parsed exports and netgroups files, checks whether a host is allowed for a directory or mounted file handle, resolves netgroup membership recursively, handles subnet entries, and enforces read-only versus read-write export options.

## APIs, Types, and Functions
Public functions are `mnt3_auth_params_init()`, `mnt3_auth_params_deinit()`, `mnt3_auth_set_exports_auth()`, `mnt3_auth_set_netgroups_auth()`, `mnt3_auth_host()`, and `check_rw_access()`. Internal structures and helpers include `struct _mnt3_subnet_match_s`, `_mnt3_auth_subnet_match()`, `_mnt3_auth_check_host_in_export()`, `struct ng_auth_search`, `__netgroup_dict_search()`, `__export_dir_lookup_netgroup()`, `_mnt3_auth_setup_search_params()`, and `_mnt3_auth_check_host_in_netgroup()`.

## Control Flow, State, and Persistence
Initialization allocates `struct mnt3_auth_params` and binds it to a `mount3_state`. Export and netgroup setters parse files, atomically replace `expfile` or `ngfile` with `__sync_lock_test_and_set()`, and deinitialize old files. `mnt3_auth_host()` first searches the exports file: for FOPs with a file handle it maps `fh->mountid` through `exp_file_dir_from_uuid()`, while mount requests use the requested directory. It then looks for exact host entries, CIDR subnet entries, and finally netgroup membership. Netgroup search walks exported netgroup names, loads corresponding netgroup entries, searches direct hosts and nested netgroups, and returns the export item that supplied options. If the operation is a write, `check_rw_access()` returns `-EROFS` unless the matched item is `rw`; otherwise authorization succeeds with 0. Deinit atomically clears `ms->auth_params` before freeing files so later FOPs are denied rather than using torn-down state.

## Dependencies and Integration
Depends on parsed exports, parsed netgroups, mount3 state, Gluster memory allocation, dict walking, `gf_is_ip_in_net()` for CIDR matching, and NFS logging. It integrates with MOUNTv3 request handling and NFS FOP authorization, and supplies the `export_item` later cached by `auth-cache.c`.

## Risks and Test Signals
Risks include atomic pointer replacement without broader reader lifetime protection, recursive netgroup cycles or deep nesting, subnet matching only for entries containing `/`, exact host string matching without DNS normalization, stale auth cache entries after reload, and the header declaration `mnt3_auth_fop_options_verify()` having no implementation in this file. Test signals include exact host, wildcard, subnet, and netgroup authorization; write attempts against read-only exports returning `-EROFS`; reload while operations run; null or missing auth files denying access; file-handle based authorization after mount; and nested netgroup search behavior.
