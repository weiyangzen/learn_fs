# Group Research: group_479_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_91b6937183a1

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_attr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_attr.c

Implements the server-side NFSv4 attribute conversion table. It maps NFSv4 `fattr4` bits to illumos vnode, VFS, export, idmap, ACL, referral, and pathconf data for GETATTR, SETATTR, VERIFY/NVERIFY, READDIR attribute support, and supported-attribute discovery.

Key elements:
- Global supported-attribute setup: `rfs4_attr_init()` initializes compound-state context, calls every `nfs4_ntov_map[]` handler in `NFS4ATTR_SUPPORTED` mode, builds `rfs4_supported_attrs`, and derives `supported_attrs[]` variants for NFSv4.0, v4.1, and v4.2.
- Attribute dispatch: `rfs4_ntov_init()` installs handlers for attribute indexes 0 through 56, covering mandatory attributes, recommended attributes, `mounted_on_fileid`, and `suppattr_exclcreat`.
- ACL handling: `rfs4_fattr4_acl()` detects filesystem ACL support with `_PC_ACL_ENABLED`, falls back to ACLENT behavior where needed, converts native ACE/ACLENT forms to NFSv4 ACEs for GET/VERIFY, and converts NFSv4 ACEs back for SETATTR under a vnode write lock.
- Identity attributes: `rfs4_fattr4_owner()` and `rfs4_fattr4_owner_group()` convert uid/gid to and from NFSv4 owner strings with `nfs_idmap_*` helpers, map nfsmapid service failures to NFSv4 errors, and free allocated UTF-8 strings in FREEIT.
- Filesystem/pathconf attributes are sourced from `statvfs64`, `VOP_PATHCONF()`, request transport size, and `vattr_t`.
- Referral attributes: `rfs4_fattr4_fs_locations()` calls `fetch_referral()`, copies returned `fs_locations4`, updates the referral kstat, and `rfs4_free_fs_locations4()` recursively frees pathname/location allocation.
- Mounted-on fileid: `rfs4_get_mntdfileid()` untraverses VROOT or zone-root vnodes to report the mounted-on stub nodeid when required.
- Settable attributes: size, mode, owner, owner_group, ACL, access time set, and modify time set populate `vattr_t` or call security-attribute VOPs. Mode SETIT strips setuid/setgid for regular files on `EX_NOSUID` exports.
- Unsupported attributes deliberately return `ENOTSUP`: archive, hidden, mimetype, quota attributes, system, backup time, create time, and several non-implemented optional fields.

Dependencies:
- NFSv4 protocol definitions and maps: `nfs4_ntov_map`, `bitmap4`, `union nfs4_attr_u`, `FATTR4_*_MASK`, `NFS4ATTR_*`.
- Vnode and VFS interfaces: `VOP_GETATTR`, `VOP_SETSECATTR`, `VOP_GETSECATTR`, `VOP_PATHCONF`, `VOP_RWLOCK`, `VOP_RWUNLOCK`.
- NFS server helpers: `rfs4_vop_getattr()`, `makefh4()`, `fetch_referral()`, `nfs_visible_change()`, `rfs4_tsize()`.
- ACL/idmap helpers: `vs_acet_to_ace4`, `vs_aent_to_ace4`, `vs_ace4_to_acet`, `vs_ace4_to_aent`, `nfs_idmap_*`.
- Export and namespace state: `compound_state`, `exportinfo`, `exi_volatile_dev`, referrals, named-attribute filehandle flags, zone root traversal.

Research notes:
- The file is table-driven: each attribute handler accepts the same command enum and must implement support probing, get, set, verify, and free behavior consistently.
- Many READDIR-compatible handlers use the `rdattr_error` convention: return `-1` when prior attribute collection failed and the caller may encode `rdattr_error`.
- `fs_locations` ownership transfers are subtle: nested allocations are freed later by FREEIT.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_deleg.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_deleg.c

Implements NFSv4 server delegation policy, callback-channel management, CB_RECALL and CB_GETATTR callbacks, v4.1 back-channel slot use, delegation grant/recall/revoke/return lifecycle, and cross-version delegation conflict checks.

