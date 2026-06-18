# Group Research: group_729_linux_sources_os_linux_linux_fs_dcache_c_sources_os_linux_linux_fs_d_3b93260e9f34

Scope: `Docs/research_subset_a.md` / `sources/os/linux/linux`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dcache.c -->
# File Research: sources/os/linux/linux/fs/dcache.c

## Purpose

`fs/dcache.c` implements the Linux VFS dentry cache. It owns dentry allocation, lookup, hashing, aliasing, instantiation, reference release, LRU/shrinker integration, subtree pruning, mountpoint checks, rename/move handling, disconnected/root aliases, temporary dentries, and early VFS cache initialization.

This is a core VFS file: path lookup, mount handling, exportable filesystem aliases, filesystem `dentry_operations`, inode lifetime, fsnotify, fscrypt rename hooks, and memory reclaim all depend on the invariants here.

## Main State

- `rename_lock`: exported seqlock for detecting and serializing topology-changing rename/move operations.
- `dentry_hashtable`: global hash table for normal dcache lookup, indexed by dentry name hash.
- `in_lookup_hashtable`: side hash for parallel in-progress lookups created by `d_alloc_parallel()`.
- `__dentry_cache`: slab cache for `struct dentry`.
- Per-CPU counters: `nr_dentry`, `nr_dentry_unused`, and `nr_dentry_negative`.
- Sysctls: `vm.vfs_cache_pressure`, `vm.vfs_cache_pressure_denom`, `fs.dentry-state`, and `fs.dentry-negative`.
- Exported qstr constants: `empty_name`, `slash_name`, and `dotdot_name`.

The documented lock order is central: `inode->i_lock` nests outside `dentry->d_lock`, which nests outside superblock LRU/hash/root locks. Parent dentries lock before children when ancestor relationships exist; otherwise rename activity is serialized or detected by `rename_lock`.

## Names And Comparison

Short dentry names live inline in `d_shortname`; long names use a refcounted `struct external_name` freed after RCU grace. `dentry_string_cmp()` has a word-at-a-time implementation under `CONFIG_DCACHE_WORD_ACCESS` and a byte loop fallback. `dentry_cmp()` deliberately tolerates transient rename inconsistency because callers validate with `d_seq`.

`take_dentry_name_snapshot()` and `release_dentry_name_snapshot()` provide a safe name snapshot across concurrent rename by combining RCU, `d_seq`, and external-name refcounts.

## Allocation And Instantiation

Allocation paths:

- `__d_alloc()` allocates and initializes an unhashed dentry, chooses inline versus external name storage, applies default dentry ops, and runs `d_init`.
- `d_alloc()` attaches a child dentry to a parent.
- `d_alloc_anon()` creates an anonymous root-style dentry.
- `d_alloc_cursor()` creates a cursor dentry for directory iteration.
- `d_alloc_pseudo()` creates NORCU pseudo dentries for lookup-less objects such as sockets and pipes.
- `d_alloc_name()` hashes a C string name and delegates to `d_alloc()`.

Instantiation paths:

- `d_instantiate()` attaches a caller-owned inode ref to a negative dentry.
- `d_instantiate_new()` combines instantiation with `I_NEW`/`I_CREATING` completion.
- `d_add()` hashes a dentry and optionally instantiates it.
- `d_make_persistent()` creates a pinned persistent dentry used by pseudo filesystems such as debugfs and devpts.
- `d_make_discardable()` releases that persistent pin.
- `d_make_root()`, `d_obtain_alias()`, and `d_obtain_root()` build root or export-handle aliases.

`d_flags_for_inode()` encodes type flags, automount needs, symlink behavior, and lookup availability into dentry flags. `set_default_d_op()` stores default dentry ops and cached operation flags in the superblock.

## Lookup

Two lookup families are provided:

- RCU/store-free lookup: `__d_lookup_rcu()` and the `DCACHE_OP_COMPARE` variant return a candidate plus `d_seq` for path-walk validation.
- Refcounted lookup: `__d_lookup()` may false-negative under unrelated rename; `d_lookup()` wraps it with `rename_lock` retry to avoid that.

`d_hash_and_lookup()` computes the standard hash, applies filesystem `d_hash` if present, and then performs lookup. `d_same_name()` compares either by raw name/hash or filesystem `d_compare`.

`d_alloc_parallel()` coordinates concurrent lookups for the same parent/name using `in_lookup_hashtable`, `DCACHE_PAR_LOOKUP`, `i_dir_seq`, and waiters. `__d_lookup_unhash_wake()` transitions an in-lookup dentry out of that state and wakes waiters after the directory sequence update is safe.

## Lifetime And Eviction

`dput()` first tries `fast_dput()` with lockref and RCU. If the last reference is dropped and the dentry cannot be retained, `finish_dput()` repeatedly calls `dentry_kill()` upward through parents.

