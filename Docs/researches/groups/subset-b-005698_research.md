# Research: subset-b-005698

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/proc.c -->
## sources/distributed-fs/ceph-client/fs/nfs/proc.c

Purpose: implements the NFSv2 client RPC operation table, translating VFS/NFS core calls into `NFSPROC_*` RPCs. Important entry points include `nfs_proc_get_root`, `nfs_proc_getattr`, `nfs_proc_setattr`, `nfs_proc_lookup`, create/mkdir/mknod/remove/link/symlink/rmdir/readdir/statfs/fsinfo/pathconf wrappers, NFSv2 read/write setup and completion hooks, lock helpers, and the exported `nfs_v2_clientops`.

Control flow is mostly synchronous RPC setup: build protocol args, initialize fattrs, call `rpc_call_sync`, then invalidate/revalidate affected dentries or inodes. Read and write operations integrate with generic pageio through callbacks rather than issuing the RPC directly here. State behavior is cache/coherency oriented: directory mutations call `nfs_mark_for_revalidate`, reads invalidate atime and synthesize EOF, writes force `NFS_FILE_SYNC`, and NFSv2 has no commit/delegation support. Dependencies include SunRPC, lockd/NLM, `internal.h`, XDR procedure tables, and shared NFS pageio structures. Risks are NFSv2 limits: 32-bit lock bounds, no ACCESS procedure, no COMMIT, symlink path length caps, and fallback auth behavior on root getattr/statfs. Test signals: NFSv2 mount, file creation/removal/rename/link/symlink, readdir, statfs, read/write short-transfer paths, and lock range rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/read.c -->
## sources/distributed-fs/ceph-client/fs/nfs/read.c

Purpose: NFS client buffered read and readahead implementation over folios, pageio, netfs, and optional pNFS layouts. Main APIs include `nfs_pageio_init_read`, `nfs_pageio_complete_read`, `nfs_pageio_reset_read_mds`, `nfs_read_alloc_scratch`, `nfs_read_folio`, `nfs_readahead`, and read-page cache init/destroy.

Control flow starts from `nfs_read_folio` or `nfs_readahead`, flushes conflicting writes, checks stale inode state, tries netfs, then falls back to `nfs_read_add_folio` plus `nfs_pageio_complete_read`. RPC completion calls protocol `read_done`, accounts bytes, handles `-ESTALE`, short reads, EOF zero-fill, uptodate marking, and folio unlock. State is transient in `nfs_pgio_header`, `nfs_page` groups, open-context error slots, folio uptodate/lock bits, per-inode stats, and optional scratch buffers. Dependencies include `nfs_pageio`, `netfs`, pNFS layout drivers, fscache, delegation atime updates, and tracepoints. Risks include correct EOF zeroing, short-read retry progress, context error propagation, stale inode handling, and pNFS retry-through-MDS behavior. Test signals: single-folio reads, readahead, EOF partial-page reads, server short reads, stale file handles, pNFS read fallback, and cache/netfs enabled and disabled paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/super.c -->
## sources/distributed-fs/ceph-client/fs/nfs/super.c

Purpose: core NFS client superblock, filesystem registration, mount display, mount negotiation, statfs, remount validation, and teardown logic. Important exported APIs include `nfs_sops`, `register_nfs_fs`, `unregister_nfs_fs`, `nfs_sb_active`, `nfs_sb_deactive`, `nfs_client_for_each_server`, `nfs_statfs`, `nfs_show_options`, `nfs_show_stats`, `nfs_umount_begin`, `nfs_try_get_tree`, `nfs_reconfigure`, `nfs_get_tree_common`, and `nfs_kill_super`.

Control flow registers NFS/NFSv4 filesystems, sysctl, ACL shrinker, and SSC hooks; mount acquisition optionally calls the MOUNT service, verifies or selects security flavors, creates an `nfs_server`, then uses `sget_fc` to share or instantiate a superblock. `nfs_fill_super` installs version-specific superblock flags, time ranges, xattrs, export ops, sysfs naming, and maximum file size. State persists in `nfs_server`, `nfs_client`, superblock active counters, mount flags/options, fscache cookies, sysfs identity, module parameters, and per-cpu IO stats. Dependencies include VFS fs_context, SunRPC transports and auth, lockd, fscache, pNFS, sysfs, sysctl, NFSv4 callback/session/idmap modules, and nfs_ssc. Risks include incorrect superblock sharing across namespaces/security options, auth flavor fallback to AUTH_UNIX/AUTH_NULL semantics, remount option mismatches, noac/sync coupling, and shutdown of pending RPCs during unmount. Test signals: v2/v3/v4 mounts, sec= negotiation, showmount/proc mount options, statfs stale recovery, remount rejection, fscache mounts, unshared/noresvport sharing behavior, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/symlink.c -->
## sources/distributed-fs/ceph-client/fs/nfs/symlink.c

