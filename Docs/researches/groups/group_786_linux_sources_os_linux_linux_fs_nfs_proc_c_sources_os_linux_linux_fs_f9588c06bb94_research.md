# Group Research: group_786_linux_sources_os_linux_linux_fs_nfs_proc_c_sources_os_linux_linux_fs_f9588c06bb94

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`. This grouped report covers the listed Linux NFS client, NFS common, and NFSD support files.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/proc.c -->
# File Research: sources/os/linux/linux/fs/nfs/proc.c

Implements the NFSv2 client RPC operation table and the version-specific procedure wrappers used by generic NFS client code.

Key behavior:
- Provides NFSv2 implementations for root probing, getattr, setattr, lookup, readlink, create, remove, rename, link, symlink, mkdir, rmdir, readdir, mknod, statfs, fsinfo, pathconf, read, write, and lock handling.
- `nfs_proc_get_root()` probes the root file handle with GETATTR and STATFS, retrying with the default client credential when needed, then fills NFSv2 transfer-size and filesystem limits.
- Directory mutations mark parent directories for revalidation after successful or attempted RPCs.
- NFSv2-specific quirks are handled locally:
  - `mknod` is encoded through CREATE.
  - FIFO creation retries with the original mode if the character-device workaround fails.
  - SYMLINK has no returned attributes, so instantiation falls back to LOOKUP.
  - COMMIT setup paths are `BUG()` because NFSv2 writes are always file-sync.
- Read completion refreshes inode attributes and synthesizes EOF detection from count and returned file size.
- Write setup forces `NFS_FILE_SYNC`; write completion treats the requested byte count as written and updates inode writeback attributes.
- Locking delegates to lockd via `nlmclnt_proc()` and validates 32-bit NFSv2 lock ranges.

Important interactions:
- Exports `nfs_v2_clientops`, the main NFSv2 dispatch contract consumed by generic mount, inode, page I/O, and VFS paths.
- Uses shared helpers from `internal.h`, including cache invalidation, instantiation, writeback, delegation stubs, and server/client allocation.
- The inode operation tables wire generic NFS VFS entry points to NFSv2 protocol procedures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/read.c -->
# File Research: sources/os/linux/linux/fs/nfs/read.c

Implements buffered read and readahead page I/O for the NFS client.

Key behavior:
- Allocates and frees read `nfs_pgio_header` objects through the `nfs_read_data` slab cache.
- `nfs_pageio_init_read()` selects ordinary MDS read I/O or pNFS layout-driver read ops, then initializes the generic NFS pageio descriptor.
- Read completion walks completed `nfs_page` requests, handles EOF zero-fill, marks successful folio ranges uptodate, records errors in the open context, unlocks folios, and notifies netfs completion.
- Handles short reads by retrying from the returned byte count, or forcing MDS retry for non-RPC layout drivers.
- `nfs_read_add_folio()` creates a read request for the valid portion of a folio, zero-fills beyond EOF within the folio, and queues it in pageio.
- `nfs_read_folio()` flushes conflicting pending writes, handles stale inodes, tries the netfs read path first, then falls back to NFS pageio.
- `nfs_readahead()` similarly tries netfs readahead first, then builds NFS pageio requests from the readahead control.
- Maintains read statistics and delegated atime updates.

Important interactions:
- Depends on protocol-specific `NFS_PROTO(inode)->read_done()` and `read_setup()` callbacks.
- Integrates with pNFS through layout-driver read ops and MDS reset support.
- Integrates with FS-Cache/netfs via `nfs_netfs_read_folio()`, `nfs_netfs_readahead()`, and related completion hooks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/super.c -->
# File Research: sources/os/linux/linux/fs/nfs/super.c

Implements NFS filesystem registration, superblock operations, mount display/statistics, mount negotiation, superblock sharing, remount validation, and NFSv4 module parameters.

Key behavior:
- Defines and exports `nfs_sops` with inode allocation/free, writeback, statfs, eviction, unmount cancellation, and show callbacks.
- `register_nfs_fs()` registers NFS and optional NFSv4 filesystems, registers sysctls, installs the NFS access-cache shrinker, and registers NFSv4.2 server-side-copy client hooks.
- `nfs_statfs()` calls protocol-specific statfs, translates byte counts to VFS block counts, and zaps parent caches on stale file handles.
- Mount option rendering covers protocol version, I/O sizes, attribute-cache timers, hard/soft mode, lookup cache mode, transport, ports, timeout/retransmit, security flavor, TLS transport security, mountd options, FS-Cache, migration, local locking, aligned writes, and eager/write-wait policy.
- `nfs_show_stats()` emits mount options, mount age, capability bits, NFSv4 attributes/session/pNFS/lease data, security flavor, per-CPU I/O counters, and RPC client stats.
- `nfs_umount_begin()` kills pending ACL and main RPC client tasks during unmount.
- Mountd negotiation requests the root file handle, verifies or selects an auth flavor, avoids selecting `AUTH_NULL` unless needed, and creates the server using the selected flavor.
- Remount rejects changes to options that are incompatible with an existing superblock, while preserving `noac` implying synchronous writes.
- `nfs_fill_super()` sets VFS operations, xattrs, block size, timestamp granularity/range, export ops, magic, maxbytes, sysfs name, and security-mount-option tracking.
- Superblock comparison checks server address, namespace, fsid, user namespace, security mount options, and shareable mount options.
- FS-Cache cookie setup handles ordinary mounts and cloned mounts.
- `nfs_get_tree_common()` handles superblock lookup/sharing, BDI setup, root dentry acquisition, and activation.
- `nfs_kill_super()` moves sysfs identity back to the server name, kills the anonymous superblock, releases FS-Cache state, and frees the server.
- NFSv4 module parameters include callback port/thread count, idmap cache timeout, idmapping disable flag, session slot limits, implementation ID sending, unique client ID, lost-lock recovery, and delay retransmit behavior.

Important interactions:
- Central bridge between fs_context mount parsing/server creation and VFS superblock lifecycle.
- Uses `sysfs.c` for server kobject naming and `sysctl.c` for tunables.
- Shares server/client objects across mounts unless `nosharecache`/unshared semantics or option mismatches prevent sharing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/symlink.c -->
# File Research: sources/os/linux/linux/fs/nfs/symlink.c

Implements NFS symlink page-cache handling and inode operations.

Key behavior:
- `nfs_symlink_filler()` reads symlink contents by invoking the protocol-specific `readlink` operation into the first page-cache folio.
- `nfs_get_link()` supports both RCU and non-RCU lookup:
  - RCU mode revalidates mapping through `nfs_revalidate_mapping_rcu()`, requires an existing uptodate folio, and returns `-ECHILD` when blocking work is required.
  - Non-RCU mode revalidates normally and uses `read_cache_folio()` with the filler to fetch the symlink target.
- Uses `set_delayed_call(done, page_put_link, folio)` so the VFS releases the folio after link resolution.
- Exports `nfs_symlink_inode_operations` with `.get_link`, `.getattr`, `.setattr`, and `.fileattr_get`.

Important interactions:
- Relies on the protocol table from `NFS_PROTO(inode)` for version-specific READLINK behavior.
- Uses the page cache as the symlink target cache, with revalidation delegated to generic NFS cache-validity helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/sysctl.c -->
# File Research: sources/os/linux/linux/fs/nfs/sysctl.c

Registers the NFS client sysctl tunables under `fs/nfs`.

Key behavior:
- Defines sysctls for:
  - `nfs_mountpoint_timeout`, backed by `nfs_mountpoint_expiry_timeout` and handled as jiffies.
  - `nfs_congestion_kb`, backed by `nfs_congestion_kb`.
- `nfs_register_sysctl()` registers the table and returns `-ENOMEM` on failure.
- `nfs_unregister_sysctl()` unregisters the table and clears the saved header pointer.

Important interactions:
- Called from `register_nfs_fs()` and `unregister_nfs_fs()` in `super.c`.
- `nfs_congestion_kb` is initialized and consumed by `write.c` for client writeback congestion control.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/sysfs.c -->
# File Research: sources/os/linux/linux/fs/nfs/sysfs.c

Implements the NFS client sysfs hierarchy for per-network-namespace client state and per-server control/status files.

Key behavior:
- Creates the top-level `/sys/fs/nfs` kset with network-namespace child support.
- For each NFS network namespace, creates `net/nfs_client` kobjects and exposes a writable `identifier` attribute capped by `CONTAINER_ID_MAXLEN`.
- Stores the namespace identifier through an RCU-protected string pointer and safely frees old values after `synchronize_rcu()`.
- Provides setup/destroy functions for per-netns sysfs objects.
- Implements server shutdown control:
  - `shutdown` reads whether `NFS_MOUNT_SHUTDOWN` is set.
  - Writing `1` marks the mount shutdown, cancels main/ACL RPC clients, shuts down lockd state if present, and shuts down the shared `nfs_client` only after all superblocks are shutdown.
- Optionally exposes NFSv4.1 implementation ID domain/name attributes.
- `nfs_sysfs_link_rpc_client()` creates links from an NFS server kobject to RPC client sysfs kobjects.
- Adds per-server kobjects named `server-<id>`, with namespace-aware attributes.
- Optionally exposes `localio` when `CONFIG_NFS_LOCALIO` is enabled.
- Renames server kobjects to the superblock ID when attached to a superblock and back to `server-<id>` when detached.
- `nfs_sysfs_remove_server()` unlinks the server kobject from sysfs.

Important interactions:
- Used by `super.c` during superblock fill and teardown.
- Uses lockd shutdown hooks and RPC task cancellation to make sysfs shutdown operational, not merely informational.
- Coordinates namespace isolation through `net_ns_type_operations` and kobject namespace callbacks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/sysfs.h -->
# File Research: sources/os/linux/linux/fs/nfs/sysfs.h

Declares the NFS client sysfs data structures and helper interface.

Key behavior:
- Defines `CONTAINER_ID_MAXLEN` as 64 bytes.
- Defines `struct nfs_netns_client`, containing:
  - A client kobject.
  - A containing `net` kobject.
  - The owning `struct net`.
  - An RCU-protected namespace/container identifier string.
- Declares global `nfs_net_kobj`.
- Declares sysfs init/exit, per-netns setup/destroy, RPC-client link creation, server add, server/superblock rename transitions, and server removal helpers.

Important interactions:
- Included by `super.c` and `sysfs.c`.
- Forms the small public contract between NFS net namespace management, server lifecycle, and sysfs exposure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/unlink.c -->
# File Research: sources/os/linux/linux/fs/nfs/unlink.c

Implements NFS asynchronous unlink, asynchronous rename, and sillyrename handling for open-but-unlinked files.

Key behavior:
- `nfs_async_unlink()` allocates `nfs_unlinkdata`, copies the target name, captures current credentials, and stores the unlink data in `dentry->d_fsdata` while setting `DCACHE_NFSFS_RENAMED`.
- `nfs_complete_unlink()` clears the sillyrename flag, returns delegations/writeback as needed, then either starts the delayed unlink RPC or frees the queued unlink data if the inode is stale.
- Asynchronous unlink uses RPC callbacks to prepare the protocol-specific REMOVE call, process completion through `unlink_done`, restart when required, release dentry lookup state, drop superblock activity, and free data.
- `nfs_call_unlink()` protects against rmdir races with `rmdir_sem`, allocates a parallel dentry for the silly name, and transfers sillyrename data if lookup races reveal an existing alias.
- `nfs_async_rename()` builds and submits an asynchronous protocol-specific RENAME RPC with held dentries, directories, credentials, and post-op attribute buffers.
- Rename release marks affected inodes/directories for revalidation on uncertain results and releases held dentries, inodes, credentials, and superblock activity.
- `nfs_sillyrename()` creates hidden `.nfs<fileid><counter>` names, queues the final unlink first, runs the rename, waits for completion unless interrupted, updates verifiers and inode cache invalidation on success, and drops dentries on unknown restart results.

Important interactions:
- Handles stateless NFS open-file unlink semantics by preserving open files client-side until the last reference is dropped.
- Delegates protocol differences through `NFS_PROTO()->unlink_setup`, `unlink_rpc_prepare`, `unlink_done`, `rename_setup`, `rename_rpc_prepare`, and `rename_done`.
- Uses dentry flags and `d_fsdata` as the durable handoff between unlink-time sillyrename setup and final dentry release.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/unlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/write.c -->
# File Research: sources/os/linux/linux/fs/nfs/write.c

Implements buffered NFS writeback, dirty folio tracking, unstable-write COMMIT handling, writeback congestion, pNFS write integration, and write/commit cache initialization.

Key behavior:
- Allocates write and commit headers from slab caches backed by mempools for low-memory writeback safety.
- Tracks optional I/O-completion callbacks with a small refcounted `nfs_io_completion` object, used to trigger commits after writeback batches.
- Associates dirty folios with `nfs_page` request groups through `folio->private`, `PG_MAPPED`, and inode request counts.
- Merges subrequests into a single head request when writeback or update paths need a coherent per-folio request range.
- Grows local inode size for extending writes, updates delegated mtime when available, and invalidates FS-Cache state after local size changes.
- Records writeback errors in the address space and superblock errseq, then invalidates cached size/change/data state.
- Implements NFS writeback congestion using `nfs_congestion_kb`, per-server writeback counters, a congestion flag, and a waitqueue.
- `nfs_writepages()` batches dirty folios through pageio, optionally waits for congestion to clear, supports eager/write-wait policy, and queues follow-up commits for unstable writes.
- Commit-list helpers add/remove requests requiring COMMIT, including pNFS data-server commit-list integration.
- `nfs_write_completion()` removes completed write requests, records errors, marks unstable writes for commit with verifiers, or removes requests after stable writes.
- `nfs_try_to_update_request()` coalesces compatible dirty regions or flushes incompatible/non-contiguous requests before creating a new one.
- `nfs_flush_incompatible()` flushes existing folio requests owned by a different open context, lock owner, or dropped folio before buffered writes proceed.
- Credential expiry logic avoids unsafe buffered writes when RPC credential keys are expired or near timeout.
- `nfs_update_folio()` optionally expands writes to page-sized regions when cache state, locking, delegation, and mount flags make it safe.
- `nfs_initiate_write()` selects RPC priority, marks swapfile tasks, calls version-specific write setup, and traces submission.
- Write completion checks server stability promises, records unstable writes, handles short writes by retrying or escalating to stable writes, and invalidates mode on suid/sgid removal cases.
- Commit handling scans commit lists, submits pNFS or MDS COMMIT calls, verifies returned write verifiers, removes successfully committed requests, and redirties mismatches for rewrite.
- Provides synchronous inode, whole-file, and single-folio writeback helpers used by close, fsync, read-before-write, reclaim, and migration.
- `nfs_migrate_folio()` blocks migration while private NFS requests are attached unless synchronous migration can flush them first.
- Initializes and destroys write/commit slab caches and mempools, and computes the default congestion threshold from system memory capped at 256 MiB.

Important interactions:
- Uses generic NFS pageio and protocol-specific `write_setup`, `write_done`, `commit_setup`, and `commit_done`.
- Integrates with pNFS through layout-driver write ops, data-server commit lists, and MDS fallback.
- Integrates with FS-Cache/netfs, NFS delegations, file locking, writeback control, and VFS dirty/writeback accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/Makefile -->
# File Research: sources/os/linux/linux/fs/nfs_common/Makefile

Builds Linux NFS code shared by the client and server.

Key behavior:
- Builds `nfs_acl.o` from `nfsacl.o` when `CONFIG_NFS_ACL_SUPPORT` is enabled.
- Adds include path flags for `localio_trace.o`.
- Builds `nfs_localio.o` from `nfslocalio.o` and `localio_trace.o` when `CONFIG_NFS_COMMON_LOCALIO_SUPPORT` is enabled.
- Builds `grace.o` when `CONFIG_GRACE_PERIOD` is enabled.
- Builds `nfs_ssc.o` when `CONFIG_NFS_V4_2_SSC_HELPER` is enabled.
- Builds `common.o` when `CONFIG_NFS_COMMON` is enabled.

Important interactions:
- Separates common protocol/status/ACL/localio/grace helpers from client-only `fs/nfs` and server-only `fs/nfsd`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/common.c -->
# File Research: sources/os/linux/linux/fs/nfs_common/common.c

Provides shared NFS status-code and errno translation helpers.

Key behavior:
- `nfs_stat_to_errno()` maps NFSv2/v3 status codes to Linux negative errno values, defaulting unknown statuses to `-EIO`.
- `nfs4_stat_to_errno()` first checks common NFSv4 mappings, then extra NFSv4 mappings such as server fault, locked, illegal op, and xattr errors.
- Unknown NFSv4 status values outside the expected protocol range map to `-EREMOTEIO`; otherwise they are returned as negative protocol status so recovery paths can handle them.
- `nfs_localio_errno_to_nfs4_stat()` maps local errno values back to NFSv4 status codes for LOCALIO, using common mappings plus LOCALIO-specific corrections.

Important interactions:
- Exported for use by NFS client, NFSD, XDR decode/encode paths, and LOCALIO conversion.
- LOCALIO mappings intentionally differ from generic client mappings where errno-to-protocol translation needs server-side semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/grace.c -->
# File Research: sources/os/linux/linux/fs/nfs_common/grace.c

Implements shared lock-manager grace-period tracking for lockd and NFSv4/NFSD state recovery.

Key behavior:
- Maintains a per-network-namespace list of lock managers currently in grace.
- `locks_start_grace()` adds a lock manager to the namespace grace list, warning on double-add attempts.
- `locks_end_grace()` removes a lock manager and is safe to call more than once because the list head is reinitialized.
- `locks_in_grace()` reports whether any lock manager is in grace, meaning ordinary lock requests should be rejected or delayed.
- `opens_in_grace()` reports whether any grace-period participant blocks opens as well as locks.
- Registers per-net operations that initialize and validate the grace list for each network namespace.

Important interactions:
- Exported for lockd and NFSD/NFSv4 state handling.
- Uses a global spinlock plus per-net generic storage to coordinate grace state across lock managers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/grace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/localio_trace.c -->
# File Research: sources/os/linux/linux/fs/nfs_common/localio_trace.c

Instantiates tracepoints for NFS LOCALIO client enable/disable events.

Key behavior:
- Includes NFS and namei headers needed by trace definitions.
- Defines `CREATE_TRACE_POINTS` before including `localio_trace.h`, causing the tracepoint storage and metadata to be emitted in this compilation unit.

Important interactions:
- Built into `nfs_localio.o` with `nfslocalio.o`.
- Tracepoint definitions are declared in `localio_trace.h` and used by LOCALIO client lifecycle code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/localio_trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/localio_trace.h -->
# File Research: sources/os/linux/linux/fs/nfs_common/localio_trace.h

Declares tracepoints for NFS LOCALIO client state changes.

Key behavior:
- Defines trace system `nfs_localio`.
- Declares an event class carrying the NFS client protocol version and server hostname.
- Defines `nfs_localio_enable_client` and `nfs_localio_disable_client` events from that class.
- Sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` so the trace generation framework can include this local header.

