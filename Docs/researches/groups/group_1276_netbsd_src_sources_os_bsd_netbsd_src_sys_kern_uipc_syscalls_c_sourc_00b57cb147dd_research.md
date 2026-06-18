# Group Research: group_1276_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_uipc_syscalls_c_sourc_00b57cb147dd

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_syscalls.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_syscalls.c

## Purpose
Implements the NetBSD syscall-facing socket API: socket creation, bind/listen/accept/connect, socketpair, send/receive message paths, socket option access, shutdown, socket name queries, pipe-as-socketpair support, and SCTP peeloff glue.

## Main Interfaces
- `sys___socket30`: creates a socket-backed file descriptor with `fsocreate` and affixes it to the process descriptor table.
- `sys_bind`, `do_sys_bind`, `sys_listen`, `sys_connect`, `do_sys_connect`: marshal user socket addresses and dispatch to socket/protocol operations.
- `do_sys_accept`, `sys_accept`, `sys_paccept`: allocate a result descriptor, dequeue a pending connection, apply nonblock/nosigpipe/close flags, and optionally install a temporary signal mask.
- `sys_socketpair`: creates and connects two sockets, including symmetric datagram connection handling.
- `sys_sendto`, `sys_sendmsg`, `do_sys_sendmsg`, `do_sys_sendmsg_so`, `sys_sendmmsg`: convert user message/iovec/control state into `uio` and mbufs, validate sizes, and call `so_send`.
- `sys_recvfrom`, `sys_recvmsg`, `do_sys_recvmsg`, `do_sys_recvmsg_so`, `sys_recvmmsg`: receive data/control/name mbufs, handle batching, partial transfer semantics, and user copyout.
- `copyout_msg_control`, `free_control_mbuf`, `free_rights`: externalize and clean up control mbufs, especially truncated or failed `SCM_RIGHTS` delivery.
- `sys_setsockopt`, `sys_getsockopt`, `sys_getsockopt2`: marshal socket options and synchronize `SO_NOSIGPIPE` with file flags.
- `pipe1` under `PIPE_SOCKETPAIR`: implements pipes as connected AF_LOCAL stream sockets with unidirectional descriptors and pipe watermarks.
- `do_sys_getsockname`, `do_sys_getpeername`, `copyout_sockname*`, `sockargs*`: socket name and control argument conversion helpers.
- `do_sys_peeloff`: optional SCTP association peeloff into a new socket descriptor.

## State And Control Flow
The file bridges user ABI structures to kernel socket operations. It obtains descriptor references with `fd_getsock`/`fd_getsock1`, allocates new descriptors with `fd_allocfile`, and uses `fd_affix`, `fd_abort`, `closef`, and `soclose` to keep descriptor and socket lifetimes balanced. Send and receive paths build `uio` structures, enforce `IOV_MAX`, `SSIZE_MAX`, socket-address length, and control-data length limits, then call protocol send/receive callbacks. Accept and connect paths hold socket locks through queue/state transitions, with explicit handling for nonblocking connect, interrupted connect, `ERESTART` conversion, and paccept signal-mask teardown.

## Dependencies And Integration
Depends on the socket core (`struct socket`, `soaccept`, `soconnect`, `soconnect2`, `soshutdown`, `so_send`, `so_receive`), file descriptor management, mbufs, ktrace, signal delivery, kqueue/select wakeups via socket buffers, kauth credentials, optional SCTP code, and AF_LOCAL helpers for pipe socketpairs.

## Risks And Edge Cases
- Descriptor lifetime is delicate in accept, socketpair, pipe, and peeloff paths; failures must abort or close exactly the resources already allocated.
- Partial send/receive deliberately suppresses `EINTR`, `ERESTART`, and `EWOULDBLOCK` after bytes are transferred.
- `copyout_msg_control` must close externalized descriptors if control copyout truncates or fails.
- `sockargs` and `sockargs_sb` enforce address/control limits and preserve 4.3BSD address-family compatibility behavior.
- `recvmmsg` defers a post-success error in `so->so_rerror` so a later receive can surface it.
- `getsockopt2` differs by copying input option data before `sogetopt`; callers must choose the intended ABI.

