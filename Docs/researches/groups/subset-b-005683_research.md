# subset-b-005683 Research

Grouped source research for kernfs file/inode/mount/symlink internals, generic VFS helper code in `fs/libfs.c`, and lockd client/host/monitoring/XDR support. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/file.c -->
# sources/distributed-fs/ceph-client/fs/kernfs/file.c

## Purpose

`sources/distributed-fs/ceph-client/fs/kernfs/file.c` implements regular-file behavior for kernfs nodes. It turns `struct kernfs_ops` callbacks into VFS file operations for sysfs/cgroup-style pseudo files, covering seq-file reads, binary reads and writes, mmap wrapping, open/release lifetime, poll notification, and file node creation. The source was read as a complete 1092-line file.

## Important APIs, Types, and Functions

The central private type is `struct kernfs_open_node`, which stores the shared per-node open-file list, poll event counter, mmap count, and release-drain count. Key helpers are `kernfs_fop_open`, `kernfs_fop_release`, `kernfs_fop_read_iter`, `kernfs_fop_write_iter`, `kernfs_fop_mmap`, `kernfs_fop_poll`, `kernfs_fop_llseek`, `kernfs_notify`, `kernfs_should_drain_open_files`, `kernfs_drain_open_files`, and `__kernfs_create_file`. `kernfs_file_fops` exports these operations to inodes initialized by `inode.c`.

## Control Flow

Open takes an active reference, validates optional extra permission checks, allocates `kernfs_open_file`, initializes seq_file state, attaches it to the node's shared `kernfs_open_node`, and calls `ops->open` if present. Reads use seq_file when `KERNFS_HAS_SEQ_SHOW` is set; otherwise a PAGE_SIZE or preallocated buffer is filled by `ops->read` under the open-file mutex and active reference. Writes copy one bounded user buffer, NUL-terminate it, then call `ops->write`; partial-write semantics are intentionally not supported. Mmap verifies `KERNFS_HAS_MMAP`, delegates setup to `ops->mmap`, rejects close callbacks, and installs wrapper VM ops that reacquire active references before forwarding faults/access/write faults. Notification increments the poll event immediately, wakes waiters, and queues work that emits fsnotify modify events for all mounted superblocks.

## State and Persistence Behavior

State is in memory only. `kn->attr.open` is RCU-published while open files exist and freed via `kfree_rcu`. Per-open buffers may be allocated once when `ops->prealloc` is enabled. `of->event` snapshots `open_node->event` so poll can report changes after reads. Drain state (`nr_mmapped`, `nr_to_release`, `released`) ensures release callbacks and mmap invalidation happen during node deactivation even if user file descriptors remain.

## Dependencies and Integration Points

This file depends on kernfs active-reference machinery from `dir.c`, inode setup from `inode.c`, mount superblock lists from `mount.c`, seq_file, VFS file operations, mm/VMA callbacks, wait queues, fsnotify, RCU, and hashed `kernfs_locks->open_file_mutex` from `kernfs-internal.h`. `__kernfs_create_file` is the construction point used by external kernfs users.

## Risks and Edge Cases

The main risks are active-reference imbalance, release called more than once, mmap close callbacks that cannot be wrapped, lockdep false positives around mmap and writable sysfs files, users expecting partial writes, and notification races across RCU-published open nodes. Custom seq operations returning `ERR_PTR(-ENODEV)` require the special stop path to avoid double put-active or leaks.

## Test Signals

Useful signals include sysfs/kernfs read/write/mmap/poll tests, KASAN/KCSAN/lockdep during concurrent open, remove, notify, and mmap fault workloads, tests for prealloc plus atomic write length, release-drain tests during node deletion, and fsnotify/poll event tests across multiple kernfs mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/kernfs/inode.c

## Purpose

`sources/distributed-fs/ceph-client/fs/kernfs/inode.c` maps persistent `kernfs_node` metadata into VFS inodes. It handles inode allocation and eviction, attribute storage, permission/getattr/setattr, and trusted/security/user xattrs for kernfs-based filesystems. The source was read as a complete 406-line file.

## Important APIs, Types, and Functions

Important entry points are `kernfs_get_inode`, `kernfs_evict_inode`, `kernfs_iop_permission`, `kernfs_iop_setattr`, `kernfs_iop_getattr`, `kernfs_iop_listxattr`, `kernfs_setattr`, `__kernfs_setattr`, `kernfs_xattr_get`, and `kernfs_xattr_set`. The private attribute allocator `__kernfs_iattrs` lazily creates `struct kernfs_iattrs`, whose layout is declared in `kernfs-internal.h`. `kernfs_xattr_handlers` registers VFS xattr handlers.

## Control Flow

`kernfs_get_inode` uses `iget_locked` on `kernfs_ino(kn)` and initializes new inodes through `kernfs_init_inode`. Initialization pins the node, installs `ram_aops`, sets default timestamps, refreshes attributes, and then chooses directory, regular-file, or symlink operations. `setattr` and `getattr` take `root->kernfs_iattr_rwsem` so inode-visible attributes and persistent kernfs attributes stay coherent. Xattr handlers translate VFS prefix/suffix pairs into full names, lazily allocate simple xattr storage, and enforce user-xattr support only when the root opts in.

## State and Persistence Behavior

Metadata is persistent for the lifetime of the `kernfs_node`, not the transient inode. `kn->iattr` stores uid, gid, atime, mtime, ctime, xattrs, and xattr limits after first non-default use. Inode eviction truncates page cache, clears the inode, and drops the node reference taken during initialization.

## Dependencies and Integration Points

The file integrates with `kernfs_file_fops`, `kernfs_dir_iops`, `kernfs_dir_fops`, and `kernfs_symlink_iops`. It depends on `ram_aops` and `simple_inode_init_ts` from `libfs.c`, simple xattr helpers, VFS permission and setattr helpers, and root-level locks from `kernfs-internal.h`.

## Risks and Edge Cases

Lazy `kn->iattr` allocation can race, so `try_cmpxchg` correctness matters. Size changes are deliberately ignored in kernfs setattr. User xattrs must remain gated by `KERNFS_ROOT_SUPPORT_USER_XATTR`; otherwise pseudo filesystems could expose unexpected mutable metadata. Directory link counts depend on `kn->dir.subdirs` and must not be refreshed for removing nodes.

## Test Signals

Use inode lifetime tests around lookup/eviction, chmod/chown/timestamp tests across inode drop and relookup, xattr get/set/list tests for trusted/security/user prefixes, lockdep coverage for `kernfs_iattr_rwsem`, and sysfs/kernfs permission tests with and without user-xattr root support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/kernfs-internal.h -->
# sources/distributed-fs/ceph-client/fs/kernfs/kernfs-internal.h

