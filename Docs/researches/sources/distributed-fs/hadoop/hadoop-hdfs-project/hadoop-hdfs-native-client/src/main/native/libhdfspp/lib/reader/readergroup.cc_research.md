# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/reader/readergroup.cc

Purpose: implements `ReaderGroup`, a small helper tracking live `BlockReader` instances by weak reference.

Important APIs and functions: `AddReader`, `GetLiveReaders`, and `ClearDeadReaders`.

Control flow: adding a reader first clears expired weak pointers, then stores a weak reference to the new reader. `GetLiveReaders` locks and promotes non-expired readers. `ClearDeadReaders` uses `remove_if` to erase expired entries.

State and persistence: maintains an in-memory vector of `weak_ptr<BlockReader>` guarded by `recursive_mutex`.

Dependencies and integration: depends on `readergroup.h`, `<algorithm>`, and `BlockReader`. It can support coordinated cancellation/inspection of active readers by higher-level file-handle code.

Risks and test signals: recursive mutex hides nested locking from `AddReader` to `ClearDeadReaders`; tests should verify expired-reader cleanup and concurrent add/list behavior. Since only weak refs are stored, callers must own readers elsewhere.
