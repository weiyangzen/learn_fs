# Group Research: group_1034_linux_stable_sources_os_linux_linux_stable_fs_nfsd_trace_h_sources__910f6a3e75a4

Scope: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/trace.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/trace.h

Purpose: defines the Linux tracepoint surface for NFSD. It is a trace-event catalog rather than runtime logic, covering request decode/encode errors, compound execution, filehandle verification, exports, VFS calls, I/O, state IDs, sessions, clients, filecache, duplicate reply cache, callbacks, nfsctl operations, server-side copy, xattrs-adjacent VFS operations, and pNFS fencing.

Key structures and state:
- Uses tracepoint macros such as `TRACE_EVENT`, `TRACE_EVENT_CONDITION`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, and `TRACE_DEFINE_ENUM`.
- Common field/assignment macros capture network namespace inode, RPC XID, server/client socket addresses, procedure status, filehandle hashes, stateid components, and NFSD permission flags.
- Includes NFSD internals (`state.h`, `filecache.h`, `vfs.h`, `cache.h`) only after early trace definitions that need lighter dependencies.
- Symbol printers translate NFSD access bits, file types, stateid types/statuses, session flags, callback state/opcodes, RPC auth flavors, filecache flags, duplicate reply cache outcomes, and recall-any masks.

Major logic:
- XDR and compound tracepoints record garbage args, encode failures, op decode failures, operation status, and nontrivial compound errors.
- Filehandle/export tracepoints record verification attempts, verification failures, export-key lookup/update, export-by-name lookup, and export cache updates.
- I/O tracepoints distinguish read/write start, splice/vector/direct paths, I/O completion, commit, and read/write error reporting.
- NFSv4 state tracepoints cover stateid allocation/free/revoke, replay, session sequence status, create-session slot sequencing, client confirmation/expiry/reclaim, verifier and credential mismatches, and grace lifecycle.
- Filecache tracepoints expose file allocation, acquisition, open/opened, cache lookup, fsnotify invalidation, LRU/GC/shrinker activity, close, and DIO alignment attributes.
- Callback tracepoints cover setup, lifecycle queue/restart/destroy, backchannel update/shutdown, CB_SEQUENCE slot state, delegation/layout/offload/getattr/notify-lock callbacks, and callback completion.
- Control-plane tracepoints cover `/proc/fs/nfsd`-style actions: unlock IP/fs, filehandle generation, thread pool changes, version/port/block-size/minthreads/time/recoverydir settings, grace end, and filehandle key changes.
- Server-side copy tracepoints capture intra/inter/async copy request state, source/destination/callback stateids, offsets/counts, completion, cancellation, and clone errors.
- Final pNFS tracepoint class records fencing errors by client, netns, device string, and error.

Concurrency and lifetime:
- Tracepoints copy strings, socket addresses, flags, stateids, and verifier bytes into trace entries during `TP_fast_assign`, avoiding later dereference of mutable kernel state.
- Several tracepoints intentionally store pointers only for identity/debug output and label them as not dereferenceable.
- Conditional tracepoints avoid unsafe contexts, for example filehandle verification events require a non-NULL request and callback recall requires a client pointer.

Important dependencies:
- Depends on kernel tracing APIs and shared trace helpers from `trace/misc/fs.h`, `trace/misc/nfs.h`, and `trace/misc/sunrpc.h`.
- Closely follows structures from NFSD export, filehandle, NFSv4 XDR, state, filecache, VFS, and duplicate reply cache code.
- Provides the event names consumed by NFSD implementation files such as `vfs.c`, `nfs4callback.c`, `nfs4state.c`, `filecache.c`, and nfsctl code.

Risk/edge cases:
- Tracepoint field layouts are tightly coupled to NFSD structure fields; structure churn can silently make trace output misleading if not updated.
- Some events expose client addresses, export paths, filenames, symlink targets, verifier bytes, and auth flavor information through tracing.
- Socket address length arguments must match local/remote address fields; most events take care to use transport-provided lengths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/vfs.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/vfs.c

