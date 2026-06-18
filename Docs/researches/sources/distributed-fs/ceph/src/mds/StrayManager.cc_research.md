# sources/distributed-fs/ceph/src/mds/StrayManager.cc

Purpose: Implements asynchronous evaluation, truncation, purge, migration, and reintegration of MDS stray dentries/inodes.

Important APIs/functions: `eval_stray`, `_eval_stray`, `eval_remote`, `_eval_stray_remote`, `queue_delayed`, `advance_delayed`, `enqueue`, `_enqueue`, `purge`, `_purge_stray_purged`, `_purge_stray_logged`, `truncate`, `_truncate_stray_logged`, `reintegrate_stray`, `migrate_stray`, `activate`, and stray counter notifications.

Control flow: `_eval_stray()` only acts on auth stray dentries after startup. If `nlink == 0`, it prunes/purges stale snap data, checks directory snap parents, replication, leases, caps, recovery, and refcounts, then enqueues either a full purge or a HEAD truncate for files with old snap metadata. If links remain, `_eval_stray_remote()` tries to reintegrate into an auth remote dentry or migrates the stray to the remote authority.

State and persistence behavior: Purge data removal is enqueued to `PurgeQueue` before metadata cleanup is journaled with `EUpdate`. Full purge journals a null dentry and destroyed inode, applies mutation, unlinks/removes cache objects, and clears purging pins. Truncate purge journals zeroed size/max-size/client ranges but keeps the metadata so snap data remains valid. Counters track total, delayed, and enqueuing strays.

Dependencies and integration points: Uses `MDSRank`, `MDCache`, `MDLog`, `PurgeQueue`, `ScrubStack`, `SnapRealm`, `EUpdate`, `MClientRequest`, `BatchOp`, `CDir`, `CDentry`, and `CInode`. Reintegration and migration are expressed as internal rename client requests.

Risks: Refcount assertions intentionally abort on rogue references after purge. Directory stray purge waits for past parent snaps to disappear. Freezing dirs delay auth pin acquisition. Race comments around reintegration note that projected remote dentries must be rechecked in rename. Dirty-parent bits are cleared early to avoid backtrace writes during purge.

Test signals: Cover purge eligibility gates, delayed queue behavior, frozen dir retry, purge queue completion, full purge journal apply, truncate-then-reevaluate, remote reintegration, remote migration during shutdown, stale snap remote cleanup, and scrub-stack removal.