`retain_dentry()` decides whether a zero-ref dentry can stay cached. It rejects unhashed, disconnected, delete-requested, and `DCACHE_DONTCACHE` dentries; otherwise it puts the dentry on the LRU or marks it referenced.

`dentry_kill()` is the single eviction path. It handles `d_lock` versus `inode->i_lock` ordering, marks the lockref dead, calls `d_prune` if present, removes LRU/hash state, detaches inode aliases, runs `d_release`, unlinks from parent/root lists, and frees immediately or leaves final free to shrink-list ownership.

Positive dentries keep inodes alive. `dentry_unlink_inode()` clears dentry type/inode state, removes alias linkage, optionally notifies removal, then calls filesystem `d_iput` or `iput`.

## LRU, Shrinkers, And Pruning

LRU helper functions keep flags and counters consistent: `d_lru_add()`, `d_lru_del()`, `d_shrink_add()`, `d_shrink_del()`, `d_lru_isolate()`, `d_lru_shrink_move()`, `__move_to_shrink_list()`, and `dput_to_list()`.

Negative dentries are counted only while on the real superblock LRU, not while temporarily on shrink lists.

Reclaim paths include `prune_dcache_sb()`, `shrink_dcache_sb()`, `d_prune_aliases()`, and `shrink_dentry_list()`.

`d_walk()` is the central non-recursive tree walker. It handles cursor dentries, rename retries, lock handoff during descent/ascent, and caller-directed continue/quit/skip/no-retry actions. It supports `path_has_submounts()`, `shrink_dcache_parent()`, `shrink_dcache_for_umount()`, and `d_invalidate()`.

Unmount cleanup uses `shrink_dcache_for_umount()` to detach the superblock root and secondary roots, waits on in-progress kills when necessary, warns on busy dentries, drops roots, and releases references.

## Mountpoint And Invalidation Behavior

`path_has_submounts()` walks a subtree and asks mount code whether mounted dentries are mountpoints in the current namespace.

`d_set_mounted()` marks `DCACHE_MOUNTED` only if the dentry and ancestors are still reachable, excluding races with `d_invalidate()`.

`d_invalidate()` unhashes a dentry, prunes children, repeatedly detaches submounts found under it, and re-prunes after detach. Negative dentries can be dropped immediately after unhash.

## Rename, Splicing, Aliases, And Temporary Files

`__d_move()` implements rename/exchange mechanics under `rename_lock`: it locks affected parents and dentries, unhashes participants, swaps or copies names, updates parent/child lists, rehashes, updates fsnotify flags, and calls `fscrypt_handle_d_move()`.

Public wrappers include `d_move()`, `d_exchange()`, `is_subdir()`, and `d_ancestor()`.

Alias helpers include `d_find_any_alias()`, `d_find_alias()`, `d_find_alias_rcu()`, `d_splice_alias_ops()`, `d_splice_alias()`, and `d_add_ci()`.

Temporary-file helpers `d_mark_tmpfile()`, `d_mark_tmpfile_name()`, and `d_tmpfile()` give unlinked temporary dentries display names and instantiate them.

## Initialization

`dcache_init_early()` optionally allocates the global hash table early. `dcache_init()` creates the dentry slab cache and allocates the hash table when hash distribution requires vmalloc availability.

`vfs_caches_init_early()` initializes in-lookup hash buckets plus dcache/inode early state. `vfs_caches_init()` initializes filename, dcache, inode, file, mount, block-device, and character-device caches.

## Key Invariants

- Dentry state observed locklessly is validated with `d_seq`, `rename_lock`, RCU, or explicit locks before use.
- Positive dentries own inode lifetime until detached.
- NORCU dentries have stricter lifetime assumptions because freeing is immediate.
- In-progress lookup dentries are visible only through `in_lookup_hashtable` until completed.
- Dentry tree walks avoid recursion and tolerate concurrent rename by retrying through `rename_lock`.
- Persistent dentries are explicitly pinned and must be made discardable before ordinary final release.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/debugfs/Makefile -->
# File Research: sources/os/linux/linux/fs/debugfs/Makefile

Builds the debugfs filesystem object when `CONFIG_DEBUG_FS` is enabled.

Composition:

- `debugfs-objs := inode.o file.o`
- `obj-$(CONFIG_DEBUG_FS) += debugfs.o`

`inode.o` provides the filesystem, mount, inode, creation, removal, and rename logic. `file.o` provides debugfs file-operation proxies and typed helper files.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/debugfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/debugfs/file.c -->
# File Research: sources/os/linux/linux/fs/debugfs/file.c

## Purpose

`fs/debugfs/file.c` implements debugfs file-operation proxying, file-removal lifetime protection, cancellation support, lockdown checks, and the many exported helpers for simple typed debugfs files.

The file is split into two broad areas: a safety wrapper around arbitrary debugfs file operations, and convenience creators/readers/writers for scalar values, strings, blobs, u32 arrays, register sets, and device-managed seqfiles.

## File Lifetime Protection

