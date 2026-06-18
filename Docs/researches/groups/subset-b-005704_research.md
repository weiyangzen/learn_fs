# subset-b-005704 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/trace.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/trace.h

## Purpose

`trace.h` defines the tracepoint surface for the in-kernel NFS server. It is not runtime logic by itself; it is the observability ABI consumed by ftrace/perf/BPF tooling and by NFSD developers diagnosing protocol, file-cache, export-cache, duplicate-reply-cache, stateid, callback, control-plane, VFS, pNFS, and server-side-copy behavior.

## Important APIs, Types, and Functions

The file sets `TRACE_SYSTEM nfsd` and relies on Linux tracepoint macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, and `TRACE_DEFINE_ENUM`. Reusable field/assignment macros `NFSD_TRACE_PROC_CALL_FIELDS`, `NFSD_TRACE_PROC_CALL_ASSIGNMENTS`, `NFSD_TRACE_PROC_RES_FIELDS`, and `NFSD_TRACE_PROC_RES_ASSIGNMENTS` capture network namespace inode, xid, local address, and remote address from `struct svc_rqst`.

Major event families include XDR decode/encode failures (`nfsd_garbage_args_err`, `nfsd_cant_encode_err`), dynamic thread scaling, NFSv4 compound progress and errors, filehandle verification and export lookups, VFS I/O (`read_*`, `write_*`, `commit_*`), directory entries, clone/copy errors, delegation wakeups, stateid/open/delegation/layout events, session slot sequence events, clientid lifecycle, grace/write-verifier events, file-cache lifetime and GC events, duplicate reply cache events, callback setup/lifetime/completion events, control-file writes, COPY lifecycle, VFS metadata operations, and pNFS fence errors.

Format helpers such as `show_nfsd_may_flags`, `show_fs_file_type`, `show_stid_type`, `show_stid_status`, `show_nfs_slot_flags`, `show_nf_flags`, `show_drc_retval`, `show_cb_state`, `show_nfsd_authflavor`, and `show_nfsd_cb_opcode` translate bitfields and enum values into trace output.

## Control Flow

Callers include trace hooks spread across NFSD request decode/encode, `fh_verify`, export cache lookup/update, VFS read/write/create/rename/unlink/statfs paths, NFSv4 state management, filecache, duplicate reply cache, callback RPC code, server control files, and COPY/CLONE handling. Each tracepoint snapshots only stable scalar data, hashes, copied strings, or socket addresses into the ring buffer; the print format later renders those fields without dereferencing live objects that may have been freed.

## State and Persistence Behavior

The tracepoints do not own persistent NFSD state. They expose identifiers for persistent or long-lived state: net namespace inode, boot time, write verifier bytes, xid, filehandle hash, clientid/session/stateid tuples, callback addresses, file-cache refcounts and flags, duplicate-reply-cache checksums, and operation status codes. These values are snapshots for diagnostics and do not change server behavior.

## Dependencies and Integration Points