Important interactions:
- Used by `nfslocalio.c` to trace when a client is enabled for, or disabled from, LOCALIO protocol bypass.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/localio_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/nfs_ssc.c -->
# File Research: sources/os/linux/linux/fs/nfs_common/nfs_ssc.c

Provides the shared registration table for NFSv4.2 server-side copy helper callbacks.

Key behavior:
- Defines and exports global `nfs_ssc_client_tbl`.
- Under `CONFIG_NFS_V4_2`, `nfs42_ssc_register()` and `nfs42_ssc_unregister()` install/remove NFSv4 client-side SSC ops.
- Under `CONFIG_NFS_V4_2`, `nfs_ssc_register()` and `nfs_ssc_unregister()` install/remove NFS filesystem-level SSC ops.
- Unregister helpers only clear pointers if the caller matches the currently registered ops.
- Without `CONFIG_NFS_V4_2`, `nfs_ssc_register()` and `nfs_ssc_unregister()` are exported no-ops.

Important interactions:
- Allows NFSD inter-server copy support to call into NFS client modules without hardwiring all callbacks directly.
- `super.c` registers the NFS client operations when NFSv4.2 support is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/nfs_ssc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/nfsacl.c -->
# File Research: sources/os/linux/linux/fs/nfs_common/nfsacl.c