## Filesystem Relevance
Indirect but important. This is descriptor/syscall substrate rather than VFS code, but Unix-domain sockets, pipes, `SCM_RIGHTS`, and descriptor lifecycle interact with filesystem objects and vnode-backed descriptors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_usrreq.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_usrreq.c

## Purpose
Implements NetBSD AF_LOCAL/Unix-domain socket protocol operations, including pathname-bound socket nodes, stream/datagram connection management, local credential passing, `SCM_RIGHTS` file-descriptor passing, and garbage collection of file references in transit.

## Main Interfaces
- `uipc_init`: initializes sysctl nodes, the global local-domain lock, and the Unix-domain garbage-collection thread.
- `unp_attach`, `unp_detach`: allocate/free `unpcb`, reserve socket buffers, manage socket locks, and unlink bound vnodes.
- `unp_bind`: creates a filesystem `VSOCK` node through `namei` and `VOP_CREATE`, stores `v_socket`, and records the socket path.
- `unp_listen`, `unp_accept`, `unp_connect`, `unp_connect2`, `unp_disconnect`, `unp_shutdown`, `unp_abort`: implement local socket connection lifecycle.
- `unp_send`, `unp_output`, `unp_rcvd`: deliver data/control mbufs and maintain stream receive-buffer backpressure accounting.
- `uipc_ctloutput`: handles `LOCAL_CREDS`, `LOCAL_OCREDS`, `LOCAL_CONNWAIT`, and `LOCAL_PEEREID`.
- `unp_externalize`, `unp_internalize`: convert between user file descriptors and in-kernel `file_t *` arrays for `SCM_RIGHTS`.
- `unp_addsockcred`: appends credential control messages.
- `unp_gc`, `unp_thread`, `unp_scan`, `unp_dispose`, `unp_mark`: mark/sweep garbage collector for file references stored inside socket buffers.
- `unp_usrreqs`: exports AF_LOCAL protocol callbacks to the generic socket layer.

## State And Control Flow
Each socket has an `unpcb` tracking peer/reference links, bound vnode/path, cached peer credentials, optional stream lock, and receive-buffer accounting. Datagram sockets use the domain-wide `uipc_lock`. Stream sockets start with private locks, move to `uipc_lock` while listening/connecting to named endpoints, then connected pairs share a private stream lock once fully established. Pathname bind and connect drop the socket lock around namei/VOP operations and mark `UNP_BUSY` to reject overlapping operations. `SCM_RIGHTS` internalization increments `unp_rights`, file reference counts, and per-file message counts; externalization allocates recipient descriptors, affixes them, and drops in-flight references.

## Dependencies And Integration
Integrates socket buffers and protocol dispatch, vnode/namei/VOP_CREATE/VOP_ACCESS, `v_socket` backpointers, file descriptor tables, process cwd/chroot state, kauth credentials, sysctl, module compatibility hooks for old credentials, the global file list, and `vn_isunder` for chroot visibility checks.

## Risks And Edge Cases
- Lock transitions between private stream locks and `uipc_lock` are race-sensitive and heavily constrained by comments and assertions.
- `unp_bind` and `unp_connect` use `UNP_BUSY` because pathname operations require dropping the socket lock.
- Passing directory descriptors across chroot boundaries is checked in `unp_externalize` with `vn_isunder`.
- `SCM_RIGHTS` is limited by `maxfiles / unp_rights_ratio` and rejects kqueue descriptors.
- Cycles of sockets containing descriptors require the GC thread; correctness depends on `f_count`, `f_msgcount`, `f_unpcount`, `FMARK`, `FDEFER`, and `FSCAN` accounting.
- Bound socket vnode teardown clears `vp->v_socket` and releases the vnode; races with connect are guarded with `v_interlock` but comments still call out fragility.