This header integrates with Linux trace infrastructure and with NFSD internals from `export.h`, `nfsfh.h`, `xdr4.h`, `state.h`, `filecache.h`, `vfs.h`, and `cache.h`. It also uses shared trace format helpers from `trace/misc/fs.h`, `trace/misc/nfs.h`, and `trace/misc/sunrpc.h`. It ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>`, so include ordering and single-definition rules matter.

## Risks and Edge Cases

Tracepoints run in hot paths, including read/write and file-cache lookup. Field collection must avoid blocking, excessive allocation, and unsafe dereferences. String fields need correct length handling because path, tag, and operation names can come from request data. Some events expose hashed file handles rather than full handles, which is intentional for size and sensitivity but limits correlation. Changes to internal struct fields can silently break trace output if event assignment code is not updated.

## Test Signals

Build with NFSD and tracing enabled to catch tracepoint declaration errors. Runtime validation should enable `nfsd:*` tracepoints while exercising mount/export lookup, NFSv3 and NFSv4 compounds, file reads/writes, commits, creates, renames, unlinks, readdir, callback recall, client recovery, duplicate request replay, and server control files. Useful failure signals are tracepoint format warnings, BPF program load failures due to format changes, missing xid/clientid correlation, or crashes from stale pointer usage in `TP_fast_assign`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/vfs.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/vfs.c

## Purpose

`vfs.c` is NFSD's VFS execution layer. It translates already-decoded NFS requests into Linux VFS operations while enforcing export policy, NFS-specific permission semantics, write verifier rules, weak cache consistency attributes, stable-write/commit behavior, file-cache interaction, local I/O throttling, NFSv4 xattrs, and NFSv4.2 clone/copy/fallocate helpers.

## Important APIs, Types, and Functions

`nfserrno()` maps Linux negative errno values to network-order NFS status values and warns on unmapped errors. Lookup and traversal are handled by `nfsd_lookup_dentry()`, `nfsd_lookup()`, `nfsd_cross_mnt()`, `nfsd_lookup_parent()`, and `nfsd_mountpoint()`. Attribute operations are centered on `nfsd_setattr()`, `nfsd_sanitize_attrs()`, `__nfsd_setattr()`, `nfsd_get_write_access()`, `commit_metadata()`, and `commit_inode_metadata()`.

I/O entry points include `nfsd_read()`, `nfsd_splice_read()`, `nfsd_iter_read()`, `nfsd_direct_read()`, `nfsd_write()`, `nfsd_vfs_write()`, `nfsd_direct_write()`, and `nfsd_commit()`. Object operations include `nfsd_create()`, `nfsd_create_locked()`, `nfsd_create_setattr()`, `nfsd_readlink()`, `nfsd_symlink()`, `nfsd_link()`, `nfsd_rename()`, `nfsd_unlink()`, `nfsd_readdir()`, `nfsd_statfs()`, and `nfsd_filp_close()`. NFSv4-specific helpers include junction detection, xattr operations, `nfsd4_vfs_fallocate()`, `nfsd4_clone_file_range()`, and `nfsd_copy_file_range()`.

## Control Flow

Most operations start with `fh_verify()` to resolve and authorize a filehandle under a requested type and `NFSD_MAY_*` access mask. Lookup refuses symlink following, treats `.` and `..` specially, and conditionally crosses mountpoints only when export, v4root, nohide, or NFSv4 rules allow it. Creation and removal paths acquire write access with `fh_want_write()`, use VFS helpers such as `start_creating()`, `start_removing()`, and `start_renaming()`, fill pre/post WCC attributes, call the VFS mutation, then commit metadata for synchronous exports.

Reads acquire an `nfsd_file` from the filecache, prefer splice unless globally disabled or GSS integrity/privacy is active, and fall back to iterator reads. Direct reads expand the byte range to filesystem alignment requirements and then trim the returned NFS payload to the original request. Writes convert the incoming `xdr_buf` to bio vectors, set `IOCB_SYNC`/`IOCB_DSYNC` for stable writes, optionally split direct I/O into prefix/middle/suffix segments, check writeback errors, update stats, and reset the write verifier on durable-storage failures. `nfsd_commit()` clamps the client range to filesystem limits, fsyncs synchronous exports, checks writeback errors, and returns the current verifier.

## State and Persistence Behavior

This file changes filesystem state through VFS operations: metadata updates, file data writes, xattrs, links, renames, unlinks, directory creation, device/special creation, clone/copy, and fallocate. It also updates NFSD-visible transient state such as WCC pre/post attributes, request page vectors, file-cache references, I/O stats, and the per-network write verifier. Persistent durability is export-policy-sensitive: `EX_ISSYNC` forces metadata or data commit paths; unstable writes rely on later COMMIT and verifier stability.

## Dependencies and Integration Points

The implementation depends on core VFS, namei, exportfs, security hooks, xattrs, POSIX ACLs, writeback/error-sequence APIs, splice/iov_iter/direct I/O, fsnotify, SUNRPC request buffers, NFSD filecache, export policy, and NFSv3/NFSv4 XDR/state headers. It is the integration point between protocol operation handlers and underlying filesystems.

## Risks and Edge Cases

High-risk areas are mount crossing across namespaces, parent lookup at export roots, negative dentries, delegation retry loops on `-EAGAIN`, write verifier reset semantics, direct I/O alignment, partial direct writes, GSS MIC safety with splice, and cached file closing before unlink/rename for filesystems that request it. Permission behavior intentionally diverges from ordinary POSIX in owner-override and device-local-access cases. Xattr list/get paths must lock around probe-and-fetch to avoid size changes.

## Test Signals

Exercise NFSv2/v3/v4 lookup, crossmnt/nohide/v4root traversal, guarded setattr, chmod/chown with setuid/setgid clearing, synchronous and asynchronous writes, commit verifier behavior, direct and buffered I/O, GSS krb5i/krb5p reads, create/mkdir/mknod/symlink/link/rename/remove, readdir cookie sizing, xattr get/list/set/remove, clone/fallocate, and export read-only checks. Tracepoints in `trace.h`, writeback error injection, lockdep, KASAN, fsnotify behavior, and delegation recall tests are good validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/vfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/vfs.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/vfs.h

## Purpose

`vfs.h` declares NFSD's internal VFS-facing service API and access flag vocabulary. It is the contract between protocol operation implementations and `vfs.c`, plus adjacent helpers such as the filecache and NFSv4 handlers.

## Important APIs, Types, and Functions

The `NFSD_MAY_*` constants define NFSD permission intents. The low bits intentionally match Linux `MAY_EXEC`, `MAY_WRITE`, and `MAY_READ`; extra bits express NFS-specific behavior such as setattr, truncate, lockd access, owner override, local device access, GSS bypass, lease-breaking suppression, read-if-exec, 64-bit readdir cookies, and localio tracing. `NFSD_MAY_CREATE` and `NFSD_MAY_REMOVE` compose common directory mutation masks.

`nfsd_filldir_t` is the callback shape for readdir encoding. `struct nfsd_attrs` bundles an input `iattr`, optional security label, access/default POSIX ACLs, and per-extension output errors. `nfsd_attrs_free()` releases ACL references and `nfsd_attrs_valid()` answers whether any attribute-like update is present.

The prototypes cover errno translation, lookup/mount traversal, setattr, create, access, commit, open, read/write, symlink/link/rename/unlink, readdir, statfs, permission checks, synchronous file close, NFSv4 xattr operations, and NFSv4.2 clone/fallocate helpers.

## Control Flow

Protocol handlers include this header to call a typed VFS operation after XDR decode and filehandle preparation. Typical flow is: decode request into an operation-specific struct, call a `vfs.h` function with `struct svc_rqst` and `struct svc_fh`, encode returned status and result fields, then release filehandles and attributes. The access flags guide `fh_verify()`, `nfsd_permission()`, `nfsd_open()`, and filecache acquisition.

## State and Persistence Behavior

The header itself stores no state. It exposes operations that mutate backing filesystems and NFSD runtime state in `vfs.c`. `struct nfsd_attrs` is an important lifetime carrier: ACL references and optional labels are decoded before VFS execution, consumed by `nfsd_setattr()` or create paths, and then released by callers.

## Dependencies and Integration Points

It depends on Linux `fs.h`, POSIX ACLs, NFSD filehandle definitions, and `nfsd.h`. Under `CONFIG_NFSD_V4`, it exposes xattr, clone, and fallocate helpers used by NFSv4 operation code. The permission constants are also mirrored by trace formatting in `trace.h`.

## Risks and Edge Cases

Because the low access bits must match VFS `MAY_*`, changing flag values would break permission checks. Callers must respect ownership rules documented in comments: many functions require `fh_put()` afterward and some creation paths transfer dentry references to release callbacks. Attribute callers must release ACLs and inspect per-field errors for labels/ACLs.

## Test Signals

Build coverage should catch mismatched prototypes and `CONFIG_NFSD_V4` guards. Runtime tests should validate that each protocol version calls the correct VFS entry point with the intended `NFSD_MAY_*` flags, especially write/truncate/create/remove, xattr, direct I/O, clone/fallocate, and readdir cookie behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/vfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/xdr.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/xdr.h

## Purpose

`xdr.h` defines server-side NFSv2 XDR argument/result storage types and encoder/decoder prototypes. It is mainly a typed bridge between SUNRPC XDR streams and the NFSD operation layer.

## Important APIs, Types, and Functions

Request structs include `nfsd_fhandle`, `nfsd_sattrargs`, `nfsd_diropargs`, `nfsd_readargs`, `nfsd_writeargs`, `nfsd_createargs`, `nfsd_renameargs`, `nfsd_linkargs`, `nfsd_symlinkargs`, and `nfsd_readdirargs`. Response structs include `nfsd_stat`, `nfsd_attrstat`, `nfsd_diropres`, `nfsd_readlinkres`, `nfsd_readres`, `nfsd_readdirres`, and `nfsd_statfsres`.

`union nfsd_xdrstore` sizes per-request scratch storage, and `NFS2_SVC_XDRSIZE` exposes that size to the RPC dispatch table. Decoder prototypes are named `nfssvc_decode_*`; encoder prototypes are `nfssvc_encode_*`. Helpers such as `nfssvc_encode_nfscookie()`, `nfssvc_encode_entry()`, `svcxdr_decode_fhandle()`, `svcxdr_encode_stat()`, and `svcxdr_encode_fattr()` are shared with NFSv2 ACL support.

## Control Flow

For each NFSv2 procedure, the RPC layer allocates argument/result storage using the union size, invokes the matching decode routine into one of these structs, executes a service operation, then calls the matching encode routine. Readdir responses carry an `xdr_stream`, `xdr_buf`, common readdir cursor data, and a cookie offset so directory entries can be encoded incrementally.

## State and Persistence Behavior

The structs are per-RPC transient state. Persistent changes occur only after decoded arguments are passed to VFS/service logic. Several fields hold filehandle references, page pointers, or XDR buffers that require release callbacks such as `nfssvc_release_attrstat()`, `nfssvc_release_diropres()`, and `nfssvc_release_readres()`.

## Dependencies and Integration Points

This header depends on Linux VFS types, `nfsd.h`, `nfsfh.h`, SUNRPC `xdr_stream`, `xdr_buf`, pages, and `svc_fh`. It feeds the NFSv2 dispatch implementation and helper code used by v2 ACL encoding.

## Risks and Edge Cases

NFSv2 uses 32-bit offsets and cookies, so handlers must guard truncation and maximum file sizes. Result structs that carry pages or filehandles need correct release functions to avoid leaks. Readdir encoding has tight buffer constraints and must report too-small/eof correctly.

## Test Signals

Run NFSv2 getattr/setattr/lookup/read/write/create/remove/rename/link/symlink/readdir/statfs tests, including oversized names, short reply buffers, 32-bit offset boundaries, readlink page handling, and filehandle release/leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/xdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/xdr3.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/xdr3.h

## Purpose

`xdr3.h` defines NFSD's NFSv3 XDR argument/result structs and the NFSv3 encoder/decoder API. Compared with NFSv2 it adds 64-bit offsets/cookies, ACCESS, COMMIT, weak cache consistency result shapes, FSINFO/PATHCONF, and optional POSIX ACL operations.

## Important APIs, Types, and Functions

Argument types include `nfsd3_sattrargs` with guard time, `nfsd3_diropargs`, `nfsd3_accessargs`, `nfsd3_readargs`, `nfsd3_writeargs` with stable mode and verifier payload, `nfsd3_createargs`, `nfsd3_mknodargs`, `nfsd3_renameargs`, `nfsd3_linkargs`, `nfsd3_symlinkargs`, `nfsd3_readdirargs`, `nfsd3_commitargs`, `nfsd3_getaclargs`, and `nfsd3_setaclargs`.

Response types include `nfsd3_attrstat`, `nfsd3_diropres`, `nfsd3_accessres`, `nfsd3_readlinkres`, `nfsd3_readres`, `nfsd3_writeres`, `nfsd3_renameres`, `nfsd3_linkres`, `nfsd3_readdirres`, `nfsd3_fsstatres`, `nfsd3_fsinfores`, `nfsd3_pathconfres`, `nfsd3_commitres`, and `nfsd3_getaclres`. `union nfsd3_xdrstore` defines request scratch size as `NFS3_SVC_XDRSIZE`.

The declared routines are `nfs3svc_decode_*`, `nfs3svc_encode_*`, release helpers, `nfs3svc_encode_cookie3()`, `nfs3svc_encode_entry3()`, `nfs3svc_encode_entryplus3()`, and ACL helper codecs.

## Control Flow

NFSv3 dispatch decodes requests into these structs, runs the corresponding service/VFS function, and encodes responses with post-op attributes and WCC data. Readdir and readdirplus use the embedded stream/buffer/common cursor fields and scratch filehandle to encode entries and optional attributes. Write and commit results carry write verifiers used by client cache consistency.

## State and Persistence Behavior

All data structures here are per-request. They hold filehandles, decoded ACL pointers, pages, XDR payload buffers, write verifiers, stat/statfs snapshots, and readdir encoding cursors. Persistent filesystem effects come from downstream operations, while release functions clean transient filehandle and ACL/page references.

## Dependencies and Integration Points

`xdr3.h` includes `xdr.h` and shares base NFSv2 helpers. It integrates with `svc_fh`, `kstat`, `kstatfs`, `xdr_stream`, `xdr_buf`, POSIX ACLs, and NFSv3 service procedure tables.

## Risks and Edge Cases

Guarded setattr must compare ctime correctly. Readdirplus has more buffer pressure because each entry can include handles and attributes. Stable write and commit verifier fields must match writeback behavior in `vfs.c`. ACL pointers require proper release on decode or execution failure. 64-bit cookies must remain consistent with file mode flags selected by the VFS readdir layer.

## Test Signals

Exercise NFSv3 ACCESS, guarded SETATTR, READ/WRITE with stable modes, COMMIT verifier changes after writeback errors, CREATE modes, MKNOD, RENAME/LINK WCC data, READDIR/READDIRPLUS small buffers and 64-bit cookies, FSSTAT/FSINFO/PATHCONF, and getacl/setacl decode/release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/xdr3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/xdr4.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/xdr4.h

## Purpose

`xdr4.h` is the central server-side NFSv4 XDR and operation-state contract. It defines compound request/response storage, per-operation argument/result structs for NFSv4.0, v4.1, and v4.2, inline XDR encoding helpers, operation descriptors, stateid handling hooks, and prototypes for stateful operation implementations.

## Important APIs, Types, and Functions

Inline encoders `nfsd4_encode_bool()`, `nfsd4_encode_uint32_t()`, `nfsd4_encode_uint64_t()`, `nfsd4_encode_opaque_fixed()`, and `nfsd4_encode_opaque()` reserve XDR stream space and return NFS status. `struct nfsd4_compound_state` tracks current/saved filehandles, replay owner, client, session, slot, minor version, response status, current/saved stateids, and stateid flags.

The file declares operation-specific structs for access, close, commit, create, delegation return, getattr, link, lock/lockt/locku, lookup, putfh, xattrs, open/open_confirm/open_downgrade, read, readdir, release_lockowner, readlink, remove, rename, secinfo, setattr, setclientid, test/free stateid, directory delegation, write, exchange_id, sequence, session/client destruction, reclaim complete, pNFS device/layout operations, NFSv4.2 allocate/deallocate/clone/copy/seek/offload status/copy notify, and xattr operations.

`struct nfsd4_op` stores an op number, status, descriptor, replay pointer, and a union of all operation payloads. `struct nfsd4_compoundargs` and `struct nfsd4_compoundres` are the decode/encode containers. `struct nfsd4_operation` binds an operation implementation, release hook, flags, name, response-size estimator, and current-stateid get/set callbacks.

## Control Flow

The NFSv4 dispatcher decodes a COMPOUND into `nfsd4_compoundargs`, using inline/scratch storage for up to eight ops and dynamically allocated temp buffers for larger data. Execution walks `struct nfsd4_op` entries, using `OPDESC()` metadata to enforce operation ordering, filehandle requirements, replay caching, response sizing, and stateid side effects. Encoding writes a compound header, per-op status, operation-specific responses, and replayed responses when applicable.

NFSv4.1 session operations use `nfsd4_sequence()` and `nfsd4_sequence_done()` to manage exactly-once slots. NFSv4.2 COPY state uses flags for intra/inter-server, sync/async, committed/completed/stopped/callback-error state, plus callback offload data and reference-counted async task state.

## State and Persistence Behavior

The structs model per-compound transient state plus references to persistent NFSD state: clients, sessions, slots, stateowners, open/lock/delegation/layout stateids, copy stateids, filehandles, and `nfsd_file` objects. Filesystem persistence is driven by downstream operation functions. Replay fields and op flags control duplicate request cache/session replay behavior, which is persistent enough to affect retries and exactly-once semantics.

## Dependencies and Integration Points

This header depends on `state.h`, `nfsd.h`, VFS filehandles, pNFS types, NFSv4 protocol constants, SUNRPC XDR streams, and operation implementations in other NFSD files. It is included by tracepoints, NFSv4 XDR codec implementation, and NFSv4 state/procedure code.

## Risks and Edge Cases

The union is large and manually synchronized with operation descriptors; adding an operation requires updates in decode, execute, encode, release, response sizing, and trace paths. XDR helper failures must propagate `nfserr_resource` without partially committing non-idempotent operations. Stateid flag handling and current/saved filehandle lifetime are error-prone. COPY/offload has complex async lifetime, callback, and cancellation state. Deviceid encode/decode uses raw big-endian field handling and assumes the unused bytes stay ignored.

## Test Signals

Exercise NFSv4 COMPOUND decode/encode with short buffers, all PUTFH/SAVEFH/RESTOREFH state transitions, replayed non-idempotent operations, NFSv4.1 sessions and slot reuse, OPEN/LOCK/CLOSE stateids, pNFS layoutget/commit/return, v4.2 allocate/deallocate/clone/copy/seek/xattrs, response-size prechecks, and release hooks under decode or execution failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/xdr4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/xdr4cb.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/xdr4cb.h

## Purpose

`xdr4cb.h` defines compile-time XDR buffer size estimates for NFSv4 callback RPCs sent by NFSD to clients. It supports sizing callback encode/decode buffers for CB_NULL, CB_SEQUENCE, CB_RECALL, CB_LAYOUTRECALL, CB_NOTIFY_LOCK, CB_OFFLOAD, CB_RECALL_ANY, and CB_GETATTR.

## Important APIs, Types, and Functions

The file is macro-only. Base sizes include `NFS4_MAXTAGLEN`, compound header sizes, session id size, referring call/list sizes, operation encode/decode sizes, filehandle size, and stateid size. Operation sizes are defined as `NFS4_enc_cb_*_sz` and `NFS4_dec_cb_*_sz`, expressed in XDR words. `NFS4_enc_cb_getattr_sz` and `NFS4_dec_cb_getattr_sz` explicitly document the expected attribute bitmap and returned attribute payload fields.

## Control Flow

Callback code uses these constants when constructing `rpc_procinfo` entries or allocating XDR buffers. Each callback compound includes a compound header and, for session-aware callbacks, a CB_SEQUENCE plus one callback operation. Decode sizes account for callback compound response headers and per-operation status fields.

## State and Persistence Behavior

No state is stored here. The constants influence transient RPC buffer allocation. Incorrect sizing can lead to encode reservation failures or truncated decode handling but does not persist data directly.

## Dependencies and Integration Points

The macros depend on NFSv4 constants such as `NFS4_MAX_SESSIONID_LEN`, `NFS4_FHSIZE`, `NFS4_STATEID_SIZE`, `NFS4_OPAQUE_LIMIT`, `NFS4_VERIFIER_SIZE`, and `XDR_QUADLEN`. They integrate with NFSv4 callback client code and callback tracepoints.

## Risks and Edge Cases

Manual XDR word accounting can drift when callback encoding changes. Underestimates cause buffer exhaustion; overestimates waste memory but are safer. `NFS4_MAXTAGLEN` is lower than NFSD compound tag max and must match callback protocol assumptions. CB_GETATTR decode sizing must remain aligned with exactly the attributes NFSD asks clients to return.

## Test Signals

Exercise each callback path with tracing enabled: delegation recall, layout recall, blocked-lock notify, offload completion, recall-any, and callback getattr. Useful signals are absence of `nfserr_resource`/XDR decode failures, successful CB_SEQUENCE handling, and correct callback status propagation under small buffer stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/xdr4cb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/Kconfig -->
# sources/distributed-fs/ceph-client/fs/nilfs2/Kconfig

## Purpose

`Kconfig` exposes the kernel configuration option for NILFS2 filesystem support. It presents NILFS2 as a tristate filesystem that can be built in, built as module `nilfs2`, or disabled.

## Important APIs, Types, and Functions

The only symbol is `CONFIG_NILFS2_FS`, described as "NILFS2 file system support". It selects `BUFFER_HEAD`, `CRC32`, and `LEGACY_DIRECT_IO`, reflecting dependencies on buffer-head metadata, checksum support, and older direct-I/O infrastructure.

## Control Flow

During kernel configuration, selecting this option enables compilation of the NILFS2 objects listed in the directory Makefile. As a module, the resulting module is named `nilfs2`.

## State and Persistence Behavior

The Kconfig file stores no runtime state. Enabling the option makes the kernel capable of mounting and modifying NILFS2 filesystems, which are log-structured and checkpoint/snapshot based.

## Dependencies and Integration Points

It integrates with the top-level filesystem Kconfig and build system. The help text documents continuous snapshotting, crash recovery, read-only snapshot mounts, and unsupported features noted by this tree's text: atime, extended attributes, and POSIX ACLs.

## Risks and Edge Cases

The selected dependencies must stay aligned with implementation requirements. If the code stops depending on legacy direct I/O or gains xattr/ACL support, the Kconfig text and selects should be revisited.

## Test Signals

Configuration tests should cover `CONFIG_NILFS2_FS=y`, `m`, and `n`. Build tests should verify selected dependencies are pulled in and the module name remains `nilfs2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/Makefile -->
# sources/distributed-fs/ceph-client/fs/nilfs2/Makefile

