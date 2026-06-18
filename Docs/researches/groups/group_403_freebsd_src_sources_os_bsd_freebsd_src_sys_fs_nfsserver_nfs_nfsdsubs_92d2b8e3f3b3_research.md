# Group Research: group_403_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_nfsserver_nfs_nfsdsubs_92d2b8e3f3b3

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdsubs.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdsubs.c

This file provides NFS server support routines for protocol marshalling, file-handle parsing, error mapping, name parsing, export/security checks, and server-side data structure initialization. It is not an operation implementation file itself; it is the shared substrate used by NFS server RPC handlers.

Key responsibilities:
- Defines NFSv2 errno-to-wire-error mapping and per-operation NFSv3/NFSv4 allowed-error tables.
- Implements `nfsd_errmap()` to convert `nd->nd_repstat` into protocol-specific XDR error values, including NFSv4.1 behavior that accepts any valid NFS error after normalization.
- Handles mbuf-chain trimming in `nfsrv_adj()`, including `M_EXTPG` external-page mbufs where trailing pages must be unwired and freed.
- Builds weak cache consistency and post-operation attributes via `nfsrv_wcc()`, `nfsrv_postopattr()`, and `nfsrv_fillattr()`.
- Parses incoming file handles with `nfsrv_mtofh()`, including public file handles, NFSv4 named attributes, and pNFS data-server file handles.
- Parses NFS path components with `nfsrv_parsename()`, including public-filehandle canonical/native path handling, percent-decoding, slash rejection, NFSv4 `"."`/`"..”` rejection, and optional UTF-8 validation.
- Initializes NFS server hash tables and queues in `nfsd_init()`.
- Checks NFSv4 root export security in `nfsd_checkrootexp()`, including GSS, export security flags, and optional TLS/mTLS constraints.
- Extracts NFSv4 compound minor version and tag data in `nfsd_getminorvers()`.

Important globals and tunables:
- `enable_checkutf8` controls NFSv4 UTF-8 name validation.
- `enable_nobodycheck` and `enable_nogroupcheck` reject attempts to set owner/group to default nobody/nogroup identities.
- `nfs_v2pubfh`, `nfsrv_dontlisthead`, and `nfsrv_recalllisthead` are initialized here.
- VNET hash pointers are allocated for clients, locks, and sessions.

Implementation notes:
- Error maps are deliberately conservative. NFSv3/NFSv4 filtering returns a per-operation default error if the current error is not in the allowlist.
- `nfsrv_fixattr()` applies a subset of NFSv4 settable attributes after creation when allowed, temporarily elevating `cr_uid` to zero for group changes where the caller is a group member, then restoring it.
- ACL handling is conditional on `NFS4_ACL_EXTATTR_NAME`; unsupported ACL bits are cleared from the returned attribute bitmap.
- Referral attributes are encoded by `nfsrv_putreferralattr()`, which handles `fs_locations`, `rdattr_error`, type, fsid, and mounted-on-fileid.

Research-relevant risks:
- Many routines signal protocol-level errors by setting `nd->nd_repstat` while returning `0`; callers must distinguish RPC decode failure from NFS status failure.
- `nfsrv_fixattr()` mutates credentials transiently and must always restore `cr_uid`.
- `nfsrv_adj()` mutates and frees mbufs/pages; callers must treat the returned mbuf as the new tail.
- `nfsrv_parsename()` edits public lookup input bytes for native public paths and percent decoding, so buffer ownership and length accounting matter.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdsubs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nullfs/null.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nullfs/null.h

This header defines the core data structures, flags, macros, and prototypes for FreeBSD nullfs, a stackable loopback filesystem layer.

Key definitions:
- `struct null_mount` stores the lower mount, referenced lower root vnode, mount flags, and upper/notification registration nodes.
- `struct null_node` stores the per-upper-vnode mapping to a referenced lower vnode, a back pointer to the upper vnode, and vnode flags.
- Mount flags:
  - `NULLM_CACHE`: cache free nullfs vnodes.
  - `NULLM_NOUNPBYPASS`: disable UNIX-domain socket bypass behavior.
