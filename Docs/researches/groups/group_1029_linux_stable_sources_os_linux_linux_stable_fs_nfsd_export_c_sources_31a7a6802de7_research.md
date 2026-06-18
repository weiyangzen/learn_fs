# Group Research: group_1029_linux_stable_sources_os_linux_linux_stable_fs_nfsd_export_c_sources_31a7a6802de7

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/export.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/export.c

## Summary
Implements NFSD export validation, lookup, display, and cache management. It owns two per-network-namespace SunRPC caches: `nfsd.export`, keyed by client plus path, and `nfsd.fh`, keyed by client plus fsid fragment.

## Main Responsibilities
- Parses mountd-supplied export and expkey cache records.
- Validates whether paths can be exported with `check_export()`.
- Resolves exports by path, fsid, parent walk, and NFSv4 pseudoroot.
- Enforces transport security and RPC auth flavor policy.
- Formats `/proc/fs/nfsd/exports` and `export_stats`.
- Initializes, flushes, and shuts down export caches.

## Key APIs
- `nfsd_export_wq_init()`, `nfsd_export_wq_shutdown()`.
- `nfsd_export_init()`, `nfsd_export_flush()`, `nfsd_export_shutdown()`.
- `exp_rootfh()`, `exp_pseudoroot()`.
- `rqst_exp_get_by_name()`, `rqst_exp_find()`, `rqst_exp_parent()`, `rqst_find_fsidzero_export()`.
- `check_xprtsec_policy()`, `check_security_flavor()`, `check_nfsd_access()`.

## Important Behavior
`svc_export_parse()` accepts client, path, expiry, flags, anonymous uid/gid, fsid, and optional `fsloc`, `uuid`, `secinfo`, and `xprtsec` records. Negative cache entries are supported when only expiry is present.

`check_export()` rejects unsupported inode types, non-device filesystems without fsid/UUID, filesystems without valid export operations, idmapped mounts, and subtree-check exports on filesystems that opt out.

Request lookups first try the AUTH_SYS client, then fall back to the deprecated GSS client naming path unless a secinfo-bearing export was found.

## State and Lifetime
`svc_export` and `svc_expkey` entries are SunRPC cache objects. Release is deferred through `queue_rcu_work()` on the `nfsd_export` workqueue. Export release drops path refs, auth-domain refs, NFSv4 fs locations, stats counters, UUID storage, and layout/device-map ownership.

## Risks
Authorization is split between transport policy and security flavor policy; callers that bypass `check_nfsd_access()` can skip part of the intended check. Lifetime is subtle because cache refs, path refs, auth-domain refs, layout device maps, percpu stats, and RCU-delayed freeing all interact.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/export.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/export.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/export.h

## Summary
Defines NFSD export structures, export stats, fs location metadata, security flavor metadata, and export lookup/lifecycle interfaces.

## Main Contents
- `struct nfsd4_fs_location` and `struct nfsd4_fs_locations`.
- `struct exp_flavor_info`.
- `struct export_stats`.
- `struct svc_export`.
- `struct svc_expkey`.
- Export option helpers such as `EX_ISSYNC()`, `EX_NOHIDE()`, and `EX_WGATHER()`.

## Key Interfaces
Declares export cache lifecycle, request export lookup helpers, root filehandle/pseudoroot helpers, and access-policy helpers. `exp_get()` and `exp_put()` wrap SunRPC cache reference management.

## Important Details
`svc_export` carries the auth domain, export flags, fsid, path, anonymous credentials, UUID, NFSv4 fs locations, secinfo flavors, pNFS layout/device state, transport security modes, cache owner, RCU release work, and per-export stats.

`svc_expkey` maps a client and fsid encoding to an export path and supports multiple fsid encodings through `ek_fsidtype` and `ek_fsid`.

## Risks
Consumers must treat these as cache-managed objects and use `exp_get()` / `exp_put()`. `svc_expkey.ek_fsid` is a generic storage area whose valid length depends on `key_len(ek_fsidtype)`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/export.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/filecache.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/filecache.c