Purpose: implements the NFSD VFS helper layer. It maps Linux VFS operations and errnos into NFS protocol behavior for lookup, mount/export crossing, attributes, permissions, open, read, write, commit, create, link, rename, unlink, readdir, statfs, xattrs, NFSv4 clone/fallocate, and metadata durability.

Key structures and state:
- Global tunables select read/write cache behavior: `nfsd_disable_splice_read`, `nfsd_io_cache_read`, and `nfsd_io_cache_write`.
- `nfserrno()` maps negative Linux errnos to network-endian NFS status values and warns on unexpected codes.
- `struct accessmap` maps NFS ACCESS bits to internal `NFSD_MAY_*` permission checks for regular files, directories, and special files.
- Direct-write support uses `struct nfsd_write_dio_seg` to split writes into prefix, aligned direct-I/O middle, and suffix segments.
- Readdir buffering uses `struct buffered_dirent` and `struct readdir_data` to decouple `iterate_dir()` from later encoding/lookup work.

Major logic:
- Lookup helpers handle `.`/`..`, parent export lookup, `NOHIDE`, NFSv4 pseudo-root behavior, junction xattrs, automount following, and `CROSSMOUNT`.
- `nfsd_setattr()` sanitizes mode/ownership changes, handles size changes separately, honors ctime guard checks, waits once for delegation return on `-EAGAIN`, applies labels/POSIX ACLs, fills weak cache consistency attrs, and commits metadata for sync exports.
- NFSv4 helpers detect junction xattrs, run `vfs_clone_file_range()` with optional sync/writeback verification, cap copy-file-range chunks to 4 MiB, and call `vfs_fallocate()`.
- `nfsd_access()` computes supported and allowed access masks by probing `nfsd_permission()` and treating denial statuses as ordinary ACCESS false bits.
- Open paths verify filehandles, optionally break leases, honor owner override for regular files after protocol-level open, retry on `-EOPENSTALE`, and expose a filecache-oriented verified open helper.
- Read paths choose splice when safe, otherwise iterator reads; direct reads expand to filesystem alignment and trim the returned payload back to the requested range.
- Write paths convert XDR payloads to bvecs, choose buffered/direct/dontcache operation, set sync flags from NFS stable mode and export sync policy, manage write verifier resets on durable-storage errors, apply local-throttle handling for localhost writes, and update stats/fsnotify.
- Commit converts NFS offset/count to a safe `vfs_fsync_range()` span, checks writeback errors since request start, and returns/reset write verifiers correctly.
- Create, symlink, link, rename, and unlink wrap VFS operations with write access, WCC pre/post attrs, metadata commits, special NFS status translation for busy open files, delegation-return retry, and filecache close-before-unlink/rename support.
- Readdir opens a private directory file, sets 32/64-bit cookie mode, seeks to the requested offset, buffers one page of dirents, and invokes the protocol-specific filldir callback.
- NFSv4 xattr helpers implement get/list/set/remove with permission checks, inode locking, probe-then-allocate reads, `XATTR_LIST_MAX` handling, WCC attrs for modifications, and xattr-specific errno mapping.
- `nfsd_permission()` applies export/mount read-only checks, immutable/append restrictions, owner override, ordinary inode permission checks, and read-if-exec fallback.

Concurrency and lifetime:
- Filehandle operations rely on `fh_verify`, `fh_want_write`, `fh_drop_write`, `fh_fill_pre_attrs`, and `fh_fill_post_attrs`.
- Attribute, xattr, rename, and unlink paths use inode or VFS directory operation locking as appropriate.
- Delegation conflicts are retried once in setattr, rename, and unlink via `nfsd_wait_for_delegreturn()`.
- Filecache entries acquired by `nfsd_file_acquire_gc()` are released with `nfsd_file_put()`.
- `nfsd_filp_close()` performs synchronous final `fput` to prevent nfsd from queuing unbounded asynchronous close work.
- Readdir deliberately avoids `file->f_pos_lock` because the opened file is private to the request.

