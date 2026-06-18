# Group Research: group_971_linux_stable_sources_os_linux_linux_stable_fs_dcache_c_sources_os_li_c4ddee09d2b9

Scope: `Docs/research_subset_a.md` only. This grouped report covers the listed Linux stable VFS, debugfs, devpts, direct I/O, and DLM configuration/callback files.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dcache.c -->
# File Research: sources/os/linux/linux-stable/fs/dcache.c

## Purpose

`dcache.c` implements the Linux VFS dentry cache: dentry allocation, lookup, hashing, aliasing, pruning, RCU path-walk support, rename/move mechanics, dentry lifetime management, and early VFS cache initialization.

## Main Responsibilities

- Maintains the global dentry hash table and in-progress parallel lookup hash table.
- Implements dentry reference release and final destruction through `dput()`, `__dentry_kill()`, and RCU-delayed freeing.
- Tracks unused and negative dentry counts with per-CPU counters and exposes dcache sysctls.
- Provides exported VFS helpers for dentry allocation, lookup, instantiation, deletion, invalidation, rename, alias splicing, and tmpfile naming.
- Manages dentry LRU and shrink-list transitions for reclaim and unmount.
- Supports lockless RCU path lookup through `__d_lookup_rcu()` and dentry sequence counts.
- Handles parallel lookup serialization through `d_alloc_parallel()`, `d_lookup_done()`-style unhash/wake helpers, and per-directory sequence updates.
- Initializes dcache slab and hash structures in `vfs_caches_init_early()` and `vfs_caches_init()`.

## Core Data and State

- `rename_lock`: global seqlock protecting rename-sensitive tree walks and lookup retry logic.
- `dentry_hashtable`: primary hash table keyed by parent/name hash.
- `in_lookup_hashtable`: temporary hash table for dentries under parallel lookup.
- Per-CPU counters: `nr_dentry`, `nr_dentry_unused`, and `nr_dentry_negative`.
- `struct external_name`: refcounted, RCU-freed storage for long names.
- Dentry flags such as `DCACHE_LRU_LIST`, `DCACHE_SHRINK_LIST`, `DCACHE_PAR_LOOKUP`, `DCACHE_DENTRY_KILLED`, `DCACHE_DISCONNECTED`, `DCACHE_DONTCACHE`, and type flags derived from inode mode.

## Key Control Flow

Lookup:
- `d_hash_and_lookup()` hashes a name, applies filesystem `d_hash`, then calls `d_lookup()`.
- `d_lookup()` wraps `__d_lookup()` with `rename_lock` retry protection.
- `__d_lookup_rcu()` performs store-free RCU lookup for path walking and returns a dentry plus sequence value that callers must validate.
- `d_same_name()` uses direct name comparison or filesystem `d_compare`.

Parallel lookup:
- `d_alloc_parallel()` first checks the normal hash under RCU, then checks the in-lookup hash, waits on an existing matching lookup if needed, or inserts a new `DCACHE_PAR_LOOKUP` dentry.
- `__d_add()` removes an in-lookup dentry from the temporary hash, wakes waiters, optionally instantiates an inode, and rehashes the dentry into the normal cache.

Lifetime and reclaim:
- `dput()` uses `fast_dput()` for the common lockref decrement path.
- When the last ref cannot be retained, `finish_dput()` and `__dentry_kill()` detach the dentry from hashes, aliases, parent children, LRU state, and inode.
- `shrink_dentry_list()`, `prune_dcache_sb()`, `shrink_dcache_sb()`, and `shrink_dcache_parent()` move unused dentries to local lists and destroy them.
- `shrink_dcache_for_umount()` tears down superblock root dentries and checks for still-busy dentries.

Rename and aliasing:
- `__d_move()` updates parents, names, child lists, hashes, fsnotify state, and fscrypt rename state under `rename_lock` and ordered dentry locks.
- `d_splice_alias_ops()` handles exportable filesystem lookup results, including disconnected directory aliases and loop prevention.
- `d_obtain_alias()` and `d_obtain_root()` create disconnected or root aliases from inodes.

## Important Dependencies

