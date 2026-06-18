# sources/distributed-fs/openafs/src/afs/afs_cbqueue.c

Purpose: Actively manages callback expiration so most cache-manager paths can test callback validity through vnode state bits instead of recomputing expiration times.

Important APIs and functions: `afs_QueueCallback` inserts a vcache into the expiration wheel. `afs_DequeueCallback` removes it. `afs_CheckCallbacks` scans the current bucket for callbacks expiring soon, invalidates or requeues them, and handles RO volume callback expiration. `afs_FlushCBs` drops all callbacks, `afs_FlushServerCBs` drops callbacks for one server, `afs_InitCBQueue` initializes the wheel, and `afs_BumpBase` advances the base bucket as time passes.

Control flow: The wheel has `CBHTSIZE` buckets of `CBHTSLOTLEN` seconds. Queueing offsets the server-provided time by `base` and leaves already queued vcaches in place. Periodic checking scans the base bucket backward under `afs_xcbhash`, compares `cbExpires` with `now + secs`, stales vcaches whose callbacks are about to expire, preserves RO callbacks when the volume callback is still valid, and rehashes entries renewed into a later slot. `BumpBase` advances `base` and concatenates old bucket contents into the new base for continued checking.

State and persistence: Volatile globals are `base`, `basetime`, `cbHashT`, debug pointer `debugvc`, and lock `afs_xcbhash`. Vcache `callsort`, `cbExpires`, callback flags, `dchint`, and volume `expireTime` are the operational state. Nothing is persisted.

Dependencies and integration points: Uses AFS queue macros, vcache/volume state, server down flags, DNLC invalidation flags, stats, and daemon periodic scheduling. It is tightly coupled with callback break handling in `afs_callback.c` and callback assignment in fetch/status paths.

Risks: The code intentionally does not lock each vcache during expiration checks to avoid deadlocks, relying on documented races with `QueueCallback`. Corrupted queues can loop; `CBQ_LIMIT` detects this and flushes all callbacks. Time-wheel assumptions depend on server callback slop and daemon scheduling frequency.

Test signals: Queue/dequeue idempotence, renewed callback rehashing, soon-expiring RW invalidation, RO volume callback preservation, server-down RO behavior, base bump across multiple slots, full flush, per-server flush, corrupted-loop safety counter, and concurrent queue/check stress.