Implements encoding and decoding for the Solaris-style NFSv3 ACL protocol extension.

Key behavior:
- Documents the differences between Solaris NFS ACL wire format and Linux POSIX draft ACLs:
  - Minimal ACLs include a mask entry.
  - Minimal mask permissions match group object permissions.
  - Owner/group object IDs are encoded explicitly.
  - Wire ACL entries are unsorted.
- `xdr_nfsace_encode()` encodes one ACE as tag/typeflag, identifier, and permission bits, using inode owner/group for object entries.
- `nfsacl_encode()` writes ACL entry count and array data into an `xdr_buf`, inserting a synthetic mask entry for 3-entry minimal ACLs without allocating memory.
- `nfs_stream_encode_acl()` performs the same encoding through `xdr_stream`.
- `xdr_nfsace_decode()` allocates the POSIX ACL on first ACE decode, validates user/group IDs and permission bits, tolerates extra Solaris mask bits, and rejects unknown tags.
- `posix_acl_from_nfsacl()` sorts decoded ACEs and removes the synthetic mask from minimal ACLs when it matches group object permissions.
- `nfsacl_decode()` decodes from an `xdr_buf`, validates counts and converted POSIX form, returns decoded byte length, and optionally returns ACE count.
- `nfs_stream_decode_acl()` performs the same decode through `xdr_stream`.