- Vnode flags:
  - `NULLV_NOUNLOCK`: reclaim path should not unlock the lower vnode.
  - `NULLV_DROP`: vnode should be recycled/dropped, typically after unlink/removal.
- Conversion helpers: `MOUNTTONULLMOUNT`, `VTONULL`, `VTONULL_SMR`, `NULLTOV`, and `NULLVPTOLOWERVP`.

Exported interfaces:
- Lifecycle: `nullfs_init()`, `nullfs_uninit()`.
- Node cache: `null_nodeget()`, `null_hashget()`, `null_hashrem()`.
- VOP bypass: `null_bypass()`.
- VOP vectors: `null_vnodeops`, `null_vnodeops_no_unp_bypass`.
- `null_is_nullfs_vnode()` tests whether a vnode uses one of the nullfs operation vectors.
- `null_node_zone` is the UMA allocation zone for `struct null_node`.

Research-relevant notes:
- The header exposes SMR-aware access to `v_data`, which is central to lock/reclaim race handling in `null_vnops.c`.
- `NULLVPTOLOWERVP` expands to a diagnostic checker when `DIAGNOSTIC` is enabled.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nullfs/null.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nullfs/null_subr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nullfs/null_subr.c

This file implements nullfs vnode alias caching: mapping a lower vnode plus upper mount to a unique nullfs vnode.

Key responsibilities:
- Initializes and destroys the nullfs hash table, hash lock, and SMR-enabled UMA node zone.
- Looks up existing aliases with `null_hashget()` and `null_hashget_locked()`.
- Creates or returns an existing alias vnode in `null_nodeget()`.
- Inserts and removes `struct null_node` entries from the hash.
- Provides diagnostic lower-vnode validation via `null_checkvp()`.

Core flow in `null_nodeget()`:
1. Requires the lower vnode locked and referenced.
2. Checks the hash for an existing alias; if found, releases the caller’s spare lower vnode reference and returns the alias.
3. Allocates a `null_node` and `getnewvnode()` using either normal or no-UNP-bypass vnode ops.
4. Sets upper vnode type, `v_data`, shared lock pointer (`v_vnlock = lowervp->v_vnlock`), page-read/inotify flags, and root flag when appropriate.
5. Rechecks for duplicates under `null_hash_lock`.
6. Inserts the vnode into the mount queue and hash, then marks it constructed.

Concurrency/lifetime details:
- Hash lookups use VFS SMR for lockless reads.
- Insert/remove use a global rwlock.
- Duplicate creation is tolerated and resolved under the write lock.
- `null_destroy_proto()` tears down a just-created duplicate/prototype vnode and frees its node via SMR.
- Lower vnode references are transferred into the nullfs node on successful creation.

Research-relevant risks:
- The code relies on the lower vnode lock to prove found aliases are not doomed during lookup.
- `null_nodeget()` has delicate ownership semantics: callers pass a locked lower vnode with a spare reference, which is consumed on success.
- Page cache and inotify flags are copied opportunistically and may be rechecked later by open paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nullfs/null_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nullfs/null_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nullfs/null_vfsops.c

This file implements nullfs mount-level VFS operations.

Key mount behavior:
- Rejects mounting nullfs as root.
- Treats update mounts as a no-op except for NFS export updates.
- Accepts mount target from `from` or `target`.
- Temporarily unlocks a covered nullfs vnode in one nesting case to reduce deadlock risk.
- Resolves and locks the lower root vnode with `namei()`.
- Rejects self-mounts and certain multi-null mount cases that would lock against themselves.
- Requires the lower root vnode to be `VDIR` or `VREG` and match the covered vnode type.
- Registers the upper mount with the lower mount using `vfs_register_upper_from_vp()`.
- Creates the root alias with `null_nodeget()`.
- Enables vnode caching based on mount options, sysctl default, and lower-mount `MNTK_NULL_NOCACHE`.
- Optionally registers lower-mount notification callbacks for cached vnode invalidation.
- Propagates relevant mount flags such as local status and buffer/cache capabilities.

Options and tunables:
- `vfs.nullfs.cache_vnodes`: default cache policy.
- Mount options: `cache`, `nocache`, `unixbypass`, `nounixbypass`.

