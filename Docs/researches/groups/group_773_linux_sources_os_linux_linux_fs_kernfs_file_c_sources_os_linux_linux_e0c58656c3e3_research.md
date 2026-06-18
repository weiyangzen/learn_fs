# Group Research: group_773_linux_sources_os_linux_linux_fs_kernfs_file_c_sources_os_linux_linux_e0c58656c3e3

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/kernfs/file.c -->
# File Research: sources/os/linux/linux/fs/kernfs/file.c

Purpose: Implements kernfs regular file behavior: open/release, seq-file reads, binary reads/writes, mmap wrapping, poll/notify, draining open files during node teardown, and internal file-node creation.

Key structures and state:
- `struct kernfs_open_node` tracks all open instances for a kernfs node, poll waitqueue, event counter, mmap count, and pending release count.
- `struct kernfs_open_file` instances are linked into the open node and serialize per-open operations through `of->mutex`.
- `kn->attr.open` is RCU-published and updated under the per-node hashed mutex from `kernfs_node_lock_ptr()`.

Main control flow:
- `kernfs_fop_open()` validates permissions, allocates and initializes `kernfs_open_file`, creates a seq_file wrapper, links into `kernfs_open_node`, and invokes optional `ops->open`.
- Read dispatch chooses `seq_read_iter()` when `KERNFS_HAS_SEQ_SHOW` is set, otherwise uses a page-sized/preallocated buffer and calls `ops->read`.
- Write copies user data into a NUL-terminated buffer, honors `atomic_write_len`, and calls `ops->write`.
- `kernfs_fop_mmap()` invokes `ops->mmap`, wraps VMA ops with `kernfs_vm_ops`, and rejects incompatible remaps or VM close callbacks.
- `kernfs_notify()` immediately updates poll state, then schedules work to emit fsnotify events across all mounted kernfs superblocks.
- `kernfs_drain_open_files()` unmaps active mappings and forces release callbacks before node removal completes.

Dependencies and integration:
- Exports `kernfs_notify()` and `kernfs_file_fops`.
- Depends on `kernfs_get_active()`/`kernfs_put_active()` from directory/core kernfs code, inode lookup for fsnotify, and `kernfs_root()->supers` for multi-superblock notification.
- Uses VFS seq_file, poll, mmap, splice, fsnotify, RCU, wait queues, and hashed kernfs node locks.

Concurrency and risk notes:
- Active references protect `kn->attr.ops`; open-file mutex serializes callbacks for one open file.
- The `ERR_PTR(-ENODEV)` seq iteration convention is delicate because custom seq ops may return the same sentinel.
- Release and drain paths intentionally avoid `of->mutex` to prevent lock dependency cycles.
- Notification list uses a self-pointer end marker and spinlock; incorrect `notify_next` handling could lose events or leak node refs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/kernfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/kernfs/inode.c -->
# File Research: sources/os/linux/linux/fs/kernfs/inode.c

Purpose: Provides kernfs inode operations, persistent inode attributes, xattr storage, inode creation/refresh, permission checks, and eviction behavior.

Key functionality:
- Lazily allocates `struct kernfs_iattrs` with default uid/gid/timestamps and simple xattr limits.
- `kernfs_setattr()` and VFS `kernfs_iop_setattr()` update persistent kernfs attributes and mirror them into live inodes.
- `kernfs_refresh_inode()` copies mode/attrs from `kernfs_node` to inode and maintains directory link counts.
- `kernfs_get_inode()` uses `iget_locked()` keyed by kernfs inode number and initializes file, dir, or symlink operations by node type.
- Xattr handlers expose trusted/security/user xattrs, with user xattrs gated by `KERNFS_ROOT_SUPPORT_USER_XATTR`.

Dependencies and integration:
- Exports `kernfs_xattr_handlers` to `mount.c` for superblock setup.
- Uses `ram_aops` from `libfs.c` for kernfs file mappings.
- References `kernfs_dir_iops`, `kernfs_dir_fops`, `kernfs_file_fops`, and `kernfs_symlink_iops`.

Concurrency and risk notes:
- Attribute updates are protected by `root->kernfs_iattr_rwsem`.
- Xattr modification uses the hashed per-node kernfs mutex because multiple superblocks/namespaces can share one node.
- Lazy allocation uses `try_cmpxchg()` to avoid duplicate persistent attribute installation.
- `kernfs_iop_permission()` returns `-ECHILD` for RCU/MAY_NOT_BLOCK permission checks, forcing blocking revalidation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/kernfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/kernfs/kernfs-internal.h -->
# File Research: sources/os/linux/linux/fs/kernfs/kernfs-internal.h

