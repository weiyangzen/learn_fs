# Group Research: group_792_linux_sources_os_linux_linux_fs_nfsd_trace_h_sources_os_linux_linux__661d55244fa7

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`.

This grouped report covers NFSD trace/VFS/XDR interfaces and NILFS2 allocator/block-map files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/trace.h -->
# File Research: sources/os/linux/linux/fs/nfsd/trace.h

`trace.h` defines the Linux tracepoint surface for the in-kernel NFS server (`TRACE_SYSTEM nfsd`). It is observability infrastructure, not request processing logic. It includes SUNRPC/NFS trace helpers plus local NFSD headers for exports, filehandles, state, filecache, VFS, and duplicate-reply cache types.

Major trace families:
- XDR failures: `nfsd_garbage_args_err`, `nfsd_cant_encode_err`.
- Dynamic thread pool events: start, kill, trylock failure, with net namespace, pool id, and thread limits.
- NFSv4 compound operation lifecycle: compound start, status, decode errors, op/encode errors.
- Filehandle/export lookup: `nfsd_fh_verify`, `nfsd_fh_verify_err`, export key/name update/find events.
- I/O: read/write/commit start, splice/vector/direct paths, I/O completion, and read/write error events.
- State management: stateid, state sequence id, stateid revocation, clientid lifecycle, grace period, session slot and sequence status.
- File cache: allocation, acquisition, open/opened, cache hits, fsnotify events, LRU/GC/shrinker activity, close.
- DRC: duplicate reply cache found and checksum mismatch.
- NFSv4 callback channel: setup, state transitions, queue/restart/destroy, sequence status, recall, notify-lock, offload, recall-any and callback completion.
- Control plane: procfs/control operations such as unlock, filehandle, threads, pool threads, protocol versions, ports, block size, grace time, recoverydir, and fh key setting.
- Server-side copy and pNFS: inter/intra/async copy, async completion/cancel, VFS clone errors, pNFS fence errors.
- NFSD VFS entry points: setattr, lookup, create, symlink, link, unlink, rename, readdir, getattr/statfs.

Notable implementation patterns:
- Shared macros (`NFSD_TRACE_PROC_CALL_FIELDS`, `NFSD_TRACE_PROC_RES_FIELDS`) standardize xid, net namespace inode, server/client sockaddr, and status capture.
- Display helpers translate internal bitmasks such as `NFSD_MAY_*`, file types, slot flags, callback state/opcode, auth flavor, DRC result, and stateid status into readable trace output.
- Several tracepoints deliberately avoid dereferencing potentially unsafe pointers in print paths and record hashes or raw pointer values instead.
- Conditional trace events suppress noise when request context is unavailable or there is no error/status flag.

This file is central for debugging NFSD request flow, state lifetime, file cache behavior, VFS operations, server-side copy, and callback behavior without changing NFSD execution logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/vfs.c -->
# File Research: sources/os/linux/linux/fs/nfsd/vfs.c

`vfs.c` implements NFSD’s bridge from NFS protocol operations to Linux VFS operations. It handles NFS-specific permission semantics, filehandle/export traversal, metadata updates, file open/read/write/commit paths, namespace mutations, directory iteration, stats, xattrs, and case-folding queries.

Key responsibilities:
- Error conversion: `nfserrno()` maps negative Linux errnos to network-order NFS status values and warns on unexpected errors.
- Lookup and mount traversal: `nfsd_cross_mnt()`, `follow_to_parent()`, `nfsd_lookup_parent()`, `nfsd_mountpoint()`, `nfsd_lookup_dentry()`, and `nfsd_lookup()` implement export-aware component lookup, parent lookup, V4ROOT behavior, junction detection, crossmount/nohide semantics, and filehandle composition.
- Attribute changes: `nfsd_setattr()` sanitizes attrs, handles guard time, splits size changes from other changes, retries delegation conflicts, applies security labels and POSIX ACLs, fills weak cache consistency attrs, and commits sync exports.
- NFSv4 helpers: `nfsd4_is_junction()` detects trusted junction xattrs; `nfsd4_clone_file_range()`, `nfsd_copy_file_range()`, and `nfsd4_vfs_fallocate()` implement v4.2 clone/copy/allocate paths with verifier reset on durable-storage errors.
- Access/open: access maps translate NFSv3/v4 ACCESS bits to `NFSD_MAY_*`; `nfsd_open_break_lease()`, `__nfsd_open()`, `nfsd_open()`, and `nfsd_open_verified()` enforce permissions, leases, append-only checks, stale-open retry, and security post-open hooks.
- Reads: supports splice reads when safe, iterator reads otherwise, and aligned direct reads when configured and possible. GSS integrity/privacy disables splice to avoid reply MIC races.
- Writes: `nfsd_vfs_write()` handles stable/unstable writes, direct/dontcache/buffered modes, write verifier copying/reset, local throttling, writeback error checks, fsnotify, stats, and NFSv2 write-gather behavior.
- Commit: `nfsd_commit()` syncs requested byte ranges and returns/reset write verifiers according to export sync policy.
- Namespace mutation: create, symlink, link, rename, unlink all fill pre/post attrs, acquire write access, use VFS helpers, commit metadata, and translate NFSv4 object-open busy errors specially.
- Readdir: buffers directory entries into a page to avoid lookup recursion/deadlocks from filldir callbacks, then feeds protocol encoders.
- Xattrs: v4 get/list/set/remove xattr helpers use VFS xattr APIs, inode locking, size probing/allocation, WCC attrs, and special xattr error mapping.
- Permissions: `nfsd_permission()` layers export read-only checks, immutable/append handling, owner override, local device access quirks, and inode permission checks.
- Case info: `nfsd_get_case_info()` probes `vfs_fileattr_get()` under kernel credentials and reports POSIX defaults when unsupported.

Notable dependencies include `filecache.h`, `nfsfh.h`, `export.h`, `xdr3.h`, `xdr4.h`, Linux VFS, xattr, fsnotify, writeback, security, and SUNRPC XDR support. The file is heavily instrumented by `trace.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/vfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/vfs.h -->
# File Research: sources/os/linux/linux/fs/nfsd/vfs.h

