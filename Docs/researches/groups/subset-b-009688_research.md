# Research: subset-b-009688

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/gluster_internal.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/gluster_internal.c

Purpose: this file provides the shared implementation helpers for the NFS-Ganesha Gluster FSAL. It translates gfapi errors and POSIX `stat` data into FSAL status/attribute structures, constructs `glusterfs_handle` objects from gfapi handles, switches gfapi credentials to match `op_ctx`, converts POSIX ACLs to and from FSAL NFSv4 ACL representation, starts the Gluster upcall thread, and optionally records latency counters under `GLTIMING`.

Important APIs and functions: `gluster2fsal_error()` maps an errno-style Gluster failure to `fsal_status_t` through `posix2fsal_error()`. `stat2fsal_attributes()` fills `struct fsal_attrlist` with POSIX attributes and trims security-label support when the export option is disabled. `construct_handle()` allocates a `struct glusterfs_handle`, combines the volume UUID and GFAPI object handle into the wire handle buffer, initializes the public FSAL object, and initializes a global FD for regular files. `setglustercreds()` wraps `glfs_setfsuid`, `glfs_setfsgid`, `glfs_setfsgroups`, and optional lease-id setup. `glusterfs_get_acl()`, `glusterfs_set_acl()`, and `glusterfs_process_acl()` bridge gfapi POSIX ACL operations with Ganesha NFSv4 ACL objects.

Control flow: most callers enter from `handle.c` object operations. Lookup/create paths build a gfapi object, extract a GFAPI handle and volume id, then call `construct_handle()`. Attribute paths call `stat2fsal_attributes()` first and conditionally enrich the result with ACLs. Setattr paths use `glusterfs_process_acl()` to translate input ACLs, set gfapi stat attributes, then call `glusterfs_set_acl()` if ACLs were requested. Upcall setup initializes pthread attributes, retries `pthread_create()` on `EAGAIN`, and returns a simple success/failure integer.

State and persistence: allocated handles persist in the FSAL object cache until released. The file stores no durable metadata itself, but it maintains per-handle wire identity, global FD initialization state, saved gfapi user/group identity, ACL buffers inside `glusterfs_fsal_xstat_t`, optional lease ids, and optional global latency counters. Credential switching is process/thread-visible through gfapi APIs and must always be paired with reset macros from the header.

Dependencies and integration points: this file depends on gfapi handle and ACL APIs, POSIX ACL helpers, `fsal_commonlib`, NFSv4 ACL cache helpers, `op_ctx`, export options, and the Gluster upcall thread entry point declared elsewhere. It is the utility layer consumed by `handle.c`, export creation, upcall code, and pNFS helpers.

Risks: credential switching failures are logged fatal but do not return status to the original caller. ACL conversion allocates and shrinks buffers, so error paths must release ACL memory with `glusterfs_fsal_clean_xstat()`. `stat2fsal_attributes()` uses legacy seconds-only timestamps because gfapi did not expose full timespecs in this code path. `construct_handle()` assumes supplied gfapi objects and UUID/handle buffers are valid and transfers ownership to the FSAL handle. Tests should exercise gfapi errno mapping, lookup/getattr with and without ACLs, directory default ACL conversion, setattr ACL failures, seclabel support toggles, and upcall thread startup failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/gluster_internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/gluster_internal.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/gluster_internal.h

Purpose: this header defines the private ABI for the Gluster FSAL. It collects module constants, supported/settable attribute masks, gfapi handle sizing, ACL flags, optional latency slots, core private structs, credential macros, and prototypes for object operations, export creation, pNFS, upcalls, and FD helpers.

Important APIs and types: `struct glusterfs_fsal_module` embeds `struct fsal_module`, the global object operation vector, a list of `glusterfs_fs` objects, and a mutex protecting that list. `struct glusterfs_fs` represents a mounted Gluster volume with the `glfs_t *`, refcount, upcall thread, polling interval, and destroy/upcall flags. `struct glusterfs_export` binds an FSAL export to a `glusterfs_fs`, export/mount paths, saved credentials, pNFS enablement flags, and security-label xattr name. `struct glusterfs_handle` is the object handle wrapper containing the gfapi object, serialized object id, global FD, public FSAL handle, share reservation counters, pNFS layout counters, and optional delegation lease state. `struct glusterfs_fd` stores the FSAL FD wrapper, gfapi fd, opener credentials, and optional lease id. `struct glusterfs_state_fd` extends `state_t` with a per-state Gluster FD.