Important dependencies:
- Uses core VFS APIs: lookup, dentry open, notify_change, file range clone/copy, fallocate, read/write iterators, splice, fsync, statfs, xattrs, link/rename/unlink/mkdir/mknod/symlink, ACLs, security labels, and inode permissions.
- Integrates with NFSD export/filehandle logic, filecache, stats, write verifier state, NFSv3/v4 XDR structs, NFSv4 state/callback semantics, and tracepoints.
- Uses export operation flags such as `EXPORT_OP_REMOTE_FS` and `EXPORT_OP_CLOSE_BEFORE_UNLINK`.

Risk/edge cases:
- Write verifier reset behavior is subtle: some errors imply unstable durable storage and others do not.
- Splice reads are disabled for GSS integrity/privacy because page contents can change after MIC calculation.
- Direct I/O paths depend on exported DIO alignment attributes and fall back or report server fault on unexpected alignment failure.
- Rename is constrained to the same exported mount and export root.
- Xattr list may report `TOOSMALL` or `XATTR2BIG` because VFS/filesystem limits do not line up cleanly with NFSv4 xattr encoding.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/vfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/vfs.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/vfs.h

Purpose: declares NFSD’s VFS helper API and permission flag vocabulary shared by NFSD protocol handlers, filecache, and VFS implementation code.

Key structures and state:
- Defines `NFSD_MAY_*` access bits for execute, write, read, setattr, truncate, lockd, owner override, local special-file access, GSS bypass hints, lease-breaking suppression, read-if-exec, 64-bit readdir cookies, and localio tracing.
- `NFSD_MAY_CREATE` and `NFSD_MAY_REMOVE` compose common directory mutation permission sets.
- Defines `nfsd_filldir_t`, the callback signature used by protocol-specific readdir encoders.
- `struct nfsd_attrs` bundles input `iattr`, security label, access/default POSIX ACLs, and output error slots for label/ACL application.
- Inline helpers release POSIX ACL references and test whether any attribute payload is present.

Major logic:
- Exposes errno translation, mount crossing, lookup, dentry lookup, setattr, mountpoint detection, create, access, commit, open, read, write, symlink, link, copy-file-range, rename, unlink, readdir, statfs, permission, and synchronous close helpers.
- Conditionally exposes NFSv4-only helpers for clone, fallocate, and xattr get/list/set/remove.
- Distinguishes high-level read/write wrappers from lower-level iterator/splice and already-open-file write helpers.

Concurrency and lifetime:
- API comments establish ownership expectations: many operations require callers to `fh_put()` involved filehandles, and attribute ACLs must be released with `nfsd_attrs_free()`.
- The declarations make filecache integration explicit through `struct nfsd_file` without exposing its layout.

Important dependencies:
- Includes Linux fs/POSIX ACL headers plus NFSD filehandle and core headers.
- Implemented primarily by `vfs.c` and called from NFSv2/v3/v4 procedure/XDR handling code.

Risk/edge cases:
- Permission flags intentionally alias low bits with `MAY_READ/WRITE/EXEC`; changing values would break `nfsd_permission()`.
- Some flags are hints for special NFS semantics rather than direct VFS permission bits, so callers must choose them carefully.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/vfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/xdr.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/xdr.h

Purpose: defines the server-side XDR argument/result storage types and encode/decode entry points for NFSv2 NFSD procedures.

Key structures and state:
- Argument structs wrap filehandles and decoded parameters for setattr, dirop, read, write, create, rename, link, symlink, and readdir.
- Result structs hold status, filehandles, kstats, pages, read counts, statfs data, and readdir encoding scratch state.
- `struct nfsd_readdirres` owns an XDR stream, dirlist buffer, common readdir context, and cookie offset used while encoding directory entries.
- `union nfsd_xdrstore` is the per-request storage union sized by `NFS2_SVC_XDRSIZE`.

Major logic:
- Declares per-procedure NFSv2 decoders for fhandle, setattr, dirop, read, write, create, rename, link, symlink, and readdir args.
- Declares result encoders for status, attrstat, dirop, readlink, read, statfs, and readdir.
- Declares readdir cookie/entry encoders and release hooks for responses that hold filehandles or pages.
- Provides helper encode/decode functions for NFSv2 ACL code: filehandle, status, and file attributes.