`vfs.h` is the public internal header for NFSD VFS helpers implemented mainly in `vfs.c`. It defines permission/open flags, attribute wrapper state, the readdir callback type, and prototypes used by protocol operation handlers.

Important definitions:
- `NFSD_MAY_*` flags mirror Linux `MAY_EXEC`, `MAY_WRITE`, and `MAY_READ` for the low bits, then add NFSD-specific policy hints: setattr, truncation, NLM, owner override, local access, GSS bypass variants, lease-breaking suppression, read-if-exec, 64-bit readdir cookies, and localio tracing.
- `NFSD_MAY_CREATE` and `NFSD_MAY_REMOVE` combine the permission bits required for namespace mutation.
- `nfsd_filldir_t` is the callback ABI used by `nfsd_readdir()` to feed protocol-specific directory encoders.
- `struct nfsd_attrs` packages requested `iattr`, security label, POSIX access/default ACLs, and per-attribute error outputs.
- `nfsd_attrs_free()` releases ACL references; `nfsd_attrs_valid()` reports whether any regular attribute, label, or ACL update is pending.

The header declares lookup, setattr, create, access, open, read/write/commit, readlink/symlink/link/rename/unlink/readdir/statfs, permission, case-info, copy range, file close, and NFSv4-only fallocate/clone/xattr helpers. It is the main contract between NFSD protocol dispatch and the Linux VFS adaptation layer.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/vfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/xdr.h -->
# File Research: sources/os/linux/linux/fs/nfsd/xdr.h

`xdr.h` defines NFSv2 server-side XDR argument/result storage types and encoder/decoder prototypes. It is primarily a type contract between the NFSv2 RPC dispatch layer and XDR implementation code.

Core request structures include filehandle-only, setattr, dirop, read, write, create, rename, link, symlink, and readdir arguments. Result structures include simple status, attrstat, diropres, readlinkres, readres, readdirres, and statfsres.

`union nfsd_xdrstore` provides per-request scratch storage sized by `NFS2_SVC_XDRSIZE`. This lets the RPC service layer allocate enough argument/result memory without knowing each procedure’s specific type.

The header declares:
- NFSv2 decoders: fhandle, sattr, dirop, read, write, create, rename, link, symlink, readdir.
- NFSv2 encoders: stat, attrstat, diropres, readlink, read, statfs, readdir.
- Directory cookie and entry encoders.
- Release callbacks for responses holding filehandles or pages.
- Common helper functions for NFSv2 ACL code: filehandle decode, status encode, and fattr encode.

The structures retain NFSv2 constraints, such as 32-bit read/write offsets and simple directory cookies.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/xdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/xdr3.h -->
# File Research: sources/os/linux/linux/fs/nfsd/xdr3.h

`xdr3.h` defines NFSv3 server-side XDR argument/result structures and encoder/decoder prototypes. It builds on `xdr.h` and adds NFSv3 features: 64-bit offsets, weak cache consistency filehandles, access checks, commit, create modes/verifiers, mknod, readdirplus, filesystem info/pathconf, and POSIX ACL procedure storage.

