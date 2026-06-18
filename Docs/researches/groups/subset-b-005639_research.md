# subset-b-005639 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dcache.c -->
# sources/distributed-fs/ceph-client/fs/dcache.c

Purpose: implements the Linux VFS dentry cache: allocation, hashing, lookup, aliasing, lifecycle, pruning, rename/move handling, and cache initialization. The file is central to pathname resolution and inode lifetime because a positive dentry pins its inode until the dentry is deleted or reclaimed.

Important APIs/types/functions: exports dentry names (`empty_name`, `slash_name`, `dotdot_name`), `rename_lock`, lookup helpers (`d_lookup`, `__d_lookup`, `__d_lookup_rcu`, `d_hash_and_lookup`), allocation helpers (`d_alloc`, `d_alloc_anon`, `d_alloc_pseudo`, `d_alloc_name`, `d_alloc_parallel`), instantiation helpers (`d_instantiate`, `d_instantiate_new`, `d_add`, `d_make_root`, `d_obtain_alias`, `d_obtain_root`, `d_splice_alias`), lifecycle helpers (`dget_parent`, `dput`, `d_drop`, `d_delete`, `d_make_persistent`, `d_make_discardable`), pruning helpers (`shrink_dentry_list`, `prune_dcache_sb`, `shrink_dcache_sb`, `shrink_dcache_parent`, `shrink_dcache_for_umount`, `d_invalidate`), rename helpers (`d_move`, `d_exchange`, `d_ancestor`, `is_subdir`), and VFS cache boot hooks (`vfs_caches_init_early`, `vfs_caches_init`). Core state includes `dentry_hashtable`, `in_lookup_hashtable`, per-cpu dentry counters, external-name reference objects, per-superblock `list_lru`, and per-dentry `d_lock`, `d_seq`, `d_lockref`, flags, parent/child links, hash links, alias links, and waiters.

Control flow: lookup hashes the requested qstr, walks RCU-protected bucket lists, validates parent/name/hash/unhashed state, and either returns a refcounted dentry or a lockless RCU candidate with a sequence value the caller must revalidate. Parallel lookup allocates a `DCACHE_PAR_LOOKUP` dentry, checks the ordinary dcache under rename and inode directory sequence counters, then publishes the in-progress lookup in a separate hash so racing lookups can wait for `d_lookup_done`. Allocation chooses inline versus external names, initializes locks/lists/operation flags, and links children under the parent lock. Instantiation attaches an inode under inode and dentry locks, updates alias lists, type flags, security hooks, fsnotify flags, and negative counters. `dput` first attempts a lockref fast path; final references either retain cacheable dentries on the LRU or kill them through `__dentry_kill`, unlinking inode aliases, invoking filesystem callbacks, removing hashes, and recursively handling parents. Pruning walks dentry subtrees with `d_walk`, moves unused entries to private shrink lists, waits for entries already being killed, and frees them outside global LRU callbacks. Rename/move takes `rename_lock`, locks parents in ancestry-safe order, unhashes affected dentries, swaps or copies names, updates parent children lists, rehashes, updates fsnotify/fscrypt state, and wakes parallel lookup waiters if needed.

State and persistence: dcache is volatile in-memory kernel state, but it persists across lookups until pressure, invalidation, delete, unmount, or explicit dontcache/discardable policy removes dentries. Names longer than inline storage are separately allocated and refcounted with RCU-delayed freeing so snapshots survive concurrent rename. Per-cpu counters feed `/proc/sys/fs/dentry-state` and negative-dentry accounting; sysctls also expose `vfs_cache_pressure`, `vfs_cache_pressure_denom`, and `dentry-negative`. Persistent dentries are used by pseudo filesystems such as debugfs/devpts and carry an extra reference until made discardable.

Dependencies and integration: depends on core VFS structs, inode cache initialization, mount namespace helpers, fsnotify, fscrypt, LSM security hooks, lockref, sequence counters, list_lru shrinker APIs, RCU hlist-bl buckets, sysctl/procfs, memblock hash allocation, and runtime constant infrastructure. Filesystems integrate through `dentry_operations` callbacks (`d_hash`, `d_compare`, `d_revalidate`, `d_delete`, `d_prune`, `d_iput`, `d_release`, `d_real`, unalias hooks) and through `get_link`, lookup, automount, and inode mode/type bits.