- VFS inode and mount internals from `internal.h` and `mount.h`.
- `list_lru` shrinker infrastructure.
- `lockref`, seqcount, RCU, hlist-bl locking, and superblock LRU state.
- Security hooks through `security_d_instantiate()`.
- fsnotify hooks for create, move, remove, and inode removal.
- fscrypt rename notification via `fscrypt_handle_d_move()`.

## Edge Cases and Risks

- Lock ordering is central: inode `i_lock`, dentry `d_lock`, superblock LRU lock, hash-bucket lock, and ancestor dentry locks must stay ordered as documented.
- RCU lookup intentionally tolerates false negatives but requires sequence validation before using returned dentry state.
- Negative dentry accounting only applies when a dentry is on the real LRU, not when on a shrink list.
- External dentry names are refcounted and RCU-freed; snapshots must release references exactly once.
- Directory aliases are constrained; `d_splice_alias_ops()` rejects alias moves that would create dcache loops.
- Parallel lookup depends on directory sequence updates and waitqueue wakeups to avoid duplicate lookup instantiation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/debugfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/debugfs/Makefile

## Purpose

Builds the debugfs filesystem object when `CONFIG_DEBUG_FS` is enabled.

## Main Responsibilities

- Defines `debugfs-objs` as `inode.o file.o`.
- Adds `debugfs.o` to the build through `obj-$(CONFIG_DEBUG_FS)`.

## Dependencies