## Purpose

The NILFS2 `Makefile` wires `CONFIG_NILFS2_FS` to the `nilfs2.o` composite object and lists every object file participating in the filesystem implementation.

## Important APIs, Types, and Functions

`obj-$(CONFIG_NILFS2_FS) += nilfs2.o` attaches NILFS2 to kbuild. `nilfs2-y` includes inode, file, directory, superblock, namei, page, metadata-file, block mapping, btree/direct mapping, DAT, recovery, segment construction, checkpoint/sufile/ifile allocators, garbage collection inode, ioctl, and sysfs objects.

## Control Flow

When `CONFIG_NILFS2_FS` is enabled, kbuild compiles the listed `.o` files and links them into `nilfs2.o`. Module or built-in behavior is controlled by the tristate value from Kconfig.

## State and Persistence Behavior

The Makefile stores no runtime state. Its object list determines which persistence mechanisms are present in the built filesystem: log segments, checkpoints, DAT, ifile, sufile, bmap, and recovery.

## Dependencies and Integration Points

It integrates with kbuild and the local NILFS2 source layout. `alloc.o` and `bmap.o`, covered in this work item, are core metadata components in that composite object.

## Risks and Edge Cases

Forgetting to list a new object causes link failures or missing functionality. Removing or renaming objects without updating this file breaks the build. Object order usually should not encode behavior but can expose unresolved dependencies at link time.

