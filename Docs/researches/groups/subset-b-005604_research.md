# subset-b-005604 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_rotate.c -->
# sources/distributed-fs/ceph-client/fs/afs/vl_rotate.c

Purpose: Implements volume location server cursor setup, server/address selection, retry rotation, and operation teardown for kAFS VLDB queries.

Important APIs and functions: `afs_begin_vlserver_operation()` initializes `struct afs_vl_cursor`, associates the cell/key, handles pending signals, and seeds the cumulative error state. `afs_select_vlserver()` is the central iterator: it starts DNS/VL server-list lookup, sends VL probes, picks a responsive server by preferred index or lowest RTT, rotates through address lists, records per-address errors, and decides whether to retry or stop. `afs_end_vlserver_operation()` releases cursor-held address/server-list references and returns the prioritized error. `afs_vl_dump_edestaddrreq()` provides bounded debug diagnostics for address resolution failures.

Control flow: First selection triggers `afs_start_vl_iteration()`, which queues cell DNS lookup when records are missing or expired, waits for lookup when necessary, obtains the RCU-protected VL server list under `vl_servers_lock`, and initializes the untried server bitmap. Subsequent calls interpret the previous RPC's `call_error`, `abort_code`, and `call_responded` fields. Network reachability errors rotate addresses; strange VL aborts rotate servers; `-ECONNRESET` marks a whole-list retry; success or local errors stop iteration.

State and persistence: The cursor owns temporary references to `server_list` and `alist`, updates `alist->preferred` when a nonpreferred address responded, and writes `last_error` into the address entry. Persistent cell state includes DNS source/status/expiry and the VL server list. The cumulative error records the most useful terminal reason across probes and calls.

Dependencies and integration points: Depends on AFS cell DNS maintenance, VL probe helpers, RxRPC peers in address lists, trace/debug helpers, and error-prioritization helpers from AFS internals. It is consumed by VL client calls in `volume.c` and server/address refresh code.

Risks: Bitmap construction assumes the server count fits an unsigned long. Correctness depends on balanced `afs_get_*`/`afs_put_*` references on all retry paths and on not using stale address lists after restart. Retry policy affects mount latency and failover behavior under partial outages.

Test signals: Exercise cells with expired DNS, no DNS record, multiple VL servers with mixed RTTs, per-address network failures, unsupported operations, reset-triggered retries, and signal interruption before operation start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_rotate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vlclient.c -->
# sources/distributed-fs/ceph-client/fs/afs/vlclient.c

Purpose: Provides kAFS Volume Location service RPC client stubs for classic AFS VL and YFSVL calls, including VLDB lookup, address lookup, capability probing, endpoint decoding, and cell-name lookup.

Important APIs and functions: `afs_vl_get_entry_by_name_u()` sends `VLGETENTRYBYNAMEU` and returns `struct afs_vldb_entry`. `afs_vl_get_addrs_u()` resolves a server UUID into an IPv4 address list. `afs_vl_get_capabilities()` sends an async probe used by VL server probing. `afs_yfsvl_get_endpoints()` decodes YFS IPv4/IPv6 endpoint arrays. `afs_yfsvl_get_cell_name()` returns a server-reported cell name. Delivery functions use `call->unmarshall` state machines for variable-length replies.

Control flow: Call builders allocate flat AFS calls, fill request XDR, bind the selected cursor peer/service id, issue the RxRPC call, wait for completion for synchronous paths, copy `abort_code`, `error`, and `responded` back into the VL cursor, then release the call. Delivery functions first extract fixed fields, allocate return containers, then iterate variable arrays in bounded chunks. Endpoint decoding validates type tags and element lengths before merging addresses.

State and persistence: Returned VLDB entries carry volume IDs, type availability bits, server UUIDs, server flags, and address versions. Address-list calls fill `struct afs_addr_list` version and merged endpoint peers. The capability probe stores probe context in the call and reports completion through `afs_vlserver_probe_result()`.