Purpose: implements NFS symlink body caching and inode operations. The key functions are `nfs_symlink_filler`, which invokes protocol `readlink`, and `nfs_get_link`, which satisfies VFS `get_link` from page cache with RCU-aware handling.

Control flow revalidates mapping state, reads folio zero from the symlink inode when needed, stores the symlink target in page cache, and returns `folio_address` with a delayed `page_put_link` cleanup. In RCU lookup, it avoids blocking and returns `-ECHILD` if the cached folio is missing or stale. State is limited to the inode page cache and folio uptodate flag; there is no persistent metadata beyond normal NFS attribute cache behavior. Dependencies are VFS symlink inode operations, `read_cache_folio`, NFS protocol `readlink`, and NFS mapping revalidation helpers. Risks include RCU pathwalk correctness, stale symlink data after server changes, page-size target limits, and proper folio reference release. Test signals: repeated symlink lookup cache hits, RCU pathwalk fallback, server-side target changes with revalidation, and readlink RPC failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/sysctl.c -->
## sources/distributed-fs/ceph-client/fs/nfs/sysctl.c

Purpose: registers `/proc/sys/fs/nfs` tunables for client behavior. It exposes `nfs_mountpoint_timeout` backed by `nfs_mountpoint_expiry_timeout` with jiffies conversion and `nfs_congestion_kb` for writeback congestion control.

Control flow is simple module lifecycle: `nfs_register_sysctl` calls `register_sysctl("fs/nfs", ...)`, and `nfs_unregister_sysctl` unregisters and clears the header pointer. State is persistent only while the NFS module is loaded and consists of the sysctl table header plus mutable global tunable values consumed by other NFS code, especially writeback congestion in `write.c`. Dependencies include the kernel sysctl API and exported NFS globals. Risks are invalid runtime tuning causing surprising mountpoint expiry or writeback throttling, and lifecycle ordering with filesystem registration. Test signals: sysctl file presence after module init, read/write permission mode 0644, jiffies conversion for timeout, congestion threshold effects, and clean removal on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/sysfs.c -->
## sources/distributed-fs/ceph-client/fs/nfs/sysfs.c

Purpose: NFS client sysfs integration under `/sys/fs/nfs`, including net-namespace client identifiers, per-server shutdown control, RPC client links, implementation-id attributes, localio visibility, and server kobject rename/removal helpers. Main APIs include `nfs_sysfs_init`, `nfs_netns_sysfs_setup`, `nfs_netns_sysfs_destroy`, `nfs_sysfs_link_rpc_client`, `nfs_sysfs_add_server`, `nfs_sysfs_move_server_to_sb`, `nfs_sysfs_move_sb_to_server`, and `nfs_sysfs_remove_server`.

Control flow allocates a namespace-aware kset, creates per-net `net/nfs_client` objects, exposes an RCU-protected identifier string, and creates per-server kobjects. Writing `shutdown=1` marks `NFS_MOUNT_SHUTDOWN`, cancels primary/ACL/NLM RPC clients, and only shuts down the shared `nfs_client` once all superblocks are marked down. State lives in kobjects, RCU identifier strings, `nfs_server` flags, sysfs object names, and links to SunRPC sysfs objects. Dependencies include kobject/sysfs, net namespace operations, SunRPC, lockd, NFSv4 implementation id, and localio. Risks include kobject lifetime ordering, namespace isolation, RCU string replacement, partial shutdown of shared clients, and sysfs rename failures around superblock activation/teardown. Test signals: sysfs tree creation/removal per netns, identifier read/write, server shutdown cancellation, RPC symlink creation, NFSv4 implid attributes, localio attribute, and mount/unmount rename behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/sysfs.h -->
## sources/distributed-fs/ceph-client/fs/nfs/sysfs.h