Important interactions:
- Exported for NFS client and NFSD ACL procedure/XDR implementations.
- Uses init user namespace conversions, so ACL IDs are translated through kernel UID/GID helpers at encode/decode boundaries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/nfsacl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/nfslocalio.c -->
# File Research: sources/os/linux/linux/fs/nfs_common/nfslocalio.c

Implements shared NFS LOCALIO client/server handshake state and local file-handle open/close coordination.

Key behavior:
- Maintains a global list of `nfs_uuid_t` objects for clients probing whether their NFS server is local.
- `nfs_uuid_init()` initializes the embedded UUID state, lists, lock, and probe count.
- `nfs_uuid_begin()` ensures the UUID state is unused, adds it to the global list, and generates a UUID for discovery.
- `nfs_uuid_end()` removes an unused UUID from the global list if the client was not matched to a local server.
- `nfs_uuid_is_local()` is called by NFSD when it sees a matching UUID; it moves the UUID to the NFSD net namespace local-client list, pins the NFSD module, holds the auth domain, and publishes the local net pointer with RCU.
- `nfs_localio_enable_client()` traces enablement; actual enablement is performed by the UUID match path.
- `nfs_localio_disable_client()` tears down local state, clears the net pointer, releases auth/module references, closes cached local files, removes the client from the NFSD namespace local list, and traces disablement.
- `nfs_localio_invalidate_clients()` disables all LOCALIO clients attached to an NFSD network namespace during server teardown.
- `nfs_open_local_fh()` safely obtains an NFSD net reference, calls NFSD local-file open operations, links the cached local file into the UUID’s file list, and unwinds on races with teardown.
- `nfs_close_local_fh()` handles ordinary close, races with client teardown, local file ref drops, list removal, and wakeups for teardown waiters.
- Exports `nfs_to`, a function-pointer table populated by NFSD for LOCALIO operations.