Purpose: Internal kernfs header defining private root, superblock, inode-attribute, dentry helper, and lock helper contracts shared by kernfs implementation files.

Key definitions:
- `struct kernfs_iattrs` stores persistent uid/gid/timestamps and simple xattrs.
- `struct kernfs_root` owns node ID allocation, syscall ops, superblock list, rwsems, rename lock, deactivate waitqueue, and xattr cache.
- `struct kernfs_super_info` maps a superblock to a kernfs root and namespace tag.
- Inline helpers derive root, parent, names, dentry nodes, directory revision checks, and per-node hashed mutexes.
- Declares cross-file operations for inode, dir, file, symlink, and mount support.

Dependencies and integration:
- Includes public `linux/kernfs.h` and VFS/fs_context/xattr headers.
- `kernfs_root()` uses RCU parent dereference and assumes parent nodes are directories.
- Hashed locks come from global `kernfs_locks`, initialized in `mount.c`.

Concurrency and risk notes:
- Parent/name access helpers encode lockdep expectations for `kernfs_rwsem`, rename lock, RCU, and dead-node cases.
- `kernfs_node_lock_ptr()` hashes node addresses, so unrelated nodes may serialize on the same mutex.
- This header is central to lock ordering and lifetime assumptions across kernfs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/kernfs/kernfs-internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/kernfs/mount.c -->
# File Research: sources/os/linux/linux/fs/kernfs/mount.c

Purpose: Implements kernfs superblock creation, mount retrieval, export file handles, path display hooks, kill_sb cleanup, and global kernfs cache/lock initialization.

Key functionality:
- Defines `kernfs_sops` with statfs, inode eviction, show_options/show_path, and explicit no freeze/thaw behavior.
- Provides export operations for encoding kernfs node IDs and resolving file handles back to dentries.
- `kernfs_node_dentry()` reconstructs a dentry path for invariant-parent roots by walking ancestor names.
- `kernfs_fill_super()` configures superblock flags, xattrs, export ops, root inode/dentry, and dentry ops.
- `kernfs_get_tree()` shares or creates anonymous superblocks based on root and namespace tag.
- `kernfs_kill_sb()` removes the superblock from the root’s mounted-super list and frees `kernfs_super_info`.
- `kernfs_init()` creates slab caches and initializes global hashed node mutexes.

Dependencies and integration:
- Uses `kernfs_get_inode()` from `inode.c`, `kernfs_dops` from dir code, and `kernfs_xattr_handlers`.
- Superblock list is consumed by `kernfs_notify_workfn()` in `file.c`.
- Export support depends on `kernfs_find_and_get_node_by_id()` and parent lookup helpers outside this file.

Concurrency and risk notes:
- Superblock list updates are protected by `kernfs_supers_rwsem`; root tree walks use `kernfs_rwsem`.
- `kernfs_set_super()` clears `kfc->ns_tag`, transferring ownership expectations to the new superblock setup.
- `kernfs_node_dentry()` requires `KERNFS_ROOT_INVARIANT_PARENT`; otherwise it returns `-EINVAL`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/kernfs/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/kernfs/symlink.c -->
# File Research: sources/os/linux/linux/fs/kernfs/symlink.c

Purpose: Implements kernfs symlink creation and VFS symlink resolution.

Key functionality:
- `kernfs_create_link()` creates a `KERNFS_LINK` node, copies target ownership if persistent attrs exist, optionally copies namespace tag, stores `target_kn`, and holds a reference on the target.
- `kernfs_get_target_path()` builds a relative path from symlink parent to target, walking up to a common base and then reverse-filling target components.
- `kernfs_iop_get_link()` allocates a page-sized path buffer, resolves the link under `kernfs_rwsem`, and returns it via delayed cleanup.
- `kernfs_symlink_iops` wires get_link plus shared kernfs xattr, setattr, getattr, and permission operations.

Dependencies and integration:
- Uses `kernfs_new_node()`, `kernfs_add_one()`, `kernfs_parent()`, and `kernfs_rcu_name()`.
- Shares inode operation helpers from `inode.c`.