Important argument types:
- `nfsd3_sattrargs` includes guard-time checking.
- Read/write/commit use 64-bit offsets.
- Create includes create mode and verifier pointer.
- Mknod carries file type plus major/minor.
- Readdir carries 64-bit cookie, count, and verifier.
- ACL get/set arguments include masks and POSIX ACL pointers.

Important response types:
- Attr, dirop, access, readlink, read, write, rename, link, readdir, fsstat, fsinfo, pathconf, commit, and getacl result structures.
- `nfsd3_readdirres` carries an XDR stream, dirlist buffer, scratch filehandle for readdirplus, common readdir callback state, cookie offset, and request pointer.
- `nfsd3_fhandle_pair` is a release-helper dummy wrapper for two filehandles.

`union nfsd3_xdrstore` centralizes scratch storage and `NFS3_SVC_XDRSIZE` exposes its size to the service layer.

The prototype set covers all NFSv3 procedure decoders/encoders, release callbacks, cookie/entry/readdirplus encoders, and helper functions for ACL XDR support. This header is the ABI between NFSv3 RPC procedure dispatch and the XDR encode/decode implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/xdr3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/xdr4.h -->
# File Research: sources/os/linux/linux/fs/nfsd/xdr4.h

`xdr4.h` is the main NFSv4 server-side operation type header. It defines compound request/response state, per-operation argument/result structures, inline XDR encode helpers, operation dispatch metadata, state/session prototypes, and v4.1/v4.2 extension types.

Key elements:
- Encoding helpers: inline bool, uint32, uint64, fixed opaque, and variable opaque encoders return `nfs_ok` or `nfserr_resource`.
- `struct nfsd4_compound_state` tracks current/saved filehandles, replay owner, client, session/slot, data offset, iov count, minor version, status, current/saved stateids, and stateid presence flags.
- `struct nfsd4_op` stores op number, status, descriptor, replay info, and a large union of every v4 operation’s decoded state.
- `struct nfsd4_compoundargs` and `struct nfsd4_compoundres` are the XDR decode/encode scratch objects used per compound.
- `enum nfsd4_op_flags` describes operation constraints: no filehandle required, absent filesystem allowed, first-op-only, wrongsec handling, PUTFH-like, modifies something, DRC cache eligibility, stateid clearing, and nontrivial error encoding.
- `struct nfsd4_operation` binds an op implementation to release, flags, name, reply-size estimator, and current-stateid accessors.

Covered operation families:
- Base v4: access, close, commit, create, delegreturn, getattr, link, lock/lockt/locku, lookup, open/open-confirm/open-downgrade, putfh, read, readdir, readlink, remove, rename, secinfo, setattr, setclientid, verify/nverify, write, release lockowner.
- v4.1/session/pNFS: exchange_id, backchannel_ctl, bind_conn_to_session, create/destroy session, destroy clientid, sequence, reclaim_complete, test/free stateid, directory delegation, getdeviceinfo, layoutget/commit/return, secinfo_no_name.
- v4.2: allocate/deallocate, clone, copy, offload status, copy notify, seek, and xattr get/set/list/remove.

Notable structures include `nfsd4_open`, `nfsd4_readdir` with case-attribute cache, layout/deviceid helpers, copy/offload structures with async state and callback result fields, and NFSv4 callback recall-any data.

This header is a dense protocol contract: it does not execute operations, but it defines the data shape and dispatch hooks used by NFSv4 decode, operation processing, state management, and encode paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/xdr4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/xdr4cb.h -->
# File Research: sources/os/linux/linux/fs/nfsd/xdr4cb.h

`xdr4cb.h` defines static XDR size estimates for NFSv4 callback requests and replies. These constants are used by callback encode/decode paths to size RPC buffers for backchannel operations.

The file defines:
- Compound callback header sizes and max callback tag length.
- Sessionid and referring-call list word sizes for `CB_SEQUENCE`.
- Common op encode/decode sizes.
- Filehandle and stateid encoded sizes.
- Per-callback size macros for `CB_RECALL`, `CB_LAYOUTRECALL`, `CB_NOTIFY_LOCK`, `CB_OFFLOAD`, `CB_RECALL_ANY`, and `CB_GETATTR`.

The comments for `CB_GETATTR` document the exact expected fields: opcode, filehandle, attribute bitmap array, fattr length, change, size, atime, and mtime components. The header is purely declarative and depends on NFSv4 constants such as `NFS4_MAX_SESSIONID_LEN`, `NFS4_FHSIZE`, `NFS4_STATEID_SIZE`, `NFS4_OPAQUE_LIMIT`, and `NFS4_VERIFIER_SIZE`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/xdr4cb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/Kconfig -->
# File Research: sources/os/linux/linux/fs/nilfs2/Kconfig