`debugfs_file_get()` and `debugfs_file_put()` guard active access to a debugfs regular file. They use per-dentry `struct debugfs_fsdata`, stored in `dentry->d_fsdata`, with active-user refcount, drain completion, cancellation list/mutex, and cached method bits.

`__debugfs_file_get()` lazily allocates `debugfs_fsdata`, records whether the file uses full `file_operations` or `debugfs_short_fops`, rejects non-regular dentries, detects removed dentries with `d_unlinked()`, and increments `active_users` only if the file is still alive.

`debugfs_enter_cancellation()` and `debugfs_leave_cancellation()` let long-running debugfs handlers register stack-owned cancellation objects. Removal can call each cancellation callback and then wait for `debugfs_file_put()`.

## Proxies And Lockdown

`debugfs_locked_down()` permits access during kernel lockdown only for world-readable, read-only files with no ioctl/mmap-style mutation path. Otherwise it calls `security_locked_down(LOCKDOWN_DEBUGFS)`.

Proxy fops:

- `debugfs_noop_file_operations`: simple empty read and count-consuming write.
- `debugfs_open_proxy_file_operations`: protects only open, then replaces the file fops with the real fops.
- `debugfs_full_proxy_file_operations`: protects open, read, write, llseek, poll, ioctl, and release against removal.
- `debugfs_full_short_proxy_file_operations`: same idea for `debugfs_short_fops` with read/write/llseek only.

Full proxy methods call `debugfs_file_get()`, dispatch only if the cached method bit exists, then call `debugfs_file_put()`. Release deliberately calls the real release unconditionally to avoid leaking resources, even if removal has already happened.

## Attribute Helpers

`debugfs_attr_read()`, `debugfs_attr_write()`, and `debugfs_attr_write_signed()` wrap `simple_attr_*` helpers with debugfs lifetime protection.

`debugfs_create_mode_unsafe()` chooses read/write, read-only, or write-only fops from the requested mode.

Typed scalar creators include decimal unsigned helpers, hex unsigned helpers, `debugfs_create_atomic_t()`, and `debugfs_create_bool()`. Each scalar helper uses simple get/set callbacks and `DEFINE_DEBUGFS_ATTRIBUTE` variants, producing mode-dependent fops.

## String, Blob, Arrays, Registers, And Device Seqfiles

String support:

- `debugfs_read_file_str()` copies the current string into a temporary buffer, appends newline, and reads it to userspace.
- `debugfs_write_file_str()` allows strict append or replace-at-zero style writes, caps at one page, trims whitespace, swaps the pointer with RCU assignment, waits for readers with `synchronize_rcu()`, and frees the old string.
- `debugfs_create_str()` validates the pointer and creates the file.

Blob support:

- `debugfs_create_blob()` exposes a `struct debugfs_blob_wrapper` through read/write helpers backed by simple buffer copy helpers.

Array support:

- `debugfs_create_u32_array()` formats a fixed-size u32 array once at open, stores the generated buffer in `file->private_data`, and frees it at release. It is read-only and nonseekable.

Register-set support under `CONFIG_HAS_IOMEM`:

- `debugfs_print_regs32()` prints register names and 32-bit MMIO values into a seq_file.
- `debugfs_create_regset32()` exposes a `debugfs_regset32` through a seq_file, wrapping output with runtime PM get/put when a device is provided.

Device-managed seqfile support:

- `debugfs_create_devm_seqfile()` allocates a devres-managed entry and creates a seq_file whose show callback receives the device pointer.

## Key Invariants

- Debugfs users that rely on protected fops can safely access private data between successful `debugfs_file_get()` and `debugfs_file_put()`.
- Removal may wait for active users and may invoke cancellation callbacks, so long-running handlers can be unwound.
- Short fops are limited to read/write/llseek and avoid full `struct file_operations` overhead.
- Full proxies retain module owners with `fops_get()` and warn when debugfs users fail to remove files before module exit.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/debugfs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/debugfs/inode.c -->
# File Research: sources/os/linux/linux/fs/debugfs/inode.c

## Purpose

`fs/debugfs/inode.c` implements the debugfs filesystem itself: mount option parsing, superblock setup, inode allocation, file/directory/symlink/automount creation, recursive removal, lookup, rename, initialization, and global enable/disable policy.

Debugfs is intentionally a debugging interface rather than a stable ABI. This file still enforces VFS lifetime rules, lockdown restrictions, and removal synchronization with `file.c`.

## Global State And Mount Options

Global state includes `debugfs_mount`, `debugfs_mount_count`, `debugfs_registered`, `debugfs_enabled`, and `debugfs_inode_cachep`.

Mount options in `struct debugfs_fs_info` store root uid, root gid, root mode, and a bitmask of explicitly provided options.

`debugfs_parse_param()` accepts `uid`, `gid`, `mode`, and `source`, while preserving historical behavior of ignoring unknown options. `debugfs_reconfigure()` applies remount options after `sync_filesystem()`. `debugfs_show_options()` prints non-default options.

