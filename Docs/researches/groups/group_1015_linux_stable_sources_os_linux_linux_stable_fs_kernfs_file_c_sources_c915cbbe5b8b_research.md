# Group Research: group_1015_linux_stable_sources_os_linux_linux_stable_fs_kernfs_file_c_sources_c915cbbe5b8b

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux-stable`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/kernfs/file.c

Implements kernfs regular-file behavior: open/release, read/write dispatch, seq_file support, mmap wrapping, poll notifications, open-file draining, and internal file-node creation.

Key structures and state:
- `struct kernfs_open_node` stores per-kernfs-node open-file state: poll event counter, wait queue, open file list, mmap count, and pending release count.
- Each `struct kernfs_open_file` is linked under `kn->attr.open` while open.
- Open-file list updates are protected by a hashed global `kernfs_locks->open_file_mutex[]`.
- Active references via `kernfs_get_active()` protect callback dispatch into `kernfs_ops`.

Major flows:
- `kernfs_fop_open()` validates permissions when `KERNFS_ROOT_EXTRA_OPEN_PERM_CHECK` is set, allocates `kernfs_open_file`, sets up optional preallocation, opens seq_file state, links the open file, and calls `ops->open`.
- Read path uses `seq_read_iter()` when `KERNFS_HAS_SEQ_SHOW` is set; otherwise `kernfs_file_read_iter()` invokes `ops->read` with a PAGE_SIZE-capped buffer.
- Write path copies a single user buffer, NUL-terminates it, honors `atomic_write_len`, and calls `ops->write`.
- mmap path requires cached `KERNFS_HAS_MMAP`, calls `ops->mmap`, rejects close callbacks in supplied VM ops, then wraps fault/open/page_mkwrite/access through `kernfs_vm_ops`.
- Release path calls `ops->release` exactly once when `KERNFS_HAS_RELEASE` is set, unlinks the open file, releases seq state, and frees buffers.
- `kernfs_drain_open_files()` unmaps mmapped files and forces release callbacks during node deactivation.
- `kernfs_notify()` wakes poll waiters immediately, increments event counters, then queues work for fsnotify events across mounted superblocks.
- `__kernfs_create_file()` creates a `KERNFS_FILE` node, stores `kernfs_ops`, size, namespace, private pointer, optional lockdep map, and caches operation-presence flags.

Concurrency and correctness notes:
- `of->mutex` serializes operations for one open file and nests outside active refs.
- The seq_file start/stop path has special handling for `ERR_PTR(-ENODEV)` so active refs are not double-dropped.
- Notification queuing uses `kn->attr.notify_next` as a singly linked membership marker and terminates with `KERNFS_NOTIFY_EOL`.
- Open-node lifetime is RCU-managed with `kfree_rcu`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/kernfs/inode.c

Implements kernfs inode attributes, inode instantiation, permission/getattr/setattr, and xattr support.

Key responsibilities:
- `kernfs_iattrs` are allocated lazily with defaults for uid/gid/timestamps and `simple_xattr_limits`.
- `kernfs_setattr()` and `kernfs_iop_setattr()` update persistent kernfs attributes under `root->kernfs_iattr_rwsem`.
- `kernfs_refresh_inode()` copies kernfs mode and persistent attributes into VFS inode state and maintains directory link counts.
- `kernfs_init_inode()` initializes inode operations based on node type:
  - directories use `kernfs_dir_iops` / `kernfs_dir_fops`
  - files use `kernfs_file_fops`
  - links use `kernfs_symlink_iops`
  - empty dirs use `make_empty_dir_inode()`
- `kernfs_get_inode()` obtains or initializes an inode keyed by `kernfs_ino(kn)`.
- `kernfs_evict_inode()` truncates pages, clears inode state, and drops the kernfs node reference.
- `kernfs_iop_permission()` refreshes attributes before delegating to `generic_permission()`.

Xattr behavior:
- Trusted and security xattrs use generic kernfs get/set wrappers.
- User xattrs require `KERNFS_ROOT_SUPPORT_USER_XATTR` and use limited simple xattr storage.
- `kernfs_iop_listxattr()` lists lazily allocated xattrs.

Important locking:
- Attribute reads and writes are serialized with `kernfs_iattr_rwsem`.
- Lazy `kn->iattr` installation uses `try_cmpxchg` to handle concurrent first allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/kernfs-internal.h -->
# File Research: sources/os/linux/linux-stable/fs/kernfs/kernfs-internal.h

Internal kernfs header tying together inode, directory, file, symlink, mount, and global-lock implementation details.

Defines:
- `struct kernfs_iattrs`: persistent uid/gid/timestamps and simple xattr state.
- `struct kernfs_root`: root node, ID allocator, syscall ops, superblock list, deactivation wait queue, rwsems, rename lock, and RCU lifetime.
- `KN_DEACTIVATED_BIAS`: active-reference deactivation bias.
- `struct kernfs_super_info`: per-superblock root and namespace tag.

Important helpers:
- `kernfs_root()` resolves a node’s root using RCU parent access.
- `kernfs_rcu_name()` and `kernfs_parent()` provide lockdep-aware access to rename-sensitive fields.
- `kernfs_dentry_node()` maps a positive dentry to its kernfs node.
- Directory revision helpers store/recheck `dentry->d_time`.

Exports internal cross-file interfaces:
- Inode operations and xattr handlers from `inode.c`.
- Directory operations and active-reference helpers from `dir.c`.
- File operations and open-file draining helpers from `file.c`.
- Symlink inode ops from `symlink.c`.
- `kernfs_locks` global lock table from `mount.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/kernfs-internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/mount.c -->
# File Research: sources/os/linux/linux-stable/fs/kernfs/mount.c