## Filesystem Relevance
High for VFS/socket interaction. AF_LOCAL bind/connect uses real filesystem path lookup and `VSOCK` vnodes, while descriptor passing can transport vnode-backed files and must respect chroot visibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/uipc_usrreq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_acl.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_acl.c

## Purpose
Implements ACL syscall glue and vnode wrappers for getting, setting, deleting, and validating filesystem ACLs, including compatibility conversion between old POSIX.1e ACL layout and newer ACL structures.

## Main Interfaces
- `acl_copy_oldacl_into_acl`, `acl_copy_acl_into_oldacl`: convert old and current ACL layouts.
- `acl_copyin`, `acl_copyout`, `acl_type_unold`: select compatibility layout based on ACL type and normalize old type constants.
- `vacl_set_acl`, `vacl_get_acl`, `vacl_delete`, `vacl_aclcheck`: prepare kernel ACL buffers and call `VOP_SETACL`, `VOP_GETACL`, or `VOP_ACLCHECK`.
- Path syscalls: `sys___acl_get_file`, `sys___acl_get_link`, `sys___acl_set_file`, `sys___acl_set_link`, `sys___acl_delete_file`, `sys___acl_delete_link`, `sys___acl_aclcheck_file`, `sys___acl_aclcheck_link`.
- FD syscalls: `sys___acl_get_fd`, `sys___acl_set_fd`, `sys___acl_delete_fd`, `sys___acl_aclcheck_fd`.
- Kernel path helpers: `kern___acl_get_path`, `kern___acl_set_path`, `kern___acl_delete_path`, `kern___acl_aclcheck_path`.
- `acl_alloc`, `acl_free`: allocate and free initialized ACL buffers.

## State And Control Flow
Syscalls resolve either a user path with follow/no-follow semantics or a file descriptor to a vnode, then call common `vacl_*` helpers. ACL payloads are copied into temporary kernel buffers before VOP calls and copied back after successful gets. Old ACL access/default types are translated to modern types before invoking filesystem vnode operations.

## Dependencies And Integration
Uses `namei_simple_user`, descriptor-to-vnode lookup, vnode locks, filesystem ACL vnode operations, `copyin`/`copyout`, `ufetch_32`, caller credentials, and NetBSD ACL allocation helpers.

## Risks And Edge Cases
- Compatibility depends on ACL type values: old access/default types use `struct oldacl`, while other types require `acl_maxcnt == ACL_MAX_ENTRIES`.
- Path variants differ only in symlink-following policy, so syscall selection matters.
- Filesystem-specific ACL validation and persistence are delegated to VOPs; this file only handles marshalling and locking.
- `vacl_aclcheck` intentionally performs no vnode lock, matching the inherited comment that vnode state auditing is limited there.
- `acl_alloc` can return `NULL` if called with non-sleeping flags; current syscall paths use `KM_SLEEP`.

## Filesystem Relevance
High. This is the VFS-facing ACL syscall layer for filesystem permission metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_bio.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_bio.c

## Purpose
Implements NetBSD's buffer cache: block buffer lookup, allocation, free-list management, synchronous/asynchronous block I/O, delayed writes, memory pressure trimming, I/O completion, nested I/O buffers, and buffer-cache sysctls.

## Main Interfaces
- Initialization: `biohist_init`, `buf_setvalimit`, `bufinit`, `bufinit2`.
- Buffer lookup/allocation: `incore`, `getblk`, `geteblk`, `allocbuf`, `getnewbuf`.
- Reads/writes: `bread`, `breadn`, `bwrite`, `vn_bwrite`, `bdwrite`, `bawrite`.
- Release/reclaim: `brelse`, `brelsel`, `bremfree`, `binvalbuf`, `buf_drain`, `buf_trim`.
- Completion: `biowait`, `biodone`, `biodone2`, `biointr`.
- Memory helpers: `buf_memcalc`, `buf_lotsfree`, `buf_canrelease`, `buf_alloc`, `buf_mrelease`.
- Sysctl/debug: `sysctl_dobuf`, `sysctl_bufvm_update`, `bufhash_stats`, optional `vfs_bufstats`.
- I/O-only buffers: `getiobuf`, `putiobuf`, `nestiobuf_setup`, `nestiobuf_iodone`, `nestiobuf_done`.
- Object lifecycle/locking: `buf_init`, `buf_destroy`, `bbusy`, `buf_nbuf`.