Key elements:
- Delegation policy controls protect or expose `nfs4_deleg_policy`; `rfs4_disable_delegation()` and `rfs4_enable_delegation()` maintain a temporary disable counter.
- v4.0 callback path: `rfs4_client_setcb()`, `rfs4_deleg_cb_check()`, `rfs4_do_cb_null()`, `rfs4_cbinfo_hold()`, `rfs4_cbinfo_rele()`, `rfs4_cb_getch()`, and `rfs4_cb_freech()` store, validate, reference, cache, and retry callback RPC client state.
- General callback execution: `rfs4_do_callback()` sends v4.0 `CB_COMPOUND` calls and retries if a failed call races with newly confirmed callback data.
- v4.1 back-channel support manages session back-channel slots and cached callback clients through `svc_slot_*()` and `rfs4x_cb_*()` helpers.
- CB_RECALL: `rfs4_do_cb_recall()` sends v4.0 recall; `rfs4x_do_cb_recall()` sends v4.1 `CB_SEQUENCE + CB_RECALL`, retries after lease delay for transport/delay errors, and revokes on persistent failures.
- CB_GETATTR: `rfs4_find_write_deleg*()` finds held write delegations; `rfs4_do_cb_getattr()` and `rfs4x_do_cb_getattr()` ask delegation holders for authoritative `FATTR4_CHANGE` and `FATTR4_SIZE`.
- Recall threading: `rfs4_recall_file()`, `do_recall_file()`, and `do_recall()` dispatch recall work without holding file/state locks across network callbacks.
- Grant policy: `rfs4_grant_delegation()` enforces server policy, client preferences, callback availability, lock-manager activity, remove/rename hold-off, recall delay state, and CLAIM_PREVIOUS behavior.
- Delegation state installation: `rfs4_deleg_state()` creates/fetches delegation state, checks local open/map conflicts, installs vnode event monitors, upgrades vnode open counts, links the delegation to the file list, and updates counters.
- Return/revocation: `rfs4_return_deleg()` removes list state, cleans v4.1 recallable-state/session slot references, uninstalls monitors for the last delegation, invalidates or marks state revoked, and increments the client revoked-delegation count for v4.1 SEQUENCE status.
- Cross-protocol checks: `rfs4_check_delegated_byfp()` and `rfs4_check_delegated()` recall delegations for v2/v3 or local conflicts and hold off new grants during remove/rename.

Dependencies:
- NFSv4 state model: `rfs4_client_t`, `rfs4_session_t`, `rfs4_state_t`, `rfs4_file_t`, `rfs4_deleg_state_t`, `rfs4_dbe_*`.
- RPC/back-channel APIs: `CLIENT`, `clnt_call`, `clnt_tli_kcreate`, `CLNT_CONTROL`, `xdr_CB_COMPOUND4args_srv`, `xdr_CB_COMPOUND4res`.
- Session/slot helpers: `SN_CB_CHAN_EST`, `slot_alloc`, `slot_free`, `slot_incr_seq`, `rfs4x_findsession_by_*`.
- Vnode/file monitoring: `fem_install`, `fem_uninstall`, `vn_open_upgrade`, `vn_open_downgrade`, `vn_is_opened`, `vn_has_other_opens`, `vn_is_mapped`.
- Lock manager and transport helpers: `lm_vp_active`, `lookupname`, `inet_pton`.

Research notes:
- v4.0 and v4.1 callback paths are intentionally separate: v4.0 uses client-supplied callback addresses, while v4.1 uses the session back-channel and slot sequencing.
- `rfs4_return_deleg()` differs by protocol version: v4.0 closes/reaps state, while v4.1 keeps revoked state until FREE_STATEID or client cleanup.
- Delegation grants depend on both protocol share state and local vnode open/map state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_deleg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_ns.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_ns.c

Implements the NFSv4 server pseudo-filesystem namespace. It builds, merges, tears down, and queries pseudo export nodes and visible directory lists so NFSv4 clients can traverse unexported path components to reach real exported descendants.

Key elements:
- `vop_fid_pseudo()` calls `VOP_FID()` but substitutes `va_nodeid` when remote NFS fids are unsupported or too large.
- `nfs4_vget_pseudo()` resolves a fid against an export's visible list or export root vnode.
- `pseudo_exportfs()` allocates an `exportinfo`, fills fsid/fid/vnode/template filehandle, marks `EX_PSEUDO`, copies propagated security flavor information, initializes auth cache AVL tables, links the export, and assigns an export id.
- Tree primitives manage `treenode_t` parent/child/sibling links and attach visible entries/exportinfo objects.
- `more_visible()` merges a newly constructed visible path/tree into an existing root or pseudo export, increments `vis_count`, transfers exportinfo pointers when safe, adds new branches, and updates change timestamps.
- `less_visible()` decrements one visible entry's reference count and removes/frees it at zero.
- `treeclimb_export()` walks from a real export up toward the zone root, crossing mountpoints with `untraverse()`, building visible entries/tree nodes, creating pseudo exports for unexported filesystem roots, and merging into existing exports when found.
- `treeclimb_unexport()` clears the unshared export, releases unused pseudo exports and visible entries, deletes non-exported leaf nodes, and updates change timestamps.
- Query helpers: `get_root_export()`, `has_visible()`, `nfs_visible()`, `nfs_exported()`, `nfs_visible_inode()`, `nfs_visible_change()`, and `tree_update_change()` answer visibility/export/change questions.

