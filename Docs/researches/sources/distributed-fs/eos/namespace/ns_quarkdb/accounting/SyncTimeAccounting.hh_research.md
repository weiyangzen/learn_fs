## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/SyncTimeAccounting.hh

Purpose: Declares `QuarkSyncTimeAccounting`, a listener that batches container mtime propagation and commits it asynchronously or manually.

Important APIs and types: public methods include the constructor with container service, update interval, and optional namespace stats; deleted copy/move operations; `containerMDChanged()`; `PropagateUpdates()`; `QueueForUpdate()`; and `setNamespaceStats()`. `UpdateT` combines an ordered list of container IDs with a map from ID to list iterator so repeated updates can be deduplicated and moved.

State behavior: two `UpdateT` slots represent the accumulating and committing batches. `mAccumulateIndx`/`mCommitIndx` are swapped under `mMutexBatch`. `mShutdown`, `mUpdateIntervalSec`, `mThread`, and the service pointer control worker lifecycle. The service and stats pointers are non-owning.

Dependencies and integration: depends on namespace metadata interfaces, assisted threading, logging, locking utilities, and stats. It is intended to be registered as an `IContainerMDChangeListener`.

Risks and test signals: users must ensure the container metadata service outlives the accounting object and that stats pointer updates are externally safe. Tests should inspect the two-batch queue model, no-thread mode, destructor join behavior, and the listener action filter.