`debugfs_setattr()` blocks chmod/chown/chgrp while lockdown forbids debugfs mutation because file mode is part of `file.c` lockdown heuristics.

## Superblock And Inodes

`debugfs_fill_super()` builds a simple single-instance filesystem with `DEBUGFS_MAGIC`, installs `debugfs_super_operations`, applies default dentry ops, sets `DCACHE_DONTCACHE`, and applies mount options.

`debugfs_inode_info` extends `struct inode` with a union of real fops, short fops, raw pointer, or automount callback plus an auxiliary pointer. Allocation and free are implemented by `debugfs_alloc_inode()` and `debugfs_free_inode()`.

`debugfs_release_dentry()` frees per-dentry `debugfs_fsdata` and verifies cancellation lists are empty. `debugfs_automount()` calls the stored automount callback.

## Creation Flow

All creators begin with `debugfs_start_creating()`: it rejects creation when debugfs is disabled or uninitialized, propagates error-valued parents, pins the debugfs filesystem, defaults a missing parent to the debugfs root, and calls `simple_start_creating()`.

File creation is centralized in `__debugfs_create_file()`. It defaults mode to regular file, allocates a debugfs inode, stores `i_private`, installs file inode operations and proxy fops, records raw fops/short fops and aux data in `DEBUGFS_I(inode)`, creates a persistent dentry with `d_make_persistent()`, and emits `fsnotify_create()`.

Public file creators include `debugfs_create_file_full()`, `debugfs_create_file_short()`, `debugfs_create_file_unsafe()`, and `debugfs_create_file_size()`.

Other creators include `debugfs_create_dir()`, `debugfs_create_automount()`, and `debugfs_create_symlink()`.

## Lookup, Removal, Rename, And Initialization

`debugfs_lookup()` returns a referenced positive dentry under a parent or the debugfs root, returning `NULL` for missing/error cases.

Removal:

- `debugfs_remove()` pins the filesystem, calls `simple_recursive_removal()`, and releases the pin.
- `remove_one()` calls `__debugfs_file_removed()` for regular files, then releases the creation-time filesystem pin.
- `__debugfs_file_removed()` pairs with `debugfs_file_get()` memory ordering, drops the active user reference, invokes cancellation callbacks as needed, and waits for active users to drain.
- `debugfs_lookup_and_remove()` combines lookup, remove, and `dput()`.

Rename:

- `debugfs_change_name()` formats a target name, looks up the target, locks rename state through `start_renaming_two_dentries()`, updates timestamps, calls `d_move()`, emits `fsnotify_move()`, and releases a safe old-name snapshot.

Initialization:

- `debugfs_kernel()` parses early `debugfs=on`, `debugfs=off`, and deprecated `debugfs=no-mount`.
- `debugfs_init()` creates `/sys/kernel/debug`, creates the inode cache, registers the filesystem, and marks debugfs registered. It runs as a `core_initcall`.

## Key Invariants

- Most debugfs creators tolerate error-valued parents so callers can ignore setup failures.
- Created debugfs dentries are persistent and require explicit `debugfs_remove()`.
- File removal is synchronized with active file operations through `debugfs_fsdata` from `file.c`.
- Lockdown affects both metadata changes and file-operation access policy.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/debugfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/debugfs/internal.h -->
# File Research: sources/os/linux/linux/fs/debugfs/internal.h

Private header shared by debugfs inode and file code.

Defines:

- `struct debugfs_inode_info`: embeds `struct inode` and stores the raw object associated with a debugfs inode: full fops, short fops, automount callback, or generic raw pointer, plus `aux`.
- `DEBUGFS_I()`: container helper from VFS inode to debugfs inode info.
- Exported internal fops declarations for noop, open proxy, full proxy, and short full proxy implementations.
- `struct debugfs_fsdata`: per-dentry file lifetime state with real/short fops, active-user refcount, completion for draining users, cancellation mutex/list, and cached method bits.
- Method bit constants `HAS_READ`, `HAS_WRITE`, `HAS_LSEEK`, `HAS_POLL`, and `HAS_IOCTL`.

This header captures the private contract between debugfs file creation/removal in `inode.c` and protected file operation dispatch in `file.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/debugfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/devpts/Makefile -->
# File Research: sources/os/linux/linux/fs/devpts/Makefile

Builds the Unix98 PTY devpts filesystem.

Composition:

- `obj-$(CONFIG_UNIX98_PTYS) += devpts.o`
- `devpts-$(CONFIG_UNIX98_PTYS) := inode.o`

All devpts filesystem logic in this group lives in `inode.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/devpts/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/devpts/inode.c -->
# File Research: sources/os/linux/linux/fs/devpts/inode.c

## Purpose

`fs/devpts/inode.c` implements the `/dev/pts` virtual filesystem used for Unix98 pseudo-terminal slave nodes and per-instance `ptmx` handling.

