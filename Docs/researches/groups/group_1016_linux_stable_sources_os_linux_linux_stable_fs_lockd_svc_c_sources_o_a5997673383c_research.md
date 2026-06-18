# Group Research: group_1016_linux_stable_sources_os_linux_linux_stable_fs_lockd_svc_c_sources_o_a5997673383c

Scope: `Docs/research_subset_a.md`; all listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svc.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/svc.c

## Summary
Central lockd service lifecycle and RPC program registration. It owns the singleton `svc_serv`, per-network-namespace lockd users, listener creation for UDP/TCP IPv4/IPv6, grace-period scheduling, module/sysctl parameters, generic netlink get/set of server settings, and common RPC dispatch.

## Main APIs
- `lockd_up()` / `lockd_down()` export global service reference management.
- `lockd()` is the service thread loop, retrying blocked NLM requests then calling `svc_recv()`.
- `lockd_up_net()` / `lockd_down_net()` bind and tear down per-net listeners and grace state.
- `nlmsvc_dispatch()` decodes, invokes, and encodes each `svc_procedure`.
- `lockd_nl_server_set_doit()` / `lockd_nl_server_get_doit()` expose per-net grace time and ports via netlink.

## Behavior
`lockd_get()` lazily creates the `svc_serv`, starts one service thread, registers address notifiers, and computes RPC buffer size from supported NLM versions. Per-net startup binds the service, creates UDP/TCP listeners, then starts a VFS lock grace period. Shutdown unwinds host state, delayed grace work, xprts, notifier registration, retry timer, and service threads.

## State and Synchronization
`nlmsvc_mutex` serializes service lifetime. Global `nlmsvc_users` and per-net `ln->nlmsvc_users` gate teardown. Grace handling uses `lockd_net.grace_period_end` delayed work and VFS `locks_start_grace()` / `locks_end_grace()`.

## Dependencies
SunRPC server APIs, network namespace storage, lockd host/resource management, procfs, generic netlink, sysctl, IPv4/IPv6 address notifiers, and NFS server binding callbacks through `nlmsvc_ops`.

## Risks
Service lifetime is split between global and per-net reference counts; mismatches can destroy xprts or the service while users remain. Callback procedures intentionally bypass early `svc_set_client()` and rely on individual procedures to look up hosts. Grace-period and listener port changes are per-net, but init-net updates also mirror legacy globals.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svc4proc.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/svc4proc.c

## Summary
NLMv4 server procedure implementation. It adapts generated `nlm4xdr_gen.h` types into legacy lockd `nlm_lock`, `nlm_cookie`, and `nlm_res` machinery, then wires all NLMv4 procedures into `nlmsvc_version4`.

## Main APIs
Procedures include `NULL`, `TEST`, `LOCK`, `CANCEL`, `UNLOCK`, `GRANTED`, async `*_MSG` callback forms, `GRANTED_RES`, `SM_NOTIFY`, `SHARE`, `UNSHARE`, `NM_LOCK`, and `FREE_ALL`.

## Behavior
Helper wrappers keep generated XDR structs first so RPC dispatch can cast them directly. `nlm4svc_lookup_host()` resolves callers and optionally starts NSM monitoring. `nlm4svc_lookup_file()` validates NFS file handle length and 64-bit lock range, opens a lockd file, fills VFS `file_lock`, and attaches lock-manager operations. Sync calls return encoded replies; async `*_MSG` procedures allocate an `nlm_rqst` and send callback replies with `nlm_async_reply()`.

## State and Data Flow
NLMv4 offsets and lengths are preserved as 64-bit values and mapped into `file_lock` ranges. Cookies are copied into fixed `NLM_MAXCOOKIELEN` storage for callback correlation. Share procedures synthesize a lock with `LOCKD_SHARE_SVID` and delegate conflict checks to `svcshare.c`.

## Dependencies
Generated NLMv4 XDR codecs, lockd host/file/NSM logic, `nlmsvc_lock()`, `nlmsvc_testlock()`, `nlmsvc_unlock()`, `nlmsvc_cancel_blocked()`, share helpers, and client grant callback handling.