Dependencies and integration points: Integrates with `vl_rotate.c` cursors, `volume.c` volume creation/update, AFS XDR protocol structures from `afs_fs.h`, RxRPC call allocation, and address-list merge helpers. YFSVL support feeds modern fileserver endpoint discovery.

Risks: Protocol parsing must strictly cap server/address counts and validate padded strings. Ownership of `ret_vldb`, `ret_alist`, and `ret_str` is transferred only on success; error paths must free partial returns. Cursor feedback is required for failover correctness.

Test signals: VLDB lookup by name and numeric ID, empty or no-media VLDB entries, large endpoint lists, bad endpoint type/length protocol errors, capability probe completion/cancel, and memory allocation failures during reply delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vlclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/volume.c -->
# sources/distributed-fs/ceph-client/fs/afs/volume.c

Purpose: Owns AFS volume records: lookup from VLDB, insertion into the cell volume tree, reference lifetime, fscache activation, server-list refresh, and volume status freshness checks.

Important APIs and functions: `afs_create_volume()` resolves a mount volume name, applies RW/RO/backup selection rules, and returns a live `struct afs_volume`. `afs_get_volume()`, `afs_try_get_volume()`, and `afs_put_volume()` manage refcounts and deferred destruction. `afs_activate_volume()` and `afs_deactivate_volume()` manage optional fscache volume cookies. `afs_check_volume_status()` ensures server lists and volume metadata are current before operations.

Control flow: `afs_create_volume()` calls `afs_vl_lookup_vldb()`, decides the desired volume type from force flags and VLDB availability, and delegates to `afs_lookup_volume()`. Allocation initializes locks, callbacks, mmap tracking, server list, volume IDs, and timestamps. Insertion uses the cell red-black tree under a seqlock and either attaches the new volume to servers or drops it in favor of an existing refcountable record.

State and persistence: A volume stores VID, all type VIDs, name, cell reference, type, server list, update deadline, creation/update volsync timestamps, cache cookie, flags, and per-volume locks. Server-list refresh can replace the RCU pointer, bump `servers_seq`, reattach to servers, and shorten the next refresh interval during RO replication.

Dependencies and integration points: Depends on VL RPC lookup, server-list allocation/annotation, cell tree/proc visibility, AFS operation keys, fscache, RCU, workqueues, and callback status logic used by vnode operations.

Risks: Volume replacement and destruction combine seqlocks, RCU, server attachment, and workqueue teardown. Refresh waiters can return `-ESTALE` after repeated update races. Name updates note a TODO for RCU-safe strings. Cache key collisions are logged and disable caching for that volume.

