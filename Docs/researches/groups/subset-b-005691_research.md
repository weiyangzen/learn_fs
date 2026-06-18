# Research Report: subset-b-005691

This grouped report covers the requested NFS client files under `sources/distributed-fs/ceph-client/fs/nfs/`. Each section preserves the source path and is bounded by the exact markers used by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/internal.h -->
# sources/distributed-fs/ceph-client/fs/nfs/internal.h

## Purpose
`internal.h` is the private integration header for the Linux NFS client implementation. It gathers cross-file declarations, mount/client context structures, inline state helpers, and small protocol-neutral utility routines used by NFSv2, NFSv3, NFSv4, pNFS, localio, direct I/O, page I/O, mount namespace handling, and superblock setup. It is the coordination point between version-specific modules and the common NFS client core.

## Important APIs, Types, And Functions
Key data types are `struct nfs_client_initdata`, which carries client construction inputs such as server address, protocol, timeout parameters, `nconnect`, network namespace, credentials, and transport security; `struct nfs_fs_context`, which stores parsed mount/reconfigure/submount state; `struct nfs_mount_request`, which is consumed by `mount_clnt.c`; `struct nfs_local_dio`, enabled for `CONFIG_NFS_LOCALIO`; and `struct nfs_direct_req`, which tracks direct I/O lifetime, completion, commit state, byte counts, errors, and flags.

The header declares the major common entry points: client/server allocation and lookup, RPC client setup, superblock creation and teardown, root/submount functions, read/write page-IO setup, commit handling, direct I/O helpers, mount namespace helpers, NFSv4 client discovery and trunking hooks, and localio hooks. Inline helpers include `nfs_attr_check_mountpoint()`, `nfs_lookup_is_soft_revalidate()`, `flags_to_mode()`, `nfs_file_block_o_direct()`, `nfs_io_gfp_mask()`, `nfs_should_remove_suid()`, `nfs_igrab_and_active()`, `nfs_block_size()`, `nfs_io_size()`, `nfs_super_set_maxbytes()`, `nfs_folio_length()`, `nfs_stateid_hash()`, and fatal-error classifiers.

## Control Flow And Integration Points
Most files in this work item include `internal.h` to bind into common client behavior. Version modules register through `struct nfs_subversion` from `nfs.h`, then use declarations here to allocate servers, clone submounts, decode directories, and dispatch `nfs_rpc_ops`. `io.c` implements the `nfs_start_io_*` functions declared here. `namespace.c` consumes the path and submount helpers. `mount_clnt.c` consumes `struct nfs_mount_request`. `localio.c` exports local open/read/write/commit helpers through the conditional declarations here. `nfs3proc.c` fills `nfs_v3_clientops` with common function pointers declared here.

## State And Persistence Behavior
The header does not persist state itself, but it defines the shapes and invariants of long-lived client state. `nfs_fs_context` persists mount configuration while a filesystem context is built. `nfs_client_initdata` seeds `struct nfs_client` instances stored in per-net lists. `nfs_direct_req` tracks async direct I/O until all requests and commits complete. Inline helpers mutate inode flags, cache-validity bits, page writeback accounting, and pNFS commit verifier state. `nfs_igrab_and_active()` and `nfs_iput_and_deactive()` couple inode references to superblock activity.

## Dependencies
This header depends on Linux VFS, fs_context, SunRPC, NFS page and XDR types, pNFS commit structures, security labels, user credentials, RCU/list locking, and optional build flags including `CONFIG_PROC_FS`, `CONFIG_NFS_V4`, `CONFIG_NFS_V4_2`, `CONFIG_NFS_V4_SECURITY_LABEL`, `CONFIG_NFS_LOCALIO`, `CONFIG_NFS_FSCACHE`, and `CONFIG_MIGRATION`.

## Risks And Edge Cases
Because this file centralizes declarations, signature drift is high risk across many compilation units. The direct I/O and buffered I/O helpers require correct `i_rwsem` ownership; callers that skip the start/end pairing can deadlock or corrupt cache semantics. Error classification affects retry and failover behavior. Size helpers clamp I/O sizes and superblock limits, so regressions can cap throughput or expose invalid offsets. Localio stubs must preserve behavior when the feature is disabled.

## Test Signals
Useful signals include build coverage across NFSv2, NFSv3 ACL, NFSv4, pNFS, migration, fscache, and localio configurations; xfstests over buffered/direct I/O transitions; mount option parsing and submount tests; pNFS commit verification; and lockdep/KCSAN checks around inode and superblock reference helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/io.c -->
# sources/distributed-fs/ceph-client/fs/nfs/io.c

## Purpose
`io.c` implements the inode-level synchronization that prevents NFS buffered I/O and direct I/O from running against the same file in incompatible modes. It is a small but central data-path helper used by file read/write and direct I/O code to serialize mode transitions using `inode->i_rwsem` and the `NFS_INO_ODIRECT` inode flag.

## Important APIs, Types, And Functions
The exported API is `nfs_start_io_read()`, `nfs_end_io_read()`, `nfs_start_io_write()`, `nfs_end_io_write()`, `nfs_start_io_direct()`, and `nfs_end_io_direct()`. `nfs_start_io_read()` obtains a killable read lock and ensures direct I/O is blocked; if direct I/O is active, it upgrades through a write lock, clears `NFS_INO_ODIRECT`, waits for in-flight direct I/O via `inode_dio_wait()`, then downgrades. `nfs_start_io_write()` takes the write lock and blocks direct I/O. `nfs_start_io_direct()` does the inverse: it ensures `NFS_INO_ODIRECT` is set, syncing the mapping to drain buffered data before downgrading to a shared lock. `nfs_block_buffered()` is the local helper that sets the direct-I/O flag and calls `nfs_sync_mapping()`.

## Control Flow And Integration Points
Buffered reads can run concurrently under a shared `i_rwsem` lock once the inode is not in direct-I/O mode. Buffered writes take the exclusive lock and therefore serialize with buffered reads and direct I/O transitions. Direct I/O similarly uses a shared lock while active, but only after an exclusive transition that sets `NFS_INO_ODIRECT` and flushes cached data. The public functions are declared in `internal.h` and called by the NFS file/direct I/O paths.

## State And Persistence Behavior
The persistent state is the `NFS_INO_ODIRECT` bit in `struct nfs_inode::flags`. It represents the current I/O mode barrier, not a permanent mount setting. The start functions hold `i_rwsem` until the paired end function runs. `nfs_block_buffered()` also pushes dirty page-cache state to the server before direct I/O proceeds.

## Dependencies
The file depends on VFS inode locking, NFS inode state, `nfs_sync_mapping()`, killable rwsems, direct-I/O wait helpers, and the inline `nfs_file_block_o_direct()` from `internal.h`.