## Summary
Implements the NFSD open-file cache. It caches `struct file` objects by inode pointer, credentials, network namespace, access mask, and GC policy.

## Main Responsibilities
- Allocates and opens `struct nfsd_file` objects.
- Reuses already-open files when safe.
- Supports both precise-lifetime and garbage-collected cached opens.
- Handles localio acquisition.
- Tracks writeback errors and direct-I/O alignment.
- Closes cached files on conflicting fsnotify and lease events.
- Exposes cache statistics.

## Key APIs
- `nfsd_file_cache_init()`, `nfsd_file_cache_shutdown()`.
- `nfsd_file_cache_start_net()`, `nfsd_file_cache_shutdown_net()`, `nfsd_file_cache_purge()`.
- `nfsd_file_acquire_gc()`, `nfsd_file_acquire()`, `nfsd_file_acquire_opened()`, `nfsd_file_acquire_local()`, `nfsd_file_acquire_dir()`.
- `nfsd_file_get()`, `nfsd_file_put()`, `nfsd_file_put_local()`.
- `nfsd_file_close_inode_sync()`, `nfsd_file_is_cached()`, `nfsd_file_cache_stats_show()`.

## Important Behavior
Entries live in an `rhltable` keyed by inode pointer. New entries start with `NFSD_FILE_PENDING`; other waiters block on that bit until construction succeeds or fails. GC-enabled entries retain an LRU-held reference after caller release, allowing reuse until the laundrette or shrinker evicts them.

Regular-file cache entries install an fsnotify mark for `FS_ATTRIB` and `FS_DELETE_SELF`, and a lease notifier closes cached files when leases conflict. Close paths check writeback errors and reset the NFSD write verifier when needed.

## State and Synchronization
Uses RCU, inode locks during insertion, a global `list_lru`, shrinker callbacks, a delayed laundrette worker, fsnotify marks, a lease notifier, per-net disposal lists, and percpu counters. Shutdown requires `nfsd_mutex`, cancels delayed work, purges all cached entries, drains RCU, and destroys slabs/groups/tables.

## Risks
`nf_inode` is intentionally not an owning inode reference and must only be compared. Refcounting is subtle around pending construction, LRU-held references, synchronous versus delayed disposal, localio installed pointers, and failure retries after stale opens.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/filecache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/filecache.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/filecache.h

## Summary
Declares NFSD file-cache data structures and public file-cache APIs.

## Main Contents
Defines `NFSD_FILE_GC_BATCH`, `struct nfsd_file_mark`, and `struct nfsd_file`.

## Important Details
`nfsd_file` stores rhashtable linkage, inode comparison key, backing file, credential, net namespace, flags, refcount, requested access mask, fsnotify mark, LRU/GC links, RCU head, birth time, and direct-I/O alignment values.

Flags include `NFSD_FILE_HASHED`, `NFSD_FILE_PENDING`, `NFSD_FILE_REFERENCED`, `NFSD_FILE_GC`, and `NFSD_FILE_RECENT`.

## Risks
`nf_inode` is not safe to dereference. `nfsd_file_mark` uses an NFSD-specific refcount because fsnotify’s own mark lifetime does not distinguish “destroy mark” from “drop mark reference” for shared NFSD users.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/filecache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/flexfilelayout.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/flexfilelayout.c

## Summary
Implements a minimal NFSv4.1 pNFS flex-file layout server where the metadata server is also the data server.

## Main Responsibilities
- Provides `ff_layout_ops`.
- Handles layoutget, getdeviceinfo, and layoutcommit for flex-file layouts.
- Builds device addresses from the request destination address.

## Important Behavior
`nfsd4_ff_proc_layoutget()` allocates one layout with one mirror, one data server, and one filehandle. It sets flags to avoid layoutcommit, avoid I/O through the MDS, and suppress read I/O for read/write segments. It grants a whole-file segment.

