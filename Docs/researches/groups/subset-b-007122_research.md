# subset-b-007122 Research

Grouped source research for GlusterFS NFS MOUNT service, netgroups parsing, shared NFS loc helpers, fop wrappers, and generic NFS operation facades. Each section is marker-delimited for deterministic splitting into source-tree-aligned per-file research documents.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3udp_svc.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3udp_svc.c

## Purpose

`mount3udp_svc.c` implements the ONC RPC UDP transport entry point for MOUNT v3. It decodes UDP MNT and UMNT requests, delegates filehandle lookup and mount-list mutation to `mount3.c`, sends XDR replies with libc/TIRPC svc APIs, and runs the UDP service thread when `nfs.mount-udp` is enabled. Source read: complete 237-line file.

## Important APIs, Types, and Functions

The external entry point is `mount3udp_thread`. Request handlers are `mountudpproc3_mnt_3_svc` and `mountudpproc3_umnt_3_svc`. The dispatcher is `mountudp_program_3`. It relies on external functions `nfs3_rootfh`, `mnt3svc_set_mountres3`, `mount3udp_add_mountlist`, `mount3udp_delete_mountlist`, and `mnt3svc_errno_to_mnterr`. The global `mnthost` stores the IPv4 caller address for the single UDP service path.

## Control Flow

`mount3udp_thread` sets `THIS`, creates a UDP transport with `svcudp_create`, registers MOUNT program version 3 with `svc_register`, and starts the NFS RPC poller. `mountudp_program_3` obtains the caller IPv4 address with `svc_getcaller`, stores it in `mnthost`, selects XDR routines and local handlers for `NULLPROC`, `MOUNT3_MNT`, or `MOUNT3_UMNT`, decodes arguments, invokes the local handler, sends the reply, frees arguments, and releases allocated result data.

For MNT, `mountudpproc3_mnt_3_svc` strips leading slashes, allocates a `mountres3` and one AUTH_UNIX flavor, calls `nfs3_rootfh`, maps errno to a MOUNT status on failure, and on success adds the client/export to the mount list. UMNT allocates a `mountstat3`, returns `MNT3_OK`, and deletes the mount-list entry.

## State and Persistence Behavior

This file has minimal local state: the global `mnthost` buffer and per-request allocations for replies and auth flavor arrays. Persistent and shared state is delegated to `mount3udp_add_mountlist` and `mount3udp_delete_mountlist`, which update `mount3_state` and rmtab in `mount3.c`.

## Dependencies and Integration Points

It depends on generated NFS XDR types, Gluster logging/memory APIs, `mount3.h`, libc/TIRPC svc APIs, portmap registration, and the NFS RPC poller. Its filehandle path is entirely integrated through `nfs3_rootfh` in `mount3.c`.

## Risks and Edge Cases

The code asserts IPv4 caller family and does not implement IPv6 UDP MOUNT. `mnthost` is global and documented as safe because only this thread uses it; that assumption matters if UDP serving changes. Failure paths must free `fh`, `res`, and auth arrays consistently. UDP mount list insertion delegates to a path that does not suppress duplicates as strictly as TCP.

## Test Signals

Enable `nfs.mount-udp` and run UDP MOUNT/UMNT interoperability tests, including bad export paths, auth rejection, stopped subvolumes, and allocation-failure simulation. Packet-level tests should confirm NULLPROC, MNT, UMNT, XDR decode errors, and unsupported procedure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3udp_svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/netgroups.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/netgroups.c

## Purpose

`netgroups.c` parses a Gluster NFS netgroups file into dictionary-backed netgroup and host structures for export authorization. It supports nested netgroup references, host triples in `(host,user,domain)` form, lookup by netgroup name, debug printing, and cleanup of a graph where multiple dictionaries may reference the same netgroup entry. Source read: complete 1161-line file.

## Important APIs, Types, and Functions

External APIs are `ng_file_parse`, `ng_file_get_netgroup`, `ng_file_deinit`, `ng_file_print`, and `ngh_dict_get`. The main internal builders are `_ng_init_parsers`, `_netgroups_file_init`, `_netgroup_entry_init`, `_netgroup_host_init`, `_parse_ng_line`, `_parse_ng_host`, `_ng_handle_host_part`, and `_ng_setup_netgroup_entry`. Cleanup is handled by `_netgroup_entry_deinit`, `_netgroup_host_deinit`, and dict walkers such as `__ngf_free_walk`, `__nge_free_walk`, and `__ngh_free_walk`.