Implements kernfs superblock operations, export handles, mount/get_tree plumbing, superblock lifetime, and kernfs global initialization.

Core superblock behavior:
- `kernfs_sops` provides statfs, inode eviction, mount option/path display, and explicitly disables freeze/thaw hooks to avoid sysfs suspend/hibernate deadlocks.
- `kernfs_statfs()` uses `simple_statfs()` and UUID-derived fsid.
- `kernfs_fill_super()` initializes kernfs superblock flags, magic, xattr handlers, optional export ops, root inode, root dentry, and dentry ops.

Export support:
- `kernfs_encode_fh()` encodes the 64-bit kernfs node ID.
- `__kernfs_fh_to_dentry()` resolves `FILEID_KERNFS` and compatibility `FILEID_INO32_GEN*` handles back to nodes.
- Parent resolution and dentry construction use `kernfs_find_and_get_node_by_id()`, `kernfs_get_inode()`, and `d_obtain_alias()`.

Mount helpers:
- `kernfs_get_tree()` allocates `kernfs_super_info`, uses `sget_fc()` to share superblocks by root and namespace, fills new superblocks, assigns UUIDs, and links them under `root->supers`.
- `kernfs_kill_sb()` removes the superblock from the root list, kills the anonymous superblock, and frees `kernfs_super_info`.
- `kernfs_free_fs_context()` frees fs context storage.

Dentry path helper:
- `kernfs_node_dentry()` walks from root to target using invariant-parent assumptions and unlocked positive lookups.

Initialization:
- Creates slab caches for `kernfs_node` and `kernfs_iattrs`.
- Allocates and initializes hashed global open-file mutexes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/symlink.c -->
# File Research: sources/os/linux/linux-stable/fs/kernfs/symlink.c

Implements kernfs symlink creation and VFS get_link behavior.

Key behavior:
- `kernfs_create_link()` creates a `KERNFS_LINK` node with mode `0777`, ownership copied from target attributes when present, optional namespace inherited from target, and a held reference to `target`.
- `kernfs_get_target_path()` constructs a relative path from the symlink parent to target by walking up to a common base, adding `../`, then reverse-filling the target path components.
- `kernfs_getlink()` protects parent/name traversal with `root->kernfs_rwsem`.
- `kernfs_iop_get_link()` allocates a PAGE_SIZE buffer, fills it with the relative target path, and registers `kfree_link` cleanup.