Concurrency and lifetime:
- The header defines storage ownership used by SunRPC service dispatch; release hooks are responsible for dropping references acquired during procedure handling.
- Read and readlink results carry page pointers that must be released by the corresponding service release path.

Important dependencies:
- Includes VFS, NFSD core, and filehandle definitions.
- Implemented by NFSv2 XDR/procedure code and consumed by the NFSD RPC version table.

Risk/edge cases:
- NFSv2 uses 32-bit offsets/counts in these structures, so callers must preserve protocol truncation/limit behavior.
- `NFS2_SVC_XDRSIZE` must remain large enough for the largest union member.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/xdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/xdr3.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/xdr3.h

Purpose: defines NFSD NFSv3 XDR argument/result structures, request storage, procedure decoder/encoder prototypes, readdir entry encoders, release hooks, and NFSv3 ACL helper declarations.

Key structures and state:
- Argument structs cover setattr with guard time, dirop, access, read/write with 64-bit offsets, create/mknod, rename, link, symlink, readdir with verifier, commit, getacl, and setacl.
- Result structs cover attrstat, dirop, access, readlink, read, write with verifier, rename/link WCC-style filehandles, readdir/readdirplus scratch, fsstat, fsinfo, pathconf, commit, and getacl.
- `struct nfsd3_readdirres` contains the response filehandle, verifier, XDR stream, dirlist buffer, scratch filehandle for readdirplus, common readdir context, cookie offset, and request pointer.
- `struct nfsd3_fhandle_pair` is a dummy release type for procedures that need two filehandles released.
- `union nfsd3_xdrstore` sizes the per-request argument/result buffer via `NFS3_SVC_XDRSIZE`.

Major logic:
- Declares NFSv3 argument decoders for core file, directory, read/write, create, mknod, rename/link/symlink, readdir/readdirplus, and commit operations.
- Declares result encoders for getattr, WCC status, lookup, access, readlink, read, write, create, rename, link, readdir, fsstat, fsinfo, pathconf, and commit.
- Declares release hooks for one or two filehandles.
- Declares cookie and entry encoders for plain readdir and readdirplus.
- Provides NFSv3 ACL helper prototypes for filehandle decode, status encode, and post-op attribute encode.

Concurrency and lifetime:
- Filehandle-containing results and ACL objects are released by procedure release hooks after SunRPC encoding.
- Readdirplus uses a scratch filehandle that must be managed while encoding individual entries.

Important dependencies:
- Extends `xdr.h` and shares lower-level NFSv2/NFSD types.
- Used by `nfs3proc.c`, `nfs3xdr.c`, ACL code, and VFS readdir callbacks.

Risk/edge cases:
- Guarded setattr depends on preserving decoded guard timestamps exactly.
- Readdir verifiers and cookie offsets are protocol-visible and must stay consistent with encoder behavior.
- ACL result structures carry POSIX ACL pointers whose lifetime must be released exactly once.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/xdr3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/xdr4.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/xdr4.h

Purpose: defines the main NFSD NFSv4 server-side operation model: COMPOUND state, per-operation argument/result structures, XDR encode helpers, pNFS and NFSv4.2 data structures, operation dispatch metadata, and state-management procedure prototypes.

Key structures and state:
- Inline XDR helpers encode bools, 32-bit integers, 64-bit integers, fixed opaque data, and counted opaque/component values, returning NFS status on buffer exhaustion.
- `struct nfsd4_compound_state` tracks current/saved filehandles, replay owner, client/session/slot, minor version, status, current/saved stateids, sid flags, iov/data offsets, and SPO enforcement state.
- Per-operation structs model NFSv4 operations including access, close, commit, create, delegreturn, getattr, link, lock/lockt/locku, lookup, putfh, open/open_confirm/open_downgrade, read, readdir, readlink, remove, rename, secinfo, setattr, setclientid, test/free stateid, get-dir-delegation, verify/write, and release-lockowner.
- NFSv4.1 structures cover exchange-id, sequence, session/clientid destruction, reclaim complete, device IDs, pNFS getdeviceinfo/layoutget/layoutcommit/layoutreturn, and secinfo-no-name.
- NFSv4.2 structures cover allocate/deallocate, clone, copy/offload, seek, offload status, copy notify, and xattr operations.
- `struct nfsd4_copy` carries server-side copy request/response state, flags, callback offload data, source/destination `nfsd_file` refs, async task/list/refcount/TTL state, inter-server copy state, and per-net pointer.
- `struct nfsd4_op` stores op number, status, op descriptor, replay pointer, and a union of all operation payloads.
- `struct nfsd4_compoundargs` and `struct nfsd4_compoundres` hold decode/encode scratch state for one COMPOUND.
- `struct nfsd4_operation` describes dispatch function, release hook, flags, name, response-size estimator, and current-stateid hooks.

