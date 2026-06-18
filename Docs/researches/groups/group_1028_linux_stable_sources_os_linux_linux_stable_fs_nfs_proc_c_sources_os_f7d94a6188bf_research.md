# Group Research: group_1028_linux_stable_sources_os_linux_linux_stable_fs_nfs_proc_c_sources_os_f7d94a6188bf

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux-stable`. All listed source files were read completely in manifest order.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/proc.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/proc.c

Purpose: Implements the NFSv2 client RPC operation table and the v2-specific glue between generic NFS/VFS operations and wire procedures.

Key responsibilities:
- Provides v2 handlers for `getroot`, `getattr`, `setattr`, `lookup`, `readlink`, create/remove/link/symlink/mkdir/rmdir/mknod, `readdir`, `statfs`, `fsinfo`, and `pathconf`.
- Builds `rpc_message` calls around `nfs_procedures[NFSPROC_*]`.
- Handles NFSv2 protocol quirks:
  - `mknod` is encoded through `CREATE`.
  - symlink creation receives no returned attributes/filehandle, so instantiation falls back to lookup.
  - no real COMMIT support; commit hooks are `BUG()`.
  - writes are always `NFS_FILE_SYNC`.
  - locks are bounded to 32-bit v2 offsets.
- Defines v2 inode operations and exports `nfs_v2_clientops`.

Integration:
- Used by the generic NFS client through `struct nfs_rpc_ops`.
- Calls into shared NFS helpers such as `nfs_instantiate`, `nfs_mark_for_revalidate`, `nfs_refresh_inode`, `nfs_writeback_update_inode`, and lockd via `nlmclnt_proc`.
- Supplies pageio setup/done hooks used by `read.c` and `write.c`.

Risks and notes:
- v2 lacks server-side delegation support; delegation hooks are stubs or force writeback.
- Root probing retries with the default RPC client when auth-specific client calls fail.
- Commit hooks intentionally must not be reached for v2.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/read.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/read.c

Purpose: Implements NFS buffered read and readahead using folios, pageio aggregation, netfs integration, and async RPC completion.

Key responsibilities:
- Allocates/frees read pageio headers from `nfs_read_data` slab cache.
- Initializes read pageio descriptors, choosing pNFS layout-driver read ops when available unless forced to MDS.
- Handles read completion:
  - marks folios uptodate once all grouped requests are complete,
  - zero-fills EOF or partial-read gaps,
  - records per-open-context errors,
  - completes netfs read accounting.
- Handles short reads by retrying the remaining byte range or forcing MDS retry for non-RPC pNFS drivers.
- Implements `nfs_read_folio` and `nfs_readahead`:
  - flushes pending writes before a locked folio read,
  - rejects stale inodes,
  - tries `nfs_netfs_*` first,
  - falls back to direct NFS pageio.

Integration:
- Uses version-specific `NFS_PROTO(inode)->read_setup/read_done`.
- Feeds common pageio via `nfs_pageio_init`, `nfs_pageio_add_request`, and `nfs_pageio_complete`.
- Integrates with fscache/netfs, pNFS, delegation atime updates, tracepoints, and NFS I/O stats.

Risks and notes:
- Read path assumes no mirrored reads and warns if mirror count differs from one.
- EOF handling depends on `good_bytes` and request ordering.
- File-less readahead must discover a readable open context or fails with `-EBADF`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/super.c

Purpose: Handles NFS client filesystem registration, superblock lifecycle, statfs, mount option display, mount authentication negotiation, remount checks, and module parameters.

Key responsibilities:
- Defines `nfs_sops` superblock operations.
- Registers/unregisters NFS and optional NFSv4 filesystems, NFS sysctl, ACL shrinker, and SSC ops.
- Implements active superblock references via `nfs_sb_active` / `nfs_sb_deactive`.
- Implements `nfs_statfs`, translating NFS byte counts into VFS block counts.
- Renders mount options and stats for `/proc/mounts` and mountstats:
  - protocol version, sizes, attribute cache timers, locking, transport, security flavor, xprtsec, fscache, pNFS, sessions, NFSv4 lease data, and counters.
- Handles mountd negotiation for v2/v3, including security flavor selection and fallback.
- Implements `nfs_try_get_tree`, `nfs_get_tree_common`, superblock sharing comparison, and `nfs_kill_super`.
- Validates remount compatibility and probes the server on remount.
- Defines NFSv4 module parameters such as callback port/thread count, idmap behavior, session slots, implementation ID, lost-lock recovery, and delay retransmission.

Integration:
- Ties fs_context mount data to `nfs_server` creation through version-specific rpc ops.
- Coordinates with sysfs server naming, fscache cookies, export ops, security mount option compatibility, SUNRPC stats, pNFS, and NFSv4 callback/idmap code.
- Used by all NFS protocol versions.

Risks and notes:
- Superblock reuse is conservative and compares address, fsid, user namespace, selected auth flavor, mount flags, sizes, cache timers, and security options.
- `noac` implies synchronous superblock behavior.
- Binary legacy mount data can skip normal remount option checks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/symlink.c

Purpose: Implements NFS symlink inode operations and symlink target caching in the page cache.

Key responsibilities:
- `nfs_symlink_filler` calls the protocol `readlink` op into page zero and completes folio read state.
- `nfs_get_link` supports both RCU pathwalk and normal lookup:
  - RCU mode validates mapping and returns `-ECHILD` if it cannot safely use a cached uptodate folio.
  - non-RCU mode revalidates mapping and reads the symlink folio if needed.
- Exports `nfs_symlink_inode_operations` with `get_link`, `getattr`, and `setattr`.

Integration:
- Uses `NFS_PROTO(inode)->readlink`, NFS mapping revalidation, and VFS delayed calls via `page_put_link`.

Risks and notes:
- Symlink cache is single-folio/page-oriented, matching legacy NFS symlink target handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/sysctl.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/sysctl.c

Purpose: Registers global NFS client sysctl tunables under `fs/nfs`.

Key responsibilities:
- Exposes `nfs_mountpoint_timeout` backed by `nfs_mountpoint_expiry_timeout` using jiffies conversion.
- Exposes `nfs_congestion_kb` backed by the writeback congestion threshold.
- Provides `nfs_register_sysctl` and `nfs_unregister_sysctl`.

Integration:
- Called from `register_nfs_fs` / `unregister_nfs_fs` in `super.c`.
- `nfs_congestion_kb` is consumed by `write.c`.

Risks and notes:
- Registration failure propagates as `-ENOMEM`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/sysfs.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/sysfs.c

Purpose: Implements NFS sysfs objects for global NFS, per-network-namespace NFS client state, and per-server controls/metadata.

Key responsibilities:
- Creates `/sys/fs/nfs` kset with network namespace-aware child handling.
- Creates per-net `net/nfs_client` object with writable `identifier`.
- Creates per-server kobjects, initially named `server-%d`, later renamed to superblock id and back during superblock attach/detach.
- Exposes server `shutdown`:
  - writing `1` marks `NFS_MOUNT_SHUTDOWN`,
  - shuts down main and ACL RPC clients,
  - shuts down lockd client if present,
  - shuts down the shared `nfs_client` only once all superblocks are marked shutdown.
- Optionally exposes NFSv4.1 implementation ID domain/name.
- Optionally exposes `localio` status.
- Creates sysfs links from NFS server objects to underlying SUNRPC clients.

Integration:
- Called by NFS namespace setup/teardown and server lifecycle code.
- Uses RCU for identifier storage and namespace association.
- Coordinates with lockd, RPC task cancellation, and `nfs_mark_client_ready`.

Risks and notes:
- Shutdown is global to the server/client object and intentionally cancels outstanding RPCs with `-EIO`.
- Identifier replacement uses `xchg` plus `synchronize_rcu` before freeing the old string.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/sysfs.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/sysfs.h

Purpose: Declares NFS sysfs data structures and lifecycle helpers.

Key responsibilities:
- Defines `CONTAINER_ID_MAXLEN`.
- Defines `struct nfs_netns_client` containing two kobjects, a net pointer, and RCU-protected identifier.
- Declares sysfs init/exit, per-net setup/destroy, RPC-client link creation, server add/move/remove helpers.

Integration:
- Included by NFS client namespace and superblock/server code.
- Paired with implementation in `sysfs.c`.

Risks and notes:
- Header exposes only lifecycle and linking APIs, keeping sysfs details mostly private to `sysfs.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/unlink.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/unlink.c