Important interactions:
- Provides protocol bypass only when client and server are in the same kernel and a UUID handshake establishes locality.
- Uses RCU, spinlocks, module references, auth-domain references, and wait variables to keep NFSD callbacks valid during local file operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs_common/nfslocalio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/Kconfig -->
# File Research: sources/os/linux/linux/fs/nfsd/Kconfig

Defines Linux NFSD configuration options and feature dependencies.

Key behavior:
- `NFSD` enables kernel NFS server support and selects core dependencies including lockd, SUNRPC, exportfs, crypto, CRC32, fsnotify, and NFS common helpers.
- `NFSD_V2` provides deprecated NFSv2 server support.
- `NFSD_V2_ACL` and `NFSD_V3_ACL` enable Solaris NFS ACL extension support for v2/v3 as applicable.
- `NFSD_V4` enables NFSv4 server support, depends on procfs, selects POSIX ACL support, RPCSEC_GSS_KRB5, grace-period tracking, and optionally SSC helper support.
- `NFSD_PNFS` is the shared internal pNFS server switch.
- `NFSD_BLOCKLAYOUT`, `NFSD_SCSILAYOUT`, and `NFSD_FLEXFILELAYOUT` enable pNFS layout types with their block/exportfs dependencies and warnings.
- `NFSD_V4_2_INTER_SSC` enables NFSv4.2 inter-server copy support.
- `NFSD_V4_SECURITY_LABEL` enables security label attributes for NFSv4.
- `NFSD_LEGACY_CLIENT_TRACKING` retains deprecated NFSv4 stable-storage tracking methods.
- `NFSD_V4_POSIX_ACLS` enables experimental draft POSIX ACL support for NFSv4.