Control flow and integration: code enters this contract from module initialization (`main.c`), object operations (`handle.c`), pNFS MDS/DS files, export creation, and upcall handlers. The `SET_GLUSTER_CREDS_OP_CTX`, `SET_GLUSTER_CREDS_MY_FD`, `SET_GLUSTER_LEASE_ID`, and `RESET_GLUSTER_CREDS` macros preserve errno while calling `setglustercreds()`, which is central to every gfapi operation that must run as the NFS caller or original opener.

State and persistence: the header describes all long-lived in-memory Gluster FSAL state. `glusterfs_fs` instances are shared by exports and reference-counted. `glusterfs_export` persists per export. `glusterfs_handle` persists per cached object, while `glusterfs_state_fd` persists per open/share state. No on-disk format is declared except the wire handle layout: a Gluster volume UUID prefix plus GFAPI object handle bytes.

Dependencies: it depends on Ganesha FSAL public/private headers, POSIX ACL support, Gluster gfapi headers, export option inspection, NFSv4/pNFS types, and conditional `USE_GLUSTER_DELEGATION` and `GLTIMING` features.

Risks and test signals: changes here affect every Gluster operation and must preserve struct ownership conventions and wire-handle length. Credential macros depend on global `op_ctx` and may be unsafe if used outside a request context. Lease IDs are derived from client socket addresses and silently zeroed if unavailable or too long. Tests should compile both delegation and non-delegation builds, pNFS and non-pNFS builds, verify serialized handle length/key behavior, validate FD credential copy/free paths, and run ACL/seclabel paths with export options enabled and disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/gluster_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/handle.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/handle.c

Purpose: this file implements the Gluster FSAL object operation vector. It covers lifecycle, lookup, readdir, creation, symlink, getattr, link/rename/unlink, open tracking, read/write/commit, locks, optional leases, setattr, NFSv4 xattrs, wire-handle encoding, and pNFS operation attachment.

Important APIs and functions: namespace operations include `lookup()`, `read_dirents()`, `makedir()`, `makenode()`, `makesymlink()`, `readsymlink()`, `linkfile()`, `renamefile()`, and `file_unlink()`. Attribute paths are `getattrs()`, `glusterfs_fsal_get_sec_label()`, and `glusterfs_setattr2()`. Open-tracking helpers include `glusterfs_create_my_fd()`, `glusterfs_reopen_func()`, `glusterfs_close_my_fd()`, `glusterfs_open2_by_handle()`, `glusterfs_open2()`, `glusterfs_status2()`, `glusterfs_reopen2()`, `glusterfs_close2()`, and `glusterfs_merge()`. I/O and state operations are `glusterfs_read2()`, `glusterfs_write2()`, `seek2()`, `glusterfs_commit2()`, `glusterfs_lock_op2()`, and optional `glusterfs_lease_op2()`. `handle_ops_init()` installs these into `struct fsal_obj_ops`.

Control flow: lookup and create paths switch to caller credentials, call gfapi handle-based operations, extract object handles and volume IDs, call `construct_handle()`, and optionally populate attrs/ACLs. `open2()` splits by name versus existing handle. By-name creates call `glusterfs_create_my_fd()`, create a FSAL handle, transfer or duplicate the temporary FD into the global FD, optionally apply post-create attributes, and then establish share counters. Existing-handle opens serialize FD work, take `obj_lock` when stateful sharing is involved, check share conflicts, reopen through gfapi, update LRU state, and verify exclusive-create verifiers when needed. Read/write/seek/commit obtain usable FDs through common FSAL FD helpers, perform synchronous gfapi calls, complete I/O, then invoke the async callback for read/write.

State and persistence: each regular file handle owns a global `glusterfs_fd`, share reservation counters, gfapi object handle, and wire handle bytes. Stateful NFS opens own `glusterfs_state_fd` descriptors. FD LRU insertion/removal tracks global and state FDs. The code stores opener credentials with FDs so close, lock, and reopen can run under the same identity. Xattrs, ACLs, and security labels are persisted in Gluster through gfapi xattr/ACL/setattr APIs.