## Purpose

`sources/distributed-fs/ceph-client/fs/kernfs/kernfs-internal.h` is the private coordination header for kernfs implementation files. It defines root and superblock-private state, inode attribute storage, lock helpers, dentry/node helpers, revision helpers, and cross-file prototypes. The source was read as a complete 214-line file.

## Important APIs, Types, and Functions

Key types are `struct kernfs_iattrs`, `struct kernfs_root`, and `struct kernfs_super_info`. Important inline helpers include `kernfs_root`, `kernfs_root_is_locked`, `kernfs_rename_is_locked`, `kernfs_rcu_name`, `kernfs_parent`, `kernfs_dentry_node`, `kernfs_set_rev`, `kernfs_inc_rev`, and `kernfs_dir_changed`. The header declares `kernfs_sops`, global slab caches, directory/file/symlink operation tables, inode hooks, and open-file drain helpers.

## Control Flow

The header has no runtime flow by itself, but its inlines define the rules for traversing kernfs parent/name state. `kernfs_root` walks to a parent under RCU because non-root nodes derive root through their parent directory. `kernfs_parent` uses RCU with lockdep checks that allow dereference when the root rwsem, rename lock, or final node teardown makes the parent stable.

## State and Persistence Behavior

`kernfs_root` owns the inode IDR, root flags, syscall hooks, superblock list, deactivate wait queue, hierarchy rwsem, iattr rwsem, superblock rwsem, rename lock, and RCU lifetime. `kernfs_super_info` binds each superblock to one root and one namespace tag. `kernfs_iattrs` persists inode metadata and simple xattrs in the node.

## Dependencies and Integration Points

This header ties together `mount.c`, `inode.c`, `dir.c`, `file.c`, and `symlink.c`; it also exposes the hashed global lock table used by open-file state. It depends on public `<linux/kernfs.h>`, VFS, xattr, fs_context, mutex, rwsem, RCU, and lockdep APIs.

## Risks and Edge Cases

Incorrect parent/name dereference outside the documented locks can race with rename or reparenting. The root/superblock namespace model assumes a single namespace tag per superblock. Revision helpers are simple counters, so users must update them consistently on directory mutations to keep dcache validation reliable.

## Test Signals

Signals include lockdep/RCU-sched validation during rename, lookup, unmount, and notification; build coverage across all kernfs implementation files; namespace-mount tests that compare `kernfs_super_info` matching; and directory revalidation tests that depend on `dir.rev` and dentry `d_time`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/kernfs-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/mount.c -->
# sources/distributed-fs/ceph-client/fs/kernfs/mount.c

## Purpose

`sources/distributed-fs/ceph-client/fs/kernfs/mount.c` implements kernfs superblock setup, mount lookup, export handles, namespace matching, superblock teardown, and early kernfs cache/lock initialization. The source was read as a complete 472-line file.

## Important APIs, Types, and Functions

Important exports are `kernfs_root_from_sb`, `kernfs_node_dentry`, `kernfs_super_ns`, `kernfs_get_tree`, `kernfs_free_fs_context`, `kernfs_kill_sb`, and `kernfs_init`. Internal components include `kernfs_sops`, `kernfs_export_ops`, `kernfs_fill_super`, `kernfs_test_super`, `kernfs_set_super`, `kernfs_encode_fh`, `kernfs_fh_to_dentry`, and `kernfs_fh_to_parent`.

## Control Flow

`kernfs_get_tree` allocates `kernfs_super_info`, sets the root/ns pair, and calls `sget_fc` so mounts sharing the same root and namespace reuse a superblock. If a new superblock is created, `kernfs_fill_super` installs kernfs super operations, xattr handlers, optional export ops, UUID, root inode, root dentry, and default dentry operations, then links the superblock into `root->supers`. `kernfs_kill_sb` removes that list entry before killing the anonymous superblock and freeing `kernfs_super_info`. Export decoding maps file handles back to kernfs IDs and then to inodes/dentries.

## State and Persistence Behavior

The persistent state is in `kernfs_root`: slab caches are global after `kernfs_init`, while each live superblock contributes one `kernfs_super_info` list node under `kernfs_supers_rwsem`. File handles persist only as encoded kernfs node IDs plus generation-compatible support for generic 32-bit handles.

## Dependencies and Integration Points

The file integrates kernfs with fs_context, anonymous superblocks, exportfs, statfs, fsnotify path display, xattr handlers from `inode.c`, dentry operations from `dir.c`, and node lookup by ID from kernfs core code. `file.c` notification uses `root->supers` to issue fsnotify events across mounts.

## Risks and Edge Cases

Superblock matching must include namespace tags or different namespace views can alias. `kernfs_node_dentry` requires `KERNFS_ROOT_INVARIANT_PARENT` because it walks ancestors outside continuous locking. Export handle decoding can return `-ESTALE` for removed nodes. Freeze support is explicitly disabled to avoid sysfs power-management deadlocks.

## Test Signals

Useful tests include repeated mount/remount/unmount with shared roots and namespaces, exportfs file-handle encode/decode tests, cgroup/sysfs dentry reconstruction for deep nodes, lockdep for super list rwsem use, UUID/statfs checks, and unmount races with notification work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/symlink.c -->
# sources/distributed-fs/ceph-client/fs/kernfs/symlink.c

## Purpose

`sources/distributed-fs/ceph-client/fs/kernfs/symlink.c` implements kernfs symlink node creation and dynamic relative target path generation for VFS `get_link`. The source was read as a complete 155-line file.

## Important APIs, Types, and Functions

The exported creation API is `kernfs_create_link`. Internal helpers are `kernfs_get_target_path`, `kernfs_getlink`, and `kernfs_iop_get_link`. `kernfs_symlink_iops` wires symlink lookup behavior together with common kernfs xattr, setattr, getattr, and permission operations.

## Control Flow

Creation inherits target ownership if target attributes exist, allocates a `KERNFS_LINK` node with mode `0777`, copies namespace tagging from the target when parent namespace support is enabled, stores `target_kn`, takes a reference to the target, and adds the node to the tree. Link resolution allocates a PAGE_SIZE buffer, takes `root->kernfs_rwsem`, computes the relative path from the symlink parent to the target by walking up to a common base and then reverse-filling target names, and returns the buffer via delayed-call cleanup.

## State and Persistence Behavior