## Risks
Range validation must reject wraparound beyond `OFFSET_MAX`. Every path that initializes an NLM lock owner must release it exactly once. Async callbacks take ownership of host references. V4-specific status mapping includes `nlm4_deadlock`, `nlm4_fbig`, `nlm4_stale_fh`, and `nlm4_failed`, unlike v1/v3.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svc4proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svclock.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/svclock.c

## Summary
Server-side lock state and blocked-lock retry machinery. This is the main race-prone lockd file: it manages pending blocks, lock owners, VFS async lock callbacks, deferred RPC revisits, GRANTED_MSG retransmission, and GRANTED_RES cleanup.

## Main APIs
- `nlmsvc_lock()`, `nlmsvc_testlock()`, `nlmsvc_unlock()`, `nlmsvc_cancel_blocked()`.
- `nlmsvc_retry_blocked()` drives retry and deferred-request processing from the lockd thread.
- `nlmsvc_grant_reply()` handles client `GRANTED_RES`.
- `nlmsvc_locks_init_private()` and `nlmsvc_release_lockowner()` manage NLM lock owners.
- `nlmsvc_lock_operations` supplies VFS lock-manager callbacks.

## Behavior
Blocking lock requests are represented by `struct nlm_block` on a global time-ordered `nlm_blocked` list and on each file’s block list. If VFS grants immediately, the block is removed. If VFS blocks or defers, lockd stores the request, sleeps or drops the RPC reply, and later sends a `GRANTED_MSG` callback. Client acceptance removes the block; denial unlocks the VFS lock.

## State and Synchronization
`nlm_blocked_lock` protects the global retry list and many block transitions. `file->f_mutex` protects per-file block list teardown. `kref` controls block lifetime. Lock owners are refcounted under `host->h_lock` and are also managed by VFS `lm_get_owner` / `lm_put_owner`.

## Dependencies
Generic VFS locks (`vfs_lock_file()`, `vfs_test_lock()`, `vfs_cancel_lock()`), SunRPC async calls, lockd file and host reference APIs, and the global retry timer in `svc.c`.

## Risks
GRANT, CANCEL, UNLOCK, deferred filesystem callbacks, and RPC completion can cross in flight. `nlmsvc_grant_release()` notes it calls a mutex-taking release path from RPC release context. List movement can cause repeated traversal, which comments accept as benign. Correct lock-owner refcounting is critical because copied VFS locks can retain owners.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svclock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svcproc.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/svcproc.c

## Summary
NLMv1 and NLMv3 server procedures. It is the older hand-written procedure layer over `nlm_args` / `nlm_res`, sharing the same lock core as NLMv4 but with v1/v3 status constraints and legacy XDR.

## Main APIs
Defines sync and async forms of `TEST`, `LOCK`, `CANCEL`, `UNLOCK`, `GRANTED`, `GRANTED_RES`, `SM_NOTIFY`, `SHARE`, `UNSHARE`, `NM_LOCK`, `FREE_ALL`, and procedure tables for `nlmsvc_version1` and `nlmsvc_version3`.

## Behavior
`nlmsvc_retrieve_args()` resolves the caller host, optionally starts NSM monitoring, opens the file in the mode implied by the requested lock, fills missing `file_lock` fields, and installs `nlmsvc_lock_operations`. Procedure handlers delegate to `svclock.c` and `svcshare.c`, then release lock owners, hosts, and files.

## State and Data Flow
`cast_status()` maps internal and v4-ish statuses into values legal for v1/v3. Async `*_MSG` procedures allocate an `nlm_rqst`, run the same underlying operation into its response, then send a callback result before returning a void reply.

## Dependencies
Legacy XDR codecs from `xdr.c`, `nlmsvc_dispatch()` from `svc.c`, lock/share helpers, NSM monitoring, host reboot processing, and SunRPC async reply support.

## Risks
Older protocol versions cannot express all internal failures, so status folding can hide stale file handles or deadlocks. The callback implementation is “async” only in the sense that the callback reply is sent separately; comments note ordering may be surprising to clients.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svcproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svcshare.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/svcshare.c

## Summary
DOS-style NLM share reservation management for lockd files.

