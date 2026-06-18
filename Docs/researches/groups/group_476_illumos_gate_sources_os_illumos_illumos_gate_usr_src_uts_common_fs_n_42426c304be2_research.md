# Group Research: group_476_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_42426c304be2

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_acl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_acl.c

## Summary
Implements illumos NFSv4 ACL conversion, validation, comparison, cache maintenance, and idmapping safety rules. It bridges three ACL representations: POSIX draft `aclent_t`, illumos/ZFS-style `ace_t`, and wire-level `nfsace4`.

## Main Responsibilities
- Initializes kmem caches for temporary ACE aggregation structures.
- Frees `vsecattr_t` payloads containing `aclent_t`, `ace_t`, or `nfsace4` entries.
- Converts POSIX draft ACL arrays to NFSv4 ACE arrays via the NFSv4 ACL mapping draft.
- Converts NFSv4 ACE arrays back to regular/default POSIX draft ACLs when the ACE pattern is representable.
- Converts between illumos `ace_t` and `nfsace4` with owner/group string idmapping.
- Maintains the per-rnode cached NFSv4 ACL copy.
- Prevents silent mapping of non-`nobody` ACL principals to `UID_NOBODY`/`GID_NOBODY`.

## Key APIs
- `nfs4_acl_init()`.
- `vs_aent_to_ace4()` and `vs_ace4_to_aent()`.
- `vs_acet_to_ace4()` and `vs_ace4_to_acet()`.
- `vs_aent_destroy()`, `vs_ace4_destroy()`, `vs_acet_destroy()`.
- `ln_ace4_cmp()`.
- `nfs4_acl_fill_cache()` and `nfs4_acl_free_cache()`.

## Important Behavior
`ln_aent_to_ace4()` performs POSIX draft ACL to NFSv4 conversion. It preprocesses ACLs to detect sorting needs, count named users/groups, and find exactly one `CLASS_OBJ` mask when named entries require it. It emits ALLOW/DENY pairs, injects mask-emulation DENY ACEs for named users/groups and `GROUP_OBJ`, places group DENY entries after the group ALLOW sequence, and maps `USER_OBJ`, `GROUP_OBJ`, and `OTHER_OBJ` to `OWNER@`, `GROUP@`, and `EVERYONE@`.

`mode_to_ace4_access()` and `access_mask_set()` decide which NFSv4-only bits are produced for allow/deny entries. Tunable static masks split behavior between client/server produce and consume paths, especially for `ACE4_SYNCHRONIZE`, `ACE4_WRITE_OWNER`, `ACE4_DELETE`, named attributes, and write attributes.

The reverse path, `ln_ace4_to_aent()`, intentionally accepts only a constrained, POSIX-mappable ACE ordering. It rejects unsupported ACE types, illegal flags, invalid masks, partial write bit sets, unsupported inheritance patterns, out-of-order entities, duplicate ALLOW entries, unmatched ALLOW/DENY complements, and inconsistent ACL mask emulation. It aggregates named users and groups in AVL trees before producing regular and default ACL lists.

`vs_acet_to_ace4()` and `vs_ace4_to_acet()` are less restrictive than the POSIX draft mapping path. They translate individual `ace_t` entries to/from NFSv4 ACEs, preserving supported NFSv4 ACE flags and access-mask bits and mapping special principals to local owner/group/everyone flags.

`nfs4_acl_fill_cache()` deep-copies NFSv4 ACE arrays into `rnode4_t.r_secattr`. If counts match, it reuses the existing ACE array but frees and replaces each embedded `who` string. If only the ACL count is being cached, it drops any stale full ACL payload.

## State and Lifetime
`nfsace4.who.utf8string_val` strings are separately allocated and must be freed per entry. The conversion routines often copy `nfsace4` structs by value, then rely on ownership transfer of embedded `who` pointers. Error paths explicitly walk partially built arrays to free embedded strings.

`ace4_list_t` is cache-allocated and contains constructed AVL trees for named user/group aggregation. `ace4_list_free()` destroys only tree nodes and returns the container to the cache; the AVL tree headers themselves are initialized/destroyed by the cache constructor/destructor.

The rnode ACL cache is protected by `r_statelock`. Cached ACL payloads are NFSv4 ACEs only; default ACL pointer fields are not populated for this cache.

