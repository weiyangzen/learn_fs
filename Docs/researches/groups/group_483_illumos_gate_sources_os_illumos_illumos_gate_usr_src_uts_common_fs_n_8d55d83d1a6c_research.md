# Group Research: group_483_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_8d55d83d1a6c

Scope verified against `Docs/research_subset_a.md`: these files are within `sources/os/illumos/illumos-gate`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_xdr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_xdr.c

## Purpose

This file provides hand-maintained XDR encode/decode/free routines for NFSv4 minor-version extensions, mainly NFSv4.1 and NFSv4.2 protocol data. It is explicitly not a raw `rpcgen` output file: the header warns that generated code must be manually integrated because this file contains hand-coded attribute XDR.

## Main Responsibilities

- Encode/decode NFSv4.1 scalar and compound data types:
  - `verifier4`, `sequenceid4`, `sessionid4`, `slotid4`, `clientid4`, `stateid4`, `offset4`, `length4`, `count4`, `mode4`.
- Encode/decode NFSv4.1 attributes and metadata:
  - ACL flags and `nfsacl41`.
  - mode-set-masked attributes.
  - implementation identity, fs status, charset capability, retention attributes, fs locations info.
- Encode/decode pNFS structures:
  - layout type/content/iomode.
  - device IDs and device addresses.
  - layout get/commit/return/update.
  - file-layout data-server address and file-layout bodies.
  - layout recall callback structures.
- Encode/decode NFSv4.1 session and backchannel operations:
  - `BACKCHANNEL_CTL`, `BIND_CONN_TO_SESSION`, `EXCHANGE_ID`, `CREATE_SESSION`, `DESTROY_SESSION`, `SEQUENCE`, `SET_SSV`, `TEST_STATEID`, `FREE_STATEID`, `RECLAIM_COMPLETE`.
- Encode/decode NFSv4.2 operations:
  - `ALLOCATE`, `COPY`, `COPY_NOTIFY`, `DEALLOCATE`, `IO_ADVISE`, `LAYOUTERROR`, `LAYOUTSTATS`, `OFFLOAD_CANCEL`, `OFFLOAD_STATUS`, `READ_PLUS`, `SEEK`, `WRITE_SAME`, `CLONE`.
- Encode/decode NFSv4.1 callback operations:
  - layout recall, notify, push delegation, recall any, recallable object available, recall slot, callback sequence, wants cancelled, notify lock, notify device ID.
- Dispatch operation-specific unions via:
  - `xdr_nfs4x_argop4()`.
  - `xdr_nfs4x_resop4()`.
  - `xdr_nfs_cb_argop4()`.
  - `xdr_nfs_cb_resop4()`.

## Important Control Flow

Most functions are thin XDR wrappers that serialize fields in wire order and return `FALSE` on the first failed field. Union-like protocol structures are handled by reading or using an enum/status discriminator, then switching to the correct arm.

Key dispatchers:

- `xdr_nfs4x_argop4()` assumes the operation number was already XDR’d and switches on `objp->argop` for all NFSv4.1 and NFSv4.2 argument bodies.
- `xdr_nfs4x_resop4()` mirrors argument dispatch for result bodies, including status-dependent success payloads.
- `xdr_nfs_cb_argop4()` dispatches callback argument bodies for NFSv4.1 callback operations.
- `xdr_nfs_cb_resop4()` reads `resop` itself with `xdr_u_int()` and dispatches callback result bodies, including legacy callback results such as `OP_CB_GETATTR`, `OP_CB_RECALL`, and `OP_CB_ILLEGAL`.

Status-dependent result routines generally encode a status first and only encode success payloads on `NFS4_OK`; some operations encode specific failure payloads, such as:

- `GETDEVICEINFO` encodes `gdir_mincount` on `NFS4ERR_TOOSMALL`.
- `LAYOUTGET` encodes `logr_will_signal_layout_avail` on `NFS4ERR_LAYOUTTRYLATER`.
- `COPY` encodes copy requirements on `NFS4ERR_OFFLOAD_NO_REQS`.