Other VFS operations:
- `nullfs_unmount()` flushes vnodes, unregisters notifications/upper mount linkage, clears cross-lock state, releases lower root, and frees mount data.
- `nullfs_root()` vgets the lower root and returns/create the upper alias.
- `nullfs_quotactl()` forwards quota operations to the lower mount while carefully unbusying the upper mount.
- `nullfs_statfs()` copies selected fields from lower `VFS_STATFS`.
- `nullfs_vget()` and `nullfs_fhtovp()` map lower returned vnodes to nullfs aliases.
- `nullfs_extattrctl()` forwards extended attribute control to the lower mount.
- `nullfs_reclaim_lowervp()` and `nullfs_unlink_lowervp()` are lower-vnode notification handlers that reclaim/drop upper aliases.

Research-relevant risks:
- Mount and unmount paths carry explicit comments about deadlock-prone relocking.
- Cache-enabled mounts depend on lower mount notification to avoid stale aliases.
- `nullfs_unlink_lowervp()` manipulates references/holds and lock ownership differently for doomed and non-doomed vnodes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nullfs/null_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nullfs/null_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nullfs/null_vnops.c

This file implements nullfs vnode operations and the generic stackable VOP bypass layer.

Core design:
- `null_bypass()` rewrites nullfs vnode arguments to their lower vnodes, calls the lower vnode operation, restores original upper vnode arguments, and wraps returned lower vnodes with `null_nodeget()`.
- The bypass path tracks operations that release vnode references and compensates with temporary references.
- Temporary holds protect lower/upper vnode relationships across lower VOPs that may unlock and allow reclamation.
- `null_copy_inotify()` synchronizes inotify routing flags between upper and lower vnodes.

Specialized VOP behavior:
- `null_lookup()` directly calls lower `VOP_LOOKUP()` for speed, rejects read-only creates/deletes/renames, handles `..` edge cases, holds the lower directory vnode across unlock/reclaim races, and wraps lower results.
- `null_open()` forwards open and then shares the lower vnode VM object/page-read state.
- `null_setattr()`, `null_access()`, and `null_accessx()` enforce read-only mount semantics before bypass.
- `null_stat()` and `null_getattr()` forward then rewrite fsid to the upper mount fsid.
- `null_remove()` and `null_rmdir()` mark the vnode for drop; remove also temporarily references the lower vnode to support lower NFS sillyrename behavior.
- `null_rename()` prevents cross-device/null-to-lower moves, maps all participating vnodes manually, and marks overwritten targets for drop.
- `null_lock()` and `null_unlock()` mostly lock/unlock the lower vnode, with SMR/interlock preparation and fallback to standard locking if the null node has been reclaimed.
- `null_inactive()` recycles the vnode when caching is disabled, the lower vnode was deleted, or the lower vnode is `VV_NOSYNC`.
- `null_reclaim()` removes the hash entry, detaches `v_data`, restores private vnode lock, clears VM object and inotify flags, unwinds writecounts, releases the lower vnode, and frees the null node.
- `null_vptocnp()`, `null_vptofh()`, `null_read_pgcache()`, `null_advlock()`, `null_vput_pair()`, and `null_getlowvnode()` provide targeted lower-vnode forwarding where generic bypass is unsafe.

VOP vectors:
- `null_vnodeops` defines the main operation table.
- `null_vnodeops_no_unp_bypass` inherits from `null_vnodeops` but uses standard UNIX-domain socket bind/connect/detach operations.

Research-relevant risks:
- Lock ownership can move between lower and upper vnodes during reclaim; several routines explicitly repair this state.
- Generic bypass assumes at most one returned vnode pointer and no inout vnode pointers.
- Reclaim must prevent upper inotify callbacks after lower vnode watch references outlive the upper vnode.
- `copy_file_range` is deliberately `VOP_PANIC`, so generic bypass is not used there.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nullfs/null_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_client.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_client.c

This file implements the 9P client request layer used by p9fs VFS/VOP code.