## State And Control Flow
Buffers are indexed by vnode/logical block in `bufhashtbl` under `bufcache_lock`. Free buffers live on `BQ_LOCKED`, `BQ_LRU`, or `BQ_AGE` queues with per-queue byte totals. `BC_BUSY` is the long-term per-buffer lock, while `b_objlock` protects I/O completion state and points to either the vnode interlock or global `buffer_lock`. `getblk` finds or creates a busy buffer, associates it with a vnode, and resizes memory. Reads call `VOP_STRATEGY` when data is not already valid; writes handle delayed-write state, WAPBL interactions, mount statistics, sync/async completion, and copy-on-write modification hooks.

## Dependencies And Integration
Tightly integrates VFS vnodes, block-device mounts, WAPBL journaling hooks, filesystem COW hooks (`fscow_run`), UVM kernel memory allocation, pool caches, soft interrupts, sysctl, DTrace SDT probes, fstrans, and per-mount I/O accounting.

## Risks And Edge Cases
- Lock order is explicitly `bufcache_lock -> b_objlock`; violating it risks deadlock.
- `getnewbuf` may start delayed writes and return `NULL`, forcing callers to retry.
- The pagedaemon gets special behavior to avoid deadlock when buffers are busy or memory cannot be allocated.
- `allocbuf` changes buffer size and global `bufmem`, then may trigger reclaim under memory pressure.
- I/O completion from interrupt context is deferred to a soft interrupt; callbacks, async release, and waiters take different paths.
- WAPBL-tracked buffers require resize/add/remove handling to preserve transaction accounting.
- `bbusy` may return `EPASSTHROUGH`, meaning the caller must rediscover the buffer because its identity may have changed.

## Filesystem Relevance
Very high. This is core block-buffer infrastructure used by local filesystems for metadata and data block I/O.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_cache.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_cache.c

## Purpose
Implements NetBSD's vnode name cache: per-directory name lookup, reverse lookup for `getcwd` and path reconstruction, negative entries, mountpoint entries, LRU replacement, cache invalidation, identity caching for fast access checks, and namecache statistics.

## Main Interfaces
- Lookup: `cache_lookup`, `cache_lookup_raw`, `cache_lookup_linked`, `cache_lookup_entry`.
- Reverse lookup: `cache_revlookup`.
- Insert/update: `cache_enter`, `cache_enter_id`, `cache_have_id`, `cache_enter_mount`, `cache_lookup_mount`, `cache_cross_mount`.
- Initialization: `nchinit`, `cache_cpu_init`, `cache_vnode_init`, `cache_vnode_fini`.
- Purge/invalidation: `cache_purge1`, `cache_purgevfs`, `cache_purge_parents`, `cache_purge_children`, `cache_purge_name`, `cache_remove`.
- Replacement: `cache_activate`, `cache_deactivate`, `cache_reclaim`.
- Statistics: `namecache_count_pass2`, `namecache_count_2passes`, `cache_update_stats`, `cache_stat_sysctl`.
- Debug: optional `namecache_print`.

## State And Control Flow
Each directory vnode owns an RB tree keyed by name hash and length for forward lookup. Each target vnode owns a parent/name list for reverse lookup. Entries also live on global active/inactive LRU lists. Forward lookup holds the parent `vi_nc_lock`; reverse lookup holds child `vi_nc_listlock`; LRU reclaim uses `cache_lru_lock`. Positive entries point to a vnode, negative entries have `nc_vp == NULL`, and mountpoint entries use an empty synthetic name. New entries go to the active list, age into inactive, and are reclaimed approximately when the cache exceeds `desiredvnodes`.

