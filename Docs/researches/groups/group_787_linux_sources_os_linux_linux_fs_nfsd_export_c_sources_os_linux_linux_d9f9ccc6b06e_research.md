# Group Research: group_787_linux_sources_os_linux_linux_fs_nfsd_export_c_sources_os_linux_linux_d9f9ccc6b06e

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/export.c -->
# File Research: sources/os/linux/linux/fs/nfsd/export.c

Read completely: 1595 lines.

NFSD export cache implementation and validation logic. It maintains the two sunrpc caches that connect client identities to exported paths and fsid/filehandle fragments, parses mountd export updates, validates filesystem exportability, checks per-export security policy, exposes exports via seq_file, and manages per-net namespace export cache lifecycle.

Key responsibilities:
- Implements the expkey cache (`nfsd.fh`) mapping auth domain plus fsid type/value to an exported path, including upcall request formatting, userspace parse/update handling, hash/match/init/update callbacks, and deferred RCU work release.
- Implements the export cache (`nfsd.export`) mapping auth domain plus path to `struct svc_export` options, including path parsing, expiry, flags, anon uid/gid, fsid, UUID fsid, NFSv4 fs_locations, secinfo, xprtsec modes, pNFS layout setup, and export stats.
- Validates exports in `check_export`: only directories, symlinks, and regular files; V4ROOT is forced read-only; non-device filesystems need fsid or UUID; filesystems must have usable export operations; idmapped mounts are rejected; subtree checking is rejected when the filesystem forbids it.
- Provides lookup APIs used by request processing: `rqst_exp_get_by_name`, `rqst_exp_find`, `rqst_exp_parent`, `rqst_find_fsidzero_export`, `exp_rootfh`, and `exp_pseudoroot`.
- Enforces access policy via `check_xprtsec_policy`, `check_security_flavor`, and `check_nfsd_access`, combining TLS/mTLS transport requirements with RPC auth flavor/secinfo rules and selected GSS bypass behavior.
- Formats `/proc/fs/nfsd/exports` and export stats output, including option names, fsid, anon credentials, fs_locations, UUIDs, secinfo runs, and per-export stale/read/write counters.
- Initializes, flushes, and shuts down per-net export and expkey caches; module-level release work is drained with `rcu_barrier()` and `flush_workqueue()`.

Important interactions:
- Uses sunrpc cache infrastructure (`cache_detail`, `sunrpc_cache_lookup_rcu`, `sunrpc_cache_update`, `cache_check`, `cache_purge`).
- Uses auth domains, nfsd file cache purge on expkey flush, VFS path/exportfs helpers, pNFS layout setup, request security state, and `nfsd_net` per-net cache pointers.
- Deferred object freeing depends on the module-level `nfsd_export_wq`.

Notable risks:
- Export parsing accepts a stream of positional tokens from userspace; validation order is intentional, especially for dummy exportfs probes and anon uid/gid checks.
- Security behavior depends on subtle fallback between `rq_client` and deprecated GSS client domains, and on secinfo list presence.
- Shutdown correctness depends on draining RCU callbacks and queued release work before destroying per-net cache storage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/export.h -->
# File Research: sources/os/linux/linux/fs/nfsd/export.h

Read completely: 142 lines.

Public NFSD export data model and function declarations shared by export lookup, filehandle verification, request processing, and procfs reporting.

Key responsibilities:
- Defines NFSv4 fs_locations structures and the `MAX_FS_LOCATIONS` limit.
- Defines secinfo flavor storage, `MAX_SECINFO_LIST`, and `EX_UUID_LEN`.
- Defines per-export stats counters for stale filehandles, read bytes, and write bytes.
- Defines `struct svc_export`, carrying cache state, auth domain, export flags/fsid/path, anon credentials, UUID, fs_locations, secinfo flavor list, pNFS layout/device data, xprtsec modes, stats, and deferred RCU work.
- Defines `struct svc_expkey`, mapping client plus fsid key to an export path.
- Provides convenience predicates for sync/nohide/write-gather options and inline cache ref helpers `exp_put` and `exp_get`.
- Declares export lifecycle, lookup, pseudoroot, root filehandle, and access-check APIs.