Core responsibilities:
- Parses mount options into client state, defaulting to `virtio`, `9P2000.L`, and `P9FS_MTU`.
- Allocates/frees request buffers, response buffers, request objects, fids, and tags through UMA zones and `unrhdr` pools.
- Builds 9P request headers, serializes payloads, invokes the transport, parses response headers, and maps `RERROR`/`RLERROR` replies to local errors.
- Maintains transport state: connected, begin-disconnect, disconnected.
- Negotiates protocol version with `Tversion`.
- Creates/destroys clients and transport handles.
- Implements request helpers for attach, walk, open, read, write, readdir, create, remove, unlink, clunk, statfs, renameat, symlink, hardlink, readlink, getattr, and setattr.

Important request lifecycle:
1. `p9_client_request()` calls `p9_client_prepare_req()`.
2. Preparation checks disconnect state, allocates a tagged request, writes the 9P header, writes typed payload fields, and finalizes the size.
3. The selected transport’s `request()` method submits the request and fills the response.
4. `p9_client_check_return()` parses the response header and handles protocol errors.
5. The caller decodes operation-specific response fields and frees the request.

FID behavior:
- `p9_fid_create()` allocates a numeric fid from the client pool and initializes mode/uid.
- `p9_client_attach()` creates a root fid for a user.
- `p9_client_walk()` optionally clones a fid, walks path components, validates returned qid count, and stores the final qid.
- `p9_client_clunk()` sends `Tclunk` when possible, then always destroys the local fid.
- Open/create set `fid->mode` and `fid->mtu`.

I/O behavior:
- `p9_client_read()` and `p9_client_readdir()` cap transfer size by fid MTU, client msize, and caller count.
- Read/write return positive byte counts on success and negative errno values on error.
- `p9_client_read()` treats a zero-byte read as `EIO`.
- `p9_client_write()` caps outgoing data to the server’s accepted size and returns the server write count.

Research-relevant risks:
- Several error paths return immediately after response decode failure and must be audited for request cleanup.
- `p9_client_create()` creates the transport before version negotiation; if negotiation fails, the visible cleanup path frees the client allocation but does not obviously close the transport handle.
- The client state machine permits only `Tclunk` once disconnect begins.
- Serialization/deserialization depends on the format mini-language in `p9_protocol.c`; mismatches can corrupt protocol framing.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_client.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_client.h

This header defines the public 9P client structures and APIs used by p9fs.

Key types:
- `enum p9_proto_versions`: legacy `9P2000`, Unix `9P2000.u`, and Linux `9P2000.L`.
- `struct p9_req_t`: transmit and receive buffers for one 9P request.
- `enum transport_status`: connected, begin-disconnect, disconnected.
- `struct p9_client`: transport ops/handle, mutexes, request CV, msize, protocol version, fid/tag pools, and transport state.
- `struct p9_fid`: local fid object with numeric fid, mode, qid, MTU, uid, open count, and list linkage.
- `struct p9_dirent`: parsed 9P directory entry.

Constants:
- `P9FS_MTU` is 131072.
- `P9FS_IOUNIT` is `P9FS_MTU - 24`.
- `P9FS_DIRENT_LEN` is 256.
- `P9_NOTAG` is 0.

Exported APIs:
- Zone lifecycle: `p9_init_zones()`, `p9_destroy_zones()`.
- Client/session lifecycle: `p9_client_create()`, `p9_client_destroy()`, `p9_client_attach()`.
- Fid/tag helpers: `p9_fid_create()`, `p9_fid_destroy()`, `p9_tag_create()`, `p9_tag_destroy()`.
- Protocol requests for open, close/clunk, walk, readdir, read/write, create, remove, unlink, statfs, symlink, hardlink, readlink, renameat, getattr, setattr.
- Buffer helpers: `p9_buf_vwritef()`, `p9_buf_readf()`, `p9_buf_prepare()`, `p9_buf_finalize()`, `p9_buf_reset()`.

Research-relevant notes:
- This header is the contract between p9fs vnode/mount code and the transport/protocol implementation.
- It exposes negative-error/positive-byte-count conventions for read/write through return types rather than separate output parameters.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_client.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_debug.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_debug.h

This header defines p9fs debug logging flags and the `P9_DEBUG()` macro.