Important interactions:
- Controls which objects from `fs/nfsd/Makefile` and `fs/nfs_common/Makefile` are built.
- Establishes feature selection relationships between NFSD, NFS common code, pNFS layouts, ACL support, and NFSv4 recovery support.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/Makefile -->
# File Research: sources/os/linux/linux/fs/nfsd/Makefile

Builds the Linux kernel NFS server module and optional protocol/layout components.

Key behavior:
- Adds the source directory include path for trace event headers.
- Builds `nfsd.o` when `CONFIG_NFSD` is enabled.
- Compiles `trace.o` first because trace macros are sensitive to include ordering.
- Core NFSD objects include service control, control filesystem, file handles, VFS access, exports, auth, lockd integration, reply cache, stats, file cache, NFSv3 proc/XDR, and netlink.
- Optional objects:
  - NFSv2 procedure/XDR support.
  - NFSv2/NFSv3 ACL support.
  - NFSv4 procedure, XDR, state, idmap, ACL, callback, recovery, and generated XDR support.
  - pNFS layout support and specific block/SCSI/flexfile layout encoders.
  - LOCALIO support.
  - debugfs support.
- Provides an `xdrgen` developer target to regenerate checked-in NFSv4.1 generated XDR files from `Documentation/sunrpc/xdr/nfs4_1.x`.

Important interactions:
- Mirrors the Kconfig feature matrix and determines which NFSD subsystems are linked into the server module.
- Notes that generated XDR files are checked in, so normal builds do not need the generator tooling.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/acl.h -->
# File Research: sources/os/linux/linux/fs/nfsd/acl.h

Declares common NFSD NFSv4 ACL helpers.

Key behavior:
- Forward-declares core NFSD ACL-related types.
- Declares helpers to compute ACL byte length, parse/get NFSv4 ACL who-type values, and encode who fields.
- Declares server-side conversion helpers:
  - `nfsd4_get_nfs4_acl()` to retrieve an NFSv4 ACL for a dentry.
  - `nfsd4_acl_to_attr()` to convert an NFSv4 ACL into NFSD attributes.
  - `sort_pacl_range()` to sort a POSIX ACL subrange.