Risk notes:
- Path construction is bounded by `PATH_MAX` and returns `-ENAMETOOLONG` on overflow.
- Relative-path generation assumes stable parent/name relationships while `root->kernfs_rwsem` is held.
- A target reference is owned by the symlink node and released through normal kernfs node cleanup paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/kernfs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/libfs.c -->
# File Research: sources/os/linux/linux/fs/libfs.c

Purpose: General VFS helper library for simple/pseudo filesystems, directory iteration, page-cache-backed in-memory files, transaction attributes, export file handles, casefolding/encryption dentry ops, inode versioning, direct-I/O fallback, and stashed anonymous dentries.

Major helper families:
- Basic stat/lookup/directory helpers: `simple_getattr()`, `simple_statfs()`, `simple_lookup()`, `simple_dir_operations`, `dcache_readdir()`.
- Stable directory offsets: `simple_offset_*`, `simple_offset_dir_operations`, and maple-tree-backed offset assignment/removal/rename support.
- Recursive removal: `simple_recursive_removal()`, `locked_recursive_removal()`, and `simple_remove_by_name()`.
- Pseudo filesystem setup: `init_pseudo()`, `pseudo_fs_fill_super()`, and pseudo fs_context operations.
- Simple inode operations: link, unlink, rmdir, rename, setattr, empty-dir helpers, symlink helpers, anonymous inode allocation.
- Ram/page-cache helpers: `ram_aops`, `simple_write_begin()`, `simple_write_end()`, `simple_fill_super()`.
- Buffer helpers: `simple_read_from_buffer()`, `simple_write_to_buffer()`, `memory_read_from_buffer()`.
- Transaction and simple attribute helpers: `simple_transaction_*`, `simple_attr_*`.
- Exportfs helpers: `generic_encode_ino32_fh()`, `generic_fh_to_dentry()`, `generic_fh_to_parent()`.
- Sync/addressability: `simple_fsync_noflush()`, `simple_fsync()`, `generic_check_addressable()`, `noop_fsync()`, `noop_direct_IO()`.
- Casefold/encryption: `generic_ci_d_compare()`, `generic_ci_d_hash()`, `generic_ci_match()`, `generic_set_sb_d_ops()`.
- I_version and I/O fallback: `inode_maybe_inc_iversion()`, `inode_query_iversion()`, `direct_write_fallback()`.
- Stashed dentries: `stashed_dentry_get()`, `stash_dentry()`, `path_from_stashed()`, `stashed_dentry_prune()` for nsfs/pidfs-style paths.

Dependencies and integration:
- Exports many symbols used by in-kernel filesystems, including kernfs (`ram_aops`, simple xattr/stat helpers), procfs-like files, pseudo filesystems, and exportfs clients.
- Uses VFS dentries/inodes, maple tree, fscrypt, Unicode casefolding, writeback, block flush, and mount/fs_context APIs.

Concurrency and risk notes:
- Directory iteration relies on dentry locks, inode rwsem, cursor dentries, and rescheduling-safe scans.
- Offset maps require caller serialization for rename/remove paths.
- Transaction files allow only one write per open and use a static spinlock to serialize `private_data` installation.
- I_version helpers rely on explicit memory barriers paired between query and increment paths.
- `direct_write_fallback()` must preserve O_DIRECT semantics by writing back and invalidating buffered fallback ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/libfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/Makefile -->
# File Research: sources/os/linux/linux/fs/lockd/Makefile

Purpose: Builds the Linux lockd module and documents regeneration of generated NLMv4 XDR files.

Key behavior:
- Adds `-I$(src)` for trace event headers.
- Builds `lockd.o` when `CONFIG_LOCKD` is enabled.
- Core objects include client lock/proc/xdr, host, service, server lock/share/subs, monitor, trace, generic xdr, and netlink.
- Adds NLMv4 client/server/generated XDR objects under `CONFIG_LOCKD_V4`.
- Adds procfs support under `CONFIG_PROC_FS`.
- Provides `make xdrgen` targets to regenerate `nlm4xdr_gen.{h,c}` and shared definitions from `Documentation/sunrpc/xdr/nlm4.x`.

Risk notes:
- Generated files are checked in, so normal builds do not require Python xdrgen tooling.
- Changing XDR specs without regenerating committed generated files would desynchronize server decode/encode declarations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/clnt4xdr.c -->
# File Research: sources/os/linux/linux/fs/lockd/clnt4xdr.c

Purpose: Client-side XDR encoder/decoder for NLM version 4 RPC calls.