Dependencies and integration: this file is glued to gfapi handle APIs, FSAL common FD/share helpers, SAL state types, NFSv4 ACL/security label support, pNFS hooks from `mds.c`, and optional LTTng tracepoints. It calls helpers from `gluster_internal.c` for errors, attributes, ACLs, credentials, handle construction, and cleanup.

Risks: the file has many paired credential switches and cleanup branches; missing a reset or `gluster_cleanup_vars()` would leak identity or gfapi handles. Some async FSAL hooks are implemented synchronously. `listxattrs()` manually packs names and values into caller memory and has tight maxcount/cookie edge cases. Lock error handling currently initializes `status` to success and relies on lower helpers, so failed gfapi lock paths require careful review. Create retry paths document rare races that may leak partially created files. Test signals include NFSv3 stateless create, NFSv4 guarded/exclusive/unchecked open, share-deny conflicts, FD LRU reopen/close, readdir with and without xreaddirplus, ACL/seclabel attrs, xattr list pagination, DATA/HOLE seek, lock conflict reporting, and pNFS operation registration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/main.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/main.c

Purpose: this file is the module entry point for the Gluster FSAL. It declares the global `GlusterFS` module object, static filesystem capabilities, module-level config parsing for pNFS roles, and load/unload hooks that register and unregister the FSAL with NFS-Ganesha.

Important APIs and functions: `GlusterFS` embeds `fsal_staticfsinfo_t` values such as max name/path length, ACL support, link/symlink/lock support, named attributes, unique handles, pNFS defaults, delegation support, and readdir-plus support. `glfs_params` and `glfs_param` define the global `GLUSTER` config block with `pnfs_mds` and `pnfs_ds`. `init_config()` loads optional config into `GlusterFS.fsal.fs_info` and displays final FS info. `glusterfs_init()` registers the FSAL name `GLUSTER`, installs module operations, initializes pNFS DS operation factories, initializes object ops through `handle_ops_init()`, and initializes the volume list/mutex. `glusterfs_unload()` unregisters the FSAL and validates that no active shares remain.

Control flow: at module load, Ganesha calls `MODULE_INIT`. Registration must succeed before any operation pointers are useful. The file then wires `create_export`, `init_config`, `getdeviceinfo`, and pNFS DS ops into the public module operations. The object operation vector is initialized once globally. At unload, unregister must succeed, the shared filesystem list should be empty, and the mutex is destroyed.

State and persistence: the global module object is process-lifetime state. It holds the shared FS info and all Gluster FS object list state initialized here. The file does not persist to disk; it establishes capability flags that affect every export and operation.

Dependencies and integration: this file depends on FSAL registration APIs, `gluster_internal.h`, commonlib helpers, pNFS hooks from `mds.c`, DS ops from other Gluster FSAL files, and object operations from `handle.c`. Export creation is delegated to `glusterfs_create_export()`.

Risks and test signals: capability flags must match actual operation support. Advertising delegations, pNFS DS, named attrs, ACLs, or readdir-plus incorrectly can expose unsupported paths to clients. The config block is optional and treats parse failures as harmless unless non-harmless errors are reported. Tests should include module load/unload, global config parse with pNFS booleans, export creation after init, pNFS feature negotiation, and unload with active exports to confirm warnings rather than crashes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/mds.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/mds.c

Purpose: this file implements the Gluster FSAL pNFS metadata-server hooks for NFSv4.1 file layouts. It advertises supported layout properties, grants and commits layouts, encodes device addresses, selects a Gluster data server from pathinfo, and attaches pNFS functions to FSAL/export/object operation vectors.

Important APIs and functions: `fs_layouttypes()`, `fs_layout_blocksize()`, `fs_maximum_segments()`, `fs_loc_body_size()`, and `fs_da_addr_size()` report pNFS layout capabilities and XDR buffer sizing. `pnfs_layout_get()` validates `LAYOUT4_NFSV4_1_FILES`, derives a device id from Gluster pathinfo, extracts GFID, builds a `glfs_ds_wire`, and calls `FSAL_encode_file_layout()`. `pnfs_layout_return()` accepts returns for file layouts. `pnfs_layout_commit()` updates size and mtime through `glfs_h_truncate()` and `glfs_h_setattrs()`. `getdeviceinfo()` encodes an NFSv4 multipath DS address from `deviceid->device_id4`. `select_ds()`, `superfasthash()`, and `glfs_get_ds_addr()` parse `trusted.glusterfs.pathinfo`, hash the object GFID across available POSIX bricks, resolve the selected hostname, and return an IPv4 address.