Major logic:
- Stateid flag macros mark current and saved stateid presence in compound state.
- Device ID inline helpers encode/decode the 16-byte NFSv4 deviceid layout used by pNFS.
- Copy inline helpers classify copy requests as synchronous/asynchronous and intra/inter-server from flag bits.
- Operation flags describe filehandle requirements, absent-fs allowance, first-op requirements, wrongsec handling, putfh-like behavior, mutating reply-size preflight, DRC cache eligibility, current-stateid clearing, and nontrivial error encoding.
- Declares the main NFSv4 compound decoder/encoder, response-size checks, operation encoder, replay encoder, fattr-to-buffer encoder, and many state/session/open/lock/delegation/clientid handlers implemented elsewhere.

Concurrency and lifetime:
- Compound args carry temporary buffers to free at release time, inline op storage for small compounds, and dynamically allocated op arrays for larger compounds.
- Operation release hooks are part of `struct nfsd4_operation` because many decoded operations own ACLs, strings, exports, file references, lock-denial owners, layout buffers, or async copy state.
- Async copy state uses list linkage, task pointer, refcount, and client/per-net references coordinated by NFSv4 procedure/state code.

Important dependencies:
- Includes `state.h` and `nfsd.h`, and is included widely by NFSv4 proc, XDR, callback, layout, trace, and VFS code.
- Uses kernel NFS protocol constants and NFSD state structures such as clients, sessions, slots, openowners, stateids, callbacks, and `nfsd_file`.

Risk/edge cases:
- The union in `struct nfsd4_op` is the ABI bridge between XDR decode and operation execution; adding operations requires correct release and size-estimation behavior.
- Mutating operations rely on `OP_MODIFIES_SOMETHING` and response-size preflight to avoid performing changes that cannot be encoded.
- NFSv4.1 sessions and v4.0 replay semantics differ, so cacheability flags are delicate.
- Inter-server copy fields combine NFSD state with NFS client-side structures and need strict lifetime handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/xdr4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/xdr4cb.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/xdr4cb.h

Purpose: defines static XDR buffer size estimates for NFSv4 callback RPCs issued by NFSD to clients.

Key structures and state:
- Contains only constants/macros, no structs or functions.
- Defines common sizes for callback compound headers, session IDs, referring call lists, CB_SEQUENCE encode/decode payloads, operation encode/decode headers, filehandles, and stateids.
- Defines per-callback encode/decode sizes for `CB_NULL`, `CB_RECALL`, `CB_LAYOUTRECALL`, `CB_NOTIFY_LOCK`, `CB_OFFLOAD`, `CB_RECALL_ANY`, and `CB_GETATTR`.

Major logic:
- Size formulas are expressed in XDR 32-bit words and compose shared pieces such as callback compound headers and sequence payloads.
- `CB_GETATTR` sizing accounts for bitmap, attribute array length, change/size, and atime/mtime fields.
- Offload sizing includes filehandle, stateid, write response info, and verifier.

Concurrency and lifetime:
- No runtime state or locking.
- Used to provision RPC encode/decode buffers before callback calls.

Important dependencies:
- Relies on NFSv4 constants such as `NFS4_MAX_SESSIONID_LEN`, `NFS4_FHSIZE`, `NFS4_STATEID_SIZE`, `NFS4_OPAQUE_LIMIT`, and `NFS4_VERIFIER_SIZE`.
- Consumed by `nfs4callback.c` callback operation definitions.