Test signals: Duplicate concurrent volume lookups, forced type selection failure, VLDB rename/server migration, RO replication refresh interval, fscache acquire `-EBUSY`, and interrupted waits in `afs_check_volume_status()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/volume.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/write.c -->
# sources/distributed-fs/ceph-client/fs/afs/write.c

Purpose: Connects kAFS regular-file writeback to the netfs writeback framework and AFS/YFS StoreData RPC operations.

Important APIs and functions: `afs_prepare_write()` sets stream write size limits. `afs_issue_write()` queues write subrequests to `system_dfl_wq`; `afs_issue_write_worker()` builds and executes the store operation. `afs_begin_writeback()` selects a valid cached writeback key. `afs_retry_request()` rotates keys after authorization failures. `afs_writepages()`, `afs_fsync()`, and `afs_page_mkwrite()` provide VFS writeback, fsync, and mmap write validation hooks. `afs_prune_wb_keys()` removes unused cached write keys.

Control flow: Netfs writeback calls `afs_begin_writeback()` to place a key in `wreq->netfs_priv`. Each subrequest worker allocates an AFS operation for the vnode, fills store offset/length/i_size/mtime, selects the AFS or YFS RPC through `afs_store_data_operation`, waits synchronously, and reports completion to netfs. Authorization errors mark the subrequest for retry when another writeback key exists.

State and persistence: Vnode writeback keys live on `vnode->wb_keys` under `wb_lock` with usage refcounts. Successful StoreData commits vnode status, increments store counters and byte stats, and prunes keys once dirty/writeback tags are gone. `validate_lock` serializes writeback against truncation.

Dependencies and integration points: Depends on Linux netfs writeback, keyrings, AFS operation framework, vnode validation/status commit, address-space dirty/writeback tags, and YFS/AFS StoreData clients.

Risks: Key rotation depends on correct `netfs_priv2` bookkeeping and refcount drops. Large `sreq_max_len` can stress server or network behavior. Worker submission must terminate every subrequest exactly once, including allocation failures.

Test signals: Writeback with expired/revoked keys, multiple author keys, truncation racing WB_SYNC_ALL and opportunistic writeback, mmap page faults after validation failure, fsync validation errors, and pruning after all dirty/writeback pages are clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/xattr.c -->
# sources/distributed-fs/ceph-client/fs/afs/xattr.c

Purpose: Exposes AFS metadata and ACL operations through Linux extended attributes instead of pioctl-style control calls.

Important APIs and functions: The exported handler table `afs_xattr_handlers[]` registers `afs.acl`, `afs.cell`, `afs.fid`, `afs.volume`, and `afs.yfs.*`. `afs_xattr_get_acl()`/`afs_xattr_set_acl()` fetch and store classic AFS ACLs. `afs_xattr_get_yfs()` and `afs_xattr_set_yfs()` handle YFS opaque ACL data and metadata fields. Metadata getters return cell name, FID text, and volume name.

Control flow: ACL getters allocate an AFS operation, set vnode slot 0, issue fetch RPCs, detach returned ACL buffers from the operation, and copy the data or return required size. Setters reject `XATTR_CREATE`, package the user buffer in `struct afs_acl`, and run synchronous store operations. YFS getters interpret suffix names (`acl`, `acl_inherited`, `acl_num_cleaned`, `vol_acl`) and request only needed opaque ACL parts.

State and persistence: This file does not persist local metadata beyond temporary operation ACL buffers. Successful ACL RPCs commit vnode status through `afs_acl_success()`. The static metadata xattrs reflect current vnode, volume, and cell fields.

Dependencies and integration points: Uses Linux xattr handlers, AFS/YFS operation dispatch, vnode status commit, ACL allocation helpers, and YFS opaque ACL free logic from `yfsclient.c`.

Risks: Buffer-size behavior must match xattr ABI: size query when `size == 0`, `-ERANGE` for undersized buffers. YFS unsupported errors are translated to `-ENODATA`. Set paths must free ACL buffers on all operation outcomes.

Test signals: Size-query and short-buffer reads, invalid YFS suffixes, unsupported YFS ACL RPCs, setting only `afs.yfs.acl`, rejecting create-only set flags, and formatting FIDs with and without high vnode bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/xdr_fs.h -->
# sources/distributed-fs/ceph-client/fs/afs/xdr_fs.h

Purpose: Defines on-wire AFS fileserver XDR structures for fetch status and directory pages, plus constants used by directory parsing and layout code.

Important APIs and types: `struct afs_xdr_AFSFetchStatus` maps the AFS3 fetch-status record, including type, link count, 64-bit size/data-version split fields, access masks, mode, parent IDs, timestamps, group, lock count, and abort code. `union afs_xdr_dirent`, `struct afs_xdr_dir_hdr`, `union afs_xdr_dir_block`, and `struct afs_xdr_dir_page` describe the 2048-byte AFS directory block format. `afs_dir_calc_slots()` computes standardized directory-entry slot counts.

Control flow: This is a header-only contract. Consumers decode network-byte-order fields and use the directory constants to walk hash tables, allocation bitmaps, directory blocks, and page-sized groups of blocks.

State and persistence: The structures describe persisted server-side wire/directory data, not local runtime state. Packed layout is essential because these definitions map directly onto network or page-cache bytes.

Dependencies and integration points: Depends on kernel endian types and `PAGE_SIZE`. It is included by AFS/YFS client and directory code that must share exactly the same layout assumptions as servers.

Risks: Any layout change would break wire compatibility. `afs_dir_calc_slots()` intentionally uses the standardized historical 16-byte first-slot calculation even though the C structure name array is effectively larger; changing this would corrupt directory parsing.

Test signals: Decode status records with high size/data-version bits, parse directories spanning multiple 2048-byte blocks per page, verify slot counts for short and long names, and assert packed sizes against protocol expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/xdr_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/yfsclient.c -->
# sources/distributed-fs/ceph-client/fs/afs/yfsclient.c

Purpose: Implements YFS fileserver RPC client stubs for data I/O, namespace changes, status, volume status, locks, bulk status, and opaque ACL operations.

Important APIs and functions: XDR helpers encode/decode YFS FIDs, strings, 64-bit values, times, store-status records, fetch-status records, callbacks, and volsync. Operation entry points include `yfs_fs_fetch_data()`, create/mkdir/remove/link/symlink/rename variants, `yfs_fs_store_data()`, `yfs_fs_setattr()`, `yfs_fs_get_volume_status()`, lock operations, `yfs_fs_fetch_status()`, `yfs_fs_inline_bulk_status()`, `yfs_fs_fetch_opaque_acl()`, and `yfs_fs_store_opaque_acl2()`.

Control flow: Each exported operation computes request/reply sizes, allocates a flat call, encodes opcode/RPC flags/FIDs/names/status payloads, checks request size with `yfs_check_req()`, tags `call->fid`, traces, and submits through `afs_make_op_call()`. Delivery functions either transfer a fixed reply or run `call->unmarshall` state machines for streamed data, volume strings, inline bulk arrays, and opaque ACLs.

State and persistence: Replies update `afs_operation` file slots with decoded status/callback data and `op->volsync`. Store and setattr calls persist server-side file data, length, mode, owner, group, and mtime. Rename/remove fallback bits (`AFS_SERVER_FL_NO_RM2`, `AFS_SERVER_FL_NO_RENAME2`) persist per server after opcode rejection.

Dependencies and integration points: Depends on YFS protocol definitions, AFS operation lifecycle, RxRPC flat calls, netfs subrequests for fetch data, vnode status commit by higher layers, lock completion callbacks, and xattr opaque ACL callers.

Risks: The file has many near-duplicate request-size calculations, making off-by-one padding and request overflow bugs high impact. Variable-length replies must cap counts and handle protocol errors. Fallback/downgrade flags affect later operations on the same server.

Test signals: Fetch short and overlong data, EOF flagging, create/remove status updates, RemoveFile2 and Rename2 downgrade on invalid opcode, setattr with and without size, lock completion, bulk-status count mismatch, opaque ACL partial requests, and negative YFS time conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/yfsclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/aio.c -->
# sources/distributed-fs/ceph-client/fs/aio.c

Purpose: Implements the legacy Linux native asynchronous I/O syscalls, including context allocation, userspace completion rings, request submission/cancellation, poll/fsync support, event retrieval, and compat/time32 variants.

Important APIs and types: `struct kioctx` owns an AIO context, ring mapping, refcounts, active request list, wait queue, completion state, and per-CPU request accounting. `struct aio_kiocb` wraps read/write, fsync, and poll requests. Syscalls implemented include `io_setup`, `io_destroy`, `io_submit`, `io_cancel`, `io_getevents`, `io_pgetevents`, and compat/time32 forms. `kiocb_set_cancel_fn()` is exported for async file operations to register cancellation.

Control flow: Boot setup creates private slab caches and a pseudo filesystem for AIO rings. `io_setup()` allocates a context, builds a pseudo file, allocates ring folios, mmaps the ring into the caller, and installs the context in `mm->ioctx_table` under RCU. `io_submit()` looks up the context, copies each userspace iocb, allocates an `aio_kiocb`, dispatches to read/write/fsync/poll, and completes or leaves async completion armed. `aio_complete()` writes `struct io_event` into the ring, advances tail with barriers, signals eventfd, and wakes waiters. `io_getevents()` drains ring entries and optionally waits with an hrtimer.

State and persistence: AIO state is per-mm and persists until `io_destroy()` or `exit_aio()`. The user-visible ring stores head/tail and events in mapped folios. Global `aio_nr` and `/proc/sys/fs/aio-*` track and limit request reservations. Active requests are cancelable under `ctx_lock`; completion-space accounting is batched per CPU.

Dependencies and integration points: Integrates with VFS `read_iter`/`write_iter`/`fsync`/`poll`, eventfd, block plugging, memory management, page migration, anonymous pseudo files, security/credentials, RCU, and syscall/compat layers.

Risks: Concurrency is subtle: ring migration, completion IRQ context, user-mutated head, poll waitqueue lifetime, cancellation, and context teardown interact. Request-slot accounting must avoid ring overflow and leaks. Poll supports only one waitqueue per request and has POLLFREE-specific lifetime rules.

Test signals: Context limits and sysctls, mmap/mremap of rings, concurrent submit/getevents, eventfd completion, async write cancellation, poll wake/POLLFREE races, io_destroy waiting for in-flight requests, timeouts/signals in pgetevents, compat pointer/time paths, and page migration of ring folios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/aio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/anon_inodes.c -->
# sources/distributed-fs/ceph-client/fs/anon_inodes.c

Purpose: Provides the anonymous inode infrastructure used by kernel subsystems that need file descriptors without real filesystem objects.

Important APIs and functions: `anon_inode_getfile()`, `anon_inode_getfile_fmode()`, and `anon_inode_getfd()` create files/fds backed by the singleton anonymous inode. `anon_inode_create_getfile()` and `anon_inode_create_getfd()` allocate unique anon inodes with LSM security initialization. `anon_inode_make_secure_inode()` is exported for secure inode creation. `anon_inode_getattr()` masks file type bits for legacy userspace expectations.

Control flow: `anon_inode_init()` mounts `anon_inodefs` and allocates the singleton inode at fs init time. Internal `__anon_inode_getfile()` pins the file-operations module, either reuses the singleton inode or creates a secure inode, allocates a pseudo file on the anon mount, assigns mapping and private data, and unwinds module/inode refs on error. FD helpers wrap the file helper with `FD_ADD()`.

State and persistence: Global read-mostly state consists of `anon_inode_mnt` and `anon_inode_inode`. Per-created files persist caller-provided `private_data`, file ops, flags, and optionally a unique inode security context. No disk persistence exists.

Dependencies and integration points: Uses pseudo filesystem helpers, `alloc_anon_inode()`, `alloc_file_pseudo()`, LSM `security_inode_init_security_anon()`, module ownership, and fd allocation helpers. Many subsystems such as eventfd, epoll, io_uring-like interfaces, and KVM-style devices rely on this pattern.

Risks: Module refcounting must pair with file release paths. Secure anon inodes intentionally clear `S_PRIVATE` and invoke LSM policy, so callers must pass correct context inodes. Legacy stat behavior masks `S_IFMT`, which is unusual compared with normal inodes.

Test signals: Singleton file/fd creation, custom `f_mode`, secure inode creation with LSM allow/deny, module owner failure, getattr mode masking, d_path dynamic names, and cleanup after `alloc_file_pseudo()` errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/anon_inodes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/attr.c -->
# sources/distributed-fs/ceph-client/fs/attr.c

Purpose: Implements generic VFS attribute-change permission checks, inode metadata copying, size-limit validation, setuid/setgid stripping, and `notify_change()` dispatch to filesystem `setattr`.

Important APIs and functions: `setattr_should_drop_sgid()`, `setattr_should_drop_suidgid()`, `setattr_prepare()`, `inode_newsize_ok()`, `setattr_copy()`, `may_setattr()`, and `notify_change()` are exported core helpers. Internal `chown_ok()` and `chgrp_ok()` implement idmapped permission logic; `setattr_copy_mgtime()` handles multigrain timestamp updates.

Control flow: `notify_change()` requires the inode locked, runs immutable/append/touch checks, rejects chmod on symlinks, truncates timestamps, evaluates killpriv and setid stripping, validates idmapped uid/gid mappings, calls LSM `security_inode_setattr()`, breaks delegations unless delegated, then invokes the filesystem `->setattr` or `simple_setattr()`. Successful changes generate fsnotify and security post hooks.

State and persistence: The file mutates in-memory inode uid/gid/mode/timestamps through `setattr_copy()`; actual persistence is delegated to each filesystem's setattr implementation. It also sends `SIGXFSZ` when extending beyond `RLIMIT_FSIZE` and protects swapfiles from truncation.

Dependencies and integration points: Central VFS dependency used by filesystem setattr paths, idmapped mounts, user namespaces, capabilities, LSM, fsnotify, file delegation, verity, swapfile protection, and timestamp infrastructure.

Risks: Permission behavior must preserve longstanding Unix semantics while supporting idmapped mounts. Incorrect ordering can allow privilege retention, invalid id mappings, or delegation races. Symlink chmod rejection is a deliberate compatibility/security stance.

Test signals: chown/chgrp under idmapped and non-idmapped mounts, chmod setgid clearing, setuid/setgid kill on write, truncate past rlimit/s_maxbytes, swapfile truncate denial, verity truncate denial, invalid uid/gid mapping `-EOVERFLOW`, delegation `-EWOULDBLOCK`, and multigrain timestamp updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/autofs/Kconfig

Purpose: Defines the build-time configuration option for Linux kernel automounter filesystem support.

Important APIs and types: `config AUTOFS_FS` is a tristate option labeled "Kernel automounter support (supports v3, v4 and v5)". It selects whether autofs is built in, built as the `autofs` module, or omitted.

Control flow: Kconfig exposes the option to kernel configuration tools. The help text explains that autofs combines kernel fast-path handling for already-mounted paths with a userspace automount daemon for demand mounting.

State and persistence: The selected tristate value persists in the kernel `.config` and controls compilation of objects in the autofs Makefile. There is no runtime state in this file.

Dependencies and integration points: Integrates with kbuild and the autofs source directory. The help text points users toward kernel.org autofs userspace tools and notes NFS support is commonly useful.

Risks: Misconfiguration omits automount support or builds it as a module when early boot expects built-in behavior. The text is user-facing and should remain accurate for supported protocol versions and module name.

Test signals: Kconfig menu visibility, `CONFIG_AUTOFS_FS=y/m/n` builds, module name generation, and successful build of the objects listed in the Makefile for enabled states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/Makefile -->
# sources/distributed-fs/ceph-client/fs/autofs/Makefile

Purpose: Connects the autofs implementation files to kbuild.

Important APIs and variables: `obj-$(CONFIG_AUTOFS_FS) += autofs4.o` builds the composite autofs object when the Kconfig option is enabled. `autofs4-objs` lists `init.o`, `inode.o`, `root.o`, `symlink.o`, `waitq.o`, `expire.o`, and `dev-ioctl.o`.

Control flow: During kbuild, the tristate expansion emits either built-in or module build rules. The composite object is still named `autofs4.o` internally while the registered filesystem/module identity is `autofs`.

State and persistence: No runtime state. The object list determines which source files form the autofs module or built-in component.

Dependencies and integration points: Integrates with `CONFIG_AUTOFS_FS`, module aliasing in `init.c`, and all autofs implementation files. Any new autofs translation unit must be added here to participate in builds.

Risks: Object list drift can silently omit required features, especially ioctl or expiration code. Renaming the composite object may affect module packaging expectations.

Test signals: Built-in and module builds, `modinfo`/module alias behavior, and link errors when adding or removing autofs functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/autofs_i.h -->
# sources/distributed-fs/ceph-client/fs/autofs/autofs_i.h

Purpose: Internal autofs header defining shared structures, flags, helpers, and prototypes for the autofs filesystem implementation.

Important APIs and types: `struct autofs_info` stores per-dentry state, flags, expiry completion, active/expiring lists, owner ids, timeout, and dentry reference. `struct autofs_sb_info` stores superblock-wide daemon pipe, owning process group, mount namespace id, protocol versions, flags, default timeout, type, locks, wait queues, and active/expiring lists. Helper APIs include `autofs_sbi()`, `autofs_dentry_ino()`, `autofs_oz_mode()`, pipe validation/preparation helpers, managed-dentry flag helpers, expiring-list helpers, and prototypes for wait, expire, inode, root, and ioctl code.

Control flow: Other autofs files include this header to coordinate mount setup, wait queue messaging, dentry management, expiry selection, and misc-device ioctl control. Inline helpers centralize common lock and flag manipulation.

State and persistence: Defines the core runtime state persisted for each mounted autofs superblock and each autofs dentry/inode. Flags such as `AUTOFS_INF_PENDING`, `AUTOFS_INF_WANT_EXPIRE`, and `AUTOFS_INF_EXPIRING` coordinate lookup and expiry. Superblock flags include catatonic, strict expire, and ignore modes.

Dependencies and integration points: Depends on VFS dentries/inodes/superblocks, mount APIs, fs_context, uapi autofs ioctl definitions, pid namespaces, pipes, wait queues, RCU, spinlocks, and mutexes.

Risks: This header sets locking expectations for all autofs code. Misusing `lookup_lock`, `fs_lock`, or expiring flags can cause RCU-walk hazards, missed expiry completion, or stale daemon communication state.

Test signals: Mount setup, daemon pipe validation, oz-mode permission checks, managed dentry flag transitions, per-dentry expiry list add/remove, catatonic behavior, and lookup behavior while entries are pending or expiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/autofs_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/dev-ioctl.c -->
# sources/distributed-fs/ceph-client/fs/autofs/dev-ioctl.c

Purpose: Implements the `/dev/autofs` miscellaneous-device ioctl control plane used by automount daemons to manage covered autofs mounts and reconnect to busy mount trees.

Important APIs and functions: `_autofs_dev_ioctl()` validates and dispatches device ioctls. Command handlers implement version/protocol queries, open/close mount control fds, ready/fail wait release, pipefd reset, catatonic mode, timeout updates, requester lookup, expire, ask-umount, and is-mountpoint checks. `autofs_dev_ioctl_init()` and `autofs_dev_ioctl_exit()` register/deregister the misc device.

Control flow: The dispatcher checks ioctl type/range, restricts most commands to `CAP_SYS_ADMIN`, copies a variable-sized `struct autofs_dev_ioctl`, validates version and path rules, looks up the handler through a nospec-protected table index, obtains the referenced autofs file when needed, enforces oz-mode except catatonic, runs the handler, then copies the fixed header back to userspace. Mount discovery climbs mount stacks with `find_autofs_mount()`.

State and persistence: Handlers mutate autofs superblock state: daemon pipe, `oz_pgrp`, mount namespace id, catatonic flag, global or per-dentry expiry timeouts, and wait queue release status. Returned fields include ioctlfd, requester uid/gid, may-umount, mountpoint device, and covering superblock magic.

Dependencies and integration points: Integrates with miscdevice, fdtable helpers, VFS path lookup and mount traversal, autofs wait/expire code, mount namespace identity, daemon pipe preparation, capability checks, and uapi ioctl structures.

Risks: ABI validation is security critical: path strings must be bounded and terminated, command indexes must be nospec-safe, and non-admin commands limited. `setpipefd` must only revive catatonic mounts and must reject PID namespace changes.

Test signals: Version mismatch, missing/invalid path, openmount by device, closemount, ready/fail tokens, setpipefd while non-catatonic, requester through covered mounts, expire loop returning `-EAGAIN`, ismountpoint with and without ioctlfd, compat ioctl, and non-admin denial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/dev-ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/expire.c -->
# sources/distributed-fs/ceph-client/fs/autofs/expire.c

Purpose: Implements autofs expiry selection, busyness checks, daemon notifications, and waits for dentries or mount trees being expired.

Important APIs and functions: `autofs_expire_run()` supports the legacy expire packet ioctl. `autofs_do_expire_multi()` and `autofs_expire_multi()` drive modern repeated expiry. `autofs_expire_wait()` blocks lookups on entries being expired. Internal helpers check direct mounts, tree mounts, leaf expiry, mount busyness, positive dentry traversal, and candidate selection.

Control flow: Expiry starts with direct/trigger mounts through `autofs_expire_direct()` or indirect mounts through `autofs_expire_indirect()`. Candidate selection checks pending flags, mountpoints, symlinks, dentry reference counts, subtree busyness, forced/immediate flags, and per-dentry or superblock timeouts. A two-phase `WANT_EXPIRE` then `EXPIRING` transition uses `synchronize_rcu()` to block RCU-walk races before notifying the daemon through `autofs_wait()`.

State and persistence: Uses `autofs_info` flags, `last_used`, per-entry `exp_timeout`, and `expire_complete`. Busy checks refresh `last_used` to avoid rapid retries. Completion clears `EXPIRING` and `WANT_EXPIRE` and wakes waiters.

Dependencies and integration points: Depends on VFS dentry/mount traversal, `may_umount_tree()`, `path_has_submounts()` indirectly through ioctl flows, autofs wait queues, superblock type helpers, RCU, dentry locking, and daemon notification packet definitions.

Risks: Expiry correctness depends on dentry refcount heuristics and locking order around `lookup_lock`, `d_lock`, and `fs_lock`. Missing completion would hang waiters. Forced expiry intentionally delegates busy handling to userspace and changes safety assumptions.

Test signals: Direct trigger expiry, indirect mount expiry, tree versus leaf mode, forced/immediate flags, per-dentry timeout override including zero timeout, busy submounts updating `last_used`, RCU-walk returning `-ECHILD`, unhashed dentry returning `-EAGAIN`, and repeated expire until `-EAGAIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/expire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/init.c -->
# sources/distributed-fs/ceph-client/fs/autofs/init.c