Exports:
- `kernfs_symlink_iops` supports listxattr, get_link, setattr, getattr, and permission through shared kernfs inode helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/kernfs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/libfs.c -->
# File Research: sources/os/linux/linux-stable/fs/libfs.c

Large VFS helper library for simple/pseudo filesystems, in-memory directory operations, offset-stable directory iteration, recursive removal, simple file operations, xattrs-adjacent helpers, export file handles, casefold/encryption dentry ops, i_version, direct-I/O fallback, and stashed anonymous paths.

Major helper families:
- Basic helpers: `simple_getattr()`, `simple_statfs()`, `simple_lookup()`, `generic_read_dir()`, `noop_fsync()`, `kfree_link()`.
- Dcache-backed directories: `dcache_dir_open/close/lseek`, `dcache_readdir()`, `simple_dir_operations`, and `simple_dir_inode_operations`.
- Offset directories: `simple_offset_init/add/remove/rename/rename_exchange/destroy()` use maple trees and `d_fsdata` to assign stable readdir offsets.
- Recursive removal: `simple_recursive_removal()`, `locked_recursive_removal()`, and `simple_remove_by_name()` walk positive children, invalidate dentries, update nlinks/timestamps, and invoke optional callbacks.
- Pseudo filesystem setup: `init_pseudo()` installs fs_context ops for non-user-mountable pseudo filesystems.
- Simple inode/dentry mutations: `simple_link()`, `simple_empty()`, `simple_unlink()`, `simple_rmdir()`, `simple_rename_timestamp()`, `simple_rename()`, `simple_setattr()`.
- Ramfs-style pagecache data: `ram_aops` with zero-fill read folio, `simple_write_begin()`, and `simple_write_end()`.
- Superblock filling and pinning: `simple_fill_super()`, `simple_pin_fs()`, and `simple_release_fs()`.
- Buffer helpers: `simple_read_from_buffer()`, `simple_write_to_buffer()`, and `memory_read_from_buffer()`.
- Transaction files: `simple_transaction_get/set/read/release()`.
- Simple numeric attrs: `simple_attr_open/read/write/write_signed/release()`.
- Export helpers: `generic_encode_ino32_fh()`, `generic_fh_to_dentry()`, `generic_fh_to_parent()`.
- Fsync and addressability: `simple_fsync_noflush()`, `simple_fsync()`, `generic_check_addressable()`.
- Anonymous inodes and fast symlinks: `alloc_anon_inode()`, `simple_get_link()`, `simple_symlink_inode_operations`.
- Empty dirs: `make_empty_dir_inode()` and `is_empty_dir_inode()`.
- Casefold/encryption: `generic_ci_d_compare()`, `generic_ci_d_hash()`, `generic_ci_match()`, `generic_set_sb_d_ops()`.
- i_version: `inode_maybe_inc_iversion()` and `inode_query_iversion()` use atomic cmpxchg and paired memory barriers.
- Direct-I/O fallback: `direct_write_fallback()` reconciles partial direct writes with buffered fallback and invalidates page cache.
- Stashed paths: `stashed_dentry_get()`, `stash_dentry()`, `path_from_stashed()`, `stashed_dentry_prune()` support nsfs/pidfs-style reusable anonymous dentries.
- Creation helpers: `simple_start_creating()` and `simple_done_creating()` wrap lookup/create locking.

Concurrency notes:
- Directory scanning uses dentry locks and cursor dentries.
- Offset directories rely on caller-held `i_rwsem`.
- `simple_pin_fs()` uses a spinlock-protected mount/count pair.
- Stashed dentries use RCU, lockref, and cmpxchg to avoid stale dead dentry reuse.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/libfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/lockd/Makefile

Build composition for the kernel lock manager (`lockd`).

