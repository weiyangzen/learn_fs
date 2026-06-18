## sources/distributed-fs/eos/namespace/interface/IFsView.hh

Purpose: Defines the filesystem-location view that indexes files by storage filesystem, unlinked state, and no-replica state, and listens to file metadata changes.

Important APIs and types: `ICollectionIterator<T>` is the generic iterator interface. `IFsView::FileList` is a dense hash set of file ids. `IFsView` exposes configure, file change/read callbacks, file-list iterators, streaming iterators, erase, random file selection, counts, unlinked list access/clear, no-replica list access, filesystem id iterator, membership checks, finalize, and shrink.

Control flow: file metadata listener events update filesystem indexes. Callers request iterators for FST cleanup, balancing, repair, or prefetch; iterators expose current element, validity, and next.

State and persistence: concrete views maintain in-memory or persisted indexes mapping filesystem ids to file ids and unlinked/no-replica collections. `FileIterator` holds a reference to a list; `StupidFileSystemIterator` walks a numeric range.

Dependencies and integration: depends on `IFileMDSvc`, `IFileMDChangeListener`, `MDException`, Google dense hash set, Murmur hash, and standard sets. Used by prefetcher and MGM filesystem operations.

Risks: `FileIterator` references an external list, so the list must outlive the iterator and not mutate unsafely. Random selection is approximate by contract. Streaming and snapshot iterator semantics can differ by implementation.

Test signals: listener-driven index updates, unlinked transitions, no-replica tracking, iterator validity on empty/non-empty lists, random file behavior, clear unlinked list, and shrink/finalize lifecycle.