## Notable Implementation Details

- `xdr_bitmap4_notify()` is a special single-word bitmap encoder used for notification bitmaps. It asserts encode mode and writes a length of `1`, then selects the correct 32-bit word depending on endian layout.
- `xdr_layoutrecall_file()` decodes and frees file handles but deliberately returns `FALSE` for encode with a `TODO: encode nfs4x_fh` comment.
- Several optional protocol fields are modeled as XDR arrays with max length `1`, such as optional retention begin time, optional stateids, and optional cookies.
- Opaque values use bounded XDR helpers where protocol limits exist, for example `NFS4_OPAQUE_LIMIT`, `NFS4_SESSIONID_SIZE`, `NFS4_DEVICEID4_SIZE`, and `NFS4_FHSIZE`.
- `xdr_netloc4()` rejects unknown netloc union discriminants instead of ignoring them.

## Dependencies

- Includes:
  - `<sys/statvfs.h>`
  - `<sys/sysmacros.h>`
  - `<sys/sdt.h>`
  - `<nfs/nfs4.h>`
  - `<nfs/nfs4_attr.h>`
- Reuses common NFSv4 XDR helpers from elsewhere, including:
  - `xdr_fattr4`
  - `xdr_nfsace4`
  - `xdr_bitmap4`
  - `xdr_nfstime4`
  - `xdr_utf8string`
  - `xdr_nfs_fh4`
  - `xdr_SECINFO4res`

## State and Memory Ownership

This file does not maintain persistent state. Memory ownership is delegated to XDR array/string/bytes routines. Routines that process variable-length arrays pass field pointers and length pointers into `xdr_array()` or `xdr_bytes()`, so decode/free behavior depends on the standard XDR memory semantics.

## Risks and Edge Cases

- Unknown enum discriminants generally return `FALSE`, which is strict and appropriate for protocol XDR but can reject forward-compatible values.
- `xdr_layoutrecall_file()` cannot encode file-layout recall file handles yet, so any path needing that encode direction will fail.
- Notification bitmaps rely on endian-specific layout assumptions in `xdr_bitmap4_notify()`.
- Many arrays use `~0` as max length, relying on upstream request sizing and XDR allocation behavior rather than local semantic caps.
- This file must stay synchronized with NFSv4 protocol structs in headers; hand-maintained XDR makes drift a real integration risk.

## Testing Notes

Useful tests would exercise encode/decode/free round trips for:

- Session setup operations.
- pNFS layout/device operations.
- NFSv4.2 sparse/offload operations.
- Callback sequence and notification operations.
- Error-result arms with non-success payloads.
- Little-endian and big-endian bitmap notification encoding.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_acl_srv.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_acl_srv.c

## Purpose

This file implements the server-side handlers for the Solaris/illumos NFS ACL side protocol for NFSv2 and NFSv3 style clients. It translates ACL RPC requests into vnode operations and translates vnode errors and attributes back into NFS ACL protocol results.

## Main Responsibilities

- NFS ACL v2 server procedures:
  - `acl2_getacl()`
  - `acl2_setacl()`
  - `acl2_getattr()`
  - `acl2_access()`
  - `acl2_getxattrdir()`
- NFS ACL v3 server procedures:
  - `acl3_getacl()`
  - `acl3_setacl()`
  - `acl3_getxattrdir()`
- File-handle extraction helpers for RPC dispatch:
  - `acl2_getacl_getfh()`, `acl2_setacl_getfh()`, `acl2_getattr_getfh()`, `acl2_access_getfh()`, `acl2_getxattrdir_getfh()`
  - `acl3_getacl_getfh()`, `acl3_setacl_getfh()`, `acl3_getxattrdir_getfh()`
- Response cleanup helpers:
  - `acl2_getacl_free()`
  - `acl3_getacl_free()`

## Important Control Flow

`acl2_getacl()` and `acl3_getacl()`:

1. Convert the incoming file handle to a vnode with `nfs_fhtovp()` or `nfs3_fhtovp()`.
2. Initialize the response `vsecattr_t`.
3. Call `VOP_GETSECATTR()`.
4. If the filesystem returns `ENOSYS` and the export does not set `EX_NOACLFAB`, fabricate an ACL with `fs_fab_acl()`.
5. Fetch file attributes with `rfs4_delegated_getattr()`.
6. Convert attributes with `vattr_to_nattr()` for v2 or `vattr_to_post_op_attr()` for v3.
7. Free unrequested ACL/default-ACL arrays according to the request mask.

`acl2_setacl()` and `acl3_setacl()`:

1. Resolve the file handle.
2. Check read-only exports with `rdonly()`.
3. Take the vnode write lock.
4. Call `VOP_SETSECATTR()`.
5. Fetch post-operation attributes.
6. Return NFS status and attributes.

`acl2_access()`:

- Computes access bits by checking `VOP_ACCESS()` for read, lookup, modify, extend, delete, and execute.
- Suppresses write checks for regular files and directories on read-only exports.
- Denies read/write/execute bits on mandatory-lock files where appropriate.
- Returns full attributes after the access computation.

`acl2_getxattrdir()` and `acl3_getxattrdir()`:

- Resolve the base vnode.
- Use `LOOKUP_XATTR`, with `CREATE_XATTR_DIR` when requested.
- For non-create lookups, first checks `_PC_SATTR_EXISTS` and `_PC_XATTR_EXISTS` to avoid creating or looking up a missing hidden attribute directory unnecessarily.
- Calls `VOP_LOOKUP()` with an empty name and xattr flags.
- Builds a returned NFS file handle and attributes for the xattr directory.

## Error Handling

- v2 handlers return `NFSERR_STALE`, `NFSERR_ROFS`, `NFSERR_NOENT`, or `puterrno(error)` results.
- v3 handlers return `NFS3ERR_*` statuses via `puterrno3(error)`.
- v3 GETACL and SETACL translate `T_WOULDBLOCK` into `NFS3ERR_JUKEBOX`.
- On failed GETACL after ACL allocation, the code frees allocated ACL arrays before returning.
- v3 failure results include weak/post-op attributes when available.

## Dependencies

- Vnode operations:
  - `VOP_GETSECATTR`
  - `VOP_SETSECATTR`
  - `VOP_GETATTR`
  - `VOP_ACCESS`
  - `VOP_LOOKUP`
  - `VOP_PATHCONF`
  - `VOP_RWLOCK`
  - `VOP_RWUNLOCK`
- NFS helpers:
  - `nfs_fhtovp`
  - `nfs3_fhtovp`
  - `makefh`
  - `makefh3`
  - `vattr_to_nattr`
  - `vattr_to_post_op_attr`
  - `rfs4_delegated_getattr`
- ACL/filesystem helpers:
  - `fs_fab_acl`
  - `rdonly`
- Kernel allocation:
  - `kmem_free`

## State and Memory Ownership

This file does not own global state. It allocates no persistent objects but must free ACL arrays returned by `VOP_GETSECATTR()` or `fs_fab_acl()` when those arrays are not returned to the RPC layer or when response cleanup is called. The response cleanup helpers free only successful GETACL responses.

## Risks and Edge Cases

- ACL fabrication exists specifically for filesystems like ZFS that support ACE-style ACLs but not `aclent_t`; export option `EX_NOACLFAB` disables this compatibility behavior.
- `acl2_getxattrdir()` and `acl3_getxattrdir()` guard against old filesystems returning the same vnode for empty-name xattr lookup.
- `acl3_setacl()` uses shared cleanup labels; the vnode is unlocked and released through `out1` when held.
- Extended attribute existence probes are best-effort; errors from `_PC_SATTR_EXISTS` and `_PC_XATTR_EXISTS` do not by themselves stop lookup unless both probes prove absence.

## Testing Notes

Relevant coverage should include:

- GETACL with native ACL support.
- GETACL with `ENOSYS` and fabricated ACLs.
- GETACL with masks excluding ACL/default ACL arrays.
- SETACL on writable and read-only exports.
- ACCESS on mandatory-lock files and read-only exports.
- GETXATTRDIR create and non-create paths for v2 and v3.
- v3 `T_WOULDBLOCK` to `NFS3ERR_JUKEBOX` translation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_acl_srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_acl_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_acl_vnops.c

## Purpose

This file implements client-side vnode ACL operations for the NFS ACL side protocol. It sends NFS ACL RPCs over the wire, integrates returned attributes into the NFS attribute cache, maintains per-rnode ACL caches, and implements hidden extended-attribute-directory lookup for NFSv2 and NFSv3 clients.

## Main Responsibilities

- NFS ACL v2 client operations:
  - `acl_getacl2()`
  - `acl_setacl2()`
  - `acl_getattr2_otw()`
  - `acl_access2()`
  - `acl_getxattrdir2()`
- NFS ACL v3 client operations:
  - `acl_getacl3()`
  - `acl_setacl3()`
  - `acl_getxattrdir3()`
- ACL cache management:
  - `nfs_acl_free()`
  - `nfs_acl_dup_cache()`
  - `nfs_acl_dup_res_impl()`
  - `nfs_acl_dup_res()`
- RPC metadata tables:
  - `aclnames_v2`
  - `acl_call_type_v2`
  - `acl_timer_type_v2`
  - `acl_ss_call_type_v2`
  - `aclnames_v3`
  - `acl_call_type_v3`
  - `acl_ss_call_type_v3`
  - `acl_timer_type_v3`

## Important Control Flow

`acl_getacl2()` and `acl_getacl3()`:

1. Check `rnode_t::r_secattr` for a cached ACL.
2. Validate caches with `nfs_validate_caches()` or `nfs3_validate_caches()`.
3. If the cached ACL covers the requested mask, duplicate it into the caller’s `vsecattr_t`.
4. Otherwise send `ACLPROC2_GETACL` or `ACLPROC3_GETACL`.
5. Cache returned file attributes.
6. Duplicate returned ACLs into the rnode cache with `nfs_acl_dup_res()`.
7. Return the RPC-owned ACL arrays to the caller by assigning `*vsp = res.resok.acl`.

`acl_setacl2()` and `acl_setacl3()`:

- Send SETACL over the wire.
- Always flush `rp->r_secattr` afterward because using SETACL input as cache content is not reliable and errors make existing cache contents unsafe.
- Cache returned attributes on success or post-op attributes on v3 failure.

`acl_access2()`:

- Converts vnode mode bits into ACL protocol access bits.
- Checks local access cache with `nfs_access_check()`.
- Uses `crnetadjust()` to retry with adjusted network credentials if a cached or remote denial may be credential-shape dependent.
- Sends `ACLPROC2_ACCESS` if no decisive cache entry exists.
- Stores returned access results with `nfs_access_cache()`.

`acl_getxattrdir2()` and `acl_getxattrdir3()`:

- Send GETXATTRDIR over the wire.
- Create NFS client vnodes with `makenfsnode()` or `makenfs3node()`.
- Mark returned vnode with `V_XATTRDIR`.
- Update DNLC with `XATTR_DIR_NAME` unless this was a soft failover-style call.
- On `ENOENT`, optionally negative-cache the lookup with `DNLC_NO_VNODE`.

## State and Memory Ownership

- `rnode_t::r_secattr` is protected by `r_statelock`.
- `nfs_acl_dup_cache()` allocates new ACL arrays for the caller when satisfying from cache.
- `nfs_acl_dup_res_impl()` updates or allocates the rnode cache, resizing cached ACL/default-ACL arrays when counts change.
- `nfs_acl_free()` frees both ACL arrays and the `vsecattr_t` wrapper.
- `acl_getacl2()` and `acl_getacl3()` transfer successful result ACL arrays to the caller by assigning `*vsp`; the caller is responsible for freeing them.
- `xattr_lookup_neg_cache` controls whether missing xattr directory lookups are negative-cached.

## Dependencies

- RPC call helpers:
  - `acl2call`
  - `acl3call`