Purpose: declares the NFS sysfs interface and the per-net namespace client object used by `sysfs.c`. It defines `CONTAINER_ID_MAXLEN`, `struct nfs_netns_client`, and the sysfs lifecycle/link/server helpers consumed by NFS client setup and teardown code.

The key type embeds two kobjects: one for the namespace-visible `nfs_client` object and one for the intermediate `net` object, plus a `struct net *` and an RCU-protected identifier string. State and persistence are owned by `sysfs.c`, with callers only holding pointers in `struct nfs_net`. Dependencies are forward-declared NFS and kernel kobject/net types from included translation units. Risks are primarily ABI/lifetime risks: changing the struct or prototypes affects netns setup, server sysfs registration, and sysfs shutdown controls. Test signals are compile coverage for all sysfs helper users and runtime creation/destruction of netns and server sysfs objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/unlink.c -->
## sources/distributed-fs/ceph-client/fs/nfs/unlink.c

Purpose: implements NFS "sillyrename" and asynchronous unlink/rename handling so open-but-unlinked files remain accessible on stateless NFS servers. Key APIs are `nfs_complete_unlink`, `nfs_async_rename`, and `nfs_sillyrename`; internal helpers manage `nfs_unlinkdata` and `nfs_renamedata` RPC lifetimes.

Control flow for sillyrename generates a `.nfs<fileid><counter>` negative dentry, queues asynchronous unlink metadata on the original dentry, starts an async rename to the hidden name, waits for rename completion unless interrupted, moves the dentry on success, and later performs the actual unlink from `dentry_iput` via `nfs_complete_unlink`. State is stored in `DCACHE_NFSFS_RENAMED`, `d_fsdata`, held dentries/inodes/creds, `rmdir_sem`, superblock active refs, and RPC tasks on `nfsiod_workqueue`. Dependencies include protocol-specific unlink/rename setup/done callbacks, VFS dcache parallel lookup, NFS delegation return, tracepoints, and RPC scheduler. Risks include races with lookup aliasing, rename result unknown on signal, freeing displaced `d_fsdata`, stale inode cancellation, and ensuring async release drops all refs. Test signals: unlink open file, close final fd triggers hidden unlink, rename failure cancels async unlink, lookup race with hidden name, rmdir serialization, interrupted rename, and NFSv2/v3/v4 protocol callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/unlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/write.c -->
## sources/distributed-fs/ceph-client/fs/nfs/write.c

Purpose: NFS client buffered writeback, dirty request tracking, unstable-write commit, pNFS/localio write routing, and writeback cache lifecycle. Important APIs include `nfs_pageio_init_write`, `nfs_update_folio`, `nfs_writepages`, `nfs_commit_inode`, `nfs_wb_all`, `nfs_wb_folio`, `nfs_filemap_write_and_wait_range`, commit data alloc/free/init helpers, and writepage cache init/destroy.

Control flow creates or extends folio-private `nfs_page` write requests, grows local i_size, marks folios dirty/uptodate, joins subrequests before writeback, batches through pageio, calls protocol `write_done`, then either removes requests or places unstable writes on commit lists. Commit scans MDS/pNFS lists, builds `nfs_commit_data`, optionally uses localio, verifies write verifiers, and redirties pages on mismatch. State is rich: folio private pointers, `PG_*` request flags, inode `nrequests`, commit lists/counts, `rpcs_out`, congestion counters, open context sync/error/key-expiry flags, fscache invalidation, mempools, and slab caches. Dependencies include VFS writeback, SunRPC, pNFS, fscache, delegation timestamps, localio, lock contexts, and tracepoints. Risks include request group locking, unstable write replay, verifier mismatch handling, credential expiry, page cache invalidation on fatal errors, congestion waits, partial writes, and sync semantics for `noac`/`O_DSYNC`. Test signals: buffered writes, mmap writepage, sync/fsync, unstable commit, verifier mismatch, ENOSPC/EIO propagation, pNFS fallback, localio commit, lock-owner conflicts, credential timeout, and folio migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/Makefile -->
## sources/distributed-fs/ceph-client/fs/nfs_common/Makefile

Purpose: builds shared NFS client/server support objects selected by Kconfig. It defines `nfs_acl` from `nfsacl.o`, `nfs_localio` from `nfslocalio.o localio_trace.o`, and standalone/common objects for grace periods, SSC helper, and protocol common code.