Purpose: Implements NFS sillyrename and deferred unlink handling for open-but-unlinked files.

Key responsibilities:
- Allocates `nfs_unlinkdata` for async deferred unlink operations.
- Marks dentries with `DCACHE_NFSFS_RENAMED` and stores unlink metadata in `d_fsdata`.
- Performs async unlink after the final dentry reference is dropped.
- Handles dentry alias races using `d_alloc_parallel` and transfers sillyrename metadata to matching aliases.
- Provides async rename helpers used by sillyrename.
- Generates hidden `.nfs<fileid><counter>` names and renames open files to those names before unlinking later.
- Cancels queued async unlink if the sillyrename RPC fails.

Integration:
- Uses protocol hooks `unlink_setup`, `unlink_rpc_prepare`, `unlink_done`, `rename_setup`, `rename_rpc_prepare`, and `rename_done`.
- Interacts with dcache lookup/aliasing, inode revalidation, lock semaphores, NFS delegation return, RPC async task machinery, and NFS stats/tracepoints.

Risks and notes:
- If sillyrename result is interrupted/unknown, it drops dentries and forces future lookup revalidation.
- Hidden sillyrename names are generated per fileid plus static counter and checked by negative lookup.
- Memory ownership is delicate: dentry refs, inode refs, credentials, superblock active refs, and `d_fsdata` all participate.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/unlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/write.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/write.c

