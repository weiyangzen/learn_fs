# sources/distributed-fs/ceph-client/block/blk-mq-debugfs.c

## Purpose
`blk-mq-debugfs.c` creates debugfs files for blk-mq queues, hardware contexts, software contexts, schedulers, and rq-qos policies. It exposes live request state, queue flags, tag bitmaps, dispatch lists, busy requests, and limited control operations for debugging.

## Important APIs, Types, And Functions
The exported request renderers are `__blk_mq_debugfs_rq_show()` and `blk_mq_debugfs_rq_show()`. Registration APIs include `blk_mq_debugfs_register()`, `blk_mq_debugfs_register_hctx()`, `blk_mq_debugfs_unregister_hctx()`, `blk_mq_debugfs_register_hctxs()`, `blk_mq_debugfs_unregister_hctxs()`, `blk_mq_debugfs_register_sched()`, `blk_mq_debugfs_unregister_sched()`, `blk_mq_debugfs_register_rq_qos()`, `blk_mq_debugfs_register_sched_hctx()`, and `blk_mq_debugfs_unregister_sched_hctx()`. `struct blk_mq_debugfs_attr` describes simple show/write or seq-ops files.

## Control Flow
Queue-level files expose `poll_stat`, `requeue_list`, `pm_only`, `state`, and zoned write plugs. Writing `state` accepts `run`, `start`, or `kick`, while rejecting writes on dying queues. Hctx files expose state/flags, dispatch and busy request lists, context maps, tags, sched tags, active count, dispatch busy score, and hctx type. Per-CPU context directories expose request lists by hctx type. Registration walks all hctxs, creates `hctxN` and `cpuN` directories, and later creates `sched` and `rqos` subtrees when schedulers or rq-qos policies are installed. File open/release selects either seq ops or `single_open()` based on the attr definition.

## State And Persistence
The debugfs tree is transient kernel diagnostic state. It stores dentries in `q->debugfs_dir`, `hctx->debugfs_dir`, `hctx->sched_debugfs_dir`, `q->sched_debugfs_dir`, and rq-qos `debugfs_dir`. Data reads are live snapshots protected by relevant locks such as `requeue_lock`, `hctx->lock`, `elevator_lock`, and `debugfs_mutex`.

## Dependencies And Integration Points
The file integrates with debugfs, seq_file, blk-mq request/tag internals, scheduler debug attributes, rq-qos debug attributes, queue debugfs locking, zone write plugging, and driver `mq_ops->show_rq`.

## Risks And Test Signals
Risks are use-after-free during queue removal, lock ordering against frozen queues, exposing stale request state while completions race, and writable debugfs operations changing queue execution. Tests should verify registration/unregistration during elevator switches and queue teardown, readable tag and request lists under load, rejection of invalid `state` writes, and correct absence of files when scheduler/rq-qos attrs are unavailable.
