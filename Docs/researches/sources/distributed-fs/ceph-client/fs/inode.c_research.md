<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/inode.c -->
# sources/distributed-fs/ceph-client/fs/inode.c

## Purpose

`sources/distributed-fs/ceph-client/fs/inode.c` is the VFS inode cache and inode lifecycle implementation. It allocates and initializes inodes, maintains global inode hash and per-superblock inode/LRU lists, implements lookup and insertion APIs, handles final `iput()` and eviction, exports link-count and ownership helpers, supports timestamp updates including multigrain timestamps, provides write-path privilege and time updates, initializes inode caches/hash tables, and supplies diagnostic helpers.

## Important APIs, Types, and Functions

Core exported lifecycle APIs include `inode_init_always_gfp()`, `alloc_inode()`, `new_inode()`, `inode_init_once()`, `address_space_init_once()`, `__destroy_inode()`, `clear_inode()`, `evict_inodes()`, `prune_icache_sb()`, `ihold()`, `iput()`, `iput_not_last()`, `unlock_new_inode()`, and `discard_new_inode()`.

Lookup and hash APIs include `__insert_inode_hash()`, `__remove_inode_hash()`, `inode_insert5()`, `iget5_locked()`, `iget5_locked_rcu()`, `iget_locked()`, `ilookup5_nowait()`, `ilookup5()`, `ilookup()`, `find_inode_nowait()`, `find_inode_rcu()`, `find_inode_by_ino_rcu()`, `insert_inode_locked()`, `insert_inode_locked4()`, `iunique()`, and `get_next_ino()`.

Metadata helpers include `drop_nlink()`, `clear_nlink()`, `set_nlink()`, `inc_nlink()`, `init_special_inode()`, `inode_init_owner()`, `inode_owner_or_capable()`, `in_group_or_capable()`, `mode_strip_sgid()`, `inode_set_flags()`, `inode_nohighmem()`, `inode_needs_sync()`, `bmap()`, `inode_dio_wait()`, and `inode_dio_wait_interruptible()`.

Time and write-path helpers include `current_time()`, `timestamp_truncate()`, `inode_set_ctime_to_ts()`, `inode_set_ctime_current()`, `inode_set_ctime_deleg()`, `inode_update_time()`, `generic_update_time()`, `atime_needs_update()`, `touch_atime()`, `dentry_needs_remove_privs()`, `file_remove_privs()`, `file_update_time()`, `file_modified()`, and `kiocb_modified()`.

Global state includes `inode_hashtable`, `inode_hash_lock`, per-cpu `nr_inodes` and `nr_unused`, the inode slab cache, multigrain timestamp debug counters, and inode sysctl state.

## Control Flow

Inode allocation flows through filesystem-specific `s_op->alloc_inode()` or the generic slab, then `inode_init_always_gfp()` initializes the inode, address_space, locks, counters, uid/gid/mode defaults, xattr/mgtime opflags, security blob, and writeback-related fields. `new_inode()` additionally links the inode onto the superblock inode list.

Cache lookup uses a global hash derived from superblock and inode/hash value. `iget_locked()` and `iget5_locked()` look for a matching inode under RCU and spinlocks, wait for `I_NEW` to clear when necessary, retry if an inode was unhashed during the race, or allocate/insert a new `I_NEW` inode for the filesystem to fill. `insert_inode_locked()` handles callers that already own an initialized inode and returns `-EBUSY` if a live duplicate exists.

Reference release runs through `iput()`. If the count does not reach zero it returns quickly. On the final put, it syncs lazytime when needed, calls filesystem `drop_inode()` or the generic drop policy, either queues the inode on the superblock LRU for reuse or marks it `I_WILL_FREE`/`I_FREEING`, waits for writeback, calls filesystem `evict_inode()` or truncates pages and clears the inode, removes hash/list state, wakes waiters, and frees the inode through RCU and filesystem slab callbacks.