Key points:
- Adds `-I$(src)` for trace event headers.
- Builds `lockd.o` when `CONFIG_LOCKD` is enabled.
- Core objects include client lock/proc/XDR, host cache, service code, server locking/sharing/proc/subs, NSM monitor, trace, XDR, and netlink.
- `CONFIG_LOCKD_V4` adds NLMv4 client XDR, server v4 procedures, and generated NLMv4 server XDR.
- `CONFIG_PROC_FS` adds procfs support.
- Provides an `xdrgen` developer target to regenerate checked-in generated files from `Documentation/sunrpc/xdr/nlm4.x`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/clnt4xdr.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/clnt4xdr.c

Client-side XDR encoder/decoder for NLM version 4 RPC calls.

Protocol details:
- Uses NFSv3 file handle size and NLMv4 64-bit byte ranges.
- Verifies client owner string size against XDR and NLM maximums at compile time.
- Encodes/decodes cookies, netobjs, caller names, NLM locks, holders, and status results.
- `lockd_set_file_lock_range4()` converts decoded `(offset,length)` into kernel `(start,end)` semantics, including EOF locks.

RPC procedures:
- Defines encode/decode routines for TEST, LOCK, CANCEL, UNLOCK, GRANTED, message variants, and result callbacks.
- `nlm4_procedures[]` maps `NLMPROC_*` IDs to XDR handlers and word-size estimates.
- Exports `nlm_version4` for the common `nlm_program`.

Correctness notes:
- Status values are kept in network byte order for upper layers.
- Invalid status enum values decode as `-EIO`.
- Zero-length cookies from HPUX are normalized to a 4-byte zero cookie.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/clnt4xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/clntlock.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/clntlock.c

Client-side NLM lock blocking and reclaim support.

Main entry points:
- `nlmclnt_init()` starts lockd for an NFS mount, selects NLM version 1 for NFSv2 or version 4 otherwise, looks up/binds an `nlm_host`, and stores NFS client callbacks.
- `nlmclnt_done()` releases the host and decrements lockd service usage.
- `nlmclnt_prepare_block()`, `nlmclnt_queue_block()`, `nlmclnt_dequeue_block()`, and `nlmclnt_wait()` manage blocking lock wait state.
- `nlmclnt_grant()` matches incoming GRANTED callbacks against blocked requests by lock range, synthetic owner pid, peer address, and file handle.

Recovery:
- `nlmclnt_recovery()` spawns a per-host reclaimer thread once per reboot episode.
- `reclaimer()` moves granted locks to a reclaim list, rebinds the peer, calls `nlmclnt_reclaim()` for each lock, restarts if the server reboots again, then wakes blocked waiters with grace-period status.

Synchronization:
- Global `nlm_blocked` is protected by `nlm_blocked_lock`.
- Host reclaim uses `host->h_rwsem`.
- Reclaimer holds an extra host reference and lockd service reference.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/clntlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/clntproc.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/clntproc.c

Implements client-side NLM RPC procedure orchestration for test, lock, unlock, cancel, and reclaim.

Key logic:
- `nlmclnt_next_cookie()` creates 4-byte cookies from an atomic counter.
- Lock owners map VFS `fl_owner_t` to per-host synthetic 32-bit pids with refcounted `nlm_lockowner` objects.
- `nlmclnt_setlockargs()` copies NFS file handle, caller name, owner handle, pid, range, and lock type into RPC args.
- `nlmclnt_proc()` is the exported fcntl-style entry point; it allocates a request, initializes private lock state, dispatches GETLK/SETLK/SETLKW/UNLCK, then releases private state.

RPC behavior:
- `nlmclnt_call()` performs synchronous RPC with grace-period waiting, rebinds after connection failures, and wakes grace waiters when the server leaves grace.
- `__nlm_async_call()`, `nlm_async_call()`, and `nlm_async_reply()` launch async RPC tasks.
- `nlmclnt_async_call()` starts async work but waits for completion to track local lock state.