Control flow: export ops advertise one file layout type and one segment. A layout get call computes a dense file layout, chooses a DS, extracts a wire GFID, and encodes one layout segment with `return_on_close`. Layout commit first stats the MDS object, conditionally extends size, computes mtime, switches credentials, and sets attributes. Device info XDR encoding writes stripe count/index, DS count, then a single TCP/2049 host.

State and persistence: the file does not keep durable state. It encodes transient pNFS state into layout bodies and device-address XDR streams. It reads Gluster pathinfo xattrs and object handles, and persists size/mtime updates during layout commit.

Dependencies and integration: this code depends on gfapi xattrs, handle extraction, DNS resolution, FSAL pNFS XDR helpers, NFS export ids, `op_ctx`, Gluster credential macros, and module/export/object ops initialized in `main.c` and `handle.c`.

Risks: only IPv4 is supported despite comments noting IPv6 gaps. `trusted.glusterfs.pathinfo` parsing uses fixed-size buffers and string scanning for `POSIX`, so pathinfo format changes can break DS selection. `MAX_DS_COUNT` truncates large brick lists. Device ids encode one IPv4 address in a 32-bit field, limiting multipath/failover semantics. Layout commit updates mtime to now when client time is not newer. Tests should cover layout get for unsupported types, valid pathinfo with one and many DS entries, malformed pathinfo, DNS failure, deviceinfo XDR decode, layout commit size extension, and pNFS ops installed only when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/mds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/CMakeLists.txt

Purpose: this build file defines the GPFS FSAL module target. It adds GPFS FSAL include paths, optionally includes DBus headers, enumerates all GPFS FSAL source files, creates the `fsalgpfs` loadable module, applies sanitizer instrumentation, links against Ganesha and system libraries, sets the module version, and installs it into the FSAL destination.

Important build APIs and targets: `fsalgpfs_LIB_SRCS` includes module registration, export, handle, file I/O, upcall, DS/MDS pNFS, unlink, symlink, rename, create, fileop, attrs, lock, lookup, convert, internal open-handle wrappers, GPFS extensions, and stats sources. `add_library(fsalgpfs MODULE ...)` builds a plugin-style shared object. `target_link_libraries()` links `ganesha_nfsd`, `${SYSTEM_LIBRARIES}`, and `${LDFLAG_DISALLOW_UNDEF}`. `set_target_properties()` declares version `4.2.0` and soversion `4`.

Control flow: CMake evaluates DBus include handling first, then module include directories, source collection, target creation, sanitizer attachment, link rule setup, version metadata, and install rule.

State and persistence: this file persists no runtime state, but it controls which source files are compiled into the GPFS FSAL. Omitting a file here removes operation implementations from the module.

Dependencies and integration: it integrates with the repository's CMake variables, sanitizer helper, Ganesha core target, and FSAL install layout. GPFS-specific headers are included from the FSAL source directory.

Risks and test signals: unresolved symbol policy depends on `${LDFLAG_DISALLOW_UNDEF}`, so platform link behavior matters. Adding new GPFS source files requires updating this list. DBus includes are conditional but no DBus library is linked here, so dependencies must be satisfied elsewhere. Tests are build-oriented: configure with and without `USE_DBUS`, build `fsalgpfs` with sanitizers enabled, verify no undefined symbols, and confirm install destination contains the module.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/export.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/export.c

Purpose: this file implements GPFS FSAL export lifecycle and export-level operations. It releases exports, returns dynamic filesystem info, reports supported attributes with export ACL policy, manages quotas, translates file handles between wire and host/key forms, allocates/free per-state FDs, claims/unclaims GPFS filesystems, starts/stops the GPFS upcall thread, and creates configured exports.