Key details:
- `p9_debug_level` is an external integer controlled elsewhere by sysctl.
- Debug categories:
  - `P9_DEBUG_TRANS`: transport tracing.
  - `P9_DEBUG_SUBR`: p9fs driver submission/subroutine tracing.
  - `P9_DEBUG_LPROTO`: low-level protocol tracing.
  - `P9_DEBUG_PROTO`: high-level protocol tracing.
  - `P9_DEBUG_VOPS`: vnode operation tracing.
  - `P9_DEBUG_ERROR`: verbose error messages.
- `P9_DEBUG(category, fmt, ...)` prints only when the corresponding `P9_DEBUG_<category>` bit is set.

Research-relevant notes:
- The category argument is token-pasted, so callers use `P9_DEBUG(PROTO, ...)`, not numeric values.
- Logging uses `printf()` directly and is synchronous kernel debug output.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_protocol.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_protocol.c

This file implements 9P protocol buffer serialization and deserialization.

Core abstraction:
- `struct p9_buffer` is treated as a typed byte stream with size, capacity, offset, tag, id, and data pointer.
- `buf_read()` copies from current offset and advances it.
- `buf_write()` appends to current size and advances size.

Format mini-language:
- `b`: 8-bit integer.
- `w`: 16-bit integer.
- `d`: 32-bit integer.
- `q`: 64-bit integer.
- `s`: counted string.
- `u`: uid.
- `g`: gid.
- `Q`: 9P qid.
- `S`: legacy/9P2000.u stat structure.
- `A`: 9P2000.L getattr/stat structure.
- `D`: data blob with 32-bit length.
- `T`: string array.
- `R`: qid array.
- `W`: string with explicit length, write-only.
- `?`: stop processing if protocol is not `.u` or `.L`.

Key functions:
- `p9_buf_readf()` and internal `p9_buf_vreadf()` decode typed fields.
- `p9_buf_vwritef()` and internal `p9_buf_writef()` encode typed fields.
- `p9stat_read()` decodes a stat blob into `p9_wstat`.
- `p9_buf_prepare()` writes an initial placeholder 9P header.
- `p9_buf_finalize()` rewrites the true size at the beginning of the buffer.
- `p9_buf_reset()` clears size and offset.
- `p9_dirent_read()` parses one directory entry from a returned readdir buffer.

Memory behavior:
- Decoding strings allocates `M_TEMP` NUL-terminated strings.
- Decoding string/qid arrays allocates arrays and cleans them on failure.
- `stat_free()` frees dynamically allocated fields in `p9_wstat`.

Research-relevant risks:
- Wire integer encoding is copied directly via host memory representation; portability depends on the broader kernel/transport assumptions.
- `p9_buf_vwritef()` caps normal string length at 255.
- `p9_dirent_read()` uses `strncpy()` for the parsed name but does not explicitly NUL-terminate beyond the copied length; consumers rely on `len`.
- `D` decode returns a pointer into the response buffer; callers must copy before freeing the request.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_protocol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_protocol.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_protocol.h

This header defines 9P wire protocol constants and structures.

Key contents:
- `enum p9_cmds_t` lists 9P message type numbers for legacy, 9P2000.u, and 9P2000.L requests/responses.
- `enum p9_open_mode_t` defines Plan 9 open modes and flags.
- `enum p9_perm_t` defines Plan 9 permission/type bits.
- `enum p9_qid_t` defines qid type bits.
- Magic values include `P9PROTO_NOFID`, default uname/aname, `P9_NONUNAME`, and `P9_MAXWELEM`.
- Wire-visible structures:
  - `struct p9_qid`
  - `struct p9_statfs`
  - `struct p9_wstat`
  - `struct p9_stat_dotl`
  - `struct p9_iattr_dotl`
  - `struct p9_buffer`

Attribute masks:
- `P9PROTO_STATS_*` masks identify requested/returned getattr fields.
- `P9PROTO_SETATTR_*` masks identify valid setattr fields.
- `P9PROTO_UNLINKAT_REMOVEDIR` defines unlinkat directory removal semantics.