Control flow is build-time only: object inclusion follows `CONFIG_NFS_ACL_SUPPORT`, `CONFIG_NFS_COMMON_LOCALIO_SUPPORT`, `CONFIG_GRACE_PERIOD`, `CONFIG_NFS_V4_2_SSC_HELPER`, and `CONFIG_NFS_COMMON`. `CFLAGS_localio_trace.o += -I$(src)` ensures trace include resolution for the local header. State/persistence is kernel build metadata, not runtime state. Dependencies align with NFS client/server Kconfig selections; incorrect object grouping can create unresolved symbols for ACL, localio, grace-period, or SSC users. Risks include config combinations that need shared symbols but fail to select the right option, and trace header include path breakage. Test signals are allyesconfig/allmodconfig, NFS client-only/server-only builds, localio-enabled builds, and module symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/common.c -->
## sources/distributed-fs/ceph-client/fs/nfs_common/common.c

Purpose: shared NFS status translation helpers. It maps NFSv2/v3 status values to Linux errnos via `nfs_stat_to_errno`, NFSv4 status values via `nfs4_stat_to_errno`, and Linux errnos back to NFSv4 LOCALIO statuses via `nfs_localio_errno_to_nfs4_stat`.

Control flow is table lookup with fallback behavior: unknown v2/v3 statuses become `-EIO`; unknown small/out-of-range NFSv4 statuses become `-EREMOTEIO`; other NFSv4 recovery statuses return negative protocol status for higher recovery logic; localio fallback is `NFS4ERR_SERVERFAULT`. State is static constant mapping tables only. Dependencies include `linux/nfs_common.h`, `linux/nfs4.h`, exported GPL symbols, and both client and server users. Risks include semantic mismatches when multiple NFS errors map to one errno, localio reverse mappings that differ from normal client mappings, and protocol recovery statuses that must not be collapsed too early. Test signals: XDR decode error paths, representative NFSv2/v3/v4 status conversion, unknown status handling, LOCALIO errno conversion, and module symbol use from client and server code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/grace.c -->
## sources/distributed-fs/ceph-client/fs/nfs_common/grace.c

Purpose: shared lock grace-period infrastructure for lockd and NFSD/NFSv4 state recovery. Public APIs are `locks_start_grace`, `locks_end_grace`, `locks_in_grace`, and `opens_in_grace`.

Control flow registers per-net storage containing a list of active `lock_manager` objects. Starting grace adds a manager to the namespace list under `grace_lock`; ending grace deletes it. Querying lock grace checks whether the list is nonempty, while open grace only returns true if a listed manager has `block_opens`. State persists per network namespace until the pernet subsystem exits and is guarded by a global spinlock. Dependencies include netns generic storage, `struct lock_manager`, file locking, and module init/exit. Risks include double add/delete ordering, stale list entries at namespace exit, global lock contention, and incorrect open-vs-lock grace decisions affecting recovery semantics. Test signals: lockd/nfsd restart recovery, multi-netns grace isolation, duplicate start warnings, end idempotence expectations, and open blocking only when requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/grace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/localio_trace.c -->
## sources/distributed-fs/ceph-client/fs/nfs_common/localio_trace.c

Purpose: instantiates tracepoints declared in `localio_trace.h` for NFS LOCALIO client enable/disable events. It defines `CREATE_TRACE_POINTS` and includes the trace header after minimal NFS headers.

There is no runtime control flow beyond tracepoint registration generated by the kernel tracing infrastructure. State is tracing metadata emitted at build/module load time. Dependencies include `linux/nfs_fs.h`, `linux/namei.h`, and the local trace header; the Makefile include path is required because `TRACE_INCLUDE_PATH` is `.`. Risks are build failures if include paths or trace macro guards are wrong, and ABI/format churn in trace events. Test signals: building with `CONFIG_NFS_COMMON_LOCALIO_SUPPORT`, presence of `nfs_localio:*` trace events, and event emission when localio clients are enabled or disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/localio_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/localio_trace.h -->
## sources/distributed-fs/ceph-client/fs/nfs_common/localio_trace.h

Purpose: declares LOCALIO trace events. It defines the `nfs_local_client_event` event class and concrete `nfs_localio_enable_client` / `nfs_localio_disable_client` events.