`Kconfig` declares `CONFIG_NILFS2_FS`, a tristate option named “NILFS2 file system support”. It selects `BUFFER_HEAD`, `CRC32`, and `LEGACY_DIRECT_IO`.

The help text describes NILFS2 as a log-structured filesystem with continuous snapshotting, checkpoint creation every few seconds or on synchronous writes, promotion of checkpoints into long-lived read-only snapshots, crash-consistent recovery, and concurrent read-only snapshot mounts for online backup.

The help also records feature limitations in this tree: atime, extended attributes, and POSIX ACLs are not supported yet. When built as a module, the module name is `nilfs2`; the default recommendation is `N` if unsure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/Makefile -->
# File Research: sources/os/linux/linux/fs/nilfs2/Makefile

The NILFS2 `Makefile` builds `nilfs2.o` when `CONFIG_NILFS2_FS` is enabled. The composite object includes core inode/file/directory/superblock/name/page metadata code, block tree/direct mapping components, DAT/recovery, segment construction, checkpoint/sufile/ifile allocators, garbage-collection inode support, ioctl, and sysfs support.

Files listed into `nilfs2-y` include this group’s `alloc.o` and `bmap.o`, placing the persistent allocator and block mapping layer in the core NILFS2 module.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/alloc.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/alloc.c

`alloc.c` implements NILFS2’s persistent object allocator used for DAT entries and disk inode allocation. It manages grouped metadata files consisting of descriptor blocks, bitmap blocks, and entry blocks.

Core layout helpers:
- `nilfs_palloc_entries_per_group()` is defined in the header; this file adds group count, groups per descriptor block, group/offset calculation, descriptor block offset, bitmap block offset, and entry block offset.
- `nilfs_palloc_init_blockgroup()` allocates block-group locks, configures metadata entry size, computes blocks per group, and computes blocks per descriptor block.
- Descriptor initialization fills each group descriptor’s free-entry count.

Buffer/cache handling:
- `nilfs_palloc_get_block()` caches the last descriptor, bitmap, and entry block through `nilfs_palloc_cache`, protected by a spinlock.
- Delete helpers invalidate matching cached buffers before deleting metadata blocks.
- Public `nilfs_palloc_get_entry_block()` locates an entry’s data block.
- Offset helpers compute descriptor, bitmap, and entry byte offsets within folios.

Allocation flow:
- `nilfs_palloc_prepare_alloc_entry()` scans descriptor blocks and group bitmaps from the requested entry number, optionally wrapping, atomically sets a free bit, decrements descriptor free count, and returns pinned descriptor/bitmap buffers in `nilfs_palloc_req`.
- `nilfs_palloc_commit_alloc_entry()` dirties descriptor/bitmap buffers, marks the metadata inode dirty, and releases buffers.
- `nilfs_palloc_abort_alloc_entry()` clears the allocated bit, increments free count, releases buffers, and resets request fields.

Free flow:
- `nilfs_palloc_prepare_free_entry()` pins descriptor and bitmap buffers for an entry.
- `nilfs_palloc_commit_free_entry()` clears the bit atomically, warns if already free, increments the descriptor free count, dirties buffers, marks metadata dirty, and releases buffers.
- `nilfs_palloc_abort_free_entry()` releases buffers without changing bitmap state.
- `nilfs_palloc_freev()` batch-frees sorted entries, deletes now-empty entry blocks, updates descriptor free counts, and deletes empty bitmap blocks when an entire group becomes free.

Capacity/cache:
- `nilfs_palloc_count_max_entries()` derives maximum allocatable entries from current descriptor blocks and possible metadata growth.
- Setup/clear/destroy cache functions attach and release the per-inode allocator cache.

Important risks/semantics: allocation is a prepare/commit/abort protocol; callers must complete the transaction correctly. Bitmap mutation uses ext2 little-endian atomic bit operations, while descriptor free counts are protected by per-group locks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/alloc.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/alloc.h

`alloc.h` declares NILFS2’s persistent allocator interface and cache structures.