Research-relevant notes:
- This header is protocol-shared; changes affect both client request encoding and p9fs vnode attribute conversion.
- `p9_buffer` is not self-owning; it tracks raw memory supplied by the client layer.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_protocol.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_transport.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_transport.c

This file implements the registry for p9fs transport modules.

Key behavior:
- Maintains a global `TAILQ` of `struct p9_trans_module` entries.
- Initializes the list at `SYSINIT` time with subsystem `SI_SUB_DRIVERS`.
- `p9_register_trans()` appends a transport module.
- `p9_unregister_trans()` removes a transport module.
- `p9_get_trans_by_name()` linearly searches by transport name and returns the matching module or `NULL`.

Research-relevant notes:
- No explicit locking protects the transport list; registration is expected to occur during controlled driver/module lifecycle.
- The default client path expects a transport named `"virtio"` unless the mount specifies `trans=`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_transport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_transport.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_transport.h

This header defines the p9fs transport module interface.

Key type:
- `struct p9_trans_module` contains:
  - TAILQ linkage.
  - Transport `name`.
  - `create(mount_tag, handlep)` to establish a connection.
  - `close(handle)` to terminate a connection.
  - `request(handle, req)` to submit a 9P request.
  - `cancel(handle, req)` to cancel an in-flight request.

Exported functions:
- `p9_register_trans()`
- `p9_unregister_trans()`
- `p9_get_trans_by_name()`

Research-relevant notes:
- The transport interface is synchronous from the client’s perspective: `request()` is expected to return with the response buffer populated or an error.
- `struct p9_req_t` is forward-declared here to avoid depending on the full client header.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_transport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs.h

This header defines the p9fs filesystem’s in-memory mount, session, node, and inode structures.

Key structures:
- `struct p9fs_qid`: p9fs-local qid mirror.
- `struct p9fs_inode`: cached remote inode metadata, including mode, type, size, timestamps, ownership strings/numeric IDs, qid path, link count, block info, generation, and data version.
- `struct p9fs_node`: per-vnode p9fs node containing VFID and VOFID lists, locks, parent pointer, qid, vnode pointer, inode cache, session pointer, session list linkage, and flags.
- `struct p9fs_session`: per-mount session state, including root node, mount pointer, access identity, 9P client, session lock, node list, mount fid, and name length cache.
- `struct p9fs_mount`: mount wrapper containing the session and mount tag.

FID model:
- `VFID` identifies general vnode fids.
- `VOFID` identifies open fids.
- Separate mutex-protected STAILQ lists track fids by node and uid/mode.

Flags:
- Node flags include modified, root, deleted, and in-session.
- Session flags include protocol version and access mode (`any`, `single`, `user`).

Exported filesystem helpers:
- Session lifecycle: `p9fs_init_session()`, `p9fs_prepare_to_close()`, `p9fs_complete_close()`, `p9fs_close_session()`.
- Node/vnode lookup and lifecycle: `p9fs_vget()`, `p9fs_vget_common()`, `p9fs_node_cmp()`, `p9fs_destroy_node()`, `p9fs_dispose_node()`, `p9fs_cleanup()`.
- Fid management: `p9fs_fid_add()`, `p9fs_fid_remove()`, `p9fs_fid_remove_all()`, `p9fs_get_fid()`.
- Attribute helpers: `p9fs_stat_vnode_dotl()`, `p9fs_reload_stats_dotl()`, `p9fs_proto_dotl()`.

Research-relevant notes:
- Parent pointers are reference-counted through vnode refs and explicitly broken during unmount preparation.
- The filesystem uses qid path/version/type for vnode identity.
- Root node is embedded in the session; non-root nodes are UMA allocated.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_proto.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_proto.h

This small header defines p9fs-facing Plan 9 open mode constants:
- `P9FS_OREAD`
- `P9FS_OWRITE`
- `P9FS_ORDWR`
- `P9FS_OEXEC`
- `P9FS_OTRUNC`

Research-relevant notes:
- These are filesystem-layer constants, distinct from the fuller protocol enum in `p9_protocol.h`.
- The file currently contains only open permission bits and a commented-out include for virtio 9P definitions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_subr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_subr.c

This file implements p9fs non-VFS helper routines for session lifecycle and fid management.

