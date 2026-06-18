# File Research: sources/cow-pools/openzfs/module/zfs/dsl_synctask.c

## Role

Provides the DSL sync-task framework for running caller-supplied checks and mutations in txg syncing context with the correct pool configuration locking and space checks.

## Key Functions

- `dsl_sync_task_common()` opens the target pool, creates a transaction, runs the check callback once in open context under config read locking, queues the task into either normal or early sync-task txg lists, waits for sync completion, and retries after `EAGAIN` once the deferred txg window has synced.
- `dsl_sync_task()` queues a normal blocking sync task.
- `dsl_early_sync_task()` queues a blocking early sync task that executes before dirty dataset data is written in `dsl_pool_sync()`.
- `dsl_sync_task_sig()` supports an interruptible wait and invokes a signal callback once if interrupted while still ensuring the txg sync completes.
- `dsl_sync_task_nowait()` and `dsl_early_sync_task_nowait()` allocate nowait task records and enqueue fire-and-forget sync callbacks.
- `dsl_sync_task_sync()` is called in syncing context, checks requested pool space reservations, takes `dp_config_rwlock` as writer, reruns the check callback, invokes the sync callback on success, and frees nowait tasks.

## Space and Locking Semantics

- `blocks_modified` is converted to an estimated MOS space cost using `DST_AVG_BLKSHIFT`.
- Space checks use `dsl_pool_unreserved_space()` and root-dir used bytes, with MOS writes multiplied by 3 for dittoed metadata.
- Open-context checks run with config read locking; sync-context checks and mutations run with config write locking.
- Early tasks are explicitly warned not to dirty metaslabs because they run before normal dirty-data syncing.

## Research Notes

This file is the small but central bridge between ioctl/open-context control paths and txg-synchronous metadata mutation. Its contract lets callers validate cheaply before queueing, then validate again under syncing-context invariants immediately before mutation.