## Test Signals

Build NILFS2 as built-in and module. Confirm all expected symbols link, `nilfs2.ko` is produced in module mode, and metadata-heavy mount/create/delete/gc paths are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/alloc.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/alloc.c

## Purpose

`alloc.c` implements NILFS2's persistent object allocator for metadata files such as the DAT and inode file. It manages numbered entries with on-disk group descriptors, bitmap blocks, and entry blocks, and exposes prepare/commit/abort operations so higher layers can allocate or free persistent records transactionally.

## Important APIs, Types, and Functions

Geometry helpers compute entries per group, groups per descriptor block, total group count, descriptor block offsets, bitmap block offsets, and entry block offsets. `nilfs_palloc_init_blockgroup()` initializes metadata-file allocator geometry and block-group locks. `nilfs_palloc_get_entry_block()` retrieves the entry block for an object number. `nilfs_palloc_entry_offset()` computes the byte offset of an entry in a folio.

Allocation and free APIs are `nilfs_palloc_prepare_alloc_entry()`, `nilfs_palloc_commit_alloc_entry()`, `nilfs_palloc_abort_alloc_entry()`, `nilfs_palloc_prepare_free_entry()`, `nilfs_palloc_commit_free_entry()`, `nilfs_palloc_abort_free_entry()`, and batched `nilfs_palloc_freev()`. `nilfs_palloc_count_max_entries()` estimates maximum representable entries from current descriptor blocks and growth room. Cache functions set, clear, and destroy `struct nilfs_palloc_cache`.