- XDR routines from `nfs_acl_xdr.c`.
- NFS client helpers:
  - `nfs_cache_fattr`
  - `nfs3_cache_post_op_attr`
  - `makenfsnode`
  - `makenfs3node`
  - `nfs_access_check`
  - `nfs_access_cache`
  - `PURGE_STALE_FH`
- Failover support:
  - `failinfo_t`
  - `nfscopyfh`, `nfs3copyfh`
  - `nfslookup`, `nfs3lookup`
  - xattr dir callback pointers.
- DNLC:
  - `dnlc_update`
  - `dnlc_enter`

## Risks and Edge Cases

- ACL cache duplication must keep mask/count/data consistency; `nfs_acl_dup_res_impl()` explicitly clears cached ACL data when counts change.
- `acl_access2()` has subtle credential ownership behavior: adjusted credentials cached into access cache must not be freed prematurely.
- v3 xattr-dir creation handles missing post-op attributes by creating a vnode without attrs and then fetching `AT_TYPE` if vnode type is `VNON`.
- Negative xattr-dir caching is tunable via `xattr_lookup_neg_cache`.
- SETACL cache invalidation is intentionally conservative.

## Testing Notes

Useful coverage should include:

- ACL cache hit and cache miss paths.
- Partial mask cache hits and misses.
- SETACL invalidating cached ACLs.
- ACCESS cache allowed, denied, and unknown paths.
- Credential-adjusted retry behavior.
- GETXATTRDIR v2/v3 success, `ENOENT`, negative caching, and failover flags.
- v3 GETACL/SETACL post-op attribute handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_acl_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_acl_xdr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_acl_xdr.c

## Purpose

This file contains XDR routines for the NFS ACL side protocol, covering ACL protocol v2 and v3 arguments/results plus shared ACL security attribute structures.

## Main Responsibilities

- Encode/decode basic ACL protocol types:
  - `xdr_uid()`
  - `xdr_o_mode()`
  - `xdr_aclent()`
  - `xdr_secattr()`
- Encode/decode NFS ACL v2 procedures:
  - GETACL
  - SETACL
  - GETATTR
  - ACCESS
  - GETXATTRDIR
- Encode/decode NFS ACL v3 procedures:
  - GETACL
  - SETACL
  - GETXATTRDIR
- Provide fast inline decode helpers for selected v2 arguments/results on supported paths:
  - `xdr_fastGETACL2args()`
  - `xdr_fastGETATTR2args()`
  - `xdr_fastACCESS2args()`
  - little-endian fast result helpers for fattrs and enums.

## Important Control Flow

`xdr_secattr()` serializes:

1. `vsa_mask`
2. `vsa_aclcnt`
3. ACL entry array, bounded by `NFS_ACL_MAX_ENTRIES`
4. `vsa_dfaclcnt`
5. default ACL entry array, bounded by `NFS_ACL_MAX_ENTRIES`

It derives the outgoing array count from whether the pointer is non-NULL. After XDR, it validates that the decoded/encoded count matches the advertised count when count is non-zero; on mismatch it stores the actual count back into the count field before returning `FALSE`.

v2 result routines:

- Encode/decode enum status.
- Only serialize `resok` on `NFS_OK`.

v3 argument routines:

- Use `xdr_nfs_fh3()` for encode/free.
- Use `xdr_nfs_fh3_server()` for decode to get server-side file-handle representation.

v3 result routines:

- Serialize post-op attributes on both success and failure for GETACL and SETACL.
- GETXATTRDIR success serializes the file handle using `xdr_nfs_fh3_server()` on encode and `xdr_nfs_fh3()` on decode/free.

## Dependencies

- Common NFS XDR:
  - `xdr_fhandle`
  - `xdr_fattr`
  - `xdr_fastfattr`
  - `xdr_fastenum`
  - `xdr_nfs_fh3`
  - `xdr_nfs_fh3_server`
  - `xdr_post_op_attr`
- ACL structures:
  - `aclent_t`
  - `vsecattr_t`
  - `NFS_ACL_MAX_ENTRIES`