It owns devpts mount options, pty allocation limits, filesystem instance state, `ptmx` node creation, PTY slave dentry creation/removal, and helper functions used by the TTY layer to acquire the correct devpts instance.

## Global Limits And Mount Options

Global sysctls under `kernel/pty`:

- `max`: global maximum Unix98 PTYs.
- `reserve`: reserved PTYs for init mount namespace users.
- `nr`: current allocated PTY count.

`struct pts_mount_opts` stores uid/gid override flags and values, slave node mode, `ptmx` mode, reserve behavior, and per-instance max index.

Parsed mount options are `uid`, `gid`, `mode`, `ptmxmode`, `newinstance`, and `max`.

## Filesystem Instance State

`struct pts_fs_info` contains the per-instance IDA of allocated PTY indexes, mount options, owning superblock pointer, and borrowed `ptmx_inode` pointer.

`devpts_init_fs_context()` allocates this state, initializes defaults, and marks the instance as reserve-eligible when mounted from the initial mount namespace.

The filesystem type is user-namespace mountable (`FS_USERNS_MOUNT`) and uses `get_tree_nodev()`.

## Mount And Superblock Setup

`devpts_fill_super()` clears internal nodev flag so device nodes can exist, sets block size, magic, operations, `DCACHE_DONTCACHE`, and timestamp granularity, creates the root directory inode and dentry, and creates the `ptmx` character device node through `mknod_ptmx()`.

`mknod_ptmx()` creates a persistent `ptmx` dentry under the devpts root, inode number 2, device `TTYAUX_MAJOR:2`, current fs uid/gid, and mount-option-controlled mode.

`devpts_reconfigure()` applies updated mount options, intentionally preserves `reserve`, and updates the live `ptmx` inode mode.

`devpts_kill_sb()` destroys the per-instance IDA, frees `pts_fs_info`, and kills the anonymous superblock.

## Finding The Correct Devpts Instance

`devpts_ptmx_path()` validates that a path resolves to the root of a devpts filesystem, using `path_pts()` to find a sibling `pts` mount when needed.

`devpts_mntget()` supports both direct `/dev/pts/ptmx` opens and bind/symlink-style `/dev/ptmx` setups. It walks upward through bind mounts of single files, finds a matching devpts filesystem, verifies it matches the requested `pts_fs_info`, and returns a referenced mount.

`devpts_acquire()` obtains the `pts_fs_info` from a file path, resolving from ptmx to devpts if necessary, and takes an active superblock reference so pty code can survive last-close races. `devpts_release()` drops that active reference with `deactivate_super()`.

## PTY Index And Slave Node Lifecycle

`devpts_new_index()` increments global `pty_count`, enforces the global reserve policy, and allocates an IDA index up to the per-instance maximum. On failure it decrements the global count.

`devpts_kill_index()` frees the per-instance IDA index and decrements the global count.

`devpts_pty_new()` creates a new persistent slave node with inode number `index + 3`, mount-option or current fs credentials, device number `UNIX98_PTY_SLAVE_MAJOR:index`, decimal index name, private data in `dentry->d_fsdata`, and a create notification. The returned dentry is borrowed; the function drops its local reference after making it persistent.

`devpts_get_priv()` returns the stored private pointer for devpts dentries only.

`devpts_pty_kill()` clears private data, drops link count, unhashes the dentry, emits unlink notification, and calls `d_make_discardable()` to release the persistent dentry pin.

## Key Invariants

- PTY indexes are scoped per devpts instance, but `pty_count` and reserve policy are global.
- Slave and `ptmx` dentries are persistent while live and must be explicitly discarded.
- `devpts_acquire()` returns state protected by an active superblock reference.
- `ptmx` path resolution supports common container and bind-mount layouts while rejecting unrelated devpts instances.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/devpts/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/direct-io.c -->
# File Research: sources/os/linux/linux/fs/direct-io.c

## Purpose

`fs/direct-io.c` implements the legacy `__blockdev_direct_IO()` helper for block-mapped filesystems and block devices. It turns an `iov_iter` plus a filesystem `get_block` callback into bios, handles holes and sub-block alignment, supports synchronous and asynchronous I/O, and coordinates completion with inode direct-I/O exclusion.

This is the older buffer-head/get_block direct-I/O path, distinct from newer iomap direct I/O.

## Main Data Structures

`struct dio_submit` is submission-path state: current bio, block size, `blkfactor`, current file block, mapped block availability, boundary flag, `get_block` callback, deferred page segment, and iterator page queue state.

`struct dio` is shared between submission and bio completion: flags, operation flags, inode, sampled i_size, end_io callback, private data, bio completion lock, errors, async/deferred state, dirty-page policy, refcount, completed bio list, waiting task, kiocb, byte result, and extracted page array or completion work item.

## Page Extraction And Pinning

`dio_refill_pages()` extracts up to `DIO_PAGES` pages from the iterator. If a write faults after blocks have already been mapped, it substitutes `ZERO_PAGE(0)` so newly allocated disk blocks can be consumed and stale data is not exposed.