Key functions:
- `p9fs_proto_dotl()` checks whether a session negotiated `9P2000.L`.
- `p9fs_init_session()` creates the 9P client, records negotiated protocol flags, parses `access=`, attaches to the server, initializes the session node list and lock, and returns the mount fid.
- `p9fs_prepare_to_close()` breaks node parent references and begins client disconnect, allowing only cleanup clunks afterward.
- `p9fs_complete_close()` marks the client disconnected.
- `p9fs_close_session()` completes disconnect, destroys the client, destroys the session lock.
- `p9fs_fid_add()`, `p9fs_fid_remove()`, and `p9fs_fid_remove_all()` manage per-node fid lists and clunk removed fids.
- `p9fs_get_fid()` finds or creates a fid for a node/user/type/mode by attaching as needed and walking from root to the node.
- Internal helpers build full root-to-node path arrays and test whether an existing open fid is compatible with a requested mode.

Access modes:
- `access=any`: reuse the session uid.
- `access=single`: session flag is set but uid selection still falls through to credential uid unless handled elsewhere.
- `access=user`: attach per user; this is the default.

Research-relevant risks:
- `p9fs_get_fid()` walks path chunks of at most `P9_MAXWELEM`, but passes the same `wnames` base pointer each time rather than offsetting by `i`; that is notable for path lengths over one chunk.
- `p9fs_fid_remove_all()` walks/removes lists without taking the per-list locks used by add/remove helpers.
- Parent references are broken during close to avoid vnode reference cycles before flush.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_vfsops.c

This file implements p9fs mount-level VFS operations and vnode creation/common lookup support.

Initialization:
- Creates UMA zones for p9fs nodes, getattr buffers, setattr buffers, I/O buffers, and pbufs.
- Calls `p9_init_zones()` for client-layer fid/request/buffer zones.
- Destroys all zones in `p9fs_uninit()`.

Mount/unmount:
- `p9_mount()` validates options (`from`, `trans`, `access`, `msize`), extracts the mount tag, allocates `struct p9fs_mount`, initializes the session/root node, creates the 9P session, installs mount flags, and marks the mount local/shared-lookup capable.
- `p9fs_mount()` supports a minimal update path that can clear read-only if remounted writable, otherwise calls `p9_mount()`.
- `p9fs_unmount()` begins disconnect, repeatedly flushes vnodes with optional force close, closes the session, frees mount data, and restores transport status if unmount fails.

Vnode/node handling:
- `p9fs_dispose_node()` detaches vnode data, releases parent vnode references, frees inode names and non-root node storage.
- `p9fs_destroy_node()` destroys fid-list mutexes then disposes the node.
- `p9fs_node_cmp()` compares vnode qid path, and for non-root also qid mode/version.
- `p9fs_vget_common()` is the shared vnode lookup/create path:
  - Hashes by qid path.
  - Searches the vnode hash with `p9fs_node_cmp()`.
  - Reloads stats for existing non-root vnodes and drops stale deleted nodes.
  - Allocates a vnode and node if needed.
  - Adds the initial fid to the node.
  - Records parent/session/name metadata.
  - Inserts into mount queue and vnode hash.
  - Adds new nodes to the session node list and marks them constructed.

Other VFS operations:
- `p9fs_root()` gets a fid for the root, falling back to the mount fid during disconnect, and returns the root vnode through `p9fs_vget_common()`.
- `p9fs_statfs()` gets root fid, calls `p9_client_statfs()`, and fills FreeBSD `statfs`, capping block size at `PAGE_SIZE`.
- `p9fs_fhtovp()` is unsupported and returns `EINVAL`.

Research-relevant risks:
- `p9fs_vget_common()` has complex cleanup behavior around `insmntque()`, stale vnode removal, reload failures, and duplicate hash insertion.
- `p9fs_statfs()` returns success even if `p9_client_statfs()` fails, setting only fallback block sizes.
- `p9_mount()` stores `mount_tag` as the mount option buffer pointer rather than duplicating it.
- The filesystem is registered as jail-capable with `VFS_SET(p9fs_vfsops, p9fs, VFCF_JAIL)`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_vfsops.c -->