- Controlled entirely by the kernel `CONFIG_DEBUG_FS` option.
- Combines debugfs inode/mount logic from `inode.c` with file helper/proxy logic from `file.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/debugfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/debugfs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/debugfs/file.c

## Purpose

`file.c` implements debugfs file-operation safety wrappers and convenience file creators for common scalar, boolean, string, blob, array, register-set, and device-managed seqfile debug files.

## Main Responsibilities

- Provides noop file operations used when a debugfs file has no real operations.
- Exposes `debugfs_get_aux()` for retrieving auxiliary data stored in the debugfs inode.
- Implements active-user lifetime tracking with `debugfs_file_get()` and `debugfs_file_put()`.
- Provides cancellation registration for long-running debugfs handlers during removal.
- Enforces kernel lockdown restrictions for debugfs access.
- Defines open-only and full proxy file operations that safely call real debugfs handlers.
- Provides typed helper creators: `debugfs_create_u8/u16/u32/u64/ulong`, hex variants, `size_t`, `atomic_t`, bool, string, blob, u32 array, regset32, and device-managed seqfile.

## Core Data Flow

File access protection:
- `__debugfs_file_get()` lazily creates `struct debugfs_fsdata`, records available methods, and increments `active_users`.
- If a dentry has been unlinked or active users are draining, it returns `-EIO`.
- `debugfs_file_put()` decrements `active_users` and completes `active_users_drained` when the last protected user exits.

Proxy operations:
- `open_proxy_open()` protects only open, obtains module fops via `fops_get()`, replaces file fops, and calls real open.
- `debugfs_full_proxy_file_operations` keeps all main operations behind `debugfs_file_get()`/`put()`.
- `debugfs_full_short_proxy_file_operations` adapts `struct debugfs_short_fops` for llseek/read/write only.
- Full proxy release always calls real release without removal protection to avoid leaking per-open resources.

Typed attributes:
- Numeric helpers use `DEFINE_DEBUGFS_ATTRIBUTE` or signed variants, with mode selection between rw/ro/wo fops.
- Boolean helpers print `Y\n` or `N\n` and parse userspace boolean text.
- String helper copies the current string for read and replaces it with an RCU-published allocation on write.
- Blob helper reads/writes a fixed `debugfs_blob_wrapper`.
- u32 array helper formats a fixed array into an open-time buffer.
- regset32 helper reads hardware registers with optional runtime PM get/put.
- device-managed seqfile helper allocates a small devm-owned entry and opens a single seqfile.

## Important Dependencies

- `internal.h` for `debugfs_inode_info`, `debugfs_fsdata`, and method bit flags.
- VFS file operations, seq_file, simple_attr, simple_read/write helpers.
- Kernel lockdown API through `security_locked_down(LOCKDOWN_DEBUGFS)`.
- Module lifetime APIs through `fops_get()` and `fops_put()`.
- Runtime PM and I/O memory access for regset32 support.

## Edge Cases and Risks

- Unsafe debugfs file creators require callers to protect their handlers or use safe helper fops.
- Removal can block waiting for active users; cancellation callbacks exist to avoid deadlocks or long waits.
- Lockdown allows only strictly world-readable, non-mutating debugfs files without ioctl or mmap.
- String writes require strict append semantics and cap stored content to one page.
- Blob writes assume caller-provided storage remains valid and sized correctly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/debugfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/debugfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/debugfs/inode.c

## Purpose

`inode.c` implements the debugfs pseudo-filesystem: mount context parsing, superblock/inode setup, public create APIs, recursive removal, rename support, enable/disable boot handling, and filesystem registration.

## Main Responsibilities

- Registers the `debugfs` filesystem and `/sys/kernel/debug` mount point.
- Parses mount options `uid`, `gid`, `mode`, and `source`.
- Applies root inode ownership/mode options on mount and remount.
- Allocates debugfs-specific inodes from `debugfs_inode_cache`.
- Creates files, directories, automounts, and symlinks.
- Removes debugfs trees while coordinating with active file users.
- Supports lookup, lookup-and-remove, and `debugfs_change_name()`.
- Tracks whether debugfs is enabled and registered.

## Core Data Flow

Mount setup:
- `debugfs_init_fs_context()` allocates `struct debugfs_fs_info` and installs fs-context operations.
- `debugfs_get_tree()` uses `get_tree_single()` with `debugfs_fill_super()`.
- `debugfs_fill_super()` calls `simple_fill_super()`, sets super operations, installs dentry operations, marks dentries `DCACHE_DONTCACHE`, and applies mount options.

Creation:
- `debugfs_start_creating()` checks enable/registration state, pins the filesystem, chooses the root if parent is NULL, and starts simple creation.
- `__debugfs_create_file()` creates a regular inode, stores `i_private`, real fops/short fops/raw pointer, aux data, and uses `d_make_persistent()`.
- Directory and automount creators set directory inode operations, link counts, and fsnotify events.
- Symlink creation duplicates target text into `i_link`.

Removal:
- `debugfs_remove()` pins the filesystem, calls `simple_recursive_removal()`, and releases the pin.
- `remove_one()` invokes `__debugfs_file_removed()` for regular files.
- `__debugfs_file_removed()` pairs with `debugfs_file_get()`, drains active users, and runs registered cancellation callbacks until active operations finish.

Rename:
- `debugfs_change_name()` formats a new name, looks up the target, starts VFS rename locking, snapshots the old name, calls `d_move()`, and sends fsnotify move events.

## Important Dependencies

- `file.c` for protected debugfs file operations and removal coordination.
- VFS simple filesystem helpers.
- config through kernel boot parameter `debugfs=on|off|no-mount`.
- Security lockdown checks in setattr and file access paths.
- `d_make_persistent()`/`d_make_discardable()` from dcache for persistent debugfs dentries.

## Edge Cases and Risks

- When debugfs is disabled at boot, initialization returns `-EPERM` and create calls return errors.
- Callers are expected to tolerate failed debugfs creation; many APIs return error dentries intentionally.
- File removal must not free private data until all protected handlers have left.
- Mode/uid/gid changes are denied under kernel lockdown because file mode participates in debugfs lockdown heuristics.
- `debugfs_end_creating()` returns a borrowed persistent dentry; lifecycle differs from ordinary transient dentry references.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/debugfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/debugfs/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/debugfs/internal.h

## Purpose

Defines debugfs-private inode and file-removal bookkeeping structures shared by `inode.c` and `file.c`.

## Main Responsibilities

- Defines `struct debugfs_inode_info`, embedding the VFS inode plus a union of stored debugfs operation pointers.
- Provides `DEBUGFS_I()` to convert from `struct inode` to debugfs inode info.
- Declares debugfs proxy/noop file operation tables implemented in `file.c`.
- Defines `struct debugfs_fsdata`, the per-dentry active-user and cancellation state used during protected file access/removal.
- Defines method bit flags for llseek, read, write, poll, and ioctl availability.

## Important Dependencies

- VFS `struct inode`, `struct file_operations`, and debugfs public types.
- Refcount, completion, mutex, and list state used by removal coordination.

## Edge Cases and Risks

- `debugfs_inode_info` stores several mutually exclusive pointer types in a union; creators and proxy open paths must agree on which type was stored.
- `debugfs_fsdata` cancellation entries can point to stack-allocated objects, so removal and leave paths must serialize through `cancellations_mtx`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/debugfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/devpts/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/devpts/Makefile

## Purpose

Builds the `/dev/pts` virtual filesystem when Unix98 PTYs are enabled.

## Main Responsibilities

- Adds `devpts.o` to the build under `CONFIG_UNIX98_PTYS`.
- Defines `devpts-y` as `inode.o`.

## Dependencies

- Controlled by `CONFIG_UNIX98_PTYS`.
- The compiled filesystem logic lives in `fs/devpts/inode.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/devpts/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/devpts/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/devpts/inode.c

