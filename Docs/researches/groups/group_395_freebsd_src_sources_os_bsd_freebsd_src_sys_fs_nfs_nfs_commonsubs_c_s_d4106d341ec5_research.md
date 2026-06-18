# Group Research: group_395_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_nfs_nfs_commonsubs_c_s_d4106d341ec5

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonsubs.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonsubs.c

This file is the common NFS client/server protocol support layer. It builds and parses RPC/XDR mbuf chains, translates NFSv2/v3/v4 attributes and file handles, manages NFSv4.1 session sequencing, handles NFSv4 owner/owner-group name mapping, and provides small shared synchronization helpers used by both client and server code.

Key behavior:
- Defines global NFS constants and mapping tables: XDR booleans, vnode/NFS type maps, NFSv4 operation metadata, large-request/reply hints, NFSv4 minor-version operation maps, and initial root/bin/wheel/operator id-name mappings.
- `nfscl_reqstart()` initializes an `nfsrv_descript` and builds the leading NFS request for v2/v3/v4, including NFSv4 compound tags, operation counts, `Sequence`, `PutFH`, and optional weak-cache-consistency `Getattr` operations.
- `nfsm_strtom()`, `nfsm_fhtom()`, `nfsm_mbufuio()`, `nfsm_dissct()`, `nfsm_advance()`, `nfsrv_mtostr()`, `nfsm_set()`, and `nfsm_add_ext_pgs()` are the low-level mbuf/XDR construction and dissection helpers, including support for external-page mbufs.
- `nfsm_stateidtom()` serializes special and normal NFSv4 stateids.
- `nfscl_fillsattr()` serializes settable attributes for NFSv2, NFSv3, and NFSv4, including size/rdev special cases, timestamp policy, owner/group, mode, flags, birthtime, and NFSv4 `mode_umask` handling.
- `nfsv4_loadattr()` parses NFSv4 attributes into `nfsvattr`, statfs/fsinfo/pathconf structures, ACLs, file handles, lease values, clone block size, true ACL form, named-attribute state, and read-directory attribute errors. In compare mode it validates wire attributes against local vnode/filesystem state.
- `nfsv4_fillattr()` emits NFSv4 attributes from vnode attributes, export/filesystem state, ACL support, pathconf-derived capabilities, pNFS layout information, quotas, xattr support, and filesystem statistics.
- `nfsrv_getattrbits()`, `nfsrv_putattrbit()`, `nfsrv_getopbits()`, and `nfsrv_putopbit()` parse and serialize NFSv4 bitmap attribute/operation sets.
- `nfsrv_dissectacl()` parses NFSv4 or POSIX draft ACL wire data, optionally discarding unsupported or oversized ACLs while still advancing the XDR stream.
- `nfsv4_uidtostr()`, `nfsv4_gidtostr()`, `nfsv4_strtouid()`, and `nfsv4_strtogid()` translate between numeric ids and NFSv4 owner strings using cached mappings, `nfsuserd`, domain suffix logic, and numeric fallback rules.
- `nfsrv_nfsuserdport()`, `nfsrv_nfsuserddelport()`, `nfsrv_getuser()`, `nfssvc_idname()`, `nfsrv_removeuser()`, and `nfsrv_cleanusergroup()` manage per-vnet id/name hash tables, nfsuserd upcalls, default nobody/nogroup identities, cache expiration, approximate LRU trimming, and teardown.
- `nfsv4_lock()`, `nfsv4_unlock()`, `nfsv4_getref()`, `nfsv4_getref_nonblock()`, `nfsv4_relref()`, and `nfsv4_testlock()` implement a small NFSv4 shared-reference/exclusive-sleep-lock primitive.
- `nfsrv_checkutf8()` validates NFSv4 UTF-8 strings, including continuation-byte and surrogate range checks.
- `nfsrv_getrefstr()` parses `fs_locations` referral attributes into internal root/server-list strings.
- `nfsrvd_rephead()` initializes server reply mbufs, using clusters or external pages for large replies.
- `newnfs_sndlock()` / `newnfs_sndunlock()` serialize socket connect/disconnect style operations.
- `nfsv4_getipaddr()` parses NFSv4 network address strings into IPv4/IPv6 socket addresses and protocol selection.
- `nfsv4_seqsession()`, `nfsv4_seqsess_cacherep()`, `nfsv4_setsequence()`, `nfsv4_sequencelookup()`, and `nfsv4_freeslot()` implement NFSv4.1 session slot sequencing, retry detection, cached replies, bad-slot handling, and forced-dismount escape paths.
- `nfsv4_findmirror()` searches pNFS device state for a matching data-server mount.
- `nfsrpc_destroysession()` sends an NFSv4.1 `DestroySession` compound.
- `nfs_trueform()`, `vtonfsv4_type()`, and `nfsv4tov_type()` convert ACL model and vnode/file types, including named attribute directory/file encodings.