## Dependencies
Depends on illumos ACL, AVL, kmem, UTF-8, and NFS idmapping helpers: `nfs_idmap_uid_str()`, `nfs_idmap_gid_str()`, `nfs_idmap_str_uid()`, `nfs_idmap_str_gid()`, `utf8_copy()`, `str_to_utf8()`, `utf8_compare()`, and `utf8_to_str()`.

## Risks
The ACL mapping is deliberately lossy and accepts only ACE layouts that can be represented as POSIX draft ACLs. Callers must be prepared for `ENOTSUP` on valid NFSv4 ACLs outside that subset.

Client-side setters reject `UID_UNKNOWN`/`GID_UNKNOWN` in outgoing ACLs to avoid read-modify-write cycles preserving unmappable entries as real principals. Server-side idmap failures can become `NFS4ERR_BADOWNER`.

`remap_id()` assigns `GID_UNKNOWN` after the user branch without an `else`, so a user remap is overwritten to `GID_UNKNOWN`. That appears intentional only if `UID_UNKNOWN` and `GID_UNKNOWN` are identical; otherwise it is a correctness hazard.

`acet_mask_to_ace4_mask()` checks `ACE4_READ_NAMED_ATTRS` against an `ace_t` mask where the surrounding code otherwise uses `ACE_*` constants. If those constants differ, read-named-attribute permission may fail to translate correctly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_attr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_attr.c

## Summary
Provides NFSv4 attribute translation support for the illumos client. It maps local `vattr_t`/`vsecattr_t` fields into encoded NFSv4 `fattr4` blobs for SETATTR, CREATE, OPEN, VERIFY, and NVERIFY operations, and defines the central NFSv4 attribute mapping table.

## Main Responsibilities
- Converts client-side set/verify attributes into XDR-encoded `fattr4` data.
- Maps local `vattr_t.va_mask` bits to NFSv4 attribute bitmaps.
- Special-cases settable atime/mtime attributes through `settime4`.
- Converts UID/GID numeric ids to NFSv4 owner/owner_group strings.
- Encodes ACL attributes supplied via `vsecattr_t`.
- Frees encoded `fattr4` payloads safely.
- Defines `nfs4_ntov_map[]`, the per-attribute mapping metadata used by attribute code.

## Key APIs
- `vattr_to_fattr4()`.
- `nfs4_fattr4_free()`.
- `nfs4_vmask_to_nmask()`.
- `nfs4_vmask_to_nmask_set()`.
- Global `nfs4_ntov_map[]` and `nfs4_ntov_map_size`.
- Global `nf4_to_vt[]`.

## Important Behavior
`vattr_to_fattr4()` selects a conversion function based on operation type. SETATTR, CREATE, and OPEN use set semantics and convert `AT_ATIME`/`AT_MTIME` to `FATTR4_TIME_ACCESS_SET`/`FATTR4_TIME_MODIFY_SET`; verify/nverify use normal read attribute semantics and convert time fields to `FATTR4_TIME_ACCESS`, `FATTR4_TIME_MODIFY`, or `FATTR4_TIME_METADATA`.

The output attribute mask is intersected with the server-supported bitmap before encoding. For verify/nverify, the code also masks out `FATTR4_CHANGE_MASK` because the local verify encoder cannot generate a `change` argument even though `nfs4_vmask_to_nmask()` adds it for ctime/mtime requests.

XDR buffer sizing is computed before encoding. Fixed-size attributes use `nfs4_ntov_map[i].xdr_size`. Variable-size owner/group strings and ACLs are manually sized with XDR length words plus rounded UTF-8 string payloads. For server-time atime/mtime SETATTR operations, the XDR size is reduced because no client timestamp is encoded.

ACL encoding is selected by the `FATTR4_ACL_MASK` table entry, whose local `vbit` is zero. The code therefore explicitly checks both `vbit` and `fbit` so ACLs are not skipped just because no `vattr_t` bit represents them.

`nfs4_fattr4_free()` clears both mask and payload pointers. It is written to tolerate repeated cleanup on partially encoded readdir entries whose attribute payload may already have been freed.

## Mapping Table
`nfs4_ntov_map[]` describes every NFSv4 attribute known to this client, including its bitmap bit, local `vattr_t` bit if any, whether it is VFS-stat-like, whether it is mandatory, numeric FATTR4 id, static XDR size, XDR function, server getter placeholder, and printable name.