For read-only layouts it changes the advertised uid by adding one to the inode uid, preventing write permission through that credential path.

`nfsd4_ff_proc_getdeviceinfo()` advertises NFSv3 over `tcp` or `tcp6`, uses `svc_max_payload()` for read and write sizes, and formats a universal address from `rq_daddr`.

## Risks
The implementation is deliberately simple and assumes the data server address is the request destination address. Credential adjustment for read layouts is a protocol-level permission trick and depends on client interpretation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/flexfilelayout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/flexfilelayoutxdr.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/flexfilelayoutxdr.c

## Summary
Encodes NFSD pNFS flex-file layoutget and getdeviceinfo replies.

## Key APIs
- `nfsd4_ff_encode_layoutget()`.
- `nfsd4_ff_encode_getdeviceinfo()`.

## Important Behavior
Layoutget encoding emits one mirror, one data server, a deviceid, stateid, one filehandle, stringified uid/gid, layout flags, and a zero stats hint.

Deviceinfo encoding emits one netaddr and one NFSv3 version entry with advertised read/write sizes. If `gd_maxcount` is zero, it returns a zero-length result following the RFC guidance cited in the file.

## Risks
XDR lengths are computed manually and must match the encoded fields. UID/GID values are formatted against `init_user_ns`, not through normal NFSv4 idmapping.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/flexfilelayoutxdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/flexfilelayoutxdr.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/flexfilelayoutxdr.h

## Summary
Defines structures and constants used by NFSD flex-file layout XDR encoding.

## Main Contents
- Flex-file flags: `FF_FLAGS_NO_LAYOUTCOMMIT`, `FF_FLAGS_NO_IO_THRU_MDS`, `FF_FLAGS_NO_READ_IO`.
- Address sizing constants `FF_NETID_LEN` and `FF_ADDR_LEN`.
- `struct pnfs_ff_netaddr`.
- `struct pnfs_ff_device_addr`.
- `struct pnfs_ff_layout`.

## Important Details
`pnfs_ff_layout` embeds the deviceid, stateid, uid/gid, flags, stats hint, and NFS filehandle. Device addresses carry netid, universal address, NFS version/minor version, read/write sizes, and tight-coupling state.

## Risks
The fixed address buffer relies on `INET6_ADDRSTRLEN + 8` being enough for the universal address plus encoded port suffix.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/flexfilelayoutxdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/idmap.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/idmap.h

## Summary
Declares the NFSD idmapping interface for NFSv4 owner/group names and uid/gid conversion.

## Key APIs
- `nfsd_idmap_init()` and `nfsd_idmap_shutdown()` when `CONFIG_NFSD_V4` is enabled.
- `nfsd_map_name_to_uid()`.
- `nfsd_map_name_to_gid()`.
- `nfsd4_encode_user()`.
- `nfsd4_encode_group()`.

## Important Behavior
When NFSDv4 is disabled, idmap init/shutdown become no-op inline functions. Mapping and encoding declarations remain present for code compiled under other guards.

## Risks
The header only declares the interface. Correctness depends on implementation files consistently using the request namespace and NFSv4 idmapping policy.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/idmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/localio.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/localio.c

## Summary
Implements NFSD support for local NFS clients to bypass the network stack while still using NFSD filehandle validation, credential mapping, and filecache machinery.

## Main Responsibilities
- Installs `nfsd_localio_operations`.
- Opens local filehandles as `struct nfsd_file`.
- Provides a hidden localio RPC version with `NULL` and `UUID_IS_LOCAL`.

## Important Behavior
`nfsd_open_local_fh()` validates filehandle size, pins the NFSD net namespace, reuses an installed localio `nfsd_file` if present, converts the client credential to an NFSD service credential, and calls `nfsd_file_acquire_local()`.

On success it installs the file with `cmpxchg()` so concurrent local opens converge on one cached pointer. It holds both file and net references for installed localio state.

`UUID_IS_LOCAL` records a client UUID in the per-net local-client list with `nfs_uuid_is_local()`.