Key functionality:
- Defines XDR word-size estimates for NLMv4 request/reply types.
- Clamps Linux `loff_t` ranges to NLMv4 signed 64-bit wire limits.
- Encodes cookies, caller names, file handles, owner handles, locks, lockargs, cancelargs, unlockargs, and result/test replies.
- Decodes cookies, NLMv4 statuses, and denied-lock holder data.
- Maps holder offsets into `struct file_lock` using `lockd_set_file_lock_range4()`.
- Exposes `nlm_version4` RPC version table with all standard NLM procedures.

Dependencies and integration:
- Used by the NLM client RPC program table in `clntxdr.c` when `CONFIG_LOCKD_V4` is enabled.
- Depends on `struct nlm_args`, `struct nlm_res`, and status constants from `lockd.h`/`nlm.h`.

Risk notes:
- Wire status values are intentionally kept in network byte order for upper layers.
- Cookie decode accepts empty HPUX cookies by substituting a zero 4-byte cookie.
- Invalid status enum values or oversized cookies return `-EIO`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/clnt4xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/clntlock.c -->
# File Research: sources/os/linux/linux/fs/lockd/clntlock.c

Purpose: Client-side lock blocking, grant callback matching, NFS mount initialization/cleanup, and lock reclaim after server reboot.

Key functionality:
- `nlmclnt_init()` starts lockd, finds/binds an NLM host, and installs client callbacks.
- `nlmclnt_done()` releases the host and decrements lockd service usage.
- Maintains global `nlm_blocked` wait list protected by `nlm_blocked_lock`.
- `nlmclnt_grant()` matches GRANTED callbacks by range, owner pid, remote address, and file handle, then wakes waiting lockers.
- `nlmclnt_recovery()` spawns a reclaim thread per host reboot.
- `reclaimer()` rebinds the host, reclaims granted locks, handles repeated reboot state changes, and wakes blocked waiters with grace-period status.

Dependencies and integration:
- Uses `lockd_up/down`, host lookup/bind/release from `host.c`, and reclaim RPC from `clntproc.c`.
- Compares file handles through NFS helpers and emits tracepoints.

Risk notes:
- Grant matching explicitly avoids using cookies because servers do not reliably echo the original blocking request cookie.
- Reclaimer uses host `h_rwsem` to serialize recovery against normal lock operations.
- Failed reclaimer thread creation leaves locks unreclaimed and logs an error.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/clntlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/clntproc.c -->
# File Research: sources/os/linux/linux/fs/lockd/clntproc.c

Purpose: Implements client-side NLM TEST, LOCK, UNLOCK, CANCEL, reclaim, async RPC handling, lockowner tracking, and status-to-errno conversion.

Key functionality:
- Generates NLM cookies with an atomic counter.
- Maps VFS `fl_owner_t` to stable 32-bit NLM pseudo-pids via `struct nlm_lockowner`.
- `nlmclnt_proc()` is the main fcntl-style entry point for GETLK/SETLK/SETLKW/UNLCK.
- `nlmclnt_call()` performs synchronous RPC with grace-period retry/rebind handling.
- Async helpers support unlock/cancel/reply RPCs and task callbacks.
- `nlmclnt_lock()` handles local VFS precheck, remote lock request, blocking wait/poll loop, cancellation, reboot state check, and final local lock installation.
- `nlmclnt_unlock()` removes the local lock then sends async remote unlock.
- `nlmclnt_reclaim()` reissues reclaim LOCK calls during recovery.
- `nlm_stat_to_errno()` maps NLM wire statuses to Linux errno values.

Dependencies and integration:
- Uses NFS file credentials and file handles, host bind/rebind, NSM monitor state, VFS file-lock APIs, and tracepoints.
- Cooperates with `clntlock.c` for blocking wait queues and with `host.c` for recovery state.

Risk notes:
- Blocking lock handling is intentionally defensive against servers that return BLOCKED without later callbacks.
- Fatal/interrupted blocking paths attempt CANCEL and may send remote UNLOCK cleanup.
- Lockowner lifetime is tied to file lock private ops; missed release would leak host refs.
- Grace-period and reboot-state races are handled by retrying when host state changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/clntproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/clntxdr.c -->
# File Research: sources/os/linux/linux/fs/lockd/clntxdr.c

Purpose: Client-side XDR encoder/decoder for NLM versions 1 and 3, plus the root `nlm_program` RPC program table.