## Dependencies And Integration
Uses vnode implementation-private locks/lists, RB trees, pool cache allocation, kauth/genfs access checks, mount flags such as `IMNT_NCLOOKUP`, DTrace probes, per-CPU counters, callouts, sysctl, and vnode lifecycle hooks.

## Risks And Edge Cases
- The lock order is central: directory tree lock, vnode reverse-list lock, then LRU lock.
- Reverse purge handles child-to-parent lock inversion with try-locks, vnode holds, waits, and retry pauses.
- `cache_lookup_linked` keeps namecache locks chained across path components and only works for filesystems publishing identity data.
- Negative entries are purged when creating the last path component.
- Reclaim is approximate by design and may temporarily exceed target size.
- `cache_revlookup` is not authoritative; on miss callers must fall back to directory scanning.
- Long names beyond `cache_maxlen` are deliberately not cached.

## Filesystem Relevance
Very high. This is the VFS path lookup acceleration layer used by namei, getcwd, mount crossing, vnode lifecycle, and filesystem lookup accounting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_cwd.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_cwd.c

## Purpose
Manages `struct cwdinfo`, the per-process or shareable current-directory state containing current directory, root directory, emulation root, umask, lock, and reference count.

## Main Interfaces
- `cwdinit`: allocate a new cwdinfo by copying the current process cwd/root/emulation-root vnodes and taking references.
- `cwdshare`: make another process share the current process cwdinfo.
- `cwdunshare`: ensure a process has a private cwdinfo when the refcount is greater than one.
- `cwdfree`: drop a cwdinfo reference and release vnode references when the count reaches zero.
- `cwdexec`: unshare on exec and release the emulation-root vnode reference if present.

## State And Control Flow
`cwdinfo` is reference counted with atomic operations. Directory vnode pointers are protected by `cwdi_lock` during copying and are held with `vref` and released with `vrele`. `cwdunshare` copy-on-writes shared cwdinfo so updates after fork/exec do not affect other processes.

## Dependencies And Integration
Uses process `p_cwdi`, vnode references, rw locks, atomic refcounts, memory barriers, and kernel memory allocation.

## Risks And Edge Cases
- Correctness depends on surrounding process/cwd synchronization when changing `p_cwdi`.
- `cwdfree` uses release/acquire barriers around the final reference drop.
- `cwdexec` releases `cwdi_edir` if present but this file does not clear the pointer; surrounding exec code must account for that state.
- `cwdshare` shares `curproc->p_cwdi`, not an arbitrary source process, so callers must use it in the intended fork/share context.

## Filesystem Relevance
High. This is the per-process root/current-directory state used by path lookup, chroot behavior, and descriptor passing visibility checks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_cwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_dirhash.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_dirhash.c

## Purpose
Provides a generic directory-entry hash cache for filesystems: maps directory names to offsets/sizes, tracks freed directory slots, limits global memory use, and exposes dirhash sysctls.

## Main Interfaces
- `dirhash_init`: initializes pools, LRU queue, memory limits, mutex, and sysctl nodes.
- `dirhash_get`, `dirhash_put`: allocate/reference and release a directory hash object.
- `dirhash_purge_entries`, `dirhash_purge`: free entries and recycle whole dirhash objects.
- `dirhash_enter`: add a live directory entry keyed by name hash and offset.
- `dirhash_enter_freed`: record free directory space.
- `dirhash_remove`: remove a live entry and convert its slot to free space.
- `dirhash_lookup`: iterate matching live name-hash entries.
- `dirhash_lookup_freed`: iterate free entries large enough for a requested size.
- `dirhash_dir_isempty`: report directory emptiness from completed hash state.

