<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_debugfs.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_debugfs.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_debugfs.c_research.md`.

Purpose: implements kfilnd debugfs files for transaction latency/state statistics, stats reset, and mempool reserve visibility.

Important APIs/types/functions: helpers `get_ave_duration()`, `get_min_duration()`, `seq_print_tn_state_stats()`, and `seq_print_tn_stats()` format per-size-bucket metrics. File operations exported are `kfilnd_initiator_state_stats_file_ops`, `kfilnd_target_state_stats_file_ops`, `kfilnd_initiator_stats_file_ops`, `kfilnd_target_stats_file_ops`, `kfilnd_reset_stats_file_ops`, and `kfilnd_mempool_stats_file_ops`.

Control flow: debugfs open uses `single_open()` with device pointer private data. State stats print one row per data-size bucket with average time spent in each transaction state. Aggregate stats print min/max/average/count for initiator or target transactions. Writing `reset_stats` calls `kfilnd_dev_reset_stats()`. `mempool_stats` calls `kfilnd_tn_get_mempool_stats()` and prints reserve and current availability or not-initialized messages.

State and persistence behavior: reads sample atomic duration/count fields stored in `struct kfilnd_dev`; write resets those atomics. Mempool stats reflect global transaction/message mempools. No persistent files are created beyond debugfs dentries.

Dependencies and integration: created by `kfilnd_dev_alloc()` under the device debugfs directory and by `kfilnd_tn_init()` for mempool stats. Depends on seq_file, debugfs, transaction state enums, and device reset helper.

Risks: averages can race with concurrent updates and are observational only. `TIME_MAX` clamps averages but max values are printed raw. Reset can race with active transaction finalization. Several debugfs dentry assignments in device allocation reuse the same struct member, so only cleanup-by-directory matters.

Test signals: run immediate and bulk traffic, read initiator/target aggregate and per-state files, reset stats while traffic runs, verify min reset displays as 0, inspect mempool stats before/after transaction init, and remove the NI while files are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_debugfs.c -->
