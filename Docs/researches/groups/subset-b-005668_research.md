# Research Group: subset-b-005668

This grouped report covers the GFS2 VFS, inode, glock, and glock-operation files listed in work item `subset-b-005668`. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/file.c -->
## sources/distributed-fs/ceph-client/fs/gfs2/file.c

### Purpose
`file.c` wires GFS2 regular-file and directory VFS operations to the cluster lock, quota, allocation, journaling, iomap, DLM POSIX lock, and DLM flock subsystems. It provides file operation tables for clustered-lock and local-lock mounts and implements the operational path for seek, readdir, mmap faults, open/release, fsync, buffered/direct reads and writes, fallocate, splice write sizing hints, ioctls, file attributes, POSIX locks, and flock locks.

### Important APIs, Types, and Functions
The exported or externally referenced entry points are `gfs2_fileattr_get`, `gfs2_fileattr_set`, `gfs2_set_inode_flags`, `gfs2_open_common`, `gfs2_file_fops`, `gfs2_dir_fops`, `gfs2_file_fops_nolock`, and `gfs2_dir_fops_nolock`. VFS callbacks include `gfs2_llseek`, `gfs2_readdir`, `gfs2_mmap`, `gfs2_open`, `gfs2_release`, `gfs2_fsync`, `gfs2_file_read_iter`, `gfs2_file_write_iter`, `gfs2_fallocate`, `gfs2_lock`, and `gfs2_flock`. The file-private state is `struct gfs2_file` from `incore.h`, primarily used to serialize and remember flock glock holders.

### Control Flow
Read-side operations acquire enough glock state to make cluster-visible inode metadata safe. `SEEK_END` takes the inode glock shared before reading file size, while `SEEK_DATA` and `SEEK_HOLE` delegate to inode helpers that use iomap under the glock. Directory iteration takes the directory glock shared and calls `gfs2_dir_read`. Buffered reads first attempt a no-I/O generic read with page faults disabled, then take the inode glock shared and retry with explicit user-page faulting windows. Direct reads take the inode glock in deferred mode to permit concurrent direct I/O.

Write-side flow is stricter. `gfs2_file_write_iter` records an allocation size hint, refreshes size for append writes, takes `inode_lock`, runs generic write checks and privilege stripping, then routes direct and buffered I/O. Direct writes take a deferred glock and fall back to buffered I/O for extending or page-fault-heavy writes; buffered writes take the inode glock exclusive, optionally lock statfs for rindex writes, and use iomap buffered write ops. `gfs2_page_mkwrite` is the mmap-write allocation path: it takes the inode glock exclusive, updates timestamps, reserves quota and resource-group space, starts a transaction, unstuffs inline data if needed, allocates backing blocks with `gfs2_iomap_alloc`, marks the folio dirty, and releases quota/reservation/glock state on all exits.

`gfs2_fallocate` takes `inode_lock` and an exclusive inode glock, validates mode and size growth, gets write access, and either punches holes externally via `__gfs2_punch_hole` or allocates chunks. Chunk allocation computes quota/rgrp-limited maximum byte ranges, starts transactions with dinode/statfs/quota/rgrp reservations, allocates iomap ranges, and zeroes new blocks with `sb_issue_zeroout`.

### State and Persistence Behavior
The file mutators persist inode flags, timestamps, block mappings, allocation bitmaps, quota changes, statfs changes, and dinode metadata through GFS2 transactions. `do_gfs2_set_flags` handles `FS_IOC_*FLAGS` translation, flushes and truncates data when toggling journaled-data mode, updates `ip->i_diskflags`, writes the dinode, and refreshes inode flags/address-space operations. `gfs2_fsync` writes data first, syncs inode metadata and journaled data as needed, flushes AIL buffers with `gfs2_ail_flush`, and waits on file data ranges. `gfs2_size_hint` updates `ip->i_sizehint` for lower allocation policy.