Control flow is trace macro expansion: each event accepts `const struct nfs_client *`, records NFS protocol version and server hostname, and prints `server=<name> NFSv<version>`. State is per-event trace buffer data, not NFS behavior state. Dependencies include kernel tracepoint infrastructure and trace helper headers for fs, NFS, and SunRPC. Integration points are calls in `nfslocalio.c` when localio is enabled/disabled for a client. Risks include dereferencing fields that must remain valid when tracing, trace header multi-read/include-path requirements, and format compatibility for tooling. Test signals: tracefs event format, enable/disable traces around LOCALIO handshake and teardown, and build with tracepoints compiled as the first object consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/localio_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/nfs_ssc.c -->
## sources/distributed-fs/ceph-client/fs/nfs_common/nfs_ssc.c

Purpose: provides a shared registration table allowing NFSD server-side-copy code to call NFS client module operations without hard static coupling. It exports `nfs_ssc_client_tbl`, `nfs42_ssc_register/unregister`, and `nfs_ssc_register/unregister`.

Control flow is direct pointer install/removal. NFSv4.2 client code registers `nfs4_ssc_client_ops`; NFS client superblock code registers generic `nfs_ssc_client_ops`; unregister only clears if the pointer matches the caller's ops. When `CONFIG_NFS_V4_2` is absent, generic register/unregister are no-ops. State persists in the global exported table and is consumed by knfsd SSC paths. Dependencies include `linux/nfs_ssc.h`, NFSv4.2 config, and client module lifecycle ordering. Risks include stale function pointers if unregister ordering is wrong, missing ops for inter-server copy, and silent no-op registration in non-v4.2 builds. Test signals: NFSv4.2 inter-server copy, module load/unload ordering, unregister with mismatched ops, and builds with/without `CONFIG_NFS_V4_2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/nfs_ssc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/nfsacl.c -->
## sources/distributed-fs/ceph-client/fs/nfs_common/nfsacl.c

Purpose: encodes and decodes Solaris-style NFSv3 ACL protocol data to/from Linux POSIX ACLs. Main APIs are `nfsacl_encode`, `nfs_stream_encode_acl`, `nfsacl_decode`, and `nfs_stream_decode_acl`.

Control flow for encode writes ACE count then XDR array entries, translating owner/group IDs from inode owners and adding a synthetic `ACL_MASK` for minimal three-entry POSIX ACLs to satisfy Solaris expectations. Stream and buffer variants share `xdr_encode_array2`. Decode reads the count, allocates a POSIX ACL if requested, validates tags/permissions/IDs, sorts entries, and removes a bogus minimal mask when it matches group permissions. State is temporary descriptors and allocated ACLs returned to callers; no persistent global state. Dependencies include SunRPC XDR, POSIX ACL helpers, sorting, uid/gid conversion in `init_user_ns`, and NFS ACL constants. Risks include malformed XDR, over-limit ACL counts, invalid uid/gid mappings, Solaris ordering quirks, mask permission normalization, and allocation failure in decode. Test signals: encode/decode minimal and extended ACLs, default ACL flags, invalid tags/permissions, max-entry boundary, stream and xdr_buf variants, and interoperability with Solaris NFS ACL clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/nfsacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/nfslocalio.c -->
## sources/distributed-fs/ceph-client/fs/nfs_common/nfslocalio.c

Purpose: implements shared NFS LOCALIO protocol-bypass support, pairing an NFS client with a local NFSD instance by UUID and caching local `nfsd_file` handles. Public APIs include `nfs_uuid_init`, `nfs_uuid_begin`, `nfs_uuid_end`, `nfs_uuid_is_local`, `nfs_localio_enable_client`, `nfs_localio_disable_client`, `nfs_localio_invalidate_clients`, `nfs_open_local_fh`, `nfs_close_local_fh`, and exported `nfs_to` operation pointers.

Control flow starts with a client UUID in a global list. NFSD detects a matching UUID, moves it onto the netns local-client list, stores net/auth-domain/module refs, and marks the client local. Opening a local file obtains an NFSD net reference under RCU, calls `nfs_to->nfsd_open_local_fh`, and links the file cache to the UUID. Disable/invalidate clears the RCU net pointer, drops auth/module refs, walks cached files, coordinates with racing close, and unlinks from local-client lists. State includes global UUID list, per-UUID locks/list locks/file lists, auth domain refs, NFSD module ref, RCU net and file pointers, and cached RO/RW local files. Dependencies include NFSD localio operations, netns, auth domains, module refs, tracepoints, and RCU/spinlock wait primitives. Risks include strict lock ordering, module pointer lifetime, races between disable and close, net namespace teardown, and using localio after NFSD unload. Test signals: local client handshake, open/read/write/commit through localio, concurrent close while disabling, netns teardown invalidation, NFSD module unload/reload, and non-local clients hammering close fast path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs_common/nfslocalio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/Kconfig -->
## sources/distributed-fs/ceph-client/fs/nfsd/Kconfig