Risk/edge cases:
- Underestimating a size causes callback encode/decode buffer failures; overestimating wastes RPC buffer space.
- Size constants must be updated whenever callback encoders add protocol fields.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/xdr4cb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/Kconfig

Purpose: declares the kernel configuration option for NILFS2 filesystem support.

Key structures and state:
- Defines `CONFIG_NILFS2_FS` as a tristate option named “NILFS2 file system support”.
- Selects `BUFFER_HEAD`, `CRC32`, and `LEGACY_DIRECT_IO`.

Major logic:
- Help text describes NILFS2 as a log-structured filesystem with continuous checkpointing and mountable read-only snapshots.
- Documents that atime, extended attributes, and POSIX ACLs are not supported yet.
- Notes the module name is `nilfs2`.

Concurrency and lifetime:
- No runtime code; controls build inclusion.

Important dependencies:
- Build-time dependency selection ensures required buffer-head, CRC, and legacy direct-I/O support are available.

Risk/edge cases:
- Feature support described here constrains expectations for VFS features such as xattrs and ACLs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/Makefile

Purpose: builds the NILFS2 filesystem module/object set when `CONFIG_NILFS2_FS` is enabled.

Key structures and state:
- Adds `nilfs2.o` to `obj-$(CONFIG_NILFS2_FS)`.
- Defines the `nilfs2-y` object list.

Major logic:
- Builds NILFS2 from inode, file, directory, superblock, namei, page, metadata-file, btnode, bmap, btree, direct, dat, recovery, core filesystem, segment buffer/segment, checkpoint file, segment usage file, inode file, allocator, GC inode, ioctl, and sysfs objects.

Concurrency and lifetime:
- No runtime code.

Important dependencies:
- The object list makes `alloc.o` and `bmap.o` part of the NILFS2 module covered by this group.

Risk/edge cases:
- Object ordering is conventional kernel build metadata; missing an object would produce unresolved symbols or feature loss.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/alloc.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/alloc.c

Purpose: implements NILFS2’s persistent object allocator used for metadata objects such as DAT entries and disk inodes. It manages grouped descriptor blocks, bitmap blocks, and entry blocks in NILFS metadata files.

Key structures and state:
- Allocator geometry derives from metadata-file block size: entries per group, groups per descriptor block, blocks per group, and blocks per descriptor block.
- Uses `struct nilfs_palloc_group_desc` on disk to track free-entry counts per group.
- Uses bitmap blocks for allocation state and entry blocks for the actual persistent records.
- `struct nilfs_palloc_req` carries allocation/free transaction state: entry number plus held descriptor, bitmap, and entry buffers.
- `struct nilfs_palloc_cache` stores last-used descriptor, bitmap, and entry buffer heads behind a spinlock.

Major logic:
- `nilfs_palloc_init_blockgroup()` allocates block-group locks, sets metadata entry sizing, and computes per-group/per-descriptor geometry.
- Block-offset helpers map an entry number to group number, descriptor block, bitmap block, and entry block.
- `nilfs_palloc_get_block()` provides cached metadata block lookup/creation with optional block initialization and safe cache replacement.
- Descriptor blocks are initialized so each group starts with all entries free.
- Allocation scans descriptor groups from a target entry, optionally wraps, skips full groups, maps bitmap blocks, atomically sets a free bit, decrements descriptor free count, and returns held buffers for commit/abort.
- Commit allocation marks bitmap/descriptor buffers dirty, marks the metadata file dirty, and releases buffers.
- Commit/abort free and abort allocation clear bitmap bits atomically, warn on double-free, adjust descriptor free counts, and release buffers.
- `nilfs_palloc_freev()` bulk-frees sorted entries by group, clears bits, detects empty entry blocks for deletion, updates group free counts, deletes bitmap blocks when a group becomes fully free, and logs cleanup warnings.
- `nilfs_palloc_count_max_entries()` derives maximum describable entries from existing descriptor blocks, with growth allowance when current usage exactly reaches capacity.
- Cache setup/clear/destroy install and release last-buffer references.