## Purpose

`inode.c` implements the `devpts` filesystem used for Unix98 PTY slave nodes under `/dev/pts`, including per-instance mount state, `/dev/pts/ptmx`, PTY index allocation, and sysctl limits.

## Main Responsibilities

- Registers the `devpts` filesystem with user-namespace mount support.
- Exposes sysctls under `kernel/pty`: `max`, `reserve`, and `nr`.
- Parses mount options: `uid`, `gid`, `mode`, `ptmxmode`, `newinstance`, and `max`.
- Creates a per-mount root directory and `ptmx` character device node.
- Resolves the correct devpts mount for `/dev/ptmx` opens and bind-mounted `ptmx` cases.
- Allocates and frees PTY indexes with global and per-instance limits.
- Creates and removes slave PTY dentries named by index.
- Stores and retrieves per-PTY private data through `d_fsdata`.

## Core Data Flow

Mount setup:
- `devpts_init_fs_context()` allocates `struct pts_fs_info`, initializes `ida`, default modes, global root uid/gid, max, and reserve behavior for the initial mount namespace.
- `devpts_fill_super()` creates the root directory inode and calls `mknod_ptmx()`.
- `mknod_ptmx()` creates inode number 2 as a `TTYAUX_MAJOR:2` character device with configured `ptmxmode`.

PTY mount acquisition:
- `devpts_acquire()` finds a devpts superblock from a file path or adjacent `pts` directory and increments `s_active`.
- `devpts_release()` drops the superblock reference.
- `devpts_mntget()` validates that a file path corresponds to the expected `pts_fs_info`.

PTY allocation:
- `devpts_new_index()` increments global `pty_count`, enforces reserve and max limits, and allocates an IDA index.
- `devpts_kill_index()` frees the index and decrements global count.
- `devpts_pty_new()` creates a slave character-device inode `UNIX98_PTY_SLAVE_MAJOR:index`, applies configured uid/gid/mode, creates a persistent dentry, and emits fsnotify create.
- `devpts_pty_kill()` clears private data, drops link count, unhashes the dentry, emits fsnotify unlink, and makes it discardable.

## Important Dependencies

- TTY/PTY core code calls the exported devpts helpers.
- VFS simple filesystem helpers and dcache persistent/discardable dentry APIs.
- IDA for per-instance PTY index allocation.
- sysctl infrastructure for global PTY limits.
- `path_pts()` and mount traversal helpers for `/dev/ptmx` resolution.

## Edge Cases and Risks

- Global PTY reserve is preserved for the initial mount namespace; other instances account against `pty_reserve`.
- `ptmxmode` defaults to `0000` to avoid unexpected access in legacy scenarios.
- `devpts_ptmx_path()` only accepts paths rooted at a devpts filesystem mounted as expected.
- PTY count must be decremented when IDA allocation fails or indexes are killed.
- `dentry->d_fsdata` is used for caller private data and must be cleared before removal.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/devpts/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/direct-io.c -->
# File Research: sources/os/linux/linux-stable/fs/direct-io.c

## Purpose

`direct-io.c` implements the legacy blockdev direct I/O helper `__blockdev_direct_IO()`, mapping user iter pages to filesystem blocks, constructing BIOs, submitting them, and completing synchronous or asynchronous direct reads/writes.

## Main Responsibilities