Risks: correctness is dominated by lock ordering and RCU/sequence validation. Bugs can produce use-after-free during path walk, missed lookups during rename, alias loops for directories, leaked inode references, stale negative entries, mountpoint races, or reclaim deadlocks. External-name refcounts and `DCACHE_PAR_LOOKUP` wakeups are particularly sensitive. Dentry counters are approximate per-cpu values, so tests should not require exact instantaneous accounting under concurrency.

Test signals: path lookup, rename, unlink, rmdir, mount/unmount, exportfs filehandle, case-insensitive lookup, tmpfile, automount, shrinker, memory pressure, and parallel lookup tests exercise this file. Useful runtime signals are lockdep, KCSAN/KASAN, RCU stall reports, dentry-state sysctl sanity, fsnotify rename/create/delete events, and fstests covering NFS/exportable filesystems, overlay-style rename patterns, and unmount with busy dentries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/debugfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/debugfs/Makefile

Purpose: builds the debugfs filesystem object when `CONFIG_DEBUG_FS` is enabled.

Important APIs/types/functions: Kbuild variables `debugfs-objs := inode.o file.o` and `obj-$(CONFIG_DEBUG_FS) += debugfs.o`.

Control flow: Kbuild links `inode.o` and `file.o` into `debugfs.o`, then includes that object in the kernel or module according to the `CONFIG_DEBUG_FS` tristate-like build setting.

State and persistence: no runtime state; this is build metadata only. It determines whether the debugfs registration, inode cache, creation APIs, and file proxy helpers are compiled.

Dependencies and integration: integrates with the Linux kernel Kbuild system and the `CONFIG_DEBUG_FS` Kconfig option. `inode.c` owns filesystem registration and object creation, while `file.c` owns typed file helpers and removal-safe proxy operations.

Risks: missing an object here would surface as unresolved symbols or absent debugfs functionality. The file deliberately keeps debugfs as a two-object composite, so adding new source files requires updating `debugfs-objs`.