Important interactions:
- Uses `nfsm_subs.h` macros and `struct nfsrv_descript` cursor fields for all mbuf building/parsing.
- Declares and implements many prototypes exposed through `nfs_var.h`.
- Depends on vnode/VFS operations for ACLs, pathconf, statfs, quota checks, and mounted-on-fileid behavior.
- Interacts with `nfsuserd(8)` through a loopback RPC socket for NFSv4 id-name translation.
- Uses per-vnet globals for name caches and defaults, so jail/vnet teardown must call `nfsrv_cleanusergroup()`.
- Coordinates with NFSv4.1 client session state in `struct nfsclsession`, including MDS/DS sessions and pNFS behavior.
- Uses the `nfsv4_opflag` table to drive server/client compound construction, current file-handle needs, sequencing, and reply cache expectations.

Edge cases:
- Many parsers cap untrusted counts and lengths, such as ACL entries, owner/group strings, attr bitmap words, referral strings, server lists, and network address strings.
- Attribute compare mode deliberately maps unsupported ACLs, hidden/system flags, clone block size, and pNFS layout support to protocol errors such as `NFSERR_ATTRNOTSUPP` or `NFSERR_NOTSAME`.
- Numeric owner/group strings are accepted only for AUTH_SYS/client-side or explicitly enabled server-side string-to-id cases, not Kerberos.
- Some known nonconforming server values are normalized, for example extreme or zero `maxname`.
- Session sequencing treats duplicate seqids as retries, can return cached replies, and returns `NFSERR_SEQMISORDERED` when all usable slots are bad.
- Forced unmount paths avoid indefinite waits in lock/reference and session-slot acquisition loops.
- The id-name cache uses careful lock ordering across name and id hash tables to avoid lock-order reversals.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonsubs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_var.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_var.h

This is the broad internal prototype header for FreeBSD’s shared NFS client/server implementation. It forward-declares NFS structures and publishes cross-file function interfaces for server state, server RPC dispatch, duplicate request cache, common mbuf/attribute helpers, client RPC operations, client state management, VFS-port routines, and kernel RPC transport glue.

