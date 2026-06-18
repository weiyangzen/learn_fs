## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/SyncTimeAccounting.cc

Purpose: Implements asynchronous synchronous-time/mtime propagation for container metadata. On `MTimeChange`, it queues the changed container and later propagates terminal mtime up ancestors that opt in with `sys.mtime.propagation`.

Important APIs and control flow: the constructor initializes two update batches and starts an assisted propagation thread when the interval is nonzero. `containerMDChanged()` queues only `MTimeChange` events. `QueueForUpdate()` deduplicates within the accumulating batch and moves repeated IDs to the end as most recent. `PropagateUpdates()` swaps accumulate/commit batches, walks the commit list in reverse, fetches containers, write-locks them, checks propagation attributes, removes `sys.tmp.etag`, copies the leaf mtime to `TMTime`, updates storage, and stops at root, depth 255, missing attribute, unchanged propagated time, already-updated node, or metadata exception.

State and persistence: all pending updates live in two `UpdateT` batches protected by `mMutexBatch`; storage updates go through `IContainerMDSvc::updateStore()`. `INamespaceStats` receives batch size and execution-time metrics when configured. Shutdown sets `mShutdown` and joins the thread.

Dependencies and integration: integrates `IContainerMDChangeListener`, `IContainerMDSvc`, container write locking, EOS logging, `AssistedThread`, and namespace stats.

Risks and test signals: with update interval zero, callers can invoke `PropagateUpdates(nullptr)` for a one-shot drain; otherwise it loops and sleeps. The reverse-order traversal and `upd_nodes` set are important for avoiding redundant ancestor writes. The code catches `MDException` and silently stops that chain. Tests should cover dedup ordering, opt-in attribute behavior, tmp-etag removal, unchanged-time early exit, depth limit, shutdown behavior, stats emission, and service exceptions.