## Risks And Edge Cases
The main risk is unmatched start/end calls, which would leak `i_rwsem` locks. Interruptible lock acquisition returns errors and callers must stop the I/O path. Mode transitions are subtle: direct I/O must not start without flushing buffered data, and buffered I/O must not start without waiting for direct I/O completion. Write paths also interact with truncate serialization via the exclusive lock.

## Test Signals
Exercise mixed buffered and `O_DIRECT` reads/writes on the same file, concurrent direct writers and buffered readers, interrupted tasks waiting for `i_rwsem`, writeback behavior during direct transitions, and lockdep under stress. xfstests direct I/O and mmap/writeback cases are especially relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/iostat.h -->
# sources/distributed-fs/ceph-client/fs/nfs/iostat.h

## Purpose
`iostat.h` defines the NFS client per-mount I/O statistics storage and fast-path update helpers. It provides cacheline-aligned per-CPU counters for byte and event statistics so common I/O paths can update mount statistics with low contention.

## Important APIs, Types, And Functions
`struct nfs_iostats` contains `bytes[__NFSIOS_BYTESMAX]` and `events[__NFSIOS_COUNTSMAX]`, aligned to a cacheline. `nfs_inc_server_stats()` increments an event counter on the current CPU for a `struct nfs_server`; `nfs_inc_stats()` derives the server from an inode. `nfs_add_server_stats()` and `nfs_add_stats()` add byte counts. `nfs_alloc_iostats()` is deliberately a macro around `alloc_percpu(struct nfs_iostats)` so allocations get distinct accounting tags. `nfs_free_iostats()` safely frees non-null per-CPU storage.

## Control Flow And Integration Points
The helpers are inlined into I/O and RPC completion paths such as `nfs3proc.c`, where `nfs3_async_handle_jukebox()` increments `NFSIOS_DELAY`. Superblock/server allocation code is expected to allocate the per-CPU structure, and stats reporting code folds per-CPU values when exposing mount statistics.

## State And Persistence Behavior
Counters persist for the lifetime of the mounted `nfs_server` object. Updates are per-CPU and not individually synchronized, trading exact instantaneous reads for low overhead on hot paths. State is memory-resident only and reset when the server object is destroyed.

## Dependencies
The header depends on Linux per-CPU allocation, cacheline alignment, `linux/nfs_iostat.h` counter enumerations, and the `NFS_SERVER(inode)` accessor.

## Risks And Edge Cases
Callers assume `server->io_stats` is allocated. Mis-sized counter enumerations or use after server teardown would corrupt memory. Because counters are per-CPU, readers must aggregate correctly and tolerate concurrent updates. The `long addend` byte helper should only be used with sane positive or intentional signed deltas.

## Test Signals
Mount statistics should change under reads, writes, readdir, commits, retries, and server delay cases. Build-time coverage should catch enum size mismatch. Runtime tests should include mount teardown under active I/O and stats reads while workloads run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/iostat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/localio.c -->
# sources/distributed-fs/ceph-client/fs/nfs/localio.c

## Purpose
`localio.c` implements NFS client support for bypassing the network path when the NFS server is local to the same kernel. It probes server locality using the `nfslocalio` auxiliary RPC program, opens local filehandles through nfsd helpers, performs reads/writes using VFS `read_iter` and `write_iter`, and maps results back into normal NFS page-IO and commit completion callbacks.

## Important APIs, Types, And Functions
Important private types are `struct nfs_local_kiocb`, which wraps a kernel `kiocb`, bvec array, page-IO header, local nfsd file, work item, and up to three `iov_iter` segments; and `struct nfs_local_fsync_ctx`, which carries local commit/fsync work. Exported functions include `nfs_server_is_local()`, `nfs_local_probe_async_work()`, `nfs_local_probe_async()`, `nfs_local_open_fh()`, `nfs_local_doio()`, and `nfs_local_commit()`.

Locality is probed by `nfs_init_localioclient()`, `nfs_server_uuid_is_local()`, and `nfs_local_probe()`. I/O setup is handled by `nfs_local_iocb_alloc()`, `nfs_is_local_dio_possible()`, `nfs_local_iters_setup_dio()`, and `nfs_local_iters_init()`. Completion flows through `nfs_local_pgio_done()`, `nfs_local_pgio_release()`, and read/write-specific completion helpers. Writes also update verifiers through `nfs_set_local_verifier()` and collect post-write attrs with `nfs_local_vfs_getattr()`. Commits run `vfs_fsync_range()` in `nfs_local_fsync_work()`.

## Control Flow And Integration Points
The probe path is asynchronous on `nfsiod_workqueue` and requires `localio_enabled`, `AUTH_SYS`, and a successful `UUID_IS_LOCAL` RPC response with initialized local UUID fields. Open uses `nfs_open_local_fh()` and disables/reprobes localio on selected stale/local-open failures. Read/write I/O obtains the underlying file from the nfsd file, builds bvec iterators from the NFS page array, optionally splits direct I/O into misaligned start, aligned middle, and misaligned end segments, then queues actual VFS I/O on `nfslocaliod_workqueue`. On completion it calls the same RPC call-done/release callbacks normal network I/O would use.

## State And Persistence Behavior
Global `localio_enabled` gates all use. Per-client locality is represented by `clp->cl_uuid` state accessed with RCU helpers and `nfs_uuid_begin/end`. Opened local files are reference-counted nfsd files and released through `nfs_local_file_put()`. `nfs_local_kiocb` state lives until all iter segments complete. Boot verifiers are stored in `cl_nfssvc_boot` under `cl_boot_lock` and reset on write/commit errors to make unstable-write verification conservative.

## Dependencies
The implementation depends on nfsd local-file APIs from `linux/nfslocalio.h`, SunRPC program binding, VFS file operations, workqueues, bvec/iov_iter helpers, credential scoping, tracepoints, pNFS/NFS page-IO types, and NFSv3/NFSv4 stable-write verifier semantics.

## Risks And Edge Cases
Direct I/O alignment is the riskiest area: incorrect split boundaries or callback ordering can produce short I/O, unexpected `-EINVAL`, or page-IO completion before all segments finish. The file explicitly clears `hdr->res.replen` after local reads to avoid NFSv3 corruption if future I/O returns to RPC. Write paths must restore task flags after `PF_LOCAL_THROTTLE | PF_MEMALLOC_NOIO`. Localio must disable itself after local server restart or stale handles and avoid using non-`READ`/`WRITE` modes.

