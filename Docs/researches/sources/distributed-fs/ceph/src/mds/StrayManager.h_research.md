# sources/distributed-fs/ceph/src/mds/StrayManager.h

Purpose: Declares the stray-management component consumed by `MDCache` to evaluate orphaned/unlinked metadata and either purge, truncate, migrate, or reintegrate it.

Important APIs/types: Public methods include `activate`, `eval_stray`, `queue_delayed`, `advance_delayed`, `eval_remote`, `migrate_stray`, stray count setters/getters, and create/remove notifications. `StrayEvalRequest` is an internal `MDSMetaRequest` wrapper that pins a dentry while an internal rename performs reintegration or migration.

Control flow: Callers can queue dentries for later evaluation when not inside another metadata operation. Remote dentries can trigger evaluation of their primary stray. Protected methods split the pipeline into evaluation, enqueue/retry, purge/truncate execution, completion, and reintegration/migration helpers.

State and persistence behavior: The manager itself stores in-memory queues/counters and a set of trimmed stray names. Persistent cleanup occurs through `PurgeQueue` plus mdlog updates in the implementation. `num_strays_enqueuing` marks dentries accepted for purge but not yet durably recorded by the queue.

Dependencies and integration points: Depends on `MDSMetaRequest`, `CDentry`, `PurgeQueue`, `MDSRank`, `CInode`, `MutationImpl`, and perf counters. Friend context classes are used for IO/log/context callback access.

Risks: The API assumes only started managers enqueue work. `StrayEvalRequest` manipulates `reintegration_reqid` and `PIN_PURGING`; leaks or duplicate requests would block future reintegration. Counters must be balanced across create/remove/enqueue/completion.

Test signals: Validate delayed list membership, request pin lifetime, counters, `started` gating, and public migration/evaluation entry points.