Lock operations:
- `nlmclnt_test()` maps conflict results back into the caller’s `file_lock`.
- `nlmclnt_lock()` monitors peer state, locally preflights with `FL_ACCESS`, queues a wait block before RPC to catch early GRANTED callbacks, polls blocked locks, cancels interrupted blocking requests, installs granted locks locally, and unlocks remotely/local state on fatal errors.
- `nlmclnt_reclaim()` sends reclaim LOCK during server grace.
- `nlmclnt_unlock()` removes local lock state first, then sends async UNLOCK and handles expected status.
- `nlmclnt_cancel()` sends async CANCEL with bounded retry logic.

Status mapping:
- `nlm_stat_to_errno()` maps NLM statuses to Linux errno, including v4-only deadlock, read-only filesystem, stale fh, and overflow cases.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/clntproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/clntxdr.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/clntxdr.c

Client-side XDR encoder/decoder for NLM versions 1 and 3.

Protocol details:
- NLMv2 is intentionally not implemented.
- Uses NFSv2 fixed file handle size and 32-bit lock offsets/lengths.
- `loff_t_to_s32()` clamps kernel offsets to NLMv1/v3 range.
- `nlm_compute_offsets()` emits length zero for lock-to-EOF.

XDR coverage:
- Encodes/decodes booleans, int32, netobj, cookies, file handles, status, holders, caller names, and lock structs.
- Handles TEST, LOCK, CANCEL, UNLOCK, GRANTED, async message variants, and result callbacks.
- Normalizes empty HPUX cookies to a 4-byte zero cookie.
- Rejects oversized cookies and invalid status enum values.

RPC program integration:
- `nlm_procedures[]` maps `NLMPROC_*` procedures to handlers and sizing constants.
- Defines version 1 and version 3 `rpc_version` tables.
- `nlm_program` includes versions 1, 3, and optionally 4.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/clntxdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/host.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/host.c

Manages shared NLM peer host handles for client and server personalities.

Host cache:
- Uses separate hash tables for client and server hosts.
- Hashes IPv4/IPv6 peer addresses into 32 buckets.
- `nlm_alloc_host()` initializes address, RPC metadata, NSM handle, locks, reclaim/granted lists, refcount, expiry, credentials, and nodename.
- `nlmclnt_lookup_host()` matches client hosts by netns, address, protocol, and NLM version.
- `nlmsvc_lookup_host()` matches server hosts by netns, client address, source address, protocol, and version; it also triggers periodic GC.

RPC binding:
- `nlm_bind_host()` creates an RPC client with NLM program/version, UNIX auth, autobind, reuseport, optional hard retry for client-side calls, optional non-privileged source port, and optional source address.
- `nlm_rebind_host()` forces UDP portmap rebinds on a timed interval.
- `nlmclnt_shutdown_rpc_clnt()` marks a client shut down and cancels outstanding tasks.

Reboot and GC:
- `nlm_host_rebooted()` maps NSM reboot notifications to all affected hosts, frees server resources, and starts client recovery.
- `nlm_shutdown_hosts_net()` expires all matching server hosts, shuts down RPC clients, frees server resources, and runs GC.
- `nlm_gc_hosts()` marks hosts with active resources, then destroys expired unreferenced server hosts.
- Per-net and global host counters are maintained.

Synchronization:
- Global host cache is protected by `nlm_host_mutex`.
- Individual RPC client binding is protected by `host->h_mutex`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/host.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/lockd.h -->
# File Research: sources/os/linux/linux-stable/fs/lockd/lockd.h

Central internal header for lockd.

Defines:
- Debug facility flags and `LOCKD_VERSION`.
- NLMv4 status constants and internal-only status values.
- `struct nlm_host`: peer identity, RPC client, protocol/version, reclaim/grace state, refcount, lock owner lists, granted/reclaim locks, NSM handle, netns, credentials, and callbacks.
- `struct nsm_handle`: cached statd monitor state, names, address, private cookie, and refcount.
- `struct nlm_lockowner`: per-host synthetic pid mapping for NFS lock owners.
- `struct nlm_wait`: client-side blocked lock wait object.
- `struct nlm_rqst`: client/server RPC request storage.
- `struct nlm_file`: server-side file handle with VFS files, shares, blocks, lock counts, and mutex.
- `struct nlm_block`: server-side blocked lock state and retry/deferred request metadata.