## Risks
Localio deliberately bypasses connection-based authorization and crosses client/server kernel contexts. Security depends on correct credential mapping, auth-domain selection, filehandle validation, and net namespace lifetime handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/localio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/lockd.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/lockd.c

## Summary
Provides NFSD’s binding layer for lockd without requiring direct NFS client/server compile-time coupling.

## Key APIs
- `nfsd_lockd_init()`.
- `nfsd_lockd_shutdown()`.
- Internal `nlm_fopen()` and `nlm_fclose()`.

## Important Behavior
`nlm_fopen()` converts an NLM filehandle into an NFSD service filehandle, chooses read or write access from POSIX open flags, and calls `nfsd_open()` with NLM, owner-override, and GSS-bypass permission flags.

It maps `nfserr_jukebox` to `-EWOULDBLOCK`, stale filehandles to `-ESTALE`, and other failures to `-ENOLCK`.

## Risks
The NLM path intentionally allows GSS bypass and, when export policy permits, authentication bypass for older clients. This makes the path security-sensitive even though it is compatibility-oriented.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/lockd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/netlink.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/netlink.c

## Summary
Auto-generated generic netlink family definition for NFSD control operations.

## Main Contents
Defines common nested nla policies for sockets and protocol versions, operation-specific policies, the `nfsd_nl_ops` split-op table, and `nfsd_nl_family`.

## Commands
Supports RPC status dump, thread set/get, protocol version set/get, listener set/get, and pool mode set/get.

## Important Behavior
Mutating commands require `GENL_ADMIN_PERM`. The family is network-namespace aware and allows parallel ops.

## Risks
The file is generated from `Documentation/netlink/specs/nfsd.yaml`; semantic changes should be made in the YAML spec and regenerated, not hand-edited here.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/netlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/netlink.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/netlink.h

## Summary
Auto-generated NFSD generic netlink header.

## Main Contents
Declares common nla policies, handler prototypes for all NFSD generic netlink commands, and the `nfsd_nl_family` object.

## Important Details
Includes the NFSD netlink UAPI header and generic netlink headers. Handler implementations live elsewhere; this header wires generated declarations to those implementations.

## Risks
Generated from `Documentation/netlink/specs/nfsd.yaml`; edits should be made in the spec and regenerated.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/netlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/netns.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/netns.h

## Summary
Defines per-network-namespace NFSD state.

## Main Contents
`struct nfsd_net` collects export caches, idmap caches, NFSv4 client/session/state tracking, duplicate reply cache state, per-net stats, server lifecycle state, write verifier state, server-to-server copy state, version enablement flags, localio state, and callback state.

## Important Fields
- `svc_expkey_cache` and `svc_export_cache` for exports.
- `idtoname_cache` and `nametoid_cache` for idmapping.
- NFSv4 client hash tables, session table, reclaim tracking, laundromat work, and grace/lease state.
- `nfsd_info.serv` via `#define nfsd_serv`.
- Duplicate reply cache table, counters, and shrinker.
- Per-net filecache disposal list.
- `nfsd_versions[]` and `nfsd4_minorversions[]`.
- Optional localio client tracking under `CONFIG_NFS_LOCALIO`.
- Optional filehandle siphash key pointer.

## Key APIs
Declares `nfsd_net_try_get()`, `nfsd_net_put()`, `nfsd_copy_write_verifier()`, and `nfsd_reset_write_verifier()`.

## Risks
This is a central cross-subsystem structure. Initialization order matters, and `nfsd_netns_ready()` only checks `sessionid_hashtbl`, so callers must understand which specific subsystems are initialized before using their fields.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/netns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs2acl.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs2acl.c

## Summary
Implements the version 2 NFSACL side protocol for NFSD.

## Procedures
- `NULL`.
- `GETACL`.
- `SETACL`.
- `GETATTR`.
- `ACCESS`.

## Important Behavior
`GETACL` verifies the filehandle, validates the ACL mask, gathers attributes, fetches access and/or default POSIX ACLs, and synthesizes a minimal access ACL from mode bits when needed.