Shrinking and unmount flow through `prune_icache_sb()` and `evict_inodes()`. The LRU isolate path skips referenced or unreclaimable inodes, may invalidate page cache for shrinkable mappings, marks selected inodes `I_FREEING`, and disposes them outside the LRU lock. Unmount removes all zero-reference inodes after `SB_ACTIVE` is cleared.

Write-path metadata flow starts with `file_modified()` or `kiocb_modified()`, which remove suid/sgid/security privileges if needed and then update ctime/mtime/i_version through filesystem `update_time` or `generic_update_time()`. Atime flow is separate: `touch_atime()` checks noatime/nodiratime/relatime, readonly/write access, unmapped IDs, and then updates atime best-effort.

## State and Persistence Behavior

The file maintains in-memory VFS inode state and schedules persistence indirectly by dirtying inodes. It does not write filesystem-specific on-disk metadata itself except through generic dirtying, writeback waits, and filesystem callbacks.

Important state transitions are encoded in `i_state`: `I_NEW`, `I_CREATING`, dirty flags, `I_SYNC`, `I_REFERENCED`, `I_LRU_ISOLATING`, `I_WILL_FREE`, `I_FREEING`, and `I_CLEAR`. List membership spans the global hash, per-superblock inode list, per-superblock LRU, and writeback lists. Counters track total and unused inodes per CPU and removal counts per superblock when link count reaches zero.

Timestamps are stored in inode fields and truncated to superblock granularity. Multigrain timestamp mode uses `I_CTIME_QUERIED` in `i_ctime_nsec`, coarse/fine clock selection, compare-exchange updates, and debug counters to provide finer ctime when timestamp values have been observed.

## Dependencies and Integration Points

This file is central to VFS, MM, writeback, fsnotify, security, fsverity, POSIX ACLs, device nodes, block mapping, mount idmaps, cgroups writeback, debugfs, sysctl, and tracepoints. Filesystems depend on these exported helpers to allocate, publish, lookup, lock, evict, and dirty their inodes.

It also integrates with reclaim via `list_lru`, with direct I/O via `i_dio_count`, with writeback via inode writeback lists and `inode_wait_for_writeback()`, with LSM via `security_inode_alloc/free()` and privilege removal hooks, and with idmapped mounts for ownership and permission helpers.

## Risks and Edge Cases

Lock ordering is the main correctness risk. The file documents ordering among `s_inode_list_lock`, `i_lock`, inode LRU locks, writeback locks, `inode_hash_lock`, and `iunique_lock`. Lookup paths must not return inodes being freed, must wait without deadlocking when `I_FREEING` races are observed, and must not sleep in callbacks that run under `inode_hash_lock`.

Final `iput()` is sensitive because filesystem `drop_inode()`, lazytime sync, writeback wait, page-cache truncation, hash removal, wakeups, and RCU freeing all interleave with concurrent lookup and reclaim. Link-count helpers update `s_remove_count`; direct manipulation of `i_nlink` by filesystems can break unmount accounting.

Timestamp paths must handle NOWAIT semantics, lazytime, i_version increments, time granularity clamping, idmapped/mapped-ID checks, and multigrain races. Write-path privilege removal can block and therefore returns `-EAGAIN` for NOWAIT callers.

## Test Signals

Useful coverage includes iget/ilookup races with concurrent eviction, duplicate insertion returning `-EBUSY`, `I_NEW` wait/wakeup behavior, final `iput()` under dirty/lazytime inodes, superblock unmount eviction, LRU shrinker behavior with page-cache-backed inodes, RCU lookup helpers, inode hash sizing via `ihash_entries=`, link-count remove-count accounting, special inode initialization for char/block/FIFO/socket, idmapped ownership initialization, suid/sgid/capability stripping on write, NOWAIT timestamp update failures, multigrain timestamp monotonicity, and direct-I/O wait behavior.

Runtime signals include `/proc/sys/fs/inode-nr`, `/proc/sys/fs/inode-state`, debugfs `multigrain_timestamps`, VFS warnings from `dump_inode()`/`dump_mapping()`, writeback tracepoints, and lockdep reports for inode lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/inode.c -->