### Dependencies and Integration Points
This file sits between the Linux VFS/mm/iomap APIs and GFS2 subsystems: `glock.[ch]` for cluster locking, `glops.c` for AIL flush policy, `inode.c` for seek helpers and permission, `bmap`/`aops`/`iomap` for mapping, `rgrp` for allocation, `quota` for accounting, `trans`/`log` for journaling, and DLM `dlm_posix_*` for POSIX byte-range locks. It selects clustered vs local file operation tables through `CONFIG_GFS2_FS_LOCKING_DLM` and `gfs2_localflocks`.

### Risks and Edge Cases
The highest-risk code is around page faults while glocks are held; read/write/direct-I/O paths deliberately disable page faults, drop glocks, fault user pages, and retry. Bugs here can cause partial I/O surprises, deadlocks, or livelock. Fallocate chunk sizing must honor quota and rgrp reservations or it can over-reserve transactions. Flag changes around journaled-data mode require correct writeback, wait, page invalidation, and ordered-list removal. Cluster lock operations must treat withdrawn filesystems as I/O errors and must not sleep while holding `file->f_lock` during flock cleanup.

### Test Signals
Useful signals are xfstests for GFS2 buffered/direct I/O, mmap write faults, append writes from multiple nodes, fallocate and punch-hole behavior, fsync durability in ordered/writeback/jdata modes, fileattr flag transitions, FITRIM/FSLABEL ioctl handling, POSIX lock and flock interoperability through DLM, and fault-injection for user-page faults and allocation/quota failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/gfs2.h -->
## sources/distributed-fs/ceph-client/fs/gfs2/gfs2.h

### Purpose
`gfs2.h` is a small common header for simple cross-file constants used throughout the GFS2 implementation. It does not own complex behavior; it provides uniform boolean-like option values and a short-name threshold.

### Important APIs, Types, and Functions
The header defines two enum pairs: `NO_CREATE`/`CREATE` and `NO_FORCE`/`FORCE`. It also defines `GFS2_FAST_NAME_SIZE` as `8`. There are no functions and no stateful types.

### Control Flow
There is no runtime control flow. The constants shape call-site readability, especially calls that conditionally create glocks or force operations.

### State and Persistence Behavior
The file contains no persisted state. Its constants can influence whether other code creates in-core structures or performs forced operations, but persistence is implemented elsewhere.

### Dependencies and Integration Points
`file.c`, `glock.c`, `inode.c`, and related GFS2 sources include this header for common symbolic values. In this subset, `CREATE` is passed into `gfs2_glock_get` paths and contrasts with `NO_CREATE` for lookup-only behavior.

### Risks and Edge Cases
Because the enums are unscoped integer constants, misuse at call sites is possible if arguments are ordered poorly. The risk is low but real in C APIs that accept plain `int create` or force parameters.

### Test Signals
No direct tests target this header. Coverage comes indirectly from glock lookup/create paths, inode creation/lookup paths, and any code that depends on fast-name sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/gfs2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/glock.c -->
## sources/distributed-fs/ceph-client/fs/gfs2/glock.c

### Purpose
`glock.c` implements GFS2's in-core glock cache and state machine. Glocks are GFS2's cluster-visible lock objects over inodes, resource groups, metadata, iopen state, flock locks, quota, journals, and nondisk coordination locks. The file handles glock lookup/creation, reference lifetime, holder queues, state promotion and demotion, DLM callbacks, object attachment, inode-delete verification, LRU shrinking, withdrawal/unmount cleanup, debugfs dumping, and lock statistics.

### Important APIs, Types, and Functions
Key public APIs are `gfs2_glock_get`, `gfs2_glock_hold`, `gfs2_glock_put`, `gfs2_glock_put_async`, `gfs2_holder_init`/`__gfs2_holder_init`, `gfs2_holder_reinit`, `gfs2_holder_uninit`, `gfs2_glock_nq`, `gfs2_glock_wait`, `gfs2_glock_async_wait`, `gfs2_glock_dq`, `gfs2_glock_dq_wait`, `gfs2_glock_nq_num`, `gfs2_glock_nq_m`, `gfs2_glock_dq_m`, `gfs2_glock_cb`, `gfs2_glock_complete`, `glock_set_object`, `glock_clear_object`, delete-work helpers, withdraw/clear/thaw helpers, and debugfs registration functions. Static state includes the global `rhashtable gl_hash_table`, global `lru_list`, `lru_count`, `lru_lock`, and hashed wait queues for concurrent creation/removal races.