## State And Control Flow
Each `struct dirhash` owns hash buckets for live entries and a free-entry list. The global `dirhash_queue` is protected by `dirhashmutex` and used for LRU-style purging under `maxdirhashsize`. Entry allocation uses pools. `dirhash_enter` removes matching free-space records, may purge unreferenced old dirhashes when global memory would exceed the limit, then inserts a new live entry. Callers are expected to hold the filesystem/vnode-specific lock protecting the dirhash itself.

## Dependencies And Integration
Uses kernel pools, sysctl, vnode-facing dirhash structures, `hash32_strn`, global physical-memory sizing, and filesystem-provided directory entry metadata.

## Risks And Edge Cases
- `dirhashsize` is global and updated by entry operations; callers must observe the documented locking model.
- Lookup returns internal entry pointers that must not be used after dropping the protecting node lock.
- `dirhash_remove` panics if the expected entry is absent, so filesystem update ordering must keep dirhash state synchronized.
- Global memory limiting is best-effort: if purging cannot free enough, insertion can still proceed.
- `dirhash_dir_isempty` relies on `DIRH_COMPLETE` and treats directories with only `..` or no entries as empty.
- `dirhash_enter` ignores duplicate entries once a hash is complete unless explicitly adding a new entry.

## Filesystem Relevance
High. This is reusable local-filesystem directory lookup/update acceleration infrastructure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_dirhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_getcwd.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_getcwd.c

## Purpose
Implements current-directory path reconstruction and ancestry checks by walking from a vnode up toward a root, using the name cache when possible and directory scanning as fallback.

## Main Interfaces
- `getcwd_scandir`: find a vnode's parent and optional name by looking up `..` and scanning the parent directory.
- `getcwd_common`: shared upward traversal used by `getcwd`, ancestry checks, and vnode path reconstruction.
- `vn_isunder`: tests whether one directory lies under another root.
- `proc_isunder`: tests whether one process root is equal to or under another process root.
- `sys___getcwd`: syscall implementation that builds a path backward into a kernel buffer and copies it out.
- `vnode_to_path`: best-effort path reconstruction for an arbitrary referenced vnode using reverse namecache plus `getcwd_common`.

## State And Control Flow
Paths are built backward from the end of a buffer. `getcwd_common` references both starting vnode and root, handles crossing covered mount roots, optionally checks access, tries `cache_revlookup`, and falls back to `getcwd_scandir` on cache miss. Directory scanning locks the lower vnode, looks up `..`, locks the parent, reads directory blocks with `VOP_READDIR`, and matches entries by file id. `sys___getcwd` bounds user length, allocates a temporary buffer, and limits traversal to roughly half the output length.

## Dependencies And Integration
Uses cwdinfo, vnode references/locks, `VOP_LOOKUP`, `VOP_GETATTR`, `VOP_ACCESS`, `VOP_READDIR`, namecache reverse lookup, mount topology, credentials, directory entry format, UIO setup, and emulation path stripping.

## Risks And Edge Cases
- Path reconstruction is inherently race-prone because vnode-to-parent mappings are not authoritative.
- Directory scanning matches by file id and does not verify by lookup that the found name resolves back to the child.
- Malformed directory records return `EINVAL`; comments note possible infinite retry behavior for pathological directory/NFS cases.
- Union mount fallback code is disabled.
- Buffer exhaustion returns `ERANGE`, and traversal is bounded by a vnode-count limit derived from output length.
- `vnode_to_path` depends on namecache success for the first reverse step and returns `ENOENT` when unavailable.

## Filesystem Relevance
High. This is VFS reverse-path logic used for `getcwd`, chroot/ancestry checks, procfs-style visibility, and best-effort vnode path reporting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_getcwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_hooks.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_hooks.c

## Purpose
Implements a small VFS hook registration and dispatch facility for mount-related lifecycle events.

## Main Interfaces
- `vfs_hooks_init`: initializes the global hook-list mutex.
- `vfs_hooks_attach`: inserts a `struct vfs_hooks` into the global list.
- `vfs_hooks_detach`: removes a registered hooks object or returns `ESRCH`.
- `vfs_hooks_unmount`: dispatches non-error unmount hooks to all registered providers.
- `vfs_hooks_reexport`: dispatches reexport hooks and stops at the first nonzero error.