- Extracts and pins user pages from an `iov_iter`.
- Calls filesystem `get_block_t` to map file blocks to disk blocks.
- Builds BIOs from page sections while preserving logical contiguity requirements.
- Handles holes, short reads, partial-block alignment, and newly allocated block zeroing.
- Tracks in-flight BIOs and completion errors.
- Supports sync and async completion, including deferred completion workqueue use.
- Integrates with inode direct-I/O exclusion through `inode_dio_begin()` and `inode_dio_end()`.
- Performs post-direct-write page-cache invalidation and write sync handling.

## Core Data Structures

- `struct dio_submit`: submission-only cursor tracking current BIO, block size factors, block mapping cursor, deferred current page section, page queue, and iterator state.
- `struct dio`: shared submission/completion state, including inode, kiocb, op flags, async flags, BIO refcount, completion list, errors, result bytes, and embedded page array/work item.

## Key Control Flow

Entry:
- `__blockdev_direct_IO()` validates count, alignment, EOF reads, and locking mode.
- It determines whether I/O can be async; extending writes are forced sync to avoid exposing uninitialized blocks in simpler filesystems.
- It initializes DIO state, starts a block plug, and calls `do_direct_IO()`.

Mapping and submission:
- `dio_refill_pages()` batches extracted pages; on write page fault after blocks were mapped, it uses `ZERO_PAGE` to consume mapped blocks and avoid stale data exposure.
- `get_more_blocks()` calls the filesystem block mapper and records completion-private data.
- `do_direct_IO()` walks blocks and pages, handles holes, maps chunks, and calls `submit_page_section()`.
- `submit_page_section()` coalesces adjacent chunks on a page or sends the previous page section into BIO assembly.
- `dio_send_cur_page()` starts a new BIO or submits existing BIOs when logical/physical contiguity breaks.
- `dio_zero_block()` submits zero-page sections for partial newly allocated filesystem blocks.

Completion:
- Async BIOs complete through `dio_bio_end_aio()` and may queue `dio_aio_complete_work()`.
- Sync BIOs complete into `dio->bio_list`; `dio_await_completion()` reaps and processes them in process context.
- `dio_complete()` derives the return value, calls optional filesystem `end_io`, invalidates cache after writes, ends inode DIO, performs async write sync if needed, invokes kiocb completion, and frees state.

## Important Dependencies

- Filesystem `get_block_t` and optional `dio_iodone_t`.
- BIO and block layer APIs.
- Page pinning and `iov_iter_extract_pages()`.
- Inode direct-I/O counters and optional `DIO_LOCKING`.
- Page cache invalidation helpers for direct writes.
- Superblock `s_dio_done_wq` for deferred async completion.

## Edge Cases and Risks

- `-ENOTBLK` is used internally as a signal to stop direct write submission and let callers fall back to buffered I/O.
- Partial filesystem-block writes to newly allocated blocks require zeroing the unwritten portions on disk.
- Async extending writes are forced synchronous because size updates before I/O completion could expose uninitialized data.
- BIO coalescing must respect both physical adjacency and logical file-offset adjacency, especially for filesystems such as btrfs.
- AIO completion can race with submission; `dio_complete()` normalizes `-EIOCBQUEUED` in that path.
- Read holes are zero-filled up to aligned EOF; write holes may force fallback.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/direct-io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/dlm/Kconfig

## Purpose

Defines kernel configuration options for the Distributed Lock Manager.

## Main Responsibilities

- Adds `menuconfig DLM` as a tristate option.
- Requires `INET`, `SYSFS`, and `CONFIGFS_FS`.
- Describes DLM as a general-purpose distributed lock manager for kernel or userspace applications.
- Adds `DLM_DEBUG`, dependent on `DLM`, to expose debugfs lockspace files showing resources and locks.

## Dependencies

- DLM build requires networking and configfs/sysfs infrastructure.
- Debug output depends on debugfs support through the DLM debug code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/dlm/Makefile

## Purpose

Builds the DLM kernel module/object and selects its component source files.

## Main Responsibilities

- Adds `dlm.o` under `CONFIG_DLM`.
- Composes `dlm-y` from callback, config, directory, lock, lockspace, membership, memory, communications, plock, recovery, request queue, user, and utility modules.
- Adds `debug_fs.o` when `CONFIG_DLM_DEBUG` is enabled.

## Dependencies