Test signals: kernel build with `CONFIG_DEBUG_FS=y` or module-style configurations should compile and expose debugfs APIs. A build with `CONFIG_DEBUG_FS=n` should omit `debugfs.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/debugfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/debugfs/file.c -->
# sources/distributed-fs/ceph-client/fs/debugfs/file.c

Purpose: implements debugfs file operation wrappers, removal-safe lifetime guards, cancellation support, lockdown checks, and helper APIs for creating common typed debugfs files.

Important APIs/types/functions: exports `debugfs_get_aux`, `debugfs_file_get`, `debugfs_file_put`, `debugfs_enter_cancellation`, `debugfs_leave_cancellation`, `debugfs_attr_read`, `debugfs_attr_write`, `debugfs_attr_write_signed`, typed creators for integer/hex/size/atomic/bool/string/blob/u32-array/regset/devm-seqfile values, and `debugfs_print_regs32`. It defines `debugfs_noop_file_operations`, `debugfs_open_proxy_file_operations`, `debugfs_full_proxy_file_operations`, and `debugfs_full_short_proxy_file_operations`. Internal state is `struct debugfs_fsdata`, which caches real or short fops, method bits, active-user refcount, drained completion, cancellation list, and cancellation mutex.

Control flow: debugfs file opens start through a proxy fops table stored in the inode by `inode.c`. `__debugfs_file_get` lazily allocates and installs `debugfs_fsdata` in `dentry->d_fsdata`, snapshots available file methods, rejects unlinked dentries, and increments `active_users`. Proxy read/write/llseek/ioctl/poll wrappers check method bits, call `debugfs_file_get`, dispatch to the real fops, and then call `debugfs_file_put`. Full proxy open additionally takes a module fops reference, applies lockdown policy, and releases the fops reference on close. Short proxy open uses `debugfs_short_fops` and `simple_open`. Cancellation registration adds stack-owned cancellation records to the fsdata list so `debugfs_remove` can invoke cancellation callbacks before waiting for active users to drain.

State and persistence: typed debugfs files expose caller-owned kernel variables or buffers through `inode->i_private`/`file->private_data`; the file does not own most pointed-to data. String writes allocate a replacement string, publish it with RCU assignment, synchronize RCU, and free the old string. Blob writes mutate the provided buffer. U32 array open formats a temporary text buffer and frees it on release. Regset reads can runtime-resume a device while reading MMIO registers. `debugfs_fsdata` lives on the dentry until `debugfs_release_dentry` in `inode.c` frees it.

Dependencies and integration: depends on VFS file operations, simple_attr helpers, seq_file, module refcounting, LSM lockdown, poll, PM runtime, IO memory accessors, devres allocation, and the debugfs internals declared in `internal.h`. It is tightly coupled to `inode.c`, which assigns proxy fops and calls removal hooks.

Risks: debugfs intentionally exposes diagnostic state, so permission and lockdown checks are security-sensitive. Callers using `debugfs_create_file_unsafe` must guard their own data lifetime unless their fops use `debugfs_file_get/put`. Removal can deadlock if a file operation waits indefinitely without registering a cancellation. Typed helper writes are simple stores without caller-specific locking, so exported variables need their own concurrency discipline. `debugfs_write_file_bool` returns `count` after a successful parse even if the write changed only one bool, which is expected but important for tests.

Test signals: create/remove races, module unload while files are open, lockdown mode access denial, read/write of all typed helper formats, cancellation callbacks during removal, `poll` fallback behavior, string append rules, blob bounds, register set seq output, and devm seqfile cleanup are the main coverage points. KASAN/lockdep should remain quiet during recursive removal with active users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/debugfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/debugfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/debugfs/inode.c

Purpose: implements debugfs filesystem registration, mount context parsing, superblock/inode allocation, object creation/removal, lookup, rename, automount, and boot-time enable/disable policy.

Important APIs/types/functions: exports `debugfs_lookup`, `debugfs_create_file_full`, `debugfs_create_file_short`, `debugfs_create_file_unsafe`, `debugfs_create_file_size`, `debugfs_create_dir`, `debugfs_create_automount`, `debugfs_create_symlink`, `debugfs_remove`, `debugfs_lookup_and_remove`, `debugfs_change_name`, and `debugfs_initialized`. Internals include `debugfs_fs_info` mount options, `debugfs_inode_cachep`, `debugfs_mount`, `debugfs_mount_count`, `debugfs_registered`, `debugfs_enabled`, inode operations for files/dirs/symlinks, `debugfs_super_operations`, `debugfs_dops`, and `debug_fs_type`.

Control flow: `debugfs_init` handles the `debugfs=` early parameter result, creates `/sys/kernel/debug`, creates a slab cache for `debugfs_inode_info`, registers the filesystem, and marks it initialized. Mount setup allocates fs context state, parses uid/gid/mode/source parameters, fills a single superblock with `simple_fill_super`, installs debugfs super ops and dentry ops, marks dentries dontcache, and applies root mount options. Creation APIs call `debugfs_start_creating`, which checks enabled/initialized state, pins the singleton filesystem, selects root when needed, and reserves a negative dentry. File creation allocates an inode, stores private data and raw fops in `DEBUGFS_I`, assigns proxy fops, marks the dentry persistent, and emits fsnotify. Directory, automount, and symlink creation similarly allocate suitable inodes and persistent dentries. Removal pins the filesystem, delegates recursive VFS removal to `simple_recursive_removal`, calls `__debugfs_file_removed` for regular files, and releases filesystem pins.

State and persistence: debugfs objects persist as VFS in-memory objects while their creators keep dentries and until `debugfs_remove` is called; there is no backing storage. The filesystem root mount options persist in `s_fs_info` across remounts. Persistent dentries hold extra references and are freed when recursive removal releases filesystem references and dcache state. `debugfs_release_dentry` frees per-dentry fsdata created by `file.c`.

Dependencies and integration: uses config through fs_context/fs_parser, simplefs helpers, dcache persistent dentry APIs, sysfs mount point creation, kobject `kernel_kobj`, LSM lockdown for setattr, fsnotify, namei helpers, seq_file mount option display, and debugfs proxy fops from `file.c`.

Risks: debugfs is optional and many callers intentionally ignore `ERR_PTR` returns, so creation helpers must tolerate error parents. Removal must synchronize with active file operations through `file.c` fsdata; missing that would allow freed private data to be accessed. Lockdown-sensitive mode/uid/gid changes are blocked to keep file modes meaningful for access policy. Rename uses VFS rename helpers and must release name snapshots and dentries on all paths.

Test signals: boot with `debugfs=on`, `debugfs=off`, and deprecated `debugfs=no-mount`; mount/remount option display and application; creating duplicate names; recursive removal with active readers; symlink and automount creation; rename to self and to existing targets; lookup reference handling; and lockdown tests for chmod/chown and unsafe file modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/debugfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/debugfs/internal.h -->
# sources/distributed-fs/ceph-client/fs/debugfs/internal.h

Purpose: declares the private debugfs data structures and proxy fops shared between `inode.c` and `file.c`.

Important APIs/types/functions: defines `struct debugfs_inode_info`, `DEBUGFS_I()`, external proxy file operation tables, `struct debugfs_fsdata`, and method-bit constants `HAS_READ`, `HAS_WRITE`, `HAS_LSEEK`, `HAS_POLL`, and `HAS_IOCTL`.

Control flow: `inode.c` stores raw file operations, short operations, automount callbacks, and auxiliary data in `debugfs_inode_info`; `file.c` reads these fields through `DEBUGFS_I()` to initialize per-dentry `debugfs_fsdata` and dispatch proxy operations.

State and persistence: `debugfs_inode_info` embeds the VFS inode and is allocated from the debugfs inode slab for inode lifetime. `debugfs_fsdata` is installed lazily in `dentry->d_fsdata` and holds active-user/cancellation state until dentry release.

Dependencies and integration: requires core inode, file operation, list, refcount, completion, mutex, and debugfs short-fops/automount type definitions from kernel headers. It is intentionally local to debugfs and not part of the external API.

Risks: the union in `debugfs_inode_info` requires the creator and opener to agree on whether the raw pointer is real fops, short fops, or automount callback. Method bits must stay synchronized with the proxy wrappers in `file.c`; otherwise wrappers may call absent operations or reject valid ones.

Test signals: compile-time coverage catches most type drift. Runtime signals come from creating full, short, noop, and automount debugfs entries, then opening/removing them under concurrent access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/debugfs/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/devpts/Makefile -->
# sources/distributed-fs/ceph-client/fs/devpts/Makefile

Purpose: builds the `/dev/pts` virtual filesystem implementation when Unix98 PTYs are enabled.

Important APIs/types/functions: Kbuild variables `obj-$(CONFIG_UNIX98_PTYS) += devpts.o` and `devpts-$(CONFIG_UNIX98_PTYS) := inode.o`.

Control flow: if `CONFIG_UNIX98_PTYS` is set, Kbuild compiles `inode.o` into `devpts.o` and links that object into the kernel build.

State and persistence: no runtime state; it controls availability of the devpts filesystem and PTY slave node management code.

Dependencies and integration: tied to the kernel PTY subsystem and the `CONFIG_UNIX98_PTYS` option.

Risks: build omissions break Unix98 PTY support. Additional devpts source files would need explicit inclusion here.

Test signals: kernel builds with Unix98 PTYs enabled should include devpts registration and allow mounting `devpts`; disabled builds should omit it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/devpts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/devpts/inode.c -->
# sources/distributed-fs/ceph-client/fs/devpts/inode.c

Purpose: implements the `devpts` filesystem used for Unix98 pseudo-terminal slave nodes, including mount option parsing, per-instance PTY allocation, `/dev/pts/ptmx`, sysctl limits, and creation/removal of numbered slave device nodes.

Important APIs/types/functions: exports `devpts_mntget`, `devpts_acquire`, `devpts_release`, `devpts_new_index`, `devpts_kill_index`, `devpts_pty_new`, `devpts_get_priv`, and `devpts_pty_kill`. Key state includes global sysctl values `pty_limit`, `pty_reserve`, `pty_count`; per-mount `struct pts_fs_info` with an `ida` of allocated PTYs, mount options, superblock, and borrowed ptmx inode; and `struct pts_mount_opts` for uid/gid/mode/ptmxmode/reserve/max.

Control flow: filesystem context initialization allocates `pts_fs_info`, initializes the IDA and defaults, and reserves PTYs for the initial mount namespace. Mount parsing accepts uid, gid, mode, ptmxmode, newinstance, and max. `devpts_fill_super` creates an anonymous superblock, root directory, and a `ptmx` character node with major `TTYAUX_MAJOR` minor 2. PTY allocation increments the global count, checks global limit minus reserve for non-reserved mounts, and allocates a per-instance IDA index. `devpts_pty_new` creates a numbered character-device inode under the devpts root, assigns uid/gid from mount options or current credentials, stores private TTY data in `d_fsdata`, marks the dentry persistent, and sends fsnotify create. `devpts_pty_kill` clears private data, drops link count, unhashes, emits unlink notification, and makes the persistent dentry discardable.

State and persistence: devpts is in-memory. Per-mount IDA state persists for the life of the superblock. The global PTY count and sysctl limits persist for the kernel lifetime. Device nodes persist while the corresponding PTY exists; removal discards their dcache references. Mount options persist in `s_fs_info` and remount updates ptmx mode plus node creation defaults.

Dependencies and integration: integrates with the TTY core, `devpts_fs.h`, mount/namei helpers, fs_context parser, IDA allocator, sysctl under `kernel/pty`, VFS simple directory operations, dcache persistent helpers, fsnotify, user namespace mount support (`FS_USERNS_MOUNT`), and path helpers for finding a suitable devpts mount when `/dev/ptmx` is a symlink or bind mount.

Risks: PTY accounting must roll back on allocation failure or the system can leak capacity. `devpts_mntget` path walking must reject mismatched devpts instances, especially with bind-mounted `ptmx`. Mount option remount semantics intentionally reset defaults in ways that are UAPI-sensitive. Persistent dentry handling must pair `devpts_pty_new` and `devpts_pty_kill` to avoid stale slave nodes or dangling `d_fsdata`.

Test signals: mount devpts with uid/gid/mode/ptmxmode/max combinations, open `/dev/ptmx` through direct, symlink, and bind-mount layouts, allocate until global and per-instance limits, verify reserve behavior outside the initial namespace, create/remove PTYs while watching fsnotify, remount ptmxmode, and run PTY stress tests under mount namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/devpts/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/direct-io.c -->
# sources/distributed-fs/ceph-client/fs/direct-io.c

Purpose: implements the legacy blockdev direct-I/O engine used by filesystems that provide a `get_block_t` mapping callback. It maps user iterators to BIOs while bypassing the page cache, handles holes/partial blocks, coordinates synchronous and asynchronous completion, and protects truncate through inode DIO accounting.

Important APIs/types/functions: exports `__blockdev_direct_IO`. Internal structures are `struct dio_submit` for submission-local cursors and `struct dio` for state shared with BIO completion. Key helpers include page extraction (`dio_refill_pages`, `dio_get_page`), page pin accounting (`dio_pin_page`, `dio_unpin_page`), BIO lifecycle (`dio_bio_alloc`, `dio_bio_submit`, `dio_bio_end_io`, `dio_bio_end_aio`, `dio_bio_complete`, `dio_await_completion`, `dio_bio_reap`), mapping (`get_more_blocks`, `do_direct_IO`), partial-block zeroing (`dio_zero_block`), deferred page section assembly (`submit_page_section`, `dio_send_cur_page`), and completion (`dio_complete`, `dio_aio_complete_work`).

Control flow: `__blockdev_direct_IO` validates zero-length reads, alignment against inode or block-device block size, EOF reads, and locking requirements. It allocates `struct dio`, samples file size, decides sync versus async mode, initializes DIO accounting and submission cursors, starts a block plug, and calls `do_direct_IO`. The main loop extracts user pages in batches, maps file blocks through `get_block`, handles holes by zeroing reads or returning `-ENOTBLK` for writes that should fall back to buffered I/O, cleans aliases for newly allocated blocks, splits page ranges into block-aligned sections, and builds contiguous BIOs. Completion either waits synchronously and reaps BIOs from `bio_list`, or returns `-EIOCBQUEUED` so asynchronous BIO endio completes the kiocb. `dio_complete` folds page faults, BIO errors, transferred byte count, short EOF reads, optional filesystem `end_io`, post-write invalidation, inode DIO end, async `ki_complete`, and slab free.

State and persistence: all request state is transient. User pages may be pinned and are unpinned as sections enter BIOs or cleanup runs. `inode_dio_begin/end` increments per-inode in-flight DIO state so truncate can wait externally. Filesystem-specific `map_bh.b_private` is copied to `dio->private` and returned to `end_io`. Async completion may persist briefly on the superblock `s_dio_done_wq` when sync or invalidation work must run in process context.

Dependencies and integration: depends on BIO/block-layer APIs, `iov_iter_extract_pages`, buffer_head mapping, filesystem `get_block` and optional `dio_iodone_t`, inode locking and writeback helpers, page-cache invalidation, task I/O accounting, write sync helpers, block plugs, and superblock direct-I/O workqueue initialization.

Risks: alignment, hole fallback, and partial-block zeroing are correctness-sensitive because stale disk data can leak if newly allocated blocks are not zeroed around sub-block writes. Async write extension is forced synchronous to avoid exposing uninitialized blocks before i_size-safe completion. Refcounting between submit path and BIO endio must stay exact or completion can double-free or never complete. Error precedence is subtle: transferred bytes suppress some page faults, `BLK_STS_AGAIN` maps to `-EAGAIN` only for NOWAIT, and `-ENOTBLK` is converted to short buffered fallback.

Test signals: direct I/O reads/writes with aligned and minimally aligned buffers, EOF short reads, holes, DIO_SKIP_HOLES fallback, extending writes, AIO writes with O_DSYNC/O_SYNC, NOWAIT failures, block-device direct I/O, memory-fault injection during writes, page-cache invalidation races with mmap/buffered I/O, truncate waiting on DIO, and filesystem `end_io` private-state callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/direct-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/Kconfig -->
# sources/distributed-fs/ceph-client/fs/dlm/Kconfig

Purpose: declares kernel configuration options for the Distributed Lock Manager.

Important APIs/types/functions: `menuconfig DLM` is a tristate option depending on `INET`, `SYSFS`, and `CONFIGFS_FS`; `config DLM_DEBUG` is a bool depending on `DLM`.

Control flow: enabling `DLM` allows the DLM subsystem to be built for kernel or userspace lock clients. Enabling `DLM_DEBUG` adds debugfs support that creates lockspace files under the `dlm` debugfs directory.

State and persistence: no runtime state directly; these options determine which source objects and debug surfaces are compiled.

Dependencies and integration: DLM requires networking, sysfs, and configfs because cluster membership and communication configuration are provided through configfs and lock managers communicate over network transports.

Risks: disabling configfs/sysfs/INET makes DLM unavailable. Debug output can expose lockspace details and depends on debugfs availability.

Test signals: config matrix builds should verify `DLM=n`, `DLM=y/m`, and `DLM_DEBUG=y` combinations, including debugfs object inclusion only when requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/Makefile -->
# sources/distributed-fs/ceph-client/fs/dlm/Makefile

Purpose: defines the composite object list for the kernel Distributed Lock Manager.

Important APIs/types/functions: `obj-$(CONFIG_DLM) += dlm.o`; `dlm-y` includes callback, config, directory, lock, lockspace, main, member, memory, mid/low comms, plock, recovery, request queue, user, and utility objects; `dlm-$(CONFIG_DLM_DEBUG) += debug_fs.o`.

Control flow: Kbuild links all core DLM objects into `dlm.o` when `CONFIG_DLM` is enabled, with `debug_fs.o` conditionally included for debugfs diagnostics.

State and persistence: no runtime state directly, but the object list determines whether DLM includes configfs, networking, recovery, userspace device, and debug functionality.

Dependencies and integration: coordinates all DLM implementation files in this directory and mirrors the Kconfig debug split.

Risks: missing an object can produce unresolved symbols or silently remove a subsystem path such as recovery or user AST delivery. Conditional debug object inclusion must match header stubs in `dlm_internal.h`.

Test signals: full DLM build, module link, and debug-enabled builds should compile cleanly; symbol resolution across DLM components is the primary check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/ast.c -->
# sources/distributed-fs/ceph-client/fs/dlm/ast.c

Purpose: manages DLM asynchronous callbacks for kernel lock clients: completion ASTs (CAST) and blocking ASTs (BAST). It suppresses redundant callbacks, captures callback state, queues callbacks during recovery/suspension, and dispatches them either directly, through an ordered workqueue, or to the userspace DLM path.

Important APIs/types/functions: exports `dlm_may_skip_callback`, `dlm_get_cb`, `dlm_add_cb`, `dlm_callback_start`, `dlm_callback_stop`, `dlm_callback_suspend`, and `dlm_callback_resume`. Internal helpers are `dlm_run_callback`, `dlm_do_callback`, `dlm_callback_work`, and `dlm_get_queue_cb`. Key state lives in `struct dlm_lkb` fields such as last callback mode/flags/timestamps, `lkb_lksb`, AST/BAST function pointers, and in `struct dlm_ls` callback lock, delay list, flags, and callback workqueue.

Control flow: `dlm_add_cb` first routes userspace locks to `dlm_user_add_ast`. Kernel locks are checked through `dlm_may_skip_callback`, which suppresses compatible or redundant BASTs and records CAST/BAST history; for user locks it can request LVB copy based on mode transition table. With `ls_cb_lock` held, callbacks are either appended to `ls_cb_delay` when callback delay is active, invoked immediately in softirq mode, or wrapped in a `dlm_callback` and queued to `ls_callback_wq`. Workqueue execution calls the captured AST/BAST function and frees the callback object. Suspend sets the delay flag and flushes in-flight work. Resume drains delayed callbacks in batches of 25, dispatching them according to softirq/workqueue mode, clears the delay flag once empty, and yields between batches.

State and persistence: callback objects are transient allocations from DLM memory helpers. Delayed callback lists persist across recovery suspension until resume. Last callback mode/time fields persist on each lock block and affect future suppression. CAST dispatch writes status and flags into the caller's `dlm_lksb` before invoking `astfn`.

Dependencies and integration: depends on DLM lock/resource/lockspace structures, LVB operation tables, userspace AST support, DLM memory allocation, tracepoints (`trace_dlm_ast`, `trace_dlm_bast`), workqueues, spinlocks with bottom-half disabling, and DLM mode compatibility logic from lock code.

Risks: skipping logic must not suppress a callback required by a client to make progress. Callback ordering matters, hence ordered workqueue and suspension delay. AST functions are external callbacks, so calling context (`LSFL_SOFTIRQ` versus workqueue) is a contract. Incorrect active delay handling can lose callbacks during recovery or invoke them while lockspace state is inconsistent.

Test signals: lock conversion and blocking scenarios should verify CAST/BAST delivery order, duplicate BAST suppression, LVB copy decisions, userspace AST routing, recovery suspend/resume queue draining, workqueue allocation failure handling, tracepoint emission, and softirq-mode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/ast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/ast.h -->
# sources/distributed-fs/ceph-client/fs/dlm/ast.h

Purpose: declares the DLM callback management interface implemented by `ast.c`.

Important APIs/types/functions: prototypes for `dlm_may_skip_callback`, `dlm_get_cb`, `dlm_add_cb`, `dlm_callback_start`, `dlm_callback_stop`, `dlm_callback_suspend`, and `dlm_callback_resume`.

Control flow: lock management code includes this header to decide whether callbacks can be skipped, allocate callback records, enqueue AST/BAST notifications, and manage callback execution around lockspace lifecycle and recovery.

State and persistence: no state in the header; it exposes operations over `struct dlm_lkb`, `struct dlm_callback`, and `struct dlm_ls` state owned elsewhere.

Dependencies and integration: depends on DLM internal type declarations provided before inclusion, especially lock blocks, callback records, and lockspaces. It links `lock.c`, `recoverd`, userspace paths, and lockspace lifecycle to `ast.c`.

Risks: signature changes must stay synchronized with callers and with userspace/user-lock routing semantics. `copy_lvb` is optional and must be handled by callers that care about lock value block propagation.

Test signals: compile coverage across DLM objects and runtime callback delivery tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/ast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/config.c -->
# sources/distributed-fs/ceph-client/fs/dlm/config.c

Purpose: implements DLM configfs configuration for clusters, lockspaces, member nodes, communication endpoints, global DLM tunables, and communication lookup helpers used by runtime DLM code.

Important APIs/types/functions: exports `dlm_config_init`, `dlm_config_exit`, `dlm_config_nodes`, `dlm_comm_seq`, `dlm_our_nodeid`, and `dlm_our_addr`, and defines global `dlm_config`. Configfs object types include clusters, spaces, comms, and nodes. Key structures are `dlm_cluster`, `dlm_space`, `dlm_comm`, `dlm_node`, `dlm_member_gone`, and `dlm_config_info`. It also exports `dlm_rhash_rsb_params` for resource hash tables.

Control flow: `dlm_config_init` registers a configfs subsystem rooted at `dlm`. Creating a cluster creates default `spaces` and `comms` groups and records their config groups globally. Creating a space creates a `nodes` subgroup with member lists protected by `members_lock`. Creating a comm parses the item name as nodeid, assigns a nonzero monotonically increasing sequence, and stores address/mark/local attributes. Creating a node parses nodeid, records default weight, marks it new, snapshots the comm sequence, and adds it to the space members list. Dropping a node moves its nodeid and `release_recover` setting to `members_gone` so the next `dlm_config_nodes` call can report departed members before freeing that queued state. `dlm_config_nodes` finds a lockspace by name, snapshots active and gone members into caller-allocated `dlm_config_node` entries, clears `new` flags, drains gone entries, and returns count. Comm attribute stores validate binary sockaddr size and maximum address count, pass addresses to midcomms, and update packet marks through lowcomms.

State and persistence: configfs objects persist while userspace keeps the corresponding directories/items. `space_list`, `comm_list`, `local_comm`, `dlm_comm_count`, per-space member lists, per-comm addresses, and global `dlm_config` are in-kernel state. Tunables such as TCP port and protocol persist until changed and reject changes while lowcomms is running where required. Gone-member state persists only until DLM reads it through `dlm_config_nodes`.

Dependencies and integration: depends on configfs, capabilities, socket address types, IPv4/IPv6 formatting, SCTP config option, midcomms address validation/close, lowcomms running and mark APIs, DLM constants, resource hash tables, and DLM membership/recovery code that consumes node snapshots.

Risks: configfs locking is subtle; `get_comm` assumes `clusters_root.subsys.su_mutex` is held unless `dlm_comm_seq` locks around it. Dropping a node can fail to allocate `dlm_member_gone`, losing departure metadata. `local_comm` is a raw pointer to a configfs object and must be cleared when that comm drops. Address writes are binary `sockaddr_storage`, so userspace tooling must write exact-sized buffers. Changing transport parameters while DLM is active is blocked to avoid inconsistent network state.

Test signals: configfs create/remove sequences for clusters, spaces, comms, and nodes; invalid names and attributes; CAP_SYS_ADMIN enforcement for cluster tunables; protocol validation with and without SCTP; lowcomms-running rejection; multiple addresses and addr_list formatting; local node selection; node add/drop snapshots from `dlm_config_nodes`; comm sequence changes; and resource hash initialization behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/config.h -->
# sources/distributed-fs/ceph-client/fs/dlm/config.h

Purpose: defines the public internal configuration contract for DLM configfs state and tunables.

Important APIs/types/functions: defines `DLM_MAX_SOCKET_BUFSIZE`, `DLM_MAX_ADDR_COUNT`, protocol constants `DLM_PROTO_TCP` and `DLM_PROTO_SCTP`, `struct dlm_config_node`, `struct dlm_config_info`, external `dlm_rhash_rsb_params`, external global `dlm_config`, and prototypes for config lifecycle and lookup helpers.

Control flow: DLM startup calls `dlm_config_init`; shutdown calls `dlm_config_exit`; membership/recovery code calls `dlm_config_nodes`; communication code calls `dlm_comm_seq`, `dlm_our_nodeid`, and `dlm_our_addr` to derive configured network state.

State and persistence: the header models snapshots of configfs state. `dlm_config_node` carries active/gone/new member data plus comm sequence and recovery release flags. `dlm_config_info` carries cluster-wide tunables including port, buffer size, hash table size, recovery/scanning timers, logging flags, protocol, packet mark, new resource count, callback recovery behavior, and cluster name.

Dependencies and integration: used by DLM config, lockspace, recovery, member, and communication code. It depends on DLM constants for lockspace name length and on socket storage declarations through including translation units.

Risks: fields in `dlm_config_info` are global mutable runtime tunables, so consumers must understand which can change while DLM is running. `dlm_our_nodeid` assumes a local comm has been configured. `dlm_config_nodes` allocates memory for callers to free, so ownership must be clear in callers.

Test signals: compile coverage, configfs membership snapshots, communication address lookup, and transport/timer tunable consumption validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/config.h -->