Important APIs and functions: `gpfs_export_ops_init()` installs export operations including `lookup_path`, `wire_to_host`, `host_to_key`, `create_handle`, dynamic info, quota get/set, state allocation, and reverse FD-to-handle lookup. `gpfs_wire_to_host()` endian-corrects `struct gpfs_file_handle`, validates expected handle length while tolerating older handles with 16 extra bytes, and returns host length. `gpfs_host_to_key()` shortens a host handle to its key size. `gpfs_alloc_state()` and `gpfs_free_state()` manage `struct gpfs_state_fd`. `open_root_fd()` opens the GPFS mount root, obtains a GPFS file handle, extracts/re-indexes FSID. `gpfs_claim_filesystem()` validates filesystem type `gpfs`, opens the export directory, initializes shared filesystem private data, and starts `GPFSFSAL_UP_Thread`. `gpfs_create_export()` parses export config, attaches the export, resolves the POSIX filesystem, obtains node id, enables pNFS DS registration when supported, and records ACL policy.

Control flow: export creation allocates `gpfs_fsal_export`, initializes ops, parses config, attaches to module, resolves/claims the filesystem, optionally queries node id, configures pNFS DS, and returns the export. Error paths unwind pNFS/export maps, detach from FSAL, free ops, and free the export. Filesystem claim creates shared private data only on first claim; later claims reuse `private_data` but still open the per-export FD. Unclaim signals the kernel/upcall thread through `OPENHANDLE_THREAD_UPDATE`, sets a stop flag, joins the thread, and frees filesystem state.

State and persistence: per-export state includes `export_fd`, filesystem list, root FS, pNFS enablement, ACL use, and `ignore_mode_change`. Per-filesystem state includes root fd, GPFS FS pointer, stop flag, and upcall thread. No durable metadata is written except GPFS quota changes via `gpfs_ganesha(OPENHANDLE_QUOTA)`.

Dependencies and integration: depends on GPFS kernel/openhandle extension APIs (`gpfs_ganesha`), Ganesha export manager, filesystem resolution, pNFS registry, FSAL state helpers, and POSIX mount/statfs/quotactl structures.

Risks and test signals: claim/unclaim threading and FD ownership are sensitive; the already-claimed path returns without closing the newly opened export fd if not carefully managed by caller lifetime. Quota operations reject mount-boundary crossings by comparing device major/minor. Wire handle length compatibility hides older format differences but should not accept malformed handles. Tests should cover export config parse, non-GPFS filesystem rejection, mount root open failures, FSID reindex failure, upcall thread start/stop, quota get/set with crossed mounts, endian wire-handle conversion, pNFS DS duplicate server id, and release cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/file.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/file.c

Purpose: this file implements GPFS FSAL open tracking and file I/O operations. It manages GPFS-backed `fsal_fd` reopen/close, duplicate-handle share merging, open-by-handle/name/create semantics, read/read-plus/write/fallocate/commit, lock operations, DATA/HOLE seek, fadvise, and global/state close operations.

Important APIs and functions: `gpfs_reopen_func()` opens a GPFS fd with requested FSAL flags and closes the old fd after successful replacement. `open_by_handle()` serializes FD work, checks share conflicts, handles no-op reopens, updates FD LRU, refreshes attrs for truncate/exclusive verifier checks, and closes on errors. `gpfs_open2()` handles NFS open/create modes, including unchecked retry without `O_EXCL`, `GPFSFSAL_create2()`, handle allocation, post-create setattr, cleanup unlink, and final open-by-handle. `gpfs_read2()` and `gpfs_write2()` loop over iovecs using `GPFSFSAL_read()`/`GPFSFSAL_write()` or `gpfs_read_plus_fd()`. `gpfs_commit2()` flushes through `OPENHANDLE_FSYNC`. `gpfs_lock_op2()` maps FSAL locks to GPFS `glock` commands, including blocking locks and cancel. `gpfs_seek2()` uses `OPENHANDLE_SEEK_BY_FD`. `gpfs_fallocate()` and `gpfs_io_advise()` call GPFS allocation and fadvise hooks.

Control flow: every data operation first calls `fsal_start_io()` or `fsal_start_global_io()` with the object global fd, a temp fd, optional state, required open mode, bypass policy, and share counters. After the GPFS operation, it calls `fsal_complete_io()` and releases temporary share counters when the operation was stateless. Create flow converts FSAL flags/mode to POSIX, optionally sets exclusive verifier attrs, creates a GPFS handle, allocates a FSAL object handle, applies remaining attrs only if this server created the file, and opens the new object.