### Control Flow
`gfs2_glock_get` first looks up a glock by `struct lm_lockname`; if absent and creation is allowed, it allocates either a plain glock or `struct gfs2_glock_aspace`, allocates an LVB for glock types that need one, initializes state/holders/work, attaches an address space for `GLOF_ASPACE`, and races insertion through `find_insert_glock`. Refcount transitions use `lockref`, and the last reference either frees immediately when unlocked or moves the glock to the LRU until demoted/unlocked.

Acquisition is holder-queue driven. `gfs2_glock_nq` initializes wait state, adds the holder through `add_to_queue`, rejects invalid try-locks early, prevents recursive same-task locking except flock glocks, and calls `run_queue`. `run_queue` processes demote requests first, otherwise promotes compatible waiters with `do_promote`, or starts an external DLM conversion via `do_xmote`. Compatibility is centralized in `may_grant`: EX is exclusive unless both holders use node-scope EX, SH only shares with SH, DF only shares with DF, and `LM_FLAG_ANY` can accept an already-held compatible state.

DLM completion enters through `gfs2_glock_complete`, which may freeze replies during recovery, stores `gl_reply`, and queues `glock_work_func`. `finish_xmote` applies returned state, handles canceled/error/try-lock cases, retries failed conversions through unlock paths, calls `go_xmote_bh`, promotes waiters, and clears `GLF_LOCK`. Remote blocking callbacks enter through `gfs2_glock_cb`, set demote state, optionally delay inode demotes based on adaptive hold time, and queue work. Release through `gfs2_glock_dq` cancels pending lock requests when possible, removes holders, and schedules demotion work if needed.

### State and Persistence Behavior
Most state is in-core: `gl_state`, `gl_target`, `gl_demote_state`, flags, holders, LRU membership, AIL counts, LVB contents, object pointer, and stats. Persistence happens through glock operation hooks rather than this file directly: `do_xmote` calls `go_sync` before demoting/unlocking and `go_inval` when dropping to unlocked/deferred. During filesystem withdraw, `do_xmote` avoids new disk writes and invalidates cached data. Iopen glock LVB-like delete-generation state records `ri_generation_deleted` for stale inode detection.

### Dependencies and Integration Points
The glock engine depends on DLM lock operations from `lm_lockops`, operation policies from `glops.c`, inode helpers for iopen eviction verification, resource allocation cleanup through superblock workqueues, debugfs/seq_file for diagnostics, and Linux shrinker infrastructure for memory pressure. Almost every GFS2 metadata/data path in this subset calls into this file before touching cluster-visible state.

### Risks and Edge Cases
This file is concurrency-critical. Risks include lockref races during lookup/free, holder queue ordering regressions, missed wakeups on bit waits, recursive glock acquisition deadlocks, incorrect try-lock failure handling, DLM callback races with cancellation, frozen replies during recovery, demote delays that starve waiters, and unsafe freeing while debugfs iteration holds references. Withdrawal behavior is delicate because it must stop writes while still invalidating dirty caches. Multi-glock acquisition sorts by lock number but assumes no equal-number same-type duplicates.

### Test Signals
High-value signals include multi-node lock contention tests, DLM recovery and withdraw tests, stress of async multi-glock acquisition with retries, debugfs `glocks`/`glstats`/`glockfd` consistency, LRU shrinker under memory pressure, unmount waits for glock disposal, iopen delete races, and fault injection in `lm_lock`, `go_sync`, and `go_instantiate`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/glock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/glock.h -->
## sources/distributed-fs/ceph-client/fs/gfs2/glock.h