Purpose: Implements NFS buffered writeback, dirty folio request tracking, unstable-write commit handling, pNFS commit integration, write congestion, and writeback cache initialization.

Key responsibilities:
- Allocates write and commit headers through slab caches backed by mempools.
- Tracks folio-associated `nfs_page` requests through folio private data and inode request counts.
- Joins multiple subrequests for a folio before writeback, removing them from write/commit lists safely.
- Implements VFS writeback:
  - `nfs_writepages`,
  - `nfs_writepage_locked`,
  - `nfs_do_writepage`,
  - per-folio writeback/commit helpers.
- Updates or creates dirty write requests through `nfs_update_folio`.
- Flushes incompatible requests when a write comes from a different open context or lock owner.
- Implements optional whole-page write extension when safe, unless disabled by mount option or sync mode.
- Handles async write completion:
  - stable writes remove requests,
  - unstable writes move requests to commit lists,
  - errors mark mapping/superblock writeback errors and invalidate cached state.
- Implements COMMIT lifecycle:
  - scans commit lists,
  - builds `nfs_commit_data`,
  - uses pNFS commit first when available,
  - falls back to MDS commit,
  - validates write verifier,
  - redirties data on verifier mismatch.
- Handles short writes by retrying from progress point or switching to stable writes.
- Provides writeback flush APIs such as `nfs_wb_all`, `nfs_wb_folio`, `nfs_wb_folio_cancel`, and reclaim/migration support.
- Initializes write congestion threshold based on memory, capped at 256 MiB.

Integration:
- Uses version-specific protocol hooks `write_setup`, `write_done`, `commit_setup`, `commit_done`, and `commit_rpc_prepare`.
- Cooperates with pNFS, localio commits, fscache invalidation, delegation timestamp handling, SUNRPC priorities, file locking, errseq writeback error reporting, and NFS tracing/stats.
- Sysctl `nfs_congestion_kb` controls congestion thresholds.

Risks and notes:
- Request lifetime and page-group locking are complex; correctness depends on `PG_*` flags and krefs.
- Commit verifier mismatch triggers rewrite to protect against server restart/unstable data loss.
- Non-fatal write errors may redirty and retry, while fatal server errors launder requests and invalidate state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/nfs_common/Makefile

Purpose: Build rules for NFS code shared by client and server.