`dio_get_page()` refills the page queue as needed. `dio_pin_page()` and `dio_unpin_page()` account for iterators that use pinned user pages. `dio_cleanup()` releases remaining queued page pins on error or short I/O.

## Bio Construction And Submission

`dio_bio_alloc()` creates a bio for the block device and first sector, chooses sync or async end_io, sets `BIO_PAGE_PINNED` when needed, and propagates write hints.

`dio_bio_add_page()` tries to add the current page segment to the bio, updates final block tracking, and pins pages on successful bio ownership.

`submit_page_section()` coalesces adjacent chunks within a page, flushes deferred page state when needed, accounts write bytes, and forces bio submission on filesystem boundary hints.

`dio_send_cur_page()` ensures logical and physical contiguity before adding a page segment to an existing bio; it avoids combining logically non-contiguous file regions even when physical blocks are adjacent.

`dio_bio_submit()` increments the shared refcount, pre-dirties async read pages when needed, stores the bio disk, submits the bio, and clears current bio state.

## Block Mapping, Holes, And Partial Blocks

`get_more_blocks()` calls the filesystem `get_block` method with filesystem-block offsets and remaining block count. It stores `b_private` for completion, honors `buffer_defer_completion()`, and implements `DIO_SKIP_HOLES` by forbidding block creation for writes inside existing i_size ranges.

`do_direct_IO()` walks extracted pages and file blocks, maps blocks as needed, and submits mapped regions. Reads from holes zero user pages until EOF; writes to holes return `-ENOTBLK` so the caller can fall back to buffered I/O; newly allocated blocks trigger `clean_bdev_aliases()`; partial filesystem-block writes may zero unused head/tail regions.

`dio_zero_block()` handles zeroing at the start or end of a newly allocated filesystem block when the direct I/O alignment is finer than filesystem block size.

## Completion

Synchronous completion queues bios into `dio->bio_list`, drains them with `dio_await_completion()`, then `dio_complete()` computes the final return value, calls filesystem `end_io`, invalidates page cache after successful direct writes, calls `inode_dio_end()`, and frees the dio.

Asynchronous completion uses `dio_bio_end_aio()`. The last bio either completes immediately or queues `dio_aio_complete_work()` on `s_dio_done_wq`. Deferred completion is required for O_DSYNC-style writes and for async writes needing post-I/O invalidation in task context.

`dio_bio_complete()` maps bio status to `dio->io_error`, releases pages, redirties async read pages when necessary, and drops bio references.

## `__blockdev_direct_IO()` Flow

The exported entry point validates count and alignment, allocates `struct dio`, applies optional `DIO_LOCKING`, samples i_size, flushes page cache for locking reads, chooses safe async/sync behavior, initializes direct-I/O accounting, runs `do_direct_IO()`, handles buffered fallback, submits remaining bios, releases page pins and read locks, waits unless a valid async request is queued, and completes or returns `-EIOCBQUEUED`.

## Key Invariants

- Filesystems using `DIO_LOCKING` rely on this helper for read-side `i_rwsem`; others must synchronize direct I/O and truncate themselves.
- `inode_dio_begin()`/`inode_dio_end()` bracket all successful submissions so truncate can wait for direct I/O.
- `-ENOTBLK` is an internal fallback signal for buffered writes, not a final error.
- Async completion is only reported through `ki_complete()` when the function returns `-EIOCBQUEUED`.
- Partial newly allocated filesystem blocks are zero-filled to avoid stale data exposure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/direct-io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/Kconfig -->
# File Research: sources/os/linux/linux/fs/dlm/Kconfig

Defines kernel configuration for the Distributed Lock Manager.

Options:

- `DLM`: tristate "Distributed Lock Manager (DLM)", depends on `INET`, `SYSFS`, and `CONFIGFS_FS`. It provides a general-purpose distributed lock manager for kernel or userspace applications.
- `DLM_DEBUG`: bool "DLM debugging", depends on `DLM`. It exposes each lockspace as a debugfs file under the `dlm` directory, showing local resources and locks.

The configfs dependency matches the DLM runtime configuration implementation in `config.c`; the debug option adds `debug_fs.o` in the Makefile.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/Makefile -->
# File Research: sources/os/linux/linux/fs/dlm/Makefile

Builds the DLM module/object when `CONFIG_DLM` is enabled.

Core object list:

- `ast.o`
- `config.o`
- `dir.o`
- `lock.o`
- `lockspace.o`
- `main.o`
- `member.o`
- `memory.o`
- `midcomms.o`
- `lowcomms.o`
- `plock.o`
- `rcom.o`
- `recover.o`
- `recoverd.o`
- `requestqueue.o`
- `user.o`
- `util.o`

Conditional object:

- `debug_fs.o` when `CONFIG_DLM_DEBUG` is enabled.