## Control Flow

`ng_file_parse` opens the target file, allocates a `netgroups_file`, initializes regex parsers from `netgroups.h`, then reads lines with `getline`. Comment lines beginning with `#` are skipped. Each non-comment line is passed to `_parse_ng_line`, which treats the first match as the parent netgroup and subsequent matches as either host triples or child netgroup names. Host triples are validated for two commas and no spaces, then split by `ng_host_parser`. Child netgroups are inserted into both the global file dictionary and the parent's `netgroup_ngs` dictionary, enabling direct lookup by name while preserving nested membership structure.

## State and Persistence Behavior

The parsed state is in memory only: `netgroups_file.filename`, `ng_file_dict`, and nested `dict_t` instances for each entry. The parser globals `ng_file_parser` and `ng_host_parser` are initialized during parse and deinitialized before returning. Cleanup uses a temporary global `__deleted_entries` dictionary to prevent double-free when the same `netgroup_entry` is referenced from multiple dictionaries.

## Dependencies and Integration Points

This file depends on Gluster `dict_t`, parser utilities, memory types, and NFS logging messages. It is consumed by `mount3-auth.c`, which loads netgroups into `mnt3_auth_params` and checks whether export hosts are members of authorized netgroups.

## Risks and Edge Cases

The accepted regexes are intentionally narrow and may reject otherwise valid netgroup syntax. Host parsing allows only three regex matches and stores empty user/domain as null when the regex finds no token. Lines with malformed host entries are skipped or logged depending on error severity. The global parser and `__deleted_entries` state make concurrent parsing/deinit unsafe unless externally serialized. Deep or cyclic netgroup membership handling is not resolved here; this file only builds references.

## Test Signals

Good tests parse empty files, comment-only files, direct host entries, nested netgroups, duplicate netgroup references, malformed host triples, missing files, and files with parent-only lines. Cleanup tests should run under ASAN/valgrind to catch double-free or leaks in shared-entry graphs. Auth integration tests should verify `mount3-auth.c` can find hosts through parsed nested groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/netgroups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/netgroups.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/netgroups.h

## Purpose

`netgroups.h` declares the in-memory representation and parser API for NFS export netgroups. It is the contract between the netgroups parser and mount authorization code. Source read: complete 53-line file.

## Important APIs, Types, and Functions

The header defines log domain `GF_NG`, parser regexes `NG_FILE_PARSE_REGEX` and `NG_HOST_PARSE_REGEX`, and structs `netgroup_host`, `netgroup_entry`, and `netgroups_file`. Public APIs are `ng_file_parse`, `ng_file_get_netgroup`, and `ng_file_deinit`; `netgroups.c` also exposes print and host-dict lookup helpers not declared here.

## Control Flow

No executable flow is present. The types describe a two-level dictionary model: a netgroups file maps names to entries, and each entry may map child netgroups and hosts.

## State and Persistence Behavior

The header defines heap-owned strings for filenames, netgroup names, hostnames, users, and domains. Persistence is external: files are parsed from disk by `ng_file_parse`, but the structures are in-memory snapshots that must be released with `ng_file_deinit`.

## Dependencies and Integration Points

It includes NFS memory types, Gluster dictionaries, and `nfs.h`. It integrates with `mount3-auth.c` via `struct netgroups_file` and `struct netgroup_entry`.

## Risks and Edge Cases

The regex macros constrain accepted syntax. Callers must treat returned pointers as owned by the parsed file and avoid freeing nested entries directly. API users must call `ng_file_deinit` to avoid leaking dictionaries and strings.

## Test Signals

Compile coverage with `netgroups.c` and `mount3-auth.c`, plus parser tests that assert struct fields and dictionary contents for representative netgroups files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/netgroups.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-common.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-common.c

## Purpose

`nfs-common.c` provides shared NFS server helpers for mapping between child xlators and ids, deriving xlators from mount paths, constructing and wiping `loc_t` objects from inodes, gfids, parents, and entries, hashing gfids, and maintaining NFS inode generation context. Source read: complete 449-line file.

## Important APIs, Types, and Functions

