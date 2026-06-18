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
