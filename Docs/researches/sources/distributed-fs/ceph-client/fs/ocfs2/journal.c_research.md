# sources/distributed-fs/ceph-client/fs/ocfs2/journal.c

## Purpose
`journal.c` implements OCFS2 journaling, checkpointing, journal load/shutdown, transaction wrappers, metadata checksum triggers, node recovery, offline-slot replay, orphan scanning, quota recovery coordination, and the commit thread. It bridges OCFS2 cluster recovery semantics with the Linux JBD2 journal.

## Important APIs, types, and functions
- `ocfs2_journal_alloc()`, `ocfs2_journal_init()`, `ocfs2_journal_load()`, `ocfs2_journal_shutdown()`, and `ocfs2_journal_wipe()` manage a node journal lifecycle.
- `ocfs2_start_trans()`, `ocfs2_commit_trans()`, `ocfs2_extend_trans()`, `ocfs2_assure_trans_credits()`, and `ocfs2_allocate_extend_trans()` wrap JBD2 handles with OCFS2 barriers and superblock write accounting.
- `ocfs2_journal_access_*()` and `ocfs2_journal_dirty()` enforce metadata-cache locking and attach ECC triggers for dinodes, extent blocks, refcount blocks, group descriptors, directories, xattrs, quotas, and indexed directory blocks.
- `ocfs2_recovery_init()`, `ocfs2_recovery_thread()`, `__ocfs2_recovery_thread()`, `ocfs2_recover_node()`, and `ocfs2_complete_recovery()` coordinate node failure recovery.
- `ocfs2_compute_replay_slots()`, `ocfs2_queue_replay_slots()`, and `ocfs2_free_replay_slots()` track offline slots that need replay/cleanup.
- `ocfs2_orphan_scan_*()` periodically scans orphan directories to catch cluster-open inodes left behind by remote unlink races.

## Control flow
Mount allocates `struct ocfs2_journal`, opens the local journal system inode, initializes JBD2 with `jbd2_journal_init_inode()`, records whether the on-disk journal was dirty, loads/replays it, marks it dirty, and starts `ocfs2_commit_thread()` for clustered mounts. Transactions take `sb_start_intwrite()` and a read lock on `j_trans_barrier`, then start a JBD2 handle. Checkpointing takes the barrier in write mode, flushes JBD2, increments `j_trans_id`, clears `j_num_trans`, wakes the downconvert thread, and wakes waiters on `j_checkpointed`.

Recovery is driven by a recovery map of node numbers. `ocfs2_recovery_thread()` test-and-sets a dead node and starts one kernel thread. The thread waits for mount state, takes the super lock, computes offline replay slots, replays each dead node's journal, begins local alloc and truncate-log recovery, clears the slot, and queues completion work. Completion work runs outside the recovery thread to return local alloc bits, finish truncate logs and quotas, and recover orphans under ordinary cluster locks. Journal replay force-reads journal blocks, initializes a temporary JBD2 journal, loads and flushes it, clears the dirty flag, bumps the slot recovery generation, and writes the journal dinode.

## State and persistence behavior
Persistent journal state is stored in the journal dinode flags and recovery generation. Runtime state includes `j_state`, `j_journal`, `j_inode`, `j_bh`, `j_num_trans`, `j_trans_id`, `j_trans_barrier`, `j_checkpointed`, and queued recovery cleanup items. Recovery maps live in memory, while slot cleanup persists through journal dirty-bit clearing, slot-map clearing, local alloc cleanup, truncate-log recovery, quota updates, and orphan deletion. Metadata ECC is recomputed at JBD2 freeze time through triggers.

## Dependencies and integration points
The file depends heavily on JBD2, OCFS2 DLM and super locks, heartbeat/slot-map state, system file lookup, inode metadata cache, localalloc, truncate log, quota, directory/orphan helpers, refcount/file helpers, and buffer-head I/O. It also exports trigger setup used by superblock initialization and transaction APIs used by almost every mutating OCFS2 subsystem.

## Risks and edge cases
- Recovery is split into critical replay/slot-cleaning and later cleanup. Tests must distinguish a recovered slot from fully reclaimed local alloc/orphan/quota state.
- `ocfs2_replay_journal()` uses recovery generation numbers to avoid replaying a slot already recovered by another node.
- `j_trans_barrier` must not be dropped during transaction extension/restart because lock transaction ids depend on it.
- `ocfs2_journal_dirty()` aborts the handle and journal if metadata dirtying fails.
- Shutdown must stop the commit thread and flush outstanding transactions before destroying JBD2 and marking the journal clean.
- Orphan scan deliberately scans active slots to resolve cluster-open/unlinked inode cases.

## Test signals
Cover journal load with clean and dirty journals, replay generation races, dead-node detection by trylocking journals, commit thread wake/shutdown behavior, checkpoint waiters in inode clear, metadata ECC trigger recomputation, aborted journal handling, quota-enabled recovery disable transitions, orphan scan sequence-number behavior, and hard-readonly journal checks that return `-EROFS` when any journal is dirty.
