# sources/distributed-fs/beegfs/meta/source/components/DisposalGarbageCollector.cpp

Purpose: This component function performs periodic cleanup of disposal-directory entries owned by the local metadata node.

Important APIs/functions: `disposalGarbageCollector()` is the scheduled entry point. It obtains `App` through `Program::getApp()`, builds a node vector containing the local metadata node, constructs `DisposalCleaner` with the metadata buddy-group mapper, and calls `dc.run()` with callbacks. `deleteFile()` wraps `DisposalCleaner::unlinkFile()` and logs communication, in-use, and other errors while counting successful unlinks. `handleError()` logs run-level failures.

Control flow: A run logs start, unlinks eligible entries through the cleaner, logs finish with the unlinked count, and re-enqueues itself on `app->getGcQueue()` after `tuneDisposalGCPeriod` seconds if the period remains nonzero and the queue still exists. The cleaner receives a termination predicate tied to `gcQueue->getSelfTerminate()`.

State and persistence behavior: This code deletes metadata/storage-disposal entries through normal BeeGFS cleanup mechanisms. It does not store its own state; scheduling state is held by `TimerQueue`.

Dependencies/integration: `App::startComponents()` enqueues this function when disposal GC is configured. Shutdown deletes `gcQueue`, so the null check before requeue matters.

Risks and test signals: `deleteFile()` currently returns `FhgfsOpsErr_SUCCESS` even when `unlinkFile()` failed, relying on logging rather than propagating per-file failure. The run references the local node handle and app queues, so shutdown races are a concern. No direct tests cover requeueing or error propagation here.
