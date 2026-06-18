# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/ValueQueue.java

## Purpose
`ValueQueue<E>` is a generic per-key value cache used by the KMS client to keep encrypted encryption keys pre-generated. It maintains expiring queues, synchronous fallback generation, and asynchronous low-watermark refill.

## Important APIs and types
`QueueRefiller<E>` supplies values for a key. `SyncGenerationPolicy` controls how many values are generated synchronously when a queue is empty: `ATLEAST_ONE`, `LOW_WATERMARK`, or `ALL`. Public APIs include constructors, `initializeQueuesForKeys()`, `getNext()`, `getAtMost()`, `drain()`, visible-for-testing `getSize()`, and `shutdown()`. Internal `UniqueKeyBlockingQueue` ensures only one queued/running refill task per key.

## Control flow
Construction validates parameters, creates striped read/write locks, builds a Guava `LoadingCache` from key name to `LinkedBlockingQueue`, and creates a daemon fixed-size refill executor. Cache load synchronously fills each new queue to the watermark. `getAtMost()` polls up to the requested count under per-key read locks. If insufficient values are present, it synchronously fills according to policy, then schedules an asynchronous refill if the queue is below watermark. `submitRefillTask()` lazily starts core threads and inserts a named runnable directly into the unique queue. `drain()` cancels queued tasks for the key and clears the existing queue under write lock.

## State and persistence
All state is in-memory: expiring per-key queues, striped locks, executor, unique refill queue, refiller callback, target queue size, watermark, and policy. There is no persistence; on restart/warmup queues are regenerated.

## Dependencies and integration points
It depends on relocated Guava `CacheBuilder`/`LoadingCache`, Java concurrent queues/executors, and Hadoop preconditions. `KMSClientProvider` instantiates it for `EncryptedKeyVersion` caching.

## Risks
Refiller exceptions are wrapped as `IOException`, and async refill exceptions become runtime exceptions on executor threads. The striped lock index uses hash masking with fixed array size; collisions serialize unrelated keys. `UniqueKeyBlockingQueue` removes a key from `keysInProgress` when a task is taken, not when it finishes, so a second task can be queued while one is running if timing allows. Queue size checks are approximate around concurrent refills.

## Test signals
Tests should cover parameter validation, cache load fill count, synchronous generation policies, async low-watermark refill, uniqueness/cancellation on drain, expiry behavior, concurrent `getAtMost()` calls for same/different keys, refiller exception propagation, and shutdown.
