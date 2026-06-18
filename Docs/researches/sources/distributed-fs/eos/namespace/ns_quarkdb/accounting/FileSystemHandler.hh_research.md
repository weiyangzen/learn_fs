# sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemHandler.hh

Purpose: declares file-list iterators and the `FileSystemHandler` cache/controller for QuarkDB filesystem views.

Important APIs/types/functions: `FileListIterator` holds a shared lock over an in-memory `IFsView::FileList`. `StreamingFileListIterator` wraps `qclient::QSet::Iterator`. `FileSystemHandler` constructors target regular/unlinked/no-replica sets and expose loading, insert/erase, size, key lookup, iterators, `nuke`, random selection, membership, and cache clearing. Private `CacheStatus` and `Target` model cache state and set type.

Control flow: declarations establish two iterator modes: locked in-memory iteration and weakly consistent streaming iteration. Cache state transitions are implemented in the `.cc`.

State and persistence: declares all cache state, QDB/flusher pointers, change list, future splitter, last cache load timestamp, and test-visible cache status under `IN_TEST_HARNESS`.

Dependencies and integration: integrates `IFsView`, `IFileMD`, `SetChangeList`, qclient `QSet`, folly futures, executor async support, EOS assertions, and `SteadyClock`.

Risks: iterator validity depends on the chosen mode. In-memory iterator holds the shared lock for its lifetime, which can block writers. Streaming iterator converts QDB strings with `std::stoull` and will throw on corrupt set members.

Test signals: direct tests in `FileSystemViewTest.cc` target this class and expose `getCacheStatus` under test harness builds.
