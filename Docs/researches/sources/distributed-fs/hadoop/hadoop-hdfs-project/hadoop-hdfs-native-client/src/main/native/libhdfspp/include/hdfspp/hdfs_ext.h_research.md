# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/hdfs_ext.h

## Purpose
`hdfs_ext.h` extends the legacy libhdfs C ABI with libhdfs++-specific functions for errors, cancellation, builder config reads, block locations, logging, event monitors, recursive find, snapshots, and two-phase filesystem connection.

## Important APIs, Control Flow, and State
It includes `hdfs/hdfs.h` for compatible typedefs and redefines `LIBHDFS_EXTERNAL`. Error APIs copy last thread error into a user buffer. Cancellation APIs cover file operations and pending filesystem connects. Builder extensions read strings/ints/longs from loaded config and can create builders from config directories. Block-location structs model file/block/datanode data and require `hdfsFreeBlockLocations`. Logging APIs set a global C hook, copy/free `LogData`, enable/disable components, and set levels. Monitor pre-attach APIs register callbacks for the next filesystem connect or file open on the current thread. Snapshot APIs and `hdfsFind` expose higher-level NameNode calls. `hdfsAllocateFileSystem`, `hdfsConnectAllocated`, and `hdfsCancelPendingConnection` support connect cancellation.

## Dependencies and Integration Points
It bridges C clients to libhdfs++ internals, while preserving legacy libhdfs types. It depends on `hdfspp/log.h` and stable event names matching `events.h`.

## Risks and Test Signals
This is ABI-sensitive and has mixed ownership rules. Callback reentrancy and thread-local monitor registration are high-risk. Tests should cover every allocation/free pair, logging hook concurrency, invalid logging levels/components, event monitor one-shot behavior, snapshot argument validation, find empty/error results, two-phase connect/cancel, and C struct conversion from C++ block locations.