Declares:
- Client procedures, async calls, reclaim, blocking/grant helpers, and cookie generation.
- Host cache lookup/release/bind/rebind/shutdown and reboot handling.
- NSM monitor/unmonitor and handle lookup/release.
- Server-side lock/file/share/resource functions.
- NLM service dispatch and lock manager operations.

Important inline helpers:
- Address accessors for peer/source sockaddr.
- `nlmsvc_file_file()` and inode helpers.
- Privileged local requester checks for IPv4/IPv6 loopback and source ports <=1023.
- `nlm_compare_locks()` compares file, pid, owner, range, and type, treating unlock type as wildcard.
- `lockd_set_file_lock_range4()` converts NLMv4 offset/length to kernel lock range with overflow/EOF handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/lockd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/mon.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/mon.c

Implements the in-kernel Network Status Monitor client used by lockd to coordinate reboot notifications with local `rpc.statd`.

Main behavior:
- `nsm_create()` builds an RPC client to local loopback `rpc.statd` using NSM program 100024 version 1.
- `nsm_monitor()` sends `NSMPROC_MON` for a peer not already monitored and updates `nsm_local_state`.
- `nsm_unmonitor()` sends `NSMPROC_UNMON` when the last non-sticky reference is released.
- `nsm_get_handle()` looks up or creates per-netns NSM handles by hostname or address depending on `nsm_use_hostnames`.
- `nsm_reboot_lookup()` matches statd reboot callbacks by private cookie.
- `nsm_release()` drops and frees handles.

Handle details:
- Hostnames containing `/` are rejected.
- `nsm_init_private()` creates a private cookie from current time and handle address to avoid stale-cookie collision across reboots.
- Address text is cached in `sm_addrbuf`.

XDR:
- Encodes NSM strings, monitor identity, callback identity, and private data.
- Decodes monitor/unmonitor status and state.
- Defines RPC procedure table for MONITOR and UNMONITOR.