The symlink node owns a reference to `target_kn`; path strings are generated on demand and freed after lookup. Ownership is persisted in the symlink node mode/uid/gid and follows target attributes at creation time, not dynamically after later target ownership changes.

## Dependencies and Integration Points

The file depends on node allocation/addition from kernfs directory code, parent/name helpers from `kernfs-internal.h`, `kfree_link` from `libfs.c`, and VFS symlink `get_link` delayed-call conventions. It uses kernfs common inode operations for metadata and permissions.

## Risks and Edge Cases

Relative path synthesis can fail with `-ENAMETOOLONG` when traversal exceeds `PATH_MAX` or `-EINVAL` if no meaningful target path is produced. Correct locking around parent/name traversal is essential during rename. Namespace copying assumes target and parent namespace semantics remain compatible.

## Test Signals

Tests should cover symlinks within one directory, across sibling and ancestor paths, deep paths near `PATH_MAX`, namespace-tagged kernfs trees, target removal lifetime, and concurrent rename/readlink under lockdep and KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/libfs.c -->
# sources/distributed-fs/ceph-client/fs/libfs.c

## Purpose

`sources/distributed-fs/ceph-client/fs/libfs.c` is a broad library of VFS helpers for simple, pseudo, in-memory, exportable, casefolded, encrypted, and special-purpose filesystems. It provides directory iteration helpers, offset-stable directory maps, simple inode operations, ramfs-like address-space operations, pseudo filesystem setup, buffer/transaction/attribute helpers, export file-handle helpers, fsync helpers, inode version helpers, direct-I/O fallback handling, stashed anonymous dentries, and simple create helpers. The source was read as a complete 2314-line file.

## Important APIs, Types, and Functions

Important exported families include `simple_getattr`, `simple_statfs`, `simple_lookup`, `simple_dir_operations`, `simple_offset_*`, `simple_recursive_removal`, `init_pseudo`, `simple_open`, `simple_link`, `simple_unlink`, `simple_rmdir`, `simple_rename`, `simple_setattr`, `ram_aops`, `simple_fill_super`, `simple_pin_fs`, `simple_read_from_buffer`, `simple_write_to_buffer`, `simple_transaction_*`, `simple_attr_*`, `generic_encode_ino32_fh`, `generic_fh_to_dentry`, `generic_fh_to_parent`, `simple_fsync`, `noop_fsync`, `alloc_anon_inode`, `simple_symlink_inode_operations`, empty-directory helpers, `generic_ci_*`, `generic_set_sb_d_ops`, `inode_maybe_inc_iversion`, `inode_query_iversion`, `direct_write_fallback`, `simple_inode_init_ts`, `path_from_stashed`, `stashed_dentry_prune`, `simple_start_creating`, and `simple_done_creating`.

## Control Flow

Directory helpers either iterate positive dentries directly with a cursor (`dcache_readdir`) or preserve stable offsets through a maple-tree-backed `offset_ctx`. Simple create/remove/rename helpers update ctime/mtime/link counts and leave actual dentry mutation to the caller or VFS path. `ram_aops` zero-fills missing folios and keeps data in page cache without writeback. Pseudo filesystem setup creates anonymous nodev superblocks and a root inode. Buffer helpers enforce bounds and advance positions after user/kernel copies. Transaction helpers allow one write per open followed by readback from a per-file page. Casefold helpers integrate Unicode and fscrypt-aware name matching. Stashed dentry helpers reuse anonymous dentries for namespace/pid-style files.

## State and Persistence Behavior

Most state is caller-owned. The offset directory API stores long offsets in `dentry->d_fsdata` and the dentry pointer map in a maple tree. Simple transaction state lives in one allocated page at `file->private_data`. Simple attrs allocate per-open buffers and callbacks. Pinned pseudo filesystems share a global spinlock-protected mount pointer and refcount. Inode version helpers mutate the atomic `i_version` queried bit and counter. Stashed dentry helpers atomically publish/reuse dentries through caller-provided storage.

## Dependencies and Integration Points

The file is a core integration point for many filesystems, including kernfs via `ram_aops`, `simple_inode_init_ts`, `simple_statfs`, `noop_fsync`, and `kfree_link`. It depends on VFS dcache/inode/file APIs, maple tree, exportfs, fsnotify, fscrypt, Unicode, writeback, block flush, user access, pidfs/nsfs-style stashed operations, and pseudo fs_context support.

## Risks and Edge Cases

Directory cursor and offset-map helpers are sensitive to dentry locking and removal races. `simple_setattr` is unsuitable for real persistent size changes without filesystem-specific work. `simple_write_end` intentionally does not mark inode dirty for size changes. Transaction files reject multiple writes per open. Direct-write fallback must write back and invalidate buffered pages to preserve O_DIRECT expectations. i_version barriers must pair correctly between query and increment paths. Stashed dentry storage must be cleared on prune or stale dentries can be reused incorrectly.

## Test Signals

Coverage should include libfs selftests through ramfs/debugfs/configfs/sysfs users, directory seek/readdir stability with concurrent create/delete/rename, maple-tree offset rename and exchange tests, simple_attr read/write parse tests, transaction error paths, exportfs handle round trips, fsync/writeback error propagation, Unicode/fscrypt lookup tests, inode i_version concurrency tests, direct-I/O fallback tests, and stashed dentry lifecycle tests with prune and reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/libfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/Makefile -->
# sources/distributed-fs/ceph-client/fs/lockd/Makefile

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/Makefile` defines how the kernel Network Lock Manager module is built and how generated NLMv4 XDR source/header files are regenerated from the protocol specification. The source was read as a complete 41-line file.

## Important APIs, Types, and Functions

The build targets are `obj-$(CONFIG_LOCKD) += lockd.o`, the base `lockd-y` object list, `lockd-$(CONFIG_LOCKD_V4)` additions, `lockd-$(CONFIG_PROC_FS)` additions, and the phony `xdrgen` target. `ccflags-y += -I$(src)` supports trace event includes.

## Control Flow

Normal builds compile the checked-in generated files. Developers who modify `Documentation/sunrpc/xdr/nlm4.x` can run `make xdrgen`, which invokes `tools/net/sunrpc/xdrgen/xdrgen` to regenerate definitions, declarations, and source output.

## State and Persistence Behavior

No runtime state exists. Persistent build state is the selected object composition based on Kconfig and the checked-in generated `nlm4xdr_gen.{h,c}` plus generated public definitions under `include/linux/sunrpc/xdrgen/nlm4.h`.

## Dependencies and Integration Points

The Makefile integrates lockd client, server, host, monitor, XDR, trace, netlink, and optional procfs/NLMv4 code. It depends on Kconfig symbols `CONFIG_LOCKD`, `CONFIG_LOCKD_V4`, and `CONFIG_PROC_FS`.

## Risks and Edge Cases

Generated XDR drift is the main risk: changing the `.x` specification without regenerating all outputs can desynchronize server decode/encode declarations and implementation. Build coverage must include both v4/procfs enabled and disabled configurations.

## Test Signals

Signals are kernel build tests for `CONFIG_LOCKD=y/m`, `CONFIG_LOCKD_V4` toggles, `CONFIG_PROC_FS` toggles, trace include compilation, and a developer regeneration diff after running `make xdrgen`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/clnt4xdr.c -->
# sources/distributed-fs/ceph-client/fs/lockd/clnt4xdr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/clnt4xdr.c` implements client-side SUNRPC XDR encoding and decoding for NLM version 4. It translates internal `nlm_args` and `nlm_res` structures into the NLMv4 wire format and publishes the `rpc_version` procedure table for version 4. The source was read as a complete 582-line file.