Exported helpers include `nfs_xlid_to_xlator`, `nfs_xlator_to_xlid`, `nfs_mntpath_to_xlator`, `nfs_loc_wipe`, `nfs_loc_copy`, `nfs_loc_fill`, `nfs_inode_loc_fill`, `nfs_gfid_loc_fill`, `nfs_root_loc_fill`, `nfs_entry_loc_fill`, `nfs_hash_gfid`, and `nfs_fix_generation`. `nfs_path_to_xlator` is a stub returning `NULL`. `nfs_parent_inode_loc_fill` is implemented here but not declared in `nfs-common.h`.

## Control Flow

Xlator helpers walk the `xlator_list_t` children list by index, pointer equality, or first mount-path component. Location helpers build up `loc_t` by referencing inode and parent objects, copying gfids, resolving inode paths, or synthesizing `<gfid:...>` paths when no path is known. `nfs_entry_loc_fill` first finds the parent by gfid, then tries to find or create the entry inode depending on `how`; it returns `-2` when it filled a loc for a missing entry and the caller should force lookup.

`nfs_fix_generation` checks for existing NFS inode context and updates the generation. If no context exists, it allocates one, initializes share list state, stores it in inode ctx, and sets generation from `nfs_state`.

## State and Persistence Behavior

This file does not persist state to disk. It manipulates references to inode-table objects and may allocate path strings and NFS inode contexts. Correct callers must wipe locs with `nfs_loc_wipe` and unref any inode references they own.

## Dependencies and Integration Points

It depends on rpcsvc/NFS XDR includes, Gluster dict/xlator/iobuf/iatt/inode APIs, `nfs-fops.h`, `nfs-mem-types.h`, and NFS message IDs. It is used heavily by MOUNT subdir resolution, NFSv3 filehandle resolution, and fop wrapper code.

## Risks and Edge Cases

`nfs_inode_loc_fill` uses `loc->gfid` in the synthetic fallback path, which requires callers to have initialized the loc gfid correctly. `nfs_entry_loc_fill` relies on inode ctx to decide whether hard resolution is needed; stale or missing ctx changes control flow. `nfs_hash_gfid` compresses a 128-bit gfid into 32 bits and can collide. The undeclared `nfs_parent_inode_loc_fill` may be intentionally private but can cause prototype drift.

## Test Signals

Tests should cover root loc fill, missing parent, missing entry with and without create mode, inode path failures, generation context creation/update, xlator list mapping, mount-path parsing with leading slashes and subdirs, and gfid hash root special casing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-common.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-common.h

## Purpose

`nfs-common.h` declares shared constants and helper APIs for GlusterFS NFS server path, inode, gfid, xlator, and generation handling. Source read: complete 72-line file.

## Important APIs, Types, and Functions

Important constants are `NFS_PATH_MAX`, `NFS_NAME_MAX`, `NFS_DEFAULT_CREATE_MODE`, `NFS_RESOLVE_EXIST`, and `NFS_RESOLVE_CREATE`. Declared APIs cover xlator mapping, loc lifecycle, inode/gfid/entry/root loc construction, gfid hashing, and generation fix-up.

## Control Flow

The header has no executable flow; it defines the helper surface used by MOUNT, NFSv3 helpers, inode wrappers, and fop wrappers.

## State and Persistence Behavior

The APIs declared here manipulate transient `loc_t`, inode references, and inode ctx state. No persistent storage is declared.

## Dependencies and Integration Points

The header depends on `unistd.h`, Gluster xlator/iatt/uuid types, and standard NAME_MAX. It integrates with `mount3.c`, `nfs-fops.c`, `nfs-generics.c`, and NFS inode/filehandle code.

## Risks and Edge Cases

`NFS_PATH_MAX` is hard-coded to 4096 as a crash workaround for long paths, so callers must preserve length checks. Declarations must stay synchronized with `nfs-common.c`; currently `nfs_parent_inode_loc_fill` is implemented but not exposed here.

## Test Signals

Compile all NFS server files with this header and exercise path/gfid loc construction through MOUNT and NFSv3 lookup/read/write tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-fops.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-fops.c

## Purpose

`nfs-fops.c` is the low-level bridge between NFS protocol handlers and GlusterFS translator fops. It creates call frames from NFS user credentials, stores per-fop local state, winds translator operations, normalizes root inode attributes, injects gfid requests for create-like operations, expands auxiliary groups, forwards callbacks to protocol code, updates inode generation context, and destroys frames. Source read: complete 1630-line file.

## Important APIs, Types, and Functions