Key responsibilities:
- Builds ACL support when `CONFIG_NFS_ACL_SUPPORT` is enabled.
- Builds localio support and its tracepoint object when `CONFIG_NFS_COMMON_LOCALIO_SUPPORT` is enabled.
- Builds grace period support, server-side-copy helper, and common status translation based on config symbols.
- Adds local include path for `localio_trace.o`.

Integration:
- Produces shared modules/objects consumed by NFS client and NFSD.

Risks and notes:
- Feature availability is entirely Kconfig-driven.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/common.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs_common/common.c

Purpose: Provides shared NFS status-code translation helpers.

Key responsibilities:
- Maps NFSv2/v3 status codes to Linux negative errno via `nfs_stat_to_errno`.
- Maps NFSv4 status codes to Linux errno via `nfs4_stat_to_errno`, using common and v4-specific tables.
- Maps Linux errno to NFSv4 status for LOCALIO via `nfs_localio_errno_to_nfs4_stat`.

Integration:
- Exported GPL symbols used by NFS client, NFSD, and localio paths.
- Includes localio-specific mappings where errno-to-NFS status differs from normal NFSv4 decode tables.

Risks and notes:
- Unknown v2/v3 statuses become `-EIO`.
- Unknown out-of-range v4 statuses become `-EREMOTEIO`; otherwise untranslated v4 statuses may be returned as `-stat` for recovery paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/grace.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs_common/grace.c

Purpose: Shared infrastructure for NFS/lockd grace periods per network namespace.

Key responsibilities:
- Maintains per-net grace-period lists of `struct lock_manager`.
- `locks_start_grace` adds a lock manager to the namespace grace list.
- `locks_end_grace` removes it, safely allowing repeated end calls.
- `locks_in_grace` reports whether ordinary locks should be blocked.
- `opens_in_grace` reports whether opens should be blocked based on managers with `block_opens`.
- Registers pernet operations to initialize and validate grace lists.

Integration:
- Used by lockd and NFSv4/NFSD state recovery paths.
- `blocklayout.c` checks `locks_in_grace` before issuing pNFS layouts.

Risks and notes:
- Uses a global spinlock for grace list protection.
- Warns on double add and on namespace teardown with non-empty grace list.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/grace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/localio_trace.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs_common/localio_trace.c

Purpose: Instantiates NFS LOCALIO tracepoints.

Key responsibilities:
- Defines `CREATE_TRACE_POINTS` and includes `localio_trace.h`.

Integration:
- Built with localio common support.
- Provides tracepoint definitions used by `nfslocalio.c`.

Risks and notes:
- Must be compiled exactly once to materialize tracepoints.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/localio_trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/localio_trace.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs_common/localio_trace.h

Purpose: Defines trace events for NFS LOCALIO client enable/disable.

Key responsibilities:
- Declares trace system `nfs_localio`.
- Defines event class `nfs_local_client_event` capturing NFS protocol version and server hostname.
- Defines `nfs_localio_enable_client` and `nfs_localio_disable_client`.

Integration:
- Included by `localio_trace.c` to instantiate and by `nfslocalio.c` to emit events.
- Uses standard Linux tracepoint infrastructure and NFS/SUNRPC trace helpers.

Risks and notes:
- Trace include path/file macros are set for local header generation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/localio_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/nfs_ssc.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs_common/nfs_ssc.c

Purpose: Shared registration table allowing NFSD server-side-copy code to call NFS client module operations.

Key responsibilities:
- Exports global `nfs_ssc_client_tbl`.
- Registers/unregisters NFSv4.2 client SSC ops with `nfs42_ssc_register` / `nfs42_ssc_unregister`.
- Registers/unregisters broader NFS client ops with `nfs_ssc_register` / `nfs_ssc_unregister`.
- Provides empty stubs when relevant NFSv4.2 config is disabled.

Integration:
- Bridges NFSD inter-server COPY support with NFS client implementation.
- `super.c` registers NFS client SSC ops under `CONFIG_NFS_V4_2`.

Risks and notes:
- Unregister only clears the table when the pointer matches, preventing accidental removal of replaced ops.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/nfs_ssc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/nfsacl.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs_common/nfsacl.c

Purpose: Encodes and decodes Solaris-style NFSv3 ACL protocol data to/from Linux POSIX ACLs.

