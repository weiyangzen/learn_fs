# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv.c lines 1-10241

## Scope

This chunk covers the first 10,241 lines of `nfs4_srv.c`, the bulk of the illumos in-kernel NFSv4 server operation implementation. It includes server/zone initialization, the NFSv4/v4.1/v4.2 operation dispatch table, compound request execution, filehandle navigation, SECINFO, attribute conversion, namespace mutations, read/write I/O, open/share/delegation state, clientid setup, close, byte-range locking, share locks, RDMA read reply setup, and the start of referral/reparse helpers. The file continues after this chunk with referral path construction and failover helpers.

## APIs And Entry Points

- Server lifecycle: `nfs4_get_srv()`, `rfs4_srv_zone_init()`, `rfs4_srv_zone_fini()`, `rfs4_srvrinit()`, `rfs4_srvrfini()`, `rfs4_do_server_start()`.
- Compound state lifecycle: `rfs4_init_compound_state()`, `rfs4_fini_compound_state()`.
- Grace/server-instance management: `rfs4_grace_start()`, `rfs4_servinst_grace_new()`, `rfs4_servinst_in_grace()`, `rfs4_clnt_in_grace()`, `rfs4_grace_reset_all()`, `rfs4_grace_start_new()`, `rfs4_servinst_create()`, `rfs4_servinst_destroy_all()`, `rfs4_servinst_assign()`, `rfs4_servinst()`.
- NFSv4 operation handlers in this chunk: ACCESS, CLOSE, COMMIT, CREATE, DELEGPURGE, DELEGRETURN, GETATTR, GETFH, LINK, LOCK, LOCKT, LOCKU, LOOKUP, LOOKUPP, OPENATTR, NVERIFY, OPEN, OPEN_CONFIRM, OPEN_DOWNGRADE, PUTFH, PUTPUBFH, PUTROOTFH, READ, READDIR free path, READLINK, RELEASE_LOCKOWNER, REMOVE, RENAME, RENEW, RESTOREFH, SAVEFH, SECINFO, SETATTR, SETCLIENTID, SETCLIENTID_CONFIRM, VERIFY, WRITE.
- Main dispatcher/free/idempotency APIs: `rfs4_compound()`, `rfs4_compound_free()`, `rfs4_idempotent_req()`.
- Lock/share support exported to state teardown: `rfs4_client_sysid()`, `rfs4_release_share_lock_state()`, `rfs4_share()`, `rfs4_unshare()`.

## Dispatch And Control Flow

`rfsv4disptab` binds NFS op numbers to handlers, free callbacks, and flags such as `OP_IDEMPOTENT` and `OP_CLEAR_STATEID`. Unsupported v4.1/v4.2 operations route to `rfs4_op_notsup()`. `rfs4_opnum_in_range()` enforces minor-version opcode limits.

`rfs4_compound()` copies the request tag, obtains RPC credentials/security flavor, allocates result slots, records request metadata in `compound_state_t`, and runs under `nfs_export_t.exported_lock`. It starts new grace periods on the first compound, dispatches ops in order, stops on first error, compacts the result array, and clears current stateid when required.

## State, Security, And Filehandles

Zone/server init allocates `nfs4_srv_t`, write verifier, locks, delegation policy, FEM delegation monitors, lock-test sysid, VSD key, state DBs, duplicate-request cache, stable-storage state, and server-instance grace metadata.

`PUTROOTFH`, `PUTPUBFH`, and `PUTFH` establish `cs->vp`, `cs->fh`, `cs->exi`, and credentials through export lookup, filehandle conversion, and `call_checkauth4()`. `do_rfs4_op_lookup()` handles dot-dot, mount traversal, LOFS boundaries, pseudo-export visibility, export transitions, label checks, credential remapping, and filehandle creation.

`SECINFO` computes allowed security flavors for a child vnode, including pseudo exports, mounted-on fallback, limited visibility, and RPCSEC_GSS OID/QOP/service construction. Session-mode SECINFO consumes the current filehandle on success.

## Attributes, I/O, And Namespace Ops

Attribute conversion is centered on `nfs4_ntov_map`, `bitmap4_to_attrmask()`, `bitmap4_get_sysattrs()`, `do_rfs4_op_getattr()`, `do_rfs4_set_attrs()`, `rfs4_verify_attr()`, and `do_rfs4_op_setattr()`. GETATTR supports referral detection and write-delegation CHANGE/SIZE callbacks.

CREATE handles non-regular objects; OPEN handles regular file creation. LINK, REMOVE, and RENAME compute change_info, recall delegations, check NBMAND conflicts, call VOPs, fsync metadata, and close state when link count reaches zero. OPENATTR opens named-attribute dirs. READLINK supports both real symlinks and referral symlink emulation for downrev clients.

READ/WRITE validate stateids, access, object type, mandatory locks, read-only exports, and NBMAND conflicts. READ supports RDMA write chunks, loaned zero-copy buffers, and normal mblks. WRITE supports mblk, RDMA read chunk, and inline buffers, applies sync modes, and temporarily switches thread credentials for quota behavior.

## OPEN, Clientid, And Locking

OPEN is the core state machine: it validates clientid, lease, grace/reclaim rules, open-owner seqids, confirmation state, share modes, and claim type. Helpers handle `CLAIM_NULL`, `CLAIM_PREVIOUS`, `CLAIM_DELEGATE_CUR`, `CLAIM_DELEGATE_PREV`, and `CLAIM_FH`. `rfs4_do_open()` manages file/state lookup, share locks, delegation recall/grant, vnode open/upgrade, counters, stateid updates, and cached replies.

SETCLIENTID and SETCLIENTID_CONFIRM implement v4.0 client identity establishment, callback info updates, in-use handling, replacement of unconfirmed clients, stable-storage recording, callback checks, and reclaim eligibility.

LOCK/LOCKU/LOCKT map NFSv4 lock owners/stateids to `VOP_FRLOCK()`, maintain seqid replay semantics, enforce grace/reclaim rules, allocate client sysids, report denied owners, and update lock stateids. `rfs4_share()`/`rfs4_unshare()` map NFS share reservations to `VOP_SHRLOCK()`.

## Risks And Cross-Chunk References

- Compound execution holds `exported_lock` across potentially blocking VFS, I/O, delegation, and locking paths.
- Error exits manually manage vnodes, creds, names, mblks, XDR buffers, and state references.
- OPEN/CLOSE/LOCK replay semantics are sensitive to exact error ordering.
- Observed risk: OPEN_DOWNGRADE clears `fp->rf_share_deny` with an access mask when write access count reaches zero.
- Observed risk: RENAME target after-change getattr uses `odvp` where `ndvp` appears intended.
- Referral support crosses the chunk boundary: `vn_find_nfs_record()` begins at line 10241, while `vn_is_nfs_reparse()`, `fetch_referral()`, `build_symlink()`, `client_is_downrev()`, and `hanfsv4_failover()` are implemented after this chunk.