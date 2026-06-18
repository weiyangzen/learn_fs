# sources/distributed-fs/coda/coda-src/vol/lockqueue.cc

Purpose: implements a volume lock queue manager that times out stale exclusive volume locks and forces unlocks.

Important APIs/classes: global `LockQueueMan`, `InitLockQueue`, `ForceUnlockVol`, `lqman`, `lq_iterator`, and `lqent`. `lqman::func` runs as an LWP, initializes RVM thread data, tags itself as a volume utility, scans queued lock entries every `LQINTERVAL`, and unlocks entries older than `LQTIMEOUT` unless they are being dequeued.

Control flow/state: exclusive locks obtained through `GetVolObj` can enqueue an `lqent`. On timeout, the manager removes the entry, calls `ForceUnlockVol`, which gets the volume without a lock and then calls `PutVolObj` as an exclusive unlock. `findanddeq` marks an entry `deqing` so the manager will not race normal unlock cleanup.

Dependencies/integration: depends on LWP, RPC2 types, RVM per-thread setup, `GetVolObj`/`PutVolObj`, `VolumeId`, and `dlist`. Risks include global manager lifetime, fixed timeout policy, forced unlock assumptions, use of write locks around list mutation, and possible stale `lqent` if callers forget `Dequeue`. Test signals: acquire/release exclusive lock with queue entry, timeout unlock, deq race, manager startup/shutdown, and lock contention with shared locks.