- Protocol types from `<nfs/nfs_acl.h>`.

## State and Memory Ownership

This file has no persistent state. Memory allocation/free for ACL arrays is handled through `xdr_array()` based on the XDR operation. Decode allocates array storage when needed; free releases it through the same XDR routines.

## Risks and Edge Cases

- Fast inline decoders only work for `XDR_DECODE` and only when `XDR_INLINE()` returns enough contiguous data; otherwise they return `FALSE`.
- Little-endian fast paths manually convert inline fields with `ntohl()`.
- `xdr_secattr()` rejects count mismatches and updates the count to the actual XDR array count before failing, which helps cleanup but can surprise callers expecting original counts to remain unchanged.
- Several max lengths use `~0` for strings/byte arrays in surrounding helpers, but ACL arrays are bounded by `NFS_ACL_MAX_ENTRIES`.
- `xdr_GETXATTRDIR3res()` switches success on `NFS_OK` rather than `NFS3_OK`; both are success-zero constants in this codebase, but the mixed naming is a maintenance hazard.

## Testing Notes

Useful tests should cover:

- XDR encode/decode/free of `vsecattr_t` with ACL and default ACL arrays.
- Count mismatch behavior in `xdr_secattr()`.
- v2 fast inline decoders on little-endian and big-endian builds.
- v3 file-handle encode/decode mode-specific behavior.
- Failure result post-op attribute serialization for v3.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_acl_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_auth.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_auth.c

## Purpose

This file implements kernel-side NFS export authorization caching and mountd door callouts. It decides whether a client/security flavor/credential tuple has read-write, read-only, denied, wrong-security, mapped-anonymous, root, group, or limited NFS access to an export.

## Main Responsibilities

- Maintain per-export authorization caches.
- Call userland `mountd` through a door when cache data is missing or refreshed.
- Support per-zone NFS authorization state.
- Start and stop an async refresh thread for stale cache entries.
- Reclaim idle auth-cache entries under memory pressure.
- Provide NFSv4-specific access wrappers:
  - `nfsauth4_access()`
  - `nfsauth4_secinfo_access()`
- Provide common access entry point:
  - `nfsauth_access()`

## Main Data Structures

- `nfsauth_globals_t`
  - Per-zone state for mountd door handle, refresh queue, refresh thread state, and synchronization.
- `refreshq_exi_node_t`
  - Queue node grouping stale auth entries by export.
- `refreshq_auth_node_t`
  - Queue node for one stale auth cache entry and the netid that triggered refresh.
- `auth_cache_clnt`
  - Per-client-address cache node, stored in export hash buckets as AVL trees.
- `auth_cache`
  - Per-client, per-flavor, per-credential authorization entry.

## Lifecycle

Global lifecycle:

- `nfsauth_init()` creates the `exi_cache_handle` kmem cache for `struct auth_cache`.
- `nfsauth_fini()` destroys that kmem cache.

Zone lifecycle:

- `nfsauth_zone_init()` allocates per-zone state, initializes mountd and refresh locks, creates the refresh queue, and stores it in `ng->nfs_auth`.
- `nfsauth_zone_shutdown()` stops the refresh thread if running, drains queued refresh work, frees invalid auth entries, releases export holds, and destroys queued lists.
- `nfsauth_zone_fini()` releases the mountd door handle, destroys locks/CVs/lists, and frees per-zone state.

Mountd door lifecycle:

- `mountd_args()` looks up a door by ID, replaces the per-zone mountd door handle, and releases any previous handle.
- `nfsauth_retrieve()` holds the door handle while calling `door_ki_upcall_limited()` and handles revoked/stale door cases.

## Important Control Flow

`nfsauth_access()`:

1. Initializes uid/gid outputs, mapping root to export anonymous identity by default.
2. Reads the security flavor from `req->rq_xprt->xp_cookie`.
3. Finds matching export security info.
4. Falls back to `AUTH_NONE` when configured.
5. Grants pseudo/export namespace read-only access when a flavor exists only because of NFSv4 namespace setup and is not explicitly exported.
6. Uses fast-path permission checks when no root/none/map lists are involved.
7. Calls `nfsauth_cache_get()` when mountd policy data is needed.
8. Clears supplemental groups for denied or wrong-security results.
9. Retries through `AUTH_NONE` on wrong security where allowed.
10. Normalizes denied results to `NFSAUTH_DENIED`.

`nfsauth4_access()`:

- Calls `nfsauth_access()`.
- If denied or wrong-security, allows `NFSAUTH_LIMITED` when `has_visible(exi, vp)` reports visible subexports below the vnode.

`nfsauth4_secinfo_access()`:

- Checks whether a security flavor is explicitly exported with `M_4SEC_EXPORTED`.
- Uses fast RO/RW decisions when no lists are involved.
- Otherwise calls `nfsauth_cache_get()`.

`nfsauth_cache_get()`:

1. Copies and masks the client address using transport address mask.
2. Hashes the masked address into `exi->exi_cache`.
3. Finds or creates an `auth_cache_clnt` AVL node for the client.
4. Finds or creates an `auth_cache` node keyed by flavor and credential identity.
5. Waits if another thread is already retrieving the entry.
6. For new entries, calls `nfsauth_retrieve()` synchronously and publishes the result.
7. For fresh entries, returns cached uid/gid/groups/access and updates use time.
8. If the entry is older than `NFSAUTH_CACHE_REFRESH`, marks it stale and queues async refresh work.
9. If allocation fails, falls back to uncached `nfsauth_retrieve()`.

`nfsauth_retrieve()`:

- Builds a versioned `varg_t` request for `NFSAUTH_ACCESS`.
- XDR-encodes the request with `xdr_varg()`.
- Calls mountd over a kernel door.
- Retries when the door is not established, returns `NFSAUTH_DROP` after repeated absence, and handles revoked/stale handles.
- XDR-decodes `nfsauth_res_t`.
- Copies returned server uid/gid/groups to caller-owned storage.

`nfsauth_refresh_thread()`:

- Waits for queued stale cache entries.
- Marks entries `NFS_AUTH_REFRESHING`.
- Calls `nfsauth_retrieve()` without blocking foreground access paths.
- Updates cached access and mapped identity on success.
- Returns entries to `NFS_AUTH_FRESH` and wakes waiters.
- Frees entries that were invalidated while refresh was in flight.

Reclaim path:

- `exi_cache_reclaim()` walks all NFS server zones.
- `exi_cache_reclaim_zone()` walks exports in each zone.
- `exi_cache_trim()` removes auth entries idle longer than `NFSAUTH_CACHE_TRIM`, avoiding entries in `NFS_AUTH_WAITING`, marking stale/refreshing entries invalid, and freeing empty client nodes.

## Synchronization

- `mountd_lock` protects the per-zone mountd door handle.
- `refreshq_lock` and `refreshq_cv` protect the async refresh queue and refresh thread state.
- `exi->exi_cache_lock` protects per-export auth-cache bucket trees.
- `auth_cache_clnt::authc_lock` protects each client’s credential/flavor AVL tree.
- `auth_cache::auth_lock` and `auth_cv` protect individual auth entry state transitions.

## Cache Timing

- `NFSAUTH_CACHE_REFRESH`: 600 seconds before an entry is considered stale and scheduled for refresh.
- `NFSAUTH_CACHE_TRIM`: 3600 idle seconds before memory-pressure reclaim may trim an entry.

## Dependencies

- Door APIs:
  - `door_ki_lookup`
  - `door_ki_hold`
  - `door_ki_rele`
  - `door_ki_upcall_limited`
  - `door_ki_info`
- XDR routines:
  - `xdr_varg`
  - `xdr_nfsauth_res`
- Export/security structures from `<nfs/export.h>` and `<nfs/auth.h>`.
- AVL trees and kernel synchronization primitives.
- NFS zone globals:
  - `nfs_srv_getzg`
  - `nfssrv_globals_list`
  - `nfssrv_globals_rwl`