Key behavior:
- Forward-declares shared NFS types such as mounts, request descriptors, file handles, client/server state objects, sessions, layouts, device info, vattrs, and service argument structures.
- Groups prototypes by implementation file, making module boundaries explicit.
- Exposes NFSv4 server state control from `nfs_nfsdstate.c`: client/session creation and destruction, opens, locks, delegations, layout operations, stable storage, pNFS device IDs, and recovery/reclaim handling.
- Exposes server operation handlers from `nfs_nfsdserv.c` for NFSv3/v4 procedures, including ordinary vnode operations, sessions, pNFS, copy/clone/seek, and extended attributes.
- Exposes server socket/cache entry points from `nfs_nfsdsocket.c` and `nfs_nfsdcache.c`.
- Exposes shared helpers from `nfs_commonsubs.c`: request start, XDR/string/file-handle helpers, NFSv4 attributes, common locks, nfsuserd/id-name mapping, session sequencing, pNFS mirror lookup, ext-page mbuf growth, and destroy-session RPC.
- Exposes client-side common parsing and request helpers from `nfs_clcomsubs.c`.
- Exposes server-side vnode/attribute/file-handle helpers from `nfs_nfsdsubs.c`, `nfs_commonport.c`, `nfs_commonacl.c`, and `nfs_nfsdport.c`.
- Exposes client RPC functions from `nfs_clrpcops.c` for metadata, I/O, directory, locking, ACL, session, pNFS, copy/clone/seek, and xattr operations.
- Exposes NFSv4 client state management from `nfs_clstate.c`: opens, locks, delegations, client/session recovery, layout/device lifetime, renew thread behavior, and close/delegation return.
- Exposes client port/VFS glue from `nfs_clport.c`, client initialization, bio flush, node cache invalidation, common kernel RPC, server krpc, and callback daemon entry points.

Important interactions:
- This header is the main compile-time coupling point between NFS protocol code, VFS-port code, client state code, server state code, and transport code.
- It relies on types and macros from other NFS headers such as `nfsport.h`, `nfsdport.h`, `nfsclstate.h`, and protocol constant headers.
- The prototypes reflect FreeBSD-specific vnode, mount, thread, credential, and mbuf interfaces while preserving some portable naming conventions inherited from the multi-platform NFS code.

Edge cases:
- Because this is a central header, signature changes here imply broad rebuild and coordination across client, server, pNFS, and callback code.
- Many functions carry `NFSPROC_T *`, `struct ucred *`, and `struct nfsrv_descript *` parameters; callers must preserve protocol version, credential, and descriptor state correctly across layers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_var.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfscl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfscl.h

This header contains small NFS client-side definitions used by the FreeBSD NFSv4 client.

Key behavior:
- Defines `struct nfsv4node`, an allocation-sized extension for an NFSv4 `nfsnode` that stores file-handle length, name length, and contiguous file-handle/name data.
- Defines `NFS4NODENAME()` to locate the node name immediately after the file handle bytes.
- Defines `NFSCL_REQSTART()` as a convenience wrapper around `nfscl_reqstart()` for vnode-based client RPC calls.
- Defines lease/renew conversion macros `NFSCL_RENEW()` and `NFSCL_LEASE()`, currently using a half-lease renew interval.
- Defines `NFSCL_FORCEDISM()` to detect forced unmount state from mount flags and NFS mount private flags.
- Defines client set-attribute flags passed to `nfscl_fillsattr()`, including full attribute send, size zero, size negative-one, rdev-as-size, and new-file handling.
- Defines `NFSCL_DEBUG()` gated by `nfscl_debuglevel`.
- Defines `struct nfscl_reconarg`, which carries minor version and session id for reconnect/session recovery.

Important interactions:
- `NFSCL_REQSTART()` depends on vnode-to-NFS mount/node macros and starts requests with the vnode’s current file handle.
- `NFSCL_FORCEDISM()` is used by lock/session wait paths to break out during forced dismount.
- `NFSSATTR_*` flags are interpreted in `nfscl_fillsattr()`.

Edge cases:
- `struct nfsv4node` uses a one-byte flexible tail pattern and must be allocated large enough for both file handle and name.
- The renew/lease macros are deliberately simple inverses; lease policy changes should keep that relationship in mind.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfscl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsclstate.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsclstate.h

This header defines the NFSv4 client-side state model: client IDs, open owners, opens, lock owners, byte-range locks, delegations, NFSv4.1 sessions, data-server connections, pNFS layouts, flex-file mirrors, recall records, and device information.