The table includes mandatory protocol attributes, optional ACL and filesystem attributes, quota/space attributes, owner/group strings, raw device data, access/modify/metadata times, mounted-on fileid, and a local extension entry for `FATTR4_SUPPATTR_EXCLCREAT_MASK_LOCAL`.

## State and Lifetime
`vattr_to_fattr4()` allocates a temporary array of `union nfs4_attr_u` sized to `nfs4_ntov_map_size`, then allocates the final XDR buffer only if at least one attribute is going out. Owner and owner_group UTF-8 buffers returned by idmapping are freed after encoding. If encoding or idmapping fails, `nfs4_fattr4_free()` releases the partially constructed output.

## Dependencies
Relies on NFSv4 XDR routines stored in `nfs4_ntov_map[]`, `nfs4_time_vton()`, `nfs_idmap_uid_str()`, `nfs_idmap_gid_str()`, kmem allocation, and local NFS attribute mask constants.

## Risks
The attribute order and table index relationship are important: `amap[]` stores `nfs4_ntov_map[i].nval` and later indexes `nfs4_ntov_map[amap[i]]`. This assumes FATTR4 numeric IDs correspond to table indexes for all emitted attributes.

Manual XDR sizing for ACLs must stay in sync with `xdr_fattr4_acl()`. Any change to `nfsace4` wire encoding or string handling needs matching size accounting.

Verify/nverify support is incomplete for attributes that do not map directly to `vattr_t`; the file documents this as a known limitation for mandatory-only servers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_callback.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_callback.c

## Summary
Implements the NFSv4 client callback service and delegation lifecycle machinery. It receives server callbacks, serves CB_GETATTR/CB_RECALL/CB_NULL, registers per-server callback program numbers, manages callback state per zone, and returns, discards, reopens, or abandons delegations.

## Main Responsibilities
- Dispatches NFSv4 callback RPC procedures and compounds.
- Handles `CB_GETATTR` for delegated files, returning change and size attributes.
- Handles `CB_RECALL` by asynchronously returning delegations.
- Tracks callback ports and callback RPC program numbers used in SETCLIENTID.
- Provides `nfs4_svc()` for userland callback service setup and delegation query.
- Initializes and tears down per-zone callback globals and kstats.
- Cleans all delegations during zone shutdown/finalization.
- Performs synchronous and asynchronous `DELEGRETURN`.
- Reopens delegation-created open streams before returning recalled delegations.
- Accepts newly granted read/write delegations and records them on server delegation lists.
- Synchronizes ordinary file operations with active recall/return work.
- Maintains a recovery-time dlist of delegations that must be returned or discarded later.

## Key APIs
- Callback service: `nfs4_callback_init()`, `nfs4_callback_fini()`, `nfs4_svc()`, `nfs4_cb_args()`, `nfs4callback_destroy()`.
- Callback globals: `nfs4_get_callback_globals()`.
- Delegation return: `nfs4delegreturn()`, `nfs4delegreturn_async()`, `nfs4_do_delegreturn()`, `nfs4_resend_delegreturn()`, `nfs4delegreturn_cleanup()`.
- Delegation bulk/discard paths: `nfs4_delegreturn_all()`, `nfs4_deleg_discard()`, `nfs4delegabandon()`.
- Delegation accept/recovery sync: `nfs4_delegation_accept()`, `wait_for_recall()`, `nfs4_end_op_recall()`, `nfs4_dlistclean()`.

## Important Behavior
`cb_dispatch()` decodes callback RPC arguments, invokes `cb_null()` or `cb_compound()`, sends the reply, frees per-op response storage, and frees decoded arguments.

`cb_compound()` copies the request tag into the response, rejects unsupported callback minor versions, allocates one response slot per argument op, executes operations in order, and truncates the response array when an op returns an error. It handles `OP_CB_GETATTR`, `OP_CB_RECALL`, and illegal/default callback ops.

`cb_getattr()` maps the request RPC program to an `nfs4_server_t`, validates the server program, finds the delegated rnode by filehandle, and replies only with supported `FATTR4_CHANGE` and `FATTR4_SIZE`. For mmapped write delegations it increments the delegation change value before returning it; if the file is not dirty, it can reset the change attribute to the grant-time value. It reads size atomically to avoid locking deadlocks.