Key responsibilities:
- Encodes ACL entries into XDR buffers or streams.
- Adds a Solaris-compatible ACL mask entry for minimal three-entry POSIX ACLs.
- Writes owner and owning group ids for `ACL_USER_OBJ` and `ACL_GROUP_OBJ`.
- Decodes XDR ACL arrays into `posix_acl`.
- Validates users, groups, permissions, tags, maximum entry count, and stream/buffer lengths.
- Sorts decoded ACL entries into canonical POSIX order.
- Removes bogus Solaris mask entries from minimal ACLs when mask permissions match group object permissions.

Integration:
- Exported to NFS client/server ACL protocol implementations.
- Uses generic SUNRPC XDR helpers and Linux POSIX ACL helpers.

Risks and notes:
- Encoding minimal ACLs uses a stack fake ACL to avoid allocation in fatal contexts.
- Decoder allocates ACL storage lazily on first decoded entry.
- Solaris interoperability drives several non-obvious transformations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/nfsacl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/nfslocalio.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs_common/nfslocalio.c

Purpose: Implements shared NFS LOCALIO protocol-bypass support between an NFS client and a local NFSD server.

Key responsibilities:
- Maintains a global list of client UUID records during localio probing.
- Initializes, begins, and ends UUID probing lifecycle.
- Marks a UUID as local once NFSD confirms it, moving it to the NFSD net namespace local client list.
- Holds an NFSD module reference and auth domain reference while localio is active.
- Enables/disables localio client tracing.
- Invalidates all local clients during NFSD net teardown.
- Opens local filehandles through NFSD callbacks while safely acquiring NFSD net/server references.
- Tracks cached local `nfsd_file` handles per NFS file localio record.
- Closes local filehandles safely while racing with client disable.
- Exports `nfs_to`, the NFSD operation vector used by NFS localio code.

Integration:
- Depends on callbacks supplied by NFSD through `struct nfsd_localio_operations`.
- Used by NFS read/write/commit paths that can bypass RPC when client and server are local.
- Uses RCU, spinlocks, module refs, auth-domain refs, and wait-var synchronization.

Risks and notes:
- Lock ordering is explicitly documented: UUID lock, global UUID lock, then namespace local-client lock.
- Net pointer is not a counted reference; safety relies on RCU and `nfsd_net_try_get`.
- File close/disable races are coordinated through `nfl->nfs_uuid` and wait variables.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs_common/nfslocalio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/Kconfig

Purpose: Declares kernel configuration options for the in-kernel NFS server.

Key responsibilities:
- Defines `NFSD` core server support and its dependencies/selects.
- Exposes deprecated NFSv2 support and v2/v3 ACL protocol options.
- Exposes NFSv4 server support and dependent features.
- Defines pNFS layout options:
  - block layouts,
  - SCSI layouts,
  - flexfile layouts.
- Defines NFSv4.2 inter-server server-to-server COPY support.
- Defines NFSv4 security labels.
- Defines deprecated legacy client tracking.
- Defines experimental NFSv4 POSIX draft ACL support.

Integration:
- Drives compilation in `fs/nfsd/Makefile` and shared `fs/nfs_common` objects.
- Selects support libraries including SUNRPC, LOCKD, EXPORTFS, NFS_COMMON, GRACE_PERIOD, RPCSEC_GSS, and NFS SSC helper.

Risks and notes:
- Several options are explicitly deprecated or experimental.
- NFSv3 server support is always present when `NFSD` is selected.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/Makefile

Purpose: Builds the NFSD module and optional feature objects.

Key responsibilities:
- Adds local include path for trace events.
- Builds core `nfsd.o` from service, control, filehandle, VFS, export, auth, lockd, duplicate reply cache, stats, filecache, NFSv3, and netlink objects.
- Ensures `trace.o` is compiled first.
- Adds objects for NFSv2, ACL extensions, NFSv4, pNFS layouts, localio, and debugfs based on configs.
- Provides `xdrgen` phony target for regenerating checked-in NFSv4 XDR code from documentation XDR definitions.

Integration:
- Mirrors Kconfig feature selection.
- Ties generated NFSv4 XDR files to `tools/net/sunrpc/xdrgen`.