### Purpose
`glock.h` declares GFS2's lock-manager-facing constants, glock public API, holder lifecycle helpers, assertion/debug macros, and DLM lockops interface. It is the contract used by file, inode, glops, quota, rgrp, super, and recovery code to acquire cluster locks.

### Important APIs, Types, and Functions
The header defines lock name types (`LM_TYPE_INODE`, `LM_TYPE_RGRP`, `LM_TYPE_IOPEN`, etc.), lock states (`LM_ST_UNLOCKED`, `LM_ST_EXCLUSIVE`, `LM_ST_DEFERRED`, `LM_ST_SHARED`), request flags (`LM_FLAG_TRY`, `LM_FLAG_RECOVER`, `LM_FLAG_ANY`, `GL_ASYNC`, `GL_EXACT`, `GL_SKIP`, `GL_NOCACHE`, `GL_NOBLOCK`), DLM output flags, adaptive hold-time constants, `struct lm_lockops`, and `struct gfs2_glock_aspace`. Inline helpers include `gfs2_glock_is_locked_by_me`, `gfs2_glock2aspace`, `gfs2_glock_nq_init`, holder initialization checks, and `glock_needs_demote`.

### Control Flow
The most important inline flow is `gfs2_glock_nq_init`: initialize a holder with the calling instruction pointer, enqueue it with `gfs2_glock_nq`, and uninitialize on failure. Callers use this to enforce acquire/release symmetry. `gfs2_glock_is_locked_by_me` scans current holders under the glock spinlock and is used to avoid self-deadlock in permission, lookup, and getattr paths.

### State and Persistence Behavior
The header does not persist state itself but defines the symbolic state machine consumed by `glock.c` and operation hooks. Flags such as `GL_NOCACHE`, `GL_SKIP`, `LM_FLAG_RECOVER`, and `LM_FLAG_NODE_SCOPE` affect whether state is cached, whether instantiate hooks read disk, whether recovery can bypass blocked locks, and whether exclusive DLM ownership can be shared locally.

### Dependencies and Integration Points
It includes `incore.h` for core structures and exposes `gfs2_dlm_ops` for clustered lock integration. It is included by all major GFS2 subsystems that need glock acquisition, debug dumps, delete verification, or debugfs integration.

### Risks and Edge Cases
Because this header defines flag values and lock-state compatibility semantics, any change can affect the whole filesystem. Inline holder checks must remain consistent with `glock.c` holder list invariants. Misusing `GL_SKIP`, `GL_NOCACHE`, or `GL_NOBLOCK` can bypass instantiate, force unnecessary demotes, or produce surprising nonblocking errors.

### Test Signals
Coverage is indirect: all glock acquisition tests, recovery tests, DLM integration tests, inode lookup/delete tests, and local-vs-clustered locking configurations exercise this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/glock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/glops.c -->
## sources/distributed-fs/ceph-client/fs/gfs2/glops.c

### Purpose
`glops.c` defines the per-glock-type policy hooks used by the generic glock engine. It decides how inode and resource-group glocks sync dirty metadata, invalidate caches, instantiate in-core objects from disk, react to freeze and iopen callbacks, and expose debug details.

### Important APIs, Types, and Functions
The externally visible functions and data are `gfs2_ail_flush`, `gfs2_inode_metasync`, `gfs2_glock2rgrp`, `gfs2_freeze_wq`, the glock operation tables (`gfs2_meta_glops`, `gfs2_inode_glops`, `gfs2_rgrp_glops`, `gfs2_freeze_glops`, `gfs2_iopen_glops`, `gfs2_flock_glops`, `gfs2_nondisk_glops`, `gfs2_quota_glops`, `gfs2_journal_glops`), and `gfs2_glops_list`. Key static hooks include `rgrp_go_sync`, `rgrp_go_inval`, `inode_go_sync`, `inode_go_inval`, `inode_go_instantiate`, `inode_go_held`, `freeze_go_callback`, `freeze_go_xmote_bh`, and `iopen_go_callback`.

