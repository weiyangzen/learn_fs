## sources/distributed-fs/ceph-client/fs/jbd2/checkpoint.c

Purpose: implements JBD2 checkpointing, the process that writes committed metadata buffers back to their home locations and frees journal log space for reuse.

Important APIs: `__jbd2_log_wait_for_space` waits for enough log space, driving checkpoints or waiting for commits. `jbd2_log_do_checkpoint` writes one checkpoint transaction's dirty buffers. `jbd2_cleanup_journal_tail` advances the journal tail after checkpointed data is safe. Checkpoint list APIs include `__jbd2_journal_insert_checkpoint`, `__jbd2_journal_remove_checkpoint`, `jbd2_journal_try_remove_checkpoint`, `jbd2_journal_shrink_checkpoint_list`, `__jbd2_journal_clean_checkpoint_list`, `jbd2_journal_destroy_checkpoint`, and `__jbd2_journal_drop_transaction`.

Control flow: log-space wait drops `j_state_lock` to take `j_checkpoint_mutex`, rechecks space, checkpoints available transactions, tries tail cleanup, waits for a committing transaction, or aborts if no progress is possible. Checkpointing cleans the tail, selects the oldest checkpoint transaction, loops its checkpoint buffers under `j_list_lock`, waits for busy buffers, removes clean buffers, batches dirty buffers into `j_chkpt_bhs`, writes them with block plugging, and retries until the transaction can be released.

State and persistence: persistent correctness hinges on not advancing the journal tail until all relevant home-location writes are durable. With `JBD2_BARRIER`, `jbd2_cleanup_journal_tail` flushes the filesystem device before updating the tail. Runtime state includes circular transaction checkpoint lists, circular buffer checkpoint lists, per-transaction checkpoint stats, `j_shrink_transaction`, and `j_checkpoint_jh_count`.

Dependencies and integration points: depends on buffer-head state, journal locks (`j_state_lock`, `j_list_lock`, `j_checkpoint_mutex`), block flushes, tracepoints, transaction states, and commit code that inserts buffers into checkpoint lists.

Risks and test signals: risks include lock ordering deadlocks, freeing a transaction before `T_FINISHED`, advancing tail after failed checkpoint writes, busy-buffer shrink livelock, and abort-state handling. Test forced small journals, heavy metadata workloads, writeback errors, barrier on/off, unmount during checkpoint, memory pressure shrinker paths, aborted journals, and transactions with buffers relogged into newer transactions.
