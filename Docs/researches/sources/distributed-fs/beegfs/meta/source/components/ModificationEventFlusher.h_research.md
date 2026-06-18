# sources/distributed-fs/beegfs/meta/source/components/ModificationEventFlusher.h

Purpose: This header declares the fsck modification-event flusher thread and its worker-synchronization controls.

Important APIs/types: `ModificationEventFlusher` derives from `PThread`. Public APIs are the constructor, `run()`, `add()`, `enableLogging()`, `disableLogging()`, `isLoggingEnabled()`, and `getFsckMissedEvent()`. Constants define max queue size, per-send batch size, flush interval, ACK wait, and ACK retries.

Control flow contract: `enableLogging()` clears buffers, sets fsck node address, marks logging enabled, and stalls all workers so they observe the state change. `disableLogging()` clears the logging flag and can flush/clear the queue while waiting for workers. `stallAllWorkers()` enqueues counter work on each worker's personal queue, with special handling when called from a worker thread to avoid self-deadlock.

State and persistence behavior: It owns the buffered event lists, mutexes/conditions for producer/flusher coordination, an atomic logging flag, fsck node handle, and missed-event flag. No durable queue exists.

Dependencies/integration: It reaches into `App` for worker list and work queue, uses `DatagramListener` for UDP ACK sends, and depends on BeeGFS worker work items such as `IncSyncedCounterWork`.

Risks and test signals: Worker-stalling is subtle and can deadlock if worker counts or thread identity are wrong. Queue clearing during disable avoids blocked producers but drops pending events, relying on `fsckMissedEvent`. Tests should cover enable/disable from worker and non-worker contexts, backpressure, and failed fsck acknowledgments.