Important interactions:
- Used by NFSD NFSv4 ACL and XDR handling code.
- Carries a permissive historical license notice in the header comment, while the file itself is not tagged with a Linux SPDX line.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/auth.c -->
# File Research: sources/os/linux/linux/fs/nfsd/auth.c

Implements NFSD credential override setup for servicing requests as the exported user.

Key behavior:
- `nfsexp_flags()` returns flavor-specific export flags when the request credential flavor has an override entry, otherwise falls back to the export’s default flags.
- `nfsd_setuser()` resets any old override credentials, prepares new credentials, and sets `fsuid`/`fsgid` from the RPC credential.
- Applies export squashing:
  - `NFSEXP_ALLSQUASH` maps user, group, and supplemental groups to anonymous identity.
  - `NFSEXP_ROOTSQUASH` maps root uid/gid and root supplemental groups to anonymous identity.
  - Otherwise reuses the request group list.
- Invalid uid/gid values are mapped to the export anonymous uid/gid.
- Installs supplemental groups and adjusts effective capabilities:
  - Non-root serving credentials drop the NFSD capability set.
  - Root serving credentials raise the NFSD capability set within permitted capabilities.
- Overrides current credentials with the prepared credentials.

Important interactions:
- Called by NFSD request paths before local filesystem operations.
- Enforces export-level identity mapping and capability constraints for kernel server file access.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/auth.h -->
# File Research: sources/os/linux/linux/fs/nfsd/auth.h

Declares NFSD authentication helper entry points.

Key behavior:
- Provides the prototype for `nfsd_setuser(struct svc_cred *cred, struct svc_export *exp)`.
- Documents that the helper sets the current process fsuid/fsgid and related credentials to represent the NFS client user.

Important interactions:
- Included by NFSD code that needs to switch request-handling credentials before VFS operations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/auth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/blocklayout.c -->
# File Research: sources/os/linux/linux/fs/nfsd/blocklayout.c

Implements NFSD pNFS block and SCSI layout operations.

Key behavior:
- `nfsd4_block_map_extent()` maps file offsets to filesystem block extents through exportfs block ops and converts `iomap` types to pNFS block extent states.
- Handles read/write differences:
  - Mapped extents become read-only or read-write data depending on layout iomode.
  - Unwritten extents may become invalid-data layouts for write layouts.
  - Holes can be represented as no-data layouts for reads.
  - Unsupported/delalloc cases return layout unavailable.
- `nfsd4_block_proc_layoutget()` validates grace state, block alignment, client maxcount, allocates a bounded extent array, maps enough extents to satisfy requested/minimum length, and adjusts the returned layout segment to extent boundaries.
- Layout commit decodes client layout updates and passes iomaps to exportfs block `commit_blocks()`, optionally applying a new size.
- Block layout `GETDEVICEINFO` returns a simple volume using the backing block device UUID, rejecting partition exports.
- Registers `bl_layout_ops` for block layout getdeviceinfo, layoutget, layoutcommit, and encoding callbacks.
- SCSI layout support manages per-client device fence state in an xarray.
- SCSI device info obtains a disk unique identifier, registers/reserves persistent-reservation keys, and returns a SCSI volume with the client PR key.
- SCSI layout commit decodes SCSI layout updates and shares block commit logic.
- `nfsd4_scsi_fence_client()` preempts a client’s persistent reservation key after recall failure and records fenced state to avoid repeated fencing loops.
- Registers `scsi_layout_ops` with SCSI-specific getdeviceinfo, layoutcommit, and fence callbacks.

Important interactions:
- Depends on filesystem `s_export_op->block_ops` for block mapping, UUID retrieval, and commit.
- Uses NFSD pNFS layout operation tables consumed by the NFSv4.1 layout server.
- Uses grace-period tracking to reject layout grants during recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/blocklayout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/blocklayoutxdr.c -->
# File Research: sources/os/linux/linux/fs/nfsd/blocklayoutxdr.c

Encodes and decodes NFSD pNFS block/SCSI layout opaque XDR payloads.

Key behavior:
- `nfsd4_block_encode_layoutget()` encodes the layout body length, extent count, and each extent’s device ID, file offset, length, storage offset, and extent state.
- `nfsd4_block_encode_volume()` encodes either:
  - Simple block volumes with signature offset and opaque signature.
  - SCSI volumes with code set, designator type, designator, and persistent-reservation key.
- `nfsd4_block_encode_getdeviceinfo()` handles the RFC maxcount-zero case by returning a zero-length body, otherwise encodes all volumes and backfills total length and volume count.
- `nfsd4_block_decode_layoutupdate()` decodes block layoutcommit extent arrays, validates total length, allocates iomaps, checks file offset/length/storage offset block alignment, requires `PNFS_BLOCK_READWRITE_DATA`, and returns iomaps for commit.
- `nfsd4_scsi_decode_layoutupdate()` decodes SCSI layoutcommit ranges, validates encoded size, allocates iomaps, and checks offset/length alignment.