`SETACL` verifies setattr permission, takes a write reference, locks the inode, sets access and default POSIX ACLs, releases decoded ACLs, and returns updated attributes.

`ACCESS` delegates to `nfsd_access()` and returns attributes plus the access mask.

## XDR and Release
Provides local decode/encode helpers for ACL and access arguments/results. ACL references allocated during decode or lookup are released in procedure or release callbacks.

## Risks
This protocol bridges old NFSACL semantics to POSIX ACLs. Error mapping differs slightly from NFSv3 ACL code, and the procedure table labels the ACCESS procedure name as `"SETATTR"`, which appears to be display/debug metadata rather than dispatch behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs2acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs3acl.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs3acl.c

## Summary
Implements the version 3 NFSACL side protocol for NFSD.

## Procedures
- `NULL`.
- `GETACL`.
- `SETACL`.

## Important Behavior
`GETACL` verifies the target, validates the ACL mask, fetches access and default POSIX ACLs, and synthesizes an access ACL from inode mode when no access ACL exists.

`SETACL` verifies setattr permission, gets write access, locks the inode, sets access and default POSIX ACLs, drops write access, releases decoded ACLs, and reports NFSv3 status with post-op attributes.

## XDR and Release
Uses NFSv3 filehandle decoding, `nfs_stream_decode_acl()`, `nfs_stream_encode_acl()`, post-op attribute encoding, and release callbacks for ACL/fhandle cleanup.

## Risks
Default ACL handling for non-directories is noted as a compatibility uncertainty. Correct cleanup depends on release callbacks and explicit ACL release on error paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs3acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs3proc.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs3proc.c

## Summary
Implements NFSD NFSv3 RPC procedure handlers and the NFSv3 procedure dispatch table.

## Procedures
Covers all NFSv3 core procedures: `NULL`, `GETATTR`, `SETATTR`, `LOOKUP`, `ACCESS`, `READLINK`, `READ`, `WRITE`, `CREATE`, `MKDIR`, `SYMLINK`, `MKNOD`, `REMOVE`, `RMDIR`, `RENAME`, `LINK`, `READDIR`, `READDIRPLUS`, `FSSTAT`, `FSINFO`, `PATHCONF`, and `COMMIT`.

## Important Behavior
`nfsd3_map_status()` maps internal NFSD errors to NFSv3-visible status codes.

Read and write handlers clamp sizes to service payload limits and `OFFSET_MAX`. `READ` reserves response buffer space before calling `nfsd_read()`. `WRITE` rejects oversized offsets and delegates to `nfsd_write()`.

`CREATE` implements unchecked, guarded, and exclusive create semantics. Exclusive create encodes the verifier into atime/mtime seconds after clearing high bits for compatibility.

`READDIR` and `READDIRPLUS` initialize page-backed directory list XDR buffers, encode cookies later, and recycle only pages used in the reply. `READDIRPLUS` honors `NFSEXP_NOREADDIRPLUS`.

`COMMIT` acquires a GC filecache entry and calls `nfsd_commit()` with the write verifier.

## Dispatch Table
`nfsd_procedures3` maps procedure numbers to handlers, XDR decode/encode functions, release callbacks, duplicate reply cache policy, argument/result sizes, and expected XDR response sizes. Non-idempotent operations generally use `RC_REPLBUFF`.

## Risks
Procedure handlers rely heavily on `svc_fh` lifetime discipline. Directory listing response construction is sensitive to page accounting and cookie backpatching. CREATE exclusive compatibility behavior encodes verifier data into timestamps and has filesystem timestamp-range caveats.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs3proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs3xdr.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs3xdr.c

## Summary
Provides XDR decode, encode, directory-entry, and release helpers for NFSD NFSv3.