### Control Flow
AIL flushing starts with `gfs2_ail_flush` or `gfs2_ail_empty_gl`. The latter can create a revoke-only transaction to remove all buffers for a glock from the AIL, flush the log, and wait for revokes/log I/O. If unexpected dirty, pinned, or locked buffers remain outside fsync-tolerated paths, `gfs2_ail_error` logs details and withdraws the filesystem.

Resource-group demotion uses `rgrp_go_sync`: if the rgrp is dirty and held exclusive, flush the journal for that glock, write/wait metadata pages covering the rgrp blocks, empty the AIL, and free clone bitmaps. `rgrp_go_inval` releases rgrp buffers, asserts the AIL is empty, and truncates the metadata mapping range. Inode demotion is similar but also handles regular file data: `inode_go_sync` unmaps shared mappings for mmap-write pages, waits for direct I/O, flushes the log, writes metadata and data mappings, waits, empties AIL, and clears dirty state. `inode_go_inval` truncates glock metadata, refreshes instantiate requirements, invalidates ACL/security/dir-hash caches, marks rindex stale if needed, and truncates regular file page cache.

Instantiation uses `inode_go_instantiate` to refresh the dinode from disk through `gfs2_inode_refresh`; `gfs2_dinode_in` validates disk block identity, type stability, height/depth bounds, exhash constraints, stuffed size bounds, timestamps, block counts, disk flags, xattr pointers, and address-space operations. `inode_go_held` waits for direct I/O unless the holder requested deferred state and resumes interrupted truncation when the holder and glock are exclusive.

### State and Persistence Behavior
This file is the bridge between in-core glock state and durable storage. It flushes journals, writes metadata/data mappings, adds revokes, empties AIL lists, invalidates cache state when locks are demoted, and reloads dinodes when glocks are instantiated. Freeze hooks validate journal heads before resuming a live journal. Iopen callbacks schedule eviction when a remote node wants an iopen lock unlocked.

### Dependencies and Integration Points
`glops.c` depends on `glock.c` for hook invocation, `log`/`lops`/`trans` for journal and revoke mechanics, `meta_io` for dinode buffers, `rgrp` for resource-group state, `dir` for hash invalidation, `recovery` for journal-head reads, security and ACL APIs for cache invalidation, and Linux writeback/page-cache APIs. Operation table indices must match `LM_TYPE_*` values from `glock.h`.

### Risks and Edge Cases
The main risks are returning from demotion before data or metadata is durable, invalidating cache while dirty AIL entries remain, mishandling filesystem withdraw, stale rindex cache after metadata invalidation, and accepting corrupt dinode fields. Freeze callback paths are race-sensitive with unmount/remount because they try to take an active superblock reference.

### Test Signals
Useful tests include multi-node cache coherency under inode/rgrp demotion, journal replay and AIL revoke tests, fsync and truncate-in-progress recovery, freeze/thaw across cluster nodes, resource group allocation/free stress, dinode corruption detection, and remote unlink/iopen eviction behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/glops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/glops.h -->
## sources/distributed-fs/ceph-client/fs/gfs2/glops.h

### Purpose
`glops.h` declares the glock operation tables and synchronization helpers implemented in `glops.c`. It lets the generic glock engine and other GFS2 modules refer to type-specific policies without coupling to implementation details.

### Important APIs, Types, and Functions
The header exports `gfs2_freeze_wq`, all `const struct gfs2_glock_operations` instances for meta, inode, rgrp, freeze, iopen, flock, nondisk, quota, and journal glocks, the `gfs2_glops_list` lookup table, `gfs2_inode_metasync`, and `gfs2_ail_flush`.

### Control Flow
There is no executable control flow in the header. The declared operation tables are selected when glocks are created and invoked by `glock.c` around state transitions.

### State and Persistence Behavior
Persistence behavior is delegated to the declared helpers: `gfs2_inode_metasync` writes inode metadata mapping pages, while `gfs2_ail_flush` converts AIL buffers into revokes and flushes the log. The operation tables drive sync/invalidate/instantiate behavior at demotion and acquisition time.