Key behavior:
- Declares list/head types and hash macros for delegations, opens, layouts, lock owners, and device info.
- `struct nfsclsession` stores NFSv4.1 session state: mutex, callback slots, client id, backchannel transport, slot sequence numbers, active/bad slot bitmaps, limits, slot counts, session id, and defunct status.
- `struct nfsclds` represents an MDS/DS server endpoint with session state, socket request pointer, expiry, verifier, flags, and variable-length server owner.
- `struct nfsclclient` stores a mounted client’s NFSv4 state roots: owner/open/delegation/layout/device lists and hashes, shared lock, renew thread, mount pointer, expiry, counters, clientid revision, callbacks, flags, and variable client id.
- `struct nfsclowner` tracks an open-owner sequence stream and its opens.
- `struct nfscldeleg` tracks a delegation for a file handle, including delegated stateid, ACE, local owners/locks, credential, size/change/modtime snapshots, timestamps, and flags.
- `struct nfsclopen` tracks an open stateid, owner, credential, mode, open count, POSIX locking state, and file handle.
- `struct nfscllockowner` and `struct nfscllock` track NFSv4 byte-range lock ownership and local lock ranges.
- `struct nfscllayout`, `struct nfsclflayout`, `struct nfsffm`, `struct nfsclrecalllayout`, and `struct nfscldevinfo` define pNFS file/flex-file layout segments, mirrors, recalls, and device-address mappings.
- Inline helpers return device address slots and get/set compact stripe indices stored after the device-address pointer array.
- Defines state flag sets for data-server endpoints, clients, delegations, layouts, file-layout segments, and device info.
- Defines `NFSCL_INCRSEQID()` to increment an owner seqid only when the descriptor indicates it should.

Important interactions:
- The structs are consumed by `nfs_clstate.c`, `nfs_clrpcops.c`, session sequencing in `nfs_commonsubs.c`, and pNFS I/O/layout code.
- Hash macros depend on `ncl_hash()` and file-handle bytes to locate open/delegation/layout records.
- Layout/device structures share variable-length trailing storage; allocation size must match file-handle, address, stripe-index, or mirror counts exactly.

Edge cases:
- `nfsclsession` slot state uses 64-bit slot bitmaps and a fixed 64-entry sequence array, so session slot counts are bounded by that representation.
- Defunct sessions, bad slots, recalled layouts, returned layouts, and forced unmount flags are represented explicitly and must be checked by session/layout users.
- Flex-file and file-layout variants share unions; code must consult flags before interpreting the union fields.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsclstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsdport.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsdport.h

This FreeBSD port header adapts generic NFS server code to FreeBSD vnode, mount, credential, export, namei, file, and debug conventions.

Key behavior:
- Defines `NFSVNO_*` macros for initializing, setting, testing, and unsetting `nfsvattr` fields using FreeBSD `vattr` storage and `VNOVAL`.
- Defines `struct nfsexstuff`, a catch-all export result used by file-handle-to-vnode and export checks. It carries export flags plus accepted security flavors.
- Defines `NFSEXITCODE()` and `NFSEXITCODE2()` as no-ops on FreeBSD; comments describe a non-upstream EXITCODE tracing facility used elsewhere.
- Defines export flag helpers for read-only, anon, strict-access, v4-only, and TLS/certificate export modes.
- Defines `NFSVNO_SETEXRDONLY()` to mark an export record read-only.
- Defines `NFSVNO_CMPFH()` for comparing FreeBSD file handles by fsid and fid.
- Defines `NFSLOCKHASH()` for selecting an NFS lock hash bucket from a file handle.
- Defines file pointer accessor macros for vnode, credential, and flags.
- Defines `NFSNAMEICNDSET()` to populate FreeBSD namei component fields.
- Defines FreeBSD path length type, server file-handle min/max sizes, and `NFSD_DEBUG()` gated by `nfsd_debuglevel`.

Important interactions:
- Used by server-side code that is shared with other platform ports but needs FreeBSD-specific vnode/export/namei behavior.
- `nfsexstuff` is passed through server access, lookup, file-handle, and export-check paths.
- `NFSEXITCODE*` calls in common code compile away on FreeBSD.