Key API:
- `nilfs_palloc_entries_per_group()` computes entries per group from inode block size: one bitmap block worth of bits.
- Initialization, entry-block lookup, entry offset, and maximum-entry counting functions.
- `struct nilfs_palloc_req` carries the requested/allocated entry number plus descriptor, bitmap, and entry buffer heads used by prepare/commit/abort operations.
- Allocation/free transaction functions: prepare/commit/abort allocation, prepare/commit/abort free, and batch free.
- Bit operation aliases bind NILFS allocation bitmaps to ext2 atomic little-endian bit operations and Linux little-endian find-bit helpers.
- `struct nilfs_bh_assoc` stores a cached block offset and buffer head.
- `struct nilfs_palloc_cache` holds cached descriptor, bitmap, and entry buffers protected by a spinlock.

The header exposes setup, clear, and destroy helpers for attaching allocator caches to NILFS metadata inodes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/bmap.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/bmap.c

`bmap.c` implements the common NILFS2 block mapping layer. It wraps direct and B-tree mapping implementations behind `nilfs_bmap_operations`, handles conversion between small direct maps and large B-trees, translates virtual block numbers through DAT, serializes operations with the bmap semaphore, and normalizes corruption errors.

Core behavior:
- `nilfs_bmap_get_dat()` returns the filesystem DAT inode.
- `nilfs_bmap_convert_error()` turns internal `-EINVAL` corruption signals into `-EIO` after reporting a broken bmap with inode number.
- Lookup functions call the active mapping operation under read lock. `nilfs_bmap_lookup_at_level()` also translates virtual block numbers to physical block numbers through DAT and treats missing DAT entries as corruption.
- Insert/delete functions call check hooks that can trigger representation conversion: direct-to-B-tree on insert growth, B-tree-to-direct on delete shrink.
- `nilfs_bmap_truncate()` repeatedly deletes the last key until all keys at or above the requested key are gone.
- Clear, propagate, dirty-buffer lookup, assign, and mark delegate to operation-table hooks under appropriate locking.
- Dirty state is tested and cleared atomically with the write lock.
- `nilfs_bmap_data_get_key()` maps a buffer head position back to a bmap key.
- Target selection helpers use sequential locality or inode-number-derived DAT group locality.

Initialization:
- `nilfs_bmap_read()` loads raw on-disk bmap data, initializes locking/state, selects pointer type by metadata inode number, assigns lockdep classes for DAT/metadata bmaps, and initializes either B-tree or direct mode based on the `NILFS_BMAP_LARGE` flag.
- DAT uses physical pointers; checkpoint/sufile use single-version virtual pointers; ifile and regular files use multi-version virtual pointers.
- `nilfs_bmap_write()` copies the in-memory bmap back to the raw inode and resets DAT’s last allocated pointer marker.
- `nilfs_bmap_init_gc()` initializes a GC-only bmap with pointer operations disabled and B-tree GC ops.
- Save/restore copies raw data, last allocation hints, and dirty state.

This file is the polymorphic control layer for NILFS block addressing and metadata relocation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/bmap.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/bmap.h

`bmap.h` defines NILFS2 block mapping data structures, operation tables, pointer types, dirty state helpers, and public bmap APIs.

Important structures:
- `union nilfs_bmap_ptr_req` wraps either a raw bmap pointer or a persistent allocator request.
- `struct nilfs_bmap_stats` tracks block creation/deletion counts.
- `struct nilfs_bmap_operations` is the polymorphic interface implemented by direct and B-tree backends. It includes lookup, contiguous lookup, insert, delete, clear, propagate, dirty-buffer collection, block assignment, GC marking, seek/last-key, and private conversion helper hooks.
- `struct nilfs_bmap` stores raw on-disk mapping data, an rw semaphore, owner inode, operation table, last allocated key/ptr hints, pointer type, state flags, and child capacity.
- `struct nilfs_bmap_store` is a snapshot used for save/restore of raw mapping data and allocation/dirty state.

Pointer modes:
- `NILFS_BMAP_PTR_P`: physical block number.
- `NILFS_BMAP_PTR_VS`: virtual block number, single version.
- `NILFS_BMAP_PTR_VM`: virtual block number, multiple versions.
- `NILFS_BMAP_PTR_U`: pointer operations disabled.
- `NILFS_BMAP_USE_VBN()` identifies virtual pointer modes.

Inline helpers:
- New-pointer marker detection.
- Normal lookup at level 1.
- Prepare/commit/abort allocation and end-of-life pointer handling, delegating to DAT when present or manipulating local allocation hints otherwise.
- Target-virtual-pointer hint update.
- Dirty-state test/set/clear helpers, assuming the bmap semaphore is held.

Constants define the inline bmap storage size, dirty flag, small/direct and large/B-tree key ranges, and conversion threshold flag. This header is the common contract used by NILFS direct, B-tree, DAT, metadata, and GC code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/bmap.h -->