State and persistence: GPFS FDs are integer descriptors stored in `struct gpfs_fd` for global object FDs or per-state FDs. Share reservations live in `gpfs_fsal_obj_handle.u.file.share`. FD LRU state is updated on opens/reopens. Writes, fallocate, locks, quota-related commit, and fadvise persist through GPFS kernel/openhandle calls.

Dependencies and integration: this file depends on helpers from `fsal_internal.c`, `fsal_fileop.c`, `fsal_attrs.c`, `fsal_create.c`, GPFS lock/fadvise/read/seek ioctl structures, common FSAL FD/share machinery, `alloc_handle()` from GPFS handle code, and `op_ctx` export/client credentials.

Risks: iovec reads/writes increment offset by requested iov length rather than actual transferred length, which is acceptable only if short I/O stops or EOF/error semantics are consistent. The comment in no-create by-name open notes suspicion that a new object handle is not returned. `gpfs_commit_fd()` sets `mountdirfd` to the open file fd, which should be validated against GPFS API expectations. Seek size check is explicitly non-atomic. Lock length range validation prevents negative POSIX lengths, but owner/state null handling is critical. Tests should cover all create modes, verifier mismatch, share deny, stateless I/O, short read/write, READ_PLUS holes, fallocate allocate/deallocate, commit errors including `EUNATCH`, lock/lockt/unlock/cancel, seek beyond EOF, fadvise, FD LRU cleanup, and cross-FSAL EXDEV rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_attrs.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_attrs.c

Purpose: this file implements GPFS FSAL attribute retrieval and mutation. It retrieves fs_locations, xstat/ACL data, filesystem statistics by file handle, and applies setattr operations including size, reserved space, mode, owner, group, timestamps, and NFSv4 ACLs.

Important APIs and functions: `GPFSFSAL_fs_loc()` calls `OPENHANDLE_FS_LOCATIONS`, builds `nfs4_fs_locations`, and stores root/path/server data in the attrlist. `GPFSFSAL_getattrs()` calls `fsal_get_xstat_by_handle()` with optional ACL buffers, retries with heap buffers if the embedded ACL buffer is too small, fills fallback FSID for older GPFS, and calls `gpfsfsal_xstat_2_fsal_attributes()`. `GPFSFSAL_statfs()` calls `OPENHANDLE_STATFS_BY_FH`. `GPFSFSAL_setattrs()` converts FSAL attr masks into GPFS xstat masks and optional NFSv4 ACL buffers, then calls `fsal_set_xstat_by_handle()`.

Control flow: getattr initializes FSID defaults, determines whether expiration and ACLs were requested, tries the stack ACL buffer first, grows to `acl_buf->acl_len` on retry, and converts only after a successful xstat fetch. Setattr first validates time-setting support, applies export umask to mode, fills `buffxstat` and mask bits for requested attrs, converts ACLs when enabled and present, then sends a single xstat update if anything changed.

State and persistence: attributes are persisted through GPFS openhandle xstat calls. The file manages temporary ACL buffers and `attrs->fs_locations` lifetime by releasing old data before replacing it. `expire_time_attr` can update attribute cache expiration in `fsal_attrlist`.

Dependencies and integration: depends on `gpfs_ganesha`, GPFS xstat structures, `fsal_acl_2_gpfs_acl()` from `fsal_convert.c`, GPFS filesystem private data, export ACL policy, and common FSAL attr/mask helpers.

Risks and test signals: ACL retry logic assumes `acl_buf->acl_len` is valid after a too-small response. Symlink chmod is intentionally ignored. `ignore_mode_change` can suppress mode changes per export. `ATTR4_SPACE_RESERVED` reuses `st_size` in the GPFS stat buffer and must match lower-layer expectations. Tests should cover ACL disabled/enabled getattrs, oversized ACL retry, RDATTR_ERR behavior, fs_locations allocation/release, statfs `EUNATCH`, setattr time support rejection, umask mode changes, symlink mode ignores, ACL inheritance validation through convert, and heap ACL cleanup on errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_attrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_convert.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_convert.c

Purpose: this file translates GPFS-specific xstat, ACL, credential, and mode representations into Ganesha FSAL structures and back. It is the conversion layer used by GPFS getattr, setattr, access, and ACL paths.

