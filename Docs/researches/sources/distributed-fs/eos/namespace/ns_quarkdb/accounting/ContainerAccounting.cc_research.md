# sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/ContainerAccounting.cc

Purpose: implements delayed propagation of file/container subtree accounting deltas up the container hierarchy.

Important APIs/types/functions: constructor starts propagation and queueing `AssistedThread`s when update interval is nonzero. Destructor queues id `0` sentinel and joins. `fileMDChanged`, `AddTree`, `RemoveTree`, `QueueForUpdate`, `PropagateUpdates`, `AsyncQueueForUpdate`, and assisted wrappers implement the accounting flow.

Control flow: file size/tree-change events enqueue the affected container id, using event `location` as container id when no file pointer is present. `AsyncQueueForUpdate` consumes queued deltas, walks parents up to root or depth 255 via `IContainerMDSvc::getContainerMD`, accumulates deltas for each ancestor in the active batch, and stops on sentinel id 0. `PropagateUpdates` swaps accumulate/commit batches, locks each target container for writing, updates tree size/file/container counters, and calls `updateStore`, then sleeps for the configured interval.

State and persistence: in-memory double-buffered batches, mutex, two assisted threads, queue of `(container id, TreeInfos)`, update interval, and container service pointer. Persistent effect is updated container metadata written through `IContainerMDSvc::updateStore`.

Dependencies and integration: registered by `QuarkNamespaceGroup` as a file change listener and injected into container service. Depends on `IFileMDChangeListener`, `IContainerMDSvc`, `MDLocking`, `TreeInfos`, and `ConcurrentQueue`.

Risks: id 0 is reserved as shutdown sentinel; accidental id 0 updates are dropped. Parent walk depth cap can miss pathological trees deeper than 255. Exceptions during propagation are swallowed, leaving counters stale until another repair. Asynchronous batching delays visible accounting updates. Destructor queues sentinel before joining but does not explicitly stop the propagation thread through a sentinel.

Test signals: tree accounting is exercised through hierarchical namespace tests and file size/container add/remove paths; direct tests should assert delayed propagation with update interval 0 and async modes.
