# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-lk-common.c

## Purpose
Provides the shared internal lock engine used by AFR transactions. It manages entry locks and inode locks across replica children, supports nonblocking acquisition with blocking fallback, records which nodes are locked for each lockee, and performs coordinated unlock.

## Important APIs, types, and functions
`afr_add_entry_lockee()` and `afr_add_inode_lockee()` populate transaction lock targets. `afr_entry_lockee_cmp()` gives deterministic entry lock ordering by gfid and basename. `afr_set_lk_owner()` assigns a lock owner from a pointer. `afr_lock_nonblocking()` sends parallel nonblocking locks to up children. `afr_blocking_lock()` retries serial blocking locks. `afr_unlock()` handles eager-lock owner list release and calls `afr_unlock_now()` when actual unlock is needed. `afr_internal_lock_wind()` chooses entrylk/fentrylk or inodelk/finodelk based on transaction type.

## Control flow
Transactions set up lockees, then try nonblocking locks across up children. If every expected lock succeeds, the transaction callback proceeds. If only some locks succeed, AFR unlocks and retries with blocking locks in deterministic child/lockee order. Blocking lock sufficiency requires at least one child where every required lockee succeeded, which matters for multi-lock operations such as mkdir and rename. Unlock callbacks decrement `lk_call_count` and call the transaction continuation once all unlocks finish.

## State and persistence behavior
State is in `afr_internal_lock_t`: lockee array, `locked_nodes[]`, locked counts, attempted counts, expected counts, op errno, lock domain, and callback. For data transactions, successful inode locks increment `inode_ctx->lock_count`; unlock can reset write subvol state. Locks are not durable, but they gate durable child mutations and changelog updates.

## Dependencies and integration points
Depends on AFR transaction types, AFR memory types, child lock FOPs, fd ctx, inode ctx, eager-lock lists, Gluster lock owner helpers, and logging message IDs. It is central to directory and inode write transaction correctness.

## Risks and test signals
Risks include deadlocks from ordering mistakes, lock leaks after partial failures, insufficient multi-lock success checks, ENOSYS behavior when locks xlator is missing, fd ctx failures during lock acquisition, eager-unlock races, and incorrect data lock count accounting. Tests should cover nonblocking success, fallback to blocking, multi-lock rename, unlock after partial child failure, child down filtering, ENOSYS, eager lock release, and fd-based lock paths.