## Important APIs, Types, and Functions

Important helpers include `nlm4_compute_offsets`, `encode_cookie`, `decode_cookie`, `encode_nlm4_lock`, `decode_nlm4_holder`, `nlm4_xdr_enc_testargs`, `nlm4_xdr_enc_lockargs`, `nlm4_xdr_enc_cancargs`, `nlm4_xdr_enc_unlockargs`, `nlm4_xdr_enc_res`, `nlm4_xdr_enc_testres`, `nlm4_xdr_dec_testres`, and `nlm4_xdr_dec_res`. The exported object is `const struct rpc_version nlm_version4`.

## Control Flow

Each RPC procedure listed in `nlm4_procedures` points at an encoder and decoder. Encoders write cookie, booleans, caller name, file handle, owner handle, pseudo pid, byte offset, byte length, reclaim flag, and state as required by the procedure. Decoders read cookies, status values, and, for denied TEST replies, a conflicting holder lock. Offset conversion maps kernel `(start,end)` locks to NLM `(offset,length)` with length zero meaning EOF.

## State and Persistence Behavior

The file owns only static procedure metadata and per-version RPC statistics counters. It does not persist lock state; encoded and decoded data live in caller-owned request/result buffers.

## Dependencies and Integration Points

It depends on `lockd.h`, NLM constants from `nlm.h`, SUNRPC XDR/client/stats helpers, and NFSv3 file-handle sizing from `uapi/linux/nfs3.h`. `clntproc.c` obtains this table through `nlm_program` when host version 4 is selected.

## Risks and Edge Cases

Offset clamping and EOF conversion must match NLMv4 semantics. Empty cookies from HPUX are normalized to a four-byte zero cookie. Invalid enum values are rejected as XDR errors. `encode_nlm4_holder` uses a read-lock/exclusive boolean that must remain consistent with protocol interpretation. Owner/caller string sizes are compile-time guarded.

## Test Signals

Use RPC encode/decode round-trip tests for TEST/LOCK/CANCEL/UNLOCK/GRANTED procedures, boundary lock ranges including EOF and overflow, invalid status enum fuzzing, empty/oversized cookie tests, and interoperability with NFSv3/NLMv4 servers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/clnt4xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/clntlock.c -->
# sources/distributed-fs/ceph-client/fs/lockd/clntlock.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/clntlock.c` manages client-side blocking lock waits, GRANTED callbacks, lockd startup/shutdown per NFS mount, and lock reclaim after server reboot. The source was read as a complete 297-line file.

## Important APIs, Types, and Functions

Important functions are `nlmclnt_init`, `nlmclnt_done`, `nlmclnt_prepare_block`, `nlmclnt_rpc_clnt`, `nlmclnt_queue_block`, `nlmclnt_dequeue_block`, `nlmclnt_wait`, `nlmclnt_grant`, `nlmclnt_recovery`, and the `reclaimer` kernel thread. Global blocked waits are tracked in `nlm_blocked` under `nlm_blocked_lock`.

## Control Flow

`nlmclnt_init` starts lockd for the mount, looks up or creates a host, binds an RPC client, and stores optional NLM client callbacks. Blocking lock acquisition queues a stack `nlm_wait` before the LOCK RPC so a GRANTED callback cannot be missed. `nlmclnt_grant` matches callbacks by range, lockowner pseudo-pid, peer address, and NFS file handle, then updates status and wakes the waiter. `nlmclnt_recovery` starts one reclaim thread per host; the reclaimer moves granted locks to a reclaim list, forces rebind, resends reclaim LOCKs, handles repeated reboots, and wakes blocked waiters with grace-period status.

## State and Persistence Behavior

The blocked list is process-local kernel memory. Granted/reclaim lock lists live on `nlm_host` and hold references through file-lock private data. Recovery state uses `host->h_reclaiming`, `h_state`, `h_nsmstate`, and `h_rwsem`; it is not persistent across local reboot.

## Dependencies and Integration Points

The file integrates with `clntproc.c` for reclaim RPCs, `host.c` for host lookup/release/binding, `svc` callbacks for GRANTED RPCs, NFS file handles, SUNRPC address comparison, and `lockd_up`/`lockd_down` service reference management.

## Risks and Edge Cases

Callback matching intentionally does not use cookies, so mismatched ranges or pseudo-pids can lose grants. A server can request blocking even for non-blocking calls, which is rejected. Reclaimer `SIGKILL` can drop unreclaimed locks from future attempts. Polling is needed because some servers lose callbacks.

## Test Signals

Signals include blocking lock tests with GRANTED callbacks arriving before and after LOCK replies, interrupted waits and timeout polling, server reboot recovery with repeated NSM state changes, host shutdown while waits exist, and lockdep/KCSAN over `nlm_blocked_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/clntlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/clntproc.c -->
# sources/distributed-fs/ceph-client/fs/lockd/clntproc.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/clntproc.c` implements client-side NLM lock RPC procedure flow for TEST, LOCK, UNLOCK, CANCEL, async calls, lockowner private state, reclaim requests, and NLM status-to-errno translation. The source was read as a complete 889-line file.

## Important APIs, Types, and Functions

Key exports are `nlmclnt_proc`, `nlm_alloc_call`, `nlmclnt_release_call`, `nlm_async_call`, `nlm_async_reply`, `nlmclnt_reclaim`, and `nlmclnt_next_cookie`. Important internal helpers include `nlmclnt_find_lockowner`, `nlmclnt_setlockargs`, `nlmclnt_call`, `nlmclnt_async_call`, `nlmclnt_test`, `nlmclnt_lock`, `nlmclnt_unlock`, `nlmclnt_cancel`, and `nlm_stat_to_errno`.