Dependencies:
- NFS export structures: `nfs_export_t`, `exportinfo_t`, `exp_visible_t`, `treenode_t`, `export_link()`, `export_unlink()`, `exi_rele()`, `checkexport4()`.
- Vnode/VFS APIs: `VOP_FID`, `VOP_GETATTR`, `VOP_LOOKUP`, `VN_HOLD`, `VN_RELE`, `VN_CMP`, `VROOT`, `vfs_lock_wait`.
- Export security helpers: `srv_secinfo_exp2pseu()`, `srv_secinfo_list_free()`.
- Zone/root helpers: `VN_IS_CURZONEROOT`, `EXI_TO_ZONEROOTVP`, current zone id checks.
- Namespace comparison macros: `EQFID`, `EQFSID`, `PSEUDO`, `TREE_ROOT`, `TREE_EXPORTED`, `vis2exi`.

Research notes:
- The pseudo namespace is represented twice: linked `exp_visible` lists attached to exportinfo roots and a tree of `treenode_t` objects.
- `vis_count` is the key lifetime mechanism for shared path components.
- Several query paths compare fid/fsid after vnode comparison because `VN_CMP()` can miss LOFS-equivalent nodes.
- Change attributes for pseudo namespace entries are maintained independently and consumed by attribute and READDIR code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_ns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_readdir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_readdir.c

Implements the NFSv4 server READDIR operation, including directory scanning, pseudo-namespace filtering, per-entry vnode lookup, referral handling, attribute encoding, buffer sizing, and STREAMS mblk response construction.

Key elements:
- Defines minimum encoded entry/reply/buffer sizes for legal READDIR responses and `VOP_READDIR()` buffers.
- `nfs4_readdir_getvp()` looks up a child name, detects referrals, traverses mounted filesystems, checks exports at mount roots, runs auth for crossed exports, and returns an entry vnode, mounted-on stub vnode, or new exportinfo.
- `rfs4_get_pc_encode()` precomputes max file size, max link count, and max name length.
- `rfs4_get_sb_encode()` precomputes statvfs-derived space and file counters.
- `rfs4_op_readdir()` validates current filehandle, directory type, `maxcount`, write-only attribute requests, read access, and cookie verifier.
- It filters pseudo-namespace entries with `nfs_visible_inode()`, converts names via `nfscmd_convname()`, looks up child vnodes only when attributes are requested, and preserves `RDATTR_ERROR` semantics.
- Referral entries are restricted to RFC 7530 absent-filesystem attributes and can return `NFS4ERR_MOVED` through `rdattr_error`.
- Attribute encoding is inlined for performance and covers core attributes, file identity, filesystem counters, referral locations, mode/link/time fields, owner/group idmap strings, and mounted-on fileid.
- Cleanup releases the READDIR data buffer, any held child vnode, owner/group UTF-8 strings, and the response mblk on error.

Dependencies:
- Vnode/VFS APIs: `VOP_LOOKUP`, `VOP_READDIR`, `VOP_ACCESS`, `VOP_GETATTR`, `VOP_FID`, `VOP_PATHCONF`, `VFS_STATVFS`, `VOP_RWLOCK`, `VOP_RWUNLOCK`, `traverse()`.
- NFS export/security helpers: `checkexport4()`, `call_checkauth4()`, `is_exported_sec()`, `client_is_downrev()`, `nfs_visible_inode()`, `fetch_referral()`, `makefh4()`.
- Encoding helpers: `IXDR_PUT_*`, `xdr_inline_encode_nfs_fh4()`, `xdr_fattr4_fs_locations()`, NFSv4 attr bitmasks.
- Name/id conversion: `nfscmd_convname()`, `nfs_idmap_uid_str()`, `nfs_idmap_gid_str()`.
- Kernel allocation and STREAMS: `allocb`, `allocb_wait`, `freeb`, `mblk_t`, `kmem_alloc`, `kmem_free`.

Research notes:
- READDIR has a separate fast attribute encoder instead of calling the generic attribute conversion table from `nfs4_srv_attr.c`; new attribute support may need changes in both places.
- The redzone approach assumes bounded chunks of attribute encoding between checks.
- Pseudo namespace filtering uses inode numbers before lookup, then carries the matching visible entry into change/export behavior.
- The crossed-filesystem statvfs/pathconf refresh path and `vfs_different` handling are worth extra review before modifying per-entry VFS attribute logic.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_readdir.c -->