Purpose: Registers and unregisters the autofs filesystem type and its misc-device control interface.

Important APIs and functions: `autofs_fs_type` names the filesystem `autofs`, points mount setup at `autofs_init_fs_context`, exposes `autofs_param_specs`, and tears down superblocks with `autofs_kill_sb`. `init_autofs_fs()` initializes the ioctl misc device then registers the filesystem. `exit_autofs_fs()` deregisters both. Module aliases expose filesystem and module names.

Control flow: Module init calls `autofs_dev_ioctl_init()` first, then `register_filesystem()`. If filesystem registration fails, the misc device is cleaned up immediately. Module exit runs the reverse order: deregister misc device then unregister filesystem.

State and persistence: Runtime global state is the registered filesystem type and misc device registration. Mount-specific state lives in other autofs files.

Dependencies and integration points: Depends on module/init infrastructure, VFS filesystem registration, autofs fs-context parsing, superblock kill path, and device ioctl setup in `dev-ioctl.c`.

Risks: Init failure handling must not leave `/dev/autofs` registered without filesystem support. Exit ordering prevents new device ioctls before filesystem unregister completes.

Test signals: Built-in and module load/unload, registration failure injection, alias lookup by filesystem name, mount parameter parsing through `autofs_param_specs`, and clean misc-device deregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/autofs/init.c -->