## Control Flow

`nlmclnt_proc` allocates a request, initializes lockowner private state, fills NLM lock arguments from the VFS `file_lock`, dispatches by fcntl command, and releases private state. Synchronous calls bind a host RPC client, handle transport errors, rebind UDP peers, wait through server grace periods, and return only when the wire call is complete or interrupted. LOCK first asks the local VFS with `FL_ACCESS`, monitors the peer via NSM, queues a blocking wait, sends the LOCK RPC, waits/polls for GRANTED when blocked, cancels interrupted blocking locks, and installs the resulting local lock only after checking the host did not reboot. UNLOCK removes local VFS state first, then sends async UNLOCK with retry/grace handling.

## State and Persistence Behavior

Request state is refcounted in `struct nlm_rqst`. Lockowner state maps VFS `fl_owner_t` to a host-local 32-bit pseudo-pid and is attached to file locks through `fl_ops`; granted locks are listed on the host. `nlm_cookie` is an atomic in-memory cookie counter. Callback data is owned by optional `nlmclnt_operations` hooks.

## Dependencies and Integration Points

This file is the bridge between VFS file locking, NFS credentials/file handles, SUNRPC tasks, NSM monitoring from `mon.c`, host binding/rebind from `host.c`, blocked wait handling from `clntlock.c`, tracepoints, and version-specific XDR procedure tables.

## Risks and Edge Cases

The path must keep local VFS lock state synchronized with remote NLM state during errors. Grace-period handling, interrupted blocking calls, lost callbacks, and server reboots are all high-risk. Async request refcounts must be balanced with RPC release callbacks. Status translation differs for NLMv4 extended errors.

## Test Signals

Tests should cover GETLK/SETLK/SETLKW/UNLCK flows, local VFS denial before RPC, denied holder reporting, blocking lock cancellation, async unlock retry/rebind, server grace periods, reboot during lock acquisition, NLMv4 error mappings, and tracepoint coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/clntproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/clntxdr.c -->
# sources/distributed-fs/ceph-client/fs/lockd/clntxdr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/clntxdr.c` implements client-side SUNRPC XDR support for NLM versions 1 and 3 and publishes the lockd RPC program table. Version 2 is intentionally absent because it is not standardized. The source was read as a complete 614-line file.

## Important APIs, Types, and Functions

Important helpers mirror the v4 file: `nlm_compute_offsets`, `encode_cookie`, `decode_cookie`, `encode_nlm_lock`, `decode_nlm_holder`, `nlm_xdr_enc_testargs`, `nlm_xdr_enc_lockargs`, `nlm_xdr_enc_cancargs`, `nlm_xdr_enc_unlockargs`, `nlm_xdr_enc_res`, `nlm_xdr_enc_testres`, `nlm_xdr_dec_testres`, and `nlm_xdr_dec_res`. It defines version tables for versions 1 and 3 and exports `const struct rpc_program nlm_program`.

## Control Flow

Procedure entries in `nlm_procedures` route each NLM procedure to an encoder/decoder. Encoders write NFSv2-sized file handles, caller/owner netobjs, pseudo-pid, 32-bit offset and length, blocking/reclaim booleans, and state. Decoders validate cookies and status and decode a holder lock when TEST returns denied. `nlm_versions` selects v1, v3, and optionally v4.

## State and Persistence Behavior

The only owned state is static RPC procedure metadata and per-version/program statistics. Request, result, and lock data are caller-owned and transient.

## Dependencies and Integration Points

The file depends on `lockd.h`, `uapi/linux/nfs2.h`, SUNRPC XDR/client/stats APIs, and the v4 table when `CONFIG_LOCKD_V4` is enabled. `host.c` RPC client creation points at `nlm_program`, and `clntproc.c` uses the selected version's procedure array.

## Risks and Edge Cases

NLM v1/v3 use 32-bit offsets, so large ranges are clamped. Empty HPUX cookies are tolerated. Invalid status enums become XDR errors. File handles are encoded as fixed NFSv2 size, so callers must provide compatible handle data for these versions.

## Test Signals

Signals include NLM v1/v3 encode/decode round trips, NFSv2 file-handle size checks, 32-bit offset boundary tests, invalid enum/cookie fuzzing, and integration mounts that select NLM version 1 for NFSv2 and version 3/4 for later NFS clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/clntxdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/host.c -->
# sources/distributed-fs/ceph-client/fs/lockd/host.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/host.c` manages cached `nlm_host` objects shared by lockd client and server personalities. It handles host lookup, allocation, RPC client binding/rebinding, reference release, reboot notification fanout, per-net shutdown, and garbage collection. The source was read as a complete 723-line file.

## Important APIs, Types, and Functions

Important APIs are `nlmclnt_lookup_host`, `nlmclnt_release_host`, `nlmclnt_shutdown_rpc_clnt`, `nlmsvc_lookup_host`, `nlmsvc_release_host`, `nlm_bind_host`, `nlm_rebind_host`, `nlm_get_host`, `nlm_host_rebooted`, `nlm_shutdown_hosts_net`, and `nlm_shutdown_hosts`. Internal state includes client/server host hash tables, `nlm_host_mutex`, and the `nlm_lookup_host_info` construction record.

## Control Flow

Client lookup searches the client table by network namespace, peer address, protocol, and NLM version, sharing an existing NSM handle for the same address when possible; otherwise it allocates and inserts a new host. Server lookup adds source-address matching and runs GC periodically. `nlm_bind_host` lazily creates an SUNRPC client, configuring hard retry for client-side calls, soft behavior for server-side block callbacks, UDP autobind/rebind, optional nonprivileged source ports, and optional source address. Reboot notification maps NSM private data to handles, marks matching hosts with new NSM state, frees server resources, and starts client recovery.

## State and Persistence Behavior

Host state is in-memory, refcounted, and separated into client and server hash tables. Each host owns credentials, NSM handle reference, optional RPC client, lockowner/granted/reclaim lists, rebinding/expiry timestamps, and net namespace pointer. Server hosts are destroyed by mark-and-sweep GC after resources and references clear; client hosts are destroyed when their refcount reaches zero.

## Dependencies and Integration Points

This file integrates with `mon.c` for NSM handles, `clntlock.c` for recovery, server resource cleanup in `svcsubs.c`/related files, `clntxdr.c` via `nlm_program`, SUNRPC client creation, portmapper autobind, per-net `lockd_net`, and service request source/destination addresses.