Dependencies:
- Pulls in sunrpc cache, percpu counters, workqueues, UAPI export flags, and NFSv4 types.

Notable risks:
- `struct svc_export` is the shared contract for many nfsd subsystems; ownership of pointer fields such as `ex_uuid`, `ex_fslocs.locations`, `ex_devid_map`, and `ex_stats` is transferred during cache updates.
- `svc_expkey.ek_fsid` stores multiple fsid formats in a fixed six-word array, so callers must use `key_len()` consistently.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/export.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/filecache.c -->
# File Research: sources/os/linux/linux/fs/nfsd/filecache.c

Read completely: 1430 lines.

NFSD open-file cache implementation. It caches `struct file` instances by inode, credential, network namespace, access mode, and garbage-collection policy, while coordinating delayed close, writeback-error detection, localio acquisition, fsnotify invalidation, lease conflicts, shrinker reclaim, and statistics.

Key responsibilities:
- Maintains a global rhashtable keyed by inode pointer and a list_lru for garbage-collected entries.
- Allocates `struct nfsd_file` entries with current credentials, net namespace, access mask, pending construction state, optional GC mode, and direct-I/O alignment fields.
- Provides safe refcount operations (`nfsd_file_get`, `nfsd_file_put`, `nfsd_file_put_local`) and RCU-delayed slab freeing.
- Uses `NFSD_FILE_PENDING` plus `wait_on_bit()` to let concurrent acquirers wait for one thread to finish opening and hashing a file.
- Opens verified files through `nfsd_open_verified` or adopts an already-open file, records DIO alignment via `fh_getattr`, retries stale opens once, and breaks leases before returning cached entries.
- Keeps GC entries on an LRU; the laundrette ages recent entries, the shrinker reclaims under memory pressure, and close work is batched through per-net disposal lists.
- Invalidates cached opens on fsnotify `FS_ATTRIB`/`FS_DELETE_SELF`, lease notifications, export flush, net shutdown, and synchronous rename/unlink paths.
- Resets the write verifier if a cached writable file observes a new writeback error.
- Registers and unregisters slab caches, list_lru, shrinker, fsnotify group, lease notifier, delayed work, and per-net disposal queues.
- Reports filecache stats through `nfsd_file_cache_stats_show`.

Important interactions:
- Uses `nfsd_mutex` for global cache startup/shutdown and purge synchronization.
- Uses `nfsd_net.fcache_disposal` to defer expensive file closes to nfsd service threads.
- LOCALIO calls `nfsd_file_acquire_local`, which verifies filehandle access using supplied service credentials instead of a live RPC request.
- Export flush calls into the file cache to close files that may retain stale export state.

Notable risks:
- `nf_inode` intentionally does not hold an inode reference and must be used only for lookup comparison.
- Refcount and LRU accounting are tightly coupled; GC entries hold an extra LRU reference that must be removed before final free.
- Shutdown ordering is sensitive: delayed work, shrinker callbacks, fsnotify marks, RCU freeing, and per-net disposal queues all have to drain before slab/table destruction.
- LOCALIO is explicitly security-sensitive because it allows a kernel client to bypass normal network request authorization using mapped credentials.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/filecache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/filecache.h -->
# File Research: sources/os/linux/linux/fs/nfsd/filecache.h

Read completely: 88 lines.

Header for the NFSD open-file cache data structures and public acquisition/lifecycle APIs.

Key responsibilities:
- Defines `NFSD_FILE_GC_BATCH`, limiting how long list_lru locks are held during scans.
- Defines `struct nfsd_file_mark`, the fsnotify mark wrapper with an independent refcount for nfsd_file references.
- Defines `struct nfsd_file`, including rhashtable linkage, inode comparison key, backing file, credential, net namespace, state flags, refcount, access mask, fsnotify mark, LRU/GC lists, RCU head, birth time, and DIO alignment fields.
- Defines state bits for hashed, pending construction, referenced, garbage-collected, and recent entries.
- Declares cache init/shutdown/purge, per-net start/shutdown, reference management, file access, inode close, disposal, cache query, file acquisition variants, and stats output.

