## sources/distributed-fs/eos/namespace/ns_quarkdb/flusher/MetadataFlusher.cc

Purpose: Implements the asynchronous metadata write queue toward QuarkDB. It wraps `qclient::BackgroundFlusher` with RocksDB-backed persistency, convenience Redis command helpers, synchronization, queue metrics, and notifier logging.

Important APIs and control flow: constructors build a background flusher from contact details and either default `RocksDBPersistency` or a builder-selected flusher type/options, then call `synchronize()` to wait for initial state. The destructor joins the monitoring thread and synchronizes all queued writes. Command helpers stage `HSET`, `HINCRBY`, `DEL`, `HDEL`, `SADD`, and `SREM`; `exec()`/`execute()` support arbitrary requests. `synchronize()` waits until a target queue index, defaulting to the latest currently enqueued item, is acknowledged, logging warnings every second while pending. `queueSizeMonitoring()` logs pending/enqueued/acknowledged/index stats every 10 seconds when there is queued work.

State and persistence: `BackgroundFlusher` owns the durable local queue and remote delivery. `persistencyConfig` caches the persistency type returned by the flusher. `id` is derived from the RocksDB path basename and used in logs.

Dependencies and integration: central dependency for quota and filesystem accounting writes. It uses `QdbContactDetails`, qclient builders, RocksDB persistency/config, assisted threads, and EOS logging.

Risks and test signals: command helpers are fire-and-forget until explicit synchronization or destruction. Crash recovery depends on the qclient persistent flusher implementation. `synchronize()` can wait indefinitely on a permanently unacknowledged index. Tests should use fake/background flusher hooks to verify command vector formation, target-index behavior, notifier logging, persistency type caching, and destructor flushing.