## Risks and Edge Cases

Host identity must include net namespace, transport, version, and server source address where applicable. UDP rebind throttling must avoid stale portmapper data without excessive rebinding. Shutdown must cancel tasks before host destruction. GC must not destroy hosts with locks, blocks, shares, or live refs. NSM reuse by address can couple host lifetime unexpectedly if names differ.

## Test Signals

Tests should cover host cache hit/miss identity, per-net isolation, UDP rebind after connection errors, RPC client shutdown races, server-host GC with and without resources, NSM reboot notifications affecting multiple host entries, and lockdep around `nlm_host_mutex` plus host mutex nesting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/lockd.h -->
# sources/distributed-fs/ceph-client/fs/lockd/lockd.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/lockd.h` is the main private header for lockd. It defines debug masks, core host/request/file/block/share-facing structures, internal status constants, public cross-file prototypes, host monitor hooks, server/client integration points, and inline lock/address helpers. The source was read as a complete 452-line file.

## Important APIs, Types, and Functions

Core types include `struct nlm_host`, `struct nsm_handle`, `struct nlm_lockowner`, `struct nlm_wait`, `struct nlm_rqst`, `struct nlm_file`, and `struct nlm_block`. Important inlines include `nlm_addr`, `nlm_srcaddr`, `nlmsvc_file_file`, `nlmsvc_file_inode`, `nlmsvc_file_cannot_lock`, `nlm_privileged_requester`, `nlm_compare_locks`, and `lockd_set_file_lock_range4`. The header declares client, host, monitor, server lock, server file, share, and lock-manager entry points.

## Control Flow

The header does not execute flow directly, but it defines how modules communicate. Client code allocates `nlm_rqst`, binds `nlm_host`, and uses `nlm_wait` for GRANTED callbacks. Server code uses `nlm_file` and `nlm_block` to manage NFS-exported file locks. NSM monitor code maps `nsm_handle` into reboot handling. Inline privileged-request helpers enforce loopback plus privileged-port checks for sensitive operations.

## State and Persistence Behavior

All state is in memory and refcounted: hosts own RPC clients and lock lists, NSM handles own monitor identity, requests own wire argument/result buffers, files own open VFS files and share/block lists, and blocks own callback/deferred request state. Constants define wire and internal-only statuses.

## Dependencies and Integration Points

The header depends on exportfs, socket address types, VFS file locking, SUNRPC service/client headers, NLM XDR structures, and the public lockd bind API. It is included across nearly all lockd implementation files.

## Risks and Edge Cases

Changing structure layout or ownership semantics affects many files. `nlm_compare_locks` treats `F_UNLCK` in the second lock as a wildcard. `lockd_set_file_lock_range4` must handle length zero and arithmetic overflow as EOF. Privileged requester checks intentionally accept only local privileged ports.

## Test Signals

Signals include allmodconfig/build coverage, sparse type checks for network-byte-order statuses, lock range conversion boundary tests, privileged requester tests for IPv4/IPv6 loopback and mapped addresses, and integration tests that exercise client and server structure lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/lockd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/mon.c -->
# sources/distributed-fs/ceph-client/fs/lockd/mon.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/mon.c` implements the in-kernel client for the Network Status Monitor service (`rpc.statd`). It registers and unregisters monitored peers, caches NSM handles, matches reboot notifications, tracks local NSM state, and provides XDR for NSM MON/UNMON calls. The source was read as a complete 581-line file.

## Important APIs, Types, and Functions

Important public functions are `nsm_monitor`, `nsm_unmonitor`, `nsm_get_handle`, `nsm_reboot_lookup`, and `nsm_release`. Internal helpers include `nsm_create`, `nsm_mon_unmon`, `nsm_lookup_hostname`, `nsm_lookup_addr`, `nsm_lookup_priv`, `nsm_init_private`, `nsm_create_handle`, and NSM XDR encoders/decoders. Global state includes `nsm_local_state`, `nsm_use_hostnames`, and `nsm_lock`.

## Control Flow

`nsm_get_handle` validates hostnames, searches the per-net handle list by hostname or address depending on `nsm_use_hostnames`, and creates a handle with a unique private cookie if not found. `nsm_monitor` chooses the monitor name, creates a loopback TCP RPC client to `rpc.statd`, sends `NSMPROC_MON`, and updates `nsm_local_state` from the response. `nsm_unmonitor` sends `NSMPROC_UNMON` only when the final non-sticky reference is being released. Reboot lookup matches the private cookie returned by statd to an existing handle.

## State and Persistence Behavior

Handles are refcounted and stored on `lockd_net->nsm_handles`. Each handle stores monitor name, peer name/address, monitored/sticky flags, unique private cookie, and printable address buffer. The local NSM state is global in memory and changes when statd reports a different state.

## Dependencies and Integration Points

This file integrates with `host.c` host allocation/destruction and reboot notification, `netns.h` per-net storage, SUNRPC client transport to loopback statd, XDR stream helpers, and the NLM callback procedure number for `NLMPROC_NSM_NOTIFY`.

## Risks and Edge Cases

If statd is unavailable, monitoring fails and client lock acquisition can fail. Hostnames containing `/` are rejected to protect statd database paths. Private cookies use timestamp plus kernel pointer and are exposed only to local loopback statd, but stale or duplicated cookies could misattribute reboot state. `nsm_use_hostnames` changes cache matching semantics.

## Test Signals

Use statd integration tests for monitor/unmonitor, simulated reboot notifications, per-net handle isolation, hostname-vs-address matching, invalid hostname rejection, statd connection refused/rebind handling, refcount release tests, and XDR encode/decode fuzzing for NSM responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/mon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/netlink.c -->
# sources/distributed-fs/ceph-client/fs/lockd/netlink.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/netlink.c` is generated generic-netlink family registration data for lockd's administrative netlink interface. It describes commands, attribute policies, permissions, and the `genl_family`. The source was read as a complete 45-line generated file.

## Important APIs, Types, and Functions

The main objects are `lockd_server_set_nl_policy`, `lockd_nl_ops`, and `struct genl_family lockd_nl_family`. The command handlers are declared in `netlink.h` and implemented elsewhere as `lockd_nl_server_set_doit` and `lockd_nl_server_get_doit`.

## Control Flow

Generic netlink dispatch uses `lockd_nl_ops`: `LOCKD_CMD_SERVER_SET` accepts gracetime, TCP port, and UDP port attributes under `GENL_ADMIN_PERM`; `LOCKD_CMD_SERVER_GET` returns current server configuration. `parallel_ops` allows concurrent generic-netlink operations.