Important interactions:
- Shared by block layout and SCSI layout server operations in `blocklayout.c`.
- Produces and consumes opaque layout bodies used inside higher-level NFSv4.1 layoutget/getdeviceinfo/layoutcommit XDR.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/blocklayoutxdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/blocklayoutxdr.h -->
# File Research: sources/os/linux/linux/fs/nfsd/blocklayoutxdr.h

Defines NFSD pNFS block/SCSI layout wire helper structures and XDR helper prototypes.

Key behavior:
- Defines `PNFS_BLOCK_LAYOUT4_SIZE`, the wire size of a layout with zero extents.
- Defines `struct pnfs_block_extent` with device ID, file offset, length, storage offset, and extent state.
- Defines `struct pnfs_block_range` for file offset/length ranges.
- Defines flexible-array `struct pnfs_block_layout` for returned extent arrays.
- Defines `PNFS_BLOCK_UUID_LEN` as a defensive upper bound for simple-volume UUID/signature length.
- Defines `struct pnfs_block_volume` for simple and SCSI volume encodings.
- Defines flexible-array `struct pnfs_block_deviceaddr` for device-address volume lists.
- Declares block getdeviceinfo/layoutget encoders and block/SCSI layoutupdate decoders.

Important interactions:
- Included by `blocklayout.c` and `blocklayoutxdr.c`.
- Provides the shared in-memory representation used between pNFS layout logic and XDR encode/decode routines.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/blocklayoutxdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/cache.h -->
# File Research: sources/os/linux/linux/fs/nfsd/cache.h

Defines the NFSD duplicate request/reply cache interface and cache-entry structure.

Key behavior:
- Defines `struct nfsd_cacherep`, keyed by XID, request checksum, procedure, protocol, version, request length, and peer address.
- Stores entries in both an rb-tree node and LRU list.
- Tracks cache entry state (`RC_UNUSED`, `RC_INPROG`, `RC_DONE`), reply type, secure-port status, timestamp, and either a reply buffer vector or status value.
- Defines cache lookup outcomes: `RC_DROPIT`, `RC_REPLY`, and `RC_DOIT`.
- Defines cache types: no-cache, status reply, and buffered reply.
- Sets cache expiration to 120 seconds and request checksum length to 256 bytes.
- Declares slab lifecycle, per-net reply cache lifecycle, lookup/update, and stats display helpers.

Important interactions:
- Used by NFSD procedure dispatch to detect duplicate non-idempotent RPCs and replay cached replies safely.
- `sockaddr_in6` is used intentionally for compact address storage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/current_stateid.h -->
# File Research: sources/os/linux/linux/fs/nfsd/current_stateid.h

Declares helpers for managing NFSv4 compound current stateid state.

Key behavior:
- Declares `clear_current_stateid()`.
- Declares setters for operations that produce/update current stateid:
  - open downgrade
  - open
  - lock
  - close
- Declares getters for operations that consume current stateid:
  - open downgrade
  - delegation return
  - free stateid
  - setattr
  - close
  - locku
  - read
  - write

Important interactions:
- Included by NFSD NFSv4 compound processing code.
- Encapsulates the RFC current-stateid mechanism across NFSv4 operations encoded in `union nfsd4_op_u`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/current_stateid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/debugfs.c -->
# File Research: sources/os/linux/linux/fs/nfsd/debugfs.c

Implements NFSD debugfs controls for server I/O behavior.

Key behavior:
- Creates `/sys/kernel/debug/nfsd`.
- Exposes `disable-splice-read`:
  - `0` allows page-splicing reads.
  - `1` forces READ to use only iov-iter reads.
  - Re-enabling splice read forces read I/O mode back to buffered.
- Exposes `io_cache_read`:
  - buffered I/O
  - buffered dropbehind/dontcache
  - direct I/O
  - dontcache/direct settings force splice-read disabled.
- Exposes `io_cache_write`:
  - buffered I/O
  - dontcache/dropbehind
  - direct I/O
- Optionally exposes `delegated_timestamps` when NFSDv4 is enabled.
- `nfsd_debugfs_init()` creates the directory and files.
- `nfsd_debugfs_exit()` removes the tree recursively and clears the top-level pointer.

Important interactions:
- Controls global NFSD read/write I/O policy variables used by server VFS I/O paths.
- Debugfs settings take effect immediately across NFS versions, exports, and NFSD network namespaces.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/debugfs.c -->