- Controlled by `CONFIG_DLM` and optionally `CONFIG_DLM_DEBUG`.
- The listed object files collectively implement DLM lockspaces, wire communication, recovery, userspace API, and diagnostics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/ast.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/ast.c

## Purpose

`ast.c` handles DLM AST/BAST callback creation, suppression, queuing, execution, suspension, and resumption for lockspaces.

## Main Responsibilities

- Executes completion AST callbacks and blocking AST callbacks.
- Suppresses redundant callbacks with `dlm_may_skip_callback()`.
- Allocates and fills `struct dlm_callback` objects for queued callbacks.
- Routes callbacks to userspace lock holders through `dlm_user_add_ast()`.
- Runs callbacks immediately, through an ordered workqueue, or through a delayed list depending on lockspace flags.
- Starts/stops callback workqueues for filesystem lockspaces.
- Suspends callback delivery during recovery and resumes delayed callbacks in bounded batches.

## Key Control Flow

- `dlm_add_cb()` is the main entry point.
- For userspace locks, it hands off to `dlm_user_add_ast()`.
- For kernel locks, it first checks whether a callback may be skipped.
- If `LSFL_CB_DELAY` is set, it queues a prepared callback on `ls_cb_delay`.
- If `LSFL_SOFTIRQ` is set, it invokes the callback inline.
- Otherwise it queues work on `ls_callback_wq`.
- `dlm_callback_suspend()` sets delay mode and flushes outstanding work.
- `dlm_callback_resume()` drains delayed callbacks in batches of `MAX_CB_QUEUE`.

## Callback Suppression Rules

- BASTs can be skipped if the blocking mode is compatible with the last granted CAST mode.
- Consecutive BASTs are suppressed when the new mode is redundant or less restrictive under the PR/CW rule.
- CASTs update last granted mode and may request LVB copying for userspace locks when mode transition rules require it.

## Important Dependencies

- DLM lock/resource structures from `dlm_internal.h`.
- Lock mode compatibility from lock code.
- LVB transition table from `lvb_table.h`.
- Callback allocation/freeing from memory helpers.
- Userspace AST routing from `user.h`.
- Tracepoints `trace_dlm_ast` and `trace_dlm_bast`.

## Edge Cases and Risks

- Callback delivery mode depends on lockspace flags; recovery paths must correctly suspend/resume to avoid callbacks during unstable state.
- Suppression relies on `lkb_last_*` state being updated consistently.
- Delayed callbacks are allocated objects and must be freed after execution.
- Inline softirq delivery bypasses workqueue context, so callback functions must be valid for that context.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/ast.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/ast.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/ast.h

## Purpose

Declares the DLM callback management interface implemented by `ast.c`.

## Main Responsibilities

- Declares callback suppression and allocation helpers:
  - `dlm_may_skip_callback()`
  - `dlm_get_cb()`
  - `dlm_add_cb()`
- Declares callback lifecycle helpers:
  - `dlm_callback_start()`
  - `dlm_callback_stop()`
  - `dlm_callback_suspend()`
  - `dlm_callback_resume()`

## Dependencies

- Uses DLM lock block and callback types from internal DLM headers.
- Shared by DLM lock/recovery paths that need to enqueue or control callback delivery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/ast.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/config.c -->
# File Research: sources/os/linux/linux-stable/fs/dlm/config.c

## Purpose

`config.c` implements DLM runtime configuration through configfs, exposing clusters, lockspaces, member nodes, communication endpoints, addresses, and cluster-wide tunables.

## Main Responsibilities

- Registers the `/config/dlm` configfs subsystem.
- Creates the configfs hierarchy:
  - `<cluster>/spaces/<space>/nodes/<node>/...`
  - `<cluster>/comms/<comm>/...`
- Stores global DLM configuration in `dlm_config`.
- Provides configfs attributes for cluster tunables, comm endpoints, and node membership.
- Tracks local communication endpoint and per-node communication sequence numbers.
- Maintains lockspace membership and delayed “gone” node records.
- Provides DLM-internal accessors for configured nodes, communication sequence, local node ID, and local addresses.
- Defines rhashtable parameters for DLM resource hash tables.

## Configfs Objects

