# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filesystem_sync.cc

Purpose: provides blocking `FileSystemImpl` methods by wrapping the asynchronous filesystem API with `std::promise` and `std::future`. It intentionally contains boilerplate sync shims rather than core filesystem logic.

Important APIs and functions: sync variants of `Connect`, `ConnectToDefaultFs`, `Open`, `GetBlockLocations`, `GetPreferredBlockSize`, `SetReplication`, `SetTimes`, `GetFileInfo`, `GetContentSummary`, `GetFsStats`, `GetListing`, `Mkdirs`, `Delete`, `Rename`, `SetPermission`, `SetOwner`, `Find`, and snapshot operations.

Control flow: each method creates a promise, passes a callback to the async method, waits on the future, then copies successful output data into caller-provided references or pointers. Listing and find accumulate multi-page callback results until `has_more`/`has_more_results` becomes false.

State and persistence: no independent persistent state. Temporary promises, futures, tuples, and output accumulators live only for the duration of the blocking call. `Find` keeps a local status that records the first async error.

Dependencies and integration: depends on `filesystem.h`, futures, tuples, and the async `FileSystemImpl` implementation. These functions require `IoService` worker threads to be running; otherwise futures may never complete.

Risks and test signals: sync methods can deadlock if called from an `IoService` worker that is needed to satisfy the async operation, or if no worker thread exists. Pointer validation is inconsistent: `GetBlockLocations`, `GetListing`, and `Find` validate output pointers, while other reference outputs assume validity. `Open` deletes a non-null handle on error and should be leak-tested.