## Test Signals
Tests should cover enabling/disabling the module parameter, AUTH_SYS versus non-AUTH_SYS mounts, local server restart, read/write fallback after localio disablement, mixed direct and buffered localio, short reads/writes, stable and unstable writes, commit/fsync ranges, and xfstests comparing localio results against normal RPC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/localio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/mount_clnt.c -->
# sources/distributed-fs/ceph-client/fs/nfs/mount_clnt.c

## Purpose
`mount_clnt.c` is the in-kernel client for the auxiliary MOUNT protocol used by NFSv2 and NFSv3 mounts. It contacts mountd, sends an export path, receives the root filehandle, decodes server-supported authentication flavors for MOUNTv3, and normalizes MOUNT protocol status codes to Linux errno values.

## Important APIs, Types, And Functions
The public entry point is `nfs_mount(struct nfs_mount_request *info, int timeo, int retrans)`. It validates path length, builds an `rpc_create_args` for program `NFS_MNT_PROGRAM`, initializes timeout values, optionally uses a non-privileged source port, selects either `MOUNTPROC_MNT` or `MOUNTPROC3_MNT`, performs a soft synchronous RPC, and fills `info->fh` plus auth flavor output arrays.

Private helpers encode the directory path (`encode_mntdirpath()`, `mnt_xdr_enc_dirpath()`), decode MOUNTv1 status and filehandles (`decode_status()`, `decode_fhandle()`, `mnt_xdr_dec_mountres()`), and decode MOUNTv3 status, variable-length filehandles, and auth flavors (`decode_fhs_status()`, `decode_fhandle3()`, `decode_auth_flavors()`, `mnt_xdr_dec_mountres3()`). Procedure tables `mnt_procedures` and `mnt3_procedures` drive SunRPC dispatch.

## Control Flow And Integration Points
Mount setup code passes an `nfs_mount_request` from `internal.h`. `nfs_mount()` creates a temporary RPC client, makes exactly one mount call using caller-provided retry policy, shuts down the client, and returns either a populated filehandle or errno. If a MOUNTv3 server returns no auth flavor list, or if using older MOUNT protocol, the code fakes a permissive one-entry list with `RPC_AUTH_NULL`, allowing later NFS security negotiation to continue.

## State And Persistence Behavior
The file itself keeps only static RPC metadata and per-procedure counters. Runtime state is transient: a temporary mount RPC client, stack `struct mountres`, caller-owned filehandle, and caller-owned auth flavor arrays. The resulting filehandle becomes persistent mount state outside this file.

## Dependencies
Dependencies include SunRPC client creation/call/shutdown, XDR stream helpers, kernel socket address structures, `nfs_init_timeout_values()`, `NFS_MAX_SECFLAVORS`, `NFS2_FHSIZE`, `NFS3_FHSIZE`, and mount protocol constants.

## Risks And Edge Cases
Path length is capped at `MNTPATHLEN` before RPC. Unknown status values map to `-EACCES`, which is conservative but may hide server-specific details. MOUNTv3 filehandles with size zero or too large are rejected and translated to `-EBADHANDLE` through `res->errno`. Auth flavor decoding caps the server-provided list to `NFS_MAX_SECFLAVORS` and the caller-provided buffer; callers must initialize `auth_flav_len` correctly.

## Test Signals
Exercise NFSv2 and NFSv3 mounts, long export paths, servers returning no auth flavors, more auth flavors than the cap, malformed or zero-length handles, `noresvport`, TCP/UDP timeout parameters, and mountd errors such as access denied, not directory, unsupported, and stale export paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/mount_clnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/namespace.c -->
# sources/distributed-fs/ceph-client/fs/nfs/namespace.c

## Purpose
`namespace.c` handles NFS namespace path reconstruction and automatic client submounts when crossing server-side filesystem boundaries or NFSv4 referrals. It also manages expiry of NFS automounts and exposes a module parameter controlling the expiry timeout.

## Important APIs, Types, And Functions
`nfs_path()` reconstructs a server pathname from a dentry by walking parents under RCU and `rename_lock`, prepending the root dentry's `d_fsdata` export path, and optionally canonicalizing slashes. `nfs_d_automount()` creates a submount filesystem context, inherits parent mount flags, credentials, network namespace, protocol version, server address, port, and selected NFS module, then calls the version-specific `submount` method and creates a mount. `nfs_do_submount()` clones an `nfs_server`, builds a source string with `nfs_devname()`, parses it into the filesystem context, and calls `vfs_get_tree()`. `nfs_submount()` performs a fresh lookup to populate the mount filehandle and attributes before delegating to `nfs_do_submount()`.

The file also defines `nfs_mountpoint_inode_operations`, `nfs_referral_inode_operations`, `nfs_expire_automounts()`, `nfs_release_automount_timer()`, and custom `param_set_nfs_timeout()` / `param_get_nfs_timeout()` handlers.

## Control Flow And Integration Points
Automount starts from VFS dentry operations via `nfs_d_automount()`. A new fs_context is created with `fs_context_for_submount()`, NFS-specific clone data is filled, and `client->rpc_ops->submount()` is called. For normal NFSv3-style boundaries, `nfs_submount()` revalidates the child by lookup. The created mount is placed on `nfs_automount_list` and a delayed work item calls `mark_mounts_for_expiry()`.

## State And Persistence Behavior
Persistent state includes the global `nfs_automount_list`, `nfs_automount_task`, and `nfs_mountpoint_expiry_timeout`. Per-submount state lives in `struct nfs_fs_context` until mount creation and then in the cloned `nfs_server` and superblock. `nfs_path()` is read-only apart from returning a pointer into the caller buffer.

## Dependencies
The file depends on VFS dcache/mount/fs_context APIs, NFS client/server structures, `nfs_alloc_fattr()`, `nfs_clone_server()`, RPC ops, module parameters, workqueues, and parent dentry locking conventions.

## Risks And Edge Cases
Path reconstruction races with rename and must retry on sequence mismatch. Buffer exhaustion returns `-ENAMETOOLONG`. Root automount attempts return `-ESTALE`. `nfs_d_automount()` manually transfers credentials and network namespace references; mistakes leak or under-reference them. Submounts deliberately inherit only `NFS_SB_MASK` flags. Timeout parameter changes can cancel or reschedule expiry work while mounts remain on the list.

## Test Signals
Test nested exports, NFSv4 referrals, rename races while reading `/proc/mounts`, source path canonicalization, automount expiry disabled/enabled, root mountpoint handling, network namespace propagation, and security flavor inheritance across submounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/netns.h -->
# sources/distributed-fs/ceph-client/fs/nfs/netns.h

## Purpose
`netns.h` defines NFS-private per-network-namespace state accessed through `net_generic()` and `nfs_net_id`. It keeps NFS client lists, callback identity state, block-layout upcall state, RPC stats, and optional procfs roots isolated per network namespace.