Risks and notes:
- Normal builds use checked-in generated XDR code; regeneration is developer-only.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/acl.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/acl.h

Purpose: Declares common NFSv4 ACL handling APIs for NFSD.

Key responsibilities:
- Forward declares NFSv4 ACL, service request/filehandle, attrs, and file type structures.
- Declares helpers for NFSv4 ACL byte sizing, who-type decoding, and who field encoding.
- Declares server-side ACL fetch and ACL-to-attribute conversion.
- Declares POSIX ACL range sorting.

Integration:
- Used by NFSD NFSv4 ACL implementation and XDR/attribute conversion paths.

Risks and notes:
- Header carries a BSD-style historical license block while source tree uses kernel-compatible terms.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/auth.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/auth.c

Purpose: Applies NFS export authentication and credential squashing to NFSD worker thread credentials.

Key responsibilities:
- `nfsexp_flags` selects export flags matching the RPC credential pseudoflavor, falling back to export default flags.
- `nfsd_setuser`:
  - reverts any old override credentials,
  - prepares new credentials,
  - sets fsuid/fsgid from RPC credentials,
  - applies `all_squash` and `root_squash`,
  - remaps invalid ids to anonymous ids,
  - copies/sorts group info as needed,
  - drops or raises NFSD capability set depending on whether fsuid is root,
  - installs override credentials.

Integration:
- Used by NFSD request handling before filesystem operations.
- Depends on export flavor metadata and `svc_cred`.

Risks and notes:
- Each worker allocates its own squashed group list for root-squash handling.
- OOM during group allocation aborts prepared creds and returns `-ENOMEM`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/auth.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/auth.h

Purpose: Declares NFSD credential setup.

Key responsibilities:
- Declares `nfsd_setuser(struct svc_cred *, struct svc_export *)`.

Integration:
- Included by NFSD request/auth paths that need to install client-derived credentials.