## Main APIs
- `nlmsvc_share_file()` creates or updates a share reservation.
- `nlmsvc_unshare_file()` removes a matching reservation.
- `nlmsvc_traverse_shares()` purges shares matching a host predicate.

## Behavior
Shares are stored as a singly linked list on `nlm_file`. A reservation is keyed by host plus owner handle. New shares conflict if requested access intersects an existing share’s deny mode, or requested deny mode intersects an existing share’s access. Existing matching reservations are updated in place. Unshare returns success even when no matching share exists, per X/Open behavior.

## State and Dependencies
Each `struct nlm_share` embeds copied owner-handle bytes immediately after the allocation. The file-level share list is cleaned from `svcsubs.c` resource traversal. Operations first reject files that cannot be locked.

## Risks
The conflict expression is compact and asymmetric by naming: `access & existing mode` or `mode & existing access`. Share list lifetime depends on higher-level lockd serialization/resource traversal; this file itself has no lock.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svcshare.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svcsubs.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/svcsubs.c

## Summary
Support routines for lockd server file tracking and resource reclamation. It maintains the global `nlm_file` hash table, opens/closes backing VFS files through nfsd callbacks, and traverses locks, blocks, and shares for cleanup.

## Main APIs
- `nlm_lookup_file()` maps an NFS file handle to an `nlm_file` and opens read/write backing files.
- `nlm_release_file()` drops references and frees unused file records.
- `nlmsvc_mark_resources()`, `nlmsvc_free_host_resources()`, `nlmsvc_invalidate_all()`.
- `nlmsvc_unlock_all_by_sb()` and `nlmsvc_unlock_all_by_ip()` export bulk unlock operations.

## Behavior
Files are hashed by the first NFSv2 file-handle bytes. `nlm_do_fopen()` tries required open modes via `nlmsvc_ops->fopen()`, translating `-EWOULDBLOCK` to drop-reply, `-ESTALE` to stale-FH, and other errors to failed. Cleanup walks VFS POSIX locks on each inode, lockd blocks, and DOS shares, then closes and frees unused file records.

## State and Synchronization
`nlm_file_mutex` protects the global hash table and file reference count. Each `nlm_file` has `f_mutex` for block-list-sensitive operations. VFS lock lists are inspected under each inode lock context’s `flc_lock`.

## Dependencies
nfsd/lockd binding callbacks, generic VFS lock context APIs, `svclock.c` block traversal, `svcshare.c` share traversal, and RPC address comparison.