## State And Control Flow
A global `LIST_HEAD` stores hook providers and is protected by `vfs_hooks_lock`. Two macros generate dispatch functions: one for hooks that return errors and short-circuit, and one for hooks that run all callbacks unconditionally.

## Dependencies And Integration
Uses `struct mount`, mutexes, BSD queue macros, errno values, and VFS hook structures declared elsewhere.

## Risks And Edge Cases
- Hooks are invoked while holding `vfs_hooks_lock`, so callbacks must avoid reentrant operations that would deadlock or block excessively.
- Detach is pointer-based and returns `ESRCH` if the exact hook object is not present.
- Error-dispatch initializes to `EJUSTRETURN`, so callers must distinguish "no hook handled it" from success.
- Hook ordering is list insertion order, with newest attachments at the head.

## Filesystem Relevance
Moderate. This is generic VFS extension plumbing around unmount/reexport behavior, not a filesystem implementation itself.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_hooks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_init.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_init.c

## Purpose
Bootstraps the NetBSD VFS layer: sysctl setup, vnode table/namecache initialization, vnode operation vector construction, generic dirhash/hooks initialization, mount authorization listener setup, VFS module initialization, and filesystem attach/detach/reinit support.

## Main Interfaces
- `vn_default_error`: generic default vnode operation returning `EOPNOTSUPP`.
- `sysctl_vfs_setup`: creates generic VFS sysctls.
- `vfs_opv_init`, `vfs_opv_free`: allocate/fill/free vnode operation vectors.
- `vfs_opv_init_explicit`, `vfs_opv_init_default`: install explicit vnode ops and default missing slots.
- Debug `vfs_op_check`: validates vnode operation descriptor offsets/count.
- `usermount_common_policy`: shared policy for unprivileged mounts.
- `mount_listener_cb`: kauth listener for mount permissions and device access.
- `vfsinit`: top-level VFS initialization path.
- `vfs_delref`, `vfs_attach`, `vfs_detach`, `vfs_reinit`: manage filesystem type registration and lifecycle.

## State And Control Flow
`vfsinit` creates generic sysctls, initializes the vnode table and namecache, validates operation descriptors in debug builds, initializes special dead/fifo/spec vnode operations, starts dirhash and VFS hook support, registers a kauth mount listener, initializes statically included VFS modules, and sets up filesystem kqueue filtering. `vfs_attach` checks for duplicate filesystem names or `makefstype` collisions, initializes vnode ops, calls the filesystem init routine, and links the `vfsops` into `vfs_list`. `vfs_detach` refuses busy filesystems, removes the entry, calls cleanup, and frees vnode op vectors. `vfs_reinit` temporarily increments each filesystem refcount while invoking its callback outside the global list lock.

## Dependencies And Integration
Uses vnode operation descriptors, special vnode operation tables, sysctl, kauth, module initialization, VFS list locking, dirhash, namecache, VFS hooks, deadfs/fifofs/specfs, filesystem-provided `vfsops`, and mount/device access VOPs.

## Risks And Edge Cases
- Vnode operation descriptor mistakes panic during initialization if an operation offset is missing or inconsistent.
- Filesystem type collisions are checked both by name and by `makefstype` numeric value.
- `vfs_detach` depends on accurate `vfs_refcount`; busy filesystems cannot be detached.
- Unprivileged mount policy requires `nodev` and `nosuid`, preserves existing `noexec`, and rejects exported mounts.
- `vfs_attach` calls filesystem init while holding `vfs_list_lock`, so init routines must fit that context.
- `vfs_reinit` drops and reacquires the list lock around callbacks, so the refcount bump is what protects the target filesystem.

## Filesystem Relevance
Very high. This is core VFS registration and initialization infrastructure for all NetBSD filesystem modules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_init.c -->