Core support functions are `nfs_fix_groups`, `nfs_fop_local_init`, `nfs_fop_local_wipe`, `nfs_frame_getctr`, `nfs_create_frame`, and `nfs_gfid_dict`. The exported fop wrappers include lookup, access, stat/fstat, opendir, flush, readdirp, statfs, create, setattr, mkdir, symlink, readlink, mknod, rmdir, unlink, link, rename, open, write, fsync, read, lk, getxattr, setxattr, and truncate. Each wrapper has a matching callback that restores program-local callback data and destroys the stack.

## Control Flow

Each wrapper validates required arguments, creates a frame with `nfs_create_frame`, initializes `nfs_fop_local` through macros from `nfs-fops.h`, saves root inode context if needed, optionally builds a `gfid-req` dictionary, and calls `STACK_WIND_COOKIE` to the child xlator fop. The callback reverses the hidden-local wrapping, fixes root inode numbers in returned `iatt` structures, updates generation on successful inode-returning operations, invokes the original protocol callback, and frees the fop local plus call stack.

Credential flow begins in `nfs_create_frame`: it copies uid, primary gid, auxiliary groups, lk owner, and identifier from `nfs_user_t` into the call stack, then `nfs_fix_groups` may replace groups with cached or freshly resolved server-side auxiliary groups.

## State and Persistence Behavior

Per-call state is stored in `struct nfs_fop_local` from an NFS mempool. It can hold original callback/local data, iobrefs, inode refs, fd refs for locks, gfid dict, root-normalization flags, paths, and lock state. There is no disk persistence. The file updates in-memory gid cache and fd lock state (`fd_lk_insert_and_merge`) and may update inode NFS generation context through `nfs_fix_generation`.

## Dependencies and Integration Points

The file depends on Gluster call frames, dicts, xlators, iobuf/iobref, call-stub semantics, semaphores, passwd/group lookup, NFSv3 helper conversion, NFS memory types, and `nfs-common.h`. Higher-level wrappers in `nfs-generics.c` and inode-aware wrappers in `nfs-inodes.c` call into this layer.

## Risks and Edge Cases

Error cleanup depends on `nfs_stack_destroy(nfl, frame)` receiving a valid `nfl`; failure before local initialization can be fragile if macros change. `nfs_fix_groups` copies up to `max_groups` but sets `root->ngrps = ngroups` after truncation, which can disagree with the copied count. `nfs_fop_write` casts `local` to `nfs3_call_state_t` to inspect `writetype`, making that wrapper less generic than its signature suggests. Root inode "funging" is necessary for stable NFS root ino but is easy to miss for new fops.

## Test Signals

Signals include NFSv3 operation tests across all wrappers, root directory stat/read/write/readdir stability after restart, create/mkdir/mknod/symlink gfid propagation, auxiliary group cache tests, lock merge tests, read/write sync mode tests, and fault injection for frame allocation, mempool allocation, dict allocation, and child fop errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-fops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-fops.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-fops.h

## Purpose

`nfs-fops.h` declares the low-level fop bridge used by GlusterFS NFS protocol code and defines `struct nfs_fop_local`, the hidden per-call state used to connect fop wrappers to protocol callbacks. Source read: complete 241-line file.

## Important APIs, Types, and Functions

The central type is `struct nfs_fop_local`, carrying protocol local/callback pointers, iobref, inode refs, root inode normalization flags, path buffers, NFS xlator pointer, gfid dict, fd, lock command, and `gf_flock`. Important macros are `nfs_state`, `nfs_fop_mempool`, `prog_data_to_nfl`, `nfl_to_prog_data`, and `nfs_fop_handle_local_init`. The header declares all `nfs_fop_*` wrappers implemented in `nfs-fops.c`.

## Control Flow

The macros define the callback wrapping pattern: allocate a fop local, move the protocol local and callback into it, install it as `frame->local`, and later restore the original protocol local before invoking the protocol callback.

## State and Persistence Behavior

State is per-call and allocated from the NFS fop mempool. The header does not persist data but encodes ownership expectations for refs and allocated dictionaries that `nfs_fop_local_wipe` releases.

## Dependencies and Integration Points

It depends on Gluster dict/iobuf/call-stub APIs, `nfs.h`, `nfs-common.h`, NFS messages, and semaphores. It is included by `nfs-generics.c`, `nfs-common.c`, NFS inode helpers, and protocol handlers.

## Risks and Edge Cases