Key functionality:
- Defines XDR size estimates for NLMv1/v3 procedures.
- Clamps lock offsets to 32-bit NLM wire limits.
- Encodes/decodes cookies, fixed NFSv2 file handles, lock owners, lock ranges, statuses, test replies, and generic result replies.
- Creates RPC procedure tables for NLMv1 and NLMv3.
- Builds `nlm_versions[]`, optionally including `nlm_version4` from `clnt4xdr.c`.
- Exports `nlm_program`.

Dependencies and integration:
- Used by `host.c` when creating RPC clients for lockd peers.
- Shares upper-layer `nlm_args`/`nlm_res` structures with `clntproc.c`.

Risk notes:
- NLMv2 is intentionally not implemented.
- Wire status values remain network byte order.
- 32-bit range conversion treats zero length or overflow as lock-to-EOF.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/clntxdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/host.c -->
# File Research: sources/os/linux/linux/fs/lockd/host.c

Purpose: Manages shared client/server `nlm_host` cache, RPC client binding, NSM handle sharing, host garbage collection, reboot notification dispatch, and per-net shutdown.

Key functionality:
- Maintains separate hash tables for client and server hosts keyed by peer address.
- `nlmclnt_lookup_host()` finds or creates client peer handles by address/protocol/version.
- `nlmsvc_lookup_host()` finds or creates server-side client handles, including source address matching.
- `nlm_bind_host()` lazily creates RPC clients with lockd program/version/protocol settings.
- `nlm_rebind_host()` forces UDP portmapper rebinding after timeout.
- `nlm_host_rebooted()` maps NSM notify cookies to hosts and triggers server cleanup or client recovery.
- `nlm_shutdown_hosts_net()` expires hosts in a net namespace, shuts down RPC clients, frees resources, and runs GC.
- `nlm_gc_hosts()` mark-and-sweeps unused server hosts.

Dependencies and integration:
- Uses `nsm_get_handle()`, `nsm_unmonitor()`, `nsm_reboot_lookup()` from `mon.c`.
- Calls server resource functions (`nlmsvc_mark_resources()`, `nlmsvc_free_host_resources()`) outside this work item.
- Uses `lockd_net` namespace state from `netns.h`.

Concurrency and risk notes:
- Global host cache is protected by `nlm_host_mutex`; individual RPC binding uses `host->h_mutex`.
- Client hosts are destroyed immediately on final ref; server hosts are GC’d after expiry/resources clear.
- Reboot notification loops drop and reacquire the global mutex, using NSM state to avoid processing a host repeatedly.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/host.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/lockd.h -->
# File Research: sources/os/linux/linux/fs/lockd/lockd.h

Purpose: Central internal lockd header defining debug flags, core host/request/file/block/share structures, status constants, function prototypes, and inline helpers.

Key definitions:
- Debug facility flags and default version/timeout constants.
- Internal status codes that must not be placed on the wire.
- `struct nlm_host` for client/server peer state, RPC client, recovery, lockowners, granted/reclaim lists, NSM handle, namespace, and credentials.
- `struct nsm_handle`, `struct nlm_lockowner`, `struct nlm_wait`, `struct nlm_rqst`, `struct nlm_file`, and `struct nlm_block`.
- Global externs for RPC programs, server versions, grace period, timeout, NSM state, and retry timer.
- Prototypes for client, host, monitor, server lock, file, share, and resource operations.
- Inline helpers for sockaddr access, privileged requester checks, lock comparison, and NLMv4 range conversion.

Dependencies and integration:
- Pulls in protocol declarations from `nlm.h`, generated/user-facing bind headers, and lockd XDR headers.
- Shared by nearly every lockd implementation file.

Risk notes:
- Struct fields encode many lifetime relationships: host refs, lockowner refs, granted/reclaim lists, RPC task refs, and server block refs.
- `nlm_privileged_requester()` accepts only loopback privileged-port senders for certain local requests.
- `lockd_set_file_lock_range4()` clamps and handles overflow in NLMv4 range conversion.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/lockd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/mon.c -->
# File Research: sources/os/linux/linux/fs/lockd/mon.c

Purpose: Kernel client for the Network Status Monitor service (`rpc.statd`), including peer monitor/unmonitor upcalls, NSM handle caching, reboot notification matching, and NSM XDR.