## Control Flow

Allocation starts from `req->pr_entry_nr`, maps it to a group and group offset, scans descriptor blocks for groups with nonzero free counts, obtains the bitmap block, atomically sets the next zero bit, decrements the group descriptor free count, and returns descriptor/bitmap buffers held in the request. Commit marks both buffers dirty and marks the metadata inode dirty; abort clears the bit, restores the descriptor free count, releases buffers, and clears request state.

Free preparation only pins descriptor and bitmap buffers. Commit clears the bitmap bit, increments the free count, warns if the entry was already free, marks buffers dirty, and marks the metadata inode dirty. `nilfs_palloc_freev()` batches entries by group, clears bits, detects entry blocks that become empty and deletes them, updates group descriptors, and deletes the bitmap block when an entire group becomes free.

## State and Persistence Behavior

Persistent state lives in metadata file blocks: group descriptors contain `pg_nfrees`, bitmap blocks contain allocation bits, and entry blocks hold DAT or inode entries. The allocator caches recently used descriptor, bitmap, and entry buffer heads in `mi_palloc_cache`, protected by a spinlock. Updates become persistent through dirty buffer marking and NILFS segment writing.

## Dependencies and Integration Points

This file depends on NILFS metadata-file helpers in `mdt.h`, allocator definitions in `alloc.h`, buffer heads, folio kmap helpers, little-endian bit operations, block-group locks, and NILFS warning/error reporting. It is used by DAT and ifile-style metadata layers and indirectly by bmap pointer allocation.