### Dependencies and Integration Points
It includes `incore.h` and is used by glock creation sites in inode, file, rgrp, quota, journal, and mount/recovery code. The declarations must stay aligned with lock types and `gfs2_glops_list` indexing.

### Risks and Edge Cases
The header is small, but mismatched declarations or missing operation table entries would break glock creation or cause type-specific hooks not to run. That can become a durability or cache-coherency bug rather than a compile-only issue if an incorrect table is wired to a lock type.

### Test Signals
Indirect coverage comes from any test that creates and transitions each glock type, especially inode/rgrp demotion, freeze, iopen remote delete, quota locking, and journal recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/glops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/incore.h -->
## sources/distributed-fs/ceph-client/fs/gfs2/incore.h

### Purpose
`incore.h` is the central definition file for GFS2 in-memory state. It defines host-side versions of log, bitmap, resource-group, glock, holder, inode, quota, transaction, journal, mount-argument, lockspace, superblock, statfs, and tuning structures used by the implementation.

### Important APIs, Types, and Functions
Important structures include `gfs2_log_header_host`, `gfs2_log_operations`, `gfs2_bitmap`, `gfs2_rgrpd`, `gfs2_bufdata`, `lm_lockname`, `gfs2_glock_operations`, `gfs2_holder`, `gfs2_qadata`, `gfs2_blkreserv`, `gfs2_alloc_parms`, `gfs2_glock`, `gfs2_inode`, `gfs2_file`, `gfs2_quota_data`, `gfs2_trans`, `gfs2_jdesc`, `gfs2_args`, `gfs2_tune`, `lm_lockstruct`, and `gfs2_sbd`. Inline helpers include `GFS2_I`, `GFS2_SB`, `glock_type`, `glock_number`, `gfs2_aspace`, `gfs2_glstats_inc`, `gfs2_sbstats_inc`, and `gfs2_max_stuffed_size`.

### Control Flow
The header itself has only inline helper flow. Its real role is data-flow: glock state in `struct gfs2_glock` drives `glock.c`; `struct gfs2_inode` ties VFS inodes to inode and iopen glocks, quota data, reservations, and disk metadata; `struct gfs2_sbd` aggregates mount-wide constants, lockspace state, journal state, workqueues, statfs, resource groups, quota state, and debugfs state.

### State and Persistence Behavior
The file separates in-core-only state from disk-backed or journal-mediated state. Resource-group clone bitmaps are explicitly in-core and prevent freed blocks from being reallocated in the same transaction. `gfs2_bufdata` tracks buffers through transactions and AIL lists. `gfs2_trans` records transaction block/revoke reservations and buffer lists. `gfs2_inode` caches dinode fields such as address, generation, xattr block, disk flags, height/depth, entries, and allocation goal. `gfs2_sbd` tracks log heads/tails, in-flight log I/O, AIL lists, local and master statfs deltas, quota bitmaps, rgrp indexes, journal descriptors, and filesystem lifecycle flags.

### Dependencies and Integration Points
Nearly every GFS2 source includes `incore.h`. It integrates Linux `super_block`, `inode`, `address_space`, `buffer_head`, workqueues, completions, rhashtable, lockref, DLM lockspace, per-cpu stats, rbtrees, and kobjects with GFS2-specific on-disk structures from `linux/gfs2_ondisk.h`.

### Risks and Edge Cases
Structure layout and flag semantics are high impact. `lm_lockname` is used as an rhashtable key and intentionally avoids interior holes. Bit numbers in `GLF_*`, `HIF_*`, `SDF_*`, and other enums are shared across asynchronous code; changing them incorrectly breaks waits and state transitions. `gfs2_sbd` has many fields with different locking disciplines, so readers must respect the owning locks described by call sites. In-core clone bitmap behavior is essential for transaction allocation correctness.