This group covers the callback path (`ast.o`) and configfs configuration path (`config.o`); the remaining listed objects implement lockspace, membership, recovery, communication, user API, and debugging support.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/ast.c -->
# File Research: sources/os/linux/linux/fs/dlm/ast.c

## Purpose

`fs/dlm/ast.c` handles DLM application callbacks: completion ASTs (`DLM_CB_CAST`), blocking ASTs (`DLM_CB_BAST`), callback allocation/population, suppression of redundant callbacks, immediate versus workqueue dispatch, and suspend/resume of callback delivery during lockspace transitions.

## Callback Execution

`dlm_run_callback()` dispatches by callback flag:

- BAST: traces `trace_dlm_bast()` and calls `bastfn(astparam, mode)`.
- CAST: traces `trace_dlm_ast()`, writes status and flags into the lock status block, then calls `astfn(astparam)`.

`dlm_do_callback()` runs a prepared callback and frees it. `dlm_callback_work()` is the ordered-workqueue entry point.

## Skipping And LVB Copy Decisions

`dlm_may_skip_callback()` updates per-lockblock callback history and may suppress redundant callbacks.

For BAST, it skips compatible or redundant blocking callbacks and records last BAST time/mode. For CAST, user lockblocks may request LVB copy based on the LVB operation table, and last CAST mode/time are recorded.

Both paths update `lkb_last_cb_mode` and `lkb_last_cb_flags`.

## Allocation And Queuing

`dlm_get_cb()` allocates a `struct dlm_callback`, copies tracing metadata such as lockspace ID, lockblock ID, resource name, flags, mode, status, status-block flags, and the lock status block pointer.

`dlm_get_queue_cb()` additionally copies kernel callback function pointers and `astparam`, then initializes work.

`dlm_add_cb()` is the public enqueue/dispatch function: user lockblocks are forwarded to `dlm_user_add_ast()`, redundant kernel callbacks are skipped, and under `ls_cb_lock`, callbacks are either delayed, run immediately in softirq mode, or queued to the lockspace callback workqueue.

## Workqueue Lifecycle And Delay Handling

`dlm_callback_start()` creates a high-priority reclaim-safe ordered workqueue named `dlm_callback` for filesystem lockspaces unless softirq delivery is used.

`dlm_callback_stop()` destroys the workqueue when present.

`dlm_callback_suspend()` sets `LSFL_CB_DELAY` and flushes the workqueue so new callbacks are retained on `ls_cb_delay`.

`dlm_callback_resume()` drains delayed callbacks in batches of `MAX_CB_QUEUE`, either running them immediately in softirq mode or queueing work. It clears `LSFL_CB_DELAY` once the delay list is empty and logs the number resumed.

## Key Invariants

- User lockblocks use the user-AST path rather than kernel function callbacks.
- Delayed callbacks are protected by `ls_cb_lock` and drained in bounded batches to allow rescheduling.
- Filesystem lockspaces get ordered callback delivery unless configured for softirq callbacks.
- CAST callbacks update the caller-visible lock status block before invoking the AST function.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/ast.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/ast.h -->
# File Research: sources/os/linux/linux/fs/dlm/ast.h

Private DLM callback header.

Declares:

- `dlm_may_skip_callback()` for callback suppression and optional LVB-copy decision.
- `dlm_get_cb()` for allocating/populating a callback object.
- `dlm_add_cb()` for adding or dispatching CAST/BAST callbacks.
- Callback workqueue lifecycle: `dlm_callback_start()`, `dlm_callback_stop()`, `dlm_callback_suspend()`, and `dlm_callback_resume()`.

The header is the internal contract between DLM lock-management code and `ast.c` callback delivery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/ast.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/config.c -->
# File Research: sources/os/linux/linux/fs/dlm/config.c

## Purpose

`fs/dlm/config.c` implements DLM runtime configuration through configfs. It creates the `/config/dlm/<cluster>/spaces/...` and `/config/dlm/<cluster>/comms/...` hierarchy, manages cluster-wide tunables, communication endpoints, lockspace members, removed-member reporting, and provides query helpers used by the DLM core.

## Configfs Topology

The file implements this hierarchy:

- `/config/dlm/<cluster>/`
- `/config/dlm/<cluster>/spaces/<space>/nodes/<node>/`
- `/config/dlm/<cluster>/comms/<comm>/`

The cluster level stores global DLM config. Each lockspace has a `nodes` group. Each comm item represents a configured node endpoint.

Global pointers are `space_list`, `comm_list`, `local_comm`, and `dlm_comm_count`.

## Cluster Attributes And Validation

Cluster attributes map to global `dlm_config` fields: `cluster_name`, `tcp_port`, `buffer_size`, `rsbtbl_size`, `recover_timer`, `toss_secs`, `scan_secs`, `log_debug`, `log_info`, `protocol`, `mark`, `new_rsb_count`, and `recover_callbacks`.