## State and Persistence Behavior

This file owns no mutable runtime configuration. The family is `__ro_after_init`; actual lockd per-net configuration is stored in `struct lockd_net` and manipulated by the command handlers.

## Dependencies and Integration Points

It depends on generated UAPI `linux/lockd_netlink.h`, generic netlink core, and declarations in `netlink.h`. It is built into lockd via the Makefile and registered by lockd init code outside this file.

## Risks and Edge Cases

Generated file drift from `Documentation/netlink/specs/lockd.yaml` is the main risk. Attribute policy bounds must match UAPI enum values. Because operations can run in parallel and are netns-aware, handlers must provide their own synchronization.

## Test Signals

Signals include ynl/netlink selftests for server set/get, permission tests for admin-only set, per-net namespace behavior, build regeneration diff checks, and malformed attribute fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/netlink.h -->
# sources/distributed-fs/ceph-client/fs/lockd/netlink.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/netlink.h` is the generated internal header for lockd's generic-netlink interface. It declares command handlers and the family object produced from the lockd netlink YAML specification. The source was read as a complete 20-line generated file.

## Important APIs, Types, and Functions

The header declares `lockd_nl_server_set_doit`, `lockd_nl_server_get_doit`, and `extern struct genl_family lockd_nl_family`.

## Control Flow

There is no executable flow in this header. It allows the generated family table in `netlink.c` and the hand-written command implementations to share prototypes.

## State and Persistence Behavior

No state is owned here. The family object is defined in `netlink.c`, and persistent configuration lives in `struct lockd_net`.

## Dependencies and Integration Points

The header includes generic netlink headers and UAPI `linux/lockd_netlink.h`, tying generated kernel dispatch to userspace-visible command and attribute definitions.

## Risks and Edge Cases

Manual edits will be lost on regeneration. Prototype drift between this generated header and command implementation will fail builds.

## Test Signals

Build coverage with lockd netlink enabled, regeneration checks from the YAML spec, and netlink command selftests that include this family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/netns.h -->
# sources/distributed-fs/ceph-client/fs/lockd/netns.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/netns.h` defines lockd's per-network-namespace state container. The source was read as a complete 25-line header.

## Important APIs, Types, and Functions

The central type is `struct lockd_net`, with fields for service user count, next host-GC time, host count, grace time, TCP/UDP ports, delayed grace-period work, `struct lock_manager`, and the NSM handle list. It declares `extern unsigned int lockd_net_id`.

## Control Flow

There is no direct control flow. Other lockd files retrieve this state with `net_generic(net, lockd_net_id)` to coordinate service lifetime, host cache accounting, grace-period control, netlink/procfs settings, and NSM handle storage.

## State and Persistence Behavior

All fields are per-net in-memory state. They persist for the lifetime of the network namespace and are cleaned up by lockd net namespace operations outside this header.

## Dependencies and Integration Points

It integrates with `host.c` for `nrhosts` and `next_gc`, `mon.c` for `nsm_handles`, procfs/netlink control paths for grace/ports, and lock-manager grace handling through `lockd_manager`.

## Risks and Edge Cases

Per-net isolation depends on every call site using the correct namespace. Grace-period delayed work and host/NSM lists must be drained before net namespace teardown.

## Test Signals

Signals include network namespace create/destroy tests with lockd active, independent netlink/procfs port and grace settings per netns, NSM handle cleanup, and host count leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/netns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/nlm.h -->
# sources/distributed-fs/ceph-client/fs/lockd/nlm.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/nlm.h` declares Network Lock Manager protocol constants: maximum offsets, status values, program number, and procedure numbers. The source was read as a complete 56-line header.

## Important APIs, Types, and Functions

Important constants include `NLM_OFFSET_MAX`, `NLM4_OFFSET_MAX`, `NLM_PROGRAM`, `NLMPROC_*` procedure IDs, and status enum values such as `NLM_LCK_GRANTED`, `NLM_LCK_DENIED`, `NLM_LCK_BLOCKED`, `NLM_LCK_DENIED_GRACE_PERIOD`, and NLMv4-only errors.

## Control Flow

There is no runtime flow. These constants drive XDR procedure tables, status translation, client/server dispatch, and reboot notification handling.

## State and Persistence Behavior

No state is owned. The values are ABI-level protocol constants and must remain stable.

## Dependencies and Integration Points

The header is included by `lockd.h` and therefore by most lockd implementation files. `clntxdr.c`, `clnt4xdr.c`, server XDR, and service dispatch tables rely on these numbers matching the NLM wire protocol.

## Risks and Edge Cases

Changing any value breaks wire compatibility. NLMv4-only statuses are conditionally compiled, so code translating statuses must handle builds without `CONFIG_LOCKD_V4`.

## Test Signals

Signals include protocol table build checks, XDR encode/decode tests that compare procedure numbers, NLMv4 status translation tests, and interoperability tests with standard NFS/NLM clients and servers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/nlm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/nlm4xdr_gen.c -->
# sources/distributed-fs/ceph-client/fs/lockd/nlm4xdr_gen.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/nlm4xdr_gen.c` is generated server-side XDR encode/decode support for NLMv4, produced by `xdrgen` from `Documentation/sunrpc/xdr/nlm4.x`. It decodes service request arguments and encodes service responses for NLMv4 server procedures. The source was read as a complete 724-line generated file.

## Important APIs, Types, and Functions

Public decode wrappers include `nlm4_svc_decode_void`, `nlm4_svc_decode_nlm4_testargs`, `nlm4_svc_decode_nlm4_lockargs`, `nlm4_svc_decode_nlm4_cancargs`, `nlm4_svc_decode_nlm4_unlockargs`, `nlm4_svc_decode_nlm4_testres`, `nlm4_svc_decode_nlm4_res`, `nlm4_svc_decode_nlm4_notifyargs`, `nlm4_svc_decode_nlm4_shareargs`, and `nlm4_svc_decode_nlm4_notify`. Public encoders include `nlm4_svc_encode_void`, `nlm4_svc_encode_nlm4_testres`, `nlm4_svc_encode_nlm4_res`, and `nlm4_svc_encode_nlm4_shareres`.

## Control Flow

Generated leaf decoders parse primitive XDR values, strings, opaque netobjs, stats, holders, locks, share arguments, notify arguments, and discriminated TEST replies. Service wrappers cast `rqstp->rq_argp` to the generated type and call the matching decoder. Encoders perform the reverse from `rqstp->rq_resp`, checking maximum string lengths before writing opaque data and encoding union arms only for statuses that require them.