Concurrency and lifetime:
- Per-cache spinlock protects cached buffer-head pointers.
- Per-group block-group locks protect descriptor free counts and bitmap bit operations.
- Buffer heads acquired in prepare calls are intentionally retained in request structs until commit or abort.
- Folio mappings use `kmap_local_folio()`/`kunmap_local()` around descriptor/bitmap mutation.
- Metadata buffers are marked dirty and the metadata inode is marked dirty only on committed changes.

Important dependencies:
- Uses NILFS metadata-file APIs from `mdt.h`, bmap lookup for descriptor counts, and ext2-style atomic little-endian bit operations.
- Supplies allocation services consumed by DAT, ifile, and bmap pointer-management helpers.

Risk/edge cases:
- Double-free or aborting an already freed entry is detected by bitmap clear failure and logged as a warning.
- Empty entry/bitmap block deletion failures are warned but nonfatal for `-ENOENT`.
- Descriptor-count logic can return `-ERANGE` if recorded used entries exceed describable capacity.
- The code notes descriptor block initialization does not support block size greater than page size.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/alloc.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/alloc.h

Purpose: declares NILFS2 persistent allocator APIs, request/cache structures, and bitmap helper aliases.

Key structures and state:
- `nilfs_palloc_entries_per_group()` computes entries per group as the number of bits representable by one bitmap block.
- `struct nilfs_palloc_req` holds an entry number and the descriptor/bitmap/entry buffer heads needed across prepare/commit/abort phases.
- Bitmap operations are aliased to ext2 atomic bit helpers and little-endian bit scanning helpers.
- `struct nilfs_bh_assoc` pairs a metadata block offset with a cached buffer head.
- `struct nilfs_palloc_cache` contains a spinlock and cached descriptor, bitmap, and entry block associations.

Major logic:
- Declares initialization, entry-block lookup, entry offset calculation, maximum-entry counting, allocation prepare/commit/abort, free prepare/commit/abort, vector free, and cache lifecycle functions.
- Defines the split transaction model used by callers that need to prepare metadata changes before committing them to the log.

Concurrency and lifetime:
- Request buffer heads are owned by callers between prepare and commit/abort.
- Cache buffer-head references are protected by `nilfs_palloc_cache.lock` and released on clear/destroy.

Important dependencies:
- Includes Linux types, buffer-head, and fs headers.
- Used by NILFS DAT, ifile, bmap, and metadata-file code.

Risk/edge cases:
- Callers must match every prepare with exactly one commit or abort to avoid leaked buffer references or stale bitmap changes.
- Entry offset calculations depend on metadata inode entry-size initialization.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/bmap.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/bmap.c

Purpose: implements the common NILFS2 block-map wrapper that sits above direct and btree mapping backends. It handles lookup, insert, delete, truncate, dirty propagation, block assignment, conversion between direct and btree formats, DAT virtual-block translation, and bmap initialization/save/restore.

Key structures and state:
- `struct nilfs_bmap` stores raw inode bmap data, an rwsem, owner inode, operation table, last allocation target key/ptr, pointer type, dirty state, and children-per-block geometry.
- Operation dispatch uses `struct nilfs_bmap_operations` supplied by direct or btree implementations.
- Pointer type controls whether records are physical block numbers, single-version virtual block numbers, multi-version virtual block numbers, or unmanaged GC pointers.
- Static lockdep classes distinguish DAT bmap locking from metadata-file bmap locking.

Major logic:
- `nilfs_bmap_lookup_at_level()` dispatches backend lookup and, for virtual-block bmaps, translates the virtual block through DAT to a physical block; missing DAT entries are treated as bmap corruption.
- Insert checks whether a direct map must convert to btree, gathers existing direct data, calls btree conversion/insert, and sets the `NILFS_BMAP_LARGE` flag on success.
- Delete checks whether a btree can convert back to direct, gathers btree data, performs delete/convert, and clears the large flag on success.
- Truncate repeatedly deletes the current last key until all keys greater than or equal to the cutoff are gone.
- Clear, propagate, dirty-buffer lookup, assign, mark, seek-key, and last-key all delegate to backend operations under appropriate locking.
- Dirty state is tested and cleared atomically under the bmap write semaphore.
- Target helpers derive sequential allocation guesses from the last allocated key/ptr or distribute targets by inode number within a DAT allocation group.
- `nilfs_bmap_read()` initializes bmap raw data from an on-disk inode, sets pointer type based on special inode number, initializes lockdep class, and selects direct versus btree backend from the on-disk large flag.
- `nilfs_bmap_write()` copies bmap raw data back to the on-disk inode and resets DAT allocation target state.
- GC bmaps are initialized as unmanaged btree-style maps with pointer type `NILFS_BMAP_PTR_U`.
- Save/restore copies raw bmap data plus allocation target and dirty state into/from a shadow store.