Key functionality:
- Creates loopback TCP RPC clients to `rpc.statd` program 100024 version 1.
- `nsm_monitor()` sends MON requests and records local NSM state.
- `nsm_unmonitor()` sends UNMON when the last non-sticky reference is released.
- Caches `nsm_handle` objects per net namespace by hostname or address depending on `nsm_use_hostnames`.
- Rejects hostnames containing `/`.
- Generates private cookies from timestamp and handle address to match later notify callbacks.
- `nsm_reboot_lookup()` matches incoming reboot private data to cached handles.
- Encodes NSM MON/UNMON arguments and decodes monitor/stat results.

Dependencies and integration:
- Used by `host.c` for host allocation, destruction, and reboot processing.
- Uses `lockd_net.nsm_handles`.
- Uses SUNRPC client and XDR stream APIs.

Risk notes:
- NSM upcalls are local loopback RPCs but still subject to statd availability and connection refusal.
- The private cookie is designed to be unique across runtime and reboots, but stale/corrupt user-space notifications are still ignored only by cache mismatch.
- `nsm_use_hostnames` changes cache matching behavior, affecting handle reuse and monitor identity.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/mon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/netlink.c -->
# File Research: sources/os/linux/linux/fs/lockd/netlink.c

Purpose: Auto-generated generic netlink family definition for lockd server configuration commands.

Key functionality:
- Defines policy for `LOCKD_CMD_SERVER_SET` attributes: grace time, TCP port, UDP port.
- Registers split ops for `LOCKD_CMD_SERVER_SET` and `LOCKD_CMD_SERVER_GET`.
- Requires admin permission for set operations.
- Defines `lockd_nl_family` with namespace support and parallel ops enabled.

Dependencies and integration:
- Includes generated `netlink.h` and UAPI `linux/lockd_netlink.h`.
- Handler implementations `lockd_nl_server_set_doit()` and `lockd_nl_server_get_doit()` are declared elsewhere in this generated interface.

Risk notes:
- File is generated from `Documentation/netlink/specs/lockd.yaml`; manual edits are not durable.
- Policy bounds are tied to UAPI enum values.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/netlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/netlink.h -->
# File Research: sources/os/linux/linux/fs/lockd/netlink.h

Purpose: Auto-generated header for lockd generic netlink handlers and family object.

Key contents:
- Includes netlink/genetlink and lockd UAPI netlink definitions.
- Declares `lockd_nl_server_set_doit()`, `lockd_nl_server_get_doit()`, and external `lockd_nl_family`.

Dependencies and integration:
- Consumed by `netlink.c` and handler implementation code.
- Generated from `Documentation/netlink/specs/lockd.yaml`.

Risk notes:
- Must remain synchronized with generated `netlink.c` and UAPI command/attribute definitions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/netlink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/netns.h -->
# File Research: sources/os/linux/linux/fs/lockd/netns.h

Purpose: Defines per-network-namespace lockd state.

Key fields:
- `nlmsvc_users` tracks users of the lockd service in a namespace.
- `next_gc`, `nrhosts` support host cache garbage collection/accounting.
- `gracetime`, `tcp_port`, `udp_port` store configurable server settings.
- `grace_period_end` delayed work and `lockd_manager` coordinate grace-period lock management.
- `nsm_handles` holds cached NSM monitor handles.

Dependencies and integration:
- Used by host management, monitor cache, procfs grace endpoint, and netlink/server configuration.
- Exposes `lockd_net_id` for `net_generic()` lookups.

Risk notes:
- Namespace-local state affects host GC, NSM identity cache, and grace management; handlers must use the correct current/request namespace.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/netns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/nlm.h -->
# File Research: sources/os/linux/linux/fs/lockd/nlm.h

Purpose: Declares core Network Lock Manager protocol constants.

Key contents:
- Defines NLMv1/v3 and NLMv4 maximum offset values.
- Enumerates lock status codes, with NLMv4-only extended errors under `CONFIG_LOCKD_V4`.
- Defines NLM RPC program number 100021.
- Defines procedure numbers for lock, unlock, cancel, async msg/res procedures, NSM notify, share/unshare, non-monitored lock, and free-all.

Dependencies and integration:
- Included by `lockd.h` and XDR/procedure table implementations.
- Status constants are used both as CPU values and converted to big-endian wire constants in `lockd.h`.

Risk notes:
- Procedure/status numeric values are protocol ABI and must not change.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/nlm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/nlm4xdr_gen.c -->
# File Research: sources/os/linux/linux/fs/lockd/nlm4xdr_gen.c