## Risks
The comments explicitly avoid normal refcount purity because `fs/locks.c` can split/delete locks without lockd notification. Cleanup therefore relies on repeated global traversal and lock-list inspection. Failure to remove all host locks triggers `BUG()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svcsubs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svcxdr.h -->
# File Research: sources/os/linux/linux-stable/fs/lockd/svcxdr.h

## Summary
Inline helpers for common server-side NLM XDR scalar, cookie, string, and owner-handle encoding/decoding.

## Main APIs
`svcxdr_decode_stats()`, `svcxdr_encode_stats()`, `svcxdr_decode_string()`, `svcxdr_decode_cookie()`, `svcxdr_encode_cookie()`, `svcxdr_decode_owner()`, and `svcxdr_encode_owner()`.

## Behavior
Strings are bounded by `NLM_MAXSTRLEN`. Cookies are specified as up to 1024-byte XDR opaque values, but Linux caps them at `NLM_MAXCOOKIELEN` and maps zero-length HPUX cookies to four zero bytes. Owner handles are bounded by `XDR_MAX_NETOBJ` and generally point directly into the decoded XDR buffer.

## Dependencies
SunRPC `xdr_stream`, `nlm_cookie`, `xdr_netobj`, and lockd constants from `xdr.h`.

## Risks
Decoded string and owner storage aliases the RPC receive buffer, so callers must not outlive the request unless they copy. Cookie length policy is intentionally stricter than the protocol.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/svcxdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/trace.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/trace.c

## Summary
Tracepoint instantiation unit for lockd.

## Behavior
Defines `CREATE_TRACE_POINTS` and includes `trace.h`, causing the trace event declarations in the header to emit storage and registration code in exactly one translation unit.

## Dependencies
Linux tracepoint build conventions and `fs/lockd/trace.h`.

## Risks
This file must remain minimal; adding other includes before trace definitions can affect tracepoint generation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/trace.h -->
# File Research: sources/os/linux/linux-stable/fs/lockd/trace.h

## Summary
Trace event definitions for lockd client-side lock operations.

## Main APIs
Defines status enums and the event class `nlmclnt_lock_event`, then instantiates `nlmclnt_test`, `nlmclnt_lock`, `nlmclnt_unlock`, and `nlmclnt_grant`.

## Behavior
Trace records include sockaddr, owner-handle CRC, server process id, NFS file-handle hash, lock start/length, and symbolic NLM status. Status symbol sets differ when `CONFIG_LOCKD_V4` is enabled.

## Dependencies
Linux tracepoint framework, CRC32, NFS file-handle hashing, and lockd structures.

## Risks
Trace output deliberately hashes handles rather than dumping opaque data. Status decoding must stay aligned with NLM status constants and v4 configuration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/xdr.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/xdr.c

## Summary
Legacy NLM v1/v3 XDR encode/decode support for lockd server procedures.

## Main APIs
Decoders: `nlmsvc_decode_testargs()`, `nlmsvc_decode_lockargs()`, `nlmsvc_decode_cancargs()`, `nlmsvc_decode_unlockargs()`, `nlmsvc_decode_res()`, `nlmsvc_decode_reboot()`, `nlmsvc_decode_shareargs()`, `nlmsvc_decode_notify()`. Encoders: `nlmsvc_encode_testres()`, `nlmsvc_encode_res()`, `nlmsvc_encode_shareres()`, `nlmsvc_encode_void()`.

## Behavior
The old protocol decoder requires NLM file handles to be exactly `NFS2_FHSIZE`, despite protocol text allowing variable opaque handles. Lock ranges use signed 32-bit start/length values, mapped to `loff_t`; zero length or wraparound-style negative end means EOF. Test replies encode a conflicting holder only for denied locks.

## State and Data Flow
Decoded lock owner handles and caller names point into XDR stream memory. Share decoding initializes a synthetic lock with `LOCKD_SHARE_SVID`. Share replies append a zero sequence field.

## Dependencies
`svcxdr.h`, SunRPC XDR streams, NFSv2 file handle sizes, generic VFS `file_lock` initialization, and `xdr.h` structures.

## Risks
The file comments note missing range checks in original share decoding. Offset conversion clamps encoded holder ranges to `NLM_OFFSET_MAX`, so large kernel ranges can be truncated on the wire.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/xdr.h -->
# File Research: sources/os/linux/linux-stable/fs/lockd/xdr.h

## Summary
Shared legacy NLM XDR data types and function prototypes.

## Contents
Defines statd constants, cookie/string limits, NLM status `__be32` constants, `struct nlm_lock`, `struct nlm_cookie`, `struct nlm_args`, `struct nlm_res`, and `struct nlm_reboot`.

## Behavior
`struct nlm_lock` carries both wire-level fields and the in-kernel `struct file_lock`. Cookies are fixed at 32 bytes for Linux interoperability with common clients. `nlm_args` is the common request container for lock, share, notify, and state fields.

## Dependencies
Linux file locks, NFS file handles, and SunRPC XDR.

## Risks
This header is shared by server procedure and XDR code, so field ownership is mixed: some pointers alias XDR buffers, while `file_lock` private state needs explicit release.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/xdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/locks.c -->
# File Research: sources/os/linux/linux-stable/fs/locks.c

## Summary
Generic Linux file-locking core. It implements BSD `flock`, POSIX byte-range locks, open-file-description locks, file leases, delegations/layout leases, lock-manager callbacks, blocking wait trees, deadlock detection, fcntl/flock entry points, cleanup on close, and `/proc/locks`.

## Main APIs
Allocation/copy helpers include `locks_alloc_lock()`, `locks_free_lock()`, `locks_init_lock()`, `locks_copy_lock()`. Lock operations include `posix_lock_file()`, `vfs_test_lock()`, `vfs_lock_file()`, `locks_lock_inode_wait()`, `vfs_cancel_lock()`, `locks_remove_posix()`, `locks_remove_file()`, and `vfs_inode_has_locks()`. Lease APIs include `__break_lease()`, `generic_setlease()`, `vfs_setlease()`, `kernel_setlease()`, `fcntl_setlease()`, and delegation helpers.

## Behavior
Each inode lazily gets a `file_lock_context` containing FLOCK, POSIX/OFD, and lease lists. Applied locks and blocked requests form conflict trees: blockers own child waiters, and wakeups recursively re-evaluate children. POSIX locks are sorted by owner and range, then merged, split, replaced, or deleted as new requests arrive. FLOCK locks conflict by file instance. OFD locks use the file pointer as owner.

## State and Synchronization
Per-inode `flc_lock` protects lock lists. `blocked_lock_lock` protects blocked-request links, blocker pointers, and the POSIX deadlock hash. Per-CPU global lock lists plus `file_rwsem` support `/proc/locks`. Lease break state uses pending flags and timeout fields.

## Dependencies
VFS files/inodes, security hooks, file operation `->lock`, `->flock`, and `->setlease`, pid namespaces, procfs seq files, fasync signaling, sysctl, tracepoints, slabs, wait queues, RCU, and lock-manager operation vectors used by lockd/nfsd.

## Risks
The core relies on strict lock ordering and acquire/release pairing around `flc_blocker`. POSIX deadlock detection is bounded and intentionally skipped for OFD locks. Close/fcntl races are handled by rechecking the fd table and zapping POSIX locks on mismatch. Lease insertion has a required memory barrier before rechecking conflicting opens.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/locks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/mbcache.c -->
# File Research: sources/os/linux/linux-stable/fs/mbcache.c

## Summary
Metadata block cache used by ext2/ext4 xattr deduplication. It is a fixed-size hash-backed key/value cache where keys may collide but key/value pairs are expected unique.

## Main APIs
`mb_cache_create()`, `mb_cache_destroy()`, `mb_cache_entry_create()`, `mb_cache_entry_find_first()`, `mb_cache_entry_find_next()`, `mb_cache_entry_get()`, `mb_cache_entry_delete_or_get()`, `mb_cache_entry_touch()`, `mb_cache_entry_wait_unused()`, and `__mb_cache_entry_free()`.

## Behavior
Entries have hash-list membership, LRU-like list membership, refcount, key, value, and reusable/referenced flags. Creation rejects duplicate key/value pairs and initially holds two refs to avoid nesting list lock under hash bucket bit locks. Searches return reusable entries with live refs. Shrinking drops unreferenced entries, giving referenced entries a second chance by clearing the referenced bit and moving them to the tail.

## State and Synchronization
Hash buckets use `hlist_bl` bit locks. Cache list/count use `c_list_lock`. A shrinker and background work item reclaim entries when counts exceed thresholds.

## Dependencies
Kernel shrinker API, slab cache `mb_cache_entry`, workqueues, list/hash primitives, and exported mbcache helpers used by filesystems.

## Risks
`mb_cache_entry_delete_or_get()` relies on exact refcount value `2` to atomically delete an unused hashed entry. Destroy assumes no external users except the shrinker and warns if entries still have unexpected refs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/mbcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/minix/Kconfig

## Summary
Kconfig entries for Linux Minix filesystem support.

## Contents
`MINIX_FS` is a tristate option depending on block-device support and selecting `BUFFER_HEAD`. Help text describes Minix FS as the original Linux filesystem, now mostly useful for old media or teaching. `MINIX_FS_NATIVE_ENDIAN` and `MINIX_FS_BIG_ENDIAN_16BIT_INDEXED` select endian/index behavior for specific architectures.

## Risks
Endian options are architecture-dependent compatibility switches; incorrect selection would affect on-disk bitmap/index interpretation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/minix/Makefile

## Summary
Build rules for the Minix filesystem module/built-in object.

## Contents
Builds `minix.o` when `CONFIG_MINIX_FS` is enabled. Object composition is `bitmap.o`, `itree_v1.o`, `itree_v2.o`, `namei.o`, `inode.o`, `file.o`, and `dir.o`.

## Dependencies
Kbuild and `CONFIG_MINIX_FS`.

## Risks
The Makefile is straightforward; coverage of this batch includes bitmap, file, and dir but not inode/namei/itree implementation files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/bitmap.c -->
# File Research: sources/os/linux/linux-stable/fs/minix/bitmap.c

## Summary
Minix block and inode bitmap management plus raw inode lookup helpers.

## Main APIs
`minix_free_block()`, `minix_new_block()`, `minix_count_free_blocks()`, `minix_V1_raw_inode()`, `minix_V2_raw_inode()`, `minix_free_inode()`, `minix_new_inode()`, and `minix_count_free_inodes()`.

## Behavior
Block bitmaps mark busy bits as set. Block allocation scans zone maps for the first zero bit, sets it, marks the buffer dirty, and translates bitmap position to disk zone. Freeing validates the data-zone range and clears the bit. Inode allocation scans inode maps, creates a VFS inode, assigns ownership/timestamps/number, clears Minix-private block pointers, inserts into inode hash, and marks dirty. Freeing clears link count and mode in the raw on-disk inode before clearing the bitmap bit.

## State and Synchronization
A global `bitmap_lock` protects bitmap bit operations. Bitmap buffers live in `minix_sb_info` as `s_imap` and `s_zmap`.

## Dependencies
Buffer heads, Minix superblock layout, endian-aware bitops through Minix helpers, VFS inode allocation, and raw V1/V2 inode formats.

## Risks
Allocation can set a bit that later maps outside valid inode/zone ranges, returning corruption/zero after dirtying the bitmap. Error handling relies on old-style printk warnings rather than recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/minix/dir.c

## Summary
Minix directory read, lookup, insertion, deletion, emptiness, and dotdot helpers.

## Main APIs
`minix_readdir()`, `minix_find_entry()`, `minix_add_link()`, `minix_delete_entry()`, `minix_make_empty()`, `minix_empty_dir()`, `minix_set_link()`, `minix_dotdot()`, and `minix_inode_by_name()`.

## Behavior
Directory entries are fixed-size records from `sbi->s_dirsize`, with V1/V2 and V3 inode/name layouts handled separately. Readdir aligns `ctx->pos` to entry size, maps folios, skips zero-inode entries, and emits names with `DT_UNKNOWN`. Lookup scans mapped folios and returns a still-mapped entry. Add-link searches for a free or end-of-directory slot, prepares the folio chunk, writes the name/inode, extends size if needed, updates timestamps, and syncs directory metadata for dirsync.

## State and Synchronization
Directory modification locks the target folio and uses `minix_prepare_chunk()` plus `block_write_end()` through `dir_commit_chunk()`. Folios are kmap-local mapped and must be released by callers.

## Dependencies
Page cache folios, buffer-head write helpers, Minix directory sizing/name limits, `minix_fsync()`, and VFS dir iteration.

## Risks
Callers of `minix_find_entry()` and `minix_dotdot()` inherit responsibility for `folio_release_kmap()`. Version-specific entry layouts differ only by inode field width/offset, so casts must track `s_version`. Directory expansion writes outside current `i_size` under folio lock.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/file.c -->
# File Research: sources/os/linux/linux-stable/fs/minix/file.c

## Summary
Regular file operations and inode attribute updates for Minix.

## Main APIs
`minix_fsync()`, `minix_file_operations`, `minix_setattr()`, and `minix_file_inode_operations`.

## Behavior
Regular files use generic llseek/read/write/mmap/splice helpers. `minix_fsync()` delegates to `mmb_fsync()` with the inode’s metadata buffer-head list. `minix_setattr()` validates attributes, handles size changes by checking the new size, updating `i_size`, and calling `minix_truncate()`, then copies remaining attributes and marks the inode dirty.

## Dependencies
Generic VFS file helpers, buffer-head metadata syncing, Minix inode private metadata buffers, `minix_truncate()`, and `minix_getattr()`.

## Risks
Size updates are non-journaled and depend on truncate plus dirty inode writeback. The idmap argument is ignored in favor of `nop_mnt_idmap`, matching this filesystem’s legacy behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/file.c -->