## State and Persistence Behavior

No state is owned. Data is decoded into SUNRPC per-request argument buffers and encoded from response buffers. Procedure counters and dispatch tables are elsewhere.

## Dependencies and Integration Points

It depends on `nlm4xdr_gen.h`, generated type definitions in `include/linux/sunrpc/xdrgen/nlm4.h`, SUNRPC service request structures, and xdrgen builtin helpers. Server NLMv4 procedure tables consume these wrappers.

## Risks and Edge Cases

Manual edits will be overwritten. The generated code must stay synchronized with the `.x` protocol and generated header/type definitions. Decode functions return boolean failure without rich errno, so callers must map failures correctly. String/netobj length limits are protocol-critical.

## Test Signals

Signals include `make xdrgen` regeneration diff checks, server-side XDR round trips, malformed XDR fuzzing for each NLMv4 argument type, share/notify/test union coverage, and lockd NLMv4 server interoperability tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/nlm4xdr_gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/nlm4xdr_gen.h -->
# sources/distributed-fs/ceph-client/fs/lockd/nlm4xdr_gen.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/nlm4xdr_gen.h` is the generated declaration header for NLMv4 server-side XDR wrappers. The source was read as a complete 32-line generated file.

## Important APIs, Types, and Functions

It declares all public decode and encode wrappers implemented by `nlm4xdr_gen.c`, including void, lock/test/cancel/unlock/testres/res/notify/share decoders and void/testres/res/shareres encoders.

## Control Flow

There is no executable flow. Server dispatch code includes this header to bind procedure descriptors to generated XDR wrapper functions.

## State and Persistence Behavior

No state is owned. The header only exposes function prototypes and generated type dependencies.

## Dependencies and Integration Points

The header includes SUNRPC XDR APIs, xdrgen builtin definitions, and generated NLMv4 protocol type definitions. It must match `nlm4xdr_gen.c` and the `.x` source.

## Risks and Edge Cases

Generated declaration drift will break server builds or, worse, mismatch expected argument/response buffers. Manual edits will be lost.

## Test Signals

Build coverage for `CONFIG_LOCKD_V4`, regeneration diff checks, and server procedure table compilation against these prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/nlm4xdr_gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/procfs.c -->
# sources/distributed-fs/ceph-client/fs/lockd/procfs.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/procfs.c` implements lockd's optional procfs control file `/proc/fs/lockd/nlm_end_grace`. It lets privileged users inspect and force the end of a lockd grace period for the current network namespace. The source was read as a complete 92-line file.

## Important APIs, Types, and Functions

Important functions are `nlm_end_grace_write`, `nlm_end_grace_read`, `lockd_create_procfs`, and `lockd_remove_procfs`. `lockd_end_grace_proc_ops` wires read, write, llseek, and release operations.

## Control Flow

Reads get `struct lockd_net` from `current->nsproxy->net_ns`, report `Y\n` when the lock manager grace list is empty, and `N\n` otherwise. Writes use `simple_transaction_get` to accept one buffer per open and only strings starting with `Y`, `y`, or `1` call `locks_end_grace`; other input returns `-EINVAL`. Creation builds `/proc/fs/lockd` and then `nlm_end_grace`; removal deletes both entries.

## State and Persistence Behavior

The file owns no persistent lockd state. Transaction write buffers are per-open and released via `simple_transaction_release`. Grace state lives in `lockd_net->lockd_manager`.

## Dependencies and Integration Points

It depends on procfs, net namespace lookup, `netns.h`, libfs transaction and buffer helpers, and VFS lock manager grace APIs. It is compiled only with `CONFIG_PROC_FS`.

## Risks and Edge Cases

The proc directory is global while operations act on current net namespace, so tests must verify namespace expectations. `simple_transaction_get` permits only one write per open. Invalid or empty writes fail. Creation must unwind the directory if file creation fails.

## Test Signals

Signals include procfs creation/removal tests, read values before/during/after grace, write parsing for accepted and rejected prefixes, per-net namespace behavior, and transaction release leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/procfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/procfs.h -->
# sources/distributed-fs/ceph-client/fs/lockd/procfs.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/procfs.h` declares optional procfs setup and teardown for lockd, with no-op stubs when procfs is disabled. The source was read as a complete 27-line header.

## Important APIs, Types, and Functions

It exposes `lockd_create_procfs` and `lockd_remove_procfs`. When `CONFIG_PROC_FS` is disabled, inline stubs return success and do nothing.

## Control Flow

There is no direct runtime flow beyond the compile-time branch. Lockd init/exit can call these functions unconditionally.

## State and Persistence Behavior

No state is owned. Real proc entries are created in `procfs.c` only when procfs support is compiled in.

## Dependencies and Integration Points

The header is included by lockd init/exit code to hide `CONFIG_PROC_FS` conditionals from callers.

## Risks and Edge Cases

The no-op create stub returns 0, so callers must not assume proc entries exist in procfs-disabled builds. Prototype drift with `procfs.c` would fail builds.

## Test Signals

Build matrix coverage with `CONFIG_PROC_FS=y` and disabled, plus lockd init/exit smoke tests in both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/procfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/share.h -->
# sources/distributed-fs/ceph-client/fs/lockd/share.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/share.h` declares DOS share-mode support used by lockd's server personality. The source was read as a complete 33-line header.

## Important APIs, Types, and Functions

The key type is `struct nlm_share`, which links a share record to a host, file, owner handle, access mode, and deny mode. It defines `LOCKD_SHARE_SVID` as a synthetic owner ID and declares `nlmsvc_share_file`, `nlmsvc_unshare_file`, and `nlmsvc_traverse_shares`.

## Control Flow

There is no executable flow. Server share-management code uses this contract to add, remove, and traverse DOS share records associated with `struct nlm_file`.

## State and Persistence Behavior

Share records are in-memory server-side state hanging from `nlm_file->f_shares`; they persist only while lockd tracks the remote client's share.

## Dependencies and Integration Points

The header depends on `struct nlm_host`, `struct nlm_file`, `struct xdr_netobj`, and `nlm_host_match_fn_t` from lockd internals. It integrates with server resource traversal and cleanup on host reboot/shutdown.

## Risks and Edge Cases

Share owner comparison depends on opaque owner handles and the synthetic SVID used for lookup. Traversal callbacks must safely remove shares during host/resource cleanup.

## Test Signals

Signals include server-side SHARE/UNSHARE procedure tests, conflicting access/deny mode tests, owner-handle matching, host reboot cleanup, and share traversal under concurrent file resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/share.h -->