## Important APIs, Types, And Functions
`struct bl_dev_msg` represents a block-layout device upcall reply with status and major/minor numbers. `struct nfs_net` is the primary type. It includes DNS resolver cache state, block device pipe/reply/wait/mutex fields, `nfs_client_list`, `nfs_volume_list`, NFSv4-only callback IDR and callback ports, callback user counts by minor version, data-server cache and lock, a namespace-level `nfs_netns_client`, `nfs_client_lock`, boot time, RPC stats, and optional procfs entry.

## Control Flow And Integration Points
Client allocation, lookup, trunking discovery, sysfs/procfs reporting, callback service setup, and pNFS data-server cache management use `struct nfs_net`. In this work item, `nfs40client.c` obtains `struct nfs_net` to manipulate `cb_ident_idr` and walk `nfs_client_list`; `nfs3client.c` includes the header for namespace integration; `internal.h` declares procfs init/exit hooks that populate namespace state.

## State And Persistence Behavior
All fields live for the lifetime of the network namespace. Lists and IDRs are protected by `nfs_client_lock` or other field-specific locks. `boot_time` provides namespace-level timing context. Callback port/user fields persist while NFSv4 callback services are active.

## Dependencies
Dependencies include network namespace generic storage, SunRPC stats and pipes, NFSv4 constants, Linux IDR/list/spinlock/mutex/waitqueue primitives, and procfs when enabled.

## Risks And Edge Cases
Per-net isolation is critical; using global state instead would leak clients across namespaces. Lock ordering around `nfs_client_lock`, callback ID replacement, and list walking must remain consistent. Optional NFSv4 fields are compile-time gated, so non-v4 builds must not reference them.

## Test Signals
Run mounts in multiple network namespaces, NFSv4 callback setup and teardown, trunking discovery under namespace isolation, pNFS data-server cache operations, procfs visibility per namespace, and lockdep on client list and callback IDR operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/netns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs.h -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs.h

## Purpose
`nfs.h` is the small public-private interface between the common NFS module and version-specific NFS modules. It defines how NFSv2, NFSv3, and other subversions register their filesystem, RPC version, operation vector, superblock operations, and xattr handlers.

## Important APIs, Types, And Functions
`struct nfs_subversion` carries `owner`, `nfs_fs`, `rpc_vers`, `rpc_ops`, `sops`, and optional `xattr` handler pointers. The declared registry API is `find_nfs_version()`, `get_nfs_version()`, `put_nfs_version()`, `register_nfs_version()`, and `unregister_nfs_version()`.

## Control Flow And Integration Points
Version modules such as `nfs2super.c` and `nfs3super.c` define a static `struct nfs_subversion`, fill it with their version-specific `rpc_version` and `nfs_rpc_ops`, and register it at module init. Mount parsing and server creation can then locate the requested version and hold a module reference through `get_nfs_version()`.

## State And Persistence Behavior
The file defines no state directly. Registered `nfs_subversion` objects persist for the lifetime of their modules. The `owner` module pointer is part of the lifetime contract that prevents use after unload while a version is active.

## Dependencies
The interface depends on VFS `file_system_type`, SunRPC scheduling/RPC version types, NFS XDR declarations, and the common `struct nfs_rpc_ops` contract.

## Risks And Edge Cases
Incorrect registration or missing module reference handling can lead to unsupported version lookup failures or module unload races. Optional `xattr` handlers must match version capabilities. Because this header is included by version modules, ABI-like changes affect all NFS version registrations.

## Test Signals
Build and load/unload NFSv2 and NFSv3 modules, mount explicit protocol versions, verify unsupported versions fail cleanly, and test module unload refusal while mounts are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs2super.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs2super.c

## Purpose
`nfs2super.c` registers NFSv2 client support as a version-specific module. It binds the common NFS filesystem type and super operations to the NFSv2 RPC version and client operation vector.

## Important APIs, Types, And Functions
The file defines static `struct nfs_subversion nfs_v2` with `THIS_MODULE`, `&nfs_fs_type`, `&nfs_version2`, `&nfs_v2_clientops`, and `&nfs_sops`. `init_nfs_v2()` registers that subversion. `exit_nfs_v2()` unregisters it. Module metadata declares GPL licensing and the description.

## Control Flow And Integration Points
At module init, `register_nfs_version(&nfs_v2)` makes NFSv2 discoverable through the registry declared in `nfs.h`. The common mount path can then select NFSv2, use `nfs_version2` from `nfs2xdr.c` for RPC procedure metadata, and call `nfs_v2_clientops` from the common v2 client implementation. Module exit removes the version from lookup.

## State And Persistence Behavior
The only state is the static registration object. Its lifetime is the module lifetime, guarded by the version registry and module owner reference.

## Dependencies
The module depends on `nfs_fs_type`, `nfs_sops`, `nfs_version2`, and `nfs_v2_clientops` from the broader NFS client implementation.

## Risks And Edge Cases
Registration must happen exactly once, and unregister must match init. Missing or mismatched operation vectors would produce mount-time failures. NFSv2 has narrower protocol semantics, so callers must not assume v3/v4 capabilities when this subversion is selected.

## Test Signals
Build with NFSv2 enabled, load/unload the module, mount an NFSv2 export, confirm `/proc` or mount stats identify v2 RPCs, and verify NFSv3-only features such as ACLs are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs2super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs2xdr.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs2xdr.c

## Purpose
`nfs2xdr.c` implements XDR encoding and decoding for NFSv2 RPC arguments and results. It defines the RPC procedure table `nfs_procedures[]` and `nfs_version2`, which the NFSv2 module registers through `nfs2super.c`.

## Important APIs, Types, And Functions
The file provides low-level codecs for fixed NFSv2 filehandles, attributes, times, filenames, paths, read/write data, directory entries, and statfs results. It translates uid/gid values through the RPC client's user namespace. Publicly consumed symbols are `nfs2_decode_dirent()` and `nfs_version2`; `nfs_procedures[]` is declared in `internal.h`.

Encoders include `nfs2_xdr_enc_fhandle()`, `nfs2_xdr_enc_sattrargs()`, `nfs2_xdr_enc_diropargs()`, `nfs2_xdr_enc_readlinkargs()`, `nfs2_xdr_enc_readargs()`, `nfs2_xdr_enc_writeargs()`, create/remove/rename/link/symlink encoders, and `nfs2_xdr_enc_readdirargs()`. Decoders include status, attrstat, diropres, readlink, read, write, readdir, and statfs result handlers.