Purpose: defines build-time configuration for the kernel NFS server and optional protocol/layout/security features. It controls `NFSD`, deprecated NFSv2, NFSv2/v3 ACL extensions, NFSv4, pNFS block/SCSI/flexfile layouts, NFSv4.2 inter-server copy, security labels, legacy client tracking, and experimental NFSv4 POSIX ACLs.

Control flow is Kconfig dependency/selection logic: `NFSD` depends on networking, locking, fsnotify, exportfs, multiuser, and selects shared NFS/SunRPC/lockd support; feature options select ACL, GRACE_PERIOD, pNFS, exportfs block ops, RPCSEC_GSS, and SSC helper as needed. State is build configuration that determines object inclusion, exported ABI, and runtime server capabilities. Dependencies integrate with `fs/nfsd/Makefile`, `nfs_common`, local filesystems, security modules, and user-space nfs-utils. Risks include unsupported protocol combinations, enabling deprecated or experimental ACL/client tracking features, block/SCSI layout requirements on block-device exports, and missing userspace support. Test signals: defconfig/allmodconfig coverage, each option's object inclusion, NFSv3 baseline server, NFSv4 with grace/krb5, pNFS layout exports, and disabled-feature negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/Makefile -->
## sources/distributed-fs/ceph-client/fs/nfsd/Makefile

Purpose: builds the `nfsd` kernel object and conditionally includes server protocol, ACL, pNFS, localio, debugfs, and generated XDR sources. It also defines an `xdrgen` developer target for regenerating NFSv4.1 XDR code.

Control flow is build-time: `trace.o` is first, then core service/control/export/auth/cache/stats/vfs/netlink objects, followed by Kconfig-selected NFSv2, ACL, NFSv4, pNFS layouts, localio, and debugfs objects. `ccflags-y += -I$(src)` supports trace headers. State is object composition and generated source dependencies. Integration points include `Kconfig`, generated `nfs4xdr_gen.{h,c}`, and documentation XDR specs. Risks include trace macro ordering, missing generated XDR regeneration after `.x` edits, unresolved symbols when feature Kconfig selections change, and localio/debugfs optional object drift. Test signals: builds for core NFSD, NFSv4, ACLs, pNFS block/SCSI/flexfile, localio, debugfs, and running `make xdrgen` after XDR spec changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/acl.h -->
## sources/distributed-fs/ceph-client/fs/nfsd/acl.h

Purpose: declares shared NFSD NFSv4 ACL helpers used by server XDR/procedure/attribute code. It forward declares ACL, filehandle, request, attrs, and file type structures and exposes ACL size, who-type, XDR writer, POSIX ACL sorting, ACL retrieval, and ACL-to-attribute conversion APIs.

There is no runtime control flow in this header. State is owned by implementation files and passed through `struct nfs4_acl`, `struct nfsd_attrs`, and POSIX ACL pointers. Dependencies include NFSD `svc_fh`, `svc_rqst`, NFSv4 file type definitions, XDR streams, and POSIX ACL handling. Integration points are NFSv4 GETATTR/SETATTR ACL handling and draft POSIX ACL support. Risks include prototype drift with implementation, ACL memory ownership ambiguity for callers, and interoperability between NFSv4 ACL and POSIX ACL semantics. Test signals: NFSv4 ACL get/set, ACL XDR encoding, POSIX ACL sorting ranges, and builds with/without experimental POSIX ACL config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/auth.c -->
## sources/distributed-fs/ceph-client/fs/nfsd/auth.c

Purpose: maps authenticated RPC credentials onto kernel filesystem credentials for NFSD request execution. Key functions are `nfsexp_flags` and `nfsd_setuser`.