## State and Memory Ownership

- Cached server supplemental groups are owned by `auth_cache` entries and freed in `nfsauth_free_node()`.
- Returned supplemental groups from `nfsauth_cache_get()` are caller-owned copies.
- Client address buffers in `auth_cache_clnt` are heap-owned and freed in `nfsauth_free_clnt_node()`.
- The copied request address in `nfsauth_cache_get()` is freed on all normal paths.
- Refresh queue nodes hold export references with `exi_hold()` and release them with `exi_rele()`.

## Risks and Edge Cases

- Door absence returns `NFSAUTH_DROP` after retries so clients retransmit rather than receiving a hard denial.
- The refresh thread intentionally lets stale data serve foreground requests while refreshing asynchronously.
- Cache comparator includes flavor, uid, gid, group count, and group data. The group `memcmp()` length is the group count, not `group_count * sizeof (gid_t)`; this should be checked carefully because it may compare only part of the supplemental group array.
- `refreshq_dead_entries` exists in `nfsauth_globals_t` but is not used in this file.
- Reclaim uses try-locking to avoid blocking under memory pressure, so reclaim may fail partially and increments failure counters.
- Invalidated stale/refreshing entries are removed from trees but freed later by refresh/queue handling.

## Testing Notes

Useful coverage should include:

- Fast-path RO/RW access with no lists.
- AUTH_NONE fallback and `NFSAUTH_MAPNONE`.
- Wrong-security retry behavior.
- Root anonymous mapping.
- New cache entry retrieval, cache hit, stale async refresh, and trim reclaim.
- Mountd door missing, revoked, stale, and decode-failure cases.
- Concurrent lookup where one thread waits on `NFS_AUTH_WAITING`.
- Zone shutdown while refresh entries are queued or refreshing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_auth_xdr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_auth_xdr.c

## Purpose

This file provides XDR routines for kernel-to-mountd NFS authorization door messages. It serializes the versioned authorization request and the authorization response used by `nfs_auth.c`.

## Main Responsibilities

- `xdr_varg()`
  - Serializes a versioned argument wrapper.
  - Supports `V_PROTO`.
  - Marks unsupported versions as `V_ERROR` and fails.
- `xdr_nfsauth_arg()`
  - Serializes an authorization request:
    - command
    - client network object
    - netid
    - export path
    - requested security flavor
    - client uid
    - client gid
    - client supplemental groups
- `xdr_nfsauth_res()`
  - Serializes an authorization response:
    - daemon status
    - authorization permission bits
    - mapped server uid
    - mapped server gid
    - mapped server supplemental groups

## Dependencies

- Includes:
  - `<nfs/auth.h>`
  - `<rpc/auth_sys.h>`
- Uses standard XDR helpers:
  - `xdr_u_int`
  - `xdr_netobj`
  - `xdr_string`
  - `xdr_int`
  - `xdr_uid_t`
  - `xdr_gid_t`
  - `xdr_array`

## State and Memory Ownership

This file maintains no state. Supplemental group arrays are encoded/decoded through `xdr_array()` with `NGROUPS_UMAX` as the maximum count. On decode, XDR owns allocation semantics until callers free with `xdr_free()` or copy the data.

## Risks and Edge Cases

- `xdr_varg()` intentionally fails unknown versions and mutates `vap->vers` to `V_ERROR`.
- `req_netid` has an unbounded `~0` XDR string limit, while `req_path` is capped at `A_MAXPATH`.
- Supplemental groups are capped at `NGROUPS_UMAX`, matching auth_sys group constraints.
- The response decoder must be paired with `xdr_free(xdr_nfsauth_res, ...)` after decoded group arrays are copied or discarded.

## Integration Notes

`nfs_auth.c` uses these routines to:

1. Compute request size with `xdr_sizeof(xdr_varg, &varg)`.
2. Encode a `varg_t` into a door request buffer.
3. Decode `nfsauth_res_t` from mountd’s door response.
4. Copy mapped identity/group data out of the decoded response before freeing XDR-owned memory.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_auth_xdr.c -->