## Control Flow And Integration Points
Each RPC operation in `nfs_procedures[]` maps an NFSv2 procedure number to an encoder, decoder, argument size, reply size, timer class, and stat index. Read and readlink replies prepare page-backed receive buffers and use `xdr_read_pages()`. Write and symlink paths mark XDR buffers as write-backed. Directory replies are stored raw in the page cache; `nfs2_decode_dirent()` later decodes entries during readdir iteration.

## State And Persistence Behavior
The file keeps static procedure metadata and per-procedure counters in `nfs_version2_counts`. Runtime decoded state is written into caller-provided `nfs_fattr`, `nfs_fh`, `nfs_pgio_res`, `nfs_entry`, or statfs structures. NFSv2 read replies have no EOF flag, so `decode_nfsdata()` clears `result->eof`.

## Dependencies
Dependencies include SunRPC XDR streams, NFSv2 protocol constants, NFS common errno/status translation, page-cache reply buffers, user namespace uid/gid conversion, tracepoints, and common NFS attribute helpers from `internal.h`.

## Risks And Edge Cases
NFSv2 has 32-bit offsets, sizes, cookies, and fixed 32-byte filehandles. The decoder clamps cheating read servers that claim more data than received. Path and filename length checks must be exact; malformed replies return `-EIO` or `-ENAMETOOLONG`. FIFO special handling maps the historical NFSv2 FIFO device convention to `S_IFIFO`. Invalid uid/gid mappings reject attributes with `-EINVAL`.

## Test Signals
Test NFSv2 getattr/setattr/lookup/read/write/create/remove/rename/readdir/statfs, long names and paths, FIFO nodes, user namespace id mapping, short or malformed read replies, directory cookie iteration, and protocol table counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs2xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs3_fs.h -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs3_fs.h

## Purpose
`nfs3_fs.h` is the NFSv3-specific private header. It declares NFSv3 ACL operations, server creation/cloning helpers, and the NFSv3 subversion object used by module registration and pNFS data-server client setup.

## Important APIs, Types, And Functions
When `CONFIG_NFS_V3_ACL` is enabled, it declares `nfs3_get_acl()`, `nfs3_set_acl()`, `nfs3_proc_setacls()`, and `nfs3_listxattr()`. Without ACL support it provides a zero-success stub for `nfs3_proc_setacls()` and defines `nfs3_listxattr` as `NULL`. It also declares `nfs3_create_server()`, `nfs3_clone_server()`, and extern `struct nfs_subversion nfs_v3`.

## Control Flow And Integration Points
`nfs3client.c` implements server creation/cloning and ACL client initialization. `nfs3acl.c` implements the ACL functions when configured. `nfs3proc.c` installs ACL hooks into inode operations and calls `nfs3_proc_setacls()` after create/mkdir/mknod. `nfs3super.c` exports `nfs_v3` for registration and data-server setup.

## State And Persistence Behavior
This header holds no state. It controls compile-time behavior through configuration stubs, preserving common NFSv3 call sites even when ACL support is absent.

## Dependencies
The header depends on POSIX ACL types, NFS subversion registration, NFS filehandles/attributes, RPC auth flavors, and the common NFS server type.

## Risks And Edge Cases
The ACL-disabled stub returns success, which deliberately makes ACL setup a no-op; callers must not infer ACL support from `nfs3_proc_setacls()` alone. Declaration changes affect `nfs3client.c`, `nfs3acl.c`, `nfs3proc.c`, and `nfs3super.c`.

## Test Signals
Build with and without `CONFIG_NFS_V3_ACL`, verify xattr listing behavior, create files and directories with default ACLs, and confirm NFSv3 server cloning preserves or disables ACL capability correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs3_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs3acl.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs3acl.c

## Purpose
`nfs3acl.c` implements POSIX ACL get/set/list behavior for NFSv3 using the separate Sun NFS ACL protocol. It bridges Linux VFS ACL APIs and xattr listing to `ACLPROC3_GETACL` and `ACLPROC3_SETACL` RPCs.

## Important APIs, Types, And Functions
Public functions are `nfs3_get_acl()`, `nfs3_proc_setacls()`, `nfs3_set_acl()`, and `nfs3_listxattr()`. Cache-race helpers `nfs3_prepare_get_acl()`, `nfs3_complete_get_acl()`, and `nfs3_abort_get_acl()` use POSIX ACL sentinels so concurrent `get_acl()` callers coordinate correctly. `__nfs3_proc_setacls()` performs the actual RPC and page allocation for large ACL payloads. `nfs3_list_one_acl()` contributes ACL xattr names only if an ACL is present.

## Control Flow And Integration Points
`nfs3_get_acl()` rejects RCU mode, checks `NFS_CAP_ACLS`, revalidates inode change state, requests access and/or default ACLs as needed, allocates an fattr, installs cache sentinels, performs a synchronous call on `server->client_acl`, frees XDR-allocated pages, refreshes inode attributes, normalizes unsupported errors to `-EOPNOTSUPP`, and completes or aborts ACL cache updates. `nfs3_set_acl()` combines access/default ACL state for directories and synthesizes an access ACL from inode mode if needed before calling `__nfs3_proc_setacls()`.

## State And Persistence Behavior
ACL values are cached in `inode->i_acl` and `inode->i_default_acl`. `server->caps` can be modified to clear `NFS_CAP_ACLS` if the extension is not supported. Set operations zap the NFS access cache and ACL cache after the RPC. Temporary pages used for XDR payloads are always freed before return.

## Dependencies
The file depends on POSIX ACL core helpers, NFS ACL XDR structures, `server->client_acl` created in `nfs3client.c`, NFS inode revalidation/refresh helpers, page allocation, and the configured ACL procedure table in `nfs3xdr.c`.

## Risks And Edge Cases
ACL cache sentinel handling must be exact to avoid caching stale ACLs or leaking references. Unsupported server responses disable capability and are converted to Linux ACL semantics. `__nfs3_proc_setacls()` treats too many ACL entries as `-ENOSPC` and allocates pages only when inline buffers are insufficient. `nfs3_proc_setacls()` masks `-EOPNOTSUPP` as success so create paths do not fail solely due to missing ACL protocol support.

## Test Signals
Run ACL get/set/list xattr tests on files and directories, concurrent ACL lookups, servers without NFS ACL support, ACL payloads above inline size, ACL entry limit overflow, create/mkdir with inherited default ACLs, and cache invalidation after chmod/setfacl.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs3acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs3client.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs3client.c

## Purpose
`nfs3client.c` implements NFSv3-specific server/client setup beyond the common client allocator. It binds the optional NFSv3 ACL RPC program, creates/clones NFSv3 servers with ACL capability initialization, and constructs pNFS data-server clients that speak NFSv3.

