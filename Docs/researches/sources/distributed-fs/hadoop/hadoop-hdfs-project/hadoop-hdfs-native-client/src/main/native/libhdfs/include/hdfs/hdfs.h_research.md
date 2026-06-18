# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/include/hdfs/hdfs.h

## Purpose
This is the public C ABI for legacy `libhdfs`, a JNI-backed HDFS client facade. It exports opaque filesystem and file handles, scalar typedefs (`tSize`, `tOffset`, `tTime`, `tPort`), file metadata structs, read statistics, hedged-read metrics, builder APIs, stream/open-future APIs, normal filesystem operations, zero-copy read APIs, and thread-local last-exception accessors. It also defines platform export/import macros so the same header can serve Unix shared libraries and Windows DLL clients.

## Important APIs, Control Flow, and State
Callers normally create a `hdfsBuilder`, configure NameNode, port, user, Kerberos ticket cache, and config strings, then call `hdfsBuilderConnect`; older `hdfsConnect*` entry points are deprecated. File access flows through `hdfsOpenFile` or `hdfsStreamBuilderBuild`, then read/write/seek/tell/flush/sync/close. Async open wraps Java `FutureDataInputStreamBuilder` through `hdfsOpenFileBuilder*` and `hdfsOpenFileFuture*`. Metadata paths allocate `hdfsFileInfo`, host arrays, block-size/capacity counters, or zero-copy `hadoopRzBuffer` instances that must be freed through matching functions. Errors are reported by return values plus `errno`; Java exception text is available per calling thread.

## Dependencies and Integration Points
The header depends on C system types and maps onto Hadoop Java `FileSystem`, `Path`, streams, block locations, permissions, and read-statistics classes through the implementation. It is also consumed by `libhdfspp/include/hdfspp/hdfs_ext.h` to keep C bindings compatible with legacy typedefs and file-info layout.

## Risks and Test Signals
This file is ABI-sensitive: struct layout, opaque typedef names, exported symbol names, ownership contracts, and errno semantics affect downstream native clients. Tests should cover builder lifetimes, default/local/URI NameNode handling, config lookup/freeing, read/write EOF and EINTR behavior, stream-builder validation, async open timeout/cancel, file-info allocation/freeing, host-array freeing, zero-copy EOF/freeing, statistics/metrics unsupported filesystems, and per-thread exception strings.