Concurrency and lifetime:
- Read operations take `b_sem` for read; mutating operations take it for write.
- Backend conversion and mutation are serialized by the common bmap semaphore.
- Dirty-buffer lookup intentionally calls the backend without taking the common semaphore in this wrapper.
- Error conversion reports `-EINVAL` as filesystem corruption and maps it to `-EIO`.

Important dependencies:
- Depends on NILFS direct maps, btrees, DAT translation, btnode, allocator, metadata files, and core NILFS inode/superblock structures.
- Supplies the mapping layer used by NILFS regular files and metadata files.

Risk/edge cases:
- A bmap record whose virtual block has no DAT translation is treated as corrupted metadata.
- Direct/tree conversion thresholds must match constants in `bmap.h`, direct, and btree code.
- Last-key-driven truncate can be expensive for large maps but preserves backend invariants.
- Pointer-type selection for special metadata inodes is central to correct DAT versus metadata behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/bmap.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/bmap.h

Purpose: defines NILFS2 block-map data structures, operation table, pointer allocation helpers, dirty-state helpers, conversion thresholds, and public bmap APIs.

Key structures and state:
- `union nilfs_bmap_ptr_req` represents either a raw pointer or a persistent allocator request for DAT-backed virtual block allocation.
- `struct nilfs_bmap_stats` records created/deleted block counts.
- `struct nilfs_bmap_operations` defines backend callbacks for lookup, contiguous lookup, insert/delete, clear, dirty propagation, dirty-buffer collection, disk block assignment, mark, seek/last key, and private conversion checks/data gathering.
- `struct nilfs_bmap` is the in-memory mapping object with raw on-disk payload, rwsem, owner inode, backend ops, allocation target cache, pointer type, state flags, and node fanout.
- Pointer types distinguish physical, single-version virtual, multi-version virtual, and unmanaged pointer handling.
- `struct nilfs_bmap_store` is a shadow copy used to save/restore bmap raw data, allocation target, and dirty state.

Major logic:
- Declares the public bmap API for lookup, contiguous lookup, insert, delete, truncate, clear, propagate, dirty-buffer lookup, assign, mark, initialization, read/write, GC initialization, save, and restore.
- Inline pointer helpers prepare/commit/abort DAT-backed virtual pointer allocation/end operations, or update local sequential physical allocation state when no DAT is used.
- `nilfs_bmap_set_target_v()` stores a preferred virtual allocation target.
- Dirty helpers test, set, and clear `NILFS_BMAP_DIRTY` under the assumption the bmap semaphore is already locked.
- Defines direct-vs-btree size thresholds: small direct key range and large btree key range.

Concurrency and lifetime:
- Comments require callers of dirty helpers to hold the bmap semaphore.
- Pointer allocation helpers must be paired with commit/abort just like allocator requests.
- DAT-backed helpers pass through to DAT transaction APIs and respect single-version versus multi-version end semantics.

Important dependencies:
- Includes NILFS on-disk format definitions, allocator, and DAT APIs.
- Used by direct, btree, metadata, inode, segment, and garbage-collection code.

Risk/edge cases:
- `NILFS_BMAP_NEW_PTR_INIT` uses the high bit of `unsigned long`; pointer arithmetic must preserve the “new pointer” marker behavior.
- Mixing pointer types would corrupt metadata because physical and virtual pointer lifecycles differ.
- Conversion constants must stay consistent with direct and btree backend capacities.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/bmap.h -->