## Important APIs, Types, And Functions
When ACL support is enabled, the file defines `nfsacl_program`, backed by `nfsacl_version3`, and `nfs_init_server_aclclient()`, which binds the NFS ACL program to the server's main RPC client and links it into sysfs. Public functions are `nfs3_create_server()`, `nfs3_clone_server()`, and exported `nfs3_set_ds_client()`.

`nfs3_set_ds_client()` builds `struct nfs_client_initdata` from a metadata server, data-server address/protocol, timeouts, credentials, network namespace, and transport security settings. It fakes a hostname from the data-server address because lockd expects one, propagates `nconnect` for selected transports, preserves no-reserved-port and network-unreachable-fatal flags, marks the client as a data-server client, initializes timeout values, and calls `nfs_get_client()`.

## Control Flow And Integration Points
Common server creation flows through `nfs_create_server()` and then `nfs_init_server_aclclient()`. Clone flows through `nfs_clone_server()` and reinitializes ACL only if the source had a valid ACL client. pNFS layouts call `nfs3_set_ds_client()` to obtain or reuse a data-server `nfs_client` matching address, port, version, and namespace.

## State And Persistence Behavior
ACL capability state is stored in `server->caps` and the bound `server->client_acl` RPC client. Data-server clients are regular `nfs_client` objects with `NFS_CS_DS` set and timeouts tuned for failback through the metadata server. Transport security is inherited for TLS only when the metadata client uses non-default transport security.

## Dependencies
Dependencies include SunRPC program binding, sysfs RPC client linking, NFSv3 ACL XDR version metadata, common server allocation/cloning, net namespace state, address formatting, handshake/TLS constants, and pNFS data-server client lookup.

## Risks And Edge Cases
If ACL binding fails, ACL capability is cleared and the mount continues. The non-ACL configuration clears `NFS_MOUNT_NOACL` and `NFS_CAP_ACLS`, making behavior explicit. `nfs3_set_ds_client()` must handle address-to-string failure, TLS downgrade to TCP when the metadata client lacks transport security, and careful timeout arithmetic. Wrong flag propagation could make pNFS data-server outages fatal instead of recoverable through the MDS.

## Test Signals
Test NFSv3 mounts with and without ACL support, ACL sysfs links, cloned submounts preserving ACL capability, pNFS data-server setup across TCP/RDMA/TLS, `nconnect`, no-reserved-port mounts, and data-server timeout/failover behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs3client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs3proc.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs3proc.c

## Purpose
`nfs3proc.c` implements the client-side NFSv3 procedure stubs and exports the `nfs_v3_clientops` operation vector consumed by common NFS VFS code. It translates VFS operations into NFSv3 RPC messages, handles post-op attribute refresh, ACL setup after object creation, lockd integration, localio probing, and NFSv3-specific retry behavior.

## Important APIs, Types, And Functions
The file defines per-procedure helpers for root/fsinfo, getattr, setattr, lookup/lookupp, access, readlink, create, remove/unlink, rename, link, symlink, mkdir, rmdir, readdir/readdirplus, mknod, statfs, fsinfo, pathconf, read/write/commit setup and completion, lock operations, and delegation stubs. `nfs3_rpc_wrapper()` wraps synchronous calls to retry `-EJUKEBOX` after `NFS_JUKEBOX_RETRY_TIME`; `nfs3_async_handle_jukebox()` restarts async calls and increments `NFSIOS_DELAY`.

`struct nfs3_createdata` bundles create-family RPC arguments, response filehandle/fattrs, and directory WCC attrs. `nfs3_alloc_createdata()`, `nfs3_do_create()`, and `nfs3_free_createdata()` support create, mkdir, symlink, and mknod flows. `nlmclnt_fl_close_lock_ops` integrates close-time unlock with NFS I/O counters.

## Control Flow And Integration Points
The `nfs_v3_clientops` table wires these functions into the common NFS client. Object creation first applies POSIX ACL creation rules, performs the NFSv3 RPC, then applies ACLs using `nfs3_proc_setacls()`. Exclusive create falls back from `EXCLUSIVE` to `GUARDED` to `UNCHECKED` if the server returns `-ENOTSUPP`, and then performs a post-create setattr for requested attributes. Read/write completion updates inode attributes and can trigger localio probing after successful normal RPC I/O. Readdir stores raw directory pages for later decoding by `nfs3_decode_dirent()`.

## State And Persistence Behavior
The file updates inode attribute caches through `nfs_refresh_inode()`, `nfs_post_op_update_inode()`, and `nfs_writeback_update_inode()`. Directory and file inode operation tables persist as static structures. `nfs3_localio_probe_throttle` is a module parameter that controls periodic localio reprobe. Close unlock paths temporarily hold open and lock contexts while waiting for outstanding I/O.

## Dependencies
Dependencies include SunRPC, NFSv3 XDR procedure metadata, NFS page I/O, POSIX ACLs, lockd/NLM, iostat counters, VFS inode operations, localio optional hooks, and common NFS helpers for dentry/inode/cache management.

## Risks And Edge Cases
`EJUKEBOX` retry loops must remain killable/freezable. Attribute refresh after failed operations relies on WCC data. Create fallback changes semantics and must not leak ACL references or dentry aliases. Localio probing is throttled with a power-of-two mask but the parameter text warns users must choose a power of two. Lock close handling must not release contexts before async unlock can wait for I/O. Delegation is mostly unsupported for v3, so return paths flush writes.

## Test Signals
Exercise all NFSv3 VFS operations, exclusive create fallback, ACL inheritance, readdirplus, server `EJUKEBOX`, softreval getattr/lookup timeouts, read/write/commit completions, lock/unlock on close with pending I/O, localio reprobe throttling, and xfstests over rename/link/remove WCC behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs3proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs3super.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs3super.c

## Purpose
`nfs3super.c` registers NFSv3 client support as a version-specific module. It binds the common NFS filesystem type and superblock operations to the NFSv3 RPC version, NFSv3 client operation vector, and optional NFSv3 xattr handlers.

## Important APIs, Types, And Functions
The file defines global `struct nfs_subversion nfs_v3` with `THIS_MODULE`, `&nfs_fs_type`, `&nfs_version3`, `&nfs_v3_clientops`, and `&nfs_sops`. `init_nfs_v3()` registers it, and `exit_nfs_v3()` unregisters it. Module metadata declares GPL licensing and an NFSv3 description.

## Control Flow And Integration Points
At module load, the common NFS version registry gains the NFSv3 subversion. Mount selection can then use `nfs_version3` from `nfs3xdr.c` and `nfs_v3_clientops` from `nfs3proc.c`. `nfs3client.c` references `nfs_v3` when creating pNFS data-server clients.

## State And Persistence Behavior
The static `nfs_v3` object persists for the module lifetime. Its `owner` field participates in module reference handling through `get_nfs_version()` and `put_nfs_version()`.