Callback pointers are stored through a generic void-pointer cast macro, so type mismatches are compile-light and runtime-sensitive. Any new fop wrapper must keep `struct nfs_fop_local` cleanup in sync with new owned fields. Path buffers are limited to `NFS_NAME_MAX + 1`.

## Test Signals

Compile-time coverage of every declared wrapper, plus callback smoke tests for fop success and failure paths, are the main signals. Memory instrumentation should show no leaked refs after each wrapper callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-fops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-generics.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-generics.c

## Purpose

`nfs-generics.c` provides the public generic NFS operation facade used by protocol handlers. Most functions validate common arguments and delegate either to low-level `nfs_fop_*` wrappers or higher-level inode-maintenance wrappers from `nfs-inodes.c`. Source read: complete 311-line file.

## Important APIs, Types, and Functions

The file implements `nfs_fstat`, `nfs_access`, `nfs_stat`, `nfs_readdirp`, `nfs_lookup`, `nfs_create`, `nfs_flush`, `nfs_mkdir`, `nfs_truncate`, `nfs_read`, `nfs_lk`, `nfs_getxattr`, `nfs_setxattr`, `nfs_fsync`, `nfs_write`, `nfs_open`, `nfs_rename`, `nfs_link`, `nfs_unlink`, `nfs_rmdir`, `nfs_mknod`, `nfs_readlink`, `nfs_symlink`, `nfs_setattr`, `nfs_statfs`, and `nfs_opendir`.

## Control Flow

Read-only or simple fd operations usually delegate directly to `nfs_fop_*`. Operations that create, link, rename, remove, or open path-based objects often call `nfs_inode_*` wrappers so inode table maintenance is handled before the protocol callback sees results. Validation failures return `-EFAULT`.

## State and Persistence Behavior

This file owns no state. It passes through `nfs_user_t`, `loc_t`, fd, iobref, and callback state to lower layers. State effects happen in `nfs-fops.c` and `nfs-inodes.c`.

## Dependencies and Integration Points

It depends on `nfs.h`, `nfs-fops.h`, `nfs-inodes.h`, and `nfs-generics.h`. It is the stable API layer used by MOUNT subdir resolution and NFS protocol implementations, allowing protocol code to avoid choosing between raw fop and inode-maintenance variants.

## Risks and Edge Cases

Validation is inconsistent: some wrappers require `nfsx`, while `nfs_truncate`, `nfs_unlink`, `nfs_read`, `nfs_lk`, `nfs_getxattr`, and `nfs_setxattr` do not check it even though lower layers may use it. The facade is thin, so behavioral differences between direct fop and inode-aware paths must stay intentional.

## Test Signals

Tests should exercise every public generic wrapper through protocol operations, especially create/open/link/rename/unlink paths where inode maintenance differs from raw fops. Static checks can catch signature drift between this file, `nfs-generics.h`, and `nfs-fops.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-generics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-generics.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-generics.h

## Purpose

`nfs-generics.h` declares the generic NFS operation facade and directory fd context structures used by protocol handlers and shared NFS code. Source read: complete 160-line file.

## Important APIs, Types, and Functions

Important types are `struct nfs_direntcache` and `nfs_fdctx_t`, which describe cached directory entries and per-fd directory context. Declared APIs mirror `nfs-generics.c`: generic async wrappers for stat, lookup, create, read, write, open, directory, link, rename, attribute, lock, xattr, and access operations. It also declares synchronous stubs `nfs_open_sync`, `nfs_write_sync`, and `nfs_read_sync`.

## Control Flow

No executable flow exists in the header. The declarations define the operation surface that higher-level NFS protocol code calls instead of directly winding Gluster fops.

## State and Persistence Behavior

`nfs_fdctx_t` contains a mutex, directory buffer size, offset, dirent cache pointer, and directory volume pointer. This is in-memory fd context state. The header does not own persistence.

## Dependencies and Integration Points

It includes `nfs.h`, `nfs-fops.h`, and `nfs-inodes.h`. It bridges protocol code to the fop and inode maintenance layers.

## Risks and Edge Cases

The header declares synchronous APIs that are not implemented in `nfs-generics.c`, so callers rely on implementations elsewhere or risk link failures if added incorrectly. Directory cache locking and lifetime must be handled by users of `nfs_fdctx_t`.

## Test Signals

Compile/link tests should verify all declared async and sync wrappers resolve. Directory readdir tests should exercise `nfs_fdctx_t` cache state, offsets, and lock behavior through the implementation that owns those fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-generics.h -->