Edge cases:
- The file-handle size macros are fixed to `sizeof(fhandle_t)`, matching FreeBSD’s server-side native file handle.
- The attribute macros assume `struct nfsvattr` embeds/aliases fields using the `na_` naming convention.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsdport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsid.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsid.h

This header defines the user/group id-to-name mapping ABI used by NFSv4 owner and owner_group handling.

Key behavior:
- Defines `struct nfsd_idargs`, the argument block for id/name updates from userland, including flag, uid, gid, cache maximum, timeout, name pointer/length, group list pointer, and group count.
- Defines operation flags for initializing the mapping domain, adding/deleting uid mappings, adding/deleting username mappings, adding/deleting gid mappings, adding/deleting group-name mappings, and marking the name pointer as kernel-space.
- Under kernel builds, defines `struct nfs_prime_userd`, the minimal bootstrap mapping record used before `nfsuserd(8)` is available.
- Declares `nfssvc_idname()` for kernel consumers.

Important interactions:
- `nfs_commonsubs.c` implements `nfssvc_idname()` and consumes the flag definitions to update per-vnet user/group hash caches.
- The structure forms part of the `nfssvc(2)` path used by userland `nfsuserd`.
- Bootstrap mappings must match system passwd/group identities for root/bin/wheel/operator/nobody-style entries.

Edge cases:
- `NFSID_SYSSPACE` controls whether names are copied from user memory or kernel memory.
- Group lists are only meaningful for uid mappings that also populate a credential with server-side group membership.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfskpiport.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfskpiport.h

This small port header provides Darwin-style KPI typedefs needed by shared NFS code while building on FreeBSD.

Key behavior:
- Defines `mount_t` as `struct mount *`.
- Defines `vnode_t` as `struct vnode *`.
- Wraps the definitions in `_NFS_NFSKPIPORT_H_` include guards.

Important interactions:
- Lets shared code use portable `mount_t` and `vnode_t` names without changing FreeBSD kernel types.
- Included by NFS port/common headers that retain compatibility naming from the multi-platform NFS code base.

Edge cases:
- This header only aliases types; it does not provide any behavioral compatibility layer.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfskpiport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsm_subs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsm_subs.h

This header defines the low-level mbuf-chain build/dissect macros used throughout the NFS protocol encoder and decoder.

Key behavior:
- Defines `NFSM_DATAP()` to advance an mbuf data pointer.
- Provides inline `nfsm_build()` to reserve contiguous output space from the current `nfsrv_descript` mbuf. It appends a new mbuf when normal trailing space is insufficient, or allocates a new external-page mbuf when ext-page space is insufficient.
- Defines `NFSM_BUILD()` as the typed assignment wrapper around `nfsm_build()`.
- Provides inline `nfsm_dissect()` and `nfsm_dissect_nonblock()` to return contiguous input bytes from the current descriptor position, falling back to `nfsm_dissct()` when data spans mbufs.
- Defines `NFSM_DISSECT()` and `NFSM_DISSECT_NONBLOCK()` wrappers that jump to `nfsmout` with `EBADRPC` on parse failure.
- Defines `NFSM_STRSIZ()` to parse an XDR string length and enforce a caller-provided maximum.
- Defines `NFSM_RNDUP()` for 4-byte XDR alignment.

Important interactions:
- These macros assume local variables named `nd`, `error`, `tl`, and `nfsmout` in many call sites.
- The heavy fallback and ext-page support are implemented in `nfs_commonsubs.c`.
- Used by client RPC builders, server reply builders, and all common XDR parsers.

Edge cases:
- The macros are intentionally specialized for NFS mbuf cursor state and are unsafe as general mbuf utilities.
- `nfsm_build()` panics if a requested normal-mbuf build size exceeds `MLEN`.
- Ext-page and non-ext-page mbuf construction paths must not be mixed for the same descriptor.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsm_subs.h -->