Risks and notes:
- Minimal header; implementation details remain in `auth.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/auth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/blocklayout.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/blocklayout.c

Purpose: Implements NFSD pNFS block and SCSI layout operations.

Key responsibilities:
- Maps filesystem extents with `s_export_op->map_blocks` and translates iomap types into pNFS block extent states.
- Handles layoutget:
  - rejects requests during grace,
  - requires block-aligned offsets,
  - enforces client `lg_maxcount`,
  - caps allocation at one page,
  - builds an extent array,
  - validates `lg_minlength`.
- Handles layoutcommit by decoding client layout updates and calling `s_export_op->commit_blocks` with mtime/size attributes.
- For block layout:
  - returns simple block device volume identity via exportfs UUID.
- For SCSI layout:
  - obtains unique disk designator,
  - registers and reserves persistent reservation key,
  - tracks client/device fencing in an xarray,
  - fences clients with PR preempt when recalls fail.
- Exports `bl_layout_ops` and `scsi_layout_ops`.

Integration:
- Depends on exportfs block operations, iomap, NFSD pNFS layout core, filecache, VFS helpers, and tracepoints.
- Uses `locks_in_grace` from `fs/nfs_common/grace.c`.
- Pairs with XDR helpers in `blocklayoutxdr.c`.

Risks and notes:
- Device IDs are advertised with notification flags to encourage Linux client caching despite RFC ambiguity.
- SCSI fencing carefully avoids infinite retry when a PR preempt may already have reached the device.
- Partitions are rejected for getdeviceinfo.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/blocklayout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/blocklayoutxdr.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/blocklayoutxdr.c

Purpose: Encodes and decodes pNFS block/SCSI layout opaque XDR payloads for NFSD.

Key responsibilities:
- Encodes layoutget extent arrays:
  - deviceid,
  - file offset,
  - extent length,
  - storage offset,
  - extent state.
- Encodes getdeviceinfo volume arrays for simple block and SCSI volumes.
- Handles zero `gd_maxcount` by returning zero-length notification marker per RFC guidance.
- Decodes block layoutcommit updates:
  - validates exact expected payload size,
  - decodes deviceid and extent fields,
  - enforces file/storage offset and length alignment,
  - requires `PNFS_BLOCK_READWRITE_DATA`,
  - produces iomap array.
- Decodes SCSI layoutcommit updates as aligned file offset/length ranges.

Integration:
- Called by `blocklayout.c` layout ops.
- Uses NFSD XDR helpers, SUNRPC XDR streams, and iomap structures.

Risks and notes:
- Allocation failure maps to `nfserr_delay`.
- Bad payload length or decode failure maps to `nfserr_bad_xdr`; alignment and invalid extent state map to `nfserr_inval`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/blocklayoutxdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/blocklayoutxdr.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/blocklayoutxdr.h

Purpose: Declares pNFS block/SCSI layout wire helper structures and XDR functions.

Key responsibilities:
- Defines wire-size constants for block layout and UUID limits.
- Defines in-memory representations:
  - `pnfs_block_extent`,
  - `pnfs_block_range`,
  - counted flexible `pnfs_block_layout`,
  - `pnfs_block_volume`,
  - counted flexible `pnfs_block_deviceaddr`.
- Declares getdeviceinfo/layoutget encoders and block/SCSI layoutupdate decoders.

Integration:
- Shared by `blocklayout.c` and `blocklayoutxdr.c`.
- Includes block device and NFSD NFSv4 XDR definitions.

Risks and notes:
- UUID length is capped at 128 as an implementation guard, not a protocol limit.
- SCSI designator buffer is fixed at 256 bytes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/blocklayoutxdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/cache.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/cache.h

Purpose: Declares NFSD duplicate request/reply cache structures and APIs.

Key responsibilities:
- Defines `struct nfsd_cacherep`, keyed by XID, checksum, procedure, protocol, version, request length, address, and privileged-source-port flag.
- Supports RB-tree lookup and LRU aging.
- Defines cache entry states: unused, in-progress, done.
- Defines lookup outcomes: drop, reply, do it.
- Defines cache payload types: no cache, reply status, reply buffer.
- Sets expiration and checksum length constants.
- Declares slab lifecycle, per-net cache init/shutdown, lookup/update, and stats show APIs.

Integration:
- Used by NFSD request dispatch/cache implementation in `nfscache.c`.
- Tied to SUNRPC service requests and NFSD net namespace state.

Risks and notes:
- Uses `sockaddr_in6` rather than `sockaddr_storage` to reduce entry size.
- Checksums only the first 256 bytes of request payload.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/current_stateid.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/current_stateid.h

Purpose: Declares helpers for NFSv4 compound current-stateid handling.

Key responsibilities:
- Declares clearing of current stateid in compound state.
- Declares setters for stateid-producing operations:
  - open downgrade,
  - open,
  - lock,
  - close.
- Declares getters for stateid-consuming operations:
  - open downgrade,
  - delegation return,
  - free stateid,
  - setattr,
  - close,
  - locku,
  - read,
  - write.

Integration:
- Used by NFSD NFSv4 compound operation processing.
- Depends on `state.h` and `xdr4.h`.

Risks and notes:
- Header only declares operation-specific plumbing; actual stateid semantics are implemented elsewhere.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/current_stateid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/debugfs.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/debugfs.c

Purpose: Provides debugfs controls for global NFSD I/O behavior.

Key responsibilities:
- Creates `/sys/kernel/debug/nfsd`.
- Exposes `disable-splice-read`:
  - `0` allows page splicing for NFS READ,
  - `1` forces iov-iter read.
- Exposes `io_cache_read`:
  - buffered,
  - dontcache/dropbehind,
  - direct I/O.
- Exposes `io_cache_write`:
  - buffered,
  - dontcache/dropbehind,
  - direct I/O accepted by setter.
- Ensures enabling dontcache/direct read disables splice read.
- Optionally exposes NFSv4 delegated timestamp toggle.
- Provides init/exit helpers for debugfs tree.

Integration:
- Built only with `CONFIG_DEBUG_FS`.
- Mutates global NFSD tunables consumed by server VFS I/O paths.

Risks and notes:
- Settings apply immediately across all NFS versions, exports, and NFSD net namespaces.
- Invalid cache mode values return `-EINVAL`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/debugfs.c -->