## Dependencies
The module depends on common NFS filesystem registration, `nfs3_fs.h`, `nfs_version3`, `nfs_v3_clientops`, and `nfs_sops`.

## Risks And Edge Cases
Registration/unregistration must pair cleanly. Since `nfs_v3` is non-static and used by data-server setup, its symbol lifetime matters. Incorrect operation vector binding would affect every NFSv3 mount and pNFS data server.

## Test Signals
Build and load/unload NFSv3 support, mount explicit `vers=3`, use pNFS data-server paths, verify NFSv3 procedure counters, and confirm module unload is blocked while NFSv3 mounts exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs3super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs3xdr.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs3xdr.c

## Purpose
`nfs3xdr.c` implements XDR encoding and decoding for NFSv3 and the optional NFSv3 ACL side protocol. It defines the NFSv3 RPC procedure table `nfs3_procedures[]`, `nfs_version3`, and, when configured, `nfsacl_version3`.

## Important APIs, Types, And Functions
The file contains size macros for each NFSv3 argument and reply shape, a file type mapping table, user namespace helpers, primitive codecs for integers, file IDs, names, paths, cookies, verifiers, filehandles, times, types, device numbers, attributes, weak cache consistency data, and post-op filehandles. Encoders cover GETATTR, SETATTR with optional guard, LOOKUP, ACCESS, READLINK, READ, WRITE, CREATE, MKDIR, SYMLINK, MKNOD, REMOVE, RENAME, LINK, READDIR, READDIRPLUS, COMMIT, GETACL, and SETACL. Decoders cover the matching result unions plus `nfs3_decode_dirent()`.

## Control Flow And Integration Points
NFSv3 procedure dispatch is table-driven through the `PROC()` macro at the end of the file. Read, readlink, readdir, and ACL get operations prepare page-backed receive buffers before RPC. Write and symlink encoders mark transmit buffers as page-backed writes. Result decoders first read `nfsstat3`, then decode success or failure arms, preserving post-op or WCC attributes even on errors. Directory replies are stored as raw XDR pages; `nfs3_decode_dirent()` later decodes entries, including readdirplus attributes and filehandles, during directory iteration.

## State And Persistence Behavior
Static state is limited to RPC procedure tables and per-procedure counters. Runtime state is written into caller-owned response structs. Attribute decoders set `NFS_ATTR_FATTR_V3`, WCC fields, pre-change values, mounted-on file IDs, and write verifier/stability values. `decode_read3resok()` records `eof`, byte count, and guards against mismatched opaque lengths. `nfs3_xdr_dec_read3res()` records `replen` so later reads can optimize header sizing.

## Dependencies
Dependencies include SunRPC XDR streams, NFSv3 protocol constants, NFS ACL encoding/decoding helpers, page buffers, user namespace uid/gid mapping, NFS common status-to-errno conversion, NFS tracepoints, and common helpers such as `nfs_timespec_to_change_attr()` and `nfs_umode_to_dtype()`.

## Risks And Edge Cases
Malformed XDR is common-risk surface: oversized names/paths/handles, invalid uid/gid mappings, bad stable write modes, mismatched read counts, invalid ACL masks, and missing post-op filehandles must be rejected or normalized. `nfs3_xdr_enc_setacl3args()` contains explicit `BUG_ON(error < 0)` comments, so invalid ACL marshalling would crash rather than return a recoverable error. Readdirplus must handle file ID mismatches by recording mounted-on fileid for mountpoint detection.

## Test Signals
Run NFSv3 protocol tests for every procedure, fuzz or fault-inject malformed XDR replies, exercise user namespaces, readdir and readdirplus caches, large ACL payloads, missing create filehandles that force lookup, WCC behavior after failures, write verifier changes, and read header-size caching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs3xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs40.h -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs40.h

## Purpose
`nfs40.h` declares the NFSv4.0 minor-version-specific client and recovery hooks shared between NFSv4.0 client setup and procedure handling files.

## Important APIs, Types, And Functions
The header declares `nfs40_shutdown_client()`, `nfs40_init_client()`, `nfs40_handle_cb_pathdown()`, extern `nfs_v4_0_minor_ops`, and `nfs40_discover_server_trunking()`.

## Control Flow And Integration Points
`nfs40client.c` implements client initialization, shutdown, callback path-down handling, and server trunking discovery. `nfs40proc.c` exports `nfs_v4_0_minor_ops`, which references those functions and installs NFSv4.0 sequence, lease renewal, migration, and recovery behavior into the common NFSv4 code.

## State And Persistence Behavior
The header holds no state directly. It exposes functions that allocate/free the NFSv4.0 slot table, update client callback state, and participate in client ID/trunking state transitions.

## Dependencies
Dependencies include NFSv4 client structures, credentials, and the `struct nfs4_minor_version_ops` type from the broader NFSv4 implementation.

## Risks And Edge Cases
Because this header separates NFSv4.0 behavior from later minor versions, declarations must match implementation exactly. The trunking discovery API returns either an existing client or the probed client; callers must honor reference and readiness semantics.

## Test Signals
Build NFSv4.0, mount `vers=4,minorversion=0`, trigger callback path-down recovery, exercise trunked server discovery, and run state recovery after server reboot and lease expiry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs40client.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs40client.c

## Purpose
`nfs40client.c` implements NFSv4.0 client initialization, shutdown, callback-path recovery, and server trunking discovery. It handles the NFSv4.0 client ID confirmation model and callback identifier swapping when two transports are discovered to reach the same server.

## Important APIs, Types, And Functions
`nfs40_init_client()` allocates and initializes a transport slot table for NFSv4.0. `nfs40_shutdown_client()` tears it down. `nfs40_handle_cb_pathdown()` marks the lease expired and returns all delegations after `NFS4ERR_CB_PATH_DOWN`; `nfs4_schedule_path_down_recovery()` also schedules the state manager. `nfs40_discover_server_trunking()` sends `SETCLIENTID`, stores the returned clientid/confirm verifier, and delegates to `nfs40_walk_client_list()` to find an existing matching client. `nfs4_swap_callback_idents()` updates per-net callback IDR ownership if the kept client should inherit the callback ident learned by the dropped client.

## Control Flow And Integration Points
Trunking discovery uses the per-net `nfs_client_list` and `cb_ident_idr` from `netns.h`. `nfs40_walk_client_list()` walks existing clients, uses `nfs4_match_client()` for owner/address matching, performs `SETCLIENTID_CONFIRM` against candidates, and on success returns a referenced existing client, swaps callback identifiers, updates `cl_confirm`, and marks the client ready. Timeout or restart cases schedule callback path recovery.