Control flow finds export flags matching the RPC pseudoflavor, reverts any prior override creds, prepares new creds, sets fsuid/fsgid from request credentials, applies `all_squash` or `root_squash`, copies/sorts group lists as needed, substitutes anonymous IDs for invalid IDs, installs groups, adjusts effective capabilities depending on whether fsuid remains root, and calls `override_creds`. State is per-thread current credential override plus allocated `group_info`; export flavor flags and anonymous IDs drive persistence of policy. Dependencies include svc credentials, export structures, Linux credential APIs, groups, and capability helpers. Risks include memory allocation failure, leaking or stacking credential overrides, incorrect root group squashing, invalid uid/gid handling, and capability over/under-granting. Test signals: exports with sec-specific flags, root_squash/all_squash/no_root_squash, supplemental group mapping, invalid ids, and filesystem operations verifying effective uid/gid/caps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/auth.h -->
## sources/distributed-fs/ceph-client/fs/nfsd/auth.h

Purpose: declares the NFSD authentication helper `nfsd_setuser`, which applies an RPC request's user/group identity to the current kernel thread for export-backed filesystem access.

The header has no runtime control flow and exists to share the auth implementation with NFSD request handlers. State effects are in `auth.c`: current task credential overrides, groups, squash policy, and capabilities. Dependencies are `struct svc_cred` and `struct svc_export` definitions from NFSD/SunRPC headers included by consumers. Risks are prototype mismatch and misuse by callers that do not later restore credentials through the standard NFSD request lifecycle. Test signals: compile coverage for NFSD auth users and request handling that verifies user identity switching across exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/blocklayout.c -->
## sources/distributed-fs/ceph-client/fs/nfsd/blocklayout.c

Purpose: implements NFSD pNFS block and SCSI layout operations. It maps exported filesystem extents into block layout extents, returns device info, processes layoutcommit updates, and fences SCSI clients through persistent reservations.

Control flow for layoutget rejects grace-period or misaligned requests, caps max extents by client maxcount/PAGE_SIZE, calls exportfs `map_blocks`, translates `iomap` types into pNFS block extent states, sets device IDs, and adjusts returned segment offset/length. Layoutcommit decodes opaque layout updates and calls exportfs `commit_blocks` with timestamp/size attrs. Block device info returns a UUID-based simple volume. SCSI device info builds designator/pr-key data, registers/reserves an MDS PR key, tracks per-client device fence state in an xarray, and `fence_client` preempts the client's reservation after recall failures. State includes allocated layout/device structures, client fence xarray marks, fence mutex, PR keys, device generations, and layout state `ls_fenced`. Dependencies include exportfs block ops, iomap, pNFS layout infrastructure, block layer PR ops, `locks_in_grace`, tracepoints, and XDR helpers. Risks include extent alignment, undersized maxcount, unwritten/hole semantics, partition rejection, PR command retry semantics, unbounded fence tracking, and filesystem export op errors. Test signals: pNFS block/SCSI layoutget/getdeviceinfo/layoutcommit, misaligned requests, grace rejection, holes/unwritten extents, minlength handling, PR registration/reserve/preempt, recall failure fencing, and exported filesystem block op coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/blocklayout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/blocklayoutxdr.c -->
## sources/distributed-fs/ceph-client/fs/nfsd/blocklayoutxdr.c

Purpose: XDR encode/decode support for NFSD pNFS block and SCSI layouts. Main APIs are `nfsd4_block_encode_layoutget`, `nfsd4_block_encode_getdeviceinfo`, `nfsd4_block_decode_layoutupdate`, and `nfsd4_scsi_decode_layoutupdate`.

Control flow encodes layoutget as opaque length, extent count, and deviceid/foff/len/soff/state tuples. Device info encodes simple volumes with signature/offset or SCSI volumes with code set/designator/pr key, respecting `gd_maxcount == 0`. Decode validates exact opaque lengths, allocates `iomap` arrays, decodes block extents or SCSI ranges, enforces block-size alignment, and only accepts `PNFS_BLOCK_READWRITE_DATA` for block layout updates. State is temporary encoded stream position and returned allocated `iomap` arrays; callers own freeing. Dependencies include SunRPC XDR streams, NFSD XDR helpers, `blocklayoutxdr.h`, iomap, and pNFS constants. Risks include XDR length mismatch, insufficient stream space, alignment validation, allocation failure mapped to protocol delay, and accepting invalid extent states. Test signals: layoutget/getdeviceinfo encoding golden cases, zero maxcount, malformed opaque lengths, unaligned extents, invalid block state, SCSI range decode, and memory-failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/blocklayoutxdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/blocklayoutxdr.h -->
## sources/distributed-fs/ceph-client/fs/nfsd/blocklayoutxdr.h