Purpose: Generated server-side XDR encode/decode helpers for NLMv4 service procedures.

Key functionality:
- Decodes primitive and compound NLMv4 types: netobj, modes/access, 32/64-bit integers, stats, holder, lock, lockargs, cancelargs, testargs, unlockargs, shareargs, notifyargs, and result types.
- Provides exported service decode wrappers such as `nlm4_svc_decode_nlm4_lockargs()` that read into `rqstp->rq_argp`.
- Encodes response/result types: void, testres, res, shareres.
- Enforces maximum string sizes for caller names and notify names during encode/decode.

Dependencies and integration:
- Includes generated declarations from `nlm4xdr_gen.h` and XDR type definitions from `linux/sunrpc/xdrgen/nlm4.h`.
- Used by the NLMv4 server procedure implementation outside this work item.
- Generated by xdrgen from `Documentation/sunrpc/xdr/nlm4.x`.

Risk notes:
- Manual edits will be lost.
- Generated code returns boolean success/failure; callers must translate decode/encode failure to appropriate RPC handling.
- It uses generated XDR builtins, so compatibility depends on synchronized generated headers and shared type definitions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/nlm4xdr_gen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/nlm4xdr_gen.h -->
# File Research: sources/os/linux/linux/fs/lockd/nlm4xdr_gen.h

Purpose: Generated declarations for NLMv4 service-side XDR encode/decode helpers.

Key contents:
- Includes XDR stream, xdrgen builtins, and generated NLMv4 type definitions.
- Declares decode wrappers for void, testargs, lockargs, cancelargs, unlockargs, testres, res, notifyargs, shareargs, and notify.
- Declares encode wrappers for void, testres, res, and shareres.

Dependencies and integration:
- Included by `nlm4xdr_gen.c` and NLMv4 service code.
- Generated from `Documentation/sunrpc/xdr/nlm4.x`.

Risk notes:
- Must match the generated source and XDR type definitions exactly.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/nlm4xdr_gen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/procfs.c -->
# File Research: sources/os/linux/linux/fs/lockd/procfs.c

Purpose: Provides `/proc/fs/lockd/nlm_end_grace` for reading and ending lockd grace-period state.

Key functionality:
- Write accepts strings beginning with `Y`, `y`, or `1` and calls `locks_end_grace()` for the current network namespace’s `lockd_manager`.
- Read returns `Y\n` when the grace list is empty, otherwise `N\n`.
- Uses `simple_transaction_get()` for write buffering and `simple_transaction_release()` on release.
- `lockd_create_procfs()` creates `fs/lockd` and `nlm_end_grace`.
- `lockd_remove_procfs()` removes both entries.

Dependencies and integration:
- Uses current task net namespace through `current->nsproxy->net_ns`.
- Depends on `lockd_net_id` and `struct lockd_net`.

Risk notes:
- Write parser only inspects the first byte.
- Proc entry is writable by owner/root only and readable by all.
- Namespace selection follows current task namespace at operation time.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/procfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/procfs.h -->
# File Research: sources/os/linux/linux/fs/lockd/procfs.h

Purpose: Declares lockd procfs setup/teardown with no-op fallbacks when procfs is disabled.

Key contents:
- Under `CONFIG_PROC_FS`, declares `lockd_create_procfs()` and `lockd_remove_procfs()`.
- Otherwise provides inline stubs returning success and doing nothing.

Dependencies and integration:
- Included by lockd service/module initialization code.

Risk notes:
- Callers can unconditionally call procfs setup/teardown regardless of configuration.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/procfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/lockd/share.h -->
# File Research: sources/os/linux/linux/fs/lockd/share.h

Purpose: Declares DOS share tracking structures and server-side share operation APIs for lockd.

Key contents:
- Defines synthetic `LOCKD_SHARE_SVID` for lockowner lookup during share operations.
- `struct nlm_share` links a host, file, owner handle, access mode, and deny mode.
- Declares `nlmsvc_share_file()`, `nlmsvc_unshare_file()`, and `nlmsvc_traverse_shares()`.

Dependencies and integration:
- Used by lockd server share implementation and resource traversal/GC.
- Depends on `struct nlm_host`, `struct nlm_file`, and `nlm_host_match_fn_t` from `lockd.h`.

Risk notes:
- Share ownership is represented by XDR netobj owner handles, so comparisons must respect length and data, not C strings.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/lockd/share.h -->