## State And Persistence Behavior
Persistent state affected includes `cl_slot_tbl`, `cl_clientid`, `cl_confirm`, `cl_cb_ident`, `cl_state`, delegation state, per-net callback IDR entries, and client refcounts. Discovery deliberately treats the newly allocated client as the last list item and may return a different existing client.

## Dependencies
Dependencies include NFSv4 session/slot helpers, callback service state, delegation expiration, per-network namespace state, state manager scheduling, SETCLIENTID/CONFIRM procedures, and client refcount/list locking.

## Risks And Edge Cases
Callback identifier swaps must be protected by `nfs_client_lock` and keep IDR entries consistent. Confirm verifiers are used to avoid false trunking matches when servers coincidentally return the same clientid-like data. Reference handling around `prev`, `pos`, and `result` is subtle. If callback path changes inadvertently, recovery must be scheduled to avoid stale delegation behavior.

## Test Signals
Test NFSv4.0 mounts, multi-address trunking discovery, callback channel changes, delegation return after `CB_PATH_DOWN`, slot table allocation failure, server reboot during trunking discovery, and list/refcount validation with lockdep/KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs40client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs40proc.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs40proc.c

## Purpose
`nfs40proc.c` defines NFSv4.0 minor-version operations for sequence slot handling, lease renewal, migration recovery, lock-owner release, and state recovery policy. It exports `nfs_v4_0_minor_ops` for the common NFSv4 client core.

## Important APIs, Types, And Functions
Key helpers are `nfs40_call_sync_prepare()` and `nfs40_call_sync_done()` for sequence setup/completion, `nfs40_sequence_free_slot()` and `nfs40_sequence_done()` for slot return, `nfs40_open_expired()` for expired open recovery without delegation recovery, `nfs4_proc_async_renew()` and `nfs4_proc_renew()` for lease renewal, `_nfs40_proc_get_locations()` and `_nfs40_proc_fsid_present()` for migration/lease-moved recovery, and `nfs4_release_lockowner()` with its async call ops.

Static operation tables include `nfs40_call_sync_ops`, `nfs40_sequence_slot_ops`, reboot and no-grace recovery ops, state renewal ops, migration recovery ops, and the exported `nfs_v4_0_minor_ops`.

## Control Flow And Integration Points
NFSv4.0 compound calls use sequence setup and slot freeing even though v4.0 sequencing differs from v4.1 sessions. Async renew allocates `nfs4_renewdata`, holds a client ref, calls RENEW with timeout, updates or schedules recovery based on status, and reschedules renewal on release if the client remains referenced. Migration recovery compounds append RENEW to signal the server and refresh leases. Lock-owner release initializes a sequence, sends `RELEASE_LOCKOWNER`, handles lease-related errors, and frees lock state on release.

## State And Persistence Behavior
The file mutates slot table state, NFSv4 state flags, lease timestamps, client refs, lock-owner state, and migration recovery status. `nfs40_test_and_free_expired_stateid()` always returns `-NFS4ERR_BAD_STATEID`, reflecting v4.0 limitations. `nfs40_open_expired()` clears delegation state IDs before reopening expired state.

## Dependencies
Dependencies include NFSv4 XDR procedure tables, sequence/session helpers, lease renewal helpers, migration and fs_locations structures, state recovery machinery, delegation clearing, lock-state lifetime helpers, and NFSv4 tracepoints.

## Risks And Edge Cases
Slot freeing must wake waiters or free slots under the slot-table lock. Async renewal must not reschedule after shutdown and must distinguish `LEASE_MOVED`, `CB_PATH_DOWN`, and normal lease recovery. Migration calls must renew leases only after successful compounds. Lock-owner release is NFSv4.0-only and must ignore later minor versions. Incorrect state recovery ops would break reboot or no-grace recovery.

## Test Signals
Exercise NFSv4.0 lease renewal, server reboot recovery, lease moved migration, callback path down, expired open and lock recovery, lock-owner release after unlock/close, slot table saturation, and fault injection on RENEW, FS_LOCATIONS, FSID_PRESENT, and RELEASE_LOCKOWNER.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs40proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs42.h -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs42.h

## Purpose
`nfs42.h` declares NFSv4.2 client procedure entry points and small helpers for newer protocol features: server-side allocation/deallocation, copy/clone, seek, layout stats/errors, copy notify, and extended attributes.

## Important APIs, Types, And Functions
When `CONFIG_NFS_V4_2` is enabled, declarations include `nfs42_proc_allocate()`, `nfs42_proc_copy()`, `nfs42_proc_deallocate()`, `nfs42_proc_zero_range()`, `nfs42_proc_llseek()`, `nfs42_proc_layoutstats_generic()`, `nfs42_proc_clone()`, `nfs42_proc_layouterror()`, `nfs42_proc_copy_notify()`, `nfs42_proc_getxattr()`, `nfs42_proc_setxattr()`, `nfs42_proc_listxattrs()`, and `nfs42_proc_removexattr()`. `nfs42_files_from_same_server()` compares NFSv4 server owner major IDs for copy/clone eligibility. `nfs42_listxattr_xdrsize()` estimates the maximum XDR buffer needed for a user xattr list buffer.

## Control Flow And Integration Points
This header is consumed by NFSv4 file, xattr, pNFS, and copy offload code. The file-same-server helper derives `nfs_client` objects from input and output file inodes and calls `nfs4_check_serverowner_major_id()`. The listxattr sizing helper assumes worst-case one-character user xattr names, includes null terminators and EOF word, and rounds to four-byte alignment.

## State And Persistence Behavior
The header defines no state. Its functions operate on files, inodes, pNFS layout segments, stateids, and NFS servers owned elsewhere. Constants `PNFS_LAYOUTSTATS_MAXDEV` and `READ_PLUS_SCRATCH_SIZE` guide bounded compound and scratch-buffer sizing.

## Dependencies
Dependencies include Linux xattr definitions, NFSv4 server owner identity, pNFS layout structures, NFSv4.2 operation implementations, and conditional compilation under `CONFIG_NFS_V4_2`.

## Risks And Edge Cases
The layoutstats maximum is explicitly marked as a FIXME, so scaling to more devices per compound is a known limitation. `nfs42_files_from_same_server()` checks owner identity, not path or export identity, and must be used in contexts where that is the right criterion. `nfs42_listxattr_xdrsize()` is a sizing upper bound; incorrect assumptions could under-allocate listxattr XDR buffers.

## Test Signals
Build with and without NFSv4.2, test fallocate/punch-zero/copy/clone/llseek xfstests, pNFS layoutstats and layouterror paths, xattr get/set/list/remove, same-server and cross-server copy decisions, and listxattr buffers with many short names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs42.h -->