Purpose: declares pNFS block/SCSI layout wire structures, size constants, and XDR helper prototypes used by NFSD block layout implementation. Key types include `pnfs_block_extent`, `pnfs_block_range`, `pnfs_block_layout`, `pnfs_block_volume`, and `pnfs_block_deviceaddr`.

There is no runtime control flow. State represented by these structs is allocated and filled in `blocklayout.c` and encoded/decoded in `blocklayoutxdr.c`: device IDs, file/storage offsets, lengths, extent state, simple UUID volume info, SCSI designator info, and persistent reservation keys. Dependencies include block device definitions, `xdr4.h`, NFSv4 pNFS enums, and `struct iomap`. Risks include wire-size constant drift, flexible-array bounds, UUID/designator maximum assumptions, and mismatched layout structures between block and SCSI users. Test signals: compile coverage for both layout drivers, XDR size/encoding tests, and static checks for counted flexible arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/blocklayoutxdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/cache.h -->
## sources/distributed-fs/ceph-client/fs/nfsd/cache.h

Purpose: declares NFSD duplicate-request reply cache structures and APIs. It defines `struct nfsd_cacherep`, cache states (`RC_UNUSED`, `RC_INPROG`, `RC_DONE`), return actions (`RC_DROPIT`, `RC_REPLY`, `RC_DOIT`), cache payload types, expiration, checksum length, and lookup/update/init/shutdown/stat functions.

Control flow is implemented elsewhere but the contract is clear: `nfsd_cache_lookup` classifies an RPC request by xid/checksum/proc/protocol/version/address/security and returns whether to drop, reply from cache, or execute; `nfsd_cache_update` stores status or reply buffer after execution. State includes rb-tree node, LRU list, timestamp, secure-port bit, and either reply status or kvec buffer. Dependencies include SunRPC svc request structures, NFSD network state, seq_file stats, and nfsd core headers. Risks include key collisions from partial checksums, sockaddr storage assumptions, stale/expired entries, memory ownership of reply buffers, and secure-port matching. Test signals: retransmitted non-idempotent RPCs, reply replay, in-progress duplicate drop, expiry behavior, IPv4/IPv6 clients, secure/insecure ports, and reply cache stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/current_stateid.h -->
## sources/distributed-fs/ceph-client/fs/nfsd/current_stateid.h

Purpose: declares helpers for NFSv4 current stateid propagation within a compound request. Setters record current stateid from OPEN/OPEN_DOWNGRADE/LOCK/CLOSE results; getters supply it to operations such as DELEGRETURN, FREE_STATEID, SETATTR, CLOSE, LOCKU, READ, and WRITE.

There is no implementation in this header. State lives in `struct nfsd4_compound_state` and operation unions from `xdr4.h`, allowing later operations in the same COMPOUND to use the special current-stateid value. Dependencies include NFSD state management and NFSv4 XDR operation definitions. Risks include using stale current stateid after errors, missing propagation for new operations, and mismatched operation union fields. Test signals: NFSv4 COMPOUND sequences that use current stateid after OPEN/LOCK, invalid current-stateid ordering, READ/WRITE with current stateid, and close/downgrade state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/current_stateid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/debugfs.c -->
## sources/distributed-fs/ceph-client/fs/nfsd/debugfs.c

Purpose: creates global NFSD debugfs controls under `/sys/kernel/debug/nfsd`. It exposes `disable-splice-read`, `io_cache_read`, `io_cache_write`, and, with NFSv4, `delegated_timestamps`.

Control flow creates the debugfs directory and files in `nfsd_debugfs_init`, and removes the tree in `nfsd_debugfs_exit`. Setters update global runtime knobs immediately: enabling dontcache/direct read disables splice read; clearing disable-splice-read forces buffered read; write cache mode accepts buffered/dontcache/direct constants. State is global NFSD variables (`nfsd_disable_splice_read`, `nfsd_io_cache_read`, `nfsd_io_cache_write`, and `nfsd_delegts_enabled`) affecting all NFSD versions, exports, and namespaces. Dependencies include debugfs and NFSD core globals. Risks include global scope surprising netns/export isolation expectations, invalid values, coupling between splice and cache mode, and debugfs absence in production configs. Test signals: debugfs file creation/removal, read/write mode validation, immediate impact on READ/WRITE I/O paths, splice disabling side effects, and NFSv4 delegated timestamp toggle when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/debugfs.c -->