Synchronization:
- Per-net NSM handle lists are protected by `nsm_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/mon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/netlink.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/netlink.c

Generated Generic Netlink family definition for lockd configuration.

Key points:
- Generated from `Documentation/netlink/specs/lockd.yaml`.
- Defines policy for `LOCKD_CMD_SERVER_SET` attributes:
  - gracetime: `NLA_U32`
  - TCP port: `NLA_U16`
  - UDP port: `NLA_U16`
- Registers split ops for:
  - `LOCKD_CMD_SERVER_SET` using `lockd_nl_server_set_doit`, admin permission required.
  - `LOCKD_CMD_SERVER_GET` using `lockd_nl_server_get_doit`.
- Exports `lockd_nl_family` with `netnsok = true`, `parallel_ops = true`, and lockd family name/version.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/netlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/netlink.h -->
# File Research: sources/os/linux/linux-stable/fs/lockd/netlink.h

Generated internal header for lockd Generic Netlink handlers.

Contains:
- Includes for generic netlink and `uapi/linux/lockd_netlink.h`.
- Prototypes for `lockd_nl_server_set_doit()` and `lockd_nl_server_get_doit()`.
- External declaration of `lockd_nl_family`.

The file is generated from `Documentation/netlink/specs/lockd.yaml`; manual edits are not intended.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/netlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/netns.h -->
# File Research: sources/os/linux/linux-stable/fs/lockd/netns.h

Defines lockd per-network-namespace state.

`struct lockd_net` stores:
- Service user count.
- Next host-GC timestamp and host count.
- Configurable grace time and TCP/UDP ports.
- Delayed work for ending grace period.
- `struct lock_manager lockd_manager`.
- Per-net list of NSM handles.

Declares `lockd_net_id` for `net_generic()` lookup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/netns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/nlm.h -->
# File Research: sources/os/linux/linux-stable/fs/lockd/nlm.h

Defines core Network Lock Manager protocol constants.

Contents:
- Maximum v1/v3 and v4 lock offsets.
- NLM status enum values:
  - granted, denied, nolocks, blocked, grace-period denied
  - v4-only deadlock, read-only filesystem, stale file handle, file too big, failed
- NLM RPC program number `100021`.
- Procedure numbers for NULL, TEST, LOCK, CANCEL, UNLOCK, GRANTED, async message/result variants, NSM notify, SHARE/UNSHARE, NM_LOCK, and FREE_ALL.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/nlm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/nlm4xdr_gen.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/nlm4xdr_gen.c

Generated server-side XDR encoder/decoder support for NLMv4.

Decode coverage:
- Primitive helpers for netobj, share mode/access, uint64/int64, uint32/int32, and NLMv4 stats.
- Compound decoders for holder, testrply, stat, res, testres, lock, lockargs, cancargs, testargs, unlockargs, share, shareargs, shareres, notify, and notifyargs.
- Public service decode entry points fill `rqstp->rq_argp` for void, TEST, LOCK, CANCEL, UNLOCK, TEST_RES, RES, NOTIFYARGS, SHAREARGS, and NOTIFY.

Encode coverage:
- Primitive helpers mirror the decoders.
- Compound encoders for holder, testrply, stat, res, testres, lock, lockargs, cancargs, testargs, unlockargs, share, shareargs, shareres, notify, and notifyargs.
- Public service encode entry points write `rqstp->rq_resp` for void, TESTRES, RES, and SHARERES.

Generated-file notes:
- Produced by `xdrgen` from `Documentation/sunrpc/xdr/nlm4.x`.
- Enforces maximum string lengths for caller and notify names before encoding.
- Uses bool-returning decode/encode helpers instead of errno.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/nlm4xdr_gen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/nlm4xdr_gen.h -->
# File Research: sources/os/linux/linux-stable/fs/lockd/nlm4xdr_gen.h

Generated declarations for NLMv4 server-side XDR handlers.

Declares service decode functions for:
- void, testargs, lockargs, cancargs, unlockargs, testres, res, notifyargs, shareargs, and notify.

Declares service encode functions for:
- void, testres, res, and shareres.

Includes generated XDR type definitions from `linux/sunrpc/xdrgen/nlm4.h` and supporting xdrgen builtins/defs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/nlm4xdr_gen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/procfs.c -->
# File Research: sources/os/linux/linux-stable/fs/lockd/procfs.c

Implements procfs control for manually ending lockd grace period.

Interface:
- Creates `/proc/fs/lockd/nlm_end_grace`.
- Read returns `Y\n` when the per-net lock manager grace list is empty, otherwise `N\n`.
- Write accepts strings beginning with `Y`, `y`, or `1`; accepted writes call `locks_end_grace(&ln->lockd_manager)`.
- Uses current task’s network namespace via `current->nsproxy->net_ns`.

Implementation notes:
- Write uses `simple_transaction_get()` and release uses `simple_transaction_release()`.
- `lockd_create_procfs()` creates directory and file, rolling back the directory on failure.
- `lockd_remove_procfs()` removes file and directory.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/procfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/procfs.h -->
# File Research: sources/os/linux/linux-stable/fs/lockd/procfs.h

Header for lockd procfs support.

Behavior:
- When `CONFIG_PROC_FS` is enabled, declares `lockd_create_procfs()` and `lockd_remove_procfs()`.
- Otherwise provides inline no-op implementations, with create returning success.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/procfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/share.h -->
# File Research: sources/os/linux/linux-stable/fs/lockd/share.h

Defines lockd DOS share-management data and server-side share operation prototypes.

Contents:
- `LOCKD_SHARE_SVID` synthetic owner id for share lockowner lookup.
- `struct nlm_share` links a share to host, file, owner handle, access mode, and deny mode.
- Declares `nlmsvc_share_file()`, `nlmsvc_unshare_file()`, and `nlmsvc_traverse_shares()`.

This header is used by server-side lockd share handling, while the implementation is outside this group.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/lockd/share.h -->