`cb_recall()` validates both delegation stateid and filehandle, then starts `nfs4delegreturn_async()` with recall/reopen flags. The async thread owns the vnode hold passed from the callback path and releases it after return processing.

`nfs4_cb_args()` associates an NFS server with an available callback program number and a previously registered transport address. Program numbers are selected from a per-zone `nfs4prog2server[]` array and reused across SETCLIENTID by first destroying the old mapping.

`nfs4_svc()` is the kernel entry point used by the mount-side helper. It supports `NFS4_DQUERY`, callback port registration, and kernel RPC transport creation through `svc_tli_kcreate()`.

## Delegation Lifecycle
`nfs4_delegation_accept()` records read/write delegations granted by OPEN. It stores stateid, permissions, space limit, grant-time change attribute, credential, and server-list membership under the required server/rnode lock ordering. It may immediately schedule a return when the server grants a recalled delegation, when policy is `IMMEDIATE`, when grant attributes are incomplete, or when an existing delegation becomes tainted.

`nfs4delegreturn_impl()` is the main return engine. It can discard without over-the-wire RPC, defer if the caller already holds start-op state, push dirty pages, take `r_deleg_recall_lock` in writer mode, optionally reopen delegation open streams, and either discard or call `nfs4_do_delegreturn()`.

`nfs4_do_delegreturn()` wraps `nfs4_start_fop()`/`nfs4_end_op()`, handles recov-only cases by creating lost request state, sends PUTFH/GETATTR/DELEGRETURN via `nfs4delegreturn_otw()`, updates the attribute cache from GETATTR on success, and starts recovery when retryable or state-related errors require it.

`deleg_reopen()` finds open streams that were created under the delegation and reopens them using `CLAIM_DELEGATE_CUR` or `CLAIM_NULL` depending on whether the delegation is being discarded. It handles EAGAIN retry, errors that already started recovery, and recovery-start decisions for other protocol failures.

`nfs4delegreturn_thread()` services async recall/abandon work. It holds `r_rwlock` in reader mode to stop non-mmap mutation during recall, flushes or invalidates pages for truncate/write/failed-recovery cases, removes recursive `NFS4_DR_DID_OP`, invokes `nfs4delegreturn_impl()`, and drops the vnode reference.

## State and Synchronization
Per-zone `nfs4_callback_globals` owns the callback program-to-server array, callback port list, delegation cleanup dlist, locks, and kstats. Zone shutdown cleans the dlist and discards delegations; finalization repeats discard, removes zone servers from the global list, frees callback ports, destroys lists/locks, and frees globals.

Delegation list membership is anchored in `nfs4_server_t.s_deleg_list` and protected by `s_lock`; per-rnode delegation fields use `r_statev4_lock`, while page/dirty flags use `r_statelock`. The code documents and follows lock ordering around `s_lock`, `r_statev4_lock`, `r_deleg_recall_lock`, `mi_recovlock`, and `r_rwlock`.

The dlist path marks `r_deleg_return_pending`, holds the vnode, stores return flags in `struct nfs4_dnode`, and later drains the list through `nfs4delegreturn_impl()`.

## Dependencies
This file depends on illumos kernel RPC service plumbing, zone-specific data, kstats, NFSv4 client recovery, rnode/open-stream state, page flushing/invalidation, XDR-generated callback structures, and server-list reference management.

## Risks
The callback-to-server mapping trusts the RPC program number after range checks; stale or confused program mappings generally fail with `BADHANDLE`/`BAD_STATEID`, but all delegation work depends on correct registration and cleanup.

Delegation return spans RPC, recovery, vnode lifetime, page flushing, open-stream reopening, and multiple lock domains. The comments repeatedly note deadlock risks around `nfs4_start_fop()`, `VOP_PUTPAGE()`, and recall locks.

`nfs4_callback_fini()` is empty even though `nfs4_callback_init()` allocates the service callout table. This may rely on module lifetime semantics, but it is a visible lifetime asymmetry.

The async paths depend on callers taking `VN_HOLD()` before thread creation. Any new caller of `nfs4delegreturn_async()` must preserve that contract.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_callback.c -->