## Main Responsibilities
- Decode NFSv3 filehandles, filenames, attributes, create/mknod args, read/write payloads, directory args, and commit args.
- Encode NFSv3 status, filehandles, attributes, weak cache consistency data, read/write payload metadata, directory entries, filesystem stats, fsinfo, pathconf, and commit replies.
- Backpatch directory cookies.
- Release service filehandle references after replies.

## Important Behavior
Filehandle decoding rejects zero-sized and oversized handles. Filename decoding rejects empty names, names over `NFS3_MAXNAMLEN`, embedded NUL bytes, and `/`.

Attribute decoding maps uid/gid through `nfsd_user_namespace(rqstp)` and records only valid ids. Write decoding verifies count equals opaque length and clamps large writes to `svc_max_payload()`.

`svcxdr_encode_fattr3()` maps Linux stat fields to NFSv3 attributes, including fsid source selection from explicit fsid, export UUID, or superblock device. Symlink sizes are capped at `NFS3_MAXPATHLEN` in attributes.

Weak cache consistency encoding uses saved pre/post attributes when available and falls back to conditional post-op attributes otherwise.

`READDIRPLUS` entry encoding composes child filehandles, skips mountpoints, avoids returning `".."` filehandles at filesystem/export roots, and emits absent attrs/fh when composition fails.

## Key APIs
- `svcxdr_decode_nfs_fh3()`, `svcxdr_encode_nfsstat3()`, `svcxdr_encode_post_op_attr()`.
- `nfs3svc_decode_*()` procedure decoders.
- `nfs3svc_encode_*()` procedure encoders.
- `nfs3svc_encode_entry3()`, `nfs3svc_encode_entryplus3()`, `nfs3svc_encode_cookie3()`.
- `nfs3svc_release_fhandle()`, `nfs3svc_release_fhandle2()`.

## Risks
Manual XDR sizing and page-backed opaque data encoding must remain consistent with procedure response reservations. Directory cookie backpatching depends on `cookie_offset` being reset correctly after each entry.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs3xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4acl.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4acl.c

## Summary
Implements conversion between Linux POSIX ACLs and NFSD’s NFSv4 ACL representation.

## Main Responsibilities
- Convert POSIX access/default ACLs to NFSv4 ACE lists for GETATTR-style reporting.
- Convert client-supplied NFSv4 ACLs into POSIX access/default ACLs for SETATTR-style updates.
- Map special who strings such as `OWNER@`, `GROUP@`, and `EVERYONE@`.
- Allocate NFSv4 ACL storage and sort POSIX ACL entries for validation.

## POSIX to NFSv4
`nfsd4_get_nfs4_acl()` fetches the inode access ACL or synthesizes one from mode bits. For directories, it also fetches a default ACL. It allocates for the worst case of deny/allow pairs and calls `_posix_to_nfsv4_one()`.

The conversion emits DENY ACEs where needed to preserve POSIX effective permissions, then ALLOW ACEs for owner, named users, group owner, named groups, and everyone. Default ACLs are emitted with inheritance and inherit-only flags.

## NFSv4 to POSIX
`nfs4_acl_nfsv4_to_posix()` processes ALLOW and DENY ACEs into effective and default `posix_acl_state` objects. It rejects unsupported ACE types/flags and rejects inheritance flags on non-directories.

The state machine tracks allowed and denied bits for owner, group, other, everyone, named users, named groups, and the POSIX mask. Missing owner/group/other default entries are copied from the effective ACL if any default ACEs were supplied.

`nfsd4_acl_to_attr()` stores converted ACLs into `struct nfsd_attrs` and maps invalid/unsupported ACLs to `nfserr_attrnotsupp`.

## Helper APIs
- `nfs4_acl_bytes()`.
- `nfs4_acl_get_whotype()`.
- `nfs4_acl_write_who()`.
- `sort_pacl_range()`.

## Risks
The conversion is intentionally pessimistic when mapping NFSv4 permissions to POSIX permissions. DENY/ALLOW ordering and group aggregation are subtle because POSIX ACLs and NFSv4 ACLs have different semantics, especially for users in multiple groups and inherited default ACLs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4acl.c -->