Stores require `CAP_SYS_ADMIN` for numeric cluster tunables. `tcp_port` and `protocol` cannot be changed while lowcomms is running. Zero-valued fields are rejected where nonsensical. SCTP protocol is rejected when `CONFIG_IP_SCTP` is unavailable. `buffer_size` must be at least `DLM_MAX_SOCKET_BUFSIZE`.

`dlm_rhash_rsb_params` defines the resource-name rhashtable layout for DLM resource blocks, with automatic shrinking and a small initial hint.

## Configfs Object Types

Object wrappers:

- `dlm_cluster`: cluster group with default `spaces` and `comms` groups.
- `dlm_space`: lockspace group with member lists, removed-member list, counts, lock, and default `nodes` group.
- `dlm_comm`: comm item with sequence, nodeid, local flag, address list, and mark.
- `dlm_node`: lockspace member item with nodeid, weight, new flag, comm sequence snapshot, and release-recover value.
- `dlm_member_gone`: delayed removed-member report.

`make_cluster()` allocates a cluster plus default groups and stores global `space_list`/`comm_list`. `drop_cluster()` removes default groups and clears those globals.

`make_space()` allocates a space plus default `nodes` group and initializes member state.

`make_comm()` parses the configfs item name as nodeid, allocates a comm item, assigns a nonzero sequence number, and initializes defaults. `drop_comm()` clears `local_comm` if needed, closes midcomms for the node, frees addresses, and drops the item reference.

`make_node()` parses nodeid, allocates a node, records the current comm sequence, and appends it to the space member list. `drop_node()` removes the node and records a `dlm_member_gone` entry because configfs rmdir cannot pass extra release attributes directly to DLM recovery.

## Comm Attributes

Comm attributes:

- `nodeid`: derived from config item name.
- `local`: marks this comm as the local node when set.
- `addr`: write-only binary `sockaddr_storage`, validated by `dlm_midcomms_addr()`, up to `DLM_MAX_ADDR_COUNT`.
- `addr_list`: read-only formatted list of IPv4/IPv6 addresses.
- `mark`: sets a per-node lowcomms mark, using global default when written as zero.

`drop_comm()` calls `dlm_midcomms_close()` for the node and frees all stored addresses.

## Node Attributes

Node attributes are `nodeid`, `weight`, and `release_recover`. Node membership is protected by each space's `members_lock`.

## DLM Query Helpers

`dlm_config_nodes()` returns a newly allocated array of `struct dlm_config_node` for a lockspace. It includes current members, clears each member's `new` flag after reporting, appends delayed gone members with `gone=true` and `release_recover`, consumes and frees `members_gone` records, and returns standard errors for missing space, zero members, or allocation failure.

`dlm_comm_seq()` finds a comm by nodeid and returns its sequence, optionally assuming the configfs subsystem mutex is already held.

`dlm_our_nodeid()` returns `local_comm->nodeid`.

`dlm_our_addr()` copies the requested local address by index and returns `-1` if no local comm or address exists.

## Defaults And Initialization

`dlm_config` defaults include TCP port 21064, socket buffer size `DLM_MAX_SOCKET_BUFSIZE`, resource table size 1024, recover timer 5, toss secs 10, scan secs 5, info logging enabled, TCP protocol, mark 0, new RSB count 128, recover callbacks disabled, and empty cluster name.

`dlm_config_init()` initializes the root configfs subsystem named `dlm` and registers it. `dlm_config_exit()` unregisters it.

## Key Invariants

- Only one active cluster's `spaces` and `comms` groups are tracked by the global pointers.
- Communication sequence numbers let lockspace membership detect comm reconfiguration for a node.
- Removed nodes are reported lazily through `dlm_config_nodes()` to carry `release_recover`.
- Address writes are binary `sockaddr_storage` records, not text.
- Low-level communication settings that affect sockets are blocked while lowcomms is running.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/dlm/config.h -->
# File Research: sources/os/linux/linux/fs/dlm/config.h

Private DLM configuration header shared by config and core DLM code.

Defines:

- `DLM_MAX_SOCKET_BUFSIZE` as 4096.
- `struct dlm_config_node`: nodeid, weight, gone/new flags, communication sequence, and release-recover value.
- `dlm_rhash_rsb_params`: external rhashtable parameters for DLM resource blocks.
- `DLM_MAX_ADDR_COUNT` as 8.
- Protocol constants `DLM_PROTO_TCP` and `DLM_PROTO_SCTP`.
- `struct dlm_config_info`: global tunables including TCP port, buffer size, resource table size, timers, logging, protocol, mark, new RSB count, recover callbacks, and cluster name.

Declares:

- global `dlm_config`;
- configfs lifecycle `dlm_config_init()` and `dlm_config_exit()`;
- membership query `dlm_config_nodes()`;
- comm sequence lookup `dlm_comm_seq()`;
- local identity/address helpers `dlm_our_nodeid()` and `dlm_our_addr()`.

This header is the internal interface by which DLM subsystems consume configfs-derived cluster, node, and communication state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/dlm/config.h -->