- `dlm_cluster`: top-level cluster group containing default `spaces` and `comms` groups.
- `dlm_space`: lockspace group containing a default `nodes` group and member lists.
- `dlm_comm`: communication endpoint item with node ID, local flag, address list, mark, and sequence.
- `dlm_node`: lockspace member item with node ID, weight, new flag, communication sequence, and release-recover value.
- `dlm_member_gone`: transient record used to report removed members later.

## Cluster Attributes

- `cluster_name`
- `tcp_port`
- `buffer_size`
- `rsbtbl_size`
- `recover_timer`
- `toss_secs`
- `scan_secs`
- `log_debug`
- `log_info`
- `protocol`
- `mark`
- `new_rsb_count`
- `recover_callbacks`

Some attributes reject changes while low-level communications are running, and privileged writes require `CAP_SYS_ADMIN`.

## Communication and Node Attributes

Comm attributes:
- `nodeid`
- `local`
- `addr` write-only binary `sockaddr_storage`
- `addr_list` textual formatted address list
- `mark`

Node attributes:
- `nodeid`
- `weight`
- `release_recover`

## Key Control Flow

Setup:
- `dlm_config_init()` initializes and registers the configfs subsystem.
- `make_cluster()` creates cluster, spaces, and comms groups and stores global pointers to `space_list` and `comm_list`.
- `make_space()` creates a lockspace and its nodes subgroup.
- `make_comm()` creates a comm endpoint and assigns a nonzero sequence number.
- `make_node()` creates a lockspace member, snapshots the comm sequence, and adds it to the space member list.

Removal:
- `drop_comm()` clears `local_comm` if needed, closes midcomms for the node, frees stored addresses, and drops the item.
- `drop_node()` moves removed node information into `members_gone` so DLM can report removal with `release_recover`.
- `drop_cluster()` removes default groups and clears global group pointers.

Accessors:
- `dlm_config_nodes()` returns an allocated array of active and gone nodes for a lockspace, clears new flags, and drains gone records.
- `dlm_comm_seq()` returns a comm endpoint sequence number under configfs locking.
- `dlm_our_nodeid()` returns the configured local comm nodeid.
- `dlm_our_addr()` copies one configured local address.

## Important Dependencies

- configfs core.
- DLM midcomms and lowcomms for address registration, close, running-state checks, and mark updates.
- Linux networking address structures.
- Rhashtable infrastructure for resource table configuration.

## Edge Cases and Risks

- `space_list`, `comm_list`, and `local_comm` are global pointers tied to configfs object lifetime.
- `dlm_our_nodeid()` assumes `local_comm` exists; callers must ensure local comm setup has completed.
- `drop_node()` can fail to allocate `dlm_member_gone`; in that case removal reporting is skipped.
- `addr` writes require exactly `sizeof(struct sockaddr_storage)` binary input and cap addresses at `DLM_MAX_ADDR_COUNT`.
- Protocol changes are rejected while lowcomms are running and SCTP requires `CONFIG_IP_SCTP`.
- `dlm_config_nodes()` returns heap memory that callers must free.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/config.h -->
# File Research: sources/os/linux/linux-stable/fs/dlm/config.h

## Purpose

Defines the public internal DLM configuration types, constants, global configuration object, and accessor prototypes used outside `config.c`.

## Main Responsibilities

- Defines `DLM_MAX_SOCKET_BUFSIZE`, `DLM_MAX_ADDR_COUNT`, and protocol constants for TCP/SCTP.
- Defines `struct dlm_config_node`, the membership snapshot returned to DLM code.
- Declares DLM resource rhashtable parameters.
- Defines `struct dlm_config_info`, the global cluster/runtime configuration structure.
- Declares `dlm_config_init()`, `dlm_config_exit()`, `dlm_config_nodes()`, `dlm_comm_seq()`, `dlm_our_nodeid()`, and `dlm_our_addr()`.

## Important Fields

`struct dlm_config_info` includes:
- TCP port and protocol.
- Buffer and resource table sizing.
- Recovery, toss, and scan timers.
- Debug/info logging toggles.
- Network packet mark.
- New resource count and recovery callback settings.
- Cluster name.

## Dependencies

- DLM lockspace length constants.
- Linux socket address storage for local address access.
- Used by DLM communications, membership, lockspace, and recovery code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/dlm/config.h -->