### Test Signals
Coverage comes from broad filesystem testing: mount/unmount, DLM recovery, journal replay, allocation/free stress, quota accounting, statfs sync, glock stats/debugfs, memory pressure, and transaction abort/withdraw tests. Static analysis can catch struct field misuse, but most risks need concurrency and fault-injection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/incore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/inode.c -->
## sources/distributed-fs/ceph-client/fs/gfs2/inode.c

### Purpose
`inode.c` implements GFS2 inode lookup, creation, directory mutation, rename/exchange, permission, getattr/setattr, symlink reading, fiemap, seek-data/hole, and inode operation tables. It is the main VFS inode-operation bridge and coordinates directory contents, dinode allocation/deallocation, quota, rgrp locking, ACL/security xattrs, and glock ordering.

### Important APIs, Types, and Functions
Externally visible functions include `gfs2_setup_inode`, `gfs2_inode_lookup`, `gfs2_lookup_by_inum`, `gfs2_lookup_meta`, `gfs2_lookupi`, `gfs2_dinode_dealloc`, `gfs2_permission`, `gfs2_seek_data`, and `gfs2_seek_hole`. Static VFS callbacks include `gfs2_create`, `gfs2_lookup`, `gfs2_link`, `gfs2_unlink`, `gfs2_symlink`, `gfs2_mkdir`, `gfs2_mknod`, `gfs2_atomic_open`, `gfs2_rename2`, `gfs2_get_link`, `gfs2_setattr`, `gfs2_getattr`, `gfs2_fiemap`, and `gfs2_update_time`. The file defines `gfs2_file_iops`, `gfs2_dir_iops`, and `gfs2_symlink_iops`.

### Control Flow
Lookup begins with `iget5_locked`, then creates inode and iopen glocks for new VFS inodes, takes the iopen glock shared, optionally takes the inode glock with `GL_SKIP` to check block type or stale generation, attaches the in-core inode object to glocks, instantiates disk state when needed, sets operations, and unlocks the inode. Directory lookup takes the parent glock shared unless already held and calls `gfs2_dir_search`.

Creation (`gfs2_create_inode`) takes quota references, refreshes rindex, locks the parent directory exclusive, validates permissions/link limits/name existence, allocates a new VFS inode, sets mode/uid/gid/timestamps/inherited disk flags, allocates dinode and optional xattr block, creates inode and iopen glocks, inserts the inode into the inode cache, locks iopen and inode glocks, writes the dinode, sets ACLs/security xattrs, links into the directory, instantiates the dentry, and opens the file if atomic open requested. Failure paths deallocate xattrs/dinode, drop glocks, clear objects, and release quota.

Hard links lock parent and child glocks exclusive, validate target/link limits/immutability, allocate directory space if needed, start a transaction, add the directory entry, increment link count, and dirty the inode. Unlink/rmdir refresh rindex, lock parent, target, and target rgrp glocks, validate sticky/append/immutability/emptiness, remove the directory entry, update link count, and mark unlinked dinodes. Rename locks the global rename glock when moving across parents, acquires involved directory/inode glocks asynchronously with retry on `-ESTALE`, optionally locks the overwritten inode's rgrp, validates source/target, allocates target dir space, unlinks replacement, updates `..` or ctime, removes old entry, and adds new entry. `RENAME_EXCHANGE` swaps directory entries and adjusts parent link counts when directory/non-directory types cross parents.

### State and Persistence Behavior
Persistent state includes dinode fields, directory entries, link counts, ctime/mtime/atime, quota usage, resource-group bitmaps, statfs, ACL/security xattrs, xattr blocks, and unlinked state. Transactions wrap all mutating directory and dinode operations. `gfs2_dinode_dealloc` frees a dinode under the rgrp glock and final-releases pages. `gfs2_setattr` takes the inode glock exclusive, validates VFS attributes, routes size changes to truncate code, routes ownership changes through quota transfer, and wraps simple metadata changes in transactions as needed.

### Dependencies and Integration Points
`inode.c` depends on `glock` for cluster locking, `dir` for directory search/add/delete/move, `rgrp` for allocation and dinode free, `quota` for creation and chown accounting, `trans` for journaling, `meta_io` for dinode buffers, `acl`/`xattr`/security for metadata, `bmap`/iomap for fiemap and seek, `file.c` for file operation tables and open common, and `glops.c` for inode glock operation behavior.