Notable risks:
- The comment on `nf_inode` is essential: it is not a live reference.
- API callers must pair each successful acquire/get with `nfsd_file_put`, and LOCALIO callers must also handle the returned net namespace lifetime via `nfsd_file_put_local`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/filecache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/flexfilelayout.c -->
# File Research: sources/os/linux/linux/fs/nfsd/flexfilelayout.c

Read completely: 144 lines.

Minimal pNFS flex-file layout server implementation where the metadata server is also the data server and both serve the same underlying storage.

Key responsibilities:
- Implements layoutget by allocating one `pnfs_ff_layout`, setting flags that avoid layoutcommit, avoid I/O through the MDS, and disable read I/O for RW layouts.
- Adjusts the UID for read-only layouts so an IOMODE_READ segment does not carry write permissions.
- Sets a deviceid from the filehandle, copies the NFS filehandle into the layout, and returns a whole-file layout segment.
- Implements getdeviceinfo by building one data-server address from the request destination address and port, using `tcp` or `tcp6`, and setting NFSv3 data-server version and payload sizes.
- Implements layoutcommit as a no-op success.
- Publishes `ff_layout_ops` with device notification support, disabled recalls, and flexfile XDR encoders.

Dependencies:
- Uses pNFS layout structures, `svc_max_payload`, `rpc_ntop`, request destination socket address, and flexfile XDR definitions.

