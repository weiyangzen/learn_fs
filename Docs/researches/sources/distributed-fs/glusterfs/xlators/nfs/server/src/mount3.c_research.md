<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3.c

## Purpose

`mount3.c` implements most of GlusterFS's NFS MOUNT protocol support for MOUNT v3 and shared MOUNT v1 actors. It owns MOUNT reply serialization, export discovery, full-volume and subdirectory mount resolution, rmtab-backed mount list persistence, TCP and UDP mount authorization checks, exports/netgroups auth refresh, and registration of the MOUNT RPC programs. Source read: complete 4466-line file.

## Important APIs, Types, and Functions

The file operates on `struct mount3_state`, `struct mnt3_export`, `struct mountentry`, `struct host_auth_spec`, and `mnt3_resolve_t` from `mount3.h`. Public or cross-file entry points include `mount_init_state`, `mount_reconfigure_state`, `mnt3svc_init`, `mnt1svc_init`, `mnt3svc_deinit`, `mount_rewrite_rmtab`, `mnt3_mntpath_to_export`, `mnt3svc_update_mountlist`, `mnt3_authenticate_request`, `mnt3_parse_dir_exports`, `mnt3_get_volume_subdir`, `nfs3_rootfh`, `mount3udp_add_mountlist`, and `mount3udp_delete_mountlist`.

Core protocol helpers include `mnt3svc_submit_reply`, `mnt3svc_mnt_error_reply`, `mnt3svc_errno_to_mnterr`, and `mnt3svc_set_mountres3`. Mount list persistence is handled by `__mount_read_rmtab`, `__mount_rewrite_rmtab`, `mount_read_rmtab`, `mount_rewrite_rmtab`, `mnt3svc_update_mountlist`, `mnt3svc_umount`, and `__mnt3svc_umountall`. Export setup is handled by `mnt3_export_fill_hostspec`, `mnt3_export_parse_auth_param`, `mnt3_init_export_ent`, `__mnt3_init_volume_direxports`, `__mnt3_init_volume`, and `mnt3_init_options`.

## Control Flow

Initialization starts with `mount_init_state`, which allocates a shared mount state and initializes exports from translator options. `mnt3svc_init` attaches the state to the MOUNT v3 RPC program, creates `mountdict`, loads exports/netgroups auth when enabled, starts the auth refresh thread, creates the TCP listener on `GF_MOUNTV3_PORT`, and optionally starts the UDP thread. `mnt1svc_init` registers a smaller MOUNT v1 actor table that reuses dump, unmount, and export handlers.

For a TCP MOUNT request, `mnt3svc_mnt` decodes the path, finds an exact export or dynamic subdir export through `mnt3_find_export`, checks volume started state and rpcsvc allow/privileged-port policy, runs exports/netgroups authorization, then dispatches to `mnt3svc_volume_mount` or `mnt3_resolve_export_subdir`. Volume mounts lookup the volume root inode and build a root filehandle in `mnt3svc_lookup_mount_cbk`. Subdirectory mounts resolve path components with hard `nfs_lookup` calls, handle `ESTALE` by unlinking the inode and retrying, optionally resolve relative symlinks via `mnt3_readlink_cbk`, authenticate the final full path, build a child filehandle, update the mount list, and reply.

The DUMP, UMNT, UMNTALL, and EXPORT actors build XDR reply lists from `mountlist` or `exportlist`. UDP MOUNT is split with `mount3udp_svc.c`; this file provides `nfs3_rootfh`, which chooses volume versus subdir handling, checks UDP auth, resolves the inode with either `inode_from_path` or `glfs_resolve_at`, and builds a filehandle.

## State and Persistence Behavior

Runtime state lives in `mount3_state`: `exportlist`, `mountlist`, `mountdict`, `mountlock`, auth parameters, auth cache, and refresh thread flags. The mount list is also persisted in the configured `nfs->rmtab` store file unless disabled. Store updates use `gf_store_handle`, advisory store locks, temporary files, and rename. Reconfiguration rebuilds `exportlist` under `mountlock`, and `mount_rewrite_rmtab` can migrate existing entries to a new rmtab path.

Auth state is loaded from `${GLUSTERD_DEFAULT_WORKDIR}/nfs/exports` and `/nfs/netgroups`. `_mnt3_auth_param_refresh_thread` polls mtimes, reloads changed auth files, purges the auth cache, and invalidates mounted exports that are no longer authorized.

## Dependencies and Integration Points

The file integrates with rpcsvc, XDR helpers, Gluster inode/location APIs, `nfs-common.c`, `nfs-generics.c`, `nfs-fops.c`, `nfs3-fh`, `exports.c`, `mount3-auth.c`, `netgroups.c`, auth-cache, gfapi path resolution, store APIs, and the parent `nfs_state`. NFSv3 file operations call back into `mnt3_authenticate_request` through `nfs3-helpers.c` to validate filehandles against the auth cache and export rules.

## Risks and Edge Cases

The main risks are authorization drift, stale filehandles, rmtab races, and incomplete cleanup. `mount3udp_add_mountlist` adds entries without the duplicate suppression used by TCP. Subdir auth only supports IPv4 host specs. DNS lookups and reverse lookups affect auth decisions and latency, although MOUNT3 is configured as a synctask. `mnt3_init_state` leaks the allocated `mount3_state` if option initialization fails. `mnt3svc_deinit` clears mounts and unrefs `mountdict` but does not visibly free all exportlist entries or the `mount3_state` object in this file. Symlink resolution rejects absolute symlink targets and has documented limitations for paths that leave and re-enter the filesystem.

## Test Signals

Useful signals include MOUNT v3 TCP and UDP mount/unmount/showmount tests, rmtab persistence and reconfigure tests, duplicate mount suppression tests, `nfs.export-dir` hostspec parsing with IPv4, CIDR, and hostname cases, exports/netgroups refresh tests that revoke active mounts, DVM on/off filehandle compatibility tests, subdir symlink resolution tests, and failure-path tests for missing volumes, stopped subvolumes, bad XDR, unprivileged clients, and missing auth files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3.c -->
