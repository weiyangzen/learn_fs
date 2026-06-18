<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3.h

## Purpose

`mount3.h` is the shared contract for the GlusterFS NFS MOUNT service. It declares MOUNT program constants, exported service lifecycle functions, mount-list and export data structures, authorization entry points, and subdirectory resolve state used by `mount3.c`, UDP MOUNT glue, exports parsing, and NFSv3 auth checks. Source read: complete 186-line file.

## Important APIs, Types, and Functions

Important constants are `GF_MOUNTV3_PORT`, `GF_MOUNTV1_PORT`, `GF_MOUNTV3_IOB`, `GF_MOUNTV3_IOBPOOL`, `GF_MNT`, `MNT3_EXPTYPE_VOLUME`, and `MNT3_EXPTYPE_DIR`. The key structures are `mountentry`, `host_auth_spec`, `mnt3_export`, `mount3_state`, and `mount3_resolve_state`.

The header declares lifecycle APIs `mnt3svc_init`, `mnt1svc_init`, `mnt3svc_deinit`, `mount_init_state`, and `mount_reconfigure_state`; persistence and lookup APIs `mount_rewrite_rmtab`, `mnt3_mntpath_to_export`, and `mnt3svc_update_mountlist`; authorization API `mnt3_authenticate_request`; and directory export helpers `mnt3_parse_dir_exports` and `mnt3_get_volume_subdir`.

## Control Flow

There is no executable control flow in the header. It defines how the MOUNT service state is passed between initialization, request handlers, export parsing, auth refresh, UDP helpers, and NFS operation authorization.

## State and Persistence Behavior

`mount3_state` owns the in-memory export list, mount list, mount dictionary, mount lock, auth parameters, auth cache, refresh thread handle, and references to `nfs_state` and the NFS translator. `mountentry` mirrors mounted client/export pairs and contains a `hashkey` for `mountdict`. Persistent state is not implemented here but is represented through APIs that rewrite rmtab from `mountlist`.

## Dependencies and Integration Points

The header depends on rpcsvc, Gluster dictionaries, xlators, list and locking primitives, XDR NFS3 definitions, NFS filehandle definitions, exports, and auth-cache. It is included by `mount3.c`, `mount3udp_svc.c`, exports parsing code, and NFS helpers that need to authenticate requests.

## Risks and Edge Cases

Because these structs are shared across service code, field lifetime and locking expectations are important. `mnt3_export.hostspec` is only meaningful for directory exports; `fullpath` is allocated during directory mount resolution; `mountdict` mirrors `mountlist` but can become stale if all mutations do not update both. Consumers must honor `mountlock` when walking or mutating the lists.

## Test Signals

Compile coverage of all MOUNT/NFS server translation units is the main header signal. Runtime signals include successful MOUNT v1/v3 initialization, export list construction, mount/unmount updates, auth refresh, and per-filehandle auth checks that use this shared state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3.h -->