## Risks and Edge Cases

The allocator mixes buffer-head caching, folio local mappings, and per-group spinlocks; incorrect release or stale cache invalidation can leak buffers or corrupt allocation state. Freeing an already-free entry is detected only as a warning. `nilfs_palloc_prepare_alloc_entry()` must handle wrap/no-wrap semantics and descriptor growth limits correctly. `nilfs_palloc_freev()` assumes useful grouping of input entries but still guards group transitions. Block size greater than page size is explicitly unsupported by descriptor initialization.

## Test Signals

Exercise DAT/inode allocation until descriptor growth, no-wrap and wrap allocation, abort paths after prepared allocations/frees, batched free across groups and entry-block boundaries, freeing already-free entries, cache clear/destroy under unmount, ENOSPC behavior, metadata I/O errors, and fsck/recovery after crashes between prepare and commit at higher layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/alloc.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/alloc.h

## Purpose

`alloc.h` declares the persistent allocator interface used by NILFS2 metadata files. It defines the request object, cache object, geometry helper, bit-operation aliases, and prepare/commit/abort API implemented in `alloc.c`.

## Important APIs, Types, and Functions

`nilfs_palloc_entries_per_group()` derives group capacity from block size in bits. `struct nilfs_palloc_req` carries the target or returned entry number plus descriptor, bitmap, and entry buffer heads. `struct nilfs_bh_assoc` pairs a block offset with a cached buffer head. `struct nilfs_palloc_cache` stores the previous descriptor, bitmap, and entry buffers under a spinlock.