Notable risks:
- This is intentionally simple and assumes a single mirror, data server, filehandle, and whole-file segment.
- Device address formatting must fit fixed buffers sized in `flexfilelayoutxdr.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/flexfilelayout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/flexfilelayoutxdr.c -->
# File Research: sources/os/linux/linux/fs/nfsd/flexfilelayoutxdr.c

Read completely: 124 lines.

XDR encoder for the NFSD pNFS flex-file layout and device-address payloads.

Key responsibilities:
- Encodes layoutget content as one stripe unit, one mirror, one data server, one deviceid, one stateid, one filehandle, stringified UID/GID, flexfile flags, and no stats-collection hint.
- Computes encoded lengths for nested mirror/data-server/filehandle structures before reserving XDR space.
- Encodes getdeviceinfo as either an empty result when `gd_maxcount` is zero, or one netaddr and one NFS version tuple with rsize/wsize/tightly-coupled fields.

Dependencies:
- Uses `xdr_stream`, `xdr_reserve_space`, opaque string encoders, `svcxdr_encode_deviceid4`, and init user namespace id conversion.

Notable risks:
- Length calculation is manual and must stay aligned with RFC layout field encoding.
- UID/GID buffers are fixed at 11 bytes, matching decimal u32 text plus terminator expectations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/flexfilelayoutxdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/flexfilelayoutxdr.h -->
# File Research: sources/os/linux/linux/fs/nfsd/flexfilelayoutxdr.h

Read completely: 50 lines.

Flex-file layout XDR data definitions and encoder declarations.

Key responsibilities:
- Defines flexfile flags for no layoutcommit, no I/O through MDS, and no read I/O.
- Defines fixed buffer lengths for flexfile netid and universal address strings.
- Defines `pnfs_ff_netaddr`, `pnfs_ff_device_addr`, and `pnfs_ff_layout`.
- Declares `nfsd4_ff_encode_getdeviceinfo` and `nfsd4_ff_encode_layoutget`.

Dependencies:
- Includes inet address length definitions and NFSv4 XDR layout types from `xdr4.h`.

Notable risks:
- Address buffers are fixed-size and rely on callers respecting `FF_NETID_LEN` and `FF_ADDR_LEN`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/flexfilelayoutxdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/idmap.h -->
# File Research: sources/os/linux/linux/fs/nfsd/idmap.h

Read completely: 60 lines.

NFSD NFSv4 idmapping interface for translating users/groups between numeric kernel ids and protocol names.

Key responsibilities:
- Declares per-net idmap initialization and shutdown when `CONFIG_NFSD_V4` is enabled, with no-op inline stubs otherwise.
- Declares name-to-UID, name-to-GID, user encoding, and group encoding helpers used by NFSv4 XDR paths.

Dependencies:
- Includes sunrpc service request types and NFS idmap definitions.

Notable risks:
- Header contains legacy BSD-style license text and one stray `> *` character in the comment block, but the declarations are straightforward.
- Callers must handle returned NFS status values rather than raw errno for mapping failures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/idmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/localio.c -->
# File Research: sources/os/linux/linux/fs/nfsd/localio.c

Read completely: 217 lines.

NFSD support for NFS LOCALIO, allowing a local kernel NFS client to bypass the network stack after proving that the server is local.

Key responsibilities:
- Implements `nfsd_open_local_fh`, converting an NFS filehandle into `svc_fh`, mapping client credentials to service credentials, and acquiring an `nfsd_file` through `nfsd_file_acquire_local`.
- Caches the acquired local `nfsd_file` in an RCU pointer supplied by the client, using compare-exchange to handle concurrent installers and paired net/file references.
- Exposes file pointer and DIO alignment accessors through `nfsd_localio_operations`.
- Installs NFSD LOCALIO operations by assigning `nfs_to`.
- Implements a hidden LOCALIO RPC version with NULL and `UUID_IS_LOCAL`; the UUID procedure records local clients in `nfsd_net.local_clients`.
- Decodes UUID arguments from fixed opaque XDR.

Important interactions:
- Uses `nfsd_net_try_get`/`nfsd_net_put` to keep the server net namespace alive for local file references.
- Uses `svcauth_map_clnt_to_svc_cred_local` and the filecache local-acquire path.
- Depends on `CONFIG_NFS_LOCALIO` fields in `nfsd_net`.

Notable risks:
- LOCALIO bypasses normal network transport and request authorization paths; correctness depends on credential mapping and auth-domain validation.
- The cached pointer owns both file and net lifetime; losing those paired references would create leaks or use-after-free risk.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/localio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/lockd.c -->
# File Research: sources/os/linux/linux/fs/nfsd/lockd.c

Read completely: 110 lines.

Binding layer between NFSD and lockd/NLM so lockd can open and close files through nfsd without requiring the NFS client module.

Key responsibilities:
- Implements `nlm_fopen`, translating an NFS filehandle into `svc_fh`, choosing read or write access from POSIX open flags, and calling `nfsd_open`.
- Adds NLM-specific access flags: bypass GSS, owner override, and `NFSD_MAY_NLM` so `insecure_locks` can bypass authentication.
- Maps nfsd status values to lockd-facing errno values, notably `nfserr_jukebox` to `-EWOULDBLOCK`, stale to `-ESTALE`, and other failures to `-ENOLCK`.
- Implements `nlm_fclose` with `fput`.
- Registers/unregisters the `nlmsvc_binding` via `nfsd_lockd_init` and `nfsd_lockd_shutdown`.

Notable risks:
- Comments document subtle client behavior around delegation conflicts and NLM denied semantics.
- NLM auth bypass is intentional but must remain limited to exports that permit it.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/lockd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/netlink.c -->
# File Research: sources/os/linux/linux/fs/nfsd/netlink.c

Read completely: 116 lines.

Auto-generated generic netlink family definition for NFSD administrative control.

Key responsibilities:
- Defines nested attribute policies for server sockets and protocol versions.
- Defines command-specific policies for setting threads, versions, listeners, and pool mode.
- Registers split generic-netlink operations for RPC status dump, thread set/get, version set/get, listener set/get, and pool mode set/get.
- Marks mutating operations with `GENL_ADMIN_PERM`; dump/get operations have command capability flags.
- Defines the `nfsd_nl_family` with name/version from UAPI, netns support, parallel ops, module owner, and operation table.

Dependencies:
- Generated from `Documentation/netlink/specs/nfsd.yaml`.
- Depends on handlers declared in `netlink.h` and UAPI constants in `linux/nfsd_netlink.h`.

Notable risks:
- This file is generated; manual edits would be overwritten by `tools/net/ynl/ynl-regen.sh`.
- Policy definitions are the kernel-side validation boundary for NFSD netlink control messages.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/netlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/netlink.h -->
# File Research: sources/os/linux/linux/fs/nfsd/netlink.h

Read completely: 32 lines.

Auto-generated header for the NFSD generic netlink family.

Key responsibilities:
- Declares shared nested policies for socket and version attributes.
- Declares NFSD netlink command handlers for RPC status dump and thread/version/listener/pool-mode get/set operations.
- Declares the global `nfsd_nl_family`.

Dependencies:
- Includes generic netlink headers and UAPI `linux/nfsd_netlink.h`.

Notable risks:
- Generated from the NFSD YNL spec; handler prototypes must stay synchronized with generated operation entries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/netlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/netns.h -->
# File Research: sources/os/linux/linux/fs/nfsd/netns.h

Read completely: 247 lines.

Per-network-namespace NFSD state definition. `struct nfsd_net` is the central container for export caches, idmap caches, NFSv4 client/session/state tracking, duplicate reply cache state, service stats, filecache disposal, localio clients, and net lifetime management.

Key responsibilities:
- Defines client/session hash sizes and the per-net stats counter enum, including duplicate reply cache, filehandle stale, I/O byte counters, and NFSv4 operation counters.
- Declares `struct nfsd_net` with export and expkey cache pointers, id mapping caches, NFSv4 lock manager/grace/boot data, client tracking tables, session tables, laundromat work, lock lists, reclaim state, write verifier, service info, net refcount/completions, server-to-server copy state, supported protocol versions, duplicate reply cache metadata, counters, svc stats, shrinkers, copy mount tracking, server name, filecache disposal queue, siphash keys, courtesy client state, localio client list, filehandle key, and callback state.
- Provides `nfsd_netns_ready` and declares `nfsd_net_id`, version support, net reference helpers, and write verifier helpers.

Dependencies:
- Pulls in net namespace, filelock, NFSv4, percpu counter/refcount, siphash, and sunrpc stats infrastructure.

Notable risks:
- Many fields have different locking rules: client mutex, `deleg_lock`, `client_lock`, `blocked_locks_lock`, `s2s_cp_lock`, `nfsd_ssc_lock`, and localio lock.
- Shutdown order is complex because caches, nfsd service threads, duplicate reply cache, NFSv4 state, filecache disposal, and LOCALIO clients all have per-net lifetime.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/netns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs2acl.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs2acl.c

Read completely: 389 lines.

NFSACL protocol version 2 procedure implementation, including ACL get/set plus getattr/access helpers and local XDR encode/decode/release logic.

Key responsibilities:
- Handles NULL, GETACL, SETACL, GETATTR, and ACCESS procedures for the NFSACL v2 side protocol.
- GETACL verifies the filehandle, validates the mask, obtains post attributes, returns access ACL or a mode-derived minimum ACL, and optionally returns default ACL.
- SETACL verifies setattr permission, takes write access, locks the inode, sets access and default POSIX ACLs, drops write access, and returns updated attributes.
- GETATTR and ACCESS reuse nfsd filehandle verification/access logic.
- Decodes v2 filehandles, ACL masks, POSIX ACL payloads, and access masks.
- Encodes status, attributes, ACL payloads, and access results; releases filehandles and POSIX ACL references.
- Publishes `nfsd_acl_version2` with procedure metadata, cache policy, XDR result sizing, dispatch, and per-CPU counters.

Dependencies:
- Uses POSIX ACL helpers, generic nfsd VFS helpers, legacy `linux/nfsacl.h`, and NFSv3 XDR helpers for shared ACL structures.

Notable risks:
- The file notes `nfsacl.h` is a broken header.
- GETACL/SETACL own several POSIX ACL references that must be released on all paths.
- Procedure name for ACLPROC2_ACCESS is set to `"SETATTR"`, which appears inconsistent with the operation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs2acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs3acl.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs3acl.c

Read completely: 279 lines.

NFSACL protocol version 3 procedure implementation for POSIX ACL get/set over the NFSv3 ACL side protocol.

Key responsibilities:
- Handles NULL, GETACL, and SETACL procedures.
- GETACL verifies the filehandle, validates the requested ACL mask, returns access ACL or a mode-derived minimum ACL, and optionally returns default ACL.
- SETACL verifies setattr permission, takes write access, locks the inode, sets access and default POSIX ACLs, and returns post-op attributes.
- Decodes NFSv3 filehandles, masks, and ACL payloads.
- Encodes NFSv3 status, post-op attributes, ACL masks, ACL payloads, and SETACL post-op attributes.
- Releases filehandle and POSIX ACL references.
- Publishes `nfsd_acl_version3` with procedure table, dispatch, XDR sizing, and per-CPU counters.

Dependencies:
- Shares data structures and XDR helpers with NFSv3 server code and legacy NFSACL support.

Notable risks:
- SETACL stores raw `nfserrno(error)` after the drop-lock label; if both ACL updates succeed, `error` is zero, which maps to success as intended.
- Default ACL handling for non-directories is left to filesystem/POSIX ACL behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs3acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs3proc.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs3proc.c

Read completely: 1080 lines.

NFSv3 RPC procedure layer. It maps decoded request structures to nfsd VFS/filecache operations, normalizes server errors into NFSv3 status codes, and declares the NFSv3 service procedure table.

Key responsibilities:
- Implements all NFSv3 core procedures: NULL, GETATTR, SETATTR, LOOKUP, ACCESS, READLINK, READ, WRITE, CREATE, MKDIR, SYMLINK, MKNOD, REMOVE, RMDIR, RENAME, LINK, READDIR, READDIRPLUS, FSSTAT, FSINFO, PATHCONF, and COMMIT.
- Maps internal nfsd statuses to NFSv3-specific errors in `nfsd3_map_status`.
- Bounds READ and WRITE offsets/counts to `OFFSET_MAX`, service payload size, and result buffer size.
- Implements NFSv3 regular-file CREATE semantics for unchecked, guarded, and exclusive modes, including verifier-to-time conversion, existing-file handling, pre/post directory attributes, and create-time setattr.
- Initializes paged directory-list encoding buffers and recycles only pages used by READDIR/READDIRPLUS replies.
- Honors `NFSEXP_NOREADDIRPLUS` by rejecting READDIRPLUS on exports with that option.
- Reports filesystem properties, max sizes, pathconf data, and case sensitivity/preservation information.
- Uses the open-file cache for COMMIT with `nfsd_file_acquire_gc`.
- Defines the `nfsd_procedures3` table, including decode/encode/release callbacks, duplicate reply cache policy, argument/result sizes, estimated XDR sizes, names, dispatch, and counters.

Important interactions:
- Calls into `vfs.c` style helpers such as `nfsd_lookup`, `nfsd_access`, `nfsd_read`, `nfsd_write`, `nfsd_create`, `nfsd_symlink`, `nfsd_unlink`, `nfsd_rename`, `nfsd_link`, `nfsd_readdir`, `nfsd_statfs`, and `nfsd_commit`.
- Uses `filecache.c` for COMMIT open-state reuse.
- Uses `nfs3xdr.c` callbacks to encode directory entries.

Notable risks:
- Non-idempotent operations use reply-cache buffering; procedure table cache modes are part of protocol correctness.
- Exclusive CREATE verifier handling deliberately clears high bits for old Solaris and XFS bigtime compatibility.
- PATHCONF maps unexpected case-query errors to the small RFC 1813 allowed error set.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs3proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs3xdr.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs3xdr.c

Read completely: 1356 lines.

NFSv3 XDR encode/decode implementation for core server arguments, results, attributes, weak cache consistency data, directory entries, and release helpers.

Key responsibilities:
- Encodes and decodes NFSv3 primitive types such as nfstime3, status, filehandles, cookie verifiers, write verifiers, filenames, directory operation arguments, setattr values, sattr guards, and device numbers.
- Encodes file attributes from `kstat`, including mode, uid/gid through the request user namespace, symlink size clamping, used bytes, rdev, fsid source selection, fileid, and atime/mtime/ctime.
- Encodes pre-op, post-op, and weak cache consistency data, including no-attribute cases for stale or negative filehandles.
- Decodes all NFSv3 procedure arguments: fhandle, setattr, diropargs, access, read, write, create, mkdir, symlink, mknod, rename, link, readdir, readdirplus, and commit.
- Encodes all NFSv3 procedure results: getattr, wccstat, lookup, access, readlink, read, write, create, rename, link, readdir, fsstat, fsinfo, pathconf, and commit.
- Handles page-backed opaque result payloads for READ, READLINK, and READDIR.
- Composes optional filehandles and attributes for READDIRPLUS entries, while suppressing mountpoint entries and export-root parent handles.
- Backfills directory cookies after the next offset is known.
- Provides release helpers for one- and two-filehandle result structures.

Important interactions:
- Depends on `fh_getattr`, `lease_get_mtime`, export fsid source logic, `fh_compose`, dcache lookup, and request result buffer/page management.
- READDIR entry encoders are callback-compatible with `nfsd_readdir`.

Notable risks:
- Filename decode rejects zero-length names, names longer than `NFS3_MAXNAMLEN`, embedded NUL, and slash.
- Manual XDR length/reservation and page payload accounting must remain exact to avoid malformed replies or buffer exhaustion.
- READDIRPLUS filehandle composition intentionally avoids returning handles for mountpoints and for `..` at filesystem/export roots.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs3xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4acl.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs4acl.c

Read completely: 884 lines.

Common NFSD NFSv4 ACL translation code. It converts POSIX ACLs to NFSv4 ACLs for GETATTR/READ ACL paths and converts NFSv4 ACLs back to POSIX ACLs for SETATTR/write paths.

Key responsibilities:
- Defines NFSv4 ACL conversion flags for default ACLs, directories, and owner entries, plus supported permission and inheritance masks.
- Converts POSIX permissions to NFSv4 ALLOW/DENY masks, adding owner-specific and directory delete-child bits where appropriate.
- Builds an NFSv4 ACL from access and default POSIX ACLs in `nfsd4_get_nfs4_acl`, allocating worst-case deny/allow ACE pairs.
- Summarizes POSIX ACLs and emits ordered NFSv4 ACEs that preserve POSIX effective permissions using explicit DENY entries for permissions not granted by later entries.
- Sorts POSIX ACL USER/GROUP ranges by uid/gid before validation.
- Tracks NFSv4-to-POSIX conversion state with allow/deny bitmasks for owner, owning group, other, everyone, named users, named groups, and mask.
- Processes each NFSv4 ACE, rejects unsupported ACE types/flags, splits effective and default ACL state, and copies missing owner/group/other entries into default ACLs when inheritable entries exist.
- Converts accumulated state into POSIX ACLs and stores them in `struct nfsd_attrs` via `nfsd4_acl_to_attr`.
- Maps special NFSv4 who strings (`OWNER@`, `GROUP@`, `EVERYONE@`) to internal whotype values and writes them back to XDR.
- Provides `nfs4_acl_bytes` allocation sizing.

Dependencies:
- Uses POSIX ACL core helpers, nfsd ACL structures, idmapped nop mount context, NFSv4 constants, XDR stream encoding, and kernel uid/gid comparison helpers.

Notable risks:
- NFSv4 ACLs are richer than POSIX ACLs; conversion is necessarily lossy and errs restrictive when setting POSIX ACLs.
- Only ALLOW and DENY ACEs with a narrow supported flag set are accepted for conversion.
- State arrays allocate space for worst-case named users/groups based on ACE count; allocation failure must unwind both states.
- `ace2type` treats unknown whotypes as a kernel bug.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4acl.c -->