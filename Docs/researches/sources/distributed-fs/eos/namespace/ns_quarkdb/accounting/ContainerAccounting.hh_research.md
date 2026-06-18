# sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/ContainerAccounting.hh

Purpose: declares `QuarkContainerAccounting`, the file-change listener that maintains container subtree counters.

Important APIs/types/functions: implements `IFileMDChangeListener` methods `fileMDChanged`, `fileMDRead`, and `fileMDCheck`; exposes `AddTree`, `RemoveTree`, `QueueForUpdate`, `PropagateUpdates`, and `AsyncQueueForUpdate`. Private state includes `UpdateT`, two batches, mutex, accumulate/commit indices, assisted threads, update interval, container service pointer, and update queue.

Control flow: the header defines the public/assisted split: one thread queues ancestor updates, another commits accumulated batches.

State and persistence: transient batching state; persistent updates are performed by implementation through the container metadata service.

Dependencies and integration: depends on namespace interfaces, assisted threading, standard threading containers, and concurrent queue.

Risks: copy/move are deleted because thread and service ownership are nontrivial. Thread lifecycle and queue sentinel protocol must match the implementation.

Test signals: hierarchical/accounting behavior should be validated by namespace tests that inspect tree counters after mutations.