Public functions initialize allocator block groups, retrieve entry blocks, compute entry offsets, count maximum entries, prepare/commit/abort allocations, prepare/commit/abort frees, batch free entries, and manage caches. Bit aliases bind NILFS allocator operations to ext2 atomic little-endian bitops and generic little-endian find-bit helpers.

## Control Flow

Callers use a two-phase pattern. For allocation, set an initial `pr_entry_nr`, call prepare, initialize or link the returned object, then commit or abort. For free, set `pr_entry_nr`, prepare, then commit or abort. Entry data access uses `nilfs_palloc_get_entry_block()` and `nilfs_palloc_entry_offset()` after an entry number is known.

## State and Persistence Behavior

The header models persistent allocator updates but does not write state itself. The request retains buffer-head references across prepare/commit/abort boundaries. The cache retains buffer references between allocator calls and must be cleared/destroyed during metadata inode teardown.

## Dependencies and Integration Points

It depends on Linux buffer heads, filesystem types, and NILFS on-disk allocator descriptors. It is included by DAT, ifile, bmap, and other metadata code that needs persistent entry numbering.

## Risks and Edge Cases

Callers must always complete a prepared request with commit or abort to release buffers and preserve bitmap/descriptor consistency. The bit operation aliases assume little-endian on-disk bitmaps. Cache users must hold/release references correctly and clear caches when metadata blocks are deleted.

## Test Signals

Compile-time tests should catch signature drift with DAT/ifile/bmap callers. Runtime tests should inspect allocation/free rollback, cache teardown, bitmap endian correctness, and entry offset calculations across block sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/bmap.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/bmap.c

## Purpose

`bmap.c` is the generic NILFS2 block-map front-end. It hides whether an inode uses a compact direct map or a btree, translates virtual block numbers through the DAT when needed, serializes map operations, handles conversion between direct and btree forms, and provides helper state for allocation target selection, dirty propagation, GC, and save/restore.

## Important APIs, Types, and Functions

Lookup APIs are `nilfs_bmap_lookup_at_level()`, `nilfs_bmap_lookup_contig()`, and the inline `nilfs_bmap_lookup()` from the header. Mutation APIs include `nilfs_bmap_insert()`, `nilfs_bmap_delete()`, `nilfs_bmap_truncate()`, and `nilfs_bmap_clear()`. Segment-construction and GC integration uses `nilfs_bmap_propagate()`, `nilfs_bmap_lookup_dirty_buffers()`, `nilfs_bmap_assign()`, and `nilfs_bmap_mark()`.

Initialization and persistence helpers are `nilfs_bmap_read()`, `nilfs_bmap_write()`, `nilfs_bmap_init_gc()`, `nilfs_bmap_save()`, and `nilfs_bmap_restore()`. Allocation target helpers include `nilfs_bmap_data_get_key()`, `nilfs_bmap_find_target_seq()`, and `nilfs_bmap_find_target_in_group()`. `nilfs_bmap_convert_error()` turns internal `-EINVAL` bmap corruption signals into filesystem errors and `-EIO`.