### Risks and Edge Cases
The largest risks are incomplete failure unwinding during create, deadlocks from inconsistent multi-glock ordering, stale inode generations during delete/recreate races, rename cycles involving directories, unlinked-directory operations, quota/rgrp reservation mismatches, and page faults while holding glocks during fiemap. RCU permission checks must return `-ECHILD` instead of blocking. `gfs2_update_time` can upgrade a held shared glock to exclusive and must preserve holder consistency.

### Test Signals
Relevant tests include lookup under concurrent unlink/recreate, atomic open with and without `O_EXCL`, mkdir/symlink/mknod ACL and security xattr creation, hard link/unlink/rmdir limits, cross-directory rename and `RENAME_EXCHANGE`, chown quota transfer, truncate/setattr, fiemap with faulted user buffers, seek-data/hole correctness, NFS readdirplus lookup/getattr paths, and multi-node rename/unlink stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/inode.h -->
## sources/distributed-fs/ceph-client/fs/gfs2/inode.h

### Purpose
`inode.h` declares GFS2 inode helpers, public inode lookup/mutation APIs, file operation table exports, file-attribute hooks, and small inline predicates for data mode, stuffed files, block counts, and inode-number handling.

### Important APIs, Types, and Functions
Inline helpers include `gfs2_is_stuffed`, `gfs2_is_jdata`, `gfs2_is_ordered`, `gfs2_is_writeback`, `gfs2_is_dir`, `gfs2_set_inode_blocks`, `gfs2_get_inode_blocks`, `gfs2_add_inode_blocks`, `gfs2_check_inum`, `gfs2_inum_out`, and `gfs2_check_internal_file_size`. Declared functions include `gfs2_release_folio`, `gfs2_internal_read`, `gfs2_set_aops`, `gfs2_setup_inode`, `gfs2_inode_lookup`, `gfs2_lookup_by_inum`, `gfs2_dinode_dealloc`, `gfs2_lookupi`, `gfs2_permission`, `gfs2_lookup_meta`, `gfs2_dinode_out`, `gfs2_open_common`, `gfs2_seek_data`, `gfs2_seek_hole`, `gfs2_fileattr_get`, `gfs2_fileattr_set`, and `gfs2_set_inode_flags`.

### Control Flow
The header provides lightweight flow for common checks. Block count helpers translate filesystem blocks to VFS sectors using `i_blkbits - SECTOR_SHIFT`. `gfs2_check_internal_file_size` validates metadata file sizes against min/max and block alignment, marks the inode inconsistent on invalid size, and returns `-EIO`. The `CONFIG_GFS2_FS_LOCKING_DLM` block selects clustered file operation tables or aliases them to nolock tables for single-node builds.

### State and Persistence Behavior
The inline helpers manipulate or interpret VFS inode state and cached GFS2 dinode fields. `gfs2_inum_out` writes endian-converted inode numbers into directory entries. The file operation and fileattr declarations connect VFS actions to persistent dinode flags, block mappings, and directory state implemented in `file.c` and `inode.c`.

### Dependencies and Integration Points
`inode.h` includes Linux fs/buffer/mm headers and `util.h`, and is used by file, glock operation, directory, super, bmap, and quota code. It forms the public contract between inode operation implementation and other subsystems.

### Risks and Edge Cases
Incorrect block count shifts can corrupt accounting. The stuffed/jdata predicates must match on-disk flag semantics or writeback/journaling choices will be wrong. `gfs2_check_internal_file_size` is an important consistency guard for system files. Build-time aliasing for local locks must stay aligned with the file operation table definitions.

### Test Signals
Indirect tests cover stuffed-file transitions, jdata vs ordered/writeback mode behavior, internal metadata file size validation, inode lookup by number, directory entry inode-number encoding, localflocks vs DLM file operations, and fileattr flag get/set behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/inode.h -->