Important APIs and functions: `gpfsfsal_xstat_2_fsal_attributes()` fills requested FSAL attributes from `gpfsfsal_xstat_t`, including type, size, FSID, ACL, fileid, mode, links, owner/group, atime/ctime/mtime, change, space used, and rawdev. `gpfs_acl_2_fsal_acl()` converts GPFS NFSv4 ACL entries into FSAL ACEs and creates a cached `fsal_acl_t`. `fsal_acl_2_gpfs_acl()` converts FSAL ACEs into a GPFS `gpfs_acl_t` buffer and validates maximum ACE count plus inheritance rules. `fsal_cred_2_gpfs_cred()` maps caller uid/gid/groups. `fsal_mode_2_gpfs_mode()` converts FSAL mode or NFSv4 access mask into GPFS access mode bits.

Control flow: attribute conversion is request-mask driven, so only requested attrs are filled and marked valid. ACL conversion is attempted only when requested, enabled, and present in `attr_valid`; failure to provide a requested ACL fails the whole conversion. Change time is computed as the greater of mtime/ctime with nanosecond handling. Mode conversion derives read/write/execute bits from NFSv4 ACE permissions when an explicit mode is zero.

State and persistence: this file does not persist data itself. It allocates FSAL ACL entries through the NFSv4 ACL cache and writes caller-provided GPFS ACL buffers. The resulting attrlists and ACLs are consumed by higher FSAL layers.

Dependencies and integration: it depends on `fsal_internal.h`, GPFS ACL constants, `nfs4_acls.h`, POSIX stat types, and FSAL ACE helper macros. It is called directly from `fsal_attrs.c` and access-related GPFS code.

Risks and test signals: `fsal_cred_2_gpfs_cred()` copies groups without checking GPFS array capacity in this file. `fsal_mode_2_gpfs_mode()` shifts mode by 24 bits, so callers must pass FSAL-mode formatted masks. ACL inheritance validation rejects inherit flags on non-directories and inherit-only without inherit flags, which should be reflected in client errors. Tests should cover request-mask partial attr conversion, ACL disabled/missing cases, special owner/group ACE conversion, max ACE overflow, invalid inheritance combinations, change time ordering with nanoseconds, credential group copying, and mode conversion from both explicit mode and v4 masks for files/directories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_convert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_create.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_create.c

Purpose: this file implements GPFS filesystem object creation helpers: regular file creation, create-with-POSIX-flags for open2, directory creation, hardlink creation, and special node creation.

Important APIs and functions: `GPFSFSAL_create()` converts FSAL access mode to Unix mode, applies export umask, calls `fsal_internal_create()` with `S_IFREG`, and fetches attributes. `GPFSFSAL_create2()` accepts a Unix mode and POSIX flags from open2, calls the same internal create helper, and optionally fetches attrs. `GPFSFSAL_mkdir()` creates directories with `S_IFDIR`. `GPFSFSAL_link()` checks export link support and calls `fsal_internal_link_fh()` against the destination directory handle. `GPFSFSAL_mknode()` converts FSAL node types to Unix `S_IFBLK`, `S_IFCHR`, `S_IFSOCK`, or `S_IFIFO`, builds a device number for block/character files, calls `fsal_internal_mknode()`, and returns attrs.

Control flow: each mutating operation validates required pointers, converts mode/device inputs, switches to caller credentials with `fsal_set_credentials()`, invokes the lower internal openhandle operation, restores Ganesha credentials, and retrieves post-create attrs on success.

State and persistence: successful operations persist filesystem entries in GPFS and return GPFS file handles. The file itself stores no long-lived state. Attribute outputs are populated through `GPFSFSAL_getattrs()` using the parent object's filesystem private data.

Dependencies and integration: depends on GPFS internal creation/link/mknode wrappers, `GPFSFSAL_getattrs()`, FSAL access/mode helpers, export umask/link capability, and `op_ctx` credentials/export.

Risks and test signals: `fsal_attr` is documented optional in comments, but `GPFSFSAL_create()` and similar functions pass it to `GPFSFSAL_getattrs()` unconditionally after success, so callers should supply a valid attrlist or confirm lower code tolerates NULL. Device construction uses a manual `(major << 20) | minor` layout instead of `makedev()`, which may be platform-sensitive. Tests should cover null argument faults, umask application, create2 with `O_EXCL`/`O_CREAT`, mkdir attrs, link disabled support, invalid node types, missing device for block/char nodes, credential restore on lower failure, and post-create getattr errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_create.c -->