## Control Flow

Every public map operation takes the bmap rwsem in read or write mode, dispatches to the current `b_ops` table, releases the lock, and converts errors. Lookup first obtains a pointer from the direct/btree implementation; for virtual-block maps it translates that pointer through the DAT into a physical block number and treats a missing DAT entry as metadata corruption.

Insert can trigger direct-to-btree conversion: if the current direct ops report that a key exceeds direct capacity, existing direct records are gathered and passed to `nilfs_btree_convert_and_insert()`, then the large-map flag is set. Delete can trigger btree-to-direct conversion when btree occupancy falls below the direct threshold. Truncate repeatedly deletes the last key until the requested cutoff is reached.

## State and Persistence Behavior

The in-memory `struct nilfs_bmap` contains raw on-disk bmap words, an rwsem, owning inode, ops table, last allocation key/pointer hints, pointer type, dirty state, and btree node fanout. `nilfs_bmap_read()` copies raw inode bmap data and selects pointer type by inode number: DAT uses physical pointers, cpfile/sufile use single-version virtual pointers, ifile and ordinary files use multi-version virtual pointers. `nilfs_bmap_write()` copies the raw map back to the on-disk inode and resets DAT allocation hints.

## Dependencies and Integration Points

This file depends on `direct.h`, `btree.h`, `btnode.h`, `mdt.h`, `dat.h`, and `alloc.h`. It is used by inode/page/segment code for logical-to-physical mapping and by metadata files for their own block maps. DAT translation ties ordinary block pointers to NILFS's log-structured relocation model.

## Risks and Edge Cases

The direct/btree conversion thresholds must remain consistent with on-disk root capacity constants. Missing DAT entries after bmap lookup indicate corruption and are deliberately escalated. Lock class setup for DAT and metadata files prevents false lockdep recursion reports; wrong classes can hide or invent deadlocks. Truncate loops can be expensive for very large maps. Save/restore only snapshots selected in-memory fields and assumes callers handle associated btree buffers safely.

## Test Signals

Test direct insertion up to conversion, btree deletion back to direct, lookups with DAT translation, missing DAT entry corruption handling, truncate from sparse and dense files, dirty propagation during segment writes, block assignment info generation, GC mark paths, bmap read/write across remount/recovery, and lockdep under DAT/metadata nesting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/bmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/bmap.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/bmap.h

## Purpose

`bmap.h` declares NILFS2's block-map abstraction. It defines the polymorphic operation table shared by direct and btree maps, the in-memory `struct nilfs_bmap`, pointer allocation helper wrappers around DAT operations, dirty-state helpers, and public map APIs.

## Important APIs, Types, and Functions

`union nilfs_bmap_ptr_req` carries either a raw pointer or a persistent allocator request. `struct nilfs_bmap_stats` reports block count changes. `struct nilfs_bmap_operations` is the direct/btree vtable for lookup, contiguous lookup, insert, delete, clear, dirty propagation, dirty-buffer lookup, assignment, mark, seek, last-key, conversion checks, and data gathering.

`struct nilfs_bmap` stores raw inode bmap data, rwsem, owner inode, ops pointer, allocation hints, pointer type, dirty state, and non-root btree capacity. Pointer types distinguish physical, single-version virtual, multi-version virtual, and no-pointer-ops GC maps. `struct nilfs_bmap_store` snapshots raw data and allocation/dirty fields.

Inline helpers implement bmap lookup, DAT-backed pointer allocation/end prepare/commit/abort, target pointer tracking, dirty flag checks/updates, and constants for direct/btree size thresholds.

## Control Flow

Callers invoke public functions declared here; `bmap.c` locks and dispatches to the active ops table. Direct and btree implementations call the pointer helper wrappers to allocate or end DAT entries when `NILFS_BMAP_USE_VBN()` is true. For physical maps, allocation helpers just advance or rewind `b_last_allocated_ptr`.

## State and Persistence Behavior

The raw `b_u.u_data` array is copied to/from the on-disk inode bmap field. The `NILFS_BMAP_LARGE` flag selects btree representation. Dirty state tracks whether bmap metadata must be propagated. Allocation hints are in-memory optimization state, while DAT commits persist virtual-to-physical mapping lifecycle.

## Dependencies and Integration Points

The header depends on Linux buffer heads, NILFS on-disk definitions, `alloc.h`, and `dat.h`. It is a shared contract for `bmap.c`, `direct.c`, `btree.c`, DAT, metadata files, segment writing, and garbage collection.

## Risks and Edge Cases

Pointer helper calls must be balanced: prepare allocation/end needs commit or abort. Physical-pointer fallback mutates `b_last_allocated_ptr` and must rewind on abort. The large/small threshold constants must match direct and btree capacities. Dirty helper comments assume the bmap semaphore is already locked.

## Test Signals

Build direct and btree users after any vtable change. Runtime tests should cover pointer allocation commit/abort for DAT-backed and physical maps, dirty flag transitions, save/restore, direct/btree conversion thresholds, GC map initialization, and bmap lookup/assign integration during segment construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/bmap.h -->
